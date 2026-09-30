# PHASE 20 — STEP 16: PACKAGE SELF-CONTAINMENT AUDIT (W5)

**Status: PASS — W5 = CLOSED.**

The packaged trace schema now ships inside the distribution and is read through `importlib.resources`, so an installed `agentsec` validates traces with no repository checkout and no `schemas/` directory beside it. The fix was verified end to end: a wheel was built, its contents inspected, and the wheel installed into an isolated virtual environment and exercised from a directory that contains no repository.

Scope: trace-schema packaging and lookup only. Nothing was committed, pushed, tagged, released or staged. Phase 17 remains **CLOSED**. **E1 remains HOLD**. No research claim is made, no study was performed, no learner data was touched, and no previous audit was modified.

---

## 1. Status

| Item | Value |
| --- | --- |
| Step | Phase 20 — Step 16, package self-containment (W5) |
| Outcome | **PASS — W5 CLOSED** |
| Defect fixed | `schema_path()` resolved the trace schema by walking parent directories to a repository checkout; outside the repository it raised `FileNotFoundError` |
| Mechanism now | package data, read through `importlib.resources` |
| Files changed | **7 modified, 3 added** (1 of the added is this audit) |
| Diff | `+151 / −43` across the 7 modified files |
| New tests | **7** (`tests/schema/test_packaged_schema.py`), plus 2 parametrisation-driven additions from the new source/test paths |
| pytest | **773 passed** (was 764) |
| labs / MkDocs / licensing | **8/8** · **exit 0** · **9/9** |
| Licence coverage | **168 files** (mit 121, cc-by 45, excluded 2, unlicensed 0); 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| Staged / committed / tagged | **none** |

## 2. Starting HEAD

| Item | Value |
| --- | --- |
| `HEAD` | `54a5e611cd1d0998f5fe4c06d8107f508f04d5a9` (`54a5e61` "final release") |
| Branch | `main` |
| Tags | 0 |
| Working tree at start | the intentional Step 15 metadata changes (3 files) plus untracked `research/32`, `research/33` |
| Baseline classification | READY WITH WARNINGS, with W5 open (`research/32` §8, `research/33` §18) |

`HEAD` is unchanged at the end of this step (§22).

## 3. Original W5 finding

Identified in `research/32` §8 and repeated in `research/33` §18:

> **Package is not self-contained.** `trace/validate.schema_path()` resolves `schemas/trace/trace_event.v1.schema.json` by walking up from `__file__`, so a copy of the package outside the repository raises `FileNotFoundError`; no package data is declared.

Reproduced on the pre-fix package as the "before" case of §19:

```
FileNotFoundError: could not locate schemas/trace/trace_event.v1.schema.json
above C:\Users\…\agentsec\trace\validate.py
```

## 4. Root cause

`src/agentsec/trace/validate.py` located the schema by filesystem traversal from the module's own location:

```python
_SCHEMA_SUBPATH = Path("schemas") / "trace" / SCHEMA_FILENAME

def schema_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / _SCHEMA_SUBPATH
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(...)
```

Three independent defects followed from that:

1. **The schema was not part of the distribution.** No `[tool.setuptools.package-data]` existed, and the only copy of `trace_event.v1.schema.json` lived in the repository's top-level `schemas/` directory, outside the `src/` package root that setuptools packages.
2. **The lookup was checkout-relative.** It searched every ancestor of the installed module for a `schemas/trace/` directory, so it only worked while the package sat somewhere under a repository. An installed wheel in `site-packages` has no such ancestor.
3. **The failure was deferred and opaque.** `load_schema()` — and therefore `validate_event()`, `validate_jsonl()` and the recorder's own validation — worked from the repository and raised `FileNotFoundError` from a deep call path once installed elsewhere. Every lab and test passed, so the defect was invisible in CI.

## 5. Packaging strategy

* **The schema is package data**, stored at `src/agentsec/schemas/trace/trace_event.v1.schema.json` inside an explicit `agentsec.schemas` subpackage, and declared in `[tool.setuptools.package-data]` so the wheel carries it.
* **The runtime reads it through `importlib.resources`** (`resources.files(SCHEMA_PACKAGE).joinpath(SCHEMA_RESOURCE)`), never by path traversal, never via the working directory, never from Git, and never by downloading it.
* **No new runtime dependency** was added: `importlib.resources`, `contextlib.ExitStack` and `atexit` are standard library.
* **The repository copy is retained** at `schemas/trace/trace_event.v1.schema.json` because it is a documented, linked artefact (`README.md` links `schemas/trace/`; `docs/development.md` describes it).
* **One writer, two outputs:** `scripts/export_trace_schema.py` now writes the same bytes to both locations, and the tests enforce identity — so duplication is mechanical rather than a second editable copy.

