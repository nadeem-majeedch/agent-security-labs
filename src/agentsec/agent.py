"""The agent loop: the smallest deterministic model/tool iteration.

The agent owns conversation state and iteration control. It knows only
abstractions:

* a :class:`~agentsec.models.base.ModelAdapter` for completions;
* a :class:`~agentsec.tools.gateway.ToolGateway` for every tool call.

It never executes a tool, evaluates a policy rule, validates a tool schema or
builds provider-specific requests - those belong to the gateway, the policy
engine, the tools and the adapters respectively. It calculates no security
metrics.

Loop (at most ``max_steps`` model calls)::

    input -> model -> final answer? return
                    -> tool calls? gateway -> tool results -> model -> ...
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .errors import AgentError, MaxStepsExceeded, UnknownTool
from .models.base import ModelAdapter
from .models.schema import Message, ModelResponse, Role, ToolSpec
from .tools.base import ToolContext, ToolResult
from .tools.gateway import ToolGateway
from .trace.recorder import TraceRecorder
from .trace.redact import hash_value
from .trace.schema import (
    AgentInputEvent,
    AgentOutputEvent,
    ModelRequestEvent,
    ModelResponseEvent,
    RunCompletedEvent,
    RunFailedEvent,
    RunStartedEvent,
    UsageCounts,
)


class RunStatus(str, Enum):
    """How an agent run ended."""

    COMPLETED = "completed"
    STEP_LIMIT = "step_limit"
    FAILED = "failed"


class AgentConfig(BaseModel):
    """Everything the agent needs that is not a collaborator."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_id: str = Field(default="agent-1", min_length=1)
    run_id: str = Field(default="run-1", min_length=1)
    scenario: str = Field(default="LAB-00-a", min_length=1)
    config_ref: str = Field(default="inline", min_length=1)
    max_steps: int = Field(default=8, ge=1)
    system_prompt: str | None = None
    #: Resource identifiers considered in-scope for the task (policy condition).
    task_scope: tuple[str, ...] = ()


class RunResult(BaseModel):
    """The structured outcome of one agent run."""

    model_config = ConfigDict(extra="forbid")

    status: RunStatus
    output: str = ""
    steps: int = 0
    tool_calls: int = 0
    error: str | None = None
    trace_path: Path | None = None
    messages: list[Message] = Field(default_factory=list)


