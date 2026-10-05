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

Begin with **LAB-00** and continue through **LAB-07**. The
**[Lab Map](README.md)** describes what each lab teaches; every lab's own page
has the commands to run, the questions to answer and a completion checklist.

## 4. Learn to read a trace

- **[Understanding Traces](TRACE-WALKTHROUGHS.md)** — an event-by-event
  walkthrough of the trace each lab actually produces, with what to look for and
  what the events do **not** prove.
- **[Practice](TRACE-READING-EXERCISES.md)** — exercises where you decide, from
  the trace alone, whether a tool was requested, denied, held for approval, or
  actually executed.

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

## 9. Predict before you run

Every step so far looked at a trace **after** it existed. This one reverses the
order: state what you expect **before** you look. A *prediction* is a small YAML
document of observable expectations — the same vocabulary a lab's own
`scenario.yaml` uses — checked against a trace with `agentsec predict`.

```bash
# 1. Run the lab, producing its trace.
PYTHONPATH=src py -m agentsec run labs/LAB-04-tool-misuse/config.yaml

# 2. Check your prediction against that trace.
PYTHONPATH=src py -m agentsec predict \
  runs/lab04_tool_misuse/trace.jsonl \
  configs/predictions/lab04.yaml
```

`configs/predictions/lab04.yaml` predicts the boundary this lab teaches: the
out-of-scope write is **denied**, so nothing **executes** and the tool result is
`denied`.

1. **Read the lab, then predict.** From the LAB-04 description, write down which
   policy decision you expect, whether the tool should execute and what state the
   tool result will be in — *before* you run anything.
2. **Run, then check.** `agentsec run` produces the trace; `agentsec predict`
   compares it against your prediction and prints each field as `predicted` /
   `observed` / `MATCH` or `MISMATCH`.
3. **Try a wrong prediction on purpose.** `configs/predictions/lab04_mismatch.yaml`
   deliberately expects `tool_executions: 1`. The output shows a clean mismatch —
   the denied call never ran. A mismatch is **not a failure**; it is exactly the
   signal that your prediction did not match the trace.
4. **Predict the injection lab — and be surprised.**
   `configs/predictions/lab02_expect_denied.yaml` guesses that a hostile
   instruction is refused. It is not: run LAB-02 and check. Report the mismatch
   rather than assuming.
5. **Check a few other kinds of outcome.** Each document below is a plain
   expectation in the same vocabulary as a lab's own `scenario.yaml` `expected`
   block, matched with the same rules. Run the lab it names, then predict:

   - `configs/predictions/lab05_expect_approval.yaml` — the **approval** case:
     LAB-05's database read is held `pending_approval` and never executed.
     `configs/predictions/lab05_expect_denied.yaml` deliberately predicts a
     *denial* instead, so you can see an approval-vs-denial guess mismatch.
   - `configs/predictions/lab03_expect_allowed_then_denied.yaml` — one run with
     **both** an allowed-and-executed request and a denied one.
   - `configs/predictions/lab07_expect_two_tools.yaml` — **two different tools**
     (`mock_db` and `mock_email`), both allowed and executed.
6. **Reflect.**
   - Which expectation was hardest to predict before reading the trace, and why?
   - When your prediction matched, what did that *actually* establish?
   - When it clashed, was the prediction wrong or the trace surprising?
   - How is predicting against one trace different from *comparing* two?

> A prediction match does **not** establish security, correctness or
> effectiveness; it only means the trace agreed with the fields you named. A
> mismatch is not a failed experiment — it is an observation that your prediction
> did not match the trace.

The lab itself is worked through on its own page — see
**[LAB-04-tool-misuse](LAB-04-tool-misuse/README.md)**. The prediction document
format and the `predict` command are described in the CLI reference in
`docs/development.md`.

## 10. Predict → Run → Compare → Interpret

The steps above each use **one** command. This one composes three you have
already met — `run`, `predict` and `compare` — into a single workflow: state an
expectation, produce a trace, check the expectation, then compare that trace with
another. Nothing new is executed and no new file is needed; it reuses the
LAB-01/LAB-05 pair from step 8 and an existing prediction.

### A. Predict

Read the expectation *before* running anything.
`configs/predictions/lab05_expect_approval.yaml` expects LAB-05's database read
to be **held** `require_approval` — never denied, never executed. That is a claim
about the trace, not a score.

### B. Run

```bash
# Trace A — LAB-01, an authorized calculator request that executes
PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml

# Trace B — LAB-05, a database read held for approval, never executed
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml
```

### C. Verify

```bash
PYTHONPATH=src py -m agentsec predict \
  runs/lab05_require_approval/trace.jsonl \
  configs/predictions/lab05_expect_approval.yaml
```

`predict` prints each field as `predicted` / `observed` / `MATCH` or `MISMATCH`.
Here every field matches; if one did not, that mismatch is an experimental
result, not a failure.

### D. Compare

```bash
PYTHONPATH=src py -m agentsec compare \
  runs/lab01_benign/trace.jsonl \
  runs/lab05_require_approval/trace.jsonl
```

### E. Interpret

Work from the output, not an opinion:

1. Did the observed trace match the prediction, and which field decided it?
2. Which structural differences does `compare` report between the two traces?
3. Which differences are directly evidenced by the traces, and which are only
   positional?
4. What would be unjustified to conclude from this comparison alone?

