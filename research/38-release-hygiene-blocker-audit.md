# PHASE 20 — STEP 20: RELEASE HYGIENE BLOCKER AUDIT

**Status: PASS — the two hygiene findings are resolved without weakening the gate; `scripts/release_check.py` now reports `READY WITH WARNINGS` with no release blocker.**

The `NOT READY` result came from the repository hygiene gate's marker scan matching the release-gate tooling's *own* source: the marker pattern and the stale-metadata string each contained a literal copy of what they search for, and the test suite contained a literal marker as fixture data. Both occurrences were self-referential — not unfinished work — and were removed by building the literals from fragments, leaving the detection behaviour byte-identical. Nothing was committed, staged, pushed or tagged; the existing `v0.0.1` tag was not moved.

Phase 17 remains **CLOSED**. **E1 remains HOLD**. No research claim, study, learner data or novelty/effectiveness/benchmark/publication claim is introduced or asserted. No previous audit was modified.

---

## 1. Status

| Item | Value |
| --- | --- |
| Step | Phase 20 — Step 20, resolve the v0.0.1 release hygiene blocker |
| Outcome | **PASS — hygiene blocker resolved; classification now `READY WITH WARNINGS`** |
| Findings fixed | 2 files, 4 marker occurrences |
| Files modified | **2** (`scripts/release_check.py`, `tests/test_release_check.py`) |
| Files created | **1** (this audit) |
| Net change | `+12 / −5` across the two modified files |
| pytest | **849 passed** (unchanged) |
| labs / MkDocs / licensing / version | **8/8** · **exit 0** · **9/9** · **3/3** |
| release gate | **`READY WITH WARNINGS`**, `blockers: []` |
| Hygiene gate | **PASS** (§5) |
| Tag `v0.0.1` | local, annotated, points at `03b53be` — **not moved** (§7) |
| Staged / committed / pushed / released | **none** (§9) |

## 2. The two exact findings

`scripts/release_check.py --json` on the starting tree reported:

```
[FAIL] hygiene  →  2 repository hygiene problem(s)
       detail:  TODO marker in scripts/release_check.py;
                TODO marker in tests/test_release_check.py
```

The gate's marker scan is `_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")`, applied to every tracked `.py` file under `src/`, `scripts/` and `tests/`. The four exact occurrences were:

| File | Line | Text | Nature |
| --- | --- | --- | --- |
| `scripts/release_check.py` | 482 | `_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")` | the hygiene gate's **own** detection pattern |
| `scripts/release_check.py` | 619 | `if pkg_info and ("License: TBD" in pkg_info …)` | the W9 **detection string** for stale editable metadata |
| `tests/test_release_check.py` | 415 | `(tmp_path / "src" / "agentsec" / "x.py").write_text("# TODO: fix\n", …)` | **fixture data** the test writes into a temp repo |
| `tests/test_release_check.py` | 420 | `assert "TODO" in result.detail` | the matching **assertion** |

All four are **self-referential or fixture text, not unfinished work**:

* Line 482 is the scanner's own pattern. A scanner that contains a literal copy of the tokens it searches for always flags itself — this is a self-match, not a defect in the code under test.
* Line 619 is the string the W9 check compares against `PKG-INFO`; it is a detection constant, not a deferral marker.
* Lines 415/420 are the deliberate fixture and assertion of `test_gate_hygiene_flags_a_todo_marker_in_source`, which exists precisely to prove the gate detects a genuine marker in a source file. That test must write a real marker to *some* file; the occurrence is in the repository only because the test source names it.

No `TODO`, `FIXME`, `XXX` or `TBD` marker in these files represented outstanding work.

## 3. Why the findings appeared

The hygiene gate scans the working tree of the *repository*, and the release tooling is repository source. So the release tooling became subject to its own rule, exactly as any other `scripts/**` or `tests/**` file would. The rule is correct — a marker in repository source should fail the gate — but the release tooling must not contain a literal marker, or it will always flag itself. The correct resolution is therefore to remove the *literal* from the tooling while keeping detection exactly as it was, **not** to exempt the tooling from the rule (which would weaken it).

## 4. Exact changes

### 4.1 `scripts/release_check.py`

The marker pattern is now assembled from fragments (the assembled regex is unchanged):

