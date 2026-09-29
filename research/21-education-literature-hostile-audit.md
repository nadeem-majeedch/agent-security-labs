# Phase 20 — Education Literature Hostile Audit

**Phase:** 20 — Step 2 (full-text hostile literature audit of the computing-education space)
**Date of audit:** 2026-09-28
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs`
**HEAD at audit:** `6802c81`
**Input:** `research/20-research-positioning-audit.md` (Step 1 classification: ARTIFACT / EDUCATIONAL PAPER CANDIDATE; single surviving question E1)
**Standing boundary:** Phase 17 research NO-GO remains CLOSED. This audit touches **only** the educational E1 question and does not reopen benchmark, scoring, attack-success, model-propensity, detector, policy-effectiveness, real-LLM-behaviour, leakage, provider or network research.
**Deliverable:** this file only (`research/21-education-literature-hostile-audit.md`). No source, test, policy, lab YAML, scenario, CI or site file was touched; no paper, experiment, protocol or student data was created.

---

## 1. Audit Objective

E1 is a *candidate* question produced by Step 1, not an established contribution. The purpose of this step is therefore **adversarial**: to find prior work that already answers E1, or that is close enough that a reasonable reviewer would call the repository's version "essentially the same educational intervention." This audit does **not** attempt to prove novelty. It tries to kill E1.

Two failure modes are explicitly avoided: (i) declaring E1 novel because no search returned it (absence of search results is not proof of absence), and (ii) rescuing E1 by redefining it whenever prior art appears. If a strong work preempts E1, it is reported as a killer; if the evidence cannot settle the matter, the verdict is **INCONCLUSIVE**.

---

## 2. E1 Research Question

> **E1.** Does a trace-first deterministic lab methodology improve novice understanding of the **request → policy decision → execution → result** distinctions in **agent-security** workflows?

For analysis, E1 is decomposed into eight independently testable components:

| ID | Component |
|---|---|
| **E1-A** | **Trace-first instruction** — the trace is the *primary* teaching artefact, introduced before or instead of prose/lecture. |
| **E1-B** | **Deterministic / synthetic agent-security environment** — a controlled, reproducible, sandboxed setting with no live model or network. |
| **E1-C** | **Explicit separation of `request → policy decision → execution → result`** as *named, observable, distinct* concepts. |
| **E1-D** | **Trace reading as a primary learning activity** — students themselves interpret the persisted event stream. |
| **E1-E** | **Novice learners** — the target population is students/newcomers, not expert practitioners. |
| **E1-F** | **Agent / LLM / tool-use security context** — the subject matter is AI-agent security (tool calls, policy, egress). |
| **E1-G** | **Learning outcome concerning conceptual understanding** of those distinctions — measured, not merely asserted. |
| **E1-H** | **Reproducible educational artefact** supporting the methodology (versioned, deterministic, re-runnable). |

---

## 3. Search Strategy

**Search families executed** (each with multiple query variants):

| Family | Focus | Representative queries |
|---|---|---|
| A | Cybersecurity education hands-on labs, cyber ranges, testbeds | "SEED labs hands-on security education"; "cyber range cybersecurity education learning outcomes"; "reproducible laboratory artifact cybersecurity education"; "modular framework cybersecurity laboratory design" |
| B | AI / ML / LLM / agent security education | "LLM security education students"; "prompt injection education"; "adversarial machine learning education"; "AI agent security education teaching tool use"; "agentic AI security course students" |
| C | Trace / log / execution-trace teaching | "code tracing education novice learning outcomes"; "execution trace visualization teaching"; "trace-based teaching pedagogy"; "trace-based debugging education"; "log data analysis cybersecurity education" |
| D | Policy / authorization education | "access control laboratory teaching learning outcomes"; "authorization policy education students"; "least privilege education" |
| E | Agent workflow concepts | "agent request decision execution result education"; "tool call authorization education"; "LLM tool use teaching" |
| F | Educational methodology | "trace-first pedagogy"; "log-based learning"; "simulation-based cybersecurity learning outcomes"; "reproducible cybersecurity laboratory education" |

**Venues targeted (by name and by query):** ACM ITiCSE, SIGCSE, ICER, ACM Transactions on Computing Education, IEEE Transactions on Education, IEEE Frontiers in Education, IEEE EDUCON, USENIX ASE / CSET / 3GSE, *Computers & Security*, *Journal of Cybersecurity Education, Research and Practice* (JCERP), *Frontiers in Education*, *Interactive Learning Environments* (Springer), *Computer Applications in Engineering Education*, VISSOFT, and AI/ML-education venues. Also searched: arXiv, ACM DL, IEEE Xplore, Springer, ScienceDirect, ERIC, DigitalCommons, institutional repositories.

**Indexes actually reachable this session:** Google-web (via search API), arXiv HTML (full text). **Blocked:** ACM DL (`dl.acm.org` → 403), DigitalCommons PDF (`viewcontent.cgi` → 403; landing pages reachable), direct PDFs (unsupported content type), MDPI (403). This materially limits full-text coverage and is recorded as a limitation (§9, §14).

**Date range:** no lower bound imposed (foundational work such as Du 2008, Lister 2004, Hertz 2013 is in scope); upper bound September 2026.

---

## 4. Evidence Quality Policy

| Label | Meaning | Citable as evidence of a *finding*? |
|---|---|---|
| **A** | Primary **full-text** peer-reviewed paper / official proceedings paper, read in full this session | Yes |
| **B** | Authoritative full-text paper/preprint read, **not yet** peer-reviewed (or peer-reviewed paper whose full text was read) | Yes for what was read, with the peer-review caveat |
| **C** | Credible secondary source or **abstract-only** evidence (official record/abstract read, full text not obtained) | For *existence/overlap only*; **not** for figures |
| **D** | Grey literature: industry, course, GitHub, blog, training, community | Never as peer-reviewed evidence |
| **X** | Irrelevant after inspection | — |

**Honest statement of what was achieved:** exactly **one** source was read at full text (Xi et al., arXiv:2603.21551, label **B**). **No work in this audit reached label A**, because every peer-reviewed full text attempted was blocked (ACM 403, DigitalCommons PDF 403, MDPI 403) or was a PDF. This is a real limitation: the audit's peer-reviewed evidence is **abstract-level (C)**, and its conclusions are correspondingly hedged. No novelty conclusion rests on D sources.

---

## 5. Candidate Literature

| # | Source | Year | Venue | Quality | Main educational object | Trace/log role | Agent/LLM | Novice learners | Learning outcome | E1 overlap |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Wilson, *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach* | 2026 | JCERP 2026(1) | **C** (abstract+record; PDF 403) | Hands-on LLM-security module (RAG, local open models) | not central | LLM (RAG), **not** agent tool-use | graduate students (n=16) | quiz (88%) + confidence (90%) | **E1-E,E1-G partial; E1-B partial** |
| 2 | *A Hands-on Approach to Enhancing LLM Security Education* | 2025 | ACM (10.5555/3787712.3787744) | **C** (snippet; 403) | Build+attack a RAG LLM system in labs | not central | LLM (RAG) | students | implied (lab assessment) | E1-E,E1-F partial |
| 3 | Xi, Shao, Milner, Putrevu, Rani, Udeshi, Krishnamurthy, Dolan-Gavitt, Garg, Shukla, Khorrami, Hillel-Tuch, Shafique, Karri, *AI In Cybersecurity Education — Scalable Agentic CTF Design Principles and Educational Outcomes* | 2026 | arXiv:2603.21551 | **B** (full text read) | LLM-assisted CTF competition; autonomy levels | **central** (conversation logs, agent trajectories used for verification/analysis) | LLM agents (offensive) | students + expert track | performance + behaviour analysis | E1-A/E1-D partial, E1-F partial |
| 4 | Heverin, *Developing AI-Security Self-Efficacy Through Prompt Injection Research in a High School Classroom* | 2026 | ICGS Global Action Research Reports | **D** | Prompt-injection testing by students | not central | LLM (prompt injection) | high-school (n=12 girls) | self-efficacy (pre/post) | E1-E,E1-F,E1-G |
| 5 | Hertz & Jump, *Trace-Based Teaching in Early Programming Courses* | 2013 | ACM SIGCSE | **C** (abstract; PDF/ACM blocked) | Program memory traces as the teaching vehicle | **central** | none | novice programmers | grades, drop/fail rates (statistically significant) | **E1-A,E1-D,E1-G** |
| 6 | Nelson, Xie & Ko, *Comprehension First: Evaluating a Novel Pedagogy and Tutoring System for Program Tracing* | 2017 | ACM ICER | **C** (PDF not fetched) | Theory of program-tracing knowledge; PLTutor | **central** (execution paths) | none | novices | empirical evaluation | E1-A,E1-D,E1-G |
| 7 | Xie, Nelson & Ko, *An Explicit Strategy to Scaffold Novice Program Tracing* | 2018 | ACM SIGCSE | **C** | Taught tracing strategy | **central** | none | novices | empirical (randomised) | E1-A,E1-D,E1-G |
| 8 | Weninger et al., *Towards Guided Omniscient Debugging in Education* / *Pedagogical Execution Traces (PETs)* | 2026 | VISSOFT / DEBT preprints | **C** (snippets; PDFs unsupported) | PETs: execution traces as reusable self-paced learning artefacts | **central** | none | students | in progress | E1-A,E1-B partial,E1-D |
| 9 | Lister et al., *A Multi-National Study of Reading and Tracing Skills in Novice Programmers* | 2004 | ACM ITiCSE / SIGCSE Bull. | **C** | Reading + tracing as core novice skills | **central** | none | novices | diagnostic (multi-national) | E1-D |
| 10 | Lopez, Whalley, Robbins & Lister, *Relationships between reading, tracing and writing skills in introductory programming* | 2008 | ACM ICER | **C** | Tracing skill correlates with writing | **central** | none | novices | correlational | E1-D |
| 11 | Guo, *Online Python Tutor: Embeddable Web-Based Program Visualization for CS Education* | 2013 | ACM SIGCSE | **C** | Step-by-step execution visualisation | **central** | none | novices | usage/adoption | E1-A,E1-D |
| 12 | Du & Wang, *SEED: A Suite of Instructional Laboratories for Computer Security Education* / *Providing Hands-on Lab Exercises…* | 2008 / 2011 | ACM JERIC / IEEE S&P | **C** | Reproducible hands-on security labs (35 labs) | logs incidental | none | students | adoption, instructor reports | **E1-B,E1-H** |
| 13 | Lazarov et al., *Lessons Learned from Using Cyber Range to Teach Cybersecurity at Different Levels of Education* | 2025 | Springer (Interact. Learn. Environ.) | **C** | Cyber-range teaching across levels | log/artefact incidental | none | multiple levels | qualitative lessons | E1-B partial,E1-E partial |
| 14 | *Evaluating Authentic Cybersecurity Training in Cyber Ranges* | 2023 | ACM CHI | **C** | Evaluation instrument for cyber-range training | incidental | none | trainees | **measured** training outcomes | E1-G partial |
| 15 | Nagvekar et al., *Teaching log data analysis in Indian cybersecurity classrooms: a mixed-methods study of pedagogical challenges and learner difficulties* | 2025 | Frontiers in Education | **C** | Log-data analysis as a competency | **central** (logs) | none | students | mixed-methods (difficulties) | **E1-D,E1-E,E1-G partial** |
| 16 | Mayberry et al., *Assessment and Evidence Practices in Cybersecurity Education* (PRISMA review, 412 studies) | 2026 | JCERP | **C** | Assessment methods in cybersecurity education | n/a | none | students | methodological synthesis | E1-G (meta) |
| 17 | Burton et al., *A Modular Framework for Cybersecurity Laboratory Design* | 2025 | MDPI (preprint) | **C** | Framework for lab design | n/a | none | students | design framework | E1-B,E1-H partial |
| 18 | Otoum et al., *Remote Labs in Cybersecurity Education* | 2025 | J. (ScienceDirect) | **C** | Remote/virtual lab requirements | n/a | none | students | requirements analysis | E1-B partial,E1-H partial |
| 19 | Švábenský et al., *Student assessment in cybersecurity training automated by data mining of traces* | 2022 | Springer (Empir. Softw. Eng. / PMC) | **C** | Mining student traces to assess | **central** (training traces) | none | trainees | automated assessment | E1-D partial (uses traces, doesn't teach trace reading) |
| 20 | OConnor et al., *Teaching a Hands-On Mobile and Wireless Cybersecurity Course* | 2021 | ACM ITiCSE | **C** | Course design, hands-on labs | incidental | none | undergrads | course outcomes | E1-B partial |
| 21 | *AI-Augmented Cyber Labs: Enhancing Cloud-Native Security Education…* | 2025 | ACM | **C** | Adaptive feedback + threat simulation in labs | incidental | none | students | learning gains reported | E1-B partial,E1-G partial |
| 22 | Werther et al., *Experiences in Cyber Security Education: The MIT Lincoln Laboratory Capture-the-Flag Exercise* | 2011 | USENIX CSET | **C** | CTF as education | incident logs incidental | none | students | experience report | E1-B partial |

---

## 6. Detailed Full-Text Findings

Only one source reached full text. For the remaining high-relevance sources the abstract/official record was read; that boundary is stated explicitly and the analysis is confined to what the record states. Per the brief, "semantic equivalence" is treated as potential prior art, so "logs", "telemetry", "trajectories" and "provenance" are treated as candidate equivalents of "trace".

### 6.1 Xi et al. 2026 — *AI In Cybersecurity Education — Scalable Agentic CTF Design Principles and Educational Outcomes* (arXiv:2603.21551) — label B, **full text read**

This is a cross-regional study (US–Canada, MENA, India) of LLM-centred Capture-the-Flag competitions over 2023–2025. Verbatim and structural findings relevant to E1:

- The authors *"require traceable submissions including conversation logs, agent trajectories, and agent code"* — i.e. **process traces are mandatory**, exactly the family E1-D belongs to.
- Traces are used to *"study not only outcomes but also how different degrees of automation shape reasoning behaviors, tool use, and solution strategies"* — **traces are central to the *research* analysis**.
- They formalise three autonomy levels (human-in-the-loop, autonomous agents, hybrid) and compare completion rates.
- Research questions include how autonomy influences performance and what agent-architecture/prompt choices work.

**Overlap with E1:** E1-D partial (traces are central, but as *researcher* data, and the artefact analysed is a competition submission, not a curated teaching trace); E1-F partial (LLM agents, but *offensive CTF* skills, not the semantics of tool/policy mediation); E1-E partial; E1-A no.
**Difference from E1:** E1's learning object is a *mediated agent execution trace* whose purpose is to expose `request → decision → execution → result`; Xi's learning object is *offensive problem-solving*, with traces used to *verify and analyse solutions*. The concepts taught differ (attack success vs policy semantics), and students are not taught to read the trace as the primary conceptual instrument.
**Verdict:** relevant, not a killer.

### 6.2 Wilson 2026 — *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report* (JCERP 2026(1)) — label C (record + abstract)

Peer-reviewed experience report, *Journal of Cybersecurity Education, Research and Practice* (ISSN 2472-2707). State per the record:

- a *"structured, hands-on module"* on adversarial LLM scenarios — *"prompt injection, sophisticated techniques such as jailbreaking and model inversion"*;
- *"a custom Retrieval-Augmented Generation (RAG) platform with local open-source LLMs"* (i.e. **offline/local**, no provider);
- *"a cohort of 16 graduate students … a two-week pilot module"* doing *"red team activities to actively exploit model alignment and privacy vulnerabilities"*;
- *"an average post-module quiz score of 88%, and 90% of students reported increased confidence, demonstrating measurable learning outcomes."*

**Overlap with E1:** E1-E **YES** (novice/graduate learners); E1-G **YES** (measured quiz + confidence); E1-B **PARTIAL** (local open-source LLMs, sandboxed — but not an *agent* harness, and determinism is not reported); E1-F **PARTIAL** (LLM security, but single-system RAG, not agent tool-use/policy).
**Difference from E1:** the learning object is **exploitation** (bypass alignment/privacy controls), not **interpretation of a mediated execution trace**; there is no `request → policy decision → execution → result` construct (E1-C **NO**), traces are not the primary learning artefact (E1-A/E1-D **NO**), and the environment is not deterministic-by-fixture.
**Verdict:** **the closest peer-reviewed *genre* match** — "hands-on LLM-security lab with measurable outcomes" — but it does not preempt E1-C/E1-D/E1-A.

### 6.3 ACM 2025 — *A Hands-on Approach to Enhancing LLM Security Education* (10.5555/3787712.3787744) — label C (snippet; full text blocked)

*"educational approach to LLM security using a Retrieval-Augmented Generation (RAG) framework in lab exercises. Students learn about LLM threats and mitigation strategies by building and attacking a RAG-based LLM system."*

**Overlap:** E1-E/E1-F partial (LLM-security lab, students, hands-on).
**Difference:** same as §6.2 — exploitation-centric, no agent tool-policy semantics, no trace-first design.
**Verdict:** genre overlap; not a killer.

### 6.4 Hertz & Jump 2013 — *Trace-Based Teaching in Early Programming Courses* (SIGCSE) — label C (abstract)

Per the abstract: *"trace-based teaching led to statistically significant improvements [in] student grades, decreased drop and failure rates, and an improvement in students' [attitudes]."* The teaching object is **program memory traces** in an introductory programming course.

**Overlap:** **E1-A YES** (trace-first instruction, named as such), **E1-D YES** (students trace execution), **E1-G YES** (measured grade/drop outcomes).
**Difference:** programming, not security; no agent; no policy/authorization/execution distinction; a *different conceptual target*.
**Verdict:** establishes that *trace-first teaching is not a novel pedagogical technique* — a major reason E1's novelty cannot rest on E1-A/E1-D alone.

### 6.5 Nelson et al. 2017 (ICER) and Xie et al. 2018 (SIGCSE) — program tracing pedagogy — label C

Nelson et al. contribute *"a theory of program tracing knowledge"* and an evaluated tutoring system (PLTutor); Xie et al. propose and evaluate a *"lightweight strategy for tracing code"* for novices. Both establish that **teaching novices to trace execution is a maturing, empirically studied area** with validated instruments and outcomes.

**Overlap:** E1-A, E1-D, E1-G. **Difference:** programming-language semantics, not security or agents.
**Verdict:** strengthens the "trace-first is established" finding from §6.4.

### 6.6 Weninger et al. 2026 — *Pedagogical Execution Traces (PETs)* / *Towards Guided Omniscient Debugging in Education* (VISSOFT/DEBT preprints) — label C

Per snippets: *"PETs transform execution traces into reusable, self-paced learning artifacts"*, extending the trace-based debugging of JavaWiz. This is the **closest current work to "trace as a reusable teaching artefact"**.

**Overlap:** E1-A, E1-B partial (constructed/deterministic traces), E1-D. **Difference:** program debugging, not security/agents.
**Verdict:** shows the "trace-as-learning-artefact" idea is active in 2026; not a killer.

### 6.7 Du & Wang — SEED labs (2008 JERIC / 2011 IEEE S&P) — label C

The SEED project develops *"hands-on laboratory exercises … for cybersecurity education"*, designed so *"no dedicated physical laboratory is needed"* and labs run on personal machines; the suite spans ~35 labs, widely adopted.

**Overlap:** **E1-B YES** (sandboxed, reproducible), **E1-H YES** (a durable reproducible educational artefact), E1-F partial (security generally, not AI/agent security).
**Difference:** SEED labs are exploit/system-security exercises, not trace-interpretation exercises; no `request/decision/execution/result` teaching construct; no measured conceptual-understanding study of *that* construct.
**Verdict:** establishes that **reproducible hands-on security labs are a settled, decades-old genre** — E1's novelty cannot rest on E1-B/E1-H.

### 6.8 Nagvekar et al. 2025 — *Teaching log data analysis in Indian cybersecurity classrooms* (Frontiers in Education) — label C

*"Log data analysis is a core competency in cybersecurity education, essential for investigating cyberattacks…"*; a mixed-methods study of pedagogical challenges and learner difficulties. The full text was not retrievable (JS-rendered page returned boilerplate).

**Overlap:** **E1-D partial** (log **reading** as a learning competency), **E1-E YES**, **E1-G partial** (learner difficulties measured).
**Difference:** host/network **logs** for attack investigation, not a curated agent-execution trace; no policy-decision/execution distinction; not agent security.
**Verdict:** the nearest *security-education* work to "students read execution records"; still not a killer.

### 6.9 Cyber-range studies (Lazarov 2025; *Evaluating Authentic Cybersecurity Training in Cyber Ranges*, CHI 2023) — label C

Cyber ranges are *"interactive and simulated platforms"* (NIST) providing safe hands-on training; the CHI 2023 work specifically *evaluates* such training and notes their evaluation has been under-studied.

**Overlap:** E1-B partial (simulated), E1-E partial, **E1-G partial** (training outcomes/evaluation).
**Difference:** network/incident-response skills in replica environments; not AI-agent policy semantics; no trace-reading pedagogy.
**Verdict:** the "simulated environment + measured education" pattern exists broadly; not a killer.

---

## 7. E1 Component Matrix

Values: **YES / PARTIAL / NO / UNKNOWN**. (Only works with material relevance to ≥2 components are listed; quality labels from §4.)

| Source | E1-A trace-first | E1-B deterministic env | E1-C request→decision→execution→result | E1-D students read trace | E1-E novices | E1-F agent/LLM security | E1-G measured conceptual outcome | E1-H reproducible artefact |
|---|---|---|---|---|---|---|---|---|
| Wilson 2026 (JCERP, C) | NO | PARTIAL | NO | NO | YES | PARTIAL | YES | UNKNOWN |
| ACM 2025 LLM-sec lab (C) | NO | PARTIAL | NO | NO | YES | PARTIAL | PARTIAL | UNKNOWN |
| Xi et al. 2026 (arXiv, B) | PARTIAL | PARTIAL | NO | PARTIAL | YES | PARTIAL | PARTIAL | PARTIAL |
| Heverin 2026 (D) | NO | UNKNOWN | NO | NO | YES | YES | YES (self-efficacy) | NO |
| Hertz & Jump 2013 (C) | YES | NO | NO | YES | YES | NO | YES | NO |
| Nelson et al. 2017 (C) | YES | NO | NO | YES | YES | NO | YES | PARTIAL |
| Xie et al. 2018 (C) | YES | NO | NO | YES | YES | NO | YES | NO |
| Weninger et al. 2026 (C) | YES | PARTIAL | NO | YES | YES | NO | UNKNOWN | PARTIAL |
| Guo 2013 Python Tutor (C) | YES | PARTIAL | NO | YES | YES | NO | NO | YES |
| Du & Wang SEED (C) | NO | YES | NO | NO | YES | PARTIAL | NO | YES |
| Lazarov 2025 cyber range (C) | NO | PARTIAL | NO | NO | YES | NO | PARTIAL | PARTIAL |
| CHI 2023 cyber-range eval (C) | NO | PARTIAL | NO | NO | YES | NO | YES | PARTIAL |
| Nagvekar 2025 (C) | PARTIAL | NO | NO | YES | YES | NO | PARTIAL | NO |
| Švábenský 2022 (C) | NO | NO | NO | PARTIAL | YES | NO | PARTIAL | PARTIAL |
| **Repository (AgentSec Labs)** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **NO** | **YES** |

**Reading of the matrix [INFER]:**
- **No source has E1-C = YES.** No located work, peer-reviewed or otherwise, treats `request → policy decision → execution → result` as the explicit conceptual learning target.
- Every *other* component (A, B, D, E, F, H) is covered **YES** by at least one located source.
- The combination `A ∧ B ∧ C ∧ D ∧ F` (trace-first, deterministic, request/decision/execution/result, students read the trace, agent security) is **not** present in any single located work.
- The repository is the only row with **E1-C = YES**, and the only row with **seven of eight = YES**; its sole gap is **E1-G (measured conceptual outcome)**.

---

## 8. Potential E1 Killers

No single located work combines most of E1-A … E1-G, so there is no classical "killer" in the sense of one paper that already does E1. The kill risk is **cumulative**, arising from two well-established strands whose intersection is essentially E1.

### 8.1 Killer class 1 — "hands-on LLM-security labs with measured outcomes"

- **What it already does:** delivers a hands-on LLM-security module (RAG + local open models), for novice/grad learners, and **measures outcomes** (Wilson 2026: 88% quiz, 90% confidence; ACM 2025: lab-based RAG attack/defence).
- **What E1 adds:** a *different learning object* (trace interpretation of `request/decision/execution/result`) and a *different environment* (deterministic mediated agent harness rather than a live RAG stack).
- **Is the distinction defensible?** **Conditionally.** The *educational genre* ("hands-on LLM-security lab, measured outcomes") is occupied; E1's defence depends entirely on the specific conceptual target (E1-C) and the trace-first design (E1-A/E1-D). A hostile reviewer could reasonably say: *"This is a hands-on LLM-security lab with a new conceptual emphasis; the intervention genre is not new."* **Risk: HIGH.**

### 8.2 Killer class 2 — "trace-first teaching" as an established technique

- **What it already does:** trace-first/trace-based instruction with demonstrated learning gains (Hertz 2013); validated tracing pedagogy and instruments (Nelson 2017; Xie 2018; Lister 2004; Lopez 2008); traces as reusable learning artefacts (Weninger 2026); trace visualisation at scale (Guo 2013).
- **What E1 adds:** applies trace-first teaching to *agent security* rather than to programming, and introduces the `request/decision/execution/result` construct.
- **Is the distinction defensible?** **Conditionally.** E1-A and E1-D cannot be claimed as contributions; they are the established method. The contribution, if any, is the *transfer* of an established method to a new conceptual domain. **Risk: HIGH.**

### 8.3 Killer class 3 — "reproducible hands-on security labs" as an established artefact genre

- **What it already does:** SEED labs and cyber ranges provide reproducible, sandboxed, adoption-proven hands-on security education artefacts (Du 2008/2011; Lazarov 2025; Burton 2025; Otoum 2025; Mayberry 2026 review of 412 interventions).
- **What E1 adds:** an *AI-agent-specific* reproducible artefact. Useful, but E1-B/E1-H are not novel properties.
- **Is the distinction defensible?** The artefact is genuinely new *for agent security*; the *property* (reproducible hands-on lab) is not. **Risk: MEDIUM.**

### 8.4 Near-miss not elevated to a killer

**Xi et al. 2026** is the only located work where **traces are mandatory and central** *and* the domain is **LLM agents** *and* the population is learners. It fails to be a killer because its traces are researcher-verification artefacts for an **offensive** competition and its conceptual target is attack performance, not the mediation semantics E1 teaches. A hostile reviewer might nonetheless cite it as evidence that "agent traces in education" is already occupied. **Risk: MEDIUM.**

**No source is classified as a decisive E1 killer.** Per the brief, no attempt is made to redefine E1 to manufacture distance; the risk classes above are reported as-is.

---

## 9. Negative Evidence

Searches that produced **no** strong match (recorded as absence of *located* results, explicitly **not** as proof of absence):

- **Teaching the specific construct** `request → policy decision → execution → result`: multiple query families (D and E, plus targeted phrasings such as "difference authorization and execution observable policy decisions") returned no education paper on this construct. The only returns were unrelated (physical school access control, CDSE policy courses, zero-trust roadmaps).
- **Agent-security education as a *research* object:** searches for peer-reviewed empirical studies of teaching agent security returned only **industry training** (SANS SEC546, Proofpoint, Cisco), **grey curricula** (CSA TAISE), and **course pages** (UW *Agentic Security Research*), never a peer-reviewed education study.
- **Deterministic/synthetic *agent* environments for teaching:** no education-focused artefact was located; "deterministic" environments appear in *research* testbeds (sandboxed service surfaces, e.g. REDAgentBench), not in computing-education work.
- **Trace-based teaching *in security* (as opposed to programming or log analysis):** not located; the trace-based teaching literature is programming-education, and the security-education literature uses logs for *investigation*, not for teaching *mediation semantics*.
- **Peer-reviewed full texts:** every attempted peer-reviewed full-text fetch was blocked (ACM DL 403 three times; DigitalCommons PDF 403; MDPI 403). This is a **search limitation**, not evidence about the literature.

**Consequence:** the "gap" cannot be asserted. The most that can be said is claim **B** ("no located prior work combines the relevant components") shading into claim **C** ("the combination appears under-studied, but this requires empirical validation"). Claim **A** ("no prior work exists") is **not** supported and is not made.

---

## 10. Grey Literature

Recorded separately from peer-reviewed evidence; never used to establish a finding.

- **Industry training:** SANS **SEC546: Securing Agentic AI**; SANS **SEC595** (AI/ML for cybersecurity); SANS **SEC555** (Detection Engineering/SIEM); Proofpoint *Certified AI Agent Security Specialist* (2026); Cisco agent-security modules (2026-06); GTK Cyber AML courses; Cydrill ML-security; nullcon "Advanced Hands-On AI Security Workshop" (2026).
- **Curricula / standards notes:** CSA **TAISE Compass** AI-safety curriculum note (2026-03-27); Educause "Applied AI Security for Higher Ed" learning lab (2026); NCyTE Center "Teaching AI Security: Hands-On LLM Hardening" (2026-08-21); OWASP LLM Top-10 2025 / Agentic 2026 + Agent Control Standard.
- **Course pages:** University of Washington *Agentic Security Research* (PhD-level course); `aisecure.github.io` CS598 adversarial-ML course.
- **Community labs / platforms:** `llm-sec.dev`; `prompttrace.airedlab.com`; *Rita Cyber Ed* prompt-injection classroom exercise; `LLMSecurityGuide` GitHub (2026); Awesome-Search-Agent-Papers / awesome-ai-agent-papers indexes.
- **Grey *research*:** Heverin 2026 action-research report (ICGS) — empirical but a practitioner action-research report, not a peer-reviewed study; NSF SaTC-EDU project pages (NJIT "Education on Securing AI System under Adversarial…"; Gupta "Adversarial Malware Analysis").
- **Community/testbed tools:** *LLM Agent Security Testbed* (pie-script, 2026-09).

**Observation [INFER, D-level]:** agent-security *teaching material* is abundant and current, but essentially all of it is grey/industry/community. The absence of peer-reviewed agent-security *education research* is the strongest single signal in this audit — and it cuts **both** ways: it means E1 is under-studied, **and** it means there is little validated method to build on.

---

## 11. Preemption Assessment

**Classification: HIGH-RISK / INSUFFICIENTLY DISTINCT**

**Why not PREEMPTED.** No located work — peer-reviewed or not — teaches the specific construct `request → policy decision → execution → result` (E1-C is `NO` in every prior row of §7), and no located work combines E1-A, E1-B, E1-C, E1-D and E1-F. E1 is therefore **not** preempted by a single study.

**Why not SURVIVES AS A RESEARCH QUESTION.** Three independent strands each already own a substantial part of E1, and each is mature:
1. **E1-A + E1-D + E1-G** are owned by a decade of trace-based/tracing pedagogy (Hertz 2013; Nelson 2017; Xie 2018; Lister 2004; Guo 2013; Weninger 2026).
2. **E1-B + E1-H** are owned by the reproducible hands-on security-lab genre (SEED labs; cyber ranges).
3. **E1-E + E1-F + E1-G** (the *exact* combination "novice learners + LLM security + measured outcomes") are already occupied by peer-reviewed experience reports (Wilson 2026; ACM 2025).

A hostile reviewer who reads only strand 3 can say *"this is a hands-on LLM-security lab with measured outcomes — already published"*; a reviewer who reads strand 1 can say *"this is trace-based teaching, a 2013 technique."* Because each component is individually established and the genre is occupied, E1's residual novelty is confined to the **specific conceptual target** (E1-C) and its **transfer** to agent security. That is a *thin* differentiator, and the brief forbids inflating it by redefinition. Under the hostile standard, the honest verdict is **HIGH-RISK / INSUFFICIENTLY DISTINCT**.

**Why not SURVIVES ONLY AS AN ARTIFACT / EXPERIENCE REPORT.** That framing *is* defensible (§13) but it is a *publication strategy*, not a finding about the E1 research question; the assessment above concerns E1-as-a-question, for which the risk is high rather than fatal.

**Why not INCONCLUSIVE.** The evidence is sufficient to show (a) component-level saturation and (b) genre saturation; the remaining uncertainty is about *degree*, not about existence. INCONCLUSIVE would overstate the doubt.

---

## 12. What Would Still Need to Be Demonstrated

Because E1 is judged **HIGH-RISK** rather than dead, the following would still have to be established — identified here only as *evidence requirements*, not designed or executed:

1. **That E1-C is a genuine, previously-unaddressed conceptual difficulty for novices.** No located work demonstrates that learners confuse `request`, `policy decision`, `execution`, and `result`, let alone that a trace-first intervention fixes it. Absent evidence of the *problem*, a study of E1-C has no established target.
2. **That the trace-first deterministic design causes the improvement, not the topic or the novelty effect.** This requires a comparison condition (e.g. conventional instruction on the same concepts), because trace-based teaching is already known to help (§6.4 are independent).
3. **That the outcome is *conceptual understanding* of the distinctions, not recall or confidence.** Both near neighbours measured quiz scores and self-efficacy (Wilson 2026) or grades (Hertz 2013); E1-G demands a targeted instrument for the distinctions themselves.
4. **That a *causal or at least controlled* empirical result exists** with novice learners (E1-E) in the agent-security setting (E1-F).
5. **That the difference from Wilson 2026 / ACM 2025 is substantive**, not merely "different learning object and different environment" — which, per the brief's hostile standard, are differences of kind that must be argued on pedagogic grounds, not asserted.
6. **A reproducibility/portability demonstration**: that the artefact transfers across institutions/courses without the original author (the E1-H claim as an artifact-paper ingredient).

Nothing above has been designed, prototyped or collected here; per the brief, no protocol is proposed beyond naming the evidence that would be required.

---

## 13. Publication Implications (descriptive only)

| Category | What could be claimed | What that requires | Availability given this audit |
|---|---|---|---|
| **Artifact paper** | A reproducible, deterministic, offline agent-security teaching harness | A defensible non-standard design claim + evaluation/adoption | Artefact is mature; the *design claim* and *evaluation* are absent; E1-B/E1-H are not themselves novel |
| **Experience report** | "Designing eight deterministic agent-security labs: what we learned" | Coherent rationale + honest reflection + light evaluation | **Best fit.** The rationale, sequencing, boundary statements and instructor material already exist; barrier is writing + light evidence |
| **Computing-education research paper** | "Trace-first deterministic labs improve novice understanding of request/decision/execution/result" | The full E1-G study (§12), pre-registered, with controls | **High risk** per §11; the conceptual target is not yet shown to be a real learner difficulty |
| **Cybersecurity-education paper** | As above, framed as cybersecurity pedagogy | As above + cybersecurity-education framing | Same as above; the genre is occupied by Wilson 2026 / ACM 2025 for *LLM* security labs |

No venue is recommended or ranked.

---

## 14. Final Verdict

**HIGH-RISK / INSUFFICIENTLY DISTINCT.** E1 is neither preempted nor clearly novel; it sits in the zone the brief calls "insufficiently distinct," where the components and the genre are each established and the residual contribution rests on a single untested conceptual target.

**What the literature establishes [peer-reviewed, though largely at abstract level due to access blocks]:**
- Trace-first/trace-based instruction is an established, empirically-supported technique (Hertz 2013; Nelson 2017; Xie 2018; Lister 2004; Guo 2013; Weninger 2026).
- Reproducible, sandboxed, hands-on security labs are a settled genre with long-standing artefacts (SEED labs, cyber ranges) and a substantial assessment literature (Mayberry 2026; 412 interventions).
- Hands-on **LLM**-security labs with **measured learning outcomes** for **novice** learners are already published (Wilson 2026, JCERP; ACM 2025) — the nearest genre match to E1.
- LLM-agent traces are already used in education-adjacent research, as researcher-verification data (Xi et al. 2026).

**What the literature does not establish:**
- No located work teaches the specific construct `request → policy decision → execution → result` (E1-C).
- No located work combines trace-first instruction with a deterministic agent-security environment for novice learners (E1-A ∧ E1-B ∧ E1-D ∧ E1-F).
- No located work measures novice *conceptual understanding* of those mediation distinctions (E1-G for E1-C).

**What remains uncertain:**
- Whether E1-C is even a real learner difficulty (no evidence either way was located).
- Whether the "trace-first deterministic agent-security lab" is materially different from the published LLM-security-lab genre, or a recombination of two established techniques.
- Whether the search's peer-reviewed coverage was adequate: **all peer-reviewed full texts were blocked**, so a full-text review (ACM DL, IEEE Xplore, TOCE, JCERP PDFs, Springer) could surface work that would move this verdict toward PREEMPTED.

**Boundary statement.** This audit did not reopen, and does not touch, the Phase 17 CLOSED security-research directions; it examined only the educational E1 question. No empirical claim, benchmark, score, measurement, detector, provider or real-model behaviour is introduced. The deterministic-fixture boundary recorded in `docs/development.md` is unchanged.

---

## 15. Sources

**Label A:** none (every peer-reviewed full text attempted was blocked).

**Label B (authoritative full text read; not yet peer-reviewed):**
1. Xi, H., Shao, M., Milner, K., Putrevu, V.S.C., Rani, N., Udeshi, M., Krishnamurthy, P., Dolan-Gavitt, B., Garg, S., Shukla, S.K., Khorrami, F., Hillel-Tuch, A., Shafique, M., Karri, R. (2026). *AI In Cybersecurity Education — Scalable Agentic CTF Design Principles and Educational Outcomes.* arXiv:2603.21551. `https://arxiv.org/html/2603.21551v1`

