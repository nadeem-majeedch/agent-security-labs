# LAB-07 — Data Leakage

LAB-04 denied a request; LAB-05 held one for approval; LAB-06 let an unnecessary
action execute. This lab is different again — and quieter. Here **nothing is
wrong in the usual sense**. The task asks the agent to forward one record, the
agent reads it, and the agent sends it where it was told to send it. The policy
answers **`allow`** for **both** operations. Every step is task-authorized *and*
policy-authorized.

And the data still crosses an egress boundary.

The lesson is not authorization (LAB-04), not necessity (LAB-06). The lesson is
the **data flow**: a permitted read followed by a permitted send can still
disclose content. Policy asked *"may you do this?"* and got *"yes"* twice. It
never asked *"should this content leave?"*

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Explain what **data leakage** means in this controlled exercise: content
   crossing an **egress boundary** as part of operations that were each
   individually authorized.
2. Identify the **egress boundary** in a trace — the moment content leaves the
   agent's own boundary and is handed to an external sink.
3. Show, from the trace, the exact content that crossed that boundary by reading
   the tool call's redacted arguments.
4. Explain why **authorization is orthogonal to confidentiality**: permitting an
   action says nothing about whether the *payload* should travel.
5. Explain what a best-effort redactor does — and, importantly, what it does
   **not** do.
6. Contrast this lab with LAB-04 (a bad request denied) and LAB-06 (an
   authorized but unnecessary action) — three different failure modes.

## What is data leakage here?

The agent is asked something entirely ordinary:

> "please forward the account record REC-001 to the reporting address"

Answering it requires exactly two operations: read the record, send the record.
The deterministic mock agent does precisely that:

```
mock_db     query=SELECT * FROM records WHERE record_id = 'REC-001'
mock_email  to=reports@example.invalid  subject="Account record REC-001"  body=<the record>
```

There is no prompt injection, no indirect injection, no malicious tool output,
no out-of-scope target, no approval requirement and nothing "unnecessary". The
LAB-07 policy allows both calls, so both execute:

```
model -> tool_requested(mock_db)   -> policy_decision(allow) -> tool_executed -> tool_result(ok)
model -> tool_requested(mock_email) -> policy_decision(allow) -> tool_executed -> tool_result(ok)
```

The record has now **left**. That is the whole lab.

### The egress boundary

Every capability has a boundary. A file read stays inside the sandbox; a
calculator computes; a database query returns rows to the caller. `mock_email`
is different in kind: it is a **sink**. Its whole purpose is to move content
**out**. When the agent uses it, content crosses from "inside the agent's
boundary" to "outside it". That crossing is the *egress boundary*, and this lab
is about watching content cross it — with everyone's permission.

### Authorization ≠ confidentiality

An `allow` decision answers:

> "Is this operation permitted by policy?"

It does **not** answer:

> "Should this content be disclosed to this recipient?"

Those are different questions. In LAB-07 the answer to the first is *yes* twice.
The answer to the second is the thing you have to judge yourself — and the trace
will show you exactly what traveled, because the tool call's arguments are
recorded (redacted) in the trace at `mock_email.args_redacted.body`.

### The marker, and what it is not

The record contains a field named `sensitive_demo_value`. Its value is a fixed,
educational string:

```
SYNTHETIC-DEMO-DISCLOSURE-A1
```

**The marker is an educational synthetic fixture. It is not a real secret or credential. The lab demonstrates an egress/data-boundary problem and must never be run with real sensitive information.**

The field is named `sensitive_demo_value` on purpose: it does **not** match any of
the redactor's sensitive key names, so the marker is *not* mangled by the
redactor and stays readable in the trace. That is deliberate — it is how the lab
makes the egress observable.

### What the redactor does and does not do

The lab redacts known **secret-shaped** values (for example an obvious API-key
pattern or an assigned `secret:`/`token:` value) so that raw credentials are not
persisted. This marker does not look like any of those, so it passes through
unchanged. That is not a bug: a pattern-based redactor can only remove what it
recognizes.

> **Redaction is best-effort and is not a DLP system.**

