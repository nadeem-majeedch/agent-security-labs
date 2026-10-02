# PHASE 24 — OWNER-CONTROLLED SIGNING OF THE PRE-TAG JSON REPORT

*An optional, owner-controlled Ed25519 signature for the machine-readable
pre-tag report (`research/61`) and its SHA-256 attestation (`research/62`),
following the tamper-evident pre-tag evidence: the same read-only sequence and
the same integrity attestation, now extensible with a signature that answers a
**different** question — *who* signed the report — while keeping a key optional
for normal validation. It changes **no runtime, CI, warning-detection,
warning-policy, version or release-gate behaviour**, preserves every existing
JSON field and the human-readable default, and does not add a CI job or a
dependency. Nothing was committed, pushed or tagged; the `v0.0.1` tag is
unchanged and no `v0.1.0` tag was created.*

## 1. Baseline

Entering this step the release was prepared and green (validated at the end of
`research/62`): version `0.1.0` (3/3); gate **READY WITH WARNINGS**,
`blockers: []`, accepted set exactly `{W7, W12}`, `W6` closed; warning-drift and
manifest-drift exit `0`; `python scripts/pre_tag_check.py --json` exit `0` with
`success: true`, 12/12 checks and a SHA-256 attestation; `--verify-report` exit
`0`; suite **1054 passed**. The report was deterministic, machine-parseable and
bound to the exact repository state that produced it — but the attestation is
keyless, so an archived report could not be tied to the owner who produced it.

## 2. The provenance problem

The attestation answers *"was this report or tree altered?"*. It cannot answer
*"who produced this report?"*, because anyone with read access to the repository
can recompute a matching attestation. That is correct for an integrity check and
wrong for provenance. The two questions must not be conflated:

- **SHA-256 attestation (integrity):** *"was this exact report/tree altered?"* —
  keyless, no trusted party, detects modification.
- **Digital signature (provenance):** *"was this exact report signed by the
  holder of the corresponding private key?"* — requires a key the owner
  controls.

The goal is to add the second **optionally**, without weakening or replacing the
first, without requiring a key for ordinary validation or CI, and without
introducing an external service or a cryptographic dependency.

## 3. Selected mechanism and why

**Ed25519 signatures performed by the local OpenSSL 3.x tool.**

- **No suitable standard-library primitive.** CPython 3.13 offers `hashlib`,
  `hmac` and `ssl`, but no asymmetric signature API. Implementing one is out of
  the question (and forbidden here): no hand-rolled RSA/ECDSA/EdDSA, no invented
  padding, no invented key formats, no MD5/SHA-1, no shared secret masquerading
  as asymmetric signing.
- **No new dependency.** `cryptography`/`nacl` are present in *some* local
  environments but are **not** declared dependencies of this project, and adding
  one merely for an optional release-time feature is not justified. OpenSSL 3.x
  is a standard, already-installed system tool (present on the local machine and
  on GitHub Actions runners), so the feature shells out to it.
- **Ed25519** is a modern, well-established signature scheme with **small keys
  and deterministic signatures**, which also makes the signed artefact
  reproducible for the same input and key.
- **Argument arrays, never a shell.** Every invocation uses
  `subprocess`-style argument tuples with `shell=False`; no shell string is ever
  built, and no key material is echoed.

The cryptography is delegated; the project only defines the signing *input*, the
envelope format and the verification semantics. The integration is an injectable
`signer` object, so tests substitute a deterministic fake and never require
OpenSSL or generate keys that could escape the temporary directory.

## 4. Exact canonical signing input

The signing input is **the canonical report payload already used for
`report_payload_sha256`** — no terminal output, no arbitrary temporary bytes and
never the repository itself:

```
signing_input = canonical_json(report without "attestation" and without "signature")
             = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True).encode("utf-8")
```

where `payload` is the report with its two *envelopes* removed:

- `attestation` — excluded so the hash is not self-referential;
- `signature` — excluded so attaching a signature does **not** change the
  payload it signs, and so the attestation's `report_payload_sha256` remains
  valid **after** signing.

Excluding `signature` is a no-op for every existing unsigned report (the key is
absent), so `report_payload_sha256` and the signing input are byte-identical
before and after a signature is attached. The bytes are deterministic: sorted
keys, no insignificant whitespace, ASCII escapes, UTF-8.

## 5. Key identification

The report names the signing key by a **deterministic public-key fingerprint**,
never by a path, username, hostname, environment variable or account id:

- `key_id` = **lowercase SHA-256 of the DER-encoded SubjectPublicKeyInfo**
  (`openssl pkey … -pubout -outform DER`), recorded as
  `key_id_method = "sha256-spki-der"`.
- It is derived only from the key, so it is portable: the same key produces the
  same `key_id` on any machine, and the report remains meaningful after being
  archived elsewhere.
- At signing time the fingerprint is derived from the private key's public part;
  at verification time it is derived from the supplied public key.

