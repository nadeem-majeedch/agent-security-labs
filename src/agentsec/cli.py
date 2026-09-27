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
  mock script, unreadable or invalid trace, bad arguments).
* ``2`` - an orchestration failure after a valid configuration (for example a
  trace that could not be written or read).

Only the standard library is used: ``argparse``, ``json``, ``pathlib`` and
``sys``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .errors import ConfigError, EvaluationError
from .eval import EvaluationInput, EvaluationResult, TraceEvaluator
from .experiment import ExperimentResult, load_experiment_config
from .mvp import build_mvp_runner
from .trace.writer import read_events

EXIT_OK = 0
EXIT_CONFIG = 1
EXIT_ORCHESTRATION = 2


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that reports usage errors with the config exit code."""

    def error(self, message: str) -> None:  # pragma: no cover - exercised via test
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
    inspect.set_defaults(func=_cmd_inspect)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "command", None) is None:
        parser.print_help(sys.stderr)
        return EXIT_CONFIG
    try:
        return int(args.func(args))
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


def _cmd_inspect(args: argparse.Namespace) -> int:
    path = Path(args.trace)
    events = read_events(path)
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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
