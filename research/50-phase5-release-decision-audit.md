# PHASE 21 — PHASE 5 RELEASE-DECISION AUDIT (v0.1.0)

*Audit and preparation only. **No implementation change was made**: no version
bump, no `date-released`, no warning resolved, no warning policy changed, no tag,
no commit, no push. The only file created is this record. The existing
uncommitted B4/B5/D1/C1/C5/C3 work is preserved as-is.*

## 1. Executive summary

The repository is green and **READY WITH WARNINGS** at the current uncommitted
tree. A `v0.1.0` release is **not yet prepared**: the version is still `0.0.1`
in all three authoritative declarations, `CITATION.cff` still has no
`date-released` (W6), and no `v0.1.0` change record exists. Phase 5 is
**decision-gated**, not blocked: the mechanical work (version bump + the planned
`date-released`) is small, but two warnings require an explicit owner decision
(**W7** and **W12**), and closing W6 forces a **deliberate** update to B5's
`ACCEPTED_RELEASE_WARNINGS` policy. Nothing here changes the release gate's
behaviour.

## 2. Current repository baseline (measured, read-only)

| Item | Value |
| --- | --- |
| Branch / HEAD | `v0.1.0-dev` / `fc80f26` |
| Tag present | `v0.0.1` (untouched) |
| Package version | **`0.0.1`** |
| Tests | **880 passed** |
| Labs | **8/8** (LAB-00 … LAB-07; no LAB-08) |
| Ruff | clean |
| mypy | **0 errors / 40 files** |
| MkDocs `--strict` | exit 0 |
| Licensing | **9/9** (195 files: mit 131, cc-by 62, excluded 2, unlicensed 0) |
| Version consistency | **3/3** |
| Release gate | **READY WITH WARNINGS**, `target_version 0.0.1`, `blockers: []` |
| Warning IDs | **`W6`, `W7`, `W12`** |
| Gate statuses | all `PASS` except `git_state: WARN` (dirty working tree) |
| Working tree | dirty by design (uncommitted B4/B5/D1/C1/C5/C3 work) |

## 3. Phase 5 requirements from the plan (`research/39`)

* **§13 Phase 5 — Release decision (A5, A6, A7, A8, B5):** "Bump the version to
  `0.1.0` in all three places, add `date-released`, decide W7, retire/restate
  W12, assert the exact warning set, write the `v0.1.0` change record."
* **A5** — add `date-released` to `CITATION.cff` **at release time** and bump the
  three declarations to `0.1.0` **together**. *(Closes W6.)*
* **A6** — **decide** W7 (keep `.freebuff/project-id` tracked with its explicit
  excluded treatment, or untrack it).
* **A7** — reduce W12 by **retiring** the human-judgement licensing residual or
  **explicitly re-documenting** it, so the gate can reach `READY`.
* **A8** — a machine-readable release manifest / changelog for `v0.1.0` (what
  changed since `v0.0.1`).
* **B5** — the exact warning-set assertion is already implemented; the plan
  expects the policy to be updated deliberately at the release.
* **§11.3** — "version bump to `0.1.0` across all three declarations,
  `date-released`, a documented `v0.1.0` change record, and **either** retiring
  W12 **or** restating it as an accepted, explicit residual."
* **§15** — update the README **verification-status table**; bump `CITATION.cff`;
  record the `0.1.0` status in `docs/development.md`; keep the Phase 17
  CLOSED / research-freeze section authoritative.
* **§17 acceptance criteria (release) — the relevant ones:** (1) all three
  declarations read `0.1.0` (`check_version.py` 3/3); (2) licensing 9/9, 0
  unaccounted; (3) tests pass (≥ current 880 + tests for new behaviour);
  (4) labs 8/8; (5) `mkdocs --strict` exits 0 with 0 warnings, answer key out of
  nav; (6) schema copies byte-identical; (7) wheel self-contained, version
  `0.1.0`, licence MIT; (8) gate **`READY`** — or, if W12 is retained,
  **`READY WITH WARNINGS`** with a **documented, explicit** warning set and
  `blockers: []` (W6 closed; W7/W9/W10/W11/W13 closed or explicitly re-accepted;
  W12 stated by decision, not accident); (9) CI green, pytest once, MkDocs
  `PASS`; (10) Phase 17 CLOSED, E1 HOLD, no research claim; (11) hygiene passes,
  tree matches the release commit; (12) the `v0.1.0` change record lists every
  changed file and the residual status of W6–W13 and R-1–R-5.

