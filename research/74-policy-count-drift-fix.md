# PHASE 35 — POLICY-COUNT DOCUMENTATION DRIFT FIX

*A documentation-only correction: the repository now ships five example policies,
but two live documents still described or enumerated only four. This phase updates
those two references and nothing else. No runtime, test, config, lab, policy,
schema, CI or release-control file was touched. Nothing was committed, pushed or
tagged.*

## 1. Reconnaissance result

Read-only inspection before editing confirmed the drift and its exact extent:

* **Actual inventory** — `policies/examples/` contains **five** files:
  `deny_by_default.yaml`, `least_privilege_v1.yaml`, `allow_all_v1.yaml`,
  `lab06_excessive_agency_v1.yaml`, `lab07_data_leakage_v1.yaml`. The permissive
  `allow_all_v1.yaml` was added in Phase 7C and is not yet reflected everywhere.
* **Live stale references** — exactly two:
  * `README.md:94` stated "**four** example policies" and named only
    `deny_by_default`, `least_privilege_v1`, plus the two per-lab policies
    (LAB-06, LAB-07) — omitting `allow_all_v1`.
  * `docs/development.md:285` (the repository tree listing) enumerated the same
    four `policies/examples/` files, omitting `allow_all_v1`.
* **No other live drift** — a repo-wide search of `README.md`, `docs/`, and
  `labs/` found no other stale policy count or list. (`README.md:109` "four
  in-memory tools" is correct: there are four tools; `labs/GETTING-STARTED.md:148`
  "four things" is unrelated and correct.) References in `research/` are
  historical records/archived evidence and were deliberately left unchanged.

Decision: **documentation-only correction.** No test, guard, or runtime change is
justified; no existing documentation-guard convention requires a new test.

## 2. Exact stale references

| File / line | Before | After |
| --- | --- | --- |
| `README.md:94` | `four example policies (deny_by_default, least_privilege_v1, and one per-lab policy each for LAB-06 and LAB-07)` | `five example policies (deny_by_default, least_privilege_v1, allow_all_v1, and one per-lab policy each for LAB-06 and LAB-07)` |
| `docs/development.md:285` | `# deny_by_default, least_privilege_v1, lab06_excessive_agency_v1, lab07_data_leakage_v1` | `# deny_by_default, least_privilege_v1, allow_all_v1, lab06_excessive_agency_v1, lab07_data_leakage_v1` |

## 3. Exact files changed

```text
Modified:
  README.md             (policy-example count four -> five; added allow_all_v1)
  docs/development.md   (tree listing now includes allow_all_v1)

Added:
  research/74-policy-count-drift-fix.md   (this record)
```

No other file was modified. Nothing under `src/agentsec/**`, `tests/**`,
`configs/**`, `labs/**`, `policies/**`, `schemas/**`, `scripts/**`,
`licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`,
`.github/workflows/**`, the version declarations, the release manifest or any tag
was touched.

## 4. Actual policy-example inventory

`policies/examples/` (five files):

| File | Role |
| --- | --- |
| `deny_by_default.yaml` | no rules; every call denied (baseline) |
| `least_privilege_v1.yaml` | shared least-privilege policy (calculator + in-workspace reads) |
| `allow_all_v1.yaml` | permissive teaching extreme (added Phase 7C) |
| `lab06_excessive_agency_v1.yaml` | per-lab policy for LAB-06 |
| `lab07_data_leakage_v1.yaml` | per-lab policy for LAB-07 |

The corrected `README.md:94` row now names the three shared examples and
summarises the two per-lab policies; the corrected `docs/development.md:285` tree
line enumerates all five filenames.

## 5. Correction made

* **README.md** — the `policies/examples/` row now reads "**five** example
  policies" and lists `deny_by_default`, `least_privilege_v1`, `allow_all_v1`,
  then the two per-lab policies. No policy was invented, renamed or removed; the
  wording keeps the existing "one per-lab policy each for LAB-06 and LAB-07"
  phrasing.
* **docs/development.md** — the `policies/examples/` line in the repository tree
  now lists `allow_all_v1` in addition to the four existing names.

Both are pure text corrections of a confirmed drift; no semantic or behavioural
change.

## 6. Validation results

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1144 passed** (unchanged) |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** @ 240 files |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |

**Test count unchanged at 1144** — this phase added no test, as reconnaissance
found no existing guard convention that requires one and the repository's
documentation is not count-guarded for this row.

## 7. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`,
`.freebuff/project-id`, `schemas/**`, `compare_traces`/`TraceEvaluator`, the demo
implementation, the release manifest, the version declarations (`0.1.0`), the lab
runtime semantics, and both `.github/workflows/*.yml`. The gate stays **READY
WITH WARNINGS** with `blockers: []`.

## 8. Artifact cleanup

Removed the `site/` directory written by `mkdocs build --strict` and all
`__pycache__` directories, plus the standard caches (`.mypy_cache`,
`.ruff_cache`, `.pytest_cache`, `build`, `dist`, `htmlcov`, `.mkdocs-build`).
Licensing was re-confirmed **9/9 @ 240 files** after cleanup; no generated
artifacts remain.

## 9. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` ("phas QA complete") — unchanged.
* `v0.0.1` and `v0.1.0` are **unchanged**; `git rev-parse v0.1.0^{commit}` is
  `3d731b0dffece499cc54a22d51701cdeecdce39f`.
* No tag was created, modified, deleted or moved.

## 10. Confirmation

* **No commit** was made.
* **No push** was performed.
* **No tag** was created, moved, deleted or published.
* **No publication** or release action occurred.

The documentation correction remains in the working tree alongside the earlier
uncommitted Phase 6A–7H work.
