# PHASE 21 — QUALITY-GATES READINESS AUDIT (B4)

*Repository-only audit for the next v0.1.0 development step: lint, type-checking
and coverage readiness. No file was modified to produce it other than this
record. Nothing was committed, pushed, tagged, or version-bumped; the Phase 17
freeze and the v0.0.1 release are untouched.*

## 0. Scope and method

The audit inspects `pyproject.toml`, `.github/workflows/`, the developer
documentation, the repository layout, and the current annotations in
`src/agentsec`, then runs only tooling that is **already installed** on this
machine (Anaconda base, CPython 3.13.9). Coverage tooling is absent, so no
coverage percentage is reported. Everything recommended below is labelled
**[PROPOSED]** and nothing proposed is described as implemented.

---

## 1. CURRENTLY IMPLEMENTED

These quality controls exist and run today:

| Control | Mechanism | Where |
| --- | --- | --- |
| Test suite (852 tests) | `pytest` with `pythonpath=["src"]`, `testpaths=["tests"]`, `addopts="-q"` | `[tool.pytest.ini_options]`, `tests/` |
| Architectural import rules | `tests/test_architecture.py` (AST-based, banned deps, layering, gateway-only execution) | `tests/` |
| Lab reproducibility | `agentsec labs check` (8/8) | `src/agentsec/selfcheck.py` |
| Licensing declarations + coverage | `scripts/check_licensing.py` (9/9) | CI |
| Version consistency | `scripts/check_version.py` (3/3) | CI |
| Trace-schema drift | `tests/schema/test_schema_file.py`, `test_packaged_schema.py` | `tests/` |
| Aggregate release gate | `scripts/release_check.py` (9 gates, W6–W13) | CI |
| Inline suppressions in use | 31 markers: `# noqa` (Ruff codes `BLE001`, `ARG002`), `# pragma: no cover`, `# type: ignore` | `src/`, `tests/` |

The `# noqa: BLE001` / `# noqa: ARG002` markers are **Ruff rule codes**, which
shows the source was written with Ruff in mind — but Ruff is not configured or
declared anywhere (§2, §3).

## 2. CURRENTLY CONFIGURED

**Nothing for lint, formatting, type-checking or coverage.** `pyproject.toml`
contains only:

```
[build-system] [project] [project.urls] [project.optional-dependencies]
[project.scripts] [tool.setuptools.packages.find]
[tool.setuptools.package-data] [tool.pytest.ini_options]
```

There is **no** `[tool.ruff]`, `[tool.mypy]`, `[tool.coverage]`, `[tool.black]`
or `[tool.isort]`, and **no** `ruff.toml`, `mypy.ini`, `setup.cfg`, `tox.ini`,
`.pre-commit-config.yaml`, `.editorconfig`, `.flake8` or `.pylintrc`.

`[project.optional-dependencies]` declares only `dev = ["pytest>=7.4"]`,
`live = ["httpx>=0.27"]` and the pinned `docs` extra. **No linter, type checker
or coverage tool is a declared dependency.**

## 3. CURRENTLY ABSENT

| Concern | Status |
| --- | --- |
| Lint configuration / gate | **Absent** (no config, no CI step) |
| Formatter configuration / gate | **Absent** |
| Import-sort configuration / gate | **Absent** |
| Type-checker configuration / gate | **Absent** |
| Coverage tooling / gate | **Absent** (`coverage` and `pytest-cov` are not importable in the project interpreter **or** in Anaconda) |
| Declared dev dependencies for any of the above | **Absent** |

**Tools present on `PATH` but outside the project environment** (Anaconda base,
CPython 3.13.9) — usable for inspection, **not** installed in the project
interpreter (`py`, CPython 3.13.14) and **not** declared as dependencies:

| Tool | Version |
| --- | --- |
| ruff | 0.12.0 |
| flake8 | 7.1.1 (mccabe 0.7.0, pycodestyle 2.12.1, pyflakes 3.2.0) |
| black | 25.9.0 |
| isort | 6.1.0 |
| mypy | 1.17.1 (compiled) |
| pyright / pyre | **not present** |

