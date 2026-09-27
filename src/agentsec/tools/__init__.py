"""Tool package: contract, sandbox tools, factory and the mediated gateway.

Concrete tools are constructible only through :func:`factory.build_tools`, and
the supported way to execute one is :class:`gateway.ToolGateway`.
"""

from .base import (
    BaseTool,
    DeniedResult,
    PendingApprovalResult,
    Tool,
    ToolContext,
    ToolResult,
    ToolSchema,
    ToolStatus,
)
from .calculator import CalculatorTool, evaluate
from .factory import build_gateway, build_tools, tool_names
from .fs_sandbox import FsSandboxTool, normalize_path
from .gateway import ToolGateway
from .mock_db import MockDatabaseTool

__all__ = [
    "BaseTool",
    "DeniedResult",
    "PendingApprovalResult",
    "Tool",
    "ToolContext",
    "ToolResult",
    "ToolSchema",
    "ToolStatus",
    "CalculatorTool",
    "evaluate",
    "FsSandboxTool",
    "normalize_path",
    "MockDatabaseTool",
    "ToolGateway",
    "build_tools",
    "build_gateway",
    "tool_names",
]
