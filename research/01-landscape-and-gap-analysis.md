# AgentSec Lab — Research Landscape and Research-Gap Analysis

**Document type:** Research discovery document (pre-paper).
**Status:** Working draft v0.1. **Not** an abstract, introduction, methodology, results or conclusion. No novelty claims are made here.
**Date compiled:** 2026-09-25.
**Companion files:** `research/tables/benchmark-comparison.csv`, `research/tables/gap-matrix.csv`, `research/tables/sources.csv`.

---

## 0. Method, evidentiary discipline and self-imposed rules

### 0.1 What this document is

This is an evidence-gathering and orientation artefact. It exists to decide *what is already known*, *what is contested*, and *what would be worth doing*. It deliberately withholds the framing that a paper would use.

### 0.2 How sources were gathered

1. Targeted web search across the named topics (§1 A–Q).
2. **Primary-source retrieval for every load-bearing claim.** For the core benchmarks I fetched the arXiv abstract page (which reports submission date, version history, and the authors' own venue statement in the `Comments` field) and, where relevant, the publisher or proceedings page. For a few items I fetched the standards draft or repository page directly.
3. **No citation is included that I did not see at the source or in a clearly attributable secondary location.** In the latter case the entry is labelled *secondary*.

### 0.3 Verification labels used throughout

| Label | Meaning |
|---|---|
| **A** | Authoritative primary source fetched in this session (arXiv abs page, publisher/proceedings page, standards draft, repository or dataset page). |
| **B** | Traceable secondary source only (e.g. an authoritative site reporting a venue, a survey citing it). Details not confirmed at source. |
| **C** | Claim could not be verified during this pass. **Not usable in the final paper without re-checking.** |

Items marked **C** must be resolved before they enter a manuscript. Items marked **B** require at least one confirmation at source.

### 0.4 Explicit non-fabrication commitments

- No numeric result in this document was estimated, interpolated, or reconstructed from memory. Where a number appears it is quoted from a source and labelled.
- Where a benchmark comparison field is not known, it is written **`not reported`** or **`unverified`**. It is never filled by inference from "what a benchmark of that type would probably do".
- No claim is made that a venue accepted a paper unless the authors' own arXiv `Comments` field or a proceedings page states it.
- Model capability claims are absent by design; the only model facts recorded are *existence*, *provider* and *published configuration metadata*.

### 0.5 What "not reported" means in the tables

`not reported` = the information is not present in the primary source I fetched.
`unverified` = the information likely exists in the full text but I did not confirm it.
These are distinct. `not reported` is *weak* evidence of absence; `unverified` is *no* evidence.

### 0.6 Known limitations of this pass

- Most entries are based on **abstract-level** evidence, not full-text reading. The gap matrix is therefore **provisional** and must be re-derived from full texts before it is used to justify a publication claim. A row-level `evidence_level` column is provided in `research/tables/gap-matrix.csv`.
- Coverage is English-language and skewed toward arXiv, ACL/NeurIPS/ICLR/USENIX/ICML. Non-English venues and industry disclosures are under-sampled.
- Search-engine indexing is not exhaustive; a systematic database search (Scopus/Web of Science/ACM DL/IEEE Xplore) with a documented query string is still required.

---

## A. Executive research landscape summary

### A.1 The field in one paragraph

Agent security matured during 2023–2026 from "prompt injection is possible" to a structured, benchmarked subfield with dedicated academic evaluation suites (InjecAgent, AgentDojo, ASB, RAS-Eval, Agent-SafetyBench, AgentHarm, ST-WebAgentBench, WASP, AgentDyn, MCPTox), a large defence literature, and — most recently — *framework-level* standardisation efforts (OWASP agentic guidance; an IETF BMWG benchmark framework draft). The epistemological centre of gravity has shifted twice: first from *attacks* to *defences*, then from *defences* to *whether the evaluations of defences are themselves trustworthy*. The most recent, and analytically sharpest, contributions are meta-evaluations: they show that most defences fail under adaptive attack (Zhan et al., arXiv:2503.00061, **A**), that most defences either under-protect or over-block in dynamic settings (AgentDyn, arXiv:2602.03117, **A**), and that agent benchmark scores are not credible without analysis of execution logs (Kirgis et al., arXiv:2605.08545, **A**).

### A.2 Where the field is dense (do not add value here)

- Cataloguing prompt-injection attack strings for tool-using agents.
- Demonstrating that an indirect prompt injection can hijack a tool call.
- Producing one more "we ran N models and they were vulnerable" evaluation.
- Demonstrating memory poisoning or RAG-corpus poisoning *exists*. Several works establish this with strong evidence.

### A.3 Where the field is thin (potential value)

1. **Cost is not a first-class evaluation axis.** Security and utility are jointly measured in several benchmarks; the *price* of the security–utility frontier (tokens, latency, monetary cost, defence overhead, number of independent model calls) is essentially absent as a systematically reported, cross-model quantity. See §D and §E.
2. **Contested empirical findings are not being resolved.** Two credible benchmark papers report *opposite* relationships between model capability and attack susceptibility (MCPTox, arXiv:2508.14925, **A**, vs RAS-Eval, arXiv:2506.15352, **A**). This contradiction is currently unexamined and is a strong, cheap, falsifiable research target.
3. **Experiment logs are almost never released.** Benchmarks release code and datasets; they do not release the per-step traces and raw model responses that would let an independent party re-derive scores without paying for inference.
4. **Adaptive attackers are described, not calibrated.** Adaptive attack is acknowledged as necessary (AgentDojo is explicitly built to host adaptive attacks, **A**) and shown to be decisive (Zhan et al. **A**), but the attacker's *budget* is not treated as a controlled experimental variable.

### A.4 One important negative result from this search

The research theme as stated by the project — *"reproducible, adaptive, multi-model security evaluation … with explicit measurement of security, utility, and operational cost"* — is **not** an empty space. Its first three adjectives are addressed by AgentDojo (adaptive, extensible), ASB (broad attack/defence grid), RAS-Eval (multi-model, real tool execution) and AgentDyn (adaptive defence evaluation in dynamic environments). The theme's differentiating element, if there is one, is the **joint, quantitative treatment of cost alongside security and utility, executed in a way that is independently re-derivable**. That is a narrower claim than the theme suggests, and the narrowing is worth taking seriously rather than resisting.

---

## B / §1. Literature analysis by topic

For each topic: what is established, what is contested, and the load-bearing sources.

### 1A. LLM-based agent security (overview)

Community surveys and framework documents now exist. The genuinely useful ones for a paper's related-work section are those that (i) define a threat taxonomy and (ii) discuss evaluation. I identify: a large-scale LLM/agent full-stack safety survey (arXiv:2504.15585, **B**); "A Survey on Agentic Security: Applications, Threats and Defenses" (arXiv:2510.06445, **B**); "Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges" (arXiv:2510.23883, **B**); and a taxonomy/consistency analysis of agent safety benchmarks (arXiv:2605.16282, **B**) which explicitly compares benchmark coverage — this last one is close to part of §2 and must be read in full before §2 is finalised for publication, to avoid re-deriving an existing comparison.

**Caveat:** all four are **B**. Two of them appear in some bibliographies as journal/conference papers (one listing places arXiv:2510.23883 in *IEEE Access* 2026) — **unverified**, do not cite the venue.

### 1B. AI-agent security benchmarks

Dense and actively contested. Established: InjecAgent (1,054 cases, ACL 2024 Findings, **A**), AgentDojo (97 tasks / 629 security cases, NeurIPS 2024 D&B, **A**), ASB (10 scenarios, >400 tools, 27 attack/defence methods, 7 metrics, ICLR 2025, **A**), RAS-Eval (80 cases / 3,802 attack tasks mapped to 11 CWE categories, **A**), Agent-SafetyBench (349 environments / 2,000 cases, **A**), AgentHarm (110 tasks / 440 with augmentations, **B**), ST-WebAgentBench (**B**), WASP (**B**), MCPTox (45 live MCP servers / 353 tools / 1,312 cases, **A**), AgentDyn (60 tasks / 560 injection cases, **A**).

Contested: *what a benchmark score means*. AgentDyn asserts three "fundamental flaws" in prior benchmarks — no dynamic open-ended tasks, no helpful (benign but instruction-bearing) third-party content, and over-simplistic user tasks (**A**). Kirgis et al. argue the scoring layer itself is the problem, that pass/fail outcomes can be inflated or deflated by shortcuts and artefacts, and that outcome metrics can conceal dangerous actions (**A**). Together these two are the strongest available evidence that *benchmark validity*, not benchmark coverage, is the current frontier.

### 1C. Prompt injection (direct)

Foundational and saturated at the direct-injection level; treat as background only. The academically load-bearing move was reframing injection as a *data-vs-instruction confusion* problem rather than a jailbreak problem (**B** for the earliest formulations). Direct injection is not a productive axis for new work.

### 1D. Indirect prompt injection (IPI)

The core threat model for real agents. Established beyond dispute: untrusted tool-returned content can hijack agent behaviour (InjecAgent **A**; AgentDojo **A**). What is *not* settled is the defensive record — see 1K.

One under-appreciated methodological problem: **payload publication drives payload decay.** Every benchmark that publishes its injection strings also, in effect, donates them to future training corpora. Attack success rates measured on a public benchmark at time *t* are therefore not necessarily comparable to rates measured at time *t+Δ*, even holding the model fixed. I found this concern raised in practitioner commentary (**B**) but **not** treated as a first-class measurement problem in any benchmark paper I verified. Treat as a candidate measurement-science gap (§E, gap 5) but note the weak evidentiary base — this needs either a real decay measurement or careful modelling, not rhetoric.

### 1E. Tool misuse / unsafe tool invocation

Established by ToolEmu (36 high-stakes tools, 144 test cases; LM-emulated tool execution; 68.8% of LM-identified failures judged valid by human review; safest agent still fails 23.9%, **A**) and by Agent-SafetyBench (none of 16 agents above a 60% safety score, **A**). Tool misuse is also the mechanism class in MCPTox (**A**) and in the privilege-control literature (1K below).

### 1F. Memory poisoning

Well established as a *phenomenon*: AgentPoison (first backdoor against generic RAG-equipped agents via long-term memory or knowledge-base poisoning; no fine-tuning required; NeurIPS 2024, **A** for venue and abstract via proceedings), MINJA (memory injection via **query-only** interaction, i.e. without direct write access to the memory bank; **B** — abstract text seen, arXiv abs page not fetched this pass), ASB (includes one memory-poisoning attack among its 27 methods, **A**).

Weakly addressed as a *benchmark dimension*: memory appears as one attack within ASB, and as the object of dedicated attack papers, but I did not find a benchmark in which persistent, cross-session memory is a **first-class evaluation surface jointly scored for security, utility and cost**. This is a narrower and more defensible claim than "memory poisoning is unexplored" — which would be false.

### 1G. RAG poisoning

Established with unusual clarity: PoisonedRAG (USENIX Security 2025) reports up to 90% attack success by injecting five malicious texts per target question into a large knowledge database (**A**). AgentPoison covers the agent-memory variant (**A**). There is a dedicated journal literature continuing this thread (**B**). Like 1F, the *attack* is well covered; the *joint evaluation surface* is not.

### 1H. Data leakage in agents

Covered as an attack *intention* in InjecAgent (direct harm vs private-data exfiltration, **A**) and as a central concern in the information-flow-control defence line (CaMeL, **B**; design patterns, **B**; Progent, **A**). A dedicated survey on agentic data leakage and privacy failure exists (**B**). Not a promising standalone axis.

### 1I. Excessive agency / excessive autonomy

Present in the practitioner frameworks rather than the academic benchmarks. OWASP's agentic work — "Agentic AI – Threats and Mitigations", the "Multi-Agentic System Threat Modeling Guide v1.0" (April 2025), the "OWASP Top 10 for Agentic Applications for 2026" (December 2025), and the Agentic Security Initiative — treats excessive agency, tool misuse, privilege escalation and multi-agent trust boundaries as named risk categories (**B**: these resource pages were located and their existence is unambiguous, but I did not retrieve the documents' contents, so I cannot quote their contents).

