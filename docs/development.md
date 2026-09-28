# AgentSec Lab - development notes (Phase A)

Educational, reproducible agent-security infrastructure. Implemented so far:
the skeleton, core data models, the trace schema/validation/recording,
redaction, a deterministic mock model, **sandboxed tools**, the **mediated
ToolGateway**, the **minimal PolicyEngine**, a small **deterministic agent
loop**, a **read-only descriptive evaluator**, a **thin one-run experiment
runner**, a **thin command-line interface**, a **declarative scenario layer**
and the **eight student labs LAB-00 … LAB-07** (LAB-00 setup verification,
LAB-01 benign-agent observation, the first three adversarial observation labs
(LAB-02 direct prompt injection, LAB-03 indirect prompt injection, LAB-04
tool misuse), LAB-05, which observes the `require_approval` decision, LAB-06,
which observes an **authorized but unnecessary** state-changing action that
actually executes, and LAB-07, which observes an **authorized egress**: a
task-requested, policy-allowed read followed by a policy-allowed send).
There are
deliberately no real model adapters and **no defences yet** - the adversarial
labs observe behaviour only.

The package makes **no research-novelty claim** anywhere; it reimplements
established concepts for teaching and reproducible experimentation.

## Research status (Phase 17 — CLOSED, research NO-GO)

**Phase 17 final status (closed).**

1. The Phase 17 research transition is **CLOSED**.
2. The project remains **infrastructure/education focused**; it is not a
   research project.
3. The proposed direction “model exfiltration propensity under policy/task
   variation” is **CLOSED / NOT READY**.
4. The Phase 17 **hostile literature/full-text audit** found substantial prior
   coverage across every area the direction touches: agentic exfiltration,
   prompt injection and indirect prompt injection, tool misuse, excessive
   agency, policy/authorization enforcement, data leakage, unnecessary
   disclosure, stochastic/repeated-trial evaluation,
   attempt-vs-authorization-vs-execution-vs-egress measurement, and
   reproducibility methodology.
5. **No literature-supported unresolved boundary condition survived** the
   audit. The direction is closed because no defensible unresolved gap remained
   — **not** because research is impossible or the project lacks value.
6. The **real stochastic model adapter remains UNIMPLEMENTED** (there is no
   provider adapter and no provider factory).
7. The **small research corpus remains UNIMPLEMENTED**.
8. **No experiment is authorized** by the current project status.
9. **No novelty claim is made** anywhere in this repository.
10. Research directions previously killed in **Phases 12–17 remain closed**.
11. Any future research direction must start from a **genuinely different
    question / boundary condition** and undergo a **fresh hostile literature
    audit before** any implementation.

**Research implementation freeze.** The following remain **unimplemented** and
must stay so while the literature gate stands at NO-GO: the real stochastic
model provider adapter, the provider factory, the repeated-trial research
harness, the research corpus, research-specific metrics, research evaluator
extensions, research trace-schema extensions, the research experiment, and the
research benchmark.

**Educational value is not a research contribution.** The literature audit
found prior art for the audited *research direction*; it does **not** invalidate
the educational infrastructure. The labs may intentionally teach established
concepts, and the project may keep improving student learning, reproducibility,
deterministic security demonstrations, mediated tool execution, policy
enforcement, trace inspection, scenario construction, sandbox safety and
documentation **without** making any research-novelty claim.

**Current project scope.** This repository is **educational + reproducibility
infrastructure** and a **mediated-agent harness** (the deterministic labs, the
trace recorder, the descriptive evaluator, and the single mediated
`ToolGateway` path). It is **not** a research benchmark, an empirical
agent-behaviour study, a novel security mechanism, a production framework, or a
security score/benchmark. It makes **no research-novelty claim**.

**Decision.** After LAB-00 … LAB-07, the Phase 17 research transition is
**CLOSED** with a **NO-GO for research at present**. This is not a failure of
the project. The deterministic architecture deliberately establishes a *controlled
and reproducible educational baseline*, and that baseline is **insufficient for
empirical claims about stochastic agent or model behaviour**.

**Why (the deterministic-fixture boundary).** Every lab drives a deterministic,
scripted `MockModel` fixture. Consequently:

- model actions are **authored** by the fixture, not produced by a model;
- tool calls are **scripted** and outcomes are predetermined;
- repeated runs demonstrate **determinism**, not behavioural distributions;
- evaluator counts are **fixture outcomes**, not model propensities;
- policy decisions are **author-controlled** (a YAML edit);
- synthetic data and in-memory tools remove real-world dynamics.

Any "result" is therefore a property of the fixtures and configuration the
author wrote, not of an agent. No falsifiable research claim about real
agent/model behaviour can be supported in this form.

