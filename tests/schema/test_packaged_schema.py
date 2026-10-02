"""The trace schema ships inside the package, so an installed agentsec works.

Regression tests for the self-containment defect: schema lookup used to walk
parent directories from ``validate.py`` looking for ``schemas/trace/...``, which
raised ``FileNotFoundError`` the moment the package was imported outside the
repository. The schema is now package data, read through
``importlib.resources``, and these tests pin all four properties that matter:

* it is a discoverable package resource (A);
* its contents match the repository copy and the pydantic models (B);
* validation works from a copy of the package with no repository in reach (C);
* the lookup does not walk parent directories (D).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib import resources
from pathlib import Path

from agentsec.trace.schema import trace_json_schema
from agentsec.trace.validate import (
    SCHEMA_PACKAGE,
    SCHEMA_RESOURCE,
    load_schema,
    schema_path,
    schema_resource,
    schema_text,
)

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_SCHEMA = ROOT / "schemas" / "trace" / "trace_event.v1.schema.json"
PACKAGED_SCHEMA = (
    ROOT / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json"
)
SOURCE_PACKAGE = ROOT / "src" / "agentsec"
VALIDATE_MODULE = SOURCE_PACKAGE / "trace" / "validate.py"

#: Run in a child interpreter against an isolated copy of the package. It
#: reports where the package came from, where the schema came from and what the
#: schema contains, then exercises the validator.
_CHILD_PROGRAM = """
import hashlib
import agentsec
from agentsec.errors import TraceSchemaError
from agentsec.trace.validate import load_schema, schema_path, schema_text, validate_event

schema = load_schema()
print("package_file=" + agentsec.__file__)
print("schema_path=" + str(schema_path()))
print("schema_digest=" + hashlib.md5(schema_text().encode("utf-8")).hexdigest())
print("variants=" + str(len(schema["oneOf"])))
try:
    validate_event({"event_type": "definitely-not-an-event"})
except TraceSchemaError:
    print("rejects_invalid=ok")
print("finished=ok")
"""


# --- A. the schema is a discoverable package resource -----------------------


def test_packaged_schema_is_a_discoverable_package_resource():
    assert schema_resource().is_file()
    assert resources.files(SCHEMA_PACKAGE).joinpath(SCHEMA_RESOURCE).is_file()
    assert PACKAGED_SCHEMA.is_file()
    assert schema_path().is_file()
    assert schema_text().startswith("{")


def test_validator_loads_the_packaged_schema():
    schema = load_schema()
    assert schema == json.loads(schema_text())
    assert schema["oneOf"], "schema should describe the event union"


def test_schema_path_is_inside_the_installed_package():
    package_root = PACKAGED_SCHEMA.parents[2]
    assert package_root in schema_path().resolve().parents


# --- B. contents match the repository copy and the models -------------------


def test_packaged_schema_is_byte_identical_to_the_repository_copy():
    assert PACKAGED_SCHEMA.read_bytes() == REPOSITORY_SCHEMA.read_bytes(), (
        "the packaged schema and schemas/trace/trace_event.v1.schema.json have "
        "diverged; both are written by `py scripts/export_trace_schema.py`"
    )


def test_packaged_schema_matches_the_models():
    assert json.loads(schema_text()) == trace_json_schema()


# --- C. validation works with no repository schemas/ directory in reach -----


def test_validation_works_from_a_copy_of_the_package_outside_the_repository(tmp_path):
    """The decisive self-containment test.

    The package is copied to a temporary directory that has no ``schemas/``
    directory and no repository above it, and a child interpreter runs with
    that copy as the only import location for ``agentsec``. The child reports
    which package and schema it used, so a pass cannot come from the repository
    checkout or from an installed distribution.
    """
    isolated = tmp_path / "isolated"
    package_copy = isolated / "agentsec"
    shutil.copytree(
        SOURCE_PACKAGE, package_copy, ignore=shutil.ignore_patterns("__pycache__")
    )
    assert not (tmp_path / "schemas").exists(), "the copy must not have a schemas/ directory"

    env = dict(os.environ, PYTHONPATH=str(isolated))
    result = subprocess.run(
        [sys.executable, "-c", _CHILD_PROGRAM],
        cwd=str(isolated),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    reported = dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
    assert reported["finished"] == "ok"

    # The child used the isolated copy, not the repository or site-packages.
    assert Path(reported["package_file"]).resolve().parent == package_copy.resolve()

    # The schema came from the isolated copy, and not from any repository.
    schema_used = Path(reported["schema_path"]).resolve()
    assert package_copy.resolve() in schema_used.parents
    assert ROOT.resolve() not in schema_used.parents

    # It is the same schema as the repository copy, and it validated events.
    assert reported["schema_digest"] == _packaged_schema_digest()
    assert int(reported["variants"]) > 0
    assert reported["rejects_invalid"] == "ok"


def _packaged_schema_digest() -> str:
    import hashlib

    return hashlib.md5(schema_text().encode("utf-8")).hexdigest()


# --- D. the lookup does not walk parent directories -------------------------


def test_schema_lookup_does_not_walk_parent_directories():
    source = VALIDATE_MODULE.read_text(encoding="utf-8")
    assert "parents" not in source, (
        "validate.py must not search parent directories for the schema; the "
        "schema is package data read through importlib.resources"
    )
    assert "resources.files(" in source, (
        "validate.py is expected to resolve the schema as a package resource"
    )
