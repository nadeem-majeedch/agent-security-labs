# PHASE 20 — STEP 15: POST-COMMIT RELEASE RE-AUDIT (v0.0.1)

**Nature of this step:** a **read-only** post-commit audit. Nothing was modified, staged, committed, pushed, tagged or released. No reset, checkout, clean, rebase or amend was run. `HEAD` is unchanged by this step. The only file created is this record, `research/32-post-commit-release-readiness.md`.

**Previous blocker B1 — RESOLVED.**
**Final evidence-based classification: READY WITH WARNINGS** — zero blockers; twelve warnings, each conscious-acceptance or pre-tag cleanup; no new blocker was invented.

Phase 17 remains **CLOSED**. **E1 remains HOLD.** No literature search, paper draft, empirical-study design, learner data, or novelty/effectiveness/publication/benchmark/security-effectiveness claim is made here.

---

## 1. Starting state

Recorded from Git before any other action; nothing was assumed from the previous step's report.

| Item | Value |
| --- | --- |
| `HEAD` | `54a5e611cd1d0998f5fe4c06d8107f508f04d5a9` (`54a5e61`) |
| Branch | `main` |
| Latest commit | `54a5e61 final release` — Dr. Muhammad Nadeem Majeed `<98729698+nadeem-majeedch@users.noreply.github.com>`, 2026-09-29 11:05:58 +0500 |
| Commit message | subject `final release`; body empty (§2) |
| Parent | `995cf68` "Research finding complete" |
| Tags | **0** (`git tag -l | wc -l`) |
| Tracked files at HEAD | **163** (`git ls-tree -r --name-only HEAD | wc -l`) |
| `git status --porcelain` | **empty** |
| `git diff --name-only` | **empty** |
| `git diff --cached --name-only` | **empty** |
| Working tree vs HEAD | **0 differing tracked files; 0 untracked non-ignored files** |
| Working tree clean? | **YES** — clean and identical to HEAD |

```
$ git status --porcelain
$ git diff --name-only
$ git diff --cached --name-only
(no output for all three)
```

**Attribution note used throughout this audit.** Every gate in §13 was executed with `py` in the working tree, not inside a Git object store. Because `git diff --name-only HEAD` returns nothing and `git ls-files -o --exclude-standard` returns nothing, the working tree is byte-identical to revision `54a5e61`, so those results are attributable to that commit. Where a claim specifically concerns what is *in the commit*, it is made from `git show HEAD:<path>`, `git grep HEAD --` or `git cat-file`, and is marked as HEAD-verified.

## 2. Commit verification

`git diff --name-status 995cf68 54a5e61` — 13 files, `+3602 / −9`:

| Status | Path |
| --- | --- |
| A | `CITATION.cff` |
| A | `LICENSE` |
| A | `LICENSE-DATA` |
| A | `licensing/manifest.toml` |
| A | `scripts/check_licensing.py` |
| A | `tests/test_licensing.py` |
| A | `research/28-content-licensing-audit.md` |
| A | `research/29-licence-ci-guard-audit.md` |
| A | `research/30-new-file-licensing-coverage-audit.md` |
| A | `research/31-final-release-readiness-audit.md` |
| M | `.github/workflows/ci.yml` |
| M | `README.md` |
| M | `pyproject.toml` |

This is exactly the release-preparation set: the four licensing instruments, the manifest, the coverage guard and its tests, the four audit records, and the three modified files (`README`, `pyproject`, CI). No file outside that set was touched — no source, lab, policy, schema, scenario, config or MkDocs change is present in the diff.

The commit message is the two-word subject `final release` with an empty body. That is a release-hygiene observation only: no gate depends on it, and it is recorded in §17 for completeness rather than as a finding.

**HEAD-verified:** the commit's content matches what `research/31` §14 classified as intended distributable content, and the previously untracked 10 paths are now tracked.

## 3. B1 resolution evidence

`research/31` §15 defined B1 as: *the release content was uncommitted, and `HEAD` contradicted the intended licensing state* — `license = { text = "TBD" }`, a README stating no licence existed, and all six licensing deliverables absent from the revision.

**Requirement 1 — the files exist at HEAD.** `git cat-file -e HEAD:<path>` for every required release file (HEAD-verified):

