"""Tests for the release-manifest drift check in ``scripts/check_release_manifest.py``.

The checker compares ``labs/V0.1.0-RELEASE-MANIFEST.md`` with the actual release
state: the version, the release gate, the accepted-warning surfaces, the CI
workflow shape, the Git tag state and the protected invariants. These tests pin
each of those comparisons independently against crafted state, and exercise the
CLI against a small fixture repository whose ``release_check.py`` is stubbed, so
no test runs the real (slow, gate-running) release check.

The fixture builders are reused from ``tests/test_warning_drift.py`` where the
warning surfaces are written; the interpreter used is ``sys.executable``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_release_manifest.py"
DRIFT_TESTS = ROOT / "tests" / "test_warning_drift.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load(SCRIPT, "check_release_manifest")
_helpers = _load(DRIFT_TESTS, "test_warning_drift_helpers")

GATE_JSON = {
    "target_version": "0.1.0",
    "classification": "READY WITH WARNINGS",
    "blockers": [],
    "warnings": ["W12", "W7"],
    "gates": {
        "tests": "PASS",
        "labs": "PASS",
        "mkdocs": "PASS",
        "licensing": "PASS",
        "version": "PASS",
        "readme": "PASS",
        "self_containment": "WARN",
        "hygiene": "PASS",
        "git_state": "WARN",
    },
}

MANIFEST_TEXT = (
    "# v0.1.0 Release Manifest\n\n"
    "- **Version:** `0.1.0`\n"
    "- **Existing tag:** `v0.0.1`\n"
    "- **`v0.1.0` has not yet been created.**\n"
    "The accepted warning set is exactly `{W7, W12}`.\n"
    "`blockers`: `[]`\n"
    "`READY WITH WARNINGS`\n"
    "`W6`: CLOSED\n"
)

GOOD_WORKFLOW = (
    "name: CI\n\n"
    "jobs:\n"
    "  lint:\n"
    "    runs-on: ubuntu-latest\n"
    "  compatibility:\n"
    "    runs-on: ubuntu-latest\n"
    "  typecheck:\n"
    "    runs-on: ubuntu-latest\n"
    "  coverage:\n"
    "    runs-on: ubuntu-latest\n"
    "  release-readiness:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - name: Run every release gate once and report readiness\n"
    '        run: python scripts/release_check.py --json > "${{ runner.temp }}/r.json"\n'
    "      - name: Check the accepted-warning surfaces for drift\n"
    '        run: python scripts/check_warning_drift.py --gate-report "${{ runner.temp }}/r.json"\n'
)


def base_state(**overrides):
    state = {
        "manifest": MANIFEST_TEXT,
        "version": "0.1.0",
        "report": dict(GATE_JSON),
        "gate_problem": "",
        "policy_ids": frozenset({"W7", "W12"}),
        "documented_ids": frozenset({"W7", "W12"}),
        "actual_ids": frozenset({"W7", "W12"}),
        "drift_problems": (),
        "workflow": GOOD_WORKFLOW,
        "tags": ("v0.0.1",),
        "tracked": (".freebuff/project-id",),
        "docs_workflow_present": True,
        "schema_copies_equal": True,
        "release_script_clean": True,
        "ruff_ok": True,
        "mypy_ok": True,
    }
    state.update(overrides)
    return guard.ReleaseState(**state)


def named(report, name):
    matches = [check for check in report.checks if check.name == name]
    assert matches, f"no check named {name!r} in {[c.name for c in report.checks]}"
    return matches[0]


# --------------------------------------------------------------------------
# Basic agreement.
# --------------------------------------------------------------------------


def test_all_checks_pass_for_a_consistent_state():
    report = guard.evaluate(base_state())
    assert report.ok, [c.name for c in report.checks if not c.ok]


def test_version_passes_for_the_matching_manifest():
    assert named(guard.evaluate(base_state()), "release version").ok


def test_warning_state_passes_for_the_expected_set():
    assert named(guard.evaluate(base_state()), "warning set").ok


def test_w6_closed_passes_when_absent_from_the_gate_and_documented():
    assert named(guard.evaluate(base_state()), "W6 closed").ok


def test_blockers_pass_when_empty():
    assert named(guard.evaluate(base_state()), "blockers").ok


def test_classification_passes_for_ready_with_warnings():
    assert named(guard.evaluate(base_state()), "classification").ok


# --------------------------------------------------------------------------
# Drift detection.
# --------------------------------------------------------------------------


def test_manifest_version_drift_is_detected():
    report = guard.evaluate(base_state(manifest=MANIFEST_TEXT.replace("0.1.0", "0.9.9")))
    assert not named(report, "release version").ok


def test_actual_version_drift_is_detected():
    report = guard.evaluate(base_state(version="0.2.0"))
    assert not named(report, "release version").ok


def test_a_new_warning_is_detected():
    report = guard.evaluate(base_state(actual_ids=frozenset({"W7", "W12", "W13"})))
    assert not named(report, "warning set").ok


def test_a_disappeared_warning_is_detected():
    report = guard.evaluate(base_state(actual_ids=frozenset({"W7"})))
    assert not named(report, "warning set").ok


def test_non_empty_blockers_are_detected():
    report = guard.evaluate(
        base_state(report={**GATE_JSON, "blockers": ["tests"]})
    )
    assert not named(report, "blockers").ok


def test_a_changed_classification_is_detected():
    report = guard.evaluate(base_state(report={**GATE_JSON, "classification": "READY"}))
    assert not named(report, "classification").ok


def test_a_malformed_manifest_warning_id_is_detected():
    report = guard.evaluate(base_state(manifest=MANIFEST_TEXT.replace("W7, W12", "W7, X9")))
    assert not named(report, "warning set").ok


def test_a_missing_manifest_is_detected():
    report = guard.evaluate(base_state(manifest=""))
    assert not named(report, "release version").ok


def test_a_malformed_manifest_is_detected():
    report = guard.evaluate(base_state(manifest="this is not the release manifest"))
    assert not named(report, "release version").ok


def test_a_missing_manifest_section_is_detected():
    report = guard.evaluate(base_state(manifest=MANIFEST_TEXT.replace("CLOSED", "closed")))
    assert not named(report, "W6 closed").ok


def test_a_wrong_ci_job_count_is_detected():
    workflow = GOOD_WORKFLOW.replace("  coverage:\n    runs-on: ubuntu-latest\n", "")
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_a_missing_release_job_is_detected():
    workflow = GOOD_WORKFLOW.replace("release-readiness", "release-readiness-renamed")
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_a_missing_drift_step_is_detected():
    workflow = "\n".join(
        line for line in GOOD_WORKFLOW.splitlines() if "check_warning_drift.py" not in line
    )
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_a_drift_step_without_gate_report_is_detected():
    workflow = GOOD_WORKFLOW.replace(
        'python scripts/check_warning_drift.py --gate-report "${{ runner.temp }}/r.json"',
        "python scripts/check_warning_drift.py",
    )
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_a_duplicate_release_gate_invocation_is_detected():
    workflow = GOOD_WORKFLOW + "        run: python scripts/release_check.py --json\n"
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_continue_on_error_is_detected():
    workflow = GOOD_WORKFLOW + "        continue-on-error: true\n"
    report = guard.evaluate(base_state(workflow=workflow))
    assert not named(report, "CI structure").ok


def test_an_unexpected_v0_1_0_tag_is_detected():
    report = guard.evaluate(base_state(tags=("v0.0.1", "v0.1.0")))
    assert not named(report, "tag state").ok


def test_a_protected_invariant_drift_is_detected():
    report = guard.evaluate(base_state(release_script_clean=False))
    assert not named(report, "protected invariants").ok


def test_every_discrepancy_is_reported(tmp_path, capsys):
    state = base_state(
        version="0.2.0",
        actual_ids=frozenset({"W7"}),
        tags=("v0.0.1", "v0.1.0"),
    )
    text = guard.format_report(guard.evaluate(state))
    assert "FAIL  release version" in text
    assert "FAIL  warning set" in text
    assert "FAIL  tag state" in text
    assert "Result: FAIL" in text


# --------------------------------------------------------------------------
# The CI workflow scanner.
# --------------------------------------------------------------------------


def test_scan_workflow_summarizes_the_good_workflow():
    scan = guard.scan_workflow(GOOD_WORKFLOW)
    assert scan["job_count"] == 5
    assert guard.RELEASE_JOB in scan["jobs"]
    assert scan["release_calls"] == 1
    assert scan["drift_present"] and scan["drift_uses_report"]
    assert scan["continue_on_error"] is False


def test_scan_workflow_reads_the_real_ci_file():
    scan = guard.scan_workflow((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    assert scan["job_count"] == 5
    assert scan["release_calls"] == 1
    assert scan["drift_uses_report"] is True


# --------------------------------------------------------------------------
# The CLI against a fixture repository with a stubbed release check.
# --------------------------------------------------------------------------


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(root: Path, *, manifest: str | None = None) -> Path:
    (root / "pyproject.toml").parent.mkdir(parents=True, exist_ok=True)
    _write(root / "pyproject.toml", '[project]\nname = "agentsec"\nversion = "0.1.0"\n')
    _write(root / "labs" / "V0.1.0-RELEASE-MANIFEST.md", manifest or MANIFEST_TEXT)
    _write(
        root / "tests" / "test_release_check.py",
        'ACCEPTED_RELEASE_WARNINGS = frozenset({"W7", "W12"})\n',
    )
    _write(
        root / "labs" / "ACCEPTED-RELEASE-WARNINGS.md",
        "## The accepted set is exactly `{W7, W12}`\n",
    )
    _write(root / ".github" / "workflows" / "ci.yml", GOOD_WORKFLOW)
    _write(root / ".github" / "workflows" / "docs.yml", "name: Docs\n")
    _write(root / "scripts" / "release_check.py", "# stub; the fake runner answers --json\n")
    schema = b'{"oneOf": []}\n'
    _write(root / "schemas" / "trace" / "trace_event.v1.schema.json", schema.decode())
    _write(root / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json", schema.decode())
    return root


class FakeRunner:
    """A recording stand-in for ``run_command`` returning canned read-only output."""

    def __init__(self, *, tags="v0.0.1\n"):
        self.calls: list[tuple[str, ...]] = []
        self.tags = tags

    def __call__(self, argv, *, cwd):
        argv = tuple(str(item) for item in argv)
        self.calls.append(argv)
        if argv and argv[0] == "git":
            rest = argv[argv.index("-C") + 2 :] if "-C" in argv else argv[1:]
            sub = rest[0] if rest else ""
            if sub == "tag":
                return guard.CommandResult(argv, 0, self.tags, "")
            if sub == "ls-files":
                return guard.CommandResult(argv, 0, ".freebuff/project-id\n", "")
            if sub == "status":
                return guard.CommandResult(argv, 0, "", "")
            return guard.CommandResult(argv, 0, "", "")
        joined = " ".join(argv)
        if "release_check.py" in joined:
            return guard.CommandResult(argv, 0, json.dumps(GATE_JSON), "")
        return guard.CommandResult(argv, 0, "", "")


def test_run_checks_passes_for_a_consistent_fixture(tmp_path):
    make_repo(tmp_path)
    report = guard.run_checks(tmp_path, run=FakeRunner())
    assert report.ok, [c.name for c in report.checks if not c.ok]


def test_run_checks_fails_for_a_drifted_fixture(tmp_path):
    make_repo(tmp_path, manifest=MANIFEST_TEXT.replace("0.1.0", "0.9.9"))
    report = guard.run_checks(tmp_path, run=FakeRunner())
    assert not report.ok
    assert not named(report, "release version").ok


def test_run_checks_uses_a_gate_report_without_running_the_gate(tmp_path):
    make_repo(tmp_path)
    report_path = tmp_path / "gate-report.json"
    report_path.write_text(json.dumps(GATE_JSON), encoding="utf-8")
    runner = FakeRunner()
    report = guard.run_checks(tmp_path, gate_report=report_path, run=runner)
    assert report.ok, [c.name for c in report.checks if not c.ok]
    # Only the release-gate invocation passes --json; --gate-report must skip it.
    assert not any("--json" in call for call in runner.calls), (
        "--gate-report must not run release_check.py again"
    )


def test_run_checks_fails_cleanly_for_a_malformed_gate_report(tmp_path):
    make_repo(tmp_path)
    report_path = tmp_path / "gate-report.json"
    report_path.write_text("{not json", encoding="utf-8")
    report = guard.run_checks(tmp_path, gate_report=report_path, run=FakeRunner())
    assert not report.ok
    assert not named(report, "release validation").ok


def test_main_returns_zero_for_a_consistent_repository(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner()) == 0
    assert "Result: PASS" in capsys.readouterr().out


def test_main_returns_nonzero_for_drift(tmp_path, capsys):
    make_repo(tmp_path, manifest=MANIFEST_TEXT.replace("0.1.0", "0.9.9"))
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner()) == 1
    assert "Result: FAIL" in capsys.readouterr().out
