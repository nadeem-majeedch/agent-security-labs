# Phase 7 — Judge Validity / Evaluator Bias Novelty Audit
## Direction under audit: does the security evaluator itself distort measured defense effectiveness in LLM-agent security evaluation?

**Date:** 2026-09-25
**Task:** attempt to destroy the final candidate research direction before any experimental design.
**Verdict:** **NO-GO.** The phenomenon is established with effect sizes; the agent-specific instance has already been measured on fixed rollouts with human ground truth and ranking inversions; the theoretical account exists; and the space has been systematised by a 2026 SoK. Recommendation: **Abandon this research direction.**

### Claim-type legend

| Tag | Meaning |
|---|---|
| **[FACT]** | Established at a primary source; verifiable from the cited document |
| **[INFER]** | My inference from established facts; not asserted by the cited source |
| **[HYP]** | Proposed hypothesis; established by nobody |
| **[OPEN]** | Genuinely unresolved as of this audit |
| **[A]** | Fetched and read at source | **[B]** | Read only via another paper's summary |
| **[C]** | Not verified |

No fabricated citations, results, URLs, DOIs, or numbers appear in this document. Sources read only through another paper's summary are labelled **[B]** and are not leaned on for the verdict.

---

# PART A — Defining the evaluator problem

## A.1 Pipeline components

| # | Component | Function | Where error enters |
|---|---|---|---|
| 1 | **Attack generator** | Produces the adversarial artifact (injection, template, optimized suffix) | Generates an artifact that is *unrealizable* or mislabeled |
| 2 | **Target agent** | The scaffolding (harness) that mediates tools and turns | Harness differs from the one used to build the case |
| 3 | **Target model** | The LLM that reasons | Sampling nondeterminism; capability ceiling |
| 4 | **Defense** | Any intervention between attack and harm | Changes *what exists to be judged* |
| 5 | **Security evaluator** | Maps evidence to a security label | The subject of this audit |
| 6 | **LLM-as-a-judge** | An LLM applied as the evaluator | Style, length, position, self-preference, prompt injection, rubric drift |
| 7 | **Rule-based evaluator** | Regex / string / schema match | Over- and under-matching; misses paraphrase; catches hallucinated strings |
| 8 | **Human evaluator** | Expert adjudication | Cost, subjectivity, disagreement |
| 9 | **Reference-based evaluator** | Compares to a known-good target | Requires a known target; brittle to legitimate variation |
| 10 | **Outcome-based evaluator** | Judges the end result | Can miss harmful intermediate steps |
| 11 | **Tool-use-based evaluator** | Judges the calls made | Cannot see effects not expressed in calls |
| 12 | **Trajectory evaluator** | Judges the message/tool-call record | Misses durable effects with no recorded evidence |
| 13 | **Final-answer evaluator** | Judges only the text output | Blind to actions entirely |

## A.2 Where the judge enters — and the four-stage decomposition

**[FACT]** REDAgentBench (arXiv:2608.10669) **[A]** formalises the pipeline explicitly and is the authoritative framing:

> *"reported ASR emerges through four stages: **exposure** determines whether an intervention reaches the agent; **execution** captures what the agent actually does in the environment; **observation** determines which trajectory or state evidence is available; and **adjudication** maps that evidence to a label."*

and:

> *"existing evaluations often reduce agent safety to a single attack success rate (ASR), **collapsing exposure, execution, observation, and adjudication and potentially conflating actual violations with evidence visibility**."*

Their formalisation: for execution configuration `s` (model, harness, evaluation cue) and valid-rollout set `Ω`,

```
ASR_Ω(s; c, b) = (1/|Ω|) Σ_{i∈Ω} Y_i(c, b)
```

where `c = (v, p, g)` is the **view-specific judging configuration** (evidence view `v`, proof contract `p`, deterministic gate `g`) and `b` is the judge backbone. Replacing `Y_i(c,b)` with the state-grounded outcome `E_i(s)` yields **execution ASR**.

**[INFER]** The candidate's proposed decomposition (`Observed Defense Effect = genuine effect + evaluator effect + interaction`) is therefore not new as a decomposition: REDAgentBench already separates *execution* from *observation* from *adjudication*, and Chouldechova et al. already separate the estimand from its measurement. What remains distinct in the candidate is only the **defense factor crossed with the evaluator factor** — see Part D.

## A.3 Terms kept strictly separate

| Term | Definition used here |
|---|---|
| **Measurement error** | Deviation of an estimate from its target estimand; includes bias and variance |
| **Evaluator bias** | Systematic error with non-zero expectation; may be constant (offset) or differential (interaction) |
| **Evaluator variance** | Dispersion of labels across repeated identical evaluations |
| **Evaluator inconsistency** | Variance across *equivalent* inputs (paraphrase, order, formatting) |
| **Evaluator susceptibility** | Degree to which a judge's label can be moved by evidence-surface manipulation |
| **Evaluator prompt injection** | Attackers place instructions intended to steer the *judge* itself |
| **Evaluator contamination** | Judge's training data includes the benchmark items |
| **Evaluator leakage** | Information about the intended label reaches the judge through the pipeline |
| **Calibration error** | Mismatch between stated/aggregate confidence and realised accuracy |
| **False positive (security)** | Judge labels a harmless trajectory as a violation |
| **False negative (security)** | Judge labels a violation as harmless |
| **Systematic defense-dependent error** | The judge's error *distribution* differs between defended and undefended conditions — the differential case, which is the only one that can reverse a ranking |

**[FACT]** The last of these has an exact analytic form, from Chouldechova et al. (NeurIPS 2025, arXiv:2601.18076) **[A]**, §5: for a judge `J` with true/false-positive rates `TPR(J;s)`, `FPR(J;s)` with respect to the oracle `s`,

```
E(ASR) = TPR(J;s)·α + FPR(J;s)·(1 − α)
```

so if `α_A = α_B` but the judge's TPR/FPR differ across systems, `E(ASR_A) ≠ E(ASR_B)`. They state explicitly: *"it is insufficient for judges to have equal overall accuracy (e.g., equal accuracy or AUC) across target systems."*

**[INFER]** That equation *is* the candidate's proposed decomposition, written for one-shot ASR, with the interaction term being the differential-error term. It is a published theoretical result.

---

# PART B — Literature search

Fresh primary-source searches were run across the Part B term list and adjacent fields. The load-bearing discoveries are tabulated below. A full per-source evaluator matrix is in `research/tables/judge-validity-matrix.csv`; the general registry update is in `sources.csv` (now R01–R90).

| Search target | Outcome |
|---|---|
| LLM-as-judge security / reliability | **HIT:** a dedicated 2026 SoK (R79) |
| Judge prompt injection / judge adversarial manipulation | **HIT, extensively:** JudgeDeceiver (CCS 2024), BadJudge (2025), rubric-induced preference drift (2026), Emoji Attack (2024), master-key attack (2025), PAIR-based judge attacks (2025), universal adversarial assessment attacks (EMNLP 2024) |
| Style/format sensitivity of judges | **HIT:** Know Thy Judge (R78) — up to **0.24 FNR jump** from output style alone |
| Agent trajectories judged rather than text | **HIT:** REDAgentBench (R77) |
| Evaluator effect on agent-security conclusions | **HIT:** REDAgentBench §4.3 — fixed-rollout judging-view audit with ranking inversions |
| Human-vs-LLM agreement on agent security | **HIT (partial):** REDAgentBench human audit (κ = 0.838) |
| Human ground-truth agent-security datasets at scale | **Only partial** — see Part G |
| Defense-dependent judge error | **NOT found as a named, isolated experiment** — see Part D |

---

# PART C — The mandatory papers

## C.1 REDAgentBench — arXiv:2608.10669 **[A]**

Chen, Liu, Zhu, Dou, Jiang, Li, Guo, Chen & Zhang (Fudan, HKUST, Qwen DianJin/Alibaba Cloud, Soochow). Submitted 2026-08-11.

