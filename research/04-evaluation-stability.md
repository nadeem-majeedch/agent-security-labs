# Reproducibility and Stability of Agent-Security Conclusions Under Repeated Evaluation

**Status:** working analysis, not a paper. Pass 4 of the AgentSec Lab landscape work.
**Date:** 2026-09-25.
**Extends:** `research/01-landscape-and-gap-analysis.md`, `research/02-capability-vs-security-analysis.md`, `research/03-asr-decomposition-gap-analysis.md`.

---

## 0. Headline finding, stated first

The candidate direction is **real but crowded**. Classification: **C — partially
addressed**, with one narrow **D — weakly addressed** residual.

Three findings dominate this pass, all verified at primary source:

1. **NIST/CAISI already ran the most on-point experiment** (Jan 2025, updated Dec 2025).
   Using **AgentDojo** with Claude 3.5 Sonnet, they attempted each of five injection tasks
   **25 times**, and report: *"After repeated attempts, the average attack success rate
   increased from 57% to 80%, and the attack success rate for individual tasks changed
   significantly."* Their Insight #4 is verbatim: *"Testing the success of attacks on
   multiple attempts may yield more realistic evaluation results."*
2. **The "how many repetitions" question is answered in the general LLM-evaluation
   literature.** Alvarado Gonzalez et al., *Do Repetitions Matter?* (`arXiv:2509.24086`,
   Sep 2025): 8 models, 3 runs each, and *"Single-run leaderboards are brittle: 10/12 slices
   (83%) invert at least one pairwise rank relative to the three-run majority."* They
   recommend ≥2 repetitions.