## 4. OBSERVED FINDINGS

### 4.1 Lint — Ruff (default rule set `E4,E7,E9,F`): **4 findings, all `F401`**

```
tests/eval/test_eval.py:10:35            F401  `agentsec.agent.AgentConfig` imported but unused
tests/schema/test_packaged_schema.py:33  F401  `agentsec.trace.validate.validate_event` imported but unused
tests/test_release_check.py:21:8         F401  `pytest` imported but unused
tests/test_version.py:21:8               F401  `pytest` imported but unused
```

All four are auto-fixable. **No `E`/`W`/`F` findings exist in `src/agentsec` or
`scripts/` under the default rules.**

### 4.2 Lint — a broader rule set is a large cleanup, not a small one

Running Ruff with `E,W,F,I,B,UP,SIM,C4,ARG,BLE` yields **292 findings**:

| Rule | Count | Rule | Count |
| --- | --- | --- | --- |
| E501 line-too-long (default width 88) | 200 | B017 assert-raises-exception | 2 |
| UP017 datetime-timezone-utc | 18 | B007 unused-loop-control-variable | 1 |
| UP035 deprecated-import | 18 | B905 zip-without-explicit-strict | 1 |
| ARG001 unused-function-argument | 14 | C408 unnecessary-collection-call | 1 |
| ARG002 unused-method-argument | 10 | C420 unnecessary-dict-comprehension | 1 |
| UP037 quoted-annotation | 7 | UP007 non-pep604-annotation-union | 1 |
| ARG005 unused-lambda-argument | 5 | I001 unsorted-imports | 3 |
| F401 unused-import | 4 | SIM102 collapsible-if | 3 |

53 of the 292 are auto-fixable. **Conclusion: start narrow (Ruff defaults); do
not open the extended rule set in the first step.**

The `ARG001/ARG002/ARG005` counts explain the existing `# noqa: ARG002` markers:
those rules are only relevant if `ARG` is enabled, which it currently is not.

### 4.3 Formatting — the tree is not formatter-clean

| Check | Result |
| --- | --- |
| `ruff format --check` (width 88) | **50 files** would reformat (32 already clean) |
| `black --check` (width 88) | **49 files** would reformat |
| `isort --check-only` | **fails** (import sorting differs from default) |
| `flake8` (default width 79) | **754** findings, overwhelmingly `E501` |

There is **no enforced line width**. In `src/agentsec`: 47 lines exceed 88
characters and 219 exceed 79 (longest is `tools/mock_db.py:181` at 136). Adding
a formatting gate now would produce a ~50-file mechanical diff — too large to
mix into a small quality-gates step.

### 4.4 Type-checking — mypy (target Python 3.11), `src/agentsec`: **9 errors / 8 files**

**Six are missing third-party stubs (environment, not code defects):**

```
trace/validate.py:31       error: Library stubs not installed for "jsonschema"           [import-untyped]
tools/base.py:19           error: Library stubs not installed for "jsonschema"           [import-untyped]
tools/base.py:20           error: Library stubs not installed for "jsonschema.exceptions" [import-untyped]
policy/loader.py:14        error: Library stubs not installed for "yaml"                  [import-untyped]
experiment/config.py:19    error: Library stubs not installed for "yaml"                  [import-untyped]
scenarios/loader.py:14     error: Library stubs not installed for "yaml"                  [import-untyped]
```

Fix by adding `types-PyYAML` + `types-jsonschema` to the dev extras, **or** by a
narrow `ignore_missing_imports` override for exactly `yaml` and `jsonschema`.

**Three are genuine, small code-level typing issues:**

| Location | Error | Nature |
| --- | --- | --- |
| `src/agentsec/trace/schema.py:60` | `Incompatible types in assignment (expression has type "str", variable has type "Literal['1.0']")` `[assignment]` | `schema_version: Literal["1.0"] = TRACE_SCHEMA_VERSION`, where `TRACE_SCHEMA_VERSION` is inferred as `str`. Fix: annotate the constant (`Final`/`Literal`). |
| `src/agentsec/trace/recorder.py:119` | `Incompatible return value type (...) expected "_EventT"` `[return-value]` | The generic `build()` returns `event_cls(**data)` typed as the union rather than `_EventT`. Fix: a precise annotation/cast (not a blanket ignore). |
| `src/agentsec/cli.py:54` | `Return type "None" of "error" incompatible with return type "Never" in supertype "argparse.ArgumentParser"` `[override]` | `_Parser.error` returns `None`; it calls `self.exit(...)`. Fix: annotate the return as `NoReturn`/`Never`. |