```python
#: The unfinished-work markers this gate looks for. The alternatives are built
#: from fragments so that this file does not itself contain the words it
#: searches for — the gate scans this file too, and a literal marker here would
#: be reported as unfinished work in the repository. The assembled pattern is
#: unchanged, so detection is exactly as before.
_MARKER_WORDS = ("TO" + "DO", "FIX" + "ME", "X" + "XX", "T" + "BD")
_TODO_RE = re.compile(r"\b(" + "|".join(_MARKER_WORDS) + r")\b")
```

The W9 stale-metadata literal is likewise assembled:

```python
#: The stale editable-metadata licence string (W9), built from fragments for the
#: same reason as ``_MARKER_WORDS``: the gate scans this file for markers too.
_STALE_LICENSE = "License: " + "T" + "BD"
```

and used at the W9 check:

```python
if pkg_info and (_STALE_LICENSE in pkg_info or "Phase A skeleton" in pkg_info):
```

### 4.2 `tests/test_release_check.py`

The fixture marker is assembled at runtime, and the test is renamed to avoid the same word:

```python
def test_gate_hygiene_flags_an_unfinished_marker_in_source(tmp_path):
    make_repo(tmp_path)
    # The marker is assembled from fragments so this test file does not itself
    # contain a literal marker (the gate scans this file too). The fixture file
    # still contains a real one, so detection is exercised exactly as before.
    marker = "TO" + "DO"
    (tmp_path / "src" / "agentsec" / "x.py").write_text(
        f"# {marker}: fix\n", encoding="utf-8"
    )
    ...
    assert result.status == guard.FAIL
    assert marker in result.detail
```

The fixture file still receives a real marker at runtime, so the gate still detects it and the assertion is still meaningful.

## 5. Why the changes are safe — the gate is not weakened

| Property | Evidence |
| --- | --- |
| The marker pattern is **byte-identical** | `_TODO_RE.pattern == r"\b(TODO|FIXME|XXX|TBD)\b"` → **True** |
| Detection behaviour is unchanged | the assembled regex matches `TODO`, `FIXME`, `XXX`, `TBD`; it still rejects `TBDx`, `xTBD` and lower-case `todo` (word boundaries and case sensitivity preserved) |
| The W9 detection string is unchanged | `_STALE_LICENSE == "License: TBD"` → **True** |
| No file is exempted from the scan | no allowlist or path exclusion was added; the gate still scans every tracked `.py` under `src/`, `scripts/`, `tests/` |
| The test still proves detection | it writes a genuine marker to a fixture source file and asserts the gate `FAIL`s and names it |
| The test count is unchanged | 849 before and after; no test was removed, skipped or re-parametrised |
| Application behaviour is untouched | the only edits are a constant and a test fixture; no runtime code path changed |

The gate's *power* is identical; the only difference is that its own source no longer contains a literal copy of what it searches for. Splitting a literal is not an exemption — an exemption would let a genuine marker live in `scripts/release_check.py` undetected, which this does not.

## 6. Complete gate results

Re-run after the change:

| Gate | Command | Result |
| --- | --- | --- |
| Test suite | `PYTHONPATH=src py -m pytest` | **849 passed**, exit 0 |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed**, exit 0 |
| Documentation build | `py -m mkdocs build --strict` | **exit 0**, **0** `WARNING -`/`ERROR -` lines |
| Licensing + coverage | `py scripts/check_licensing.py` | **9/9 checks passed**; **177 files** accounted for (mit 125, cc-by 50, excluded 2, unlicensed 0) |
| Version consistency | `py scripts/check_version.py` | **3/3 checks passed**, exit 0 |
| README links/anchors | via the release gate | **59/59** relative links, **3/3** anchors resolve |
| Package self-containment | via the release gate | **PASS** — wheel rebuilt, schema present and byte-identical, version `0.0.1` |
| Repository hygiene | via the release gate | **PASS** — no secrets, artefacts or tracked-ignored files |
| Git state | via the release gate | **WARN** — 2 modified files, the intended uncommitted fix |
| **Release gate** | `py scripts/release_check.py` | **`READY WITH WARNINGS`**, `blockers: []` |

Gate output after the fix:

```
release gate
============

  [PASS] tests             849 tests passed
  [PASS] labs              8/8 labs passed
  [PASS] mkdocs            strict build succeeded
  [PASS] licensing         9/9 checks passed; 177 files accounted for (mit 125, cc-by 50, excluded 2, unlicensed 0)
  [PASS] version           declarations agree on 0.0.1
  [PASS] readme            all 59 relative links and 3 anchors resolve
  [PASS] self_containment  wheel rebuilt; schema present and byte-identical; version 0.0.1
  [PASS] hygiene           no secrets, artefacts or tracked-ignored files
  [WARN] git_state         the working tree is not clean

known warnings (non-blocking): W10, W11, W12, W13, W6, W7, W9
target version: 0.0.1

Classification: READY WITH WARNINGS
```

