"""Tests for the tool contract, schema and factory."""

from __future__ import annotations

import pytest

from agentsec.errors import ConfigError
from agentsec.tools.base import BaseTool, Tool, ToolSchema
from agentsec.tools.factory import build_tools, tool_names


def test_factory_builds_all_mvp_tools():
    tools = build_tools()
    assert sorted(tools) == ["calculator", "fs_sandbox", "mock_db", "mock_email"]
    assert set(tools) == set(tool_names())


def test_factory_builds_only_requested_tools():
    tools = build_tools(["calculator"])
    assert sorted(tools) == ["calculator"]


def test_factory_rejects_unknown_tool():
    with pytest.raises(ConfigError):
        build_tools(["nope"])


def test_factory_rejects_duplicates():
    with pytest.raises(ConfigError):
        build_tools(["calculator", "calculator"])


def test_built_tools_satisfy_the_protocol():
    for name, tool in build_tools().items():
        assert isinstance(tool, Tool)
        assert tool.name == name
        assert isinstance(tool.schema(), ToolSchema)


def test_factory_returns_fresh_instances():
    assert build_tools(["fs_sandbox"])["fs_sandbox"] is not build_tools(["fs_sandbox"])["fs_sandbox"]


def test_every_schema_is_a_valid_json_schema():
    for tool in build_tools().values():
        schema = tool.schema()
        assert schema.input_schema["type"] == "object"
        assert schema.output_schema["type"] == "object"
        assert schema.description


def test_invalid_json_schema_is_rejected():
    with pytest.raises(Exception):
        ToolSchema(name="x", input_schema={"type": "nonsense"}, output_schema={"type": "object"})


def test_schema_input_is_forbidden_extra_properties():
    for tool in build_tools().values():
        assert tool.schema().input_schema.get("additionalProperties") is False


class _EchoTool(BaseTool):
    name = "echo"
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }
    OUTPUT_SCHEMA = INPUT_SCHEMA


def test_base_tool_defaults_action_and_resource():
    tool = _EchoTool()
    assert tool.action({"value": 1}) == "invoke"
    assert tool.resource({"value": 1}) is None