## 6. Files changed

Modified (`git diff --stat`, `+151 / −43`):

| File | Change |
| --- | --- |
| `src/agentsec/trace/validate.py` | The fix: schema resolved from package resources; added `SCHEMA_PACKAGE`, `SCHEMA_RESOURCE`, `schema_resource()`, `schema_text()`; `load_schema()` reads the packaged schema by default; `schema_path()` materialises a process-lifetime filesystem path via `resources.as_file`; the parent-directory walk and `_SCHEMA_SUBPATH` are gone; module docstring updated. |
| `pyproject.toml` | Added `[tool.setuptools.package-data] "agentsec.schemas" = ["trace/*.json"]`. (Also carries the Step 15 `description` correction.) |
| `scripts/export_trace_schema.py` | Now the single writer of both copies; docstring explains the relationship. |
| `src/agentsec/trace/__init__.py` | Re-exports the new `schema_resource` and `schema_text` alongside the existing `load_schema`/`schema_path`. |
| `tests/schema/test_schema_file.py` | Guards the **repository** copy explicitly by path instead of through `schema_path()` (which now resolves the packaged copy), so the repository copy keeps its model-drift guard and its failure message names the right file. |
| `docs/development.md` | Short paragraph in "Trace schema" documenting the two copies, the package-resource lookup and the sync requirement. |
| `src/agentsec/__init__.py` | Unchanged by this step (carries the Step 15 docstring correction). |

Added:

| File | Purpose |
| --- | --- |
| `src/agentsec/schemas/__init__.py` | Documented package marker for the packaged data; states the source-of-truth relationship. |
| `src/agentsec/schemas/trace/trace_event.v1.schema.json` | The packaged schema — **byte-identical** to the repository copy. |
| `tests/schema/test_packaged_schema.py` | The seven regression tests (A–D). |
| `research/34-package-self-containment-audit.md` | This audit. |

No lab, policy, scenario, schema *content*, gateway, trace semantics, CLI, CI or licensing file was modified, and no test was weakened or removed.

## 7. Schema source-of-truth decision

```
pydantic models  (src/agentsec/trace/schema.py)
        │  py scripts/export_trace_schema.py  — the only writer
        ├──────────────►  schemas/trace/trace_event.v1.schema.json
        │                 repository / documentation copy (README links it)
        └──────────────►  src/agentsec/schemas/trace/trace_event.v1.schema.json
                          packaged copy, read at runtime
```

* The **models are the source of truth**; both JSON files are generated artefacts. This was already the case before this step — the export script and the model-drift test already existed — so no new source of truth was introduced.
* The repository copy is **byte-identical** to the packaged copy (31,544 bytes, md5 `7446450a672f38a7819ffb245115a6c1`, verified by direct byte comparison in §11 and by test).
* Duplication is required by the repository's structure rather than chosen: `schemas/` is a documented public artefact and `src/agentsec/` is what the wheel packages. The two are therefore kept in step mechanically — one writer for both — with three independent guards: the repository copy against the models, the packaged copy against the models, and the two copies against each other.
* The packaged copy was produced by a **byte-exact file copy** of the repository copy, so `git status --porcelain schemas/` is empty: the tracked repository schema is provably unmodified by this step.

## 8. `schema_path()` implementation result

```python
SCHEMA_FILENAME = "trace_event.v1.schema.json"
SCHEMA_PACKAGE = "agentsec.schemas"
SCHEMA_RESOURCE = f"trace/{SCHEMA_FILENAME}"

_RESOURCE_STACK = ExitStack()
atexit.register(_RESOURCE_STACK.close)

def schema_resource():
    """The packaged trace schema as an importlib.resources resource."""
    return resources.files(SCHEMA_PACKAGE).joinpath(SCHEMA_RESOURCE)

def schema_text() -> str:
    """The packaged trace schema as text, with no filesystem path involved."""

def schema_path() -> Path:
    """A filesystem path to the packaged trace schema, kept valid for the process."""
    return _RESOURCE_STACK.enter_context(resources.as_file(schema_resource()))

def load_schema(path: Path | None = None) -> dict[str, Any]:
    """Packaged schema by default; an explicit ``path`` still loads that file."""
```

