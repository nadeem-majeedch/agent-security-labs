# PHASE 26 — POST-v0.1.0 ROADMAP AND ARCHITECTURE RECONNAISSANCE

*Reconnaissance and planning only.* This record maps the repository as it stands
after the verified `v0.1.0` release, assesses whether more release-control
machinery is warranted, and proposes a staged roadmap for the next substantive
work. **Nothing is implemented here.** No source, test, CI, schema, policy or
release file was modified; no tag was created; nothing was committed, pushed or
published.

It makes **no research-novelty, effectiveness, security, benchmark or
publication claim**, and it does not reopen the Phase 17 research freeze or the
held E1 question. Where a proposal touches research, it is explicitly marked as
requiring a fresh hostile literature audit **before** any implementation.

## 0. Provenance and starting state

| Item | Value (verified read-only at the start of this audit) |
| --- | --- |
| Branch | `v0.1.0-dev` @ **`e831e0c`** — *"phas QA complete"*; in sync with `origin/v0.1.0-dev` |
| Released tag | **`v0.1.0`** → commit `3d731b0` (annotated; present locally and on `origin`) |
| Prior release | `v0.0.1` |
| Package version | `0.1.0` (3/3: `pyproject.toml`, `src/agentsec/__init__.py`, `CITATION.cff`) |
| Working tree | **clean** (`git status --porcelain` empty) |
| Tests | **1081 passed** (offline, hermetic) |
| Labs | `agentsec labs check` **8/8** |
| Quality gates | Ruff clean; `python -m mypy` 0 issues / 40 files; MkDocs `build --strict` exit 0; licensing 9/9; version 3/3 |
| Release gate | **READY WITH WARNINGS**, `blockers: []`, accepted set exactly `{W7, W12}`, `W6` CLOSED |
| Research posture | Phase 17 **CLOSED** (research NO-GO); E1 **HOLD**; no LAB-08 by design |

Note on the baseline: the branch head is now `e831e0c`, **one commit ahead of the
tagged release commit** `3d731b0`. That is expected — the tag pins the release;
the branch continues. No re-tagging or history change is implied or proposed.

**Status vocabulary** (as in `research/39`): **[MATURE]** present and exercised;
**[RECENT]** introduced in the release-engineering push (`research/50`–`64`);
**[RESERVED]** schema-defined but deliberately not emitted; **[DEFERRED]**
documented design, deliberately unbuilt; **[HOLD]** paused pending a condition;
**[CLOSED]** decided and not to be reopened.

---

# Part A — Repository architecture map

## A.1 Package structure and layering (`src/agentsec/`, ~5,400 lines)

A layered, dependency-inward harness. Import rules are enforced by
`tests/test_architecture.py`.

| Layer | Modules | Role | Maturity |
| --- | --- | --- | --- |
| Errors | `errors.py` | Typed exceptions actually used | [MATURE] |
| Models | `models/schema.py`, `models/base.py`, `models/mock.py` | Message/ToolSpec/ToolCall/Usage types; `ModelAdapter` protocol; deterministic scripted `MockModel` | [MATURE] (mock), [DEFERRED] (real adapter) |
| Tools | `tools/base.py`, `calculator.py`, `fs_sandbox.py`, `mock_db.py`, `mock_email.py`, `gateway.py`, `factory.py` | Four in-memory tools built only via the factory; single mediated `ToolGateway` path | [MATURE] |
| Policy | `policy/schema.py`, `base.py`, `loader.py` | Flat ordered rule list, first-match-wins, three decisions; strict YAML loader | [MATURE] |
| Agent | `agent.py` | Smallest deterministic model/tool loop; depends only on abstractions | [MATURE] |
| Composition | `mvp.py` | The one place wiring model + tools + policy + recorder into a runner | [MATURE] |
| Eval | `eval/base.py`, `eval/builtin.py` | Read-only, descriptive `TraceEvaluator` (counts, flags, outcomes; no score) | [MATURE] |
| Experiment | `experiment/config.py`, `runner.py` | Single-run orchestration; `extra="forbid"` config | [MATURE] |
| Scenarios | `scenarios/base.py`, `loader.py`, `registry.py` | Declarative expectation/interpretation layer; manual registry | [MATURE] |
| Trace | `trace/schema.py`, `redact.py`, `validate.py`, `recorder.py`, `writer.py` | Versioned 12-event schema; redaction-before-write; append-only JSONL | [MATURE] |
| CLI | `cli.py`, `__main__.py` | Thin `run` / `evaluate` / `inspect` / `labs check`; no execution logic | [MATURE] |
| Self-check | `selfcheck.py` | Offline lab reproducibility check | [MATURE] |

