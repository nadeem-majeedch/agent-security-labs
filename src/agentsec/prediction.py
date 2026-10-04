"""Deterministic, read-only comparison of a learner's prediction to a trace.

A *prediction* is a small YAML document of observable expectations — the same
vocabulary as a lab's ``scenario.yaml`` ``expected`` block. :func:`check_prediction`
reads an **existing** trace, evaluates it with the existing
:class:`~agentsec.eval.TraceEvaluator`, builds the observable values, and compares
them against the prediction, reporting what matched and what did not.

It reuses the scenario expectation representation (:class:`ExpectedObservation`),
its match rules and its check record (:class:`ObservationCheck`) rather than
defining a second expectation model. It is deliberately narrow and honest:

* It reports predicted vs observed and nothing else. There is **no** score,
  threshold, confidence, risk, similarity, effectiveness or ranking, and a match
  is **not** evidence of security, correctness or effectiveness.
* It never runs an experiment, executes a tool, evaluates a policy, calls a model
  or writes a trace. The trace is read only; a mismatch is an experimental
  *result*, not a failure.
* The output contains **no** timestamps, absolute paths, host details or generated
  identifiers, so the same two inputs always render the same bytes.

The result is a plain dictionary (JSON-ready); :func:`render_prediction` renders
it as concise text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .errors import ConfigError, EvaluationError
from .eval import EvaluationInput, TraceEvaluator
from .scenarios.base import (
    ExpectedObservation,
    observation_checks,
    observations_from_evaluation,
)
from .trace.writer import read_events

#: Schema version of the prediction-check document (purely additive structure).
PREDICTION_SCHEMA_VERSION = "1"


def load_prediction(path: str | Path) -> ExpectedObservation:
    """Read a prediction YAML document into an :class:`ExpectedObservation`.

    The document is a mapping of observable fields (the same set a scenario's
    ``expected`` block uses). Malformed YAML, a non-mapping document or an
    unknown/invalid field raises :class:`~agentsec.errors.ConfigError`.
    """
    resolved = Path(path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read prediction {resolved}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(
            f"{resolved}: prediction document must be a mapping, "
            f"got {type(data).__name__}"
        )
    try:
        return ExpectedObservation.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'/'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"{resolved}: invalid prediction: {details}") from exc


def _load_trace(path: str | Path) -> list[dict[str, Any]]:
    """Read one JSONL trace, raising :class:`EvaluationError` for bad input."""
    resolved = Path(path)
    try:
        return read_events(resolved)
    except (OSError, ValueError) as exc:
        raise EvaluationError(f"could not read trace {resolved}: {exc}") from exc


def _first(events: list[dict[str, Any]], key: str) -> str | None:
    for event in events:
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _output_text(events: list[dict[str, Any]]) -> str | None:
    """The agent's final answer, read from the trace's own ``agent_output``."""
    for event in events:
        if event.get("event_type") == "agent_output":
            answer = event.get("answer_redacted")
            if isinstance(answer, str):
                return answer
    return None


def check_prediction(
    trace_path: str | Path, prediction_path: str | Path
) -> dict[str, Any]:
    """Compare a prediction against an existing trace and return a result mapping.

    The trace is read through the existing reader and evaluated through the
    existing evaluator; neither input is modified and nothing is executed. Raises
    :class:`EvaluationError` for an unreadable trace and
    :class:`~agentsec.errors.ConfigError` for a malformed prediction.
    """
    prediction = load_prediction(prediction_path)
    events = _load_trace(trace_path)

    evaluation = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    observed = observations_from_evaluation(
        evaluation, output=_output_text(events)
    )
    checks = observation_checks(prediction, observed)

    check_rows = [
        {
            "name": check.name,
            "predicted": check.expected,
            "observed": check.observed,
            "matched": check.matched,
        }
        for check in checks
    ]
    return {
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "trace": {
            "run_id": _first(events, "run_id"),
            "scenario": _first(events, "scenario"),
            "event_count": len(events),
        },
        "checks": check_rows,
        "matched": [row["name"] for row in check_rows if row["matched"]],
        "mismatched": [row["name"] for row in check_rows if not row["matched"]],
    }


def render_prediction(result: dict[str, Any]) -> str:
    """Render a :func:`check_prediction` result as concise, deterministic text."""
    trace = result["trace"]
    lines = ["Prediction results", "=" * len("Prediction results"), ""]
    lines.append(f"  trace: {trace['run_id'] if trace['run_id'] else '-'}")
    lines.append(f"  scenario: {trace['scenario'] if trace['scenario'] else '-'}")
    lines.append(f"  events: {trace['event_count']}")
    lines.append("")

    checks = result["checks"]
    if not checks:
        lines.append("  (the prediction configures no expectations)")
    for row in checks:
        lines.append(f"  {row['name']}")
        lines.append(f"    predicted: {_render_value(row['predicted'])}")
        lines.append(f"    observed: {_render_value(row['observed'])}")
        lines.append("    MATCH" if row["matched"] else "    MISMATCH")
        lines.append("")

    matched = len(result["matched"])
    mismatched = len(result["mismatched"])
    lines.append(
        f"Summary: {matched} matched, {mismatched} mismatched ({len(checks)} checks)"
    )
    if mismatched:
        lines.append("A mismatch is an experimental result, not a failure.")
    return "\n".join(lines)


def _render_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        import json

        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


__all__ = [
    "PREDICTION_SCHEMA_VERSION",
    "check_prediction",
    "load_prediction",
    "render_prediction",
]
