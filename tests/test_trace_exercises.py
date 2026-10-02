"""The trace-reading exercises and their answer key must stay in step.

``labs/TRACE-READING-EXERCISES.md`` is student-facing; its answers live in the
instructor-only ``labs/TRACE-READING-EXERCISES-ANSWER-KEY.md``. This test pins
that every numbered exercise has a matching answer, that the per-lab "what if"
section covers every lab, and that the student page links the schema-derived
field reference. It is a documentation consistency guard, not a content check.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = ROOT / "labs" / "TRACE-READING-EXERCISES.md"
ANSWER_KEY = ROOT / "labs" / "TRACE-READING-EXERCISES-ANSWER-KEY.md"

_LAB_IDS = [f"LAB-{n:02d}" for n in range(8)]


def _exercise_ids(text: str) -> set[str]:
    return set(re.findall(r"^### ([A-Z]-\d+)", text, flags=re.MULTILINE))


def _answered_ids(text: str) -> set[str]:
    # Answers are bolded, and a few carry a parenthetical label, e.g.
    # ``**E-2 (approval)**``.
    return set(re.findall(r"\*\*([A-Z]-\d+)\b", text))


def test_every_exercise_has_a_matching_answer():
    exercises = _exercise_ids(EXERCISES.read_text(encoding="utf-8"))
    answers = _answered_ids(ANSWER_KEY.read_text(encoding="utf-8"))
    assert exercises, "no numbered exercises found"
    assert exercises <= answers, f"exercises with no answer: {sorted(exercises - answers)}"


def test_answer_key_only_answers_real_exercises():
    exercises = _exercise_ids(EXERCISES.read_text(encoding="utf-8"))
    answers = _answered_ids(ANSWER_KEY.read_text(encoding="utf-8"))
    assert answers <= exercises, f"answers for missing exercises: {sorted(answers - exercises)}"


def test_per_lab_what_if_section_covers_every_lab():
    exercises = EXERCISES.read_text(encoding="utf-8")
    answers = ANSWER_KEY.read_text(encoding="utf-8")
    for lab in _LAB_IDS:
        assert lab in exercises, f"{lab} missing from the per-lab what-if section"
        assert lab in answers, f"{lab} missing from the per-lab answer section"


def test_student_page_links_the_field_reference():
    exercises = EXERCISES.read_text(encoding="utf-8")
    assert "TRACE-FIELD-REFERENCE.md" in exercises, (
        "the exercises should point students at the trace field reference"
    )
