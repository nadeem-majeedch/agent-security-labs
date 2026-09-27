"""The minimal policy engine.

Semantics (Phase 14, Task 9):

* decisions are ``allow``, ``deny`` or ``require_approval``;
* the **first matching rule wins**;
* unmatched calls fall to ``default_decision`` (default ``deny``);
* matching is plain string/glob comparison - no inheritance and no attributes.

The engine knows nothing about concrete tools. The gateway derives an action
and resource from the tool's own authorization metadata and passes them in, so
policy rules can match on ``action``/``resource`` without importing any tool.
"""

from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, Mapping

from ..errors import PolicyConfigError
from .schema import Decision, Policy, PolicyDecision, PolicyRule


class PolicyEngine:
    """Evaluate a proposed call against an ordered list of flat rules."""

    def __init__(
        self,
        rules: list[PolicyRule] | None = None,
        default_decision: Decision = Decision.DENY,
    ) -> None:
        self._rules = list(rules or [])
        self._default = default_decision

    @classmethod
    def from_policy(cls, policy: Policy) -> "PolicyEngine":
        return cls(rules=policy.rules, default_decision=policy.default)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "PolicyEngine":
        """Load a YAML policy file (imported lazily to keep the engine pure)."""
        from .loader import load_policy

        return load_policy(path)

    @property
    def rules(self) -> list[PolicyRule]:
        return list(self._rules)

    @property
    def default_decision(self) -> Decision:
        return self._default

    def decide(
        self,
        subject: str,
        tool_name: str,
        args: Mapping[str, Any],
        ctx: Any = None,
        *,
        action: str | None = None,
        resource: str | None = None,
    ) -> PolicyDecision:
        """Return the decision for one proposed call.

        ``action`` and ``resource`` are supplied by the gateway from the tool's
        authorization metadata; when omitted they default to ``"invoke"`` and
        ``None``.
        """
        resolved_action = action if action is not None else "invoke"
        for rule in self._rules:
            if self._matches(rule, subject, tool_name, resolved_action, resource, ctx):
                return PolicyDecision(
                    decision=rule.decision,
                    reason=rule.reason,
                    matched_rule=rule.id,
                )
        return PolicyDecision(
            decision=self._default,
            reason="no matching rule; default decision",
            matched_rule=None,
        )

    def _matches(
        self,
        rule: PolicyRule,
        subject: str,
        tool_name: str,
        action: str,
        resource: str | None,
        ctx: Any,
    ) -> bool:
        if rule.subject not in ("*", subject):
            return False
        if rule.tool not in ("*", tool_name):
            return False
        if rule.action not in ("*", action):
            return False
        if not self._resource_matches(rule.resource, resource):
            return False
        return self._conditions_match(rule.conditions, ctx, resource)

    @staticmethod
    def _resource_matches(pattern: str | None, resource: str | None) -> bool:
        if pattern is None:
            return True
        if resource is None:
            return pattern == "*"
        return fnmatchcase(resource, pattern)

    @staticmethod
    def _conditions_match(
        conditions: dict[str, Any] | None, ctx: Any, resource: str | None
    ) -> bool:
        if not conditions:
            return True
        scope = tuple(getattr(ctx, "task_scope", ()) or ())
        for key, expected in conditions.items():
            if key == "outside_task_scope":
                actual = resource is None or resource not in scope
                if bool(actual) != bool(expected):
                    return False
            else:  # pragma: no cover - guarded by the schema
                raise PolicyConfigError(f"unhandled condition key: {key}")
        return True
