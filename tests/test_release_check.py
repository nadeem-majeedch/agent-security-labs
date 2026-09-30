"""Tests for the release-gate runner in ``scripts/release_check.py``.

The runner orchestrates subprocesses, so the tests never invoke the real ones:
they inject a recording ``FakeRunner`` and drive the gates, the classification
and the report rendering directly. That keeps the suite hermetic, offline and
fast, and it lets a test assert exactly which commands the runner *would* run —
including that no mutating ``git`` subcommand is ever among them.

The gates that read files (readme, self-containment, hygiene, warnings) run
against small fixtures in ``tmp_path``, never against the checked-in files.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_check.py"


def _load_guard():
    """Import ``scripts/release_check.py``, which is not an installed module."""
    spec = importlib.util.spec_from_file_location("release_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()
CommandResult = guard.CommandResult

HEX40 = "a" * 40


def _token_matches(key: str, argv: tuple[str, ...]) -> bool:
    """Whether every word of ``key`` names an argument of ``argv``.

    Matching on whole arguments (by name, so a full script path matches its
    filename) avoids a substring like ``pytest`` matching a temporary directory
    whose path happens to contain it.
    """
    for word in key.split():
        if not any(token == word or Path(token).name == word for token in argv):
            return False
    return True


class FakeRunner:
    """A recording stand-in for ``run_command``.

    ``responses`` maps a small command signature to ``(rc, out, err)``; ``git``
    overrides the canned read-only git output per key.
    """

    def __init__(self, responses=None, git=None):
        self.calls: list[tuple[str, ...]] = []
        self.responses = dict(responses or {})
        self.git = {
            "inside": "true",
            "head": HEX40,
            "branch": "main",
            "status": "",
            "staged": "",
            "ls-files": "",
            "tags": "",
            "ignored": "",
            **(git or {}),
        }

    def __call__(self, argv, *, cwd, env=None, timeout=None):
        argv = tuple(str(item) for item in argv)
        self.calls.append(argv)
        if argv and argv[0] == "git":
            rest = argv[argv.index("-C") + 2 :] if "-C" in argv else argv[1:]
            sub = rest[0] if rest else ""
            if sub == "rev-parse":
                if "--is-inside-work-tree" in rest:
                    return CommandResult(argv, 0, self.git["inside"] + "\n", "")
                key = "branch" if "--abbrev-ref" in rest else "head"
                return CommandResult(argv, 0, self.git[key] + "\n", "")
            if sub == "ls-files":
                if "-i" in rest:
                    return CommandResult(argv, 0, self.git["ignored"], "")
                return CommandResult(argv, 0, self.git["ls-files"], "")
            if sub == "status":
                return CommandResult(argv, 0, self.git["status"], "")
            if sub == "diff":
                return CommandResult(argv, 0, self.git["staged"], "")
            if sub == "tag":
                return CommandResult(argv, 0, self.git["tags"], "")
            return CommandResult(argv, 0, "", "")
        for key, (rc, out, err) in self.responses.items():
            if _token_matches(key, argv):
                return CommandResult(argv, rc, out, err)
        return CommandResult(argv, 0, "", "")


def happy_runner(**overrides) -> FakeRunner:
    responses = {
        "pytest": (0, "800 passed in 1s\n", ""),
        "agentsec labs check": (0, "8/8 labs passed\n", ""),
        "mkdocs": (0, "", ""),
        "check_licensing.py": (0, "9/9 checks passed\n12 file(s) accounted for (mit 12)\n", ""),
        "check_version.py": (0, "3/3 checks passed\n", ""),
        "pip wheel": (1, "", "No module named 'setuptools'"),
    }
    responses.update(overrides)
    return FakeRunner(responses)


SCHEMA_BYTES = b'{"oneOf": []}\n'


def make_repo(root: Path, *, version="0.0.1", citation_date=None, schema=None) -> Path:
    """Write a minimal repository that the file-reading gates accept."""
    (root / "src" / "agentsec" / "schemas" / "trace").mkdir(parents=True, exist_ok=True)
    (root / "schemas" / "trace").mkdir(parents=True, exist_ok=True)
    (root / "licensing").mkdir(parents=True, exist_ok=True)
    body = SCHEMA_BYTES if schema is None else schema
    (root / "schemas" / "trace" / "trace_event.v1.schema.json").write_bytes(body)
    (root / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json").write_bytes(body)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "example"\nversion = "{version}"\n', encoding="utf-8"
    )
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (root / "README.md").write_text(
        "# Example\n\n## Licensing\n\nSee [LICENSE](LICENSE).\n", encoding="utf-8"
    )
    citation = f'cff-version: 1.2.0\nversion: "{version}"\n'
    if citation_date:
        citation += f"date-released: {citation_date}\n"
    (root / "CITATION.cff").write_text(citation, encoding="utf-8")
    (root / ".gitignore").write_text("runs/\n", encoding="utf-8")
    (root / "licensing" / "manifest.toml").write_text("schema-version = 1\n", encoding="utf-8")
    # Stub the two delegated guards; their behaviour is exercised by their own
    # test suites, and the runner only needs them to exist and exit per the fake.
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts" / "check_licensing.py").write_text("# guard\n", encoding="utf-8")
    (root / "scripts" / "check_version.py").write_text("# guard\n", encoding="utf-8")
    return root


def context(root: Path, scratch: Path):
    return guard.Context(root=root, scratch=scratch, python=sys.executable, env={})


# --------------------------------------------------------------------------
# The module stays stdlib-only and does not write into the repository.
# --------------------------------------------------------------------------


def test_release_check_imports_only_the_standard_library():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            imported.add((node.module or "").split(".")[0])
    allowed = {
        "__future__",
        "argparse",
        "dataclasses",
        "json",
        "os",
        "pathlib",
        "re",
        "shutil",
        "subprocess",
        "sys",
        "tempfile",
        "tomllib",
        "zipfile",
    }
    assert imported <= allowed, f"unexpected import(s): {sorted(imported - allowed)}"


def test_release_check_has_no_network_module():
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("urllib", "httpx", "requests"):
        assert forbidden not in source, f"the runner must not use {forbidden!r}"


def test_release_check_only_reads_the_tree():
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("write_text", "write_bytes", "open("):
        assert forbidden not in source, f"the runner must not modify files: {forbidden!r}"


def test_gates_are_in_the_documented_order():
    assert [name for name, _gate in guard.GATES] == [
        "tests",
        "labs",
        "mkdocs",
        "licensing",
        "version",
        "readme",
        "self_containment",
        "hygiene",
        "git_state",
    ]


# --------------------------------------------------------------------------
# Target version comes from pyproject.toml, never hard-coded.
# --------------------------------------------------------------------------


def test_target_version_is_read_from_pyproject(tmp_path):
    make_repo(tmp_path, version="9.9.9")
    assert guard.read_target_version(tmp_path) == "9.9.9"


def test_target_version_is_none_when_pyproject_is_missing(tmp_path):
    assert guard.read_target_version(tmp_path) is None


# --------------------------------------------------------------------------
# Classification logic.
# --------------------------------------------------------------------------


def _result(gate, status):
    return guard.GateResult(gate, status, "summary")


def test_classify_flags_nothing_is_ready():
    gates = [_result("tests", guard.PASS), _result("labs", guard.PASS)]
    assert guard.classify(gates, []) == guard.READY


def test_classify_with_a_warning_is_ready_with_warnings():
    gates = [_result("tests", guard.PASS)]
    assert guard.classify(gates, [guard.Warning("W6", "x")]) == guard.READY_WITH_WARNINGS


def test_classify_with_a_warned_gate_is_ready_with_warnings():
    gates = [_result("git_state", guard.WARN)]
    assert guard.classify(gates, []) == guard.READY_WITH_WARNINGS


def test_classify_with_a_failed_gate_is_not_ready_even_with_warnings():
    gates = [_result("tests", guard.FAIL), _result("labs", guard.PASS)]
    assert guard.classify(gates, [guard.Warning("W6", "x")]) == guard.NOT_READY


# --------------------------------------------------------------------------
# Individual gates: pass, warn and fail paths.
# --------------------------------------------------------------------------


def test_gate_tests_reports_the_count(tmp_path):
    result = guard.gate_tests(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.PASS
    assert "800 tests passed" in result.summary


def test_gate_tests_failure_is_actionable(tmp_path):
    runner = happy_runner(pytest=(1, "1 failed, 799 passed\n", ""))
    result = guard.gate_tests(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert result.exit_code == 1
    assert "failed" in result.summary
    assert result.inspect


def test_gate_labs_failure_is_actionable(tmp_path):
    runner = happy_runner(**{"agentsec labs check": (1, "1/8 labs passed\n", "")})
    result = guard.gate_labs(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert result.exit_code == 1
    assert "labs" in result.inspect.lower()


def test_gate_mkdocs_missing_dependency_is_a_warning(tmp_path):
    runner = happy_runner(mkdocs=(1, "", "No module named 'mkdocs'"))
    result = guard.gate_mkdocs(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.WARN
    assert "not installed" in result.summary


def test_gate_mkdocs_build_failure_is_a_failure(tmp_path):
    runner = happy_runner(mkdocs=(1, "WARNING - page missing", ""))
    result = guard.gate_mkdocs(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL


def test_gate_licensing_failure_is_actionable(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner(**{"check_licensing.py": (1, "Result: 1 of 9 checks failed\n", "")})
    result = guard.gate_licensing(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert result.exit_code == 1
    assert "licensing" in result.inspect.lower()


def test_gate_version_failure_is_actionable(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner(**{"check_version.py": (1, "Result: 1 of 3 checks failed\n", "")})
    result = guard.gate_version(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert "reconcile" in result.inspect.lower()


def test_gate_version_missing_script_fails(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "scripts" / "check_version.py").unlink()
    result = guard.gate_version(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.FAIL
    assert "missing" in result.summary


# --------------------------------------------------------------------------
# README links and anchors.
# --------------------------------------------------------------------------


def test_check_readme_accepts_a_valid_fixture(tmp_path):
    make_repo(tmp_path)
    ok, detail = guard.check_readme(tmp_path / "README.md", tmp_path)
    assert ok
    assert "1 relative links" in detail


def test_check_readme_detects_a_missing_link(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Example\n\nSee [gone](docs/missing.md).\n", encoding="utf-8"
    )
    ok, detail = guard.check_readme(tmp_path / "README.md", tmp_path)
    assert not ok
    assert "docs/missing.md" in detail


def test_check_readme_detects_an_unresolved_anchor(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "README.md").write_text(
        "# Example\n\n[Jump](#nowhere)\n", encoding="utf-8"
    )
    ok, detail = guard.check_readme(tmp_path / "README.md", tmp_path)
    assert not ok
    assert "nowhere" in detail


def test_gate_readme_missing_file_fails(tmp_path):
    result = guard.gate_readme(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.FAIL
    assert "missing" in result.detail


# --------------------------------------------------------------------------
# Self-containment.
# --------------------------------------------------------------------------


def test_gate_self_containment_fails_when_the_packaged_schema_is_missing(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json").unlink()
    result = guard.gate_self_containment(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.FAIL
    assert "packaged trace schema is missing" in result.summary


def test_gate_self_containment_fails_when_the_copies_differ(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json").write_bytes(
        b"different"
    )
    result = guard.gate_self_containment(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.FAIL
    assert "differs" in result.summary


def test_gate_self_containment_warns_when_the_wheel_cannot_be_built(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner(**{"pip wheel": (1, "", "could not fetch setuptools")})
    result = guard.gate_self_containment(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.WARN
    assert "byte-identical" in result.summary
    assert result.inspect


# --------------------------------------------------------------------------
# Hygiene.
# --------------------------------------------------------------------------


def test_gate_hygiene_passes_on_a_clean_tree(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner()
    runner.git["ls-files"] = "README.md\nLICENSE\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.PASS


def test_gate_hygiene_flags_a_tracked_editor_file(tmp_path):
    make_repo(tmp_path)
    (tmp_path / ".DS_Store").write_text("junk\n", encoding="utf-8")
    runner = happy_runner()
    runner.git["ls-files"] = ".DS_Store\nREADME.md\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert ".DS_Store" in result.detail


def test_gate_hygiene_flags_a_todo_marker_in_source(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "src" / "agentsec" / "x.py").write_text("# TODO: fix\n", encoding="utf-8")
    runner = happy_runner()
    runner.git["ls-files"] = "src/agentsec/x.py\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert "TODO" in result.detail


def test_gate_hygiene_flags_a_secret_shaped_value(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "src" / "agentsec" / "x.py").write_text(
        'key = "AKIAIOSFODNN7EXAMPLE"\n', encoding="utf-8"
    )
    runner = happy_runner()
    runner.git["ls-files"] = "src/agentsec/x.py\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert "secret-shaped" in result.detail


def test_gate_hygiene_flags_a_tracked_ignored_file(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner()
    runner.git["ls-files"] = "README.md\n"
    runner.git["ignored"] = "runs/trace.jsonl\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.FAIL
    assert "git-ignored" in result.detail


def test_gate_hygiene_does_not_scan_tests_or_research_for_secrets(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "note.md").write_text(
        "AKIAIOSFODNN7EXAMPLE\n", encoding="utf-8"
    )
    runner = happy_runner()
    runner.git["ls-files"] = "research/note.md\nREADME.md\n"
    result = guard.gate_hygiene(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.PASS


# --------------------------------------------------------------------------
# Git state.
# --------------------------------------------------------------------------


def test_gate_git_state_clean_is_pass(tmp_path):
    result = guard.gate_git_state(context(tmp_path, tmp_path / "s"), happy_runner())
    assert result.status == guard.PASS
    assert "clean" in result.summary


def test_gate_git_state_dirty_is_a_warning(tmp_path):
    runner = happy_runner()
    runner.git["status"] = " M README.md\n?? new.txt\n"
    result = guard.gate_git_state(context(tmp_path, tmp_path / "s"), runner)
    assert result.status == guard.WARN
    assert "1 modified" in result.detail
    assert "1 untracked" in result.detail


def test_gate_git_state_outside_a_repository_is_a_failure(tmp_path):
    class NoGit(FakeRunner):
        def __call__(self, argv, *, cwd, env=None, timeout=None):
            return CommandResult(tuple(str(a) for a in argv), 128, "", "not a git repository")

    result = guard.gate_git_state(context(tmp_path, tmp_path / "s"), NoGit())
    assert result.status == guard.FAIL
    assert "not a Git working tree" in result.summary


def test_gate_git_state_without_commits_is_a_failure(tmp_path):
    class NoHead(FakeRunner):
        def __call__(self, argv, *, cwd, env=None, timeout=None):
            argv = tuple(str(a) for a in argv)
            self.calls.append(argv)
            rest = argv[argv.index("-C") + 2 :] if "-C" in argv else argv[1:]
            if rest[:1] == ("rev-parse",) and "HEAD" in rest:
                return CommandResult(argv, 128, "", "unknown revision")
            return super().__call__(argv, cwd=cwd, env=env, timeout=timeout)

    result = guard.gate_git_state(context(tmp_path, tmp_path / "s"), NoHead())
    assert result.status == guard.FAIL
    assert "no commits" in result.summary


# --------------------------------------------------------------------------
# Known warnings are detected, and nothing new is invented.
# --------------------------------------------------------------------------


def test_detect_warnings_reports_w6_when_date_released_is_absent(tmp_path):
    make_repo(tmp_path, citation_date=None)
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())]
    assert "W6" in ids


def test_detect_warnings_omits_w6_when_date_released_is_present(tmp_path):
    make_repo(tmp_path, citation_date="2026-01-01")
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())]
    assert "W6" not in ids


def test_detect_warnings_reports_w7_when_project_id_is_tracked(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner()
    runner.git["ls-files"] = ".freebuff/project-id\n"
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), runner)]
    assert "W7" in ids


def test_detect_warnings_reports_w10_and_w11_for_legacy_pyproject(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "0.0.1"\n'
        'license = { text = "MIT" }\n'
        '[project.optional-dependencies]\ndocs = ["mkdocs-material>=9"]\n',
        encoding="utf-8",
    )
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())]
    assert "W10" in ids
    assert "W11" in ids


def test_detect_warnings_reports_w13_when_traces_directory_is_absent(tmp_path):
    make_repo(tmp_path)
    (tmp_path / ".gitignore").write_text("traces/*.jsonl\n", encoding="utf-8")
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())]
    assert "W13" in ids


def test_detect_warnings_always_includes_the_w12_residual(tmp_path):
    make_repo(tmp_path)
    ids = [w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())]
    assert "W12" in ids


def test_detect_warnings_uses_only_the_known_identifiers(tmp_path):
    make_repo(tmp_path)
    known = {"W6", "W7", "W9", "W10", "W11", "W12", "W13"}
    ids = {w.id for w in guard.detect_warnings(context(tmp_path, tmp_path / "s"), happy_runner())}
    assert ids <= known, sorted(ids - known)


# --------------------------------------------------------------------------
# Report assembly, rendering and the CLI contract.
# --------------------------------------------------------------------------


def test_build_report_has_the_documented_shape(tmp_path):
    make_repo(tmp_path)
    report = guard.build_report(context(tmp_path, tmp_path / "s"), happy_runner())
    assert set(report) >= {
        "target_version",
        "classification",
        "blockers",
        "warnings",
        "gates",
        "gate_details",
        "warning_details",
        "repository",
    }
    assert set(report["gates"]) == {name for name, _gate in guard.GATES}
    assert report["target_version"] == "0.0.1"
    assert report["classification"] == guard.READY_WITH_WARNINGS
    assert report["blockers"] == []


def test_build_report_with_a_blocker_is_not_ready(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner(pytest=(1, "1 failed\n", ""))
    report = guard.build_report(context(tmp_path, tmp_path / "s"), runner)
    assert report["classification"] == guard.NOT_READY
    assert report["blockers"] == ["tests"]


def test_main_human_output_shows_the_classification(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path)], run=happy_runner()) == 0
    out = capsys.readouterr().out
    assert "Classification: READY WITH WARNINGS" in out
    assert "release gate" in out


def test_main_json_flag_emits_valid_json(tmp_path, capsys):
    make_repo(tmp_path)
    assert guard.main(["--root", str(tmp_path), "--json"], run=happy_runner()) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["classification"] == guard.READY_WITH_WARNINGS
    assert report["gates"]["tests"] == guard.PASS


def test_main_returns_nonzero_when_not_ready(tmp_path):
    make_repo(tmp_path)
    runner = happy_runner(pytest=(1, "boom\n", ""))
    assert guard.main(["--root", str(tmp_path)], run=runner) == 1


def test_main_is_read_only_and_runs_no_git_write_command(tmp_path):
    make_repo(tmp_path)
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    runner = happy_runner()
    assert guard.main(["--root", str(tmp_path)], run=runner) == 0
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert before == after, "the runner must not modify the repository"

    read_only = {"rev-parse", "ls-files", "status", "diff", "tag"}
    for call in runner.calls:
        if call and call[0] == "git":
            rest = call[call.index("-C") + 2 :] if "-C" in call else call[1:]
            sub = rest[0] if rest else ""
            assert sub in read_only, f"unexpected git call: {call}"
            if sub == "tag":
                assert len(rest) == 1, f"git tag must only list tags: {call}"
