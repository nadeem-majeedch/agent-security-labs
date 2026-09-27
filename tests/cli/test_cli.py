"""Tests for the thin, in-process command-line interface.

The CLI is exercised by calling :func:`agentsec.cli.main` directly and asserting
command semantics, exit codes and structured output rather than terminal
formatting.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from agentsec.agent import RunResult, RunStatus
from agentsec.cli import main
from agentsec.experiment import ExperimentResult
from agentsec.models.mock import MockAction, MockScript, MockStep

REPO = Path(__file__).resolve().parents[2]
LEAST_PRIVILEGE = REPO / "policies" / "examples" / "least_privilege_v1.yaml"
DENY_BY_DEFAULT = REPO / "policies" / "examples" / "deny_by_default.yaml"


def write_config(
    tmp_path: Path,
    *,
    task: str = "please add 2 and 3",
    mock_script: str = "benign",
    policy_path: Path | None = LEAST_PRIVILEGE,
    max_steps: int = 6,
    trace_name: str = "trace.jsonl",
    extra: dict | None = None,
) -> Path:
    data = {
        "experiment_id": "cli-exp",
        "task": task,
        "mock_script": mock_script,
        "trace_path": str(tmp_path / trace_name),
        "agent": {
            "agent_id": "agent-1",
            "run_id": "run-1",
            "scenario": "LAB-01-a",
            "max_steps": max_steps,
        },
    }
    if policy_path is not None:
        data["policy_path"] = str(policy_path)
    if extra:
        data.update(extra)
    path = tmp_path / "exp.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# -- help / usage --------------------------------------------------------------
def test_help_exits_zero():
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0


def test_no_command_is_a_config_error(capsys):
    assert main([]) == 1
    assert "usage" in capsys.readouterr().err


def test_unknown_command_uses_config_exit_code(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["nope"])
    assert excinfo.value.code == 1


# -- run -----------------------------------------------------------------------
def test_run_benign_config(tmp_path, capsys):
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "experiment: cli-exp" in out
    assert "agent status: completed" in out
    assert "evaluation status: completed" in out
    assert (tmp_path / "trace.jsonl").is_file()


def test_run_allowed_tool(tmp_path, capsys):
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "tool calls: calculator=1" in out
    assert "policy decisions: allow=1 deny=0 require_approval=0" in out


def test_run_denied_tool_is_not_a_cli_error(tmp_path, capsys):
    config = write_config(tmp_path, policy_path=DENY_BY_DEFAULT)
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "deny=1" in out
    assert "tool_executions=0" in out
    assert "agent status: completed" in out


def test_run_pending_approval(tmp_path, capsys):
    config = write_config(
        tmp_path,
        task="look up the key",
        mock_script="authorization_violation",
        policy_path=LEAST_PRIVILEGE,
    )
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "require_approval=1" in out
    assert "pending_approval=1" in out


def test_run_multi_step(tmp_path, capsys):
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "model_calls=2" in out


def test_run_step_limit_preserves_outcome(tmp_path, capsys, monkeypatch):
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
    config = write_config(tmp_path, max_steps=3)
    assert main(["run", str(config)]) == 0
    out = capsys.readouterr().out
    assert "agent status: step_limit" in out
    assert "evaluation status: step_limit" in out


def test_run_json_output(tmp_path, capsys):
    config = write_config(tmp_path)
    assert main(["run", str(config), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["experiment_id"] == "cli-exp"
    assert payload["agent"]["status"] == "completed"
    assert payload["evaluation"]["status"] == "completed"
    assert payload["trace_path"]


def test_run_writes_a_valid_trace(tmp_path):
    config = write_config(tmp_path)
    main(["run", str(config)])
    lines = (tmp_path / "trace.jsonl").read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(line) for line in lines]
    assert events[0]["event_type"] == "run_started"
    assert events[-1]["event_type"] in {"run_completed", "run_failed"}
    assert {event["run_id"] for event in events} == {"run-1"}


def test_run_missing_config_is_config_error(tmp_path, capsys):
    assert main(["run", str(tmp_path / "nope.yaml")]) == 1
    assert "error:" in capsys.readouterr().err


def test_run_malformed_config_is_config_error(tmp_path, capsys):
    path = tmp_path / "bad.yaml"
    path.write_text("experiment_id: [\n", encoding="utf-8")
    assert main(["run", str(path)]) == 1
    assert "error:" in capsys.readouterr().err


def test_run_unknown_mock_script_is_config_error(tmp_path, capsys):
    config = write_config(tmp_path, mock_script="not_a_script")
    assert main(["run", str(config)]) == 1
    assert "error:" in capsys.readouterr().err


def test_run_is_deterministic(tmp_path, capsys):
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    first = capsys.readouterr().out
    assert main(["run", str(config)]) == 0
    second = capsys.readouterr().out
    assert first == second


# -- evaluate / inspect --------------------------------------------------------
def _produce_trace(tmp_path, capsys) -> Path:
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    capsys.readouterr()  # discard the run output; only the command under test matters
    return tmp_path / "trace.jsonl"


def test_evaluate_command(tmp_path, capsys):
    trace = _produce_trace(tmp_path, capsys)
    assert main(["evaluate", str(trace)]) == 0
    out = capsys.readouterr().out
    assert "evaluation status: completed" in out
    assert "tool calls: calculator=1" in out


def test_evaluate_json(tmp_path, capsys):
    trace = _produce_trace(tmp_path, capsys)
    assert main(["evaluate", str(trace), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "completed"
    assert payload["tool_calls"] == {"calculator": 1}


def test_evaluate_missing_trace_is_config_error(tmp_path, capsys):
    assert main(["evaluate", str(tmp_path / "nope.jsonl")]) == 1
    assert "error:" in capsys.readouterr().err


def test_evaluate_invalid_trace_is_config_error(tmp_path, capsys):
    path = tmp_path / "trace.jsonl"
    path.write_text("not json\n", encoding="utf-8")
    assert main(["evaluate", str(path)]) == 1
    assert "error:" in capsys.readouterr().err


def test_evaluate_does_not_execute_anything(tmp_path, capsys, monkeypatch):
    trace = _produce_trace(tmp_path, capsys)

    from agentsec.policy.base import PolicyEngine
    from agentsec.tools.gateway import ToolGateway

    def explode(*args, **kwargs):  # pragma: no cover - must not run
        raise AssertionError("evaluate must not execute")

    monkeypatch.setattr(ToolGateway, "invoke", explode)
    monkeypatch.setattr(PolicyEngine, "decide", explode)
    assert main(["evaluate", str(trace)]) == 0


def test_inspect_command(tmp_path, capsys):
    trace = _produce_trace(tmp_path, capsys)
    assert main(["inspect", str(trace)]) == 0
    out = capsys.readouterr().out
    assert "events:" in out
    assert "run_started" in out
    assert "parent=ev-000000" in out


# -- delegation / no retry -----------------------------------------------------
class SpyRunner:
    def __init__(self, *, error: str | None = None) -> None:
        self.calls: list[ExperimentResult] = []
        self._error = error

    def run(self, config) -> ExperimentResult:
        result = ExperimentResult(
            experiment_id=config.experiment_id,
            run_id=config.agent.run_id,
            scenario=config.agent.scenario,
            agent=RunResult(status=RunStatus.COMPLETED, output="x", steps=1),
            error=self._error,
        )
        self.calls.append(result)
        return result


def test_run_delegates_to_the_runner(tmp_path, monkeypatch, capsys):
    spy = SpyRunner()
    captured: list = []
    monkeypatch.setattr(
        "agentsec.cli.build_mvp_runner", lambda config: captured.append(config) or spy
    )
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 0
    assert len(captured) == 1
    assert captured[0].experiment_id == "cli-exp"
    assert len(spy.calls) == 1
    assert "agent status: completed" in capsys.readouterr().out


def test_no_hidden_retry_on_orchestration_error(tmp_path, monkeypatch, capsys):
    spy = SpyRunner(error="TraceReadError: boom")
    monkeypatch.setattr("agentsec.cli.build_mvp_runner", lambda config: spy)
    config = write_config(tmp_path)
    assert main(["run", str(config)]) == 2
    assert len(spy.calls) == 1
    out = capsys.readouterr().out
    assert "error: TraceReadError: boom" in out


# -- console entry point -------------------------------------------------------
def test_python_m_agentsec_help():
    env = {"PYTHONPATH": str(REPO / "src")}
    import os

    proc = subprocess.run(
        [sys.executable, "-m", "agentsec", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, **env},
    )
    assert proc.returncode == 0
    assert "usage" in proc.stdout
