"""Tests for scenario YAML loading and the explicit registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentsec.errors import ScenarioConfigError
from agentsec.experiment import ExperimentConfig
from agentsec.scenarios import (
    DeclarativeScenario,
    ExpectedObservation,
    ScenarioDef,
    ScenarioRegistry,
    load_scenario,
    parse_scenario,
)

VALID = {
    "scenario_id": "benign-tool-ok",
    "title": "Benign tool use",
    "description": "a benign read-only tool call is allowed",
    "expected": {"agent_status": "completed", "tool_executions": 1},
    "experiment": {
        "experiment_id": "s1",
        "task": "please add 2 and 3",
        "mock_script": "benign",
        "agent": {"run_id": "run-1", "scenario": "LAB-01-a"},
    },
}


def test_parse_scenario_builds_a_scenario():
    scenario = parse_scenario(VALID)
    assert isinstance(scenario, DeclarativeScenario)
    assert scenario.scenario_id == "benign-tool-ok"
    assert scenario.prepare().experiment_id == "s1"


def test_load_scenario_from_yaml(tmp_path):
    import yaml

    path = tmp_path / "scenario.yaml"
    path.write_text(yaml.safe_dump(VALID), encoding="utf-8")
    scenario = load_scenario(path)
    assert scenario.definition().title == "Benign tool use"
    assert scenario.definition().expected.tool_executions == 1


def test_load_scenario_missing_file():
    with pytest.raises(ScenarioConfigError):
        load_scenario(Path("does-not-exist.yaml"))


def test_load_scenario_invalid_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("scenario_id: [\n", encoding="utf-8")
    with pytest.raises(ScenarioConfigError):
        load_scenario(path)


def test_non_mapping_document_is_rejected():
    with pytest.raises(ScenarioConfigError):
        parse_scenario(["not", "a", "mapping"])


def test_missing_experiment_is_rejected():
    with pytest.raises(ScenarioConfigError):
        parse_scenario({"scenario_id": "x"})


def test_unknown_field_is_rejected():
    data = dict(VALID)
    data["payload"] = {"attack": "nope"}
    with pytest.raises(ScenarioConfigError):
        parse_scenario(data)


def test_error_names_the_file(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("scenario_id: x\n", encoding="utf-8")
    with pytest.raises(ScenarioConfigError) as excinfo:
        load_scenario(path)
    assert str(path) in str(excinfo.value)


# -- registry ------------------------------------------------------------------
def make(id_: str) -> DeclarativeScenario:
    return DeclarativeScenario(
        ScenarioDef(
            scenario_id=id_,
            expected=ExpectedObservation(),
            experiment=ExperimentConfig(experiment_id="e", task="t"),
        )
    )


def test_registry_register_get_names():
    registry = ScenarioRegistry()
    registry.register(make("b"))
    registry.register(make("a"))
    assert registry.names() == ["a", "b"]
    assert registry.get("a").scenario_id == "a"
    assert "a" in registry
    assert "z" not in registry
    assert len(registry) == 2


def test_registry_duplicate_is_rejected():
    registry = ScenarioRegistry()
    registry.register(make("a"))
    with pytest.raises(ScenarioConfigError):
        registry.register(make("a"))


def test_registry_unknown_is_rejected():
    registry = ScenarioRegistry()
    with pytest.raises(ScenarioConfigError):
        registry.get("missing")
