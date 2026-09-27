"""Tests for the thin, single-run experiment runner."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentsec.agent import Agent, AgentConfig, RunResult, RunStatus
from agentsec.errors import ConfigError, ModelError
from agentsec.eval import EvaluationInput, EvaluationResult, RunOutcome, TraceEvaluator
from agentsec.experiment import ExperimentConfig, ExperimentRunner
from agentsec.models.base import Capabilities, ModelInfo
from agentsec.models.mock import MockAction, MockModel, MockScript, MockStep, script_for
from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, PolicyRule
from agentsec.tools import build_gateway
from agentsec.trace.recorder import TraceRecorder
from agentsec.trace.schema import RunStartedEvent
from agentsec.trace.writer import read_events

FIXED = datetime(2026, 1, 1, tzinfo=timezone.utc)


# -- policies ------------------------------------------------------------------
def allow_calc() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="allow-calc", tool="calculator", decision=Decision.ALLOW, reason="ok")],
        default_decision=Decision.DENY,
    )


def allow_all() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="allow-all", decision=Decision.ALLOW, reason="ok")],
        default_decision=Decision.DENY,
    )


def deny_all() -> PolicyEngine:
    return PolicyEngine([], default_decision=Decision.DENY)


def require_calc() -> PolicyEngine:
    return PolicyEngine(
        [PolicyRule(id="req", tool="calculator", decision=Decision.REQUIRE_APPROVAL, reason="r")],
        default_decision=Decision.DENY,
    )


# -- scripts -------------------------------------------------------------------
def answer_only(text: str, contains: str | None = None) -> MockScript:
    return MockScript(
        name="answer_only",
        steps=[MockStep(action=MockAction(kind="answer", text=text), contains=contains)],
        fallback=MockAction(kind="answer", text="fallback"),
    )


def _answer(text: str, **matchers) -> MockStep:
    return MockStep(action=MockAction(kind="answer", text=text), **matchers)


def _tool(name: str, arguments: dict, **matchers) -> MockStep:
    return MockStep(
        action=MockAction(kind="tool_call", tool_name=name, arguments=arguments), **matchers
    )


class RaisingAdapter:
    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def complete(self, messages, *, temperature=None, seed=None, tools=None):  # noqa: ARG002
        raise self._exc

    def capabilities(self):
        return Capabilities(supports_temperature=False, supports_seed=False, supports_tools=True)

    def describe(self):
        return ModelInfo(provider="fake", model_id="fake-v1")


# -- stack helpers -------------------------------------------------------------
def make_stack(
    tmp_path,
    *,
    policy,
    script=None,
    model=None,
    scenario="LAB-01-a",
    run_id="run-1",
    agent_id="agent-1",
    max_steps=8,
    approval=None,
):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id=run_id,
        agent_id=agent_id,
        model="mock-v1",
        scenario=scenario,
        clock=lambda: FIXED,
    )
    gateway = build_gateway(policy, recorder=rec)
    config = AgentConfig(
        agent_id=agent_id, run_id=run_id, scenario=scenario, max_steps=max_steps
    )
    agent = Agent(model or MockModel(script), gateway, rec, config=config, approval=approval)
    runner = ExperimentRunner(agent, TraceEvaluator(), rec)
    return runner, rec, config


def run_experiment(runner, config, task, experiment_id="exp-1"):
    return runner.run(
        ExperimentConfig(experiment_id=experiment_id, task=task, agent=config)
    )


# -- flows ---------------------------------------------------------------------
def test_benign_experiment(tmp_path):
    runner, _, config = make_stack(tmp_path, policy=deny_all(), script=answer_only("hi there", "hello"))
    result = run_experiment(runner, config, "hello agent")
    assert result.agent.status is RunStatus.COMPLETED
    assert result.agent.output == "hi there"
    assert result.evaluation.status is RunOutcome.COMPLETED
    assert result.evaluation.metrics["model_calls"] == 1
    assert result.evaluation.metrics["tool_requests"] == 0
    assert result.error is None


def test_allowed_tool_experiment(tmp_path):
    runner, _, config = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    result = run_experiment(runner, config, "please add 2 and 3")
    assert result.agent.status is RunStatus.COMPLETED
    assert result.evaluation.metrics["tool_requests"] == 1
    assert result.evaluation.metrics["tool_executions"] == 1
    assert result.evaluation.tool_calls == {"calculator": 1}
    assert result.evaluation.tool_results["ok"] == 1


def test_denied_tool_experiment(tmp_path):
    runner, _, config = make_stack(tmp_path, policy=deny_all(), script=script_for("benign"))
    result = run_experiment(runner, config, "please add 2 and 3")
    assert result.evaluation.decisions["deny"] == 1
    assert result.evaluation.tool_results["denied"] == 1
    assert result.evaluation.metrics["tool_executions"] == 0


def test_pending_approval_experiment(tmp_path):
    runner, _, config = make_stack(tmp_path, policy=require_calc(), script=script_for("benign"))
    result = run_experiment(runner, config, "please add 2 and 3")
    assert result.evaluation.decisions["require_approval"] == 1
    assert result.evaluation.tool_results["pending_approval"] == 1
    assert result.evaluation.metrics["tool_executions"] == 0


def test_multistep_experiment(tmp_path):
    model = MockModel(
        MockScript(
            name="multi",
            steps=[
                _tool("calculator", {"expr": "2+3"}, contains="add", is_tool_result=False),
                _tool("calculator", {"expr": "4+5"}, contains='"value": 5.0', is_tool_result=True),
                _answer("both done", contains='"value": 9.0', is_tool_result=True),
            ],
            fallback=MockAction(kind="answer", text="fallback"),
        )
    )
    runner, _, config = make_stack(tmp_path, policy=allow_calc(), model=model, max_steps=6)
    result = run_experiment(runner, config, "please add 2 and 3")
    assert result.agent.steps == 3
    assert result.evaluation.metrics["tool_requests"] == 2
    assert result.evaluation.tool_calls == {"calculator": 2}


def test_step_limit_experiment(tmp_path):
    model = MockModel(
        MockScript(
            name="loop",
            steps=[_tool("calculator", {"expr": "1+1"})],
            fallback=MockAction(kind="tool_call", tool_name="calculator", arguments={"expr": "1+1"}),
        )
    )
    runner, _, config = make_stack(tmp_path, policy=allow_calc(), model=model, max_steps=3)
    result = run_experiment(runner, config, "keep going")
    assert result.agent.status is RunStatus.STEP_LIMIT
    assert result.evaluation.status is RunOutcome.STEP_LIMIT
    assert result.evaluation.flags["reached_step_limit"] is True


def test_agent_failure_experiment(tmp_path):
    runner, _, config = make_stack(
        tmp_path, policy=allow_all(), model=RaisingAdapter(ModelError("boom"))
    )
    result = run_experiment(runner, config, "hello")
    assert result.agent.status is RunStatus.FAILED
    assert result.evaluation.status is RunOutcome.FAILED
    assert result.evaluation.metrics["run_failed"] == 1


# -- trace + evaluator integration --------------------------------------------
def test_trace_output_exists_and_belongs_to_the_run(tmp_path):
    runner, rec, config = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    result = run_experiment(runner, config, "please add 2 and 3")
    assert result.trace_path == rec.path
    assert rec.path.is_file()
    events = read_events(rec.path)
    assert events[0]["event_type"] == "run_started"
    assert {e["run_id"] for e in events} == {"run-1"}


def test_deterministic_experiment(tmp_path):
    def once(directory):
        runner, rec, config = make_stack(
            directory, policy=allow_calc(), script=script_for("benign")
        )
        result = run_experiment(runner, config, "please add 2 and 3")
        return result, rec.path.read_text(encoding="utf-8")

    first, first_trace = once(tmp_path / "a")
    second, second_trace = once(tmp_path / "b")
    assert first.agent.output == second.agent.output
    assert first.agent.steps == second.agent.steps
    assert first.evaluation == second.evaluation
    assert first_trace == second_trace


class SpyEvaluator:
    """Records the input it is given and returns a fixed result."""

    VERSION = "spy-v1"

    def __init__(self) -> None:
        self.inputs: list[EvaluationInput] = []

    @property
    def version(self) -> str:
        return self.VERSION

    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        self.inputs.append(data)
        return EvaluationResult(version=self.VERSION, status=RunOutcome.INCOMPLETE)


def test_evaluator_receives_the_completed_trace(tmp_path):
    runner, rec, config = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    spy = SpyEvaluator()
    runner._evaluator = spy  # noqa: SLF001 - deliberate injection of a test double
    result = run_experiment(runner, config, "please add 2 and 3")
    assert len(spy.inputs) == 1
    types = [e["event_type"] for e in spy.inputs[0].events]
    assert "run_completed" in types
    # the runner preserves the evaluator's result untouched (no new metrics)
    assert result.evaluation is not None
    assert result.evaluation.version == "spy-v1"
    assert result.evaluation.status is RunOutcome.INCOMPLETE


class FakeAgent:
    """A stand-in agent that records calls and writes one trace event."""

    def __init__(self, config: AgentConfig, recorder: TraceRecorder, status=RunStatus.COMPLETED):
        self.config = config
        self._rec = recorder
        self._status = status
        self.calls: list[str] = []

    def run(self, task: str) -> RunResult:
        self.calls.append(task)
        self._rec.emit_event(
            RunStartedEvent, config_ref="cfg", scenario_id=self.config.scenario
        )
        return RunResult(status=self._status, output="done", steps=1, trace_path=self._rec.path)


class NoWriteAgent:
    """An agent that never writes a trace (to exercise the missing-trace path)."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.calls = 0

    def run(self, task: str) -> RunResult:
        self.calls += 1
        return RunResult(status=RunStatus.COMPLETED, output="done", steps=1)


