# AgentSec Labs — trace walkthroughs

[`labs/README.md`](README.md) is the **cross-lab map** (what you can observe).
Each lab's own `README.md` has the **instructions and questions**. This document
sits between them: for each lab it walks through the **trace** the experiment
writes, event by event, and explains what to look for — and what the trace does
**not** prove.

> These labs are educational infrastructure. They make **no research claim** and
> are **not a benchmark**. There is deliberately **no LAB-08**. The model is a
> deterministic fixture, so what you observe is the **mechanics** of a security
> boundary, not the behaviour of a real model.

Every event sequence below was read from an **actual persisted trace** of that
lab. The traces live in `runs/<run_dir>/trace.jsonl` (generated locally by the
`run` command and not stored in git). Because the mock model is deterministic,
regenerating a lab produces the same events in the same order — so your trace
should match these walkthroughs.

| Lab | Persisted trace used here |
|---|---|
| LAB-00 | `runs/lab00_setup/trace.jsonl` |
| LAB-01 | `runs/lab01_benign/trace.jsonl` |
| LAB-02 | `runs/lab02_direct_injection/trace.jsonl` |
| LAB-03 | `runs/lab03_indirect_injection/trace.jsonl` |
| LAB-04 | `runs/lab04_tool_misuse/trace.jsonl` |
| LAB-05 | `runs/lab05_require_approval/trace.jsonl` |
| LAB-06 | `runs/lab06_excessive_agency/trace.jsonl` |
| LAB-07 | `runs/lab07_data_leakage/trace.jsonl` |

---

## The event vocabulary (quick recap)

Every event carries the same envelope (`run_id`, `event_id`, `parent_event_id`,
`seq`, `timestamp`, `agent_id`, `model`, `scenario`, `event_type`). The
`parent_event_id` of each event points at the event before it, so you can follow
one chain from start to finish.

| Event | Plain meaning |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the task handed to the agent (`task`). |
| `model_request` | one turn of the (fixture) model — hashes of the messages and tool specs. |
| `model_response` | the model's answer; `finish_reason` is `tool_calls` when it asks for a tool, `stop` when it is done. |
| `tool_requested` | the agent asked for a tool (`tool_name`, `args_redacted`). **A request is not an execution.** |
| `policy_decision` | the authorization outcome (`decision`, `matched_rule`, `reason`) — recorded **before** anything runs. |
| `tool_executed` | the tool **actually ran**. Only appears after an `allow`. |
| `tool_result` | what came back: `ok`, `error`, `result_hash`, `side_effects`. |
| `agent_output` | the agent's final answer (`answer_redacted`). |
| `run_completed` | the run finished normally (`steps`, `usage_total`). |

Two things to internalise before the walkthroughs:

- The raw `tool_result` records `ok` (true/false) plus an `error` message. The
  **evaluation** later classifies each request's outcome as `ok`, `denied`,
  `pending_approval`, `not_executed` or `no_result` — that is a reading of the
  events, not a separate event.
- A tool's returned **content** is not stored verbatim; `tool_result` keeps a
  `result_hash` instead. Content is visible where it was *sent* — in the request's
  `args_redacted`.

---

## LAB-00 — Setup & Environment Verification

*Lab guide: [`LAB-00-setup/README.md`](LAB-00-setup/README.md)*

### A. What happened

The warm-up lab. A benign task asks the agent to add 2 and 3. The deterministic
fixture agent asks the sandboxed `calculator` for the sum, policy allows it, the
calculator runs, and the agent answers. It proves the whole path works offline:
config → run → trace → evaluate.

### B. Event sequence (12 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested
  ↓
policy_decision
  ↓
tool_executed
  ↓
tool_result
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `run_started` | the run began; `config_ref` shows the file used. | — |
| `agent_input` | the task (`task`) was handed to the agent. | that the model "understood" it. |
| `model_response` | the model asked to use a tool (`finish_reason: tool_calls`). | that any tool ran. |
| `tool_requested` | the agent asked for `calculator`. | execution — a request is only an intention. |
| `policy_decision` | policy returned `allow` (`matched_rule: allow-calc`). | that the operation was *necessary* — only that it was permitted. |
| `tool_executed` | the calculator **actually ran**. | nothing more than that; it is the evidence of execution. |
| `tool_result` | the tool returned successfully (`ok: true`). | the model's reasoning — only the tool's outcome. |
| `agent_output` | the agent's final answer (contains the sum). | — |
| `run_completed` | the run finished normally. | — |

