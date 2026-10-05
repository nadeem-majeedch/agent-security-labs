"""Tests for the read-only controlled experiment runner (Phase 11D).

The runner executes the same base scenario twice — control and treatment — using
an **injected executor**, so no real run happens here. Traces are written only to
a temporary directory that the runner owns and removes; the repository is never
written to. These tests pin the semantics: the held-constant invariant, the
single policy intervention, deterministic score-free results, and the discrete
outcome states.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentsec.errors import ConfigError
from agentsec.experiment import load_experiment_config
from agentsec.experiment_lab import (
    BOUNDED_NOTE,
    ExperimentStatus,
    assert_held_constant,
    load_experiment_spec,
    run_controlled_experiment,
)
from agentsec.scenarios import ExpectedObservation

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "configs" / "experiments" / "lab04-policy-intervention.yaml"
LAB04_BASE = REPO / "labs" / "LAB-04-tool-misuse" / "config.yaml"


# -- synthetic traces ----------------------------------------------------------
def _event(seq: int, event_type: str, **extra) -> dict:
    event = {
        "schema_version": "1.0",
        "run_id": "lab04-run-1",
        "event_id": f"ev-{seq:06d}",
        "parent_event_id": None if seq == 0 else f"ev-{seq - 1:06d}",
        "seq": seq,
        "timestamp": f"2026-01-01T00:00:{seq:02d}+00:00",
        "agent_id": "agent-1",
        "model": "fixture",
        "scenario": "LAB-04-tool-misuse",
        "event_type": event_type,
    }
    event.update(extra)
    return event


def _write_trace(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )


def _control_events() -> list[dict]:
    """A denied request: policy refuses, the tool never executes."""
    return [
        _event(0, "run_started"),
        _event(1, "agent_input", task="please process the report and save a short note"),
        _event(2, "model_request"),
        _event(3, "model_response", finish_reason="tool_calls"),
        _event(4, "tool_requested", tool_name="fs_sandbox"),
        _event(5, "policy_decision", decision="deny", reason="outside workspace"),
        _event(6, "tool_result", ok=False),
        _event(7, "agent_output", answer_redacted="I could not complete that."),
        _event(8, "run_completed"),
    ]


def _treatment_events() -> list[dict]:
    """An allowed request: policy permits, the tool executes."""
    return [
        _event(0, "run_started"),
        _event(1, "agent_input", task="please process the report and save a short note"),
        _event(2, "model_request"),
        _event(3, "model_response", finish_reason="tool_calls"),
        _event(4, "tool_requested", tool_name="fs_sandbox"),
        _event(5, "policy_decision", decision="allow", reason="allow all"),
        _event(6, "tool_executed"),
        _event(7, "tool_result", ok=True),
        _event(8, "agent_output", answer_redacted="Saved the note."),
        _event(9, "run_completed"),
    ]


def _base_spec():
    return load_experiment_spec(EXAMPLE)


def _executor(records: list):
    """Write the control/treatment trace according to the run's policy."""

    def execute(config) -> None:
        records.append(config)
        if Path(config.policy_path).name == "allow_all_v1.yaml":
            _write_trace(Path(config.trace_path), _treatment_events())
        else:
            _write_trace(Path(config.trace_path), _control_events())

    return execute


# -- derivation and held-constant ---------------------------------------------
def test_control_and_treatment_are_derived_from_the_base():
    records: list = []
    run_controlled_experiment(_base_spec(), root=REPO, execute=_executor(records))
    assert len(records) == 2
    by_policy = {Path(c.policy_path).name: c for c in records}
    assert set(by_policy) == {"least_privilege_v1.yaml", "allow_all_v1.yaml"}
    assert by_policy["least_privilege_v1.yaml"] is not by_policy["allow_all_v1.yaml"]


def test_policy_is_the_only_intended_difference():
    records: list = []
    run_controlled_experiment(_base_spec(), root=REPO, execute=_executor(records))
    control, treatment = records
    assert control.policy_path != treatment.policy_path
    assert control.model_dump(exclude={"policy_path", "trace_path"}) == treatment.model_dump(
        exclude={"policy_path", "trace_path"}
    )


def test_assert_held_constant_rejects_a_second_difference():
    base = load_experiment_config(LAB04_BASE)
    control = base.model_copy(update={"policy_path": Path("policies/examples/deny_by_default.yaml")})
    treatment = base.model_copy(
        update={
            "policy_path": Path("policies/examples/allow_all_v1.yaml"),
            "mock_script": "benign",
        }
    )
    with pytest.raises(ConfigError) as excinfo:
        assert_held_constant(control, treatment)
    assert "mock_script" in str(excinfo.value)


