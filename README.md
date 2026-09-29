# Agent Security Labs

**Offline, deterministic AI-agent security labs — learn by reading the trace.**

📖 **Live documentation site:** <https://nadeem-majeedch.github.io/agent-security-labs/>

Eight small labs, **LAB-00 … LAB-07**. Each one runs a single deterministic
experiment, writes a **trace** (one JSON event per line), and lets you read that
trace and answer one question with evidence:

> **"What can I actually observe in the trace?"**

There is deliberately **no LAB-08**. These labs are **educational
infrastructure**: they make **no research claim**, they are **not a benchmark**,
and the model they run against is a **deterministic fixture**, not a real LLM.

---

## What Agent Security Labs is

An **offline, deterministic, mediated-agent security laboratory**.

`agentsec` runs a small agent loop against a **scripted model fixture** and a set
of **in-memory tools**. Every tool call passes through a single mediated path —
the **tool gateway** — which validates the arguments, records the request,
records an **explicit policy decision**, and only then either executes the tool
or refuses it. Each run writes a **JSONL trace** that you can inspect, evaluate
and reason about without re-running anything.

Nothing here touches a real system: the filesystem, database and mail sink are
in-memory, and there is no network, no API key and no model provider involved.

**Current status:** an existing, working artefact — not a plan. The package, the
eight labs, the test suite, the offline self-check, the documentation site and
the CI workflows are all implemented and verified at this revision.

---

## What you can learn

Read a trace left to right as **one request's path** — what was asked for, what
policy decided, whether the tool really ran, and whether anything changed:

| Stage | Event | What it does **not** prove |
| --- | --- | --- |
| Model turn | `model_request` / `model_response` | that a tool was requested |
| **Requested** | `tool_requested` | that the tool ran |
| **Decided** | `policy_decision` (`allow` / `deny` / `require_approval`) | that the tool ran |
| **Executed** | `tool_executed` | *(nothing — this is the evidence that it ran)* |
| **Result** | `tool_result` (`ok`, `denied`, `pending_approval`, …) | that anything changed |
| Change | `tool_result.side_effects` | that anything real was touched |

Every event links to the one before it (`parent_event_id`), so the whole chain —
**task → response → request → policy → execution → result → answer** — is
reconstructable from the trace alone.

### Eight distinctions to carry across every lab

These are the ideas the labs are built to make visible. They are teaching
distinctions, not measurements.

1. A **model response** is not the same as a **tool request**.
2. A **tool request** is not proof that the tool **executed**.
3. The **policy decision** happens **before** execution.
4. A **`deny`** decision prevents execution.
5. A **`require_approval`** decision does **not** mean execution happened.
6. An **`allow`** followed by a **`tool_executed`** event means the tool
   **really ran**.
7. A successful execution may produce a **synthetic side effect**.
8. A **`tool_result`** can exist for a denied request **even though no
   `tool_executed` event exists** (same for a pending-approval request).

Two more that LAB-07 makes concrete:

9. LAB-07 shows **authorized, synthetic egress** — it is **not** real-world
   exfiltration and does **not** demonstrate a vulnerability.
10. Because the model is a **deterministic fixture**, what you observe is the
    **mechanics of a security boundary**, not the behaviour of a real model.

