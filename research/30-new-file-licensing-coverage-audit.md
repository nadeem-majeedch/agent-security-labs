# PHASE 20 — STEP 13: NEW-FILE LICENSING COVERAGE AUDIT

**Status:** PASS — the licensing residual "the guard cannot see a new wrongly-scoped file" is closed by an explicit, machine-checked coverage manifest.
**Scope:** licensing coverage mechanics only. No literature search, no research design, no empirical study design, no learner-data work, no paper drafting, no novelty analysis, no Phase 17 reopening. **E1 remains HOLD.**
**Revision:** `main` at `995cf68` "Research finding complete" (unchanged by this step; nothing committed, staged, or pushed).

---

## 1. Starting repository state

Inspected at the start of this step rather than assumed from the previous report.

| Item | Value |
| --- | --- |
| `HEAD` | `995cf68` "Research finding complete" |
| Branch | `main` |
| Staged files | none (`git diff --cached --name-only` empty) |
| Working tree | dirty with the uncommitted Steps 9–12 work |
| Modified | `.github/workflows/ci.yml`, `README.md`, `pyproject.toml` |
| Untracked | `CITATION.cff`, `LICENSE`, `LICENSE-DATA`, `research/28-…`, `research/29-…`, `scripts/check_licensing.py`, `tests/test_licensing.py` |
| Tracked files | 153 |
| Release-candidate set (tracked + untracked, ignoring `.gitignore`) | 160 before this step; **162** at the final revision (161 Step-13 deliveries plus this audit) |

The two previous licensing audits (`research/28`, `research/29`) and the committed audits (`research/20`–`research/27`) were read but **not modified**: they are historical records. `research/27` still describes the pre-Step-10 state deliberately.

Inspection targets actually read: `LICENSE`, `LICENSE-DATA` (scope notice plus legal-code headers and byte count), `README.md`, `pyproject.toml`, `CITATION.cff`, `scripts/check_licensing.py`, `tests/test_licensing.py`, `research/28-content-licensing-audit.md`, `research/29-licence-ci-guard-audit.md`, `docs/development.md`, `mkdocs.yml`, `.gitignore`, `.github/workflows/ci.yml`, and the whole repository tree (including `runs/`, `site/`, `.freebuff/`, `configs/`, `schemas/`, `policies/`, `labs/`).

## 2. The residual problem

`research/29` §16 recorded residual 10:

> **The guard cannot see a new, wrongly-scoped file.** Adding a Markdown file to `labs/` without updating the README's licensing table passes CI.

That is accurate and it is a real hole, precisely bounded: the six existing checks verify that the *declarations* agree with each other, but none of them knows what files exist. The repository's licensing boundary was **documented and self-consistent, but not complete**. A new file entered the project with no licensing decision recorded anywhere, and the only thing standing between that file and a release was a contributor remembering to edit a README table.

Two distinct failures hide behind the residual, and they are not equally fixable:

1. **Silent omission** — nobody decided anything about the file. This is mechanically detectable.
2. **A wrong decision** — somebody recorded the file under the wrong category. This is *not* mechanically detectable in general; it needs a human judgement about provenance.

This step fixes (1) completely, and narrows (2) from "unnoticed" to "visible in a small reviewed file". §9 records the part that remains.

## 3. Design alternatives considered

