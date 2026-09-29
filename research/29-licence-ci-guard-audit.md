# Phase 20 — Step 12: Licence Guardrails in CI

**Phase:** 20 — Step 12 (licence metadata guardrails)
**Date:** 2026-09-29
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs`
**Audited revision:** `995cf68` (`main`) with the uncommitted Step 10–12 working tree
**Deliverable:** `scripts/check_licensing.py`, `tests/test_licensing.py`, one step in `ci.yml`, a short README note.
**Mode:** repository maintenance only — no architecture, lab, policy, scenario, trace or research change.

---

## 1. Starting repository state

`HEAD` was `995cf68` ("Research finding complete"), which tracks `research/20`–`research/27`. The working tree was **not** clean: it carried the still-uncommitted Step 10 and Step 11 work.

```
$ git status --porcelain
 M README.md
 M pyproject.toml
?? CITATION.cff
?? LICENSE
?? LICENSE-DATA
?? research/28-content-licensing-audit.md
```

Because the licence files themselves were (and remain) untracked, nothing in CI would have caught their accidental deletion, replacement or divergence — which is precisely the gap this step closes.

---

## 2. The existing dual-licence boundary

Established by Steps 10–11 and treated as fixed:

| Material | Licence | Declared in |
|---|---|---|
| Software (`src/`, `tests/`, `scripts/`) | MIT | `LICENSE`, `pyproject.toml`, `CITATION.cff` |
| Machine-readable configuration (`policies/`, `configs/`, `labs/**/*.yaml`, `schemas/`, `research/tables/*.csv`, `mkdocs.yml`, `pyproject.toml`, `.github/`) | MIT | `LICENSE` |
| Repository-authored Markdown (`README.md`, `docs/`, `labs/**/*.md`, `research/**/*.md`) | CC BY 4.0 | `LICENSE-DATA` |
| Third-party quotations, bibliographic records and any third-party asset | **excluded from both grants** | `LICENSE-DATA` §3, `README.md` → `Licensing` |

The boundary is documented across five files, and the point of the guard is that **those five declarations must keep agreeing with each other**.

---

## 3. Guardrail design

Three rules shaped the design.

1. **Assert the declarations, not the files.** The guard knows about the five files that *declare* the licence boundary. It does not walk the tree deciding what each file "is".
2. **Semantic markers, not hashes.** Step 12 explicitly warned against brittle whole-file hashing; the guard therefore looks for a small number of short, stable phrases that the boundary genuinely depends on. Reflowing the prose does not fail the build; deleting the statement does.
3. **Offline, read-only, standard library only.** No network, no download of licence texts, no dependency on the package being installed, no writes.

The guard is organised as one function per check returning a `CheckResult(name, ok, detail)`, with a `CHECKS` tuple defining report order and a `run_checks(root)` entry point that accepts any root — which is what makes the failure cases testable against temporary directories.

---

## 4. Exact checks implemented

Six checks, run in this order.

| # | Check | Objective assertion | Markers used |
|---|---|---|---|
| 1 | `LICENSE` | exists; contains the MIT licence; does **not** contain the CC BY 4.0 text (catches two files swapped) | `MIT License`, `Permission is hereby granted, free of charge`, `THE SOFTWARE IS PROVIDED "AS IS"` |
| 2 | `pyproject.toml` | parses as TOML; `project.license` declares MIT in any supported spelling | `MIT` as a string; `{text = "MIT"}`; `{file = "LICENSE"}` (accepted because check 1 proves `LICENSE` is MIT) |
| 3 | `CITATION.cff` | has a top-level `license:` field whose value is MIT | `license: MIT` |
| 4 | `LICENSE-DATA` | exists; identifies CC BY 4.0; cites the canonical licence location; embeds the **complete** legal code | `CC BY 4.0`, `Creative Commons Attribution 4.0 International`, `creativecommons.org/licenses/by/4.0`, and all eight `Section N --` headings |
| 5 | `README.md` | has a `## Licensing` section naming both licences and both licence files | `MIT`, `CC BY 4.0`, `LICENSE`, `LICENSE-DATA` |
| 6 | third-party exclusion | third-party material is still excluded from the repository's grants, **in both** `LICENSE-DATA` and `README.md` | `third-party material`, `respective owners` (case-insensitive) |