Key architectural invariants (enforced by tests): one run → one coherent trace;
the gateway is the only path to a tool; a denied call never executes; a
`require_approval` call never silently becomes an allow; the evaluator is a pure
read-only function; scenario code never runs the agent.

## A.2 CLI structure

`agentsec` (`argparse`, stdlib-only) with subcommands:

- `run <config.yaml> [--json]` — one experiment through the MVP stack.
- `evaluate <trace.jsonl> [--json]` — read-only trace analysis.
- `inspect <trace.jsonl> [--events]` — short summary, or a detailed read-only view.
- `labs check [--labs-dir] [--json]` — re-run every canonical lab into a temp dir.

Exit codes: `0` result produced (including denials/failures); `1` config/usage
problem or a failing lab; `2` orchestration failure. No subcommand compares two
traces or renders a diagram — see Part D.

## A.3 Lab structure (`labs/`)

Eight labs **LAB-00 … LAB-07** (no LAB-08), each a `README.md` + `config.yaml`
(+ `scenario.yaml` for LAB-01…07). Supporting teaching pages: `GETTING-STARTED.md`,
`README.md` (lab map + observables matrix), `TRACE-WALKTHROUGHS.md`,
`TRACE-FIELD-REFERENCE.md` (schema-derived), `TRACE-READING-EXERCISES.md` (48
exercises, sets A–I) with an instructor answer key, `INSTRUCTOR-GUIDE.md`,
`LOCAL-VERIFICATION.md`, plus the release pages `ACCEPTED-RELEASE-WARNINGS.md` and
`V0.1.0-RELEASE-MANIFEST.md`. [MATURE], with [RECENT] release pages.

## A.4 Test structure (`tests/`, 13 modules + subdirs, ~4,900 lines)

`conftest.py`; focused unit suites for eval, experiment, tools, policy, trace,
models, scenarios, schema and labs; architecture invariants; and the release
guards (`test_release_check.py`, `test_warning_drift.py`,
`test_release_manifest*.py`, `test_accepted_release_warnings.py`,
`test_licensing.py`, `test_version.py`, `test_public_surface.py`,
`test_pre_tag_check.py` — the last ~1,260 lines covering the orchestrator, the
`--json` report, the attestation and the optional signing). `test_architecture.py`
parametrises over every `tests/*.py`, so each new top-level test module adds one
collected test. [MATURE], with [RECENT] release-guard suites.

## A.5 Release / validation tooling (`scripts/`, 8 scripts)

| Script | Role | Maturity |
| --- | --- | --- |
| `release_check.py` | Composes all gates, emits classification + warnings (W6/W7/W9/W10/W11/W12/W13) | [MATURE], protected |
| `check_version.py` | 3-declaration version consistency | [MATURE] |
| `check_licensing.py` | LICENSE/LICENSE-DATA/README/manifest agreement + coverage | [MATURE] |
| `check_warning_drift.py` | Policy ↔ documentation ↔ gate warning sets | [RECENT] |
| `check_release_manifest.py` | v0.1.0 manifest vs repository (9 checks) | [RECENT] |
| `pre_tag_check.py` | Read-only 12-step owner pre-tag orchestrator; `--json`, `--verify-report`, `--sign-report` | [RECENT] |
| `export_trace_schema.py` | Generates both trace-schema copies | [MATURE] |
| `export_trace_reference.py` | Generates the trace field reference page | [MATURE] |

## A.6 Research records (`research/`, 64 numbered `.md` + `tables/`)

Historical audits `01`–`59`, then the release line `60`–`64`
(pre-tag validation → machine report → attestation → signing → post-release
snapshot). `research/tables/*.csv` holds the matrices. These are records, not
code; per the repository rule they are **not rewritten**. Post-`v0.1.0` the line
continues here as `research/65`.

## A.7 Documentation structure