| Path | `git cat-file -e` | Size at HEAD |
| --- | --- | --- |
| `LICENSE` | PRESENT | 1,083 bytes |
| `LICENSE-DATA` | PRESENT | 24,031 bytes |
| `CITATION.cff` | PRESENT | 1,142 bytes |
| `licensing/manifest.toml` | PRESENT | 7,064 bytes |
| `scripts/check_licensing.py` | PRESENT | 26,395 bytes |
| `tests/test_licensing.py` | PRESENT | 21,918 bytes |
| `README.md` | PRESENT | 18,629 bytes |
| `pyproject.toml` | PRESENT | 962 bytes |
| `.github/workflows/ci.yml` | PRESENT | 1,738 bytes |
| `research/28` … `research/31` | PRESENT | committed in the same commit |

**Requirement 2 — the old statements are gone from HEAD.** `git grep -F <pattern> HEAD -- README.md pyproject.toml CITATION.cff`:

| Pattern | Result at HEAD |
| --- | --- |
| `text = "TBD"` | **absent** |
| `No licence has been assigned yet` | **absent** |
| `no \`LICENSE\` or \`CITATION.cff\` file exists yet` | **absent** |
| `TBD` (any occurrence) | **absent** |

**Requirement 3 — the replacement statements are in place at HEAD.**

* `HEAD:pyproject.toml:11` → `license = { text = "MIT" }`
* `HEAD:README.md:279` → "**Licences: MIT for the software, CC BY 4.0 for the content.** The same software licence is declared in [`pyproject.toml`](pyproject.toml) and [`CITATION.cff`](CITATION.cff)."
* `HEAD:README.md` contains a full `## Licensing` section with the three-row boundary table, the attribution guidance and the third-party exclusion.
* `HEAD:LICENSE:1` → `MIT License`; `HEAD:LICENSE:3` → `Copyright (c) 2026 Dr. Muhammad Nadeem Majeed`.
* `HEAD:LICENSE-DATA` → repository notice with sections 1 (Scope), 2 (Exclusions) and 3 (Third-party material) followed by the CC BY 4.0 legal code (24,031 bytes).
* `HEAD:CITATION.cff` → CFF `1.2.0`, `type: software`, `license: MIT`, `version: "0.0.1"`, repository code and documentation URL.
* `HEAD:licensing/manifest.toml:55` → `schema-version = 1`, with `[[coverage]]` entries for `mit`, `cc-by`, two `excluded` and `not-distributed`.

### B1: **RESOLVED**

The resolution test set out in `research/31` is met in full, verified from the commit rather than from the working tree: the release revision now contains every licensing deliverable, declares MIT in its packaged metadata, and its README no longer states that no licence exists. No part of B1 remains.

## 4. Version consistency

| Location | Value | HEAD-verified |
| --- | --- | --- |
| `pyproject.toml` `[project] version` | `0.0.1` | yes |
| `CITATION.cff` `version` | `"0.0.1"` | yes |
| `src/agentsec/__init__.py` `__version__` (line 56) | `"0.0.1"` | yes |
| `README.md` citation block (line 333) | "version 0.0.1" | yes |
| Installed package metadata (editable) | `Version: 0.0.1` | working tree |
| `CITATION.cff` `date-released` | **absent** | yes |

**Result: PASS.** All four declarations agree on `0.0.1`; no location contradicts another, and no file was modified to check this.

Two version-adjacent gaps remain as warnings, unchanged from `research/31`: `CITATION.cff` still has no `date-released` (W6), and nothing in the test suite or scripts ties `pyproject.toml`'s version to `__version__` or to `CITATION.cff` — `tests/labs/test_lab00.py` only asserts that `__version__` is a non-empty string (W8).

## 5. Licensing verification

`py scripts/check_licensing.py` → exit **0**:

```
  ok    LICENSE                MIT licence text present
  ok    pyproject.toml         project.license.text = 'MIT'
  ok    CITATION.cff           license: MIT
  ok    LICENSE-DATA           CC BY 4.0 notice and complete legal code (8/8 sections)
  ok    README.md              MIT and CC BY 4.0 boundary documented
  ok    third-party exclusion  stated in LICENSE-DATA and README.md
  ok    manifest               licensing/manifest.toml: schema-version 1, 36 coverage entries
  ok    licence coverage       163 file(s) accounted for (mit 118, cc-by 43, excluded 2, unlicensed 0)
  ok    unlicensed files       none recorded; every file has a licence decision

Result: 9/9 checks passed
```