## 4. Version inventory

Authoritative trio (parsed by `scripts/check_version.py`; `pyproject.toml` is the
single source of truth):

| File | Location | Current value | Expected `v0.1.0` action |
| --- | --- | --- | --- |
| `pyproject.toml` | `[project] version` (line 9) | `0.0.1` | **change → `0.1.0`** (authoritative) |
| `src/agentsec/__init__.py` | `__version__` (line 60) | `0.0.1` | **change → `0.1.0`** |
| `CITATION.cff` | top-level `version:` (line 5) | `0.0.1` | **change → `0.1.0`** (+ `date-released`) |

Other occurrences (classification matters):

| File | Location | Current | Expected action |
| --- | --- | --- | --- |
| `README.md` | line 349, citation example "(version 0.0.1)" | `0.0.1` | **update to `0.1.0`** (documentation example) |
| `README.md` | line 224, verification table "849 tests pass" | `849` | **update to `880`** (stale, not a version field) |
| `README.md` | line 92, "36 practice exercises (sets A–G)" | `A–G` | **update** (C1 added sets H, I and a per-lab section) |
| `README.md` | line 113, CLI list `run`, `inspect`, `evaluate`, `labs check` | — | optionally note `inspect --events` (C3) |
| `scripts/release_check.py` | line 1 docstring "whether v0.0.1 is ready" | `v0.0.1` | **optional** text update only; behaviour uses `target_version` read from `pyproject.toml` |
| `tests/test_version.py` | `VERSION = "0.0.1"` + fixture asserts | `0.0.1` | **no change** — used only for `tmp_path` fixtures |
| `tests/test_release_check.py` | `make_repo(version="0.0.1")`, fixture `target_version == "0.0.1"` | `0.0.1` | **no version change** — fixtures, not the real repo |
| `tests/test_licensing.py` | fixture `'version = "0.0.1"'` (line 86) | `0.0.1` | **no change** — fixture |
| `src/agentsec.egg-info/PKG-INFO` | generated, git-ignored | `0.0.1` | regenerated by reinstall; not committed |
| `research/**` (historical records) | e.g. `research/1`–`research/50` | `0.0.1`/`v0.0.1` | **do NOT touch** — historical records are not updated |

**Conclusion:** exactly **three** files change the version (the authoritative
trio); `README.md` carries one documentation example that should follow. **No
test hardcodes the real repository version**, so no version-related test change
is required.

## 5. W6 analysis

* **Source location:** `scripts/release_check.py`, `detect_warnings()` (lines
  ~618–623).
* **Exact condition:** `CITATION.cff` exists **and** contains no unindented
  `^date-released:` line → append `Warning("W6", "CITATION.cff has no
  date-released (add it at release time)")`.
* **Current state:** `CITATION.cff` has no `date-released` field (confirmed by
  reading the file); W6 is emitted today.
* **Exact action for `v0.1.0`:** add a top-level `date-released:` (a date) to
  `CITATION.cff`, in the same change as the version bump.
* **Expected to disappear?** **Yes** — the condition becomes false, so
  `detect_warnings` stops emitting W6.
* **What proves resolution:** the release gate's JSON `warnings` no longer
  contains `W6`; `tests/test_release_check.py`'s
  `test_repository_reports_exactly_the_accepted_warning_set` (B5) **fails until**
  `ACCEPTED_RELEASE_WARNINGS` is updated deliberately. There is **no
  W6-specific** fixture test asserting its own disappearance by name; the exact-set
  test is the guard.

## 6. W7 analysis

* **Source location:** `scripts/release_check.py`, `detect_warnings()` (lines
  ~625–628).
* **Exact condition:** `".freebuff/project-id" in set(_git_lines(ctx, run,
  "ls-files"))` → append W7.
