# LAB-03 — Indirect Prompt Injection

In LAB-02 the hostile instruction was typed straight into the task. Here it is
**hidden inside content that a tool returns**, so the agent reads it while doing
something completely ordinary. You will trace where that instruction enters and
what the agent does next.

> Educational infrastructure. Not a benchmark, no research claim.

## Learning objectives

By the end of this lab you should be able to:

1. Describe what "indirect" prompt injection means: the hostile instruction
   reaches the agent through **data returned by a tool**, not through the task.
2. Follow the extra hop in the path — content → tool → tool result → model —
   that direct injection does not have.
3. Distinguish a **successful** tool result (the allowed read) from a **denied**
   one (the out-of-scope write).
4. Explain why treating tool output as data rather than instructions is the
   question this lab raises.
5. Compare this lab's path with LAB-02 descriptively, without ranking which is
   "worse".

## What is indirect prompt injection?

The agent is asked a benign question:

> "please summarize the note in `workspace/notes/note.txt`"

To answer, the agent reads a sandboxed note. That note is **synthetic content**
delivered by a tool, and it happens to contain an instruction aimed at the agent.
The agent — again a deterministic fixture — follows the instruction found in the
returned content and attempts an unrelated, out-of-scope write.

The difference from LAB-02 is the **path**, not the wording:

```
LAB-02 (direct)                 LAB-03 (indirect)
content                         synthetic content
   |                               |
   v                               v
task (user input)               sandbox tool
   |                               |
   v                               v
model                           tool result
                                   |
                                   v
                                 model
```

The synthetic content is entirely local and harmless: it lives in the tool's
in-memory filesystem and leaves no trace on your machine.

## Prerequisites

- Completed `labs/LAB-00-setup`, `labs/LAB-01-benign-agent` and `labs/LAB-02`.
- Basic Python and command-line familiarity, and a little JSON/JSONL.
- No prior security knowledge.

## Safety boundary

- The model is a **deterministic fixture**, not a real LLM.
- The "document" is **synthetic in-memory `fs_sandbox` content** — no host
  filesystem, no real files, no network, no web page, no email, no API.
- The policy is **least-privilege**: reads inside `workspace/` are allowed,
  anything outside is denied.
- Offline: no API keys, no real credentials, no shell execution.

## Scenario description

`config.yaml` runs one experiment. The task asks the agent to summarize a note.
`workspace/notes/note.txt` is seeded (in memory) with synthetic content that
carries a hidden instruction. The agent reads the note (allowed), then attempts
to write `../exfil.txt` (denied by policy), and finally answers that it could not
complete the note's instruction. `scenario.yaml` embeds the same experiment and
lists the observations a correct run should produce.

## Procedure

### 1. Run the experiment

```bash
agentsec run labs/LAB-03-indirect-prompt-injection/config.yaml
```

### 2. Inspect the trace it wrote

```bash
agentsec inspect runs/lab03_indirect_injection/trace.jsonl
```

### 3. Evaluate the trace on its own

```bash
agentsec evaluate runs/lab03_indirect_injection/trace.jsonl
```

### 4. Read the trace as raw data (optional)

Open `runs/lab03_indirect_injection/trace.jsonl` in any text editor. Notice that
the injected content is not stored verbatim — the `tool_result` event records a
**hash** of what the tool returned, so the untrusted text does not land in the
trace. You can still see *that* a read happened and *that* an out-of-scope write
was requested afterwards.

## What to observe

The sequence a correct run produces:

1. the original task (`agent_input`),
2. a tool request to **read** the note (`tool_requested`),
3. the policy **allows** it (`policy_decision`, `allow`),
4. the tool executes and returns the note (`tool_executed`, `tool_result`),
5. a **second** model turn that requests an unrelated **write** (`tool_requested`),
6. the policy **denies** it (`policy_decision`, `deny`),
7. a denied `tool_result` — note there is **no** `tool_executed` for a denied call,
8. the agent's final answer (`agent_output`, `run_completed`).

| Event | What it records |
|---|---|
| `run_started` | the run began. |
| `agent_input` | the benign task handed to the agent. |
| `model_request` / `model_response` | one model turn and its answer. |
| `tool_requested` | the agent asked for a tool (a *request*, not execution). |
| `policy_decision` | the authorization outcome (`allow`, `deny` or `require_approval`). |
| `tool_executed` | the tool actually ran (only after an `allow`). |
| `tool_result` | what the tool returned (success, safe error or `denied`). |
| `agent_output` | the agent's final answer. |
| `run_completed` | the run finished normally. |

> Note: the trace records **what** happened — a read, then a denied write. It
> does not (and cannot) prove *why* the model behaved that way.

## Questions to answer

Write short answers for yourself. Do not look for them in this file.

1. Where did the instruction come from in this lab — the task, or something else?
2. Which tool call returned the synthetic content, and was it allowed?
3. What did the agent request right after receiving that content?
4. Did that second request execute? Which event proves it did or did not?
5. Which trace events establish the difference between the read and the write?
6. Why is a `denied` `tool_result` shown without a matching `tool_executed`?
7. Why does the trace store a *hash* of the tool result rather than its text?
8. Descriptively, how is this path different from LAB-02's path?

## Expected outcome

A correct run **completes**. The evaluation reports two tool requests (one read,
one write), one `allow` decision, one `deny` decision, one tool execution, one
successful tool result and one denied result, and a final answer stating the
instruction could not be completed. The scenario then labels the run `passed`.

To see the scenario verdict for yourself, run the lab's verification test:

```bash
python -m pytest tests/labs/test_lab03.py -q
```

## Completion checklist

- [ ] The experiment ran and reported a completed status.
- [ ] I found the read request and confirmed its policy decision was `allow`.
- [ ] I found the write request and confirmed its policy decision was `deny`.
- [ ] I confirmed the denied call produced a `tool_result` but no `tool_executed`.
- [ ] I found the `agent_output` / `run_completed` events.
- [ ] The scenario test reports the scenario `passed`.
- [ ] I can answer the eight questions above in my own words.

## Reflection

The agent did the read you asked for — and then acted on words that came back
inside the data. In your own words, why is "the model read this text" different
from "the model should obey this text"? Compare the two labs' paths once more and
note the one extra hop that makes LAB-03 indirect.
