# PHASE 39 — PREDICT-THEN-COMPARE EVALUATION

*A small, read-only capability that lets a learner state observable expectations
**before** running a lab and check them against the resulting trace: a new
`agentsec predict <trace> <prediction>` command. It reuses the existing scenario
expectation system and evaluator, adds no new expectation model and no score,
and never executes anything. Nothing was committed, pushed or tagged.*

## 1. Motivation

Every existing comparison workflow is **retrospective**: `compare` asks "what
changed between these two traces?", and the exercises run first, read after.
Phase 8 adds the complementary, prospective workflow of a falsifiable prediction:
*state what you expect, then run, then see where you were right or wrong.* It is
the difference between inspecting a result and testing an expectation.

## 2. Reconnaissance

Read-only inspection before any code was written:

* **The expectation system already exists.** `scenarios/base.py` defines
  `ExpectedObservation` (the observable field set), `ObservationCheck`
  (`name`/`expected`/`observed`/`matched`), and `DeclarativeScenario.interpret`,
  which compares a run's observations against `expected`. `scenario.yaml`'s
  `expected` block is exactly a prediction, and `agentsec labs check` already
  checks the designer-authored version.
* **The evaluator is stable and observable.** `TraceEvaluator` →
  `EvaluationResult` exposes `status`, `metrics`, `decisions`, `tool_results`,
  `tool_calls`, `flags`, `warnings` — deterministic and read-only.
* **Two gaps for a *trace-only* check:** `agent_status` (`RunStatus`) is not on
  `EvaluationResult`, and `output_contains` needs the agent's answer text. Both
  are resolvable from the trace itself (`agent_output.answer_redacted`; the
  terminal event implies the run status).
* **Licensing.** `configs/**` and `labs/**.yaml` are MIT-covered; a **new
  top-level directory** would be uncovered and fail `check_licensing.py`. So
  predictions live under `configs/predictions/`.
* **Architecture guards.** The CLI must stay thin and import no execution layers;
  a new `src` module and a new `tests` module each add one parametrised case.

**Decision: GO WITH MODIFICATIONS** — reuse the expectation representation
rather than forking it; keep it trace-only and tiny.

## 3. Reuse of the existing expectation system

No second expectation model was created. `scenarios/base.py` gained two small,
**additive, behaviour-preserving** public helpers:

* `observation_checks(expected, observed)` — the scenario's own match rule
  (`requested_tools` by set equality, `output_contains` by substring, else exact
  equality), exposed so a trace-only caller reuses it instead of re-implementing
  it. `DeclarativeScenario.interpret` was refactored to call it (identical
  behaviour; existing scenario tests unchanged).
* `observations_from_evaluation(evaluation, *, output=None)` — builds the
  `ExpectedObservation` field mapping from an `EvaluationResult` alone (the
  run-based `_observations` reads the agent directly; `agent_status` is inferred
  from the evaluator's terminal outcome, `output_contains` from the trace's own
  `agent_output` text).

Neither touches policy, tool, trace or evaluator semantics.

## 4. Prediction artifact design

A prediction is a small YAML mapping of the existing observable fields, parsed
strictly into `ExpectedObservation` (`extra="forbid"`, so a made-up field such as
`risk_score` is a clean `ConfigError`). Example — `configs/predictions/lab04.yaml`:

```yaml
evaluation_status: completed
requested_tools:
  - fs_sandbox
policy_denials: 1
tool_executions: 0
tool_results_denied: 1
```

No score, threshold, confidence, severity, risk, similarity or ranking field
exists. Two more files demonstrate deliberate mismatches: `lab04_mismatch.yaml`
(wrongly expects `tool_executions: 1`) and `lab02_expect_denied.yaml` (wrongly
expects an injection to be denied).

## 5. CLI design

`agentsec predict <trace> <prediction> [--json]` — thin, read-only, mirroring
`compare`/`evaluate`; it never runs a lab (running stays `agentsec run`). The
human output lists, per configured field, `predicted` / `observed` / `MATCH` or
`MISMATCH`, then a summary. Exit codes: `0` when the comparison is produced
**regardless of matches** (a mismatch is an experimental result, like a denied
tool); `1` for a missing/malformed trace or prediction (`EvaluationError` /
`ConfigError`, printed `error: …` as the other commands do).

## 6. LAB-04 demonstration

```bash
agentsec run labs/LAB-04-tool-misuse/config.yaml
agentsec predict runs/lab04_tool_misuse/trace.jsonl configs/predictions/lab04.yaml
```

```text
  evaluation_status   predicted completed  observed completed  MATCH
  tool_executions     predicted 0          observed 0          MATCH
  policy_denials      predicted 1          observed 1          MATCH
  tool_results_denied predicted 1          observed 1          MATCH
  requested_tools     predicted ["fs_sandbox"] observed ["fs_sandbox"] MATCH
Summary: 5 matched, 0 mismatched (5 checks)
```

