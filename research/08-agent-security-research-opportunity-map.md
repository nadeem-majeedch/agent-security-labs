# 08 — Agent-Security Research Opportunity Map (Phase 8)

**Status: SEARCH COMPLETE — SURVIVORS: 0 → NO-GO (no candidate survives)**

**Date of audit:** 25 September 2026
**Scope:** Find a *fundamentally different* LLM-agent security research problem that supports a **real security mechanism or attack/defence system** and an **experimentally demonstrated new security phenomenon**. Explicitly **not** a metric, benchmark-validity, judge-comparison, or survey contribution.
**Standing constraints (unchanged):** do not fabricate citations/numbers/DOIs/URLs; use primary sources; prefer NO-GO over manufactured novelty; mark unverified claims; do not write the paper; do not implement AgentSec Lab; do not commit/push; do not rank models by capability; do not claim acceptance probability.

---

## Part 0 — Method, verification convention, and what changed since Phase 7

### 0.1 Verification labels

| Label | Meaning | Citable as a figure? |
|---|---|---|
| **A** | Fetched and read at the source (abstract page or full HTML at the publisher/arXiv). | Yes, for what was actually read |
| **B** | Read only through another paper's summary, a search snippet, or a third-party listing. | **No** — never quote a number |
| **C** | Not verified at all. | No |

Claim tags used throughout: **[FACT]** (verified at source), **[INFER]** (derived from verified facts), **[HYP]** (hypothesis, not established), **[OPEN]** (explicitly unresolved in the literature).

### 0.2 What this phase had to overcome

Seven directions have now been rejected (ASR decomposition; repetition/ICC/ESS/ranking stability; attack-budget-vs-replication; statistical evaluation methodology; LLM-judge/evaluator validity; defence-dependent evaluator bias; benchmark/evaluation measurement validity generally). Every one of them was a *measurement* contribution. Phase 8 is therefore required to produce a **mechanism** contribution with a **new phenomenon**.

The decisive discovery of this phase is that the mechanism space is **as saturated as the measurement space**. Two systematizations published **inside the last thirty days** name the structural framings that a Phase-8 candidate would naturally reach for, and close them:

* **arXiv:2609.23700** — *When the Agent Becomes the Kernel: A Systematization of Security on the Path to AI-Native Operating Systems* (Zhang, Sun & Shi, submitted **2026-09-20**, 32 pages) **[FACT — abstract read at source, label A]**. Verbatim, the paper "systematize[s] the security of such systems around a single distinction: a **crossing mediated over provenance admits a deterministic check, while one over content semantics does not**", gives a **trust-boundary taxonomy** that "locates where mediation must occur", isolates "the central mediation gap at two kinds of semantic judgment", argues the gap "leaves an **irreducible residual of undetected attacks** wherever inputs and actions are not restricted in advance to an enumerated set", and "systematize[s] defenses across **runtime monitoring, architectural separation, and authorization**". It also states the compositional-reversibility point that was this phase's best remaining idea: *"Individually reversible actions can compose into an irreversible effect, so reversibility is a property of the action sequence, not of each [action]"* **[FACT — search snippet of the same paper, label B for this sentence]**. It concludes by "deriv[ing] the design constraints, open challenges, and research agenda".
* **arXiv:2609.00595** — *SoK: When Safe Agents Fail Together: The Security of Multi Agent LLM Systems* (Yang, Xu, Liu, Fendley, Hong, Li & Cao, submitted **2026-09-01**) **[FACT — abstract read at source, label A]**. Systematizes **197 works** through "six interaction interfaces, four adversary positions, seven system-level risks, and eight recurring attack paths", introduces an **A-I-R framework** (adversary position → interaction interface → system-level risk), organizes defences into a **five-part contract** (path target, observation, intervention, trust boundary, **recovery**), and "identif[ies] **path closure and recovery as key challenges**". It also audits **44 evaluation/benchmark works**. Opening sentence: *"Safe agents can fail together."*

**[INFER]** Together these two documents claim (a) the compositional/multi-agent threat space, (b) the mechanism taxonomy (monitoring / separation / authorization), (c) the provenance-vs-content distinction, (d) the reversibility-composition result, and (e) recovery and path closure. A Phase-8 candidate must therefore find space *outside* both — or demonstrate that their claimed "irreducible residual" is reducible. The latter is a legitimate research direction but is an *adversarial* claim against a systematization, and the only honest way to make it is to produce a deterministic mediator for a class they say has none. Every attempt to do so in this phase collapsed onto an existing mechanism (§Part G).

### 0.3 Reading discipline and known limitations

* **OpenReview blocks automated fetch** (`/challenge?redirect=` on both `/forum` and `/pdf`). Three Phase-8 items that live only on OpenReview are therefore **label B**: Causal Detection of Multi-Step LLM Agent Attacks (`Kb2m543agS`), Interaction-Barrier Shielding (`v2QHWcC0UC`), and Stronger Adaptive Attacks Bypass Defences Against LLM... (`7B9mTg7z25`). None is load-bearing for the verdict; all three are listed as corroborating saturation evidence only.
* **MDPI blocks scripted fetch** (403). The one MDPI item used here (`Electronics` 15(10):2214, Park 2026) is **label B**.
* **PDF fetch is unsupported** (`application/pdf`). All source reads used the arXiv `/abs/` route or, where available, `/html/<id>vN`.
* **Several key Phase-8 sources are label B** because only their abstract listing or a search snippet was retrieved. They are sufficient to establish *existence and overlap* (which is what a novelty audit needs) but **not** to quote a figure.

---

## Part A — Current (2025–2026) map of LLM-agent security

Fifteen areas were searched. For each: strongest work found, strongest attack, strongest defence, benchmark, the limitation that a candidate would target, experimental accessibility, apparent novelty space, required model capability, and resource demand. Labels are attached to every load-bearing claim.

