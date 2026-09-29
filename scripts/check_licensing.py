"""Check the repository's declared licence metadata for accidental drift.

The project ships two licences — MIT for the software and machine-readable
configuration, CC BY 4.0 for the repository-authored Markdown — and this script
verifies that the files that *declare* that boundary still agree with each
other:

    LICENSE                 the MIT licence text
    LICENSE-DATA            the CC BY 4.0 scope notice and legal code
    pyproject.toml          the distributed package licence metadata
    CITATION.cff            the licence attached to the cited software
    README.md               the reader-facing statement of the boundary
    licensing/manifest.toml the explicit licensing treatment of every path

The first six checks keep those declarations from drifting apart. The last
three check *coverage*: every file present in the repository must be accounted
for by an entry in ``licensing/manifest.toml``, so a newly added file cannot
slip in without somebody recording what its licensing status is.

Usage::

    py scripts/check_licensing.py

Exits ``0`` when every check passes and ``1`` otherwise, printing one line per
check so the failure is readable in a CI log.

Scope and limits
----------------
This is a **licence metadata consistency check**, not a provenance adjudicator.
It compares the repository's own declarations against each other; it does not
decide who owns anything, and it deliberately does not classify files as
"first-party" or "third-party" by extension. Coverage is decided by the
explicit patterns in ``licensing/manifest.toml``, never by a file's extension
or location. Nothing here contacts a network, downloads a licence text, reads
Git's internal data structures, or modifies a file.

The walk starts at the repository root and skips only ``.git`` and the paths
``licensing/manifest.toml`` records as ``not-distributed``. It therefore sees
tracked files and untracked-but-not-ignored files alike, which is deliberate:
the purpose is to catch a file *before* it is committed, not after. The cost is
that a brand-new untracked file fails the check until it is recorded, which is
the conservative direction to be wrong in.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Semantic markers. These are deliberately short, stable phrases rather than
# whole-file hashes: the point is to catch a switched, truncated or absent
# licence, not to freeze the exact wording of a legal text.
# --------------------------------------------------------------------------

MIT_MARKERS = (
    "MIT License",
    "Permission is hereby granted, free of charge",
    'THE SOFTWARE IS PROVIDED "AS IS"',
)

CCBY_MARKERS = (
    "CC BY 4.0",
    "Creative Commons Attribution 4.0 International",
)

#: The canonical location of the licence text, asserted to be cited.
CCBY_CANONICAL = "creativecommons.org/licenses/by/4.0"

#: The CC BY 4.0 legal code has exactly eight numbered sections.
LEGAL_CODE_SECTIONS = tuple(f"Section {number} --" for number in range(1, 9))

#: Both the content licence and the README must keep excluding third-party
#: material from the repository's grants.
EXCLUSION_MARKERS = ("third-party material", "respective owners")

#: The README must name both licences and both licence files.
README_MARKERS = ("MIT", "CC BY 4.0", "LICENSE", "LICENSE-DATA")

README_HEADING = "## licensing"


@dataclass(frozen=True)
class CheckResult:
    """One named check and its outcome."""

    name: str
    ok: bool
    detail: str


def _read(root: Path, name: str) -> str | None:
    path = root / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _missing(name: str) -> CheckResult:
    return CheckResult(
        name=name,
        ok=False,
        detail=f"required file {name} is missing (expected {name})",
    )


def _top_level_scalar(text: str, key: str) -> str | None:
    """Return the value of a top-level ``key: value`` line, if present.

    Uses a line scan rather than a YAML parser so the guard stays on the
    standard library. It matches only unindented keys, which is what a
    ``CITATION.cff`` header field is.
    """
    prefix = f"{key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"').strip("'")
    return None


def check_license_file(root: Path) -> CheckResult:
    """``LICENSE`` exists and contains the MIT licence, and is not the CC text."""
    text = _read(root, "LICENSE")
    if text is None:
        return _missing("LICENSE")

    if "Creative Commons Attribution 4.0" in text:
        return CheckResult(
            name="LICENSE",
            ok=False,
            detail=(
                "contains the CC BY 4.0 text; LICENSE must hold MIT and the "
                "content licence belongs in LICENSE-DATA"
            ),
        )
    missing = [marker for marker in MIT_MARKERS if marker not in text]
    if missing:
        return CheckResult(
            name="LICENSE",
            ok=False,
            detail=(
                "does not look like the MIT licence "
                f"(missing marker {missing[0]!r}); the software licence is MIT"
            ),
        )
    return CheckResult(
        name="LICENSE",
        ok=True,
        detail="MIT licence text present",
    )


def check_pyproject(root: Path) -> CheckResult:
    """``pyproject.toml`` declares MIT for the distributed package."""
    text = _read(root, "pyproject.toml")
    if text is None:
        return _missing("pyproject.toml")

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - malformed file
        return CheckResult(
            name="pyproject.toml",
            ok=False,
            detail=f"is not valid TOML: {exc}",
        )

    declared = data.get("project", {}).get("license")
    if isinstance(declared, str):
        ok = declared.strip().upper() == "MIT"
        detail = f"project.license = {declared!r}"
    elif isinstance(declared, dict):
        text_value = declared.get("text")
        file_value = declared.get("file")
        if isinstance(text_value, str):
            ok = text_value.strip().upper() == "MIT"
            detail = f"project.license.text = {text_value!r}"
        elif isinstance(file_value, str):
            # The referenced file IS LICENSE, which check 1 verifies is MIT.
            ok = Path(file_value).name.lower() in {"license", "license.txt"}
            detail = f"project.license.file = {file_value!r} (LICENSE is MIT)"
        else:
            ok = False
            detail = f"project.license = {declared!r} names neither text nor file"
    else:
        ok = False
        detail = f"project.license = {declared!r} (expected MIT)"

    if not ok:
        detail = f"{detail}; the package licence is MIT"
    return CheckResult(name="pyproject.toml", ok=ok, detail=detail)


def check_citation(root: Path) -> CheckResult:
    """``CITATION.cff`` declares MIT for the cited software."""
    text = _read(root, "CITATION.cff")
    if text is None:
        return _missing("CITATION.cff")

    declared = _top_level_scalar(text, "license")
    if declared is None:
        return CheckResult(
            name="CITATION.cff",
            ok=False,
            detail="has no top-level 'license:' field; the software licence is MIT",
        )
    ok = declared.upper() == "MIT"
    detail = f"license: {declared}"
    if not ok:
        detail = f"{detail}; the software licence is MIT"
    return CheckResult(name="CITATION.cff", ok=ok, detail=detail)


def check_license_data(root: Path) -> CheckResult:
    """``LICENSE-DATA`` exists, is CC BY 4.0, and embeds the whole legal code."""
    text = _read(root, "LICENSE-DATA")
    if text is None:
        return _missing("LICENSE-DATA")

    missing = [marker for marker in CCBY_MARKERS if marker not in text]
    if missing:
        return CheckResult(
            name="LICENSE-DATA",
            ok=False,
            detail=(
                "does not identify CC BY 4.0 "
                f"(missing marker {missing[0]!r})"
            ),
        )
    if CCBY_CANONICAL not in text:
        return CheckResult(
            name="LICENSE-DATA",
            ok=False,
            detail=f"does not cite the canonical licence location {CCBY_CANONICAL!r}",
        )

    absent = [section for section in LEGAL_CODE_SECTIONS if section not in text]
    if absent:
        return CheckResult(
            name="LICENSE-DATA",
            ok=False,
            detail=(
                "the embedded legal code looks truncated "
                f"(missing {absent[0]!r}, {len(absent)} of "
                f"{len(LEGAL_CODE_SECTIONS)} sections absent)"
            ),
        )
    return CheckResult(
        name="LICENSE-DATA",
        ok=True,
        detail=(
            "CC BY 4.0 notice and complete legal code "
            f"({len(LEGAL_CODE_SECTIONS)}/{len(LEGAL_CODE_SECTIONS)} sections)"
        ),
    )


def check_readme(root: Path) -> CheckResult:
    """``README.md`` documents the dual-licence boundary."""
    text = _read(root, "README.md")
    if text is None:
        return _missing("README.md")

    if README_HEADING not in text.lower():
        return CheckResult(
            name="README.md",
            ok=False,
            detail="has no '## Licensing' section describing the licence boundary",
        )
    missing = [marker for marker in README_MARKERS if marker not in text]
    if missing:
        return CheckResult(
            name="README.md",
            ok=False,
            detail=(
                f"does not mention {missing[0]!r}; the boundary names both "
                "licences and both licence files"
            ),
        )
    return CheckResult(
        name="README.md",
        ok=True,
        detail="MIT and CC BY 4.0 boundary documented",
    )


def check_exclusions(root: Path) -> CheckResult:
    """Third-party material stays excluded from the repository's grants."""
    license_data = _read(root, "LICENSE-DATA")
    readme = _read(root, "README.md")
    for name, text in (("LICENSE-DATA", license_data), ("README.md", readme)):
        if text is None:
            return _missing(name)
        lowered = text.lower()
        absent = [marker for marker in EXCLUSION_MARKERS if marker not in lowered]
        if absent:
            return CheckResult(
                name="third-party exclusion",
                ok=False,
                detail=(
                    f"{name} no longer excludes third-party material "
                    f"(missing {absent[0]!r})"
                ),
            )
    return CheckResult(
        name="third-party exclusion",
        ok=True,
        detail="stated in LICENSE-DATA and README.md",
    )


