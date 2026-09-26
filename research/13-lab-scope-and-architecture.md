# 13 — AI Agent Security Lab: Scope, Architecture & MVP Definition (Phase 13)

**Status: PHASE 13 COMPLETE — LAB SCOPE: MINIMAL**

**Date:** 26 September 2026
**Premise (from Phase 12):** *No research commitment is recommended.* The Lab is therefore built as **educational + reproducible open-source infrastructure**, not as a paper. **No research-novelty claim is made anywhere in this document.**
**This phase produces architecture and scope only.** No source code, no GitHub Pages site, no datasets, no commits.

**Standing rules honoured:** no novelty claims; established security concepts only; no proprietary-model dependency; no unrestricted real-world tools; no production deployment; MVP kept small; educational demonstrations clearly separated from research experiments; primary-source references are by registry ID (see `research/tables/sources.csv`).

---

## Task 1 — The Lab's boundary

**A. What the Lab IS.**
A small, provider-independent Python toolkit and a set of guided labs that let a learner run a *simulated* LLM agent, watch its execution trace, reproduce a *known* security problem, apply a *known* defense, and understand the outcome. It reuses established security concepts and, where useful, established benchmark case styles (R01 AgentDojo, R04 InjecAgent, R02 ASB) rather than inventing new ones.

**B. What the Lab IS NOT.**
Not a new benchmark; not a new security mechanism; not a production agent framework; not a frontier-model evaluation suite; not a comprehensive security-coverage claim; not an autonomous real-world agent.

**C. Primary users.** BS students with a programming background, MS/PhD students, security practitioners, and instructors. Two modes: **Student Mode** (guided labs, mock tools) and **Research Mode** (configuration-driven experiments, trace analysis).

**D. Educational objectives.**
1. Explain an agent architecture and its trust boundaries.
2. Read and interpret an execution trace.
3. Reproduce canonical agent-security problems.
4. Apply a defense and reason about its utility cost.
5. Distinguish attack *success* from attack *attempt*.
6. Understand why a result is or is not reproducible.

**E. Research/experimental objectives (secondary).**
Provide instrumentation (pinned model ids, seeds where supported, JSONL traces, cost logging) sufficient to run *controlled* experiments later — **without** claiming any result is novel.

**F. Non-goals / scope-creep guards.** The initial Lab explicitly excludes: production-grade orchestration, large-scale benchmarking, frontier-model evaluation, autonomous real-world actions, commercial deployment, comprehensive-security claims, and novel security algorithms. Justification for each is in Task 19.

---

## Task 2 — The MVP

Smallest set of components that demonstrates the full security lifecycle:

```
AGENT → INPUT → MODEL → TOOL/MEMORY → EXECUTION TRACE
      → ATTACK → OBSERVATION → DEFENSE → RE-EVALUATION
```

| Component | Purpose | Complexity | Dependencies | Educational value | Research value | MVP? |
|---|---|---|---|---|---|---|
| Reference agent + loop | Run a multi-step task | Low | Python stdlib | High | Low | **Yes** |
| Model adapter (provider-independent) | Call any configured model | Low-Med | `httpx` | Medium | Medium | **Yes** |
| Deterministic mock model | Test without API | Low | none | Low | Medium | **Yes** |
| Tool gateway + 3 mock tools | Mediated tool access | Medium | stdlib | High | Medium | **Yes** |
| JSONL trace recorder | Observable execution | Low | stdlib | High | High | **Yes** |
| Attack runner | Inject one payload | Low | stdlib | High | Medium | **Yes** |
| Policy engine (defense) | Mediate tool calls | Medium | stdlib | High | Medium | **Yes** |
| Evaluator | Score a trace | Medium | stdlib | High | High | **Yes** |
| Experiment config (YAML) | Reproducible runs | Low | `PyYAML` | Medium | High | **Yes** |
| CLI | Run labs/experiments | Low | stdlib | Medium | Low | **Yes** |
| Memory store | Phase-2 module | Medium | stdlib | High | Medium | No (Phase 2) |
| RAG retriever | Phase-2 module | Medium | stdlib | High | High | No (Phase 2) |
| Web UI (Streamlit) | Optional visualization | Low | Streamlit | Medium | Low | No (optional) |

