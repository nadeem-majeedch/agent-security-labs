"""A safe, AST-restricted calculator.

This is an **educational sandbox, not a Python interpreter**. It parses a small
arithmetic expression language and refuses everything else. There is no
``eval``, no ``exec``, no attribute access, no subscripts, no comprehensions,
no lambdas, no names other than a tiny function whitelist, no strings, no
imports and no I/O.

Supported expression language:

* integer and float literals (booleans are rejected - they are not numbers here);
* binary ``+  -  *  /  //  %  **``;
* unary ``+`` and ``-``;
* parentheses;
* whitelisted calls: ``abs(x)``, ``round(x[, n])``, ``min(...)``, ``max(...)``.

Everything else raises :class:`ToolValidationError`. Arithmetic that fails at
runtime (division by zero, overflow, non-finite result) raises
:class:`ToolExecutionError`. Output is always a finite ``float``, which keeps
results deterministic across platforms.
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Any, Callable, Mapping

from ..errors import ToolExecutionError, ToolValidationError
from .base import BaseTool, ToolContext, ToolResult

NAME = "calculator"
MAX_EXPRESSION_LENGTH = 200
MAX_NODES = 64
MAX_POW_EXPONENT = 64
MAX_POW_BASE = 1_000_000.0

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "expr": {"type": "string", "minLength": 1, "maxLength": MAX_EXPRESSION_LENGTH}
    },
    "required": ["expr"],
    "additionalProperties": False,
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"value": {"type": "number"}},
    "required": ["value"],
    "additionalProperties": False,
}

_BIN_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


def _fail(message: str) -> ToolValidationError:
    return ToolValidationError(NAME, message)


def _require_number(value: Any, context: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _fail(f"{context} must be a number, got {type(value).__name__}")
    return value


def _call_abs(args: list[Any]) -> float:
    if len(args) != 1:
        raise _fail("abs() takes exactly one argument")
    return abs(_require_number(args[0], "abs() argument"))


def _call_round(args: list[Any]) -> float:
    if len(args) not in (1, 2):
        raise _fail("round() takes one or two arguments")
    number = _require_number(args[0], "round() argument")
    if len(args) == 1:
        return round(number)
    digits = _require_number(args[1], "round() ndigits")
    if not isinstance(digits, int):
        raise _fail("round() ndigits must be an integer")
    if abs(digits) > 12:
        raise _fail("round() ndigits out of range")
    return round(number, digits)


def _call_min(args: list[Any]) -> float:
    if not args:
        raise _fail("min() needs at least one argument")
    return min(_require_number(arg, "min() argument") for arg in args)


def _call_max(args: list[Any]) -> float:
    if not args:
        raise _fail("max() needs at least one argument")
    return max(_require_number(arg, "max() argument") for arg in args)


#: The complete set of callable names; nothing else may be called.
_ALLOWED_FUNCTIONS: dict[str, Callable[[list[Any]], float]] = {
    "abs": _call_abs,
    "round": _call_round,
    "min": _call_min,
    "max": _call_max,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _fail(f"unsupported literal: {value!r}")
        return value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise _fail(f"unsupported operator: {op_type.__name__}")
        left = _eval(node.left)
        right = _eval(node.right)
        if op_type is ast.Pow:
            _guard_power(left, right)
        try:
            return _BIN_OPS[op_type](left, right)
        except ZeroDivisionError as exc:
            raise ToolExecutionError(NAME, "division by zero") from exc
        except OverflowError as exc:
            raise ToolExecutionError(NAME, "numeric overflow") from exc

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return +_eval(node.operand)
        if isinstance(node.op, ast.USub):
            return -_eval(node.operand)
        raise _fail(f"unsupported unary operator: {type(node.op).__name__}")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise _fail("only direct calls to whitelisted functions are allowed")
        if node.keywords:
            raise _fail("keyword arguments are not allowed")
        name = node.func.id
        handler = _ALLOWED_FUNCTIONS.get(name)
        if handler is None:
            allowed = ", ".join(sorted(_ALLOWED_FUNCTIONS))
            raise _fail(f"function {name!r} is not allowed (allowed: {allowed})")
        return handler([_eval(arg) for arg in node.args])

    raise _fail(f"unsupported expression element: {type(node).__name__}")


def _guard_power(base: float, exponent: float) -> None:
    if abs(exponent) > MAX_POW_EXPONENT:
        raise _fail(f"exponent magnitude must be <= {MAX_POW_EXPONENT}")
    if abs(base) > MAX_POW_BASE:
        raise _fail("base magnitude too large for '**'")


def evaluate(expr: str) -> float:
    """Evaluate ``expr`` and return a finite float.

    Raises :class:`ToolValidationError` for any expression outside the supported
    language and :class:`ToolExecutionError` for failing arithmetic.
    """
    if not isinstance(expr, str):
        raise _fail("expr must be a string")
    if not expr.strip():
        raise _fail("expr must not be empty")
    if len(expr) > MAX_EXPRESSION_LENGTH:
        raise _fail(f"expr must be <= {MAX_EXPRESSION_LENGTH} characters")
    if "\x00" in expr:
        raise _fail("expr must not contain null bytes")

    try:
        tree = ast.parse(expr, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise _fail(f"invalid expression syntax: {exc}") from exc

    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise _fail(f"expression is too complex (more than {MAX_NODES} nodes)")

    value = float(_eval(tree))
    if not math.isfinite(value):
        raise ToolExecutionError(NAME, "result is not a finite number")
    return value


class CalculatorTool(BaseTool):
    """Deterministic, offline baseline tool."""

    name = NAME
    description = "Evaluate a small arithmetic expression (AST-restricted, no code execution)."
    INPUT_SCHEMA = INPUT_SCHEMA
    OUTPUT_SCHEMA = OUTPUT_SCHEMA

    def action(self, args: Mapping[str, Any]) -> str:  # noqa: ARG002 - fixed action
        return "invoke"

    def resource(self, args: Mapping[str, Any]) -> str | None:  # noqa: ARG002 - no resource
        return None

    def run(self, args: dict[str, Any], ctx: ToolContext) -> ToolResult:
        value = evaluate(args["expr"])
        return ToolResult.success({"value": value})
