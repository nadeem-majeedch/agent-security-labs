"""Default, best-effort redaction for trace payloads.

This is deliberately simple and pattern-based. It is **not** a DLP system and
makes no claim to catch every secret; it exists so that the lab's default
behaviour never persists obvious credentials.

Policy (Phase 14, Task 11):

* redact by default, raw values are never persisted by default;
* secrets become ``[REDACTED:<kind>]``; content-bearing values can be hashed;
* redaction is deterministic and idempotent.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

_MARKER_RE = re.compile(r"^\[REDACTED:[a-z_]+\]$")

#: Named regex patterns applied to string values.
DEFAULT_PATTERNS: dict[str, str] = {
    "openai_key": r"\bsk-[A-Za-z0-9_\-]{16,}\b",
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    "bearer": r"(?i)\bBearer\s+[A-Za-z0-9._\-]{10,}",
    "lab_fake_secret": r"\bFAKE_SECRET_[A-Za-z0-9]+\b",
    "assigned_secret": r"(?i)\b(?:secret|token|password|passwd|api[_-]?key)\s*[:=]\s*[^\s,;'\"]{6,}",
}

#: Mapping keys whose values are replaced wholesale.
DEFAULT_KEY_NAMES: dict[str, str] = {
    "api_key": "api_key",
    "apikey": "api_key",
    "authorization": "authorization",
    "bearer": "authorization",
    "cookie": "cookie",
    "set-cookie": "cookie",
    "password": "password",
    "passwd": "password",
    "secret": "secret",
    "client_secret": "secret",
    "private_key": "secret",
    "token": "token",
    "access_token": "token",
    "refresh_token": "token",
}


class Redactor:
    """Deterministic, idempotent redaction of text, values and mappings."""

    def __init__(
        self,
        extra_patterns: Mapping[str, str] | None = None,
        extra_key_names: Mapping[str, str] | None = None,
    ) -> None:
        patterns = dict(DEFAULT_PATTERNS)
        if extra_patterns:
            patterns.update(extra_patterns)
        self._compiled = {
            kind: re.compile(pattern) for kind, pattern in patterns.items()
        }
        key_names = dict(DEFAULT_KEY_NAMES)
        if extra_key_names:
            key_names.update(extra_key_names)
        self._key_names = {k.lower(): v for k, v in key_names.items()}

    @staticmethod
    def is_marker(value: str) -> bool:
        """True when ``value`` is already a redaction marker."""
        return bool(_MARKER_RE.match(value.strip()))

    def redact_text(self, text: str) -> str:
        """Replace known secret patterns inside ``text``.

        Values that are already markers are returned unchanged, and repeated
        application produces the same result (idempotent).
        """
        if self.is_marker(text):
            return text
        result = text
        for kind, pattern in self._compiled.items():
            result = pattern.sub(f"[REDACTED:{kind}]", result)
        return result

    def _marker_for_key(self, key: str) -> str:
        return f"[REDACTED:{self._key_names[key.lower()]}]"

    def redact_value(self, value: Any) -> Any:
        """Recursively redact strings, mappings and sequences."""
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, Mapping):
            return self.redact_mapping(value)
        if isinstance(value, (list, tuple)):
            return [self.redact_value(item) for item in value]
        return value

    def redact_mapping(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Redact a mapping, replacing sensitive-keyed values entirely."""
        out: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(key, str) and key.lower() in self._key_names:
                out[key] = self._marker_for_key(key)
            else:
                out[key] = self.redact_value(value)
        return out

    @staticmethod
    def hash_value(value: Any) -> str:
        """Return a stable ``sha256`` digest for any JSON-serializable value."""
        canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


#: Shared default instance; stateless, so reuse is safe.
DEFAULT_REDACTOR = Redactor()


def redact_value(value: Any) -> Any:
    """Convenience wrapper around :data:`DEFAULT_REDACTOR`."""
    return DEFAULT_REDACTOR.redact_value(value)


def hash_value(value: Any) -> str:
    """Convenience wrapper around :meth:`Redactor.hash_value`."""
    return DEFAULT_REDACTOR.hash_value(value)
