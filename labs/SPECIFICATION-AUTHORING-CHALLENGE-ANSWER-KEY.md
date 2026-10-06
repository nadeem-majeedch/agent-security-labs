# Specification authoring challenge — instructor answer key

> **Instructor-only.** This file contains a complete reference specification, the
> expected values and the validator messages each common mistake produces. Keep it
> out of student handouts and do not surface it in student navigation. It is not
> linked from the student challenge page.

This key accompanies `SPECIFICATION-AUTHORING-CHALLENGE.md`. Every value below is
grounded in the **real** experiment, produced by running the reference
specification with:

```bash
agentsec experiment lab05-authoring.yaml
```

The central teaching point: a **design error** (exit `1`) and a **result state**
(exit `0`) are categorically different, and the strict schema makes an
**uncontrolled** specification impossible to express.

---

## Reference specification (Deliverable A)

```yaml
schema_version: "1"
experiment_id: lab05-policy-authoring
title: Authoring challenge — LAB-05 policy intervention

hypothesis: >
  Changing only the LAB-05 policy, from the shipped least-privilege policy to the
  permissive allow-all policy, changes whether the held database read is permitted
  to execute.

base_config: labs/LAB-05-require-approval/config.yaml

intervention:
  type: policy
  control_policy: policies/examples/least_privilege_v1.yaml
  treatment_policy: policies/examples/allow_all_v1.yaml

expected_changes:
  tool_executions: 1

expected_invariants:
  requested_tools: ["mock_db"]
  produced_final_output: true

alternative_explanations:
  - the difference is a property of this deterministic fixture, not of any real model

claim: >
  Within this deterministic fixture, changing only the policy changes whether the
  held database read is permitted to execute.
```

Accept any well-formed variant with a different slug, title or wording. The two
non-negotiable design properties are: (1) a shared `base_config`, and (2) exactly
one declared intervention whose two policies differ.

---

## Deliverable A answers

1. **Control** = `least_privilege_v1.yaml`; **treatment** = `allow_all_v1.yaml`.
2. Under least privilege the `mock_db` read matches the
   `db-read-requires-approval` rule and is answered **`require_approval`** (held);
   under allow-all it is **allowed**.
3. Yes — under allow-all the held read is permitted, so the treatment executes a
   tool: `expected_changes.tool_executions: 1`.
4. `requested_tools` and `produced_final_output` are good invariants because the
   one permitted change (the policy) should **not** change *which* tool the agent
   asks for or whether it finishes with an answer. They are expected in **both**
   runs.

## Deliverable B — expected prediction

- State: **`changes_observed`** (the declared change appears and the invariants
  hold).
- Events: **different** — an executed tool writes an extra event the held side
  lacks (observed: 11 → 12).
- An evaluator difference such as `decisions.allow` or
  `tool_results.pending_approval` is expected to flip.

## Deliverable C — expected result (real values)

```text
state                           changes_observed     (exit 0)
control   policy                policies/examples/least_privilege_v1.yaml
control   status                completed
control   event_count           11
treatment policy                policies/examples/allow_all_v1.yaml
treatment status                completed
treatment event_count           12
expected change  tool_executions        expected 1, control 0, treatment 1, OBSERVED
invariant        requested_tools        expected ["mock_db"] in both, HELD
invariant        produced_final_output  expected true in both, HELD
observed difference
    events                      A=11 B=12 delta=-1
    decisions.allow             0 -> 1
    decisions.require_approval  1 -> 0
    tool_results.ok             0 -> 1
    tool_results.pending_approval 1 -> 0
```

Note the control's read was **`pending_approval`** (held), not denied — that is
the LAB-05 boundary, and it is why the treatment's `tool_results.ok` flips to `1`
rather than `tool_results.denied`.

---

## Deliverable D — validator messages (design errors, exit `1`)

| Mistake | Actual behaviour | Why it is a *design* error |
| --- | --- | --- |
| Same policy both sides | `invalid experiment specification: intervention: Value error, control_policy and treatment_policy must be different references` | There is no difference to test — nothing ran. |
| Extra field changing a second thing | `invalid experiment specification: also_change_task: Extra inputs are not permitted` | The format cannot express an uncontrolled design; the schema rejects it rather than ignoring it. |
| Missing `expected_invariants` | `invalid experiment specification: <root>: Value error, expected_invariants must declare at least one observation` | The experiment is under-specified; nothing ran. |
| Blank `hypothesis` | `invalid experiment specification: hypothesis: Value error, hypothesis must not be empty` | The frame of the experiment is missing; nothing ran. |
| Non-existent `base_config` | `could not read experiment config <path>: [Errno 2] No such file or directory` | A referenced file does not exist; nothing ran. |
| Malformed YAML | `invalid YAML in <path>: …` | The document cannot even be parsed; nothing ran. |

In every case the command exits **`1`** and nothing executes — which is exactly
what makes it a design error rather than a result state.

---

## Deliverable E — expected explanation

A strong answer:

> Within this deterministic fixture, the experiment held everything constant
> except the policy. Under least privilege the database read was held
> (`require_approval`), so `tool_executions` was `0`; under allow-all it executed,
> so `tool_executions` was `1`, and the declared change was `OBSERVED`. Both
> invariants held — both runs requested `mock_db` and produced a final output — so
> the state is `changes_observed`. The result describes *what* differed between
> the two traces; it does not establish *why*, and it makes no ranking or causal
> claim.

**Withhold credit for:** ranking the policies, claiming the policy *caused* real
behaviour, or asserting the run "proves" security. Each needs evidence a single
deterministic comparison cannot supply.

---

## Section 9 — reflection (expected answers)

1. **Uncontrolled designs are unrepresentable** because there is only one shared
   `base_config` and only one intervention section, and the schema accepts only a
   `policy` intervention. A second difference has nowhere to go, and an unknown
   field is rejected.
2. **Unknown fields as errors** prevent a typo from silently changing the meaning
   of an experiment — a misspelled key cannot quietly become a no-op.
3. **Held-constant guarantees** that the two runs differ only in the declared
   policy (and the per-run trace file). It does **not** guarantee the result means
   the policy would have the same effect off-fixture, nor that any difference is
   causal.
4. **Design error vs result state** — a design error means nothing ran; a result
   state is what the runner reports after two completed runs.
5. **`changes_not_observed` is not a broken specification.** It is a valid result:
   the design was fine and the runs completed; the declared change simply did not
   appear. (A broken specification would exit `1` instead.)
6. **An `OBSERVED` change licenses only** "within this deterministic fixture, the
   declared change appeared in the treatment." It does not license a ranking, a
   safety claim or a causal claim.

---

## Marking guidance

An **instructional** rubric only — not a security score, risk metric or research
measure.

| Criterion | Excellent | Satisfactory | Needs improvement |
| --- | --- | --- | --- |
| Well-formed specification | Valid, single-variable, all required fields | Minor issues, still valid | Invalid or uncontrollable design |
| Design discipline | Explains why exactly one difference is allowed | Understands the rule | Confuses the intervention |
| Prediction | Commits to a state with a reason, before running | States a state only | Predicts after seeing the result |
| Design vs result | Clearly separates exit `1` from the four states | Usually separates them | Treats a design error as a result |
| Causal boundary | Explicitly withholds causal/ranking claims | Mostly bounded | Makes a claim the evidence cannot support |

---

## One-sentence summary to give students

> A specification can only describe a **controlled** experiment, and getting it
> past the validator is a **design** step — separate from the four **result**
> states the runner reports once both runs complete.
