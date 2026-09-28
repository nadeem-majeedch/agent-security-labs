"""Tests for the offline lab self-check (``agentsec labs check``).

These exercise the real application path: lab discovery, running each canonical
lab through the deterministic MVP stack, interpreting the result against the
lab's existing declared expectations, and the CLI command's exit codes. The
self-check is a reproducibility/teaching check - it is not a benchmark and
computes no score. Everything here is offline.
"""

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

import agentsec.selfcheck as selfcheck_module
from agentsec.agent import RunStatus
from agentsec.cli import EXIT_CONFIG, EXIT_OK, main
from agentsec.experiment import ExperimentConfig, ExperimentResult
from agentsec.mvp import build_mvp_runner
from agentsec.scenarios import ScenarioStatus
from agentsec.selfcheck import (
    SMOKE_EXPECTATIONS,
    check_labs,
    discover_labs,
    expected_observation,
)

REPO = Path(__file__).resolve().parents[2]
LABS = REPO / "labs"
TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

EXPECTED_LAB_IDS = [f"LAB-0{n}" for n in range(8)]


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    """Run one lab config with the deterministic stack and a fixed clock."""
    runner = build_mvp_runner(config, clock=lambda: TS)
    return runner.run(config)


def _tree(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if "__pycache__" not in path.parts
    }


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def _make_labs_dir(tmp_path: Path, *lab_names: str) -> Path:
    """Copy canonical labs into a throwaway labs directory."""
    root = tmp_path / "labs"
    root.mkdir()
    for name in lab_names:
        source = LABS / name
        dest = root / name
        dest.mkdir()
        (dest / "config.yaml").write_bytes((source / "config.yaml").read_bytes())
        scenario = source / "scenario.yaml"
        if scenario.is_file():
            (dest / "scenario.yaml").write_bytes(scenario.read_bytes())
    return root


# -- discovery -----------------------------------------------------------------
def test_discover_labs_finds_lab_00_through_lab_07():
    specs = discover_labs(LABS)
    assert [spec.lab_id for spec in specs] == EXPECTED_LAB_IDS


def test_discovery_order_is_deterministic_and_sorted():
    first = discover_labs(LABS)
    second = discover_labs(LABS)
    assert first == second
    ids = [spec.lab_id for spec in first]
    assert ids == sorted(ids)


def test_every_discovered_lab_has_a_config_file():
    for spec in discover_labs(LABS):
        assert spec.config_path.is_file()
        assert spec.directory.is_dir()


def test_no_lab_08_exists_or_is_discovered():
    assert not any(path.name.startswith("LAB-08") for path in LABS.iterdir())
    assert "LAB-08" not in {spec.lab_id for spec in discover_labs(LABS)}


def test_labs_without_a_scenario_use_smoke_expectations():
    by_id = {spec.lab_id: spec for spec in discover_labs(LABS)}
    assert by_id["LAB-00"].has_scenario is False
    assert expected_observation(by_id["LAB-00"]) == SMOKE_EXPECTATIONS
    assert expected_observation(by_id["LAB-00"]).agent_status is RunStatus.COMPLETED
    # Every other lab declares its own expectations in scenario.yaml.
    for lab_id in EXPECTED_LAB_IDS[1:]:
        assert by_id[lab_id].has_scenario is True


# -- happy path ----------------------------------------------------------------
def test_self_check_passes_for_every_lab(tmp_path):
    report = check_labs(LABS, tmp_path / "out", run_experiment=run_experiment)
    assert report.total == 8
    assert report.ok, [(r.lab_id, r.detail) for r in report.failed]
    assert all(result.status is ScenarioStatus.PASSED for result in report.results)


def test_self_check_writes_no_traces_into_the_repository_runs_dir(tmp_path):
    before = _tree(REPO / "runs")
    check_labs(LABS, tmp_path / "out", run_experiment=run_experiment)
    after = _tree(REPO / "runs")
    assert before == after


def test_self_check_does_not_modify_the_lab_definitions(tmp_path):
    before = _snapshot(LABS)
    check_labs(LABS, tmp_path / "out", run_experiment=run_experiment)
    after = _snapshot(LABS)
    assert before == after


# -- failure path --------------------------------------------------------------
def test_altered_expectation_produces_a_failure(tmp_path):
    labs = _make_labs_dir(tmp_path, "LAB-01-benign-agent")
    scenario_path = labs / "LAB-01-benign-agent" / "scenario.yaml"
    document = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    document["expected"]["tool_requests"] = 99
    scenario_path.write_text(yaml.safe_dump(document), encoding="utf-8")

    report = check_labs(labs, tmp_path / "out", run_experiment=run_experiment)

    assert report.total == 1
    assert not report.ok
    failed = report.failed[0]
    assert failed.lab_id == "LAB-01"
    assert failed.status is ScenarioStatus.FAILED
    assert "tool_requests" in failed.detail


def test_a_missing_expectation_field_still_matches(tmp_path):
    """Removing one expectation must not fail the lab (others still hold)."""
    labs = _make_labs_dir(tmp_path, "LAB-01-benign-agent")
    scenario_path = labs / "LAB-01-benign-agent" / "scenario.yaml"
    document = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    document["expected"].pop("output_contains", None)
    scenario_path.write_text(yaml.safe_dump(document), encoding="utf-8")

    report = check_labs(labs, tmp_path / "out", run_experiment=run_experiment)
    assert report.ok


# -- CLI -----------------------------------------------------------------------
def test_cli_labs_check_returns_zero(capsys):
    code = main(["labs", "check", "--labs-dir", str(LABS)])
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "8/8 labs passed" in out
    assert out.count("PASS") == 8


def test_cli_labs_check_json(capsys):
    code = main(["labs", "check", "--labs-dir", str(LABS), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == EXIT_OK
    assert payload["ok"] is True
    assert payload["total"] == 8
    assert payload["passed"] == 8
    assert [lab["lab"] for lab in payload["labs"]] == EXPECTED_LAB_IDS


def test_cli_labs_check_returns_non_zero_on_failure(tmp_path, capsys):
    labs = _make_labs_dir(tmp_path, "LAB-01-benign-agent")
    scenario_path = labs / "LAB-01-benign-agent" / "scenario.yaml"
    document = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    document["expected"]["tool_requests"] = 99
    scenario_path.write_text(yaml.safe_dump(document), encoding="utf-8")

    code = main(["labs", "check", "--labs-dir", str(labs)])
    out = capsys.readouterr().out
    assert code != EXIT_OK
    assert "FAIL" in out
    assert "0/1 labs passed" in out
    assert "tool_requests" in out


def test_cli_labs_check_missing_dir_is_a_config_error(tmp_path, capsys):
    code = main(["labs", "check", "--labs-dir", str(tmp_path / "nope")])
    assert code == EXIT_CONFIG
    assert "error" in capsys.readouterr().err.lower()


def test_cli_labs_without_subcommand_is_a_usage_error(capsys):
    assert main(["labs"]) == EXIT_CONFIG
    assert "usage" in capsys.readouterr().err.lower()


def test_cli_help_still_lists_the_existing_commands(capsys):
    code = main([])
    err = capsys.readouterr().err
    assert code == EXIT_CONFIG
    for command in ("run", "evaluate", "inspect", "labs"):
        assert command in err


# -- offline / no external requirements ---------------------------------------
def test_selfcheck_module_imports_only_stdlib_and_local_code():
    path = Path(selfcheck_module.__file__)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    top_level: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top_level.add(node.module.split(".")[0])
    permitted = {"__future__", "re", "dataclasses", "pathlib", "typing"}
    assert top_level <= permitted, top_level - permitted
