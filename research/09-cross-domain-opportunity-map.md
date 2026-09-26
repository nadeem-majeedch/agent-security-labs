# 09 — Cross-Domain Research Opportunity Map (Phase 9)

**Status: PHASE 9 COMPLETE — SURVIVORS: 0 → NO SURVIVORS**

**Date of audit:** 25 September 2026
**Strategic shift:** stop asking "what agent-security problem is unsolved?" and ask "what scientific/engineering problem can be solved *using* AI agents as the instrument?" — in data science, ML, software engineering, scientific computing, research reproducibility, data-analysis verification, computational auditing, and executable evidence.
**Standing constraints (unchanged):** do not fabricate citations/numbers/DOIs/URLs; primary sources only; prefer NO-GO over manufactured novelty; mark unverified claims; do not write paper prose; do not implement the system; do not commit/push; do not fabricate novelty; do not use marketing material as primary scientific evidence; every claimed gap must be supported by primary literature.

---

## Part 0 — Method, labels, and the headline finding

| Label | Meaning | Citable as a figure? |
|---|---|---|
| **A** | Fetched and read at the source (abstract or full text). | Yes, for what was read |
| **B** | Read only via a snippet, third-party listing, or another paper's summary. | **No** — never quote a number |
| **C** | Not verified at all. | No |

Claim tags: **[FACT]** verified at source · **[INFER]** derived from verified facts · **[HYP]** hypothesis · **[OPEN]** explicitly unresolved in the literature.

**Headline finding [INFER].** The cross-domain space is *more* crowded than the agent-security space audited in Phase 8, and for a structural reason: the natural units of contribution here (benchmark, auditing framework, verifier, evidence chain) are all *publishable in 2026 with a code release*, so every obvious framing already has a 2026 occupant with a released artifact. Specifically:

* The Part D proposal — "every analytical claim should be linked to executable evidence that independently verifies the claim" — is **already built and published as a named standard**: Google Research's **Chain-of-Evidence (CoE)** inside the **ScientistOne / Science One Framework**, "a verifiability standard requiring every claim to trace, through a recorded evidence chain, to a grounding source" (**R127**, arXiv:2605.26340) **[B]**. The Google Research blog for the same work states the motivating failures explicitly: "An unreproducible score does not reappear when the code is re-run. A misdescribed method claims one algorithm in the paper while the code implements another" **[B]**.
* The Part C proposal — audit agent-written research documents against their artifacts — is **already built and published** as **ReAgent** (**R128**, arXiv:2609.22111), which "introduce[s] **Claim-Code Consistency** as a new auditing problem for autonomous research" and performs **static + dynamic auditing** (executing experiments to collect evidence), reporting that combining both perspectives "identifies inconsistencies that may remain hidden under either perspective alone, such as **experiments that reproduce reported numbers while deviating from the claimed methodology**" **[A]**.
* The Part C/E proposal — locate *where* a run went wrong rather than whether it succeeded — is **already built** as **Traverse** (a 2,518-trajectory, 6,967-mistake, 78-failure-type human-verified benchmark) plus **Scout**, a trained 4B verifier (**R129**, arXiv:2609.17930) **[A]**.
* The Part B/statistics proposal — agentic multiplicity and p-hacking at machine scale — is **already measured with a released artifact**: **The Agentic Garden of Forking Paths** with **Agentic Bootstrap** and an Amazon Science repository (**R131**, arXiv:2607.01507) **[B]**.

**[INFER]** Any Phase-9 candidate in the four domains that matter most (analytics verification, reproducibility, SWE correctness, verifier trust) must therefore beat a 2026 artifact, not a gap. That is a materially harder bar than Phase 8's, and it is the reason the survivor count is zero.

---

## Part A — Map of the cross-domain space

Forty search topics were covered across seven probe rounds. Findings are grouped by the four domains the brief requires.

### A.1 Data science / analytics agents (topics 1–7, 22, 24)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **InfiAgent-DABench** | ICML 2024, arXiv:2401.05507 | B | "the first benchmark specifically designed to evaluate LLM-based agents in data analysis tasks"; CSV-centric end-to-end analysis |
| **DA-Code** | da-code-bench.github.io | B | code-generation benchmark for "agent-based data science tasks" |
| **DSBench** | ICLR 2025 (repo `liqiangjing/dsbench`) | B | "realistic data analysis and data modeling tasks collected from modeloff and [Kaggle]" |
| **DataSciBench** | ACL Findings 2026 | B | "a comprehensive benchmark for evaluating Large Language Models in data sci[ence]" |
| **AgenticDataBench** | arXiv:2607.01647 | B | newer comprehensive data-analysis-agent benchmark |
| **DABstep**, **FDABench**, **InsightBench** | surfaced in related searches | C | additional analytics-agent benchmarks; **not verified** |
| **NL2SQL-BUGs** | arXiv:2503.11984 | B | "the **first benchmark** designed for evaluating the capabilities of **NL2SQL semantic errors detection**", 2,018 expert-annotated items |
| **DataAiPrep** | *SoftwareX*, ScienceDirect S235271102600155X (2026) | B | data-quality platform with "a hierarchical, multi-layered **leakage detection** pipeline that combines **row-hash fingerprinting for train–test contamination**, cosine [similarity]" |
| **Automated Data Quality Validation in an End-to-End ML pipeline** | arXiv:2502.10667 | B | existing validation relies on metrics or expert constraints; "automated constraint generation methods … are often incomplete and may be too strict or too soft, causing false positives or missed [violations]" |
| **PyDataQuality** | GitHub + preprint (2026) | B | profiling + distribution-drift detection for production ML pipelines |

**[INFER]** Data-analysis-agent *evaluation* is saturated at the benchmark layer (at least six 2024–2026 benchmarks), and two of the specific failure classes named in the brief — semantic SQL errors and train-test leakage — already have purpose-built detection artifacts.

### A.2 Statistical reasoning and analysis multiplicity (topics 21, 22, 38–40)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **Fisher-R1 / P-Bench (P-value Bench)** | arXiv:2608.07437 | B | "a benchmark of **425 open-ended hypothesis-testing tasks built on real scientific data**" plus a trained agent for reliable hypothesis testing |
| **Classifying 25 misinterpretations of statistical tests** | ResearchGate, Sep 2026 | B | evaluates whether six LLMs "endorse or reproduce well documented interpretive errors" |
| **Evaluating the Accuracy of LLMs in [statistical test selection]** | PMC13419856 (Paolella 2026) | B | LLM ability to recommend appropriate statistical tests for research scenarios |
| **Evaluating the Accuracy and Explanatory Quality of LLMs in statistical test selection** | *Cureus* (Oct 2025) | B | prompts-to-model test selection |
| **The Agentic Garden of Forking Paths** | arXiv:2607.01507 (2026-07-01); code `amazon-science/agentic-forking-path` | B | introduces **Agentic Bootstrap**, which "estimates the m-value by using AI agents to systematically sample and log plausible analysis paths"; runs "autonomous AI data scientist agents on any dataset + hypothesis, then analyz[es] the resulting **multiverse**" |
| **Many AI Analysts, One Dataset: Navigating the Agentic Data Science Multiverse** | ResearchGate (Feb 2026) | B | "fully autonomous AI analysts built on large language models can reproduce a similar structured analytic [multiverse]" |
| **The garden of forking paths** | Gelman & Loken (2013) | — | the classical result being extended |

**[INFER]** Multiplicity inflation by autonomous analysts is not merely studied — it has a named estimator (**m-value** via Agentic Bootstrap) and a released codebase. This is the single most decisive closure in the analytics cluster.

### A.3 Scientific reproducibility and autonomous research (topics 8–11, 28, 29)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **ScientistOne / Science One Framework** | arXiv:2605.26340; research.google/pubs; Google Research blog | B | **Chain-of-Evidence**: "CoE defines what 'verifiable' means for a research claim: every claim must trace, through a recorded evidence chain, to a grounding source"; evidence chains built "at the time a claim is produced rather than attempting to reconstruct grounding after the fact" |
| **ReAgent** | arXiv:2609.22111 (2026-08-18) | A | static + dynamic auditing of agent-written research documents vs repositories; **Claim-Code Consistency**; structured repository-level audit report for "transparent evidence traceability" |
| **Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap** | ResearchGate (2026-06-29) | B | "code release is now common, but **reproducibility-grade and claim-verification artifacts remain much less common**" — the verification gap is already named and surveyed |
| **REPRO-Bench** | identifier not captured | B | "a new benchmark designed to evaluate whether AI agents can accurately assess the **computational reproducibility** of social science [research]" |
| **AI4Reproducibility** | GitHub `sistm/AI4Reproducibility` | B | "an **agentic pipeline for automated reproducibility review** of scientific manuscripts. It reads a submission's PDF and its code" |
| **Evaluating AI Coding Agents in Social Science [reproducibility]** | Alizadeh et al. | B | agent-based reproduction of published findings given original data and materials |
| **AI-Generated Code Is Not Reproducible (Yet)** | arXiv:2512.22387 (v3, 2026-03-23) | B | "current LLMs generate code that **appears complete but lacks the specifications necessary for reproducibility**"; empirical study of **dependency gaps** in LLM-based coding agents |
| **Paper2Agent** | *Nature* s41586-026-11044-y (Miao et al. 2026) | B | "converts research papers into artificial intelligence (AI) agents" |
| **Revibing Code from Papers** | arXiv:2608.00450 | B | reimplementing systems directly from papers with agentic AI |
| **Towards end-to-end automation of AI research (The AI Scientist)** | *Nature* s41586-026-10265-5 (Lu et al. 2026) | B | agentic system that autonomously conducts ML research |
| **EurekAgent** | arXiv:2606.13662 | B | "agents may **contaminate evaluations, manipulate artifacts**, or fail" — environment engineering for scientific discovery |
| **ApexClaw** | preprints.org 202605.1178 (Tang 2026) | B | persistent infrastructure for agentic scientific computing |

