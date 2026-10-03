"""The command-line interface: a thin user interface over the lab.

The CLI contains **no execution logic**. It loads an experiment configuration,
asks the MVP composition root for a ready
:class:`~agentsec.experiment.runner.ExperimentRunner`, calls ``run`` once, and
renders the :class:`~agentsec.experiment.runner.ExperimentResult`. It never runs
an agent loop, dispatches a tool, evaluates a policy, calls a model or computes a
metric. It reuses the existing evaluator for ``evaluate`` and the existing trace
reader for ``inspect``.

Exit codes:

* ``0`` - the command completed and produced a result. Experimental outcomes
  (a denied tool, a pending approval, a step limit or even an agent failure) are
  *results*, not CLI errors, so they keep exit code ``0``.
* ``1`` - a configuration/usage/input problem (bad or missing config, unknown
  mock script, unreadable or invalid trace, bad arguments), **or** one or more
  labs failing the ``agentsec labs check`` self-check.
* ``2`` - an orchestration failure after a valid configuration (for example a
  trace that could not be written or read).

Only the standard library is used: ``argparse``, ``json``, ``pathlib`` and
``sys``.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Never, Sequence

from .compare import compare_traces, render_comparison
from .demo import LAB04_TWO_POLICIES, demo_to_dict, render_demo, run_demo
from .errors import ConfigError, EvaluationError
from .eval import EvaluationInput, EvaluationResult, TraceEvaluator
from .experiment import ExperimentConfig, ExperimentResult, load_experiment_config
from .mvp import build_mvp_runner
from .selfcheck import check_labs, render_report, report_to_dict
from .trace.writer import read_events

EXIT_OK = 0
EXIT_CONFIG = 1
EXIT_ORCHESTRATION = 2
#: A self-check ran but one or more labs failed their expectations. This is a
#: "the command found a problem" outcome (1), not an orchestration failure.
EXIT_CHECK_FAILED = EXIT_CONFIG


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that reports usage errors with the config exit code."""

    def error(self, message: str) -> Never:  # pragma: no cover - exercised via test
        self.print_usage(sys.stderr)
        self.exit(EXIT_CONFIG, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = _Parser(
        prog="agentsec",
        description="AI Agent Security Lab - run one deterministic experiment or evaluate a trace.",
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="run one experiment from a YAML config")
    run.add_argument("config", help="path to an experiment configuration (YAML)")
    run.add_argument("--json", action="store_true", help="emit the result as JSON")
    run.set_defaults(func=_cmd_run)

    evaluate = sub.add_parser("evaluate", help="evaluate an existing trace (read-only)")
    evaluate.add_argument("trace", help="path to a JSONL trace")
    evaluate.add_argument("--json", action="store_true", help="emit the result as JSON")
    evaluate.set_defaults(func=_cmd_evaluate)

    inspect = sub.add_parser("inspect", help="print a short summary of a trace")
    inspect.add_argument("trace", help="path to a JSONL trace")
    inspect.add_argument(
        "--events",
        action="store_true",
        help="also print each event's payload fields, side effects and run flags",
    )
    inspect.set_defaults(func=_cmd_inspect)

    compare = sub.add_parser(
        "compare", help="compare two existing traces (read-only)"
    )
    compare.add_argument("trace_a", help="path to the first JSONL trace")
    compare.add_argument("trace_b", help="path to the second JSONL trace")
    compare.add_argument("--json", action="store_true", help="emit the comparison as JSON")
    compare.set_defaults(func=_cmd_compare)

    demo = sub.add_parser("demo", help="run a small read-only teaching demonstration")
    demo.add_argument(
        "name",
        choices=[LAB04_TWO_POLICIES],
        help="which demonstration to run",
    )
    demo.add_argument("--json", action="store_true", help="emit the demonstration as JSON")
    demo.set_defaults(func=_cmd_demo)

    labs = sub.add_parser("labs", help="reproducibility utilities for the student labs")
    labs_sub = labs.add_subparsers(dest="labs_command")
    check = labs_sub.add_parser(
        "check", help="verify every canonical lab still meets its declared expectations"
    )
    check.add_argument(
        "--labs-dir",
        default="labs",
        help="directory containing the LAB-xx folders (default: labs)",
    )
    check.add_argument("--json", action="store_true", help="emit the report as JSON")
    check.set_defaults(func=_cmd_labs_check)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if getattr(args, "command", None) is None or func is None:
        parser.print_help(sys.stderr)
        return EXIT_CONFIG
    try:
        return int(func(args))
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except EvaluationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except Exception as exc:  # noqa: BLE001 - orchestration failure
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ORCHESTRATION


# -- commands ------------------------------------------------------------------
def _cmd_run(args: argparse.Namespace) -> int:
    config = load_experiment_config(args.config)
    runner = build_mvp_runner(config)
    result = runner.run(config)

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        _render_result(result)

    return EXIT_ORCHESTRATION if result.error else EXIT_OK


def _cmd_evaluate(args: argparse.Namespace) -> int:
    path = Path(args.trace)
    events = read_events(path)
    result = TraceEvaluator().evaluate(EvaluationInput.from_events(events))

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        _render_evaluation(result)
    return EXIT_OK


def _cmd_labs_check(args: argparse.Namespace) -> int:
    """Run the offline self-check for every canonical lab.

    Each lab runs through the existing deterministic MVP stack into a temporary
    directory, and its result is compared against the lab's existing declared
    expectations. Nothing is written under the repository's ``runs/`` output.
    """
    with tempfile.TemporaryDirectory(prefix="agentsec-labs-check-") as tmp:
        report = check_labs(
            Path(args.labs_dir), Path(tmp), run_experiment=_run_for_self_check
        )

    if args.json:
        print(json.dumps(report_to_dict(report), indent=2))
    else:
        print(render_report(report))
    return EXIT_OK if report.ok else EXIT_CHECK_FAILED


def _run_for_self_check(config: ExperimentConfig) -> ExperimentResult:
    """Run one lab config with the deterministic stack and a fixed clock."""
    runner = build_mvp_runner(config, clock=_fixed_clock)
    return runner.run(config)


def _fixed_clock() -> datetime:
    """A fixed clock so a self-check replay is byte-identical."""
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


def _cmd_compare(args: argparse.Namespace) -> int:
    result = compare_traces(args.trace_a, args.trace_b)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_comparison(result))
    return EXIT_OK


