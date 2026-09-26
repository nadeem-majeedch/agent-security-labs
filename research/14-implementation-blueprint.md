# 14 — AI Agent Security Lab: Implementation Blueprint & Repository Skeleton (Phase 14)

**Status: PHASE 14 COMPLETE — IMPLEMENTATION BLUEPRINT: READY (with flagged OPEN DECISIONS)**

**Date:** 26 September 2026
**This phase is DESIGN ONLY.** No source code, no dependency installation, no GitHub Pages files, no application-repository changes, no commit/push.
**Governing specification:** `research/13-lab-scope-and-architecture.md` (Phase 13). This blueprint implements that scope and does not expand it.

---

## Task 1 — Phase 13 conformance and flagged conflicts

**[FACT]** Phase 13 was re-read together with `research/tables/lab-module-matrix.csv` and `research/tables/lab-scenario-matrix.csv`. Phase 13 governs: MVP modules M01/M02/M03/M04/M13; core dependencies `httpx`, `pydantic`, `PyYAML`, `jsonschema`; offline deterministic mock; provider-independent adapter with explicit `unsupported` for temperature/seed; JSONL traces; established metrics only; student-first docs.

**CONFLICT 1 (lab numbering) — flagged, not silently resolved.** The Phase 14 brief's Task 14 names "LAB-00 fundamentals, LAB-01 direct, LAB-02 indirect, LAB-03 tool misuse, LAB-04 authorization". Phase 13's canonical numbering is: LAB-00 setup, LAB-01 benign observation, LAB-02 direct injection, LAB-03 indirect injection, LAB-04 tool misuse, **LAB-08 authorization**, LAB-09 vulnerable-vs-defended. Per Task 1, **Phase 13 governs**, so this blueprint keeps the Phase 13 IDs. The brief's "first five labs" therefore maps to **LAB-00, LAB-01, LAB-02, LAB-03, LAB-04**, with **LAB-08** as the authorization lab (and LAB-09 optional in Phase A).

**CONFLICT 2 (repo `research/` dir) — minor.** The brief lists a top-level `research/` in the *lab* tree; Phase 13 does not. Resolution: include `research/templates/` **inside the lab repo** for experiment templates (distinct from this separate research repository) and label it clearly. Flagged as **OPEN DECISION OD-1**.

No other conflict found.

---

## Task 2 — Exact repository tree

