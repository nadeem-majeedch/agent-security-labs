"""Deterministic, read-only comparison of two existing traces.

Given two JSONL traces a run already produced, :func:`compare_traces` reports
**what structurally changed between them** — event counts, the event-type
distribution, the ordered event sequence, and the descriptive results the
existing :class:`~agentsec.eval.TraceEvaluator` already produces.

It is deliberately narrow and honest about its limits:

* It reuses ``read_events`` and ``TraceEvaluator`` — it does not re-parse events
  or re-derive evaluation semantics.
* It invents **no score, ranking, similarity or "better/worse" judgement**. It is
  a factual structural comparison only.
* Events are aligned **by position only**. No semantic alignment (matching an
  event in one trace to an "equivalent" event in the other) is attempted, because
  no such equivalence is defined by the trace model; that limitation is stated in
  the output rather than guessed at.
* The output contains **no timestamps, absolute paths, host details or generated
  identifiers**, so the same two input traces always render the same bytes.

The comparison output is a plain dictionary (JSON-ready); :func:`render_comparison`
renders it as concise text.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .errors import EvaluationError
from .eval import EvaluationInput, TraceEvaluator
from .trace.schema import TRACE_EVENT_TYPES
from .trace.writer import read_events

#: Schema version of the comparison document (purely additive structure).
COMPARISON_SCHEMA_VERSION = "1"

#: The alignment limitation, stated verbatim in every comparison.
ALIGNMENT_NOTE = (
    "events are aligned by position only; no semantic alignment is attempted"
)

#: Label used for an event whose ``event_type`` is missing or not a string.
_UNCLASSIFIED = "(no event_type)"

#: Evaluator result sections compared, in a fixed order.
_EVALUATOR_MAPPINGS: tuple[tuple[str, str], ...] = (
    ("decisions", "decisions"),
    ("tool_results", "tool_results"),
    ("tool_calls", "tool_calls"),
    ("flags", "flags"),
)


def load_trace(path: str | Path) -> list[dict[str, Any]]:
    """Read one JSONL trace, raising :class:`EvaluationError` for bad input.

    A missing file, an unreadable file or a malformed line is an input problem,
    reported the same way the ``evaluate`` command reports it — as a clean error,
    never a partial comparison or a stack trace.
    """
    resolved = Path(path)
    try:
        return read_events(resolved)
    except (OSError, ValueError) as exc:
        raise EvaluationError(f"could not read trace {resolved}: {exc}") from exc


def _type_label(event: dict[str, Any]) -> str:
    value = event.get("event_type")
    if isinstance(value, str) and value:
        return value
    return _UNCLASSIFIED


def _first(events: list[dict[str, Any]], key: str) -> str | None:
    for event in events:
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _ordered_types(counts: Counter[str]) -> list[str]:
    """Return event-type labels in a deterministic order.

    Canonical schema order first, then any unknown types alphabetically, with the
    unclassified label always last.
    """
    known = [name for name in TRACE_EVENT_TYPES if name in counts]
    others = sorted(name for name in counts if name not in TRACE_EVENT_TYPES and name != _UNCLASSIFIED)
    tail = [_UNCLASSIFIED] if _UNCLASSIFIED in counts else []
    return known + others + tail


def _sequence_comparison(a_types: list[str], b_types: list[str]) -> dict[str, Any]:
    """Compare two ordered event-type sequences by position only."""
    n, m = len(a_types), len(b_types)
    changed = [
        {"index": index, "a": a_types[index], "b": b_types[index]}
        for index in range(min(n, m))
        if a_types[index] != b_types[index]
    ]
    only_in_a = [
        {"index": index, "event_type": a_types[index]} for index in range(m, n)
    ]
    only_in_b = [
        {"index": index, "event_type": b_types[index]} for index in range(n, m)
    ]
    return {
        "identical": n == m and not changed,
        "length_a": n,
        "length_b": m,
        "changed": changed,
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
    }


def _evaluator_differences(
    a_result: Any, b_result: Any
) -> list[dict[str, Any]]:
    """Return the evaluator fields that differ between the two results."""
    differences: list[dict[str, Any]] = []
    if a_result.status != b_result.status:
        differences.append(
            {
                "section": "status",
                "key": "status",
                "a": a_result.status.value,
                "b": b_result.status.value,
            }
        )
    for section, attribute in _EVALUATOR_MAPPINGS:
        a_map = getattr(a_result, attribute)
        b_map = getattr(b_result, attribute)
        for key in sorted(set(a_map) | set(b_map)):
            if a_map.get(key) != b_map.get(key):
                differences.append(
                    {"section": section, "key": key, "a": a_map.get(key), "b": b_map.get(key)}
                )
    if list(a_result.warnings) != list(b_result.warnings):
        differences.append(
            {
                "section": "warnings",
                "key": "warnings",
                "a": list(a_result.warnings),
                "b": list(b_result.warnings),
            }
        )
    return differences


def compare_traces(trace_a: str | Path, trace_b: str | Path) -> dict[str, Any]:
    """Compare two existing traces and return a deterministic result mapping.

    Both traces are read through the existing trace reader and evaluated through
    the existing evaluator; neither file is modified and nothing is executed.
    Raises :class:`EvaluationError` if either trace cannot be read.
    """
    a_events = load_trace(trace_a)
    b_events = load_trace(trace_b)

    a_types = [_type_label(event) for event in a_events]
    b_types = [_type_label(event) for event in b_events]
    a_counts: Counter[str] = Counter(a_types)
    b_counts: Counter[str] = Counter(b_types)

    evaluator = TraceEvaluator()
    a_result = evaluator.evaluate(EvaluationInput.from_events(a_events))
    b_result = evaluator.evaluate(EvaluationInput.from_events(b_events))

    distribution = [
        {
            "event_type": name,
            "a": int(a_counts.get(name, 0)),
            "b": int(b_counts.get(name, 0)),
            "delta": int(a_counts.get(name, 0)) - int(b_counts.get(name, 0)),
        }
        for name in _ordered_types(a_counts | b_counts)
    ]

    return {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "trace_a": {
            "run_id": _first(a_events, "run_id"),
            "scenario": _first(a_events, "scenario"),
            "event_count": len(a_events),
        },
        "trace_b": {
            "run_id": _first(b_events, "run_id"),
            "scenario": _first(b_events, "scenario"),
            "event_count": len(b_events),
        },
        "event_count_delta": len(a_events) - len(b_events),
        "event_type_distribution": distribution,
        "sequence": _sequence_comparison(a_types, b_types),
        "evaluator": {
            "status": {"a": a_result.status.value, "b": b_result.status.value},
            "differences": _evaluator_differences(a_result, b_result),
        },
        "notes": [ALIGNMENT_NOTE],
    }


# -- rendering -----------------------------------------------------------------
def _delta(value: int) -> str:
    return f"{value:+d}"


def render_comparison(result: dict[str, Any]) -> str:
    """Render a :func:`compare_traces` result as concise, deterministic text."""
    a = result["trace_a"]
    b = result["trace_b"]
    lines: list[str] = ["trace comparison", "================", ""]

    for label, summary in (("Trace A", a), ("Trace B", b)):
        lines.append(label)
        lines.append(f"  run_id: {summary['run_id'] if summary['run_id'] else '-'}")
        lines.append(f"  scenario: {summary['scenario'] if summary['scenario'] else '-'}")
        lines.append(f"  events: {summary['event_count']}")
        lines.append("")

    lines.append("Validation")
    lines.append("  both traces parsed as JSONL")
    for note in result["notes"]:
        lines.append(f"  {note}")
    lines.append("")

    lines.append("Event counts")
    lines.append(f"  A: {a['event_count']}")
    lines.append(f"  B: {b['event_count']}")
    lines.append(f"  delta: {_delta(result['event_count_delta'])}")
    lines.append("")

    lines.append("Event-type distribution")
    for entry in result["event_type_distribution"]:
        lines.append(
            f"  {entry['event_type']:<18} A {entry['a']}  B {entry['b']}  ({_delta(entry['delta'])})"
        )
    lines.append("")

    lines.append("Sequence differences")
    sequence = result["sequence"]
    if sequence["identical"]:
        lines.append("  event sequences are identical")
    else:
        for change in sequence["changed"]:
            lines.append(f"  index {change['index']}: A {change['a']} | B {change['b']}")
        for item in sequence["only_in_a"]:
            lines.append(f"  only in A: index {item['index']}: {item['event_type']}")
        for item in sequence["only_in_b"]:
            lines.append(f"  only in B: index {item['index']}: {item['event_type']}")
    lines.append("")

    lines.append("Evaluator differences")
    status = result["evaluator"]["status"]
    differences = result["evaluator"]["differences"]
    if not differences:
        lines.append("  none")
    else:
        for difference in differences:
            lines.append(
                f"  {difference['section']}.{difference['key']}: "
                f"{_render_value(difference['a'])} -> {_render_value(difference['b'])}"
            )
    if status["a"] != status["b"] and not any(
        difference["section"] == "status" for difference in differences
    ):
        # Defensive: status difference is normally in ``differences`` already.
        lines.append(f"  status.status: {status['a']} -> {status['b']}")
    return "\n".join(lines)


def _render_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        import json

        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


__all__ = [
    "COMPARISON_SCHEMA_VERSION",
    "ALIGNMENT_NOTE",
    "compare_traces",
    "load_trace",
    "render_comparison",
]
