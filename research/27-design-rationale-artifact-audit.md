# Phase 20 — Step 8: Design Rationale & Artifact Contribution Audit

**Phase:** 20 — Step 8 (design rationale and artifact contribution audit)
**Date:** 2026-09-29
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs.git`
**Audited revision:** `6802c81` (branch `main`)
**Documentation site:** `https://nadeem-majeedch.github.io/agent-security-labs/`
**Prior audits:** `research/20-research-positioning-audit.md` … `research/26-wilson-2025-final-closure.md`
**Method:** read-only inspection of the repository at `6802c81`, using the prior audits as evidence but re-deriving every claim in this document from repository content.
**Deliverable:** this file only (`research/27-design-rationale-artifact-audit.md`). No source, test, policy, lab YAML, scenario, CI, MkDocs, README, licence or citation file was created or modified; no literature search, no paper, no study design and no data collection was performed.

**Status: PASS.**

---

## 1. Executive Summary

**What the artifact is.** AgentSec Labs is a **designed educational and reproducibility artifact**: a deterministic, offline, mediated-agent harness (`agentsec`) with a single mediated tool-execution path, a three-valued policy engine, a versioned trace schema, a read-only descriptive evaluator, a declarative scenario layer, eight student labs (LAB-00 … LAB-07), instructor material, a MkDocs documentation site and CI. Every claim below is anchored to a file and, where relevant, to a test.

**What is established.** The artifact has a **coherent and largely explicit design rationale**. It is stated in `docs/development.md` (the longest design-rationale document in the repository), in the docstrings of the core components, in `labs/README.md` (the observables matrix and the "Eight distinctions"), in each lab's `README.md`/`config.yaml`/`scenario.yaml`, and in `labs/INSTRUCTOR-GUIDE.md` (learning objectives, teaching sequence, marking rubric, discussion prompts). The rationale is **distributed across those surfaces rather than consolidated into one design document**, and no single file states the artifact's contribution as a design claim.

**What is not established.** There is **no learner study, no participant data, no learning instrument, no comparison condition and no evidence that the construct the labs teach is a genuine learner difficulty**. Nothing in the artifact demonstrates educational effectiveness, security effectiveness, benchmark validity, measurement validity or research novelty, and nothing in this audit supplies any of those. The artifact is explicitly and repeatedly documented as making **no research-novelty claim**, and the Phase 17 research transition remains CLOSED.

**Governing constraint found in the repository.** `docs/development.md` records the design intent behind the artifact's own scope, including the deliberate absence of defences, provider adapters and research machinery, and — decisively for §14 — states that the root `README.md` "belongs to the surrounding research project and is intentionally left untouched".

**Three findings a next phase must act on.**

1. **The root `README.md` is stale** (§14) — it describes a single research-discovery deliverable and a "planned empirical study", and does not mention the package, the labs, the docs site or the Phase 17 closure. Staleness is *documented intent*, not an oversight.
2. **There is no `LICENSE` and no `CITATION.cff`** (`pyproject.toml` carries `license = { text = "TBD" }`), and there is no consolidated design-rationale document (§13).
3. **The artifact's contribution can be stated today only at the descriptive and design levels, with an evidence boundary** (§11) — the educational-method and research-contribution levels remain unsupported by evidence.

**Publication gate: unchanged (`HOLD`)** — Gates A and B NOT READY, Gate C INSUFFICIENT EVIDENCE (§12). The audit found **new evidence about artifact design only**; it found **no evidence of educational effectiveness** and **no evidence of research novelty**.

---

## 2. Repository Baseline

| Field | Value (verified at `6802c81`, branch `main`) |
|---|---|
| HEAD | `6802c81` — "PHASE 19 — STEP 2 PASS Github deployment Ready" |
| Recent history | `6802c81`, `5f7d2ae` (docs site), `0ed62a7` (Phase 18 labs + self-check), `d095d06` (Phase 16 LAB-07) |
| Working tree at audit start | clean except seven untracked research audits (`research/20` … `research/26`) |
| Package | `src/agentsec/` — 33 Python modules |
| Tests | 34 Python test modules; **694 tests collected and passing** |
| Tests by area (count of `def test_`) | labs 204 · tools 85 · trace 56 · policy 34 · scenario 33 · experiment 31 · eval 28 · cli 24 · agent 18 · mock 15 · models 12 · schema 2 |
| Runtime dependencies | `pydantic>=2.6`, `jsonschema>=4.20`, `PyYAML>=6.0` |
| Optional extras | `dev` (`pytest>=7.4`), `live` (`httpx>=0.27`, unused), `docs` (`mkdocs-material>=9`) |
| Python | `requires-python = ">=3.11"`; version `0.0.1`; `license = { text = "TBD" }`; `readme = "docs/development.md"` |
| Console entry point | `agentsec = "agentsec.cli:main"` |
| Tool set | `calculator`, `fs_sandbox`, `mock_db`, `mock_email` (`tools/factory.py::TOOL_FACTORIES`) |
| Policies | `deny_by_default.yaml`, `least_privilege_v1.yaml`, `lab06_excessive_agency_v1.yaml`, `lab07_data_leakage_v1.yaml` |
| Trace schema | `schemas/trace/trace_event.v1.schema.json`, version `1.0`, 12 event types, generated from the pydantic models with a drift test |
| Labs | `labs/LAB-00-setup` … `labs/LAB-07-data-leakage`; **no LAB-08** (deliberate, documented) |
| Docs | `mkdocs.yml` with `docs_dir: labs`; nav = Getting Started → Lab Map (Overview + 8 labs) → Understanding Traces → Practice → Instructor Guide → Local Verification |
| CI | `.github/workflows/ci.yml` — `python -m pytest` then `agentsec labs check` |
| Pages | `.github/workflows/docs.yml` — strict MkDocs build + `deploy-pages`; `permissions: contents: read, pages: write, id-token: write` |
| Ignored output | `.gitignore` ignores `runs/`, `site/`, `traces/*.jsonl` (except `traces/examples/`) |
| Missing at root | **no `LICENSE`, no `LICENSE-*`, no `CITATION.cff`** |
| `docs/` contents | `development.md` only — **no separate design-rationale document** |

**Verification run for this step** (§17): `pytest` 694 passed, exit 0; `agentsec labs check` 8/8, exit 0; `mkdocs build --strict` exit 0; `git diff --name-only` empty.

---

## 3. Artifact Purpose

**Purpose as stated by the repository itself** (paraphrased from `docs/development.md`, `labs/README.md`, `labs/GETTING-STARTED.md`, `pyproject.toml`):

- An **educational + reproducibility infrastructure** project and a **mediated-agent harness**: eight small, offline, deterministic labs in which a learner runs one experiment, reads the trace it wrote, and answers "What can I actually observe in the trace?" with evidence.
- The package description (`pyproject.toml`) states: "AI Agent Security Lab - educational, reproducible agent-security infrastructure".

**Explicit non-goals recorded in the repository:**

| Non-goal | Where it is stated |
|---|---|
| Not a research paper / no research claim | `docs/development.md`; `labs/README.md`; every lab README's "Research positioning" (LAB-06, LAB-07) |
| Not a benchmark and not a scoring system | `labs/README.md`, `labs/LOCAL-VERIFICATION.md`, `docs/development.md` |
| Not a novelty claim | `docs/development.md` ("The package makes **no research-novelty claim** anywhere") |
| Not a production framework / not a security measurement | `docs/development.md` ("Current project scope") |
| No real model, no provider, no network | `docs/development.md`; `models/mock.py`; CI/test architecture rules |
| No defences | `docs/development.md` ("no defences yet - the adversarial labs observe behaviour only") |
| No LAB-08 | `labs/README.md`, `labs/GETTING-STARTED.md`, `docs/development.md` |

**Phase 17 boundary (carried into the artifact).** `docs/development.md` records the research transition as **CLOSED, NO-GO**, with a research-implementation freeze (no real stochastic adapter, no provider factory, no repeated-trial harness, no research corpus, no research metrics/evaluator/schema extensions, no research experiment, no benchmark). It also records the reason: every lab is driven by a deterministic scripted fixture, so model actions are *authored* by the fixture, tool calls are *scripted*, and any "result" is a property of the fixtures — not of an agent.

**Assessment.** The purpose is **coherent, scoped and consistently repeated** across code, docs, labs and CI. It is also **defensively over-stated**: the "not a research claim / not a benchmark / not real exfiltration" boundary appears in the package docs, `labs/README.md`, `labs/LOCAL-VERIFICATION.md`, `labs/INSTRUCTOR-GUIDE.md` §§9–10, and in both LAB-06 and LAB-07 READMEs. That redundancy is itself evidence that the boundary is a deliberate design principle rather than an afterthought.

