# PHASE 21 — COVERAGE BASELINE AND REPORT-ONLY GATE IMPLEMENTATION (B4.3)

*Implementation record for the third quality-gate item in
`research/41-quality-gates-audit.md` (§5 item 3, §8 decision 5): a measured
test-coverage baseline and a report-only coverage CI job. Only coverage tooling
was added. Nothing was committed, pushed, tagged or version-bumped; the Phase 17
freeze and the `v0.0.1` release are untouched.*

## 0. Scope

This step implements **only** the coverage item:

* a measured statement + branch coverage baseline, taken **before** any edit;
* one pinned coverage development dependency (`pytest-cov`);
* one new, independent `coverage` CI job on Python 3.11 that runs the **complete
  test suite exactly once** under coverage;
* report-only semantics — **no threshold, no `--cov-fail-under`**.

**Explicitly NOT done in this step:**

* **No coverage threshold** and **no release blocker**: a low coverage number
  cannot fail the job. The job fails only if the test run itself (or the
  coverage plugin) is broken.
* **Ruff remains unchanged** — `[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]`
  is exactly as implemented in B4.1 (`research/42`); no rule was added or removed.
* **mypy remains unchanged** — `[tool.mypy]` and the `IPython` override are
  exactly as implemented in B4.2 (`research/43`).
* **No tests were added** to raise the coverage percentage.
* **Black / isort / flake8 / pyright were NOT introduced.**
* **`scripts/release_check.py` was NOT changed** — coverage is a CI/development
  report, not a release gate; the gate is still invoked exactly once.
* **`.github/workflows/docs.yml` was NOT changed.**
* The project **version remains `0.0.1`** and the **`v0.0.1` tag remains
  untouched**.

## 1. Baseline before implementation (measured, not assumed)

`research/41` (§4.5) recorded that coverage was **not measurable** because
neither `coverage` nor `pytest-cov` was importable. That was re-confirmed, then
the chosen tool was installed **into the project interpreter** and the suite was
measured **before** any repository file was edited.

Baseline command (branch coverage enabled, missing lines listed):

```
python -m pytest --cov=agentsec --cov-branch --cov-report=term-missing
```

| | |
| --- | --- |
| Tests executed | **852 passed** |
| Statement coverage | **96%** — 2226 statements, 92 missed (covered 2134 = 95.87%) |
| Branch coverage | **89%** — 522 branches, 58 partial (covered 464 = 88.89%) |
| Combined `Cover` (coverage.py composite) | **94%** |
| Tool | `pytest-cov` **7.0.0** (pulls `coverage` **7.16.2**) |
| Interpreter | project interpreter, CPython **3.13.14** (win32) |

A separate statement-only run (`--cov=agentsec --cov-report=term`, no
`--cov-branch`) reported `TOTAL 2226 92 96%` and `852 passed`, confirming the
statement figure independent of branch measurement.

### 1.1 Least-covered modules (from the baseline `Missing` column)

| File | Stmts | Miss | Branch | BrPart | Cover | Missing (excerpt) |
| --- | --- | --- | --- | --- | --- | --- |
| `src/agentsec/__main__.py` | 4 | 4 | 2 | 0 | **0%** | `3-8` |
| `src/agentsec/tools/factory.py` | 49 | 5 | 26 | 5 | 87% | `68, 78, 107, 109, 111` |
| `src/agentsec/tools/fs_sandbox.py` | 93 | 9 | 44 | 7 | 87% | `81, 83, 91, 101, 114-116, 133, 167` |
| `src/agentsec/tools/calculator.py` | 122 | 12 | 58 | 10 | 88% | `72, 78, 84, 90, 92, 98, 104, 130, 139-140, 147, 178` |
| `src/agentsec/trace/validate.py` | 100 | 8 | 28 | 5 | 88% | `61, 94-98, 151->161, 170->148, 199-202` |
| `src/agentsec/selfcheck.py` | 123 | 9 | 24 | 5 | 89% | `153, 156, 237-238, 254, 261-263, 277` |
| `src/agentsec/tools/mock_db.py` | 155 | 12 | 56 | 6 | 91% | `129, 134-139, 184, 221, 257, 259, 273` |
| `src/agentsec/tools/gateway.py` | 104 | 7 | 30 | 1 | 94% | `164-165, 174, 202-203, 209-210` |

`src/agentsec/__main__.py` is the module executed by `python -m agentsec`; the
suite imports `agentsec.cli` directly, so those four lines are not exercised.

## 2. Selected tool and version

**Tool: `pytest-cov`, pinned `pytest-cov==7.0.0`** (installs `coverage==7.16.2`).

### 2.1 Why it was selected

* It is the **pytest plugin** around `coverage`, so measurement happens inside
  the single `pytest` run that CI already performs — **no second test
  execution** and no second interpreter invocation to keep in sync.
