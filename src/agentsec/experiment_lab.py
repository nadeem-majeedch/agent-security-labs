"""Experiment specification: a declarative controlled-experiment definition.

An *experiment specification* is a small YAML document that describes a
**controlled comparison** between two runs of the same base scenario that differ
in exactly one declared intervention. For v0.3.0 the only supported intervention
is a **policy** change.

    same base scenario + same everything else
        control   = base run under the control policy
        treatment = base run under the treatment policy

This module is deliberately narrow. It defines and validates the *specification*
only; it never runs anything, executes a tool, evaluates a policy, writes a
trace or judges an outcome. Execution belongs to a later, separate phase.

Reuse, not reinvention:

* the base run is an existing :class:`~agentsec.experiment.ExperimentConfig`,
  read with the existing strict ``load_experiment_config`` loader;
* ``expected_changes`` and ``expected_invariants`` are the existing
  :class:`~agentsec.scenarios.base.ExpectedObservation` vocabulary, so there is
  no second expectation model;
* policies are validated with the existing ``load_policy`` loader.

What this deliberately does **not** do: score, rank, aggregate, measure
"security", classify pass/fail, or claim causality. A specification states a
hypothesis and the observations that would change or stay the same; whether the
evidence supports the hypothesis is decided later, by a reader or a future
read-only runner — never encoded here as a number.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from .compare import compare_traces
from .errors import ConfigError, PolicyConfigError
from .eval import EvaluationInput, TraceEvaluator
from .experiment import ExperimentConfig, load_experiment_config
from .policy import load_policy
from .scenarios.base import (
    ExpectedObservation,
    observation_checks,
    observations_from_evaluation,
)
from .trace.writer import read_events

#: Schema version of the experiment specification (purely additive structure).
EXPERIMENT_SPEC_SCHEMA_VERSION = "1"

#: Deterministic experiment identifier: a lowercase slug.
_ID_PATTERN = r"^[a-z0-9][a-z0-9._-]*$"


class InterventionType(str, Enum):
    """The kinds of single-variable intervention a specification may declare.

    Only ``policy`` exists today. The enum is the extension point; adding a
    second kind is a deliberate, separate decision and is not part of v0.3.0.
    """

    POLICY = "policy"


def _require_nonempty_path(value: Any) -> Any:
    """Reject an empty/whitespace path reference before ``Path`` coercion.

    ``Path("")`` silently becomes ``Path(".")``, so the emptiness has to be
    checked on the raw value, before pydantic coerces it.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError("path must be a non-empty string")
    return value


class PolicyIntervention(BaseModel):
    """A single declared intervention: the policy difference between two runs.

    ``control_policy`` and ``treatment_policy`` are both required and must be
    distinct references. Everything else about the two runs is inherited from the
    specification's shared base configuration, so the policy is the only thing
    the specification lets change.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    type: InterventionType
    control_policy: Path
    treatment_policy: Path

    @field_validator("control_policy", "treatment_policy", mode="before")
    @classmethod
    def _paths_are_nonempty(cls, value: Any) -> Any:
        return _require_nonempty_path(value)

    @model_validator(mode="after")
    def _policies_differ(self) -> "PolicyIntervention":
        if self.control_policy == self.treatment_policy:
            raise ValueError(
                "control_policy and treatment_policy must be different references"
            )
        return self


class ExperimentSpec(BaseModel):
    """A validated, declarative controlled-experiment specification.

    Strict (``extra="forbid"``): an unknown field is an error rather than a
    silent no-op, so a typo cannot quietly change what an experiment means. The
    specification carries a hypothesis, exactly one intervention, a shared base
    configuration, the observations expected to change, the observations expected
    to stay the same, and the alternative explanations the author considered.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = Field(default=EXPERIMENT_SPEC_SCHEMA_VERSION, min_length=1)
    experiment_id: str = Field(min_length=1, pattern=_ID_PATTERN)
    title: str = ""
    hypothesis: str = Field(min_length=1)
    #: The shared base run. Both control and treatment are derived from it, so
    #: everything except the policy is held constant by construction.
    base_config: Path
    intervention: PolicyIntervention
    #: An :class:`ExpectedObservation` the **treatment** is expected to satisfy.
    expected_changes: ExpectedObservation = Field(default_factory=ExpectedObservation)
    #: An :class:`ExpectedObservation` **both** runs are expected to satisfy.
    expected_invariants: ExpectedObservation = Field(default_factory=ExpectedObservation)
    #: Non-empty: the author must acknowledge at least one alternative.
    alternative_explanations: list[str] = Field(min_length=1)
    #: Optional bounded conclusion. Echoed, never machine-judged.
    claim: str | None = None

    @field_validator("hypothesis")
    @classmethod
    def _hypothesis_nonempty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("hypothesis must not be empty")
        return value

    @field_validator("base_config", mode="before")
    @classmethod
    def _base_config_nonempty(cls, value: Any) -> Any:
        return _require_nonempty_path(value)

    @field_validator("alternative_explanations")
    @classmethod
    def _alternatives_nonempty(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError("alternative_explanations entries must not be empty")
        return cleaned

    @model_validator(mode="after")
    def _expectations_present(self) -> "ExperimentSpec":
        if not any(True for _ in self.expected_changes.configured()):
            raise ValueError("expected_changes must declare at least one observation")
        if not any(True for _ in self.expected_invariants.configured()):
            raise ValueError(
                "expected_invariants must declare at least one observation"
            )
        return self


def parse_experiment_spec(data: Any) -> ExperimentSpec:
    """Validate an already-parsed specification mapping.

    Raises :class:`~agentsec.errors.ConfigError` for a non-mapping document or
    any invalid field. Nothing is read from disk and nothing is created.
    """
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(
            f"experiment specification must be a mapping, got {type(data).__name__}"
        )
    try:
        return ExperimentSpec.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'/'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"invalid experiment specification: {details}") from exc


