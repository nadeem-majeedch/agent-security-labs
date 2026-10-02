"""Tests for the accepted-warning drift check in ``scripts/check_warning_drift.py``.

The check compares three surfaces that must agree: the policy constant in
``tests/test_release_check.py``, the documented set on
``labs/ACCEPTED-RELEASE-WARNINGS.md`` and the warnings the release gate actually
emits. These tests pin the comparison logic with explicit surface objects and
exercise the file readers and the CLI against small fixtures in ``tmp_path``.

The end-to-end fixture stubs ``scripts/release_check.py`` with a tiny JSON
printer, so no test ever runs the real (slow, gate-running) release check — and
the check stays hermetic, offline and fast.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_warning_drift.py"


def _load_guard():
    """Import ``scripts/check_warning_drift.py``, which is not a package module."""
    spec = importlib.util.spec_from_file_location("check_warning_drift", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


# --------------------------------------------------------------------------
# Fixtures: a repository whose three surfaces are trivially satisfiable.
# --------------------------------------------------------------------------

POLICY_REL = "tests/test_release_check.py"
DOC_REL = "labs/ACCEPTED-RELEASE-WARNINGS.md"
RELEASE_REL = "scripts/release_check.py"


def _source(name: str, ids) -> object:
    return guard.Source(name, frozenset(ids))


def write_policy(root: Path, ids) -> None:
    path = root / POLICY_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    body = ", ".join(f'"{item}"' for item in sorted(ids))
    path.write_text(
        "from __future__ import annotations\n\n"
        f"ACCEPTED_RELEASE_WARNINGS = frozenset({{{body}}})\n",
        encoding="utf-8",
    )


def write_doc(root: Path, raw_ids: str) -> None:
    path = root / DOC_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Accepted Release Warnings (v0.1.0)\n\n"
        f"## {guard.DOC_MARKER} `{{{raw_ids}}}`\n",
        encoding="utf-8",
    )


def write_release_stub(root: Path, ids) -> None:
    """A stand-in release check that prints the given warning IDs as JSON."""
    path = root / RELEASE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    literal = "[" + ", ".join(repr(item) for item in sorted(ids)) + "]"
    path.write_text(
        "import json\n"
        f"print(json.dumps({{'warnings': {literal}}}))\n",
        encoding="utf-8",
    )


def make_tree(root: Path, *, policy, documented, actual) -> Path:
    write_policy(root, policy)
    write_doc(root, ", ".join(sorted(documented)))
    write_release_stub(root, actual)
    return root


# --------------------------------------------------------------------------
# The script stays read-only, offline and standard-library-only.
# --------------------------------------------------------------------------


def test_check_imports_only_the_standard_library():
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
        "ast",
        "dataclasses",
        "json",
        "pathlib",
        "re",
        "subprocess",
        "sys",
    }
    assert imported <= allowed, f"unexpected import(s): {sorted(imported - allowed)}"


def test_check_does_not_modify_anything_or_use_the_network():
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("write_text", "write_bytes", "mkdir", "open(", "urlopen", "requests"):
        assert forbidden not in source, f"the check must be read-only: {forbidden!r}"


# --------------------------------------------------------------------------
# Reading each surface.
# --------------------------------------------------------------------------


def test_load_policy_reads_the_frozenset(tmp_path):
    write_policy(tmp_path, {"W7", "W12"})
    source = guard.load_policy(tmp_path)
    assert source.ids == frozenset({"W7", "W12"})
    assert source.problem == ""


def test_load_policy_missing_file_is_reported(tmp_path):
    source = guard.load_policy(tmp_path)
    assert source.ids is None
    assert "missing" in source.problem


def test_load_policy_rejects_a_non_set_value(tmp_path):
    path = tmp_path / POLICY_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ACCEPTED_RELEASE_WARNINGS = ['W7']\n", encoding="utf-8")
    source = guard.load_policy(tmp_path)
    assert source.ids is None
    assert "not a set of string literals" in source.problem


def test_load_documented_reads_the_canonical_statement(tmp_path):
    write_doc(tmp_path, "W7, W12")
    source = guard.load_documented(tmp_path)
    assert source.ids == frozenset({"W7", "W12"})
    assert source.problem == ""


def test_load_documented_reports_a_malformed_identifier(tmp_path):
    write_doc(tmp_path, "W7, X9")
    source = guard.load_documented(tmp_path)
    assert source.ids == frozenset({"W7", "X9"})
    assert "malformed" in source.problem
    assert "X9" in source.problem


def test_load_documented_reports_a_missing_statement(tmp_path):
    path = tmp_path / DOC_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Accepted Release Warnings\n\nNothing here.\n", encoding="utf-8")
    source = guard.load_documented(tmp_path)
    assert source.ids is None
    assert guard.DOC_MARKER in source.problem


def test_load_actual_reads_the_json_warnings_list(tmp_path):
    write_release_stub(tmp_path, {"W7", "W12"})
    source = guard.load_actual(tmp_path)
    assert source.ids == frozenset({"W7", "W12"})
    assert source.problem == ""


def test_load_actual_reports_non_json_output(tmp_path):
    path = tmp_path / RELEASE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("print('not json')\n", encoding="utf-8")
    source = guard.load_actual(tmp_path)
    assert source.ids is None
    assert "did not emit JSON" in source.problem


# --------------------------------------------------------------------------
# The comparison logic: agreement and every drift direction.
# --------------------------------------------------------------------------


def test_all_three_sets_agree():
    report = guard.compare(
        (
            _source("policy", {"W7", "W12"}),
            _source("documentation", {"W7", "W12"}),
            _source("actual", {"W7", "W12"}),
        )
    )
    assert report.ok
    assert report.problems == ()


def test_policy_accepted_but_missing_from_documentation():
    report = guard.compare(
        (
            _source("policy", {"W7", "W12"}),
            _source("documentation", {"W7"}),
            _source("actual", {"W7", "W12"}),
        )
    )
    assert not report.ok
    assert any("missing from documentation" in p for p in report.problems)
    assert any("W12" in p for p in report.problems)


def test_documented_but_missing_from_policy():
    report = guard.compare(
        (
            _source("policy", {"W7"}),
            _source("documentation", {"W7", "W12"}),
            _source("actual", {"W7"}),
        )
    )
    assert not report.ok
    assert any("missing from policy" in p for p in report.problems)


def test_unexpected_warning_in_the_gate():
    report = guard.compare(
        (
            _source("policy", {"W7", "W12"}),
            _source("documentation", {"W7", "W12"}),
            _source("actual", {"W7", "W12", "W14"}),
        )
    )
    assert not report.ok
    assert any("not accepted by policy" in p for p in report.problems)
    assert any("W14" in p for p in report.problems)


def test_accepted_warning_disappeared_from_the_gate():
    report = guard.compare(
        (
            _source("policy", {"W7", "W12"}),
            _source("documentation", {"W7", "W12"}),
            _source("actual", {"W7"}),
        )
    )
    assert not report.ok
    assert any("disappeared" in p for p in report.problems)


def test_documentation_and_gate_disagree():
    report = guard.compare(
        (
            _source("policy", {"W7", "W12"}),
            _source("documentation", {"W7"}),
            _source("actual", {"W12"}),
        )
    )
    assert not report.ok
    assert any("documentation and the gate disagree" in p for p in report.problems)


def test_a_source_problem_is_surfaced():
    report = guard.compare(
        (
            _source("policy", {"W7"}),
            guard.Source("documentation", None, "no documented set"),
            _source("actual", {"W7"}),
        )
    )
    assert not report.ok
    assert any("no documented set" in p for p in report.problems)


def test_malformed_documented_identifier_is_surfaced():
    report = guard.compare(
        (
            _source("policy", {"W7"}),
            guard.Source("documentation", frozenset({"W7", "X9"}), "malformed X9"),
            _source("actual", {"W7"}),
        )
    )
    assert not report.ok
    assert any("malformed" in p for p in report.problems)


# --------------------------------------------------------------------------
# Report rendering and the CLI contract (against stubbed fixtures).
# --------------------------------------------------------------------------


def test_format_report_shows_all_three_sets(tmp_path):
    make_tree(tmp_path, policy={"W7", "W12"}, documented={"W7", "W12"}, actual={"W7", "W12"})
    report = guard.run_checks(tmp_path)
    text = guard.format_report(report)
    assert "policy" in text
    assert "documentation" in text
    assert "actual gate" in text
    assert "all three sets agree" in text


def test_format_report_flags_drift(tmp_path):
    make_tree(tmp_path, policy={"W7", "W12"}, documented={"W7"}, actual={"W7", "W12"})
    report = guard.run_checks(tmp_path)
    text = guard.format_report(report)
    assert "DRIFT DETECTED" in text
    assert "missing from documentation" in text


def test_main_returns_zero_when_the_sets_agree(tmp_path, capsys):
    make_tree(tmp_path, policy={"W7", "W12"}, documented={"W7", "W12"}, actual={"W7", "W12"})
    assert guard.main(["--root", str(tmp_path)]) == 0
    assert "all three sets agree" in capsys.readouterr().out


def test_main_returns_nonzero_when_the_sets_drift(tmp_path, capsys):
    make_tree(tmp_path, policy={"W7", "W12"}, documented={"W7"}, actual={"W7", "W12"})
    assert guard.main(["--root", str(tmp_path)]) == 1
    assert "DRIFT DETECTED" in capsys.readouterr().out


# --------------------------------------------------------------------------
# The real repository's readable surfaces agree (the actual set is pinned by
# the exact-set test in tests/test_release_check.py).
# --------------------------------------------------------------------------


def test_real_repository_surfaces_agree():
    policy = guard.load_policy(ROOT)
    documented = guard.load_documented(ROOT)
    assert policy.problem == "", policy.problem
    assert documented.problem == "", documented.problem
    assert policy.ids == frozenset({"W7", "W12"})
    assert documented.ids == policy.ids


# --------------------------------------------------------------------------
# Reading the actual set from an existing --gate-report file (the CI path).
# These fixtures deliberately omit scripts/release_check.py, proving the gate
# is not run when a report is supplied.
# --------------------------------------------------------------------------


def write_gate_report(root: Path, ids, *, text: str | None = None) -> Path:
    path = root / "gate-report.json"
    if text is None:
        text = json.dumps({"warnings": sorted(ids)})
    path.write_text(text, encoding="utf-8")
    return path


def test_load_actual_from_report_reads_the_warnings_list(tmp_path):
    path = write_gate_report(tmp_path, {"W7", "W12"})
    source = guard.load_actual_from_report(path)
    assert source.ids == frozenset({"W7", "W12"})
    assert source.problem == ""


def test_load_actual_from_report_missing_file_is_reported(tmp_path):
    source = guard.load_actual_from_report(tmp_path / "nope.json")
    assert source.ids is None
    assert "missing" in source.problem


def test_load_actual_from_report_rejects_malformed_json(tmp_path):
    path = write_gate_report(tmp_path, set(), text="{")
    source = guard.load_actual_from_report(path)
    assert source.ids is None
    assert "not valid JSON" in source.problem


def test_load_actual_from_report_requires_a_warnings_list(tmp_path):
    path = write_gate_report(tmp_path, set(), text=json.dumps({"gates": {}}))
    source = guard.load_actual_from_report(path)
    assert source.ids is None
    assert "no 'warnings' list" in source.problem


def test_load_actual_from_report_flags_malformed_ids(tmp_path):
    path = write_gate_report(tmp_path, set(), text=json.dumps({"warnings": ["W7", "X9"]}))
    source = guard.load_actual_from_report(path)
    assert source.ids == frozenset({"W7", "X9"})
    assert "malformed" in source.problem


def test_run_checks_uses_the_gate_report_without_running_the_gate(tmp_path):
    write_policy(tmp_path, {"W7", "W12"})
    write_doc(tmp_path, "W7, W12")
    report = write_gate_report(tmp_path, {"W7", "W12"})
    # No scripts/release_check.py exists here, so running the gate would fail.
    result = guard.run_checks(tmp_path, gate_report=report)
    assert result.ok, result.problems


def test_main_gate_report_exits_zero_when_the_sets_agree(tmp_path, capsys):
    write_policy(tmp_path, {"W7", "W12"})
    write_doc(tmp_path, "W7, W12")
    report = write_gate_report(tmp_path, {"W7", "W12"})
    assert guard.main(["--root", str(tmp_path), "--gate-report", str(report)]) == 0
    assert "all three sets agree" in capsys.readouterr().out


@pytest.mark.parametrize(
    "actual",
    [
        {"W7"},  # an accepted warning disappeared
        {"W7", "W12", "W14"},  # an unexpected new warning
    ],
)
def test_main_gate_report_fails_on_gate_drift(tmp_path, capsys, actual):
    write_policy(tmp_path, {"W7", "W12"})
    write_doc(tmp_path, "W7, W12")
    report = write_gate_report(tmp_path, actual)
    assert guard.main(["--root", str(tmp_path), "--gate-report", str(report)]) == 1
    assert "DRIFT DETECTED" in capsys.readouterr().out


def test_main_gate_report_fails_on_policy_documentation_mismatch(tmp_path, capsys):
    write_policy(tmp_path, {"W7", "W12"})
    write_doc(tmp_path, "W7")
    report = write_gate_report(tmp_path, {"W7", "W12"})
    assert guard.main(["--root", str(tmp_path), "--gate-report", str(report)]) == 1
    assert "missing from documentation" in capsys.readouterr().out


def test_main_gate_report_fails_on_a_missing_report(tmp_path, capsys):
    write_policy(tmp_path, {"W7"})
    write_doc(tmp_path, "W7")
    missing = tmp_path / "none.json"
    assert guard.main(["--root", str(tmp_path), "--gate-report", str(missing)]) == 1
    out = capsys.readouterr().out
    assert "DRIFT DETECTED" in out
    assert "missing" in out
