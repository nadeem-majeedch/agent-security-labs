# Getting Started

AgentSec Labs is a set of **eight small, offline, deterministic labs** for
learning AI-agent security by reading the traces the labs produce. You do not
need an API key, a network connection or any security background to begin.

> These labs are educational infrastructure. The model is a deterministic
> **fixture**, so what you observe is the **mechanics** of a security boundary —
> not the behaviour of a real model. They are **not a benchmark** and make **no
> research claim**. There is deliberately **no LAB-08**.

## What you need

- Python 3.11 or newer (`py` on Windows, `python` elsewhere).
- A terminal in the repository root.
- Basic familiarity with the command line and with JSON/JSONL.

## 1. Install

```bash
py -m pip install -e ".[dev]"
```

Nothing else is required: the labs run offline with the in-memory sandbox tools.

## 2. Run your first lab

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-00-setup/config.yaml
PYTHONPATH=src py -m agentsec inspect runs/lab00_setup/trace.jsonl
PYTHONPATH=src py -m agentsec evaluate runs/lab00_setup/trace.jsonl
```

The first command runs the experiment and writes a **trace**; the second lists
its events in order; the third evaluates the trace on its own — it does **not**
re-run the experiment.

## 3. Work through the labs in order

Begin with **LAB-00** and continue through **LAB-07**. The **Lab Map** describes
what each lab teaches; every lab's own page has the commands to run, the
questions to answer and a completion checklist.

## 4. Learn to read a trace

- **Understanding Traces** — an event-by-event walkthrough of the trace each lab
  actually produces, with what to look for and what the events do **not** prove.
- **Practice** — exercises where you decide, from the trace alone, whether a tool
  was requested, denied, held for approval, or actually executed.

## 5. Try a two-policy comparison

You have read one trace. The natural next question is *what changed* between two
runs. The repository ships a one-command demonstration that runs **the same lab**
— LAB-04 — under **two policies** and compares the two traces:

```bash
PYTHONPATH=src py -m agentsec demo lab04-two-policies
```

The two runs write their traces into a temporary directory that is removed when
the command finishes, so nothing is added to the repository.

1. **Run the demonstration.** It executes the LAB-04 scenario twice and prints a
   single factual, structural comparison.
2. **Observe the two policies.** Trace **A** runs under `allow_all_v1`, a
   permissive example policy; Trace **B** runs under `least_privilege_v1`, the
   policy LAB-04 ships with. The task, the mock fixture and the agent are
   identical — only the policy differs.
3. **Inspect the comparison.** It reuses the same read-only `compare` machinery
   you would use on any two traces: the event counts, the event-type
   distribution, the ordered sequence (aligned **by position only**) and the
   evaluator differences. It reports **no score** and does **not** say which
   policy is "better".
4. **Try the JSON form.** Add `--json` for one machine-readable document — the
   two policies plus the full comparison — intended for tooling:

   ```bash
   PYTHONPATH=src py -m agentsec demo lab04-two-policies --json
   ```

5. **Think about why the traces differ.** Work from the trace, not an opinion:
   - Which event types differ between the two policies?
   - What happens to the tool request under each policy?
   - Why does the comparison report positional sequence differences instead of
     assigning a score?

The scenario, the exact observables and the questions to answer are worked
through in the LAB-04 page — see **["Same lab, different policy"](LAB-04-tool-misuse/README.md#same-lab-different-policy)**.
For the command itself, `agentsec --help` and the CLI reference in
`docs/development.md` describe `compare` and `demo` in full.

> The demonstration is descriptive, not a verdict: ask *what changed* and *why*,
> not *which policy won*.

## 6. Try an approval-vs-deny comparison

The two-policy comparison above ran the same lab under two different **policy
files**. This step runs **the same LAB-05 experiment** — the same task, mock agent
and requested operation — and lets the policy answer the one request two
incompatible ways: held for approval, or refused outright.

```bash
# Trace A — LAB-05 as shipped: the read needs approval, so it is held pending
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml

# Trace B — the same lab under a deny-by-default policy
PYTHONPATH=src py -m agentsec run configs/examples/lab05_require_approval_deny_by_default.yaml

# Compare them
PYTHONPATH=src py -m agentsec compare \
  runs/lab05_require_approval/trace.jsonl \
  runs/lab05_require_approval_deny_by_default/trace.jsonl