def _cmd_demo(args: argparse.Namespace) -> int:
    """Run a demonstration into a temporary directory and print its result.

    The two traces are written to a temporary directory that is removed on exit,
    so the repository is never written to.
    """
    with tempfile.TemporaryDirectory(prefix="agentsec-demo-") as tmp:
        outcome = run_demo(tmp, execute=_run_demo_config)
    if args.json:
        print(json.dumps(demo_to_dict(outcome, name=args.name), indent=2))
    else:
        print(render_demo(outcome))
    return EXIT_OK


def _run_demo_config(config: ExperimentConfig) -> None:
    """Run one demonstration configuration through the existing MVP stack."""
    runner = build_mvp_runner(config)
    runner.run(config)


def _cmd_inspect(args: argparse.Namespace) -> int:
    path = Path(args.trace)
    events = read_events(path)
    if args.events:
        evaluation = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
        print(render_inspection(events, evaluation, path=path))
        return EXIT_OK
    run_id = next((e.get("run_id") for e in events if e.get("run_id")), None)
    print(f"trace: {path}")
    print(f"run: {run_id}")
    print(f"events: {len(events)}")
    for event in events:
        seq = event.get("seq")
        event_type = event.get("event_type", "?")
        event_id = event.get("event_id", "?")
        parent = event.get("parent_event_id")
        print(f"  {seq:>3}  {event_type:<18} {event_id}  parent={parent}")
    return EXIT_OK


# -- rendering -----------------------------------------------------------------
def _render_result(result: ExperimentResult) -> None:
    print(f"experiment: {result.experiment_id}")
    print(f"run: {result.run_id}")
    print(f"scenario: {result.scenario}")
    print(f"agent status: {result.agent.status.value}")
    print(f"trace: {result.trace_path}")
    if result.evaluation is None:
        print("evaluation: none")
    else:
        _render_evaluation(result.evaluation, indent="")
    if result.error:
        print(f"error: {result.error}")


def _render_evaluation(result: EvaluationResult, indent: str = "") -> None:
    print(f"{indent}evaluation status: {result.status.value}")
    print(f"{indent}tool calls: {_pairs(result.tool_calls)}")
    print(f"{indent}policy decisions: {_pairs(result.decisions)}")
    print(f"{indent}tool results: {_pairs(result.tool_results)}")
    key_metrics = {
        key: result.metrics[key]
        for key in ("model_calls", "tool_requests", "tool_executions", "total_events")
        if key in result.metrics
    }
    print(f"{indent}metrics: {_pairs(key_metrics)}")
    print(f"{indent}warnings: {'; '.join(result.warnings) if result.warnings else 'none'}")


def _pairs(mapping: dict) -> str:
    return " ".join(f"{key}={value}" for key, value in mapping.items()) or "none"


#: Envelope fields shown once per event, so the payload block lists only the
#: fields specific to that event (the same split the field reference uses).
_ENVELOPE_FIELDS = frozenset(
    {
        "run_id",
        "event_id",
        "seq",
        "timestamp",
        "agent_id",
        "model",
        "scenario",
        "schema_version",
        "event_type",
        "parent_event_id",
    }
)


def render_inspection(
    events: list[dict[str, Any]], evaluation: EvaluationResult, *, path: Path
) -> str:
    """Render a detailed, deterministic, read-only view of one trace.

    Reuses the parsed event mappings and the existing evaluator result. Every
    value shown comes from an event the run already produced, or from the
    evaluator's already-computed flags and warnings; nothing is executed,
    nothing is written, and the trace is not modified.
    """
    lines = [f"trace: {path}", f"run: {evaluation.run_id}", f"events: {len(events)}"]
    for index, event in enumerate(events):
        lines.append("")
        lines.append(f"Event {index}")
        lines.append(f"  type: {event.get('event_type', '?')}")
        lines.append(f"  event_id: {event.get('event_id', '?')}")
        lines.append(f"  seq: {event.get('seq')}")
        lines.append(f"  parent: {_display(event.get('parent_event_id'))}")
        payload = {
            key: value for key, value in event.items() if key not in _ENVELOPE_FIELDS
        }
        if payload:
            lines.append("  fields:")
            for key in sorted(payload):
                lines.append(f"    {key}: {_display(payload[key])}")
    lines.append("")
    lines.append("Side effects:")
    effects = [
        (event.get("event_id", "?"), event.get("side_effects"))
        for event in events
        if event.get("side_effects")
    ]
    if effects:
        for event_id, side_effects in effects:
            lines.append(f"  {event_id}  {_display(side_effects)}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Flags:")
    if evaluation.flags:
        for flag in sorted(evaluation.flags):
            lines.append(f"  {flag}: {_display(evaluation.flags[flag])}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("Warnings:")
    if evaluation.warnings:
        lines.extend(f"  {warning}" for warning in evaluation.warnings)
    else:
        lines.append("  none")
    return "\n".join(lines)


def _display(value: object) -> str:
    """A deterministic, readable rendering of a single trace value."""
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
