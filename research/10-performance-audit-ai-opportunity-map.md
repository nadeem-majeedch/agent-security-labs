# 10 — Performance Auditing × AI × Computational Verification: Opportunity Map (Phase 10)

**Status: PHASE 10 COMPLETE — SURVIVORS: 0 → NO SURVIVORS**

**Date of audit:** 25 September 2026
**Domain shift:** performance auditing × public-sector auditing × data science × ML/LLM/agents × computational evidence × reproducibility × audit trails × independent verification.
**Standing constraints (unchanged):** no invented citations, no invented gaps, no marketing claims as scientific evidence, no LLM-wrapper or RAG or provenance-only or explainability-only or dataset-only novelty, no "human in the loop" as novelty, no confidential audit data, no implementation, no paper prose, no commit/push. Every major novelty claim must be supported by primary literature.

---

## Part 0 — Method, labels, and the headline finding

| Label | Meaning | Citable as a figure? |
|---|---|---|
| **A** | Fetched and read at the source (abstract or full text). | Yes, for what was read |
| **B** | Read only via a snippet, listing, or another work's summary. | **No** |
| **C** | Not verified at all. | No |

Claim tags: **[FACT]** · **[INFER]** · **[HYP]** · **[OPEN]**.

### 0.1 Headline finding

**[FACT]** The AI-in-*auditing* literature is real and large, but it is overwhelmingly about **financial audit and controls**, not performance audit. IntelliAudit, the most directly relevant 2026 system, states this explicitly: *"LLM-based auditing research has concentrated primarily on financial audits (Wang et al. 2026, 2025a, 2025b) an[d] AI-driven workflow…"* **[A]**.

**[FACT]** The AI-in-*public/performance* audit literature consists almost entirely of institutional and conceptual material — OECD's cross-country consultation with 15 audit institutions across 14 countries (May 2026) **[B]**, KPMG's SAI brief (Feb 2026) **[B]**, an INTOSAI Journal practitioner piece (Jun 2026) **[B]**, and conceptual/exploratory academic work such as Genaro-Moya et al. in *MDPI Administrative Sciences* 6(2):78 (2025) **[B]** and an econstor working paper on scaling AI in SAIs (Mdhlalose 2026) **[B]**. No primary *technical* research line on performance-audit analytics was located.

**[INFER] This is the paradox of Phase 10, and it produces the NO-SURVIVOR verdict.** The performance-audit AI space looks empty — and the reason it is empty is not neglect. It is that **every identifiable technical sub-problem in performance auditing reduces to a problem that is already solved in an adjacent, better-instrumented field**, and the performance-audit setting removes the very thing a research contribution needs: a ground-truth oracle.

Concretely, the four load-bearing reductions:

| Performance-audit problem | Already solved where | Occupant |
|---|---|---|
| Audit evidence sufficiency | IT audit evidence evaluation | **IntelliAudit** — "audit conclusions depend on **evidentiary sufficiency** rather than keyword matching"; produces "**missing-evidence analysis**" and "**challenges adverse findings**" **[A]** |
| Independent challenge / devil's advocate against a finding | adversarial-critique architectures + research-artifact review | **ARCADE**, the **adversary** harness, insurance adversarial self-critique **[B]** |
| Selecting and validating a causal identification strategy | econometrics / program-evaluation automation | **Mining Causality** (IV search), **CauSciBench**, **NBER w35588** (AI agents + econometric coding), an epidemiology causal-inference agent, **Causal-LLM** **[B]** |
| Cross-source numeric/logical consistency | financial-document analysis | **SEC-FINTABLES**, **FinVerBench**, **FinLongDocQA**, **FinStructBench**, **LOGICONBENCH** **[B]** |

