"""Validation of trace events against the versioned JSON Schema.

Two layers are provided:

* **Schema validation** - every event is checked with ``jsonschema`` against
  the checked-in schema at ``schemas/trace/trace_event.v1.schema.json``.
* **Semantic validation** - optional checks that exceed the schema: ``seq``
  must increase, and ``parent_event_id`` must reference an earlier event.

Nothing here indexes, searches or visualizes traces.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

from ..errors import TraceSchemaError

SCHEMA_FILENAME = "trace_event.v1.schema.json"
_SCHEMA_SUBPATH = Path("schemas") / "trace" / SCHEMA_FILENAME


def schema_path() -> Path:
    """Locate the checked-in trace schema in the repository."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / _SCHEMA_SUBPATH
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"could not locate {_SCHEMA_SUBPATH.as_posix()} above {__file__}"
    )


_SCHEMA_CACHE: dict[Path, dict[str, Any]] = {}


def load_schema(path: Path | None = None) -> dict[str, Any]:
    """Load and cache the trace JSON Schema."""
    resolved = Path(path) if path is not None else schema_path()
    if resolved not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[resolved] = json.loads(resolved.read_text(encoding="utf-8"))
    return _SCHEMA_CACHE[resolved]


def _validator(schema: Mapping[str, Any] | None) -> Draft202012Validator:
    return Draft202012Validator(schema if schema is not None else load_schema())


def validate_event(
    event: Mapping[str, Any], schema: Mapping[str, Any] | None = None
) -> None:
    """Validate a single event mapping, raising ``TraceSchemaError`` on failure."""
    errors = sorted(_validator(schema).iter_errors(event), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
            for err in errors
        )
        raise TraceSchemaError(f"event failed schema validation: {details}")


@dataclass(frozen=True)
class ValidationIssue:
    """A single problem found while validating a JSONL file."""

    line: int
    message: str
    event_id: str | None = None


@dataclass
class ValidationReport:
    """Outcome of validating a JSONL trace file."""

    path: Path
    total: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues


def _semantic_issues(events: Iterable[tuple[int, Mapping[str, Any]]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    last_seq: int | None = None
    for line, event in events:
        event_id = event.get("event_id")
        seq = event.get("seq")
        if isinstance(seq, int):
            if last_seq is not None and seq <= last_seq:
                issues.append(
                    ValidationIssue(
                        line,
                        f"seq must increase (got {seq} after {last_seq})",
                        str(event_id) if event_id is not None else None,
                    )
                )
            last_seq = seq
        parent = event.get("parent_event_id")
        if parent is not None and parent not in seen_ids:
            issues.append(
                ValidationIssue(
                    line,
                    f"parent_event_id {parent!r} does not reference an earlier event",
                    str(event_id) if event_id is not None else None,
                )
            )
        if isinstance(event_id, str):
            seen_ids.add(event_id)
    return issues


def validate_jsonl(
    path: Path,
    schema: Mapping[str, Any] | None = None,
    *,
    semantic: bool = True,
) -> ValidationReport:
    """Validate every line of a JSONL trace file.

    Reports per-line issues instead of raising, so callers can show students
    exactly which line failed and why.
    """
    path = Path(path)
    report = ValidationReport(path=path)
    valid: list[tuple[int, Mapping[str, Any]]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        report.total += 1
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            report.issues.append(ValidationIssue(line_no, f"invalid JSON: {exc}"))
            continue
        if not isinstance(event, dict):
            report.issues.append(
                ValidationIssue(line_no, "event must be a JSON object")
            )
            continue
        try:
            validate_event(event, schema)
        except TraceSchemaError as exc:
            report.issues.append(ValidationIssue(line_no, str(exc), event.get("event_id")))
            continue
        valid.append((line_no, event))
    if semantic:
        report.issues.extend(_semantic_issues(valid))
    return report
