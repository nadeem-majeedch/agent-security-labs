"""Export the versioned trace JSON Schema from the pydantic models.

Run this whenever ``src/agentsec/trace/schema.py`` changes, then commit the
regenerated file:

    py scripts/export_trace_schema.py

``tests/schema/test_schema_file.py`` fails if the checked-in file and the
models ever disagree, so drift cannot go unnoticed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentsec.trace.schema import trace_json_schema  # noqa: E402

OUTPUT = ROOT / "schemas" / "trace" / "trace_event.v1.schema.json"


def main() -> int:
    schema = trace_json_schema()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
