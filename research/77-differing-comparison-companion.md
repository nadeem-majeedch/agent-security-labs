# PHASE 38 — DIFFERING-COMPARISON COMPANION EXERCISE

*The companion to Phase 7K: a student-facing exercise comparing two existing labs
whose traces genuinely differ, so learners see what `agentsec compare` surfaces
when a difference exists. It is a documentation + guard change only — no runtime,
comparison, policy, config, schema or release-control file was touched. Nothing
was committed, pushed or tagged.*

## 1. Reconnaissance

Read-only inspection before choosing a pair:

* **Compare semantics** (`src/agentsec/compare.py`) report event counts, the
  event-type distribution, the ordered sequence (aligned **by position only**)
  and the differences the existing `TraceEvaluator` already produces (status,
  decisions, tool results, tool calls, flags, warnings). No score, ranking or
  payload diff.
* **Actual traces** (from real runs of the existing configs):

  | Lab | scenario | events | decisions | results | executions |
  | --- | --- | --- | --- | --- | --- |
  | LAB-01 | `LAB-01-benign-agent` | 12 | allow 1 | ok 1 | 1 |
  | LAB-02 | `LAB-02-direct-prompt-injection` | 12 | allow 1 | ok 1 | 1 |
  | LAB-03 | `LAB-03-indirect-prompt-injection` | 17 | allow 1, deny 1 | ok 1, denied 1 | 1 |
  | LAB-04 | `LAB-04-tool-misuse` | 11 | deny 1 | denied 1 | 0 |
  | LAB-05 | `LAB-05-require-approval` | 11 | require_approval 1 | pending_approval 1 | 0 |
  | LAB-06 | `LAB-06-excessive-agency` | 12 | allow 1 | ok 1 | 1 |
  | LAB-07 | `LAB-07-data-leakage` | 18 | allow 2 | ok 2 | 2 |
* **Existing coverage** — `tests/cli/test_compare.py` already compares LAB-01 vs
  LAB-04 (`test_compare_real_lab_pair_surfaces_the_difference`) plus same-lab
  policy pairs.

## 2. Candidate pairs considered

| Pair | Count delta | Sequence | Evaluator differences | Notes |
| --- | --- | --- | --- | --- |
| LAB-01 vs LAB-02 (Phase 7K) | +0 | identical | none | the "no difference" case — already used |
| LAB-01 vs LAB-04 | +1 | shifted | allow/deny, ok/denied, tool calls | clearest, but **duplicates the existing test pair** |
| LAB-04 vs LAB-05 | +0 | identical | deny/require_approval, denied/pending, tool calls | no *structural* difference |
| LAB-03 vs LAB-04 | +6 | shifted | allow, ok, tool-call counts | real difference, same tool `fs_sandbox`, but needs explaining two complex injection/misuse labs |
| **LAB-01 vs LAB-05** | **+1** | **shifted** | **allow/require_approval, ok/pending, tool calls** | real difference; not in any test; both labs share the `least_privilege_v1` policy |

## 3. Selected pair and justification

**LAB-01 vs LAB-05.**

* No new config and no fixture change — both labs' existing `config.yaml` files
  are used verbatim.
* Deterministic comparison output (fixed fixtures; verified by repeated runs).
* A clear observable structural difference: event-count delta `+1`, a
  `tool_executed` present in A and absent in B, a positional shift in the
  sequence, and several evaluator differences.
* **Does not duplicate an existing test** (LAB-01 vs LAB-04 is the tested pair);
  the `tests/test_getting_started.py` guards are extended, but no compare-behaviour
  test is added because the behaviour is unchanged.
* One shared policy — both labs run `least_privilege_v1`, so the difference stems
  from the *operation and its decided outcome*, not from a second policy file.
* It reuses LAB-01 from Phase 7K, giving a crisp two-step arc: the *same* Trace A
  compared against a structurally identical lab (LAB-02) and then against a lab
  that differs (LAB-05).
* Interesting without a "better/worse" judgement: it names what changed, not
  which run is preferable.

## 4. Exact commands

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml
PYTHONPATH=src py -m agentsec run labs/LAB-05-require-approval/config.yaml
PYTHONPATH=src py -m agentsec compare \
  runs/lab01_benign/trace.jsonl \
  runs/lab05_require_approval/trace.jsonl
