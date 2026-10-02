# PHASE 21 — B4/B5 CLOSE-OUT AND PLAN RECONCILIATION

*Close-out record for the B4 quality-gate sequence (`research/42`,
`research/43`, `research/44`) and the B5 warning-set assertion (`research/45`),
reconciled against the v0.1.0 plan of record `research/39`. This step is
**documentation only**: no implementation code, gate, configuration or test was
changed. Nothing was committed, pushed, tagged or version-bumped.*

## 0. Why a new record (not an edit to `research/39`)

`research/39-v0.1.0-development-plan.md` is the plan of record; its §15 states
that historical audits `research/20`–`research/38` are not modified, and it
carries its own status vocabulary. The repository's established convention for
every subsequent step has been to **add a new record** (`research/41`…`research/45`)
rather than rewrite the plan. This close-out therefore follows that convention:
`research/39` is left **byte-unchanged**, and the reconciliation below is the new
record. No status tag inside `research/39` was edited.

## 1. Baseline (verified before this step)

| Item | Value |
| --- | --- |
| Branch | `v0.1.0-dev` |
| HEAD | `fc80f26` — `Simplify CI release validation` |
| Released tag | `v0.0.1` → commit `121acc3` (**untouched**) |
| Working tree | B4.1–B4.3 and B5 changes present, **uncommitted** |
| Tests | **853 passed** |
| Labs | **8/8** |
| Release gate | **READY WITH WARNINGS**, `blockers: []`, warnings `{W6, W7, W12}` |
| CI jobs | `lint`, `compatibility`, `typecheck`, `coverage`, `release-readiness` |
| Compatibility matrix | `["3.11", "3.13"]` |
| Package version | `0.0.1` |
| `src/agentsec/py.typed` | **absent** (D1 not started) |

## 2. Reconciliation — planned item → status → evidence

Scope: the B-items the plan groups under **Phase 2 (CI honesty: B1, B2, B3)**,
**Phase 3 (quality gates: B4, D1)** and **Phase 5 (B5)**, since B4/B5 are the
subject of this close-out. Status uses the plan's own vocabulary.

### 2.1 B4 — lint / type / coverage gates

| Field | Value |
| --- | --- |
| **Planned item** | `research/39` §9 **B4 [PROPOSED]** — "Add lint/format/type gates (e.g. `ruff`, `mypy`) and a coverage floor, with hermetic offline configuration." |
| **Implementation status** | **[PARTIAL]** — lint ✓, type ✓, coverage measured (report-only), **coverage *floor* not added**, **format gate not added** (both deliberate, see §3). |
| **Evidence** | `research/41` (audit) → `research/42` (Ruff 0.12.0, `[tool.ruff.lint]` select `E4,E7,E9,F`, `lint` job) → `research/43` (mypy 1.17.1, `[tool.mypy]`, stub packages, `typecheck` job) → `research/44` (pytest-cov 7.0.0, report-only `coverage` job). |
| **Files changed** | `pyproject.toml` (`[tool.ruff.lint]`, `[tool.mypy]` + override, dev extra: `ruff==0.12.0`, `mypy==1.17.1`, `types-PyYAML`, `types-jsonschema`, `pytest-cov==7.0.0`); `.github/workflows/ci.yml` (`lint`, `typecheck`, `coverage` jobs; header "Four levels"→"Five levels"); `.gitignore` (coverage outputs); 4 test files (F401 fixes); `src/agentsec/trace/schema.py`, `trace/recorder.py`, `cli.py` (annotation/cast only). |
| **Validation** | `ruff check` clean; `mypy` 0 errors (40 files); coverage baseline measured (852→ statement 96%, branch 89%, combined 94%). |
| **Remaining work** | The **coverage floor** named in B4 (deliberately deferred — a threshold needs a stable baseline); the **format gate** (deferred wholesale in `research/41` §7 as a ~50-file mechanical change). |

### 2.2 B5 — exact warning-set assertion

| Field | Value |
| --- | --- |
| **Planned item** | `research/39` §9 **B5 [PROPOSED]** — "Make the release-gate exact: assert the emitted warning set matches the documented set, and fail on an *unexpected* new warning." |
| **Implementation status** | **[IMPLEMENTED]** |
| **Evidence** | `research/45`; `tests/test_release_check.py` gains `ACCEPTED_RELEASE_WARNINGS = frozenset({"W6","W7","W12"})` and `test_repository_reports_exactly_the_accepted_warning_set`, asserting on structured `Warning.id` results (not console text). |
| **Files changed** | `tests/test_release_check.py` only (plus `research/45`). |
| **Validation** | New test passes; suite 852→**853**; the gate still reports **READY WITH WARNINGS**, `blockers: []`, `warnings {W6, W7, W12}`. |
| **Remaining work** | None for B5 itself. The plan pairs B5 with the Phase 5 release decision (retire/restate W12, close W6 via `date-released`), which is **not** part of this close-out. |

