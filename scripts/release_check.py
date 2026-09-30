"""Run the established release gates and report whether v0.0.1 is ready.

This is a **read-only release-preparation command**, not a release tool. It does
not tag, commit, push, stage or publish anything, and it never edits a file in
the repository. It runs the checks that the Phase 20 audits already established,
in one deterministic pass, and prints:

* a human-readable report (the default), and
* a machine-readable JSON summary (``--json``) suitable for CI.

The gates
---------
    tests             python -m pytest
    labs              python -m agentsec labs check
    mkdocs            python -m mkdocs build --strict
    licensing         scripts/check_licensing.py   (declarations + coverage)
    version           scripts/check_version.py     (version consistency)
    readme            README.md relative links and anchors
    self_containment  packaged trace schema + a rebuilt wheel
    hygiene           secrets / artefacts / tracked-ignored files
    git_state         branch, HEAD, tags, staged, untracked

Each gate is ``PASS``, ``WARN`` or ``FAIL``. Any ``FAIL`` is a release blocker
and yields **NOT READY**; otherwise remaining ``WARN``s and the standing
warnings ``W6``–``W13`` (the terminology recorded in ``research/31``–``research/36``)
yield **READY WITH WARNINGS**; with none of either, **READY**.

Scope and limits
----------------
The runner *orchestrates* the guards; it does not re-implement their logic. The
version and licensing checks are delegated to their own scripts, and the tests
and lab self-check delegate to their own commands. It uses only the standard
library for its own work, runs no command that changes the repository, and keeps
every build artefact in a temporary directory outside the checkout. The only
network access is whatever an existing build command inherently needs: rebuilding
the wheel exercises pip's build isolation, and when that is unavailable the
self-containment gate reports ``WARN`` rather than silently skipping.

Usage::

    py scripts/release_check.py
    py scripts/release_check.py --json
    py scripts/release_check.py --root <repository>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

READY = "READY"
READY_WITH_WARNINGS = "READY WITH WARNINGS"
NOT_READY = "NOT READY"

#: A release gate may legitimately take a while (the test suite, a wheel build).
DEFAULT_TIMEOUT = 1200

#: How much captured output to quote when a gate fails.
TAIL_LENGTH = 1500


@dataclass(frozen=True)
class CommandResult:
    """The outcome of one external command."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GateResult:
    """One release gate and its outcome."""

    gate: str
    status: str
    summary: str
    detail: str = ""
    command: tuple[str, ...] | None = None
    exit_code: int | None = None
    inspect: str = ""


@dataclass(frozen=True)
class Warning:
    """One known, non-blocking release warning, in the audits' terminology."""

    id: str
    summary: str


@dataclass
class Context:
    """Everything a gate needs: the root, a scratch dir and the interpreter."""

    root: Path
    scratch: Path
    python: str
    env: dict


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
    return CommandResult(tuple(str(item) for item in argv), proc.returncode, proc.stdout, proc.stderr)