`mkdocs.yml` with `docs_dir: labs` (no duplicated copy), `site_dir: site`,
`exclude_docs: **/*.yaml`, nav listing the lab pages; the instructor answer key
is built but kept out of nav. `docs/development.md` is the architecture/status
reference and is also the package `readme` (`pyproject.toml`). CI builds the site
strictly (`docs.yml`), and `release_check.py` runs a strict MkDocs gate locally.

## A.8 CI structure (`.github/`)

`ci.yml` — five jobs, one `release_check.py` invocation, no `continue-on-error`:
`lint` (Ruff, 3.11), `compatibility` (matrix 3.11 + 3.13: suite + labs check),
`typecheck` (mypy, 3.11), `coverage` (pytest-cov, report-only, no threshold), and
`release-readiness` (licensing + version, install `.[dev,docs]`, run the gate once,
warning-drift check). `docs.yml` — build + deploy to GitHub Pages on `main`.
[MATURE], intentionally minimal.

## A.9 Schemas

`schemas/trace/trace_event.v1.schema.json` and its packaged twin
`src/agentsec/schemas/trace/…` must stay byte-identical to a fresh
`export_trace_schema.py` run (drift-tested). The union is a discriminated set of
**12 event types**, including a **reserved** `security_event` (`label`/`severity`/
`evidence`) with **no runtime emitter** [RESERVED]. [MATURE].

## A.10 Runtime / application functionality

`agentsec run` executes exactly one deterministic, offline, mediated agent run and
writes a JSONL trace; `evaluate`/`inspect` read it back; `labs check` reproduces
all eight labs. There is **no network, no provider, no database server, no
defences beyond the three policy decisions, and no persistence/memory/RAG**.

## A.11 Component maturity summary

| Classification | Components |
| --- | --- |
| **MATURE / stable** | Core runtime (models/mock, tools + gateway, policy, agent, eval, trace, experiment, scenarios), 8 labs, trace schema + generators, CLI, self-check, licensing/version gates, CI, docs site |
| **RECENT** | Release-control line: warning-drift, release manifest + drift check, pre-tag orchestrator, `--json` report, SHA-256 attestation, optional Ed25519 signing; CI quality gates (ruff/mypy/coverage/compatibility matrix) |
| **EXPERIMENTAL** | Only the optional, key-optional signing path (`research/63`) — functional but not required by or wired into release validation |
| **RESERVED (schema, no emitter)** | `security_event` |
| **DEFERRED** | Real stochastic model adapter + provider factory; research corpus; repeated-trial harness; research metrics/evaluator/trace extensions; research benchmark; `shell_sandbox` and real tools; further defences; memory/RAG/persistence |
| **HOLD** | **E1** — educational question "does a trace-first deterministic lab improve novice understanding of the request → policy → execution → result distinctions?" (needs learner data/ethics; not authorized) |
| **CLOSED** | Phase 17 research transition (NO-GO); previously killed directions (`research/12`–`14`, `research/20`–`26`); **no LAB-08**; no paper/novelty claim |

---

# Part B — Release-control saturation analysis

The release-control surface is **already saturated**. Fourteen controls exist
(gate, warning policy, retirement procedure, drift check, CI integration,
single-gate-run, pre-tag checklist, manifest, manifest-drift, pre-tag
orchestrator, machine report, attestation, optional signing, post-release
snapshot). Each new layer adds maintenance, its own guard tests, and a new way
for the tree to drift. Evaluated individually:

| Candidate | Classification | Reasoning |
| --- | --- | --- |
| **Post-release checker** (`scripts/post_release_check.py`) | **Useful later** | A genuine narrow gap exists: nothing in the repository verifies the *published* tag — remote presence, annotated-ness, tag→commit identity, or version-at-tag — and the pre-tag guards structurally report NOT READY once `v0.1.0` exists. But it is fully satisfiable today with ~5 read-only `git` commands (done in `research/64`), so it is convenience, not necessity. Justified only if kept strictly read-only, stdlib-only, and independent of `pre_tag_check.py`. |
| **Append-only evidence log** | **Potentially harmful** | Introduces storage, ordering, retention and trust questions with **no consumer** in the repository. Nothing reads an evidence log. Pure maintenance cost. |
| **JSON Schema for the `--json` report** | **Useful later** | The report carries `schema_version` and a tested shape but no machine-checkable schema; adding one is additive and enables external validation. Optional, low value until a consumer exists. |
| **Mandatory signing** | **Potentially harmful** | Breaks the deliberate invariant that **a key is never required for release validation**. Would force key custody on every releaser and CI secrets. Rejected. |
| **External transparency log** | **Potentially harmful** | Adds a network dependency and external trust/availability authority, contradicting the offline, self-contained character of the project. No consumer. |
| **CI signature verification** | **Unnecessary for v0.1.x** | Needs key distribution and CI secrets; would make CI depend on a key, which the repository explicitly forgoes. The signing feature is owner-optional by design. |
| **Automated tag creation** | **Potentially harmful** | The owner-controlled tag is a deliberate human gate and a stated invariant. Automating it removes the review step and risks mis-tagging. Rejected. |
| **Automatic publication** | **Potentially harmful** | Release publication is owner-controlled; `docs.yml` already publishes the *docs site* on `main`. Automatic release publication would add irreversible side effects to CI. Rejected. |

