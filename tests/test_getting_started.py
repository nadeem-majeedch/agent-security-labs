"""The guided getting-started path must keep exposing the comparison exercises.

``labs/GETTING-STARTED.md`` is the student's first-run path. Phase 7F added a
"Try a two-policy comparison" step that points at the already-existing
``agentsec demo lab04-two-policies`` command (and its ``--json`` form), so a
learner can reach the two-policy comparison without hunting through the CLI
reference or the per-lab pages. Phase 7H added the companion
"Try an approval-vs-deny comparison" step, which runs the same LAB-05 experiment
under two policies and compares the traces, Phase 7K added a "Try a cross-lab
comparison" step that compares two *different* labs (LAB-01 and LAB-02), and
Phase 7L added its companion, "Compare two labs that differ" (LAB-01 and LAB-05),
which shows a comparison with a real structural difference, and Phase 8 added
"Predict before you run", which checks a learner's prediction against a trace
with the read-only `agentsec predict` command. Phase 8A expanded that step to
name a small set of example predictions covering distinct observable outcomes
(approval-held, mixed allowed-and-denied, and two different tools).

These tests pin the things that make those steps useful and that no other check
covers -- ``mkdocs build --strict`` validates links but not that the exercises
are actually *surfaced*, and the suite never runs their text:

* **the documented commands** -- the demo's plain and ``--json`` forms and the
  two LAB-05 run commands must still appear verbatim, so a reader can copy them;
* **the links** -- each step must link to its lab page's worked explanation, and
  that file and anchor must both exist; and
* **the section headings** -- each numbered step must still be present, so the
  exercises do not silently disappear or get renumbered out of the flow.

This is a documentation-consistency guard, not a content review. It reads files
directly, uses no subprocess and no network, and asserts nothing about the
number of tests in the suite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GETTING_STARTED = ROOT / "labs" / "GETTING-STARTED.md"

#: The exact commands the guided step must document, in repository convention.
DEMO_COMMAND = "PYTHONPATH=src py -m agentsec demo lab04-two-policies"
DEMO_JSON_COMMAND = "PYTHONPATH=src py -m agentsec demo lab04-two-policies --json"

#: The section heading the exercise is filed under.
SECTION_HEADING = "## 5. Try a two-policy comparison"

#: The precise LAB-04 link target used by the new section: the page, and the
#: "Same lab, different policy" anchor that works the example through.
LAB04_LINK = "LAB-04-tool-misuse/README.md#same-lab-different-policy"

#: The two LAB-05 commands the approval-vs-deny step must document: the shipped
#: lab and the deny-by-default example config.
LAB05_APPROVAL_COMMAND = (
    "PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml"
)
LAB05_DENY_COMMAND = (
    "PYTHONPATH=src py -m agentsec run "
    "configs/examples/lab05_require_approval_deny_by_default.yaml"
)

#: The heading of the approval-vs-deny step.
APPROVAL_SECTION_HEADING = "## 6. Try an approval-vs-deny comparison"

#: The LAB-05 link target: the page, and the "Same lab, two decisions" anchor.
LAB05_LINK = "LAB-05-require-approval/README.md#same-lab-two-decisions"

#: The two commands the cross-lab step must document: the two introductory labs.
CROSS_LAB_COMMAND_A = (
    "PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml"
)
CROSS_LAB_COMMAND_B = (
    "PYTHONPATH=src py -m agentsec run "
    "labs/LAB-02-direct-prompt-injection/config.yaml"
)

#: The heading of the cross-lab step.
CROSS_LAB_SECTION_HEADING = "## 7. Try a cross-lab comparison"

#: The lab pages the cross-lab step must link to.
CROSS_LAB_LINKS = (
    "LAB-01-benign-agent/README.md",
    "LAB-02-direct-prompt-injection/README.md",
)

#: The heading of the differing-comparison step (Phase 7L).
DIFFERING_SECTION_HEADING = "## 8. Compare two labs that differ"

#: The two commands and two trace paths the differing-comparison step documents.
DIFFERING_COMMAND_A = (
    "PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml"
)
DIFFERING_COMMAND_B = (
    "PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml"
)
DIFFERING_TRACE_A = "runs/lab01_benign/trace.jsonl"
DIFFERING_TRACE_B = "runs/lab05_require_approval/trace.jsonl"

#: The lab pages the differing-comparison step must link to.
DIFFERING_LINKS = (
    "LAB-01-benign-agent/README.md",
    "LAB-05-require-approval/README.md",
)

#: The heading of the predict-before-you-run step (Phase 8).
PREDICT_SECTION_HEADING = "## 9. Predict before you run"
#: The predict invocation, trace and prediction the step must document.
PREDICT_MARKER = "PYTHONPATH=src py -m agentsec predict"
PREDICT_TRACE = "runs/lab04_tool_misuse/trace.jsonl"
PREDICT_PREDICTION = "configs/predictions/lab04.yaml"
#: The lab page the predict step must link to.
PREDICT_LINK = "LAB-04-tool-misuse/README.md"
#: The expanded example predictions (Phase 8A) the predict step must surface.
PREDICT_EXAMPLES = (
    "configs/predictions/lab05_expect_approval.yaml",
    "configs/predictions/lab05_expect_denied.yaml",
    "configs/predictions/lab03_expect_allowed_then_denied.yaml",
    "configs/predictions/lab07_expect_two_tools.yaml",
)


def _text() -> str:
    assert GETTING_STARTED.is_file(), "labs/GETTING-STARTED.md is missing"
    return GETTING_STARTED.read_text(encoding="utf-8")


def _slug(heading_text: str) -> str:
    """Return the GitHub/MkDocs-style anchor for a heading's text."""
    text = heading_text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s]+", "-", text).strip("-")


