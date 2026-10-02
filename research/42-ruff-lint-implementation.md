# PHASE 21 — RUFF LINT GATE IMPLEMENTATION (B4.1)

*Implementation record for the first quality-gate item identified in
`research/41-quality-gates-audit.md` (§5 item 1, §8 decisions 1–3): the Ruff
lint gate. Only Ruff lint was implemented. Nothing was committed, pushed,
tagged or version-bumped; the Phase 17 freeze and the `v0.0.1` release are
untouched.*

## 0. Scope

This step implements **only** the Ruff lint gate:

* Ruff's **default** rule set — `E4`, `E7`, `E9`, `F`;
* a pinned Ruff development dependency;
* the four `F401` findings fixed;
* one new, independent `lint` CI job.

**Explicitly NOT implemented in this step:**

* **Black — NOT implemented.** No formatter was added, configured or run.
* **isort — NOT implemented.** No import-sorting tool was added.
* **mypy — NOT implemented.** No type checker was added or configured.
* **coverage — NOT implemented.** No coverage tool was added; no threshold set.
* No broad Ruff rule set (`E,W,F,I,B,UP,SIM,C4,ARG,BLE`) was enabled.

`scripts/release_check.py` was **NOT changed** (see §7), and
`.github/workflows/docs.yml` was **NOT changed**.

## 1. Starting state (from research/41)

`research/41` recorded, as the audit baseline immediately before this step:

* No lint configuration existed anywhere (`[tool.ruff]`, `ruff.toml`, …).
* No linter/type-checker/coverage tool was a declared dependency; `dev` was
  `["pytest>=7.4"]` only.
* Ruff default rule set (`E4,E7,E9,F`) reported **4 findings, all `F401`**:

  ```
  tests/eval/test_eval.py:10:35            F401  `agentsec.agent.AgentConfig` imported but unused
  tests/schema/test_packaged_schema.py:33  F401  `agentsec.trace.validate.validate_event` imported but unused
  tests/test_release_check.py:21:8         F401  `pytest` imported but unused
  tests/test_version.py:21:8               F401  `pytest` imported but unused
  ```

* The broader rule set `E,W,F,I,B,UP,SIM,C4,ARG,BLE` reported **292** findings —
  confirming the decision to start with Ruff defaults only.

The working tree at the start of this step contained the **uncommitted
two-job** `ci.yml` from the previous step (`compatibility` +
`release-readiness`, `git diff --stat`: 1 file, +59/−29). This step added the
`lint` job **on top of** that version; it did not revert it.

## 2. Ruff version selected

**`ruff==0.12.0`** — the exact version identified in `research/41` §3 as the only
Ruff available for inspection on this machine (Anaconda base, CPython 3.13.9).
It is pinned with `==`, matching the repository's existing dependency-pinning
discipline (the `docs` extra, W11): an unpinned linter can flip a green CI to
red on an upstream release.

## 3. Exact `pyproject.toml` changes

Version remained **`0.0.1`** (unchanged).

**(a) Pinned dev dependency** — `[project.optional-dependencies]`:

```diff
 dev = [
     "pytest>=7.4",
+    # Pinned so the lint gate cannot flip red on an upstream Ruff release (the
+    # same version-drift discipline as the pinned `docs` extra below, W11).
+    "ruff==0.12.0",
 ]
```

**(b) Minimal lint configuration** — new `[tool.ruff.lint]` section, default
rule set only:

```toml
# Lint gate (research/41, research/42). Ruff's *default* rule set only:
# E4 = pycodestyle imports, E7 = pycodestyle statements, E9 = pycodestyle
# runtime and F = Pyflakes. Formatting (E5 line length), import sorting (I) and
# the broader families (W, B, UP, SIM, C4, ARG, BLE) are deliberately not
# enabled here: those are a large, separately reviewed cleanup, not this gate.
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

No `line-length`, no `[tool.ruff.format]`, no `[tool.ruff.lint.isort]`, no
per-file ignores were added. Ruff discovers this configuration from
`pyproject.toml`, so **no new file** was created and no
`licensing/manifest.toml` entry was needed (the reason `research/41` §7 gave
for preferring `pyproject.toml` configuration).

> **Note on section name.** `research/41` illustrated the config as
> `[tool.ruff]` with a top-level `select`. Ruff 0.12.0 emits a deprecation
> warning for that form and recommends the `[tool.ruff.lint]` table
> (`'select' -> 'lint.select'`). This implementation uses the non-deprecated
> `[tool.ruff.lint]` table so the gate runs warning-free; the semantics are
> unchanged.

## 4. Exact `F401` fixes

Exactly four unused imports were removed. No other cleanup, no
opportunistic refactoring, no formatting change.

| File | Removed |
| --- | --- |
| `tests/eval/test_eval.py` | `AgentConfig` from `from agentsec.agent import Agent, AgentConfig` |
| `tests/schema/test_packaged_schema.py` | `validate_event` from the `agentsec.trace.validate` import block |
| `tests/test_release_check.py` | the `import pytest` line (file uses CRLF; ending preserved) |
| `tests/test_version.py` | the `import pytest` line |

## 5. Exact CI change

Added one new job to `.github/workflows/ci.yml`, and updated the file's header
comment from "Two levels" to "Three levels" (documenting `lint`,
`compatibility`, `release-readiness`). The new job:

```yaml
  lint:
    name: lint (Ruff, Python 3.11)
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install the package (with dev extras)
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Run the Ruff lint gate
        run: ruff check src tests scripts