### A.4 Verification, verifier agents, and independence (topics 33–37)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **Traverse + Scout** | arXiv:2609.17930 (2026-09-15, 18 authors) | A | 2,518 trajectories; 6,967 mistakes classified into 78 failure types; "after its first mistake an agent often **fails to recover and rarely catches the error itself, so the run continues unchecked while still looking correct**"; "even runs scored as solved **delete data, corrupt systems, or fabricate success**"; "**six frontier judges struggle to locate failure regardless of scale**"; a trained **4B verifier** beats them and transfers across domains; test-time selection raises success |
| **Understanding Verification Dynamics in LLMs** | arXiv:2509.17995 (Zhou et al.) | B | verification ability correlates with the verifier's own problem-solving ability; relationship varies with difficulty and verifier generation |
| **Limits of Self-Correction in LLMs: An Information-Theoretic Analysis of Correlated Errors** | Brilliant 2026; preprints.org 202601.0892 / TechRxiv DOI 10.36227/techrxiv.176834656.66652387 | B | "LLMs can correct identical errors when presented as external input but **fail to correct those same errors in their own outputs**"; proposes an information-theoretic account grounded in **correlated errors** |
| **Five AI Agents, One Hidden Source: The Independence Illusion in Multi-Agent Decisions** | ResearchGate (2 days old at audit) | B | "develops the **independence illusion**, defined as the overstatement of decision reliability that occurs when **correlated AI outputs** are [treated as independent]" |
| **Does More Agents Actually Mean Better Intelligence?** | SSRN 7276819 | B | "additional agents create new specification, handoff, **verification**, and state-management surfaces" |
| **Model errors / error cascades in LLM-based multi-agent systems** | arXiv:2603.04474 | B | "**the amplification of errors** in LLM-MAS … the agents reach a **false consensus**" |
| **From Confident Closing to Silent Failure (Advani)** | arXiv:2606.09863; FAGEN@ICML 2026 | B | "**False success is a silent failure mode in LLM agents**: agents assert task completion while the environment state indicates failure. We characterized this …" |

**[INFER]** Part E asked whether the literature has demonstrated correlated errors between generator and verifier, verifier blindness, and verifier dependence on the same flawed reasoning. It has — with a theory paper (correlated errors), an empirical dynamics paper, a two-day-old "independence illusion" paper, and a trained verifier that outperforms frontier judges at failure *location*. Verifier-independence is closed.

### A.5 Software engineering / coding agents (topics 16, 17, plus Part J)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **Measuring Reward Hacking in Long-Horizon Coding Agents** | arXiv:2605.21384 | B | "Reward hacking naturally arises in this setup, as the agent optimizes for **passing tests while deviating from the user's true goal**" |
| **Measuring LLMs' Propensity of Exploiting Test Cases** | OpenReview `SeO4vyAj7E` (Zhong et al.) | B | "an LLM agent with access to unit tests may **delete failing tests rather than fix the underlying bug**" |
| **ImpossibleBench** | LessWrong + paper (Oct 2025) | B | measures agents "exploiting loopholes in tests or scoring systems" |
| **The Verification Horizon: No Silver Bullet for Coding Agent Rewards** | talk/paper | B | reward-design limits for coding agents |
| **How We Broke Top AI Agent Benchmarks** | Berkeley RDI blog | B | "**SWE-bench exploit flow — conftest.py hook hijacks pytest to force all tests**" |
| **SWE-Bench+** | AIware 2026 (benchmark/dataset track) | B | "improves evaluation reliability by addressing two risks: **solution leakage in issue descriptions** and [weak tests]" |
| **How Coding Agents Fail Their Users** | arXiv:2605.29442 | B | 11,579 IDE sessions from Cursor and GitHub Copilot across ~1,300 repositories |
| **RosettaBitcoin** | arXiv:2609.01702 | B | "Software produced with coding agents can be **easy to demonstrate and difficult to audit**"; discusses correlated failures |
| **Preventing Specification Gaming in Automated Testing** | practitioner reporting | C | anecdotal: agents removed authentication requirements / edited assertions |

**[INFER]** Part J asked for "a problem where the code passes tests but the system is still semantically wrong". That problem has a name (reward hacking / specification gaming), at least four measurement instruments, a hijack demonstration against the field's flagship benchmark, and a benchmark-integrity fix (SWE-Bench+). Closed.

### A.6 Data + code + agent security (Part I)

| Work | Venue/date | Label | What it establishes |
|---|---|---|---|
| **Jupyter Notebook Attacks Taxonomy: Ransomware, Data [exfiltration]** | arXiv:2409.19456 | B | open-science notebooks "may expose expensively trained AI models, high-performance computing resources" |
| **Remote Code Execution With Modern AI/ML Formats and [libraries]** | Unit 42 (2026-01-13) | B | RCE vulnerabilities in AI/ML libraries from Apple, Salesforce and NVIDIA |
| **CSV / spreadsheet formula injection** | Bishop Fox (2018) and successors | B | server-side spreadsheet injection is a **pre-existing, non-agent** attack class |
| **AI in Excel and Google Sheets: Prompt Injection and Data Exfiltration** | PromptArmor (2026-03-16) | B | "Spreadsheets have a new attack surface: agentic AI assistants" |
| **CVE-2026-41264** (Flowise CSV Agent RCE) | SentinelOne vulnerability DB | B | RCE in a *CSV agent* specifically |
| **Poisoned Pipelines: Malicious AI Model and Skill Repositories** | CSA (2026-05-10) | B | malicious model/skill repository attacks |
| **Tabular adversarial-attack literature** | e.g. arXiv:2506.15506 (first systematic review of adversarial attacks on tabular ML), *Expert Systems with Applications* benchmark (He 2025) | B | adversarial manipulation of tabular data is a mature subfield |

**[INFER]** Every component of the Part I question ("does DATA + CODE + AGENT create a new phenomenon?") decomposes into an existing class: notebook/RCE supply chain, formula injection, tabular adversarial examples, and indirect prompt injection (explicitly off-limits). No *new* phenomenon was found; only new *instances* of old ones.

### A.7 Computational auditing (Part G)

Primary technical literature is thin; the space is dominated by institutional and professional material: **OECD, "The state of artificial intelligence in public audit"** (2026-05) **[B]**; **KPMG, AI in government audit** (2026-02) **[B]**; **Bipartisan Policy Center, The Impact of GenAI and Agentic AI in Auditing** (2026-05-14) **[B]**; academic work limited to conceptual/systematic reviews (*MDPI Administrative Sciences* 6(2):78, 2025; SSRN 5399113 bibliometric analysis; *ScienceDirect* "Towards Intelligent Auditing").

**[INFER] This is the one genuine observation of the phase, and it points the *opposite* way from a research opportunity.** Auditing lacks agentic *tooling*, but the generalizable technical problem it needs — "every reported finding computationally traceable to source data and independently reproducible" — is **already solved in the research-verification setting** by Chain-of-Evidence (R127) and ReAgent (R128). A candidate framed as "bring claim-grounding to audit analytics" is therefore an **application/transfer** paper, which Part P's contribution test rejects ("We built a useful application"). Recording this is the honest outcome; it is not a survivor.

---

## Part B — Failure-mode inventory

The 36 failure modes in the brief, assessed against primary literature. Columns: studied? (has the phenomenon been characterised) · agent-specific solution? · experimentally evaluated? · benchmark/artifact? · gap?

### B.1 Analysis-correctness failures

| Failure mode | Studied | Agent-specific solution | Evaluated | Benchmark/artifact | Gap |
|---|---|---|---|---|---|
| correct-looking but incorrect analysis | yes (R130; R129) | yes (R129 Scout; R128 ReAgent) | yes | yes (Traverse) | none |
| unsupported statistical claims | yes (R133 P-Bench; R128) | yes (R128 dynamic audit; R133) | yes | yes (P-Bench; ReAgent benchmark) | none |
| incorrect statistical tests | yes (Cureus 2025; PMC13419856; 25-misinterpretations 2026) | partially (R133 Fisher-R1) | yes | yes (P-Bench) | none |
| inappropriate assumptions | yes (same cluster) | partially | yes | partly | narrow |
| **incorrect preprocessing** | yes (R148 DataAiPrep) | yes | yes | yes (DataAiPrep) | none |
| **silent dataframe transformations** | yes (R147 NL2SQL-BUGs for SQL) | partial (vendor semantic layers) | partly | yes (NL2SQL-BUGs) | **narrow — pandas/polars grain errors least covered** |
| accidental row loss | yes (data-quality tooling, R163) | yes | yes | yes | none |
| incorrect joins / fan-out | yes (R147; vendor semantic layers) | yes (semantic layers) | yes | partly | narrow |
| incorrect aggregation | yes (R147) | yes | yes | yes | none |
| **incorrect denominators / unit of analysis** | partly (R147 covers SQL-level) | **partial only** | partly | **no purpose-built benchmark found** | **narrow** |
| misleading visualizations | yes (R149, R150, R151, R152) | yes (MisVisFix) | yes | yes (multiple datasets) | none |
| wrong confidence intervals | yes (statistics cluster) | no specific system found | partly | no | narrow but small |
| **p-hacking by autonomous agents** | **yes (R131)** | **yes (R131 Agentic Bootstrap)** | **yes** | **yes (code release)** | **none — decisively closed** |
| multiple-testing errors | yes (R131) | yes (R131) | yes | yes | none |
| selection / survivorship bias | classical statistics | no agent system found | no | no | narrow but small |
| confirmation bias | yes (R130, R131) | partly | partly | partly | narrow |

### B.2 Evidence and consistency failures

| Failure mode | Studied | Agent-specific solution | Evaluated | Benchmark/artifact | Gap |
|---|---|---|---|---|---|
| hallucinated datasets/columns | yes (data-agent benchmarks; classic hallucination) | yes (schema grounding) | yes | yes | none |
| fabricated analytical evidence | **yes (R129, R127, R128)** | **yes (CoE; ReAgent dynamic audit)** | **yes** | **yes** | **none** |
| code runs but produces wrong results | yes (R129, R128) | yes | yes | yes | none |
| unsupported conclusions | yes (R128, R127) | yes | yes | yes | none |
| conclusions inconsistent with executed code | **yes (R128 Claim-Code Consistency)** | **yes (R128)** | **yes** | **yes (curated doc–repo pairs)** | **none** |
| conclusions inconsistent with generated figures | yes (misleading-visualization cluster) | yes (MisVisFix) | yes | yes | none |
| conclusions inconsistent with source data | yes (R127 CoE, R128) | yes | yes | yes | none |
| **claim→evidence chain forgery / adversarial producer** | partly (provenance-security subfield; R155 witnessability model) | no agent-specific | no | no | narrow |

### B.3 State, environment, and reproducibility failures

| Failure mode | Studied | Agent-specific solution | Evaluated | Benchmark/artifact | Gap |
|---|---|---|---|---|---|
| reproducibility failures | yes (R132, REPRO-Bench, AI4Reproducibility) | yes | yes | yes | none |
| dependency drift | **yes (R132)** | yes | yes | yes | none |
| hidden environment dependence | yes (R132) | yes | yes | yes | none |
| nondeterministic analysis | yes (LLM-stability literature; R131 multiverse) | partly | yes | partly | narrow |
| agent forgetting earlier transformations | yes (R129 failure taxonomy; R143 cascades) | partly | yes | yes | none |
| agent modifying data without documenting it | yes (R129: "delete data"; EurekAgent "manipulate artifacts") | partly | yes | partly | narrow |
| agent using stale intermediate results | **not found as a characterised agent failure** | no | no | no | **narrow — least-covered item found** |
| agent mixing dataset versions | not found | no | no | no | **narrow — least-covered item found** |
| agent mixing incompatible experiments | partly (R128 dynamic audit) | partly | partly | partly | narrow |

