"""The tool contract: typed schema, authorization metadata and results.

A ``Tool`` is a single sandboxed capability. It is deliberately independent of
the model adapter, the agent loop, the policy engine and trace storage: it can
be constructed and exercised on its own. Everything a tool exposes is typed:

* :class:`ToolSchema` — name, description, JSON Schema for input and output;
* :meth:`Tool.action` / :meth:`Tool.resource` — the metadata the gateway hands
  to the policy engine so authorization rules can match on ``action`` and
  ``resource`` without the policy engine knowing any concrete tool;
* :meth:`Tool.run` — execution, called only by the gateway.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Mapping, Protocol, runtime_checkable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..errors import ToolValidationError


class ToolContext(BaseModel):
    """Non-argument context a tool may need (never model/provider state)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_id: str = Field(min_length=1)
    run_id: str = ""
    scenario: str = ""
    #: Resource identifiers considered in-scope for the current task. Used by
    #: policy conditions such as ``outside_task_scope``; never by the tools.
    task_scope: tuple[str, ...] = ()


class ToolStatus(str, Enum):
    """Outcome class of a mediated tool call."""

    OK = "ok"
    ERROR = "error"
    DENIED = "denied"
    PENDING_APPROVAL = "pending_approval"


class ToolResult(BaseModel):
    """The structured outcome of a tool call.

    ``status`` distinguishes a genuine execution (``ok`` or ``error``) from a
    call that never reached the tool (``denied`` or ``pending_approval``), so a
    caller can tell *why* nothing happened.
    """

    model_config = ConfigDict(extra="forbid")

    status: ToolStatus
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    side_effects: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True only for a successful execution."""
        return self.status is ToolStatus.OK

    @property
    def executed(self) -> bool:
        """True when the tool was actually run (success or execution error)."""
        return self.status in (ToolStatus.OK, ToolStatus.ERROR)

    @classmethod
    def success(
        cls, output: Mapping[str, Any] | None = None, *, side_effects: list[str] | None = None
    ) -> "ToolResult":
        return cls(
            status=ToolStatus.OK,
            output=dict(output or {}),
            side_effects=list(side_effects or []),
        )

    @classmethod
    def failure(
        cls, error: str, *, side_effects: list[str] | None = None
    ) -> "ToolResult":
        return cls(
            status=ToolStatus.ERROR,
            error=error,
            side_effects=list(side_effects or []),
        )


class DeniedResult(ToolResult):
    """A call the policy engine refused; the tool never ran."""

    status: Literal[ToolStatus.DENIED] = ToolStatus.DENIED


class PendingApprovalResult(ToolResult):
    """A call that requires approval which was not (yet) granted."""

    status: Literal[ToolStatus.PENDING_APPROVAL] = ToolStatus.PENDING_APPROVAL


class ToolSchema(BaseModel):
    """The typed contract of a single tool."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    description: str = ""
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]

    @model_validator(mode="after")
    def _check_schemas(self) -> "ToolSchema":
        for label, schema in (
            ("input_schema", self.input_schema),
            ("output_schema", self.output_schema),
        ):
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                raise ValueError(f"{self.name}.{label} is not a valid JSON Schema: {exc.message}") from exc
        return self

    def _validate(
        self, value: Mapping[str, Any], schema: Mapping[str, Any], label: str
    ) -> dict[str, Any]:
        try:
            errors = sorted(
                Draft202012Validator(schema).iter_errors(dict(value)),
                key=lambda err: list(err.path),
            )
        except Exception as exc:  # pragma: no cover - non-serializable input
            raise ToolValidationError(self.name, f"{label} could not be validated: {exc}") from exc
        if errors:
            details = "; ".join(
                f"{'/'.join(str(part) for part in err.path) or '<root>'}: {err.message}"
                for err in errors
            )
            raise ToolValidationError(self.name, f"invalid {label}: {details}")
        return dict(value)

    def validate_args(self, args: Mapping[str, Any]) -> dict[str, Any]:
        """Validate arguments against ``input_schema`` and return a plain dict.

        Raises :class:`ToolValidationError` so the gateway can refuse the call
        before the tool is ever executed.
        """
        return self._validate(args, self.input_schema, "arguments")

    def validate_output(self, output: Mapping[str, Any]) -> dict[str, Any]:
        """Validate a tool's output against ``output_schema``."""
        return self._validate(output, self.output_schema, "output")


@runtime_checkable
class Tool(Protocol):
    """The only interface the gateway uses to reach a capability."""

    name: str

    def schema(self) -> ToolSchema:
        """Return the typed input/output contract."""
        ...

    def action(self, args: Mapping[str, Any]) -> str:
        """Return the action label used for authorization (e.g. ``read``)."""
        ...

    def resource(self, args: Mapping[str, Any]) -> str | None:
        """Return the resource identifier used for authorization, if any."""
        ...

    def run(self, args: dict[str, Any], ctx: ToolContext) -> ToolResult:
        """Execute the capability. Called **only** by the ToolGateway."""
        ...


class BaseTool:
    """Convenience base for concrete tools.

    Subclasses set :attr:`name`, :attr:`description`, :data:`INPUT_SCHEMA` and
    :data:`OUTPUT_SCHEMA` and implement :meth:`run`. The default action is
    ``"invoke"`` and the default resource is ``None``.
    """

    name: str = ""
    description: str = ""
    INPUT_SCHEMA: dict[str, Any] = {"type": "object"}
    OUTPUT_SCHEMA: dict[str, Any] = {"type": "object"}

    def schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema=self.INPUT_SCHEMA,
            output_schema=self.OUTPUT_SCHEMA,
        )

    def action(self, args: Mapping[str, Any]) -> str:  # noqa: ARG002 - default
        return "invoke"

    def resource(self, args: Mapping[str, Any]) -> str | None:  # noqa: ARG002 - default
        return None

    def run(self, args: dict[str, Any], ctx: ToolContext) -> ToolResult:  # pragma: no cover
        raise NotImplementedError
