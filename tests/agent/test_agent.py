"""End-to-end tests for the agent loop, gateway dispatch and trace output."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agentsec.agent import Agent, AgentConfig, RunStatus
from agentsec.errors import ModelError, ToolExecutionError, UnknownTool
from agentsec.models.base import Capabilities, ModelInfo
from agentsec.models.mock import MockAction, MockModel, MockScript, MockStep, script_for
from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, PolicyRule
from agentsec.tools.base import BaseTool, ToolResult
from agentsec.tools.factory import build_gateway
from agentsec.trace.recorder import TraceRecorder
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

FIXED = datetime(2026, 1, 1, tzinfo=timezone.utc)


# -- helpers -------------------------------------------------------------------
def allow_calc() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="allow-calc", tool="calculator", decision=Decision.ALLOW, reason="ok")],
        default_decision=Decision.DENY,
    )


def allow_all() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="allow-all", decision=Decision.ALLOW, reason="ok")],
        default_decision=Decision.DENY,
    )


def require_calc() -> PolicyEngine:
    return PolicyEngine(
        [
            PolicyRule(
                id="approve-calc",
                tool="calculator",
                decision=Decision.REQUIRE_APPROVAL,
                reason="needs approval",
            )
        ],
        default_decision=Decision.DENY,
    )


def deny_all() -> PolicyEngine:
    return PolicyEngine([], default_decision=Decision.DENY)


def recorder(tmp_path):
    return TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )


def answer(text: str, **matchers) -> MockStep:
    return MockStep(action=MockAction(kind="answer", text=text), **matchers)


def tool_call(name: str, arguments: dict, **matchers) -> MockStep:
    return MockStep(
        action=MockAction(kind="tool_call", tool_name=name, arguments=arguments), **matchers
    )


def script(steps, fallback) -> MockScript:
    fb = fallback.action if isinstance(fallback, MockStep) else fallback
    return MockScript(name="integration", steps=steps, fallback=fb)


class CountingTool(BaseTool):
    """A tool double named ``calculator`` that records whether it ran."""

    name = "calculator"
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {"expr": {"type": "string"}},
        "required": ["expr"],
        "additionalProperties": False,
    }
    OUTPUT_SCHEMA = {"type": "object", "properties": {"value": {"type": "number"}}}

    def __init__(self) -> None:
        self.runs = 0

    def run(self, args, ctx):  # noqa: ARG002
        self.runs += 1
        return ToolResult.success({"value": 42.0})


class RaisingAdapter:
    """A model adapter that raises on ``complete``."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def complete(self, messages, *, temperature=None, seed=None, tools=None):  # noqa: ARG002
        raise self._exc

    def capabilities(self):
        return Capabilities(supports_temperature=False, supports_seed=False, supports_tools=True)

    def describe(self):
        return ModelInfo(provider="fake", model_id="fake-v1")


class WrongAdapter(RaisingAdapter):
    """A model adapter that returns a malformed response."""

    def __init__(self) -> None:
        super().__init__(RuntimeError("unused"))

    def complete(self, messages, *, temperature=None, seed=None, tools=None):  # noqa: ARG002
        return {"text": "not a ModelResponse"}


# -- flows ---------------------------------------------------------------------
def test_benign_flow_without_tools():
    model = MockModel(script([answer("hello there", contains="hello")], answer("fallback")))
    agent = Agent(model, build_gateway(allow_all()), config=AgentConfig())
    result = agent.run("hello agent")
    assert result.status is RunStatus.COMPLETED
    assert result.steps == 1
    assert result.tool_calls == 0
    assert result.output == "hello there"
    assert result.trace_path is None


def test_allowed_tool_flow():
    agent = Agent(MockModel(script_for("benign")), build_gateway(allow_calc()), config=AgentConfig())
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert result.steps == 2
    assert result.tool_calls == 1
    assert result.output == "The sum of 2 and 3 is 5."


def test_denied_tool_flow_does_not_execute(tmp_path):
    rec = recorder(tmp_path)
    counting = CountingTool()
    gw = build_gateway(deny_all(), tools={"calculator": counting}, recorder=rec)
    agent = Agent(MockModel(script_for("benign")), gw, rec, config=AgentConfig())
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert result.tool_calls == 1
    assert counting.runs == 0

    types = [e["event_type"] for e in read_events(rec.path)]
    assert "tool_executed" not in types
    decisions = [e for e in read_events(rec.path) if e["event_type"] == "policy_decision"]
    assert decisions[0]["decision"] == "deny"
    results = [e for e in read_events(rec.path) if e["event_type"] == "tool_result"]
    assert results[0]["ok"] is False


