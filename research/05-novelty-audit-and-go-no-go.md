# Final Novelty Audit and GO/NO-GO Decision
## Direction under audit: within-case dependence, effective sample size, and ranking stability in repeated LLM-agent security evaluation

**Date of audit:** 2026-09-25
**Status:** FINAL novelty audit before experimental design. No implementation performed.
**Verdict (summary):** **NO-GO on the direction as framed. GO WITH MAJOR MODIFICATION on a narrower, security-specific question** — provided three gates in §11 are passed first. Contributions 1–4 as written are **subsumed**; contribution 5 is the only one with a defensible residual, and it is narrowed further below.

### Evidence-labelling convention (carried forward, unchanged)

| Label | Meaning |
|---|---|
| **A** | Fetched and read at the primary source (full text or official vendor document) |
| **B** | Search-result level only; snippet or abstract, full text not read |
| **C** | Not verified; aggregator, blog, or unlocated record |

Claims marked **A** may be quoted. Claims marked **B/C** may not be cited as established. Everything proposed (rather than measured) is marked **PROPOSED** or **HYPOTHESIS** and is not a finding.

---

## 0. What changed in this pass

Four sources were located or fully read that were not available to the previous pass. Two of them materially change the conclusion.

| New source | Status | Effect on the direction |
|---|---|---|
| **Khan, AlKhanbashi & Mohamed (2026),** *Evaluating Indirect Prompt Injection Defenses in Tool-Using LLM Agents: Security, Utility, and Replication*, **Computers 15(9):570** | **A** — read via real browser (MDPI blocks scripted fetch) | **Decisive.** A peer-reviewed paper that already performs repeated agent-security evaluation on AgentDojo with confidence intervals, a correlation caveat stated verbatim, paired tests, cost measures, and an explicit correlation-aware method considered and declined. This is the closest competitor and it is substantially the proposed study. |
| **Hofer, Debenedetti & Tramèr (2026),** *Assessing Automated Prompt Injection Attacks in Agentic Environments*, arXiv:2606.10525 | **A** | **Major.** Already runs 4 seeds × 6 evaluation repetitions per injection on AgentDojo and reports Success@N. Repetition is no longer absent from agent security; it is instrumentally standard practice in the strongest recent attack paper. |
| **Miller (2024),** *Adding Error Bars to Evals*, arXiv:2411.00640 | **A** | **Decisive for novelty.** Publishes clustered standard errors, intra-cluster correlation, the variance decomposition, the repetition rule `K ≫ E[σ²]/Var(x)`, and cluster-adjusted Minimum Detectable Effect formulas — i.e. the method for contributions 1–4, in the adjacent literature, in 2024. |
| **Madaan et al. (2024),** *Quantifying Variance in Evaluation Benchmarks*, arXiv:2406.10229 | **A** | Neutral. Measures **pretraining-seed** variance and training monotonicity, not per-case Bernoulli replication. Does not subsume the question. |

Also newly verified (see §9): **DeepSeek-V4.1-Flash** and **GLM-5.3-Flash** are now confirmable at official vendor documentation — the four-pass model-verification blocker is resolved except for the seed question, which is itself a finding.

---

## 1. Full review of the closest paper (Li, Fung, Li, Ismail & Iqbal, arXiv:2605.16282)

Full text read at source (**A**). Title: *Taxonomy and Consistency Analysis of Safety Benchmarks for AI Agents*. Submitted 2026-04-11.

| Item | What the paper actually does |
|---|---|
| **Research question** | "How do agent-safety benchmarks measure safety, and do methodological differences between benchmarks predict contradictory safety conclusions?" |
| **Benchmark population** | 40 "core behavioral" agent-safety benchmarks (Apr 2023 – Mar 2026) plus 5 adjacent evaluator/defense/dataset artifacts = 45 entries. |
| **Number of benchmarks** | 40 core; 45 total entries. |
| **Metrics** | Six-axis methodological taxonomy (adversarial pressure source, environment fidelity, capability envelope, scoring method, evaluation granularity, safety–utility coupling); a 10-category risk-coverage matrix with primary/secondary/none coding (450 entry–risk cells); for the consistency check, reported benchmark scores per model. |
| **Statistical methods** | 95% **Wilson** confidence intervals; **Kendall's W** concordance. |
| **Confidence intervals** | Wilson, on reported benchmark scores. |
| **Kendall's W analysis** | W = 0.10, p = 0.94 across dimensions — "no evidence of ranking concordance across evaluation dimensions". |
| **Unit of analysis** | **Model × benchmark (or model × evaluation dimension)** — i.e. the unit is a *published reported score*. |
| **Treatment of repeated trials** | **None.** The paper does not re-execute anything. Verbatim: *"Our quantitative claims are descriptive over benchmark design choices and reported results, **not re-execution estimates of current model behavior**."* |
| **Within-case dependence** | **Not treated.** No clustering, no repeated measures. |
| **Intra-case correlation estimated?** | **No.** |
| **Design effect calculated?** | **No.** |
| **Effective sample size calculated?** | **No.** |
| **MDD corrected for clustering?** | **No** — no MDD is computed at all. |
| **Rank stability measured *within* a benchmark?** | **No.** The W statistic is concordance **between** benchmarks/dimensions at one time point. |
| **Repetition count experimentally varied?** | **No.** |
| **Attacker budget varied?** | **No.** |

### 1.1 Overlap verdict

**Our proposed study does not overlap with Li et al.** The two are orthogonal along the single axis that matters: **Li et al. compare *across* benchmarks using *reported* numbers; the candidate study compares *within* one benchmark using *re-executed* numbers.** Li et al. explicitly disclaim re-execution. Their W = 0.10 measures disagreement *between instruments*; our ρ would measure dependence *within an instrument across runs*. These are different quantities with different estimands.

**But two caveats must be stated before that defence is deployed:**

1. Li et al. use the phrase *"inconsistent safety behavior, where agents exhibit safe behavior in some contexts but unsafe behavior in semantically equivalent situations — making safety guarantees unreliable"* as a description of risk category R10. This is a *qualitative construct claim*, not a measurement, and they list "robustness" as their sixth structural finding (a "complete robustness blind spot"). A reviewer will ask why a dependence study is not simply an instance of R10's robustness gap. The answer — that ρ is an *estimable, design-relevant* quantity with a computable effect on inference, whereas R10 is a coverage category — must be made in the first paragraph.
2. Li et al. already supply "minimum reporting standards for future benchmarks" and release an artifact bundle. A new reporting recommendation is therefore **not** available as a contribution. This kills any residual "we propose a reporting protocol" framing.

---

## 2. Recheck of Pathade et al. (arXiv:2609.25173)

Full text read at source (**A**). Title: *Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation*. Pathade (Independent), Pawar, Patil.

### 2.1 Exact definition of MDD

The paper's Minimum Detectable Difference follows from treating **ASR-hat as a binomial proportion over m independent units**:

> *"the minimum difference detectable at 80% power and α = 0.05 is* `(z_{α/2} + z_β) √(2p(1−p)/m)`*"*

At m = 100 this yields **18.2 percentage points**. Two defenses truly separated by 5 points are ranked backwards **~21%** of the time; by 2 points, **~38%** (normal approximation; a 200,000-trial Monte Carlo check "slightly understates inversion", e.g. .214 vs .237 at m = 100, δ = 5 pp).

### 2.2 Assumptions behind the MDD

Stated verbatim and repeatedly:

> *"we assume throughout that the evaluation is otherwise perfect, **that units are independent**, and that the only defect is the one under study."*

### 2.3 Treatment of correlated tasks

Named as a limitation, not handled:

> *"The Section V results are analytical: they show what must follow from binomial sampling and oracle error, **under independence assumptions real benchmarks violate — correlated tasks and shared environments make effective sample size smaller than m, so our MDDs are optimistic.** We have not run defenses end to end, so we report no empirical ranking inversion; **that experiment is the natural next step and needs model access we did not have.**"*

### 2.4 The eight checklist questions

