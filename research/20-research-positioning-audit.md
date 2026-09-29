# Research Positioning Audit

**Phase:** 20 — Step 1 (research-positioning audit, read-only)
**Date of audit:** 2026-09-28
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs`
**HEAD at audit:** `6802c81` — *PHASE 19 — STEP 2 PASS Github deployment Ready*
**Verified prior releases:** Phase 18 `0ed62a7`; Phase 19 deployment `6802c81`
**Live documentation:** `https://nadeem-majeedch.github.io/agent-security-labs/`
**Question under audit:** *Does the current repository contain a defensible research contribution that can support a publishable research paper, or is it primarily an educational/reproducibility artifact?*

**Standing constraints honoured in this step:** no source, test, policy, lab YAML, scenario, trace-schema, CI, MkDocs or documentation change; no `CITATION.cff`; no Zenodo release; no paper draft; no commit; no push. This step created exactly one file (`research/20-research-positioning-audit.md`).

**Evidence-labelling convention (carried forward from `research/05`, unchanged).**
Every literature claim carries a label:

| Label | Meaning |
|---|---|
| **A** | Fetched and read at the primary source in this session (abstract page / full text / official record). |
| **B** | Search-result, snippet or third-party listing only; full text not read. **Not quotable as a figure.** |
| **C** | Not verified; aggregator, blog or unlocated record. |

Repository claims cite the exact path and, where useful, the class/function. **[FACT]** = observed in the repository as read; **[INFER]** = derived from those observations; **[OPEN]** = unresolved. The audit distinguishes *observed implementation* from *interpretation* throughout.

---

## 1. Audit Scope

This audit establishes what the repository actually is at HEAD, separates artifact value from research contribution, performs a fresh (2026-09) literature search over twenty adjacent areas, rechecks the works that were load-bearing in the Phase 17 closure, applies a claim-by-claim novelty test, and classifies the artifact into exactly one evidence-based state. It does **not** design an experiment, does **not** reopen the Phase 17 research direction, and does **not** manufacture a contribution.

Two facts frame the whole audit:

1. **[FACT]** The project has itself recorded a **NO-GO** for research: `docs/development.md` §"Research status (Phase 17 — CLOSED, research NO-GO)" states, verbatim, *"The Phase 17 research transition is **CLOSED**"*, *"No literature-supported unresolved boundary condition survived the audit"*, and *"No novelty claim is made anywhere in this repository."* The same section documents the **deterministic-fixture boundary**: every lab drives a scripted `MockModel`, so *"model actions are authored by the fixture, not produced by a model"* and *"evaluator counts are fixture outcomes, not model propensities."*
2. **[FACT]** The audit prompt for this step asks whether a *defensible research contribution* exists. The honest answer must therefore be tested against the literature **and** against the project's own boundary, not against the polish, size or reproducibility of the artifact.

A methodological note on evidence quality: the fresh sources gathered here are mostly **label B** (search snippets and abstract listings). Four load-bearing sources were upgraded to **label A** by fetching the primary page in this session (§5). The Phase 17 audits (`research/05`–`research/14`) already contain **A-level** full-text evidence for the saturated measurement/mechanism space; those are cross-referenced, not re-derived.

---

## 2. Current Artifact

**[FACT]** The repository is a Python package (`pyproject.toml`, `name = "agentsec"`, `requires-python = ">=3.11"`) implementing an offline, deterministic, mediated-agent harness plus eight teaching labs, a command-line interface, a documentation site and CI.

### 2.1 Repository purpose

`docs/development.md` (top of file) defines the project as *"Educational, reproducible agent-security infrastructure"* and states *"The package makes no research-novelty claim anywhere; it reimplements established concepts for teaching and reproducible experimentation."* The live site and `labs/README.md` repeat *"educational infrastructure… not a benchmark… no research claim."* **[FACT]**

### 2.2 Architecture (as implemented, not as described)

The core is organised as strict layers, each with a single responsibility. The composition root is `src/agentsec/mvp.py::build_mvp_runner`, which the module docstring states *"constructs objects and never runs an agent loop, executes a tool, takes a policy decision or computes a metric."*

| Layer | Path | Observed responsibility |
|---|---|---|
| Agent loop | `src/agentsec/agent.py` (`class Agent`, `AgentConfig`, `RunStatus`) | Deterministic ReAct-style loop, at most `max_steps` model calls; emits trace events; never executes a tool or evaluates policy itself. |
| Model contract | `src/agentsec/models/base.py` (`ModelAdapter`, `Capabilities`, `ModelInfo`) | Provider-independent protocol; capabilities reported explicitly. |
| Mock model | `src/agentsec/models/mock.py` (`MockModel`, `MockScript`, `script_for`) | *"a test fixture, not an LLM simulation"*; raises `UnsupportedParameter` for `temperature`/`seed`; reports `provider="mock"`, `revision="fixture"`. |
| Mediated tool path | `src/agentsec/tools/gateway.py` (`class ToolGateway`) | The **single** mediated path for every tool call: validate → `tool_requested` → policy → `policy_decision` → (deny / require_approval / allow) → `tool_executed` → `tool_result`. |
| Tool contract | `src/agentsec/tools/base.py` (`Tool`, `ToolSchema`, `ToolResult`, `DeniedResult`, `PendingApprovalResult`) | Typed JSON-Schema input/output; `action()`/`resource()` metadata for authorization. |
| Tools | `src/agentsec/tools/{calculator,fs_sandbox,mock_db,mock_email}.py` | Four sandboxed, in-memory capabilities (`tools/factory.py::TOOL_FACTORIES`). |
| Policy | `src/agentsec/policy/{base,schema,loader}.py` | Flat ordered rules, first match wins, default `deny`; decisions `allow`/`deny`/`require_approval`; one condition key (`outside_task_scope`); strict YAML loading. |
| Trace | `src/agentsec/trace/{schema,recorder,writer,validate,redact}.py` | Versioned (`schema_version = "1.0"`) JSONL event contract; parent-linked events; best-effort pattern redaction + sha256 hashing. |
| Evaluator | `src/agentsec/eval/{base,builtin}.py` (`TraceEvaluator`) | Read-only descriptive counts; module docstring: *"does not execute anything… or compute any score/rating."* |
| Runner | `src/agentsec/experiment/runner.py` (`ExperimentRunner`) | Orchestrates exactly one run; no metrics, no retries. |
| Scenarios | `src/agentsec/scenarios/{base,loader,registry}.py` (`ScenarioDef`, `ExpectedObservation`, `DeclarativeScenario`) | Declarative, read-only; embeds an `ExperimentConfig`; interprets expectations as plain comparisons. |
| Self-check | `src/agentsec/selfcheck.py` | Offline reproducibility check over the canonical labs. |
| CLI | `src/agentsec/cli.py` | `run`, `evaluate`, `inspect`, `labs check`; standard library only. |

