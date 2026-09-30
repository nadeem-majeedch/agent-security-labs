"""Tests for the version-consistency guard in ``scripts/check_version.py``.

The guard is a small consistency check, so these tests pin its contract from
both directions: the real repository must satisfy it, and each declaration must
be able to fail on its own. The failure cases run against minimal fixtures in
``tmp_path``, never against the checked-in files.

The guard parses declarations rather than matching text, so the malformed cases
matter as much as the mismatch cases: a missing file, an absent key, a
non-string value and a syntactically broken file each have to fail clearly
rather than slip through as "no drift found".
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_version.py"

PYPROJECT = "pyproject.toml"
INIT = "src/agentsec/__init__.py"
CITATION = "CITATION.cff"

VERSION = "0.0.1"


def _load_guard():
    """Import ``scripts/check_version.py``, which is not an installed module."""
    spec = importlib.util.spec_from_file_location("check_version", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # Register before executing: ``@dataclass`` looks the module up in sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


# --------------------------------------------------------------------------
# Fixtures: a minimal repository whose three declarations agree.
# --------------------------------------------------------------------------

PYPROJECT_TEXT = (
    "[project]\n"
    'name = "example"\n'
    f'version = "{VERSION}"\n'
)

INIT_TEXT = f'__version__ = "{VERSION}"\n'

CITATION_TEXT = (
    "cff-version: 1.2.0\n"
    'title: "Example"\n'
    "type: software\n"
    f'version: "{VERSION}"\n'
)

FILES = {
    PYPROJECT: PYPROJECT_TEXT,
    INIT: INIT_TEXT,
    CITATION: CITATION_TEXT,
}


def make_repo(root: Path, **overrides) -> Path:
    """Write a minimal repository that satisfies the version contract.

    An override value of ``None`` omits that file; any other value replaces its
    contents.
    """
    contents = dict(FILES)
    contents.update(overrides)
    for name, text in contents.items():
        if text is None:
            continue
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def results_for(root: Path) -> dict[str, object]:
    return {result.name: result for result in guard.run_checks(root)}


def failures_for(root: Path) -> list[str]:
    return [result.name for result in guard.run_checks(root) if not result.ok]


# --------------------------------------------------------------------------
# The contract holds for the real repository.
# --------------------------------------------------------------------------


def test_current_repository_satisfies_the_version_contract():
    results = guard.run_checks(ROOT)
    assert [r.name for r in results] == [
        "pyproject.toml",
        "agentsec.__version__",
        "CITATION.cff",
    ], "the report order is part of the CI output"
    assert [(r.name, r.detail) for r in results if not r.ok] == []


def test_guard_reports_every_check_passing(capsys):
    assert guard.main(["--root", str(ROOT)]) == 0
    out = capsys.readouterr().out
    assert "3/3 checks passed" in out
    assert "FAIL" not in out


def test_valid_fixture_passes(tmp_path):
    make_repo(tmp_path)
    assert failures_for(tmp_path) == []


# --------------------------------------------------------------------------
# A mismatch in each declaration fails on its own and names the source.
# --------------------------------------------------------------------------


def test_mismatched_dunder_version_fails(tmp_path):
    make_repo(tmp_path, **{INIT: '__version__ = "0.0.2"\n'})
    results = results_for(tmp_path)
    assert "agentsec.__version__" in failures_for(tmp_path)
    detail = results["agentsec.__version__"].detail
    assert "'0.0.2'" in detail and "'0.0.1'" in detail
    assert PYPROJECT in detail


def test_mismatched_citation_version_fails(tmp_path):
    make_repo(tmp_path, **{CITATION: 'cff-version: 1.2.0\nversion: "0.0.2"\n'})
    results = results_for(tmp_path)
    assert "CITATION.cff" in failures_for(tmp_path)
    detail = results["CITATION.cff"].detail
    assert "'0.0.2'" in detail and "'0.0.1'" in detail


def test_mismatched_pyproject_version_fails(tmp_path):
    """Changing the source of truth makes the declarations that still name the
    old value fail, and the report states both the expected and observed
    values."""
    make_repo(
        tmp_path,
        **{PYPROJECT: '[project]\nname = "example"\nversion = "0.0.2"\n'},
    )
    results = results_for(tmp_path)
    failures = failures_for(tmp_path)
    assert "agentsec.__version__" in failures
    assert "CITATION.cff" in failures
    # The authoritative declaration itself is still a valid declaration.
    assert "pyproject.toml" not in failures
    assert "'0.0.2'" in results["agentsec.__version__"].detail
    assert "'0.0.1'" in results["agentsec.__version__"].detail


def test_a_quoting_style_in_citation_still_agrees(tmp_path):
    make_repo(tmp_path, **{CITATION: f"cff-version: 1.2.0\nversion: {VERSION}\n"})
    assert failures_for(tmp_path) == []


def test_dunder_version_may_be_annotated(tmp_path):
    make_repo(tmp_path, **{INIT: f'__version__: str = "{VERSION}"\n'})
    assert failures_for(tmp_path) == []


# --------------------------------------------------------------------------
# Malformed or missing declarations fail clearly.
# --------------------------------------------------------------------------


def test_a_missing_pyproject_makes_the_dependents_fail(tmp_path):
    make_repo(tmp_path, **{PYPROJECT: None})
    failures = failures_for(tmp_path)
    assert failures == ["pyproject.toml", "agentsec.__version__", "CITATION.cff"]
    assert "missing" in results_for(tmp_path)["pyproject.toml"].detail
    unverifiable = results_for(tmp_path)["agentsec.__version__"].detail
    assert "unavailable" in unverifiable and PYPROJECT in unverifiable


def test_a_missing_init_file_fails(tmp_path):
    make_repo(tmp_path, **{INIT: None})
    assert "agentsec.__version__" in failures_for(tmp_path)


def test_a_missing_citation_file_fails(tmp_path):
    make_repo(tmp_path, **{CITATION: None})
    assert "CITATION.cff" in failures_for(tmp_path)


def test_pyproject_that_is_not_toml_is_reported(tmp_path):
    make_repo(tmp_path, **{PYPROJECT: '[project\nversion = "0.0.1"\n'})
    assert "not valid TOML" in results_for(tmp_path)[PYPROJECT].detail


def test_pyproject_without_a_version_is_reported(tmp_path):
    make_repo(tmp_path, **{PYPROJECT: '[project]\nname = "example"\n'})
    assert "no project.version" in results_for(tmp_path)[PYPROJECT].detail


def test_pyproject_version_must_be_a_string(tmp_path):
    make_repo(tmp_path, **{PYPROJECT: "[project]\nversion = 1\n"})
    assert "non-empty string" in results_for(tmp_path)[PYPROJECT].detail


def test_an_empty_pyproject_version_is_reported(tmp_path):
    make_repo(tmp_path, **{PYPROJECT: '[project]\nversion = "  "\n'})
    assert "non-empty string" in results_for(tmp_path)[PYPROJECT].detail


def test_init_without_a_version_is_reported(tmp_path):
    make_repo(tmp_path, **{INIT: "x = 1\n"})
    assert "no module-level __version__" in results_for(tmp_path)[
        "agentsec.__version__"
    ].detail


def test_init_version_must_be_a_string_literal(tmp_path):
    make_repo(tmp_path, **{INIT: "__version__ = 1\n"})
    assert "non-string" in results_for(tmp_path)["agentsec.__version__"].detail


def test_a_nested_dunder_version_is_not_the_module_version(tmp_path):
    make_repo(tmp_path, **{INIT: 'def f():\n    __version__ = "9.9.9"\n'})
    assert "no module-level __version__" in results_for(tmp_path)[
        "agentsec.__version__"
    ].detail


def test_a_missing_citation_version_is_reported(tmp_path):
    make_repo(tmp_path, **{CITATION: "cff-version: 1.2.0\ntitle: Example\n"})
    assert "no top-level 'version:'" in results_for(tmp_path)[CITATION].detail


def test_an_empty_citation_version_is_reported(tmp_path):
    make_repo(tmp_path, **{CITATION: "cff-version: 1.2.0\nversion:\n"})
    assert "empty" in results_for(tmp_path)[CITATION].detail


def test_a_nested_citation_version_is_not_the_document_version(tmp_path):
    make_repo(
        tmp_path,
        **{CITATION: "cff-version: 1.2.0\npreferred-citation:\n  version: 9.9.9\n"},
    )
    assert "no top-level 'version:'" in results_for(tmp_path)[CITATION].detail


def test_failing_run_explains_itself_and_exits_nonzero(tmp_path, capsys):
    make_repo(tmp_path, **{INIT: '__version__ = "0.0.2"\n'})
    assert guard.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "agentsec.__version__" in out
    assert "failed" in out


# --------------------------------------------------------------------------
# The guard stays offline, read-only and dependency-free.
# --------------------------------------------------------------------------


def test_guard_imports_only_the_standard_library():
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
        "pathlib",
        "sys",
        "tomllib",
    }
    assert imported <= allowed, f"unexpected import(s): {sorted(imported - allowed)}"


def test_guard_does_not_fetch_or_write_anything():
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("urlopen", "urlretrieve", "urllib", "requests", "subprocess"):
        assert forbidden not in source, f"the guard must not use {forbidden!r}"
    for forbidden in ("write_text", "write_bytes", "open(", "mkdir"):
        assert forbidden not in source, f"the guard must not modify files: {forbidden!r}"


def test_guard_does_not_read_git_or_open_a_connection():
    """The version comes from the files in the tree, never from Git or a network."""
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in (
        "rev-parse",
        "describe",
        "popen",
        ".git/index",
        "refs/heads",
        "connect(",
    ):
        assert forbidden not in source, (
            f"the guard must not substitute {forbidden!r} for the declarations"
        )


DECLARATIONS = (PYPROJECT, INIT, CITATION)


def test_guard_reports_no_drift_when_run_from_the_repository(capsys):
    """Running the guard must not change anything it inspects."""
    before = {name: (ROOT / name).read_bytes() for name in DECLARATIONS}
    assert guard.main(["--root", str(ROOT)]) == 0
    capsys.readouterr()
    after = {name: (ROOT / name).read_bytes() for name in DECLARATIONS}
    assert before == after
