"""Minimal, append-only JSONL serialization for trace events.

Deliberately narrow: serialize an event, append one or many events, and read
them back. No indexing, no query engine, no database.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from ..errors import TraceWriteError
from .redact import Redactor
from .schema import TraceEvent


def serialize_event(event: TraceEvent, redactor: Redactor | None = None) -> str:
    """Serialize one event to a single JSON line (without a trailing newline).

    When a ``redactor`` is supplied it is applied to the event payload *before*
    serialization, so redaction cannot be bypassed by a later write path.
    """
    data: dict[str, Any] = event.model_dump(mode="json")
    if redactor is not None:
        data = redactor.redact_mapping(data)
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def write_event(path: Path, event: TraceEvent, *, redactor: Redactor | None = None) -> None:
    """Append a single event to ``path`` as one JSONL line."""
    write_events(path, [event], redactor=redactor)


def write_events(
    path: Path, events: Iterable[TraceEvent], *, redactor: Redactor | None = None
) -> None:
    """Append events to ``path``, creating parent directories as needed."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for event in events:
                handle.write(serialize_event(event, redactor))
                handle.write("\n")
    except OSError as exc:  # pragma: no cover - depends on host filesystem
        raise TraceWriteError(f"could not write trace to {path}: {exc}") from exc


def read_events(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL trace file into a list of raw event mappings.

    Raises ``json.JSONDecodeError`` for malformed lines so callers can decide
    how to report them; use :func:`agentsec.trace.validate.validate_jsonl` for
    schema-aware validation.
    """
    path = Path(path)
    events: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            events.append(json.loads(raw))
    return events
