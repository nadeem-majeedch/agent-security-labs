# PHASE 20 — STEP 15: STALE PACKAGE METADATA CLEANUP AUDIT

**Status: PASS — the stale metadata identified as W2, W2b and W3/W4 in `research/31`/`research/32` has been corrected, and the correction did not disturb the working artefact.**

Scope: three active files describing the package. No other file was touched. No commit, push, tag, release or staging was performed. The working tree is left unstaged and uncommitted for manual review.

This step makes **no research claim**. Phase 17 remains **CLOSED**. **E1 remains HOLD**. No learner study was performed. No novelty, effectiveness, security-effectiveness, benchmark or publication claim was introduced. No previous audit was modified. No commit, tag or release was created.

---

## 1. Status

| Item | Value |
| --- | --- |
| Step | Phase 20 — Step 15, stale package metadata cleanup |
| Outcome | **PASS** |
| Files modified | **3** (`pyproject.toml`, `docs/development.md`, `src/agentsec/__init__.py`) |
| Net change | `+18 / −11` lines |
| Gates after the change | pytest **764 passed** · labs **8/8** · MkDocs strict **exit 0** · licensing **9/9** |
| Licence coverage after the change | **164 files accounted for** (mit 118, cc-by 44, excluded 2, unlicensed 0); 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| Warnings addressed | W2, W2b, W3/W4 (all three text sites) |
| Warnings deliberately left | W5 (self-containment), W6, W7, W8, W9, W10, W11, W12, W13 |
| Staged / committed / tagged | **none** |
| Release classification after this step | **not re-declared** — see §18 |

## 2. Starting HEAD

| Item | Value |
| --- | --- |
| `HEAD` | `54a5e611cd1d0998f5fe4c06d8107f508f04d5a9` (`54a5e61` "final release") |
| Branch | `main` |
| Tags | 0 |
| Working tree at start | clean except the untracked `research/32-post-commit-release-readiness.md` |
| `git diff --name-only` at start | empty |
| Baseline classification | READY WITH WARNINGS (`research/32`) |

`HEAD` is unchanged at the end of this step (§16).

## 3. Files modified

`git diff --stat`:

```
 docs/development.md      |  9 ++++++---
 pyproject.toml           |  2 +-
 src/agentsec/__init__.py | 18 +++++++++++------
 3 files changed, 18 insertions(+), 11 deletions(-)
```

Nothing else was patched: no lab, policy, scenario, schema, config, CLI, CI, licensing, manifest, test or research file was modified. The change set is exactly the three stale-metadata sites.

## 4. Exact stale metadata found

Confirmed by reading each file before editing and by `git grep` at HEAD (all three are active, non-research files):

| File | Line | Stale text |
| --- | --- | --- |
| `pyproject.toml` | 8 | `description = "AI Agent Security Lab - educational, reproducible agent-security infrastructure (Phase A skeleton)."` |
| `docs/development.md` | 1 | `# AgentSec Lab - development notes (Phase A)` |
| `docs/development.md` | 3–4 | `Educational, reproducible agent-security infrastructure. Implemented so far:` / `the skeleton, core data models, the trace schema/validation/recording,` |
| `src/agentsec/__init__.py` | 3–8 | `Phase A: core data models, … scenario layer. Deliberately no real model adapters or lab material yet (see research/14-implementation-blueprint.md).` |

Three distinct defects:

1. **A stale phase label** in packaged metadata and the two most-read prose sites (`Phase A`, `Phase A skeleton`).
2. **A skeleton framing** ("the skeleton", "Implemented so far") that presents an existing, verified artefact as an early scaffold.
3. **A factually false statement inside the distributed package**: the module docstring claimed there was no "lab material yet", while the repository ships eight labs (LAB-00 … LAB-07) and the same revision's README states that all eight are implemented.

The historical occurrences in `research/06`, `research/08`, `research/09`, `research/13`, `research/14`, `research/27`, `research/28`, `research/29`, `research/30`, `research/31` and `research/32` are records of earlier repository states and were **left untouched** (§9).