```

* Python **3.11**, `checkout@v4`, `setup-python@v5` — as required.
* Installs the **development** extras (`.[dev]`, which now includes the pinned
  Ruff).
* Runs `ruff check` **exactly once**, against the project's Python sources
  (`src tests scripts`), and fails the job on any finding (Ruff exits non-zero
  on violations).
* The job has **no `strategy.matrix`**, so it is independent of the Python
  compatibility matrix and runs a single time.

Unchanged, as required: `compatibility` still runs the test suite and the lab
self-check once per matrix entry (**Python 3.11 + 3.13**, `fail-fast: false`);
`release-readiness` still runs on Python 3.11 with the licence/version guards,
`.[dev,docs]` install, and **`release_check.py --json` exactly once**. The
expensive validation stays out of the matrix.

## 6. Commands executed and results

| Command | Result |
| --- | --- |
| `ruff --version` | `ruff 0.12.0` |
| `ruff check --no-cache src tests scripts` (before) | exit 1 — **4 × `F401`** |
| `ruff check src tests scripts` (after — **the exact CI command**) | exit 0 — **All checks passed!** (0 findings, no warning) |
| config probe (`scripts/_ruff_probe.py`: unused imports + an >88-char line + unsorted imports) | only `F401` reported — `E501` and `I001` **not** raised, proving the narrow `E4,E7,E9,F` selection; probe deleted afterwards |
| `python -m pytest` | **852 passed** in 11.04 s |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 180 files (mit 125, cc-by 53, excluded 2, unlicensed 0) |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []` |

### 6.1 Before / after Ruff comparison

| | Findings |
| --- | --- |
| Before (Ruff defaults) | **4** — all `F401` |
| After (Ruff defaults) | **0** |

* No broad rule set is enabled: `select = ["E4", "E7", "E9", "F"]` only.
  (For comparison, `research/41` measured 292 findings for the broad set; none
  of those were addressed here.)
* No formatting or import-sorting change was introduced: the only edits are the
  four removed unused imports plus configuration/CI text. `ruff format` and
  `isort` were neither run as fixes nor configured.

### 6.2 Release-gate detail (all gates)

`tests` PASS (852) · `labs` PASS (8/8) · `mkdocs` PASS (strict) · `licensing`
PASS (9/9) · `version` PASS · `readme` PASS (59 links, 3 anchors) ·
`self_containment` PASS (wheel rebuilt; schema byte-identical) · `hygiene` PASS
(no secrets/artefacts/tracked-ignored files) · `git_state` **WARN** (working
tree not clean — expected before a release commit).

## 7. `release_check.py` and scope boundaries

* **`scripts/release_check.py` was NOT changed.** The lint gate is a
  *development/CI* concern; making it a release blocker would require editing
  the release gate, which is explicitly out of scope for this step. The release
  gate remains the single authoritative, unmodified check and is still invoked
  **exactly once**.
* `.github/workflows/docs.yml` was **NOT changed**.
* No runtime code under `src/` was changed. No `labs/` change. No version bump.
* The Phase 17 freeze holds; `research/20`–`research/41` were not modified.

## 8. CI structure verification

Parsed `.github/workflows/ci.yml` with PyYAML and asserted:

| Check | Result |
| --- | --- |
| Jobs present | exactly `compatibility`, `lint`, `release-readiness` |
| `compatibility` matrix | `["3.11", "3.13"]` (unchanged) |
| `release-readiness` exists | yes (Python 3.11) |
| `release_check.py` occurrences across all `run` steps | **1** |
| `lint` job occurrences | **1** |
| `lint` independent of the matrix | yes — no `strategy` key |
| `ruff check` occurrences | **1** |
| `pytest` invocations | **1** (compatibility only — no duplication) |
| `labs check` invocations | **1** (compatibility only — no duplication) |

All assertions passed.

## 9. Remaining warnings

The release gate still reports the same three warnings as the `research/41`
baseline — **W6, W7, W12** — unchanged:

* **W6** — `CITATION.cff` has no `date-released` (set at release time).
* **W7** — `.freebuff/project-id` is tracked.
* **W12** — human-judgement licensing residuals (`research/28`–`research/36`).

`git_state` remains **WARN** because the working tree is not clean during
development (expected; it clears on the release commit). The MkDocs
stderr notice about the future MkDocs 2.0 / Material compatibility is the
pre-existing upstream advisory (already recorded via the pinned `docs` extra),
not a new warning.

No new linter warnings remain: `ruff check` on the configured rule set is
silent.

## 10. Files changed

Two modified tracked files plus four one-line import fixes plus this record:

```
pyproject.toml                             (+ruff==0.12.0 dep, +[tool.ruff.lint])
.github/workflows/ci.yml                   (+lint job, header comment)
tests/eval/test_eval.py                    (-AgentConfig import)
tests/schema/test_packaged_schema.py       (-validate_event import)
tests/test_release_check.py                (-import pytest)
tests/test_version.py                      (-import pytest)
research/42-ruff-lint-implementation.md    (this record, new)
```

**Nothing was committed, pushed or tagged.** `git diff --check` reported no
whitespace errors, and `git status --short` showed no generated artefacts,
caches or unrelated modifications (the transient `scripts/_ruff_probe.py` used
to prove the rule selection was deleted; `site/`, `__pycache__/` etc. are
pre-existing git-ignored build output and do not appear in status).

### Safety boundary (Phase 17)

This step adds no runtime code, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains
**HOLD**; no novelty, effectiveness, security-effectiveness, benchmark or
publication claim is made.
