"""The policy-example inventory must stay documented in both live locations.

``policies/examples/`` is the repository's set of example policies, and two live
documents describe it: the root ``README.md`` project table and the
``policies/examples/`` line of the repository tree in ``docs/development.md``.
Phase 7C added a fifth example (``allow_all_v1``) and both locations drifted
until Phase 7I corrected them; this guard keeps them from drifting again.

The expected inventory is *derived* from the actual ``policies/examples/*.yaml``
files -- the number and the filenames are never hard-coded -- and both documents
must name every example and nothing that no longer exists. Historical research
records under ``research/`` are deliberately out of scope: they preserve
historical snapshots on purpose. This is a documentation-consistency guard, not a
content review. It reads files directly, uses no subprocess and no network, and
asserts nothing about the number of tests in the suite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "policies" / "examples"
README = ROOT / "README.md"
DEVELOPMENT = ROOT / "docs" / "development.md"

#: Spelled-out counts the README row may use, so the count can be compared
#: without the guard hard-coding a number.
_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

#: The README project-table row that documents ``policies/examples/``.
_README_ROW = re.compile(r"^.*policies/examples/.*example polic.*$", re.MULTILINE)
#: The repository-tree line in ``docs/development.md``.
_DEVELOPMENT_LINE = re.compile(
    r"^policies/examples/\s*#\s*(?P<names>.+?)\s*$", re.MULTILINE
)
#: An inline-code token that could be a policy-example name (no path separator).
_BACKTICKED = re.compile(r"`([a-z0-9_]+)`")


def _example_stems() -> set[str]:
    """The example-policy names on disk, by filename stem."""
    assert POLICY_DIR.is_dir(), "policies/examples/ is missing"
    stems = {path.stem for path in POLICY_DIR.glob("*.yaml")}
    assert stems, "no policy examples found under policies/examples/"
    return stems


def _readme_policy_line() -> str:
    text = README.read_text(encoding="utf-8")
    match = _README_ROW.search(text)
    assert match is not None, (
        "README.md no longer has a project-table row documenting "
        "`policies/examples/`"
    )
    return match.group(0)


def _readme_documented_names() -> set[str]:
    return set(_BACKTICKED.findall(_readme_policy_line()))


def _development_documented_names() -> set[str]:
    text = DEVELOPMENT.read_text(encoding="utf-8")
    match = _DEVELOPMENT_LINE.search(text)
    assert match is not None, (
        "docs/development.md no longer has a 'policies/examples/' tree line"
    )
    names = {name.strip() for name in match.group("names").split(",")}
    return {name for name in names if name}


def test_policy_example_inventory_is_discovered():
    assert _example_stems(), "no policy examples discovered under policies/examples/"


def test_readme_documents_every_policy_example():
    missing = _example_stems() - _readme_documented_names()
    assert not missing, (
        "README.md's policy-example row does not mention: "
        + ", ".join(sorted(missing))
    )


def test_readme_has_no_stale_policy_example_entries():
    stale = _readme_documented_names() - _example_stems()
    assert not stale, (
        "README.md names policy examples that no longer exist: "
        + ", ".join(sorted(stale))
    )


def test_readme_states_the_correct_policy_example_count():
    line = _readme_policy_line().lower()
    match = re.search(r"\b(" + "|".join(_NUMBER_WORDS) + r")\b\s+example polic", line)
    assert match is not None, (
        "README.md's policy-example row does not state a count such as "
        "'five example policies'"
    )
    stated = _NUMBER_WORDS[match.group(1)]
    actual = len(_example_stems())
    assert stated == actual, (
        f"README.md says there are {stated} example policies but "
        f"policies/examples/ holds {actual}"
    )


def test_development_docs_document_every_policy_example():
    stems = _example_stems()
    documented = _development_documented_names()
    missing = stems - documented
    stale = documented - stems
    assert not missing, (
        "docs/development.md's 'policies/examples/' tree line omits: "
        + ", ".join(sorted(missing))
    )
    assert not stale, (
        "docs/development.md's 'policies/examples/' tree line names policy "
        "examples that no longer exist: " + ", ".join(sorted(stale))
    )
