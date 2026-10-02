# PHASE 21 — WARNING RETIREMENT PROCEDURE

*Documentation step following the accepted-warnings page (`research/52`): it adds
a controlled **retirement procedure** to the canonical page and two focused
regression guards. It changes **no release logic**, retires **no warning**, and
does not touch `scripts/release_check.py`. Nothing was committed, pushed or
tagged; the `v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline warning state

Entering this step the v0.1.0 preparation was complete and documented:

- Version `0.1.0` at 3/3 (`pyproject.toml`, `src/agentsec/__init__.py`,
  `CITATION.cff`).
- `CITATION.cff` carries `date-released: 2026-10-01`, so **W6 is CLOSED**.
- The B5 policy `ACCEPTED_RELEASE_WARNINGS = frozenset({"W7", "W12"})` in
  `tests/test_release_check.py`, pinned by an exact-set-equality test.
- The gate is **READY WITH WARNINGS**, `blockers: []`, warnings
  `["W12", "W7"]`.
- Baseline suite: **885 passed** (after `research/52`), labs 8/8, Ruff clean,
  mypy 0/40, MkDocs strict PASS, licensing 9/9.

The canonical page `labs/ACCEPTED-RELEASE-WARNINGS.md` (from `research/52`)
recorded the accepted set and why each warning is accepted, but said nothing
about how a warning would be **retired**. This step closes that gap.

## 2. Purpose

An accepted warning is a knowing, reviewed decision, so the repository needs an
explicit, ordered procedure for retiring one — otherwise "make the gate cleaner"
could silently become "weaken the assertion". The added section makes clear that
**retiring a warning is not the same as deleting it from the accepted set**: the
underlying condition must be genuinely resolved first, and the exact-set test
then **forces** the policy update.

## 3. Files changed

```
labs/ACCEPTED-RELEASE-WARNINGS.md         + "How to Retire an Accepted Warning"
                                          + "Do not retire warnings by" subsection
tests/test_accepted_release_warnings.py   + 2 focused guards (4 -> 6 tests)
research/53-warning-retirement-procedure.md   (this record, new)
```

No other file was changed. `licensing/manifest.toml` needed no edit: the existing
globs cover the new record (`research/**.md` → CC BY 4.0) and the page/test
(`labs/**.md` → CC BY 4.0, `tests/**` → MIT). `mkdocs.yml` needed no change — the
page was already nav-listed by `research/52`.

## 4. Procedure documented

The page now records the controlled retirement process, in deliberate order:

1. Identify the warning and its precise detection condition in
   `scripts/release_check.py`.
2. Establish that the underlying condition is **genuinely** resolved.
3. Make the smallest implementation/configuration change required.
4. Update the B5 `ACCEPTED_RELEASE_WARNINGS` policy **deliberately** (and its
   comment).
5. Update the documentation and the research record.
6. Run `release_check.py --json` and verify the warning **disappears**.
7. Verify **no unexpected** warning appears.
8. Verify `blockers` remain **empty**.
9. Run the complete validation suite.
10. Record the transition in a **new** research audit.
11. **Only then** consider the next release or tag.

The unit is closed with **current examples**, so the procedure is grounded in the
real repository rather than hypothetical:

- **W7 — accepted (kept).** Accepted because `.freebuff/project-id` remains
  **tracked**. Retirement requires an intentional decision to stop tracking and
  distributing the file. **Do not make that change now.**
- **W12 — accepted / re-stated (kept).** Retirement requires an intentional
  change to the release-check behaviour (`scripts/release_check.py` appends it
  unconditionally). **Do not modify `scripts/release_check.py` now.**
- **W6 — closed (already retired).** The worked example of a warning that
  disappeared **naturally** after its condition was resolved (`CITATION.cff`
  gained `date-released: 2026-10-01`): condition first, then policy.

A **"Do not retire warnings by"** subsection lists the prohibited shortcuts:
weakening/removing the exact-set assertion, broadening the accepted set, changing
the release classification just to obtain `READY`, suppressing warning output, or
modifying unrelated release gates.

## 5. Exact current warning set

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12", "W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**. The only non-`PASS` gate
is `git_state: WARN` (the working tree is dirty by design until the owner
commits). No warning was retired by this step.

## 6. Deliberately NOT changed

* `scripts/release_check.py` — **no change** (W12 retained; detection unchanged;
  no warning suppressed).
* `.freebuff/project-id` tracking, `.gitignore`, `licensing/manifest.toml` — no
  change (W7 kept; manifest entry unchanged).
* `tests/test_release_check.py` — the B5 policy constant and the exact-set
  assertion — **no change** (policy stays `{W7, W12}`; assertion not weakened).
* `.github/workflows/ci.yml`, `.github/workflows/docs.yml` — no change; no new CI
  job, no coverage floor, no formatting/import-sorting gate.
* `schemas/**`, `labs/LAB-00`…`LAB-07` definitions, runtime behaviour, packaging
  configuration — no change. Version remains `0.1.0`. No `LAB-08`, no C4.
* `research/1`–`research/52` — not modified.

## 7. Tests and validation

`tests/test_accepted_release_warnings.py` gained two focused guards (module now 6
tests):

- `test_page_documents_the_retirement_procedure` — the page contains
  "How to Retire an Accepted Warning" and the "Do not retire warnings by" list.
- `test_page_states_retiring_is_not_deleting_from_the_set` — the page states the
  distinction and points at `release_check.py --json` as the proof step.

The existing guards (page exists; W7 and W12 documented as `{W7, W12}`; W6
documented as **CLOSED** with `date-released: 2026-10-01`; page in the MkDocs
navigation) are unchanged. No new test module was added, so the
`tests/test_architecture.py` parametrization count is unchanged. No assertion in
`tests/test_release_check.py` was modified.

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **887 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 201 files accounted for (mit 132, cc-by 67, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `git diff --check` | clean |

**Test delta: 885 → 887 (+2).** Only the two new guards were added.

## 8. Tag and Git status

* `v0.0.1` — **unchanged**: `git tag` still lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** No `git commit`, no `git push`,
  no `git tag`.

## 9. Confirmation

The accepted warning set for v0.1.0 is exactly `{W7, W12}`; W6 is closed; no
warning was retired; the release gate remains **READY WITH WARNINGS** with
`blockers: []` by decision. `scripts/release_check.py` is untouched. Phase 17
remains **CLOSED** and E1 remains **HOLD**; no novelty, effectiveness, security,
benchmark or publication claim is made.
