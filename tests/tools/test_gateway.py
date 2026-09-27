"""Tests for the single mediated tool path and its trace integration."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentsec.errors import (
    PolicyDenied,
    ToolExecutionError,
    ToolValidationError,
    UnknownTool,
)
from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, PolicyRule
from agentsec.tools.base import (
    BaseTool,
    DeniedResult,
    PendingApprovalResult,
    ToolContext,
    ToolResult,
    ToolStatus,
)
from agentsec.tools.gateway import ToolGateway
from agentsec.trace.recorder import TraceRecorder
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

CTX = ToolContext(agent_id="agent-1", run_id="run-1", scenario="LAB-04-a")
FIXED = datetime(2026, 1, 1, tzinfo=timezone.utc)


class CountingTool(BaseTool):
    """A controllable tool double that records whether it was ever run."""

    name = "counter"
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }
    OUTPUT_SCHEMA = {
        "type": "object",
        "properties": {"doubled": {"type": "integer"}},
        "required": ["doubled"],
        "additionalProperties": False,
    }

    def __init__(self, *, fail: bool = False, bad_output: bool = False) -> None:
        self.calls = 0
        self._fail = fail
        self._bad_output = bad_output

    def run(self, args, ctx):  # noqa: ARG002
        self.calls += 1
        if self._fail:
            raise ToolExecutionError(self.name, "boom")
        if self._bad_output:
            return ToolResult.success({"wrong": True})
        return ToolResult.success({"doubled": args["value"] * 2})


def allow_engine() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="allow-all", decision=Decision.ALLOW, reason="allowed")],
        default_decision=Decision.DENY,
    )


def deny_engine() -> PolicyEngine:
    return PolicyEngine([], default_decision=Decision.DENY)


def approval_engine() -> PolicyEngine:
    return PolicyEngine(
        [
            PolicyRule(
                id="needs-approval",
                tool="counter",
                decision=Decision.REQUIRE_APPROVAL,
                reason="needs approval",
            )
        ],
        default_decision=Decision.DENY,
    )


def gateway(tool=None, policy=None, **kwargs):
    tools = {"counter": tool or CountingTool()}
    return ToolGateway(tools, policy or allow_engine(), **kwargs)


def test_allowed_call_executes():
    tool = CountingTool()
    result = gateway(tool).invoke("agent-1", "counter", {"value": 3}, CTX)
    assert result.status is ToolStatus.OK
    assert result.output == {"doubled": 6}
    assert tool.calls == 1


def test_denied_call_never_executes():
    tool = CountingTool()
    result = gateway(tool, deny_engine()).invoke("agent-1", "counter", {"value": 3}, CTX)
    assert isinstance(result, DeniedResult)
    assert result.status is ToolStatus.DENIED
    assert result.executed is False
    assert tool.calls == 0


def test_approval_required_does_not_execute_without_approval():
    tool = CountingTool()
    result = gateway(tool, approval_engine()).invoke("agent-1", "counter", {"value": 3}, CTX)
    assert isinstance(result, PendingApprovalResult)
    assert result.status is ToolStatus.PENDING_APPROVAL
    assert tool.calls == 0


def test_approval_granted_executes():
    tool = CountingTool()
    result = gateway(tool, approval_engine()).invoke(
        "agent-1", "counter", {"value": 3}, CTX, approval=True
    )
    assert result.status is ToolStatus.OK
    assert tool.calls == 1


def test_approval_refused_is_denied_and_does_not_execute():
    tool = CountingTool()
    result = gateway(tool, approval_engine()).invoke(
        "agent-1", "counter", {"value": 3}, CTX, approval=False
    )
    assert isinstance(result, DeniedResult)
    assert tool.calls == 0


def test_scripted_approver_can_grant():
    tool = CountingTool()
    result = gateway(tool, approval_engine(), approver=lambda *a: True).invoke(
        "agent-1", "counter", {"value": 3}, CTX
    )
    assert result.status is ToolStatus.OK
    assert tool.calls == 1


def test_scripted_approver_can_deny():
    tool = CountingTool()
    result = gateway(tool, approval_engine(), approver=lambda *a: False).invoke(
        "agent-1", "counter", {"value": 3}, CTX
    )
    assert isinstance(result, DeniedResult)
    assert tool.calls == 0


def test_invalid_input_raises_before_execution():
    tool = CountingTool()
    with pytest.raises(ToolValidationError):
        gateway(tool).invoke("agent-1", "counter", {"value": "not-an-int"}, CTX)
    with pytest.raises(ToolValidationError):
        gateway(tool).invoke("agent-1", "counter", {}, CTX)
    assert tool.calls == 0


def test_unknown_tool_raises():
    with pytest.raises(UnknownTool):
        gateway().invoke("agent-1", "nope", {}, CTX)


def test_tool_exception_is_captured_not_propagated():
    tool = CountingTool(fail=True)
    result = gateway(tool).invoke("agent-1", "counter", {"value": 1}, CTX)
    assert result.status is ToolStatus.ERROR
    assert "boom" in (result.error or "")
    assert tool.calls == 1


def test_invalid_tool_output_is_captured():
    tool = CountingTool(bad_output=True)
    result = gateway(tool).invoke("agent-1", "counter", {"value": 1}, CTX)
    assert result.status is ToolStatus.ERROR
    assert "invalid tool output" in (result.error or "")


def test_strict_mode_raises_policy_denied():
    tool = CountingTool()
    gw = gateway(tool, deny_engine(), raise_on_denied=True)
    with pytest.raises(PolicyDenied):
        gw.invoke("agent-1", "counter", {"value": 3}, CTX)
    assert tool.calls == 0


def test_list_tools_is_sorted():
    gw = ToolGateway(
        {"b": CountingTool(), "a": CountingTool()}, allow_engine()
    )
    assert gw.list_tools() == ["a", "b"]


def recorder(tmp_path):
    return TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-04-a",
        clock=lambda: FIXED,
    )


def test_allowed_call_emits_correlated_trace(tmp_path):
    rec = recorder(tmp_path)
    gw = gateway(policy=allow_engine(), recorder=rec)

    result = gw.invoke("agent-1", "counter", {"value": 3}, CTX)
    assert result.ok
    rec.close()

    events = read_events(rec.path)
    assert [e["event_type"] for e in events] == [
        "tool_requested",
        "policy_decision",
        "tool_executed",
        "tool_result",
    ]
    assert validate_jsonl(rec.path).ok
    requested = events[0]
    assert requested["tool_name"] == "counter"
    assert events[2]["parent_event_id"] == requested["event_id"]
    assert events[3]["parent_event_id"] == requested["event_id"]
    assert events[3]["ok"] is True
    assert events[1]["decision"] == "allow"
    assert events[1]["matched_rule"] == "allow-all"


def test_denied_call_traces_decision_and_result_but_no_execution(tmp_path):
    rec = recorder(tmp_path)
    gw = gateway(policy=deny_engine(), recorder=rec)
    gw.invoke("agent-1", "counter", {"value": 3}, CTX)
    rec.close()
    events = read_events(rec.path)
    types = [e["event_type"] for e in events]
    assert types == ["tool_requested", "policy_decision", "tool_result"]
    assert "tool_executed" not in types
    assert events[1]["decision"] == "deny"
    assert events[2]["ok"] is False
    assert validate_jsonl(rec.path).ok


def test_pending_approval_trace_has_no_execution(tmp_path):
    rec = recorder(tmp_path)
    gw = gateway(policy=approval_engine(), recorder=rec)
    gw.invoke("agent-1", "counter", {"value": 3}, CTX)
    rec.close()
    types = [e["event_type"] for e in read_events(rec.path)]
    assert types == ["tool_requested", "policy_decision", "tool_result"]
    assert validate_jsonl(rec.path).ok


def test_trace_redacts_arguments(tmp_path):
    rec = recorder(tmp_path)
    gw = ToolGateway({"notes": _StringTool()}, allow_engine(), rec)
    gw.invoke("agent-1", "notes", {"note": "token=abcdefghijk"}, CTX)
    rec.close()
    contents = rec.path.read_text(encoding="utf-8")
    assert "abcdefghijk" not in contents
    assert "tool_requested" in contents


class _StringTool(BaseTool):
    name = "notes"
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {"note": {"type": "string"}},
        "additionalProperties": False,
    }
    OUTPUT_SCHEMA = {"type": "object"}

    def run(self, args, ctx):  # noqa: ARG002
        return ToolResult.success({"echo": args.get("note", "")})
