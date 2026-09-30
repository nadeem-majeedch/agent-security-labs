# PHASE 20 — STEP 17: VERSION-DRIFT GUARD AUDIT (W8, W6)

**Status: PASS — W8 = CLOSED (mechanically); W6 = OPEN, documented as awaiting the real release date.**

A single authoritative version now governs the repository, and a stdlib-only, offline, read-only checker fails the build if the three declarations ever disagree. The guard was verified end to end: the repository passes, each declaration was made to fail on its own in a temporary fixture outside the repository, and every malformed/missing case produces a clear, actionable diagnostic naming the expected and the observed value. `CITATION.cff` still has no `date-released`, because there is still no tagged release — that warning is left explicitly open rather than closed with an invented date.

Scope: version-declaration consistency only. Nothing was committed, pushed, tagged, released or staged. Phase 17 remains **CLOSED**. **E1 remains HOLD**. No research claim is made, no study was performed, no learner data was touched, and no previous audit was modified.

---

## 1. Status

| Item | Value |
| --- | --- |
| Step | Phase 20 — Step 17, version-drift guard (W8, handle W6) |
| Outcome | **PASS — W8 CLOSED; W6 OPEN and recorded** |
| Defect closed | nothing in the repository tied `pyproject.toml`'s version to `__version__` or to `CITATION.cff`; `tests/labs/test_lab00.py` only asserted `__version__` was a non-empty string |
| Mechanism now | `scripts/check_version.py`, run in CI before `pip install` |
| Files changed | **2 modified, 2 added** (1 of the added is this audit) |
| Diff | `+21 / −6` across the 2 modified files |
| New tests | **26** (`tests/test_version.py`), plus 1 parametrisation-driven addition from the new test path |
| pytest | **800 passed** (was 773) |
| labs / MkDocs / licensing / version | **8/8** · **exit 0** · **9/9** · **3/3** |
| Licence coverage | **172 files** (mit 123, cc-by 47, excluded 2, unlicensed 0); 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| Staged / committed / tagged | **none** |

## 2. Starting repository state