**[INFER]** Additionally, three of the *domain-specific* technical candidates are occupied by mature literature rather than by AI papers: performance-indicator gaming (Heckman's identification method; threshold/bunching manipulation detection; 2026 J-PART empirical work), efficiency/peer benchmarking (45 years of DEA plus a 2026 review of three decades of DEA×ML integration), and measurement/definition change detection (structural-break and change-point detection, plus official-statistics time-series-break conventions such as SDMX and FAO guidance).

---

## Part A — Defining performance auditing and mapping AI entry points

### A.1 The analytical lifecycle (per ISSAI/INTOSAI, GAO *Government Auditing Standards* 2024 revision, and ECA methodology)

Performance audit examines **economy, efficiency and effectiveness** — value for money — of government programs, and answers whether public resources were used well, whether intended results were achieved, and **why not**. The standards corpus establishes the touchstones used throughout this document: GAO's *Government Auditing Standards* 2024 revision frames "**sufficient, appropriate evidence**… The concepts of evidence, significance, and audit risk form a framework for applying [standards]" **[B]**; the ECA states that auditors "assess the evidence we find against the audit criteria, and on this basis develop audit findings and conclusions" **[B]**; PCAOB AS 1105 and ISA 500 establish "sufficient appropriate audit evidence" as the sufficiency/appropriateness pair **[B]**.

### A.2 Twenty lifecycle stages × AI entry

`[C]` = closed for our purposes · `[M]` = modelled/solved in an adjacent field · `[S]` = saturated by AI literature.
Suitability column answers the brief's instruction not to assume every stage is automatable.

| # | Stage | AI can enter? | Status | Governing evidence |
|---|---|---|---|---|
| 1 | Audit planning | partly | `[M]` | "Leveraging Artificial Intelligence in Audit Planning" (CPA Journal, Aug 2026) **[B]**, conceptual only |
| 2 | Problem identification | partly | `[M]` | AI-for-evaluation framing (OECD "AI in policy evaluation", 2025) **[B]** |
| 3 | Risk assessment | yes | `[S]` | ML risk models are a large financial-audit literature **[B]** |
| 4 | **Audit questions** | weak | `[OPEN]`-ish but not technical | no technical work found; requires professional judgement |
| 5 | **Criteria development** | weak | `[OPEN]`-ish but not technical | ECA: auditors "examine the quality of the indicators and measures developed by auditees" **[B]** |
| 6 | Evidence collection | yes | `[S]` | IntelliAudit **[A]** |
| 7 | Data acquisition | yes | `[S]` | NBER w35188 "Deep Research on a Loop: Using AI Agents to Construct Economic Datasets" **[B]** |
| 8 | Data cleaning | yes | `[S]` | Phase 9: DataAiPrep, automated data-quality validation **[B]** |
| 9 | Analytical procedures | yes | `[S]` | Phase 9 analytics-agent benchmarks |
| 10 | Sampling | yes | `[M]` | classical statistical audit sampling **[B]** |
| 11 | Statistical analysis | yes | `[S]` | P-Bench/Fisher-R1 (Phase 9) **[B]** |
| 12 | Benchmarking | yes | `[C]` | DEA + ML: "first review… covering 3 decades of scholarly works from 1996 to 2025" **[B]** |
| 13 | Causal analysis | yes | `[S]` | Mining Causality, CauSciBench, NBER w35588 **[B]** |
| 14 | **Finding development** | partly | `[S]` | IntelliAudit generates findings; ReAgent (Phase 9) audits claims **[A]** |
| 15 | Evidence evaluation | yes | `[S]` | **IntelliAudit** — sufficiency, missing-evidence analysis **[A]** |
| 16 | Root-cause analysis | yes | `[S]` | Causal-LLM "integrates causal discovery algorithms with LLMs to automate root cause [analysis]" (ACM 2026) **[B]** |
| 17 | Recommendation development | yes | `[S]` | IntelliAudit produces "remediation guidance" **[A]** |
| 18 | Reporting | yes | `[S]` | generic LLM report generation — explicitly excluded by the brief |
| 19 | Quality assurance | yes | `[S]` | IntelliAudit challenges findings; the-adversary harness **[A/B]** |
| 20 | Follow-up | yes | `[M]` | continuous-auditing literature; no agentic occupant found |

**[INFER] Part A conclusion.** Of 20 stages, 11 have an AI occupant, 5 are handled in adjacent fields, 3 are excluded by the brief, and only **criteria development** and **audit-question formulation** are technically unoccupied — and both are **judgement stages with no ground truth**, which is precisely why they have no technical literature and cannot carry an experimental contribution.

---

## Part B — Current AI-in-auditing literature

### B.1 Public-sector / SAI-specific (institutional and conceptual)

| Source | Date | Label | Content |
|---|---|---|---|
| **OECD, The state of artificial intelligence in public audit** | 2026-05 | B | consulted **15 audit institutions across 14 countries and the EU** (Mar–Jul 2025) "to assess current AI adoption in public audit"; framed against the OECD Framework for Trustworthy AI |
| **KPMG, AI in Government Audit and Public Expenditure** | 2026-02 | B | "SAIs and finance ministries are moving from AI pilots to scaled, risk-aware deployment" — **consulting material, not scientific evidence** |
| **Genaro-Moya et al., Artificial Intelligence and Public Sector Auditing** (*MDPI Administrative Sciences* 6(2):78) | 2025 | B | authors describe it as "a conceptual and exploratory analysis… interpretative and illustrative, rather than conclusive" |
| **Mdhlalose, Scaling AI in Public Audit Institutions** (econstor) | 2026 | B | working paper; cites OECD working paper on SAIs overseeing AI |
| **INTOSAI Journal, "How AI and Innovation are Changing Audit"** | 2026-06 | B | practitioner commentary; IMPACT 2026 conference framing |
| **INTOSAI PAS external publications** | — | B | includes a study on "the feasibility of incorporating the advanced language model, such as generative AI like ChatGPT, in **SAI Thailand's performance audit**" |
| **World Bank, The Quality of Audits by Supreme Audit Institutions** | — | B | "Public sector auditing provides unbiased, objective assessments of public sector programs, policies, operations, and results" |
| **GAO Innovation Lab**; **GAO-24-107237** | 2024–2026 | B | GAO reports deploying "a large language model… augmented with GAO-specific information and appropriate security controls" |

**[FACT]** Not one of these is a primary technical research contribution. The OECD artefact is a consultation report; KPMG is marketing; Genaro-Moya et al. self-describe as interpretative; the INTOSAI material is practitioner guidance. **[INFER]** The brief's instruction not to treat marketing as scientific evidence therefore removes most of this corpus from evidentiary use — and what remains is descriptive.

### B.2 Financial / IT / internal audit AI (technical, and the actual state of the art)

| Source | Date | Label | Content |
|---|---|---|---|
| **IntelliAudit** (arXiv:2608.07688) | 2026-08-07 | **A** | see Part C |
| **Fedyk et al., Is artificial intelligence improving the audit process?** (*Review of Accounting Studies*) | 2022 | B | large empirical study; auditors leverage AI to improve processes |
| **Kokina et al., Challenges and opportunities for AI in auditing** (ScienceDirect) | 2025 | B | adoption study at large public accounting firms |
| **Johri et al., Enhancing audit quality and reducing costs** (PMC12876229) | 2026 | B | AI lets auditors "evaluate all data… and automate routine tasks" |
| **Silahtaroğlu et al., ML approach to audit modification risk** (*JRFM* 19(3):221) | 2026 | B | financial-ratio categorical states → audit modification prediction |
| **Predicting Material Misstatements Using Machine Learning** (*The Accounting Review* 100(6):225) | 2025 | B | ML forecasting of material misstatements |
| **Hunt et al., Using machine learning to predict auditor switches** | 2021 | B | ML on auditor-switch likelihood |
| **Audit Data Analytics, ML, and Full Population Testing** | 2022/2026 | B | full-population testing |
| **Ilieva et al., Generative AI-Based Framework for Proactive Quality Management and Auditing** (*Applied Sciences* 16(9):4237; preprint 202601.0579) | 2026 | B | "structured conceptual framework… three functional [layers]" — conceptual |
| **Kálmán et al., From the EU AI Act to Audit Practice** (*MDPI* 2(3):12) | 2026 | B | "doctrinal requirements-to-controls mapping" — conceptual |
| **LLM-as-a-Verifier** | 2026-07 | B | general-purpose verification framework |
| **Proofreader: Informally Auditing Formal Proofs with LLMs** (Vanderbilt) | 2026-06 | B | "an informal audit screens for the kinds of issues an alert human co-author might [catch]" |
| **Specification-anchored audit of code** (arXiv:2604.26495) | 2026-04 | B | "LLM-driven evidence construction with structured reasoning steps, **not formal verification**" |

**[INFER]** The technical state of the art in AI-for-auditing is: (i) prediction of financial-audit outcomes from structured financial data, (ii) full-population analytics, (iii) one retrieval-grounded multi-agent system for IT control-evidence evaluation, and (iv) a set of conceptual governance frameworks. **None of it addresses economy, efficiency, effectiveness, outcomes, or value for money.**

---

## Part C — Existing AI/support systems mapped

| System / class | Input | Output | Method | Human role | Validation → ground truth | Metrics | Reproducible? | Key limitation |
|---|---|---|---|---|---|---|---|---|
| **IntelliAudit** (arXiv:2608.07688) **[A]** | a control + heterogeneous evidence corpus (policies, records, spreadsheets, operational artifacts) | auditor-facing recommendation with **cited evidence, rationale, missing-evidence analysis, remediation guidance** | retrieval-grounded **multi-agent**: retrieves artifacts → generates evidence-grounded assessment → **challenges adverse findings** → **adjudicates disagreements** | decision-support; "should remain decision-support tools rather than autonomous certification systems" | "multiple **simulated** organizations"; "**expert auditor review** and audit-readiness user feedback"; instantiated on **ISO/IEC 27001** | not captured at abstract level | not stated | **IT controls**, not performance audit; simulated organisations; "revealing the importance of human oversight for **calibrating sufficiency judgments** and correcting **overly permissive recommendations**" |
| **Financial-statement error detection** (FinVerBench, arXiv:2605.29586) **[B]** | financial statements | error identification + explanation | five-stage evaluation framework | — | benchmark | "LLMs can identify errors in financial statements but **struggle to explain them**" | benchmark released | financial statements only |
| **FinStructBench** (SSRN 6506403) **[B]** | structured financial data | extraction/aggregation/reasoning | benchmark | — | benchmark | not captured | benchmark | financial only |
| **SEC-FINTABLES** (ACL Findings 2026) **[B]** | financial tables | four inconsistency-detection sub-tasks | benchmark | — | benchmark | not captured | benchmark | financial tables only |
| **ARCADE** (medRxiv 2025.12.21.25342744) **[B]** | complex documents | adversarial critique of "the analytical agent's scores and reasoning through structured debate" | "three-stage semantic pipeline… preserves retrieval grounding but adds **adversarial validation**" | — | not captured | not captured | not stated | document analysis, not audit; medRxiv preprint |
| **the-adversary** (GitHub, 2026-03) **[B]** | "papers, code, releases, and protocols" | adversarial findings + **independent verifier reproduction** | "finds what you missed before a reviewer does, then makes an independent verifier **reproduce every finding against your artifact**"; thesis: "finding is cheap; verification is the product" | user | — | — | open source | research artifacts, not audit findings |
| **Adversarial self-critique underwriting** (arXiv:2602.13213) **[B]** | underwriting case | decision + critique + "formal failure-mode taxonomy for decision-negative agents" | "critic agent challenges the primary agent's conclusions before human review" | human reviews all binding decisions | "500 expert-validated cases" | reported hallucination ↓ 11.3%→3.8%, accuracy ↑ 92%→96% — **do not cite; single-source secondary reporting** | not stated | insurance underwriting |
| **ECA AWARE / ECA methodology platform** **[B]** | audit evidence corpus | evidence linked to findings and conclusions | methodology governance, not AI | auditor | professional standards | — | — | not a research system; establishes that finding→evidence linkage is *already* standardised practice |
| **OpenAudit** (GitHub `jerikdcruz/OpenAudit`) **[B]** | published audit reports | "more structured datasets" | extraction + "partnerships to ensure the validity of resulting data" | community | — | — | open source | dataset project, not a method |
| **GAO Innovation Lab** **[B]** | — | — | "exploration of data science, artificial intelligence" | — | — | — | — | institutional capability, not a published method |
| **Commercial audit-analytics / AI-audit tooling** (Vero AI, DataSnipper, AuditBoard-class, Kognitos, Aurascape, Sweet Security, Vanta-class) | — | — | — | — | **none published** | — | no | **marketing material; excluded as scientific evidence per the brief** |

**[INFER] Part C conclusion.** The one system that touches the brief's Part G (evidence sufficiency) and Part K/L (challenge findings, quality assurance) is **IntelliAudit**, and it does so with expert-auditor validation. Everything else is either financial-audit-specific, conceptual, commercial, or a dataset project.

---

## Part D — Performance audit vs financial audit: does AI research address the performance-specific problems?

| Performance-audit concept | Distinctive analytical demand | AI research coverage |
|---|---|---|
| Economy | input cost relative to a benchmark of what was needed | **DEA/ML mature** (3-decade review, Kehinde 2026) **[B]** |
| Efficiency | outputs per input, with heterogeneous operating environments | **DEA/ML mature** **[B]** |
| Effectiveness | outcomes vs intended results | program-evaluation literature + econometrics agents **[B]** |
| Program performance | time series of administrative indicators | change-point/structural-break literature; **no performance-audit-specific work found** |
| Outcomes | distal, multi-causal, often unmeasured | econometrics; **no audit-specific work found** |
| Implementation | fidelity between policy design and delivery | **none found** |
| Service delivery | equity, accessibility, quality of service | **none found** |
| Value for money | integrating the three Es into a defensible judgement | **none found** |
| Policy/program results | attribution to the program | causal-inference automation (occupied) **[B]** |
| Causes of poor performance | root cause | **Causal-LLM** (causal discovery + LLM root cause) **[B]** |

**Part D answer [INFER].** AI research has **not** adequately addressed the performance-specific concepts (implementation, service delivery, value-for-money integration, unmeasured outcomes). But the reasons matter: these are *construct-definition and professional-judgement* problems, and the fields that do address their technical cores (production-frontier estimation, program evaluation, causal discovery) are all better instrumented than performance auditing. **The absence is a measure of the problem's unsuitability for experimental research, not of its importance.**

---

## Part E — The hard analytical problems, assessed

The brief supplied seven candidate problems. Each is assessed against primary literature.

### E.1 Evidence-to-finding logical validity (DATA → ANALYSIS → EVIDENCE → FINDING)

* **Occupied:** IntelliAudit performs evidence-grounded assessment with cited evidence and rationale, then challenges findings and adjudicates disagreements **[A]**. Phase 9 established that claim↔artifact consistency is solved for research artefacts by **ReAgent** (static + dynamic auditing, with a benchmark) and **Chain-of-Evidence** (claims must trace to a grounding source).
* **Status: CLOSED** for the general problem. The performance-audit instantiation would be a domain transfer.

### E.2 Root-cause analysis — correlation vs a defensible causal explanation

* **Occupied:** **Causal-LLM** (ACM, Apr 2026) "integrates causal discovery algorithms with Large Language Models (LLMs) **to automate root cause [analysis]**" **[B]**; **CF-RAG** identifies a "**Correlation Trap**": "existing systems cannot distinguish **causally decisive evidence** from overwhelmingly correlated yet misleading information" **[B]**; **Causal Agent Replay** models an agent run as a structural causal model and applies a **do-operation** to attribute outcomes **[B]**.
* **Status: CLOSED.**

### E.3 Economy / efficiency / effectiveness reasoning about resources → activities → outputs → outcomes

* **Occupied:** DEA and its ML integration (see Part D). The *reasoning* problem is the production-frontier problem, solved since Charnes-Cooper-Rhodes (1981, 2,800+ citations) **[B]** and reviewed as recently as 2026 **[B]**.
* **Status: CLOSED.**

### E.4 Counterfactual reasoning — "performance improved" vs "the program caused the improvement"

* **Occupied:** the entire program-evaluation identification literature (DiD, IV, RD, synthetic control) plus its automation: **Mining Causality** (LLM-assisted IV search) **[B]**, **CauSciBench** (367 causal-reasoning tasks from 100+ real papers across 9 disciplines) **[B]**, an **AI agent for automated causal inference in epidemiology** **[B]**, and evidence that automated program-evaluation papers are being produced at scale (reported as 1,000 automated empirical "program evaluation" papers) **[B — secondary reporting, do not cite as a number]**.
* **Status: CLOSED.**

### E.5 Indicator validity — poorly defined, gameable, incomplete, misleading, disconnected from outcomes

* **Partially occupied, from three directions:**
  * **Gaming identification:** Heckman, Heinrich & Smith, *Measuring Government Performance* (2011, 328 citations) — "one can identify gaming by estimating **the correlation between a performance measure and the true goal** of the organization" **[B]**; threshold/bunching manipulation detection is a mature econometric toolkit (Kleven, *Annual Review of Economics*; Andarge et al. 2025; procurement-bunching literature) **[B]**.
  * **Measurement theory:** Manheim & Garrabrant, "Building less-flawed metrics" (2023) **[B]**; Fisher, "Performance Measurement: Issues, Approaches" (*HDSR* 2021) — "we illustrate some of the consequences of **poor performance measurement**, explore some of the reasons why poor metrics are in use" **[B]**.
  * **Recent KPI work:** Teymourifar (2026) — "adaptive analytics, drift detection, and routine KPI refresh cycles can help sustain indicator validity" **[B]**.
* **Status: MAJOR MODIFICATION** — a formal, automated indicator-validity assessment would consolidate existing theory. The residual is automation, not a new phenomenon. **And note the general trap:** "a new dataset alone" and "an LLM wrapper" are both excluded by the brief.

### E.6 Cross-source evidence consistency (administrative data, reports, KPIs, budgets, surveys, policy documents)

* **Occupied (technically, in finance):** **SEC-FINTABLES** evaluates LLM detection of "**logical inconsistencies in financial tables**" across four sub-tasks **[B]**; **FinVerBench** (benchmark validity and calibration) **[B]**; **FinLongDocQA** — "annual reports often exceed **129k tokens**, exacerbating the [long-context bottleneck]" **[B]**; **FinStructBench** **[B]**; **LOGICONBENCH** (ICLR 2026) **[B]**; an industry "LLM-enabled multi-document correlation" framework for financial compliance **[B]**.
* **Status: CLOSED.** The specific performance-audit twist — changing definitions, conflicting denominators, revisions — is real, but each is a *data-engineering* variant of inconsistency detection, and Part B/E of Phase 9 already established that grain/definition errors are the least-covered item *and* the most engineering-shaped.

### E.7 Evidence sufficiency — does evidence exist vs does it actually support the finding?

* **Occupied:** **IntelliAudit** is built on exactly this distinction — "audit conclusions depend on **evidentiary sufficiency** rather than keyword matching" — and emits **missing-evidence analysis** alongside its assessment, validated by expert auditors **[A]**.
* **Also:** the standards corpus formalises the requirement (GAO GAS 2024 "sufficient, appropriate evidence"; ISA 500; AS 1105) **[B]**, so there is no terminological gap to exploit.
* **Status: CLOSED.** The residual — a *quantitative* sufficiency calculus for non-statistical performance-audit evidence — is discussed in Part E.7-residual below, and is the single most interesting residual of the phase.

**E.7-residual.** Financial audit has a sufficiency formalism (statistical and non-statistical sampling, audit risk models). Performance audit's evidence is heterogeneous, largely non-statistical (documents, interviews, site observation, expert panels), and the standards say "sufficient appropriate" without a calculus. **[HYP]** A formal sufficiency calculus over heterogeneous audit evidence would be a genuine contribution. **Two blockers:** (i) it requires an expert-annotated corpus of real findings with sufficiency labels — i.e. the annotation/confidentiality problem the brief's Part P explicitly excludes; (ii) it is an extension of audit sampling theory, so a reviewer can plausibly call it an adaptation rather than a new phenomenon. **Not promoted (see M-OV3).**

---

## Part F — Performance audit + causal inference

**Does an AI system already select and justify an identification strategy with machine-verifiable assumptions?** Substantially yes.

| Source | What it does | Label |
|---|---|---|
| **Mining Causality: AI-Assisted Search for Instrumental Variables** (arXiv:2409.14202; Han et al. 2025, 22 citations) | "The instrumental variables (IVs) method is a leading empirical strategy for causal inference. **We propose using large language models (LLMs) to** [search for and validate IVs]" | B |
| **CauSciBench** (Acharya et al. 2025) | "**367 evaluation tasks** based on **100+ real-world research papers across 9 disciplines**, augmented with synthetic scenarios and textbook [material]" | B |
| **NBER w35588, Galiani et al. 2026 — AI Agents and Prompt Engineering in Econometric Coding** | "The tasks cover applied econometric methods, including linear regression and classical inference, **difference-in-differences, regression** [discontinuity], **instrumental variables**, panel estimators"; reported result that giving AI "agency… boosts task success from **74.4% to 95.7%**" | B |
| **Can AI Master Econometrics?** (arXiv:2506.00856) | "Econometrics AI Agent achieves significantly higher replication accuracy, with rates above **66%** for course assignments" | B |
| **An AI Agent for Automated Causal Inference in Epidemiology** (medRxiv, 2026-02-06) | "this study aims to develop an epidemiological **causal inference agent by calling LLMs**" | B |
| **Causal-LLM** (ACM DOI 10.1145/3801228.3801315, 2026-04-25) | "a hybrid framework that integrates causal discovery algorithms with LLMs to automate root cause [analysis]" | B |
| **CF-RAG** (OpenReview 9U51rOnGko) | names the **Correlation Trap**: inability "to distinguish causally decisive evidence from overwhelmingly correlated yet misleading information"; introduces **Counterfactual RAG** | B |
| **Causal Agent Replay** (arXiv:2606.08275) | models an agent run as an SCM, applies a **do-operation**, re-executes under the same stochastic policy, measures outcome shift | B |
| **Executable Counterfactuals** (ICLR 2026) | "operationalizes causal reasoning through code and math problems… requires the simultaneous use of **abduction, intervention, and prediction**" | B |
| **GPLab** (*JASSS* 29(1):6, 2026) | generative agent-based framework for policy [evaluation] | B |
| **HLER** (arXiv:2603.07444) | "Human-in-the-Loop Economic Research via Multi-[agent]" | B |
| **AI-Assisted Workflow for Large-Scale Replication and Reanalysis** (Xu et al. 2026) | "automated **full-paper replication** — retrieving materials, reconstructing environments, executing code" | B |
| **Auto-Empirical-Research-Skills** (GitHub) | "**23,000+ agent skills** for empirical research across 8 social science disciplines" | B |

**[INFER] Part F conclusion.** The brief's proposed research problem — "can an AI analytical system select and justify an appropriate causal identification strategy for a performance-audit question, while providing **machine-verifiable evidence for its assumptions and conclusion**?" — is **occupied in its first half** (strategy selection: Mining Causality; benchmarked: CauSciBench, NBER w35588; agentified: epidemiology causal agent, Causal-LLM) and **solved or bounded in its second half** (assumption checks: pre-trend and manipulation tests are standard econometric practice; sensitivity analysis with interpretable bounds is published; the correlation-vs-causal-evidence discrimination is named and addressed by CF-RAG). **The performance-audit wrapper does not add a new technical constraint.** CLOSED.

---

## Part G — Performance audit + evidence sufficiency

**Question: can an AI system distinguish "evidence exists" from "evidence actually supports the finding"?**

**Answer: yes — this is precisely IntelliAudit's design target.** Verbatim: "audit conclusions depend on **evidentiary sufficiency** rather than keyword matching"; the system "retrieves relevant artifacts, generates an evidence-grounded assessment, **challenges adverse findings, adjudicates disagreements**, and produces an auditor-facing recommendation with **cited evidence, rationale, missing-evidence analysis, and remediation guidance**" **[A]**. Validation used "multiple **simulated** organizations", **expert auditor review**, and audit-readiness user feedback, on ISO/IEC 27001 **[A]** — and the authors' own honest limitation is that human oversight matters for "**calibrating sufficiency judgments** and correcting **overly permissive recommendations**" **[A]**.

**Is it already solved by standards, rule-based systems, audit analytics, LLMs, evidence graphs, RAG, or verification systems?** Partially each:

* **Standards:** define sufficiency/appropriateness but give no algorithm (GAO GAS 2024; ISA 500; AS 1105) **[B]**.
* **Rule-based / audit analytics:** no sufficiency logic found **[B]**.
* **Evidence graphs / provenance:** mature computationally, but they answer *traceability*, not *sufficiency* (Phase 8/9: TraceCaps, Agent-Sentry, the evidence-tracing survey, CoE, ReAgent) **[B]**.
* **LLM/RAG:** IntelliAudit is the occupant, and it explicitly warns against autonomous certification **[A]**.

**Status: CLOSED for the general problem.** The only residual is the quantitative-sufficiency calculus over *heterogeneous non-statistical* performance-audit evidence (E.7-residual), which fails on ground truth and resource feasibility.

---

## Part H — Performance audit + data quality: genuine change vs changed measurement

**Question: can an AI system distinguish a genuine performance change from a change in how performance was measured?**

| Component | Occupying literature | Status |
|---|---|---|
| detecting a break in a series | structural-break and change-point detection; mature econometrics and statistics, with 2026 reviews and a *Journal of Time Series Analysis* special issue on "data segmentation… structural breaks and real-time monitoring" **[B]** | `[C]` as a method |
| attributing a break to a **measurement/definition/reporting change** | official-statistics convention: SDMX states "**Time series breaks can be explained by changes to classifications, methodology, survey scope, data sources**"; FAO guidance: "When major methodological changes cannot be applied retrospectively… the resulting **lack of comparability should be** [flagged]" | `[C]` — handled by convention and metadata, not by an inference procedure |
| detecting **deliberate** manipulation of a reported measure | bunching/threshold-manipulation estimators (Kleven review; Andarge et al. 2025 — "relies on **discontinuity-based and/or bunching estimators to detect manipulation**"); public-procurement bunching below thresholds; "Ghost citizens" notches; Heckman's measure-vs-goal correlation | `[C]` |
| detecting manipulation in a **performance-evaluation cycle** | **Li et al., J-PART 2026** — "uncovering a routine form of **manipulation embedded in bureaucratic practices**… advances theories of performance gaming" | `[C]` |

**Status: CLOSED as a research opening, and this is the most important closure of Part H.** Note the structure carefully: the *method family* exists (breaks, bunching, gaming identification), the *institutional practice* exists (metadata flags, comparability notes), and the *empirical phenomenon* has just been documented in a top public-administration journal. **[INFER]** What does not exist is an agent that orchestrates these — and orchestration is an application, which the brief excludes. **MAJOR MODIFICATION at best.**

---

## Part I — Cross-source contradiction

**Question: reconcile Dataset A + Dataset B + annual report + budget + performance report + policy document and detect inconsistent totals, contradictory KPIs, incompatible definitions, unsupported claims, unexplained changes.**

**Status: CLOSED (technically), with the hard cases explicitly benchmarked in the financial analogue.**

* **SEC-FINTABLES** (ACL Findings 2026) evaluates "the ability of mainstream LLMs to detect **logical inconsistencies in financial tables**, focusing on the four sub-tasks defined in Sec[tions…]" **[B]**.
* **FinVerBench** (arXiv:2605.29586) is a 2026 benchmark on "**validity and calibration**"; it reports prior work finding "LLMs can identify errors in financial statements but **struggle to explain them**" **[B]**.
* **FinLongDocQA** (arXiv:2604.03664) addresses the multi-document long-context case: "annual reports often exceed **129k tokens**, exacerbating the [bottleneck]"; it explicitly evaluates "**Document-Level Numerical Reasoning across Single and
 [multi-document]**" settings **[B]**.
* **FinStructBench** (SSRN 6506403) benchmarks "extract, **aggregate** and reason over structured [financial data]" — i.e. the aggregation-level mismatch case **[B]**.
* **LOGICONBENCH** (ICLR 2026) benchmarks logical consistency **[B]**.
* Industry frameworks for "**multi document correlation**… cross document reasoning" in fraud/compliance exist **[B]**.

**Does the brief's list of hard cases (different time periods, changing definitions, differing aggregation levels, conflicting denominators, revisions, missing provenance) constitute an uncovered technical problem?** **[INFER] No.** Each maps to an occupied sub-problem: aggregation-level mismatch → FinStructBench; long multi-document periods → FinLongDocQA; definition change → Part H (metadata + break detection); revisions → provenance (Phase 8/9); missing provenance → generic provenance, excluded by the brief. **CLOSED.**

---

## Part J — Audit trail for AI-generated audit analysis

**Question: can AI-generated audit analysis be made reproducible, traceable, independently executable, versioned, evidence-linked and reviewable — specifically for **audit evidence and audit findings**?**

**Does a system already provide finding → evidence → data → code → execution → result?** Substantially yes, from three directions:

1. **Audit profession:** the ECA states that auditors "**assess the evidence we find against the audit criteria, and on this basis develop audit findings and conclusions**" **[B]**, and its AWARE methodological platform formalises the finding–evidence relationship **[B]**. So the *linkage discipline* is standard practice.
2. **Research verification (Phase 9):** **Chain-of-Evidence** (ScientistOne, arXiv:2605.26340) — "every claim must trace, through a recorded evidence chain, to a grounding source", built at claim-production time **[B]**; **ReAgent** (arXiv:2609.22111) — static + dynamic auditing producing a "structured repository-level audit report, enabling transparent **evidence traceability**" **[A]**.
3. **Econometrics at scale:** Xu et al. (2026), "automated **full-paper replication** — retrieving materials, reconstructing environments, executing code, and [reproducing results]" **[B]**; **AI4Reproducibility**; **REPRO-Bench** **[B]**.

**Status: CLOSED.** Per the brief's own instruction ("If yes, reject generic provenance as a contribution"), the finding→evidence→execution chain is occupied. **MAJOR MODIFICATION at most** (the residual would be audit-specific attestation, which Phase 8 already reduced to provenance security).

---

## Part K — Human–AI collaboration: where can AI provide *measurable* assistance?

**Measurable division-of-labour questions and their occupancy:**

| Question | Occupancy |
|---|---|
| AI identifies candidate anomalies; auditor validates | Saturated: anomaly detection is decades old; the human-validation pattern is standard **[B]** |
| AI generates hypotheses; auditor selects audit questions | No technical work found; **judgement stage, no ground truth** |
| AI proposes causal models; auditor validates assumptions | Occupied by the econometrics-agent cluster (§Part F) **[B]** |
| AI checks evidence sufficiency; auditor makes final judgement | **Occupied by IntelliAudit**, whose stated limitation is exactly the calibration of sufficiency judgement and correction of "overly permissive recommendations" **[A]** |
| **AI independently challenges an auditor's finding (devil's advocate)** | **Occupied:** IntelliAudit "challenges adverse findings, adjudicates disagreements" **[A]**; **ARCADE** adds "adversarial validation: a dedicated critic agent systematically challenges the analytical agent's scores and reasoning through structured debate" **[B]**; **the-adversary** is a released adversarial review harness with independent verification of every finding **[B]**; **adversarial self-critique** in underwriting (arXiv:2602.13213) **[B]** |
| Does AI assistance enhance or erode expert judgement? | **Occupied:** NBER w35720, Autor et al. 2026, "**Does AI Assistance Enhance or Erode Expertise?**" **[B]**; plus the audit-judgement / automation-bias accounting literature **[B]** |