| Item | Extraction |
|---|---|
| Research question | Can red-teaming and *faithful measurement* of tool-using agents be made executable and evidence-grounded? |
| Evaluation target | Six closed models through three agent harnesses |
| Evaluator type | **Three view-specific evaluators sharing one judge backbone**: Trajectory, State, Hybrid |
| Evaluator model | **Qwen3.7-plus** (backbone held fixed across views) |
| Evaluator input | Trajectory: messages + tool calls. State: sandbox receipts + final-state changes. Hybrid: both, with alignment and discrepancy resolution |
| Evaluator output | Binary harmful/not-harmful label `Y_i(c,b)`; separate recognition label `R` |
| Human ground truth | **Yes** — stratified sample of **360 valid GPT-5.2 rollouts**, two blinded reviewers, third adjudicates |
| Number of evaluators | 3 view-specific, 1 backbone; plus 2–3 humans |
| Judge agreement | **91.94%** agreement pre-adjudication, **κ = 0.838** |
| False positives / negatives | Judge audit: **precision 97.84%** (95% CI 96.00–99.28), **recall 91.27%** (88.58–93.80), accuracy 93.62% (91.57–95.44). Raw judged ASR **55.43%** vs human-audited estimate **59.42%** |
| Calibration | Not reported as such |
| Evaluator attacks | Not the focus |
| Evaluator prompt injection | Not the focus |
| Evaluator robustness | **Central** — §4.3 fixed-rollout judging-configuration audit |
| Defense comparison | **Yes** — §4.6 paired re-measurement of a policy reminder |
| Do evaluator effects change security conclusions? | **Yes, explicitly** — ranking inversions |
| Are evaluator effects isolated experimentally? | **Yes, this is the paper's methodological core** |
| Limitations | Single diagnostic cohort (Qwen-plus) for state-grounded analysis; replays do not estimate full-benchmark ASR |
| Stated future work | Broader model/harness coverage |

## C.2 Chouldechova, Cooper, Barocas, Palia, Vann & Wallach — NeurIPS 2025, arXiv:2601.18076 **[A]** — see Part L.

## C.3 Pathade, Pawar & Patil — arXiv:2609.25173 **[A]**

Read in full in earlier phases. Relevant here: their **A2 (Success Oracle)** axis argues four oracle families (string/regex, LLM judge, environment state, human) *"disagree in both directions"*; that LLM judges add sensitivity to judge model, prompt, and trajectory length; and:

> *"Judge-based ASR is a measurement taken through an instrument whose calibration is seldom reported; we find that **29.7% of judge-using papers report agreement with human labels**."*
> *"**Defenses change the distribution of trajectories — more refusals, more hedging, more truncation — so an uncalibrated judge's error rate is not constant across the systems being compared. That is precisely the condition under which ranking fails to be preserved.**"*

**[INFER]** This is the candidate's hypothesis, stated as a diagnosis, in a paper already catalogued. Pathade et al. do not run the experiment, but they name the exact mechanism and the exact reason it matters.

## C.4 Know Thy Judge — arXiv:2503.04474 **[A]**

Eiras, Zemour, Lin & Mugunthan. ICBINB Workshop at ICLR'25. Submitted 2025-03-06.

| Item | Extraction |
|---|---|
| Research question | *"can we trust the evaluations of these evaluators?"* — robustness meta-evaluation of LLM safety judges |
| Evaluation target | Commonly used safety judges |
| Evaluator type | LLM-as-a-judge (safety moderators) |
| Evaluator model | Multiple commonly used safety judges (specific set not captured in the abstract) |
| Evaluator input | Model generations under harmful prompts |
| Human ground truth | Yes, per "same dataset" comparisons |
| Judge agreement | Not captured at abstract level |
| **False negatives** | ***"small changes such as the style of the model output can lead to jumps of up to 0.24 in the false negative rate on the same dataset"*** |
| **Evaluator attacks** | **Yes** — *"adversarial attacks on the model generation can fool some judges into misclassifying **100% of harmful generations as safe ones**"*** |
| Calibration | Not captured |
| Robustness | Central |
| Defense comparison | **No** |
| Changes security conclusions? | **Yes, and stated:** *"low attack success under certain judges could create a false sense of security"* |
| Isolated experimentally? | **Yes** — style manipulation at fixed dataset; adversarial generation |
| Limitations | Workshop paper; safety-judge framing rather than agent trajectories; full text not read in this phase |

## C.5 Any primary paper demonstrating adversarial manipulation of judges **[B]**

Via the SoK (R79), with quantitative results reported. These are **[B]** — read only through the SoK's summary, not at source:

| Attack | Judge models | Reported effect |
|---|---|---|
| JudgeDeceiver — optimization-based prompt injection (Shi et al., **ACM CCS 2024**) | Open-source and proprietary | Very high ASR; known-answer and perplexity defences miss ≥70% |
| BadJudge — backdoor poisoning (Tong et al., 2025) | Mistral-7B-Instruct, Qwen1.5-7B-Chat, LLaMA-3-8B-Instruct | 1% poisoned data inflates scores up to 3× (1.4→4.6/5); backdoored guardrails misclassify toxic content as safe **83.9%** |
| Universal adversarial assessment (Raina et al., **EMNLP 2024**) | FlanT5-xl, Mistral-7B, Llama2-7B, GPT-3.5 | ASR ≈70% score inflation on SummEval and TopicalChat |
| Emoji Attack (Wei et al., 2024) | Llama Guard, ShieldLM, WildGuard, GPT-3.5/4, Gemini, Claude, DeepSeek, o3-mini | ShieldLM detection **71.9% → 3.5%** |
| Master-key attack on reward models (Zhao et al., 2025) | GPT-4o, Claude-4, GPT-o1, Qwen-2.5-72B, LLaMA-3-70B | **FPR up to 80%** across 10 keys and 5 benchmarks |
| Prompt injection on judges (Maloyan & Namiot, 2025) | Gemma-3-27B/4B-Instruct, Llama-3.2-3B, GPT-4, Claude-3-Opus | Max ASR **73.8%** |
| 15-attack robustness assessment (Li et al., 2025) | GPT-4o, JudgeLM-13B, OpenChat-3.5 | PAIR + Combined ≈70% ASR on GPT-4o; robustness varies up to **40%** across prompt templates |
| Rubric-Induced Preference Drift (Ding et al., 2026) | Qwen3-14B, Gemma-3-27B-it, DeepSeek-V3 | Accuracy ↓9.5% helpfulness, ↓27.9% harmlessness while benchmark agreement stays ≈0.85; **invisible to human review** |

## C.6 Judges on agent trajectories rather than ordinary text

**[FACT]** REDAgentBench (C.1) is exactly this, and it is the only such work located. **[FACT]** R-Judge (Yuan et al., Findings of EMNLP 2024) is a *dataset* of agent interaction records with human safety-risk annotations — it evaluates whether an LLM can recognise risk in agent records, i.e. it is adjacent but concerns risk *awareness*, not adjudication of defense effects.

---

# PART D — Has the field already tested defense-dependent judge error?

## D.1 The exact question

Systems A (undefended) and B (defended), same automated evaluator. Does the defense itself change the evaluator's probability of assigning SUCCESS/FAILURE/SAFE/UNSAFE/ATTACKED/NOT ATTACKED, independently of the underlying security state?

## D.2 Answer: **YES for the general phenomenon; NO for the defense factor specifically.**

### Established: evaluator-side error that changes security conclusions, at fixed underlying behaviour

| Source | Design | Result |
|---|---|---|
| **Know Thy Judge** (2025) **[A]** | Same dataset, same ground truth; vary the **style** of the model output | FNR moves by up to **0.24**; adversarial attacks on the *generation* fool some judges into calling **100%** of harmful generations safe; the authors conclude low ASR under some judges *"could create a false sense of security"* |
| **REDAgentBench** (2026) **[A]** | **Fixed rollout**, judge backbone fixed to Qwen3.7-plus, vary the *complete view-specific judging configuration* | State view reports **7.73–11.72 pp higher ASR** than trajectory view for **every** model; **12.97–21.20% of paired labels change**; **43 strict pairwise reversals across 23 of 64 slices**; all six paired differences significant (**exact McNemar p ≤ 6.54×10⁻⁵**) |
| **Chouldechova et al.** (2025) **[A]** | Analytic; differential judge TPR/FPR | `E(ASR) = TPR·α + FPR·(1−α)`; **equal overall accuracy is insufficient**; inversion condition derived |
| **Pathade et al.** (2026) **[A]** | Meta-analysis + analytic | *"Defenses change the distribution of trajectories… so an uncalibrated judge's error rate is not constant across the systems being compared"* |

**[FACT]** REDAgentBench also documents the **mechanism** by which the evaluator's evidence view fails, including the one that most closely resembles a defense artifact:

> *"Durable workspace changes often lacked a verifiable write event in the trajectory; in several multi-turn cases, **the agent even refused only after the harmful write had occurred**. Conversely, receipts often omitted the authorization or payload context needed to interpret a recorded action. Finally, attempted and realized effects could diverge, as when an agent reported sending an attachment that the sent-message receipt did not contain."*

and, from their motivating example: *"a trajectory-view may suggest safety, while the state-view confirms harm."*

**[INFER] That is the candidate's H2 in a stronger form than the candidate proposed**: a *system* can look safe or unsafe *purely as a function of the evaluator's evidence view*, at fixed rollout, with the reversal verified against human labels and significant under a paired test.

