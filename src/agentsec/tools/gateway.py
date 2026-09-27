"""The ToolGateway: the single mediated path for every tool call.

Lifecycle per call (Phase 14, Task 8):

1. look up the tool (``UnknownTool`` if missing);
2. validate arguments against the tool schema (``ToolValidationError``);
3. emit ``tool_requested``;
4. ask the policy engine for a decision;
5. emit ``policy_decision``;
6. deny -> emit ``tool_result{denied}`` and return a ``DeniedResult``;
   require_approval -> resolve the approval (see below); allow -> execute;
7. emit ``tool_executed`` then ``tool_result``;
8. return a structured :class:`~agentsec.tools.base.ToolResult`.

Two invariants the tests enforce:

* a denied call **never** invokes the underlying tool;
* a call requiring approval **never** silently becomes an allow.

Approval model (OD-2): approval is deterministic and offline. ``invoke`` accepts
``approval=True`` (granted) or ``approval=False`` (refused); when neither is
given an optional scripted ``approver`` callable decides. If nothing grants
approval the call stays ``pending_approval`` and is *not* executed.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from ..errors import PolicyDenied, ToolExecutionError, ToolValidationError, UnknownTool
from ..policy.base import PolicyEngine
from ..policy.schema import Decision
from ..trace.recorder import TraceRecorder
from ..trace.redact import DEFAULT_REDACTOR, hash_value
from ..trace.schema import (
    PolicyDecisionEvent,
    ToolExecutedEvent,
    ToolRequestedEvent,
    ToolResultEvent,
)
from .base import (
    DeniedResult,
    PendingApprovalResult,
    Tool,
    ToolContext,
    ToolResult,
    ToolSchema,
)

#: A deterministic offline approver: ``(agent_id, tool_name, args) -> bool``.
Approver = Callable[[str, str, Mapping[str, Any]], bool]


class ToolGateway:
    """Mediate every tool call through validation, policy and tracing."""

    def __init__(
        self,
        tools: Mapping[str, Tool],
        policy: PolicyEngine,
        recorder: TraceRecorder | None = None,
        *,
        approver: Approver | None = None,
        raise_on_denied: bool = False,
    ) -> None:
        self._tools: dict[str, Tool] = dict(tools)
        self._policy = policy
        self._recorder = recorder
        self._approver = approver
        self._raise_on_denied = raise_on_denied

    def list_tools(self) -> list[str]:
        """Names of the tools this gateway mediates, sorted."""
        return sorted(self._tools)

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def tool_schemas(self) -> list[ToolSchema]:
        """The typed contract of every mediated tool, sorted by name.

        Advertised to the model as provider-independent ``ToolSpec`` objects by
        the agent, so the agent never needs tool objects to description tools.
        """
        return [self._tools[name].schema() for name in self.list_tools()]

    # -- public entry point ----------------------------------------------------
    def invoke(
        self,
        agent_id: str,
        tool_name: str,
        args: Mapping[str, Any],
        ctx: ToolContext | None = None,
        *,
        approval: bool | None = None,
        parent_event_id: str | None = None,
    ) -> ToolResult:
        """Validate, authorize, execute and trace one tool call.

        ``parent_event_id`` links the emitted ``tool_requested`` event to the
        caller's preceding event (for example the model response that produced
        the call), so the trace stays reconstructable.
        """
        if ctx is None:
            ctx = ToolContext(agent_id=agent_id)

        tool = self._tools.get(tool_name)
        if tool is None:
            raise UnknownTool(tool_name)

        validated = tool.schema().validate_args(dict(args))

        requested = self._emit_requested(tool_name, validated, parent_event_id)
        decision = self._policy.decide(
            agent_id,
            tool_name,
            validated,
            ctx,
            action=self._safe_action(tool, validated),
            resource=self._safe_resource(tool, validated),
        )
        self._emit_decision(decision, requested)

        if decision.decision is Decision.DENY:
            result: ToolResult = DeniedResult(error=f"denied: {decision.reason}")
            self._emit_result(result, requested)
            if self._raise_on_denied:
                raise PolicyDenied(tool_name, decision.reason, decision.matched_rule)
            return result

        if decision.decision is Decision.REQUIRE_APPROVAL:
            outcome = self._resolve_approval(agent_id, tool_name, validated, approval)
            if outcome == "denied":
                result = DeniedResult(error=f"approval denied: {decision.reason}")
                self._emit_result(result, requested)
                return result
            if outcome == "pending":
                result = PendingApprovalResult(
                    error=f"approval required: {decision.reason}"
                )
                self._emit_result(result, requested)
                return result
            # outcome == "approved" -> fall through and execute

        return self._execute(tool, validated, ctx, requested)

    # -- execution -------------------------------------------------------------
    def _execute(
        self,
        tool: Tool,
        args: dict[str, Any],
        ctx: ToolContext,
        requested: ToolRequestedEvent | None,
    ) -> ToolResult:
        parent = requested.event_id if requested is not None else None
        if self._recorder is not None:
            self._recorder.emit_event(
                ToolExecutedEvent, tool_name=tool.name, parent_event_id=parent
            )
        try:
            raw = tool.run(args, ctx)
        except (ToolExecutionError, ToolValidationError) as exc:
            result = ToolResult.failure(str(exc))
        except Exception as exc:  # noqa: BLE001 - never let a tool crash the caller
            result = ToolResult.failure(f"{type(exc).__name__}: {exc}")
        else:
            result = self._validate_output(tool, raw)
        self._emit_result(result, requested)
        return result

    @staticmethod
    def _validate_output(tool: Tool, raw: ToolResult) -> ToolResult:
        if not raw.ok:
            return raw
        try:
            tool.schema().validate_output(raw.output)
        except ToolValidationError as exc:
            return ToolResult.failure(f"invalid tool output: {exc.message}")
        return raw

    # -- approval --------------------------------------------------------------
    def _resolve_approval(
        self,
        agent_id: str,
        tool_name: str,
        args: Mapping[str, Any],
        approval: bool | None,
    ) -> str:
        if approval is True:
            return "approved"
        if approval is False:
            return "denied"
        if self._approver is not None:
            return "approved" if self._approver(agent_id, tool_name, args) else "denied"
        return "pending"

    # -- metadata (tools must never break mediation) ---------------------------
    @staticmethod
    def _safe_action(tool: Tool, args: Mapping[str, Any]) -> str:
        try:
            return tool.action(args)
        except Exception:  # noqa: BLE001
            return "invoke"

    @staticmethod
    def _safe_resource(tool: Tool, args: Mapping[str, Any]) -> str | None:
        try:
            return tool.resource(args)
        except Exception:  # noqa: BLE001
            return None

    # -- tracing ---------------------------------------------------------------
    def _emit_requested(
        self,
        tool_name: str,
        args: Mapping[str, Any],
        parent_event_id: str | None = None,
    ) -> ToolRequestedEvent | None:
        if self._recorder is None:
            return None
        return self._recorder.emit_event(
            ToolRequestedEvent,
            tool_name=tool_name,
            args_hash=hash_value(dict(args)),
            args_redacted=DEFAULT_REDACTOR.redact_mapping(args),
            parent_event_id=parent_event_id,
        )

    def _emit_decision(self, decision: Any, requested: ToolRequestedEvent | None) -> None:
        if self._recorder is None:
            return
        self._recorder.emit_event(
            PolicyDecisionEvent,
            decision=decision.decision.value,
            matched_rule=decision.matched_rule,
            reason=decision.reason,
            parent_event_id=requested.event_id if requested is not None else None,
        )

    def _emit_result(self, result: ToolResult, requested: ToolRequestedEvent | None) -> None:
        if self._recorder is None:
            return
        self._recorder.emit_event(
            ToolResultEvent,
            ok=result.ok,
            result_hash=hash_value(result.output),
            error=result.error,
            side_effects=result.side_effects or None,
            parent_event_id=requested.event_id if requested is not None else None,
        )