### 2.3 The eight labs (LAB-00 … LAB-07)

**[FACT]** `labs/` contains eight lab directories (`LAB-00-setup` … `LAB-07-data-leakage`), each with `README.md` and `config.yaml`; LAB-01…07 additionally carry `scenario.yaml`. There is **no LAB-08** (asserted deliberately in `labs/README.md`).

| Lab | Security concept | Fixture script (`models/mock.py`) | Observed outcome (from `labs/README.md` observables matrix + `scenario.yaml`) |
|---|---|---|---|
| LAB-00 | Setup warm-up | `benign` | run completes; `calculator` allowed/executed/`ok`. |
| LAB-01 | Benign baseline | `benign` | normal lifecycle: request → decision → execution → result → answer. |
| LAB-02 | Direct prompt injection | `direct_redirect` | instruction arrives in the **task**; agent runs an unrelated `calculator` op. |
| LAB-03 | Indirect prompt injection | `indirect_redirect` | instruction arrives in **tool-returned content**; read allowed, write **denied**. |
| LAB-04 | Tool misuse | `tool_misuse` | out-of-scope `fs_sandbox` write **denied**; tool never executes. |
| LAB-05 | Require approval | `approval_read` | legitimate read held: `require_approval`, `pending_approval`, not executed. |
| LAB-06 | Excessive agency | `excessive_agency` | authorized `mock_db` write **executes** though unnecessary; synthetic side effect. |
| LAB-07 | Data leakage | `data_leakage` | authorized read + authorized `mock_email` send; synthetic marker crosses an egress boundary. |

### 2.4 Trace / event model

**[FACT]** `src/agentsec/trace/schema.py::TRACE_EVENT_TYPES` defines a versioned, discriminated union of twelve event types: `run_started`, `agent_input`, `model_request`, `model_response`, `tool_requested`, `policy_decision`, `tool_executed`, `tool_result`, `security_event`, `agent_output`, `run_completed`, `run_failed`. All events share `run_id`, `event_id`, `parent_event_id`, `seq`, `timestamp` (UTC-enforced), `agent_id`, `model`, `scenario`, `event_type`. `trace_json_schema()` normalises the emitted JSON Schema so `event_type` is required on every variant.

### 2.5 Policy decision model

**[FACT]** `policy/schema.py::Decision` is the closed set `{allow, deny, require_approval}`. `PolicyEngine.decide` (`policy/base.py`) returns the first matching rule's decision, else `default_decision` (default `deny`). `ToolGateway.invoke` records a `policy_decision` event **before** execution, makes a `deny` short-circuit to `DeniedResult` (tool never runs), and makes `require_approval` resolve to approved / denied / pending (pending is not executed). The module docstring records two enforced invariants: *"a denied call never invokes the underlying tool"* and *"a call requiring approval never silently becomes an allow."*

### 2.6 Deterministic mock machinery

**[FACT]** `models/mock.py` is a script-driven fixture. Each `MockScript` is an ordered list of `MockStep(matcher, action)` evaluated against the last message; the first match wins. Matching is a pure function of `(message, script)` — no clock, no RNG — so replay is byte-identical. Ten fixtures exist: `benign`, `direct_injection`, `direct_redirect`, `indirect_injection`, `indirect_redirect`, `tool_misuse`, `excessive_agency`, `authorization_violation`, `approval_read`, `data_leakage`. LAB-07's canonical marker `SYNTHETIC-DEMO-DISCLOSURE-A1` is defined in `mock.py::DISCLOSURE_MARKER` and seeded via `labs/LAB-07-data-leakage/config.yaml::sandbox_db_seed`.

### 2.7 Self-check mechanism

**[FACT]** `src/agentsec/selfcheck.py` re-runs each canonical lab through the *existing* stack and compares the result against the lab's *existing* declared `scenario.yaml` expectations. `discover_labs` scans `labs/` for `LAB-<nn>-<slug>` with a `config.yaml`, sorted; `plan_lab_check` redirects `trace_path` into a caller-supplied temp dir; `check_labs` takes a caller-supplied `run_experiment` executor so the module *"never holds the agent/runner execution path itself"*. LAB-00 (no `scenario.yaml`) uses `SMOKE_EXPECTATIONS`. The module docstring states it *"introduces no new metric, no score, no ranking and no security claim."*

### 2.8 CI verification

**[FACT]** `.github/workflows/ci.yml` runs `python -m pytest` and `agentsec labs check` on push/PR. `.github/workflows/docs.yml` builds the MkDocs site with `python -m mkdocs build --strict` and deploys it to GitHub Pages. The two workflows have deliberately separate responsibilities.

### 2.9 Documentation site and GitHub Pages deployment

**[FACT]** `mkdocs.yml` uses `docs_dir: labs`, Material theme, and a fixed nav (Getting Started → Lab Map → Understanding Traces → Practice → Instructor Guide → Local Verification). The instructor-only answer key is built but omitted from nav (`validation.nav.omitted_files: ignore`). GitHub Pages is live at `https://nadeem-majeedch.github.io/agent-security-labs/` (verified in Phase 19 Step 4: Docs run succeeded, deployment `6706505656` at `6802c81`).

### 2.10 Reproducibility properties

**[FACT]** (a) The mock model is clock-free and RNG-free; (b) `cli.py::_run_for_self_check` uses `_fixed_clock()` (`2026-01-01T00:00:00Z`) so self-check replay is byte-identical; (c) `ExperimentRunner.run` calls the agent once and adds no retries; (d) the self-check writes only to a temp directory; (e) CI is offline (no network, no secrets).

### 2.11 Explicit limitations and research-boundary statements