> **What each step establishes.** A prediction match means only that the trace
> agreed with the fields you named. A comparison means only that two traces
> differ structurally under the existing position-only alignment. **Neither**
> establishes causality, which lab or policy is better, which is safer, or *why*
> the agent behaved as it did. You are reading evidence, not a verdict.

**Common misreadings.** Two conclusions feel natural here, and neither is
established by this exercise:

- **"LAB-01 is the better/safer run."** The comparison is descriptive: it reports
  observed structural differences between two traces. It produces no security
  ranking and cannot establish which run is better or safer.
- **"The prediction match proves the run is secure."** A match only means the
  observed trace agreed with the observations you explicitly predicted. It does
  not establish overall security, safety or correctness, and it does not show
  that no vulnerability exists.

The two labs are worked through on their own pages — see
**[LAB-01](LAB-01-benign-agent/README.md)** and
**[LAB-05](LAB-05-require-approval/README.md)**. The `predict` and `compare`
commands are documented in the CLI reference in `docs/development.md`.

## 11. Predict a difference before comparing

The last step predicted **one** trace, then compared two. This one reverses the
order once more: write down how you expect **two runs to differ** *before* you
look at the comparison. The pair is LAB-04 run under two policies — the same lab
from step 5, but now read through `compare`.

### Weak and useful predictions

> **Weak:** "the two traces will be different." It is true but unfalsifiable — no
> observation could contradict it.

> **Useful:** "one trace will have a field the other lacks, or an evaluator count
> will differ by a specific amount." It names an observable difference you can
> check against the actual output, and it commits to no cause and no ranking.

A prediction is worth writing only if the comparison could **disprove** it.

### A. Predict

Before running anything, answer in your own words:

1. Which run do you expect to **allow** the request, and which to **deny** it?
2. Will the tool **execute** in both runs, in one, or in neither?
3. Will the two traces have the **same number of events**?
4. Which **evaluator differences** do you expect (`decisions.*`, `tool_results.*`)?

### B. Run

```bash
# Trace A — LAB-04 under a permissive policy (allow_all_v1)
PYTHONPATH=src py -m agentsec run configs/examples/lab04_tool_misuse_allow_all.yaml

# Trace B — the same lab under its shipped least-privilege policy
PYTHONPATH=src py -m agentsec run labs/LAB-04-tool-misuse/config.yaml
```

### C. Compare

```bash
PYTHONPATH=src py -m agentsec compare \
  runs/lab04_tool_misuse_allow_all/trace.jsonl \
  runs/lab04_tool_misuse/trace.jsonl
```

### D. Verify

Check each predicted field against the comparison output, and record whether the
observed difference matches your prediction:

- the **event counts** and the count delta;
- the **event-type distribution** (which event types differ, and by how many);
- the **sequence** differences (aligned by position only);
- the **evaluator differences** (`decisions`, `tool_results`).

You can also confirm each side on its own — the shipped prediction
`configs/predictions/lab04.yaml` describes the least-privilege trace:

```bash
PYTHONPATH=src py -m agentsec predict \
  runs/lab04_tool_misuse/trace.jsonl \
  configs/predictions/lab04.yaml
```

### E. Interpret

- Which of your predictions were **correct**, and which were **wrong**?
- Which **evidence** in the comparison supports each conclusion?
- What does the comparison **still not establish**?

> **Two boundaries to keep.** A correct prediction does **not** prove causality —
> it shows the traces matched what you expected, not *why*. And a structural
> difference does **not** by itself establish which run is better, safer or more
> secure; `compare` is descriptive and produces no ranking.

LAB-04 is worked through on its own page — see
**[LAB-04-tool-misuse](LAB-04-tool-misuse/README.md)** — and the `compare` and
`predict` commands are documented in the CLI reference in `docs/development.md`.

> **Output and cleanup.** Running the example config writes
> `runs/lab04_tool_misuse_allow_all/trace.jsonl`, which sits under the untracked
> `runs/` directory. When you have finished, remove it with
> `rm -rf runs/lab04_tool_misuse_allow_all`.

### Going further: adjudicate competing claims

The steps above ask you to write **one** prediction and compare. The next thing a
reader can practise is harder: taking a mixed set of *competing statements* about
two runs and deciding **what kind of statement each one is** — a prediction, an
observation, a bounded interpretation, or a claim the evidence cannot support —
and justifying each decision from the trace.

That is the **claim-adjudication** exercise, not another comparison:
[`PREDICTION-ADJUDICATION-CHALLENGE.md`](PREDICTION-ADJUDICATION-CHALLENGE.md)
uses the LAB-05 approval-vs-deny pair you met in step 6 and the prediction and
comparison commands you have just used.

### Going further: run a controlled experiment end to end

Everything above compares two runs you produced **separately**. The next step is
stricter: declare, in advance and in one file, that *only one thing* may differ
between the two runs, state what you expect to **change** and what you expect to
**stay the same**, then let a single command run both sides and report the result.
That is a **controlled experiment**, and it is taught in the
[controlled-experiments learning module](CONTROLLED-EXPERIMENTS.md) with the
`agentsec experiment` command and a worked LAB-04 example.

Once you can read a specification and run it, the next step is to **write** one.
The [specification-authoring challenge](SPECIFICATION-AUTHORING-CHALLENGE.md)
asks you to author your own specification for LAB-05, get it past the validator,
predict the outcome and explain the result — while keeping a **design error**
(exit `1`) apart from the four experiment **result** states (exit `0`).

## 12. Check your setup stays healthy

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