**Conclusion (Part B).** No new release-control layer is *necessary* now. The only
defensible addition is a small, read-only **post-release checker** (useful later),
and the only cheap add-on is a **report JSON Schema** (optional). Everything else
is either unnecessary for `v0.1.x` or outright harmful to the project's
owner-controlled, offline, self-contained posture. Engineering attention is
better spent on the actual lab (Part D). `scripts/release_check.py`, warning
detection and B5 are **not** to be touched.

---

# Part C — W7 and W12 (analysis only; no retirement)

Neither warning is retired or modified. Both are deliberately accepted at this
release.

## C.1 W7 — tracked `.freebuff/project-id`

1. **Why it remains accepted.** `.freebuff/project-id` is a tool-generated
   identifier that the development harness requires; the repository keeps it
   **tracked** and records it as `excluded` in `licensing/manifest.toml`. The
   warning is therefore an accepted, explicit residual rather than an accident.
2. **Concrete cause.** `release_check.py` flags a *tracked* file whose manifest
   treatment is `excluded` — a tracked artifact that no licence covers.
3. **Condition that would clear it naturally.** The file would stop being
   tracked (or the harness would stop requiring it), so no tracked `excluded`
   file remained.
4. **What retirement would require.** Either untrack and delete the file — which
   would break the harness identity it exists for — or change the warning
   detection / manifest policy, both of which are protected. Neither is
   appropriate.
5. **Milestone.** **v0.1.x** keeps it accepted. Revisiting is warranted only if
   the tooling that writes it changes.
6. **New release risk if retired.** Deleting a tracked project-id can break the
   local harness and, if re-added later, simply re-triggers W7 — churn without
   benefit.

## C.2 W12 — human-judgement licensing residual

1. **Why it remains accepted.** Some licence-coverage decisions in `research/`
   (third-party citations, boundary files) require human judgement and cannot be
   fully automated; W12 is retained and re-stated rather than retired.
2. **Concrete cause.** The warning is part of the repository's warning policy —
   it is emitted for the human-judgement licensing residual rather than derived
   from a file-by-file licence failure.
3. **Condition that would clear it naturally.** None today: there is no
   repository condition that removes it without a policy change.
4. **What retirement would require.** A deliberate edit to the warning policy /
   detection in `scripts/release_check.py`, plus updating the exact-set
   assertion and the documentation. That is a **policy decision**, not a cleanup.
5. **Milestone.** **v0.2.x or later**, and only with an explicit, documented
   decision; it is out of scope for `v0.1.x`.
6. **New release risk if retired.** Retiring it means weakening/removing an
   always-on human-judgement signal and editing the exact-set assertion. That
   could mask genuinely new licensing residuals and reduce the gate's honesty.

**Constraint honoured:** the accepted set stays exactly `{W7, W12}`; the
classification stays `READY WITH WARNINGS`; the exact-set assertion is unchanged.

---

# Part D — Research / product direction candidates

Each candidate improves the actual lab. None adds a numbered lab, a benchmark, a
research claim or a defence mechanism. `[SUPPORT]` = current repository support;
`[GAP]` = missing capability; `[VALUE]`; `[SCOPE]`; `[DEPS]`; `[RISKS]`;
`[VALIDATION]`; `[MILESTONE]`.

## D1 — Read-only trace comparison (`agentsec compare A B`)

- **[SUPPORT]** Every run already writes a self-describing JSONL trace;
  `read_events` and the descriptive `TraceEvaluator` already produce comparable
  results. The `inspect` view already renders one trace.
