# PHASE 20 — STEP 14: FINAL RELEASE-READINESS AUDIT (v0.0.1)

**Nature of this step:** a **read-only** audit. No file was created, modified or deleted except this audit record (`research/31-final-release-readiness-audit.md`). No stage, commit, push, tag, GitHub release, reset, checkout, clean, rebase or amend was performed, and `HEAD` is unchanged.

**Final evidence-based status: NOT READY** — determined by one BLOCKER (§14, B1): the release content is uncommitted, and `HEAD` itself declares `license = { text = "TBD" }` with no licence files. Once the pending work is committed, the status implied by the remaining findings is **READY WITH WARNINGS**; no WARNING alone is a blocker (§15).

Phase 17 remains **CLOSED**. **E1 remains HOLD.** No literature search, research direction, paper draft, empirical study design or novelty/effectiveness/publication/benchmark/security-effectiveness claim is made here.

---

## 1. Starting state

Recorded before any other action, from the working tree as found.

| Item | Value |
| --- | --- |
| `HEAD` | `995cf6876d0a103968204c5b9be59371d564ae4f` — `995cf68` "Research finding complete" (2026-09-29 06:56:59 +0500) |
| Branch | `main` |
| Working tree | **dirty** — 3 modified, 10 untracked paths |
| Staged | **nothing** (`git diff --cached --name-only` empty) |
| Recent commits | `995cf68` Research finding complete · `6802c81` PHASE 19 — STEP 2 PASS Github deployment Ready · `5f7d2ae` Add GitHub Pages documentation site · `0ed62a7` Complete Phase 18 lab education and self-check · `d095d06` phase 16 step 5 repot finalize |
| Tags | **0** (`git tag -l | wc -l`) |
| Repository version | `0.0.1` (`pyproject.toml` `[project] version`; `src/agentsec/__init__.py.__version__`; `CITATION.cff` `version`) |
| Python requirement | `requires-python = ">=3.11"`; CI and the docs workflow both use `3.11`; local interpreter is `py` → Python 3.13 |
| Licence declarations | `LICENSE` (MIT, `Dr. Muhammad Nadeem Majeed`, 2026) · `LICENSE-DATA` (CC BY 4.0 scope notice + legal code) · `pyproject.toml` `license = { text = "MIT" }` · `CITATION.cff` `license: MIT` · README `## Licensing` (dual boundary + third-party exclusion) |
| Licensing manifest | `licensing/manifest.toml`, `schema-version = 1`, 36 coverage entries, 5 statuses |
| CI | `ci.yml` job **`tests and lab self-check`** → checkout → Python 3.11 → **licence metadata and coverage** → install `-e ".[dev]"` → `python -m pytest` → `agentsec labs check`; `docs.yml` builds strictly and publishes to Pages |
| Tracked files | 153 |
| Release-candidate set (tracked + untracked, honouring `.gitignore`) | 162 |

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
?? research/30-new-file-licensing-coverage-audit.md
?? scripts/check_licensing.py
?? tests/test_licensing.py
```

## 2. Scope and limits

Audited: version/release identity, licensing, package quality, repository hygiene, README/documentation, the documentation site, tests, labs, the licensing guard, both CI workflows, security/offline properties demonstrable from the repository, the research boundary, and the content a clean source release would contain.

**Not** audited or asserted: research novelty, publication acceptance, educational effectiveness, causal learning effects, security effectiveness, real-model behaviour, benchmark validity, measurement validity, or third-party licence terms. This audit does **not** claim the repository is "secure" in any general sense; §11 records only the specific, repository-demonstrable properties checked.

Nothing was fixed. Every finding is reported, not acted on.

## 3. Exact commands executed

Read-only inspection:

```bash
git rev-parse HEAD; git log -1 --format='%h %s (%ci)'; git rev-parse --abbrev-ref HEAD
git log --oneline -5; git status --porcelain; git diff --name-only
git diff --cached --name-only; git tag -l | wc -l; git ls-files | wc -l
git ls-files -co --exclude-standard | wc -l; git status --porcelain --ignored
git show HEAD:pyproject.toml; git show HEAD:README.md; git cat-file -e HEAD:<path>
grep -rn "<versions|TODO|FIXME|TBD|secrets|local paths|claim language>" <paths>
find . -name '*.swp' -o -name '*.orig' -o -name '.DS_Store' ...; find . -name __pycache__ | wc -l
du -sh site runs .pytest_cache
py -m pip show agentsec
PYTHONPATH=src py -c "import agentsec; print(agentsec.__version__)"
PYTHONPATH=src py -m agentsec --help; agentsec --help
```

Gate commands (each run at least twice: before and after this audit existed):

```bash
PYTHONPATH=src py -m pytest
PYTHONPATH=src py -m pytest -W error::DeprecationWarning
PYTHONPATH=src py -m agentsec labs check
py -m mkdocs build --strict
py scripts/check_licensing.py
```

Targeted demonstrations (write to temporary directories outside the repository only):

```bash
# YAML validity of both workflows, mkdocs.yml and two config YAMLs
py -c "import yaml; yaml.safe_load(open(<path>))"