```
ai-agent-security-lab/
├── README.md                      # student-first: what/why/who/how-to-start
├── LICENSE                        # code licence (to be chosen)
├── LICENSE-DATA                   # docs/data licence (e.g. CC-BY-4.0)
├── pyproject.toml                 # package + pinned deps + tool config
├── .gitignore                     # excludes runs/, __pycache__, .env
├── src/
│   └── agentsec/
│       ├── __init__.py
│       ├── agent.py               # Agent loop, context builder, RunResult
│       ├── models/
│       │   ├── base.py            # ModelAdapter protocol, ModelInfo, Capabilities
│       │   ├── schema.py          # ModelResponse, Usage, message typing
│       │   ├── mock.py            # deterministic MockModel (test fixture)
│       │   ├── deepseek.py        # provider adapter
│       │   ├── mimo.py            # provider adapter
│       │   ├── glm.py             # provider adapter
│       │   ├── solar.py           # provider adapter (optional, verified only)
│       │   └── factory.py         # build adapter from config
│       ├── tools/
│       │   ├── base.py            # Tool protocol, ToolSchema, ToolContext, ToolResult
│       │   ├── gateway.py         # ToolGateway (single mediated path)
│       │   ├── calculator.py      # harmless baseline tool
│       │   ├── fs_sandbox.py      # virtual filesystem in isolated workspace
│       │   ├── mock_db.py         # in-memory/temp SQLite
│       │   └── factory.py         # build tools from config
│       ├── policy/
│       │   ├── base.py            # PolicyEngine, PolicyDecision
│       │   ├── schema.py          # PolicyRule, Decision enum
│       │   └── loader.py          # YAML -> PolicyEngine
│       ├── trace/
│       │   ├── schema.py          # TraceEvent + event classes
│       │   ├── recorder.py        # TraceRecorder (append-only JSONL)
│       │   ├── redact.py          # Redactor
│       │   └── validate.py        # jsonschema validation
│       ├── eval/
│       │   ├── base.py            # Evaluator protocol, EvalResult
│       │   └── builtin.py         # established signals only
│       ├── scenarios/
│       │   ├── base.py            # Scenario protocol, ScenarioDef, ExpectedObservation
│       │   └── loader.py          # YAML/JSON scenario loading
│       ├── experiment/
│       │   ├── config.py          # ExperimentConfig (pydantic)
│       │   └── runner.py          # ExperimentRunner
│       ├── config.py              # shared config models
│       └── cli.py                 # CLI entrypoint
├── tests/
│   ├── unit/                      # adapters, policy, tools, trace, eval
│   ├── integration/               # gateway + agent loop + runner
│   ├── schema/                    # trace + config schema validation
│   ├── security_regression/       # attack-then-defend regressions
│   ├── cli/                       # subprocess CLI tests
│   ├── fixtures/                  # canned traces, mock scripts, scenario set
│   └── conftest.py                # offline-only fixtures
├── labs/
│   ├── LAB-00-setup/
│   ├── LAB-01-observe-trace/
│   ├── LAB-02-direct-injection/
│   ├── LAB-03-indirect-injection/
│   ├── LAB-04-tool-misuse/
│   └── LAB-08-authorization/      # (LAB-05/06/07/10/11/12/13/14 added in Phase B/C)
├── scenarios/
│   └── mvp/                       # YAML scenario definitions for MVP labs
├── policies/
│   └── examples/                  # least_privilege_v1.yaml, deny_by_default.yaml
├── configs/
│   └── examples/                  # benign.yaml, prompt_injection.yaml, tool_misuse_defense.yaml
├── research/
│   └── templates/                 # experiment templates (NOT the research repo)
├── docs/
│   ├── mkdocs.yml                 # nav, theme, plugins
│   ├── index.md
│   ├── getting-started/
│   ├── learning-path/
│   ├── concepts/
│   ├── labs/
│   ├── attack-catalog/
│   ├── defense-catalog/
│   ├── experiment-guide/
│   ├── reference/
│   ├── research-mode/
│   └── instructor/
├── examples/
│   ├── basic-agent/
│   ├── prompt-injection/
│   └── tool-authorization/
├── scripts/
│   ├── validate_traces.py         # CI helper (no hidden logic)
│   └── build_docs.sh              # docs build helper
└── traces/
    └── examples/                  # redacted example traces for labs
```

Every first-level directory has a single clear purpose; no deep nesting in the MVP.

---

## Task 3 — Python package architecture

| Module | Responsibility | Public API | May import | Must NOT know about |
|---|---|---|---|---|
| `agent` | Multi-step loop and context assembly | `Agent`, `RunResult`, `AgentConfig` | `models.base`, `tools.gateway`, `trace.recorder`, `scenarios.base` | provider HTTP, policy rule internals, trace file format |
| `models` | Provider-independent LLM access | `ModelAdapter`, `ModelResponse`, `Capabilities`, `factory` | `httpx`, `models.schema` | agent loop, tools, policy, evaluator |
| `tools` | Tool protocol + sandbox implementations + mediation | `Tool`, `ToolSchema`, `ToolGateway`, `factory` | `pydantic`, `policy.base`, `trace.recorder` | model adapter internals, scenario semantics |
| `policy` | Authorization decisions over a small policy model | `PolicyEngine`, `PolicyDecision`, `loader` | `pydantic`, `PyYAML` | tools, models, trace |
| `trace` | Standard event stream, redaction, validation | `TraceRecorder`, `TraceEvent`, `Redactor`, `validate` | `jsonschema` | policy/tool/model logic |
| `eval` | Established-measurement scoring | `Evaluator`, `EvalResult` | `trace.schema` | adapters, policy internals |
| `scenarios` | Declarative lab/experiment definitions | `Scenario`, `ScenarioDef`, `loader` | `pydantic`, `PyYAML` | adapters, policy, runner |
| `experiment` | Config-driven orchestration with repetitions | `ExperimentConfig`, `ExperimentRunner` | `config`, factories, `scenarios.base`, `eval.base` | provider HTTP internals |
| `cli` | User-facing commands | `main(argv)` | all of the above (thin) | (nothing internal) |

