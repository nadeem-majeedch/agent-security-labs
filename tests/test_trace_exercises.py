"""The trace-reading exercises and their answer key must stay in step.

``labs/TRACE-READING-EXERCISES.md`` is student-facing; its answers live in the
instructor-only ``labs/TRACE-READING-EXERCISES-ANSWER-KEY.md``. This test pins
that every numbered exercise has a matching answer, that the per-lab "what if"
section covers every lab, that the student page links the schema-derived field
reference, and that the predict-a-difference capstone table still matches a real
LAB-04 two-policy comparison. It is a documentation consistency guard, not a
content check.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from agentsec.compare import compare_traces
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = ROOT / "labs" / "TRACE-READING-EXERCISES.md"
ANSWER_KEY = ROOT / "labs" / "TRACE-READING-EXERCISES-ANSWER-KEY.md"
ALLOW_ALL_CONFIG = ROOT / "configs" / "examples" / "lab04_tool_misuse_allow_all.yaml"
LAB04_CONFIG = ROOT / "labs" / "LAB-04-tool-misuse" / "config.yaml"
TS = datetime(2026, 1, 1, tzinfo=timezone.utc)
CAPSTONE_HEADING = "## Predict-a-difference capstone \u2014 expected observations"

_LAB_IDS = [f"LAB-{n:02d}" for n in range(8)]


def _exercise_ids(text: str) -> set[str]:
    return set(re.findall(r"^### ([A-Z]-\d+)", text, flags=re.MULTILINE))


def _answered_ids(text: str) -> set[str]:
    # Answers are bolded, and a few carry a parenthetical label, e.g.
    # ``**E-2 (approval)**``.
    return set(re.findall(r"\*\*([A-Z]-\d+)\b", text))


def _section(text: str, heading: str) -> str:
    """Return the body of the ``##`` section introduced by ``heading``."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            body = []
            for following in lines[index + 1 :]:
                if following.startswith("## "):
                    break
                body.append(following)
            return "\n".join(body)
    assert False, f"the answer key has no `{heading}` section"


def _lab04_capstone_facts(tmp_path: Path) -> dict[str, object]:
    """Run both LAB-04 policies and derive the six capstone comparison facts."""

    def run(config: Path, name: str) -> Path:
        loaded = load_experiment_config(config).model_copy(
            update={"trace_path": tmp_path / name}
        )
        build_mvp_runner(loaded, clock=lambda: TS).run(loaded)
        return tmp_path / name

    result = compare_traces(
        run(ALLOW_ALL_CONFIG, "permissive.jsonl"),
        run(LAB04_CONFIG, "least_privilege.jsonl"),
    )
    distribution = {e["event_type"]: e for e in result["event_type_distribution"]}
    differences = {
        (d["section"], d["key"]): (d["a"], d["b"])
        for d in result["evaluator"]["differences"]
    }
    return {
        "event_count": (result["trace_a"]["event_count"], result["trace_b"]["event_count"]),
        "event_count_delta": result["event_count_delta"],
        "tool_executed": (
            distribution["tool_executed"]["a"],
            distribution["tool_executed"]["b"],
        ),
        "decisions.allow": differences[("decisions", "allow")],
        "decisions.deny": differences[("decisions", "deny")],
        "tool_results.error": differences[("tool_results", "error")],
        "tool_results.denied": differences[("tool_results", "denied")],
    }


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


def test_answer_key_capstone_table_matches_the_lab04_comparison(tmp_path):
    """The instructor capstone table must track the real LAB-04 comparison.

    The table is human-authored; this only pins it to the observed comparison so
    it cannot drift silently when a policy or lab changes. The expected rows are
    built from the derived values, never hard-coded.
    """
    facts = _lab04_capstone_facts(tmp_path)
    section = _section(ANSWER_KEY.read_text(encoding="utf-8"), CAPSTONE_HEADING)

    a_count, b_count = facts["event_count"]
    tool_executed_a, tool_executed_b = facts["tool_executed"]
    expected_rows = [
        f"| Events | {a_count} | {b_count} (delta {facts['event_count_delta']:+d}) |",
        f"| `tool_executed` | {tool_executed_a} | {tool_executed_b} |",
        f"| `decisions.allow` | {facts['decisions.allow'][0]} | {facts['decisions.allow'][1]} |",
        f"| `decisions.deny` | {facts['decisions.deny'][0]} | {facts['decisions.deny'][1]} |",
        f"| `tool_results.error` | {facts['tool_results.error'][0]} | {facts['tool_results.error'][1]} |",
        f"| `tool_results.denied` | {facts['tool_results.denied'][0]} | {facts['tool_results.denied'][1]} |",
    ]
    for row in expected_rows:
        assert row in section, f"capstone table row drifted from the comparison: {row}"
