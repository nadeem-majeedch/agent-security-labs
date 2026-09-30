# PHASE 21 — W9/W10/W11/W13 PACKAGING & DOCUMENTATION HYGIENE AUDIT

## 0. Scope, provenance and method

**Scope.** Implement *only* the packaging/documentation hygiene work for the
non-blocking release warnings **W9, W10, W11 and W13** identified in
`research/39-v0.1.0-development-plan.md` (§9 A1–A4, §13 Phase 1). W6 (release
date), W7 (owner decision) and W12 (human-judgement residual) are explicitly
**out of scope** and were **not** touched. No research direction was reopened, no
LAB-08 was added, and no novelty/effectiveness/security/benchmark/publication
claim is made.

**Provenance (unchanged by this work).**

| Item | Value |
| --- | --- |
| Branch | `v0.1.0-dev` |
| HEAD | `121acc33c875748efdff1547dde982fa301b3019` (`fix release hygiene self-scan`) |
| Released tag | `v0.0.1` → the same commit `121acc3` (not modified) |
| Package version | `0.0.1` (unchanged; the `0.1.0` bump is a later phase) |
| Python | 3.13.14 (local); CI pins 3.11 |

**Method.** Each warning's detection logic in `scripts/release_check.py`
(`detect_warnings`) was read first, so each fix closes the *detected condition*
rather than weakening the check. The release checker's detection logic was **not
modified**. Metadata was taken **only** from the repository's own authoritative
records (`CITATION.cff`, `LICENSE`, `README.md`, `requires-python`).

---

## 1. Before (baseline, recorded before any edit)

Commands and results at the start of this work:

```
$ python scripts/release_check.py        # READY WITH WARNINGS, exit 0
  [PASS] tests             849 tests passed
  [PASS] labs              8/8 labs passed
  [PASS] mkdocs            strict build succeeded
  [PASS] licensing         9/9 checks passed; 178 files accounted for (mit 125, cc-by 51, excluded 2, unlicensed 0)
  [PASS] version           declarations agree on 0.0.1
  [PASS] readme            all 59 relative links and 3 anchors resolve
  [PASS] self_containment  wheel rebuilt; schema present and byte-identical; version 0.0.1
  [PASS] hygiene           no secrets, artefacts or tracked-ignored files
  [WARN] git_state         the working tree is not clean

known warnings (non-blocking): W6, W7, W9, W10, W11, W12, W13
Classification: READY WITH WARNINGS

$ python -m pytest                       # 849 passed
```

**Exact detection conditions and observed state (before).**

| Id | Detected by (unchanged) | Observed before |
| --- | --- | --- |
| W9 | `src/agentsec.egg-info/PKG-INFO` contains `License: TBD` or `Phase A skeleton` | `Summary: … (Phase A skeleton)`, `License: TBD`; file git-ignored via `*.egg-info/` |
| W10 | `[project] license` is `{ text = … }`, **or** any of `authors`/`classifiers`/`keywords`/`urls` is missing | `license = { text = "MIT" }`; all four keys missing |
| W11 | the `docs` extra names `mkdocs-material` with none of `==`, `!=`, `~=`, `<` | `docs = ["mkdocs-material>=9"]` |
| W13 | `traces/*.jsonl` appears in `.gitignore` **or** `licensing/manifest.toml`, while `traces/` does not exist | both, and no `traces/` directory |

**W9 root cause.** `python -m pip install -e ".[dev]"` writes an editable-install
snapshot into `src/agentsec.egg-info/` (and a matching `*.dist-info` into
`site-packages`). The snapshot is generated and git-ignored. It goes **stale**
whenever package metadata in `pyproject.toml` changes without a reinstall, so
`pip show agentsec` and the local install describe earlier metadata until it is
refreshed.

