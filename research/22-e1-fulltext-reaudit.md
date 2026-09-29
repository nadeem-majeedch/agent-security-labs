# Phase 20 — Step 3 E1 Full-Text Re-Audit

**Phase:** 20 — Step 3 (targeted full-text re-audit of E1)
**Date:** 2026-09-28
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs`
**HEAD at audit:** `6802c81`
**Inputs:** `research/20-research-positioning-audit.md`; `research/21-education-literature-hostile-audit.md` (Step 2 classification: **HIGH-RISK / INSUFFICIENTLY DISTINCT**)
**Boundary:** Phase 17 research NO-GO remains CLOSED. This step examines only the educational E1 question. No paper, experience report, experiment, protocol or student data was produced. Only this file was created.

---

## 1. Purpose

Step 2 concluded that every component of E1 was individually covered but the exact combination was not located, and that the single most load-bearing uncertainty was whether the closest prior educational work (Wilson 2026; the ACM 2025 RAG lab) actually overlaps E1 closely enough to render it **PREEMPTED**. Step 2 also noted that its peer-reviewed evidence was abstract-level because full-text fetches failed.

Step 3 therefore does two things:

1. **Aggressive multi-route full-text retrieval** for the strongest sources (publisher HTML, institutional repositories, PMC, arXiv, landing pages, public metadata APIs), without circumventing any paywall, authentication, robots directive or access control.
2. **Targeted E1-C and E1-G searches** — the explicit `request → policy decision → execution → result` construct and the measurement of conceptual understanding — across semantic-equivalent vocabulary.

E1 is **not** redefined here. Where a source would preempt E1, it is reported as a killer regardless of the consequences for the repository's prospects.

---

## 2. E1 Question

> **E1.** Does a trace-first deterministic lab methodology improve novice understanding of the **request → policy decision → execution → result** distinctions in **agent-security** workflows?

Components (unchanged from Step 2): E1-A trace-first · E1-B deterministic/synthetic agent-security environment · E1-C the four-stage construct as distinct observable stages · E1-D students read the trace · E1-E novices · E1-F agent/LLM/tool-use security · E1-G measured conceptual understanding of those distinctions · E1-H reproducible artefact.

---

## 3. Sources Targeted

Tier 1 (closest competitors): Wilson 2026 (JCERP); ACM 2025 *A Hands-on Approach to Enhancing LLM Security Education*; Xi et al. 2026 (arXiv:2603.21551).
Tier 2 (trace-based pedagogy): Hertz & Jump 2013; Nelson et al. 2017; Xie et al. 2018; Weninger et al. 2026 (PETs).
Tier 3 (reproducible security labs): SEED / Du 2008–2011; cyber-range studies (Lazarov 2025; CHI 2023).
Tier 4 (security education method & assessment): Švábenský et al. 2022 (trace mining for assessment); Thompson et al. 2018 (novice misconceptions); Cybersecurity Concept Inventory (CCI, ACM TOCE 2021); Nagvekar et al. 2025 (log analysis teaching).
Tier 5 (E1-C-specific): the exact construct and its semantic equivalents, searched directly (§6).

---

## 4. Full-Text Access Results

| Source | Full text obtained? | Evidence level achieved | Access route attempted | Limitation |
|---|---|---|---|---|
| Wilson 2026, JCERP | **No** | **C** (official record + full abstract) | DigitalCommons landing page (`/jcerp/vol2026/iss1/2/`) ✓; PDF `viewcontent.cgi` ✗ 403 | Full text PDF blocked; abstract read |
| ACM 2025 *A Hands-on Approach to Enhancing LLM Security Education* | **No** | **C** (snippet only) | ACM DL DOI page ✗ 403 | No abstract page; only search snippet |
| Xi et al. 2026, arXiv:2603.21551 | **Yes** | **B** (authoritative full text; preprint) | arXiv HTML ✓ | Not peer-reviewed (preprint) |
| Hertz & Jump 2013 (SIGCSE) | **No** | **C** (abstract ×3 citation records) | ACM DL ✗ 403; author PDF ✗ unsupported; flashcard/report summaries ✓ | No full text |
| Nelson et al. 2017 (ICER) | **No** | **C** (abstract/enumeration) | ACM ✗ 403; author PDF ✗ unsupported | No full text |
| Xie et al. 2018 (SIGCSE) | **No** | **C** | author PDF ✗ unsupported | No full text |
| Weninger et al. 2026 (PETs, VISSOFT/DEBT) | **No** | **C** (snippets) | author PDFs ✗ unsupported | No full text |
| SEED / Du 2008, 2011 | **No** (full text) / **Yes** (project record) | **C/D** | seedsecuritylabs.org publications page ✓; PDFs ✗ unsupported | Lab list + publication record only |
| Švábenský et al. 2022 | **Yes** | **A** (peer-reviewed full text via PMC) | PMC `PMC8964927` ✓ | none material |
| Thompson et al. 2018 (JCERP) | **No** (full text) / **Yes** (abstract) | **C** | JCERP landing page ✓; PDF ✗ 403 | Abstract only |
| CCI (ACM TOCE 2021, 10.1145/3451346) | **No** | **C** | ACM ✗ 403; thesis PDF ✗ unsupported | Abstract/snippet only |
| Lazarov et al. 2025 (Springer) | **No** | **C** | Springer ✗ 406; ResearchGate ✗ | Snippet only |
| CHI 2023 cyber-range evaluation | **No** | **C** | ACM ✗ 403 | Snippet only |
| Nagvekar et al. 2025 (Frontiers) | **No** | **C** | Frontiers ✗ JS-rendered (boilerplate only) | Snippet only |
| Public metadata APIs (Semantic Scholar) | **No** | — | `api.semanticscholar.org` ✗ 429 rate-limited | Not used |

**Net effect:** full-text access improved for **two** sources (Švábenský → **A**; Xi → **B** full text). The **single closest competitor (Wilson 2026) remains abstract-only (C)**, and the ACM 2025 lab remains snippet-only (C). The most consequential uncertainty from Step 2 is therefore **not fully resolved**.

Attempts that are explicitly *not* made: paywall circumvention, credentialed/authenticated access, robots-directive bypass, or scraping of restricted repositories.

---

## 5. Detailed Source Analysis

### 5.1 Wilson 2026 — JCERP (label C, official record + full abstract)

- **Educational objective:** teach adversarial LLM attacks (prompt injection, jailbreaking, model inversion) and their security implications.
- **Learner population:** 16 graduate cybersecurity students.
- **Intervention:** a "structured, hands-on module", two-week pilot; "red team activities to actively exploit model alignment and privacy vulnerabilities".
- **Environment:** "a custom Retrieval-Augmented Generation (RAG) platform with local open-source LLMs".
- **Trace/log role:** **not** reported as a learning artefact. The learning object is the exploit and its effect.
- **Agent/LLM role:** LLM **as attack target** (RAG pipeline); **no agent tool-calling, no tool gateway, no policy engine**.
- **Policy/authorization role:** alignment/privacy safeguards of the model — i.e. *guardrails to bypass*, not a policy decision exposed as a distinct event.
- **Learning assessment:** post-module quiz (mean 88%) and self-reported confidence (90% "increased confidence").
- **Overlap with E1:** E1-E YES; E1-G YES (quiz + confidence); E1-B PARTIAL (local models, sandboxed); E1-F PARTIAL (LLM security but not agent tool-use).
- **Difference from E1:** exploitation-centric, RAG-centric, not trace-centric; no `request/decision/execution/result` construct; no mediation boundary.

### 5.2 ACM 2025 — *A Hands-on Approach to Enhancing LLM Security Education* (label C, snippet)

- **Objective/intervention:** "lab exercises … Students learn about LLM threats and mitigation strategies by building and attacking a RAG-based LLM system."
- **Overlap/difference:** essentially the same profile as §5.1 (build-and-attack RAG lab). **No** evidence of trace-first design, policy-decision observability, or the E1-C construct.

### 5.3 Xi et al. 2026 — arXiv:2603.21551 (label B, full text read)

- **Objective:** design LLM-assisted CTF competitions as learning technologies and study outcomes.
- **Learners:** multi-region competition participants (in-class, standard, expert tracks).
- **Intervention:** LLM-assisted CTF across autonomy levels (human-in-the-loop, autonomous agents, hybrid).
- **Environment:** real CTF challenges; **submissions must be "traceable"** ("conversation logs, agent trajectories, and agent code").
- **Trace role:** **central to the research analysis** — traces reveal "reasoning behaviours, tool use, and solution strategies"; iteration/tool choice/debugging are extracted from traces.
- **Agent/LLM role:** LLM agents as **solvers** (offensive); tool use is present.
- **Policy/authorization role:** **none** — no authorization or policy-decision construct.
- **Assessment:** competition performance + behavioural analysis; not a concept instrument.
- **Overlap:** E1-A/E1-D PARTIAL (traces central, but as *researcher* data), E1-F PARTIAL (agents, offensive).
- **Difference:** students are taught/assessed on *offensive problem-solving*; the trace is evidence for the *researcher*, not the *student's* conceptual instrument; no mediation semantics.

### 5.4 Hertz & Jump 2013 (C) and Nelson 2017 / Xie 2018 (C)

- **Objective:** teach introductory programming by centering instruction on **program memory traces** (Hertz), or teach a formal **program-tracing knowledge** theory + tutoring (Nelson), or an explicit novice tracing strategy (Xie).
- **Learners:** novice programmers.
- **Environment:** ordinary programming; deterministic in the sense that a program's execution is fixed.
- **Trace role:** **central** — the trace *is* the teaching object.
- **Assessment:** Hertz: statistically significant grade improvement, reduced drop/failure. Nelson/Xie: empirical evaluations of tracing skill.
- **Overlap:** **E1-A, E1-D, E1-G all YES.**
- **Difference:** programming semantics, not security or agents; no policy/authorization/execution boundary; the traced object is a program's memory state, not a mediated tool call.

### 5.5 Weninger et al. 2026 — Pedagogical Execution Traces (C)

- **Objective:** turn execution traces into "reusable, self-paced learning artifacts" for guided trace-based debugging.
- **Trace role:** central; traces are the learning artefact.
- **Overlap:** E1-A, E1-D, E1-B partial. **Difference:** debugging/programming; no security, no agents, no policy decisions.
- **Significance:** shows the *general idea* "trace as a reusable teaching artefact" is an **active 2026 research topic** — so E1-H-style artefact design is not untouched territory.

### 5.6 SEED / Du (C) — reproducible cybersecurity labs

- **Objective/intervention:** a suite of ~28–35 hands-on system-security labs; the project publishes **evaluation results** ("show how students evaluate our labs").
- **Environment:** sandboxed, runnable on personal machines (reproducible).
- **Trace role:** incidental (logs are outputs of exercises, not the teaching object).
- **Overlap:** **E1-B, E1-H YES**; E1-F partial (security generally). **Difference:** exploit/system mechanics; no mediation/policy-decision construct; no trace-first pedagogy.
- **Significance:** establishes that "reproducible hands-on security lab" is a **settled, evaluated, decades-old genre**.

### 5.7 Švábenský et al. 2022 (label A, full text via PMC) — trace mining for assessment

- **Objective:** support **automated assessment** of hands-on cybersecurity training by mining trainee interaction data.
- **Data:** 8,834 commands from 113 trainees across 18 sessions; pattern mining + clustering of command histories (i.e. **execution traces**).
- **Findings:** patterns reveal typical behaviour, mistakes, solution strategies; instructors can see where each trainee needs help; "targeted scaffolding."
- **Trace role:** **central** — but the trace is analysed **by the system/instructor**, not read by the student as the learning activity.
- **Overlap:** E1-D partial (traces used in education, for assessment); E1-E YES. **Difference:** assessment/tutoring support, not trace-interpretation pedagogy; no policy/authorization/execution construct; no agent context.
- **Significance:** the *strongest available full text* in this audit, and it confirms that "traces in cybersecurity education" already has a peer-reviewed research programme — directed at **assessment**, not at teaching students to reason about mediation stages.

### 5.8 Thompson et al. 2018 (C) and the Cybersecurity Concept Inventory (C) — E1-G landscape

- **Thompson et al. 2018 (JCERP):** 25 think-aloud interviews across three institutions document novice **misconceptions** in cybersecurity; themes include **"conflated concepts"** and "incorrect assumptions"; the authors conclude students "generally failed to grasp the complexity and subtlety" and call for "instructional methods that engage students in reasoning about complex scenarios".
- **CCI (ACM TOCE 2021, 10.1145/3451346):** "a validated instrument for assessing student knowledge of introductory cybersecurity".
- **Significance for E1-G:** the *methodology* of measuring conceptual understanding in cybersecurity education exists and is mature. What is **not** located is an instrument or study targeting the `request → decision → execution → result` construct, or agent-security mediation generally.

### 5.9 Cyber-range studies (C) and Nagvekar 2025 (C)

- Cyber ranges: simulated hands-on environments with **measured** training evaluation (CHI 2023 explicitly studies how to evaluate them). Overlap: E1-B/E1-G partial; no agents, no trace-first, no mediation semantics.
- Nagvekar 2025: "log data analysis is a core competency in cybersecurity education"; mixed-methods study of learner difficulties. Overlap: E1-D partial (students read logs), E1-E/E1-G partial. Difference: **host/network logs for attack investigation**, not a curated agent trace, and no policy/execution distinction.

---

## 6. E1-C Hostile Analysis

The requirement is *not* whether a system emits logs, but whether the **educational intervention** teaches learners to reason about the distinction. Each table records the strongest available evidence; `UNKNOWN` is used where the full text could not be obtained and the abstract is silent.

### 6.1 Wilson 2026 (C)
| E1-C element | Evidence in source | Verdict |
|---|---|---|
| Request observable | Not described; module is about inject/jailbreak/inversion prompts | NO |
| Policy/authorization decision observable | Saferails exist only as **targets to bypass**, not as recorded decisions | NO |
| Execution observable | No tool execution described | NO |
| Result/effect observable | Exploit success described qualitatively | PARTIAL |
| Distinct events | No event model described | NO |
| Explicitly taught | Not in the abstract | NO |
| Student reasoning required | Yes, but about *exploits*, not mediation stages | PARTIAL |
| Central to learning activity | Exploitation is central | NO (for E1-C) |
| Deterministic/reproducible | Local open-source models; determinism not reported | UNKNOWN |
| Agent/LLM/tool context | LLM (RAG); **no tool gateway** | PARTIAL |

### 6.2 ACM 2025 RAG lab (C)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | Not described | NO |
| Policy/authorization decision observable | Not described | NO |
| Execution observable | Not described | NO |
| Result/effect observable | Attack outcome | PARTIAL |
| Distinct events | Not described | NO |
| Explicitly taught | Not described | NO |
| Student reasoning required | Yes (attack design) | PARTIAL |
| Central to learning activity | Attack/defence of RAG | NO (for E1-C) |
| Deterministic/reproducible | Not reported | UNKNOWN |
| Agent/LLM/tool context | LLM (RAG); no agent tools | PARTIAL |

### 6.3 Xi et al. 2026 (B)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | Tool use appears in trajectories | PARTIAL |
| Policy/authorization decision observable | No policy/authorization construct anywhere | NO |
| Execution observable | Tool interactions observed | PARTIAL |
| Result/effect observable | Solve/fail outcomes | PARTIAL |
| Distinct events | Event types not modelled; free-form trajectories | NO |
| Explicitly taught | No; traces are verification evidence | NO |
| Student reasoning required | Yes (solving), not about mediation | PARTIAL |
| Central to learning activity | Traces central to **research**, not instruction | PARTIAL |
| Deterministic/reproducible | Real competitions (non-deterministic) | NO |
| Agent/LLM/tool context | LLM agents with tools | YES |

### 6.4 Hertz & Jump 2013 (C)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | n/a (program execution) | NO |
| Policy/authorization decision observable | None | NO |
| Execution observable | Execution is the traced object | PARTIAL |
| Result/effect observable | Program state / output | PARTIAL |
| Distinct events | Trace = memory state over time | PARTIAL |
| Explicitly taught | Tracing taught explicitly | PARTIAL (different construct) |
| Student reasoning required | Yes, central | YES |
| Central to learning activity | Traces are the core | YES |
| Deterministic/reproducible | Fixed program execution | PARTIAL |
| Agent/LLM/tool context | None | NO |

### 6.5 Nelson 2017 / Xie 2018 (C)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | n/a | NO |
| Policy/authorization decision observable | None | NO |
| Execution observable | Execution tracing taught | PARTIAL |
| Result/effect observable | Program outputs/state | PARTIAL |
| Distinct events | Control-flow/execution paths | PARTIAL |
| Explicitly taught | Tracing strategy taught | PARTIAL |
| Student reasoning required | Yes | YES |
| Central to learning activity | Yes | YES |
| Deterministic/reproducible | Deterministic programs | PARTIAL |
| Agent/LLM/tool context | None | NO |

### 6.6 Weninger et al. 2026 (C)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | n/a | NO |
| Policy/authorization decision observable | None | NO |
| Execution observable | Traces of execution | PARTIAL |
| Result/effect observable | Program state | PARTIAL |
| Distinct events | PETs structure trace events | PARTIAL |
| Explicitly taught | Trace reading as self-paced artefact | PARTIAL |
| Student reasoning required | Yes | YES |
| Central to learning activity | Yes | YES |
| Deterministic/reproducible | Reusable artefacts imply reproducibility | PARTIAL |
| Agent/LLM/tool context | None | NO |

### 6.7 SEED / Du (C)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | Exercise actions, not a mediated request event | NO |
| Policy/authorization decision observable | Some labs touch access control conceptually, not as an event | PARTIAL |
| Execution observable | Yes (operations performed) | PARTIAL |
| Result/effect observable | Yes (effects, e.g. files, permissions) | PARTIAL |
| Distinct events | No event model | NO |
| Explicitly taught | Exploit mechanics, not mediation stages | NO |
| Student reasoning required | Yes (security mechanics) | YES |
| Central to learning activity | Hands-on exploitation | NO (for E1-C) |
| Deterministic/reproducible | Yes (sandboxed, scriptable) | YES |
| Agent/LLM/tool context | None | NO |

### 6.8 Švábenský et al. 2022 (A)
| E1-C element | Evidence | Verdict |
|---|---|---|
| Request observable | Commands executed by trainees | PARTIAL |
| Policy/authorization decision observable | None | NO |
| Execution observable | Commands and their execution | PARTIAL |
| Result/effect observable | Command outcomes inferred | PARTIAL |
| Distinct events | Command histories (timestamps) | PARTIAL |
| Explicitly taught | No — traces used for *assessment* | NO |
| Student reasoning required | Student acts; analysis is automated | NO |
| Central to learning activity | Centra to *assessment*, not instruction | NO |
| Deterministic/reproducible | Training environment; not deterministic-by-design | PARTIAL |
| Agent/LLM/tool context | None | NO |

### 6.9 Repository (AgentSec Labs) — via `labs/`, `src/agentsec/trace/schema.py`
| E1-C element | Evidence in repository | Verdict |
|---|---|---|
| Request observable | `tool_requested` event (`tools/gateway.py`) | **YES** |
| Policy/authorization decision observable | `policy_decision` with `allow`/`deny`/`require_approval` (`policy/schema.py::Decision`) | **YES** |
| Execution observable | `tool_executed` — emitted **only after an allow** | **YES** |
| Result/effect observable | `tool_result` (`ok`/`error`/`denied`/`pending_approval`) | **YES** |
| Distinct events | Versioned trace contract, parent-linked (`trace/schema.py`, 12 event types) | **YES** |
| Explicitly taught | `labs/README.md` ("Eight distinctions"), `labs/TRACE-WALKTHROUGHS.md` | **YES** |
| Student reasoning required | `labs/TRACE-READING-EXERCISES.md` + answer key | **YES** |
| Central to learning activity | The labs are trace-reading exercises | **YES** |
| Deterministic/reproducible | Clock-free fixture; fixed-clock self-check; `agentsec labs check` | **YES** |
| Agent/LLM/tool context | Mediated agent/tool harness | **YES** |

**E1-C conclusion.** Across **every** strong prior source, the column *"policy/authorization decision observable"* is **NO**, and no source implements a **distinct `tool_executed` stage**. The construct is present as a **complete, explicitly-taught, student-reasoned** object only in this repository. This is the strongest single result of the re-audit — and, per §11, it is still not sufficient to make E1 novel.

---

## 7. E1-G Learning-Outcome Analysis

Question: does prior work already **measure conceptual understanding** of the `request → decision → execution → result` distinction?

| Measurement type | Located in prior work? | What it actually measures | Overlap with E1-G |
|---|---|---|---|
| Pre/post self-efficacy surveys | Heverin 2026 (D); Wilson 2026 (confidence) | Confidence, not concept mastery | PARTIAL |
| Post-module **quiz** scores | Wilson 2026 (88%) | Factual/skill recall of exploits | PARTIAL |
| Validated **concept inventory** | CCI (ACM TOCE 2021) | Introductory cybersecurity concepts generally | PARTIAL (method, not construct) |
| **Misconception** interviews | Thompson 2018 (JCERP) | Generic security misconceptions ("conflated concepts") | PARTIAL (method, not construct) |
| Tracing-skill with **empirical evaluation** | Nelson 2017; Xie 2018; Hertz 2013 | Program-tracing skill in programming | PARTIAL (construct differs) |
| Automated **trace-based assessment** | Švábenský 2022 | Behavioural patterns, not conceptual understanding | PARTIAL |
| Trace-**interpretation** questions about mediation stages | **Not located** | — | — |
| **Security concept inventories** beyond CCI | Not located for agent security | — | — |

**E1-G conclusion.** The *instruments and methods* for measuring conceptual understanding in (cyber)security education exist and are validated (CCI; misconception interviews), and trace-based pedagogy has measured outcomes — but **no located study measures conceptual understanding of the mediation distinction between request, policy decision, execution, and result**. E1-G is therefore unoccupied as a *construct*, while being well-supported as a *methodology*. That combination is the crux of the classification in §11: the *measurement* is feasible, which raises the bar on novelty, while the *target* is untested, which is what keeps E1 alive.

---

## 8. Cross-Source Comparison

| Source | Trace-first | Deterministic | Policy decision | Execution | Result | Agent/LLM | Novices | Learning outcome |
|---|---|---|---|---|---|---|---|---|
| Wilson 2026 (C) | NO | UNKNOWN | NO | NO | PARTIAL | PARTIAL | YES | YES |
| ACM 2025 RAG lab (C) | NO | UNKNOWN | NO | NO | PARTIAL | PARTIAL | YES | PARTIAL |
| Xi et al. 2026 (B) | PARTIAL | NO | NO | PARTIAL | PARTIAL | YES | YES | PARTIAL |
| Hertz & Jump 2013 (C) | YES | PARTIAL | NO | PARTIAL | PARTIAL | NO | YES | YES |
| Nelson 2017 (C) | YES | PARTIAL | NO | PARTIAL | PARTIAL | NO | YES | YES |
| Xie 2018 (C) | YES | PARTIAL | NO | PARTIAL | PARTIAL | NO | YES | YES |
| Weninger 2026 (C) | YES | PARTIAL | NO | PARTIAL | PARTIAL | NO | YES | UNKNOWN |
| SEED / Du (C) | NO | YES | PARTIAL | PARTIAL | PARTIAL | NO | YES | PARTIAL |
| Švábenský 2022 (A) | NO | PARTIAL | NO | PARTIAL | PARTIAL | NO | YES | PARTIAL |
| Thompson 2018 (C) | NO | NO | NO | NO | NO | NO | YES | YES (misconceptions) |
| CCI 2021 (C) | NO | NO | NO | NO | NO | NO | YES | YES (instrument) |
| **AgentSec Labs (repo)** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **NO** |

**Pattern [INFER].** No prior row has *policy decision* or a distinct *execution* stage; no prior row has both *trace-first* and *agent/LLM*; the repository is the only row with all of trace-first, determinism, policy decision, execution, result and agent context — but it is also the **only** row with **no learning outcome**, which is precisely the evidence a research contribution would require.

---

## 9. Potential E1 Killers

### 9.1 Killer class 1 — hands-on LLM-security labs with measured outcomes
- **Evidence:** Wilson 2026 (16 graduate students; 88% post-module quiz; 90% increased confidence); ACM 2025 (build-and-attack RAG lab).
- **Overlap:** novice learners, LLM-security subject matter, measured outcomes, hands-on lab.
- **Remaining distinction:** both are **exploitation-centric** (inject/jailbreak/invert a RAG model); neither exposes a **mediated tool pipeline** with an observable authorization decision, and neither uses the trace as the learning object. The E1-C construct is absent from both (tables 6.1–6.2).
- **Reviewer interpretation:** a reviewer who frames E1 as "a hands-on LLM-security lab with measured outcomes" would say **the intervention type already exists**. A reviewer who reads E1-C would say **the construct is new**. The outcome depends on framing, which is why the risk is *high*, not fatal.

### 9.2 Killer class 2 — trace-based pedagogy is established
- **Evidence:** Hertz 2013 (statistically significant grade improvements); Nelson 2017; Xie 2018; Weninger 2026; Guo 2013.
- **Overlap:** E1-A and E1-D are the *established method*; E1-G has precedent.
- **Remaining distinction:** E1 transfers trace-first teaching to **agent-security mediation semantics**; the technique itself is not a contribution.
- **Reviewer interpretation:** *"This applies a known pedagogy (trace-based teaching) to a new topic."* Recombination risk: **HIGH**.

### 9.3 Killer class 3 — reproducible hands-on security labs are established
- **Evidence:** SEED (~28–35 labs, with published evaluation); cyber ranges; remote labs; a 412-study assessment review.
- **Overlap:** E1-B and E1-H are not novel properties.
- **Remaining distinction:** the artefact is the first *agent-security* instance, which is a genuine but **artefactual** novelty, not a research finding. **Risk: MEDIUM.**

### 9.4 Near-miss: Xi et al. 2026
- Traces central + LLM agents + learners — but the traces are researcher-verification data for an *offensive* competition, and there is no authorization/policy construct. **Risk: MEDIUM.**

**Conclusion of §9:** no located source is a **decisive E1 killer**; there is no work that already delivers E1-A…E1-G together. The kill risk is **cumulative** (two established strands + one occupied genre), which is exactly the "insufficiently distinct" condition.

---

## 10. Evidence Gaps

Claims that **cannot** be established from this audit because full text was unavailable:

1. **Wilson 2026 module internals.** Whether the module includes any authorization/execution event model, any trace-reading activity, or any determinism. The abstract indicates it does not, but this is **inference from an abstract**, not full-text evidence.
2. **ACM 2025 lab internals.** Only a snippet was obtainable; the environment, determinism and assessment design are unknown.
3. **Hertz 2013 / Nelson 2017 / Xie 2018 instrument details.** Whether any of them measures a *concept* close to the mediation distinction (all available evidence says the construct is programming-centric, but the instruments were not read).
4. **Weninger 2026 PET structure.** Whether PETs expose something analogous to a policy decision (unlikely for debugging, but unverified).
5. **CCI item content.** Whether any CCI item touches authorization-vs-execution (the instrument is introductory-security; the item list was not obtained).
6. **Non-indexed / non-English venues.** Any relevant work outside the reachable English-language sources would be missed.
7. **Systematic-database coverage.** No Scopus / Web of Science / ACM DL / IEEE Xplore *search* (as opposed to fetch) was possible; coverage is web-search sampling.

**Consequence for classification.** These gaps prevent a claim of *absence*, and they prevent moving the verdict to **PREEMPTED** as much as they prevent moving it to **SURVIVES**. They do not, however, reverse the positive findings in §6–§8, which rest on: (a) the explicit abstracts of the two closest competitors, (b) fifteen-plus targeted E1-C searches across semantic equivalents, and (c) full-text evidence for the one source where full text was obtainable (Švábenský, label A).

---

## 11. Updated E1 Classification

**HIGH-RISK / INSUFFICIENTLY DISTINCT**

**Why not PREEMPTED.** No located work — including the two closest competitors, whose own abstracts describe exploitation-centric RAG modules — exposes a **policy/authorization decision** or a distinct **execution** stage as a learning object (tables 6.1–6.8: the *policy decision* column is `NO` everywhere), and no work teaches the full `request → decision → execution → result` construct. E1-C is unoccupied.

**Why not SURVIVES AS A RESEARCH QUESTION.** Three independent strands each already own a substantial part of E1 and are mature: trace-based pedagogy owns E1-A/E1-D/E1-G (Hertz, Nelson, Xie, Weninger, Guo); reproducible lab methodology owns E1-B/E1-H (SEED, cyber ranges); and "novices + LLM security + measured outcomes" is already **published** (Wilson 2026). The residual novelty is one untested conceptual target plus a transfer to agent security — thin, and not to be inflated.

**Why not SURVIVES ONLY AS AN ARTIFACT / EXPERIENCE REPORT.** That remains a plausible *publication strategy* (§12) but is not a verdict about the *research question*.

**Why not INCONCLUSIVE.** Full-text access did fail on the closest competitors, and §10 records that. But the verdict here does not turn on that gap: even taking the two closest competitors' own abstracts at face value, they lack E1-C, and the "insufficiently distinct" risk follows from the *combination* of an occupied genre and occupied component strands. Classifying INCONCLUSIVE would understate the positive evidence gathered (E1-C absent across every source; Švábenský full text confirming trace-in-education is assessment-oriented).

**Residual uncertainty (must be stated).** If Wilson 2026 or the ACM 2025 lab were found, on full text, to include a mediated tool pipeline with observable authorization decisions and a trace-reading activity, the verdict would move to **PREEMPTED** for the LLM case. This is the single decisive test that remains open, and it is recorded rather than resolved.

---

## 12. Publication Implication (descriptive only; no paper drafted)

Based on the evidence, the following contribution types appear supportable — stated descriptively, with no venue recommendation and no claim of novelty:

- **Experience report** — the strongest fit. The design rationale (mediated gateway as a single boundary; declarative scenarios; trace-first teaching; eight sequenced labs; the "Eight distinctions") exists and is coherent; the required evidence (rationale + honest reflection + light evaluation) is largely present. No testable novelty claim is needed.
- **Artifact paper** — supportable only on the strength of the artefact and its reproducibility; E1-B/E1-H are not themselves novel, so the paper would stand or fall on the design rationale and any adoption/evaluation data.
- **Cybersecurity-education / computing-education research paper** — **high risk**, because it would rest on E1-C + E1-G, which are untested (no prior evidence that E1-C is a real learner difficulty, and no instrument for it). The audit does **not** establish that such a paper would be novel.
- **Not supportable:** any paper claiming E1-A, E1-D, E1-B or E1-H as contributions (each is established in prior work).

---

## 13. Final Conclusion

**Established by the literature:**
- Trace-first / trace-based instruction is an established, empirically-supported pedagogy with measured gains (Hertz 2013; Nelson 2017; Xie 2018; Weninger 2026; Guo 2013).
- Reproducible, sandboxed, hands-on security labs are a settled genre with published evaluation (SEED/Du 2008, 2011; cyber ranges; remote labs).
- Hands-on **LLM**-security labs with **measured outcomes** for **novice** learners are already published (Wilson 2026, JCERP: 88% quiz, 90% confidence; ACM 2025 RAG lab).
- Cybersecurity education has validated instruments and misconception research for conceptual understanding (CCI 2021; Thompson 2018).
- Execution traces are already used in cybersecurity education research — for **automated assessment** (Švábenský 2022, label A), and for **competition verification/behaviour analysis** with LLM agents (Xi 2026).

**Not established:**
- Any prior work — including the two closest competitors, per their own abstracts — that exposes a **policy/authorization decision** or a distinct **execution** stage as a **learning object** (E1-C). Across every strong source, that column is `NO`.
- Any prior work teaching the full `request → policy decision → execution → result` construct.
- Any prior work measuring conceptual understanding of that construct (E1-G for E1-C).

**Uncertain:**
- Whether Wilson 2026 or the ACM 2025 lab contains, on full text, any mediated-tool or authorization-decision content. Full text was unobtainable (403/abstract-only). If they do, E1 becomes **PREEMPTED**; if they do not (as their abstracts indicate), the **HIGH-RISK** verdict stands.
- Whether E1-C is even a genuine novice difficulty: no located evidence either way.
- Whether a trace-first deterministic agent-security lab is substantively different from the published LLM-security-lab genre, or a recombination of two established techniques — the hostile standard treats the latter as insufficient novelty unless the pedagogic difference is demonstrated.

**Verdict:** **HIGH-RISK / INSUFFICIENTLY DISTINCT** — unchanged from Step 2, now with stronger (though still abstract-level for the closest competitors) support for the specific reason: the *construct* E1-C is unoccupied, but the *genre* and every other *component* are occupied, so E1's defensible surface is narrow and would need empirical validation that does not yet exist.

No attempt was made to redefine E1 to preserve novelty; no paper, experiment or protocol was produced; the Phase 17 CLOSED security-research directions remain untouched.

---

## 14. References

**Full text obtained this step:**
1. Švábenský, V., Vykopal, J., Čeleda, P., Tkáčik, K., & Popovič, D. — *Student assessment in cybersecurity training automated by pattern mining and clustering* — **Education and Information Technologies** 27(7):9231–9262, 2022. DOI `10.1007/s10639-022-10954-4`. PMCID `PMC8964927`, PMID `35370440`. `https://pmc.ncbi.nlm.nih.gov/articles/PMC8964927/` — **[A]**
2. Xi, H., Shao, M., Milner, K., Putrevu, V.S.C., Rani, N., Udeshi, M., Krishnamurthy, P., Dolan-Gavitt, B., Garg, S., Shukla, S.K., Khorrami, F., Hillel-Tuch, A., Shafique, M., Karri, R. — *AI In Cybersecurity Education — Scalable Agentic CTF Design Principles and Educational Outcomes* — arXiv:2603.21551, 2026. `https://arxiv.org/html/2603.21551v1` — **[B]**