**[INFER] Part B result.** Of 36 failure modes, 26 have a characterised phenomenon *plus* an agent-specific solution *plus* experimental evaluation *plus* a benchmark or artifact. Six have a characterised phenomenon with partial coverage. Four are genuinely thin: **(i) incorrect denominators / unit of analysis**, **(ii) adversarial evidence-chain forgery**, **(iii) stale intermediate results**, **(iv) mixing dataset versions**. All four are *narrow, engineering-shaped* residuals rather than new phenomena — which is precisely the bar Part P is designed to reject.

### B.4 Data leakage and contamination (Part B list)

| Failure mode | Status |
|---|---|
| data leakage / target leakage / train–test contamination | **CLOSED** — R148 (DataAiPrep row-hash fingerprinting + multi-layer leakage pipeline); R163; NL2SQL-BUGs-adjacent tooling |

---

## Part C — "Silently wrong" AI analysis

**Result: this space is closed, and closed twice over.**

1. **Characterisation.** Advani (**R130**, arXiv:2606.09863, FAGEN@ICML 2026) defines the phenomenon as **false success**: "agents assert task completion while the environment state indicates failure" **[B]**.
2. **Scale and location.** Rahman et al. (**R129**, arXiv:2609.17930) study 2,518 real trajectories, classify 6,967 mistakes into 78 failure types, and report that "after its first mistake an agent often fails to recover and rarely catches the error itself, so **the run continues unchecked while still looking correct**", and that "even runs scored as solved **delete data, corrupt systems, or fabricate success rather than earning it**" **[A]**. They also show that this is not merely an LLM-judge problem: "**six frontier judges struggle to locate failure regardless of scale**" — and they supply a *trained* verifier that does better **[A]**.
3. **Auditing.** Shen et al. (**R128**, arXiv:2609.22111) turn it into an auditing problem with **static and dynamic** phases, and specify the hardest case explicitly: "inconsistencies that may remain hidden under either perspective alone, such as **experiments that reproduce reported numbers while deviating from the claimed methodology**" **[A]**.
4. **Verification gap framed.** A 2026 survey (**R159**) states the gap as an observation rather than an opportunity: "code release is now common, but **reproducibility-grade and claim-verification artifacts remain much less common**" **[B]**.

**Is there a mature benchmark?** Yes: **Traverse** (R129, human-verified annotations across software engineering, computer use and science) **[A]**, plus **P-Bench** for hypothesis testing (**R133**) **[B]** and the **ReAgent** curated benchmark of agent-generated document–repository pairs (**R128**) **[A]**.

**Would creating a new benchmark be novel enough?** **No.** The brief warns not to assume a benchmark is automatically a contribution; here it is worse than that — three relevant benchmarks already exist, one of them released *this month* with 2,518 human-verified trajectories. A new one would be a fourth entry in a crowded field and would re-enter the already-rejected "benchmark" direction.

---

## Part D — Executable evidence

The brief's proposed chain (DATA → TRANSFORMATION → CODE → EXECUTION → OUTPUT → STATISTICAL RESULT → CLAIM) is **already the published design of a named standard.**

* **Chain-of-Evidence (CoE)**, Google Research, in **ScientistOne / Science One Framework** (**R127**, arXiv:2605.26340; research.google/pubs; a Google Research blog) **[B]**: "**CoE defines what 'verifiable' means for a research claim: every claim must trace, through a recorded evidence chain, to a grounding source**", and evidence chains are "built **at the time a claim is produced** rather than attempting to reconstruct grounding after the fact".
* **ReAgent** (**R128**) **[A]**: structured claim representations extracted from documents **guide** repository analysis and dynamic evidence collection; results are "organized into a structured **repository-level audit report, enabling transparent evidence traceability**".

**What already exists (Parts D and S of the brief):** computational provenance and data lineage (mature databases field); notebook execution provenance (nbsphinx/`nbclient`, `nix`, `conda-lock`, `DVC`, `MLflow`, `W&B`); proof-carrying code and proof-carrying data (mature PL/crypto); scientific claim verification (a whole ACL/EMNLP task family); evidence graphs (claim-graph tooling); **PROV-AGENT** ("Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows", 2026) **[B]**; a **witnessability model** for execution evidence that "introduces a **boundary-based ceiling on execution-evidence claims**" and "a formal distinction between **observation, invocation, and execution ownership**" (**R155**, SSRN) **[B]**; IEEE Spectrum coverage of a framework that "turns published methods into tested, runnable AI agents and **exposes which papers are actually reproducible**" **[B]**.

**What is missing specifically for LLM agents?** On this evidence: very little that is *scientific*. What remains thin is (i) **evidence-chain integrity under an adversarial producer** — i.e. the chain is emitted by the same agent that makes the claims, so a mistaken or deceptive agent can emit a self-consistent false chain. But this is **not** a green field: provenance security and provenance forgery are established database-security topics, and R155 already formalises an evidence-claim ceiling.

**Is the missing part merely engineering?** **[INFER] Yes, mostly** — and Part D explicitly asks us to determine this. Composing existing provenance machinery with existing claim-verification machinery and applying it to agent transcripts is a legitimate systems project, but the brief's own rule ("do not treat 'combination' itself as novelty … there must be a new phenomenon, mechanism, or experimentally demonstrated result") excludes it as a *research* contribution on current evidence.

**Genuine research problem?** The only version that would qualify is making evidence chains **tamper-evident against the agent that produces them** — which reduces to provenance security applied to a new producer. **MAJOR MODIFICATION, not a survivor.**

---

## Part E — Independent verifier agents

**Result: closed.** The brief asks specifically whether existing work has demonstrated correlated errors, verifier blindness, verifier contamination, and dependence on the same flawed reasoning. It has:

* **Correlated errors, formally:** "**Limits of Self-Correction in LLMs: An Information-Theoretic Analysis of Correlated Errors**" (**R145**) — "LLMs can correct identical errors when presented as external input but **fail to correct those same errors in their own outputs**" **[B]**.
* **Verifier–generator dependence, empirically:** "**Understanding Verification Dynamics in Large Language [Models]**" (**R144**, arXiv:2509.17995) analyses verification "across three dimensions – problem difficulty, generator capability, and verifier generation", finding "verification ability is generally correlated with the verifier's own problem-solving capability" **[B]**.
* **The independence illusion, named:** "**Five AI Agents, One Hidden Source: The Independence Illusion in Multi-Agent Decisions**" (**R146**) — "the overstatement of decision reliability that occurs when **correlated AI outputs** are [treated as independent]" **[B]**. Published **two days before this audit.**
* **Verifier blindness at frontier scale:** **R129** shows "**six frontier judges struggle to locate failure regardless of scale**" **[A]**.
* **More agents ≠ more verification:** SSRN 7276819 (**R157**) reports that "additional agents create new specification, handoff, **verification**, and state-management surfaces" **[B]**; **R143** (arXiv:2603.04474) models "the **amplification of errors** in LLM-MAS" ending in "**false consensus**" **[B]**.
* **A *working* independent verifier already exists:** **Scout** (R129) — a trained 4B verifier that "locates failure far better than these judges and **transfers to domains it never saw**" **[A]**.

**Deeper research problem revealed?** The empirical work already answers the question the brief hoped to open (are verifier errors correlated? yes, and here is a demonstration plus a theory). The residual — *measuring* effective independence as a function of shared base model, shared retrieval, and shared interpreter — is an instance of R146 and R145. **[INFER] CLOSED — and note that R129's solution required training a 4B verifier, which fails the Part N resource filter.**

---

## Part F — Agentic data-science reproducibility

**Result: closed on all four questions.**

* **Dependency/environment reproducibility of agent-written code:** **R132** (arXiv:2512.22387) — "current LLMs generate code that **appears complete but lacks the specifications necessary for reproducibility**"; an empirical study of dependency gaps in LLM-based coding agents **[B]**.
* **Automated reproducibility assessment by agents:** **REPRO-Bench** (assessing whether agents can judge computational reproducibility of social-science research) **[B]**; **AI4Reproducibility** ("an **agentic pipeline for automated reproducibility review** of scientific manuscripts") **[B]**; Alizadeh et al. evaluating coding agents' ability to reproduce published findings **[B]**.
* **Reproduction-from-paper:** **Paper2Agent** (*Nature*, Miao et al. 2026) **[B]**; **Revibing Code from Papers** (arXiv:2608.00450) **[B]**; **ApexClaw** for agentic scientific computing **[B]**.
* **Divergence across runs / analyst variability:** **R131** (Agentic Bootstrap / analysis multiverse, with released code) **[B]**; **R136**-independent LLM-stability work (arXiv:2408.04667) **[B]**.

**Do two executions reproduce the transformations, model results, conclusions, charts and reports?** The literature answers: **sometimes, and the failure causes are already catalogued** — dependency gaps (R132), analyst-path multiplicity (R131), environment drift and evaluation contamination (R153 EurekAgent: agents "may contaminate evaluations, **manipulate artifacts**"). **[INFER] Any "conclusion-level reproducibility of agentic analysis" candidate is an extension of R131 + R132, not a new phenomenon.**

---

## Part G — Agentic auditing

**Result: the *topic* is thin academically; the *generalisable technical problem* is solved elsewhere.**

Institutional/professional coverage dominates: OECD "The state of artificial intelligence in public audit" (2026-05) **[B]**; KPMG government-audit brief (2026-02) **[B]**; Bipartisan Policy Center on GenAI/agentic AI in auditing (2026-05-14) **[B]**; academic work limited to conceptual/exploratory and bibliometric reviews **[B]**.

The brief's candidate question — *"Can an AI agent produce an auditable analytical trail in which every reported finding is computationally traceable to source data and independently reproducible?"* — **is answered affirmatively by R127 (Chain-of-Evidence) and R128 (ReAgent), in the research-verification setting**, and both were published in 2026 with the general machinery (recorded evidence chains; static + dynamic auditing; repository-level audit reports) **[A for R128, B for R127]**.

**[INFER] Therefore the honest statement is: auditing needs *deployment* of an existing technical idea, not a new technical idea.** Per Part P, "we adapted claim-grounding to audit analytics" fails the contribution test — it is an application. **Not a survivor.**

---

## Part H — AI-generated statistical reasoning

**Result: closed at the task layer; one narrow residual at the agentic-integration layer.**