**[FACT]** Boundary statements are present and repeated in `docs/development.md`, `labs/README.md`, `labs/GETTING-STARTED.md`, `labs/LOCAL-VERIFICATION.md`, `labs/INSTRUCTOR-GUIDE.md`, `labs/TRACE-WALKTHROUGHS.md` and `labs/TRACE-READING-EXERCISES.md`. Representative: *"The deterministic mock model is a fixture, so what you observe is the mechanics of a security boundary, not the behaviour of a real model"*; *"It is not a benchmark or a security score"*; LAB-07 *"does not demonstrate autonomous unintended leakage… or real-model exfiltration propensity."*

### 2.12 A documentation defect found during this audit (reported, not fixed)

**[FACT]** The **root `README.md` is stale** and contradicts the repository at HEAD. It states *"This repository currently contains **one research-discovery deliverable only**"* and lists `research/01-landscape-and-gap-analysis.md` as the deliverable; it does not mention the labs, the CLI, the sixteen-plus source modules, the documentation site, CI, or Phases 13–19. It also still lists *"Direction selection and pre-registration"* as *"Not started"* and `LICENSE` / `CITATION.cff` as *"Not yet assigned."* This is a documentation-consistency finding only (no research implication), reported per the "report problems, make no fixes" constraint of this step.

---

## 3. Artifact Contributions

These are contributions to *utility* (teaching, reproducibility, engineering), not to research.

### A. Existing artifact contributions

| # | Contribution | Evidence (path) |
|---|---|---|
| A1 | Educational infrastructure: eight self-contained labs with a fixed pedagogic progression | `labs/LAB-00…LAB-07/` |
| A2 | Trace-based teaching: students reason from a persisted JSONL trace, not from prose | `labs/TRACE-WALKTHROUGHS.md`, `labs/TRACE-READING-EXERCISES.md`, `agentsec inspect`/`evaluate` |
| A3 | Deterministic reproducibility: byte-identical replay of a lab | `models/mock.py` (clock/RNG-free), `cli.py::_fixed_clock` |
| A4 | Declarative scenarios: the expected observations live in data, and a test asserts config≡scenario | `labs/*/scenario.yaml`, `scenarios/base.py::ScenarioDef` |
| A5 | Policy/trace observability: decisions are recorded as first-class events, separate from execution | `tools/gateway.py`, `trace/schema.py` |
| A6 | Offline verification: a single command re-checks all labs | `selfcheck.py`, `agentsec labs check` |
| A7 | Lab-based instruction package: student exercises + instructor guide + answer key (separation of concerns) | `labs/INSTRUCTOR-GUIDE.md`, `labs/TRACE-READING-EXERCISES-ANSWER-KEY.md` |
| A8 | CI reproducibility: tests + self-check on every push/PR | `.github/workflows/ci.yml` |
| A9 | Deployed documentation site | `mkdocs.yml`, `.github/workflows/docs.yml` |
| A10 | A single mediated tool-execution boundary as an architectural invariant (enforced by a test) | `tools/gateway.py`, `tests/test_architecture.py` |

**[INFER]** A1–A10 constitute a genuine, above-average *artifact*. They do not, by themselves, constitute a research contribution: reproducibility, completeness and polish are explicitly **not** novelty (audit brief, "IMPORTANT" clause), and the project's own boundary (Phase 17) says so.

---

## 4. Candidate Research Contributions

Each candidate below is a candidate for the *security-research* sense of "contribution" (new method, framework, formalization, evaluation methodology, dataset, benchmark, measurement approach, mechanism, experimental/educational/reproducibility methodology). None is asserted to be novel.

| # | Candidate claim the repository might tempt a paper to make | What is actually implemented | Preempted? (see §5–§6) |
|---|---|---|---|
| R1 | "A new framework for agent security evaluation" | A layered harness with a mediated gateway and descriptive evaluator | **Yes** — AgentDojo/ASB/REDAgentBench are full research environments; MEDIATION is standard (Progent, CaMeL, FIDES, ActPlane). |
| R2 | "A deterministic/mock agent environment for reproducible experiments" | `MockModel` fixture + fixed clock | **Yes as research** — mock/fixture agents are ubiquitous; determinism is the *opposite* of a contribution for empirical agent security (it removes the phenomenon under study). |
| R3 | "A new policy-enforcement mechanism for agents" | Flat first-match YAML rules, default deny | **Yes, decisively** — symbolic per-call least privilege (Progent), capability/capture-checking (Odersky et al. 2026), OS-level eBPF mediation (ActPlane), taint/IFC (CaMeL, FIDES, NeuroTaint). |
| R4 | "A trace/observability model for agent security" | Versioned JSONL event contract, parent-linked | **Yes** — evidence-tracing/provenance survey (arXiv:2606.04990), TraceCaps, OpenTelemetry-based structural testing of agents. The artifact's schema is a *simplified* instance. |
| R5 | "A new security benchmark" | Eight deterministic labs, no real models, no attack-success measurement | **Yes, and explicitly disclaimed** — `labs/README.md`: *"not a benchmark."* Also the brief forbids benchmark/metric/scores. |
| R6 | "A new measurement approach (exposure vs execution vs egress)" | `policy_decision` vs `tool_executed` vs `tool_result` distinction | **Yes, decisively** — REDAgentBench formalises exactly this decomposition; Pathade et al. analyse it; the project's own boundary forbids claiming it. |
| R7 | "A new educational methodology: trace-first, deterministic agent-security labs" | The labs, exercises, instructor guide, self-check | **Partially open** — the *research* literature (peer-reviewed computing-education work on agent-security labs) appears thin; see §5, §8. This is the only candidate not clearly preempted, and it is *education research*, not security research. |
| R8 | "A reproducibility artifact for agent-security education" | CI + self-check + deterministic replay + docs | **Weak** — reproducibility artifacts exist widely; needs a stated novel property. |
| R9 | "A new detection mechanism" | None | **N/A** — no detector is implemented. |
| R10 | "A new dataset/corpus" | None (synthetic fixtures only) | **N/A** — no corpus exists; Phase 17 records the research corpus as UNIMPLEMENTED. |

**[INFER]** Of ten candidates, nine are either preempted or explicitly out of scope, and the tenth (R7) is an **education-research** candidate whose contribution would be a *study*, not the artifact.

---

## 5. Fresh Literature Landscape

Fresh search, September 2026. Note the evidence caveat: unless marked **A**, entries are **B** (snippet/listing).

### 5.1 Works fetched at the primary source in this session (label A)