# Docker-free / wheel-free demonstration of schema resolution outside the repo
py -c "copytree('src/agentsec', tmp/agentsec); schema_path()"

# persisted-runtime check: runs/ mtimes before and after `agentsec labs check`
find runs -type f -printf '%T@ %p\n' | sort
```

Two commands did **not** succeed and are recorded as such: `from setuptools import build_meta` raised `ModuleNotFoundError: No module named 'setuptools'` in the active interpreter, so the declared wheel metadata could not be generated; the `[project]` table in `pyproject.toml` was therefore read as the authoritative source instead. `python -m build` was not attempted (it is not installed, and a network-free audit should not install it).

## 4. Version / release identity audit

| Location | Version | Notes |
| --- | --- | --- |
| `pyproject.toml` `[project] version` | `0.0.1` | canonical for packaging |
| `src/agentsec/__init__.py.__version__` | `0.0.1` | matches |
| `CITATION.cff` `version` | `"0.0.1"` | matches (CFF requires a string) |
| `README.md` citation block | "version 0.0.1" | matches |
| `CITATION.cff` `cff-version` | `1.2.0` | schema version, unrelated to the release number |
| `mkdocs.yml` | no version | no inconsistency |
| `docs/development.md` | no release-version statement | no inconsistency; its H1 carries a stale `(Phase A)` label (§6) |
| `schemas/trace/trace_event.v1.schema.json` | `v1` (schema version) | a different axis, correctly named |

**Result: PASS.** `0.0.1` is declared consistently in all four places it appears, and no location contradicts another. Two gaps, both reported as warnings rather than inconsistencies: nothing in the test suite ties `pyproject.toml`'s version to `__version__` or to `CITATION.cff` (`tests/labs/test_lab00.py` only asserts `__version__` is a non-empty string), and `CITATION.cff` has no `date-released` field.

## 5. Licence audit

`py scripts/check_licensing.py` → exit `0`:

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

(The coverage line reads 162 files / `cc-by 42` before this audit existed and 163 / `cc-by 43` after it; both runs pass. The audit is itself covered by the manifest's `research/**.md` pattern.)

| Declaration | State | Consistent? |
| --- | --- | --- |
| `LICENSE` | verbatim MIT, 2026, `Dr. Muhammad Nadeem Majeed`; contains no CC BY text | yes |
| `LICENSE-DATA` | CC BY 4.0 scope notice (§1 scope, §2 exclusions, §3 third-party, §4 attribution, §5 notes) + complete 8-section legal code | yes |
| `pyproject.toml` | `license = { text = "MIT" }` | yes |
| `CITATION.cff` | `license: MIT` | yes |
| `README.md` | `## Licensing` names MIT, CC BY 4.0, `LICENSE`, `LICENSE-DATA`, and excludes third-party material | yes |
| `licensing/manifest.toml` | 36 entries across 5 statuses; `excluded`/`unlicensed` entries carry reasons | yes |
| `scripts/check_licensing.py` | 9 checks; declaration checks unchanged since Step 12 | yes |
| `tests/test_licensing.py` | 69 tests; 6 declaration checks + manifest + coverage + offline/read-only | yes |

**Coverage:** 163 files accounted for, **0 unaccounted, 0 conflicts, 0 stale patterns, 0 undecided**. Zero files are recorded as unlicensed. Every file in the release-candidate set has an explicit recorded treatment, and nothing is classified by file extension.

**Human-judgement residuals (not machine-detectable, carried from `research/28`–`research/30`):**

1. `LICENSE`'s MIT text refers to "this software and associated documentation files", which overlaps the CC BY 4.0 content grant. Consistency is enforced; exclusivity is not. Owner's call.
2. CC BY 4.0 was adopted from documented intent, not an explicit decision; CC BY-SA 4.0 or CC0 remain viable, and a switch would touch `LICENSE-DATA`, one README table row, the manifest's `cc-by` status, and the guard's markers together.
3. The adopted content scope is narrower than the older planning records ("data/docs/documents") describe.
4. The guard detects a *missing* licensing decision, not a *wrong* one.
5. The README's licensing table is prose; the manifest is the machine-checked source, and the two can drift without failing CI.
6. Third-party titles, names, venues, DOIs and quotations inside `research/*.md` are outside both grants by declaration only; no per-quotation inventory is maintained.
7. `.freebuff/project-id` is recorded as outside both grants (see §7, W7).
8. No SPDX identifiers and no `license-files`/`license-expression` packaging field.

No legal text was altered in this step.

## 6. Package / metadata audit

| Item | Observed | Verdict |
| --- | --- | --- |
| `[build-system]` | `setuptools>=68`, `setuptools.build_meta` | PASS |
| `name` / `version` | `agentsec` / `0.0.1` | PASS |
| `description` | ends `"(Phase A skeleton)"` | **W2** |
| `readme` | `docs/development.md` (H1 contains `(Phase A)`) | **W3/W4** |
| `requires-python` | `>=3.11` | PASS |
| `license` | `{ text = "MIT" }` — legacy form (PEP 639 prefers an SPDX string + `license-files`) | **W10** |
| runtime dependencies | `pydantic>=2.6`, `jsonschema>=4.20`, `PyYAML>=6.0` | PASS — exactly the three imported |
| optional extras | `dev = ["pytest>=7.4"]`, `live = ["httpx>=0.27"]`, `docs = ["mkdocs-material>=9"]` | PASS with W11 (unpinned docs extra) |
| console entry point | `agentsec = "agentsec.cli:main"` | PASS — `agentsec --help` works |
| module entry point | `py -m agentsec --help` | PASS — four subcommands: `run`, `evaluate`, `inspect`, `labs` |
| package discovery | `[tool.setuptools.packages.find] where = ["src"]` | PASS |
| package data | **none declared** | **W5** |
| `[project] authors / classifiers / keywords / urls` | absent | **W10** (informational for a tag release) |
| importability | `import agentsec` → version `0.0.1` from `src/agentsec/__init__.py` | PASS |
| import errors | none | PASS |
| stale package docstring | `__init__.py` says "Phase A … **Deliberately no real model adapters or lab material yet**" | **W2b** |
| debug leftovers | no `breakpoint(`, no `import pdb`, no stray `print(` outside `cli.py`/`selfcheck.py`/`mvp.py` | PASS |
| TODO/FIXME/XXX/HACK/TBD in source | **none** (the only `TBD` hits are historical statements inside `research/27`, deliberately unmodified) | PASS |

**Dependency verification (AST scan of every `src/**/*.py`):** absolute imports are `__future__`, `argparse`, `ast`, `collections`, `copy`, `dataclasses`, `datetime`, `enum`, `fnmatch`, `hashlib`, `json`, `jsonschema`, `math`, `operator`, `pathlib`, `pydantic`, `re`, `sys`, `tempfile`, `typing`, `yaml`. The only third-party imports are the three declared runtime dependencies — **no development-only dependency leaked into the runtime set**, and **no network module is imported anywhere in `src/`**.

**W5, demonstrated:** copying `src/agentsec` to a temporary directory outside the repository and importing it yields
`schema_path() raised: FileNotFoundError could not locate schemas/trace/trace_event.v1.schema.json above …/agentsec/trace/validate.py`.
The trace schema is resolved by walking up from `__file__` to the repository's `schemas/` directory, and the `labs check` subcommand likewise needs a `--labs-dir` pointing at the repository's `labs/`. The documented workflow (README "Getting started": `pip install -e ".[dev]"` from the repository root, commands run from the repository root) is unaffected, and a tagged source release preserves the layout. A wheel or sdist published to an index would not be self-contained.

**W9, local-state evidence:** `py -m pip show agentsec` reports `Summary: … (Phase A skeleton).` and **`License: TBD`** because the editable install in this checkout predates the Step 10 licence change; its metadata lives in the git-ignored `src/agentsec.egg-info/`. It does not enter the release (ignored), but the local environment misreports the licence until the package is reinstalled.

## 7. Repository hygiene audit

Classification used below: **A** harmless ignored development artefact · **B** release-distributed artefact · **C** actual release blocker.

| Material | Status | Class | Note |
| --- | --- | --- | --- |
| `.pytest_cache/` (67 K) | ignored (`!!`) | A | test cache |
| `site/` (62 files, 3.3 M) | ignored | A | MkDocs build output, regenerated by the docs workflow |
| `src/agentsec.egg-info/` | ignored | A | editable-install metadata (§6, W9) |
| 22 × `__pycache__/` | ignored | A | bytecode |
| `runs/` (8 traces, 68 K) | ignored | A (runtime data) | lab runtime output; see §14 W-trace |
| `.freebuff/project-id` (37 bytes) | **tracked** | B | local tooling metadata, distributed in every clone and source archive (W7) |
| editor/OS files (`*.swp`, `*.orig`, `*~`, `.DS_Store`, `Thumbs.db`, `*.bak`, `*.tmp`) | none found | — | PASS |
| `build/`, `dist/` | absent | — | PASS |
| secrets / API keys / tokens / credentials | **none found** | — | see §11 |
| private filesystem paths (`F:\…`, `C:\…`, `/home/…`, `/Users/…`) in repository content | **none found** | — | the only `Nadeem` matches are the intentional copyright holder in `LICENSE`, `LICENSE-DATA`, `CITATION.cff` |
| generated-but-tracked artefacts | `schemas/trace/trace_event.v1.schema.json` | B | intentional and drift-tested (`tests/schema/test_schema_file.py`) |

`git status --porcelain --ignored` shows every ignored entry under `!!`; no ignored material is tracked and no tracked file is in an ignored path. **No category-C hygiene blocker was found.**

The `.gitignore` categories that protect the release — `__pycache__/`, `*.egg-info/`, build/dist, `.venv/`, tooling caches, `runs/`, `site/`, `.env`, `*.local` — are all present and effective, and are mirrored by the manifest's `not-distributed` patterns.

## 8. README / documentation audit

| Check | Result |
| --- | --- |
| Describes the actual current artefact | PASS — "an existing, working artefact — not a plan", eight labs LAB-00…LAB-07, explicit "no LAB-08" |
| Installation instructions | PASS — `py -m pip install -e ".[dev]"`, Python 3.11+, "no API key and no network connection are needed" |
| Basic usage | PASS — five numbered commands, each of which is a real CLI command (`run`, `inspect`, `evaluate`, `labs check`) |
| Labs described | PASS — lab map matches `labs/` (8 lab directories) |
| Verification instructions | PASS — `## Verification status` table with the four real gates |
| Licensing | PASS — `## Licensing` with the dual boundary, attribution guidance and the third-party exclusion |
| Citation | PASS — `## Citation` with a formatted reference and the `CITATION.cff` link |
| Repository URLs | PASS — <https://github.com/nadeem-majeedch/agent-security-labs> matches `CITATION.cff` `repository-code` |
| Documentation URL | PASS — <https://nadeem-majeedch.github.io/agent-security-labs/> matches `CITATION.cff` `url` |
| Stale "planned study" language | **none found** (`planned`/`not started`/`will be`/`TBD`/`placeholder` → 0 hits) |
| Stale "implementation not started" language | **none found** in the README; the stale equivalents live in `pyproject.toml`, `docs/development.md` and `src/agentsec/__init__.py` (§6 W2/W2b/W4) |
| False research claims | none — `## What this project does **not** claim` disclaims novelty, effectiveness and real-model claims explicitly |
| Relative links | **57/57 resolve** |
| In-page anchors | **3/3 resolve** (`#licensing`, `#verification-status` ×2) |
| Version references | PASS — citation says version 0.0.1, matching `pyproject.toml` |

