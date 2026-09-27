"""LAB-01 - observe a benign agent: validation tests.

These prove the lab's configuration and scenario load, that the scenario's
experiment matches the runnable config, that a run passes every expectation,
that the trace is valid and ordered, and that the whole thing replays
byte-identically. Fully offline: mock model + sandbox calculator only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from agentsec.agent import RunStatus
from agentsec.eval import EvaluationInput, RunOutcome, TraceEvaluator
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner
from agentsec.scenarios import ScenarioStatus, load_scenario
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "labs" / "LAB-01-benign-agent"
CONFIG = LAB / "config.yaml"
SCENARIO = LAB / "scenario.yaml"
TRACE_NAME = "trace.jsonl"

TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def run_lab01(tmp_path: Path):
    """Run the LAB-01 experiment into ``tmp_path`` with a fixed clock."""
    config = load_experiment_config(CONFIG)
    config = config.model_copy(update={"trace_path": tmp_path / TRACE_NAME})
    runner = build_mvp_runner(config, clock=lambda: TS)
    result = runner.run(config)
    return result, load_scenario(SCENARIO)


# -- files / loading -----------------------------------------------------------
def test_lab01_files_exist():
    for name in ("README.md", "config.yaml", "scenario.yaml"):
        assert (LAB / name).is_file()


def test_lab01_readme_is_student_facing():
    text = (LAB / "README.md").read_text(encoding="utf-8")
    for heading in (
        "Learning objectives",
        "Prerequisites",
        "Procedure",
        "Questions to answer",
        "Expected outcome",
        "Completion checklist",
    ):
        assert heading in text
    # student material carries an explicit no-claims disclaimer
    assert "no research claim" in " ".join(text.lower().split())


def test_lab01_config_loads():
    config = load_experiment_config(CONFIG)
    assert config.experiment_id == "lab01_benign"
    assert config.mock_script == "benign"
    assert config.policy_path is not None
    assert config.agent.run_id == "lab01-run-1"


def test_lab01_scenario_loads_with_id():
    scenario = load_scenario(SCENARIO)
    assert scenario.scenario_id == "LAB-01-benign-agent"
    assert scenario.definition().title
    assert scenario.definition().description


def test_lab01_scenario_experiment_matches_config():
    """scenario.yaml and config.yaml must describe the same experiment."""
    scenario = load_scenario(SCENARIO)
    assert scenario.prepare() == load_experiment_config(CONFIG)


# -- execution / scenario ------------------------------------------------------
def test_lab01_scenario_passes(tmp_path):
    result, scenario = run_lab01(tmp_path)
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.PASSED, [
        (c.name, c.expected, c.observed) for c in outcome.checks if not c.matched
    ]
    assert outcome.error is None
    assert all(check.matched for check in outcome.checks)


def test_lab01_expected_observations_hold(tmp_path):
    result, _ = run_lab01(tmp_path)
    evaluation = result.evaluation
    assert result.agent.status is RunStatus.COMPLETED
    assert evaluation is not None
    assert evaluation.status is RunOutcome.COMPLETED
    assert evaluation.metrics["tool_requests"] == 1
    assert evaluation.metrics["tool_executions"] == 1
    assert evaluation.decisions.get("allow") == 1
    assert evaluation.decisions.get("deny", 0) == 0
    assert evaluation.decisions.get("require_approval", 0) == 0
    assert evaluation.tool_calls == {"calculator": 1}
    assert evaluation.tool_results.get("ok") == 1
    assert evaluation.flags.get("produced_final_output") is True
    assert "5" in (result.agent.output or "")


def test_lab01_trace_is_valid(tmp_path):
    run_lab01(tmp_path)
    report = validate_jsonl(tmp_path / TRACE_NAME)
    assert report.issues == [], report.issues


def test_lab01_trace_is_ordered(tmp_path):
    run_lab01(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    seq = {event["event_type"]: event["seq"] for event in events}
    assert seq["run_started"] < seq["tool_requested"]
    assert seq["tool_requested"] < seq["policy_decision"]
    assert seq["policy_decision"] < seq["tool_executed"]
    assert seq["tool_executed"] < seq["tool_result"]
    assert seq["tool_result"] < seq["run_completed"]

    # the tool request and its decision are linked by parent_event_id
    requested = next(e for e in events if e["event_type"] == "tool_requested")
    decision = next(e for e in events if e["event_type"] == "policy_decision")
    executed = next(e for e in events if e["event_type"] == "tool_executed")
    assert decision["parent_event_id"] == requested["event_id"]
    assert executed["parent_event_id"] == requested["event_id"]
    assert decision["decision"] == "allow"
    assert requested["tool_name"] == "calculator"


def test_lab01_scenario_evidence_references_trace(tmp_path):
    result, scenario = run_lab01(tmp_path)
    outcome = scenario.interpret(result)
    types = {ref.event_type for ref in outcome.evidence}
    assert {"run_started", "tool_requested", "tool_executed", "run_completed"} <= types


def test_lab01_outcome_is_serializable(tmp_path):
    result, scenario = run_lab01(tmp_path)
    outcome = scenario.interpret(result)
    serialized = outcome.model_dump_json()
    assert '"status":"passed"' in serialized.replace(" ", "")


def test_lab01_replay_is_byte_identical(tmp_path):
    run_lab01(tmp_path)
    first = (tmp_path / TRACE_NAME).read_bytes()
    run_lab01(tmp_path)
    second = (tmp_path / TRACE_NAME).read_bytes()
    assert first == second


def test_lab01_evaluation_is_deterministic(tmp_path):
    result, _ = run_lab01(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    first = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    second = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    assert first == second


# -- safety / offline ----------------------------------------------------------
def test_lab01_only_uses_sandbox_tools(tmp_path):
    result, _ = run_lab01(tmp_path)
    evaluation = result.evaluation
    assert evaluation is not None
    assert set(evaluation.tool_calls) <= {"calculator", "fs_sandbox", "mock_db"}
    # this lab exercises only the arithmetic sandbox
    assert evaluation.tool_calls == {"calculator": 1}


def test_lab01_yaml_is_declarative(tmp_path):
    """Lab YAML must not name code, imports or shell commands."""
    for path in (CONFIG, SCENARIO):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for forbidden in ("!!python", "__import__", "subprocess", "shell:", "eval("):
            assert forbidden not in lowered, f"{path.name} contains {forbidden!r}"
        document = yaml.safe_load(text)
        assert isinstance(document, dict)


def test_lab01_uses_no_secrets_or_real_paths(tmp_path):
    """The lab config references only sandbox fixtures, never host paths."""
    config = load_experiment_config(CONFIG)
    assert config.mock_script == "benign"
    assert config.policy_path is not None
    assert config.policy_path.parts[0] == "policies"
    assert config.trace_path is None
