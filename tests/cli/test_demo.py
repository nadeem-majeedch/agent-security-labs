"""Tests for the one-command LAB-04 two-policy demonstration.

The planning/orchestration is unit-tested with an **injected fake executor** (so
no real run happens), and the CLI wrapper is exercised once end to end for a real
integration/smoke test. Traces are written only to ``tmp_path``; the repository is
never written to.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agentsec.cli import main
from agentsec.compare import compare_traces
from agentsec.demo import (
    LAB04_TWO_POLICIES,
    demo_to_dict,
    plan_demo,
    render_demo,
    run_demo,
)
from agentsec.errors import ConfigError

REPO = Path(__file__).resolve().parents[2]
LAB04_CONFIG = REPO / "labs" / "LAB-04-tool-misuse" / "config.yaml"
ALLOW_ALL_POLICY = REPO / "policies" / "examples" / "allow_all_v1.yaml"
LEAST_PRIVILEGE_POLICY = REPO / "policies" / "examples" / "least_privilege_v1.yaml"


# -- helpers -------------------------------------------------------------------
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


def _fake_executor(records: list):
    """An executor that writes a per-policy synthetic trace and records configs."""

    def execute(config) -> None:
        records.append(config)
        permissive = "allow_all" in str(config.policy_path)
        if permissive:
            events = [
                _event(0, "run_started"),
                _event(1, "tool_requested"),
                _event(2, "policy_decision", decision="allow"),
                _event(3, "tool_executed"),
                _event(4, "tool_result", ok=False),
                _event(5, "run_completed"),
            ]
        else:
            events = [
                _event(0, "run_started"),
                _event(1, "tool_requested"),
                _event(2, "policy_decision", decision="deny"),
                _event(3, "tool_result", ok=False),
                _event(4, "run_completed"),
            ]
        _write_trace(Path(config.trace_path), events)

    return execute


# -- planning ------------------------------------------------------------------
def test_plan_demo_changes_only_the_policy_and_output(tmp_path):
    runs = plan_demo(tmp_path, REPO)
    assert len(runs) == 2
    assert Path(runs[0].policy_path).name == "allow_all_v1.yaml"
    assert Path(runs[1].policy_path).name == "least_privilege_v1.yaml"
    # Same experiment; only the policy and the output trace path differ.
    assert runs[0].config.experiment_id == runs[1].config.experiment_id
    assert runs[0].config.task == runs[1].config.task
    assert runs[0].config.mock_script == runs[1].config.mock_script
    assert runs[0].config.agent.agent_id == runs[1].config.agent.agent_id
    assert runs[0].config.agent.run_id == runs[1].config.agent.run_id
    assert runs[0].trace_path != runs[1].trace_path
    assert all(r.trace_path.parent == tmp_path for r in runs)


# -- orchestration -------------------------------------------------------------
def test_run_demo_executes_both_policies_and_compares(tmp_path):
    records: list = []
    outcome = run_demo(tmp_path, root=REPO, execute=_fake_executor(records))

    # Both policies were actually used, and both traces were generated.
    used = {Path(c.policy_path).name for c in records}
    assert used == {"allow_all_v1.yaml", "least_privilege_v1.yaml"}
    assert (tmp_path / "trace-a.jsonl").is_file()
    assert (tmp_path / "trace-b.jsonl").is_file()

    assert len(outcome.labels) == 2
    distribution = {
        entry["event_type"]: entry for entry in outcome.comparison["event_type_distribution"]
    }
    assert distribution["tool_executed"] == {
        "event_type": "tool_executed",
        "a": 1,
        "b": 0,
        "delta": 1,
    }
    differences = {
        (d["section"], d["key"]): (d["a"], d["b"])
        for d in outcome.comparison["evaluator"]["differences"]
    }
    assert differences[("decisions", "allow")] == (1, 0)
    assert differences[("decisions", "deny")] == (0, 1)


def test_run_demo_is_deterministic(tmp_path):
    first = run_demo(tmp_path / "a", root=REPO, execute=_fake_executor([]))
    second = run_demo(tmp_path / "b", root=REPO, execute=_fake_executor([]))
    assert render_demo(first) == render_demo(second)


def test_run_demo_invokes_the_existing_comparison(tmp_path, monkeypatch):
    calls: list = []
    real = compare_traces

    def spy(a, b):
        calls.append((Path(a), Path(b)))
        return real(a, b)

    monkeypatch.setattr("agentsec.demo.compare_traces", spy)
    run_demo(tmp_path, root=REPO, execute=_fake_executor([]))
    assert calls == [(tmp_path / "trace-a.jsonl", tmp_path / "trace-b.jsonl")]


def test_run_demo_requires_a_trace(tmp_path):
    def execute(config) -> None:  # writes nothing
        return None

    with pytest.raises(ConfigError):
        run_demo(tmp_path, root=REPO, execute=execute)


def test_run_demo_propagates_execution_failure(tmp_path):
    def execute(config) -> None:
        raise ConfigError("boom")

    with pytest.raises(ConfigError, match="boom"):
        run_demo(tmp_path, root=REPO, execute=execute)


def test_run_demo_does_not_modify_repository_files(tmp_path):
    watched = {
        path: path.read_bytes()
        for path in (LAB04_CONFIG, ALLOW_ALL_POLICY, LEAST_PRIVILEGE_POLICY)
    }
    run_demo(tmp_path, root=REPO, execute=_fake_executor([]))
    for path, before in watched.items():
        assert path.read_bytes() == before, f"{path} was modified"


# -- CLI -----------------------------------------------------------------------
def test_demo_cli_runs_the_real_stack(capsys):
    """One real integration/smoke test: the actual MVP stack, end to end."""
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    out = capsys.readouterr().out
    assert "Trace A: permissive (allow_all_v1)" in out
    assert "Trace B: least privilege (least_privilege_v1)" in out
    assert "tool_executed" in out
    assert "decisions.deny: 0 -> 1" in out


def test_demo_cli_is_deterministic(capsys):
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    first = capsys.readouterr().out
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    assert capsys.readouterr().out == first


def test_demo_cli_cleans_up_its_temporary_directory(capsys, monkeypatch):
    real = tempfile.TemporaryDirectory
    created: list[str] = []

    class Recording(real):  # type: ignore[misc, valid-type]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self.name)

    monkeypatch.setattr(tempfile, "TemporaryDirectory", Recording)
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    capsys.readouterr()
    assert created, "the demo should create a temporary directory"
    assert not Path(created[0]).exists(), "the temporary directory was not removed"


def test_demo_cli_does_not_write_into_the_repository(capsys):
    watched = {
        path: path.read_bytes()
        for path in (LAB04_CONFIG, ALLOW_ALL_POLICY, LEAST_PRIVILEGE_POLICY)
    }
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    capsys.readouterr()
    for path, before in watched.items():
        assert path.read_bytes() == before


def test_demo_cli_execution_failure_is_non_zero(capsys, monkeypatch):
    def explode(config):
        raise ConfigError("no runner")

    monkeypatch.setattr("agentsec.cli.build_mvp_runner", explode)
    assert main(["demo", LAB04_TWO_POLICIES]) == 1
    assert "error:" in capsys.readouterr().err


def test_demo_cli_unknown_name_is_a_usage_error():
    with pytest.raises(SystemExit) as excinfo:
        main(["demo", "nope"])
    assert excinfo.value.code == 1


def test_demo_referenced_files_exist():
    assert LAB04_CONFIG.is_file()
    assert ALLOW_ALL_POLICY.is_file()
    assert LEAST_PRIVILEGE_POLICY.is_file()


# -- JSON output ---------------------------------------------------------------
_TOP_LEVEL = {"schema_version", "demo", "title", "status", "policies", "comparison"}


def _demo_json(capsys) -> dict:
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def test_demo_json_is_valid_with_the_expected_top_level_fields(capsys):
    payload = _demo_json(capsys)
    assert set(payload) == _TOP_LEVEL
    assert payload["schema_version"] == "1"


def test_demo_json_reports_the_demo_name_and_status(capsys):
    payload = _demo_json(capsys)
    assert payload["demo"] == LAB04_TWO_POLICIES
    assert payload["title"] == "LAB-04 under two policies"
    assert payload["status"] == "ok"


def test_demo_json_represents_both_policies(capsys):
    payload = _demo_json(capsys)
    by_trace = {entry["trace"]: entry for entry in payload["policies"]}
    assert by_trace["A"]["policy"] == "policies/examples/allow_all_v1.yaml"
    assert by_trace["B"]["policy"] == "policies/examples/least_privilege_v1.yaml"
    assert "permissive" in by_trace["A"]["label"]
    assert "least privilege" in by_trace["B"]["label"]


def test_demo_json_represents_trace_identity_counts_and_delta(capsys):
    comparison = _demo_json(capsys)["comparison"]
    assert comparison["trace_a"]["run_id"] == "lab04-run-1"
    assert comparison["trace_a"]["scenario"] == "LAB-04-tool-misuse"
    assert comparison["trace_b"]["scenario"] == "LAB-04-tool-misuse"
    assert comparison["trace_a"]["event_count"] == 12
    assert comparison["trace_b"]["event_count"] == 11
    assert comparison["event_count_delta"] == 1


def test_demo_json_represents_evaluator_differences(capsys):
    differences = {
        (d["section"], d["key"]): (d["a"], d["b"])
        for d in _demo_json(capsys)["comparison"]["evaluator"]["differences"]
    }
    assert differences[("decisions", "allow")] == (1, 0)
    assert differences[("decisions", "deny")] == (0, 1)
    assert differences[("tool_results", "denied")] == (0, 1)
    assert differences[("tool_results", "error")] == (1, 0)


def test_demo_to_dict_reuses_the_comparison_object(tmp_path):
    outcome = run_demo(tmp_path, root=REPO, execute=_fake_executor([]))
    document = demo_to_dict(outcome, name=LAB04_TWO_POLICIES)
    # It embeds the comparison produced by the demo rather than recomputing it.
    assert document["comparison"] is outcome.comparison


def test_demo_json_contains_no_volatile_values(capsys):
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 0
    text = capsys.readouterr().out
    for forbidden in (
        "trace_path",
        "timestamp",
        "agentsec-demo-",
        "TemporaryDirectory",
        chr(92),  # a backslash (Windows separator) must never appear
    ):
        assert forbidden not in text, f"unexpected {forbidden!r} in the JSON output"


def test_demo_json_is_deterministic(capsys):
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 0
    first = capsys.readouterr().out
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 0
    assert capsys.readouterr().out == first


def test_demo_default_output_is_unchanged(capsys):
    assert main(["demo", LAB04_TWO_POLICIES]) == 0
    out = capsys.readouterr().out
    assert out.startswith("LAB-04 under two policies\n")
    assert "Trace A: permissive (allow_all_v1)" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_demo_json_leaves_no_traces_in_the_repository(capsys):
    watched = {
        path: path.read_bytes()
        for path in (LAB04_CONFIG, ALLOW_ALL_POLICY, LEAST_PRIVILEGE_POLICY)
    }
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 0
    capsys.readouterr()
    for path, before in watched.items():
        assert path.read_bytes() == before
    assert not (REPO / "runs" / "lab04_tool_misuse_allow_all").exists()


def test_demo_json_failure_emits_no_partial_output(capsys, monkeypatch):
    def explode(config):
        raise ConfigError("no runner")

    monkeypatch.setattr("agentsec.cli.build_mvp_runner", explode)
    assert main(["demo", LAB04_TWO_POLICIES, "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "error:" in captured.err


def test_demo_json_unknown_name_is_a_usage_error():
    with pytest.raises(SystemExit) as excinfo:
        main(["demo", "nope", "--json"])
    assert excinfo.value.code == 1