## 9. Documentation site audit

`py -m mkdocs build --strict` → **exit 0**, "Documentation built in 0.44 seconds", 16 HTML pages.

| Check | Result |
| --- | --- |
| Build errors | **0** |
| Builder warnings | **0** (`grep -c "WARNING -|ERROR -"` → 0) |
| Non-fatal banner | one **upstream advisory** from the Material for MkDocs theme about MkDocs 2.0 (backward-incompatible changes, "currently unlicensed"), printed by the theme, not a build diagnostic (W11) |
| Navigation resolves | PASS — every nav target in `mkdocs.yml` exists (`GETTING-STARTED.md`, `README.md`, the eight lab pages, `TRACE-WALKTHROUGHS.md`, `TRACE-READING-EXERCISES.md`, `INSTRUCTOR-GUIDE.md`, `LOCAL-VERIFICATION.md`) |
| Referenced files exist | PASS — `docs_dir: labs`; `exclude_docs: **/*.yaml` keeps lab config out of the site |
| Intentional validation relaxation | `validation.nav.omitted_files: ignore` — the instructor answer key is built but deliberately not in the nav; documented in `mkdocs.yml` |
| Local-only URLs in built output | **none** — no `F:\`, `localhost`, `127.0.0.1` or `file://` in site content; those strings occur only inside the vendored Material JavaScript **source map** (`site/assets/javascripts/*.js.map`), which is third-party asset content |
| External hosts in built output | only third-party asset/font/anchor hosts (`w3.org`, `bit.ly`, `mozilla.org`, `rxjs.dev`, `squidfunk.github.io`, `fonts.g*`, library source-map comments) |
| Docs workflow | `docs.yml` builds strictly and publishes to Pages with minimum permissions; untouched |