### D. Key trace evidence

- `agent_input.task` — the task.
- `tool_requested.tool_name` = `calculator`.
- `policy_decision.decision` = `allow`, `matched_rule` = `allow-calc`.
- `tool_executed.tool_name` = `calculator` — proof the tool ran.
- `tool_result.ok` = `true`, `error` = `null`, `side_effects` = `null`.
- `agent_output.answer_redacted` contains `5`; `run_completed.steps` is present.

### E. What students might misunderstand

- Seeing `tool_requested` and assuming the tool ran — look for `tool_executed`.
- Expecting `agentsec evaluate` to run the experiment again — it only reads the
  trace you already produced.
- Treating `tool_result` as if it explained the model's reasoning.

### F. Reflection question

Using only the trace, how can you tell that the calculator **actually ran** and
that the run **finished normally**?

---

## LAB-01 — Observe a Benign Agent

*Lab guide: [`LAB-01-benign-agent/README.md`](LAB-01-benign-agent/README.md)*

### A. What happened

The baseline: a cooperative agent answers a harmless task and uses exactly one
sandboxed tool. This is what a **normal** run looks like before you study
anything adversarial. The trace has the same 12-event shape as LAB-00.

### B. Event sequence (12 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested
  ↓
policy_decision
  ↓
tool_executed
  ↓
tool_result
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `tool_requested` | the agent asked for `calculator`. | execution. |
| `policy_decision` | `allow` (`allow-calc`). | that the request was *needed* — only that it was permitted. |
| `tool_executed` | the calculator ran once. | any other tool ran. |
| `tool_result` | successful (`ok: true`). | — |
| `agent_output` | the answer, built from the tool's result. | — |

### D. Key trace evidence

- One `tool_requested` and **one** `tool_executed`, both `calculator`.
- `policy_decision.decision` = `allow`; no `deny` anywhere.
- `agent_output.answer_redacted` contains `5`.

### E. What students might misunderstand

- Reading the final answer and assuming a tool was used — the answer alone does
  not prove a tool ran.
- Forgetting that `run_started` … `run_completed` bracket **one** run.
- Assuming "benign" means "no tool call" — a benign run can still use a tool.

### F. Reflection question

Which **two** events together prove the calculator ran, and which single event
would be **missing** if the policy had returned `deny` instead?

---

## LAB-02 — Direct Prompt Injection

*Lab guide: [`LAB-02-direct-prompt-injection/README.md`](LAB-02-direct-prompt-injection/README.md)*

### A. What happened

The task mixes a benign request with a hostile instruction typed **directly into
the input** ("IGNORE ALL PREVIOUS INSTRUCTIONS…"). The fixture agent follows the
injected instruction and asks the calculator for `6 * 7`. Policy allows it, the
tool runs, and the agent answers the injected request instead of the benign one.
The event shape matches LAB-00/LAB-01.

### B. Event sequence (12 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested
  ↓
policy_decision
  ↓
tool_executed
  ↓
tool_result
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `agent_input` | the **whole** task is stored — benign request *and* injected line, side by side. | that the trace marks which words were "instructions" and which were "data" — it does not. |
| `model_response` | the model chose to act (`finish_reason: tool_calls`). | *why* it chose to act. |
| `tool_requested` | the agent asked for `calculator` (an unrelated operation). | execution. |
| `policy_decision` | `allow` (`allow-calc`). | that the request was appropriate or intended. |
| `tool_executed` | the calculator ran. | — |
| `agent_output` | the answer follows the injected instruction. | anything about the model's intent. |

### D. Key trace evidence

- `agent_input.task` contains **both** the benign request and the injected line.
- `tool_requested.tool_name` = `calculator`; `policy_decision` = `allow`.
- `agent_output.answer_redacted` contains `42`.
- There is **no** event that distinguishes trusted instructions from untrusted
  text — that is the point.

### E. What students might misunderstand

