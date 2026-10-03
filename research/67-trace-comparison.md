# PHASE 28 — DETERMINISTIC READ-ONLY TRACE COMPARISON

*A new read-only CLI command, `agentsec compare <trace-a> <trace-b>`, that reports
the factual structural differences between two existing traces so a learner can
ask **"what changed between these two runs?"** It reuses the existing trace reader
and evaluator, introduces no new events, metrics, scores or claims, and neither
modifies a trace nor adds CI. Nothing was committed, pushed or tagged.*

## 1. Reconnaissance

Read-only inspection of the existing architecture before any code was written:

* **Trace reader** — `agentsec.trace.writer.read_events(path)` returns a list of
  raw event mappings and raises `json.JSONDecodeError`/`OSError` for malformed or
  missing input.
* **Event model** — `agentsec.trace.schema.TRACE_EVENT_TYPES` defines the 12
  event types in canonical order; each event carries `run_id`, `scenario`,
  `event_type`, `seq`, `event_id`, `parent_event_id`, etc.
* **Evaluator** — `agentsec.eval.TraceEvaluator` is a pure, read-only function of
  the events; `EvaluationInput.from_events` adapts them; `EvaluationResult`
  carries `status`, `metrics`, `decisions`, `tool_calls`, `tool_results`, `flags`,
  `warnings` and `evidence`. It computes no score.
* **CLI** — `agentsec.cli` is a thin `argparse` interface; `main()` catches
  `ConfigError`/`EvaluationError`/`OSError`/`ValueError` and returns exit `1` for
  input problems, `2` for orchestration failures. `evaluate`/`inspect` read a
  trace and never rerun anything. Existing CLI tests (`tests/cli/test_cli.py`,
  `test_inspect.py`) call `main([...])` and assert exit codes and captured output.
* **Architecture guards** — `tests/test_architecture.py` parametrises over
  `python_files(SRC)` and `python_files(TESTS)` (so a new module in either tree is
  picked up automatically) and enforces the layering/import rules; the CLI must not
  import concrete execution layers and must contain no execution logic.
* **`runs/` is git-ignored** and holds only generated traces, so a real lab-pair
  test must generate traces into `tmp_path` from the lab configs (the pattern used
  by `tests/labs/test_lab0*.py`).

## 2. Design decision

* **New module `src/agentsec/compare.py`** rather than an addition to `eval/` or
  `cli.py`: it is a read-only *analysis* concern that composes the evaluator, and
  a separate module keeps `cli.py` thin and avoids overloading the evaluator
  package. It imports only `errors`, `eval`, `trace.schema` and `trace.writer`
  (plus stdlib), so it satisfies the layering rules.
* **Thin CLI subcommand** `compare <trace_a> <trace_b> [--json]`, mirroring
  `evaluate`/`inspect` and their `--json` convention.
* **Positional alignment only.** No semantic event-equivalence rule exists in the
  trace model, so none is invented: events are compared **by position**, and the
  output states this limitation explicitly rather than guessing an alignment.
* **Plain dict output** (JSON-ready), rendered to text by `render_comparison`,
  matching the `labs check`/`selfcheck` style of a computed mapping rather than a
  second pydantic model.
* **Errors mirror `evaluate`.** A missing or malformed trace is an input problem:
  `load_trace` raises `EvaluationError` with a clear message, `main` prints
  `error: …` to stderr and returns `1`. No partial comparison is printed, and the
  command never emits a stack trace.

## 3. Files changed

```text
Added:
  src/agentsec/compare.py            (read-only comparison logic + renderer, MIT)
  tests/cli/test_compare.py          (focused tests + real lab-pair integration, MIT)
  research/67-trace-comparison.md    (this record, CC BY 4.0)

Modified:
  src/agentsec/cli.py                (import + `compare` subcommand + _cmd_compare)
  docs/development.md                (CLI section: command + description)
  labs/README.md                     (student-facing "Comparing two traces" section)
  README.md                          (CLI row; test count 1085 -> 1103, see §6)
```

No other file was touched.

## 4. Comparison semantics

`compare_traces(a, b)` reads both traces via `read_events`, evaluates each via
`TraceEvaluator`, and returns a dict with:

* `trace_a` / `trace_b`: `run_id`, `scenario`, `event_count` (each trace's own
  values — **no file paths are included**).