## 10. Test audit

| Metric | Value |
| --- | --- |
| Command | `PYTHONPATH=src py -m pytest` |
| Result | **764 passed**, exit 0, 11.2 s |
| Failures | 0 |
| Errors | 0 |
| Skipped / xfail | **0** — no `pytest.mark.skip`, `xfail` or `pytest.skip` anywhere under `tests/` |
| Warnings | none surfaced; the suite also passes under `-W error::DeprecationWarning` (764 passed) |
| Test files | 35 modules under `tests/` (34 tracked before Step 13 + `tests/test_licensing.py`) |
| Composition | 695 tests before Step 13 + 69 in `tests/test_licensing.py` = 764 |
| Tests changed in this step | **none** |

## 11. Lab audit

`PYTHONPATH=src py -m agentsec labs check` → exit 0:

```
LAB SELF-CHECK
==============

LAB-00  PASS
LAB-01  PASS
LAB-02  PASS
LAB-03  PASS
LAB-04  PASS
LAB-05  PASS
LAB-06  PASS
LAB-07  PASS

Result: 8/8 labs passed
```

* **8/8**, no hidden failure; exit code 0.
* **No generated artefact entered the repository.** `find runs -type f -printf '%T@ %p\n' | sort` produced a byte-identical mtime list before and after the self-check re-run — all 8 trace files kept their original timestamps — confirming the documented behaviour that `labs check` runs each lab into a temporary directory and writes nothing under `runs/`.
* The self-check uses the deterministic fixture stack with a fixed clock, requires no network, no credentials and no external service.

