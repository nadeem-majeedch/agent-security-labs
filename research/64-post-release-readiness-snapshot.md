# PHASE 25 — POST-RELEASE READINESS SNAPSHOT FOR v0.1.0

*A read-only, evidence-only record of the already-published `v0.1.0` release. The
owner created and pushed the annotated tag after the pre-tag validation
(`research/60`–`research/63`); this step captures the **current post-tag
repository state** and distinguishes it explicitly from the **pre-tag evidence**
archived outside the repository. It changes **no source, test, CI, warning
policy, version declaration, tag or release behaviour**, and the agent performs
no commit, push or tag action.*

This snapshot is observational. It does **not** authorize, perform or reopen a
release, it does **not** claim that the pre-tag evidence proves the post-tag
state, and it deliberately adds no checker. Phase 17 remains **CLOSED**, E1
remains **HOLD**, and no novelty, effectiveness, security, benchmark or
publication claim is made.

## 1. Release identity

* Repository: `agent-security-labs`
* Release: **`v0.1.0`**
* Target version: **`0.1.0`**
* Previous release: `v0.0.1` (unchanged)
* Remote: `origin`
* Snapshot taken: **2026-10-02**

## 2. Release commit

The annotated tag resolves to release commit:

```text
3d731b0dffece499cc54a22d51701cdeecdce39f   "owner controlled signing of pre-tag jason report"
```

Both `git rev-parse v0.1.0^{commit}` and `git rev-parse v0.1.0^{}` return that
full commit id, and it equals the branch head (section 3).

## 3. Branch

```text
  main       03b53be [origin/main] release prepare
* v0.1.0-dev 3d731b0 [origin/v0.1.0-dev] owner controlled signing of pre-tag jason report
```

The snapshot was taken on `v0.1.0-dev`, which is **up to date with
`origin/v0.1.0-dev`**. At the moment of this snapshot the development branch and
the tagged release commit are the **same commit** (`3d731b0`). This is a snapshot
fact only: it is not a requirement, and the branch may legitimately diverge from
the tag as future development continues.

## 4. Local tag state

`git tag -n` lists exactly two tags:

```text
v0.0.1          Release v0.0.1
v0.1.0          Release v0.1.0
```

`v0.1.0` exists locally. No tag was created, modified, deleted or moved during
this step.

## 5. Remote tag state

```text
$ git ls-remote --tags origin v0.1.0
13464ba6eb9b678f2a8a6e2500d60fcc90c49fda    refs/tags/v0.1.0
```

```text
$ git ls-remote --refs origin refs/tags/v0.1.0
13464ba6eb9b678f2a8a6e2500d60fcc90c49fda    refs/tags/v0.1.0
```

The remote tag exists and its tag object (`13464ba…`) matches the local tag
object. The remote was not altered.

## 6. Annotation / peel verification

`git show v0.1.0 --no-patch`:

```text
tag v0.1.0
Tagger: Dr. Muhammad Nadeem Majeed <98729698+nadeem-majeedch@users.noreply.github.com>
Date:   Fri Oct 2 23:20:54 2026 +0500

Release v0.1.0

commit 3d731b0dffece499cc54a22d51701cdeecdce39f
```

The tag is **annotated** (a real tag object `13464ba…`, not a lightweight ref),
carries the message `Release v0.1.0`, and is **unsigned** (no `gpgsig`). Its
peeled commit, `3d731b0`, is exactly the intended release commit of section 2.

## 7. Version verification

```text
$ python scripts/check_version.py
  ok    pyproject.toml       project.version = '0.1.0' (authoritative)
  ok    agentsec.__version__ declares '0.1.0', matching pyproject.toml
  ok    CITATION.cff         declares '0.1.0', matching pyproject.toml
Result: 3/3 checks passed        (exit 0)
```

`CITATION.cff` also records `date-released: 2026-10-01`; the W6 metadata item
remains closed. Version declarations are unchanged at `0.1.0`.

## 8. Licensing verification

```text
$ python scripts/check_licensing.py
  ok    licence coverage       220 file(s) accounted for (mit 140, cc-by 78, excluded 2, unlicensed 0)
  ok    unlicensed files       none recorded; every file has a licence decision
Result: 9/9 checks passed        (exit 0)
```

Because the evidence report (`research/64` is the only new file) is covered by
the existing `research/**.md` → CC BY 4.0 glob, no `licensing/manifest.toml`
change was needed; the coverage count rises by one per added research record.

## 9. Test verification

```text
$ python -m pytest
1081 passed
```

The full suite passes on the clean post-tag tree.

## 10. Release-gate state

```text
$ python scripts/release_check.py --json
target_version 0.1.0
classification READY WITH WARNINGS
blockers       []
warnings       ['W12', 'W7']
```

The gate is unchanged: version `0.1.0`, classification **READY WITH WARNINGS**,
no blockers, and the accepted set exactly `{W7, W12}`. The warning set was **not**
altered to make the post-release state appear cleaner.

## 11. Warning-drift state

```text
$ python scripts/check_warning_drift.py
  policy         {W12, W7}
  documentation  {W12, W7}
  actual gate    {W12, W7}
Result: all three sets agree: {W12, W7}      (exit 0)
```

## 12. Manifest state

`python scripts/check_release_manifest.py` is a **pre-tag** guard: it asserts the
pre-release invariant that `v0.0.1` is present and `v0.1.0` is **absent**. On the
released tree it reports:

