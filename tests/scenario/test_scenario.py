"""Tests for the declarative scenario abstraction and its interpretation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agentsec.agent import AgentConfig, RunResult, RunStatus
from agentsec.eval import EvaluationResult, RunOutcome
from agentsec.experiment import ExperimentConfig, ExperimentResult
from agentsec.models.mock import MockAction, MockScript, MockStep
from agentsec.mvp import build_mvp_runner
from agentsec.scenarios import (
    DeclarativeScenario,
    ExpectedObservation,
    ScenarioDef,
    ScenarioStatus,
)

REPO = Path(__file__).resolve().parents[2]
LEAST_PRIVILEGE = REPO / "policies" / "examples" / "least_privilege_v1.yaml"
DENY_BY_DEFAULT = REPO / "policies" / "examples" / "deny_by_default.yaml"


def make_config(
    tmp_path: Path,
    *,
    task: str = "please add 2 and 3",
    mock_script: str = "benign",
    policy_path: Path = LEAST_PRIVILEGE,
    max_steps: int = 6,
    run_id: str = "run-1",
    scenario: str = "LAB-01-a",
) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="s1",
        task=task,
        mock_script=mock_script,
        policy_path=policy_path,
        trace_path=tmp_path / "trace.jsonl",
        agent=AgentConfig(run_id=run_id, scenario=scenario, max_steps=max_steps),
    )


def run(config: ExperimentConfig) -> ExperimentResult:
    return build_mvp_runner(config).run(config)


def make_scenario(config: ExperimentConfig, expected: ExpectedObservation, sid="sc-1"):
    return DeclarativeScenario(
        ScenarioDef(scenario_id=sid, expected=expected, experiment=config)
    )


# -- construction / validation -------------------------------------------------
def test_scenario_def_requires_experiment():
    with pytest.raises(ValidationError):
        ScenarioDef(scenario_id="x")


def test_scenario_def_requires_id():
    with pytest.raises(ValidationError):
        ScenarioDef(experiment=ExperimentConfig(experiment_id="e", task="t"))


def test_scenario_def_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ScenarioDef(
            scenario_id="x",
            experiment=ExperimentConfig(experiment_id="e", task="t"),
            payload={"nope": 1},
        )


def test_expected_observation_rejects_unknown_and_negative():
    with pytest.raises(ValidationError):
        ExpectedObservation(security_score=1)
    with pytest.raises(ValidationError):
        ExpectedObservation(tool_requests=-1)


def test_configured_yields_only_set_fields():
    expected = ExpectedObservation(tool_requests=1, policy_denials=0)
    assert dict(expected.configured()) == {"tool_requests": 1, "policy_denials": 0}


def test_scenario_identity_and_prepare():
    config = ExperimentConfig(experiment_id="e", task="t")
    scenario = make_scenario(config, ExpectedObservation())
    assert scenario.scenario_id == "sc-1"
    assert scenario.definition().scenario_id == "sc-1"
    assert scenario.prepare() == config


# -- interpretation ------------------------------------------------------------
def test_benign_expected_outcome_passes(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(
        config,
        ExpectedObservation(
            agent_status=RunStatus.COMPLETED,
            evaluation_status=RunOutcome.COMPLETED,
            tool_requests=1,
            tool_executions=1,
            tool_results_ok=1,
            policy_denials=0,
            requested_tools=("calculator",),
        ),
    )
    outcome = scenario.interpret(run(config))
    assert outcome.status is ScenarioStatus.PASSED
    assert outcome.run_id == "run-1"
    assert all(check.matched for check in outcome.checks)
    assert outcome.warnings == []


def test_expected_vs_observed_mismatch_fails(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(policy_denials=1))
    outcome = scenario.interpret(run(config))
    assert outcome.status is ScenarioStatus.FAILED
    assert [c.name for c in outcome.checks] == ["policy_denials"]
    assert outcome.checks[0].matched is False
    assert outcome.checks[0].expected == 1
    assert outcome.checks[0].observed == 0


def test_requested_tools_mismatch_fails(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(requested_tools=("fs_sandbox",)))
    outcome = scenario.interpret(run(config))
    assert outcome.status is ScenarioStatus.FAILED


def test_output_contains_check(tmp_path):
    config = make_config(tmp_path)
    ok = make_scenario(config, ExpectedObservation(output_contains="The sum"))
    assert ok.interpret(run(config)).status is ScenarioStatus.PASSED
    bad = make_scenario(config, ExpectedObservation(output_contains="nope"))
    assert bad.interpret(run(config)).status is ScenarioStatus.FAILED


def test_denied_scenario_passes(tmp_path):
    config = make_config(tmp_path, policy_path=DENY_BY_DEFAULT)
    scenario = make_scenario(
        config,
        ExpectedObservation(
            agent_status=RunStatus.COMPLETED,
            policy_denials=1,
            tool_executions=0,
            tool_results_denied=1,
        ),
    )
    assert scenario.interpret(run(config)).status is ScenarioStatus.PASSED


def test_pending_approval_scenario_passes(tmp_path):
    config = make_config(
        tmp_path,
        task="look up the key",
        mock_script="authorization_violation",
    )
    scenario = make_scenario(
        config,
        ExpectedObservation(
            policy_approvals_required=1,
            tool_results_pending_approval=1,
            tool_executions=0,
        ),
    )
    assert scenario.interpret(run(config)).status is ScenarioStatus.PASSED


def test_step_limit_scenario_passes(tmp_path, monkeypatch):
    loop = MockScript(
        name="loop",
        steps=[
            MockStep(
                action=MockAction(
                    kind="tool_call", tool_name="calculator", arguments={"expr": "1+1"}
                )
            )
        ],
        fallback=MockAction(
            kind="tool_call", tool_name="calculator", arguments={"expr": "1+1"}
        ),
    )
    monkeypatch.setattr("agentsec.mvp.script_for", lambda name: loop)
    config = make_config(tmp_path, max_steps=3)
    scenario = make_scenario(
        config,
        ExpectedObservation(
            agent_status=RunStatus.STEP_LIMIT,
            evaluation_status=RunOutcome.STEP_LIMIT,
            reached_step_limit=True,
        ),
    )
    assert scenario.interpret(run(config)).status is ScenarioStatus.PASSED


# -- inconclusive / malformed --------------------------------------------------
def test_no_expectations_is_inconclusive(tmp_path):
    config = make_config(tmp_path)
    outcome = make_scenario(config, ExpectedObservation()).interpret(run(config))
    assert outcome.status is ScenarioStatus.INCONCLUSIVE
    assert "no expected observations" in " ".join(outcome.warnings)


def test_missing_evaluation_is_inconclusive(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_requests=1))
    result = ExperimentResult(
        experiment_id="s1",
        run_id="run-1",
        scenario="LAB-01-a",
        agent=RunResult(status=RunStatus.COMPLETED, output="x", steps=1),
        evaluation=None,
        error="TraceReadError: boom",
    )
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.INCONCLUSIVE
    assert outcome.error == "TraceReadError: boom"
    assert outcome.evidence == []


def test_run_id_mismatch_is_inconclusive(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_requests=1))
    result = ExperimentResult(
        experiment_id="s1",
        run_id="other-run",
        scenario="LAB-01-a",
        agent=RunResult(status=RunStatus.COMPLETED, output="x", steps=1),
        evaluation=EvaluationResult(version="v1", status=RunOutcome.COMPLETED),
    )
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.INCONCLUSIVE
    assert "does not match" in " ".join(outcome.warnings)


def test_incomplete_evaluation_is_inconclusive(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_requests=0))
    result = ExperimentResult(
        experiment_id="s1",
        run_id="run-1",
        scenario="LAB-01-a",
        agent=RunResult(status=RunStatus.COMPLETED, output="x", steps=1),
        evaluation=EvaluationResult(
            version="v1",
            status=RunOutcome.INCOMPLETE,
            warnings=["no terminal event (run_completed/run_failed)"],
        ),
    )
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.INCONCLUSIVE
    assert "incomplete" in " ".join(outcome.warnings)


# -- evidence / determinism / isolation ---------------------------------------
def test_outcome_references_evidence(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_executions=1))
    outcome = scenario.interpret(run(config))
    assert outcome.evidence
    assert {ref.event_type for ref in outcome.evidence} >= {
        "run_started",
        "tool_executed",
        "run_completed",
    }


def test_interpretation_is_deterministic(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_executions=1))
    result = run(config)
    assert scenario.interpret(result) == scenario.interpret(result)


def test_interpretation_does_not_mutate_the_trace(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_executions=1))
    result = run(config)
    before = (tmp_path / "trace.jsonl").read_bytes()
    scenario.interpret(result)
    assert (tmp_path / "trace.jsonl").read_bytes() == before


def test_interpretation_does_not_execute_anything(tmp_path, monkeypatch):
    from agentsec.agent import Agent
    from agentsec.policy.base import PolicyEngine
    from agentsec.tools.gateway import ToolGateway

    config = make_config(tmp_path)
    result = run(config)  # produce a real result first

    def explode(*args, **kwargs):  # pragma: no cover - must not run
        raise AssertionError("scenario interpretation must not execute")

    monkeypatch.setattr(ToolGateway, "invoke", explode)
    monkeypatch.setattr(PolicyEngine, "decide", explode)
    monkeypatch.setattr(Agent, "run", explode)

    scenario = make_scenario(config, ExpectedObservation(tool_executions=1))
    assert scenario.interpret(result).status is ScenarioStatus.PASSED


# -- serialization -------------------------------------------------------------
def test_scenario_def_and_outcome_round_trip(tmp_path):
    config = make_config(tmp_path)
    scenario = make_scenario(config, ExpectedObservation(tool_executions=1))
    definition_json = scenario.definition().model_dump_json()
    assert ScenarioDef.model_validate_json(definition_json) == scenario.definition()

    outcome = scenario.interpret(run(config))
    restored = json.loads(outcome.model_dump_json())
    assert restored["status"] == "passed"
    assert restored["scenario_id"] == "sc-1"
    assert restored["checks"][0]["name"] == "tool_executions"