### Not established: the defense factor crossed with the evaluator factor

**[OPEN]** The specific cell that remains unoccupied: REDAgentBench's fixed-rollout judging-view audit (§4.3) contains **no defense factor**. Their defense experiment (§4.6, the training-free policy reminder) is measured **exclusively with state-grounded outcomes** — deliberately avoiding the judged path:

> *"we replay known harmful cases with a self-reminder, a case-specific policy reminder, or neutral text… they nevertheless connect receipt-grounded diagnosis to a defense verified by paired re-execution."*

with results on the confirmatory 510-case Qwen-plus cohort: policy reminder reduces ASR by **74.19 points** (95% source-case cluster CI **[69.85, 78.41]**), preventing 368 of 434 baseline harmful executions, against 85.51% / 88.59% / 85.19% for neutral controls.

**[OPEN]** Also unoccupied: REDAgentBench holds the **judge backbone fixed**. Judge *model* or *version* variation with a defense factor is not tested there.

**[INFER]** So the surviving cell is: **is there a defense × evaluator-view (or defense × judge-model) interaction, over and above the evaluator-view main effect and the defense main effect?**

## D.3 Assessment of that residual

**[INFER]** The residual is real but is a *factorial extension* of an existing design — run REDAgentBench's §4.3 audit with a defense factor added. Under this project's stated standard, a factorial extension of a published audit, whose main effect is already quantified and whose theoretical form is already written down, is a replication-plus-extension, not a discovery. See Part N.

---

# PART E — Validity versus reliability

**[FACT]** Chouldechova et al. draw the distinction explicitly: *"we are primarily concerned with **validity issues (bias and systematic mismeasurement) not simply reliability issues (sampling variation)**."*

- **Validity:** does the evaluator measure the intended security property?
- **Reliability:** would the evaluator give the same answer under repeated evaluation?

**[INFER]** The candidate direction is **primarily validity (type A)**, with a reliability tail. That is the *right* side of Chouldechova's line — which is precisely why the space is crowded: the validity side is where Chouldechova, Pathade, REDAgentBench, Know Thy Judge and the SoK all live.

## E.1 Mapping

| Problem | Validity | Reliability | Already studied? | Closest source |
|---|---|---|---|---|
| Judge randomness | ○ | ● | **Yes** | Chouldechova 2025 §4 (repeated sampling); R73 Miller 2024 |
| Judge disagreement | ◐ | ● | **Yes** | SoK R79 taxonomy; REDAgentBench (3 views) |
| Judge calibration | ● | ○ | **Yes (theory); rarely measured in practice** | Chouldechova §5; Pathade A2 (29.7% report calibration) |
| Judge prompt injection | ● | ○ | **Yes, extensively** | JudgeDeceiver (CCS 2024); Maloyan & Namiot 2025; SoK §5.1.2 |
| Evaluator adversarial attack | ● | ○ | **Yes** | Know Thy Judge; Raina et al. EMNLP 2024; BadJudge; Emoji Attack; master-key |
| **Defense-dependent judge bias** | ● | ○ | **Partially** — mechanism + analytic form established; **defense factor not crossed with evaluator factor** | Chouldechova §5 (theory); Pathade A2 (mechanism); REDAgentBench §4.3 (view, no defense) |
| Human-vs-LLM disagreement (agent) | ● | ● | **Yes, at moderate scale** | REDAgentBench (360 rollouts, κ=0.838) |
| Trajectory-vs-final-answer evaluation | ● | ○ | **Yes** | REDAgentBench §4.3; LITMUS (Zhang et al. 2026a) |
| Outcome definition | ● | ○ | **Yes** | REDAgentBench four-stage pipeline; Chouldechova §4 |
| Metric definition | ● | ○ | **Yes** | Pathade six axes; Chouldechova estimand framework |
| Threshold selection | ● | ○ | **Partially** | Binary pass/fail noted by Li et al. 2026 (79% of safety benchmarks) |
| Judge model choice | ◐ | ◐ | **Yes (general); not with a defense factor in agent security** | SoK R79; REDAgentBench holds backbone fixed |

**Legend:** ● primary concern, ◐ secondary, ○ not the focus.

---

# PART F — The "defense effect" test

The candidate's proposed experiment: take the **same underlying attack trajectory**, present it under different surface conditions (raw / undefended / defended / added refusal language / restyled), and test whether the evaluator changes its judgment despite equivalent underlying security behaviour.

## F.1 Has this been done? — **Yes, in two forms.**

1. **[FACT]** **Style condition, at fixed ground truth** — Know Thy Judge: *"small changes such as the style of the model output can lead to jumps of up to 0.24 in the false negative rate on the same dataset."* Same dataset, same labels, only surface changed. Requirement met.
2. **[FACT]** **Evidence-view condition, at fixed rollout, on agents** — REDAgentBench §4.3: *"We hold each rollout and the Qwen3.7-plus judge backbone fixed while varying the complete view-specific configuration—evidence, proof contract, and deterministic gates."* Labels change on 12.97–21.20% of paired cases; 43 ranking inversions; McNemar p ≤ 6.54×10⁻⁵; verified against two blinded human reviewers (κ = 0.838). Requirement met, on agents, with human ground truth.

## F.2 What has NOT been done

**[OPEN]** The **defense-manipulation** variant specifically: take a trajectory produced *under a defense*, and establish that the defense's *observable artifact* (refusal phrasing, disclaimer, hedging, truncation, extra tool calls, reordered reasoning) shifts the judge's label at fixed *executed* outcome. This is a surface condition that is *induced by a defense* rather than authored.

**[INFER] But this is the same experiment as Know Thy Judge's style condition, with the style sourced from a defense instead of an adversary.** The mechanism is identical; only the provenance of the perturbation differs. The scientifically interesting question (does surface perturb judge labels enough to change conclusions?) is answered. The remaining question (does *this particular* surface perturbation, arising from *this particular* defense, do so?) is a per-instance measurement, not a mechanism.

## F.3 If untested, would it be a genuine contribution or a sanity check?

**[INFER]** Given F.1, it would be a **sanity check with a dataset attached** — closer to establishing that a known phenomenon occurs in one more setting than to discovering anything. Under Part N's rules it is at best contribution type **A (new empirical phenomenon)** and the phenomenon is not new.

---

# PART G — Human ground truth

**[FACT]** Human-adjudicated agent-security evaluation data **already exists at moderate scale**:

- **REDAgentBench [A]:** two security experts reviewed **480 sampled case versions** across three development rounds for IVC consistency, threat-model compliance, task–attack coherence, and verifier correctness; then independently audited a stratified sample of **320 frozen cases** under blinded conditions. Separately, a stratified sample of **360 valid GPT-5.2 rollouts** was labelled independently by two blinded reviewers with a third adjudicating, reporting **91.94% agreement, κ = 0.838**, precision 97.84%, recall 91.27%, and a human-audited ASR estimate (59.42%) against the raw judged value (55.43%). Disagreement statistics: Cohen's κ.
- **R-Judge** (Yuan et al., Findings of EMNLP 2024) **[B]** — 569 records across 27 risk scenarios with human risk annotations; evaluates risk *recognition*, not defense adjudication.
- **Know Thy Judge [A]** — uses human-labelled safety datasets as ground truth.
- **Khan et al. 2026 [A]** — two evaluators R1/R2, 12,194 responses on the local-model side (via MDPI *Computers* 15(7):460, SafeBoundary-LLM).

**[INFER]** Would building a small human-adjudicated agent-security evaluation set be novel? **No.** Redundant with REDAgentBench's blinded audit, and a dataset is not a contribution by this project's own standard. Building a *larger* one is an engineering contribution to an existing artefact, not a research finding.

---

# PART H — Judge ensembles

**[FACT]** Already standard practice in the located literature:

- REDAgentBench uses **three** view-specific evaluators over one backbone, and treats the **hybrid** judge as the reconciled reference.
- The SoK (R79) catalogues ensembles as an established technique: Abeyratne et al. (2025) "unsupervised ensemble method" (Law domain); Zhou et al. (2025) "**LLM-as-Ensemble-Judge**" metric; and Detection/Defence works including Li et al. (2025) [24] on *judgment detection*.
- **[B]** Li et al. (2025) robustness work across 15 attacks uses multiple judge models as controls.

**[INFER]** Using multiple judges is **(a)** already done, **(b)** already named as a metric variant, and **(c)** a mitigation whose limitations are already documented (Chouldechova et al.: equal accuracy is insufficient; only *differential* TPR/FPR matters). Recommending an ensemble would be recommending a known mitigation. **Not a contribution.**