All six declaration checks behave exactly as they did at Step 12, and the three coverage checks pass. The committed guard is the same 744-line script audited in `research/31`; no check was weakened or reordered.

## 6. Coverage verification

| Metric | Value |
| --- | --- |
| Commit with manifest + guard | `54a5e61` |
| Coverage entries | 36 |
| Files accounted for (before this audit) | **163** — equal to the 163 tracked files at HEAD |
| MIT | 118 |
| CC BY 4.0 | 43 |
| Excluded (outside both grants) | 2 (`LICENSE-DATA`, `.freebuff/project-id`) |
| Unlicensed | **0** |
| Unaccounted | **0** |
| Conflicts | **0** |
| Stale patterns | **0** |
| Undecided | **0** |

The count matches `research/31` §5 exactly (163 / 118 / 43 / 2 / 0), and it now coincides with the tracked-file count because the audit records that were previously untracked are committed. After this audit exists the walk reports **164** files (`cc-by 44`); the audit is matched by the manifest's `research/**.md` pattern, verified in §14.

## 7. Package audit

| Item | HEAD / working-tree observation | Verdict |
| --- | --- | --- |
| Package name / version | `agentsec` / `0.0.1` | PASS |
| `requires-python` | `>=3.11` | PASS |
| Entry point | `agentsec = "agentsec.cli:main"` — `agentsec --help` works | PASS |
| Module entry | `py -m agentsec --help` — `run`, `evaluate`, `inspect`, `labs` | PASS |
| Importability | `import agentsec` → `0.0.1` from `src/agentsec/__init__.py` | PASS |
| Runtime dependencies | `pydantic>=2.6`, `jsonschema>=4.20`, `PyYAML>=6.0` — exactly the three third-party modules imported across `src/` | PASS |
| Dev-only dependency leakage | none — `pytest` is confined to the `dev` extra | PASS |
| Optional extras | `dev`, `live` (`httpx`, unused by `src/`), `docs` (`mkdocs-material>=9`, unpinned) | PASS with W11 |
| Package data | **none declared**; schema lives in `schemas/trace/`, not inside `src/agentsec/` | W5 |
| `[project]` `authors` / `classifiers` / `urls` | absent | W10 |
| `license` form | `{ text = "MIT" }` — legacy form (PEP 639 prefers an SPDX string + `license-files`) | W10 |
| Debug leftovers / TODO markers | none | PASS |
| Build attempt | not made — `setuptools` is unavailable in the active interpreter, so no wheel or sdist was produced (recording, not a finding) | — |

## 8. Self-containment finding

**Condition re-tested, still present. Classification: WARNING (unchanged).**

Method (writes only to a temporary directory outside the repository; the repository was not written to):

```
shutil.copytree("src/agentsec", <tmp>/agentsec)
sys.path.insert(0, <tmp>); importlib.import_module("agentsec.trace.validate")
```

Result:

```
schema_path() raised: FileNotFoundError could not locate
schemas/trace/trace_event.v1.schema.json above <tmp>\agentsec\trace\validate.py
```

Supporting evidence: `pyproject.toml` declares no `package-data`, `include-package-data`, `license-files` or `urls`; `schemas/trace/trace_event.v1.schema.json` exists only in the repository's `schemas/` directory; `find src/agentsec -name "*.schema.json"` returns nothing, so the schema is not inside the package. `trace/validate.schema_path()` resolves it by walking up from `__file__`.

**Why WARNING and not BLOCKER, on evidence.** The release being audited is a tagged source release of the repository (README documents `pip install -e ".[dev]"` from the repository root and all documented commands run from that root; the release identity in `CITATION.cff` is `repository-code` plus a documentation `url`, with no index or distribution URL). In that layout the schema is present and every gate passes. The defect only manifests if the package is installed outside the repository, as from a wheel or sdist on an index. No documented workflow depends on that, so nothing in the release is broken by it — but an installed-package consumer would hit a `FileNotFoundError`, so it must be consciously accepted.

## 9. Stale metadata finding

