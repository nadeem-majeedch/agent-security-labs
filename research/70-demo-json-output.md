# PHASE 31 — MACHINE-READABLE OUTPUT FOR THE DEMO COMMAND

*Adds `--json` to `agentsec demo lab04-two-policies`, matching the other read-only
commands. This is a **CLI output-consistency** change only: demo semantics,
comparison semantics, lab behaviour, runtime security logic and release controls
are unchanged. Nothing was committed, pushed or tagged.*

## 1. Reconnaissance

Inspection before editing:

* **Existing `--json` conventions.** `agentsec run` and `agentsec evaluate` print
  `result.model_dump_json(indent=2)` (a pydantic model). `agentsec compare` prints
  `json.dumps(result, indent=2)` over the plain comparison dict. A structured,
  machine-readable result therefore already exists for the demo to embed — no new
  schema style is invented.
* **`agentsec demo`** had no output options, so nothing is mutually exclusive with
  a new `--json`.
* **`demo.py`** already builds a `DemoOutcome` carrying the labels and the
  `compare_traces` result; the JSON document reuses that comparison rather than
  recomputing anything.
* **Error path.** `main()` catches `ConfigError`/`EvaluationError`/`OSError`/
  `ValueError` (exit `1`) and prints `error: …` to stderr; because the CLI prints
  only after the demo finishes, a failure cannot emit partial JSON.
* **Architecture guards** unchanged: `demo.py` still contains no `.run(` and no
  execution engine; `cli.py` stays thin; `test_lab00_cli_is_available` only checks
  a subcommand **superset**.

## 2. Implementation status

Complete. `agentsec demo lab04-two-policies --json` (and
`python -m agentsec demo lab04-two-policies --json`) emit exactly one
deterministic JSON document on stdout.

## 3. Files changed

```text
Modified:
  src/agentsec/demo.py                        (DEMO_TITLE, DEMO_SCHEMA_VERSION,
                                               DemoOutcome.policies, demo_to_dict)
  src/agentsec/cli.py                         (demo --json flag; _cmd_demo branch)
  tests/cli/test_demo.py                      (JSON tests, +12)
  docs/development.md                         (CLI section: --json)
  labs/LAB-04-tool-misuse/README.md           (one-command section: --json)
  README.md                                   (test count 1122 -> 1134)

Added:
  research/70-demo-json-output.md             (this record)
```

`DemoOutcome` gained a `policies: tuple[str, ...]` field (the two runs' relative
policy paths); `render_demo` now shares the `DEMO_TITLE` constant but produces the
identical string as before.

## 4. JSON schema summary

Top-level keys (exactly six): `schema_version`, `demo`, `title`, `status`,
`policies`, `comparison`.

```json
{
  "schema_version": "1",
  "demo": "lab04-two-policies",
  "title": "LAB-04 under two policies",
  "status": "ok",
  "policies": [
    {"trace": "A", "label": "permissive (allow_all_v1)",
     "policy": "policies/examples/allow_all_v1.yaml"},
    {"trace": "B", "label": "least privilege (least_privilege_v1)",
     "policy": "policies/examples/least_privilege_v1.yaml"}
  ],
  "comparison": { /* the full compare_traces result */ }
}
```

The nested `comparison` is the unchanged `compare_traces` document (trace A/B
identity `run_id`/`scenario`/`event_count`, `event_count_delta`,
`event_type_distribution`, `sequence`, `evaluator` status and differences, and the
alignment `notes`). Trace paths are **not** included — identity is each trace's own
`run_id`/`scenario`, and policies are **relative POSIX paths** (via
`Path.as_posix()`), so there are no absolute paths, backslashes, temporary
directory names, timestamps, host details or generated ids.

## 5. Default-output compatibility

Unchanged. `render_demo` still prints the same heading and comparison; a test
asserts the default output starts with `LAB-04 under two policies` and is **not**
valid JSON. The only refactor is using the shared `DEMO_TITLE` constant, which
yields the identical text.

## 6. Determinism

`agentsec demo lab04-two-policies --json` run twice produced byte-identical JSON.
The comparison document contains no timestamps (property of Phase 7B), and the
demo adds only static fields, so the output is deterministic even though the CLI
runs the real stack with the real clock.

## 7. Test coverage

Extended `tests/cli/test_demo.py` with **12** JSON tests (module total 26): valid
JSON with exactly the six intended top-level fields; correct `demo` name, title
and `status`; both policies (paths and labels) represented; trace identity,
event counts and delta represented; evaluator differences represented;
`demo_to_dict` **reuses** the comparison object (identity check); no volatile
values (`trace_path`, `timestamp`, temp-dir markers, `chr(92)` backslash);
deterministic across two executions; default human output unchanged and not JSON;
`--json` leaves no traces in `runs/` and does not modify repository files;
failure emits no partial stdout (only stderr) with exit `1`; unknown name with
`--json` is still a usage error. The existing real end-to-end smoke test remains.

## 8. Real end-to-end result

Both `agentsec demo lab04-two-policies` and `… --json` ran against the real MVP
stack. The JSON reported 12 vs 11 events and the same evaluator differences as the
text mode (`decisions.allow 1→0`, `decisions.deny 0→1`, `tool_results.denied 0→1`,
`tool_results.error 1→0`).

## 9. Validation results

| Check | Result |
| --- | --- |
| `python -m pytest` | **1134 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | **All checks passed** |
| `python -m mypy` | **Success: no issues found in 42 source files** |
| `python -m mkdocs build --strict` | **exit 0** |
| `python scripts/check_licensing.py` | **9/9 passed** (233 files) |
| `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| `git diff --check` | clean |

**Test count: 1122 → 1134 (+12).** The README's derived test-count row was updated
to `1134` as required by `tests/test_readme.py`.

## 10. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `scripts/pre_tag_check.py`, the release manifest,
`licensing/manifest.toml`, `.gitignore`, `.freebuff/project-id`, `schemas/**`, the
version declarations (`0.1.0`), both `.github/workflows/*.yml`, the existing tags
and archived evidence; no CI was added. `compare_traces` semantics, `read_events`
semantics, `TraceEvaluator` semantics and LAB-04 are unchanged. The gate stays
**READY WITH WARNINGS** with `blockers: []`.

## 11. Artifact cleanup

Traces are written only into the CLI's temporary directory (removed on exit) and
the demo overrides `trace_path`, so nothing lands in `runs/`. All caches,
`__pycache__`, and build/site output were removed; the working tree contains only
the intended source/test/docs changes.

## 12. Git / tag state

* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
