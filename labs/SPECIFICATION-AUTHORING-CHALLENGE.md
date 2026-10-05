# Specification authoring challenge

So far you have **read** controlled experiments and **run** them. This challenge
turns it around: you **author** a specification yourself.

You will write a small YAML file that declares a controlled experiment — a shared
base run, exactly one intervention, the observation you expect to **change**, the
observations you expect to **stay the same**, and the alternative explanations you
considered — then get it past the specification validator, predict its outcome,
run it, and explain the result.

The command is the one you already met in the
[controlled-experiments learning module](CONTROLLED-EXPERIMENTS.md):

```bash
PYTHONPATH=src py -m agentsec experiment <your-specification.yaml>
```

> This is a **documentation-only** exercise. You write a local YAML file; you do
> not modify any tracked file, run any new command, or produce any score, ranking
> or security claim.

---

## 1. The core skill: a *controlled* design

A specification is only a controlled experiment if **exactly one thing** differs
between the two runs it describes. The format enforces this for you:

- Both runs are derived from **one shared `base_config`** — same scenario, same
  task, same tools, same deterministic model.
- The **only** section that may introduce a difference is `intervention`, and the
  only intervention type the schema accepts is `policy`.

This has a sharp consequence you should notice: **you cannot write an
uncontrolled specification.** There is nowhere to put a second difference. If you
try to add a field that changes something else, the strict schema **rejects the
file** — it will not quietly ignore your extra field. The runner additionally
performs a held-constant check on the two derived runs as an internal backstop,
but the format means a valid specification never needs it to fire.

So authoring a specification is really about **choosing one variable and
committing, up front, to what you expect it to do.**

---

## 2. What a valid specification must contain

Every field below is required (or required to be non-empty) unless marked
optional. The validator checks all of them **before** anything runs.

| Field | Rule |
| --- | --- |
| `schema_version` | The specification schema version, `"1"`. |
| `experiment_id` | A lowercase **slug**: letters, digits, `.`, `_`, `-`; must start with a letter or digit. |
| `title` | Optional short title. |
| `hypothesis` | Non-empty prose: the single-variable question you are testing. |
| `base_config` | Path to the shared base run both sides derive from. |
| `intervention.type` | `policy` (the only value). |
| `intervention.control_policy` | Path to the control policy. |
| `intervention.treatment_policy` | Path to the treatment policy — must be **different** from the control policy. |
| `expected_changes` | At least one observation, expected to **change** (a claim about the treatment). |
| `expected_invariants` | At least one observation, expected to stay the same in **both** runs. |
| `alternative_explanations` | At least one non-empty alternative you considered. |
| `claim` | Optional bounded conclusion (echoed, never machine-judged). |

Two more rules the validator enforces:

- **Unknown fields are errors.** A typo, or a field that tries to change a second
  thing, is rejected rather than ignored.
- **Referenced files must exist and load.** A missing `base_config`, control
  policy or treatment policy is a configuration error.

Any violation is a **design error**: the command exits `1` and prints a short,
actionable message. Nothing runs.

---

## 3. Deliverable A — author your specification

Choose a base scenario and exactly one policy question. The worked example from
the learning module used LAB-04; for this challenge use
**[LAB-05 (Require Approval)](LAB-05-require-approval/README.md)** and ask a
different, equally narrow question:

> *If the only thing that changes is the policy, does the **held** database read
> become permitted to execute?*

Start from this scaffold and fill it in. Save it **outside the tracked trees** —
for example `lab05-authoring.yaml` in the repository root (the `runs/` directory
is untracked too, but it is meant for traces).

```yaml
schema_version: "1"
experiment_id: <a-lowercase-slug>
title: <short title>

hypothesis: >
  <one sentence naming the single variable and what you expect it to do>

base_config: labs/LAB-05-require-approval/config.yaml

intervention:
  type: policy
  control_policy: policies/examples/least_privilege_v1.yaml
  treatment_policy: policies/examples/allow_all_v1.yaml

expected_changes:
  tool_executions: <0 or 1? — what you expect in the treatment>

expected_invariants:
  requested_tools: ["mock_db"]
  produced_final_output: true

alternative_explanations:
  - <at least one honest alternative explanation>

claim: >
  <a bounded conclusion that stays inside the fixture>
```

Before you move on, answer on paper:

1. Which policy is the **control** and which is the **treatment**?
2. Read both policy files. Under the control policy, what happens to a `mock_db`
   read? Under the treatment policy?
3. Will the held read **execute** in the treatment? So what value do you put in
   `expected_changes.tool_executions`?
4. Why are `requested_tools` and `produced_final_output` good choices for
   `expected_invariants`?

---

## 4. Deliverable B — predict the outcome

