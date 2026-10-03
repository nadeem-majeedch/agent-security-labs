# LAB-05 — Require Approval / Human-in-the-Loop

The previous labs showed two policy outcomes: a request the policy **allows** and
a request the policy **denies**. There is a third, easy-to-miss outcome. Some
actions are not refused — they are simply **not authorized yet**, and they wait
for a human to say yes. In this lab a perfectly legitimate request lands in
exactly that state, and you will see that it never executes on its own.

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Name all three policy decisions: `allow`, `deny` and `require_approval`.
2. Explain that `require_approval` is **not** rejection: the request is still
   under consideration, but authorization has not been granted.
3. Show that a `require_approval` call produces a **pending** result and **no**
   `tool_executed` event.
4. Restate why `tool_requested` does **not** mean `tool_executed`.
5. Tell the difference between a request that is **inappropriate** (LAB-04 →
   `deny`) and one that is **legitimate but sensitive** (this lab →
   `require_approval`).

## What is the approval boundary?

The agent is asked something ordinary and completely in-scope:

> "please review the project notes and tell me what they say"

To answer, the agent asks the in-memory synthetic database for the notes. The
request is a valid, appropriately-scoped read — nothing is wrong with it. Yet the
least-privilege policy returns:

```
require_approval
```

That means: *this is not forbidden, but it must not happen without a human
authorization step.* No approval is granted in this lab, so the call stays
**pending** and the tool never runs. The agent then reports that it is waiting.

Three decisions, three outcomes:

| Decision | Meaning | Tool executed? |
|---|---|---|
| `allow` | Authorized | Yes |
| `deny` | Rejected | No |
| `require_approval` | Waiting for authorization (not rejected) | No |

### How this differs from LAB-04

LAB-04 and LAB-05 both end with a call that does **not** execute, but for
opposite reasons:

```
LAB-04  inappropriate operation            -> deny             -> not executed
LAB-05  legitimate operation needing a yes -> require_approval -> not executed (yet)
```

`deny` says "no". `require_approval` says "not without authorization". This lab
adds **no** injected instruction, **no** malicious content, **no** misuse and
**no** exploit — the only new idea is the third decision.

## Prerequisites

- Completed `labs/LAB-00-setup` … `labs/LAB-04-tool-misuse`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety boundary

- The model is a **deterministic fixture**, not a real LLM.
- The tool is the **in-memory synthetic database** (`mock_db`); it is read-only
  by default and seeded with fake rows. It never touches a real database.
- No real approval system, no UI, no network, no external identity, no
  authentication. The approval boundary is simulated purely through the existing
  policy engine — nothing is actually authorized in this lab.
- Offline: no network, no API keys, no real files, no host filesystem, no shell,
  no real credentials.

## Scenario description

`config.yaml` runs one experiment. The task asks the agent to review the notes.
The mock agent requests a `mock_db` read (`SELECT note FROM notes`). The policy's
existing `db-read-requires-approval` rule answers `require_approval`, so the call
is held pending and never executes; the agent then answers that it is waiting.
`scenario.yaml` embeds the same experiment and lists the observations a correct
run should produce.

## Procedure