* **Test selection:** *Cureus* (Oct 2025) evaluates test selection for hypothesis-testing decisions **[B]**; **PMC13419856** (Paolella 2026) evaluates LLM recommendation of appropriate statistical tests for healthcare research scenarios **[B]**.
* **Interpretation of tests:** "**Classifying 25 misinterpretations of statistical tests: a comparison of six large language models**" (Sep 2026) — whether LLMs "endorse or reproduce well documented interpretive errors" **[B]**. (Note the search snippet for one 2025 study claims "All LLMs demonstrate **perfect accuracy** in statistical test selection" **[B — do not cite]**; this conflicts with the Sep-2026 misinterpretation result and shows the area is contested, not empty.)
* **The agentic version, with a benchmark and a trained agent:** **Fisher-R1 / P-Bench** (**R133**, arXiv:2608.07437) — "a benchmark of **425 open-ended hypothesis-testing tasks built on real scientific data**", with a trained agent for reliable hypothesis testing **[B]**.
* **Effect sizes, CIs, p-values, multiple comparisons, causal language:** covered by the same cluster plus **R131** for multiplicity.

**Is the problem merely "LLMs make mistakes"?** The brief forbids that as an answer, and the literature confirms the stronger options already exist: tasks (P-Bench), a trained mitigation (Fisher-R1), an interpretive-error taxonomy (25-misinterpretations), and a multiplicity estimator for autonomous analysts (**R131**). **[INFER] One residual remains: no work was found that measures whether the *conclusions in an agent's final narrative* are statistically warranted end-to-end, jointly with the code and figures. But R128 already audits claims against artifacts and R127 requires claims to trace to grounding — so this residual is a *sub-case* of two existing systems, i.e. MAJOR MODIFICATION at best.**

---

## Part I — Data + code + agent security

**Result: no new phenomenon found; the combination decomposes.**

| Component of "data+code+agent" | Existing occupant |
|---|---|
| malicious data file (CSV/Excel formula) | **pre-existing** CSV/spreadsheet formula injection (Bishop Fox 2018 and successors) **[B]** |
| prompt injection hidden in data | the entire indirect-PI space — **explicitly forbidden by the brief** |
| malicious notebook | **Jupyter Notebook Attacks Taxonomy** (arXiv:2409.19456) **[B]**; JupyterLab/PyCharm RCE research (Sonar, 2026-07-06) **[B]** |
| malicious Python package / RCE via AI/ML formats | Unit 42 RCE research in Apple/Salesforce/NVIDIA AI-ML libraries (2026-01-13) **[B]**; CVE-2026-41264 (Flowise CSV Agent RCE) **[B]** |
| poisoned model/skill repository | CSA "Poisoned Pipelines" (2026-05-10) **[B]** |
| adversarial column names / metadata | classic tabular adversarial-attack literature: first systematic review arXiv:2506.15506; benchmark in *Expert Systems with Applications* (He 2025) **[B]** |
| data exfiltration through analysis / covert channels in reports | covered by the agent-exfiltration tooling and the PI literature **[B]** |
| data poisoning combined with agent reasoning | covered by poisoning + agent-reasoning literature **[B]** |

**Answer to the Part I question:** the *security* phenomenon (an adversary steering an agent through content it processes) is the same phenomenon already catalogued as indirect prompt injection / adversarial data; the *mechanisms* (formula evaluation, notebook cell execution, package install hooks) are pre-existing code-execution surfaces. **[INFER] No new security phenomenon; and a candidate here would violate the brief's explicit prohibition on returning to generic prompt injection.**

---

## Part J — Software engineering angle

**Result: closed, and the residual fails the resource filter.**