Note the terminology split worth acknowledging in a paper: the academic literature says "unsafe tool invocation"; the framework literature says "excessive agency". They overlap but are not identical, and conflating them is a reviewable defect.

### 1J. Adaptive attacks

**This is the single most decisive empirical result in the subfield.** Zhan et al. evaluate eight IPI defences and bypass **all** of them with adaptive attacks, consistently achieving attack success rate above 50% (arXiv:2503.00061, NAACL 2025 Findings, **A**). Their conclusion — that adaptive attack evaluation is required for defence claims to mean anything — is now the standard against which defence papers are judged. Follow-on work on stronger adaptive attacks exists (**B**).

Consequence for AgentSec Lab: **"adaptive attacks break defences" is no longer a contribution.** It is a premise. Any work that rediscovers it has produced an implementation, not research.

### 1K. Adaptive defences

The defensible line of work is moving from filtering to *structural* guarantees:

- **Privilege control.** Progent encodes privilege as symbolic rules over tool names and arguments; an LLM proposes policy updates; an SMT solver classifies each update as a narrowing (auto-applied) or an expansion (requires explicit approval), giving *monotonic confinement*. Evaluated on AgentDojo and ASB. Crucially, the abstract itself names "an inherent tradeoff between security and utility" (arXiv:2504.11703, **A**).
- **Capability / information-flow control.** CaMeL creates a protective layer around the LLM using control-flow and data-flow extraction with explicit capabilities restricting data flows; artifact released at `google-research/camel-prompt-injection`. That repository carries an unusually candid disclaimer: it is a research artefact, "the interpreter implementation likely contains bugs", and is "not a Google product" (**A** for the repository statement; **B** for the paper text, arXiv:2503.18813). That disclaimer is *itself evidence* for the reproducibility argument in §E.
- **Design patterns.** Six patterns for injection-resistant agent design (arXiv:2506.08837, **B**).
- **Memory-specific defences.** A-MemGuard (proactive memory-poisoning defence, **B**) and other 2026 memory-defence work (**B**).

The pattern to notice: the strongest defences are *architectural*, they impose utility costs, and they are evaluated on the same handful of benchmarks.

### 1L. Agent security evaluation

See §1B and §4. Summary position: coverage is good, validity is the open question, and the two most credible recent contributions are critiques rather than benchmarks.

### 1M. Security–utility trade-offs

**A real but narrow gap.** AgentDojo measures utility and security jointly (**A**). ASB introduces a dedicated metric to evaluate agents' capability to balance utility and security (**A**). Progent explicitly frames security and utility as being in inherent tension (**A**). AgentDyn reports over-defence behaviour — defences that block benign content (**A**).

So the *existence* of the trade-off is established and, in two benchmarks, is even quantified. What I could not locate in any verified primary source is a benchmark that reports the trade-off **as a frontier function of an explicit, controlled intervention**, across models, with the *third* axis (§1N) attached. This distinction is the difference between "we also plot utility" and "we measure the shape of the frontier and the rank stability of models along it". Only the latter is a contribution.

### 1N. Multi-model security evaluation

Universal in the weak sense (every benchmark runs N models) and rare in the strong sense (systematically treating the *model family* as an experimental factor). Two verified data points:

- RAS-Eval reports that "scaling laws held for security capabilities, with larger models outperforming smaller counterparts" (6 models, **A**).
- MCPTox reports the opposite pattern: "more capable models are often more susceptible, as the attack exploits their superior instruction-following abilities" (20 agents, `o1-mini` highest at 72.8% ASR, **A**).

These are not necessarily contradictory — they use different attack classes (CWE-mapped task attacks vs tool-metadata poisoning) and different models — but they are *presented as general findings about capability and security*, and no work I found reconciles them. **This is the most promising verified contradiction in the literature.**

### 1O. Reproducible security benchmarks

Weak across the board. Evidence gathered:

- Non-determinism in commercial LLM inference is a recognised obstacle to reproducing studies built on commercial APIs (**B**, arXiv:2510.25506).
- CaMeL ships an artefact with a self-declared bug caveat and no product guarantee (**A**).
- MCPTox releases its dataset at an "anonymized repository" — i.e. at the time of the arXiv posting, the dataset was not durably or identifiably published (**A**). This is a concrete, quotable reproducibility weakness in a 2025 benchmark.
- The most explicit treatment of why agent evaluation is not credible without log analysis is Kirgis et al. (2026), who provide a taxonomy of threats to credible evaluation and principles for log analysis, and illustrate on tau-Bench Airline that `pass^5` was "under-elicited by nearly 50%" and that deployment failure modes were invisible to outcome metrics (arXiv:2605.08545, **A**). Their author list (Princeton/Arc/METR-adjacent) gives this high evidentiary weight. **This is the most important paper in this document for AgentSec Lab's methodology.**

### 1P. Agentic AI security frameworks

- **OWASP GenAI Security Project** — agentic threats and mitigations, multi-agentic threat-modelling guide, Top 10 for Agentic Applications 2026, Agentic Security Initiative, Agentic Security Solutions Landscape (**B**; documents unread).
- **IETF BMWG draft** `draft-han-bmwg-agent-security-benchmark-00`, "Security Evaluation Benchmark for AI Agents", published 2026-07-05, Informational, expires 2027-01-06 (**A** — fetched in full). It defines four first-level dimensions (Model-Native Security, Interaction Security, Operational Security, Basic Security) and **55 second-level metrics**, with methodology spanning static, dynamic, attack–defence, compliance and quantitative evaluation; metrics are pass rates over test cases; SUT decomposed into foundation model, interaction access layer, execution/scheduling components, and infrastructure. Its §4.2.2 states that standardised evaluation is conducted only on "controllable, reproducible external inputs" and excludes "random data streams from external networks that are untraceable and non-reproducible" (**A**, quoted).
  - **Two consequences.** (1) The draft is *methodologically aligned* with AgentSec Lab's reproducibility goal and is a mandatory citation. (2) The draft itself is a **framework**, not an experiment — it specifies 55 metrics but supplies no empirical results. That is precisely the seam between framework-level standardisation and empirical measurement, and it is a legitimate place for a paper to sit.
  - **Citation caveat:** the IETF states on the document itself that Internet-Drafts are "inappropriate to use or cite ... other than as 'work in progress'". Any citation must be framed as a work-in-progress draft.
- **MITRE ATLAS** and **NIST AI 100-2** are the usual companion references for adversarial-ML threat modelling — **not verified in this pass**; check before citing.

### 1Q. Open-source agent security testing platforms

Three tools dominate practitioner discussion: NVIDIA **garak** (model-level scanning, 120+ probes, limited agentic/RAG coverage), Microsoft **PyRIT** (multi-turn attack orchestration, used in 100+ internal MS red-team operations), and **promptfoo** (application/CI-level testing, also maintains an LLM security database referenced repeatedly in this search) (**B**, and the capability and usage numbers come from vendor blogs and comparison sites — treat every figure as **C**). Their *existence* and open-source status are not in doubt; their *agentic coverage claims* are unverified.

Analytically: these are **tooling**, evaluated on their own terms. They are not benchmarks, they do not report security–utility–cost frontier measurements, and they do not release experiment logs. The academic benchmarks and the practitioner tooling are two largely disconnected ecosystems — an integration gap of marginal publishable weight.

**AgentInjectionBench** — the project brief names this as a benchmark to investigate. Finding: the name resolves to **community Hugging Face datasets** (`sincpp/AgentInjectionBench`, `ppradyoth/AgentInjectionBench`) with a schema including `attack_category`, `attacker_intent`, `injection_surface`, `complexity` (observed value: `single_turn`), `target_tools`, `defense_bypass`, `system_prompt`, `tools_available`, `conversation`, `ground_truth`, `severity`, `notes` (**A**: dataset page fetched). I found **no peer-reviewed publication, no venue, no author-affiliated paper, and no DOI** for it. It is a **useful schema reference and a candidate secondary comparison set, but it is not citable as a benchmark in a peer-reviewed paper** and must not be presented as comparable to AgentDojo or ASB. The dataset content also embeds agent-control style prompt-injection payloads; handle with the same care as an attack corpus.

---

## C / §2. Benchmark comparison

Machine-readable version: `research/tables/benchmark-comparison.csv`. Per-field confidence follows §0.3.

> **Global warning.** This table is **abstract-level**, not full-text. Fields marked `unverified` are likely answerable from the papers' full texts and appendices; they must be resolved by reading the papers before this table appears in any manuscript. Do not treat a blank as a finding.

### 2.1 Core comparison