| Work | Authors | Year / status | Where | What it contributes | Overlap with this repo | Difference |
|---|---|---|---|---|---|---|
| **AgentDojo** (`arXiv:2406.13352`) | Debenedetti, Zhang, Balunović, Beurer-Kellner, Fischer, Tramèr | 2024, arXiv (v3) — venue not stated on the abstract page | arxiv.org/abs/2406.13352 | *"an extensible environment for designing and evaluating new agent tasks, defenses, and adaptive attacks"*; 97 tasks, 629 security test cases | Tool-using agents, untrusted tool output, prompt-injection scenarios, traces | AgentDojo is a **research evaluation environment with real LLMs**; this repo is an **offline deterministic teaching harness**. Purpose, fidelity and measurement differ in kind. |
| **ASB** (`arXiv:2410.02644`) | Zhang, Huang, Mei, Yao, Wang, Zhan, Wang, Zhang | 2024, **Accepted by ICLR 2025** | arxiv.org/abs/2410.02644 | Formalises/benchmarks attacks+defences: 10 scenarios, 10 agents, >400 tools, 27 attack/defence types, 7 metrics, "highest average attack success rate of 84.30%" | Categories the labs illustrate (prompt injection, memory poisoning, tool misuse) | ASB **measures** attack success across 13 real backbones; this repo **observes mechanics** with a fixture. |
| **REDAgentBench** (`arXiv:2608.10669`) | Chen, Liu, Zhu, Dou, Jiang, Li, Guo, Chen, Zhang | 2026, arXiv (v1, 11 Aug) | arxiv.org/abs/2608.10669 | Executable red-teaming + *"faithful measurement"*; decomposes ASR into **exposure, execution, observation, adjudication**; 1,661 cases; service sandboxes; state-grounded verification | The artifact's `tool_requested`/`policy_decision`/`tool_executed`/`tool_result` distinction is the same *idea* in miniature | REDAgentBench *operationalises and measures* the decomposition across six models and three harnesses; the artifact only *narrates* it deterministically. |
| **"Comparison requires valid measurement…"** | Chouldechova, Cooper, Barocas, Palia, Vann, Wallach | 2025, **NeurIPS 2025 Position Paper (Poster)** | neurips.cc/virtual/2025/poster/121931 | *"conclusions drawn about relative system safety or attack method efficacy via AI red teaming are often not supported by evidence provided by ASR comparisons"*; conditions under which ASRs are/are not comparable | The measurement-validity critique that closed Phase 17 | Establishes that the *measurement* argument is published and settled — i.e., the artifact's determinism cannot supply an ASR claim. |

### 5.2 Works locateable but read only at snippet level (label B)

| Area (brief §3 item) | Work | Year / status | Contributes | Relation to this repo |
|---|---|---|---|---|
| Agent security benchmark | Agent Security Bench (ASB) | ICLR 2025 | see A | adjacent, research |
| Agent security benchmark | MCPTox (`arXiv:2508.14925`) | 2025 preprint | tool-poisoning ASR | tool-trust area; not implemented here |
| Agent security evaluation | AgentDyn; RAS-Eval (`arXiv:2506.15352`) | 2025–2026 | dynamic/realistic agent evaluation | research testbeds |
| Agent security evaluation | CVE-Bench (`arXiv:2503.17332`) | 2025 | real web-exploitation by agents | out of scope |
| Agent security evaluation | SEC-bench (OpenReview `QQhQIqons0`) | 2026 | "first fully automated benchmarking framework for evaluating LLM agents on authentic security engineering tasks" | research benchmark |
| Agent security testbed | *LLM Agent Security Testbed* (community, `pie-script`) | 2026-09 | "an empirical security testbed evaluating prompt injection, confused-deputy vulnerabilities, and tool-calling defenses" | closest surface overlap in the *testbed* sense; community, not peer-reviewed |
| Policy enforcement | Progent; ActPlane (`arXiv:2606.25189`); CaMeL (`arXiv:2503.18813`); FIDES/RTBAS/FORGE; NeuroTaint (`arXiv:2604.23374`) | 2025–2026 | per-call least privilege; OS-level eBPF mediation; taint/IFC | far beyond the artifact's flat rule engine |
| Capability security | Odersky, Zhao, Xu, Bračevac & Pham (`arXiv:2603.00991`) + ACM DOI `10.1145/3786335.3813127` | 2026 | capture-checked capabilities for agents | research mechanism |
| Trace/observability | *From Agent Traces to Trust* (`arXiv:2606.04990`) | 2026 | survey of evidence tracing & execution provenance | the artifact implements a simplified version |
| Trace/testing | *Automated structural testing of LLM-based agents* (`arXiv:2601.18827`) | 2026 | OpenTelemetry traces for agent coverage testing | trace-as-instrument, research |
| Agent-security SoK | *SoK: Bridging Research and Practice in LLM Agent Security* (CMU SEI) | 2025-11 | systematic review; academic + grey literature + case studies | consolidation of the security space |
| Agent-security surveys | *LLM agents security duality* (Springer, `10.1007/s10462-026-11563-0`); *Risk taxonomy* (`arXiv:2605.09721`) | 2026 | taxonomies/lifecycles | background |
| Measurement | Pathade et al. (`arXiv:2609.25173`); Miller (`arXiv:2411.00640`); Li et al. (`arXiv:2605.16282`) | 2024–2026 | MDD/ICC/ESS; taxonomy & consistency of agent-safety benchmarks | the Phase 17 closure material |
| Reproducibility (agents *doing* repro) | CORE-Bench (`arXiv:2409.11363`); REPRO-Bench (**Findings of ACL 2025**); ReplicatorBench (2026); ARA (`arXiv:2605.02651`) | 2024–2026 | benchmarks for AI agents assessing/reproducing published research | different question (agent capability, not a teaching artifact) |
| Standards / framework | OWASP LLM06:2025 Excessive Agency; OWASP GenAI Agentic guidance; ISACA white paper (2026-09) | 2025–2026 | risk taxonomy, controls | the labs teach OWASP-flavoured concepts |
| **Education (grey/industry)** | SANS **SEC546: Securing Agentic AI**; Proofpoint *Certified AI Agent Security Specialist* (2026); Cisco agent-security modules (2026-06); CSA **TAISE Compass** curriculum note (2026-03-27) | 2025–2026 | agent-security curricula/training | **closest educational overlap**; all grey/industry, none peer-reviewed research |
| Education (community) | `llm-sec.dev` interactive labs; `prompttrace.airedlab.com` labs; *Rita Cyber Ed* prompt-injection classroom exercise | 2025–2026 | hands-on LLM-security exercises | teaching resources; **no evaluation of learning outcomes** |
| Education (research, adjacent) | *AI-Augmented Cyber Labs* (ACM, `10.1145/3769694.3771136`, 2025-12); JCERP systematic review of 412 cybersecurity-education interventions (2026); Hertz & Jump, *Trace-Based Teaching in Early Programming Courses* (SIGCSE 2013) | 2013–2026 | cybersecurity-education methods; trace-based teaching precedent | **methods** exist; the *specific* object (deterministic agent-security labs) was not found as peer-reviewed research |

