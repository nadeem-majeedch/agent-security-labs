# 12 — Research Direction Selection Audit (Phase 12)

**Status: PHASE 12 COMPLETE — RESEARCH COMMITMENT: 3 (BUILD INFRASTRUCTURE WITHOUT PAPER COMMITMENT)**

**Date of audit:** 26 September 2026
**Purpose:** decide whether any research direction is worth months of implementation and experimentation. This phase performs **no new open-ended gap hunting**; it consolidates Phases 1–11 and applies explicit decision gates.
**Outcome:** **OUTCOME C — only infrastructure/education outputs survive; no paper direction is mature.** Explicit verdict: **NO RESEARCH COMMITMENT RECOMMENDED AT THIS TIME.**

**Standing rules honoured:** no forced novelty, no manufactured gap, no engineering project called a research contribution, no acceptance predictions, no ranking, no scores. Prior conclusions are cross-referenced, not rewritten.

---

## Part 0 — Method and labels

Consolidation used the existing artifacts: `research/01`–`research/11` and their matrices. No literature was re-searched except where a candidate demanded it; where a candidate was not audited, this is marked **NOT TESTED** rather than assumed.

Claim tags: **[FACT]** · **[INFER]** · **[HYP]** · **[OPEN]**. Source labels **A/B/C** as in `sources.csv`.

---

## Part 1 — Consolidated map of Phases 1–11

### 1.1 What was exhausted or repeatedly closed

| Phase | Direction attempted | Result | Decisive occupant(s) |
|---|---|---|---|
| 1 | Agent-security landscape / benchmark gap | Gaps rejected; multi-model eval, adaptive attacks, security–utility trade-off saturated | AgentDojo, ASB, AgentDyn |
| 2 | Capability-vs-security (inverse scaling) | Confound identified; **resource-infeasible**; recommended question never run | AgentDojo confound; MCPTox reasoning-mode; RAS-Eval mischaracterisation |
| 3 | ASR decomposition | Occupied | Pathade et al. (R52); REDAgentBench (R77) |
| 4 | Evaluation stability / repetitions | Reversed verdict; residual subsumed | Alvarado (R61); Miller (R72); Khan (R70) |
| 5 | Novelty audit of the stability direction | **NO-GO** (contributions 1–4 subsumed) | R52, R61, R72, R68, R70 |
| 6 | Repetition vs attack budget | **NO-GO** | Chouldechova et al. (R74) |
| 7 | Judge validity | **NO-GO** | Eiras (R78); REDAgentBench (R77); SoK (R79) |
| 8 | Agent-security mechanisms | **SURVIVORS: 0** (15 areas occupied; 12 with 2026 systematizations) | R91–R125 |
| 9 | Cross-domain (data science / SE / reproducibility) | **SURVIVORS: 0** | CoE (R127); ReAgent (R128); Traverse/Scout (R129); Agentic Forking Paths (R131) |
| 10 | Performance audit × AI | **SURVIVORS: 0** | IntelliAudit (R169); econometrics agents (R170–R178) |
| 11 | Empirical anomalies / contradictions | 18 CLOSED, 2 verified and killed → **0 survivors** | R204 (S1); R205/R206 (S2) |

**[FACT]** Across eleven phases the surviving research direction count is **zero**.

### 1.2 Recurring reasons ideas were rejected

1. **Recent occupancy.** A 2025–2026 primary paper (often within months) already does the work.
2. **Measurement-validity explanation already published.** The hidden variable (estimand, budget, evidence view, judge bias, compute) is already named.
3. **Artifact already released.** Benchmark/standard/tool shipped with code.
4. **Resource block.** No capability spread; no GPU for white-box adversarial optimisation; four Flash-tier models only.
5. **Shape violation.** "Another benchmark", "another dataset", "a literature gap", or "a new application" is not novelty.
6. **Replication alone.** Not publishable without a new boundary condition or mechanism.

### 1.3 Resource limitations (carried forward)

* **[FACT]** Four Flash/mini-tier models, three from one region; no frontier model; no verified parameter counts; no capability ladder (R35–R38, Phase 2 §9).
* **[FACT]** No GPU cluster; white-box GCG-style work is out of reach (Phase 8, R97).
* **[FACT]** Reproducibility hazards: DeepSeek temperature inert in default thinking mode; GLM thinking cannot be disabled; peak/off-peak pricing; unpinned commercial revisions (R35, R37).

### 1.4 Types of novelty that remain realistic

**[INFER]** Given the above, the only realistically achievable contribution types are **K (open-source infrastructure/tooling)**, **L (educational)**, and *conditionally* **H/J** (replication/characterization) where a genuinely untested boundary exists. Explanatory (C), new-phenomenon (B), and new-problem (A) contributions have been ruled out eleven times for this resource profile.

---

## Part 2 — Decision matrix of novelty types