| Field | **AgentDojo** | **ASB** | **RAS-Eval** | **InjecAgent** | **AgentDyn** |
|---|---|---|---|---|---|
| Year (v1) | 2024-06-19 (**A**) | 2024-10-03, v4 2025-05-30 (**A**) | 2025-06-18 (**A**) | 2024-03-05 (**A**) | 2026-02-03, v3 2026-05-07 (**A**) |
| Venue / status | NeurIPS 2024 Datasets & Benchmarks (**A**) | ICLR 2025 (**A**, authors' own statement) | Preprint; **peer-review status not reported** (**A**) | ACL 2024 Findings (**A**) | Preprint; venue not reported (**A**) |
| Scenarios | 97 realistic tasks; 629 security test cases (**A**) | 10 scenarios (e-commerce, autonomous driving, finance, …); 10 agents; >400 tools (**A**) | 80 test cases; 3,802 attack tasks; 11 CWE categories (**A**) | 1,054 test cases; 17 user tools; 62 attacker tools (**A**) | 60 open-ended tasks; 560 injection cases; 3 domains (Shopping, GitHub, Daily Life) (**A**) |
| Attacks | "Various attack and defense paradigms from the literature"; count not reported in abstract (**A**); adaptive-attack-ready by design (**A**) | 10 prompt injection + 1 memory poisoning + Plan-of-Thought backdoor + 4 mixed (**A**) | 3,802 attack tasks mapped to 11 CWEs (**A**) | 2 intentions (direct harm; data exfiltration); + "hacking prompt" reinforcement variant (**A**) | Injection cases across dynamic open-ended tasks; count 560 (**A**) |
| Agent architectures | LLM agents executing tools over untrusted data; multi-suite (**A**) | 10 scenario-specific agents (**A**) | LangGraph, JSON tools, MCP tool formats (**A**) | ReAct and other promptings; 30 agents evaluated (**A**) | unspecified; dynamic planning required (**A**) |
| Models | "state-of-the-art LLMs"; list unverified | 13 LLM backbones (**A**) | 6 SOTA LLMs (**A**) | 30 LLM agents (**A**) | not reported in abstract |
| Defences | "various defence paradigms from the literature"; enumeration unverified | 11 defences (**A**) | not reported in abstract | not reported in abstract | 10 state-of-the-art defences evaluated (**A**) |
| Metrics | security test cases + task utility (joint) (**A**) | 7 metrics + a dedicated utility/security-balance metric (**A**) | TCR (task completion rate); attack success rate (**A**) | attack success rate (**A**) | security + over-defence (**A**) |
| Adaptive attacks supported | **Yes — explicitly an extensible environment for adaptive attacks** (**A**) | Adaptive attackers not reported in abstract; attacks are enumerated static set (**A** for enumeration) | not reported | "enhanced setting" with hacking prompt; not adaptive in the attacker-in-the-loop sense (**A**) | **Yes in spirit** — explicitly critiques static benchmarks and evaluates defences dynamically (**A**) |
| Multi-turn | Multi-step tool execution; multi-turn *attack* support not reported | not reported | not reported | not reported | multi-step open-ended tasks; attack multi-turn not reported |
| Tool execution | Real (code-level tool execution) (**A**) | Simulated/emulated per scenario (**A** for scenario framing; mechanism unverified) | **Both simulated and real-world tool execution** (**A**) | Simulated tool replay (**unverified**) | unspecified |
| Memory evaluated | not reported | **Yes** (1 memory-poisoning attack) (**A**) | not reported | not reported | not reported |
| RAG evaluated | not reported | partially (memory retrieval stage) (**A**) | not reported | not reported | not reported |
| MCP / protocols | not reported | not reported | **Yes** — tools in MCP format (**A**) | not reported | not reported |
| Security + utility jointly | **Yes** (**A**) | **Yes** (**A**) | Yes, via TCR under attack (**A**) | No (security-focused) | Yes, via over-defence analysis (**A**) |
| Operational cost measured | not reported | not reported | not reported | not reported | not reported |
| Code public | Yes — `ethz-spylab/agentdojo` (**A**) | Yes (code link in paper) (**A**) | Yes (code and data available) (**A**) | Yes (**A**) | Yes — `leolee99/AgentDyn` (**A**) |
| Data public | Yes (in repo) (**A**) | Yes (**A**) | Yes (**A**) | Yes (**A**) | Yes (**A**) |
| Reproducibility provisions | Dynamic environment, extensible; bug-fix version history documented (**A**) | Code released; 13 backbones (**A**) | Simulated **and** real execution paths (**A**) | Benchmark released (**A**) | Benchmark released; 26 pp. / 17 tables (**A**) |
| Author-identified limitations | SOTA LLMs fail many tasks even without attacks; existing attacks break some but not all security properties (**A**) | Current defences show limited effectiveness (**A**) | Attack-driven TCR drop; scaling-law observation (**A**) | Agents widely vulnerable; deployment questions raised (**A**) | **Three flaws in prior benchmarks**: no dynamic open-ended tasks, no helpful instructions, over-simplistic tasks; most defences too weak or over-defensive (**A**) |

### 2.2 Second tier

| Benchmark | Year | Venue | Scale (as reported) | Security+utility | Cost | Adaptivity | Source label |
|---|---|---|---|---|---|---|---|
| **MCPTox** | 2025-08-19 | none stated | 45 live MCP servers; 353 tools; 3 templates; 1,312 cases; 10 risk categories; 20 agents; `o1-mini` ASR 72.8%; max refusal <3% | not reported | not reported | no | **A** |
| **Agent-SafetyBench** | 2024-12-19 (v2 2025-05-20) | none stated | 349 environments; 2,000 cases; 8 risk categories; 10 failure modes; 16 agents; none >60% safety | helpfulness analysed; joint metric not reported | not reported | no | **A** |
| **AgentHarm** | 2024-10-11 | **not verified** | 110 tasks (440 with augmentations); 11 harm categories | no (harmfulness focus) | not reported | no | **B** |
| **ToolEmu** | 2023-09-25 (v2 2024-05-17) | **not verified** | 36 high-stakes tools; 144 cases; 68.8% of LM-identified failures human-validated; safest agent fails 23.9% | risk analysis, not joint frontier | **tool-execution cost is the paper's motivation** (emulation to avoid manual setup) — cost of the *system*, not of defences | no | **A** |
| **ST-WebAgentBench** | 2024-10-09 | **conflict**: ICML 2025 virtual listing and ICLR 2026 proceedings both surfaced — unresolved | policy-aware; metrics CuP and Risk Ratio | utility + policy compliance | not reported | no | **B** |
| **WASP** | 2025-04-22 | NeurIPS 2025 D&B per secondary source — **unverified** | web-agent IPI | not reported | not reported | no | **B** |
| **AgentInjectionBench** | dataset updated 2026 | **no publication located** | HF dataset; schema includes complexity/severity/ground_truth/notes | no | no | no (`complexity: single_turn` observed) | **A** (dataset page) / **no paper exists** |

### 2.3 What the comparison reveals (three observations)

1. **`operational cost` is `not reported` for every single benchmark examined.** Across fourteen comparison fields and ten+ artefacts, cost is the *only* column with a uniform blank. That uniformity is the strongest single piece of evidence in this document.
2. **Adaptive and multi-turn attack support is the exception, not the rule.** Only AgentDojo (adaptive, by design) and AgentDyn (dynamic defence evaluation) treat the attacker as a live component. Multi-turn *attack* support is not reported anywhere I verified — which sits oddly against a 2026 practitioner consensus that multi-turn escalation is the dominant real-world vector (**B**).
3. **Venue status is often unverifiable from the artefacts themselves.** RAS-Eval, MCPTox, Agent-SafetyBench, AgentDyn and AgentHarm all lack a verifiable archival venue statement in the sources I fetched. A field in which a large fraction of the primary evaluation infrastructure is un-refereed preprints has a structural credibility problem, which is itself a legitimate framing for a methods paper — provided it is stated carefully and not as an accusation.

---

## D / §3. Research-gap matrix

Machine-readable version: `research/tables/gap-matrix.csv` with an `evidence_level` column.

**Legend:** `Y` = addressed · `P` = partially addressed · `N` = not addressed in the verified sources · `?` = not reported / not verified in this pass.

**Reading rule:** a single `N` proves nothing. A `?` proves nothing at all. Conclusions are drawn only from *columns*, i.e. only where many rows agree, per the brief's instruction.

| Work | multi-model | multi-agent | multi-turn | adaptive attacker | memory | RAG | tools | tool authz | defence eval | security metrics | utility metrics | op. cost | repro-ducibility | open bench | open logs | indep. verification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AgentDojo (2024) | Y | N | P | **Y** | ? | ? | Y | N | Y | Y | Y | **N** | Y | Y | N | P |
| ASB (2024/25) | Y | P | ? | N | P | P | Y | N | Y | Y | Y | **N** | Y | Y | N | P |
| RAS-Eval (2025) | Y | N | ? | N | ? | ? | Y | N | P | Y | P | **N** | P | Y | N | P |
| InjecAgent (2024) | Y | N | N | N | N | N | Y | N | N | Y | N | **N** | Y | Y | N | P |
| AgentDyn (2026) | ? | N | P | P | ? | ? | Y | N | Y | Y | Y | **N** | Y | Y | N | P |
| MCPTox (2025) | Y | N | N | N | N | N | Y | P | N | Y | N | **N** | P | P | N | N |
| Agent-SafetyBench (2024) | Y | N | ? | N | N | N | Y | N | P | Y | P | **N** | Y | Y | N | P |
| AgentHarm (2024) | P | N | ? | N | N | N | Y | N | N | Y | N | **N** | P | Y | N | P |
| ToolEmu (2023) | P | N | N | N | N | N | Y | N | N | P | N | **N** | P | P | N | P |
| ST-WebAgentBench (2024) | P | N | ? | N | N | N | Y | P | N | Y | Y | **N** | P | Y | N | P |
| WASP (2025) | P | N | ? | N | N | N | Y | N | P | Y | ? | **N** | ? | P | N | P |
| Zhan et al. adaptive attacks (2025) | Y | N | N | **Y** | N | N | Y | N | **Y** | Y | N | **N** | Y | Y | N | P |
| Progent (2025/26) | P | N | ? | P | N | N | Y | **Y** | Y | Y | Y | **N** | Y | Y | N | P |
| CaMeL (2025) | P | N | N | P | N | N | Y | **Y** | Y | Y | Y | **N** | P | Y | N | P |
| Design Patterns (2025) | P | P | ? | P | P | P | Y | **Y** | Y | P | P | **N** | ? | Y | N | N |
| AgentPoison (2024) | P | N | N | N | **Y** | **Y** | Y | N | N | Y | N | **N** | P | Y | N | P |
| MINJA (2025) | P | N | N | N | **Y** | P | Y | N | P | Y | N | **N** | ? | P | N | N |
| PoisonedRAG (2025) | P | N | N | N | N | **Y** | N | N | N | Y | N | **N** | Y | Y | N | P |
| Prompt Infection (2024) | P | **Y** | N | P | P | N | P | N | N | Y | N | **N** | ? | P | N | N |
| IETF BMWG draft (2026) | Y | Y | Y | P | Y | Y | Y | Y | Y | Y | Y | **?** | Y (process) | N (spec) | N | N |
| OWASP agentic guidance (2025–26) | Y | Y | P | P | Y | Y | Y | Y | P | P | P | **N** | N | N | N | N |
| PyRIT / garak / promptfoo | Y | P | **Y** | P | P | P | Y | P | Y | P | N | P | P | Y | N | N |

### 3.1 Column verdicts

| Column | Verdict | Basis |
|---|---|---|
| multi-model | **Well established** | Every major benchmark runs ≥6 models; RAS-Eval 6, ASB 13, InjecAgent 30, MCPTox 20. |
| tools | **Well established** | Universal. |
| security metrics | **Well established** | Universal; ASR and TCR are de facto standards. |
| defence evaluation | **Well established** | ASB (11 defences), AgentDojo, AgentDyn (10 defences), Zhan et al. (8 defences). |
| open benchmark | **Well established** | Public repos for essentially all academic benchmarks. |
| utility metrics | **Partially addressed** | Present in AgentDojo, ASB, AgentDyn, ST-WebAgentBench; absent in InjecAgent, MCPTox, AgentHarm. |
| adaptive attacker | **Partially addressed** | Genuinely addressed only by AgentDojo (design), AgentDyn (critique), Zhan et al. (measurement). Sparse beyond those three. |
| multi-agent | **Weakly addressed** | Only Prompt Infection and the framework documents; no benchmark with multi-agent topology as a controlled factor. |
| multi-turn | **Weakly addressed** | No verified benchmark reports first-class multi-turn *attack* support. |
| memory / RAG | **Weakly addressed as a benchmark dimension** | Well covered as attack papers (AgentPoison, MINJA, PoisonedRAG); ASB only partially. |
| tool authorization | **Weakly addressed** | Progent, CaMeL, design patterns, MCPTox partially — but authorisation *policy quality* is not a standard metric. |
| reproducibility | **Weakly addressed** | CaMeL's self-declared bug caveat; MCPTox's anonymized-repository release; Kirgis et al.'s critique; API non-determinism. |
| **operational cost** | **Largely unexplored** | **Zero verified benchmarks report it.** |
| open experiment logs | **Largely unexplored** | No benchmark verified to release per-step traces as a first-class artefact. |
| independent verification | **Largely unexplored** | No artefact verified to support score re-derivation without re-running inference. |

### 3.2 The four columns worth building on

`operational cost`, `open experiment logs`, `independent verification`, and (with weaker evidence) `multi-turn attack`. Add to these the *validity* problems documented by AgentDyn and Kirgis et al., and the *unresolved contradiction* between MCPTox and RAS-Eval.

### 3.3 Three things that are NOT gaps (explicit rejections)

- **"No benchmark covers multiple models."** False. Reject.
- **"Memory poisoning is unexplored."** False. Reject.
- **"MCP security is unexplored."** False as of 2025-08 (MCPTox) and later (**B**: MCP-SafetyBench, MCP-TDP, MCP-ITP and others surfaced). Reject.

---

## E / §4. Candidate research gaps

Eight candidates. Each is assessed for whether existing work already substantially addresses it; where it does, the candidate is **rejected** rather than reframed.

---

### Gap 1 — The security–utility frontier has not been measured as a *function of a controlled intervention*, jointly with cost

**Gap statement.** Security and utility are jointly reported but not modelled: existing benchmarks report point measurements (an ASR and a utility score) rather than the *shape* of the security–utility frontier, and none attaches the cost of traversing it.

**Evidence.** AgentDojo measures utility and security jointly (**A**). ASB adds a metric for the utility/security balance (**A**). Progent names the "inherent tradeoff between security and utility" (**A**) and is evaluated on AgentDojo and ASB (**A**). AgentDyn demonstrates that defences show over-defence (**A**). Cost column: uniform `not reported` across ten benchmarks (§C). Secondary corroboration of the cost angle: a survey reports a defence reducing ASR below 1% "at a cost of 14,605 tokens" (**B** — quoted from a survey, primary source not retrieved; must not be cited as a number until the primary source is read).

**Partially addressed by.** AgentDojo (joint metrics), ASB (balance metric), AgentDyn (over-defence), Progent (trade-off framing).

**Why it matters.** Deployment decisions are cost-constrained. A defence that reduces ASR by 90% at 15× inference cost is not "better" than one that reduces it by 80% at 1.2× cost; a benchmark that cannot distinguish these cannot inform procurement, and its "best defence" ranking is an artefact of the metric.

**What could be investigated experimentally.** Inject one or more *tunable* defence controls (a privilege-policy strictness knob; a detector threshold) and sweep the control across its range, measuring security, utility and cost at each point, for each model in a multi-model grid. Estimate the empirical Pareto frontier per model.

**What would make the contribution novel.** The frontier is reported *as a curve with confidence bands*, the control is explicit, cost is measured with a stated accounting rule, and models are *ranked by frontier dominance* rather than by a single operating point.

**Required data.** Existing public benchmarks as substrates (AgentDojo and/or ASB) — no new scenarios initially.

**Required models.** ≥6 models spanning ≥2 capability tiers and ≥3 providers; see §6 for the deficiency in the currently available set.

**Required infrastructure.** Deterministic tool sandbox; token/latency/$ accounting per step; a runner that can execute a defence sweep reproducibly; storage for full traces.

**Main risks to novelty.** (i) This is the closest candidate to "we added a cost column", which a reviewer will call an implementation. (ii) AgentDyn and ASB may already contain partial frontier evidence in their full texts — **must be read before proceeding**. (iii) Cost accounting is trivial once stated; the intellectual content must come from the frontier *shape* and its stability, not the arithmetic.

---

### Gap 2 — The capability–vulnerability relationship is contested and unresolved

**Gap statement.** Two credible benchmark papers report opposite directions for the relationship between model capability and attack susceptibility, and no work reconciles them.

**Evidence.** RAS-Eval: "scaling laws held for security capabilities, with larger models outperforming smaller counterparts" (**A**, quoted). MCPTox: "more capable models are often more susceptible, as the attack exploits their superior instruction-following abilities"; `o1-mini` highest at 72.8% ASR; model refusal rates below 3% (**A**, quoted). Different attack classes and model sets are implicated but neither paper scopes its claim to an attack class.

**Partially addressed by.** Nothing found. Both papers report a finding; neither addresses the other.

**Why it matters.** If susceptibility is monotone in capability, then capability scaling improves security and the field can rely on model progress. If it is not, then every safety claim derived from a single model or a single attack class is unfalsifiable in practice, and reviewer-facing claims about "the security of LLM agents" are really claims about one model at one capability tier. Any deployment guidance inherits this ambiguity.

**What could be investigated experimentally.** A factorial design crossing model capability tier × attack class (metadata/tool-poisoning vs tool-output injection vs memory injection) × defence on/off, on a fixed scenario set and a fixed scaffold, testing whether the sign of the capability–vulnerability association is stable across attack classes.

**What would make the contribution novel.** A *conditional* statement — "capability predicts susceptibility **negatively for class X and positively for class Y**, and here is the mechanism" — rather than another aggregate correlation. The mechanism matters: instruction-following as a double-edged capability has a plausible theoretical framing.

**Required data.** One benchmark that supports multiple attack classes on identical scenarios. ASB is the closest (10 prompt-injection + 1 memory-poisoning + backdoor + 4 mixed attacks, 13 backbones, **A**).

**Required models.** The binding constraint. A capability *spread* is required, and the currently available models (§6) are all "Flash"/mini tier — this threatens the design. Either acquire ≥2 substantially larger or smaller models, or reframe as within-tier variance with correspondingly weaker claims.

**Required infrastructure.** Fixed agent scaffold across models (to avoid scaffold confounding), adversarial filtering of provider-side blocks, repeated runs.

**Main risks to novelty.** (i) The literature publishes capability–security correlations continuously; a new correlation is not novel. The novelty is the *contradiction resolution*, which requires both classes in one design. (ii) Confounding: model, provider, safety tuning and scaffold all vary together in most benchmark grids. A design that does not separate these has a fatal validity problem.

---

### Gap 3 — Attack-budget calibration: adaptive attackers are not treated as calibrated measuring instruments

**Gap statement.** Adaptive attacks are established as necessary, but the attacker's resource budget (attempts, queries, tokens, wall-clock, attacker model strength) is not treated as an experimental variable. Consequently, reported "adaptive attack success rates" are not comparable across papers, and it is unknown whether defence rankings are stable as attacker strength increases.

**Evidence.** Zhan et al. bypass all 8 defences, "consistently achieving an attack success rate of over 50%", and explicitly call for adaptive attack evaluation (**A**). AgentDojo is designed as an extensible environment for adaptive attacks (**A**) but does not report a budget sweep in its abstract. AgentDyn critiques static benchmarks and evaluates defences dynamically (**A**). Kirgis et al. show outcome metrics can misrepresent and conceal, and that `pass^5` was under-elicited by ~50% (**A**) — direct evidence that measurement configuration changes conclusions.

**Partially addressed by.** AgentDojo (hosts adaptive attacks), Zhan et al. (executes them), follow-on stronger-adaptive-attack work (**B**).

**Why it matters.** Security evaluations that report a single ASR at an undisclosed attacker budget are not measurements, they are anecdotes with numbers attached. This is a *measurement-science* gap with a direct practical consequence: if defence or model rankings are budget-dependent, then all single-point rankings in the literature are potentially non-comparable.

**What could be investigated experimentally.** Hold the scenario set, scaffold, and defence fixed. Sweep attacker budget across discretely increasing levels. Measure ASR, utility and cost at each level. Test **rank stability** of the defended models as a function of budget.

**What would make the contribution novel.** The *falsifiable claim* that security rankings are budget-dependent, with an empirical rank-stability statistic. That is a claim about the literature's methodology, not about one defence.

**Required data.** Existing benchmarks; the attacker is the new component.

**Required models.** ≥6.

**Required infrastructure.** A reproducible adaptive-attack harness with explicit, logged budget accounting; attacker LLM determinism control; cost accounting.

**Main risks to novelty.** (i) The "adaptive attacks are necessary" argument is settled; the contribution must be the *calibration* result, not the argument. (ii) Compute cost of sweeping budgets × models × defences × repeats is multiplicative and could be prohibitive with §6's model set. (iii) Attack-strength measurement is itself contested; a defensible operationalisation of "budget" is needed (attempts is the most defensible; token budget is more precise but conflates with verbosity).

---

### Gap 4 — Experiment logs are not released, so agent-security results cannot be independently re-derived

**Gap statement.** Benchmarks release code and datasets but not the raw per-step traces, raw model responses, and scoring inputs. Independent verification therefore requires re-running inference, which is expensive, non-deterministic, and may be impossible if a model version is retired.

**Evidence.** CaMeL's artefact self-declares likely bugs and no product guarantee (**A**). MCPTox releases data at an "anonymized repository" (**A**). Kirgis et al. argue log analysis is *necessary* for credible agent evaluation and give a threat taxonomy plus principles (**A**). Commercial-API non-determinism impedes reproducing studies (**B**). No artefact verified in §C releases experiment logs as a first-class output.

**Partially addressed by.** Kirgis et al. (principle), open benchmark repositories (code and data).

**Why it matters.** This is the difference between a *result* and a *reproducible result*, and it is the most direct answer to the project's stated reproducibility goal. It also has a hard practical consequence: separating **generation** from **scoring** means a scorer can be re-run offline, with no API calls, by a reviewer with no credentials and no budget.

**What could be investigated experimentally.** Not an experiment per se. Rather: derive a scoring-only reproduction path, then quantify how much a conclusion changes when scoring is recomputed from released traces under alternative but defensible metric definitions.

**What would make the contribution novel.** Only if it produces a *finding*, not a schema. Candidate finding: published ASR figures are sensitive to defensible metric-definition choices, and the variance introduced by scoring choices is comparable to the effect being reported. That would be a strong, verifiable claim. If instead the finding is "we released logs and here is a template", it is infrastructure, not research.

**Required data.** Released traces from the work's own runs.

**Required models.** Any — this is model-agnostic.

**Required infrastructure.** Trace schema, hashing/checksums, a scoring-only CLI, container, frozen metric definitions with provenance.

**Main risks to novelty.** (i) **High.** "We released more artefacts" is not a research contribution at a strong journal; it is a resource paper at best, and a D&B-style venue is the honest target. (ii) Feasibility risk: provider terms may restrict redistribution of raw model outputs — **this must be checked before the design is fixed.**

---

### Gap 5 — Injection-payload decay: published benchmark payloads may become non-comparable over time

**Gap statement.** Publishing injection payloads plausibly donates them to future training corpora, so a fixed benchmark measured at time *t* and *t+Δ* may not yield comparable ASR, and cross-paper ASR comparisons across time may be invalid.

**Evidence.** Practitioner commentary asserts the mechanism (**B**); a security database tracking such issues exists (**B**). **I found no verified academic paper measuring decay.** The benchmark papers I read do not address it. This candidate therefore rests on the *weakest* evidence base in this document.

**Partially addressed by.** Nothing located. Also: *nothing located* is not the same as *nothing exists* — this needs a proper search of the contamination literature (see §3.3 of the brief's own instruction not to call something a gap because one paper omits it).

**Why it matters.** If real, it invalidates longitudinal comparisons and gives vendors an incentive to train on published payloads.

**What would make the contribution novel.** A *measurement* of decay, or a credible model of it. A rhetorically argued version is not publishable.

**Risks.** **High duplication risk** with the large existing literature on benchmark contamination and data leakage into training sets (**B**). Also methodologically hard: you cannot cleanly attribute a refusal to memorisation without model access or controlled pre-training data. **Provisional verdict: do not lead with this. Keep as a threats-to-validity consideration or a secondary analysis.**

---

### Gap 6 — Multi-agent topologies are not a controlled evaluation factor

**Gap statement.** Multi-agent systems are recognised as a distinct attack surface, but no benchmark verified here treats agent *topology* (number of agents, trust boundaries, delegation depth, communication medium) as an experimental factor with security, utility and cost measured jointly.

**Evidence.** Prompt Infection shows self-replicating injection across interconnected agents (**B**). OWASP's multi-agent threat-modelling guide and the 2026 agentic Top 10 name inter-agent trust as a risk category (**B**). The IETF draft includes multi-agent collaborative systems in scope (**A**, quoted) but supplies no measurements. In the gap-matrix column verdicts, `multi-agent` was the most weakly populated academic column.

**Partially addressed by.** Prompt Infection (propagation), framework documents (taxonomy).

**Why it matters.** Multi-agent is the fastest-growing deployment pattern and the least measured. Cost also becomes structurally interesting here — token cost per task grows with topology, so a security–utility–cost analysis is *more* informative in multi-agent settings than single-agent ones.

**What could be investigated experimentally.** Fix the task and models; vary topology as the treatment; measure propagation rate, task success, and cost per completed task.

**What would make the contribution novel.** Topology as an *independent variable* rather than a case study, with a cost axis that makes the security–utility trade-off explicitly a *three-way* decision.

**Risks.** **Feasibility.** A credible multi-agent benchmark is a much larger construction effort than a single-agent one, and prompt-infection-style attacks are hard to make deterministic. Frameworks may move under you mid-project.

**Provisional verdict: strong long-term direction, high risk as a first study.**

---

### Gap 7 — Tool-authorisation policy quality is not a standard metric

**Gap statement.** Privilege/authorisation mechanisms are proposed (Progent, CaMeL, design patterns) but benchmarks measure attack success, not *policy quality* — the false-allow / false-deny rates of the authorisation layer itself.

**Evidence.** Progent enforces least privilege via symbolic policy with SMT-classified updates and monotonic confinement, evaluated on AgentDojo and ASB (**A**). CaMeL uses flow tags and capabilities to prevent unauthorised exfiltration (**B**). MCPTox shows agents "rarely refuse" attacks using legitimate tools for unauthorised operations, with refusal <3% at best (**A**) — i.e. legitimacy of the tool is not the same as legitimacy of the operation.

**Partially addressed by.** Progent and CaMeL measure the security and utility of *their own* mechanism. What is missing is a *benchmark-level* metric for authorisation quality.

**Why it matters.** "The agent could technically call this tool" and "the agent was authorised to perform this operation" are different predicates; conflating them is why refusal rates are near zero in MCPTox.

**What would make the contribution novel.** A benchmark-level authorisation metric with the same status as ASR — measured on held-out policies, not on one system's own policy language.

**Risks.** **Duplication with Progent.** Progent is explicitly a privilege-control framework evaluated on the leading benchmarks; a paper whose headline is "privilege control matters" would be derivative. The defensible wedge is the *metric*, and even then the contribution is narrow. **Provisional verdict: attractive but crowded; do not lead with it.**

---

### Gap 8 — Real tool execution at scale is not combined with cost accounting and reproducibility

**Gap statement.** RAS-Eval supports both simulated and real tool execution (**A**) and warns that simulated-only evaluation may not reflect real deployments; AgentDyn criticises static benchmarks; ToolEmu's emulation was motivated precisely by the cost of manual instantiation (**A**). But no artefact verified here combines real-side-effect-capable tool execution, cost accounting, and released traces.

**Partially addressed by.** RAS-Eval (real execution, MCP tool format), ToolEmu (emulation), MCPTox (live MCP servers).

**Why it matters.** Simulated tools are cheaper and safer to benchmark but may miss real-API failure modes, rate limits and partial-execution hazards — which are exactly where cost becomes non-linear.

**Risks.** Safety and ethics: real tool execution with real side effects is a dual-use risk requiring strong isolation. Infrastructure fragility. **Provisional verdict: an infrastructure property, not a research gap. Treat as a design requirement, not a contribution.**

---

### E.1 Gap summary

| # | Gap | Evidence strength | Existing coverage | Verdict |
|---|---|---|---|---|
| 1 | Security–utility frontier × cost | Strong (verified) | Partial (joint metrics exist; frontiers and cost do not) | **Pursue — as the differentiating element** |
| 2 | Capability–vulnerability contradiction | Strong (two verified, opposed findings) | None located | **Pursue — highest intellectual novelty** |
| 3 | Attack-budget calibration / rank stability | Strong (adaptive attacks verified as necessary; calibration absent) | Partial | **Pursue — as the methodological engine** |
| 4 | Released logs / scoring re-derivation | Strong | Principle only | **Pursue — as release discipline; weak as a standalone paper** |
| 5 | Payload decay over time | Weak | Possibly substantial elsewhere | **Do not lead with** |
| 6 | Multi-agent topology as a factor | Moderate | Prompt Infection + frameworks | **Defer** |
| 7 | Authorisation policy-quality metric | Moderate | Progent/CaMeL self-evaluation | **Do not lead with** |
| 8 | Real tools + cost + traces | Moderate | RAS-Eval partially | **Design requirement, not a gap** |

---

## F / §5. Strongest research directions

Three directions, compared qualitatively. **No numerical ranking is used**; the comparison is a reasoned argument, and the recommendation in §G is stated with its uncertainties.

### Direction I — *The budget-calibrated security frontier across model families*

**One-sentence statement.** Establish whether the security and utility of tool-using agents can be measured as a stable, budget-calibrated frontier across model families, or whether published single-point security comparisons are non-comparable because defence and model rankings move with attacker budget.

**Novelty potential.** High, but bounded. The novelty is not "adaptive attacks break defences" (settled, **A**) nor "cost matters" (uncontroversial). It is the *stability question* — a claim about the measurement apparatus of the subfield, with a falsifiable statistic (rank correlation across budget levels). If rankings are stable, that is a genuinely useful positive result and it *validates* the existing literature; if unstable, it invalidates a class of comparisons. Both outcomes are publishable, which is a strong design property.

**Scientific significance.** High. It addresses measurement validity, which AgentDyn and Kirgis et al. have established as the live problem (**A**), and it attaches the missing cost axis.

**Feasibility.** Moderate-to-high. Requires building an adaptive-attack harness with budget accounting, not a new benchmark. Substrates exist.

**Reproducibility.** High if generation and scoring are separated (§J).

**Model availability.** **The binding constraint.** Needs capability spread; see §6.

**Experimental cost.** Highest of the three. Cost scales as budgets × models × defences × repeats. Must be budgeted and possibly subsampled — with any subsampling pre-registered.

**Public datasets.** Available (AgentDojo, ASB, AgentDyn).

**Duplication risk.** Moderate. Zhan et al. and AgentDyn are close in spirit; neither performs a budget sweep or reports rank stability. **Both full texts must be read before committing.**

**Journal contribution.** Strong methods-plus-empirics paper; plausible at a security or trustworthy-ML venue. Not a new-capability paper.

---

### Direction II — *Resolving the capability–vulnerability contradiction*

**One-sentence statement.** Determine whether the sign of the model-capability/susceptibility relationship depends on attack class, and identify the mechanism, in a controlled design that separates model capability from scaffold and provider effects.

**Novelty potential.** Highest. A verified, direct contradiction between two published findings (**A**, **A**) with no reconciliation attempt is rare and valuable. Explaining *why* instruction-following is a liability in one class and a defence in another is a mechanism claim, not a correlation.

**Scientific significance.** High. It would convert a collection of incompatible benchmark results into a conditional theory.

**Feasibility.** **Low with the current model set.** Requires a genuine capability spread across providers. This is the direction most exposed to the §6 deficiency.

**Reproducibility.** High, and arguably easier than Direction I (smaller design).

**Model availability.** **Binding and currently unsatisfied.** All four available models are "Flash"/mini tier. A capability-spread design cannot be executed on them.

**Experimental cost.** Lower than Direction I.

**Public datasets.** Available.

**Duplication risk.** Low for the reconciliation; high for yet another correlation.

**Journal contribution.** The most attractive narrative — a contradiction resolved — and the most fragile, because it depends on an experimental factor the project may not be able to manipulate.

---

### Direction III — *A verifiable-release agent-security evaluation protocol*

**One-sentence statement.** Define and demonstrate an evaluation protocol in which every reported number can be re-derived offline from released traces by an independent party, and quantify how sensitive published-style conclusions are to defensible metric-definition choices.

**Novelty potential.** Moderate. As pure infrastructure, low. As a *sensitivity finding* — "scoring-rule variance is comparable to reported effects" — potentially high, and aligned with Kirgis et al.'s agenda (**A**).

**Scientific significance.** Moderate-to-high for the community, lower for theory.

**Feasibility.** High technically; the risk is **policy**, not engineering: provider terms may not permit redistribution of raw outputs.

**Reproducibility.** This *is* reproducibility; it is self-exemplifying.

**Model availability.** Not binding.

**Experimental cost.** Low.

**Public datasets.** N/A (produces artefacts).

**Duplication risk.** Low.

**Journal contribution.** Best fit is a datasets-and-benchmarks or reproducibility track, or a methods journal. Weak as a standalone contribution to a strong journal unless the sensitivity analysis produces a real finding.

---

### F.1 Qualitative comparison

| Criterion | Direction I (budget-calibrated frontier) | Direction II (capability contradiction) | Direction III (verifiable release) |
|---|---|---|---|
| Novelty potential | High (measurement-stability claim) | **Highest** (resolves a verified contradiction) | Moderate (a finding, if any) |
| Scientific significance | High | High | Moderate–High |
| Feasibility | Moderate–High | **Low with current models** | High (technically) — policy risk |
| Reproducibility | High | High | Self-exemplifying |
| Model availability | Constraining (needs spread) | **Binding (needs spread)** | Not binding |
| Experimental cost | Highest | Moderate | Lowest |
| Public datasets | Available | Available | N/A |
| Duplication risk | Moderate | **Low** | Low |
| Journal contribution | Strong methods+empirics | Strong but fragile | Track-dependent |

**Note on Directions I and II.** They are **complementary, not competing**: Direction I supplies the harness and the budget discipline; Direction II supplies the scientific question that harness is pointed at. Treating them as one programme with a staged design is more honest than choosing between them.

---

## G / §6. Model availability assessment

The four named models: **DeepSeek V4.1 Flash**, **MiMo 2.6 Flash**, **GLM 5.3 Flash**, **Solar Mini 4**. Everything below is about *configuration and availability*, not capability. **No benchmark score is invented or recalled.**

### 6.1 Verification status of the model facts

| Model | Provider / origin | Status of my information |
|---|---|---|
| DeepSeek V4.1 Flash | DeepSeek (China) | **B/C.** DeepSeek V4 with a 1M-token context and tool-call support is reported around 2026-04-24 (vendor news page and Hugging Face blog surfaced; a third-party provider page quotes ~$0.14/M input). The **specific "V4.1 Flash"** designation is **not confirmed at a vendor source in this pass**, and vendor context/pricing figures varied across secondary pages. |
| MiMo 2.6 Flash | Xiaomi (China) | **B/C.** MiMo-V2-Flash is documented (Dec 2025) with a 256K window, hybrid thinking toggle and function-calling support; a technical report exists. A **2.6** generation appears in vendor model-release documentation but I did not fetch the page for that variant. |
| GLM 5.3 Flash | Z.ai / Zhipu (China) | **B/C.** GLM-5 was released 2026-02-11 with weights reportedly open under MIT; GLM-5.1 (2026-04) and GLM-5.2 (2026-06) are documented on the vendor blog. A **5.3 Flash** variant is **not confirmed at a vendor source in this pass**. |
| Solar Mini 4 | Upstage (South Korea) | **B/C.** Reported as released 2026-09-22 under the ID `solar-mini4-260922`, ~35B MoE with ~3B active parameters and a ~524K context window, targeting agentic workloads with function calling; sources are model-aggregator pages and vendor API docs, not the vendor launch post. |

**Action required before any experiment.** Retrieve, for each model: the exact API model ID string; a dated, vendor-issued specification page; the context window; tool/function-calling support and its API shape; rate limits; pricing; and whether weights are downloadable. Store these as immutable artefacts in `specs/models/` (§J). **Do not build the design on the figures in the table above.**

### 6.2 Sufficiency assessment: **the set is adequate for Directions I and III, and inadequate for Direction II**

**The core problem: capability range, not model count.** All four are described as "Flash"/mini/cost-optimised tiers. A study whose design variable is *capability* cannot be executed on four models that occupy essentially one capability band. Direction II (§F) depends on that variable and therefore **cannot proceed on this set as-is.** This is the single most consequential finding of §6.

**Additional consequence: provider and capability are confounded three ways.** Three of four models are from Chinese labs; one is Korean. So the study would have *no* Western-frontier representation. For a paper claiming general findings about "LLM-based agents", that is a reviewable external-validity defect — and reviewers at strong venues will raise it immediately. It must either be fixed by adding models or scoped explicitly in the title and claims ("open-weight East Asian model families") — and the latter substantially narrows the paper's contribution.

**Compensating strength: reproducibility may be better than with frontier APIs.** GLM-5's weights are reportedly MIT-licensed (**B**) and MiMo is reported open-weight (**B**), and `solar-mini4-…` carries a dated version string (**B**). Self-hosted or dated open weights permit genuine version pinning — including *hash-level* pinning — which closed frontier APIs structurally cannot offer. If even two of the four can be pinned by weight hash, AgentSec Lab's reproducibility claim becomes materially stronger than that of most published agent-security work. **This is a real strategic advantage and should be verified early**, because it may be worth building the study around.

**Diversity.** Four providers, three countries, at least three architecture families — reasonable *vendor* diversity, weak *capability* diversity, and no representation of the most widely deployed Western frontier models. Coverage of multimodal capability is unverified.

**Experimental comparability.** The serious risk is not model quality but **API semantics**: tool-call schemas, parallel-tool-call support, streaming behaviour, JSON/function-call reliability, and system-prompt handling differ across providers. Papers have already documented reproducible tool-call compatibility failures for at least one of these model families (**B**). Any agent scaffold must therefore be validated per model *before* the security experiment — otherwise the experiment measures API plumbing, not security. A per-model scaffold-conformance test suite is a design requirement, not an optional extra.

**Context-window requirements.** Reported windows range from ~256K to ~1M. This exceeds agent-security benchmark needs (AgentDojo/ASB tasks are short-horizon), so window size is **not** the constraint. A **long-context** study would be constrained by the smallest window — but note the smallest here is still large, so a long-context/memory study is actually *feasible* on this set (relevant to Gap 6/memory work, which is otherwise deferred).

**Reproducibility concerns.** Temperature/top-p/seed support varies by provider; several providers expose no seed parameter, and even seeded generation is not guaranteed deterministic across hardware and batching. Plan for **k repeated runs and pass^k style reporting** rather than for determinism — consistent with the `pass^5` under-elicitation finding of Kirgis et al. (**A**).

**Version pinning.** For API models: record the exact model ID string, response headers, and the timestamp of every call; re-check the ID string at the start and end of each campaign; be prepared for silent updates. For open-weight models: record the weight revision hash. **Record the finding if a version changes mid-campaign** — that is data, not noise.

**Provider-side safety filtering — the most under-appreciated validity threat.** A provider may intercept an injection payload before the model ever sees it. This produces a *false* "defence" that is an artefact of the vendor's guardrail rather than of the agent. It also causes silent, non-random attrition: some payloads are blocked, others are not. **Every run must log raw request and raw response, and detect/flag provider-level refusals and content-filter blocks separately from agent behaviour.** Without this, ASR measurements on hosted APIs are uninterpretable.

**Cost.** Not assessed statistically here, but the project does not need frontier pricing: cheap, high-throughput tiers are exactly right for a design with multiplicative factor levels. That is genuinely in the project's favour — Direction I's budget sweep is affordable *because* the models are cheap. **This is the strongest argument for the current model set.**

**Recommendation.** (i) Keep all four as the reproducible core, subject to verifying that weights can be pinned. (ii) Add **at least two additional models spanning a clearly higher and a clearly lower capability tier**, ideally including one Western frontier API and one small open-weight model, to (a) de-confound provider from capability and (b) make the capability axis manipulable. (iii) If no additional models are obtainable, **drop Direction II** and rewrite the study as a within-tier study with explicitly narrowed claims — do not attempt a capability claim on a single capability band.

---

## J / §7. Reproducibility requirements

### 7.1 What a genuinely reproducible agent-security benchmark must release

Grouped by function, ordered by how much they actually enable independent verification.

**Tier 1 — enables independent re-derivation of results (highest value, almost always missing)**

1. **Raw generation artefacts.** Unmodified model request payloads and responses, one record per model call, including provider error bodies, refusals and filter blocks.
2. **Full execution traces.** Per-step agent state: observation, thought/action, tool name, raw arguments, tool return value, timestamp, cumulative token counts. Machine-readable (JSONL).
3. **Scoring inputs and outputs.** The exact material fed to the scorer, the scorer's verdict, and the scorer's own version. Needed because many agent-security conclusions depend on an LLM-as-judge.
4. **A scoring-only reproduction path.** A command that recomputes every reported number from released traces **with no network access and no API keys**.
5. **Checksums and manifests** binding code, data, weights, and results together.

**Tier 2 — enables re-running the experiment**

6. **Attack specifications** as declarative, versioned artefacts (target property, payload, injection surface, success predicate) — not prose in an appendix and not strings embedded in code.
7. **Benchmark scenarios** with the *canonical solution* and the *security property* under test, decoupled from the agent scaffold.
8. **Agent definitions and system prompts**, verbatim and versioned. System prompts are experimental treatments and must be diffable.
9. **Tool definitions**: JSON schemas, side-effect semantics, rate limits, and the sandbox in which they execute.
10. **Environment configuration** as code: container image digests, network policy, filesystem fixtures, seeded initial state.
11. **Model configuration**: exact model ID/weight hash, temperature, top-p, max tokens, seed (or explicit statement that no seed is supported), tool-choice mode, and the date of every call.
12. **Experiment manifests** per run: seeds, factor levels, budget, repeat index, git commit, reproduction command.
13. **Dependency lock files** and pinned container digests.

**Tier 3 — analysis and presentation**

14. **Processed per-task results** (one row per task × condition) — not only aggregates. Aggregates cannot be audited.
15. **Statistical analysis scripts**, seeded, with the full model specification, not only the reported test.
16. **Plot and table generators** producing the published figures from the released results table, so a reviewer can regenerate a figure after changing one assumption.
17. **Pre-registration** of the analysis plan before the confirmatory campaign, plus a **deviations log** recording every post-hoc change and why.
18. **Confidence intervals and effective sample size** for every headline number; never a bare point estimate.

**Tier 4 — governance**

19. **AI-use disclosure** (§7.3).
20. **Ethics and dual-use statement**, including the policy for whether and how attack payloads are released.
21. **Licences** separately for code, data, and documents.
22. **CITATION.cff** with a versioned DOI (Zenodo) for each release.

### 7.2 Proposed AgentSec Lab structure

```
agentsec-lab/
├── README.md
├── LICENSE                 # code: Apache-2.0 (or MIT)
├── LICENSE-DATA            # data: CC-BY-4.0
├── CITATION.cff
├── docs/
│   ├── threat-model.md         # asset / adversary / trust-boundary definition
│   ├── metrics.md              # every metric DEFINED at code level, with provenance
│   ├── operational-cost-accounting.md   # what counts as cost, and how it is attributed
│   ├── preregistration.md      # frozen BEFORE the confirmatory campaign
│   ├── deviations-log.md       # every post-hoc change, dated
│   ├── ai-use-disclosure.md
│   └── ethics-and-dual-use.md
├── specs/                      # declarative, version-controlled experiment definitions
│   ├── scenarios/              # task + canonical solution + security property
│   ├── attacks/                # payload, surface, success predicate, budget
│   ├── defenses/               # mechanism + tunable control + threshold range
│   ├── agents/                 # scaffold + system prompt + tool bindings
│   ├── models/                 # pinned ID, pinned spec URL, config, verification date
│   └── experiments/            # factor grids + seeds + repeats
├── src/agentsec/               # runner, scorers, cost meter, trace writer
├── environment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── lock/                   # uv.lock / poetry.lock / requirements.lock
│   └── versions.json           # runtime versions captured automatically
├── runs/<run_id>/              # RELEASED artefact, one directory per campaign
│   ├── manifest.json           # spec hashes, git commit, seeds, budget, timestamp
│   ├── environment.json        # model IDs, container digests, provider headers
│   ├── traces/*.jsonl          # full per-step traces
│   ├── raw/*.jsonl             # unmodified requests + responses, incl. errors
│   ├── scores/*.jsonl          # per-task verdicts + scorer version
│   └── checksums.sha256
├── analysis/
│   ├── stats/                  # seeded analysis scripts
│   ├── fig/                    # figure generators
│   └── tables/                 # table generators
└── repro/
    ├── REPRODUCE.md
    ├── rescore.sh              # offline, no API keys: traces -> scores -> tables
    └── verify.sh               # integrity + invariants + headline-number check
```

**Design rationale (the parts that matter):**

- **`runs/` is a released artefact, not scratch space.** Scored traces are the evidence; code alone is not.
- **`repro/rescore.sh` needs no network.** This is the mechanism by which a reviewer with no API credentials can check the work. It is the single highest-value item in the whole structure.
- **Cost accounting is a specification document, not an afterthought.** "Operational cost" must be defined before measurement: which tokens count (prompt, completion, cached, retries, scorer calls, attacker calls), how latency is attributed, and how monetary cost is computed when prices change. Undefined cost accounting produces unfalsifiable cost claims.
- **Metrics are defined in code and in `metrics.md` together.** Agent-security ASR definitions differ materially between papers (does a blocked attempt count? a partial exfiltration? a refusal?). Two papers can both report "ASR" and mean different things. The provenance table is what makes comparison legitimate.
- **`.freebuff` / agent scratch directories and secrets are excluded by `.gitignore`** and never enter a release.

### 7.3 AI-tool use disclosure (draft policy — the project's own requirement)

The project brief asks for transparency about AI tooling. A defensible, verifiable policy — as opposed to a vague statement — would record:

1. **Which** AI systems were used (vendor, model ID, date) for: literature search, code generation, analysis, and writing.
2. **What class of contribution** each made. A defensible taxonomy: (a) discovery/search, (b) code implementation, (c) analysis and statistics, (d) drafting prose.
3. **Which artefacts are AI-generated vs AI-assisted vs human-authored.** Code files carry a provenance header; analysis scripts state whether the design was reviewed by a human.
4. **The rule that no AI system generated a citation, a numeric result, or a claim about the literature without independent human verification at source.** This is the rule that prevents the failure mode the brief is most concerned about.
5. **A per-result verification trail**: for each headline number, who or what produced it and how it was checked.

This disclosure should be published in the repository and summarised in the manuscript's methods and AI-use statement.

### 7.4 Release and versioning

- Immutable versioned releases (v0.1, v1.0 …) with Zenodo DOIs; the paper cites the exact DOI.
- A `MANIFEST.sha256` over the release.
- Released: full traces for all reported results, including *failed* runs and abandoned conditions (survivorship bias in released runs is itself a reproducibility threat).
- Explicitly **not** released without a stated policy: raw attack payloads if the dual-use assessment requires gating; anything restricted by provider terms.

---

## K / §8. Threats to validity

Structured as a genuine threat analysis, not a disclaimer list.

### 8.1 Construct validity — are we measuring the right thing?

- **ASR is under-defined across the field.** "Attack success" may mean the agent emitted an unauthorised tool call, the call succeeded, the data actually left the system, or a judge model *said* it was hijacked. Kirgis et al. (**A**) show outcome metrics can be inflated or deflated by shortcuts and can conceal dangerous actions. **Mitigation:** define ASR at code level with a documented predicate; report intermediate and final outcomes separately; never rely on a judge model alone without human calibration on a sample.
- **Security is not a single scalar.** A model can resist exfiltration while being highly manipulable. Ranking models by one ASR discards that structure. **Mitigation:** report per-attack-class results; do not aggregate across classes without stating a weighting rule.
- **Utility has multiple defensible definitions** (task completion, partial credit, rubric score, human rating). Under attack, a "correct" final answer reached via a compromised trajectory may be scored as utility. **Mitigation:** score utility *and* trajectory legitimacy.
- **Over-defence is a form of failure** (AgentDyn, **A**). Benchmarks that score only attacks systematically under-penalise it. **Mitigation:** include benign instruction-bearing content and report false-block rate alongside ASR.

### 8.2 Internal validity — could something else explain the result?

- **Provider-side safety filtering** silently removes payloads (§6). Non-random attrition of the treatment. **Mitigation:** log raw requests/responses; flag filter blocks; report attrition rates per condition.
- **Scaffold confound.** In most published grids, model and scaffold co-vary. Any "model X is less secure" claim may be a scaffold claim. **Mitigation:** one scaffold, conformance-tested per model, held fixed.
- **Scoring leakage.** If the attacker model and the judge model are the same, or share a family, scores are correlated. **Mitigation:** separate attacker, target and judge models; state the configuration; where (un)available, disclose it as a limitation.
- **Regression to the mean / selection.** Reporting the best-performing defence configuration after a sweep inflates apparent defence quality. **Mitigation:** pre-register the operating point, or report the whole sweep.
- **Multiplicity.** Sweeping models × attacks × defences × thresholds × repeats generates many comparisons; unadjusted p-values will produce "significant" findings at the expected rate. **Mitigation:** pre-register the primary contrast; treat the rest as exploratory; use corrections or report effect sizes with intervals.

### 8.3 External validity — does it generalise?

- **Model sample.** Four Flash-tier models, three providers, three countries, none Western-frontier (§6). Claims about "LLM agents" would be over-claims. **Mitigation:** state the scope in the claims themselves.
- **Benchmark specificity.** All benchmarks are synthetic, short-horizon, English. Real deployments are longer-horizon, multi-session and often non-English.
- **Temporal.** Model versions change; published payloads decay (§4, gap 5). Results are dated, and today's finding may not hold after the next model update. **Mitigation:** date-stamp every result and state the model version in the claim itself.
- **Ecological.** Attack payloads crafted for a benchmark may not represent real adversaries' capabilities or incentives.

### 8.4 Statistical conclusion validity

- **Sample size.** Attack counts are large (AgentDojo 629, RAS-Eval 3,802) but *effective* sample size is smaller than it appears: attacks within a scenario correlate, and model calls within a task correlate. Clustered structure must be modelled or the intervals are too narrow. **Mitigation:** cluster-aware analysis (by scenario/attack family); report effective sample size.
- **Non-determinism.** Temperature, provider routing, batching and hardware all vary. **Mitigation:** k repeats, report pass^k and dispersion; pre-register k.
- **Ceiling/floor effects.** ASR clipping at 0% or 100% makes effects invisible and comparisons uninformative. **Mitigation:** report the distribution, not only the mean; flag saturated conditions.

### 8.5 Reproducibility validity

- Silent model updates; retired model versions; rate-limit-induced retries that alter traces; clock and timezone effects; non-deterministic tool emulation; judge-model version drift. **Mitigation:** the §J structure, plus re-verification of model ID strings at campaign boundaries.

### 8.6 Ethical and dual-use validity

- Attack payloads and automated adaptive attackers are dual-use. Publishing a strong adaptive attacker alongside a defence is the standard disclosure dilemma. **Mitigation:** responsible-disclosure policy, gated payload release, and no new class of real-world attack capability released without deliberation.
- Running real tool side effects risks real harm. **Mitigation:** isolation by default; real execution only where explicitly justified and sandboxed.
- If the work evaluates models from specific jurisdictions, avoid framing results as comparative capability claims about providers; frame them as measurements of configurations.

---

## L / §9. Critical reviewer assessment

Conducted before committing to a direction, as instructed.

**"What would a sceptical reviewer at a strong journal say is already known?"**

That indirect prompt injection hijacks tool-using agents (InjecAgent, **A**); that adaptive attacks defeat published defences (Zhan et al. bypass all eight, ASR >50%, **A**); that existing defences are either too weak or over-defensive in dynamic settings (AgentDyn, **A**); that memory and RAG can be poisoned (AgentPoison **A**, PoisonedRAG **A**, MINJA **B**); that tool metadata is an attack surface (MCPTox, **A**); and that agent benchmark scores need log analysis to be credible (Kirgis et al., **A**). A reviewer who knows these five things will reject any proposal that restates them. They will also note that security–utility trade-offs are already acknowledged (Progent, **A**) and quantified in balance metrics (ASB, **A**).

**"What existing paper is closest to our proposed contribution?"**

Three near-neighbours, and honesty requires naming all three:
1. **AgentDyn** (arXiv:2602.03117, **A**) — dynamic, open-ended evaluation of ten defences, explicit over-defence finding, explicit critique of prior benchmarks' flaws. *Closest on defence evaluation.*
2. **Zhan et al.** (arXiv:2503.00061, **A**) — adaptive attacks against eight defences, explicit call for adaptive evaluation. *Closest on adaptive-attack methodology.*
3. **Kirgis et al.** (arXiv:2605.08545, **A**) — threat taxonomy for credible agent evaluation, log-analysis principles, empirical demonstration that outcome metrics mislead (`pass^5` under-elicited ~50%). *Closest on measurement validity.* And, for framing, the **IETF BMWG draft** (**A**), which already enumerates 55 security metrics.

If our contribution is "adaptive, multi-model, security–utility–cost evaluation with released logs", then AgentDyn supplies *adaptive* and *dynamic*; Zhan et al. supplies *adaptive attacks*; the IETF draft supplies the *metric framework*; and the novelty reduces to *cost* and *released logs*. A reviewer will say so. The project must therefore either (a) make cost and verifiability do real scientific work, or (b) find a question those papers did not ask — and §E, gap 2 is the best candidate for (b).

**"What would make our work merely an implementation rather than research?"**

- Running existing benchmarks on new models and reporting new ASR numbers.
- Adding a cost column to an existing benchmark's table.
- Porting a benchmark to MCP.
- Re-confirming that adaptive attacks break defences on a different model set.
- Building a harness and calling the harness a contribution.
- Reporting a new capability–security correlation without a mechanism.
Each of these is individually useful and none is a research contribution at a strong journal.

**"What evidence would we need to establish novelty?"**

At least one of the following, each stated as a falsifiable claim:

1. **Non-invariance.** Model or defence security *rankings* change with attacker budget or metric definition, so published single-point comparisons are not comparable. Requires the budget sweep plus a rank-stability statistic with intervals.
2. **Conditional mechanism.** The sign of capability–vulnerability depends on attack class, with a stated mechanism and a design that separates model capability from scaffold and provider.
3. **Quantified measurement artefact.** A specific, previously unmeasured artefact (provider-side filter attrition; scoring-rule sensitivity; payload decay) whose magnitude is comparable to reported effects.
4. **Frontier non-dominance.** No single defence dominates on the joint security–utility–cost frontier across models — i.e. the optimum is model- and budget-dependent.
Any of these is a finding. None can be obtained by adding a column.

**"What experiment would most strongly distinguish our work from existing benchmarks?"**

A **rank-stability experiment under attacker-budget sweep**, executed on a fixed scenario set and a fixed scaffold, across a model set with genuine capability spread, with a tunable defence, cost measured per configuration, and full traces released.

Its distinguishing property is that **both outcomes are informative**: if rankings are stable, the existing literature's comparisons are validated and the field gains a defensible evaluation protocol; if rankings are unstable, a large class of published comparisons is invalidated and the field must change how it reports security. A design whose negative result is as publishable as its positive result is the strongest asymmetric bet available here. The principal threat to executing it is model availability (§6).

---

## M — Bibliography

Full machine-readable registry with verification status: `research/tables/sources.csv`.

**Legend:** **A** = primary source fetched in this session · **B** = traceable secondary source only · **C** = unverified, do not cite without re-checking.
Venue is stated **only** where the authors' own arXiv `Comments` field or a publisher/proceedings page states it.

### Peer-reviewed / archival

1. **Debenedetti, E., Zhang, J., Balunović, M., Beurer-Kellner, L., Fischer, M., Tramèr, F.** — *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.* NeurIPS 2024 Datasets and Benchmarks Track. arXiv:2406.13352 (v1 2024-06-19; v3 2024-11-24). DOI: 10.48550/arXiv.2406.13352. Code: https://github.com/ethz-spylab/agentdojo — **A**
2. **Zhang, H., Huang, J., Mei, K., Yao, Y., Wang, Z., Zhan, C., Wang, H., Zhang, Y.** — *Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents.* ICLR 2025 (per authors' statement). arXiv:2410.02644 (v1 2024-10-03; v4 2025-05-30). DOI: 10.48550/arXiv.2410.02644 — **A**
3. **Zhan, Q., Liang, Z., Ying, Z., Kang, D.** — *InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.* Findings of ACL 2024. arXiv:2403.02691. DOI: 10.48550/arXiv.2403.02691 — **A**
4. **Zhan, Q., Fang, R., Panchal, H. S., Kang, D.** — *Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents.* Findings of NAACL 2025. arXiv:2503.00061. DOI: 10.48550/arXiv.2503.00061. Code: https://github.com/uiuc-kang-lab/AdaptiveAttackAgent — **A**
5. **Chen, Z., Xiang, Z., Xiao, C., Song, D., Li, B.** — *AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases.* NeurIPS 2024. arXiv:2407.12784. Code: https://github.com/AI-secure/AgentPoison — **A** (venue/abstract via NeurIPS proceedings; arXiv abs page not fetched)
6. **Zou, W., Geng, R., Wang, B., Jia, J.** — *PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models.* 34th USENIX Security Symposium, 2025. arXiv:2402.07867. Code: https://github.com/sleeepeer/PoisonedRAG — **A** (via USENIX programme page)
7. **Ruan, Y., Dong, H., Wang, A., Pitis, S., Zhou, Y., Ba, J., Dubois, Y., Maddison, C. J., Hashimoto, T.** — *Identifying the Risks of LM Agents with an LM-Emulated Sandbox (ToolEmu).* arXiv:2309.15817 (v1 2023-09-25; v2 2024-05-17). DOI: 10.48550/arXiv.2309.15817 — **A**. *(Widely cited as ICLR 2024; venue not stated in the arXiv record — do not assert without checking.)*
8. **Levy, I., et al.** — *ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents.* arXiv:2410.06703. Code: https://github.com/segev-shlomov/ST-WebAgentBench — **B**. *(Venue unresolved: an ICML 2025 listing and an ICLR 2026 proceedings entry both surfaced — must be resolved.)*

### Preprints (no archival venue verified in this pass)

9. **Fu, Y., Yuan, X., Wang, D.** — *RAS-Eval: A Comprehensive Benchmark for Security Evaluation of LLM Agents in Real-World Environments.* arXiv:2506.15253 (2025-06-18). DOI: 10.48550/arXiv.2506.15253 — **A**. Peer-review status not reported.
10. **Wang, Z., Gao, Y., Wang, Y., Liu, S., Sun, H., Cheng, H., Shi, G., Du, H., Li, X.** — *MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers.* arXiv:2508.14925 (2025-08-19). DOI: 10.48550/arXiv.2508.14925 — **A**. Dataset released at an anonymized repository at time of posting.
11. **Zhang, Z., Cui, S., Lu, Y., Zhou, J., Yang, J., Wang, H., Huang, M.** — *Agent-SafetyBench: Evaluating the Safety of LLM Agents.* arXiv:2412.14470 (v2 2025-05-20). DOI: 10.48550/arXiv.2412.14470. Code: https://github.com/thu-coai/Agent-SafetyBench — **A**
12. **Li, H., Wen, R., Shi, S., Zhang, N., Vorobeychik, Y., Xiao, C.** — *AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?* arXiv:2602.03117 (v3 2026-05-07). DOI: 10.48550/arXiv.2602.03117. Code: https://github.com/leolee99/AgentDyn — **A**
13. **Kirgis, P., Kapoor, S., Rabanser, S., Nadgir, N., Ududec, C., Dubois, M., Allaire, J. J., Stosz, C., Hobbhahn, M., Steinhardt, J., Narayanan, A.** — *Log analysis is necessary for credible evaluation of AI agents.* arXiv:2605.08545 (2026-05-08). DOI: 10.48550/arXiv.2605.08545 — **A**
14. **Shi, T., He, J., Wang, Z., Li, H., Wu, L., Guo, W., Song, D.** — *Progent: Securing AI Agents with Privilege Control.* arXiv:2504.11703 (v1 2025-04-16; v3 2026-05-14). DOI: 10.48550/arXiv.2504.11703 — **A**
15. **Andriushchenko, M., Souly, A., et al.** — *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents.* arXiv:2410.09024 (2024-10-11). Dataset: https://huggingface.co/datasets/ai-safety-institute/AgentHarm — **B**
16. **Debenedetti, E., et al.** — *Defeating Prompt Injections by Design (CaMeL).* arXiv:2503.18813 (2025-03). Code: https://github.com/google-research/camel-prompt-injection — **B** *(paper text unread; the repository's research-artefact disclaimer was verified — **A**). An IEEE CSDL listing surfaced suggesting an IEEE SaTML 2026 proceedings article — **unverified**.*
17. **Beurer-Kellner, L., Buesser, B., Creţu, A.-M., Debenedetti, E., Dobos, D., et al.** — *Design Patterns for Securing LLM Agents against Prompt Injections.* arXiv:2506.08837 (2025-06). DOI: 10.48550/arXiv.2506.08837 — **B**
18. **Lee, D., Tiwari, M.** — *Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems.* arXiv:2410.07283 (2024-10-09) — **B**
19. **Dong, S., et al.** — *Memory Injection Attacks on LLM Agents via Query-Only Interaction (MINJA).* arXiv:2503.03704 — **B** *(a NeurIPS 2025 poster listing surfaced, and a v4 dated 2025-12-10; neither confirmed at source).*
20. **Evtimov, I., et al.** — *WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks.* arXiv:2504.18575 (2025-04-22) — **B** *(a secondary source places it in the NeurIPS 2025 D&B track — unverified).*
21. **Wei, Q., et al.** — *A-MemGuard: A Proactive Defense Framework for LLM-Based Agent Memory.* — **B** *(an ICML 2026 poster listing and an OpenReview entry surfaced; unverified).*
22. *Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents.* arXiv:2605.16282 — **B**. **Must be read in full before §2 is finalised** to avoid duplicating its comparison.
23. *A Survey on Agentic Security: Applications, Threats and Defenses.* arXiv:2510.06445 — **B**
24. *Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges.* arXiv:2510.23883 — **B** *(one bibliography places this in IEEE Access 2026 — unverified).*
25. *A Comprehensive Survey in LLM(-Agent) Full Stack Safety.* arXiv:2504.15585 — **B**
26. *Reflections on the Reproducibility of Commercial LLM [studies].* arXiv:2510.25506 — **B**
27. **Alshammari, A. A., et al.** — *Detecting Prompt Injection Attacks in Generative AI Systems.* Electronics 15(11):2242, 2026 — **B** *(an abstract-level surveillance source only; content unread).*
28. **Ferrag, M. A., et al.** — *From prompt injections to protocol exploits: Threats in LLM-powered AI agents workflows.* 2025. DOI: 10.1016/j.hcc.2025.100299 (link uncertain) — **B**
29. **Duarte, J. D., et al.** — *A Systematic Review of Prompt Injection Attacks on Large Language Models.* IEEE 2026 — **B** *(noted because it explicitly identifies a research gap regarding multi-LLM/multi-model agent applications, which is relevant to §E; content unread).*

### Standards, frameworks and authoritative practitioner sources

30. **Han, Y., Chen, M., Yu, Y., Lin, J.** — *Security Evaluation Benchmark for AI Agents.* IETF Internet-Draft `draft-han-bmwg-agent-security-benchmark-00`, BMWG, Informational, published 2026-07-05, expires 2027-01-06. https://www.ietf.org/archive/id/draft-han-bmwg-agent-security-benchmark-00.html — **A**. **Cite only as a work in progress**, per the document's own status statement. Defines 4 first-level dimensions and 55 second-level metrics; static, dynamic, attack–defence, compliance and quantitative methodology; §4.2.2 excludes non-reproducible external inputs from standardised evaluation.
31. **OWASP GenAI Security Project** — *Agentic AI – Threats and Mitigations*; *Multi-Agentic System Threat Modeling Guide v1.0* (2025-04-23); *OWASP Top 10 for Agentic Applications for 2026* (2025-12); *Agentic Security Initiative*; *Agentic Security Solutions Landscape* (Q3 2025). https://genai.owasp.org/ — **B** (resource pages verified to exist; contents unread).
32. **NVIDIA garak** — model-level LLM vulnerability scanner — **B** (existence and open-source status solid; the frequently quoted "120+ probes" figure is **C**).
33. **Microsoft PyRIT** — Python Risk Identification Toolkit for generative AI — **B** (the "100+ red-teaming operations" figure is vendor-sourced, **C**).
34. **promptfoo** — LLM/agent application testing, CI integration, and the LLM Security Database referenced repeatedly here — **B**.

### Community artefacts — explicitly **not** citable as peer-reviewed benchmarks

35. **AgentInjectionBench** — Hugging Face datasets `sincpp/AgentInjectionBench` and `ppradyoth/AgentInjectionBench` — **A** (dataset pages fetched). **No peer-reviewed publication, venue, affiliated paper or DOI located.** Schema fields observed: `id`, `attack_category`, `attacker_intent`, `injection_surface`, `complexity`, `target_tools`, `defense_bypass`, `system_prompt`, `tools_available`, `conversation`, `ground_truth`, `severity`, `notes`. Observed `complexity` value: `single_turn`. Useful as a schema reference and as a candidate secondary comparison set only. Contains live prompt-injection payloads — handle as an attack corpus.

### Model documentation (configuration metadata only — see §6)

36. DeepSeek V4 / V4-Flash API documentation and release notes; Hugging Face DeepSeek-V4 blog — **B/C**. Exact status of a **"V4.1 Flash"** designation: **unconfirmed**.
37. **MiMo-V2-Flash** vendor blog, repository and technical report (arXiv:2601.02780 surfaced) — **B**. A **2.6** generation appears in vendor model-release documentation; **unconfirmed**.
38. **GLM-5** vendor blog (2026-02-11) and subsequent 5.1/5.2 posts — **B**. A **5.3 Flash** variant: **unconfirmed**.
39. **Solar Mini 4** (`solar-mini4-260922`, reported 2026-09-22) — **B/C**. Vendor launch note not fetched.

### Not verified in this pass — do not cite yet

**MITRE ATLAS**; **NIST AI 100-2 (Adversarial Machine Learning taxonomy)**; **SafeAgentBench**; **MobileSafetyBench**; **R-Judge**; **AgentAuditor / ASSEBench** (a NeurIPS 2025 poster listing surfaced); **MCP-SafetyBench** (arXiv:2512.15163 surfaced); **MCP-TDP Security Benchmark** (arXiv:2605.24069 surfaced); **MCP-ITP** (arXiv:2601.07395 surfaced); **tau-bench**/**τ²-bench**; **AgentBench**; **MultiAgentBench**; **AgentSmith**; **Dreadnode AI red-team benchmark**; **"Stronger Adaptive Attacks Bypass Defenses"** (arXiv:2510.09023 surfaced). Each of these must be located and read at source before citation.

---

## Appendix: immediate next actions before any experiment

1. **Full-text reading list** (blocking): AgentDyn; Zhan et al. (2503.00061); Kirgis et al. (2605.08545); Progent; RAS-Eval; ASB; AgentDojo; the taxonomy/consistency paper (2605.16282, to avoid duplicating its comparison); the IETF draft in full.
2. **Systematic database search** (Scopus / Web of Science / ACM DL / IEEE Xplore) with a documented, reproducible query string, to replace search-engine sampling and to check gaps 4 and 5 for prior art.
3. **Model verification** (§6): obtain vendor-issued spec pages and exact API IDs for all four models; determine whether weights are downloadable and hash-pinnable.
4. **Resolve the venue questions** in §M items 8 and 15–21, or drop the venue claim.
5. **Decide the model-set question** (§6): add capability-spread models, or narrow the claims and drop Direction II.
6. **Check provider terms** for redistribution of raw model outputs — this gates the entire §J reproducibility design.
