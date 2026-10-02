# PHASE 23 — TAMPER-EVIDENT PRE-TAG EVIDENCE

*A SHA-256 integrity attestation for the machine-readable pre-tag report
(`research/61`), following the machine-readable pre-tag report: the same
read-only sequence, now bound to the exact repository state that produced it,
with a read-only `--verify-report` mode to re-check an archived report. It
changes **no runtime, CI, warning-detection, warning-policy, version or
release-gate behaviour**, preserves every existing JSON field and the
human-readable default, and does not add a CI job. Nothing was committed, pushed
or tagged; the `v0.0.1` tag is unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release was prepared and green (validated at the end of
`research/61`): version `0.1.0` (3/3); gate **READY WITH WARNINGS**,
`blockers: []`, accepted set exactly `{W7, W12}`, `W6` closed; warning-drift and
manifest-drift exit `0`; `python scripts/pre_tag_check.py --json` exit `0` with
`success: true`, 12/12 checks; suite **1034 passed**. The JSON report was
deterministic and machine-parseable, but nothing bound it to the tree that
produced it: an archived report could not be distinguished from one generated
against a different (or later-modified) tree.

## 2. Motivation

The owner archives the JSON report as pre-tag evidence. Without a binding to the
tree, "this report says the tree was ready" is an unverifiable claim: the report
could be edited, or paired with an unrelated checkout. A deterministic SHA-256
attestation makes the evidence *self-checking* against the repository content it
describes, using only the standard library and no external service.

## 3. Threat model — what the digest does and does not protect

The attestation answers one question: **"what exact repository state produced
this validation report?"** It detects:

- a report whose fields, warning set, target version or check statuses were
  edited after generation (the report-payload digest changes);
- a report paired with a repository whose content changed (a file added,
  removed or edited — the repository-state digest changes);
- a report whose attestation values were altered (they no longer match the
  recomputed digests);
- a malformed or unsupported attestation.

It does **not** provide:

- **authorship or provenance.** Possessing a valid report does not prove *who*
  generated it. There is no secret, no key and no signature, so anyone who can
  read the repository can produce a matching attestation.
- **protection against an attacker who controls both the report and the
  checkout.** If an attacker can rewrite the tree *and* regenerate the report,
  the recomputed digests agree. The attestation is integrity evidence for
  archiving, not an authenticity guarantee.
- **a Git commit/tag binding.** It binds to working-tree content, not to a
  commit object or a signature over one.

This is stated plainly wherever the feature is documented: SHA-256 integrity
evidence is **not** equivalent to a cryptographic signature or trusted
provenance.

## 4. Canonical repository-state definition

`repository_state_files(root)` reuses Git's authoritative working-tree
inventory:

```
git -C <root> ls-files --cached --others --exclude-standard -z
```

That is every tracked file plus every untracked-but-not-ignored file — the same
content set the licensing check accounts for (218 files at this step). `.git`
metadata and ignored/generated content (`.mypy_cache`, `.pytest_cache`,
`.ruff_cache`, `__pycache__`, `runs/`, `site/`, `build/`, `dist/`,
`*.egg-info`, `.env`, `*.local`) are therefore excluded **by construction**,
because `.gitignore` excludes them and the manifest keeps its `not-distributed`
patterns in step with `.gitignore`. No bespoke exclusion list was invented.

The digest is:

```
sha256( for each file in lexicographic relative-path order:
            utf8(relative_path) || 0x00 || file_bytes )
```

- relative POSIX paths, never absolute;
- global lexicographic order (the raw `git ls-files` output is re-sorted);
- bytes, not text, so encodings and binary files are handled uniformly;
- a tracked-but-deleted file contributes **no** bytes (it still changes the
  digest, so deletion is detected rather than silently normalised away).

## 5. Report-payload hashing method

The report digest is computed **before** the attestation is added:

```
report_payload_sha256 = sha256( canonical_json(report without "attestation") )
```

`canonical_json` is `json.dumps(payload, sort_keys=True,
separators=(",", ":"), ensure_ascii=True)` encoded as UTF-8: sorted keys (no
dependence on dict insertion order), no insignificant whitespace, and ASCII
escapes so the bytes are identical across platforms. Excluding the
`attestation` key avoids a self-referential hash.

## 6. CLI behaviour

```
python scripts/pre_tag_check.py --json
python scripts/pre_tag_check.py --verify-report <report.json>
```

`--json` now emits the existing fields **plus** a top-level `attestation`
object appended last:

```json
"attestation": {
  "algorithm": "SHA-256",
  "method": "sha256-canonical-git-inventory-v1",
  "repository_state_sha256": "<64 lowercase hex>",
  "report_payload_sha256": "<64 lowercase hex>"
}
```

All prior fields are unchanged (`schema_version`, `result`, `success`,
`target_version`, `classification`, `blockers`, `warnings`, `checks`,
`check_count`, `passed_count`, `failed_count`). stdout stays JSON-only; the
report is deterministic; the exit code is unchanged. `--summary`, `--json` and
`--verify-report` are mutually exclusive (argparse group). If the repository
state cannot be enumerated, `--json` prints an error to stderr and exits `1`
rather than emitting an unattested report.

