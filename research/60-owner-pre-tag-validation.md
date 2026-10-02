# PHASE 21 — OWNER PRE-TAG VALIDATION

*Read-only orchestration following the release-manifest drift check
(`research/59`): one command runs the owner pre-tag checklist as an executable
sequence, capturing the release gate once and reusing its report. It changes **no
runtime, CI, warning-detection, warning-policy, version or release-gate
behaviour**, and it does not add a CI job. Nothing was committed, pushed or
tagged; the `v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release was prepared and green (validated at the end of
`research/59`): version `0.1.0` (3/3); gate **READY WITH WARNINGS**,
`blockers: []`, accepted set exactly `{W7, W12}`, `W6` closed; warning-drift exit
`0`; manifest-drift exit `0`; CI with exactly five jobs running
`release_check.py` once and feeding its captured report to the drift checker;
suite **991 passed**. The owner pre-tag checklist and the release manifest were
prose-only: correct, but requiring the owner to run roughly a dozen commands by
hand and read each result.

## 2. Objective

Turn the documented owner pre-tag checklist into **one executable, read-only
command** that runs the established checks in a sensible order, captures the
release gate once, reuses its JSON report in both drift checks, verifies the
read-only Git/tag invariant, reports **all** failures, and exits non-zero unless
every required check succeeds — without modifying release policy, release-gate
semantics, CI structure, versioning or Git state.

## 3. Existing checks reused

The command orchestrates, and does not re-implement, the checks the owner already
runs:

- `scripts/check_version.py` (version consistency, `--root`);
- `scripts/check_licensing.py` (licence declarations + coverage, `--root`);
- `python -m pytest` (the complete suite);
- `python -m agentsec labs check` (the offline lab self-check);
- `ruff check src tests scripts`;
- `python -m mypy` (the interpreter-local mypy, which sees the project's stubs);
- `python -m mkdocs build --strict`;
- `scripts/release_check.py --json` (the release gate, run once);
- `scripts/check_warning_drift.py --gate-report`;
- `scripts/check_release_manifest.py --gate-report`;
- a read-only `git tag` for the tag invariant.

No check was altered, and `scripts/release_check.py` was not modified.

## 4. Orchestration design

`scripts/pre_tag_check.py` (standard library only, read-only, deterministic)
defines eleven ordered step functions and a final result banner (step 12),
reported as `[1/12]` … with a `PASS`/`FAIL` line per check. Each step returns a
`StepResult(name, ok, lines)`; `run_checks(ctx)` runs every step **without
stopping at the first failure**, so all independent failures are reported, not
just the first. The overall status is `all(result.ok)`; the command exits `0`
only then.

The injectable-runner convention follows `release_check.py`:
`main(argv, *, run=run_command)`, so tests inject a recording runner and never
execute the real (slow) suite or gate. `run_command` preserves each subprocess's
exit code, stdout and stderr; failing steps quote a bounded tail of the captured
output. A `--summary` flag prints only failing steps and the final banner; it adds
no other option and never exposes temporary-file details.

The sectioned output uses the fixed title `AgentSec v0.1.0 PRE-TAG VALIDATION` and
ends with `RESULT: READY FOR OWNER REVIEW` or `RESULT: NOT READY`, followed by
`No commit, push, tag, or publication was performed.` The warning set is rendered
numerically sorted, so the expected `{W7, W12}` appears as documented.

## 5. Gate-report reuse

`release_check.py --json` runs exactly **once**. Its stdout is parsed and written
to `release-report.json` inside a `tempfile.mkdtemp` scratch directory **outside
the repository**; both `check_warning_drift.py` and
`check_release_manifest.py` are then invoked with `--gate-report <that path>`, so
neither runs the gate again. The scratch directory (which also holds the MkDocs
site build) is removed in a `finally` block. This is the same single-execution
design CI uses, so the orchestrator and CI consume the gate identically.

## 6. Git/tag checks

The only Git access is a read-only `git -C <root> tag`. The command verifies that
`v0.0.1` exists and `v0.1.0` does not. It does **not** inspect or require a clean
working tree — the tree is intentionally dirty while the release awaits owner
review — and it never runs `git status`, commits, pushes, creates or moves a tag.
A failure of the tag invariant is reported like any other step failure.

## 7. Test strategy

`tests/test_pre_tag_check.py` — **31 focused tests** against a fixture repository
whose subprocess commands are stubbed by an injected recording runner:

- **successful orchestration** — exit `0`, the expected warning state accepted,
  `v0.0.1` present and `v0.1.0` absent, and a dirty tree accepted (the
  orchestrator never runs `git status`);
- **failure propagation** — each of version, licensing, tests, labs, Ruff, mypy,
  MkDocs, the release gate and both drift checks fails independently and is
  reported at its own section; a missing `v0.0.1`, an unexpected `v0.1.0`, a gate
  blocker, and multiple simultaneous failures (all listed together);
- **gate reuse** — exactly one `release_check.py` invocation, one `--json` call,
  both drift checks receiving the *same* `--gate-report` path, the report living
  outside the repository, and the report removed afterwards;
- **read-only behaviour** — no commit/push/tag creation, the repository file set
  unchanged, and no `build`/`dist`/`site`/`.coverage`/`.mypy_cache` left behind;
- **output** — every `[n/12]` section present, failures clearly reported, the
  final status unambiguous, and `--summary` hiding passing steps while still
  reporting failures.

No test runs the real suite or the real gate; the interpreter used is
`sys.executable`.

## 8. Exact files changed

Added:

```
scripts/pre_tag_check.py                      (new read-only orchestrator, MIT)
tests/test_pre_tag_check.py                   (new focused guard, MIT)
research/60-owner-pre-tag-validation.md       (this record, CC BY 4.0)
```

Modified:

```
labs/ACCEPTED-RELEASE-WARNINGS.md             + "Executable Owner Pre-Tag Validation"
labs/V0.1.0-RELEASE-MANIFEST.md               + concise reference (no procedure copy)
tests/test_release_manifest.py                + 1 guard for that reference
```

No other file was changed. `licensing/manifest.toml` needed no edit (existing
globs cover the new files, so coverage simply grew by two files). No `mkdocs.yml`
change (the sections live on already-listed pages). **No CI change.**

## 9. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **1024 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 (built outside the repository) |
| `python scripts/check_licensing.py` | **9/9** — 217 files accounted for (mit 140, cc-by 75, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_release_manifest.py` | exit **0** — manifest and repository state agree |
| `python scripts/pre_tag_check.py` | exit **0** — `RESULT: READY FOR OWNER REVIEW` (12/12) |
| `git diff --check` | clean |

