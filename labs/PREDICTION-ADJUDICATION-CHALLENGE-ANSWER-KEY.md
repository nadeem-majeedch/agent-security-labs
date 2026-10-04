# Prediction adjudication challenge — instructor answer key

> **Instructor-only.** This file contains the expected classifications. Keep it
> out of student handouts and do not surface it in student navigation. It is not
> linked from the student challenge page.

This key accompanies `PREDICTION-ADJUDICATION-CHALLENGE.md`. Every classification
below is grounded in the **real** LAB-05 comparison (approval policy vs
deny-by-default policy). The expected values, produced by
`agentsec compare runs/lab05_require_approval/trace.jsonl runs/lab05_require_approval_deny_by_default/trace.jsonl`:

```text
Trace A (approval policy)      : 11 events
Trace B (deny-by-default)      : 11 events
Event counts                   : A 11, B 11, delta +0
Event-type distribution        : identical in both
Sequence differences           : "event sequences are identical"
Evaluator differences          : decisions.deny              0 -> 1
                                 decisions.require_approval  1 -> 0
                                 tool_results.denied         0 -> 1
                                 tool_results.pending_approval 1 -> 0
```

The two traces are **structurally identical** — same event types, same counts,
identical sequence. The only difference is the **value** recorded in the
`policy_decision` event and its `tool_result` consequence. Nothing executes in
either run.

**The central teaching point:** this pair isolates a *single* policy variable, so
it is ideal for separating an observation from an interpretation from a claim the
evidence cannot support. Hold every student to "name the event/field," and accept
a security, causal or ranking conclusion only when they can point to evidence
that a deterministic trace comparison simply does not contain — which is never
here.

---

## Expected classifications

| # | Claim | Classification | Expected evidence |
| - | ----- | -------------- | ----------------- |
| 1 | approval run has a `pending_approval` tool result | **Prediction** | Made before running; later confirmed (`tool_results.pending_approval: 1`, `policy_decision.decision=require_approval`) |
| 2 | deny-by-default run records `require_approval` | **Prediction** | Made before running; **turns out wrong** — the deny run records `decision=deny` |
| 3 | both runs have the same number of events | **Prediction** | Made before running; later confirmed (A 11, B 11, delta +0) |
| 4 | deny trace has a `policy_decision` with `decision=deny` | **Observation** | `decisions.deny: 0 -> 1`; the single decision event in B |
| 5 | approval trace has a `tool_result` of `pending_approval` | **Observation** | `tool_results.pending_approval: 1 -> 0` |
| 6 | neither trace has a `tool_executed` event | **Observation** | No `tool_executed` row; `evaluate` reports `tool_executions: 0` |
| 7 | policy changes how the same request is handled (held vs refused) | **Interpretation** | `require_approval`→`pending_approval` in A vs `deny`→`denied` in B; bounded, no cause/rank |
| 8 | the runs differ only in the decision and its consequence | **Interpretation** | Sequences identical, delta +0, distributions identical; difference is value-only |
| 9 | the approval policy is safer | **Unsupported** | No safety/risk/severity field exists; one deterministic pair cannot rank |
| 10 | the policy caused the model to behave more responsibly | **Unsupported** | Trace records the decision, not model motivation; no causal link |
| 11 | the deny-by-default configuration is better | **Unsupported** | `compare` is descriptive and produces no ranking |
| 12 | the approval run proves the system is secure | **Unsupported** | A single deterministic comparison cannot establish security |

Distribution: **3 Prediction, 3 Observation, 2 Interpretation, 4 Unsupported**.

---

## Per-claim rationale, expected evidence and the misconception it exposes

### Claim 1 — Prediction

- **Class:** Prediction. The claim is phrased as a commitment made before running;
  the classification depends on *when* it was made, not on the outcome.
- **Evidence (supporting):** the approval trace's `policy_decision` is
  `require_approval`; its `tool_result` is `pending_approval`; `evaluate` reports
  `policy_approvals_required: 1` and `tool_results_pending_approval: 1`.
- **Misconception it tests:** that "prediction" means "guess that turned out
  right." A student who reasons "this matched, so it is an observation" has
  confused the act of predicting with the act of observing.
- **Acceptable alternative:** a student may note it is *both* a prediction and, in
  hindsight, correct — the category is still Prediction.

### Claim 2 — Prediction (and deliberately wrong)

- **Class:** Prediction. Same reasoning as claim 1, but here the prediction is
  **false**: the deny-by-default run records `decision=deny`, never
  `require_approval`.
- **Evidence (contradicting):** `decisions.require_approval: 1 -> 0` and
  `decisions.deny: 0 -> 1` — the value is present only in A, absent in B.
- **Misconception it tests:** that a wrong prediction is not a prediction, or that
  a mismatch is a "failed" exercise. It is the same category; the mismatch is a
  result.
- **Acceptable alternative:** none for the class. If a student calls it an
  observation, that is wrong — it was stated before the run.

### Claim 3 — Prediction

- **Class:** Prediction (stated in advance; confirmed by A 11 = B 11, delta +0).
- **Evidence (supporting):** the event counts in the comparison.
- **Misconception it tests:** that a prediction must be surprising. Correct
  predictions are still predictions.
- **Acceptable alternative:** a student may add that a *count* prediction was a
  weak one, since the two runs share the same fixture — fine, as long as the class
  stays Prediction.

### Claim 4 — Observation

- **Class:** Observation. It names an event and a field value actually present.
- **Evidence:** `decisions.deny: 0 -> 1`; the B trace's single `policy_decision`
  carries `decision: deny`.