**LAB-07 boundary (Data Leakage).** LAB-07 demonstrates an **observable
authorized egress**: a task-requested, policy-allowed read followed by a
policy-allowed send, with the synthetic marker visible at
`mock_email.args_redacted.body`. It does **not** demonstrate autonomous
unintended leakage, a policy failure, a security vulnerability, or real-model
exfiltration propensity. The transfer is explicitly requested by the task and
deterministically scripted (`deny = 0`).

**Previously audited and closed directions.** Earlier hostile audits already
examined and rejected: repeated-run statistical correction; budget-vs-replication
novelty; same-trajectory/different-evaluator validity; recovery; MCP/tool trust;
runtime monitoring; cross-domain verifier independence; reproducibility as a
novelty angle; AI-assisted performance audit; grounding/detectability anomaly;
AI-generated tests versus fault detection; and further agent-security candidates
(see `research/12`–`research/14` and `research/tables/`). These remain closed.
Reopening any of them requires a **genuinely different boundary condition** *and*
a fresh literature audit — not merely the fact that they are listed here.

**Single reopening condition.** Research work may be reconsidered only after, in
this mandatory order:

1. adding a **real, stochastic model adapter**;
2. creating a **small, controlled research corpus**;
3. performing a **hostile literature/full-text audit before** designing any
   substantive experiment.

```
real model adapter + small corpus
        -> hostile literature audit
        -> only if a genuine gap survives
        -> controlled experiment
```

This condition does **not** guarantee a contribution, and no candidate is claimed
to be novel. If the audit finds nothing unresolved, the project stays in
infrastructure/education mode.

**Future real-model adapter — design requirements (documented, not implemented).**
A future adapter must preserve the existing abstractions: the `ModelAdapter`
protocol, `ToolGateway` mediation, `PolicyEngine` mediation, the `TraceRecorder`,
the deterministic `MockModel` as the **control condition**, offline/sandbox
safety where possible, reproducible configuration, explicit model/provider
metadata, model-response capture sufficient for audit, trial/repetition support,
and a clear separation between the deterministic control and the stochastic
treatment. Introducing a real model changes the research character: it adds
stochasticity, model/provider dependence, cost, latency, possible network
requirements, model/version drift, statistical design, repeated trials, corpus
construction and further threats to validity. None of this exists today.

**Future small corpus — requirements (documented, not created).** A future
research corpus should be small initially, synthetic, controlled, versioned,
reproducible, explicitly labeled, designed around research conditions rather
than educational demonstrations, and accompanied by expected observations /
ground truth where possible. It is **not** a benchmark and makes no
representativeness claim.

**Candidate status.** The considered direction “model exfiltration propensity
under policy/task variation” is **CLOSED / NOT READY**: it requires real model
behaviour and stochastic trials; the area is crowded; and no novelty claim has
survived a fresh full-text audit. It may be reopened only once the real-model
adapter and corpus exist **and** a fresh literature audit isolates an unresolved
boundary condition.

**Cross-references (historical records — not rewritten here).**

- Phase 12 — research-direction audit:
  `research/12-research-direction-selection-audit.md`
- Phase 13–14 — lab scope, architecture and implementation blueprint:
  `research/13-lab-scope-and-architecture.md`,
  `research/14-implementation-blueprint.md`
- Phase 16 — Data Leakage: `labs/LAB-07-data-leakage/`
- Phase 17 — research transition and hostile literature audit: **this section**
- Supporting matrices: `research/tables/*.csv`

**No paper yet.** No abstract, positioning or paper is drafted. The sequence
remains: infrastructure → observation → hypothesis → literature audit →
experiment → final novelty audit → paper.

## Install (development)

```bash
py -m pip install -e ".[dev]"
```

Requires Python 3.11+. Core runtime dependencies are `pydantic`, `jsonschema`
and `PyYAML` (the policy YAML loader). `httpx` is an optional extra for future
live provider adapters and is not needed by anything current.

## Run the tests

```bash
py -m pytest
```

The entire suite runs **offline**: no network, no API keys, no external model
providers, no database, no Docker, no GPU. Everything is driven by the
deterministic mock model and the sandbox tools.

CI (`.github/workflows/ci.yml`) runs the suite with `python -m pytest` and then
`agentsec labs check`, so a change that breaks a canonical lab scenario fails the
build.

## What is implemented