**Status: CLOSED.** Note carefully: the devil's-advocate idea — which is the most attractive candidate this setting offers, because an adversarial reviewer of a performance finding has a *natural* ground-truth proxy (does the critique identify a defect the auditor agrees is real?) — **already has three independent occupants, one of them released as open source.**

---

## Part L — Audit quality assurance

**Question: can an AI system detect unsupported or analytically weak audit findings before publication?**

* **IntelliAudit** performs exactly this pre-publication function for IT control evidence: challenges findings, adjudicates, flags missing evidence **[A]**.
* **ReAgent** (Phase 9) does the equivalent for research documents, and its hardest reported case is "experiments that **reproduce reported numbers while deviating from the claimed methodology**" **[A]** — i.e. the analytically-weak-but-numerically-correct case.
* **the-adversary** (released harness) targets pre-review defect discovery with verified findings **[B]**.
* **Proofreader** (2026) informally audits formal proofs **[B]**; **specification-anchored audit** (arXiv:2604.26495) audits code against specifications with structured evidence construction **[B]**.
* Institutional: GAO's own AI work and the CAQ's 2026 guidance on governance/documentation **[B]** — governance, not method.

**Status: CLOSED.**

---

## Part M — Government / public-sector data availability

**[FACT]** Reproducible experiments *are* possible without confidential data:

| Data family | Availability | Notes |
|---|---|---|
| Federal award/expenditure records (USASpending-class, FPDS-class) | public | transaction-level, machine-readable, historical depth |
| Audited agency performance reports and budget documents | public (GovInfo, agency sites) | the Part I cross-source corpus |
| **PART** program ratings (OMB, 2003–onward) | public (archived White House site; NIH; policy archives) | "a series of diagnostic questions used to assess and evaluate programs across a set of performance-related criteria" **[B]** — an existing labelled performance-rating dataset |
| GAO report corpus | public | GovInfo fielded search; structured metadata **[B]** |
| Supreme-audit-institution reports (ECA, national SAIs) | public | ECA publishes methodology and reports **[B]** |
| World Bank / development-project performance data | public | openknowledge.worldbank.org |
| Open audit-report datasets | emerging | **OpenAudit** GitHub project is converting reports into "more structured datasets" **[B]** |

**[INFER] Part M conclusion.** Data availability is **not** the binding constraint — and that is precisely why the NO-SURVIVOR result is about *contribution*, not feasibility. The constraint is ground truth: for performance findings, there is no oracle that says whether a finding is correct, so any evaluable contribution must either (a) import a ground truth from an adjacent field (financial statements, IT controls, research artefacts — all already occupied), or (b) manufacture one by expert annotation at a cost and confidentiality profile the brief excludes.

---

## Part N — Twelve candidates

Clusters: **PA** = performance analytics · **EV** = evidence/verification · **CE** = causal/program evaluation · **QA** = audit quality / human–AI. Fields 1–20 as required. No ranking implied.

---

### C-PA1 — Measurement-Change Attribution for Government Performance Series

1. **Title:** Did Performance Change, or Did the Measure Change? Attributing Trend Breaks in Administrative Performance Data
2. **Problem:** an apparent improvement/degradation in a performance indicator is often a change in definition, coverage, denominator, reporting period, or collection instrument — and audit conclusions inherit the error.
3. **Why it matters to performance audit:** the first question an effectiveness finding must survive is whether the underlying series is comparable over time.
4. **SOTA:** change-point/structural-break detection is mature; SDMX and FAO guidance require breaks to be flagged in metadata; bunching estimators detect threshold manipulation; Li et al. (J-PART 2026) document manipulation in evaluation cycles; Heckman (2011) identifies gaming via measure–goal correlation. **[B]**
5. **Closest 5 primary papers:** Heckman/Heinrich/Smith (2011) **[B]**; Li et al. (J-PART 2026) **[B]**; Andarge et al. (2025) **[B]**; Kleven (2016) bunching review **[B]**; SDMX/FAO comparability guidance **[B]**.
6. **Exact gap:** no procedure attributes a specific trend break to a **documented** measurement change with calibrated error rates, jointly using the series and the accompanying metadata/report text.
7. **Contribution:** a labelled corpus of real government series with documented breaks, plus an attribution procedure (statistical break detection + document-grounded cause attribution) with reported precision/recall.
8. **System:** series analyser + metadata/report retriever + attribution classifier producing a comparability verdict.
9. **Data required:** public agency performance series; the accompanying annual reports and metadata revisions.
10. **Ground truth:** documented methodology changes in public metadata and revision notes; plus expert adjudication of ambiguous cases.
11. **Evaluation:** held-out series with known breaks; confusion matrix for break detection × cause attribution.
12. **Primary metric:** attribution accuracy on series with documented changes, versus break-detection-only baseline.
13. **Baselines:** naive change-point detection; manual-metadata lookup; a strong zero-shot LLM.
14. **Models:** our four available models suffice.
15. **Compute:** single machine.
16. **Reproducibility:** high (public data, deterministic pipeline).
17. **Reviewer objection:** "Every component exists — break detection, metadata flags, and manipulation tests. Orchestrating them is an engineering paper, and the 'corpus' is a dataset contribution, which the brief excludes as novelty."
18. **Falsification:** if break attribution is already implicit in official metadata and shows no residual error, nothing remains.
19. **Novelty confidence:** low.
20. **Feasibility:** high.

---

### C-PA2 — Indicator Validity Auditor (construct, gaming exposure, denominator stability)