# --------------------------------------------------------------------------
# Coverage: the explicit licensing treatment of every file
#
# The six checks above keep the declarations consistent with each other, but
# none of them can see a file that nobody declared anything about. The manifest
# closes that gap: it names every path in the repository and the treatment that
# applies to it, and the coverage checks fail when a file is present that no
# entry accounts for. Nothing is inferred from a file's extension or location —
# the decisions live in a reviewed file, not in a rule.
# --------------------------------------------------------------------------

MANIFEST_RELATIVE = "licensing/manifest.toml"

#: Manifest schema versions this guard understands.
SCHEMA_VERSIONS = (1,)

NOT_DISTRIBUTED = "not-distributed"

#: Statuses that decide the treatment of the files they match.
COVERAGE_STATUSES = ("mit", "cc-by", "excluded", "unlicensed")

#: Every status a coverage entry may declare.
STATUSES = COVERAGE_STATUSES + (NOT_DISTRIBUTED,)

#: Statuses that record a judgement rather than a mechanical mapping, and so
#: must say why. Recording a file as excluded, or as deliberately undecided,
#: without a reason would be the silent classification this manifest exists to
#: prevent.
REASON_REQUIRED = ("excluded", "unlicensed")

#: The guard never descends into Git's own directory and never reads it.
GIT_DIRECTORY = ".git"

