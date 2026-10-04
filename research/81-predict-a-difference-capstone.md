# PHASE 8C — PREDICT-A-DIFFERENCE CAPSTONE

*A documentation-and-composition-only capstone that closes the loop between
prediction and comparison: a student pre-registers how two runs will differ, then
runs the existing workflow and checks that prediction against `compare`. It adds
one getting-started step, an instructor-only answer-key entry, documentation
guards, and this record. **No runtime code was written.** Nothing was committed,
pushed or tagged.*

## 1. Objective

Add the next smallest substantive pedagogical step: teach students to make a
**falsifiable prediction about how two executions will differ** *before* looking
at the comparison output, then verify it with the existing `compare` command.
The phase shows how `run`, `predict` and `compare` compose into a single
evidence-based loop, without building any new runtime abstraction, comparison
algorithm, scoring, ranking, causal model or generalized prediction framework.

## 2. Reconnaissance

Read-only inspection before anything changed:

* **The commands already compose.** `run` produces a trace; `predict`
  (`prediction.check_prediction`, schema `"1"`) checks one trace; `compare`
  (`compare.compare_traces`) structurally compares two. None needed to change.
* **The LAB-04 two-policy pair is the cleanest deterministic difference.** The
  permissive example `configs/examples/lab04_tool_misuse_allow_all.yaml` and the
  shipped `labs/LAB-04-tool-misuse/config.yaml` run the **same** experiment
  (same task, fixture, agent) and differ only in policy, producing a real count
  delta and an execution difference. The already-established LAB-05 pair is
  structurally identical (delta 0, no `tool_executed` in either), so it is a
  weaker target for a *difference* prediction; it remains the contrast in step 6.
* **The difference is not expressible as a single-trace prediction.** The
  prediction schema describes one trace, so a "difference" prediction is written
  down by the student and verified against `compare`; no new prediction file was
  warranted. The shipped `configs/predictions/lab04.yaml` describes one side
  (the least-privilege trace) and is referenced so the student can confirm each
  side independently.
* **An instructor-only convention exists.**
  `labs/TRACE-READING-EXERCISES-ANSWER-KEY.md` is the repository's authoritative
  instructor-only answer key (the *Instructor Guide* deliberately holds no
  answers), so the expected observations belong there — not in the student page.
* **Guard convention.** `tests/test_getting_started.py` owns getting-started
  documentation invariants; `tests/test_trace_exercises.py` guards the answer
  key (and would fail on stray bolded exercise-answer ids, so the addition avoids
  them).

**Decision: composition-only.** The exercises are fully expressible with the
existing commands; no helper command was added (a helper would hide the
composition being taught), and no new prediction fixture was needed.

**Pre-existing conflict found.** `tests/cli/test_demo.py::
test_demo_json_leaves_no_traces_in_the_repository` asserts that
`runs/lab04_tool_misuse_allow_all/` never exists, yet the allow-all example
config **declares** that trace path and `labs/LAB-04-tool-misuse/README.md`
already documents running it directly. The guard therefore already conflicted
with the shipped docs before this phase; running the documented workflow creates
the (untracked) directory and trips the guard. The capstone is documented with an
explicit cleanup step, and the underlying guard is flagged for a follow-up fix
(see §14–§15) rather than changed here.

## 3. Selected lab pair and rationale

LAB-04 under `allow_all_v1` (A) versus LAB-04 under `least_privilege_v1` (B):

* Same lab — the policy is the only variable, so the difference is attributable
  to the comparison's own semantics and nothing else.
* Real, deterministic, falsifiable differences: event count, a present/absent
  `tool_executed`, and four evaluator fields.
* Requires no new lab, fixture, policy or configuration; reuses the config from
  the existing two-policy demonstration (step 5) and the shipped LAB-04 policy.

## 4. Existing mechanisms reused

* `agentsec run` — produces both traces through the existing stack.
* `agentsec compare` — `compare_traces` / `render_comparison`; position-only
  alignment, `ALIGNMENT_NOTE`, evaluator differences.
* `agentsec predict` + `configs/predictions/lab04.yaml` — optional per-side check
  of the least-privilege trace.

No trace reading, prediction matching, comparison or evaluator logic was
duplicated, and no new prediction schema, engine or CLI command was introduced.

## 5. Exact student workflow

`labs/GETTING-STARTED.md` §11, "Predict a difference before comparing":

* **Weak vs useful predictions** — contrast the unfalsifiable "the traces will be
  different" with a specific, checkable claim.
* **A. Predict** — four pre-registration questions (who allows/denies, who
  executes, same event count?, which evaluator differences?).
* **B. Run** — the two existing configs.
* **C. Compare** — `agentsec compare runs/lab04_tool_misuse_allow_all/trace.jsonl
  runs/lab04_tool_misuse/trace.jsonl`.
* **D. Verify** — check event counts, distribution, sequence and evaluator
  differences; optionally confirm the least-privilege side with `predict`.
* **E. Interpret** — which predictions were right/wrong, what evidence supports
  each, and what the comparison still does not establish, with the explicit
  boundary that a correct prediction does not prove causality and a structural
  difference is not a ranking.