---

## 4. Learning Objects

The concrete learning objects the artifact represents, and where each is realised:

| # | Learning object | Where it is realised |
|---|---|---|
| 1 | **Model response ≠ tool request** | `models/schema.py` (`ModelResponse.tool_calls`); `agent.py` dispatches calls through the gateway; trace types `model_response` and `tool_requested` |
| 2 | **Request** (an intention, not an action) | `ToolRequestedEvent` (`tool_requested`), emitted by `gateway.invoke` before any decision |
| 3 | **Policy / authorization decision** | `policy/schema.py::Decision` (`allow`, `deny`, `require_approval`); `policy/base.py::PolicyEngine` (first-match-wins, `default: deny`); `PolicyDecisionEvent` with `decision`, `matched_rule`, `reason` |
| 4 | **Denial** | `gateway.invoke` deny branch → `DeniedResult`, `tool_result{ok:false}`; no `tool_executed` |
| 5 | **Approval (pending vs granted vs refused)** | `gateway._resolve_approval` → `PendingApprovalResult`; `ToolResult.status = pending_approval` |
| 6 | **Execution** (a distinct stage) | `ToolExecutedEvent` (`tool_executed`), emitted only on the execute path |
| 7 | **Result / effect** | `ToolResultEvent` (`tool_result`) with `ok`, `result_hash`, `error`, `side_effects` |
| 8 | **Synthetic side effect** | `ToolResult.side_effects`; observable in LAB-06 (database write) and LAB-07 (message in the outbox) |
| 9 | **Trace / event sequence and causal chain** | Versioned trace schema; `seq`, `event_id = ev-<seq>`, `parent_event_id`; `TraceRecorder` |
| 10 | **Mediation boundary** | `ToolGateway` is the single supported execution path; `tools/factory.py` is the only tool constructor; enforced by `tests/test_architecture.py::test_gateway_is_the_only_tool_execution_boundary` and `tests/tools/test_no_bypass.py` |
| 11 | **Deterministic replay** | Injectable clock (`TraceRecorder(clock=...)`, `build_mvp_runner(clock=...)`); `MockModel` is clock-free/RNG-free; byte-identical replay tests for LAB-00…LAB-07 |
| 12 | **Separation between model intent and tool execution** | The agent never executes a tool; the gateway never calls a model; import-boundary tests forbid either from reaching into the other's layer |
| 13 | **Policy enforcement (and its limits)** | The three-valued engine; LAB-06 ("authorization ≠ necessity") and LAB-07 ("authorization ≠ confidentiality") |
| 14 | **Data-leakage / egress boundary** | `mock_email` in-memory egress sink; LAB-07's `SYNTHETIC-DEMO-DISCLOSURE-A1` marker visible at `mock_email.args_redacted.body` |
| 15 | **Trace interpretation as a learning task** | `TRACE-WALKTHROUGHS.md` (8 lab walkthroughs), `TRACE-READING-EXERCISES.md` (Sets A–G + final challenge), instructor-only answer key, `INSTRUCTOR-GUIDE.md` §5–§8 |
| 16 | **Descriptive (non-scoring) evidence** | `eval/builtin.py::TraceEvaluator` — counts, decisions, tool-result outcomes, flags, warnings; explicitly "no composite/risk/safety score" |
| 17 | **Expectation vs observation** | `scenarios/base.py` — `ExpectedObservation` → `ObservationCheck(expected, observed, matched)`; `inconclusive` instead of a silent pass |
| 18 | **Provenance without persisting secrets** | `trace/redact.py` — pattern/key redaction before write, `[REDACTED:<kind>]` markers, `hash_value` sha256 |
| 19 | **Running ≠ evaluating** | `ExperimentRunner` returns `ExperimentResult` with `agent` and `evaluation` side by side; `agentsec inspect`/`evaluate` read an existing trace without re-running |
| 20 | **Offline safety as a design property** | In-memory tools only; no network, credentials or host filesystem; tests forbid network references |

**These are learning objects, not novelty claims.** Objects 1–8 are the four-stage mediation chain the labs walk a learner through; objects 9–11, 16–20 are the reproducibility and evidence-discipline apparatus; objects 12–15 are the pedagogical method. All of them are established concepts re-implemented for teaching, exactly as `docs/development.md` states.

---

## 5. Explicit Design Principles

Only principles supported by repository evidence are listed. "Explicit" means the repository states the principle in prose (comment, docstring or documentation); "inferred" means the principle is enforced in code or tests but not stated as a principle anywhere.

| # | Principle | Repository evidence | Educational / reproducibility purpose | Explicit or inferred |
|---|---|---|---|---|
| 1 | **Single mediated tool path** | `tools/gateway.py` module docstring ("the single mediated path for every tool call"); `tools/factory.py` ("there is no supported path that executes a tool without a policy decision"); `tests/test_architecture.py::test_gateway_is_the_only_tool_execution_boundary` | Makes the authorization boundary an inspectable object rather than an implicit one | **Explicit** |
| 2 | **Policy decision precedes execution** | Gateway lifecycle steps 3–7 in `tools/gateway.py` and `docs/development.md`; `PolicyDecisionEvent` emitted before `ToolExecutedEvent` | The ordering the labs teach and the learner must verify in the trace | **Explicit** |
| 3 | **Three-valued authorization** | `policy/schema.py::Decision` = `allow`, `deny`, `require_approval`; `docs/development.md` "Policy model" | Distinguishes "no" from "not without a yes" (LAB-05) | **Explicit** |
| 4 | **A denied call never executes** | `gateway.invoke` returns a `DeniedResult` before `_execute`; `tests/tools/test_no_bypass.py` asserts the probe tool's run counter stays 0 | The lesson is verifiable in the trace (absence of `tool_executed`) | **Explicit** (docstring: "a denied call **never** invokes the underlying tool") |
| 5 | **Approval never silently becomes an allow** | `_resolve_approval` returns `pending` when nothing grants approval; docstring invariant; `docs/development.md` (OD-2) | Human-in-the-loop is observable and non-defaulted | **Explicit** |
| 6 | **Deterministic execution** | `models/mock.py` (pure function of messages + script; no clock/RNG; `latency_ms=None`); `MockModel` raises `UnsupportedParameter` for temperature/seed | Reproducible answers; the fixture can never be mistaken for a controllable LLM | **Explicit** |
| 7 | **Fixed-clock replay** | `TraceRecorder(clock=...)`; `event_id = ev-<seq>`; `build_mvp_runner(clock=...)`; `cli._fixed_clock` for `labs check` | Byte-identical replay, which is what makes a trace a citable artefact | **Explicit** |
| 8 | **Offline operation** | In-memory tools (`calculator`, `fs_sandbox`, `mock_db`, `mock_email`); no provider adapter; `tests/test_architecture.py::test_tests_do_not_reference_the_network`; docstrings "no network, no SMTP, no subprocess" | The labs run in any classroom with no keys, no cost and no legal exposure | **Explicit** |
| 9 | **Provider independence** | `models/base.py::ModelAdapter` protocol + `Capabilities` + `ModelInfo`; `agent.py` imports only abstractions; no provider adapter exists | Isolates the taught semantics from provider variability | **Explicit** |
| 10 | **Trace-first inspection** | `agentsec inspect` / `evaluate`; `TRACE-WALKTHROUGHS.md`; `TRACE-READING-EXERCISES.md`; `GETTING-STARTED.md` §4 | The trace is the primary teaching artefact | **Explicit** |
| 11 | **Descriptive-only evaluation (no scores)** | `eval/builtin.py` docstring ("no score/rating"); `docs/development.md` ("No composite/risk/safety score is produced") | Keeps the artifact outside benchmark/security-measurement territory | **Explicit** |
| 12 | **Declarative, non-executing scenarios** | `scenarios/base.py`; `ScenarioDef` embeds the experiment; `tests/test_architecture.py::test_scenario_layer_does_not_execute_anything`; a lab test asserts `config.yaml` and `scenario.yaml` cannot drift | Expectations are declared once and checked, not asserted in prose | **Explicit** |
| 13 | **Inconclusive rather than a silent pass** | `scenarios/base.py` `ScenarioStatus`; `docs/development.md` "Inconclusive, not silently passing" | An unevaluated or mismatched run can never look clean | **Explicit** |
| 14 | **Reproducible educational artefact** | `agentsec labs check` (temp-dir writes); `labs/LOCAL-VERIFICATION.md`; `ci.yml` runs pytest + labs check | The teaching claims are re-verified on every push | **Explicit** |
| 15 | **Instructor/student separation** | `TRACE-READING-EXERCISES-ANSWER-KEY.md` built by MkDocs but omitted from `nav` (`mkdocs.yml` `validation.nav.omitted_files: ignore`); `labs/README.md` "Instructors:"; `INSTRUCTOR-GUIDE.md` §6 | Exercise answers are not shipped in student-facing navigation | **Explicit** |
| 16 | **Safe synthetic data** | `mock_db` synthetic seed; LAB-07 `sandbox_db_seed` with `SYNTHETIC-DEMO-DISCLOSURE-A1`; recipient `reports@example.invalid` (RFC 2606) | A data-boundary lesson with nothing real to leak | **Explicit** |
| 17 | **Redaction before writing** | `trace/redact.py`; `TraceRecorder.emit` redacts, then validates, then writes; `writer.py` also redacts | No write path persists obvious secrets | **Explicit** (also bounded: "**not** a DLP system") |
| 18 | **No bypass by construction (scoped claim)** | `docs/development.md` "No-bypass" section states it is an architectural property, "not a claim that Python makes bypass impossible" | Honest claim scope; avoids overclaiming | **Explicit** |
| 19 | **Minimal, audited dependency surface** | `pyproject.toml` (three runtime deps); `tests/test_architecture.py::BANNED_TOP_LEVEL` (langchain, llama_index, crewai, langgraph, autogen, pandas, numpy, fastapi, streamlit, sqlite3, requests, flask, django, torch, tensorflow) applied to **both** `src/` and `tests/` | Installability and reproducibility in constrained environments | **Explicit** (the ban list is code, with a documented rationale in the test module docstring) |
| 20 | **One run, one recorder, one coherent trace** | `ExperimentRunner._validate_config` (config must match agent and recorder); `build_mvp_runner` replaces an existing trace file; `docs/development.md` "One run, one recorder, one coherent trace" | Prevents a run from producing an incoherent or appended-to trace | **Explicit** |
| 21 | **Sequential only — no retries, no parallelism** | `tests/test_architecture.py::test_experiment_modules_are_sequential_only` forbids `threading`, `multiprocessing`, `asyncio`, `concurrent.futures`, `subprocess`; `runner.py` docstring "never retries" | Removes an entire class of nondeterminism | **Explicit** |
| 22 | **The artefact must state its own limits** | The "Research positioning" sections (LAB-06, LAB-07); `INSTRUCTOR-GUIDE.md` §§9–10; `labs/LOCAL-VERIFICATION.md` "What it is — and is not"; Phase 17 section in `docs/development.md` | Prevents learners and reviewers from reading a fixture as a finding | **Explicit** |