| Option | Why it was rejected |
| --- | --- |
| **SPDX headers on every file** | Requires editing all 161 files, produces a large unrelated diff, and still leaves non-commentable formats (JSON, CSV, YAML at scale) needing a side list. Adds churn without adding completeness. |
| **Infer the licence from the file extension** (`.md` → CC BY, `.py`/`.yaml` → MIT) | Explicitly excluded by the step brief, and demonstrably wrong here: `LICENSE` and `LICENSE-DATA` are extensionless, `research/tables/*.csv` is MIT while `research/**/*.md` is CC BY, and `labs/*.yaml` is MIT while `labs/*.md` is CC BY. Extension is not the boundary. Inference would also *pre-empt* the human decision that this step exists to force. |
| **Directory rules only** (`.github/` → MIT, `research/` → CC BY) | Coarser than the boundary the repository actually documents, which splits `labs/**/*.yaml` from `labs/**/*.md` inside one directory. It would also let a whole new directory inherit a licence silently. |
| **`git ls-files`, or parsing `.git/index`** | Needs `subprocess` (the guard is dependency-free and shell-free today) or Git's internal format, and it would *miss untracked files*, i.e. it would catch the problem one commit late. The step brief rules this out as a substitute for a real manifest. |
| **Deriving the ignored set from `.gitignore`** | `.gitignore` is shaped for a different purpose and does not express licences. Re-implementing gitignore semantics inside the guard would be a second, unofficial parser of an ignored-format file. The manifest lists the ignored categories explicitly instead. |
| **A YAML manifest (e.g. `licensing/manifest.yaml`)** | The guard is deliberately standard-library-only so CI can run it *before* `pip install` and fail fast. Parsing YAML would either add a dependency (breaking that ordering) or hand-roll a parser (a new drift risk). TOML is already parsed by the guard with `tomllib` for `pyproject.toml`, so the selected format costs nothing and keeps the offline property. See §5. |
| **A per-file allowlist of all 161 paths** | Correct but unmaintainable: a one-line change would become a 161-line diff, and neither reviewers nor CI would read it. |
| **An explicit category manifest with path patterns** (selected) | Records every decision in one small reviewed file, keeps the repo's stated boundary, and fails loudly when a file is not covered. |

## 4. Why the selected mechanism is conservative

* It **adds** a check and removes none; the six existing checks are untouched in behaviour (§8).
* It **records** decisions instead of deriving them. Nothing is classified by extension, by directory depth, or by a clever rule; every pattern is a line somebody wrote.
* Its **failure mode is over-strictness**, not silence: a file it does not recognise fails the build, and the fix is one line in a reviewed file. The opposite failure — a file quietly inheriting a licence — is not reachable.
* Patterns that match **nothing** are reported, so the manifest cannot rot into a list of decisions about deleted files.
* A path claimed by **two** categories is rejected statically *and* per file, so coverage cannot silently overlap.
* `excluded` and `unlicensed` entries must **say why**. An exclusion is a judgement, and an undecided file is a decision that has not been made; recording either without a reason would recreate the silent classification this manifest exists to prevent.
* The manifest does not widen the boundary: `LICENSE`, `LICENSE-DATA` and `CITATION.cff` are unchanged (§12), and `LICENSE-DATA` remains the authoritative scope statement.

## 5. The manifest: name, format, schema

**`licensing/manifest.toml`** (new, 189 lines).