**Still present at HEAD. Classification: WARNING (unchanged) — not a blocker, not merely informational.**

`git grep` at HEAD (HEAD-verified):

| Path | Line | Text |
| --- | --- | --- |
| `pyproject.toml` | 8 | `description = "AI Agent Security Lab - educational, reproducible agent-security infrastructure (Phase A skeleton)."` |
| `docs/development.md` | 1 | `# AgentSec Lab - development notes (Phase A)` |
| `src/agentsec/__init__.py` | 3 | `Phase A: core data models, trace schema/validation/recording, redaction, a` |
| `src/agentsec/__init__.py` | 7 | `scenario layer. Deliberately no real model adapters or lab material yet (see` |

The `pyproject.toml` string becomes the packaged `Summary`; `docs/development.md` is the package's `readme` target, so its H1 ships as the long description; and the module docstring ships inside the package while stating that there is no "lab material yet" — which is false for an artefact containing the eight labs.

The reasoning that keeps this a warning is unchanged from `research/31` §16, and was re-checked rather than restated: no gate fails because of it (764 tests, 8/8 labs, MkDocs strict exit 0, licensing 9/9 all pass with the strings in place), it does not affect installability, the entry point, the declared licence, the dependency set or the labs, and the error direction is *understatement* rather than a false claim of achievement. It is not "merely informational" because it is user-visible in packaged metadata and contradicts the README.

## 10. Repository hygiene

Tracked-versus-ignored, resolved per path (`git ls-files --error-unmatch` and `git check-ignore`):

| Path | State | Class |
| --- | --- | --- |
| `.freebuff/project-id` | **TRACKED** | B (distributed) — W7 |
| `runs/` (8 traces) | ignored, untracked | A (runtime data) |
| `site/` (62 files) | ignored, untracked | A (docs build output) |
| `.pytest_cache/` | ignored, untracked | A (test cache) |
| `src/agentsec.egg-info/` | ignored, untracked | A (editable-install metadata) |
| 22 × `__pycache__/` | ignored, untracked | A (bytecode) |

* **No tracked file matches any cache or build-artefact pattern** — `git ls-files | grep -E "__pycache__|\.pyc$|\.egg-info|/site/|^runs/|\.pytest_cache|\.env$|\.local$"` returns nothing.
* **No editor or OS artefacts** (`*.swp`, `*.orig`, `*~`, `.DS_Store`, `Thumbs.db`, `*.bak`, `*.tmp`) anywhere in the tree.
* **No `build/` or `dist/` directory.** No tracked generated runtime data. `schemas/trace/trace_event.v1.schema.json` remains the one intentionally tracked generated file, drift-tested by `tests/schema/test_schema_file.py`.
* **Secrets scan over the tracked tree** (`git grep` for API-key, bearer, private-key, `ghp_`, `AKIA…` patterns): every hit is a synthetic or educational reference — the redaction pattern table in `src/agentsec/trace/redact.py`, the lab redaction tests, and prose in `labs/LAB-07-data-leakage/README.md` about redacting secret-shaped values. **No credential, token or key is present.**
* **No private filesystem paths** in repository content; the only personal name is the intentional copyright holder in `LICENSE`, `LICENSE-DATA` and `CITATION.cff`.
* **Nothing was deleted or moved.**

No category-C (hygiene blocker) finding. The only tracked local-tooling file is `.freebuff/project-id` (W7), whose licensing status is explicitly recorded as outside both grants.

## 11. CI audit

`git show HEAD:.github/workflows/ci.yml` (HEAD-verified; also re-parsed as YAML — valid):

| Position | Step |
| --- | --- |
| 1 | Check out the repository |
| 2 | Set up Python 3.11 |
| 3 | **Check the licence metadata and coverage** → `python scripts/check_licensing.py` |
| 4 | Install the package (with dev extras) → `pip install -e ".[dev]"` |
| 5 | Run the test suite → `python -m pytest` |
| 6 | Run the lab self-check → `agentsec labs check` |