```
src/agentsec/
├── errors.py            # typed exceptions actually used today
├── models/
│   ├── schema.py        # Message, ToolSpec, ToolCall, Usage, ModelResponse
│   ├── base.py          # ModelAdapter protocol, Capabilities, ModelInfo
│   └── mock.py          # deterministic MockModel + MVP fixture scripts
├── tools/
│   ├── base.py          # Tool protocol, ToolSchema, ToolContext, ToolResult
│   ├── calculator.py    # AST-restricted arithmetic
│   ├── fs_sandbox.py    # in-memory virtual filesystem
│   ├── mock_db.py       # in-memory synthetic database
│   ├── mock_email.py    # in-memory synthetic egress sink (no network/SMTP)
│   ├── gateway.py       # ToolGateway (single mediated path)
│   └── factory.py       # build tools / build a gateway
├── policy/
│   ├── schema.py        # Decision, PolicyRule, Policy, PolicyDecision
│   ├── base.py          # PolicyEngine (first-match-wins)
│   └── loader.py        # YAML -> PolicyEngine
├── agent.py             # Agent loop, AgentConfig, RunResult
├── mvp.py               # MVP composition root (wires the deterministic stack)
├── cli.py               # thin CLI: run / evaluate / inspect
├── __main__.py          # python -m agentsec
├── eval/
│   ├── base.py          # Evaluator protocol, EvaluationInput/Result, EventRef
│   └── builtin.py       # TraceEvaluator (descriptive counts)
├── experiment/
│   ├── config.py        # ExperimentConfig + YAML loader
│   └── runner.py        # ExperimentRunner, ExperimentResult
├── scenarios/
│   ├── base.py          # ScenarioDef, ExpectedObservation, ScenarioOutcome, DeclarativeScenario
│   ├── loader.py        # strict YAML scenario loading
│   └── registry.py      # explicit in-memory registry
└── trace/
    ├── schema.py        # versioned TraceEvent union (12 event types)
    ├── redact.py        # Redactor: deterministic, idempotent redaction
    ├── validate.py      # jsonschema + semantic (seq/parent) validation
    ├── recorder.py      # TraceRecorder (stamps header, redacts, validates)
    └── writer.py        # append-only JSONL I/O
schemas/trace/trace_event.v1.schema.json   # versioned trace contract
policies/examples/                          # deny_by_default, least_privilege_v1, lab06_excessive_agency_v1, lab07_data_leakage_v1
labs/
├── LAB-00-setup/                # README.md, config.yaml (environment verification)
├── LAB-01-benign-agent/         # README.md, config.yaml, scenario.yaml
├── LAB-02-direct-prompt-injection/   # README.md, config.yaml, scenario.yaml
├── LAB-03-indirect-prompt-injection/ # README.md, config.yaml, scenario.yaml
├── LAB-04-tool-misuse/               # README.md, config.yaml, scenario.yaml
├── LAB-05-require-approval/          # README.md, config.yaml, scenario.yaml
├── LAB-06-excessive-agency/          # README.md, config.yaml, scenario.yaml
└── LAB-07-data-leakage/              # README.md, config.yaml, scenario.yaml
```

## Trace schema

Every JSONL line is one event. All events carry `schema_version`, `run_id`,
`event_id`, `parent_event_id`, `seq`, `timestamp` (UTC), `agent_id`, `model`,
`scenario` and `event_type`; each type adds its own fields. The union is
discriminated on `event_type`, so unknown types and missing per-type fields are
rejected by both pydantic and the JSON Schema.

The checked-in schema is generated from the pydantic models:

```bash
py scripts/export_trace_schema.py
```

`tests/schema/test_schema_file.py` fails if the file and the models diverge.

`TraceRecorder` stamps the shared header onto every event, redacts it, validates
it and appends it. `event_id` is `ev-<seq>` and the clock is injectable, so a
replay is byte-identical.

## Deterministic mock

`agentsec.models.mock.MockModel` is a **test fixture, not an LLM simulation**.
Its response is a pure function of the message list and a `MockScript`, so
identical inputs yield byte-identical outputs. It consults no clock and no RNG
(`latency_ms` is always `None`). It reports `supports_temperature=False` and
`supports_seed=False`, and raises `UnsupportedParameter` if a caller passes
either, so it can never be mistaken for a controllable model.

Fixture scripts cover the five MVP security modules plus a benign baseline:
`benign`, `direct_injection`, `indirect_injection`, `tool_misuse`,
`excessive_agency`, `authorization_violation` (see `script_for`). Two further
lab fixtures, `direct_redirect` and `indirect_redirect`, back the first
adversarial labs: each follows an untrusted instruction - one placed directly in
the task, one arriving in a tool's returned content - by requesting an otherwise
unrelated sandbox operation, and discloses nothing. Every tool call in those
scripts is schema-valid for the Step 2 tools, so the tools and the mock already
agree. LAB-04 reuses the existing `tool_misuse` fixture directly: no injected
instruction, just an over-broad filesystem write that the policy denies. LAB-05
adds one small fixture, `approval_read`: a legitimate `mock_db` read that the
existing `db-read-requires-approval` policy rule holds for approval. LAB-06
reuses the existing `excessive_agency` fixture directly: no injection and no
misuse, just a state-changing `mock_db` write that the lab's own policy allows,
so the tool executes and leaves an observable (synthetic) side effect. LAB-07
adds one more fixture, `data_leakage`: a task-requested `mock_db` read of a
synthetic record followed by a `mock_email` send to a reserved RFC-2606
address. Nothing is injected and nothing is out of scope; both operations are
policy-allowed, so the synthetic record crosses the egress boundary. The
record's `sensitive_demo_value` is a deliberately non-secret marker
(`SYNTHETIC-DEMO-DISCLOSURE-A1`) that matches none of the redactor's patterns,
so it stays observable in the trace; secret-shaped values are still redacted.

