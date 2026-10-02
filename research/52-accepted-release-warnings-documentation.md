# PHASE 21 — ACCEPTED RELEASE WARNINGS DOCUMENTATION (v0.1.0)

*Documentation step for the v0.1.0 release preparation (`research/51`): a short,
site-served reference that records the accepted release warnings. It adds **one
documentation page**, **one MkDocs navigation entry** and **one focused test
module**; it changes no release logic. Nothing was committed, pushed or tagged;
`scripts/release_check.py` is untouched and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the v0.1.0 preparation was complete: version `0.1.0` at 3/3,
`CITATION.cff` with `date-released: 2026-10-01` (W6 closed), the B5 policy
`ACCEPTED_RELEASE_WARNINGS = {"W7", "W12"}`, and the gate at **READY WITH
WARNINGS** with `blockers: []` and warnings `["W12","W7"]`. The accepted set was
`{W7, W12}`; W6 was closed. Baseline suite: **880 passed**, labs 8/8, Ruff clean,
mypy 0/40, MkDocs strict PASS, licensing 9/9.

**Placement decision.** The documentation site's `docs_dir` is `labs/`, so a page
under `docs/` is *not* part of the MkDocs site and cannot enter its navigation.
The page therefore lives at `labs/ACCEPTED-RELEASE-WARNINGS.md`, consistent with
the other site-served `labs/` pages (`TRACE-FIELD-REFERENCE.md`,
`LOCAL-VERIFICATION.md`), so it can be both built and nav-listed.

## 2. Files changed

Added:

```
labs/ACCEPTED-RELEASE-WARNINGS.md         (new site page, CC BY 4.0)
tests/test_accepted_release_warnings.py   (new focused guard, MIT)
research/52-accepted-release-warnings-documentation.md   (this record)
```

Modified:

```
mkdocs.yml   + nav entry "Accepted Release Warnings: ACCEPTED-RELEASE-WARNINGS.md"
             under "Local Verification"
```

No other file was changed. `licensing/manifest.toml` needed no edit: its existing
globs already cover the new files (`labs/**.md` → CC BY 4.0, `tests/**` → MIT).

## 3. Documentation added

`labs/ACCEPTED-RELEASE-WARNINGS.md` is a concise operational reference (not a copy
of the audit). It states:

* **v0.1.0 release context** — version 0.1.0, release date 2026-10-01, gate
  `READY WITH WARNINGS`.
* **The invariant** — the accepted set for v0.1.0 is **exactly `{W7, W12}`**.
* **W7** — what it means (`.freebuff/project-id` is tracked, hence distributed),
  why it remains (intentionally kept tracked; not untracked, gitignored or
  re-manifested), and why it is accepted (deliberate, low-risk, manifest already
  records it as `excluded`).
* **W12** — what it means (human-judgement licensing residuals), why it remains
  (release-check behaviour intentionally unchanged; appended unconditionally), and
  why it is accepted/re-stated (documented on three surfaces, carried knowingly).
* **W6** — explicitly **CLOSED**, not accepted, because `CITATION.cff` now carries
  `date-released: 2026-10-01`; the page shows the YAML.
* **Enforcement** — a new warning, or a warning that disappears, **fails** the
  exact-set-equality regression test rather than being silently accepted.
* **Gate honesty** — the release stays `READY WITH WARNINGS`; it is not forced to
  `READY`.

The page links only within the site (`docs_dir = labs/`); the two research records
it cites are referenced as plain code paths, not Markdown links, so `mkdocs build
--strict` stays green.

## 4. Tests added

`tests/test_accepted_release_warnings.py` — four focused guards:

1. `test_page_exists` — `labs/ACCEPTED-RELEASE-WARNINGS.md` exists.
2. `test_page_documents_the_accepted_warnings_w7_and_w12` — W7 and W12 appear and
   the set is stated as `{W7, W12}`.
3. `test_page_marks_w6_as_closed` — W6 is present, is identified as **CLOSED**,
   and the page records the `date-released: 2026-10-01` reason.
4. `test_page_is_listed_in_the_mkdocs_navigation` — the page is in the MkDocs nav.

No CI job was added, and no existing test was modified.

## 5. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **885 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 200 files accounted for (mit 132, cc-by 66, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `git diff --check` | clean |

**Test delta: 880 → 885 (+5).** The new module contributes its 4 tests plus one
`tests/test_architecture.py` parametrization entry (that suite parametrizes over
every `tests/*.py` file, so a new test module adds one collected case there).

## 6. Warning-set result

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` closed,
`blockers: []`, and the only non-`PASS` gate is `git_state: WARN` (working tree
dirty by design until the owner commits).

## 7. Untouched

* `scripts/release_check.py` — **no change**; W12 retained, detection unchanged.
* `.freebuff/project-id` tracking, `.gitignore`, `licensing/manifest.toml` — no
  change (W7 kept).
* `.github/workflows/ci.yml`, `.github/workflows/docs.yml` — no change; no new CI
  job.
* `schemas/**`, `labs/LAB-00`…`LAB-07` definitions, runtime behaviour, packaging
  configuration — no change. Version remains `0.1.0`.
* `research/1`–`research/51` — not modified.

## 8. Tag and Git status

* `v0.0.1` — **unchanged**: tag object
  `cd60b32c7da3174423657e3ec53ecb7dd120eecb` still resolves; `git tag` lists only
  `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`,
  no `git tag`.

## 9. Confirmation

The accepted warning set for v0.1.0 is exactly `{W7, W12}`; W6 is closed; the
release gate remains **READY WITH WARNINGS** by decision. Phase 17 remains
**CLOSED** and E1 remains **HOLD**; no novelty, effectiveness, security,
benchmark or publication claim is made.
