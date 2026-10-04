"""Tests for the read-only ``predict`` command.

A prediction is compared against an existing trace, never by re-running
anything. Synthetic traces are written to ``tmp_path`` as plain JSONL; the
integration tests run the real LAB-04 configuration into ``tmp_path`` with a
fixed clock. The prediction logic and its renderer are exercised directly, and
the CLI wrapper through :func:`agentsec.cli.main`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from agentsec.cli import main
from agentsec.errors import ConfigError, EvaluationError
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner
from agentsec.prediction import check_prediction, load_prediction, render_prediction

REPO = Path(__file__).resolve().parents[2]
LAB03 = REPO / "labs" / "LAB-03-indirect-prompt-injection" / "config.yaml"
LAB04 = REPO / "labs" / "LAB-04-tool-misuse" / "config.yaml"
LAB05 = REPO / "labs" / "LAB-05-require-approval" / "config.yaml"
LAB07 = REPO / "labs" / "LAB-07-data-leakage" / "config.yaml"
PREDICTIONS = REPO / "configs" / "predictions"
LAB04_PREDICTION = PREDICTIONS / "lab04.yaml"
LAB04_MISMATCH = PREDICTIONS / "lab04_mismatch.yaml"
#: Phase 8A expanded examples, each tied to a lab with a distinct observation.
LAB03_PREDICTION = PREDICTIONS / "lab03_expect_allowed_then_denied.yaml"
LAB05_APPROVAL_PREDICTION = PREDICTIONS / "lab05_expect_approval.yaml"
LAB05_DENIED_MISMATCH = PREDICTIONS / "lab05_expect_denied.yaml"
LAB07_PREDICTION = PREDICTIONS / "lab07_expect_two_tools.yaml"
TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


# -- helpers -------------------------------------------------------------------
def _event(seq: int, event_type: str, *, parent: str | None = None, run_id="run-x", **extra):
    event = {
        "schema_version": "1.0",
        "run_id": run_id,
        "event_id": f"ev-{seq:06d}",
        "parent_event_id": parent,
        "seq": seq,
        "timestamp": f"2026-01-01T00:00:{seq:02d}+00:00",
        "agent_id": "agent-1",
        "model": "fixture",
        "scenario": "LAB-XX",
        "event_type": event_type,
    }
    event.update(extra)
    return event


def _write_trace(path: Path, events: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )
    return path


def _allowed_calculator_trace(path: Path, *, output: str = "the answer is 5") -> Path:
    """A coherent trace: an authorized calculator call that executed."""
    return _write_trace(
        path,
        [
            _event(0, "run_started"),
            _event(1, "agent_input"),
            _event(2, "model_request"),
            _event(3, "model_response", parent="ev-000002"),
            _event(4, "tool_requested", tool_name="calculator"),
            _event(5, "policy_decision", parent="ev-000004", decision="allow"),
            _event(6, "tool_executed", parent="ev-000004"),
            _event(7, "tool_result", parent="ev-000004", ok=True),
            _event(8, "agent_output", answer_redacted=output),
            _event(9, "run_completed"),
        ],
    )


def _write_prediction(path: Path, **fields) -> Path:
    path.write_text(yaml.safe_dump(fields, sort_keys=True), encoding="utf-8")
    return path


def _run_lab(config: Path, out: Path) -> Path:
    loaded = load_experiment_config(config)
    loaded = loaded.model_copy(update={"trace_path": out})
    build_mvp_runner(loaded, clock=lambda: TS).run(loaded)
    return out


# -- prediction parsing --------------------------------------------------------
def test_load_prediction_parses_observable_fields(tmp_path):
    path = _write_prediction(
        tmp_path / "p.yaml", tool_executions=0, policy_denials=1, requested_tools=["fs_sandbox"]
    )
    prediction = load_prediction(path)
    assert dict(prediction.configured()) == {
        "tool_executions": 0,
        "policy_denials": 1,
        "requested_tools": ("fs_sandbox",),
    }


def test_load_prediction_rejects_unknown_field(tmp_path):
    path = _write_prediction(tmp_path / "p.yaml", risk_score=0.5)
    with pytest.raises(ConfigError) as excinfo:
        load_prediction(path)
    assert "risk_score" in str(excinfo.value)


def test_load_prediction_rejects_missing_file(tmp_path):
    with pytest.raises(ConfigError):
        load_prediction(tmp_path / "missing.yaml")


def test_load_prediction_rejects_non_mapping(tmp_path):
    path = tmp_path / "p.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_prediction(path)


# -- checking ------------------------------------------------------------------
def test_check_prediction_reports_all_matched(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(
        tmp_path / "p.yaml",
        evaluation_status="completed",
        tool_executions=1,
        requested_tools=["calculator"],
    )
    result = check_prediction(trace, prediction)
    assert result["mismatched"] == []
    assert set(result["matched"]) == {"evaluation_status", "tool_executions", "requested_tools"}
    assert all(row["matched"] for row in result["checks"])


def test_check_prediction_reports_mismatches(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(
        tmp_path / "p.yaml", tool_executions=0, policy_denials=1
    )
    result = check_prediction(trace, prediction)
    assert result["matched"] == []
    assert set(result["mismatched"]) == {"tool_executions", "policy_denials"}
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["tool_executions"]["predicted"] == 0
    assert by_name["tool_executions"]["observed"] == 1


def test_requested_tools_match_regardless_of_order(tmp_path):
    trace = _write_trace(
        tmp_path / "t.jsonl",
        [
            _event(0, "run_started"),
            _event(1, "tool_requested", tool_name="mock_db"),
            _event(2, "policy_decision", parent="ev-000001", decision="deny"),
            _event(3, "tool_result", parent="ev-000001", ok=False),
            _event(4, "tool_requested", tool_name="calculator"),
            _event(5, "policy_decision", parent="ev-000004", decision="deny"),
            _event(6, "tool_result", parent="ev-000004", ok=False),
            _event(7, "run_completed"),
        ],
    )
    prediction = _write_prediction(
        tmp_path / "p.yaml", requested_tools=["calculator", "mock_db"]
    )
    result = check_prediction(trace, prediction)
    assert result["mismatched"] == []
    assert result["checks"][0]["name"] == "requested_tools"


def test_output_contains_uses_substring_semantics(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl", output="the answer is 5")
    hit = _write_prediction(tmp_path / "hit.yaml", output_contains="answer is 5")
    miss = _write_prediction(tmp_path / "miss.yaml", output_contains="goodbye")
    assert check_prediction(trace, hit)["mismatched"] == []
    assert check_prediction(trace, miss)["mismatched"] == ["output_contains"]


def test_check_prediction_is_deterministic(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=1)
    first = render_prediction(check_prediction(trace, prediction))
    second = render_prediction(check_prediction(trace, prediction))
    assert first == second


def test_check_prediction_does_not_modify_the_trace(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=1)
    before = trace.read_bytes()
    check_prediction(trace, prediction)
    assert trace.read_bytes() == before


def test_prediction_with_no_expectations_reports_no_checks(tmp_path):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml")
    result = check_prediction(trace, prediction)
    assert result["checks"] == []
    assert "no expectations" in render_prediction(result)


# -- CLI -----------------------------------------------------------------------
def test_predict_cli_prints_human_output(tmp_path, capsys):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=0)
    assert main(["predict", str(trace), str(prediction)]) == 0
    out = capsys.readouterr().out
    assert "Prediction results" in out
    assert "predicted:" in out and "observed:" in out
    assert "MISMATCH" in out


def test_predict_cli_json_output(tmp_path, capsys):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=1)
    assert main(["predict", str(trace), str(prediction), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "1"
    assert payload["mismatched"] == []
    assert payload["checks"][0]["matched"] is True


def test_predict_cli_malformed_trace_exits_one(tmp_path, capsys):
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=0)
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n", encoding="utf-8")
    assert main(["predict", str(bad), str(prediction)]) == 1
    assert "error:" in capsys.readouterr().err


def test_predict_cli_malformed_prediction_exits_one(tmp_path, capsys):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    bad = tmp_path / "bad.yaml"
    bad.write_text("not_a_field: 1\n", encoding="utf-8")
    assert main(["predict", str(trace), str(bad)]) == 1
    assert "error:" in capsys.readouterr().err


def test_predict_cli_missing_trace_exits_one(tmp_path, capsys):
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=0)
    assert main(["predict", str(tmp_path / "missing.jsonl"), str(prediction)]) == 1
    assert "error:" in capsys.readouterr().err


def test_predict_cli_mismatch_still_exits_zero(tmp_path, capsys):
    trace = _allowed_calculator_trace(tmp_path / "t.jsonl")
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=0)
    assert main(["predict", str(trace), str(prediction)]) == 0
    assert "MISMATCH" in capsys.readouterr().out


# -- real lab integration ------------------------------------------------------
def test_check_prediction_real_lab04_matches(tmp_path):
    trace = _run_lab(LAB04, tmp_path / "lab04.jsonl")
    result = check_prediction(trace, LAB04_PREDICTION)
    assert result["mismatched"] == []
    assert result["trace"]["scenario"] == "LAB-04-tool-misuse"


def test_check_prediction_real_lab04_deliberate_mismatch(tmp_path):
    trace = _run_lab(LAB04, tmp_path / "lab04.jsonl")
    result = check_prediction(trace, LAB04_MISMATCH)
    assert result["mismatched"] == ["tool_executions"]
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["tool_executions"]["predicted"] == 1
    assert by_name["tool_executions"]["observed"] == 0


# -- expanded real-lab examples (Phase 8A) -------------------------------------
def test_check_prediction_real_lab05_approval_matches(tmp_path):
    """LAB-05's read is *held for approval*: a pending outcome, not a denial."""
    trace = _run_lab(LAB05, tmp_path / "lab05.jsonl")
    result = check_prediction(trace, LAB05_APPROVAL_PREDICTION)
    assert result["mismatched"] == []
    assert result["trace"]["scenario"] == "LAB-05-require-approval"
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["tool_results_pending_approval"]["observed"] == 1
    assert by_name["tool_executions"]["observed"] == 0


