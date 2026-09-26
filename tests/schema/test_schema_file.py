"""The checked-in trace schema must not drift from the pydantic models."""

from __future__ import annotations

import json

from agentsec.trace.schema import trace_json_schema
from agentsec.trace.validate import schema_path


def test_checked_in_schema_matches_models():
    checked_in = json.loads(schema_path().read_text(encoding="utf-8"))
    generated = trace_json_schema()
    assert checked_in == generated, (
        "schemas/trace/trace_event.v1.schema.json is out of date; "
        "run `py scripts/export_trace_schema.py`"
    )


def test_schema_declares_every_event_type():
    schema = json.loads(schema_path().read_text(encoding="utf-8"))
    mapping = schema["discriminator"]["mapping"]
    assert set(mapping) == {
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
    }