| Check | Result |
| --- | --- |
| Licensing check exists | PASS — committed with its header comment describing both the declaration and the coverage checks |
| Coverage check exists | PASS — same step; it is part of `check_licensing.py` and reports `manifest`, `licence coverage` and `unlicensed files` |
| Licensing before `pip install` | PASS — step 3 of 6 |
| Tests remain present | PASS |
| Labs check remains present | PASS |
| Job display name unchanged | PASS — still `tests and lab self-check` (`jobs.checks.name`) |
| Network requirement introduced into the guard | PASS — none: the guard imports only `argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `tomllib` |
| Secrets required | PASS — no `secrets.` context anywhere; the only expression is `steps.deployment.outputs.page_url` in `docs.yml` |
| Commands match the repository | PASS — all three commands exist and were run successfully in §13 |
| Commands altered in this step | none |

`docs.yml` (build strictly + deploy to Pages) is unchanged and was not modified by the commit.

## 12. README audit

Checked from `HEAD:README.md` (HEAD-verified) with link targets resolved on disk:

| Check | Result |
| --- | --- |
| Relative links | **57 / 57 resolve; 0 broken** |
| In-page anchors | **3 / 3 resolve** (`#licensing`, `#verification-status` ×2) |
| Licensing description matches HEAD | PASS — `## Licensing` states MIT for software and machine-readable configuration, CC BY 4.0 for repository-authored Markdown, third-party material under neither grant, and names `LICENSE` and `LICENSE-DATA`; `## Repository status` states "Licences: MIT for the software, CC BY 4.0 for the content" |
| Version reference | PASS — the citation block reads "version 0.0.1" |
| Documentation URL | PASS — `https://nadeem-majeedch.github.io/agent-security-labs/`, identical to `CITATION.cff` `url` |
| Repository URL | PASS — matches `CITATION.cff` `repository-code` |
| Describes an unimplemented / planned artefact? | **NO** — `git grep` at HEAD for `planned`, `not started`, `not yet implemented`, `will be implemented`, `TBD`, `placeholder`, `skeleton` returns **nothing** in `README.md` |
| Positive status statement | PASS — `HEAD:README.md:33` "**Current status:** an existing, working artefact — not a plan." |
| False research claims | none — `## What this project does **not** claim` disclaims novelty, security effectiveness and any claim about real model behaviour |

## 13. Verification gates

All four gates were run against revision `54a5e61` (working tree identical to HEAD, §1):

| Gate | Command | Actual result |
| --- | --- | --- |
| Tests | `PYTHONPATH=src py -m pytest` | **764 passed**, 0 failed, 0 errors, 0 skipped, 11.2 s, exit 0 |
| Labs | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed** (LAB-00 … LAB-07 all `PASS`), exit 0 |
| Docs | `py -m mkdocs build --strict` | **exit 0**; 0 `WARNING -`/`ERROR -` lines; 16 pages; navigation resolves |
| Licensing | `py scripts/check_licensing.py` | **9/9 checks passed**, exit 0; coverage 163 files, 0 unaccounted / 0 conflicts / 0 stale / 0 undecided |

Measured, not assumed. The counts match the `research/31` baseline exactly (764 tests, 8/8, strict exit 0, 9/9), so the commit introduced no behavioural change: the same tree passed before and after being committed. The only non-gate output is the Material for MkDocs theme's upstream advisory banner about MkDocs 2.0 (W11), which is not a build diagnostic.

Environment note (recording, not a finding): local verification ran on Python 3.13.14, while both workflows pin Python 3.11; `requires-python = ">=3.11"` covers both. No CI run was observed in this audit (offline).

## 14. Research-boundary verification

