"""Minimal append-only trace recorder.

A recorder owns one run's JSONL file. It stamps the shared header fields
(``run_id``, ``event_id``, ``seq``, ``timestamp``, ``agent_id``, ``model``,
``scenario``) onto every event, redacts it, validates it against the versioned
schema and appends it. ``event_id`` is ``ev-<seq>`` so a run is byte-identical
when replayed with the same inputs and a fixed clock - no UUID or wall clock is
consulted unless the caller injects a clock.

This is deliberately not an index, a query engine or a viewer. It is only the
write path the gateway (and later the agent loop) needs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

from ..errors import TraceSchemaError
from .redact import DEFAULT_REDACTOR, Redactor
from .schema import TraceEvent
from .validate import validate_event
from .writer import write_event

_EventT = TypeVar("_EventT", bound=TraceEvent)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TraceMeta:
    """Summary returned when a recorder is closed."""

    path: Path
    run_id: str
    event_count: int


class TraceRecorder:
    """Append redacted, validated events for a single run."""

    def __init__(
        self,
        path: str | Path,
        *,
        run_id: str,
        agent_id: str,
        model: str,
        scenario: str,
        redactor: Redactor | None = None,
        clock: Callable[[], datetime] | None = None,
        validate: bool = True,
    ) -> None:
        self._path = Path(path)
        self._run_id = run_id
        self._agent_id = agent_id
        self._model = model
        self._scenario = scenario
        self._redactor = redactor if redactor is not None else DEFAULT_REDACTOR
        self._clock = clock or _utcnow
        self._validate = validate
        self._seq = 0
        self._count = 0
        self._last_event_id: str | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def scenario(self) -> str:
        return self._scenario

    @property
    def event_count(self) -> int:
        return self._count

    @property
    def last_event_id(self) -> str | None:
        """The id of the most recently emitted event, for chaining.

        Callers (for example the agent loop) use this to set the next event's
        ``parent_event_id`` without inventing a second correlation mechanism.
        """
        return self._last_event_id

    def _header(self) -> dict[str, Any]:
        seq = self._seq
        self._seq += 1
        return {
            "run_id": self._run_id,
            "event_id": f"ev-{seq:06d}",
            "seq": seq,
            "timestamp": self._clock(),
            "agent_id": self._agent_id,
            "model": self._model,
            "scenario": self._scenario,
        }

    def build(self, event_cls: type[_EventT], **fields: Any) -> _EventT:
        """Construct an event of ``event_cls`` with a stamped header.

        Advances the sequence counter; does not write.
        """
        data: dict[str, Any] = dict(self._header())
        data.update(fields)
        return event_cls(**data)

    def emit(self, event: TraceEvent) -> None:
        """Redact, validate and append ``event``."""
        payload = self._redactor.redact_mapping(event.model_dump(mode="json"))
        if self._validate:
            validate_event(payload)
        write_event(self._path, event, redactor=self._redactor)
        self._count += 1
        self._last_event_id = event.event_id

    def emit_event(self, event_cls: type[_EventT], **fields: Any) -> _EventT:
        """Build and emit an event, returning it (with its generated ids)."""
        event = self.build(event_cls, **fields)
        self.emit(event)
        return event

    def close(self) -> TraceMeta:
        """Return a summary; the recorder does not hold the file open."""
        return TraceMeta(path=self._path, run_id=self._run_id, event_count=self._count)


__all__ = ["TraceRecorder", "TraceMeta", "TraceSchemaError"]
