# PHASE 22 — MACHINE-READABLE PRE-TAG REPORT

*A `--json` output mode for the owner pre-tag orchestrator
(`scripts/pre_tag_check.py`), following the executable owner pre-tag validation
(`research/60`): the same read-only sequence, rendered as one deterministic JSON
object so the exact owner-review evidence can be archived without copying terminal
output. It changes **no runtime, CI, warning-detection, warning-policy, version or
release-gate behaviour**, preserves the human-readable default byte-for-byte, and
does not add a CI job. Nothing was committed, pushed or tagged; the `v0.0.1` tag
is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release was prepared and green (validated at the end of
`research/60`): version `0.1.0` (3/3); gate **READY WITH WARNINGS**,
`blockers: []`, accepted set exactly `{W7, W12}`, `W6` closed; warning-drift exit
`0`; manifest-drift exit `0`; `pre_tag_check.py` exit `0` with
`RESULT: READY FOR OWNER REVIEW` (12/12); suite **1024 passed**. The orchestrator
produced only a **human-readable** sectioned report: correct and unambiguous, but
the owner had to copy terminal text to archive the evidence, and no artifact could
be diffed or machine-parsed.

## 2. Motivation

Machine-readable evidence is easier to archive, diff between runs, and attach to a
release record than pasted terminal output. The owner pre-tag validation already
computes a structured result internally (`StepResult` objects plus the release
gate's parsed JSON); exposing that in a deterministic JSON form lets the owner
capture the exact pre-tag evidence mechanically without weakening any check or
introducing a second source of truth.

## 3. Exact implementation

`scripts/pre_tag_check.py` gained:

- a `--json` CLI flag, **mutually exclusive** with the existing `--summary` flag
  (argparse group), so the output modes cannot be combined;
- a `SCHEMA_VERSION = "1"` constant and a `READY_FOR_OWNER = "READY FOR OWNER
  REVIEW"` constant;
- a new optional field on `StepResult`: `info: dict | None = None`. Only the
  release-gate step populates it, with the gate's `target_version`,
  `classification`, `blockers` and `warnings`. The human-readable lines are built
  from the **same** values, so the two views cannot drift apart;
- a `build_json_report(results, *, ok, root=None)` function that derives the
  report from the existing `StepResult` list (reusing `run_checks`), the gate's
  captured `info`, `read_version(root)` as a fallback for the target version, and
  the existing `_warning_sort_key` for ordering;
- a branch in `main` that, when `--json` is set, prints only
  `json.dumps(build_json_report(...), indent=2)` — no other stdout — and returns
  the **same** exit code as the human-readable path.

Nothing else changed: the check set, the order, the gate-capture/reuse design, the
scratch-directory lifecycle and the read-only guarantees are identical. The
default (no flag) output is **byte-for-byte unchanged**.

## 4. JSON schema

```json
{
  "schema_version": "1",
  "result": "READY FOR OWNER REVIEW" | "NOT READY",
  "success": true | false,
  "target_version": "0.1.0",
  "classification": "READY WITH WARNINGS",
  "blockers": [],
  "warnings": ["W7", "W12"],
  "checks": [
    {"name": "Version", "status": "PASS", "details": ["PASS  0.1.0"]},
    "... 11 ordered steps ...",
    {"name": "Final result", "status": "PASS", "details": ["RESULT: READY FOR OWNER REVIEW"]}
  ],
  "check_count": 12,
  "passed_count": 12,
  "failed_count": 0
}
```

`checks` holds the eleven step results in execution order (their `name`, a
`status` of `PASS`/`FAIL`, and the exact `details` lines the human report prints)
plus the final-result banner as the twelfth entry — matching the human report's
`[i/12]` numbering. `warnings` is normalised to numeric order, so the gate's raw
`["W12","W7"]` is reported as `["W7","W12"]`. `blockers` and `classification` come
from the release gate; `passed_count`/`failed_count` are computed from `checks`.

## 5. Deterministic-output policy

The report is derived **only** from the `StepResult` objects and the gate's
captured report, so it contains no timestamps, no absolute or machine-specific
paths, no scratch-directory names and no environment-dependent values. Check order
is the fixed `CHECKS` order; warning order is numeric; the object shape and key
order are fixed by construction. Two runs over the same repository state therefore
produce the same bytes (only the content of the checks' `details` reflects the
repository state itself).

## 6. Gate invocation count

Unchanged and single. `release_check.py --json` still runs **once**; its parsed
report is written to `release-report.json` in the scratch directory **outside the
repository** and reused by both `check_warning_drift.py --gate-report` and
`check_release_manifest.py --gate-report`. JSON mode introduces **no** second gate
invocation; it is a rendering of the same run.

## 7. Tests

`tests/test_pre_tag_check.py` gained **10 focused tests** reusing the existing
fixture infrastructure (`FakeRunner`, `make_repo`, `_step_key`,
`_gate_invocations`, `_gate_report_paths`, and the importlib-loaded `guard` module):

- `--json` exits `0` and emits parseable JSON only (stdout alone is valid JSON, so
  no diagnostics are mixed in);
- the expected state: `schema_version` `"1"`, `result` `READY FOR OWNER REVIEW`,
  `success` true, `target_version` `0.1.0`, `classification` `READY WITH
  WARNINGS`, `blockers` `[]`, warning set exactly `{W7, W12}`, `check_count`/`12`,
  `passed_count` `12`, `failed_count` `0`;
- warnings normalised to stable numeric order `["W7","W12"]`;
- the twelve checks in stable execution order with `PASS` statuses and non-empty
  `details`;
- exit-code parity and `success: false` on a simulated failure (the failing step
  and the final-result entry are the two FAILs);
- a gate blocker yields `classification` `NOT READY`, `blockers` `["tests"]` and
  exit `1`;
- the gate still runs exactly once and the captured report is reused by both drift
  checks;
- no temporary report remains afterwards;
- the repository file set is unchanged.

No test runs the real suite or the real gate.

## 8. Exact files changed

Added:

```
research/61-machine-readable-pre-tag-report.md   (this record, CC BY 4.0)
```

Modified:

```
scripts/pre_tag_check.py          + --json mode, build_json_report, StepResult.info
tests/test_pre_tag_check.py       + 10 JSON tests
labs/ACCEPTED-RELEASE-WARNINGS.md + "Machine-Readable Pre-Tag Report"
labs/V0.1.0-RELEASE-MANIFEST.md   + short --json evidence reference
```

`licensing/manifest.toml` needed no edit (existing globs cover the new file), and
`mkdocs.yml` needed no change (the section lives on an already-listed page). **No
CI change.**

## 9. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **1034 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 (built outside the repository) |
| `python scripts/check_licensing.py` | **9/9** — 218 files accounted for |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_release_manifest.py` | exit **0** — manifest and repository state agree |
| `python scripts/pre_tag_check.py` | exit **0** — `RESULT: READY FOR OWNER REVIEW` (12/12) |
| `python scripts/pre_tag_check.py --json` | exit **0** — valid JSON, `success: true`, warnings `["W7","W12"]`, 12/12 |
| `git diff --check` | clean |

The JSON output was parsed independently and verified: exactly one
`release_check.py` invocation by the orchestrator, `blockers` `[]`, classification
`READY WITH WARNINGS`, warning set exactly `{W7, W12}`, 12/12 checks, and no
temporary artifacts left behind.

**Test delta: 1024 → 1034 (+10).** No existing test was modified or weakened.

## 10. Warning state

Unchanged and exact: **`{W7, W12}`** (gate JSON order `["W12","W7"]`; report order
`["W7","W12"]`), `W6` **closed**, `blockers: []`, classification **READY WITH
WARNINGS**; version **`0.1.0`**. The orchestrator treats `READY WITH WARNINGS` as a
success and never forces `READY`.

## 11. Protected invariants

`scripts/release_check.py` (and its warning detection), the B5 exact-warning
assertion (`ACCEPTED_RELEASE_WARNINGS`), `.freebuff/project-id`,
`licensing/manifest.toml`, `schemas/**`, the lab runtime, `.github/workflows/docs.yml`
and the warning classification logic were **not modified**. CI keeps its five-job
structure and its single `release_check.py` invocation; no `continue-on-error` was
added. The default human-readable output is unchanged, and no generated artifacts
remain.

## 12. Tag / Git status

* `v0.0.1` — unchanged; `git tag` lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* No commit, push or tag was performed.

## 13. Deferred work

**No CI step was added.** The `--json` mode is an owner-facing convenience for
archiving the pre-tag evidence; wiring it into CI would duplicate the existing
`release-readiness` job and is out of scope. Possible future work (not done here):
treating the JSON report as a signed/attested release artifact, or feeding it to a
release-notes generator — both require an owner decision and are deliberately
deferred. The remaining action is the **owner's**: review the working tree and the
archived JSON evidence, then commit, push, tag and (optionally) publish manually.
The agent does not commit, push, tag or publish. Phase 17 remains **CLOSED**, E1
remains **HOLD**, and no novelty, effectiveness, security, benchmark or publication
claim is made.
