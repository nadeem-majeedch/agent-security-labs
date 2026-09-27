"""Tests for the isolated, in-memory virtual filesystem."""

from __future__ import annotations

import pytest

from agentsec.errors import ToolExecutionError, ToolValidationError
from agentsec.tools.base import ToolContext, ToolStatus
from agentsec.tools.fs_sandbox import FsSandboxTool, normalize_path

CTX = ToolContext(agent_id="agent-1")


def tool(**initial):
    return FsSandboxTool(initial or None)


def test_write_then_read_round_trip():
    fs = tool()
    written = fs.run({"op": "write", "path": "workspace/notes/note.txt", "content": "hi"}, CTX)
    assert written.status is ToolStatus.OK
    assert written.output == {"path": "workspace/notes/note.txt", "size": 2}

    read = fs.run({"op": "read", "path": "workspace/notes/note.txt"}, CTX)
    assert read.output == {"content": "hi"}


def test_list_returns_sorted_entries():
    fs = tool()
    fs.run({"op": "write", "path": "workspace/b.txt", "content": "b"}, CTX)
    fs.run({"op": "write", "path": "workspace/a.txt", "content": "a"}, CTX)
    result = fs.run({"op": "list", "path": "workspace"}, CTX)
    assert result.output == {"entries": ["workspace/a.txt", "workspace/b.txt"]}


def test_list_root_returns_everything():
    fs = FsSandboxTool({"workspace/a.txt": "a", "other/b.txt": "b"})
    result = fs.run({"op": "list", "path": "."}, CTX)
    assert result.output["entries"] == ["other/b.txt", "workspace/a.txt"]


def test_read_missing_file_is_execution_error():
    with pytest.raises(ToolExecutionError):
        tool().run({"op": "read", "path": "workspace/missing.txt"}, CTX)


@pytest.mark.parametrize(
    "path",
    [
        "../exfil.txt",
        "../../etc/passwd",
        "workspace/../../etc/passwd",
        "..",
        "a/../../b",
        "..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32",
        "c:/temp/x",
        "\\\\server\\share\\x",
        "//server/share",
        "\x00bad",
        "CON",
        "workspace/nul",
    ],
)
def test_path_traversal_and_absolute_paths_are_rejected(path):
    with pytest.raises(ToolValidationError):
        normalize_path(path)


def test_traversal_rejected_through_run():
    with pytest.raises(ToolValidationError):
        tool().run({"op": "write", "path": "../exfil.txt", "content": "leaked"}, CTX)


def test_normalization_collapses_dots_and_separators():
    assert normalize_path("a/./b//c") == "a/b/c"
    assert normalize_path("a\\b\\c") == "a/b/c"
    assert normalize_path("workspace/notes/") == "workspace/notes"


def test_oversized_write_is_rejected_at_runtime():
    fs = tool()
    with pytest.raises(ToolValidationError):
        fs.run({"op": "write", "path": "workspace/big.txt", "content": "x" * 70_000}, CTX)


def test_oversized_content_is_rejected_by_schema():
    schema = tool().schema()
    with pytest.raises(ToolValidationError):
        schema.validate_args({"op": "write", "path": "a", "content": "x" * 70_000})


def test_instances_are_isolated():
    a = tool()
    b = tool()
    a.run({"op": "write", "path": "workspace/a.txt", "content": "a"}, CTX)
    assert "workspace/a.txt" in a.files
    assert "workspace/a.txt" not in b.files


def test_nothing_is_written_to_the_host_filesystem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tool().run({"op": "write", "path": "workspace/x.txt", "content": "x"}, CTX)
    assert not (tmp_path / "workspace").exists()
    assert list(tmp_path.iterdir()) == []


def test_initial_files_are_seeded_and_normalized():
    fs = FsSandboxTool({"workspace/./note.txt": "hello"})
    assert fs.files == {"workspace/note.txt": "hello"}


def test_invalid_initial_path_is_rejected():
    with pytest.raises(ToolValidationError):
        FsSandboxTool({"../escape.txt": "x"})


def test_action_and_resource_metadata_use_raw_path():
    fs = tool()
    assert fs.action({"op": "read", "path": "workspace/x"}) == "read"
    assert fs.action({"op": "write", "path": "workspace/x", "content": ""}) == "write"
    assert fs.resource({"op": "read", "path": "../x"}) == "../x"


def test_output_schema_validates_write_and_list():
    fs = tool()
    schema = fs.schema()
    assert schema.validate_output({"path": "workspace/x", "size": 1})
    assert schema.validate_output({"entries": ["workspace/x"]})
    with pytest.raises(ToolValidationError):
        schema.validate_output({"unexpected": 1})


def test_schema_requires_content_for_write():
    schema = tool().schema()
    with pytest.raises(ToolValidationError):
        schema.validate_args({"op": "write", "path": "workspace/x"})
    assert schema.validate_args({"op": "write", "path": "workspace/x", "content": ""})


def test_side_effects_recorded_on_write():
    result = tool().run({"op": "write", "path": "workspace/x", "content": "y"}, CTX)
    assert result.side_effects == ["wrote workspace/x"]