def test_check_prediction_real_lab05_deliberate_mismatch(tmp_path):
    """Predicting a *denial* for LAB-05 mismatches: the policy held it instead."""
    trace = _run_lab(LAB05, tmp_path / "lab05.jsonl")
    result = check_prediction(trace, LAB05_DENIED_MISMATCH)
    assert set(result["mismatched"]) == {"policy_denials", "tool_results_denied"}
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["policy_denials"]["predicted"] == 1
    assert by_name["policy_denials"]["observed"] == 0
    assert by_name["tool_executions"]["matched"] is True


def test_check_prediction_real_lab03_matches(tmp_path):
    """LAB-03 allows one request and denies another within the same run."""
    trace = _run_lab(LAB03, tmp_path / "lab03.jsonl")
    result = check_prediction(trace, LAB03_PREDICTION)
    assert result["mismatched"] == []
    assert result["trace"]["scenario"] == "LAB-03-indirect-prompt-injection"
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["tool_executions"]["observed"] == 1
    assert by_name["tool_results_denied"]["observed"] == 1


def test_check_prediction_real_lab07_matches(tmp_path):
    """LAB-07 allows and executes two different tools in one run."""
    trace = _run_lab(LAB07, tmp_path / "lab07.jsonl")
    result = check_prediction(trace, LAB07_PREDICTION)
    assert result["mismatched"] == []
    assert result["trace"]["scenario"] == "LAB-07-data-leakage"
    by_name = {row["name"]: row for row in result["checks"]}
    assert by_name["requested_tools"]["observed"] == ["mock_db", "mock_email"]
    assert by_name["tool_executions"]["observed"] == 2


