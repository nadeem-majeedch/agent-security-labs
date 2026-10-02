# PHASE 21 — PY.TYPED AND PUBLIC-SURFACE TYPE CHECKING (D1)

*Implementation record for `research/39` item **D1**: the PEP 561 ``py.typed``
marker plus public-surface type checking. This is the last item of the plan's
**Phase 3** (quality gates). Nothing was committed, pushed, tagged or
version-bumped; the Phase 17 freeze and the `v0.0.1` release are untouched.*

## 1. D1 requirement (from `research/39`)

* `research/39` §9 **D1 [PROPOSED]** — "Add `py.typed` and type-check the public
  surface."
* `research/39` §13 **Phase 3 — Quality gates (B4, D1)** — "Add lint/format/type
  config and a coverage floor; add `py.typed`; fix whatever they surface."
* `research/39` §10 — "**B4 (type gate) → D1 (`py.typed`)** are the same thread
  and should be one phase."

So D1 has two halves: (a) ship the PEP 561 marker so downstream type checkers
see agentsec's inline annotations, and (b) type-check the public surface.

## 2. Baseline (verified before editing)

| Item | Value |
| --- | --- |
| `src/agentsec/py.typed` | **absent** |
| Tests | **853 passed** |
| mypy | `[tool.mypy] python_version = "3.11"`, `files = ["src/agentsec"]` — **0 errors / 40 files** |
| License manifest accounting | **185** files (after `research/46`), 9/9 checks |
| Packaging config | `[tool.setuptools.packages.find] where = ["src"]`; `[tool.setuptools.package-data] "agentsec.schemas" = ["trace/*.json"]`; **no** `MANIFEST.in`, no `include_package_data` |
| CI jobs | `lint`, `compatibility`, `typecheck`, `coverage`, `release-readiness` |
| Release gate | **READY WITH WARNINGS**, `blockers: []`, warnings `{W6, W7, W12}` |

### 2.1 How the package is discovered and packaged

setuptools discovers packages under `src/` and, for the marker decision, the key
question was whether an empty, non-`.py` file is included automatically. It is:
**setuptools ≥ 69 automatically includes `py.typed`** in the built distribution,
and this project's `[build-system]` already requires `setuptools >= 77`. The
baseline wheel (built without the marker) contained no `py.typed`; after adding
the marker, the wheel contained `agentsec/py.typed` with **no packaging change**
(§3.2).

## 3. Implementation

### 3.1 The marker

`src/agentsec/py.typed` — an **intentionally empty** PEP 561 marker file (the
PEP requires the file to be empty).

### 3.2 Packaging: no configuration change

Because setuptools ≥ 69 already includes `py.typed`, the wheel ships the marker
without touching `pyproject.toml`. The smallest defensible change was therefore
to add **no** packaging machinery:

* **not** added: a `[tool.setuptools.package-data]` `"agentsec" = ["py.typed"]`
  entry;
* **not** added: `MANIFEST.in` or `include_package_data`.

Verified by building the wheel with and without the marker (§6.1): the marker
appears only when the file exists, and no packaging key changed.
`pyproject.toml`'s packaging block is byte-identical to its pre-D1 state.

### 3.3 Public-surface type checking

**Chosen: the existing package-wide mypy gate plus a small consumer test.** The
existing `[tool.mypy]` already type-checks every module under `src/agentsec`,
which includes the public `__init__.py` and its `__all__`; that half of D1 is
already satisfied by B4.2 and was **not** weakened or broadened (no strict mode,
no new mypy file scope, no whole-project strict conversion, as required).

The delta D1 adds from a *downstream* perspective is a tiny consumer that
imports the public API and uses it with annotations, type-checked with the
repository's own mypy configuration:

```python
from agentsec import (
    Agent, AgentConfig, ScenarioRegistry, TraceEvaluator, __version__,
)
from agentsec.errors import AgentSecError

def use_public_surface(agent: Agent, config: AgentConfig) -> str:
    evaluator: TraceEvaluator = TraceEvaluator()
    registry: ScenarioRegistry = ScenarioRegistry()
    error: type[AgentSecError] = AgentSecError
    del evaluator, registry, error
    return __version__
```

This demonstrates that the advertised surface is usable by a type checker (the
thing `py.typed` enables), and it fails if a public name is removed or retyped
incompatibly.

### 3.4 Regression test

New file `tests/test_public_surface.py` (5 tests):