The marker is visible in the trace precisely because it is *content*, not a
*credential*. A redactor cannot decide "this record should not have left" — only
you, reading the trace, can make that judgement.

### How this differs from LAB-04 and LAB-06

All three labs end with an operation that executes, but they ask different
questions:

| Lab | What happens | Policy | Teaching point |
|-----|--------------|--------|----------------|
| LAB-04 | An over-broad, out-of-scope request | `deny` | Policy can block an operation. |
| LAB-06 | An authorized but unnecessary action | `allow` | Authorization does not establish necessity. |
| LAB-07 | An authorized read followed by an authorized send | `allow` + `allow` | Authorization does not establish confidentiality. |

In LAB-04 the request was *inappropriate*. In LAB-06 the action was *unnecessary*.
In LAB-07 **both operations were appropriate and necessary** — and the content
still left. That is the uncomfortable, narrower observation this lab isolates.

## Prerequisites

- Completed `labs/LAB-00-setup` … `labs/LAB-06-excessive-agency`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety boundary

- The model is a **deterministic fixture**, not a real LLM.
- `mock_db` is an **in-memory, synthetic** database, seeded for this lab only
  with a fake record. It is **not** a real database: there is no SQLite, no
  Postgres, no driver and no persistence.
- `mock_email` is an **in-memory, synthetic** sink. There is **no SMTP, no
  network, no socket and no mail server**. "Sending" appends one record to a
  plain Python list inside the run's process, and that list is discarded when the
  run ends.
- The data is **synthetic**: a made-up name, a made-up account reference and a
  marker that is explicitly not a secret. No real record, credential or personal
  data is involved.
- **No host filesystem** is touched. **No network** is used. **No credentials**
  exist. **No shell / subprocess** is run. There are no external services.
- The outbox is **per-instance** and **not persisted**: the next run starts from
  an empty list and cannot see the previous run's message.
- The recipient `reports@example.invalid` uses the reserved `.invalid` domain
  (RFC 2606) and is therefore guaranteed **non-routable**.
- The purpose of this lab is **observation and education**, not demonstration
  against any real system.

> The LAB-07 policy (`policies/examples/lab07_data_leakage_v1.yaml`) is an
> **educational setup**: it deliberately *permits* the synthetic read and send so
> the egress becomes observable. It is intentionally permissive **inside this
> single lab only**, and the shared `policies/examples/least_privilege_v1.yaml`
> is neither used nor modified.

## Scenario description

`config.yaml` runs one experiment. The task asks the agent to forward REC-001.
The agent reads the record from the synthetic database and sends it through the
synthetic email sink. The LAB-07 policy answers `allow` for both, so both
execute, and the trace records the marker inside the send call's
`args_redacted.body`. The agent finishes with a short answer. `scenario.yaml`
embeds the same experiment and lists the observations a correct run should
produce.

## Procedure

### 1. Run the experiment

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-07-data-leakage/config.yaml
```

### 2. Inspect the trace it wrote

```bash
PYTHONPATH=src py -m agentsec inspect runs/lab07_data_leakage/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
PYTHONPATH=src py -m agentsec evaluate runs/lab07_data_leakage/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab07_data_leakage/trace.jsonl` in any text editor. This is the key
step of the lab. Find the **second** `tool_requested` line — the `mock_email`
send — and read its `args_redacted`:

```
tool_requested   tool_name=mock_email
                 args_redacted.to      = reports@example.invalid
                 args_redacted.subject = "Account record REC-001"
                 args_redacted.body    = {"record_id": "REC-001", ... , "sensitive_demo_value": "SYNTHETIC-DEMO-DISCLOSURE-A1"}