### 2.3 Related CI items (Phase 2) — completed, for completeness

| Item | Plan wording | Status | Evidence |
| --- | --- | --- | --- |
| **B1** | Install `.[docs]` so MkDocs is `PASS`, not `WARN` | **[IMPLEMENTED]** | `release-readiness` installs `.[dev,docs]`; gate `mkdocs: PASS` |
| **B2** | De-duplicate the pytest run | **[IMPLEMENTED]** | committed `fc80f26` (`Simplify CI release validation`); one standalone pytest |
| **B3** | Python-version matrix (3.11 + 3.13) | **[IMPLEMENTED]** | `compatibility` job `matrix.python-version: ["3.11","3.13"]`, `fail-fast: false` |

### 2.4 Companion Phase 3 item — not started

| Item | Plan wording | Status | Note |
| --- | --- | --- | --- |
| **D1** | Add `py.typed` and type-check the public surface | **[NOT STARTED]** | No `src/agentsec/py.typed` exists; the plan places D1 in the same phase as B4. |

## 3. Deviations from the plan (recorded, not silent)

1. **B4's "coverage floor" was deliberately not added.** B4.3 established a
   *measured* baseline and a **report-only** job instead (§5 of `research/41`,
   §4 of `research/44`): a floor chosen without a baseline is an invented number,
   and a failing floor would effectively be a release blocker requiring a change
   to `scripts/release_check.py`. The reconciliation marks B4 **[PARTIAL]** for
   this reason — the floor is *remaining work*, not an oversight.
2. **The "format" gate in B4 was deferred.** `research/41` §7/§8 recommended
   deferring formatting/import-sorting as a separate ~50-file mechanical change;
   B4.1/B4.2/B4.3 added **lint + type + coverage** only.
3. **`research/39` was not edited.** The plan's B4/B5 remain tagged `[PROPOSED]`;
   the authoritative status is this record, consistent with the add-a-record-per-
   step convention (§0).

## 4. What is now complete

* **B4 (mostly):** hermetic, offline, single-run **Ruff** lint gate and **mypy**
  type-check gate in CI, plus a **report-only** coverage baseline and job. Three
  independent, non-matrix CI jobs; `release_check.py` still invoked exactly once.
* **B5 (fully):** the repository's release warning set is now an explicit,
  regression-protected contract (`{"W6","W7","W12"}`); a new or silently resolved
  warning fails a structured test.
* **Phase 2 (B1, B2, B3):** MkDocs `PASS`, single pytest run, 3.11+3.13 matrix.

## 5. Remaining work (after this close-out)

* **D1** — `py.typed` + type-checking the public surface (the other half of
  Phase 3).
* **Coverage floor** — optional; would need a stable baseline and a decision to
  make coverage a gate rather than a report.
* **Format gate** — optional, deferred by `research/41`.
* **Phase 4 education** (C1, C5, optional C3/C4) — unaffected by this close-out.
* **Phase 5 release decision** (A5, A6, A7, A8) — version bump to `0.1.0`,
  `date-released` (closes W6), W7/W12 decisions; B5 is already in place.

## 6. Validation results (after the documentation change)

| Command | Result |
| --- | --- |
| `python -m pytest` | **853 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `python -m mypy` | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 185 files accounted for (mit 125, cc-by 58, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]` |
| `git diff --check` | clean |

## 7. Confirmations

* **`blockers: []`** — confirmed by the release gate.
* **Warnings remain exactly `W6`/`W7`/`W12`** — none resolved, suppressed or
  reclassified; `git_state` is the only non-`PASS` gate (dirty dev tree) and is
  not one of the warning IDs.
* **Version remains `0.0.1`** (`check_version.py` 3/3).
* **`v0.0.1` tag remains untouched** — object
  `cd60b32c7da3174423657e3ec53ecb7dd120eecb` → commit `121acc3`.
* **No implementation file was modified by this step** — the only file added is
  this record; the pre-existing B4/B5 working-tree changes are unchanged.
* **No generated artifacts remain** — no `.coverage`, `coverage.xml`, `htmlcov/`,
  `.mypy_cache/`, probe or temporary files in `git status`.
* **No commit, push or tag was performed.**

## 8. Files changed by this step

```
research/46-b4-b5-closeout.md   (this record, new)
```

No other file was created or modified.

### Safety boundary (Phase 17)

This step adds no runtime code, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains **HOLD**;
no novelty, effectiveness, security-effectiveness, benchmark or publication claim
is made.