## 5. Exact replacement rationale

Every replacement states only what the repository demonstrably contains, keeps the package version and all other metadata unchanged, and avoids the forbidden vocabulary (no "novel", "state-of-the-art", "effective", "secure", "superior", "benchmark", "publication-ready", "research contribution").

| Site | Replacement | Rationale |
| --- | --- | --- |
| `pyproject.toml` description | `Agent Security Labs - an offline, deterministic agent-security teaching laboratory with mediated tool execution and eight reproducible labs.` | Names the existing artefact (teaching laboratory), the two properties the code implements (mediated tool execution, determinism/reproducibility), the offline orientation, and the eight labs. One line, no phase label, no claim of quality, effect or novelty. Matches the CITATION title "Agent Security Labs". |
| `docs/development.md` H1 | `# AgentSec Lab - development notes` | Drops the stale phase label; the document remains what it is — the architecture and development reference — and its in-repo links from the README and the instructor guide are unaffected. |
| `docs/development.md` opening | "An existing, working educational agent-security laboratory. Every tool call passes through one mediated gateway and every run writes a readable trace, so behaviour is studied by reading the trace; the runs are offline and deterministic, with no network and no API key. It consists of core data models, the trace schema/validation/recording, …" | Replaces "Implemented so far: the skeleton, …" with a description of the existing artefact, and states the mediated-execution and offline/readable-trace properties that the rest of the document already describes. The component inventory that follows is unchanged. |
| `src/agentsec/__init__.py` docstring | "AgentSec Lab - the implementation behind the Agent Security Labs." plus a description of the offline deterministic loop, the mediated `ToolGateway`, the readable JSONL trace, the components that live in the package, and "the eight student labs (LAB-00 to LAB-07) are repository content under `labs/`." | Identifies the package as the implementation behind the educational artefact, removes the false "no lab material yet" claim, and drops a reference to a repository-only file (`research/14-implementation-blueprint.md`) that is not meaningful inside a shipped package. The pre-existing "no real model adapters and no defences" limitation and the "**no research-novelty claim**" disclaimer are retained verbatim in substance. |

**Scope discipline:** the component inventory, the architecture sections, the operating instructions and the research-boundary statements in `docs/development.md` were **not** rewritten; the document was not restructured. The two untouched sentences in the opening paragraph ("There are deliberately no real model adapters and **no defences yet** - the adversarial labs observe behaviour only") remain as they were.

## 6. pyproject metadata result

```toml
[project]
name = "agentsec"
version = "0.0.1"
description = "Agent Security Labs - an offline, deterministic agent-security teaching laboratory with mediated tool execution and eight reproducible labs."
readme = "docs/development.md"
requires-python = ">=3.11"
license = { text = "MIT" }
```

* **Version unchanged:** `0.0.1`.
* **Unchanged:** dependencies (`pydantic>=2.6`, `jsonschema>=4.20`, `PyYAML>=6.0`), optional dependencies (`dev`, `live`, `docs`), `license = { text = "MIT" }`, `readme`, `requires-python`, `[build-system]`, `[project.scripts]`, `[tool.setuptools.packages.find]`, `[tool.pytest.ini_options]`. The diff is one line.
* No dependency was added or removed. Nothing outside `description` was touched.

## 7. Development documentation result

`docs/development.md`, first paragraph after the H1 (as written):

```
# AgentSec Lab - development notes

An existing, working educational agent-security laboratory. Every tool call
passes through one mediated gateway and every run writes a readable trace, so
behaviour is studied by reading the trace; the runs are offline and
deterministic, with no network and no API key. It consists of core data models,
the trace schema/validation/recording,
redaction, a deterministic mock model, **sandboxed tools**, the **mediated
ToolGateway**, ...
```

