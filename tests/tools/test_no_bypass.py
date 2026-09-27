"""Architectural mediation: no supported path executes a tool except the gateway.

This is a *supported-API* claim, not an adversarial Python guarantee: nothing
stops code that deliberately imports a tool class and calls ``run`` directly.
What it proves is that the lab's own wiring only ever exposes the gateway, and
that every branch of the gateway that does not authorize execution leaves the
tool untouched.
"""

from __future__ import annotations

import inspect

import pytest

from agentsec.errors import ToolExecutionError, ToolValidationError, UnknownTool
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
from agentsec.tools.factory import build_gateway, build_tools
from agentsec.tools.gateway import ToolGateway

CTX = ToolContext(agent_id="student-agent", run_id="run-1", scenario="LAB-08-a")


class ProbeTool(BaseTool):
    """A real tool whose only job is to count how often it actually runs."""

    name = "probe"
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }
    OUTPUT_SCHEMA = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }

    def __init__(self, *, fail: bool = False) -> None:
        self.runs = 0
        self._fail = fail

    def run(self, args, ctx):  # noqa: ARG002
        self.runs += 1
        if self._fail:
            raise ToolExecutionError(self.name, "exploded")
        return ToolResult.success({"value": args["value"]})


def policy(decision: Decision, tool: str = "probe") -> PolicyEngine:
    if decision is Decision.DENY:
        return PolicyEngine([], default_decision=Decision.DENY)
    return PolicyEngine(
        [PolicyRule(id="rule", tool=tool, decision=decision, reason="rule")],
        default_decision=Decision.DENY,
    )


def test_allowed_tool_executes_through_gateway():
    tool = ProbeTool()
    gw = ToolGateway({tool.name: tool}, policy(Decision.ALLOW))
    assert gw.invoke("student-agent", "probe", {"value": 1}, CTX).ok is True
    assert tool.runs == 1


def test_denied_tool_does_not_execute():
    tool = ProbeTool()
    gw = ToolGateway({tool.name: tool}, policy(Decision.DENY))
    result = gw.invoke("student-agent", "probe", {"value": 1}, CTX)
    assert isinstance(result, DeniedResult)
    assert tool.runs == 0


def test_approval_required_tool_does_not_execute_without_approval():
    tool = ProbeTool()
    gw = ToolGateway({tool.name: tool}, policy(Decision.REQUIRE_APPROVAL))
    result = gw.invoke("student-agent", "probe", {"value": 1}, CTX)
    assert isinstance(result, PendingApprovalResult)
    assert tool.runs == 0


def test_invalid_input_does_not_execute():
    tool = ProbeTool()
    gw = ToolGateway({tool.name: tool}, policy(Decision.ALLOW))
    with pytest.raises(ToolValidationError):
        gw.invoke("student-agent", "probe", {}, CTX)
    assert tool.runs == 0


def test_unknown_tool_does_not_execute():
    tool = ProbeTool()
    gw = ToolGateway({tool.name: tool}, policy(Decision.ALLOW))
    with pytest.raises(UnknownTool):
        gw.invoke("student-agent", "ghost", {}, CTX)
    assert tool.runs == 0


def test_tool_exceptions_are_captured_safely():
    tool = ProbeTool(fail=True)
    gw = ToolGateway({tool.name: tool}, policy(Decision.ALLOW))
    result = gw.invoke("student-agent", "probe", {"value": 1}, CTX)
    assert result.status is ToolStatus.ERROR
    assert result.error is not None
    assert tool.runs == 1


def test_no_public_method_runs_a_tool_directly():
    gw = build_gateway(policy(Decision.ALLOW, tool="calculator"))
    public = {
        name
        for name, _ in inspect.getmembers(gw, predicate=inspect.ismethod)
        if not name.startswith("_")
    }
    assert public == {"invoke", "list_tools", "has_tool", "tool_schemas"}


def test_build_gateway_mediates_factory_built_tools():
    gw = build_gateway(policy(Decision.ALLOW, tool="calculator"))
    assert gw.list_tools() == ["calculator", "fs_sandbox", "mock_db"]
    assert gw.invoke("student-agent", "calculator", {"expr": "2+3"}).ok is True


def test_factory_tools_are_not_returned_by_the_gateway():
    gw = build_gateway(policy(Decision.ALLOW))
    assert not hasattr(gw, "get_tool")
    assert not hasattr(gw, "tools")
    # a gateway is the only object a consumer needs; it has no public "run"
    assert not hasattr(gw, "run")
    assert build_tools(["calculator"])  # tools exist, just not surfaced


def test_build_gateway_rejects_ambiguous_arguments():
    from agentsec.errors import ConfigError

    with pytest.raises(ConfigError):
        build_gateway(policy(Decision.ALLOW), tools={}, names=["calculator"])
