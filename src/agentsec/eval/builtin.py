"""The built-in trace evaluator: descriptive counts over existing events.

Given a run's trace (the same events the recorder wrote), :class:`TraceEvaluator`
returns counts and flags that are read straight off the events. It is a pure
function of its input: no clock, no randomness, no network, no model, no tool
execution, no trace mutation. Evaluating the same input twice yields an equal
result.

What it deliberately does **not** do: execute anything, reinterpret a policy
decision, infer success from a request alone, or compute any score/rating.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from ..errors import EvaluationError
from ..trace.schema import TRACE_EVENT_TYPES
from ..trace.writer import read_events
from .base import EvaluationInput, EvaluationResult, EventRef, RunOutcome

#: Terminal event types.
_TERMINAL = ("run_completed", "run_failed")
#: Event types that must reference a preceding ``tool_requested``.
_TOOL_CHILD_EVENTS = ("policy_decision", "tool_executed", "tool_result")
#: Fixed decision keys so the result shape is stable.
_DECISION_KEYS = ("allow", "deny", "require_approval")
#: Observable tool-result outcomes.
_RESULT_OUTCOMES = (
    "ok",
    "error",
    "denied",
    "pending_approval",
    "not_executed",
    "no_result",
)
#: Descriptive aliases that read naturally in reports; each maps 1:1 to an event
#: type, so no number is invented or combined.
_DERIVED_METRICS: dict[str, str] = {
    "model_calls": "model_request",
    "tool_requests": "tool_requested",
    "tool_executions": "tool_executed",
    "tool_results": "tool_result",
    "agent_outputs": "agent_output",
    "security_events": "security_event",
}


class TraceEvaluator:
    """Deterministic, read-only evaluation of one run's trace events."""

    #: Static implementation identifier; never generated from the input.
    VERSION = "v1"

    @property
    def version(self) -> str:
        return self.VERSION

    # -- entry points ----------------------------------------------------------
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        """Return a deterministic :class:`EvaluationResult` for ``data``."""
        events = data.events
        warnings: list[str] = []
        if not events:
            warnings.append("trace is empty")
        counts: Counter[str] = Counter()
        decisions: Counter[str] = Counter()
        tool_calls: Counter[str] = Counter()
        tool_results: Counter[str] = Counter()
        evidence: list[EventRef] = []
        seq_values: list[int] = []

        run_id = data.run_id
        scenario = data.scenario
        first_run_id: str | None = None
        first_scenario: str | None = None
        tool_request_ids: set[str] = set()
        model_request_ids: set[str] = set()
        # tool_requested id -> aggregate of its associated child events
        associated: dict[str, dict[str, Any]] = {}
        last_terminal: str | None = None
        step_limit = False

        for index, event in enumerate(events):
            event_type = event.get("event_type")
            if not isinstance(event_type, str) or not event_type:
                warnings.append(f"unclassified event at index {index}")
                continue

            counts[event_type] += 1
            seq = event.get("seq")
            if isinstance(seq, int):
                seq_values.append(seq)
            event_id = event.get("event_id")
            evidence.append(
                EventRef(
                    seq=seq if isinstance(seq, int) else None,
                    event_id=event_id if isinstance(event_id, str) else "",
                    event_type=event_type,
                )
            )
            if first_run_id is None and isinstance(event.get("run_id"), str):
                first_run_id = event["run_id"]
            if first_scenario is None and isinstance(event.get("scenario"), str):
                first_scenario = event["scenario"]

            if event_type == "tool_requested":
                if isinstance(event_id, str):
                    tool_request_ids.add(event_id)
                    associated[event_id] = {"name": str(event.get("tool_name", "unknown"))}
                tool_calls[str(event.get("tool_name", "unknown"))] += 1
            elif event_type == "model_request":
                if isinstance(event_id, str):
                    model_request_ids.add(event_id)
            elif event_type == "policy_decision":
                decisions[str(event.get("decision"))] += 1
                self._attach(associated, event, "decision", event.get("decision"))
            elif event_type == "tool_executed":
                self._attach(associated, event, "executed", True)
            elif event_type == "tool_result":
                self._attach(associated, event, "result_ok", bool(event.get("ok")))
            elif event_type == "run_failed":
                last_terminal = event_type
                error_type = event.get("error_type")
                step_limit = step_limit or error_type == "MaxStepsExceeded"
            elif event_type == "run_completed":
                last_terminal = event_type

        self._check_correspondence(
            events, tool_request_ids, model_request_ids, warnings
        )
        self._classify_tool_results(associated, tool_results, warnings)

        if seq_values != sorted(seq_values) or len(set(seq_values)) != len(seq_values):
            warnings.append("event seq values are not strictly increasing")
        if counts["run_started"] == 0:
            warnings.append("missing run_started event")
        terminal_count = counts["run_completed"] + counts["run_failed"]
        if terminal_count == 0:
            warnings.append("no terminal event (run_completed/run_failed)")
        elif terminal_count > 1:
            warnings.append("multiple terminal events")

        status = self._status(counts, last_terminal, step_limit)

        metrics = {name: int(counts.get(name, 0)) for name in TRACE_EVENT_TYPES}
        for alias, source in _DERIVED_METRICS.items():
            metrics[alias] = int(counts.get(source, 0))
        metrics["total_events"] = len(events)

        return EvaluationResult(
            version=self.VERSION,
            run_id=run_id if run_id is not None else first_run_id,
            scenario=scenario if scenario is not None else first_scenario,
            status=status,
            metrics=metrics,
            decisions={key: int(decisions.get(key, 0)) for key in _DECISION_KEYS},
            tool_calls={key: int(tool_calls[key]) for key in sorted(tool_calls)},
            tool_results={key: int(tool_results.get(key, 0)) for key in _RESULT_OUTCOMES},
            flags={
                "has_run_started": counts["run_started"] > 0,
                "has_terminal_event": terminal_count > 0,
                "produced_final_output": counts["agent_output"] > 0,
                "reached_step_limit": step_limit,
                "has_tool_requests": counts["tool_requested"] > 0,
            },
            evidence=evidence,
            warnings=warnings,
        )

    def evaluate_trace(self, path: str | Path) -> EvaluationResult:
        """Read a JSONL trace file and evaluate it.

        Raises :class:`EvaluationError` if the file cannot be read at all;
        content problems are reported as warnings instead.
        """
        resolved = Path(path)
        try:
            events = read_events(resolved)
        except (OSError, ValueError) as exc:
            raise EvaluationError(f"could not read trace {resolved}: {exc}") from exc
        return self.evaluate(EvaluationInput.from_events(events))

    # -- helpers ---------------------------------------------------------------
    @staticmethod
    def _attach(
        associated: dict[str, dict[str, Any]],
        event: Mapping[str, Any],
        key: str,
        value: Any,
    ) -> None:
        parent = event.get("parent_event_id")
        entry = associated.get(parent) if isinstance(parent, str) else None
        if entry is not None:
            entry[key] = value

    @staticmethod
    def _check_correspondence(
        events: list[dict[str, Any]],
        tool_request_ids: set[str],
        model_request_ids: set[str],
        warnings: list[str],
    ) -> None:
        for event in events:
            event_type = event.get("event_type")
            parent = event.get("parent_event_id")
            if event_type in _TOOL_CHILD_EVENTS:
                if not isinstance(parent, str) or parent not in tool_request_ids:
                    warnings.append(
                        f"{event_type} has no matching tool_requested event"
                    )
            elif event_type == "model_response":
                if not isinstance(parent, str) or parent not in model_request_ids:
                    warnings.append(
                        "model_response has no matching model_request event"
                    )

    @staticmethod
    def _classify_tool_results(
        associated: dict[str, dict[str, Any]],
        tool_results: Counter[str],
        warnings: list[str],
    ) -> None:
        for entry in associated.values():
            if "result_ok" not in entry:
                tool_results["no_result"] += 1
                warnings.append("tool_requested without a tool_result")
                continue
            if "executed" in entry:
                tool_results["ok" if entry["result_ok"] else "error"] += 1
            else:
                decision = entry.get("decision")
                if decision == "deny":
                    tool_results["denied"] += 1
                elif decision == "require_approval":
                    tool_results["pending_approval"] += 1
                else:
                    tool_results["not_executed"] += 1

    @staticmethod
    def _status(
        counts: Counter[str], last_terminal: str | None, step_limit: bool
    ) -> RunOutcome:
        if counts["run_completed"] == 0 and counts["run_failed"] == 0:
            return RunOutcome.INCOMPLETE
        if last_terminal == "run_completed":
            return RunOutcome.COMPLETED
        if step_limit:
            return RunOutcome.STEP_LIMIT
        return RunOutcome.FAILED


__all__ = ["TraceEvaluator"]
