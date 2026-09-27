"""Composition root for the educational MVP.

This is the one place that wires the concrete mock model, the sandbox tools, the
policy and the trace recorder into an :class:`~agentsec.experiment.runner.ExperimentRunner`.
It is a *composition* helper only: it constructs objects and never runs an agent
loop, executes a tool, takes a policy decision or computes a metric. Keeping it
outside the core classes means the runner and CLI stay free of concrete-layer
imports.

The MVP is deterministic and offline: the deterministic ``MockModel``, the
in-memory sandbox tools and a policy loaded from YAML (or deny-by-default when
none is given). No provider, network or database is involved.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

from .agent import Agent
from .errors import ConfigError
from .eval import TraceEvaluator
from .experiment.config import ExperimentConfig
from .experiment.runner import ExperimentRunner
from .models.mock import MockModel, script_for
from .policy.base import PolicyEngine
from .policy.loader import load_policy
from .policy.schema import Decision
from .tools.factory import build_gateway
from .trace.recorder import TraceRecorder


def default_trace_path(config: ExperimentConfig) -> Path:
    """The deterministic trace path for an experiment when none is given."""
    return Path("runs") / config.experiment_id / "trace.jsonl"


def build_mvp_runner(
    config: ExperimentConfig,
    *,
    clock: Callable[[], datetime] | None = None,
) -> ExperimentRunner:
    """Wire the deterministic MVP stack for ``config`` into a runner.

    The returned runner owns its trace file: an existing file at the resolved
    path is replaced so one run writes one coherent trace (the recorder itself
    remains append-only). Raises :class:`ConfigError` for an unknown mock script
    or an unreadable policy.
    """
    agent_config = config.agent

    try:
        model = MockModel(script_for(config.mock_script))
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc

    path = Path(config.trace_path) if config.trace_path is not None else default_trace_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        path.unlink()

    recorder = TraceRecorder(
        path,
        run_id=agent_config.run_id,
        agent_id=agent_config.agent_id,
        model=model.describe().model_id,
        scenario=agent_config.scenario,
        clock=clock,
    )

    if config.policy_path is not None:
        policy = load_policy(config.policy_path)
    else:
        policy = PolicyEngine([], default_decision=Decision.DENY)

    gateway = build_gateway(
        policy,
        recorder=recorder,
        sandbox_files=config.sandbox_files,
        sandbox_db_writes=config.sandbox_db_writes,
        sandbox_db_seed=config.sandbox_db_seed,
    )
    agent = Agent(model, gateway, recorder, config=agent_config)
    return ExperimentRunner(agent, TraceEvaluator(), recorder)


__all__ = ["build_mvp_runner", "default_trace_path"]