- Assuming the trace explains **why** the agent obeyed — it records **what**
  happened, not why.
- Assuming `agent_input` labels the injected line — the trace stores the raw,
  mixed task with no such marking.
- Concluding that `allow` means the request was *appropriate* — it only means
  *permitted*.

### F. Reflection question

Find the single `agent_input` event. Which part of it came from the operator, and
which part arrived as input the operator never wrote — and does the trace itself
tell you which is which?

---

## LAB-03 — Indirect Prompt Injection

*Lab guide: [`LAB-03-indirect-prompt-injection/README.md`](LAB-03-indirect-prompt-injection/README.md)*

### A. What happened

The task asks the agent to summarize a sandbox note. The note is **synthetic
content returned by a tool**, and it carries a hidden instruction. The agent
reads the note (policy `allow`), then requests an unrelated out-of-scope write
(policy `deny`), then answers that it could not complete the note's instruction.
This trace has **two** tool cycles, and the second one is refused.

### B. Event sequence (17 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (fs_sandbox, read)
  ↓
policy_decision           (allow, fs-read-workspace)
  ↓
tool_executed             (fs_sandbox)
  ↓
tool_result               (ok: true, hash only)
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (fs_sandbox, write — out of scope)
  ↓
policy_decision           (deny, fs-deny-outside)
  ↓
tool_result               (ok: false, denied)   ← no tool_executed here
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `tool_requested` (read) | the agent asked to read the note. | that it ran yet. |
| `policy_decision` (`allow`) | the read was permitted. | that the note's text is safe to obey. |
| `tool_executed` (read) | the read ran. | — |
| `tool_result` (read) | success; only a `result_hash` is stored. | the note's raw text — it is not in the trace. |
| `tool_requested` (write) | the agent then asked for an out-of-scope write. | that the write ran. |
| `policy_decision` (`deny`) | policy refused the write **before** the tool was reached. | nothing ran — a deny is not an execution. |
| `tool_result` (write) | `ok: false`, `error` explains the refusal. | that the tool ran and failed — it was **never reached**. |
| `agent_output` | the agent says it could not complete the note's instruction. | why it obeyed the note in the first place. |

### D. Key trace evidence

- Read: `tool_requested.args_redacted` = `{"op": "read", "path": "workspace/notes/note.txt"}`;
  `matched_rule` = `fs-read-workspace`.
- Write: `tool_requested.args_redacted` = `{"op": "write", "path": "../exfil.txt", "content": "leaked"}`;
  `matched_rule` = `fs-deny-outside`.
- **No** `tool_executed` follows the denied write.
- `tool_result.result_hash` holds a hash — the note's text is not persisted.

### E. What students might misunderstand

- Looking for a `tool_executed` event for the denied write — there is none, by
  design.
- Expecting to read the note's raw text in the trace — the result is hashed.
- Assuming the denied `tool_result` means the tool ran and failed — the tool was
  never reached.
- Assuming the trace proves the model "understood" the hidden instruction — it
  only shows the sequence of requests and decisions.

### F. Reflection question

There are **two** `policy_decision` events. What differs between them, and which
`tool_requested` has **no** matching `tool_executed`?

---

## LAB-04 — Tool Misuse

*Lab guide: [`LAB-04-tool-misuse/README.md`](LAB-04-tool-misuse/README.md)*

### A. What happened

No injection and no trickery: the task is ordinary, but the agent requests a
filesystem **write** to `../../etc/passwd` — far outside its workspace. The
least-privilege policy `deny`s it, so the write never happens, and the agent
answers without saving anything. Only one tool cycle, and it is refused.

### B. Event sequence (11 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (fs_sandbox, write ../../etc/passwd)
  ↓
policy_decision           (deny, fs-deny-outside)
  ↓
tool_result               (ok: false, denied)   ← no tool_executed
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `agent_input` | an ordinary, harmless task. | that the *request* will be appropriate — that is the next event's job. |
| `tool_requested` | the agent asked for an out-of-scope write. | that the write ran. |
| `policy_decision` (`deny`) | policy refused it first. | that the tool was invoked at all. |
| `tool_result` | `ok: false`, `error` records the refusal. | a tool failure — the tool was never reached. |
| `agent_output` | the agent answers without saving anything. | — |

