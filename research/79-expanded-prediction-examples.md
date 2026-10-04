# PHASE 8A — EXPANDED PREDICTION EXAMPLES

*A small, example/documentation/test-only follow-on to Phase 8. It adds four
student-facing prediction documents under `configs/predictions/`, each tied to an
existing lab with a *different* observable outcome, extends the existing
prediction tests and the getting-started guards, and changes no engine code,
schema or lab behaviour. Nothing was committed, pushed or tagged.*

## 1. Reconnaissance

Read-only inspection before anything was written:

* **The prediction engine is already complete and needs no change.**
  `src/agentsec/prediction.py` exposes `load_prediction`, `check_prediction` and
  `render_prediction` at `PREDICTION_SCHEMA_VERSION = "1"`. Every observable
  field an example could need — `policy_denials`,
  `policy_approvals_required`, `tool_executions`, `tool_results_ok`,
  `tool_results_denied`, `tool_results_pending_approval`, `tool_requests`,
  `requested_tools`, `output_contains`, `evaluation_status` — is already in
  `ExpectedObservation`. **No engine change was necessary, and none was made.**
* **Matching is reused, not forked.** `check_prediction` builds observations via
  `observations_from_evaluation(...)` and compares them with the scenario's own
  `observation_checks(...)`: `requested_tools` by set equality, `output_contains`
  by substring, everything else by exact equality.
* **Existing examples.** `configs/predictions/lab04.yaml` (matched: denial /
  containment), `lab04_mismatch.yaml` (deliberate exec-count error) and
  `lab02_expect_denied.yaml` (deliberate policy error).
* **Actual lab outcomes** (verified by evaluating the lab traces):

  | Lab | events | decisions | tool_results | tools | exec |
  |-----|--------|-----------|--------------|-------|------|
  | LAB-01 | 12 | allow 1 | ok 1 | calculator | 1 |
  | LAB-02 | 12 | allow 1 | ok 1 | calculator | 1 |
  | LAB-03 | 17 | allow 1, deny 1 | ok 1, denied 1 | fs_sandbox | 1 |
  | LAB-04 | 11 | deny 1 | denied 1 | fs_sandbox | 0 |
  | LAB-05 | 11 | require_approval 1 | pending_approval 1 | mock_db | 0 |
  | LAB-06 | 12 | allow 1 | ok 1 | mock_db | 1 |
  | LAB-07 | 18 | allow 2 | ok 2 | mock_db, mock_email | 2 |

* **Coverage gap.** The existing examples cover only *denial* and a *denial
  error*; they do not show an approval hold, a run mixing an allowed and a denied
  request, or a run using two different tools. Those are three genuinely
  different observation types, so the expansion adds real value.
* **Licensing.** `configs/**` is MIT-covered, so new prediction files under
  `configs/predictions/` need no `licensing/manifest.toml` edit (confirmed 9/9,
  250 files). No new top-level directory was introduced.
* **Docs/MkDocs.** `docs_dir` is `labs/`; the predict step lives in
  `labs/GETTING-STARTED.md` §9 and links to `docs/development.md` as inline code
  (linking to files outside `docs_dir` would break `mkdocs build --strict`).

## 2. Candidate labs considered

| Candidate | Observation type | Verdict |
|-----------|------------------|---------|
| **LAB-05** | approval held (`require_approval` / `pending_approval`) | **selected** — the third policy outcome, distinct from allow and deny |
| **LAB-03** | mixed allow + deny in one run | **selected** — the only lab with both outcomes |
| **LAB-07** | two different tools, both allowed and executed | **selected** — `requested_tools` set matching with >1 tool |
| LAB-06 | allow + execute | rejected — structurally duplicates LAB-01/allow|
| LAB-01 | allow + execute | rejected — already the "happy path" a learner runs first |
| LAB-02 (matched) | allow + execute despite injection | rejected — the mismatch example already teaches "the policy did not trip" |
| LAB-04 (matched) | deny | rejected — already the shipped matched example |

## 3. Selected examples and rationale

Four new files (three matched, one deliberate mismatch):

* `configs/predictions/lab05_expect_approval.yaml` — matched. LAB-05's database
  read is **held** `pending_approval`, never executed; `policy_denials: 0`,
  `tool_executions: 0`, `policy_approvals_required: 1`,
  `tool_results_pending_approval: 1`, `output_contains: "waiting for approval"`.
  Teaches that an approval hold is a third outcome, not a denial.
* `configs/predictions/lab05_expect_denied.yaml` — **deliberate mismatch**. It
  guesses a denial for the same LAB-05 trace. Observed: `policy_denials` is 0 and
  `tool_results_denied` is 0, so two checks mismatch — the lesson that
  `require_approval` ≠ `deny`.
* `configs/predictions/lab03_expect_allowed_then_denied.yaml` — matched. LAB-03
  makes **two** `fs_sandbox` requests in one run: the note read is allowed and
  executed, the injected out-of-scope write is denied. `tool_requests: 2`,
  `tool_executions: 1`, `tool_results_ok: 1`, `tool_results_denied: 1`.