---

## Task 3 — Security modules and sequencing

Full classification in `research/tables/lab-module-matrix.csv`. Summary:

| ID | Module | Phase | Rationale |
|---|---|---|---|
| M01 | Prompt Injection | **MVP** | Simplest reproducible failure; prerequisite for everything |
| M02 | Indirect Prompt Injection | **MVP** | Canonical agent risk (R01, R04); needs only a mock retrieved document |
| M03 | Tool Misuse | **MVP** | Exercises the tool gateway, the Lab's central abstraction |
| M04 | Excessive Agency | **MVP** | Motivates the policy engine without new infrastructure |
| M13 | Permission / Authorization Controls | **MVP** | The defense half of the MVP lifecycle |
| M05 | Memory Poisoning | Phase 2 | Needs a persistent store; adds state beyond MVP |
| M06 | Data Leakage | Phase 2 | Needs a mock sink + secret handling; richer evaluation |
| M07 | RAG Poisoning | Phase 2 | Needs a retrieval layer |
| M08 | MCP / Tool Trust | Phase 2 | Needs a mock tool-server abstraction (R06) |
| M10 | Runtime Monitoring | Phase 2 | Needs a trace store + rules; builds directly on MVP traces |
| M12 | Output Validation | Phase 2 | Small, but better after traces/monitoring exist |
| M09 | Multi-Agent Delegation | Phase 3 | Requires multiple agents; high complexity |
| M11 | Recovery / Rollback | Phase 3 | Requires a state store and checkpointing; niche |

**Out of scope (all phases):** novel mechanism design, distributed/byzantine multi-agent protocols, model-weight attacks, supply-chain signing infrastructure.

---

## Task 4 — Educational sequence

| Level | Title | Objectives | Concepts | Prerequisites | Outcome |
|---|---|---|---|---|---|
| L0 | Agent fundamentals | Describe an agent loop and trust boundaries | controller, model, tools, context | Python basics | Can run the reference agent |
| L1 | Execution and tracing | Read a JSONL trace | events, causality, redaction | L0 | Can annotate a trace |
| L2 | Prompt injection | Reproduce direct injection | instruction vs data | L1 | A working direct injection |
| L3 | Tool security | Exploit/mitigate over-permissive tools; indirect injection | tool scope, argument validation | L2 | Attack then defend a tool call |
| L4 | Data & memory security | Trace leakage; poison memory | secrets, provenance, persistence | L3 | Leakage and poisoning demos |
| L5 | RAG security | Poison a small corpus | retrieval, grounding, provenance | L4 | Poisoned-corpus demonstration |
| L6 | Defensive controls | Apply least-privilege policy and output checks | mediation, allow-lists | L3 | Measured utility/security trade-off |
| L7 | Monitoring & evaluation | Detect and score security events from traces | detection rules, metrics, intervals | L1, L6 | A monitor with measured precision/recall |
| L8 | Advanced agent security | Delegation, recovery, monitoring-aware attacks | capability tokens, rollback hazards | L4, L7 | An advanced scenario write-up |
| L9 | Research experiments | Design a controlled experiment | controls, repetition, reproducibility | all | A reproducible experiment directory |

Progress is gated by prerequisites; the sequence deliberately delays multi-agent and recovery until the fundamentals are understood.

---

## Task 5 — Laboratory scenarios

Full record in `research/tables/lab-scenario-matrix.csv`. Each scenario specifies scenario, learning objective, setup, attack/experiment, expected observation, questions, extension exercise and safety note. The set:

- **LAB-00** Lab setup and first benign run (L0)
- **LAB-01** Observe a benign agent execution (L1)
- **LAB-02** Direct prompt injection (L2)
- **LAB-03** Indirect prompt injection via retrieved content (L3)
- **LAB-04** Exploit an over-permissive tool (L3)
- **LAB-05** Unauthorized data exposure (L4, Phase 2)
- **LAB-06** Memory poisoning (L4, Phase 2)
- **LAB-07** RAG poisoning (L5, Phase 2)
- **LAB-08** Apply an authorization policy (L6)
- **LAB-09** Compare vulnerable vs defended agents (L6)
- **LAB-10** Inspect and classify execution traces (L1/L7, Phase 2)
- **LAB-11** Runtime monitoring and detection (L7, Phase 2)
- **LAB-12** Controlled experiment: repetition and variance (L9, Phase C)
- **LAB-13** Recovery and rollback hazards (L8, Phase 3)
- **LAB-14** Design an original experiment (L9, Phase C)