#: How many offending paths a failure line names before it summarises.
MAX_LISTED_PATHS = 5


class ManifestError(Exception):
    """The coverage manifest is missing or does not satisfy its schema."""


@dataclass(frozen=True)
class CoverageEntry:
    """One ``status``/``pattern`` pair from the manifest."""

    status: str
    pattern: str


@dataclass(frozen=True)
class CoverageManifest:
    """The parsed, validated coverage manifest."""

    schema_version: int
    entries: tuple[CoverageEntry, ...]

    def patterns_for(self, status: str) -> tuple[str, ...]:
        """Every pattern recorded under ``status``, in manifest order."""
        return tuple(
            entry.pattern for entry in self.entries if entry.status == status
        )


def _pattern_problem(pattern: str) -> str | None:
    """Say why ``pattern`` is not a usable path pattern, or return ``None``."""
    if not pattern.strip():
        return "is empty"
    if pattern.startswith("/") or pattern.startswith("./"):
        return "must be relative to the repository root"
    if "\\" in pattern:
        return "must use forward slashes"
    if "//" in pattern:
        return "has an empty path segment"
    if ".." in pattern.split("/"):
        return "must not step outside the repository root"
    return None


def _pattern_regex(pattern: str):
    """Compile a manifest pattern into an anchored regular expression.

    ``**`` spans separators, ``*`` does not, and a trailing ``/`` means "this
    directory and everything beneath it". The two wildcards are kept distinct
    on purpose, so ``labs/*.md`` and ``labs/**.md`` mean different things and
    neither silently widens the other.
    """
    directory = pattern.endswith("/")
    body = pattern[:-1] if directory else pattern
    suffix = r"(?:/.*)?" if directory else ""
    pieces: list[str] = []
    index = 0
    while index < len(body):
        character = body[index]
        if character == "*":
            if body[index + 1 : index + 2] == "*":
                pieces.append(".*")
                index += 2
                continue
            pieces.append("[^/]*")
        else:
            pieces.append(re.escape(character))
        index += 1
    return re.compile(r"\A" + "".join(pieces) + suffix + r"\Z")


def path_is_covered(pattern: str, path: str) -> bool:
    """Whether the repository-relative ``path`` matches ``pattern``."""
    return _pattern_regex(pattern).match(path) is not None


