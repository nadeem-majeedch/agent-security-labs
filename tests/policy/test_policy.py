"""Tests for decision semantics: allow/deny/require_approval, precedence, default."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, Policy, PolicyRule
from agentsec.tools.base import ToolContext


def engine(rules=(), default=Decision.DENY):
    return PolicyEngine(list(rules), default_decision=default)


def rule(**overrides):
    data = {"id": "r", "decision": Decision.ALLOW, "reason": "why", "tool": "calculator"}
    data.update(overrides)
    return PolicyRule(**data)


def test_explicit_allow():
    decision = engine([rule(decision=Decision.ALLOW)]).decide("agent", "calculator", {})
    assert decision.decision is Decision.ALLOW
    assert decision.matched_rule == "r"
    assert decision.reason == "why"


def test_explicit_deny():
    decision = engine([rule(decision=Decision.DENY)]).decide("agent", "calculator", {})
    assert decision.decision is Decision.DENY


def test_require_approval():
    decision = engine([rule(decision=Decision.REQUIRE_APPROVAL)]).decide(
        "agent", "calculator", {}
    )
    assert decision.decision is Decision.REQUIRE_APPROVAL


def test_default_is_deny_when_nothing_matches():
    decision = engine().decide("agent", "calculator", {})
    assert decision.decision is Decision.DENY
    assert decision.matched_rule is None


def test_default_can_be_overridden():
    decision = engine(default=Decision.ALLOW).decide("agent", "unknown", {})
    assert decision.decision is Decision.ALLOW


def test_first_match_wins():
    rules = [
        rule(id="first", decision=Decision.DENY),
        rule(id="second", decision=Decision.ALLOW),
    ]
    decision = engine(rules).decide("agent", "calculator", {})
    assert decision.decision is Decision.DENY
    assert decision.matched_rule == "first"


def test_subject_matching():
    rules = [rule(id="alice", subject="alice")]
    assert engine(rules).decide("alice", "calculator", {}).decision is Decision.ALLOW
    assert engine(rules).decide("bob", "calculator", {}).decision is Decision.DENY


def test_wildcard_matches_everything():
    decision = engine([rule(subject="*", tool="*", action="*")]).decide(
        "anyone", "anything", {}, action="whatever"
    )
    assert decision.decision is Decision.ALLOW


def test_action_matching():
    rules = [rule(id="read", action="read", tool="fs_sandbox")]
    assert engine(rules).decide("agent", "fs_sandbox", {}, action="read").decision is Decision.ALLOW
    assert engine(rules).decide("agent", "fs_sandbox", {}, action="write").decision is Decision.DENY


def test_resource_glob_matching():
    rules = [rule(id="ws", tool="fs_sandbox", resource="workspace/*")]
    assert (
        engine(rules)
        .decide("agent", "fs_sandbox", {}, resource="workspace/notes/n.txt")
        .decision
        is Decision.ALLOW
    )
    assert (
        engine(rules).decide("agent", "fs_sandbox", {}, resource="../exfil.txt").decision
        is Decision.DENY
    )


def test_star_resource_matches_missing_resource():
    decision = engine([rule(resource="*")]).decide("agent", "calculator", {})
    assert decision.decision is Decision.ALLOW


def test_specific_resource_does_not_match_missing_resource():
    decision = engine([rule(resource="workspace/*")]).decide("agent", "calculator", {})
    assert decision.decision is Decision.DENY


def test_condition_outside_task_scope():
    rules = [
        rule(
            id="outside",
            tool="fs_sandbox",
            resource="workspace/*",
            conditions={"outside_task_scope": True},
        )
    ]
    ctx = ToolContext(agent_id="a", task_scope=("workspace/in-scope.txt",))
    assert (
        engine(rules)
        .decide("a", "fs_sandbox", {}, ctx, resource="workspace/other.txt")
        .decision
        is Decision.ALLOW
    )
    assert (
        engine(rules)
        .decide("a", "fs_sandbox", {}, ctx, resource="workspace/in-scope.txt")
        .decision
        is Decision.DENY
    )


def test_decision_string_is_case_insensitive():
    assert rule(decision="ALLOW").decision is Decision.ALLOW
    assert Policy(default="DENY").default is Decision.DENY


def test_unknown_decision_is_rejected():
    with pytest.raises(ValidationError):
        PolicyRule(id="r", decision="maybe", reason="x")


def test_unknown_condition_key_is_rejected():
    with pytest.raises(ValidationError):
        PolicyRule(id="r", decision="allow", reason="x", conditions={"typo": True})


def test_missing_required_fields_are_rejected():
    with pytest.raises(ValidationError):
        PolicyRule(decision="allow", reason="x")  # no id
    with pytest.raises(ValidationError):
        PolicyRule(id="r", decision="allow")  # no reason


def test_extra_rule_field_is_rejected():
    with pytest.raises(ValidationError):
        PolicyRule(id="r", decision="allow", reason="x", nope=1)


def test_policy_defaults_to_deny_and_no_rules():
    policy = Policy()
    assert policy.default is Decision.DENY
    assert policy.rules == []


def test_from_policy_builds_engine():
    eng = PolicyEngine.from_policy(
        Policy(default=Decision.ALLOW, rules=[rule(decision=Decision.DENY)])
    )
    assert eng.default_decision is Decision.ALLOW
    assert len(eng.rules) == 1
    assert eng.decide("agent", "calculator", {}).decision is Decision.DENY


def test_engine_does_not_mutate_input_rules():
    rules = [rule()]
    eng = engine(rules)
    rules.clear()
    assert len(eng.rules) == 1
