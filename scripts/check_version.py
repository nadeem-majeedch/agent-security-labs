"""Check the repository's declared version for accidental drift.

The project states its version in three places, and this script verifies that
they still agree with each other:

    pyproject.toml              the authoritative project version
    src/agentsec/__init__.py    the version the package reports at runtime
    CITATION.cff                the version attached to the citation metadata

``pyproject.toml``'s ``[project] version`` is the single source of truth: it is
what the build backend stamps into the distribution, and it is the value the
other two declarations must equal. The script does not invent a fourth place
for the number to live, and it never reads a version out of Git, a tag, an
installed distribution or the working directory — the check is offline and
depends only on files already in the tree.

Each declaration is *parsed* rather than matched textually:

* ``pyproject.toml`` is read with :mod:`tomllib`, so a stray ``version =``
  string inside a comment or another table cannot masquerade as the project
  version;
* ``__version__`` is located with :mod:`ast`, so only a real module-level
  assignment counts and the value must be a string literal;
* ``CITATION.cff`` has no standard-library YAML parser, so its header is read
  by a top-level (unindented) ``version:`` key scan, the same technique the
  licence guard uses for ``license:``.

Usage::

    py scripts/check_version.py

Exits ``0`` when the three declarations agree and ``1`` otherwise, printing one
line per declaration so the drift is readable in a CI log and names the exact
source whose value disagrees.

Scope and limits
----------------
This is a **version-consistency check**, not a release manager. It compares the
repository's own declarations against each other; it does not determine the
release version from tags, it does not create a release, and it does not edit a
file. It uses only the standard library, contacts no network, spawns no child
process, reads no Git data structure, and leaves the files it inspects
byte-identical.
"""

from __future__ import annotations

import argparse
import ast
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

#: The authoritative version declaration, and the two that must match it.
PYPROJECT = "pyproject.toml"
INIT = "src/agentsec/__init__.py"
CITATION = "CITATION.cff"

#: The runtime declaration's name in the report, distinct from its file.
INIT_NAME = "agentsec.__version__"


@dataclass(frozen=True)
class CheckResult:
    """One named declaration and whether it agrees with the authoritative one."""

    name: str
    ok: bool
    detail: str


def _read(root: Path, name: str) -> str | None:
    path = root / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _missing(name: str, where: str) -> CheckResult:
    return CheckResult(
        name=name,
        ok=False,
        detail=f"required file {where} is missing (expected {where})",
    )


def _top_level_scalar(text: str, key: str) -> str | None:
    """Return the value of an unindented ``key: value`` line, if present.

    The line scan keeps the guard on the standard library. Matching only
    column-zero keys is what makes it a *top-level* read: an indented
    ``version:`` nested under some other field is not the document version.
    """
    prefix = f"{key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"').strip("'")
    return None


def read_pyproject_version(text: str) -> tuple[str | None, str | None]:
    """Return ``(version, problem)`` for the project version in ``text``."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - malformed file
        return None, f"is not valid TOML: {exc}"

    project = data.get("project")
    if not isinstance(project, dict):
        return None, "has no [project] table"
    declared = project.get("version")
    if declared is None:
        return None, "declares no project.version"
    if not isinstance(declared, str) or not declared.strip():
        return None, (
            f"project.version is {declared!r}, expected a non-empty string"
        )
    return declared.strip(), None


def read_init_version(text: str) -> tuple[str | None, str | None]:
    """Return ``(version, problem)`` for the module-level ``__version__``."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:  # pragma: no cover - malformed file
        return None, f"is not valid Python: {exc}"

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        else:
            continue
        if not (isinstance(target, ast.Name) and target.id == "__version__"):
            continue
        if value is None:
            return None, "declares __version__ with no value"
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            return None, (
                "declares __version__ with a non-string value; expected a "
                "string literal"
            )
        return value.value, None
    return None, "declares no module-level __version__"


def read_citation_version(text: str) -> tuple[str | None, str | None]:
    """Return ``(version, problem)`` for the top-level ``version:`` field."""
    declared = _top_level_scalar(text, "version")
    if declared is None:
        return None, "declares no top-level 'version:' field"
    if not declared.strip():
        return None, "declares an empty 'version:' field"
    return declared, None


