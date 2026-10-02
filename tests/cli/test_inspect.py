"""Tests for the richer read-only ``inspect --events`` view (C3).

The formatting is exercised through :func:`agentsec.cli.render_inspection`
directly, and the CLI wrapper through :func:`agentsec.cli.main`. The traces are
written to ``tmp_path`` as plain JSONL, so nothing is executed and the
repository is never touched.
"""

from __future__ import annotations

import json
from pathlib import Path

from agentsec.cli import main, render_inspection
from agentsec.eval import EvaluationInput, TraceEvaluator

_RUN = "run-inspect"


def _event(seq: int, event_type: str, **extra) -> dict:
    event = {
        "schema_version": "1.0",
        "run_id": _RUN,
        "event_id": f"ev-{seq:06d}",
        "parent_event_id": None if seq == 0 else f"ev-{seq - 1:06d}",
        "seq": seq,
        "timestamp": f"2026-01-01T00:00:{seq:02d}+00:00",
        "agent_id": "agent-1",
        "model": "fixture",
        "scenario": "LAB-XX",
        "event_type": event_type,
    }
    event.update(extra)
    return event


def _write_trace(path: Path, events: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )
    return path


def _trace_with_side_effects(path: Path) -> Path:
    return _write_trace(
        path,
        [
            _event(0, "run_started", config_ref="c.yaml", scenario_id="LAB-XX"),
            _event(
                1,
                "tool_result",
                ok=True,
                error=None,
                result_hash="abc",
                side_effects=["deleted 2 row(s) from audit_log"],
            ),
            _event(2, "run_completed", steps=2, duration_ms=0.0, usage_total=None),
        ],
    )


def _trace_without_side_effects(path: Path) -> Path:
    return _write_trace(
        path,
        [
            _event(0, "run_started", config_ref="c.yaml", scenario_id="LAB-XX"),
            _event(2, "run_completed", steps=1, duration_ms=0.0, usage_total=None),
        ],
    )


def _evaluate(path: Path) -> tuple[list[dict], "object"]:
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    result = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    return events, result


# -- underlying formatting function -------------------------------------------


def test_render_inspection_includes_event_information(tmp_path):
    events, result = _evaluate(_trace_with_side_effects(tmp_path / "trace.jsonl"))
    text = render_inspection(events, result, path=tmp_path / "trace.jsonl")
    assert "events: 3" in text
    assert "Event 0" in text
    assert "type: run_started" in text
    assert "event_id: ev-000000" in text
    assert "parent: -" in text  # the first event has no parent
    assert "config_ref: c.yaml" in text  # payload fields are shown


def test_render_inspection_shows_side_effects_when_present(tmp_path):
    events, result = _evaluate(_trace_with_side_effects(tmp_path / "trace.jsonl"))
    text = render_inspection(events, result, path=tmp_path / "trace.jsonl")
    assert "Side effects:" in text
    assert "ev-000001" in text
    assert '["deleted 2 row(s) from audit_log"]' in text


def test_render_inspection_omits_absent_side_effects_safely(tmp_path):
    events, result = _evaluate(_trace_without_side_effects(tmp_path / "trace.jsonl"))
    text = render_inspection(events, result, path=tmp_path / "trace.jsonl")
    # The section is still present, reports "none", and nothing crashes.
    assert "Side effects:" in text
    assert text.split("Side effects:", 1)[1].split("\n", 2)[1].strip() == "none"


def test_render_inspection_shows_flags(tmp_path):
    events, result = _evaluate(_trace_with_side_effects(tmp_path / "trace.jsonl"))
    text = render_inspection(events, result, path=tmp_path / "trace.jsonl")
    assert "Flags:" in text
    for flag in ("has_run_started", "has_terminal_event", "produced_final_output"):
        assert f"{flag}: " in text


def test_render_inspection_is_deterministic(tmp_path):
    path = _trace_with_side_effects(tmp_path / "trace.jsonl")
    first = render_inspection(*_evaluate(path), path=path)
    second = render_inspection(*_evaluate(path), path=path)
    assert first == second


# -- CLI wrapper ---------------------------------------------------------------


def test_inspect_events_cli_prints_the_richer_view(tmp_path, capsys):
    trace = _trace_with_side_effects(tmp_path / "trace.jsonl")
    assert main(["inspect", str(trace), "--events"]) == 0
    out = capsys.readouterr().out
    assert "Event 0" in out
    assert "Side effects:" in out
    assert "Flags:" in out
    assert "tool_result" in out


def test_inspect_events_cli_is_deterministic(tmp_path, capsys):
    trace = _trace_with_side_effects(tmp_path / "trace.jsonl")
    assert main(["inspect", str(trace), "--events"]) == 0
    first = capsys.readouterr().out
    assert main(["inspect", str(trace), "--events"]) == 0
    assert capsys.readouterr().out == first


def test_inspect_events_cli_does_not_modify_the_trace(tmp_path, capsys):
    trace = _trace_with_side_effects(tmp_path / "trace.jsonl")
    before = trace.read_bytes()
    assert main(["inspect", str(trace), "--events"]) == 0
    capsys.readouterr()
    assert trace.read_bytes() == before


def test_inspect_without_events_keeps_the_original_summary(tmp_path, capsys):
    trace = _trace_with_side_effects(tmp_path / "trace.jsonl")
    assert main(["inspect", str(trace)]) == 0
    out = capsys.readouterr().out
    # The original one-line-per-event summary is unchanged.
    assert "events:" in out
    assert "run_started" in out
    assert "parent=ev-000000" in out
    assert "Side effects:" not in out


def test_inspect_events_missing_trace_is_a_config_error(tmp_path, capsys):
    assert main(["inspect", str(tmp_path / "missing.jsonl"), "--events"]) == 1
    assert "error:" in capsys.readouterr().err