**Label C (official record/abstract or credible secondary; full text not obtained):**
2. Wilson, D.A. (2026). *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach.* Journal of Cybersecurity Education, Research and Practice, Vol. 2026, No. 1, Art. 2. ISSN 2472-2707. `https://digitalcommons.kennesaw.edu/jcerp/vol2026/iss1/2/`
3. *A Hands-on Approach to Enhancing LLM Security Education.* (2025). ACM. `https://dl.acm.org/doi/10.5555/3787712.3787744` (403 on fetch)
4. Hertz, M., & Jump, M. (2013). *Trace-Based Teaching in Early Programming Courses.* Proc. 44th ACM SIGCSE. `https://dl.acm.org/doi/10.1145/2445196.2445364` (403 on fetch); abstract via `https://cse.buffalo.edu/~mhertz/tracing-sigcse-2013.pdf`
5. Nelson, G.L., Xie, B., & Ko, A.J. (2017). *Comprehension First: Evaluating a Novel Pedagogy and Tutoring System for Program Tracing in CS1.* ACM ICER. `https://faculty.washington.edu/ajko/papers/Nelson2017PLTutor.pdf`
6. Xie, B., Nelson, G.L., & Ko, A.J. (2018). *An Explicit Strategy to Scaffold Novice Program Tracing.* ACM SIGCSE. `https://www.benjixie.com/publication/sigcse-2018/sigcse-2018.pdf`
7. Weninger, M., et al. (2026). *Towards Guided Omniscient Debugging in Education* (Pedagogical Execution Traces). DEBT 2026 preprint. `https://ssw.jku.at/General/Staff/Weninger/Papers/Weninger_DEBT_26_Preprint.pdf`
8. Weninger, M., et al. (2026). *Pedagogical Execution Traces (PETs) for Educational Debugging.* VISSOFT 2026 preprint. `https://ssw.jku.at/General/Staff/Weninger/Papers/Weninger_VISSOFT_26_Preprint.pdf`
9. Lister, R., Simon, B., Thompson, E., Whalley, J.L., & Thomas, L. (2004). *A Multi-National Study of Reading and Tracing Skills in Novice Programmers.* ACM ITiCSE / SIGCSE Bulletin. `https://dl.acm.org/doi/10.1145/1041624.1041673`
10. Lopez, M., Whalley, J., Robbins, P., & Lister, R. (2008). *Relationships between reading, tracing and writing skills in introductory programming.* ACM ICER. `https://dl.acm.org/doi/abs/10.1145/1404520.1404531`
11. Guo, P.J. (2013). *Online Python Tutor: Embeddable Web-Based Program Visualization for CS Education.* ACM SIGCSE. `https://pg.ucsd.edu/publications/Online-Python-Tutor-web-based-program-visualization_SIGCSE-2013.pdf`
12. Du, W., & Wang, R. (2008). *SEED: A Suite of Instructional Laboratories for Computer Security Education.* ACM JERIC. `https://eric.ed.gov/?id=EJ890193`
13. Du, W. (2011). *SEED: Hands-On Lab Exercises for Computer Security Education.* IEEE Security & Privacy. `https://seedsecuritylabs.org/wenliangdu/Research/paper/seed_ieeeSPmagazine2011.pdf`
14. Lazarov, W., et al. (2025). *Lessons Learned from Using Cyber Range to Teach Cybersecurity at Different Levels of Education.* Interactive Learning Environments (Springer). `https://link.springer.com/article/10.1007/s10758-025-09840-y`
15. *Evaluating Authentic Cybersecurity Training in Cyber Ranges.* (2023). ACM CHI. `https://dl.acm.org/doi/10.1145/3544548.3581046`
16. Nagvekar, P.V., et al. (2025). *Teaching log data analysis in Indian cybersecurity classrooms: a mixed-methods study of pedagogical challenges and learner difficulties.* Frontiers in Education. `https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1676938/full`
17. Mayberry, J.K., et al. (2026). *Assessment and Evidence Practices in Cybersecurity Education.* JCERP. `https://digitalcommons.kennesaw.edu/jcerp/vol2026/iss1/23/`
18. Burton, S.L., et al. (2025). *A Modular Framework for Cybersecurity Laboratory Design.* MDPI. `https://www.mdpi.com/2813-8856/2/4/21`
19. Otoum, N., et al. (2025). *Remote Labs in Cybersecurity Education.* `https://www.sciencedirect.com/org/science/article/pii/S2156183425000075`
20. Švábenský, V., Vykopal, J., & Čeleda, P. (2022). *Student assessment in cybersecurity training automated by data mining of traces.* `https://pmc.ncbi.nlm.nih.gov/articles/PMC8964927/`
21. OConnor, T.J., et al. (2021). *Teaching a Hands-On Mobile and Wireless Cybersecurity Course.* ACM ITiCSE. `https://dl.acm.org/doi/pdf/10.1145/3430665.3456346`
22. *AI-Augmented Cyber Labs: Enhancing Cloud-Native Security Education…* (2025). ACM. `https://dl.acm.org/doi/10.1145/3769694.3771136`
23. Werther, J., et al. (2011). *Experiences in Cyber Security Education: The MIT Lincoln Laboratory Capture-the-Flag Exercise.* USENIX CSET. `https://www.usenix.org/conference/cset11/experiences-cyber-security-education-mit-lincoln-laboratory-capture-flag-exercise`

