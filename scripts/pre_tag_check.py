"""Run the owner pre-tag validation sequence for the v0.1.0 release.

This is a small, **read-only orchestration tool**, not a release tool and not a
new check. It runs the checks the owner already runs by hand before creating the
``v0.1.0`` tag, in one deterministic pass, and prints a sectioned report with an
unambiguous final status.

It *orchestrates* the established checks rather than re-implementing any of them:

    1.  version check      scripts/check_version.py
    2.  licensing check    scripts/check_licensing.py
    3.  test suite         python -m pytest
    4.  labs check         python -m agentsec labs check
    5.  Ruff               ruff check src tests scripts
    6.  mypy               python -m mypy
    7.  MkDocs strict      python -m mkdocs build --strict
    8.  release gate       scripts/release_check.py --json   (run once)
    9.  warning drift      scripts/check_warning_drift.py    --gate-report
    10. manifest drift     scripts/check_release_manifest.py --gate-report
    11. Git/tag state      read-only `git tag`
    12. final result

Steps 9 and 10 consume the JSON report of step 8 (written to a temporary file
outside the repository), so ``release_check.py`` executes exactly **once**. That
is the same single-execution design CI uses: the gate runs once and its captured
report is reused.

Scope and limits
----------------
The command is read-only and deterministic. It never commits, pushes, stages,
tags or publishes anything, and it never edits a file in the repository, the
version, the acceptance policy, the release gate or the CI. It does **not**
require a clean working tree — the tree is intentionally dirty while the release
awaits owner review — and a dirty tree is not treated as a failure unless the
existing release gate already reports a blocker. It uses only the standard
library for its own work and contacts no network beyond whatever an existing
command inherently needs. Standard output, values reported by the existing
checks, and their exit codes are preserved.

The expected ``v0.1.0`` state is version ``0.1.0``, ``blockers: []``,
classification ``READY WITH WARNINGS``, warnings exactly ``{W7, W12}``, ``W6``
closed, ``v0.0.1`` present and ``v0.1.0`` absent. ``READY WITH WARNINGS`` is a
**success**, not a failure.

Usage::

    python scripts/pre_tag_check.py
    python scripts/pre_tag_check.py --summary
    python scripts/pre_tag_check.py --json
    python scripts/pre_tag_check.py --verify-report <report.json>

Exits ``0`` only when every required check succeeds, ``1`` otherwise. A
successful validation means the repository is ready for owner review. It does
not authorize or perform the release.

``--json`` prints a single deterministic JSON object on standard output
(nothing else) so the exact owner pre-tag evidence can be archived without
copying terminal text. It shares the same exit status as the human-readable
mode and changes nothing about which checks run or how the gate report is
reused.

Tamper-evident attestation
--------------------------
The ``--json`` report carries an ``attestation`` object binding it to the exact
repository state that produced it:

* ``repository_state_sha256`` — a SHA-256 digest over the repository's
  **tracked and untracked-but-not-ignored** files (the ``git ls-files``
  working-tree inventory, the same content set the licensing check accounts
  for). Each file contributes ``relative_path + NUL + file_bytes`` in
  lexicographic path order, with **no** ``.git`` metadata, ignored/generated
  files, temporary files, caches, build output, absolute paths or timestamps.
* ``report_payload_sha256`` — a SHA-256 digest of the canonical JSON of the
  report **without** its ``attestation`` object, so it is not self-referential.

``--verify-report`` re-checks an archived report against the current tree
without running any check: it recomputes both digests, reports every mismatch
and exits ``0`` only when the report still matches. This is **integrity
evidence, not a digital signature** and not trusted provenance — it proves the
report and the tree were not altered together; it does not prove who generated
the report.

Owner-controlled signing
------------------------
Integrity is not provenance. The SHA-256 attestation says *whether* a report or
tree was altered; it cannot say *who* produced the report. To add that
provenance without weakening the attestation, an **optional** signature can be
attached with the local OpenSSL 3.x tool — no cryptographic dependency is added
to the project, and normal validation never needs a key:

* ``--sign-report <report.json>`` reads an already-generated report, **verifies
  its SHA-256 attestation first** (and refuses to sign if that attestation is
  already invalid), then signs the exact canonical report payload described
  above — the bytes ``report_payload_sha256`` covers, with the ``attestation``
  and ``signature`` envelopes excluded. The Ed25519 signature, its base64
  encoding, the algorithm and a deterministic public-key fingerprint are written
  into a new ``signature`` object in an explicitly chosen output file. The input
  is never overwritten unless the same path is supplied explicitly.
* ``--verify-report <report.json> --public-key <public.pem>`` additionally
  checks that signature. An unsigned report still verifies for its integrity; a
  signed report without ``--public-key`` is reported as **signature present but
  not verified** rather than silently accepted; a wrong key, a modified report,
  a modified signature, a malformed signature or an unsupported algorithm fails.

Signing is optional, read-only with respect to the repository, and never
commits, pushes, tags or publishes. It proves **possession and control of the
signing key**, not personal identity.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

#: A full gate run may rebuild the wheel and run the suite; allow it time.
DEFAULT_TIMEOUT = 1800

#: How much captured output to quote when a step fails.
TAIL_LENGTH = 1500

#: The release title shown in the report banner.
TITLE = "AgentSec v0.1.0 PRE-TAG VALIDATION"

#: The total number of sections, including the final result.
TOTAL_STEPS = 12

NOT_READY = "NOT READY"
READY_FOR_OWNER = "READY FOR OWNER REVIEW"
READY_WITH_WARNINGS = "READY WITH WARNINGS"

#: The schema version of the ``--json`` pre-tag report.
SCHEMA_VERSION = "1"

#: The attestation algorithm and method recorded in the JSON report. The method
#: names the canonical repository-state definition so a reader knows exactly
#: what was hashed.
ATTESTATION_ALGORITHM = "SHA-256"
ATTESTATION_METHOD = "sha256-canonical-git-inventory-v1"

#: The two report *envelopes* excluded from the canonical payload: the
#: integrity attestation and the optional owner signature. Excluding both keeps
#: the payload — and therefore ``report_payload_sha256`` and the signing input —
#: identical before and after a signature is attached.
ATTESTATION_KEY = "attestation"
SIGNATURE_KEY = "signature"

#: Owner-controlled signing constants. Ed25519 is a modern, well-established
#: signature scheme with deterministic signatures and small keys; the actual
#: cryptography is performed by the external OpenSSL 3.x tool (argument arrays,
#: never a shell), so no cryptographic dependency is added to the project.
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_ENCODING = "base64"
#: How the public-key fingerprint named by ``key_id`` is computed: the SHA-256
#: of the DER-encoded SubjectPublicKeyInfo. It is deterministic, portable and
#: derived only from the key — never from a path, user, host or environment.
SIGNATURE_KEY_ID_METHOD = "sha256-spki-der"
SUPPORTED_SIGNATURE_ALGORITHMS = (SIGNATURE_ALGORITHM,)

#: The four distinguishable signature states reported by ``--verify-report``.
SIGNATURE_ABSENT = "absent"
SIGNATURE_UNVERIFIED = "present-not-verified"
SIGNATURE_VERIFIED = "verified"
SIGNATURE_INVALID = "invalid"

#: A lowercase hexadecimal SHA-256 digest.
_HEX_DIGEST = re.compile(r"\A[0-9a-f]{64}\Z")

#: The pre-tag Git/tag invariant.
PRESENT_TAG = "v0.0.1"
ABSENT_TAG = "v0.1.0"

BAR = "=" * 40


@dataclass(frozen=True)
class CommandResult:
    """The outcome of one read-only command."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class StepResult:
    """One validation step: its name, outcome and the lines to print.

    ``info`` carries structured data the JSON report needs (currently only the
    release gate populates it) without changing the human-readable output.
    """

    name: str
    ok: bool
    lines: tuple[str, ...]
    info: dict | None = None


