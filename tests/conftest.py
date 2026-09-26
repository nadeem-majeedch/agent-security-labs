"""Shared, offline-only test fixtures.

Nothing here touches the network, external model providers, a database, Docker
or a GPU.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

import pytest

#: Fixed timestamp so tests are fully deterministic.
TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def ts() -> datetime:
    return TS


@pytest.fixture
def base() -> Callable[..., dict[str, Any]]:
    """Factory for the shared trace-event header fields."""

    def _base(**overrides: Any) -> dict[str, Any]:
        data: dict[str, Any] = {
            "run_id": "run-1",
            "event_id": "ev-1",
            "seq": 0,
            "timestamp": TS,
            "agent_id": "agent-1",
            "model": "mock-v1",
            "scenario": "LAB-01-a",
        }
        data.update(overrides)
        return data

    return _base