1. **Title:** Before You Measure: Automated Construct-Validity Audit of Government Performance Indicators
2. **Problem:** indicators are adopted because they are measurable, not because they measure the outcome; auditors then inherit indicators disconnected from program objectives.
3. **Why it matters:** ECA methodology has auditors "examine the quality of the indicators and measures developed by auditees" **[B]** — currently a judgement task with no instrument.
4. **SOTA:** Manheim & Garrabrant (2023) on less-flawed metrics **[B]**; Fisher (*HDSR* 2021) on consequences of poor performance measurement **[B]**; Heckman (2011) gaming identification **[B]**; Teymourifar (2026) KPI validity/drift **[B]**; PART as an institutionalised manual instrument **[B]**.
5. **Closest 5:** Manheim & Garrabrant (2023) **[B]**; Fisher (2021) **[B]**; Heckman et al. (2011) **[B]**; PART (OMB) **[B]**; Teymourifar (2026) **[B]**.
6. **Exact gap:** no automated assessment that an indicator's operational definition can support the construct it claims to measure.
7. **Contribution:** a validity rubric operationalised against program documents + indicator definitions, with measured agreement to expert audit judgement.
8. **System:** document-grounded indicator analyser producing construct-validity, gaming-exposure and denominator-stability flags.
9. **Data required:** program performance frameworks and indicator definitions (public).
10. **Ground truth:** expert auditor ratings — the blocker.
11. **Evaluation:** agreement with expert ratings; flag precision.
12. **Primary metric:** agreement (κ) with expert adjudication.
13. **Baselines:** the PART criteria applied manually; an LLM rubric prompt.
14. **Models:** available models.
15. **Compute:** low.
16. **Reproducibility:** medium (depends on expert labels).
17. **Reviewer objection:** "This is the PART framework or a measurement-theory checklist implemented as a prompt; the contribution is a rubric, and the validation requires expert annotation you cannot obtain at scale."
18. **Falsification:** if expert agreement is at chance or if a plain rubric prompt matches the system, there is no mechanism.
19. **Novelty confidence:** low.
20. **Feasibility:** medium-low (annotation).

---

### C-PA3 — Fair Peer Benchmarking for Cross-Agency Efficiency Comparison

1. **Title:** Comparable Units: Adjusting Cross-Agency Efficiency Benchmarks for Structural Difference
2. **Problem:** performance audit compares agencies/programs whose operating environments differ structurally; naive benchmarking attributes environmental difference to managerial performance.
3. **Why it matters:** benchmarking and cross-agency comparison are standard performance-audit procedures, and misattribution produces unfair findings.
4. **SOTA:** DEA since Charnes-Cooper-Rhodes (1981); DEA+ML "first review… covering **3 decades**… 1996 to 2025" (Kehinde 2026) **[B]**; a 2026 dissertation applying DEA to agency IT-investment efficiency **[B]**.
5. **Closest 5:** Kehinde et al. (2026) **[B]**; Charnes et al. (1981) **[B]**; Soffan et al. (2025) DEA+ML **[B]**; Guevel et al. (2025) DEA benchmarking **[B]**; a 2026 DEA agency-efficiency dissertation **[B]**.
6. **Exact gap:** none identified: environmental adjustment is the central subject of the DEA/StoNED/SFA literature.
7. **Contribution:** would duplicate three decades of work.
11. **Evaluation:** DEA-family comparisons.
17. **Reviewer objection:** "Cross-agency efficiency benchmarking with environmental adjustment is a 45-year-old field with a 2026 review; there is no gap here, only a new application domain."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-PA3).**

---

### C-EV1 — Evidence Sufficiency Scoring for Performance Findings

1. **Title:** Enough to Conclude? Machine-Assisted Sufficiency Assessment for Performance-Audit Findings
2. **Problem:** "sufficient appropriate evidence" is a standard requirement with no algorithm for the heterogeneous, largely non-statistical evidence performance audit uses.
3. **Why it matters:** it is the single most load-bearing judgement in a performance audit.
4. **SOTA:** **IntelliAudit** (arXiv:2608.07688) — retrieval-grounded multi-agent evidence evaluation built on "evidentiary sufficiency", producing missing-evidence analysis and challenging findings, validated by expert auditors on ISO 27001 **[A]**; standards define the concept without a calculus (GAO GAS 2024; ISA 500; AS 1105) **[B]**.
5. **Closest 5:** IntelliAudit **[A]**; GAO GAS 2024 **[B]**; ISA 500 **[B]**; AS 1105 **[B]**; ReAgent (Phase 9) **[A]**.
6. **Exact gap:** IntelliAudit targets **IT control** evidence in **simulated** organisations on a **certification** question; the performance-audit variant would need a sufficiency calculus for argumentative, non-statistical evidence about value for money.
7. **Contribution:** a sufficiency calculus + a scoring system validated against expert judgement.
8. **System:** evidence graph builder + sufficiency scorer + gap explainer.
9. **Data required:** performance audit reports and their working-paper evidence — **largely confidential**.
10. **Ground truth:** expert sufficiency labels — **expensive, and on confidential material**.
11. **Evaluation:** agreement with expert labels; the brief's Part P excludes this profile.
12. **Primary metric:** agreement with expert sufficiency rating.
13. **Baselines:** IntelliAudit-style retrieval+challenge; LLM rubric.
14. **Models:** available models.
15. **Compute:** low.
16. **Reproducibility:** low (confidential ground truth).
17. **Reviewer objection:** "IntelliAudit already demonstrates sufficiency-driven evidence evaluation with expert validation; your differentiation reduces to a different evidence type, and your validation is not reproducible because the ground truth is confidential."
18. **Falsification:** if a rubric prompt achieves the same agreement, no mechanism exists.
19. **Novelty confidence:** low.
20. **Feasibility:** low.

---

### C-EV2 — Computational Audit Trail for Findings (finding → evidence → data → code → execution)

1. **Title:** Executable Findings: A Reproducible Evidence Chain for Performance-Audit Conclusions
2. **Problem:** a performance finding cannot be independently reproduced by a third party; the analysis behind it is not executable.
3. **Why it matters:** it is the precondition for external review and for follow-up audits.
4. **SOTA:** **Chain-of-Evidence** (ScientistOne, arXiv:2605.26340) **[B]**; **ReAgent** (arXiv:2609.22111) **[A]**; Xu et al. large-scale AI-assisted replication (2026) **[B]**; ECA methodology platform **[B]**.
5. **Closest 5:** ScientistOne/CoE **[B]**; ReAgent **[A]**; Xu et al. **[B]**; AI4Reproducibility **[B]**; ECA AWARE **[B]**.
6. **Exact gap:** none — the chain exists for research claims and the linkage discipline exists in audit practice.
7. **Contribution:** would be an audit-domain transfer.
17. **Reviewer objection:** "Chain-of-Evidence and ReAgent already provide claim→evidence→execution traceability; the audit setting supplies different documents, not a new technical problem. The brief tells you to reject generic provenance and to reject the same chain relabelled."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-EV2).**

---

### C-EV3 — Cross-Source Contradiction Detection for Performance Reporting

1. **Title:** Reading the Reports Together: Detecting Cross-Source Contradiction in Government Performance Reporting
2. **Problem:** totals, KPIs, denominators and period definitions disagree across administrative data, budget documents, annual reports and policy documents; contradictions signal either error or concealment.
3. **Why it matters:** reconciling these sources is a core audit procedure and a large share of fieldwork.
4. **SOTA:** SEC-FINTABLES (logical inconsistency in financial tables, four sub-tasks) **[B]**; FinVerBench (validity/calibration) **[B]**; FinLongDocQA (>129k-token multi-document numerical reasoning) **[B]**; FinStructBench (extract/aggregate/reason) **[B]**; LOGICONBENCH (ICLR 2026) **[B]**.
5. **Closest 5:** all five above **[B]**.
6. **Exact gap:** the financial analogue covers each mechanistic case (period, aggregation level, totals, long context); the residual is *definition* change, which Part H shows is handled by metadata convention plus break detection.
7. **Contribution:** a government-document contradiction benchmark + detector.
17. **Reviewer objection:** "This is SEC-FINTABLES and FinStructBench moved to government PDFs. The brief forbids treating a new dataset as novelty and forbids another benchmark-validity paper."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-EV3).**

---

### C-CE1 — Certified Identification Strategies for Audit Causal Claims

1. **Title:** Assumptions You Can Check: Machine-Verifiable Identification for Causal Claims in Performance Audit
2. **Problem:** a performance finding that attributes an outcome to a program rests on untested identification assumptions.
3. **Why it matters:** causal attribution is the audit conclusion most likely to be wrong and most consequential.
4. **SOTA:** Mining Causality (LLM IV search) **[B]**; CauSciBench (367 tasks, 100+ papers, 9 disciplines) **[B]**; NBER w35588 (DiD/IV/RD/panel tasks; 74.4%→95.7% with agency) **[B]**; epidemiology causal-inference agent **[B]**; Causal-LLM **[B]**; CF-RAG's "Correlation Trap" **[B]**; sensitivity-analysis-with-bounds literature **[B]**.
5. **Closest 5:** Han et al. Mining Causality **[B]**; Acharya et al. CauSciBench **[B]**; Galiani et al. NBER w35588 **[B]**; CF-RAG **[B]**; arXiv:2506.00856 Can AI Master Econometrics **[B]**.
6. **Exact gap:** the residual is attaching *machine-checkable assumption certificates* (pre-trend tests, manipulation tests, sensitivity bounds) to each claim so a reviewer can verify them without re-running the analysis — but each certificate type already exists as standard econometric practice, and Phase 8's CAGE (arXiv:2607.29190) already demonstrates **certified authorization** with a *proof* that per-channel certification does not compose.
7. **Contribution:** an audit-finding object carrying executable assumption checks.
8. **System:** identification-selector + assumption-check generator + refusal on failed checks.
9. **Data required:** public program data with evaluable designs.
10. **Ground truth:** designer-intent labels for simulated interventions; published evaluations for real programs.
11. **Evaluation:** fraction of claims with passing certificates vs a baseline agent.
12. **Primary metric:** checkable-claim rate at fixed false-certificate rate.
13. **Baselines:** direct LLM causal analysis; design-agnostic DiD.
14. **Models:** available models (econometric checks are deterministic Python).
15. **Compute:** low.
16. **Reproducibility:** high.
17. **Reviewer objection:** "CauSciBench and NBER w35588 already benchmark causal/econometric agent performance; pre-trend and manipulation tests and sensitivity bounds are textbook. Wrapping them as 'certificates' is an interface, and CAGE already showed what a real certificate looks like."
18. **Falsification:** if agents already emit passing assumption checks at high rates, the certificate adds nothing.
19. **Novelty confidence:** low-moderate.
20. **Feasibility:** high.

---

### C-CE2 — Counterfactual Attribution for Public Programs