The legal-code completeness check (all eight sections present) is a genuine stabiliser: it cannot detect a subtle wording change — no network — but it does catch truncation, which is the realistic way a 19 KB legal text gets damaged during an edit.

Exit codes: **`0`** when all six pass, **`1`** otherwise. Failures print the file, the problem and what was expected, followed by a pointer to the README's `Licensing` section and the instruction to fix the declaration rather than the check.

Sample output on the real repository:

```
licence metadata check
======================

  ok    LICENSE                MIT licence text present
  ok    pyproject.toml         project.license.text = 'MIT'
  ok    CITATION.cff           license: MIT
  ok    LICENSE-DATA           CC BY 4.0 notice and complete legal code (8/8 sections)
  ok    README.md              MIT and CC BY 4.0 boundary documented
  ok    third-party exclusion  stated in LICENSE-DATA and README.md

Result: 6/6 checks passed
```

A `<root>` argument (`--root PATH`, defaulting to the script's grandparent directory) exists for testing and manual inspection; it does not weaken the check, since the guard has no notion of a "known good" root.

---

## 5. Files added and modified

| File | Action | Detail |
|---|---|---|
| `scripts/check_licensing.py` | **created** | 359 lines. Standard library only (`argparse`, `dataclasses`, `pathlib`, `sys`, `tomllib`). No writes, no network. |
| `tests/test_licensing.py` | **created** | 304 lines, 24 tests over `tmp_path` fixtures plus the real repository. |
| `.github/workflows/ci.yml` | **modified** | `+11/−1`: one new step ("Check the licence metadata") and a header-comment paragraph. No existing step removed, reordered or weakened. |
| `README.md` | **modified** | `+13/−4`: CI paragraph in `## Licensing`, a licence row in the `Verification status` table, the test count corrected, and the `ci.yml` sentence extended. |
| `research/29-licence-ci-guard-audit.md` | **created** | This record. |

Not modified: `src/**`, `labs/**`, `policies/**`, `configs/**`, `schemas/**`, `mkdocs.yml`, `.github/workflows/docs.yml`, `CITATION.cff`, `LICENSE`, `LICENSE-DATA`, `pyproject.toml`, and every research record `20`–`28`.

---

## 6. CI integration

The step runs **inside the existing `checks` job**, immediately after Python is set up and **before** `pip install`:

```yaml
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Check the licence metadata
        run: python scripts/check_licensing.py

      - name: Install the package (with dev extras)
```

Verified order: `Check out the repository` → `Set up Python` → **`Check the licence metadata`** → `Install the package (with dev extras)` → `Run the test suite` → `Run the lab self-check`. The workflow still parses as valid YAML.

Two deliberate decisions:

* **Why before the install:** the guard uses only the standard library, so it does not need the package, the dev extra or the network. Putting it first makes a licensing mistake fail the job in seconds instead of after an install, and it keeps the failure at the top of the log.
* **Why the job's display name was left alone:** the job is still called `tests and lab self-check` even though it now does three things. Branch-protection rules can reference a required check by its *name*, so renaming it is a change with consequences outside this repository. The new step's own name is explicit, and the header comment now describes all three responsibilities.

`docs.yml` was deliberately **not** touched: it builds and publishes the site, and duplicating the licence check there would add a second place for the contract to drift without adding coverage — both workflows trigger on push to `main`.

---

## 7. Test strategy

24 tests in `tests/test_licensing.py`, in four groups.

1. **The contract holds for the real repository** (2 tests): `run_checks(ROOT)` reports no failures, and the report order is asserted, since that order is part of the CI output. `main(["--root", ROOT])` returns `0` and prints `6/6 checks passed` with no `FAIL`.
2. **A valid fixture passes, and each declaration can fail on its own** (16 tests): a minimal consistent repository is written into `tmp_path`, then exactly one declaration is broken at a time — `LICENSE` missing; `LICENSE` holding an Apache licence; `LICENSE` holding the CC text; `LICENSE-DATA` missing; `LICENSE-DATA` without any content licence; `CITATION.cff` missing; `CITATION.cff` naming Apache-2.0; `README.md` missing; a truncated legal code; `README.md` missing a licence; `README.md` missing its `## Licensing` section; the third-party exclusion removed from `README.md`; a wrong `pyproject.toml` licence; and a failing run that must explain itself and exit `1`.
3. **Accepted spellings** (3 tests): `license = "MIT"`, `{text = "MIT"}` and `{file = "LICENSE"}` all pass, so the guard does not prescribe one packaging style.
4. **The guard itself is offline and read-only** (3 tests): an AST check asserts imports are a subset of `{__future__, argparse, dataclasses, pathlib, sys, tomllib}`; a source scan asserts no `urllib`/`urlopen`/`requests`/`subprocess` and no `write_text`/`write_bytes`/`open(`/`mkdir`; and running the guard against the repository is asserted to leave all five declarations byte-identical afterwards.

**A constraint worth recording.** `tests/test_architecture.py::test_tests_do_not_reference_the_network` forbids the literal strings `http://`, `https://` and `socket` in *any* file under `tests/`. The guard's fixtures therefore cite the canonical licence path **without a scheme** (`creativecommons.org/licenses/by/4.0`), which is also what the check asserts. This is a good example of the repository's own discipline shaping a new test rather than the new test bending it.

**Why the test count changed from 694 to 719.** The increase is `+25`, in two parts:

* **+24** — the new `tests/test_licensing.py` module.
* **+1** — `tests/test_architecture.py::test_no_banned_dependency_in_tests` is parametrized over `python_files(TESTS)`, i.e. over every `.py` file found under `tests/`. Adding one test module adds one parametrized case to that existing test.

The arithmetic closes exactly: `694 + 24 + 1 = 719`. (A run with `--ignore=tests/test_licensing.py` reports **695**, not 694, for the same reason — the parametrization scans the directory, so it still sees the new file even when pytest is told to ignore its module. That is the correct behaviour, not a leak.)

No existing test was modified, skipped, xfailed or removed.

---

## 8. Validation results

| Check | Command | Result |
|---|---|---|
| Test suite | `PYTHONPATH=src py -m pytest` | **719 passed**, exit 0 (694 → 719, explained above) |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed** (LAB-00 … LAB-07), exit 0 |
| Documentation build | `py -m mkdocs build --strict` | **exit 0**; the only `warning` match is line 2, Material for MkDocs' informational upstream 2.0 notice |
| Licence guard | `py scripts/check_licensing.py` | **6/6 checks passed**, exit 0 |
| Licence guard on a broken fixture | `py scripts/check_licensing.py --root <tmp>` | exit **1**, with `FAIL` lines naming the file and the missing marker |
| CI workflow validity | YAML parse of `.github/workflows/ci.yml` | valid; step order verified programmatically |
| Test count decomposition | suite, new module, and `--ignore` run | `719 = 694 + 24 + 1`; ignored run reports `695` |
| README links | every relative link resolved against the filesystem | **42/42** resolve, including the new `scripts/check_licensing.py` link; 0 broken |
| Guard determinism | run twice, and with `--root` | identical output; no environment-specific paths (root derives from `__file__`) |

---

## 9. False-positive and false-negative boundaries

Stated explicitly, because a guard that is trusted for more than it does is worse than no guard.

**False positives — the guard can fail while the licensing is perfectly sound**

| Situation | Why it fails | Judgement |
|---|---|---|
| Rewording the licence notices (e.g. dropping "respective owners") | marker phrases are literal | Accepted. The markers were chosen as the statements the boundary *depends on*; the failure message names the exact missing phrase, so the fix is one sentence. |
| `pyproject.toml` using a non-SPDX spelling such as `license = "MIT License"` | only exact `MIT` is accepted | Accepted risk. `MIT` is the SPDX identifier and the canonical declaration; a variant spelling is worth flagging once. |
| `CITATION.cff` with a trailing comment (`license: MIT  # software only`) | the line scan does not strip comments | Known limitation of staying YAML-parser-free. Not present today. |
| CFF `license` becoming a list, to express dual licensing | the guard expects a scalar | Intentional: CFF 1.2.0 defines one licence per cited work, so a list is a modelling error worth surfacing. |
| Renaming or relocating `LICENSE-DATA` | the file name is part of the contract | Intentional — the name is referenced by README and by the planning records. |

**False negatives — drift the guard will *not* catch**

| Gap | Consequence |
|---|---|
| It does not classify files. A new Markdown file is not asserted to be CC BY, and a new YAML file is not asserted to be MIT. | A new file could be added without the README's table being updated, and the guard still passes. **This is the deliberate conservative limit** — see §10. |
| It does not compare `LICENSE-DATA`'s legal code to Creative Commons' canonical text. | Only the eight section headings and the canonical citation are checked. A subtle wording change inside the legal code would pass. Step 11's byte-identity verification (md5 `2ab724713fdaf49e4523c4503bfd068d`) was a one-off manual check — re-confirmed this step — and re-verifying it in CI would require a download, which §3 forbids. |
| It does not detect a third-party file being added to the repository. | Out of scope by construction: the guard cannot know who owns a file. |
| It does not verify copyright holder names, years or the correctness of the README's path lists. | Those are content-review matters, not metadata consistency. |

---

## 10. Why the guard does not adjudicate provenance

Step 12 forbade exactly the temptation a licensing check invites: scanning the tree and declaring that "every `.md` is CC BY", "every YAML is MIT" and "every file belongs to the repository author". That kind of scanner is both **brittle** and **legally unsafe**:

* **Brittle**, because it turns a file extension into a legal conclusion. A future `labs/LAB-09/README.md` that quotes a third-party figure would be silently declared CC BY.
* **Unsafe**, because it asserts ownership the repository may not have. Step 11 established that the research records contain third-party quotations and that **those remain outside both grants**; a scanner that swept them into the CC BY grant would contradict the licence the repository actually publishes.

So the guard checks only what the repository **says about itself**: that the five declarations still agree, that both licence files exist and still say what they said, that the legal code is still whole, and that the third-party exclusion has not been quietly dropped. Determining ownership and the licence of third-party material needs human judgement, and the guard's own docstring, its report and the README note all say so.

---

## 11. Research-boundary confirmation

* **Phase 17 remains CLOSED.** Nothing under `docs/development.md` or the frozen direction list was touched.
* **E1 remains HOLD.** `research/20`–`research/28` were not edited.
* **No research claim, novelty claim, educational-effectiveness claim, benchmark claim, security claim or publication claim** was introduced. The new files speak only about licence metadata.
* **No literature search** was performed, and no prior-art conclusion was revisited.
* **No learner data** was collected, referenced or solicited.
* **No educational study** was designed, and **no paper** was drafted.
* The 719-test suite, the 8/8 lab self-check and the MkDocs build are unchanged in substance: the only test-count movement is the licensing module itself and its parametrization effect.

---

## 12. Final git status

```
$ git status --porcelain
 M .github/workflows/ci.yml
 M README.md
 M pyproject.toml
?? CITATION.cff
?? LICENSE
?? LICENSE-DATA
?? research/28-content-licensing-audit.md
?? scripts/check_licensing.py
?? tests/test_licensing.py

$ git diff --name-only
.github/workflows/ci.yml
README.md
pyproject.toml

$ git diff --numstat
11      1       .github/workflows/ci.yml
55      7       README.md
1       1       pyproject.toml
```

`HEAD` is still `995cf68`. `README.md` and `pyproject.toml` also carry the uncommitted Step 10–11 changes, which is why their diffs exceed this step's own edits. `research/29-licence-ci-guard-audit.md` is expected to appear untracked after this record is written.

---

## 13. Confirmation: nothing staged

**No `git add` was run, and nothing is staged.** `git diff --cached --name-only` is empty; every change is in the working tree only.

---

## 14. Confirmation: nothing committed

**No `git commit` was run.** The repository has no commit from this step; `HEAD` is unchanged at `995cf68`.

---

## 15. Confirmation: nothing pushed

**No `git push` was run, and no remote operation of any kind was performed.** No `git reset`, `git checkout`, `git clean`, `git rebase` or `git amend` was run either.

---

## 16. Remaining licensing residuals

Carried forward from `research/28` §16, unchanged by this step, plus what this step adds:

**Unchanged from Step 11**

1. `LICENSE`'s MIT text refers to "this software and associated documentation files", which overlaps the CC BY grant. The guard does **not** resolve this; it only requires the declarations to stay mutually consistent. Deciding whether the boundary should be strictly exclusive is the owner's call.
2. CC BY 4.0 was adopted from documented intent, not from an explicit decision; CC BY-SA 4.0 or CC0 remain viable alternatives. A switch would mean editing `LICENSE-DATA`, one README table row — and nothing in the guard, which keys on "CC BY 4.0" as the marker and would need its marker updated in the same commit.
3. The adopted content scope is narrower than the older planning records describe ("data/docs/documents"); the guard does not arbitrate that difference.
4. `.freebuff/project-id` remains tracked and is covered by neither grant; still not deleted.
5. No SPDX identifiers anywhere. A `license-files` entry in `pyproject.toml` or per-file SPDX headers would make the boundary machine-readable; the guard does not require them.
6. `research/27` still describes the pre-Step-10 state, deliberately unmodified.
7. No release or tag exists, so `CITATION.cff` still has no `date-released`.
8. Traces under `runs/` remain git-ignored and unlicensed; if example traces are ever published, a data decision is needed.
9. `pyproject.toml`'s `description` still ends "(Phase A skeleton)" — stale, out of scope.

**New in this step**

10. **The guard cannot see a new, wrongly-scoped file.** Adding a Markdown file to `labs/` without updating the README's licensing table passes CI. Closing this properly needs a human decision about the new file's provenance, not a scanner — so the README instruction stands: update the table, then the guard stays honest.
11. **The legal code is no longer byte-verified on every run.** Step 11's md5 equivalence check was manual and one-off; CI checks only structure and citation. A future edit inside the legal text would pass CI silently. Acceptable given the no-network rule, and recorded so nobody assumes otherwise.
12. **No pre-commit hook.** The guard runs in CI only, so a broken declaration is caught on push rather than on commit. Adding it to a local hook (or to the docs workflow) is possible but would duplicate the same check in a second place.
13. **The guard's markers are English phrasing.** Rewording the licence notices — a legitimate editorial act — requires updating the markers in the same commit. The failure message names the missing phrase precisely so the coupling is obvious rather than mysterious.

---

## 17. Conclusion

The repository's dual-licence boundary is now **self-checking**. Six objective assertions in `scripts/check_licensing.py` verify that `LICENSE`, `LICENSE-DATA`, `pyproject.toml`, `CITATION.cff` and `README.md` still agree about which licence applies to what, that both licence files are still present and still say what they said, that the CC BY 4.0 legal code is still complete, and that the third-party exclusion has not been quietly dropped. The check runs first in CI, uses only the standard library, never touches the network, never writes, and is covered by 24 tests including a failure case for every declaration it protects.

It is deliberately **not** a provenance adjudicator, and §9 and §10 record exactly where it stops — so the guard can be trusted for what it does without being trusted for more.

**What this step does not establish:** research novelty, publication acceptance, educational effectiveness, causal learning effects, security effectiveness, model behaviour, benchmark validity, or measurement validity. It verifies licence metadata consistency and nothing else.