def load_manifest(root: Path) -> CoverageManifest:
    """Read and validate ``licensing/manifest.toml`` under ``root``.

    Raises :class:`ManifestError` naming the exact entry to fix, so the report
    stays actionable instead of becoming a scanner nobody trusts.
    """
    path = root / MANIFEST_RELATIVE
    if not path.is_file():
        raise ManifestError(
            "is missing; every file needs a recorded licensing treatment"
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"is not valid TOML: {exc}") from exc

    version = data.get("schema-version")
    if version not in SCHEMA_VERSIONS:
        expected = ", ".join(str(item) for item in SCHEMA_VERSIONS)
        raise ManifestError(
            f"declares schema-version {version!r}; this guard understands {expected}"
        )

    blocks = data.get("coverage")
    if not isinstance(blocks, list) or not blocks:
        raise ManifestError("has no [[coverage]] entries")

    entries: list[CoverageEntry] = []
    seen: set[tuple[str, str]] = set()
    for number, block in enumerate(blocks, 1):
        if not isinstance(block, dict):
            raise ManifestError(f"coverage entry {number} is not a table")
        status = block.get("status")
        if status not in STATUSES:
            raise ManifestError(
                f"coverage entry {number} has status {status!r}; expected one of "
                f"{', '.join(STATUSES)}"
            )
        paths = block.get("paths")
        if not isinstance(paths, list) or not all(
            isinstance(item, str) for item in paths
        ) or not paths:
            raise ManifestError(
                f"coverage entry {number} ({status}) needs a non-empty list of "
                "path patterns"
            )
        reason = block.get("reason")
        if status in REASON_REQUIRED and not (
            isinstance(reason, str) and reason.strip()
        ):
            raise ManifestError(
                f"coverage entry {number} ({status}) needs a non-empty 'reason': "
                "recording a file as excluded or undecided is a decision, and a "
                "decision has to say why"
            )
        for pattern in paths:
            problem = _pattern_problem(pattern)
            if problem is not None:
                raise ManifestError(
                    f"coverage entry {number} ({status}) pattern {pattern!r} "
                    f"{problem}"
                )
            if (status, pattern) in seen:
                raise ManifestError(
                    f"coverage entry {number} repeats the pattern {pattern!r} "
                    f"under status {status!r}"
                )
            seen.add((status, pattern))
            entries.append(CoverageEntry(status=status, pattern=pattern))

    # Two statuses for one pattern is exactly the silent overlap this manifest
    # must not have, so it is rejected statically as well as per file below.
    statuses_for: dict[str, set[str]] = {}
    for entry in entries:
        statuses_for.setdefault(entry.pattern, set()).add(entry.status)
    overlapping = sorted(
        pattern for pattern, items in statuses_for.items() if len(items) > 1
    )
    if overlapping:
        clash = overlapping[0]
        raise ManifestError(
            f"declares {clash!r} under more than one status "
            f"({', '.join(sorted(statuses_for[clash]))}); a path cannot have two "
            "licensing treatments"
        )

    return CoverageManifest(schema_version=version, entries=tuple(entries))


def _is_ignored(ignored_patterns: tuple[str, ...], path: str) -> bool:
    return any(path_is_covered(pattern, path) for pattern in ignored_patterns)


def walk_repository(root: Path, ignored_patterns: tuple[str, ...]) -> list[str]:
    """List the distributable content set as repository-relative paths.

    Every file under ``root`` is visited except the contents of ``.git`` and
    anything matching a ``not-distributed`` pattern; a directory that matches
    is skipped along with everything beneath it. Paths are sorted, so the
    report is identical on every machine and every run.
    """
    files: list[str] = []

    def visit(directory: Path, prefix: str) -> None:
        for child in sorted(directory.iterdir(), key=lambda item: item.name):
            relative = prefix + child.name
            if child.is_dir():
                if child.name == GIT_DIRECTORY:
                    continue
                if _is_ignored(ignored_patterns, relative):
                    continue
                visit(child, relative + "/")
            elif child.is_file() and not _is_ignored(ignored_patterns, relative):
                files.append(relative)

    visit(root, "")
    return files


@dataclass(frozen=True)
class CoverageReport:
    """How the manifest accounts for the files that are actually present."""

    files: int
    counts: dict[str, int]
    unaccounted: list[str]
    conflicts: list[tuple[str, list[str]]]
    stale: list[str]
    undecided: list[str]