**Search-coverage note [INFER]:** across all twenty brief areas, I found **no peer-reviewed paper whose contribution is a deterministic, trace-first, offline teaching laboratory for LLM-agent security**. The educational space is dominated by grey/industry/community material; the research space (AgentDojo, ASB, REDAgentBench, Progent, CaMeL, ActPlane, the tracing survey) is dominated by *evaluation environments* and *mechanisms*, not teaching artifacts. That observation is the seed of the only candidate gap (§8), and it is a **gap in computing-education research**, not in agent-security research.

---

## 6. Prior Work Overlap

Recheck of the Phase 17 load-bearing works (all characterised in `research/05`–`research/12`; the four fetched here are marked **A**). Classification key: **A** duplicate · **B** educational version of an existing concept · **C** recombination without demonstrated novelty · **D** potentially distinct · **E** exposes a gap.

| Work (as rechecked) | Repo relation | Class |
|---|---|---|
| **AgentDojo** (A, `2406.13352`) | not a duplicate; the repo has no real-LLM environment | **B** |
| **ASB** (A, ICLR 2025) | the labs teach ASB-style concepts (injection, tool misuse, excessive agency) without measuring | **B** |
| **REDAgentBench** (A, `2608.10669`) | the repo's event distinction parallels REDAgentBench's exposure/execution/observation/adjudication decomposition | **B** (and **A** if the repo *claimed* the decomposition — it does not) |
| **NeurIPS 2025 ASR-validity position paper** (A) | the repo makes no ASR claim, so it neither duplicates nor conflicts | **E** (a boundary, not a gap the repo fills) |
| **CAISI / NIST `agentdojo-inspect`** (B) | a public harness exists; the repo does not compete with it | **B** |
| **REPRO-Bench** (B, ACL 2025) | agents reproducing research ≠ reproducible teaching labs | not overlapping |
| **AI4Reproducibility / ReAgent / Traverse+Scout / Agentic Garden of Forking Paths / ScientistOne Chain-of-Evidence** (B, per `research/09`) | all are agents *performing* reproducibility; the repo is a *reproducible artifact* | not overlapping |
| **P-Bench / Fisher-R1** (B) | performance/evaluation of agents; unrelated to teaching | not overlapping |
| **MCPTox / tool-poisoning family** (B) | the repo has no tool-poisoning lab | not overlapping |
| **Progent, ActPlane, CaMeL, FIDES, RTBAS, FORGE, NeuroTaint, Odersky et al.** (B) | the repo's policy engine is a simplification of this family | **C** |
| **Agent-trace/observability survey (`2606.04990`), TraceCaps, agent structural testing (`2601.18827`)** (B) | the repo's trace schema is a simplified instance | **B** |
| **`llm-sec.dev` / `prompttrace` / Rita Cyber Ed** (B/C) | closest *educational* surface overlap; none PeerReviewed; none with a learning-outcomes evaluation | **B** (as teaching resources), **D** (as a research object) |
| **SANS SEC546 / Proofpoint / Cisco / CSA TAISE** (B/C) | industry training with the same concepts; no research evaluation | **B** |
| **Hertz & Jump, SIGCSE 2013** (B) | *methodological* precedent for trace-based teaching, in programming courses | **D** (precedent, not a duplicate) |

**[FACT] + [INFER]:** the user-facing material of every earlier audit is unchanged — the *security-research* space remains saturated (Phase 12: "the surviving research direction count is zero"). The one line of attack the earlier phases never ran is the **education** line, which Phase 12 explicitly records as *"NOT TESTED rather than promising"* (`research/12`, Strategy C).

---

## 7. Claim-by-Claim Novelty Test

The ten-question test is applied to the only candidates that survive §4 as even *arguable*: **R7** (trace-first deterministic agent-security educational methodology), **R8** (reproducibility artifact), and — for completeness — **R6** (the exposure/execution/egress distinction), which is the artifact's strongest technical idea.

### 7.1 R6 — the event decomposition (request vs decision vs execution vs result)

1. **Proposed contribution:** a formal treatment/measurement built on separating "asked" from "authorized" from "executed" from "resulted".
2. **Prior work:** REDAgentBench (A) formalises and measures exactly this (exposure → execution → observation → adjudication); Pathade et al. (B) analyse ASR validity; the NeurIPS position paper (A) establishes the measurement-validity conditions.
3. **Technically different?** No. The artifact *records* the distinction; REDAgentBench *defines, measures and validates* it.
4. **Substantive or implementation?** Implementation/documentation only.
5. **Empirical evidence?** None — the repo's "evidence" is a deterministic fixture.
6. **Reproducible by another researcher?** The *determinism* is trivially reproducible but proves nothing about agents.
7. **Experiment required:** measure the gap between exposure/execution/egress across real models and harnesses.
8. **Does the repo contain it?** No.
9. **What would be needed:** a real stochastic adapter + corpus + host-verified side effects.
10. **Reopens Phase 17?** **Yes** — this is the measurement direction that was closed.
**Verdict:** preempted; not a contribution; and pursuing it reopens the closed direction. **DO NOT pursue.**

### 7.2 R8 — the reproducibility artifact

