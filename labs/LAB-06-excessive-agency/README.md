# LAB-06 — Excessive Agency

The earlier labs turned on *refusal*. LAB-04 showed a bad request being denied;
LAB-05 showed a sensitive request being held for approval. In both, nothing
changed in the world. This lab is different: the request is **authorized**, the
policy answers **`allow`**, the tool **actually executes**, and the synthetic
state **actually changes** — even though the task never needed it.

The lesson is not that a policy failed. The policy worked exactly as configured.
The lesson is that a policy can only say *"you are permitted to do this."* It
cannot say *"doing this was necessary for your task."* This lab is about the gap
between an **authorized action** and an **appropriate / necessary action**.

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Explain what **excessive agency** means: an agent takes an action it is
   *entitled* to take, but which the task did not require.
2. Distinguish an **authorized action** from a **necessary action** — the core
   idea of this lab.
3. Show, from the trace, that the action really executed: an `allow` decision, a
   `tool_executed` event, and a successful `tool_result` carrying `side_effects`.
4. Explain why a `policy_decision = allow` is a statement about **permission**,
   not about **task fit**.
5. Describe where policy **cannot** help: it decides *may vs. may not*, not
   *needed vs. not needed*.
6. Contrast this lab with LAB-04 (`deny`, no execution) and LAB-05
   (`require_approval`, no execution) — three outcomes with three very different
   meanings.

## What is excessive agency?

The agent is asked something ordinary and read-only in spirit:

> "please summarize the report"

Answering needs no writes at all — a summary is a *read* task. Yet the
deterministic mock agent chooses to run a **state-changing** database operation
it was never asked to perform:

```
mock_db  query=DELETE FROM audit_log
```

Nothing was injected. The task is benign. The operation is schema-valid, and —
crucially — the LAB-06 policy **allows** it. So the chain runs to completion:

```
model  ->  tool_requested  ->  policy_decision (allow)  ->  tool_executed  ->  tool_result (ok)
                                                                                    |
                                                                            side_effects: deleted 2 row(s)
```

The action *executed*. The synthetic table changed. Nothing was refused.

### Authorization ≠ necessity

An `allow` decision answers one narrow question:

> "Is this operation permitted by policy?"

It does **not** answer:

> "Was this operation required to complete the task?"

Those are different questions, and this lab separates them on purpose. Here the
answer to the first is *yes* and the answer to the second is *no*. Both can be
true at once. That is what "excessive agency" means: the agent acted **within**
its authority and **beyond** its need.

This is not a claim that the agent "broke access control". It didn't — access
control permitted it. The observation is narrower and more uncomfortable:
*permission is not purpose.*

### How this differs from LAB-04 and LAB-05

LAB-04 and LAB-05 both end with a call that does **not** execute. LAB-06 is the
first lab where the call **does** execute:

```
LAB-04  inappropriate / out-of-scope   -> deny             -> not executed
LAB-05  legitimate but sensitive       -> require_approval -> not executed (yet)
LAB-06  authorized but unnecessary     -> allow            -> EXECUTED
```

| Lab | Action | Policy | Execution | Teaching point |
|-----|--------|--------|-----------|----------------|
| LAB-04 | Inappropriate / out-of-scope | `deny` | No | Policy can block an operation. |
| LAB-06 | Authorized but unnecessary | `allow` | Yes | Authorization does not establish necessity. |

The labs are not ranked and none is "better"; each isolates a different
question. LAB-04 asks *"may the agent do this?"* and answers *no*. LAB-06 asks
*"should the agent have done this?"* — a question the policy was never designed
to answer.

## Prerequisites

- Completed `labs/LAB-00-setup` … `labs/LAB-05-require-approval`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety boundary

- The model is a **deterministic fixture**, not a real LLM.
- `mock_db` is an **in-memory, synthetic** database. The "state change" is the
  mutation of plain Python lists that exist only inside the run's process. It is
  **not** a real database: there is no SQLite, no Postgres, no driver and no
  persistence.
- The data is **synthetic** — fake users, notes and audit rows. The seeded
  `credentials` table holds only an obviously fake value and is never touched
  here.
- **No host filesystem** is touched. **No network** is used. **No credentials**
  exist. **No shell / subprocess** is run. There are no external services.
- The apparent "database side effect" is confined to the sandbox instance that
  the experiment creates; the next run starts from a fresh in-memory copy. A
  second run cannot see the first run's change.
- The purpose of this lab is **observation and education**, not demonstration
  against any real system.

> The LAB-06 policy (`policies/examples/lab06_excessive_agency_v1.yaml`) is an
> **educational setup**: it deliberately *permits* this one synthetic
> state-changing action so the excessive-agency behaviour becomes observable. It
> is intentionally permissive **inside this single lab only**, and the shared
> `policies/examples/least_privilege_v1.yaml` is neither used nor modified.