- **[GAP]** There is no way to line up *two* runs — e.g. LAB-01 (benign) vs LAB-02
  (injection), or one lab under two policies — and see what changed. The core
  teaching act ("read the trace") is single-trace only.
- **[VALUE]** Makes the request → policy → execution → result chain *comparable*,
  which is precisely the distinction set the labs teach; high educational value.
- **[SCOPE]** Small: one thin CLI subcommand over existing reader + evaluator;
  no new events, metrics, scoring or reruns.
- **[DEPS]** Trace reader, evaluator, CLI; nothing else.
- **[RISKS]** Accidental invention of a "score" — avoid by comparing only
  existing descriptive fields; different run ids must not be treated as an error.
- **[VALIDATION]** Hermetic unit tests (identical / added / changed / unreadable);
  a real LAB-01-vs-LAB-02 comparison test; CLI wiring; docs page section; strict
  MkDocs.
- **[MILESTONE]** **v0.2.0.**

## D2 — Emit the reserved `security_event`

- **[SUPPORT]** The 12-event schema already defines `security_event`
  (`label`/`severity`/`evidence`); the evaluator already counts it.
- **[GAP]** No runtime emitter, so the event never appears in a trace.
- **[VALUE]** Lets a lab *observe* an explicitly labelled security-relevant event
  end to end, closing a schema/observer loop.
- **[SCOPE]** Medium: an emission point (gateway or scenario interpretation),
  schema/package regeneration, tests, and a lab observation — **without** adding
  judgement or a defence.
- **[DEPS]** Trace recorder, schema generator, a lab config/scenario.
- **[RISKS]** `label`/`severity` can read as an effectiveness/severity *claim*;
  mitigate by defining them as descriptive author labels only, never a verdict.
- **[VALIDATION]** Schema drift tests, recorder tests, a lab observation; strict
  MkDocs; architecture invariants.
- **[MILESTONE]** **v0.2.0** (or document it as reserved only, in v0.1.x).

## D3 — Use the three unused mock fixtures as documented variants

- **[SUPPORT]** `script_for` defines 10 scripts; 7 are used by labs. Three
  (`direct_injection`, `indirect_injection`, `authorization_violation`) are
  implemented but unused (`research/39` §8).
- **[GAP]** No lab or page exercises them, so they are dead-but-maintained code.
- **[VALUE]** Cheap breadth: documented "alternate variant" runs for existing
  labs, reinforcing the same distinctions from a second angle.
- **[SCOPE]** Small: documentation + possibly an extra example config; no new
  runtime semantics.
- **[DEPS]** Existing fixtures and configs only.
- **[RISKS]** Scope creep into new numbered labs — must stay as variants of
  existing labs.
- **[VALIDATION]** Tests already cover the fixtures; add doc/config consistency
  checks; strict MkDocs.
- **[MILESTONE]** **v0.1.x / v0.2.0.**

## D4 — "How a policy decision is reached" walkthrough

- **[SUPPORT]** The policy engine, rules and decisions are implemented and
  documented (`docs/development.md`).
- **[GAP]** No single end-to-end narrative tracing one rule table to a decision.
- **[VALUE]** Directly targets the "policy decision happens before execution"
  distinction the labs emphasise.
- **[SCOPE]** Small, documentation-only.
- **[DEPS]** Existing engine and labs.
- **[RISKS]** Prose drift from the engine — mitigate by referencing tested
  behaviour.
- **[VALIDATION]** Doc consistency tests; strict MkDocs.
- **[MILESTONE]** **v0.1.x.**

## D5 — Reproducibility / environment manifest

- **[SUPPORT]** Determinism is established (fixed clock, byte-identical replay,
  `labs check`).
- **[GAP]** No recorded dependency pins + environment snapshot for a
  "same inputs → same bytes" reproduction record.
- **[VALUE]** Strengthens the reproducibility story for instructors/reviewers.
- **[SCOPE]** Small–medium; stdlib-only, read-only generation.
- **[DEPS]** `pyproject.toml`, installed versions.
- **[RISKS]** Bit-rot; keep it generated, not hand-maintained.
- **[VALIDATION]** A guard that it is regenerable; no CI dependency on network.
- **[MILESTONE]** **v0.2.0.**

## D6 — Public API compatibility policy