1. **Title:** Improved, or Caused? Counterfactual Attribution for Public-Program Performance Claims
2. **Problem:** audits frequently observe improvement and must decide whether the program caused it.
3. **Why it matters:** this is the effectiveness question in its purest form.
4. **SOTA:** the identification literature (DiD, RD, IV, synthetic control, matching); automation per §Part F; CF-RAG names the correlation-vs-causal-evidence discrimination; Causal Agent Replay performs do-operation attribution for agent runs.
5. **Closest 5:** CF-RAG **[B]**; Causal Agent Replay (arXiv:2606.08275) **[B]**; Executable Counterfactuals (ICLR 2026) **[B]**; CauSciBench **[B]**; Mining Causality **[B]**.
6. **Exact gap:** none — counterfactual attribution *is* program evaluation, a mature field now served by agents.
17. **Reviewer objection:** "Program-effect attribution is the central problem of a 50-year-old evaluation literature, and 2025–2026 work has already automated the estimation and named the correlation trap."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-CE2).**

---

### C-CE3 — Assumption-Falsification Agent for Quasi-Experimental Audit Designs

1. **Title:** Try to Break It: Automated Falsification Testing for Quasi-Experimental Audit Designs
2. **Problem:** designs are adopted and then reported without the falsification tests that would expose them.
3. **Why it matters:** an unfalsified design is a guess with numbers attached.
4. **SOTA:** pre-trend, manipulation, placebo and sensitivity analyses are standard econometric practice; Roth/Rambachan-Roth-style sensitivity with interpretable bounds is published; CauSciBench and NBER w35588 benchmark agent capability.
5. **Closest 5:** CauSciBench **[B]**; NBER w35588 **[B]**; Mining Causality **[B]**; Causal-LLM **[B]**; Archambault-adjacent sensitivity literature **[B]**.
6. **Exact gap:** none at the method level; the residual is automatic *selection* of the right falsification suite, which is the same residual as C-CE1.
17. **Reviewer objection:** "This is C-CE1 with a different name, and both reduce to orchestrating textbook diagnostics."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-CE3).**

---

### C-QA1 — Devil's Advocate Agent Against an Audit Finding

1. **Title:** Adversarial Review of Performance Findings: Can an Agent Falsify an Auditor's Conclusion?
2. **Problem:** findings are reviewed for procedural compliance, not for whether the inference survives an adversarial attack.
3. **Why it matters:** an independent challenger is the cheapest available error-detection mechanism.
4. **SOTA:** **IntelliAudit** — "challenges adverse findings, adjudicates disagreements" **[A]**; **ARCADE** — "a dedicated critic agent systematically challenges the analytical agent's scores and reasoning through structured debate" **[B]**; **the-adversary** — released harness that "makes an independent verifier **reproduce every finding against your artifact**" **[B]**; adversarial self-critique underwriting (arXiv:2602.13213) **[B]**.
5. **Closest 5:** IntelliAudit **[A]**; ARCADE **[B]**; the-adversary **[B]**; arXiv:2602.13213 **[B]**; ReAgent **[A]**.
6. **Exact gap:** none — three independent occupants, one open source.
7. **Contribution:** would be a fourth adversarial-review harness.
17. **Reviewer objection:** "IntelliAudit already challenges findings and validates with expert auditors; the-adversary already releases a finding-reproduction harness. Your contribution is a re-implementation for a new document type."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-QA1).**

---

### C-QA2 — Pre-Publication Detection of Unsupportable Findings

1. **Title:** Before It Is Published: Detecting Analytically Weak Performance Findings
2. **Problem:** weakly supported findings are published and then drive real resource decisions.
3. **Why it matters:** findings have consequences and are hard to retract.
4. **SOTA:** ReAgent's dynamic audit catches "experiments that reproduce reported numbers while **deviating from the claimed methodology**" **[A]**; IntelliAudit's missing-evidence analysis and permissive-recommendation warnings **[A]**; the-adversary **[B]**; Proofreader **[B]**; specification-anchored audit **[B]**.
5. **Closest 5:** ReAgent **[A]**; IntelliAudit **[A]**; the-adversary **[B]**; arXiv:2604.26495 **[B]**; Proofreader **[B]**.
6. **Exact gap:** none.
17. **Reviewer objection:** "ReAgent is precisely pre-publication detection of unsupported claims against artefacts, benchmarked, and reports the hard case you would target."
19. **Novelty confidence:** very low.
20. **Feasibility:** high.
**Kill: CLOSED (see M-QA2).**

---

### C-QA3 — Measured Division of Labour: Does an Adversarial AI Change Auditor Conclusions?

1. **Title:** Whose Judgement? Measuring Whether Adversarial AI Review Changes Auditor Conclusions — and Improves Them
2. **Problem:** the value of AI challenge depends on whether it changes expert conclusions in the right direction, or merely adds noise or anchoring.
3. **Why it matters:** this is the only question here with a natural, obtainable ground truth — whether a raised objection is judged *valid* by independent experts.
4. **SOTA:** NBER w35720 "**Does AI Assistance Enhance or Erode Expertise?**" (Autor et al. 2026) **[B]**; audit-judgement and automation-bias accounting literature **[B]**; ARCADE and IntelliAudit report critique *mechanisms* but not measured *conclusion change* **[A/B]**; IntelliAudit's own limitation is that oversight matters for "calibrating sufficiency judgments" **[A]**.
5. **Closest 5:** Autor et al. NBER w35720 **[B]**; IntelliAudit **[A]**; ARCADE **[B]**; the-adversary **[B]**; arXiv:2602.13213 **[B]**.
6. **Exact gap:** *claimed* — no measured effect of adversarial AI review on expert audit conclusions, with validity of objections adjudicated by independent experts.
7. **Contribution:** a within-subject study measuring whether adversarial AI review shifts expert conclusions, and whether shifted conclusions are better or worse by independent adjudication.
8. **System:** adversarial reviewer producing structured objections with evidence citations; a blinded adjudication protocol.
9. **Data required:** realistic performance findings with seeded defects, built from public reports.
10. **Ground truth:** seeded-defect labels (known by construction); plus independent expert adjudication of every objection's validity.
11. **Evaluation:** conclusion-change rate; objection validity rate; net improvement over control review.
12. **Primary metric:** valid-objection rate and net conclusion correction.
13. **Baselines:** no-AI review; generic LLM critique; a checklist-based reviewer.
14. **Models:** available models (adequate for critique generation).
15. **Compute:** low.
16. **Reproducibility:** medium-high (public source reports; synthetic-but-realistic findings).
17. **Reviewer objection:** "This is a human-factors study, not a technical contribution; it measures a phenomenon already implied by Autor et al. on expertise erosion and by the automation-bias literature; and 'AI changes human conclusions' is not a new scientific result. It also needs expert participants, so it is closer to a CHI/IS study than to a methods contribution."
18. **Falsification:** if adversarial review never changes expert conclusions, or changes them at chance validity, the mechanism is inert.
19. **Novelty confidence:** low-moderate.
20. **Feasibility:** medium (recruiting auditors; no confidential records needed if findings are synthesised from public reports).
**Kill: MAJOR MODIFICATION — not a survivor (see M-QA3).**

---

## Part O — Hostile literature audit

Each candidate was searched for: identical paper, equivalent paper, 2024/2025/2026 successor, thesis, government research, major audit-organisation work, commercial system, open-source system.

