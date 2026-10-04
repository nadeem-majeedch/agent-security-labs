# PHASE 8E — TEXT-MODE DEMO ARTIFACT GUARD

*A small, test-only follow-up to Phase 8D. It hardens the **text-mode** demo guard
to use the same repository-wide `runs/` snapshot invariant as the JSON-mode guard,
so both modes prove the same thing: running `agentsec demo` leaves persistent
repository state unchanged. **No runtime code was changed.** Nothing was
committed, pushed or tagged.*

## 1. Remaining weakness after Phase 8D

Phase 8D fixed the JSON-mode guard
(`test_demo_json_leaves_no_traces_in_the_repository`) to snapshot the `runs/`
tree. Its **text-mode** sibling
(`test_demo_cli_does_not_write_into_the_repository`) was left weaker: it watched
only the bytes of `LAB04_CONFIG`, `ALLOW_ALL_POLICY` and `LEAST_PRIVILEGE_POLICY`.
Those are genuine, independent invariants worth keeping — but they do **not** prove
that the demo leaves no new artifacts under `runs/`. A text-mode regression that
wrote a trace into `runs/` would have passed.

## 2. Text-mode invariant

```text
before demo:  repository runs/ state = S
run demo:     agentsec demo lab04-two-policies
after demo:   repository runs/ state = S
```

The same invariant as JSON mode, detecting newly created files, newly created
directories, deleted files/directories and modified files, while tolerating any
pre-existing `runs/` contents (including `runs/lab04_tool_misuse_allow_all/`).

## 3. Reuse of `_runs_snapshot()`

The Phase 8D helper is reused unchanged — no second snapshot implementation was
created:

```python
def _runs_snapshot() -> dict[str, bytes | None]:
    root = REPO / "runs"
    if not root.is_dir():
        return {}
    snapshot: dict[str, bytes | None] = {}
    for path in root.rglob("*"):
        if "__pycache__" in path.parts:
            continue
        snapshot[str(path.relative_to(root))] = (
            path.read_bytes() if path.is_file() else None
        )
    return snapshot
```

It is read-only, standard-library based, deterministic, independent of git and
network, and safe with pre-existing user files.

## 4. Files changed

* `tests/cli/test_demo.py` — added a `runs/` before/after snapshot assertion to
  `test_demo_cli_does_not_write_into_the_repository` (keeping its existing
  config/policy byte assertions); added one focused text-mode regression test,
  `test_demo_cli_tolerates_a_preexisting_lab04_allow_all_trace`.
* `README.md` — derived test-suite row 1196 → 1197.
* `research/83-text-mode-demo-artifact-guard.md` — this record.

No `src/**`, config, policy, lab, schema, script or workflow file changed. The
Phase 8B/8C/8D work is untouched apart from the shared `README.md` count.

## 5. Regression scenario

The new test recreates the exact path the old JSON guard wrongly rejected, for
text mode:

* if `runs/lab04_tool_misuse_allow_all/` is absent, it is created;
* if `trace.jsonl` is absent, a known sentinel (`b"{}\n"`) is written;
* the text-mode demo runs; the `runs/` snapshot is asserted unchanged and the
  file byte-identical;
* only what the test itself created is removed — a pre-existing directory or file
  is never modified or deleted.

## 6. Validation

Full battery at **1197 tests**:

* `python -m pytest` — 1197 passed.
* `python -m pytest tests/cli/test_demo.py` — 28 passed.
* `python -m agentsec labs check` — 8/8 labs.
* `ruff check src tests scripts` — clean.
* `python -m mypy` — no issues (43 source files).
* `python -m mkdocs build --strict` — exit 0.
* `python scripts/check_licensing.py` — 9/9.
* `python scripts/check_version.py` — 3/3 @ `0.1.0`.
* `python scripts/release_check.py --json` — READY WITH WARNINGS; blockers `[]`,
  warnings `["W12", "W7"]`.
* `git diff --check` — clean.

The documented text-mode demo (`agentsec demo lab04-two-policies`) was executed:
exit `0`, deterministic heading/output, and the `runs/` file-list hash unchanged
before/after.

### State A / State B

* **State A** — `runs/lab04_tool_misuse_allow_all/` absent: the guard and the
  text-mode regression test both pass (`2 passed`); the demo leaves `runs/`
  unchanged.
* **State B** — the directory present with a hand-written `trace.jsonl`: both
  tests pass (`2 passed`); the file is still present and its SHA-1 is unchanged.

The JSON-mode guard and the text-mode guard now enforce conceptually identical
invariants (`runs before == runs after`), each also retaining its independent
config/policy byte check.

## 7. Protected invariants

Untouched: `src/agentsec/**` (including `demo.py`, `compare.py`,
`prediction.py`), `TraceEvaluator`, `compare_traces`, demo runtime semantics,
policy files, lab configurations, `schemas/**`, release scripts,
`licensing/manifest.toml`, `.github/workflows/**`, version declarations,
`.gitignore`, and tags. No runtime change, no CLI change, no release change.

## 8. Cleanup

The manually created State A/B directory and all build/test caches were removed;
`runs/` is back to its prior state. The regression test cleans up after itself.

## 9. Git/tag state

Working tree contains only the intended Phase 8E change plus the previously
uncommitted Phase 8B/8C/8D work. Branch `v0.1.0-dev`, HEAD `2110dd0`; tags
unchanged (`v0.0.1`, `v0.1.0`). Nothing was committed, pushed, published or
tagged.

## 10. Recommended stopping point

Stop incremental feature work here. Both demo modes now enforce the same
artifact invariant and the guard family is internally consistent. The appropriate
next direction is **consolidation, not another increment**: audit the entire
Phase 7–8 learning path end to end (the getting-started sequence, the prediction
examples, the answer key, and the documentation guards) for redundancy,
contradictions and gaps, and report concrete findings before implementing any
further capability. New features should wait on that audit.
