"""AgentSec Lab - educational, reproducible agent-security infrastructure.

Phase A skeleton: core data models, trace schema/validation, redaction and a
deterministic mock model. Deliberately no adapters, tools, policy engine, agent
loop, evaluator, runner or CLI yet (see research/14-implementation-blueprint.md).

This package makes **no research-novelty claim**; it reimplements established
concepts for teaching and reproducible experimentation.
"""

from .errors import (
    AgentSecError,
    ModelError,
    TraceSchemaError,
    TraceWriteError,
    UnsupportedParameter,
)

__version__ = "0.0.1"

__all__ = [
    "__version__",
    "AgentSecError",
    "ModelError",
    "TraceSchemaError",
    "TraceWriteError",
    "UnsupportedParameter",
]
