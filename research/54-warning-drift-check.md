# PHASE 21 — WARNING DRIFT CHECK

*Read-only consistency check added after the retirement-procedure documentation
(`research/53`). It compares the accepted-warning policy, the documented set and
the release gate's actual warnings, and reports any disagreement. It changes **no
release logic**, retires **no warning**, and does not touch
`scripts/release_check.py`. Nothing was committed, pushed or tagged; the `v0.0.1`
tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline sets

Entering this step the release state was, and remains:

- **Policy** (`ACCEPTED_RELEASE_WARNINGS` in `tests/test_release_check.py`):
  `{W7, W12}`.
- **Documented** (`labs/ACCEPTED-RELEASE-WARNINGS.md`): `{W7, W12}`.
- **Actual gate** (`scripts/release_check.py --json` → `warnings`):
  `["W12", "W7"]` → `{W7, W12}`.

`W6` is **CLOSED**; the gate is **READY WITH WARNINGS** with `blockers: []`. The
baseline suite was **887 passed** (after `research/53`).

## 2. Design decision

The three surfaces are not copies of one another, so "they agree" is worth
checking rather than assuming — but the check must **not** become a second
hard-coded warning set. Design choices:

- **Reusable script under `scripts/`**, matching the repository's existing
  standalone guards (`check_version.py`, `check_licensing.py`,
  `release_check.py`): stdlib-only, `--root`, human-readable report, exit `0`/`1`.
- **No hard-coded IDs.** The policy is parsed structurally from the test module
  (via `ast`, unwrapping `frozenset({...})`); the documented set is read from the
  canonical `{...}` statement on the page; the actual set comes from the gate.
- **Actual set is structural, not textual.** The check runs
  `python scripts/release_check.py --root <root> --json` and reads the JSON
  `warnings` list. It never parses human-readable console output.
- **Read-only and side-effect free.** No file writes, no state-changing Git, no
  warning suppression, no classification changes.
- **Complement, not replacement.** The exact-set regression test in
  `tests/test_release_check.py` remains the CI protection; this script adds the
  on-demand three-way view.
- **No CI job.** The repository's structure does not require one, so the check is
  a standalone command that release validation can adopt later.

## 3. Implementation

`scripts/check_warning_drift.py`:

- `load_policy(root)` — AST-parses `tests/test_release_check.py`, finds the
  `ACCEPTED_RELEASE_WARNINGS` assignment, and collects its string literals
  (accepting a bare set literal or a `frozenset({...})`/`set({...})` wrapper).
- `load_documented(root)` — reads `labs/ACCEPTED-RELEASE-WARNINGS.md` and parses
  the `{...}` block on the line containing `The accepted set is exactly`.
- `load_actual(root, python)` — runs the release gate with `--json` and reads the
  structured `warnings` list.
- `compare(sources)` — returns a `DriftReport` collecting every problem:
  policy-but-not-documented, documented-but-not-policy, gate-but-not-policy
  (unexpected), policy-but-not-gate (disappeared), documentation/gate
  disagreement, per-source problems (missing file, malformed ID, non-JSON).
- Identifier validation rejects anything not matching `^W\d+$`.
- `format_report(report)` / `main()` — print the three sets and the drift, and
  exit `0` only when all three are exactly equal.

## 4. Test cases

`tests/test_warning_drift.py` — **23 focused tests**:

- script discipline: stdlib-only imports; no write/network calls in source;
- surface readers: policy (present, missing, non-set), documentation (present,
  malformed ID, missing statement), actual gate (JSON list, non-JSON output);
- comparison: all three agree; policy/documentation mismatch; documentation/policy
  mismatch; unexpected new warning; disappeared accepted warning;
  documentation/gate disagreement; source problem surfaced; malformed ID
  surfaced;
- report/CLI: `format_report` shows all three sets and flags drift;
  `main` exits `0` on agreement and `1` on drift (end-to-end against a stubbed
  release check in `tmp_path`);
- real repository: the readable policy and documented surfaces both equal
  `{W7, W12}` (the actual set is pinned by the B5 exact-set test).

The end-to-end tests stub `scripts/release_check.py` with a tiny JSON printer, so
no test runs the real (slow, gate-running) release check and the suite stays
hermetic. No existing test was modified; `tests/test_accepted_release_warnings.py`
gained **one** guard that the page documents the drift check.

## 5. Exact command and expected result

```
python scripts/check_warning_drift.py
```

Expected (and observed):

```
accepted-warning drift check
============================

  policy         {W12, W7}
  documentation  {W12, W7}
  actual gate    {W12, W7}

Result: all three sets agree: {W12, W7}
```

Exit code `0`.

## 6. Files changed

Added:

```
scripts/check_warning_drift.py           (new read-only check, MIT)
tests/test_warning_drift.py              (new focused guard, MIT)
research/54-warning-drift-check.md       (this record, CC BY 4.0)
```

Modified:

```
labs/ACCEPTED-RELEASE-WARNINGS.md        + "Executable drift check" section
tests/test_accepted_release_warnings.py  + 1 guard for the drift-check section
```

No MkDocs navigation change was needed: the drift-check section lives on the
already-listed page, and a script is not a site page. `licensing/manifest.toml`
needed no edit: existing globs cover the new files (`scripts/**` → MIT,
`tests/**` → MIT, `research/**.md` → CC BY 4.0).

## 7. Deliberately left untouched

- `scripts/release_check.py` — **no change** (W12 retained; detection unchanged;
  no warning suppressed); the drift check *runs* it read-only.
- `tests/test_release_check.py` — the B5 policy constant and the exact-set
  assertion — **no change** (the new check complements it, never replaces it).
- `.freebuff/project-id` tracking, `.gitignore`, `licensing/manifest.toml` — no
  change (W7 kept).
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml` — no change; no new CI
  job.
- Runtime source, `schemas/**`, `labs/LAB-00`…`LAB-07` definitions, packaging
  configuration — no change. Version remains `0.1.0`. No `LAB-08`, no C4, no
  coverage floor, no formatting/import-sorting gate.
- `research/1`–`research/53` — not modified.

## 8. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **912 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 204 files accounted for (mit 134, cc-by 68, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `git diff --check` | clean |

**Test delta: 887 → 912 (+25).** The new module contributes its 23 tests plus one
`tests/test_architecture.py` parametrization entry (that suite parametrizes over
every `tests/*.py` file), and `tests/test_accepted_release_warnings.py` gained one
guard.

## 9. Final warning set

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**. The drift check reports
all three surfaces equal. No warning was retired, added or suppressed.

## 10. Tag and Git status

* `v0.0.1` — **unchanged**: `git tag` still lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`,
  no `git tag`. The new files are untracked working-tree changes.

## 11. Confirmation

The accepted warning set for v0.1.0 is exactly `{W7, W12}` across policy,
documentation and gate; W6 is closed; the release gate remains **READY WITH
WARNINGS** with `blockers: []` by decision. `scripts/release_check.py` is
untouched. Phase 17 remains **CLOSED** and E1 remains **HOLD**; no novelty,
effectiveness, security, benchmark or publication claim is made.