| Requirement | Evidence | Result |
| --- | --- | --- |
| Phase 17 remains CLOSED | `HEAD:docs/development.md:23` "## Research status (Phase 17 — CLOSED, research NO-GO)"; line 27 "The Phase 17 research transition is **CLOSED**" | PASS |
| E1 remains HOLD | E1 classifications and the held publication gate are recorded in the research records (`research/24`, `research/25`, `research/26`: E1 = HIGH-RISK / INSUFFICIENTLY DISTINCT; publication gate = HOLD), carried forward by `research/28`–`research/31` | PASS |
| No empirical evidence claimed | no gate, README or documentation statement asserts a measured effect | PASS |
| No novelty claim introduced | `git grep` over `README.md`, `docs`, `labs`, `src`, `scripts`, `schemas`, `policies`, `configs` for overclaim phrases returns only **disclaimers** ("does **not** claim **security effectiveness**") and pedagogical questions ("What event proves that a tool was actually executed?") | PASS |
| No security-effectiveness claim | README `## What this project does **not** claim` disclaims it explicitly | PASS |
| No benchmark claim | README and `docs/development.md` state the labs are "not a benchmark"; `ci.yml`'s comment says the self-check is "not a benchmark or a security measurement" | PASS |
| No paper drafted | no manuscript, article or submission artefact exists in the repository | PASS |
| No learner data | `git ls-files` matched against learner/student/participant/survey/assessment patterns returns **nothing** | PASS |
| No research direction reopened | this step created no research record and changed no research conclusion; the commit's research changes are the four new audit records (`research/28`–`research/31`) | PASS |
| Prior records unaltered | the commit's diff contains **no modification** to any pre-existing research file — only additions of `research/28`–`research/31` | PASS |

`research/31` was committed unchanged by this step and its findings are carried forward rather than restated.

## 15. Blockers

**None.**

B1 (uncommitted release content; `HEAD` declaring `license = { text = "TBD" }`) is **RESOLVED** on HEAD-verified evidence (§3). No new blocker was found in any audited area: no gate fails, no tracked secret or private path exists, no ignored material is tracked, no tracked build artefact or cache exists, CI performs the licensing guard before installation with the job name preserved, the README is accurate and fully linked, and the research boundary is intact.

## 16. Warnings

Classification: release is technically possible; each item should be consciously accepted or cleaned up before tagging. None blocks.

| # | Warning | Status |
| --- | --- | --- |
| W2 | `pyproject.toml:8` description ends "(Phase A skeleton)"; becomes the packaged `Summary` | present (§9) |
| W2b | `src/agentsec/__init__.py:3,7` — "Phase A"; "Deliberately no real model adapters or **lab material yet**" (false: eight labs exist); ships inside the package | present (§9) |
| W3/W4 | `docs/development.md:1` H1 "(Phase A)"; the file is the package `readme` target | present (§9) |
| W5 | Package is not self-contained: no package data; `schema_path()` raises `FileNotFoundError` outside the repository | reproduced (§8) |
| W6 | `CITATION.cff` has no `date-released` | absent at HEAD (§4) |
| W7 | `.freebuff/project-id` is tracked, so local tooling metadata is distributed; recorded in the manifest as outside both grants | present (§10) |
| W8 | No version-drift guard across `pyproject.toml`, `__version__` and `CITATION.cff` | present (§4) |
| W9 | The local editable install still reports stale metadata (`License: TBD`) because it predates the Step 10 change; git-ignored, so it does not reach the release | present |
| W10 | Legacy `license = { text = "MIT" }` form; no `authors`, `classifiers`, `keywords` or `urls`; no SPDX identifiers | present (§7) |
| W11 | `docs` extra unpinned (`mkdocs-material>=9`); upstream advisory that MkDocs 2.0 breaks themes, plugins and overrides | present (§13) |
| W12 | Human-judgement licensing residuals carried from `research/28`–`research/31` (MIT "associated documentation files" overlap with CC BY; the guard detects a missing decision, not a wrong one; the README prose table can drift from the checked manifest) | carried |
| W13 | `traces/*.jsonl` is listed in `.gitignore` and the manifest but the `traces/` directory does not exist | present |

Warning set is unchanged from `research/31`; the commit neither fixed nor worsened any of them, and no warning was added for the opportunity to do so.

## 17. Informational findings

**I1** The release commit's message is the bare subject `final release` with an empty body, so `git log` carries no record of what the commit contains or why. Cosmetic; `git show --stat` recovers the content.
**I2** Zero `TODO`/`FIXME`/`XXX`/`HACK` markers in any tracked source file.
**I3** Zero skips, xfails, failures, errors or meaningful warnings across 764 tests.
**I4** `site/`, `runs/`, `.pytest_cache/`, 22 `__pycache__/` trees and `src/agentsec.egg-info/` exist on disk, all correctly ignored and untracked.
**I5** No tags and no GitHub release exist, so there is no stale release metadata to correct and no release artefact to withdraw.
**I6** The built documentation site contains no local or absolute URLs; `localhost`/`file://` strings occur only inside the vendored Material JavaScript source map.
**I7** Local verification ran on Python 3.13.14 while CI pins 3.11; `requires-python = ">=3.11"` covers both, and no CI run was observed in this offline audit.
**I8** `setuptools` is unavailable in the active interpreter, so no wheel or sdist was built during the audit; `pyproject.toml` was read as the authoritative metadata source.
**I9** `research/31` is now committed, so the pre-commit audit and this post-commit re-audit sit alongside each other in the history as the before/after record of B1.