---

# PART I — The candidate research questions

## I.1 *"How much can evaluator/judge behavior alter measured security-defense effectiveness in LLM-agent security evaluation?"*

**Status: (2)–(3) — partially answered to substantially answered, with one open cell.**

- The magnitude of *evaluator-view* effects on agent-security measurement is **quantified**: 7.73–11.72 pp on ASR, 12.97–21.20% of labels flipped, 43 ranking inversions, McNemar p ≤ 6.54×10⁻⁵ (REDAgentBench §4.3).
- The magnitude of *style* effects on safety judges is **quantified**: up to 0.24 FNR (Know Thy Judge).
- The *defense-specific* magnitude is **not** measured — but the defense experiment in REDAgentBench is measured with a state oracle, so a judge-vs-oracle gap for that defense is inferrable from their own tables and is a small extension.

**[INFER] Verdict: not a viable standalone research question.** The "how much" for the general phenomenon is answered; the defense-specific "how much" is a recomputation.

## I.2 *"Can an AI-agent security defense appear more effective because it changes the evaluator's observable evidence rather than because it prevents the underlying attack?"*

**Status: the mechanism is answered; the defense-conditioned instance is not.**

- **Closest paper:** REDAgentBench (arXiv:2608.10669).
- **Exact overlap:** REDAgentBench already establishes that a *system* can appear safe under one evidence view and harmful under another *at fixed rollout* — their Figure 1 caption: *"the agent recognizes the constraint and claims that it will not perform the merge (R=1), yet still executes the harmful action (E=1). Consequently, **a trajectory-view may suggest safety, while the state-view confirms harm**."* They also show the converse mechanism: *"the agent even refused only after the harmful write had occurred."* A refusal-shaped artifact that the judge reads as safety, while the state oracle reads harm, **is the candidate's H2 already demonstrated**.
- **Exact remaining gap:** no **defense factor** in the view audit; judge backbone held fixed.
- **Why "not tested exactly this way" ≠ novelty here:** the mechanism, the direction, the approximate magnitude, the reversal phenomenon, the human ground truth, and the theoretical form all exist. Only the factorial crossing is missing.

---

# PART J — The identification problem

## J.1 Is it an identification problem? — **Yes.**

**[INFER]** Given only `Defense A → lower measured ASR`, the two hypotheses

- **H1:** A genuinely reduces attacks, versus
- **H2:** A leaves the security-relevant behaviour largely unchanged but makes the evaluator less likely to label it an attack

are **not** identified without an instrument for the underlying security state. The observed difference is `Δ_measured = Δ_true + Δ_evaluator + interaction`, and the last two terms are unobserved by construction. This is exactly the structure Chouldechova et al. formalise.

## J.2 What additional evidence would identify it — and which is already used

| Instrument | Already used? | Where |
|---|---|---|
| **Independent rule-based checks** | **Yes** | REDAgentBench "rule-first judging": deterministic verifiers read consequential fields from receipts or state transitions; the LLM judge is consulted only for semantically defined constraints |
| **Tool-call evidence** | **Yes, and shown insufficient alone** | REDAgentBench Trajectory Judge — *"a transcript alone therefore systematically misses durable prohibited effects"* |
| **State changes / external side effects** | **Yes — the strongest available instrument** | REDAgentBench State Judge; service receipts and final-state diffs, "independently of the agent's self-reported completion or refusal" |
| **Human adjudication** | **Yes** | REDAgentBench 360-rollout blinded audit |
| **Multiple independent judges** | **Yes** | REDAgentBench 3 views; SoK ensembles |
| **Evaluator swap** | **Yes (as evidence view), no (as judge model)** | REDAgentBench holds the backbone fixed |
| **Trajectory-level invariants** | **Yes, partially** | REDAgentBench proof contracts |
| **Evaluator-blind labels** | **Yes** | REDAgentBench's state oracle is constructed to be independent of agent claims |
| **Adversarial evaluator testing** | **Yes** | Know Thy Judge; JudgeDeceiver; BadJudge; RIPD |

**[INFER] Conclusion: the identification problem has a known solution (a state-grounded oracle), it has been implemented at scale, and it has been used to re-measure a defense.** The instrument the candidate would build is the instrument REDAgentBench already is.

---

# PART K — REDAgentBench deep audit

## K.1 WHAT REDAgentBench DOES

1. **Builds an executable benchmark**: 1,661 cases across **15 intervention strategies, 11 vulnerability types, 28 constraints, 5 service surfaces**, generated by an autonomous pipeline fed by 12,181 source-linked attack mappings consolidated from prior agent-safety studies. Expert review: 480 sampled case versions over three rounds; 320 frozen cases independently audited blinded.
2. **Treats the environment as a measurement instrument** and formalises reported ASR as **exposure → execution → observation → adjudication**.
3. **Runs everything in instrumented sandboxes** over five service surfaces (workspace, email, browser, banking, external files), recording structured **service receipts** and baseline-to-final **state differences**.
4. **Separates execution from adjudication by construction**: execution outcome `E` is determined by policy-specific deterministic verifiers where possible; a state-grounded ledger for Qwen-plus gives 1,014/1,661 (Codex, 61.1%), 1,162/1,661 (Hermes, 69.9%), 1,001/1,502 (OpenClaw, 66.6%).
5. **Implements an explicit evaluator-validity audit**: three view-specific evaluators (Trajectory / State / Hybrid) over a **fixed judge backbone**, with proof contracts and deterministic gates; the fixed-rollout design isolates the judging configuration.
6. **Quantifies evaluator effects on conclusions**: 7.73–11.72 pp ASR shift, 12.97–21.20% label changes, **43 ranking inversions across 23 of 64 slices**, all six paired differences significant under **exact McNemar (p ≤ 6.54×10⁻⁵)**; local comparisons change, global ranking stable.
7. **Validates the judge against humans**: 360 stratified GPT-5.2 rollouts, two blinded reviewers plus adjudicator, κ = 0.838, precision 97.84%, recall 91.27%, accuracy 93.62%; raw judged ASR 55.43% vs human-audited 59.42%.
8. **Tests harness effects** and shows model rankings are not stable across harnesses: Qwen-plus on E5 goes 40.62% (OpenClaw) → 91.92% (Codex) → 95.00% (Hermes); the highest-ASR model differs by harness. The 8.8-point Hermes–Codex gap in the state-grounded ledger "cannot be attributed to a model change."
9. **Tests evaluation-context disclosure as an experimental variable**: disclosure of a mocked authorized evaluation lowers ASR by **6.59 pp** for Qwen3.7-plus (95% CI [−7.89,−5.30]) and **4.77 pp** for Qwen3.5-plus ([−6.01,−3.55]); not uniform (OpenClaw/T4 moves +6.02 and +4.82).
10. **Diagnoses the Recognition–Execution Gap**: 17.92% broad / 5.48% strict of state-confirmed violations occur after the agent states the constraint. Lower bounds 16.05% and 4.91% if all unresolved anchors counted negative.
11. **Re-measures a defense with a state oracle**: policy reminder reduces ASR by **74.19 pp** (95% CI [69.85, 78.41]) on 510 matched pairs; 368 of 434 baseline harmful executions prevented; neutral control ≈ baseline.
12. **Makes the measurement tuple part of the metric**: *"we make the (harness, judging configuration, evaluation cue, judge backbone) tuple part of the ASR."*

## K.2 WHAT REDAgentBench DOES NOT DO

1. **No defense factor in the evaluator audit.** §4.3's fixed-rollout view comparison contains no defense; §4.6's defense is measured only with state-grounded outcomes.
2. **No judge-backbone variation in the main audit.** Backbone held fixed at Qwen3.7-plus to isolate the view; the pipeline is described as *supporting* backbone audits, but the reported experiments hold it fixed.
3. **No judge prompt-injection or adversarial-judge stress test.** The evaluator is treated as a measurement instrument, not as an attack surface.
4. **No judge calibration curve.** Precision/recall/accuracy are reported at one operating point, not as functions of threshold or as a full ROC.
5. **No variance decomposition of ASR** (no ICC, design effect, or effective sample size) — consistent with Phase 6's findings; that axis remains unoccupied but was rejected there for other reasons.
6. **Single-model diagnostic cohort** (Qwen-plus) for the state-grounded analyses.
7. **Replays are not full-benchmark estimates** — stated by the authors.

## K.3 Is the remaining gap significant?

**[INFER] No, not at the magnitude this project requires.** The residual is (1) × (2): add a defense factor to a published evaluator audit, and optionally vary the judge backbone. The published audit already supplies the mechanism, the direction, the approximate magnitude, the human ground truth, the significance test, and the ranking-inversion demonstration. Adding a factor is a **type-A extension**, and the phenomenon is not new.