## 7. Verification behaviour

`--verify-report` is a **read-only** verification path that runs **no** check:

- it reads the supplied JSON (malformed JSON → clear failure);
- it requires a well-formed `attestation` object with the supported algorithm
  and method and two 64-hex digests (unsupported algorithm/method and malformed
  digests are each reported);
- it recomputes `report_payload_sha256` and compares — any modified report field
  (result, success, warnings, target version, check status, …) is detected;
- it recomputes `repository_state_sha256` and compares — any added, changed or
  deleted relevant repository file is detected;
- it reports **every** problem, prints `FAIL` and exits `1`; it exits `0` only
  when the report is valid for the current tree;
- it does **not** run the release gate, the suite or the drift checks, creates
  no temporary file, and modifies nothing.

A tampered report is never repaired or normalised — it is reported and rejected.

## 8. Tests

`tests/test_pre_tag_check.py` gained **20 tests** (one parametrized over four
mutations) reusing the existing fixture infrastructure (`FakeRunner`,
`make_repo`, `_gate_invocations`). `FakeRunner` was extended to answer
`git ls-files -z` from the fixture's working tree, so repository-state hashing
responds to real added, changed and deleted files.

Generation: the attestation is present with algorithm `SHA-256` and two 64-hex
digests; the method is recorded; repeated generation on an unchanged tree yields
identical reports (all fields and both digests); the attestation contains no
timestamps, absolute paths or temp-prefix noise; the expected 12/12 state is
preserved; the gate still runs exactly once.

Verification: a valid report exits `0`; a modified result/`success`, warning set,
target version or check status fails with a payload mismatch; a modified report
hash fails; a changed, added or deleted repository file fails with a repository
mismatch; a missing or malformed attestation and an unsupported algorithm or
method fail; `--verify-report` invokes neither the release gate nor the suite and
passes no `--gate-report`; verification leaves the repository file set unchanged.

No test runs the real suite or the real gate.

## 9. Validation

| Command | Result |
| --- | --- |
| `python -m pytest` | **1054 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 (built outside the repository) |
| `python scripts/check_licensing.py` | **9/9** — 219 files accounted for |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_release_manifest.py` | exit **0** — manifest and repository state agree |
| `python scripts/pre_tag_check.py` | exit **0** — `RESULT: READY FOR OWNER REVIEW` (12/12) |
| `python scripts/pre_tag_check.py --json` | exit **0** — valid JSON with a SHA-256 attestation |
| `python scripts/pre_tag_check.py --verify-report <report>` | exit **0** — valid for the current tree |
| `git diff --check` | clean |

**Test delta: 1034 → 1054 (+20).** No existing test was modified or weakened;
`FakeRunner` was extended, not replaced.

Determinism and tamper detection were also checked directly against the real
repository: two `--json` runs produce identical `repository_state_sha256`,
`report_payload_sha256` and report fields; an edited report is rejected; a report
verified against a deliberately changed tree is rejected; verification runs no
gate; and no temporary or generated artifacts remain.

## 10. Protected invariants

`scripts/release_check.py` (and its warning detection), the B5 exact-warning
assertion (`ACCEPTED_RELEASE_WARNINGS`), `.freebuff/project-id`,
`licensing/manifest.toml`, `schemas/**`, the lab runtime,
`.github/workflows/docs.yml` and the warning classification logic were **not
modified**. CI keeps its five-job structure and its single `release_check.py`
invocation; no `continue-on-error` was added. The accepted set stays exactly
`{W7, W12}`, `W6` remains CLOSED, `blockers` stay `[]`, the classification stays
`READY WITH WARNINGS`, and the 12-check sequence is unchanged. The default
human-readable output is unchanged.

## 11. Limitations

The digest is integrity evidence only. It is not a digital signature, carries no
key material, and does not establish who generated the report or that an external
authority authenticated the release. It binds to working-tree content, not to a
Git commit or tag. A party able to rewrite both the tree and the report can
produce a self-consistent attestation; the feature raises the cost of accidental
drift and casual tampering, not of a determined adversary with write access.

## 12. Tag / Git status

* `v0.0.1` — unchanged; `git tag` lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* No commit, push or tag was performed.

## 13. Deferred work

Deliberately **not** done in this step, per scope: no external signing or key
management, no transparency log, and no append-only evidence log. Those would
introduce key custody and trust questions that a SHA-256 integrity attestation
does not answer. Possible future work (owner decision): signing the report with a
key the owner controls, or recording reports in an append-only log — both are
explicitly out of scope here. The remaining action is the **owner's**: review the
tree and the attested report, then commit, push, tag and (optionally) publish
manually. The agent does not commit, push, tag or publish. Phase 17 remains
**CLOSED**, E1 remains **HOLD**, and no novelty, effectiveness, security,
benchmark or publication claim is made.