API and behaviour:

* **`schema_path()` keeps its public contract** — it still returns a `Path` and `Path.is_file()` is still true; the existing tests that call it need no change.
* **Resource lifetime is handled explicitly.** `as_file` can materialise a resource into a temporary file for non-filesystem resources (a zip import). The returned path is entered into a module-level `ExitStack` closed at interpreter exit, so the path cannot be invalidated before the caller uses it. For unpacked wheels and source checkouts — the cases that exist here — `as_file` returns the real file path with no copy.
* **`schema_text()` and `load_schema()` avoid paths altogether**, which is the access path the validator itself uses.
* **`load_schema(path=...)` is preserved**, so the helper can still load an alternative schema from disk.
* **Caching is preserved**: `load_schema() is load_schema()` still holds (`_SCHEMA_CACHE` keyed by the packaged-resource key or the explicit path).
* **Failure is now explicit and actionable**: if the data file is missing, the error says `packaged trace schema agentsec.schemas:trace/trace_event.v1.schema.json is missing; the agentsec installation is incomplete (reinstall the package)`.
* **No repository reference remains**: the string `parents` no longer occurs in the module, and the module resolves the schema with `resources.files(` (asserted by test D).

## 9. pyproject packaging configuration

```toml
[tool.setuptools.packages.find]
where = ["src"]

# The trace schema ships inside the package so that an installed agentsec is
# self-contained: trace/validate.py reads it through importlib.resources, and
# needs no repository checkout beside it.
[tool.setuptools.package-data]
"agentsec.schemas" = ["trace/*.json"]
```

* Package discovery already covered `where = ["src"]`; `agentsec.schemas` is a real subpackage (it has `__init__.py`) and is discovered automatically.
* `package-data` is the minimum declaration needed to carry the JSON; nothing else in `pyproject.toml` changed in this step.
* **Unchanged:** version `0.0.1`, `requires-python`, `license`, the Step 15 description, all dependencies, all three extras, `[project.scripts]`, `[build-system]`, `[tool.pytest.ini_options]`.
* The wheel actually contains the file — verified by inspecting the built archive, not by reading `pyproject.toml` (§11).

## 10. Regression tests

Seven tests in `tests/schema/test_packaged_schema.py`, plus the preservation of the two existing guards:

| Test | Covers | What it asserts |
| --- | --- | --- |
| `test_packaged_schema_is_a_discoverable_package_resource` | **A** | `schema_resource()` is a file; `resources.files("agentsec.schemas").joinpath(...)` is a file; the on-disk packaged path is a file; `schema_path().is_file()`; `schema_text()` starts with `{` |
| `test_validator_loads_the_packaged_schema` | A | `load_schema()` equals the parsed packaged text and declares the event union |
| `test_schema_path_is_inside_the_installed_package` | A | the resolved path lies under the packaged schema's `agentsec/` root |
| `test_packaged_schema_is_byte_identical_to_the_repository_copy` | **B** | `PACKAGED_SCHEMA.read_bytes() == REPOSITORY_SCHEMA.read_bytes()`, with a message naming the export script |
| `test_packaged_schema_matches_the_models` | B | the packaged schema equals `trace_json_schema()` |
| `test_validation_works_from_a_copy_of_the_package_outside_the_repository` | **C** | the decisive test (§12 method): a child interpreter, importing only the isolated copy, loads the schema, validates a real event and rejects an invalid one, with the reported package and schema paths asserted to be inside the copy and outside the repository |
| `test_schema_lookup_does_not_walk_parent_directories` | **D** | `validate.py`'s source contains no `parents` traversal and does resolve the schema via `resources.files(` |

Existing coverage that was **preserved, not weakened**:

* `tests/schema/test_schema_file.py` still fails if `schemas/trace/trace_event.v1.schema.json` diverges from the models — it now names that path directly rather than going through `schema_path()`, which was silently repointed at the packaged copy by this change. Had it been left alone, the repository copy would have lost its only drift guard.
* `tests/trace/test_validate.py` (14 tests) is unchanged and still passes: `schema_path()` still returns a real file, `load_schema()` is still cached, and validation behaviour is identical.

