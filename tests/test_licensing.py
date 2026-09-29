"""Tests for the licence metadata guard in ``scripts/check_licensing.py``.

The guard is a small consistency check, so these tests pin its contract from
both directions: the real repository must satisfy it, and each individual
declaration must be able to fail on its own. The failure cases run against
minimal fixtures in ``tmp_path``, never against the checked-in files.

The second half covers the coverage manifest. A fixture repository plus one
new file must fail; the same file must pass once ``licensing/manifest.toml``
records it; and a file must never be classified by its extension.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_licensing.py"


def _load_guard():
    """Import ``scripts/check_licensing.py``, which is not an installed module."""
    spec = importlib.util.spec_from_file_location("check_licensing", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # Register before executing: ``@dataclass`` looks the module up in sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


# --------------------------------------------------------------------------
# Fixtures: a minimal repository that satisfies the contract.
# --------------------------------------------------------------------------

MIT_TEXT = (
    "MIT License\n"
    "\n"
    "Copyright (c) 2026 Example Author\n"
    "\n"
    "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
    "of this software and associated documentation files (the \"Software\"), to deal\n"
    "in the Software without restriction.\n"
    "\n"
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.\n'
)

CCBY_TEXT = (
    "Content licence: CC BY 4.0\n"
    "\n"
    "Third-party material is not covered by this grant.\n"
    "Quotations remain the property of their respective owners.\n"
    "\n"
    "creativecommons.org/licenses/by/4.0\n"
    "\n"
    "Creative Commons Attribution 4.0 International Public License\n"
    "\n"
    + "".join(
        f"Section {number} -- Placeholder.\n" for number in range(1, 9)
    )
)

README_TEXT = (
    "# Example\n"
    "\n"
    "## Licensing\n"
    "\n"
    "| Material | Licence | File |\n"
    "| --- | --- | --- |\n"
    "| Software | MIT | LICENSE |\n"
    "| Documentation | CC BY 4.0 | LICENSE-DATA |\n"
    "\n"
    "Third-party material remains the property of their respective owners.\n"
)

PYPROJECT_TEXT = (
    "[project]\n"
    'name = "example"\n'
    'version = "0.0.1"\n'
    'license = { text = "MIT" }\n'
)

CITATION_TEXT = (
    "cff-version: 1.2.0\n"
    'title: "Example"\n'
    "type: software\n"
    "license: MIT\n"
)

FILES = {
    "LICENSE": MIT_TEXT,
    "LICENSE-DATA": CCBY_TEXT,
    "README.md": README_TEXT,
    "pyproject.toml": PYPROJECT_TEXT,
    "CITATION.cff": CITATION_TEXT,
}

MANIFEST = "licensing/manifest.toml"
LOCAL_STATE = ".freebuff/project-id"

# The fixture manifest is built from named blocks so a test can vary exactly
# one decision without restating the whole file.
MIT_ENTRY = (
    "[[coverage]]\n"
    'status = "mit"\n'
    'paths = ["LICENSE", "CITATION.cff", "pyproject.toml", "licensing/**"]\n'
)
CCBY_ENTRY = '[[coverage]]\nstatus = "cc-by"\npaths = ["README.md"]\n'
EXCLUDED_ENTRY = (
    "[[coverage]]\n"
    'status = "excluded"\n'
    'reason = "fixture: governed by neither grant"\n'
    'paths = ["LICENSE-DATA", ".freebuff/project-id"]\n'
)
IGNORED_ENTRY = (
    "[[coverage]]\n"
    'status = "not-distributed"\n'
    'paths = ["runs/", "traces/*.jsonl", "**/__pycache__/"]\n'
)
UNLICENSED_WITHOUT_REASON = (
    '[[coverage]]\nstatus = "unlicensed"\npaths = ["notes/scratch.txt"]\n'
)
UNLICENSED_WITH_REASON = (
    "[[coverage]]\n"
    'status = "unlicensed"\n'
    'reason = "fixture: decision deliberately deferred"\n'
    'paths = ["notes/scratch.txt"]\n'
)

MANIFEST_TEXT = "\n".join(
    [
        "schema-version = 1",
        MIT_ENTRY,
        CCBY_ENTRY,
        EXCLUDED_ENTRY,
        IGNORED_ENTRY,
    ]
)

#: The seven files a fixture repository contains.
FIXTURE_FILE_COUNT = 7


def write_manifest(root: Path, text: str) -> None:
    (root / MANIFEST).write_text(text, encoding="utf-8")


def make_repo(root: Path, **overrides) -> Path:
    """Write a minimal repository that satisfies the whole contract.

    An override value of ``None`` omits that file; any other value replaces
    its contents. The coverage manifest and the tracked local-state file are
    written too, because the contract includes the coverage check.
    """
    contents = dict(FILES)
    contents[MANIFEST] = MANIFEST_TEXT
    contents.update(overrides)
    for name, text in contents.items():
        if text is None:
            continue
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    local = root / LOCAL_STATE
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text("fixture\n", encoding="utf-8")
    return root


def add_file(root: Path, name: str, text: str = "x\n") -> Path:
    """Create one more file, the way a contributor would."""
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def results_for(root: Path) -> dict[str, object]:
    return {result.name: result for result in guard.run_checks(root)}


def failures_for(root: Path) -> list[str]:
    return [result.name for result in guard.run_checks(root) if not result.ok]


# --------------------------------------------------------------------------
# The contract holds for the real repository.
# --------------------------------------------------------------------------


def test_current_repository_satisfies_the_licence_contract():
    results = guard.run_checks(ROOT)
    assert [r.name for r in results] == [
        "LICENSE",
        "pyproject.toml",
        "CITATION.cff",
        "LICENSE-DATA",
        "README.md",
        "third-party exclusion",
        "manifest",
        "licence coverage",
        "unlicensed files",
    ], "the report order is part of the CI output"
    assert [(r.name, r.detail) for r in results if not r.ok] == []


def test_guard_reports_every_check_passing(capsys):
    assert guard.main(["--root", str(ROOT)]) == 0
    out = capsys.readouterr().out
    assert "9/9 checks passed" in out
    assert "FAIL" not in out


# --------------------------------------------------------------------------
# Valid fixtures pass; each declaration can fail independently.
# --------------------------------------------------------------------------


def test_valid_fixture_passes(tmp_path):
    make_repo(tmp_path)
    assert failures_for(tmp_path) == []


@pytest.mark.parametrize(
    "name, replacement, expected",
    [
        ("LICENSE", None, "LICENSE"),
        ("LICENSE", "Apache License\nVersion 2.0\n", "LICENSE"),
        ("LICENSE", CCBY_TEXT, "LICENSE"),
        ("LICENSE-DATA", None, "LICENSE-DATA"),
        ("LICENSE-DATA", "MIT only, no content licence here.\n", "LICENSE-DATA"),
        ("CITATION.cff", None, "CITATION.cff"),
        ("CITATION.cff", "cff-version: 1.2.0\nlicense: Apache-2.0\n", "CITATION.cff"),
        ("README.md", None, "README.md"),
    ],
)
def test_single_file_failure_is_detected(tmp_path, name, replacement, expected):
    make_repo(tmp_path, **{name: replacement})
    failures = failures_for(tmp_path)
    assert expected in failures


def test_license_must_not_hold_the_content_licence(tmp_path):
    make_repo(tmp_path, **{"LICENSE": CCBY_TEXT, "LICENSE-DATA": CCBY_TEXT})
    detail = results_for(tmp_path)["LICENSE"].detail
    assert "CC BY 4.0" in detail


def test_pyproject_rejects_a_different_software_licence(tmp_path):
    make_repo(
        tmp_path,
        **{"pyproject.toml": '[project]\nname = "example"\nlicense = "Apache-2.0"\n'},
    )
    assert "pyproject.toml" in failures_for(tmp_path)


@pytest.mark.parametrize(
    "declaration",
    [
        'license = "MIT"\n',
        'license = { text = "MIT" }\n',
        'license = { file = "LICENSE" }\n',
    ],
)
def test_pyproject_accepts_mit_in_its_supported_spellings(tmp_path, declaration):
    make_repo(
        tmp_path,
        **{"pyproject.toml": '[project]\nname = "example"\n' + declaration},
    )
    assert "pyproject.toml" not in failures_for(tmp_path)


def test_truncated_legal_code_is_detected(tmp_path):
    truncated = CCBY_TEXT.replace("Section 8 -- Placeholder.\n", "")
    make_repo(tmp_path, **{"LICENSE-DATA": truncated})
    detail = results_for(tmp_path)["LICENSE-DATA"].detail
    assert "truncated" in detail


def test_readme_must_name_both_licences(tmp_path):
    make_repo(
        tmp_path,
        **{
            "README.md": (
                "# Example\n\n## Licensing\n\nSoftware is MIT, see LICENSE.\n"
                "Third-party material stays with its respective owners.\n"
            )
        },
    )
    assert "README.md" in failures_for(tmp_path)


def test_readme_must_have_a_licensing_section(tmp_path):
    make_repo(
        tmp_path,
        **{
            "README.md": (
                "# Example\n\nMIT and CC BY 4.0 are documented in LICENSE and "
                "LICENSE-DATA.\nThird-party material stays with its respective "
                "owners.\n"
            )
        },
    )
    detail = results_for(tmp_path)["README.md"].detail
    assert "Licensing" in detail


def test_third_party_exclusion_is_required_in_both_files(tmp_path):
    make_repo(
        tmp_path,
        **{
            "README.md": (
                "# Example\n\n## Licensing\n\nMIT in LICENSE, CC BY 4.0 in "
                "LICENSE-DATA.\n"
            )
        },
    )
    failures = failures_for(tmp_path)
    assert "third-party exclusion" in failures


def test_failing_run_explains_itself_and_exits_nonzero(tmp_path, capsys):
    make_repo(tmp_path, **{"LICENSE-DATA": None})
    assert guard.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "LICENSE-DATA" in out
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
        "dataclasses",
        "pathlib",
        "re",
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


def test_guard_does_not_read_git_internals():
    """Coverage comes from the manifest, not from what Git happens to record."""
    source = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("ls-files", "popen", ".git/index", "refs/heads"):
        assert forbidden not in source, (
            f"the guard must not substitute {forbidden!r} for the manifest"
        )


def test_the_walk_skips_git_and_not_distributed_paths(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, ".git/HEAD", "ref: refs/heads/main\n")
    add_file(tmp_path, "runs/trace.jsonl", "{}\n")
    add_file(tmp_path, "runs/nested/deep.json", "{}\n")
    walked = guard.walk_repository(tmp_path, ("runs/",))
    assert ".git/HEAD" not in walked
    assert not any(path.startswith("runs/") for path in walked)


DECLARATIONS = (
    "LICENSE",
    "LICENSE-DATA",
    "README.md",
    "pyproject.toml",
    "CITATION.cff",
    MANIFEST,
)


def test_guard_reports_no_drift_when_run_from_the_repository(capsys):
    """Running the guard must not change anything it inspects."""
    before = {name: (ROOT / name).read_text(encoding="utf-8") for name in DECLARATIONS}
    assert guard.main(["--root", str(ROOT)]) == 0
    capsys.readouterr()
    after = {name: (ROOT / name).read_text(encoding="utf-8") for name in DECLARATIONS}
    assert before == after


# --------------------------------------------------------------------------
# Coverage: a file cannot exist without a recorded licensing treatment.
# --------------------------------------------------------------------------


def test_the_real_manifest_accounts_for_every_file():
    """The coverage contract holds for the repository as it stands."""
    manifest = guard.load_manifest(ROOT)
    report = guard.evaluate_coverage(ROOT, manifest)
    assert report.unaccounted == []
    assert report.conflicts == []
    assert report.stale == []
    assert report.undecided == []
    assert report.files > 0
    assert sum(report.counts.values()) == report.files


def test_the_fixture_manifest_accounts_for_every_file(tmp_path):
    make_repo(tmp_path)
    report = guard.evaluate_coverage(tmp_path, guard.load_manifest(tmp_path))
    assert report.unaccounted == []
    assert report.stale == []
    assert report.files == FIXTURE_FILE_COUNT
    assert report.counts == {"mit": 4, "cc-by": 1, "excluded": 2, "unlicensed": 0}


def test_coverage_manifest_is_required(tmp_path):
    make_repo(tmp_path, **{MANIFEST: None})
    failures = failures_for(tmp_path)
    assert "manifest" in failures
    assert "licence coverage" in failures


def test_a_new_unaccounted_file_fails_the_check(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, "notes/idea.md", "# Idea\n")
    results = results_for(tmp_path)
    assert not results["licence coverage"].ok
    assert "notes/idea.md" in results["licence coverage"].detail
    assert "no recorded licensing treatment" in results["licence coverage"].detail


def test_the_new_file_passes_once_the_manifest_records_it(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, "notes/idea.md", "# Idea\n")
    assert "notes/idea.md" in results_for(tmp_path)["licence coverage"].detail
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + '\n[[coverage]]\nstatus = "cc-by"\npaths = ["notes/**.md"]\n',
    )
    assert failures_for(tmp_path) == []


def test_a_new_file_is_not_licensed_by_its_extension(tmp_path):
    """A Markdown file the manifest does not name is unaccounted for, not CC BY."""
    make_repo(tmp_path)
    add_file(tmp_path, "ROADMAP.md", "# Roadmap\n")
    assert "ROADMAP.md" in results_for(tmp_path)["licence coverage"].detail


def test_an_explicitly_excluded_file_passes(tmp_path):
    make_repo(tmp_path)
    assert (tmp_path / LOCAL_STATE).is_file()
    assert failures_for(tmp_path) == []


def test_a_file_outside_both_grants_must_be_recorded(tmp_path):
    """Removing the exclusion decision makes the file unaccounted for."""
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        "\n".join(["schema-version = 1", MIT_ENTRY, CCBY_ENTRY, IGNORED_ENTRY]),
    )
    detail = results_for(tmp_path)["licence coverage"].detail
    assert LOCAL_STATE in detail
    assert "LICENSE-DATA" in detail


def test_not_distributed_paths_are_not_reviewed(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, "runs/trace.jsonl", "{}\n")
    add_file(tmp_path, "runs/nested/deep.json", "{}\n")
    assert failures_for(tmp_path) == []
    assert results_for(tmp_path)["licence coverage"].detail.startswith(
        f"{FIXTURE_FILE_COUNT} file(s) accounted for"
    )


def test_an_unlicensed_file_without_a_reason_is_rejected(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, "notes/scratch.txt", "scratch\n")
    write_manifest(tmp_path, MANIFEST_TEXT + "\n" + UNLICENSED_WITHOUT_REASON)
    results = results_for(tmp_path)
    assert "manifest" in failures_for(tmp_path)
    assert "reason" in results["manifest"].detail
    assert "not evaluated" in results["licence coverage"].detail


def test_a_recorded_unlicensed_file_passes_and_is_reported(tmp_path):
    make_repo(tmp_path)
    add_file(tmp_path, "notes/scratch.txt", "scratch\n")
    write_manifest(tmp_path, MANIFEST_TEXT + "\n" + UNLICENSED_WITH_REASON)
    results = results_for(tmp_path)
    assert failures_for(tmp_path) == []
    assert "notes/scratch.txt" in results["unlicensed files"].detail
    assert "deliberately" in results["unlicensed files"].detail


def test_a_path_cannot_be_claimed_by_two_categories(tmp_path):
    """Overlap the static duplicate check cannot see is caught per file."""
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + '\n[[coverage]]\nstatus = "mit"\npaths = ["*.md"]\n',
    )
    results = results_for(tmp_path)
    assert not results["licence coverage"].ok
    assert "more than one category" in results["licence coverage"].detail
    assert "README.md" in results["licence coverage"].detail


def test_an_identical_pattern_under_two_statuses_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + '\n[[coverage]]\nstatus = "mit"\npaths = ["README.md"]\n',
    )
    detail = results_for(tmp_path)["manifest"].detail
    assert "more than one status" in detail
    assert "README.md" in detail


def test_a_pattern_that_matches_nothing_is_reported(tmp_path):
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + '\n[[coverage]]\nstatus = "cc-by"\npaths = ["docs/**.md"]\n',
    )
    results = results_for(tmp_path)
    assert not results["licence coverage"].ok
    assert "docs/**.md" in results["licence coverage"].detail
    assert "match no file" in results["licence coverage"].detail


def test_an_unknown_status_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + '\n[[coverage]]\nstatus = "sort-of-mit"\npaths = ["README.md"]\n',
    )
    assert "sort-of-mit" in results_for(tmp_path)["manifest"].detail


def test_an_unsupported_schema_version_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(tmp_path, MANIFEST_TEXT.replace("schema-version = 1", "schema-version = 2"))
    assert "schema-version" in results_for(tmp_path)["manifest"].detail


def test_a_manifest_with_no_entries_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(tmp_path, "schema-version = 1\n")
    assert "no [[coverage]] entries" in results_for(tmp_path)["manifest"].detail


def test_a_manifest_that_is_not_toml_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(tmp_path, "schema-version = 1\n[[coverage]\n")
    assert "not valid TOML" in results_for(tmp_path)["manifest"].detail


@pytest.mark.parametrize(
    "declared",
    [
        '"/etc/passwd"',
        '"   "',
        '"../outside.md"',
        # A TOML literal string, so the backslash reaches the guard unchanged.
        "'licensing\\manifest.toml'",
        '"./README.md"',
        '"docs//development.md"',
    ],
)
def test_unusable_patterns_are_rejected(tmp_path, declared):
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        MANIFEST_TEXT + f'\n[[coverage]]\nstatus = "cc-by"\npaths = [{declared}]\n',
    )
    assert "pattern" in results_for(tmp_path)["manifest"].detail


def test_an_empty_path_list_is_rejected(tmp_path):
    make_repo(tmp_path)
    write_manifest(tmp_path, MANIFEST_TEXT + '\n[[coverage]]\nstatus = "mit"\npaths = []\n')
    assert "non-empty list" in results_for(tmp_path)["manifest"].detail


def test_an_excluded_entry_must_say_why(tmp_path):
    make_repo(tmp_path)
    write_manifest(
        tmp_path,
        "\n".join(["schema-version = 1", MIT_ENTRY, CCBY_ENTRY, IGNORED_ENTRY])
        + '\n[[coverage]]\nstatus = "excluded"\npaths = ["LICENSE-DATA"]\n',
    )
    detail = results_for(tmp_path)["manifest"].detail
    assert "reason" in detail
    assert "excluded" in detail


@pytest.mark.parametrize(
    "pattern, path, expected",
    [
        ("README.md", "README.md", True),
        ("README.md", "docs/README.md", False),
        ("labs/*.md", "labs/README.md", True),
        ("labs/*.md", "labs/LAB-01/README.md", False),
        ("labs/**.md", "labs/README.md", True),
        ("labs/**.md", "labs/LAB-01/README.md", True),
        ("src/**", "src/agentsec/agent.py", True),
        ("src/**", "tests/test_licensing.py", False),
        ("runs/", "runs", True),
        ("runs/", "runs/trace.jsonl", True),
        ("runs/", "runs/nested/deep.json", True),
        ("runs/", "runner/x.json", False),
        ("**/__pycache__/", "src/agentsec/__pycache__/agent.pyc", True),
        ("**/__pycache__/", "src/agentsec/agent.py", False),
        ("LIC*", "LICENSE", True),
        ("LIC*", "licensing/manifest.toml", False),
    ],
)
def test_pattern_semantics(pattern, path, expected):
    assert guard.path_is_covered(pattern, path) is expected


def test_a_failing_coverage_run_explains_itself_and_exits_nonzero(tmp_path, capsys):
    make_repo(tmp_path)
    add_file(tmp_path, "notes/idea.md", "# Idea\n")
    assert guard.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "licence coverage" in out
    assert "notes/idea.md" in out
    assert "licensing/manifest.toml" in out