Coupling rule: dependencies point **inward** — `agent`/`experiment` depend on interfaces, never on concrete provider code; concrete adapters/tools are wired only through `factory` from config.

---

## Task 4 — Core interfaces (specification only, no implementation)

Type hints below define the contract a coding agent must implement. Duplicated concisely in `research/tables/lab-interface-matrix.csv`.

```python
# models/base.py
class ModelAdapter(Protocol):
    def complete(self, messages: list[Message], *, temperature: float | None = None,
                 seed: int | None = None, tools: list[ToolSpec] | None = None) -> ModelResponse: ...
    def capabilities(self) -> Capabilities:      # supports_temperature, supports_seed, supports_tools
        ...
    def describe(self) -> ModelInfo:             # provider, model_id, revision, notes
        ...

# tools/base.py
class Tool(Protocol):
    name: str
    def schema(self) -> ToolSchema: ...
    def run(self, args: dict, ctx: ToolContext) -> ToolResult: ...

# tools/gateway.py
class ToolGateway:
    def invoke(self, agent_id: str, tool_name: str, args: dict, ctx: ToolContext) -> ToolResult: ...
    def list_tools(self) -> list[str]: ...

# policy/base.py
class PolicyEngine:
    def decide(self, subject: str, tool_name: str, args: dict, ctx: ToolContext) -> PolicyDecision: ...

# trace/recorder.py
class TraceRecorder:
    def emit(self, event: TraceEvent) -> None: ...
    def close(self) -> TraceMeta: ...
    def validate(self, path: Path) -> ValidationReport: ...

# eval/base.py
class Evaluator(Protocol):
    version: str
    def score(self, trace_path: Path, ctx: EvalContext) -> EvalResult: ...

# scenarios/base.py
class Scenario(Protocol):
    def setup(self, env: Env) -> ScenarioState: ...
    def payload(self) -> dict: ...
    def expected(self) -> ExpectedObservation: ...
    def evaluate_criteria(self) -> list[str]: ...

# experiment/runner.py
class ExperimentRunner:
    def run(self, config: ExperimentConfig) -> ExperimentResult: ...
```

**Exceptions (typed, minimal):** `UnsupportedParameter`, `RateLimited`, `TransientError`, `ModelError`, `ToolValidationError`, `ToolExecutionError`, `UnknownTool`, `PolicyDenied`, `PolicyConfigError`, `TraceSchemaError`, `EvaluationError`, `ScenarioConfigError`, `ConfigError`, `MaxStepsExceeded`.

**Lifecycle:** `Agent.run` opens a trace → loops until an answer or `max_steps` → closes the trace. `ExperimentRunner.run` builds components once per config, then repeats `run_once` per repetition with a distinct `run_id`.

---

## Task 5 — Model adapter

The adapter reports capability **explicitly**:

```python
class Capabilities(BaseModel):
    supports_temperature: bool
    supports_seed: bool
    supports_tools: bool
    supports_forced_thinking: bool | None = None
```

**Rule (from Phase 13 and registry R35/R37):** where a provider documents a parameter as inert or unavailable, the adapter sets the capability to `False` and the trace records `"unsupported"` — never a silent default. `complete()` raises `UnsupportedParameter` if a caller passes a parameter the capability says is unsupported; the agent loop only passes parameters the capability advertises.

`ModelInfo` = `{provider, model_id, revision (or "unpinned"), notes}`. Request metadata (message count, tool specs hash) and response metadata (usage, latency, finish reason) are returned for the trace.

---

## Task 6 — Deterministic mock model

A **test fixture**, not an artificial intelligence. It is a script-driven state machine keyed deterministically by `(messages_hash, step_index)`.

* **Input:** the same `messages` structure as any adapter.
* **Deterministic response rules:** a scenario supplies a `MockScript` — an ordered list of `(matcher, action)` where `matcher` tests the last message/tool result and `action` returns either a tool call or a final answer.
* **Scenario-specific behaviours:** one script per MVP module: benign task, direct injection (follows an injected instruction when present), indirect injection (follows instruction found in a retrieved/mock document), tool misuse (issues an over-broad tool argument), excessive agency (takes an unnecessary state-changing action), authorization violation (requests a denied tool).
* **Tool-call generation:** emits a `ToolCall(name, args)` from the script; no model reasoning.
* **Reproducibility:** pure function of input + script; identical inputs produce byte-identical outputs.