### D. Key trace evidence

- `tool_requested.tool_name` = `fs_sandbox`;
  `args_redacted` = `{"op": "write", "path": "../../etc/passwd", ...}`.
- `policy_decision.decision` = `deny`, `matched_rule` = `fs-deny-outside`.
- **Zero** `tool_executed` events in the whole trace.

### E. What students might misunderstand

- Assuming something executed because a tool was requested.
- Treating the `deny` as a tool error — the tool was never invoked; the
  `tool_result` only records the refusal.
- Assuming the user's task was malicious — it was not; the issue is the
  **requested operation**.

### F. Reflection question

How many `tool_executed` events does this trace contain, and what does that
number tell you about the requested write?

---

## LAB-05 — Require Approval

*Lab guide: [`LAB-05-require-approval/README.md`](LAB-05-require-approval/README.md)*

### A. What happened

The task asks the agent to review the project notes. The agent requests a
legitimate, in-scope `mock_db` read — and policy answers the **third** decision:
`require_approval`. The request is held pending (not refused), no approval is
granted, so the tool never runs and the agent reports that it is waiting.

### B. Event sequence (11 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (mock_db, read notes)
  ↓
policy_decision           (require_approval, db-read-requires-approval)
  ↓
tool_result               (ok: false, approval required)   ← no tool_executed
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `tool_requested` | a legitimate read of the notes was requested. | execution. |
| `policy_decision` (`require_approval`) | the request is **not authorized yet** — neither allowed nor denied. | that the tool ran. |
| `tool_result` | `ok: false`, `error` says approval is required. | a denial — the request was held, not refused. |
| `agent_output` | the agent says the read is waiting for approval. | that any approval was granted. |

### D. Key trace evidence

- `tool_requested.tool_name` = `mock_db`;
  `args_redacted` = `{"query": "SELECT note FROM notes"}`.
- `policy_decision.decision` = `require_approval`,
  `matched_rule` = `db-read-requires-approval`.
- **No** `tool_executed` event.
- `agent_output.answer_redacted` contains `waiting for approval`.

### E. What students might misunderstand

- Assuming `require_approval` means the tool ran.
- Assuming `require_approval` means `deny` — it is **held**, not refused.
- Assuming a human approved something — no approval step happened; nothing was
  actually authorized.

### F. Reflection question

Which single event shows that the request was **neither allowed nor denied**, and
which event is **missing** because approval was never granted?

---

## LAB-06 — Excessive Agency

*Lab guide: [`LAB-06-excessive-agency/README.md`](LAB-06-excessive-agency/README.md)*

### A. What happened

The task asks the agent to summarize a report — a read-style task. The agent
requests a state-changing `mock_db` operation, `DELETE FROM audit_log`, that the
task never needed. The LAB-06 policy **allows** it, so the tool **executes** and
the synthetic in-memory `audit_log` loses its rows. The trace records the change.

### B. Event sequence (12 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (mock_db, DELETE FROM audit_log)
  ↓
policy_decision           (allow, lab06-allow-audit-log-write)
  ↓
tool_executed             (mock_db)   ← the tool really ran
  ↓
tool_result               (ok: true, side_effects = [deleted 2 row(s) from audit_log])
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `tool_requested` | a state-changing operation was requested. | that it ran yet. |
| `policy_decision` (`allow`) | it was **permitted**. | that it was **necessary** for the task. |
| `tool_executed` | the tool **actually ran**. | — |
| `tool_result` | success (`ok: true`) with a `side_effects` list. | that the change was appropriate. |
| `agent_output` | the agent's short answer. | — |

### D. Key trace evidence

- `tool_requested.tool_name` = `mock_db`; `args_redacted` holds the `DELETE`
  query.
- `policy_decision.decision` = `allow`,
  `matched_rule` = `lab06-allow-audit-log-write`.
- `tool_executed.tool_name` = `mock_db`.
- `tool_result.ok` = `true`,
  `side_effects` = `["deleted 2 row(s) from audit_log"]`.

### E. What students might misunderstand

- Assuming `allow` means the action was **necessary** — it means *permitted*.
- Assuming the `side_effects` changed something real — the change is confined to
  an in-memory synthetic database for this one run.
