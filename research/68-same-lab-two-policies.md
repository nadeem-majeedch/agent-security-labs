# PHASE 29 — SAME LAB UNDER TWO POLICIES

*A small educational extension to the `agentsec compare` capability: run the
**same** LAB-04 experiment under two different policies and read the factual
differences between the two traces. It adds no runtime semantics, no metric, no
score and no claim. Nothing was committed, pushed or tagged.*

## 1. Reconnaissance

Read-only inspection before changing anything:

* **LAB-04** (`labs/LAB-04-tool-misuse/config.yaml`) runs the `tool_misuse`
  deterministic fixture: a benign task makes the mock agent request an
  out-of-scope `fs_sandbox` **write** to `../../etc/passwd`.
* **Policy mechanism** — the repository has one policy engine: a YAML document
  (`default` + ordered `rules`, first match wins, decisions
  `allow`/`deny`/`require_approval`) loaded by `agentsec.policy.load_policy`. An
  experiment selects one with `ExperimentConfig.policy_path`. LAB-04 uses the
  shared `policies/examples/least_privilege_v1.yaml`, which denies the
  out-of-scope write.
* **Example policies** already exist (`deny_by_default.yaml`,
  `least_privilege_v1.yaml`, and the two lab-specific ones). There was **no
  permissive example** to contrast against, but the engine and the config
  `policy_path` field already support one.
* **Trace generation** — `agentsec run <config.yaml>` is the supported lab
  execution mechanism; traces land in `runs/<experiment_id>/trace.jsonl`
  (`runs/` is git-ignored). Tests generate traces into `tmp_path` with a fixed
  clock (`tests/labs/test_lab0*.py`).
* **`agentsec compare`** (Phase 7B) compares two traces read-only: event counts
  and distribution, the ordered event sequence (positional alignment only) and
  the evaluator differences — decisions, tool results, tool calls, flags,
  warnings. No score.
* **Boundary semantics** (from `docs/development.md`): tools enforce
  *containment* (a request cannot leave the sandbox); the policy engine enforces
  *authorization*. They are deliberately separate, so an *allowed* request can
  still be *refused by the tool itself*.

## 2. Selected lab

**LAB-04 (Tool Misuse)** — the natural fit: its whole point is a *request* and the
policy decision that follows it, with the same deterministic input, so changing
only the policy isolates exactly what the policy contributes to the trace.

## 3. Policy A and policy B

* **Policy A — permissive (new):** `policies/examples/allow_all_v1.yaml`
  (`default: allow`, no rules). Added as the symmetric teaching extreme of
  `deny_by_default.yaml`.
* **Policy B — least privilege (existing):**
  `policies/examples/least_privilege_v1.yaml`, the policy LAB-04 already uses.

A ready-made config runs the same LAB-04 experiment under policy A:
`configs/examples/lab04_tool_misuse_allow_all.yaml`.

## 4. Why only the policy differs