This lets every core test run **offline and deterministically**.

---

## Task 7 — Tool system (MVP tools)

| Tool | Input schema | Output schema | Permissions | Side effects | Security boundary | Trace events |
|---|---|---|---|---|---|---|
| `calculator` | `{expr: str}` | `{value: float}` | none | none | pure expression eval (no `eval` of arbitrary code; AST-restricted) | `tool_requested`, `tool_executed`, `tool_result` |
| `fs_sandbox` | `{op: "read"|"write"|"list", path: str, content?: str}` | `{ok, content?, entries?}` | scoped to workspace root | writes inside isolated temp workspace only | rejects `..`, absolute paths, symlink escapes | `tool_requested`, `policy_decision`, `tool_executed`, `tool_result` |
| `mock_db` | `{query: str, params?: list}` | `{rows: list, count: int}` | read-only by default | writes only to a temp in-memory SQLite seeded per run | no persistence beyond the run | `tool_requested`, `policy_decision`, `tool_executed`, `tool_result` |

No real filesystem outside the workspace; no real database; no network.

---

## Task 8 — Tool gateway (single mediated path)

Responsibilities: tool lookup → input validation → authorization request → execution → result capture → error handling → trace recording.

Lifecycle per call:

```
1. agent requests tool(name, args)
2. gateway looks up the tool (UnknownTool if missing)
3. validate args against ToolSchema (ToolValidationError)
4. recorder.emit(tool_requested)
5. policy.decide(...) -> PolicyDecision
6. recorder.emit(policy_decision)
7. if deny  -> recorder.emit(tool_result{denied}); return DeniedResult
   if require_approval -> return PendingApprovalResult (MVP: treated as deny unless a
                          scripted approver in the scenario grants it)   [see OD-2]
   if allow -> tool.run(...)
8. recorder.emit(tool_executed) then tool_result
9. return ToolResult
```

**Enforcement point: the gateway, before execution.** There is **no alternate path** to a tool: tools are constructible only via the factory, and the agent receives only the gateway, never tool objects. A no-bypass integration test asserts that a direct tool call raises/does not exist in the agent's public surface.

---

## Task 9 — Policy engine (minimal)

```python
class Decision(str, Enum): ALLOW = "allow"; DENY = "deny"; REQUIRE_APPROVAL = "require_approval"

class PolicyRule(BaseModel):
    id: str
    subject: str            # agent id or "*"
    tool: str               # tool name or "*"
    action: str             # e.g. "invoke", "read", "write"
    resource: str | None    # e.g. path glob for fs
    conditions: dict | None # e.g. {"outside_task_scope": true}
    decision: Decision
    reason: str
```

Precedence: first matching rule wins; unmatched calls fall to `default_decision` (default `DENY`). Example policies:

```yaml
# policies/examples/deny_by_default.yaml
default: deny
rules: []
```

```yaml
# policies/examples/least_privilege_v1.yaml
default: deny
rules:
  - id: allow-calc
    subject: "*"
    tool: calculator
    action: invoke
    decision: allow
    reason: "read-only helper"
  - id: fs-inside-workspace
    subject: "*"
    tool: fs_sandbox
    action: read
    resource: "workspace/*"
    decision: allow
    reason: "in-scope read"
  - id: fs-outside-workspace
    subject: "*"
    tool: fs_sandbox
    action: "*"
    resource: "*"
    decision: deny
    reason: "least privilege: out-of-scope path"
```

The policy model is deliberately small: **no roles, no inheritance, no attribute-based engine.**

---

## Task 10 — Trace schema (JSONL)

Every line is one `TraceEvent`. Common required fields: `run_id`, `event_id`, `parent_event_id (nullable)`, `timestamp` (ISO-8601 UTC), `agent_id`, `model`, `scenario`, `event_type`. Validated with JSON Schema.

