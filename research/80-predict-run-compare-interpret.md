# PHASE 8B — PREDICT → RUN → COMPARE → INTERPRET

*A documentation-and-composition-only follow-on to Phases 8 and 8A. It adds one
getting-started step that composes the existing `run`, `predict` and `compare`
commands into a single learning workflow over the existing LAB-01/LAB-05 pair,
plus documentation guards and this record. **No runtime code was written.**
Nothing was committed, pushed or tagged.*

## 1. Objective

Make the learning sequence explicit end to end: a student should be able to
(1) state a prediction about a lab outcome, (2) run the lab, (3) check the
prediction against the resulting trace, (4) compare that trace with a second
existing trace, and (5) interpret what the combined evidence establishes and
what it does **not**. The phase is pedagogical; it introduces no scoring,
ranking, causal model, "better/worse/safer" conclusion or new evaluation model.

## 2. Reconnaissance

Read-only inspection before anything was changed:

* **Every primitive already exists.** `run` (`cli.py::_cmd_run`) produces a
  trace; `predict` (`cli.py::_cmd_predict` → `prediction.check_prediction`)
  checks a prediction against an existing trace; `compare`
  (`cli.py::_cmd_compare` → `compare.compare_traces`) structurally compares two
  traces. Each is deterministic, read-only with respect to repository source,
  and exits `0` on a produced result (including a prediction mismatch).
* **The prediction engine and schema are complete.** `prediction.py` at
  `PREDICTION_SCHEMA_VERSION = "1"` needs no change; the 8A example
  `configs/predictions/lab05_expect_approval.yaml` already predicts exactly the
  LAB-05 approval boundary this workflow verifies.
* **The comparison pair already exists.** `labs/GETTING-STARTED.md` step 8
  already compares LAB-01 against LAB-05; the pair shares the least-privilege
  policy, needs no new fixture/policy/lab, and differs structurally (LAB-01
  allows and executes a `calculator` call; LAB-05 holds a `mock_db` read for
  approval and never executes).
* **Licensing / MkDocs.** The change touches `labs/**` (MIT) and `research/**`
  (CC-BY), both already covered; no manifest edit and no new top-level directory.
  `docs_dir` is `labs/`, so the step links to `docs/development.md` as inline
  code only.
* **Guard convention.** `tests/test_getting_started.py` owns the
  getting-started documentation invariants via its `_section(heading)` helper,
  so the new step is guarded there rather than in a new module.

**Decision: composition-only.** The workflow is fully expressible with the
existing commands, so no runtime code, and no one-command helper (a helper would
hide the very composition the exercise teaches).

## 3. Selected labs and rationale

LAB-01 vs LAB-05, the pair already established in step 8:

* LAB-01 **allows and executes** an authorized calculator call (12 events).
* LAB-05 **reaches the approval boundary**: its `mock_db` read is answered
  `require_approval`, becomes a `pending_approval` result, and never executes
  (11 events).
* They share the shipped `least_privilege_v1` policy and require no new fixture,
  config, policy or lab.

The prediction checked is LAB-05's own `lab05_expect_approval.yaml`, so the
prediction and the comparison address the same run.

## 4. Existing mechanisms reused

* `agentsec run` — produces the two traces through the existing MVP stack.
* `agentsec predict` — `load_prediction` + `check_prediction` +
  `render_prediction`; the scenario's own `observation_checks` match rule.
* `agentsec compare` — `compare_traces` + `render_comparison`; position-only
  alignment, `ALIGNMENT_NOTE`, evaluator differences.
* `configs/predictions/lab05_expect_approval.yaml` — the Phase 8A example.

No trace reading, prediction matching, comparison, or evaluator logic was
duplicated.

## 5. Exact workflow

Documented as `labs/GETTING-STARTED.md` §10, in five labelled parts:

* **A. Predict** — read `configs/predictions/lab05_expect_approval.yaml`.
* **B. Run** — `agentsec run` for LAB-01 and for LAB-05.
* **C. Verify** — `agentsec predict runs/lab05_require_approval/trace.jsonl
  configs/predictions/lab05_expect_approval.yaml`.
* **D. Compare** — `agentsec compare runs/lab01_benign/trace.jsonl
  runs/lab05_require_approval/trace.jsonl`.
* **E. Interpret** — four questions, with the explicit note that a match means
  only that the trace agreed with the named fields and a comparison means only
  that two traces differ structurally — neither establishes causality, which lab
  or policy is better, which is safer, or why.

`## 10. Check your setup stays healthy` was renumbered to `## 11`, keeping the
setup check last before "The one habit to build". Since the new step is inserted
between predict (§9) and check-setup, §10 is the next sequential number.

## 6. Implementation changes

**Runtime code: none.** No `src/**` file changed, and no new CLI command was
added. Changes:

* `labs/GETTING-STARTED.md` — new `## 10. Predict → Run → Compare → Interpret`
  section; `## 10. Check your setup stays healthy` renumbered to `## 11`.
* `tests/test_getting_started.py` — new constants (`COMPOSE_*`) and three
  guards: heading present; workflow commands/prediction/traces documented and
  the prediction file exists; both LAB links present and resolvable. Docstring
  extended. No existing test weakened or rewritten.
