"""The minimal scenario abstraction.

A scenario describes one controlled experiment and interprets its *observable*
result. It is declarative and read-only:

* :meth:`Scenario.prepare` returns the already-composed
  :class:`~agentsec.experiment.config.ExperimentConfig` the caller runs with the
  existing ``ExperimentRunner``;
* :meth:`Scenario.interpret` compares an :class:`ExperimentResult` against the
  scenario's expectations and returns a :class:`ScenarioOutcome`.

Scenario code never runs the agent, executes a tool, evaluates a policy or
mutates a trace. It only prepares configuration and interprets what the generic
evaluator already observed, so scenario-specific semantics stay out of the
Agent, ToolGateway, PolicyEngine, Evaluator and ExperimentRunner.

The outcome vocabulary is deliberately scenario-oriented (``passed`` /
``failed`` / ``inconclusive``); it is not a security score and nothing is ranked.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterator, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from ..agent import RunStatus
from ..eval import EvaluationResult, EventRef, RunOutcome
from ..experiment.config import ExperimentConfig
from ..experiment.runner import ExperimentResult


class ScenarioStatus(str, Enum):
    """How a scenario's expectations related to the observed run."""

    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class ExpectedObservation(BaseModel):
    """Explicit, optional expectations about a run's observable result.

    Every field that is set produces one check. An expectation is a plain
    comparison against a value the generic evaluator already reports - no field
    is a score and no field is combined with another.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_status: RunStatus | None = None
    evaluation_status: RunOutcome | None = None
    reached_step_limit: bool | None = None
    produced_final_output: bool | None = None
    tool_requests: int | None = Field(default=None, ge=0)
    tool_executions: int | None = Field(default=None, ge=0)
    policy_denials: int | None = Field(default=None, ge=0)
    policy_approvals_required: int | None = Field(default=None, ge=0)
    tool_results_ok: int | None = Field(default=None, ge=0)
    tool_results_denied: int | None = Field(default=None, ge=0)
    tool_results_pending_approval: int | None = Field(default=None, ge=0)
    requested_tools: tuple[str, ...] | None = None
    output_contains: str | None = None

    def configured(self) -> Iterator[tuple[str, Any]]:
        """Yield ``(field_name, expected_value)`` for every set expectation."""
        for name in type(self).model_fields:
            value = getattr(self, name)
            if value is not None:
                yield name, value


class ObservationCheck(BaseModel):
    """One expectation compared against the observed value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    expected: Any
    observed: Any
    matched: bool


class ScenarioDef(BaseModel):
    """Declarative description of one scenario.

    The experiment is **composed**, not copied: a scenario references an existing
    :class:`~agentsec.experiment.config.ExperimentConfig` rather than repeating
    its task, agent, policy or mock-script fields.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(min_length=1)
    title: str = ""
    description: str = ""
    expected: ExpectedObservation = Field(default_factory=ExpectedObservation)
    experiment: ExperimentConfig


class ScenarioOutcome(BaseModel):
    """The result of interpreting a run against a scenario's expectations."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    run_id: str | None = None
    status: ScenarioStatus
    checks: list[ObservationCheck] = Field(default_factory=list)
    #: Reuses the evaluator's existing evidence pointers; no new reference system.
    evidence: list[EventRef] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None


@runtime_checkable
class Scenario(Protocol):
    """Prepare configuration and interpret an experiment's observable result."""

    def definition(self) -> ScenarioDef:
        """The scenario's declarative definition."""
        ...

    def prepare(self) -> ExperimentConfig:
        """Return the experiment configuration to run (no execution)."""
        ...

    def interpret(self, result: ExperimentResult) -> ScenarioOutcome:
        """Compare ``result`` against the scenario's expectations."""
        ...


class DeclarativeScenario:
    """The generic :class:`Scenario` implementation driven by a definition."""

    def __init__(self, definition: ScenarioDef) -> None:
        self._definition = definition

    @property
    def scenario_id(self) -> str:
        return self._definition.scenario_id

    def definition(self) -> ScenarioDef:
        return self._definition

    def prepare(self) -> ExperimentConfig:
        return self._definition.experiment

    def interpret(self, result: ExperimentResult) -> ScenarioOutcome:
        definition = self._definition
        evaluation = result.evaluation
        evidence = list(evaluation.evidence) if evaluation is not None else []
        warnings: list[str] = []

        if evaluation is None:
            return ScenarioOutcome(
                scenario_id=definition.scenario_id,
                run_id=result.run_id,
                status=ScenarioStatus.INCONCLUSIVE,
                checks=[],
                evidence=evidence,
                warnings=warnings,
                error=result.error or "no evaluation available (trace missing or unreadable)",
            )

        warnings.extend(evaluation.warnings)

        expected_run_id = definition.experiment.agent.run_id
        if result.run_id != expected_run_id:
            warnings.append(
                f"result run_id {result.run_id!r} does not match the scenario run_id "
                f"{expected_run_id!r}; cannot attribute the observation"
            )
            return ScenarioOutcome(
                scenario_id=definition.scenario_id,
                run_id=result.run_id,
                status=ScenarioStatus.INCONCLUSIVE,
                checks=[],
                evidence=evidence,
                warnings=warnings,
            )

        observed = _observations(result)
        checks = observation_checks(definition.expected, observed)

        if not checks:
            warnings.append("no expected observations defined; outcome is inconclusive")
            return ScenarioOutcome(
                scenario_id=definition.scenario_id,
                run_id=result.run_id,
                status=ScenarioStatus.INCONCLUSIVE,
                checks=[],
                evidence=evidence,
                warnings=warnings,
            )

        if evaluation.status is RunOutcome.INCOMPLETE:
            warnings.append("evaluation is incomplete; outcome is inconclusive")
            return ScenarioOutcome(
                scenario_id=definition.scenario_id,
                run_id=result.run_id,
                status=ScenarioStatus.INCONCLUSIVE,
                checks=checks,
                evidence=evidence,
                warnings=warnings,
            )

        status = (
            ScenarioStatus.PASSED
            if all(check.matched for check in checks)
            else ScenarioStatus.FAILED
        )
        return ScenarioOutcome(
            scenario_id=definition.scenario_id,
            run_id=result.run_id,
            status=status,
            checks=checks,
            evidence=evidence,
            warnings=warnings,
        )