```

Traces land in the git-ignored `runs/` directory; nothing tracked is written.

## 5. Actual comparison result

```text
Trace A   scenario: LAB-01-benign-agent            events: 12
Trace B   scenario: LAB-05-require-approval        events: 11

Event counts
  A: 12   B: 11   delta: +1

Event-type distribution
  tool_executed      A 1  B 0  (+1)

Sequence differences
  index 6: A tool_executed | B tool_result
  index 7: A tool_result | B model_request
  index 8: A model_request | B model_response
  index 9: A model_response | B agent_output
  index 10: A agent_output | B run_completed
  only in A: index 11: run_completed

Evaluator differences
  decisions.allow: 1 -> 0
  decisions.require_approval: 0 -> 1
  tool_results.ok: 1 -> 0
  tool_results.pending_approval: 0 -> 1
  tool_calls.calculator: 1 -> None
  tool_calls.mock_db: None -> 1
```

The command exited `0`; two consecutive runs rendered byte-identical output.

## 6. Educational interpretation

Two labs whose operations and outcomes differ produce a comparison with a real
structural difference: a count delta, a changed event type (`tool_executed`),
a positional shift, and differing evaluator fields. LAB-01's calculator request
was authorized and **executed**; LAB-05's database read was **held for approval**
and never executed. The comparison surfaces that difference and nothing more.

## 7. Explicit limitations

* The comparison is **descriptive**: it reports *what* changed, never *why*, and
  never which run is better — there is no score or ranking.
* Events are aligned **by position only**; the shift is reported literally and is
  **not** a claim that index 6 "means" the same thing in both traces.
* It does not diff payloads or content, and does not interpret the shift as a
  causal relationship.
* Only LAB-01 and LAB-05 are demonstrated; no other lab changed.
* No novelty, effectiveness, security, benchmark or publication claim is made.

## 8. Files changed

```text
Added:
  research/77-differing-comparison-companion.md   (this record)

Modified:
  labs/GETTING-STARTED.md        (new §8 "Compare two labs that differ";
                                  §9 renumbered)
  tests/test_getting_started.py  (+3 documentation guards, plus a section helper)
  README.md                      (derived test-count row 1153 -> 1156)
```

No `src/agentsec/**` (including `compare.py`), `TraceEvaluator`, policy, config,
schema, lab runtime, licensing, workflow or version change.

## 9. Test-count delta

**1153 → 1156 (+3).** The three new guard functions were added to the existing
getting-started guard (`tests/test_getting_started.py`) — no new guard module, and
no compare-behaviour test (the runtime is unchanged and
`tests/cli/test_compare.py` already covers real-lab comparison). The README's
derived test-count row was updated via the existing `tests/test_readme.py`
mechanism; no second hard-coded count.

## 10. Validation results

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1156 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 244 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| The exercise | run LAB-01, LAB-05, then `compare` | exit `0`; deterministic; output as §5 |

## 11. Protected invariants

Untouched: `src/agentsec/**` (including `compare.py`), `TraceEvaluator`,
`read_events` semantics, the policy files, `scripts/release_check.py` and its
warning detection, the B5 exact-warning assertion, `W7`/`W12` (still accepted),
`licensing/manifest.toml`, `.freebuff/project-id`, `schemas/**`, the release
manifest, the version declarations (`0.1.0`), the lab runtime semantics, and both
`.github/workflows/*.yml`. The gate stays **READY WITH WARNINGS** with
`blockers: []`.

## 12. Artifact cleanup

Removed the `site/` directory written by `mkdocs build --strict` and all
`__pycache__` directories, plus `.mypy_cache`, `.ruff_cache`, `.pytest_cache`,
`build`, `dist`, `htmlcov` and `.mkdocs-build`, and the temporary comparison text
files. The `runs/` traces are git-ignored and were left as the labs' normal
output. Licensing was re-confirmed after cleanup; no generated artifacts or
scratch directories remain.

## 13. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` — unchanged.
* `v0.0.1` and `v0.1.0` are **unchanged**; `git rev-parse v0.1.0^{commit}` is
  `3d731b0dffece499cc54a22d51701cdeecdce39f`.
* No tag was created, modified, deleted or moved.

## 14. Confirmation

No commit was made, no push was performed, no tag was created/moved/deleted, and
no publication or release action occurred. The change remains in the working tree
alongside the earlier uncommitted Phase 6A–7K work.
