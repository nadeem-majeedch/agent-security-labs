# PHASE 21 — WARNING DRIFT SINGLE GATE RUN

*Optimization following the drift integration (`research/55`): the
`release-readiness` CI job ran the release gate twice — once directly and once
inside the drift checker. This step makes the gate run **once** by capturing its
JSON report to a temporary file and having the drift checker consume it. It
changes no release-logic semantics. Nothing was committed, pushed or tagged; the
`v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline behaviour

After `research/55` the `release-readiness` job ran:

```
python scripts/check_licensing.py
python scripts/check_version.py
python -m pip install -e ".[dev,docs]"
python scripts/release_check.py --json        # all gates, incl. pytest/mkdocs
python scripts/check_warning_drift.py         # runs release_check.py again
```

`check_warning_drift.py` obtained the actual warning set by invoking
`release_check.py --json` internally, so the aggregate gate — tests, labs,
mkdocs, licensing, version, readme, self-containment, hygiene, git state —
executed **twice** per CI run. Version `0.1.0`; gate `READY WITH WARNINGS`;
`blockers: []`; warnings `{W7, W12}`; `W6` closed; suite 928 passed; five CI
jobs.

## 2. Reason for the optimization

Running the whole gate twice is wasteful (the test suite alone is the bulk of CI
time) and gives no extra assurance: both runs read the same tree and must produce
the same warnings. The goal is to run the gate once and feed its structured
result to the drift checker, without weakening the three-surface protection and
without modifying `scripts/release_check.py`.

## 3. Design

- **`scripts/check_warning_drift.py` gains an explicit read-only option,
  `--gate-report <path>`.** Without it, the checker behaves exactly as before
  (it runs `release_check.py --json` itself). With it, the checker reads the
  supplied report instead of executing the gate.
- **The report is validated structurally, not textually.** `load_actual_from_report`
  requires a JSON object with a `warnings` list; a missing file, malformed JSON,
  a non-object, or an absent `warnings` list all produce a clear failure. It
  never parses human-readable console output.
- **CI captures the gate output once to a temporary file outside the checkout**
  (`${{ runner.temp }}/release-report.json`), using plain output redirection so
  the gate's own exit status is the step's exit status — no pipe, no fallback, no
  `continue-on-error`.
- **The drift step consumes that file** (`--gate-report <file>`), so the gate
  runs exactly once and the drift check still compares policy, documentation and
  the actual gate.
- **No second warning set is defined.** The checker continues to derive the
  policy from `ACCEPTED_RELEASE_WARNINGS` (via `ast`) and the documentation from
  the canonical page statement.

## 4. Files changed

Modified:

```
scripts/check_warning_drift.py           + load_actual_from_report(); run_checks()
                                         takes gate_report; main() takes
                                         --gate-report; docstring/usage updated
.github/workflows/ci.yml                 gate writes its JSON report once to a
                                         temp file; drift step passes
                                         --gate-report; header comment updated
tests/test_warning_drift.py              + 11 tests for --gate-report
tests/test_drift_release_integration.py  + 5 tests (single run, report reuse,
                                         no re-invocation, no hidden exit status)
labs/ACCEPTED-RELEASE-WARNINGS.md        "Executable drift check" section now
                                         explains the single-execution flow
```

Added:

```
research/56-warning-drift-single-gate-run.md   (this record, CC BY 4.0)
```

The CI steps are now:

```yaml
      - name: Run every release gate once and report readiness
        run: python scripts/release_check.py --json > "${{ runner.temp }}/release-report.json"

      - name: Check the accepted-warning surfaces for drift
        run: python scripts/check_warning_drift.py --gate-report "${{ runner.temp }}/release-report.json"