## 7. Deliberate mismatch

`configs/predictions/lab04_mismatch.yaml` expects the out-of-scope write to
execute; the trace shows it never did:

```text
  tool_executions   predicted 1  observed 0  MISMATCH
  tool_results_denied predicted 1 observed 1 MATCH
Summary: 1 matched, 1 mismatched (2 checks)
A mismatch is an experimental result, not a failure.
```

`configs/predictions/lab02_expect_denied.yaml` predicts a direct-injection run
will be denied; it is allowed and executed, so three fields mismatch
(`tool_executions`, `policy_denials`, `tool_results_denied`) — exit code stays
`0`, and no "better/worse/safer" wording is emitted.

## 8. Tests

New `tests/cli/test_prediction.py` (20 tests): prediction parsing (valid, unknown
field, missing file, non-mapping) → `ConfigError`; synthetic traces all-matched
and mismatched; `requested_tools` set semantics; `output_contains` substring
semantics; empty-prediction reporting; determinism; the trace stays byte-identical;
CLI human output; `--json`; malformed trace/prediction/missing trace → exit `1`;
mismatch → exit `0`; real LAB-04 integration (match and deliberate mismatch);
missing trace → `EvaluationError`. No `compare` test was duplicated.

**Test count: 1156 → 1181 (+25).** Breakdown: +20 for `tests/cli/test_prediction.py`,
+1 for the new `src/agentsec/prediction.py`
(`test_no_banned_dependency_in_source`), +1 for the new test module
(`test_no_banned_dependency_in_tests`), +3 for the extended
`tests/test_getting_started.py` guard.

## 9. Determinism

The result document contains no timestamps, absolute paths, temp-dir names, host
details or generated ids — identity is the trace's own `run_id`/`scenario` and
`event_count`. Checks are emitted in `ExpectedObservation` field order; keys are
stable. The `--json` output was run twice and was byte-identical.

## 10. Limitations

* A prediction **match is not evidence of security, correctness or
  effectiveness** — it only means the trace agreed with the fields the learner
  named. A mismatch is not a failure; it is an observation that the prediction did
  not match the trace.
* It is trace-only and single-trace: no re-run, no multi-trace suites, no
  cross-trace prediction, no history, no trending.
* `agent_status` is inferred from the evaluator's terminal outcome (so an
  `incomplete` trace has no agent-status value); `output_contains` uses the
  redacted `agent_output` text.
* No score, threshold, confidence, risk, similarity, effectiveness or ranking;
  no causal claim; no novelty, benchmark or publication claim.

## 11. Protected invariants

Untouched: `TraceEvaluator` semantics, `compare.py`/`demo.py`, policy/tool/trace
semantics, `schemas/**`, `scripts/release_check.py` and its warning detection,
the B5 assertion, `W7`/`W12`, `licensing/manifest.toml`, `.freebuff/project-id`,
the release manifest, the version declarations (`0.1.0`), and both
`.github/workflows/*.yml`. The `scenarios/base.py` change is additive and
behaviour-preserving. The gate stays **READY WITH WARNINGS**, `blockers: []`.

## 12. Validation

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1181 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 43 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 250 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| Predict (match) | `agentsec predict <LAB-04 trace> configs/predictions/lab04.yaml` | exit `0`, 5/5 matched |
| Predict (mismatch) | `… lab04_mismatch.yaml` | exit `0`, `tool_executions` MISMATCH |
| Determinism | `--json` run twice | byte-identical |

## 13. Exact files changed

```text
Added:
  src/agentsec/prediction.py
  tests/cli/test_prediction.py
  configs/predictions/lab04.yaml
  configs/predictions/lab04_mismatch.yaml
  configs/predictions/lab02_expect_denied.yaml
  research/78-predict-then-compare.md

Modified:
  src/agentsec/scenarios/base.py   (additive: observation_checks, observations_from_evaluation)
  src/agentsec/cli.py              (thin `predict` subcommand)
  docs/development.md              (CLI section)
  labs/GETTING-STARTED.md          (new §9 "Predict before you run"; §10 renumbered)
  tests/test_getting_started.py    (+3 documentation guards)
  README.md                        (derived test-count row 1156 -> 1181)
```

No `schemas/`, `TraceEvaluator`, `compare.py`, `demo.py`, policy, workflow or
release-control change.

## 14. Git / tag state

* Starting point was clean at HEAD `13b3c5a` (branch `v0.1.0-dev`).
* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* **No commit, push or publication was performed** — the changes remain in the
  working tree for the owner to commit manually.
