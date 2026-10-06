# LAB-01 — Observe a Benign Agent

Before studying attacks and defences you need to know what **normal** looks
like. In this lab a cooperative, deterministic agent answers a harmless
question and uses exactly one sandboxed tool. Nothing here is adversarial.

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Describe the basic agent lifecycle: task → model → tool call → policy
   decision → tool execution → tool result → final answer.
2. Find a tool **request** in a trace and tell it apart from actual **tool
   execution**.
3. Locate the **policy decision** for a tool call and see that it was allowed.
4. Explain how the agent produced its final answer.
5. Read a basic descriptive evaluation of a run.

## Prerequisites

- Completed `labs/LAB-00-setup`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety

- The model is a **deterministic fixture**, not a real LLM.
- The tool is the **sandboxed calculator** (arithmetic only, no `eval`).
- The policy is **least-privilege**: the calculator is allowed, everything else
  is denied.
- Offline: no network, no API keys, no real files, no real database.

## What this lab contains

| File | Purpose |
|---|---|
| `config.yaml` | The experiment to run with the CLI. |
| `scenario.yaml` | The same experiment plus the **expected observations**. |
| `README.md` | This guide. |

`scenario.yaml` is read-only: it lists what a correct run should show. The
scenario's expectation is machine-checked by a test (see *Expected outcome*).

## Procedure

### 1. Run the experiment

```bash
agentsec run labs/LAB-01-benign-agent/config.yaml
```

### 2. Inspect the trace it wrote

```bash
agentsec inspect runs/lab01_benign/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
agentsec evaluate runs/lab01_benign/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab01_benign/trace.jsonl` in any text editor. Each line is one JSON
event; read them top to bottom.

## What to look for

**In the terminal output** (steps 1 and 3): the agent status is `completed`, the
evaluation status is `completed`, and the summary lists one tool call, one
policy decision and one tool result.

**In the trace** (steps 2 and 4): the events appear in a sensible order and each
one links back to the event that caused it via `parent_event_id`. The important
event types for this lab are:

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the task handed to the agent. |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool (a *request*, not execution). |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (this only happens after an allow). |
| `tool_result` | what the tool returned (success or a safe error). |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

## Questions to answer

Write short answers for yourself:

1. What caused the tool request to happen?
2. Where exactly is the policy decision recorded, and what was the outcome?
3. How can you tell that the tool **actually executed** rather than only being
   requested?
4. Which event carries the tool's returned value?
5. What indicates the agent produced a final answer?
6. Why is the trace useful when something goes wrong, or when an agent behaves
   unexpectedly?

## Expected outcome

A correct run **completes** after exactly one model-driven tool call to the
calculator, the policy **allows** it, the tool executes once, and the agent
answers with the sum. The evaluation reports one tool call, one `allow`
decision and one successful tool result, with no denials. The scenario then
labels the run `passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
python -m pytest tests/labs/test_lab01.py -q
```

`scenario.yaml` records the exact expectations; the test runs the experiment
and checks that every expectation was met.

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I found the `tool_requested` event and the separate `tool_executed` event.
- [ ] I found the `policy_decision` event and read its `allow` outcome.
- [ ] I found the `tool_result` event with the tool's returned value.
- [ ] I found the `agent_output` / `run_completed` events.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the six questions above in my own words.
