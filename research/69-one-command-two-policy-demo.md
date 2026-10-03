# PHASE 30 — ONE-COMMAND TWO-POLICY DEMONSTRATION

*The Phase 7C LAB-04 two-policy exercise made reproducible in a single command,
`agentsec demo lab04-two-policies`. It reuses the existing MVP stack and the
existing `agentsec compare` logic, adds no metric, score or policy judgement, and
writes nothing to the repository. Nothing was committed, pushed or tagged.*

## 1. Phase 7C limitation

Phase 7C documented the same-lab-two-policies comparison, but a learner had to
run **two** `agentsec run` commands and then locate and compare two traces by
hand (one under `runs/lab04_tool_misuse_allow_all/`, one under
`runs/lab04_tool_misuse/`). That is three commands, two output locations, and a
manual trace-path step — enough friction that the demonstration was easy to get
wrong.

## 2. Reconnaissance

* **`agentsec run`** is the supported lab execution mechanism; the CLI already
  imports the MVP composition root (`build_mvp_runner`) and runs one config.
* **LAB-04 configs**: `labs/LAB-04-tool-misuse/config.yaml` uses
  `least_privilege_v1`; `configs/examples/lab04_tool_misuse_allow_all.yaml`
  (Phase 7C) is the same experiment with `allow_all_v1`.
* **`agentsec compare`** (Phase 7B) is the existing read-only comparison; it must
  be reused, not reimplemented.
* **Trace output**: `runs/` is git-ignored; tests generate traces into `tmp_path`.
* **CLI convention for temporary work**: `_cmd_labs_check` already wraps a
  `tempfile.TemporaryDirectory`, runs into it and cleans up — the pattern to
  follow.
* **Testability**: no test imports a `scripts/` module (tests invoke scripts by
  subprocess), so a reusable, injectable `src/` module is far easier to unit-test
  than a helper script.
* **Architecture guards**: `test_gateway_is_the_only_tool_execution_boundary`
  allows only `gateway.py`, `base.py`, `runner.py`, `cli.py` to contain `.run(`;
  `test_cli_contains_no_execution_logic` forbids execution verbs in `cli.py` but
  permits `runner.run(config)` (as `_cmd_run` already does);
  `test_lab00_cli_is_available` asserts only that the subcommand set is a
  **superset** of `{run, evaluate, inspect}`, so adding a subcommand is safe.

## 3. Selected implementation point

A small read-only helper module plus a thin CLI command (the smallest natural
interface; no new orchestration framework):

* **`src/agentsec/demo.py`** — planning and orchestration only. It holds **no
  execution engine**: running a configuration is an injected `execute` callable.
  It imports just `compare`, `errors`, `experiment`, `pathlib`, `dataclasses` —
  not `mvp` and not the tools/policy/model layers — so it contains no `.run(`
  and cannot accidentally call a tool.
* **`agentsec demo lab04-two-policies`** in `cli.py` — a thin command mirroring
  `_cmd_labs_check`: it creates a `tempfile.TemporaryDirectory`, calls
  `run_demo(tmp, execute=_run_demo_config)`, prints the rendered result, and lets
  the context manager remove the directory. `_run_demo_config` supplies the real
  execution (`build_mvp_runner(config).run(config)`), which is why `cli.py` — an
  allowed file — owns that one line rather than the helper module.

## 4. Command / interface

```text
agentsec demo lab04-two-policies
```

`demo` is a new subcommand with one positional `name`, constrained by
`argparse` `choices=[LAB04_TWO_POLICIES]`; an unknown name is a usage error
(exit `1`). The command is deterministic, offline, read-only with respect to the
repository, temporary-output based, and safe to run repeatedly.

## 5. Execution flow

1. `plan_demo(output_dir, root)` loads LAB-04's `config.yaml` and produces two
   runs, overriding only `policy_path` (permissive → Trace A, least-privilege →
   Trace B) and the output `trace_path` (so the runs do not collide). The same
   `experiment_id`, task, `mock_script` and agent are preserved.
2. `run_demo` calls the injected `execute(config)` for each run and requires each
   to have written a trace (else `ConfigError`).
3. It compares the two traces with the existing **`compare_traces`** (called by
   name so the module-level reference is spy-able) and returns a `DemoOutcome`.
4. `render_demo` prints a short header naming which policy is which, then the
   standard `render_comparison` output.
5. The CLI's `TemporaryDirectory` removes both traces on exit.

No comparison logic and no execution engine are duplicated.

## 6. Deterministic behaviour

