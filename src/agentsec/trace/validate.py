"""Validation of trace events against the versioned JSON Schema.

Two layers are provided:

* **Schema validation** - every event is checked with ``jsonschema`` against
  the packaged trace schema, shipped as package data at
  ``agentsec/schemas/trace/trace_event.v1.schema.json``.
* **Semantic validation** - optional checks that exceed the schema: ``seq``
  must increase, and ``parent_event_id`` must reference an earlier event.

The schema is read from **package resources**, never by walking the filesystem
out of this module: an installed ``agentsec`` is self-contained, so validation
works from a wheel with no repository checkout and no ``schemas/`` directory
beside it. ``scripts/export_trace_schema.py`` is the single writer of the
packaged copy and of the repository copy, and the tests enforce that both stay
byte-identical to each other and to the pydantic models.

Nothing here indexes, searches or visualizes traces.
"""

from __future__ import annotations

import atexit
import json
from contextlib import ExitStack
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

from ..errors import TraceSchemaError

SCHEMA_FILENAME = "trace_event.v1.schema.json"

#: The package that carries the schema, and its location inside that package.
SCHEMA_PACKAGE = "agentsec.schemas"
SCHEMA_RESOURCE = f"trace/{SCHEMA_FILENAME}"

#: Cache key for the packaged schema, as opposed to an explicit path.
_PACKAGED_KEY = f"{SCHEMA_PACKAGE}:{SCHEMA_RESOURCE}"

# ``as_file`` materialises a resource that is not already a plain file (for
# example inside a zip import) into a temporary file. Keeping one stack open for
# the life of the process means a path returned by ``schema_path()`` stays valid
# for as long as the caller can use it.
_RESOURCE_STACK = ExitStack()
atexit.register(_RESOURCE_STACK.close)


def schema_resource():
    """The packaged trace schema as a :class:`importlib.resources` resource."""
    return resources.files(SCHEMA_PACKAGE).joinpath(SCHEMA_RESOURCE)


def _schema_text() -> str:
    """Read the packaged schema, or explain that the install is incomplete."""
    resource = schema_resource()
    if not resource.is_file():
        raise FileNotFoundError(
            f"packaged trace schema {_PACKAGED_KEY} is missing; the agentsec "
            "installation is incomplete (reinstall the package)"
        )
    return resource.read_text(encoding="utf-8")


def schema_text() -> str:
    """The packaged trace schema as text, with no filesystem path involved."""
    return _schema_text()


def schema_path() -> Path:
    """A filesystem path to the packaged trace schema.

    Convenience for callers that need a path rather than the contents. The
    path is obtained from ``importlib.resources.as_file`` and is kept valid for
    the lifetime of the process, so it can be held by the caller.
    """
    return _RESOURCE_STACK.enter_context(resources.as_file(schema_resource()))


_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def load_schema(path: Path | None = None) -> dict[str, Any]:
    """Load and cache the trace JSON Schema.

    With no argument, the schema comes from the package resources. An explicit
    ``path`` still loads that file instead, so the helper remains usable for
    inspecting an alternative schema on disk.
    """
    if path is not None:
        resolved = Path(path)
        key = str(resolved)
        if key not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[key] = json.loads(resolved.read_text(encoding="utf-8"))
        return _SCHEMA_CACHE[key]

    if _PACKAGED_KEY not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[_PACKAGED_KEY] = json.loads(_schema_text())
    return _SCHEMA_CACHE[_PACKAGED_KEY]


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