- **[SUPPORT]** `test_public_surface.py` and `py.typed` exist.
- **[GAP]** No stated `0.x` compatibility policy for the exported surface.
- **[VALUE]** Sets expectations for external users of the package.
- **[SCOPE]** Small, documentation + guard.
- **[DEPS]** `agentsec.__all__`, packaging metadata.
- **[RISKS]** Over-committing stability for a `0.x` artefact.
- **[VALIDATION]** A test asserting the exported set matches the documented one.
- **[MILESTONE]** **v0.2.0.**

## D7 — Documentation-drift correction and guard

- **[SUPPORT]** The repository has drift guards for schema, warnings and the
  release manifest.
- **[GAP]** The README verification table states **"880 tests pass"** while the
  suite is **1081** (verified this phase); `docs/development.md` also still says
  the root README is "intentionally left untouched" though it was updated for
  `v0.1.0`. **These are real, verified drifts.**
- **[VALUE]** The README is the front door; stale counts undermine trust.
- **[SCOPE]** Small, but the *guard* is the interesting part: extend the existing
  documentation-consistency tests to derive the test count from the suite.
- **[DEPS]** Existing docs tests.
- **[RISKS]** A brittle exact-count assertion — prefer a derived/consistency
  check over a hard-coded number.
- **[VALIDATION]** The new guard plus strict MkDocs.
- **[MILESTONE]** **v0.1.x** (correction is essentially a defect fix).

---

# Part E — Research novelty sanity check

None of Part D is presented as novel research. The prior audits already showed
that generic agent-security and education ideas are heavily published, and the
Phase 17 freeze stands.

| Candidate | Builds on | Literature verification before any novelty claim | Engineering vs research | Experiment needed for a defensible contribution |
| --- | --- | --- | --- | --- |
| D1 trace comparison | Existing trace/evaluator | None needed — it is a reading aid, not a claim | **Engineering** | None (no claim) |
| D2 `security_event` | Reserved schema event | None for emitting it; any *interpretive* meaning would need review | **Engineering** (descriptive only) | None unless it becomes a measurement |
| D3 alternate fixtures | Existing fixtures | None | **Engineering / education** | None |
| D4 policy walkthrough | Existing engine | None | **Documentation** | None |
| D5 reproducibility manifest | Determinism work | None | **Engineering** | None |
| D6 API policy | Packaging surface | None | **Documentation / engineering** | None |
| D7 doc-drift guard | Existing drift guards | None | **Engineering** | None |
| Any "measure the lab's effect" idea | E1 | **Required** — fresh hostile full-text audit | **Research (currently HOLD)** | Learner study with ethics approval; not authorized |

Explicitly: a proposal that *measures* whether the labs improve learning, or that
compares attack/defence success rates, would be **research**, not engineering. It
must not be attempted without the mandated order (real stochastic adapter → small
controlled corpus → hostile literature audit → experiment) and, for E1
specifically, without authorized learner data. No such claim is made here.

---

# Part F — Proposed roadmap

Each phase ends green before the next begins. Nothing is implemented in this
phase; the agent never commits, tags, pushes or publishes.

## F.1 v0.1.x — maintenance (low risk, post-release appropriate)

- **Objective:** remove verified drift and small residuals without changing
  behaviour or the release posture.
- **Deliverables:** fix the README test-count drift and the `docs/development.md`
  README note (D7); add a documentation-consistency guard that derives counts
  rather than hard-coding them; optionally add a minimal read-only
  `scripts/post_release_check.py` (Part B) and, if desired, a JSON Schema for the
  `--json` pre-tag report.
- **Components likely affected:** `README.md`, `docs/development.md`,
  `tests/test_release_manifest.py` (or the appropriate existing docs-test module),
  possibly `scripts/` + `tests/` for the optional checker, `licensing/manifest.toml`
  (coverage count only, via the existing globs).
- **Tests/evaluation:** the new guard(s); full suite must stay ≥ 1081 and green;
  labs 8/8; strict MkDocs.
- **Release implications:** a patch-level change; no version bump required to
  land, but a future `0.1.1` could carry it. Accepted set stays `{W7, W12}`.

## F.2 v0.2.0 — substantive product / lab capabilities

- **Objective:** deepen the teaching artefact while keeping the observation-only,
  no-claim boundary.