**Verdict: the project is realistically type-checkable** — 3 small code fixes
plus a stub decision, with no major refactor. The pydantic-heavy modules
(`schema.py`, `models/`) type-check cleanly apart from the `Literal` note.

### 4.5 Coverage — **not measurable in this environment**

Neither `coverage` nor `pytest-cov` is importable in the project interpreter
(`py`, 3.13.14) or in Anaconda (3.13.9). No `[tool.coverage]` configuration
exists and no coverage dependency is declared. **Therefore no coverage
percentage, source-coverage figure, missing-line list, or branch-coverage figure
can be reported without first adding tooling, which this audit deliberately did
not do.** (Uncovered-risk areas to target once it is available: the release
gate itself (`scripts/release_check.py`), lab execution paths, schema validation
branches, and the security-sensitive tools — `tools/calculator.py`,
`tools/fs_sandbox.py`, `tools/mock_db.py`, `tools/mock_email.py`.)

## 5. RECOMMENDED TOOLING

**[PROPOSED]** Adopt, in this order, one small step each — subject to the
decisions in §8:

1. **[PROPOSED] Lint: Ruff**, configured only in `pyproject.toml` (`[tool.ruff]`
   with the default `E4,E7,E9,F` selection). One tool covers linting (and later
   import sorting/formatting) without adding a new file to the licensing
   manifest. Fix the 4 `F401` findings first. Pin the Ruff version (consistent
   with the repository's existing dependency-pinning discipline, e.g. W11).
2. **[PROPOSED] Type-checking: mypy**, non-strict to start, with either
   `types-PyYAML` + `types-jsonschema` in the dev extras **or** a two-module
   `ignore_missing_imports` override; fix the 3 code-level errors above.
   Pin the mypy version.
3. **[PROPOSED] Coverage: `coverage` + `pytest-cov`**, added as dev extras and
   used **report-only** (no `--cov-fail-under`), so no arbitrary threshold is
   invented. A threshold can be decided later from a measured baseline.
4. **[PROPOSED — defer] Formatting/import-sorting.** Adopt only as a separate,
   mechanical, review-isolated change (~50 files), and only after deciding
   between Ruff's formatter and Black. Do not mix it into the lint step.

Do **not** adopt Flake8+plugins separately: Ruff's default set already covers
pyflakes/pycodestyle equivalents, and `flake8` at its default width (79) is
misaligned with the tree (754 findings), so it would need configuration to add
no value over Ruff.

## 6. PROPOSED CI PLACEMENT

**[PROPOSED]** Add the new gates as **separate, cheap jobs** that do not disturb
the current two-level architecture. The intended shape:

- **`lint` (new job, Python 3.11, once):** install `.[dev]`, run `ruff check`.
  Not in the matrix (lint results do not depend on the interpreter version), not
  in the release gate.
- **`typecheck` (new job, Python 3.11, once):** install `.[dev]`, run `mypy`.
  One canonical type-check; a per-version matrix of type-checking is optional
  and not recommended yet.
- **Coverage (new step or job, one Python version, once):** run the suite under
  `coverage` in **report-only** mode. If added, prefer a single dedicated job
  (or one step in the `compatibility` job) so it is **not** multiplied across
  the 3.11/3.13 matrix.
- **Unchanged:** `compatibility` (3.11 + 3.13) still runs only the test suite and
  the lab self-check; `release-readiness` (3.11) still runs licensing, version,
  install `.[dev,docs]`, and **`release_check.py --json` exactly once**. The
  expensive MkDocs/wheel/self-containment/hygiene checks stay out of the matrix.

**[PROPOSED]** Keep the release gate authoritative: if lint/type/coverage should
become release blockers, that is a *separate* decision, because it would mean
changing `scripts/release_check.py` (current audit instruction: keep it
unchanged, invoked once).

## 7. RISKS / TRADE-OFFS

- **Formatting is the big trap.** Black/Ruff-format/isort each fail on ~50 files;
  gating formatting now creates a large mechanical diff and review noise. Defer.
- **Breadth of Ruff rules.** Defaults are 4 findings; the extended set is 292.
  Enabling too much at once turns a small step into a large cleanup.
- **Tool version drift.** Ruff/mypy output changes between versions; pin them, or
  a green CI can flip to red on an upstream release (the same class of risk as
  W11).
- **mypy + pydantic v2 dynamics.** Non-strict mode is recommended to start; the
  temptation to add blanket `# type: ignore` must be resisted (it would weaken
  checking rather than fix it).
- **Coverage thresholds are arbitrary.** Report-only first; a threshold chosen
  without a baseline is a made-up number.
- **New dev dependencies** increase CI install time and expand `.[dev]`; they do
  not affect the wheel, so self-containment is unaffected. Any new *file* (e.g.
  `ruff.toml`) would require a new `licensing/manifest.toml` entry — another
  reason to prefer `pyproject.toml` configuration.
- **Interpreter coverage.** Local inspection used Anaconda's 3.13.9; the project
  targets 3.11+. Chosen tools must be available on both 3.11 and 3.13.
- **No local coverage measurement was possible**, so the first coverage run will
  be the real baseline.

## 8. DECISIONS REQUIRED

1. **Adopt Ruff for lint?** If yes: default rule set only, and which pinned
   version.
2. **Is lint advisory or a blocking CI job?** (Recommend blocking, since defaults
   are clean apart from 4 trivial unused imports.)
3. **Fix the 4 `F401` unused imports now** (tests only), as part of the lint step?
4. **Adopt mypy?** Non-strict or stricter; stubs (`types-PyYAML`,
   `types-jsonschema`) vs a narrow `ignore_missing_imports`; fix the 3 code
   errors.
5. **Adopt coverage?** Which tool (`coverage` vs `pytest-cov`); report-only vs a
   threshold (and if a threshold, what number, from which baseline).
6. **Where in CI?** Confirm the proposed separate `lint` / `typecheck` /
   coverage jobs on one Python version, leaving `release_check.py` invoked once
   and the matrix unchanged.
7. **Should any of these become release blockers?** That would change
   `release_check.py` (out of scope for this audit) — accept or defer?
8. **Formatting/import sorting:** defer entirely, or adopt as a separate
   mechanical change? Which formatter?

## 9. VERIFICATION RESULTS

Commands run for this audit (read-only; the only artifact created was a
git-ignored `.mypy_cache`, which was removed afterwards):

| Command | Result |
| --- | --- |
| `ruff check --no-cache src tests scripts` | exit 1 — 4 × `F401` |
| `ruff check --no-cache --statistics --select E,W,F,I,B,UP,SIM,C4,ARG,BLE …` | 292 findings |
| `ruff format --no-cache --check …` | exit 1 — 50 files would reformat |
| `black --check …` | exit 1 — 49 files would reformat |
| `isort --check-only …` | exit 1 |
| `flake8 …` | 754 findings (default width 79) |
| `mypy --no-incremental --python-version 3.11 src/agentsec` | 9 errors in 8 files |
| `coverage` / `pytest-cov` import | **not available** (no coverage figure) |
| `python -m pytest` | **852 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, gates all `PASS` except `git_state: WARN` |

**Release safety confirmed:** `v0.0.1` tag untouched; `pyproject.toml` version
still `0.0.1`; 852 tests; 8/8 labs; gate `READY WITH WARNINGS` with
`blockers: []`; remaining warnings exactly **W6, W7, W12**. **No file other
than this audit record was created or modified, and nothing was committed,
pushed or tagged.**

### Safety boundary (Phase 17)

This audit adds no runtime code, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains
**HOLD**; no novelty, effectiveness, security-effectiveness, benchmark or
publication claim is made. `research/20`–`research/40` are unmodified.