`## 11. Check your setup stays healthy` was renumbered to `## 12`, keeping the
setup check last before "The one habit to build".

## 6. Implementation changes

**Runtime code: none.** No `src/**` file changed and no CLI command was added.

* `labs/GETTING-STARTED.md` — new `## 11. Predict a difference before comparing`
  section; check-setup renumbered to `## 12`.
* `labs/TRACE-READING-EXERCISES-ANSWER-KEY.md` — a short instructor-only
  "Predict-a-difference capstone — expected observations" section (a table of the
  real `compare` values plus an evidence-not-verdict note). No answer was placed
  in the student page.
* `tests/test_getting_started.py` — new `DIFFERENCE_*` constants and three guards
  (section heading present; run/compare commands, traces and referenced
  prediction/config documented and existing; LAB-04 link present and resolvable).
  No existing test weakened or rewritten.
* `README.md` — derived test-suite row 1192 → 1195.
* `research/81-predict-a-difference-capstone.md` — this record.

## 7. Actual end-to-end result

Executed exactly as documented (`compare` A = allow-all, B = least privilege):

* trace A: 12 events; trace B: 11 events; **delta +1**;
* `tool_executed` `A 1 / B 0` (`-1`); every other event type equal;
* sequence differences from index 6 (extra `tool_executed` in A), `only in A:
  index 11`;
* evaluator differences: `decisions.allow 1 -> 0`, `decisions.deny 0 -> 1`,
  `tool_results.denied 0 -> 1`, `tool_results.error 1 -> 0`.

Optional per-side check: `predict` on B with `configs/predictions/lab04.yaml`
reports **5 matched, 0 mismatched**, exit `0`. The comparison names *what*
changed and never *why* or *which is better*.

## 8. Test-count delta

**1192 → 1195 (+3)**, all in `tests/test_getting_started.py`. No new module, so
the architecture parametrisation is unchanged, and `tests/test_trace_exercises.py`
still passes unchanged.

## 9. Validation

Full battery at 1195 tests:

* `python -m pytest` — 1195 passed.
* `python -m agentsec labs check` — 8/8 labs.
* `ruff check src tests scripts` — clean.
* `python -m mypy` — no issues (43 source files).
* `python -m mkdocs build --strict` — exit 0.
* `python scripts/check_licensing.py` — 9/9.
* `python scripts/check_version.py` — 3/3 @ `0.1.0`.
* `python scripts/release_check.py --json` — READY WITH WARNINGS; blockers `[]`,
  warnings `["W12", "W7"]`.
* `git diff --check` — clean.

Determinism: `compare` and the optional `predict` were run twice and match;
neither trace is modified by either command.

## 10. Conceptual boundaries

The step states plainly that a correct prediction establishes only that the
observed traces matched what was predicted (not causality), and that a structural
difference does not establish which run is better, safer or more secure — the
comparison is descriptive and produces no ranking. No scoring, ranking or
security-metric language is introduced.

## 11. Protected invariants

Untouched: `scripts/release_check.py`, release warning detection, B5,
`pre_tag_check.py`, the release manifest, `licensing/manifest.toml`,
`.gitignore`, `.freebuff/project-id`, `schemas/**`, `.github/workflows/**`,
version declarations, tags, `compare_traces`, `TraceEvaluator`, existing lab
semantics, and the prediction schema (`PREDICTION_SCHEMA_VERSION = "1"`). No CI
changes, no scoring, no ranking, no security score, no causal model.

## 12. Cleanup

Build/test caches removed; no `site/`, `*.egg-info` or scratch files remain.
`runs/` output (including `runs/lab04_tool_misuse_allow_all/`) stays ignored.

## 13. Git/tag state

Working tree contains only the intended Phase 8C changes. Branch `v0.1.0-dev`;
tags unchanged (`v0.0.1`, `v0.1.0`). Nothing was committed, pushed, published or
tagged.

## 14. Limitations

* The capstone demonstrates one pair and one contrast; it is not an exhaustive
  matrix of observable differences.
* The "difference" prediction is checked by the reader against `compare` output,
  not by an automated per-difference checker — by design, since the prediction
  schema is single-trace.
* The fixtures are deterministic, so the evidence concerns the observed traces,
  not real model or policy behaviour.
* Running the example config writes `runs/lab04_tool_misuse_allow_all/` (untracked,
  gitignored). The demo test above asserts that directory never exists, so a
  student who runs the exercise and then the suite (without cleanup) will see one
  failing test. This is a **pre-existing** docs/guard inconsistency, not caused by
  this phase; the step documents `rm -rf runs/lab04_tool_misuse_allow_all` to
  restore a clean state.

## 15. Smallest sensible next step

Fix the pre-existing demo guard so it tests what it means: snapshot the `runs/`
tree, run the demo, and assert it added **no new** files — rather than asserting a
specific config's directory (which the docs legitimately create) never exists.
This is a small, correctness-preserving test change that removes the docs/test
conflict without weakening coverage; it should be its own focused phase. A
secondary, purely cosmetic follow-up would be to add a "what changed / what did
not" table to the LAB-04 page mirroring the capstone's four evaluator differences
and the single `tool_executed` delta.