* **Location.** The repository already organises concerns by top-level directory (`src/`, `tests/`, `scripts/`, `schemas/`, `policies/`, `configs/`, `labs/`, `docs/`, `research/`). A dedicated `licensing/` directory keeps licensing decisions out of `configs/`, which holds *lab experiment* configuration — the two are different kinds of machine-readable input, and mixing them would blur the boundary this file records. Root-level placement was rejected as clutter alongside `pyproject.toml` and `mkdocs.yml`.
* **Format.** TOML, not YAML. The guard is standard-library-only by design (`REASON_REQUIRED` aside, its import set is `argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `tomllib`). CI runs it *before* `pip install`, which is only possible because it needs nothing from the environment. `tomllib` is already imported for `pyproject.toml`, so a TOML manifest preserves that property; a YAML manifest would break it. The step brief permitted an alternative name "justified by the repository structure", and this is that justification.
* **Schema.**
  * `schema-version = 1` — an integer the guard must recognise; bumping it is a deliberate act.
  * Zero or more `[[coverage]]` entries, each with `status`, `paths` (a non-empty list of patterns) and, for `excluded` and `unlicensed`, a non-empty `reason`.
* **Pattern syntax**, documented in the manifest header and pinned by tests:
  * `*` matches within one path segment (never `/`);
  * `**` spans separators;
  * a trailing `/` means "this directory and everything beneath it";
  * anything else matches literally.
* **Purpose stated in the file** so a reader who opens it without this audit still knows what it is for and how to change it.

## 6. Exact categories and scope

The vocabulary has five statuses. Four decide the treatment of a file; one removes a path from the review entirely.

| Status | Meaning | Count of patterns | Files matched at the final revision |
| --- | --- | --- | --- |
| `mit` | Software and machine-readable configuration, covered by `LICENSE`. Mirrors `LICENSE-DATA` §2. | 16 | 118 |
| `cc-by` | Repository-authored Markdown, covered by `LICENSE-DATA`. Mirrors `LICENSE-DATA` §1. | 4 | 42 |
| `excluded` | Governed by neither grant; a `reason` is required. | 2 | 2 |
| `unlicensed` | Deliberately undecided; a `reason` is required, and listed files are reported every run. | 0 (none today) | 0 |
| `not-distributed` | Generated, runtime or local-only material; not distributable content, not reviewed for licensing. | 14 | not walked |

Category contents:

* **`mit` (A).** `.gitignore`, `CITATION.cff`, `LICENSE`, `mkdocs.yml`, `pyproject.toml`, `licensing/**`, `.github/**`, `src/**`, `tests/**`, `scripts/**`, `configs/**`, `policies/**`, `schemas/**`, `labs/**.yaml`, `research/tables/*.csv`.
  `research/tables/*.csv` is written exactly as `LICENSE-DATA` §2 writes it, so a table placed in a new subdirectory is a decision rather than a default.
* **`cc-by` (B).** `README.md`, `docs/**.md`, `labs/**.md`, `research/**.md`.
* **`excluded` (C).**
  * `LICENSE-DATA` — the content-licence instrument itself. `LICENSE-DATA` §2 already places this file outside its own scope, and the legal code it embeds is Creative Commons' text dedicated to the public domain under CC0. The file nonetheless states the CC BY 4.0 grant for the material it describes.
  * `.freebuff/project-id` — tracked local tooling metadata. `LICENSE-DATA` §2 records it as neither project content nor third-party material. It is recorded here rather than deleted, so the decision is visible instead of accidental (this closes the ambiguity noted as residual 4 in `research/28`/`research/29` without deleting a file).
  * `LICENSE` is deliberately **not** here: it *is* the MIT grant text, and the MIT grant covers the software it accompanies.
* **`unlicensed` (D).** No entries today — every file has a decision. The status exists so that a future undecided file is *recorded* rather than silent, and an entry without a `reason` fails the check. The manifest documents how to add one.
* **`not-distributed` (E).** `runs/`, `traces/*.jsonl`, `site/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`, `**/__pycache__/`, `.venv/`, `venv/`, `build/`, `dist/`, `**/*.egg-info/`, `.env`, `*.local` — mirroring the "Lab runtime output", "Tooling", "Docs site build output" and "Local secrets" sections of `.gitignore`.

## 7. How tracked-file coverage is determined

`scripts/check_licensing.py` gained a walk, a matcher and three checks:

1. **Load and validate the manifest** (`manifest` check). Missing file, invalid TOML, unrecognised `schema-version`, unknown status, missing/empty `paths`, missing `reason` where required, unusable pattern, repeated pattern under one status, or one pattern under two statuses — each fails with a message naming the entry number and the reason.
2. **Walk the distributable content set.** Starting at the repository root, every file and directory is visited, sorted by name for determinism. Two things are skipped: the `.git` directory (never entered, never read) and anything matching a `not-distributed` pattern, including everything beneath a matching directory.
3. **Match every file against the four decision statuses** (`licence coverage` check). A file with **no** match is unaccounted for; a file with matches of **more than one** status is a conflict; a pattern that matched no file in this revision is stale. All three fail.
4. **Report undecided files** (`unlicensed files` check). Fails as part of (1) if an entry lacks a reason; otherwise prints every file recorded as deliberately undecided.

**Tracked set, and the deliberate superset.** The walk cannot read Git's index (that would mean `subprocess` or `.git` internals), so the guard uses the working tree. That set is a **superset** of the tracked set: it includes untracked-but-not-ignored files. This is the conservative direction and it is the point — a new file is caught *before* it is committed rather than in the next CI run.

**In CI the two sets coincide.** `actions/checkout` produces tracked files only, and the licensing step runs before `pip install`, so no build output or cache exists yet. The check therefore operates on exactly the tracked file set upstream, using a mechanism that is safe to run at any point locally.

**Ignored material is not inferred.** The `not-distributed` patterns are written out in the manifest; `.gitignore` is not parsed. The cost is that the two files are maintained in step by hand, and the failure mode of drift is safe (a new generated directory fails the check until it is recorded, rather than silently passing).

## 8. The six existing checks are unchanged

No check was weakened, relaxed, or removed. The guard's six declaration checks (`LICENSE`, `pyproject.toml`, `CITATION.cff`, `LICENSE-DATA`, `README.md`, third-party exclusion) run first, in the same order, with the same markers, the same failure messages and the same semantics. The report now continues with three further lines:

```
  ok    LICENSE                MIT licence text present
  ok    pyproject.toml         project.license.text = 'MIT'
  ok    CITATION.cff           license: MIT
  ok    LICENSE-DATA           CC BY 4.0 notice and complete legal code (8/8 sections)
  ok    README.md              MIT and CC BY 4.0 boundary documented
  ok    third-party exclusion  stated in LICENSE-DATA and README.md
  ok    manifest               licensing/manifest.toml: schema-version 1, 36 coverage entries
  ok    licence coverage       162 file(s) accounted for (mit 118, cc-by 42, excluded 2, unlicensed 0)
  ok    unlicensed files       none recorded; every file has a licence decision

Result: 9/9 checks passed
```

Four existing test assertions were updated **only** because the contract grew, not because it loosened: the expected report order (6 names → 9 names), the pass line (`6/6` → `9/9`), the permitted-import set (gained `re`), and the fixture repository (now also writes the manifest and the tracked local-state file, so the fixture still satisfies the whole contract). The offline/read-only assertion was **strengthened**: it now also forbids `ls-files`, `popen`, `.git/index` and `refs/heads`, and the byte-comparison drift test now covers the manifest as well.

## 9. False positives

* **A new untracked scratch file fails the check.** Disclosed and intentional: the guard sees the working tree, so `notes/scratch.md` fails until it is recorded — or deleted — before commit. The message names the path and the file to edit.
* **A new file under an existing directory is not inherited.** `research/notes/example.json` fails even though `research/**.md` exists: only `.md` under `research/` is covered by that pattern. This is the intended behaviour, demonstrated live in §10.
* **A stale pattern fails.** Deleting the last file a pattern covered fails the check until the pattern is removed or updated. Intended: the manifest is a record of live decisions.
* **`not-distributed` drift.** A new generated directory (say `runs-v2/`) fails the check until it is listed, because the manifest mirrors `.gitignore` by hand.
* **`.freebuff/` additions.** The manifest covers `.freebuff/project-id` only. A second local file under `.freebuff/` fails CI until it is recorded (usually under `not-distributed`). Intended, and noted in the manifest itself, because the directory is tracked.

## 10. False negatives

* **A wrong decision is not detected.** If `docs/naming.md` were recorded under `mit`, the check would pass. The guard can detect that a decision is *absent*; it cannot detect that a decision is *wrong*. Deciding provenance remains a human act. The manifest is small enough to review in full, which is the mitigation, not a solution.
* **The README's licensing table is prose.** It is checked for the presence of both licences and both licence file names, not for agreement with the manifest. `licensing/manifest.toml` is the machine-checked source of truth; the README table is the human-readable summary. A mismatch between the two would pass CI. Recorded as a new residual (§14).
* **Breadth of a pattern is a human choice.** `labs/**.md` covers every Markdown file under `labs/` at any depth — including one deliberately placed elsewhere. The pattern is written to match how the repository is actually organised, not to be adversarial.
* **Runtime output is not reviewed at all.** Anything under a `not-distributed` path is skipped, so the check says nothing about it. That is the documented meaning of the category.
* **Nothing is verified against the licence texts.** The manifest records scope; it does not verify that the CC BY 4.0 legal code is byte-identical (residual 11 in `research/29`, unchanged; the no-network rule prevents re-fetching it).
* **The boundary could still change silently.** Editing the `cc-by` patterns to add a path widens the content grant without touching `LICENSE-DATA`. The check would pass. The manifest is the mitigation: the change is one reviewable line.

## 11. Treatment of `research/`, `runs/`, `.freebuff/` and generated files

* **`research/`** — Markdown (`research/**.md`, 25 files including this audit) is CC BY 4.0 under `LICENSE-DATA` §1; the machine-readable tables (`research/tables/*.csv`, 13 files) are MIT under §2. A non-Markdown, non-`tables/*.csv` file anywhere under `research/` is unaccounted for and fails, demonstrated live below. Third-party titles, author names, venues, DOIs and quotations inside those Markdown files remain outside both grants; the manifest does not and cannot track quotations inside a file, and `LICENSE-DATA` §3 plus the README carry that exclusion separately.
* **`runs/`** — lab runtime output, git-ignored, listed as `not-distributed`. It is not distributable content and is not reviewed for licensing. `research/29` residual 8 (unlicensed traces under `runs/`) is unchanged by this step: if example traces are ever published, a data decision is needed, and publishing them would mean placing them outside the `not-distributed` set — at which point the check would force that decision.
* **`.freebuff/`** — `project-id` is tracked, so it is `excluded` rather than `not-distributed`: it does enter a clone, but `LICENSE-DATA` §2 records it as neither project content nor third-party material. Its licensing status is now an explicit recorded decision instead of an open question.
* **Generated material** — `site/` (MkDocs output), caches, bytecode, virtual environments, packaging output, `.env` and `*.local` are `not-distributed` and skipped. `site/` and `runs/` both existed on disk when the check was run and neither entered the coverage count, which is the observable evidence that the skip works.

**Live demonstration on the real repository** (probe files created and then removed; nothing left behind):

1. `research/99-coverage-probe.md` → **exit 0**, cc-by count up by one: covered by the deliberate `research/**.md` pattern, which is exactly the intended behaviour for a new research Markdown file.
2. `research/notes/coverage-probe.json` → **exit 1**, `1 file(s) have no recorded licensing treatment: research/notes/coverage-probe.json; add a [[coverage]] entry to licensing/manifest.toml`. Both the file and its directory were deleted afterwards and their absence was verified.

## 12. Files created and modified

| File | Change | Detail |
| --- | --- | --- |
| `licensing/manifest.toml` | **created** | 189 lines; schema version, five-status vocabulary, pattern syntax, 36 coverage entries, and a documented example of how to record an `unlicensed` file. |
| `scripts/check_licensing.py` | **modified** (untracked from Step 12) | 359 → 744 lines. Six declaration checks untouched; added the manifest loader/validator, the pattern compiler and matcher, the deterministic tree walk, the coverage evaluator, three new checks, and the extended failure footer. Still offline, deterministic, read-only, standard-library-only, and it never modifies a file. |
| `tests/test_licensing.py` | **modified** (untracked from Step 12) | 304 → 652 lines; 24 → 69 tests. Four assertions updated for the grown contract (§8); 45 new tests for the manifest and coverage. |
| `.github/workflows/ci.yml` | **modified** | Header comment now describes coverage (4 lines added); the existing step renamed from "Check the licence metadata" to **"Check the licence metadata and coverage"**. The job name `tests and lab self-check` is unchanged. Cumulative against `HEAD`: `+15/−1` (Step 12 contributed `+11/−1`). |
| `README.md` | **modified** | The `## Licensing` section gained a ten-line paragraph describing the manifest and the coverage rule; the verification-status row was renamed to "Licence metadata and file coverage" with **9/9 checks pass**; the `ci.yml` sentence now also names the no-recorded-treatment failure. Existing research-boundary language untouched. Cumulative against `HEAD`: `+64/−7` (Steps 9–13). |
| `pyproject.toml` | unchanged by this step | `license = { text = "MIT" }` as set in Step 10; cumulative `+1/−1`. |
| `LICENSE`, `LICENSE-DATA`, `CITATION.cff` | **unchanged** | No objectively demonstrated consistency problem required an edit, so their legal text was not touched. `LICENSE-DATA` remains the authoritative statement of the boundary. |

No automatic file modification was introduced. The guard writes nothing; every fix is a human edit to a declaration or to the manifest.

## 13. Test results

`PYTHONPATH=src py -m pytest tests/test_licensing.py` → **69 passed** (24 before this step; +45).

| Group | Tests | What it pins |
| --- | --- | --- |
| Real repository satisfies the contract | 2 | the nine report names in order; `9/9 checks passed`, no `FAIL` |
| Fixture passes; each declaration can fail independently | 16 | the six declaration checks still fail one at a time (unchanged from Step 12) |
| Accepted `pyproject.toml` spellings | 3 | unchanged |
| Guard is offline and read-only | 3 + 2 | import allowlist (now including `re`), forbidden calls, byte-comparison drift test (now covering the manifest), plus new: no `ls-files`/`popen`/`.git/index`/`refs/heads`, and the walk skips `.git` and `not-distributed` paths |
| **Coverage: manifest** | 18 | complete manifest passes; missing manifest; invalid TOML; unsupported `schema-version`; no entries; unknown status; empty `paths`; unusable patterns (6 cases); `excluded` and `unlicensed` entries must state a reason; identical pattern under two statuses |
| **Coverage: files** | 5 | the real manifest accounts for every file with no unaccounted, conflicting, stale or undecided entries; the fixture accounts for exactly 7 files in the expected category counts; a new unaccounted file fails and names the path; the same file passes once recorded; a new `.md` file is **not** licensed by its extension; an explicitly excluded file passes; removing the exclusion makes it fail; `not-distributed` paths are not reviewed |
| **Coverage: undecided** | 2 | an `unlicensed` entry without a reason is rejected; one with a reason passes and is named in the report |
| **Coverage: overlap and staleness** | 3 | a path claimed by two categories fails (`more than one category`); a stale pattern fails (`match no file`); a failing coverage run exits `1` and explains itself including the manifest path |
| Pattern semantics | 16 (parametrised) | `*` does not cross `/`, `**` does, a trailing `/` is a directory subtree, and a directory pattern does not match a longer sibling name |

Full suite: **764 passed** (10.4 s), up from 719. `719 + 45 = 764`; the two collection baselines used in Step 12 are unchanged by this step.

## 14. CI integration and verification gates

CI change: the coverage check runs inside the existing licensing guard — the same step, now `Check the licence metadata and coverage`, still placed after `Set up Python` and before `Install`, so it fails fast with no dependency install. **The job name `tests and lab self-check` is preserved**, since branch protection may reference it by name. `pytest` and `agentsec labs check` steps are untouched.

| Gate | Command | Result |
| --- | --- | --- |
| Test suite | `PYTHONPATH=src py -m pytest` | **764 passed**, exit 0 |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed**, exit 0 |
| Documentation build | `py -m mkdocs build --strict` | built with no warnings or errors, exit 0 |
| Existing licensing guard | `py scripts/check_licensing.py` | **9/9 checks passed**, exit 0 |
| New-file coverage guard | (same command) `licence coverage` + `manifest` + `unlicensed files` | 162 files accounted for (mit 118, cc-by 42, excluded 2, unlicensed 0); 36 coverage entries, 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| README links | 57 relative links, 3 in-page anchors | all resolve |

## 15. Research boundary

This step is licensing plumbing only. It performed no literature search, produced no research design or empirical study design, touched no learner data, drafted no paper text, and made no novelty claim. Phase 17 was not reopened. **E1 remains HOLD.**

The work says nothing about research validity, publication, educational effectiveness, causal learning effects, security effectiveness, model behaviour, benchmark validity or measurement validity. It verifies that every file in the repository has a recorded licensing treatment, and nothing else. It does not adjudicate provenance or ownership, and it does not determine the licence of any third-party material — a limit `README.md` and the guard's own docstring both state.

Research records `research/20`–`research/29` were read and left unmodified; this audit is a new record at `research/30`, not an edit of an earlier one. Two research-adjacent actions are the only ones that changed anything: adding a manifest entry for `research/` Markdown (already CC BY 4.0 under `LICENSE-DATA` §1) and recording `.freebuff/project-id` as outside both grants. Neither changes what any research file says or is licensed as.

## 16. Git safety

* Nothing staged: `git diff --cached --name-only` is empty.
* Nothing committed: `HEAD` is still `995cf68` "Research finding complete".
* Nothing pushed. No tag, no release, no `date-released` added to `CITATION.cff`.
* No `add`, `commit`, `push`, `reset`, `clean`, `checkout`, `rebase`, `amend`, `stash` or `rm` of tracked files was run.
* The only files written are the deliveries listed in §12, all of them unstaged and untracked.
* The two probe files used for the live demonstrations in §11 were created and deleted inside this step, and their absence was verified.
* Git's `LF will be replaced by CRLF` messages are the pre-existing `autocrlf` behaviour of this checkout, not a change made here.
* `LICENSE`, `LICENSE-DATA` and `CITATION.cff` were not modified. `mkdocs.yml` was not modified.

Final status:

```
 M .github/workflows/ci.yml
 M README.md
 M pyproject.toml
?? CITATION.cff
?? LICENSE
?? LICENSE-DATA
?? licensing/
?? research/28-content-licensing-audit.md
?? research/29-licence-ci-guard-audit.md
?? scripts/check_licensing.py
?? tests/test_licensing.py
```

The owner commits and pushes when they choose; this step leaves the tree for them to review.

## 17. Remaining licensing residuals

Carried forward from `research/29` §16, with this step's effect noted.

**Narrowed by this step**

10. **The guard cannot see a new, wrongly-scoped file.** → **Closed for silent omission.** A new file now fails the check until a human records it. The narrower residual that remains: the guard detects a *missing* decision, not a *wrong* one (§10), and the README licensing table can still drift from the manifest (§10).
4. **`.freebuff/project-id` is covered by neither grant and still not deleted.** → **Now an explicit recorded decision** (`excluded`, with a reason) rather than an unaddressed ambiguity. The file is still tracked.

**New in this step**

14. **Manifest/README/`.gitignore` drift is possible.** The README table is prose and `.gitignore` is not parsed, so a new generated directory or a widened content pattern can be recorded in one place and not the others. The failure mode is safe (over-strict), but the three descriptions are maintained by hand.
15. **The working-tree walk is a superset of the tracked set locally.** Intentional (§7), but it means a local helper file fails CI until recorded. Running the guard with `--root` pointed at a clean export would show the tracked-only view.
16. **`licensing/` is not declared as packaged data.** `pyproject.toml` has no `license-files` entry, so the manifest lives in the repository and CI but is not part of a built distribution. Consistent with residual 5 (no SPDX identifiers); unchanged in scope.

**Unchanged from Steps 11–12**

1. `LICENSE`'s MIT text refers to "this software and associated documentation files", which overlaps the CC BY grant. The guard still does not resolve this; it requires the declarations to stay mutually consistent. Strict exclusivity remains the owner's call.
2. CC BY 4.0 was adopted from documented intent, not an explicit decision; a switch would mean editing `LICENSE-DATA`, one README table row, the manifest's `cc-by` status naming, and the guard's markers in the same commit.
3. The adopted content scope is narrower than the older planning records describe ("data/docs/documents").
5. No SPDX identifiers anywhere.
6. `research/27` still describes the pre-Step-10 state, deliberately unmodified.
7. No release or tag, so `CITATION.cff` still has no `date-released`.
8. Traces under `runs/` remain git-ignored and unlicensed.
9. `pyproject.toml`'s `description` still ends "(Phase A skeleton)" — stale, out of scope.
11. The CC BY 4.0 legal code is no longer byte-verified on every run; the one-off check performed in Step 11 covered the embedded legal-code text only, and is not repeated offline.
12. No pre-commit hook; the guard runs in CI only.
13. The guard's markers are English phrasing, and the manifest patterns are literal paths; both require the corresponding declaration to be updated in the same commit.

## 18. Conclusion

The licensing boundary is now **complete as well as consistent**. Before this step the repository could prove that its declarations agreed with each other; it could not prove that it had a decision for every file. Now `licensing/manifest.toml` records the treatment of every path, and `scripts/check_licensing.py` fails — with a message naming the file and the file to edit — when a file has no recorded treatment, when two categories claim the same path, when a recorded pattern matches nothing, or when a file is recorded as excluded or undecided without a reason.

The mechanism is deliberately un-clever: explicit patterns, no inference from extension or location, no Git internals, no network, no writes, standard library only. The boundary it enforces is the one the repository already documented — MIT for software and machine-readable configuration, CC BY 4.0 for repository-authored Markdown, third-party material outside both grants — and it neither widened nor narrowed it.

**What this step does not establish:** that any decision recorded in the manifest is correct; that the README table and the manifest agree; that any third-party material has been identified or licensed; or anything about research novelty, publication, educational effectiveness, security effectiveness, benchmark validity or measurement validity. It makes licensing coverage explicit and checkable, and nothing else.