## Tools

A `Tool` exposes a typed `ToolSchema` (name, description, JSON Schema for input
and output), an `action(args)` / `resource(args)` pair used only for
authorization metadata, and `run(args, ctx)`. Tools do not know about the model
adapter, the agent loop, the policy engine or trace storage, so each is
independently testable. Concrete tools are built **only** through
`agentsec.tools.factory.build_tools`.

* `calculator` — parses a small arithmetic expression and evaluates it with an
  explicit AST walker. Supported: numeric literals, `+ - * / // % **`, unary
  `+/-`, parentheses and the calls `abs`, `round`, `min`, `max`. There is no
  `eval`, no `exec`, no attribute/subscript access, no names, no strings, no
  imports and no I/O. Everything else raises `ToolValidationError`; failing
  arithmetic (division by zero, overflow, non-finite result) raises
  `ToolExecutionError`. Output is always a finite `float`.
* `fs_sandbox` — an **entirely in-memory** virtual filesystem (no disk access).
  Supports `read`, `write` and `list`. Paths are relative to the virtual
  workspace; `..`, absolute POSIX paths, Windows drive paths, UNC/device paths,
  null bytes and reserved device names are rejected. There are no symlinks.
  Max content size is 64 KiB. Instances are fully isolated.
* `mock_db` — an in-memory, synthetic "database" (no SQLite and no database
  library). Understands a deliberately small SQL-shaped subset: `SELECT`,
  `INSERT`, `UPDATE`, `DELETE`, with an optional single `WHERE col = value` and
  `?` parameters. Default `read_only=True`, so writes raise
  `ToolExecutionError` unless the tool is built writable. Each instance holds
  its own copy of the synthetic seed. `build_tools(..., sandbox_db_writes=True)`
  builds it writable for a lab that needs to observe a synthetic state change;
  `build_tools(..., sandbox_db_seed={...})` instead replaces its synthetic seed
  for that instance with per-lab fixture data (the shared defaults are
  untouched). Nothing else changes and every other lab stays read-only.
* `mock_email` — an **entirely in-memory** synthetic egress sink (no network, no
  SMTP, no filesystem, no subprocess). Its single action is `send`, whose
  `resource` is the recipient; the input schema requires non-empty `to`,
  `subject` and `body` (body capped at 4096 characters) and the output records
  `sent`, `recipient` and a per-instance `message_id`. Messages are held in an
  in-memory outbox, so a lab can observe that an egress *was requested and
  permitted* without anything leaving the process.

**Sandbox boundary.** Tools enforce *containment* (a request cannot leave the
sandbox). Which resources *within* the sandbox an agent may touch is a **policy**
question, answered by the policy engine. Keeping the two separate is the point
of the lab. To keep that separation honest, `fs_sandbox.resource()` returns the
*raw* requested path so policy can judge scope, and the tool's own
normalization/rejection happens later, at run time.

## ToolGateway lifecycle

`ToolGateway` is the single mediated path. Per call:

```
1. look up the tool            (UnknownTool if missing)
2. validate args vs ToolSchema (ToolValidationError; the tool is not reached)
3. emit tool_requested
4. policy.decide(agent, tool, args, ctx, action, resource)
5. emit policy_decision
6. deny             -> emit tool_result{denied}; return DeniedResult
   require_approval -> resolve approval (below); otherwise PendingApprovalResult
   allow            -> execute
7. emit tool_executed, run the tool, validate its output
8. emit tool_result; return a structured ToolResult
```

Two invariants are enforced by tests: a denied call **never** invokes the
underlying tool, and a call requiring approval **never** silently becomes an
allow. The `ToolResult` carries a `status` of `ok`, `error`, `denied` or
`pending_approval`, so a caller can tell why nothing happened.

**Approval model (OD-2).** Approval is deterministic and offline. `invoke`
accepts `approval=True` (granted) or `approval=False` (refused); when neither is
given, an optional scripted `approver` callable decides. If nothing grants
approval, the call stays `pending_approval` and is not executed.

