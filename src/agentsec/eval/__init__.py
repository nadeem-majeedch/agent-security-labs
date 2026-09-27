"""Evaluation package: a read-only, descriptive trace evaluator."""

from .base import (
    EvaluationInput,
    EvaluationResult,
    Evaluator,
    EventRef,
    RunOutcome,
)
from .builtin import TraceEvaluator

__all__ = [
    "Evaluator",
    "EvaluationInput",
    "EvaluationResult",
    "EventRef",
    "RunOutcome",
    "TraceEvaluator",
]