Every scenario uses mock tools, synthetic data and clearly fake secrets; none touches a real account.

---

## Task 6 — Reference agent architecture

Minimal and explicit; interfaces are Python protocols, not a framework.

```
User / Scenario
      │
      ▼
AgentController ──► ContextBuilder ──► ModelAdapter ──► LLM (any provider or mock)
      │                                     ▲
      │                                     │
      ├──► Planner (simple: model-driven, no framework)
      │
      └──► ToolGateway ──► PolicyEngine ──► Tool(s) [sandboxed]
                  │              │
                  ▼              ▼
             TraceRecorder (JSONL, append-only)

Optional (Phase 2+): MemoryStore, Retriever, Monitor
```

**Technology choices (justified in Task 22):** Python 3.11+, `httpx` (HTTP), `pydantic` (config/schema validation), `PyYAML` (configs), `jsonschema` (trace validation). CLI first; **Streamlit optional and non-MVP**. Storage: JSONL traces; SQLite optional index. No LangChain/LlamaIndex/AutoGen/CrewAI in the MVP — they add hidden behaviour that obscures the teaching points.

Interfaces:
- `ModelAdapter.complete(messages, *, temperature, seed, tools) -> ModelResponse`
- `Tool.run(args, ctx) -> ToolResult`
- `PolicyEngine.decide(tool_name, args, ctx) -> Decision(allow|deny|scope)`
- `TraceRecorder.emit(event: Event)`
- `Evaluator.score(trace) -> Result`

---

## Task 7 — Trace format

Append-only **JSONL**, one event per line, validated with `jsonschema`.

| Field | Meaning | Required | Notes |
|---|---|---|---|
| `run_id` | Unique experiment run | **Mandatory** | Groups events |
| `seq` | Monotonic event index | **Mandatory** | Ordering |
| `timestamp` | ISO-8601 UTC | **Mandatory** | Reproducibility |
| `event_type` | e.g. `model_call`, `tool_call`, `policy_decision`, `memory_read/write`, `security_event`, `final_output` | **Mandatory** | Core discriminator |
| `model_id` | Exact model identifier + revision | Conditional | On model events |
| `model_params` | temperature/seed **if supported**, else `unsupported` | Conditional | Honesty about control |
| `input_ref` | Hash/pointer to prompt (not raw secrets) | Optional | Privacy |
| `retrieved_context` | Doc ids + hashes | Optional | Phase 2 |
| `tool_name`, `tool_args` | Tool request | Conditional | Redact secrets |
| `policy_decision` | allow/deny/scope + rule id | Conditional | Defense record |
| `tool_result` | Result hash/summary | Conditional | Avoid raw sensitive data |
| `memory_op` | read/write + key | Optional | Phase 2 |
| `model_response` | Response hash + truncated text | Conditional | Redaction policy applies |
| `security_event` | label + severity | Optional | Produced by monitor |
| `defense_decision` | applied / not applied | Optional | From evaluator |
| `final_output` | Task result | Mandatory | Terminal event |
| `labels` | ground truth for teaching | Optional | Off by default in real experiments |

**Reproducibility:** the trace records model id, params, prompt/config versions and timestamps. **Privacy:** no secrets, no raw PII, redaction on by default, prompts stored as hashes unless explicitly retained. **Mandatory vs optional:** identifiers and event types are mandatory; all content-bearing fields are optional/redacted so the Lab can run in a privacy-preserving mode.

---

## Task 8 — Attack / defense interface

```python
trace   = attack(agent, scenario)        # -> trace file
trace   = defense(agent, policy)         # -> trace file (re-run with policy)
result  = evaluate(trace)                # -> summary dict
results = experiment(config)             # -> results dir
```