| Event type | Required extra fields | Optional |
|---|---|---|
| `run_started` | `config_ref`, `scenario_id` | `seed`, `temperature` |
| `agent_input` | `input_ref` (hash) | `task` (redacted) |
| `model_request` | `messages_hash`, `tool_specs_hash` | `temperature`, `seed` |
| `model_response` | `response_hash`, `finish_reason` | `usage`, `latency_ms`, `text_ref` |
| `tool_requested` | `tool_name`, `args_hash` | `args_redacted` |
| `policy_decision` | `decision`, `matched_rule`, `reason` | — |
| `tool_executed` | `tool_name` | `started_at` |
| `tool_result` | `ok`, `result_hash` | `error`, `side_effects` |
| `security_event` | `label`, `severity` | `evidence` |
| `agent_output` | `output_hash` | `answer_redacted` |
| `run_completed` | `steps`, `duration_ms` | `usage_total` |
| `run_failed` | `error_type`, `message` | — |

Correlation: `parent_event_id` links a tool call to its request/result; `event_id` is a ULID/UUID; `seq` is monotonic. Validation runs both at emit time and via `trace validate`.

---

## Task 11 — Redaction

**Default policy:** redact before writing; raw values are never persisted by default.

* **What:** API keys, bearer/authorization headers, cookies, tokens, passwords, and configured secret patterns (e.g. `SECRET_*`, fake keys used in labs).
* **How represented:** replaced with `"[REDACTED:<kind>]"`; content-bearing fields are stored as **hashes** (`sha256`) plus an optional redacted excerpt.
* **Where:** in `Redactor`, called by `TraceRecorder.emit` for every event, so no code path can bypass it.
* **Raw retention:** off by default; an explicit opt-in config flag `trace.retain_raw=false` exists for local debugging only and is documented as unsafe.

---

## Task 12 — YAML configuration + examples

`ExperimentConfig` fields: `experiment_id`, `model(s)`, `agent`, `tools`, `policy`, `scenario_set`, `evaluation`, `repetitions`, `output_dir`, `logging`. Validated by pydantic (schema errors are `ConfigError`).

**Example 1 — benign agent**

```yaml
experiment_id: benign_baseline
repetitions: 1
models: [{ id: mock, provider: mock }]
agent: { system_prompt_version: v1, max_steps: 6, tools: [calculator, fs_sandbox] }
policy: policies/examples/allow_all_local.yaml
scenario_set: { id: benign_v1, scenarios: [LAB-01-a] }
evaluation: { version: v1, signals: [benign_success, steps, latency] }
output_dir: runs/benign_baseline
```

**Example 2 — prompt injection**

```yaml
experiment_id: direct_injection
repetitions: 1
models: [{ id: mock, provider: mock }]
agent: { system_prompt_version: v1, max_steps: 6, tools: [calculator] }
policy: policies/examples/deny_by_default.yaml
scenario_set: { id: direct_injection_v1, scenarios: [LAB-02-a, LAB-02-b] }
evaluation: { version: v1, signals: [attack_success, benign_success, steps] }
output_dir: runs/direct_injection
```

**Example 3 — tool misuse + authorization defense**

```yaml
experiment_id: tool_misuse_defense
repetitions: 3
models:
  - { id: deepseek-v4.1-flash, provider: deepseek }   # temperature/seed: unsupported -> recorded
  - { id: glm-5.3-flash, provider: glm, temperature: 1 }
agent: { system_prompt_version: v1, max_steps: 8, tools: [calculator, fs_sandbox, mock_db] }
policy: policies/examples/least_privilege_v1.yaml
scenario_set: { id: tool_misuse_v1, scenarios: [LAB-04-a, LAB-08-a] }
evaluation: { version: v1, signals: [attack_success, policy_violation, benign_success, leakage] }
output_dir: runs/tool_misuse_defense
```

---

## Task 13 — Scenario interface

`ScenarioDef` (declarative, loaded from YAML/JSON) contains: `id`, `title`, `learning_objective`, `prerequisites`, `setup`, `attack_or_experiment`, `expected_observation`, `safety_note`, `evaluation_criteria`, plus an optional `payload` and a `mock_script` reference.

**Definition is separated from execution:** the core engine never contains scenario-specific branches; `Scenario.setup` produces a `ScenarioState`, and the `ExperimentRunner` executes it. Scenarios live only under `scenarios/` and `labs/`.

---

## Task 14 — First labs to implement