The comparison document contains no timestamps, absolute paths, host details or
generated ids (Phase 7B property), so the demo output is byte-identical across
runs even though the CLI executes the real stack with the real clock. Ordering —
policies A then B, event types canonical-then-sorted, evaluator keys sorted — is
fixed. Two consecutive `agentsec demo lab04-two-policies` runs print the same
text.

## 7. Test coverage

New module `tests/cli/test_demo.py` (**14 tests**), using an **injected fake
executor** for the unit tests and one real end-to-end test:

* `plan_demo` changes only the policy and the output path (same experiment);
* `run_demo` executes **both** policies, generates **both** traces, and invokes
  the existing comparison (a spy asserts `compare_traces` is called with the two
  trace paths);
* the expected factual differences appear (`tool_executed` A1/B0;
  `decisions.allow` 1→0; `decisions.deny` 0→1);
* determinism (two runs render identically);
* a run that writes no trace raises `ConfigError`; an executor failure propagates;
* neither `run_demo` nor the CLI modifies LAB-04's config or either policy file;
* **CLI**: the real stack runs end to end and prints the labels and the key
  difference; the CLI is deterministic; its temporary directory is created **and
  removed** (verified by recording the `TemporaryDirectory` name); an execution
  failure returns a deterministic non-zero code (exit `1`); an unknown demo name
  is a usage error (exit `1`).

No existing test was weakened, and no manual architecture update was needed.

## 8. Artifact cleanup

The two traces are written only into the CLI's `tempfile.TemporaryDirectory`
(prefix `agentsec-demo-`) and removed on exit; the helper writes nowhere else.
The demo overrides `trace_path`, so it never writes under `runs/`. After running
the demo, the working tree is unchanged and no `.jsonl`, cache or build artifact
remains.

## 9. Validation

Re-run at this revision (all green):

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `python -m pytest` | **1122 passed** |
| Lab self-check | `python -m agentsec labs check` | **8/8 labs passed** |
| Lint | `ruff check src tests scripts` | **All checks passed** |
| Types | `python -m mypy` | **Success: no issues found in 42 source files** |
| Docs | `python -m mkdocs build --strict` | **exit 0** |
| Licensing | `python scripts/check_licensing.py` | **9/9 passed** (232 files) |
| Version | `python scripts/check_version.py` | **3/3 passed** (`0.1.0`) |
| Release gate | `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `['W12','W7']` |
| Whitespace | `git diff --check` | clean |
| The command | `agentsec demo lab04-two-policies` | exit `0`; prints the header and the comparison |

Actual comparison result (abridged): 12 vs 11 events; `tool_executed A 1 B 0`;
`decisions.allow: 1 -> 0`; `decisions.deny: 0 -> 1`; `tool_results.denied: 0 -> 1`;
`tool_results.error: 1 -> 0` — the same facts Phase 7C established.

**Test count: 1106 → 1122 (+16):** 14 new demo tests, +1 from
`test_architecture.py::test_no_banned_dependency_in_source` (parametrised over
`src/agentsec/*.py`, gaining `demo.py`), and +1 from
`…::test_no_banned_dependency_in_tests` (parametrised over `tests/**/*.py`,
gaining `test_demo.py`). The README's derived test-count row was updated
(`1106` → `1122`) as required by `tests/test_readme.py`.

## 10. Limitations

* It demonstrates exactly one lab (LAB-04) under exactly two fixed policies; the
  `name` argument is a `choices` list of one.
* It reports the same structural comparison as `compare`; it adds no metric,
  score, ranking or "better/worse" judgement, and it does not diff payloads.
* Real runs use the real clock; only the *comparison* is timestamp-free, so the
  **printed output** is deterministic, not the two traces themselves.
* It is a repository-checkout helper: the CLI resolves the lab/policy paths
  relative to the current directory (the lab convention is to run from the
  repository root), so it is not intended for an installed-package context.
* No novelty, effectiveness, security, benchmark or publication claim is made.

## 11. Protected invariants

Untouched: `scripts/release_check.py` and its warning detection, the B5
exact-warning assertion, `W7`/`W12` (still accepted), `licensing/manifest.toml`
(new files are covered by existing globs), `.freebuff/project-id`, `schemas/**`,
the release manifest, the version declarations (`0.1.0`), `TraceEvaluator`
semantics, `read_events` semantics, the existing `compare` semantics, and both
`.github/workflows/*.yml` (no CI integration). No scope creep into payload-level
diffing, post-release verification, security-event changes or new policy
experiments. The gate stays **READY WITH WARNINGS** with `blockers: []`.

## 12. Git / tag state

* `v0.0.1` and `v0.1.0` are **unchanged** (`v0.1.0` → `3d731b0`).
* No tag was created, modified, deleted or moved.
* No commit, push or publication was performed.