* **Input format:** a scenario object + agent config + optional policy.
* **Output format:** JSONL trace + `result.json` (evaluator summary) + `run_meta.json`.
* **Configuration:** YAML (Task 9).
* **Reproducibility metadata:** model id/revision, prompt-template version, scenario version, dataset version, tool config, seed (or `unsupported`), temperature (or `unsupported`), evaluator version, environment hash, timestamp.
* **Seeds:** used only where the provider supports them; otherwise recorded as unsupported — the Lab never pretends stochastic outputs are deterministic.

---

## Task 9 — Experiment configuration

```yaml
# experiments/examples/indirect_injection_baseline.yaml
experiment_id: indirect_injection_baseline
seed: 7                     # used only if the model supports it
repetitions: 3

models:
  - id: deepseek-v4.1-flash
    temperature: unsupported   # thinking mode ignores temperature (R35)
    seed: unsupported
  - id: glm-5.3-flash
    temperature: 1
    seed: unsupported          # GLM thinking cannot be disabled (R37)

agent:
  system_prompt_version: v1
  max_steps: 8
  tools: [calculator, fs_sandbox, mock_email]

scenario_set:
  id: indirect_injection_v1
  scenarios: [LAB-03-a, LAB-03-b, LAB-03-c]

defense:
  policy: none            # or policies/least_privilege_v1.yaml

evaluator:
  version: v1
  signal: [attack_success, benign_success, policy_violation]

output_dir: runs/indirect_injection_baseline
```

---

## Task 10 — Evaluation layer (established terminology only)

| Measurement | Definition | Objective or evaluator-dependent | Limitation |
|---|---|---|---|
| Attack success | Target action/content achieved (established: ASR) | Ground-truth state check where possible; else evaluator | Judge/state dependence (R52, R77) |
| Policy violation | A tool call denied by policy was attempted | Objective | Only within the Lab's policy model |
| Unauthorized tool execution | A tool call executed outside task scope | Objective (state/argument check) | Scope definition is scenario-specific |
| Data leakage | A designated synthetic secret appears at a sink | Objective (string/taint) | Only detectable for planted secrets |
| Defense success | Attack fails with policy enabled | Derived | Requires paired undefended run |
| Benign task success | Task completes without attack | Objective where state-grounded | Model competence confound |
| Tool-call count | Number of tool invocations | Objective | Not a security signal by itself |
| Latency | Wall-clock per step/run | Objective | Environment-dependent |
| Token usage | Provider-reported where available | Objective if reported | Often unavailable |
| Execution steps | Trace length | Objective | Correlates with task complexity |
| Recovery success | Post-restore task validity | Objective in simulated state | Simulated only |

**Do not invent new security metrics.** The Lab uses `attack_success`, paired `benign_success`, and state-grounded checks; it must report intervals and repetition counts because single runs are unstable (R52, R70, R74).

---

## Task 11 — Model adapter

```python
class ModelAdapter(Protocol):
    def complete(self, messages, *, temperature=None, seed=None, tools=None) -> ModelResponse: ...
    def capabilities(self) -> Capabilities   # supports_temperature, supports_seed, supports_tools
    def describe(self) -> ModelInfo          # id, revision, provider, notes
```

* Shared `ModelResponse` (`text`, `tool_calls`, `usage`, `raw`).
* Provider modules: `deepseek`, `mimo`, `glm`, `solar` (optional/verified only), `mock` (deterministic, for tests), `local` (open weights, later).
* Error handling: typed exceptions (`RateLimited`, `Transient`, `Unsupported`), bounded retries with backoff and jitter, and **an explicit `Unsupported` for temperature/seed** rather than silent defaults (R35, R37).
* Logging: request/response metadata + hashes to the trace (redacted).
* **No architectural dependency on one provider**; the mock adapter covers all tests.

---

## Task 12 — Tool sandbox