| Question | Answered by Pathade et al.? |
|---|---|
| Intra-case correlation estimated? | **No.** |
| Design effect measured? | **No.** |
| Effective sample size measured? | **No** — asserted to be smaller than *m*, never quantified. |
| Repetition count experimentally varied? | **No** — they *measure how often papers report* more than one run (20.5% corpus-wide; 26–32% in the hand-coded sample). Measuring reporting is not measuring variation. |
| Ranking stability experimentally measured? | **No** — the 21%/38% inversion figures are analytic/Monte-Carlo, not empirical. |
| How many repetitions are needed? | **No.** |
| Do defense rankings change under repeated evaluation? | **No** (empirically). |
| Are CIs sufficient to resolve ranking instability? | **No.** |

### 2.5 The A3 axis is the hinge

Verbatim:

> *"Agent policies are typically sampled at temperature >0, so a trajectory is a draw, not a measurement. Under Eq. (1) with m = |U| units evaluated once each, ASR-hat is a binomial proportion... and **repeated evaluation would additionally expose run-to-run variance that a single pass cannot separate from unit-to-unit variance.**"*

Pathade et al. explicitly separate **A3 (trials / non-determinism)** from **A4 (attacker adaptivity and budget)**, and note that A3 "does not bias the ordering systematically; it randomizes it", whereas A1/A2/A4/A5 are system-dependent and can *reverse* rankings. This separation is the single most useful artefact for the modified direction in §13.

### 2.6 Pathade's own sensitivity numbers

- A3 reporting: 23.9% report a variance/CI (strict); 20.5% report repeated runs; **65.3% report neither** (58.0%, 95% Wilson CI 44.2–70.6, in the 50-paper hand-coded sample).
- A4: **10.8% state an attack budget**; 30.5% consider an adaptive attacker; 16.2% state attacker knowledge of the defense.
- A6: 2.3% address partial success. Utility: 37.8%.
- Judge calibration: 24.7% use an LLM judge (lower bound); 29.7% of those validate against humans.
- Corpus: 1,168 arXiv records → 259 included (Feb 2025 – Sep 2026); true population 259–347.
- Two detectors were abandoned (oracle family, string matching) — *"Across 259 papers we could not mechanically locate a statement of how attack success is decided."*

### 2.7 Verdict on Pathade

**The diagnosis is theirs. The experiment is not.** They name the exact quantity that converts a nominal MDD into a real one, name the direction of the correction (optimistic), and state that running it "needs model access we did not have". They publish **no artifact repository** ("We have not published an artifact repository"), so their analytical results are reproducible from closed forms only.

---

## 3. Recheck of NIST / CAISI, *Strengthening AI Agent Hijacking Evaluations*

Source (**A**, non-peer-reviewed government technical blog, posted 2025-01-17, updated 2025-12-19; artifact at `github.com/usnistgov/agentdojo-inspect`).

| Question | Findings |
|---|---|
| **Exact experiment** | AgentDojo, Anthropic's upgraded Claude 3.5 Sonnet, five injection tasks, four insights. |
| **Number of repetitions** | *"CAISI took the five injection tasks in the previous section and **attempted each attack 25 times**. After repeated attempts, the average attack success rate increased from 57% to 80%, and the attack success rate for individual tasks changed significantly."* |
| **Are repetitions independent attack attempts?** | **No — and this is the central terminological problem.** The reported effect is **best-of-25**: the attacker keeps trying and the run is scored as a success if any attempt lands. That is a *budget* effect, not a variance measurement. Insight #4's own wording, *"Testing the success of attacks on multiple attempts may yield more realistic evaluation results"*, is consistent with either reading. |
| **Attack budget varied?** | Implicitly (1 vs 25 attempts) but **no curve is reported**, and budget is not separated from repetition. |
| **Statistical uncertainty reported?** | **No.** |
| **Variance measured?** | **No** — no dispersion statistic on the per-task rates is reported, though the authors note per-task rates "changed significantly". |
| **Confidence intervals reported?** | **No.** |
| **Ranking stability measured?** | **No** — one model, no defenses compared. |

**Do not reinterpret best-of-N attack success as variance.** The 57%→80% change cannot be used as evidence about run-to-run dependence, and it is *not* interchangeable with a repetition effect. As of this audit, NIST/CAISI is the **only** source that reports a repeated-attempt protocol with a numerical change, and it conflates the two axes.

### 3.1 Consequence

The NIST result was previously treated as the most on-point existing work. This pass revises that: it is the most on-point *demonstration that repetition matters*, but it is a demonstration of a **budget** effect. This is precisely the conflation identified in the modified research question (§13).

---

## 4. Fresh search for additional close work

Ten fresh primary-source searches were run (§4 queries plus adjacent-field variants). Four sources are new and load-bearing; they are catalogued as **R70–R73** in `sources.csv`.

### 4.1 R70 — Khan, AlKhanbashi & Mohamed (2026). **The decisive competitor. (A)**

*Evaluating Indirect Prompt Injection Defenses in Tool-Using LLM Agents: Security, Utility, and Replication.* **Computers 2026, 15(9), 570.** DOI 10.3390/computers15090570. Received 21 Jul 2026, revised 21 Aug 2026, accepted 28 Aug 2026, published **31 Aug 2026**. Adil Khan (Liwa University, UAE), Khaled AlKhanbashi, Azza Mohamed (Abu Dhabi University).

**Setup.** Four defenses + undefended control across GPT-5.4, GPT-5.4-mini, and Claude Sonnet 4.6 on the **AgentDojo banking** benchmark. Tool Filter evaluated only for the OpenAI models (relied on the OpenAI function-calling interface). **14 evaluated model–defense configurations.** Each configuration ran **two independent benchmark runs**; each run = **144 attack instances + 16 benign-task evaluations**; pooled = 288 attack instances per configuration.

**Metrics.** ASR, benign utility (BU), utility under attack (UUA), goal-completable canaries, action/tool availability, response latency, tool-call counts, run-to-run variation, 95% Wilson CIs, paired comparisons.

**Statistics.** Wilson intervals per run and pooled; **paired exact McNemar tests** on 144 matched attack-level records for GPT-5.4-mini run 2; **Holm correction** across the comparison family; α = 0.05.

**Verbatim statements that matter most:**

> *"For the pooled two-run counts, these intervals are descriptive summaries of the observed proportions and **not the correlation-aware inferential intervals. As the same benchmark instances were repeated in the runs, a pooled Wilson interval can be narrower than the interval explicitly accounting for the correlation.**"*

> *"The workflow diagram lists **task-cluster bootstrap as an approach considered during method planning; it was not adopted** in the reported statistical methods, which are described in Section 4.7 and rely on Wilson intervals and paired McNemar tests."*

> *"robust across-run summary statistics (e.g., medians or **cluster bootstrap intervals) are not estimated because each cell has only two replications**."*

> *"**The second issue is replication and variability of low-frequency outcomes.** Attack success events happen infrequently in many agentic benchmarks; hence, a single execution can make a difference for a security outcome... **Replication is needed to differentiate a single occurrence from a systematic outcome and to estimate the level of variance involved in infrequent attack events.**"*

**Headline results.** Raw undefended ASR: **0/288** (GPT-5.4), **11/288** (GPT-5.4-mini), **1/288** (Claude Sonnet 4.6). *"None of the four paired GPT-5.4-mini comparisons reached significance after Holm correction; only Tool Filter had an unadjusted p-value below 0.05."* And:

> *"Because both models' undefended baselines were 0/144 in run 2, the exact McNemar test has **no practical power to detect a defense effect of any size** in this comparison, so the absence of a paired result reflects the benchmark's low event rate rather than defense performance."*

> *"benign utility was generally **more stable** than individual low-frequency attack outcomes."*

**Limitations, verbatim:** *"Sparsity of attacks and few independent replicates limit the statistical power as well. More independent replicates and more attack scenarios in the future work will provide better estimations of defense effectiveness."* Future work to *"use enough runs to increase statistical power"*.

**What Khan et al. did NOT do:** no intra-case correlation estimated (the strings "intraclass" and "design effect" appear **nowhere** in the article); no design effect; no effective sample size; no corrected MDD; no attacker-budget axis; **no seed or temperature reported or varied** (the word "seed" appears nowhere) — so their "two independent replications" are two replicas of a benchmark whose sampling configuration is unspecified, and their run-to-run variation cannot be attributed to any named stochastic source.

