"""Tests for experiment configuration composition and YAML loading."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from agentsec.agent import AgentConfig
from agentsec.errors import ConfigError
from agentsec.experiment import ExperimentConfig, load_experiment_config

EXAMPLE = Path(__file__).resolve().parents[2] / "configs" / "examples" / "benign.yaml"


def test_config_composes_agent_config():
    config = ExperimentConfig(experiment_id="e", task="t")
    assert isinstance(config.agent, AgentConfig)
    assert config.agent.max_steps == 8
    assert config.trace_path is None


def test_config_requires_experiment_id_and_task():
    with pytest.raises(ValidationError):
        ExperimentConfig(task="t")
    with pytest.raises(ValidationError):
        ExperimentConfig(experiment_id="e")


def test_config_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        ExperimentConfig(experiment_id="e", task="t", repetitions=3)
    with pytest.raises(ValidationError):
        ExperimentConfig(experiment_id="e", task="t", agent={"temperature": 0.0})


def test_config_embeds_agent_fields():
    config = ExperimentConfig(
        experiment_id="e",
        task="t",
        agent=AgentConfig(agent_id="a", run_id="r", scenario="LAB-01-a", max_steps=2),
    )
    assert config.agent.agent_id == "a"
    assert config.agent.max_steps == 2


def test_load_example_config():
    config = load_experiment_config(EXAMPLE)
    assert config.experiment_id == "benign_baseline"
    assert config.task == "please add 2 and 3"
    assert config.agent.scenario == "LAB-01-a"
    assert config.agent.max_steps == 6
    assert config.agent.config_ref == "configs/examples/benign.yaml"


def test_missing_file_is_config_error(tmp_path):
    with pytest.raises(ConfigError):
        load_experiment_config(tmp_path / "nope.yaml")


def test_invalid_yaml_is_config_error(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_id: [\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_experiment_config(path)


def test_non_mapping_document_is_config_error(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_experiment_config(path)


def test_missing_required_field_is_config_error(tmp_path):
    path = tmp_path / "incomplete.yaml"
    path.write_text("experiment_id: e\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_experiment_config(path)


def test_extra_field_is_config_error(tmp_path):
    path = tmp_path / "extra.yaml"
    path.write_text(
        "experiment_id: e\n" "task: t\n" "repetitions: 3\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_experiment_config(path)


def test_invalid_agent_field_is_config_error(tmp_path):
    path = tmp_path / "badagent.yaml"
    path.write_text(
        "experiment_id: e\ntask: t\nagent:\n  max_steps: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_experiment_config(path)


def test_error_names_the_file(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_id: e\n", encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_experiment_config(path)
    assert str(path) in str(excinfo.value)
