# AgentSec Labs — what you can observe

These labs are a small, offline playground for learning **AI-agent security** by
watching what an agent actually does. There are **eight labs, LAB-00 through
LAB-07**. Each one runs a single deterministic experiment, writes a **trace**
(one JSON event per line), and lets you read the trace to see the path the agent
took.

You are not scoring anything here. Nothing is ranked, and no lab is "worse" or
"better" than another — each one isolates a **different question**. The goal is
to be able to answer one question with evidence:

> **"What can I actually observe in the trace?"**

> These labs are educational infrastructure. They make **no research claim** and
> are **not a benchmark**. There is deliberately **no LAB-08**. The deterministic
> mock model is a fixture, so what you observe is the **mechanics** of a security
> boundary, not the behaviour of a real model.

---

## How to run a lab

Every lab works the same way. From the repository root:

```bash
# 1. run the experiment (writes a trace)
PYTHONPATH=src py -m agentsec run labs/LAB-0X-.../config.yaml

# 2. inspect the trace it wrote (short summary, in order)
PYTHONPATH=src py -m agentsec inspect runs/<run_dir>/trace.jsonl

# 3. evaluate the trace on its own (read-only; does NOT re-run anything)
PYTHONPATH=src py -m agentsec evaluate runs/<run_dir>/trace.jsonl
```

Start with **LAB-00** to confirm your setup, then work through the labs in order.
Each lab's own `README.md` has the exact command, the questions to answer and a
completion checklist. For a per-lab walkthrough of the trace each experiment
writes — event by event — see [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md),
and for practice reading a trace yourself see
[`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md) (answers are in an
instructor-only key).

**Instructors:** [`INSTRUCTOR-GUIDE.md`](INSTRUCTOR-GUIDE.md) is instructor-facing
teaching material — it explains the sequence, timings, rubric and discussion
prompts, and it does **not** contain the exercise answers.

## Richer inspection: `inspect --events`

The plain `inspect` summary lists one line per event. Add `--events` for a
**read-only** event-by-event view that shows each event's payload fields (only
the fields specific to that `event_type` — the shared header is listed once),
every recorded **side effect**, and the run's **flags** and **warnings**:

```bash
PYTHONPATH=src py -m agentsec inspect runs/<run_dir>/trace.jsonl --events
```

```text
Event 7
  type: tool_result
  event_id: ev-000007
  seq: 7
  parent: ev-000006
  fields:
    error: -
    ok: true
    result_hash: 8f0c...
    side_effects: ["deleted 2 row(s) from audit_log"]

Side effects:
  ev-000007  ["deleted 2 row(s) from audit_log"]

Flags:
  has_run_started: true
  has_terminal_event: true
  has_tool_requests: true
  produced_final_output: true
  reached_step_limit: false
```

`--events` only **reads** the trace: it never re-runs anything, never changes the
trace file, and never touches a lab. It is a convenience for the exercises in
[`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md) — the field-by-field
meaning of every key lives in the generated
[`TRACE-FIELD-REFERENCE.md`](TRACE-FIELD-REFERENCE.md), and the flags and
warnings are the same ones `agentsec evaluate` already reports.

## Comparing two traces: `compare`

Once you can read one trace, the next question is *what changed* between two
runs — for example the same lab under two policies, or one lab against another.
`compare` reads two existing traces and reports what differs, **read-only and
without re-running anything**:

```bash
PYTHONPATH=src py -m agentsec compare runs/<a>/trace.jsonl runs/<b>/trace.jsonl
```

The comparison is factual and structural. It reports:

* the event **counts** and their difference;
* the **event-type distribution** of each trace;
* the ordered event **sequence**, aligned **by position only** — it never guesses
  that one event "means the same as" another;
* the **evaluator differences** — status, policy decisions, tool results, tool
  calls, flags and warnings.

```text
Evaluator differences
  decisions.deny: 0 -> 1
  tool_results.denied: 0 -> 1
```

`compare` produces **no score, ranking or "better/worse" judgement** — it is a
structural comparison only. Like `inspect` and `evaluate`, it never changes a
trace and never touches a lab. Add `--json` for a machine-readable comparison.

