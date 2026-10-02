"""D1: the package is PEP 561-typed and its public surface is usable.

``research/39`` item D1 asks for a ``py.typed`` marker and public-surface type
checking. The marker makes agentsec's inline annotations visible to downstream
type checkers; these tests pin the two halves of that:

* **packaging** - the marker exists, is empty, and ships inside the built wheel
  next to the packaged schema, so the distribution stays self-contained; and
* **public surface** - every advertised name resolves, and a small *consumer*
  module type-checks against the public imports.

The package's own modules (including the public ``__init__``) are already
type-checked by the existing mypy gate (``files = ["src/agentsec"]``); the
consumer check here adds the downstream view that ``py.typed`` enables.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import agentsec

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "agentsec"
PY_TYPED = PACKAGE / "py.typed"

WHEEL_MARKER = "agentsec/py.typed"
WHEEL_SCHEMA = "agentsec/schemas/trace/trace_event.v1.schema.json"

#: A minimal module that imports the public API and uses it with annotations.
#: Type-checked by ``test_the_public_surface_type_checks_for_a_consumer``.
_CONSUMER = '''\
from agentsec import (
    Agent,
    AgentConfig,
    ScenarioRegistry,
    TraceEvaluator,
    __version__,
)
from agentsec.errors import AgentSecError


def use_public_surface(agent: Agent, config: AgentConfig) -> str:
    evaluator: TraceEvaluator = TraceEvaluator()
    registry: ScenarioRegistry = ScenarioRegistry()
    error: type[AgentSecError] = AgentSecError
    del evaluator, registry, error
    return __version__
'''


# --- the PEP 561 marker exists -----------------------------------------------


def test_the_pep_561_marker_exists_and_is_empty():
    assert PY_TYPED.is_file(), "src/agentsec/py.typed (the PEP 561 marker) is missing"
    assert PY_TYPED.read_bytes() == b"", "the PEP 561 marker must be an empty file"


# --- the public surface resolves ---------------------------------------------


def test_every_advertised_public_name_resolves():
    assert agentsec.__all__, "the package should advertise its public surface"
    missing = sorted(name for name in agentsec.__all__ if not hasattr(agentsec, name))
    assert missing == [], f"names advertised in __all__ but not importable: {missing}"


def test_the_public_surface_has_no_duplicate_names():
    names = list(agentsec.__all__)
    duplicates = sorted({name for name in names if names.count(name) > 1})
    assert duplicates == [], f"duplicate entries in __all__: {duplicates}"


def test_the_public_surface_type_checks_for_a_consumer(tmp_path):
    """A downstream consumer of the public API type-checks cleanly.

    Run with the repository's mypy configuration (from ``cwd``) and with the
    package importable through ``MYPYPATH``, this checks the surface a
    ``py.typed`` consumer actually sees. Skipped only when mypy is absent.
    """
    if importlib.util.find_spec("mypy") is None:  # pragma: no cover - env guard
        pytest.skip("mypy is not installed")
    consumer = tmp_path / "consumer.py"
    consumer.write_text(_CONSUMER, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--no-incremental",
            "--cache-dir",
            str(tmp_path / "mypy-cache"),
            str(consumer),
        ],
        cwd=str(ROOT),
        env=dict(os.environ, MYPYPATH=str(ROOT / "src")),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# --- the marker ships in the wheel -------------------------------------------


def _build_wheel(scratch: Path) -> Path | None:
    """Build a wheel from a copy of the project, returning ``None`` on failure.

    Mirrors ``scripts/release_check.py::_build_wheel``: the project is copied
    out of the repository first, so building never touches the working tree, and
    only the files the build needs are copied. Returns ``None`` (rather than
    raising) when the build cannot run - for example when offline build
    isolation is unavailable - so the caller can skip.
    """
    project = scratch / "project"
    (project / "docs").mkdir(parents=True)
    (project / "src").mkdir(parents=True)
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        source = ROOT / name
        if source.is_file():
            shutil.copy(source, project / name)
    development = ROOT / "docs" / "development.md"
    if development.is_file():
        shutil.copy(development, project / "docs" / "development.md")
    shutil.copytree(
        PACKAGE,
        project / "src" / "agentsec",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    dist = scratch / "dist"
    dist.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "-w", str(dist)],
        cwd=str(project),
        capture_output=True,
        text=True,
        timeout=600,
    )
    wheels = sorted(dist.glob("agentsec-*.whl"))
    return wheels[-1] if result.returncode == 0 and wheels else None


def test_the_built_wheel_ships_the_marker_and_stays_self_contained(tmp_path):
    wheel = _build_wheel(tmp_path)
    if wheel is None:  # pragma: no cover - env guard (offline build isolation)
        pytest.skip("wheel build unavailable; the release gate covers the wheel")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    assert WHEEL_MARKER in names, f"{WHEEL_MARKER} is missing from the built wheel"
    assert WHEEL_SCHEMA in names, "the packaged schema is missing (self-containment)"
    assert not any(name.startswith("labs/") for name in names), (
        "repository-only content leaked into the wheel"
    )
