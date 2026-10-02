# PHASE 21 — EXACT RELEASE WARNING-SET ASSERTION (B5)

*Implementation record for the follow-on step in
`research/39-v0.1.0-development-plan.md` (B5): turning the current release
warning set into an explicit, regression-protected contract. One regression test
was added; **no** release warning was resolved and **no** gate behaviour was
changed. Nothing was committed, pushed, tagged or version-bumped; the Phase 17
freeze and the `v0.0.1` release are untouched.*

## 0. Scope

This step implements **only** the exact warning-set assertion:

* a focused regression test asserting the repository's release warning IDs are
  exactly `{"W6", "W7", "W12"}`;
* a named `ACCEPTED_RELEASE_WARNINGS` constant that serves as the reviewed policy
  a future change must update deliberately.

**Explicitly NOT done in this step:**

* **W6, W7 and W12 were not resolved** (all three remain, by design).
* **`scripts/release_check.py` was not modified** — no warning detection was
  added, removed, reclassified or suppressed; the existing structured API was
  sufficient, as required.
* **No CI job was added** — B5 is a repository regression test, not a new gate,
  so `.github/workflows/ci.yml` is unchanged.
* **B4.1 Ruff configuration is unchanged** (`[tool.ruff.lint]`).
* **B4.2 mypy configuration is unchanged** (`[tool.mypy]`, `[[tool.mypy.overrides]]`).
* **B4.3 coverage configuration is unchanged** (`pytest-cov==7.0.0` dev extra and
  the report-only `coverage` CI job).
* **`src/`, `labs/` and unrelated documentation were not modified.**
* The project **version remains `0.0.1`** and the **`v0.0.1` tag remains
  untouched**.

## 1. Baseline warning set (measured before editing)

The existing release gate was run *before* editing:

```
python scripts/release_check.py --json
```

| | |
| --- | --- |
| `classification` | **READY WITH WARNINGS** |
| `blockers` | **[]** (empty) |
| `warnings` (IDs) | **`["W12", "W6", "W7"]`** → the set **`{"W6", "W7", "W12"}`** |
| `gates` | all `PASS` except `git_state: WARN` (dirty development tree) |
| exit code | 0 |

`.freebuff/project-id` is confirmed tracked (`git ls-files --error-unmatch`
succeeds), which is the W7 precondition, and `src/agentsec.egg-info/PKG-INFO` is
present but fresh, so **W9 is not emitted**. The measured set is therefore
exactly `{"W6", "W7", "W12"}`.

## 2. Where the warning IDs originate

In `scripts/release_check.py`:

* **`Warning`** (line ~102) is a frozen dataclass `Warning(id: str, summary: str)`
  — the structured warning value, "in the audits' terminology".
* **`detect_warnings(ctx, run)`** (line ~614) builds and returns
  `list[Warning]`, appending `W6`, `W7`, `W9`, `W10`, `W11`, `W12` and `W13` only
  when their conditions hold (`W12` is always appended).
* **`build_report(ctx, run)`** (line ~702) sorts the warnings by ID and exposes
  them structurally in two report fields:
  * `"warnings": [warning.id for warning in warnings]` — the **ID list**;
  * `"warning_details": [{"id": ..., "summary": ...}, ...]` — the full values.

