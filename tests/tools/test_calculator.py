"""Tests for the AST-restricted calculator tool."""

from __future__ import annotations

import math

import pytest

from agentsec.errors import ToolExecutionError, ToolValidationError
from agentsec.tools.base import ToolContext, ToolStatus
from agentsec.tools.calculator import CalculatorTool, evaluate

CTX = ToolContext(agent_id="agent-1")


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("2+3", 5.0),
        ("2 + 3 * 4", 14.0),
        ("(2 + 3) * 4", 20.0),
        ("10 / 4", 2.5),
        ("7 // 2", 3.0),
        ("7 % 3", 1.0),
        ("2 ** 10", 1024.0),
        ("-5", -5.0),
        ("+5", 5.0),
        ("--5", 5.0),
        ("0x10 + 1", 17.0),
        ("1_000 + 1", 1001.0),
        ("3.5 + 0.5", 4.0),
        ("abs(-4)", 4.0),
        ("min(1, 2, 3)", 1.0),
        ("max(1, 2, 3)", 3.0),
        ("round(3.14159, 2)", 3.14),
        ("round(2.5)", 2.0),
    ],
)
def test_supported_expressions(expr, expected):
    assert evaluate(expr) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('echo hi')",
        "open('/etc/passwd').read()",
        "(1).__class__",
        "(1.0).real",
        "lambda: 1",
        "[x for x in range(3)]",
        "a + 1",
        "print(1)",
        "eval('1+1')",
        "1 if True else 2",
        "2 < 3",
        "'a' + 'b'",
        "b'abc'",
        "f'{1}'",
        "x := 5",
        "abs(x=1)",
        "{1: 2}",
        "[1, 2]",
        "(1, 2)",
    ],
)
def test_malicious_or_unsupported_expressions_are_rejected(expr):
    with pytest.raises(ToolValidationError):
        evaluate(expr)


@pytest.mark.parametrize("expr", ["2 ** 1000", "1000001 ** 2", "2 ** -1000"])
def test_exponent_guard_rejects_huge_powers(expr):
    with pytest.raises(ToolValidationError):
        evaluate(expr)


@pytest.mark.parametrize("expr", ["1/0", "1//0", "1%0", "1e308 * 1e308"])
def test_failing_arithmetic_is_an_execution_error(expr):
    with pytest.raises(ToolExecutionError):
        evaluate(expr)


@pytest.mark.parametrize("expr", ["", "   ", "\x00", "1 +"])
def test_invalid_text_is_rejected(expr):
    with pytest.raises(ToolValidationError):
        evaluate(expr)


def test_over_long_expression_is_rejected():
    with pytest.raises(ToolValidationError):
        evaluate("1+" * 200 + "1")


def test_too_many_nodes_is_rejected():
    with pytest.raises(ToolValidationError):
        evaluate("+".join(["1"] * 40))


def test_result_is_always_finite_float():
    value = evaluate("2+3")
    assert isinstance(value, float)
    assert math.isfinite(value)


def test_evaluation_is_deterministic():
    assert evaluate("2+3") == evaluate("2+3")


def test_tool_run_returns_success_result():
    result = CalculatorTool().run({"expr": "6*7"}, CTX)
    assert result.status is ToolStatus.OK
    assert result.output == {"value": 42.0}
    assert result.ok is True


def test_tool_output_validates_against_output_schema():
    tool = CalculatorTool()
    result = tool.run({"expr": "1+1"}, CTX)
    assert tool.schema().validate_output(result.output) == {"value": 2.0}


def test_schema_rejects_missing_and_wrong_typed_args():
    schema = CalculatorTool().schema()
    with pytest.raises(ToolValidationError):
        schema.validate_args({})
    with pytest.raises(ToolValidationError):
        schema.validate_args({"expr": 5})
    with pytest.raises(ToolValidationError):
        schema.validate_args({"expr": "1+1", "extra": True})


def test_action_and_resource_metadata():
    tool = CalculatorTool()
    assert tool.action({"expr": "1+1"}) == "invoke"
    assert tool.resource({"expr": "1+1"}) is None
