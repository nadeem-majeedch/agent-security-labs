"""Check the three accepted-warning surfaces for drift.

The v0.1.0 release carries a small set of *deliberately accepted*,
non-blocking warnings. That fact lives in three places, and this script verifies
they still agree:

    tests/test_release_check.py        the policy: ACCEPTED_RELEASE_WARNINGS
    labs/ACCEPTED-RELEASE-WARNINGS.md  the documentation: the accepted set
    scripts/release_check.py --json    the actual gate: the emitted warnings

None of the three is a copy of the others, so "they agree" is a claim worth
checking rather than assuming. This script reads the policy constant
structurally (via :mod:`ast`), reads the documented set from the canonical
statement on the page, and obtains the actual set from a structured
``release_check.py --json`` report — never by parsing human-readable console
output. By default it runs the release gate itself; with ``--gate-report`` it
reads an already-generated report instead, so CI can run the gate once and reuse
its output.

The three surfaces must be **exactly equal**. When they are not, the difference
is reported per pair:

* accepted by policy but missing from the documentation;
* documented as accepted but missing from the policy;
* emitted by the gate but not accepted by the policy (an unexpected warning);
* accepted by the policy but no longer emitted (a warning has disappeared);
* the documentation and the gate otherwise disagreeing.

This is a **consistency check, not a release-policy change**. It never retires,
adds or suppresses a warning, never edits a file, never changes the release
classification and never touches Git state beyond the read-only query the gate
itself already runs. It complements — and does not replace — the exact-set
regression test that pins ``ACCEPTED_RELEASE_WARNINGS``; that test is the
protection, this script is the cross-surface view.

Usage::

    python scripts/check_warning_drift.py
    python scripts/check_warning_drift.py --gate-report <report.json>

Exits ``0`` when all three sets are equal, ``1`` otherwise.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

#: Where the three surfaces live, relative to the repository root.
POLICY_FILE = "tests/test_release_check.py"
POLICY_NAME = "ACCEPTED_RELEASE_WARNINGS"
DOC_FILE = "labs/ACCEPTED-RELEASE-WARNINGS.md"
RELEASE_SCRIPT = "scripts/release_check.py"

#: The canonical sentence whose ``{...}`` block states the documented set.
DOC_MARKER = "The accepted set is exactly"

#: A warning identifier is ``W`` followed by digits (``W6``, ``W7``, ``W12``).
WARNING_ID = re.compile(r"^W\d+$")
_BRACES = re.compile(r"\{([^}]*)\}")


@dataclass(frozen=True)
class Source:
    """One accepted-warning surface: its name, its set and any problem.

    ``ids`` is ``None`` only when the surface could not be read or parsed at
    all; a surface that parses but holds a malformed identifier keeps its set
    and reports the problem in ``problem``.
    """

    name: str
    ids: frozenset[str] | None
    problem: str = ""


@dataclass(frozen=True)
class DriftReport:
    """The three surfaces and the disagreements between them."""

    policy: Source
    documented: Source
    actual: Source
    problems: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.problems


def _read(root: Path, name: str) -> str | None:
    path = root / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _validate(ids: frozenset[str], where: str) -> str:
    """Return a problem string if any identifier is not ``W``-and-digits."""
    bad = sorted(item for item in ids if not WARNING_ID.match(item))
    if bad:
        return f"malformed warning identifier(s) {bad} in {where}"
    return ""


def _set_literal(node: ast.AST) -> list[ast.expr] | None:
    """The elements of a set literal, unwrapping ``frozenset({...})``/``set({...})``."""
    if isinstance(node, ast.Set):
        return list(node.elts)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"frozenset", "set"}
        and len(node.args) == 1
    ):
        return _set_literal(node.args[0])
    return None


def load_policy(root: Path) -> Source:
    """Read ``ACCEPTED_RELEASE_WARNINGS`` from the policy test module."""
    text = _read(root, POLICY_FILE)
    if text is None:
        return Source("policy", None, f"{POLICY_FILE} is missing")
    try:
        tree = ast.parse(text, filename=POLICY_FILE)
    except SyntaxError as exc:  # pragma: no cover - malformed file
        return Source("policy", None, f"{POLICY_FILE} is not valid Python: {exc}")

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        else:
            continue
        if not (isinstance(target, ast.Name) and target.id == POLICY_NAME):
            continue
        elements = _set_literal(value)
        if elements is None:
            return Source(
                "policy",
                None,
                f"{POLICY_NAME} in {POLICY_FILE} is not a set of string literals",
            )
        if not all(
            isinstance(element, ast.Constant) and isinstance(element.value, str)
            for element in elements
        ):
            return Source(
                "policy",
                None,
                f"{POLICY_NAME} in {POLICY_FILE} is not a set of string literals",
            )
        ids = frozenset(element.value for element in elements)  # type: ignore[attr-defined]
        return Source("policy", ids, _validate(ids, POLICY_FILE))
    return Source("policy", None, f"{POLICY_FILE} declares no {POLICY_NAME}")


def load_documented(root: Path) -> Source:
    """Read the documented accepted set from the canonical page statement."""
    text = _read(root, DOC_FILE)
    if text is None:
        return Source("documentation", None, f"{DOC_FILE} is missing")
    for line in text.splitlines():
        if DOC_MARKER not in line:
            continue
        match = _BRACES.search(line)
        if match is None:
            return Source(
                "documentation",
                None,
                f"{DOC_FILE} states {DOC_MARKER!r} with no {{...}} set",
            )
        ids = frozenset(
            token.strip() for token in match.group(1).split(",") if token.strip()
        )
        return Source("documentation", ids, _validate(ids, DOC_FILE))
    return Source(
        "documentation",
        None,
        f"{DOC_FILE} does not state {DOC_MARKER!r}",
    )


def load_actual(root: Path, python: str | None = None) -> Source:
    """Run the release gate with ``--json`` and read its structured warnings."""
    script = root / RELEASE_SCRIPT
    if not script.is_file():
        return Source("actual", None, f"{RELEASE_SCRIPT} is missing")
    interpreter = python or sys.executable
    try:
        completed = subprocess.run(
            [interpreter, str(script), "--root", str(root), "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
    except OSError as exc:  # pragma: no cover - environment failure
        return Source("actual", None, f"could not run {RELEASE_SCRIPT}: {exc}")
    if completed.returncode not in (0, 1):
        return Source(
            "actual",
            None,
            f"{RELEASE_SCRIPT} --json exited {completed.returncode}",
        )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return Source(
            "actual",
            None,
            f"{RELEASE_SCRIPT} --json did not emit JSON: {exc}",
        )
    warnings = report.get("warnings") if isinstance(report, dict) else None
    if not isinstance(warnings, list):
        return Source(
            "actual",
            None,
            f"{RELEASE_SCRIPT} report has no 'warnings' list",
        )
    ids = frozenset(str(item) for item in warnings)
    return Source("actual", ids, _validate(ids, f"{RELEASE_SCRIPT} --json"))


def load_actual_from_report(path: Path) -> Source:
    """Read the actual warning set from an existing ``--json`` gate report.

    This is the CI path: the release gate runs once, its JSON report is written
    to a temporary file outside the checkout, and this reads that file rather
    than executing ``release_check.py`` a second time. The report is validated
    the same way as live output (a JSON object with a ``warnings`` list), so a
    missing or malformed report fails just as clearly.
    """
    if not path.is_file():
        return Source("actual", None, f"gate report {path} is missing")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:  # pragma: no cover - environment failure
        return Source("actual", None, f"could not read gate report {path}: {exc}")
    try:
        report = json.loads(text)
    except json.JSONDecodeError as exc:
        return Source(
            "actual",
            None,
            f"gate report {path} is not valid JSON: {exc}",
        )
    warnings = report.get("warnings") if isinstance(report, dict) else None
    if not isinstance(warnings, list):
        return Source("actual", None, f"gate report {path} has no 'warnings' list")
    ids = frozenset(str(item) for item in warnings)
    return Source("actual", ids, _validate(ids, f"gate report {path}"))


def _fmt(ids: frozenset[str] | None) -> str:
    if ids is None:
        return "(unreadable)"
    if not ids:
        return "{}"
    return "{" + ", ".join(sorted(ids)) + "}"


def compare(sources: tuple[Source, Source, Source]) -> DriftReport:
    """Compare the three surfaces and collect every disagreement.

    Pairwise differences are only computed between surfaces that both parsed;
    a surface that could not be read contributes its own problem instead.
    """
    policy_source, documented_source, actual_source = sources
    policy, documented, actual = (
        policy_source.ids,
        documented_source.ids,
        actual_source.ids,
    )

    problems: list[str] = []
    for source in sources:
        if source.problem:
            problems.append(f"{source.name}: {source.problem}")

    if policy is not None and documented is not None:
        missing = policy - documented
        extra = documented - policy
        if missing:
            problems.append(
                "accepted by policy but missing from documentation: "
                + _fmt(missing)
            )
        if extra:
            problems.append(
                "documented as accepted but missing from policy: " + _fmt(extra)
            )

    if policy is not None and actual is not None:
        unexpected = actual - policy
        disappeared = policy - actual
        if unexpected:
            problems.append(
                "the release gate emits warning(s) not accepted by policy: "
                + _fmt(unexpected)
            )
        if disappeared:
            problems.append(
                "accepted warning(s) have disappeared from the release gate: "
                + _fmt(disappeared)
            )

    if documented is not None and actual is not None and documented != actual:
        only_documented = documented - actual
        only_actual = actual - documented
        parts = []
        if only_documented:
            parts.append("only documented: " + _fmt(only_documented))
        if only_actual:
            parts.append("only in the gate: " + _fmt(only_actual))
        problems.append("documentation and the gate disagree: " + "; ".join(parts))

    return DriftReport(
        policy=policy_source,
        documented=documented_source,
        actual=actual_source,
        problems=tuple(problems),
    )


def run_checks(
    root: Path, python: str | None = None, gate_report: Path | None = None
) -> DriftReport:
    """Load all three surfaces for ``root`` and compare them.

    With ``gate_report`` the actual set is read from that existing report
    instead of running the release gate, so the gate needs to run only once.
    """
    actual = (
        load_actual_from_report(gate_report)
        if gate_report is not None
        else load_actual(root, python)
    )
    return compare((load_policy(root), load_documented(root), actual))


def format_report(report: DriftReport) -> str:
    """Render the three sets and any drift as a short, CI-friendly report."""
    title = "accepted-warning drift check"
    lines = [title, "=" * len(title), ""]
    lines.append(f"  policy         {_fmt(report.policy.ids)}")
    lines.append(f"  documentation  {_fmt(report.documented.ids)}")
    lines.append(f"  actual gate    {_fmt(report.actual.ids)}")
    lines.append("")
    if report.ok:
        lines.append(f"Result: all three sets agree: {_fmt(report.documented.ids)}")
    else:
        lines.append("Result: DRIFT DETECTED")
        for problem in report.problems:
            lines.append(f"  - {problem}")
        lines.append("")
        lines.append(
            "The policy (tests/test_release_check.py), the documentation "
            "(labs/ACCEPTED-RELEASE-WARNINGS.md) and the release gate "
            "(scripts/release_check.py --json) must report the same accepted "
            "warning set. Reconcile the surfaces deliberately; do not retire a "
            "warning by weakening the policy or suppressing the gate."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the accepted-warning surfaces for drift.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to check (default: the parent of this script)",
    )
    parser.add_argument(
        "--gate-report",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "read an existing 'release_check.py --json' report instead of "
            "running the release gate"
        ),
    )
    args = parser.parse_args(argv)

    report = run_checks(args.root, gate_report=args.gate_report)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