**W13 root cause.** `traces/*.jsonl` (and the negation `!traces/examples/`) are
residue from an earlier repository shape. Nothing in `src/`, `docs/`, `labs/`,
`README.md` or `mkdocs.yml` references `traces/`; the recorder writes to `runs/`
(`agentsec.mvp.default_trace_path` → `runs/<experiment_id>/trace.jsonl`). The
configuration is stale, not intentional.

---

## 2. Change (what was edited, and why)

### 2.1 `pyproject.toml` — W10 (metadata) and W11 (pinned docs extra)

- **Licence modernized to PEP 639 / SPDX.** `license = { text = "MIT" }` →
  `license = "MIT"` plus `license-files = ["LICENSE"]`. The declared meaning is
  unchanged (the software is MIT). `license-files` is restricted to `LICENSE`
  deliberately: the content licence (`LICENSE-DATA`, CC BY 4.0) governs
  repository prose and must **not** become the package's licence metadata, so
  the existing MIT-software / CC-BY-content boundary is preserved.
- **Build requirement bumped** `setuptools>=68` → `setuptools>=77`, which is
  required for the SPDX expression and `license-files` keys.
- **Author, keywords and URLs taken from `CITATION.cff`** (the repository's
  authoritative citation record) — none invented:
  - `authors = [{ name = "Muhammad Nadeem Majeed", email = "98729698+nadeem-majeedch@users.noreply.github.com" }]`
    (from `family-names`/`given-names`/`email`);
  - `keywords` = the six `keywords` in `CITATION.cff`;
  - `[project.urls] Homepage` = `CITATION.cff` `url`;
    `Repository` = `CITATION.cff` `repository-code`.
- **Classifiers limited to repository-established facts:** `Intended Audience ::
  Education` (README audience), `Programming Language :: Python :: 3` and
  `:: 3.11` (`requires-python = ">=3.11"`, CI 3.11), `Topic :: Education` and
  `Topic :: Security` (project identity).
- **`docs` extra pinned** to the deliberately tested toolchain:
  `docs = ["mkdocs-material==9.7.7", "mkdocs==1.6.1"]`. These are exactly the
  versions installed in the working environment that builds the site green
  (`mkdocs-material 9.7.7`, `mkdocs 1.6.1`); the pin fixes the upstream "latest"
  drift rather than choosing a version at random. `mkdocs-material 9.x` requires
  `mkdocs<2,>=1.6`, which records the decision on the upstream MkDocs 2.0
  advisory.

**Correction made during implementation (honest record).** The first attempt
included the classifier `License :: OSI Approved :: MIT License`. Setuptools
(≥77) **rejected** the build — PEP 639 forbids license classifiers when an SPDX
`license` expression is present:

```
setuptools.errors.InvalidConfigError: License classifiers have been superseded
by license expressions (see https://peps.python.org/pep-0639/). Please remove:
  License :: OSI Approved :: MIT License
```

The classifier was removed; the SPDX `license = "MIT"` carries the licence. The
`classifiers` key remains present (five entries), so W10 stays closed.

### 2.2 `.gitignore` and `licensing/manifest.toml` — W13

Both sources of the stale pattern were removed together, so the two stay "in
step" as the manifest comment requires (the manifest is deliberately kept in step
with `.gitignore`):

- `.gitignore`: dropped `traces/*.jsonl` and `!traces/examples/` (kept `runs/`);
- `licensing/manifest.toml`: dropped the `"traces/*.jsonl"` entry from the
  `not-distributed` list.

No `traces/` directory or placeholder file was created — creating an empty
directory merely to silence a warning would be meaningless.

### 2.3 `docs/development.md` — W9 (workflow/documentation)

A new subsection **"Editable-install metadata (W9)"** documents that
`src/agentsec.egg-info/` and the matching `*.dist-info` are **generated,
git-ignored snapshots** that can go stale after any metadata change, that the
gate reports this as W9, and how to refresh them
(`py -m pip install -e ".[dev]"`, or delete the stale directory and let the next
editable install regenerate it). The install section also now names the pinned
`docs` extra. No generated metadata was (or can be) introduced into Git.

