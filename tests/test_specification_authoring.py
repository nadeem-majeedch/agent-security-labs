"""Structural guards for the specification-authoring challenge.

``labs/SPECIFICATION-AUTHORING-CHALLENGE.md`` is student-facing; the reference
specification and expected values live in the instructor-only
``labs/SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md``. This is a
documentation-consistency guard, not a content review. It pins the small set of
things that keep the challenge usable and non-leaking:

* both files exist;
* the student page names the four ``ExperimentResult`` states it must distinguish
  from a design error;
* the student page documents the ``agentsec experiment`` command and the required
  specification fields;
* the student page links the controlled-experiments module and the LAB-05 page,
  both of which must exist;
* the student page keeps the design-error / result boundary and does not leak the
  answer key;
* the student page is in the published navigation;
* the getting-started path points at the challenge; and
* the answer key is instructor-only and stays out of the published nav.

It does not hard-code the individual answers, and it asserts no large block of
prose.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENT = ROOT / "labs" / "SPECIFICATION-AUTHORING-CHALLENGE.md"
ANSWER_KEY = ROOT / "labs" / "SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md"
GETTING_STARTED = ROOT / "labs" / "GETTING-STARTED.md"
MKDOCS = ROOT / "mkdocs.yml"

#: The four result states the challenge must keep distinct from a design error.
STATES = (
    "changes_observed",
    "changes_not_observed",
    "invariant_violated",
    "execution_failed",
)

#: The command the challenge must document, in repository convention.
EXPERIMENT_COMMAND = "agentsec experiment"

#: The required specification fields the challenge must name.
SPEC_FIELDS = (
    "base_config",
    "intervention",
    "expected_changes",
    "expected_invariants",
    "alternative_explanations",
)

#: In-docs links the student page must carry, which must exist.
MODULE_LINK = "CONTROLLED-EXPERIMENTS.md"
LAB05_LINK = "LAB-05-require-approval/README.md"


def _student() -> str:
    return STUDENT.read_text(encoding="utf-8")


def test_challenge_and_answer_key_files_exist():
    assert STUDENT.is_file(), "labs/SPECIFICATION-AUTHORING-CHALLENGE.md is missing"
    assert ANSWER_KEY.is_file(), (
        "labs/SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md is missing"
    )


def test_student_page_names_the_four_states():
    text = _student()
    for state in STATES:
        assert state in text, f"the challenge no longer names the state {state!r}"


def test_student_page_documents_the_experiment_command():
    assert EXPERIMENT_COMMAND in _student(), (
        "the challenge no longer documents the `agentsec experiment` command"
    )


def test_student_page_names_the_required_specification_fields():
    text = _student()
    for field in SPEC_FIELDS:
        assert field in text, (
            f"the challenge no longer names the required field {field!r}"
        )


def test_student_page_keeps_the_design_error_boundary():
    lowered = _student().lower()
    assert "design error" in lowered, (
        "the challenge no longer distinguishes a design error from a result state"
    )
    assert "exit" in lowered, (
        "the challenge no longer explains the exit-code semantics"
    )


def test_student_page_links_the_module_and_the_lab05_page():
    text = _student()
    for link in (MODULE_LINK, LAB05_LINK):
        assert link in text, f"the challenge no longer links `{link}`"
        assert (STUDENT.parent / link).is_file(), (
            f"the challenge links to `{link}`, which does not exist"
        )


def test_student_page_does_not_reference_the_answer_key():
    assert "SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY" not in _student(), (
        "the student page must not link to or name the instructor-only answer key"
    )


def test_student_page_is_in_the_published_navigation():
    nav = MKDOCS.read_text(encoding="utf-8")
    assert "SPECIFICATION-AUTHORING-CHALLENGE.md" in nav, (
        "the specification-authoring challenge is no longer in the MkDocs "
        "navigation"
    )


def test_getting_started_points_to_the_challenge():
    text = GETTING_STARTED.read_text(encoding="utf-8")
    assert "SPECIFICATION-AUTHORING-CHALLENGE.md" in text, (
        "the getting-started path no longer points at the authoring challenge"
    )


def test_answer_key_is_instructor_only_and_stays_out_of_nav():
    text = ANSWER_KEY.read_text(encoding="utf-8")
    assert "instructor-only" in text.lower(), (
        "the answer key should be marked instructor-only"
    )
    nav = MKDOCS.read_text(encoding="utf-8")
    assert "SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md" not in nav, (
        "the answer key must not appear in the published navigation"
    )