* `configs/predictions/lab07_expect_two_tools.yaml` — matched. LAB-07 uses **two
  different tools** (`mock_db`, `mock_email`), both allowed and executed;
  `tool_executions: 2`, `tool_results_ok: 2`. Teaches that a matched prediction
  says only that the trace agreed — it does not mean the run was safe.

No new lab was created; every example is checked against an existing lab's real
trace.

## 4. Exact files changed

Added:

* `configs/predictions/lab05_expect_approval.yaml`
* `configs/predictions/lab05_expect_denied.yaml`
* `configs/predictions/lab03_expect_allowed_then_denied.yaml`
* `configs/predictions/lab07_expect_two_tools.yaml`
* `research/79-expanded-prediction-examples.md` (this record)

Modified:

* `tests/cli/test_prediction.py` — new lab config/prediction constants and six
  tests (three matched integrations, one deliberate mismatch, one JSON
  determinism, one "no tracked writes"). Existing tests untouched.
* `labs/GETTING-STARTED.md` — §9 gains a new numbered item listing the expanded
  examples and a pointer to the CLI reference; no section was renumbered.
* `tests/test_getting_started.py` — one new guard (`PREDICT_EXAMPLES`) and a
  docstring note.
* `README.md` — the derived test-suite row 1181 → 1188.

No engine, schema, lab, policy, `src/**`, release, CI or manifest file changed.

## 5. Prediction behaviour

Each new matched prediction reports `mismatched: []` and exits `0`:

* LAB-05 approval: 7 checks, 7 matched.
* LAB-03 mixed: 8 checks, 8 matched.
* LAB-07 two tools: 5 checks, 5 matched.

`--json` prints `json.dumps(result, indent=2)`; two runs on the same inputs are
byte-identical. The result carries no timestamps, absolute paths or generated
ids, so it is deterministic.

## 6. Mismatch behaviour

`configs/predictions/lab05_expect_denied.yaml` against the real LAB-05 trace
reports `policy_denials` (predicted 1, observed 0) and `tool_results_denied`
(predicted 1, observed 0) as `MISMATCH`, while `tool_executions: 0` matches. The
summary line is `1 matched, 2 mismatched (3 checks)`, it prints "A mismatch is an
experimental result, not a failure.", and the command still exits `0`. A mismatch
is a produced result, not an error.

## 7. Test-count delta

**1181 → 1188 (+7).**

* `tests/cli/test_prediction.py`: +6 (20 → 26).
* `tests/test_getting_started.py`: +1.
* No new `src` or `tests` module, so the architecture parametrisation is
  unchanged.

## 8. Validation results

Full battery, all green at 1188 tests:

* `python -m pytest` — 1188 passed.
* `python -m agentsec labs check` — 8/8 labs.
* `ruff check src tests scripts` — clean.
* `python -m mypy` — no issues (43 source files).
* `python -m mkdocs build --strict` — exit 0.
* `python scripts/check_licensing.py` — 9/9 @ 250 files.
* `python scripts/check_version.py` — 3/3 @ `0.1.0`.
* `python scripts/release_check.py --json` — READY WITH WARNINGS; blockers `[]`,
  warnings `["W12", "W7"]`.
* `git diff --check` — clean.

Every newly documented example was executed against its real lab trace: the three
matched examples report no mismatches; the LAB-05 mismatch example reports the two
expected mismatches; each exits `0`; each `--json` run is byte-identical on
repeat; no tracked file changed.

## 9. Protected invariants

Nothing in the protected list was touched: release controls,
`scripts/release_check.py`, warning detection, B5, `pre_tag_check.py`, the release
manifest, `licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`,
`schemas/**`, `.github/workflows/**`, version declarations, tags,
`compare_traces`, `TraceEvaluator`, existing lab semantics and the existing
prediction schema (`PREDICTION_SCHEMA_VERSION = "1"`). No CI changes, no runtime
redesign, no prediction scoring, no ranking, no better/worse/safer language.

## 10. Cleanup and git/tag state

Working tree contains only the Phase 8A changes listed in §4. Build/test caches
were removed. Tags are unchanged (`v0.0.1`, `v0.1.0`); branch is `v0.1.0-dev`.
Nothing was committed, pushed, published or tagged.

## 11. Limitations

* The examples are four documents covering four observation patterns, not an
  exhaustive matrix; `event_count`, `reached_step_limit`, `agent_status` and
  `produced_final_output` remain unexercised as *documented* examples (they are
  covered by unit tests).
* A match establishes only that the named fields agreed with the trace — it is
  not evidence of safety, correctness or effectiveness, and it establishes no
  causality.
* The examples are tied to the current mock fixtures; if a lab's fixture changes,
  the example and its test must change with it (the integration tests make that
  fail loudly).

## 12. Smallest sensible next step

Exercise one more genuinely distinct observable — `agent_status` /
`reached_step_limit` — by adding a prediction for a lab that stops at the step
limit, **only if** an existing lab actually produces that outcome; otherwise add
nothing. If no existing lab reaches that state, the honest next step is to stop:
the prediction vocabulary is demonstrated end to end, and manufacturing a lab to
produce a state would violate the "no new lab merely for an example" rule.
