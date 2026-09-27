"""LAB-07 - data leakage: validation tests.

These prove the lab's configuration and scenario load, that the scenario's
experiment matches the runnable config, that a run passes every expectation,
that both the synthetic read and the synthetic send are policy-*allowed* and
actually execute, that the disclosed marker is observable in
``mock_email.args_redacted.body`` and *nowhere* it should not be, that the
synthetic database result stays hash-only, that the sandbox database seed is a
default-off, per-lab, in-memory overlay, and that the whole thing replays
byte-identically. Fully offline: mock model + sandbox tools only.

The important contrast is asserted directly: unlike LAB-04 (deny) and LAB-06
(authorized but unnecessary), here **two** task-authorized operations both take
``allow`` and both execute - and content still crosses an egress boundary.
"""

from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from agentsec.agent import RunStatus
from agentsec.errors import ConfigError, ToolValidationError
from agentsec.eval import EvaluationInput, RunOutcome, TraceEvaluator
from agentsec.experiment import load_experiment_config
from agentsec.experiment.config import ExperimentConfig
from agentsec.mvp import build_mvp_runner
from agentsec.policy.base import PolicyEngine
from agentsec.policy.schema import Decision, PolicyRule
from agentsec.scenarios import ScenarioStatus, load_scenario
from agentsec.scenarios.base import ExpectedObservation
from agentsec.tools.base import ToolContext
from agentsec.tools.factory import build_tools
from agentsec.tools.gateway import ToolGateway
from agentsec.tools.mock_db import MockDatabaseTool
from agentsec.tools.mock_email import MockEmailTool
from agentsec.trace.redact import DEFAULT_PATTERNS, DEFAULT_REDACTOR
from agentsec.trace.validate import validate_jsonl
from agentsec.trace.writer import read_events

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "labs" / "LAB-07-data-leakage"
CONFIG = LAB / "config.yaml"
SCENARIO = LAB / "scenario.yaml"
POLICY = REPO / "policies" / "examples" / "lab07_data_leakage_v1.yaml"
TRACE_NAME = "trace.jsonl"

MARKER = "SYNTHETIC-DEMO-DISCLOSURE-A1"
RECIPIENT = "reports@example.invalid"
SUBJECT = "Account record REC-001"
DB_QUERY = "SELECT * FROM records WHERE record_id = 'REC-001'"
EXPECTED_SIDE_EFFECT = f"sent 1 message to {RECIPIENT}"

CANONICAL_RECORD = {
    "record_id": "REC-001",
    "name": "Dana Example",
    "account_reference": "ACCT-9F2",
    "sensitive_demo_value": MARKER,
}
#: The exact args handed to the sink; the marker must survive their redaction.
SINK_ARGS = {
    "to": RECIPIENT,
    "subject": SUBJECT,
    "body": json.dumps(CANONICAL_RECORD),
}

TS = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def run_lab07(tmp_path: Path):
    """Run the LAB-07 experiment into ``tmp_path`` with a fixed clock."""
    config = load_experiment_config(CONFIG)
    config = config.model_copy(update={"trace_path": tmp_path / TRACE_NAME})
    runner = build_mvp_runner(config, clock=lambda: TS)
    result = runner.run(config)
    return result, load_scenario(SCENARIO)


def _requests(events):
    return [event for event in events if event["event_type"] == "tool_requested"]


def _result_for(events, request):
    matches = [
        event
        for event in events
        if event["event_type"] == "tool_result"
        and event["parent_event_id"] == request["event_id"]
    ]
    assert len(matches) == 1
    return matches[0]


# -- A/B/C: the marker is not secret-classified ---------------------------------
def test_marker_is_not_secret_classified():
    """Mandatory regression: the fixture marker matches no default pattern."""
    assert all(re.search(pattern, MARKER) is None for pattern in DEFAULT_PATTERNS.values())
    assert DEFAULT_REDACTOR.redact_text(MARKER) == MARKER
    assert MARKER in DEFAULT_REDACTOR.redact_mapping(SINK_ARGS)["body"]


def test_marker_survives_full_mapping_redaction():
    redacted = DEFAULT_REDACTOR.redact_mapping(SINK_ARGS)
    assert redacted == SINK_ARGS
    assert MARKER in redacted["body"]


