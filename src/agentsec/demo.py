"""A one-command teaching demonstration: one lab, two policies, one comparison.

Runs a single canonical lab scenario under two different policies, writes the two
traces into a caller-supplied directory (the CLI uses a temporary one), and
compares them with the existing deterministic ``agentsec compare`` logic. It adds
no metric, score, ranking or policy judgement — it exists so the "same lab, two
policies" exercise is reproducible in **one** step.

It owns **no execution engine**: running a configuration is injected as
``execute`` (the CLI supplies the real stack; tests supply a fake). Nothing in the
repository is written — the traces live only in the output directory the caller
owns.

The demonstration is LAB-04 (Tool Misuse) under a permissive policy and under the
lab's least-privilege policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .compare import compare_traces, render_comparison
from .errors import ConfigError
from .experiment import ExperimentConfig, load_experiment_config

#: The demonstration identifier accepted by the CLI.
LAB04_TWO_POLICIES = "lab04-two-policies"

#: The single demonstration's title, shared by the text and JSON renderers.
DEMO_TITLE = "LAB-04 under two policies"

#: Schema version of the JSON demonstration document (purely additive).
DEMO_SCHEMA_VERSION = "1"

#: The lab scenario demonstrated (LAB-04 Tool Misuse), relative to the root.
LAB_CONFIG = Path("labs") / "LAB-04-tool-misuse" / "config.yaml"

#: The two policies, in presentation order: (Trace A, Trace B).
POLICIES: tuple[tuple[str, Path], ...] = (
    ("permissive (allow_all_v1)", Path("policies") / "examples" / "allow_all_v1.yaml"),
    (
        "least privilege (least_privilege_v1)",
        Path("policies") / "examples" / "least_privilege_v1.yaml",
    ),
)

#: The per-run identity only; the experiment itself is LAB-04's own config.
_TRACE_NAMES = ("trace-a.jsonl", "trace-b.jsonl")


@dataclass(frozen=True)
class DemoRun:
    """One policy's run of the shared lab scenario."""

    label: str
    policy_path: Path
    config: ExperimentConfig
    trace_path: Path


@dataclass(frozen=True)
class DemoOutcome:
    """The two runs' labels and policy paths, plus the comparison produced."""

    labels: tuple[str, ...]
    policies: tuple[str, ...]
    comparison: dict[str, Any]


def plan_demo(output_dir: str | Path, root: str | Path) -> list[DemoRun]:
    """Plan the two runs, changing only the policy and the output trace path.

    Both runs carry the **same** experiment (``experiment_id``, task,
    ``mock_script`` and agent); only ``policy_path`` and the output ``trace_path``
    differ.
    """
    root = Path(root)
    output_dir = Path(output_dir)
    base = load_experiment_config(root / LAB_CONFIG)
    runs: list[DemoRun] = []
    for (label, policy), trace_name in zip(POLICIES, _TRACE_NAMES):
        trace_path = output_dir / trace_name
        config = base.model_copy(
            update={"policy_path": root / policy, "trace_path": trace_path}
        )
        runs.append(
            DemoRun(
                label=label,
                policy_path=policy,
                config=config,
                trace_path=trace_path,
            )
        )
    return runs


def run_demo(
    output_dir: str | Path,
    *,
    execute: Callable[[ExperimentConfig], Any],
    root: str | Path | None = None,
) -> DemoOutcome:
    """Run both policies, then compare the two traces with ``compare_traces``.

    ``execute(config)`` must run one configuration and write its trace to
    ``config.trace_path``; it is injected so the demonstration can be tested
    without invoking the real stack. Raises :class:`ConfigError` if a run writes
    no trace; an execution failure propagates unchanged.
    """
    resolved_root = Path(root) if root is not None else Path.cwd()
    runs = plan_demo(output_dir, resolved_root)
    for run in runs:
        execute(run.config)
        if not run.trace_path.is_file():
            raise ConfigError(
                f"the demonstration run wrote no trace at {run.trace_path}"
            )
    comparison = compare_traces(runs[0].trace_path, runs[1].trace_path)
    return DemoOutcome(
        labels=tuple(run.label for run in runs),
        policies=tuple(run.policy_path.as_posix() for run in runs),
        comparison=comparison,
    )


def render_demo(outcome: DemoOutcome) -> str:
    """Render the demo heading (which policy is which) plus the comparison."""
    lines = [DEMO_TITLE, "=" * len(DEMO_TITLE), ""]
    for name, label in zip(("A", "B"), outcome.labels):
        lines.append(f"Trace {name}: {label}")
    lines.append("")
    lines.append(render_comparison(outcome.comparison))
    return "\n".join(lines)


def demo_to_dict(
    outcome: DemoOutcome, *, name: str = LAB04_TWO_POLICIES
) -> dict[str, Any]:
    """Build the machine-readable demonstration document.

    It describes the demonstration (name, title, status), the two runs' labels and
    relative policy paths, and the full ``compare_traces`` result. It reuses that
    comparison rather than recomputing it, and contains **no** timestamps, absolute
    paths, temporary-directory names, host details or generated ids.
    """
    return {
        "schema_version": DEMO_SCHEMA_VERSION,
        "demo": name,
        "title": DEMO_TITLE,
        "status": "ok",
        "policies": [
            {"trace": trace, "label": label, "policy": policy}
            for trace, label, policy in zip(
                ("A", "B"), outcome.labels, outcome.policies
            )
        ],
        "comparison": outcome.comparison,
    }


__all__ = [
    "DEMO_SCHEMA_VERSION",
    "DEMO_TITLE",
    "LAB04_TWO_POLICIES",
    "LAB_CONFIG",
    "POLICIES",
    "DemoOutcome",
    "DemoRun",
    "demo_to_dict",
    "plan_demo",
    "render_demo",
    "run_demo",
]