def _child_env(root: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    return env


def _tail(text: str, length: int = TAIL_LENGTH) -> str:
    text = text.strip()
    return text if len(text) <= length else "…" + text[-length:]


def _last_nonempty(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-1].strip() if lines else ""


# --------------------------------------------------------------------------
# Git helpers (read-only).
# --------------------------------------------------------------------------


def _git(ctx: Context, run, *args: str) -> str | None:
    result = run(("git", "-C", str(ctx.root), *args), cwd=ctx.root, env=ctx.env)
    if result.returncode != 0:
        return None
    return result.stdout


def _git_lines(ctx: Context, run, *args: str) -> list[str]:
    output = _git(ctx, run, *args)
    if output is None:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Gates.
# --------------------------------------------------------------------------


def gate_tests(ctx: Context, run) -> GateResult:
    # No ``-q`` here: the project's own ``addopts`` already sets it, and a second
    # ``-q`` would suppress the summary line this gate reads the count from.
    command = (ctx.python, "-m", "pytest", "-p", "no:cacheprovider")
    result = run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        match = re.search(r"(\d+) passed", result.stdout + "\n" + result.stderr)
        summary = f"{match.group(1)} tests passed" if match else "test suite passed"
        return GateResult("tests", PASS, summary, command=command, exit_code=0)
    return GateResult(
        "tests",
        FAIL,
        "the test suite failed",
        detail=_tail(result.stdout + "\n" + result.stderr),
        command=command,
        exit_code=result.returncode,
        inspect="Run `PYTHONPATH=src python -m pytest` and fix the failing tests.",
    )


def gate_labs(ctx: Context, run) -> GateResult:
    command = (ctx.python, "-m", "agentsec", "labs", "check")
    result = run(command, cwd=ctx.root, env=ctx.env)
    combined = result.stdout + "\n" + result.stderr
    if result.returncode == 0:
        match = re.search(r"(\d+)\s*/\s*(\d+) labs passed", result.stdout)
        summary = f"{match.group(0)}" if match else "lab self-check passed"
        return GateResult("labs", PASS, summary, command=command, exit_code=0)
    return GateResult(
        "labs",
        FAIL,
        "the lab self-check failed",
        detail=_tail(combined),
        command=command,
        exit_code=result.returncode,
        inspect="Run `PYTHONPATH=src python -m agentsec labs check` and inspect the failing lab.",
    )


def gate_mkdocs(ctx: Context, run) -> GateResult:
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
    result = run(command, cwd=ctx.root, env=ctx.env)
    combined = result.stdout + "\n" + result.stderr
    if result.returncode == 0:
        return GateResult("mkdocs", PASS, "strict build succeeded", command=command, exit_code=0)
    if re.search(r"No module named .{0,3}mkdocs", combined):
        return GateResult(
            "mkdocs",
            WARN,
            "mkdocs is not installed, so the documentation build was not verified",
            detail=_tail(combined),
            command=command,
            exit_code=result.returncode,
            inspect="Install the docs extra: `pip install -e \".[docs]\"`.",
        )
    return GateResult(
        "mkdocs",
        FAIL,
        "the strict documentation build failed",
        detail=_tail(combined),
        command=command,
        exit_code=result.returncode,
        inspect="Run `python -m mkdocs build --strict` and fix the reported page.",
    )


def gate_licensing(ctx: Context, run) -> GateResult:
    script = ctx.root / "scripts" / "check_licensing.py"
    command = (ctx.python, str(script))
    if not script.is_file():
        return GateResult(
            "licensing",
            FAIL,
            "scripts/check_licensing.py is missing",
            inspect="Restore the licensing guard; it is the release coverage check.",
        )
    result = run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        checks = re.search(r"(\d+)\s*/\s*(\d+) checks passed", result.stdout)
        coverage = re.search(r"(\d+) file\(s\) accounted for \(([^)]*)\)", result.stdout)
        summary = "licensing declarations and coverage pass"
        if checks:
            summary = f"{checks.group(0)}"
        if coverage:
            summary += f"; {coverage.group(1)} files accounted for ({coverage.group(2)})"
        return GateResult("licensing", PASS, summary, command=command, exit_code=0)
    return GateResult(
        "licensing",
        FAIL,
        "the licensing declarations or coverage check failed",
        detail=_tail(result.stdout + "\n" + result.stderr),
        command=command,
        exit_code=result.returncode,
        inspect="Run `python scripts/check_licensing.py` and fix the named declaration or coverage gap.",
    )


def gate_version(ctx: Context, run) -> GateResult:
    script = ctx.root / "scripts" / "check_version.py"
    command = (ctx.python, str(script))
    if not script.is_file():
        return GateResult(
            "version",
            FAIL,
            "scripts/check_version.py is missing",
            inspect="Restore the version guard; it is the release version-consistency check.",
        )
    result = run(command, cwd=ctx.root, env=ctx.env)
    if result.returncode == 0:
        target = read_target_version(ctx.root)
        summary = f"declarations agree on {target}" if target else "version declarations agree"
        return GateResult("version", PASS, summary, command=command, exit_code=0)
    return GateResult(
        "version",
        FAIL,
        "the version declarations disagree",
        detail=_tail(result.stdout + "\n" + result.stderr),
        command=command,
        exit_code=result.returncode,
        inspect="Run `python scripts/check_version.py`; reconcile pyproject.toml, __version__ and CITATION.cff.",
    )


_LINK_RE = re.compile(r"\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^#+ (.+)$", re.M)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", text.strip().lower()).replace(" ", "-")


def check_readme(readme: Path, root: Path) -> tuple[bool, str]:
    """Return ``(ok, detail)`` for the README's relative links and anchors."""
    if not readme.is_file():
        return False, "README.md is missing"
    text = readme.read_text(encoding="utf-8", errors="replace")
    links = _LINK_RE.findall(text)
    relative = [link for link in links if not link.startswith(("http", "#", "mailto"))]
    missing = [link for link in relative if not (root / link.split("#")[0]).exists()]
    anchors = [link for link in links if link.startswith("#")]
    slugs = {_slug(heading) for heading in _HEADING_RE.findall(text)}
    bad_anchors = [link for link in anchors if link[1:] not in slugs]
    detail = f"{len(relative)} relative links and {len(anchors)} anchors"
    if missing:
        detail += f"; missing: {', '.join(missing[:5])}"
    if bad_anchors:
        detail += f"; unresolved anchors: {', '.join(bad_anchors[:5])}"
    return (not missing and not bad_anchors), detail


def gate_readme(ctx: Context, run) -> GateResult:
    ok, detail = check_readme(ctx.root / "README.md", ctx.root)
    if ok:
        return GateResult("readme", PASS, f"all {detail} resolve")
    return GateResult(
        "readme",
        FAIL,
        "README.md has a broken relative reference",
        detail=detail,
        inspect="Fix the named missing link or unresolved anchor in README.md.",
    )


def _build_wheel(ctx: Context, run) -> tuple[Path | None, str]:
    """Build a wheel from a copy of the project outside the repository."""
    copy = ctx.scratch / "proj"
    (copy / "docs").mkdir(parents=True, exist_ok=True)
    (copy / "src").mkdir(parents=True, exist_ok=True)
    shutil.copy(ctx.root / "pyproject.toml", copy / "pyproject.toml")
    for name in ("README.md", "docs/development.md"):
        source = ctx.root / name
        if source.is_file():
            shutil.copy(source, copy / name)
    shutil.copytree(
        ctx.root / "src" / "agentsec",
        copy / "src" / "agentsec",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    dist = ctx.scratch / "dist"
    dist.mkdir(exist_ok=True)
    result = run(
        (ctx.python, "-m", "pip", "wheel", ".", "--no-deps", "-w", str(dist)),
        cwd=copy,
        env=ctx.env,
    )
    if result.returncode != 0:
        return None, _tail(result.stdout + "\n" + result.stderr)
    wheels = sorted(dist.glob("*.whl"))
    if not wheels:
        return None, "pip reported success but produced no wheel"
    return wheels[0], ""


def gate_self_containment(ctx: Context, run) -> GateResult:
    repository_schema = ctx.root / "schemas" / "trace" / "trace_event.v1.schema.json"
    packaged_schema = (
        ctx.root / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json"
    )
    if not packaged_schema.is_file():
        return GateResult(
            "self_containment",
            FAIL,
            "the packaged trace schema is missing",
            detail=f"expected {packaged_schema.relative_to(ctx.root).as_posix()}",
            inspect="Re-run `python scripts/export_trace_schema.py`; the wheel would ship without a schema.",
        )
    if not repository_schema.is_file() or packaged_schema.read_bytes() != repository_schema.read_bytes():
        return GateResult(
            "self_containment",
            FAIL,
            "the packaged schema differs from the repository copy",
            inspect="Run `python scripts/export_trace_schema.py` so both copies match.",
        )

    wheel, problem = _build_wheel(ctx, run)
    if wheel is None:
        return GateResult(
            "self_containment",
            WARN,
            "packaged schema is present and byte-identical; the wheel was not rebuilt here",
            detail=problem,
            inspect="Needs pip build isolation (setuptools); re-run where that is available.",
        )

    with zipfile.ZipFile(wheel) as archive:
        names = [name.replace(os.sep, "/") for name in archive.namelist()]
        schema_name = "agentsec/schemas/trace/trace_event.v1.schema.json"
        if schema_name not in names:
            return GateResult(
                "self_containment",
                FAIL,
                f"the wheel does not contain {schema_name}",
                inspect="Check [tool.setuptools.package-data] and the package layout.",
            )
        if archive.read(schema_name) != repository_schema.read_bytes():
            return GateResult(
                "self_containment",
                FAIL,
                "the wheel's schema is not byte-identical to the repository copy",
                inspect="Run `python scripts/export_trace_schema.py` and rebuild.",
            )
        metadata = _wheel_metadata(archive, names)

    target = read_target_version(ctx.root)
    version = _metadata_field(metadata, "Version")
    if target and version and version != target:
        return GateResult(
            "self_containment",
            FAIL,
            f"the wheel reports version {version!r}, expected {target!r}",
            inspect="The built distribution must carry the authoritative version.",
        )
    tops = sorted({name.split("/")[0] for name in names})
    unwanted = [top for top in tops if top not in {"agentsec"} and not top.endswith(".dist-info")]
    if unwanted:
        return GateResult(
            "self_containment",
            FAIL,
            "the wheel contains repository files it should not",
            detail=f"unexpected top-level entries: {', '.join(unwanted)}",
            inspect="Move non-package files outside src/ or adjust the packaging configuration.",
        )
    return GateResult(
        "self_containment",
        PASS,
        f"wheel rebuilt; schema present and byte-identical; version {version}",
        command=(ctx.python, "-m", "pip", "wheel"),
    )


def _wheel_metadata(archive: zipfile.ZipFile, names: list[str]) -> str:
    for name in names:
        if name.endswith(".dist-info/METADATA"):
            return archive.read(name).decode("utf-8", errors="replace")
    return ""


def _metadata_field(metadata: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}: (.*)$", metadata, re.M)
    return match.group(1).strip() if match else None


# --- hygiene ---------------------------------------------------------------

_EDITOR_ARTIFACT_RE = re.compile(
    r"(^|/)(\.idea|\.vscode|build|dist)/"
    r"|\.(swp|swo|bak|orig|tmp)$|~$"
    r"|(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini)$"
)

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
)

#: Directories scanned for secrets; tests and historical research are excluded
#: so deliberate fixtures and prose are never reported as leaks.
_SECRET_SCAN_ROOTS = ("src", "scripts", "labs", "policies", "configs", "schemas", "docs", ".github")
_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")


def gate_hygiene(ctx: Context, run) -> GateResult:
    findings: list[str] = []

    if (ctx.root / "build").is_dir() or (ctx.root / "dist").is_dir():
        findings.append("a build/ or dist/ directory exists in the repository")

    tracked = _git_lines(ctx, run, "ls-files")
    if tracked:
        for path in tracked:
            if _EDITOR_ARTIFACT_RE.search(path):
                findings.append(f"tracked artefact: {path}")
        ignored_tracked = _git_lines(ctx, run, "ls-files", "-i", "-c", "--exclude-standard")
        for path in ignored_tracked:
            findings.append(f"tracked but git-ignored: {path}")

        for path in tracked:
            if not path.endswith(".py"):
                continue
            if not path.startswith(("src/", "scripts/", "tests/")):
                continue
            try:
                text = (ctx.root / path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            match = _TODO_RE.search(text)
            if match:
                findings.append(f"{match.group(0)} marker in {path}")

        for path in tracked:
            if not path.startswith(_SECRET_SCAN_ROOTS):
                continue
            try:
                text = (ctx.root / path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in _SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(f"secret-shaped value in {path}")
                    break

    if findings:
        return GateResult(
            "hygiene",
            FAIL,
            f"{len(findings)} repository hygiene problem(s)",
            detail="; ".join(findings[:8]),
            inspect="Inspect the named paths; remove secrets and generated artefacts before release.",
        )
    return GateResult("hygiene", PASS, "no secrets, artefacts or tracked-ignored files")


# --- git state -------------------------------------------------------------


def gate_git_state(ctx: Context, run) -> GateResult:
    inside = _git(ctx, run, "rev-parse", "--is-inside-work-tree")
    if inside is None or inside.strip() != "true":
        return GateResult(
            "git_state",
            FAIL,
            "the target is not a Git working tree",
            inspect="Run the gate from inside the repository checkout.",
        )
    head = _git(ctx, run, "rev-parse", "HEAD")
    if head is None:
        return GateResult(
            "git_state",
            FAIL,
            "the repository has no commits yet",
            inspect="Commit the release revision before creating the tag.",
        )
    branch = (_git(ctx, run, "rev-parse", "--abbrev-ref", "HEAD") or "").strip() or "(detached)"
    tags = _git_lines(ctx, run, "tag")
    porcelain = _git_lines(ctx, run, "status", "--porcelain")
    staged = _git_lines(ctx, run, "diff", "--cached", "--name-only")
    untracked = [line[3:] for line in porcelain if line.startswith("??")]
    dirty = len(porcelain) - len(untracked)

    detail = (
        f"branch {branch}, HEAD {head.strip()[:12]}, {len(tags)} tag(s), "
        f"{len(staged)} staged, {dirty} modified, {len(untracked)} untracked"
    )
    if porcelain:
        return GateResult(
            "git_state",
            WARN,
            "the working tree is not clean",
            detail=detail,
            inspect="Expected before a release commit; review `git status` before tagging.",
        )
    return GateResult("git_state", PASS, "working tree is clean", detail=detail)


# --------------------------------------------------------------------------
# Known warnings (the audits' W6–W13 terminology).
# --------------------------------------------------------------------------


def read_target_version(root: Path) -> str | None:
    """The authoritative version, from pyproject.toml. Never hard-coded."""
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except tomllib.TOMLDecodeError:
        return None
    version = data.get("project", {}).get("version")
    return version if isinstance(version, str) else None


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def detect_warnings(ctx: Context, run) -> list[Warning]:
    """Detect the known, non-blocking warnings without inventing new ones."""
    warnings: list[Warning] = []
    tracked = set(_git_lines(ctx, run, "ls-files"))

    citation = _read(ctx.root / "CITATION.cff")
    if citation and not re.search(r"^date-released:", citation, re.M):
        warnings.append(
            Warning("W6", "CITATION.cff has no date-released (add it at release time)")
        )

    if ".freebuff/project-id" in tracked:
        warnings.append(
            Warning("W7", ".freebuff/project-id is tracked and therefore distributed")
        )

    pkg_info = _read(ctx.root / "src" / "agentsec.egg-info" / "PKG-INFO")
    if pkg_info and ("License: TBD" in pkg_info or "Phase A skeleton" in pkg_info):
        warnings.append(
            Warning("W9", "the local editable install metadata is stale (git-ignored)")
        )

    pyproject = _read(ctx.root / "pyproject.toml")
    if pyproject:
        try:
            data = tomllib.loads(pyproject)
        except tomllib.TOMLDecodeError:
            data = {}
        project = data.get("project", {}) if isinstance(data.get("project"), dict) else {}
        license_value = project.get("license")
        legacy_license = isinstance(license_value, dict) and "text" in license_value
        missing = [key for key in ("authors", "classifiers", "keywords", "urls") if key not in project]
        if legacy_license or missing:
            warnings.append(
                Warning("W10", "package metadata is minimal (legacy licence form; missing " + ", ".join(missing) + ")")
            )
        docs = project.get("optional-dependencies", {}).get("docs", []) if isinstance(
            project.get("optional-dependencies", {}), dict
        ) else []
        if any("mkdocs-material" in str(item) for item in docs):
            pinned = any(
                token in str(item)
                for item in docs
                for token in ("==", "!=", "~=", "<")
            )
            if not pinned:
                warnings.append(
                    Warning("W11", "the docs extra leaves mkdocs-material unpinned")
                )

    warnings.append(
        Warning("W12", "human-judgement licensing residuals remain (review research/28–research/36)")
    )

    ignore = _read(ctx.root / ".gitignore")
    manifest = _read(ctx.root / "licensing" / "manifest.toml")
    if "traces/*.jsonl" in ignore or "traces/*.jsonl" in manifest:
        if not (ctx.root / "traces").is_dir():
            warnings.append(
                Warning("W13", "traces/*.jsonl is configured but the traces/ directory does not exist")
            )

    return warnings


# --------------------------------------------------------------------------
# Report assembly and classification.
# --------------------------------------------------------------------------

#: The gates, in execution/report order.
GATES = (
    ("tests", gate_tests),
    ("labs", gate_labs),
    ("mkdocs", gate_mkdocs),
    ("licensing", gate_licensing),
    ("version", gate_version),
    ("readme", gate_readme),
    ("self_containment", gate_self_containment),
    ("hygiene", gate_hygiene),
    ("git_state", gate_git_state),
)


def classify(gates: list[GateResult], warnings: list[Warning]) -> str:
    """READY / READY WITH WARNINGS / NOT READY, per the audits' rules."""
    if any(result.status == FAIL for result in gates):
        return NOT_READY
    if warnings or any(result.status == WARN for result in gates):
        return READY_WITH_WARNINGS
    return READY


def build_report(ctx: Context, run) -> dict:
    """Run every gate and return the full machine-readable report."""
    gate_results = [gate(ctx, run) for _name, gate in GATES]
    warnings = detect_warnings(ctx, run)
    warnings.sort(key=lambda item: item.id)
    classification = classify(gate_results, warnings)

    head = (_git(ctx, run, "rev-parse", "HEAD") or "").strip() or None
    branch = (_git(ctx, run, "rev-parse", "--abbrev-ref", "HEAD") or "").strip() or None
    tags = _git_lines(ctx, run, "tag")

    return {
        "target_version": read_target_version(ctx.root),
        "classification": classification,
        "blockers": [result.gate for result in gate_results if result.status == FAIL],
        "warnings": [warning.id for warning in warnings],
        "gates": {result.gate: result.status for result in gate_results},
        "gate_details": [
            {
                "gate": result.gate,
                "status": result.status,
                "summary": result.summary,
                "detail": result.detail,
                "command": list(result.command) if result.command else None,
                "exit_code": result.exit_code,
                "inspect": result.inspect,
            }
            for result in gate_results
        ],
        "warning_details": [
            {"id": warning.id, "summary": warning.summary} for warning in warnings
        ],
        "repository": {"branch": branch, "head": head, "tags": tags},
    }


def render_human(report: dict) -> str:
    """Render the report as a readable, CI-friendly block of text."""
    lines = ["release gate", "=" * 12, ""]
    for result in report["gate_details"]:
        lines.append(f"  [{result['status']}] {result['gate']:<17} {result['summary']}")
        if result["status"] != PASS and result["detail"]:
            lines.append(f"         {result['detail']}")
    lines.append("")
    if report["warning_details"]:
        lines.append("known warnings (non-blocking):")
        for warning in report["warning_details"]:
            lines.append(f"  [{WARN}] {warning['id']:<4} {warning['summary']}")
        lines.append("")
    if report["blockers"]:
        lines.append("release blockers:")
        for detail in report["gate_details"]:
            if detail["status"] == FAIL:
                lines.append(f"  [{FAIL}] {detail['gate']}: {detail['summary']}")
                if detail["inspect"]:
                    lines.append(f"         inspect: {detail['inspect']}")
        lines.append("")
    repository = report["repository"]
    lines.append(
        "repository: branch {branch}, HEAD {head}, {count} tag(s)".format(
            branch=repository["branch"],
            head=(repository["head"] or "")[:12] or None,
            count=len(repository["tags"]),
        )
    )
    lines.append(f"target version: {report['target_version']}")
    lines.append("")
    lines.append(f"Classification: {report['classification']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None, *, run=run_command) -> int:
    parser = argparse.ArgumentParser(
        description="Run the established release gates and report readiness (read-only).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to check (default: the parent of this script)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable summary instead of the human report",
    )
    args = parser.parse_args(argv)

    scratch = Path(tempfile.mkdtemp(prefix="agentsec-release-check-"))
    try:
        ctx = Context(
            root=args.root.resolve(),
            scratch=scratch,
            python=sys.executable,
            env=_child_env(args.root.resolve()),
        )
        report = build_report(ctx, run)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_human(report))
    return 1 if report["classification"] == NOT_READY else 0


if __name__ == "__main__":
    sys.exit(main())
