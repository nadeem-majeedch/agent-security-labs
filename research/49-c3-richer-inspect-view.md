# PHASE 21 — PHASE 4 C3: RICHER READ-ONLY INSPECT VIEW

*Implementation record for `research/39` item **C3** — the last Phase 4 item.
Nothing was committed, pushed, tagged or version-bumped; the Phase 17 freeze and
the `v0.0.1` release are untouched. No new runtime semantics were introduced and
no **LAB-08** was created.*

## 1. C3 objective (from `research/39`)

* `research/39` §9 **C3 [PROPOSED]** — "Add a richer `inspect` view (e.g.
  `--events`, or show `flag`/`side_effects` inline) — still read-only, no viewer
  framework."
* §11 lists C3 under "Optional if time allows (should)".
* §16 — a trace-field reference page; §14 — keep the suite hermetic and offline.

The goal: make it easier for a learner to read an existing trace — event
sequence, event type, existing identifiers, payload fields, `side_effects`,
flags — **without** changing any runtime behaviour.

## 2. Existing trace / CLI architecture inspected

* **CLI** (`src/agentsec/cli.py`, stdlib only): subcommands `run`, `evaluate`,
  `inspect`, `labs`. `inspect <trace>` already prints a header plus **one line
  per event** (`seq`, `event_type`, `event_id`, `parent=…`). Rendering helpers
  (`_render_result`, `_render_evaluation`) already live here.
* **Trace I/O** (`src/agentsec/trace/writer.py`): `read_events(path)` returns a
  `list[dict[str, Any]]` of the raw JSONL event mappings — the single existing
  reader.
* **Evaluator** (`src/agentsec/eval/`): `TraceEvaluator().evaluate(EvaluationInput
  .from_events(events))` returns a read-only `EvaluationResult` with `flags`
  (`has_run_started`, `has_terminal_event`, `produced_final_output`,
  `reached_step_limit`, `has_tool_requests`), `warnings`, `metrics`, counts and
  `evidence`. `evaluate` already uses exactly this.
* **Schema**: `side_effects` is an optional `tool_result` field; no `flags` field
  exists **in the trace** — flags are the evaluator's derived booleans.
* **Architecture tests**: `cli.py` must not reference `.complete(`, `.invoke(`,
  `.decide(`, `while `, `ToolCall`, `ModelResponse`, and must not import the
  concrete execution layers. C3 respects all of these.

## 3. Exact implementation

Smallest coherent change, in the existing `inspect` subcommand:

1. `build_parser()` gains an `--events` flag on `inspect` (default `False`, so the
   existing summary is unchanged).
2. `_cmd_inspect()` branches: when `--events` is given it reuses the **existing**
   reader and **existing** evaluator
   (`TraceEvaluator().evaluate(EvaluationInput.from_events(events))`) and prints
   `render_inspection(events, evaluation, path=path)`; otherwise it runs the
   original code unchanged.
3. New module-level `render_inspection(events, evaluation, *, path)` returns the
   full text, and `_display(value)` renders one value deterministically
   (`None` → `-`, booleans → `true`/`false`, dict/list → sorted JSON, else `str`).

The rendering function is deliberately separate from the CLI wrapper so it can be
tested directly. Nothing executes: no agent, model, gateway, policy or tool is
touched, and the trace file is opened read-only through `read_events`.

## 4. Why it is read-only

* It calls only `read_events` (a read) and the pure `TraceEvaluator.evaluate`
  (a read-only analysis of already-parsed events).
* It writes no files, creates no directories, opens no sockets, and never
  re-runs an experiment.
* The CLI keeps its existing semantics: no mutation of labs, sources or trace
  files (asserted by a byte-for-byte test).

## 5. Output design (deterministic)

```
trace: runs/lab06_excessive_agency/trace.jsonl
run: lab06-run-1
events: 12

Event 7
  type: tool_result
  event_id: ev-000007
  seq: 7
  parent: ev-000006
  fields:
    error: -
    ok: true
    result_hash: 8f0c...
    side_effects: ["deleted 2 row(s) from audit_log"]

Side effects:
  ev-000007  ["deleted 2 row(s) from audit_log"]

Flags:
  has_run_started: true
  has_terminal_event: true
  has_tool_requests: true
  produced_final_output: true
  reached_step_limit: false

Warnings:
  none
```

* **Payload fields** are the event's keys minus the ten shared **envelope** fields
  (run/event ids, `seq`, timestamp, agent, model, scenario, `schema_version`,
  `event_type`, `parent_event_id`) — the same header/extras split the C5 field
  reference uses — printed in **sorted order**.