**Why this is decisive.** Khan et al. deliver, in peer-reviewed form and on the exact benchmark, with the exact model-tier class: repetition, variance discussion, confidence intervals, the correlation caveat, paired testing with multiplicity correction, cost/latency measurement, security **and** utility **and** action availability, and the negative finding that low event rates defeat power. **Contributions 1–4 of the candidate, as framed, are a refinement of a paper that already exists.** The only surviving differentiator is that they *name* the correlation-aware interval as the correct thing and *decline* to compute it — so the quantity remains unmeasured, but the paper that would have "discovered" it has already been written and already told readers the interval is wrong.

### 4.2 R71 — Hofer, Debenedetti & Tramèr (2026). (A)

*Assessing Automated Prompt Injection Attacks in Agentic Environments.* arXiv:2606.10525. ETH Zurich.

**Evaluation protocol, verbatim:** *"(1) Optimization: We performed **n = 4 independent optimization runs** for each task (or universal set) using different random seeds. (2) Evaluation: **Each generated injection was evaluated m = 6 times** against the target agent to account for non-determinism in tool execution."*

**Metric:** *"**Success@N (S@N): The fraction of test cases where at least one attack succeeds within N separate optimization and evaluation attempts**... This captures the effectiveness of stochastic methods like GCG and TAP, which may require multiple restarts, **as well as addressing the non-deterministic nature of the target LLM.**"* They also use *"reliability retries [that] average evaluator scores across multiple trials to provide a stable signal despite non-deterministic target responses."*

**Setup:** AgentDojo, 80 task pairs across 4 domains, Qwen3-4B, Gemma3-4B, GPT-5; transfer to 7 further models. TAP 45.2% vs GCG 24.1% ASR on Qwen3-4B.

**Effect on the direction.** Repeated stochastic evaluation of agent security with a matched-case design is **already implemented and published by the strongest group in the subfield** (Debenedetti and Tramèr are AgentDojo and CaMeL authors). This refutes any framing that begins "the field evaluates once". Furthermore, S@N **again conflates attacker restarts with target nondeterminism** — the same conflation as NIST — which reinforces §4.1's differentiator but also means the conflation is now the field's *default* practice rather than an isolated error. They report **no** variance, CI, ICC, design effect, ESS, or corrected MDD.

### 4.3 R72 — Miller (2024). **The novelty killer for contributions 1–4. (A)**

*Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations.* arXiv:2411.00640, **Anthropic**, 1 Nov 2024.

Miller already publishes, for LLM evaluations:

- **Clustered standard errors** for questions drawn in groups (Eq. 4): `SE_clustered = (SE_CLT² + (1/n²)Σ_c Σ_i Σ_{j≠i}(s_ic − s̄)(s_jc − s̄))^{1/2}`, explicitly *"a kind of 'sliding scale' between cases where scores within a cluster are perfectly correlated... and perfectly uncorrelated"*.
- **Intra-cluster correlation**: *"The intra-cluster correlations (or lack thereof) are captured by the triple summation."*
- An **additive variance decomposition** (law of total variance): `Var(μ̂) = (Var(x) + E[σ_i²])/n` — between-case variance of conditional means versus mean conditional (within-case) variance.
- The **repetition rule**, which is the design-effect logic in another notation: resampling K times gives `Var(s_i) = σ_i²/K`, and *"Once E[σ_i²]/K ≪ Var(x), increasing K further will have little effect"*; also the explicit `K ≫ 2` derivation.
- A **cluster-adjusted MDE/sample-size formula** (Eq. 9–10 and Appendix C), with clustered `ω²`, `σ_A²`, `σ_B²` and an estimator using `K ≫ 1` replicates.
- **Paired and paired-clustered** comparison standard errors (Eq. 7–8), exploiting `Cov(x_A, x_B)` between models on the same questions.
- A worked demonstration that clustered SEs exceed naive SEs by **up to 3.05×** on real evals (DROP), and that `K: 1 → 10` moves the MDE from **13.2% to 7.5%**.
- An explicit warning against controlling variance by lowering temperature (*"Don't touch the thermostat!"*): it may shift variance from the reducible conditional term into the irreducible super-population term, or inject bias.

**Consequence: contributions 1, 2, 3 and the statistical half of 4 are a *transplant of a published 2024 framework into a new domain*, not a new method.** A reviewer will locate Miller in one search, because Pathade et al. cite it as reference [26].

### 4.4 R73 — Madaan et al. (2024). Neutral. (A)

*Quantifying Variance in Evaluation Benchmarks.* arXiv:2406.10229 (Meta/NVIDIA/others; also cited by Miller as [15], and previously mis-catalogued in `sources.csv` as R64 with "identifier not captured" — now resolved).

Measures **pretraining-seed** variance across initialisations, monotonicity during training, and continuous-vs-discrete scoring; concludes item analysis / IRT "struggle to meaningfully reduce variance". **This is a different variance axis** (training-run seed, not per-case Bernoulli replication) and it does **not** subsume the candidate direction. It does, however, occupy the phrase "quantifying variance in evaluation benchmarks" — title collision risk only.

### 4.5 Also surfaced, not pursued

| Source | Status | Note |
|---|---|---|
| Alvarado Gonzalez et al., *Do Repetitions Matter?* arXiv:2509.24086 | **A** (abstract + page) | 8 models, AI4Math, **3 runs**; 10/12 slices (83%) invert ≥1 pairwise rank vs the three-run majority; *"moderate overall interclass correlation"*; two runs remove ~83% of single-run inversions; recommends **≥ 2 repetitions**. **Already reports an ICC for LLM evaluation** and already delivers the repetitions-vs-ranking result — for a capability benchmark with no adversary. This is the single most damaging source for contribution 4's novelty, and the source that makes the *transfer* question (§5.4) the only live one. |
| R67, arXiv:2604.23887 | **B** | *"the attacker generates 10 attack prompts... Each attack is then sent to the defender"* — a further prompt-injection defense evaluation that already repeats per case. Full text not read. |
| R68, MDPI Computers 15(7):460 | **C** | Safety-boundary stability; judge positional bias and ranking instability. Not read. |
| R65, SSP-Bench arXiv:2609.25352 (**B**) | **B** | *"ranking instability is service-dependent and predictable, exposing family-specific failures such as inverse safety scaling in Gemma-3"*. Relevant to the *service-side* (provider) variance component. Not read. |
| R66, *Persona Non Grata* (OpenReview, **B**) | **B** | "Persona Rank Inversion Between Methods" — safety rank inversion across evaluation methods. Not read. |
| *Attack Selection in Agentic AI Control Evals Can Decrease Safety* (LessWrong, **C**) | **C** | Audit-budget selection; AI-control framing. Not a primary source. Do not cite. |

### 4.6 Adjacent-field methodology

General searches for `intraclass correlation`, `design effect`, `effective sample size`, `clustered binary outcomes` returned **only** standard biostatistics/clinical-trial methodology (cluster randomised trials, ICC reporting surveys, design-effect calculators) and no agent-security application. **The method is mature and unremarkable in its home field.** The candidate direction cannot claim it, and the phrase "we apply ICC/design effects" signals a methods-transfer paper rather than a contribution.

---

## 5. Method versus contribution

**Question:** is "estimate ICC / design effect / effective sample size" merely a standard statistical method?

**Answer: yes, unambiguously.** The three components decompose as follows.

| Component | Status | Where it already exists |
|---|---|---|
| Clustered SE for grouped eval items | **Established** | Miller 2024 §2.2 Eq. 4; Abadie et al. 2022 (cited by Miller) |
| Intra-cluster / intra-case correlation | **Established** | Miller 2024 §2.2; and reported for LLM evals by Alvarado Gonzalez et al. 2025 |
| Variance decomposition (between-case vs within-case) | **Established** | Miller 2024 §3, law of total variance |
| Repetition sufficiency rule | **Established** | Miller 2024 §3.1 (`K ≫ E[σ²]/Var(x)`) |
| Design effect / effective sample size | **Trivial arithmetic** | DE = 1 + (K−1)ρ; ESS = mK/DE |
| Cluster-adjusted MDD / power | **Established** | Miller 2024 Eq. 9–10, Appendix C |
| Cluster bootstrap | **Established, and explicitly considered by the competitor** | Khan et al. 2026 §4.7 |
| Ranking instability under repeated runs | **Established for capability evals** | Alvarado Gonzalez et al. 2025; Pathade et al. 2026 Fig. 2b (analytic) |