* The H1 no longer carries `(Phase A)`.
* "the skeleton" and "Implemented so far:" are gone; the sentence now describes the artefact as it is.
* The eight-lab inventory, the LAB-02/LAB-03/LAB-04 parenthetical, the `require_approval` note and the LAB-07 "authorized egress" description are unchanged.
* The architectural and development guidance later in the file is untouched, as is the `## Research status (Phase 17 — CLOSED, research NO-GO)` section, which was not opened or edited.
* This file is also `pyproject.toml`'s `readme` target, so the corrected text is what ships as the package long description (§10).

## 8. Package `__init__` result

`src/agentsec/__init__.py` now opens:

```python
"""AgentSec Lab - the implementation behind the Agent Security Labs.

An offline, deterministic educational agent-security laboratory: a small agent
loop runs against a scripted model fixture and in-memory tools, every tool call
passes through the mediated ToolGateway, and each run writes a readable JSONL
trace. The core data models, trace schema/validation/recording, redaction, the
minimal PolicyEngine, the read-only descriptive evaluator, the one-run
experiment runner, the CLI and the declarative scenario layer live here; the
eight student labs (LAB-00 to LAB-07) are repository content under ``labs/``.

There are deliberately no real model adapters and no defences yet - the
adversarial labs observe behaviour only.

This package makes **no research-novelty claim**; it reimplements established
concepts for teaching and reproducible experimentation.
"""
```

* The false "no real model adapters or lab material yet" statement is gone; the eight labs are named as repository content.
* The package is identified as the implementation behind the educational artefact.
* No claim was added about security effectiveness, research novelty, real-agent behaviour, benchmark validity, learner outcomes or publication. The only occurrence of the word "novelty" is the **pre-existing negative disclaimer** ("makes **no research-novelty claim**"), retained deliberately.
* `__version__` and `__all__` are unchanged; the change is docstring-only, so import behaviour and the public API are identical (`PYTHONPATH=src py -c "import agentsec"` succeeds and reports `0.0.1`).

**Defect found and fixed inside this step (recorded for transparency).** The first edit of this docstring inserted the labs range as a literal `\u2026` escape sequence rather than the intended character. It was detected by inspecting the codepoints of the line (`0x5c 0x75 0x32 0x30 0x32 0x36`), corrected to plain ASCII `LAB-00 to LAB-07`, and the whole tree was then scanned for stray literal escape sequences — **0 occurrences** across all tracked and untracked non-ignored files (§9). The committed revision `54a5e61` and every other file were unaffected.

## 9. Stale-phrase verification

Searched over the tracked tree, excluding `research/` (`research/` is also reported separately):

| Phrase | Outside `research/` | Inside `research/` (historical, untouched) |
| --- | --- | --- |
| `Phase A skeleton` | **none** | `research/28`, `research/29`, `research/30`, `research/31` (5 occurrences) — records of the stale state and of its classification |
| `phase-a skeleton` (case-insensitive) | **none** | none |
| `lab material yet` | **none** | `research/31` (records the docstring defect) |
| `implementation not started` | **none** | `research/31` (records that the README did *not* contain this) |
| `planned empirical study` | **none** | `research/27` (records that the pre-Step-9 README did) |
| `skeleton` (case-insensitive) | **none** | none |
| `Phase A` (case-sensitive) | **none** | `research/01`, `research/02`, `research/03`, `research/05`, `research/06`, `research/13`, `research/14`, `research/27`, `research/28`, `research/29`, `research/30`, `research/31`, `research/32` |

**The distinction is deliberate.** Historical research audits describe earlier repository states and the phases in which those states existed (`research/13` even contains a "### Phase A — MVP" section). They are evidence, not stale documentation, and editing them to make a search clean would falsify the audit trail. They were therefore left exactly as they were: `git diff --name-only` contains no `research/` path.

A second scan covered a defect class rather than a phrase: a Python-based sweep of every tracked and untracked non-ignored text file for literal backslash-u escape sequences (`\uXXXX`) returned **0 hits**, confirming the §8 defect was the only instance and is gone.

## 10. Package metadata verification