def test_expanded_prediction_json_output_is_deterministic(tmp_path, capsys):
    trace = _run_lab(LAB05, tmp_path / "lab05.jsonl")
    args = ["predict", str(trace), str(LAB05_APPROVAL_PREDICTION), "--json"]
    assert main(args) == 0
    first = capsys.readouterr().out
    assert main(args) == 0
    second = capsys.readouterr().out
    assert first == second
    assert json.loads(first)["mismatched"] == []


def test_expanded_predictions_do_not_write_to_tracked_paths(tmp_path):
    """Checking a prediction leaves the trace and the prediction untouched."""
    prediction_files = [
        LAB03_PREDICTION,
        LAB05_APPROVAL_PREDICTION,
        LAB05_DENIED_MISMATCH,
        LAB07_PREDICTION,
    ]
    before = {path: path.read_bytes() for path in prediction_files}
    for config, prediction, name in (
        (LAB03, LAB03_PREDICTION, "lab03.jsonl"),
        (LAB05, LAB05_APPROVAL_PREDICTION, "lab05.jsonl"),
        (LAB07, LAB07_PREDICTION, "lab07.jsonl"),
    ):
        trace = _run_lab(config, tmp_path / name)
        snapshot = trace.read_bytes()
        check_prediction(trace, prediction)
        assert trace.read_bytes() == snapshot, f"predict modified {name}"
    for path in prediction_files:
        assert path.read_bytes() == before[path], f"predict modified {path.name}"


# -- errors from the module surface --------------------------------------------
def test_check_prediction_missing_trace_raises_evaluation_error(tmp_path):
    prediction = _write_prediction(tmp_path / "p.yaml", tool_executions=0)
    with pytest.raises(EvaluationError):
        check_prediction(tmp_path / "missing.jsonl", prediction)
