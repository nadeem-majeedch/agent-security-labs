"""Tests for the acceptance-warning drift check's release-validation integration.

The check itself lives in ``scripts/check_warning_drift.py`` and is covered by
``tests/test_warning_drift.py``. This module pins the *integration*: the CI
``release-readiness`` job must run the drift check as a step that cannot be
silently ignored, and the integrated command must fail whenever the three
accepted-warning surfaces disagree.

The fixture builders are reused from ``tests/test_warning_drift.py`` (loaded as a
module, since ``tests`` is not a package) rather than duplicated. The
end-to-end cases run the real drift script as a subprocess against ``tmp_path``
fixtures whose ``scripts/release_check.py`` is a tiny JSON printer, so no test
runs the real (slow, gate-running) release check. The interpreter used is
``sys.executable`` — the one running the tests, never a global Python.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"
DRIFT_SCRIPT = ROOT / "scripts" / "check_warning_drift.py"
DRIFT_TESTS = ROOT / "tests" / "test_warning_drift.py"

RELEASE_JOB = "release-readiness"
DRIFT_COMMAND = "scripts/check_warning_drift.py"


def _load(path: Path, name: str):
    """Import a standalone module that is not part of an installed package."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


#: The drift-check script, and the fixture helpers from its own test module.
helpers = _load(DRIFT_TESTS, "test_warning_drift_helpers")
guard = helpers.guard

WORKFLOW = yaml.safe_load(CI.read_text(encoding="utf-8"))


def _jobs() -> dict:
    return WORKFLOW["jobs"]


def _run_commands(job: str) -> list[str]:
    return [step.get("run", "") for step in _jobs()[job]["steps"]]


def _drift_step() -> dict:
    for step in _jobs()[RELEASE_JOB]["steps"]:
        if DRIFT_COMMAND in step.get("run", ""):
            return step
    raise AssertionError("the release-readiness job does not run the drift check")


def _gate_step() -> dict:
    for step in _jobs()[RELEASE_JOB]["steps"]:
        if "scripts/release_check.py --json" in step.get("run", ""):
            return step
    raise AssertionError("the release-readiness job does not run the release gate")


