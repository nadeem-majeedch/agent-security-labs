"""LAB-05 - require approval: validation tests.

These prove the lab's configuration and scenario load, that the scenario's
experiment matches the runnable config, that a run passes every expectation,
that the policy answers ``require_approval`` for a legitimate request, that the
call is held pending and therefore never executes, and that the whole thing
replays byte-identically. Fully offline: mock model + sandbox tools only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from agentsec.agent import RunStatus
from agentsec.eval import EvaluationInput, RunOutcome, TraceEvaluator
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner
from agentsec.scenarios import ScenarioStatus, load_scenario
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "labs" / "LAB-05-require-approval"
CONFIG = LAB / "config.yaml"
SCENARIO = LAB / "scenario.yaml"
TRACE_NAME = "trace.jsonl"

EXPECTED_QUERY = "SELECT note FROM notes"

TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def run_lab05(tmp_path: Path):
    """Run the LAB-05 experiment into ``tmp_path`` with a fixed clock."""
    config = load_experiment_config(CONFIG)
    config = config.model_copy(update={"trace_path": tmp_path / TRACE_NAME})
    runner = build_mvp_runner(config, clock=lambda: TS)
    result = runner.run(config)
    return result, load_scenario(SCENARIO)


# -- files / loading -----------------------------------------------------------
def test_lab05_files_exist():
    for name in ("README.md", "config.yaml", "scenario.yaml"):
        assert (LAB / name).is_file()


def test_lab05_readme_is_student_facing():
    text = (LAB / "README.md").read_text(encoding="utf-8")
    for heading in (
        "Learning objectives",
        "Prerequisites",
        "Procedure",
        "Questions to answer",
        "Expected outcome",
        "Completion checklist",
        "Reflection",
    ):
        assert heading in text
    assert "no research claim" in " ".join(text.lower().split())


def test_lab05_config_loads():
    config = load_experiment_config(CONFIG)
    assert config.experiment_id == "lab05_require_approval"
    assert config.mock_script == "approval_read"
    assert config.policy_path is not None
    assert config.agent.run_id == "lab05-run-1"


def test_lab05_scenario_loads_with_id():
    scenario = load_scenario(SCENARIO)
    assert scenario.scenario_id == "LAB-05-require-approval"
    assert scenario.definition().title
    assert scenario.definition().description


def test_lab05_scenario_experiment_matches_config():
    scenario = load_scenario(SCENARIO)
    assert scenario.prepare() == load_experiment_config(CONFIG)


# -- execution / scenario ------------------------------------------------------
def test_lab05_scenario_passes(tmp_path):
    result, scenario = run_lab05(tmp_path)
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.PASSED, [
        (c.name, c.expected, c.observed) for c in outcome.checks if not c.matched
    ]
    assert outcome.error is None
    assert all(check.matched for check in outcome.checks)


def test_lab05_expected_observations_hold(tmp_path):
    result, _ = run_lab05(tmp_path)
    evaluation = result.evaluation
    assert result.agent.status is RunStatus.COMPLETED
    assert evaluation is not None
    assert evaluation.status is RunOutcome.COMPLETED
    assert evaluation.metrics["tool_requests"] == 1
    assert evaluation.metrics["tool_executions"] == 0
    assert evaluation.decisions.get("require_approval") == 1
    assert evaluation.decisions.get("allow") == 0
    assert evaluation.decisions.get("deny") == 0
    assert evaluation.tool_calls == {"mock_db": 1}
    assert evaluation.tool_results.get("pending_approval") == 1
    assert evaluation.tool_results.get("ok") == 0
    assert evaluation.flags.get("produced_final_output") is True


def test_lab05_trace_is_valid(tmp_path):
    run_lab05(tmp_path)
    report = validate_jsonl(tmp_path / TRACE_NAME)
    assert report.issues == [], report.issues


def test_lab05_policy_decision_is_require_approval(tmp_path):
    run_lab05(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    decisions = [e for e in events if e["event_type"] == "policy_decision"]
    assert [d["decision"] for d in decisions] == ["require_approval"]
    assert decisions[0]["matched_rule"] == "db-read-requires-approval"


def test_lab05_approval_requirement_count_is_one(tmp_path):
    result, _ = run_lab05(tmp_path)
    assert result.evaluation is not None
    assert result.evaluation.decisions["require_approval"] == 1


def test_lab05_expected_tool_request_exists(tmp_path):
    run_lab05(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    requested = [e for e in events if e["event_type"] == "tool_requested"]
    assert len(requested) == 1
    assert requested[0]["tool_name"] == "mock_db"
    assert requested[0]["args_redacted"] == {"query": EXPECTED_QUERY}


def test_lab05_request_is_not_executed(tmp_path):
    """A legitimate request held for approval does not run."""
    run_lab05(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    executed = [e for e in events if e["event_type"] == "tool_executed"]
    assert executed == []
    # the decision is parent-linked to the request it answered
    requested = [e for e in events if e["event_type"] == "tool_requested"][0]
    decisions = [e for e in events if e["event_type"] == "policy_decision"][0]
    assert decisions["parent_event_id"] == requested["event_id"]


def test_lab05_pending_result_exists(tmp_path):
    run_lab05(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    results = [e for e in events if e["event_type"] == "tool_result"]
    assert len(results) == 1
    assert results[0]["ok"] is False
    assert "approval required" in (results[0]["error"] or "")


def test_lab05_final_output_exists(tmp_path):
    result, _ = run_lab05(tmp_path)
    assert result.agent.output
    assert "waiting for approval" in result.agent.output
    events = read_events(tmp_path / TRACE_NAME)
    assert any(e["event_type"] == "agent_output" for e in events)
    assert events[-1]["event_type"] == "run_completed"


def test_lab05_scenario_evidence_references_trace(tmp_path):
    result, scenario = run_lab05(tmp_path)
    outcome = scenario.interpret(result)
    types = {ref.event_type for ref in outcome.evidence}
    assert {"run_started", "tool_requested", "tool_result", "run_completed"} <= types


def test_lab05_outcome_is_serializable(tmp_path):
    result, scenario = run_lab05(tmp_path)
    outcome = scenario.interpret(result)
    assert '"status":"passed"' in outcome.model_dump_json().replace(" ", "")


def test_lab05_replay_is_byte_identical(tmp_path):
    run_lab05(tmp_path)
    first = (tmp_path / TRACE_NAME).read_bytes()
    run_lab05(tmp_path)
    second = (tmp_path / TRACE_NAME).read_bytes()
    assert first == second


def test_lab05_evaluation_is_deterministic(tmp_path):
    result, _ = run_lab05(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    first = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    second = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    assert first == second


# -- safety / offline ----------------------------------------------------------
def test_lab05_only_uses_sandbox_tools(tmp_path):
    result, _ = run_lab05(tmp_path)
    evaluation = result.evaluation
    assert evaluation is not None
    assert set(evaluation.tool_calls) <= {"calculator", "fs_sandbox", "mock_db"}
    assert evaluation.tool_calls == {"mock_db": 1}


def test_lab05_yaml_is_declarative():
    for path in (CONFIG, SCENARIO):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for forbidden in (
            "!!python",
            "__import__",
            "subprocess",
            "shell:",
            "eval(",
            "sock" + "et",
            "http" + "://",
            "https" + "://",
        ):
            assert forbidden not in lowered, f"{path.name} contains {forbidden!r}"
        document = yaml.safe_load(text)
        assert isinstance(document, dict)


def test_lab05_has_no_credentials(tmp_path):
    run_lab05(tmp_path)
    text = (tmp_path / TRACE_NAME).read_text(encoding="utf-8")
    for marker in ("FAKE_SECRET", "credentials", "password", "api_key"):
        assert marker not in text


def test_lab05_does_not_touch_the_host_filesystem(tmp_path):
    """Nothing executes, and the sandbox database is in-memory only."""
    result, _ = run_lab05(tmp_path)
    assert not (tmp_path / "notes.txt").exists()
    events = read_events(tmp_path / TRACE_NAME)
    pending = [e for e in events if e["event_type"] == "tool_result" and e["ok"] is False]
    assert len(pending) == 1
    assert pending[0].get("side_effects") in (None, [])