def load_experiment_spec(path: str | Path) -> ExperimentSpec:
    """Read ``path`` as YAML and return a validated :class:`ExperimentSpec`.

    Malformed YAML, a non-mapping document, a missing file or an invalid field
    raises :class:`~agentsec.errors.ConfigError`. The specification references
    other files (the base config and the two policies); those are validated
    separately by :func:`validate_experiment_files`.
    """
    resolved = Path(path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read experiment specification {resolved}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    try:
        return parse_experiment_spec(data)
    except ConfigError as exc:
        raise ConfigError(f"{resolved}: {exc}") from exc


@dataclass(frozen=True)
class ResolvedExperiment:
    """The files a validated specification points at, all confirmed to load.

    This is the hand-off to a future read-only runner: the shared base
    configuration plus the two policy paths. It performs no execution.
    """

    base_config: ExperimentConfig
    control_policy: Path
    treatment_policy: Path


def validate_experiment_files(
    spec: ExperimentSpec, *, root: str | Path
) -> ResolvedExperiment:
    """Resolve and load the base config and both policies named by ``spec``.

    ``root`` is the directory the specification's relative paths are resolved
    against. A missing or malformed base configuration raises
    :class:`~agentsec.errors.ConfigError`; a missing or malformed policy raises
    :class:`~agentsec.errors.PolicyConfigError`, re-raised here as a
    :class:`~agentsec.errors.ConfigError` with the offending path for context.
    Nothing is executed and nothing is written.
    """
    resolved_root = Path(root)
    base_path = resolved_root / spec.base_config
    control_path = resolved_root / spec.intervention.control_policy
    treatment_path = resolved_root / spec.intervention.treatment_policy

    base_config = load_experiment_config(base_path)
    for label, policy_path in (
        ("control_policy", control_path),
        ("treatment_policy", treatment_path),
    ):
        try:
            load_policy(policy_path)
        except PolicyConfigError as exc:
            raise ConfigError(
                f"{label} {policy_path}: {exc}"
            ) from exc

    return ResolvedExperiment(
        base_config=base_config,
        control_policy=control_path,
        treatment_policy=treatment_path,
    )


# -- controlled experiment runner ----------------------------------------------
#: The intended, and only permitted, differences between the two derived runs.
_INTERVENTION_FIELDS = ("policy_path", "trace_path")

#: A fixed note repeated in every result, stating the causal boundary.
BOUNDED_NOTE = (
    "the observed difference is described, not explained; no causal or security "
    "claim is made, and the result is bounded to this deterministic fixture"
)


class ExperimentStatus(str, Enum):
    """The discrete outcome of a controlled experiment. Never a score.

    Precedence, from strongest to weakest, is ``execution_failed`` then
    ``invariant_violated`` then ``changes_not_observed`` then
    ``changes_observed``.
    """

    CHANGES_OBSERVED = "changes_observed"
    CHANGES_NOT_OBSERVED = "changes_not_observed"
    INVARIANT_VIOLATED = "invariant_violated"
    EXECUTION_FAILED = "execution_failed"


class RunRole(str, Enum):
    """Which side of the controlled comparison a run is."""

    CONTROL = "control"
    TREATMENT = "treatment"


class TraceIdentity(BaseModel):
    """Deterministic identity read from a trace (no paths, no timestamps)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str | None = None
    scenario: str | None = None
    event_count: int


class RunSummary(BaseModel):
    """One side's run: its role, declared policy, terminal status and trace."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    role: RunRole
    policy: str
    status: str
    trace: TraceIdentity


class ChangeOutcome(BaseModel):
    """One ``expected_changes`` observation, against both runs.

    ``observed`` records whether the **treatment** satisfied the expectation; the
    control's value is carried alongside for context. No judgement is implied.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    expected: Any
    control_observed: Any
    treatment_observed: Any
    observed: bool


class InvariantOutcome(BaseModel):
    """One ``expected_invariants`` observation, against both runs.

    ``held`` is true only when **both** runs satisfied the expectation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    expected: Any
    control_observed: Any
    treatment_observed: Any
    held: bool


class ExperimentResult(BaseModel):
    """A deterministic, score-free description of a controlled experiment.

    It carries the experiment identity, both runs, the expected changes and
    invariants as observed (not scored), the author's alternative explanations
    and bounded claim, and the descriptive ``compare_traces`` document. When a
    run could not be completed, ``status`` is ``execution_failed``, ``error``
    names the run, and the unavailable fields are ``None``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str
    experiment_id: str
    title: str
    hypothesis: str
    status: ExperimentStatus
    control: RunSummary | None = None
    treatment: RunSummary | None = None
    expected_changes: list[ChangeOutcome] = Field(default_factory=list)
    expected_invariants: list[InvariantOutcome] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    claim: str | None = None
    comparison: dict[str, Any] | None = None
    error: str | None = None
    notes: list[str] = Field(default_factory=list)


def assert_held_constant(control: ExperimentConfig, treatment: ExperimentConfig) -> None:
    """Verify the two runs differ only in the declared intervention fields.

    Compares the two configurations with ``policy_path`` and ``trace_path``
    excluded, so everything else (task, tools, agent settings, limits, scenario,
    sandbox seed and so on) must be identical. Raises :class:`ConfigError` naming
    the differing fields rather than silently executing a mis-controlled pair.
    """
    control_data = control.model_dump(exclude=set(_INTERVENTION_FIELDS))
    treatment_data = treatment.model_dump(exclude=set(_INTERVENTION_FIELDS))
    if control_data != treatment_data:
        differing = sorted(
            key
            for key in set(control_data) | set(treatment_data)
            if control_data.get(key) != treatment_data.get(key)
        )
        detail = ", ".join(differing) if differing else "shape mismatch"
        raise ConfigError(
            "held-constant invariant violated: control and treatment differ "
            f"beyond {'/'.join(_INTERVENTION_FIELDS)} ({detail})"
        )


def _first(events: list[dict[str, Any]], key: str) -> str | None:
    for event in events:
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _output_text(events: list[dict[str, Any]]) -> str | None:
    """The run's final answer, read from its own ``agent_output`` event."""
    for event in events:
        if event.get("event_type") == "agent_output":
            answer = event.get("answer_redacted")
            if isinstance(answer, str):
                return answer
    return None


def _observables(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the observable values for one run, reusing the evaluator."""
    evaluation = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    return observations_from_evaluation(evaluation, output=_output_text(events))


def _execute_run(
    config: ExperimentConfig,
    execute: Callable[[ExperimentConfig], Any],
    role: RunRole,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Run one configuration and read its trace.

    Returns ``(events, None)`` on success and ``(None, message)`` when the run
    cannot be completed — an executor error, no trace written, or an unreadable
    trace. A failure is reported distinctly, never as an observation.
    """
    try:
        execute(config)
    except Exception as exc:  # noqa: BLE001 - report any executor failure distinctly
        return None, f"{role.value} run failed: {exc}"
    trace_path = config.trace_path
    if trace_path is None or not Path(trace_path).is_file():
        return None, f"{role.value} run produced no trace"
    try:
        return read_events(Path(trace_path)), None
    except (OSError, ValueError) as exc:
        return None, f"{role.value} trace could not be read: {exc}"


def _run_summary(
    role: RunRole,
    policy: str,
    events: list[dict[str, Any]],
) -> RunSummary:
    evaluation = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    return RunSummary(
        role=role,
        policy=policy,
        status=evaluation.status.value,
        trace=TraceIdentity(
            run_id=_first(events, "run_id"),
            scenario=_first(events, "scenario"),
            event_count=len(events),
        ),
    )


def _status(
    *,
    failed: bool,
    invariant_violated: bool,
    change_missing: bool,
) -> ExperimentStatus:
    if failed:
        return ExperimentStatus.EXECUTION_FAILED
    if invariant_violated:
        return ExperimentStatus.INVARIANT_VIOLATED
    if change_missing:
        return ExperimentStatus.CHANGES_NOT_OBSERVED
    return ExperimentStatus.CHANGES_OBSERVED


def run_controlled_experiment(
    spec: ExperimentSpec,
    *,
    execute: Callable[[ExperimentConfig], Any],
    root: str | Path | None = None,
) -> ExperimentResult:
    """Run the control and treatment of ``spec`` and describe the outcome.

    ``execute(config)`` runs one configuration and writes its trace to
    ``config.trace_path``; it is injected so the runner owns no execution engine.
    Both runs happen in a temporary directory that is removed on exit, so the
    repository is never written to.

    The two configurations are derived from the shared base config and differ
    only in ``policy_path``/``trace_path`` (enforced by
    :func:`assert_held_constant`). A specification/file problem raises
    :class:`ConfigError`; a run that cannot be completed yields a result with
    status :attr:`ExperimentStatus.EXECUTION_FAILED` (never an observation).
    Nothing is scored, ranked or claimed.
    """
    resolved_root = Path(root) if root is not None else Path.cwd()
    resolved = validate_experiment_files(spec, root=resolved_root)
    base = resolved.base_config

    control_policy = spec.intervention.control_policy.as_posix()
    treatment_policy = spec.intervention.treatment_policy.as_posix()

    with tempfile.TemporaryDirectory(prefix="agentsec-experiment-") as tmp:
        tmp_dir = Path(tmp)
        control_trace = tmp_dir / "control.jsonl"
        treatment_trace = tmp_dir / "treatment.jsonl"
        control_config = base.model_copy(
            update={
                "policy_path": resolved.control_policy,
                "trace_path": control_trace,
            }
        )
        treatment_config = base.model_copy(
            update={
                "policy_path": resolved.treatment_policy,
                "trace_path": treatment_trace,
            }
        )
        assert_held_constant(control_config, treatment_config)

        control_events, control_error = _execute_run(
            control_config, execute, RunRole.CONTROL
        )
        treatment_events, treatment_error = _execute_run(
            treatment_config, execute, RunRole.TREATMENT
        )

        comparison: dict[str, Any] | None = None
        if control_error is None and treatment_error is None:
            comparison = compare_traces(control_trace, treatment_trace)

    error = control_error or treatment_error
    if error is not None:
        return ExperimentResult(
            schema_version=EXPERIMENT_SPEC_SCHEMA_VERSION,
            experiment_id=spec.experiment_id,
            title=spec.title,
            hypothesis=spec.hypothesis,
            status=ExperimentStatus.EXECUTION_FAILED,
            alternative_explanations=list(spec.alternative_explanations),
            claim=spec.claim,
            error=error,
            notes=[BOUNDED_NOTE],
        )

    # Both runs succeeded: describe them, then check the declared expectations.
    control_obs = _observables(control_events or [])
    treatment_obs = _observables(treatment_events or [])
    control_summary = _run_summary(RunRole.CONTROL, control_policy, control_events or [])
    treatment_summary = _run_summary(
        RunRole.TREATMENT, treatment_policy, treatment_events or []
    )

    change_rows = []
    for check in observation_checks(spec.expected_changes, treatment_obs):
        control_value = next(
            (
                row.observed
                for row in observation_checks(spec.expected_changes, control_obs)
                if row.name == check.name
            ),
            None,
        )
        change_rows.append(
            ChangeOutcome(
                name=check.name,
                expected=check.expected,
                control_observed=control_value,
                treatment_observed=check.observed,
                observed=check.matched,
            )
        )

    invariant_rows = []
    treatment_invariants = {
        row.name: row for row in observation_checks(spec.expected_invariants, treatment_obs)
    }
    for control_check in observation_checks(spec.expected_invariants, control_obs):
        treatment_check = treatment_invariants[control_check.name]
        invariant_rows.append(
            InvariantOutcome(
                name=control_check.name,
                expected=control_check.expected,
                control_observed=control_check.observed,
                treatment_observed=treatment_check.observed,
                held=control_check.matched and treatment_check.matched,
            )
        )

    failed = (
        control_summary.status != "completed" or treatment_summary.status != "completed"
    )
    status = _status(
        failed=failed,
        invariant_violated=any(not row.held for row in invariant_rows),
        change_missing=any(not row.observed for row in change_rows),
    )

    return ExperimentResult(
        schema_version=EXPERIMENT_SPEC_SCHEMA_VERSION,
        experiment_id=spec.experiment_id,
        title=spec.title,
        hypothesis=spec.hypothesis,
        status=status,
        control=control_summary,
        treatment=treatment_summary,
        expected_changes=change_rows,
        expected_invariants=invariant_rows,
        alternative_explanations=list(spec.alternative_explanations),
        claim=spec.claim,
        comparison=comparison,
        notes=[BOUNDED_NOTE],
    )


__all__ = [
    "BOUNDED_NOTE",
    "EXPERIMENT_SPEC_SCHEMA_VERSION",
    "ChangeOutcome",
    "ExperimentResult",
    "ExperimentSpec",
    "ExperimentStatus",
    "InterventionType",
    "InvariantOutcome",
    "PolicyIntervention",
    "ResolvedExperiment",
    "RunRole",
    "RunSummary",
    "TraceIdentity",
    "assert_held_constant",
    "load_experiment_spec",
    "parse_experiment_spec",
    "run_controlled_experiment",
    "validate_experiment_files",
]
