"""Construction of concrete tools from configuration.

Tools are built **only** here. The rest of the lab (and, later, the agent loop)
receives a :class:`~agentsec.tools.gateway.ToolGateway`, never tool objects, so
there is no supported path that executes a tool without a policy decision.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from ..errors import ConfigError
from ..policy.base import PolicyEngine
from ..trace.recorder import TraceRecorder
from .base import Tool
from .calculator import CalculatorTool
from .fs_sandbox import FsSandboxTool
from .gateway import Approver, ToolGateway
from .mock_db import MockDatabaseTool

#: The tools available in the MVP, by name.
TOOL_FACTORIES: dict[str, type[Tool]] = {
    CalculatorTool.name: CalculatorTool,
    FsSandboxTool.name: FsSandboxTool,
    MockDatabaseTool.name: MockDatabaseTool,
}


def tool_names() -> list[str]:
    """Return the names of every buildable tool, sorted."""
    return sorted(TOOL_FACTORIES)


def build_tools(
    names: Iterable[str] | None = None,
    *,
    sandbox_files: Mapping[str, str] | None = None,
) -> dict[str, Tool]:
    """Build a fresh ``{name: Tool}`` mapping.

    ``names=None`` builds every MVP tool. Requesting an unknown tool raises
    :class:`ConfigError` rather than silently skipping it. ``sandbox_files``
    optionally seeds the in-memory ``fs_sandbox`` workspace with synthetic
    content (still memory-only); it requires that tool to be selected.
    """
    selected = tool_names() if names is None else list(names)
    tools: dict[str, Tool] = {}
    for name in selected:
        factory = TOOL_FACTORIES.get(name)
        if factory is None:
            known = ", ".join(tool_names())
            raise ConfigError(f"unknown tool {name!r}; known tools: {known}")
        if name in tools:
            raise ConfigError(f"duplicate tool {name!r}")
        tools[name] = factory()
    if sandbox_files:
        if FsSandboxTool.name not in tools:
            raise ConfigError("sandbox_files requires the fs_sandbox tool")
        tools[FsSandboxTool.name] = FsSandboxTool(sandbox_files)
    return tools


def build_gateway(
    policy: PolicyEngine,
    *,
    tools: dict[str, Tool] | None = None,
    names: Iterable[str] | None = None,
    recorder: TraceRecorder | None = None,
    approver: Approver | None = None,
    raise_on_denied: bool = False,
    sandbox_files: Mapping[str, str] | None = None,
) -> ToolGateway:
    """Wire tools, policy and (optionally) a recorder into a gateway.

    This is the only supported way to obtain a gateway, and a gateway is the
    only supported way to execute a tool. ``sandbox_files`` seeds the in-memory
    ``fs_sandbox`` workspace when the gateway builds its own tools.
    """
    if tools is not None and names is not None:
        raise ConfigError("pass either 'tools' or 'names', not both")
    if tools is not None and sandbox_files:
        raise ConfigError("pass either 'tools' or 'sandbox_files', not both")
    built = tools if tools is not None else build_tools(names, sandbox_files=sandbox_files)
    return ToolGateway(
        built,
        policy,
        recorder,
        approver=approver,
        raise_on_denied=raise_on_denied,
    )
