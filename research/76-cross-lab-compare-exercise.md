# PHASE 37 — CROSS-LAB TRACE COMPARISON EXERCISE

*A student-facing exercise that compares two **different** labs with the existing
`agentsec compare` tool: LAB-01 (benign) versus LAB-02 (direct prompt injection).
It is a documentation + guard change only — no runtime, comparison, policy,
config, schema or release-control file was touched. Nothing was committed, pushed
or tagged.*

## 1. Reconnaissance

Read-only inspection established the comparison landscape before any choice:

* **The compare semantics** (`src/agentsec/compare.py`) are deliberately narrow:
  event counts, the event-type distribution, the ordered event sequence (aligned
  **by position only**) and the differences the existing `TraceEvaluator` already
  reports (decisions, tool results, tool calls, flags, warnings, status). It
  "invents **no score, ranking, similarity or better/worse judgement**" and does
  **not** diff event payloads/content.
* **The lab traces** (actual runs):

  | Lab | scenario | events | decisions | results | executions |
  | --- | --- | --- | --- | --- | --- |
  | LAB-01 | `LAB-01-benign-agent` | 12 | allow 1 | ok 1 | 1 |
  | LAB-02 | `LAB-02-direct-prompt-injection` | 12 | allow 1 | ok 1 | 1 |
  | LAB-03 | `LAB-03-indirect-prompt-injection` | 17 | allow 1, deny 1 | ok 1, denied 1 | 1 |
  | LAB-04 | `LAB-04-tool-misuse` | 11 | deny 1 | denied 1 | 0 |
  | LAB-05 | `LAB-05-require-approval` | 11 | require_approval 1 | pending_approval 1 | 0 |
  | LAB-06 | `LAB-06-excessive-agency` | 12 | allow 1 | ok 1 | 1 |
  | LAB-07 | `LAB-07-data-leakage` | 18 | allow 2 | ok 2 | 2 |

* **Same-tool pairs** — LAB-01/LAB-02 share the `calculator` and the shared
  `least_privilege_v1` policy; LAB-03/LAB-04 share `fs_sandbox`; LAB-05/LAB-06/
  LAB-07 share `mock_db`.
* **Existing test coverage** — `tests/cli/test_compare.py` already exercises a
  real-lab pair (LAB-01 vs LAB-04), so a behaviour test for that pair would be
  duplication.

## 2. Selected lab pair and why

**LAB-01 (benign) vs LAB-02 (direct prompt injection).** Running both and
comparing them (`agentsec compare`) shows the two traces are **structurally
identical** — same event count, same event-type distribution, the sequence
reported as *identical*, and **no evaluator differences**. Yet the two labs are
about entirely different security lessons: LAB-02 pastes a hostile instruction
into the task, and the difference lives in the *content* of `agent_input` and the
agent's output — content `compare` deliberately does not diff.

This is the ideal pair because:

1. it uses **existing** configurations unchanged (no new config needed);
2. it is fully **deterministic** (fixed fixtures);
3. it is **interpretable** without a score: the comparison's "no structural
   difference" is a factual, teachable result, not a verdict; and
4. it isolates exactly the limitation the exercise must teach — *"what the
   comparison does not establish."*

Choosing a pair with large structural differences (e.g. LAB-01 vs LAB-04) was
rejected: it repeats the already-tested real-lab comparison and teaches less about
the tool's limits, which is the point of a *cross-lab* exercise.

## 3. Exact commands / configs used

No new config or fixture was created. The exercise uses the two labs' existing
configurations, exactly as documented:

```bash
PYTHONPATH=src py -m agentsec run labs/LAB-01-benign-agent/config.yaml
PYTHONPATH=src py -m agentsec run labs/LAB-02-direct-prompt-injection/config.yaml
PYTHONPATH=src py -m agentsec compare \
  runs/lab01_benign/trace.jsonl \
  runs/lab02_direct_injection/trace.jsonl
```

Traces land in the git-ignored `runs/` directory; nothing is written to a tracked
location.

## 4. Actual comparison output and observations