def _observations(result: ExperimentResult) -> dict[str, Any]:
    """The observable values a scenario may compare against."""
    evaluation = result.evaluation
    assert evaluation is not None  # guarded by the caller
    return {
        "agent_status": result.agent.status,
        "evaluation_status": evaluation.status,
        "reached_step_limit": evaluation.flags.get("reached_step_limit"),
        "produced_final_output": evaluation.flags.get("produced_final_output"),
        "tool_requests": evaluation.metrics.get("tool_requests"),
        "tool_executions": evaluation.metrics.get("tool_executions"),
        "policy_denials": evaluation.decisions.get("deny"),
        "policy_approvals_required": evaluation.decisions.get("require_approval"),
        "tool_results_ok": evaluation.tool_results.get("ok"),
        "tool_results_denied": evaluation.tool_results.get("denied"),
        "tool_results_pending_approval": evaluation.tool_results.get("pending_approval"),
        "requested_tools": tuple(sorted(evaluation.tool_calls)),
        "output_contains": result.agent.output,
    }


def _matches(name: str, expected: Any, observed: Any) -> bool:
    if name == "requested_tools":
        return set(expected) == set(observed or ())
    if name == "output_contains":
        return isinstance(observed, str) and expected in observed
    return expected == observed


def _check(name: str, expected: Any, observed: Any) -> ObservationCheck:
    return ObservationCheck(
        name=name,
        expected=_presentation(expected),
        observed=_presentation(observed),
        matched=_matches(name, expected, observed),
    )


def _presentation(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return list(value)
    return value


#: The observable agent status inferred from an evaluator's terminal outcome,
#: for trace-only observation building (the run-based mapping reads the agent
#: directly). ``RunOutcome.INCOMPLETE`` has no agent-status equivalent.
_AGENT_STATUS_BY_OUTCOME: dict[RunOutcome, RunStatus] = {
    RunOutcome.COMPLETED: RunStatus.COMPLETED,
    RunOutcome.STEP_LIMIT: RunStatus.STEP_LIMIT,
    RunOutcome.FAILED: RunStatus.FAILED,
}


def observation_checks(
    expected: ExpectedObservation, observed: dict[str, Any]
) -> list[ObservationCheck]:
    """Compare ``expected`` against ``observed``, one check per set field.

    This is the scenario's own matching rule (``requested_tools`` by set
    equality, ``output_contains`` by substring, everything else by exact
    equality), exposed so a trace-only caller can reuse it instead of
    re-implementing it. It changes no scenario behaviour.
    """
    return [
        _check(name, value, observed.get(name))
        for name, value in expected.configured()
    ]


def observations_from_evaluation(
    evaluation: EvaluationResult, *, output: str | None = None
) -> dict[str, Any]:
    """Observable values for a prediction, from an evaluator result alone.

    Mirrors the field names of :class:`ExpectedObservation`. Unlike the run-based
    :func:`_observations`, it reads only the existing evaluator result: the agent
    status is inferred from the evaluator's terminal outcome, and
    ``output_contains`` uses the ``output`` the caller read from the trace's own
    ``agent_output`` payload. Nothing here is a score or a new measurement.
    """
    return {
        "agent_status": _AGENT_STATUS_BY_OUTCOME.get(evaluation.status),
        "evaluation_status": evaluation.status,
        "reached_step_limit": evaluation.flags.get("reached_step_limit"),
        "produced_final_output": evaluation.flags.get("produced_final_output"),
        "tool_requests": evaluation.metrics.get("tool_requests"),
        "tool_executions": evaluation.metrics.get("tool_executions"),
        "policy_denials": evaluation.decisions.get("deny"),
        "policy_approvals_required": evaluation.decisions.get("require_approval"),
        "tool_results_ok": evaluation.tool_results.get("ok"),
        "tool_results_denied": evaluation.tool_results.get("denied"),
        "tool_results_pending_approval": evaluation.tool_results.get(
            "pending_approval"
        ),
        "requested_tools": tuple(sorted(evaluation.tool_calls)),
        "output_contains": output,
    }


__all__ = [
    "ScenarioStatus",
    "ExpectedObservation",
    "ObservationCheck",
    "ScenarioDef",
    "ScenarioOutcome",
    "Scenario",
    "DeclarativeScenario",
    "observation_checks",
    "observations_from_evaluation",
]