Neutral; no ranking, no scores.

| Type | Publication value (typical) | Feasibility (our resources) | Preemption risk | Implementation required | Frontier-model dependence | Reproducibility |
|---|---|---|---|---|---|---|
| A New problem | High | Low | High | High | Often | Variable |
| B New phenomenon | High | Low–Medium | High | High | Often | Variable |
| C New explanation/mechanism | High | Low–Medium | High | Medium–High | Sometimes | Medium |
| D New algorithm | Medium–High | Medium | Medium | High | Sometimes | High |
| E New benchmark | Medium | Medium | **Very high** | High | Sometimes | High |
| F New dataset | Low–Medium | Medium | High | Medium | Rarely | High |
| G New evaluation methodology | Medium–High | Medium | High | Medium | Sometimes | High |
| H Replication/extension | Low–Medium | **High** | Low | Medium | Rarely | **High** |
| I New application/domain | Low–Medium | **High** | Medium | Medium | Rarely | High |
| J New empirical characterization | Medium | Medium–High | High | Medium | Sometimes | High |
| K Open-source infrastructure/tooling | Low as research; high as utility | **High** | Medium (crowded but tolerated) | High | Rarely | **High** |
| L Educational contribution | Low as research; high as utility | **High** | Low | Medium | Rarely | Medium |

**[INFER]** The only rows where feasibility is high *and* resource dependence is low are **H, I, J, K, L**. A, B, C are exactly the rows Phases 1–11 repeatedly failed to secure.

---

## Part 3 — The three broad strategies

### Strategy A — AI Agent Security Lab (infrastructure)

