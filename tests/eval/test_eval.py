"""Tests for the read-only, descriptive trace evaluator."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from agentsec.agent import Agent
from agentsec.errors import EvaluationError
from agentsec.eval import EvaluationInput, RunOutcome, TraceEvaluator
from agentsec.models.mock import MockModel, script_for
from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, PolicyRule
from agentsec.tools import build_gateway
from agentsec.trace import TraceRecorder

FIXED = datetime(2026, 1, 1, tzinfo=timezone.utc)


def ev(base, seq, event_type, **extra):
    payload = base(event_id=f"ev-{seq:02d}", seq=seq)
    payload["event_type"] = event_type
    payload.update(extra)
    return payload


def evaluate(events):
    return TraceEvaluator().evaluate(EvaluationInput.from_events(events))


def run_started(base):
    return ev(base, 0, "run_started", config_ref="cfg", scenario_id="LAB-01-a")


def run_completed(base, seq, steps=1):
    return ev(base, seq, "run_completed", steps=steps, duration_ms=0.0)


def run_failed(base, seq, error_type="ModelError", message="boom"):
    return ev(base, seq, "run_failed", error_type=error_type, message=message)


def model_call(base, seq, response_hash="r"):
    """A model_request immediately followed by its model_response."""
    request = ev(
        base, seq, "model_request", messages_hash="m", tool_specs_hash="t"
    )
    response = ev(
        base, seq + 1, "model_response", response_hash=response_hash,
        parent_event_id=request["event_id"],
    )
    return [request, response]


def tool_block(base, seq, name="calculator", decision="allow", executed=True, ok=True):
    """A tool_requested and its associated child events."""
    block = [ev(base, seq, "tool_requested", tool_name=name, args_hash="a")]
    request_id = block[0]["event_id"]
    nxt = seq + 1
    if decision is not None:
        block.append(
            ev(base, nxt, "policy_decision", decision=decision, reason="r",
               parent_event_id=request_id)
        )
        nxt += 1
    if executed:
        block.append(
            ev(base, nxt, "tool_executed", tool_name=name, parent_event_id=request_id)
        )
        nxt += 1
    block.append(ev(base, nxt, "tool_result", ok=ok, result_hash="res",
                    parent_event_id=request_id))
    return block


def test_benign_completed_run(base):
    events = [run_started(base)]
    events += model_call(base, 1)
    events.append(ev(base, 3, "agent_output", output_hash="o", parent_event_id="ev-02"))
    events.append(run_completed(base, 4))
    result = evaluate(events)
    assert result.status is RunOutcome.COMPLETED
    assert result.metrics["model_request"] == 1
    assert result.metrics["model_calls"] == 1
    assert result.metrics["agent_output"] == 1
    assert result.metrics["total_events"] == 5
    assert result.flags["produced_final_output"] is True
    assert result.flags["reached_step_limit"] is False
    assert result.run_id == "run-1"
    assert len(result.evidence) == 5
    assert result.warnings == []


def test_failed_run(base):
    events = [run_started(base), *model_call(base, 1), run_failed(base, 3)]
    result = evaluate(events)
    assert result.status is RunOutcome.FAILED
    assert result.metrics["run_failed"] == 1
    assert result.flags["has_terminal_event"] is True


def test_step_limit_run(base):
    events = [run_started(base), *model_call(base, 1), run_failed(base, 3, "MaxStepsExceeded")]
    result = evaluate(events)
    assert result.status is RunOutcome.STEP_LIMIT
    assert result.flags["reached_step_limit"] is True


def test_allowed_tool_call(base):
    events = [run_started(base), *model_call(base, 1), *tool_block(base, 3)]
    events.append(run_completed(base, 7, steps=2))
    result = evaluate(events)
    assert result.decisions == {"allow": 1, "deny": 0, "require_approval": 0}
    assert result.tool_results["ok"] == 1
    assert result.tool_calls == {"calculator": 1}
    assert result.metrics["tool_requests"] == 1
    assert result.metrics["tool_executions"] == 1
    assert result.warnings == []


def test_denied_tool_call_never_executed(base):
    events = [
        run_started(base),
        *model_call(base, 1),
        *tool_block(base, 3, decision="deny", executed=False, ok=False),
    ]
    result = evaluate(events)
    assert result.decisions["deny"] == 1
    assert result.tool_results["denied"] == 1
    assert result.tool_results["ok"] == 0
    assert result.metrics["tool_executed"] == 0


def test_approval_required_tool_call_pending(base):
    events = [
        run_started(base),
        *model_call(base, 1),
        *tool_block(base, 3, decision="require_approval", executed=False, ok=False),
    ]
    result = evaluate(events)
    assert result.decisions["require_approval"] == 1
    assert result.tool_results["pending_approval"] == 1
    assert result.metrics["tool_executed"] == 0


def test_tool_execution_error(base):
    events = [
        run_started(base),
        *model_call(base, 1),
        *tool_block(base, 3, decision="allow", executed=True, ok=False),
    ]
    result = evaluate(events)
    assert result.tool_results["error"] == 1
    assert result.tool_results["ok"] == 0
    assert result.metrics["tool_executed"] == 1


def test_multiple_tool_calls_by_name(base):
    events = [run_started(base), *model_call(base, 1)]
    events += tool_block(base, 3, name="calculator")
    events += tool_block(base, 6, name="fs_sandbox")
    result = evaluate(events)
    assert result.metrics["tool_requests"] == 2
    assert result.tool_calls == {"calculator": 1, "fs_sandbox": 1}
    assert result.tool_results["ok"] == 2


def test_multiple_model_calls(base):
    events = [run_started(base)]
    events += model_call(base, 1)
    events += model_call(base, 3)
    result = evaluate(events)
    assert result.metrics["model_request"] == 2
    assert result.metrics["model_response"] == 2


def test_evaluation_is_deterministic(base):
    events = [run_started(base), *model_call(base, 1), *tool_block(base, 3)]
    first = evaluate(events)
    second = evaluate(events)
    assert first == second
    assert TraceEvaluator().VERSION == "v1"
    assert TraceEvaluator().version == "v1"


def test_metric_counts_match_trace_events_exactly(base):
    events = [run_started(base), *model_call(base, 1), *tool_block(base, 3)]
    result = evaluate(events)
    counts: dict[str, int] = {}
    for event in events:
        counts[event["event_type"]] = counts.get(event["event_type"], 0) + 1
    for event_type, expected in counts.items():
        assert result.metrics[event_type] == expected, event_type
    assert result.metrics["total_events"] == len(events)


def test_empty_trace(base):
    result = evaluate([])
    assert result.status is RunOutcome.INCOMPLETE
    assert "trace is empty" in result.warnings
    assert result.metrics["total_events"] == 0
    assert result.flags["has_run_started"] is False
    assert result.flags["has_terminal_event"] is False


def test_missing_run_started_is_warned(base):
    events = [*model_call(base, 0), run_completed(base, 2)]
    result = evaluate(events)
    assert "missing run_started event" in result.warnings
    assert result.status is RunOutcome.COMPLETED


def test_missing_terminal_event_is_warned(base):
    events = [run_started(base), *model_call(base, 1)]
    result = evaluate(events)
    assert "no terminal event (run_completed/run_failed)" in result.warnings
    assert result.status is RunOutcome.INCOMPLETE


def test_duplicate_terminal_events_are_warned(base):
    events = [run_started(base), run_completed(base, 1), run_completed(base, 2)]
    result = evaluate(events)
    assert "multiple terminal events" in result.warnings


def test_tool_result_without_request_is_warned(base):
    events = [
        run_started(base),
        ev(base, 1, "tool_result", ok=True, result_hash="h", parent_event_id="ev-99"),
    ]
    result = evaluate(events)
    assert "tool_result has no matching tool_requested event" in result.warnings


def test_policy_decision_without_request_is_warned(base):
    events = [
        run_started(base),
        ev(base, 1, "policy_decision", decision="deny", reason="r", parent_event_id=None),
    ]
    result = evaluate(events)
    assert "policy_decision has no matching tool_requested event" in result.warnings


def test_model_response_without_request_is_warned(base):
    events = [
        run_started(base),
        ev(base, 1, "model_response", response_hash="r", parent_event_id="ev-99"),
    ]
    result = evaluate(events)
    assert "model_response has no matching model_request event" in result.warnings


def test_tool_request_without_result_is_warned(base):
    events = [
        run_started(base),
        ev(base, 1, "tool_requested", tool_name="calculator", args_hash="a"),
    ]
    result = evaluate(events)
    assert "tool_requested without a tool_result" in result.warnings
    assert result.tool_results["no_result"] == 1


def test_malformed_seq_is_warned(base):
    events = [run_started(base), run_completed(base, 1), run_completed(base, 2)]
    events[2]["seq"] = 1
    result = evaluate(events)
    assert "event seq values are not strictly increasing" in result.warnings


def test_unclassified_event_is_warned(base):
    events = [run_started(base), {"seq": 1, "no_event_type": True}]
    result = evaluate(events)
    assert any("unclassified event" in warning for warning in result.warnings)
    assert result.metrics["total_events"] == 2


def test_from_events_copies_the_list(base):
    events = [run_started(base)]
    data = EvaluationInput.from_events(events)
    events.clear()
    assert len(data.events) == 1


def test_evaluator_does_not_execute_anything(base, monkeypatch):
    """The evaluator must never reach a tool, gateway, policy or agent."""
    from agentsec.agent import Agent
    from agentsec.policy.base import PolicyEngine
    from agentsec.tools.gateway import ToolGateway

    def explode(*args, **kwargs):  # pragma: no cover - must not run
        raise AssertionError("evaluator must not execute this")

    monkeypatch.setattr(ToolGateway, "invoke", explode)
    monkeypatch.setattr(PolicyEngine, "decide", explode)
    monkeypatch.setattr(Agent, "run", explode)

    events = [run_started(base), *model_call(base, 1), *tool_block(base, 3)]
    result = evaluate(events)
    assert result.tool_calls == {"calculator": 1}
    assert result.tool_results["ok"] == 1


def test_evaluate_trace_file_missing_raises(tmp_path):
    with pytest.raises(EvaluationError):
        TraceEvaluator().evaluate_trace(tmp_path / "missing.jsonl")


def test_evaluate_trace_malformed_json_raises(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_text("this is not json\n", encoding="utf-8")
    with pytest.raises(EvaluationError):
        TraceEvaluator().evaluate_trace(path)


def test_evaluate_agent_produced_trace(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    policy = PolicyEngine(
        [PolicyRule(id="allow", tool="calculator", decision=Decision.ALLOW, reason="ok")],
        default_decision=Decision.DENY,
    )
    agent = Agent(MockModel(script_for("benign")), build_gateway(policy, recorder=rec), rec)
    run_result = agent.run("please add 2 and 3")
    assert run_result.status.value == "completed"

    result = TraceEvaluator().evaluate_trace(rec.path)
    assert result.status is RunOutcome.COMPLETED
    assert result.metrics["model_calls"] == 2
    assert result.metrics["tool_requests"] == 1
    assert result.metrics["tool_executions"] == 1
    assert result.tool_calls == {"calculator": 1}
    assert result.tool_results["ok"] == 1
    assert result.warnings == []


def test_evaluate_denied_agent_trace(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-04-a",
        clock=lambda: FIXED,
    )
    policy = PolicyEngine([], default_decision=Decision.DENY)
    agent = Agent(MockModel(script_for("benign")), build_gateway(policy, recorder=rec), rec)
    agent.run("please add 2 and 3")

    result = TraceEvaluator().evaluate_trace(rec.path)
    assert result.status is RunOutcome.COMPLETED
    assert result.decisions["deny"] == 1
    assert result.tool_results["denied"] == 1
    assert result.metrics["tool_executions"] == 0


def test_result_is_json_serializable(base):
    result = evaluate([run_started(base), *model_call(base, 1), run_completed(base, 3)])
    restored = json.loads(result.model_dump_json())
    assert restored["status"] == "completed"
    assert restored["version"] == "v1"