**Principles deliberately *not* present** (and recorded as such): no defence mechanisms (no prompt firewall, no output filter, no DLP); no real model/provider adapter; no scoring, ranking or benchmark; no research metrics; no multi-agent support; no persistence/memory; no network functionality. Each absence is stated in `docs/development.md`, which is itself a design decision worth recording.

---

## 6. Architecture-to-Pedagogy Mapping

| Technical mechanism | Learner-facing concept | Observable artefact | Teaching purpose |
|---|---|---|---|
| `ToolGateway` (single mediated path) | the mediation boundary | `tool_requested` → `policy_decision` → (`tool_executed`) → `tool_result` | Distinguish intent, authorization, execution and outcome as separate things |
| `PolicyEngine` + `Decision` enum | authorization vocabulary: allow / deny / require_approval | `policy_decision.decision`, `matched_rule`, `reason` | Read *why* a request was refused versus held, with the deciding rule named |
| Gateway deny branch | "a `deny` prevents execution" | a `tool_result` with **no** `tool_executed` | Make the lesson falsifiable from the trace rather than asserted |
| `_resolve_approval` / `PendingApprovalResult` | human-in-the-loop boundary | `require_approval` + `tool_result{status: pending_approval}` | Separate "no" from "not without a yes" (LAB-05) |
| `ToolExecutedEvent` | "execution actually happened" | the presence of `tool_executed` | The single event that proves a tool ran |
| `ToolResult.side_effects` | synthetic state change | `tool_result.side_effects` | Distinguish "returned success" from "changed something" (LAB-06) |
| `MockModel` (scripted fixture) | controlled model behaviour | scripted `model_request` / `model_response` pairs | Isolate agent/tool and policy semantics from provider variability |
| Injected clock + `event_id = ev-<seq>` | deterministic replay | identical `timestamp`/`seq`/`event_id` across runs | Reproducibility: the same inputs give the same trace |
| `MockEmailTool` (in-memory egress sink) | egress / data boundary | `mock_email.args_redacted.body`; `side_effects` | Show that authorization ≠ confidentiality (LAB-07) |
| `MockDatabaseTool` + `sandbox_db_seed` | synthetic scenario data and provenance | the seeded row carrying `SYNTHETIC-DEMO-DISCLOSURE-A1` | A safe, inspectable data-flow lesson |
| `Redactor` + `hash_value` | provenance without exposure | `[REDACTED:<kind>]` markers and `result_hash` | Persistent evidence that does not persist secrets |
| `TraceEvaluator` (descriptive counts) | evidence discipline | `metrics`, `decisions`, `tool_calls`, `tool_results`, `flags`, `warnings` | Answer "what can I observe" with counts read straight off events |
| `DeclarativeScenario` / `ExpectedObservation` | expectation vs observation | `ObservationCheck(expected, observed, matched)`; `passed`/`failed`/`inconclusive` | Turn a declared expectation into a checked, evidence-referenced outcome |
| `ExperimentRunner` (one run, side-by-side results) | running ≠ evaluating | `ExperimentResult.agent` and `.evaluation` kept separate | Stop a run from collapsing into a single pass/fail boolean |
| `agentsec inspect` / `evaluate` CLI | reading an existing artefact | a text listing of `seq`, `event_type`, `event_id`, `parent` | Practise reading without re-running |
| `agentsec labs check` (temp-dir, declared expectations) | reproducibility of the teaching material | PASS/FAIL per lab; non-zero exit on failure | The lab claims are mechanically re-verified |

Every mapping above is supported by a named file, and the "observable artefact" column names fields that exist in `trace/schema.py` or in an evaluator/scenario result model.

---

## 7. LAB-00–LAB-07 Progression

Purpose: state **what progression the artifact implements**, not whether it works. Evidence: each lab's `README.md` (learning objectives, prerequisites, safety, procedure, what to observe/expect, checklist), `config.yaml`, and `scenario.yaml` `expected` block. Each `scenario.yaml` embeds the same experiment as its `config.yaml`, and a lab test asserts they cannot drift.

