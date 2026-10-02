# PHASE 21 — OWNER PRE-TAG CHECKLIST (v0.1.0)

*Documentation/governance step following the single-gate-run integration
(`research/56`): a concise, executable owner checklist for the v0.1.0 tag is added
to the canonical accepted-warnings page, with focused documentation guards. This
step changes **no runtime, CI, warning-detection, warning-policy, version or
tooling behaviour**. Nothing was committed, pushed or tagged; the `v0.0.1` tag is
unchanged and no `v0.1.0` tag was created.*

## 1. Context

The release is prepared and green: version `0.1.0` (3/3), gate
**READY WITH WARNINGS**, `blockers: []`, accepted warning set exactly
`{W7, W12}`, `W6` closed, drift check exit `0`, and CI running `release_check.py`
once and feeding its captured JSON report to the drift checker (`research/55`,
`research/56`). What was missing was a single, ordered, **owner-facing** procedure
for the final review before the `v0.1.0` tag — gathering the already-established
checks rather than inventing new requirements.

## 2. Files changed

Modified:

```
labs/ACCEPTED-RELEASE-WARNINGS.md        + "Owner pre-tag checklist for v0.1.0"
tests/test_accepted_release_warnings.py  + 4 focused documentation guards
```

Added:

```
research/57-owner-pre-tag-checklist.md   (this record, CC BY 4.0)
```

`licensing/manifest.toml` needed no edit: existing globs cover the new record
(`research/**.md` → CC BY 4.0). No `mkdocs.yml` change — the checklist lives on
the already navigation-listed page.

## 3. The checklist

Added to `labs/ACCEPTED-RELEASE-WARNINGS.md` as an owner-facing section with ten
ordered parts and a fill-in result template:

1. **Working-tree review** — `git status`; inspect the complete diff; confirm
   every changed/new file is intentional; confirm no generated artifacts.
2. **Version** — `python scripts/check_version.py`; confirm 3/3 at `0.1.0` and no
   unintended version string.
3. **Tests and quality gates** — `python -m pytest`, `python -m agentsec labs
   check`, `ruff check src tests scripts`, `python -m mypy`, `python -m mkdocs
   build --strict`, `python scripts/check_licensing.py`; **verify success**, not
   merely execution.
4. **Release gate** — `python scripts/release_check.py --json`; verify
   `target_version 0.1.0`, `blockers []`, `READY WITH WARNINGS`, warnings exactly
   `{W7, W12}`; do not force `READY`.
5. **Warning drift** — `python scripts/check_warning_drift.py`; confirm exit `0`,
   proving the B5 policy, the canonical documentation and the actual gate agree
   (CI reuses the captured report via `--gate-report`).
6. **Release metadata** — `CITATION.cff` `version: "0.1.0"` +
   `date-released: 2026-10-01`; README version consistency; `docs/development.md`
   `0.1.0` status; this page in the MkDocs navigation. No invented requirements.
7. **Warning decisions** — W6 closed; W7 accepted; W12 accepted/re-stated; no new
   warning added to the accepted set to go green. References the retirement
   procedure above instead of duplicating it.
8. **Protected invariants** — `scripts/release_check.py` unchanged by release
   preparation; `.freebuff/project-id` intentionally tracked;
   `licensing/manifest.toml` correct; `.github/workflows/docs.yml` unchanged;
   schemas and lab runtime unchanged unless documented; no stray artifacts.
9. **Git history and tag** — `git diff --check`, `git status`, `git log
   --oneline --decorate -n 20`, `git tag`; confirm `v0.0.1` unchanged, no
   `v0.1.0` tag yet, intended commit contents only. Do not create the tag
   automatically.
10. **Human release decision** — the checklist ends with an **owner decision**;
    the agent must not commit, push, create the `v0.1.0` tag or publish a release,
    and must not alter W7/W12, change the classification, or modify
    `scripts/release_check.py`.

A `v0.1.0 PRE-TAG REVIEW` template (Version → Owner approval, then "v0.1.0 tag
created: YES / NO") lets the owner record the result, and the section states that
`READY WITH WARNINGS` with `blockers: []` and warnings exactly `{W7, W12}` is the
**expected** result, not a failure.

## 4. Tests added

`tests/test_accepted_release_warnings.py` gained four guards:

- `test_page_documents_the_owner_pre_tag_checklist` — the section heading is
  present.
- `test_owner_checklist_lists_the_release_commands` — every required command
  (version, pytest, labs, Ruff, mypy, MkDocs, licensing, release gate, drift
  check, `git diff --check`, `git tag`) appears.
- `test_owner_checklist_states_the_expected_warning_set_and_blockers` — the page
  names `{W7, W12}`, `Blockers:`, `READY WITH WARNINGS`, and calls it *expected*.
- `test_owner_checklist_reserves_tagging_for_the_owner` — the page ends with an
  owner decision (`Owner approval`) and forbids the agent from committing,
  pushing or tagging (`must not commit, push, create the v0.1.0 tag`).

No CI job was added. No existing test was modified.

## 5. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **948 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 208 files accounted for (mit 135, cc-by 71, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `target_version 0.1.0`, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| CI YAML parse | valid; exactly **five** jobs |
| `scripts/release_check.py` occurrences in executable CI `run:` steps | **1** |
| drift step uses `--gate-report` | yes; no `continue-on-error` anywhere |
| `git diff --check` | clean |

**Test delta: 944 → 948 (+4).** Four new documentation guards in an existing
module; no new test module (so the architecture parametrization count is
unchanged). No existing test was modified.

## 6. Warning set and release gate

Unchanged and exact: **`{W7, W12}`** (JSON order `["W12","W7"]`), `W6` **closed**,
`blockers: []`, classification **READY WITH WARNINGS**. The drift check reports
all three surfaces equal.

## 7. Protected invariants

- `scripts/release_check.py` — **unchanged** (not touched by the checklist step).
- `scripts/check_warning_drift.py`, `.github/workflows/ci.yml` — **unchanged** by
  this step; the single-gate-run drift integration remains intact (verified: one
  gate invocation, drift step consumes the captured report, no
  `continue-on-error`).
- `.github/workflows/docs.yml`, `licensing/manifest.toml`, `.freebuff/project-id`,
  schemas, lab runtime, version declarations (`pyproject.toml`,
  `src/agentsec/__init__.py`, `CITATION.cff`) — **unchanged** by this step.
- `tests/test_release_check.py` B5 policy — **unchanged**.
- Version remains `0.1.0`. Phase 17 remains **CLOSED**; E1 remains **HOLD**; no
  novelty, effectiveness, security, benchmark or publication claim is made.

## 8. Tag and Git status

* `v0.0.1` — **unchanged**: `git tag` still lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* **Nothing was committed, pushed, or tagged.** The checklist step added no
  commit; generated `site/` output from local validation was removed; no build,
  dist or coverage artifacts remain.

## 9. Remaining owner action

The release is prepared and now has a documented owner procedure. The remaining
action is the owner's: **review the working tree, commit the release changes,
push, and optionally create the `v0.1.0` tag and publish**, using the
`v0.1.0 PRE-TAG REVIEW` template above. Per the checklist, the agent does not
commit, push, tag or publish, and `READY WITH WARNINGS` with `blockers: []` and
warnings exactly `{W7, W12}` is the expected, honest result.
