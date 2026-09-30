# PHASE 20 — STEP 18: RELEASE-GATE AUTOMATION AUDIT

**Status: PASS — the established release procedure is now one deterministic, read-only command, and it reports `READY WITH WARNINGS`.**

`scripts/release_check.py` runs all nine release gates in one pass and prints a human report (default) or a machine-readable JSON summary (`--json`), classifying the repository as **READY**, **READY WITH WARNINGS** or **NOT READY**. It orchestrates the existing guards rather than re-implementing them, uses only the standard library, and never writes to the repository. Nothing was committed, pushed, tagged, staged or released; no existing file's behaviour was changed except the README's documentation and the appended CI step.

Phase 17 remains **CLOSED**. **E1 remains HOLD**. No research claim, study, learner data, novelty/effectiveness/benchmark/publication claim is introduced or asserted. No previous audit was modified.

---

## 1. Starting HEAD

| Item | Value |
| --- | --- |
| `HEAD` | `a193076e5b5cf92f1fd387b54ed008fc306b65dc` (`a193076` "Phase 20 step 16 complete") |
| Branch | `main` |
| Tags | **0** |
| Working tree at start | uncommitted Step 17 work: `M .github/workflows/ci.yml`, `M README.md`, `?? research/35-version-drift-guard-audit.md`, `?? research/36-v0.0.1-release-checklist.md`, `?? scripts/check_version.py`, `?? tests/test_version.py` |
| Staged | **empty** |
| Baseline gates | pytest **800 passed** · labs **8/8** · MkDocs strict **exit 0** · licensing **9/9 over 173 files** · version **3/3** |

`HEAD` is unchanged at the end of this step (§18).

## 2. Files created

| File | Purpose |
| --- | --- |
| `scripts/release_check.py` | The release-gate runner (stdlib only, read-only). |
| `tests/test_release_check.py` | 48 tests for the runner. |
| `research/37-release-gate-automation-audit.md` | This audit. |

## 3. Files modified

| File | Change | Behavioural impact |
| --- | --- | --- |
| `.github/workflows/ci.yml` | Appended one step, `Report release readiness` (`python scripts/release_check.py --json`), and extended the header comment. | None to existing steps; job name `tests and lab self-check` unchanged; new step runs last. |
| `README.md` | Verification table gained a “Release readiness (all gates)” row and the test count was corrected; a paragraph documents the new command; the CI paragraph mentions the final step. | Documentation only. |

No source module, lab, policy, scenario, schema, config, licence, manifest, `CITATION.cff`, version, dependency or existing test was modified. Nothing was added to `pyproject.toml`.

## 4. Release-gate architecture

```
scripts/release_check.py            (standard library only)
│
│  Context(root, scratch, python, env)     scratch = tempdir OUTSIDE the repo
│  run_command(argv, cwd, env)             the single subprocess boundary
│
├─ GATES (in order) ────────────────────────────────────────────────────────┐
│  tests             → python -m pytest -p no:cacheprovider                 │
│  labs              → python -m agentsec labs check                        │
│  mkdocs            → python -m mkdocs build --strict -d <scratch>/site     │
│  licensing         → python scripts/check_licensing.py   (delegated)      │
│  version           → python scripts/check_version.py     (delegated)      │
│  readme            → in-process: relative links + heading anchors         │
│  self_containment  → byte-compare + pip wheel in a scratch copy           │
│  hygiene           → in-process scan + git ls-files (read-only)           │
│  git_state         → git rev-parse / tag / status / diff (read-only)      │
└───────────────────────────────────────────────────────────────────────────┘
     │
     ├─ GateResult(gate, status, summary, detail, command, exit_code, inspect)
     └─ Warning(id, summary)          the audits' W6–W13 terminology
     │
   build_report() → classify() → render_human() | JSON
```

Design points:

* **Orchestration, not duplication.** The version and licensing checks are delegated to their own scripts, and tests/labs/MkDocs to their own commands, so there is exactly one implementation of each check. The runner adds only what the audits established and no single command covered: README links/anchors, packaging self-containment, repository hygiene, and Git state.
* **One subprocess boundary.** Every external command goes through `run_command`; tests inject a recording stand-in, so the suite is hermetic and can assert exactly which commands *would* run — including that no mutating `git` subcommand is among them.
* **Read-only.** Build output goes to a `tempfile.mkdtemp()` scratch directory outside the checkout; MkDocs is redirected with `-d`; pytest runs with `-p no:cacheprovider`; the wheel is built from a copy under the scratch directory. The runner contains no `write_text`/`write_bytes`/`open(`.
* **Fail fast, but not silently.** A failed gate quotes the captured output, its exit code and an `inspect` hint. A gate whose *tooling* is unavailable (MkDocs not installed; pip build isolation unreachable) reports `WARN`, never a silent pass and never a false failure.

## 5. Commands and checks executed

| Gate | Command / check | Source |
| --- | --- | --- |
| tests | `python -m pytest -p no:cacheprovider` (project `addopts = "-q"` supplies quiet mode) | subprocess |
| labs | `python -m agentsec labs check` (writes to its own temp dir) | subprocess |
| mkdocs | `python -m mkdocs build --strict -d <scratch>/site` | subprocess |
| licensing | `python scripts/check_licensing.py` | delegated |
| version | `python scripts/check_version.py` | delegated |
| readme | markdown link extraction + heading-slug anchors | in-process |
| self_containment | packaged-vs-repository schema byte compare; `python -m pip wheel . --no-deps -w <scratch>/dist` in a scratch copy; wheel contents/metadata/byte-identity | in-process + subprocess |
| hygiene | `git ls-files`, `git ls-files -i -c --exclude-standard`, plus in-process scans | subprocess + in-process |
| git_state | `git rev-parse --is-inside-work-tree`, `git rev-parse HEAD`, `git rev-parse --abbrev-ref HEAD`, `git tag`, `git status --porcelain`, `git diff --cached --name-only` | subprocess |

`python` is `sys.executable`; tests and labs run with `PYTHONPATH=src`.

## 6. Classification logic

```
any gate == FAIL                     → NOT READY          (release blockers)
else if any warning or gate == WARN  → READY WITH WARNINGS
else                                 → READY
```

* The rule is implemented once, in `classify(gates, warnings)`, and tested directly.
* A `FAIL` gate is always a blocker — the specification's “a mandatory release gate fails or repository state violates a release prerequisite”. Non-blocking conditions report `WARN` instead (a dirty working tree; unavailable tooling; build isolation unreachable).
* The CLI exits `1` only for `NOT READY`, `0` otherwise, so it is safe to wire into CI (a warning does not break the build).

## 7. JSON output contract

`--json` prints the object below. Values are never fabricated — every field is read from the actual run.

```json
{
  "target_version": "0.0.1",
  "classification": "READY WITH WARNINGS",
  "blockers": [],
  "warnings": ["W6", "W7", "W9", "W10", "W11", "W12", "W13"],
  "gates": {
    "tests": "PASS", "labs": "PASS", "mkdocs": "PASS",
    "licensing": "PASS", "version": "PASS", "readme": "PASS",
    "self_containment": "PASS", "hygiene": "PASS", "git_state": "WARN"
  },
  "gate_details": [
    {"gate": "...", "status": "...", "summary": "...", "detail": "...",
     "command": [...], "exit_code": 0, "inspect": "..."}
  ],
  "warning_details": [{"id": "W6", "summary": "..."}],
  "repository": {"branch": "main", "head": "a193076e…", "tags": []}
}
```

`target_version` comes from `pyproject.toml` via `tomllib` — it is **never hard-coded**. The `gates` map is present and complete on every run.

## 8. Tests (`tests/test_release_check.py`, 48 tests)