* **Why it exists:** `.freebuff/project-id` **is tracked** (`git ls-files`
  confirms), so it is distributed in a clone, yet it is local tooling metadata.
  `licensing/manifest.toml` already records it explicitly as **`status =
  "excluded"`** ("tracked local tooling metadata, outside both grants").
* **Alternatives available** (the plan's A6 framework — *the owner decides*):
  1. **Keep it tracked**, explicitly re-accepted, with its existing `excluded`
     manifest entry (this is the documented treatment already in place). W7
     remains.
  2. **Untrack it** (`git rm --cached .freebuff/project-id`, add to
     `.gitignore`, adjust the manifest entry). W7 disappears.
* **Consequences:** keeping it leaves the gate at `READY WITH WARNINGS` with W7
  as a stated residual; untracking removes W7 and edits `.gitignore` +
  `licensing/manifest.toml`, changing the tracked set (and the W7 test
  precondition).
* **What the plan says:** A6 lists precisely those two options and does **not**
  recommend one; §17.8 accepts either "closed or explicitly re-accepted".
* **This audit does not choose** on the owner's behalf.

## 7. W12 analysis

* **Source location:** `scripts/release_check.py`, `detect_warnings()`
  (unconditional append, lines ~664–666).
* **Exact condition:** **always** emitted — `Warning("W12",
  "human-judgement licensing residuals remain (review research/28–research/36)")`.
* **Current wording/behaviour:** unconditional, so `READY` (no warnings) is
  currently **unreachable by construction** (the plan's earlier R-4).
* **What the plan requires (A7 / §11.3 / §17.8):** **either** retire it (remove
  the unconditional emission, which changes `release_check.py`),
  **or** restate it deliberately as an accepted, explicit residual and document
  that the gate is expected to stay `READY WITH WARNINGS`.
* **Possible release-time treatments** (*the owner decides*):
  1. **Retire:** drop the unconditional W12 emission in `release_check.py` and
     update the B5 policy — the gate could then reach `READY` once W6/W7 are
     resolved.
  2. **Restate (accept):** keep W12, document the decision in the `v0.1.0`
     change record, and keep B5 accepting `W12`.
* **This audit does not choose** on the owner's behalf. Note: retiring W12 is a
  **behavioural change to the release gate** and is explicitly out of scope for
  an audit.

## 8. B5 policy impact

Implementation inspected: `tests/test_release_check.py`
`ACCEPTED_RELEASE_WARNINGS = frozenset({"W6", "W7", "W12"})` (line 621) and
`test_repository_reports_exactly_the_accepted_warning_set`, which asserts the
**real repository's** structured `Warning.id` set equals that constant.

```
Current accepted set:  {W6, W7, W12}

Expected post-release set: (decision-dependent — derived, not guessed)
  W6  -> EXPECTED TO DISAPPEAR  (A5 adds date-released)
  W7  -> DEPENDS on A6: kept-tracked => remains; untracked => disappears
  W12 -> DEPENDS on A7: restated => remains;  retired   => disappears
```

Enumerated outcomes:

| W7 decision | W12 decision | Post-release set | Gate classification |
| --- | --- | --- | --- |
| keep | restate | `{W7, W12}` | READY WITH WARNINGS |
| keep | retire | `{W7}` | READY WITH WARNINGS |
| untrack | restate | `{W12}` | READY WITH WARNINGS |
| untrack | retire | `{}` | **READY** |

Whatever the owner chooses, the constant and the test must be updated
**deliberately** in the release change (that is exactly the B5 mechanism working
as designed). A warning must **not** be removed merely because it is
inconvenient — each removal must correspond to a real change (W6 by
`date-released`; W7 by untracking; W12 by a `release_check.py` policy change).

## 9. Release metadata requirements

| Requirement | Current state | Needed for a clean `0.1.0` |
| --- | --- | --- |
| Version (3 declarations) | all `0.0.1` | set to `0.1.0` together (A5) |
| `CITATION.cff` `date-released` | **absent** | **add** (A5, closes W6) |
| Release/change record, `v0.1.0` (A8) | **does not exist** (no `CHANGELOG*`) | **create**; list changed files + residual W6–W13/R-1–R-5 (§17.12) |
| README verification-status table | stale (`849 tests`, sets A–G, CLI list) | update (test count 880, exercise sets, `--events`) (§15) |
| README citation example | `version 0.0.1` | update to `0.1.0` |
| `docs/development.md` release status | no `0.1.0` status line | record the `0.1.0` status (§15) |
| Package metadata | SPDX MIT, authors/classifiers/keywords/urls present | no change (already modern) |
| Tag expectations | `v0.0.1` only | owner creates `v0.1.0` **after** the release commit; agent does not tag |
| Licensing manifest | 195 files accounted | any **new root-level file** (e.g. a `CHANGELOG.md`) needs a manifest entry, else licensing fails 9/9 |

## 10. Cumulative release contents (since `v0.0.1`, factual)

**Committed** (`git log v0.0.1..HEAD`):

* `32b2ef1` Add v0.1.0 development plan (`research/39`).
* `9cb2d45` Close packaging hygiene warnings — A1/A2/A4: SPDX `license`,
  `license-files`, authors/keywords/classifiers, `[project.urls]`,
  `setuptools>=77`, pinned `docs` extra; dropped stale `traces/*.jsonl`
  (closes W10, W11, W13).
* `fc80f26` Simplify CI release validation — B2 (single pytest run) and B1
  (docs extra installed so MkDocs is `PASS`).

**Implemented but uncommitted** (working tree):

* **B3** — Python compatibility matrix `["3.11", "3.13"]` (`ci.yml`).
* **B4.1** — Ruff lint gate (`[tool.ruff.lint]`, `lint` job).
* **B4.2** — mypy type-check gate (`[tool.mypy]` + stub packages, `typecheck` job).
* **B4.3** — coverage, **report-only** (pytest-cov, `coverage` job).
* **B5** — exact warning-set assertion (`ACCEPTED_RELEASE_WARNINGS`).
* **D1** — `py.typed` + public-surface consumer type check.
* **C1** — trace-reading education (exercise sets H, I, per-lab what-if, answers).
* **C5** — schema-derived trace field reference (`labs/TRACE-FIELD-REFERENCE.md`
  + generator + drift/nav tests).
* **C3** — richer read-only `inspect --events`.
* Records `research/41`–`research/49`.

Five CI jobs now exist: `lint`, `compatibility`, `typecheck`, `coverage`,
`release-readiness`; `release_check.py` is still invoked exactly once.

## 11. Deferred items

* **Coverage floor** — deferred; coverage is report-only (`research/44`, B4.3).
* **Formatting / import-sorting gate** — deferred (`research/41` §7; ~50-file
  mechanical change).
* **C4** — optional: use the three unused mock fixtures without adding a
  numbered lab. **Not implemented.**
* **W9** — stale editable-install metadata: **not currently emitted** (the local
  `egg-info` is fresh); a local-only, git-ignored warning.
* **W10, W11, W13** — closed by `9cb2d45`; a regression would re-introduce them.
* **R-1/R-2** — addressed (`fc80f26`, B1). **R-3** — self-containment degrades to
  `WARN` offline (by design). **R-4** — W12 makes `READY` unreachable unless A7
  retires it. **R-5** — the gate reports W6/W7 but does not decide them (A6/A7).
* No `LAB-08`; no research implementation; Phase 17 remains CLOSED.

## 12. Validation results (this audit, read-only)

| Command | Result |
| --- | --- |
| `python -m pytest` | **880 passed** (exit 0) |
| `python -m agentsec labs check` | **8/8 labs passed** (exit 0) |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 195 files accounted |
| `python scripts/check_version.py` | **3/3** — all `0.0.1` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]`, only `git_state: WARN` |
| `git diff --check` | clean |
| `git status --short` | expected uncommitted work only; no stray artifacts |

`git_state` is `WARN` **solely** because the working tree is dirty (the
intentional, uncommitted release work), not because of any failing gate.

## 13. Exact proposed implementation sequence for the NEXT step

*(To be executed only after the owner resolves the W7 and W12 decisions. Each
step ends green.)*

1. **Owner decisions first:** choose **A6 (W7)** and **A7 (W12)** from §6/§7.
2. **Version + citation (A5):** set `pyproject.toml`, `src/agentsec/__init__.py`
   and `CITATION.cff` to `0.1.0` **together**, and add `CITATION.cff`
   `date-released`. Run `check_version.py` (expect 3/3) and the gate (expect W6
   gone).
3. **B5 policy update:** set `ACCEPTED_RELEASE_WARNINGS` in
   `tests/test_release_check.py` to the post-release set from §8 and confirm the
   exact-set test passes.
4. **If A7 = retire W12:** make the minimal `release_check.py` change (remove the
   unconditional W12) and its documentation; otherwise record W12 as an accepted
   residual. *(Behavioural gate change — owner-approved only.)*
5. **If A6 = untrack W7:** `git rm --cached .freebuff/project-id`, add it to
   `.gitignore`, update `licensing/manifest.toml`; otherwise leave as the
   documented `excluded` entry.
6. **Release record (A8):** create the `v0.1.0` change record listing changed
   files and the residual W6–W13 / R-1–R-5 status. If a root-level file such as
   `CHANGELOG.md` is chosen, add its `licensing/manifest.toml` entry in the same
   change.
7. **Documentation (§15):** update the README verification-status table
   (**880** tests), the exercise-set line (sets A–I + per-lab), the CLI list
   (`inspect --events`), the citation example (`0.1.0`), and record the `0.1.0`
   status in `docs/development.md`.
8. **Full validation:** re-run pytest, labs, ruff, mypy, `mkdocs --strict`,
   licensing, version, `release_check.py --json`, `git diff --check`.
9. **Owner** commits and tags `v0.1.0` (the agent does not commit/push/tag).

## 14. Files that will need modification during implementation

* `pyproject.toml` — version → `0.1.0`.
* `src/agentsec/__init__.py` — `__version__` → `0.1.0`.
* `CITATION.cff` — `version` → `0.1.0`; add `date-released`.
* `tests/test_release_check.py` — `ACCEPTED_RELEASE_WARNINGS` policy (§8).
* `README.md` — verification table, exercise counts, CLI list, citation example.
* `docs/development.md` — `0.1.0` release status (§15).
* **New:** the `v0.1.0` change record (A8) — location is an owner decision
  (`CHANGELOG.md` vs a `research/` record).
* **Conditional:** `scripts/release_check.py` (only if A7 = retire W12; and/or the
  stale `v0.0.1` docstring line), `.gitignore` + `licensing/manifest.toml` (only
  if A6 = untrack W7), and `licensing/manifest.toml` again if a new root-level
  record file is added.

## 15. Files that must remain untouched

* `scripts/release_check.py` **logic** (unless A7 explicitly retires W12),
  `scripts/check_version.py`, `scripts/check_licensing.py`,
  `scripts/export_trace_schema.py`, `scripts/export_trace_reference.py`.
* `.github/workflows/ci.yml` and `.github/workflows/docs.yml`.
* `schemas/**` and the package data schema copies.
* `labs/LAB-00`…`LAB-07` definitions; `labs/TRACE-FIELD-REFERENCE.md` and the
  other generated/education pages except where §15 doc updates require.
* `src/agentsec/**` other than the `__version__` line.
* `licensing/manifest.toml` and `.gitignore` except the conditional A6/new-file
  edits above.
* `research/1`–`research/49` (historical records) and `research/39`.
* The `v0.0.1` tag and any tag.
* Package quality-gate configuration (`[tool.ruff.lint]`, `[tool.mypy]`,
  coverage report-only) unless a dependency change is genuinely required.

## 16. Statement of no implementation change

This audit **made no implementation change**. It did not modify `pyproject.toml`,
`CITATION.cff`, `scripts/release_check.py`, `.github/workflows/ci.yml`,
`tests/test_release_check.py`, any source, lab, schema, or documentation; it did
not change the warning policy, did not bump the version, did not resolve W6/W7/
W12, did not create or move any tag, and did not commit or push. The only file
created is `research/50-phase5-release-decision-audit.md`. The version remains
`0.0.1`; the `v0.0.1` tag remains untouched; the warning set remains exactly
`W6`, `W7`, `W12`; `blockers` remain `[]`.