1. **Contribution:** a reproducible, offline, deterministic agent-security teaching harness.
2. **Prior work:** CORE-Bench / REPRO-Bench / ReplicatorBench / ARA (B) are reproducibility *benchmarks for agents*; the agent-security SoK (B) catalogues harnesses; AgentDojo (A) ships an extensible environment with released code.
3. **Technically different?** Only in *purpose* (teaching vs evaluation).
4. **Substantive?** Purpose difference is real but *not* a research technique; reproducibility is a property, not a finding, and the brief's "IMPORTANT" clause says reproducibility does not constitute novelty.
5. **Empirical evidence?** None about learning or about agents.
6. **Reproducible?** Yes — that is the point, but reproducibility alone is not a claim.
7. **Experiment required:** an evaluation (learning outcomes, or a comparative study against an alternative teaching design).
8. **In the repo?** No study exists.
9. **Needed:** study design, participants, instruments, ethics approval.
10. **Reopens Phase 17?** No (it is a different, educational question).
**Verdict:** not a security-research contribution; a possible *artifact-paper* ingredient **only if** paired with an evaluation.

### 7.3 R7 — trace-first deterministic agent-security labs (the education candidate)

1. **Proposed contribution:** a teaching methodology in which students learn agent-security concepts by reading a deterministic trace, with the concepts sequenced (baseline → injection → tool misuse → approval → excessive agency → data leakage) and separated by *events*, not severity.
2. **Prior work:** *hands-on LLM-security labs* exist widely as community/industry material (`llm-sec.dev`, `prompttrace`, Rita Cyber Ed, SANS SEC546, Proofpoint, Cisco, CSA TAISE) (B/C). Peer-reviewed cybersecurity-education research is mature (*AI-Augmented Cyber Labs* ACM 2025; JCERP 2026 review) (B). *Trace-based teaching* has methodological precedent (Hertz & Jump, SIGCSE 2013) (B). **No peer-reviewed work with this specific object was located.**
3. **Technically different?** The object (deterministic, offline, trace-first, no API keys) is a *design choice* that is defensible pedagogically (no cost, no variance, safe) and not obviously duplicated in the literature.
4. **Substantive or implementation?** This is where the classification turns: the *artifact* is substantive as an engineering/pedagogy object, but the *research contribution* would be the **evidence that this design improves learning**, which does not exist.
5. **Empirical evidence?** **None.** No students, no pre/post, no comparison, no instrument. `labs/` states explicitly that the labs "make no research claim."
6. **Reproducible by another researcher?** The artifact is (CI + self-check), but the *claim* cannot even be tested without an evaluation.
7. **Experiment required:** an educational study (e.g., a pre-registered pre/post or randomised comparison of trace-first vs conventional instruction, with a validated instrument).
8. **In the repo?** No.
9. **Needed:** study design, recruitment, ethics/IRB, validated instrument, controls for prior experience — a substantial *new* project, mostly outside the current codebase.
10. **Reopens Phase 17?** No. It is a computing-education question, distinct from the closed security-measurement direction.
**Verdict:** **the only surviving, non-preempted candidate**, and it is an *education-research* candidate requiring a study the repository does not contain.

### 7.4 Aggregate result of the test

**[INFER]** No candidate satisfies the test as a *security* contribution. The single candidate that survives is educational and study-dependent.

---

## 8. Paper-Type Analysis

For each plausible type: what would be claimed, what evidence is required, what exists, what is missing, and whether substantial new implementation is needed. No type is recommended on attractiveness.

| Type | Claimed contribution | Evidence required | Evidence present | Evidence missing | New implementation |
|---|---|---|---|---|---|
| **Software / artifact paper** | "A novel design for a mediated, deterministic agent-security teaching harness" | A design insight not already standard + adoption/utility evidence | Mediated gateway, declarative scenarios, self-check, CI, docs | A non-standard design claim; any evaluation or adoption data | Medium (to establish a defensible design claim) |
| **Systems / tool paper** | "A new tool for agent security" | A new mechanism, benchmarked | none (mechanism space saturated: §6) | almost everything; the mechanism is preempted | High, and preempted |
| **Cybersecurity-education paper** | "Trace-first deterministic labs improve student understanding of agent security" | A learning-outcomes study with controls/instrument; ethics approval | A mature, deployable artifact ready to *serve* as the intervention | The entire study (design, participants, instrument, analysis) | Medium–high (study, not codebase) |
| **Educational-technology paper** | as above, framed around tooling/pedagogy | as above + tooling evaluation | as above | as above | Medium–high |
| **Reproducibility / artifact paper (journal software section)** | "A reproducible artifact for agent-security education" | A stated novel reproducible property + evaluation/citation | Determinism, self-check, CI, live docs | A stated property beyond "we are reproducible"; an evaluation | Low–medium (framing + evaluation) |
| **Experience report (e.g., ITiCSE/SIGCSE)** | "What we learned designing eight deterministic agent-security labs" | A coherent design rationale + honest reflection + (ideally) light evaluation | Strong: the artifact, the sequencing, the boundary statements, the instructor material | A written rationale and any evaluation; venue fit | Low (writing + light evaluation) |
| **Dataset / resource paper** | — | — | **none** (no dataset/corpus) | — | N/A |

**[INFER]** Only three types are live: **experience report** (lowest barrier, honest fit), **cybersecurity-education paper** (highest ceiling, requires a real study), and **reproducibility/artifact paper** (requires a defensible property beyond reproducibility). None is a *security* research paper. The dataset/resource type is not available because the repository contains no dataset.

---

## 9. Research Gaps

Exactly one gap is identified, and it is **not** a security gap.

### Gap E1 — Peer-reviewed, evidence-based pedagogy for LLM/agent security

- **Existing state of the art.** Hands-on LLM-security labs and agent-security curricula are abundant but **grey/industry/community** (llm-sec.dev; prompttrace; Rita Cyber Ed; SANS SEC546; Proofpoint; Cisco; CSA TAISE). Evaluation methodology for cybersecurity education is mature (*AI-Augmented Cyber Labs*, ACM 2025; JCERP 2026 PRISMA review of 412 interventions). Trace-based teaching has precedent (Hertz & Jump, SIGCSE 2013). Research agent-security environments (AgentDojo, ASB, REDAgentBench) are **not** teaching interventions and carry no pedagogical claims.
- **Missing capability.** Peer-reviewed **evidence** on whether (and how) trace-first, deterministic, offline agent-security labs affect student understanding of agent-security concepts such as policy-before-execution, approval vs deny, excessive agency, and authorization vs confidentiality.
- **Why it matters.** The security community repeatedly documents conceptual confusion (request ≠ execution; allow ≠ security; authorized ≠ confidential). The artifact already encodes these as teaching distinctions; whether the design *works* is untested anywhere in the located literature.
- **Proposed research question (shape only, not designed here).** "Does a trace-first deterministic agent-security lab sequence improve novice understanding of the request/decision/execution/result distinctions relative to a conventional reading-based treatment?"
- **Required methodology.** A computing-education empirical design (pre-registered), with a validated instrument.
- **Required experiment.** Pre/post or randomised comparison with a control condition; ideally a delayed retention check.
- **Required data.** Human participants (students), background survey, instrument responses.
- **Required baselines.** A conventional instruction condition (reading/written case study) or a non-trace hands-on condition.
- **Expected threats to validity.** Small-n; confounds (prior security/LLM experience, motivation); instrument validity; novelty/Hawthorne effects; single-institution generalisability; the deterministic fixture may *simplify* concepts so much that transfer to real, stochastic agents does not follow.

