"""Tests for schema and semantic trace validation."""

from __future__ import annotations

import json

import pytest

from agentsec.errors import TraceSchemaError
from agentsec.trace.schema import RunCompletedEvent, RunStartedEvent
from agentsec.trace.validate import (
    load_schema,
    schema_path,
    validate_event,
    validate_jsonl,
)


def valid_event(base, **overrides):
    return RunStartedEvent(**base(config_ref="cfg.yaml", scenario_id="LAB-01-a", **overrides))


def test_schema_file_exists_and_is_valid_json():
    path = schema_path()
    assert path.is_file()
    schema = load_schema()
    assert schema["oneOf"], "schema should describe the event union"


def test_load_schema_is_cached():
    assert load_schema() is load_schema()


def test_valid_event_passes(base):
    validate_event(valid_event(base).model_dump(mode="json"))


def test_missing_required_field_rejected(base):
    data = valid_event(base).model_dump(mode="json")
    del data["run_id"]
    with pytest.raises(TraceSchemaError):
        validate_event(data)


def test_wrong_type_rejected(base):
    data = valid_event(base).model_dump(mode="json")
    data["seq"] = "not-a-number"
    with pytest.raises(TraceSchemaError):
        validate_event(data)


def test_unknown_event_type_rejected(base):
    data = valid_event(base).model_dump(mode="json")
    data["event_type"] = "nope"
    with pytest.raises(TraceSchemaError):
        validate_event(data)


def test_missing_event_type_rejected(base):
    data = valid_event(base).model_dump(mode="json")
    del data["event_type"]
    with pytest.raises(TraceSchemaError):
        validate_event(data)


def test_wrong_schema_version_rejected(base):
    data = valid_event(base).model_dump(mode="json")
    data["schema_version"] = "9.9"
    with pytest.raises(TraceSchemaError):
        validate_event(data)


def _write_jsonl(path, events):
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event) + "\n")


def test_validate_jsonl_reports_ok(tmp_path, base):
    events = [
        RunStartedEvent(**base(seq=0, event_id="e0", config_ref="c", scenario_id="s")).model_dump(mode="json"),
        RunCompletedEvent(**base(seq=1, event_id="e1", steps=1, duration_ms=1.0)).model_dump(mode="json"),
    ]
    path = tmp_path / "trace.jsonl"
    _write_jsonl(path, events)
    report = validate_jsonl(path)
    assert report.ok
    assert report.total == 2
    assert report.issues == []


def test_validate_jsonl_reports_line_numbers(tmp_path, base):
    good = RunStartedEvent(**base(seq=0, event_id="e0", config_ref="c", scenario_id="s")).model_dump(mode="json")
    path = tmp_path / "trace.jsonl"
    path.write_text(
        json.dumps(good) + "\n" + "{not json}\n" + json.dumps({"event_type": "nope"}) + "\n",
        encoding="utf-8",
    )
    report = validate_jsonl(path)
    assert not report.ok
    assert report.total == 3
    assert [issue.line for issue in report.issues] == [2, 3]


def test_seq_regression_is_flagged(tmp_path, base):
    first = RunStartedEvent(**base(seq=1, event_id="e0", config_ref="c", scenario_id="s")).model_dump(mode="json")
    second = RunCompletedEvent(**base(seq=0, event_id="e1", steps=1, duration_ms=1.0)).model_dump(mode="json")
    path = tmp_path / "trace.jsonl"
    _write_jsonl(path, [first, second])
    report = validate_jsonl(path)
    assert not report.ok
    assert any("seq must increase" in issue.message for issue in report.issues)


def test_unknown_parent_reference_is_flagged(tmp_path, base):
    event = RunCompletedEvent(
        **base(seq=0, event_id="e1", parent_event_id="missing", steps=1, duration_ms=1.0)
    ).model_dump(mode="json")
    path = tmp_path / "trace.jsonl"
    _write_jsonl(path, [event])
    report = validate_jsonl(path)
    assert not report.ok
    assert any("parent_event_id" in issue.message for issue in report.issues)


def test_semantic_checks_can_be_disabled(tmp_path, base):
    event = RunCompletedEvent(
        **base(seq=0, event_id="e1", parent_event_id="missing", steps=1, duration_ms=1.0)
    ).model_dump(mode="json")
    path = tmp_path / "trace.jsonl"
    _write_jsonl(path, [event])
    assert validate_jsonl(path, semantic=False).ok


def test_blank_lines_are_ignored(tmp_path, base):
    event = RunStartedEvent(**base(seq=0, event_id="e0", config_ref="c", scenario_id="s")).model_dump(mode="json")
    path = tmp_path / "trace.jsonl"
    path.write_text(json.dumps(event) + "\n\n\n", encoding="utf-8")
    report = validate_jsonl(path)
    assert report.ok
    assert report.total == 1
