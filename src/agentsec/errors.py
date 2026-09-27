"""Typed exceptions used by the currently implemented modules.

The Phase 14 blueprint lists a fuller hierarchy; scenario/config errors are
intentionally **not** defined here yet because the modules that would raise them
do not exist, and unused exception classes would be dead code.
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


class AgentError(AgentSecError):
    """Raised for invalid agent configuration or unrecoverable loop failures."""


class MaxStepsExceeded(AgentError):
    """Raised when an agent loop reaches its step limit without finishing."""

    def __init__(self, max_steps: int) -> None:
        super().__init__(f"agent reached the maximum of {max_steps} step(s) without a final answer")
        self.max_steps = max_steps


class ModelError(AgentSecError):
    """Raised for invalid model requests or unrecoverable adapter failures."""



class ConfigError(AgentSecError):
    """Raised when a component cannot be constructed from configuration."""


class ToolValidationError(AgentSecError):
    """Raised when tool arguments or output fail schema/semantic validation.

    The gateway raises this before execution, so a tool never sees arguments
    that do not satisfy its declared input schema.
    """

    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(f"{tool_name}: {message}")
        self.tool_name = tool_name
        self.message = message


class ToolExecutionError(AgentSecError):
    """Raised when a tool fails while executing already-validated arguments."""

    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(f"{tool_name}: {message}")
        self.tool_name = tool_name
        self.message = message


class UnknownTool(AgentSecError):
    """Raised when a caller requests a tool the gateway does not hold."""

    def __init__(self, tool_name: str) -> None:
        super().__init__(f"unknown tool {tool_name!r}")
        self.tool_name = tool_name


class PolicyDenied(AgentSecError):
    """Raised by the gateway in strict mode when a policy denies a call.

    The default gateway behaviour is to *return* a ``DeniedResult`` so a caller
    (for example the future agent loop) can continue and record the denial in
    the trace. Strict mode exists for callers that prefer an exception.
    """

    def __init__(self, tool_name: str, reason: str, matched_rule: str | None = None) -> None:
        super().__init__(f"policy denied {tool_name!r}: {reason}")
        self.tool_name = tool_name
        self.reason = reason
        self.matched_rule = matched_rule


class PolicyConfigError(AgentSecError):
    """Raised when a policy document or rule is malformed."""


class ScenarioConfigError(AgentSecError):
    """Raised when a scenario definition or registry entry is malformed.

    Observation mismatches are *not* errors of this kind: they are represented
    as a ``ScenarioOutcome``. This error is reserved for invalid configuration
    (bad YAML, missing fields, duplicate/unknown scenario ids).
    """


class EvaluationError(AgentSecError):
    """Raised when an evaluation input cannot be read at all.

    Content problems inside an otherwise readable trace are reported as
    warnings on the result; this error is reserved for fundamental input
    failures (for example an unreadable or non-JSON trace file), so the
    evaluator never silently produces misleading metrics.
    """


class TraceSchemaError(AgentSecError):
    """Raised when a trace event does not conform to the versioned schema."""


class TraceWriteError(AgentSecError):
    """Raised when a trace cannot be written to disk."""