**[OPEN]** Whether E1 is genuinely unoccupied at the peer-reviewed level cannot be fully settled by a snippet-level search; a **full-text, venue-targeted** review (SIGCSE/ITiCSE/ICER/TOCE; ACM DL; IEEE Xplore; Scopus) is required before any claim.

### Non-gaps (explicitly rejected, not reframed)

- **Security mechanism / detector / defence:** preempted (§6).
- **Benchmark / metric / measurement:** preempted and additionally forbidden by the standing boundary.
- **Reproducibility-as-novelty:** reproducibility is a property, not a finding.
- **Attack/behaviour characterisation with the current harness:** impossible without a real adapter; and the adapter is the gate that Phase 17 says must precede any audit.

---

## 10. Evidence Currently Available

**[FACT]**
- A complete, tested artifact: `PYTHONPATH=src py -m pytest` → **694 passed**; `agentsec labs check` → **8/8 labs passed** (exit 0); `py -m mkdocs build --strict` → exit 0; CI and Pages green; live site healthy (Phase 19 Step 4).
- Three executable, byte-identical reproducibility mechanisms: clock-free mock, fixed-clock self-check, one-run-per-experiment.
- A buildable, self-contained teaching intervention deployable in any classroom offline.
- Instructor material, sequentially ordered labs, and explicit boundary statements (ready for honest framing).
- A recorded, internally consistent research posture (`docs/development.md`, `research/05`–`research/14`): NO-GO, with the deterministic-fixture boundary stated.

**[FACT] What is *not* evidence of a research contribution:** passing CI, byte-identical replay, a polished GH-Pages site, 694 tests. These are engineering/reproducibility facts.

---

## 11. Evidence Missing

**[FACT] + [INFER]**
- **Any empirical result about a real model.** No adapter, no corpus, no provider — recorded UNIMPLEMENTED in Phase 17.
- **Any learning-outcomes evidence.** No participants, instrument, protocol, or analysis (the E1 study does not exist).
- **Any measurement evidence** (ASR/utility/cost) — absent by design and forbidden by the boundary.
- **A novelty check of the education space at full text** — this audit is snippet-level for the education sources (§5.2).
- **A comparable-artifact analysis** establishing what this artifact does that no existing teaching resource does.
- **For an artifact paper:** a stated non-reproducibility property and/or evaluation/adoption data.
- **Housekeeping for publication:** `LICENSE`, `LICENSE-DATA`, `CITATION.cff`, a dual-use payload policy — all still unassigned (root `README.md`), and the **root README is stale** (§2.12).

---

## 12. Research-Boundary Check

The audit explicitly verifies that **none** of the following is claimed, and that the Phase 17 boundary is intact.

| Must not be claimed | Status in this audit |
|---|---|
| Deterministic mock behaviour represents real LLM behaviour | **Not claimed.** §2.6, §2.11, §7 record the fixture boundary verbatim from `docs/development.md`. |
| Lab traces measure model propensity | **Not claimed.** §2.11 quotes `docs/development.md`: *"evaluator counts are fixture outcomes, not model propensities."* |
| Policy decisions establish security effectiveness | **Not claimed.** §2.5; the labs teach *authorization ≠ necessity ≠ confidentiality*. |
| LAB-07 demonstrates real-world exfiltration | **Not claimed.** §2.11 quotes the LAB-07 boundary; §7.1 does **not** elevate it. |
| The labs constitute a benchmark | **Not claimed.** `labs/README.md`: *"not a benchmark."* |
| The self-check is a security metric | **Not claimed.** `selfcheck.py` docstring: *"no new metric, no score, no ranking and no security claim."* |
| Passing CI establishes security | **Not claimed.** §10 lists CI as an engineering fact only. |
| Educational exercises constitute empirical evidence | **Not claimed.** §7.3 finds **no** empirical evidence; the exercises are materials, not findings. |

**[FACT]** Phase 17 remains **CLOSED** as recorded in `docs/development.md`; this audit **does not reopen** it. It identifies only an **education-research** question (E1), which is orthogonal to the closed *security-measurement* direction and was already flagged as **NOT TESTED** by Phase 12. No claim of novelty is made for E1.

**[INFER] Boundary interaction to flag for the reader:** if E1 were ever pursued, two of its threats (§9) touch the closed direction — the deterministic fixture simplifies what real, stochastic agents do, so a pedagogical result would *not* transfer automatically to security-research claims. That is a reason to keep the two questions separate, not to reopen Phase 17.

---

## 13. Overall Evidence-Based Classification

**ARTIFACT / EDUCATIONAL PAPER CANDIDATE**

**Why this classification is the only one supported by the evidence:**

- **Not RESEARCH-READY.** There is no empirical result, no real model, and no evaluation; the project's own Phase 17 section records NO-GO and states *"no novelty claim is made anywhere."*
- **Not RESEARCH-PROMISING BUT INCOMPLETE** in the sense the brief intends (a plausible *research contribution* missing its experiments). There is no security-research claim whose experiments are simply pending; the mechanism, benchmark and measurement spaces are preempted, and the repo is explicitly deterministic by design. The only "incomplete" thing is an *education* study, which is a different project rather than a missing experiment on an existing claim.
- **ARTIFACT / EDUCATIONAL PAPER CANDIDATE** fits precisely: *"the main contribution is the educational/reproducibility artifact itself rather than a new security method or empirical finding."* The artifact is real, mature and deployable (§3), and it is a **candidate** for a paper of the *education / artifact / experience-report* kind (§8) — **contingent on** (i) a full-text novelty check of the education space and (ii) an evaluation, neither of which exists today. It is a candidacy, not a ready paper.
- **NOT CURRENTLY PAPER-WORTHY** would understate the artifact: as a *security* paper it is not worthy, but as an *education/artifact* object it has credible potential. The classification above states this without overclaiming; the "candidate" qualifier and §11 carry the negative finding explicitly.