3. **A cross-benchmark concordance analysis already exists for agent safety.**
   Li, Fung, Li, Ismail & Iqbal (`arXiv:2605.16282`, Apr 2026) analyse 40 agent-safety
   benchmarks and report *"no evidence of ranking concordance across evaluation dimensions
   (Kendall's W = 0.10, p = 0.94)"*, with 95% CIs, and release minimum reporting standards.

What remains genuinely open is narrow and specific: **no located study measures the
intra-case correlation of agent-security outcomes, derives from it how many repetitions
comparative conclusions require, and combines that with attacker-budget variation on
defenses.** Every ingredient exists separately; the intersection does not.

This is a defensible empirical contribution. It is not a framework, and it must not be
presented as one.

Labels: **A** read at primary source · **B** search-result level · **C** unverified.

---

## 1. Defining the research problem

### 1.1 The question, precisely

Fix the entire experimental configuration `θ` = (model, model revision, agent scaffold,
system prompt, task set, attack payload set, defense configuration, tool layer, environment
version). The question is whether the **conclusion** — not the point estimate — is stable
when `θ` is held fixed and only stochastic variation is allowed to vary.

Two distinct conclusions must be separated, because they are affected differently:

| Conclusion type | Form | Why it can be unstable |
|---|---|---|
| **Absolute** | "Defense A reduces ASR to 7.5%" | Point estimate moves with run-to-run variance |
| **Comparative** | "Defense A is better than Defense B" | *Ranking* can invert even when both estimates move together, if the gap is smaller than the noise. Pathade et al. show a 100-instance benchmark inverts a true 5pp gap ≈21% of the time |

The comparative conclusion is the one the field actually consumes, and the one that is
fragile. This distinction is the crux of the whole direction.

### 1.2 Sources of variation, and what can realistically be controlled

| # | Source | Controllable? | Notes |
|---|---|---|---|
| V1 | **Sampling temperature** | **Yes** — a declared parameter | But `temperature = 0` does **not** guarantee determinism (§1.3) |
| V2 | **Random seed** | **Provider-dependent** | OpenAI offers best-effort `seed` + `system_fingerprint`; most providers do not expose seeds at all. **Must be verified per provider before the study is designed** |
| V3 | **Model non-determinism** (batching, MoE routing, kernel non-determinism, floating-point reduction order) | **No** — not controllable via API | The dominant and most-misunderstood source. See §1.3 |
| V4 | **Tool outputs** | **Yes** if tools are simulated/deterministic; **no** for live MCP/network tools | RAS-Eval's simulated mode uses an in-memory dict with deterministic outputs; real mode has "Full latency/errors" (R03) |
| V5 | **Retrieval order** | **Yes**, if we own the retriever | Not relevant for AgentDojo (no retrieval); highly relevant for MCP/RAG settings |
| V6 | **Environment state** | **Yes** — reset per episode | But state *carried* between steps creates path dependence within an episode |
| V7 | **Attack variation** | **Partly** — payloads are fixed text, but *whether the payload is placed in a read position* depends on the trajectory | This is Pathade's A4/A5 territory |
| V8 | **Judge / oracle variation** | **Partly** — fix the judge model and prompt; but judge calls are themselves stochastic | Pathade §V-B: judge error is *differential* across systems, which is what actually reverses rankings |
| V9 | **Attacker budget** | **Yes** — an explicit design variable | NIST varied it (1 → 25 attempts); Pathade finds only **10.8%** of 259 papers state a budget at all |

**The honest scoping statement:** V1, V4, V5, V6, V7 (payload text) and V9 are
controllable. **V3 is not controllable and never will be via a hosted API** — it can only be
*measured*. V2 is providentially available or not. V8 can be held fixed in form but not in
outcome.

That scoping is itself a contribution: much of the field writes as though `temperature = 0`
makes evaluation reproducible, and it does not.

### 1.3 Why `temperature = 0` is not determinism

Verified at search/primary level (**B** for the vendor-facing claims, **A** for the
statement that this is a live concern):

- "The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism"
  — *"Temperature-zero BF16 LLM inference is often treated as reproducible, yet the same
  request can emit different tokens when decoded alone or inside a larger batch."*
  (**B**)
- Batch-invariance as the mechanism (Thinking Machines Lab's "Defeating Nondeterminism in
  LLM Inference"; vLLM issue trackers showing same-request divergence under different
  batching/DP replicas). (**B**)
- `arXiv:2601.07239` refers to *"recent work on LLM stability and reproducibility [showing]
  that repeated nominally deterministic runs—e.g., temperature T=0 with fixed…"* (**B**)

**Consequence for the design:** we must assume stochasticity, measure it empirically, and
**not** claim to have eliminated it. If a provider supports no seed, that is a finding, not
a blocker — it means the measured variance is the *real* deployable variance, which is
arguably the more useful quantity.

---

## 2. Prior work (2023–2026)

### 2.1 Agent-security-specific

| Source | Level | What it establishes |
|---|---|---|
| **NIST/CAISI, "Strengthening AI Agent Hijacking Evaluations"** (2025-01-17, updated 2025-12-19) | **A** (government technical blog; **not peer-reviewed**) | Uses **AgentDojo** + upgraded Claude 3.5 Sonnet. Four insights. **#4: repeated attempts.** Five injection tasks × **25 attempts** → *"the average attack success rate increased from 57% to 80%, and the attack success rate for individual tasks changed significantly."* **#3: task-specific vs aggregate.** Aggregate 57% hides tasks "well over 57%" and tasks "markedly less successful." **#2: adaptivity** — 11% for strongest baseline attack → **81%** for a new red-team attack developed against the model, then generalising to the other three environments. Open-sourced: `github.com/usnistgov/agentdojo-inspect` |
| **Pathade, Pawar & Patil, "Attack Success Rate Is Not a Number"** (`arXiv:2609.25173`, 2026-09) | **A** (full text) | See §3 |
| **Li et al., "Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents"** (`arXiv:2605.16282`, 2026-04) | **A** (abstract) | 40 behavioral agent-safety benchmarks (2023–2026) + 5 adjacent artifacts; six-axis taxonomy of evaluation methodology; corpus-wide codings. Findings: *"benchmark choice can yield contradictory safety conclusions"*; *"coverage counts often overstate evaluation depth"*; *"environment fidelity systematically shapes reported safety"*; *"metric fragmentation limits comparison"*; *"robustness remains effectively unbenchmarked."* **Cross-benchmark consistency check with 95% CIs and Kendall's W: "no evidence of ranking concordance across evaluation dimensions (W = 0.10, p = 0.94)."** Releases metadata, codings, artifacts, and **minimum reporting standards** |
| **REDAgentBench** (`arXiv:2608.10669`, 2026-08) | **A** (abstract) | *"reported ASR varies with harness and evidence view, while evaluation-context disclosure changes execution behavior."* 1,661 cases, six models, three harnesses |
| **AgentDojo** (`arXiv:2406.13352`) | **A** (full text) | Reports **95% CIs** via `statsmodels.stats.proportion.proportion_confint`; reports the estimated cost of running the full suite on GPT-4o (checklist 3(d)) |
| **`arXiv:2604.23887`** (2026-04) | **B** | "the attacker generates 10 attack prompts. Each attack is then sent to the defender and the response recorded. Responses are scored…" — some repetition discipline in prompt-injection defense evaluation |
| **SSP-Bench** (`arXiv:2609.25352`, ~2026-09-21) | **B** | *"ranking instability is service-dependent and predictable, exposing family-specific failures such as inverse safety scaling in Gemma-3"* |
| **"Persona Non Grata: Single-Method Safety Evaluation Is In…"** (OpenReview) | **B** | Figure: *"Persona Rank Inversion Between Methods"*; *"Reverse: dangerous under SP, safe under AS"* — **safety rank inversions between single evaluation methods** |
| **SafeBoundary-LLM** (MDPI *Computers* 15(7):460, 2026) | **B** | *"LLM-as-judge evaluation may be affected by evaluator reliability limits, positional bias, and ranking instability"* |
| **"AIDG"** (2026-02) | **B** | *"defensive ranking instability discussed in Section 5"* |

### 2.2 General LLM / safety evaluation (directly applicable)

| Source | Level | What it establishes |
|---|---|---|
| **Alvarado Gonzalez et al., "Do Repetitions Matter? Strengthening Reliability in LLM Evaluations"** (`arXiv:2509.24086`, 2025-09-28) | **A** (abstract) | 8 SOTA models, **AI4Math**, **3 independent runs** per setting. Methods: mixed-effects logistic regression, domain-level marginal means, **rank-instability analysis**, run-to-run reliability. Findings: *"Single-run leaderboards are brittle: 10/12 slices (83%) invert at least one pairwise rank relative to the three-run majority"*, despite *"a zero sign-flip rate for pairwise significance and moderate overall interclass correlation."* *"Averaging runs yields modest SE shrinkage (∼5% from one to three) but large ranking gains; two runs remove ∼83% of single-run inversions."* Recommends **≥2 repetitions** under stochastic decoding |
| **"Quantifying Variance in Evaluation Benchmarks"** (OpenReview) | **B** | Benchmark variance quantification |
| **ReasonBENCH, "Benchmarking the (In)Stability of LLM Reasoning"** (`arXiv:2512.07795v2`) | **B** | *"Run Noise measures within-benchmark z-score variance, isolating repeated-run stochasticity from benchmark difficulty"* — a variance-decomposition method |
| **Yao et al., τ-bench** (`arXiv:2406.12045`) | **A** (search-level quotes of the paper) | *"We also propose a new metric (**pass^k**) to evaluate the reliability of agent behavior over multiple trials."* `pass^k` = *"the probability that a task is successfully completed in all k independent trials."* *"All models show dramatic drops in the pass^k metric."* **This is the established agent reliability metric** |
| **Miller, "Adding Error Bars to Evals"** (`arXiv:2411.00640`, R56) | **B** | Statistical approach to LLM evaluations |
| **Biderman et al., "Lessons from the Trenches on Reproducible Evaluation"** (`arXiv:2405.14782`, R27) | **B** | Reproducible eval practice |
| **Carlini, Athalye et al., "On Evaluating Adversarial Robustness"** (`arXiv:1902.06705`, R57) | **B** | The methodology-checklist precedent the whole area is importing |
| **Kirgis et al.** (`arXiv:2605.08545`, R09) | **A** | pass^5 under-elicited by nearly 50% on tau-Bench Airline — repeated-run reliability already a live problem in *benign* agent evaluation |

### 2.3 The picture these sources form together

The stability problem has been attacked from four directions, and each is occupied:

- **Reporting practice** — Pathade et al. (259 papers; 65.3% no variance/repeats).
- **Analytical consequence** — Pathade et al. (MDD ≈18.2pp at n=100; 21% inversion at 5pp).
- **General empirical demonstration** — Alvarado Gonzalez et al. (83% of slices invert);
  ReasonBENCH; "Quantifying Variance".
- **Domain-specific initial demonstration** — NIST/CAISI (AgentDojo, 25 attempts, 57%→80%);
  Li et al. (cross-benchmark W = 0.10, p = 0.94); REDAgentBench (harness/evidence view).

What is **not** occupied: the *within-benchmark, across-repetition* stability of
**defense and model rankings in agent security**, with **variance components estimated**
and **attacker budget as a crossed factor**. That is a narrow, specific, and testable
residual.

---

## 3. Audit of Pathade et al. (`arXiv:2609.25173`)

Read in full (**A**). Distinguishing what the paper does from what it recommends.

### A. What it establishes **theoretically / analytically**

| Item | Status |
|---|---|
| ASR is a family of metrics parameterised by design choices, not a single quantity | **Established** |
| Formalisation `ASR̂ = (1/|U|) Σ_{u∈U} O(τ_u)`, with `U`, `O`, `τ_u ∼ π_θ(·|u)` all researcher-chosen | **Established** |
| Six axes of divergence: A1 unit of analysis, A2 oracle, A3 trials/non-determinism, A4 attacker adaptivity, A5 attacker knowledge of defence, A6 binarisation | **Established** |
| Claim that the shift is **system-dependent** (not a constant offset that cancels in comparison) for A1, A2, A4, A5 but **not** A3 or A6 | **Advanced analytically** |
| Minimum detectable difference at 80% power, α=0.05: ≈**18.2pp** at m=100 | **Established (closed form)** |
| Single-run rank inversion probability: ≈**21%** for a true 5pp gap at m=100; ≈38% for 2pp | **Established**, with a 200,000-trial Monte Carlo check on three cells agreeing within 2.3 points and indicating the normal approximation slightly *understates* inversion (.214 vs .237 at m=100, δ=5pp) |
| Oracle differential error: `p̂ = p(1−β) + (1−p)α`; inversion when `(1−β_B)/(1−β_A) < p_A/p_B` | **Established**; the paper states honestly that inversion needs *substantial* differential error, and that the real issue is unmeasured judge calibration |

### B. What it establishes **empirically**

| Item | Status |
|---|---|
| **Reporting-practice rates across 259 agentic-security papers** (2025-02-27 → 2026-09-17; 43 from 2025, 216 from 2026) | **Established.** Variance/CI 23.9%; repeated runs 20.5%; **neither 65.3%** (hand-coded sample of 50: **58.0%**, 95% Wilson CI 44.2–70.6); decoding info 30.9%; temperature 20.8%; seed 15.1%; LLM judge ≥24.7%, of those 29.7% report human-agreement checks; adaptive attacker 30.5%; attack budget 10.8%; attacker knowledge of defence 16.2%; partial success 2.3%; **benign-task utility 37.8%**; code released 65.3% |
| **A measured quantity of run-to-run variance in agent security** | **NOT established.** The paper measures *reporting*, not variance |
| **An empirical ranking inversion** | **NOT established — explicitly so** |
| **How much variance comes from the agent itself / attack generation / stochastic sampling / environment-tool behaviour** | **NOT established.** No variance decomposition is performed |
| **Any end-to-end evaluation** | **NOT performed** |

The paper says so unambiguously:

> *"We have not run defenses end to end, so we report no empirical ranking inversion; that
> experiment is the natural next step and needs model access we did not have."*

### C. What it **recommends**

A ten-item reporting checklist. The items relevant to us:

| # | Item | Current rate |
|---|---|---|
| 1 | Unit of analysis, and `|U|` | — |
| 2 | The oracle (and judge model + prompt if judged) | oracle family not codable |
| 3 | Judge calibration vs human labels on a subsample | 29.7% |
| 4 | Runs per configuration; if one, say so | 20.5% report >1 |
| 5 | Variance: interval; claim no improvement smaller than the MDD | 23.9% |
| 6 | Decoding: temperature, top-p, seeds | 30.9% |
| 7 | Attacker static/adaptive, plus the query budget | 10.8% |
| 8 | What the attacker knows about the defence | 16.2% |
| 9 | Partial-success binarisation rule, incl. refused-then-retried | 2.3% |
| 10 | **Benign-task success under the same defence** | 37.8% |

The checklist is *"proposed, not validated"* — their own words.

### D. What remains **untested**

Cross-referencing the brief's nine questions against what Pathade et al. actually did:

| Question | Already answered? |
|---|---|
| How many repetitions are needed for stable agent-security conclusions? | **Partly.** General LLM: ≥2 runs (2509.24086), but on a math benchmark. Agent security: **no empirical answer**. Pathade gives MDD vs *cases*, not a trials-vs-stability curve |
| How often do defense rankings change under repeated evaluation? | **NO** — explicitly left undone |
| How much variance comes from the agent itself? | **NO** |
| How much variance comes from attack generation? | **NO** |
| How much variance comes from stochastic model sampling? | **NO** |
| How much variance comes from environment/tool behaviour? | **NO** |
| Whether repeated evaluation changes **model** rankings? | **NO** (analytical prediction only; the two-runs result is from a non-security benchmark) |
| Whether repeated evaluation changes **defense** rankings? | **NO** |
| Whether confidence intervals are sufficient to resolve ranking instability? | **Partly, analytically** — their §V shows CIs at realistic sizes are too wide, which implies CIs are *necessary but not sufficient*. Not tested empirically |

**Critical limitation of their own analysis, which they state:** the §V results are
analytical and *"under independence assumptions real benchmarks violate — correlated tasks
and shared environments make effective sample size smaller than m, so our MDDs are
optimistic."*

**That sentence is the opening.** They compute an MDD assuming independent units. Real
agent-security benchmarks have correlated outcomes across *repeated runs of the same case* —
which is precisely the quantity nobody has measured. A design-effect-corrected MDD
requires the intra-case correlation, which requires exactly the experiment nobody has run.

---

## 4. Ranking instability: does the specific study exist?

Searching for whether `Defense A > Defense B` survives across seeds, trials, attack samples,
models, budgets, and configurations:

| Comparison axis | Work that tests it | Level |
|---|---|---|
| Across **benchmarks** (agent safety) | Li et al. `arXiv:2605.16282` — *"no evidence of ranking concordance across evaluation dimensions (W = 0.10, p = 0.94)"*, 95% CIs | **A** (abstract) |
| Across **runs**, non-security, model rankings | Alvarado Gonzalez et al. `arXiv:2509.24086` — 83% of slices invert ≥1 pairwise rank; 2 runs remove ~83% of inversions | **A** (abstract) |
| Across **runs**, reasoning | ReasonBENCH `arXiv:2512.07795` — run-noise variance | **B** |
| Across **attack attempts** (budget), agent security | **NIST/CAISI** — 25 attempts, AgentDojo, ASR 57%→80%, per-task ASR changed | **A** (non-peer-reviewed) |
| Across **harnesses / evidence views**, agent security | REDAgentBench `arXiv:2608.10669` | **A** (abstract) |
| Across **evaluation methods**, safety personas | "Persona Non Grata" — persona rank inversion between methods | **B** |
| Across **services**, safety | SSP-Bench `arXiv:2609.25352` — ranking instability service-dependent | **B** |
| Across **runs**, **defense rankings in agent security** | **Not located** | — |
| Across **runs × budget**, **defense rankings in agent security** | **Not located** | — |

**Reading.** Every *component* of §4 exists. The *specific* combination — repeated
stochastic runs of a real agent-security benchmark, multiple defenses, multiple models, with
variance components and a budget axis, measuring rank stability — was not located.

Two caveats I must state honestly:

1. **Absence of a located study is not absence of a study.** My search was bounded; the R21
   corpus (40 benchmarks) and Pathade's corpus (259 papers) may contain work I did not
   retrieve by search.
2. **R21 is the most dangerous overlap.** It already combines a taxonomy, a consistency
   analysis, CIs, a rank-concordance statistic, minimum reporting standards, and an artifact
   release — in agent safety. The difference is that its concordance is **between**
   benchmarks and dimensions, not **within** a benchmark across runs. That distinction must
   be made explicitly and early in any write-up, or a reviewer will treat our work as
   subsumed.

---

## 5. Attacker budget × repeated evaluation

Has the complete design (budgets 1, 5, 10, 25, 50 × N repeated stochastic trials ×
defense success × utility × cost × variance × CI) been performed?

| Element | Exists? | Source |
|---|---|---|
| Budget → ASR, agent security | **Yes, one point** | NIST/CAISI: 25 attempts on 5 injection tasks, 1 model, ASR 57%→80% |
| Budget → ASR, industry practice | **Yes, as a curve** | A vendor technical blog cited in search reports *"17.8% success at 1 attempt, rising to 78.6% at 200 attempts without safeguards and 57.1% with…"* — **B, and the underlying primary source is unidentified; do not cite** |
| Budget stated at all in the literature | **Rarely** | Pathade: **10.8%** of 259 papers |
| Budget defers to future work | **Yes** | Nasr et al. (R48): adversary compute deliberately unbounded; *"it would be interesting to investigate to what extent it is possible to achieve strong attacks… more efficiently"* |
| Budget as an AgentDojo design gap | **Yes** | AgentDojo future work (v): constraints on injection "length or format" to capture realistic adversary capabilities |
| GCG-style query accounting | **Yes, but as a fixed cost** | 500 steps × 512 queries/step × 20-token suffix (quoted in R48); not swept as an independent variable |
| **Budget × repeated trials × variance × CI × defenses** | **Not located** | — |

**Assessment.** The *combination* is unoccupied, but it is also **telegraphed from three
directions simultaneously** (NIST's Insight #4, R48's declared future work, AgentDojo's
future-work item). A budget study is therefore a *component* of a defensible design, not a
standalone contribution. It should never be the headline.

---

## 6. Evaluating the three candidate research questions

| # | Candidate question | Class | Evidence |
|---|---|---|---|
| **Q1** | "How stable are comparative security conclusions for LLM-based agents under repeated stochastic evaluation?" | **C — partially addressed** | General form **solved** (2509.24086: 83% inversion, ≥2 runs). Cross-benchmark agent-safety form **solved** (Li et al., W=0.10). Analytical agent-security form **solved** (Pathade, 21% inversion at 5pp). Agent-security **empirical** form: only NIST's single-model, 5-task, no-CI demonstration. **Residual: real but narrow** |
| **Q2** | "How does attacker query budget interact with statistical uncertainty in agent-security evaluation?" | **D — weakly addressed, edging to C** | NIST shows budget moves ASR but reports no uncertainty and no curve. Pathade: 10.8% state a budget; their A4 axis covers adaptivity but not the budget–uncertainty interaction. R48 declares it future work. **No located study crosses budget with variance** |
| **Q3** | "How many independent trials are required before defense rankings become statistically stable?" | **C — partially addressed** | The general answer exists for capability benchmarks (≥2 runs, 2509.24086). Pathade gives MDD as a function of *cases*, and explicitly notes their MDDs are optimistic under correlated outcomes. **No located answer for agent-security defenses, none corrected for the design effect** |

**None is E (potentially novel).** None is F (too vague) either — all three are precise and
testable. The honest summary is that **Q1 and Q3 are refinements of published results;
Q2 is the least-covered of the three, and it is only interesting in interaction with Q3.**

**The strongest formulation is the intersection:**

> **Given the intra-case correlation of agent-security outcomes, how many repetitions are
> required for comparative security conclusions (defence and model rankings) to stabilise —
> and how does attacker budget interact with that requirement?**

This differs from 2509.24086 (capability benchmark, no adversary), from Pathade (no
empirical measurement), from Li et al. (between-benchmark, not within-run), and from NIST
(single model, no uncertainty, no defenses). It is empirical, cheap, and falsifiable.

---

## 7. Possible contribution

### 7.1 Elements: what is established vs what is open

| Element | Established? | Prior art |
|---|---|---|
| Point estimate | **Established** | Every benchmark |
| Confidence interval on ASR | **Established** — Wilson/binomial; AgentDojo already reports 95% CIs | AgentDojo; Pathade item 5 |
| Variance estimate | **Established method**, rarely applied in agent security | Pathade (23.9% do it) |
| **Variance decomposition by source** (case vs run vs model) | **Method established in general eval; not applied in agent security** | ReasonBENCH run-noise; 2509.24086 ICC |
| Effect size | **Established** | — |
| **Ranking stability** | **Established method** (rank-inversion vs high-repetition majority; Kendall's W) | 2509.24086; Li et al. |
| Minimum sample size / MDD | **Established formula**, but **uncorrected for clustering** | Pathade §V-A |
| Attacker-budget sensitivity | **Demonstrated once**, without uncertainty | NIST |
| **pass^k run-to-run reliability** | **Established metric for agents** | τ-bench (Yao et al. `arXiv:2406.12045`) |

### 7.2 The contribution, stated without inflation

> **Measure the design effect and intra-case correlation of agent-security outcomes, use
> them to correct the minimum detectable difference for comparative security claims, and
> report how rank stability depends on repetition count and attacker budget.**

Four things make this more than "proper statistical reporting":

1. **A measured quantity nobody has: the intra-case correlation ρ of agent-security
   outcomes.** It determines the design effect `1 + (m−1)ρ` and therefore the *effective*
   sample size. Pathade's own headline MDD of 18.2pp is optimistic precisely because ρ is
   unmeasured. **Our ρ would let every existing agent-security benchmark's MDD be
   recomputed.**
2. **A non-obvious, testable asymmetry.** 2509.24086 found that going from 1→3 runs bought
   only ~5% SE shrinkage but removed ~83% of rank inversions. If that asymmetry replicates
   in security, it means *precision* and *ranking stability* respond to repetitions on
   different scales — a genuinely useful result for practitioners deciding how to spend
   compute.
3. **Budget as a crossed factor with uncertainty.** No located study reports a
   budget→ASR curve with confidence intervals, let alone budget × repetition interaction.
4. **A design-effect-corrected MDD table** that a benchmark author can read off. This is the
   item with the clearest practical audience.

**What it is not:** a new framework, a new metric, a new benchmark, or a decomposition. Do
not name the result anything except the established terms (MDD, design effect, ICC,
`pass^k`, Kendall's W, rank inversion).

### 7.3 The trap to avoid

The strongest version of the reviewer objection is not "this is just statistics." It is:
**"You have re-measured a property of one benchmark, not of agent security."** ρ, ICC, and
the design effect are properties of a *task distribution*, not of the field. Answering that
objection requires either multiple benchmarks or an explicit, bounded claim. I recommend the
bounded claim: state that the measured quantities characterise the surveyed benchmark(s)
and give the recomputation recipe for others.

---

## 8. Minimal pilot experiment

Deliberately small. The purpose is to **estimate ρ and the variance components**, not to
test a hypothesis about defenses.

| Element | Specification |
|---|---|
| **Models** | 2 of the 4 available Flash models initially (add the other 2 once the pipeline is validated). Rationale in §10 |
| **Agent scaffold** | **One**, version-pinned. Adding a second harness later tests REDAgentBench's harness effect |
| **Attacks** | AgentDojo's existing injection attacks; **no new payload authoring** (avoids a benchmark-authorship confound and keeps results comparable to NIST's) |
| **Defenses** | **2 conditions**: (1) no defense; (2) one cheap deterministic defense — AgentDojo's **tool filter**, reported at 7.5% ASR. Add **prompt sandwiching** only if budget allows |
| **Tasks/cases** | A **pre-registered fixed subset** of AgentDojo security cases, `n = 100` — chosen deliberately so Pathade's ≈18.2pp MDD applies directly and can be corrected by our measured ρ. Subset selection stratified across the four environments |
| **Repetitions** | **10 runs per (model, case, defense, budget) cell** at temperature > 0. 10 (not 3) because the pilot's job is to *estimate* ρ, and ρ estimated from 3 runs is very noisy |
| **Seeds** | Use provider seeds **where supported**; otherwise record the absence as a finding. Do not claim determinism either way |
| **Temperature** | Fixed at one non-zero value (record it). Do not sweep — that is a separate study |
| **Attacker budget** | **Fixed at 1 attempt** for the pilot. The budget arm (1, 5, 25) is the *second* experiment, run only if the pilot shows the ranking-stability signal is worth pursuing |
| **Metrics** | Per-case binary attack outcome; benign task success; `pass^k` for k = 1…5; per-episode token cost and wall-clock; refusal rate |
| **Statistical tests** | §9 |
| **Total episodes** | 100 cases × 2 models × 2 defenses × 10 reps = **4,000 episodes**; ~1,000 per defense×model cell. For a Flash-tier API this is affordable |
| **Output** | ρ (intra-case correlation), ICC, design effect, corrected MDD, rank-inversion counts across repetition budgets (1, 2, 3, 5, 10), `pass^k` curve, cost per episode |

**Why this is the right size.** 4,000 episodes is enough to estimate ρ with usable precision
and to demonstrate the rank-stability curve; it is far short of what a claim about
*frontier* models would require, which is why the claim must be scoped to the models tested.

---

## 9. Statistical methodology

Chosen for the **actual structure**: binary outcomes, cases as the unit, repetitions nested
within cases, defenses paired within case, models crossed with everything.

| Method | Include? | Justification |
|---|---|---|
| **Wilson score intervals** | **Yes** — for all reported marginal proportions | Correct coverage at small n and extreme p (agent-security ASRs are often near 0% or near 80%). Strictly better than Wald |
| **Cluster-robust SEs / mixed-effects logistic regression** with a random intercept for case (repetitions nested within case) | **Yes — the core method** | Repeated runs on the same case are *not* independent. This is the single most important methodological requirement, and its absence is what makes Pathade's MDDs optimistic. Their own limitations acknowledge this |
| **McNemar's test** | **Yes** — for two-defense comparisons on the same cases | The natural paired test for binary outcomes on matched units |
| **Cochran's Q** | Yes, if >2 defenses | Generalises McNemar to k conditions |
| **ICC / variance components** | **Yes** | Directly estimates ρ and answers "how much variance is run vs case" |
| **Design effect** `1 + (m−1)ρ` and effective sample size | **Yes** | Converts ρ into a corrected MDD. The practical output |
| **`pass^k`** | **Yes** | Established agent-reliability metric (τ-bench). Do not invent a replacement |
| **Rank-inversion analysis** vs a high-repetition majority; **Kendall's W** for concordance | **Yes** | Both established (2509.24086; Li et al.). Reuse rather than invent |
| **Bootstrap intervals** for derived quantities (ρ, design effect, rank-inversion probability) | **Yes, limited** | Appropriate for non-standard functionals; not needed for the primary proportions, where Wilson is cleaner |
| **Power analysis / MDD** | **Yes** | Pathade's closed form, corrected by the measured design effect |
| **Sequential analysis / early stopping** | **No** | No need; adds complexity and pre-registration burden |
| **Bayesian hierarchical estimation** | **Only for per-case estimates** if partial pooling is needed to stabilise small-n cases | Unnecessary complexity for headline numbers. Include only if the per-case variance component is unstable |
| **Permutation tests** | No | Covered by McNemar/Cochran's Q on matched binary data |

**Recommended headline stack:** Wilson intervals + mixed-effects logistic regression (case
random intercept) + McNemar for paired defense comparisons + measured ρ/ICC/design effect +
corrected MDD + `pass^k` + rank-inversion counts + Kendall's W.

**One methodological warning worth stating in any write-up:** with a moderate ρ (say 0.3) and
m = 10 repetitions, the design effect is `1 + 9(0.3) = 3.7`, so effective n ≈ 27% of nominal
— meaning **repeating runs is a very inefficient way to buy precision, even if it is an
efficient way to buy ranking stability.** Whether that holds is exactly the asymmetry
2509.24086 observed and exactly what we would measure.

---

## 10. Are the four available models sufficient?

**Reconsidered in light of the new goal.** The pass-2/3 objection was that the four models
lack a capability *ladder*. **That objection does not apply here** — this study makes no
claim about capability. What matters for a stability study is a different list:

| Requirement | Status |
|---|---|
| Multiple models, ideally from different providers | **Satisfied** — four, three Chinese vendors + one Korean |
| Cheap enough to run thousands of episodes | **Satisfied** — Flash/mini tier is exactly right; cost is the binding constraint on repetitions |
| Seed support | **UNVERIFIED — must be checked per provider.** If absent, that is a finding, not a blocker |
| Determinism at temperature 0 | **Will not hold** (§1.3). Must be measured, not assumed |
| Version pinning / revision identifiers | **UNVERIFIED** — still label B/C in `sources.csv` (R35–R38). **This is the one genuine blocker**, because a stability study whose model version drifts mid-experiment is measuring drift, not variance |
| Tool calling + structured output | Reported for all four, but **only at aggregator/vendor-blog level (B/C)** — must be verified |
| Parameter counts | **Irrelevant for this study.** Do not collect them, do not report them |

**Verdict: sufficient for the pilot and for a scoped claim about these four models.**
Insufficient for any claim about "LLM agents" generally. Specifically:

- **Adequate for:** estimating ρ, ICC, design effect, corrected MDD; demonstrating the
  rank-stability curve; the budget sweep.
- **Inadequate for:** generalising to frontier models, whose refusal training and
  determinism behaviour plausibly differ. State this as a scope limitation, not a caveat.
- **Prerequisite:** **verified revision identifiers for all four.** If a provider offers no
  way to pin a revision, that provider must be dropped or the drift must be measured and
  reported as an additional variance component.

This is a reversal of the pass-2/3 verdict, and it is a genuine one: the four Flash models
are a **liability for a capability claim** and an **asset for a stability claim**.

---

## 11. Open reproducibility: what to release

| Artifact | Release? | Notes |
|---|---|---|
| Benchmark case identifiers (subset list + selection seed) | **Yes** | The pre-registered subset, not the whole benchmark (which is already public) |
| Attack prompts / payloads | **Yes, with a usage note** | These are dual-use. Existing practice is to release (AgentInjectionBench, MCPTox, AgentDojo all do). Label the corpus as an attack corpus; do not embed it in prose |
| Defense configurations | **Yes** | Exact prompts / policy files, versioned |
| **Exact model identifiers** (provider, model string, **revision/fingerprint**) | **Yes — mandatory** | This is what makes the study a stability study rather than a drift study |
| API configuration (temperature, top-p, max tokens, seed param, retry policy, timeout) | **Yes** | Pathade checklist item 6 |
| Seeds | **Yes** — including "no seed support" | Pathade checklist item 6 |
| Temperatures | **Yes** | |
| Raw execution traces | **Release where ToS permit; otherwise release a schema + a redacted sample** | Provider ToS often restrict redistribution of raw API responses. Release the *structured* record regardless |
| Tool outputs and environment state | **Yes for simulated tools** | Deterministic and ours to publish |
| **Raw binary outcomes per (case, model, defense, rep)** | **Yes — this is the analytic substrate** | Even if traces cannot be released, this matrix can. It is sufficient for every reported statistic |
| Aggregate results | **Yes** | |
| Statistical scripts | **Yes** | R or Python, pinned |
| Confidence intervals | **Yes**, with the method named | |
| Figures | **Yes**, with generation scripts | |
| Experiment manifest (case list, cell ordering, run IDs, timestamps) | **Yes** | Reproducibility anchor |
| Docker environment | **Yes** | AgentDojo + harness + pinned deps |
| Dependency lockfiles | **Yes** | |

**Privacy / provider constraints to state explicitly:**

- Raw API responses may be redistributable only in derived form — release the per-case
  outcome matrix and a redacted trace sample, and say why the full traces are withheld.
- No user data is involved (simulated environments), so the privacy exposure is low; the
  binding constraint is **provider terms**, not privacy.
- Live-MCP or live-web tools must **not** be used, both for determinism (V4) and because
  their outputs cannot be redistributed.
- Release the "no seed" finding as a first-class limitation, not buried in an appendix.

**Against prior art:** AgentDojo releases code (R01); Pathade et al. released **no**
artifact repository; Li et al. release metadata and codings. A complete reproduction bundle
including the raw outcome matrix would be **above the current norm** and is therefore a
legitimate (if secondary) contribution.

---

## 12. Reviewer attack

Acting as a hostile reviewer.

### R1 — "This is merely proper statistical reporting."

**Partly true, and the strongest objection.** Wilson intervals, ICC, McNemar, and rank
correlation are textbook.

**Evidence needed:** a *result*, not a method. Specifically: a measured ρ, a
design-effect-corrected MDD, and a rank-stability curve that **changes a practical decision**
(a benchmark's recommended `n`, or a default repetition count). If the paper's contribution
can be summarised as "we recommend reporting CIs," it fails — Pathade et al. already
recommend that.

### R2 — "Pathade et al. already established this."

**True for the diagnosis; false for the measurement.** They explicitly did not run the
experiment (*"needs model access we did not have"*), and their MDDs assume independence,
which they acknowledge makes them optimistic.

**Evidence needed:** the measured ρ and the corrected MDD. That is a *number* they could not
produce. Frame the work as supplying the quantity their analysis assumes away — and cite
their limitation sentence directly.

### R3 — "Repeated runs do not constitute novelty."

**True in isolation.** Alvarado Gonzalez et al. ran 3 repetitions on 8 models in 2025; NIST
ran 25 attempts in 2025; τ-bench introduced `pass^k` in 2024.

**Evidence needed:** a *security-specific* result that does not follow from the capability
literature. The candidate: the 1→3-run asymmetry (small SE gain, large ranking gain) may not
replicate in security, because security outcomes are more clustered by case (a case is either
attackable or not) and more extreme in `p`. **If ρ is higher in security than in capability
benchmarks, the recommended repetition count differs — that is the novelty.** If ρ is
similar, the honest conclusion is that the general result transfers, which is a smaller but
still reportable finding.

### R4 — "The results will depend on the selected models."

**True by construction, and unanswerable at pilot scale.** Four Flash-tier models cannot
support a general claim.

**Evidence needed:** scoping, not more models. State the claim as "for the four models and
one benchmark tested," release the recomputation recipe, and report the model-to-model
variation in ρ as a *range* rather than a point. Do **not** write "LLM agents."

### R5 — "The experiment is too small."

**Contestable, and it cuts both ways.** Pathade's own analysis says a 100-instance benchmark
has an 18.2pp MDD. If our pilot uses 100 cases, we cannot resolve small effects — but the
pilot's purpose is estimating ρ, not detecting differences, and ρ is estimable from 100
cases × 10 reps.

**Evidence needed:** a pre-registered statement of exactly what each estimate can and cannot
support, plus the corrected MDD. Explicitly refuse to claim anything below the MDD. State
the design effect up front so no reader computes a naive power figure.

### R6 — "The stochasticity is API-specific."

**True and important.** Hosted-API variance includes batching, routing, and infrastructure
effects that a local deployment would not have. This is arguably a *feature* (it is the
variance a deployer actually faces) but it is not the variance of the model.

**Evidence needed:** (a) frame the measured quantity as **deployable variance** under the
specific API, not model variance; (b) if feasible, run one model both locally (open weights,
vLLM) and via API and report the difference — a cheap and very informative contrast;
(c) report revision identifiers so infrastructure changes are detectable.

### R7 — "The benchmark itself dominates the result."

**The most dangerous objection.** ρ and ICC are properties of a task distribution, not of
"agent security." PATH: Pathade's A1 (unit of analysis) and REDAgentBench's harness/evidence
finding both show that benchmark and harness choices move the number more than stochastic
noise does.

**Evidence needed:** either a second benchmark, or a frank statement that the estimates are
benchmark-specific and a recipe for recomputation. Li et al. already showed *between*-benchmark
non-concordance; if our *within*-benchmark noise is smaller than Li et al.'s
*between*-benchmark disagreement, that is a coherent and interesting combined story — and it
positions our work as complementary to R21 rather than competing with it.

---

## 13. Final decision

### A. Existing literature already covering this idea

1. **Pathade, Pawar & Patil (2026-09)** — diagnosis, six axes, 259-paper meta-analysis,
   analytical power/MDD, rank-inversion probability, checklist. **No empirical experiment;
   explicitly deferred.**
2. **NIST/CAISI (2025-01, updated 2025-12)** — repeated attempts on **AgentDojo**: 25
   attempts, ASR 57%→80%, per-task ASR changed; task-specific vs aggregate analysis;
   adaptivity (11%→81%); open-sourced harness.
3. **Alvarado Gonzalez et al. (2025-09)** — repetitions in general LLM evaluation: 3 runs,
   8 models, 83% of slices invert ≥1 pairwise rank, 2 runs remove ~83% of inversions,
   `≥2` repetitions recommended; mixed-effects logistic regression + rank-instability
   analysis.
4. **Li, Fung, Li, Ismail & Iqbal (2026-04)** — 40 agent-safety benchmarks, six-axis
   taxonomy, cross-benchmark consistency check with 95% CIs and **Kendall's W = 0.10,
   p = 0.94**, minimum reporting standards, artifacts released.
5. **REDAgentBench (2026-08)** — reported ASR varies with harness and evidence view.
6. **τ-bench (Yao et al. 2024)** — `pass^k`, the established run-to-run agent reliability metric.
7. **AgentDojo (2024)** — already reports 95% CIs and suite-run cost.
8. **Supporting:** ReasonBENCH (run-noise decomposition), "Quantifying Variance in Evaluation
   Benchmarks", Miller 2024, Biderman et al. 2024, Carlini et al. 2019; plus safety-side
   rank-inversion evidence (SSP-Bench, "Persona Non Grata", SafeBoundary-LLM, AIDG).

### B. What remains genuinely untested

Stated narrowly:

1. **The intra-case correlation ρ of agent-security outcomes** — unmeasured anywhere. It is
   the quantity that converts a nominal MDD into a real one, and Pathade et al. explicitly
   note their MDDs are optimistic without it.
2. **A design-effect-corrected MDD for agent-security benchmarks** — the practical output
   nobody has produced.
3. **Within-benchmark, across-repetition ranking stability for agent-security *defenses*** —
   the general result exists for capability; the cross-benchmark result exists for safety;
   the within-benchmark defense result was not located.
4. **Attacker budget crossed with uncertainty** — NIST shows budget moves ASR with no CIs and
   no curve; Pathade finds 10.8% of papers state a budget at all; R48 defers it.
5. **Whether the 1→3-run asymmetry transfers to security**, where outcome clustering is
   plausibly higher.
6. **Local vs API variance decomposition** for the same open-weight model.

### C. Is evaluation stability a viable research direction?

**Yes, but only in the narrow form, and only if we accept that it is an empirical
measurement rather than a framework.** It is viable because:

- The residual (§B) is specific, falsifiable, and cheap.
- The four Flash models are **well suited** (§10) — the pass-2/3 objection inverts.
- Every required method is established, so no methodological risk.
- **Both outcomes are informative.** If ρ is high, repetitions buy less precision than the
  field assumes and the correct remedy is *more cases or fewer claims*, not more runs. If ρ
  is low, single-run conclusions are already stable and the field's anxiety is misplaced in
  the agent-security setting. Either is a real result.

It is **not** viable as a general "we studied reproducibility" paper, and it will not survive
as a framework or a metrics proposal.

### D. The strongest defensible research question

> **Given the intra-case correlation of agent-security outcomes, how many repetitions are
> required for comparative security conclusions to stabilise — and how does attacker budget
> interact with that requirement?**

### E. The strongest possible contribution

> **A measured intra-case correlation and design effect for agent-security evaluation, a
> corrected minimum detectable difference that existing benchmarks can apply to their own
> results, and a rank-stability curve over repetition count and attacker budget.**

Framed as filling the estimation gap in Pathade et al.'s own limitations and as complementary
to Li et al.'s between-benchmark non-concordance. **No new metric, no new framework, no new
benchmark.** Reuse `pass^k`, ICC, design effect, Kendall's W, Wilson, MDD.

### F. The minimal pilot experiment

§8: 2 models × 2 defense conditions × 100 pre-registered AgentDojo cases × 10 repetitions
= 4,000 episodes at fixed non-zero temperature and fixed budget 1; estimate ρ, ICC, design
effect, corrected MDD, `pass^k`, rank-inversion counts; check seed support and revision
pinning first. Add the budget arm (1, 5, 25) only if the pilot shows a signal.

### G. What would falsify the research hypothesis

The hypothesis is *"repeated stochastic evaluation materially destabilises comparative
security conclusions in agent security."* It is falsified if:

- **ρ is near zero** (runs within a case are effectively independent), **and**
- **the rank-stability curve flattens at 1–2 repetitions** (i.e. single-run rankings already
  match the 10-run majority), **and**
- **the corrected MDD is close to the nominal MDD** (design effect ≈ 1).

In that case we must report: *comparative agent-security conclusions are more stable than the
general LLM-evaluation literature would predict, and the documented brittleness does not
transfer to this setting.* **That is a legitimate and publishable negative result, and we
should pre-register it as the outcome we would report.**

A second falsifier: if **benchmark identity dominates stochastic noise** by a large margin —
i.e. within-benchmark run variance is trivial compared to Li et al.'s between-benchmark
non-concordance — then the useful advice is "pick your benchmark carefully, don't run it
more," which again reverses the expected recommendation.

### H. The biggest reviewer objection

> *"This is a statistical audit of one benchmark, and both the diagnosis and the recommended
> remedies are already published — Pathade et al. for measurement validity, Alvarado Gonzalez
> et al. for the repetition question, NIST for the agent-hijacking demonstration, and Li et
> al. for the concordance analysis. Your measured ρ is a property of AgentDojo, not of agent
> security, and four Flash-tier models cannot support a general claim."*

**What would answer it, in order of strength:**

1. **The measured ρ**, because it is the one number Pathade's analysis explicitly assumes
   away, and it is what makes every existing agent-security MDD either valid or optimistic.
2. **A corrected MDD table** that changes what benchmark authors should do — a concrete
   deliverable, not advice.
3. **The 1→3 asymmetry tested in security** — if ρ differs materially from capability
   benchmarks, the general result does not transfer and the recommendation changes.
4. **Local vs API variance for one open-weight model**, which converts "API-specific
   stochasticity" from a weakness into a measured result.
5. **Explicit, bounded scoping** — one benchmark, four models, stated limits, plus a
   recomputation recipe. Li et al. already showed benchmarks disagree *with each other*; if
   we show runs within a benchmark agree *more* than benchmarks agree with each other, the
   two findings compose into a coherent story rather than competing.

If items 1 and 2 cannot be produced, the direction collapses into "proper statistical
reporting" and should be abandoned.

### I. Should we proceed to experimental design?

**Yes — but only to a specific, cheap, decision-gating step, not to the full platform.**

Recommended next step, in order:

1. **Verify the prerequisites before designing anything:** provider seed support, revision
   identifiers, tool-calling and structured-output behaviour, and per-episode cost for all
   four models. Three of these are label B/C after four passes; the study cannot be designed
   without them. **If revision pinning is unavailable for a model, drop that model now.**
2. **Read Li et al. (`arXiv:2605.16282`) in full** — it is the highest-overlap source and the
   only one that combines a taxonomy, a concordance statistic, CIs, and reporting standards
   in agent safety. The positioning of our work depends on exactly what its cross-benchmark
   analysis does and does not cover.
3. **Run the §8 pilot** to obtain ρ. **This is the gate:** if ρ and the design effect are
   near 1, stop — the negative result is the paper, and no further compute should be spent.
   If the design effect is substantial and the rank-stability curve shows instability past
   2–3 repetitions, proceed to the budget arm.
4. **Only then** design the budget × repetition experiment.

Do not proceed further until steps 1 and 2 are complete. The single largest risk is not
feasibility — it is that the contribution is positioned as a framework when the correct
positioning is as one measured number, a corrected table, and a scoped result.

---

## Appendix: sources verified or added in this pass

| ID | Status |
|---|---|
| **R60** | **New, A (government technical blog; NOT peer-reviewed).** NIST/CAISI, *Technical Blog: Strengthening AI Agent Hijacking Evaluations*, 2025-01-17, updated 2025-12-19. **The most on-point existing experiment.** |
| **R61** | **New, A (abstract).** Alvarado Gonzalez, Bruno Hernandez, Peñaloza Perez, Lopez Orozco, Cruz Soto, Malagon, *Do Repetitions Matter? Strengthening Reliability in LLM Evaluations*, `arXiv:2509.24086`, 2025-09-28. |
| **R21** | **Upgraded B → A (abstract).** Li, Fung, Li, Ismail, Iqbal, *Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents*, `arXiv:2605.16282`, 2026-04-11. Abstract verified; **full text still unread and is the highest-overlap source for the stability direction.** Kendall's W = 0.10, p = 0.94; 40 benchmarks; minimum reporting standards; artifacts released. |
| **R49** | **Upgraded C → A (search-level quotes of the paper).** Yao, Shinn, Razavi, Narasimhan, *τ-bench*, `arXiv:2406.12045`. Source of **`pass^k`**, the established run-to-run agent reliability metric. Full text still to be read. |
| **R62** | **New, B.** *The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism* — temperature-zero non-determinism and batch invariance. |
| **R63** | **New, B.** ReasonBENCH, *Benchmarking the (In)Stability of LLM Reasoning*, `arXiv:2512.07795v2` — run-noise variance decomposition. |
| **R64** | **New, B.** *Quantifying Variance in Evaluation Benchmarks* (OpenReview). |
| **R65** | **New, B.** SSP-Bench, `arXiv:2609.25352` — service-dependent safety ranking instability. |
| **R66** | **New, B.** *Persona Non Grata: Single-Method Safety Evaluation Is In…* (OpenReview) — persona rank inversion between evaluation methods. |
| **R67** | **New, B.** *Evaluation of Prompt Injection Defenses in Large…*, `arXiv:2604.23887` — 10 attack prompts per defense. |
| **R68** | **New, B.** SafeBoundary-LLM, MDPI *Computers* 15(7):460, 2026 — judge reliability limits and ranking instability. |
| **R69** | **New, B.** *Cost-Aware Evaluation of Offensive and Defensive Security…*, `arXiv:2607.15263` — cost-success lens for security agents. |
| **R48** | Notes unchanged but relevant: adversary compute deliberately unbounded, attack **efficiency declared future work** — the budget-axis pointer. |
| **R09** | Notes unchanged but relevant: pass^5 under-elicitation on tau-Bench Airline — repeated-run reliability is already a live problem in *benign* agent evaluation. |
| — | **Explicitly NOT usable:** an industry blog cited in search reporting "17.8% success at 1 attempt, rising to 78.6% at 200 attempts" — the underlying primary source was not identified. Do not cite. |
