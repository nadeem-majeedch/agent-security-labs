# PHASE 21 — MYPY TYPE-CHECK GATE IMPLEMENTATION (B4.2)

*Implementation record for the second quality-gate item in
`research/41-quality-gates-audit.md` (§5 item 2, §8 decision 4): the mypy
type-check gate. Only mypy was added. Nothing was committed, pushed, tagged or
version-bumped; the Phase 17 freeze and the `v0.0.1` release are untouched.*

## 0. Scope

This step implements **only** the mypy type-check gate:

* the six missing-stub findings resolved by declaring the real PEP 561 stub
  packages (**not** by ignoring the imports);
* the three genuine code-level findings fixed in source;
* a minimal `[tool.mypy]` configuration;
* a pinned mypy development dependency;
* one new, independent `typecheck` CI job.

**Explicitly NOT done in this step:**

* **Ruff remains unchanged** — `[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]`
  is exactly as implemented in B4.1 (`research/42`); no rule was added or removed.
* **coverage was NOT implemented** (no tool, no threshold).
* **Black was NOT implemented** (no formatter).
* **isort was NOT implemented** (no import sorter).
* **`scripts/release_check.py` was NOT changed** — mypy is a CI/development
  gate, not a release blocker; the gate is still invoked exactly once.
* `.github/workflows/docs.yml` was **NOT changed**.
* The project **version remains `0.0.1`** and the **`v0.0.1` tag remains
  untouched**.

## 1. Baseline (verified, not assumed)

`research/41` recorded 9 mypy errors. The baseline was re-measured before any
change, with the audit's own command:

```
mypy --no-incremental --python-version 3.11 --cache-dir=/dev/null src/agentsec
```

| | |
| --- | --- |
| mypy version | **1.17.1** (compiled) |
| Total errors | **9**, in 8 files (40 source files checked) |
| Missing-stub errors | **6** (`import-untyped`) |
| Code-level errors | **3** |

Baseline output:

```
src\agentsec\trace\validate.py:31:  error: Library stubs not installed for "jsonschema"            [import-untyped]
src\agentsec\trace\schema.py:60:    error: Incompatible types in assignment ...                    [assignment]
src\agentsec\tools\base.py:19:      error: Library stubs not installed for "jsonschema"            [import-untyped]
src\agentsec\tools\base.py:20:      error: Library stubs not installed for "jsonschema.exceptions" [import-untyped]
src\agentsec\policy\loader.py:14:   error: Library stubs not installed for "yaml"                  [import-untyped]
src\agentsec\trace\recorder.py:119: error: Incompatible return value type ...                      [return-value]
src\agentsec\experiment\config.py:19: error: Library stubs not installed for "yaml"                [import-untyped]
src\agentsec\scenarios\loader.py:14: error: Library stubs not installed for "yaml"                 [import-untyped]
src\agentsec\cli.py:54:             error: Return type "None" of "error" incompatible ...          [override]
Found 9 errors in 8 files (checked 40 source files)
```

### 1.1 The six stub findings (exact)

| File:line | Module | Message |
| --- | --- | --- |
| `trace/validate.py:31` | `jsonschema` | Library stubs not installed |
| `tools/base.py:19` | `jsonschema` | Library stubs not installed |
| `tools/base.py:20` | `jsonschema.exceptions` | Library stubs not installed |
| `policy/loader.py:14` | `yaml` | Library stubs not installed |
| `experiment/config.py:19` | `yaml` | Library stubs not installed |
| `scenarios/loader.py:14` | `yaml` | Library stubs not installed |

### 1.2 The three code-level findings (exact)

| Location | Error | Nature |
| --- | --- | --- |
| `src/agentsec/trace/schema.py:60` | `[assignment]` — `str` assigned to `Literal['1.0']` | `TRACE_SCHEMA_VERSION` was inferred as plain `str` |
| `src/agentsec/trace/recorder.py:119` | `[return-value]` — got the `TraceEvent` union, expected `_EventT` | generic `build()` result |
| `src/agentsec/cli.py:54` | `[override]` — `error()` returns `None`, supertype declares `Never` | argparse override |

## 2. Stub strategy

**Chosen: declare the real PEP 561 stub packages as development dependencies.**
Both exist and are the correct, upstream-maintained stubs, so the imports are
actually typed rather than hidden.

Added to `[project.optional-dependencies].dev`:

