# Controlled experiments — instructor answer key

> **Instructor-only.** This file contains the expected answers for the guided
> exercise in `CONTROLLED-EXPERIMENTS.md`. Keep it out of student handouts and do
> not surface it in student navigation. It is not linked from the student module.

This key accompanies `CONTROLLED-EXPERIMENTS.md`. Every value below is grounded in
the **real** shipped experiment, produced by:

```bash
PYTHONPATH=src py -m agentsec experiment configs/experiments/lab04-policy-intervention.yaml
```

The central teaching point is the same as the prediction-adjudication challenge's:
hold students to **"name the evidence"**, and accept a causal, ranking or
security conclusion only when they can point to evidence that a single
deterministic experiment does not contain — which is never here.

---

## The shipped result

```text
status                          changes_observed
control   policy                policies/examples/least_privilege_v1.yaml
control   status                completed
control   event_count           11
treatment policy                policies/examples/allow_all_v1.yaml
treatment status                completed
treatment event_count           12
expected change  tool_executions        expected 1, control 0, treatment 1, OBSERVED
invariant        produced_final_output  expected true, control true, treatment true, HELD
invariant        requested_tools        expected ["fs_sandbox"] in both, HELD
observed difference
    events                      A=11 B=12 delta=-1
    decisions.allow             0 -> 1
    decisions.deny              1 -> 0
    tool_results.denied         1 -> 0
    tool_results.error          0 -> 1
exit code                       0
```

---

## Section 12 — guided exercise

### A. Inspect the specification

1. **Base run** — `base_config: labs/LAB-04-tool-misuse/config.yaml`, the shared
   run both sides derive from.
2. **Intervention** — `intervention: {type: policy, control_policy: …, treatment_policy: …}`.
   The **only** things allowed to differ between control and treatment are the
   policy and the per-run trace file (the held-constant invariant excludes
   `policy_path` and `trace_path` and nothing else).
3. **`expected_changes`** — `tool_executions: 1`.
4. **`expected_invariants`** — `requested_tools: ["fs_sandbox"]` and
   `produced_final_output: true`. Each is expected in **both** runs.

### B. Predict the expected outcome

1. **Control** = `least_privilege_v1.yaml`; **treatment** = `allow_all_v1.yaml`.
2. Under least privilege the out-of-scope write is **denied** (does not execute);
   under allow-all it is **permitted and executes**. A reasonable prediction is
   that at least one side records a `tool_execution`.
3. A well-reasoned prediction is **`changes_observed`** (the declared change is
   met and the invariants hold).
4. The traces need **not** have the same number of events: an executed tool writes
   a `tool_executed` event the denied side lacks, so the treatment is expected to
   have **more** events. (Observed: control 11, treatment 12, delta −1.)

Accept any of these predictions, right or wrong — the exercise is to commit first.
A wrong prediction is a *result*, not a failure.

### C. Run

```bash
PYTHONPATH=src py -m agentsec experiment configs/experiments/lab04-policy-intervention.yaml
```

### D. Inspect control and treatment

| Side | policy | status | events |
| --- | --- | --- | --- |
| control | `policies/examples/least_privilege_v1.yaml` | `completed` | 11 |
| treatment | `policies/examples/allow_all_v1.yaml` | `completed` | 12 |

### E. Compare expected vs observed changes

| Entry | expected | control | treatment | verdict |
| --- | --- | --- | --- | --- |
| `tool_executions` | 1 | 0 | 1 | `OBSERVED` |

Observed-difference evaluator fields that differ:

```text
decisions.allow        0 -> 1
decisions.deny         1 -> 0
tool_results.denied    1 -> 0
tool_results.error     0 -> 1
```

(The event counts differ by one: A 11, B 12, delta `-1`.)

### F. Invariants

| Entry | expected | control | treatment | verdict |
| --- | --- | --- | --- | --- |
| `produced_final_output` | true | true | true | `HELD` |
| `requested_tools` | `["fs_sandbox"]` | `["fs_sandbox"]` | `["fs_sandbox"]` | `HELD` |

