# Publication-Gate Audit

**Phase:** 20 — Step 4 (publication-gate decision audit)
**Date:** 2026-09-28
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs.git`
**HEAD at audit:** `6802c81`
**Primary sources of truth:** `research/20-research-positioning-audit.md`; `research/21-education-literature-hostile-audit.md`; `research/22-e1-fulltext-reaudit.md`
**Deliverable:** this file only (`research/23-publication-gate-audit.md`). No paper, study design artefact, experiment, protocol, ethics submission or student data was created. No source, test, policy, lab YAML, scenario, CI, MkDocs or site file was modified.

---

## 1. Scope

This audit decides whether the surviving E1 education-research question is **sufficiently concrete and defensible to justify designing a future empirical study**, or whether the project should **remain an educational/reproducibility artefact without a research paper**. It judges readiness only. It does not design a study, does not draft a paper, does not re-open the Phase 17 CLOSED security-research directions, and does not redefine E1.

**Operating rules applied:** every missing study element is written `NOT SPECIFIED` rather than invented; classification uses only evidence present in the repository and the three prior audits; the most severe skeptical reading is recorded rather than argued against; no novelty is manufactured.

---

## 2. E1 Recovered From Prior Audits

**Exact E1 question (verbatim from `research/21` §2 and `research/22` §2):**

> **E1.** Does a trace-first deterministic lab methodology improve novice understanding of the **request → policy decision → execution → result** distinctions in **agent-security** workflows?

**Exact components (verbatim from `research/21` §2):**

| ID | Component (exact meaning from the prior audits) |
|---|---|
| **E1-A** | **Trace-first instruction** — the trace is the *primary* teaching artefact, introduced before or instead of prose/lecture. |
| **E1-B** | **Deterministic / synthetic agent-security environment** — a controlled, reproducible, sandboxed setting with no live model or network. |
| **E1-C** | **Explicit separation of `request → policy decision → execution → result`** as *named, observable, distinct* concepts. |
| **E1-D** | **Trace reading as a primary learning activity** — students themselves interpret the persisted event stream. |
| **E1-E** | **Novice learners** — the target population is students/newcomers, not expert practitioners. |
| **E1-F** | **Agent / LLM / tool-use security context** — the subject matter is AI-agent security (tool calls, policy, egress). |
| **E1-G** | **Learning outcome concerning conceptual understanding** of those distinctions — measured, not merely asserted. |
| **E1-H** | **Reproducible educational artefact** supporting the methodology (versioned, deterministic, re-runnable). |

**Prior-audit status:** `research/21` §11 and `research/22` §11 both classify E1 as **HIGH-RISK / INSUFFICIENTLY DISTINCT**. `research/22` §6 recorded that **E1-C is `NO` in every located prior source** (including the two closest competitors, whose own abstracts describe exploitation-centric RAG modules), and that the repository is the only source with E1-C fully present and explicitly taught. `research/22` §10 records one decisive open test: the full text of Wilson 2026 / the ACM 2025 RAG lab could not be obtained, so it remains unproven that they lack a mediated-tool/authorization construct.

### 2.1 Component disposition

| Component | Exact meaning | Already supported by literature? | Present in repository? | Empirical evidence in repository? |
|---|---|---|---|---|
| E1-A | Trace-first instruction | **YES** — Hertz & Jump 2013; Nelson 2017; Xie 2018; Weninger 2026; Guo 2013 (`research/21` §6.4–6.6) | **YES** — `labs/README.md` ("Reading the trace"), `labs/TRACE-WALKTHROUGHS.md`, `labs/TRACE-READING-EXERCISES.md`; CLI `inspect`/`evaluate` | **NO** — capability only |
| E1-B | Deterministic / synthetic agent-security environment | **YES (as a property)** — SEED labs; cyber ranges (`research/21` §6.7–6.9) | **YES** — `models/mock.py` (clock-free fixture), `selfcheck.py`, in-memory tools | **NO** — capability only |
| E1-C | Explicit `request → policy decision → execution → result` separation | **NO** — absent in every located source (`research/22` §6; the policy-decision column is `NO` throughout) | **YES** — `trace/schema.py` (`tool_requested`, `policy_decision`, `tool_executed`, `tool_result`); `tools/gateway.py`; `policy/schema.py::Decision` | **NO** — capability only |
| E1-D | Trace reading as primary learning activity | **YES** — Hertz 2013; Nelson 2017; Xie 2018; Weninger 2026 | **YES** — `labs/TRACE-READING-EXERCISES.md` + answer key; `labs/TRACE-WALKTHROUGHS.md` | **NO** — materials only |
| E1-E | Novice learners | **YES** — addressed by Wilson 2026, Hertz 2013, Thompson 2018, etc. | **YES (intended audience)** — `labs/GETTING-STARTED.md`, `labs/INSTRUCTOR-GUIDE.md` | **NO** — no participants |
| E1-F | Agent / LLM / tool-use security context | **PARTIAL** — LLM-security labs exist (Wilson 2026); agent traces in education exist (Xi 2026) | **YES** — `tools/gateway.py`, `labs/LAB-00…07` | **NO** — capability only |
| E1-G | Measured conceptual understanding of those distinctions | **NO** — instruments exist for other constructs (CCI 2021; Thompson 2018), but not for this construct (`research/22` §7) | **NO** — nothing measures learning | **NO** |
| E1-H | Reproducible educational artefact | **YES (as a property)** — SEED labs; cyber ranges | **YES** — `agentsec labs check`; `.github/workflows/ci.yml`; `pyproject.toml` | **NO** — capability only |

### 2.2 Separation of kinds

| Kind | What it is | Where it stands |
|---|---|---|
| **Artefact capability** | What the code and materials *can* do (emits four distinct events; deterministic replay; eight labs; exercises; CI) | **Present and verified** (694 tests; 8/8 labs; strict build) |
| **Pedagogical method** | The *design choice* to teach by reading a mediated trace | **Present as design**; E1-A/E1-D are established techniques, not contributions |
| **Research question** | E1 as stated above | **Formed but largely unspecified** (§3) |
| **Empirical evidence** | Learning-outcome data | **Absent** — explicitly recorded in `research/20` §11 ("Any learning-outcomes evidence … does not exist") |

**[FACT]** The repository contains **artefact capability** and a **pedagogical method**, and it *names* a **research question**; it contains **no empirical evidence** of any kind about learning.

---

## 3. Is E1 a Falsifiable Research Question?

E1 is *falsifiable in principle* — "does a trace-first deterministic lab methodology improve novice understanding of the four-stage distinction?" admits a negative answer. The question is whether the current formulation specifies the elements a study requires. Each element is recorded exactly as the prior audits left it.

| # | Element | Specified? | What the prior audits actually say |
|---|---|---|---|
| 1 | **Population** | **PARTIAL** | "novice learners … students/newcomers, not expert practitioners" (E1-E). No level, discipline, institution type, prior-knowledge band. |
| 2 | **Intervention** | **YES (as a description)** | The eight deterministic labs with trace walkthroughs and exercises. No dosage/contact-hours definition, no implementation protocol. |
| 3 | **Comparison / control** | **NOT SPECIFIED** | `research/20` §9 lists *possible* baselines ("a conventional instruction condition … or a non-trace hands-on condition") but names none as chosen. |
| 4 | **Outcome** | **PARTIAL** | "improve novice understanding" — direction stated, magnitude and criterion unstated. |
| 5 | **Measurable construct** | **PARTIAL** | E1-C names the four stages; the *observable* that would evidence understanding is not defined. |
| 6 | **Assessment method** | **NOT SPECIFIED** | No instrument, no item format, no scoring rule. `research/22` §7 records that validated instruments exist for *other* constructs only. |
| 7 | **Time frame** | **NOT SPECIFIED** | No session count, duration, or retention interval. |
| 8 | **Plausible hypothesis** | **NOT SPECIFIED** | No directional hypothesis with an expected effect. |
| 9 | **Confounders** | **PARTIAL** | `research/20` §9 lists threats (prior security/LLM experience, motivation, instrument validity, novelty/Hawthorne, single-institution, fixture simplification) — identified, not controlled for. |
| 10 | **Unit of analysis** | **NOT SPECIFIED** | Individual learner vs cohort vs course-run is not stated. |

### 3.1 Classification of the gaps

The missing elements divide into two kinds, and the distinction matters:

- **Ordinary study-design details that can be specified later** — items 1 (level/institution), 3 (baseline choice), 4 (criterion), 6 (instrument format), 7 (duration), 8 (hypothesis wording), 10 (unit of analysis). These are normal decisions made when designing a study; their absence now is not evidence that E1 is vague.
- **A gap that is *not* ordinary design detail** — item 5, the operationalization of the construct, combined with the fact (from `research/22` §7 and §10) that **no located evidence establishes that the four-stage distinction is a genuine novice difficulty at all**. The prior audits show students have generic security misconceptions (Thompson 2018: "conflated concepts") but say nothing about this specific construct.

**[INFER]** E1 is therefore **falsifiable in form** and **under-specified in substance**. It is *not* too vague to be a research question — the construct is concrete and the intervention exists — but it is **not yet specified to the point where a study could be registered**, and, more importantly, the *problem* it would address has not been shown to exist.

---

## 4. Construct Operationalization

The construct must remain **educational**: "understanding the distinction between `request`, policy decision, `execution`, and `result`." It must **not** become an attack-success rate, security score, vulnerability score, policy-effectiveness score, benchmark, agent-capability metric, or model-propensity measurement.

Candidate observable educational outcomes (recorded as candidates only; the audit does not indicate that any candidate is preferable to another):

| Candidate observable | Sketch | What it would evidence | What it could merely reflect |
|---|---|---|---|
| Classification accuracy | Learner labels each trace event's stage (request / decision / execution / result) | Ability to identify stages in a presented trace | Event-name recognition; interface familiarity |
| Trace-interpretation accuracy | Learner answers questions about a *specific* run's path (e.g. "did the denied call execute?") | Ability to reason from events to behaviour | Memorised lab-specific facts |
| Scenario-explanation accuracy | Learner explains *why* a tool did not run, using the trace | Reasoning about the decision↔execution relationship | Recall of the instructor's phrasing |
| Error / misconception patterns | Coded taxonomy of learner errors (e.g. treating a request as execution) | Presence and kind of confusion | Test-format artefacts |
| Transfer to unseen traces | Same tasks on a lab the learner never ran | Generalisation beyond the taught instance | Prior security knowledge |

**[FACT]** None of these instruments exists; none is validated; and each could be operationalized **without** introducing a security metric, which keeps the construct inside the educational boundary.

**[OPEN]** Whether any candidate would be aligned with the E1-C construct (rather than with generic trace reading) is unresolved. `research/22` §12 item 3 records the same concern: existing near-neighbour studies measured quiz scores/self-efficacy or grades, not the distinctions themselves.

---

## 5. Measurement-Validity Audit

**What would count as evidence that a learner understands the four-stage distinction?** Consistent, correct reasoning *from trace events* to the relationship between them (specifically: that a `request` is not an `execution`; that a `policy decision` precedes and conditions execution; that an `allow` may still not have executed; that a `tool_result` can exist with no `tool_executed`). This is a *reasoning* claim, not a *recognition* claim.

**What would merely show memorization?** Correct labelling of event names; recall of the eight "distinctions" as prose; correct answers on the specific traces students have already seen. `research/22` §6.9 and `labs/README.md` show the repository currently teaches via exactly such named distinctions, so a recognition-only instrument would be indistinguishable from recall of the material.

**What would constitute transfer?** Correct reasoning on an **unseen** lab or a **novel** trace where the stage pattern differs from the taught sequence (e.g. a `require_approval` that is later approved, or a denied write).

**Alternative explanations that could produce an apparent improvement:**
- **Interface/format familiarity** — improved performance from practice with the trace format, not the concept.
- **Topic exposure** — any encounter with agent terminology (including plain reading) could raise scores.
- **Test-retest / practice effects** — pre/post with the same instrument.
- **Instructor / implementation effects** — enthusiasm, scaffolding, or time-on-task differences.
- **Selection bias** — volunteers, or students already motivated and capable.
- **Novelty/Hawthorne effects** — a new tool changing engagement.
- **Demand characteristics** — learners inferring the expected answers.

**Evidence needed to separate conceptual understanding from interface familiarity:** at minimum (a) a **comparison condition** that receives equivalent time, interface and topic exposure without the trace-first mediation sequence, and (b) **transfer items** on unseen traces, and ideally (c) an instrument that asks for *reasoning* (justification) rather than labels.

**Threats to validity requiring particular attention:**

| Threat | Why it is acute here |
|---|---|
| **Construct validity** | No instrument exists for E1-C; the nearest instruments measure other constructs (CCI 2021) or other domains (program tracing). |
| **Internal validity** | Learning effects, instructor effects, selection bias and novelty effects are all plausible and none is currently controlled. |
| **External validity** | The deterministic fixture *simplifies* behaviour; `research/20` §9 warns the concept may not transfer to real, stochastic agents, so even a positive result would be narrow. |
| **Statistical conclusion validity** | Small-n and no power analysis; `research/22` §12 states the nearest neighbours used small cohorts (e.g. Wilson 2026, n=16; Heverin 2026, n=12). |
| **Assessment alignment** | The intervention teaches named distinctions, so an instrument built from those names risks teaching-to-the-test. |
| **Task equivalence** | Comparison conditions would need genuinely equivalent tasks and time. |

**[FACT]** `research/20` §9 and `research/22` §12 already identify these threats. **[INFER]** A pre/post score alone would not discharge any of them; the prior audits explicitly warn that an apparent improvement is compatible with several non-conceptual explanations.

---

## 6. Publication-Type Analysis

Three routes are described. They are described, not ranked; no route is called preferable.

### Route A — Artefact / educational-artefact paper

| Field | Content |
|---|---|
| **Required evidence** | A stated, defensible design claim (something the artefact does that existing artefacts do not), plus evaluation or adoption evidence; a licence and citation metadata for a released artefact. |
| **Currently available** | A complete, tested, reproducible, documented artefact: 694 tests passing, 8/8 labs self-checking, deterministic replay, CI, a deployed documentation site, instructor material. |
| **Missing** | A non-standard design claim argued against the existing artefact genre (SEED, cyber ranges); any evaluation or adoption data; `LICENSE` / `CITATION.cff` (still unassigned per root `README.md`, which is also stale — `research/20` §2.12). |
| **Main novelty burden** | E1-B and E1-H are *properties* (reproducible, hands-on), and `research/21` §6.7–6.9 records that this genre is settled and evaluated. The burden falls on the design claim. |
| **Main risk** | A reviewer reading the genre rather than the design: "another hands-on security lab." |
| **Can the current repository alone support it?** | **No** — the artefact exists, but the claim and the evaluation evidence do not. |

### Route B — Experience report

| Field | Content |
|---|---|
| **Required evidence** | A coherent design rationale, implementation description, honest reflection, and (typically) light evaluation such as student feedback or an instructor's observations. |
| **Currently available** | The rationale is largely *implicit* in the repository: the mediated-gateway invariant, declarative scenarios, the eight-lab sequence, the "Eight distinctions" in `labs/README.md`, the boundary statements, and `labs/INSTRUCTOR-GUIDE.md` teaching material. |
| **Missing** | A written synthesis of the rationale as such; any learner or instructor evaluation; deployment experience data. |
| **Main novelty burden** | An experience report carries a low novelty burden; its burden is on the coherence and honesty of the reflection, not on a testable claim. |
| **Main risk** | A reviewer judging the report as a description of an unstudied intervention: "interesting, but no evidence of effect." |
| **Can the current repository alone support it?** | **Partly** — the material exists in the repository, but the synthesis and any light evidence would have to be produced. |

### Route C — Empirical computing-education / cybersecurity-education study

| Field | Content |
|---|---|
| **Required evidence** | A falsifiable question with specified population, intervention, comparison, outcome and instrument; a pre-registered design; ethics/IRB approval; collected and analysed learner data; controls for the threats in §5. |
| **Currently available** | The intervention (E1-A/B/C/D/F/H artefacts). |
| **Missing** | Everything empirical: participants, instrument, comparison condition, protocol, ethics approval, data, analysis. Also missing: any evidence that E1-C is a genuine learner difficulty. |
| **Main novelty burden** | `research/21` §11 / `research/22` §11: the genre is occupied (Wilson 2026), trace-first pedagogy is established, and the residual is one untested construct — the novelty burden is high and undischarged. |
| **Main risk** | Both the kill-test criticisms in §9 (another hands-on lab; interface familiarity; a restatement of existing concepts) can be raised against the current evidence base. |
| **Can the current repository alone support it?** | **No** — the repository contains no empirical evidence, and `research/22` §10 records an unresolved decisive prior-art test. |

---

## 7. Research Readiness Gates

### GATE A — Artefact publication readiness
**NOT READY**

The repository is a mature artefact (694 tests; 8/8 labs; deterministic replay; CI; live documentation site; instructor material), so an artefact-oriented *vehicle* exists. What is absent is what an artefact publication requires beyond existence: a **stated design claim** distinguishing it from the settled hands-on-security-lab genre, and **evaluation or adoption evidence**. `research/20` §11 records both as missing, and also records that licensing/citation metadata is unassigned. Absence of the claim and the evidence is why this gate is NOT READY rather than PASS.

### GATE B — Experience-report readiness
**NOT READY**

The repository contains substantial *implicit* experience: the design invariants (a single mediated tool-execution boundary enforced by a test), the declarative-scenario layer, the eight-lab progression, the pedagogic distinctions, the boundary statements, and instructor-facing teaching material. It does **not** contain a written rationale-and-reflection artefact, nor any learner/instructor evaluation. `research/22` §12 describes this route as requiring "rationale + honest reflection + light evaluation"; the rationale material exists, the synthesis and the evaluation do not. Hence NOT READY.

### GATE C — Empirical-study readiness
**INSUFFICIENT EVIDENCE**

The repository contains **no** empirical evidence of learning: no participants, no instrument, no comparison condition, no protocol, no analysis (`research/20` §11; `research/22` §12). It also contains no evidence that the E1-C construct is a real novice difficulty, and `research/22` §10 records an unresolved decisive prior-art test. This gate cannot be PASS or NOT READY because the required evidence is not merely incomplete — it does not exist.

---

## 8. Minimum Future Study Specification

E1 is not abandoned (see §10), so the minimum future study is outlined at a high level. **Nothing here was implemented, designed in detail, or run.**

| Item | Specification | Status |
|---|---|---|
| **Research question** | Does a trace-first deterministic agent-security lab sequence improve novice understanding of the `request → policy decision → execution → result` distinction relative to a comparison condition? | **Specified** (same as E1) |
| **Hypothesis** | A directional hypothesis and expected effect size are not stated in any prior audit. | **NOT YET SPECIFIED** |
| **Population** | Novice learners (students/newcomers). Level, discipline, and prior-knowledge band are not stated. | **NOT YET SPECIFIED** (only E1-E as a descriptor) |
| **Intervention** | The eight deterministic labs with trace walkthroughs and trace-reading exercises. Contact hours and implementation protocol are not defined. | **PARTIALLY SPECIFIED** |
| **Comparison** | A conventional instruction condition, or a non-trace hands-on condition (`research/20` §9 lists candidates; none chosen). | **NOT YET SPECIFIED** |
| **Primary educational outcome** | Conceptual understanding of the four-stage distinction, evidenced by reasoning from trace events. | **Specified as a construct**; observable not fixed |
| **Secondary outcomes** | Candidates only: transfer to unseen traces; error/misconception patterns; retention. | **NOT YET SPECIFIED** |
| **Assessment approach** | Candidate instruments in §4 (classification accuracy, trace interpretation, scenario explanation, error patterns, transfer). None exists or is validated. | **NOT YET SPECIFIED** |
| **Study duration** | No session count, duration or retention interval is stated. | **NOT YET SPECIFIED** |
| **Minimum methodological safeguards** | A comparison condition with equivalent time/interface/topic exposure; transfer items on unseen traces; reasoning-based items; pre-registration; control for prior experience. | **PARTIALLY SPECIFIED** (threats identified in `research/20` §9, `research/22` §12; no design to implement them) |
| **Ethics / IRB requirement** | Human-participant data collection would require ethics/IRB approval. | **Required**, but no submission exists or is proposed here |
| **Preregistration requirement** | `research/20` §9 and `research/22` §12 call for a pre-registered design. | **Required**, not produced |

**Sample size and statistical tests are deliberately not chosen**, because no power analysis exists and no prior audit supplies an effect-size estimate that would justify a choice.

---

## 9. Hostile Reviewer Kill-Test

Each criticism is recorded in its most severe form, followed by the evidence that would be required to answer it. No rebuttal is offered.

### 9.1 "This is simply another hands-on cybersecurity lab with trace visualisations."

**Why a reviewer could say it:** `research/21` §6 and `research/22` §9 record that hands-on security labs (SEED, cyber ranges), LLM-security labs with measured outcomes (Wilson 2026; ACM 2025), and trace-based teaching (Hertz 2013; Nelson 2017; Xie 2018; Weninger 2026) each already exist, and that the repository's own materials read as a deterministic lab with a trace view.

**Evidence required to answer it:** a demonstration that the intervention teaches a **learning object that the existing genre does not**: specifically, reasoning about the *relationship between* an authorization decision and execution (E1-C), assessed on **unseen** traces, in a comparison against a non-trace-hands-on condition. A description of the pipeline is not sufficient — `research/22` §6.9 already shows the pipeline exists; what is missing is the pedagogical *effect*.

### 9.2 "The claimed learning effect is merely interface familiarity."

**Why a reviewer could say it:** the intervention is presented through a bespoke trace format with named events; improved performance is compatible with format practice (`research/22` §12 item 3; §5 above).

**Evidence required to answer it:** transfer items on traces the learner has **not** seen; a comparison condition with equivalent interface exposure but without the mediation sequence; and items that require **justification** rather than event labelling.

### 9.3 "The four-stage distinction is simply a pedagogical restatement of existing trace/code-analysis/access-control concepts."

**Why a reviewer could say it:** access control (request → decision), execution tracing, and result/effect analysis are all long-established; `research/22` §6.7 shows SEED labs already touch access control conceptually (`PARTIAL`), and §6.4–6.6 show trace-based teaching already traces execution.

**Evidence required to answer it:** a demonstration that (a) novices specifically **conflate** these stages as agent-security events (i.e. the *problem* is real and not previously documented for this construct), and (b) the trace-first mediated intervention **reduces that confusion relative to a comparison**, on transfer items. Without (a), the construct is a restatement; without (b), the intervention is untested.

**Aggregate skeptical reading (recorded, not contested):** on the present evidence base, a reviewer could hold that the repository is a well-built hands-on agent-security lab whose *distinctive* element (E1-C) is asserted rather than demonstrated, in a genre that already contains measured-outcome examples.

---

## 10. Final Decision

**1. HOLD — artefact only; no paper yet**

**Why this decision follows from the evidence:**

- **Gate C is INSUFFICIENT EVIDENCE, not NOT READY.** The repository contains no empirical learning evidence, no instrument, no comparison condition and no protocol (`research/20` §11; `research/22` §12). Gates A and B are NOT READY for the specific reasons in §7. No gate is PASS.
- **The *problem* behind E1 is unestablished.** No located evidence shows that novices confuse the four stages in agent-security workflows (`research/22` §7, §10). A study of E1-C would address a need that has not been shown to exist.
- **The novelty burden is unmet and undischarged.** E1 is HIGH-RISK / INSUFFICIENTLY DISTINCT (`research/21` §11; `research/22` §11): the genre is occupied, and every component except E1-C is already established.
- **A decisive prior-art test remains open.** `research/22` §10 records that the full text of the two closest competitors could not be obtained; if either contains a mediated-tool/authorization construct with a trace-reading activity, E1 becomes PREEMPTED. Deciding on study design before closing that test would be premature.
- **HOLD is consistent with the project's own recorded posture.** `docs/development.md` states the repository is educational/reproducibility infrastructure making no novelty claim, and Phase 17's research transition is CLOSED.

**Why not PREPARE STUDY.** PREPARE STUDY would commit to designing a study on a construct whose *pedagogical problem* is unevidenced, in a genre already occupied, while the decisive prior-art test is unresolved. The evidence does not support that commitment.

**Why not ABANDON E1.** E1-C is genuinely `NO` across every located source (`research/22` §6); the construct is concrete and observable in the artefact; and the question is falsifiable. E1 is kept alive as a *held* question, not closed.

**Conditions that would move the decision (recorded; none is performed here):**
1. The decisive full-text test resolves **against** preemption (Wilson 2026 / ACM 2025 contain no mediated-tool/authorization construct).
2. Evidence emerges that novices **do** conflate request/decision/execution/result in agent-security tasks (e.g. an exploratory, non-study classroom observation or a documented misconception pattern).
3. A full-text, venue-targeted review of the computing-education space (ACM DL, IEEE Xplore, TOCE, JCERP, SIGCSE/ITiCSE/ICER proceedings) confirms the construct is unoccupied.

If (1)–(3) hold, the decision would be reconsidered — not automatically advanced.

---

## 11. What This Audit Does NOT Establish

This audit explicitly does **not** establish, and must not be read as establishing:

- **research novelty** — E1 is classified HIGH-RISK / INSUFFICIENTLY DISTINCT; no novelty is claimed for the repository, for E1, or for any component;
- **publication acceptance** — no venue outcome is predicted or implied;
- **causal educational effectiveness** — no study exists; nothing here shows the labs improve learning;
- **security effectiveness** — no security claim is made or measured;
- **model behaviour** — the deterministic fixture is a fixture; nothing here speaks to real model or agent behaviour;
- **benchmark validity** — the repository is not a benchmark and this audit does not treat it as one.

It also does not reopen the Phase 17 CLOSED directions (benchmark/scoring, attack-success measurement, model-propensity measurement, detector research, policy-effectiveness claims, real-LLM behavioural experiments, real-world leakage experiments, provider integration, network functionality). It does not redesign the intervention, and it does not recommend a publication route.

---

## 12. Verification

Commands run after creating this file (read-only with respect to tracked files):

```
PYTHONPATH=src py -m pytest            -> 694 passed (exit 0)
agentsec labs check                    -> 8/8 labs passed (exit 0)
py -m mkdocs build --strict            -> exit 0, no warnings/errors
git diff --name-only                   -> (empty)
git status --porcelain                 -> ?? research/23-publication-gate-audit.md
                                          (plus the still-untracked research/20, /21, /22 from prior steps)
```

- **No tracked file was modified** (`git diff --name-only` is empty).
- **The only file created by this step** is `research/23-publication-gate-audit.md`.
- **Nothing was staged, committed, pushed, reset, checked out, rebased, amended or cleaned.**

---

*End of publication-gate audit. No paper was drafted; no study was designed or implemented; no data was collected.*
