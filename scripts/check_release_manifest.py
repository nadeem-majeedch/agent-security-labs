"""Check the v0.1.0 release manifest against the actual release state.

``labs/V0.1.0-RELEASE-MANIFEST.md`` is the owner-facing summary of the prepared
release: the version, the release gate's classification, the accepted warning
set, the CI assumptions and the tag state. Because it is evidence written down
in prose, it can silently drift from the repository — a version bump, a new
warning, a changed CI shape or an unexpected tag would leave the manifest
claiming something false.

This script is a **read-only, deterministic** consistency check for exactly that
drift. It compares the manifest with:

* the authoritative version (``pyproject.toml``, read with :mod:`tomllib`);
* the release gate (``scripts/release_check.py --json``, or a captured report);
* the accepted-warning policy, the canonical documentation and the actual gate
  (reusing :mod:`check_warning_drift`, so the warning-set logic is not
  duplicated);
* the CI workflow (``.github/workflows/ci.yml``): five jobs, one release-gate
  invocation, a drift step that consumes the captured report, no
  ``continue-on-error``;
* the Git tag state (``git tag``, read-only);
* the protected invariants the manifest names.

It never writes a file, never changes the version, never touches the release
gate logic and never creates or moves a tag. It reports **every** disagreement
rather than stopping at the first, and exits ``0`` only when the manifest and the
repository agree.

Usage::

    python scripts/check_release_manifest.py
    python scripts/check_release_manifest.py --gate-report <report.json>

Exits ``0`` when the manifest and the repository state agree, ``1`` otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_FILE = "labs/V0.1.0-RELEASE-MANIFEST.md"
WORKFLOW_FILE = ".github/workflows/ci.yml"
DOCS_WORKFLOW_FILE = ".github/workflows/docs.yml"
RELEASE_SCRIPT = "scripts/release_check.py"
DRIFT_SCRIPT = "scripts/check_warning_drift.py"
SCHEMA_REPO = "schemas/trace/trace_event.v1.schema.json"
SCHEMA_PACKAGED = "src/agentsec/schemas/trace/trace_event.v1.schema.json"
PROJECT_ID = ".freebuff/project-id"
VERSION_FILE = "pyproject.toml"

EXPECTED_CLASSIFICATION = "READY WITH WARNINGS"
EXPECTED_JOB_COUNT = 5
RELEASE_JOB = "release-readiness"
REQUIRED_PASSING_GATES = ("tests", "labs", "mkdocs", "licensing", "version")
CLOSED_WARNING = "W6"

#: The manifest states the accepted set as a ``{...}`` block; parse it rather
#: than trusting a fixed string, then check it against the policy.
_MANIFEST_SET = re.compile(r"\{((?:\s*W\d+\s*,?)+)\}")
_JOB_LINE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
_RUN_LINE = re.compile(r"^\s*-?\s*run:\s*(.+)$")
_CONTINUE_ON_ERROR = re.compile(r"^\s*continue-on-error:")


@dataclass(frozen=True)
class CommandResult:
    """The outcome of one read-only command."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class Check:
    """One manifest invariant: its name, outcome and explanatory detail."""

    name: str
    ok: bool
    summary: str = ""
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ManifestReport:
    """The full set of checks, in report order."""

    checks: tuple[Check, ...]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


@dataclass(frozen=True)
class ReleaseState:
    """Everything the checks compare: the manifest text and the actual state."""

    manifest: str
    version: str | None
    report: dict | None
    gate_problem: str
    policy_ids: frozenset[str] | None
    documented_ids: frozenset[str] | None
    actual_ids: frozenset[str] | None
    drift_problems: tuple[str, ...]
    workflow: str
    tags: tuple[str, ...]
    tracked: tuple[str, ...]
    docs_workflow_present: bool
    schema_copies_equal: bool
    release_script_clean: bool
    ruff_ok: bool
    mypy_ok: bool


