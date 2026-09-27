"""The deliberately small policy data model.

There are no roles, no inheritance, no attribute-based engine and no policy
language: a policy is an ordered list of flat rules plus a default decision.
The *first* rule whose subject, tool, action, resource and conditions all match
wins; unmatched calls fall to ``default`` (which defaults to ``deny``).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

#: Condition keys the engine understands. Unknown keys are a config error, so a
#: typo cannot silently weaken a policy.
KNOWN_CONDITIONS: frozenset[str] = frozenset({"outside_task_scope"})


class Decision(str, Enum):
    """The only three outcomes a policy can return."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


def _coerce_decision(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    return value


class PolicyRule(BaseModel):
    """A single, flat authorization rule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    subject: str = "*"  # agent id or "*"
    tool: str = "*"  # tool name or "*"
    action: str = "*"  # e.g. "invoke", "read", "write", "*"
    resource: str | None = None  # e.g. "workspace/*" glob; None means "any"
    conditions: dict[str, Any] | None = None
    decision: Decision
    reason: str

    _normalize_decision = field_validator("decision", mode="before")(_coerce_decision)

    @field_validator("conditions")
    @classmethod
    def _known_conditions(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        unknown = sorted(set(value) - KNOWN_CONDITIONS)
        if unknown:
            known = ", ".join(sorted(KNOWN_CONDITIONS))
            raise ValueError(
                f"unknown condition key(s): {', '.join(unknown)}; known: {known}"
            )
        return value


class Policy(BaseModel):
    """A complete policy document."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    default: Decision = Decision.DENY
    rules: list[PolicyRule] = Field(default_factory=list)

    _normalize_default = field_validator("default", mode="before")(_coerce_decision)


class PolicyDecision(BaseModel):
    """The engine's answer for one proposed call."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision: Decision
    reason: str
    matched_rule: str | None = None