* `README.md` — derived test-suite row 1188 → 1191.
* `research/80-predict-run-compare-interpret.md` — this record.

## 7. Actual end-to-end result

Executed exactly as documented:

* `predict` on the fresh LAB-05 trace: **7 matched, 0 mismatched (7 checks)**,
  exit `0`.
* `compare` LAB-01 (A) vs LAB-05 (B), exit `0`:
  * event counts `A 12 / B 11`, delta `+1`;
  * `tool_executed` `A 1 / B 0` (`-1`); every other event type equal;
  * positional sequence differences at indices 6–10 plus `only in A: index 11`;
  * evaluator differences: `decisions.allow 1 -> 0`,
    `decisions.require_approval 0 -> 1`, `tool_results.ok 1 -> 0`,
    `tool_results.pending_approval 0 -> 1`, `tool_calls.calculator 1 -> None`,
    `tool_calls.mock_db None -> 1`.

The comparison names *what* changed (an extra executed event in A, a policy
boundary difference) and never *why* or *which is better*.

## 8. Test-count delta

**1188 → 1191 (+3)**, all in `tests/test_getting_started.py`. No new module, so
the architecture parametrisation is unchanged.

## 9. Validation

Full battery at 1191 tests:

* `python -m pytest` — 1191 passed.
* `python -m agentsec labs check` — 8/8 labs.
* `ruff check src tests scripts` — clean.
* `python -m mypy` — no issues (43 source files).
* `python -m mkdocs build --strict` — exit 0.
* `python scripts/check_licensing.py` — 9/9 (file count unchanged; no new file
  outside the already-covered globs except this record's CC-BY path).
* `python scripts/check_version.py` — 3/3 @ `0.1.0`.
* `python scripts/release_check.py --json` — READY WITH WARNINGS; blockers `[]`,
  warnings `["W12", "W7"]`.
* `git diff --check` — clean.

Determinism: `compare` and the human `predict` output were run twice and match;
neither trace was modified.

## 10. Conceptual boundaries

The section states explicitly: a **prediction** establishes only whether the
observed trace matched the predefined expectation; a **comparison** establishes
only whether two traces differ structurally under the existing position-only
semantics. **Neither** establishes causality, which lab or policy is better,
which is safer, *why* an agent behaved as it did, or any general security
conclusion beyond the observed evidence. No "better/worse/safer/caused/proves"
language is used except to say what the evidence does **not** establish.

## 11. Protected invariants

Untouched: `scripts/release_check.py`, release warning detection, B5,
`pre_tag_check.py`, the release manifest, `licensing/manifest.toml`,
`.gitignore`, `.freebuff/project-id`, `schemas/**`, `.github/workflows/**`,
version declarations, tags, `compare_traces`, `TraceEvaluator`, existing lab
semantics, and the prediction schema (`PREDICTION_SCHEMA_VERSION = "1"`). No CI
changes, no scoring, no ranking, no security score, no causal model, no policy
effectiveness metric, no better/worse/safer classification.

## 12. Cleanup

Build/test caches removed; no `site/`, `*.egg-info` or scratch files remain.
`runs/` output stays ignored and is documented as the normal run location.

## 13. Git/tag state

Working tree contains only the intended Phase 8B changes (plus the still-uncommitted
Phase 8A files, left untouched). Branch `v0.1.0-dev`; tags unchanged
(`v0.0.1`, `v0.1.0`). Nothing was committed, pushed, published or tagged.

## 14. Limitations

* The exercise demonstrates one pair (LAB-01/LAB-05) and one prediction; it does
  not enumerate every observation type.
* A prediction match and a structural comparison are both evidence about the
  *observed trace*, not about a real model, a real policy or a real board
  security posture — the fixtures are deterministic.
* The interpretation questions are unguided by design (no answers are given), so
  correctness depends on an instructor or the reader.

## 15. Smallest sensible next step

Add a short "common misreadings" note to the interpret step (or a sibling page)
that names the two most likely wrong conclusions — "the comparison shows LAB-01
is the better/safer run" and "the prediction match proves the run is secure" —
and explains why each is unjustified. This is documentation only; if it grows a
test, extend `tests/test_getting_started.py`, and stop there rather than building
new runtime machinery.

## 16. Finalization refinement — common misreadings

The smallest sensible next step from §15 was then implemented as shipped: the
interpret step gained a short **"Common misreadings"** note naming the two
predictable but unjustified conclusions — "LAB-01 is the better/safer run" (the
comparison is descriptive and produces no security ranking) and "the prediction
match proves the run is secure" (a match only means the observed trace agreed
with the predicted observations). Wording stays within the existing educational
framing; no new security terminology, runtime code, scoring, ranking or metric
was added. `tests/test_getting_started.py` gained one stable invariant
(`test_getting_started_keeps_the_common_misreadings_note`) checking the note's
heading remains in the composed section, so the test count moved 1191 → 1192.
The README derived test row was updated to match. No new research record was
created; this refinement is folded into the existing Phase 8B record.