## 6. Signature object

```json
"signature": {
  "algorithm": "Ed25519",
  "encoding": "base64",
  "key_id_method": "sha256-spki-der",
  "key_id": "<64 lowercase hex>",
  "signature": "<base64 Ed25519 signature>"
}
```

No private key, passphrase or secret is embedded. The field names follow the
mechanism's standard representation (algorithm, encoding, key id, signature
bytes).

## 7. CLI

Normal validation is unchanged and needs no key:

```
python scripts/pre_tag_check.py
python scripts/pre_tag_check.py --summary
python scripts/pre_tag_check.py --json
python scripts/pre_tag_check.py --verify-report <report.json>
```

Two optional operations are added, mutually exclusive with the existing output
modes:

```
python scripts/pre_tag_check.py --sign-report <report.json> --private-key <private.pem> [--output <signed.json>]
python scripts/pre_tag_check.py --verify-report <report.json> --public-key <public.pem>
```

`--sign-report`:

- reads an existing report (malformed JSON/non-object → clear failure);
- **verifies its SHA-256 attestation first** and **refuses to sign** when the
  attestation is already invalid (a modified report, or a report paired with a
  changed tree, is rejected rather than signed);
- signs the canonical payload from section 4;
- adds/replaces the `signature` envelope;
- writes to `--output`, or to a **new** file named `<report>.signed.json` when
  `--output` is omitted; the input is overwritten **only** when the same path is
  supplied explicitly;
- never modifies a repository file and never commits, pushes or tags;
- prints only the output path, algorithm and `key_id` — no key material.

`--private-key`/`--output` are only valid with `--sign-report`, and
`--public-key` only with `--verify-report`; argparse rejects other combinations.

## 8. Verification semantics

`--verify-report` keeps its read-only, no-check behaviour and reports the two
evidence layers distinctly:

| Situation | Result |
| --- | --- |
| Attestation valid, **no** `signature` object | attestation `PASS`; exit `0` |
| Attestation valid, signed, **no `--public-key`** | attestation `PASS` + **`WARN signature present but not verified`**; exit `0` |
| Attestation valid, signed, **correct** public key | attestation `PASS` + **`PASS report signature verified (key <key_id>)`**; exit `0` |
| **Wrong** public key | `FAIL` — `key_id` mismatch (the report records key A, the key supplied is B); exit `1` |
| **Modified** report | `FAIL` — report payload hash mismatch (integrity catches it first); exit `1` |
| **Modified** signature | `FAIL` — signature does not match the report content; exit `1` |
| **Malformed** signature / `key_id` / encoding, or **unsupported** algorithm | `FAIL` with the specific reason; exit `1` |
| `--public-key` supplied but the report is **unsigned** | `FAIL` — no signature object to verify; exit `1` |
| Signing tool unavailable | `FAIL` — clear "not available on PATH" message; exit `1` |

The five outcomes are therefore distinguishable: *integrity verified*, *signature
absent*, *signature present but not verified*, *signature verified*, and
*signature invalid*. An **unsigned** report remains valid for its SHA-256
integrity, so already-archived keyless reports keep verifying. Verification runs
**no** release gate, no suite and no drift check, creates no temporary file and
modifies nothing; stdout stays clean and diagnostics go to stderr.

## 9. Security considerations

- No hand-rolled cryptography; no invented padding or key formats; no MD5 or
  SHA-1; no shared secret used as asymmetric signing (a signature must not be
  producible by any verifier). The fake signer exists **only** in tests.
- No automatic key generation and no permanent key anywhere in the repository;
  the integration test generates a throwaway key **outside** the working tree
  under the pytest temporary directory.
- The external tool is detected explicitly (`shutil.which`) and reports a clear
  error if absent; all subprocess calls use argument tuples with no
  `shell=True`.
- Private-key material is never written to the report, to stdout or to stderr;
  only the public fingerprint is recorded. Binary artefacts (payload, signature,
  DER public key) live in a private temporary directory that is removed
  afterwards.
- Signing only verifies that a report was signed by **a holder of the private
  key**. It makes **no identity claim** beyond key possession/control, and no
  claim that the repository, the release or an external authority is trusted.
- The signature does **not** replace the attestation and does **not** perturb it:
  a modified content field still fails the integrity check, and a modified
  signature fails the signature check.

## 10. Tests

`tests/test_pre_tag_check.py` gained **27 tests**, reusing `FakeRunner`,
`make_repo`, `_generate_json`, `_archived` and `_verify`, plus an injected
`FakeSigner` (deterministic HMAC-SHA-256 stand-in matching the signer interface)
and fake key files written **outside** the working tree.

