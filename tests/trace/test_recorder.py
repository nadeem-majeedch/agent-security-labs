"""Tests for the append-only TraceRecorder."""

from __future__ import annotations

from datetime import datetime, timezone

from agentsec.trace.recorder import TraceMeta, TraceRecorder
from agentsec.trace.schema import (
    PolicyDecisionEvent,
    RunStartedEvent,
    ToolRequestedEvent,
)
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

FIXED = datetime(2026, 1, 1, tzinfo=timezone.utc)


def recorder(tmp_path, **overrides):
    kwargs = dict(
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    kwargs.update(overrides)
    return TraceRecorder(tmp_path / "trace.jsonl", **kwargs)


def test_build_stamps_header_and_sequence(tmp_path):
    rec = recorder(tmp_path)
    first = rec.build(RunStartedEvent, config_ref="cfg.yaml", scenario_id="LAB-01-a")
    second = rec.build(RunStartedEvent, config_ref="cfg.yaml", scenario_id="LAB-01-a")
    assert first.event_id == "ev-000000"
    assert second.event_id == "ev-000001"
    assert first.seq == 0 and second.seq == 1
    assert first.run_id == "run-1"
    assert first.timestamp == FIXED


def test_emit_writes_a_valid_trace(tmp_path):
    rec = recorder(tmp_path)
    rec.emit_event(RunStartedEvent, config_ref="cfg.yaml", scenario_id="LAB-01-a")
    rec.emit_event(
        ToolRequestedEvent, tool_name="calculator", args_hash="sha256:a"
    )
    rec.emit_event(
        PolicyDecisionEvent, decision="allow", reason="ok", matched_rule="r"
    )
    meta = rec.close()
    assert isinstance(meta, TraceMeta)
    assert meta.event_count == 3
    assert validate_jsonl(rec.path).ok
    assert [e["event_type"] for e in read_events(rec.path)] == [
        "run_started",
        "tool_requested",
        "policy_decision",
    ]


def test_recording_is_deterministic(tmp_path):
    def write(directory):
        rec = TraceRecorder(
            directory / "trace.jsonl",
            run_id="run-1",
            agent_id="agent-1",
            model="mock-v1",
            scenario="LAB-01-a",
            clock=lambda: FIXED,
        )
        rec.emit_event(RunStartedEvent, config_ref="cfg.yaml", scenario_id="LAB-01-a")
        return rec.path.read_text(encoding="utf-8")

    assert write(tmp_path / "a") == write(tmp_path / "b")


def test_redaction_is_applied_before_writing(tmp_path):
    rec = recorder(tmp_path)
    rec.emit_event(
        RunStartedEvent,
        config_ref="sk-abcdefghijklmnop1234",
        scenario_id="LAB-01-a",
    )
    rec.close()
    contents = rec.path.read_text(encoding="utf-8")
    assert "sk-abcdefghijklmnop1234" not in contents
    assert "[REDACTED:openai_key]" in contents


def test_emit_event_returns_the_written_event(tmp_path):
    rec = recorder(tmp_path)
    event = rec.emit_event(RunStartedEvent, config_ref="c", scenario_id="s")
    assert event.event_type == "run_started"
    assert event.event_id == "ev-000000"


def test_close_reports_the_path_and_count(tmp_path):
    rec = recorder(tmp_path)
    rec.emit_event(RunStartedEvent, config_ref="c", scenario_id="s")
    meta = rec.close()
    assert meta.path == tmp_path / "trace.jsonl"
    assert meta.run_id == "run-1"
    assert meta.event_count == 1


def test_build_does_not_write(tmp_path):
    rec = recorder(tmp_path)
    rec.build(RunStartedEvent, config_ref="c", scenario_id="s")
    assert not rec.path.exists()
    assert rec.event_count == 0