def _section(heading: str) -> str:
    """Return the body of the ``##`` section introduced by ``heading``."""
    lines = _text().splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            body = []
            for following in lines[index + 1 :]:
                if following.startswith("## "):
                    break
                body.append(following)
            return "\n".join(body)
    assert False, f"labs/GETTING-STARTED.md has no `{heading}` section"


def test_getting_started_documents_both_demo_commands():
    text = _text()
    assert DEMO_COMMAND in text, (
        "labs/GETTING-STARTED.md no longer documents "
        f"`{DEMO_COMMAND}`; the two-policy demo must stay reachable from the "
        "guided path"
    )
    assert DEMO_JSON_COMMAND in text, (
        "labs/GETTING-STARTED.md no longer documents the machine-readable form "
        f"`{DEMO_JSON_COMMAND}`"
    )


def test_getting_started_links_the_lab04_two_policy_section():
    text = _text()
    assert LAB04_LINK in text, (
        "labs/GETTING-STARTED.md no longer links to the LAB-04 worked example "
        f"at `{LAB04_LINK}`; point the exercise at the detailed explanation "
        "instead of duplicating it"
    )

    target, _, anchor = LAB04_LINK.partition("#")
    linked = GETTING_STARTED.parent / target
    assert linked.is_file(), (
        f"the getting-started page links to `{target}`, which does not exist"
    )

    headings = re.findall(r"^#{1,6}\s+(.*)$", linked.read_text(encoding="utf-8"), flags=re.MULTILINE)
    anchors = {_slug(heading) for heading in headings}
    assert anchor in anchors, (
        f"`{target}` has no heading with the anchor `#{anchor}`; the link would "
        "land nowhere (available anchors: " + ", ".join(sorted(anchors)) + ")"
    )


def test_getting_started_keeps_the_two_policy_section_heading():
    text = _text()
    headings = re.findall(r"^##\s+.*$", text, flags=re.MULTILINE)
    assert SECTION_HEADING in headings, (
        f"labs/GETTING-STARTED.md has no `{SECTION_HEADING}` section. If the "
        "page was legitimately renumbered or retitled, update SECTION_HEADING "
        "here in the same change so the exercise stays guarded."
    )


def test_getting_started_documents_both_lab05_commands():
    text = _text()
    assert LAB05_APPROVAL_COMMAND in text, (
        "labs/GETTING-STARTED.md no longer documents "
        f"`{LAB05_APPROVAL_COMMAND}`; the approval-vs-deny step must still run "
        "the shipped LAB-05 config"
    )
    assert LAB05_DENY_COMMAND in text, (
        "labs/GETTING-STARTED.md no longer documents "
        f"`{LAB05_DENY_COMMAND}`; the deny-by-default config must stay reachable"
    )


def test_getting_started_links_the_lab05_two_decisions_section():
    text = _text()
    assert LAB05_LINK in text, (
        "labs/GETTING-STARTED.md no longer links to the LAB-05 worked example "
        f"at `{LAB05_LINK}`; point the exercise at the detailed explanation "
        "instead of duplicating it"
    )

    target, _, anchor = LAB05_LINK.partition("#")
    linked = GETTING_STARTED.parent / target
    assert linked.is_file(), (
        f"the getting-started page links to `{target}`, which does not exist"
    )

    headings = re.findall(
        r"^#{1,6}\s+(.*)$", linked.read_text(encoding="utf-8"), flags=re.MULTILINE
    )
    anchors = {_slug(heading) for heading in headings}
    assert anchor in anchors, (
        f"`{target}` has no heading with the anchor `#{anchor}`; the link would "
        "land nowhere (available anchors: " + ", ".join(sorted(anchors)) + ")"
    )


def test_getting_started_keeps_the_approval_vs_deny_section_heading():
    text = _text()
    headings = re.findall(r"^##\s+.*$", text, flags=re.MULTILINE)
    assert APPROVAL_SECTION_HEADING in headings, (
        f"labs/GETTING-STARTED.md has no `{APPROVAL_SECTION_HEADING}` section. If "
        "the page was legitimately renumbered or retitled, update "
        "APPROVAL_SECTION_HEADING here in the same change so the exercise stays "
        "guarded."
    )


