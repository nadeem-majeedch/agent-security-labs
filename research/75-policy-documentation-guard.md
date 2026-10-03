# PHASE 36 — GUARDING THE POLICY-EXAMPLE DOCUMENTATION

*Adds one focused documentation-consistency guard so the example-policy
inventory cannot drift again between the files on disk and the two live
documents that describe it. This is a **test + documentation** change: no
runtime, policy, config, schema, CI or release-control file was touched. Nothing
was committed, pushed or tagged.*

## 1. Reconnaissance findings

Read-only inspection before editing:

* **Actual inventory** — `policies/examples/` holds **five** `*.yaml` files:
  `allow_all_v1.yaml`, `deny_by_default.yaml`, `lab06_excessive_agency_v1.yaml`,
  `lab07_data_leakage_v1.yaml`, `least_privilege_v1.yaml`. Every example ends in
  the `_v1` naming convention.
* **Two live locations describe it** — the root `README.md` project table row
  for `policies/examples/` (line 94) and the `policies/examples/` line of the
  repository tree in `docs/development.md` (line 285). Each file mentions
  `policies/examples/` exactly once, so each has a single, unambiguous target.
* **The drift that motivated Phase 7I** — Phase 7C added `allow_all_v1` but the
  README said "four example policies" and its row omitted the per-lab filenames
  (`lab06_excessive_agency_v1`, `lab07_data_leakage_v1`), while the development
  tree line listed only four filenames. Phase 7I corrected the count but nothing
  prevented the drift from recurring.
* **Historical records** — `research/14`, `research/27` and `research/39` also
  enumerate example policies; these are historical snapshots and are
  intentionally out of scope for the guard.

Decision: add one focused guard module plus the small README row correction its
README invariant requires. No runtime or policy change.

## 2. Existing documentation-guard convention

The repository keeps one focused module per documentation artefact, each with a
module docstring that states the invariant and that it is "not a content review",
`from __future__ import annotations`, `pathlib`/`re` only, small helpers, and
set-difference assertions with messages naming the offending entries:

* `tests/test_readme.py` — the root README verification table (count derived from
  `pytest --collect-only` in a child process) plus a `docs/development.md` note.
* `tests/test_getting_started.py` — the guided getting-started comparison steps.
* `tests/test_trace_exercises.py` — the exercises/answer-key pair.
* `tests/test_release_manifest.py` — the release manifest page.

None hard-codes a test count, and the repository's only count guard
(`tests/test_readme.py`) derives the number from the suite. The new guard follows
the same shape: it **derives** the inventory from the filesystem and never
hard-codes the count or the filenames.

## 3. Actual policy-example inventory

| File | Role |
| --- | --- |
| `deny_by_default.yaml` | no rules; every call denied |
| `least_privilege_v1.yaml` | shared least-privilege policy |
| `allow_all_v1.yaml` | permissive teaching extreme (Phase 7C) |
| `lab06_excessive_agency_v1.yaml` | per-lab policy for LAB-06 |
| `lab07_data_leakage_v1.yaml` | per-lab policy for LAB-07 |

## 4. README invariant

The `policies/examples/` project-table row must:

* name **every** current example (by filename stem), and
* name **no** example that no longer exists, and
* state the **correct** count (the spelled-out number is parsed, not assumed).

The row was corrected in this phase to name all five examples:

```text
five example policies: `deny_by_default`, `least_privilege_v1`, `allow_all_v1`,
`lab06_excessive_agency_v1`, `lab07_data_leakage_v1`
```

(`tests/test_policy_documentation.py` reads the row's inline-code tokens as the
documented set, so the two per-lab examples must be named literally rather than
described.)

## 5. Development-documentation invariant

The `policies/examples/` line of the repository tree in `docs/development.md`
must list every current example filename stem and no stale one. The comma-list
after the line's trailing `#` is parsed and compared to the filesystem in both
directions.

## 6. Guard design

`tests/test_policy_documentation.py` (read-only, `pathlib`/`re`, no subprocess,
no network, no generated files) provides:

* `_example_stems()` — derives the inventory from `policies/examples/*.yaml`.
* `_readme_policy_line()` / `_readme_documented_names()` — locate the README row
  and read its inline-code tokens.
* `_development_documented_names()` — parse the tree line's comma-list.

and five assertions:

1. `test_policy_example_inventory_is_discovered` — the inventory is non-empty
   (guard sanity).
2. `test_readme_documents_every_policy_example` — no example is missing from the
   README row.
3. `test_readme_has_no_stale_policy_example_entries` — the README names nothing
   that no longer exists.
4. `test_readme_states_the_correct_policy_example_count` — the spelled-out count
   equals the number of files on disk.
5. `test_development_docs_document_every_policy_example` — the development tree
   line names every example and nothing stale.

Failure messages name the missing or stale filename (or the stated-vs-actual
count). The number "5" and the filenames are never hard-coded. `research/` is not
scanned.

## 7. Exact files changed

```text
Added:
  tests/test_policy_documentation.py          (5 focused guards)
  research/75-policy-documentation-guard.md   (this record)

Modified:
  README.md    (policy-example row now names all five filenames;
                derived test-count row 1144 -> 1150)
```

No `src/agentsec/**`, `policies/**`, `configs/**`, `labs/**`, `schemas/**`,
`scripts/**`, `licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`,
`.github/workflows/**`, version declaration or release manifest change.

## 8. Test-count delta

**1144 → 1150 (+6):** the five new guard functions plus the single case the
`tests/test_architecture.py` parametrisation adds for the new test module
(`test_no_banned_dependency_in_tests`). The README's derived test-count row was
updated to `1150` via the existing `tests/test_readme.py` mechanism; no second
hard-coded count was introduced.

## 9. Validation results

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1150 passed** |
| New guard | `python -m pytest tests/test_policy_documentation.py` | **5 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 242 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |

## 10. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`
(covered by existing globs), `.freebuff/project-id`, `schemas/**`, the policy
files themselves, `compare_traces`/`TraceEvaluator`, the demo implementation, the
release manifest, the version declarations (`0.1.0`), the lab runtime semantics,
and both `.github/workflows/*.yml`. The gate stays **READY WITH WARNINGS** with
`blockers: []`.

## 11. Artifact cleanup

Removed the `site/` directory written by `mkdocs build --strict` and all
`__pycache__` directories, plus `.mypy_cache`, `.ruff_cache`, `.pytest_cache`,
`build`, `dist`, `htmlcov` and `.mkdocs-build`. Licensing was re-confirmed after
cleanup; no generated artifacts or scratch directories remain.

## 12. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` — unchanged.
* `v0.0.1` and `v0.1.0` are **unchanged**; `git rev-parse v0.1.0^{commit}` is
  `3d731b0dffece499cc54a22d51701cdeecdce39f`.
* No tag was created, modified, deleted or moved.

## 13. Confirmation

No commit was made, no push was performed, no tag was created/moved/deleted, and
no publication or release action occurred. The change remains in the working tree
alongside the earlier uncommitted Phase 6A–7I work.
