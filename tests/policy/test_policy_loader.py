"""Tests for YAML policy loading and its strict error handling."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentsec.errors import PolicyConfigError
from agentsec.policy.base import PolicyEngine
from agentsec.policy.loader import load_policy, load_policy_text, parse_policy
from agentsec.policy.schema import Decision

EXAMPLES = Path(__file__).resolve().parents[2] / "policies" / "examples"


def test_load_deny_by_default_example():
    eng = load_policy(EXAMPLES / "deny_by_default.yaml")
    assert isinstance(eng, PolicyEngine)
    assert eng.default_decision is Decision.DENY
    assert eng.rules == []
    assert eng.decide("agent", "calculator", {}).decision is Decision.DENY


def test_load_least_privilege_example():
    eng = load_policy(EXAMPLES / "least_privilege_v1.yaml")
    assert [r.id for r in eng.rules] == [
        "allow-calc",
        "fs-read-workspace",
        "fs-deny-outside",
        "db-read-requires-approval",
        "db-writes-denied",
    ]
    assert eng.decide("agent", "calculator", {}, action="invoke").decision is Decision.ALLOW
    assert (
        eng.decide("agent", "fs_sandbox", {}, action="read", resource="workspace/a.txt").decision
        is Decision.ALLOW
    )
    assert (
        eng.decide("agent", "mock_db", {}, action="read", resource="users").decision
        is Decision.REQUIRE_APPROVAL
    )
    assert (
        eng.decide("agent", "mock_db", {}, action="write", resource="users").decision
        is Decision.DENY
    )


def test_load_from_text():
    eng = load_policy_text(
        """
        default: DENY
        rules:
          - id: allow-calc
            subject: student-agent
            tool: calculator
            action: calculate
            decision: ALLOW
            reason: baseline
        """
    )
    assert eng.decide("student-agent", "calculator", {}, action="calculate").decision is Decision.ALLOW


def test_parse_none_is_default_deny():
    eng = parse_policy(None)
    assert eng.default_decision is Decision.DENY
    assert eng.rules == []


def test_missing_file_is_a_config_error(tmp_path):
    with pytest.raises(PolicyConfigError):
        load_policy(tmp_path / "nope.yaml")


def test_invalid_yaml_syntax_is_a_config_error(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("default: deny\nrules: [\n", encoding="utf-8")
    with pytest.raises(PolicyConfigError):
        load_policy(path)


def test_non_mapping_document_is_a_config_error():
    with pytest.raises(PolicyConfigError):
        parse_policy("just a string")
    with pytest.raises(PolicyConfigError):
        parse_policy([1, 2, 3])


def test_unknown_decision_is_a_config_error():
    with pytest.raises(PolicyConfigError):
        parse_policy({"default": "maybe", "rules": []})


def test_missing_rule_field_is_a_config_error():
    with pytest.raises(PolicyConfigError):
        parse_policy({"rules": [{"decision": "allow", "reason": "x"}]})


def test_unknown_condition_is_a_config_error():
    with pytest.raises(PolicyConfigError):
        parse_policy(
            {
                "rules": [
                    {
                        "id": "r",
                        "decision": "allow",
                        "reason": "x",
                        "conditions": {"typo": True},
                    }
                ]
            }
        )


def test_extra_document_field_is_a_config_error():
    with pytest.raises(PolicyConfigError):
        parse_policy({"default": "deny", "rules": [], "extra": 1})


def test_engine_from_yaml_classmethod(tmp_path):
    path = EXAMPLES / "deny_by_default.yaml"
    eng = PolicyEngine.from_yaml(path)
    assert eng.default_decision is Decision.DENY


def test_load_reports_the_offending_file(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("default: maybe\nrules: []\n", encoding="utf-8")
    with pytest.raises(PolicyConfigError) as excinfo:
        load_policy(path)
    assert str(path) in str(excinfo.value)