Per the Task-1 conflict resolution, the first labs follow **Phase 13 numbering**.

**LAB-00 — Setup and first benign run.** Objective: install, run the mock agent. Config: `benign_baseline`. Scenario: `LAB-01-a` (renamed "setup"). Expected trace: `run_started → agent_input → model_response → agent_output → run_completed`. Expected result: `benign_success=true`. Questions: "which events describe reasoning vs tool use?" Extension: swap the mock for a Flash adapter.

**LAB-01 — Observe a benign agent execution.** Objective: read a trace. Expected trace: adds `tool_requested → policy_decision → tool_executed → tool_result`. Expected result: `benign_success=true`, `steps≥2`. Questions: "where is the trust boundary?" Extension: annotate each event.

**LAB-02 — Direct prompt injection.** Objective: divert a benign agent. Config: `direct_injection`. Expected trace: injection text in `agent_input`; `agent_output` diverges. Expected result: `attack_success=true`. Questions: "what policy would have prevented this?" Extension: re-run with `deny_by_default` (partial).

**LAB-03 — Indirect prompt injection.** Objective: untrusted content issues instructions. Expected trace: a mock document read, then a tool call matching the injected instruction. Expected result: `attack_success=true`. Questions: "how does content become instruction?" Extension: add a policy that treats retrieved content as data.

**LAB-04 — Tool misuse.** Objective: over-broad tool argument. Expected trace: `tool_requested{args out of scope} → policy_decision → tool_executed`. Expected result: `policy_violation=true` under no policy. Questions: "was this a bug or a security failure?" Extension: enable `least_privilege_v1` and observe the denial.

**LAB-08 — Authorization defense.** Objective: enforce least privilege. Config: `tool_misuse_defense`. Expected trace: `policy_decision{deny} → tool_result{denied}`. Expected result: `attack_success=false`, `benign_success` preserved. Questions: "what utility cost did the defense impose?" Extension: tighten/loosen the policy and measure.

**(LAB-09, vulnerable-vs-defended comparison, optional in Phase A.)**

---

## Task 15 — Evaluator interface

```python
class EvalResult(BaseModel):
    version: str
    metrics: dict[str, float | int | None]
    evidence: list[EventRef]      # pointers into the trace
```

Established signals only: `attack_success`, `benign_success`, `policy_violation`, `leakage`, `steps`, `latency_ms`, `usage` (where reported). Each metric records whether it is **objective** (state/argument/string check) or **evaluator-dependent** (requires judgement); for the MVP all signals are objective so no LLM judge is required. No new security metric is introduced.

---

## Task 16 — Experiment runner

```python
class ExperimentRunner:
    def __init__(self, adapter_factory, tool_factory, policy_factory, scenario_loader, evaluator): ...
    def run(self, config: ExperimentConfig) -> ExperimentResult: ...
    def run_once(self, config, seed) -> RunResult: ...
```

Responsibilities: load config → instantiate model(s) → tools → policy → scenario → execute `repetitions` runs → collect traces → evaluate → write `results/`. **Deterministic vs stochastic:** with the mock model everything is deterministic; with a real adapter the runner records `seed/temperature` as supported/unsupported and never claims determinism it cannot deliver. Orchestration is a plain loop — no queues, no async frameworks.

---

## Task 17 — CLI (minimum viable set)

| Command | Purpose |
|---|---|
| `agentsec lab list` | List available labs |
| `agentsec lab run <id>` | Run a lab end-to-end |
| `agentsec scenario list` | List scenarios |
| `agentsec scenario run <id>` | Run one scenario |
| `agentsec experiment run <config.yaml>` | Run an experiment |
| `agentsec trace validate <file>` | Validate JSONL against schema |
| `agentsec trace inspect <file>` | Human-readable timeline |
| `agentsec evaluate <trace>` | Run the evaluator on a trace |

Example: `agentsec lab run LAB-03` → prints the observation, writes a trace to `runs/`, exits non-zero on schema failure.

---

## Task 18 — Test architecture