**No-bypass.** This is an architectural property, not a claim that Python makes
bypass impossible. The lab's own wiring exposes only the gateway: tools are
built by the factory, the gateway's public surface is `invoke` / `list_tools` /
`has_tool`, and the gateway holds no public accessor for tool objects. Code that
deliberately imports a tool class could still call it directly; the lab simply
never does, and the no-bypass tests prove the gateway's branches never execute a
tool that was not authorized.

## Agent loop

`agentsec.agent.Agent` is the smallest deterministic model/tool loop. It depends
only on abstractions: a `ModelAdapter` and a `ToolGateway`. It never executes a
tool, evaluates a policy rule, validates a tool schema or builds provider-
specific requests.

```
input -> model -> final answer? return
               -> tool calls? gateway -> tool results -> model -> ...
```

At most `AgentConfig.max_steps` model calls are made. A run ends in one of three
states, reported by `RunResult.status`:

* `completed` - the model produced a final response;
* `step_limit` - the limit was reached while the model was still requesting
  tools (a `max_steps_exceeded` event is recorded);
* `failed` - a model error, malformed response, unknown tool or invalid tool
  arguments ended the run.

Tool calls are read from the structured `ModelResponse.tool_calls`; the agent
does not parse natural-language text for tool calls. Each call is dispatched
through `ToolGateway.invoke`. A denial, pending approval or tool error is fed
back to the model as a tool result so it can choose a final answer; an unknown
tool or invalid arguments is terminal. The agent uses `ToolSpec` objects built
from `gateway.tool_schemas()`, so it advertises tools without ever holding a
tool object.

Conversation state is a plain list of `Message` objects (optional system turn,
the user turn, the assistant turns and tool results). There is no memory, RAG or
persistence - those are later phases.

### Model adapter integration

The MVP uses the deterministic `MockModel`, which ignores the advertised tools
and answers from its script. It reports `supports_temperature=False` and
`supports_seed=False` and raises `UnsupportedParameter` for either, so nothing
pretends the fixture is a controllable LLM. `RunResult` never claims
determinism it cannot deliver: with the mock, identical inputs produce
byte-identical traces.

### Trace and correlation

One `TraceRecorder` is built first and shared by the gateway and the agent, so a
run writes a single coherent JSONL file. The agent emits `run_started`,
`agent_input`, `model_request`, `model_response`, `agent_output` and
`run_completed` (or `run_failed`); the gateway emits the `tool_requested` /
`policy_decision` / `tool_executed` / `tool_result` block. `parent_event_id`
links each event to its predecessor, so the whole chain - input -> response ->
tool call -> policy -> execution -> result -> next response - is reconstructable
from the existing `run_id` / `event_id` / `parent_event_id` fields. No wall clock
is consulted (`duration_ms` is `0.0`); timing is injected by the later runner.

## Experiment runner

`agentsec.experiment.ExperimentRunner` is a thin, single-run orchestration layer.
It coordinates components that already exist and does nothing they already do:

```
ExperimentRunner
  └── Agent (owns the loop) ── ModelAdapter + ToolGateway + PolicyEngine
  └── TraceRecorder (owns writing)
  └── Evaluator (owns analysis)
```

```python
runner = ExperimentRunner(agent=agent, evaluator=TraceEvaluator(), recorder=recorder)
result = runner.run(ExperimentConfig(experiment_id="benign_baseline", task="...", agent=agent.config))
```

`run` executes exactly **one** agent run, then reads the trace the recorder wrote
and passes its events to the evaluator. There are no repetitions, batches,
parallel runs, sweeps or retries.

### Configuration

`ExperimentConfig` is composed, not copied: it carries `experiment_id`, `task`,
the existing `AgentConfig`, an optional expected `trace_path`, an optional
`policy_path`, the `mock_script` name, an optional `sandbox_files` mapping
that seeds the in-memory `fs_sandbox` workspace with synthetic fixture content
(memory only; it never touches the host disk), a `sandbox_db_writes` flag
(default `false`) that builds the in-memory `mock_db` writable so a lab can
observe a synthetic state change, and an optional `sandbox_db_seed` mapping
(default empty) that replaces the in-memory `mock_db` synthetic seed, by table
name, for one run only (still memory-only and per-instance; the shared defaults
are untouched, so every other lab keeps them). It has no fields for
capabilities that do not exist (no temperature, seed, retries, parallelism or
credentials).
`load_experiment_config(path)` parses YAML with the same strict behaviour as the
policy loader and raises `ConfigError` on a malformed document.

### One run, one recorder, one coherent trace

Before executing, the runner checks the configuration against its collaborators:
the experiment's `AgentConfig` must equal the injected agent's config, and the
recorder's `run_id` / `agent_id` / `scenario` must match it (and the optional
`trace_path`, when set). This preserves the Step 3 invariant that one run writes
one coherent trace. Any mismatch raises `ConfigError`.

