# PHASE 21 — RELEASE MANIFEST DRIFT CHECK

*Read-only validation following the v0.1.0 release manifest (`research/58`): a
script and focused tests verify that the manifest and the actual release state
stay consistent. It changes **no runtime, CI, warning-detection, warning-policy,
version or tooling behaviour**. Nothing was committed, pushed or tagged; the
`v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release was prepared and green: version `0.1.0` (3/3);
gate **READY WITH WARNINGS**, `blockers: []`, accepted set exactly `{W7, W12}`,
`W6` closed; warning-drift check exit `0`; CI with exactly five jobs running
`release_check.py` once and feeding its captured report to the drift checker;
suite **956 passed**. `labs/V0.1.0-RELEASE-MANIFEST.md` (`research/58`) recorded
the release identity, readiness, evidence, warning table, scope, protected
invariants, owner sequence and templates — as prose, which can silently drift.

## 2. Objective

Make the manifest's claims executable-checkable: a small, deterministic,
read-only checker that compares the manifest against the actual repository and
release state, detects drift, reports **every** discrepancy, and exits non-zero
on disagreement — without modifying the manifest, the release gate, the version,
the CI or the Git state.

## 3. Inspected surfaces

`labs/V0.1.0-RELEASE-MANIFEST.md`, `labs/ACCEPTED-RELEASE-WARNINGS.md`,
`scripts/check_warning_drift.py`, `scripts/release_check.py`,
`tests/test_release_manifest.py`, `tests/test_warning_drift.py`,
`tests/test_drift_release_integration.py`, `tests/test_release_check.py`,
`pyproject.toml`, `CITATION.cff`, `mkdocs.yml`, `.github/workflows/ci.yml`. The
existing conventions reused: the `CommandResult` + injectable `run` pattern from
`release_check.py`, the drift-check module loaded via `importlib` (as the tests
already do), `--gate-report` capture-once design, and the `PASS`/`FAIL` report
style.

## 4. Implementation

`scripts/check_release_manifest.py` (standard library only, read-only,
deterministic):

- reads the authoritative version from `pyproject.toml` with `tomllib` (never
  hard-coded);
- obtains the release gate report from `release_check.py --json`, or from a
  supplied `--gate-report` file (validated as a JSON object; malformed or missing
  fails clearly);
- **reuses `check_warning_drift`** (loaded as a module) for the policy,
  canonical-documentation and actual-warning surfaces, and parses the manifest's
  own `{...}` set to compare against the policy — so no second warning-set
  definition is introduced;
- scans `.github/workflows/ci.yml` **without a YAML dependency** (a small text
  scan of the jobs block and `run:` lines), keeping the script stdlib-only;
- reads the tag state with a read-only `git tag`, and the tracked paths with
  read-only `git ls-files` / `git status --porcelain -- scripts/release_check.py`;
- compares the repository and packaged trace-schema copies byte-for-byte;
- runs Ruff and mypy (not part of the release gate) to cover the manifest's
  stated validation evidence;
- evaluates each invariant into a `Check` and reports **all** of them.

CLI:

```
python scripts/check_release_manifest.py
python scripts/check_release_manifest.py --gate-report <report.json>
```

Exits `0` only when manifest and repository agree; prints one `PASS`/`FAIL` line
per invariant and all supporting detail on failure.

## 5. Exact files changed

Added:

```
scripts/check_release_manifest.py               (new read-only checker, MIT)
tests/test_release_manifest_drift.py            (new focused guard, MIT)
research/59-release-manifest-drift-check.md     (this record, CC BY 4.0)
```

Modified:

```
labs/V0.1.0-RELEASE-MANIFEST.md                 + "Executable manifest drift check"
tests/test_release_manifest.py                  + 1 guard for that section
```

No other file was changed. `licensing/manifest.toml` needed no edit (existing
globs cover the new files). No `mkdocs.yml` change (the section lives on the
already-listed page). No CI change.

## 6. Drift conditions checked

- **Release version** — the manifest's stated version equals the authoritative
  `pyproject.toml` version.
- **Warning set** — policy, canonical documentation, actual gate and the
  manifest's own `{...}` set all equal; a warning added or disappeared, or a
  malformed ID in the manifest, fails.
- **Blockers** — the gate reports `[]` and the manifest states it.
- **Classification** — `READY WITH WARNINGS` in the gate and the manifest.
- **W6 closed** — absent from the gate and documented CLOSED.
- **Release validation** — the gate's tests/labs/mkdocs/licensing/version statuses
  are `PASS`, no blockers, and Ruff and mypy succeed.
- **CI structure** — exactly five jobs, `release-readiness` present, one
  release-gate invocation in `run:` steps, a drift step present that uses
  `--gate-report`, and no `continue-on-error`.
- **Tag state** — `v0.0.1` present, `v0.1.0` absent, and documented as such.
- **Protected invariants** — `.freebuff/project-id` tracked, `docs.yml` present,
  schema copies byte-identical, `scripts/release_check.py` unmodified.

## 7. Test strategy

`tests/test_release_manifest_drift.py` — **33 focused tests**: basic agreement
for every invariant; each drift direction independently (manifest version, actual
version, warning added, warning disappeared, non-empty blockers, changed
classification, malformed manifest ID, missing/malformed manifest, a missing
manifest section, wrong job count, missing release job, missing drift step, drift
step without `--gate-report`, a duplicate gate invocation, `continue-on-error`
introduced, an unexpected `v0.1.0` tag, a protected-invariant drift); all
discrepancies reported at once; the workflow scanner (crafted text and the real
`ci.yml`); and the CLI against a fixture repository whose `release_check.py` is
stubbed, including that `--gate-report` never runs the gate again.

The fixture builders are reused from `tests/test_warning_drift.py`; the checks
run against crafted `ReleaseState` objects (no subprocess) except the CLI cases,
which use an injected recording runner. The interpreter used is
`sys.executable`. One documentation guard was added to
`tests/test_release_manifest.py` for the new manifest section.

## 8. CI decision and rationale

**No CI step was added.** The manifest is explicitly **owner-facing, pre-tag
documentation** that records point-in-time evidence (including a test count); it
is not a live contract. Wiring the checker into `release-readiness` would couple
CI to owner documentation, duplicate the Ruff/mypy work already run in their own
jobs, and risk false failures for a document that is meant to be reviewed
manually. The check therefore runs as part of the owner pre-tag review (the
manifest section documents the command), and the checker's `--gate-report` option
means it can consume the CI-captured report when the owner runs it after CI. The
five-job structure, the single `release_check.py` invocation and the
`docs.yml` workflow are all unchanged.

## 9. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **991 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 214 files accounted for (mit 138, cc-by 74, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_release_manifest.py` | exit **0** — manifest and repository state agree |
| `git diff --check` | clean |

