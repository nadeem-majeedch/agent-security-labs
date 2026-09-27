"""Experiment configuration: one experiment, one run.

Configuration is deliberately thin and composed, not copied: an experiment
declares its identity and task, and embeds the existing
:class:`~agentsec.agent.AgentConfig` rather than duplicating the agent's fields.
It contains nothing about capabilities that do not exist (no temperature, seed,
retries, parallelism or provider credentials).

Loading YAML is kept separate from execution and uses the same strict pattern as
the policy loader: a malformed document raises :class:`ConfigError` rather than
quietly defaulting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..agent import AgentConfig
from ..errors import ConfigError


class ExperimentConfig(BaseModel):
    """Declarative description of a single experiment run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    experiment_id: str = Field(min_length=1)
    task: str
    #: Reuses the agent's own configuration; not a parallel copy of its fields.
    agent: AgentConfig = Field(default_factory=AgentConfig)
    #: Optional expected trace path. The recorder owns writing; when set, the
    #: runner checks it matches the recorder so one run writes one trace.
    trace_path: Path | None = None
    #: Optional policy file. When omitted, the MVP composition uses a
    #: deny-by-default policy (safe and deterministic).
    policy_path: Path | None = None
    #: Deterministic mock fixture script (see ``agentsec.models.mock``).
    mock_script: str = "benign"
    #: Optional initial contents for the in-memory ``fs_sandbox`` tool, keyed by
    #: virtual path. Purely synthetic fixture data held in memory; it never
    #: touches the host filesystem, so a lab can make a sandbox tool return
    #: controlled content. Empty by default (an empty workspace).
    sandbox_files: dict[str, str] = Field(default_factory=dict)
    #: When true, the in-memory ``mock_db`` tool is built writable so a lab can
    #: observe a synthetic state change. Still memory-only and per-instance:
    #: no real database is involved, and every existing lab keeps the default
    #: read-only sandbox. Off by default.
    sandbox_db_writes: bool = False
    #: Optional replacement seed for the in-memory ``mock_db`` tool, keyed by
    #: table name. Purely synthetic fixture data held in memory; it never touches
    #: a host database and leaves the global database defaults untouched, so a
    #: lab can give the sandbox a controlled record. Empty by default (the
    #: shared ``mock_db`` seed is used).
    sandbox_db_seed: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    """Read ``path`` as YAML and return an :class:`ExperimentConfig`."""
    resolved = Path(path)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read experiment config {resolved}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"{resolved}: experiment config must be a mapping")
    try:
        return ExperimentConfig.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'/'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"{resolved}: invalid experiment config: {details}") from exc


__all__ = ["ExperimentConfig", "load_experiment_config"]