Tests are deterministic and offline: the child process runs with the ambient environment, no network, no provider, and the only filesystem work is copying the package into pytest's temporary directory.

## 11. Wheel-content verification

Built with `py -m pip wheel . --no-deps -w <temp>/dist` from an **identical copy of the project placed outside the repository** (the repository was never a build directory; `git status` afterwards shows no `build/`, no `dist/` and no new file). The build backend was fetched by build isolation — the only network access in this step.

| Check | Result |
| --- | --- |
| Wheel built | `agentsec-0.0.1-py3-none-any.whl`, exit 0 |
| `agentsec/schemas/trace/trace_event.v1.schema.json` present | **True** |
| Embedded schema **byte-identical** to `schemas/trace/trace_event.v1.schema.json` | **True** (31,544 bytes, md5 `7446450a672f38a7819ffb245115a6c1`) |
| `Name` / `Version` | `agentsec` / `0.0.1` |
| `Summary` | the corrected Step 15 description (no "Phase A" wording) |
| `License` | `MIT` |
| `Requires-Python` | `>=3.11` |
| Unwanted top-level entries (`research`, `.git`, `.freebuff`, `runs`, `site`, `tests`, `licensing`) | **none** |
| Archive entries | 46 (the `agentsec` package tree, the packaged schema and the dist-info) |

The wheel is a package, not a repository snapshot.

## 12. Isolated-install verification

The decisive test for W5, run entirely outside the repository:

1. `py -m venv --system-site-packages <temp>/venv` — a fresh environment whose third-party dependencies come from the existing interpreter.
2. `<venv>/Scripts/python -m pip install --no-deps --no-index <wheel>` → `Successfully installed agentsec-0.0.1` (`--no-index` with an empty dependency set: no network).
3. A child interpreter is run with `cwd` set to the temporary directory (no repository, no `schemas/`, no checkout) and with `PYTHONPATH` **removed** from the environment.

Result:

```
agentsec=C:\Users\…\Temp\w5-wheel-…\venv\Lib\site-packages\agentsec\__init__.py
version=0.0.1
schema=C:\Users\…\Temp\w5-wheel-…\venv\Lib\site-packages\agentsec\schemas\trace\trace_event.v1.schema.json
variants=12
valid_event=accepted
invalid_event=rejected
(exit 0, no stderr)
```

Every requirement of the step's "after" condition holds:

1. `import agentsec` succeeds ✔
2. the packaged schema is discovered ✔
3. a trace/schema operation runs: a real `RunStartedEvent` is accepted and a malformed event is rejected with `TraceSchemaError` ✔
4. no access to the repository — the imported package came from the virtual environment's `site-packages`, not from the checkout or the system editable install, and `PYTHONPATH` was cleared ✔
5. no top-level `schemas/` directory exists anywhere in the run's working tree ✔
6. no network access: the install used `--no-index`, and the package imports no network module ✔

## 13. Repository-root verification

The repository workflow is unaffected:

* `PYTHONPATH=src py -m pytest` → 773 passed (§14).
* `agentsec labs check` → 8/8 (§15).
* Both the packaged copy and the repository copy are read from the working tree exactly as before; `schemas/` is untouched (`git status --porcelain schemas/` is empty).
* `load_schema()` now returns the parsed packaged copy, which is byte-identical to the repository copy, so the dict the validator uses is unchanged. The model-drift guard on the repository copy continues to run (§10).

## 14. pytest result

`PYTHONPATH=src py -m pytest` → **773 passed** in 11.3 s, exit 0. No failures, no errors, no skips.

Count arithmetic: **764** before this step, **+7** for the new tests, **+2** from the architecture suite's parametrisations, which run once per source file and once per test file under `src/` and `tests/` — the new `src/agentsec/schemas/__init__.py` and `tests/schema/test_packaged_schema.py` each add one case. No existing test was modified to preserve a count; the only test edit was the deliberate repointing in `tests/schema/test_schema_file.py` (§10).

## 15. labs result

`agentsec labs check` → **8/8 labs passed** (LAB-00 … LAB-07 all `PASS`), exit 0. No lab, policy, scenario or configuration file was modified, and trace semantics are unchanged: the schema content is byte-identical, so recorder output and every lab's declared expectations are untouched.

## 16. MkDocs result