* It reports the summary table (`term-missing`) directly in the CI log, so the
  required outputs (total statement coverage, branch coverage, test count, and
  uncovered lines) are all produced by the one command.
* It is the approach `research/41` §5.3 recommended for this repository
  ("`coverage` + `pytest-cov` … report-only"). Using bare `coverage run -m
  pytest` would add a second command and a follow-up `coverage report` step for
  no benefit here.

The version is **pinned**, consistent with the repository's version-drift
discipline (W11, and the B4.1/B4.2 pins): an unpinned plugin or coverage release
can change the reported number or break the plugin and flip a green CI red.

`pytest-cov` lives in the existing `dev` extra, so `pip install -e ".[dev]"`
brings it in exactly as it brings in Ruff and mypy. **No new file** (e.g. a
`coverage.toml`) and **no new `[tool.coverage]` section** were added: the command
line carries the (small) coverage configuration, keeping the change minimal and
`pyproject.toml`'s new surface to a single dependency line.

## 3. Exact command used

Locally and in CI:

```
python -m pytest --cov=agentsec --cov-branch --cov-report=term-missing
```

* `--cov=agentsec` — measure the `agentsec` **source package** only (the code
  under test), not `tests/` or `scripts/`.
* `--cov-branch` — **branch coverage is measured** (in addition to statements).
* `--cov-report=term-missing` — print the table with the uncovered line numbers.

There is **no `--cov-fail-under`**, so the command is report-only by
construction: pytest's exit code reflects only the tests, never the percentage.

## 4. CI placement

A new, independent job **`coverage`** was inserted between `typecheck` and
`release-readiness`:

```yaml
  coverage:
    name: coverage (pytest-cov, Python 3.11)
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

      - name: Run the test suite once with coverage (report only)
        run: python -m pytest --cov=agentsec --cov-branch --cov-report=term-missing
```

* **Job id/name:** `coverage` / `coverage (pytest-cov, Python 3.11)`.
* **Python 3.11**, `checkout@v4`, `setup-python@v5`, installs `.[dev]`.
* **No `strategy.matrix`**: it runs once, never multiplied across the 3.11/3.13
  compatibility matrix.
* **Exactly one** `pytest` execution in this job (with coverage); there is no
  plain/duplicate `pytest` step.
* **No `release_check.py` invocation** — the release gate stays solely in
  `release-readiness`.
* The file header comment was updated from **"Four levels"** to **"Five levels"**
  and now describes `lint`, `typecheck`, `coverage`, `compatibility` and
  `release-readiness` as five distinct answers. The closing paragraph was
  updated from four answers to five.

## 5. Why no threshold was introduced

* `research/41` §7 flags that "**coverage thresholds are arbitrary**" and §5.3
  recommends **report-only** first. A number chosen before any baseline existed
  would be made up; this step deliberately records the measured baseline instead.
* The release gate must keep its existing behaviour and single invocation, and
  making coverage fail a build would effectively be a release blocker — that is
  a **separate decision** that would change `scripts/release_check.py`, which is
  out of scope here.
* Report-only keeps the coverage job honest: it fails **only** when the test run
  (or the plugin) is broken, exactly like a normal failing test, and never
  because the percentage moved.

## 6. Files changed

```
pyproject.toml                             (+pytest-cov==7.0.0 in the dev extra)
.github/workflows/ci.yml                   (+coverage job; "Four levels" -> "Five levels")
.gitignore                                 (+.coverage, .coverage.*, coverage.xml, htmlcov/)
research/44-coverage-implementation.md     (this record, new)
```

`pyproject.toml` — the only functional edit to the project metadata (one dev
dependency line; `[tool.ruff.lint]` and `[tool.mypy]` untouched):

```toml
    # Coverage tooling (research/41, research/44). pytest-cov is the pytest
    # plugin around `coverage`, chosen because it measures the suite inside the
    # single `pytest` run CI already performs (no second test execution). Pinned
    # for the same version-drift reason as Ruff and mypy above: an unpinned
    # coverage release can change the reported numbers or break the plugin.
    # This gate is report-only - there is deliberately no `fail_under` here.
    "pytest-cov==7.0.0",
```

`.gitignore` — added a **Coverage output** block so local measurement artifacts
(`.coverage`, `.coverage.*`, `coverage.xml`, `htmlcov/`) can never be tracked
accidentally. (CI writes nothing to the tree; it reports to the log only.)

## 7. Validation results

Run after the edits, locally, with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **852 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `mypy` (exact CI command; locally run as `python -m mypy`, see §8) | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 183 files accounted for (mit 125, cc-by 56, excluded 2, unlicensed 0), including this record |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `git_state: WARN` |
| `git diff --check` | clean (no whitespace errors) |

### 7.1 CI structure verification (`.github/workflows/ci.yml` parsed as YAML)