def authoritative(root: Path) -> tuple[str | None, str]:
    """Return ``(version, problem)`` for the single source-of-truth version.

    When the authoritative declaration cannot be read, the dependent checks
    cannot have an expected value to compare against, so the reason is returned
    and reported on their lines as well.
    """
    text = _read(root, PYPROJECT)
    if text is None:
        return None, f"{PYPROJECT} is missing"
    version, problem = read_pyproject_version(text)
    if version is None:
        return None, f"{PYPROJECT} {problem}"
    return version, ""


def check_pyproject(root: Path) -> CheckResult:
    """``pyproject.toml`` declares a usable authoritative version."""
    text = _read(root, PYPROJECT)
    if text is None:
        return _missing(PYPROJECT, PYPROJECT)

    version, problem = read_pyproject_version(text)
    if version is None:
        return CheckResult(
            name=PYPROJECT,
            ok=False,
            detail=(
                f"{problem}; {PYPROJECT} holds the authoritative project version"
            ),
        )
    return CheckResult(
        name=PYPROJECT,
        ok=True,
        detail=f"project.version = {version!r} (authoritative)",
    )


def _compare(
    root: Path, name: str, where: str, version: str | None, problem: str | None
) -> CheckResult:
    """Compare one parsed declaration against the authoritative version.

    The caller has already established that ``where`` exists, so a missing
    ``version`` here means the declaration could not be parsed, which is what
    ``problem`` reports.
    """
    if problem is not None or version is None:
        return CheckResult(
            name=name,
            ok=False,
            detail=(
                f"{problem or 'declares no usable version'}; {where} must "
                f"declare the version in {PYPROJECT}"
            ),
        )

    expected, note = authoritative(root)
    if expected is None:
        return CheckResult(
            name=name,
            ok=False,
            detail=(
                f"found {version!r} but the authoritative version is "
                f"unavailable because {note}"
            ),
        )
    if version != expected:
        return CheckResult(
            name=name,
            ok=False,
            detail=(
                f"declares {version!r} but {PYPROJECT} declares {expected!r}; "
                f"set {where} to {expected!r} (or update {PYPROJECT})"
            ),
        )
    return CheckResult(
        name=name,
        ok=True,
        detail=f"declares {version!r}, matching {PYPROJECT}",
    )


def check_init(root: Path) -> CheckResult:
    """``src/agentsec/__init__.py`` reports the authoritative version."""
    text = _read(root, INIT)
    if text is None:
        return _missing(INIT_NAME, INIT)
    version, problem = read_init_version(text)
    return _compare(root, INIT_NAME, INIT, version, problem)


def check_citation(root: Path) -> CheckResult:
    """``CITATION.cff`` cites the authoritative version."""
    text = _read(root, CITATION)
    if text is None:
        return _missing(CITATION, CITATION)
    version, problem = read_citation_version(text)
    return _compare(root, CITATION, CITATION, version, problem)


#: The declarations, in report order: the source of truth first.
CHECKS = (
    check_pyproject,
    check_init,
    check_citation,
)


def run_checks(root: Path) -> list[CheckResult]:
    """Run every declaration check against ``root`` and return them in order."""
    return [check(root) for check in CHECKS]


def format_report(results: list[CheckResult]) -> str:
    """Render the results as a short, CI-friendly report."""
    passed = sum(1 for result in results if result.ok)
    lines = ["version consistency check", "=" * len("version consistency check"), ""]
    for result in results:
        status = "ok  " if result.ok else "FAIL"
        lines.append(f"  {status}  {result.name:<20} {result.detail}")
    lines.append("")
    if passed == len(results):
        lines.append(f"Result: {passed}/{len(results)} checks passed")
    else:
        lines.append(
            f"Result: {len(results) - passed} of {len(results)} checks failed "
            f"({passed} passed)"
        )
        lines.append("")
        lines.append(
            f"The version is declared once, in {PYPROJECT} ([project] version), "
            f"and {INIT} (__version__) and {CITATION} (version:) must equal it. "
            "Fix the declaration, not the check."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the repository's declared version for drift.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to check (default: the parent of this script)",
    )
    args = parser.parse_args(argv)

    results = run_checks(args.root)
    print(format_report(results))
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
