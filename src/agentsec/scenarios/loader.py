"""Load a scenario definition from YAML.

Strict, like the policy and experiment loaders: malformed YAML, a non-mapping
document or a missing/invalid field raises
:class:`~agentsec.errors.ScenarioConfigError`. Only declarative pydantic fields
are accepted; no class names or Python objects can be named from the file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ..errors import ScenarioConfigError
from .base import DeclarativeScenario, ScenarioDef


def parse_scenario(data: Any) -> DeclarativeScenario:
    """Build a scenario from an already-parsed definition mapping."""
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ScenarioConfigError(
            f"scenario document must be a mapping, got {type(data).__name__}"
        )
    try:
        definition = ScenarioDef.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'/'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ScenarioConfigError(f"invalid scenario: {details}") from exc
    return DeclarativeScenario(definition)


def load_scenario(path: str | Path) -> DeclarativeScenario:
    """Read ``path`` as YAML and return a scenario."""
    resolved = Path(path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScenarioConfigError(f"could not read scenario {resolved}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ScenarioConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    try:
        return parse_scenario(data)
    except ScenarioConfigError as exc:
        raise ScenarioConfigError(f"{resolved}: {exc}") from exc


__all__ = ["parse_scenario", "load_scenario"]
