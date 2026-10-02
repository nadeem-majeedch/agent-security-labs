"""The v0.1.0 release manifest must exist and state the release facts.

``labs/V0.1.0-RELEASE-MANIFEST.md`` is the owner-facing summary of the prepared
release. These tests pin that it exists, that it records the release identity and
readiness, that its warning table matches the accepted policy, that it reserves
commit/push/tag for the owner, and that it is reachable from the MkDocs
navigation. They are a documentation-consistency guard, not a content review.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "labs" / "V0.1.0-RELEASE-MANIFEST.md"
MKDOCS = ROOT / "mkdocs.yml"


def _page_text() -> str:
    assert PAGE.is_file(), "labs/V0.1.0-RELEASE-MANIFEST.md is missing"
    return " ".join(PAGE.read_text(encoding="utf-8").split())


def test_page_exists():
    assert PAGE.is_file(), "labs/V0.1.0-RELEASE-MANIFEST.md is missing"


def test_page_records_the_release_identity():
    page = _page_text()
    assert "0.1.0" in page
    assert "v0.1.0" in page and "v0.0.1" in page
    assert "has not yet been created" in page, (
        "the manifest should state that v0.1.0 does not exist yet"
    )


def test_page_records_the_release_readiness():
    page = _page_text()
    assert "READY WITH WARNINGS" in page
    assert "blockers" in page.lower()
    assert "{W7, W12}" in page
    assert "W6" in page and "CLOSED" in page


def test_page_warning_table_matches_the_accepted_policy():
    page = _page_text()
    assert "ACCEPTED" in page
    assert "RESTATED" in page.upper()
    assert "Keep accepted" in page


def test_page_reserves_commit_push_and_tag_for_the_owner():
    page = _page_text()
    assert "owner actions" in page.lower()
    assert "Create the `v0.1.0` tag" in page
    assert "Push the tag" in page


def test_page_includes_the_pre_tag_result_template():
    page = _page_text()
    assert "v0.1.0 RELEASE REVIEW" in page
    assert "Release approved: YES / NO" in page


def test_page_documents_the_executable_manifest_drift_check():
    page = _page_text()
    assert "check_release_manifest.py" in page, (
        "the page should document the executable manifest drift check"
    )
    assert "read-only" in page.lower(), "the page should state the check is read-only"
    assert "check_warning_drift.py" in page, (
        "the page should note it complements the warning drift check"
    )


def test_page_references_the_executable_owner_pre_tag_validation():
    page = _page_text()
    assert "pre_tag_check.py" in page, (
        "the page should reference the executable owner pre-tag validation"
    )
    assert "read-only" in page.lower(), (
        "the page should state the pre-tag validation is read-only"
    )
    assert "ready for owner review" in page.lower(), (
        "the page should state a successful run is ready for owner review"
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
    assert "V0.1.0-RELEASE-MANIFEST.md" in paths, (
        "the release manifest page is not in the MkDocs navigation"
    )