def _run_drift(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(DRIFT_SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


# --------------------------------------------------------------------------
# The CI wiring: one added step in the existing release-readiness job.
# --------------------------------------------------------------------------


def test_ci_keeps_its_five_job_structure():
    assert set(_jobs()) == {
        "lint",
        "compatibility",
        "typecheck",
        "coverage",
        RELEASE_JOB,
    }, "the drift check must not introduce or remove a CI job"


def test_release_readiness_runs_the_drift_check():
    assert any(DRIFT_COMMAND in run for run in _run_commands(RELEASE_JOB))


def test_the_drift_check_runs_only_in_release_readiness():
    jobs_with_drift = [
        name
        for name, job in _jobs().items()
        if any(DRIFT_COMMAND in step.get("run", "") for step in job["steps"])
    ]
    assert jobs_with_drift == [RELEASE_JOB]


def test_release_readiness_still_runs_the_existing_gates():
    runs = " ".join(_run_commands(RELEASE_JOB))
    for expected in (
        "scripts/check_licensing.py",
        "scripts/check_version.py",
        "scripts/release_check.py --json",
    ):
        assert expected in runs, f"the release-readiness job must keep running {expected}"


def test_the_drift_step_cannot_be_silently_ignored():
    step = _drift_step()
    assert step.get("continue-on-error", False) is False, (
        "the drift step must fail the job on drift"
    )
    run = step["run"]
    for swallow in ("|| true", "|| echo", "set +e", "; true", "&& true"):
        assert swallow not in run, f"the drift step must not swallow failure via {swallow!r}"


def test_the_drift_step_runs_after_the_release_gate():
    runs = _run_commands(RELEASE_JOB)
    drift_index = next(i for i, run in enumerate(runs) if DRIFT_COMMAND in run)
    gate_index = next(
        i for i, run in enumerate(runs) if "scripts/release_check.py --json" in run
    )
    assert drift_index > gate_index, "the drift check should follow the release gate"


def test_the_release_gate_runs_exactly_once():
    commands = [
        step.get("run", "")
        for job in _jobs().values()
        for step in job["steps"]
    ]
    occurrences = sum(run.count("scripts/release_check.py") for run in commands)
    assert occurrences == 1, f"release_check.py should run once, found {occurrences}"


def test_the_drift_command_does_not_reinvoke_the_gate():
    run = _drift_step()["run"]
    assert "release_check" not in run, (
        "the drift command must consume the report, not run the gate again"
    )


def test_the_drift_step_consumes_the_generated_gate_report():
    gate_run = _gate_step()["run"]
    drift_run = _drift_step()["run"]
    assert ">" in gate_run and "release-report.json" in gate_run, (
        "the gate step must capture its JSON report"
    )
    assert "--gate-report" in drift_run and "release-report.json" in drift_run, (
        "the drift step must read the captured gate report"
    )
    assert "runner.temp" in gate_run and "runner.temp" in drift_run, (
        "the report must live outside the checkout, not become an artifact"
    )


def test_the_release_gate_step_does_not_hide_its_exit_status():
    step = _gate_step()
    assert step.get("continue-on-error", False) is False, (
        "a failing release gate must fail the job"
    )
    run = step["run"]
    assert "|" not in run, "a pipe could hide the gate's exit status"
    assert ">" in run, "redirection keeps the gate's own exit status"


# --------------------------------------------------------------------------
# The integrated command: current repository passes; every drift direction fails.
# --------------------------------------------------------------------------


def test_current_repository_surfaces_agree():
    policy = guard.load_policy(ROOT)
    documented = guard.load_documented(ROOT)
    assert policy.problem == "", policy.problem
    assert documented.problem == "", documented.problem
    assert policy.ids == frozenset({"W7", "W12"})
    assert documented.ids == policy.ids


def test_integrated_check_passes_for_agreeing_surfaces(tmp_path):
    helpers.make_tree(
        tmp_path, policy={"W7", "W12"}, documented={"W7", "W12"}, actual={"W7", "W12"}
    )
    result = _run_drift(tmp_path)
    assert result.returncode == 0, result.stdout
    assert "all three sets agree" in result.stdout


def test_integrated_check_consumes_a_gate_report(tmp_path):
    # No scripts/release_check.py: supplying --gate-report must not run the gate.
    helpers.write_policy(tmp_path, {"W7", "W12"})
    helpers.write_doc(tmp_path, "W7, W12")
    report = helpers.write_gate_report(tmp_path, {"W7", "W12"})
    result = subprocess.run(
        [
            sys.executable,
            str(DRIFT_SCRIPT),
            "--root",
            str(tmp_path),
            "--gate-report",
            str(report),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
    assert "all three sets agree" in result.stdout


@pytest.mark.parametrize(
    "policy, documented, actual",
    [
        # documentation disagrees with policy (and the gate).
        ({"W7", "W12"}, {"W7"}, {"W7", "W12"}),
        # the gate disagrees with policy: an accepted warning disappeared.
        ({"W7", "W12"}, {"W7", "W12"}, {"W7"}),
        # the gate emits an unexpected warning.
        ({"W7", "W12"}, {"W7", "W12"}, {"W7", "W12", "W14"}),
        # documentation is broader than policy.
        ({"W7"}, {"W7", "W12"}, {"W7"}),
    ],
)
def test_integrated_check_fails_on_drift(tmp_path, policy, documented, actual):
    helpers.make_tree(tmp_path, policy=policy, documented=documented, actual=actual)
    result = _run_drift(tmp_path)
    assert result.returncode == 1, result.stdout
    assert "DRIFT DETECTED" in result.stdout


def test_integrated_check_fails_on_a_malformed_documented_id(tmp_path):
    helpers.write_policy(tmp_path, {"W7"})
    helpers.write_doc(tmp_path, "W7, X9")
    helpers.write_release_stub(tmp_path, {"W7"})
    result = _run_drift(tmp_path)
    assert result.returncode == 1, result.stdout
    assert "malformed" in result.stdout


def test_integrated_check_fails_when_the_gate_output_is_unusable(tmp_path):
    helpers.write_policy(tmp_path, {"W7"})
    helpers.write_doc(tmp_path, "W7")
    script = tmp_path / "scripts" / "release_check.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("print('not json')\n", encoding="utf-8")
    result = _run_drift(tmp_path)
    assert result.returncode == 1, result.stdout
    assert "did not emit JSON" in result.stdout


def test_integrated_check_is_read_only(tmp_path):
    helpers.make_tree(
        tmp_path, policy={"W7", "W12"}, documented={"W7", "W12"}, actual={"W7", "W12"}
    )
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert _run_drift(tmp_path).returncode == 0
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert before == after, "the integrated drift check must not modify the tree"
