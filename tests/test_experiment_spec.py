"""Tests for the controlled-experiment specification model and validator.

Phase 11C adds a declarative experiment *specification* and a strict validator.
These tests pin its semantics: the required hypothesis, the single declared
intervention, the reuse of the existing ``ExpectedObservation`` vocabulary, the
non-empty alternative explanations, strict unknown-field rejection, deterministic
validation, and file resolution against the shared base config and policies.

They are semantic, not structural: they assert what the validator accepts and
rejects, not how it is implemented. Nothing here executes an experiment.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agentsec.errors import ConfigError, PolicyConfigError
from agentsec.experiment import ExperimentConfig
from agentsec.experiment_lab import (
    ExperimentSpec,
    load_experiment_spec,
    parse_experiment_spec,
    validate_experiment_files,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "configs" / "experiments" / "lab04-policy-intervention.yaml"


def valid_data() -> dict:
    """A minimal valid specification, as an already-parsed mapping."""
    return {
        "schema_version": "1",
        "experiment_id": "lab04-policy-intervention",
        "title": "Controlled policy intervention (LAB-04)",
        "hypothesis": "changing only the policy changes whether the write executes",
        "base_config": "labs/LAB-04-tool-misuse/config.yaml",
        "intervention": {
            "type": "policy",
            "control_policy": "policies/examples/least_privilege_v1.yaml",
            "treatment_policy": "policies/examples/allow_all_v1.yaml",
        },
        "expected_changes": {"tool_executions": 1},
        "expected_invariants": {"requested_tools": ["fs_sandbox"]},
        "alternative_explanations": [
            "the change is a property of the deterministic fixture",
        ],
        "claim": "within this fixture, the policy change explains the difference",
    }


# -- valid specification -------------------------------------------------------
def test_valid_spec_parses():
    spec = parse_experiment_spec(valid_data())
    assert isinstance(spec, ExperimentSpec)
    assert spec.experiment_id == "lab04-policy-intervention"
    assert spec.intervention.type.value == "policy"


def test_valid_example_file_loads():
    spec = load_experiment_spec(EXAMPLE)
    assert spec.experiment_id == "lab04-policy-intervention"
    assert spec.intervention.control_policy.name == "least_privilege_v1.yaml"
    assert spec.intervention.treatment_policy.name == "allow_all_v1.yaml"


def test_valid_observation_vocabulary_is_accepted():
    data = valid_data()
    data["expected_changes"] = {
        "tool_executions": 1,
        "policy_denials": 0,
        "produced_final_output": True,
    }
    data["expected_invariants"] = {
        "requested_tools": ["fs_sandbox"],
        "agent_status": "completed",
    }
    spec = parse_experiment_spec(data)
    assert spec.expected_changes.tool_executions == 1
    assert spec.expected_invariants.requested_tools == ("fs_sandbox",)


def test_claim_is_optional():
    data = valid_data()
    del data["claim"]
    assert parse_experiment_spec(data).claim is None


# -- required structure --------------------------------------------------------
def test_missing_hypothesis_is_rejected():
    data = valid_data()
    del data["hypothesis"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_blank_hypothesis_is_rejected():
    data = valid_data()
    data["hypothesis"] = "   "
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_missing_base_config_is_rejected():
    data = valid_data()
    del data["base_config"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_non_mapping_document_is_rejected():
    with pytest.raises(ConfigError):
        parse_experiment_spec(["not", "a", "mapping"])


def test_invalid_experiment_id_is_rejected():
    data = valid_data()
    data["experiment_id"] = "Not A Slug"
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


# -- intervention --------------------------------------------------------------
def test_missing_intervention_is_rejected():
    data = valid_data()
    del data["intervention"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_multiple_interventions_as_list_are_rejected():
    data = valid_data()
    data["intervention"] = [
        valid_data()["intervention"],
        valid_data()["intervention"],
    ]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_undeclared_second_intervention_field_is_rejected():
    data = valid_data()
    data["intervention_b"] = {"type": "policy"}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_unsupported_intervention_type_is_rejected():
    data = valid_data()
    data["intervention"]["type"] = "scenario"
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_missing_control_policy_is_rejected():
    data = valid_data()
    del data["intervention"]["control_policy"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_missing_treatment_policy_is_rejected():
    data = valid_data()
    del data["intervention"]["treatment_policy"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_identical_control_and_treatment_are_rejected():
    data = valid_data()
    data["intervention"]["treatment_policy"] = data["intervention"]["control_policy"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_unknown_intervention_field_is_rejected():
    data = valid_data()
    data["intervention"]["scope"] = "everything"
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


# -- expectations --------------------------------------------------------------
def test_missing_expected_changes_is_rejected():
    data = valid_data()
    del data["expected_changes"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_empty_expected_changes_is_rejected():
    data = valid_data()
    data["expected_changes"] = {}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_missing_expected_invariants_is_rejected():
    data = valid_data()
    del data["expected_invariants"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_empty_expected_invariants_is_rejected():
    data = valid_data()
    data["expected_invariants"] = {}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_invalid_observation_vocabulary_is_rejected():
    data = valid_data()
    data["expected_changes"] = {"tool_executions": "many"}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_unknown_observation_field_is_rejected():
    data = valid_data()
    data["expected_changes"] = {"bogus_metric": 1}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


# -- alternative explanations --------------------------------------------------
def test_missing_alternative_explanations_is_rejected():
    data = valid_data()
    del data["alternative_explanations"]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_empty_alternative_explanations_list_is_rejected():
    data = valid_data()
    data["alternative_explanations"] = []
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_blank_alternative_explanation_is_rejected():
    data = valid_data()
    data["alternative_explanations"] = ["a real alternative", "   "]
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


# -- strictness / determinism --------------------------------------------------
def test_unknown_top_level_field_is_rejected():
    data = valid_data()
    data["payload"] = {"attack": "nope"}
    with pytest.raises(ConfigError):
        parse_experiment_spec(data)


def test_validation_is_deterministic():
    first = parse_experiment_spec(valid_data())
    second = parse_experiment_spec(valid_data())
    assert first == second
    # A copy with the same content validates to the same value.
    assert parse_experiment_spec(copy.deepcopy(valid_data())) == first


def test_malformed_yaml_is_rejected(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_id: [\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_experiment_spec(path)


def test_missing_spec_file_is_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_experiment_spec(tmp_path / "does-not-exist.yaml")


def test_load_error_names_the_file(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_id: x\n", encoding="utf-8")
    with pytest.raises(ConfigError) as excinfo:
        load_experiment_spec(path)
    assert str(path) in str(excinfo.value)


# -- file validation -----------------------------------------------------------
def test_validate_example_files_resolves_the_base_and_policies():
    spec = load_experiment_spec(EXAMPLE)
    resolved = validate_experiment_files(spec, root=ROOT)
    assert isinstance(resolved.base_config, ExperimentConfig)
    assert resolved.base_config.experiment_id == "lab04_tool_misuse"
    assert resolved.control_policy != resolved.treatment_policy


def test_validate_files_rejects_a_missing_policy():
    spec = load_experiment_spec(EXAMPLE)
    data = spec.model_dump()
    data["intervention"]["treatment_policy"] = "policies/examples/not-a-real-policy.yaml"
    broken = parse_experiment_spec(data)
    with pytest.raises((ConfigError, PolicyConfigError)):
        validate_experiment_files(broken, root=ROOT)


def test_validate_files_rejects_a_missing_base_config():
    spec = load_experiment_spec(EXAMPLE)
    data = spec.model_dump()
    data["base_config"] = "labs/does-not-exist/config.yaml"
    broken = parse_experiment_spec(data)
    with pytest.raises(ConfigError):
        validate_experiment_files(broken, root=ROOT)
