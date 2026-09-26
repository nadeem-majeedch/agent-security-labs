# Phase 6 — Final Competitor Elimination and Estimand Audit
## Direction under audit: budget-vs-replication separation in LLM-agent security evaluation

**Date:** 2026-09-25
**Task:** attempt to destroy the remaining research idea before any experimental design.
**Verdict:** **NO-GO.** The direction's central insight is published, formally, with theory and experiment, by a NeurIPS 2025 position paper. Recommendation at the end: **Abandon this direction.**

### Claim-type legend (used throughout)

| Tag | Meaning |
|---|---|
| **[FACT]** | Established at a primary source; verifiable from the cited document |
| **[INFER]** | My inference from established facts; not asserted by any source |
| **[HYP]** | Proposed hypothesis; not established by anyone |
| **[OPEN]** | Genuinely unresolved in the literature as of this audit |
| **[A]** | Fetched and read at source | 
| **[B]** | Search-level only | **[C]** | Not verified |

Nothing in this document is a fabricated citation, result, URL, DOI, or number. Sources I could not read are marked unread and are not leaned on.

---

# PART A — Destroy the novelty claim

## A.1 The three axes, defined

The candidate rests on distinguishing:

| Axis | Symbol | Meaning |
|---|---|---|
| **A — attack attempts against the same case** | *b* | More adaptive/query attempts against one case; a *budget* |
| **B — independent evaluation cases** | *m* | More distinct cases; sample size |
| **C — repeated stochastic executions of the same case** | *r* / *K* | Re-running one case at fixed budget; a *replicate* |

## A.2 Has anyone already separated them? — **YES.**

**[FACT]** The conceptual separation of A from C is **established, named, and formalized** by Chouldechova, Cooper, Barocas, Palia, Vann & Wallach, *Comparison requires valid measurement: Rethinking attack success rate comparisons in AI red teaming*, **NeurIPS 2025 (position paper)**, arXiv:2601.18076, all authors Microsoft Research **[A]**. This is the decisive source for this phase.

Their central formal result is exactly the candidate's H2. Verbatim:

> *"In this section, we discuss this issue through a three-part case study of **repeated sampling for non-deterministic target system configurations. We show that repeated sampling has the effect of, in the language of §2, changing the underlying estimands.**"*

They define both estimands explicitly:

- One-shot: `α = ℙ_{P∼D}[J(L(P;φ)) = 1]`
- Top-1 of K: `α_{Top1(K)} = ℙ_{P∼D}[max_{k∈{1,…,K}} J(L(P;φ)_k); P) = 1]`

and state:

> *"comparing Top-1 (of 392) to one-shot is akin to comparing 2-year survival under treatment to 3-year survival under control. **It is fundamentally apples-to-oranges.**"*

> *"when prompt-level success is defined as at least one attack succeeding, **we can trivially improve the ASR of any jailbreak through repeated sampling** using a non-deterministic configuration."*

with the mechanism `1 − (1−p)^K` for per-prompt probability `p`. They further note that term usage is inconsistent: *"Appendix C provides additional discussion of aggregations and resulting estimands, including remarks on how terms like 'Top-1' are used inconsistently in the literature to refer to different aggregation schemes."*