**Method.** `setuptools` and `build` are not installed in the active interpreter and no wheel was cached, so the wheel was built with build isolation in a **copy of the project placed in a temporary directory outside the repository** (`pyproject.toml`, `src/agentsec`, `docs/development.md`, `README.md`). The repository was never used as a build directory: the build ran with `cwd` set to the temporary copy, and the resulting wheel was written to that copy's `dist/` plus pip's own cache, both outside the repository. `git status --porcelain` afterwards shows no `build/`, no `dist/` and no new file in the repository (§16). Build isolation fetched the build backend, which is the only network access performed in this step.

**Result:** `agentsec-0.0.1-py3-none-any.whl` built successfully.

| Wheel `METADATA` field | Value | Expectation | Verdict |
| --- | --- | --- | --- |
| `Metadata-Version` | `2.4` | — | — |
| `Name` | `agentsec` | unchanged | PASS |
| `Version` | `0.0.1` | **version remains 0.0.1** | PASS |
| `Summary` | `Agent Security Labs - an offline, deterministic agent-security teaching laboratory with mediated tool execution and eight reproducible labs.` | corrected description | PASS |
| `License` | `MIT` | **license remains MIT** | PASS |
| `Requires-Python` | `>=3.11` | unchanged | PASS |
| `Requires-Dist` | `pydantic>=2.6`, `jsonschema>=4.20`, `PyYAML>=6.0`; extras `dev`, `live`, `docs` | unchanged | PASS |
| Long description (from `docs/development.md`) | first line `# AgentSec Lab - development notes` | no phase label | PASS |

Stale-phrase probes against the built wheel's `METADATA` **and** against the packaged `agentsec/__init__.py` inside the wheel:

| Probe | In `METADATA` | In packaged `__init__.py` |
| --- | --- | --- |
| `Phase A` | **False** | **False** |
| `skeleton` | **False** | **False** |
| `lab material yet` | **False** | **False** |
| `not started` | **False** | **False** |
| `TBD` | **False** | **False** |

Corrected-marker probes (positive controls): the corrected `Summary` and the phrase `mediated tool execution` appear in `METADATA`; `LAB-00 to LAB-07` and `the implementation behind the Agent Security Labs` appear in the packaged `__init__.py`.

**Conclusion:** the distributed metadata carries the corrected description, version `0.0.1`, the MIT licence and the unchanged dependency set, and contains **no stale skeleton wording**. No distribution artefact was left in the repository.

## 11. pytest result

`PYTHONPATH=src py -m pytest` → **764 passed** in 11.0 s, exit 0.

Matches the expected baseline exactly. The count is unchanged because the correction is documentation/metadata only: no test was added, removed, modified, skipped or re-parametrised. The 764 figure equals the `research/31`/`research/32` baseline (695 pre-Step-13 tests + 69 in `tests/test_licensing.py`).

## 12. Labs result

`agentsec labs check` → **8/8 labs passed**:

```
LAB-00  PASS   LAB-01  PASS   LAB-02  PASS   LAB-03  PASS
LAB-04  PASS   LAB-05  PASS   LAB-06  PASS   LAB-07  PASS

Result: 8/8 labs passed
```

Exit 0, and no lab, policy, scenario or configuration file was modified.

## 13. MkDocs result

`py -m mkdocs build --strict` → **exit 0**, zero `WARNING -`/`ERROR -` lines.

`docs/development.md` is not part of the documentation site (`docs_dir: labs`), so the site content is unaffected by this change; the build was run to confirm the repository as a whole still builds strictly. The only output beyond INFO lines is the Material for MkDocs upstream advisory about MkDocs 2.0 (W11, unchanged).

## 14. Licensing result

`py scripts/check_licensing.py` → **9/9 checks passed**, exit 0:

```
  ok    LICENSE                MIT licence text present
  ok    pyproject.toml         project.license.text = 'MIT'
  ok    CITATION.cff           license: MIT
  ok    LICENSE-DATA           CC BY 4.0 notice and complete legal code (8/8 sections)
  ok    README.md              MIT and CC BY 4.0 boundary documented
  ok    third-party exclusion  stated in LICENSE-DATA and README.md
  ok    manifest               licensing/manifest.toml: schema-version 1, 36 coverage entries
  ok    licence coverage       164 file(s) accounted for (mit 118, cc-by 44, excluded 2, unlicensed 0)
  ok    unlicensed files       none recorded; every file has a licence decision
```

The licensing model was not modified in this step: `LICENSE`, `LICENSE-DATA`, `CITATION.cff`, `licensing/manifest.toml` and the guard are untouched, and the `pyproject.toml` change was confined to `description` — the `license` key still reads `{ text = "MIT" }`, which the second check re-verified.

## 15. Licensing coverage result

| Metric | Value |
| --- | --- |
| Files accounted for | **164** |
| MIT | 118 |
| CC BY 4.0 | 44 |
| Excluded | 2 (`LICENSE-DATA`, `.freebuff/project-id`) |
| Unlicensed | 0 |
| Unaccounted | **0** |
| Conflicts | **0** |
| Stale manifest patterns | **0** |
| Undecided | **0** |

The coverage mechanism was used exactly as implemented; no manifest pattern was added, removed or altered. The three modified files were already covered (`pyproject.toml` → MIT by exact path, `docs/**.md` → CC BY 4.0, `src/**` → MIT), so the change introduced no new path and required no manifest edit. The total is unchanged from `research/32` §18 (164 = the 163 files committed in `54a5e61` plus the untracked `research/32`), and after this audit is created it becomes **165** (`cc-by 45`), with the audit matched by `research/**.md`, as verified at the end of this step.

## 16. Git safety result

| Command | Output |
| --- | --- |
| `git diff --name-only` | `docs/development.md`, `pyproject.toml`, `src/agentsec/__init__.py` — the three intended files and nothing else |
| `git diff --cached --name-only` | **empty** — nothing staged |
| `git status --porcelain` | ` M docs/development.md`, ` M pyproject.toml`, ` M src/agentsec/__init__.py`, `?? research/32-post-commit-release-readiness.md`, `?? research/33-stale-metadata-cleanup-audit.md` |
| `git log -1 --oneline` | `54a5e61 final release` — **`HEAD` unchanged** |
| `git tag -l` | **0** — no tag created |
| Release | none created |
| Commit / push | none performed |
| `research/32-post-commit-release-readiness.md` | untouched, still untracked, content unchanged |

Confirmed additional safety properties:

* Only the intended metadata/documentation files are modified; the diff is `+18 / −11` across exactly three files.
* No `reset`, `checkout`, `clean`, `rebase`, `amend` or `stash` was run.
* No research audit was modified — `git diff --name-only` contains no `research/` path, and no audit file was edited in place.
* No `build/` or `dist/` directory and no generated distribution artefact exists in the repository after the wheel verification (§10).
* Generated wheel output was confined to a temporary directory outside the repository and to pip's cache.

The tree is left **unstaged and uncommitted** for manual review by the owner.

## 17. Research-boundary confirmation

| Statement | Evidence |
| --- | --- |
| This step makes **no research claim** | The change is confined to three descriptive strings; no research statement was added, altered or removed. |
| **Phase 17 remains CLOSED** | `docs/development.md`'s `## Research status (Phase 17 — CLOSED, research NO-GO)` section was not opened or edited and is unmodified in the diff. |
| **E1 remains HOLD** | No E1 classification or publication-gate statement was touched; the research records carrying them (`research/24`–`research/26`, and `research/28`–`research/32`) are unmodified. |
| No learner study was performed | No learner, student, participant, survey or assessment data exists or was created; no learner-related file was touched. |
| No novelty/effectiveness claim introduced | The new text asserts properties the code implements (mediated tool execution, deterministic reproducible runs, eight labs) and no quality, effect or novelty claim. Forbidden vocabulary was avoided throughout; the only occurrence of "novelty" is the pre-existing negative disclaimer retained in the package docstring. |
| No security-effectiveness claim introduced | The docstring's "no defences yet … observe behaviour only" limitation is retained; nothing asserts that the labs measure or improve security. |
| No benchmark/publication claim introduced | Neither new text nor the new `Summary` uses "benchmark" or references publication. |
| No previous audit modified | Verified by `git diff --name-only` and by the absence of any `research/` path in the diff. |
| No source behaviour changed | The only code-adjacent file change is a module docstring; no executable statement was altered. |