**Test delta: 956 → 991 (+35).** Thirty-three tests in the new module, one
documentation guard in `tests/test_release_manifest.py`, and one
`tests/test_architecture.py` parametrization entry (new `tests/*.py` module). No
existing test was modified.

## 10. Warning set and version

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**; version **`0.1.0`**.

## 11. Tag state

* `v0.0.1` — unchanged; `git tag` lists only `v0.0.1`.
* `v0.1.0` — **not created**.

## 12. Protected invariants

`scripts/release_check.py` (and its warning detection), the B5 exact-warning
assertion, `.freebuff/project-id`, `licensing/manifest.toml`, `schemas/**`, the
lab runtime, `.github/workflows/docs.yml` and the warning classification logic
were **not modified**. CI keeps its five-job structure and single gate
invocation. No generated artifacts remain.

## 13. Deferred items

- The checker is not wired into CI (see §8); it is an owner pre-tag check. If a
  future change makes the manifest a live contract, a `release-readiness` step
  could reuse the captured report via `--gate-report`.
- The checker verifies that the recorded **validation succeeds**, not the exact
  numeric test count: the manifest is point-in-time evidence, and pinning the
  count would make it brittle. This is deliberate.

## 14. Confirmation

**Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`, no
`git tag`; no version bump; no release published. Phase 17 remains **CLOSED** and
E1 remains **HOLD**; no novelty, effectiveness, security, benchmark or
publication claim is made.
