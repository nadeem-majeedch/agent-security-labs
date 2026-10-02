# Trace field reference

Every AgentSec trace is one JSON object per line (JSONL). Each line is a
single **event**, and every event carries the same **shared header** plus
fields specific to its `event_type`.

> **This page is generated from the trace schema.** It is derived from the
> canonical schema (`agentsec.trace.schema`), the same source that produces
> `schemas/trace/trace_event.v1.schema.json`. Do not edit it by hand; run
> `py scripts/export_trace_reference.py` instead. A test fails if the page
> and the schema disagree.

The exercises in [`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md)
and the per-lab walkthroughs in [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md)
both assume you can find these fields. This page is the lookup table for
them.

## How to read a row

* **Field** - the JSON key, exactly as it appears in the trace.
* **Type** - the JSON type; allowed values are listed for enumerated fields.
* **Required** - whether the field is always present (`yes`) or may be
  absent/`null` (`no`).
* **Meaning** - what the field records. A field records a *fact*; it does not
  by itself prove what happened elsewhere in the run.

## Shared header fields

Every event carries these. `event_type` decides which additional fields
follow.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `run_id` | string (non-empty) | yes | Identifier shared by every event of one run. |
| `event_id` | string (non-empty) | yes | Stable id of this event (`ev-<seq>`); referenced by `parent_event_id`. |
| `seq` | integer (>= 0) | yes | Zero-based position of the event within the run. |
| `timestamp` | string (RFC 3339 date-time) | yes | When the event was recorded (UTC, RFC 3339). |
| `agent_id` | string (non-empty) | yes | The agent that produced the event. |
| `model` | string (non-empty) | yes | The model identifier the agent ran with (a deterministic fixture in these labs). |
| `scenario` | string (non-empty) | yes | The scenario the run belongs to. |
| `event_type` | string | yes | Discriminator naming the kind of event. |
| `schema_version` | string - always `1.0` | no | Trace-format version; always `1.0` for this schema. |
| `parent_event_id` | string or null | no | The `event_id` of the event that caused this one, or null. |

## Event records

Each entry lists the **event-specific** fields; add the shared header above
to get the whole record.

### `run_started`

The run began; records the configuration and scenario it ran.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `config_ref` | string (non-empty) | yes | Reference to the experiment configuration that was run. |
| `scenario_id` | string (non-empty) | yes | Identifier of the scenario that ran. |
| `seed` | integer or null | no | Deterministic seed recorded for the turn, when applicable. |
| `temperature` | number or null | no | Sampling temperature recorded for the turn, when applicable. |

### `agent_input`

The task handed to the agent for this step.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `input_ref` | string (non-empty) | yes | Reference (hash) for the agent's input on this step. |
| `task` | string or null | no | The full task text handed to the agent, when recorded. |

### `model_request`

A turn was sent to the model.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `messages_hash` | string (non-empty) | yes | Hash of the messages sent to the model. |
| `seed` | integer or null | no | Deterministic seed recorded for the turn, when applicable. |
| `temperature` | number or null | no | Sampling temperature recorded for the turn, when applicable. |
| `tool_specs_hash` | string (non-empty) | yes | Hash of the tool specifications offered to the model. |

### `model_response`

The model's reply for one turn.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `finish_reason` | string or null | no | Why the model's turn ended (for example `tool_calls` or `stop`). |
| `latency_ms` | number or null | no | Model latency in milliseconds, when recorded. |
| `response_hash` | string (non-empty) | yes | Hash of the model's response. |
| `text_ref` | string or null | no | Reference to the model's text output, when there is one. |
| `usage` | UsageCounts or null | no | Token usage for the model turn (see the token-usage object below). |

### `tool_requested`

The agent asked for a tool call - a request, not an execution.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `args_hash` | string (non-empty) | yes | Hash of the tool arguments. |
| `args_redacted` | object or null | no | The tool arguments after redaction (secret-looking values replaced). |
| `tool_name` | string (non-empty) | yes | Name of the tool that was requested or executed. |

### `policy_decision`

The authorization outcome for a tool request.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `decision` | string - one of `allow`, `deny`, `require_approval` | yes | The policy outcome: `allow`, `deny` or `require_approval`. |
| `matched_rule` | string or null | no | Name of the policy rule that matched, or null when none did. |
| `reason` | string | yes | Human-readable explanation from the policy engine. |

### `tool_executed`

The tool actually ran (only ever after an `allow`).

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `started_at` | string (RFC 3339 date-time) or null | no | When tool execution began, when recorded. |
| `tool_name` | string (non-empty) | yes | Name of the tool that was requested or executed. |

### `tool_result`

What the tool returned, or why a call was denied or held.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `error` | string or null | no | Error text for a failed, denied or held tool call, or null. |
| `ok` | boolean | yes | Whether the tool call succeeded (`true`) or returned a safe error or refusal (`false`). |
| `result_hash` | string (non-empty) | yes | Hash of the value the tool returned. |
| `side_effects` | array of string or null | no | Observable synthetic state changes (a row deleted, a message sent), or null. |

### `security_event`

A labelled security observation - defined in the schema but not emitted by the current runtime.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `evidence` | object or null | no | Free-form evidence object for the security event. |
| `label` | string (non-empty) | yes | Short label for the security event. |
| `severity` | string - one of `info`, `low`, `medium`, `high`, `critical` | yes | Severity of the security event: `info`, `low`, `medium`, `high` or `critical`. |

### `agent_output`

The agent's final answer.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `answer_redacted` | string or null | no | The agent's final answer after redaction. |
| `output_hash` | string (non-empty) | yes | Hash of the agent's final output. |

### `run_completed`

The run finished normally.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `duration_ms` | number (>= 0) | yes | Total run duration in milliseconds. |
| `steps` | integer (>= 0) | yes | Number of agent steps taken in the run. |
| `usage_total` | UsageCounts or null | no | Aggregate token usage for the whole run. |

### `run_failed`

The run ended with an error.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `error_type` | string (non-empty) | yes | Type of the error that ended the run. |
| `message` | string | yes | Error message for the failed run. |

## Token usage (`usage` / `usage_total`)

The object def `UsageCounts`.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `completion_tokens` | integer (>= 0) | yes | Tokens in the completion. |
| `prompt_tokens` | integer (>= 0) | yes | Tokens in the prompt. |
| `total_tokens` | integer (>= 0) | yes | Prompt tokens plus completion tokens. |

## Where this page comes from

```bash
py scripts/export_trace_schema.py     # underlies the fields above
py scripts/export_trace_reference.py  # regenerates this page
```
