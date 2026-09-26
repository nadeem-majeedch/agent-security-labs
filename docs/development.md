# AgentSec Lab - development notes (Phase A, step 1)

Educational, reproducible agent-security infrastructure. This step implements
**only** the skeleton, core data models, the trace schema, redaction and a
deterministic mock model. There are deliberately no model adapters, tools,
policy engine, agent loop, evaluator, experiment runner or CLI yet.

The package makes **no research-novelty claim** anywhere; it reimplements
established concepts for teaching and reproducible experimentation.

## Install (development)

```bash
py -m pip install -e ".[dev]"
```

Requires Python 3.11+. Core runtime dependencies are `pydantic` and
`jsonschema` only. `PyYAML` and `httpx` are declared as optional extras and
will be required by later steps (config/policy/scenario loading and live
provider adapters). Nothing in the current code needs them.

## Run the tests

```bash
py -m pytest
```

The entire suite runs **offline**: no network, no API keys, no external model
providers, no database, no Docker, no GPU. Everything is driven by the
deterministic mock model.

## What is implemented

```
src/agentsec/
├── errors.py            # typed exceptions actually used today
├── models/
│   ├── schema.py        # Message, ToolSpec, ToolCall, Usage, ModelResponse
│   ├── base.py          # ModelAdapter protocol, Capabilities, ModelInfo
│   └── mock.py          # deterministic MockModel + MVP fixture scripts
└── trace/
    ├── schema.py        # versioned TraceEvent union (12 event types)
    ├── redact.py        # Redactor: deterministic, idempotent redaction
    ├── validate.py      # jsonschema + semantic (seq/parent) validation
    └── writer.py        # append-only JSONL I/O
schemas/trace/trace_event.v1.schema.json   # versioned trace contract
```

## Trace schema

Every JSONL line is one event. All events carry `schema_version`, `run_id`,
`event_id`, `parent_event_id`, `seq`, `timestamp` (UTC), `agent_id`, `model`,
`scenario` and `event_type`; each type adds its own fields. The union is
discriminated on `event_type`, so unknown types and missing per-type fields are
rejected by both pydantic and the JSON Schema.

The checked-in schema is generated from the pydantic models:

```bash
py scripts/export_trace_schema.py
```

`tests/schema/test_schema_file.py` fails if the file and the models diverge.

## Deterministic mock

`agentsec.models.mock.MockModel` is a **test fixture, not an LLM simulation**.
Its response is a pure function of the message list and a `MockScript`, so
identical inputs yield byte-identical outputs. It consults no clock and no RNG
(`latency_ms` is always `None`). It reports `supports_temperature=False` and
`supports_seed=False`, and raises `UnsupportedParameter` if a caller passes
either, so it can never be mistaken for a controllable model.

Fixture scripts cover the five MVP security modules plus a benign baseline:
`benign`, `direct_injection`, `indirect_injection`, `tool_misuse`,
`excessive_agency`, `authorization_violation` (see `script_for`).

## Redaction

`agentsec.trace.redact.Redactor` redacts known secret patterns and sensitive
mapping keys to `[REDACTED:<kind>]`. It is deterministic and idempotent, and can
hash content-bearing values (`hash_value`). Redaction happens before writing,
so no write path bypasses it. This is best-effort and **not** a DLP system.

## Note on the repository README

The repository root `README.md` belongs to the surrounding research project and
is intentionally left untouched. The student-facing lab README and the MkDocs
site are later steps (see `research/14-implementation-blueprint.md`).
