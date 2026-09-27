"""A tiny, in-memory, synthetic email "sender".

There is **no SMTP, no network, no socket, no subprocess and no persistence**:
sending appends one record to a plain Python list held by the instance. Two
instances never share state, so independent runs cannot leak into each other,
and a fresh instance always starts with an empty outbox.

The tool's value for the labs is that it is a *sink*: it is the moment an agent
hands content across an egress boundary. Its output deliberately carries **no
payload** - only a boolean, the recipient and a message id - so the only place
the sent content is retained is the tool call's own (redacted) arguments in the
trace. Message ids are a deterministic per-instance counter (``msg-001``,
``msg-002``, ...): no clock, no UUID, no randomness, no host state.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .base import BaseTool, ToolContext, ToolResult

NAME = "mock_email"

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "to": {"type": "string", "minLength": 1},
        "subject": {"type": "string", "minLength": 1},
        "body": {"type": "string", "minLength": 1, "maxLength": 4096},
    },
    "required": ["to", "subject", "body"],
    "additionalProperties": False,
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sent": {"type": "boolean"},
        "recipient": {"type": "string"},
        "message_id": {"type": "string"},
    },
    "required": ["sent", "recipient", "message_id"],
    "additionalProperties": False,
}


class MockEmailTool(BaseTool):
    """Deterministic, per-instance, in-memory synthetic email sink."""

    name = NAME
    description = "Send a synthetic in-memory email (no network, no persistence)."
    INPUT_SCHEMA = INPUT_SCHEMA
    OUTPUT_SCHEMA = OUTPUT_SCHEMA

    def __init__(self) -> None:
        self._outbox: list[dict[str, Any]] = []
        self._sent = 0

    def snapshot(self) -> list[dict[str, Any]]:
        """A deep copy of every sent message (for inspection/tests)."""
        return copy.deepcopy(self._outbox)

    # -- authorization metadata ------------------------------------------------
    def action(self, args: Mapping[str, Any]) -> str:  # noqa: ARG002 - fixed action
        return "send"

    def resource(self, args: Mapping[str, Any]) -> str | None:
        recipient = args.get("to")
        return None if recipient is None else str(recipient)

    # -- execution -------------------------------------------------------------
    def run(self, args: dict[str, Any], ctx: ToolContext) -> ToolResult:  # noqa: ARG002
        self._sent += 1
        message_id = f"msg-{self._sent:03d}"
        to = args["to"]
        self._outbox.append(
            {
                "to": to,
                "subject": args["subject"],
                "body": args["body"],
                "message_id": message_id,
            }
        )
        return ToolResult.success(
            {"sent": True, "recipient": to, "message_id": message_id},
            side_effects=[f"sent 1 message to {to}"],
        )
