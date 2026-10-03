"""The root README's verification table must match the repository it describes.

``README.md`` carries a "Verification status" table that a reader is told was
re-run "at this revision". Its test-suite row once hard-coded a count that
silently drifted as the suite grew, so a reader could not trust the table. This
guard derives the current collected-test count **from the suite itself** — by
collecting the tests with ``pytest --collect-only`` in a child process, which
enumerates the suite without running it — and asserts the README states exactly
that number. It also pins the README-maintenance note in ``docs/development.md``,
which previously described the README as "intentionally left untouched" long
after the README had become a maintained, release-facing document.

This is a documentation-consistency guard, not a content review. The count is
derived, never copied into a second constant, so the only place a stale number
can live is the README itself, and it fails loudly when it drifts.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEVELOPMENT = ROOT / "docs" / "development.md"

#: The test-suite row of the README verification table. Kept tolerant of the
#: surrounding Markdown so only the number has to be maintained.
README_TEST_ROW = re.compile(
    r"\|\s*Test suite\s*\|[^|\n]*\|\s*\*\*(?P<count>\d+)\s+tests?\s+pass\*\*[^|\n]*"
)

#: ``pytest --collect-only`` prints one summary line like
#: ``1081 tests collected in 0.43s``; parse the count out of it.
COLLECTED = re.compile(r"(?P<count>\d+)\s+tests?\s+collected")


def _collected_test_count() -> int:
    """Return the number of tests the suite collects, derived from pytest.

    This runs *collection only* (``--collect-only``) in a child process, so the
    suite is enumerated but never executed here; there is no recursive run. The
    repository's own pytest configuration supplies ``testpaths``/``pythonpath``,
    and ``-o addopts=`` neutralises the configured quiet flag so the summary line
    is always emitted.
    """
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-o",
            "addopts=",
            "-p",
            "no:cacheprovider",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    match = COLLECTED.search(completed.stdout)
    assert match is not None, "pytest did not report a collected-test count:\n" + completed.stdout[
        -2000:
    ]
    return int(match.group("count"))


def test_readme_states_the_current_collected_test_count():
    match = README_TEST_ROW.search(README.read_text(encoding="utf-8"))
    assert match is not None, (
        "README.md has no 'Test suite ... **N tests pass**' row in its "
        "verification table"
    )
    documented = int(match.group("count"))
    collected = _collected_test_count()
    assert documented == collected, (
        f"README.md advertises {documented} tests but the suite collects "
        f"{collected}; update the README verification table to {collected}"
    )


def test_readme_row_reports_a_passing_suite():
    match = README_TEST_ROW.search(README.read_text(encoding="utf-8"))
    assert match is not None
    # The row must still claim a passing suite, not merely a count.
    assert "exit 0" in match.group(0), (
        "the README test-suite row should record the passing exit status"
    )


def test_development_note_describes_the_maintained_readme():
    text = DEVELOPMENT.read_text(encoding="utf-8")
    assert "intentionally left untouched" not in text, (
        "docs/development.md still calls the root README intentionally untouched"
    )
    assert "tests/test_readme.py" in text, (
        "docs/development.md should point at the README consistency guard"
    )