---

# PART L — Chouldechova et al. deep audit

## L.1–L.6 Extraction

| # | Item | Content |
|---|---|---|
| 1 | **One-shot estimand** | `α = ℙ_{P∼D}[J(L(P;φ)) = 1]` |
| 2 | **Top-1-of-K estimand** | `α_{Top1(K)} = ℙ_{P∼D}[max_{k∈{1..K}} J(L(P;φ)_k); P) = 1]` |
| 3 | **Theoretical argument** | ASR is a *measurement* of an estimand defined by a probabilistic threat model `M = (s, D, C)` (oracle criteria, goal distribution, conditions). Two-part sufficient condition for meaningful comparison: **conceptual coherence** and **measurement validity**. Three processes: systematization → operationalization → execution; "conceptual gaps" separate from "measurement error". |
| 4 | **Empirical experiment** | Replication of Huang et al. on Llama 2 7B/13B Chat, 100 MaliciousInstruct prompts, 49 decoding configurations × 49 samples; one-shot ASR ≈0.2 flat across configs while Top-1 rises; per-prompt success-probability entropy increases with temperature. Also: Top-1 ASR over 50 resamples of the **base prompt** at temperature 2.0 is **0.83**. |
| 5 | **Measurement validity** | *"the extent to which a measurement instrument measures what it purports to measure"*; validity = agreement between the operationalized activity (`J`) and the systematized criteria (`s`). |
| 6 | **What they explicitly leave out** | *"we are primarily concerned with **validity issues (bias and systematic mismeasurement) not simply reliability issues (sampling variation)**."* Also, scope: jailbreaking as running example; *"the ideas are broadly applicable to ASRs obtained via other AI red teaming approaches"*; a broader related-work discussion deferred to Appendix A. |
| 7 | **Does the framework apply to judge error?** | **Yes — centrally.** §5 is *entirely* about it. `E(ASR) = TPR(J;s)·α + FPR(J;s)·(1−α)`; differential TPR/FPR across systems and across jailbreak approaches; *"equal accuracy or AUC across target systems"* is insufficient; cites Claude 2.1 false positives ("such false positives happen rarely on other models") and token-length-dependent judge error. |
| 8 | **Does it subsume the proposed question?** | **The theoretical half, yes.** The candidate's "evaluator effect" and "interaction" terms are the differential-error term in their equation. They add: *"issues of differential misclassification have been studied extensively in the statistics literature, and can be applied to produce more valid ASRs."* |

## L.7 The key sentence

**[FACT]** *"we are primarily concerned with validity issues… not simply reliability issues."*

**[INFER] This does not leave the evaluator-validity problem open — it is the *opposite*.** The sentence declares the validity side to be their focus. What they set aside is *reliability*. In Phase 6 that mattered, because the rejected direction sat on the reliability side. Here it cuts the other way: the candidate would be working **inside** their declared scope, on a problem their §5 already names and models analytically, and whose agent-specific empirical content REDAgentBench already supplies.

**[INFER] Verdict on Part L:** Chouldechova et al. **do** largely subsume the proposed direction's conceptual content. The residual is the agent-specific, defense-crossed measurement — which Part K.3 finds insufficient.

---

# PART M — "Judge attacks the judge"

**[FACT]** **Yes — the security community already treats the evaluator as an attack surface, extensively, with a dedicated 2026 SoK systematising it.** Al Masoud et al., *Security in LLM-as-a-Judge: A Comprehensive SoK*, arXiv:2603.29403 **[A]** (partial read), analyses **863 works**, selects **45 studies (2020–2026)**, and proposes a taxonomy with five perspectives: (i) **attacks targeting LaaJ systems**, (ii) attacks performed *through* LaaJ, (iii) defences leveraging LaaJ, (iv) evaluating LaaJ, (v) LaaJ as an evaluation strategy in security tasks.

Their §5.1 sub-taxonomy:

> *"Attacks targeting Judge LLMs can be organized along two temporal axes: those that corrupt the judge **during training**, and those that manipulate it at **inference time**. … training-time attacks include **backdoor and poisoning** attacks as well as **rubric and protocol manipulation**, while inference-time attacks encompass **prompt injection**, **token and surface-level perturbations**, and broader robustness assessments."*

Their §8 "Challenges and Open Problems" lists, verbatim in structure: **8.1 Vulnerability to Adversarial Prompt Manipulation**; **8.2 Positional Bias and Evaluation Manipulation**; **8.3 Length and Style Bias Exploitation**.

**[FACT]** §8.3 is titled **"Length and Style Bias Exploitation"** — i.e. the SoK *already names* the style-sensitivity problem that the candidate's Part F experiment would target, and frames the open problem as *designing detection and defence mechanisms*, not as *measuring defense-dependent error in agent security*:

> *"The open research problems in this context are: • Create evaluation systems based on LLM to prevent adversarial attacks. • Design methods for detecting prompt injection and evaluation manipulation attacks. • Design defence mechanisms for secured evaluation pipelines."*

**[INFER] Does agent-security defense evaluation add anything fundamentally new?** The SoK's taxonomy has a slot for LaaJ "used as an evaluation strategy in security-related domains" — their Table 3 already includes Shao et al. (2025), *"Automated assessment of LLM agents performing cybersecurity attacks"*, and Wang et al. (2025) on multimodal agent prompt injection. So **judge-based evaluation of security agents is already inside the systematised corpus.**

**Answer: no new fundamental surface.** What agent security adds is (a) trajectories rather than text — already handled by REDAgentBench; (b) durable side effects that can serve as an oracle — already handled; (c) defenses that alter observable evidence — the surviving residual, and thin.

---

# PART N — Scientific contribution test

Forced choice among A–G:

| Type | Verdict |
|---|---|
| **A. New empirical phenomenon** | **Not available.** Style/surface sensitivity is known (Know Thy Judge); evaluator-view sensitivity on agents with ranking reversals is known (REDAgentBench); defense-dependent judge error is named analytically (Chouldechova, Pathade). |
| **B. New benchmark/dataset** | **Not a contribution** by this project's standard, and redundant with REDAgentBench's blinded human audit (480 case versions, 320 frozen cases, 360 rollouts). |
| **C. New evaluation methodology** | **Not available.** State-grounded verification, view-specific proof contracts, hybrid reconciliation, an exposure–execution–observation–adjudication pipeline, rule-first judging, and the (harness, judging configuration, cue, backbone) tuple are all published by REDAgentBench. |
| **D. New statistical method** | **Not available.** Differential-TPR/FPR theory exists (Chouldechova §5, building on established differential-misclassification statistics); the accuracy-correction literature is cited by them as prior art. |
| **E. New theoretical result** | **Not available.** The identification structure and the inversion condition are published. |
| **F. New security mechanism** | **Out of scope** for a measurement project. |
| **G. New measurement-validity finding** | **The only partially open slot — and the residual is a factorial extension.** |

**Conclusion: none of A–G is cleanly available.** The direction fails Part N. Ordinary replication is not a contribution; combining existing metrics is not; "we use multiple judges" is not.

---

# PART O — Minimum novel experiment

**Not designed.** Part O is conditional on Parts A–N, which returned NO-GO.

**[INFER] For the record, the design the candidate sketched would have been:** crossed `defense {undefended, D₁, D₂} × evidence view {trajectory, state, hybrid} × judge backbone {2–3}` on a fixed set of matched rollouts, with a state-grounded oracle as ground truth and human adjudication on a subsample. That is **REDAgentBench's §4.3 audit plus a defense factor** — see Part N.

## O.1 Model suitability for that design — see Part P.

---

# PART P — Model resource audit

Verified at vendor sources in Phase 6; re-checked here.