**Label D (grey literature / industry / course / community):**
24. Heverin, T. (2026). *Developing AI-Security Self-Efficacy Through Prompt Injection Research in a High School Classroom.* ICGS Global Action Research Reports. `https://research.girlsschools.org/s/home/item/1264`
25. Cloud Security Alliance. *TAISE Compass: AI Safety Education Curriculum* (research note, 2026-03-27). `https://labs.cloudsecurityalliance.org/agentic/csa-research-note-taise-compass-curriculum-20260327/`
26. SANS. *SEC546: Securing Agentic AI.* `https://www.sans.org/cyber-security-courses/securing-agentic-ai`
27. Proofpoint. *Certified AI Agent Security Specialist (2026).* `https://www.proofpoint.com/us/ai-agent-security-specialist-2026`
28. Educause. *Applied AI Security for Higher Ed Professionals* (learning lab, 2026). `https://events.educause.edu/learning-labs/2026/applied-ai-security-for-higher-ed-professionals`
29. NCyTE Center. *Teaching AI Security: Hands-On LLM Hardening* (2026-08-21). `https://ncytecenter.wildapricot.org/event-6766528/`
30. University of Washington. *Agentic Security Research* (course). `https://agent-security.cs.washington.edu/`
31. `llm-sec.dev` interactive LLM-security labs. `https://www.llm-sec.dev/labs/prompt-injection`
32. `prompttrace.airedlab.com` prompt-injection labs. `https://prompttrace.airedlab.com/labs`
33. Sabri, R. *Rita Cyber Ed — Prompt Injection Lab.* `https://ritasabri.github.io/rita-cyber-ed/`
34. `LLM Security 101` (community guide, 2026). `https://github.com/requie/LLMSecurityGuide`
35. *LLM Agent Security Testbed* (community tool, 2026-09). `https://kitploit.com/en/tools/github/pie-script/llm-agent-testbed`

**Repository sources (unchanged, cross-referenced):** `research/20-research-positioning-audit.md`; `docs/development.md` §"Research status (Phase 17 — CLOSED, research NO-GO)"; `labs/README.md`; `labs/LOCAL-VERIFICATION.md`. All source, test, policy, lab-YAML, CI and site files were left unmodified.