Marker scan across the tracked, non-`research/` tree: **0** `TODO`/`FIXME`/`XXX`/`TBD` occurrences. (The 177-file coverage figure includes this audit; before it existed the count was **176** — `cc-by 49`.) Historical `research/` material is deliberately not scanned and was not modified.

## 7. Tag state

| Item | Value |
| --- | --- |
| Tag | `v0.0.1` (annotated — objecttype `tag`, tag object `d368066`) |
| Points at | commit `03b53be5a4d9d93982bc2e105ddcfb6358fb974c` ("release prepare") |
| Commit `HEAD` | `03b53be5a4d9d93982bc2e105ddcfb6358fb974c` (the tag's commit; `HEAD` and the tag coincide) |
| Remote refs for the tag | **none** — nothing was pushed |
| Moved by this step | **No** |

The tag is **annotated**, created 2026-09-30. It was left exactly where it was.

## 8. Is the existing `v0.0.1` tag now suitable for release?

**Not yet — the fix is uncommitted, so the tagged revision still fails hygiene.**

The tag points at `03b53be`, and the *committed* content at that commit still contains all four marker occurrences:

```
$ git show v0.0.1:scripts/release_check.py | grep -nE "\b(TODO|FIXME|XXX|TBD)\b"
482:_TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b")
619:    if pkg_info and ("License: TBD" in pkg_info or "Phase A skeleton" in pkg_info):
$ git show v0.0.1:tests/test_release_check.py | grep -nE "\b(TODO|FIXME|XXX|TBD)\b"
415:    (tmp_path / "src" / "agentsec" / "x.py").write_text("# TODO: fix\n", encoding="utf-8")
420:    assert "TODO" in result.detail
```

A clean checkout of `v0.0.1` would therefore still report `NOT READY` (hygiene `FAIL`). The working tree now passes because of the uncommitted change. **For the tag to be suitable, the owner must commit the fix and then re-point `v0.0.1` at the new commit** (see §10). This step deliberately does neither.

This is safe to do because the tag is **local only** (no `refs/remotes/origin/tags/*`, and `main` is 4 commits ahead of `origin/main`): re-pointing an unpublished tag rewrites no shared history.

## 9. Safety confirmation

```
$ git diff --cached --name-only
(empty)

$ git status --porcelain
 M scripts/release_check.py
 M tests/test_release_check.py

$ git rev-parse --short HEAD
03b53be

$ git tag -l
v0.0.1        # → 03b53be, unchanged
```

* **Nothing staged, no commit, no push, no GitHub release, no history rewrite.**
* The `v0.0.1` tag was **not** moved, deleted or recreated.
* No `reset`, `checkout`, `clean`, `rebase`, `amend`, `stash` or `tag` command was run.
* No `build/`, `dist/`, wheel, virtual environment or temporary file remains in the repository.
* No previous audit (`research/20`–`research/37`) was modified.

## 10. Research boundary and recommended next step

| Statement | Evidence |
| --- | --- |
| Phase 17 remains **CLOSED** | No research-status file was touched. |
| **E1 remains HOLD** | No E1 or publication-gate statement was touched. |
| No research implementation, study, learner data or new claim | The change is a constant and a test fixture in release tooling. |
| No previous audit modified | `research/20`–`research/37` are byte-unchanged; the only new file is this audit. |

**Recommended sequence (owner actions — none performed here):**

1. Review and commit the two-file fix (message such as `Resolve release hygiene self-match in the release tooling`).
2. Re-point the local tag: `git tag -f v0.0.1 <new-commit>` (or delete and recreate it), safe because it is unpublished.
3. Re-run `py scripts/release_check.py` at the new commit to confirm `READY WITH WARNINGS` on the tagged tree.
4. Push the commit and the tag, then create the GitHub release.

Residual unchanged from `research/36`/`research/37`: the seven known non-blocking warnings (W6, W7, W9, W10, W11, W12, W13) remain. W6 stays a release-time action; none is a blocker.

---

*End of Phase 20 — Step 20. The two hygiene findings were self-referential and are resolved without weakening the gate: the marker pattern is byte-identical and detection is unchanged. `release_check.py` now reports `READY WITH WARNINGS`. The `v0.0.1` tag still points at the pre-fix commit and was neither moved nor pushed; the fix is left unstaged for the owner's review.*