| # | Candidate | Verdict | Killing evidence |
|---|---|---|---|
| M-PA1 | Measurement-change attribution | **MAJOR MODIFICATION** | Breaks: mature change-point/structural-break detection (2026 *JRSS/JTSA* special issue on "data segmentation in time series, structural breaks and real-time monitoring") **[B]**. Attribution to measurement change: **official statistics already mandates it** — SDMX: "**Time series breaks can be explained by changes to classifications, methodology, survey scope, data sources**"; FAO: where retrospective revision is impossible, "the resulting **lack of comparability should be** [flagged]" **[B]**. Manipulation: bunching/threshold estimators, Andarge et al. 2025 ("discontinuity-based and/or bunching estimators to detect manipulation"), Kleven's review, procurement-bunching work, and Li et al. (J-PART 2026) on manipulation in evaluation cycles **[B]**. Residual = orchestration + a corpus. **Not promoted:** orchestration is engineering and a corpus is excluded as novelty by the brief. |
| M-PA2 | Indicator validity auditor | **MAJOR MODIFICATION** | Measurement theory: Manheim & Garrabrant (2023) **[B]**; Fisher (*HDSR* 2021) **[B]**. Gaming identification: Heckman, Heinrich & Smith (2011) — identify gaming "by estimating the **correlation between a performance measure and the true goal**" **[B]**. Institutionalised manual instrument: **PART** ("a series of diagnostic questions used to assess and evaluate programs across a set of performance-related criteria, including program design") **[B]**. Recent: Teymourifar 2026 on sustaining indicator validity **[B]**; Li et al. J-PART 2026 **[B]**. Residual = a rubric + automation, with expert-annotation-dependent validation. **Not promoted.** |
| M-PA3 | Fair peer benchmarking | **CLOSED** | DEA since 1981 (Charnes et al., 2,800+ citations) **[B]**; **Kehinde et al. 2026**: "the **first review** … data envelopment analysis (DEA) and machine learning (ML), covering **3 decades** of scholarly works from 1996 to 2025" **[B]**; Soffan et al. 2025 (ML+DEA) **[B]**; Guevel et al. 2025 (DEA benchmarking) **[B]**; 2026 doctoral dissertation applying DEA to agency efficiency **[B]**. Environmental adjustment is the field's core subject. |
| M-EV1 | Evidence sufficiency scoring | **CLOSED (and resource-blocked)** | **IntelliAudit** (arXiv:2608.07688) is built on "**evidentiary sufficiency**", emits **missing-evidence analysis**, **challenges adverse findings**, and is validated with **expert auditor review** **[A]**. Standards already define the concept (GAO GAS 2024 "sufficient, appropriate evidence… significance, and audit risk form a framework"; ISA 500; AS 1105) **[B]**. The performance-audit variant needs confidential working papers + expert labels, which the brief's Part P excludes. |
| M-EV2 | Computational audit trail | **CLOSED** | **Chain-of-Evidence** (ScientistOne) — "every claim must trace, through a recorded evidence chain, to a grounding source" **[B]**; **ReAgent** — structured repository-level **audit report enabling transparent evidence traceability**, static + dynamic **[A]**; **Xu et al. 2026** AI-assisted full-paper replication **[B]**; ECA/AWARE establishes finding→evidence linkage as standard audit practice **[B]**. Brief explicitly: "If yes, reject generic provenance as a contribution." |
| M-EV3 | Cross-source contradiction | **CLOSED** | **SEC-FINTABLES** (ACL Findings 2026) — LLM detection of "**logical inconsistencies in financial tables**" with four sub-tasks **[B]**; **FinVerBench** (validity/calibration) **[B]**; **FinLongDocQA** — multi-document numerical reasoning, "annual reports often exceed **129k tokens**" **[B]**; **FinStructBench** — extract/**aggregate**/reason over structured financial data **[B]**; **LOGICONBENCH** (ICLR 2026) **[B]**; industry multi-document correlation frameworks **[B]**. Each hard case the brief lists maps to an occupied sub-task. |
| M-CE1 | Certified identification strategies | **MAJOR MODIFICATION** | **CauSciBench** benchmarks LLM causal reasoning on "**367 evaluation tasks** based on **100+ real-world research papers across 9 disciplines**" **[B]**; **NBER w35588** benchmarks agents on "difference-in-differences, regression [discontinuity], instrumental variables, panel estimators" **[B]**; **Mining Causality** does LLM-assisted IV search **[B]**; an **epidemiology causal-inference agent** exists **[B]**; **Causal-LLM** automates root-cause analysis **[B]**; **CF-RAG** names and addresses the correlation trap **[B]**. Pre-trend/manipulation/sensitivity tests are standard econometrics; Phase 8's **CAGE** already shows what a certification guarantee with a proof looks like. Residual = an interface over textbook diagnostics. **Not promoted.** |
| M-CE2 | Counterfactual attribution | **CLOSED** | Program-effect attribution *is* the identification literature (DiD/RD/IV/synthetic control) **[B]**, now automated (§Part F) **[B]**; **Causal Agent Replay** (arXiv:2606.08275) already performs do-operation attribution and measures outcome-distribution shift **[B]**; **Executable Counterfactuals** (ICLR 2026) operationalises abductive/interventional/predictive counterfactuals **[B]**. |
| M-CE3 | Assumption-falsification agent | **CLOSED** | Same residual as M-CE1; falsification testing is standard practice and the selection residual is not a new phenomenon. |
| M-QA1 | Devil's advocate agent | **CLOSED** | **IntelliAudit** "**challenges adverse findings, adjudicates disagreements**" **[A]**; **ARCADE** "a dedicated **critic agent** systematically challenges the analytical agent's scores and reasoning through **structured debate**" **[B]**; **the-adversary** — open-source harness that "finds what you missed before a reviewer does, then makes an independent verifier **reproduce every finding** against your artifact" **[B]**; **adversarial self-critique** in underwriting with an explicit "critic agent challenges the primary agent's conclusions before human review" **[B]**. |
| M-QA2 | Pre-publication weakness detection | **CLOSED** | **ReAgent** (Phase 9) performs pre-publication auditing of claims against artefacts and reports the hard case — "experiments that **reproduce reported numbers while deviating from the claimed methodology**" **[A]**; IntelliAudit flags missing evidence and warns of "overly permissive recommendations" **[A]**; the-adversary **[B]**; Proofreader **[B]**; specification-anchored audit (arXiv:2604.26495) **[B]**. |
| M-QA3 | Measured division of labour | **MAJOR MODIFICATION** | **NBER w35720** "**Does AI Assistance Enhance or Erode Expertise?**" (Autor et al. 2026) already studies the expertise effect **[B]**; audit-judgement/automation-bias literature exists in accounting **[B]**; **IntelliAudit's** stated limitation is exactly "the importance of human oversight for **calibrating sufficiency judgments** and correcting overly permissive recommendations" **[A]**. Residual = a measurement of conclusion drift with adjudicated objection validity — a human-factors study rather than a technical contribution, and it needs expert participants. **Not promoted.** |
| M-ADJ | *All 12* — marketing-material check | — | Commercial audit-analytics and "AI audit tool" vendors publish **no** validation, ground truth, or metrics (Vero AI, DataSnipper-class, AuditBoard-class, Kognitos, Aurascure, Sweet Security). **[INFER]** So although the *market* is crowded, none of it constitutes prior scientific work — which means it neither blocks nor supports a candidate. |

**Part O result: 7 CLOSED, 5 MAJOR MODIFICATION, 0 OPEN.**

---

## Part P — Resource audit

Constraints: limited GPU; API access to DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4; Python/pandas/scikit-learn/statsmodels; Docker; GitHub; public datasets. Excluded: proprietary government data, unavailable audit records, expensive frontier models, massive annotation budgets, H100/H200, confidential datasets.

| Candidate | Passes Part P? | Binding issue |
|---|---|---|
| C-PA1 | Yes | public series + metadata; no GPU |
| C-PA2 | **No** | expert-annotated indicator-validity labels at scale |
| C-PA3 | Yes | but closed on novelty |
| C-EV1 | **No** | confidential working papers; expert sufficiency labels |
| C-EV2 | Yes | but closed on novelty |
| C-EV3 | Yes | but closed on novelty |
| C-CE1 | Yes | public data + deterministic econometric checks |
| C-CE2, C-CE3 | Yes | but closed on novelty |
| C-QA1, C-QA2 | Yes | but closed on novelty |
| C-QA3 | **Borderline** | needs expert auditor participants; possible with synthesised findings but not cheap |

**[INFER]** Part P does not produce the NO-GO — novelty does — but note that **the two candidates with the most interesting residual (C-PA2 indicator validity, C-EV1 sufficiency scoring) both fail Part P**, because each needs a costly, non-public expert-labelled ground truth. That combination — *interesting but unevaluable* — is the structural reason this domain yields no survivor.

---

## Part Q — Scientific contribution test

Template: "We discover/show that ___ / We develop ___ / We evaluate it against ___ / We demonstrate ___ / We release ___."

| Candidate | Result | Verdict |
|---|---|---|
| C-PA1 | show that trend breaks can be attributed to documented measurement changes / develop an attribution pipeline / evaluate against break-only baselines / demonstrate attribution accuracy / release a labelled corpus | **Application + dataset** — reject |
| C-PA2 | show that indicators are often construct-invalid (known: Heckman, Fisher, Manheim) / develop a rubric / evaluate against expert agreement / demonstrate agreement / release a rubric | **Rubric** — reject |
| C-PA3 | — | **Duplicate** — reject |
| C-EV1 | show that sufficiency judgement can be partially automated (**IntelliAudit**) | **Duplicate** — reject |
| C-EV2 | show that findings can be evidence-linked (**CoE, ReAgent, ECA AWARE**) | **Duplicate** — reject |
| C-EV3 | show that documents contradict each other (**SEC-FINTABLES**) | **Duplicate** — reject |
| C-CE1 | show that identification assumptions can be checked automatically (textbook) / develop a certificate wrapper / evaluate against a baseline agent / demonstrate check rates / release the wrapper | **Interface over existing diagnostics** — reject |
| C-CE2 | show that attribution requires identification (**mature field**) | **Duplicate** — reject |
| C-CE3 | — | **Duplicate** — reject |
| C-QA1 | show that an adversary finds weaker findings (**three occupants**) | **Duplicate** — reject |
| C-QA2 | show that unsupported findings are detectable (**ReAgent**) | **Duplicate** — reject |
| C-QA3 | show that adversarial AI review changes expert conclusions / develop a review protocol / evaluate against control review / demonstrate net correction / release the protocol | **Human-factors measurement, not a technical contribution** — reject |

**[INFER]** Not one candidate produces the sanctioned form: *"We introduce a new method/system that addresses a previously unstudied technical problem in performance-audit analytics and demonstrate measurable improvement against established baselines."* Every one either duplicates an occupant or is an application, rubric, wrapper or measurement of an existing phenomenon.

---

## Part R — Dataset / benchmark test

| Candidate needing data | Existing dataset sufficient? | Transform legitimately? | New dataset necessary? | Assessment |
|---|---|---|---|---|
| C-PA1 | partly — public agency performance series exist | yes (pair series with their public metadata/revision notes) | yes, a break-attribution corpus | Annotation protocol: documented changes are objective (metadata) → high agreement expected. **Privacy: none. Public release: feasible.** But the brief says a new dataset is **not sufficient novelty**, and this one carries no method contribution. |
| C-PA2 | no | — | yes, expert validity ratings | Multi-rater protocol needed; κ required; experts scarce. **Not feasible at scale.** |
| C-EV1 | no | — | yes, sufficiency labels on working papers | **Confidential material; excluded by Part P.** |
| C-EV3 | analogous financial datasets exist (SEC-FINTABLES, FinStructBench) | yes | yes, a government-document set | Public; feasible. But it is a benchmark, and the brief forbids benchmark-novelty and benchmark-validity framing. |
| C-CE1/C-CE3 | yes — public program data with evaluable designs; CauSciBench-style task construction | yes | no | Ground truth = designer intent for simulated interventions + published evaluations. Feasible. |
| C-QA3 | no | yes (synthesise realistic findings with seeded defects from public reports) | yes | Ground truth = seeded defects + independent expert adjudication of objections. Feasible but participant-dependent. |

**[INFER] Part R conclusion.** Data is available; **ground truth is the binding constraint**. Only the candidates whose truth is *objective by construction* (seeded defects, documented metadata changes, designer-intent interventions) are evaluable — and those are exactly the candidates that duplicate existing work.

---

## Part S — Potential research artifacts

| Candidate | Artifact | Would it support a contribution? |
|---|---|---|
| C-PA1 | `series-attribution` — break attribution with document grounding | supports a dataset/orchestration paper only |
| C-PA2 | `indicator-validity` — construct-validity rubric engine | supports a rubric automation, not a contribution |
| C-EV1 | sufficiency scorer + evidence graph | supports a duplicate of IntelliAudit |
| C-EV2 | audit evidence-chain recorder | supports a duplicate of CoE/ReAgent |
| C-EV3 | `govdoc-contradiction` benchmark + detector | benchmark-only |
| C-CE1/C-CE3 | `assumption-checks` certificate generator | certificate interface over textbook diagnostics |
| C-QA1/Q2 | adversarial finding reviewer | duplicate of the-adversary / ARCADE / IntelliAudit |
| C-QA3 | review-effect measurement protocol + toolkit | human-factors protocol |
| — | **`audit-ai-saturation-map`** — the corpus of this phase, mapped to lifecycle stage and occupant | **the only artefact this phase can genuinely claim, and it is a survey, which the brief excludes** |

Per the brief, the software must support the contribution rather than *be* it. **No survivor, so no recommended artifact.**

---

## Part T — Publication potential (near-misses only; no acceptance prediction)

