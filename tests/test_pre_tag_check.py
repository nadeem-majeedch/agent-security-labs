"""Tests for the owner pre-tag validation in ``scripts/pre_tag_check.py``.

The orchestrator runs the established release checks in one deterministic pass,
captures the release gate once, reuses its JSON report in the two drift checks,
and verifies the read-only Git/tag invariant. These tests stub every subprocess
command with a recording runner, so no test runs the real (slow) suite or the
real release gate, and they pin:

* successful orchestration (exit ``0``, dirty tree accepted, tag state);
* independent failure propagation for every step;
* gate reuse (one gate run, a report outside the repository, ``--gate-report``
  for both drift checks, the report removed afterwards);
* read-only behaviour (no commit/push/tag creation, no source edits, no
  artefacts);
* the sectioned output and the unambiguous final status.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pre_tag_check.py"


def _load():
    """Import ``scripts/pre_tag_check.py``, which is not a package module."""
    spec = importlib.util.spec_from_file_location("pre_tag_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load()

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

#: Canned stdout per step key, so summaries are parsed the way the real
#: commands print them.
_OUTPUT = {
    "version": "Result: 3/3 checks passed\n",
    "licensing": (
        "Result: 9/9 checks passed\n"
        "214 file(s) accounted for (mit 138, cc-by 74, excluded 2, unlicensed 0)\n"
    ),
    "tests": "991 passed in 12.34s\n",
    "labs": "8/8 labs passed\n",
}


def _step_key(argv, joined: str) -> str:
    """Classify a command by the step it belongs to."""
    if "check_version.py" in joined:
        return "version"
    if "check_licensing.py" in joined:
        return "licensing"
    if "check_warning_drift.py" in joined:
        return "drift"
    if "check_release_manifest.py" in joined:
        return "manifest"
    if "release_check.py" in joined:
        return "gate"
    if "pytest" in argv:
        return "tests"
    if "mkdocs" in argv:
        return "mkdocs"
    if "labs" in argv:
        return "labs"
    if "mypy" in argv:
        return "mypy"
    if "ruff" in argv:
        return "ruff"
    return "other"


class FakeRunner:
    """A recording stand-in for ``run_command`` returning canned output."""

    def __init__(self, *, tags: str = "v0.0.1\n", failures=()):
        self.calls: list[tuple[str, ...]] = []
        self.tags = tags
        self.failures = set(failures)

    def __call__(self, argv, *, cwd, env=None):
        argv = tuple(str(item) for item in argv)
        self.calls.append(argv)
        joined = " ".join(argv)
        if argv and argv[0] == "git":
            if "ls-files" in argv:
                return guard.CommandResult(argv, 0, self._ls_files(cwd), "")
            return guard.CommandResult(argv, 0, self.tags, "")
        key = _step_key(argv, joined)
        rc = 1 if key in self.failures else 0
        if key == "gate":
            report = dict(GATE_JSON)
            if "gate" in self.failures:
                report = {
                    **GATE_JSON,
                    "classification": "NOT READY",
                    "blockers": ["tests"],
                }
            return guard.CommandResult(argv, rc, json.dumps(report), "")
        return guard.CommandResult(argv, rc, _OUTPUT.get(key, ""), "")

    @staticmethod
    def _ls_files(cwd) -> str:
        """Emulate ``git ls-files -co --exclude-standard -z`` for the fixture.

        Lists the fixture repository's files from the working tree (excluding
        ``.git``), NUL-separated, so repository-state hashing sees real content
        and responds to added, changed and deleted files.
        """
        base = Path(cwd)
        names = []
        for entry in sorted(base.rglob("*")):
            if not entry.is_file():
                continue
            relative = entry.relative_to(base)
            if ".git" in relative.parts:
                continue
            names.append(relative.as_posix())
        return "\0".join(names) + ("\0" if names else "")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(root: Path) -> Path:
    """A minimal fixture repository root for the orchestrator."""
    _write(root / "pyproject.toml", '[project]\nname = "agentsec"\nversion = "0.1.0"\n')
    for name in (
        "check_version.py",
        "check_licensing.py",
        "check_warning_drift.py",
        "check_release_manifest.py",
        "release_check.py",
    ):
        _write(root / "scripts" / name, "# stub; the fake runner answers\n")
    return root


def _gate_report_paths(runner: FakeRunner) -> list[str]:
    paths = []
    for call in runner.calls:
        if "--gate-report" in call:
            paths.append(call[call.index("--gate-report") + 1])
    return paths


def _gate_invocations(runner: FakeRunner) -> int:
    return sum(1 for call in runner.calls if "release_check.py" in " ".join(call))


# --------------------------------------------------------------------------
# Successful orchestration.
# --------------------------------------------------------------------------


def test_main_returns_zero_for_the_expected_state(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner()) == 0
    out = capsys.readouterr().out
    assert "RESULT: READY FOR OWNER REVIEW" in out
    assert "No commit, push, tag, or publication was performed." in out


def test_success_accepts_the_expected_warning_state(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner()) == 0
    out = capsys.readouterr().out
    assert "READY WITH WARNINGS" in out
    assert "{W7, W12}" in out
    assert "blockers: []" in out


def test_success_reports_the_git_tag_state(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner()) == 0
    out = capsys.readouterr().out
    assert "PASS  v0.0.1 exists" in out
    assert "PASS  v0.1.0 absent" in out


def test_a_dirty_working_tree_is_not_a_failure(tmp_path, capsys):
    make_repo(tmp_path)
    runner = FakeRunner()
    # A dirty tree would make `git status` noisy; the orchestrator must not gate
    # on it, so it must not run `git status` at all.
    assert guard.main(["--root", str(tmp_path)], run=runner) == 0
    assert not any("status" in call for call in runner.calls)
    assert "RESULT: READY FOR OWNER REVIEW" in capsys.readouterr().out


def test_run_checks_returns_every_step(tmp_path):
    make_repo(tmp_path)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    ctx = guard.Context(
        root=tmp_path,
        python=sys.executable,
        env={},
        scratch=scratch,
        run=FakeRunner(),
    )
    results = guard.run_checks(ctx)
    assert [result.name for result in results] == [
        "Version",
        "Licensing",
        "Tests",
        "Labs",
        "Ruff",
        "Mypy",
        "MkDocs",
        "Release gate",
        "Warning drift",
        "Release manifest",
        "Git/tag state",
    ]
    assert all(result.ok for result in results)


# --------------------------------------------------------------------------
# Failure propagation: each step fails independently.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("failure", "index", "section"),
    [
        ("version", 1, "Version"),
        ("licensing", 2, "Licensing"),
        ("tests", 3, "Tests"),
        ("labs", 4, "Labs"),
        ("ruff", 5, "Ruff"),
        ("mypy", 6, "Mypy"),
        ("mkdocs", 7, "MkDocs"),
        ("gate", 8, "Release gate"),
        ("drift", 9, "Warning drift"),
        ("manifest", 10, "Release manifest"),
    ],
)
def test_each_step_failure_is_reported(tmp_path, capsys, failure, index, section):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner(failures={failure})) == 1
    out = capsys.readouterr().out
    assert "RESULT: NOT READY" in out
    assert f"[{index}/12] {section}\nFAIL" in out


def test_a_missing_v0_0_1_tag_fails(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner(tags="\n")) == 1
    out = capsys.readouterr().out
    assert "FAIL  v0.0.1 is missing" in out
    assert "RESULT: NOT READY" in out


def test_an_unexpected_v0_1_0_tag_fails(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner(tags="v0.0.1\nv0.1.0\n")) == 1
    out = capsys.readouterr().out
    assert "FAIL  v0.1.0 already exists" in out
    assert "RESULT: NOT READY" in out


def test_a_gate_blocker_fails(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=FakeRunner(failures={"gate"})) == 1
    out = capsys.readouterr().out
    assert "FAIL  NOT READY" in out
    assert "blockers: ['tests']" in out


def test_all_failures_are_listed_together(tmp_path, capsys):
    make_repo(tmp_path)
    runner = FakeRunner(failures={"tests", "ruff"})
    assert guard.main(["--root", str(tmp_path)], run=runner) == 1
    out = capsys.readouterr().out
    assert "FAILURES" in out
    assert "- Tests" in out
    assert "- Ruff" in out
    # An independent, passing step is still reported as PASS.
    assert "PASS  v0.0.1 exists" in out


# --------------------------------------------------------------------------
# Gate reuse: one capture, two consumers.
# --------------------------------------------------------------------------


def test_release_gate_runs_exactly_once(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    assert _gate_invocations(runner) == 1


def test_both_drift_checks_receive_the_same_captured_report(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    paths = _gate_report_paths(runner)
    assert len(paths) == 2
    assert paths[0] == paths[1]


def test_the_captured_report_lives_outside_the_repository(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    for path in _gate_report_paths(runner):
        assert not Path(path).is_relative_to(tmp_path.resolve())


def test_the_captured_report_is_removed_afterwards(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    for path in _gate_report_paths(runner):
        assert not Path(path).exists()


def test_no_second_gate_run_when_the_report_is_reused(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    # Exactly one --json gate invocation and no bare second call.
    json_calls = [call for call in runner.calls if call and "--json" in call]
    assert len(json_calls) == 1


# --------------------------------------------------------------------------
# Read-only behaviour.
# --------------------------------------------------------------------------


def test_the_orchestrator_never_commits_pushes_or_tags(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path)], run=runner)
    for call in runner.calls:
        assert "commit" not in call
        assert "push" not in call
        # The only tag access is the read-only listing: `git ... tag` with no
        # extra argument.
        if "tag" in call:
            index = call.index("tag")
            assert index == len(call) - 1, f"tag creation attempted: {call}"


def test_the_orchestrator_leaves_the_repository_unmodified(tmp_path):
    make_repo(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    guard.main(["--root", str(tmp_path)], run=FakeRunner())
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


def test_the_orchestrator_leaves_no_build_artifacts(tmp_path):
    make_repo(tmp_path)
    guard.main(["--root", str(tmp_path)], run=FakeRunner())
    for name in ("build", "dist", "site", ".coverage", ".mypy_cache"):
        assert not (tmp_path / name).exists(), f"unexpected artifact {name}"


# --------------------------------------------------------------------------
# Output contract.
# --------------------------------------------------------------------------


def test_every_section_is_represented(tmp_path, capsys):
    make_repo(tmp_path)
    guard.main(["--root", str(tmp_path)], run=FakeRunner())
    out = capsys.readouterr().out
    for index, name in enumerate(
        [
            "Version",
            "Licensing",
            "Tests",
            "Labs",
            "Ruff",
            "Mypy",
            "MkDocs",
            "Release gate",
            "Warning drift",
            "Release manifest",
            "Git/tag state",
        ],
        1,
    ):
        assert f"[{index}/12] {name}" in out


def test_summary_mode_hides_passing_steps(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--summary"], run=FakeRunner()) == 0
    out = capsys.readouterr().out
    assert "RESULT: READY FOR OWNER REVIEW" in out
    assert "[1/12] Version" not in out


def test_summary_mode_still_reports_failures(tmp_path, capsys):
    make_repo(tmp_path)
    assert (
        guard.main(
            ["--root", str(tmp_path), "--summary"], run=FakeRunner(failures={"ruff"})
        )
        == 1
    )
    out = capsys.readouterr().out
    assert "RESULT: NOT READY" in out
    assert "[5/12] Ruff" in out


# --------------------------------------------------------------------------
# The script's own stderr/stdout and exit statuses are preserved.
# --------------------------------------------------------------------------


def test_captured_output_is_quoted_on_failure(tmp_path, capsys):
    make_repo(tmp_path)

    class FailingRunner(FakeRunner):
        def __call__(self, argv, *, cwd, env=None):
            argv = tuple(str(item) for item in argv)
            self.calls.append(argv)
            if argv and argv[0] == "git":
                return guard.CommandResult(argv, 0, self.tags, "")
            key = _step_key(argv, " ".join(argv))
            if key == "gate":
                return guard.CommandResult(argv, 0, json.dumps(GATE_JSON), "")
            return guard.CommandResult(argv, 1, "", "boom: detail line\n")

    assert guard.main(["--root", str(tmp_path)], run=FailingRunner()) == 1
    out = capsys.readouterr().out
    assert "boom: detail line" in out


# --------------------------------------------------------------------------
# Machine-readable output (--json): a single, deterministic JSON object.
# --------------------------------------------------------------------------


def _json_report(capsys) -> dict:
    """Parse stdout as JSON; this itself proves no diagnostics were mixed in."""
    return json.loads(capsys.readouterr().out)


def test_json_mode_exits_zero_and_emits_json_only(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner()) == 0
    report = _json_report(capsys)
    assert isinstance(report, dict)


def test_json_mode_reports_the_expected_state(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner()) == 0
    report = _json_report(capsys)
    assert report["schema_version"] == "1"
    assert report["result"] == "READY FOR OWNER REVIEW"
    assert report["success"] is True
    assert report["target_version"] == "0.1.0"
    assert report["classification"] == "READY WITH WARNINGS"
    assert report["blockers"] == []
    assert set(report["warnings"]) == {"W7", "W12"}
    assert report["check_count"] == 12
    assert report["passed_count"] == 12
    assert report["failed_count"] == 0


def test_json_warnings_are_stably_sorted(tmp_path, capsys):
    make_repo(tmp_path)
    guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner())
    report = _json_report(capsys)
    # The gate emits ["W12", "W7"]; the report normalises to numeric order.
    assert report["warnings"] == ["W7", "W12"]


def test_json_checks_are_ordered_and_described(tmp_path, capsys):
    make_repo(tmp_path)
    guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner())
    report = _json_report(capsys)
    assert [check["name"] for check in report["checks"]] == [
        "Version",
        "Licensing",
        "Tests",
        "Labs",
        "Ruff",
        "Mypy",
        "MkDocs",
        "Release gate",
        "Warning drift",
        "Release manifest",
        "Git/tag state",
        "Final result",
    ]
    assert all(check["status"] == "PASS" for check in report["checks"])
    assert all(
        isinstance(check["details"], list) and check["details"]
        for check in report["checks"]
    )


def test_json_mode_preserves_the_exit_code_on_failure(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner(failures={"ruff"})) == 1
    report = _json_report(capsys)
    assert report["success"] is False
    assert report["result"] == "NOT READY"
    # The failing step and the final-result entry are both FAIL.
    assert report["failed_count"] == 2
    assert report["failed_count"] == report["check_count"] - report["passed_count"]
    statuses = {check["name"]: check["status"] for check in report["checks"]}
    assert statuses["Ruff"] == "FAIL"
    assert statuses["Final result"] == "FAIL"


def test_json_mode_reports_a_gate_blocker(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner(failures={"gate"})) == 1
    report = _json_report(capsys)
    assert report["success"] is False
    assert report["classification"] == "NOT READY"
    assert report["blockers"] == ["tests"]


def test_json_mode_still_runs_the_gate_exactly_once(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path), "--json"], run=runner)
    assert _gate_invocations(runner) == 1


def test_json_mode_reuses_the_same_captured_report(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path), "--json"], run=runner)
    paths = _gate_report_paths(runner)
    assert len(paths) == 2
    assert paths[0] == paths[1]


def test_json_mode_leaves_no_temporary_report(tmp_path):
    make_repo(tmp_path)
    runner = FakeRunner()
    guard.main(["--root", str(tmp_path), "--json"], run=runner)
    for path in _gate_report_paths(runner):
        assert not Path(path).exists()


def test_json_mode_leaves_the_repository_unmodified(tmp_path):
    make_repo(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    guard.main(["--root", str(tmp_path), "--json"], run=FakeRunner())
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


# --------------------------------------------------------------------------
# Tamper-evident attestation: generation.
# --------------------------------------------------------------------------


def _generate_json(tmp_path, capsys, runner=None) -> tuple[dict, FakeRunner]:
    """Run ``--json`` through a fresh runner and return the parsed report."""
    runner = FakeRunner() if runner is None else runner
    assert guard.main(["--root", str(tmp_path), "--json"], run=runner) == 0
    return json.loads(capsys.readouterr().out), runner


def _archived(tmp_path, report) -> Path:
    """Write a report to an archive **outside** the repository under test."""
    path = tmp_path.parent / f"{tmp_path.name}-archived-report.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def _verify(tmp_path, capsys, report_path, runner=None) -> tuple[int, str]:
    """Run ``--verify-report`` and return (exit code, combined output)."""
    runner = FakeRunner() if runner is None else runner
    rc = guard.main(
        ["--root", str(tmp_path), "--verify-report", str(report_path)], run=runner
    )
    captured = capsys.readouterr()
    return rc, captured.out + captured.err


def test_json_report_carries_a_sha256_attestation(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    attestation = report["attestation"]
    assert attestation["algorithm"] == "SHA-256"
    assert attestation["method"] == guard.ATTESTATION_METHOD
    assert re.fullmatch(r"[0-9a-f]{64}", attestation["repository_state_sha256"])
    assert re.fullmatch(r"[0-9a-f]{64}", attestation["report_payload_sha256"])


def test_attestation_is_deterministic(tmp_path, capsys):
    make_repo(tmp_path)
    first, _ = _generate_json(tmp_path, capsys)
    second, _ = _generate_json(tmp_path, capsys)
    assert first["attestation"] == second["attestation"]
    assert first == second


def test_attestation_has_no_timestamps_paths_or_machine_noise(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    blob = json.dumps(report["attestation"])
    assert str(tmp_path) not in blob
    assert "agentsec-pre-tag" not in blob
    assert not re.search(r"\d{4}-\d{2}-\d{2}T", blob)


def test_attestation_preserves_the_expected_state(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    assert report["result"] == "READY FOR OWNER REVIEW"
    assert report["warnings"] == ["W7", "W12"]
    assert report["check_count"] == 12
    assert report["passed_count"] == 12
    assert report["failed_count"] == 0


def test_json_mode_still_runs_the_gate_once_with_attestation(tmp_path, capsys):
    make_repo(tmp_path)
    _, runner = _generate_json(tmp_path, capsys)
    assert _gate_invocations(runner) == 1


# --------------------------------------------------------------------------
# Tamper-evident attestation: verification.
# --------------------------------------------------------------------------


def test_verify_accepts_a_valid_report(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 0
    assert "PASS" in out


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda r: r.__setitem__("success", False), "report payload hash mismatch"),
        (lambda r: r.__setitem__("warnings", ["W7"]), "report payload hash mismatch"),
        (lambda r: r.__setitem__("target_version", "9.9.9"), "report payload hash mismatch"),
        (
            lambda r: r["checks"][0].__setitem__("status", "FAIL"),
            "report payload hash mismatch",
        ),
    ],
)
def test_verify_rejects_a_modified_report(tmp_path, capsys, mutate, expected):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    mutate(report)
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert expected in out


def test_verify_rejects_a_modified_report_hash(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report["attestation"]["report_payload_sha256"] = "0" * 64
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert "report payload hash mismatch" in out


def test_verify_rejects_a_changed_repository_file(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    _write(tmp_path / "scripts" / "check_version.py", "# changed\n")
    rc, out = _verify(tmp_path, capsys, archived)
    assert rc == 1
    assert "repository state hash mismatch" in out


def test_verify_rejects_an_added_repository_file(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    _write(tmp_path / "docs" / "new-page.md", "# new\n")
    rc, out = _verify(tmp_path, capsys, archived)
    assert rc == 1
    assert "repository state hash mismatch" in out


def test_verify_rejects_a_deleted_repository_file(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    (tmp_path / "scripts" / "check_version.py").unlink()
    rc, out = _verify(tmp_path, capsys, archived)
    assert rc == 1
    assert "repository state hash mismatch" in out


def test_verify_rejects_a_missing_attestation(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report.pop("attestation")
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert "no attestation object" in out


def test_verify_rejects_a_malformed_hash(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report["attestation"]["repository_state_sha256"] = "not-a-hash"
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert "malformed repository_state_sha256" in out


def test_verify_rejects_an_unsupported_algorithm(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report["attestation"]["algorithm"] = "MD5"
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert "unsupported attestation algorithm" in out


def test_verify_rejects_an_unsupported_method(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report["attestation"]["method"] = "something-else"
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 1
    assert "unsupported attestation method" in out


def test_verify_does_not_run_the_release_gate_or_the_suite(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    runner = FakeRunner()
    rc, _ = _verify(tmp_path, capsys, archived, runner=runner)
    assert rc == 0
    assert _gate_invocations(runner) == 0
    assert not any("pytest" in call for call in runner.calls)
    assert not any("--gate-report" in call for call in runner.calls)


def test_verify_is_read_only(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    _verify(tmp_path, capsys, archived)
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


# --------------------------------------------------------------------------
# Owner-controlled signing.
# --------------------------------------------------------------------------


class FakeSigner:
    """A deterministic stand-in for the OpenSSL Ed25519 signer.

    Deterministic (HMAC-SHA-256) so signatures and key ids are reproducible
    without running OpenSSL; its interface matches ``OpenSSLEd25519Signer``.
    """

    algorithm = "Ed25519"
    encoding = "base64"
    key_id_method = "sha256-spki-der"

    def __init__(self, *, available: bool = True):
        self.available = available

    def check_available(self):
        if not self.available:
            raise guard.SignatureError(
                "the signing tool 'openssl' is not available on PATH"
            )

    @staticmethod
    def _secret(path) -> bytes:
        return Path(path).read_bytes()

    def sign(self, data, private_key):
        secret = self._secret(private_key)
        key_id = hashlib.sha256(secret).hexdigest()
        return key_id, hmac.new(secret, data, hashlib.sha256).digest()

    def key_id_from_public_key(self, public_key):
        return hashlib.sha256(self._secret(public_key)).hexdigest()

    def verify(self, data, signature, public_key):
        secret = self._secret(public_key)
        expected = hmac.new(secret, data, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)


SECRET = b"test-signing-secret"


def _keypair(tmp_path, *, secret=SECRET, name="keys"):
    """Write a fake key pair **outside** the repository under test."""
    directory = tmp_path.parent / f"{tmp_path.name}-{name}"
    directory.mkdir(exist_ok=True)
    private = directory / "private.pem"
    private.write_bytes(secret)
    public = directory / "public.pem"
    public.write_bytes(secret)
    return private, public


def _sign(
    tmp_path, capsys, report_path, *, private_key, output=None, signer=None, runner=None
):
    """Run ``--sign-report`` and return (exit code, combined output)."""
    runner = FakeRunner() if runner is None else runner
    signer = FakeSigner() if signer is None else signer
    argv = [
        "--root",
        str(tmp_path),
        "--sign-report",
        str(report_path),
        "--private-key",
        str(private_key),
    ]
    if output is not None:
        argv += ["--output", str(output)]
    rc = guard.main(argv, run=runner, signer=signer)
    captured = capsys.readouterr()
    return rc, captured.out + captured.err


def _verify_with_key(
    tmp_path, capsys, report_path, public_key, *, signer=None, runner=None
):
    """Run ``--verify-report --public-key`` and return (exit code, output)."""
    runner = FakeRunner() if runner is None else runner
    signer = FakeSigner() if signer is None else signer
    rc = guard.main(
        [
            "--root",
            str(tmp_path),
            "--verify-report",
            str(report_path),
            "--public-key",
            str(public_key),
        ],
        run=runner,
        signer=signer,
    )
    captured = capsys.readouterr()
    return rc, captured.out + captured.err


def _signed_report(tmp_path, capsys, *, secret=SECRET):
    """Generate, archive and sign a report; return (unsigned, signed, keys)."""
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, public = _keypair(tmp_path, secret=secret)
    output = tmp_path.parent / f"{tmp_path.name}-signed.json"
    rc, out = _sign(tmp_path, capsys, archived, private_key=private, output=output)
    assert rc == 0, out
    return report, json.loads(output.read_text(encoding="utf-8")), (private, public)


def test_signing_writes_a_valid_signed_report(tmp_path, capsys):
    _, signed, _ = _signed_report(tmp_path, capsys)
    assert signed["schema_version"] == "1"
    assert signed["result"] == "READY FOR OWNER REVIEW"
    assert signed["success"] is True


def test_signature_object_is_present_and_well_formed(tmp_path, capsys):
    _, signed, _ = _signed_report(tmp_path, capsys)
    envelope = signed["signature"]
    assert envelope["algorithm"] == "Ed25519"
    assert envelope["encoding"] == "base64"
    assert envelope["key_id_method"] == guard.SIGNATURE_KEY_ID_METHOD
    assert re.fullmatch(r"[0-9a-f]{64}", envelope["key_id"])
    # The signature is valid base64 of the signer's fixed-size digest.
    raw = base64.b64decode(envelope["signature"], validate=True)
    assert len(raw) == hashlib.sha256().digest_size


def test_signature_does_not_embed_the_private_key(tmp_path, capsys):
    _, signed, (private, _) = _signed_report(tmp_path, capsys)
    blob = json.dumps(signed)
    assert private.read_bytes().decode("ascii") not in blob
    assert "PRIVATE KEY" not in blob


def test_signature_records_a_public_key_fingerprint(tmp_path, capsys):
    _, signed, (private, _) = _signed_report(tmp_path, capsys)
    expected = hashlib.sha256(private.read_bytes()).hexdigest()
    assert signed["signature"]["key_id"] == expected


def test_signing_is_deterministic(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    first = tmp_path.parent / f"{tmp_path.name}-first.json"
    second = tmp_path.parent / f"{tmp_path.name}-second.json"
    assert _sign(tmp_path, capsys, archived, private_key=private, output=first)[0] == 0
    assert _sign(tmp_path, capsys, archived, private_key=private, output=second)[0] == 0
    assert first.read_bytes() == second.read_bytes()


def test_signing_does_not_change_the_payload_attestation(tmp_path, capsys):
    report, signed, _ = _signed_report(tmp_path, capsys)
    # The signature is an envelope: it must not perturb the attested payload.
    assert signed["attestation"] == report["attestation"]
    assert guard.report_payload_digest(signed) == report["attestation"][
        "report_payload_sha256"
    ]


def test_signing_preserves_every_report_field(tmp_path, capsys):
    report, signed, _ = _signed_report(tmp_path, capsys)
    for key, value in report.items():
        assert signed[key] == value
    assert set(signed) == set(report) | {"signature"}


def test_signing_refuses_a_report_with_an_invalid_attestation(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    report["success"] = False  # breaks report_payload_sha256
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    rc, out = _sign(tmp_path, capsys, archived, private_key=private)
    assert rc == 1
    assert "refusing to sign" in out
    assert "report payload hash mismatch" in out


def test_signing_default_output_is_a_new_file(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    before = archived.read_bytes()
    private, _ = _keypair(tmp_path)
    rc, out = _sign(tmp_path, capsys, archived, private_key=private)
    assert rc == 0, out
    derived = guard._signed_output_path(archived)
    assert derived.exists()
    assert derived != archived
    # The original report is untouched.
    assert archived.read_bytes() == before
    assert "signature" not in json.loads(archived.read_text(encoding="utf-8"))


def test_signing_can_overwrite_when_the_same_path_is_explicit(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    rc, out = _sign(
        tmp_path, capsys, archived, private_key=private, output=archived
    )
    assert rc == 0, out
    assert "signature" in json.loads(archived.read_text(encoding="utf-8"))


def test_signing_requires_a_private_key(tmp_path):
    make_repo(tmp_path)
    with pytest.raises(SystemExit):
        guard.main(  # argparse rejects the incomplete invocation.
            ["--root", str(tmp_path), "--sign-report", "report.json"], run=FakeRunner()
        )


def test_signing_reports_a_missing_tool_clearly(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    rc, out = _sign(
        tmp_path,
        capsys,
        archived,
        private_key=private,
        signer=FakeSigner(available=False),
    )
    assert rc == 1
    assert "not available on PATH" in out


# --------------------------------------------------------------------------
# Signature verification.
# --------------------------------------------------------------------------


def test_verify_unsigned_report_reports_no_signature(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    rc, out = _verify(tmp_path, capsys, _archived(tmp_path, report))
    assert rc == 0
    assert "attestation is valid" in out
    assert "signature" not in out.lower()


def test_verify_signed_report_without_a_key_is_not_verified(tmp_path, capsys):
    _, signed, _ = _signed_report(tmp_path, capsys)
    path = tmp_path.parent / f"{tmp_path.name}-signed.json"
    rc, out = _verify(tmp_path, capsys, path)
    assert rc == 0
    assert "attestation is valid" in out
    assert "not verified" in out


def test_verify_signed_report_with_the_correct_key_verifies(tmp_path, capsys):
    _, _, (_, public) = _signed_report(tmp_path, capsys)
    path = tmp_path.parent / f"{tmp_path.name}-signed.json"
    rc, out = _verify_with_key(tmp_path, capsys, path, public)
    assert rc == 0
    assert "signature verified" in out


def test_verify_signed_report_with_the_wrong_key_fails(tmp_path, capsys):
    _, _, _ = _signed_report(tmp_path, capsys)
    path = tmp_path.parent / f"{tmp_path.name}-signed.json"
    _, wrong = _keypair(tmp_path, secret=b"a-different-secret", name="wrong")
    rc, out = _verify_with_key(tmp_path, capsys, path, wrong)
    assert rc == 1
    assert "key_id mismatch" in out


def test_verify_rejects_a_modified_signed_report(tmp_path, capsys):
    _, signed, (_, public) = _signed_report(tmp_path, capsys)
    signed["warnings"] = ["W7"]
    path = tmp_path.parent / f"{tmp_path.name}-tampered.json"
    path.write_text(json.dumps(signed), encoding="utf-8")
    rc, out = _verify_with_key(tmp_path, capsys, path, public)
    assert rc == 1
    assert "report payload hash mismatch" in out


def test_verify_rejects_a_modified_signature(tmp_path, capsys):
    _, signed, (_, public) = _signed_report(tmp_path, capsys)
    signed["signature"]["signature"] = base64.b64encode(b"0" * 64).decode("ascii")
    path = tmp_path.parent / f"{tmp_path.name}-badsig.json"
    path.write_text(json.dumps(signed), encoding="utf-8")
    rc, out = _verify_with_key(tmp_path, capsys, path, public)
    assert rc == 1
    assert "does not match" in out


def test_verify_rejects_a_malformed_signature(tmp_path, capsys):
    _, signed, (_, public) = _signed_report(tmp_path, capsys)
    signed["signature"]["signature"] = "not valid base64!!"
    path = tmp_path.parent / f"{tmp_path.name}-malformed.json"
    path.write_text(json.dumps(signed), encoding="utf-8")
    rc, out = _verify_with_key(tmp_path, capsys, path, public)
    assert rc == 1
    assert "not valid base64" in out


def test_verify_rejects_an_unsupported_signature_algorithm(tmp_path, capsys):
    _, signed, (_, public) = _signed_report(tmp_path, capsys)
    signed["signature"]["algorithm"] = "RSA-SHA1"
    path = tmp_path.parent / f"{tmp_path.name}-alg.json"
    path.write_text(json.dumps(signed), encoding="utf-8")
    rc, out = _verify_with_key(tmp_path, capsys, path, public)
    assert rc == 1
    assert "unsupported signature algorithm" in out


def test_verify_with_a_key_on_an_unsigned_report_fails(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    _, public = _keypair(tmp_path)
    rc, out = _verify_with_key(tmp_path, capsys, archived, public)
    assert rc == 1
    assert "no signature object" in out


def test_verify_signature_does_not_run_the_release_gate(tmp_path, capsys):
    _, _, (_, public) = _signed_report(tmp_path, capsys)
    path = tmp_path.parent / f"{tmp_path.name}-signed.json"
    runner = FakeRunner()
    rc, _ = _verify_with_key(tmp_path, capsys, path, public, runner=runner)
    assert rc == 0
    assert _gate_invocations(runner) == 0
    assert not any("--gate-report" in call for call in runner.calls)


def test_verify_signature_is_read_only(tmp_path, capsys):
    _, _, (_, public) = _signed_report(tmp_path, capsys)
    path = tmp_path.parent / f"{tmp_path.name}-signed.json"
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    _verify_with_key(tmp_path, capsys, path, public)
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


# --------------------------------------------------------------------------
# Security: no key material, no repository mutation.
# --------------------------------------------------------------------------


def test_private_key_material_never_appears_in_output(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, public = _keypair(tmp_path)
    output = tmp_path.parent / f"{tmp_path.name}-signed.json"
    signer = FakeSigner()
    sign_rc = guard.main(
        [
            "--root",
            str(tmp_path),
            "--sign-report",
            str(archived),
            "--private-key",
            str(private),
            "--output",
            str(output),
        ],
        run=FakeRunner(),
        signer=signer,
    )
    verify_rc = guard.main(
        [
            "--root",
            str(tmp_path),
            "--verify-report",
            str(output),
            "--public-key",
            str(public),
        ],
        run=FakeRunner(),
        signer=signer,
    )
    captured = capsys.readouterr()
    assert sign_rc == 0 and verify_rc == 0
    for stream in (captured.out, captured.err):
        assert SECRET.decode("ascii") not in stream
    assert SECRET.decode("ascii") not in json.dumps(
        json.loads(output.read_text(encoding="utf-8"))
    )


def test_signing_leaves_the_repository_unmodified(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    _sign(tmp_path, capsys, archived, private_key=private)
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


def test_signing_never_commits_pushes_or_tags(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)
    private, _ = _keypair(tmp_path)
    runner = FakeRunner()
    _sign(tmp_path, capsys, archived, private_key=private, runner=runner)
    for call in runner.calls:
        assert "commit" not in call
        assert "push" not in call
        assert "tag" not in call


# --------------------------------------------------------------------------
# Real OpenSSL integration (skipped when the tool is unavailable).
# --------------------------------------------------------------------------

pytestmark_openssl = pytest.mark.skipif(
    shutil.which("openssl") is None, reason="openssl is not available"
)


@pytestmark_openssl
def test_real_openssl_ed25519_round_trip(tmp_path, capsys):
    make_repo(tmp_path)
    report, _ = _generate_json(tmp_path, capsys)
    archived = _archived(tmp_path, report)

    keys = tmp_path.parent / f"{tmp_path.name}-openssl-keys"
    keys.mkdir(exist_ok=True)
    private = keys / "private.pem"
    public = keys / "public.pem"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)],
        check=True,
        capture_output=True,
    )
    signer = guard.OpenSSLEd25519Signer()
    output = keys / "signed.json"
    rc, out = _sign(
        tmp_path, capsys, archived, private_key=private, output=output, signer=signer
    )
    assert rc == 0, out

    # The real fingerprint is the SHA-256 of the DER public key.
    der = subprocess.run(
        ["openssl", "pkey", "-pubin", "-in", str(public), "-outform", "DER"],
        check=True,
        capture_output=True,
    ).stdout
    signed = json.loads(output.read_text(encoding="utf-8"))
    assert signed["signature"]["key_id"] == hashlib.sha256(der).hexdigest()

    rc, out = _verify_with_key(tmp_path, capsys, output, public, signer=signer)
    assert rc == 0, out
    assert "signature verified" in out

    # Tampering with the report content is caught by the attestation first.
    signed["success"] = False
    tampered = keys / "tampered.json"
    tampered.write_text(json.dumps(signed), encoding="utf-8")
    rc, out = _verify_with_key(tmp_path, capsys, tampered, public, signer=signer)
    assert rc == 1