| Lab | Stated purpose | Prerequisite concepts | Main concept | Learner activity | Observable trace/event evidence | Declared expected observation | Relationship to previous | Relationship to next |
|---|---|---|---|---|---|---|---|---|
| **LAB-00 Setup** | Prove the environment works end to end (run → trace → evaluate) | none | warm-up; the whole path works offline | check import, check CLI, run the experiment, `inspect`, `evaluate`, work the troubleshooting list | full lifecycle for a `calculator` call: `run_started` … `agent_output` … `run_completed`; policy `allow`; `tool_executed` | **no `scenario.yaml`** — checked by the self-check's `SMOKE_EXPECTATIONS` (run completes, final answer produced) | n/a (first) | LAB-01 makes the same path the *subject* of study rather than a smoke test |
| **LAB-01 Benign** | Observe a normal agent lifecycle | LAB-00 | benign baseline: task → model → request → decision → execution → result → answer | run, inspect, evaluate, optionally read raw JSONL | 1 `tool_requested`(calculator) + `allow` + 1 `tool_executed` + `ok` result; output "5" | `tool_requests: 1`, `requested_tools: [calculator]`, `policy_denials: 0`, `tool_executions: 1`, `tool_results_ok: 1`, `output_contains: "5"` | LAB-00 proved the path runs; LAB-01 asks the learner to read it | LAB-02 introduces the first untrusted instruction (in the task) |
| **LAB-02 Direct prompt injection** | Observe an untrusted instruction placed **directly in the task** change what the agent does | LAB-01; request vs execution | direct prompt injection; trust boundary of the input | run, inspect, compare the answer with what the task appeared to ask; answer the questions | the fixture ignores the benign request and requests `calculator 6*7`; `allow`; `tool_executed`; output "42" | `tool_requests: 1`, `policy_denials: 0`, `tool_executions: 1`, `output_contains: "42"` | LAB-01's benign instruction is replaced by a hostile one in the same position | LAB-03 moves the instruction from the task into tool-returned content |
| **LAB-03 Indirect prompt injection** | Observe an instruction arriving **through content a tool returns**, then driving a follow-up request | LAB-02; note return values | indirect prompt injection; data read vs words obeyed | run, inspect, follow both tool calls in order, explain why one executed and one did not | `fs_sandbox` read: `allow` + `tool_executed` + `ok`; then an out-of-scope `fs_sandbox` write: `deny` + **no** `tool_executed` + `denied`; output "could not" | `tool_requests: 2`, `requested_tools: [fs_sandbox]`, `policy_denials: 1`, `tool_executions: 1`, `tool_results_ok: 1`, `tool_results_denied: 1`, `output_contains: "could not"` | LAB-02 added one hop (task → model); LAB-03 adds a second (content → tool → tool result → model) | LAB-04 removes injection entirely: the *requested operation itself* is out of scope |
| **LAB-04 Tool misuse** | Observe a **legitimate tool requested with an out-of-scope argument**; policy denies it, so it never executes | LAB-03; policy decision vocabulary | tool misuse; "the tool can" vs "the agent may" | run, inspect, locate the `policy_decision: deny` and confirm the absence of `tool_executed` | 1 request (`fs_sandbox` write `../../etc/passwd`), `policy_decision: deny` (rule `fs-deny-outside`), **0** `tool_executed`, `tool_result{ok:false}` | `tool_requests: 1`, `policy_denials: 1`, `tool_executions: 0`, `tool_results_denied: 1`, `output_contains: "I can help with that"` | LAB-03's denial was a side effect of an injection; LAB-04 makes the denial the point | LAB-05 introduces a decision that is neither allow nor deny |
| **LAB-05 Require approval** | Observe the third policy decision: a legitimate request held for authorization | LAB-04; allow/deny semantics | the approval boundary; "no" vs "not without a yes" | run, inspect, distinguish `deny` from `require_approval` in the decision event and result status | `mock_db` read → `policy_decision: require_approval` (rule `db-read-requires-approval`), **0** `tool_executed`, `tool_result{ok:false}` (pending), output "waiting for approval" | `tool_requests: 1`, `policy_denials: 0`, `policy_approvals_required: 1`, `tool_executions: 0`, `tool_results_pending_approval: 1`, `output_contains: "waiting for approval"` | LAB-04 showed a refusal; LAB-05 shows a hold that is not a refusal | LAB-06 flips to `allow` and execution — while the action remains unnecessary |
| **LAB-06 Excessive agency** | Observe an **authorized but unnecessary** state-changing action that actually executes | LAB-05; the three decisions | excessive agency; authorization ≠ necessity | run, inspect, find `tool_executed` for the write and read `side_effects` | `mock_db` `DELETE FROM audit_log` → `allow` (lab06 policy) → `tool_executed` → `tool_result` with `side_effects` | `tool_requests: 1`, `policy_denials: 0`, `tool_executions: 1`, `tool_results_ok: 1`, `output_contains: "I can help with that."` | LAB-05's control *waits*; LAB-06's control is *satisfied* and the outcome is still undesirable | LAB-07 keeps authorization and necessity satisfied and moves the problem to the data flow |
| **LAB-07 Data leakage** | Observe an **authorized read + authorized egress** that still move content across a boundary | LAB-06; egress concept | data leakage; authorization ≠ confidentiality | run, inspect, locate the marker in `mock_email.args_redacted.body`, explain what crossed and where it is visible | `mock_db` read → `allow` → `tool_executed` → `ok`; `mock_email` send → `allow` → `tool_executed` → `ok` with `side_effects`; `SYNTHETIC-DEMO-DISCLOSURE-A1` visible in `args_redacted.body` | `tool_requests: 2`, `requested_tools: [mock_db, mock_email]`, `policy_denials: 0`, `tool_executions: 2`, `tool_results_ok: 2`, `output_contains: "I forwarded"` | LAB-06 changed a database; LAB-07 moves content across a boundary | **no next lab** — the sequence deliberately ends here (`labs/README.md`, `GETTING-STARTED.md`) |

**Progression logic implemented.** The sequence varies **one thing at a time** along two axes: (a) **where the instruction or problem originates** — task (LAB-02), tool-returned content (LAB-03), the requested operation itself with no instruction (LAB-04), nothing adversarial at all (LAB-05, LAB-06, LAB-07); and (b) **what policy answers** — `allow` (LAB-01, LAB-02, LAB-06, LAB-07), `deny` (LAB-03 write, LAB-04), `require_approval` (LAB-05). The last two labs shift the question from authorization to *necessity* (LAB-06) and then to *confidentiality* (LAB-07). `labs/README.md` states the sequence is **not ranked**: "each one isolates a **different question**".

**Not assessed here:** whether the progression produces learning. No claim is made about ordering, difficulty or effectiveness.

---

## 8. Eight Distinctions Evidence Matrix

`labs/README.md` states "**Eight distinctions to carry across every lab**" (items 1–8) and then "Two more that LAB-07 makes concrete" (items 9–10). The matrix below checks each one against **implementation**, **trace representation**, **lab exercise** and **documentation** — a distinction is not credited as implemented merely because it is documented.

| # | Distinction (as stated) | Explicitly stated | Implemented in code | Represented in traces | Exercised by labs | Documented for learners/instructors |
|---|---|---|---|---|---|---|
| 1 | A **model response** is not the same as a **tool request** | **YES** — `labs/README.md`; `INSTRUCTOR-GUIDE.md` §5.1 | **YES** — `agent.py` reads `ModelResponse.tool_calls` and dispatches separately; `AgentOutputEvent` vs `ToolRequestedEvent` | **YES** — distinct `model_response` and `tool_requested` event types | **YES** — LAB-01…LAB-07 | **YES** — `labs/README.md`, `TRACE-WALKTHROUGHS.md`, exercises Set A |
| 2 | A **tool request** is not proof the tool **executed** | **YES** — `labs/README.md`; exercises §1 rule 1; `INSTRUCTOR-GUIDE.md` §5.2 | **YES** — `tool_requested` is emitted before the decision; `ToolExecutedEvent` only on the execute path | **YES** — presence/absence of `tool_executed` | **YES** — LAB-03, LAB-04, LAB-05 | **YES** — exercises Set B ("Requested or executed?") |
| 3 | The **policy decision** happens **before** execution | **YES** — `labs/README.md`; `INSTRUCTOR-GUIDE.md` §5.3 | **YES** — fixed emit order in `gateway.invoke` (steps 3–7) | **YES** — `seq` ordering; `parent_event_id` chains `tool_requested → policy_decision` | **YES** — LAB-01…LAB-07 | **YES** — `TRACE-WALKTHROUGHS.md` (event-by-event) |
| 4 | A **`deny`** decision prevents execution | **YES** — `labs/README.md`; exercises rule 3 | **YES** — deny branch returns before `_execute`; `tests/tools/test_no_bypass.py` asserts the tool never runs | **YES** — `policy_decision: deny` + `tool_result{ok:false}` with no `tool_executed` | **YES** — LAB-03 (write), LAB-04 | **YES** — exercises Set C ("Policy interpretation") |
| 5 | A **`require_approval`** decision does **not** mean execution happened | **YES** — `labs/README.md`; `INSTRUCTOR-GUIDE.md` §5.5 | **YES** — `_resolve_approval` → `pending` unless granted; `PendingApprovalResult` | **YES** — `require_approval` + `tool_result{ok:false}` + no `tool_executed` | **YES** — LAB-05 | **YES** — LAB-05 README; exercises Set C |
| 6 | An **`allow`** followed by **`tool_executed`** means the tool **really ran** | **YES** — `labs/README.md`; `INSTRUCTOR-GUIDE.md` §5.6 | **YES** — execute path emits `tool_executed`, then runs the tool | **YES** — `tool_executed` is the only execution evidence | **YES** — LAB-01, LAB-02, LAB-06, LAB-07 | **YES** — `TRACE-WALKTHROUGHS.md` |
| 7 | A successful execution may produce a **synthetic side effect** | **YES** — `labs/README.md`; `INSTRUCTOR-GUIDE.md` §5.7 | **YES** — `ToolResult.side_effects`, recorded on `tool_result` | **YES** — `tool_result.side_effects` | **YES** — LAB-06 (write), LAB-07 (outbox) | **YES** — exercises Set D ("Side-effect evidence") |
| 8 | A **`tool_result`** can exist for a denied request **even though no `tool_executed` exists** | **YES** — `labs/README.md`; exercises rule 6 | **YES** — the deny and pending branches emit a result without executing | **YES** — `tool_result` whose `parent_event_id` is a `tool_requested` with no `tool_executed` child | **YES** — LAB-03, LAB-04, LAB-05 | **YES** — exercises Sets B/C |
| 9 | LAB-07 shows **authorized, synthetic egress** — **not** real-world exfiltration, and not a vulnerability | **YES** — `labs/README.md`; LAB-07 README "The marker, and what it is not"; `INSTRUCTOR-GUIDE.md` §9 | **PARTIAL** — implemented as a synthetic in-memory sink with an RFC 2606 recipient and a non-secret marker; the *negative* claim ("not real exfiltration") is a boundary statement, **not** a code-enforced property | **YES** — `mock_email.args_redacted.body` shows the marker | **YES** — LAB-07 | **YES** — LAB-07 README, `INSTRUCTOR-GUIDE.md` §9, `docs/development.md` |
| 10 | Because the model is a **deterministic fixture**, what you observe is the **mechanics** of a boundary, not a distribution of real model behaviour | **YES** — `labs/README.md`; `docs/development.md`; `GETTING-STARTED.md` | **YES** — `MockModel` is a pure function; no clock/RNG; `Capabilities` reports no temperature/seed | **YES** — observable in any replayed trace (identical events) | **YES** — all labs; LAB-07 states it most explicitly | **YES** — `docs/development.md` "Why (the deterministic-fixture boundary)" |