- **Misconception it tests:** none serious — it is a clean observation. Watch that
  students do not embellish it ("…therefore it refused to execute because it is
  stricter"), which would turn it into an interpretation or an unsupported claim.

### Claim 5 — Observation

- **Class:** Observation.
- **Evidence:** `tool_results.pending_approval: 1 -> 0`; the A trace's `tool_result`
  marks the read `pending_approval`.
- **Misconception it tests:** that "pending" is the same as "denied." The trace
  records a *hold*, not a refusal — claim 4 and claim 5 together show the two are
  different values.

### Claim 6 — Observation (an absence)

- **Class:** Observation. Observing the **absence** of an event is still an
  observation, as long as it is checkable.
- **Evidence:** no `tool_executed` row appears in the distribution or the sequence;
  `evaluate` reports `tool_executions: 0` for the A trace.
- **Misconception it tests:** that only "positive" statements can be observations,
  or that a missing event is unobservable. An absence in a complete trace is
  evidence.
- **Acceptable alternative (for B):** `evaluate` on B also reports
  `tool_executions: 0`. Either trace supports the claim about itself; the joint
  claim ("neither") is supported by both.

### Claim 7 — Interpretation (bounded)

- **Class:** Interpretation. It generalises the two observed decisions into "how
  the same request is handled," which stays close to the evidence and names no
  cause or rank.
- **Evidence:** the value-only difference — `require_approval`→`pending_approval`
  in A, `deny`→`denied` in B — with everything else identical.
- **Misconception it tests:** that any statement going beyond a single field is
  automatically "unsupported." Bounded interpretation is legitimate; smuggling in
  *why* or *which is better* is not.
- **Boundary to enforce:** if a student writes "…so the approval policy handles
  requests more safely," it has tipped into an unsupported claim.

### Claim 8 — Interpretation

- **Class:** Interpretation.
- **Evidence:** `compare` reports "event sequences are identical," delta +0, and
  identical event-type distribution; the only differences are the values in
  `policy_decision` / `tool_result` / the evaluator rows. So the runs differ in
  *decision*, not in *attempted structure*.
- **Misconception it tests:** the assumption that a policy change must produce a
  structural trace difference. Here it produces a **value-only** difference —
  unlike the LAB-04 capstone, where the count and sequence changed.
- **Boundary to enforce:** "not in what the agent attempted" is an inference from
  structural identity, and is acceptable **bounded**; "the agent intended the same
  thing" is not, because intent is not recorded.

### Claim 9 — Unsupported causal / security claim

- **Class:** Unsupported. "Safer" is a security judgement.
- **Why unsupported:** the comparison exposes no safety, risk, severity or
  effectiveness field. It reports counts and decisions. "Safer" also implies a
  comparison of outcomes against a threat model the exercise does not state.
- **What the trace does establish:** that A answers `require_approval` and B
  answers `deny` for the same request, and that neither executes.
- **Misconception it exposes:** equating a *decision value* with a *safety
  outcome*. A `deny` is not automatically "safe," and a `require_approval` is not
  automatically "safer."

### Claim 10 — Unsupported causal claim

- **Class:** Unsupported. It asserts that the policy **caused** the model to behave
  a certain way.
- **Why unsupported:** the trace records the *policy decision* and the *tool
  result*; it records nothing about model motivation or "responsibility," and the
  model is a deterministic fixture. Correlation in a two-run comparison is not
  causation, and no mechanism is observed.
- **What would be needed:** a controlled manipulation that isolates the policy
  while holding everything else fixed **and** a measure of "responsibility" — which
  this exercise does not define or record.
- **Misconception it exposes:** reading a *policy* difference as a *model*
  behaviour difference, and treating temporal/positional association as cause.

### Claim 11 — Unsupported ranking claim

- **Class:** Unsupported. "Better" is a ranking.
- **Why unsupported:** `compare` is explicitly descriptive and produces **no
  ranking**; there is no objective function, no score, no severity. "Better" would
  require criteria the exercise does not supply.
- **Misconception it exposes:** assuming that two policies shown side by side imply
  one is preferable. The trace shows the boundary every time, never a verdict.

### Claim 12 — Unsupported security claim

- **Class:** Unsupported. It generalises from one deterministic pair to "the
  system is secure."
- **Why unsupported:** a security claim needs evidence of coverage, threats,
  adversary capability and absence of vulnerabilities — none of which a single
  deterministic trace comparison can provide. The comparison is one fixture under
  two policies.
- **Misconception it exposes:** treating a resolved decision (a `require_approval`
  or a `deny` on one request) as a system-wide assurance.

---

## Marking guidance

- **Credit the classification *and* the justification.** A correct class with no
  evidence is incomplete; a defensible class with a real event/field cited is
  credit-worthy even if it differs from the sample wording.
- **Claims 1–3 (Prediction):** the only correct class is Prediction, because the
  claim is *phrased* as a pre-run commitment. Accept any correct observation of
  the outcome alongside it.
- **Claims 4–6 (Observation):** the only correct class is Observation, and the
  student must name the field or the absence.
- **Claims 7–8 (Interpretation):** accept nearby bounded wording, but not a
  ranking or a cause.
- **Claims 9–12 (Unsupported):** the classification must be some form of
  *unsupported / not established*, and the student must explain **what evidence is
  missing** — not merely assert that the trace "does not say."

**Do not accept** for claims 9–12: "it is true but the trace just doesn't mention
it," or any attempt to supply external reasoning as if the trace contained it.
The exercise is about what the **evidence** supports.

---

## One-sentence summary to give students

> Every claim can climb only as high as the evidence underneath it: the trace can
> show you a `require_approval` and a `deny`, but it cannot tell you that one is
> safer, that the model was more responsible, or that the system is secure.