Therefore the contribution **cannot** be "we calculated ICC". A defensible contribution would have to be a transferable empirical claim of the form: *"repeated security outcomes exhibit materially different dependence structure from conventional LLM evaluations, and this changes the number of independent cases required to support reliable security comparisons."*

### 5.1 Is that claim defensible?

**Partly, and only if it is actually tested against a comparison.** The claim is falsifiable and mechanistic, and it has a specific, checkable form: the quantity that governs everything is the ratio `E[σ²]/Var(x)` (Miller's notation) — equivalently ρ. In capability evals, Alvarado Gonzalez et al. report this ratio as producing *"~5% SE shrinkage from one to three [runs]"* with ICC described as *"moderate"*. If agent-security outcomes are dominated by case-level all-or-nothing behaviour (which Khan et al.'s 0/144 and 1/288 baselines suggest), then `Var(x)` is large and `E[σ²]` small **within successful cases**, but the mass of saturated cases (p̂ ∈ {0,1}) is itself large — which means **Wilson/binomial intervals are simultaneously too wide in the middle and structurally uninformative at the boundary**, and repetition buys almost nothing for the aggregated ASR while still being necessary for detecting *whether a given case is saturable at all*.

There is a genuine, non-obvious, testable hypothesis here, and it is **not** "ICC is large". It is:

> **HYPOTHESIS H1 (the two-population structure).** Agent-security outcomes are not drawn from a unimodal case-difficulty distribution but from a mixture: a large mass of cases that are *deterministically* unsusceptible (p = 0) or deterministically compromised (p = 1) under a given model–defense configuration, and a minority of genuinely stochastic cases. Consequence: (a) the **mean** ASR is estimable from a single run with negligible repetition benefit, while (b) the **existence of any compromise at all** in a case, and hence the *ranking of defenses*, is a different and much less stable estimand. Repetitions do not improve precision much but change the *comparison* qualitatively.

If H1 holds, the practical implication has teeth: **the field is optimising the wrong estimand.** Point-estimate ASR is cheap and stable; the defence-relevant quantity (per-case saturation, i.e. whether a defence converts a saturable case into a non-saturable one) is expensive and unstable, and no current paper measures it. That is a genuinely different claim from Khan et al.'s "we were underpowered" and from Pathade's "MDDs are optimistic". It also reframes Alvarado Gonzalez et al.'s asymmetry ("modest SE shrinkage but large ranking gains") as the *capability* case and predicts the *opposite* asymmetry for security — a directional, falsifiable transfer prediction.

### 5.2 What is *not* defensible

- "We provide the first statistical framework for repeated agent-security evaluation." **False** (Miller 2024).
- "The field never repeats evaluations." **False** (NIST 25 attempts; Hofer 4×6; Khan two replications; R67 10 prompts per case).
- "We propose a reporting checklist." **False** (Pathade 10 items; Li et al. minimum reporting standards).
- "We show repeated evaluation changes rankings." **Weak** — Alvarado Gonzalez et al. 2025 shows it for math; Khan et al. shows two-run variation on AgentDojo; the claim needs the *security-specific* mechanism (H1) to be novel.

---

## 6. The unit of analysis

### 6.1 Proposed hierarchy — revised

The hierarchy suggested in the brief (`Model → Agent → Defense → Attack Case → Repeated Run`) **mixes crossed and nested factors**. Model, defense and case are **crossed** (fully factorial over the evaluated configurations), not nested. The correct structure for the candidate design is:

```
Configuration cell (crossed: model × defense)
└── Case  (attack instance = task × injection target; crossed with configuration)
    └── Episode  (one independent stochastic execution of that case under that configuration)
```

with a **separate, crossed attacker axis**:

```
Attacker procedure (static template | adaptive with budget B)
└── Attempt (1..B)  → produces an injection artifact
    └── Episode  (execution of the case under that artifact)
```

### 6.2 Why the distinction is load-bearing

Three different "N"s are routinely confused:

| Unit | Symbol | What it indexes | Variance it carries |
|---|---|---|---|
| **Case** (task × injection pair) | *m* | unit-to-unit heterogeneity | `Var(x)` — between-case, irreducible, a property of the super-population |
| **Episode** (repeated run) | *K* | within-case stochasticity | `E[σ²]/K` — reducible |
| **Attempt** (attacker query) | *B* | attacker search | not a variance term at all: **B shifts the estimand upward** (best-of-B), it does not reduce noise |

**The critical error in the literature audited here is treating B as a *K*.** NIST/CAISI (25 attempts → 57%→80%) and Hofer et al. (S@N over N optimization and evaluation attempts) both express a *budget* quantity in the language of repetition. Pathade et al. correctly separate these (A3 vs A4) but do not connect them statistically.

**Correct minimal hierarchy for the pilot:** episodes are nested within case; case is nested within nothing (it is the cluster); configuration is crossed with case and is a fixed factor; attacker budget is a **separate crossed manipulation**, not a repetition.

### 6.3 Consequence for K and B

Because case is the cluster and episodes are the replicates, the unit of analysis for inference on ASR is **the case**, with episode-level outcomes averaged (or modelled with a random case intercept). The valid analytic N is *m*, not *mK*. This is exactly the quantity Pathade declares unmeasured.

---

## 7. Statistical methods for binary clustered outcomes

**Requirements, derived from the actual structure:** binary outcome; *m* ≈ 144 clusters (cases); *K* ≈ 10 replicates per cluster; interest centres on **one variance ratio (ρ)**, an **ASR proportion** with a cluster-aware interval, a **paired** defense comparison on matched cases, and a **rank-stability curve** as a function of K.

| Method | Verdict | Reason |
|---|---|---|
| **Binomial / Wilson interval on pooled episodes** | **Reject** | Exactly the error Khan et al. flag in their own paper: pooling correlated episodes narrows the interval. |
| **Wilson interval computed on case-level means** | **Adopt (descriptive)** | Case-level means are (approximately) independent; Wilson on them is honest and trivially computable. Also gives the per-case saturation picture needed for H1. |
| **Beta-binomial (moment or ML) for ρ** | **Adopt as primary** | The canonical model for *m* independent clusters of *K* binary trials with a shared within-cluster correlation; estimable in a few lines; directly yields ρ and therefore DE and ESS; robust to the extreme saturation expected here (unlike a random-effects logistic model, whose normal random intercept is a poor fit to a mixture with mass at 0 and 1). |
| **Random-effects logistic (GLMM) with case random intercept** | **Adopt as sensitivity** | Familiar and citable; ICC = σ²_case/(σ²_case + π²/3). Report alongside beta-binomial to show robustness; do not make it primary, because the normal-intercept assumption is weakest exactly where H1 predicts mass. |
| **GEE with exchangeable working correlation** | **Optional** | Gives a marginal (population-averaged) ASR and a robust sandwich SE, which is the right estimand for "ASR of this configuration". Useful third line. |
| **Cluster bootstrap (resample cases with replacement)** | **Adopt for intervals and ranking** | Non-parametric, makes no distributional assumption, and handles the paired defense difference naturally (resample cases, recompute the paired statistic). Miller's own guidance: *"sampling at the cluster level (i.e. drawing clusters in their entirety)"*. |
| **Hierarchical Bayesian** | **Reject** | Adds prior specification and compute for a problem whose estimand is one variance ratio estimable in closed form. Justify only if the rank-stability analysis needs full posterior propagation — and even then, the bootstrap is simpler. |
| **McNemar's exact test** | **Adopt for paired defense comparisons** | Matched binary outcomes on the same cases — the correct test, and the one Khan et al. used, which makes results directly comparable. Its **power collapses when the undefended baseline is 0** — a fact Khan et al. demonstrate and which must be pre-registered as a design risk here. |
| **Mixed-effects model with rank-instability analysis** | **Adopt the *analysis*, not the model** | Alvarado Gonzalez et al.'s rank-instability procedure (compare each K-run subsample's ranking to the K-max majority) is directly reusable; it does not require their mixed-effects fit. |
| **Permutation test** | **Optional robustness** | Cheap, distribution-free; report for the paired difference if the McNemar exact test is degenerate. |
| **Sequential analysis** | **Reject for inference; use for budget** | Sequential stopping would invalidate the dependence estimate. Its only legitimate use here is as a *cost* instrument (deciding how many runs to buy), which is a separate exploratory question. |
| **Power analysis** | **Adopt, cluster-adjusted** | Miller Eq. 9–10 / Appendix C. The whole point of estimating ρ is to feed it into this. |