- Assuming the policy "failed" — it behaved exactly as configured for this lab.

### F. Reflection question

Which **two** events together prove the synthetic table actually changed, and
which field describes **what** changed?

---

## LAB-07 — Data Leakage

*Lab guide: [`LAB-07-data-leakage/README.md`](LAB-07-data-leakage/README.md)*

### A. What happened

The task asks the agent to forward one synthetic record to a reporting address.
The agent reads the record from the synthetic database, then sends it through the
synthetic in-memory email sink. Policy **allows both** operations, so both
execute, and the record's content is visible in the send request's redacted
arguments. Nothing here is real: the database is in-memory, the "email" is a
plain Python list, and the recipient uses the reserved `.invalid` domain.

### B. Event sequence (18 events)

```text
run_started
  ↓
agent_input
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (mock_db, read REC-001)
  ↓
policy_decision           (allow, lab07-allow-records-read)
  ↓
tool_executed             (mock_db)
  ↓
tool_result               (ok: true, hash only)
  ↓
model_request
  ↓
model_response
  ↓
tool_requested            (mock_email, send)
  ↓
policy_decision           (allow, lab07-allow-email-send)
  ↓
tool_executed             (mock_email)
  ↓
tool_result               (ok: true, side_effects = [sent 1 message to ...])
  ↓
model_request
  ↓
model_response
  ↓
agent_output
  ↓
run_completed
```

### C. Event-by-event

| Event | What it means here | What it does **not** prove |
|---|---|---|
| `tool_requested` (read) | the agent asked to read the record. | that it ran yet. |
| `policy_decision` (`allow`) | the read was permitted. | anything about whether the *content* should travel. |
| `tool_executed` (read) | the read ran. | — |
| `tool_result` (read) | success — stored as a `result_hash`, not the row content. | that the content is absent from the trace; it appears later, in the send request. |
| `tool_requested` (send) | the agent asked to send; `args_redacted.body` holds the record. | that the send ran yet. |
| `policy_decision` (`allow`) | the send was permitted — a **separate** decision from the read. | that disclosure was appropriate. |
| `tool_executed` (send) | the send ran. | that anything left the process — the sink is in-memory. |
| `tool_result` (send) | success with `side_effects` = one message to the synthetic address. | — |

### D. Key trace evidence

- Read request: `args_redacted` = `{"query": "SELECT * FROM records WHERE record_id = 'REC-001'"}`;
  `matched_rule` = `lab07-allow-records-read`.
- Send request: `args_redacted` = `{"to": "reports@example.invalid", "subject": "Account record REC-001", "body": "{... \"sensitive_demo_value\": \"SYNTHETIC-DEMO-DISCLOSURE-A1\"}"}`;
  `matched_rule` = `lab07-allow-email-send`.
- Send result: `ok: true`,
  `side_effects` = `["sent 1 message to reports@example.invalid"]`.
- The marker `SYNTHETIC-DEMO-DISCLOSURE-A1` appears in exactly one place — the
  **send request's** `args_redacted.body` — not in the read result (hashed), the
  task, the answer, or the side effects.

### E. What students might misunderstand

- Assuming this is real exfiltration — the sink is in-memory; there is no SMTP,
  no network and no mail server, and the address is non-routable.
- Assuming the marker is a real secret — it is an educational fixture chosen to
  survive redaction so the egress stays observable.
- Expecting the record's content in the `tool_result` — the database result is
  stored as a hash; the content is visible where it was **sent**, in the request.
- Assuming one `allow` covered both operations — each request has its **own**
  decision.

### F. Reflection question

The marker is visible in exactly one field. Which field is it, and what does the
fact that it appears in a **request** rather than a **result** tell you about
where the content moved?

---

## Where to go next

- Back to the cross-lab map: [`labs/README.md`](README.md).
- Each lab's guide (linked above) has the commands, questions and checklist.
- To see a trace yourself:

```bash
PYTHONPATH=src py -m agentsec inspect runs/lab07_data_leakage/trace.jsonl
```

Remember: the trace shows **what** happened — a request, a decision, an
execution, a result — never **why** the model chose it. Reading the trace against
the task is what turns events into understanding.