## 18. Verification gates after this audit, and final classification

After creating `research/32-post-commit-release-readiness.md`, all four gates were re-run:

| Gate | Result |
| --- | --- |
| `PYTHONPATH=src py -m pytest` | **764 passed**, exit 0 |
| `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed**, exit 0 |
| `py -m mkdocs build --strict` | **exit 0**, 0 warnings, 0 errors |
| `py scripts/check_licensing.py` | **9/9 checks passed**, exit 0 |

Manifest coverage of the new audit, checked directly against the guard's own functions:

```
research/32-post-commit-release-readiness.md -> [('cc-by', 'research/**.md')]
files: 164 {'mit': 118, 'cc-by': 44, 'excluded': 2, 'unlicensed': 0}
unaccounted: [] | conflicts: [] | stale: [] | undecided: []
```

The new audit is accounted for (CC BY 4.0 by the deliberate `research/**.md` pattern), with **no unaccounted files, no stale patterns, no conflicts and no undecided files**. The audit itself is the only new file in the working tree, and it is untracked — which the coverage check now counts, as designed, and which is precisely the B1 condition that the owner resolved by committing the previous set.

### Final release classification

# READY WITH WARNINGS

**Determination, from evidence only:**

1. **B1 is RESOLVED** (§3): every required release file exists at HEAD, `HEAD` declares MIT, and the README no longer states that no licence exists. No blocker remains (§15).
2. **Every gate passes at the committed revision** (§13): 764/764 tests, 8/8 labs, MkDocs strict exit 0 with zero warnings and zero errors, and 9/9 licensing checks with 164/164 files accounted for and 0 unaccounted, 0 conflicts, 0 stale, 0 undecided (§18).
3. **The repository is clean and matches HEAD** (§1): no modified tracked file, no staged file, no untracked non-ignored file before this audit was written.
4. **The twelve warnings in §16** are all conscious-acceptance or pre-tag cleanup items, none of which prevents a v0.0.1 release: stale descriptive metadata (W2–W4), an installed-package self-containment gap that the documented repository-root workflow does not exercise (W5), a missing CFF `date-released` that is normally added at release time (W6), a tracked local-tooling file whose licensing status is explicitly recorded (W7), missing automation for version drift (W8), stale local environment metadata (W9), legacy packaging metadata (W10), an unpinned docs extra against a future upstream major (W11), human-judgement licensing residuals (W12), and a manifest entry for a directory that does not exist (W13).

No blocker was invented to justify withholding the release, and no warning was dismissed to justify granting it. The classification follows from B1's resolution plus the passing gates; the warnings are recorded so they are accepted knowingly rather than by default.

## 19. Statement: no release operation was performed

In this step:

* **no** tag was created (`git tag -l` → 0, unchanged);
* **no** GitHub release was created;
* **nothing** was staged (`git diff --cached --name-only` empty both before and after);
* **nothing** was committed — `HEAD` remains `54a5e611cd1d0998f5fe4c06d8107f508f04d5a9`;
* **nothing** was pushed;
* no `reset`, `checkout`, `clean`, `rebase`, `amend` or `stash` was run;
* **no** source, lab, test, policy, schema, scenario, CI, documentation, licensing, manifest or previously committed research file was modified;
* `LICENSE` and `LICENSE-DATA` were read from Git but not altered in any way;
* the only file created is `research/32-post-commit-release-readiness.md`;
* the only writes performed were inside temporary directories outside the repository (the package copy for the §8 demonstration, deleted by its context manager).

**This audit stops here. It does not create the v0.0.1 release, and it makes no commitment to do so.**

---

*End of Phase 20 — Step 15. Post-commit re-audit complete; B1 RESOLVED; classification READY WITH WARNINGS; no staging, commit, push, tag or release was performed.*
