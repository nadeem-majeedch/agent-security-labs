"""Tests for the JSONL trace writer/reader."""

from __future__ import annotations

import json

from agentsec.trace.redact import Redactor
from agentsec.trace.schema import RunCompletedEvent, RunStartedEvent
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events, serialize_event, write_event, write_events


def started(base, **overrides):
    return RunStartedEvent(**base(config_ref="cfg.yaml", scenario_id="LAB-01-a", **overrides))


def completed(base, **overrides):
    return RunCompletedEvent(**base(seq=1, event_id="e1", steps=1, duration_ms=1.0, **overrides))


def test_serialize_event_is_single_line_json(base):
    line = serialize_event(started(base))
    assert "\n" not in line
    assert json.loads(line)["event_type"] == "run_started"


def test_serialize_event_is_deterministic(base):
    event = started(base)
    assert serialize_event(event) == serialize_event(event)


def test_write_event_creates_file(tmp_path, base):
    path = tmp_path / "nested" / "trace.jsonl"
    write_event(path, started(base))
    assert path.is_file()
    assert len(path.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_write_events_appends(tmp_path, base):
    path = tmp_path / "trace.jsonl"
    write_event(path, started(base))
    write_events(path, [completed(base)])
    events = read_events(path)
    assert [e["event_type"] for e in events] == ["run_started", "run_completed"]


def test_written_trace_validates(tmp_path, base):
    path = tmp_path / "trace.jsonl"
    write_events(path, [started(base), completed(base)])
    assert validate_jsonl(path).ok


def test_read_events_round_trips(tmp_path, base):
    path = tmp_path / "trace.jsonl"
    event = started(base)
    write_event(path, event)
    assert read_events(path)[0] == json.loads(serialize_event(event))


def test_redaction_applied_on_write(tmp_path, base):
    path = tmp_path / "trace.jsonl"
    event = started(base).model_copy(update={"config_ref": "sk-abcdefghijklmnop1234"})
    write_event(path, event, redactor=Redactor())
    contents = path.read_text(encoding="utf-8")
    assert "sk-abcdefghijklmnop1234" not in contents
    assert "[REDACTED:openai_key]" in contents


def test_no_redaction_when_no_redactor_supplied(tmp_path, base):
    path = tmp_path / "trace.jsonl"
    event = started(base).model_copy(update={"config_ref": "literal-value"})
    write_event(path, event)
    assert "literal-value" in path.read_text(encoding="utf-8")