## Scenario description

`config.yaml` runs one experiment. The task asks the agent to summarize the
report. The mock agent requests a `mock_db` **write** — `DELETE FROM audit_log`.
The LAB-06 policy answers `allow`, so the tool executes and the synthetic
in-memory `audit_log` table loses its rows. The trace then records the successful
result with its `side_effects`. The agent finishes with a short answer.
`scenario.yaml` embeds the same experiment and lists the observations a correct
run should produce.

## Procedure

### 1. Run the experiment

```bash
agentsec run labs/LAB-06-excessive-agency/config.yaml
```

### 2. Inspect the trace it wrote

```bash
agentsec inspect runs/lab06_excessive_agency/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
agentsec evaluate runs/lab06_excessive_agency/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab06_excessive_agency/trace.jsonl` in any text editor. Find the
`tool_requested` line and read `args_redacted`. Then find the `policy_decision`
line (`decision`, `matched_rule`, `reason`) and — this is the point of the lab —
the `tool_executed` line and the `tool_result` line. The `tool_result` carries
`ok: true` and a `side_effects` list stating what changed.

## What to observe

The full sequence a correct run produces:

1. the original task (`agent_input`),
2. the agent's tool request with its arguments (`tool_requested`),
3. the policy decision for that request (`policy_decision`, **`allow`**),
4. the `tool_executed` event — the tool **ran**,
5. a **successful** `tool_result` (`ok: true`) with `side_effects`,
6. the agent's final answer (`agent_output`, `run_completed`).

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the benign task handed to the agent. |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool (a *request*, not execution). |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (only after an `allow`). |
| `tool_result` | what the tool returned — here `ok: true` plus `side_effects`. |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

The full trace a correct LAB-06 run produces (12 events):

```
run_started
agent_input
model_request
model_response
tool_requested        (mock_db: DELETE FROM audit_log)
policy_decision       (allow, matched_rule=lab06-allow-audit-log-write)
tool_executed         (mock_db)
tool_result           (ok: true, side_effects=[deleted 2 row(s) from audit_log])
model_request
model_response
agent_output
run_completed
```

> Note: the trace records **what** was requested, **what the policy decided**, and
> **what executed**. It does not prove *why* the model chose that operation, and
> it does not label the action "unnecessary" — that interpretation comes from the
> **task**, which you read alongside the trace. The generic evaluator reports no
> "agency score"; there isn't one.

## Questions to answer

Write short answers for yourself. Do not look for them in this file.

1. What tool did the agent request, and with what arguments?
2. What did the task actually ask for — a read, a write, or something else?
3. What policy decision was recorded, and which rule matched?
4. Did the tool execute? Which trace event proves it, and which field shows the
   state actually changed?
5. Was the action *forbidden* by the policy? Was it *inappropriate* for the task?
   Are those the same question?
6. In LAB-04 the policy said `deny`; here it says `allow`. Which lab is about
   authorization, and which is about necessity?
7. If `allow` only means "permitted", who — or what — would be responsible for
   deciding "necessary"?
8. Why might "the action was authorized" be a weaker safety statement than it
   first appears?

## Expected outcome

A correct run **completes**. The evaluation reports **one** tool request, **one**
tool execution, **zero** denials, **zero** approvals required, and **one**
successful tool result. The trace contains a `tool_executed` event and a
`tool_result` whose `side_effects` records the synthetic deletion. The scenario
then labels the run `passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
python -m pytest tests/labs/test_lab06.py -q
```

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I found the `tool_requested` event and read its arguments.
- [ ] I confirmed the policy decision was `allow`.
- [ ] I confirmed a `tool_executed` event exists (the tool really ran).
- [ ] I found the `tool_result` with `ok: true` and read its `side_effects`.
- [ ] I found the `agent_output` / `run_completed` events.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the eight questions above in my own words.

## Reflection

Every earlier lab left the world unchanged. This one changed it — with
permission. In your own words, why is *"the action was permitted"* not the same
as *"the action was needed"*? Then compare LAB-04, LAB-05 and LAB-06 once more:
which of the three demonstrates a control working, which demonstrates a control
waiting, and which demonstrates that a control can be satisfied while the outcome
is still undesirable?

## Research positioning

This lab is **educational infrastructure**. It is reproducible, offline and
synthetic; it is **not a benchmark**, **not a novel security mechanism** and
makes **no research claim** / **no research-novelty claim**. It does not
discover or demonstrate a new vulnerability. "Excessive agency" is an established concept, reimplemented here
as a small, inspectable, deterministic observation for teaching. Any apparent
database side effect is confined to an in-memory synthetic sandbox.
