"""The checked-in trace schema must not drift from the pydantic models.

This module guards the **repository** copy, ``schemas/trace/`` - the
documentation-facing artefact that ``README.md`` links to. The packaged copy
that ships inside the wheel, and its identity with this one, are guarded by
``tests/schema/test_packaged_schema.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from agentsec.trace.schema import trace_json_schema

REPOSITORY_SCHEMA = (
    Path(__file__).resolve().parents[2] / "schemas" / "trace" / "trace_event.v1.schema.json"
)


def test_checked_in_schema_matches_models():
    checked_in = json.loads(REPOSITORY_SCHEMA.read_text(encoding="utf-8"))
    generated = trace_json_schema()
    assert checked_in == generated, (
        "schemas/trace/trace_event.v1.schema.json is out of date; "
        "run `py scripts/export_trace_schema.py`"
    )


def test_schema_declares_every_event_type():
    schema = json.loads(REPOSITORY_SCHEMA.read_text(encoding="utf-8"))
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