| Tool | Purpose | Security risk | Sandbox requirement | Attack scenario | Logging |
|---|---|---|---|---|---|
| `calculator` | Harmless baseline tool | None | none | — | args/result |
| `fs_sandbox` | File read/write | Path traversal / scope escape | Virtual FS rooted in a temp dir; no symlinks out | LAB-04 | path + hash |
| `mock_email` | External sink | Data leakage | Writes only to a local JSONL "outbox" | LAB-05 | recipient + hash |
| `mock_db` | SQL-lite store | Injection/over-broad query | In-memory/temp SQLite; read-only role option | LAB-04 | query + rows |
| `mock_search` | Retrieval over local corpus | Poisoning | Local synthetic corpus only | LAB-07 | doc ids |
| `mock_weather` | Benign network-shaped tool | none | Deterministic canned responses | — | args/result |
| `shell_sandbox` | (Deferred) command exec | Arbitrary execution | Container/`chroot`-like isolation | LAB-08 | command + exit |
| KB retrieval | Glossary/help lookup | Prompt injection via docs | Local corpus | LAB-03 | doc ids |

**Default: mock/sandboxed tools only.** `shell_sandbox` is deferred to Phase 2 and must run inside an isolated container with no host network/credentials.

---

## Task 13 — Repository structure

```
ai-agent-security-lab/
├── README.md                  # what/why/who/how — student-first
├── LICENSE                    # code
├── LICENSE-DATA               # data/docs, likely CC-BY-4.0
├── pyproject.toml
├── docs/                      # MkDocs sources (GitHub Pages)
├── src/agentsec/
│   ├── agent/                 # controller, context, planning
│   ├── models/                # adapters + mock
│   ├── tools/                 # gateway + sandbox tools
│   ├── policy/                # policy engine + example policies
│   ├── trace/                 # schema, recorder, validators
│   ├── eval/                  # evaluators
│   ├── experiment/            # config loader + runner
│   └── cli.py
├── labs/                      # one folder per LAB-xx (notebook + README + config)
├── scenarios/                 # scenario definitions (YAML/JSON)
├── policies/                  # example least-privilege policies
├── configs/                   # experiment configs
├── datasets/                  # synthetic corpora only (doc ids + hashes)
├── experiments/               # research-mode templates
├── traces/                    # example/expected traces (redacted)
├── tests/                     # unit/integration/schema/security tests
├── examples/                  # minimal runnable snippets
└── .github/workflows/         # CI (present, but not the README's focus)
```

The **README** explains what the Lab is, who it is for, the learning path, the lab list, the security topics, how to start, documentation and examples — **not** deployment or CI/CD.

---

## Task 14 — GitHub Pages documentation

**Recommendation: MkDocs Material** (already familiar, student-oriented, light, Markdown-first; Jekyll adds friction with little gain here).

Navigation:
```
Home
├── Learning Path (L0–L9)
├── Labs (LAB-00 … LAB-14)
├── Concepts
│   ├── Agent architecture
│   ├── Trust boundaries
│   └── Execution traces
├── Attack Catalog (established techniques, cited)
├── Defense Catalog (established techniques, cited)
├── Experiment Guide (Research Mode)
├── Reference (API: adapters, tools, trace schema, configs)
├── Research Mode (how to run controlled studies honestly)
└── Instructor Resources (objectives, rubric, safety policy)
```

---

## Task 15 — Testing strategy

* **Unit tests:** adapters (mock), policy engine, evaluator, trace validator.
* **Integration tests:** full agent loop with mock model + sandbox tools.
* **Scenario tests:** each lab asserts an expected trace signature.
* **Trace-schema tests:** every emitted event validates against `jsonschema`.
* **Model-adapter tests:** capability reporting (temperature/seed `Unsupported` handled).
* **Deterministic mock-model tests:** the entire CI suite runs **without any external API**.
* **Security regression tests:** known attacks succeed before policy, fail after.
* **Documentation tests:** code blocks and configs in docs are validated.

**Core requirement:** the test suite must pass offline.

---

## Task 16 — Reproducibility

Recorded per run: model id + revision, prompt-template version, config, dataset/scenario version, seed, temperature, tool config, environment (`python`, package versions, hash), timestamp, evaluator version.

**Deterministic components:** mock model, sandbox tools, policy engine, evaluator, trace ordering.
**Stochastic components:** commercial-model sampling, retrieval order (if nondeterministic), timing.

**Rule:** where a provider documents that a parameter is inert or unsupported, the trace records `unsupported`; the Lab never claims deterministic reproduction of stochastic provider output. This mirrors the Phase 2/5 findings (R35, R37, R62, R74).

---

## Task 17 — Safety