| Model | Exact model ID | Release | Provider | API | Tool calling | Structured output | Temperature | Seed | Deterministic mode | Context | Revision pinning | Independently controllable? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **DeepSeek V4.1 Flash** | **`deepseek-flash`** (version `DeepSeek-V4.1-Flash`) | — | DeepSeek | **Yes**, official docs | **Yes** | **Yes** (JSON) | **Ignored in default thinking mode** — official: *"Thinking mode does not support the temperature, presence_penalty, or frequency_penalty parameters"* | **Not documented** | No | **1M** (max output 384K) | Legacy IDs retired; version string published | **Partially** — verified ID and version, but no seed and no temperature control in default mode |
| **GLM-5.3-Flash** | **`glm-5.3-flash`** / `glm-5.3-flashx` | 2026-08-26 (launch blog) | Z.ai / Zhipu | **Yes**, official docs `docs.z.ai` | **Yes** | **Yes** | **Yes**, recommended `temperature: 1`, `top_p: 0.95` | **Not documented** | No — *"thinking.type only supports enabled; thinking cannot be disabled"* | **1M** (max output 128K) | Model code published; 320B total / 18B active | **Partially** — temperature settable; no seed; thinking cannot be disabled |
| **MiMo 2.6 Flash** | **Unverified** — serving ID `mimo-v2.6-flash` appears only on aggregators; vendor HF card is an **RL variant** (`XiaomiMiMo/MiMo-V2.6-Flash-RL`) | — | Xiaomi | Vendor domain lists the product but the API-docs page did not render retrievable content (`mimo.mi.com/docs/price/pay-as-you-go` returned only a title) | **Unverified** | **Unverified** | **Unverified** | **Unverified** | **Unknown** | **Unverified** | **No** | **NO — fails the bar** |
| **Solar Mini 4** | `solar-mini4` (reported) | **~2026-09-22** | Upstage | Vendor blog confirms "live on Console" | **Unverified** | **Unverified** | **Unverified** | **Unverified** | **Unknown** | 524K (aggregator only) | **None** | **NO — excluded** (≈3 days old at audit; no independent evaluation; all specs aggregator-only) |

**[INFER] Verdict on Part P: the inventory is insufficient for the proposed design, for three independent reasons.**

1. **No seed and no temperature control on either verifiable model** — DeepSeek's default mode ignores temperature outright, and GLM cannot disable thinking. A judge-validity study requires stable, reproducible *target* behaviour so that variation in labels can be attributed to the evaluator rather than to an uncontrolled target. **[INFER]** With both models' sampling uncontrollable, evaluator-attributable variance is confounded with target sampling variance at the source.
2. **No frontier or plus-tier target.** REDAgentBench ran GPT-5.2, Qwen3.7-plus, Qwen3.5-plus, Qwen-plus-2025-12-01, Kimi K2.6, GLM-5.2 through three harnesses; Hofer et al. ran GPT-5; Khan et al. ran GPT-5.4/5.4-mini and Claude Sonnet 4.6; Deep et al. ran Gemini 2.5 Pro, GPT-5.4, Claude Sonnet 4.6. **[INFER]** A judge-validity study needs the target to *commit* violations so the judge has something to misjudge. If the two available models refuse broadly, the label distribution is degenerate and the comparison is vacuous — the same failure mode Khan et al. hit at 0/288.
3. **No sandbox/service infrastructure and no judge diversity.** REDAgentBench required instrumented sandboxes across five service surfaces and 8×A100s; the design also needs a judge strong enough to be a realistic evaluator, plus human adjudication.

**[FACT]** Independently of novelty, the resource position would have to change materially before this class of study is runnable.

---

# PART Q — Hostile reviewer test

### Reviewer 1 — "This is just LLM-as-a-judge reliability research."
**Strongest form.** The judge-reliability literature is mature and systematised (SoK: 863 works screened, 45 analysed); style/length/position bias and judge attacks are catalogued with effect sizes; Miller 2024 supplies the reliability statistics.
**Fatal?** **YES**, for the framing. Not fatal to a validity-framed study, which is why the candidate pivoted to validity — and the validity side is where Chouldechova and REDAgentBench sit.
**Minimum evidence.** A validity finding, not a reliability measurement: a demonstrated case where the *conclusion* changes and the cause is evaluator-side rather than behaviour-side.

### Reviewer 2 — "Chouldechova et al. already establish that repeated sampling changes the estimand."
**Strongest form.** Their §4 formalises one-shot vs Top-1-of-K and calls the comparison apples-to-oranges; §5 gives the differential-error equation with the explicit statement that equal accuracy is insufficient.
**Fatal?** **NO — it is a different claim** (sampling/budget, not defense-dependent judge error). But it **is fatal to any claim that the evaluator-error framing is new**, and it supplies the theoretical half of our decomposition.
**Minimum evidence.** A defense-crossed, agent-specific measurement that their framework *predicts* but does not contain.

### Reviewer 3 — "REDAgentBench already solves the evaluator problem."
**Strongest form.** REDAgentBench formalises reported ASR as exposure → execution → observation → adjudication; implements three view-specific evaluators over a fixed backbone; holds rollouts fixed and shows 7.73–11.72 pp ASR shifts, 12.97–21.20% label flips and **43 ranking inversions significant at p ≤ 6.54×10⁻⁵**; validates against two blinded human reviewers (κ = 0.838); and re-measures a defense with a state oracle, which *is* the oracle-vs-judge comparison.
**Fatal?** **PARTIALLY FATAL.** Not a total solve — no defense in the view audit, backbone fixed — but it establishes the phenomenon, the magnitude, the mechanism, the human ground truth, and the ranking conclusion on agents. The candidate's contribution reduces to "add a defense factor".
**Minimum evidence.** A defense × view interaction that is (a) non-zero, (b) sign-changing for a *published* defense, and (c) not predictable from the main effects REDAgentBench reports. **[INFER]** That is a narrow, quantitative target.

### Reviewer 4 — "This is just comparing several judges."
**Strongest form.** Multiple judges, ensembles, view-specific evaluators, cross-judge bias transfer (RIPD) and ensemble metrics are all published.
**Fatal?** **YES**, if the contribution is stated as comparing judges. Multi-judge comparison is a known mitigation with documented limits.
**Minimum evidence.** A substantive finding *from* the comparison — which is precisely the defense × evaluator interaction.

### Reviewer 5 — "Human annotation would trivially solve this."
**Strongest form.** If ground truth is the issue, label it by hand — REDAgentBench already did (480 case versions, 320 frozen cases, 360 rollouts, κ = 0.838).
**Fatal?** **YES**, as a contribution. "Use humans" is a known solution with a known cost, and the human-adjudicated comparison already exists on agents.
**Minimum evidence.** Evidence that human adjudication *fails* in some regime (scale, cost, expertise, adversarial cases) — nobody has shown that, and showing it would be a different paper.

### Reviewer 6 — "The defense genuinely changes the output, so the evaluator is correctly responding to it."
**Strongest form.** If a defense causes the agent to refuse, the trajectory *is* safer, and a judge reading "refusal" as "no violation" is not biased — it is accurate. The candidate would need to separate "the defense changed behaviour" from "the defense changed appearance", and the judge is entitled to use appearance as evidence.
**Fatal?** **PARTIALLY — and this is the sharpest objection.** REDAgentBench's own mechanisms cut both ways: *"the agent even refused only after the harmful write had occurred"* (judge wrong — harm already done) versus *"receipts often omitted the authorization or payload context needed to interpret a recorded action"* (state view wrong — a legitimate action misread as a violation). **[INFER]** Neither view is privileged; this is a **multi-instrument validity** problem, not a judge-bias problem, and REDAgentBench already frames it that way with a hybrid reconciler.
**Minimum evidence.** An oracle that is agreed *a priori* to be correct for the cases at issue, and a demonstration that the judge deviates from it systematically by defense. **[INFER]** For durable side-effect cases the state oracle is that oracle — which is why REDAgentBench's defense experiment uses it, and why the candidate's premise is partly answered by design.

### Reviewer 7 — "Your finding is an artifact of weak Flash-tier models."
**Strongest form.** All four available models are Flash/mini-tier; two are unverified; none documents a seed; DeepSeek ignores temperature in default mode and GLM cannot disable thinking. Judge bias is *strongest* for degenerate trajectories, so a Flash-tier target could manufacture an evaluator effect that a frontier target would not show.
**Fatal?** **YES** for the proposed instantiation, and independently of novelty (Part P).
**Minimum evidence.** A second, stronger model tier and documented sampling control.

---

# PART R — Falsification criteria

