# PHASE 33 — GUARDING THE GETTING-STARTED DEMO PATH

*Adds one focused documentation-consistency guard so the guided student path
keeps exposing the existing LAB-04 two-policy demo. This is a **test-only**
change: no runtime, comparison or schema semantics were touched, and
`labs/GETTING-STARTED.md` was **not** modified. Nothing was committed, pushed or
tagged.*

## 1. Reconnaissance

Inspection before editing:

* **`labs/GETTING-STARTED.md`** already carries the Phase 7F section
  `## 5. Try a two-policy comparison`, documenting
  `PYTHONPATH=src py -m agentsec demo lab04-two-policies` and its `--json` form,
  and linking `LAB-04-tool-misuse/README.md#same-lab-different-policy`. It is
  already correct, so it was left untouched (the subject being guarded).
* **`labs/LAB-04-tool-misuse/README.md`** has the `## Same lab, different policy`
  heading (anchor `same-lab-different-policy`) — the link target resolves.
* **Existing documentation guards** are one focused module per artefact:
  `tests/test_readme.py` (root README table + a `docs/development.md` note),
  `tests/test_trace_exercises.py` (the exercise/answer-key pair),
  `tests/test_release_manifest.py` and `tests/test_accepted_release_warnings.py`.
  There is **no** guard for `labs/GETTING-STARTED.md`.
* **`tests/test_architecture.py`** is the only guard that enumerates test files:
  `test_no_banned_dependency_in_tests` is parametrised over `python_files(TESTS)`,
  so a new `tests/*.py` module adds exactly **one** collected case. No test
  asserts a fixed file or test count other than the derived README guard.
* **`tests/test_readme.py`** derives the collected-test count from the suite
  itself and asserts the README states it, so any new test forces the README
  count row to move in the same change.

**Decision.** The repository's established convention is a dedicated guard module
per documentation artefact, and `tests/test_readme.py`'s own scope is the root
README (plus one development note). A new focused module,
`tests/test_getting_started.py`, therefore fits the convention better than
appending to `test_readme.py`.

## 2. Implementation status

Complete. `tests/test_getting_started.py` guards the getting-started demo path;
all existing tests still pass and the guarded page is unchanged.

## 3. Files changed

```text
Added:
  tests/test_getting_started.py               (3 focused guards)
  research/72-guard-getting-started-demo.md   (this record)

Modified:
  README.md                                    (test count 1134 -> 1138)
```

No `src/agentsec/**` change; no `labs/GETTING-STARTED.md` change; no policy,
config, schema, licensing, workflow or version change.

## 4. Exact invariants guarded

`tests/test_getting_started.py` pins three things, each with a message that says
what to update:

* **A — the documented commands.** Both
  `PYTHONPATH=src py -m agentsec demo lab04-two-policies` and
  `PYTHONPATH=src py -m agentsec demo lab04-two-policies --json` must still appear
  verbatim (not merely the word `demo`), so a reader can copy them.
* **B — the LAB-04 link.** The page must still contain the precise link target
  `LAB-04-tool-misuse/README.md#same-lab-different-policy`; the test also resolves
  the file **and** the anchor against the target page's real headings (a small
  GitHub/MkDocs slugger), so a renamed heading is caught, not just a missing
  file.
* **C — the section heading.** The exact heading
  `## 5. Try a two-policy comparison` must still be present among the page's
  `##` headings; if the step is legitimately renumbered or retitled the test
  fails and points at the `SECTION_HEADING` constant to update.

## 5. Test design

The module reads `labs/GETTING-STARTED.md` (and the LAB-04 page) directly with
`pathlib`; it uses **no** subprocess, **no** network, writes nothing, and asserts
nothing about the suite's size. It imports only `re` and `pathlib`, so the
architecture dependency guard is satisfied. The link check derives the anchor
from the target page's headings rather than hard-coding a slug, so it verifies the
real link, not a guess.

## 6. Validation results

| Check | Result |
| --- | --- |
| `python -m pytest` | **1138 passed** |
| `python -m pytest tests/test_getting_started.py` | **3 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | **All checks passed** |
| `python -m mypy` | **Success: no issues found in 42 source files** |
| `python -m mkdocs build --strict` | **exit 0** |
| `python scripts/check_licensing.py` | **9/9 passed** (236 files) |
| `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| `git diff --check` | clean |

**Test-count delta: 1134 → 1138 (+4)**: three new guard functions plus one new
parametrised case in `test_no_banned_dependency_in_tests` (the new test module).
The README's derived test-count row was updated to `1138` as required by
`tests/test_readme.py`.

## 7. Protected invariants

Untouched: `src/agentsec/**`, `scripts/release_check.py` and its warning
detection, the B5 exact-warning assertion, `scripts/pre_tag_check.py`, the release
manifest, `licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`,
`schemas/**`, the version declarations (`0.1.0`), both `.github/workflows/*.yml`,
the existing tags and archived evidence; no CI was added. `compare_traces`
semantics, `read_events` semantics, `TraceEvaluator` semantics, the demo, the demo
JSON schema, and `labs/GETTING-STARTED.md` are all unchanged. The gate stays
**READY WITH WARNINGS** with `blockers: []`.

## 8. Artifact cleanup

`mkdocs` was built into the default `site/` (then removed) and caches,
`__pycache__` and scratch directories were cleared after validation. The working
tree contains only the intended test, README and record changes.

## 9. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` (unchanged).
* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