def evaluate_coverage(root: Path, manifest: CoverageManifest) -> CoverageReport:
    """Match every distributable file against the manifest's entries."""
    ignored = manifest.patterns_for(NOT_DISTRIBUTED)
    entries = tuple(
        entry for entry in manifest.entries if entry.status in COVERAGE_STATUSES
    )
    files = walk_repository(root, ignored)

    counts = {status: 0 for status in COVERAGE_STATUSES}
    unaccounted: list[str] = []
    conflicts: list[tuple[str, list[str]]] = []
    undecided: list[str] = []
    matched: set[str] = set()

    for relative in files:
        hits = [entry for entry in entries if path_is_covered(entry.pattern, relative)]
        if not hits:
            unaccounted.append(relative)
            continue
        matched.update(entry.pattern for entry in hits)
        statuses = sorted({entry.status for entry in hits})
        if len(statuses) > 1:
            conflicts.append((relative, statuses))
            continue
        counts[statuses[0]] += 1
        if statuses[0] == "unlicensed":
            undecided.append(relative)

    stale = sorted(
        {entry.pattern for entry in entries if entry.pattern not in matched}
    )
    return CoverageReport(
        files=len(files),
        counts=counts,
        unaccounted=unaccounted,
        conflicts=conflicts,
        stale=stale,
        undecided=undecided,
    )


def _summarise(paths: list[str]) -> str:
    """Shorten a list of offending paths for a one-line report."""
    listed = ", ".join(paths[:MAX_LISTED_PATHS])
    if len(paths) > MAX_LISTED_PATHS:
        return f"{listed} (and {len(paths) - MAX_LISTED_PATHS} more)"
    return listed


def coverage_results(root: Path) -> list[CheckResult]:
    """Check the manifest itself, then the coverage it establishes."""
    try:
        manifest = load_manifest(root)
    except ManifestError as exc:
        skipped = "not evaluated: the coverage manifest did not load"
        return [
            CheckResult(
                name="manifest", ok=False, detail=f"{MANIFEST_RELATIVE} {exc}"
            ),
            CheckResult(name="licence coverage", ok=False, detail=skipped),
            CheckResult(name="unlicensed files", ok=False, detail=skipped),
        ]

    results = [
        CheckResult(
            name="manifest",
            ok=True,
            detail=(
                f"{MANIFEST_RELATIVE}: schema-version "
                f"{manifest.schema_version}, {len(manifest.entries)} coverage entries"
            ),
        )
    ]

    report = evaluate_coverage(root, manifest)
    problems: list[str] = []
    if report.unaccounted:
        problems.append(
            f"{len(report.unaccounted)} file(s) have no recorded licensing "
            f"treatment: {_summarise(report.unaccounted)}; add a [[coverage]] "
            f"entry to {MANIFEST_RELATIVE}"
        )
    if report.conflicts:
        detail = "; ".join(
            f"{path} ({', '.join(statuses)})"
            for path, statuses in report.conflicts[:MAX_LISTED_PATHS]
        )
        problems.append(
            f"{len(report.conflicts)} file(s) are claimed by more than one "
            f"category: {detail}; each path needs exactly one treatment"
        )
    if report.stale:
        problems.append(
            f"{len(report.stale)} pattern(s) match no file in this revision: "
            f"{_summarise(report.stale)}; remove them or update them"
        )

    if problems:
        results.append(
            CheckResult(name="licence coverage", ok=False, detail="; ".join(problems))
        )
    else:
        breakdown = ", ".join(
            f"{status} {count}" for status, count in report.counts.items()
        )
        results.append(
            CheckResult(
                name="licence coverage",
                ok=True,
                detail=f"{report.files} file(s) accounted for ({breakdown})",
            )
        )

    if report.undecided:
        detail = (
            f"{len(report.undecided)} file(s) recorded as deliberately "
            f"undecided: {_summarise(report.undecided)}; review before release"
        )
    else:
        detail = "none recorded; every file has a licence decision"
    results.append(CheckResult(name="unlicensed files", ok=True, detail=detail))
    return results


#: The declaration checks, in report order. The coverage checks follow them.
CHECKS = (
    check_license_file,
    check_pyproject,
    check_citation,
    check_license_data,
    check_readme,
    check_exclusions,
)


def run_checks(root: Path) -> list[CheckResult]:
    """Run every check against ``root`` and return the results in order."""
    results = [check(root) for check in CHECKS]
    results.extend(coverage_results(root))
    return results


def format_report(results: list[CheckResult]) -> str:
    """Render the results as a short, CI-friendly report."""
    passed = sum(1 for result in results if result.ok)
    lines = ["licence metadata check", "=" * len("licence metadata check"), ""]
    for result in results:
        status = "ok  " if result.ok else "FAIL"
        lines.append(f"  {status}  {result.name:<22} {result.detail}")
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
            "The declared boundary is documented in README.md ('Licensing') and "
            "every path's treatment is recorded in licensing/manifest.toml. "
            "Fix the declaration, not the check."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the repository's declared licence metadata.",
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