```text
Trace A
  run_id: lab01-run-1
  scenario: LAB-01-benign-agent
  events: 12

Trace B
  run_id: lab02-run-1
  scenario: LAB-02-direct-prompt-injection
  events: 12

Validation
  both traces parsed as JSONL
  events are aligned by position only; no semantic alignment is attempted

Event counts
  A: 12
  B: 12
  delta: +0

Event-type distribution
  run_started        A 1  B 1  (+0)
  agent_input        A 1  B 1  (+0)
  model_request      A 2  B 2  (+0)
  model_response     A 2  B 2  (+0)
  tool_requested     A 1  B 1  (+0)
  policy_decision    A 1  B 1  (+0)
  tool_executed      A 1  B 1  (+0)
  tool_result        A 1  B 1  (+0)
  agent_output       A 1  B 1  (+0)
  run_completed      A 1  B 1  (+0)

Sequence differences
  event sequences are identical

Evaluator differences
  none
```

Observations: the comparison exited `0`; two consecutive runs rendered
byte-identical output (deterministic); `evaluate` on each trace reports the same
allow/ok/execute counts. The two runs differ only in the *content* the comparison
does not read.

## 5. What the comparison does and does not establish

**Does establish** (factually, from structure alone): the two traces have the same
number of events, the same typed distribution, the same ordered event-type
sequence (by position), and no evaluator-level differences (same decisions,
results, tool calls, flags, warnings, status).

**Does not establish**: that the two runs are behaviourally or security-wise the
same. LAB-02's injected instruction and the agent's divergent output are content,
not structure, and `compare` never diffs content. "No structural difference" is
therefore **not** "no security difference." The output also states its own limit —
events are *aligned by position only*; no semantic alignment or causal mapping is
attempted.

## 6. Files changed

```text
Added:
  research/76-cross-lab-compare-exercise.md   (this record)

Modified:
  labs/GETTING-STARTED.md                     (new §7, "Try a cross-lab
                                               comparison"; §8 renumbered)
  tests/test_getting_started.py               (+3 documentation guards)
  README.md                                   (derived test-count row 1150 -> 1153)
```

No `src/agentsec/**` (including `compare.py`), `TraceEvaluator`, policy, config,
schema, lab runtime, licensing, workflow or version change.

## 7. Tests added/changed and test-count delta

Only the documentation-artefact guard was extended (`tests/test_getting_started.py`
is already the home of the getting-started guards — one focused guard per
artefact, no new module):

* `test_getting_started_documents_both_cross_lab_commands` — the two LAB-01/LAB-02
  run commands stay documented.
* `test_getting_started_links_both_cross_lab_pages` — the step links both lab
  pages, and both files exist.
* `test_getting_started_keeps_the_cross_lab_section_heading` — the numbered step
  stays present.

No compare-behaviour test was added: `tests/cli/test_compare.py` already exercises
real-lab comparison and the exercise introduces no new runtime invariant, so
duplicating it would only inflate coverage. **Test count: 1150 → 1153 (+3).** The
README's derived test-count row was updated to `1153` via the existing
`tests/test_readme.py` mechanism; no second hard-coded count was introduced.

## 8. Validation results

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1153 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 243 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| The exercise | run LAB-01, LAB-02, then `compare` | exit `0`; deterministic; output as §4 |

## 9. Protected invariants

Untouched: `src/agentsec/compare.py`, `TraceEvaluator`, `read_events` semantics,
the policy files, `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`,
`.freebuff/project-id`, `schemas/**`, the release manifest, the version
declarations (`0.1.0`), the lab runtime semantics, and both
`.github/workflows/*.yml`. The gate stays **READY WITH WARNINGS** with
`blockers: []`.

## 10. Artifact cleanup

Removed the `site/` directory written by `mkdocs build --strict` and all
`__pycache__` directories, plus `.mypy_cache`, `.ruff_cache`, `.pytest_cache`,
`build`, `dist`, `htmlcov` and `.mkdocs-build`. The `runs/` traces are git-ignored
and were left as the labs' normal output. Licensing was re-confirmed after
cleanup; no generated artifacts or scratch directories remain.

## 11. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` — unchanged.
* `v0.0.1` and `v0.1.0` are **unchanged**; `git rev-parse v0.1.0^{commit}` is
  `3d731b0dffece499cc54a22d51701cdeecdce39f`.
* No tag was created, modified, deleted or moved.

## 12. Confirmation

No commit was made, no push was performed, no tag was created/moved/deleted, and
no publication or release action occurred. The change remains in the working tree
alongside the earlier uncommitted Phase 6A–7J work.