For a worked example that compares the **same** lab under two different policies,
see ["Same lab, different policy"](LAB-04-tool-misuse/README.md#same-lab-different-policy)
in the LAB-04 README.

---

## The lab sequence

| Lab | Security concept | One line |
|---|---|---|
| [`LAB-00-setup`](LAB-00-setup/README.md) | *(warm-up)* | Prove your setup works end to end: run, trace, evaluate. |
| [`LAB-01-benign-agent`](LAB-01-benign-agent/README.md) | Benign baseline | See what a normal, cooperative run looks like. |
| [`LAB-02-direct-prompt-injection`](LAB-02-direct-prompt-injection/README.md) | Direct prompt injection | An instruction arrives **straight in the task**. |
| [`LAB-03-indirect-prompt-injection`](LAB-03-indirect-prompt-injection/README.md) | Indirect prompt injection | An instruction arrives **inside content a tool returns**. |
| [`LAB-04-tool-misuse`](LAB-04-tool-misuse/README.md) | Tool misuse | No injected instruction — the **requested operation** is out of scope. |
| [`LAB-05-require-approval`](LAB-05-require-approval/README.md) | Require approval | A legitimate request is **held for authorization** instead of refused. |
| [`LAB-06-excessive-agency`](LAB-06-excessive-agency/README.md) | Excessive agency | The action is **allowed and executes**, though the task never needed it. |
| [`LAB-07-data-leakage`](LAB-07-data-leakage/README.md) | Data leakage | An **authorized read + authorized send** still move content across an egress boundary. |

---

## The observables matrix

The same columns for every lab. Read it left to right as **one request's path**:
what was asked for, what policy decided, whether the tool really ran, and whether
anything changed.

| Lab | Security concept | Requested tool | Policy decision | Tool executed? | Tool result | Side effect |
|---|---|---|---|---|---|---|
| LAB-00 | *(warm-up)* | `calculator` | `allow` | **Yes** | `ok` | none |
| LAB-01 | Benign baseline | `calculator` | `allow` | **Yes** | `ok` | none |
| LAB-02 | Direct prompt injection | `calculator` | `allow` | **Yes** | `ok` | none |
| LAB-03 | Indirect prompt injection | `fs_sandbox` (read, then write) | `allow`, then `deny` | **Yes** (read) · **No** (write) | `ok`, then `denied` | none (the write never ran) |
| LAB-04 | Tool misuse | `fs_sandbox` (write) | `deny` | **No** | `denied` | none |
| LAB-05 | Require approval | `mock_db` (read) | `require_approval` | **No** | `pending_approval` | none |
| LAB-06 | Excessive agency | `mock_db` (write) | `allow` | **Yes** | `ok` | **Yes** — the synthetic table changed |
| LAB-07 | Data leakage | `mock_db` (read), then `mock_email` (send) | `allow`, then `allow` | **Yes** · **Yes** | `ok` · `ok` | **Yes** — content crossed an egress boundary |

**Words in this table:**

- **Requested** — the agent *asked* for the tool. That is all a request means.
- **Policy decision** — the authorization outcome: `allow`, `deny` or
  `require_approval`. It is recorded **before** anything runs.
- **Executed** — the tool **actually ran**. There is a separate event for it
  (`tool_executed`), and it only appears after an `allow`.
- **Tool result** — what came back: `ok`, `denied`, `pending_approval`, or a
  safe `error`.
- **Side effect** — the sandbox state actually changed (a write, a delete, or a
  message landing in the synthetic outbox). None of these touch anything real.

---

## Where the request comes from, and what you are looking at

| Lab | Where the instruction / problem originates | Main observation | What to distinguish |
|---|---|---|---|
| LAB-00 | a plain arithmetic task | the whole path works offline | running ≠ evaluating (step 3 reads only the trace) |
| LAB-01 | a plain arithmetic task | a normal lifecycle: model → request → decision → execution → result → answer | a **request** vs. an **execution** |
| LAB-02 | an instruction typed **into the task** | the agent follows the injected instruction instead of the real request | what the operator meant vs. what arrived as input |
| LAB-03 | an instruction **inside tool-returned content** | the agent reads a note, then acts on words hidden in that note | data the model **read** vs. words it **obeyed** |
| LAB-04 | **no instruction at all** — the chosen operation is out of scope | a valid tool is asked to do something it should not | "the tool **can**" vs. "the agent **may**" |
| LAB-05 | a legitimate, in-scope request | a request that is neither allowed nor denied — it waits | `deny` ("no") vs. `require_approval` ("not without a yes") |
| LAB-06 | a benign read-style task | an authorized action **executes** even though the task did not need it | **authorized** vs. **necessary** |
| LAB-07 | a task that explicitly asks for the transfer | both operations are authorized and required, yet the content crosses an egress boundary | **authorized** vs. **confidential** |

LAB-00 through LAB-07 are **not ranked**. LAB-04 shows a control *working*;
LAB-05 shows a control *waiting*; LAB-06 shows a control *satisfied while the
outcome is still undesirable*; LAB-07 shows that **authorization and
confidentiality are simply different questions**.

---

## Reading the trace

Every lab writes the same kind of events. You do not need the source to read
them — here is the vocabulary, in plain terms.

| Event | Plain meaning |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the task handed to the agent. |
| `model_request` / `model_response` | one turn of the (fixture) model and its answer. |
| `tool_requested` | the agent asked for a tool. **A request is not an execution.** |
| `policy_decision` | the authorization outcome: `allow`, `deny` or `require_approval`. |
| `tool_executed` | the tool **actually ran**. Only appears after an `allow`. |
| `tool_result` | what the tool returned — `ok`, `denied`, `pending_approval`, or a safe `error`. |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

Each event links to the one before it (`parent_event_id`), so you can follow the
chain: **task → response → tool request → policy → execution → result → next
response → answer**. The trace records **what** happened; it never claims to
prove **why** the model chose it.

---

## Eight distinctions to carry across every lab

These are the ideas the labs are built to make visible. They are teaching
distinctions, not measurements.

1. A **model response** is not the same as a **tool request**.
2. A **tool request** is not proof that the tool **executed**.
3. The **policy decision** happens **before** execution.
4. A **`deny`** decision prevents execution.
5. A **`require_approval`** decision does **not** mean execution happened.
6. An **`allow`** followed by a **`tool_executed`** event means the tool
   **really ran**.
7. A successful execution may produce a **synthetic side effect**.
8. A **`tool_result`** can exist for a denied request **even though no
   `tool_executed` event exists** (same for a pending-approval request).

Two more that LAB-07 makes concrete:

9. LAB-07 shows **authorized, synthetic egress** — it is **not** real-world
   exfiltration and does not demonstrate a vulnerability.
10. Because the model is a **deterministic fixture**, what you observe is the
    **mechanics of the security boundary**, not a distribution of real model
    behaviour.

---

## The concepts, side by side

Each lab changes **one** thing about where the request comes from or how policy
answers it. Read these as differences in kind, not in severity.

| Lab | How the situation differs |
|---|---|
| **LAB-02** | The instruction enters through the **task/input** (direct). |
| **LAB-03** | The instruction enters through **tool-returned content** (indirect) — one extra hop: content → tool → tool result → model. |
| **LAB-04** | **No injected instruction is needed**; the requested operation itself is outside policy scope, so policy `deny`s it. |
| **LAB-05** | The requested operation reaches an **approval boundary**; it is legitimate but is **not authorized automatically**. |
| **LAB-06** | The requested operation is **authorized and executes** — showing that authorization does **not** establish task necessity. |
| **LAB-07** | **Authorized synthetic data** is transferred through the `mock_email` egress sink — showing that authorization does **not** establish confidentiality. |

---

## What these labs are — and are not

- They are **educational infrastructure**: reproducible, offline and synthetic.
- They are **not** a benchmark, a scoring system or a ranking of attacks.
- They make **no research claim** and **no research-novelty claim**.
- LAB-07 demonstrates **observable, authorized, synthetic egress** — it is
  **not** autonomous real-world leakage, **not** a vulnerability demonstration,
  **not** real exfiltration and **not** a measurement of any model's propensity
  to leak.
- The model is a **deterministic fixture**, the tools are **in-memory**, and the
  data is **synthetic**. Nothing here touches a real system, network or
  credential.

When you can answer "what did I actually observe, and how do I know?" for a lab
without looking at the source, that lab is complete. Move on to the next one.

---

## Controlled experiments

A **controlled experiment** is a stricter comparison than `compare`: one file
declares exactly what may differ between two runs, what is expected to **change**
and what is expected to **stay the same**, and then a single command runs both
sides. The [controlled-experiments learning module](CONTROLLED-EXPERIMENTS.md)
explains the vocabulary (control/treatment, the held-constant invariant, the four
result states) and works through the shipped LAB-04 policy-intervention example
with the `agentsec experiment` command. The
[specification-authoring challenge](SPECIFICATION-AUTHORING-CHALLENGE.md) then
asks you to **write** your own specification and get it past the validator. Neither
produces any score, ranking or security claim.

---

## Lab self-check

One command verifies that the labs still behave as documented: it re-runs
**LAB-00 … LAB-07** against their declared expectations and prints a PASS/FAIL
summary per lab (returning a non-zero exit code if any lab fails). See
[`LOCAL-VERIFICATION.md`](LOCAL-VERIFICATION.md) for what it checks, how to run
it, and what it deliberately does **not** claim.