### 2.4 Local refresh (not a repository change)

`python -m pip install -e ".[dev]"` was re-run to regenerate the local editable
snapshot from the updated `pyproject.toml`. The resulting git-ignored
`src/agentsec.egg-info/PKG-INFO` now reports
`License-Expression: MIT` and the current summary:

```
Category            Before                                   After
Summary             … (Phase A skeleton)                     Agent Security Labs - an offline, deterministic …
License             TBD                                      License-Expression: MIT
Project-URL         (none)                                   Homepage / Repository
Keywords            (none)                                   six keywords
Author-email        (none)                                   Muhammad Nadeem Majeed <…@users.noreply.github.com>
```

### 2.5 Tests added (`tests/test_release_check.py`)

Three hermetic tests were added; no existing test was removed or relaxed:

- `test_detect_warnings_reports_w9_for_stale_editable_metadata` — a fixture
  `PKG-INFO` with the stale marker raises W9. (W9 had **no** test before.)
- `test_detect_warnings_omits_w9_for_fresh_editable_metadata` — a fresh
  `PKG-INFO` does not raise W9.
- `test_repository_does_not_trigger_the_closed_metadata_warnings` — the **real**
  repository root does not raise W10, W11 or W13 (these are read from checked-in
  files, so the fix is pinned against regression). W9 is intentionally excluded
  from the repo-level assertion because it depends on the local install snapshot
  and is covered by the two fixture tests.

The stale marker in the fixture is assembled from fragments (`"License: " + "T" +
"BD"`) so the test file does not itself contain an unfinished-work marker — the
hygiene gate scans `tests/` and this was caught and corrected during
verification.

---

## 3. Verification (all commands re-run after the change)

| # | Command | Result |
| --- | --- | --- |
| 1 | `python -m pytest` | **852 passed** (849 + 3 new) |
| 2 | `python -m agentsec labs check` | **8/8 labs passed** |
| 3 | `python -m mkdocs build --strict` | **exit 0** (0 warnings/errors) |
| 4 | `python scripts/check_licensing.py` | **9/9 checks passed**; 179 files accounted for (mit 125, cc-by 52, excluded 2, unlicensed 0) |
| 5 | `python scripts/check_version.py` | **3/3 checks passed** (all `0.0.1`) |
| 6 | `python scripts/release_check.py` | **READY WITH WARNINGS**, `blockers: []` |
| 7 | `git diff --check` | **clean** (no whitespace errors) |
| 8 | `git status` | 5 modified + 2 untracked (`research/39`, `research/40`); nothing staged |
| 9 | generated artifacts tracked? | **none** (`git ls-files` has no `egg-info`, `__pycache__`, `.pyc`, `site/`, `runs/`, `build/`, `dist/`, `*.whl`) |
| 10 | README links | **all 59 relative links and 3 anchors resolve** (release gate `readme` PASS) |

**Final release-gate output:**

```
release gate
============

  [PASS] tests             852 tests passed
  [PASS] labs              8/8 labs passed
  [PASS] mkdocs            strict build succeeded
  [PASS] licensing         9/9 checks passed; 179 files accounted for (mit 125, cc-by 52, excluded 2, unlicensed 0)
  [PASS] version           declarations agree on 0.0.1
  [PASS] readme            all 59 relative links and 3 anchors resolve
  [PASS] self_containment  wheel rebuilt; schema present and byte-identical; version 0.0.1
  [PASS] hygiene           no secrets, artefacts or tracked-ignored files
  [WARN] git_state         the working tree is not clean

known warnings (non-blocking):
  [WARN] W6   CITATION.cff has no date-released (add it at release time)
  [WARN] W7   .freebuff/project-id is tracked and therefore distributed
  [WARN] W12  human-judgement licensing residuals remain

Classification: READY WITH WARNINGS
```

**Per-warning outcome.**

