# PHASE 27 — DOCUMENTATION DRIFT FIX

*A small, evidence-driven documentation-consistency correction found by
`research/65`. It fixes two verified drifts — a stale test count in the root
README and an outdated README-maintenance note in `docs/development.md` — and
adds a derived guard so the count cannot silently drift again.*

This is **documentation consistency work, not a release-policy change**. No
warning is retired, no classification changes, and no release control is added or
altered. `scripts/release_check.py`, its warning detection and the accepted set
`{W7, W12}` are untouched.

## 1. Baseline

| Item | Value (verified read-only at the start of this step) |
| --- | --- |
| Branch | `v0.1.0-dev` @ `e831e0c` — *"phas QA complete"* |
| Released tag | `v0.1.0` → commit `3d731b0` (unchanged) |
| Version | `0.1.0` (3/3) |
| Tests | **1081 passed**; labs **8/8**; Ruff clean; mypy 0/40; MkDocs strict pass; licensing 9/9 |
| Gate | **READY WITH WARNINGS**, `blockers: []`, `{W7, W12}` |
| Working tree | untracked `research/65-post-v0.1.0-roadmap.md` (from the prior step) |

## 2. Exact documentation discrepancies

1. **`README.md`** (verification-status table): the test-suite row claimed
   **“880 tests pass”**, while the suite collects and passes **1081**. The README
   tells the reader the table was “re-run locally at this revision”, so a stale
   count is a trust defect, not a cosmetic one.
2. **`docs/development.md`** (“Note on the repository README”): it stated the root
   README “is intentionally left untouched”, which was true historically but
   false after the README was updated for `v0.1.0` (release identity, licence
   boundary, verification table, “what this project does not claim”).

Both were simple accumulated drift; neither was caused by this step.

## 3. Files inspected

`README.md`, `docs/development.md`, `pyproject.toml`, the whole of `tests/`
(including `tests/test_architecture.py` and `tests/test_release_manifest.py` as
the existing documentation/architecture-guard patterns), `scripts/`
(`release_check.py` and the other guards, read-only), and `labs/V0.1.0-RELEASE-MANIFEST.md`.

Findings from inspection:

* The only stale count in the tree is README line 225; no other file repeats it.
* There is **no existing documentation-test module** guarding the root README
  (the existing guards cover the lab pages and the release manifest).
* `tests/test_architecture.py` parametrises over `python_files(TESTS)`, so a new
  test module is picked up automatically — **no manual architecture update is
  required**.
* A derivation mechanism exists: `pytest --collect-only` enumerates the suite
  (without running it) and prints `N tests collected`.

## 4. Chosen correction

* **`README.md`:** the test-suite row now reads
  `| Test suite | \`PYTHONPATH=src py -m pytest\` | **1085 tests pass** (exit 0) |`.
* **`docs/development.md`:** the note now says the root README is a maintained
  front-page summary (verification table, licence boundary, release identity,
  “no claim” section), names the new guard, and points to
  `research/14-implementation-blueprint.md` for the original plan — instead of
  claiming the README is untouched.

The number stated in the README is **the total the suite collects at this
revision**, which is also the number it passes. It is the *only* place the count
is written; there is no second constant.

**Why the number is retained rather than removed.** Two shapes were possible: a
volatile count, or a stable non-numeric phrase (the README already uses one for
the documentation-build row). A count was kept **because the derived guard is
most useful when it pins a fact that actually drifts** — a documented number that
cannot go stale would need no guard at all. Keeping the number and deriving it
gives the strongest protection and matches the repository's existing
drift-guard discipline (schema drift, warning drift, release-manifest drift),
where a surface that must stay in step is checked against its source of truth.
The failure message tells the maintainer the exact value to set.

## 5. Derived guard design (`tests/test_readme.py`)

The guard mirrors the existing documentation-consistency style (text assertions
on a page) but derives the value instead of hard-coding it.