The permissive example config carries the **same** `experiment_id`
(`lab04_tool_misuse`), the **same** task, the **same** `mock_script`
(`tool_misuse`) and the **same** agent (`agent_id`, `run_id`, `scenario`,
`max_steps`). Only two fields differ: `policy_path` (the point of the exercise)
and an explicit output `trace_path` (so the two runs do not overwrite each other;
the lab's own config writes to `runs/lab04_tool_misuse/trace.jsonl`). A test
asserts this equality.

## 5. Trace-generation method

Using the existing supported mechanism, from the repository root:

```bash
# Trace A — same lab, permissive policy
python -m agentsec run configs/examples/lab04_tool_misuse_allow_all.yaml
# Trace B — the lab as shipped, least-privilege policy
python -m agentsec run labs/LAB-04-tool-misuse/config.yaml
```

Generated traces are **not** committed (`runs/` is git-ignored). The tests
reproduce both runs deterministically into `tmp_path` with a fixed clock and
never touch `runs/`.

## 6. Comparison output

```bash
python -m agentsec compare \
  runs/lab04_tool_misuse_allow_all/trace.jsonl \
  runs/lab04_tool_misuse/trace.jsonl
```

```text
Trace A
  run_id: lab04-run-1
  scenario: LAB-04-tool-misuse
  events: 12

Trace B
  run_id: lab04-run-1
  scenario: LAB-04-tool-misuse
  events: 11

Event counts
  A: 12
  B: 11
  delta: +1

Event-type distribution
  tool_executed      A 1  B 0  (+1)
  ...

Sequence differences
  index 6: A tool_executed | B tool_result
  ...                       (positional shift from the extra event)
  only in A: index 11: run_completed

Evaluator differences
  decisions.allow: 1 -> 0
  decisions.deny: 0 -> 1
  tool_results.denied: 0 -> 1
  tool_results.error: 1 -> 0
```

What the difference means, descriptively:

* Under **least privilege**, the request is denied at the policy gate, so there
  is **no `tool_executed`** and the result is `denied`.
* Under **allow-all**, the request is allowed, so a `tool_executed` event is
  recorded — and the sandbox tool **still refuses the out-of-scope path**, giving
  an `error` result (containment). One extra event shifts every later position,
  which `compare` reports as positional differences rather than guessing an
  alignment.

The request is identical; **only the policy differs**.

## 7. Educational purpose

It makes two ideas visible in one trace pair:

1. The **policy decision** (authorization) is a distinct stage from **tool
   execution**: same request, different decision, different trace.
2. **Authorization and containment are different boundaries.** An allowed call is
   not a successful call — the sandbox can still refuse it. LAB-04's own safety
   note ("the policy denies the request before the tool is reached") is
   complemented here by the permissive case, where the tool *is* reached and
   refuses the path itself.

It produces **no score and no ranking**; it states what changed and why.

## 8. Tests

Added to `tests/cli/test_compare.py` (**+3** tests; the module is already the home
of the real-lab comparison test, so it was extended rather than duplicated):

1. `test_lab04_two_policy_configs_describe_the_same_experiment` — the permissive
   example and LAB-04 share `experiment_id`, task, `mock_script` and agent, and
   differ only in `policy_path`.
2. `test_example_policies_decide_the_out_of_scope_write_differently` — the
   permissive policy *allows* the `fs_sandbox` write while least privilege
   *denies* it (same engine, same inputs).
3. `test_compare_same_lab_two_policies_surfaces_the_policy_boundary` — runs both
   configs with a fixed clock, and asserts the factual, expected differences
   (A has `tool_executed`; `allow`→`deny`, `error`→`denied`) and that the
   comparison is deterministic and neither trace is modified.

No existing test was weakened.

## 9. Validation

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1106 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 41 source files** |
| Docs | `python -m mkdocs build --strict` | **rc 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| The demonstration | `agentsec compare` on the two LAB-04 traces | exit `0`; differences as in §6 |

A first MkDocs build failed strict mode because the new LAB-04 section linked to
`../../policies/examples/allow_all_v1.yaml`, which is not a documentation file
(`docs_dir: labs`). The link was replaced with inline code; the build then passed
and the gate returned to `READY WITH WARNINGS`.

**Test count: 1103 → 1106 (+3).** No manual architecture update was needed. The
README's derived test-count row was updated (`1103` → `1106`) as required by the
`tests/test_readme.py` guard from Phase 7A.

## 10. Limitations

* The comparison is **structural and factual**. It does not diff payloads, does
  not measure "how different" the traces are, and does not judge either policy as
  better, safer, stronger or weaker.
* Positional alignment is only meaningful when traces are similar; the extra
  `tool_executed` event shifts later positions, which `compare` reports literally.
* The permissive policy is a **teaching extreme** for this demonstration only; it
  is not a recommendation, and the sandbox still enforces containment.
* Only LAB-04 is demonstrated; other labs are unchanged.
* No novelty, effectiveness, security, benchmark or publication claim is made.

## 11. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`
(new files are covered by existing globs), `.freebuff/project-id`, `schemas/**`
(no schema or `security_event` change), the release manifest, the version
declarations (`0.1.0`), `TraceEvaluator` semantics, the lab runtime semantics,
and both `.github/workflows/*.yml` (no CI integration). The gate stays **READY
WITH WARNINGS** with `blockers: []`.

## 12. Git / tag state

* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