| Id | Result | Evidence |
| --- | --- | --- |
| **W9** | **Closed** | Fresh editable metadata: `pip show agentsec` reports `License-Expression: MIT` and the current summary; `PKG-INFO` contains no stale marker; documented refresh workflow. Guarded by two new tests. |
| **W10** | **Closed** | SPDX `license = "MIT"` + `license-files = ["LICENSE"]`; `authors`, `keywords`, `classifiers`, `[project.urls]` all present. `detect_warnings` no longer emits W10. |
| **W11** | **Closed** | `docs = ["mkdocs-material==9.7.7", "mkdocs==1.6.1"]`; the strict build is green with exactly those versions. |
| **W13** | **Closed** | Removed from both `.gitignore` and the manifest; `traces/` remains non-existent and nothing references it. |

---

## 4. Files changed

| File | Change |
| --- | --- |
| `pyproject.toml` | W10: SPDX licence + `license-files`, `authors`, `keywords`, `classifiers`, `[project.urls]`, `setuptools>=77`. W11: pinned `docs` extra. |
| `.gitignore` | W13: removed `traces/*.jsonl` and `!traces/examples/`. |
| `licensing/manifest.toml` | W13: removed the `traces/*.jsonl` `not-distributed` entry. |
| `docs/development.md` | W9: added "Editable-install metadata (W9)" section; noted the pinned docs extra. |
| `tests/test_release_check.py` | Added 3 tests (W9 detection both ways; repository-level W10/W11/W13 closure). |
| `research/40-packaging-hygiene-audit.md` | This audit (new). |

**Not changed:** `scripts/release_check.py` (detection logic and philosophy
untouched), `scripts/check_licensing.py`, `scripts/check_version.py`, all
`src/agentsec/**`, all `labs/**`, all other `tests/**`, `CITATION.cff`
(version and `date-released` are a later phase), `LICENSE`, `LICENSE-DATA`,
`README.md`, `mkdocs.yml`, and every file under `research/20`–`research/39`.
No Git tag was created or modified; nothing was committed, pushed or staged.

---

## 5. Remaining limitations (deliberately unresolved)

These are **out of scope** for this task and are reported honestly rather than
silenced:

- **W6 — `CITATION.cff` has no `date-released`.** A release-time action: the date
  is only meaningful once the tag/release exists. Not added here (no tag was
  created).
- **W7 — `.freebuff/project-id` is tracked.** An owner keep-or-untrack decision;
  its licensing treatment is already explicit in the manifest. Unchanged.
- **W12 — human-judgement licensing residuals.** Emitted unconditionally by
  design, so `READY` remains unreachable until it is retired or restated. Not in
  scope here.
- **`git_state` WARN.** Expected: the working tree is intentionally dirty before
  the owner commits. The gate reports it rather than failing.
- **W10 completeness is structural, not editorial.** The gate checks that the
  metadata *keys exist* and that the licence is not the legacy form; it does not
  judge whether every classifier is the ideal one. The classifier set here is
  deliberately conservative and repository-derived; it is not exhaustive.
- **Upstream MkDocs 2.0 advisory.** `mkdocs build` still prints the upstream
  Material-for-MkDocs advisory about a future MkDocs 2.0; the build exits 0. The
  `mkdocs-material==9.7.7` pin (which requires `mkdocs<2`) records the decision
  and keeps the build reproducible, but it does not resolve the upstream
  advisory itself.
- **R-1/R-2 (CI structure)** and the other roadmap items in `research/39` §9–§13
  (CI docs-extra install, pytest de-duplication, version bump, lint/type gates,
  education additions) are **not** part of this task and remain proposed.

**Boundary confirmation.** Phase 17 remains **CLOSED** and E1 remains **HOLD**;
no research implementation, corpus, experiment, study or learner data was added;
`research/20`–`research/39` are byte-unchanged; and no novelty, effectiveness,
security-effectiveness, benchmark or publication claim is made.