class Agent:
    """A small, deterministic ReAct-style loop over a model and a gateway."""

    def __init__(
        self,
        model: ModelAdapter,
        gateway: ToolGateway,
        recorder: TraceRecorder | None = None,
        *,
        config: AgentConfig | None = None,
        approval: bool | None = None,
    ) -> None:
        self._model = model
        self._gateway = gateway
        self._config = config or AgentConfig()
        self._approval = approval
        # One recorder is shared with the gateway so a single run writes a
        # single coherent trace. Build the recorder first and pass it to both.
        self._recorder = recorder

    @property
    def config(self) -> AgentConfig:
        return self._config

    def _emit(self, event_cls: Any, **fields: Any) -> Any:
        if self._recorder is None:
            return None
        return self._recorder.emit_event(event_cls, **fields)

    def _parent(self) -> str | None:
        return self._recorder.last_event_id if self._recorder is not None else None

    def _tool_specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(name=schema.name, description=schema.description, parameters=dict(schema.input_schema))
            for schema in self._gateway.tool_schemas()
        ]

    def _context(self) -> ToolContext:
        return ToolContext(
            agent_id=self._config.agent_id,
            run_id=self._config.run_id,
            scenario=self._config.scenario,
            task_scope=self._config.task_scope,
        )

    def run(self, task: str) -> RunResult:
        """Run the loop for ``task`` and return a structured result."""
        config = self._config
        messages: list[Message] = []
        if config.system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=config.system_prompt))
        messages.append(Message(role=Role.USER, content=task))

        specs = self._tool_specs()
        tool_specs_hash = hash_value([spec.model_dump(mode="json") for spec in specs])
        tool_call_count = 0
        usage_total: UsageCounts | None = None
        step = 0

        try:
            self._emit(
                RunStartedEvent,
                config_ref=config.config_ref,
                scenario_id=config.scenario,
            )
            self._emit(
                AgentInputEvent,
                input_ref=hash_value(task),
                task=task,
                parent_event_id=self._parent(),
            )

            for step in range(1, config.max_steps + 1):
                self._emit(
                    ModelRequestEvent,
                    messages_hash=hash_value([m.model_dump(mode="json") for m in messages]),
                    tool_specs_hash=tool_specs_hash,
                    parent_event_id=self._parent(),
                )
                response = self._model.complete(list(messages), tools=specs or None)
                if not isinstance(response, ModelResponse):
                    raise AgentError(
                        f"model returned {type(response).__name__}, expected ModelResponse"
                    )
                usage_total = _merge_usage(usage_total, response.usage)
                self._emit(
                    ModelResponseEvent,
                    response_hash=hash_value(response.model_dump(mode="json")),
                    finish_reason=response.finish_reason,
                    usage=_usage_counts(response.usage),
                    latency_ms=response.latency_ms,
                    parent_event_id=self._parent(),
                )

                if not response.tool_calls:
                    messages.append(Message(role=Role.ASSISTANT, content=response.text))
                    self._emit(
                        AgentOutputEvent,
                        output_hash=hash_value(response.text),
                        answer_redacted=response.text,
                        parent_event_id=self._parent(),
                    )
                    self._emit(
                        RunCompletedEvent,
                        steps=step,
                        duration_ms=0.0,
                        usage_total=usage_total,
                        parent_event_id=self._parent(),
                    )
                    return RunResult(
                        status=RunStatus.COMPLETED,
                        output=response.text,
                        steps=step,
                        tool_calls=tool_call_count,
                        trace_path=self._recorder.path if self._recorder else None,
                        messages=messages,
                    )

                messages.append(Message(role=Role.ASSISTANT, content=response.text))
                for call in response.tool_calls:
                    if not self._gateway.has_tool(call.name):
                        raise UnknownTool(call.name)
                    result = self._gateway.invoke(
                        config.agent_id,
                        call.name,
                        call.arguments,
                        self._context(),
                        approval=self._approval,
                        parent_event_id=self._parent(),
                    )
                    tool_call_count += 1
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=_tool_message(result),
                            tool_call_id=call.id,
                        )
                    )

            raise MaxStepsExceeded(config.max_steps)

        except MaxStepsExceeded as exc:
            self._emit(
                RunFailedEvent,
                error_type="MaxStepsExceeded",
                message=str(exc),
                parent_event_id=self._parent(),
            )
            return RunResult(
                status=RunStatus.STEP_LIMIT,
                steps=step,
                tool_calls=tool_call_count,
                error=str(exc),
                trace_path=self._recorder.path if self._recorder else None,
                messages=messages,
            )
        except Exception as exc:  # noqa: BLE001 - the loop must terminate safely
            self._emit(
                RunFailedEvent,
                error_type=type(exc).__name__,
                message=str(exc),
                parent_event_id=self._parent(),
            )
            return RunResult(
                status=RunStatus.FAILED,
                steps=step,
                tool_calls=tool_call_count,
                error=str(exc),
                trace_path=self._recorder.path if self._recorder else None,
                messages=messages,
            )


def _tool_message(result: ToolResult) -> str:
    """Render a tool result as a JSON tool message for the model."""
    payload: dict[str, Any] = {"ok": result.ok, "output": result.output}
    if result.error:
        payload["error"] = result.error
    return json.dumps(payload, sort_keys=True)


def _usage_counts(usage: Any) -> UsageCounts | None:
    if usage is None:
        return None
    return UsageCounts(
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
    )


def _merge_usage(total: UsageCounts | None, usage: Any) -> UsageCounts | None:
    if usage is None:
        return total
    if total is None:
        total = UsageCounts(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    return UsageCounts(
        prompt_tokens=total.prompt_tokens + usage.prompt_tokens,
        completion_tokens=total.completion_tokens + usage.completion_tokens,
        total_tokens=total.total_tokens + usage.total_tokens,
    )


__all__ = ["Agent", "AgentConfig", "RunResult", "RunStatus"]