### Result semantics

The returned `ExperimentResult` keeps the two results side by side and never
collapses them into a boolean: `agent` is the untouched
`agentsec.agent.RunResult` (with its own `completed` / `failed` / `step_limit`
status) and `evaluation` is the untouched `EvaluationResult`. `error` records an
*orchestration* problem (for example an unreadable trace), not an agent failure -
that stays in `agent.error`. A missing/invalid trace yields `evaluation=None`
with `error` set, so an unevaluated run can never look like a clean pass.

### Determinism

The runner adds no randomness, clock, filenames or environment dependence: it
uses the caller-supplied `run_id` and recorder path. With the deterministic
mock, identical inputs produce byte-identical traces and equal results.

### What the runner deliberately does not do

It does not implement the agent loop, execute tools, invoke the gateway or
policy engine, write trace events, retry, run in parallel, load scenarios,
compute metrics, or score anything. It only orchestrates and reports.

## Evaluator

`agentsec.eval.TraceEvaluator` is a **read-only, descriptive** analysis layer
over the trace a run already produced. It is a pure function of its input: no
clock, no randomness, no network, no model, no tool, no gateway, no policy, no
agent rerun and no trace mutation. Evaluating identical input twice returns an
equal `EvaluationResult`.

```python
evaluator = TraceEvaluator()
result = evaluator.evaluate(EvaluationInput.from_events(read_events(path)))
result = evaluator.evaluate_trace(path)  # convenience: read + evaluate
```

`EvaluationInput` reuses the existing trace representation (the parsed event
mappings), so there is no second event model. `EvaluationResult` carries the run
identity, the implementation `version` (`"v1"`, static), the run `status`
(`completed` / `failed` / `step_limit` / `incomplete`), the descriptive numbers,
flags, evidence pointers and warnings.

### Descriptive measurements only

Everything is read straight off an event; nothing is combined into a score and
nothing is called a "security" measurement beyond what an event records.

* `metrics` - counts per event type (`model_request`, `tool_requested`, ...)
  plus `total_events`, and 1:1 aliases such as `model_calls`, `tool_requests`,
  `tool_executions`, `tool_results`, `agent_outputs`, `security_events`.
* `decisions` - `policy_decision` counts by outcome (`allow`, `deny`,
  `require_approval`), preserved exactly as recorded.
* `tool_calls` - `tool_requested` counts by tool name.
* `tool_results` - observable outcome per tool request: `ok`, `error` (executed,
  failed), `denied`, `pending_approval`, `not_executed`, `no_result`. A request
  is never counted as a success just because it happened.
* `flags` - `has_run_started`, `has_terminal_event`, `produced_final_output`,
  `reached_step_limit`, `has_tool_requests`.

Scenario-specific outcomes (for example whether an attack succeeded) are **not**
here; they belong to the scenario framework, which can interpret these generic
signals. No composite/risk/safety score is produced.

### Malformed or incomplete traces

The evaluator prefers a result with `warnings` over raising, so an incomplete
trace can never look like a clean pass without a note. It warns on an empty
trace, a missing `run_started`, a missing or duplicated terminal event,
non-increasing `seq` values, unclassified events, a `policy_decision` /
`tool_executed` / `tool_result` with no matching `tool_requested`, a
`model_response` with no matching `model_request`, and a `tool_requested` with no
result. It raises `EvaluationError` only when the input cannot be read at all
(unreadable file or invalid JSON), never for content problems.

### What the evaluator deliberately does not do

It does not execute tools, call a model, invoke the gateway or policy engine,
rerun the agent, modify traces, inspect provider internals, or compute any
invented/weighted metric.

## Policy model

The policy engine is deliberately tiny. Decisions are `allow`, `deny` or
`require_approval`. A policy is a flat, ordered list of rules plus a `default`
(which defaults to `deny`). **First matching rule wins.** There are no roles, no
inheritance and no attribute-based engine. A rule matches on `subject`
(`*` wildcard), `tool`, `action`, an optional `resource` glob, and an optional
`conditions` mapping. The only condition understood today is
`outside_task_scope`; an unknown condition key is a configuration error so a
typo cannot silently weaken a policy. The engine knows nothing about concrete
tools: the gateway derives `action` and `resource` from the tool's metadata.

```yaml
default: deny
rules:
  - id: allow-calc
    subject: "*"
    tool: calculator
    action: invoke
    decision: allow
    reason: "read-only helper"
  - id: db-read-requires-approval
    subject: "*"
    tool: mock_db
    action: read
    decision: require_approval
    reason: "database reads need an explicit approval"
```

