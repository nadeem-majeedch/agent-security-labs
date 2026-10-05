"""Structural guards for the controlled-experiments learning module.

``labs/CONTROLLED-EXPERIMENTS.md`` is student-facing; the expected answers live in
the instructor-only ``labs/CONTROLLED-EXPERIMENTS-ANSWER-KEY.md``. This is a
documentation-consistency guard, not a content review. It pins the small set of
things that keep the module usable and non-leaking:

* both files exist;
* the student page names the four ``ExperimentResult`` states it teaches;
* the student page documents the exact ``agentsec experiment`` commands (plain
  and ``--json``) and the specification it runs, which must exist;
* the student page keeps the observation/claim boundary and does not leak the
  answer key;
* the student page is in the published navigation;
* the getting-started path points at the module; and
* the answer key is marked instructor-only, names every state, and stays out of
  the published nav.

It does not hard-code the individual answers, and it asserts no large block of
prose.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENT = ROOT / "labs" / "CONTROLLED-EXPERIMENTS.md"
ANSWER_KEY = ROOT / "labs" / "CONTROLLED-EXPERIMENTS-ANSWER-KEY.md"
GETTING_STARTED = ROOT / "labs" / "GETTING-STARTED.md"
MKDOCS = ROOT / "mkdocs.yml"

#: The four result states the module teaches.
STATES = (
    "changes_observed",
    "changes_not_observed",
    "invariant_violated",
    "execution_failed",
)

#: The exact commands the student page must document, in repository convention.
EXPERIMENT_COMMAND = (
    "PYTHONPATH=src py -m agentsec experiment "
    "configs/experiments/lab04-policy-intervention.yaml"
)
EXPERIMENT_JSON_COMMAND = EXPERIMENT_COMMAND + " --json"

#: The specification the module runs, which must exist in the repository.
SPEC = "configs/experiments/lab04-policy-intervention.yaml"

#: The lab page the worked example is built from, which must exist.
LAB04_LINK = "LAB-04-tool-misuse/README.md"


def _student() -> str:
    return STUDENT.read_text(encoding="utf-8")


def _worked_example_block() -> str:
    """The fenced human-output example under §11's "### The result"."""
    text = _student()
    anchor = text.index("### The result")
    start = text.index("```text\n", anchor) + len("```text\n")
    end = text.index("\n```", start)
    return text[start:end]


def test_module_and_answer_key_files_exist():
    assert STUDENT.is_file(), "labs/CONTROLLED-EXPERIMENTS.md is missing"
    assert ANSWER_KEY.is_file(), "labs/CONTROLLED-EXPERIMENTS-ANSWER-KEY.md is missing"


def test_student_page_names_the_four_states():
    text = _student()
    for state in STATES:
        assert state in text, f"the module no longer names the state {state!r}"


def test_student_page_documents_the_experiment_commands():
    text = _student()
    assert EXPERIMENT_COMMAND in text, (
        "the module no longer documents the plain `agentsec experiment` command"
    )
    assert EXPERIMENT_JSON_COMMAND in text, (
        "the module no longer documents the machine-readable `--json` form"
    )
    assert (ROOT / SPEC).is_file(), (
        f"the module runs `{SPEC}`, which does not exist"
    )


def test_student_page_names_the_result_model_and_exit_boundary():
    text = _student()
    assert "ExperimentResult" in text, (
        "the module no longer names ExperimentResult as the result schema"
    )
    # The observation/claim boundary must stay explicit in student-facing prose.
    lowered = text.lower()
    assert "causal" in lowered, (
        "the module no longer draws the observation/causal boundary"
    )
    assert "exit" in lowered or "exit code" in lowered, (
        "the module no longer explains the exit-code semantics"
    )


def test_student_page_links_the_worked_example_lab():
    text = _student()
    assert LAB04_LINK in text, (
        "the module no longer links the LAB-04 worked example"
    )
    assert (STUDENT.parent / LAB04_LINK).is_file(), (
        f"the module links to `{LAB04_LINK}`, which does not exist"
    )


def test_student_page_does_not_reference_the_answer_key():
    assert "CONTROLLED-EXPERIMENTS-ANSWER-KEY" not in _student(), (
        "the student page must not link to or name the instructor-only answer key"
    )


def test_student_page_is_in_the_published_navigation():
    nav = MKDOCS.read_text(encoding="utf-8")
    assert "CONTROLLED-EXPERIMENTS.md" in nav, (
        "the controlled-experiments module is no longer in the MkDocs navigation"
    )


def test_getting_started_points_to_the_module():
    assert "CONTROLLED-EXPERIMENTS.md" in GETTING_STARTED.read_text(encoding="utf-8"), (
        "the getting-started path no longer points at the controlled-experiments "
        "module"
    )


def test_worked_example_output_matches_the_renderer(monkeypatch, capsys):
    """The §11 result block must stay byte-identical to the real command output.

    The worked example is the module's fidelity anchor: a reader pastes the
    command and should see exactly what the page shows. Running the real command
    in-process (the same interface the reader uses) and comparing against the
    fenced block catches both renderer drift and documentation-only edits, which
    the section-presence guards above cannot see.
    """
    from agentsec.cli import main

    monkeypatch.chdir(ROOT)
    assert main(["experiment", SPEC]) == 0
    actual = capsys.readouterr().out.replace("\r\n", "\n").rstrip("\n")
    assert actual == _worked_example_block(), (
        "labs/CONTROLLED-EXPERIMENTS.md §11 no longer matches the real "
        "`agentsec experiment` output; update the worked example to match the "
        "renderer"
    )


def test_answer_key_is_instructor_only_names_every_state_and_stays_out_of_nav():
    text = ANSWER_KEY.read_text(encoding="utf-8")
    assert "instructor-only" in text.lower(), (
        "the answer key should be marked instructor-only"
    )
    for state in STATES:
        assert state in text, (
            f"the answer key no longer names the state {state!r}"
        )
    nav = MKDOCS.read_text(encoding="utf-8")
    assert "CONTROLLED-EXPERIMENTS-ANSWER-KEY.md" not in nav, (
        "the answer key must not appear in the published navigation"
    )
