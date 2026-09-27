"""An entirely in-memory virtual filesystem (no host filesystem access).

Nothing here touches the real disk. Files live in a per-instance dictionary, so
two instances are fully isolated and nothing survives the process. This is what
makes the tool safe to run in an offline lab.

Safety properties (Phase 14, Task 7 / Phase 13, Task 12):

* paths are relative to the virtual workspace root only;
* ``..`` segments are rejected, so traversal cannot escape the root;
* absolute POSIX paths, Windows drive paths and UNC/device paths are rejected;
* null bytes and Windows reserved device names are rejected;
* there are no symlinks, so there is no symlink escape to defend against.

Note on scope: this tool enforces *containment* (a path cannot leave the
virtual workspace). Which paths *within* the workspace an agent may touch is a
**policy** question, answered by the policy engine via the ``resource``
identifier. Keeping those concerns separate is the point of the lab.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from ..errors import ToolExecutionError, ToolValidationError
from .base import BaseTool, ToolContext, ToolResult

NAME = "fs_sandbox"
MAX_CONTENT_LENGTH = 65_536
MAX_PATH_LENGTH = 512

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "op": {"enum": ["read", "write", "list"]},
        "path": {"type": "string", "minLength": 1, "maxLength": MAX_PATH_LENGTH},
        "content": {"type": "string", "maxLength": MAX_CONTENT_LENGTH},
    },
    "required": ["op", "path"],
    "additionalProperties": False,
    "allOf": [
        {
            "if": {"properties": {"op": {"const": "write"}}, "required": ["op"]},
            "then": {"required": ["content"]},
        }
    ],
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "entries": {"type": "array", "items": {"type": "string"}},
        "path": {"type": "string"},
        "size": {"type": "integer"},
    },
    "additionalProperties": False,
}

_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def _fail(message: str) -> ToolValidationError:
    return ToolValidationError(NAME, message)


def normalize_path(path: str, *, allow_root: bool = False) -> str:
    """Normalize a virtual path, rejecting anything that could escape the root.

    Returns a canonical ``a/b/c`` string with no leading slash, no ``.``
    segments and no trailing slash. ``allow_root=True`` permits ``""``/``"."``
    to normalize to ``""`` (used by ``list`` for the workspace root).
    """
    if not isinstance(path, str):
        raise _fail("path must be a string")
    if len(path) > MAX_PATH_LENGTH:
        raise _fail(f"path must be <= {MAX_PATH_LENGTH} characters")
    if "\x00" in path:
        raise _fail("path must not contain null bytes")

    candidate = path.strip()
    if allow_root and candidate in ("", ".", "./", "/"):
        return ""
    if not candidate:
        raise _fail("path must not be empty")

    # Normalize Windows separators so `..\\..\\x` is caught by the `..` check.
    candidate = candidate.replace("\\", "/")

    if candidate.startswith("/"):
        raise _fail("absolute paths are not allowed")
    if _DRIVE_RE.match(candidate):
        raise _fail("absolute drive paths are not allowed")
    if candidate.startswith("//"):
        raise _fail("UNC paths are not allowed")

    segments: list[str] = []
    for raw in candidate.split("/"):
        if raw in ("", "."):
            continue
        if raw == "..":
            raise _fail("path traversal ('..') is not allowed")
        if raw.lower() in _RESERVED_NAMES:
            raise _fail(f"reserved device name {raw!r} is not allowed")
        segments.append(raw)

    if not segments:
        if allow_root:
            return ""
        raise _fail("path must reference a file")
    return "/".join(segments)


class FsSandboxTool(BaseTool):
    """Isolated, in-memory read/write/list filesystem."""

    name = NAME
    description = "Read, write or list files in an isolated in-memory workspace."
    INPUT_SCHEMA = INPUT_SCHEMA
    OUTPUT_SCHEMA = OUTPUT_SCHEMA

    def __init__(self, initial_files: Mapping[str, str] | None = None) -> None:
        self._files: dict[str, str] = {}
        for path, content in (initial_files or {}).items():
            normalized = normalize_path(path)
            if len(content) > MAX_CONTENT_LENGTH:
                raise _fail(f"initial file {path!r} exceeds {MAX_CONTENT_LENGTH} characters")
            self._files[normalized] = content

    @property
    def files(self) -> dict[str, str]:
        """A copy of the current workspace contents (for inspection/tests)."""
        return dict(self._files)

    def action(self, args: Mapping[str, Any]) -> str:
        return str(args.get("op", "invoke"))

    def resource(self, args: Mapping[str, Any]) -> str | None:
        # The *raw* path is returned so the policy engine can judge scope; the
        # tool's own normalization/rejection happens later, at run time.
        path = args.get("path")
        return path if isinstance(path, str) else None

    def run(self, args: dict[str, Any], ctx: ToolContext) -> ToolResult:  # noqa: ARG002
        op = args["op"]
        if op == "read":
            return self._read(args["path"])
        if op == "write":
            return self._write(args["path"], args["content"])
        return self._list(args["path"])

    def _read(self, path: str) -> ToolResult:
        normalized = normalize_path(path)
        if normalized not in self._files:
            raise ToolExecutionError(NAME, f"no such file: {normalized}")
        return ToolResult.success({"content": self._files[normalized]})

    def _write(self, path: str, content: str) -> ToolResult:
        normalized = normalize_path(path)
        if not isinstance(content, str):
            raise _fail("content must be a string")
        if len(content) > MAX_CONTENT_LENGTH:
            raise _fail(f"content must be <= {MAX_CONTENT_LENGTH} characters")
        self._files[normalized] = content
        return ToolResult.success(
            {"path": normalized, "size": len(content)},
            side_effects=[f"wrote {normalized}"],
        )

    def _list(self, path: str) -> ToolResult:
        prefix = normalize_path(path, allow_root=True)
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        entries = sorted(
            key for key in self._files if key.startswith(prefix) or key == prefix.rstrip("/")
        )
        return ToolResult.success({"entries": entries})