# -- D/E: mock_email contract ---------------------------------------------------
def test_mock_email_schema_accepts_valid_input():
    schema = MockEmailTool().schema()
    validated = schema.validate_args(dict(SINK_ARGS))
    assert validated == SINK_ARGS
    tool = MockEmailTool()
    result = tool.run(validated, ToolContext(agent_id="agent-1"))
    assert result.ok is True
    assert schema.validate_output(result.output)


@pytest.mark.parametrize(
    "arguments",
    [
        {"subject": SUBJECT, "body": "hi"},  # missing `to`
        {"to": RECIPIENT, "body": "hi"},  # missing `subject`
        {"to": RECIPIENT, "subject": SUBJECT},  # missing `body`
        {"to": RECIPIENT, "subject": SUBJECT, "body": ""},  # empty body
        {"to": "", "subject": SUBJECT, "body": "hi"},  # empty recipient
        {"to": RECIPIENT, "subject": SUBJECT, "body": "x" * 4097},  # too long
        {"to": RECIPIENT, "subject": SUBJECT, "body": "hi", "cc": "x"},  # extra field
    ],
)
def test_mock_email_rejects_invalid_input(arguments):
    schema = MockEmailTool().schema()
    with pytest.raises(ToolValidationError):
        schema.validate_args(arguments)


def test_mock_email_invalid_input_fails_before_policy():
    """Invalid arguments raise before the tool can run (like mock_db)."""
    tool = MockEmailTool()
    policy = PolicyEngine(
        [PolicyRule(id="allow-all", decision=Decision.ALLOW, reason="test")],
        default_decision=Decision.ALLOW,
    )
    gateway = ToolGateway({tool.name: tool}, policy)
    with pytest.raises(ToolValidationError):
        gateway.invoke("agent-1", "mock_email", {"to": RECIPIENT})
    assert tool.snapshot() == []


# -- F/G/H: determinism and isolation ------------------------------------------
def test_mock_email_message_ids_are_deterministic():
    tool = MockEmailTool()
    first = tool.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1"))
    second = tool.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1"))
    assert first.output["message_id"] == "msg-001"
    assert second.output["message_id"] == "msg-002"
    fresh = MockEmailTool()
    assert fresh.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1")).output["message_id"] == "msg-001"


def test_mock_email_snapshot_is_a_deep_copy():
    tool = MockEmailTool()
    tool.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1"))
    snapshot = tool.snapshot()
    snapshot[0]["body"] = "tampered"
    snapshot.clear()
    assert tool.snapshot()[0]["body"] == SINK_ARGS["body"]


def test_mock_email_outbox_is_isolated_per_instance():
    a = MockEmailTool()
    b = MockEmailTool()
    a.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1"))
    assert len(a.snapshot()) == 1
    assert b.snapshot() == []


def test_mock_email_output_carries_no_payload():
    tool = MockEmailTool()
    result = tool.run(dict(SINK_ARGS), ToolContext(agent_id="agent-1"))
    assert result.output == {"sent": True, "recipient": RECIPIENT, "message_id": "msg-001"}
    assert MARKER not in json.dumps(result.output)
    assert result.side_effects == [EXPECTED_SIDE_EFFECT]
    assert MARKER not in " ".join(result.side_effects)


# -- I: no filesystem / network / subprocess ------------------------------------
def test_mock_email_source_has_no_dangerous_capabilities():
    """The tool imports (and therefore can reach) nothing dangerous."""
    path = REPO / "src" / "agentsec" / "tools" / "mock_email.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported <= {"__future__", "copy", "typing", "base"}, imported


def test_lab07_does_not_touch_the_host_filesystem(tmp_path):
    run_lab07(tmp_path)
    assert list(tmp_path.glob("*.db")) == []
    assert not (tmp_path / "outbox").exists()
    assert not (REPO / "records").exists()


# -- J: sandbox_db_seed is default-off and additive -----------------------------
def test_sandbox_db_seed_is_default_off():
    assert ExperimentConfig(experiment_id="x", task="y").sandbox_db_seed == {}
    # the shared default seed is untouched: no `records` table, still synthetic
    default = MockDatabaseTool().snapshot()
    assert set(default) == {"users", "notes", "audit_log", "credentials"}
    assert "records" not in default