`py -m mkdocs build --strict` → **exit 0**, zero `WARNING -`/`ERROR -` lines. The documentation change is a paragraph in `docs/development.md`, which is not part of the site (`docs_dir: labs`); the build was run to confirm the repository as a whole still builds strictly.

## 17. Licensing result

`py scripts/check_licensing.py` → **9/9 checks passed**, exit 0. Nothing in the licensing model was touched: `LICENSE`, `LICENSE-DATA`, `CITATION.cff`, `licensing/manifest.toml` and the guard are unmodified, and the `pyproject.toml` change was confined to a new `[tool.setuptools.package-data]` table — the `license` key still reads `{ text = "MIT" }`.

## 18. Coverage result

| Metric | Value |
| --- | --- |
| Files accounted for | **168** |
| MIT | 121 |
| CC BY 4.0 | 45 |
| Excluded | 2 |
| Unlicensed | 0 |
| Unaccounted | **0** |
| Conflicts | **0** |
| Stale patterns | **0** |
| Undecided | **0** |

The three new files are covered by rules that already existed — `src/agentsec/schemas/__init__.py` and the packaged schema by `src/**` (MIT, per `LICENSE-DATA` section 2), and `tests/schema/test_packaged_schema.py` by `tests/**` (MIT) — so **`licensing/manifest.toml` was left unchanged**, as the step required. No licensing scope was broadened. After this audit exists the count becomes **169** (`cc-by 46`), matched by `research/**.md`.

## 19. Before/after W5 evidence

Both cases ran in a temporary directory outside the repository, with `PYTHONPATH` pointing only at the isolated copy and with the child importing only names present in both implementations.

**Before** — the package exactly as committed at `54a5e61` (old `trace/validate.py` and old `trace/__init__.py` restored from Git, packaged schema directory removed), which is the state `research/32` §8 described:

```
file  package_file=…\w5-baf-…\agentsec\__init__.py
exit  1
      FileNotFoundError: could not locate schemas/trace/trace_event.v1.schema.json
      above …\w5-baf-…\agentsec\trace\validate.py
```

**After** — the current package, same isolation, same child program:

```
file   package_file=…\w5-baf-…\agentsec\__init__.py
exit   0
       schema_path=…\w5-baf-…\agentsec\schemas\trace\trace_event.v1.schema.json
       finished=ok
```

Plus the stronger, independent proof of §12: a wheel installed into a fresh virtual environment in a directory with no repository at all imports `agentsec` from `site-packages`, locates the schema at `site-packages/agentsec/schemas/trace/trace_event.v1.schema.json`, and accepts a valid event while rejecting an invalid one.

### W5 = CLOSED

This is justified by the evidence and not by the intent:

1. The failure is **reproduced** from the pre-fix code (§19 before) and is **absent** after (§19 after).
2. The schema is **physically inside the distribution** and byte-identical to the authoritative copy (§11).
3. A wheel **installed into an isolated environment** performs real trace validation from a directory with no repository, no `schemas/` directory and no `PYTHONPATH` (§12).
4. The lookup **no longer consults the filesystem hierarchy** and cannot regress silently: six of the seven new tests fail if either the resource, its contents, the copy identity, the models or the lookup mechanism changes (§10).
5. The repository workflow and the repository copy are unaffected (§13–§15), so the fix did not trade one defect for another.

**Residual honesty.** The archived-copy path (`zipimport`) is covered by the `as_file` + process-lifetime `ExitStack` design and by the existing tests, but this step did not build a zipapp or run from inside a zip archive, so that specific case is designed-for rather than demonstrated. It is recorded here rather than implied to be proven.

## 20. Remaining warnings

The step's purpose was narrowly W5, and only W5 is closed. Nothing else was reclassified.