They also supply the **per-case heterogeneity mechanism** (the candidate's H1/H3), verbatim:

> *"while the average one-shot attack success probability (the mean of the distribution shown in the histograms) does not change, the **distributional shift has a large effect on Top-1 type metrics under resampling**. This is because the probability that a prompt P₀ with success probability p₀ succeeds on at least one of K samples, `1−(1−p₀)^K`, grows rapidly as p₀ moves away from 0 for even moderate K."*

> *"as we increase the temperature, the entropy of the prompt-level attack success probability distribution increases. **The success probability actually decreases for many prompts, but also more prompts move away from an effectively-0 success probability** to a slightly larger one."*

**[INFER]** That is the candidate's H3 in the literature's own words: an aggregate quantity can remain flat while the per-case classification of vulnerable cases changes, and the change interacts with the sampling budget. They also demonstrate it experimentally (Llama-2 7B/13B Chat, 100 MaliciousInstruct prompts, 49 decoding configurations × 49 samples per prompt per configuration): one-shot ASR stays ≈0.2 across configurations while Top-1 ASR rises with temperature, K and p.

They additionally supply a **concrete literature failure**: GCG (`A = 0.31`, one-shot of 500 steps) vs Generation Exploitation (`A = 0.89`, Top-1 of 392) in Huang et al.; and Chu et al.'s 17 jailbreaks × 8 models compared as Top-1 (of ~50) against a one-shot "baseline". They report that **Top-1 ASR over 50 repeated resamples of the base prompt at temperature 2.0 is 0.83** on Llama 2 7B Chat — i.e. resampling the unmodified prompt rivals published "sophisticated" jailbreaks. They recommend the Best-of-N jailbreak as a required stronger baseline.

**[FACT]** Separation of the *adaptive-attack budget* axis (A) from the rest, in a defense-comparison setting, is demonstrated by Deep, Emmons, Fox, Bacon, McAllister, Ortiz & Flautner (Swept AI + University of Michigan), arXiv:2604.23887 **[A]**:

> *"We built an adaptive attacker that evolves its strategies over **hundreds of rounds** and tested it against **nine defense configurations** across **more than 20,000 attacks**."*
> *"Campaigns run from **25 to 500 rounds with 10 attacks per round**."*
> *"The sandwich defense went from a **0.4% leak rate in 25 rounds to 3.8% over 277 rounds**, with worst-case severity escalating from 0.05 to 0.95. **Any evaluation of prompt injection defenses that runs fewer than 50 to 100 rounds risks significantly overestimating defense effectiveness.**"*

Break points: input sanitization round 39, security directives 49, delimiter 84, instruction hierarchy 247, sandwich 277. They also describe a reproducible **two-phase pattern** — a long near-zero probing phase, then an abrupt single-round breakthrough to ≥0.9.

**[FACT]** Separation of *attack-side* randomness from *evaluation-side* randomness (A/C boundary) is implemented in agent security by Hofer, Debenedetti & Tramèr (ETH Zurich), arXiv:2606.10525 **[A]** — see Part D. And they report **both** an ASR and a Success@N figure, which means the budget/estimand divergence is already *measured on agents*.

**[FACT]** Replication at fixed budget on AgentDojo is reported by Khan, AlKhanbashi & Mohamed (2026) — see Part C.

**[FACT]** SSP-Bench (Deniz, Boshmaf & Khalil, QCRI, arXiv:2609.25352) **[A]** separates the *case-sampling* axis (B) from everything else by design, holding evaluation deterministic: *"Validation rules and the selection objective are deterministic, and evaluation of a given benchmark instance is deterministic given fixed model checkpoints and decoding temperature; stochasticity is confined to the sampling-based components named above."* It then measures rank stability across **3 independent runs of the generation pipeline** via Kendall's τ, rescaled as `Stab = (1+τ)/2`. It also formalises per-item difficulty and separability as `f_sep(c) = p_c(1−p_c)` — the candidate's "case heterogeneity" construct under standard psychometric names.

## A.3 Adjacent fields

**[FACT]** The reliability side (axis C) is fully solved in the adjacent LLM-evaluation literature (Miller 2024, arXiv:2411.00640 **[A]**: clustered standard errors, intra-cluster correlation, variance decomposition, `K ≫ E[σ²]/Var(x)`, cluster-adjusted MDE). Fuzzing / software-testing / cybersecurity query-budget literature adds nothing that overturns this; the budget-as-budget distinction (`best-of-N`, `pass@k`) is textbook.

**[FACT]** A standards body is currently specifying agent-security benchmarking **without any uncertainty protocol**: IETF `draft-han-bmwg-agent-security-benchmark-00` (China Mobile, published 2026-07-05, Internet-Draft, *"inappropriate to use... as reference material or to cite"*) defines 4 dimensions and **55 second-level metrics**, all pass-rates (`Metric Value = Number of Passed Test Cases / Total Number of Test Cases`), with no confidence intervals, no repetition count, and no budget specification **[A]**.

## A.4 Part A conclusion

**Someone has already experimentally separated these axes — and, more damagingly, someone has already established the conceptual claim that doing so matters.** The candidate treats "budget changes the estimand, replication contracts uncertainty" as a hypothesis to be discovered. Chouldechova et al. state it as a position, define both estimands, and demonstrate the divergence. Deep et al. demonstrate budget sensitivity of defense conclusions. Hofer et al. demonstrate the ASR-vs-Success@N divergence **on agents**. Khan et al. report AgentDojo replication variability. SSP-Bench isolates the remaining axis.

**[INFER]** The candidate is not redundant with any *single* paper, because nobody has run the full `budget × cases × replicates` factorial in agent security. But the *insight* is taken, and each *component* has been handled. What remains is a combination with no new mechanism — which is a replication study, not a discovery.

---

# PART B — The four unread candidates

## B.1 SSP-Bench — arXiv:2609.25352 **[A]**

| Item | Extraction |
|---|---|
| Research question | Can dynamic, on-demand instance generation reveal behavioural differences that *static* SSP benchmarks miss (score saturation, contamination, aggregation artifacts)? |
| Threat model | Not an attacker/defender deployment model; adversarial prompts grounded in the AIAAIC incident corpus. |
| Benchmark | SSP-Bench itself: 4 services (safety, hallucination, over-refusal, privacy), generated benchmarks; 24 models; steering + evaluation + testing panels. |
| Unit of analysis | **Item (candidate prompt) × model.** Per-item difficulty and separability. |
| Number of cases | Varies per generated instance; safety deployed subsets N=830 (grounded) and N=938 (mutation). |
| Number of repeated runs | **3 independent runs of the *generation pipeline*.** |
| Attack attempts per case | **None** — single response per item; evaluation held deterministic. |
| Attack budget varied? | **No.** |
| Replication varied independently? | **No** — the 3 runs vary benchmark generation, not evaluation of a fixed benchmark. |
| Per-case outcomes reported? | **Yes** — `f_diff(c)` (fraction of models failing) and `f_sep(c) = p_c(1−p_c)`, plus `p_c` = per-item success rate **across models**. |
| Aggregate ASR reported? | Aggregate *scores* per model and service. |
| Confidence intervals? | **Yes for the construct-mixing comparison** (e.g. refusal-only average τ=0.670, 95% CI [+0.478, +0.841]; aggregate τ=−0.016, 95% CI [−0.394, +0.360]). |
| Uncertainty decomposed? | **No.** |
| Case-level heterogeneity analysed? | **Yes**, as item difficulty/separability — but as a *selection criterion* for benchmark assembly, not as an inference problem. |
| Ranking stability analysed? | **Yes** — Kendall τ across pipeline runs; `Stab` and `Q`. |
| Defense conclusions change with budget? | **No** — no defences. |
| Explicitly distinguishes budget from replication? | **No.** It separates *item sampling* from a deterministic evaluation. |
| Relevant limitations / future work | Stab is measured across generation runs; the paper treats stochasticity as confined to generation. |

**Overlap assessment. [INFER]** Low-to-moderate. SSP-Bench is about **item sampling** (axis B) and rank stability across *benchmark regenerations*. It does **not** vary budget, does not repeat stochastic executions of a fixed case, and its `p_c` is across *models*, not across *replicates* — a different quantity from the candidate's `p_c`. Its main relevance is terminological: the candidate's H1 ("heterogeneous mixtures of near-deterministic cases") is **standard item difficulty/discrimination in IRT**, and SSP-Bench uses exactly that formalism. A reviewer will say H1 is a known construct, not a new hypothesis.

## B.2 arXiv:2604.23887 **[A]** — see Part A.2 for the full extraction. Summary:

| Item | Extraction |
|---|---|
| Research question | Can prompt-injection defences be trusted against an attacker that **adapts and persists**? |
| Threat model | Black-box, direct prompt injection against an LLM app with secrets in the system prompt; attacker and defender are separate agents with no shared memory. |
| Benchmark | **Custom** — 3 embedded secrets, 5 operational instructions, SecureBot persona, 9 defence configurations (t0–t8). |
| Unit of analysis | **Round** (10 attacks per round), not case. |
| Number of cases | No case population; one target system per configuration. |
| Number of repeated runs | 25 rounds baseline; extended until score ≥0.9 or 500 rounds; t5/t7 stress-tested **3 independent times at 500 rounds**. |
| Attack attempts per case | 10 per round; up to 5,000 per configuration. |
| Attack budget varied? | **Yes, explicitly** (25 → ≤500 rounds). |
| Replication varied independently? | **Partially** — 3 replicas, but only for the two survivors, to confirm a zero. |
| Per-case outcomes reported? | **No.** |
| Aggregate ASR reported? | Leak rate, defined as **% of *rounds* with a detected leak** — an unusual and non-standard denominator. |
| Confidence intervals? | **No.** |
| Uncertainty decomposed? | **No.** |
| Case-level heterogeneity analysed? | **No.** |
| Ranking stability analysed? | **No** — defences were tested separately, not ranked. |
| Defense conclusions change with budget? | **Yes — this is the paper's methodological core.** |
| Distinguishes budget from replication? | **No.** |
| Limitations | Single-turn only; substring scoring misses fuzzy/encoded leaks; no uncertainty quantification. Vendor paper (Swept AI), arXiv only, not peer-reviewed. |

## B.3 Computers 15(7):460 — SafeBoundary-LLM **[A]**

| Item | Extraction |
|---|---|
| Research question | Do safety boundaries remain stable **during conversation** for local open-weight LLMs, rather than only on isolated prompts? |
| Threat model | Single-turn adversarial prompts and 5-turn escalation conversations; not an adaptive attacker with a query budget. |
| Benchmark | SafeBoundary-LLM (7 local models, 14 sensitive domains, 84 boundary sets, 672 single-turn prompts, 84 five-turn escalation conversations) + XSTest + JBB-Behaviors. |
| Unit of analysis | **Response**, with **boundary set** and **source item** as clustering units. |
| Number of cases | 7,644 responses in SafeBoundary-LLM + external sets; 12,194 responses classified in total. |
| Number of repeated runs | **One** — but with **fixed decoding**: `temperature = 0.0, top_p = 1.0, top_k = 40, seed = 42`. |
| Attack attempts per case | **None.** |
| Attack budget varied? | **No.** |
| Replication varied independently? | **No** — stochasticity was *eliminated*, not studied. |
| Per-case outcomes reported? | Per-response labels; aggregated by domain/boundary set. |
| Aggregate rates reported? | **Yes**: multi-turn failure 14.69% vs single-turn 0.51%, **rate ratio 28.80 (95% CI [21.20, 43.80]; Holm-adjusted p = 0.0006)**; over-refusal 4.34% (XSTest) and 17.29% (JBB). |
| Confidence intervals? | **Yes** — plus **cluster bootstrap**, 10,000 deterministic replications, seed 42. |
| **Clustering handled?** | **Yes, explicitly**: *"cluster bootstrap resampling, with the boundary set used as the resampling unit for SafeBoundary-LLM and the source item used for XSTest and JBB-Behaviors **so that the seven model responses associated with the same public prompt remained within the same bootstrap cluster**."* Plus unweighted Cohen's κ and Holm adjustment over six tests. |
| Uncertainty decomposed? | **No.** |
| Case-level heterogeneity? | Partially (turns 4–5 only). |
| Ranking stability analysed? | Cites judge positional bias and ranking instability as *motivation*; does not measure it. |
| Defense conclusions change with budget? | **No** — no defences. |
| Distinguishes budget from replication? | **No.** |
| Relevance | **This erodes the "correlation-aware interval" residual.** Cluster bootstrap for LLM safety evaluation is already published, in a peer-reviewed journal, with the clustering rationale stated. **But note the clustering reason is unrelated to the candidate's**: they cluster because *different prompts share a boundary set*, i.e. Miller's "questions drawn in groups" — **not** because a single case was re-run. |

## B.4 Persona Non Grata — **UNREAD**

OpenReview (`forum?id=dyKvBEOToq` and the `/pdf` route) is behind a browser-verification challenge; both fetch and interactive browser access were refused. **Not read, not leaned on.** **[C]** Its abstract-level description ("Persona Rank Inversion Between Methods") would concern rank inversion *between evaluation methods*, not budget-vs-replication, and it cannot change the verdict reached in Part A.

---

# PART C — Khan et al. (2026), Computers 15(9):570

## C.1 The sixteen questions

| # | Question | Answer |
|---|---|---|
| 1 | What does "two independent replications" mean? | **[FACT]** *"The benchmark was executed twice for each of the 14 evaluated model–defense configurations."* Each run = 144 attack instances + 16 benign-task evaluations. |
| 2 | What is held fixed across replications? | **[FACT]** The benchmark tasks and the configuration-specific evaluation procedure: *"Each run used the same benchmark tasks and configuration-specific evaluation procedure."* |
| 3 | What is varied? | **[INFER]** Only the execution occurrence. **No** named stochastic source is varied or reported — the word "seed" does not appear in the article, and neither does "temperature". |
| 4 | Are attack attempts repeated? | **No.** |
| 5 | Are benchmark instances repeated? | **Yes** — the same 144 instances in both runs. |
| 6 | Is attack search randomness repeated? | **No** — no attacker search; injections are benchmark-provided. |
| 7 | Is model sampling randomness repeated? | **Presumably**, but unattributed and undocumented. **[INFER]** |
| 8 | Is the attack budget identical? | **Yes** — and there is no budget in the design at all. |
| 9 | Is budget ever varied experimentally? | **No.** |
| 10 | Are the same vulnerable cases observed across replications? | **[FACT]** Not reported. No per-case stability table appears. |
| 11 | Per-case stability reported? | **No.** |
| 12 | Any case-level correlation? | **No** — the strings "intraclass" and "design effect" appear nowhere. |
| 13 | Do they distinguish budget / replication / stochastic-execution effects? | **No.** They distinguish *replication* only, and explicitly decline the correlation-aware treatment of it. |
| 14 | What does the pooled-Wilson statement mean? | **[FACT]** Verbatim: *"For the pooled two-run counts, these intervals are descriptive summaries of the observed proportions and **not the correlation-aware inferential intervals. As the same benchmark instances were repeated in the runs, a pooled Wilson interval can be narrower than the interval explicitly accounting for the correlation.**"* And: *"robust across-run summary statistics (e.g., medians or cluster bootstrap intervals) are not estimated because each cell has only two replications."* And: *"The workflow diagram lists **task-cluster bootstrap as an approach considered during method planning; it was not adopted**."* |
| 15 | Does their analysis permit estimating `P(success\|budget, case)`, between/within-case variance, ranking stability? | **No, none of them.** Two replications cannot identify a within-case variance component; there is no budget factor; ranking stability is not analysed. Their reported collapse is itself the evidence: undefended baselines of **0/288 (GPT-5.4)**, **11/288 (GPT-5.4-mini)**, **1/288 (Claude Sonnet 4.6)** leave *"no discordant pairs and leaving the exact McNemar test without power"*, and they conclude the test *"has no practical power to detect a defense effect of any size."* |
| 16 | Could a new paper performing the full `budget × cases × replicates` factorial still make a scientifically meaningful contribution? | **NO — see C.2.** |

## C.2 Direct answer to question 16: **NO**

**Justification.** A factorial separation would be *methodologically* new (nobody has run it in agent security) but *scientifically* redundant, on four independent grounds:

1. **The theoretical claim is settled. [FACT]** Chouldechova et al. (NeurIPS 2025) already establish that Top-1-of-K and one-shot ASRs are different estimands and that comparing them is apples-to-oranges. A factorial in agent security would *confirm* a published position, not establish one.
2. **The empirical divergence is already reported on agents. [FACT]** Hofer et al. (2026) report ASR and Success@N **side by side on AgentDojo** — e.g. GPT-5 at *"~5% ASR, 30% S@N"*. A ~6× inflation from the same underlying system is exactly the effect the candidate proposes to discover.
3. **Budget sensitivity of defense conclusions is already demonstrated. [FACT]** Deep et al. show a defence moving from a 0.4% to a 3.8% leak rate and from 0.05 to 0.95 severity across 25→277 rounds, and state the methodological warning explicitly.
4. **The residual statistical piece is a transplant. [FACT]** Design effects and cluster-robust inference are published for LLM evals (Miller 2024) and cluster bootstrap is published for LLM safety evaluation (SafeBoundary-LLM 2026). What would remain is applying them to agent data.

**[INFER]** What is left is a *quantification study in a new domain*: "how big is the effect for agent benchmarks?" The candidate's own standard — and this phase's instruction that it is better to kill the project than manufacture a weak novelty claim — rules that out.

---

# PART D — Hofer et al. (2026), arXiv:2606.10525

## D.1 What is repeated, and which randomness

**[FACT]** The protocol, verbatim: *"(1) Optimization: We performed **n = 4 independent optimization runs** for each task (or universal set) using **different random seeds**. (2) Evaluation: **Each generated injection was evaluated m = 6 times** against the target agent to account for **non-determinism in tool execution**."*

| Axis | Where it sits |
|---|---|
| The **4 seeds** index | **Attack-generation randomness** — the GCG/TAP search. Different seeds produce *different injections*. |
| The **6 evaluation runs** index | **Evaluation-side randomness** — target sampling + tool execution, at fixed injection. |
| Attack **budget** | **Not varied as a curve.** TAP has structural hyperparameters (3 root nodes, branching 3, max width 8, max depth 5) and GCG has 800 steps × 256 candidates, but these are configuration, not a budget axis under study. |

**[FACT]** They also use *"reliability retries [that] average evaluator scores across multiple trials to provide a stable signal despite non-deterministic target responses."*

## D.2 Does Success@N change the estimand? — **Yes, mathematically**

Let `p_c(b)` be the per-case success probability at budget `b`. Then under independent attempts:

- **One-shot / fixed-budget estimand:** `α_c = p_c(b)`. Estimated by replication as `p̂_c = (1/R)·Σ_r 1[success]`, with `E[p̂_c] = p_c` and `Var(p̂_c) = p_c(1−p_c)/R` (or larger under clustering).
- **Success@N:** `S_N = ℙ(∃ success among N attempts) = 1 − Π_{i=1..N}(1 − p_c^{(i)}) = 1 − (1 − p_c)^N` for i.i.d. attempts.

**[INFER]** These are **different functionals of the same `p_c`**. Increasing *N* drives `S_N → 1` monotonically; increasing *R* drives `p̂_c → p_c`. **One moves the target; the other narrows the estimate.** They are not interchangeable, and no amount of replication recovers `p_c` from `S_N` without knowing *N* and the independence assumption. This is precisely Chouldechova et al.'s one-shot-vs-Top-1 distinction, instantiated with an agent trajectory in the loop.

**[FACT]** Hofer et al. *define* the difference explicitly: *"Success@N (S@N): The fraction of test cases where at least one attack succeeds within N separate optimization and evaluation attempts... This captures the effectiveness of stochastic methods like GCG and TAP, which may require multiple restarts, **as well as addressing the non-deterministic nature of the target LLM**."* **[INFER]** That sentence is a budget quantity and a replication quantity fused into one metric — which is the *diagnostic problem* the candidate wanted to name. But Hofer et al. handle it *correctly* in the practical sense: they report **both** ASR and S@N, so a reader can see both the one-shot rate and the budget-conditional rate.

## D.3 Does their design already answer the candidate's question?

**Substantially, yes — for the part that mattered. [INFER]**

- Does it separate budget from replication? **No** (no budget curve).
- Does it separate *attack-side* randomness from *evaluation-side* randomness? **Yes** — 4 attack seeds vs 6 evaluation replicates, orthogonally.
- Does it change the estimand via budget? **Yes** — S@N is a Top-1-of-N estimand.
- Does it report both estimands so the divergence is visible? **Yes.**
- Does it quantify uncertainty, decompose variance, or test ranking stability? **No.**

**[INFER]** The candidate's strongest surviving claim was "budget changes the estimand while replication does not." Hofer et al. already *publish the two numbers* that show this on agents. That converts the candidate's H2 from a discovery into a restatement.

---

# PART E — NIST / CAISI: what are the 25 attempts?

**[FACT]** (*Strengthening AI Agent Hijacking Evaluations*, NIST/CAISI technical blog, posted 2025-01-17, updated 2025-12-19; non-peer-reviewed; artifact `github.com/usnistgov/agentdojo-inspect`) **[A]**: five injection tasks on upgraded Claude 3.5 Sonnet, *"attempted each attack 25 times"*, average ASR **57% → 80%**, and *"the attack success rate for individual tasks changed significantly."* Insight #4: *"Testing the success of attacks on multiple attempts may yield more realistic evaluation results."*

**Classification, applied strictly:**

| Candidate reading | Verdict |
|---|---|
| Independent attack attempts? | **Yes** — 25 attempts at the same injection goal. |
| Repeated stochastic executions? | **Not the object of study.** Any per-task stochasticity is averaged into "did any of the 25 succeed". |
| Attack-budget increases? | **Yes — this is the primary reading.** |
| Independent benchmark cases? | **No** — five tasks held fixed. |
| Combination? | **Effectively a budget increase; the repetition aspect is not analysed.** |

**What estimand are the 25 attempts estimating? [INFER]** The fraction of the five injection tasks on which the attacker achieved success **within a budget of 25 attempts** — i.e. a per-task Top-1-of-25 (`1 − (1−p_c)^25`), averaged over 5 tasks. It is **not** an estimate of `p_c` and it carries **no uncertainty statement** (no CI, no dispersion, no repetition of the whole protocol).

**Is 57% → 80% evidence about uncertainty, budget sensitivity, or both?** — **Budget sensitivity, with a secondary and unquantified signal about heterogeneity.**

- It is **not** evidence about uncertainty: no variance of the estimate is reported, and the protocol was not repeated, so no sampling distribution is available.
- It **is** evidence about budget: the same five tasks, the same model, more attempts, systematically higher success. **[INFER]** Given `1−(1−p_c)^25`, going 57%→80% across tasks implies non-trivial per-task `p_c > 0` — i.e. tasks that a single run would score 0 are budget-saturable.
- **[INFER]** The observation that per-task rates "changed significantly" is *consistent with* the candidate's H1/H3, but it is unquantified and reported as an aside. It is suggestive, not established.

**Do not call these replications. [FACT]** The blog itself uses "attempts", and the reported quantity is a budget-conditional success rate.

---

# PART F — The central statistical question, formalised

## F.1 The quantities

Let `c` index a benchmark case (task × injection pair), `b` a budget (attempts allocated against that case), and `r` a replicate (a fresh stochastic execution).

- Per-case success probability at budget `b`: `p_c(b) = ℙ(attack succeeds on case c | budget b)`.
- The fixed-budget aggregate estimand: `ASR(b) = E_{c∼C}[p_c(b)]` — a population mean over a case super-population.
- A replicate estimate: `p̂_c(b) = (1/R) Σ_{r=1}^R Y_{c,r}(b)`, with `Y ∈ {0,1}`.
- The budget-conditional Top-1 estimand: `S_N(b) = E_c[1 − (1−p_c(b))^N]`.

## F.2 Is `ASR(b₁) ≠ ASR(b₂)` a change of estimand?

**Yes. [FACT, per Chouldechova et al.; INFER in the agent instantiation]** Two separate things differ:

1. **A change of functional.** `p_c(b)` is not `max`-aggregated over `b`; the estimand is a *different function of the same underlying stochastic process* at different `b`. Chouldechova et al. formalise this for one-shot vs Top-1-of-K and call the comparison "fundamentally apples-to-oranges".
2. **A change of the underlying process.** With an *adaptive* attacker, increasing `b` also changes *what is attempted* — attempt `b+1` is conditioned on feedback from attempts `1..b`. So `p_c(b)` is not merely a re-aggregation; it is a different generative process. **[INFER]** This is the strongest defensible version of "budget changes the estimand", and it is exactly what Deep et al.'s rounds campaign exhibits (probing phase → breakthrough), and what Pathade's A4 axis names.

**By contrast, increasing `r` at fixed `b` does not move the estimand.** It reduces `Var(p̂_c) = p_c(1−p_c)/R` (or, under clustering, `p_c(1−p_c)·[1+(R−1)ρ]/R`). **[FACT]** Miller 2024 §3.1 establishes the diminishing-return structure: `Var(s_i) = σ_i²/K`, and once `E[σ_i²]/K ≪ Var(x)` further K "will have little effect".

## F.3 Heterogeneity: can `ASR(b)` be stable while individual `p_c(b)` is unstable? — **Yes, and this has been shown**

**[FACT]** Chouldechova et al.: *"while the average one-shot attack success probability... does not change, the distributional shift has a large effect on Top-1 type metrics under resampling."* They report that as temperature rises, per-prompt success probability *decreases* for many prompts while more prompts move off effectively-zero — mean flat, distribution changed.

**[INFER]** The converse is equally possible: mean ASR moves while individual classifications are stable (if a few cases strictly gain saturability). Both are empirical questions, and both are already answerable with a per-case design.

## F.4 Could increasing `b` systematically change *which* cases are vulnerable?

**[INFER]** Yes, and this is the most interesting surviving question — but note it is the *adaptive-attacker* version, not the replication version. If the attacker conditions on feedback, budget reallocates search towards cases that respond to refinement, so the *set* of compromised cases can change qualitatively, not just in size. **[FACT]** Deep et al. observe the two-phase probing/breakthrough pattern that produces exactly this. **[HYP]** Whether it holds systematically across cases is untested.

## F.5 Could defense rankings change as `b` changes?

**[INFER]** Yes, and the mechanism is concrete: defences differ in their *break-time*, so ranking is a function of the budget at which it is measured. **[FACT]** Deep et al.: on a 25-round budget, seven of nine configurations show a 0% leak rate and the ordering is uninformative; by round 277 a ranked order exists among the same configurations, and t5/t7 remain at 0. **[INFER]** So a ranking computed at 25 rounds differs from one computed at 500 rounds. This is established-by-inspection, though not reported as a ranking analysis.

## F.6 What this section changes

**[INFER]** Part F was intended to *articulate* the candidate's insight. Executing it revealed that the articulation is already published (F.2, F.3) and the agent-specific consequences are already demonstrated (F.4, F.5). The remaining contribution is quantification.

---

# PART G — Is there a surviving contribution?

## G.1 Verdict on the proposed framing

**No.** The framing — *"we experimentally disentangle attack-budget effects from replication effects and show when conclusions about security and defenses are sensitive to the allocation of evaluation computation"* — is **not novel**, for the reasons in Parts A–F. Every clause is occupied:

- "attack-budget effects [differ] from replication effects" → **Chouldechova et al. 2026 [FACT]**
- "conclusions about security and defenses are sensitive to the allocation of evaluation computation" → **Deep et al. 2026 [FACT]**, at least for the budget axis
- "the allocation of evaluation computation" as a design variable → **Hofer et al. 2026 [FACT]** (attack seeds vs evaluation replicates)

## G.2 What a defensible contribution would have to be

**[INFER]** To survive, a contribution would need a *mechanism or quantity that no located work provides*, of a kind that changes practice. Candidates that were considered and rejected:

| Candidate | Why rejected |
|---|---|
| "Measure ICC / design effect / ESS in agent security" | Method published (Miller 2024); the reported value is a number, not a mechanism. |
| "First factorial `budget × cases × replicates` in agent security" | Confirms a published position; a replication, not a discovery. |
| "Show defenses degrade under budget" | Demonstrated (Deep et al. 2026). |
| "Show ASR and Top-1 diverge on agents" | Demonstrated (Hofer et al. 2026, ASR vs Success@N). |
| "Show rankings are unstable at low budget" | Follows directly from Deep et al.'s break-times. |
| "Quantify per-case saturation in agent security" | H1 is standard item difficulty/discrimination (SSP-Bench, IRT); the quantification alone is thin. |

**[INFER]** The single most promising unexploited item located in this entire audit is **not** in the candidate's frame at all, and comes from Chouldechova et al. §5 — see Part L.4.

---

# PART H — Minimal novel study

**Not performed.** Part H is conditional on the idea surviving Parts A–G. It did not. Designing a pilot would manufacture exactly the weak novelty claim this phase instructed against. **[HYP]** A sketch is retained only as a record of the rejected design: AgentDojo banking, 144 cases, `b ∈ {1,5,10,25}` adaptive rounds, `K = 10` replicates, 2–3 defences — which Part C.2 rules out on grounds (1)–(4).

---

# PART I — Estimands, and why they do not rescue the direction

**[FACT]** Notation: `c` = case, `b` = budget, `r` = replicate, `Y_{c,b,r} ∈ {0,1}`.

| # | Estimand | Definition | Estimator | Status |
|---|---|---|---|---|
| 1 | Fixed-budget attack success | `ASR(b) = E_{c∼C}[p_c(b)]` | `(1/(mK)) ΣΣ Y_{c,b,r}` | Standard |
| 2 | Per-case success probability | `p_c(b)` | `(1/K) Σ_r Y_{c,b,r}` | Standard |
| 3 | Budget sensitivity | `ΔASR = ASR(b₂) − ASR(b₁)` | difference of (1) | **Conflates two estimands [FACT: Chouldechova §4]** |
| 4 | Case saturation | `S_c(b₁,b₂) = 1[p̂_c(b₁) ≠ p̂_c(b₂)]` or `1[p̂_c ∈ {0,1}]` | per-case indicator | **Item difficulty/separability [FACT: SSP-Bench §2.3]** |
| 5 | Ranking stability across budgets | `ℙ(R(b_i) = R(b_j))`, Kendall τ | subsample comparison | **Implicit in break-time differences [FACT: Deep et al.]** |
| 6 | Uncertainty at fixed budget | `Var(p̂_c) = p_c(1−p_c)[1+(K−1)ρ]/K` | beta-binomial / cluster bootstrap | **Published [FACT: Miller 2024]** |

**Terminology, strictly separated:**

| Term | Indexes | Role |
|---|---|---|
| **Estimand** | — | the population quantity targeted |
| **Estimator** | — | the function of data used |
| **Benchmark case** | `c` | unit of the case super-population; the cluster |
| **Attack attempt** | `b` | a query in a budget; *moves the estimand* |
| **Replication** | `r` / `K` | a stochastic re-execution; *contracts uncertainty* |
| **Budget** | `b` | the number of attempts allocated; a design factor, not a replicate |

**[INFER]** Estimands 1, 2, 4 and 6 are published constructs; 3 and 5 are published as *warnings* by Chouldechova et al. and Deep et al. respectively. There is no estimand here that is both well-posed, unclaimed, and consequential.

---

# PART J — Falsification test

## J.1 The criteria, and which are already met

| # | NO-GO criterion | Met? | Evidence |
|---|---|---|---|
| J1 | A prior paper already separates budget from replication | **PARTLY MET** | Chouldechova et al. separate one-shot from Top-1-of-K **conceptually and experimentally**; Hofer et al. separate attack seeds from evaluation replicates on agents; Deep et al. vary budget across defences |
| J2 | A prior paper establishes that budget changes the estimand | **MET** | Chouldechova et al.: *"repeated sampling has the effect of... changing the underlying estimands"*; *"fundamentally apples-to-oranges"* |
| J3 | Defense conclusions are already shown to depend on budget | **MET** | Deep et al.: 0.4% → 3.8% leak rate, 0.05 → 0.95 severity, 25 → 277 rounds; *"fewer than 50 to 100 rounds risks significantly overestimating defense effectiveness"* |
| J4 | Case-level heterogeneity is already shown to matter and is already a standard construct | **MET** | Chouldechova et al. per-prompt histograms and entropy shift; SSP-Bench `f_sep(c) = p_c(1−p_c)`; IRT |
| J5 | The statistical machinery for the replication axis is already published for LLM evals | **MET** | Miller 2024 (clustered SE, ICC, variance decomposition, `K ≫ E[σ²]/Var(x)`, cluster-adjusted MDE) |
| J6 | Correlation-aware intervals are already published in LLM safety evaluation | **MET (adjacent)** | SafeBoundary-LLM 2026: cluster bootstrap with stated clustering rationale |
| J7 | Replication in agent security is already practised and reported | **MET** | NIST/CAISI 25 attempts; Hofer et al. 4×6; Khan et al. two runs on AgentDojo; Deep et al. 3 replicas at 500 rounds |
| J8 | "Better ASR reporting" is already proposed | **MET** | Pathade et al. 10-item checklist; Li et al. minimum reporting standards; Chouldechova et al. four recommendations |
| J9 | Budget changes are negligible across realistic ranges | Not met | The opposite is shown |
| J10 | Replication and budget are statistically interchangeable | Not met | The opposite is shown |
| J11 | Findings only occur in one artificial environment | Not met | Shown across jailbreaking, direct injection, and AgentDojo |
| J12 | Two models cannot produce informative variation | Not met | Irrelevant — the direction fails earlier |

## J.2 Additional criteria I add

| # | Criterion | Met? |
|---|---|---|
| **J13** | The proposed contribution can be restated as applying a published framework to a new domain, with the framework's authors having already declared its scope to be general | **MET** — Chouldechova et al.: *"we focus on jailbreaking, though the ideas are broadly applicable to ASRs obtained via other AI red teaming approaches"* |
| **J14** | The residual empirical quantity is a number whose interpretation depends on no new mechanism | **MET** — ρ, DE, ESS are descriptive of a benchmark |
| **J15** | The strongest version of the contribution requires only existing tools on existing benchmarks | **MET** — AgentDojo + beta-binomial + bootstrap |
| **J16** | Falsification would leave nothing publishable | **MET** — if ρ is small, the honest finding is "the field's problem is bias, not variance", which Chouldechova et al. already argue |

**Four independent criteria (J1/J2/J3, J5, J7, J13) are each sufficient to reject.** The direction fails a conjunctive standard, not a marginal one.

---

# PART K — Five hostile reviewers

## Reviewer 1 — "This is just Success@N under another name."

**Strongest form.** "The authors propose to distinguish 'budget' from 'replication', but budget-conditional success is a named, quantified, and already-reportable metric: `Success@N`, i.e. `1−(1−p)^N`. Hofer, Debenedetti & Tramèr (2026) report exactly that on AgentDojo, alongside ASR, e.g. GPT-5 at ~5% ASR and 30% S@N. Chouldechova et al. (NeurIPS 2025) formalise the same quantity as `α_{Top1(K)}` and show it is a different estimand from one-shot. There is nothing left to name."

**Fatal?** **YES**, for the framing as presented. It is fatal because the candidate's contribution statement is a *conceptual* claim about estimands, and the concept is published.

**Minimum evidence to answer.** A quantity or mechanism *not* expressible as a Top-1-of-N transform — i.e. something that changes the *set* of compromised cases in a way not captured by `1−(1−p)^N`, with a reproduction recipe. **[INFER]** Only the adaptive-attacker *reallocation* mechanism is a candidate, and Deep et al. already exhibit it qualitatively.

## Reviewer 2 — "This is merely standard experimental design."

**Strongest form.** "Budget × sample size × replicates is a textbook factorial with a textbook analysis: beta-binomial for intraclass correlation, design effect `1+(K−1)ρ`, effective sample size, cluster bootstrap, McNemar with multiplicity control. Miller (2024) published all of the statistics for LLM evals; SafeBoundary-LLM published clustered resampling in this domain; Khan et al. published McNemar+Holm on AgentDojo. The paper is a routine application."

**Fatal?** **YES**, as a contribution claim — though not as a *valid* study. It would be competent and uninteresting.

**Minimum evidence to answer.** A *finding* that changes how practitioners design evaluations, not a *method*. **[INFER]** The only such finding available from the audited literature would be a case where the standard recipe yields a materially different conclusion from the published one *and* the discrepancy traces to a mechanism not already named.

## Reviewer 3 — "Khan et al. already did repeated AgentDojo evaluations."

**Strongest form.** "Computers 15(9):570 (Aug 2026) already ran AgentDojo banking twice per configuration across 14 model–defence configurations, with Wilson intervals, paired exact McNemar, Holm correction, utility, action availability, and operational cost — and already concluded that low event rates destroy power (0/288, 1/288 baselines). They also state the correlation problem verbatim and explain why they do not compute the correlation-aware interval. The proposed study is the same benchmark, the same conclusion, more runs."

**Fatal?** **PARTIALLY.** Not fatal to the *narrow* residual (they explicitly decline the correlation-aware interval, and two replications cannot identify ρ) — but fatal to the *framing*, because they occupy the "repeated agent-security evaluation with statistics" slot in a peer-reviewed venue.

**Minimum evidence to answer.** A demonstrated *consequence* of ρ large enough to change a published conclusion, plus a corrected-MDD table. **[INFER]** This is answerable but small: a value, not a mechanism.

## Reviewer 4 — "The observed effect is benchmark-specific and not scientifically general."

**Strongest form.** "ρ, break-time, and budget sensitivity are all properties of a specific environment's case-difficulty distribution and attack feasibility. Khan et al. warn explicitly that results are 'limited to the evaluated benchmark, models, defenses, and conditions'. AgentDojo banking has 144 cases with a goal-feasibility structure that produces 0/288 baselines on strong models; a dependence estimate from that cell generalises to almost nothing. Deep et al.'s rounds-based result comes from a bespoke single-target setup with a non-standard 'rounds' denominator."

**Fatal?** **YES** in practice. Even had the concept survived, a benchmark-specific number would not.

**Minimum evidence to answer.** The same recipe instantiated on ≥2 benchmarks *and* ≥2 model tiers, with portability of the *sign* of the effect, not the magnitude. **[INFER]** The candidate's two verified models (DeepSeek-V4.1-Flash, GLM-5.3-Flash) cannot supply the tier spread.

## Reviewer 5 — "You have only two or four models and cannot make broad claims."

**Strongest form.** "Two verifiable models remain after excluding Solar Mini 4 (~3 days old, no independent evaluation, aggregator-only specs), both non-Western Flash-tier, both with mandatory thinking modes, neither documenting a seed, and one (DeepSeek) whose default mode **ignores temperature**. That is not a platform for a general claim about security-evaluation methodology, and the vendor-documented absence of seed control undermines the reproducibility framing directly."

**Fatal?** **PARTIALLY, and it is redundant here.** For a *variance-ratio* estimand the capability-ladder objection does not apply (capability spread is a confound to avoid). But the *seed and temperature* situation does undercut any "we control stochasticity" claim — and, as this phase established, the honest response is to measure irreducible variance rather than claim to control it, which removes the remaining hook for a novelty claim.

**Minimum evidence to answer.** Vendor-documented seeds and a documented revision-pinning scheme; failing that, strict scoping plus a reported provider-side variance bound. **[INFER]** Neither converts the direction into a contribution.

---

# PART L — Final decision

# **NO-GO**

The direction's central proposition — that evaluation/attack budget changes the estimand while replication contracts uncertainty, and that this matters for defence conclusions in agent security — is **published**. It was killed by competitors, not by resource limits.

### L.1 Final research question

**None for this direction.** The candidate question — *"at fixed total cost, are attack budget and independent replication interchangeable, and does within-case dependence make the field's MDDs wrong?"* — is answered: **not interchangeable** (Chouldechova et al., formally; Hofer et al., empirically on agents), and the MDD correction is a published formula (Miller 2024) awaiting a number.

### L.2 Why it is or is not novel

**It is not novel.** [FACT] The estimand-incoherence claim is a NeurIPS 2025 position paper's central thesis, with a formal framework and a replication experiment. [FACT] Budget sensitivity of defence conclusions is demonstrated with 9 defences and >20,000 attacks. [FACT] The ASR-vs-budget-metric divergence is reported on AgentDojo. [FACT] Replication in agent security is practised and its basic limits reported. [FACT] The statistical machinery is published for LLM evals and cluster resampling is published in this journal family. What remains is quantification in a new benchmark.

### L.3 Closest competing paper

**Chouldechova, Cooper, Barocas, Palia, Vann & Wallach (2026),** *Comparison requires valid measurement: Rethinking attack success rate comparisons in AI red teaming*, **NeurIPS 2025** position paper, arXiv:2601.18076, all authors Microsoft Research. Secondary: **Deep et al. (2026)** arXiv:2604.23887 (budget sensitivity); **Hofer, Debenedetti & Tramèr (2026)** arXiv:2606.10525 (attack-side vs evaluation-side separation, ASR vs Success@N on AgentDojo).

### L.4 Exact difference from that paper

**[FACT]** Chouldechova et al. use **jailbreaking** as their running example and scope their repeated-sampling case study to **sampling from non-deterministic *decoding configurations*** (K resamples; temperature; 49 configurations × 49 samples). They do **not** run an **adaptive attacker with a query budget**, do **not** analyse **agent** benchmarks, do **not** run **defence comparisons**, and **explicitly set aside the reliability side**: *"we are primarily concerned with validity issues (bias and systematic mismeasurement) not simply reliability issues (sampling variation)."*

**[INFER]** So a genuinely different contribution from *this* paper exists in principle. But it is **not** the candidate direction, which sits on the reliability side the paper deprioritised, and which is already occupied by Miller 2024, Khan et al. 2026 and SafeBoundary-LLM 2026.

### L.5 Primary estimand — for the proposed replacement (see L.13)

`Δ_judge ≡ E_j[ ASR_judge(π_j) ] − E_j[ ASR_oracle(π_j) ]`, the *judge-induced bias* in a defence comparison at matched cases, and its interaction with defence identity. **[HYP]**

### L.6 Hypotheses — for the proposed replacement

- **[HYP] R1.** In LLM-judged agent benchmarks, a measurable fraction of the reported defence effect is attributable to *differential judge error* rather than to differential resistance.
- **[HYP] R2.** The bias is *defence-dependent* in sign as well as magnitude, so it can reverse a defence ordering, not merely shift it.
- **[HYP] R3.** Deterministic environment-state oracles (e.g. AgentDojo) are immune by construction, and the bias concentrates in benchmarks using LLM-as-judge — which Li et al. (2026) report is the dominant paradigm among agent-safety benchmarks.
- **[HYP] R4.** Reporting judge TPR/FPR *disaggregated by defence* (Chouldechova et al.'s recommendation 4) is sufficient to predict which comparisons are at risk.

### L.7–L.10 Minimal pilot, data, analysis, falsification — conditional

**Not specified.** Specifying these would require the fresh primary-source elimination that this direction received and the replacement has not. Per the phase instruction, that audit comes before design.

### L.11 Biggest remaining risk

**[INFER]** That the replacement direction is *also* occupied. Chouldechova et al. §5 provides the theory of differential judge error; Pathade et al. flag the mechanism (*"defenses change the distribution of trajectories… so an uncalibrated judge's error rate is not constant"*); Li et al. cite Colosseum (Nakamura et al. 2026) finding LLM-as-judge insufficient for collusion detection; and REDAgentBench (arXiv:2608.10669) already shows execution-based evaluation materially changes reported outcomes. **The isolation of judge error as the *mechanism* for agent-defence conclusions may already exist, and REDAgentBench is the most likely place to find it.** This must be checked before any design.

### L.12 What would make me abandon the project entirely

- **[INFER]** If REDAgentBench (or any located paper) already isolates judge error as the mechanism for a changed agent-security outcome by oracle-swap at matched cases, then the replacement is occupied too, and **no direction in this space currently survives**. In that case the honest conclusion is that this research programme's novelty window has closed.
- Also abandon if the candidate space is judged to require frontier-model access the project does not have: Chouldechova et al., Deep et al., Hofer et al. and Khan et al. all used GPT-5/5.4-family, Claude 4.5/4.6, and Gemini 2.5/3. The audited literature's decisive results were obtained with **frontier** models; two Flash-tier models may be insufficient to enter the conversation at all.

### L.13 Proposed next strongest direction

**[HYP/OPEN]** *"Differential judge error as a confound in LLM-agent security defence evaluation: measuring how much of a reported defence effect is an artefact of the oracle."*

Reasoning: it targets **validity**, which Chouldechova et al. designate the primary concern and which the reliability side cannot address; it is **not** solved by Miller's framework; it is **causal and falsifiable** (oracle-swap at matched cases, paired, with the judge blinded to condition); it has a **cost profile** compatible with limited resources; and the agent setting makes it sharper than jailbreaking because agent trajectories differ *structurally* between defended and undefended conditions (refusals, hedges, truncation, tool-retry loops) — which is exactly the condition under which differential judge error is not constant.

**Status: not audited.** This direction has had none of the elimination effort applied in this phase and should be assumed occupied until checked.

---

# PART M — Source registry

`sources.csv` updated: **R01–R76**, validated (74 → 77 rows, 11 fields each, no malformed records). New and upgraded entries in the appendix below.

## Appendix — registry changes in this phase

| id | Change |
|---|---|
| **R74** | **NEW** — Chouldechova, Cooper, Barocas, Palia, Vann & Wallach, *Comparison requires valid measurement: Rethinking attack success rate comparisons in AI red teaming*, **NeurIPS 2025 position paper**, arXiv:2601.18076. **Label A** (full HTML read). **THE DECISIVE SOURCE FOR THE NO-GO.** |
| **R75** | **NEW** — Deep, Emmons, Fox, Bacon, McAllister, Ortiz & Flautner, *Evaluation of Prompt Injection Defenses in Large Language Models*, arXiv:2604.23887. **Label A** (full HTML v2 read). Varies adaptive attack budget across 9 defences; 20,000+ attacks. |
| **R76** | **NEW** — Deniz, Boshmaf & Khalil, *SSP-Bench*, arXiv:2609.25352. **Label A** (full HTML read). Separates item sampling from deterministic evaluation; rank stability across pipeline regenerations. |
| **R68** | Upgraded **C → A**. MDPI *Computers* 15(7):460, SafeBoundary-LLM. Read via browser. **Contains published cluster bootstrap in LLM safety evaluation**, with the clustering rationale stated. |
| **R66** | Marked **UNREAD / inaccessible** — OpenReview browser-verification challenge blocks both fetch and interactive access. Downgraded in confidence; not leaned on. |
| **R29** | Re-read **A**. IETF `draft-han-bmwg-agent-security-benchmark-00`: 55 pass-rate metrics, **no uncertainty protocol, no repetition count, no budget specification**. |

---

# Final recommendation

# **Abandon this direction.**

Not "search one more time" — the elimination was executed, and it succeeded. Four independent papers each independently destroy a component of the candidate:

1. **Chouldechova et al. (NeurIPS 2025)** destroy the conceptual claim and demonstrate the estimand divergence.
2. **Deep et al. (2026)** destroy the empirical claim for defences, with a verbatim methodological warning.
3. **Hofer et al. (2026)** destroy the agent-specific novelty by reporting ASR and Success@N side by side on AgentDojo.
4. **Miller (2024)** plus **Khan et al. (2026)** plus **SafeBoundary-LLM (2026)** destroy the statistical residual as either published method or declined-and-bounded empirical gap.

The candidate direction is now a **replication-plus-quantification** study. Under this phase's standard, it should be killed rather than dressed up.

**One caveat worth recording honestly. [INFER]** The programme is not obviously out of ideas — but it may be out of *frontier access*. Every decisive result in the audited literature was produced with GPT-5/5.4-family, Claude 4.5/4.6, or Gemini 2.5/3 models. The project's verified inventory is two Flash-tier models, one of which ignores temperature in its default mode and neither of which documents a seed. Before a third direction is audited, the resource question should be answered, because it constrains which questions are answerable irrespective of novelty.

**Next action, if the user wishes to continue:** audit the **differential-judge-error** direction (L.13), beginning with REDAgentBench (arXiv:2608.10669), which is the most likely existing occupant. Do not begin design.