## 12. CI audit

Both workflows parsed with `yaml.safe_load` → **valid**.

`ci.yml` (`name: CI`, trigger `push` + `pull_request`):

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
| YAML validity | PASS |
| Licensing check **before** `pip install` | PASS — step 3 of 6; possible because the guard is standard-library-only |
| Test suite intact | PASS |
| Labs check intact | PASS |
| Job display name | **`tests and lab self-check`** — unchanged since before Step 12 (branch protection may reference it) |
| Unexpected secrets required | **none** — the only `${{ … }}` expression is `steps.deployment.outputs.page_url` in `docs.yml`; no `secrets.` context is used anywhere |
| Network dependency introduced into the licensing guard | **none** — see §13 |
| Commands correspond to current repository commands | PASS — all three commands exist and were executed successfully in this audit |

`docs.yml` (`name: Docs`, `push` to `main` + `workflow_dispatch`): builds the site strictly and deploys to Pages with `contents: read`, `pages: write`, `id-token: write` and a non-cancelling `pages` concurrency group. No tests, as documented. **No issue found.**

## 13. Security / offline audit (repository-demonstrable properties only)

| Property | Evidence | Result |
| --- | --- | --- |
| No credentials, tokens or API keys in repository content | full-tree scan for `api_key`, `secret`, `password`, `token`, `bearer`, `credential`, `ghp_`, `BEGIN … PRIVATE KEY` (excluding `.git`/ignored caches); all hits are prose about *not* using credentials, synthetic lab fixtures, or the workflows' OIDC/Pages references | PASS |
| No network calls in the licensing guard | no `urlopen`, `urlretrieve`, `urllib`, `requests`, `httpx`, `socket` in `scripts/check_licensing.py`; the import allowlist is `argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `tomllib` | PASS |
| No write operations in the licensing guard | no `write_text`, `write_bytes`, `open(`, `mkdir`; the guard only reads and walks | PASS |
| No shell execution in the licensing guard | no `subprocess`, `popen`, `os.system`; it does not read `.git` internals (`ls-files`, `.git/index`, `refs/heads` all absent) | PASS |
| Guard verified read-only at runtime | `tests/test_licensing.py` byte-compares all six declarations (including the manifest) before and after a run | PASS |
| No network module anywhere in `src/` | AST scan of every `src/**/*.py` — **no** network/transport module imported | PASS |
| No hidden external service dependency for the labs | synthetic in-memory `mock_db` / `mock_email` / sandboxed filesystem; `labs check` re-run in this environment completed offline | PASS |
| No real-provider credentials required | the "live" adapter does not exist in `src/` (the `httpx` extra is declared but unused); the model is a deterministic scripted fixture | PASS |
| No accidental outbound calls during the audited runs | all five gate commands completed in an offline-capable environment with no provider configuration | PASS |

This audit demonstrates the properties above and nothing more. It does **not** claim the repository is secure, audited for vulnerabilities, or free of defects outside these checks.

## 14. Release-content classification

Derived from the tracked set plus `.gitignore`; nothing was moved or removed.

**A. Intended distributable repository content — 163 files.** `src/` (39) · `research/` (39: 26 Markdown records + 13 machine-readable CSVs) · `tests/` (35) · `labs/` (30: 15 Markdown + 15 YAML) · `policies/` (4) · `scripts/` (2) · `.github/` (2) · `schemas/` (1) · `licensing/` (1) · `docs/` (1) · `configs/` (1) · `.freebuff/` (1) · root metadata (7: `.gitignore`, `CITATION.cff`, `LICENSE`, `LICENSE-DATA`, `README.md`, `mkdocs.yml`, `pyproject.toml`). Every one of these is accounted for by the manifest; the count was 162 before this audit existed.

**B. Development-only ignored files.** `__pycache__/` ×22, `.pytest_cache/`, `src/agentsec.egg-info/`; `.mypy_cache/`, `.ruff_cache/`, `.venv/`, `build/`, `dist/` are declared but absent.

**C. Local tooling metadata.** `.freebuff/project-id` — **tracked**, so it is distributed despite being local tooling state (W7).

**D. Generated runtime data.** `runs/` (8 traces), `site/` (62 files). Both ignored and in the manifest's `not-distributed` set.

**E. Research / audit records.** 39 files: 26 Markdown (tracked `research/01`–`research/14` and `research/20`–`research/27`, plus the uncommitted new `research/28`, `research/29`, `research/30` and this audit) and 13 CSVs in `research/tables/`. All are licence-covered (Markdown → CC BY 4.0 under `research/**.md`; CSVs → MIT under `research/tables/*.csv`).

**F. Licence / legal files.** `LICENSE`, `LICENSE-DATA` (self-excluded from its own grant), `CITATION.cff`, `licensing/manifest.toml`.

A clean source release would therefore contain A + B-absent + C + E + F, with D excluded by `.gitignore`, and would — after a commit of the pending work — be fully covered by the licensing manifest.

## 15. Findings, classified

Exactly one classification per finding. No subjective ranking is used.

### BLOCKER

**B1 — The release content is uncommitted, and `HEAD` contradicts it about licensing.**
Evidence: `git status --porcelain` lists 13 pending paths; `git show HEAD:pyproject.toml` contains `license = { text = "TBD" }`; `git show HEAD:README.md` still states "**No licence has been assigned yet.** … no `LICENSE` or `CITATION.cff` file exists yet"; `git cat-file -e HEAD:<path>` fails for **all six** licensing deliverables (`LICENSE`, `LICENSE-DATA`, `CITATION.cff`, `licensing/manifest.toml`, `scripts/check_licensing.py`, `tests/test_licensing.py`).
Consequence: any tag, GitHub release or source archive created from the current revision would publish an artefact whose own metadata declares no licence, whose README says no licence exists, and which contains none of the licensing, coverage, manifest or CI work verified above. The v0.0.1 release identity would be factually wrong about its own licence. This is not a defect of the working tree — it is the fact that the release content does not yet exist in a commit.
Resolution is a commit of the pending work (out of scope for this step, which must not commit).

### WARNING

**W2 — `pyproject.toml` `description` ends `"(Phase A skeleton)"`.** Appears as the packaged `Summary`. Contradicts the README and the eight implemented labs.
**W2b — `src/agentsec/__init__.py` module docstring** states "Phase A … **Deliberately no real model adapters or lab material yet**". Factually wrong for the current artefact: the eight labs exist. It ships inside the distributed package.
**W3 / W4 — `docs/development.md` H1** reads "# AgentSec Lab - development notes (Phase A)" and the file is `pyproject.toml`'s `readme` target, so the stale label ships as the package long description.
**W5 — The package is not self-contained.** No package data is declared; `trace/validate.schema_path()` walks up from `__file__` to the repository's `schemas/` directory and raises `FileNotFoundError` when the package is used outside the repository (demonstrated, §6). Affects a wheel/sdist on an index; does not affect a tagged source release or the documented in-repo workflow.
**W6 — `CITATION.cff` has no `date-released`.** Optional in CFF 1.2.0; normally set when the release is created.
**W7 — `.freebuff/project-id` is tracked**, so local tooling metadata for a third-party tool is distributed in every clone and source archive. Its licensing status is now explicitly recorded as outside both grants. Note also that `research/01` line 716 asserts `.freebuff` is "excluded by `.gitignore` and never enter[s] a release", which is false for this file — a historical record, not to be edited.
**W8 — No version-drift guard.** `pyproject.toml` version, `__version__` and `CITATION.cff` version agree today (all `0.0.1`), but no test or script enforces that; `tests/labs/test_lab00.py` only asserts `__version__` is a non-empty string.
**W9 — The local editable install reports stale metadata** (`License: TBD`, old Summary) because it predates the Step 10 licence change. Ignored artefact, so it does not reach the release; the local environment is misleading until reinstalled.
**W10 — Legacy/limited packaging metadata.** `license = { text = "MIT" }` is the deprecated form (PEP 639 prefers an SPDX string plus `license-files`); `[project]` declares no `authors`, `classifiers`, `keywords` or `urls`. No SPDX identifiers anywhere in the repository.
**W11 — `docs` extra is unpinned** (`mkdocs-material>=9`), and the theme prints an upstream advisory that MkDocs 2.0 will break themes, plugins and overrides, and is "currently unlicensed". A forward dependency risk to accept consciously.
**W12 — Licensing residuals requiring human judgement** (§5 items 1–8), including the MIT/CC-BY "associated documentation files" overlap and the fact that the machine-checked manifest can drift from the README's prose table.
**W13 — `traces/*.jsonl` is listed in `.gitignore` and the manifest but the `traces/` directory does not exist.** Harmless, but the entry refers to nothing.

### INFORMATIONAL

**I1** `site/` (3.3 M), `runs/` (68 K), `.pytest_cache/`, 22 `__pycache__/` and `src/agentsec.egg-info/` exist on disk and are all correctly ignored.
**I2** Zero `TODO`/`FIXME`/`XXX`/`HACK`/`TBD` markers in any source file; the only `TBD` occurrences are historical statements in `research/27`.
**I3** Zero skips, xfails or deprecation warnings in the 764-test suite (the suite also passes with `-W error::DeprecationWarning`).
**I4** No editor or OS artefacts; no `build/` or `dist/`; no secrets or private paths in repository content.
**I5** No tags and no GitHub release exist, so there is no stale release metadata to correct.
**I6** `mkdocs.yml` deliberately sets `validation.nav.omitted_files: ignore` for the instructor answer key, documented in the file's own comments.
**I7** The built site's only local-looking URLs are inside the vendored Material JS source map (third-party asset), not site content.
**I8** The README documentation URL and `CITATION.cff` `url` are identical; the README repository URL matches `CITATION.cff` `repository-code`.
**I9** `python -m build` / `setuptools` are not available in this environment, so no wheel or sdist was produced during the audit; `pyproject.toml` was read as the authoritative metadata source.

### PASS

| # | Item |
| --- | --- |
| P1 | Version `0.0.1` declared consistently in `pyproject.toml`, `__version__`, `CITATION.cff` and the README citation block |
| P2 | Licensing guard: **9/9 checks pass**, exit 0 |
| P3 | Licensing coverage: **163 files accounted for**, 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| P4 | Declared licence boundary internally consistent across all six declarations; no legal text altered |
| P5 | Package imports cleanly; `agentsec` console script and `python -m agentsec` both work; four documented subcommands |
| P6 | Runtime dependencies are exactly the three third-party modules imported; no dev-only dependency leaked into runtime |
| P7 | No TODO/FIXME/TBD release markers in source; no debug leftovers |
| P8 | No secrets, credentials, tokens, private paths or editor/OS artefacts in repository content |
| P9 | All ignored material is correctly ignored; no ignored file is tracked |
| P10 | README accurately describes the artefact; 57/57 relative links and 3/3 anchors resolve; no stale planning or "implementation not started" language |
| P11 | MkDocs strict build: exit 0, 0 errors, 0 warnings, 16 pages, navigation resolves |
| P12 | Test suite: 764 passed, 0 failures, 0 errors, 0 skips, no meaningful warnings |
| P13 | Lab self-check: 8/8 passed, exit 0, and writes nothing into `runs/` (mtime-verified) |
| P14 | CI: both workflows valid YAML; licensing runs before `pip install`; job name preserved; no secrets required; commands match the repository |
| P15 | Licensing guard is offline, read-only, dependency-free and does not read Git internals |
| P16 | No network module in `src/`; labs need no network, credentials or external service |
| P17 | Research boundary intact: Phase 17 CLOSED and documented; no tracked research file modified; no novelty/effectiveness/publication/benchmark/security claims added |

## 16. Version consistency: `"(Phase A skeleton)"`

**Classification: WARNING (W2), not a blocker, and not merely informational.**

Reasoning, from evidence:

* **Not a blocker** — no gate fails because of it (`pytest` 764/764, labs 8/8, MkDocs strict exit 0, licensing 9/9 all pass with the string in place); it does not affect installability, the entry point, the declared licence, the dependency set, the test suite or the labs; and it is a stale *label*, not a false claim of achievement or a false legal statement. A release remains technically possible while it stands.
* **Not merely informational** — it is not invisible: it becomes the packaged `Summary` field (verified in the local distribution metadata, §6), it appears in a file (`docs/development.md`) that is simultaneously the package's `readme` target and a linked architecture reference from the README, and it contradicts the repository's own README and its eight implemented labs. The same staleness appears in the package's top-level module docstring, which additionally claims there is no "lab material yet" — a statement that is false for the shipped artefact. `research/27` had already flagged the description as stale before Step 10, and Steps 10–13 deliberately left it untouched.
* **Why a warning, not a blocker, is the consistent call:** the direction of the error is *understatement* — it describes the artefact as less complete than it is — and this repository's stated risk posture targets overstatement. It is also a documentation-accuracy defect on a metadata field, with no behavioural consequence. The owner must consciously accept or fix it before tagging.

**Is `0.0.1` declared consistently enough to release?** Yes. The number itself is consistent across all four locations that state it (§4), the package imports and reports `0.0.1`, and `CITATION.cff` carries `version: "0.0.1"` matching `pyproject.toml`. The gaps are adjacent to the version rather than in it: no `date-released` in `CITATION.cff` (W6) and no automated guard preventing future drift between the three copies (W8). Neither makes the current declaration inconsistent.

## 17. Release checklist

**Must be resolved before v0.0.1 can be released**

- [ ] **B1** Commit the pending Steps 9–13 work so that the release revision contains the licence files, `CITATION.cff`, the manifest, the coverage guard, the licensing tests, the README rewrite and the CI step. Until `HEAD` matches the audited working tree, do not tag.

**Consciously accepted or fixed before tagging (not blocking)**

- [ ] **W2** Decide on the `pyproject.toml` description ending `"(Phase A skeleton)"`.
- [ ] **W2b** Decide on the stale `src/agentsec/__init__.py` package docstring ("no … lab material yet").
- [ ] **W3/W4** Decide on the `docs/development.md` H1 `(Phase A)` label (it is the packaged long description).
- [ ] **W5** Accept or address that the installed package is not self-contained outside the repository (no package data; `schema_path()` needs the repo layout).
- [ ] **W6** Add `date-released` to `CITATION.cff` when the release is created.
- [ ] **W7** Accept or remove distribution of `.freebuff/project-id`.
- [ ] **W8** Optionally add a version-drift check across `pyproject.toml`, `__version__` and `CITATION.cff`.
- [ ] **W9** Locally reinstall (`pip install -e ".[dev]"`) so the environment stops reporting `License: TBD`.
- [ ] **W10** Optionally modernise packaging metadata (SPDX string, `license-files`, `authors`, `classifiers`, `urls`).
- [ ] **W11** Accept the unpinned `docs` extra and the MkDocs 2.0 advisory.
- [ ] **W12** Record the human-judgement licensing residuals as accepted.
- [ ] **W13** Optionally drop or keep the non-existent `traces/*.jsonl` entry.

**Verified passing at this revision (no action)**

- [x] P1–P17 above.

## 18. Final evidence-based release status

# NOT READY

**Determined solely by B1.** The specific findings that determine the status:

1. The audited release content does not exist in a commit. `HEAD` (`995cf68`) declares `license = { text = "TBD" }`, its README states that no licence and no `CITATION.cff` exist, and `git cat-file -e HEAD:<path>` confirms that `LICENSE`, `LICENSE-DATA`, `CITATION.cff`, `licensing/manifest.toml`, `scripts/check_licensing.py` and `tests/test_licensing.py` are all absent from that revision.
2. Because a release is created from a revision, a v0.0.1 tag placed now would publish an artefact that is factually wrong about its own licence and that omits every licensing control verified in §5 and §12.

**No other finding determines the status.** Every technical gate passes on the working tree as it stands: 764/764 tests, 8/8 labs, MkDocs strict with zero warnings and zero errors, and 9/9 licensing checks with 163/163 files accounted for, 0 unaccounted, 0 conflicts, 0 stale and 0 undecided. There are no secrets, no private paths, no debug markers and no network dependency in `src/` or in the guard.

**What the status would become.** Once B1 is resolved by a commit — and no other change is made — the findings that remain are the WARNINGs in §15, and the evidence-based status would be **READY WITH WARNINGS**, which the owner may accept consciously or reduce by addressing W2–W13. This audit does not recommend either course; it records the evidence.

## 19. Statement: no release was created

In this step:

* no tag was created (`git tag -l` → 0 entries, unchanged);
* no GitHub release was created;
* nothing was staged (`git diff --cached --name-only` empty);
* nothing was committed — `HEAD` remains `995cf6876d0a103968204c5b9be59371d564ae4f`;
* nothing was pushed;
* no `reset`, `checkout`, `clean`, `rebase`, `amend`, `stash` or destructive command was run;
* no source, lab, test, policy, schema, scenario, CI, documentation, licensing, manifest or previous research file was modified;
* `LICENSE`, `LICENSE-DATA` and `CITATION.cff` were read but not altered in any way;
* `research/30` was not modified; the only file created is this audit, `research/31-final-release-readiness-audit.md`;
* the only writes performed were to temporary directories outside the repository (a package copy for the §6 demonstration, which was deleted by its context manager).

**This audit stops here. It does not proceed to v0.0.1 release creation, and it makes no commitment to do so.**

## 20. Research-boundary confirmation

* **Phase 17 remains CLOSED** — recorded in `docs/development.md` ("Research status (Phase 17 — CLOSED, research NO-GO)").
* **E1 remains HOLD** — recorded in the research records (`research/24`, `research/25`, `research/26`: E1 = HIGH-RISK / INSUFFICIENTLY DISTINCT; publication gate = HOLD) and carried forward by `research/28`–`research/30`. E1 is deliberately not a claim in the shipped README or documentation site.
* **Historical records preserved.** `git status --porcelain research/` shows **no modification to any tracked research file** — the 35 tracked research paths are untouched, so no research conclusion, classification or uncertainty reading has been silently altered. The only research-tree changes in the working tree are the three new untracked audit records (`research/28`, `research/29`, `research/30`) plus this file.
* **No claim added.** This audit asserts no research novelty, no empirical or educational effectiveness, no benchmark or measurement validity, no security effectiveness, no real-model behaviour, no learner improvement and no publication readiness. Its §13 findings are limited to what the repository demonstrates about its own offline, credential-free operation.

---

*End of Phase 20 — Step 14. Read-only release-readiness audit complete; status NOT READY on B1; no tag, release, commit, push or staging was performed.*