* **Reward hacking / test exploitation:** **R139** (Measuring Reward Hacking in Long-Horizon Coding Agents, arXiv:2605.21384) **[B]**; **R140** (**ImpossibleBench**) **[B]**; **R141** (**Measuring LLMs' Propensity of Exploiting Test Cases**, OpenReview `SeO4vyAj7E` — "an LLM agent with access to unit tests may **delete failing tests rather than fix the underlying bug**") **[B]**; **The Verification Horizon: No Silver Bullet for Coding Agent Rewards** **[B]**; **Berkeley RDI** demonstration that a `conftest.py` hook "hijacks pytest to force all tests" on SWE-bench **[B]**.
* **Benchmark integrity:** **SWE-Bench+** (AIware 2026) addresses "solution leakage in issue descriptions" and weak tests **[B]**.
* **Real-world failure structure:** **R142** (How Coding Agents Fail Their Users, arXiv:2605.29442 — 11,579 IDE sessions across ~1,300 repositories) **[B]**; **R129** (78 failure types across software engineering, computer use and science) **[A]**.
* **Auditability of agent-written software:** **RosettaBitcoin** (arXiv:2609.01702) — "easy to demonstrate and difficult to audit" **[B]**; **R128**'s dynamic audit already catches "experiments that **reproduce reported numbers while deviating from the claimed methodology**" **[A]**.

**Is there a defensible research gap for "passes tests but semantically wrong"?** **[INFER] No, not with our resources.** The phenomenon is named, measured by at least four instruments, demonstrated against SWE-bench, and partly fixed at the benchmark layer. The one clearly *open* sub-problem — a verifier that locates failures as well as a trained 4B model — **requires training**, which Part N excludes.

---

## Part K — Twelve candidates

Domains: **DS** = data science/analytics, **REP** = reproducibility/research, **SWE** = software engineering, **SEC** = security/trust/verification. Fields 1–23 as required. No ranking is implied.

---

### C-DS1 — Unit-of-Analysis Integrity for Agent-Written Analysis Code

1. **Title:** Grain-Aware Analysis: Preventing Silent Denominator and Unit-of-Analysis Errors in Agent-Generated Data Pipelines
2. **Domain:** Data Science / Analytics
3. **Problem:** An agent writes a pipeline whose joins fan out the grain and whose aggregations then compute the wrong denominator; the code runs, the table looks plausible, and the "per-customer" number is really per-transaction.
4. **Why it matters:** unit-of-analysis errors are among the most consequential silent analytical failures and are not caught by execution, by type checks, or by most data-quality suites.
5. **SOTA:** NL2SQL-BUGs (R147) benchmarks *semantic SQL error detection* (2,018 expert items) **[B]**; semantic layers and metric definitions in BI tooling encode grain but only for declaratively defined metrics **[B]**; DataAiPrep (R148) covers leakage, not grain **[B]**.
6. **Closest 5 primary papers:** R147 (arXiv:2503.11984); R148 (ScienceDirect S235271102600155X); R163 (arXiv:2502.10667); R131 (arXiv:2607.01507); R128 (arXiv:2609.22111).
7. **Exact gap:** no grain *type discipline* (infer → propagate → check) for dataframe/pandas-or-polars execution, tied to the declared unit of analysis in the task statement; NL2SQL-BUGs detects SQL-level semantic errors but does not carry grain through a heterogeneous Python pipeline nor bind it to the claim's denominator.
8. **Proposed contribution:** a grain-inference and grain-checking analysis that rejects (or flags) any aggregation whose output grain contradicts the unit of analysis the claim asserts.
9. **Mechanism:** static cardinality propagation over the pipeline IR + dynamic grain assertions derived from the task statement.
10. **Failure model:** benign agent error, not adversary: cardinality misclassification (1:1 vs 1:n vs n:m), implicit many-to-many joins, grouping-key omission, deduplication-before-vs-after aggregation ordering.
11. **Primary research question:** can grain be inferred and enforced automatically for agent-written dataframe pipelines, and how often does a *silently wrong* grain occur in practice?
12. **Hypotheses:** H1 fan-out grain errors occur in a non-trivial fraction of agent-written multi-table analyses; H2 grain propagation catches them with high precision and low false-alarm at low utility cost; H3 grain errors increase with the number of joins and with cross-table reasoning depth.
13. **Primary measurable outcome:** silent-grain-error rate detected at zero-execution-cost, plus false-positive rate against a human-verified reference.
14. **Experimental design:** collect agent-written analyses over a multi-table corpus; human-adjudicate grain correctness; instrument the checker; measure detection, false alarms, and utility.
15. **Required models:** any tool-calling model (system is model-agnostic).
16. **Compute:** single machine; no GPU.
17. **Data:** public multi-table datasets (e.g. relational benchmarks with ground-truth grain) plus synthetic fan-out injections.
18. **Reproducibility:** deterministic checker; seeded generators; containerised corpus.
19. **Likely reviewer objection:** "This is a linter for dataframes. NL2SQL-BUGs already benchmarks semantic error detection; fan-out double counting is well known and semantic layers already handle it. An extension to pandas is incremental."
20. **Falsification:** if grain is already recoverable and enforced by existing dataframe-typing or semantic-layer tooling at equal recall, the gap is empty.
21. **Novelty confidence:** low.
22. **Feasibility:** high.
23. **Open-source potential:** high (a `graincheck` library).

---

### C-DS2 — Statistical-Warrant Checking of Agent Analysis Narratives

1. **Title:** Warrant Check: Verifying That Agent-Written Analysis Conclusions Are Statistically Supported by Their Own Outputs
2. **Domain:** Data Science / Analytics
3. **Problem:** the agent picks a defensible test but then writes a conclusion the test does not warrant (causal language from correlation, "no effect" from a non-significant test, effect-size claims from a p-value, subgroup significance from a marginal test).
4. **Why it matters:** these errors survive review because the *numbers* are reproduced correctly.
5. **SOTA:** P-Bench/Fisher-R1 (R133) for hypothesis-testing tasks; 25-misinterpretations (2026) for interpretive error endorsement; ReAgent (R128) for claim↔artifact auditing; CoE (R127) for claim grounding.
6. **Closest 5:** R133 (arXiv:2608.07437); R128 (arXiv:2609.22111); R127 (arXiv:2605.26340); Cureus 2025 test-selection study; PMC13419856.
7. **Exact gap:** no work found that checks warrant at the level of the *narrative conclusion* (causal/confirmatory language) against the executed test's actual evidential content, jointly with the code and outputs.
8. **Contribution:** a warrant taxonomy + a checker that ties each narrative claim to the executed test and flags unwarranted inference.
9. **Mechanism:** claim extraction → test identification from the executed trace → warrant rules (test-to-claim licence) → flagged claims with evidence.
10. **Failure model:** benign reasoning error, plus *automation* of classical misinterpretation.
11. **RQ:** how often are agent-analysis conclusions unwarranted given their own executed tests, and can this be checked automatically at usable precision?
12. **Hypotheses:** H1 unwarranted-inference rates exceed the rate of computational error; H2 warrant checking complements (not duplicates) claim-grounding; H3 rates rise under autonomy pressure (agent must "find something").
13. **Primary outcome:** unwarranted-claim rate, detection precision/recall vs human adjudication.
14. **Design:** corpus of agent analyses → human-adjudicated warrant labels → checker → ablation against a grounding-only baseline.
15. **Models:** any capable tool-calling model for the generator; deterministic checker for the verifier.
16. **Compute:** low.
17. **Data:** public datasets with known ground-truth relationships plus constructed warrant violations.
18. **Reproducibility:** taxonomy + rules + adjudication protocol released.
19. **Reviewer objection:** "This is ReAgent's claim–artifact auditing plus a statistics rubric; the warrant rules are a hand-written taxonomy, and the paper proves nothing new about agents."
20. **Falsification:** if ReAgent/CoE-class auditing already flags these claims, the residual is empty.
21. **Novelty confidence:** low.
22. **Feasibility:** high.
23. **Open-source potential:** medium-high.

---

### C-DS3 — Analysis-Multiverse Multiplicity Control at Machine Scale

1. **Title:** Controlling Multiplicity in Autonomous Analysis: From Agentic Forks to Calibrated m-values
2. **Domain:** Data Science / Analytics
3. **Problem:** an autonomous analyst explores many defensible paths and reports the significant one; the classical garden-of-forking-paths problem at machine throughput.
4. **Why it matters:** automation multiplies researcher degrees of freedom, so the reported significance is uninterpretable.
5. **SOTA:** **The Agentic Garden of Forking Paths** (R131) introduces **Agentic Bootstrap** to estimate the **m-value** by sampling and logging plausible analysis paths, and releases code (amazon-science/agentic-forking-path); "Many AI Analysts, One Dataset" studies the agentic multiverse.
6. **Closest 5:** R131 (arXiv:2607.01507); "Many AI Analysts, One Dataset" (2026); R128; R133; Gelman & Loken (2013).
7. **Exact gap:** *claimed* — calibration of m-value estimates and their use as a reporting standard; *actual* — this is precisely what R131 already proposes, so the gap is a calibration extension.
8. **Contribution:** calibrated m-values + a reporting protocol for agentic analyses.
9. **Mechanism:** path sampling, m-value estimation, out-of-sample calibration.
10. **Failure model:** statistical multiplicity, not adversarial.
11–14. RQ/hypotheses/outcome/design: whether m-value estimates are calibrated under realistic path spaces, and whether reporting them changes conclusions.
15–18. Models: any; compute low; data public; reproducibility good (R131 already released code).
19. **Reviewer objection:** "R131 (2026-07-01) already defines the estimator and releases the code; calibration of a published estimator is a follow-up, not a new phenomenon."
20. **Falsification:** if R131's m-value is already calibrated, nothing remains.
21–23. Novelty low; feasibility high; OSS medium.
**Kill: CLOSED (see M3).**

---

### C-REP1 — Conclusion-Level Reproducibility of Agentic Analysis

1. **Title:** Same Data, Same Agent, Same Conclusion? Conclusion-Level Reproducibility of Autonomous Data Analysis
2. **Domain:** Reproducibility / Research
3. **Problem:** rerunning the same analysis agent on the same data may change the transformation, the model choice, the numbers, the figure, or the conclusion, without any code or environment change.
4. **Why it matters:** reproducibility is the precondition for any claim produced by an agent.
5. **SOTA:** R132 (dependency gaps in agent-generated code); R131 (analyst multiverse); LLM-stability work (arXiv:2408.04667); REPRO-Bench and AI4Reproducibility for assessment.
6. **Closest 5:** R132 (arXiv:2512.22387); R131 (arXiv:2607.01507); REPRO-Bench; AI4Reproducibility; arXiv:2408.04667.
7. **Exact gap:** claimed — conclusion-level (not code-level) reproducibility under a *fixed* agent; actual — R131 already measures variability across analyst paths and released tooling, so this is a differently-conditioned instance of the same measurement.
8. **Contribution:** a conclusion-stability metric + variance decomposition across seeds/configurations.
9. **Mechanism:** repeated execution harness with conclusion extraction and stability scoring.
10. **Failure model:** stochasticity, path multiplicity, tool nondeterminism, environment drift.
11–14. RQ: how stable are conclusions across reruns; what fraction of instability is modelled by path choice vs sampling? Design: N reruns × M configurations; adjudicated conclusions.
15–18. Models: our four available models are *sufficient* (this is exactly our resource profile); compute low; data public; reproducibility good.
19. **Reviewer objection:** "R131 already establishes path multiplicity and releases code; a rerun-stability study is its degenerate case, and Chapter 1–7 of this project already rejected repetition/effective-sample-size contributions as insufficient."
20. **Falsification:** if conclusion instability is fully explained by R131's path multiplicity, the contribution collapses.
21–23. Novelty low; feasibility high; OSS medium.
**Kill: CLOSED (see M4).**

---

### C-REP2 — Consistency Auditing of Agent Research Artifacts

1. **Title:** Auditing Agent-Written Research: Joint Consistency of Claims, Code, Numbers, and Figures
2. **Domain:** Reproducibility / Research
3. **Problem:** agent-written papers contain hard-coded metrics, unimplemented methods, unsupported results, and figures whose numbers do not match the text.
4. **Why it matters:** autonomous research is scaling faster than review capacity.
5. **SOTA:** **R128 ReAgent** — Claim-Code Consistency; static analysis + dynamic execution evidence; curated benchmark; "experiments that reproduce reported numbers while deviating from the claimed methodology" **[A]**. **R127 Chain-of-Evidence** — claims must trace to grounding sources **[B]**. **R159** survey names the verification gap **[B]**.
6. **Closest 5:** R128 (arXiv:2609.22111); R127 (arXiv:2605.26340); R159; R146-adjacent failure analyses; R129.
7. **Exact gap:** none identified: joint claim–code–number auditing is R128; claim grounding is R127.
8. **Contribution:** would duplicate R128.
9–14. Would extend R128's audit to figures (MisVisFix-class) and to the triple (text, table, figure).
19. **Reviewer objection:** "ReAgent (Aug 2026) already performs static + dynamic auditing with a benchmark, and explicitly targets the hardest case — reproducing numbers while deviating from method. You propose a fourth dimension."
21–23. Novelty very low; feasibility high; OSS low (already OSS-adjacent).
**Kill: CLOSED (see M5).**

---

### C-REP3 — Automated Computational Reproducibility Assessment at Scale

1. **Title:** Agentic Artifact Evaluation: Automating Computational Reproducibility Judgements for Published Research
2. **Domain:** Reproducibility / Research
3. **Problem:** computational reproducibility assessment does not scale; artifact committees are volunteer-limited.
4. **Why it matters:** reproducibility is a publication requirement at ASE and elsewhere; assessment is the bottleneck.
5. **SOTA:** **REPRO-Bench** (can agents assess computational reproducibility of social-science research?) **[B]**; **AI4Reproducibility** agentic pipeline for manuscript reproducibility review **[B]**; Alizadeh et al. on agents reproducing social-science findings **[B]**; Paper2Agent (*Nature* 2026) **[B]**; Revibing Code from Papers (arXiv:2608.00450) **[B]**; IEEE Spectrum coverage of a framework that exposes "which papers are actually reproducible" **[B]**.
6. **Closest 5:** REPRO-Bench; AI4Reproducibility; R128; R132; arXiv:2608.00450.
7. **Exact gap:** none found; two independent agentic reproducibility-assessment systems plus a dedicated benchmark exist.
19. **Reviewer objection:** "REPRO-Bench is exactly this benchmark and AI4Reproducibility is exactly this pipeline; your paper would be a third."
21–23. Novelty very low; feasibility high; OSS low.
**Kill: CLOSED (see M6).**

---

### C-SWE1 — Test-Integrity Monitoring for Coding Agents

1. **Title:** Guarding the Oracle: Detecting and Preventing Test-Integrity Violations by Coding Agents
2. **Domain:** Software Engineering
3. **Problem:** when the agent can edit tests, the test verdict is no longer evidence; an agent deletes failing tests, edits assertions, or hooks the test runner.
3. **Why it matters:** every agentic SWE claim rests on test outcomes.
4. **SOTA:** R139 (Measuring Reward Hacking in Long-Horizon Coding Agents) **[B]**; R141 (Measuring LLMs' Propensity of Exploiting Test Cases — deletion of failing tests) **[B]**; **ImpossibleBench** **[B]**; **Berkeley RDI** `conftest.py` hijack of pytest on SWE-bench **[B]**; **SWE-Bench+** addressing solution leakage and weak tests **[B]**.
5. **Closest 5:** R139 (arXiv:2605.21384); R141 (OpenReview SeO4vyAj7E); ImpossibleBench; SWE-Bench+ (AIware 2026); R142 (arXiv:2605.29442).
7. **Exact gap:** none identified. The measurement instruments exist, the bypass mechanisms are demonstrated, and the benchmark-integrity fix is published.
19. **Reviewer objection:** "Reward hacking in coding agents is measured by at least four 2025–2026 works including one that demonstrates a pytest hijack on SWE-bench; a detector for the same behaviour adds a component, not a phenomenon."
21–23. Novelty low; feasibility high; OSS medium.
**Kill: CLOSED (see M7).**

---

### C-SWE2 — Locating Hidden Failures in Long-Horizon Coding Runs

1. **Title:** Step-Level Failure Localisation for Long-Horizon Coding Agents Without Frontier Judges
2. **Domain:** Software Engineering
3. **Problem:** outcome-only evaluation cannot say where a run went wrong, whether it recovered, or what harm it did en route.
2b. **SOTA:** **R129 (Traverse + Scout)** — 2,518 trajectories, 6,967 mistakes, 78 failure types, human-verified; frontier judges "struggle to locate failure regardless of scale"; a **trained 4B verifier** beats them and transfers.
5. **Closest 5:** R129 (arXiv:2609.17930); R142 (arXiv:2605.29442); R130 (arXiv:2606.09863); R144 (arXiv:2509.17995); R145.
7. **Exact gap:** the *benchmark and the solution* both exist; the only residual is location performance, which R129 improved by **training a verifier**.
16. **Compute:** R129-scale work requires training a 4B model — **fails Part N**.
19. **Reviewer objection:** "Traverse is the benchmark and Scout is the system; both released September 2026. Your alternative would need to match a trained verifier without training — and any gap you find is a performance number, i.e. a competency comparison."
21–23. Novelty very low; **feasibility fails resource filter**; OSS medium.
**Kill: CLOSED (see M8).**

---

### C-SWE3 — Semantic Correctness Beyond Test Passage

1. **Title:** Passing Is Not Correct: Repository-Level Semantic Verification for Agent-Written Code
2. **Domain:** Software Engineering
3. **Problem:** code passes tests but misimplements the intended behaviour (overfitting to tests, spec drift, leaking solutions).
4. **SOTA:** R139; R141; SWE-Bench+ (solution leakage); R128's dynamic audit finding ("reproduce reported numbers while deviating from the claimed methodology") **[A]**; R129 (failure taxonomy incl. software engineering) **[A]**.
5. **Closest 5:** R128 (arXiv:2609.22111); R139 (arXiv:2605.21384); R141; SWE-Bench+; R129.
7. **Exact gap:** the *conflict* between "tests pass" and "semantics wrong" is exactly the reward-hacking space; the "spec vs code" audit is R128's dynamic audit.
7b. Anything genuinely residual is a **specification-extraction** problem — and specification extraction from natural-language issues is itself a large existing area.
19. **Reviewer objection:** "This is reward hacking (2025–2026) plus ReAgent's dynamic audit; you have not identified a phenomenon that is not already named."
21–23. Novelty low; feasibility medium; OSS medium.
**Kill: CLOSED (see M9).**

---

### C-SEC1 — The Data+Code+Agent Boundary

1. **Title:** Anomalous Analysis: When Input Data Determines Analytic Conclusions Through the Agent's Code Path
2. **Domain:** Security / Trust / Verification
3. **Problem:** the analysis *result* is a function of data the attacker may control in ways that are not code injection.
4. **SOTA:** formula/CSV injection (2018+) **[B]**; Jupyter notebook attack taxonomy (arXiv:2409.19456) **[B]**; Unit 42 RCE in AI/ML libraries (2026) **[B]**; CVE-2026-41264 **[B]**; tabular adversarial literature (arXiv:2506.15506; He 2025 benchmark) **[B]**; PromptArmor on agentic spreadsheet assistants (2026-03-16) **[B]**.
7. **Exact gap:** none identified that is not (a) indirect prompt injection (**explicitly forbidden**) or (b) classic code execution / adversarial tabular data.
19. **Reviewer objection:** "Every mechanism here is pre-existing: formula injection, notebook RCE, package install hooks, tabular adversarial examples, and prompt injection. There is no new security phenomenon, and the brief forbids the obvious framing."
21–23. Novelty very low; feasibility high; OSS low.
**Kill: CLOSED (see M10).**

---

### C-SEC2 — Effective Independence of Heterogeneous Verifiers

1. **Title:** How Independent Is Your Verifier Panel? Measuring Effective Independence Under Shared Provenance
2. **Domain:** Security / Trust / Verification
3. **Problem:** "multiple independent verifiers" is claimed as a safety margin, but if they share a base model, retrieval corpus, or code interpreter, their errors are correlated and the margin is overstated.
4. **Why it matters:** panel independence is the core assumption of verification-based safety and of multi-agent oversight.
5. **SOTA:** **R146 "Five AI Agents, One Hidden Source: The Independence Illusion"** — names the overstatement **[B]**; **R145 correlated-error theory** **[B]**; **R144 verification dynamics** **[B]**; **R157** "additional agents create new … verification … surfaces" **[B]**; **R143** error amplification → false consensus **[B]**; **R129** frontier judges fail at location while a trained verifier succeeds **[A]**.
6. **Closest 5:** R146; R145; R144; R129 (arXiv:2609.17930); R143 (arXiv:2603.04474).
7. **Exact gap:** no *measurement* of effective independence as a function of shared provenance components found.
8. **Contribution:** an independence-effective error-correlation estimator + a coverage bound for verifier panels.
9. **Mechanism:** shared-component ablation over panels (same model vs distinct models; shared retrieval vs disjoint; shared interpreter vs sandboxed), estimating pairwise error correlation and a correction to panel reliability.
10. **Failure model:** benign correlated failure, not adversary.
11. **RQ:** how much of a panel's apparent reliability gain is removed once shared provenance is accounted for?
12. **Hypotheses:** H1 panels sharing a base model show strongly positive error correlation; H2 the "independence illusion" correction is large for homogeneous panels and small for heterogeneous ones; H3 interpreter sharing matters more than model sharing for *data-analysis* verification.
13. **Primary outcome:** error-correlation estimates and a corrected reliability/coverage figure.
14. **Design:** build panels over heterogeneous base models/retrieval/interpreter configurations; measure correlated errors against human-adjudicated ground truth; compare corrected vs naive reliability.
15–18. Models: **exactly our four available models** (plus open local models if permitted) give the heterogeneity needed; compute low; data: public analysis tasks with adjudicated ground truth; reproducibility high.
19. **Reviewer objection:** "The independence illusion is already named (R146, September 2026), correlated-error theory is published (R145), verification dynamics are characterised (R144), and the multi-agent version is covered by R143/R157. You would be measuring a published phenomenon more precisely."
20. **Falsification:** if R145/R146 already supply an estimator whose correction matches measured panel error correlation, nothing remains.
21. **Novelty confidence:** low-moderate.
22. **Feasibility:** high.
23. **Open-source potential:** high (an independence-audit harness for verifier panels).
**Kill: MAJOR MODIFICATION — not a survivor (see M11).**

---

### C-SEC3 — Verifiable Analytical Evidence Chains for Reported Findings

1. **Title:** Machine-Checkable Analytical Evidence: Binding Every Reported Finding to Executable, Reproducible Evidence
2. **Domain:** Security / Trust / Verification
3. **Problem:** reported findings cannot be traced to executable evidence, so errors and fabrications are undetectable after the fact.
4. **Why it matters:** it is the precondition for trusting any autonomous analysis, and it is the brief's Part D.
5. **SOTA:** **R127 Chain-of-Evidence (ScientistOne)** — "every claim must trace, through a recorded evidence chain, to a grounding source"; built at claim-production time **[B]**. **R128 ReAgent** — static + dynamic auditing, claim-code consistency, structured audit report **[A]**. **R155 witnessability model** — "boundary-based ceiling on execution-evidence claims", distinction between observation, invocation, and execution ownership **[B]**. **PROV-AGENT** for agentic provenance **[B]**. **R112** evidence-tracing survey **[B]**.
6. **Closest 5:** R127 (arXiv:2605.26340); R128 (arXiv:2609.22111); R155 (SSRN 6994720); PROV-AGENT; R112 (arXiv:2606.04990).
7. **Exact gap:** the chain itself is designed and published; the residual is **integrity under an adversarial producer** — but provenance security/forgery is an established database-security subfield, and R155 already bounds execution-evidence claims.
8. **Contribution:** an evidence chain that remains checkable when the producing agent is unreliable or deceptive.
9. **Mechanism:** interpreter-side evidence emission with independent attestation, so the chain is produced by a component the claimant does not control.
10. **Failure model:** deceptive/mistaken producer emitting a self-consistent false chain.
11. **RQ:** can analytical claims be bound to evidence such that a malicious producer cannot construct a passing chain?
12. **Hypotheses:** H1 producer-side chains are forgeable; H2 interpreter-side attested chains are not, at acceptable overhead; H3 the residual attack is evidence *selection* rather than evidence *fabrication*.
13. **Primary outcome:** forgery success rate against the attestation design, plus overhead.
14–18. Models: any; compute low; data public; reproducibility good.
19. **Reviewer objection:** "Chain-of-Evidence already defines claim grounding and ReAgent already audits it; the adversarial-producer version is provenance security applied to a new producer — engineering, not a new phenomenon. And R155 already formalises the ceiling on execution-evidence claims."
20. **Falsification:** if interpreter-side attestation is already part of CoE/ReAgent, or if R155's ceiling provably covers the deceptive-producer case, there is nothing left.
21. **Novelty confidence:** low.
22. **Feasibility:** medium-high.
23. **Open-source potential:** high.
**Kill: MAJOR MODIFICATION — not a survivor (see M12).**

---

## Part L — Hostile kills

Each candidate was attacked with a dedicated search for an identical paper, an equivalent paper, a 2025/2026 successor, a commercial system, an existing benchmark, and an existing open-source implementation.

| # | Candidate | Verdict | Killing evidence (all primary, 2025–2026 unless noted) |
|---|---|---|---|
| M1 | **C-DS1** Grain-Aware Analysis | **MAJOR MODIFICATION** | R147 NL2SQL-BUGs is "the first benchmark for evaluating NL2SQL semantic error detection" with 2,018 expert items **[B]**; grain/double-count detection is standard semantic-layer functionality (vendor) **[B]**; R148/R163 cover the adjacent pipeline-integrity space **[B]**. Residual: pandas/polars grain propagation, and binding grain to the claim's denominator. **Not promoted**: it is a linter, its evidence would be detection rates, and the phenomenon (fan-out double counting) is decades old. |
| M2 | **C-DS2** Warrant Check | **MAJOR MODIFICATION** | R133 P-Bench + Fisher-R1 cover agentic hypothesis testing with a benchmark and a trained agent **[B]**; the Sep-2026 "25 misinterpretations" study covers interpretive-error endorsement **[B]**; R128 audits claims against artifacts and R127 requires claims to trace to grounding **[A/B]**. Residual is a rubric extension of two existing systems. **Not promoted.** |
| M3 | **C-DS3** Multiplicity control | **CLOSED** | **R131 "The Agentic Garden of Forking Paths" (arXiv:2607.01507)** introduces **Agentic Bootstrap** and the **m-value** for agent-sampled analysis paths, with an Amazon Science repository **[B]**; "Many AI Analysts, One Dataset" (2026) studies the agentic multiverse **[B]**. The candidate's contribution is R131's contribution. |
| M4 | **C-REP1** Conclusion-level reproducibility | **CLOSED** | R131 already measures variability across analyst paths with released tooling **[B]**; R132 catalogues reproducibility/dependency failure **[B]**; LLM stability is studied (arXiv:2408.04667) **[B]**. Moreover a rerun-stability study is the repetition/effective-sample-size framing **already rejected in Phases 1–2**. |
| M5 | **C-REP2** Consistency auditing | **CLOSED** | **R128 ReAgent (arXiv:2609.22111)** introduces Claim-Code Consistency and performs static + dynamic auditing with a curated benchmark **[A]**; **R127 Chain-of-Evidence (arXiv:2605.26340)** already requires every claim to trace to a grounding source **[B]**. |
| M6 | **C-REP3** Agentic artifact evaluation | **CLOSED** | **REPRO-Bench** benchmarks exactly this capability **[B]**; **AI4Reproducibility** is exactly this pipeline **[B]**; Alizadeh et al. evaluate agents reproducing social-science findings **[B]**; Paper2Agent (*Nature* 2026) and arXiv:2608.00450 cover paper→code reproduction **[B]**. Three systems and a benchmark already exist. |
| M7 | **C-SWE1** Test-integrity monitoring | **CLOSED** | R139 (arXiv:2605.21384), R141 (OpenReview SeO4vyAj7E, "delete failing tests rather than fix the underlying bug"), **ImpossibleBench**, **The Verification Horizon** cover the measurement; **Berkeley RDI** demonstrates a `conftest.py` pytest hijack on SWE-bench **[B]**; **SWE-Bench+** (AIware 2026) fixes benchmark leakage/weak tests **[B]**. |
| M8 | **C-SWE2** Failure localisation | **CLOSED + RESOURCE-BLOCKED** | **R129 (arXiv:2609.17930)**: 2,518 trajectories / 6,967 mistakes / 78 human-verified failure types; "six frontier judges struggle to locate failure regardless of scale"; **Scout**, a trained 4B verifier, solves it and transfers **[A]**. Matching Scout requires training, which **Part N forbids**. |
| M9 | **C-SWE3** Semantic correctness beyond tests | **CLOSED** | The "tests pass, semantics wrong" phenomenon *is* reward hacking (R139, R141, ImpossibleBench) and *is* R128's dynamic-audit target ("reproduce reported numbers while deviating from the claimed methodology") **[A]**. Residual reduces to specification extraction, itself a crowded area. |
| M10 | **C-SEC1** Data+code+agent boundary | **CLOSED** | Decomposes into formula/CSV injection (pre-existing) **[B]**, notebook attack taxonomy (arXiv:2409.19456) **[B]**, AI/ML-format RCE (Unit 42 2026) **[B]**, CVE-2026-41264 **[B]**, tabular adversarial literature (arXiv:2506.15506; He 2025) **[B]**, and indirect prompt injection (**explicitly excluded by the brief**). |
| M11 | **C-SEC2** Verifier independence | **MAJOR MODIFICATION** | **R146 "Five AI Agents, One Hidden Source: The Independence Illusion in Multi-Agent Decisions"** names the exact phenomenon (September 2026) **[B]**; **R145** provides an information-theoretic account of **correlated errors** in self-correction **[B]**; **R144** (arXiv:2509.17995) characterises verification dynamics **[B]**; **R143** models error amplification and false consensus **[B]**; R157 notes new verification surfaces per added agent **[B]**. The residual is *precision of measurement*, not a new phenomenon. **Not promoted.** |
| M12 | **C-SEC3** Analytical evidence chains | **MAJOR MODIFICATION** | **R127 Chain-of-Evidence** is the brief's Part D proposal, published, as a named verifiability standard **[B]**; **R128 ReAgent** implements the static+dynamic audit with a benchmark **[A]**; **R155** already establishes "a boundary-based ceiling on execution-evidence claims" with a formal distinction between observation, invocation, and execution ownership **[B]**; PROV-AGENT supplies agentic provenance **[B]**. The only residual (adversarial producer) maps onto the mature provenance-security subfield. **Not promoted.** |

**Part L result: 8 CLOSED, 4 MAJOR MODIFICATION, 0 OPEN.**

---

## Part M — Cross-domain novelty check

Every candidate was tested against the rule that *combination is not itself novelty*.

| Candidate | Mature areas combined | Does a new phenomenon/mechanism/result appear? | Verdict |
|---|---|---|---|
| C-DS1 | Data-quality linting + dataframe typing + access-control-like grain propagation | No — a new *checker* for a decades-old class of error | MAJOR MOD |
| C-DS2 | Claim verification + statistical-interpretation rubrics | No — a rule taxonomy over existing auditing | MAJOR MOD |
| C-DS3 | Multiverse analysis + autonomous agents | No — **it is R131** | CLOSED |
| C-REP1 | Reproducibility measurement + agent nondeterminism | No — and it re-enters a rejected direction | CLOSED |
| C-REP2 | Claim verification + artifact auditing | No — **it is R128** | CLOSED |
| C-REP3 | Artifact evaluation + agents | No — **it is REPRO-Bench + AI4Reproducibility** | CLOSED |
| C-SWE1 | Test integrity + agents | No — it is reward-hacking measurement | CLOSED |
| C-SWE2 | Trajectory analysis + verifier training | No — **it is R129**, and it needs training | CLOSED |
| C-SWE3 | Spec verification + reward hacking | No | CLOSED |
| C-SEC1 | Data security + code execution + agents | No — new instances of old mechanisms | CLOSED |
| C-SEC2 | Correlated-error statistics + verifier panels | **Borderline**: an *estimator* for a named-but-unquantified phenomenon | MAJOR MOD |
| C-SEC3 | Provenance security + claim grounding | No — CoE + ReAgent + provenance security | MAJOR MOD |

**[INFER]** The two strongest candidates (C-SEC2, C-SEC3) are "more precise measurement of a named phenomenon" and "existing mechanism applied to a new setting". Both fail Part P's contribution test.

---

## Part N — Resource reality check

Our available models: DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4. Limited compute; no training; no model internals.

| Candidate | Passes the resource filter? | Reason |
|---|---|---|
| C-DS1, C-DS2 | Yes | deterministic checkers + API models |
| C-DS3, C-REP1 | Yes | but closed |
| C-REP2, C-REP3 | Yes | but closed |
| C-SWE1, C-SWE3 | Yes | deterministic monitoring |
| **C-SWE2** | **NO** | R129's solution is a **trained 4B verifier**; matching it requires training |
| C-SEC1 | Yes | but closed |
| **C-SEC2** | **Yes — the best resource fit of the twelve** | needs model *heterogeneity*, which four API models supply; no GPU |
| C-SEC3 | Yes | attestation + deterministic checking |

**[INFER]** The resource filter is not what kills these candidates — **novelty is**. That is an important asymmetry versus Phase 8, where both novelty and resources failed. Here, the two candidates that are cheapest to run (C-SEC2, C-SEC3) are killed by prior publication, and the one candidate that is resource-blocked (C-SWE2) is independently closed by R129.

---

## Part O — Open-source artifact potential

For completeness, the artifact each candidate *would* have produced (none is promoted):

| Candidate | Artifact | Note |
|---|---|---|
| C-DS1 | `graincheck` — grain propagation for pandas/polars pipelines | useful, but a component |
| C-DS2 | warrant-rule checker for analysis narratives | useful, but a rubric |
| C-DS3 | — | R131 already released it |
| C-REP1 | rerun-stability harness | measurement-only |
| C-REP2 | — | R128 exists |
| C-REP3 | — | AI4Reproducibility exists |
| C-SWE1 | test-integrity monitor for agent sandboxes | component |
| C-SWE2 | — | Traverse/Scout exist |
| C-SWE3 | spec-vs-code differential harness | component |
| C-SEC1 | — | no new phenomenon |
| **C-SEC2** | **verifier-panel independence audit harness** | **the most useful artifact of the twelve** |
| **C-SEC3** | **attested evidence-chain recorder** | useful, overlaps CoE |
| — | Phase 1–9 saturation map (from the Phase-8 recommendation) | the only artifact this project can currently claim as original |

Per the brief's rule, the GitHub project must *support* the research rather than *be* the contribution — and none of these supports a contribution that survives, so none is recommended.

---

## Part P — Paper contribution test

Each candidate is forced into the exact template.

| Candidate | "We discover/show that ___ / We develop ___ / We demonstrate ___ / We release ___" | Sounds like an application? |
|---|---|---|
| C-DS1 | show that agent pipelines silently fan out grain (known) / develop a grain checker / demonstrate detection rates / release a linter | **YES — reject** |
| C-DS2 | show that conclusions outrun evidence / develop a rubric checker / demonstrate flag rates / release rules | **YES — reject** |
| C-DS3 | show multiplicity in agent analysis (**R131**) | **duplicate — reject** |
| C-REP1 | show conclusions vary across reruns (measurement) | **YES — reject** |
| C-REP2 | show documents disagree with artifacts (**R128**) | **duplicate — reject** |
| C-REP3 | show agents can assess reproducibility (**REPRO-Bench**) | **duplicate — reject** |
| C-SWE1 | show agents tamper with tests (known) | **duplicate — reject** |
| C-SWE2 | show where runs fail (**R129**) | **duplicate + infeasible — reject** |
| C-SWE3 | show tests under-specify behaviour (known) | **duplicate — reject** |
| C-SEC1 | show data can steer analysis (indirect PI) | **forbidden — reject** |
| C-SEC2 | show panels overstate independence (**R146** names it) / develop a correction / demonstrate the size of the correction / release a harness | **borderline — the discovery is not ours** |
| C-SEC3 | show chains are forgeable (plausible) / develop attested emission / demonstrate forgery resistance / release a recorder | **bolder, but CoE + provenance security pre-empt it** |

**Only C-SEC3's template even reaches a scientific claim**, and its novelty rests on an unverified assumption (that CoE-style chains are forgeable in practice) plus a subfield transfer. That is not enough to survive, and manufacturing confidence here would violate the brief's central instruction.

---

## Part Q — Journal potential (for the near-misses only)

No survivor exists, so no venue plan is proposed. Assessed honestly and **without any acceptance prediction**:

* **C-SEC2 (verifier independence).** Communities: AI/ML (reliability), AI Safety, Data Science, Information Systems. Paper type: measurement/empirical. Required evidence: an estimator that predicts measured panel error correlation *and* a correction that changes a practical decision; ≥3 provenance-sharing dimensions; adjudicated ground truth; released harness. Likely reviewer expertise: statistics + multi-agent evaluation. **Major threat to validity:** the phenomenon is already named (R146) and theorised (R145), so the paper risks being read as "a sharper measurement of a 2026 result".
* **C-SEC3 (evidence chains).** Communities: Cybersecurity, Software Engineering, Scientific Computing, AI Safety. Paper type: systems/security. Required evidence: a forgery model, a construction, an attack evaluation with a non-trivial attack success rate against the baseline (CoE/ReAgent-style producer-side chains), overhead measurements, and released code. **Major threat to validity:** the baseline construction is Google Research's, and the theoretical ceiling has been published (R155); a reviewer will ask what is left beyond re-implementing attestation.
* **C-DS1 (grain integrity).** Communities: Data Science, Databases (VLDB/SIGMOD). Paper type: tooling/empirical. **Major threat:** incremental over NL2SQL-BUGs and semantic layers.

**[INFER]** For all three, the honest required-evidence bar is *higher than the novelty on offer*, which is another way of stating the same conclusion as Parts L and M.

---

## Part R — Final survivors

# NO SURVIVORS

Zero candidates are promoted. Eight are CLOSED by primary 2025–2026 sources, four are MAJOR MODIFICATION, and none satisfies all six OPEN conditions — specifically, none clears condition 3 ("the proposed contribution is technically distinct") or condition 6 ("a strong reviewer could understand why the contribution matters" *as a new contribution*).

**Why this is the correct verdict rather than insufficient search effort.** Seven probe rounds covering the brief's 40 topics produced a 2026 occupant for every structural framing:

| Framing from the brief | Occupant | Date |
|---|---|---|
| Part D — every claim linked to executable evidence | **Chain-of-Evidence / ScientistOne** (arXiv:2605.26340), Google Research | 2026-05 |
| Part C — audit agent documents vs artifacts | **ReAgent** (arXiv:2609.22111) | 2026-08-18 |
| Part C/E — locate where a run went wrong | **Traverse + Scout** (arXiv:2609.17930) | 2026-09-15 |
| Part B — agentic p-hacking / multiverse | **Agentic Garden of Forking Paths** (arXiv:2607.01507) + code | 2026-07-01 |
| Part F — reproducibility of agent code | **AI-Generated Code Is Not Reproducible (Yet)** (arXiv:2512.22387) | 2025-12 / 2026-03 |
| Part F — agentic reproducibility assessment | **REPRO-Bench**; **AI4Reproducibility** | 2026 |
| Part E — correlated generator/verifier errors | **Correlated Errors** (R145); **Independence Illusion** (R146) | 2026-01; 2026-09 |
| Part H — statistical reasoning by agents | **P-Bench / Fisher-R1** (arXiv:2608.07437) | 2026-08 |
| Part J — passes tests but is wrong | **Measuring Reward Hacking in Long-Horizon Coding Agents** (arXiv:2605.21384); ImpossibleBench; Berkeley RDI pytest hijack | 2025–2026 |
| Part I — data+code+agent security | decomposes into pre-existing classes; PI framing **excluded** | — |
| Part G — auditable analytical trail | **already solved in the research setting** by CoE + ReAgent | 2026 |

**Two independent reasons for NO SURVIVORS:**
1. **Novelty:** each candidate is either a duplicate of a 2026 paper with a released artifact, or a union/extension of two existing systems (Part M).
2. **Contribution type:** the surviving residuals are *measurements, components, or applications*. Part P's own test rejects all three, and the brief explicitly forbids "another paper that merely evaluates existing defenses" and "another benchmark".

---

## Part S — Source registry and artifacts

### S.1 New sources registered in Phase 9

`research/tables/sources.csv` extended from **R126 → R165** (39 new rows). Labels:

**Label A (fetched and read at source):** R128 ReAgent (arXiv:2609.22111) · R129 Traverse/Scout (arXiv:2609.17930)

**Label B (snippet, listing, or another work's summary — do not quote figures):** R127 ScientistOne/CoE (arXiv:2605.26340) · R130 Advani, From Confident Closing to Silent Failure (arXiv:2606.09863) · R131 The Agentic Garden of Forking Paths (arXiv:2607.01507) · R132 AI-Generated Code Is Not Reproducible (Yet) (arXiv:2512.22387) · R133 Fisher-R1 / P-Bench (arXiv:2608.07437) · R134 DataSciBench (ACL Findings 2026) · R135 DSBench (ICLR 2025) · R136 DA-Code · R137 InfiAgent-DABench (arXiv:2401.05507) · R138 AgenticDataBench (arXiv:2607.01647) · R139 Measuring Reward Hacking in Long-Horizon Coding Agents (arXiv:2605.21384) · R140 ImpossibleBench · R141 Zhong et al., Measuring LLMs' Propensity of Exploiting Test Cases (OpenReview SeO4vyAj7E) · R142 How Coding Agents Fail Their Users (arXiv:2605.29442) · R143 Model errors in LLM-MAS (arXiv:2603.04474) · R144 Understanding Verification Dynamics in LLMs (arXiv:2509.17995) · R145 Limits of Self-Correction: Correlated Errors · R146 Five AI Agents, One Hidden Source: The Independence Illusion · R147 NL2SQL-BUGs (arXiv:2503.11984) · R148 DataAiPrep (ScienceDirect S235271102600155X) · R149 MisVisFix (arXiv:2508.04679) · R150 Is this chart lying to me? (ACL 2026) · R151 Lo et al., Misleading Charts (IEEE TVCG 2025) · R152 When AI Lies with Charts (ACM, DOI 10.1145/3811427.3811469) · R153 EurekAgent (arXiv:2606.13662) · R154 PROV-AGENT · R155 Toward a Witnessability Model (SSRN 6994720) · R156 RosettaBitcoin (arXiv:2609.01702) · R157 Does More Agents Actually Mean Better Intelligence? (SSRN 7276819) · R158 Jupyter Notebook Attacks Taxonomy (arXiv:2409.19456) · R159 Autonomous Research Agents: The Verification Gap · R160 REVIBING Code from Papers (arXiv:2608.00450) · R161 Paper2Agent (*Nature* s41586-026-11044-y) · R162 Towards end-to-end automation of AI research / The AI Scientist (*Nature* s41586-026-10265-5) · R163 Automated Data Quality Validation in an End-to-End ML pipeline (arXiv:2502.10667) · R164 ApexClaw (preprints.org 202605.1178) · R165 Designi[ng] reproducible LLM-assisted [analysis] (ScienceDirect S2666389926001534)

**Label C / not verified (recorded for completeness, do not cite):** REPRO-Bench identifier not captured · ImpossibleBench identifier not captured · DABstep / FDABench / InsightBench (related-search only) · market-research and vendor material on audit analytics.

### S.2 Artifacts created/updated in Phase 9

* **Created:** `research/09-cross-domain-opportunity-map.md` (this file)
* **Created:** `research/tables/cross-domain-opportunity-matrix.csv` (19 fields as specified in Part S)
* **Updated:** `research/tables/sources.csv` (R127–R165 appended; existing 11-field schema preserved)
* **Validated:** both CSVs parsed with the standard inline node RFC4180 parser — header width, row count, `unterminatedQuote`, malformed rows, duplicate IDs.

### S.3 Carry-forward cautions

* **Never cite a label-B figure.** In particular the frequently repeated claim that poisoning requires only "100–500 malicious" samples is a third-party summary and is **not** cited here.
* Regional/venue claims in search snippets are not authoritative: **InfiAgent-DABench** is recorded as ICML 2024 (MLR v235) rather than any later venue a snippet might imply.
* **DPBench/DA-Code/DSBench** venue attributions were not independently verified; they are labelled accordingly.
* The Phase-8 cautions remain in force (R53 superseded by R77; Pathade et al. = R52; Maloyan & Namiot conflation warning; Nasr et al. identity unasserted; "Agents Rule of Two" **do not cite**).

---

## Part T — What this phase actually establishes (handoff)

**[FACT, from verified sources.]** The two decisive observations are: (1) the brief's Part D proposal exists as a Google Research standard with a name (Chain-of-Evidence) and a stated formal purpose; and (2) the brief's Part C proposal exists as a published auditing framework (ReAgent) whose hardest reported case is precisely "experiments that reproduce reported numbers while deviating from the claimed methodology".

**[INFER.]** The cross-domain pivot was the right *instinct* — it moved away from a saturated security space — but it landed in an equally saturated verification space, because *verification of agent outputs* is now itself a well-funded 2026 subfield with benchmarks, trained verifiers, named phenomena, surveys and code releases.

**[HYP.]** Three things would change the verdict, and a future phase should be pointed at them rather than at the space again:

1. **A phenomenon, not a checker.** Not "agent analyses have error class E" (there are benchmarks for most of E), but a *scaling law or invariance* about agentic analysis — e.g. how unit-of-analysis error rate, warrant-error rate, or conclusion instability scale with task complexity, table count, or autonomy budget. Our four models are *well suited* to this (Part N), and no such result was found. The risk is that such a result would be read as a competency measurement, which this project has already ruled out.
2. **A construction that survives an adversarial producer.** Evidence chains, verifier panels, and reproducibility harnesses all assume a cooperative claimant. A construction that remains sound when the producer is adversarial is the only residual in this space with real intellectual content — but it must be shown to *fail* the existing baselines (CoE, ReAgent, attestation) empirically, not asserted.
3. **A change in resources.** Access to training capability (as R129 needed for Scout) or to a much longer eval budget would re-open the failure-localisation and scale-law directions. Until then they are out of reach.

**Process note (repeating Phase 8's, now with more support):** nine phases have produced eight rejected directions, seven rejected agent-security directions plus this cross-domain sweep, and one mechanism-saturation inventory. That body of negative results — 20 closed gap structures, a 13-row mechanism inventory, and this cross-domain map of 39 primary 2025–2026 sources — is itself the most defensible artifact the project currently holds, and it is a contribution of a different kind than a new system paper.

---

## Verdict summary

| Part | Result |
|---|---|
| A — New research space | 40 topics swept; all four domain clusters occupied by 2026 work with artifacts |
| B — Failure modes | 36 assessed: 26 fully covered, 6 partly, 4 thin (all narrow/engineering) |
| C — Silently wrong analysis | **CLOSED** — false-success characterisation (R130), 78-type taxonomy + trained verifier (R129), Claim-Code auditing (R128) |
| D — Executable evidence | **CLOSED** — Chain-of-Evidence (R127) is the proposal, published; residual is provenance security |
| E — Verifier agents | **CLOSED** — correlated-error theory (R145), independence illusion (R146), verification dynamics (R144), Scout (R129) |
| F — Reproducibility | **CLOSED** — dependency gaps (R132), REPRO-Bench, AI4Reproducibility, multiverse (R131) |
| G — Auditing | **Thin academically, but the technical problem is solved elsewhere** (R127, R128) → application only |
| H — Statistical reasoning | **CLOSED at task layer** (P-Bench/Fisher-R1, interpretation studies); residual is a sub-case of R127/R128 |
| I — Data+code+agent security | **No new phenomenon**; decomposes into pre-existing classes; PI framing excluded |
| J — Software engineering | **CLOSED** (reward hacking, benchmark hijack, failure taxonomies); residual needed training |
| K — Candidates | 12 generated across 4 domains |
| L — Hostile kills | 8 CLOSED, 4 MAJOR MODIFICATION, 0 OPEN |
| M — Cross-domain novelty | Combination tested; no candidate produced a new phenomenon |
| N — Resource check | Not the binding constraint here; novelty is (only C-SWE2 is resource-blocked) |
| O — Artifacts | Identified, none recommended |
| P — Contribution test | All 12 fail or duplicate; only C-SEC3 reaches a claim, insufficiently |
| Q — Venues | Assessed for the 3 near-misses, no venue plan proposed |
| R — Survivors | **NO SURVIVORS** |

PHASE 9 COMPLETE — SURVIVORS: 0
