"""Export the versioned trace JSON Schema from the pydantic models.

Run this whenever ``src/agentsec/trace/schema.py`` changes, then commit the
regenerated files:

    py scripts/export_trace_schema.py

The same bytes are written to two places, and this script is their only writer:

    schemas/trace/trace_event.v1.schema.json          the repository copy
    src/agentsec/schemas/trace/trace_event.v1.schema.json   the packaged copy

The repository copy is the documentation-facing artefact (``README.md`` links
to ``schemas/trace/``). The packaged copy is package data, read at runtime
through ``importlib.resources`` by ``agentsec.trace.validate``, which is what
makes an installed ``agentsec`` self-contained.

``tests/schema/test_schema_file.py`` and ``tests/schema/test_packaged_schema.py``
fail if either copy disagrees with the models, or if the two copies differ, so
drift cannot go unnoticed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentsec.trace.schema import trace_json_schema  # noqa: E402

REPOSITORY_OUTPUT = ROOT / "schemas" / "trace" / "trace_event.v1.schema.json"
PACKAGED_OUTPUT = (
    ROOT / "src" / "agentsec" / "schemas" / "trace" / "trace_event.v1.schema.json"
)


def main() -> int:
    content = json.dumps(trace_json_schema(), indent=2, sort_keys=True) + "\n"
    for output in (REPOSITORY_OUTPUT, PACKAGED_OUTPUT):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
