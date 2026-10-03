# PHASE 32 — TWO-POLICY DEMO ON THE GETTING-STARTED PATH

*Documentation-only discoverability change. The existing `agentsec demo
lab04-two-policies` command (and its `--json` form) is surfaced as a guided step
in the student getting-started sequence. No runtime functionality, comparison
semantics or JSON schema changed. Nothing was committed, pushed or tagged.*

## 1. Reconnaissance

Inspection before editing:

* **`labs/GETTING-STARTED.md`** is the student-guided path: install → run/inspect/
  evaluate a first lab → work through the labs → read a trace → check the setup.
  It had **no** section about comparing traces, and no mention of `demo`.
* **`labs/README.md`** already documents `compare` (and links LAB-04's "Same lab,
  different policy"); **`labs/LAB-04-tool-misuse/README.md`** already carries the
  full two-policy worked example plus the "One-command demonstration" section,
  including `--json`. Both are **references**, not the guided path.
* **`README.md`** lists `demo` in its CLI summary row; **`docs/development.md`**
  is the CLI/architecture reference. Neither is the student's first-run path.
* **No existing test guard covers `labs/GETTING-STARTED.md`.** The documentation
  guards that exist cover the README verification table
  (`tests/test_readme.py`), the trace exercises (`tests/test_trace_exercises.py`),
  the release manifest (`tests/test_release_manifest.py`) and the accepted
  warnings — not this page.

The natural placement is a new numbered step **after** "Learn to read a trace"
(you have just read one trace; the next question is *what changed* between two)
and **before** "Check your setup stays healthy".

## 2. Implementation status

Complete. Section **5. Try a two-policy comparison** was inserted into
`labs/GETTING-STARTED.md`; the former "Check your setup stays healthy" became
section **6** (its text is unchanged).

## 3. Files changed

```text
Modified:
  labs/GETTING-STARTED.md                     (new section 5; section 6 renumbered)

Added:
  research/71-getting-started-two-policy-demo.md   (this record)
```

No `src/agentsec/**` change; no test change; no README test-count change (no new
test module, so the derived count is untouched).

## 4. Exact section location

`labs/GETTING-STARTED.md`, heading `## 5. Try a two-policy comparison`, between
the "Learn to read a trace" section (`## 4.`) and the renumbered
`## 6. Check your setup stays healthy`.

## 5. Commands documented

```bash
PYTHONPATH=src py -m agentsec demo lab04-two-policies
PYTHONPATH=src py -m agentsec demo lab04-two-policies --json
```

Both were run against the real stack during validation and behave as documented.

## 6. Student-learning flow

1. **Run the demonstration** — one command runs the same LAB-04 scenario twice
   into a temporary directory (removed on exit) and prints one comparison.
2. **Observe the two policies** — Trace A runs under `allow_all_v1` (permissive
   example), Trace B under `least_privilege_v1` (the policy LAB-04 ships with);
   task, fixture and agent are identical, only the policy differs.
3. **Inspect the comparison** — the same read-only `compare` machinery (counts,
   event-type distribution, positional-only sequence, evaluator differences); no
   score, no "better/worse".
4. **Try the JSON form** — `--json` emits one machine-readable document (the two
   policies plus the full comparison) for tooling.
5. **Think about why the traces differ** — three short questions (which event
   types differ; what happens to the tool request under each policy; why the
   comparison reports positional differences rather than a score), with **no**
   evaluative answer supplied.

The section keeps DRY: it does not repeat the LAB-04 scenario, the policy YAML,
the full comparison output, the JSON schema or the implementation; it links to
LAB-04's detailed worked example
(`LAB-04-tool-misuse/README.md#same-lab-different-policy`) and points at
`agentsec --help` and the CLI reference in `docs/development.md`.

## 7. Tests

No test was added. The reconnaissance found **no existing guard** for
`labs/GETTING-STARTED.md`, and the repository convention does not clearly require
one for every lab page (only the README table, the trace exercises and the
release artefacts are guarded). Adding a guard here would add a new test module
(+1 collected test) and force a README test-count edit for a purely editorial
page, so the convention was judged **not** to require it. The page's correctness
is still covered structurally by `mkdocs build --strict`, which fails on a broken
relative link (the LAB-04 anchor) and on a malformed page. No existing test was
modified or weakened.

## 8. Validation results

| Check | Result |
| --- | --- |
| `python -m pytest` | **1134 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | **All checks passed** |
| `python -m mypy` | **Success: no issues found in 42 source files** |
| `python -m mkdocs build --strict` | **exit 0** (link to the LAB-04 anchor resolves) |
| `python scripts/check_licensing.py` | **9/9 passed** (234 files) |
| `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| `git diff --check` | clean |

**Test-count delta: 0 (1134 → 1134).** No test was added, so the README's derived
test-count row is unaffected.

## 9. Protected invariants

Untouched: `src/agentsec/**`, `scripts/release_check.py` and its warning
detection, the B5 exact-warning assertion, `scripts/pre_tag_check.py`, the release
manifest, `licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`,
`schemas/**`, the version declarations (`0.1.0`), both `.github/workflows/*.yml`,
the existing tags and archived evidence; no CI was added. `compare_traces`
semantics, `read_events` semantics, `TraceEvaluator` semantics, the demo
implementation and the demo JSON schema are all unchanged. The gate stays **READY
WITH WARNINGS** with `blockers: []`.

## 10. Artifact cleanup

`mkdocs` was built into a scratch directory (`.mkdocs-build/`) that was removed;
`runs/` (gitignored) was left as found. All caches and `__pycache__` directories
were removed after validation. The working tree contains only the intended
documentation change and this record.

## 11. Git / tag state

* Branch `v0.1.0-dev`, HEAD `e831e0c` (unchanged).
* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
