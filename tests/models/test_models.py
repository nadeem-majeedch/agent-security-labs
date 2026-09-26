"""Unit tests for the core model data types and adapter metadata."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agentsec.models.base import Capabilities, ModelInfo
from agentsec.models.schema import Message, ModelResponse, Role, ToolCall, ToolSpec, Usage


def test_message_defaults_and_enum():
    message = Message(role=Role.USER, content="hello")
    assert message.role is Role.USER
    assert message.content == "hello"
    assert message.name is None
    assert message.tool_call_id is None


def test_message_accepts_role_string():
    assert Message(role="system", content="x").role is Role.SYSTEM


def test_message_rejects_unknown_field():
    with pytest.raises(ValidationError):
        Message(role=Role.USER, content="x", extra="nope")


def test_message_rejects_unknown_role():
    with pytest.raises(ValidationError):
        Message(role="wizard", content="x")


def test_tool_spec_defaults():
    spec = ToolSpec(name="calculator")
    assert spec.description == ""
    assert spec.parameters == {}


def test_tool_spec_requires_non_empty_name():
    with pytest.raises(ValidationError):
        ToolSpec(name="")


def test_tool_call_requires_id_and_name():
    call = ToolCall(id="call-0", name="calculator", arguments={"expr": "1+1"})
    assert call.arguments == {"expr": "1+1"}
    with pytest.raises(ValidationError):
        ToolCall(id="", name="calculator")
    with pytest.raises(ValidationError):
        ToolCall(id="call-0", name="")


def test_usage_rejects_negative_counts():
    with pytest.raises(ValidationError):
        Usage(prompt_tokens=-1, completion_tokens=0, total_tokens=0)


def test_model_response_defaults():
    response = ModelResponse()
    assert response.text == ""
    assert response.tool_calls == []
    assert response.usage is None
    assert response.latency_ms is None
    assert response.finish_reason is None


def test_model_response_round_trips_json():
    response = ModelResponse(
        text="ok",
        tool_calls=[ToolCall(id="call-0", name="t", arguments={"a": 1})],
        usage=Usage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        finish_reason="stop",
    )
    restored = ModelResponse.model_validate_json(response.model_dump_json())
    assert restored == response


def test_capabilities_is_frozen():
    caps = Capabilities(supports_temperature=False, supports_seed=False, supports_tools=True)
    assert caps.supports_forced_thinking is None
    with pytest.raises(ValidationError):
        caps.supports_tools = False  # type: ignore[misc]


def test_model_info_defaults_revision_unpinned():
    info = ModelInfo(provider="mock", model_id="mock-v1")
    assert info.revision == "unpinned"
    assert info.notes is None