**Findings from the matrix.**

- Distinctions 1–8 are **fully implemented, represented, exercised and documented**. They are not documentation-only claims; each maps to an event type or a gateway branch that the tests cover.
- Distinction 9 is implemented in the *positive* sense (synthetic sink, reserved domain, non-secret marker) but its *negative* formulation ("not real-world exfiltration") is unavoidably a **documented boundary rather than an enforced invariant**.
- Distinction 10 is a **property of the implementation** (`MockModel`, injectable clock) that is *stated* as an epistemic caution.
- No distinction in the list is documentation-only. The matrix found **no case** where documentation claims a distinction that the trace cannot show.

---

## 9. Determinism and Reproducibility

### 9.1 Guaranteed by implementation

| Mechanism | Evidence |
|---|---|
| **Clock-free, RNG-free model** | `models/mock.py`: response is a pure function of the message list and script; `latency_ms=None`; token usage computed by word counts; module docstring: "consults no clock or RNG". |
| **Explicit capability reporting** | `MockModel` reports `supports_temperature=False`, `supports_seed=False` and raises `UnsupportedParameter` if either is passed, so no caller can silently assume control it does not have. |
| **Deterministic event identity** | `TraceRecorder._header`: `event_id = f"ev-{seq:06d}"`, `seq` monotonic; no UUID. |
| **Injectable clock** | `TraceRecorder(clock=...)` and `build_mvp_runner(clock=...)`. |
| **Single-run orchestration** | `ExperimentRunner.run` executes exactly one run and "never retries"; no batches, sweeps or parallelism. |
| **Sequential-only enforcement** | `tests/test_architecture.py::test_experiment_modules_are_sequential_only` forbids `threading`, `multiprocessing`, `asyncio`, `concurrent.futures`, `subprocess` anywhere under `src/agentsec/experiment`. |
| **Offline by construction** | Tools are in-memory (`calculator` AST-only, `fs_sandbox` virtual, `mock_db` synthetic, `mock_email` outbox); no provider adapter exists; `tests/test_architecture.py::test_tests_do_not_reference_the_network` forbids `http://`, `https://` and `socket` in the test suite; a banned-module list covers `src/` and `tests/`. |
| **Writes are contained** | `agentsec labs check` writes into `tempfile.TemporaryDirectory(prefix="agentsec-labs-check-")`, so the self-check never touches `runs/`; `runs/` and `site/` are git-ignored. |
| **Redaction is deterministic and idempotent** | `trace/redact.py` — pattern/key substitution to `[REDACTED:<kind>]`, idempotent for existing markers; `hash_value` is a canonical-JSON sha256. |

### 9.2 Intended/documented, but only conditionally guaranteed

| Claim | Precisely what holds | Evidence |
|---|---|---|
| "byte-identical replay" | Holds **when the recorder's clock is injected** (the test suite and `agentsec labs check` both do this). A plain `agentsec run` does **not** inject a clock — `_cmd_run` calls `build_mvp_runner(config)` with no `clock` — so two default runs differ in their `timestamp` fields (all other fields, including `event_id`, `seq` and content hashes, are reproducible). | `src/agentsec/cli.py` (`_cmd_run` vs `_run_for_self_check`); `trace/recorder.py` docstring ("no wall clock is consulted unless the caller injects a clock"). |
| "one run writes one coherent trace" | Guaranteed per run (`build_mvp_runner` replaces an existing file at the resolved path; the runner validates config/recorder consistency). Two *concurrent* runs pointed at the same path are not protected against each other — there is no locking and no parallelism support. | `src/agentsec/mvp.py`, `experiment/runner.py`. |
| Cross-environment reproducibility | The dependency set is small and pinned by lower bound only; the CI matrix is a single Python (3.11) on `ubuntu-latest`. Reproducibility across operating systems, architectures and other Python versions is **not tested**. | `.github/workflows/ci.yml`; `pyproject.toml`. |
| CI reproducibility on GitHub | The workflows are configured for it; the remote execution itself was **not observed** in this audit (documented site/Pages deployment is a separate, previously audited concern). | `.github/workflows/ci.yml`, `.github/workflows/docs.yml`. |

### 9.3 Empirically verified by repository tests

Determinism is not merely asserted in prose; it is **tested**:

- `tests/labs/test_lab0N.py::test_lab0N_replay_is_byte_identical` — for **all eight** labs (LAB-00 … LAB-07), each run twice with a fixed clock into `tmp_path` and compared byte-for-byte.
- `tests/labs/test_lab0N.py::test_lab0N_evaluation_is_deterministic` — evaluation stability per lab.
- `tests/mock/test_mock.py::test_replay_is_byte_identical_over_many_runs`, `::test_no_clock_dependency`.
- `tests/trace/test_recorder.py::test_recording_is_deterministic`; `test_writer.py::test_serialize_event_is_deterministic`; `test_redact.py::test_redaction_is_deterministic`.
- `tests/experiment/test_runner.py::test_deterministic_experiment`.
- `tests/eval/test_eval.py::test_evaluation_is_deterministic`.
- `tests/scenario/test_scenario.py::test_interpretation_is_deterministic`.
- `tests/cli/test_cli.py::test_run_is_deterministic`.
- `tests/labs/test_lab_selfcheck.py::test_discovery_order_is_deterministic_and_sorted`.
- `tests/tools/test_mock_db.py::test_deterministic_across_instances`; `tests/tools/test_calculator.py::test_evaluation_is_deterministic`; `tests/labs/test_lab07.py::test_mock_email_message_ids_are_deterministic`.

**Independently re-observed in this audit:** `agentsec labs check` returned **8/8 PASS, exit 0** and the full suite returned **694 passing, exit 0**.

**Boundary of the claim (important).** The artifact's reproducibility claim is a claim about **deterministic fixtures under controlled conditions**, and the repository says so in the same breath (`docs/development.md`: "repeated runs demonstrate determinism, not behavioural distributions"). Reproducibility across platforms, Python patch versions or dependency upgrades is *supported by design* (small dependency surface, pinned lower bounds, generated schema with a drift test) but **not proven** by the current tests.

---

## 10. Safety and Boundary Design