* **C-CE1 (certified identification for audit claims).** Communities: Auditing/Accounting, Information Systems, Data Science, Government Analytics. Paper type: methods + benchmark. Evidence required: checkable certificates on real audit-style causal questions, with a false-certificate rate and an ablation against a design-agnostic baseline; ideally audit-practitioner review. Likely reviewers: econometricians plus audit academics. **Main threat to validity:** the diagnostic tests are textbook, the benchmark analogues exist (CauSciBench, NBER w35588), and the certificate framing invites comparison with CAGE.
* **C-QA3 (measured effect of adversarial review).** Communities: Information Systems, Accounting/Auditing (behavioural), CHI, Public Administration. Paper type: behavioural study. Evidence required: a within-subject design with practising auditors, an adjudicated objection-validity measure, and a control condition. **Main threat:** Autor et al. (2026) already studies AI assistance and expertise; the contribution would be read as a domain replication.
* **C-EV1 (performance-audit sufficiency calculus).** Communities: Auditing, Accounting, Information Systems. Paper type: framework + validation. Evidence required: a formal calculus plus agreement with expert sufficiency judgements on real findings. **Main threat:** confidential ground truth makes the paper unreproducible, and IntelliAudit already occupies the sufficiency framing with expert validation.

---

## Part U — Final survivors

# NO SURVIVORS

Zero candidates are promoted. Seven are CLOSED by primary sources; five are MAJOR MODIFICATION; none satisfies the brief's bar of "a new method/system addressing a previously unstudied technical problem in performance-audit analytics with measurable improvement against established baselines."

**Why this is the correct verdict, stated precisely.** Phase 10's domain emptiness is real but *explanatory*, not opportunistic:

1. **The technical sub-problems of performance auditing are already solved in better-instrumented adjacent fields.** Evidence sufficiency → IT audit (**IntelliAudit**, expert-validated). Adversarial challenge → critique architectures (**ARCADE**, **the-adversary**). Causal identification → econometrics automation (**Mining Causality**, **CauSciBench**, **NBER w35588**, an epidemiology causal agent, **Causal-LLM**). Cross-source numeric consistency → financial-document benchmarks (**SEC-FINTABLES**, **FinVerBench**, **FinLongDocQA**, **FinStructBench**, **LOGICONBENCH**). Indicator gaming → **Heckman's identification method**, bunching estimators, and **Li et al. (J-PART 2026)**. Efficiency benchmarking → **DEA** with a 2026 review of three decades of DEA×ML. Measurement-change detection → structural-break detection plus **SDMX/FAO comparability conventions**.

2. **The stages that are genuinely unoccupied are judgement stages with no ground truth.** Criteria development and audit-question formulation have no technical literature — because there is no oracle against which an intervention can be evaluated, and the brief excludes confidential working papers, unavailable audit records, and massive annotation budgets.

3. **The brief's exclusion list removes the remaining escape routes.** Generic provenance (Part J), generic reproducibility (Part J), generic "AI auditor", generic report generation, RAG, explainability-only, dataset-only, benchmark-only, and "human in the loop" are all excluded — and each is precisely where a performance-audit-relabelled version would land.

4. **The one residual with real intellectual content is unevaluable.** A quantitative sufficiency calculus for heterogeneous non-statistical performance-audit evidence (E.7-residual) is the only genuinely understudied technical problem identified. It is blocked twice: expert-annotated sufficiency labels on confidential material (Part P), and a plausible reviewer classification as an adaptation of audit sampling theory rather than a new phenomenon.

**The single honest, defensible observation this phase produced** is structural rather than opportunistic: *performance auditing has no ground-truth oracle, and that — not neglect, and not data availability — is why it has no technical AI research literature.* Public data is abundant (Part M: USASpending-class records, GovInfo, PART ratings, GAO/ECA/World Bank corpora, and an emerging OpenAudit-style report-to-dataset project). The scarcity is in **labelled correctness of findings**, which is why every evaluable candidate here had to import its truth from an adjacent field — and every adjacent field is already occupied.

---

## Part V — Source registry and artifacts

### V.1 New sources registered in Phase 10

`research/tables/sources.csv` extended from **R165 → R199** (34 new rows).

**Label A (fetched and read at source):** R169 **IntelliAudit** (arXiv:2608.07688) — abstract and full quoted claims read at source.

**Label B (snippet, listing, or another work's summary — do not quote figures):**
R166 OECD *The state of artificial intelligence in public audit* (2026-05) · R167 Genaro-Moya et al. (*MDPI Admin. Sci.* 6(2):78, 2025) · R168 Mdhlalose, *Scaling AI in Public Audit Institutions* (econstor 2026) · R170 Mining Causality (arXiv:2409.14202) · R171 CauSciBench (Acharya et al. 2025) · R172 Galiani et al., NBER w35588 (2026) · R173 Can AI Master Econometrics (arXiv:2506.00856) · R174 Afonso et al., NBER w35188 · R175 Autor et al., NBER w35720 · R176 AI Agent for Automated Causal Inference in Epidemiology (medRxiv 2026) · R177 Causal-LLM (ACM DOI 10.1145/3801228.3801315) · R178 CF-RAG / Correlation Trap (OpenReview 9U51rOnGko) · R179 Causal Agent Replay (arXiv:2606.08275) · R180 Executable Counterfactuals (ICLR 2026, OpenReview Lm46gJA0q8) · R181 Xu et al., AI-assisted large-scale replication (2026) · R182 SEC-FINTABLES (ACL Findings 2026) · R183 FinVerBench (arXiv:2605.29586) · R184 FinLongDocQA (arXiv:2604.03664) · R185 FinStructBench (SSRN 6506403) · R186 LOGICONBENCH (ICLR 2026) · R187 ARCADE (medRxiv 2025.12.21.25342744) · R188 the-adversary (GitHub, 2026-03) · R189 Adversarial Self-Critique underwriting (arXiv:2602.13213) · R190 Heckman, Heinrich & Smith, *Measuring Government Performance* (2011) · R191 Li et al., *J-PART* (2026) · R192 Andarge et al., threshold manipulation (2025) · R193 Kleven, Bunching (*Annual Review of Economics*) · R194 Kehinde et al., DEA×ML review (2026) · R195 Teymourifar (2026) KPI validity · R196 Manheim & Garrabrant (2023) · R197 Fisher (*HDSR* 2021) · R198 Agent Benchmarks Fail Public Sector Requirements (arXiv:2601.20617) · R199 CitizenQuery-UK (ODI, 2026-02-05)

**Standards and institutional references used as context (not counted as citable research sources):** GAO *Government Auditing Standards* 2024 revision; PCAOB AS 1105; ISA 500; ECA methodology guide and AWARE platform; SDMX glossary (time-series breaks); FAO statistical standard series; OMB **PART**; INTOSAI Journal (2026-06); KPMG SAI brief (2026-02); World Bank *The Quality of Audits by SAIs*; GAO Innovation Lab and GAO-24-107237; OECD *AI in policy evaluation* (2025). All **[B]**; none is citable as a figure.

**Explicitly excluded as scientific evidence:** commercial audit/AI-audit tooling (Vero AI, DataSnipper-class, AuditBoard-class, Kognitos, Aurascure, Sweet Security, Trustle, Vanta-class); market-research reports; vendor "state of AI in audit" surveys.

**Carry-forward cautions:** the frequently repeated claim that automated systems produced "1,000 program-evaluation papers using DiD/IV" is **secondary reporting only — do not cite as a number**. The insurance self-critique figures (11.3%→3.8%, 92%→96%) appear only in third-party coverage — **do not cite**. Never cite a label-B figure.

### V.2 Artifacts created/updated in Phase 10

* **Created:** `research/10-performance-audit-ai-opportunity-map.md` (this file)
* **Created:** `research/tables/performance-audit-opportunity-matrix.csv` (19 fields as specified in Part V)
* **Updated:** `research/tables/sources.csv` (R166–R199 appended; existing 11-field schema preserved)
* **Validated:** both CSVs parsed with the standard inline node RFC4180 parser — header width, row count, `unterminatedQuote`, malformed rows, duplicate IDs.

### V.3 Domain note for the project (not a research topic)

**[INFER]** The user's performance-audit domain expertise is real and was useful here — it is what allowed the reduction table at §0.1 to be built quickly and what made the *ground-truth* obstruction visible. But the brief's instruction that expertise must not be treated as evidence of novelty was correct: the domain advantage produced **no** surviving research problem, and the phase's most valuable output is a negative result — a stage-by-stage map of where performance-audit AI work is *possible* versus where it is *evaluable*.

---

## Verdict summary

| Part | Result |
|---|---|
| A — Lifecycle | 20 stages mapped; 11 occupied, 5 handled elsewhere, 3 excluded, 2 unoccupied-but-unevaluable (criteria development, audit-question formulation) |
| B — Literature | Public-sector AI-in-audit work is institutional/conceptual and mostly non-citable; technical work is financial/IT audit |
| C — Systems | 12 system classes mapped; one (IntelliAudit) touches the brief's Parts G/K/L |
| D — Performance vs financial | Performance-specific concepts (implementation, service delivery, value-for-money integration) uncovered — but for construct/ground-truth reasons |
| E — Hard analytical problems | 6 of 7 CLOSED; 1 (indicator validity) MAJOR MODIFICATION |
| F — Causal inference | **CLOSED** (Mining Causality, CauSciBench, NBER w35588, epidemiology agent, Causal-LLM, CF-RAG) |
| G — Evidence sufficiency | **CLOSED** (IntelliAudit) + residual with no obtainable ground truth |
| H — Data quality / measurement change | **MAJOR MODIFICATION** (breaks + SDMX/FAO conventions + bunching + J-PART 2026) |
| I — Cross-source contradiction | **CLOSED** (SEC-FINTABLES, FinVerBench, FinLongDocQA, FinStructBench, LOGICONBENCH) |
| J — Audit trail | **CLOSED** (Chain-of-Evidence, ReAgent, Xu et al., ECA AWARE) |
| K — Human–AI | **CLOSED** (IntelliAudit, ARCADE, the-adversary, NBER w35720) |
| L — Quality assurance | **CLOSED** (same occupants) |
| M — Public data | **Available** — feasibility is not the constraint |
| N — Candidates | 12 generated across the 4 required clusters |
| O — Hostile kills | 7 CLOSED, 5 MAJOR MODIFICATION, 0 OPEN |
| P — Resource audit | 3 candidates fail; **the two most interesting residuals (indicator validity, sufficiency scoring) both fail** |
| Q — Contribution test | All 12 fail or duplicate |
| R — Dataset test | Ground truth is the binding constraint, not data |
| S — Artifacts | Identified, none recommended |
| T — Publication | Assessed for 3 near-misses; no venue plan |
| U — Survivors | **NO SURVIVORS** |

PHASE 10 COMPLETE — SURVIVORS: 0