@dataclass(frozen=True)
class Context:
    """Everything a step needs: the root, interpreter, env, scratch and runner."""

    root: Path
    python: str
    env: dict
    scratch: Path
    run: object


def run_command(argv, *, cwd, env=None, timeout=DEFAULT_TIMEOUT) -> CommandResult:
    """Run ``argv`` and capture its output. Never mutates the repository."""
    proc = subprocess.run(
        [str(item) for item in argv],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CommandResult(
        tuple(str(item) for item in argv),
        proc.returncode,
        proc.stdout,
        proc.stderr,
    )


def _child_env(root: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    return env


def _tail(text: str, length: int = TAIL_LENGTH) -> str:
    text = text.strip()
    return text if len(text) <= length else "…" + text[-length:]


def _indent(text: str) -> tuple[str, ...]:
    """Indent captured output under a failing step's line."""
    return tuple(f"      {line}" for line in text.splitlines() if line.strip())


def read_version(root: Path) -> str | None:
    """Return the authoritative project version, or ``None``."""
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except tomllib.TOMLDecodeError:  # pragma: no cover - malformed file
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    version = project.get("version")
    return version.strip() if isinstance(version, str) and version.strip() else None


def _warning_sort_key(identifier: str):
    """Order ``W7`` before ``W12`` (numeric, not lexicographic)."""
    match = re.fullmatch(r"W(\d+)", identifier)
    return (0, int(match.group(1))) if match else (1, identifier)


def _fmt_set(ids) -> str:
    if not isinstance(ids, list):
        return "(unavailable)"
    if not ids:
        return "{}"
    return "{" + ", ".join(sorted((str(item) for item in ids), key=_warning_sort_key)) + "}"


# --------------------------------------------------------------------------
# Steps 1-7: the established quality gates.
# --------------------------------------------------------------------------


def step_version(ctx: Context) -> StepResult:
    """Step 1: the three version declarations agree."""
    script = ctx.root / "scripts" / "check_version.py"
    command = (ctx.python, str(script), "--root", str(ctx.root))
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    version = read_version(ctx.root)
    if result.returncode == 0:
        return StepResult("Version", True, (f"PASS  {version or 'declarations agree'}",))
    return StepResult(
        "Version",
        False,
        ("FAIL  the version declarations disagree",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_licensing(ctx: Context) -> StepResult:
    """Step 2: the licensing declarations and coverage pass."""
    script = ctx.root / "scripts" / "check_licensing.py"
    command = (ctx.python, str(script), "--root", str(ctx.root))
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        match = re.search(r"(\d+) file\(s\) accounted for", result.stdout)
        summary = f"{match.group(1)} files" if match else "declarations and coverage pass"
        return StepResult("Licensing", True, (f"PASS  {summary}",))
    return StepResult(
        "Licensing",
        False,
        ("FAIL  the licensing declarations or coverage check failed",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_tests(ctx: Context) -> StepResult:
    """Step 3: the complete test suite passes."""
    command = (ctx.python, "-m", "pytest", "-p", "no:cacheprovider")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        match = re.search(r"(\d+) passed", result.stdout + "\n" + result.stderr)
        summary = f"{match.group(1)} passed" if match else "test suite passed"
        return StepResult("Tests", True, (f"PASS  {summary}",))
    return StepResult(
        "Tests",
        False,
        ("FAIL  the test suite failed",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_labs(ctx: Context) -> StepResult:
    """Step 4: the offline lab self-check passes."""
    command = (ctx.python, "-m", "agentsec", "labs", "check")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    combined = result.stdout + "\n" + result.stderr
    if result.returncode == 0:
        match = re.search(r"(\d+)\s*/\s*(\d+) labs passed", result.stdout)
        summary = match.group(0) if match else "lab self-check passed"
        return StepResult("Labs", True, (f"PASS  {summary}",))
    return StepResult(
        "Labs",
        False,
        ("FAIL  the lab self-check failed",) + _indent(_tail(combined)),
    )


def step_ruff(ctx: Context) -> StepResult:
    """Step 5: Ruff reports no findings."""
    command = ("ruff", "check", "src", "tests", "scripts")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        return StepResult("Ruff", True, ("PASS",))
    return StepResult(
        "Ruff",
        False,
        ("FAIL  Ruff reported findings",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_mypy(ctx: Context) -> StepResult:
    """Step 6: mypy reports no issues."""
    command = (ctx.python, "-m", "mypy")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        return StepResult("Mypy", True, ("PASS",))
    return StepResult(
        "Mypy",
        False,
        ("FAIL  mypy reported issues",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_mkdocs(ctx: Context) -> StepResult:
    """Step 7: the strict MkDocs build succeeds (output kept outside the repo)."""
    site = ctx.scratch / "site"
    command = (
        ctx.python,
        "-m",
        "mkdocs",
        "build",
        "--strict",
        "-d",
        str(site),
    )
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        return StepResult("MkDocs", True, ("PASS",))
    return StepResult(
        "MkDocs",
        False,
        ("FAIL  the strict documentation build failed",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


# --------------------------------------------------------------------------
# Steps 8-10: the release gate and the two drift checks that reuse it.
# --------------------------------------------------------------------------


def step_release_gate(ctx: Context) -> StepResult:
    """Step 8: run the release gate once and capture its JSON report.

    The report is written to the scratch directory (outside the repository) so
    steps 9 and 10 can reuse it without running the gate again.
    """
    script = ctx.root / "scripts" / "release_check.py"
    command = (ctx.python, str(script), "--root", str(ctx.root), "--json")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)

    report = None
    problem = ""
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        problem = f"the gate did not emit valid JSON: {exc}"
    else:
        if isinstance(parsed, dict):
            report = parsed
        else:
            problem = "the gate report is not a JSON object"

    if result.returncode not in (0, 1):
        return StepResult(
            "Release gate",
            False,
            (f"FAIL  the release gate exited {result.returncode}",)
            + _indent(_tail(result.stdout + "\n" + result.stderr)),
        )
    if report is None:
        return StepResult(
            "Release gate",
            False,
            (f"FAIL  {problem or 'no report'}",)
            + _indent(_tail(result.stdout + "\n" + result.stderr)),
        )

    # The report is valid JSON: capture it for the two drift steps to reuse.
    (ctx.scratch / "release-report.json").write_text(
        json.dumps(report), encoding="utf-8"
    )

    classification = report.get("classification")
    blockers = report.get("blockers")
    warnings = report.get("warnings")
    # Structured data for the JSON report; the human-readable lines are built
    # from the same values, so the two views cannot drift apart.
    info = {
        "target_version": report.get("target_version"),
        "classification": classification,
        "blockers": blockers if isinstance(blockers, list) else [],
        "warnings": warnings if isinstance(warnings, list) else [],
    }
    if classification == NOT_READY or (isinstance(blockers, list) and blockers):
        lines = [
            f"FAIL  {classification or 'unknown classification'}",
            f"      blockers: {blockers if isinstance(blockers, list) else '(unavailable)'}",
            f"      warnings: {_fmt_set(warnings)}",
        ]
        return StepResult("Release gate", False, tuple(lines), info)
    lines = [
        f"PASS  {classification}",
        f"      blockers: {blockers if isinstance(blockers, list) else '[]'}",
        f"      warnings: {_fmt_set(warnings)}",
    ]
    return StepResult("Release gate", True, tuple(lines), info)


def _step_drift(
    ctx: Context, name: str, script_name: str, success_line: str, fail_line: str
) -> StepResult:
    """Run one drift checker against the captured release-gate report."""
    script = ctx.root / "scripts" / script_name
    report = ctx.scratch / "release-report.json"
    command = (
        ctx.python,
        str(script),
        "--root",
        str(ctx.root),
        "--gate-report",
        str(report),
    )
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        return StepResult(name, True, (f"PASS  {success_line}",))
    return StepResult(
        name,
        False,
        (f"FAIL  {fail_line}",)
        + _indent(_tail(result.stdout + "\n" + result.stderr)),
    )


def step_warning_drift(ctx: Context) -> StepResult:
    """Step 9: the accepted-warning policy, docs and gate agree."""
    return _step_drift(
        ctx,
        "Warning drift",
        "check_warning_drift.py",
        "policy = documentation = gate",
        "the accepted-warning surfaces disagree",
    )


def step_manifest_drift(ctx: Context) -> StepResult:
    """Step 10: the release manifest and the repository state agree."""
    return _step_drift(
        ctx,
        "Release manifest",
        "check_release_manifest.py",
        "manifest = repository state",
        "the release manifest and the repository state disagree",
    )


# --------------------------------------------------------------------------
# Step 11: the read-only Git/tag invariant.
# --------------------------------------------------------------------------


def step_git_tags(ctx: Context) -> StepResult:
    """Step 11: ``v0.0.1`` exists and ``v0.1.0`` does not."""
    command = ("git", "-C", str(ctx.root), "tag")
    result = ctx.run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode != 0:
        return StepResult(
            "Git/tag state",
            False,
            ("FAIL  could not read the tag list",)
            + _indent(_tail(result.stderr)),
        )
    tags = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    lines: list[str] = []
    ok = True
    if PRESENT_TAG in tags:
        lines.append(f"PASS  {PRESENT_TAG} exists")
    else:
        lines.append(f"FAIL  {PRESENT_TAG} is missing")
        ok = False
    if ABSENT_TAG not in tags:
        lines.append(f"PASS  {ABSENT_TAG} absent")
    else:
        lines.append(f"FAIL  {ABSENT_TAG} already exists")
        ok = False
    return StepResult("Git/tag state", ok, tuple(lines))


#: The ordered steps, excluding the final result banner (step 12).
CHECKS = (
    step_version,
    step_licensing,
    step_tests,
    step_labs,
    step_ruff,
    step_mypy,
    step_mkdocs,
    step_release_gate,
    step_warning_drift,
    step_manifest_drift,
    step_git_tags,
)


def run_checks(ctx: Context) -> list[StepResult]:
    """Run every step in order, without stopping at the first failure."""
    return [check(ctx) for check in CHECKS]


def format_report(
    results: list[StepResult], *, ok: bool, summary: bool = False
) -> str:
    """Render the sectioned report with an unambiguous final status.

    In ``summary`` mode only failing steps (and the final banner) are printed;
    hidden passing steps keep the exit status authoritative.
    """
    lines: list[str] = []
    if not summary:
        lines.extend([BAR, TITLE, BAR, ""])
    for index, result in enumerate(results, 1):
        if summary and result.ok:
            continue
        lines.append(f"[{index}/{TOTAL_STEPS}] {result.name}")
        lines.extend(result.lines)
        lines.append("")

    if not ok:
        failing = [result.name for result in results if not result.ok]
        lines.append("FAILURES")
        lines.append("-" * len("FAILURES"))
        for name in failing:
            lines.append(f"- {name}")
        lines.append("")

    lines.extend(
        [
            BAR,
            "RESULT: READY FOR OWNER REVIEW" if ok else "RESULT: NOT READY",
            BAR,
            "",
        ]
    )
    lines.append("No commit, push, tag, or publication was performed.")
    if ok:
        lines.append(
            "A successful validation means the repository is ready for owner "
            "review."
        )
        lines.append("It does not authorize or perform the release.")
    return "\n".join(lines)


def build_json_report(
    results: list[StepResult], *, ok: bool, root: Path | None = None
) -> dict:
    """Build the deterministic machine-readable pre-tag report.

    The report is derived only from the same ``StepResult`` objects the human
    output uses, plus the release gate's captured report. It therefore contains
    no timestamps, no absolute paths and no environment-dependent values, and it
    is stable across runs given the same repository state.
    """
    checks = [
        {
            "name": result.name,
            "status": "PASS" if result.ok else "FAIL",
            # The exact lines the human report prints for this step.
            "details": list(result.lines),
        }
        for result in results
    ]
    # The human report numbers its sections ``[i/12]``; the twelfth is the final
    # result banner. Represent it as a check so the machine view has the same
    # twelve entries in the same order.
    checks.append(
        {
            "name": "Final result",
            "status": "PASS" if ok else "FAIL",
            "details": [f"RESULT: {READY_FOR_OWNER if ok else NOT_READY}"],
        }
    )

    # The release gate is the only step that records structured data. Reuse it
    # rather than re-deriving (or re-running) anything.
    gate_info = next((result.info for result in results if result.info), {}) or {}

    target_version = gate_info.get("target_version")
    if not target_version and root is not None:
        target_version = read_version(root)

    raw_warnings = gate_info.get("warnings")
    warnings = (
        # Numeric sort so W7 precedes W12 regardless of the gate's raw order.
        [str(item) for item in sorted(raw_warnings, key=_warning_sort_key)]
        if isinstance(raw_warnings, list)
        else []
    )

    raw_blockers = gate_info.get("blockers")
    blockers = list(raw_blockers) if isinstance(raw_blockers, list) else []

    passed = sum(1 for check in checks if check["status"] == "PASS")
    return {
        "schema_version": SCHEMA_VERSION,
        "result": READY_FOR_OWNER if ok else NOT_READY,
        "success": bool(ok),
        "target_version": target_version,
        "classification": gate_info.get("classification"),
        "blockers": blockers,
        "warnings": warnings,
        "checks": checks,
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": len(checks) - passed,
    }


# --------------------------------------------------------------------------
# Tamper-evident attestation
#
# The report is bound to the exact repository state that produced it with two
# SHA-256 digests computed from repository content and the report itself. This
# is integrity evidence, not a signature: it detects modification but makes no
# claim about who generated the report.
# --------------------------------------------------------------------------


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(payload) -> bytes:
    """Canonical JSON bytes for hashing: sorted keys, no insignificant space.

    ``ensure_ascii`` keeps the encoding byte-identical across platforms, and
    ``sort_keys`` removes any dependence on dict insertion order.
    """
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def repository_state_files(root: Path, *, run=run_command) -> list[str]:
    """List the repository content set, in deterministic path order.

    Reuses Git's authoritative working-tree inventory
    (``git ls-files --cached --others --exclude-standard``): every tracked file
    plus every untracked-but-not-ignored file, which is the same content set the
    licensing check accounts for. ``.git`` metadata and ignored/generated
    content (caches, ``site/``, ``dist/``, ``build/``, runtime output) are
    therefore excluded by construction. Paths are returned globally sorted so
    the digest is identical on every machine and every run.
    """
    command = (
        "git",
        "-C",
        str(root),
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
    )
    result = run(command, cwd=root, env=None)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return sorted({name for name in result.stdout.split("\0") if name})


def repository_state_digest(root: Path, *, run=run_command) -> str:
    """SHA-256 over ``relative_path + NUL + file_bytes`` for every content file."""
    digest = hashlib.sha256()
    for relative in repository_state_files(root, run=run):
        path = root / relative
        if not path.is_file():
            # A tracked-but-deleted file still changes the digest (its bytes are
            # absent here); it is not silently normalised away.
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def report_payload(report: dict) -> dict:
    """The signed/attested report payload: everything except its envelopes.

    Both the ``attestation`` and the optional ``signature`` objects are
    *envelopes* around the report, not part of the report's own evidence: the
    attestation must not hash itself, and a signature must not change the
    payload it signs. Excluding both keeps the payload stable before and after a
    signature is attached.
    """
    return {
        key: value
        for key, value in report.items()
        if key not in (ATTESTATION_KEY, SIGNATURE_KEY)
    }


def report_payload_bytes(report: dict) -> bytes:
    """The exact bytes hashed by the attestation and signed by the owner.

    Canonical JSON (sorted keys, no insignificant whitespace, ASCII-escaped) of
    the report with its ``attestation`` and ``signature`` envelopes removed.
    This is the deterministic signing input: terminal output, arbitrary
    temporary bytes and the repository itself are never signed.
    """
    return canonical_json(report_payload(report))


def report_payload_digest(report: dict) -> str:
    """SHA-256 of the report's canonical payload (its two envelopes excluded)."""
    return _sha256_hex(report_payload_bytes(report))


def build_attestation(report: dict, root: Path, *, run=run_command) -> dict:
    """Build the attestation object for ``report`` against ``root``."""
    return {
        "algorithm": ATTESTATION_ALGORITHM,
        "method": ATTESTATION_METHOD,
        "repository_state_sha256": repository_state_digest(root, run=run),
        "report_payload_sha256": report_payload_digest(report),
    }


def _attestation_problems(data: dict, root: Path, *, run=run_command) -> list[str]:
    """Every reason the report's SHA-256 attestation is invalid ([] if valid)."""
    attestation = data.get(ATTESTATION_KEY)
    if not isinstance(attestation, dict):
        return ["report has no attestation object"]

    problems: list[str] = []
    if attestation.get("algorithm") != ATTESTATION_ALGORITHM:
        problems.append(
            f"unsupported attestation algorithm: {attestation.get('algorithm')!r}"
        )
    if attestation.get("method") != ATTESTATION_METHOD:
        problems.append(
            f"unsupported attestation method: {attestation.get('method')!r}"
        )

    recorded_report = attestation.get("report_payload_sha256")
    recorded_repo = attestation.get("repository_state_sha256")
    report_hash_ok = isinstance(recorded_report, str) and bool(
        _HEX_DIGEST.match(recorded_report)
    )
    repo_hash_ok = isinstance(recorded_repo, str) and bool(
        _HEX_DIGEST.match(recorded_repo)
    )
    if not report_hash_ok:
        problems.append(
            f"malformed report_payload_sha256 in attestation: {recorded_report!r}"
        )
    if not repo_hash_ok:
        problems.append(
            f"malformed repository_state_sha256 in attestation: {recorded_repo!r}"
        )

    if report_hash_ok and recorded_report != report_payload_digest(data):
        problems.append(
            "report payload hash mismatch: the report fields were modified"
        )

    try:
        actual_repo = repository_state_digest(root, run=run)
    except RuntimeError as exc:
        problems.append(f"cannot compute the repository state digest: {exc}")
    else:
        if repo_hash_ok and recorded_repo != actual_repo:
            problems.append(
                "repository state hash mismatch: the repository files changed"
            )
    return problems


# --------------------------------------------------------------------------
# Owner-controlled signing
#
# The signing input is exactly the canonical report payload (the bytes
# ``report_payload_sha256`` covers); the cryptography is delegated to the
# external OpenSSL 3.x tool through an injectable signer, so no cryptographic
# dependency is added and no RSA/ECDSA/EdDSA mathematics is hand-rolled. The
# signature establishes possession/control of a key, not personal identity.
# --------------------------------------------------------------------------


class SignatureError(Exception):
    """The external signing tool is unavailable or the operation failed."""


class OpenSSLEd25519Signer:
    """Ed25519 sign/verify via the external OpenSSL 3.x tool.

    Only argument arrays are executed (never a shell string), every binary
    artefact — the payload, the signature and the DER public key — is written to
    a private temporary directory that is removed afterwards, and no key material
    is ever written to standard output, standard error or the report. The class
    is injectable so tests can substitute a fake signer without running OpenSSL.
    """

    algorithm = SIGNATURE_ALGORITHM
    encoding = SIGNATURE_ENCODING
    key_id_method = SIGNATURE_KEY_ID_METHOD

    def __init__(self, *, executable: str = "openssl", run=run_command) -> None:
        self.executable = executable
        self._run = run

    def check_available(self) -> None:
        """Raise :class:`SignatureError` if the signing tool is not on PATH."""
        if shutil.which(self.executable) is None:
            raise SignatureError(
                f"the signing tool {self.executable!r} is not available on PATH; "
                "install OpenSSL 3.x to sign or verify report signatures"
            )

    def _run_tool(self, argv, *, cwd: Path):
        result = self._run(tuple(str(item) for item in argv), cwd=cwd, env=None)
        if result.returncode != 0:
            detail = _tail(result.stderr or result.stdout)
            raise SignatureError(
                f"{self.executable} failed ({result.returncode}): {detail}"
            )
        return result

    def _public_key_der(self, key, *, private: bool, cwd: Path) -> bytes:
        """DER-encode a key's SubjectPublicKeyInfo to a temp file and read it."""
        der_path = cwd / "public.der"
        argv = [self.executable, "pkey"]
        if not private:
            argv.append("-pubin")
        argv += [
            "-in",
            str(key),
            "-pubout",
            "-outform",
            "DER",
            "-out",
            str(der_path),
        ]
        self._run_tool(argv, cwd=cwd)
        return der_path.read_bytes()

    def key_id_from_public_key(self, public_key: Path) -> str:
        """Deterministic fingerprint: SHA-256 of the DER public key."""
        self.check_available()
        with tempfile.TemporaryDirectory(prefix="agentsec-signature-") as tmp:
            return _sha256_hex(
                self._public_key_der(public_key, private=False, cwd=Path(tmp))
            )

    def sign(self, data: bytes, private_key: Path) -> tuple[str, bytes]:
        """Sign ``data`` and return ``(key_id, signature_bytes)``."""
        self.check_available()
        with tempfile.TemporaryDirectory(prefix="agentsec-signature-") as tmp:
            cwd = Path(tmp)
            payload = cwd / "payload.bin"
            payload.write_bytes(data)
            signature = cwd / "signature.bin"
            self._run_tool(
                (
                    self.executable,
                    "pkeyutl",
                    "-sign",
                    "-inkey",
                    str(private_key),
                    "-rawin",
                    "-in",
                    str(payload),
                    "-out",
                    str(signature),
                ),
                cwd=cwd,
            )
            key_id = _sha256_hex(
                self._public_key_der(private_key, private=True, cwd=cwd)
            )
            return key_id, signature.read_bytes()

    def verify(self, data: bytes, signature: bytes, public_key: Path) -> bool:
        """Return ``True`` only if ``signature`` is valid for ``data``."""
        self.check_available()
        with tempfile.TemporaryDirectory(prefix="agentsec-signature-") as tmp:
            cwd = Path(tmp)
            payload = cwd / "payload.bin"
            payload.write_bytes(data)
            signature_file = cwd / "signature.bin"
            signature_file.write_bytes(signature)
            # Ed25519 verification returns a non-zero status for a bad
            # signature; the public key is checked separately, so a failure here
            # is a signature failure rather than a tool failure.
            result = self._run(
                (
                    self.executable,
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(public_key),
                    "-rawin",
                    "-in",
                    str(payload),
                    "-sigfile",
                    str(signature_file),
                ),
                cwd=cwd,
                env=None,
            )
            return result.returncode == 0


def _make_signer(signer, run):
    return OpenSSLEd25519Signer(run=run) if signer is None else signer


def build_signature_object(
    report: dict, private_key, *, run=run_command, signer=None
) -> dict:
    """Sign the report payload and return its ``signature`` envelope.

    Raises :class:`SignatureError` if the tool is unavailable or the key cannot
    be used. The private key is read only by the signer; no key material is
    placed in the returned object (only its public fingerprint).
    """
    signer = _make_signer(signer, run)
    signer.check_available()
    key_id, signature = signer.sign(report_payload_bytes(report), Path(private_key))
    return {
        "algorithm": signer.algorithm,
        "encoding": signer.encoding,
        "key_id_method": signer.key_id_method,
        "key_id": key_id,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def _signed_output_path(report_path) -> Path:
    """Default signed-report path: the input with a ``.signed`` marker."""
    path = Path(report_path)
    if path.suffix == ".json":
        return path.with_suffix(".signed.json")
    return path.with_name(path.name + ".signed.json")


def sign_report(
    report_path,
    output_path,
    private_key,
    *,
    root: Path,
    run=run_command,
    signer=None,
) -> list[str]:
    """Sign an archived JSON report; return problems ([] on success).

    The report's existing SHA-256 attestation is verified first and signing is
    refused when it is already invalid. The signed report is written to
    ``output_path`` (which may equal the input only when the caller chose it
    explicitly); no repository file and no Git state is touched.
    """
    path = Path(report_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"cannot read report {path}: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"report is not valid JSON: {exc}"]
    if not isinstance(data, dict):
        return ["report is not a JSON object"]

    attestation_problems = _attestation_problems(data, root, run=run)
    if attestation_problems:
        return [
            "the report's SHA-256 attestation is not valid; refusing to sign",
            *attestation_problems,
        ]

    try:
        data[SIGNATURE_KEY] = build_signature_object(
            data, private_key, run=run, signer=signer
        )
    except SignatureError as exc:
        return [f"cannot sign the report: {exc}"]

    try:
        Path(output_path).write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        return [f"cannot write signed report {output_path}: {exc}"]
    return []


def _signature_evidence(data: dict, public_key, *, run, signer) -> tuple[str, str, list[str]]:
    """Return ``(state, message, problems)`` for the report's signature."""
    signature = data.get(SIGNATURE_KEY)
    if signature is None:
        if public_key is not None:
            message = "report has no signature object to verify"
            return SIGNATURE_INVALID, message, [
                "report has no signature object to verify with the supplied "
                "public key"
            ]
        return SIGNATURE_ABSENT, "", []
    if not isinstance(signature, dict):
        return SIGNATURE_INVALID, "signature object is malformed", [
            "signature object is malformed"
        ]

    algorithm = signature.get("algorithm")
    if algorithm not in SUPPORTED_SIGNATURE_ALGORITHMS:
        message = f"unsupported signature algorithm: {algorithm!r}"
        return SIGNATURE_INVALID, message, [message]
    if signature.get("encoding") != SIGNATURE_ENCODING:
        message = f"unsupported signature encoding: {signature.get('encoding')!r}"
        return SIGNATURE_INVALID, message, [message]
    key_id = signature.get("key_id")
    if not (isinstance(key_id, str) and _HEX_DIGEST.match(key_id)):
        message = f"malformed signature key_id: {key_id!r}"
        return SIGNATURE_INVALID, message, [message]
    recorded = signature.get("signature")
    if not isinstance(recorded, str):
        return SIGNATURE_INVALID, "signature is not a string", [
            "malformed signature: the signature is not a string"
        ]
    try:
        signature_bytes = base64.b64decode(recorded, validate=True)
    except ValueError:
        return SIGNATURE_INVALID, "signature is not valid base64", [
            "malformed signature encoding: not valid base64"
        ]

    if public_key is None:
        return SIGNATURE_UNVERIFIED, (
            "signature present but not verified (no --public-key supplied)"
        ), []

    signer = _make_signer(signer, run)
    try:
        signer.check_available()
        actual_key_id = signer.key_id_from_public_key(Path(public_key))
    except SignatureError as exc:
        message = f"cannot use the public key: {exc}"
        return SIGNATURE_INVALID, message, [message]

    if actual_key_id != key_id:
        message = "signature was made with a different key"
        return SIGNATURE_INVALID, message, [
            "signature key_id mismatch: the report records key "
            f"{key_id} but the supplied public key is {actual_key_id}"
        ]

    try:
        valid = signer.verify(
            report_payload_bytes(data), signature_bytes, Path(public_key)
        )
    except SignatureError as exc:
        message = f"signature verification could not run: {exc}"
        return SIGNATURE_INVALID, message, [message]

    if valid:
        return SIGNATURE_VERIFIED, f"report signature verified (key {key_id})", []
    return SIGNATURE_INVALID, "signature does not match the report", [
        "signature does not match the report content: the report or the "
        "signature was modified"
    ]


@dataclass(frozen=True)
class Verification:
    """The outcome of checking an archived report.

    ``problems`` are SHA-256 integrity failures; ``signature_problems`` are
    signature failures. The two are kept apart so the caller can distinguish
    "integrity verified", "signature absent", "signature present but not
    verified", "signature verified" and "signature invalid".
    """

    problems: list[str]
    signature_state: str
    signature_message: str
    signature_problems: list[str]


def verify_report_evidence(
    report_path,
    root: Path,
    *,
    run=run_command,
    public_key=None,
    signer=None,
) -> Verification:
    """Verify an archived report's attestation and (optionally) its signature.

    Read-only: it reads the report and the repository, runs no check, creates no
    temporary file and modifies nothing.
    """
    path = Path(report_path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return Verification(
            [f"cannot read report {path}: {exc}"], SIGNATURE_ABSENT, "", []
        )
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return Verification(
            [f"report is not valid JSON: {exc}"], SIGNATURE_ABSENT, "", []
        )
    if not isinstance(data, dict):
        return Verification(["report is not a JSON object"], SIGNATURE_ABSENT, "", [])

    problems = _attestation_problems(data, root, run=run)
    state, message, signature_problems = _signature_evidence(
        data, public_key, run=run, signer=signer
    )
    return Verification(problems, state, message, signature_problems)


def verify_report(report_path, root: Path, *, run=run_command) -> list[str]:
    """Return every reason ``report_path`` is not valid for ``root`` ([] if valid).

    Compatibility wrapper around :func:`verify_report_evidence` for callers that
    only need the integrity problems; it makes no signature claim.
    """
    evidence = verify_report_evidence(report_path, root, run=run)
    return [*evidence.problems, *evidence.signature_problems]


def main(argv: list[str] | None = None, *, run=run_command, signer=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the v0.1.0 owner pre-tag validation sequence (read-only)."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to check (default: the parent of this script)",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--summary",
        action="store_true",
        help="print only failing steps and the final result",
    )
    output.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="print a single deterministic JSON report on stdout",
    )
    output.add_argument(
        "--verify-report",
        type=Path,
        default=None,
        metavar="REPORT",
        help=(
            "verify an archived JSON report against the current repository "
            "state without running any check (read-only); add --public-key to "
            "also verify an owner signature"
        ),
    )
    output.add_argument(
        "--sign-report",
        type=Path,
        default=None,
        metavar="REPORT",
        help=(
            "sign an archived JSON report with --private-key (requires a "
            "valid SHA-256 attestation; writes a signed copy, read-only)"
        ),
    )
    parser.add_argument(
        "--public-key",
        type=Path,
        default=None,
        metavar="PATH",
        help="Ed25519 public key (PEM) used to verify a report signature",
    )
    parser.add_argument(
        "--private-key",
        type=Path,
        default=None,
        metavar="PATH",
        help="Ed25519 private key (PEM) used by --sign-report",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "where --sign-report writes the signed report (default: the input "
            "with a .signed.json suffix)"
        ),
    )
    args = parser.parse_args(argv)

    # Reject nonsensical option combinations early, the way argparse would.
    if args.sign_report is not None:
        if args.private_key is None:
            parser.error("--sign-report requires --private-key")
        if args.public_key is not None:
            parser.error("--public-key is only valid with --verify-report")
    else:
        if args.private_key is not None:
            parser.error("--private-key is only valid with --sign-report")
        if args.output is not None:
            parser.error("--output is only valid with --sign-report")
    if args.public_key is not None and args.verify_report is None:
        parser.error("--public-key is only valid with --verify-report")

    root = args.root.resolve()

    if args.sign_report is not None:
        output_path = args.output
        if output_path is None:
            output_path = _signed_output_path(args.sign_report)
            if output_path.resolve() == args.sign_report.resolve():
                parser.error(
                    "cannot derive an output path distinct from the input; "
                    "pass --output explicitly"
                )
        problems = sign_report(
            args.sign_report,
            output_path,
            args.private_key,
            root=root,
            run=run,
            signer=signer,
        )
        if problems:
            print("FAIL  the report could not be signed", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        signed = json.loads(Path(output_path).read_text(encoding="utf-8"))
        envelope = signed.get(SIGNATURE_KEY, {})
        print(f"PASS  signed report written to {output_path}")
        print(f"      algorithm: {envelope.get('algorithm')}")
        print(f"      key id: {envelope.get('key_id')} ({envelope.get('key_id_method')})")
        return 0

    if args.verify_report is not None:
        # Verification is read-only and self-contained: no checks, no gate, no
        # scratch directory, no side effects.
        evidence = verify_report_evidence(
            args.verify_report,
            root,
            run=run,
            public_key=args.public_key,
            signer=signer,
        )
        if evidence.problems:
            print("FAIL  report attestation could not be verified", file=sys.stderr)
            for problem in evidence.problems:
                print(f"  - {problem}", file=sys.stderr)
        else:
            print(
                "PASS  report attestation is valid for the current repository "
                "state"
            )
        if evidence.signature_state == SIGNATURE_VERIFIED:
            print(f"PASS  {evidence.signature_message}")
        elif evidence.signature_state == SIGNATURE_UNVERIFIED:
            print(f"WARN  {evidence.signature_message}")
        elif evidence.signature_state == SIGNATURE_INVALID:
            print("FAIL  report signature could not be verified", file=sys.stderr)
            for problem in evidence.signature_problems:
                print(f"  - {problem}", file=sys.stderr)
        if evidence.problems or evidence.signature_problems:
            return 1
        return 0

    scratch = Path(tempfile.mkdtemp(prefix="agentsec-pre-tag-"))
    try:
        ctx = Context(
            root=root,
            python=sys.executable,
            env=_child_env(root),
            scratch=scratch,
            run=run,
        )
        results = run_checks(ctx)
    finally:
        # The captured report and the MkDocs site both live here; remove them.
        shutil.rmtree(scratch, ignore_errors=True)

    ok = all(result.ok for result in results)
    if args.as_json:
        # stdout must stay machine-parseable: emit only the JSON object.
        report = build_json_report(results, ok=ok, root=root)
        try:
            report[ATTESTATION_KEY] = build_attestation(report, root, run=run)
        except RuntimeError as exc:
            print(
                f"cannot compute the repository-state attestation: {exc}",
                file=sys.stderr,
            )
            return 1
        print(json.dumps(report, indent=2))
    else:
        print(format_report(results, ok=ok, summary=args.summary))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