* **Side effects** lists every event whose `side_effects` is non-empty (or
  `none`).
* **Flags** and **Warnings** are the evaluator's existing values, **sorted** for
  determinism.
* `--events` output is fully derived from the parsed events and the existing
  evaluator — no field is invented and no field name is duplicated from the
  schema by hand.

## 6. Tests added

`tests/cli/test_inspect.py` (10 tests) exercises the formatting function directly
and the CLI wrapper:

1. event information is included (type, `event_id`, `seq`, `parent`, payload);
2. `side_effects` are shown when present;
3. absent `side_effects` render `none` without crashing;
4. flags are shown;
5. output is deterministic (formatting function, twice);
6. the CLI richer view prints the event/payload/side-effects/flags sections;
7. the CLI richer view is deterministic (two runs, identical capture);
8. the CLI richer view does **not** modify the trace (byte comparison);
9. plain `inspect` (no `--events`) keeps its original summary;
10. a missing trace is still a config error (exit 1).

No existing test was weakened.

## 7. Documentation changes

`labs/README.md` gains a short **"Richer inspection: `inspect --events`"** section
after *How to run a lab*: the command, a representative output block, and a note
that it only reads the trace. It points at the existing
`TRACE-READING-EXERCISES.md` and the generated `TRACE-FIELD-REFERENCE.md`, and
says the flags/warnings are the same ones `agentsec evaluate` reports — so it
does **not** duplicate field-by-field schema detail (that stays in C5's generated
page). No new page and no navigation change were needed; the strict MkDocs build
stays green.

## 8. No new runtime semantics

The change adds a **display-only** option. It does not alter the agent, model,
gateway, policy engine, tools, trace schema, recorder, writer, evaluator or any
lab definition. The plain `inspect` output and every other command are
byte-for-byte unchanged.

## 9. LAB-08

Not created. The repository still contains exactly **LAB-00 … LAB-07**.

## 10. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **880 passed** (869 → 880) |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `python -m mypy` | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 195 files accounted for (mit 131, cc-by 62, excluded 2, unlicensed 0), including this record |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]` |
| `git diff --check` | clean |
| `git status --short` | only C3 + earlier uncommitted work; no artifacts |

**Test-count delta: 869 → 880 (+11):** 10 new tests in
`tests/cli/test_inspect.py`, plus **1** automatic case in
`tests/test_architecture.py`, which parametrises over every `tests/*.py` file and
therefore now guards the new test module too.

The feature was also exercised manually against a real trace produced by
`agentsec run labs/LAB-06-excessive-agency/config.yaml`: `inspect --events`
printed all 12 events, the payload fields, the single
`["deleted 2 row(s) from audit_log"]` side effect, and the five flags.

## 11. Files changed

```
src/agentsec/cli.py              (+ --events flag; + render_inspection/_display/_ENVELOPE_FIELDS)
labs/README.md                   (+ "Richer inspection: inspect --events" section)
tests/cli/test_inspect.py        (new, 10 tests)
research/49-c3-richer-inspect-view.md   (this record, new)
```

## 12. Files explicitly left untouched

`scripts/release_check.py`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`,
`pyproject.toml`, `schemas/`, the trace schema and `src/agentsec/trace/` sources,
all `labs/LAB-*` definitions, the warning policy (`tests/test_release_check.py`),
and the package version. `research/39` and all earlier research records are
unmodified. The pre-existing B4.x/D1/C1/C5 working-tree changes are unchanged by
this step. Version remains **`0.0.1`**; the **`v0.0.1`** tag is untouched
(`cd60b32c7da3174423657e3ec53ecb7dd120eecb`).

## 13. Remaining Phase 4 / Phase 5 work

* **Phase 4:** complete. Optional **C4** (use the three unused mock fixtures
  without adding a numbered lab) remains unimplemented and was **not** required
  by C3.
* **Phase 5 (release decision):** pending — version bump to `0.1.0` across the
  three declarations, `date-released` (closes W6), the W7/W12 decisions, and the
  `v0.1.0` change record. B5's exact warning-set assertion is already in place
  and will need its `ACCEPTED_RELEASE_WARNINGS` policy updated deliberately at
  that point.

### Safety boundary (Phase 17)

This step adds a read-only display option only: no research implementation, no
corpus, no experiment and no learner data. Phase 17 remains **CLOSED**; E1
remains **HOLD**; no novelty, effectiveness, security-effectiveness, benchmark or
publication claim is made. No LAB-08 was created. **Nothing was committed, pushed
or tagged.**