### 1. Run the experiment

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml
```

### 2. Inspect the trace it wrote

```bash
PYTHONPATH=src py -m agentsec inspect runs/lab05_require_approval/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
PYTHONPATH=src py -m agentsec evaluate runs/lab05_require_approval/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab05_require_approval/trace.jsonl` in any text editor. Find the
`policy_decision` line and read `decision` (`require_approval`) and
`matched_rule`. Then confirm there is **no** `tool_executed` line for that call,
and that its `tool_result` carries an approval-required error.

## What to observe

The sequence a correct run produces:

1. the original task (`agent_input`),
2. the agent's tool request (`tool_requested`),
3. the policy decision (`policy_decision`, `require_approval`),
4. a **pending** `tool_result` — and **no** `tool_executed`,
5. the agent's final answer (`agent_output`, `run_completed`).

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the benign task handed to the agent. |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool (a *request*, not execution). |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (only after an `allow`). |
| `tool_result` | what the tool returned (success, safe error, `denied`, or `pending_approval`). |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

> Note: the trace records **what** the policy decided and whether the tool ran.
> It does not grant approval and it does not prove *why* the agent asked.

## Questions to answer

Write short answers for yourself. Do not look for them in this file.

1. What tool did the agent request, and what did it ask to read?
2. Was the request denied? Which event and which field tell you?
3. Which decision was recorded, and which policy rule matched?
4. Did the tool execute? Which event proves it did or did not?
5. How is `require_approval` different from `deny`, in your own words?
6. Why is `tool_requested` not the same as `tool_executed`?
7. In LAB-04 the call was denied; here it is pending. What makes the *operation*
   different, even though neither executed?
8. Who or what would have to happen for this pending call to become an execution?

## Expected outcome

A correct run **completes**. The evaluation reports one tool request, **zero**
tool executions, one `require_approval` decision, zero denials, and one pending
tool result, with a final answer saying the read is waiting for approval. The
scenario then labels the run `passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
PYTHONPATH=src py -m pytest tests/labs/test_lab05.py -q
```

## Same lab, two decisions

The policy is the only thing that decides *how* this request is answered. The
cleanest way to see that is to run **this same lab** under a second policy that
refuses the request outright, then compare the two traces.

The repository ships a deny-by-default example policy,
`policies/examples/deny_by_default.yaml`, and a ready-made config that runs **this
same LAB-05 experiment** with it — the same `experiment_id`, task, mock fixture
and agent; only the `policy_path` and the output `trace_path` differ:

```bash
# Trace A — the lab as shipped, under the least-privilege policy
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml

# Trace B — the same lab under a deny-by-default policy
PYTHONPATH=src py -m agentsec run configs/examples/lab05_require_approval_deny_by_default.yaml

# Compare them
PYTHONPATH=src py -m agentsec compare \
  runs/lab05_require_approval/trace.jsonl \
  runs/lab05_require_approval_deny_by_default/trace.jsonl
```

Read the comparison and look for the two events that carry the difference:

* **`policy_decision`** — `require_approval` in A (matched by the
  `db-read-requires-approval` rule) versus `deny` in B (no rule matched, so the
  deny-by-default policy refused it).
* **`tool_result`** — A records a **pending** result (its `error` reads
  `approval required: …`), B records a **denied** result
  (`error: denied: …`). Neither trace contains a `tool_executed` event.

The evaluator differences name exactly these:

```text
decisions.deny:                0 -> 1
decisions.require_approval:    1 -> 0
tool_results.denied:           0 -> 1
tool_results.pending_approval: 1 -> 0
```

### The distinction is not in the agent's prose

Both runs finish with the **same** final answer. The mock fixture reacts to *any*
failed tool result, and both a pending result and a denied result are failures,
so the agent says it is waiting either way. Do **not** try to tell the two runs
apart by their last sentence — it is identical. The difference lives in the
trace: the **policy decision** and the resulting **tool-result category**. Read
the `policy_decision` and `tool_result` events, not the agent's closing line.

> `require_approval` means "not without a yes"; `deny` means "no". Both leave the
> tool unexecuted — but they are different answers, and only the trace shows
> which one the policy gave.

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I found the `tool_requested` event and read what it asked for.
- [ ] I confirmed the policy decision was `require_approval` (not `allow`/`deny`).
- [ ] I confirmed the call produced a `tool_result` but **no** `tool_executed`.
- [ ] I found the `agent_output` / `run_completed` events.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the eight questions above in my own words.

## Reflection

Not every blocked action is forbidden. In your own words, why does
"`require_approval`" carry a different message than "`deny`", even though the
tool runs in neither case? Then compare LAB-04 and LAB-05 once more: same
observable outcome (nothing executed), two different decisions — and say which
laboratory taught you which.
