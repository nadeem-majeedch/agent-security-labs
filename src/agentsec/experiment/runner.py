"""The experiment runner: thin orchestration of exactly one run.

The runner coordinates components that already exist and does nothing they
already do:

* the :class:`~agentsec.agent.Agent` owns the agent loop;
* the gateway owns tool execution and authorization;
* the :class:`~agentsec.trace.recorder.TraceRecorder` owns writing the trace;
* the :class:`~agentsec.eval.base.Evaluator` owns analysis.

The runner only: validates the experiment configuration against the recorder and
agent, triggers one agent run, then hands the produced trace to the evaluator and
reports the two results side by side. It calls no tool, no gateway, no policy and
no model, runs no loop of its own, adds no metrics, and never retries.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from ..agent import Agent, RunResult
from ..errors import ConfigError, EvaluationError
from ..eval.base import EvaluationInput, EvaluationResult, Evaluator
from ..trace.recorder import TraceRecorder
from ..trace.writer import read_events
from .config import ExperimentConfig


class ExperimentResult(BaseModel):
    """The outcome of one experiment: agent result + evaluation, side by side.

    The agent's own :class:`~agentsec.agent.RunStatus` is preserved untouched;
    the evaluation is preserved untouched. ``error`` records an *orchestration*
    problem (for example an unreadable trace), never an agent failure - that
    stays in ``agent.error``.
    """

    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    run_id: str
    scenario: str
    agent: RunResult
    evaluation: EvaluationResult | None = None
    trace_path: Path | None = None
    error: str | None = None


class ExperimentRunner:
    """Run exactly one experiment and evaluate its trace."""

    def __init__(
        self,
        agent: Agent,
        evaluator: Evaluator,
        recorder: TraceRecorder | None = None,
    ) -> None:
        self._agent = agent
        self._evaluator = evaluator
        self._recorder = recorder

    @property
    def recorder(self) -> TraceRecorder | None:
        return self._recorder

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        """Execute one run and evaluate its trace.

        Raises :class:`ConfigError` for an inconsistent configuration (the
        documented failure mode for bad input). An agent failure is *not* an
        exception - it is preserved in the returned ``agent`` result. An
        unreadable/invalid trace is reported in ``error`` with
        ``evaluation=None`` rather than being reported as a clean run.
        """
        self._validate_config(config)

        run_result = self._agent.run(config.task)

        trace_path = self._recorder.path if self._recorder is not None else None
        evaluation: EvaluationResult | None = None
        error: str | None = None

        if self._recorder is not None:
            try:
                events = read_events(self._recorder.path)
                evaluation = self._evaluator.evaluate(
                    EvaluationInput.from_events(events)
                )
            except (OSError, ValueError, TypeError, EvaluationError) as exc:
                error = f"{type(exc).__name__}: {exc}"

        return ExperimentResult(
            experiment_id=config.experiment_id,
            run_id=self._recorder.run_id if self._recorder is not None else config.agent.run_id,
            scenario=config.agent.scenario,
            agent=run_result,
            evaluation=evaluation,
            trace_path=trace_path,
            error=error,
        )

    # -- validation ------------------------------------------------------------
    def _validate_config(self, config: ExperimentConfig) -> None:
        agent_config = self._agent.config
        if agent_config != config.agent:
            raise ConfigError(
                "experiment agent config does not match the runner's agent"
            )
        if config.trace_path is not None:
            if self._recorder is None:
                raise ConfigError("trace_path was set but no recorder was provided")
            if Path(config.trace_path) != self._recorder.path:
                raise ConfigError(
                    f"trace_path {config.trace_path} does not match the recorder "
                    f"path {self._recorder.path}"
                )
        if self._recorder is not None:
            for label, actual, expected in (
                ("run_id", self._recorder.run_id, config.agent.run_id),
                ("agent_id", self._recorder.agent_id, config.agent.agent_id),
                ("scenario", self._recorder.scenario, config.agent.scenario),
            ):
                if actual != expected:
                    raise ConfigError(
                        f"recorder {label} {actual!r} does not match config {expected!r}"
                    )


__all__ = ["ExperimentRunner", "ExperimentResult"]
