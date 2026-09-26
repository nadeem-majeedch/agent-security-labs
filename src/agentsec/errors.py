"""Typed exceptions used by the currently implemented modules.

The Phase 14 blueprint lists a fuller hierarchy (tool, policy, evaluation and
config errors). Those are intentionally **not** defined here yet: the modules
that raise them do not exist in this implementation step, and unused exception
classes would be dead code.
"""

from __future__ import annotations


class AgentSecError(Exception):
    """Base class for all AgentSec errors."""


class UnsupportedParameter(AgentSecError):
    """Raised when a caller passes a parameter the adapter does not support.

    A provider that documents a parameter as unavailable must report the
    capability as ``False`` and raise this error rather than silently
    substituting a default (Phase 14, Task 5).
    """

    def __init__(self, parameter: str, model_id: str) -> None:
        super().__init__(f"{model_id!r} does not support parameter {parameter!r}")
        self.parameter = parameter
        self.model_id = model_id


class ModelError(AgentSecError):
    """Raised for invalid model requests or unrecoverable adapter failures."""


class TraceSchemaError(AgentSecError):
    """Raised when a trace event does not conform to the versioned schema."""


class TraceWriteError(AgentSecError):
    """Raised when a trace cannot be written to disk."""