**Allowed:** attack only the Lab's own simulated agents, mock tools, synthetic data and clearly fake secrets; run in an isolated local environment.
**Not allowed:** attacking real systems/accounts, live third-party MCP servers, real credentials, real personal data, outbound network actions, kernel/OS-level changes.
**Default posture:** mock tools, virtual filesystem, in-memory/temp DB, no outbound network beyond configured model APIs; `shell_sandbox` containerized in Phase 2 with no host credentials.

---

## Task 18 — Three-phase roadmap

### Phase A — MVP
Components: agent loop, model adapter + mock, tool gateway + 3 mock tools, policy engine, JSONL trace, evaluator, YAML config, CLI.
Labs: LAB-00…LAB-04, LAB-08, LAB-09.
Complexity: small (roughly one package, no framework).
Exit criteria: a student can clone, run LAB-03, see the injection in the trace, enable the policy (LAB-08), and see the attack fail — entirely offline via the mock model, and online with a configured Flash model.

### Phase B — Educational expansion
Components: memory store, retrieval, monitor, output validation, trace store/index, Streamlit viewer (optional), MkDocs site.
Labs: LAB-05, LAB-06, LAB-07, LAB-10, LAB-11.
Exit criteria: full L0–L7 path runs; docs published; CI green offline.

### Phase C — Research experimentation
Components: experiment runner hardening, cost/token accounting, repetition/variance reporting, trace-analysis utilities, `shell_sandbox`.
Labs: LAB-12, LAB-13, LAB-14.
Exit criteria: a documented experiment template produces config + traces + results with reproducibility metadata, and the Phase-12 research escape hatch (Task 20) is in place.

No timelines are asserted; phases are gated by exit criteria, not dates.

---

## Task 19 — "Do not build" list

* Custom LLM training or fine-tuning.
* Frontier-model benchmarking or leaderboard claims.
* Distributed/parallel execution, queues, Kubernetes.
* Autonomous real-world agents or live accounts.
* Heavy multi-agent frameworks (AutoGen/CrewAI/LangGraph) in the MVP.
* New security metrics or a new threat taxonomy.
* A large benchmark or dataset; no "benchmark for its own sake".
* Novel defense algorithms.
* Production deployment, hosting, auth for real users.
* Live third-party MCP servers or unrestricted network tools.
* Vector databases, message brokers, or microservices for the MVP.
* Comprehensive-security-coverage claims.
* A LAN/CTF-style offensive range (out of scope unless later justified).

---

## Task 20 — Research escape hatch

The Lab is **not** built for a paper. If an observation looks interesting, it must pass a strict pipeline before anyone calls it research:

```
OBSERVATION → REPEAT → CONTROL VARIABLES → LITERATURE CHECK
→ HYPOTHESIS → EXPERIMENT → FULL-TEXT NOVELTY AUDIT → (maybe) PAPER
```

**Strict rules (learned from Phases 1–11):**
1. An unexpected result is **not** automatically novel; most surprises are already explained.
2. A full-text audit is required before declaring a candidate open (Phases 11 verified this the hard way).
3. An engineering feature is **not** a research claim.
4. The Lab's existence is **not** evidence of scientific contribution.
5. A single run is not evidence; repetition and intervals are required.
6. If a phenomenon is a known hidden variable (budget, harness, evidence view, judge bias), do not re-claim it.

---

## Task 21 — Final MVP specification

1. **Purpose:** teach and experimentally explore known agent-security problems in a simulated, reproducible environment.
2. **Target users:** students (L0–L9), researchers (Research Mode), instructors.
3. **Core architecture:** controller → context → adapter → tool gateway → policy → trace; optional memory/retrieval later.
4. **Core security modules:** M01, M02, M03, M04, M13.
5. **Model abstraction:** provider-independent `ModelAdapter` + deterministic `mock`.
6. **Tool sandbox:** calculator, fs_sandbox, mock_email (3 mock tools for MVP).
7. **Trace format:** append-only JSONL + `jsonschema`, redaction by default.
8. **Experiment format:** YAML config → JSONL traces + result JSON.
9. **Evaluation layer:** established metrics (attack_success, benign_success, policy_violation, leakage, steps, latency, usage).
10. **Learning path:** L0–L9, prerequisite-gated.
11. **Lab list:** LAB-00…LAB-04, LAB-08, LAB-09 in the MVP; the rest in Phases B/C.
12. **Repository structure:** as in Task 13.
13. **Documentation:** MkDocs Material on GitHub Pages (Task 14).
14. **Testing:** fully offline-capable suite (Task 15).
15. **Safety model:** mocks, synthetic data, fake secrets, no real systems (Task 17).
16. **Roadmap:** Phases A/B/C (Task 18).
17. **Non-goals:** Task 19.