```

`licensing/manifest.toml` needed no edit: existing globs cover the new record
(`research/**.md` → CC BY 4.0). No `mkdocs.yml` change.

## 5. Security / read-only considerations

- The checker remains **read-only**: it still only reads files and (in local mode)
  runs a read-only gate; `--gate-report` adds a file *read*, no write.
- The temporary report lives **outside the repository**, so it cannot become a
  tracked artifact.
- The provided path is only read; a report that is missing or malformed fails
  loudly (exit `1`) rather than being treated as "no warnings", so the check can
  never pass by accident.
- The gate step uses `>` redirection, which preserves the gate's exit status; the
  step has no `continue-on-error`, so a failing gate still fails CI. The drift
  command contains no reference to `release_check.py`, so the gate cannot be
  re-invoked from inside it.
- `--gate-report` does not accept a path that would be executed; the argument is
  opened as text and parsed as JSON.

## 6. Test results

Added/updated tests (no existing test removed or weakened):

- `tests/test_warning_drift.py` — `load_actual_from_report` reads a valid report
  and flags a missing file, malformed JSON, a missing `warnings` list, and
  malformed IDs; `run_checks` uses the report without running the gate (the
  fixture tree has no `scripts/release_check.py`); `main` exits `0` when the sets
  agree and `1` for gate drift (a disappeared warning and an unexpected new
  warning), for a policy/documentation mismatch, and for a missing report.
- `tests/test_drift_release_integration.py` — still exactly five CI jobs; the
  `release-readiness` job still runs the existing gates; `release_check.py`
  occurs exactly once in executable `run:` steps; the drift command does **not**
  reference `release_check.py`; the drift step consumes the generated report and
  the report path lives under `runner.temp`; the gate step (and the drift step)
  carry no `continue-on-error` and the gate step uses no pipe; and the real script
  consumes a `--gate-report` end-to-end against a fixture with no release script.

All tests use the interpreter running the suite (`sys.executable`), never a global
Python. Fixture builders are reused from `tests/test_warning_drift.py`.

## 7. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **944 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 207 files accounted for (mit 135, cc-by 70, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_warning_drift.py --gate-report <report>` | exit **0** — all three sets `{W7, W12}` (gate not re-run) |
| CI YAML parse | valid; exactly five jobs |
| `git diff --check` | clean |

**Test delta: 928 → 944 (+16).** Eleven new tests in `tests/test_warning_drift.py`
(the `--gate-report` reading and CLI cases, one of them parametrized) plus five
new tests in `tests/test_drift_release_integration.py`. No new test *module* was
added, so the `tests/test_architecture.py` parametrization count is unchanged, and
no existing test was modified.

## 8. CI invocation count

`scripts/release_check.py` now appears in **exactly one** executable `run:` step
across the workflow (the `release-readiness` gate step). The drift step invokes
only `scripts/check_warning_drift.py --gate-report`, which reads the captured
report instead of running the gate. The gate therefore executes **once** per CI
run.

## 9. Warning set and release-gate result

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**. The drift check reports
all three surfaces equal in both modes.

## 10. Confirmation

- `scripts/release_check.py` is **byte-for-byte unchanged** (verified with
  `git diff --quiet`); its semantics, output contract and exit code are untouched.
- `tests/test_release_check.py`'s B5 policy constant and exact-set assertion are
  unchanged.
- `.freebuff/project-id`, `.gitignore`, `licensing/manifest.toml` and
  `.github/workflows/docs.yml` are unchanged. `.github/workflows/ci.yml` keeps its
  five-job structure and gains no `continue-on-error`; only the two
  `release-readiness` steps and the header comment changed.
- Version remains `0.1.0`. No `build/`, `dist/`, `.coverage`, `site/` or temporary
  report remains in the repository.
- Phase 17 remains **CLOSED** and E1 remains **HOLD**; no novelty, effectiveness,
  security, benchmark or publication claim is made.

## 11. Tag and Git status

* `v0.0.1` — **unchanged**: `git tag` still lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`,
  no `git tag`; no version bump.

## 12. Limitations and deferred work

- The local developer default still runs the full gate inside the checker; only
  the CI path uses `--gate-report`. A developer who has just run
  `release_check.py --json` can pass that file to avoid a second local run.
- The report is passed by path within a single job; no artifact upload/download
  is used (the job keeps everything in one runner). Multi-job reuse would be a
  larger change and is not needed here.