Key/signing: a signed report is valid JSON with the expected top-level fields;
the `signature` object carries algorithm/`encoding`/`key_id_method`, a 64-hex
`key_id` and base64 bytes of the signer's fixed digest size; the private key is
not embedded; the `key_id` matches the public-key fingerprint; signing is
deterministic (two runs are byte-identical); signing preserves every report
field and the attestation (the signature is an envelope and does not change
`report_payload_sha256`); signing a report with an already-invalid attestation
is refused; the default output is a **new** file and leaves the input untouched;
the input can be overwritten only when the same path is passed explicitly;
`--sign-report` without `--private-key` is rejected; a missing tool fails
clearly.

Verification: an unsigned report still verifies; a signed report without a key
is reported as *not verified* (exit `0`); the correct key verifies (exit `0`);
the wrong key fails (`key_id` mismatch); a modified report fails; a modified
signature fails; a malformed signature fails; an unsupported algorithm fails;
supplying a key for an unsigned report fails; verification invokes no release
gate and passes no `--gate-report`; verification is read-only.

Security: the private secret never appears in stdout, stderr or the JSON report;
signing leaves the repository file set unchanged; signing never commits, pushes
or tags. A `skipif` integration test performs a **real** OpenSSL Ed25519
round-trip (generate key, sign, verify, confirm the fingerprint is the SHA-256
of the DER public key, and confirm a tampered report fails) and is skipped when
OpenSSL is unavailable.

No test runs the real suite or the real release gate.

## 11. Validation

| Command | Result |
| --- | --- |
| `python -m pytest` | **1081 passed** |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — All checks passed |
| `python -m mypy` | exit 0 — Success: no issues found in 40 source files |
| `python -m mkdocs build --strict` | exit 0 (built outside the repository) |
| `python scripts/check_licensing.py` | **9/9** — 220 files accounted for |
| `python scripts/check_version.py` | **3/3** — all `0.1.0` |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W7"]` |
| `python scripts/check_warning_drift.py` | exit **0** — all three sets `{W7, W12}` |
| `python scripts/check_release_manifest.py` | exit **0** — manifest and repository state agree |
| `python scripts/pre_tag_check.py` | exit **0** — `RESULT: READY FOR OWNER REVIEW` (12/12) |
| `python scripts/pre_tag_check.py --json` | exit **0** — valid JSON with a SHA-256 attestation |
| `python scripts/pre_tag_check.py --verify-report <report>` | exit **0** — valid for the current tree |
| `git diff --check` | clean |

**Test delta: 1054 → 1081 (+27).** No existing test was modified or weakened;
the shared fixtures were extended, not replaced.

Signature behaviour was also checked end-to-end against the real repository with
a throwaway Ed25519 key outside the tree: a signed report verifies with the
correct public key; the wrong key fails; a tampered report fails; a tampered
signature fails; an unsigned report keeps its existing integrity behaviour;
signature verification runs no release gate; and no key material, and no
generated artefact, is left in the tree or in the output.

## 12. Protected invariants

`scripts/release_check.py` (and its warning detection), the B5 exact-warning
assertion (`ACCEPTED_RELEASE_WARNINGS`), `.freebuff/project-id`,
`licensing/manifest.toml`, `schemas/**`, the lab runtime,
`.github/workflows/docs.yml` and the warning classification logic were **not
modified**. CI keeps its five-job structure and its single `release_check.py`
invocation; no `continue-on-error` and no signing step were added. The accepted
set stays exactly `{W7, W12}`, `W6` remains CLOSED, `blockers` stay `[]`, the
classification stays `READY WITH WARNINGS`, and the 12-check sequence is
unchanged. Signing is never a CI requirement and a key is never required for
release validation. The default human-readable output is unchanged, and no new
report schema version was needed — the `signature` object is purely additive.

## 13. Limitations

The signature proves **possession and control of the signing key**, not personal
identity, and it does not authenticate the repository, the release or an external
authority. It covers the report payload only, not a Git commit or tag. It relies
on the owner keeping the private key secret and on the verifier obtaining the
genuine public key or fingerprint through a trusted channel — signing adds no key
distribution, no revocation and no transparency. OpenSSL must be available for
signing and for key-assisted verification (it is **not** needed for ordinary
validation). Ed25519 signatures here are deterministic; that aids reproducibility
but is a property of the scheme, not a security claim.

## 14. Deferred work

Deliberately **not** done in this step, per scope: no append-only evidence log,
no transparency service, no automatic key generation, and no CI signing. Those
would introduce key custody, distribution and trust questions beyond optional
owner-controlled provenance. The remaining action is the **owner's**: review the
tree and the attested report, optionally sign the reviewed report with their
private key and archive it alongside the public key/fingerprint, then commit,
push, tag and (optionally) publish manually. The agent does not commit, push, tag
or publish. Phase 17 remains **CLOSED**, E1 remains **HOLD**, and no novelty,
effectiveness, security, benchmark or publication claim is made.

## 15. Tag / Git status

* `v0.0.1` — unchanged; `git tag` lists only `v0.0.1`.
* `v0.1.0` — **not created**.
* No commit, push or tag was performed.
