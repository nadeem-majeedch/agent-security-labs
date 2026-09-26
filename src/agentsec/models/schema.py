"""Shared, provider-independent message and response data types.

These types are the only vocabulary the rest of the lab uses to talk to a
model. Concrete providers must map onto them; nothing here knows about HTTP,
providers, tools, policy or traces.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    """Chat message role."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A single chat message."""

    model_config = ConfigDict(extra="forbid")

    role: Role
    content: str = ""
    name: str | None = None
    tool_call_id: str | None = None


class ToolSpec(BaseModel):
    """A tool declaration advertised to the model.

    ``parameters`` holds a JSON Schema object describing the tool arguments.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """A model's request to invoke a tool."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class Usage(BaseModel):
    """Token accounting for a single model call, when the provider reports it."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class ModelResponse(BaseModel):
    """A normalized model response.

    ``latency_ms`` is ``None`` when no wall clock was consulted (for example a
    deterministic fixture), which keeps those responses reproducible.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: Usage | None = None
    latency_ms: float | None = None
    finish_reason: str | None = None
