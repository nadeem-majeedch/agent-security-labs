"""Tests for the in-memory, synthetic mock database."""

from __future__ import annotations

import pytest

from agentsec.errors import ToolExecutionError, ToolValidationError
from agentsec.tools.base import ToolContext, ToolStatus
from agentsec.tools.mock_db import MockDatabaseTool

CTX = ToolContext(agent_id="agent-1")


def rw() -> MockDatabaseTool:
    return MockDatabaseTool(read_only=False)


def run(tool, query, params=None):
    args = {"query": query}
    if params is not None:
        args["params"] = params
    return tool.run(args, CTX)


def test_select_all_rows():
    result = run(MockDatabaseTool(), "SELECT * FROM users")
    assert result.status is ToolStatus.OK
    assert result.output["count"] == 2
    assert {row["name"] for row in result.output["rows"]} == {"alice", "bob"}


def test_select_specific_columns():
    result = run(MockDatabaseTool(), "SELECT name FROM users")
    assert result.output["rows"] == [{"name": "alice"}, {"name": "bob"}]


def test_select_with_where():
    result = run(MockDatabaseTool(), "SELECT id FROM users WHERE name = 'bob'")
    assert result.output == {"rows": [{"id": 2}], "count": 1}


def test_select_with_params():
    result = run(MockDatabaseTool(), "SELECT id FROM users WHERE name = ?", ["alice"])
    assert result.output == {"rows": [{"id": 1}], "count": 1}


def test_missing_parameter_is_rejected():
    with pytest.raises(ToolValidationError):
        run(MockDatabaseTool(), "SELECT id FROM users WHERE name = ?")


def test_unknown_table_is_execution_error():
    with pytest.raises(ToolExecutionError):
        run(MockDatabaseTool(), "SELECT * FROM does_not_exist")


def test_unknown_column_is_rejected():
    with pytest.raises(ToolValidationError):
        run(MockDatabaseTool(), "SELECT nope FROM users")


def test_unsupported_statement_is_rejected():
    with pytest.raises(ToolValidationError):
        run(MockDatabaseTool(), "DROP TABLE users")


def test_read_only_by_default_refuses_writes():
    db = MockDatabaseTool()
    assert db.read_only is True
    with pytest.raises(ToolExecutionError):
        run(db, "DELETE FROM audit_log")
    assert len(db.snapshot()["audit_log"]) == 2


def test_delete_works_when_writable():
    db = rw()
    result = run(db, "DELETE FROM audit_log WHERE event = 'login'")
    assert result.output == {"rows": [], "count": 1}
    assert result.side_effects == ["deleted 1 row(s) from audit_log"]
    assert db.snapshot()["audit_log"] == [{"id": 2, "event": "logout"}]


def test_insert_works_when_writable():
    db = rw()
    result = run(db, "INSERT INTO users (id, name) VALUES (3, 'carol')")
    assert result.output["count"] == 1
    assert {"id": 3, "name": "carol"} in db.snapshot()["users"]


def test_update_works_when_writable():
    db = rw()
    result = run(db, "UPDATE users SET role = 'admin' WHERE name = 'alice'")
    assert result.output["count"] == 1
    assert db.snapshot()["users"][0]["role"] == "admin"


def test_instances_are_isolated():
    a = rw()
    b = rw()
    run(a, "DELETE FROM users")
    assert a.snapshot()["users"] == []
    assert b.snapshot()["users"] != []


def test_default_seed_is_synthetic_only():
    db = MockDatabaseTool()
    rows = db.snapshot()
    assert set(rows) == {"users", "notes", "audit_log", "credentials"}
    # a planted fake secret for leakage labs; not a real credential
    assert rows["credentials"][0]["value"].startswith("FAKE_SECRET_")


def test_snapshot_is_a_copy():
    db = MockDatabaseTool()
    snapshot = db.snapshot()
    snapshot["users"].clear()
    assert len(db.snapshot()["users"]) == 2


def test_deterministic_across_instances():
    assert run(MockDatabaseTool(), "SELECT * FROM users").output == run(
        MockDatabaseTool(), "SELECT * FROM users"
    ).output


def test_action_and_resource_metadata():
    db = MockDatabaseTool()
    assert db.action({"query": "SELECT * FROM users"}) == "read"
    assert db.action({"query": "DELETE FROM audit_log"}) == "write"
    assert db.action({"query": "PRAGMA foo"}) == "invoke"
    assert db.resource({"query": "SELECT * FROM users"}) == "users"
    assert db.resource({"query": "DELETE FROM audit_log"}) == "audit_log"


def test_output_schema_validation():
    schema = MockDatabaseTool().schema()
    assert schema.validate_output({"rows": [], "count": 0})
    with pytest.raises(ToolValidationError):
        schema.validate_output({"rows": []})