Load with `agentsec.policy.load_policy(path)` (or `PolicyEngine.from_yaml`).
Malformed YAML, a non-mapping document, an unknown decision, a missing field or
an unknown condition key all raise `PolicyConfigError`. A policy that cannot be
understood never silently becomes permissive.

## Redaction

`agentsec.trace.redact.Redactor` redacts known secret patterns and sensitive
mapping keys to `[REDACTED:<kind>]`. It is deterministic and idempotent, and can
hash content-bearing values (`hash_value`). Redaction happens before writing,
so no write path bypasses it. This is best-effort and **not** a DLP system.

## Safety limitations

* The sandbox tools are safe by construction rather than by OS enforcement:
  there is no host filesystem, database or network access, so there is nothing
  to escape to. `shell_sandbox` and any real tool are out of scope.
* `mock_db` values are synthetic, including one planted fake secret
  (`FAKE_SECRET_DB001`) so leakage labs have a detectable sink. It is not a real
  credential.
* The policy engine is a teaching model, not a production authorization system.
* Malicious student payloads should target only these synthetic tools.

## Scenarios

The scenario layer lets the Lab describe one controlled experiment and interpret
its observable result, **without** putting scenario-specific semantics into the
Agent, ToolGateway, PolicyEngine, Evaluator, ExperimentRunner or CLI. A scenario
is declarative and read-only; it is not a second runner.

```
Scenario.prepare() -> ExperimentConfig
        |                       (run with the existing ExperimentRunner)
        v
ExperimentResult  ->  Scenario.interpret(result)  ->  ScenarioOutcome
```

```python
scenario = load_scenario("scenarios/benign.yaml")
result = runner.run(scenario.prepare())          # the existing runner
outcome = scenario.interpret(result)             # passed / failed / inconclusive
```

A `ScenarioDef` is composed, not copied: it carries `scenario_id`, `title`,
`description`, an `ExpectedObservation`, and the existing `ExperimentConfig`. No
task, agent, policy or mock-script field is duplicated.

### Expected vs observed

`ExpectedObservation` holds optional, plain expectations about values the
generic evaluator already reports - run/agent status, step limit, tool-request /
-execution counts, policy denial / approval counts, tool-result outcomes,
requested tools and final output. Each set field produces one `ObservationCheck`
with `expected`, `observed` and `matched`. The generic evaluator has no idea what
"passed" means; that interpretation lives here. There is no score, no weighting,
no ranking and no new security metric.

### ScenarioOutcome

`ScenarioOutcome` records `scenario_id`, `run_id`, a status of `passed` /
`failed` / `inconclusive`, the checks, evidence, warnings and an optional
error. Evidence reuses the evaluator's existing `EventRef` pointers - there is no
second reference system - so a reader can see *why* an outcome was reached
without touching the trace.

### Inconclusive, not silently passing

An outcome is `inconclusive` (never a silent pass) when there is no evaluation,
when the result's `run_id` does not match the scenario's expected run id, when
the evaluation is incomplete, or when no expectations are defined. Observation
mismatches are `failed`; they are reported in the outcome, not raised.
Configuration problems (bad YAML, missing fields, duplicate/unknown ids) raise
`ScenarioConfigError`.

### Registry

`ScenarioRegistry` is an explicit, deterministic in-memory map of
`scenario_id -> Scenario`. Registration is manual; there are no dynamic imports,
plugin discovery, filesystem scanning or code execution from configuration.

### What the scenario layer deliberately does not do

It does not run the agent, execute tools, evaluate policy, write or mutate
traces, compute metrics, retry, or run anything in parallel. It prepares
configuration and interprets an already-produced `ExperimentResult`.

## Labs

The student labs live under `labs/` and run **LAB-00 … LAB-07**; the current MVP
lab sequence **ends at LAB-07** (there is deliberately no LAB-08). They add **no
new runtime code**: a lab is a configuration to run plus a scenario that
declares the observations a correct run should produce.

