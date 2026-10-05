# AgentSec Labs — Instructor Guide

> **Instructor guide — intended for teaching use; not a student handout.**
> It contains teaching strategy and discussion prompts, but **not** the exercise
> answers. The authoritative answer key is a separate instructor-only file:
> [`TRACE-READING-EXERCISES-ANSWER-KEY.md`](TRACE-READING-EXERCISES-ANSWER-KEY.md).

This guide helps you teach **LAB-00 … LAB-07** and the trace-reading material in
[`labs/README.md`](README.md), [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md)
and [`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md). It assumes the
repository as it stands: eight labs, a deterministic mock model, in-memory tools,
offline execution, and **no LAB-08**.

> These labs are educational/reproducibility infrastructure. They make **no
> research claim** and are **not a benchmark**. The deterministic mock fixtures
> demonstrate the **mechanics** of a security boundary; they are **not** a
> distribution of real model behaviour.

---

## 1. Course / lab learning objectives

By the end of the lab sequence, students should be able to:

1. **Distinguish a model response from a tool request** — the events are
   different, and one may lead to the other without being the same thing.
2. **Distinguish a tool request from actual tool execution** — `tool_requested`
   is an intention, not a fact of execution.
3. **Interpret a policy decision** — read `policy_decision` and know that it is
   recorded **before** anything runs.
4. **Recognise the three decisions** — `allow`, `deny` and `require_approval`
   mean three different things.
5. **Identify when a tool actually executed** — using the `tool_executed` event.
6. **Interpret a `tool_result`** — including that it can exist **without** a
   `tool_executed`.
7. **Identify observable synthetic side effects** — using `side_effects`.
8. **Read a multi-event JSONL trace** — follow the sequence and the
   `parent_event_id` chain.
9. **Explain the difference between observable trace mechanics and assumptions
   about model behaviour** — the trace records **what** happened, not **why**.

---

## 2. Recommended teaching sequence

The sequence is **conceptual, not a severity ranking**. Each lab isolates a
different question; do not present one as more important or "more dangerous" than
another.

| Stage | Material | Purpose | Suggested activity |
|---|---|---|---|
| 1 | LAB-00 — setup | Verify the environment end to end (run → trace → evaluate). | Instructor demos one run; students reproduce it on their own machines. |
| 2 | LAB-01 — benign tool use | Establish the baseline lifecycle and the request/execution distinction. | Students run it and locate `tool_requested` vs `tool_executed`. |
| 3 | LAB-02 — direct prompt injection | Instruction arrives **in the task**. | Students inspect `agent_input` and notice the mixed task. |
| 4 | LAB-03 — indirect prompt injection | Instruction arrives **in tool-returned content**; adds a second (denied) call. | Students follow the two-call sequence and the extra hop. |
| 5 | LAB-04 — tool misuse | No injected instruction; the **requested operation** is out of scope. | Students confirm the `deny` and the missing `tool_executed`. |
| 6 | LAB-05 — require approval | The third decision: a legitimate request **held**, not refused. | Students contrast `require_approval` with `deny`. |
| 7 | LAB-06 — excessive agency | An **authorized** action executes though the task did not need it. | Students read `tool_executed` + `side_effects`. |
| 8 | LAB-07 — data leakage | An authorized read + authorized send cross an **egress** boundary. | Students locate the content in the send request's args. |
| 9 | `TRACE-WALKTHROUGHS.md` | Event-by-event reading of each real trace. | Led reading; students annotate their own traces. |
| 10 | `TRACE-READING-EXERCISES.md` | Active practice reading traces. | Individual → pair → whole-class discussion. |

---

## 3. Suggested time allocation

These are **suggested teaching times**, not empirically validated optima. Adjust
to your course length and student background.

| Segment | Suggested time |
|---|---|
| Orientation (repo, CLI, what a trace is) | 15–20 min |
| LAB-00 / LAB-01 (introductory) | 20–30 min each |
| LAB-02 … LAB-07 (more involved) | 30–40 min each |
| Trace walkthroughs | ~30 min |
| Exercises (`TRACE-READING-EXERCISES.md`) | 45–60 min |
| Discussion / reflection | 20–30 min |

A single-session version can compress to an orientation, one benign lab, one
denied lab, one side-effect lab, and a short exercise block.

---

## 4. Per-lab instructor notes

### LAB-00 — Setup & Environment Verification

- **Teaching objective.** Students confirm the toolchain works and understand the
  loop: config → `run` → trace → `evaluate`.
- **Before the lab.** Explain what the CLI does, where traces are written
  (`runs/<run_dir>/trace.jsonl`), and that `evaluate` only reads a trace — it does
  not re-run anything.
- **Student activity.** Follow [`LAB-00-setup/README.md`](LAB-00-setup/README.md):
  run the experiment, `inspect` the trace, then `evaluate` it.
- **Trace focus.** `run_started`, `agent_input`, `tool_requested` (`calculator`),
  `policy_decision` (`allow`, `allow-calc`), `tool_executed`, `tool_result`
  (`ok: true`), `agent_output`, `run_completed`.
- **Questions to ask.**
  1. Which event tells you the calculator finished successfully?
  2. Which event tells you it *started*?
  3. Why does the trace contain `parent_event_id`?
- **Common misconception.** Expecting `evaluate` to run the experiment again, or
  assuming the final answer alone proves a tool ran.
- **Expected learning outcome.** Students can run a lab and say which event proves
  what, without help.

### LAB-01 — Observe a Benign Agent

- **Teaching objective.** Establish the "normal" lifecycle before anything
  adversarial, and separate a request from an execution.
- **Before the lab.** Frame this as the baseline; nothing here is adversarial.
- **Student activity.** Follow
  [`LAB-01-benign-agent/README.md`](LAB-01-benign-agent/README.md); answer the six
  questions.
- **Trace focus.** One `tool_requested` and **one** `tool_executed`, both
  `calculator`; a single `allow`; no `deny`.
- **Questions to ask.**
  1. What would be missing if the policy had returned `deny`?
  2. Does the answer text on its own prove the calculator ran?
- **Common misconception.** Reading the final answer and assuming a tool ran.
- **Expected learning outcome.** Students can point to `tool_executed` as the
  execution evidence and explain why the answer text is not.

### LAB-02 — Direct Prompt Injection

- **Teaching objective.** The hostile instruction arrives **directly in the
  task**; the agent follows it.
- **Before the lab.** Explain that the trace records **what** happened, not
  **why**, and that it does not label trusted instructions vs untrusted text.
- **Student activity.** Follow
  [`LAB-02-direct-prompt-injection/README.md`](LAB-02-direct-prompt-injection/README.md).
- **Trace focus.** `agent_input.task` holds the benign request **and** the
  injected line; the tool request is `calculator` with `expr = "6*7"`; the answer
  reflects the injected instruction.
- **Questions to ask.**
  1. Where exactly did the instruction enter the system?
  2. Does any event tag the injected line as untrusted?
- **Common misconception.** Believing the trace explains the model's reasoning.
- **Expected learning outcome.** Students trace *where* an instruction entered and
  explain that the trace records events, not intent.

### LAB-03 — Indirect Prompt Injection

- **Teaching objective.** The instruction arrives **through tool-returned
  content** — an extra hop: content → tool → tool result → model.
- **Before the lab.** Emphasise that this trace has **two** calls, and the second
  is refused.
- **Student activity.** Follow
  [`LAB-03-indirect-prompt-injection/README.md`](LAB-03-indirect-prompt-injection/README.md).
- **Trace focus.** Read: `allow` (`fs-read-workspace`) → `tool_executed` →
  `tool_result ok: true`. Write: `deny` (`fs-deny-outside`) → denied `tool_result`
  **with no `tool_executed`**. The read result is stored as a `result_hash`.
- **Questions to ask.**
  1. Which call has a `tool_executed` event, and which does not?
  2. Why is the note's text not present in the trace?
- **Common misconception.** Looking for a `tool_executed` for the denied write, or
  expecting the tool's returned content to be stored verbatim.
- **Expected learning outcome.** Students can describe the second hop and explain
  why the denied call leaves no execution event.

### LAB-04 — Tool Misuse

- **Teaching objective.** No injection is needed: a valid tool is requested with
  an **out-of-scope operation**, and policy stops it.
- **Before the lab.** Clarify that the requested path is only a string; nothing
  real is touched.
- **Student activity.** Follow
  [`LAB-04-tool-misuse/README.md`](LAB-04-tool-misuse/README.md).
- **Trace focus.** `tool_requested` `fs_sandbox` with
  `{"op":"write","path":"../../etc/passwd"}`; `deny` (`fs-deny-outside`);
  `tool_result ok: false`; **zero** `tool_executed` in the whole trace.
- **Questions to ask.**
  1. How many `tool_executed` events are there?
  2. Does a `deny` mean the tool ran and failed?
- **Common misconception.** Treating the denied `tool_result` as a tool failure,
  and conflating "the tool can" with "the agent may".
- **Expected learning outcome.** Students can show from the trace that a denied
  request never reached the tool.

### LAB-05 — Require Approval

- **Teaching objective.** The third decision: a legitimate request **held**
  pending authorization — neither allowed nor denied.
- **Before the lab.** Stress that no human/UI approves anything; the boundary is
  simulated through the policy engine.
- **Student activity.** Follow
  [`LAB-05-require-approval/README.md`](LAB-05-require-approval/README.md).
- **Trace focus.** `mock_db` read; `require_approval`
  (`db-read-requires-approval`); `tool_result ok: false` with an approval-required
  error; **no `tool_executed`**.
- **Questions to ask.**
  1. Which event shows the request was neither allowed nor denied?
  2. What is missing because approval was not granted?
- **Common misconception.** Assuming `require_approval` means the tool ran, or
  that it is the same as `deny`.
- **Expected learning outcome.** Students can distinguish "held" from "refused"
  and predict the missing event in each case.

### LAB-06 — Excessive Agency

- **Teaching objective.** An **authorized** action executes even though the task
  did not require it: authorization ≠ necessity.
- **Before the lab.** Note that the LAB-06 policy deliberately **allows** this one
  synthetic write, and that the change is confined to an in-memory database.
- **Student activity.** Follow
  [`LAB-06-excessive-agency/README.md`](LAB-06-excessive-agency/README.md).
- **Trace focus.** `mock_db` `DELETE FROM audit_log`; `allow`
  (`lab06-allow-audit-log-write`); `tool_executed`; `tool_result ok: true` with
  `side_effects = ["deleted 2 row(s) from audit_log"]`.
- **Questions to ask.**
  1. Which two events together prove the synthetic table changed?
  2. Does `allow` say anything about whether the action was *needed*?
- **Common misconception.** Reading `allow` as "correct", or assuming the policy
  failed.
- **Expected learning outcome.** Students can state that permission and necessity
  are different questions and cite the evidence for the execution.

### LAB-07 — Data Leakage

- **Teaching objective.** An authorized read followed by an authorized send still
  moves content across an **egress boundary**: authorization ≠ confidentiality.
- **Before the lab.** Set the safety frame explicitly (see §9).
- **Student activity.** Follow
  [`LAB-07-data-leakage/README.md`](LAB-07-data-leakage/README.md); inspect the
  second `tool_requested` closely.
- **Trace focus.** Read: `allow` (`lab07-allow-records-read`) → executed →
  `ok: true` (hash only). Send: `allow` (`lab07-allow-email-send`) → executed →
  `side_effects = ["sent 1 message to reports@example.invalid"]`. The record's
  content, including the marker, appears in the **send request's**
  `args_redacted.body`.
- **Questions to ask.**
  1. How many `policy_decision` events are there, and what was each?
  2. In which field is the observable evidence of the egress?
  3. Why is the marker visible at all (what does that say about a
     pattern-based redactor)?
- **Common misconception.** Calling this "real exfiltration", treating the marker
  as a real secret, or expecting the record in the `tool_result`.
- **Expected learning outcome.** Students can identify the egress boundary, the
  exact field carrying the content, and explain that both operations were
  permitted yet the content still crossed.

---

## 5. Core trace-reading teaching points

Reinforce these repeatedly; they are the spine of the whole sequence.

1. **Model response ≠ tool request.** A `model_response` (with
   `finish_reason: "tool_calls"`) can lead to a request, but they are distinct
   events.
2. **Tool request ≠ tool execution.** `tool_requested` alone proves nothing about
   execution.
3. **Policy decision precedes execution.** Always locate `policy_decision`
   **before** looking for `tool_executed`.
4. **`deny` means no execution.** In these labs a denied operation yields a
   `tool_result` (often `ok: false`) with **no** `tool_executed`.
5. **`require_approval` means no execution here.** LAB-05 shows a pending request
   is not an executed operation.
6. **`allow` + `tool_executed`.** Together these are the observable evidence that
   the tool actually ran.
7. **Side effects.** LAB-06 and LAB-07 show observable **synthetic** state
   changes via `side_effects`.
8. **Deterministic fixtures.** Repeated runs demonstrate deterministic mechanics,
   **not** distributions of real model behaviour.

---

## 6. Using the exercise set

`TRACE-READING-EXERCISES.md` has 48 numbered exercises (sets A–I), a per-lab
"what if" stretch section and a final integrated challenge, ordered beginner →
intermediate.

Suggested classroom uses:

- **Individual work** — students attempt sets A–C first, then discuss.
- **Pair work** — one student argues the answer, the other challenges it with
  evidence from the fragment.
- **Classroom projection** — walk a single exercise together, requiring the class
  to name the exact event and field.
- **Small-group trace analysis** — give each group a real `runs/*/trace.jsonl`
  and have them reconstruct the story.
- **Instructor-led discussion** — use the pair-comparison set (F) to surface the
  request/execution confusion.

Require students to **justify answers with observable trace evidence**. Do not ask
them to guess model intent beyond what the trace supports — the trace records
**what**, not **why**.

The **answer key is instructor-only** : keep
[`TRACE-READING-EXERCISES-ANSWER-KEY.md`](TRACE-READING-EXERCISES-ANSWER-KEY.md)
out of student handouts.

The [controlled-experiments learning module](CONTROLLED-EXPERIMENTS.md) is a
self-contained exercise of the same kind, one level more formal: students read a
specification, commit to an expected outcome, run one controlled comparison with
`agentsec experiment`, and explain the result while withholding any causal or
ranking claim. Its [answer key](CONTROLLED-EXPERIMENTS-ANSWER-KEY.md) is likewise
instructor-only.

The [specification-authoring challenge](SPECIFICATION-AUTHORING-CHALLENGE.md) is
the authoring counterpart: students write their own specification for LAB-05, get
it past the validator, predict the outcome and explain the result, keeping a
**design error** (exit `1`) apart from the four experiment **result** states (exit
`0`). Its
[answer key](SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md) is instructor-only.

---

## 7. Suggested marking rubric

An **instructional** rubric only. It is **not** a security score, a risk metric,
or a research measure.

| Criterion | Excellent | Satisfactory | Needs improvement |
|---|---|---|---|
| Event identification | Correctly identifies relevant events | Minor mistakes | Frequent mistakes |
| Request vs execution | Clearly distinguishes them | Usually distinguishes them | Frequently conflates them |
| Policy interpretation | Correctly explains decisions | Understands basic decisions | Misinterprets decisions |
| Evidence | Cites concrete trace evidence | Provides some evidence | Mostly unsupported |
| Side-effect interpretation | Correctly identifies observable effects | Mostly correct | Confuses request/result/effect |
| Trace reasoning | Follows event sequence logically | Mostly coherent | Jumps to conclusions |

---

## 8. Instructor discussion prompts

Use these to drive evidence-based discussion. (No answers here — see the answer
key for the exercise items.)

1. What event proves that a tool was **actually executed**?
2. Why can a `tool_result` exist **without** a `tool_executed` event?
3. What changes when policy returns `require_approval` instead of `deny`?
4. What evidence shows that LAB-06 actually changed sandbox state?
5. What exactly crosses the egress boundary in LAB-07, and where is it visible?
6. In LAB-02, where did the instruction enter — and does any event mark it as
   untrusted?
7. In LAB-03, why does one call have a `tool_executed` and the other not?
8. Why does the trace store a `result_hash` instead of the tool's raw content?
9. Why is `allow` a statement about permission, not about necessity?
10. What can these deterministic traces tell us — and what can they **not** tell
    us?

---

## 9. LAB-07 teaching boundary

> **LAB-07 is an authorized, synthetic, sandboxed demonstration of observable
> egress. It is not real-world data exfiltration, an autonomous leakage
> experiment, or a measurement of model propensity.**

Everything in LAB-07 is local and synthetic: the database and the email sink are
in-memory, the recipient uses the reserved `.invalid` domain, and the marker is an
educational fixture, not a secret. Teach it as a **trace-reading and data-flow**
lab, not as a vulnerability demonstration.

---

## 10. Research boundary

This material preserves the **Phase 17** decision:

- the current labs are **educational/reproducibility infrastructure**;
- deterministic mock fixtures demonstrate **mechanics**, not real LLM behavioural
  distributions;
- the labs are **not a benchmark**;
- the current project makes **no research-novelty claim**;
- previously closed research directions **remain closed**.

Do **not** reopen the research question or propose a research experiment while
teaching these labs. If a student raises a research idea, point them to the
process documented in `docs/development.md`: a genuinely different question or
boundary condition, plus a fresh hostile literature audit, **before** any
implementation.

---

## 11. Instructor preparation checklist

### Before class

- [ ] Repository available to students (clone/checkout).
- [ ] Python 3.11+ environment works (`py -m pip install -e ".[dev]"`).
- [ ] Test suite passes (`PYTHONPATH=src py -m pytest`).
- [ ] One lab runs end to end (for example LAB-00).
- [ ] Trace files can be generated (`runs/<run_dir>/trace.jsonl`).
- [ ] Students can read JSON/JSONL.
- [ ] Student materials distributed
      ([`labs/README.md`](README.md), [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md),
      [`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md), lab READMEs).
- [ ] Answer key kept instructor-only.

### During class

- [ ] Demonstrate one **benign** trace (LAB-01).
- [ ] Demonstrate one **denied** operation (LAB-04).
- [ ] Demonstrate one **approval** case (LAB-05).
- [ ] Demonstrate one successful **synthetic side effect** (LAB-06).
- [ ] Let students work through exercises, individually then in pairs.
- [ ] Discuss answers as **evidence-based** interpretation.

### After class

- [ ] Collect exercise responses if desired.
- [ ] Apply the rubric (§7).
- [ ] Discuss the most common misconceptions.
- [ ] Encourage students to re-run labs and inspect the traces themselves.

No deployment, network, credentials or external services are required.

---

## 12. Resource map

| Resource | Audience | Purpose |
|---|---|---|
| [`labs/README.md`](README.md) | Students | Cross-lab map and observables matrix. |
| [`TRACE-WALKTHROUGHS.md`](TRACE-WALKTHROUGHS.md) | Students | Event-by-event walkthrough of each real trace. |
| [`TRACE-READING-EXERCISES.md`](TRACE-READING-EXERCISES.md) | Students | Practice reading traces (no answers). |
| [`TRACE-READING-EXERCISES-ANSWER-KEY.md`](TRACE-READING-EXERCISES-ANSWER-KEY.md) | **Instructors only** | Answers, evidence and marking guidance for the exercises. |
| [`CONTROLLED-EXPERIMENTS.md`](CONTROLLED-EXPERIMENTS.md) | Students | Controlled-experiment module: control/treatment, the held-constant invariant, the four result states and a worked LAB-04 example. |
| [`CONTROLLED-EXPERIMENTS-ANSWER-KEY.md`](CONTROLLED-EXPERIMENTS-ANSWER-KEY.md) | **Instructors only** | Expected values and marking guidance for the controlled-experiment exercise. |
| [`SPECIFICATION-AUTHORING-CHALLENGE.md`](SPECIFICATION-AUTHORING-CHALLENGE.md) | Students | Author your own controlled-experiment specification for LAB-05 and see the validator reject an uncontrolled design. |
| [`SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md`](SPECIFICATION-AUTHORING-CHALLENGE-ANSWER-KEY.md) | **Instructors only** | Reference specification, expected values and validator messages for the authoring challenge. |
| `LAB-0X-.../README.md` | Students | Per-lab commands, questions and checklist. |
| `docs/development.md` | Instructors | Repository status and the Phase 17 research boundary. |

The single habit to build across the whole sequence: separate **what was
requested**, **what was decided**, **what executed**, and **what changed** — and
name the event that supports each claim.