Both held because **both** sides matched — an invariant holds only when neither
run violates it.

### G. Explain the result — expected model answer

A strong answer looks like:

> Within this deterministic fixture, the experiment held everything constant
> except the policy. The control (least-privilege) denied the out-of-scope write,
> so `tool_executions` was `0`; the treatment (allow-all) executed it, so
> `tool_executions` was `1`, and the declared change was `OBSERVED`. Both
> invariants held — both runs requested the same tool and produced a final
> output — so the state is `changes_observed`. The result describes *what*
> differed between the two traces; it does not establish *why*, and it makes no
> ranking or causal claim.

**What to withhold credit for:** any sentence that ranks the policies
("least-privilege is safer", "allow-all is worse"), claims the policy *caused*
real behaviour, or concludes the run "proves" security. Each needs evidence a
single deterministic comparison cannot supply.

### H. Explore the other states

| Edit | Result |
| --- | --- |
| `expected_changes: {tool_executions: 0}` | `tool_executions` prints `NOT OBSERVED`; state **`changes_not_observed`**; exit `0`. |
| `expected_invariants: {tool_executions: 0}` | `tool_executions` prints `VIOLATED` (control 0, treatment 1); state **`invariant_violated`**; exit `0`. |
| trigger `execution_failed` | Not reachable from a valid specification on purpose — it occurs only when a run cannot be completed (executor error or no trace written). |

Every one of these exits **`0`**: they are experiment outcomes, not CLI errors.

---

## Section 13 — reflection (expected answers)

1. **Held-constant invariant** — it stops a mis-controlled pair from running. If
   anything other than the declared intervention differs, the runner raises a
   configuration error instead of attributing an uncontrolled difference to the
   intervention.
2. **Change vs invariant** — a change is a claim about the **treatment** (the side
   the intervention acts on); an invariant is a claim that behaviour stayed the
   same in **both** runs.
3. **`invariant_violated` is about the experiment's assumptions** — it means
   something declared constant did not stay constant, so the run was not as
   controlled as the specification asked. It is not evidence for or against the
   hypothesis.
4. **`execution_failed` ≠ `changes_not_observed`** — the former means a run did not
   finish, so there is nothing to compare; the latter means both runs finished
   cleanly and the expected change simply did not appear.
5. **An `OBSERVED` change licenses** only: "within this deterministic fixture, the
   declared change appeared in the treatment." It does **not** license a ranking,
   a safety claim, or a causal claim.
6. **No causality despite holding variables constant** — holding the fixture
   constant rules out the things you varied against, but a single synthetic,
   deterministic scenario cannot rule out that the difference is a property of the
   fixture itself, nor extrapolate to real models. It narrows explanations; it
   does not prove one.
7. **Additional evidence** would include: repeated runs, varied scenarios and
   fixtures, a non-deterministic (real) execution stack, and an argument that the
   held-constant assumptions mirror the real deployment. That is research, not a
   teaching fixture.

---

## Marking guidance

An **instructional** rubric only — not a security score, risk metric or research
measure.

| Criterion | Excellent | Satisfactory | Needs improvement |
| --- | --- | --- | --- |
| Specification reading | Names base, intervention, changes and invariants correctly | Minor slips | Conflates the parts |
| State identification | Correct state with the evidence for it | Right state, thin evidence | Wrong or unjustified state |
| Change vs invariant | Clearly separates treatment-only from both-runs | Usually distinguishes | Conflates them |
| Evidence | Cites the exact result fields | Cites some fields | Asserts without evidence |
| Causal boundary | Explicitly withholds causal/ranking claims | Mostly bounded | Makes a claim the evidence cannot support |

---

## One-sentence summary to give students

> A controlled experiment holds everything constant except the one thing you
> declare, and then reports **what differs** — never **why**, and never which side
> is better.