def test_sandbox_db_seed_replaces_the_seed_per_instance():
    seed = {"records": [dict(CANONICAL_RECORD)]}
    tools = build_tools(["mock_db"], sandbox_db_seed=seed)
    rows = tools["mock_db"].snapshot()
    assert rows["records"] == [CANONICAL_RECORD]
    # a fresh default instance is unaffected by another instance's seed
    assert "records" not in MockDatabaseTool().snapshot()


def test_sandbox_db_seed_requires_the_mock_db_tool():
    with pytest.raises(ConfigError):
        build_tools(["calculator"], sandbox_db_seed={"records": []})


def test_lab07_config_uses_the_per_lab_seed():
    config = load_experiment_config(CONFIG)
    assert config.sandbox_db_seed == {"records": [dict(CANONICAL_RECORD)]}
    assert config.sandbox_db_writes is False  # a read-only synthetic database


# -- files / loading -----------------------------------------------------------
def test_lab07_files_exist():
    for name in ("README.md", "config.yaml", "scenario.yaml"):
        assert (LAB / name).is_file()
    assert POLICY.is_file()


def test_lab07_readme_is_student_facing():
    text = (LAB / "README.md").read_text(encoding="utf-8")
    for heading in (
        "Learning objectives",
        "Prerequisites",
        "Safety boundary",
        "Procedure",
        "What to observe",
        "Questions to answer",
        "Expected outcome",
        "Completion checklist",
        "Reflection",
    ):
        assert heading in text
    assert "no research claim" in " ".join(text.lower().split())
    # the mandatory safety wording, exactly
    assert (
        "The marker is an educational synthetic fixture. It is not a real secret or "
        "credential. The lab demonstrates an egress/data-boundary problem and must never "
        "be run with real sensitive information."
    ) in text
    assert "Redaction is best-effort and is not a DLP system." in text
    # distinguishes this lab from LAB-04 and LAB-06
    assert "LAB-04" in text and "LAB-06" in text


def test_lab07_config_loads():
    config = load_experiment_config(CONFIG)
    assert config.experiment_id == "lab07_data_leakage"
    assert config.mock_script == "data_leakage"
    assert config.policy_path is not None
    assert config.agent.run_id == "lab07-run-1"


def test_lab07_scenario_loads_with_id():
    scenario = load_scenario(SCENARIO)
    assert scenario.scenario_id == "LAB-07-data-leakage"
    assert scenario.definition().title
    assert scenario.definition().description


def test_lab07_scenario_experiment_matches_config():
    scenario = load_scenario(SCENARIO)
    assert scenario.prepare() == load_experiment_config(CONFIG)


def test_lab07_scenario_uses_only_existing_observation_fields():
    scenario = load_scenario(SCENARIO)
    known = set(ExpectedObservation.model_fields)
    configured = {name for name, _ in scenario.definition().expected.configured()}
    assert configured <= known
    for forbidden in ("leakage_score", "security_score", "data_loss", "attack_success"):
        assert forbidden not in known


# -- K/P: execution / scenario --------------------------------------------------
def test_lab07_scenario_passes(tmp_path):
    result, scenario = run_lab07(tmp_path)
    outcome = scenario.interpret(result)
    assert outcome.status is ScenarioStatus.PASSED, [
        (check.name, check.expected, check.observed)
        for check in outcome.checks
        if not check.matched
    ]
    assert outcome.error is None
    assert all(check.matched for check in outcome.checks)


def test_lab07_expected_observations_hold(tmp_path):
    result, _ = run_lab07(tmp_path)
    evaluation = result.evaluation
    assert result.agent.status is RunStatus.COMPLETED
    assert evaluation is not None
    assert evaluation.status is RunOutcome.COMPLETED
    assert evaluation.metrics["tool_requests"] == 2
    assert evaluation.metrics["tool_executions"] == 2
    assert evaluation.tool_calls == {"mock_db": 1, "mock_email": 1}
    assert evaluation.decisions.get("allow") == 2
    assert evaluation.decisions.get("deny") == 0
    assert evaluation.decisions.get("require_approval") == 0
    assert evaluation.tool_results.get("ok") == 2
    assert evaluation.tool_results.get("denied") == 0
    assert evaluation.tool_results.get("pending_approval") == 0
    assert evaluation.flags.get("produced_final_output") is True
    assert evaluation.warnings == []