def test_approval_required_not_executed_without_approval(tmp_path):
    rec = recorder(tmp_path)
    counting = CountingTool()
    gw = build_gateway(require_calc(), tools={"calculator": counting}, recorder=rec)
    agent = Agent(MockModel(script_for("benign")), gw, rec, config=AgentConfig())
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert counting.runs == 0
    assert "tool_executed" not in [
        e["event_type"] for e in read_events(rec.path)
    ]


def test_approval_granted_executes():
    counting = CountingTool()
    gw = build_gateway(require_calc(), tools={"calculator": counting})
    agent = Agent(MockModel(script_for("benign")), gw, config=AgentConfig(), approval=True)
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert counting.runs == 1


def test_multi_step_flow():
    model = MockModel(
        script(
            [
                tool_call("calculator", {"expr": "2+3"}, contains="add", is_tool_result=False),
                tool_call("calculator", {"expr": "4+5"}, contains='"value": 5.0', is_tool_result=True),
                answer("both done", contains='"value": 9.0', is_tool_result=True),
            ],
            answer("fallback"),
        )
    )
    agent = Agent(model, build_gateway(allow_calc()), config=AgentConfig(max_steps=6))
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert result.steps == 3
    assert result.tool_calls == 2
    assert result.output == "both done"


def test_step_limit_flow_stops_exactly_at_max_steps(tmp_path):
    rec = recorder(tmp_path)
    model = MockModel(
        script(
            [tool_call("calculator", {"expr": "1+1"})],
            MockAction(kind="tool_call", tool_name="calculator", arguments={"expr": "1+1"}),
        )
    )
    agent = Agent(model, build_gateway(allow_calc(), recorder=rec), rec, config=AgentConfig(max_steps=3))
    result = agent.run("keep going")
    assert result.status is RunStatus.STEP_LIMIT
    assert result.steps == 3
    assert result.tool_calls == 3
    assert "maximum" in (result.error or "")
    events = read_events(rec.path)
    assert [e["event_type"] for e in events][-1] == "run_failed"
    assert events[-1]["error_type"] == "MaxStepsExceeded"


def test_model_error_is_terminal(tmp_path):
    rec = recorder(tmp_path)
    agent = Agent(RaisingAdapter(ModelError("boom")), build_gateway(allow_all()), rec, config=AgentConfig())
    result = agent.run("hello")
    assert result.status is RunStatus.FAILED
    assert "boom" in (result.error or "")
    failed = [e for e in read_events(rec.path) if e["event_type"] == "run_failed"]
    assert failed[0]["error_type"] == "ModelError"


def test_malformed_model_response_is_terminal():
    agent = Agent(WrongAdapter(), build_gateway(allow_all()), config=AgentConfig())
    result = agent.run("hello")
    assert result.status is RunStatus.FAILED
    assert "ModelResponse" in (result.error or "")


def test_tool_execution_error_is_fed_back(tmp_path):
    rec = recorder(tmp_path)
    model = MockModel(
        script(
            [
                tool_call(
                    "fs_sandbox",
                    {"op": "read", "path": "workspace/missing.txt"},
                    contains="read",
                ),
                answer("could not read it", is_tool_result=True, tool_result_ok=False),
            ],
            answer("fallback"),
        )
    )
    agent = Agent(model, build_gateway(allow_all(), recorder=rec), rec, config=AgentConfig())
    result = agent.run("please read the note")
    assert result.status is RunStatus.COMPLETED
    assert result.tool_calls == 1
    assert result.output == "could not read it"
    results = [e for e in read_events(rec.path) if e["event_type"] == "tool_result"]
    assert results[0]["ok"] is False


def test_unknown_tool_is_terminal_and_traced(tmp_path):
    rec = recorder(tmp_path)
    model = MockModel(
        script([tool_call("ghost", {}, contains="ghost")], answer("fallback"))
    )
    agent = Agent(model, build_gateway(allow_all(), recorder=rec), rec, config=AgentConfig())
    result = agent.run("call the ghost")
    assert result.status is RunStatus.FAILED
    assert isinstance(result.error, str)
    failed = [e for e in read_events(rec.path) if e["event_type"] == "run_failed"]
    assert failed[0]["error_type"] == "UnknownTool"