## 18. Remaining warnings

The previous step's blocker (B1) was already resolved. This step resolves the stale-metadata warning; the rest remain and are reported honestly. **This step does not declare the repository fully release-ready.**

**Resolved by this step**

| # | Warning | Status |
| --- | --- | --- |
| W2 | `pyproject.toml` description ending "(Phase A skeleton)" | **RESOLVED** — corrected `Summary`, verified in the built wheel metadata |
| W2b | Package docstring claiming "no … lab material yet" | **RESOLVED** — corrected docstring, verified inside the built wheel |
| W3/W4 | `docs/development.md` H1 "(Phase A)" and skeleton framing, also the package long description | **RESOLVED** — corrected H1 and opening, verified as the wheel's long description |

**Still open**

| # | Warning | Status after this step |
| --- | --- | --- |
| W5 | **Package is not self-contained.** `trace/validate.schema_path()` resolves `schemas/trace/trace_event.v1.schema.json` by walking up from `__file__`, so a copy of the package outside the repository raises `FileNotFoundError`; no package data is declared. | **Still present — deliberately not fixed in this step.** This is the separate future task identified in `research/32` §8 and was explicitly excluded from this cleanup. The build in §10 exercised exactly this shape: the wheel ships `agentsec/__init__.py` and the module tree, but the schema remains a repository file. |
| W6 | `CITATION.cff` has no `date-released` | unchanged; normally added at release time |
| W7 | `.freebuff/project-id` is tracked and therefore distributed | unchanged; recorded in the manifest as outside both grants |
| W8 | No automated version-drift guard across `pyproject.toml`, `__version__` and `CITATION.cff` | unchanged; all three still read `0.0.1` (§10, §11) and the wheel reports `0.0.1` |
| W9 | **The local editable-install metadata is still stale** — `src/agentsec.egg-info/PKG-INFO` records `Summary: … (Phase A skeleton).` and `License: TBD`, because that install predates both the Step 10 licence change and this cleanup | unchanged; the artefact is git-ignored and cannot enter a release, so this is a local-environment cosmetic issue. The corrected **wheel** metadata in §10 is the authoritative proof that packaged metadata is right; a local `pip install -e ".[dev]"` refresh would clear it |
| W10 | Legacy `license = { text = "MIT" }` form; no `authors`, `classifiers`, `keywords`, `urls`; no SPDX identifiers | unchanged (touching these was outside this step's scope) |
| W11 | `docs` extra unpinned (`mkdocs-material>=9`) against the MkDocs 2.0 advisory | unchanged |
| W12 | Human-judgement licensing residuals tracked in `research/28`–`research/32` | unchanged |
| W13 | `traces/*.jsonl` listed in `.gitignore` and the manifest while `traces/` does not exist | unchanged |

**Net effect on the release classification.** Three of the twelve warnings from `research/32` are now closed, including the one that appeared in the package's own `Summary` and the one that made a shipped docstring factually false. The remaining warnings — most importantly W5, the package self-containment gap — are unchanged, and none was silently dropped, downgraded or reclassified. Whether the repository should now be tagged remains the owner's decision, and this step does not assert it.

**This step's purpose was limited to removing contradictory stale package metadata and verifying that the correction did not disturb the working artefact — no commit, tag, release, staging or push was created.**

---

*End of Phase 20 — Step 15 (stale metadata cleanup). Three files corrected; all gates green on the unchanged baseline; warnings W2, W2b and W3/W4 closed; W5 and the other warnings carried forward; working tree left unstaged and uncommitted.*