**Official record / abstract obtained:**
3. Wilson, D.A. — *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach* — **Journal of Cybersecurity Education, Research and Practice** 2026(1):2, 2026. ISSN 2472-2707. `https://digitalcommons.kennesaw.edu/jcerp/vol2026/iss1/2/` — **[C]**
4. Thompson, J.D., Herman, G.L., Scheponik, T., Oliva, L., Sherman, A., Golaszewski, E., Phatak, D., Patsourakos, K. — *Student Misconceptions about Cybersecurity Concepts: Analysis of Think-Aloud Interviews* — **JCERP** 2018(1):5, 2018. `https://digitalcommons.kennesaw.edu/jcerp/vol2018/iss1/5/` — **[C]**
5. Du, W. — *The SEED Project: Providing Hands-on Lab Exercises for Computer Security Education* — **IEEE Security & Privacy**, Sep/Oct 2011 (invited); and Du, W., & Wang, R. — *SEED: A Suite of Instructional Laboratories for Computer Security Education* — **ACM JERIC** 8(1), 2008. Project record: `https://seedsecuritylabs.org/publications.html` — **[C/D]**

**Snippet-level only (full text not obtained):**
6. *A Hands-on Approach to Enhancing LLM Security Education* — ACM, 2025. DOI `10.5555/3787712.3787744`. `https://dl.acm.org/doi/10.5555/3787712.3787744` — **[C]**
7. Hertz, M., & Jump, M. — *Trace-based Teaching in Early Programming Courses* — Proc. 44th ACM SIGCSE, 2013. DOI `10.1145/2445196.2445364` — **[C]**
8. Nelson, G.L., Xie, B., & Ko, A.J. — *Comprehension First: Evaluating a Novel Pedagogy and Tutoring System for Program Tracing in CS1* — ACM ICER, 2017 — **[C]**
9. Xie, B., Nelson, G.L., & Ko, A.J. — *An Explicit Strategy to Scaffold Novice Program Tracing* — ACM SIGCSE, 2018 — **[C]**
10. Weninger, M., et al. — *Towards Guided Omniscient Debugging in Education* (Pedagogical Execution Traces) — DEBT 2026; and *Pedagogical Execution Traces (PETs) for Educational Debugging* — VISSOFT 2026 — **[C]**
11. Guo, P.J. — *Online Python Tutor: Embeddable Web-Based Program Visualization for CS Education* — ACM SIGCSE, 2013 — **[C]**
12. Offenberger, S., Herman, G.L., et al. — *Psychometric Evaluation of the Cybersecurity Concept Inventory* — **ACM TOCE**, 2021. DOI `10.1145/3451346` — **[C]**
13. Lazarov, W., et al. — *Lessons Learned from Using Cyber Range to Teach Cybersecurity at Different Levels of Education* — **Interactive Learning Environments**, 2025. DOI `10.1007/s10758-025-09840-y` — **[C]**
14. *Evaluating Authentic Cybersecurity Training in Cyber Ranges* — ACM CHI, 2023. DOI `10.1145/3544548.3581046` — **[C]**
15. Nagvekar, P.V., et al. — *Teaching log data analysis in Indian cybersecurity classrooms* — **Frontiers in Education**, 2025. DOI `10.3389/feduc.2025.1676938` — **[C]**
16. Mayberry, J.K., et al. — *Assessment and Evidence Practices in Cybersecurity Education* — **JCERP**, 2026 — **[C]**
17. Burton, S.L., et al. — *A Modular Framework for Cybersecurity Laboratory Design* — MDPI, 2025 — **[C]**
18. Otoum, N., et al. — *Remote Labs in Cybersecurity Education* — 2025 — **[C]**