def test_getting_started_documents_both_cross_lab_commands():
    text = _text()
    assert CROSS_LAB_COMMAND_A in text, (
        "labs/GETTING-STARTED.md no longer documents "
        f"`{CROSS_LAB_COMMAND_A}`; the cross-lab step must still run LAB-01"
    )
    assert CROSS_LAB_COMMAND_B in text, (
        "labs/GETTING-STARTED.md no longer documents "
        f"`{CROSS_LAB_COMMAND_B}`; the cross-lab step must still run LAB-02"
    )


def test_getting_started_links_both_cross_lab_pages():
    text = _text()
    for link in CROSS_LAB_LINKS:
        assert link in text, (
            "labs/GETTING-STARTED.md no longer links the cross-lab step to "
            f"`{link}`; point it at the lab page instead of duplicating it"
        )
        assert (GETTING_STARTED.parent / link).is_file(), (
            f"the getting-started page links to `{link}`, which does not exist"
        )


def test_getting_started_keeps_the_cross_lab_section_heading():
    text = _text()
    headings = re.findall(r"^##\s+.*$", text, flags=re.MULTILINE)
    assert CROSS_LAB_SECTION_HEADING in headings, (
        f"labs/GETTING-STARTED.md has no `{CROSS_LAB_SECTION_HEADING}` section. "
        "If the page was legitimately renumbered or retitled, update "
        "CROSS_LAB_SECTION_HEADING here in the same change so the exercise stays "
        "guarded."
    )


def test_getting_started_keeps_the_differing_comparison_section_heading():
    text = _text()
    headings = re.findall(r"^##\s+.*$", text, flags=re.MULTILINE)
    assert DIFFERING_SECTION_HEADING in headings, (
        f"labs/GETTING-STARTED.md has no `{DIFFERING_SECTION_HEADING}` section. "
        "If the page was legitimately renumbered or retitled, update "
        "DIFFERING_SECTION_HEADING here in the same change so the exercise stays "
        "guarded."
    )


def test_getting_started_documents_the_differing_comparison_commands():
    body = _section(DIFFERING_SECTION_HEADING)
    for command in (DIFFERING_COMMAND_A, DIFFERING_COMMAND_B):
        assert command in body, (
            "the differing-comparison section no longer documents "
            f"`{command}`"
        )
    for trace in (DIFFERING_TRACE_A, DIFFERING_TRACE_B):
        assert trace in body, (
            "the differing-comparison section no longer compares "
            f"`{trace}`"
        )


def test_getting_started_links_both_pages_in_the_differing_comparison_section():
    body = _section(DIFFERING_SECTION_HEADING)
    for link in DIFFERING_LINKS:
        assert link in body, (
            "the differing-comparison section no longer links "
            f"`{link}`; point it at the lab page instead of duplicating it"
        )
        assert (GETTING_STARTED.parent / link).is_file(), (
            f"the getting-started page links to `{link}`, which does not exist"
        )


def test_getting_started_keeps_the_predict_section_heading():
    text = _text()
    headings = re.findall(r"^##\s+.*$", text, flags=re.MULTILINE)
    assert PREDICT_SECTION_HEADING in headings, (
        f"labs/GETTING-STARTED.md has no `{PREDICT_SECTION_HEADING}` section. If "
        "the page was legitimately renumbered or retitled, update "
        "PREDICT_SECTION_HEADING here in the same change so the exercise stays "
        "guarded."
    )


def test_getting_started_documents_the_predict_command():
    body = _section(PREDICT_SECTION_HEADING)
    assert PREDICT_MARKER in body, (
        "the predict step no longer documents the `agentsec predict` command"
    )
    assert PREDICT_TRACE in body, (
        "the predict step no longer names the trace it checks "
        f"(`{PREDICT_TRACE}`)"
    )
    assert PREDICT_PREDICTION in body, (
        "the predict step no longer names the example prediction "
        f"(`{PREDICT_PREDICTION}`)"
    )


def test_getting_started_links_the_lab04_page_in_the_predict_section():
    body = _section(PREDICT_SECTION_HEADING)
    assert PREDICT_LINK in body, (
        "the predict step no longer links the LAB-04 page; point it at the lab "
        "instead of duplicating it"
    )
    assert (GETTING_STARTED.parent / PREDICT_LINK).is_file(), (
        f"the getting-started page links to `{PREDICT_LINK}`, which does not exist"
    )


def test_getting_started_names_the_expanded_prediction_examples():
    body = _section(PREDICT_SECTION_HEADING)
    for example in PREDICT_EXAMPLES:
        assert example in body, (
            "the predict step no longer names the example prediction "
            f"`{example}`"
        )
        assert (ROOT / example).is_file(), (
            f"the predict step names `{example}`, which does not exist"
        )