### 7.1 Recommended primary analysis chain (fixed)

1. Fit **beta-binomial** per configuration cell → `ρ̂`, with cluster bootstrap CI.
2. Compute **DE = 1 + (K−1)ρ̂** and **ESS = mK / DE**.
3. Compute **cluster-adjusted MDD** (Miller Eq. 10 with clustered variance terms) and publish it next to Pathade's nominal 18.2 pp at m = 100 and next to this pilot's own nominal MDD.
4. Compute **ASR with a cluster bootstrap interval** (not Wilson on pooled episodes), plus Wilson on case-level means as a cross-check.
5. **Paired exact McNemar** per defense vs control, **Holm-corrected** across the defense family.
6. **Rank-stability curve**: for K' = 1…K, draw subsamples, rank defenses, compare to the K-max consensus; report P(correct order) vs K'.
7. **Utility, cost and budget co-reported** (BU, UUA, latency, tokens, and B) — required to distinguish a real defence from a refusing one (Pathade checklist item 10) and to address the operational-cost column that remains empty in `benchmark-comparison.csv`.

**Explicitly not included:** Bayesian estimation, permutation-first design, sequential stopping, IRT/item analysis (Madaan et al. found IRT "struggle[s] to meaningfully reduce variance"), next-token-probability scoring (unavailable through these APIs for agent trajectories).

---

## 8. Minimal scientific contribution

If the direction survives the §11 gates, the smallest defensible contribution is **one sentence**:

> **We show that repeated stochastic security outcomes for LLM agents are drawn from a two-population mixture of near-deterministic and genuinely stochastic cases, so that the mean attack-success rate is cheap and stable while the defence-relevant per-case quantity is expensive and unstable — which means the field's standing repetition recommendation (≥ 2 runs) is adequate for point estimates and inadequate for defence comparisons, and that a single design effect converts the literature's nominal minimum detectable differences into honest ones.**

That is one claim with three measurable consequences: a ρ (and hence a design effect), a rank-stability curve as a function of K, and a corrected MDD. No framework. No new metric. The nearest competitor is Khan et al. (2026), and the differentiator is not "we repeat evaluations" but **"we measure the dependence structure that three independent papers identify, decline to compute, and then correct the resulting inference"** — a quantity that, on the current evidence, is unmeasured anywhere.

**Caveat carried forward:** the *value* of ρ for agent security is unknown, so the sentence above is a **PROPOSED** claim about a to-be-measured quantity, not a finding. It may be false, and §11 states what would refute it.

---

## 9. Feasibility of the four available models

Four passes treated this as unverified. It is now largely resolved. **All vendor pages were fetched and read directly.**

### 9.1 DeepSeek V4.1 Flash — **VERIFIED (A)**

Official: `https://api-docs.deepseek.com/quick_start/pricing/` (fetched, read).

| Property | Verified value |
|---|---|
| API model name | **`deepseek-flash`** — *"Use deepseek-flash as the model name. The legacy names deepseek-v4-flash and deepseek-v4-flash-vision-exp are still accepted, but the corresponding models have been **retired**"* |
| Model version | **DeepSeek-V4.1-Flash** |
| Context / max output | **1M** / **384K** |
| Thinking mode | *"Supports both non-thinking and thinking (**default**) modes"* |
| Tool calls / JSON / Vision | ✓ / ✓ / ✓ |
| Concurrency limit | 2500 |
| Cost | Off-peak vs **peak**; peak = **2×** off-peak. Peak hours 01:00–04:00 and 06:00–10:00 UTC Mon–Fri (excl. Chinese public holidays). Flash: $0.15 (cache-miss off-peak) / $0.30 (peak) per 1M input; $0.60 / $1.20 per 1M output. |
| **Temperature** | **Not controllable in default mode.** Official *Thinking Mode* page: *"Thinking mode does not support the **temperature**, presence_penalty, or frequency_penalty parameters."* Since thinking is the default, temperature is inert unless the caller explicitly switches to non-thinking. |
| **Seed** | **Not documented** on the pricing or thinking-mode pages. |

Also present: official announcement page `deepseek.com/en/news/deepseek-v4-1-flash/` and Hugging Face `deepseek-ai/DeepSeek-V4.1-Flash` (**existence A; the "552B MoE backbone" parameter figure is snippet-level → B**).

**Two findings that matter for the design:**
1. **Temperature control is unavailable in the default configuration** of the primary available model. This is not a nuisance; it is direct evidence that some of the brief's proposed variance controls (`temperature`) are *not implementable*, which strengthens the case for measuring variance instead of attempting to control it.
2. **Peak/off-peak pricing introduces a 2× cost discontinuity** with a time-of-day dependency. Cost measured during a pilot is therefore not reproducible unless the wall-clock window is recorded — an operational-cost reproducibility hazard that is trivially solved (record UTC timestamp per episode) and worth reporting because it will bite anyone replicating a cost claim.

### 9.2 GLM-5.3-Flash — **VERIFIED (A)**

Official: `https://docs.z.ai/guides/vlm/glm-5.3-flash` (fetched, read); official launch blog `z.ai/blog/glm-5.3-flash` (26 Aug 2026).

| Property | Verified value |
|---|---|
| Model code | **`glm-5.3-flash`** / `glm-5.3-flashx` |
| Architecture | **320B total parameters, 18B activated**; sparse + linear attention |
| Context / max output | **1M** / **128K** |
| Input modality | Video / Image / Text / File |
| Function calling, structured output, streaming | ✓ ✓ ✓ |
| **Thinking mode** | *"thinking.type **only supports enabled**; thinking **cannot be disabled**."* |
| Recommended settings | *"temperature: 1, top_p: 0.95, and reasoning_effort: max"*; `thinking.clear_thinking: false` |
| Cost | Points-based plan; off-peak/weekend consumes 50% of standard points (cost nondeterminism again) |
| **Temperature** | **Settable** (recommended 1; text parameters "consistent with GLM-5.3") |
| **Seed** | **Not documented** on the model overview page. |

### 9.3 MiMo 2.6 Flash — **PARTIAL (product A; API surface B/C)**

- **Vendor domain confirms the product family exists (A):** `mimo.mi.com` lists *"MiMo-V2.6-Pro · MiMo-V2.6-Flash · MiMo-V2.6-Pro-UltraSpeed"*; official pricing doc at `mimo.mi.com/docs/price/pay-as-you-go` describes *"MiMo-V2.6-Flash: Full-modality, high-intelligence, low-cost reasoning model"*.
- **Hugging Face card (A for existence):** `XiaomiMiMo/MiMo-V2.6-Flash-RL` — note this is an **RL variant**, which need not be the served checkpoint.
- **Not verified at vendor source:** the serving model-ID string (`mimo-v2.6-flash` appears only on aggregators: apimaster.ai, benchlm.ai, openclawlaunch.com → **B/C**), parameter counts (309B MoE / 15B active appear only on `mindstudio.ai` and `benchlm.ai` → **C** — note these contradict the notion used in earlier passes), tool-calling and structured-output support, temperature and seed parameters.

### 9.4 Solar Mini 4 — **RECOMMEND EXCLUSION**