| Check | Result |
| --- | --- |
| Job ids, in order | `lint`, `compatibility`, `typecheck`, `coverage`, `release-readiness` |
| `coverage` job Python version | `3.11` |
| `coverage` uses `checkout@v4` / `setup-python@v5` | yes / yes |
| `coverage` installs `.[dev]` | yes |
| `compatibility` matrix | `["3.11", "3.13"]` (unchanged) |
| `compatibility` job still runs pytest + `agentsec labs check` | yes |
| `lint`, `typecheck`, `coverage`, `release-readiness` have a matrix | no (all four) |
| `release_check.py` occurrences in `run` steps | **1** |
| `ruff check` occurrences in `run` steps | **1** |
| `mypy` occurrences in `run` steps | **1** |
| `pytest` executions in the `coverage` job | **1** |
| `agentsec labs check` occurrences in `run` steps | **1** |
| `--cov-fail-under` anywhere in a `run` step | **none** |
| `.github/workflows/docs.yml` present (untouched) | yes |

### 7.2 No stray generated files

After all runs, the working tree contains **no** tracked or untracked
`.coverage`, `coverage.xml`, `htmlcov/`, `.mypy_cache/`, or temporary probe
files. `.gitignore` now covers the coverage outputs; `.mypy_cache/` was already
covered and was removed after the earlier mypy run. (An earlier scratch file
written to the repository root during this step was deleted, and the licensing
gate — which flagged it — then passed 9/9 on the clean tree.)

## 8. Remaining limitations

* **Local coverage used CPython 3.13.14**, not 3.11: this machine has only 3.13
  available, so the CI **3.11 leg cannot be verified locally**. Coverage numbers
  can differ marginally between interpreters; the recorded baseline is the 3.13
  figure. CI will establish the 3.11 figure when it runs.
* **Local `mypy` PATH ambiguity (pre-existing, not caused by this step):** bare
  `mypy` on this machine resolves to Anaconda's copy
  (`/c/ProgramData/anaconda3/Scripts/mypy`), which does not see the project
  interpreter's installed `types-PyYAML` / `types-jsonschema` stubs and therefore
  reports the six `import-untyped` errors. The **faithful local equivalent of
  CI's command is `python -m mypy`** (the project interpreter's mypy), which
  reports **Success: no issues found in 40 source files**. In CI, `.[dev]` is
  installed into the active environment, so bare `mypy` is the project's mypy and
  behaves identically. This step changed no mypy configuration.
* **Measured scope is `agentsec` source only.** `tests/` and `scripts/` are not
  measured (`--cov=agentsec`), so the 814-line `scripts/release_check.py` and the
  scripts' own logic are outside the number.
* **`# pragma: no cover` markers are honoured** by coverage.py, so deliberately
  unexercised lines are excluded rather than counted as missed.
* **No threshold means the number can drift.** Without a threshold or a recorded
  ratchet, a future change can lower coverage without failing anything; that is
  the intended report-only trade-off. A later step could record the baseline or
  add a ratchet, separately from the release gate.
* **The suite runs twice overall across CI** (once plainly in `compatibility` per
  matrix leg, once under coverage in `coverage`) — by design, since this step
  requires a single execution *within* the coverage job and must not remove the
  compatibility matrix's plain run.
* **`__main__.py` is 0%**: `python -m agentsec` is not exercised by the suite.

## 9. Non-alteration confirmation

Confirmed by `git status` / `git diff` / `git rev-parse` at the end of this step:

* **`scripts/release_check.py` is unmodified** (no tracked diff).
* **`.github/workflows/docs.yml` is unmodified** (no tracked diff).
* **The package version remains `0.0.1`** (`pyproject.toml`,
  `agentsec.__version__`, and `CITATION.cff` all `0.0.1`; `check_version.py`
  3/3).
* **The `v0.0.1` tag is untouched** — tag object
  `cd60b32c7da3174423657e3ec53ecb7dd120eecb` still points to commit
  `121acc33c875748efdff1547dde982fa301b3019`.
* **The labs are unmodified** — `agentsec labs check` 8/8.
* **`research/20`–`research/43` are unmodified** — no tracked diff; only the
  untracked audit records `research/41`, `research/42`, `research/43` from the
  earlier steps and this new `research/44` exist.
* **The B4.1 Ruff and B4.2 mypy configurations are unmodified** — `[tool.ruff.lint]`
  and `[tool.mypy]`/`[[tool.mypy.overrides]]` are byte-for-byte the earlier steps'
  versions; this step only appended one dev dependency.
* **Nothing was committed, pushed or tagged.**

### Safety boundary (Phase 17)

This step adds no runtime code, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains **HOLD**;
no novelty, effectiveness, security-effectiveness, benchmark or publication claim
is made. The measured coverage is reported as a number only — it is **not**
described as good, sufficient or adequate.
