# Prediction adjudication challenge

This challenge builds on the getting-started capstone
([step 11](GETTING-STARTED.md#11-predict-a-difference-before-comparing)) and the
[trace-reading exercises](TRACE-READING-EXERCISES.md). The capstone taught you to
write *one* prediction and check it against a comparison. This one asks something
different:

> You are given a set of **competing statements** about two runs. Decide **what
> kind of statement each one is**, and defend that decision with evidence.

The commands are already familiar (`run`, `inspect`, `evaluate`, `predict`,
`compare`). The new skill is **adjudication**: telling apart

**what you predicted** → **what you observed** → **what you can reasonably
interpret** → **what the traces cannot establish at all**.

> This is a trace-reading exercise, not a security judgement. The model is a
> deterministic fixture, the comparison is descriptive, and **no ranking is
> produced**. Do not score, grade or rank the two policies.

---

## The scenario

LAB-05 ("Require Approval") runs the *same* experiment under two different
policies. The task, the mock fixture and the agent are identical the whole way
through — **only the policy differs**.

- **Run A — approval policy:** `labs/LAB-05-require-approval/config.yaml`
- **Run B — deny-by-default policy:**
  `configs/examples/lab05_require_approval_deny_by_default.yaml`

Read **both** policy files before you run anything. What each policy answers is
the thing you are about to test.

---

## A. Before running — predict

From the two policy files alone, write **2–3 predictions** on paper. Each
prediction must name an *observable* you can later check against a trace or a
comparison — a decision, a tool result, an event count. Write them down **before**
you run.

A prediction can be **wrong** and still be a perfectly legitimate prediction. The
result of a wrong prediction is a *mismatch*, which is a result, not a failure.

## B. Run

```bash
agentsec run labs/LAB-05-require-approval/config.yaml
agentsec run configs/examples/lab05_require_approval_deny_by_default.yaml
```

## C. Inspect

```bash
# a short, in-order summary of each trace
agentsec inspect runs/lab05_require_approval/trace.jsonl
agentsec inspect runs/lab05_require_approval_deny_by_default/trace.jsonl

# the evaluator's read-only counts for one of them
agentsec evaluate runs/lab05_require_approval/trace.jsonl

# check the shipped prediction for the approval run
agentsec predict \
  runs/lab05_require_approval/trace.jsonl \
  configs/predictions/lab05_expect_approval.yaml

# compare the two traces
agentsec compare \
  runs/lab05_require_approval/trace.jsonl \
  runs/lab05_require_approval_deny_by_default/trace.jsonl
```

## D. Adjudicate and E. Justify

Classify **every** claim in the table below into exactly one of the four
categories, then justify it with concrete evidence from the traces or the
comparison output. Where a claim is not supported, say what evidence is missing.

---

## The four categories

**Prediction** — a statement made *before* observing the result. Its defining
feature is *when* it was made, not whether it turned out correct. "I predict the
read will be held" is a prediction even if the trace later shows it was refused.

**Observation** — a statement that corresponds directly to something **actually
present** in the trace, the evaluator output, or the comparison. If you cannot
point to the exact event, field or line, it is not an observation.

**Interpretation** — a statement that reasonably explains observed behaviour while
staying close to the evidence. It is bounded: it says what the difference *is*,
not *why* it is good or bad. Interpretations must not smuggle in a cause or a
rank.

**Unsupported causal / security claim** — a statement that requires evidence this
exercise does not provide. A single deterministic trace comparison shows *what
differs*; it does not show *why*, and it does not establish that anything is
safer, better or more secure.

Keep this one distinction firmly in mind:

> **"The trace shows X"** is not the same as **"X happened because of Y"**, and
> neither is the same as **"X is safer/better."**

---

## The claim ladder

```text
Prediction
    ↓
Observed trace evidence
    ↓
Bounded interpretation
    ↓
Causal / ranking claim
```

The ladder is **not** a ladder of confidence. Moving down it does **not** mean a
statement becomes more certain. The first rung is a commitment made in advance
and may be wrong; the last rung usually needs evidence that a single trace
comparison **cannot supply**. A statement can climb no further than the evidence
underneath it.

---

## Claims to adjudicate

For each claim: write its **classification**, the **evidence** that supports or
contradicts it (name the event, field or comparison line), and whether you judge
it **supported**.

| # | Claim | Classification | Evidence / reasoning | Supported? |
| - | ----- | -------------- | -------------------- | ---------- |
| 1 | "I predict that the approval-policy run will contain a `pending_approval` tool result." | | | |
| 2 | "I predict that the deny-by-default run will record a `require_approval` policy decision." | | | |
| 3 | "I expect both runs to contain the same number of events." | | | |
| 4 | "The deny-by-default trace contains a `policy_decision` event whose `decision` is `deny`." | | | |
| 5 | "The approval-policy trace contains a `tool_result` reporting the read as `pending_approval`." | | | |
| 6 | "Neither trace contains a `tool_executed` event." | | | |
| 7 | "The policy configuration changes how the same request is handled: held under the approval policy, refused under deny-by-default." | | | |
| 8 | "The two runs differ only in the recorded policy decision and its consequence, not in what the agent attempted." | | | |
| 9 | "The approval policy is safer." | | | |
| 10 | "Because it held the read, the policy caused the model to behave more responsibly." | | | |
| 11 | "The deny-by-default configuration is better." | | | |
| 12 | "The approval run proves that the system is secure." | | | |

---

## F. Reflect

Answer in your own words, using the evidence:

1. Can a prediction be **wrong** and still be a valid prediction? Why?
2. What makes an **observation** stronger than an **interpretation**?
3. Why does a trace **difference** not automatically establish **causality**?
4. Why can the comparison show a **policy boundary** without proving which policy
   is "better" or "safer"?
5. What **additional evidence** would be needed before any security or
   effectiveness claim could be made?

---

> **Answers are not in this file.** Your instructor has a separate, instructor-only
> answer key. Do your own classification first: explain *why* each claim belongs
> in its category, and where a claim reaches beyond the evidence.

> **Output and cleanup.** Running the second configuration writes
> `runs/lab05_require_approval_deny_by_default/trace.jsonl`, which sits under the
> untracked `runs/` directory. Neither run modifies the repository's tracked
> files.