| # | NO-GO criterion | Met? | Evidence |
|---|---|---|---|
| R1 | A recent paper already experimentally isolates defense-dependent evaluator error | **PARTIALLY MET** | REDAgentBench isolates *evaluator-view*-dependent error at fixed rollout, with ranking inversions and human ground truth; the defense factor is not crossed |
| R2 | Human-vs-LLM evaluator disagreement is already characterised for agent security | **MET** | REDAgentBench: 360 rollouts, κ = 0.838, precision 97.84%, recall 91.27%, raw judged ASR 55.43% vs audited 59.42% |
| R3 | REDAgentBench already provides the required methodology | **MET** | View-specific evaluators over a fixed backbone, state-grounded oracle, rule-first judging, hybrid reconciliation, the measurement tuple, paired McNemar, clustered CIs |
| R4 | Chouldechova's validity framework already subsumes the proposed contribution | **MOSTLY MET** | §5 gives `E(ASR) = TPR·α + FPR·(1−α)`, differential error across systems and methods, and "equal accuracy is insufficient"; they declare validity to be their focus |
| R5 | A SoK already systematises the space | **MET** | R79: 863 works, 45 selected, five-perspective taxonomy; §8.3 is "Length and Style Bias Exploitation" |
| R6 | The style/surface-sensitivity phenomenon is already quantified | **MET** | Know Thy Judge: up to 0.24 FNR from style alone; adversarial generation → up to 100% misclassification |
| R7 | The evaluator is already treated as an attack surface | **MET** | JudgeDeceiver, BadJudge, Emoji Attack, master-key, RIPD, Malayan & Namiot, Li et al. — all catalogued with effect sizes |
| R8 | Multiple judges are already standard | **MET** | REDAgentBench 3 views; SoK ensembles; Ensemble-Judge metric |
| R9 | Human ground truth already exists at meaningful scale for agent security | **MET** | REDAgentBench blinded audits |
| R10 | Evaluator disagreement does not materially change conclusions | **NOT MET** | The opposite: 43 inversions, p ≤ 6.54×10⁻⁵ |
| R11 | The effect exists only with one weak evaluator | **NOT MET** | Holds across all six models in REDAgentBench |
| R12 | The effect disappears under evaluator swapping | **NOT MET** | It *persists* under view swapping |
| R13 | Human adjudication confirms the automated judge | **PARTIALLY MET** | REDAgentBench's judge is *accurate* (precision 97.84%) yet the view still changes 12.97–21.20% of labels — accuracy and view-sensitivity coexist |
| R14 | The phenomenon occurs only in toy examples | **NOT MET** | 1,661 executable cases, five service surfaces |
| R15 | Cannot be reproduced across models | **NOT MET** | Reproduced across six models |
| R16 | The proposed experiment is merely a replication/extension | **MET** | The residual is REDAgentBench §4.3 plus a defense factor |

### Additional criteria I add

| # | Criterion | Met? |
|---|---|---|
| **R17** | The candidate's central hypothesis is already stated as a diagnosis in an existing paper's own words | **MET** — Pathade et al.: *"Defenses change the distribution of trajectories… so an uncalibrated judge's error rate is not constant across the systems being compared. That is precisely the condition under which ranking fails to be preserved."* |
| **R18** | The identification problem has a known, published solution | **MET** — state-grounded oracles and rule-first judging (REDAgentBench) |
| **R19** | The candidate's proposed instrument already exists as a published artefact | **MET** — REDAgentBench *is* the instrument |
| **R20** | The contribution would land inside a scope another paper explicitly claims as its own focus | **MET** — Chouldechova et al.: *"primarily concerned with validity issues… not simply reliability issues"* |
| **R21** | The resource position makes the experiment unrunnable regardless of novelty | **MET** — Part P |
| **R22** | Even a positive result would be unsurprising to a reader of the SoK | **MET** — R79 §8.3 predates and names style bias exploitation |

**Five criteria (R3, R4, R5, R19, R20) are each sufficient to reject.** As in Phase 6, the direction fails a conjunctive standard.

---

# PART S — Final decision

# **NO-GO**

### S.1 Final research question

**None for this direction.** The candidate question — *"how much can evaluator/judge behavior alter measured security-defense effectiveness in LLM-agent security evaluation?"* — has its magnitude quantified for the evaluator-view axis (7.73–11.72 pp; 43 inversions; p ≤ 6.54×10⁻⁵) and for the surface/style axis (up to 0.24 FNR). The defense-crossed version is a factorial extension of a published audit.

### S.2 Novelty status

**Not novel.** [FACT] The phenomenon is established with effect sizes (Know Thy Judge, REDAgentBench). [FACT] The agent-specific instance is established on fixed rollouts with human ground truth and ranking inversions (REDAgentBench §4.3). [FACT] The theoretical account is published with an exact equation and an insufficiency result (Chouldechova §5). [FACT] The mechanism is named in an existing catalogue entry (Pathade A2). [FACT] The space is systematised (SoK R79). [FACT] The evaluator is already treated as an attack surface, with a dedicated taxonomy. [FACT] The identification solution is published and implemented (state-grounded oracles, rule-first judging).

### S.3 Closest competing paper

**REDAgentBench**, Chen et al., arXiv:2608.10669 (2026-08-11) **[A]**. Secondary: **Chouldechova et al.**, NeurIPS 2025, arXiv:2601.18076; **Eiras et al.** (*Know Thy Judge*), arXiv:2503.04474; **Al Masoud et al.** (SoK), arXiv:2603.29403; **Pathade et al.**, arXiv:2609.25173.

### S.4 Exact overlap

REDAgentBench formalises reported ASR as **exposure → execution → observation → adjudication**; builds three **view-specific evaluators** (trajectory / state / hybrid) over a **fixed judge backbone** with proof contracts and deterministic gates; holds **rollouts fixed** and shows the judging configuration changes 12.97–21.20% of labels, shifts ASR by 7.73–11.72 pp, produces **43 ranking inversions across 23 of 64 slices** (all six paired differences at exact McNemar p ≤ 6.54×10⁻⁵), and validates the judge against **two blinded human reviewers** (κ = 0.838). It documents the mechanism: *"a trajectory-view may suggest safety, while the state-view confirms harm"*, and *"the agent even refused only after the harmful write had occurred."* It then re-measures a **defense** with a state-grounded oracle (74.19 pp reduction, 95% CI [69.85, 78.41]). **That is the candidate's core experiment, with a better instrument, human ground truth, and a published significance test.**

### S.5 Exact remaining gap

Two cells: (i) the **defense factor is absent from the view audit** (their defense is measured only with the state oracle); (ii) the **judge backbone is held fixed**, so judge-model × defense interaction is untested.

### S.6 Why the gap matters scientifically

**[INFER] It matters less than the project standard requires.** The main effect is quantified; the mechanism is documented; the theoretical form is written; the human ground truth exists; the ranking consequence is demonstrated. A defense × view interaction is a *quantitative refinement* whose direction can be predicted from the published main effects. It would not change how the field designs evaluations — REDAgentBench already changed that by making the measurement tuple part of the metric.

### S.7 Primary estimand — **MARGINAL, for the record only**

`Δ_obs-judge(D) = E_c[ Y_c(D, trajectory view) ] − E_c[ E_c(D) ]`, the defense-conditional judge-minus-oracle gap, and its sign/magnitude across defenses. **[HYP]** This is the only estimand the residual supports, and it is a difference of two quantities the closest paper already reports separately.

### S.8 Hypotheses — **NOT RECOMMENDED**

Recorded only to show they are thin:
- **[HYP] J1.** A defense that changes refusal phrasing shifts judge labels more than a defense that changes executed outcomes.
- **[HYP] J2.** The defense × view interaction is non-zero and can reverse a defense ordering.
- **[HYP] J3.** The interaction magnitude scales with the *style distance* between defended and undefended trajectories.
- **[HYP] J4.** Hybrid reconciliation does not remove the interaction.

**[INFER]** J1 and J3 are restatements of the known style-sensitivity result; J2 is the factorial extension; J4 is an ablation of an existing artefact.

### S.9 Minimum viable experiment — **NOT DESIGNED**

Would have been REDAgentBench §4.3 with a defense factor added (Part O). Ruled out at Parts N and R16.

### S.10 Required ground truth — **ALREADY EXISTS**

State-grounded oracles over durable side effects (receipts, final-state diffs), plus blinded human adjudication. Both published by REDAgentBench at a scale this project cannot match.

### S.11 Required models — **INSUFFICIENT**

Per Part P: two verifiable models, both Flash-tier, neither with a documented seed, DeepSeek ignoring temperature in its default mode, GLM unable to disable thinking; MiMo's API surface unverified at the vendor; Solar excluded as ~3 days old. No frontier or plus-tier target, no documented sampling control, and a real risk of degenerate (all-refusal) trajectories that would make the judge comparison vacuous.

### S.12 Required statistics — **PUBLISHED**

Paired exact McNemar (REDAgentBench uses it on the matched view comparison), case-clustered confidence intervals (REDAgentBench RQ3/RQ5), stratified case-cluster uncertainty for the judge audit, precision/recall/specificity/F1, and the differential-error equation (Chouldechova). Nothing new is needed, which is itself a signal that the study would be an application, not a contribution.

### S.13 Falsification criteria

See Part R. **Sixteen standard criteria and six added criteria are met or partially met; five are individually sufficient for rejection.**

### S.14 Biggest reviewer objection