```

1. **What is the same.** The task, the mock agent and the requested operation are
   identical in both runs.
2. **What differs.** Only the policy outcome: **approval-required**
   (`require_approval`, a *pending* result) versus **denied** (`deny`, a
   *denied* result).
3. **What never happens.** Neither run **executes** the tool — there is no
   `tool_executed` event in either trace.
4. **Read the evidence, not the prose.** Both runs end with the same final
   sentence, so tell them apart from the trace: the `policy_decision` and the
   *category* of the `tool_result`.
5. **Think it through.**
   - Which field changes between the two runs, and which do not?
   - In your own words, how is `require_approval` a different answer from `deny`?

The scenario, the exact observables and the questions to answer are worked
through in the LAB-05 page — see **["Same lab, two decisions"](LAB-05-require-approval/README.md#same-lab-two-decisions)**.

## 7. Try a cross-lab comparison

The two steps above compared runs of the **same** lab. The same `compare` tool
also accepts traces from **different** labs — but only if you read it for what it
is. Run the two introductory labs and compare them:

```bash
# Trace A — LAB-01, a benign, authorized request
PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml

# Trace B — LAB-02, a request with a hostile instruction injected into it
PYTHONPATH=src py -m agentsec run labs/LAB-02-direct-prompt-injection/config.yaml

# Compare them
PYTHONPATH=src py -m agentsec compare \
  runs/lab01_benign/trace.jsonl \
  runs/lab02_direct_injection/trace.jsonl
```

1. **Inspect event counts and the distribution.** Both runs have the same number
   of events, and the same event types in the same order.
2. **Inspect the sequence.** `compare` reports the event sequences as
   **identical** — and it aligns events *by position only*.
3. **Inspect the evaluator differences.** It reports **none**: the same one
   `allow`, the same executed tool, the same successful result, no denials.
4. **Explain what this does *not* establish.** Identical structure does **not**
   mean the two runs are the same. LAB-02 pasted a hostile instruction into the
   task; that difference lives in the **content** of `agent_input` and of the
   agent's output — content `compare` deliberately does **not** diff. A
   structural comparison is content-blind, so "no structural difference" is not
   "no security difference."
5. **Reflect.**
   - What changed between the two runs, and why is it invisible to `compare`?
   - Why does `compare` refuse to align events semantically?
   - If two traces look structurally identical, what would you read next to tell
     them apart?

Both labs are worked through on their own pages — see
**[LAB-01](LAB-01-benign-agent/README.md)** and
**[LAB-02](LAB-02-direct-prompt-injection/README.md)**. For the command itself,
`docs/development.md` documents `compare` in full.

## 8. Compare two labs that differ

The step above ended in a comparison with **no** structural difference. Here is
the complementary case — two labs whose traces genuinely differ. Run LAB-01
again, this time alongside LAB-05:

```bash
# Trace A — LAB-01, an authorized calculator request that executes
PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml

# Trace B — LAB-05, a database read held for approval, never executed
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml

# Compare them
PYTHONPATH=src py -m agentsec compare \
  runs/lab01_benign/trace.jsonl \
  runs/lab05_require_approval/trace.jsonl
```

1. **Inspect event counts and the distribution.** Trace A has one more event — a
   `tool_executed` (`tool_executed  A 1  B 0`). Trace B never ran its tool.
2. **Inspect the sequence.** The extra event shifts every later position, so
   `compare` reports a chain of positional differences and one event *only in A*.
   Alignment is **by position only** — it is not a claim that index 6 "means" the
   same thing in both runs.
3. **Inspect the evaluator differences.** A was `allow`ed and executed
   (`tool_results.ok`); B was held as `require_approval`
   (`tool_results.pending_approval`). The requested tools differ as well.
4. **What this establishes.** With different operations and outcomes, `compare`
   surfaces real structural differences: a count delta, changed event types, a
   positional shift, and differing evaluator fields.
5. **What it does not establish.** It stays descriptive: it names *what* changed,
   never *why*, and never *which run is better*. Read the *why* from the lab
   pages and the trace itself.
6. **Reflect.**
   - Which single event explains the count difference, and where does it sit?
   - Why is "aligned by position only" more honest than guessing an alignment?
   - What do the evaluator differences say about the two operations?

Both labs are explained on their own pages — see
**[LAB-01](LAB-01-benign-agent/README.md)** and
**[LAB-05](LAB-05-require-approval/README.md)**.

## 9. Check your setup stays healthy

```bash
PYTHONPATH=src py -m agentsec labs check
```

This re-runs every lab and confirms each still produces its declared result. See
**Local Verification** for what it checks and what it deliberately does not.

## The one habit to build

The goal of the whole sequence is to answer a single question **with evidence**:

> **"What can I actually observe in the trace?"**

Keep four things separate as you read — **what was requested**, **what was
decided**, **what executed**, and **what changed** — and name the event that
supports each claim.
