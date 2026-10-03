"""Tests for the deterministic, read-only ``compare`` command.

The comparison logic and its renderer are exercised directly, and the CLI wrapper
through :func:`agentsec.cli.main`. Synthetic traces are written to ``tmp_path`` as
plain JSONL; the integration test runs two real lab configurations into
``tmp_path`` with a fixed clock. Nothing is executed by the comparison itself and
the repository is never touched.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agentsec.cli import main
from agentsec.compare import ALIGNMENT_NOTE, compare_traces, render_comparison
from agentsec.experiment import load_experiment_config
from agentsec.mvp import build_mvp_runner
from agentsec.policy.loader import load_policy
from agentsec.policy.schema import Decision

REPO = Path(__file__).resolve().parents[2]
LAB01 = REPO / "labs" / "LAB-01-benign-agent" / "config.yaml"
LAB04 = REPO / "labs" / "LAB-04-tool-misuse" / "config.yaml"
LAB05 = REPO / "labs" / "LAB-05-require-approval" / "config.yaml"
LAB05_DENY = REPO / "configs" / "examples" / "lab05_require_approval_deny_by_default.yaml"
ALLOW_ALL_CONFIG = REPO / "configs" / "examples" / "lab04_tool_misuse_allow_all.yaml"
ALLOW_ALL_POLICY = REPO / "policies" / "examples" / "allow_all_v1.yaml"
LEAST_PRIVILEGE_POLICY = REPO / "policies" / "examples" / "least_privilege_v1.yaml"
TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


# -- helpers -------------------------------------------------------------------
def _event(seq: int, event_type: str, *, run_id: str = "run-x", **extra) -> dict:
    event = {
        "schema_version": "1.0",
        "run_id": run_id,
        "event_id": f"ev-{seq:06d}",
        "parent_event_id": None if seq == 0 else f"ev-{seq - 1:06d}",
        "seq": seq,
        "timestamp": f"2026-01-01T00:00:{seq:02d}+00:00",
        "agent_id": "agent-1",
        "model": "fixture",
        "scenario": "LAB-XX",
        "event_type": event_type,
    }
    event.update(extra)
    return event


def _write(path: Path, events: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
        encoding="utf-8",
    )
    return path


def _run_lab(config: Path, out: Path) -> Path:
    """Run one real lab config into ``out`` with a fixed clock."""
    loaded = load_experiment_config(config)
    loaded = loaded.model_copy(update={"trace_path": out})
    build_mvp_runner(loaded, clock=lambda: TS).run(loaded)
    return out


# -- identical traces ----------------------------------------------------------
def test_identical_traces_report_no_difference(tmp_path):
    path = _write(
        tmp_path / "a.jsonl",
        [
            _event(0, "run_started"),
            _event(1, "agent_input"),
            _event(2, "run_completed"),
        ],
    )
    result = compare_traces(path, path)
    assert result["event_count_delta"] == 0
    assert result["sequence"]["identical"] is True
    assert result["sequence"]["changed"] == []
    assert result["evaluator"]["differences"] == []
    text = render_comparison(result)
    assert "event sequences are identical" in text
    assert "Evaluator differences\n  none" in text


# -- event counts --------------------------------------------------------------
def test_event_count_difference_is_reported(tmp_path):
    a = _write(
        tmp_path / "a.jsonl",
        [_event(0, "run_started"), _event(1, "agent_input"), _event(2, "run_completed")],
    )
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    result = compare_traces(a, b)
    assert result["trace_a"]["event_count"] == 3
    assert result["trace_b"]["event_count"] == 2
    assert result["event_count_delta"] == 1


# -- event-type distribution ---------------------------------------------------
def test_event_type_distribution_reports_both_traces(tmp_path):
    a = _write(
        tmp_path / "a.jsonl",
        [_event(0, "run_started"), _event(1, "agent_input"), _event(2, "run_completed")],
    )
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    distribution = {
        entry["event_type"]: entry for entry in compare_traces(a, b)["event_type_distribution"]
    }
    assert distribution["agent_input"] == {"event_type": "agent_input", "a": 1, "b": 0, "delta": 1}
    assert distribution["run_started"]["delta"] == 0


def test_distribution_uses_schema_order_then_unknown_sorted(tmp_path):
    a = _write(
        tmp_path / "a.jsonl",
        [_event(0, "run_started"), _event(1, "zzz_unknown"), _event(2, "aaa_unknown")],
    )
    order = [entry["event_type"] for entry in compare_traces(a, a)["event_type_distribution"]]
    # known schema types first, unknown types alphabetically after them.
    assert order == ["run_started", "aaa_unknown", "zzz_unknown"]


# -- ordered sequence ----------------------------------------------------------
def test_sequence_change_is_reported_positionally(tmp_path):
    a = _write(
        tmp_path / "a.jsonl",
        [_event(0, "run_started"), _event(1, "tool_result"), _event(2, "run_completed")],
    )
    b = _write(
        tmp_path / "b.jsonl",
        [_event(0, "run_started"), _event(1, "agent_input"), _event(2, "run_completed")],
    )
    sequence = compare_traces(a, b)["sequence"]
    assert sequence["identical"] is False
    assert sequence["changed"] == [{"index": 1, "a": "tool_result", "b": "agent_input"}]
    assert sequence["only_in_a"] == []
    assert sequence["only_in_b"] == []


def test_sequence_reports_events_present_only_in_one_trace(tmp_path):
    a = _write(
        tmp_path / "a.jsonl",
        [_event(0, "run_started"), _event(1, "agent_input"), _event(2, "run_completed")],
    )
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    sequence = compare_traces(a, b)["sequence"]
    assert sequence["only_in_a"] == [{"index": 2, "event_type": "run_completed"}]
    assert sequence["only_in_b"] == []


def test_alignment_limitation_is_stated(tmp_path):
    path = _write(tmp_path / "a.jsonl", [_event(0, "run_started")])
    result = compare_traces(path, path)
    assert result["notes"] == [ALIGNMENT_NOTE]
    assert ALIGNMENT_NOTE in render_comparison(result)


# -- evaluator differences -----------------------------------------------------
def test_evaluator_differences_are_reported(tmp_path):
    denied = _write(
        tmp_path / "denied.jsonl",
        [
            _event(0, "run_started", run_id="denied"),
            _event(1, "tool_requested", tool_name="fs_sandbox"),
            _event(2, "policy_decision", decision="deny"),
            _event(3, "tool_result", ok=False),
            _event(4, "run_completed"),
        ],
    )
    allowed = _write(
        tmp_path / "allowed.jsonl",
        [
            _event(0, "run_started", run_id="allowed"),
            _event(1, "tool_requested", tool_name="calculator"),
            _event(2, "policy_decision", decision="allow"),
            _event(3, "tool_executed"),
            _event(4, "tool_result", ok=True),
            _event(5, "run_completed"),
        ],
    )
    result = compare_traces(denied, allowed)
    sections = {(d["section"], d["key"]) for d in result["evaluator"]["differences"]}
    assert ("decisions", "deny") in sections
    assert ("decisions", "allow") in sections


# -- determinism / read-only ---------------------------------------------------
def test_output_is_deterministic(tmp_path):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "agent_input")])
    first = render_comparison(compare_traces(a, b))
    second = render_comparison(compare_traces(a, b))
    assert first == second


def test_comparison_does_not_modify_either_trace(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    before_a, before_b = a.read_bytes(), b.read_bytes()
    assert main(["compare", str(a), str(b)]) == 0
    capsys.readouterr()
    assert a.read_bytes() == before_a
    assert b.read_bytes() == before_b


# -- CLI -----------------------------------------------------------------------
def test_compare_cli_exits_zero_and_prints_text(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "agent_input")])
    assert main(["compare", str(a), str(b)]) == 0
    out = capsys.readouterr().out
    assert "trace comparison" in out
    assert "Trace A" in out and "Trace B" in out
    assert "Event-type distribution" in out
    assert "Sequence differences" in out


def test_compare_cli_json_output(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "agent_input")])
    assert main(["compare", str(a), str(b), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "1"
    assert payload["trace_a"]["event_count"] == 2
    assert payload["sequence"]["changed"] == [
        {"index": 1, "a": "run_completed", "b": "agent_input"}
    ]


def test_compare_cli_is_deterministic(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started"), _event(1, "run_completed")])
    b = _write(tmp_path / "b.jsonl", [_event(0, "run_started"), _event(1, "agent_input")])
    assert main(["compare", str(a), str(b)]) == 0
    first = capsys.readouterr().out
    assert main(["compare", str(a), str(b)]) == 0
    assert capsys.readouterr().out == first


# -- errors --------------------------------------------------------------------
def test_compare_missing_trace_is_a_config_error(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_event(0, "run_started")])
    assert main(["compare", str(a), str(tmp_path / "missing.jsonl")]) == 1
    assert "error:" in capsys.readouterr().err


def test_compare_malformed_trace_is_a_config_error(tmp_path, capsys):
    good = _write(tmp_path / "good.jsonl", [_event(0, "run_started")])
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n", encoding="utf-8")
    assert main(["compare", str(good), str(bad)]) == 1
    assert "error:" in capsys.readouterr().err


# -- real lab-pair integration -------------------------------------------------
def test_compare_real_lab_pair_surfaces_the_difference(tmp_path):
    """LAB-01 (allowed calculator) vs LAB-04 (denied tool misuse)."""
    a = _run_lab(LAB01, tmp_path / "lab01.jsonl")
    b = _run_lab(LAB04, tmp_path / "lab04.jsonl")

    result = compare_traces(a, b)
    assert result["trace_a"]["scenario"] == "LAB-01-benign-agent"
    assert result["trace_b"]["scenario"] == "LAB-04-tool-misuse"

    # The benign run allows and executes a tool; the tool-misuse run is denied.
    assert result["sequence"]["identical"] is False
    sections = {(d["section"], d["key"]) for d in result["evaluator"]["differences"]}
    assert ("decisions", "deny") in sections
    assert ("tool_results", "denied") in sections

    # Deterministic, and the traces are left untouched.
    before = (a.read_bytes(), b.read_bytes())
    assert render_comparison(compare_traces(a, b)) == render_comparison(result)
    assert (a.read_bytes(), b.read_bytes()) == before


# -- same lab, two policies ----------------------------------------------------
def test_lab04_two_policy_configs_describe_the_same_experiment():
    """The permissive example is LAB-04 with only the policy changed."""
    permissive = load_experiment_config(ALLOW_ALL_CONFIG)
    denying = load_experiment_config(LAB04)
    assert permissive.experiment_id == denying.experiment_id
    assert permissive.task == denying.task
    assert permissive.mock_script == denying.mock_script
    assert permissive.agent.agent_id == denying.agent.agent_id
    assert permissive.agent.run_id == denying.agent.run_id
    assert permissive.agent.scenario == denying.agent.scenario
    assert permissive.agent.max_steps == denying.agent.max_steps
    assert Path(permissive.policy_path).name == "allow_all_v1.yaml"
    assert Path(denying.policy_path).name == "least_privilege_v1.yaml"
    assert permissive.policy_path != denying.policy_path


def test_example_policies_decide_the_out_of_scope_write_differently():
    permissive = load_policy(ALLOW_ALL_POLICY)
    least = load_policy(LEAST_PRIVILEGE_POLICY)
    kwargs = {"action": "write", "resource": "../../etc/passwd"}
    assert (
        permissive.decide("agent-1", "fs_sandbox", {}, **kwargs).decision
        is Decision.ALLOW
    )
    assert (
        least.decide("agent-1", "fs_sandbox", {}, **kwargs).decision is Decision.DENY
    )


def test_compare_same_lab_two_policies_surfaces_the_policy_boundary(tmp_path):
    """LAB-04 under a permissive vs the least-privilege policy."""
    a = _run_lab(ALLOW_ALL_CONFIG, tmp_path / "permissive.jsonl")
    b = _run_lab(LAB04, tmp_path / "least_privilege.jsonl")

    result = compare_traces(a, b)
    assert result["trace_a"]["scenario"] == "LAB-04-tool-misuse"
    assert result["trace_b"]["scenario"] == "LAB-04-tool-misuse"

    distribution = {
        entry["event_type"]: entry for entry in result["event_type_distribution"]
    }
    # Only the allowed run reaches the tool, so only it has a ``tool_executed``.
    assert distribution["tool_executed"] == {
        "event_type": "tool_executed",
        "a": 1,
        "b": 0,
        "delta": 1,
    }

    differences = {
        (d["section"], d["key"]): (d["a"], d["b"])
        for d in result["evaluator"]["differences"]
    }
    assert differences[("decisions", "allow")] == (1, 0)
    assert differences[("decisions", "deny")] == (0, 1)
    # The permissive run's request reaches the sandbox and is still refused
    # (containment); the least-privilege run denies it before the tool.
    assert differences[("tool_results", "error")] == (1, 0)
    assert differences[("tool_results", "denied")] == (0, 1)

    # Deterministic, and neither trace is modified.
    before = (a.read_bytes(), b.read_bytes())
    assert render_comparison(compare_traces(a, b)) == render_comparison(result)
    assert (a.read_bytes(), b.read_bytes()) == before


# -- same lab, two decisions ---------------------------------------------------
def test_compare_lab05_two_decisions_surfaces_the_approval_boundary(tmp_path):
    """LAB-05 requires approval; the deny-by-default example refuses it."""
    a = _run_lab(LAB05, tmp_path / "require_approval.jsonl")
    b = _run_lab(LAB05_DENY, tmp_path / "deny.jsonl")

    result = compare_traces(a, b)
    assert result["trace_a"]["scenario"] == "LAB-05-require-approval"
    assert result["trace_b"]["scenario"] == "LAB-05-require-approval"

    # Same request, same shape: the two traces are structurally identical and
    # neither executes the tool.
    assert result["event_count_delta"] == 0
    assert result["sequence"]["identical"] is True
    distribution = {
        entry["event_type"]: entry for entry in result["event_type_distribution"]
    }
    assert "tool_executed" not in distribution

    differences = {
        (d["section"], d["key"]): (d["a"], d["b"])
        for d in result["evaluator"]["differences"]
    }
    assert differences[("decisions", "require_approval")] == (1, 0)
    assert differences[("decisions", "deny")] == (0, 1)
    assert differences[("tool_results", "pending_approval")] == (1, 0)
    assert differences[("tool_results", "denied")] == (0, 1)

    # Deterministic, and neither trace is modified.
    before = (a.read_bytes(), b.read_bytes())
    assert render_comparison(compare_traces(a, b)) == render_comparison(result)
    assert (a.read_bytes(), b.read_bytes()) == before
