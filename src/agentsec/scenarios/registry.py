"""A tiny, explicit, in-memory scenario registry.

Registration is explicit and deterministic: no dynamic imports, no plugin
discovery, no filesystem scanning and no code execution from configuration.
Names are returned sorted. Duplicate or unknown ids raise
:class:`~agentsec.errors.ScenarioConfigError`.
"""

from __future__ import annotations

from ..errors import ScenarioConfigError
from .base import Scenario


class ScenarioRegistry:
    """Map ``scenario_id`` to a scenario, with explicit registration only."""

    def __init__(self) -> None:
        self._scenarios: dict[str, Scenario] = {}

    def register(self, scenario: Scenario) -> None:
        """Register ``scenario`` under its ``scenario_id``."""
        scenario_id = scenario.definition().scenario_id
        if scenario_id in self._scenarios:
            raise ScenarioConfigError(f"scenario {scenario_id!r} is already registered")
        self._scenarios[scenario_id] = scenario

    def get(self, scenario_id: str) -> Scenario:
        """Return the scenario for ``scenario_id``."""
        try:
            return self._scenarios[scenario_id]
        except KeyError:
            known = ", ".join(self.names()) or "<none>"
            raise ScenarioConfigError(
                f"unknown scenario {scenario_id!r}; registered: {known}"
            ) from None

    def names(self) -> list[str]:
        """Registered scenario ids, sorted."""
        return sorted(self._scenarios)

    def __contains__(self, scenario_id: object) -> bool:
        return scenario_id in self._scenarios

    def __len__(self) -> int:
        return len(self._scenarios)


__all__ = ["ScenarioRegistry"]