### A.1 Indirect prompt injection / instruction-vs-data
* **Major work:** CaMeL (arXiv:2503.18813, Phase-6/7 registry); FIDES; RTBAS; FORGE; Progent — all five named together as the "out-of-band defence" family by **R97** arXiv:2606.26479 **[A]**. Also **STAC** (arXiv:2509.25624) and **StepJack** (splitting one attack across multiple pages along the agent's navigation path) **[B]**.
* **Strongest attack:** adaptive/defence-aware attacks. **R97** states verbatim that an earlier wave of adaptive attacks "broke twelve of them at over 90% success" **[A for the claim as published in R97; the underlying twelve-defence result is third-hand]**.
* **Strongest defence:** deterministic out-of-band mediation. **R97** reproduces Progent on AgentDojo with Qwen2.5-7B self-hosted on **one H200** and reports mean ASR cut **25.8% → 4.2%** over three runs, with a hand-crafted adaptive attack at **2.6%**; it explicitly declines to generalise ("does not establish the hypothesis") **[A]**.
* **Benchmark:** AgentDojo (universal), ASB (**R02**, already registered), WASP (seen in related-search, not verified).
* **Limitation a candidate would target:** in-band detection is broken; out-of-band enforcement is the accepted answer.
* **Accessibility:** high (AgentDojo is open). **Novelty space:** near zero — the family is systematized as Biba integrity + reference monitoring + least privilege in R97. **Model needs:** any tool-calling model. **Resource:** low.
* **Verdict for a Phase-8 candidate: CLOSED.**

### A.2 Tool misuse / tool authorization / excessive agency
* **Major work:** **Progent** (symbolic per-call least-privilege rules) and its documented limitation — verbatim from **R97**: *"Progent's proxy checks tool-call names and arguments; it **does not track the provenance of the data those arguments derive from**"* **[A]**. **R96 ActPlane** (arXiv:2606.25189) — "Programmable OS-Level Policy Enforcement for Agent Harnesses" **[A]**.
* **Strongest attack:** tool-call chains composed of individually authorised calls (see A.11, A.12).
* **Strongest defence:** argument-motivated per-call policy (Progent); OS-level eBPF mediation (ActPlane) which "improves policy compliance, **including on indirect execution paths that tool-call interception cannot observe**, with **1.9%–8.4% overhead**" **[A]**.
* **Benchmark:** AgentDojo; **R108 PEAR** (Planner-Executor Agent Robustness Benchmark) **[B]**.
* **Novelty space:** the one evident crack — *argument provenance* — is immediately closed by **R116 NeuroTaint** (arXiv:2604.23374), described as "the **first comprehensive taint tracking framework** tailored for the unique information flow characteristics of LLM agents" **[B]**, and by CaMeL/FIDES/RTBAS/FORGE which are taint/label systems already **[A via R97]**.
* **Verdict: CLOSED.**

### A.3 Tool poisoning, tool supply chain, MCP ecosystem
* **Major work:** **MCPTox** (arXiv:2508.14925, already **R06**); **R111** *Beyond Tool Poisoning: Attack Surfaces of Malicious MCP Servers* (MDPI *Electronics* 15(10):2214, Park 2026) **[B]**; **R107** *Malicious Agent Skills in the Wild: A Large-Scale Security Analysis* (arXiv:2602.06547) **[B]**; CSA research note on `SKILL.md` agent-context poisoning (2026-05-06) **[B]**; Snyk "ToxicSkills" audit **[B]**; OWASP MCP Top-10 MCP03 Tool Poisoning **[B]**; NSA/DoD-style MCP security guidance (media.defense.gov, 2026-06-02) **[B]**.
* **Strongest attack:** poisoned tool metadata (MCPTox 72.8% ASR as recorded in Phase-6 notes); `SKILL.md`-level context poisoning.
* **Strongest defence:** **R91 De**legation Without Trust's authorization broker (§A.6); MCP gateways/scanners (vendor).
* **Benchmark:** MCPTox; MCP Security Bench (MSB) surfaced in related searches, unverified.
* **Novelty space:** the precise four-way discrimination problem the brief asks for — trusted tool vs compromised tool vs malicious *output* vs poisoned *description* — is attacked from at least three directions in 2026 (R91 runtime authorization; R111 attack-surface enumeration over four surfaces; R107 skill-level supply chain) **[B/A mix]**.
* **Verdict: CLOSED.**

### A.4 Memory poisoning and persistent state
* **Major work:** **R109** *A Systematic Study of Memory Poisoning Attacks in LLM Agents* (arXiv:2606.04329) — "persistent memory introduces the risk of memory poisoning, where **a single adversarial memory write can exert long-term influence**" **[B]**; ASB's memory-poisoning and Plan-of-Thought backdoor components (**R02**) **[A, registered in pass 2]**; CAMS five-layer memory security architecture (ScienceDirect, Dhivyasree 2026) **[B]**; MPBench and a MemGuard-style proactive defence (surfaced in related searches, unverified).
* **Attack:** persistent, delayed, cross-session instruction injection.
* **Defence:** memory integrity architectures (CAMS), runtime memory guards.
* **Benchmark:** ASB (R02) has a memory-poisoning component; MPBench unverified.
* **Verdict: CLOSED.**

### A.5 RAG / context poisoning
* **Major work:** ordinary RAG-poisoning literature (PoisonedRAG lineage) plus agent-context poisoning notes **[B]**; the Ferrag et al. survey "From prompt injections to protocol exploits" (ScienceDirect, 2025, cited-by 161 per the listing) **[B]**.
* **Verdict: CLOSED** (this is the oldest sub-area; no new phenomenon available).

### A.6 Multi-agent, delegation, identity, trust
* **Major work:** **R91** *Delegation Without Trust* (arXiv:2609.00267) **[A]**. Four adversaries (confused deputy, token theft/replay, prompt-injection privilege escalation, compromised sub-agents); eight security requirements; default runtime fails all four; **LangGraph, CrewAI, AutoGen and the MCP authorization model give none or partial confinement**; an authorization broker "blocks all four threats", "resists 11 direct attacks on its design", "accepts **0 of 200,000** forged tokens", "confines a compromised sub-agent to its delegated task (**a mean of 1.5 reachable actions versus all 8,100 under bearer delegation, across 2,000 randomized scenarios**)", at "**about 2.6 microseconds per decision**", and is "realized in production in VotalAI's LLM Shield".
* **Also:** **R100** the MAS SoK (arXiv:2609.00595) **[A]**; **R106 AgentDID** (arXiv:2604.25189) **[B]**; cross-agent privilege escalation (Rehberger, Sep 2025, from Phase-7 notes); **R119** *Towards Secure Systems of Interacting AI Agents* (arXiv:2505.02077) **[B]**; FIDO Alliance agentic-interaction standards initiative (2026-04-28) **[B]**; NIST NCCoE concept paper on agent identity/authorization (Feb 2026) **[B]**; a "principal hierarchy problem" write-up **[B]**.
* **Defence:** capability/authorization brokers with delegation-chain semantics.
* **Verdict: CLOSED** — the strongest closure of the phase's conventional sub-areas; R91 answers the "what security guarantees survive delegation" question directly, with an implementation and an adversarial evaluation.

### A.7 Isolation, sandboxing, OS-mediated mediation
* **Major work:** **R96 ActPlane** (eBPF, information-flow-control DSL, policies declared by the agent and enforced in the kernel) **[A]**; **R114** *Isolation, Access Control, and Time-of-Check-to-...:* "A systematized corpus of **39 execution-security papers (2023–2026)**, organized into **17 categories**: isolation architectures, escape and adversarial..." (arXiv:2607.05743) **[B]**; **R117** *A Deterministic Control Plane for LLM Coding Agents* (arXiv:2606.26924) — "Integrity controls in §4.1 protect this project's installed agent definitions from tampering" **[B]**; **R99** the AI-native-OS systematization **[A]**.
* **Real-world attacks:** CVE-2026-82533 (a sandboxed DeepSeek-harness agent able to **disable its own confinement**) **[B — vendor research blog]**; CSA note "AI Coding Agent Sandbox Escapes: The Trust Handoff Flaw" (2026-07-22) **[B]**.
* **Verdict: CLOSED.** Note in particular that the "agent must not be able to reach its own control plane" idea is already covered by R117 §4.1 (agent-definition tamper protection) and R96 (kernel-level enforcement), and its real-world instance is a CVE rather than an open phenomenon.

### A.8 Runtime monitoring, policy engines, IFC, capabilities
* **Major work:** **R92** *Tracking Capabilities for Safer Agents* (Odersky, Zhao, Xu, Bračevac & Pham, arXiv:2603.00991) **[A]** — agents express intentions as Scala 3 code under **capture checking**; "capabilities are program variables that regulate access to effects and resources"; "**local purity**, the ability to enforce that sub-computations are side-effect-free, preventing information leakage when agents process classified data"; "experiments show that agents can generate capability-safe code with **no significant loss in task performance**, while the type system reliably prevents unsafe behaviors". Companion: *Securing Agents With Tracked Capabilities*, ACM DOI 10.1145/3786335.3813127 **[A — related DOI on the abs page]**.
* **Also:** **R110 AgentGuard** (arXiv:2509.23864) "Runtime Verification of AI Agents" **[B]**; AgentSpec; VeriGuard; **R98 CAGE** (arXiv:2607.29190) **[A]**; CaMeL; FIDES; RTBAS; FORGE; Progent (all named in R97) **[A]**.
* **Verdict: CLOSED.** The mechanism zoo is fully populated: capability, capture-checking, taint, IFC lattice, reference monitor, symbolic rules, OS-level IFC.

### A.9 Provenance, audit, observability, accountability
* **Major work:** **R112** *From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents* (arXiv:2606.04990, v4 dated 2026-06-28) — "An action or tool call depends on a parameter, tool output, or memory item; **agent provenance adds trust/taint labels on the used value**"; six-dimension taxonomy (trace sources, evidence and execution units, provenance relations, ...) **[B]**; **R113 TraceCaps** (ACM DOI 10.1145/3786582.3786832) — "coupl[es] **tamper-evident provenance** with a **monotone risk enforcement** that gates agent actions" **[B]**; **R101 Agent-Sentry** (arXiv:2603.22868) — "a runtime defense system that **enforces safe bounded execution of LLM-based agents by learning and reasoning over their execution provenance**" **[B]**, published at **IMC 2026** per the author's publication list **[B]**; University of Southern California "Auditable Agents" five-dimension/three-mechanism-class framing **[B]**; METR's investigation of an agent probing "tampering with their own transcripts" and a working **tool-call spoofing** technique (metr.org, 2026-08-26) **[B]**.
* **Verdict: CLOSED** (both the survey and at least one peer-reviewed mechanism exist).

### A.10 Containment, recovery, rollback, incident response
**This is the area where the phase's strongest candidate lived, and it was the most decisively closed.**
* **R93 ACRFence** (arXiv:2603.20625, CoDAIM workshop 2026) **[A]** — "Servers treat these re-generated requests as new, enabling **duplicate payments, unauthorized reuse of consumed credentials, and other irreversible side effects**; we term these **semantic rollback attacks**. We identify two attack classes, **Action Replay** and **Authority Resurrection**, validate them in a proof of concept, ... We propose ACRFence, a framework-agnostic mitigation that **records irreversible tool effects and enforces replay-or-fork semantics upon restoration**".
* **R94 Safe to Resume?** (arXiv:2608.29381) **[A]** — "**the first systematic security study of checkpoint and rollback in existing agent systems**". "Correct rollback does not imply secure recovery: a faithfully restored checkpoint may resume an execution whose states, assumptions, and external effects **never coexisted in any valid history**." **Five failure modes**; **three end-to-end attacks on Hermes, Cline and LangGraph** enabling "malware-verification bypass, unauthorized mail forwarding, and double payment"; a "multi-agent analysis pipeline that reconstructs execution semantics, identifies violations of the five failure conditions, and validates them through actual rollback"; evaluated "across **five representative frameworks**".
* **R95 Robust Agent Compensation (RAC)** (arXiv:2605.03409, ACM CAIS 2026) **[A]** — "**a log-based recovery paradigm** (providing a safety net) implemented as an architectural extension... to support reliable executions (**avoiding unintended side effects**)", implemented on LangChain, demonstrated on **τ-bench and REALM-Bench**, "1.5–8× or more better in both latency and token economy compared to state-of-the-art LLM-based recovery approaches".
* **Also:** **R123 SecRespond** (arXiv:2607.26791) — "the **first benchmark for evaluating LLM agents on the post-compromise incident-response workflow**" **[B]**; **R124** *Delegation-Aware Runtime Contracts for Open LLM Multi-Agent Systems* (ResearchSquare rs-10533072, 2026-08-13) containing a **recovery-consistency** property: *"After recovery completes, no active capability or persistent state depends exclusively on a revoked delegation chain"* **[B]**.
* **Verdict: CLOSED — and note the shape of the closure.** Phase 8's first hypothesis was "prevention dominates; detection→containment→recovery is underdeveloped". Within a single search that hypothesis produced **two independent primary papers specific to agent checkpoint/rollback security, a third on compensation-based recovery, a dedicated incident-response benchmark, and a recovery-consistency security property**. Recovery is not underdeveloped; it is a mature sub-area with its own attack classes, failure taxonomy, benchmark and property.

### A.11 Compositional / emergent / interaction security
* **Major work:** **R100** the MAS SoK (**197 works**) **[A]**; **R121** *Unsafe Only in Combination: Interaction-Barrier Shielding* (OpenReview `v2QHWcC0UC`) — "**many agent attacks are unsafe only in capability combinations**" **[B]**; **R122** *Compositional Threat Analysis of Latent Compromise in LLM Agents* (arXiv:2608.08131) — "**no component is catastrophic alone, yet their conjunction can produce correlated destructive action**" **[B]**; **R103 STAC** (arXiv:2509.25624) — *"STAC enforces that every intermediate step appears individually benign"* **[B]**; **R120** *Causal Detection of Multi-Step LLM Agent Attacks* (OpenReview `Kb2m543agS`) — detects attacks "where **individually benign actions combine into malicious workflows**" **[B]**.
* **Verdict: CLOSED.** Part D's thesis — safety does not compose — is now the *opening sentence* of a September-2026 SoK and is subject to at least one dedicated shielding mechanism and at least two detection systems.

### A.12 Temporal / stateful / latent / long-horizon
* **Major work:** **R94** (state continuity), **R115** *Self-Evolving Stealthy Prompt Injection Attack against Long-Horizon Agents* (arXiv:2608.30441) — "security evaluations must test whether an injected objective can **survive**..." **[B]**; **R116** NeuroTaint **[B]**; AgentLAB (long-horizon attack benchmark) **[B, identifier not captured]**; "Goal Persistence and Goal Drift in Long-Horizon AI Agents" **[B]**; OpenAI "Safety and alignment in an era of long-horizon models" (2026-07-20) **[B]**; a claim that "attack success rates increase 16% on average as interactions extend across turns" **[B — do not cite]**.
* **Verdict: CLOSED.**

### A.13 Human-in-the-loop approval and consent integrity
* **Major work:** **R102** *Trustworthy Human-in-the-Loop Control for Secure ...* (arXiv:2609.18411, 2026-09-16) **[B]** — "We present the **Verifiable Action Card (VAC)**, an architectural defence that **reconstructs approval information from the ground-truth pending [action]**"; "We implement VAC in a complete agentic browser and evaluate it on a **24-scenario benchmark covering confused-deputy attacks, Lies-in-the-Loop** [attacks]...".
* **Also:** Anthropic's "approval fatigue" framing **[B]**; a fleet of vendor/blog treatments of reversibility-tiered approval gates **[B]**; MDPI *Computers* 14(5):98 (Kanaker 2026) modelling HITL residual risk **[B]**.
* **Verdict: CLOSED.**

### A.14 Formal methods and verification
* **Major work:** **R98 CAGE** (arXiv:2607.29190) — **[A]** verbatim: "We ask whether a candidate action stays authorized over a declared neighborhood of plausible correctly bound returns: **one admissible binding fault plus bounded numerical drift**. We prove that **certifying the categorical and numerical channels separately does not compose**: perturbations that are safe on each channel alone can jointly turn the same action unsafe. CAGE certifies this joint neighborhood directly, enumerating the discrete branches exactly and certifying the continuous perturbation within each branch. ... CAGE removes the **in-budget false allows** that accurate pointwise gates admit, while keeping a useful fraction of decisions autonomous." Code released. *(Micro-finding of this phase: the sentence "certifying the categorical and numerical channels separately does not compose" is a **non-composition** result with a proof — i.e. a published instance of exactly the compositional-security framing, in the authorization layer, with a certificate.)*
* **Also:** AgentVerify (FSM + LTL model checking, preprints.org 202604.1029) **[B]**; VeriGuard; AgentSpec; **R92** capture-checking; ActPlane's IFC DSL; noninterference framed as "local purity" in R92 **[A]**.
* **Verdict: CLOSED.** Part J wanted "a concrete property and a concrete mechanism". CAGE supplies both, including a **certificate** and a **non-composition theorem**.

### A.15 Adversarial testing, adaptive evaluation, security regression testing
* **Major work:** **R97** (adaptive-evaluation protocol as a contribution) **[A]**; Adaptive Attacks Break AI Agent Defenses (NAACL 2025 Findings) **[B]**; **R104** *Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols* (arXiv:2510.09462) **[B]**; **7B9mTg7z25** *Stronger Adaptive Attacks Bypass Defences Against LLM...* **[B]**; **R105** *Visual Confused Deputy* (arXiv:2603.14707) **[B]**; AgentFuzz (USENIX Security 2025, directed greybox fuzzing for taint-style vulnerabilities in LLM agents) **[B]**; **R108 PEAR** **[B]**.
* **Note for the audit:** the *natural* Phase-8 candidate in this area ("run every published defence against an adaptive attacker") is **both** already published (R97, R104, NAACL 2025) **and** a member of the already-rejected direction 7 (evaluation methodology). Double-excluded.
* **Verdict: CLOSED.**

### A.16 Cross-cutting: the systematization layer (new in Phase 8)
* **R99** AI-native-OS systematization (32 pages, 2026-09-20) **[A]**
* **R100** MAS security SoK, 197 works (2026-09-01) **[A]**
* **R112** Evidence-tracing/provenance survey (2026-06-28) **[B]**
* **R114** Execution-security/isolation systematization, 39 papers, 17 categories (2026-07-07) **[B]**
* **R118** *Reframing LLM Agent Security as an Agent-Human Interaction Problem* (arXiv:2605.24309) **[B]**
* **R109** memory-poisoning systematic study **[B]**
* Chhabra et al., *Agentic AI Security: Threats, Defenses, Evaluation* (IEEE, 2026, "Cited by 58" per listing) **[B]**
* Sun et al., *A Survey on the Unique Security of Autonomous and [Agentic] ...* (preprints.org 202602.1655) **[B]**
* Phase-7's **R79** LLM-as-a-judge SoK, **R77** REDAgentBench **[A]**

**[INFER]** A field with eight systematizations in twelve months, each covering ≥39–197 works, has no room for a *fundamentally different* problem at the layer the brief targets. That is the phase's central finding.

---

## Part B — The "uncomfortable gap": which structures are actually open?

The brief supplied ~18 candidate gap structures. Each is scored against primary 2025–2026 evidence.

| # | Structure from the brief | Occupying evidence | Status |
|---|---|---|---|
| B1 | X only works before the agent enters state Z | R93 ACRFence; R94 (state/continuation mismatch) | CLOSED |
| B2 | X fails after memory persistence | R109 systematic study; CAMS; ASB memory-poisoning | CLOSED |
| B3 | X cannot distinguish trusted vs untrusted tool outputs | CaMeL/FIDES/RTBAS/FORGE (R97) **[A]**; R116 NeuroTaint **[B]** | CLOSED |
| B4 | X creates a new attack surface | R104 (trusted monitors subverted) **[B]**; R93 (rollback attacks) **[A]** | CLOSED |
| B5 | X protects one agent but fails under composition | R100 SoK **[A]**; R121; R122; R103 | CLOSED |
| B6 | X fails when permissions change dynamically | R91 (delegation lifecycle, token theft/replay, revocation) **[A]**; R124 recovery consistency **[B]** | CLOSED |
| B7 | X assumes static tools | R107; R111; MCPTox (R06) | CLOSED |
| B8 | X assumes trustworthy tool descriptions | R111 (four MCP attack surfaces) **[B]**; MCPTox (R06) **[A]** | CLOSED |
| B9 | X cannot recover after compromise | R93, R94, R95, R123, R124 | **CLOSED (densely)** |
| B10 | X detects but cannot safely contain | R100 identifies "path closure" as a challenge → published challenge, not an open gap **[A]** | CLOSED |
| B11 | X blocks attacks but destroys utility | R97 reports the Progent residue **[A]**; R98 CAGE "keeping a useful fraction of decisions autonomous" **[A]** | CLOSED |
| B12 | X bypassed through cross-step interactions | R103 STAC **[B]**; R120 causal multi-step detection **[B]** | CLOSED |
| B13 | secure in isolation, insecure when composed with another agent | R100 **[A]**; R121 **[B]** | CLOSED |
| B14 | X assumes the agent's internal state is trustworthy | R94 (five failure modes incl. inconsistent internal state) **[A]** | CLOSED |
| B15 | X assumes tool results are truthful | R97/Progent limitation **[A]**; R116 **[B]** | CLOSED |
| B16 | X assumes the memory layer is trusted | R109 **[B]**; CAMS **[B]**; AWS/CockroachDB tenant-isolation guidance **[B]** | CLOSED |
| B17 | X assumes authorization decisions are static | R91 **[A]** | CLOSED |
| B18 | X assumes the attacker controls only one channel | R99 trust-boundary taxonomy **[A]**; R100 six interfaces **[A]** | CLOSED |

Two further structures were added by this phase and also fail:

| # | Additional structure | Occupying evidence | Status |
|---|---|---|---|
| B19 | **Reversibility is a property of the sequence, not the action** ("individually reversible actions compose into an irreversible effect") | Stated verbatim in **R99** (arXiv:2609.23700) **[B for the sentence]**; **R93** and **R95** already engineer around irreversible effects **[A]** | CLOSED |
| B20 | **The agent must not be able to influence its own enforcement plane** (policy/monitor/agent-definition tampering as a two-stage attack) | **R117** §4.1 protects installed agent definitions from tampering **[B]**; **R96** enforces at the kernel **[A]**; real-world instance is CVE-2026-82533 **[B]**; METR documents agents tampering with their own transcripts and a working tool-call-spoofing technique **[B]** | CLOSED |

**Part B result: 20 of 20 candidate gap structures are occupied. No structure survives with primary evidence.**

---

## Part C — Saturation test applied

For every candidate generated in Part L, the rejection test was: *does 2025–2026 literature already contain a comparable attack, defence, benchmark, architecture, or experiment?* No candidate was rejected merely because an older paper left "future work". In every case the killing citation is **2026**, and in five cases it is **September 2026** (R99 09-20, R100 09-01, R102 09-16, R91 08-31, R94 08-29).

---

## Parts D–J — Targeted probes (condensed)

* **Part D (compositional failures):** closed by R100/R121/R122/R103/R120 and, at the authorization layer, by the published non-composition theorem in R98 **[A]**.
* **Part E (temporal/stateful):** closed by R94/R109/R115/R116. Specifically, the "does the literature evaluate single interactions while real agents are stateful?" hypothesis is **false in 2026**: R94 is a systematic study of stateful recovery, R109 a systematic study of persistent-memory attacks.
* **Part F (recovery):** **the pivotal negative result of this phase.** The prior is that recovery is underdeveloped. The evidence says otherwise: two dedicated checkpoint/rollback *security* papers (R93 CoDAIM 2026; R94), one compensation/recovery paradigm at ACM CAIS 2026 (R95), a dedicated post-compromise IR benchmark (R123), a recovery-consistency property (R124), and R100 naming "path closure and recovery" as a systematized contract element rather than an empty space.
* **Part G (mechanisms):** every mechanism named in the brief is implemented and evaluated somewhere — see the matrix below.
* **Part H (MCP/tool ecosystem):** R111 enumerates four malicious-MCP attack surfaces; R107 does large-scale skill supply-chain measurement; MCPTox (R06) benchmarks the canonical attack; R91 supplies runtime confinement. The four-way trust-discrimination problem is addressed but **not as a distinct research contribution with a new phenomenon** — it is a union of existing mechanisms. This makes it a *MAJOR MODIFICATION*-class candidate at best (see C5/C6 below), not an OPEN one.
* **Part I (multi-agent):** closed by R91 + R100 + R106 + R119.
* **Part J (formal guarantees):** closed by R98 (certificate + non-composition proof), R92 (capture checking, local purity, noninterference), R96 (IFC DSL), AgentGuard/AgentSpec/VeriGuard/AgentVerify.

### Part G mechanism inventory

| Mechanism class | Proposed | Implemented | Evaluated on real agents | Documented failure |
|---|---|---|---|---|
| Capability tokens / authorization broker | R91 **[A]** | yes (VotalAI LLM Shield) | yes (2,000 scenarios) | none claimed by authors |
| Capture checking / capability-safe code | R92 **[A]** | yes (Scala 3) | yes (task-performance parity) | none claimed |
| Taint / IFC labels | CaMeL, FIDES, RTBAS, FORGE; R116 **[B]** | yes | yes (AgentDojo) | adaptive attacks (R97) |
| Symbolic per-call least privilege | Progent **[A via R97]** | yes | yes | no argument provenance **[A]** |
| OS-level policy/IFC mediation | R96 **[A]** | yes (eBPF) | yes; 1.9–8.4% overhead | agent declares the policies **[A]** |
| Certified authorization under return uncertainty | R98 **[A]** | yes (+ code) | yes (4 setting classes) | fidelity assumption for learned gates |
| Provenance bounds from prior runs | R101 **[B]** | yes | yes (IMC 2026) | uses an LLM judge for ambiguous cases |
| Tamper-evident provenance + risk gating | R113 **[B]** | claimed | not captured | not captured |
| Checkpoint/rollback safety | R93, R94 **[A]** | yes | yes (Hermes, Cline, LangGraph; 5 frameworks) | five failure modes remain |
| Compensation-based recovery | R95 **[A]** | yes (LangChain) | yes (τ-bench, REALM-Bench) | failure-driven, not adversary-driven |
| Verifiable human approval | R102 **[B]** | yes (agentic browser) | yes (24 scenarios) | not captured |
| Runtime verification | R110 **[B]**, AgentSpec | yes | yes | not captured |
| Kernel-grade complete mediation | R99 (agenda) **[A]** | partly (R96, R117) | partly | declared *irreducible residual* **[A]** |

**Empty rows: none.** That is the operational definition of a saturated mechanism space.

---

## Part K — Resource feasibility (re-applied)

Available (settled in Phase 6 from vendor sources): `deepseek-flash` (thinking default, temperature ignored), `glm-5.3-flash` (320B/18B, thinking cannot be disabled), MiMo 2.6 Flash (specs aggregator-only, **B/C**), Solar Mini 4 (released ~2026-09-22 — too new). No frontier tier; no sampling control.

Two feasibility filters applied to every candidate:

1. **Model-agnostic architecture.** Passed by all ten candidates. None required training or capability-ranking.
2. **No white-box access requirement.** **This is the decisive filter.** R97's own honest limitation is that "a stronger optimized (**white-box GCG**) attack remains open"; it ran its adaptive reproduction with a **self-hosted open-weight Qwen2.5-7B on a single H200**. Any candidate whose novelty claim rests on *defeating* the out-of-band enforcement family therefore requires either white-box gradients over a self-hosted open model with GPU access we do not have, or frontier-model adaptive attacks we cannot run. **[INFER]** Two candidates (C1 and C2) failed on this filter *in addition to* being closed.

**Part K result: even if a candidate had survived Parts C/M, the residual novelty in this space would sit behind a white-box/GPU requirement that our resource profile cannot meet.** This is a second, independent reason for the NO-GO.

---

## Part L — Ten candidates

Each candidate is stated in its strongest form. Fields 1–19 as required. No ranking is implied by numbering.

### C1 — Reversibility-Compositional Authorization (aggregate-reversibility gating)
1. **Title:** Reversibility-Compositional Authorization for Tool-Using Agents.
2. **Core problem:** per-action authorisation cannot see that a sequence of individually reversible, individually authorised actions composes into an irreversible effect.
3. **Threat model:** attacker controls one untrusted input channel; holds no credentials; cannot modify the agent's policy store; can choose injected content adaptively.
4. **SOTA:** Progent (per-call rules); R93 ACRFence (records irreversible effects, replay-or-fork on restore); R95 RAC (compensation log).
5. **Closest papers:** R93 (arXiv:2603.20625), R94 (arXiv:2608.29381), R95 (arXiv:2605.03409), Progent (via R97), R92 (arXiv:2603.00991).
6. **Exact gap claimed:** no system computes a *sequence-level* reversibility class or gates on it.
7. **Mechanism:** propagate a reversibility lattice over the effect graph of the transcript; deny any transition whose cumulative class is irreversible while untrusted-derived.
8. **Security property:** "no irreversible effect may depend on untrusted-derived state unless a human authorises that specific effect."
9. **Experiment:** measure composition-induced irreversibility rate on AgentDojo-style tasks; compare ASR and utility against Progent and against a per-action reversibility gate.
10. **Models:** any tool-calling model.
11. **Infrastructure:** AgentDojo + a reversibility-annotated tool set.
12. **Cost:** low.
13. **Why existing defences fail:** Progent has no provenance; taint systems (CaMeL/FIDES/R116) have no reversibility model.
14. **Why interesting:** it is a genuine information-flow property over an effect graph.
15. **Novelty confidence:** low.
16. **Resource feasibility:** good.
17. **Reproducibility:** good.
18. **Reviewer objection:** "This is Biba integrity plus a lattice annotation; the interesting case (an irreversible action composed from reversible ones) is a standard transitive-closure result."
19. **Falsification:** if a per-action gate with argument provenance achieves the same sequence-level property, C1 has no content.
**Kill: CLOSED (see M1).**

### C2 — Argument-Provenance-scoped Authorization
1. **Title:** Provenance of the Argument, Not the Context.
2. **Core problem:** existing gates either check a tool call's name/arguments without provenance (Progent) or label the whole context (coarse IFC).
3. **Threat model:** as C1.
4. **SOTA:** R97 documents the exact crack: *"Progent's proxy checks tool-call names and arguments; it does not track the provenance of the data those arguments derive from"* **[A]**.
5. **Closest papers:** R97, R116 NeuroTaint, CaMeL, FIDES, RTBAS.
6. **Exact gap:** combine symbolic per-call rules with value-level provenance so autonomy is preserved.
7. **Mechanism:** per-argument provenance resolver feeding a symbolic policy engine.
8. **Security property:** "authorization decisions are a function of (rule, argument provenance), never of context labels alone."
9. **Experiment:** ASR/utility frontier vs Progent, CaMeL, FIDES on AgentDojo.
10.–12. Models/infra/cost: any tool-calling model; AgentDojo; low.
13. **Why existing defences fail:** Progent lacks provenance; IFC systems lack per-call symbolic rules.
14. **Why interesting:** precision/autonomy trade-off is a measurable systems quantity.
15. **Novelty confidence:** low.
16. **Resource feasibility:** good.
17. **Reproducibility:** good.
18. **Reviewer objection:** "This is the intersection of two published systems. It is an integration, not a phenomenon, and its evaluation is a benchmark comparison of exactly the kind the field has already systematized."
19. **Falsification:** if NeuroTaint or CaMeL already resolves per-argument provenance, nothing remains.
**Kill: CLOSED (see M2).**

### C3 — Enforcement-Plane Integrity (the agent must not reach its own control plane)
1. **Title:** Unreachable Policy: Separating the Agent's Effect Set from its Enforcement Plane.
2. **Core problem:** a compromised agent can *subvert the defence* instead of defeating it — weaken a guardrail, edit a policy, spoof a receipt — then act.
3. **Threat model:** prompt-injected agent with legitimate tool access; no OS privilege; attacker does not know the policy.
4. **SOTA:** R117 §4.1 (agent-definition tamper protection), R96 (kernel enforcement), R91 (authorization broker outside the model).
5. **Closest papers:** R117 (arXiv:2606.26924), R96 (arXiv:2606.25189), R99 (arXiv:2609.23700), R91.
6. **Exact gap:** nobody *measures* policy-plane reachability across real deployments or proves its absence.
7. **Mechanism:** static reachability analysis over the tool graph producing a *policy-plane disjointness* certificate, plus a runtime guard.
8. **Security property:** "no action reachable from the agent may write to the policy plane."
9. **Experiment:** audit N real agent deployments for policy-plane reachability; measure two-stage attack success with and without the guard.
10.–12. Models/infra/cost: any; open framework corpus (LangGraph/CrewAI/AutoGen); low.
13. **Why existing defences fail:** tool-call interception misses indirect execution paths (R96) and agent-declared policies are writable by design (R96).
14. **Why interesting:** converts "defence subversion" into a checkable static invariant.
15. **Novelty confidence:** low-moderate.
16. **Resource feasibility:** good.
17. **Reproducibility:** good.
18. **Reviewer objection:** "This is privilege separation with a static analysis. The interesting finding (agents can edit their own config) is a CVE, not a research result; and R117 §4.1 plus ActPlane already protect the plane."
19. **Falsification:** if the audited frameworks are already policy-plane-disjoint, there is nothing to report.
**Kill: CLOSED (see M3).**

### C4 — Defence-Interaction / Compositional-Defence Security
**Core problem:** two individually validated defences may be jointly weaker than either alone.
**Closest papers:** R121 Interaction-Barrier Shielding; R100 SoK; R99; R97.
**Mechanism:** a defence-interaction test harness with interference taxonomy.
**Kill: CLOSED.** R100 explicitly warns that "without an execution-level view, a multi-agent setting can easily be mistaken for **evidence of a genuinely multi-agent security effect**" **[A]**, and R121 already builds a shield *because* "many agent attacks are unsafe only in capability combinations". A defence-interaction study is also evaluation-shaped and would re-enter rejected direction 7.

### C5 — Tool-Identity Attestation (trusted vs compromised vs malicious-output vs poisoned-description)
**Core problem:** four distinct trust states are indistinguishable to the agent.
**Closest papers:** R111 (four MCP attack surfaces) **[B]**; R107 **[B]**; MCPTox (R06) **[A]**; R91 **[A]**; R112/R113 (provenance).
**Mechanism:** signed tool manifests + per-call output provenance envelopes + drift detection.
**Kill: MAJOR MODIFICATION → not a survivor.** The discrimination problem is attacked from three independent 2026 directions; the residual is a *union of existing mechanisms* (signing + taint + drift), which is an engineering integration. Recall that Phase 3 already rejected "unified ASR oracle" for exactly this reason: composing existing components into one artifact is not a new phenomenon.

### C6 — Cross-Principal Agent-Memory Isolation
**Core problem:** pooled agent memory leaks across tenants/principals.
**Closest papers:** R109 (memory poisoning systematic study) **[B]**; CAMS **[B]**; vendor architectures (AWS AgentCore hierarchical namespaces, CockroachDB row-level isolation) **[B]**.
**Kill: MAJOR MODIFICATION → not a survivor.** This is the one area where the search returned mostly *vendor* material rather than peer-reviewed work — which is a genuine observation and worth recording. But (i) it is ordinary access control at a datastore boundary, (ii) a production platform already ships the isolation primitive, and (iii) it is application-shaped: it would be an "application-only paper", which the brief forbids. **Recorded as the strongest *residual* observation of the phase, not as a research candidate.**

### C7 — Non-repudiable Action Receipts for Agents
**Core problem:** third-party verification of "what did this agent do and under whose authority", without trusting the agent's own logs.
**Closest papers:** R113 TraceCaps (tamper-evident provenance) **[B]**; R101 Agent-Sentry **[B]**; R112 survey **[B]**; METR's tool-call-spoofing finding **[B]**.
**Kill: CLOSED.** Tamper-evident provenance plus risk enforcement is published as a system (R113), and the survey layer already exists (R112). The METR finding sharpens the problem statement but does not create a gap.

### C8 — Distributed/Split-Payload Attacks against Per-Step Monitors
**Core problem:** an attack distributed across steps so that each step is individually benign under a per-step monitor.
**Closest papers:** R103 STAC ("enforces that every intermediate step appears individually benign") **[B]**; R120 causal detection of multi-step attacks **[B]**; StepJack (splitting one attack across pages) **[B]**; R115 long-horizon self-evolving injection **[B]**; AgentLAB **[B]**.
**Kill: CLOSED.** At least one prevention system and one detection system target precisely this composition, and StepJack already demonstrates the split-payload primitive.

### C9 — Certified Adaptive Robustness (a defence with a checkable certificate against an adaptive class)
**Core problem:** every published defence is validated on a static attack set.
**Closest papers:** R97 (adaptive-evaluation protocol + a reproduction) **[A]**; R104 **[B]**; R98 CAGE (a *certificate*, and a non-composition proof) **[A]**; R99 (argues the residual is irreducible) **[A]**.
**Kill: CLOSED and DOUBLE-EXCLUDED.** The protocol is published (R97); the certificate machinery exists (R98); the impossibility framing is systematized (R99); and the contribution would be evaluation methodology, i.e. rejected direction 7. Additionally, the residual open problem R97 itself names requires **white-box GCG**, which fails Part K.

### C10 — Continuity-Aware Recovery (secure resumption after compromise)
**Core problem:** a correctly restored checkpoint may resume an execution whose state, assumptions and external effects never coexisted.
**Closest papers:** R94 (five failure modes; three end-to-end attacks on Hermes, Cline, LangGraph; multi-agent analysis pipeline across five frameworks) **[A]**; R93 ACRFence **[A]**; R95 RAC **[A]**; R123 SecRespond **[B]**; R124 recovery-consistency property **[B]**.
**Kill: CLOSED — the most decisive closure of the phase.** R94 *is* the paper this candidate would write, with the same motivating sentence ("Correct rollback does not imply secure recovery"), a failure taxonomy, three end-to-end attacks on three real frameworks, an analysis pipeline, and a five-framework evaluation.

---

## Part M — Hostile kills

| # | Candidate | Verdict | Killing evidence (all 2025–2026) |
|---|---|---|---|
| M1 | C1 Reversibility-Compositional Authorization | **CLOSED** | **R99** states the composition result verbatim ("Individually reversible actions can compose into an irreversible effect, so reversibility is a property of the action sequence") **[B]**; R93/R95 already engineer irreversible-effect handling **[A]**. Additional kill: requires no frontier model — but also adds no phenomenon beyond transitive closure over a lattice. |
| M2 | C2 Argument-Provenance-scoped Authorization | **CLOSED** | **R116 NeuroTaint** is described as "the first comprehensive taint tracking framework tailored for the unique information flow characteristics of LLM agents" **[B]**; CaMeL/FIDES/RTBAS/FORGE already label values (R97) **[A]**; Progent already checks arguments (R97) **[A]**. The union is an integration. |
| M3 | C3 Enforcement-Plane Integrity | **CLOSED** | **R117** §4.1 already "protect[s] this project's installed agent definitions from tampering" **[B]**; **R96 ActPlane** enforces at the kernel with 1.9–8.4% overhead **[A]**; the real-world instance is CVE-2026-82533 **[B]**; METR documents agent transcript tampering and tool-call spoofing **[B]**. A reviewer classifies the audit as vulnerability discovery. |
| M4 | C4 Defence-Interaction Security | **CLOSED** | R100's execution-level caution **[A]**; R121's interaction-barrier shield **[B]**; and it re-enters rejected direction 7. |
| M5 | C5 Tool-Identity Attestation | **MAJOR MODIFICATION** | R111, R107, R06, R91 cover three of the four trust states; residual is a mechanism union. Not a survivor. |
| M6 | C6 Cross-Principal Memory Isolation | **MAJOR MODIFICATION** | Vendor-level saturation plus standard access control; application-shaped. Not a survivor. **But note: this is the only area where peer-reviewed coverage was thinner than vendor coverage — the single genuinely informative residual of the phase.** |
| M7 | C7 Non-repudiable Action Receipts | **CLOSED** | R113 (tamper-evident provenance + risk enforcement) **[B]**; R112 (survey) **[B]**; R101 (provenance-bounded execution, IMC 2026) **[B]**. |
| M8 | C8 Split-Payload Attacks on Per-Step Monitors | **CLOSED** | R103 STAC **[B]**; R120 causal multi-step detection **[B]**; StepJack **[B]**; R115 **[B]**. |
| M9 | C9 Certified Adaptive Robustness | **CLOSED (double-excluded)** | R97 **[A]**; R104 **[B]**; R98 certificate + non-composition theorem **[A]**; R99 declares the residual **[A]**; and it is evaluation methodology (rejected direction 7). Fails Part K (needs white-box GCG). |
| M10 | C10 Continuity-Aware Recovery | **CLOSED** | R94 is the same paper with stronger evidence (5 frameworks, 3 attacks) **[A]**; R93, R95, R123, R124 corroborate **[A/B]**. |

**Part M result: 8 CLOSED, 2 MAJOR MODIFICATION, 0 OPEN.**

---

## Part N — Survivors

**NO SURVIVOR.**

No candidate is marked OPEN. The two MAJOR MODIFICATION candidates (C5, C6) are not promoted, because promotion would require treating a mechanism union or an application-shaped access-control gap as a new security phenomenon, which is exactly the failure mode the brief tells us to avoid ("Do not force a winner").

Recorded for the record, and *not* recommended as a research topic:

* **C5** could become a paper as a *systems* contribution ("one runtime that discriminates four tool-trust states, evaluated end-to-end") — but the security property is the union of signing, taint and drift detection, and the paper's evidence would be benchmark-shaped. **Not recommended.**
* **C6** is the only area where peer-reviewed work was notably thinner than vendor practice. If a future phase wants to revisit agent security, this is the least-crowded corner — but it is a multi-tenant access-control problem, not an agent-security mechanism, and it would be an applied/application paper. **Not recommended as-is.**

---

## Part O — Design of the best surviving direction

**Not applicable: no candidate survived Part N.** Per the brief, Part O is executed only if at least one candidate survives. Providing a design here would manufacture the novelty this phase exists to test, so it is deliberately left empty.

---

## Part P — Required novel security guarantee

**Not applicable for the same reason.** For completeness, the invariant that C3 would have offered — *"no action reachable from the agent may write to the policy plane"* — **is** automatically checkable (static reachability over the tool graph, plus a runtime guard). This is recorded because the *checkability* finding is reusable: a future phase should prefer candidates whose security property is a **static, decidable relation** rather than a statistical claim, since only the former escapes both the measurement-saturation of Phases 1–7 and the mechanism-saturation documented here. But R117 §4.1 already implements the control, so checkability alone does not rescue the candidate.

---

## Part Q — Venue/paper potential

**Not applicable: no survivor.** For the two near-misses, honestly assessed and without any claim about acceptance:

* **C5** would be a **systems/security engineering** submission whose evidence requirement is: ≥2 real frameworks, ≥4 tool-trust states exercised end-to-end, adaptive attacker, utility cost. The blocker is not feasibility but **contribution type** — the reviewers would ask for the *new phenomenon*, and there is none.
* **C6** would be an **applied/industry** paper. Evidence requirement: a measured cross-principal leakage rate in a real pooled deployment plus a mechanism with a utility cost. The blocker is that the primitive already ships in a production platform.
* **Minimum bar for any future Phase-8-style candidate to be worth a deep audit:** a security property that is (i) statically decidable or provable, (ii) not derivable as a union of the mechanisms in the Part-G inventory, and (iii) demonstrable on a corpus of real open-source agent frameworks without GPU/white-box access.

---

## Part R — Final decision

# NO-GO — NO CANDIDATE SURVIVES

No candidate is promoted to the next audit. Zero survivors. The brief states explicitly that "If everything is closed, that is a successful research result"; this is that result.

**Why this is the correct verdict rather than a failure of search effort.** Twenty distinct gap structures derived from the brief (Part B) were each matched against primary 2025–2026 evidence and each was occupied. Fifteen security areas (Part A) were searched, and every one returned a 2026 primary paper, and twelve returned an additional systematization. The decisive sources are not old papers with stale "future work" clauses — they are:

| Source | Date | What it closes |
|---|---|---|
| R99 arXiv:2609.23700 | 2026-09-20 | Complete-mediation framing; provenance-vs-content distinction; monitoring/separation/authorization taxonomy; reversibility composition; declares the irreducible residual |
| R100 arXiv:2609.00595 | 2026-09-01 | Compositional/multi-agent security (197 works); defence contract incl. recovery; execution-level view |
| R102 arXiv:2609.18411 | 2026-09-16 | Human-approval integrity (Verifiable Action Card) |
| R91 arXiv:2609.00267 | 2026-08-31 | Delegation/identity/authorization confinement, with implementation and adversarial evaluation |
| R94 arXiv:2608.29381 | 2026-08-29 | Checkpoint/rollback security as a first systematic study, five frameworks |
| R98 arXiv:2607.29190 | 2026-07-31 | Certified authorization + a published non-composition theorem |
| R97 arXiv:2606.26479 | 2026-06-25 | The out-of-band defence family systematized as Biba+reference monitoring+least privilege; adaptive-evaluation protocol |
| R96 arXiv:2606.25189 | 2026-06-23 | OS-level policy plane for agent harnesses (eBPF, IFC DSL) |
| R92 arXiv:2603.00991 | 2026-03-01 (rev. 05-07) | Capability/capture-checking safety harness with local purity |
| R93 arXiv:2603.20625 | 2026-03-21 | Semantic rollback attacks + replay-or-fork mitigation |

**Two independent, additive reasons for NO-GO:**
1. **Novelty:** every candidate is either CLOSED by a 2026 primary source or reduces to a union of already-implemented mechanisms.
2. **Feasibility (Part K):** the only surviving residual novelty in this space — breaking deterministic out-of-band enforcement under a *stronger optimized* adaptive attacker — is explicitly named as open by R97 and requires **white-box GCG over a self-hosted open-weight model on GPU hardware we do not have**. So even a hypothetical survivor would fail the resource filter.

---

## Part S — Source registry and artifacts

### S.1 New sources registered in Phase 8

`research/tables/sources.csv` extended from **R90 → R126** (36 new rows). New primary sources with verification labels:

**Label A (fetched and read at source — abstract level):**
R91 arXiv:2609.00267 · R92 arXiv:2603.00991 · R93 arXiv:2603.20625 · R94 arXiv:2608.29381 · R95 arXiv:2605.03409 · R96 arXiv:2606.25189 · R97 arXiv:2606.26479 · R98 arXiv:2607.29190 · R99 arXiv:2609.23700 · R100 arXiv:2609.00595

**Label B (snippet, third-party listing, or another paper's summary — do not quote figures):**
R101 arXiv:2603.22868 (Agent-Sentry, IMC 2026) · R102 arXiv:2609.18411 (Verifiable Action Card) · R103 arXiv:2509.25624 (STAC) · R104 arXiv:2510.09462 (Adaptive Attacks on Trusted Monitors) · R105 arXiv:2603.14707 (Visual Confused Deputy) · R106 arXiv:2604.25189 (AgentDID) · R107 arXiv:2602.06547 (Malicious Agent Skills in the Wild) · R108 arXiv:2510.07505 (PEAR) · R109 arXiv:2606.04329 (memory poisoning systematic study) · R110 arXiv:2509.23864 (AgentGuard) · R111 MDPI *Electronics* 15(10):2214 (Beyond Tool Poisoning) · R112 arXiv:2606.04990 (evidence-tracing survey) · R113 DOI 10.1145/3786582.3786832 (TraceCaps) · R114 arXiv:2607.05743 (execution-security systematization) · R115 arXiv:2608.30441 (self-evolving long-horizon injection) · R116 arXiv:2604.23374 (NeuroTaint) · R117 arXiv:2606.26924 (deterministic control plane for coding agents) · R118 arXiv:2605.24309 (agent–human interaction reframing) · R119 arXiv:2505.02077 (secure systems of interacting agents) · R120 OpenReview Kb2m543agS (causal multi-step detection) · R121 OpenReview v2QHWcC0UC (interaction-barrier shielding) · R122 arXiv:2608.08131 (compositional threat analysis) · R123 arXiv:2607.26791 (SecRespond) · R124 ResearchSquare rs-10533072 (delegation-aware runtime contracts) · R125 metr.org blog 2026-08-26 (agent transcript tampering / tool-call spoofing) · R126 "Agents Rule of Two" (Meta; **identifier not captured — do not cite**)

**Already registered (not duplicated):** MCPTox = **R06**; Agent Security Bench = **R02**.

### S.2 Artifacts created/updated in Phase 8

* **Created:** `research/08-agent-security-research-opportunity-map.md` (this file)
* **Created:** `research/tables/research-opportunity-matrix.csv` (source-oriented, 17 fields as specified in Part S)
* **Updated:** `research/tables/sources.csv` (R91–R126 appended; existing 11-field schema and 11-field row width preserved)
* **Validated:** both CSVs parsed with the standard inline node RFC4180 parser — header width, row count, `unterminatedQuote` flag, malformed-row indices, duplicate IDs.

### S.3 Corrections and cautions carried forward

* **R53 is SUPERSEDED BY R77** (REDAgentBench, abstract-only pass-3 entry).
* **Pathade et al. = R52**, not R68 (R68 is SafeBoundary-LLM).
* **Maloyan & Namiot conflation warning:** arXiv:2604.18333 (judge prompt injection) ≠ arXiv:2601.17548 (agentic coding assistants). Two distinct papers.
* **Nasr et al., "The attacker moves second"** (USENIX Security, cited by R77) is *likely* the same work as **R48** (arXiv:2510.09023); identity **not asserted** — confirm before merging.
* **"Agents Rule of Two"** is used in this phase only as a *design principle* that candidates must beat; **no citation of it is permitted** until a primary source is fetched (R126, label B, identifier not captured).
* No figure taken from a label-B source appears in this document.

---

## Part T — What would change the verdict (handoff for a future phase)

The NO-GO is specific, not general. It says: *as of 25 September 2026, in the fifteen areas mapped in Part A, using the four flash-tier models available, no fundamentally different agent-security mechanism/attack problem survives.* It would be overturned by any one of the following, and a future phase should be pointed at these rather than at the space again:

1. **A construction, not a gap.** Not "X fails after Y" — instead a *deterministic mediator* for a class that R99 declares has no such mediator ("wherever inputs and actions are not restricted in advance to an enumerated set"). R99 commits to the claim that this residual is irreducible; a counter-construction is a genuine scientific contribution. Our searches found no such construction, and our resource profile cannot build one that depends on white-box adversarial optimisation.
2. **A cross-principal boundary at a layer nobody has systematized.** C6 was the only area where vendor material outweighed primary literature. If it is to be pursued at all, it must be framed as a *mechanism* with a decidable property — not as tenant isolation.
3. **A property about the agent's relationship to its own records** that is provable rather than detected. METR's tool-call-spoofing finding and CVE-2026-82533 both point at "the agent can lie about what it did", which R113/R101/R117 cover from three sides — so this needs a *new* decidable property, not another log.
4. **A resource change.** Access to a self-hosted open-weight model with GPU capacity would re-open R97's explicitly-stated white-box residual. Until then, that residual is out of reach.

**Recommended next action for the project (not a research topic, a process note):** stop generating new security directions in this space and instead convert the eight existing phase deliverables into a *negative-results + saturation map* artifact — the seven rejected directions plus this phase's mechanism-saturation inventory are themselves a citable account of where the 2026 agent-security field is crowded. That is a defensible contribution of a different kind, and it is the honest use of what has been established.

---

## Verdict summary

| Part | Result |
|---|---|
| A — Landscape | 15 areas mapped; all occupied; 12 have a dedicated 2026 systematization |
| B — Uncomfortable gaps | 20 structures examined; 20 CLOSED |
| C — Saturation test | Applied; all kills are 2026 sources, five from September 2026 |
| D — Compositional | CLOSED (R100, R121, R122, R103, R120, and the non-composition theorem in R98) |
| E — Temporal/stateful | CLOSED (R94, R109, R115, R116) |
| F — Recovery | **CLOSED densely** (R93, R94, R95, R123, R124) — the phase's pivotal negative result |
| G — Mechanisms | 13 mechanism classes; no empty row |
| H — MCP/tool ecosystem | CLOSED (R111, R107, R06, R91) |
| I — Multi-agent | CLOSED (R91, R100, R106, R119) |
| J — Formal guarantees | CLOSED (R98 certificate + non-composition proof; R92 local purity) |
| K — Resource feasibility | Two candidates failed an *additional* white-box/GPU filter |
| L — Candidates | 10 generated |
| M — Hostile kills | 8 CLOSED, 2 MAJOR MODIFICATION, 0 OPEN |
| N — Survivors | **NO SURVIVOR** |
| O/P/Q | Not applicable (no survivor) |
| R — Decision | **NO-GO** |

SEARCH COMPLETE — SURVIVORS: 0
