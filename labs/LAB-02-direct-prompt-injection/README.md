# LAB-02 — Direct Prompt Injection

An agent only behaves well if you can tell **instructions you meant** apart from
**instructions that arrived as part of the input**. In this lab a hostile
instruction is pasted *directly* into the agent's task, and you watch the trace
to see what the agent actually did.

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Identify the trusted **task context** and the untrusted **instruction** inside
   one agent input.
2. Describe what "direct" prompt injection means: the hostile instruction enters
   the agent straight from its task input.
3. Trace what the agent requested, what the policy decided, and whether the tool
   actually executed.
4. Explain why the trace records *what* happened and not *why*.
5. Compare this lab's path with LAB-03, where the instruction arrives through
   data returned by a tool instead.

## What is direct prompt injection?

The agent receives a single input that mixes two things:

- a harmless request ("write a welcome message"), and
- an instruction the operator never gave ("IGNORE ALL PREVIOUS INSTRUCTIONS …").

Because both arrive as ordinary text in the same turn, the agent has no built-in
way to know which words are its real task and which are content that merely
*looks like* a command. Here the deterministic mock follows the injected
instruction and performs an unrelated (but completely harmless) sandbox
operation.

This lab is **descriptive**: it shows the path the instruction took. It does not
introduce a detector, a filter or any defence.

## Prerequisites

- Completed `labs/LAB-00-setup` and `labs/LAB-01-benign-agent`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety boundary

- The model is a **deterministic fixture**, not a real LLM.
- The tool is the **sandboxed calculator** (arithmetic only, no `eval`).
- The policy is **least-privilege**: the calculator is allowed, everything else
  is denied.
- Offline: no network, no API keys, no real files, no real database, no host
  filesystem, no shell, no real credentials. Nothing here discloses anything.

## Scenario description

`config.yaml` runs one experiment. The task contains a benign request plus an
injected line. The mock agent ignores the benign request, asks the calculator
for `6 * 7`, the policy allows it, the tool executes, and the agent answers with
the redirected result. `scenario.yaml` embeds the same experiment and lists the
observations a correct run should produce.

## Procedure

### 1. Run the experiment

```bash
agentsec run labs/LAB-02-direct-prompt-injection/config.yaml
```

### 2. Inspect the trace it wrote

```bash
agentsec inspect runs/lab02_direct_injection/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
agentsec evaluate runs/lab02_direct_injection/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab02_direct_injection/trace.jsonl` in any text editor. Each line is
one JSON event; read them top to bottom and notice where the injected line sits.

## What to observe

- The `agent_input` event contains the **whole** task — the benign request *and*
  the injected instruction sitting side by side. Nothing marks one as data.
- The first `model_response` is a **tool call**, even though the benign request
  never asked for arithmetic.
- The `policy_decision` for that call is `allow`, and a separate `tool_executed`
  event shows the tool really ran.
- The final `agent_output` answers the injected instruction, not the benign one.

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the task handed to the agent (benign request + injected instruction). |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool (a *request*, not execution). |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (only after an `allow`). |
| `tool_result` | what the tool returned (success or a safe error). |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

## Questions to answer

Write short answers for yourself. Do not look for them in this file.

1. Which part of `agent_input` was the trusted task context?
2. Which part was the untrusted instruction?
3. What did the model request after reading the injected instruction?
4. Did the policy allow the requested action?
5. Did the tool actually execute? Which event proves it?
6. Which trace events establish your answers to the previous two questions?
7. Why is "tool requested" different from "tool executed"?
8. Does the trace prove the model's internal reasoning? Why or why not?

## Expected outcome

A correct run **completes**. The evaluation reports one tool request, one
`allow` decision, one tool execution and one successful tool result, with no
denials, and the agent's final answer reflects the injected instruction. The
scenario then labels the run `passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
python -m pytest tests/labs/test_lab02.py -q
```

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I located the injected instruction inside `agent_input`.
- [ ] I found the `tool_requested` event and the separate `tool_executed` event.
- [ ] I found the `policy_decision` event and read its `allow` outcome.
- [ ] I found the `tool_result` event.
- [ ] I found the `agent_output` / `run_completed` events.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the eight questions above in my own words.

## Reflection

In one or two sentences: the agent saw one input that mixed a real request with
an instruction the operator did not intend. In your own words, why is it hard for
the agent to know which is which — and why does the *trace*, rather than the
output alone, help you reason about it? Then think about how LAB-03 changes the
path by which the instruction arrives.