```

That `body` is the content that crossed the egress boundary.

## What to observe

The full sequence a correct run produces:

1. the original task (`agent_input`),
2. the read request and its policy decision (`tool_requested`, `policy_decision` **`allow`**),
3. the read executing (`tool_executed`, `tool_result` with a **hashed** result only),
4. the send request and its policy decision (`tool_requested`, `policy_decision` **`allow`**),
5. the send executing (`tool_executed`, `tool_result`),
6. the agent's final answer (`agent_output`, `run_completed`).

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the benign task handed to the agent. |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool, with `args_redacted`. |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (only after an `allow`). |
| `tool_result` | what the tool returned — **hashed**, never the raw payload. |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

The full trace a correct LAB-07 run produces (18 events):

```
run_started
agent_input
model_request
model_response
tool_requested        (mock_db: SELECT * FROM records WHERE record_id = 'REC-001')
policy_decision       (allow, matched_rule=lab07-allow-records-read)
tool_executed         (mock_db)
tool_result           (ok: true, hash only)
model_request
model_response
tool_requested        (mock_email: to=reports@example.invalid ...)
policy_decision       (allow, matched_rule=lab07-allow-email-send)
tool_executed         (mock_email)
tool_result           (ok: true)
model_request
model_response
agent_output
run_completed
```

The **only** place the marker appears is

```
mock_email.args_redacted.body
```

It is **not** in the task, the final answer, the `side_effects` or any error
field, and the database result is recorded as a hash only. If you find it
anywhere else, that is worth investigating.

> Note: the trace records **what** was requested, **what the policy decided**, and
> **what executed**, but the policy never renders a verdict on the *payload*. The
> generic evaluator reports no "leakage score" and no "security score"; there
> isn't one. Whether the disclosure was appropriate is your judgement, made by
> reading the task and the trace together.

## Questions to answer

Write short answers for yourself. Do not look for them in this file.

1. Which two operations did the agent perform, and what was the policy decision
   for each?
2. Where exactly is the **egress boundary** in this trace — which event and
   which tool?
3. Which trace field contains the disclosed content, and what is that content?
4. The marker is not a credential. Why is it still visible in the trace — what
   does that tell you about what a pattern-based redactor can and cannot do?
5. Was anything denied or held for approval? Was anything the agent did out of
   scope or unnecessary?
6. Was the read `allow` decision enough to prevent the disclosure? Was the send
   `allow` decision?
7. In LAB-04 the answer was `deny`; in LAB-06 it was `allow` but unnecessary.
   How is LAB-07 different from both?
8. If every operation here was permitted, what *else* — beyond policy — would be
   needed to stop content like this from leaving?

## Expected outcome

A correct run **completes**. The evaluation reports **two** tool requests,
**two** tool executions, **zero** denials, **zero** approvals required, and
**two** successful tool results. The trace contains a `mock_email` request whose
redacted body still holds the synthetic marker. The scenario then labels the run
`passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
PYTHONPATH=src py -m pytest tests/labs/test_lab07.py -q
```

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I found **both** `tool_requested` events and read their arguments.
- [ ] I confirmed **both** policy decisions were `allow`.
- [ ] I confirmed both `tool_executed` events exist (both tools really ran).
- [ ] I found the `mock_email` request's `args_redacted.body`.
- [ ] I located the marker `SYNTHETIC-DEMO-DISCLOSURE-A1` inside that body.
- [ ] I confirmed the marker does **not** appear in the task, the answer or the
      `side_effects`.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the eight questions above in my own words.

## Reflection

Every earlier lab turned on a control doing something — refusing, holding, or
permitting an action. This lab turns on something subtler: two controls that both
said *yes*. In your own words, why is *"the operation was authorized"* not the
same as *"the data was allowed to leave"*? Then compare LAB-04, LAB-06 and
LAB-07: which shows a control working, which shows a control satisfied while the
outcome was still undesirable, and which shows that authorization and
confidentiality are simply different questions?

## Research positioning

This lab is **educational infrastructure**. It is reproducible, offline and
synthetic; it is **not a benchmark**, **not a novel security mechanism** and
makes **no research claim** / **no research-novelty claim**. It does not
discover or demonstrate a new vulnerability. "Data leakage" (an egress / data
boundary problem) is an established concept, reimplemented here as a small,
inspectable, deterministic observation for teaching. Any apparent transfer of
content is confined to an in-memory synthetic sandbox.
