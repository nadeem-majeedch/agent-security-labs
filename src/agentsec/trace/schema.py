"""The versioned trace event contract (Phase 14, Task 10).

Every line of a JSONL trace is one event. All events share the identifiers
``run_id``, ``event_id``, ``parent_event_id``, ``seq``, ``timestamp``,
``agent_id``, ``model``, ``scenario`` and ``event_type``; per-type payload
fields are added by each concrete event class.

The union is discriminated on ``event_type`` so both pydantic and the generated
JSON Schema reject unknown event types and missing per-type fields.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

TRACE_SCHEMA_VERSION = "1.0"

#: All defined event types, in schema order.
TRACE_EVENT_TYPES: tuple[str, ...] = (
    "run_started",
    "agent_input",
    "model_request",
    "model_response",
    "tool_requested",
    "policy_decision",
    "tool_executed",
    "tool_result",
    "security_event",
    "agent_output",
    "run_completed",
    "run_failed",
)


def _as_utc(value: datetime) -> datetime:
    """Require an explicit timezone and normalize to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware (use UTC)")
    return value.astimezone(timezone.utc)


class UsageCounts(BaseModel):
    """Aggregate token usage recorded on ``run_completed``."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class _EventBase(BaseModel):
    """Fields shared by every trace event."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = TRACE_SCHEMA_VERSION
    run_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    parent_event_id: str | None = None
    seq: int = Field(ge=0)
    timestamp: datetime
    agent_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    scenario: str = Field(min_length=1)
    event_type: str

    @field_validator("timestamp")
    @classmethod
    def _timestamp_utc(cls, value: datetime) -> datetime:
        return _as_utc(value)


class RunStartedEvent(_EventBase):
    event_type: Literal["run_started"] = "run_started"
    config_ref: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    seed: int | None = None
    temperature: float | None = None


class AgentInputEvent(_EventBase):
    event_type: Literal["agent_input"] = "agent_input"
    input_ref: str = Field(min_length=1)
    task: str | None = None


class ModelRequestEvent(_EventBase):
    event_type: Literal["model_request"] = "model_request"
    messages_hash: str = Field(min_length=1)
    tool_specs_hash: str = Field(min_length=1)
    temperature: float | None = None
    seed: int | None = None


class ModelResponseEvent(_EventBase):
    event_type: Literal["model_response"] = "model_response"
    response_hash: str = Field(min_length=1)
    finish_reason: str | None = None
    usage: UsageCounts | None = None
    latency_ms: float | None = None
    text_ref: str | None = None


class ToolRequestedEvent(_EventBase):
    event_type: Literal["tool_requested"] = "tool_requested"
    tool_name: str = Field(min_length=1)
    args_hash: str = Field(min_length=1)
    args_redacted: dict | None = None


class PolicyDecisionEvent(_EventBase):
    event_type: Literal["policy_decision"] = "policy_decision"
    decision: Literal["allow", "deny", "require_approval"]
    matched_rule: str | None = None
    reason: str


class ToolExecutedEvent(_EventBase):
    event_type: Literal["tool_executed"] = "tool_executed"
    tool_name: str = Field(min_length=1)
    started_at: datetime | None = None

    @field_validator("started_at")
    @classmethod
    def _started_at_utc(cls, value: datetime | None) -> datetime | None:
        return None if value is None else _as_utc(value)


class ToolResultEvent(_EventBase):
    event_type: Literal["tool_result"] = "tool_result"
    ok: bool
    result_hash: str = Field(min_length=1)
    error: str | None = None
    side_effects: list[str] | None = None


class SecurityEvent(_EventBase):
    event_type: Literal["security_event"] = "security_event"
    label: str = Field(min_length=1)
    severity: Literal["info", "low", "medium", "high", "critical"]
    evidence: dict | None = None


class AgentOutputEvent(_EventBase):
    event_type: Literal["agent_output"] = "agent_output"
    output_hash: str = Field(min_length=1)
    answer_redacted: str | None = None


class RunCompletedEvent(_EventBase):
    event_type: Literal["run_completed"] = "run_completed"
    steps: int = Field(ge=0)
    duration_ms: float = Field(ge=0)
    usage_total: UsageCounts | None = None


class RunFailedEvent(_EventBase):
    event_type: Literal["run_failed"] = "run_failed"
    error_type: str = Field(min_length=1)
    message: str


#: Discriminated union of every event type.
TraceEvent = Annotated[
    Union[
        RunStartedEvent,
        AgentInputEvent,
        ModelRequestEvent,
        ModelResponseEvent,
        ToolRequestedEvent,
        PolicyDecisionEvent,
        ToolExecutedEvent,
        ToolResultEvent,
        SecurityEvent,
        AgentOutputEvent,
        RunCompletedEvent,
        RunFailedEvent,
    ],
    Field(discriminator="event_type"),
]


class TraceEventEnvelope(RootModel[TraceEvent]):
    """Single-event envelope.

    Exists so the versioned JSON Schema can be derived from (and checked
    against) the pydantic models.
    """


def trace_json_schema() -> dict[str, Any]:
    """Return the JSON Schema for trace events.

    Each concrete event gives ``event_type`` a default so it can be constructed
    ergonomically, which would otherwise drop the discriminator from
    ``required`` in the generated schema. A dictionary missing ``event_type``
    whose remaining fields happen to fit a single variant would then validate.
    This normalizes the contract by re-adding ``event_type`` to every variant's
    ``required`` list. Pydantic already rejects such input on the model path.
    """
    schema = TraceEventEnvelope.model_json_schema()
    for definition in schema.get("$defs", {}).values():
        properties = definition.get("properties", {})
        if "event_type" not in properties:
            continue
        required = definition.setdefault("required", [])
        if "event_type" not in required:
            required.append("event_type")
    return schema
