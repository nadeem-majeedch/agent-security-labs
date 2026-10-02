"""Generate the student-facing trace field reference from the canonical schema.

Run this whenever ``src/agentsec/trace/schema.py`` changes, then commit the
regenerated page:

    py scripts/export_trace_reference.py

The **canonical source is the trace schema**. This script derives the page from
the same ``trace_json_schema()`` output that ``scripts/export_trace_schema.py``
writes, so the reference cannot describe a field, type, required flag or allowed
value that the schema does not contain.

What the schema *cannot* provide is a field's **meaning** - the pydantic models
carry no per-field descriptions, so the schema only has machine titles. Those
one-line meanings are curated in ``FIELD_MEANINGS`` / ``EVENT_MEANINGS`` below;
the generator **fails** if the schema has a field or event with no meaning, so a
new field forces a deliberate documentation update rather than silent drift.

``tests/schema/test_trace_reference.py`` fails if the committed page disagrees
with fresh output from this module.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentsec.trace.schema import TRACE_EVENT_TYPES, trace_json_schema  # noqa: E402

OUTPUT = ROOT / "labs" / "TRACE-FIELD-REFERENCE.md"

#: One-line purpose of each event type (the schema has no such text).
EVENT_MEANINGS: dict[str, str] = {
    "run_started": "The run began; records the configuration and scenario it ran.",
    "agent_input": "The task handed to the agent for this step.",
    "model_request": "A turn was sent to the model.",
    "model_response": "The model's reply for one turn.",
    "tool_requested": "The agent asked for a tool call - a request, not an execution.",
    "policy_decision": "The authorization outcome for a tool request.",
    "tool_executed": "The tool actually ran (only ever after an `allow`).",
    "tool_result": "What the tool returned, or why a call was denied or held.",
    "security_event": "A labelled security observation - defined in the schema but not emitted by the current runtime.",
    "agent_output": "The agent's final answer.",
    "run_completed": "The run finished normally.",
    "run_failed": "The run ended with an error.",
}

#: One-line meaning of each field name (the schema has no such text).
FIELD_MEANINGS: dict[str, str] = {
    # shared header
    "run_id": "Identifier shared by every event of one run.",
    "event_id": "Stable id of this event (`ev-<seq>`); referenced by `parent_event_id`.",
    "seq": "Zero-based position of the event within the run.",
    "timestamp": "When the event was recorded (UTC, RFC 3339).",
    "agent_id": "The agent that produced the event.",
    "model": "The model identifier the agent ran with (a deterministic fixture in these labs).",
    "scenario": "The scenario the run belongs to.",
    "schema_version": "Trace-format version; always `1.0` for this schema.",
    "event_type": "Discriminator naming the kind of event.",
    "parent_event_id": "The `event_id` of the event that caused this one, or null.",
    # event-specific
    "input_ref": "Reference (hash) for the agent's input on this step.",
    "task": "The full task text handed to the agent, when recorded.",
    "answer_redacted": "The agent's final answer after redaction.",
    "output_hash": "Hash of the agent's final output.",
    "messages_hash": "Hash of the messages sent to the model.",
    "tool_specs_hash": "Hash of the tool specifications offered to the model.",
    "seed": "Deterministic seed recorded for the turn, when applicable.",
    "temperature": "Sampling temperature recorded for the turn, when applicable.",
    "finish_reason": "Why the model's turn ended (for example `tool_calls` or `stop`).",
    "latency_ms": "Model latency in milliseconds, when recorded.",
    "response_hash": "Hash of the model's response.",
    "text_ref": "Reference to the model's text output, when there is one.",
    "usage": "Token usage for the model turn (see the token-usage object below).",
    "decision": "The policy outcome: `allow`, `deny` or `require_approval`.",
    "matched_rule": "Name of the policy rule that matched, or null when none did.",
    "reason": "Human-readable explanation from the policy engine.",
    "duration_ms": "Total run duration in milliseconds.",
    "steps": "Number of agent steps taken in the run.",
    "usage_total": "Aggregate token usage for the whole run.",
    "error_type": "Type of the error that ended the run.",
    "message": "Error message for the failed run.",
    "config_ref": "Reference to the experiment configuration that was run.",
    "scenario_id": "Identifier of the scenario that ran.",
    "label": "Short label for the security event.",
    "severity": "Severity of the security event: `info`, `low`, `medium`, `high` or `critical`.",
    "evidence": "Free-form evidence object for the security event.",
    "tool_name": "Name of the tool that was requested or executed.",
    "args_hash": "Hash of the tool arguments.",
    "args_redacted": "The tool arguments after redaction (secret-looking values replaced).",
    "started_at": "When tool execution began, when recorded.",
    "ok": "Whether the tool call succeeded (`true`) or returned a safe error or refusal (`false`).",
    "error": "Error text for a failed, denied or held tool call, or null.",
    "result_hash": "Hash of the value the tool returned.",
    "side_effects": "Observable synthetic state changes (a row deleted, a message sent), or null.",
    # token-usage object
    "prompt_tokens": "Tokens in the prompt.",
    "completion_tokens": "Tokens in the completion.",
    "total_tokens": "Prompt tokens plus completion tokens.",
}

#: The shared header, in the reading order the labs use.
HEADER_ORDER = (
    "run_id",
    "event_id",
    "seq",
    "timestamp",
    "agent_id",
    "model",
    "scenario",
    "event_type",
    "schema_version",
    "parent_event_id",
)

#: Object defs rendered as their own table (not as event records).
OBJECT_DEFS = {"UsageCounts": "Token usage (`usage` / `usage_total`)"}

#: Human note for JSON Schema ``format`` values.
FORMATS = {"date-time": "RFC 3339 date-time"}


def _simple(spec: dict) -> str:
    """A short type label for one JSON Schema fragment."""
    if "$ref" in spec:
        return spec["$ref"].rsplit("/", 1)[-1]
    kind = spec.get("type", "any")
    if kind == "array":
        return f"array of {_simple(spec.get('items', {}))}"
    if kind == "object":
        return "object"
    notes = []
    fmt = spec.get("format")
    if fmt in FORMATS:
        notes.append(FORMATS[fmt])
    if spec.get("minLength") == 1:
        notes.append("non-empty")
    if "minimum" in spec:
        notes.append(f">= {spec['minimum']}")
    return kind + (f" ({', '.join(notes)})" if notes else "")


def _type_label(spec: dict) -> str:
    """A type label that also shows enum/union information."""
    if "enum" in spec:
        values = ", ".join(f"`{value}`" for value in spec["enum"])
        return f"{spec.get('type', 'string')} - one of {values}"
    if "const" in spec:
        return f"{spec.get('type', 'string')} - always `{spec['const']}`"
    if "anyOf" in spec:
        return " or ".join(_simple(part) for part in spec["anyOf"])
    return _simple(spec)


def _table(rows: list[tuple[str, str, str, str]]) -> list[str]:
    """Render rows of (field, type, required, meaning) as a Markdown table."""
    lines = [
        "| Field | Type | Required | Meaning |",
        "| --- | --- | --- | --- |",
    ]
    for field, type_label, required, meaning in rows:
        lines.append(f"| `{field}` | {type_label} | {required} | {meaning} |")
    return lines


def _field_row(name: str, spec: dict, required: set[str]) -> tuple[str, str, str, str]:
    if name not in FIELD_MEANINGS:
        raise SystemExit(
            f"no documented meaning for field {name!r}; add it to FIELD_MEANINGS "
            "in scripts/export_trace_reference.py"
        )
    return (
        name,
        _type_label(spec),
        "yes" if name in required else "no",
        FIELD_MEANINGS[name],
    )


def render() -> str:
    """Return the complete Markdown page derived from the canonical schema."""
    schema = trace_json_schema()
    defs = schema["$defs"]
    mapping = schema["discriminator"]["mapping"]
    events = [event for event in TRACE_EVENT_TYPES]
    missing = [event for event in events if event not in EVENT_MEANINGS]
    if missing:
        raise SystemExit(f"no documented meaning for event(s) {missing}")

    header_specs = defs[mapping[events[0]].rsplit("/", 1)[-1]]["properties"]
    lines: list[str] = [
        "# Trace field reference",
        "",
        "Every AgentSec trace is one JSON object per line (JSONL). Each line is a",
        "single **event**, and every event carries the same **shared header** plus",
        "fields specific to its `event_type`.",
        "",
        "> **This page is generated from the trace schema.** It is derived from the",
        "> canonical schema (`agentsec.trace.schema`), the same source that produces",
        "> `schemas/trace/trace_event.v1.schema.json`. Do not edit it by hand; run",
        "> `py scripts/export_trace_reference.py` instead. A test fails if the page",
        "> and the schema disagree.",
        "",
        "The exercises in [`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md)",
        "and the per-lab walkthroughs in [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md)",
        "both assume you can find these fields. This page is the lookup table for",
        "them.",
        "",
        "## How to read a row",
        "",
        "* **Field** - the JSON key, exactly as it appears in the trace.",
        "* **Type** - the JSON type; allowed values are listed for enumerated fields.",
        "* **Required** - whether the field is always present (`yes`) or may be",
        "  absent/`null` (`no`).",
        "* **Meaning** - what the field records. A field records a *fact*; it does not",
        "  by itself prove what happened elsewhere in the run.",
        "",
        "## Shared header fields",
        "",
        "Every event carries these. `event_type` decides which additional fields",
        "follow.",
        "",
    ]
    header_required = set(defs[mapping[events[0]].rsplit("/", 1)[-1]]["required"])
    header_rows = []
    for name in HEADER_ORDER:
        spec = header_specs[name]
        if name == "event_type":
            # ``event_type`` is a per-event discriminator: its ``const`` differs
            # for every record, so show the plain type here and enumerate the
            # values in the event sections below.
            spec = {key: value for key, value in spec.items() if key not in ("const", "default")}
        header_rows.append(_field_row(name, spec, header_required))
    lines.extend(_table(header_rows))
    lines.append("")
    lines.append("## Event records")
    lines.append("")
    lines.append(
        "Each entry lists the **event-specific** fields; add the shared header above"
    )
    lines.append("to get the whole record.")
    lines.append("")
    for event in events:
        def_name = mapping[event].rsplit("/", 1)[-1]
        body = defs[def_name]
        props = body["properties"]
        required = set(body.get("required", []))
        extras = [name for name in sorted(props) if name not in HEADER_ORDER]
        lines.append(f"### `{event}`")
        lines.append("")
        lines.append(EVENT_MEANINGS[event])
        lines.append("")
        if extras:
            lines.extend(_table([_field_row(name, props[name], required) for name in extras]))
        else:
            lines.append("_No event-specific fields beyond the shared header._")
        lines.append("")
    for def_name, title in OBJECT_DEFS.items():
        body = defs[def_name]
        props = body["properties"]
        required = set(body.get("required", []))
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"The object def `{def_name}`.")
        lines.append("")
        lines.extend(
            _table([_field_row(name, props[name], required) for name in sorted(props)])
        )
        lines.append("")
    lines.append("## Where this page comes from")
    lines.append("")
    lines.append(
        "```bash\npy scripts/export_trace_schema.py     # underlies the fields above\n"
        "py scripts/export_trace_reference.py  # regenerates this page\n```"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