| Test | Proves |
| --- | --- |
| `test_the_pep_561_marker_exists_and_is_empty` | `src/agentsec/py.typed` exists and is empty |
| `test_every_advertised_public_name_resolves` | every `__all__` name is importable from `agentsec` |
| `test_the_public_surface_has_no_duplicate_names` | `__all__` has no duplicates |
| `test_the_public_surface_type_checks_for_a_consumer` | the consumer above type-checks (skips only if mypy is absent) |
| `test_the_built_wheel_ships_the_marker_and_stays_self_contained` | the built wheel contains `agentsec/py.typed` **and** the packaged schema, and leaks no `labs/` |

The wheel test reuses the release gate's packaging approach
(`scripts/release_check.py::_build_wheel`): it **copies the project out of the
repository** and runs `pip wheel . --no-deps` on the copy, so the working tree is
never touched (confirmed: no `build/`, no `dist/`, no new tracked files). When
the build cannot run (e.g. offline build isolation), it skips — mirroring the
gate, which treats a wheel-build failure as a `WARN`, not a blocker.

## 4. Files changed

```
src/agentsec/py.typed          (new, intentionally empty PEP 561 marker)
tests/test_public_surface.py   (new, 5 tests)
research/47-pytyped-implementation.md   (this record, new)
```

No other file was created or modified: `pyproject.toml`, `.github/workflows/ci.yml`,
`scripts/release_check.py`, `src/` sources and the B4/B5 configuration are
unchanged.

## 5. CI

**No CI change was needed.** The five jobs (`lint`, `compatibility`,
`typecheck`, `coverage`, `release-readiness`) are unchanged. The new test runs
inside the existing test suite; the mypy gate already covers the public surface;
and the wheel content is proven by the test and independently by the release
gate's `self_containment` check.

## 6. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **859 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `python -m mypy` (exact CI command, project interpreter) | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 188 files accounted for (mit 127, cc-by 59, excluded 2, unlicensed 0), including this record |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]` |
| `git diff --check` | clean |

Suite count **853 → 859**: the 5 new tests plus **1** automatic case in
`tests/test_architecture.py`, which parametrizes over every `tests/*.py` file and
therefore now guards the new test module as well.

### 6.1 Explicit packaging proof (built from a copy, repo untouched)

```
wheel build exit: 0
wheel: agentsec-0.0.1-py3-none-any.whl
  agentsec/py.typed present        : True
  packaged schema present          : True
  labs/ leaked into wheel          : False
```

The same properties are asserted by
`test_the_built_wheel_ships_the_marker_and_stays_self_contained`, and the
existing self-containment verification (`release_check.py` `self_containment`
gate, plus `tests/schema/test_packaged_schema.py`) remains green.

## 7. Invariants confirmed

* **D1 status: [IMPLEMENTED]** (both halves: marker shipped, public surface
  type-checked).
* Version remains **`0.0.1`**; the **`v0.0.1` tag is untouched**
  (`cd60b32c7da3174423657e3ec53ecb7dd120eecb`).
* `research/39` is **unmodified**.
* **B4.1 Ruff configuration unchanged** (`select = ["E4","E7","E9","F"]`).
* **B4.2 mypy configuration unchanged** (`python_version = "3.11"`,
  `files = ["src/agentsec"]`, the `IPython` override) — D1 did **not** broaden the
  mypy scope.
* **B4.3 coverage remains report-only** (`pytest-cov==7.0.0`, no `fail_under`).
* **B5 exact warning assertion unchanged** (`ACCEPTED_RELEASE_WARNINGS`).
* Warnings remain exactly **`W6`, `W7`, `W12`**; `blockers: []`; `git_state` is
  the only non-`PASS` gate (dirty dev tree).
* No generated artifacts are tracked; no `build/`, `dist/`, caches or probes
  remain.
* **No commit, push or tag was performed.**

## 8. Limitations and deviations

* **The wheel-build test costs time and needs build isolation.** `pip wheel`
  pulls the build backend, so a fully offline environment must skip that one
  test; the release gate covers the wheel contents there instead. It is the only
  reason the suite grew from ~11s to ~23s.
* **No strict-mypy conversion was attempted**, as instructed; the public surface
  is checked at the same strictness as the rest of the package.
* **The consumer check is a smoke test**, not a matrix of every public symbol:
  it imports a representative subset and exercises the type-checker path. The
  exhaustive guarantee (every `__all__` name resolves) is covered by a separate
  structural test.
* **The marker's effect is environmental**: `py.typed` makes inline types visible
  to *other* projects' type checkers; within this repository mypy already reads
  the source directly, so the marker changes nothing here and cannot be fully
  exercised without an installed consumer.

### Safety boundary (Phase 17)

This step adds no runtime behaviour, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains **HOLD**;
no novelty, effectiveness, security-effectiveness, benchmark or publication claim
is made.
