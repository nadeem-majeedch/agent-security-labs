"""Structural guards for the prediction-adjudication challenge.

``labs/PREDICTION-ADJUDICATION-CHALLENGE.md`` is student-facing; its expected
classifications live in the instructor-only
``labs/PREDICTION-ADJUDICATION-CHALLENGE-ANSWER-KEY.md``. This is a
documentation-consistency guard, not a content review. It pins the small set of
things that keep the exercise usable and non-leaking:

* both files exist;
* the student page names the four classification categories it teaches;
* the student page ships a claims table whose classification/evidence columns
  are *unanswered* (no answer leakage);
* the student page does not link to, or name, the answer key;
* the getting-started path points at the challenge; and
* the answer key classifies every claim and stays out of the published nav.

It does not hard-code the individual answers, and it asserts no large block of
prose.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENT = ROOT / "labs" / "PREDICTION-ADJUDICATION-CHALLENGE.md"
ANSWER_KEY = ROOT / "labs" / "PREDICTION-ADJUDICATION-CHALLENGE-ANSWER-KEY.md"
GETTING_STARTED = ROOT / "labs" / "GETTING-STARTED.md"
MKDOCS = ROOT / "mkdocs.yml"

#: The four categories the exercise teaches (matched case-insensitively).
CATEGORIES = ("prediction", "observation", "interpretation", "unsupported")

#: A markdown table row whose first cell is a claim number, e.g. ``| 1 | ... |``.
_NUMBERED_ROW = re.compile(r"^\|\s*\d+\s*\|")

#: The smallest and largest accepted claim counts.
_MIN_CLAIMS = 10
_MAX_CLAIMS = 13


def _rows(text: str) -> list[list[str]]:
    """Return the cells of every numbered table row in ``text``."""
    rows = []
    for line in text.splitlines():
        if _NUMBERED_ROW.match(line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def test_challenge_and_answer_key_files_exist():
    assert STUDENT.is_file(), "labs/PREDICTION-ADJUDICATION-CHALLENGE.md is missing"
    assert ANSWER_KEY.is_file(), (
        "labs/PREDICTION-ADJUDICATION-CHALLENGE-ANSWER-KEY.md is missing"
    )


def test_student_page_names_the_four_categories():
    text = STUDENT.read_text(encoding="utf-8").lower()
    for category in CATEGORIES:
        assert category in text, f"the challenge no longer names {category!r}"


def test_student_claims_table_is_present_and_unanswered():
    rows = _rows(STUDENT.read_text(encoding="utf-8"))
    assert _MIN_CLAIMS <= len(rows) <= _MAX_CLAIMS, (
        f"the challenge should list about {_MIN_CLAIMS}-{_MAX_CLAIMS} claims, "
        f"found {len(rows)}"
    )
    for row in rows:
        assert len(row) == 5, f"claim row should have 5 columns: {row}"
        # Columns 3-5 are Classification / Evidence / Supported? -- they must
        # ship blank, so the answers cannot leak through the student page.
        assert row[2] == "", f"claim {row[0]} leaks its classification: {row[2]!r}"
        assert row[3] == "", f"claim {row[0]} leaks its evidence: {row[3]!r}"
        assert row[4] == "", f"claim {row[0]} leaks a supported verdict: {row[4]!r}"


def test_student_page_does_not_reference_or_link_the_answer_key():
    text = STUDENT.read_text(encoding="utf-8")
    assert "PREDICTION-ADJUDICATION-CHALLENGE-ANSWER-KEY" not in text, (
        "the student page must not link to or name the instructor-only answer key"
    )


def test_getting_started_points_to_the_challenge():
    text = GETTING_STARTED.read_text(encoding="utf-8")
    assert "PREDICTION-ADJUDICATION-CHALLENGE.md" in text, (
        "the getting-started path no longer points at the challenge"
    )


def test_answer_key_classifies_every_claim_and_stays_out_of_nav():
    student_rows = _rows(STUDENT.read_text(encoding="utf-8"))
    key_text = ANSWER_KEY.read_text(encoding="utf-8")
    key_rows = _rows(key_text)
    assert len(key_rows) == len(student_rows), (
        "the answer key should classify exactly the claims on the student page: "
        f"{len(key_rows)} key rows vs {len(student_rows)} claims"
    )
    for row in key_rows:
        assert len(row) >= 3, f"answer-key row should be a table: {row}"
        classification = row[2].lower()
        assert any(category in classification for category in CATEGORIES), (
            f"claim {row[0]} has no recognisable classification: {row[2]!r}"
        )
    assert "instructor-only" in key_text.lower(), (
        "the answer key should be marked instructor-only"
    )
    nav = MKDOCS.read_text(encoding="utf-8")
    assert "PREDICTION-ADJUDICATION-CHALLENGE-ANSWER-KEY.md" not in nav, (
        "the answer key must not appear in the published navigation"
    )