1. **Infrastructure or research?** **[INFER] Primarily infrastructure.** Phase 8 established that public, maintained harnesses already exist (AgentDojo, NIST/CAISI's `agentdojo-inspect`, UK AISI Inspect, ASB, AgentDyn). A new harness is not a novel mechanism.
2. **What would make it scientifically publishable?** Only if it *constructs* something the literature declares missing (Phase 8 Part T: a deterministic mediator for the class R99 calls irreducible) — which our resource profile cannot build.
3. **What merely makes it engineering?** Reproducing existing attacks/defences with a different orchestration layer.
4. **Differentiation?** Not established. Cost/repetition awareness is a feature, not a mechanism; Phase 6/7 showed the measurement-side is occupied.
5. **Venues for tooling:** systems/tool demonstration tracks and journal software sections exist, but they require demonstrated, differentiated utility.
6. **Required empirical evidence:** a result an existing harness cannot produce — **[OPEN]** and not currently identified.
7. **Value without a paper?** **Yes, high** — teaching and open-source reuse.

### Strategy B — Replication / extension

1. **Can replications contribute here?** **[INFER] Yes, but only with a genuine boundary condition or mechanism**, not a model or language substitution.
2. **Scientific extension vs rerunning code:** the extension must test a stated boundary the original left open and be pre-registered as such.
3. **How much novelty?** Enough to change the *scope* of the original claim (a boundary, a reversal, a transfer question with a mechanism), not merely to re-measure.
4. **Suitable recent results:** R206 (coverage/mutation vs fault detection, Java only) is the best-fit replication target for our resources; R74/R75 (repetition/budget) are already fully explained and unsuitable.
5. **Realism:** plausible for empirical-SE venues **conditionally**, if and only if a discriminating boundary is identified; otherwise not.

### Strategy C — New applied research direction outside the saturated cluster

**[FACT]** Phase 9 (data science / SE / reproducibility) and Phase 10 (performance audit) both returned **SURVIVORS: 0**: benchmarks, standards, verifiers, evidence chains and econometric agents already exist. **[INFER]** The same occupancy logic applies to adjacent applied domains. The one direction *not* audited in Phases 1–11 is **computing education / AI-assisted learning**, which therefore remains **NOT TESTED** rather than promising.

---

## Part 4 — Eight concrete candidates

Full field-level record: `research/tables/research-direction-selection-matrix.csv`.

* **C1** Reproducible agent-security evaluation harness (infrastructure).
* **C2** Language/ecosystem extension of the LLM test coverage–fault-detection study (Python; four Flash models).
* **C3** Repetition-vs-budget design-effect replication.
* **C4** Scaffolded AI coding-agent lab and novice learning outcomes (education).
* **C5** Reproducibility study of published performance-audit findings against open data.
* **C6** Inferential-validity characterization of AI data-analysis agents.
* **C7** Hybrid teaching lab that doubles as an evidence-generating platform.
* **C8** Reproducible re-measurement of a published network-security result.

Each has a stated concrete question, hypothesis, novelty type, competitor, method, resources, risks and kill condition in the CSV.

---

## Part 5 — Hostile competitor check

| Candidate | Has it been done? | Mechanism already proposed? | Benchmark already built? | Boundary already evaluated? | Merely model substitution? | Depends on inaccessible resources? | Collapse risk under full-text audit |
|---|---|---|---|---|---|---|---|
| C1 | Yes (harnesses) | n/a | Yes | n/a | No | No | Low (already accepted as engineering) |
| C2 | Partially (R206, Java) | n/a | Yes (Defects4J) | Boundary untested | **Risk: yes** | No | Medium |
| C3 | Yes | Yes (R74/R75) | n/a | Yes | Partly | No | **Low (already killed)** |
| C4 | **Not tested** | Unknown | Unknown | Unknown | No | IRB/students | High (education lit unaudited) |
| C5 | Partially (Phase 10) | n/a | No | Unknown | No | No | Medium |
| C6 | Yes (components) | n/a | Yes | Yes | No | No | Low (components occupied) |
| C7 | Not tested | n/a | n/a | n/a | No | No | High (no controlled design) |
| C8 | **Not tested** | Unknown | Unknown | Unknown | No | Data/ethics | High (unaudited) |

**[INFER]** C3 and C6 collapse immediately; C2 risks pure substitution; C4/C5/C8 are **NOT TESTED** and cannot be given the benefit of the doubt.

---

## Part 6 — Feasibility audit (LOW / MEDIUM / HIGH)

| Candidate | Eng. effort | Inference cost | Data acquisition | Annotation | Duration | Reproducibility | Power | Impl. complexity | Proprietary dependence | Special hardware |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | HIGH | LOW | LOW | NONE | MEDIUM | HIGH | MEDIUM | HIGH | LOW (Flash APIs) | NO |
| C2 | MEDIUM | LOW | LOW | LOW | MEDIUM | HIGH | MEDIUM | MEDIUM | LOW | NO |
| C3 | MEDIUM | MEDIUM | LOW | NONE | MEDIUM | HIGH | **HIGH (needs many runs)** | MEDIUM | LOW | NO |
| C4 | MEDIUM | LOW | MEDIUM | MEDIUM (instruments) | **HIGH (cohorts)** | MEDIUM | **LOW (small N)** | MEDIUM | LOW | NO |
| C5 | MEDIUM | LOW | **HIGH (document assembly)** | MEDIUM | HIGH | MEDIUM | LOW | MEDIUM | NONE | NO |
| C6 | LOW | LOW | LOW | NONE | LOW | HIGH | MEDIUM | LOW | LOW | NO |
| C7 | LOW | LOW | MEDIUM | MEDIUM | HIGH | MEDIUM | LOW | LOW | LOW | NO |
| C8 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NONE | POSSIBLY |

---

## Part 7 — "Would we still do this without a paper?"

| Candidate | Valuable without paper? | Why |
|---|---|---|
| C1 | **Yes** | Reusable teaching/research harness; improves reproducibility of any future work |
| C2 | Yes | Produces an open test-generation dataset and Python tooling |
| C3 | Marginal | Only a redundant confirmation; little standalone value |
| C4 | **Yes** | Directly improves a course and student outcomes regardless of publication |
| C5 | Yes | A public recomputation reference for auditors/educators |
| C6 | Marginal | A validity test-suite is useful, but the finding is already known |
| C7 | **Yes** | Teaching infrastructure with learning-analytics value |
| C8 | Unknown | Depends on the unaudited target result |

**[INFER]** C1, C4, C5, C7 have genuine paper-independent value; C2 modest; C3/C6/C8 little or unknown.

---

## Part 8 — Research project vs infrastructure

The AI Agent Security Lab is assessed **independently** of the paper question.

**[INFER] Recommendation: build it as educational/open-source infrastructure (option D), optionally co-developed with a *later* empirical question (option F), but not as a research contribution (E is not assumed preferable).** Justification: (i) public harnesses already exist, so the platform is not differentiated as research; (ii) it has clear teaching and community value; (iii) building it first generates the instrumentation (logging, cost accounting, revision pinning) that any later empirical question would need.

Option F ("develop first, use later to generate questions") is attractive because it defers — rather than forces — the research commitment. Option A (abandon) is rejected: the lab has independent value. Option E is not selected because no specific research question currently passes the gates.

---

## Part 9 — Publication realism

| Direction | Plausible category | Contribution expected | Evidence required | Likely reviewer objection | Satisfied? |
|---|---|---|---|---|---|
| C1 | Systems/tool demo | Differentiation from existing harnesses | A result existing harnesses cannot produce | "Another harness" | **No** |
| C2 | Empirical SE | Boundary transfer with mechanism | Pre-registered boundary test | "Model/language substitution" | Conditional |
| C4 | Education technology | Controlled learning-outcome improvement | IRB, validated instruments, adequate N | "Confounded, small N" | Not tested |
| C5 | IS / public-sector computing | Reproducible recomputation dataset | Coverage of public data | "Anecdotal; definitional drift" | Conditional |
| C8 | Network measurement | Independent reproduction | Accessible data | "Preempted; no new insight" | Not tested |

**[INFER]** No candidate presents evidence that satisfies its venue's expectation today. Acceptance is not predicted.

---

## Part 10 — Decision gates

| Candidate | G1 interesting | G2 literature open | G3 distinguishable | G4 identifiable | G5 resources | G6 falsifiable/useful | G7 worth without paper | Decision |
|---|---|---|---|---|---|---|---|---|
| C1 | PASS | FAIL | FAIL | PASS | PASS | PASS | PASS | **Infrastructure only** |
| C2 | PASS | CONDITIONAL | FAIL | PASS | PASS | PASS | PASS | **Conditional (human choice)** |
| C3 | PASS | FAIL | FAIL | PASS | PASS | PASS | PASS | **DO NOT COMMIT** |
| C4 | PASS | NOT TESTED | CONDITIONAL | CONDITIONAL | CONDITIONAL | PASS | PASS | **Conditional (needs audit)** |
| C5 | PASS | CONDITIONAL | CONDITIONAL | CONDITIONAL | CONDITIONAL | PASS | PASS | **Conditional (needs audit)** |
| C6 | PASS | FAIL | FAIL | PASS | PASS | PASS | PASS | **DO NOT COMMIT** |
| C7 | CONDITIONAL | NOT TESTED | FAIL | FAIL | PASS | PASS | PASS | **Infrastructure only** |
| C8 | CONDITIONAL | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | PASS | PASS | **Not tested (needs audit)** |

**Critical-gate failures:** C1 fails G2/G3; C3 fails G2/G3; C6 fails G2/G3; C7 fails G3/G4. No candidate passes all seven gates.

---

## Part 11 — Outcome

**OUTCOME C — only infrastructure/education directions survive; no research (paper) direction is mature.**
Not OUTCOME A (no direction passes all gates). Not OUTCOME B (no two fully gate-passing research directions). Not D (infrastructure is genuinely valuable). Not E (there is productive work to do — just not a paper commitment).

**NO RESEARCH COMMITMENT RECOMMENDED AT THIS TIME.**

---

## Part 12 — Final decision matrix

The complete matrix (candidate, research question, novelty type, strongest competitor, novelty status, scientific value, feasibility, reproducibility, resource dependence, publication fit, value without paper, critical risk, kill condition, and Gates 1–7) is in `research/tables/research-direction-selection-matrix.csv` — verified: **8 candidates × 21 columns, no duplicate IDs, no malformed records.** No scores and no ranking are used.

Summary of decisions:
* **C1, C7 — BUILD AS INFRASTRUCTURE; DO NOT COMMIT AS RESEARCH.**
* **C3, C6 — DO NOT COMMIT** (occupied).
* **C2, C4, C5 — CONDITIONAL**, requiring human judgment and, for C4/C5, a scoped audit.
* **C8 — NOT TESTED** (no audit performed; no benefit of the doubt).

---

## Part 13 — Recommended next action

**3. BUILD INFRASTRUCTURE WITHOUT PAPER COMMITMENT.**

**Minimum useful scope of the infrastructure:**
1. A **teaching/reproducible lab skeleton** (the AI Agent Security Lab) built on existing benchmarks rather than a new one — reuse AgentDojo / ASB case sets; do not re-implement them.
2. **Revision pinning + cost accounting + repetition logging** for the four Flash models, with documented hazards (temperature inert in DeepSeek thinking mode; GLM thinking forced on; peak/off-peak pricing).
3. **A small open test-generation toolkit** (Python) as a teaching asset and a possible future replication substrate for C2.
4. **Explicit labelling of the lab as educational/open-source infrastructure**, with no research-novelty claim.

**Why not a research commitment now:** eleven phases produced zero gate-passing directions; the four candidates that remain (C2, C4, C5, C8) are either substitution-shaped or **NOT TESTED**, and committing months to them would be exactly the forced novelty this phase exists to prevent.

**Optional (not required):** if the researcher wants a research path later, the single highest-value targeted audit would be the **computing-education literature for C4**, because it is the only direction that is both *unaudited* and aligned with the researcher's demonstrated strengths. This is a scoped audit, not a broad hunt — but it is **not** recommended as a commitment now.

---

## Files

* **Created:** `research/12-research-direction-selection-audit.md` (this document).
* **Created:** `research/tables/research-direction-selection-matrix.csv` — validated (8 × 21; no duplicate IDs; no malformed records).
* **`research/tables/sources.csv`:** unchanged — this phase re-used existing sources and introduced no new primary claim requiring a new record.
* No previous research conclusion was modified; prior results are cross-referenced only.

---

**PHASE 12 COMPLETE — RESEARCH COMMITMENT: 3**