```toml
    # PEP 561 stubs for the two untyped third-party imports (PyYAML, jsonschema)
    # so mypy inspects the project's code instead of hiding those imports behind
    # ignore_missing_imports. The ranges mirror the runtime constraints above.
    "types-PyYAML>=6.0",
    "types-jsonschema>=4.20",
```

**Without** (as required): no blanket `ignore_missing_imports`, no per-module
`ignore_missing_imports`, no broad `# type: ignore` for the stubs. The stub
packages simply replace the untyped imports, so mypy reads the project's real
code against typed `yaml` / `jsonschema` APIs.

## 3. Exact code changes

Smallest type-correct change at each site; runtime and public behaviour are
preserved.

**`src/agentsec/trace/schema.py`** — annotate the constant so the
`Literal["1.0"]` field type-checks (runtime value unchanged):

```diff
-TRACE_SCHEMA_VERSION = "1.0"
+#: Annotated with the literal so the ``schema_version`` field below (typed
+#: ``Literal["1.0"]``) type-checks; a bare assignment infers plain ``str``.
+TRACE_SCHEMA_VERSION: Literal["1.0"] = "1.0"
```

**`src/agentsec/trace/recorder.py`** — a precise cast (not a blanket ignore)
where mypy cannot narrow a `TypeVar` bound to a discriminated union:

```diff
-from typing import Any, Callable, TypeVar
+from typing import Any, Callable, TypeVar, cast
...
         data: dict[str, Any] = dict(self._header())
         data.update(fields)
-        return event_cls(**data)
+        # ``_EventT`` is bound to the discriminated *union* ``TraceEvent``, which
+        # mypy cannot narrow through ``type[_EventT]``: it infers the union, not
+        # the specific member. The cast is exact (the caller passes the class it
+        # expects back) and keeps the return type useful for callers.
+        return cast(_EventT, event_cls(**data))
```

**`src/agentsec/cli.py`** — match argparse's declared `Never` return type:

```diff
-from typing import Sequence
+from typing import Never, Sequence
...
-    def error(self, message: str) -> None:  # pragma: no cover - exercised via test
+    def error(self, message: str) -> Never:  # pragma: no cover - exercised via test
```

`_Parser.error` already ends by calling `self.exit(...)` (which never returns),
so `Never` is accurate and the method still raises SystemExit with
`EXIT_CONFIG`. No `# type: ignore` was added anywhere.

## 4. mypy configuration

Minimal, in `pyproject.toml` (no `mypy.ini`/`setup.cfg`, so no new licensing
manifest entry):

```toml
[tool.mypy]
python_version = "3.11"
files = ["src/agentsec"]
```

* **Python 3.11** — the package minimum (`requires-python = ">=3.11"`), the same
  version the `compatibility` and `release-readiness` jobs use.
* **`files = ["src/agentsec"]`** — the declared scope; CI can therefore run a
  bare `mypy` exactly once.
* **No strict mode**, and no optional check families (`disallow_untyped_defs`,
  `warn_unused_ignores`, `check_untyped_defs`, …). The baseline is deliberately
  the smallest useful one.

### 4.1 One documented override (local-environment robustness)

```toml
[[tool.mypy.overrides]]
module = ["IPython", "IPython.*"]
follow_imports = "skip"
```

**Why.** mypy follows imports transitively. agentsec depends only on pydantic,
jsonschema and PyYAML, but in a *developer* environment those libraries'
optional/deferred imports reach packages that are **not** dependencies at all.
The concrete case: `rich` → `IPython` → `IPython.lib.display`, which imports
**numpy**; numpy 2.5's inline stubs use PEP 695 `type` statements that mypy 1.17
refuses to parse when targeting Python 3.11, aborting the whole run with a
syntax error in a file agentsec never touches:

```
.../site-packages/numpy/__init__.pyi:737: error: Type statement is only
supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
```

A clean CI environment does not have rich/IPython/numpy installed, so this path
does not exist there; but any developer whose environment has numpy present
would otherwise get a red gate for a reason unrelated to agentsec. Skipping this
single non-dependency keeps `mypy` deterministic and identical across a clean CI
env and a developer machine. **Nothing agentsec imports is hidden** — `grep`
confirms `src/` contains no reference to `IPython` or `numpy`, and pydantic,
jsonschema, yaml and their stubs are still fully followed.

This is a `follow_imports` scope on a non-dependency, not an error ignore: no
`ignore_errors`, no `ignore_missing_imports`, no blanket `# type: ignore`.
(For the record, a same-shaped override targeting `numpy` itself was tried first
and did **not** prevent the abort; skipping the non-dependency that reaches it
does.)