* **Offline by default:** unit, integration, schema, security-regression, CLI tests all use the mock model and sandbox tools.
* **Adapter tests:** capability reporting; `UnsupportedParameter` raised correctly; error mapping.
* **Mock tests:** determinism replays.
* **Tool/schema tests:** validation and sandbox-escape attempts.
* **Gateway no-bypass test:** asserts the agent has no path to a tool except `ToolGateway.invoke`.
* **Trace/redaction tests:** schema conformance; planted secrets never appear.
* **Evaluator tests:** fixture traces with known expected metrics.
* **Runner tests:** repetition count, metadata completeness.
* **CLI tests:** subprocess invocation and exit codes.
* **Optional, opt-in:** `tests/live/` (external adapters), skipped unless `AGENTSEC_LIVE=1` and credentials exist. **Never part of the default suite.**

---

## Task 19 — Documentation skeleton (GitHub Pages, MkDocs Material)

```
Home (index.md)
├── Getting Started: install, first run, using a Flash model
├── Learning Path: L0–L9 overview + per-level pages
├── Concepts: agent architecture, trust boundaries, execution traces, redaction
├── Labs: one page per LAB-xx (objective, steps, expected trace, questions)
├── Attack Catalog: M01–M04, M02 (established techniques, cited by registry id)
├── Defense Catalog: M13 policy, output validation (Phase 2), least privilege
├── Experiment Guide: config, repetitions, reproducibility, trace analysis
├── Reference: ModelAdapter, Tool, ToolGateway, PolicyEngine, TraceRecorder, Evaluator, CLI
├── Research Mode: how to run a controlled experiment honestly (Phase 13 escape hatch)
└── Instructor Resources: objectives, rubric, safety policy
```

Student-first; deployment/CI is confined to a short "Development" note, not the front page.

---

## Task 20 — Examples

```
examples/
├── basic-agent/          # smallest runnable benign agent + trace
├── prompt-injection/     # one direct injection + expected trace
└── tool-authorization/   # tool misuse, then least-privilege policy
```

Each example is a `README.md` + one config, and points to the corresponding lab rather than duplicating it.

---

## Task 21 — Implementation order

Full detail (prerequisites, deliverables, tests, completion criteria) in `research/tables/lab-implementation-order.csv`. Sequence:

1. Repository skeleton → 2. Core data models → 3. ModelAdapter + capabilities → 4. Deterministic mock → 5. Tool interface/schemas → 6. Sandbox tools → 7. Policy engine → 8. Trace recorder + redaction → 9. Tool gateway → 10. Evaluator → 11. Agent loop → 12. Experiment runner → 13. CLI → 14. First labs + docs → 15. Full verification.

**Modification to the brief's order:** the brief placed the mock model after the adapter (kept), but also implied gateway before tools; this blueprint implements **tools before gateway** because the gateway needs concrete tools to mediate. Flagged as a deliberate, minor reordering consistent with Phase 13.

---

## Task 22 — Dependency audit

| Dependency | Why | Type | Essential? | Stdlib alternative |
|---|---|---|---|---|
| `httpx` | HTTP for provider adapters | runtime (optional extra) | Only for live adapters | `urllib.request` (possible but poorer ergonomics) |
| `pydantic` | Config/schema/response validation | runtime | **Yes** | `dataclasses` + manual validation (weaker) |
| `PyYAML` | YAML configs/policies/scenarios | runtime | **Yes** | `tomllib` (config only) / JSON |
| `jsonschema` | Trace validation against a schema | runtime | **Yes** | manual checks (not standardised) |
| `pytest` | Test runner | development | **Yes** | `unittest` |
| `mkdocs-material` | Docs site | development | No (docs only) | plain Markdown |
| `ruff` | Lint/format | development | No | `pyflakes` |

**Core runtime set = `pydantic`, `PyYAML`, `jsonschema`.** `httpx` is optional and only pulled in when a live adapter is used; the MVP runs with the mock and **zero** network dependencies.

---

## Task 23 — Risks

**Architectural**
1. Gateway bypass — *consequence:* security teaching invalid — *mitigation:* tools constructed only by factory; no-bypass test.
2. Adapter leakage of provider specifics into the core — *consequence:* brittle core — *mitigation:* protocols + factory; lint import rules.
3. Schema churn breaking traces — *consequence:* broken labs — *mitigation:* versioned schema; `trace validate`.
4. Over-abstract interfaces — *consequence:* harder for students — *mitigation:* keep to the nine interfaces in Task 4.
5. Evaluator coupling to trace internals — *consequence:* fragile scoring — *mitigation:* `EventRef` indirection.