So the structured identifiers are already first-class (`Warning.id`, and the
report's `warnings` / `warning_details`), and no change to `release_check.py`
was needed for a clean structured assertion.

## 3. The exact test added

Added to `tests/test_release_check.py` (the module that already drives the gate
directly), alongside the existing real-repository warning test:

```python
#: The exact release-warning set this repository is allowed to report.
#:
#: These are the three accepted, non-blocking warnings recorded in
#: ``research/31``-``research/36`` and the v0.1.0 development plan:
#:
#: * ``W6``  - ``CITATION.cff`` has no ``date-released`` (set at release time);
#: * ``W7``  - ``.freebuff/project-id`` is tracked and therefore distributed;
#: * ``W12`` - human-judgement licensing residuals remain.
#:
#: None of the three is resolved here. This constant is the *policy*: the
#: exact-set test below fails on any change to the reported IDs, so introducing
#: a new warning (say ``W14``) - or resolving one of these three - is a
#: deliberate, reviewed edit to this constant, not silent drift.
ACCEPTED_RELEASE_WARNINGS = frozenset({"W6", "W7", "W12"})


def _tracked_paths():
    """The repository's tracked paths, from one read-only ``git ls-files``."""
    result = guard.run_command(
        ("git", "-C", str(ROOT), "ls-files"), cwd=ROOT, env=os.environ.copy()
    )
    assert result.returncode == 0, result.stderr
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def test_repository_reports_exactly_the_accepted_warning_set(tmp_path):
    """The real repository emits exactly W6, W7 and W12 - no more, no fewer."""
    runner = FakeRunner()
    runner.git["ls-files"] = "\n".join(_tracked_paths())
    ids = {w.id for w in guard.detect_warnings(context(ROOT, tmp_path), runner)}
    assert ids == ACCEPTED_RELEASE_WARNINGS, (
        f"release warning policy changed: {sorted(ids)}; update "
        "ACCEPTED_RELEASE_WARNINGS deliberately if that is intended"
    )
```

(An `import os` was added for the read-only `git ls-files` call.)

### 3.1 Why the assertion is structured, not text-based

* It asserts on **`Warning.id`** values returned by the gate's own
  `detect_warnings`, and compares **sets**, not on the rendered console block
  (`render_human`'s `[WARN] W6 ...` lines). Console text is presentation: it is
  padded, ordered and worded for humans and can change without any change to the
  warning contract, so pinning it would be fragile in the wrong direction.
* Set equality is also direction-complete: it fails if a warning is **added**
  (e.g. `W14`) *and* if an accepted one is **removed**, which a
  "is-subset-of-known" check would not catch.
* It reuses the same `FakeRunner`/`context` scaffolding as the surrounding
  tests, so a gate failure is reported as a normal assertion rather than a
  subprocess error.

### 3.2 Real tracked-state input (W7)

W7 depends on whether `.freebuff/project-id` is **tracked**, so the test answers
`git ls-files` from the real checkout (one read-only command — the same command
`detect_warnings` runs) instead of faking it. This keeps W7 an assertion about
real repository state, and `run_command` is read-only, so nothing is mutated.
Everything else is driven by the checked-in files the gate reads directly.

## 4. How a future warning is detected

If a new warning such as `W14` is introduced into `detect_warnings` (or a new
file/state makes an existing detection fire), the real repository's ID set no
longer equals `ACCEPTED_RELEASE_WARNINGS`, and
`test_repository_reports_exactly_the_accepted_warning_set` fails with the
offending set printed. The only way to green it is to **deliberately edit the
`ACCEPTED_RELEASE_WARNINGS` policy** in the same reviewed change. Conversely, if
W6, W7 or W12 stops being emitted (e.g. `date-released` is added to
`CITATION.cff`), the test fails until the policy is updated — so a warning cannot
be resolved silently either.

Demonstrated locally by evaluating the gate's own detection against the real
checkout:

```
observed warning ids: ['W12', 'W6', 'W7']
accepted policy     : ['W12', 'W6', 'W7']
exact match         : True
would a W14 be caught: True
```

## 5. Validation results

Run after the edit, locally, with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **853 passed** (852 before + the new regression test) |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `python -m mypy` | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 184 files accounted for (mit 125, cc-by 57, excluded 2, unlicensed 0), including this record |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]` |
| `git diff --check` | clean (no whitespace errors) |

### 5.1 Explicit verification checklist

| Check | Result |
| --- | --- |
| Tests pass at 852+ | **853** pass |
| Labs remain 8/8 | yes |
| Ruff remains clean | yes |
| mypy remains at 0 errors | yes |
| Coverage configuration unchanged | yes (`pytest-cov==7.0.0` dev extra + report-only `coverage` CI job untouched) |
| Release gate remains READY WITH WARNINGS | yes |
| `blockers` remain `[]` | yes |
| Warning IDs exactly `W6, W7, W12` | yes |
| `git_state` the only WARN (dirty tree) | yes — every other gate `PASS` |
| No generated artifacts / caches / probes / coverage files tracked | yes (none in `git status`) |
| `v0.0.1` untouched | yes — tag object `cd60b32c7da3174423657e3ec53ecb7dd120eecb` |
| Version remains `0.0.1` | yes (`check_version.py` 3/3) |

## 6. Remaining W6/W7/W12 status

All three accepted warnings **remain exactly as they were** — none was resolved,
suppressed or reclassified in this step:

| ID | Meaning | Status after this step |
| --- | --- | --- |
| **W6** | `CITATION.cff` has no `date-released` | **Remains** (to be set at release time) |
| **W7** | `.freebuff/project-id` is tracked and therefore distributed | **Remains** (still tracked) |
| **W12** | human-judgement licensing residuals remain | **Remains** (always emitted) |

`git_state` continues to be `WARN` solely because the working tree is dirty
during development; that is a gate status, not one of the `W6`–`W13` warning IDs.

## 7. Exact files changed

```
tests/test_release_check.py     (+import os; +ACCEPTED_RELEASE_WARNINGS policy;
                                 +_tracked_paths helper;
                                 +test_repository_reports_exactly_the_accepted_warning_set)
research/45-exact-warning-set-assertion.md   (this record, new)
```

No other file was modified. In particular `scripts/release_check.py`,
`pyproject.toml`, `.github/workflows/ci.yml`, `src/`, `labs/` and
`.github/workflows/docs.yml` are unchanged relative to the end of B4.3.

## 8. Non-alteration confirmation

Confirmed by `git status` / `git diff` / `git rev-parse` at the end of this step:

* **No release warning was resolved** — W6, W7 and W12 are all still reported.
* **`scripts/release_check.py` is unmodified** (no tracked diff).
* **No gate was weakened or bypassed**, and **no warning detection was changed**.
* **The package version remains `0.0.1`**; **the `v0.0.1` tag is untouched**.
* **The labs are unmodified** (8/8).
* **`research/20`–`research/44` are unmodified** (only untracked audit records
  from the earlier steps and this new `research/45` exist).
* **The B4.1 Ruff, B4.2 mypy and B4.3 coverage configurations are unmodified.**
* **Nothing was committed, pushed or tagged.**

### Safety boundary (Phase 17)

This step adds no runtime code, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains **HOLD**;
no novelty, effectiveness, security-effectiveness, benchmark or publication claim
is made.