def test_invalid_tool_arguments_are_terminal(tmp_path):
    rec = recorder(tmp_path)
    model = MockModel(
        script([tool_call("calculator", {"expr": 5}, contains="calculate")], answer("fallback"))
    )
    agent = Agent(model, build_gateway(allow_calc(), recorder=rec), rec, config=AgentConfig())
    result = agent.run("please calculate")
    assert result.status is RunStatus.FAILED
    assert "ToolValidationError" in json.dumps(
        [e for e in read_events(rec.path) if e["event_type"] == "run_failed"][0]
    )


# -- trace & determinism -------------------------------------------------------
def test_trace_order_and_correlation(tmp_path):
    rec = recorder(tmp_path)
    agent = Agent(
        MockModel(script_for("benign")),
        build_gateway(allow_calc(), recorder=rec),
        rec,
        config=AgentConfig(),
    )
    result = agent.run("please add 2 and 3")
    assert result.status is RunStatus.COMPLETED
    assert validate_jsonl(rec.path).ok

    events = read_events(rec.path)
    assert [e["event_type"] for e in events] == [
        "run_started",
        "agent_input",
        "model_request",
        "model_response",
        "tool_requested",
        "policy_decision",
        "tool_executed",
        "tool_result",
        "model_request",
        "model_response",
        "agent_output",
        "run_completed",
    ]
    by_id = {e["event_id"]: e for e in events}
    ids = [e["event_id"] for e in events]
    assert events[0]["parent_event_id"] is None
    # every parent references an earlier event in the same run
    for index, event in enumerate(events[1:], start=1):
        assert event["parent_event_id"] in ids[:index]
    # the tool-call block hangs off the model response that produced it
    assert by_id[events[4]["parent_event_id"]]["event_type"] == "model_response"
    for event in events[5:8]:
        assert by_id[event["parent_event_id"]]["event_type"] == "tool_requested"
    # the next model call follows the tool result
    assert by_id[events[8]["parent_event_id"]]["event_type"] == "tool_result"


def test_deterministic_replay(tmp_path):
    def run(directory):
        rec = TraceRecorder(
            directory / "trace.jsonl",
            run_id="run-1",
            agent_id="agent-1",
            model="mock-v1",
            scenario="LAB-01-a",
            clock=lambda: FIXED,
        )
        agent = Agent(
            MockModel(script_for("benign")),
            build_gateway(allow_calc(), recorder=rec),
            rec,
            config=AgentConfig(),
        )
        result = agent.run("please add 2 and 3")
        return result, rec.path.read_text(encoding="utf-8")

    first_result, first_trace = run(tmp_path / "a")
    second_result, second_trace = run(tmp_path / "b")
    assert first_result.output == second_result.output
    assert first_result.steps == second_result.steps
    assert first_result.tool_calls == second_result.tool_calls
    assert first_trace == second_trace


def test_system_prompt_is_part_of_conversation():
    agent = Agent(
        MockModel(script([answer("ok", is_tool_result=False)], answer("f"))),
        build_gateway(allow_all()),
        config=AgentConfig(system_prompt="You are terse."),
    )
    result = agent.run("hi")
    assert result.messages[0].role.value == "system"
    assert result.messages[0].content == "You are terse."
    assert result.messages[1].role.value == "user"


def test_max_steps_must_be_positive():
    with pytest.raises(ValidationError):
        AgentConfig(max_steps=0)


def test_tool_specs_are_advertised_to_the_model():
    gateway = build_gateway(allow_all())
    assert {schema.name for schema in gateway.tool_schemas()} == {
        "calculator",
        "fs_sandbox",
        "mock_db",
    }
    agent = Agent(MockModel(script([answer("ok")], answer("f"))), gateway, config=AgentConfig())
    result = agent.run("hi")
    assert result.status is RunStatus.COMPLETED


def test_tool_execution_error_class_is_importable():
    # guards against the error hierarchy being broken while wiring the loop
    assert issubclass(ToolExecutionError, Exception)
    assert issubclass(UnknownTool, Exception)