**Grey literature (context only):**
19. Heverin, T. — *Developing AI-Security Self-Efficacy Through Prompt Injection Research in a High School Classroom* — ICGS Global Action Research Reports, 2026 — **[D]**
20. Cloud Security Alliance — *TAISE Compass: AI Safety Education Curriculum* (research note, 2026-03-27) — **[D]**
21. SANS — *SEC546: Securing Agentic AI* — **[D]**; Proofpoint — *Certified AI Agent Security Specialist* (2026) — **[D]**; University of Washington — *Agentic Security Research* (course) — **[D]**
22. `llm-sec.dev`; `prompttrace.airedlab.com`; Sabri, R. — *Rita Cyber Ed* — **[D]**

**Repository sources (unmodified):** `research/20-research-positioning-audit.md`; `research/21-education-literature-hostile-audit.md`; `labs/README.md` (`Eight distinctions`); `labs/TRACE-WALKTHROUGHS.md`; `labs/TRACE-READING-EXERCISES.md`; `labs/INSTRUCTOR-GUIDE.md`; `labs/LOCAL-VERIFICATION.md`; `src/agentsec/trace/schema.py`; `src/agentsec/tools/gateway.py`; `src/agentsec/policy/schema.py`; `src/agentsec/selfcheck.py`; `docs/development.md`.