- **Deliverables:** **D1** read-only trace comparison (the flagship); **D3**
  documented alternate-variant runs for existing labs; **D4** the policy-decision
  walkthrough; **D2** emit (or explicitly re-document as reserved) the
  `security_event`; **D5** reproducibility/environment manifest; **D6** public-API
  compatibility policy.
- **Components likely affected:** `src/agentsec/cli.py` and a small new
  read-only comparison module; `labs/` teaching pages and `mkdocs.yml` nav if a
  new page is added; `docs/development.md`; `tests/` (unit + a lab-pair
  comparison test); possibly `src/agentsec/trace/` + both schema copies if D2
  emits the reserved event.
- **Tests/evaluation:** hermetic unit tests per feature; architecture invariants
  preserved; schema-drift tests if the schema changes; labs check; strict MkDocs.
- **Release implications:** a minor version bump; the release-control machinery is
  unchanged; `{W7, W12}` remain accepted unless a separate policy decision says
  otherwise.

## F.3 Future research (gated — not scheduled)

- **Objective:** none authorized. Any research direction must start from a
  genuinely different boundary condition.
- **Deliverables:** the mandated prerequisites only — a real stochastic model
  adapter, a small controlled corpus, then a **hostile literature audit before**
  any experiment. E1 remains **HOLD** pending authorized learner data and ethics.
- **Components likely affected:** `models/`, a new provider factory, a corpus
  directory, research evaluator/schema extensions — **all currently frozen**.
- **Tests/evaluation:** would require statistical design and repeated trials that
  do not exist; no current infrastructure supports them.
- **Release implications:** none until a gap survives the audit; the Phase 17
  freeze stands and no paper/novelty claim may be made before then.

---

# Part G — Decision

## Recommended next engineering task

**Implement a deterministic, read-only trace comparison command,
`agentsec compare <trace-a> <trace-b>`.**

This is a **product/lab** task, not another release-control layer: it directly
serves the repository's core mission ("learn by reading the trace") by letting a
learner line up two runs — e.g. LAB-01 (benign) vs LAB-02 (direct injection), or
the same lab under two policies — and see, deterministically, what changed. It
composes existing components and adds no new runtime semantics, metrics, scores,
events, defences or claims.

- **Exact objective.** A new thin CLI subcommand that reads two existing JSONL
  traces and prints a deterministic, read-only comparison of their descriptive
  results; `--json` for a machine-readable form. No execution, no rerun, no
  mutation.
- **Expected files / components.** `src/agentsec/cli.py` (subcommand wiring,
  thin), a small new read-only comparison module under `src/agentsec/` (or
  `eval/`), `tests/` (unit + a real lab-pair test), and a documentation section on
  an existing lab/`inspect` page (plus `mkdocs.yml` nav only if a new page is
  added).
- **Acceptance criteria.** Deterministic output; exit `0` when both traces are
  readable and `1` on an unreadable/invalid trace, matching existing CLI
  conventions; comparison limited to fields the evaluator already reports (run/
  evaluation status, decision counts, tool request/execution counts, tool-result
  outcomes, requested tools, produced output); identical traces compare as equal;
  different `run_id` values are compared, not treated as an error; stdlib-only;
  no score, ranking or claim.
- **Tests required.** Hermetic tests for identical / differing / unreadable
  inputs; a real LAB-01-vs-LAB-02 comparison; CLI dispatch; architecture
  invariants preserved; full suite stays green (≥ 1081); labs 8/8; strict MkDocs.
- **What must remain untouched.** `scripts/release_check.py` and its warning
  detection; the B5 exact-warning assertion; `.freebuff/project-id`;
  `licensing/manifest.toml` (except the automatic coverage count for any new
  file); `schemas/**` (D1 adds no event); the version declarations; existing tags
  and release evidence; the lab runtime semantics; and the CI structure (no new
  job).

**Immediate prerequisite.** Before or alongside this task, land the **D7
documentation-drift correction** (README "880 tests" → current count; the
`docs/development.md` README note) with a derived consistency guard — it is a
verified, low-risk defect and the repository's drift-guard discipline should cover
the README too.

---

## Exact files changed

Added:

```text
research/65-post-v0.1.0-roadmap.md   (this record, CC BY 4.0)
```

Modified:

```text
(none)
```

## Tag / Git status

* `v0.0.1` and `v0.1.0` — unchanged; present locally and on `origin`.
* No commit, push or tag was performed by the agent.
