# PHASE 8D — DEMO ARTIFACT GUARD FIX

*A small, test-only correctness fix. It replaces an over-specific assertion in the
demo JSON guard with the invariant that actually matters — running `agentsec demo`
leaves the repository's persistent `runs/` tree unchanged — so a legitimate
pre-existing LAB-04 allow-all trace no longer trips it. **No runtime code was
changed.** Nothing was committed, pushed or tagged.*

## 1. The pre-existing contradiction

`tests/cli/test_demo.py::test_demo_json_leaves_no_traces_in_the_repository`
ended with:

```python
assert not (REPO / "runs" / "lab04_tool_misuse_allow_all").exists()
```

But that directory is exactly what the allow-all example config declares:

```yaml
# configs/examples/lab04_tool_misuse_allow_all.yaml
trace_path: runs/lab04_tool_misuse_allow_all/trace.jsonl
```

and `labs/LAB-04-tool-misuse/README.md` **already documents** running that config
directly (as does the Phase 8C capstone). So a documented, legitimate action —
running the allow-all config — creates the very path the guard asserted must
never exist, and the suite fails afterwards. The contradiction predates this
phase and was surfaced by the Phase 8C capstone.

## 2. Why the old guard was too specific

The test's purpose is: *the demo must not write persistent files into the
repository*. `demo`/`run_demo` write traces only into a caller-supplied
`TemporaryDirectory` and never to `REPO/runs`. The old assertion tried to prove
that by naming a single config's output directory and demanding its absence —
which conflates two different things:

* "the demo created no repository artifacts" (always true, and the real
  invariant), and
* "nobody, ever, ran the allow-all config directly" (false, and contradicted by
  the docs).

It also assumed `runs/` is empty, which is not guaranteed: `runs/` legitimately
holds traces written by other commands and labs.

## 3. The invariant that actually matters

```text
before demo:  repository runs/ state = S
run demo:     agentsec demo lab04-two-policies --json
after demo:   repository runs/ state = S
```

The exact contents of `runs/` are irrelevant; only the *absence of change* is
asserted. This holds whether or not `runs/lab04_tool_misuse_allow_all/` already
exists, and it detects new, deleted and modified entries.

## 4. Snapshot-based solution

Following the repository's existing conventions (`_tree`/`_snapshot` in
`tests/labs/test_lab_selfcheck.py`), the module gained a small helper that
snapshots the `runs/` tree, mapping each relative path to its file bytes, or
`None` for a directory (so new/deleted directories are detected too; `__pycache__`
is ignored):

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

The guard now snapshots before and after and asserts equality. It tolerates an
already-existing `runs/`, existing trace files, and detects creation, deletion
and modification. It uses only the standard library, no network, and no git.

## 5. Files changed

* `tests/cli/test_demo.py` — added `_runs_snapshot()`; rewrote the
  `test_demo_json_leaves_no_traces_in_the_repository` assertion from
  path-absence to snapshot-equality; added one regression test
  (`test_demo_json_tolerates_a_preexisting_lab04_allow_all_trace`).
* `README.md` — derived test-suite row 1195 → 1196.
* `research/82-demo-artifact-guard-fix.md` — this record.

No `src/**`, config, policy, lab, schema, script or workflow file changed.

## 6. Tests added/modified

* **Modified:** the existing guard keeps its other assertions (the config and
  policy files are byte-unchanged) and now proves the `runs/` tree is unchanged.
  Coverage is strictly stronger, not weaker: the old check proved one path is
  absent; the new check proves no path changed.
* **Added:** one regression test that recreates the exact path the old guard
  wrongly rejected. It creates `runs/lab04_tool_misuse_allow_all/trace.jsonl`
  only if absent, runs the demo, asserts the `runs/` snapshot is unchanged and the
  file is byte-identical, then removes **only** what it created (it never deletes
  or modifies a pre-existing user file).

## 7. Validation

Full battery at **1196 tests**:

* `python -m pytest` — 1196 passed.
* `python -m pytest tests/cli/test_demo.py` — 27 passed.
* `python -m agentsec labs check` — 8/8 labs.
* `ruff check src tests scripts` — clean.
* `python -m mypy` — no issues (43 source files).
* `python -m mkdocs build --strict` — exit 0.
* `python scripts/check_licensing.py` — 9/9.
* `python scripts/check_version.py` — 3/3 @ `0.1.0`.
* `python scripts/release_check.py --json` — READY WITH WARNINGS; blockers `[]`,
  warnings `["W12", "W7"]`.
* `git diff --check` — clean.

### State A / State B (explicit)

* **State A** — `runs/lab04_tool_misuse_allow_all/` absent: the guard and the
  regression test both pass (`2 passed`).
* **State B** — the directory present with a legitimately hand-written
  `trace.jsonl`: both tests pass (`2 passed`), the file is still present
  afterwards and its SHA-1 is unchanged (the demo neither modified nor deleted
  it). The old assertion evaluated to `False` in this state, confirming it would
  have failed.

## 8. Artifact cleanup

The manually created State A/B directory and all build/test caches were removed;
`runs/` is back to its prior state. The regression test cleans up after itself.

## 9. Protected invariants

Untouched: `src/agentsec/**` (including `demo.py`, `compare.py`,
`prediction.py`), `TraceEvaluator`, `compare_traces`, demo runtime semantics,
policy files, lab configurations, `schemas/**`, `scripts/release_check.py`,
release controls, `licensing/manifest.toml`, `.github/workflows/**`, version
declarations, tags, and `.gitignore`. No runtime change, no new CLI command, no
release-semantics change.

## 10. Git/tag state

Working tree contains only the intended Phase 8D change plus the previously
uncommitted Phase 8B/8C work. Branch `v0.1.0-dev`, HEAD `2110dd0`; tags unchanged
(`v0.0.1`, `v0.1.0`). Nothing was committed, pushed, published or tagged.

## 11. Limitations

* The snapshot compares file **contents** and the set of paths; it does not track
  file metadata (timestamps, permissions), which are not part of the invariant.
* `runs/` is gitignored, so this guard protects local state only — which is
  precisely the concern the demo raises.
* The fix corrects the guard's logic, not the underlying fact that running the
  allow-all config writes an (ignored) trace; that remains a documented, expected
  side effect with a cleanup note in the getting-started capstone.

## 12. Next recommended step

Apply the same snapshot-based pattern to the text-mode guard
(`test_demo_cli_does_not_write_into_the_repository`), which likewise watches only
config/policy bytes: extend it to assert the `runs/` tree is unchanged in text
mode too. That closes the last place where "no repository artifacts" is proven by
a weaker check than the invariant, and it is a small, coverage-strengthening
follow-up.
