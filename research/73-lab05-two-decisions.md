# PHASE 34 — SAME LAB, TWO DECISIONS (LAB-05)

*A documentation/config/test-only extension: run the **same** LAB-05 experiment
under two policies and read the factual difference between the two traces — a
request that is **held for approval** versus the same request **denied**. It adds
no runtime semantics, no metric, no score, no new approval mechanism and no
claim. Nothing was committed, pushed or tagged.*

## 1. Motivation

LAB-05 teaches the third policy decision, `require_approval`: a legitimate request
that is neither allowed nor denied but *held pending*. Its own page contrasts this
with LAB-04's `deny`, but only in prose. The question a student should be able to
answer from evidence is: *what does the trace actually show for a request that is
held versus one that is refused?* This phase answers that by running **the same
LAB-05 experiment** — same task, same mock fixture, same agent, same requested
operation — under two policies and comparing the traces with the existing
`agentsec compare` command.

This is an **educational contrast between two policy outcomes for one request. It
does not introduce, extend or simulate a new approval mechanism.** The approval
boundary is the existing `require_approval` decision, unchanged.

## 2. Reconnaissance basis

Read-only inspection before editing confirmed each assumption:

* **LAB-05 already yields the approval path.**
  `labs/LAB-05-require-approval/config.yaml` runs a benign task through the
  `approval_read` fixture; the least-privilege policy's `db-read-requires-approval`
  rule answers `require_approval` for the `mock_db` read. Observed:
  `require_approval=1`, `pending_approval=1`, `tool_executions=0`.
* **`deny_by_default.yaml` already yields the denial path** for the same request.
  `policies/examples/deny_by_default.yaml` is `default: deny` with no rules, so
  the identical `mock_db` read is answered `deny`, producing a `denied` result —
  still with `tool_executions=0`.
* **The comparison machinery needs no change.** `agentsec compare` (Phase 7B)
  already reports evaluator differences for `decisions` and `tool_results`.
* **The fixture's final prose is identical in both runs.** `approval_read_script`
  step 2 matches *any* failed tool result (approval-required **or** denied), so
  both runs end with the same sentence. The contrast therefore lives **only** in
  the `policy_decision` and the `tool_result` category — a documented teaching
  caveat, not a defect.

Decision: **GO.** No runtime change is required; the change is documentation,
one example config and tests.

## 3. Files changed

```text
Added:
  configs/examples/lab05_require_approval_deny_by_default.yaml   (example config)
  research/73-lab05-two-decisions.md                             (this record)

Modified:
  labs/LAB-05-require-approval/README.md   ("Same lab, two decisions" section)
  labs/GETTING-STARTED.md                  (§6 approval-vs-deny; §7 renumbered)
  tests/test_getting_started.py            (+3 documentation guards)
  tests/labs/test_lab05.py                 (+2: config + behaviour)
  tests/cli/test_compare.py                (+1: same-lab comparison)
  README.md                                (test count 1138 -> 1144)
```

No `src/agentsec/**`, policy, schema, licensing, workflow, release-manifest or
version change. The existing `labs/LAB-05-require-approval/config.yaml` and
`scenario.yaml` are untouched.

## 4. Why no runtime changes were necessary

Every ingredient already existed and is reused verbatim:

* the **policy engine** and its three decisions (`allow`/`deny`/`require_approval`);
* the shared **example policies** (`least_privilege_v1.yaml`, `deny_by_default.yaml`);
* the **mock fixture** (`approval_read`) and the `mock_db` tool;
* the **`run`** command and the read-only **`compare`** command.

The only new artifact is a second *config* that points the same experiment at a
different policy — exactly the pattern LAB-04 already uses in
`configs/examples/lab04_tool_misuse_allow_all.yaml`.

## 5. Configuration contrast

`configs/examples/lab05_require_approval_deny_by_default.yaml` carries the **same**
`experiment_id` (`lab05_require_approval`), task, `mock_script` (`approval_read`)
and agent block as the lab. Only two fields differ:

| Field | LAB-05 (`labs/LAB-05-require-approval/config.yaml`) | Deny example |
| --- | --- | --- |
| `policy_path` | `policies/examples/least_privilege_v1.yaml` | `policies/examples/deny_by_default.yaml` |
| `trace_path` | *(unset — default `runs/lab05_require_approval/trace.jsonl`)* | `runs/lab05_require_approval_deny_by_default/trace.jsonl` |

A test (`test_lab05_deny_example_config_is_the_same_experiment`) asserts this
equality and the two differences.

## 6. Observed trace behaviour

Both runs completed with the same structure (11 events each); neither executed the
tool.

| Observation | LAB-05 (approval) | Deny example |
| --- | --- | --- |
| `policy_decision.decision` | `require_approval` | `deny` |
| `policy_decision.matched_rule` | `db-read-requires-approval` | `null` |
| `tool_result.error` | `approval required: …` | `denied: …` |
| `tool_result.ok` | `false` | `false` |
| `tool_executed` events | `0` | `0` |
| final `agent_output.answer_redacted` | *(identical)* | *(identical; same `output_hash`)* |

The final answer is byte-identical because the fixture reacts to any failed
result — the documented caveat.

## 7. Comparison output

```bash
python -m agentsec run labs/LAB-05-require-approval/config.yaml
python -m agentsec run configs/examples/lab05_require_approval_deny_by_default.yaml
python -m agentsec compare \
  runs/lab05_require_approval/trace.jsonl \
  runs/lab05_require_approval_deny_by_default/trace.jsonl
```

```text
Event counts
  A: 11
  B: 11
  delta: +0

Event-type distribution
  (identical for every type; no tool_executed in either)

Sequence differences
  event sequences are identical

Evaluator differences
  decisions.deny:                0 -> 1
  decisions.require_approval:    1 -> 0
  tool_results.denied:           0 -> 1
  tool_results.pending_approval: 1 -> 0
```

The request is identical and the traces are structurally identical; **only the
policy outcome differs.** `compare` produces no score and states no
preference.

## 8. Educational purpose

It makes one idea visible in one trace pair: the **policy decision** chooses
between two *different* answers to the same request — "not without a yes"
(`require_approval`, a pending result) and "no" (`deny`, a denied result) — even
though neither executes the tool. It also trains the discipline of reading the
**trace evidence** (`policy_decision`, `tool_result`) rather than the agent's
final prose, which is identical in both runs.

## 9. Tests

* **Config** — `tests/labs/test_lab05.py::test_lab05_deny_example_config_is_the_same_experiment`:
  same `experiment_id`, task, `mock_script` and agent; only `policy_path` and
  `trace_path` differ.
* **Behaviour/integration** — `tests/labs/test_lab05.py::test_lab05_deny_example_is_denied_without_executing`:
  the deny config records a `deny` decision (no matched rule), no
  `tool_executed`, and a `denied` result; the shipped LAB-05 config still records
  `require_approval`, a pending result and no execution.
* **Comparison** — `tests/cli/test_compare.py::test_compare_lab05_two_decisions_surfaces_the_approval_boundary`:
  both traces through `compare`, asserting the positional sequence is identical,
  no `tool_executed` in either, and the four evaluator differences above; the
  comparison is deterministic and neither trace is modified.
* **Documentation guards** — `tests/test_getting_started.py` gained the three
  LAB-05 checks (commands, link + resolved anchor, section heading) alongside the
  existing LAB-04 demo guards. No existing test was weakened.

## 10. Validation

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1144 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **rc 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 239 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| The comparison | `agentsec compare` on the two LAB-05 traces | exit `0`; differences as in §7 |

**Test count: 1138 → 1144 (+6).** The README's derived test-count row was updated
(`1138` → `1144`) as required by the `tests/test_readme.py` guard; no second
hard-coded count was introduced.

## 11. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`
(covered by existing globs), `.freebuff/project-id`, `schemas/**`,
`compare_traces`/`TraceEvaluator`, the demo implementation, the release manifest,
the version declarations (`0.1.0`), the LAB-05 runtime semantics, and both
`.github/workflows/*.yml`. The gate stays **READY WITH WARNINGS** with
`blockers: []`.

## 12. Git / tag state

* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` tag object `13464ba` →
  commit `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