* `event_count_delta`: A minus B.
* `event_type_distribution`: one row per event type present in either trace —
  `{event_type, a, b, delta}`.
* `sequence`: `{identical, length_a, length_b, changed, only_in_a, only_in_b}`
  where `changed` lists positions in the common prefix whose types differ,
  `only_in_a`/`only_in_b` list positions beyond the shorter trace.
* `evaluator`: `{status: {a, b}, differences: [...]}`, where each difference is
  `{section, key, a, b}` for the evaluator fields that differ — `status`, then the
  `decisions` / `tool_results` / `tool_calls` / `flags` mappings (keys unioned and
  sorted), then `warnings` when the lists differ.
* `notes`: the alignment limitation, stated verbatim.

Deliberately **not** compared or produced: no similarity/risk/effectiveness
score, no ranking, no "better/worse" judgement, no semantic event matching, no
payload-diffing engine, no timeline/visualisation, and no re-run of either trace.

## 5. Deterministic ordering

* **Event types** are ordered by canonical schema order (`TRACE_EVENT_TYPES`),
  then any unknown types alphabetically, with the unclassified label last.
* **Evaluator mapping keys** are iterated in `sorted(set(a) | set(b))`; the
  `status` difference is emitted first, `warnings` last; sections follow a fixed
  order.
* **Sequence differences** are emitted in ascending index order.
* **No timestamps, absolute paths, host details or generated identifiers** appear
  in the output — identity is the traces' own `run_id`/`scenario`, so the same two
  input traces always render identical bytes. (Error messages on stderr may name
  the path given, which is not part of the comparison document.)

## 6. Tests

New module `tests/cli/test_compare.py` (16 tests):

* identical traces → identical sequence, no evaluator differences;
* different event counts → correct delta;
* event-type distribution reports both traces, and uses canonical order then
  unknown-sorted;
* ordered sequence: positional change; events only in A / only in B;
* the alignment limitation is stated in output;
* evaluator differences (deny/allow decisions between two synthetic traces);
* deterministic output; the comparison modifies neither trace;
* CLI exit status `0` and human output; `--json` structure; CLI determinism;
* missing trace → exit `1`; malformed trace → exit `1`;
* **real lab-pair integration**: LAB-01 (allowed calculator) vs LAB-04 (denied
  tool misuse), generated from the lab configs with a fixed clock — asserts the
  scenarios, that the sequences differ, that `decisions.deny` and
  `tool_results.denied` differences surface, that the render is deterministic, and
  that neither trace is modified.

**Test count: 1085 → 1103 (+18).** Breakdown: +16 for `tests/cli/test_compare.py`,
+1 from `tests/test_architecture.py::test_no_banned_dependency_in_source`
(parametrised over `src/agentsec/*.py`, gaining `compare.py`), +1 from
`…::test_no_banned_dependency_in_tests` (parametrised over `tests/**/*.py`,
gaining the new test module). No existing test was weakened or removed, and no
manual architecture update was needed.

## 7. Validation

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1103 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 41 source files** |
| Docs | `python -m mkdocs build --strict` | **rc 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| New command | `agentsec compare <LAB-01> <LAB-04>` | exit `0`; deterministic; traces unchanged |

## 8. Limitations

* The comparison is **structural, not semantic**: two traces with the same event
  types in the same order can still differ in payload, and `compare` reports no
  sequence difference for them (it does report evaluator-field differences). This
  is stated in the output.
* Positional alignment is only as meaningful as the traces are similar; an
  insertion early in a trace shifts every later position. `compare` reports the
  shifted positions as changes rather than guessing a better alignment.
* It reports the evaluator's already-descriptive numbers; it interprets nothing,
  and it cannot tell whether a difference is "good" or "bad".
* It is a two-trace comparison only; it does not compare more than two, nor a
  directory of traces.
* It adds no CI step and no release control, and it makes no novelty,
  effectiveness, security or benchmark claim.

## 9. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`
(no edit — new files are covered by existing globs), `.freebuff/project-id`,
`schemas/**` (no new or changed event), the release manifest, the version
declarations (`0.1.0`), the existing lab runtime semantics, and both
`.github/workflows/*.yml` (no CI integration was added). The gate stays **READY
WITH WARNINGS** with `blockers: []`.

## 10. Git / tag state

* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