* **Derivation.** `_collected_test_count()` runs
  `sys.executable -m pytest --collect-only -o addopts= -p no:cacheprovider`
  with `cwd = ROOT` and parses the summary line `N tests collected` with a
  tolerant regex (`(\d+)\s+tests?\s+collected`). The repository's own pytest
  configuration supplies `testpaths`/`pythonpath`; `-o addopts=` neutralises the
  configured quiet flag so the summary is always printed.
* **No recursive run.** `--collect-only` *enumerates* the suite; it never
  executes it, so this guard does not run the suite from inside a test. Running
  it at **function** scope (not import time) avoids the obvious recursion — a
  module-level collection would re-import the guard during the child collection.
* **No second constant, no `assert 1081`.** The README is parsed with
  `README_TEST_ROW` and its number is asserted equal to the derived count; there
  is no duplicated expected value anywhere.
* **Deterministic and fast.** One child-process collection (~0.5 s), no network
  (the module passes the repository's `test_tests_do_not_reference_the_network`
  scan), no clock, no randomness.
* **Tests provided.**
  1. `test_readme_states_the_current_collected_test_count` — README count ==
     derived count, with a message naming the correct value.
  2. `test_readme_row_reports_a_passing_suite` — the row still claims the passing
     exit status.
  3. `test_development_note_describes_the_maintained_readme` — the stale
     “intentionally left untouched” phrasing is gone and the note names
     `tests/test_readme.py`.

**Reasoning for a new module.** The task prefers extending an existing
documentation-test module; inspection found none that covers the root README
(the existing guards target the lab pages and the release manifest), so a focused
new module is the appropriate home. Because `tests/test_architecture.py`
auto-parametrises over `tests/*.py`, adding it required **no** architecture
update.

## 6. Test delta

**+4 collected tests** (1081 → **1085**):

* `+3` for the three guard functions in `tests/test_readme.py`;
* `+1` because `tests/test_architecture.py::test_no_banned_dependency_in_tests`
  is parametrised over the test modules and gains one case for the new module.

No existing test was weakened or removed.

## 7. Validation results

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1085 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 40 source files** |
| Docs | `python -m mkdocs build --strict` | **rc 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** (223 files: mit 141, cc-by 80, excluded 2, unlicensed 0) |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Whitespace | `git diff --check` | clean (rc 0) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |

## 8. Protected invariants

Confirmed untouched: `scripts/release_check.py` and its warning detection
(`git diff --stat -- scripts/` is empty), the B5 exact-warning set, `W7` and
`W12` (still accepted), the release manifest and `licensing/manifest.toml` (no
edit — the new files are covered by existing globs), the version declarations
(`0.1.0`), `.freebuff/project-id`, `schemas/**`, the lab runtime, and the CI
structure. The classification stays **READY WITH WARNINGS** with `blockers: []`.

## 9. Artifacts removed

All generated artifacts/caches were removed before finishing: `.mypy_cache`,
`.ruff_cache`, `.pytest_cache`, any `site/`/`build/`/`dist/`/`htmlcov/`, and all
`__pycache__` directories. No generated file remains in the tree.

## 10. Git / tag state

* `v0.1.0` → `3d731b0` and `v0.0.1` — **unchanged** (local and remote).
* No tag was created, modified or deleted.
* **No commit, push or publication** was performed.

## 11. Files changed

```text
Modified:
  README.md                          (test-count row: 880 -> 1085)
  docs/development.md                (README-maintenance note corrected)

Added:
  tests/test_readme.py               (derived documentation-consistency guard, MIT)
  research/66-documentation-drift-fix.md   (this record, CC BY 4.0)
```

## 12. Why no release-control changes were necessary

The drifts were documentation statements whose source of truth (the test suite,
the maintenance policy) already existed. Correcting them and *guarding* them
needed no change to the release gate, the warning policy, the accepted set, the
manifest, the version or CI: the new guard is an ordinary offline test, and the
README count is derived, not declared twice. Adding release-control machinery for
a documentation-statement drift would be disproportionate; the correct fix is the
existing pattern — assert the documentation against its source of truth — applied
to the one surface that lacked it.