def test_assert_held_constant_accepts_policy_only_difference():
    base = load_experiment_config(LAB04_BASE)
    control = base.model_copy(
        update={
            "policy_path": Path("policies/examples/deny_by_default.yaml"),
            "trace_path": Path("a.jsonl"),
        }
    )
    treatment = base.model_copy(
        update={
            "policy_path": Path("policies/examples/allow_all_v1.yaml"),
            "trace_path": Path("b.jsonl"),
        }
    )
    assert_held_constant(control, treatment)  # does not raise


def test_traces_are_temporary_and_removed():
    records: list = []
    run_controlled_experiment(_base_spec(), root=REPO, execute=_executor(records))
    for config in records:
        trace_path = Path(config.trace_path)
        assert REPO not in trace_path.resolve().parents
        # The temporary directory is removed when the runner returns.
        assert not trace_path.exists()


def test_executor_is_called_once_per_run():
    records: list = []
    run_controlled_experiment(_base_spec(), root=REPO, execute=_executor(records))
    assert len(records) == 2


# -- result semantics ----------------------------------------------------------
def test_changes_observed_status():
    result = run_controlled_experiment(
        _base_spec(), root=REPO, execute=_executor([])
    )
    assert result.status is ExperimentStatus.CHANGES_OBSERVED
    changed = {row.name: row for row in result.expected_changes}
    assert changed["tool_executions"].observed is True
    assert changed["tool_executions"].control_observed == 0
    assert changed["tool_executions"].treatment_observed == 1


def test_changes_not_observed_status():
    spec = _base_spec().model_copy(
        update={"expected_changes": ExpectedObservation(tool_executions=5)}
    )
    result = run_controlled_experiment(spec, root=REPO, execute=_executor([]))
    assert result.status is ExperimentStatus.CHANGES_NOT_OBSERVED
    assert result.expected_changes[0].observed is False


def test_invariant_violated_status():
    spec = _base_spec().model_copy(
        update={"expected_invariants": ExpectedObservation(tool_executions=0)}
    )
    result = run_controlled_experiment(spec, root=REPO, execute=_executor([]))
    assert result.status is ExperimentStatus.INVARIANT_VIOLATED
    assert result.expected_invariants[0].held is False


def test_invariants_hold_when_preserved():
    result = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    assert all(row.held for row in result.expected_invariants)


def test_alternative_explanations_and_claim_are_carried():
    result = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    assert result.alternative_explanations  # non-empty
    assert result.claim and "fixture" in result.claim
    assert BOUNDED_NOTE in result.notes


def test_comparison_is_reused_and_descriptive():
    result = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    assert result.comparison is not None
    assert result.comparison["schema_version"] == "1"
    assert "evaluator" in result.comparison
    assert "sequence" in result.comparison


def test_result_is_deterministic():
    first = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    second = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    assert first == second


def test_result_contains_no_absolute_or_temp_paths():
    result = run_controlled_experiment(_base_spec(), root=REPO, execute=_executor([]))
    dumped = json.dumps(result.model_dump(mode="json"))
    assert "agentsec-experiment-" not in dumped
    assert str(REPO) not in dumped
    for summary in (result.control, result.treatment):
        assert summary is not None
        assert not Path(summary.policy).is_absolute()


# -- failure paths -------------------------------------------------------------
def test_control_execution_failure_is_reported_distinctly():
    def execute(config) -> None:
        raise RuntimeError("boom")

    result = run_controlled_experiment(_base_spec(), root=REPO, execute=execute)
    assert result.status is ExperimentStatus.EXECUTION_FAILED
    assert result.error is not None and "control" in result.error


def test_treatment_execution_failure_is_reported_distinctly():
    def execute(config) -> None:
        if Path(config.policy_path).name == "allow_all_v1.yaml":
            raise RuntimeError("boom")
        _write_trace(Path(config.trace_path), _control_events())

    result = run_controlled_experiment(_base_spec(), root=REPO, execute=execute)
    assert result.status is ExperimentStatus.EXECUTION_FAILED
    assert result.error is not None and "treatment" in result.error


def test_missing_trace_is_reported_distinctly():
    def execute(config) -> None:  # writes nothing
        return None

    result = run_controlled_experiment(_base_spec(), root=REPO, execute=execute)
    assert result.status is ExperimentStatus.EXECUTION_FAILED
    assert "no trace" in (result.error or "")


def test_non_completed_run_is_execution_failed():
    def execute(config) -> None:
        events = _control_events()
        events[-1] = _event(len(events) - 1, "run_failed", error_type="ModelError")
        _write_trace(Path(config.trace_path), events)

    result = run_controlled_experiment(_base_spec(), root=REPO, execute=execute)
    assert result.status is ExperimentStatus.EXECUTION_FAILED


def test_invalid_spec_files_raise_before_execution():
    spec = _base_spec().model_copy(update={"base_config": Path("labs/nope/config.yaml")})
    with pytest.raises(ConfigError):
        run_controlled_experiment(spec, root=REPO, execute=_executor([]))