Inspected before any change (this step's §1 instruction):

| Item | Value |
| --- | --- |
| `HEAD` | `a193076e5b5cf92f1fd387b54ed008fc306b65dc` (`a193076` "Phase 20 step 16 complete") |
| Branch | `main` |
| Tags | 0 |
| Working tree at start | **clean** — `git status --porcelain` empty |
| Tracked files | 169 |
| Untracked (non-ignored) | 0 |
| Baseline gates | pytest 773 passed · labs 8/8 · MkDocs strict exit 0 · licensing 9/9 |
| Baseline classification | READY WITH WARNINGS (`research/32`), W5 closed in `research/34` |

`HEAD` is unchanged at the end of this step (§13).

## 3. Current version declarations (verified from the repository)

The version was read out of the tree rather than assumed. `0.0.1` is declared in four places; the fourth is prose, not an independent declaration:

| Location | Line | Declared value | Kind |
| --- | --- | --- | --- |
| `pyproject.toml` | 7 | `version = "0.0.1"` | **authoritative machine declaration** |
| `src/agentsec/__init__.py` | 60 | `__version__ = "0.0.1"` | runtime `str` declaration |
| `CITATION.cff` | 5 | `version: "0.0.1"` | citation metadata declaration |
| `README.md` | 339 | “version 0.0.1” (citation block) | **prose sentence**, not a declaration |

`CITATION.cff` correctly separates its schema version (`cff-version: 1.2.0`) from the software `version:`, and `mkdocs.yml` and `docs/development.md` carry no release version at all. No source contradicts another; the three machine declarations already agree, which is why W8 is a *missing guard* rather than a present inconsistency.

## 4. Authoritative-source decision

**`pyproject.toml`'s `[project] version` is the single authoritative version.** The other two must equal it:

```
pyproject.toml  [project] version   ── authoritative (what the build stamps)
        │
        ├──  src/agentsec/__init__.py  __version__     must equal
        └──  CITATION.cff              version:        must equal
```

Rationale:

* It is already the value the build backend stamps into the distribution (confirmed in the wheel metadata of `research/33` §10 and `research/34` §11), so it is the natural source of truth rather than a new invention.
* The brief forbids introducing a *fourth independent* version source, and none was introduced: the guard reads the three existing declarations and compares them, it does not create a new file to hold the number.
* The **README citation block is deliberately excluded** from the guard. It is a human-written sentence in prose, not a machine declaration; parsing it textually would be fragile and would turn wording into a build failure. The same reasoning already applies to the licensing guard, which checks *markers* in the README rather than values. The README's version is kept in step by the citation-prose review the README already requires.

## 5. Implementation — `scripts/check_version.py`

Standard library only (`argparse`, `ast`, `dataclasses`, `pathlib`, `sys`, `tomllib`), offline, read-only, no subprocess, no Git, no network, no installation. It parses rather than matching text:

| Declaration | Parsed with | Why not text matching |
| --- | --- | --- |
| `pyproject.toml` `[project] version` | `tomllib` | a `version =` string in a comment or another table cannot masquerade as the project version |
| `src/agentsec/__init__.py` `__version__` | `ast` (module-body `Assign`/`AnnAssign` to the name `__version__`) | only a real module-level assignment counts, and its value must be a **string literal** |
| `CITATION.cff` `version:` | top-level (column-zero) key line scan | no stdlib YAML parser exists; matching only unindented keys is what makes it a *top-level* read |

Structure and report order (mirroring `scripts/check_licensing.py`, so the two guards read the same way in CI):

```
version consistency check
=========================

  ok    pyproject.toml       project.version = '0.0.1' (authoritative)
  ok    agentsec.__version__ declares '0.0.1', matching pyproject.toml
  ok    CITATION.cff         declares '0.0.1', matching pyproject.toml

Result: 3/3 checks passed
```

* Exit `0` when all three agree, `1` otherwise.
* Each failure line **names the exact source**, states the **expected** and the **observed** value, and says how to fix it: e.g. `agentsec.__version__ declares '0.0.2' but pyproject.toml declares '0.0.1'; set src/agentsec/__init__.py to '0.0.1' (or update pyproject.toml)`.
* When the authoritative declaration itself cannot be read, its own line reports why, and the two dependent lines say the expected value is **unavailable** and repeat the reason — the report never silently claims agreement.
* Public, testable API: `CheckResult`, `read_pyproject_version`, `read_init_version`, `read_citation_version`, `authoritative`, `check_pyproject`, `check_init`, `check_citation`, `CHECKS`, `run_checks`, `format_report`, `main`.
* The script **modifies nothing**; it only calls `Path.read_text`.

## 6. Test design — `tests/test_version.py`

26 tests, following the `tests/test_licensing.py` conventions (guard imported with `importlib.util.spec_from_file_location`; failure cases run against minimal `tmp_path` fixtures, never against the checked-in files).

| Group | Tests | What they pin |
| --- | --- | --- |
| Contract holds for the real repository | `test_current_repository_satisfies_the_version_contract`, `test_guard_reports_every_check_passing` | report order `pyproject.toml`, `agentsec.__version__`, `CITATION.cff`; `main` exits 0 and prints `3/3 checks passed` |
| Each declaration can fail independently | `test_mismatched_dunder_version_fails`, `test_mismatched_citation_version_fails`, `test_mismatched_pyproject_version_fails` | each mismatch fails; the detail carries both `'0.0.2'` (observed) and `'0.0.1'` (expected) and names `pyproject.toml` |
| Accepted spellings | `test_a_quoting_style_in_citation_still_agrees`, `test_dunder_version_may_be_annotated`, `test_valid_fixture_passes` | quoted/unquoted CFF value and `__version__: str = "…"` are accepted |
| Malformed / missing declarations | `test_a_missing_pyproject_makes_the_dependents_fail`, `test_a_missing_init_file_fails`, `test_a_missing_citation_file_fails`, `test_pyproject_that_is_not_toml_is_reported`, `test_pyproject_without_a_version_is_reported`, `test_pyproject_version_must_be_a_string`, `test_an_empty_pyproject_version_is_reported`, `test_init_without_a_version_is_reported`, `test_init_version_must_be_a_string_literal`, `test_a_nested_dunder_version_is_not_the_module_version`, `test_a_missing_citation_version_is_reported`, `test_an_empty_citation_version_is_reported`, `test_a_nested_citation_version_is_not_the_document_version` | each fails **clearly**, and a nested `__version__`/`version:` (inside a function or under `preferred-citation:`) is correctly **not** treated as the declaration |
| Failure report | `test_failing_run_explains_itself_and_exits_nonzero` | `main` exits 1, prints `FAIL`, the source name and `failed` |
| Offline / read-only / dependency-free | `test_guard_imports_only_the_standard_library`, `test_guard_does_not_fetch_or_write_anything`, `test_guard_does_not_read_git_or_open_a_connection`, `test_guard_reports_no_drift_when_run_from_the_repository` | imports ⊆ stdlib; source contains no `urlopen`/`urlretrieve`/`urllib`/`requests`/`subprocess`, no `write_text`/`write_bytes`/`open(`/`mkdir`, no `rev-parse`/`describe`/`popen`/`.git/index`/`refs/heads`/`connect(`; running against the repository leaves all three files byte-identical |

**Architecture-test accounting.** `tests/test_architecture.py` parametrises `test_no_banned_dependency_in_tests` over every `tests/**/*.py`, so the new `tests/test_version.py` adds exactly one case (it imports only `ast`, `importlib.util`, `sys`, `pathlib`, `pytest`). The new script lives under `scripts/`, which that suite does not scan. The new test file contains no `http`/`https`/`socket` literal, so `test_tests_do_not_reference_the_network` stays green.

## 7. CI placement

`.github/workflows/ci.yml`, job **`tests and lab self-check`** (name unchanged), with the version check inserted **after the licence check and before `pip install`**, because the guard is stdlib-only and must fail fast:

```text
Check out the repository
Set up Python 3.11
Check the licence metadata and coverage   → python scripts/check_licensing.py
Check the declared version is consistent   → python scripts/check_version.py   ← added
Install the package (with dev extras)      → pip install -e ".[dev]"
Run the test suite                         → python -m pytest
Run the lab self-check                     → agentsec labs check
```

The existing pytest and lab-check commands are untouched, and the workflow's header comment was extended to describe the version step in the same terms as the licence step. Diff: **+9 lines** in `ci.yml`, no other workflow touched (`docs.yml` unmodified).

## 8. W8 resolution

**W8 — no automated version-drift guard — is CLOSED.**

* The three machine declarations are now compared mechanically on every push and pull request, **before dependency installation**, so drift cannot reach a release.
* The guard reads the files from the working tree: it needs no installed package, no Git and no network, so it runs on the bare checkout exactly as the licensing guard does.
* It is not a one-off assertion: 26 tests pin the contract from both directions, including a test that a *malformed* declaration fails and a test that running the guard leaves the inspected files byte-identical.

**Residual honesty.** The guard compares the declarations; it cannot know which one “should” be right when they disagree, so it follows the documented convention (`pyproject.toml` wins) and its diagnostic offers both fixes. It also deliberately does not check the README citation prose (§4). Both limits are recorded rather than implied away.

## 9. W6 status and why it was not closed

**W6 — `CITATION.cff` has no `date-released` — remains OPEN.**

* A `date-released` states the date a release was made. There is **no tag and no release** (`git tag` lists 0), so any value written today would be an invented date.
* The brief is explicit: do not manufacture a date, and do not create a release. Accordingly no `date-released` was added and `CITATION.cff` was **not modified at all**.
* Closing W6 is therefore a **release-time action**, to be performed when the owner creates the `v0.0.1` tag/release — adding `date-released` with the actual release date at that moment. The guard does not read tags (§5, §10), so it cannot and does not attempt to derive this date.
* No release convention document was introduced either, because the repository has no tag convention to document yet; adding one would be inventing process rather than recording it. The recommendation to add `date-released` at tag time is carried in §15 and §16.

## 10. Malformed / mismatch failure demonstrations

Run against temporary fixtures **outside the repository** with the current guard, capturing real output. Exit code and the single failing line are quoted.

**Mismatched `__version__`** (`__version__ = "0.0.2"`, others `0.0.1`) → exit **1**:

```
  ok    pyproject.toml       project.version = '0.0.1' (authoritative)
  FAIL  agentsec.__version__ declares '0.0.2' but pyproject.toml declares '0.0.1'; set src/agentsec/__init__.py to '0.0.1' (or update pyproject.toml)
  ok    CITATION.cff         declares '0.0.1', matching pyproject.toml
Result: 1 of 3 checks failed (2 passed)
```

**Mismatched `CITATION.cff`** (`version: "0.0.2"`, others `0.0.1`) → exit **1**:

```
  FAIL  CITATION.cff         declares '0.0.2' but pyproject.toml declares '0.0.1'; set CITATION.cff to '0.0.1' (or update pyproject.toml)
Result: 1 of 3 checks failed (2 passed)
```

**Mismatched `pyproject.toml`** (source of truth `0.0.2`, others `0.0.1`) → exit **1**, both dependents fail:

```
  ok    pyproject.toml       project.version = '0.0.2' (authoritative)
  FAIL  agentsec.__version__ declares '0.0.1' but pyproject.toml declares '0.0.2'; set src/agentsec/__init__.py to '0.0.2' (or update pyproject.toml)
  FAIL  CITATION.cff         declares '0.0.1' but pyproject.toml declares '0.0.2'; set CITATION.cff to '0.0.2' (or update pyproject.toml)
Result: 2 of 3 checks failed (1 passed)
```

**Malformed `pyproject.toml`** (unterminated table) → exit **1**, every line states the reason:

```
  FAIL  pyproject.toml       is not valid TOML: Expected ']' at the end of a table declaration (at line 1, column 9); pyproject.toml holds the authoritative project version
  FAIL  agentsec.__version__ found '0.0.1' but the authoritative version is unavailable because pyproject.toml is not valid TOML: …
  FAIL  CITATION.cff         found '0.0.1' but the authoritative version is unavailable because pyproject.toml is not valid TOML: …
Result: 3 of 3 checks failed (0 passed)
```

**Missing `pyproject.toml`** → exit **1**:

```
  FAIL  pyproject.toml       required file pyproject.toml is missing (expected pyproject.toml)
  FAIL  agentsec.__version__ found '0.0.1' but the authoritative version is unavailable because pyproject.toml is missing
  FAIL  CITATION.cff         found '0.0.1' but the authoritative version is unavailable because pyproject.toml is missing
Result: 3 of 3 checks failed (0 passed)
```

Every case exits non-zero, names the disagreeing source, and states both the expected and the observed value. The matching test for each case is listed in §6.

## 11. Offline / read-only evidence

| Property | Evidence |
| --- | --- |
| Standard library only | `test_guard_imports_only_the_standard_library` parses the guard's AST and asserts the imported set ⊆ `{__future__, argparse, ast, dataclasses, pathlib, sys, tomllib}` — passed |
| No network | guard source contains none of `urlopen`, `urlretrieve`, `urllib`, `requests`, `connect(` — asserted by test, passed |
| No child process | guard source contains no `subprocess`/`popen` — asserted by test, passed |
| No reference to Git | guard source contains no `rev-parse`, `describe`, `.git/index`, `refs/heads`; the version is read from files only — asserted by test, passed |
| No writes | guard source contains none of `write_text`, `write_bytes`, `open(`, `mkdir`; it only calls `Path.read_text` — asserted by test, passed |
| Read-only in practice | `test_guard_reports_no_drift_when_run_from_the_repository` snapshots `pyproject.toml`, `src/agentsec/__init__.py` and `CITATION.cff` as bytes, runs `main` against the repository, and asserts the bytes are unchanged — passed |

The repository was also left untouched by the demonstrations in §10, which ran entirely in `tempfile.mkdtemp()` directories outside the working tree.

## 12. All verification results

Re-run at this revision:

| Gate | Command | Result |
| --- | --- | --- |
| Test suite | `PYTHONPATH=src py -m pytest` | **800 passed**, exit 0 (was 773; **+26** new tests, **+1** architecture parametrisation) |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed** (LAB-00 … LAB-07), exit 0 |
| Documentation build | `py -m mkdocs build --strict` | **exit 0**, **0** `WARNING -`/`ERROR -` lines; the only advisory is the Material for MkDocs upstream note about MkDocs 2.0 (W11, unchanged) |
| Licence metadata + coverage | `py scripts/check_licensing.py` | **9/9 checks passed**, exit 0 |
| Version consistency | `py scripts/check_version.py` | **3/3 checks passed**, exit 0 |
| README links/anchors | relative-link and heading-slug scan | **58/58** relative links resolve, **3/3** in-document anchors resolve |
| Licence coverage | `check_licensing.py` | **172 files** accounted for (mit 123, cc-by 47, excluded 2, unlicensed 0); 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| New files covered by the manifest | pattern check | `scripts/check_version.py` → MIT (`scripts/**`), `tests/test_version.py` → MIT (`tests/**`), `research/35-….md` → CC BY 4.0 (`research/**.md`) — **no manifest change needed** |
| Stale version statements | `git grep` | README's verification table no longer claims the old test count; the only `0.0.1` sites outside `research/` are the four intended ones (§3) |
| Literal escape sequences | tree scan for `\uXXXX` | **1 hit**, and it is the *prose description* of the old Step 15 defect inside `research/33` (a historical audit, not to be modified); **0** in code |
| Build artefacts | `ls -d build dist` | **none** — no `build/`, no `dist/` in the repository |

## 13. Exact files changed

Modified (`git diff --stat`, `+21 / −6`):

| File | Change |
| --- | --- |
| `.github/workflows/ci.yml` | +9 lines: the version check step, inserted after the licence step and before the install; the header comment extended. Job name `tests and lab self-check` and the pytest/lab commands unchanged. |
| `README.md` | Verification table: the **stale “719 tests pass”** row corrected to **800**, and a **Version consistency · `py scripts/check_version.py` · 3/3 checks pass** row added; the CI paragraph updated to mention the version check; the licensing section gained two sentences describing the guard. |

Added:

| File | Purpose |
| --- | --- |
| `scripts/check_version.py` | The guard (§5). |
| `tests/test_version.py` | The 26 tests (§6). |
| `research/35-version-drift-guard-audit.md` | This audit. |

**Not modified:** `LICENSE`, `LICENSE-DATA`, `CITATION.cff` (W6 left open by design), `licensing/manifest.toml`, `pyproject.toml` (the version was **not** changed), `src/agentsec/__init__.py`, `docs/development.md`, every lab/policy/scenario/schema/config file, `scripts/check_licensing.py`, every existing test, and every research audit `research/20`–`research/34`. No dependency was added; no pre-commit framework was introduced.

## 14. Git safety confirmation

```
$ git status --porcelain
 M .github/workflows/ci.yml
 M README.md
?? scripts/check_version.py
?? tests/test_version.py

$ git diff --cached --name-only
(empty)

$ git rev-parse --short HEAD
a193076

$ git tag --list
(no tags)
```

* `HEAD` remains `a193076e5b5cf92f1fd387b54ed008fc306b65dc`; **no commit, no push, no tag, no GitHub release**.
* **Nothing staged.** The working tree is left unstaged and uncommitted for the owner.
* Only the intended files changed: the two modifications of §13, the two new files, and this audit.
* No `reset`, `checkout`, `clean`, `rebase`, `amend` or `stash` was run; no previous commit was rewritten.
* No build artefact was left behind: no `build/`, no `dist/`, and `git status` shows no unexpected file. The §10 demonstrations ran entirely in temporary directories outside the repository.
* No research audit was modified — `git diff --name-only` contains no `research/` path, and `research/20`–`research/34` are byte-unchanged.

## 15. Research-boundary confirmation

| Statement | Evidence |
| --- | --- |
| Phase 17 remains **CLOSED** | `docs/development.md`'s `## Research status (Phase 17 — CLOSED, research NO-GO)` section was not opened or edited; `docs/development.md` is not in the diff. |
| **E1 remains HOLD** | No E1 classification or publication-gate statement was touched; `research/24`–`research/26` and `research/28`–`research/34` are unmodified. |
| No research direction reopened | No research record was created or edited; the only new Markdown file is this audit. |
| No literature search | None performed. |
| No novelty claim | The change is version bookkeeping; no statement about the artefact's novelty, originality or significance was added. |
| No effectiveness claim | Nothing asserts learning, security or performance effectiveness. |
| No learner study / learner data | None performed or created; no learner-related file exists or was touched. |
| No benchmark claim | Nothing describes the artefact as a benchmark or as producing measurements. |
| No paper drafted | No manuscript or submission artefact was created. |
| No previous audit modified | `git diff --name-only` contains no `research/` path; `research/20`–`research/34` are untouched. |

## 16. Remaining warnings and next step

§15 of `research/34` listed eight open warnings. This step closes **one** of them:

| # | Warning | Status after this step |
| --- | --- | --- |
| **W8** | no automated version-drift guard | **CLOSED** — `scripts/check_version.py`, run in CI before install, with 26 tests (§5–§8) |
| W6 | `CITATION.cff` has no `date-released` | **OPEN** — no tag/release exists; add the real date when the `v0.0.1` tag is created (§9) |
| W7 | `.freebuff/project-id` is tracked and therefore distributed | open — recorded in the manifest as outside both grants |
| W9 | local editable-install metadata is stale (`License: TBD`, old `Summary` in git-ignored `src/agentsec.egg-info/`) | open — local only; a `pip install -e ".[dev]"` refresh clears it |
| W10 | legacy `license = { text = "MIT" }` form; no `authors`, `classifiers`, `keywords`, `urls`; no SPDX identifiers | open |
| W11 | `docs` extra unpinned (`mkdocs-material>=9`) against the MkDocs 2.0 advisory | open |
| W12 | human-judgement licensing residuals tracked in `research/28`–`research/34` | open |
| W13 | `traces/*.jsonl` in `.gitignore`/manifest while `traces/` does not exist | open |

W2–W5 remain closed as recorded in `research/33` and `research/34`.

**Next recommended step.** Two candidates, in order:

1. **Owner action (out of agent scope): tag and release `v0.0.1`, then close W6** by adding `date-released` to `CITATION.cff` with the actual date. This is the only way to close W6 legitimately.
2. **Next hardening step: W10 / W13**, the remaining pre-tag packaging-metadata and manifest-hygiene items, or W11 (pin the `docs` extra and record the MkDocs 2.0 decision) — all optional, none blocking a release on their own.

The repository should not be described as “release-ready” by this step: **eight warnings remain open**, and this step closes only W8 and documents W6.

---

*End of Phase 20 — Step 17. W8 CLOSED on reproduced-mismatch / verified-consistency evidence with an offline, read-only, stdlib-only guard wired into CI before the install; W6 left OPEN and documented as awaiting the real release date. Seven warnings remain open. No staging, commit, push, tag or release was performed.*
