"""Offline self-check for the canonical student labs.

This module is a **reproducibility / teaching check only**. It re-runs each
canonical lab through the *existing* deterministic machinery and compares the
result against the lab's *existing* declared expectations
(``scenario.yaml`` ``expected`` observations). It introduces no new metric, no
score, no ranking and no security claim: it only answers "do the labs still
produce the observable results they declare?".

Design notes:

* discovery is explicit and deterministic - the ``labs/`` folder is scanned for
  ``LAB-<nn>-*`` directories (sorted by name), and each must contain a
  ``config.yaml``;
* execution is delegated: the caller supplies a ``run_experiment`` callable so
  this module never holds the agent/runner execution path itself;
* interpretation reuses the existing scenario machinery
  (:class:`~agentsec.scenarios.base.DeclarativeScenario`), so a lab "passes"
  exactly when its existing ``expected`` observations still match;
* a lab without a ``scenario.yaml`` (currently LAB-00, a setup smoke test) is
  checked against a minimal built-in smoke expectation
  (:data:`SMOKE_EXPECTATIONS`) instead of inventing a scenario file.

Nothing here touches the network, a model provider, a database or a subprocess.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .agent import RunStatus
from .errors import AgentSecError, ConfigError
from .eval import RunOutcome
from .experiment import ExperimentConfig, ExperimentResult, load_experiment_config
from .scenarios import (
    DeclarativeScenario,
    ExpectedObservation,
    ObservationCheck,
    ScenarioDef,
    ScenarioStatus,
    load_scenario,
)

#: A canonical lab directory is ``LAB-<two digits>-<slug>``.
LAB_DIR_PATTERN = re.compile(r"^(LAB-\d{2})-(?P<slug>.+)$")

CONFIG_NAME = "config.yaml"
SCENARIO_NAME = "scenario.yaml"

#: Minimal expectations for a lab that ships no ``scenario.yaml`` (LAB-00).
#: This is a smoke check, not a new scenario: the run must simply complete and
#: produce a final answer.
SMOKE_EXPECTATIONS = ExpectedObservation(
    agent_status=RunStatus.COMPLETED,
    evaluation_status=RunOutcome.COMPLETED,
    produced_final_output=True,
)

#: Signature of the caller-supplied executor: run one experiment configuration.
Executor = Callable[[ExperimentConfig], ExperimentResult]


@dataclass(frozen=True)
class LabSpec:
    """One discovered canonical lab."""

    lab_id: str
    slug: str
    directory: Path
    config_path: Path
    scenario_path: Path | None

    @property
    def has_scenario(self) -> bool:
        """Whether the lab declares its expectations in a ``scenario.yaml``."""
        return self.scenario_path is not None


@dataclass(frozen=True)
class LabCheckPlan:
    """A prepared, not-yet-run lab check.

    The experiment carries a caller-supplied ``trace_path`` so a check never
    writes into the repository's default ``runs/`` location.
    """

    lab_id: str
    scenario: DeclarativeScenario
    trace_path: Path

    @property
    def experiment(self) -> ExperimentConfig:
        return self.scenario.definition().experiment


@dataclass(frozen=True)
class LabCheckResult:
    """The outcome of checking one lab."""

    lab_id: str
    status: ScenarioStatus
    detail: str = ""
    checks: tuple[ObservationCheck, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status is ScenarioStatus.PASSED


@dataclass(frozen=True)
class LabSelfCheckReport:
    """The outcome of checking every discovered lab."""

    results: tuple[LabCheckResult, ...] = field(default_factory=tuple)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> tuple[LabCheckResult, ...]:
        return tuple(result for result in self.results if not result.passed)

    @property
    def ok(self) -> bool:
        return not self.failed


def discover_labs(labs_dir: str | Path) -> tuple[LabSpec, ...]:
    """Return every canonical lab under ``labs_dir``, in deterministic order.

    A directory counts as a lab when its name matches ``LAB-<nn>-<slug>`` and it
    contains a ``config.yaml``. Results are sorted by lab id, so the order never
    depends on the filesystem.
    """
    root = Path(labs_dir)
    if not root.is_dir():
        raise ConfigError(f"labs directory not found: {root}")

    specs: list[LabSpec] = []
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        match = LAB_DIR_PATTERN.match(entry.name)
        if match is None:
            continue
        config_path = entry / CONFIG_NAME
        if not config_path.is_file():
            continue
        scenario_path = entry / SCENARIO_NAME
        specs.append(
            LabSpec(
                lab_id=match.group(1),
                slug=match.group(2),
                directory=entry,
                config_path=config_path,
                scenario_path=scenario_path if scenario_path.is_file() else None,
            )
        )
    specs.sort(key=lambda spec: (spec.lab_id, spec.slug))
    return tuple(specs)


def expected_observation(spec: LabSpec) -> ExpectedObservation:
    """The expectations a lab must satisfy.

    A lab with a ``scenario.yaml`` uses its own declared ``expected`` block
    unchanged; a lab without one uses :data:`SMOKE_EXPECTATIONS`.
    """
    if spec.scenario_path is None:
        return SMOKE_EXPECTATIONS
    return load_scenario(spec.scenario_path).definition().expected


def plan_lab_check(spec: LabSpec, out_dir: str | Path) -> LabCheckPlan:
    """Prepare (but do not run) the check for ``spec``.

    The experiment is the lab's canonical ``config.yaml``; only its
    ``trace_path`` is redirected into ``out_dir`` so checking never mutates the
    repository's ``runs/`` output.
    """
    config = load_experiment_config(spec.config_path)
    trace_path = Path(out_dir) / spec.lab_id / "trace.jsonl"
    config = config.model_copy(update={"trace_path": trace_path})
    definition = ScenarioDef(
        scenario_id=spec.lab_id,
        title=f"{spec.lab_id} self-check",
        description=(
            "Offline reproducibility check: the canonical lab run must still "
            "satisfy its declared expected observations."
        ),
        expected=expected_observation(spec),
        experiment=config,
    )
    return LabCheckPlan(
        lab_id=spec.lab_id,
        scenario=DeclarativeScenario(definition),
        trace_path=trace_path,
    )


def check_labs(
    labs_dir: str | Path,
    out_dir: str | Path,
    *,
    run_experiment: Executor,
) -> LabSelfCheckReport:
    """Check every canonical lab under ``labs_dir``.

    ``run_experiment`` is the caller-supplied executor (the composition root
    wires the deterministic MVP stack). A problem with one lab is reported as a
    failed result rather than hiding the others.
    """
    specs = discover_labs(labs_dir)
    results = [check_lab(spec, out_dir, run_experiment=run_experiment) for spec in specs]
    return LabSelfCheckReport(results=tuple(results))


def check_lab(
    spec: LabSpec,
    out_dir: str | Path,
    *,
    run_experiment: Executor,
) -> LabCheckResult:
    """Run and interpret the check for a single lab."""
    try:
        plan = plan_lab_check(spec, out_dir)
        result = run_experiment(plan.experiment)
        outcome = plan.scenario.interpret(result)
    except AgentSecError as exc:
        return LabCheckResult(
            lab_id=spec.lab_id,
            status=ScenarioStatus.FAILED,
            detail=f"{type(exc).__name__}: {exc}",
        )
    return LabCheckResult(
        lab_id=spec.lab_id,
        status=outcome.status,
        detail="" if outcome.status is ScenarioStatus.PASSED else _reason(outcome),
        checks=tuple(outcome.checks),
    )


def _reason(outcome: Any) -> str:
    """A concise human-readable reason a lab did not pass."""
    if outcome.error:
        return str(outcome.error)
    failing = [check for check in outcome.checks if not check.matched]
    if failing:
        return "; ".join(
            f"{check.name} expected {check.expected!r} got {check.observed!r}"
            for check in failing[:3]
        )
    if outcome.warnings:
        return "; ".join(outcome.warnings)
    return f"scenario status was {outcome.status.value}"


def render_report(report: LabSelfCheckReport, *, labs_dir: str | Path | None = None) -> str:
    """Render a human-readable self-check report (no scores, no ranking)."""
    lines = ["LAB SELF-CHECK", "=" * len("LAB SELF-CHECK"), ""]
    width = max((len(result.lab_id) for result in report.results), default=3)
    for result in report.results:
        label = "PASS" if result.passed else "FAIL"
        line = f"{result.lab_id:<{width}}  {label}"
        if not result.passed and result.detail:
            line += f"  ({result.detail})"
        lines.append(line)
    if not report.results:
        lines.append("(no labs discovered)")
    lines.append("")
    lines.append(f"Result: {report.passed_count}/{report.total} labs passed")
    return "\n".join(lines)


def report_to_dict(report: LabSelfCheckReport) -> dict[str, Any]:
    """A JSON-serialisable view of a self-check report."""
    return {
        "labs": [
            {
                "lab": result.lab_id,
                "status": result.status.value,
                "passed": result.passed,
                "detail": result.detail,
            }
            for result in report.results
        ],
        "passed": report.passed_count,
        "total": report.total,
        "ok": report.ok,
    }


__all__ = [
    "LabSpec",
    "LabCheckPlan",
    "LabCheckResult",
    "LabSelfCheckReport",
    "SMOKE_EXPECTATIONS",
    "discover_labs",
    "expected_observation",
    "plan_lab_check",
    "check_labs",
    "check_lab",
    "render_report",
    "report_to_dict",
]
