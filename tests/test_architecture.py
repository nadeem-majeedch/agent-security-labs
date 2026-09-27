"""Import-boundary and dependency-discipline tests.

These encode the coupling rules from Phase 14 (Task 3) and the dependency audit
(Task 22): dependencies point inward, no banned frameworks/libraries appear,
and the policy engine/tools stay independent of each other where required.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "agentsec"
TESTS = ROOT / "tests"

BANNED_TOP_LEVEL = {
    "langchain",
    "llama_index",
    "crewai",
    "langgraph",
    "autogen",
    "pandas",
    "numpy",
    "fastapi",
    "streamlit",
    "sqlite3",
    "requests",
    "flask",
    "django",
    "torch",
    "tensorflow",
}


def python_files(root: Path):
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def import_records(path: Path):
    """Yield ``(level, module)`` for every import statement."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield 0, alias.name
        elif isinstance(node, ast.ImportFrom):
            yield node.level, node.module or ""


@pytest.mark.parametrize("path", python_files(SRC), ids=lambda p: p.name)
def test_no_banned_dependency_in_source(path):
    for _level, module in import_records(path):
        top = module.split(".")[0]
        assert top not in BANNED_TOP_LEVEL, f"{path.name} imports banned module {module!r}"


@pytest.mark.parametrize("path", python_files(TESTS), ids=lambda p: p.name)
def test_no_banned_dependency_in_tests(path):
    for _level, module in import_records(path):
        top = module.split(".")[0]
        assert top not in BANNED_TOP_LEVEL, f"{path.name} imports banned module {module!r}"


def test_tools_do_not_depend_on_model_adapter():
    for path in python_files(SRC / "tools"):
        for level, module in import_records(path):
            target = module.split(".")[-1]
            assert not (
                level > 0 and target == "models"
            ), f"{path.name} must not import the model adapter package"
            assert not module.startswith("agentsec.models")


def test_policy_does_not_depend_on_tools():
    for path in python_files(SRC / "policy"):
        for level, module in import_records(path):
            target = module.split(".")[-1]
            assert not (
                level > 0 and target == "tools"
            ), f"{path.name} must not import the tools package"
            assert not module.startswith("agentsec.tools")


def test_agent_imports_only_abstractions():
    records = list(import_records(SRC / "agent.py"))
    modules = {module.split(".")[-1] for _level, module in records}
    assert modules.isdisjoint({"calculator", "fs_sandbox", "mock_db", "mock_email", "mock"})
    assert modules.isdisjoint({"policy", "deepseek", "mimo", "glm", "solar"})
    for _level, module in records:
        assert not module.startswith("agentsec.policy")
        assert not module.startswith("agentsec.models.mock")


def test_agent_does_not_import_concrete_tools():
    source = (SRC / "agent.py").read_text(encoding="utf-8")
    for concrete in ("CalculatorTool", "FsSandboxTool", "MockDatabaseTool", "MockEmailTool"):
        assert concrete not in source


def test_evaluator_is_a_read_only_analysis_layer():
    for path in python_files(SRC / "eval"):
        for _level, module in import_records(path):
            target = module.split(".")[-1]
            assert target not in {"tools", "policy", "agent", "gateway", "mock"}, (
                f"{path.name} must not import {module!r}"
            )
            assert not module.startswith(
                ("agentsec.tools", "agentsec.policy", "agentsec.agent")
            )


def test_evaluator_does_not_reference_execution_symbols():
    for path in python_files(SRC / "eval"):
        source = path.read_text(encoding="utf-8")
        for forbidden in ("ToolGateway", "PolicyEngine", "Agent(", "TraceRecorder"):
            assert forbidden not in source, f"{path.name} references {forbidden!r}"


def test_runner_does_not_depend_on_concrete_layers():
    for path in python_files(SRC / "experiment"):
        for _level, module in import_records(path):
            target = module.split(".")[-1]
            assert target not in {
                "tools",
                "policy",
                "gateway",
                "calculator",
                "fs_sandbox",
                "mock_db",
                "mock",
            }, f"{path.name} must not import {module!r}"
            assert not module.startswith(("agentsec.tools", "agentsec.policy"))