| Group | Coverage |
| --- | --- |
| Module discipline | imports ⊆ stdlib; no `urllib`/`httpx`/`requests`; no `write_text`/`write_bytes`/`open(`; gate order is the documented order |
| Target version | read from `pyproject.toml` (a fixture with `9.9.9`); `None` when the file is absent |
| Classification | all-pass → READY; a warning → READY WITH WARNINGS; a warned gate → READY WITH WARNINGS; a failed gate → NOT READY even with warnings |
| Individual gates | tests pass/fail (count parsed, exit code, actionable `inspect`); labs failure; MkDocs missing-dependency → WARN, build failure → FAIL; licensing/version failure and missing-script; readme missing file / missing link / unresolved anchor |
| Self-containment | fails when the packaged schema is missing; fails when the copies differ; warns when the wheel cannot be built |
| Hygiene | clean tree passes; tracked editor artefact, `TODO` marker, secret-shaped value and tracked-ignored file each fail; `research/` is exempt from the secret scan |
| Git state | clean → PASS; dirty → WARN; outside a worktree → FAIL; no commits → FAIL |
| Warnings | W6 present/absent by `date-released`; W7; W10+W11; W13; W12 always; only the known identifiers are ever emitted |
| Report/CLI | report shape and keys; blocker classification; human output shows the classification; `--json` parses; exit code 1 on NOT READY; **read-only** (fixture bytes unchanged) and **no mutating git command** is invoked |

The tests never invoke the real subprocesses: they inject a recording `FakeRunner`, so the suite is offline, fast and hermetic. `FakeRunner` matches a command by whole argument tokens (a full script path matches its filename), which avoids a temporary directory named `…/pytest-of-…` masquerading as the `pytest` command.

## 9. CI integration

`.github/workflows/ci.yml` gained exactly one step, appended **after** the existing prerequisite checks:

```yaml
      - name: Report release readiness
        run: python scripts/release_check.py --json
```

* The job name `tests and lab self-check`, the checkout/setup steps, the licence and version checks, the install step and the pytest/labs commands are **unchanged**.
* The step fails the build only on `NOT READY`; a `READY WITH WARNINGS` result leaves the job green.
* In the CI environment MkDocs is not installed (the job installs `.[dev]`), so the MkDocs gate reports `WARN` rather than failing — honest, and consistent with the runner's tooling policy (§4).
* Tagging and publishing are **not** part of CI (unchanged).

## 10. Read-only verification

| Evidence | Result |
| --- | --- |
| Runner source contains no `write_text`/`write_bytes`/`open(` | asserted by test |
| Scratch space | `tempfile.mkdtemp(prefix="agentsec-release-check-")`, removed in a `finally` block; all build output lives there, outside the checkout |
| MkDocs output | redirected with `-d <scratch>/site` — nothing written to the repository |
| pytest cache | disabled with `-p no:cacheprovider` |
| Wheel build | from a copy of the project under the scratch directory; no `build/`, `dist/` or `.egg-info` in the repository |
| Runtime read-only | a test snapshots every fixture file, runs `main`, and asserts the bytes are unchanged |
| No Git writes | a test asserts every `git` call is one of `rev-parse`, `ls-files`, `status`, `diff`, `tag` (and `tag` with no arguments, i.e. listing only) |
| Real runs | after the real gate runs, `git status --porcelain` shows only the intended Step 17/18 files and no artifact (§16, §18) |

## 11. Failure-path demonstrations

Both probes ran against temporary fixtures **outside the repository** and were removed afterwards.

**Probe A — a copy of the repository with one version declaration drifted** (`CITATION.cff` set to `0.0.2`), initialized as a Git repo with no commit. Real subprocesses:

```
classification: NOT READY
blockers: ['tests', 'version', 'git_state']
   FAIL tests      -> the test suite failed | Run `PYTHONPATH=src python -m pytest` and fix the failing tests.
   FAIL version    -> the version declarations disagree | Run `python scripts/check_version.py`; reconcile pyproject.toml, __version__ and CITATION.cff.
   FAIL git_state  -> the repository has no commits yet | Commit the release revision before creating the tag.
```

Note the drift is caught **twice** — by the delegated `check_version.py` guard and independently by `tests/test_version.py` — which is the redundancy the guards were built for.

**Probe B — a minimal broken fixture** (a README with a dead relative link, no guards, no Git):

```
classification: NOT READY
blockers: ['tests', 'labs', 'mkdocs', 'licensing', 'version', 'readme', 'self_containment', 'git_state']
   FAIL tests             -> Run `PYTHONPATH=src python -m pytest` and fix the failing tests.
   FAIL labs              -> Run `PYTHONPATH=src python -m agentsec labs check` and inspect the failing lab.
   FAIL mkdocs            -> Run `python -m mkdocs build --strict` and fix the reported page.
   FAIL licensing         -> Restore the licensing guard; it is the release coverage check.
   FAIL version           -> Restore the version guard; it is the version-consistency check.
   FAIL readme            -> Fix the named missing link or unresolved anchor in README.md.
   FAIL self_containment  -> Re-run `python scripts/export_trace_schema.py`; the wheel would ship without a schema.
   FAIL git_state         -> Run the gate from inside the repository checkout.
```