**Test delta: 991 → 1024 (+33).** Thirty-one tests in the new module, one
documentation guard in `tests/test_release_manifest.py`, and one
`tests/test_architecture.py` parametrization entry (new `tests/*.py` module). No
existing test was modified or weakened.

## 10. Warning state

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**; version **`0.1.0`**. The
orchestrator treats `READY WITH WARNINGS` as a success and never forces `READY`.

## 11. Protected invariants

`scripts/release_check.py` (and its warning detection), the B5 exact-warning
assertion (`ACCEPTED_RELEASE_WARNINGS`), `.freebuff/project-id`,
`licensing/manifest.toml`, `schemas/**`, the lab runtime,
`.github/workflows/docs.yml` and the warning classification logic were **not
modified**. CI keeps its five-job structure and its single `release_check.py`
invocation; no `continue-on-error` was added. No generated artifacts remain.

## 12. Tag / Git status

* `v0.0.1` — unchanged; `git tag` lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* No commit, push or tag was performed.

## 13. CI decision and remaining owner action

**No CI step was added.** The existing CI already validates the release gate, the
warning drift, the five-job structure and the single release-gate invocation. The
new command is explicitly an **owner pre-tag convenience/orchestration tool** — it
re-runs the full suite and the individual quality gates locally, which would
duplicate the `lint`, `typecheck`, `coverage` and `release-readiness` jobs if
wired into CI, and it exists precisely because the owner runs it by hand. Adding
a sixth job or a second gate invocation was therefore out of scope and is
deliberately avoided.

The remaining action is the **owner's**: review the working tree and the
`v0.1.0 RELEASE REVIEW` evidence, then commit, push, tag and (optionally) publish
manually. The agent does not commit, push, tag or publish. A successful
`pre_tag_check.py` run means the repository is ready for owner review; it does
not authorize or perform the release. Phase 17 remains **CLOSED**, E1 remains
**HOLD**, and no novelty, effectiveness, security, benchmark or publication claim
is made.