- **Vendor blog confirms existence (A):** `upstage.ai/blog/en/solar-pro-4` carries the banner *"New: Solar Mini 4 is live on Console. 50% off through Oct 22 (UTC)"*.
- **All specifications are aggregator-only (B/C):** 35B MoE / 3B active / 524K context come from OpenRouter, ppq.ai, orcarouter.ai — **not** Upstage documentation. No Upstage model card was located.
- **Decisive disqualifier:** released **~22 September 2026**, i.e. **approximately three days before this audit**. One aggregator states plainly: *"Solar Mini 4 is one day old and has no independent evaluation."* A model three days old has no pinned revision history and can be silently re-pointed mid-experiment. For a study whose entire contribution is the reproducibility of security conclusions, using it as a primary subject would be a self-inflicted wound.

### 9.5 Verdict on model sufficiency

**Two models are verified and sufficient; a third is optional; the fourth should be dropped.**

Critically, **the objection from the previous pass — "no capability ladder" — does not apply here, and the brief is right to ask for it to be reconsidered.** The estimand is a **variance ratio**, not a capability difference. Four models of similar tier are, if anything, *better* than a capability ladder, because heterogeneity in capability would confound ρ (a more capable model may produce both lower mean ASR and different within-case dependence, and with m = 144 there is no power to separate those). The design needs **mid-range mean ASR** (so cases are neither saturated at 0 nor at 1 — see §11's saturation gate), not capability spread.

What the models must supply, and do:
- **Documented, pinnable identifiers** — `deepseek-flash` (version DeepSeek-V4.1-Flash) and `glm-5.3-flash` are both official. ✓
- **Tool calling** for agentic evaluation — both ✓.
- **Some capability to reach AgentDojo injection goals at all** — unverified for both, and this is a **real pre-pilot risk**: Khan et al. found GPT-5.4-family undefended baselines at 0/288 and 1/288. If DeepSeek-Flash and GLM-5.3-Flash are *too* robust, the pilot is uninformative. **This is the single largest unresolved feasibility risk and it is cheap to test — a 20-case smoke run at K = 5 decides it for a few dollars.**
- **A documented seed** — **neither** model documents one. ✓ = not satisfied.

**The seed situation is a finding, not a blocker.** If seeds are unavailable (or, as on DeepSeek, temperature is inert in the default mode), the study cannot separate "seed-driven" from "provider-side" stochasticity — which means the honest design is *N independent runs at fixed documented configuration*, with the irreducible provider variance **reported as part of the result** rather than controlled away. This should be verified empirically by a cheap determinism probe before the main run: send an identical request N = 20 times, record exact-match rate and any `system_fingerprint`-like field. **Requirement: 30 episodes × 1 model ≈ under $1.**

*One unverified claim to correct:* earlier passes recorded a "1M-token context" for DeepSeek from tech-media. It is **now confirmed at the vendor** (1M, and 384K max output). The MiMo and Solar context figures remain aggregator-only.

---

## 10. Minimal pilot design

**Scope discipline:** this is the smallest experiment that can produce or refute the §8 sentence. It is **not** the AgentSec platform. No attacker training, no new benchmark, no new defence.

### 10.1 Fixed design

| Element | Choice | Rationale |
|---|---|---|
| **Benchmark** | **AgentDojo `banking` suite** (144 attack instances; 16 benign tasks/run) | Deterministic environment-state oracles (no judge-variance confound); matches Khan et al. exactly, so results are directly comparable to a peer-reviewed two-run baseline; small enough to run fully. |
| **Models** | **2 primary:** `deepseek-flash` (DeepSeek-V4.1-Flash), `glm-5.3-flash` (GLM-5.3-Flash). Optional 3rd: MiMo pending vendor docs. **Excluded:** Solar Mini 4. | Verified identifiers; two vendors gives one provider-level replication of ρ without a capability confound. |
| **Agents** | One ReAct-style tool-calling agent, fixed system prompt, pinned in the release | Agent scaffolding must be constant, since it is a variance source. |
| **Attack cases** | **All 144 banking attack instances** (task × injection target), frozen | m = 144 is the cluster count; it is also the count used by the competitor. |
| **Defenses** | **3 + control:** (1) undefended control, (2) Spotlighting, (3) Prompt-Injection Detector, (4) Tool Filter | Same defense families as Khan et al. so any disagreement is interpretable. Note Tool Filter changes the *action space* — must be reported as such (Khan et al.'s point). |
| **Runs per case** | **K = 10** independent episodes | Needs K ≥ 5 for a stable beta-binomial ρ; 10 gives a usable rank-stability curve K' = 1…10 at no extra modelling cost. |
| **Attacker budget** | **B ∈ {1, 5, 10, 25}** on a **reduced grid**: 30 cases × 1 model × 1 defense × B values × 8 runs | This is the arm that carries the novelty. Must be *adaptive* (attempt B+1 informed by feedback on attempts 1..B) to be a genuine budget rather than more repetitions. |
| **Seeds** | **Not controllable** (undocumented on both vendors). Record requested seed if accepted; run N independent episodes otherwise; record UTC timestamp and any provider fingerprint per episode. | Turns an unavailable control into a reported measurement. |
| **Temperature** | `temperature = 1`, `top_p = 0.95` for GLM (vendor-recommended); **record that temperature is inert in DeepSeek's default thinking mode** | Honest documentation of what could not be controlled. |
| **Total executions** | Main arm: 2 models × 4 configs × 144 cases × 10 runs = **11,520 episodes**. Budget arm: 30 × 4 × 8 = **960 episode-sets** (with B attempts each). **≈ 12,500 episodes.** | |
| **Estimated cost** | Order **$100–$500** at Flash-tier pricing, dominated by the budget arm. DeepSeek peak/off-peak 2× applies; pin the window. | PROPOSED estimate, derived from published vendor per-token prices and assumed ~5–10 tool-calls/episode; to be confirmed by the 20-case smoke run before committing. |

### 10.2 Pre-registered ordering

1. **Gate 0 — determinism probe** (~30 calls, < $1): identical request × 20; measure exact-match rate. Establishes whether "seed control" is even a coherent concept for these endpoints.
2. **Gate 1 — reachability smoke test** (20 cases × 5 runs × 2 models, ≈ 200 episodes): is mean ASR in a workable band (roughly 5–60%)? If both models are ≈ 0, escalate (see §11).
3. **Gate 2 — main run** (11,520 episodes).
4. **Gate 3 — budget arm** (960 episode-sets) — run last, because it is the most expensive and its interpretation depends on ρ.
5. **Gate 4 — analysis and release** (§10.3).

### 10.3 Analysis to be computed (fixed in advance)

Per configuration cell:

1. `ρ̂` (**beta-binomial**, primary) with **cluster bootstrap** CI over the 144 cases; **GLMM ICC** as sensitivity; **GEE** marginal ASR as a third line.
2. `DE = 1 + (K−1)ρ̂`; `ESS = mK/DE`.
3. **Corrected MDD** via Miller's clustered Eq. 10; reported beside (a) the nominal binomial MDD at the same m and (b) Pathade's 18.2 pp at m = 100.
4. **ASR** with cluster-bootstrap interval **and** Wilson-on-case-means; explicitly *not* Wilson on pooled episodes.
5. **Per-case saturation profile**: distribution of p̂ over cases; the mass at p̂ ∈ {0, 1}. This is the direct test of H1.
6. **Paired exact McNemar** per defense vs control on matched cases, **Holm-corrected** (following Khan et al.); permutation test as robustness where McNemar is degenerate (baseline at 0).
7. **Effect size**: paired risk difference with cluster-bootstrap CI; report alongside BU and UUA so over-refusal is separable from resistance.
8. **Rank-stability curve**: P(subsample of K' runs recovers the K = 10 defense ordering) for K' = 1…10, with case-resampling.
9. **Transfer test**: compare the security ρ and the K→stability curve against the *capability* values published in Alvarado Gonzalez et al. (2025) — this is the §5.1 transfer prediction and the only genuinely novel comparison available.
10. **Budget interaction**: for B ∈ {1,5,10,25} at matched total episode cost, compare ASR, cluster-bootstrap CI width, and defense ordering between the *budget-allocated* and *repetition-allocated* arms. This is contribution 5 and the paper's likely headline.

---

## 11. Falsification criteria

**Pre-registered abandon conditions.** These are the conditions under which we walk away, and they must be written down before the run, not after.

| # | Condition | Reading |
|---|---|---|
| **F1** | `ρ̂` upper 95% CI **< 0.05** | Within-case dependence is negligible. DE ≈ 1, ESS ≈ mK, the corrected MDD ≈ the nominal MDD, and the direction's central premise fails. **Abandon the dependence framing.** (Note: this would still be publishable as a negative result, but it would no longer be a *security* contribution — it would be "the general recommendation transfers, and the field should simply run 2–3 times".) |
| **F2** | Defense ordering at **K' = 2** agrees with the K = 10 consensus for **≥ 95%** of case-resamples | Rankings stabilise almost immediately; the field's ≥ 2-run advice is already sufficient; there is no ranking problem to solve. **Abandon contribution 4.** |
| **F3** | At **matched total query cost**, budget-allocated and repetition-allocated arms give ASRs within **± 2 pp** *and* identical defense orderings | The budget/repetition non-substitutability claim fails. Since this is the surviving novelty, **abandon the direction** rather than retreat to contribution 5. |
| **F4** | `ρ̂` differs across the 2 models with **non-overlapping** bootstrap CIs **and** opposite sign | The quantity is a model artefact, not a property of the evaluation. **Downgrade to a benchmark-and-model-specific descriptive note**, not a general claim. |
| **F5** | **> 70%** of cases sit at p̂ ∈ {0, 1} **and** the remaining cases' ρ is not estimable | The benchmark is saturated. This is the *predicted* risk given Khan et al.'s 0/144, 1/288 baselines. Response: **do not abandon** — instead switch to a configuration with mid-range ASR (weaker defense, or a more vulnerable model, or the `workspace` suite). A saturated benchmark cannot support a dependence estimate; it can only support the claim that the benchmark is saturated, which is a different (and much weaker) paper. |
| **F6** | Reachability smoke test gives mean ASR < 1% for **both** models after one escalation attempt | Both available models are too robust for AgentDojo banking. The pilot cannot be run on the available models. **Blocked — do not proceed to design.** |
| **F7** | A full-text read of R65/R67/R68/R66 reveals a published estimate of ρ (or a design effect) for agent security | The residual closes. **Abandon.** (These are the only unread candidates likely to contain it; reading them is a **precondition** on starting Gate 2.) |

---

## 12. Reviewer simulation

Five objections, each with its legitimacy, the evidence that would answer it, and whether this pilot can supply that evidence.

### Objection 1 — "This is merely proper statistical reporting, and the method is not yours."
**Legitimate because:** Miller (2024) already publishes clustered standard errors, intra-cluster correlation, a variance decomposition, the `K ≫ E[σ²]/Var(x)` rule and cluster-adjusted MDEs; Alvarado Gonzalez et al. (2025) already report an ICC for LLM evaluation; Pathade et al. (2026) already prescribe variance reporting in their checklist. On its face, "estimate ICC, get a design effect, correct the MDD" is a textbook exercise.
**Evidence required to answer:** a *transferable empirical claim*, not a method. Specifically, a measured `ρ_security` that differs materially from the published capability-eval value **and** a demonstrated consequence (a corrected MDD table; a rank-stability curve that contradicts the field's ≥ 2 rule).
**Can the pilot answer it?** **Yes** — but only if the analysis leads with the *comparison* against Alvarado Gonzalez et al. and the *consequence*, never with "we computed ICC". If the result is "ρ_security ≈ ρ_capability", this objection is fatal and F1 applies.

### Objection 2 — "Pathade et al. already established this."
**Legitimate because:** they identify the exact quantity ("effective sample size smaller than m"), state the direction of error ("our MDDs are optimistic"), give the analytic inversion probabilities, and prescribe reporting.
**Evidence required to answer:** the distinction between *naming* and *measuring*, demonstrated by the fact that three independent sources name the quantity and none computes it — Pathade (*"needs model access we did not have"*), Khan et al. (*"not the correlation-aware inferential intervals... task-cluster bootstrap... was not adopted"*), Li et al. (no re-execution). Plus the fact that Pathade publish **no artefact repository**, so the correction cannot be obtained from their work.
**Can the pilot answer it?** **Partly.** The distinction is real and citable, and Khan et al.'s refusal to adopt cluster bootstrap is strong evidence of a live hole. But this is a *narrow* defence: it establishes that a quantity is unmeasured, not that measuring it is important. The pilot's success on this objection rests entirely on the size of the effect.

### Objection 3 — "Repeated runs do not constitute novelty; the field already repeats."
**Legitimate because:** NIST/CAISI ran each attack 25 times; Hofer et al. (2026) run 4 optimization seeds × 6 evaluation runs per injection and report Success@N; Khan et al. (2026) run two independent benchmark replications across 14 configurations; R67 describes 10 attack prompts per case. Any abstract opening with "the field evaluates once" is factually wrong and will be caught.
**Evidence required to answer:** a *corrected mechanism claim* — that existing repetition practice targets the wrong estimand. Both NIST and Hofer et al. express a **budget** quantity (best-of-N, S@N) in the language of repetition; Khan et al.'s two replicas do not vary any named stochastic source and produce a baseline of 0/144 that destroys McNemar power. The claim must therefore be about the *misallocation* of repetition, not its absence.
**Can the pilot answer it?** **Yes, and this is the pilot's strongest card** — but only via the budget arm (contribution 5). Without the budget arm, the pilot is exposed to this objection directly and would fail.

### Objection 4 — "A statistical audit of one benchmark. ρ is a property of AgentDojo, not of agent security. And four Flash-tier models cannot support a general claim."
**Legitimate because:** every measured quantity here is conditional on AgentDojo banking's task structure, injection-goal feasibility, and oracle; Khan et al. themselves caution against generalisation (*"Results are limited to the evaluated benchmark, models, defenses, and conditions"*); two models is two models; and the models are now down to two, both non-Western Flash-tier with mandatory thinking modes.
**Evidence required to answer:** strict scoping stated in the abstract; a **recomputation recipe** so ρ can be measured for any benchmark without new theory; *2-model* ρ with overlapping CIs as the minimal portability evidence (not 4); and an explicit statement that no capability claim is made. The prior "no capability ladder" objection should be pre-empted in writing: the estimand is a variance ratio, so capability spread is a confound to be *avoided*, not a diversity requirement.
**Can the pilot answer it?** **Partly.** The scoping and recipe are free; the portability evidence is weak by construction. This is the objection most likely to survive. The mitigation is to reframe the deliverable from "ρ for agent security" to **"a reproducible procedure for estimating the effective sample size of any agent-security benchmark, instantiated on two benchmarks and two models"**, with the two-benchmark comparison as the minimal generalisation evidence. If the pilot succeeds, the natural follow-up is to run the same recipe on `workspace` (same benchmark, different domain) — which is cheap and materially strengthens the claim.

### Objection 5 — "The stochasticity is API-specific and unmeasured; you cannot even control seeds."
**Legitimate because:** neither `deepseek-flash` nor `glm-5.3-flash` documents a seed parameter; DeepSeek's thinking mode **explicitly ignores temperature**; GLM-5.3-Flash **cannot disable thinking**; solar is excluded; batch-composition nondeterminism is a known phenomenon (R62, **B**); and provider-side revision drift can occur mid-study.
**Evidence required to answer:** the determinism probe (Gate 0) reported as a result; pinned model version strings and per-episode UTC timestamps; a recorded provider fingerprint where exposed; a stated upper bound on what fraction of measured variance could be provider-side; and the explicit admission that repetition count K is *not* a seed-control design.
**Can the pilot answer it?** **Yes, honestly and cheaply.** This objection is best answered by converting the weakness into a reported finding: *"seed control was not available on the evaluated endpoints; we therefore measured the irreducible variance rather than attempting to eliminate it, and we report what fraction of the total cannot be attributed to any controllable factor."* This is a defensible framing and it is exactly the brief's question 1 ("determine which sources can realistically be controlled") — answered **empirically**, not asserted.

---

## 13. Final GO / NO-GO

# **NO-GO** on the direction as framed.
# **GO WITH MAJOR MODIFICATION** on one narrowed question, subject to F6 and F7.

### 13.1 Why the framed direction is NO-GO

The candidate contribution as submitted has six listed components. Assessed against the primary literature read in this pass:

| # | Component | Status | Subsumed by |
|---|---|---|---|
| 1 | Estimate within-case correlation for repeated agent-security outcomes | **Method subsumed; value unmeasured** | Miller 2024 §2.2 (intra-cluster correlation); Alvarado Gonzalez et al. 2025 (ICC for LLM evals) |
| 2 | Estimate design effects and effective sample sizes | **Subsumed as method; arithmetic from (1)** | Miller 2024 §2.2, §3 |
| 3 | Produce corrected MDD estimates | **Subsumed as method** | Miller 2024 Eq. 9–10, Appendix C; Pathade et al. 2026 name the correction |
| 4 | Measure ranking stability as repetitions increase | **Subsumed** (for capability evals) | Alvarado Gonzalez et al. 2025 (83% of slices invert; ≥2 runs); Pathade et al. 2026 Fig. 2b |
| 5 | Attacker budget × repetition interaction | **Residual** | Nobody. Named as separate axes by Pathade (A3 vs A4); conflated by NIST/CAISI and Hofer et al.; absent from Khan et al. |
| 6 | Do repetition recommendations transfer from LLM eval to agent security? | **Residual** | Nobody has compared security ρ against the published capability-eval ICC |

Additionally, the *empirical demonstration* that the framed direction was reaching for has already been published: **Khan et al. (2026)**, peer-reviewed, on AgentDojo, with replications, confidence intervals, the correlation caveat verbatim, paired tests with Holm correction, cost measures, and the underpowered negative result. Items 1–4 as framed are a refinement of an existing paper, and item 6 alone is too thin to carry a paper.

### 13.2 The final research question

> **At a fixed total attacker query cost, are independent repetitions and adaptive attack budget interchangeable — and does the within-case dependence of agent-security outcomes make the field's standing repetition recommendation and its published minimum detectable differences wrong by a measurable factor?**

### 13.3 Hypotheses

- **H1 (mixture).** Agent-security outcomes follow a two-population mixture — near-deterministic cases (p̂ ∈ {0,1}) and a minority of genuinely stochastic cases — so that the *mean* ASR is cheaply and stably estimable while *per-case saturability* is expensive and unstable. **HYPOTHESIS.**
- **H2 (non-substitutability).** At matched total query cost, budget-allocated and repetition-allocated evaluations yield systematically different ASR **and** can order defenses differently, because budget raises the estimand (best-of-B) while repetition narrows the interval around a fixed estimand. **HYPOTHESIS.**
- **H3 (design effect).** The within-case correlation implies a design effect materially greater than 1, so that the effective sample size of a 100-case agent-security benchmark is a small fraction of its nominal size, and the corrected MDD is correspondingly larger than Pathade et al.'s nominal 18.2 pp. **HYPOTHESIS.**
- **H4 (transfer asymmetry).** The repetitions-vs-ranking asymmetry reported for capability evaluation (modest SE shrinkage, large ranking gains — Alvarado Gonzalez et al. 2025) reverses or weakens for security outcomes, because security outcomes are more saturated and more extreme in p. **HYPOTHESIS.**

### 13.4 Minimal pilot

As specified in §10: AgentDojo banking, 144 attack instances, 2 verified models (`deepseek-flash`, `glm-5.3-flash`), 3 defenses + control, K = 10 runs, a reduced adaptive-budget arm at B ∈ {1,5,10,25}, ≈ 12,500 episodes, order $100–500. Four gates, the first two costing under $1 and under ~200 episodes. Analysis chain fixed in §10.3 and methods justified in §7.

### 13.5 Expected contribution

An honest design effect and effective sample size for agent-security evaluation; a **corrected MDD** replacing the literature's independence-assuming figure; a rank-stability curve as a function of repetition count; and the **non-substitutability result** for attacker budget versus repetition. The last is the headline, because it is a security claim rather than a statistical one and it is not occupied by any source located.

### 13.6 Nearest competing paper and exact differentiation

**Nearest:** Khan, AlKhanbashi & Mohamed (2026), *Evaluating Indirect Prompt Injection Defenses in Tool-Using LLM Agents: Security, Utility, and Replication*, Computers 15(9):570.

| Axis | Khan et al. 2026 | This study |
|---|---|---|
| Benchmark | AgentDojo banking | AgentDojo banking *(deliberate, for comparability)* |
| Repetitions | **2** independent benchmark runs | **10** runs/case, giving a rank-stability *curve* |
| Dependence | **Named and declined**: *"not the correlation-aware inferential intervals"*; task-cluster bootstrap *"considered... was not adopted"*; cluster intervals omitted because *"each cell has only two replications"* | **Measured**: ρ, DE, ESS, corrected MDD |
| Intervals | Wilson (per-run and pooled, with a caveat) | Cluster bootstrap + Wilson-on-case-means; Wilson on pooled *rejected* |
| Attacker budget | **Absent** | **Varied** (B ∈ {1,5,10,25}), separated from K |
| Seeds | **Not reported or varied** | Probed, and non-control reported as a result |
| Statistics | Exact McNemar + Holm | Same, **plus** cluster-robust inference and rank stability |
| Cost | Reported (latency, tool calls) | Reported, **plus** the peak/off-peak pricing hazard |
| Alignment | *"More independent replicates... will provide better estimations"* | Supplies the number that tells them **how many** |

**Differentiation in one sentence:** *Khan et al. identify that a pooled interval is anti-conservative and decline to compute the correlation-aware interval because two replications cannot support it; we quantify the dependence, correct the interval and the MDD, and show that the field's repetitions and its attacker budget are not interchangeable.*

### 13.7 Preconditions before any Gate-2 run

Two items, both cheap, one of which is a hard block:

1. **F7 (hard block):** read R65 (SSP-Bench, arXiv:2609.25352), R67 (arXiv:2604.23887), R68 (MDPI Computers 15(7):460), and R66 (*Persona Non Grata*) in full. These are the only unread candidates plausibly containing a published ρ or design effect for agent security. If any does, the residual closes and the direction is abandoned.
2. **F6:** run Gate 0 (determinism probe) and Gate 1 (20-case reachability smoke test). If both available models sit at ≈ 0 ASR on AgentDojo banking, the pilot is blocked and the fallback is a weaker defense configuration or the `workspace` suite.

**Do not begin experimental design beyond the Gates until both preconditions clear.**

---

## Appendix: source-label changes made in this pass

| id | Change |
|---|---|
| **R70** | **NEW** — Khan, AlKhanbashi & Mohamed (2026), Computers 15(9):570, DOI 10.3390/computers15090570. **Label A.** Read in full via browser. Closest competitor. |
| **R71** | **NEW** — Hofer, Debenedetti & Tramèr (2026), arXiv:2606.10525. **Label A.** 4 seeds × 6 evaluation runs; Success@N. |
| **R72** | **NEW** — Miller (2024), arXiv:2411.00640. **Label A.** Clustered SEs, ICC, variance decomposition, `K ≫ E[σ²]/Var(x)`, cluster-adjusted MDE. |
| **R73** | **NEW** — Madaan et al. (2024), arXiv:2406.10229. **Label A.** Resolves the R64 "identifier not captured" gap. |
| **R21** | Upgraded from "A for the abstract; full text NOT yet read" to **A (full text read)**. Full 15-item audit in §1. |
| **R60** | Re-verified **A**; §3 now records that its 57%→80% is a **best-of-25 budget** effect, not a variance measurement. |
| **R35** | Upgraded **B/C → A** for model name, version, context, modality, tool calling, pricing and the thinking-mode temperature restriction (official DeepSeek docs). Seed **still undocumented**. |
| **R37** | Upgraded **B/C → A** for model code, architecture, context, modality, function calling, thinking-mode restriction and recommended sampling parameters (official Z.ai docs). Seed **still undocumented**. |
| **R36** | Partially upgraded: product family confirmed at `mimo.mi.com` (**A**); serving model ID and parameter counts remain aggregator-only (**B/C**). |
| **R38** | Existence confirmed at Upstage's own blog (**A**); all specifications remain aggregator-only (**B/C**); **recommend exclusion** — released ~3 days before this audit, no independent evaluation. |
| **R64** | Identifier resolved to **arXiv:2406.10229**; superseded by R73. |