## 5. Pinned version and CI job

**Pinned:** `mypy==1.17.1` in `[project.optional-dependencies].dev` — the exact
version the audit and this step used, pinned for the same version-drift reason as
Ruff (W11): an unpinned type checker can flip a green CI to red. The stub
packages use ranges mirroring the runtime constraints (`types-PyYAML>=6.0`,
`types-jsonschema>=4.20`).

**New CI job** (`typecheck`, inserted between `compatibility` and
`release-readiness`):

```yaml
  typecheck:
    name: typecheck (mypy, Python 3.11)
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

      - name: Run the mypy type-check gate
        run: mypy
```

Python 3.11, `checkout@v4`, `setup-python@v5`, installs `.[dev]` (which now
brings mypy **and** the stubs), runs **mypy exactly once**, and fails on any
error. The job has **no `strategy.matrix`**, so it is independent of the Python
compatibility matrix and runs a single time. The file header comment was updated
from "Three levels" to "Four levels".

## 6. Commands executed and results

| Command | Result |
| --- | --- |
| `mypy --version` | `mypy 1.17.1 (compiled: yes)` |
| `mypy --no-incremental --python-version 3.11 --cache-dir=/dev/null src/agentsec` (before) | exit 1 — **9 errors** (6 stubs, 3 code) |
| `python -m pip install -e ".[dev]"` | installed mypy 1.17.1, ruff 0.12.0, types-PyYAML 6.0.12.20260906, types-jsonschema 4.26.0.20260518 |
| `mypy` (bare — the exact CI command) | exit 0 — **Success: no issues found in 40 source files** |
| `mypy --python-version 3.11 src/agentsec` (the audit command) | exit 0 — **Success: no issues found in 40 source files** |
| `python -m pytest` | **852 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** (Ruff unchanged) |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []` |

### 6.1 Before / after error count

| | Errors |
| --- | --- |
| Before | **9** (6 stub + 3 code) |
| After | **0** |

Local verification used the project interpreter (CPython 3.13.14), where the
declared dev extras were installed as CI does. Because the local machine targets
the same `python_version = "3.11"` config, the target-version analysis is
identical to CI.

## 7. CI structure verification

`.github/workflows/ci.yml` was parsed with PyYAML and asserted:

| Check | Result |
| --- | --- |
| Jobs present | exactly `lint`, `compatibility`, `typecheck`, `release-readiness` |
| `compatibility` matrix | `["3.11", "3.13"]` (unchanged) |
| `lint` has no matrix | yes |
| `typecheck` has no matrix | yes |
| `release-readiness` has no matrix | yes |
| `release_check.py` occurrences | **1** |
| `ruff check` occurrences | **1** |
| `mypy` occurrences | **1** |
| `pytest` invocations | **1** (compatibility only — not duplicated) |
| `agentsec labs check` invocations | **1** (compatibility only — not duplicated) |
| `.github/workflows/docs.yml` exists (untouched) | yes |

All assertions passed. `mypy` is **not** in the compatibility matrix and **not**
in `release_check.py`.

## 8. Remaining release warnings

Unchanged: exactly **W6, W7, W12**.

* **W6** — `CITATION.cff` has no `date-released` (set at release time).
* **W7** — `.freebuff/project-id` is tracked.
* **W12** — human-judgement licensing residuals (`research/28`–`research/36`).

`git_state` remains **WARN** (working tree not clean during development). No
warning was addressed in this step.

## 9. Files changed

```
pyproject.toml                             (+mypy==1.17.1, +types-PyYAML, +types-jsonschema,
                                            +[tool.mypy], +[[tool.mypy.overrides]])
.github/workflows/ci.yml                   (+typecheck job, 3 levels -> 4 levels)
src/agentsec/trace/schema.py               (Literal-annotate TRACE_SCHEMA_VERSION)
src/agentsec/trace/recorder.py             (import cast; cast build() return)
src/agentsec/cli.py                        (import Never; error() -> Never)
research/43-mypy-typecheck-implementation.md   (this record, new)
```

**Nothing was committed, pushed or tagged.** The transient `_mypy_probe.ini`
and `.mypy_cache` used during investigation were deleted.

### Safety boundary (Phase 17)

This step adds no runtime behaviour change (the three fixes are annotation/cast
only), no research implementation, no corpus, no experiment and no learner data.
Phase 17 remains **CLOSED**; E1 remains **HOLD**; no novelty, effectiveness,
security-effectiveness, benchmark or publication claim is made.