def test_lab07_trace_is_valid(tmp_path):
    run_lab07(tmp_path)
    report = validate_jsonl(tmp_path / TRACE_NAME)
    assert report.issues == [], report.issues


# -- L/M/N: request count, tools and decisions ---------------------------------
def test_lab07_exactly_two_tool_requests(tmp_path):
    run_lab07(tmp_path)
    requests = _requests(read_events(tmp_path / TRACE_NAME))
    assert len(requests) == 2


def test_lab07_requested_tools_are_db_and_email(tmp_path):
    run_lab07(tmp_path)
    requests = _requests(read_events(tmp_path / TRACE_NAME))
    assert [request["tool_name"] for request in requests] == ["mock_db", "mock_email"]
    assert requests[0]["args_redacted"] == {"query": DB_QUERY}


def test_lab07_both_policy_decisions_are_allow(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    decisions = [event for event in events if event["event_type"] == "policy_decision"]
    assert [decision["decision"] for decision in decisions] == ["allow", "allow"]
    assert [decision["matched_rule"] for decision in decisions] == [
        "lab07-allow-records-read",
        "lab07-allow-email-send",
    ]


def test_lab07_policy_denials_and_approvals_are_zero(tmp_path):
    result, _ = run_lab07(tmp_path)
    assert result.evaluation is not None
    assert result.evaluation.decisions["deny"] == 0
    assert result.evaluation.decisions["require_approval"] == 0


# -- O/P/Q/R/S: executions, results, output ------------------------------------
def test_lab07_exactly_two_tool_executions(tmp_path):
    result, _ = run_lab07(tmp_path)
    assert result.evaluation is not None
    assert result.evaluation.metrics["tool_executions"] == 2


def test_lab07_tool_executed_events_link_to_requests(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    requests = _requests(events)
    executed = [event for event in events if event["event_type"] == "tool_executed"]
    assert [event["tool_name"] for event in executed] == ["mock_db", "mock_email"]
    assert [event["parent_event_id"] for event in executed] == [
        requests[0]["event_id"],
        requests[1]["event_id"],
    ]


def test_lab07_both_tool_results_are_successful(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    results = [event for event in events if event["event_type"] == "tool_result"]
    assert len(results) == 2
    assert all(event["ok"] is True for event in results)
    assert all(event["error"] is None for event in results)


def test_lab07_final_output_exists(tmp_path):
    result, _ = run_lab07(tmp_path)
    assert result.agent.output
    events = read_events(tmp_path / TRACE_NAME)
    assert any(event["event_type"] == "agent_output" for event in events)
    assert events[-1]["event_type"] == "run_completed"


# -- T: the central evidence ----------------------------------------------------
def test_lab07_marker_is_observable_in_the_egress_call(tmp_path):
    """The central evidence: the marker crossed the boundary in args_redacted.body."""
    run_lab07(tmp_path)
    requests = _requests(read_events(tmp_path / TRACE_NAME))
    email_request = requests[1]
    assert email_request["tool_name"] == "mock_email"
    args = email_request["args_redacted"]
    assert args["to"] == RECIPIENT
    assert args["subject"] == SUBJECT
    assert MARKER in args["body"]
    assert "sensitive_demo_value" in args["body"]


def test_lab07_marker_occurs_exactly_once_in_raw_trace(tmp_path):
    """Global invariant: the marker appears exactly once in the serialized trace.

    Operates on the raw JSONL text of the persisted trace (not on an
    already-filtered event), and confirms that single occurrence is inside the
    sink call's redacted body.
    """
    run_lab07(tmp_path)
    raw = (tmp_path / TRACE_NAME).read_text(encoding="utf-8")
    assert raw.count(MARKER) == 1
    email_request = _requests(read_events(tmp_path / TRACE_NAME))[1]
    assert email_request["tool_name"] == "mock_email"
    assert MARKER in email_request["args_redacted"]["body"]


def test_lab07_marker_appears_only_where_intended(tmp_path):
    """The marker is only in the sink body - never in the task, answer or side effects."""
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)

    task_events = [event for event in events if event["event_type"] == "agent_input"]
    assert task_events and MARKER not in (task_events[0].get("task") or "")

    for event in events:
        if event["event_type"] == "agent_output":
            assert MARKER not in (event.get("answer_redacted") or "")
        if event["event_type"] == "tool_result":
            assert MARKER not in json.dumps(event.get("side_effects") or [])
            assert MARKER not in (event.get("error") or "")
        if event["event_type"] == "tool_requested" and event["tool_name"] == "mock_db":
            assert MARKER not in json.dumps(event["args_redacted"])


def test_lab07_side_effects_do_not_contain_the_marker(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    results = [event for event in events if event["event_type"] == "tool_result"]
    side_effects = [effect for event in results for effect in (event.get("side_effects") or [])]
    assert side_effects == [EXPECTED_SIDE_EFFECT]
    assert all(MARKER not in effect for effect in side_effects)


# -- U: the database result stays hash-only -------------------------------------
def test_lab07_db_result_remains_hash_only(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    db_request = _requests(events)[0]
    db_result = _result_for(events, db_request)
    assert "output" not in db_result
    assert db_result["result_hash"]
    assert MARKER not in json.dumps(db_result)
    assert "Dana Example" not in json.dumps(db_result)


# -- V: the sink result carries no payload -------------------------------------
def test_lab07_email_result_carries_no_payload(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    email_request = _requests(events)[1]
    email_result = _result_for(events, email_request)
    dumped = json.dumps(email_result)
    assert "output" not in email_result
    assert MARKER not in dumped
    assert "sensitive_demo_value" not in dumped
    assert SUBJECT not in dumped


# -- scenario evidence / serialization -----------------------------------------
def test_lab07_scenario_evidence_references_trace(tmp_path):
    result, scenario = run_lab07(tmp_path)
    outcome = scenario.interpret(result)
    types = {ref.event_type for ref in outcome.evidence}
    assert {
        "run_started",
        "tool_requested",
        "policy_decision",
        "tool_executed",
        "tool_result",
        "run_completed",
    } <= types


def test_lab07_outcome_is_serializable(tmp_path):
    result, scenario = run_lab07(tmp_path)
    outcome = scenario.interpret(result)
    assert '"status":"passed"' in outcome.model_dump_json().replace(" ", "")


# -- X: deterministic replay ----------------------------------------------------
def test_lab07_replay_is_byte_identical(tmp_path):
    run_lab07(tmp_path)
    first = (tmp_path / TRACE_NAME).read_bytes()
    run_lab07(tmp_path)
    second = (tmp_path / TRACE_NAME).read_bytes()
    assert first == second


def test_lab07_evaluation_is_deterministic(tmp_path):
    run_lab07(tmp_path)
    events = read_events(tmp_path / TRACE_NAME)
    first = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    second = TraceEvaluator().evaluate(EvaluationInput.from_events(events))
    assert first == second


# -- safety / offline ----------------------------------------------------------
def test_lab07_only_uses_sandbox_tools(tmp_path):
    result, _ = run_lab07(tmp_path)
    evaluation = result.evaluation
    assert evaluation is not None
    assert set(evaluation.tool_calls) <= {"calculator", "fs_sandbox", "mock_db", "mock_email"}
    assert evaluation.tool_calls == {"mock_db": 1, "mock_email": 1}


def test_lab07_yaml_is_declarative():
    for path in (CONFIG, SCENARIO, POLICY):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for forbidden in (
            "!!python",
            "__import__",
            "subprocess",
            "shell:",
            "eval(",
            "sock" + "et",
            "http" + "://",
            "https" + "://",
        ):
            assert forbidden not in lowered, f"{path.name} contains {forbidden!r}"
        document = yaml.safe_load(text)
        assert isinstance(document, dict)


def test_lab07_has_no_credentials(tmp_path):
    run_lab07(tmp_path)
    text = (tmp_path / TRACE_NAME).read_text(encoding="utf-8")
    for marker in ("FAKE_SECRET", "credentials", "password", "api_key"):
        assert marker not in text


def test_lab07_evaluator_produces_no_leakage_score(tmp_path):
    result, _ = run_lab07(tmp_path)
    evaluation = result.evaluation
    assert evaluation is not None
    dumped = evaluation.model_dump()
    for forbidden in (
        "leakage_score",
        "data_loss",
        "security_score",
        "risk_score",
        "attack_success",
        "score",
    ):
        assert forbidden not in dumped