def run_command(argv, *, cwd) -> CommandResult:
    """Run ``argv`` and capture its output. Read-only."""
    proc = subprocess.run(
        [str(item) for item in argv],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    return CommandResult(
        tuple(str(item) for item in argv), proc.returncode, proc.stdout, proc.stderr
    )


def _read(root: Path, name: str) -> str | None:
    path = root / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _fmt_ids(ids: frozenset[str] | None) -> str:
    if ids is None:
        return "(unreadable)"
    if not ids:
        return "{}"
    return "{" + ", ".join(sorted(ids)) + "}"


def read_version(root: Path) -> str | None:
    """The authoritative version, from ``pyproject.toml``. Never hard-coded."""
    text = _read(root, VERSION_FILE)
    if text is None:
        return None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    version = project.get("version")
    return version if isinstance(version, str) else None


def _load_drift_guard():
    """Import the sibling ``check_warning_drift`` module (not an installed module)."""
    path = Path(__file__).resolve().parent / "check_warning_drift.py"
    spec = importlib.util.spec_from_file_location("check_warning_drift", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest_warning_ids(text: str) -> frozenset[str] | None:
    """The documented ``{...}`` warning set, or ``None`` when it is absent."""
    match = _MANIFEST_SET.search(text)
    if match is None:
        return None
    return frozenset(
        token.strip() for token in match.group(1).split(",") if token.strip()
    )


def scan_workflow(text: str) -> dict:
    """Summarize the CI workflow's shape from its text (no YAML dependency)."""
    jobs: list[str] = []
    in_jobs = False
    for line in text.splitlines():
        if line.startswith("jobs:"):
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if line.strip() and not line[0].isspace():
            break
        match = _JOB_LINE.match(line)
        if match:
            jobs.append(match.group(1))

    run_lines = [
        match.group(1) for line in text.splitlines() if (match := _RUN_LINE.match(line))
    ]
    drift_lines = [command for command in run_lines if DRIFT_SCRIPT in command]
    return {
        "jobs": jobs,
        "job_count": len(jobs),
        "release_calls": sum(command.count(RELEASE_SCRIPT) for command in run_lines),
        "drift_present": bool(drift_lines),
        "drift_uses_report": bool(drift_lines)
        and all("--gate-report" in command for command in drift_lines),
        "continue_on_error": any(
            _CONTINUE_ON_ERROR.match(line) for line in text.splitlines()
        ),
    }


def _gate_state(
    root: Path, python: str | None, gate_report: Path | None, run
) -> tuple[dict | None, str]:
    """Load the release gate's JSON report, either captured or freshly run."""
    if gate_report is not None:
        if not gate_report.is_file():
            return None, f"gate report {gate_report} is missing"
        text = gate_report.read_text(encoding="utf-8", errors="replace")
        try:
            report = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, f"gate report {gate_report} is not valid JSON: {exc}"
        if not isinstance(report, dict):
            return None, f"gate report {gate_report} is not a JSON object"
        return report, ""
    script = root / RELEASE_SCRIPT
    if not script.is_file():
        return None, f"{RELEASE_SCRIPT} is missing"
    result = run(
        (python or sys.executable, str(script), "--root", str(root), "--json"),
        cwd=root,
    )
    if result.returncode not in (0, 1):
        return None, f"{RELEASE_SCRIPT} --json exited {result.returncode}"
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"{RELEASE_SCRIPT} --json did not emit JSON: {exc}"
    if not isinstance(report, dict):
        return None, f"{RELEASE_SCRIPT} --json did not emit a JSON object"
    return report, ""


def _git_lines(root: Path, run, *args: str) -> list[str]:
    result = run(("git", "-C", str(root), *args), cwd=root)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Individual checks.
# --------------------------------------------------------------------------


def _check_version(state: ReleaseState) -> Check:
    if state.version is None:
        return Check("release version", False, details=("pyproject.toml has no version",))
    marker = f"**Version:** `{state.version}`"
    ok = marker in _normalize(state.manifest)
    return Check(
        "release version",
        ok,
        summary=state.version,
        details=() if ok else (f"manifest does not state {marker!r}",),
    )


def _check_warning_set(state: ReleaseState) -> Check:
    manifest_ids = _manifest_warning_ids(state.manifest)
    details: list[str] = list(state.drift_problems)
    ok = (
        state.policy_ids is not None
        and state.actual_ids is not None
        and state.documented_ids is not None
        and not state.drift_problems
        and state.policy_ids == state.actual_ids
        and manifest_ids is not None
        and manifest_ids == state.policy_ids
    )
    if manifest_ids is None:
        details.append("manifest states no {W...} warning set")
    elif state.policy_ids is not None and manifest_ids != state.policy_ids:
        details.append(f"manifest {_fmt_ids(manifest_ids)} != policy {_fmt_ids(state.policy_ids)}")
    return Check(
        "warning set",
        ok,
        summary=(
            f"manifest {_fmt_ids(manifest_ids)}; policy {_fmt_ids(state.policy_ids)}; "
            f"gate {_fmt_ids(state.actual_ids)}"
        ),
        details=tuple(details),
    )


def _check_blockers(state: ReleaseState) -> Check:
    blockers = state.report.get("blockers") if isinstance(state.report, dict) else None
    manifest = _normalize(state.manifest)
    ok = blockers == [] and "blockers" in manifest.lower() and "[]" in manifest
    details = []
    if blockers != []:
        details.append(f"actual blockers: {blockers!r}")
    if "blockers" not in manifest.lower() or "[]" not in manifest:
        details.append("manifest does not state that blockers are empty")
    return Check("blockers", ok, summary="[]", details=tuple(details))


def _check_classification(state: ReleaseState) -> Check:
    actual = state.report.get("classification") if isinstance(state.report, dict) else None
    in_manifest = EXPECTED_CLASSIFICATION in _normalize(state.manifest)
    ok = actual == EXPECTED_CLASSIFICATION and in_manifest
    details = []
    if actual != EXPECTED_CLASSIFICATION:
        details.append(f"actual classification: {actual!r}")
    if not in_manifest:
        details.append(f"manifest does not state {EXPECTED_CLASSIFICATION!r}")
    return Check("classification", ok, summary=EXPECTED_CLASSIFICATION, details=tuple(details))


def _check_closed_warning(state: ReleaseState) -> Check:
    manifest = _normalize(state.manifest)
    actual_closed = state.actual_ids is not None and CLOSED_WARNING not in state.actual_ids
    documented = CLOSED_WARNING in manifest and "CLOSED" in manifest
    ok = actual_closed and documented
    details = []
    if not actual_closed:
        details.append(f"{CLOSED_WARNING} is still reported by the gate: {_fmt_ids(state.actual_ids)}")
    if not documented:
        details.append(f"manifest does not document {CLOSED_WARNING} as CLOSED")
    return Check(f"{CLOSED_WARNING} closed", ok, details=tuple(details))


def _check_release_validation(state: ReleaseState) -> Check:
    gates = state.report.get("gates") if isinstance(state.report, dict) else None
    gates = gates if isinstance(gates, dict) else {}
    failing = [name for name in REQUIRED_PASSING_GATES if gates.get(name) != "PASS"]
    blockers = state.report.get("blockers") if isinstance(state.report, dict) else None
    ok = not failing and blockers == [] and state.ruff_ok and state.mypy_ok
    details = []
    if state.report is None:
        details.append(state.gate_problem or "no gate report")
    for name in REQUIRED_PASSING_GATES:
        details.append(f"gate {name}: {gates.get(name, 'missing')}")
    details.append(f"ruff: {'PASS' if state.ruff_ok else 'FAIL'}")
    details.append(f"mypy: {'PASS' if state.mypy_ok else 'FAIL'}")
    return Check("release validation", ok, details=tuple(details))


def _check_ci_structure(state: ReleaseState) -> Check:
    scan = scan_workflow(state.workflow)
    ok = (
        scan["job_count"] == EXPECTED_JOB_COUNT
        and RELEASE_JOB in scan["jobs"]
        and scan["release_calls"] == 1
        and scan["drift_present"]
        and scan["drift_uses_report"]
        and not scan["continue_on_error"]
    )
    details = [
        f"jobs: {scan['job_count']} {scan['jobs']}",
        f"release-gate invocations in run steps: {scan['release_calls']}",
        f"drift step present: {scan['drift_present']}, uses --gate-report: {scan['drift_uses_report']}",
        f"continue-on-error present: {scan['continue_on_error']}",
    ]
    return Check(
        "CI structure",
        ok,
        summary=f"{scan['job_count']} jobs, one gate invocation" if ok else "",
        details=tuple(details),
    )


def _check_tag_state(state: ReleaseState) -> Check:
    manifest = _normalize(state.manifest)
    actual = "v0.0.1" in state.tags and "v0.1.0" not in state.tags
    documented = "v0.0.1" in manifest and "has not yet been created" in manifest
    ok = actual and documented
    details = []
    if not actual:
        details.append(f"actual tags: {list(state.tags)}")
    if not documented:
        details.append("manifest does not document the pre-tag state (v0.0.1 present, v0.1.0 absent)")
    return Check(
        "tag state",
        ok,
        summary="v0.0.1 present, v0.1.0 absent" if ok else "",
        details=tuple(details),
    )


def _check_protected(state: ReleaseState) -> Check:
    ok = (
        PROJECT_ID in state.tracked
        and state.docs_workflow_present
        and state.schema_copies_equal
        and state.release_script_clean
    )
    details = [
        f"{PROJECT_ID} tracked: {PROJECT_ID in state.tracked}",
        f"docs workflow present: {state.docs_workflow_present}",
        f"schema copies byte-identical: {state.schema_copies_equal}",
        f"{RELEASE_SCRIPT} unmodified: {state.release_script_clean}",
    ]
    return Check("protected invariants", ok, details=tuple(details))


def evaluate(state: ReleaseState) -> ManifestReport:
    """Evaluate every manifest invariant, without stopping at the first failure."""
    return ManifestReport(
        (
            _check_version(state),
            _check_warning_set(state),
            _check_blockers(state),
            _check_classification(state),
            _check_closed_warning(state),
            _check_release_validation(state),
            _check_ci_structure(state),
            _check_tag_state(state),
            _check_protected(state),
        )
    )


def gather_state(
    root: Path, python: str | None = None, gate_report: Path | None = None, run=run_command
) -> ReleaseState:
    """Collect the manifest text and the actual repository state (read-only)."""
    manifest = _read(root, MANIFEST_FILE) or ""
    version = read_version(root)
    report, gate_problem = _gate_state(root, python, gate_report, run)

    drift = _load_drift_guard()
    if isinstance(report, dict) and isinstance(report.get("warnings"), list):
        ids = frozenset(str(item) for item in report["warnings"])
        actual_source = drift.Source("actual", ids)
    else:
        actual_source = drift.Source("actual", None, gate_problem or "no gate report")
    drift_result = drift.compare(
        (drift.load_policy(root), drift.load_documented(root), actual_source)
    )

    schema_repo = root / SCHEMA_REPO
    schema_packaged = root / SCHEMA_PACKAGED
    schema_equal = (
        schema_repo.is_file()
        and schema_packaged.is_file()
        and schema_repo.read_bytes() == schema_packaged.read_bytes()
    )
    ruff = run(("ruff", "check", "src", "tests", "scripts"), cwd=root)
    mypy = run((python or sys.executable, "-m", "mypy"), cwd=root)

    return ReleaseState(
        manifest=manifest,
        version=version,
        report=report,
        gate_problem=gate_problem,
        policy_ids=drift_result.policy.ids,
        documented_ids=drift_result.documented.ids,
        actual_ids=drift_result.actual.ids,
        drift_problems=drift_result.problems,
        workflow=_read(root, WORKFLOW_FILE) or "",
        tags=tuple(_git_lines(root, run, "tag")),
        tracked=tuple(_git_lines(root, run, "ls-files")),
        docs_workflow_present=(root / DOCS_WORKFLOW_FILE).is_file(),
        schema_copies_equal=schema_equal,
        release_script_clean=not _git_lines(root, run, "status", "--porcelain", "--", RELEASE_SCRIPT),
        ruff_ok=ruff.returncode == 0,
        mypy_ok=mypy.returncode == 0,
    )


def run_checks(
    root: Path, python: str | None = None, gate_report: Path | None = None, run=run_command
) -> ManifestReport:
    """Gather the release state for ``root`` and evaluate the manifest."""
    return evaluate(gather_state(root, python, gate_report, run))


def format_report(report: ManifestReport) -> str:
    """Render every check, reporting all discrepancies rather than the first."""
    title = "Release manifest drift check"
    lines = [title, "=" * len(title), ""]
    for check in report.checks:
        status = "PASS" if check.ok else "FAIL"
        line = f"{status}  {check.name}"
        if check.ok and check.summary:
            line += f": {check.summary}"
        lines.append(line)
        if not check.ok:
            for detail in check.details:
                lines.append(f"      {detail}")
    lines.append("")
    if report.ok:
        lines.append("Result: PASS — manifest and repository state agree")
    else:
        lines.append("Result: FAIL — release manifest drift detected")
    return "\n".join(lines)


def main(argv: list[str] | None = None, *, run=run_command) -> int:
    parser = argparse.ArgumentParser(
        description="Check the v0.1.0 release manifest against the repository (read-only).",
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

    report = run_checks(args.root, gate_report=args.gate_report, run=run)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
