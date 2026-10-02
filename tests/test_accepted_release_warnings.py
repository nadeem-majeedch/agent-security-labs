"""The accepted-release-warnings page must exist and state the policy.

``labs/ACCEPTED-RELEASE-WARNINGS.md`` records the warnings that are deliberately
accepted for the v0.1.0 release. These tests pin that the page exists, that it
documents both accepted warnings (W7, W12), that it identifies W6 as **closed**
rather than active, that it records the controlled retirement procedure, and that
it is reachable from the MkDocs navigation. They are a documentation-consistency
guard, not a content review.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "labs" / "ACCEPTED-RELEASE-WARNINGS.md"
MKDOCS = ROOT / "mkdocs.yml"


def _page_text() -> str:
    assert PAGE.is_file(), "labs/ACCEPTED-RELEASE-WARNINGS.md is missing"
    return PAGE.read_text(encoding="utf-8")


def test_page_exists():
    assert PAGE.is_file(), "labs/ACCEPTED-RELEASE-WARNINGS.md is missing"


def test_page_documents_the_accepted_warnings_w7_and_w12():
    page = _page_text()
    assert "W7" in page, "W7 should be documented as an accepted warning"
    assert "W12" in page, "W12 should be documented as an accepted warning"
    assert "{W7, W12}" in page, "the accepted set should be stated as exactly {W7, W12}"


def test_page_marks_w6_as_closed():
    page = _page_text()
    assert "W6" in page, "the page should mention the closed W6 warning"
    assert "CLOSED" in page, "W6 should be explicitly identified as CLOSED"
    assert "date-released: 2026-10-01" in page, (
        "the page should record why W6 closed (CITATION.cff date-released)"
    )


def test_page_documents_the_retirement_procedure():
    page = " ".join(_page_text().split())
    assert "How to Retire an Accepted Warning" in page, (
        "the page should document the controlled retirement procedure"
    )
    assert "Do not retire warnings by" in page, (
        "the page should list prohibited retirement shortcuts"
    )


def test_page_states_retiring_is_not_deleting_from_the_set():
    page = " ".join(_page_text().split())
    assert "the same as deleting it from the accepted set" in page, (
        "the page should distinguish retiring a warning from deleting it"
    )
    assert "release_check.py --json" in page, (
        "the procedure should point at the release check that proves retirement"
    )


def test_page_documents_the_executable_drift_check():
    page = " ".join(_page_text().split())
    assert "Executable drift check" in page, (
        "the page should document the executable drift check"
    )
    assert "scripts/check_warning_drift.py" in page, (
        "the page should name the drift-check script"
    )
    assert "read-only" in page, "the page should state the check is read-only"


def test_page_documents_the_owner_pre_tag_checklist():
    page = " ".join(_page_text().split())
    assert "Owner pre-tag checklist for v0.1.0" in page, (
        "the page should carry the owner pre-tag checklist"
    )


def test_owner_checklist_lists_the_release_commands():
    page = " ".join(_page_text().split())
    for command in (
        "python scripts/check_version.py",
        "python -m pytest",
        "python -m agentsec labs check",
        "ruff check src tests scripts",
        "python -m mypy",
        "python -m mkdocs build --strict",
        "python scripts/check_licensing.py",
        "python scripts/release_check.py --json",
        "python scripts/check_warning_drift.py",
        "git diff --check",
        "git tag",
    ):
        assert command in page, f"the checklist should include {command!r}"


def test_owner_checklist_states_the_expected_warning_set_and_blockers():
    page = " ".join(_page_text().split())
    assert "{W7, W12}" in page
    assert "Blockers:" in page
    assert "READY WITH WARNINGS" in page
    assert "expected" in page, (
        "the checklist should say READY WITH WARNINGS is the expected result"
    )


def test_owner_checklist_reserves_tagging_for_the_owner():
    page = " ".join(_page_text().split())
    assert "Owner approval" in page, "the checklist should end with an owner decision"
    assert "must **not** commit, push, create the `v0.1.0` tag" in page, (
        "the checklist must forbid the agent from committing, pushing or tagging"
    )


def test_page_is_listed_in_the_mkdocs_navigation():
    config = yaml.safe_load(MKDOCS.read_text(encoding="utf-8"))
    paths: set[str] = set()

    def collect(node):
        if isinstance(node, dict):
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
        elif isinstance(node, str):
            paths.add(node)

    collect(config.get("nav"))
    assert "ACCEPTED-RELEASE-WARNINGS.md" in paths, (
        "the accepted-release-warnings page is not in the MkDocs navigation"
    )