The same columns are laid out per lab in the
[observables matrix](labs/README.md#the-observables-matrix).

---

## What is included

| Area | Contents |
| --- | --- |
| [`src/agentsec/`](src/agentsec) | the `agentsec` package: agent loop, tool gateway, policy engine, trace schema/recorder/redaction, descriptive evaluator, declarative scenarios, experiment runner, composition root and CLI |
| [`labs/`](labs) | **LAB-00 … LAB-07** — each a `README.md` plus `config.yaml` (and a `scenario.yaml` for LAB-01 … LAB-07) |
| [`labs/TRACE-WALKTHROUGHS.md`](labs/TRACE-WALKTHROUGHS.md) | an event-by-event walkthrough of the trace each lab produces |
| [`labs/TRACE-READING-EXERCISES.md`](labs/TRACE-READING-EXERCISES.md) | 36 practice exercises (sets A–G) plus a final challenge, with an instructor-only [answer key](labs/TRACE-READING-EXERCISES-ANSWER-KEY.md) |
| [`policies/examples/`](policies/examples) | four example policies (`deny_by_default`, `least_privilege_v1`, and one per-lab policy each for LAB-06 and LAB-07) |
| [`schemas/trace/`](schemas/trace) | the versioned trace-event JSON Schema (`v1`), generated from the models with a drift test |
| [`tests/`](tests) | the offline test suite (see [verification status](#verification-status)) |
| [`mkdocs.yml`](mkdocs.yml) | the MkDocs configuration for the published documentation site |
| [`.github/workflows/`](.github/workflows) | `ci.yml` (tests + lab self-check) and `docs.yml` (strict build + GitHub Pages) |

---

## How it works

| Component | Role |
| --- | --- |
| **Agent loop** ([`agent.py`](src/agentsec/agent.py)) | the smallest deterministic model/tool loop; it knows only a `ModelAdapter` and a `ToolGateway` — it never executes a tool or evaluates a policy |
| **Tool gateway** ([`tools/gateway.py`](src/agentsec/tools/gateway.py)) | the **single mediated path** for every tool call: validate → record request → policy decision → execute or refuse → record result |
| **Policy engine** ([`policy/`](src/agentsec/policy)) | a deliberately small engine: a flat, ordered rule list plus a default, first match wins, three decisions only — `allow`, `deny`, `require_approval` |
| **Tools** ([`tools/`](src/agentsec/tools)) | four in-memory tools: `calculator` (AST-restricted arithmetic), `fs_sandbox` (virtual filesystem), `mock_db` (synthetic database), `mock_email` (in-memory egress sink) |
| **Deterministic fixture** ([`models/mock.py`](src/agentsec/models/mock.py)) | a scripted, clock-free, RNG-free model whose response is a pure function of the messages and the script — a **test fixture, not an LLM** |
| **Trace** ([`trace/`](src/agentsec/trace)) | a versioned 12-event schema, an append-only JSONL recorder with redaction-before-write, and a validator |
| **Descriptive evaluator** ([`eval/builtin.py`](src/agentsec/eval/builtin.py)) | read-only counts, decisions, tool-result outcomes, flags and warnings — it computes **no score** and re-runs nothing |
| **Declarative scenarios** ([`scenarios/`](src/agentsec/scenarios)) | each lab declares its expected observations; the scenario interprets an already-finished run and reports `passed` / `failed` / `inconclusive` |
| **CLI** ([`cli.py`](src/agentsec/cli.py)) | a thin interface: `run`, `inspect`, `evaluate`, `labs check` — it contains no execution logic |

The full architecture reference is in [`docs/development.md`](docs/development.md).

---

## Reproducibility

What the artefact supports, precisely:

- **Deterministic fixture.** The model is scripted: identical inputs produce the
  same responses, and it consults no clock or RNG (`latency_ms` is always `None`).
  It reports that it supports neither `temperature` nor `seed`, and refuses
  either parameter rather than pretending to honour it.
- **Injectable clock.** The trace recorder accepts a clock, and `event_id` is
  `ev-<seq>`, so a run replayed with a **fixed clock** is byte-identical. The
  test suite and the `labs check` self-check both inject that fixed clock.
- **Ordinary runs use the real clock.** A plain `agentsec run` does not inject a
  clock, so two default runs of the same configuration have **different
  `timestamp` values** — everything else (event order, ids and content hashes) is
  reproducible.
- **Offline operation.** No network, no credentials, no provider, no database
  server, no Docker and no GPU. In-memory tools enforce containment: a request
  cannot leave the sandbox.
- **One run, one trace.** The runner orchestrates exactly one run — no retries,
  no batches, no parallelism — and validates that configuration, agent and
  recorder agree, so one run writes one coherent trace.
- **Automated tests and an offline self-check.** See
  [verification status](#verification-status) below.

---

## The labs

| Lab | Security concept | One line |
| --- | --- | --- |
| [LAB-00 Setup](labs/LAB-00-setup/README.md) | *(warm-up)* | Prove your setup works end to end: run, trace, evaluate. |
| [LAB-01 Benign agent](labs/LAB-01-benign-agent/README.md) | Benign baseline | See what a normal, cooperative run looks like. |
| [LAB-02 Direct prompt injection](labs/LAB-02-direct-prompt-injection/README.md) | Direct prompt injection | An instruction arrives **straight in the task**. |
| [LAB-03 Indirect prompt injection](labs/LAB-03-indirect-prompt-injection/README.md) | Indirect prompt injection | An instruction arrives **inside content a tool returns**. |
| [LAB-04 Tool misuse](labs/LAB-04-tool-misuse/README.md) | Tool misuse | No injected instruction — the **requested operation** is out of scope. |
| [LAB-05 Require approval](labs/LAB-05-require-approval/README.md) | Require approval | A legitimate request is **held for authorization** instead of refused. |
| [LAB-06 Excessive agency](labs/LAB-06-excessive-agency/README.md) | Excessive agency | The action is **allowed and executes**, though the task never needed it. |
| [LAB-07 Data leakage](labs/LAB-07-data-leakage/README.md) | Data leakage | An **authorized read + authorized send** still move content across an egress boundary. |

The labs are **not ranked**: each isolates a different question, and none is
"worse" or "better" than another.

---

## Getting started

Requires **Python 3.11+** (`py` on Windows, `python` elsewhere) and a terminal in
the repository root. No API key and no network connection are needed.

```bash
# 1. install (documentation and test extras are optional)
py -m pip install -e ".[dev]"

# 2. run your first lab — this writes a trace
PYTHONPATH=src py -m agentsec run labs/LAB-00-setup/config.yaml

# 3. list the events it wrote, in order
PYTHONPATH=src py -m agentsec inspect runs/lab00_setup/trace.jsonl

# 4. evaluate the trace on its own (read-only; re-runs nothing)
PYTHONPATH=src py -m agentsec evaluate runs/lab00_setup/trace.jsonl

# 5. confirm every lab still behaves as documented
PYTHONPATH=src py -m agentsec labs check
```

Then:

- **[`labs/GETTING-STARTED.md`](labs/GETTING-STARTED.md)** — the guided path from
  install to reading your first trace.
- **[`labs/README.md`](labs/README.md)** — the lab map, the observables matrix
  and the event vocabulary.
- **[`labs/LOCAL-VERIFICATION.md`](labs/LOCAL-VERIFICATION.md)** — what
  `agentsec labs check` verifies and what it deliberately does **not** claim.
- **[`labs/INSTRUCTOR-GUIDE.md`](labs/INSTRUCTOR-GUIDE.md)** — instructor-facing
  teaching material: sequence, timings, discussion prompts and a marking rubric
  (it does not contain the exercise answers).

Build the documentation site locally with
`py -m pip install -e ".[docs]"` and `py -m mkdocs build --strict`.

---

## Documentation site

**<https://nadeem-majeedch.github.io/agent-security-labs/>**

The site is built from the lab documentation itself (`docs_dir: labs` in
[`mkdocs.yml`](mkdocs.yml)), so there is no second copy to keep in sync, and it is
published to GitHub Pages by [`docs.yml`](.github/workflows/docs.yml) on pushes to
`main`. It contains Getting Started, the Lab Map, the trace walkthroughs, the
practice exercises, the instructor guide and the local-verification page. The
instructor answer key is built but intentionally not part of the site navigation.

---

## Verification status

Re-run locally at this revision:

| Check | Command | Result |
| --- | --- | --- |
| Licence metadata and file coverage | `py scripts/check_licensing.py` | **9/9 checks pass** (exit 0) |
| Test suite | `PYTHONPATH=src py -m pytest` | **719 tests pass** (exit 0) |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs pass** (exit 0) |
| Documentation build | `py -m mkdocs build --strict` | **builds with no warnings or errors** (exit 0) |

[`ci.yml`](.github/workflows/ci.yml) checks the licence metadata first, then runs
the test suite and the lab self-check, on every push and pull request — so a
change that breaks a canonical lab scenario, that lets the licensing
declarations drift apart, or that adds a file with no recorded licensing
treatment, fails the build.

---

## What this project does **not** claim

- It is **not a benchmark**, and it is not a scoring system or a ranking of
  attacks.
- It does **not** claim **research novelty**. The concepts taught here are
  established ones, reimplemented as small, inspectable, deterministic
  observations for teaching.
- It does **not** claim **security effectiveness** and does **not** assert that
  any policy is "effective" or that any attack "succeeds".
- It does **not** claim anything about **real model or agent behaviour**. The
  model is a deterministic fixture; repeated runs demonstrate determinism, not a
  distribution over real behaviour.
- It is **not** a measurement of real-world data leakage. LAB-07's transfer is
  task-requested, policy-authorized and entirely synthetic, in memory only.
- It is **not** a production framework and **not** a content-filtering or DLP
  system. Redaction is best-effort by design.
- It makes **no paper claim**: there is no abstract, no paper and no draft.

**Research boundary.** The research status recorded in
[`docs/development.md`](docs/development.md) stands: the Phase 17 research
transition is **CLOSED**, previously closed research directions **remain closed**,
and no research experiment, benchmark or real-model integration is included or
authorised here.

---

## Who this is for

| Audience | Start here |
| --- | --- |
| **Students** | [`labs/GETTING-STARTED.md`](labs/GETTING-STARTED.md), then the labs in order, then [`labs/TRACE-READING-EXERCISES.md`](labs/TRACE-READING-EXERCISES.md) |
| **Instructors** | [`labs/INSTRUCTOR-GUIDE.md`](labs/INSTRUCTOR-GUIDE.md) (teaching sequence, rubric, discussion prompts) |
| **Researchers / reviewers** | [`docs/development.md`](docs/development.md) for the architecture and status; [`schemas/trace/`](schemas/trace) and [`src/agentsec/`](src/agentsec) for the implementation; [`tests/`](tests) for what is enforced; [`labs/LOCAL-VERIFICATION.md`](labs/LOCAL-VERIFICATION.md) to reproduce the lab checks |
| **History of the research direction** | [`research/12-research-direction-selection-audit.md`](research/12-research-direction-selection-audit.md), [`research/13-lab-scope-and-architecture.md`](research/13-lab-scope-and-architecture.md), [`research/14-implementation-blueprint.md`](research/14-implementation-blueprint.md) (historical records; not rewritten) |

---

## Repository status

- **Existing, working artefact** — the package, the eight labs, the test suite,
  the offline self-check, the documentation site and the CI workflows are
  implemented at this revision.
- **Requirements:** Python 3.11+; three runtime dependencies (`pydantic`,
  `jsonschema`, `PyYAML`). `httpx` is declared as an optional extra for a future
  live adapter that **does not exist**; MkDocs is an optional `docs` extra.
- **Licences: MIT for the software, CC BY 4.0 for the content.** The same
  software licence is declared in [`pyproject.toml`](pyproject.toml) and
  [`CITATION.cff`](CITATION.cff). See [Licensing](#licensing) for the exact
  boundary.
- **No LAB-08**, deliberately; the lab sequence ends at LAB-07.
- **No live model provider**, no network functionality and no defences are
  included: the adversarial labs observe behaviour only.

---

## Licensing

Two licences, split along one line: **what the harness parses is MIT; what a
person reads is CC BY 4.0.**

| Material | Licence | Licence file |
| --- | --- | --- |
| **Software** — `src/`, `tests/`, `scripts/` | MIT | [`LICENSE`](LICENSE) |
| **Machine-readable configuration** — `policies/`, `configs/`, `labs/**/*.yaml`, `schemas/`, `research/tables/*.csv`, `mkdocs.yml`, `pyproject.toml`, `.github/` | MIT | [`LICENSE`](LICENSE) |
| **Documentation and educational text** — `README.md`, `docs/`, `labs/**/*.md`, `research/**/*.md` | CC BY 4.0 | [`LICENSE-DATA`](LICENSE-DATA) |

So the labs' YAML is MIT while the instructions that explain them are CC BY 4.0.
You may reuse and adapt the exercises, walkthroughs and instructor material —
including in your own teaching — provided you give attribution and indicate what
you changed. [`LICENSE-DATA`](LICENSE-DATA) carries the exact scope notice, a
ready-made attribution string and the full text of the licence.

Third-party material cited or quoted in `research/` is covered by **neither**
grant: titles, author names, venues, DOIs and quotations remain the property of
their respective owners and are included for citation and identification only.
No third-party image, figure, dataset or lengthy excerpt is redistributed here.

CI keeps these declarations from drifting apart.
[`scripts/check_licensing.py`](scripts/check_licensing.py) re-reads `LICENSE`,
`LICENSE-DATA`, `pyproject.toml`, `CITATION.cff` and this README, and fails the
build if they stop agreeing about which licence applies to what.

It then checks **coverage**. Every path in this repository is recorded
explicitly in [`licensing/manifest.toml`](licensing/manifest.toml) as MIT,
CC BY 4.0, outside both grants, deliberately undecided, or generated material
that is not distributable content. A file that no entry accounts for — a new
one, typically — fails the build until somebody records what it is, so
licensing is a decision that has to be made rather than a side effect of a file
extension. The checker compares the repository's own declarations: it does
**not** establish ownership, and it does not determine the licence of any
third-party material.

---

## Citation

Machine-readable citation metadata is provided in [`CITATION.cff`](CITATION.cff).
If you reference this repository, please cite it as:

> Majeed, M. N. (2026). *Agent Security Labs* (version 0.0.1) [Computer software].
> MIT Licence. <https://github.com/nadeem-majeedch/agent-security-labs>

This citation identifies the **software** only. It does not assert that a study
has been conducted, that any learning outcome has been measured, or that any
result has been published.
