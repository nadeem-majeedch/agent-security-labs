"""Load a YAML policy document into a :class:`PolicyEngine`.

Parsing is strict: malformed YAML, a non-mapping document, an unknown decision,
a missing field or an unknown condition key all raise
:class:`~agentsec.errors.PolicyConfigError` with a readable message. A policy
that cannot be understood must never silently fall back to something permissive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ..errors import PolicyConfigError
from .base import PolicyEngine
from .schema import Policy


def parse_policy(data: Any) -> PolicyEngine:
    """Build an engine from an already-parsed policy mapping."""
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise PolicyConfigError(
            f"policy document must be a mapping, got {type(data).__name__}"
        )
    try:
        policy = Policy.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'/'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise PolicyConfigError(f"invalid policy: {details}") from exc
    return PolicyEngine.from_policy(policy)


def load_policy(path: str | Path) -> PolicyEngine:
    """Read ``path`` as YAML and return an engine."""
    resolved = Path(path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyConfigError(f"could not read policy {resolved}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise PolicyConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    try:
        return parse_policy(data)
    except PolicyConfigError as exc:
        raise PolicyConfigError(f"{resolved}: {exc}") from exc


def load_policy_text(text: str) -> PolicyEngine:
    """Parse a YAML string (used by tests and callers without a file)."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PolicyConfigError(f"invalid YAML: {exc}") from exc
    return parse_policy(data)