**Bottom line.** The repository is, at HEAD, a **mature educational/reproducibility artifact** with **no current research contribution in the security sense**, and **one unoccupied but un-evidenced education-research direction** (E1). This is consistent with — and does not disturb — the Phase 17 NO-GO.

---

## 14. Recommendation for Phase 20 Step 2

**Recommended (evidence-based): do not draft a research paper now.** The evidence does not support a security-research contribution, and the artifact contains no empirical study. Drafting a paper in this state would require manufacturing a claim — the one thing every prior phase forbade.

**Step 2, option (recommended) — "Hold and document".** Keep the repository in educational/reproducibility mode (consistent with Phase 17), and take the low-risk, honest actions that do not require a research claim:
1. Record the classification and the single gap (E1) in the project's own record (this file does that).
2. Fix the **stale root `README.md`** (§2.12) and, if a public release is intended, add `LICENSE` / `CITATION.cff` — *nothing here is a research claim*.
3. Stop. Do not reopen Phase 17.

**Step 2, option (gated alternative) — "Test the one open question, as education research".** Only if publication is genuinely wanted, and **only** through a gate, in this order:
1. A **full-text, venue-targeted, hostile literature audit** of the *computing-education* space (SIGCSE/ITiCSE/ICER/TOCE, ACM DL, IEEE Xplore, Scopus) to test whether E1 is truly unoccupied. If prior art is found, stop.
2. If E1 survives, **pre-register** an educational study and obtain ethics/IRB approval **before** any data collection.
3. Run the study; analyse learning outcomes; *then* decide on a paper type (§8: experience report, cybersecurity-education paper, or artifact paper).
4. Keep the security-measurement direction **closed** throughout; the education study must not be presented as evidence about real agent/model security behaviour.

**Do not (this step or next):** write the paper; create `CITATION.cff` or a Zenodo release; implement the real model adapter or a corpus; add metrics, benchmarks, detectors or defences; claim novelty for the artifact or for E1.

**One-sentence Step 2 recommendation:** *Treat the repository as an educational/reproducibility artifact, document the classification and gap E1, and — only if publication is pursued — gate any education study behind a full-text literature audit and IRB approval, without reopening the closed security research direction.*

---

## Appendix — Sources consulted in this pass

**Label A (fetched at the primary source this session):**
1. Debenedetti, Zhang, Balunović, Beurer-Kellner, Fischer, Tramèr — *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents* — arXiv:2406.13352 (2024). `https://arxiv.org/abs/2406.13352`
2. Zhang, Huang, Mei, Yao, Wang, Zhan, Wang, Zhang — *Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents* — arXiv:2410.02644; **Accepted by ICLR 2025**. `https://arxiv.org/abs/2410.02644`
3. Chen, Liu, Zhu, Dou, Jiang, Li, Guo, Chen, Zhang — *REDAgentBench: Executable Red Teaming and Faithful Measurement of LLM Agent Systems* — arXiv:2608.10669 (2026). `https://arxiv.org/abs/2608.10669`
4. Chouldechova, Cooper, Barocas, Palia, Vann, Wallach — *Comparison requires valid measurement: Rethinking attack success rate comparisons in AI red teaming* — **NeurIPS 2025 Position Paper (Poster)**. `https://neurips.cc/virtual/2025/poster/121931`

**Label B/C (snippet/listing only; not quotable as figures):** MCPTox (`arXiv:2508.14925`); RAS-Eval (`arXiv:2506.15352`); CVE-Bench (`arXiv:2503.17332`); AgentDyn; SEC-bench (OpenReview `QQhQIqons0`); *LLM Agent Security Testbed* (pie-script, 2026-09); Progent; ActPlane (`arXiv:2606.25189`); CaMeL (`arXiv:2503.18813`); FIDES/RTBAS/FORGE; NeuroTaint (`arXiv:2604.23374`); Odersky et al. (`arXiv:2603.00991`; ACM `10.1145/3786335.3813127`); *From Agent Traces to Trust* (`arXiv:2606.04990`); TraceCaps; *Automated structural testing of LLM-based agents* (`arXiv:2601.18827`); *SoK: Bridging Research and Practice in LLM Agent Security* (CMU SEI, 2025-11); *LLM agents security duality* (Springer `10.1007/s10462-026-11563-0`); *Security Risks in Tool-Enabled AI Agents* (`arXiv:2605.09721`); Pathade et al. (`arXiv:2609.25173`); Miller (`arXiv:2411.00640`); Li et al. (`arXiv:2605.16282`); CORE-Bench (`arXiv:2409.11363`); REPRO-Bench (Findings of ACL 2025); ReplicatorBench (2026); ARA (`arXiv:2605.02651`); OWASP LLM06:2025 Excessive Agency; ISACA white paper (2026-09); SANS SEC546; Proofpoint AI Agent Security Specialist (2026); Cisco agent-security modules (2026-06); CSA TAISE Compass (2026-03-27); `llm-sec.dev`; `prompttrace.airedlab.com`; *Rita Cyber Ed*; *AI-Augmented Cyber Labs* (ACM `10.1145/3769694.3771136`, 2025-12); JCERP cybersecurity-education systematic review (2026); Hertz & Jump — *Trace-Based Teaching in Early Programming Courses* — SIGCSE 2013.

**Repository sources:** `docs/development.md` (§"Research status (Phase 17 — CLOSED, research NO-GO)"); `labs/README.md`; `labs/LAB-07-data-leakage/{config,scenario}.yaml`; `src/agentsec/{agent,mvp,cli,selfcheck}.py`; `src/agentsec/models/{base,mock,schema}.py`; `src/agentsec/tools/{base,gateway,factory}.py`; `src/agentsec/policy/{base,schema,loader}.py`; `src/agentsec/trace/{schema,redact}.py`; `src/agentsec/eval/{base,builtin}.py`; `src/agentsec/experiment/{config,runner}.py`; `src/agentsec/scenarios/{base,loader,registry}.py`; `.github/workflows/{ci,docs}.yml`; `mkdocs.yml`; `pyproject.toml`; `README.md`; `research/05`, `research/08`, `research/12`.
