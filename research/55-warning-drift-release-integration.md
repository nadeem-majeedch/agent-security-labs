# PHASE 21 — WARNING DRIFT RELEASE INTEGRATION

*Integration step following the drift check (`research/54`): the existing
read-only checker is now part of the release-validation flow. It adds **one CI
step**, **one documentation paragraph** and **one focused test module**; it
changes no release-logic semantics. Nothing was committed, pushed or tagged; the
`v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release state was, and remains:

- Version `0.1.0` (3/3 declarations); package version unchanged.
- Gate **READY WITH WARNINGS**, `blockers: []`, warnings `["W12","W7"]` →
  `{W7, W12}`; `W6` closed.
- `scripts/check_warning_drift.py` exists, is read-only and stdlib-only, and
  exits `0` (all three surfaces `{W7, W12}`).
- Suite **912 passed** (after `research/54`); labs 8/8.
- CI has **five** jobs: `lint`, `compatibility`, `typecheck`, `coverage`,
  `release-readiness`. The `release-readiness` job runs, in order:
  `check_licensing.py`, `check_version.py`, install `.[dev,docs]`,
  `release_check.py --json`.

## 2. Rationale for the integration point

The constraint is that `scripts/release_check.py`'s **semantics must not
change**, so the drift check cannot become a new gate *inside* the runner. The
smallest clean integration is therefore a **distinct step in the existing
`release-readiness` CI job**, placed after `release_check.py --json`, with no new
job and no change to any existing gate. This preserves the five-job structure,
the Python versions, the compatibility matrix, every existing release check and
the existing `release_check.py` invocation.

The drift checker remains the single executable drift checker; nothing about it
was re-implemented in the workflow or in `release_check.py`.

## 3. Files changed

Modified:

```
.github/workflows/ci.yml                 + 1 step in `release-readiness`
                                         + header comment for that step
labs/ACCEPTED-RELEASE-WARNINGS.md        "Executable drift check" section now
                                         states the check is part of release
                                         validation
```

Added:

```
tests/test_drift_release_integration.py  new focused integration guard (MIT)
research/55-warning-drift-release-integration.md   (this record, CC BY 4.0)
```

The added CI step is:

```yaml
      - name: Check the accepted-warning surfaces for drift
        run: python scripts/check_warning_drift.py
```

`licensing/manifest.toml` needed no edit: existing globs cover the new files
(`tests/**` → MIT, `research/**.md` → CC BY 4.0), and `ci.yml` is already
covered (`.github/**` → MIT). `mkdocs.yml` needed no change — no new page.

## 4. Behavior before / after

Before: the drift check existed and could be run by hand, but nothing bound it to
release validation; a release could be tagged while policy, documentation and the
gate disagreed.

After: the `release-readiness` job runs the drift check as its final step. A
non-zero exit fails the job (the step has no `continue-on-error` and no shell
fallback), so **release validation cannot pass while the three surfaces
disagree**. The current state passes:

```
policy = {W7, W12}
documentation = {W7, W12}
actual gate = {W7, W12}
```

The step is read-only (it runs the gate with `--json` and reads files) and
creates no artifact in the checkout.

## 5. Test strategy

`tests/test_drift_release_integration.py` — **15 focused tests** in three groups:

- **CI wiring** — the workflow still has exactly five jobs; the
  `release-readiness` job runs `scripts/check_warning_drift.py`; the drift check
  appears in *no other* job; the job still runs `check_licensing.py`,
  `check_version.py` and `release_check.py --json`; the drift step cannot be
  silently ignored (no `continue-on-error`, no `|| true`/`set +e`-style
  fallback); the drift step follows the release-gate step.
- **Integrated behavior** — the current repository's readable surfaces
  (policy, documentation) both equal `{W7, W12}`; the real drift script run as a
  subprocess exits `0` when a fixture tree agrees, and exits `1` for every drift
  direction (documentation vs policy, gate vs policy — including a disappeared
  accepted warning — an unexpected new warning, and documentation broader than
  policy), for a malformed documented ID, and when the gate output is unusable
  (non-JSON).
- **Read-only** — running the integrated command leaves the fixture tree
  byte-identical (no files written, no artifacts produced).

The fixture builders are **reused** from `tests/test_warning_drift.py` (loaded as
a module, since `tests` is not a package) rather than duplicated. End-to-end cases
stub `scripts/release_check.py` with a tiny JSON printer, so no test runs the real
(slow, gate-running) release check. The interpreter used is `sys.executable` — the
one running the tests — never a global Python installation.

## 6. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **928 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 206 files accounted for (mit 135, cc-by 69, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `git diff --check` | clean |

**Test delta: 912 → 928 (+16).** The new module contributes its 15 tests plus one
`tests/test_architecture.py` parametrization entry (that suite parametrizes over
every `tests/*.py` file). No existing test was modified.

## 7. Warning set and release-gate result

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**. The integrated drift check
reports all three surfaces equal. No warning was retired, added or suppressed.

## 8. Protected invariants

- `scripts/release_check.py` — **no change**; its semantics and output contract
  are exactly as before. The integration is entirely in the workflow.
- `tests/test_release_check.py` — the B5 policy constant and the exact-set
  assertion — **no change** (not weakened).
- `.freebuff/project-id` — unchanged and still tracked (W7 kept).
- `.gitignore`, `licensing/manifest.toml` — no change.
- `.github/workflows/docs.yml` — no change. `.github/workflows/ci.yml` gains one
  step in the existing job; the five-job structure, Python versions, compatibility
  matrix and all existing checks are preserved. No separate job was created.
- Version remains `0.1.0`; no `LAB-08`, no C4, no coverage floor, no
  formatting/import-sorting gate.
- `research/1`–`research/54` — not modified.

## 9. Tag and Git status

* `v0.0.1` — **unchanged**: `git tag` still lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`,
  no `git tag`. The new files are untracked working-tree changes; the generated
  `site/` build output from local validation was removed.

## 10. Limitations and deferred work

- The drift step runs after `release_check.py --json`, and the drift checker
  itself invokes `release_check.py --json` again, so the release gate runs
  **twice** in the `release-readiness` job. This is deliberate: the constraint
  forbids changing `release_check.py`'s semantics (e.g. by folding the drift
  check into it), and the checker is intentionally the single executable drift
  checker. If a future change is permitted, the runner could emit the warning set
  once and the drift check could consume it.
- The integration is a CI step only; it is not yet part of a documented pre-tag
  owner checklist beyond this record.
- Coverage remains report-only; formatting/import-sorting gates remain deferred.

## 11. Confirmation

The accepted warning set for v0.1.0 is exactly `{W7, W12}` across policy,
documentation and gate; `W6` is closed; the release gate remains **READY WITH
WARNINGS** with `blockers: []` by decision, and the drift check is now part of
release validation. Version remains `0.1.0`; no commit, push, tag or version bump
occurred. Phase 17 remains **CLOSED** and E1 remains **HOLD**; no novelty,
effectiveness, security, benchmark or publication claim is made.