def test_runner_only_delegates():
    source = (SRC / "experiment" / "runner.py").read_text(encoding="utf-8")
    for forbidden in (
        "ToolGateway",
        "PolicyEngine",
        ".invoke(",
        ".decide(",
        "CalculatorTool",
        "FsSandboxTool",
        "MockDatabaseTool",
        ".action(",
        ".resource(",
        "max_steps",
        "tool_calls",
        "while ",
    ):
        assert forbidden not in source, f"runner must not reference {forbidden!r}"


def test_scenario_layer_does_not_execute_anything():
    for path in python_files(SRC / "scenarios"):
        for _level, module in import_records(path):
            target = module.split(".")[-1]
            assert target not in {
                "tools",
                "policy",
                "gateway",
                "calculator",
                "fs_sandbox",
                "mock_db",
                "recorder",
            }, f"{path.name} must not import {module!r}"
            assert not module.startswith(("agentsec.tools", "agentsec.policy"))
        source = path.read_text(encoding="utf-8")
        for forbidden in (
            ".invoke(",
            ".decide(",
            ".complete(",
            ".run(",
            ".action(",
            ".resource(",
            "emit_event",
            "write_event",
        ):
            assert forbidden not in source, f"{path.name} must not reference {forbidden!r}"


def test_cli_does_not_import_concrete_execution_layers():
    records = list(import_records(SRC / "cli.py"))
    modules = {module.split(".")[-1] for _level, module in records}
    assert modules.isdisjoint(
        {"tools", "policy", "gateway", "models", "agent", "mock", "calculator", "fs_sandbox", "mock_db"}
    )
    for _level, module in records:
        assert not module.startswith(
            ("agentsec.tools", "agentsec.policy", "agentsec.models", "agentsec.agent")
        )


def test_cli_contains_no_execution_logic():
    for name in ("cli.py", "mvp.py"):
        source = (SRC / name).read_text(encoding="utf-8")
        for forbidden in (
            ".complete(",
            ".invoke(",
            ".decide(",
            "while ",
            "ToolCall",
            "ModelResponse",
        ):
            assert forbidden not in source, f"{name} must not reference {forbidden!r}"


def test_mvp_composition_constructs_but_does_not_execute():
    source = (SRC / "mvp.py").read_text(encoding="utf-8")
    # construction is allowed; execution is not
    assert "build_gateway(" in source
    assert ".run(" not in source
    for forbidden in (".complete(", ".invoke(", ".decide("):
        assert forbidden not in source


def test_experiment_modules_are_sequential_only():
    for path in python_files(SRC / "experiment"):
        source = path.read_text(encoding="utf-8")
        for forbidden in (
            "threading",
            "multiprocessing",
            "asyncio",
            "concurrent.futures",
            "subprocess",
        ):
            assert forbidden not in source, f"{path.name} must not use {forbidden!r}"


def test_gateway_is_the_only_tool_execution_boundary():
    # Only the gateway may call a tool's ``run``. ``runner.py``/``cli.py`` are
    # allowed because they call the *agent's* / *runner's* run, not a tool's;
    # ``base.py`` only defines it.
    allowed = {"gateway.py", "base.py", "runner.py", "cli.py"}
    importers = []
    for path in python_files(SRC):
        source = path.read_text(encoding="utf-8")
        if ".run(" in source and path.name not in allowed:
            importers.append(path.name)
    assert importers == []


def test_policy_does_not_depend_on_trace():
    for path in python_files(SRC / "policy"):
        for level, module in import_records(path):
            target = module.split(".")[-1]
            assert not (level > 0 and target == "trace")


def test_calculator_never_calls_dangerous_builtins():
    path = SRC / "tools" / "calculator.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    dangerous = {"eval", "exec", "compile", "open", "__import__", "globals", "locals"}
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called.isdisjoint(dangerous), called & dangerous
    imported = {module.split(".")[0] for _level, module in import_records(path)}
    allowed = {"__future__", "ast", "math", "operator", "typing", "errors", "base"}
    assert imported <= allowed, imported - allowed


def test_tests_do_not_reference_the_network():
    needles = ("http" + "://", "https" + "://", "socket")
    for path in python_files(TESTS):
        if path.name == Path(__file__).name:
            continue  # this file names the needles on purpose
        source = path.read_text(encoding="utf-8")
        for needle in needles:
            assert needle not in source, f"{path.name} references {needle!r}"
