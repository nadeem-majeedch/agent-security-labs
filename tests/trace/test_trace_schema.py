"""Tests for the versioned trace event models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from agentsec.trace.schema import (
    TRACE_EVENT_TYPES,
    TRACE_SCHEMA_VERSION,
    AgentInputEvent,
    AgentOutputEvent,
    ModelRequestEvent,
    ModelResponseEvent,
    PolicyDecisionEvent,
    RunCompletedEvent,
    RunFailedEvent,
    RunStartedEvent,
    SecurityEvent,
    ToolExecutedEvent,
    ToolRequestedEvent,
    ToolResultEvent,
    TraceEventEnvelope,
)

REQUIRED_EXTRA = {
    "run_started": {"config_ref": "cfg.yaml", "scenario_id": "LAB-01-a"},
    "agent_input": {"input_ref": "sha256:in"},
    "model_request": {"messages_hash": "sha256:m", "tool_specs_hash": "sha256:t"},
    "model_response": {"response_hash": "sha256:r"},
    "tool_requested": {"tool_name": "calculator", "args_hash": "sha256:a"},
    "policy_decision": {"decision": "allow", "reason": "read-only"},
    "tool_executed": {"tool_name": "calculator"},
    "tool_result": {"ok": True, "result_hash": "sha256:res"},
    "security_event": {"label": "prompt_injection", "severity": "high"},
    "agent_output": {"output_hash": "sha256:out"},
    "run_completed": {"steps": 2, "duration_ms": 12.5},
    "run_failed": {"error_type": "MaxStepsExceeded", "message": "boom"},
}


def envelope(header, event_type: str, **extra):
    payload = dict(header)
    payload.update(REQUIRED_EXTRA[event_type])
    payload.update(extra)
    payload["event_type"] = event_type
    return TraceEventEnvelope.model_validate(payload)


def test_schema_version_constant():
    assert TRACE_SCHEMA_VERSION == "1.0"
    assert len(TRACE_EVENT_TYPES) == 12
    assert sorted(TRACE_EVENT_TYPES) == sorted(REQUIRED_EXTRA)


def test_common_header_fields_present_once(base):
    for event_type in TRACE_EVENT_TYPES:
        event = envelope(base(), event_type)
        for field in (
            "run_id",
            "event_id",
            "parent_event_id",
            "seq",
            "timestamp",
            "agent_id",
            "model",
            "scenario",
            "event_type",
        ):
            assert field in event.root.model_dump(), (event_type, field)


def test_every_required_extra_field_is_enforced(base):
    for event_type, fields in REQUIRED_EXTRA.items():
        payload = dict(base())
        payload["event_type"] = event_type
        with pytest.raises(ValidationError):
            TraceEventEnvelope.model_validate(payload)
        # sanity: adding the required extras validates
        assert envelope(base(), event_type) is not None


def test_missing_shared_field_rejected(base):
    payload = {k: v for k, v in base().items() if k != "run_id"}
    payload.update(REQUIRED_EXTRA["run_started"])
    payload["event_type"] = "run_started"
    with pytest.raises(ValidationError):
        TraceEventEnvelope.model_validate(payload)


def test_unknown_event_type_rejected(base):
    payload = dict(base())
    payload["event_type"] = "made_up_event"
    with pytest.raises(ValidationError):
        TraceEventEnvelope.model_validate(payload)


def test_invalid_schema_version_rejected(base):
    payload = dict(base(schema_version="2.0"))
    payload.update(REQUIRED_EXTRA["run_started"])
    payload["event_type"] = "run_started"
    with pytest.raises(ValidationError):
        TraceEventEnvelope.model_validate(payload)


def test_unknown_extra_field_rejected(base):
    with pytest.raises(ValidationError):
        envelope(base(), "run_started", unexpected="nope")


def test_naive_timestamp_rejected(base):
    with pytest.raises(ValidationError):
        RunStartedEvent(**base(timestamp=datetime(2026, 1, 1)), config_ref="c", scenario_id="s")


def test_non_utc_timestamp_is_normalized():
    from datetime import timezone, timedelta

    event = RunStartedEvent(
        **{
            "run_id": "r",
            "event_id": "e",
            "seq": 0,
            "timestamp": datetime(2026, 1, 1, 3, 0, tzinfo=timezone(timedelta(hours=3))),
            "agent_id": "a",
            "model": "m",
            "scenario": "s",
            "config_ref": "c",
            "scenario_id": "s",
        }
    )
    assert event.timestamp.utcoffset().total_seconds() == 0


def test_negative_seq_rejected(base):
    with pytest.raises(ValidationError):
        envelope(base(seq=-1), "run_started")


def test_decision_literal_enforced(base):
    with pytest.raises(ValidationError):
        PolicyDecisionEvent(**base(), decision="maybe", reason="r")


def test_severity_literal_enforced(base):
    with pytest.raises(ValidationError):
        SecurityEvent(**base(), label="x", severity="catastrophic")


def test_event_round_trips_through_json(base):
    event = envelope(base(), "run_completed", steps=3, duration_ms=1.5)
    restored = TraceEventEnvelope.model_validate_json(event.model_dump_json())
    assert restored == event


def test_each_event_class_is_constructible(base):
    instances = [
        RunStartedEvent(**base(), config_ref="c", scenario_id="s"),
        AgentInputEvent(**base(), input_ref="sha256:in"),
        ModelRequestEvent(**base(), messages_hash="m", tool_specs_hash="t"),
        ModelResponseEvent(**base(), response_hash="r"),
        ToolRequestedEvent(**base(), tool_name="calculator", args_hash="a"),
        PolicyDecisionEvent(**base(), decision="deny", reason="r"),
        ToolExecutedEvent(**base(), tool_name="calculator"),
        ToolResultEvent(**base(), ok=False, result_hash="res"),
        SecurityEvent(**base(), label="x", severity="low"),
        AgentOutputEvent(**base(), output_hash="out"),
        RunCompletedEvent(**base(), steps=1, duration_ms=1.0),
        RunFailedEvent(**base(), error_type="E", message="m"),
    ]
    assert len(instances) == 12