**Reviewer 6**, sharpened: *"The defense genuinely changes the output, so the evaluator is correctly responding to it."* **[INFER]** This is the deepest problem with the direction and it is not merely rhetorical. REDAgentBench's own findings cut both ways — a trajectory judge misses a write that already happened (judge wrong), while a state receipt can omit the authorization context that makes a recorded action benign (state view wrong). The correct framing is therefore **multi-instrument validity with no privileged instrument**, and REDAgentBench already reflects that by *reconciling* rather than choosing. **[INFER]** A candidate premised on "the judge is the biased instrument" is answering a question the closest paper has already reframed as "which instrument is reliable for which evidence class."

### S.15 Biggest practical/resource risk

**[INFER]** The target models may not produce enough violations for the judge to misclassify. Khan et al. hit exactly this at **0/288** and **1/288** undefended baselines, concluding the paired test had *"no practical power to detect a defense effect of any size."* Two Flash-tier models on any benchmark with AgentDojo-like goal-feasibility structure risk the same degeneracy, which would make a judge-validity comparison uninformative before it began.

### S.16 Does Agent Security Lab remain useful as infrastructure?

**[INFER] Largely no, as currently conceived.** The infrastructure this direction would need — instrumented service sandboxes with structured receipts and baseline-to-final state diffs across five surfaces, three view-specific evaluators over a fixed backbone with proof contracts, rule-first deterministic verifiers, and a blinded human-adjudication workflow — **is REDAgentBench**, already built and published. Reimplementing it would duplicate a released artefact. The parts of AgentSec Lab that retain value are (a) the **source registry and claim-labeling discipline** (A/B/C plus FACT/INFER/HYP/OPEN), which has now survived three failed directions and is doing real work; and (b) the **reproducibility/measurement-validity literature map**, which is a genuine asset for whoever writes the eventual survey. Neither is a security measurement platform.

---

# Final recommendation

# **Abandon this research direction.**

Not "search one more time." The elimination was executed and succeeded, and this phase found the decisive obstacle in the *second* paper read. Three independent grounds:

1. **REDAgentBench already ran the experiment.** Fixed rollouts, view-specific evaluators over a fixed backbone, 12.97–21.20% of labels changed, 43 ranking inversions across 23 of 64 slices, all paired differences significant at exact McNemar **p ≤ 6.54×10⁻⁵**, validated against two blinded human reviewers (κ = 0.838), with the mechanism documented ("a trajectory-view may suggest safety, while the state-view confirms harm"). The candidate's Part F experiment is a subset of this, and the residual is a factorial extension — REDAgentBench §4.3 plus a defense factor.
2. **The theory is published and the scope is claimed.** Chouldechova et al. give `E(ASR) = TPR·α + FPR·(1 − α)`, show equal accuracy is insufficient, and declare validity — not reliability — to be their focus. Pathade et al. state the candidate's mechanism in their own words. A 2026 SoK, screening 863 works, has systematised the space and names "Length and Style Bias Exploitation" as a known challenge.
3. **The resources do not support it independently of novelty.** Two verifiable Flash-tier models, no documented seed on either, DeepSeek ignoring temperature in its default mode, GLM unable to disable thinking, MiMo unverifiable at the vendor, Solar excluded — against a closest competitor using six models across three harnesses on 8×A100s, with two blinded expert reviewers.

**A pattern worth recording honestly, since it has now held three times. [INFER]** In Phases 5, 6 and 7 the same structure recurred: the project identified a real, important, correctly-reasoned problem, and the literature had already reached it — not with a narrow statistical variation, but with the full instrumentation. Phase 5 lost to Khan et al. and Miller; Phase 6 to Chouldechova et al. and Deep et al.; Phase 7 to REDAgentBench and a SoK. That convergence is evidence about the *field*, not about the project's method: LLM-agent security evaluation **is** a measurement-validity research programme now, and it is being executed by groups with frontier model access and expert annotation capacity. **[INFER]** The binding constraint on this project has shifted from novelty to resources, and the honest next step is not another direction audit but a decision about whether the resource position can change.

**Suggested disposition of the existing work.** The three audits (Phases 5–7) plus the source registry constitute a defensible **systematic review with claim-level verification** — "measurement validity in LLM-agent security evaluation: what is established, what is claimed, and what remains untested" — which is publishable in a survey/SoK-adjacent venue precisely *because* it does not require original experiments. It would need to be positioned against Li et al. (40-benchmark taxonomy, R21) and Al Masoud et al. (judge-security SoK, R79), and it must not claim methodological novelty.

---

# PART T — Source registry

- **`research/tables/sources.csv`** — extended to **R01–R90**, preserving the existing 11-field schema so the file remains valid. New entries R77–R90, with schema-compatible notes carrying the evaluator dimensions.
- **`research/tables/judge-validity-matrix.csv`** — **new**, carrying the 18 evaluator-specific fields requested in Part T (`source_id, title, authors, year, venue, url, arxiv_or_doi, research_question, evaluator_type, ground_truth, judge_reliability, judge_validity, judge_attack, defense_evaluation, agent_security, exact_overlap, relevance, status`). This is a separate table because appending 18-field rows to an 11-field registry would corrupt it.

Both files validated: field counts uniform, quoting correct, no malformed rows.

## Appendix — registry changes in this phase

| id | Source | Label | Role |
|---|---|---|---|
| **R77** | REDAgentBench, Chen et al., arXiv:2608.10669 | **A** | **The decisive source.** Closest competitor |
| **R78** | Eiras, Zemour, Lin & Mugunthan, *Know Thy Judge*, arXiv:2503.04474, ICBINB @ ICLR'25 | **A** (abstract + key results) | Style → FNR jump up to 0.24; adversarial generation → 100% misclassification |
| **R79** | Al Masoud et al., *Security in LLM-as-a-Judge: A Comprehensive SoK*, arXiv:2603.29403 | **A** (partial: §1–5, §8.1–8.3; truncated) | 863 works screened, 45 selected; five-perspective taxonomy; §8.3 Length and Style Bias Exploitation |
| **R80** | Shi et al., JudgeDeceiver — *Optimization-based prompt injection attack to LLM-as-a-judge*, **ACM CCS 2024** | **B** (via R79) | Judge prompt injection; known-answer/perplexity defences miss ≥70% |
| **R81** | Tong, Wang, Zhao & Chen, *BadJudge*, arXiv:2503.00596 | **B** (via R79) | Judge backdoor; 1% poisoning → 3× score inflation; toxic misclassified as safe 83.9% |
| **R82** | Ding et al., *Rubrics as an attack surface: stealthy preference drift in LLM judges*, arXiv:2602.13576 | **B** (via R79) | Rubric-induced preference drift; ↓9.5% / ↓27.9% accuracy at ≈0.85 benchmark agreement |
| **R83** | Wei et al., Emoji Attack | **B** (via R79) | Token-segmentation bias; ShieldLM 71.9% → 3.5% |
| **R84** | Zhao et al., master-key attack on reward models | **B** (via R79) | FPR up to 80% across 10 keys, 5 benchmarks |
| **R85** | Li, Xu, Wang et al., *LLMs cannot reliably judge (yet?)*, arXiv:2506.09443 | **B** (via R79) | 15 attacks; PAIR+Combined ≈70% ASR on GPT-4o; up to 40% variation across prompt templates |
| **R86** | Maloyan & Namiot, *Adversarial attacks on LLM-as-a-judge systems*, arXiv:2504.18333 | **B** (via R79) | Max ASR 73.8%. **Note:** distinct from the R-set entry for Maloyan & Namiot on agentic coding assistants (arXiv:2601.17548) — do not conflate |
| **R87** | Zhang et al., *Stop comparing LLM agents without disclosing the harness*, arXiv:2605.23950 | **B** (via R77) | Harness disclosure; harness-dependent rankings |
| **R88** | Lee, Zeng, Jeong, Sohn & Lee, *How to correctly report LLM-as-a-judge evaluations*, arXiv:2511.21140 | **B** (via R77) | Reporting practice for judge-based evaluation |
| **R89** | Divekar & Majumder, *PRECISE*, AAAI | **B** (via R77) | Prediction-powered ranking estimation to reduce evaluator bias |
| **R90** | McKenzie et al., *STACK: adversarial attacks on LLM safeguard pipelines*, AAAI | **B** (via R77) | Attacks on guard pipelines |
| **R43** | Yuan et al., R-Judge, Findings of EMNLP 2024 | upgraded to **A for venue** (via R77) | Agent risk-awareness dataset; adjacent, not adjudication |

**Also noted, not yet independently verified:** Nasr et al., *The attacker moves second* (USENIX Security, cited by R77) is likely the same work previously catalogued as **R48** (arXiv:2510.09023, *"Stronger Adaptive Attacks Bypass Defenses"*) — the titles and framing correspond, but **identity is not asserted here** and should be confirmed at source before the two entries are merged.
