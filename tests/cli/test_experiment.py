"""Tests for the `agentsec experiment` CLI integration (Phase 11E).

The command is thin wiring over the Phase 11D runner: it loads and validates the
specification, hands the real execution function to the runner, and renders the
result. These tests exercise the CLI in-process (``main``) for exit codes,
deterministic output and JSON round-tripping, and monkeypatch the runner for the
non-``changes_observed`` states so the CLI semantics are tested independently of
outcomes that would otherwise need bespoke traces.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentsec.cli import build_parser, main
from agentsec.experiment_lab import ExperimentResult, ExperimentStatus

REPO = Path(__file__).resolve().parents[2]
SPEC = "configs/experiments/lab04-policy-intervention.yaml"


def _result(status: ExperimentStatus) -> ExperimentResult:
    return ExperimentResult(
        schema_version="1",
        experiment_id="lab04-policy-intervention",
        title="Controlled policy intervention (LAB-04)",
        hypothesis="changing only the policy changes the observed execution",
        status=status,
    )


# -- wiring --------------------------------------------------------------------
def test_the_experiment_command_exists():
    args = build_parser().parse_args(["experiment", SPEC])
    assert args.func is not None
    assert args.func.__name__ == "_cmd_experiment"
    assert args.json is False


def test_existing_commands_still_parse():
    parser = build_parser()
    for argv in (
        ["run", "c"],
        ["evaluate", "t"],
        ["inspect", "t"],
        ["compare", "a", "b"],
        ["predict", "t", "p"],
        ["demo", "lab04-two-policies"],
        ["labs", "check"],
    ):
        assert parser.parse_args(argv).func is not None


# -- real integration ----------------------------------------------------------
def test_valid_experiment_exits_zero(monkeypatch):
    monkeypatch.chdir(REPO)
    assert main(["experiment", SPEC]) == 0


def test_human_output_contains_the_result_sections(monkeypatch, capsys):
    monkeypatch.chdir(REPO)
    assert main(["experiment", SPEC]) == 0
    out = capsys.readouterr().out
    for fragment in (
        "experiment: lab04-policy-intervention",
        "control",
        "treatment",
        "expected changes",
        "expected invariants",
        "observed difference",
        "state: changes_observed",
        "claim:",
        "boundary:",
    ):
        assert fragment in out


def test_json_output_is_valid_and_round_trips(monkeypatch, capsys):
    monkeypatch.chdir(REPO)
    assert main(["experiment", SPEC, "--json"]) == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["experiment_id"] == "lab04-policy-intervention"
    # The JSON is the ExperimentResult schema authority: it re-validates.
    result = ExperimentResult.model_validate_json(out)
    assert result.status is ExperimentStatus.CHANGES_OBSERVED


def test_json_output_is_deterministic(monkeypatch, capsys):
    monkeypatch.chdir(REPO)
    main(["experiment", SPEC, "--json"])
    first = capsys.readouterr().out
    main(["experiment", SPEC, "--json"])
    second = capsys.readouterr().out
    assert first == second


def test_json_contains_no_absolute_or_temp_paths(monkeypatch, capsys):
    monkeypatch.chdir(REPO)
    main(["experiment", SPEC, "--json"])
    out = capsys.readouterr().out
    assert "agentsec-experiment-" not in out
    assert str(REPO) not in out


# -- exit codes for every state ------------------------------------------------
@pytest.mark.parametrize("status", list(ExperimentStatus))
def test_every_experiment_state_exits_zero(monkeypatch, capsys, status):
    monkeypatch.setattr(
        "agentsec.cli.run_controlled_experiment",
        lambda spec, execute, **kw: _result(status),
    )
    assert main(["experiment", SPEC]) == 0
    assert f"state: {status.value}" in capsys.readouterr().out


def test_invalid_spec_exits_one(capsys):
    assert main(["experiment", "does-not-exist.yaml"]) == 1
    assert "error" in capsys.readouterr().err.lower()


def test_malformed_spec_exits_one(tmp_path, capsys):
    bad = tmp_path / "bad.yaml"
    bad.write_text("experiment_id: x\n", encoding="utf-8")
    assert main(["experiment", str(bad)]) == 1
    assert "error" in capsys.readouterr().err.lower()


def test_unexpected_orchestration_failure_exits_two(monkeypatch, capsys):
    def boom(spec, execute, **kw):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("agentsec.cli.run_controlled_experiment", boom)
    assert main(["experiment", SPEC]) == 2
    assert "RuntimeError" in capsys.readouterr().err