| Lab | Purpose | Files |
|---|---|---|
| `LAB-00-setup` | Verify the environment: package import, CLI, a benign run, a trace and its evaluation - all offline. | `README.md`, `config.yaml` |
| `LAB-01-benign-agent` | Observe a normal agent lifecycle: task -> model -> tool request -> policy decision -> tool execution -> tool result -> final answer. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-02-direct-prompt-injection` | Observe an untrusted instruction placed **directly in the task** change what the agent does. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-03-indirect-prompt-injection` | Observe an untrusted instruction arriving **through content a sandbox tool returns**, then driving a follow-up tool request. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-04-tool-misuse` | Observe a **legitimate tool requested with an out-of-scope argument**; the policy denies it, so the tool never executes. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-05-require-approval` | Observe the third policy decision: a legitimate request answered with **`require_approval`**, held pending, so the tool does not execute without authorization. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-06-excessive-agency` | Observe an **authorized but unnecessary** state-changing action: the policy says `allow`, the tool **executes**, and a synthetic side effect is recorded - authorization does not establish necessity. | `README.md`, `config.yaml`, `scenario.yaml` |
| `LAB-07-data-leakage` | Observe an **authorized egress**: a task-requested, policy-allowed read of a synthetic record followed by a policy-allowed `mock_email` send - every operation is permitted, yet the synthetic content crosses a data boundary. An educational demonstration of observable, authorized, **synthetic** egress: **not** real exfiltration, an autonomous leak, a vulnerability demo, a propensity measurement or a security benchmark. | `README.md`, `config.yaml`, `scenario.yaml` |

`config.yaml` is an ordinary `ExperimentConfig` run with
`agentsec run <config.yaml>`. `scenario.yaml` is a `ScenarioDef`: it embeds the
*same* experiment (a test asserts the two files match, so they cannot drift) and
lists the `expected` observations. The scenario is read-only - it prepares the
configuration and interprets the finished `ExperimentResult`; it never runs the
agent, executes a tool or writes a trace.

The labs are purely **student-facing**: deterministic, offline, sandboxed and
synthetic (mock model, in-memory calculator/filesystem/database). Their
validation tests live in `tests/labs/` and are ordinary offline tests, not a
separate framework. Students read the learning objectives, run the commands and
answer the questions in the lab README; the scenario test supplies the
`passed` / `failed` verdict.

The labs make **no research-novelty claim** and are not a benchmark. LAB-07 in
particular is an educational demonstration of observable, authorized, synthetic
egress/data-boundary behaviour - it is **not** autonomous real-world leakage, a
vulnerability demonstration, real exfiltration, a model-propensity measurement
or a security benchmark. Teaching established concepts is the point; it is not a
research contribution (see the Phase 17 section above).

## Command-line interface

The CLI is only a **thin user interface** over the existing components. It loads
a configuration, asks the MVP composition root for a ready `ExperimentRunner`,
runs it once, and renders the result. It contains no agent loop, tool dispatch,
policy evaluation, model call or metric calculation.

```bash
agentsec run configs/examples/benign.yaml          # run one experiment
agentsec run configs/examples/benign.yaml --json   # machine-readable result
agentsec evaluate trace.jsonl                       # read-only trace analysis
agentsec evaluate trace.jsonl --json
agentsec inspect trace.jsonl                        # short trace summary
agentsec labs check                                 # verify every canonical lab
```

`agentsec run` reads the configuration with `load_experiment_config`, wires the
deterministic MVP stack (`agentsec.mvp.build_mvp_runner`: mock model + sandbox
tools + policy + recorder + agent + evaluator + runner), executes exactly one
run, and prints the `ExperimentResult`. The optional `policy_path` selects a
policy file (default: deny-by-default) and `mock_script` selects the mock
fixture script (default: `benign`).

`agentsec evaluate` reads a trace, builds an `EvaluationInput` and calls the
existing `TraceEvaluator`; it never reruns the agent, executes a tool or mutates
the trace. `agentsec inspect` prints a short textual summary (run id, event
count, event sequence and parent links) - it is not a viewer.

`agentsec labs check` re-runs every canonical lab (`labs/LAB-00` … `labs/LAB-07`)
through the same deterministic MVP stack into a **temporary** directory and
compares each result against the lab's own declared expectations (its
`scenario.yaml` `expected` observations; LAB-00 has no scenario and is checked as
a setup smoke test). It is an offline reproducibility/teaching check: it adds no
metric, score, ranking or security claim, writes nothing into `runs/`, and prints
a per-lab PASS/FAIL summary with a non-zero exit code if any lab fails. See
`labs/README.md` for the description aimed at students and instructors.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | the command completed and produced a result. Experimental outcomes - a denied tool, a pending approval, a step limit, even an agent failure - are *results*, not CLI errors, so they keep `0`. |
| `1` | a configuration/usage/input problem (bad or missing config, unknown mock script, unreadable or invalid trace, bad arguments), or one or more labs failing `agentsec labs check`. |
| `2` | an orchestration failure after a valid configuration (for example a trace that could not be read or written). |

### Packaging

The console entry point is declared in `pyproject.toml`:

```toml
[project.scripts]
agentsec = "agentsec.cli:main"
```

Until the package is installed, it is also runnable from a checkout with
`PYTHONPATH=src py -m agentsec ...`.

## Note on the repository README

The repository root `README.md` belongs to the surrounding research project and
is intentionally left untouched. The student-facing lab README and the MkDocs
site are later steps (see `research/14-implementation-blueprint.md`).