**Minimum MVP components:** reference agent loop; provider-independent adapter + mock; tool gateway + 3 mock tools; policy engine; JSONL trace + schema; evaluator; YAML config; CLI; LAB-00…LAB-04, LAB-08, LAB-09; offline test suite.

**Optional future components:** memory store; retrieval; monitor; output validation; Streamlit viewer; trace index; `shell_sandbox`; multi-agent delegation; recovery/rollback; local open-weight adapter.

---

## Task 22 — Architecture Decision Records

| # | Decision | Reason | Alternative considered | Why not |
|---|---|---|---|---|
| ADR-1 | Python 3.11+ | Ecosystem, student familiarity, readable | Node/TypeScript | Smaller LLM/security tooling ecosystem for this audience |
| ADR-2 | Lightweight abstractions (protocols, no framework) | Keeps teaching points visible; minimal deps | LangChain/CrewAI/AutoGen | Hidden behaviour obscures causality and adds heavy deps |
| ADR-3 | Provider-independent model adapter | No single-provider dependency; reproducibility | Direct SDK per provider | Couples the Lab to one vendor; harder to swap |
| ADR-4 | Deterministic mock model | Offline, fast, deterministic tests | Always call a real API | Slow, costly, irreproducible; breaks CI |
| ADR-5 | JSONL traces + jsonschema | Append-only, observable, machine-checkable | Opaque logs / DB-only | Harder to teach; less inspectable |
| ADR-6 | Mock/sandboxed tools | Safety; no real accounts | Real APIs (web/email) | Unsafe, non-reproducible, ethically fraught |
| ADR-7 | Configuration-driven experiments | Reproducibility; research-ready | Hard-coded scripts | Irreproducible; hinders comparison |
| ADR-8 | Established metrics only | Honesty; avoid fake novelty | Invent new security metrics | Phase 12: metric inflation is a known hazard |
| ADR-9 | MkDocs Material on GitHub Pages | Light, Markdown-first, student-friendly | Jekyll/Docusaurus | More friction/maintenance for little gain |
| ADR-10 | Student-first documentation | Primary user is a learner | Research-first docs | Would exclude the main audience |
| ADR-11 | Research Mode separate from Student Mode | Prevents conflating demos with studies | One mode | Risks presenting demonstrations as experiments |
| ADR-12 | Privacy-safe traces (redaction, hashes) | Ethical default; shareability | Store raw prompts | Leaks secrets/PII |

---

## Task 23 — Final scope gate

**Question:** Can a student clone the repository, read the documentation, run a basic agent, observe a trace, perform a security attack, apply a defense, and understand the result **without expensive infrastructure**?

**Answer: YES.** The MVP runs offline with the deterministic mock model (no API cost), uses three sandboxed mock tools, and produces a validated JSONL trace; a configured Flash model can be swapped in via the adapter.

**Extensibility check:** the adapter, tool-gateway, policy-engine, trace-schema and experiment-config interfaces are stable enough to add memory, retrieval, monitoring, delegation and recovery without redesign. The design is therefore small enough for the MVP and open enough for Phase B/C — but no claim of research novelty is made.

---

## Files

* **Created:** `research/13-lab-scope-and-architecture.md` (this document).
* **Created:** `research/tables/lab-module-matrix.csv` — 13 modules.
* **Created:** `research/tables/lab-scenario-matrix.csv` — 15 scenarios.
* **`research/tables/sources.csv`:** unchanged (no new primary claims; references are by existing registry ID).
* No code, no Pages site, no datasets created.

---

**PHASE 13 COMPLETE — LAB SCOPE: MINIMAL**
