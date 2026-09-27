"""LAB-00 - setup & environment verification tests.

These prove the setup lab's files exist, that its configuration loads and runs
offline, that the run produces a valid trace, and that the trace evaluates and
replays byte-identically under a fixed clock. Nothing here touches the network,
API keys, a real database, Docker or a GPU.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from agentsec import __version__
from agentsec.cli import EXIT_CONFIG, build_parser, main
from agentsec.eval import EvaluationInput, RunOutcome, TraceEvaluator
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "labs" / "LAB-00-setup"
CONFIG = LAB / "config.yaml"

#: Fixed clock so a replayed run is byte-identical.
TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def run_lab00(tmp_path: Path):
    """Run the LAB-00 experiment into ``tmp_path`` with a fixed clock."""
    config = load_experiment_config(CONFIG)
    config = config.model_copy(update={"trace_path": tmp_path / "trace.jsonl"})
    runner = build_mvp_runner(config, clock=lambda: TS)
    return runner.run(config), config


def test_lab00_files_exist():
    assert (LAB / "README.md").is_file()
    assert CONFIG.is_file()


def test_lab00_readme_is_student_facing():
    text = (LAB / "README.md").read_text(encoding="utf-8")
    for heading in (
        "Learning objectives",
        "Prerequisites",
        "Procedure",
        "Troubleshooting",
        "Completion checklist",
    ):
        assert heading in text
    # student material carries an explicit no-claims disclaimer
    assert "no research claim" in " ".join(text.lower().split())


def test_lab00_config_loads():
    config = load_experiment_config(CONFIG)
    assert config.experiment_id == "lab00_setup"
    assert config.mock_script == "benign"
    assert config.policy_path is not None


def test_lab00_cli_is_available():
    parser = build_parser()
    subparsers = next(
        action for action in parser._actions if action.dest == "command"
    )
    available = set(subparsers.choices)
    assert {"run", "evaluate", "inspect"} <= available
    # no command -> usage error, not a crash
    assert main([]) == EXIT_CONFIG


def test_lab00_package_imports():
    assert isinstance(__version__, str) and __version__


def test_lab00_run_produces_valid_trace(tmp_path):
    result, _ = run_lab00(tmp_path)
    trace = tmp_path / "trace.jsonl"
    assert trace.is_file()
    assert result.error is None
    assert result.evaluation is not None

    report = validate_jsonl(trace)
    assert report.issues == [], report.issues
    assert report.total >= 8


def test_lab00_trace_has_expected_lifecycle(tmp_path):
    run_lab00(tmp_path)
    events = read_events(tmp_path / "trace.jsonl")
    types = [event["event_type"] for event in events]
    assert types[0] == "run_started"
    assert types[-1] == "run_completed"
    for expected in ("agent_input", "model_request", "model_response", "agent_output"):
        assert expected in types


def test_lab00_trace_evaluates(tmp_path):
    run_lab00(tmp_path)
    events = read_events(tmp_path / "trace.jsonl")
    evaluation = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    assert evaluation.status is RunOutcome.COMPLETED
    assert evaluation.tool_results.get("ok") == 1


def test_lab00_replay_is_byte_identical(tmp_path):
    run_lab00(tmp_path)
    first = (tmp_path / "trace.jsonl").read_bytes()
    run_lab00(tmp_path)
    second = (tmp_path / "trace.jsonl").read_bytes()
    assert first == second