Before running anything, write down:

1. Which of the four states you expect — `changes_observed`, `changes_not_observed`,
   `invariant_violated`, or `execution_failed` — and why.
2. Whether the two traces will have the **same** number of events or different.
3. One evaluator field you expect to differ (`decisions.*`, `tool_results.*`).

A prediction can be **wrong** and still be a good prediction. The point is to
commit before you look.

---

## 5. Deliverable C — get it past the validator, then run it

First, a syntax/design check happens automatically every time you run the command.
If your file is malformed or violates a rule, you get a design error (exit `1`)
and nothing executes. When it validates, the experiment runs and prints the
`ExperimentResult`.

```bash
PYTHONPATH=src py -m agentsec experiment lab05-authoring.yaml
```

Record from the output:

- the **state** (`state:` line);
- the **control** and **treatment** policy, status and event count;
- each `expected changes` line: `expected` / `control` / `treatment` and whether it
  is `OBSERVED` or `NOT OBSERVED`;
- each `expected invariants` line and whether it is `HELD` or `VIOLATED`;
- the `observed difference` fields;
- the **exit code** (check it with `echo $?`).

---

## 6. Deliverable D — iterate against the validator

The validator is your feedback loop. Deliberately introduce **one** mistake at a
time, run the command, and record the message and exit code before fixing it.
These are the mistakes the format catches:

| Mistake | What you should see |
| --- | --- |
| Set `control_policy` and `treatment_policy` to the **same** policy | A design error: the two must be **different references** (exit `1`). |
| Add a field that changes a **second** thing (for example `also_change_task: …`) | A design error: **extra inputs are not permitted** (exit `1`). The format will not let you express an uncontrolled design. |
| Leave out `expected_invariants` | A design error: invariants must declare at least one observation (exit `1`). |
| Leave `hypothesis` blank | A design error: the hypothesis must not be empty (exit `1`). |
| Point `base_config` at a path that does not exist | A design error: the base config could not be read (exit `1`). |
| Break the YAML (a stray colon, a bad indent) | A design error: invalid YAML (exit `1`). |

For each, note **why** the failure is a *design* error and not one of the four
result states. (Hint: nothing ran.)

---

## 7. Deliverable E — explain the result, honestly

Write a three-to-four-sentence explanation of your experiment that:

- names the **state**, with the evidence for it;
- uses only fields **in the result**;
- uses the words *"within this deterministic fixture"*;
- does **not** say which policy is better or safer, and does **not** claim the
  policy *caused* anything.

---

## 8. The boundary: design error vs result state

Keep these two apart — it is the whole point of the exercise:

| Situation | Exit code | What it means |
| --- | --- | --- |
| Invalid or incomplete **specification** | `1` | A **design** error. Nothing ran. Fix the specification. |
| The experiment runs, any of the four **states** | `0` | A **result**. The runner did its job — even `execution_failed` is a result the runner reports, not a CLI failure. |
| Something breaks **outside** normal handling | `2` | An **orchestration** failure — the command itself failed. Never reported as `changes_not_observed`. |

A design error is the format telling you *"this is not a well-formed controlled
experiment."* A result state is the runner telling you *"here is what the two runs
showed."* Confusing the two is the most common mistake this challenge is designed
to catch.

---

## 9. Reflect

Answer in your own words:

1. Why does the format make an **uncontrolled** specification impossible to
   express, rather than merely discouraging one?
2. Why is it useful that an unknown field is an **error** instead of being
   silently ignored?
3. What does the held-constant invariant guarantee about the two runs — and what
   does it *not* guarantee about the result?
4. Why is a specification **design error** (exit `1`) categorically different from
   any of the four **result states** (exit `0`)?
5. If your experiment returns `changes_not_observed`, is your specification
   broken? Explain.
6. What may you conclude when your declared change is `OBSERVED`, and what may you
   **not** conclude?

---

## Where to go next

- **[Controlled experiments — learning module](CONTROLLED-EXPERIMENTS.md)** — the
  vocabulary this challenge assumes: control/treatment, the held-constant
  invariant, the `ExperimentResult` fields and the four states.
- **[LAB-05 (Require Approval)](LAB-05-require-approval/README.md)** — the lab this
  challenge's base scenario comes from.
- **`docs/development.md`** — the CLI reference, including the `agentsec experiment`
  section and its exit codes.

> **Your instructor has an answer key** with a complete reference specification,
> the expected values, and the validator messages each common mistake produces.
> Write your own specification first and try to predict before you compare.

> **Output and cleanup.** The two experiment runs write their traces to a
> temporary directory that the command removes afterwards, so the repository's
> tracked files are never touched. Delete your `lab05-authoring.yaml` and any
> scratch specifications when you have finished.