```text
PASS  release version: 0.1.0
PASS  warning set: manifest {W12, W7}; policy {W12, W7}; gate {W12, W7}
PASS  blockers: []
PASS  classification: READY WITH WARNINGS
PASS  W6 closed
PASS  release validation
PASS  CI structure: 5 jobs, one gate invocation
FAIL  tag state
      actual tags: ['v0.0.1', 'v0.1.0']
PASS  protected invariants
Result: FAIL — release manifest drift detected       (exit 1)
```

The **only** difference is the expected post-release tag state: `v0.1.0` now
exists, which the pre-tag guard treats as drift. This is a correct
pre-tag-versus-post-tag invariant difference, **not** a release defect, and
nothing was modified to silence it.

## 13. Archived pre-tag evidence location

The pre-tag report was moved out of the repository working tree (Phase 6A) to:

```text
../v0.1.0-pre-tag-report.json
```

* size: **6465 bytes**
* SHA-256: `639c7aa34066009d2302c14b9feff2fcce559b05003782de32f48ebca6268219`

It was moved byte-for-byte and was **not** copied back into the repository and
was **not** regenerated inside the tree.

## 14. Evidence verification result

```text
$ python scripts/pre_tag_check.py --verify-report ../v0.1.0-pre-tag-report.json
FAIL  report attestation could not be verified
  - repository state hash mismatch: the repository files changed
exit 1
```

This is **expected post-release behaviour and is not repaired here**. The
attestation binds the report to the exact repository inventory that produced it
(`sha256-canonical-git-inventory-v1`). The current tree legitimately differs — it
is the released state (tag present, this record added), and the report itself was
produced while the evidence file sat inside the tree. A pre-tag digest therefore
**cannot** be made to match the post-tag tree, and it must not be:

**PRE-TAG EVIDENCE** (the archived report) answers *"was this report and the
tree that produced it altered?"* for the **pre-tag** inventory only.
**POST-TAG CURRENT STATE** (this record's sections 2–12) is verified directly
against the repository and the published tag. The archived report does **not**
prove the post-tag state.

## 15. Working-tree state

```text
$ git status --short
(lines = 0)
```

The working tree is **clean** — no tracked modifications and no untracked files.

## 16. Artifact state

No generated artifacts remain in the repository. The previously stray
`v0.1.0-pre-tag-report.json` now lives outside the tree (section 13); git-ignored
caches (`.mypy_cache`, `.ruff_cache`, `.pytest_cache`) and any `site/`, `build/`,
`dist/`, `htmlcov/` output were removed. `research/64-post-release-readiness-snapshot.md`
is the only new (intentional, tracked-when-committed) file.

## 17. Protected-invariant confirmation

Unaffected by this step: `scripts/release_check.py` and its warning detection, the
B5 exact-warning set (`ACCEPTED_RELEASE_WARNINGS`), `.freebuff/project-id`,
`licensing/manifest.toml`, `schemas/**`, the lab runtime, `.github/workflows/docs.yml`
and the CI structure (five jobs, one `release_check.py` invocation, no
`continue-on-error`), the version declarations, and the existing release tags and
evidence. `W7` and `W12` remain accepted, `W6` remains CLOSED, `blockers` remain
`[]`, and the classification remains `READY WITH WARNINGS`.

## 18. Commit / push / tag actions

**None.** No commit, push, tag, release publication or history rewrite was
performed by the agent. `v0.0.1` and `v0.1.0` are unchanged.

## 19. Final post-release assessment

The published `v0.1.0` is **correctly placed and consistent**:

* the annotated tag `v0.1.0` (tag object `13464ba…`) is present **locally and
  remotely** and peels to the intended release commit `3d731b0`;
* the release branch `v0.1.0-dev` is at that same commit and in sync with its
  remote;
* version declarations, licensing and the full test suite are green;
* the release gate reports `READY WITH WARNINGS`, `blockers: []`, `{W7, W12}`,
  with warning drift agreed across policy, documentation and the gate.

The only non-green signals are the two **pre-tag** guards that assert `v0.1.0`
absent (`pre_tag_check.py` step 11 and `check_release_manifest.py` tag state) and
the pre-tag attestation failing against the changed post-tag tree. All three are
expected consequences of the release having been tagged, and none indicates a
release defect.

## 20. Limitations

* This is a **snapshot**, not a continuous guarantee. The branch/tag equality in
  section 3 is true only at the instant of this record.
* The pre-tag attestation is **keyless integrity**, not provenance; the archived
  report is also stored **outside** version control, so its presence and
  freshness depend on the owner's local archive, not on the repository.
* Nothing here verifies the remote tag beyond the `git ls-remote` observed in
  section 5; there is no server-side or transparency-log proof.
* The two pre-tag guards cannot be used post-tag; there is deliberately **no**
  `post_release_check.py` — existing read-only controls were judged sufficient
  for the verified scope.
* No claim is made about build reproducibility, distribution, or publication.

## 21. Exact files changed

Added:

```text
research/64-post-release-readiness-snapshot.md   (this record, CC BY 4.0)
```

Modified:

```text
(none)
```

No test file was added: the repository convention guards the owner-facing lab
pages, not individual `research/*.md` records, so no documentation guard was
required and no new test infrastructure was created.

## 22. Tag / Git status

* `v0.0.1` — unchanged.
* `v0.1.0` — **created and pushed by the owner**; present locally and on `origin`.
* No commit, push or tag was performed by the agent.