| Boundary | Implemented? | Evidence |
|---|---|---|
| **All tools in-memory; no host filesystem, database or network** | **Implemented** | `tools/fs_sandbox.py` (virtual filesystem; rejects `..`, absolute POSIX, Windows drive, UNC/device paths, null bytes, reserved names; 64 KiB cap); `tools/mock_db.py` (synthetic, no SQLite); `tools/mock_email.py` (in-memory outbox, "no network, no SMTP, no subprocess"); `docs/development.md` "Safety limitations" |
| **No code execution in the calculator** | **Implemented, and test-enforced** | AST-restricted evaluator; `tests/test_architecture.py::test_calculator_never_calls_dangerous_builtins` asserts no `eval`/`exec`/`compile`/`open`/`__import__` and an allow-listed import set |
| **Synthetic data only** | **Implemented** | `mock_db` synthetic seed (including a planted non-credential `FAKE_SECRET_DB001` mentioned in `docs/development.md`); LAB-07's `sandbox_db_seed` row; recipient `reports@example.invalid` (RFC 2606) |
| **The LAB-07 marker is not a secret** | **Implemented + documented** | `models/mock.py::DISCLOSURE_MARKER = "SYNTHETIC-DEMO-DISCLOSURE-A1"`, chosen because it matches none of the redactor's patterns; LAB-07 README explains the choice |
| **Secrets are redacted before writing** | **Implemented** | `trace/redact.py` patterns + sensitive-key names; `TraceRecorder.emit` redacts → validates → writes; `writer.py` also redacts |
| **No real credentials exist anywhere** | **Implemented by absence** | No provider adapter, no `.env` usage, no credential field in `ExperimentConfig` (`docs/development.md`: "It has no fields for capabilities that do not exist (no temperature, seed, retries, parallelism or credentials)") |
| **No provider / no network dependency** | **Implemented** | No adapter module; `live = ["httpx>=0.27"]` extra is unused; `tests/test_architecture.py` network-needle test; banned-module list |
| **No production-agent interaction** | **Implemented** | Agent loop is local; tools are in-memory; no external endpoints |
| **No benchmark, no score, no ranking** | **Implemented + documented** | `eval/builtin.py` returns counts/flags only and states "no score/rating"; `scenarios` compare declared values; `labs/README.md` and `LOCAL-VERIFICATION.md` state the boundary explicitly |
| **No security-effectiveness claim** | **Documented** | `labs/LOCAL-VERIFICATION.md` "What it is — and is not"; `INSTRUCTOR-GUIDE.md` §9–§10; `docs/development.md` |
| **No claim that fixture behaviour represents real model behaviour** | **Documented, and structurally supported** | `docs/development.md` deterministic-fixture boundary; `MockModel` docstring ("not an LLM"); `Capabilities` refusal of temperature/seed |
| **The mediation boundary is not a Python-level guarantee** | **Documented honestly** | `docs/development.md` "No-bypass": "an architectural property, not a claim that Python makes bypass impossible"; `tests/tools/test_no_bypass.py` docstring repeats the scope limit |
| **Research freeze** | **Documented** | `docs/development.md` Phase 17 section lists the unimplemented research machinery that must stay unimplemented while the literature gate is NO-GO |

**Assessment.** Every safety boundary that could be enforced in code **is** enforced in code, and the residual boundary claims (no real exfiltration; fixture ≠ model; no benchmark) are **explicitly documented as claims rather than mechanisms**, with their scope limits stated. The one structural limitation the repository itself names is that the no-bypass property is a *supported-API* property, not a sandbox guarantee — a limitation that is recorded rather than hidden.

---

## 11. Artifact Contribution Levels

Progressively conservative descriptions of what the artifact contributes, derived **only** from repository evidence. **No level is selected as the answer**; the purpose is to expose the evidence boundary. Wording is deliberately limited: no "novel", "first", "state of the art", "better", "more effective" or "publishable".

### Level 1 — Descriptive artifact statement

> AgentSec Labs is a deterministic, offline, mediated-agent security lab set: an agent loop, a single mediated tool-execution gateway with a three-valued policy engine, a versioned JSONL trace schema, a read-only descriptive trace evaluator, a declarative scenario layer, eight student labs (LAB-00 … LAB-07) with declared expected observations, an offline self-check (`agentsec labs check`), instructor material including a trace-reading exercise set and answer key, a MkDocs documentation site and CI.

- **Safely stated now?** **YES.** Every clause maps to a file that exists at `6802c81` and, for the behavioural clauses, to a passing test.
- **Missing evidence:** none for the statement as written. (The statement is descriptive; it makes no claim about effect.)
- **Requires learner evaluation?** No. **Requires comparative evidence?** No.

### Level 2 — Design contribution statement

> The artifact implements a design in which (a) every tool call passes through exactly one mediated path that validates arguments, records the request, records an explicit authorization decision, and only then either executes or refuses; (b) authorization is three-valued (`allow` / `deny` / `require_approval`) and the decision is recorded *before* execution; (c) the resulting trace makes request, decision, execution and result into distinguishable, causally linked events; (d) the model is a deterministic fixture and the clock is injectable, so replays are byte-identical under controlled conditions; and (e) the tests enforce import boundaries, a single execution boundary, sequential-only execution, a banned dependency set and network-free operation.

- **Safely stated now?** **YES, with the claim scoped to "what the artifact does in code and tests"** — not to novelty and not to effect. Condition (d) must be stated as "under an injected fixed clock" (see §9.2).
- **Missing evidence:** a **written, consolidated design claim** argued against the existing hands-on-lab genre. The rationale exists, but it is distributed across `docs/development.md`, docstrings and lab docs, and no file states the design as a claim.
- **Requires learner evaluation?** No. **Requires comparative evidence?** No — but it does require a prior-art comparison to be defensible as a *contribution*, which is exactly the territory where Phase 20 records an occupied genre (`research/21`, `research/23`, `research/25`, `research/26`).

### Level 3 — Educational-method statement

> The artifact teaches agent-security concepts by having learners read a deterministic mediated trace and distinguish, with evidence, what was requested, what was decided, what executed and what changed; the trace-reading exercise set and instructor rubric target that distinction directly.

- **Safely stated now?** **PARTIALLY — as a description of the materials and the intended activity, yes; as a claim that the method teaches, no.** The materials exist (learning objectives, 36 exercises + final challenge, walkthroughs, rubric, discussion prompts) and the intended learner activity is explicit.
- **Missing evidence:** participants; a validated instrument; pre/post or transfer measures; a comparison condition; any observation of learner error patterns; and any evidence that the distinction is a genuine novice difficulty.
- **Requires learner evaluation?** **Yes.** **Requires comparative evidence?** **Yes**, for any claim about method effect (a non-trace comparison condition with equivalent time and topic exposure).

### Level 4 — Research-contribution statement

> *(Not formulated as a claim here.)* Any research-contribution statement would have to name a construct that prior work does not already teach and show an effect for it.

- **Safely stated now?** **NO.** Phase 20 records the genre as occupied, every component except E1-C as already established in the literature, E1-C as `INSUFFICIENT EVIDENCE` (the final decisive document remains unread), and the overall E1 question as **HIGH-RISK / INSUFFICIENTLY DISTINCT**.
- **Missing evidence:** everything empirical, plus closure of the remaining prior-art gap, plus a demonstrated learner difficulty, plus a validated instrument. Also missing: `LICENSE` and `CITATION.cff`, which any release-shaped contribution requires.
- **Requires learner evaluation?** **Yes.** **Requires comparative evidence?** **Yes.**

**Evidence boundary exposed:** levels 1 and 2 are supported by repository artefacts and tests today; level 3 is supported only as a description of teaching materials; level 4 is unsupported and additionally constrained by the Phase 20 prior-art position. The boundary between level 2 and level 3 is the boundary between **what the artifact does** and **what learners gain** — and only the former is evidenced here.

---

## 12. Publication-Gate Implications

`research/23` §7 established Gate A **NOT READY**, Gate B **NOT READY**, Gate C **INSUFFICIENT EVIDENCE**, and a final decision of **HOLD**; `research/24`, `research/25` and `research/26` left all three unchanged. This step does not change them automatically, and asks whether it supplies evidence relevant to any of them.

| Gate | Prior status | Effect of this audit | New evidence actually supplied |
|---|---|---|---|
| **Gate A — artefact publication** | **NOT READY** | **Unchanged** | New evidence **about artifact design**: the design principles are explicit and mostly test-enforced (§5), the architecture-to-pedagogy mapping is complete (§6), the lab progression is coherent (§7), and eight of the ten stated distinctions are fully implemented, trace-represented, exercised and documented (§8). **Still absent:** a stated design claim in citable form; any evaluation or adoption evidence; `LICENSE`/`CITATION.cff`. |
| **Gate B — experience report** | **NOT READY** | **Unchanged** | New evidence **about the rationale material**: it exists in quantity and detail (`docs/development.md`, `INSTRUCTOR-GUIDE.md`, lab docs, code docstrings) but is **distributed rather than synthesised**, and there is still **no learner or instructor evaluation**. |
| **Gate C — empirical study** | **INSUFFICIENT EVIDENCE** | **Unchanged** | **Nothing.** This audit collected no data, has no participants, and did not design a study. It also confirms the artifact lacks the instrument and comparison condition a study would need. Human-participant work would require **ethics/IRB approval**, which does not exist. |