Every failure is actionable: it names the gate, the command, the exit code and what to inspect. Both probes exited `1`.

## 12. Package self-containment handling

The gate preserves the W5 check established in `research/34` and re-run in `research/36`:

1. **Always (offline):** the packaged schema `src/agentsec/schemas/trace/trace_event.v1.schema.json` must exist and be **byte-identical** to `schemas/trace/trace_event.v1.schema.json`. Missing or divergent → `FAIL`.
2. **Best-effort:** a wheel is built in a scratch copy and inspected for the schema, byte-identity, the authoritative version, and unwanted top-level entries. Success → `PASS`; a genuinely wrong wheel → `FAIL`.
3. **Tooling unavailable:** if `pip wheel` cannot run (no build isolation / no setuptools / offline), the gate reports **`WARN`** — “packaged schema is present and byte-identical; the wheel was not rebuilt here” — rather than a silent skip or a false failure.

On the audited revision the wheel **was** rebuilt: `agentsec-0.0.1-py3-none-any.whl`, schema present and byte-identical (31,544 bytes, md5 `7446450a672f38a7819ffb245115a6c1`), version `0.0.1`, MIT licence, no unwanted top-level entries.

## 13. Git-state handling

| Condition | Status | Rationale (from `research/36`) |
| --- | --- | --- |
| Clean working tree | `PASS` | — |
| Dirty / staged / untracked | `WARN` | The release audit recorded a dirty tree as expected **before** the release commit (`research/36` §2, §23) and did not treat it as a blocker. |
| Not inside a Git worktree | `FAIL` | There is no revision to release. |
| Worktree with no commits | `FAIL` | “repository state violates a release prerequisite” — commit before tagging. |

The gate always reports branch, HEAD, tag count, staged/modified/untracked counts, and embeds them in the JSON `repository` object. It never cleans or alters the tree.

## 14. Warning handling

The runner detects the known warnings mechanically and **introduces no new identifiers**:

| Id | Detection |
| --- | --- |
| W6 | `CITATION.cff` has no top-level `date-released:` |
| W7 | `.freebuff/project-id` is tracked |
| W9 | a `src/agentsec.egg-info/PKG-INFO` still says `License: TBD` or the old `(Phase A skeleton)` summary |
| W10 | `[project] license` uses the legacy `{ text = … }` form, or `authors`/`classifiers`/`keywords`/`urls` are absent |
| W11 | the `docs` extra names `mkdocs-material` without an upper bound or pin |
| W12 | always — the standing human-judgement licensing residual (cannot be closed mechanically) |
| W13 | `traces/*.jsonl` appears in `.gitignore`/the manifest while `traces/` does not exist |

A test asserts the emitted set is a subset of `{W6…W13}`. The `hygiene` gate scans only `src/`, `scripts/`, `labs/`, `policies/`, `configs/`, `schemas/`, `docs/`, `.github/` for high-signal secret patterns and deliberately skips `tests/` and `research/`, so fixtures and historical audit prose are never reported as leaks.

## 15. Research boundary

| Statement | Evidence |
| --- | --- |
| Phase 17 remains **CLOSED** | `docs/development.md`'s research-status section is unmodified; the step touched no research file except adding this audit. |
| **E1 remains HOLD** | No E1 classification or publication-gate statement was touched. |
| No research implementation, study or learner data | None added; the change is release tooling. |
| No novelty/effectiveness/benchmark/publication claim | The new code and docs describe version bookkeeping and packaging only. |
| No previous audit modified | `research/20`–`research/36` are byte-unchanged. |

## 16. Final validation

Re-run at this revision, all green:

| Gate | Result |
| --- | --- |
| Test suite | **849 passed** (was 800; **+48** new tests, **+1** architecture parametrisation) |
| Lab self-check | **8/8 labs passed** |
| MkDocs strict | **exit 0**, 0 `WARNING -`/`ERROR -` lines |
| Licensing (declarations + coverage) | **9/9 checks passed**; **176 files** accounted for (mit 125, cc-by 49, excluded 2, unlicensed 0); 0 unaccounted, 0 conflicts, 0 stale, 0 undecided |
| Version consistency | **3/3 checks passed** |
| README | **59/59** relative links, **3/3** anchors resolve |
| Package self-containment | **PASS** — wheel rebuilt, schema present and byte-identical, version `0.0.1` |
| Hygiene | **PASS** — no secrets, artefacts or tracked-ignored files |
| Git state | **WARN** — the working tree is intentionally dirty before the release commit |
| `release_check.py` | **`READY WITH WARNINGS`**, `blockers: []`, warnings `[W6, W7, W9, W10, W11, W12, W13]`, exit 0 |
| JSON output | parses; contract fields present and correct (§7) |

Human output at this revision:

```
release gate
============

  [PASS] tests             849 tests passed
  [PASS] labs              8/8 labs passed
  [PASS] mkdocs            strict build succeeded
  [PASS] licensing         9/9 checks passed; 176 files accounted for (mit 125, cc-by 49, excluded 2, unlicensed 0)
  [PASS] version           declarations agree on 0.0.1
  [PASS] readme            all 59 relative links and 3 anchors resolve
  [PASS] self_containment  wheel rebuilt; schema present and byte-identical; version 0.0.1
  [PASS] hygiene           no secrets, artefacts or tracked-ignored files
  [WARN] git_state         the working tree is not clean

Classification: READY WITH WARNINGS
```

(The coverage figures above are the post-audit totals; before this audit existed the count was **175** — `cc-by 48`.)

## 17. Remaining residuals

| # | Residual | Notes |
| --- | --- | --- |
| R-1 | **CI runs pytest twice** — once as its own step and once inside `release_check`. | Deliberate: the brief asked to place the gate after the existing checks. If the duplication is unwanted, the standalone step could later be dropped and the aggregate kept, or the gate run as a separate job. |
| R-2 | **MkDocs is a `WARN` in CI** because the job installs `.[dev]`, not `.[docs]`. | Honest and non-blocking; adding the `docs` extra would change the install step, which the brief discouraged. |
| R-3 | **Self-containment is `WARN` where pip build isolation is unavailable** (offline). | The offline structural check still `FAIL`s a missing/divergent schema; only the end-to-end wheel proof degrades to `WARN`. |
| R-4 | **W12 is emitted unconditionally**, so `READY` is unreachable until the human-judgement residual is retired. | This matches the audits (`research/28`–`research/36`) and is intentional rather than a bug. |
| R-5 | The runner is **not** a substitute for the owner's judgement on W6/W7. | It reports; it does not decide. |

The seven known warnings remain exactly as classified in `research/36`: **no release blocker**, W6 a release-time action, W7 an owner decision, W9/W10/W11/W12/W13 non-blocking warnings.

## 18. Safety confirmation

```
$ git diff --cached --name-only
(empty)

$ git rev-parse --short HEAD
a193076

$ git tag --list
(no tags)

$ ls -d build dist
(absent)
```

* **Nothing staged, no commit, no push, no tag, no GitHub release, no history rewrite.**
* No `reset`, `checkout`, `clean`, `rebase`, `amend` or `stash` was run; every `git` call the runner makes is read-only and asserted as such by test.
* The only new files are `scripts/release_check.py`, `tests/test_release_check.py` and this audit; the only modified files are `.github/workflows/ci.yml` and `README.md`. The Step 17 files (`scripts/check_version.py`, `tests/test_version.py`, `research/35`, `research/36`) remain present and uncommitted.
* No `build/`, `dist/`, wheel, virtual environment or temporary file remains in the repository; every build ran in a temporary directory outside it and was removed.
* No previous audit was modified.

---

*End of Phase 20 — Step 18. The release procedure is now one command: `py scripts/release_check.py` reports **READY WITH WARNINGS** with every gate green and only the known non-blocking warnings, and exits non-zero only on a real blocker. Nothing staged, committed, tagged, pushed or released.*
