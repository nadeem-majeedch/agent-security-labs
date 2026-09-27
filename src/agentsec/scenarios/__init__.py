"""Scenario package: declarative experiments and their interpretation.

Scenarios prepare configuration and interpret observable results. They do not
run the agent, execute tools, evaluate policy or write traces - those remain the
responsibility of the existing layers.
"""

from .base import (
    DeclarativeScenario,
    ExpectedObservation,
    ObservationCheck,
    Scenario,
    ScenarioDef,
    ScenarioOutcome,
    ScenarioStatus,
)
from .loader import load_scenario, parse_scenario
from .registry import ScenarioRegistry

__all__ = [
    "Scenario",
    "ScenarioDef",
    "ScenarioOutcome",
    "ScenarioStatus",
    "ExpectedObservation",
    "ObservationCheck",
    "DeclarativeScenario",
    "ScenarioRegistry",
    "load_scenario",
    "parse_scenario",
]