**Explicit separation of the three kinds of evidence** (the central discipline of this step):

1. **Evidence about artifact design** — supplied in quantity by this audit (§§5–10). This is evidence that the artifact *is deliberately constructed*, not that it *works*.
2. **Evidence of educational effectiveness** — **none**. No learners, no instrument, no measurement, no comparison. No result in this audit may be read as a learning effect.
3. **Evidence of research novelty** — **none**. Phase 20 records the genre as occupied and the distinctive element (E1-C) as `INSUFFICIENT EVIDENCE` overall while absent from the two sources that could be inspected in full. A mature artifact is not a novel contribution.

**Do not treat (1) as (2) or (3).** No venue is chosen, ranked or recommended here, and no acceptance likelihood is estimated or implied.

**Gate-relevant condition already on record** (`research/23` §10): the prior-art condition would move the gate only if the decisive full-text test resolved against preemption. `research/25`/`research/26` record that it resolved against preemption for Wilson 2026 but remains unresolved for Wilson 2025 (JCSC 41(4):173–182, closed access). That condition is therefore still only half satisfied, and this audit adds nothing to it.

---

## 13. Missing Evidence Inventory

### A. Artifact completeness

| Item | Status |
|---|---|
| `LICENSE` (code) | **Absent.** `pyproject.toml` carries `license = { text = "TBD" }`. |
| `LICENSE-DATA` (or equivalent) | **Absent** (referenced as needed in the root README's licensing note). |
| `CITATION.cff` | **Absent.** |
| **Stale root `README.md`** | **Present and stale** — see §14. |
| Release metadata | **Absent.** `version = "0.0.1"`; no tags/releases referenced in the repository; no changelog file. |
| Dual-use release policy | **Absent** as a document; the boundary is stated in prose across several files, but there is no single policy for releasing adversarial educational material. |
| Consolidated design-rationale document | **Absent.** `docs/` contains only `development.md`. |

### B. Design documentation

| Item | Status |
|---|---|
| An explicit design-rationale document | **Absent as a single artefact**; the rationale is distributed across `docs/development.md`, module docstrings, `labs/README.md`, lab READMEs and `INSTRUCTOR-GUIDE.md`. |
| An architecture-to-learning-object mapping | **Absent as a document.** This audit produced one (§6) from code and docs; the repository does not state it in this form. |
| A formal lab-progression rationale | **Partial.** The progression is *implemented* (§7) and the labs are described individually, but no file states why the sequence is ordered this way beyond the per-lab "how this differs" sections. |
| A written statement of the artifact's design claim | **Absent.** |
| Integration of the Phase 20 prior-art position into repository documentation | **Absent.** The Phase 17 closure is in `docs/development.md`; the Phase 20 audits live in `research/` and are untracked. |

### C. Educational evidence

| Item | Status |
|---|---|
| Participants / cohort | **None.** |
| Learning instrument (validated or otherwise) | **None.** A marking rubric exists (`INSTRUCTOR-GUIDE.md` §7) but it is described as an "**instructional** rubric only" and "**not** a research measure". |
| Pre/post assessment | **None.** |
| Comparison condition | **None.** |
| Transfer assessment (unseen traces) | **None.** Note the exercise set uses *unlabelled* fragments drawn from the labs, which is a step toward transfer practice, but there is no measurement. |
| Qualitative learner interviews / misconception coding | **None.** |
| Evidence that the taught distinction is a genuine learner difficulty | **None.** No repository content asserts that novices actually conflate the four stages, and Phase 20 records this as the unestablished *problem* behind E1. |
| Ethics/IRB approval | **None** — and any learner-data collection would require it. |

### D. Prior-art evidence

Per the final state of Phase 20 (`research/20` … `research/26`):

| Item | Status |
|---|---|
| Decisive Wilson 2026 (JCERP) full text | **Inspected at level A**; contains no E1-C element. |
| Devadiga et al. 2026 (ITiCSE) full text | **Inspected at level A**; partially overlaps E1-C (prompt → output → manual execution → recorded result) but has **no authorization/policy decision**; the closest overlap located. |
| Wilson 2025 (JCSC 41(4):173–182) | **`INSUFFICIENT EVIDENCE`** — closed access; could not be obtained through any legitimate route reachable from the audit environment. |
| E1-C status | `INSUFFICIENT EVIDENCE` overall; **not preempted by inspected sources** (explicitly not "novel"). |
| Overall E1 classification | **HIGH-RISK / INSUFFICIENTLY DISTINCT** (unchanged across Phase 20). |
| Systematic database search (Scopus / WoS / ACM DL / IEEE Xplore) | **Not performed.** Coverage is web-search sampling plus targeted API/archive retrieval. |
| E1-G (measured conceptual understanding of the distinctions) | **Absent from the artifact and unlocated in prior work.** |

**No literature search was conducted in this step** and no prior-art conclusion is revised here.

---

## 14. Root README Status

`research/20` §2.12 flagged the root `README.md` as stale. **Verified: it remains stale at `6802c81`.**

**What the root README says** (all quotes from `README.md`):

- "Working project name for a planned empirical study on the security evaluation of LLM-based AI agents."
- "This repository currently contains **one research-discovery deliverable only**. It contains **no paper**."
- A status table whose rows are "Research landscape and gap analysis — **Complete**", "Full-text reading of the priority papers — Not started", "Systematic database search — Not started", "Model configuration verification — Not started", "Direction selection and pre-registration — Not started", "Implementation, experiments, paper — Not started".
- A "What is in here" tree that lists only `research/01-landscape-and-gap-analysis.md` and `research/tables/*.csv`, followed by a section map for that document.
- "**Licences** — Not yet assigned. Before any public release, `LICENSE` (code), `LICENSE-DATA` (data, likely CC-BY-4.0) and `CITATION.cff` must be created…"
- "Immediate next actions" beginning with "**Full-text reading (blocking).** AgentDyn; Zhan et al. …"

**Specific discrepancies against the audited revision:**

| Root README says | Actual repository at `6802c81` |
|---|---|
| "one research-discovery deliverable only" | A full `agentsec` package (33 modules), 8 labs, 694 tests, a docs site, CI and two workflows |
| "no paper" (true) but implies no other artefact | An installed console command `agentsec`, a versioned trace schema with a drift test, an offline self-check |
| "Implementation, experiments, paper — Not started" | Implementation complete for the educational artifact (labs, evaluator, scenarios, CLI, CI, Pages deployment) |
| Describes `research/01…` as the entry point | The student entry point is `labs/GETTING-STARTED.md`; the research audits are `research/12`–`research/27` |
| Does not mention labs, traces, MkDocs, GitHub Pages, or the mediated gateway | All exist and are documented in `labs/` and `docs/development.md` |
| Does not mention the Phase 17 closure | `docs/development.md` carries the CLOSED / NO-GO research status |
| "Licences — Not yet assigned" | Still true (`license = { text = "TBD" }`), and still no `LICENSE`/`CITATION.cff` |

**Important nuance.** The staleness is **documented intent, not an oversight**. `docs/development.md` ends with a section titled "Note on the repository README":

> "The repository root `README.md` belongs to the surrounding research project and is intentionally left untouched. The student-facing lab README and the MkDocs site are later steps (see `research/14-implementation-blueprint.md`)."

So the repository records a decision to leave the root README as the surrounding research project's document. **This audit does not fix it**, and any future fix is a scoping decision (does the repository become student-facing at the root, or stay research-project-facing?) rather than a copy edit.

**Consequence for a reader.** A visitor arriving at the repository root — or at the GitHub repository page — is told the project is a planned empirical study with no implementation. That is materially inaccurate for the audited revision and is the single largest documentation defect found in this audit.

---

## 15. Phase 20 Evidence Boundary

The prior-art position this audit must not override, restated from `research/20`–`research/26`:

1. **E1** (the education-research question about trace-first instruction and the `request → policy decision → execution → result` distinction in agent-security workflows) is classified **HIGH-RISK / INSUFFICIENTLY DISTINCT**.
2. **E1-C** — the explicit separation of request → policy decision → execution → result as named, observable, distinct concepts — is the distinctive element, and its status is **`INSUFFICIENT EVIDENCE`**: it was **not preempted by the inspected sources** (Wilson 2026 level A; Devadiga et al. 2026 level A, which partially overlaps but lacks any authorization/policy decision), while the final decisive document (Wilson 2025, JCSC 41(4):173–182) remains **unread and unobtainable** from the audit environment. "Not preempted by inspected sources" is **not** novelty.
3. **E1-G** — measured conceptual understanding of those distinctions — is **absent** from the artifact and unlocated in prior work.
4. The **genre is occupied**: hands-on LLM-security labs for novices with measured outcomes are published.
5. The publication gate is **HOLD** (Gates A/B NOT READY; Gate C INSUFFICIENT EVIDENCE).
6. **Phase 17 remains CLOSED**; no closed security-research direction was reopened.

**How this audit relates to that boundary.** The artifact *does* realize E1-C's four stages as distinguishable, causally linked trace events (§4, §6, §8 — distinctions 1–8), and it *does* implement trace-first instruction and trace reading as the primary learning activity (§4 objects 15–16, §6, §7). That is a **statement about the artifact's construction**. It does **not** establish that the construct is novel, that teaching it works, or that learners need it. Every Phase 20 conclusion above is therefore left exactly as recorded.

---

## 16. Recommended Next Phase

**Recommendation (one option, chosen from the brief's list): Option 1 — artifact hardening / documentation.**

**Why this option follows from the evidence in this audit:**

1. **The two hard blockers for any release-shaped artefact are documentation-completeness items, not engineering items.** The artifact is already mature in behaviour: 694 passing tests, 8/8 labs self-checking, a strict-building documentation site, no runtime dependencies beyond three, and no network or credential requirement. What is missing is a `LICENSE` (`pyproject.toml` currently says `TBD`), a `CITATION.cff`, a non-stale root `README.md`, and a consolidated design-rationale document (§13 A and B). All four are artefact-completeness work.
2. **The design rationale exists but is not in a durable, citable form.** `docs/development.md` is the largest rationale document in the repository, but it is framed as "development notes (Phase A)" and mixes status, architecture reference, operating instructions and research-boundary statements. Consolidating the design principles (§5), the architecture-to-pedagogy mapping (§6) and the progression rationale (§7) into one design document is the work that would let a reader (or a future reviewer) see the design as a design.
3. **The root README defect is reader-facing and currently inaccurate.** A visitor is told the project is an unimplemented planned study. This is the highest-value single fix, and it requires a scoping decision that only the project owner can make (student-facing root vs research-project root) — which is why it belongs in a hardening/documentation phase rather than being silently rewritten.

**Why not Option 2 — release preparation.** Release preparation presumes the two prerequisites that are absent: a licence and an accurate, non-stale root README. Preparing a release around a README that misdescribes the repository would ship the defect.

**Why not Option 3 — empirical educational study preparation.** Not supported by the evidence. There is **no demonstrated learner difficulty** to study, **no validated instrument**, **no comparison condition**, and no participant access. A study would additionally require **ethics/IRB approval**, and `research/23` §3.1 records that the operationalization of the construct is precisely the gap that is *not* ordinary study-design detail. Committing to study preparation now would also front-run the still-unresolved prior-art question (§15, item 2). If it is ever pursued, it must start with a documented, minimal, non-invasive observation and the appropriate ethics approval — not with data collection.

**Why not Option 4 — abandon E1.** E1 is **held**, not killed: E1-C is absent from every source that could be inspected in full and the question remains falsifiable and concrete; `research/23` §10 already records why ABANDON is not warranted. Abandoning would also discard the artifact's independent educational value, which does not depend on E1 at all.

**What this recommendation explicitly does not include.** Drafting a paper; choosing or ranking a venue; designing a study; collecting data; recruiting participants; adding defences, provider adapters or research machinery that `docs/development.md` records as deliberately frozen; or reopening any closed Phase 17 direction. **No paper should be drafted merely because the artifact is mature** — maturity is not a contribution, and §11 shows the contribution statement stops at the design level today.

---

## 17. Verification

Commands run for this step (read-only with respect to tracked files; the repository's own `py` launcher is used per project convention):

```
PYTHONPATH=src py -m pytest -q --tb=no
    -> exit 0; 694 tests executed (694 progress marks); 0 failure/error marks
PYTHONPATH=src py -m agentsec labs check
    -> LAB-00 … LAB-07 all PASS; "Result: 8/8 labs passed"; exit 0
py -m mkdocs build --strict
    -> exit 0; site built with no MkDocs warnings or errors
       (the only line matching "warning" is the standard Material for MkDocs
        informational banner about MkDocs 2.0, which is not a build warning;
        --strict would fail on a real warning)
git diff --name-only
    -> (empty) — no tracked file modified
git status --porcelain
    -> ?? research/20-research-positioning-audit.md
       ?? research/21-education-literature-hostile-audit.md
       ?? research/22-e1-fulltext-reaudit.md
       ?? research/23-publication-gate-audit.md
       ?? research/24-decisive-prior-art-closure.md
       ?? research/25-e1-c-source-recovery.md
       ?? research/26-wilson-2025-final-closure.md
       ?? research/27-design-rationale-artifact-audit.md   <-- the only new file
```

- **pytest:** 694 passed, exit 0.
- **labs check:** 8/8 passed, exit 0.
- **MkDocs strict:** exit 0, no warnings/errors.
- **`git diff --name-only`:** empty — no tracked file modified.
- **`git status --porcelain`:** exactly one new file, `research/27-design-rationale-artifact-audit.md`.
- `site/` is git-ignored build output and is not part of the tracked tree; building it does not modify tracked files.

---

## 18. Git Safety Confirmation

- **No `git add`.** **Nothing was staged.**
- **No `git commit`.** **No `git push`.**
- **No `git reset`, no `git checkout`, no `git clean`, no `git rebase`, no `git amend`.**
- **No existing file was modified or deleted** — not source, tests, policies, lab YAML, scenarios, CI, `mkdocs.yml`, `README.md`, nor any prior audit (`research/20` … `research/26`).
- **Exactly one file was created by this step:** `research/27-design-rationale-artifact-audit.md`.
- All Git operations remain the repository owner's to perform manually.

---

## Final report (as required by the step brief)

| Item | Result |
|---|---|
| **Status** | **PASS** — read-only audit completed; documents inspected: root `README.md`, `docs/development.md`, `labs/README.md`, `labs/GETTING-STARTED.md`, `labs/LOCAL-VERIFICATION.md`, `labs/INSTRUCTOR-GUIDE.md`, `labs/TRACE-WALKTHROUGHS.md`, `labs/TRACE-READING-EXERCISES.md` (+ answer key), all LAB-00 … LAB-07 `README.md`/`config.yaml`/`scenario.yaml`, `mkdocs.yml`, `pyproject.toml`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.gitignore`, `agent.py`, `tools/gateway.py`, `tools/factory.py`, `models/base.py`, `models/mock.py`, `policy/schema.py`, `policy/loader.py`, `policy examples`, `trace/schema.py`, `trace/recorder.py`, `trace/redact.py`, `eval/builtin.py`, `experiment/runner.py`, `mvp.py`, `selfcheck.py`, `cli.py`, `schemas/trace/trace_event.v1.schema.json`, `tests/test_architecture.py`, `tests/tools/test_no_bypass.py`, `tests/conftest.py`, and `research/20` … `research/26` |
| **Exact file created** | `research/27-design-rationale-artifact-audit.md` |
| **Files modified** | **none** |
| **pytest result** | 694 passed, exit 0 |
| **labs check result** | 8/8 labs passed, exit 0 |
| **MkDocs result** | `py -m mkdocs build --strict` exit 0, no warnings/errors |
| **git status** | `git diff --name-only` empty; `git status --porcelain` shows only the seven pre-existing untracked research audits plus the one new file |
| **Research claims introduced?** | **No.** No novelty, effectiveness, security-effectiveness, benchmark, measurement-validity or publication claim was introduced; each contribution level in §11 is explicitly bounded, and §12 separates evidence about design from evidence of effectiveness from evidence of novelty |
| **Phase 17 remains CLOSED?** | **Yes** — CLOSED, research NO-GO, unchanged; no closed direction reopened and nothing from the frozen list was implemented |

---

*End of Phase 20 — Step 8 design rationale and artifact contribution audit. The artifact is a coherent, deliberately designed educational/reproducibility artifact with an explicit (if distributed) rationale; the next phase is artifact hardening/documentation; the publication gate is unchanged at HOLD; Phase 17 remains CLOSED.*