**Educational**
1. Students mistake the mock for an LLM — *mitigation:* label clearly as a fixture.
2. Students mistake demos for experiments — *mitigation:* separate Student/Research modes.
3. Over-complex setup — *mitigation:* offline-first, one command to run.
4. Labs reveal attack payloads without context — *mitigation:* synthetic-only payloads + safety note per lab.
5. Hidden magic reduces learning — *mitigation:* no frameworks; explicit traces.

**Maintainability**
1. Dependency creep — *mitigation:* dependency audit; CI denies undeclared imports.
2. Provider API drift — *mitigation:* adapters isolated; capability flags; pinned tests use mock.
3. Docs drift from code — *mitigation:* docs build test; doctest-style config validation.
4. Test suite needs network — *mitigation:* live tests opt-in only.
5. Scope creep into benchmark territory — *mitigation:* Task 24 check each release.

**Security/safety**
1. Accidental real tool use — *mitigation:* sandbox-only tools; no network by default.
2. Secret leakage into traces — *mitigation:* redaction by default; planted-secret tests.
3. Malicious student payloads — *mitigation:* synthetic targets only; usage policy.
4. Filesystem escape — *mitigation:* virtual FS rooted in temp; escape tests.
5. Dual-use misuse — *mitigation:* documented ethics policy; no real-target tooling.

---

## Task 24 — Scope-creep check against Phase 13

Checked item by item. Nothing in this blueprint adds a mechanism, benchmark, framework, database, or Phase 2/3 module. Two items were **removed** during this check: a proposed `trace index (SQLite)` (not needed for the MVP) and a proposed `Streamlit viewer` (Phase 2, optional). The `research/templates/` directory is retained **only** as inert experiment templates and is flagged (OD-1). Result: **no expansion beyond the approved MVP.**

---

## Task 25 — Final implementation contract

**A. Repository tree** — Task 2. **B. Core interfaces** — Task 4 (+ `lab-interface-matrix.csv`). **C. Data schemas** — Tasks 10–12 (trace, config, policy). **D. CLI** — Task 17. **E. Initial labs** — Task 14 (LAB-00/01/02/03/04 + LAB-08). **F. Test architecture** — Task 18. **G. Documentation structure** — Task 19. **H. Dependency list** — Task 22. **I. Implementation order** — Task 21. **J. Definition of Done** — below.

**Definition of Done**
- All core tests pass **offline** (mock model, sandbox tools).
- The JSONL trace schema validates every emitted event.
- Redaction works; planted secrets never appear in traces.
- Mock scenarios are **deterministic** (byte-identical replays).
- The first five labs (+LAB-08) execute and reproduce their expected observations.
- The CLI works offline for every listed command.
- Documentation builds with MkDocs.
- No undeclared dependencies (CI import check).
- No real credentials or real-world tools are required.
- No research-novelty claim appears anywhere.
- No Phase 2/3 functionality is accidentally included.

### Flagged OPEN DECISIONS
* **OD-1** — Whether the lab repo should carry `research/templates/` at all, or reference an external repo. *Recommendation:* keep as inert templates; confirm with maintainer.
* **OD-2** — MVP handling of `REQUIRE_APPROVAL`: treat as deny unless a scripted approver exists. *Alternative:* a stub interactive prompt. *Recommendation:* deny + scripted approver (keeps offline determinism).
* **OD-3** — Default `trace.retain_raw`: assumed `false`. *Confirm* before implementation.
* **OD-4** — Whether `solar.py` is included at all given R38 (release too new to pin). *Recommendation:* omit from the MVP; document as optional.

These four are the **only** architectural points not fixed by Phase 13; everything else is determined.

---

## Files

* **Created:** `research/14-implementation-blueprint.md` (this document).
* **Created:** `research/tables/lab-interface-matrix.csv` — 9 interfaces.
* **Created:** `research/tables/lab-implementation-order.csv` — 15 steps.
* **`research/tables/sources.csv`:** unchanged (no new primary claims).
* No source code, no dependencies installed, no Pages files, no commit/push.

---

**PHASE 14 COMPLETE — IMPLEMENTATION BLUEPRINT: READY**
