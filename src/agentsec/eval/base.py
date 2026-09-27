"""The evaluator contract: input, result and the evaluator protocol.

The evaluator is a **read-only, descriptive analysis layer**. It consumes the
trace events a run already produced and reports simple, observable counts. It
does not execute tools, call a model, invoke the gateway or policy engine, rerun
the agent, mutate a trace or inspect provider internals.

Every value here is derived directly from an event that exists in the trace. No
formula is invented, nothing is normalized into a score, and nothing claims to
measure "security" beyond what an event plainly records.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class RunOutcome(str, Enum):
    """How the analysed run ended, as observable from terminal events."""

    COMPLETED = "completed"
    FAILED = "failed"
    STEP_LIMIT = "step_limit"
    INCOMPLETE = "incomplete"


class EventRef(BaseModel):
    """A pointer to a single trace event (no payload is copied)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    seq: int | None = None
    event_id: str = ""
    event_type: str


class EvaluationInput(BaseModel):
    """The smallest useful evaluation input.

    It reuses the existing trace representation: a list of already-parsed event
    mappings (as returned by ``agentsec.trace.writer.read_events``). No second
    parallel event model is introduced.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    events: list[dict[str, Any]] = Field(default_factory=list)
    run_id: str | None = None
    scenario: str | None = None

    @classmethod
    def from_events(
        cls,
        events: list[dict[str, Any]],
        *,
        run_id: str | None = None,
        scenario: str | None = None,
    ) -> "EvaluationInput":
        """Build an input from parsed event mappings (copies the list)."""
        return cls(events=[dict(event) for event in events], run_id=run_id, scenario=scenario)


class EvaluationResult(BaseModel):
    """A deterministic, machine-readable summary of one run's trace."""

    model_config = ConfigDict(extra="forbid")

    version: str
    run_id: str | None = None
    scenario: str | None = None
    status: RunOutcome
    #: Counts of observable events, keyed by event type (plus ``total_events``).
    metrics: dict[str, int] = Field(default_factory=dict)
    #: Policy decisions by outcome: ``allow`` / ``deny`` / ``require_approval``.
    decisions: dict[str, int] = Field(default_factory=dict)
    #: Tool requests by tool name.
    tool_calls: dict[str, int] = Field(default_factory=dict)
    #: Tool results by observable outcome: ``ok`` / ``error`` / ``denied`` /
    #: ``pending_approval`` / ``not_executed`` / ``no_result``.
    tool_results: dict[str, int] = Field(default_factory=dict)
    #: Directly observable booleans (never a composite judgement).
    flags: dict[str, bool] = Field(default_factory=dict)
    #: Pointers to the events the numbers were derived from.
    evidence: list[EventRef] = Field(default_factory=list)
    #: Directly observable findings about incomplete/malformed input.
    warnings: list[str] = Field(default_factory=list)


@runtime_checkable
class Evaluator(Protocol):
    """Score a completed run from its trace, using established measurements."""

    @property
    def version(self) -> str:
        """Static implementation identifier (not generated per run)."""
        ...

    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        """Return a deterministic result for ``data`` (never mutates it)."""
        ...
