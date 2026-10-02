# Accepted Release Warnings (v0.1.0)

`scripts/release_check.py` reports a set of *known, non-blocking* warnings next to
the release gates. This page records which of those warnings are **deliberately
accepted** for the v0.1.0 release, and why, so that a **READY WITH WARNINGS**
gate is a documented decision rather than a surprise. It is an operational
reference, not the full audit — the reasoning lives in
`research/50-phase5-release-decision-audit.md` and
`research/51-v0.1.0-release-preparation.md` (repository files, kept out of this
site's navigation).

## Release context

- **Version:** `0.1.0` (declared in `pyproject.toml`, `src/agentsec/__init__.py`
  and `CITATION.cff`; `scripts/check_version.py` reports 3/3).
- **Release date:** 2026-10-01.
- **Gate state:** `READY WITH WARNINGS` — `blockers: []`, and the only
  non-`PASS` gate is `git_state` while the working tree is uncommitted.

## The accepted set is exactly `{W7, W12}`

For v0.1.0 the accepted warning set is **exactly two**: `W7` and `W12`. Nothing
else is accepted, and neither of these is silently ignored — each is a decision
recorded below.

## W7 — `.freebuff/project-id` is tracked

- **What it means.** `.freebuff/project-id` is a small local-tooling metadata
  file that is committed to the repository, so it is present in a clone. The
  gate flags tracked local metadata as *distributed* content.
- **Why it remains.** The file is intentionally kept **tracked** for this
  release. It was not `git rm --cached`, not added to `.gitignore`, and its
  `licensing/manifest.toml` entry is unchanged (recorded as `excluded`, governed
  by neither grant).
- **Why it is accepted.** The tracking is a deliberate, low-risk choice, and the
  licensing manifest already accounts for the file explicitly, so the coverage
  check still passes. The W7 detection condition is intentional and unchanged.

## W12 — human-judgement licensing residuals remain

- **What it means.** W12 is emitted whenever the project still carries
  human-judgement licensing residuals; it points at the
  `research/28`–`research/36` review history.
- **Why it remains.** The existing `release_check.py` behaviour is intentionally
  left unchanged for this release. W12 is appended unconditionally, so the gate
  keeps reporting it.
- **Why it is accepted.** It is a *re-stated* acceptance, not a retirement: the
  residual is documented here, in `docs/development.md`, and in the exact-warning
  policy in `tests/test_release_check.py`, and is knowingly carried into v0.1.0.

## W6 — CLOSED

W6 (`CITATION.cff` has no `date-released`) is **closed**, not accepted.
`CITATION.cff` now carries:

```yaml
date-released: 2026-10-01
```

So the W6 condition is false and W6 no longer appears in the gate. It must not be
documented or treated as an active warning.

## How the policy is enforced

The accepted set is pinned by an **exact set equality** regression test
(`ACCEPTED_RELEASE_WARNINGS` in `tests/test_release_check.py`), which runs against
the real repository. A new warning — or a warning that unexpectedly disappears —
**fails the test** rather than being silently accepted. So accepting a future
warning is an explicit policy change, not an accident.

## Executable drift check

`scripts/check_warning_drift.py` is a small, **read-only** consistency check that
verifies the three surfaces which record the accepted set still agree:

- the **policy** — `ACCEPTED_RELEASE_WARNINGS` in `tests/test_release_check.py`;
- the **documentation** — the `{W7, W12}` statement on this page;
- the **actual gate** — the `warnings` field of `scripts/release_check.py --json`.

Run it with:

```
python scripts/check_warning_drift.py
python scripts/check_warning_drift.py --gate-report <release_check-report.json>
```

Without `--gate-report` the checker obtains the actual set by running the release
gate itself. With `--gate-report` it reads an already-generated
`release_check.py --json` report instead, so a caller that has just run the gate
can reuse its output rather than running it a second time.

It exits `0` only when all three sets are **exactly equal**; otherwise it exits
`1` and prints all three sets plus the disagreement — a warning accepted by
policy but missing from the docs, documented but missing from policy, emitted by
the gate but not accepted, disappeared from the gate, or the docs and gate
otherwise disagreeing. A non-zero exit means the three surfaces must be
**reconciled deliberately**, not that the gate should be forced clean.

The check **complements** the exact-set regression test rather than replacing
it. The test pins the policy in CI; this script adds the three-way view on every
CI run and on demand (for example, before a release), running the gate read-only
and never retiring, adding or suppressing a warning. It changes no file, no
release classification and no Git state.

The drift check is part of **release validation**. The CI `release-readiness`
job runs `scripts/release_check.py --json` **once** and captures its report to a
temporary file outside the checkout; the final step then runs
`python scripts/check_warning_drift.py --gate-report <that report>` (with no way
to swallow its exit code). The gate therefore executes exactly once, and release
validation still cannot pass while the policy, this documentation and the actual
gate disagree. A **successful** release validation requires all three surfaces to
report the same accepted set. If the check fails, **investigate the
disagreement**: reconcile the surfaces deliberately, or record a retirement as
described below. Do not change the accepted set merely to make the check green,
and do not weaken the policy or suppress the gate.

## Executable Owner Pre-Tag Validation

`scripts/pre_tag_check.py` turns the owner pre-tag checklist below into one
executable, **read-only** sequence:

```
python scripts/pre_tag_check.py
python scripts/pre_tag_check.py --summary
```

It runs the established release checks in order — version, licensing, the test
suite, the labs check, Ruff, mypy, the strict MkDocs build, the release gate, the
warning drift check, the release-manifest drift check and the Git/tag invariant —
and prints one section per check followed by an unambiguous final status
(`RESULT: READY FOR OWNER REVIEW` or `RESULT: NOT READY`). It **orchestrates**
the existing checks; it does not replace or re-implement any of them.

It captures the release gate (`scripts/release_check.py --json`) **once**, writes
its report to a temporary file **outside the repository**, and reuses that report
in both `check_warning_drift.py --gate-report` and
`check_release_manifest.py --gate-report`, so the gate is never run twice. The
temporary report is removed afterwards.

It is read-only: it does not commit, push, tag or publish, and it never edits a
file, the version, the accepted set, the release gate or the CI. It does **not**
require a clean working tree — the tree is intentionally dirty while the release
awaits owner review — and a dirty tree is not a failure unless the release gate
itself reports a blocker. It exits `0` only when every required check succeeds
and reports **all** failures otherwise; it never repairs a failure automatically.
`READY WITH WARNINGS` with `blockers: []` and the warning set exactly
`{W7, W12}` is the expected, successful result, not a failure.

> A successful validation means the repository is ready for owner review. It
> does not authorize or perform the release.

## Machine-Readable Pre-Tag Report

`scripts/pre_tag_check.py` also offers a **machine-readable** mode so the exact
pre-tag evidence can be archived without copying terminal output by hand:

```
python scripts/pre_tag_check.py --json
```

The command and its checks are **identical** to the human-readable default — the
only difference is the output format. With `--json` the tool prints a single
**deterministic JSON object** to standard output and nothing else, so stdout
stays machine-parseable. The default (no flag) remains the human-readable
sectioned report described above; `--json` and `--summary` are mutually
exclusive.

The object records, in a stable order and shape: a `schema_version`; the overall
`result` (`READY FOR OWNER REVIEW` or `NOT READY`) and `success` flag; the
`target_version`; the release gate's `classification`, `blockers` and the exact
`warnings` set (normalised to numeric order, so `{W7, W12}` rather than the gate's
raw order); the twelve individual `checks` in execution order with their
`name`, `status` and printed `details`; and the `check_count`, `passed_count` and
`failed_count`. It carries no timestamps, no absolute or machine-specific paths
and no environment-dependent noise, so two runs over the same repository state
produce the same bytes.

Exit semantics are unchanged: the process exits `0` only when every required
check succeeds and `1` otherwise, so `--json` uses the **same exit code** as the
normal command. `READY WITH WARNINGS` with `blockers: []` and the warning set
exactly `{W7, W12}` is the successful, expected result. The JSON mode is still
fully read-only, runs the release gate exactly once, reuses the captured report
in both drift checks and removes the temporary report afterwards. It performs
**no release action** — no commit, push, tag or publication — and the captured
report is suitable as **archival owner-review evidence** for the release record.

## Tamper-Evident Pre-Tag Evidence

The JSON report carries a **SHA-256 attestation** that binds it to the exact
repository state that produced it, so an archived report can be checked against
the tree later. It is **integrity evidence, not a digital signature**: it detects
modification, but it does not prove who generated the report.

The attestation records:

- **`repository_state_sha256`** — a SHA-256 digest over the repository's
tracked and untracked-but-not-ignored files (the `git ls-files` working-tree
inventory, the same content set the licensing check accounts for). Each file
contributes its relative path, a NUL separator and its bytes, in lexicographic
path order; `.git` metadata, ignored/generated content and build output are
excluded, and there are no timestamps or machine-specific paths.
- **`report_payload_sha256`** — a SHA-256 digest of the canonical JSON of the
report **without** its attestation object, so the hash is not self-referential.

Generate the attested report, archive it **outside the repository**, and verify
it later with:

```
python scripts/pre_tag_check.py --json > ../release-evidence.json
python scripts/pre_tag_check.py --verify-report ../release-evidence.json
```

Archive the report **outside the working tree**: any file added inside the
repository becomes part of the repository-state inventory and would change the
recorded digest, so a report saved into the tree would no longer verify against
it.

`--verify-report` is **read-only** and runs **no check**: it re-reads the report,
recomputes both digests and exits `0` only when the report still matches the
current tree. It reports every mismatch — an edited report field, a changed
warning set or target version, a changed check status, and an added, changed or
deleted repository file — and it does **not** rerun the release gate or the test
suite. The command performs no release action.

Limitations: the attestation uses no key material and no external service. It
does not establish authorship or trusted provenance, and it is not a substitute
for a cryptographic signature. Possession of a valid report does not prove who
generated it, and a party who can rewrite both the tree and the report can
produce a self-consistent attestation.

## Owner-Controlled Report Signing

The SHA-256 attestation above provides **integrity** — it answers *"was this
report or tree altered?"* — but it is keyless, so it cannot answer *"who
produced this report?"*. An **optional** owner signature adds that **provenance**
without replacing or weakening the attestation. It answers a narrow, honest
question: *"was this exact report signed by the holder of the corresponding
private key?"* It proves **possession and control of a key**, not personal
identity.

Signing is **optional**. The normal commands need no key and behave exactly as
before:

```
python scripts/pre_tag_check.py
python scripts/pre_tag_check.py --json
python scripts/pre_tag_check.py --verify-report report.json
```

Signing uses the local **OpenSSL 3.x** tool and the modern **Ed25519** signature
scheme (deterministic signatures, small keys). No cryptographic dependency is
added to the project, no shell string is executed, and no cryptographic
mathematics is implemented here. `scripts/pre_tag_check.py` detects OpenSSL and
reports a clear error if it is unavailable.

The tool signs the canonical report payload — the same bytes
`report_payload_sha256` covers, with the `attestation` and `signature` envelopes
excluded — so the signing input is deterministic and the signature does not
perturb the report's own evidence:

```
python scripts/pre_tag_check.py --sign-report report.json --private-key <private.pem> --output report.signed.json
```

The command **verifies the report's SHA-256 attestation first** and refuses to
sign a report whose attestation is already invalid. It writes a `signature`
object — `algorithm`, `encoding` (`base64`), `key_id_method`, `key_id` (a
`sha256-spki-der` public-key fingerprint) and the base64 `signature` — to the
explicit output file. With no `--output` it writes a **new** file
(`report.signed.json`); the input is overwritten **only** when the same path is
supplied explicitly. The private key never appears in the report, in standard
output or in standard error.

Verify a signature by supplying the public key:

```
python scripts/pre_tag_check.py --verify-report report.signed.json --public-key <public.pem>
```

The two evidence layers are reported distinctly: an **unsigned** report still
verifies for its integrity; a **signed** report without `--public-key` is
reported as **signature present but not verified** (not silently accepted); a
**correct** key verifies the signature; a **wrong** key, a modified report, a
modified signature, a malformed signature or an unsupported algorithm fails with
exit `1`. Verification runs **no** check and **no** release gate.

Only the **public key** and the `key_id` fingerprint belong in archived
verification material. The **private key stays under owner control** and must
never be committed, archived in the repository, or shared as evidence. Signing
**does not** authorize a release, create or push a Git tag, or modify the release
gate; it is provenance for a report the owner has already reviewed.

### Minimal signing workflow

1. **Generate the report** — `python scripts/pre_tag_check.py --json > ../release-evidence.json`.
2. **Review the report** — confirm the result, classification, blockers and warning set.
3. **Verify the SHA-256 attestation** — `python scripts/pre_tag_check.py --verify-report ../release-evidence.json`.
4. **Sign the reviewed report** — `--sign-report` with the owner's private key, writing a new file.
5. **Archive the report and the public key/fingerprint** — outside the working tree; keep the private key private.
6. **Verify the signature when needed** — `--verify-report <signed report> --public-key <public.pem>`.
7. **Only then perform the owner's normal release process** — commit, push, tag and publish remain owner actions.

Signing is **not** a release action and **not** a prerequisite for release
validation. It is an optional provenance record layered on top of the existing
integrity evidence.

## How to Retire an Accepted Warning

An accepted warning is a **knowing, reviewed decision**, so retiring one is a
controlled procedure — never a shortcut to a cleaner gate. The underlying warning
condition must be genuinely *resolved* first; the exact-set test then **forces**
the policy update. Retiring a warning is **not** the same as deleting it from the
accepted set: you resolve the condition, watch the warning disappear on its own,
and update the recorded policy to match.

The order below is deliberate — do the small steps first and the release steps
last.

1. **Identify the warning and its detection condition.** Name the warning ID and
   the precise condition in `scripts/release_check.py` that produces it (W7:
   `.freebuff/project-id` is in `git ls-files`; W6: `CITATION.cff` has no
   `^date-released:`; W12: always appended).
2. **Establish that the condition is genuinely resolved.** Confirm the reason is
   real — not a wish for a cleaner gate — and that resolving it does not
   regress something else.
3. **Make the smallest implementation or configuration change required.** Only
   the minimum change that makes the detection condition false; nothing
   unrelated.
4. **Update the B5 exact-warning policy deliberately.** Edit
   `ACCEPTED_RELEASE_WARNINGS` in `tests/test_release_check.py` to the new set,
   and revise its policy comment. This is the deliberate, reviewed step that
   records the retirement.
5. **Update the documentation and research record.** Update this page (move the
   warning from accepted to closed) and write a new research record for the
   transition.
6. **Run `release_check.py --json` and verify the warning disappears** — and
   only that warning.
7. **Verify no unexpected warning appears.** The set should lose the retired ID
   and gain nothing; an unexpected arrival is a separate investigation.
8. **Verify `blockers` remain empty.** Retiring a warning must not trade one
   warning for a blocker.
9. **Run the complete validation suite** (pytest, labs check, Ruff, mypy, MkDocs
   strict, licensing, version, `release_check.py --json`, `git diff --check`).
10. **Record the transition in a new research audit** — the warning, its
    condition, the change, the before/after set, and the validation evidence.
11. **Only then consider the next release or tag.** Retiring a warning is not a
    release action; the tag remains a separate, owner-driven step.

### Current examples

- **W7 (accepted — kept).** W7 is currently accepted because
  `.freebuff/project-id` remains **tracked**. Retiring it would require an
  intentional decision to stop tracking and distributing that file (e.g.
  `git rm --cached` plus a `.gitignore`/manifest decision). That decision is out
  of scope here — **do not make that change now.**
- **W12 (accepted / re-stated — kept).** W12 is currently accepted and
  re-stated. Retiring it would require an intentional change to the release-check
  behaviour in `scripts/release_check.py` (it is appended unconditionally). That
  change is out of scope here — **do not modify `scripts/release_check.py` now.**
- **W6 (closed — already retired).** W6 is the worked example of a warning that
  disappeared **naturally** after its underlying condition was resolved:
  `CITATION.cff` gained `date-released: 2026-10-01`, the W6 condition became
  false, the warning vanished from the gate, and the policy was updated to match.
  That is the shape every retirement should take — condition first, then policy.

### Do not retire warnings by

Retirement means the *condition* is gone. It is **not** any of the following:

- **Weakening or removing the exact-set assertion** in
  `tests/test_release_check.py` (e.g. `issubset`, or deleting the test).
- **Broadening the accepted set** to absorb a warning that was not actually
  resolved (adding the ID rather than fixing the condition).
- **Changing the release classification** just to obtain `READY` instead of
  `READY WITH WARNINGS`.
- **Suppressing warning output** in `scripts/release_check.py` (filtering,
  silencing, or dropping a warning from the report).
- **Modifying unrelated release gates** to mask the residual.

## The gate stays `READY WITH WARNINGS`

The release is not forced to `READY`. With W7 and W12 knowingly accepted, the
correct and honest gate state for v0.1.0 is **READY WITH WARNINGS**: no blockers,
and the accepted residuals visible rather than hidden.

## Owner pre-tag checklist for v0.1.0

This is the **owner-facing** sequence to run before creating the `v0.1.0` tag.
Run every command from the repository root and confirm the stated result — run
the commands **and check their output**, do not assume success. `READY WITH
WARNINGS` is the **expected** classification for this release whenever the
accepted set is exactly `{W7, W12}` and `blockers` are empty; it is not a
failure. The checklist ends with an **owner decision**: the agent must not
commit, push, create the `v0.1.0` tag, or publish a release.

### 1. Working-tree review

- `git status` — inspect the tracked and untracked changes.
- Inspect the **complete diff** (`git diff` and `git diff --staged`) of the
  release commit.
- Confirm every changed and new file is **intentional** and belongs to this
  release.
- Confirm **no generated artifacts** are present (no `build/`, `dist/`,
  `.coverage`, `site/`, caches or temporary reports).

### 2. Version

```
python scripts/check_version.py
```

Confirm all three declarations report `0.1.0` and the check is **3/3**
(`pyproject.toml`, `src/agentsec/__init__.py`, `CITATION.cff`). No unintended
version string should remain.

### 3. Tests and quality gates

Run each and **verify a successful result** (not merely that it ran):

```
python -m pytest
python -m agentsec labs check
ruff check src tests scripts
python -m mypy
python -m mkdocs build --strict
python scripts/check_licensing.py
```

Expected: the full suite passes; `8/8 labs passed`; Ruff reports no findings;
mypy reports no issues; the strict MkDocs build exits `0`; licensing is `9/9`
with zero unaccounted files.

### 4. Release gate

```
python scripts/release_check.py --json
```

Verify the structured report:

- `target_version` is `0.1.0`
- `blockers` is `[]`
- `classification` is `READY WITH WARNINGS`
- `warnings` is **exactly** `{W7, W12}`

Do **not** force the gate to `READY`; `READY WITH WARNINGS` is the honest,
documented state for this release.

### 5. Warning drift

```
python scripts/check_warning_drift.py
```

Confirm it exits `0`. This proves the three surfaces agree: the **B5 policy**
(`ACCEPTED_RELEASE_WARNINGS`), the **canonical documentation** (this page), and
the **actual release-gate warning set**. In CI the same check runs against the
gate's captured report (`--gate-report`), so the gate is executed once.

### 6. Release metadata

Verify the already-established metadata:

- `CITATION.cff` declares `version: "0.1.0"` and `date-released: 2026-10-01`.
- `README.md` release/version information is consistent with `0.1.0`.
- `docs/development.md` records the `0.1.0` release status.
- This page is present in the MkDocs navigation.

Do not invent additional release-metadata requirements.

### 7. Warning decisions

Confirm the decisions explicitly:

- **W6 is closed** — it must **not** appear in the current warning set.
- **W7 is intentionally accepted** for this release (`.freebuff/project-id`
  stays tracked).
- **W12 is intentionally accepted / re-stated** for this release.
- **No new warning may simply be added** to the accepted set to make the gate
  green.

To change any of these, follow **"How to Retire an Accepted Warning"** above
rather than editing the accepted set directly.

### 8. Protected invariants

Verify:

- `scripts/release_check.py` was **not changed** as part of release preparation.
- `.freebuff/project-id` remains **intentionally tracked** (W7 is a decision, not
  an accident).
- `licensing/manifest.toml` remains correct (coverage `9/9`, zero unaccounted).
- `.github/workflows/docs.yml` is unchanged.
- `schemas/**` and the lab runtime are unchanged unless already documented.
- **No accidental build artifacts** remain in the tree.

### 9. Git history and tag

Before tagging, inspect:

```
git diff --check
git status
git log --oneline --decorate -n 20
git tag
```

Confirm:

- `v0.0.1` is **unchanged**;
- **no `v0.1.0` tag exists yet**;
- the intended release commit contains the reviewed changes;
- there are no unintended commits or files.

Do **not** create the tag automatically.

### 10. Human release decision

The checklist ends with an **owner decision**. The agent must **not** commit,
push, create the `v0.1.0` tag, or publish a release, and must not alter W7/W12,
change the release classification, or modify `scripts/release_check.py`. The
owner reviews the evidence above and decides whether the tree is ready to
commit, push, tag and (optionally) publish.

### Checklist result template

```text
v0.1.0 PRE-TAG REVIEW

Version:                 PASS / FAIL
Tests:                   PASS / FAIL
Labs:                    PASS / FAIL
Ruff:                    PASS / FAIL
Mypy:                    PASS / FAIL
MkDocs:                  PASS / FAIL
Licensing:               PASS / FAIL
Release gate:            PASS / FAIL
Warning drift:           PASS / FAIL
Warnings:                {W7, W12}
Blockers:                []
Git diff check:          PASS / FAIL
v0.0.1 integrity:        PASS / FAIL
Working tree reviewed:   YES / NO
Owner approval:          YES / NO

v0.1.0 tag created:      YES / NO
```

`READY WITH WARNINGS` with `blockers: []` and the warning set exactly
`{W7, W12}` is the **expected** result; it is not a failure.