| # | Warning | Status |
| --- | --- | --- |
| **W5** | package self-containment / schema package data | **CLOSED** (§11, §12, §19) |
| W6 | `CITATION.cff` has no `date-released` | open — normally added when the release is created |
| W7 | `.freebuff/project-id` is tracked and therefore distributed | open — recorded in the manifest as outside both grants |
| W8 | no automated version-drift guard across `pyproject.toml`, `__version__` and `CITATION.cff` | open — all three still read `0.0.1` (also confirmed in the built wheel's metadata) |
| W9 | the local editable-install metadata is stale (`License: TBD`, pre-cleanup `Summary` in the git-ignored `src/agentsec.egg-info/`) | open — local only; the built wheel's metadata is correct |
| W10 | legacy `license = { text = "MIT" }` form; no `authors`, `classifiers`, `keywords`, `urls`; no SPDX identifiers | open |
| W11 | `docs` extra unpinned (`mkdocs-material>=9`) against the MkDocs 2.0 advisory | open |
| W12 | human-judgement licensing residuals tracked in `research/28`–`research/33` | open |
| W13 | `traces/*.jsonl` listed in `.gitignore` and the manifest while `traces/` does not exist | open |

Two related observations, recorded so they are not mistaken for W5:

* **The `labs` CLI subcommand still needs the repository's `labs/` directory** (`agentsec labs check --labs-dir`, default `labs`). That is inherent rather than a packaging defect: the labs *are* repository content, and the subcommand is documented as a repository-level reproducibility check. Distributing the lab material inside the wheel was not in scope and was not done.
* **The packaged schema is a second physical copy**, which adds ~31 KB to the wheel and means a schema change must be propagated by running `scripts/export_trace_schema.py`; the three drift guards exist precisely because that copy could otherwise diverge.

Warnings W2, W2b and W3/W4 remain closed as recorded in `research/33`. This step does not claim that all release warnings are closed: **eight warnings remain open.**

## 21. Research-boundary confirmation

| Statement | Evidence |
| --- | --- |
| Phase 17 remains **CLOSED** | `docs/development.md`'s `## Research status (Phase 17 — CLOSED, research NO-GO)` section is unmodified; the Step 16 documentation edit is confined to the "Trace schema" paragraph. |
| **E1 remains HOLD** | No E1 classification or publication-gate statement was touched; `research/24`–`research/26` and `research/28`–`research/33` are unmodified. |
| No research direction reopened | No research record was created or edited; the only new Markdown file is this audit. |
| No literature search | None performed. |
| No novelty claim | The change is packaging and lookup mechanics; no statement about the artefact's novelty, originality or significance was added. |
| No effectiveness claim | Nothing asserts learning, security or performance effectiveness. |
| No learner study / learner data | None performed or created; no learner-related file exists or was touched. |
| No benchmark claim | Nothing describes the artefact as a benchmark or as producing measurements. |
| No paper drafted | No manuscript or submission artefact was created. |
| No previous audit modified | `research/32` and `research/33` are byte-unchanged and untouched (`git status` lists them only as untracked). |
| Schema *content* unchanged | The packaged file is a byte-identical copy; the schema was not edited, and `git status --porcelain schemas/` is empty. |

## 22. Git safety confirmation

```
$ git diff --name-only
docs/development.md
pyproject.toml
scripts/export_trace_schema.py
src/agentsec/__init__.py
src/agentsec/trace/__init__.py
src/agentsec/trace/validate.py
tests/schema/test_schema_file.py

$ git diff --cached --name-only
(empty)

$ git status --porcelain
 M docs/development.md
 M pyproject.toml
 M scripts/export_trace_schema.py
 M src/agentsec/__init__.py
 M src/agentsec/trace/__init__.py
 M src/agentsec/trace/validate.py
 M tests/schema/test_schema_file.py
?? research/32-post-commit-release-readiness.md
?? research/33-stale-metadata-cleanup-audit.md
?? src/agentsec/schemas/
?? tests/schema/test_packaged_schema.py
?? research/34-package-self-containment-audit.md

$ git log -1 --oneline
54a5e61 final release

$ git tag --list
(no tags)
```

* `HEAD` remains `54a5e611cd1d0998f5fe4c06d8107f508f04d5a9`; **no commit, no push, no tag, no GitHub release**.
* **Nothing staged.** The working tree is left unstaged and uncommitted for the owner.
* Only the intended files changed: the seven modifications listed in §6, the two new package/test files, and the new audit. `research/32` and `research/33` are untouched.
* No build artefact was left behind: no `build/`, no `dist/`, and `git status` shows no unexpected file. Wheels and the virtual environment were created only in temporary directories outside the repository.
* No `reset`, `checkout`, `clean`, `rebase`, `amend` or `stash` was run at any point.
* The repository schema file is provably unmodified (`git status --porcelain schemas/` empty), and the packaged copy was produced by a byte-exact copy.

---

*End of Phase 20 — Step 16. W5 CLOSED on reproduced-before / verified-after evidence, including an isolated wheel installation with no repository in reach. Eight warnings remain open. No staging, commit, push, tag or release was performed.*