def _fake_config(scenario="LAB-01-a", run_id="run-1", agent_id="agent-1") -> AgentConfig:
    return AgentConfig(agent_id=agent_id, run_id=run_id, scenario=scenario)


def test_runner_delegates_and_calls_the_agent_once(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    config = _fake_config()
    fake = FakeAgent(config, rec)
    runner = ExperimentRunner(fake, TraceEvaluator(), rec)
    result = runner.run(ExperimentConfig(experiment_id="e", task="do it", agent=config))
    assert fake.calls == ["do it"]
    assert result.agent.status is RunStatus.COMPLETED
    assert result.evaluation is not None


def test_no_hidden_retry_when_the_agent_fails(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    config = _fake_config()
    fake = FakeAgent(config, rec, status=RunStatus.FAILED)
    runner = ExperimentRunner(fake, TraceEvaluator(), rec)
    result = runner.run(ExperimentConfig(experiment_id="e", task="do it", agent=config))
    assert len(fake.calls) == 1
    assert result.agent.status is RunStatus.FAILED


def test_missing_trace_is_reported_not_silent(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="run-1",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    config = _fake_config()
    runner = ExperimentRunner(NoWriteAgent(config), TraceEvaluator(), rec)
    result = runner.run(ExperimentConfig(experiment_id="e", task="do it", agent=config))
    assert result.evaluation is None
    assert result.error is not None


def test_runner_without_recorder_skips_evaluation(tmp_path):
    config = _fake_config()
    runner = ExperimentRunner(NoWriteAgent(config), TraceEvaluator(), recorder=None)
    result = runner.run(ExperimentConfig(experiment_id="e", task="do it", agent=config))
    assert result.agent.status is RunStatus.COMPLETED
    assert result.evaluation is None
    assert result.error is None
    assert result.trace_path is None


# -- configuration errors ------------------------------------------------------
def test_agent_config_mismatch_raises(tmp_path):
    runner, _, _ = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    other = AgentConfig(agent_id="agent-9", run_id="run-1", scenario="LAB-01-a")
    with pytest.raises(ConfigError):
        runner.run(ExperimentConfig(experiment_id="e", task="x", agent=other))


def test_trace_path_mismatch_raises(tmp_path):
    runner, _, config = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    with pytest.raises(ConfigError):
        runner.run(
            ExperimentConfig(
                experiment_id="e", task="x", agent=config, trace_path=tmp_path / "other.jsonl"
            )
        )


def test_trace_path_without_recorder_raises(tmp_path):
    config = _fake_config()
    runner = ExperimentRunner(NoWriteAgent(config), TraceEvaluator(), recorder=None)
    with pytest.raises(ConfigError):
        runner.run(
            ExperimentConfig(
                experiment_id="e", task="x", agent=config, trace_path=tmp_path / "t.jsonl"
            )
        )


def test_recorder_identity_mismatch_raises(tmp_path):
    rec = TraceRecorder(
        tmp_path / "trace.jsonl",
        run_id="other-run",
        agent_id="agent-1",
        model="mock-v1",
        scenario="LAB-01-a",
        clock=lambda: FIXED,
    )
    config = _fake_config(run_id="run-1")
    runner = ExperimentRunner(FakeAgent(config, rec), TraceEvaluator(), rec)
    with pytest.raises(ConfigError):
        runner.run(ExperimentConfig(experiment_id="e", task="x", agent=config))


def test_runner_preserves_agent_status_vocabulary(tmp_path):
    runner, _, config = make_stack(
        tmp_path, policy=allow_calc(), script=script_for("benign")
    )
    result = run_experiment(runner, config, "please add 2 and 3")
    # no separate success/failure boolean: the agent's own status is preserved
    assert result.agent.status is RunStatus.COMPLETED
    assert isinstance(result.evaluation.status, RunOutcome)
