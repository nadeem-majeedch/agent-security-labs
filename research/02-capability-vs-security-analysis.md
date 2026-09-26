# Capability vs. Security in LLM-Agent Evaluation — Verification and Reconciliation

**Status:** working analysis, not a paper. Pass 2 of the AgentSec Lab landscape work.
**Supersedes/extends:** `research/01-landscape-and-gap-analysis.md`.
**Date:** 2026-09-25.

---

## 0. Method, verification convention, and limitations

This document answers a single prior question: *is the apparent "capability vs. security
contradiction" real, meaningful, and experimentally testable?*

### 0.1 Verification labels (unchanged from pass 1)

| Label | Meaning |
|---|---|
| **A** | Text read at the primary source in this pass or pass 1 (vendor/authored arXiv HTML or abs page, proceedings page). |
| **B** | Search-result level only. Do not cite. |
| **C** | Not verified at all. Do not cite. |

`usable_in_paper_now` in `research/tables/sources.csv` remains the gate for citation.
Nothing asserted below as a fact is labelled B or C unless it is explicitly flagged as
unverified in-line.

### 0.2 Limitations that constrain this pass

These are stated up front because several of them bear directly on the conclusion.

1. **Full texts were truncated at fetch time.** The HTML renderings of RAS-Eval
   (`arXiv:2506.15253v1`) and MCPTox (`arXiv:2508.14925v1`) were cut off mid-paper in
   **both** passes. All statements below about RAS-Eval's scaling analysis are therefore
   marked as **pass-1 full-text reading, not re-confirmed in pass 2**.
2. **Footnote-only evidence.** The AgentDojo tool count has an internal inconsistency
   (§3.1 says 74 tools; Table 1's caption says 70; Table 1's rows sum to 74). Recorded
   as evidence that even high-quality benchmarks carry small numerical defects.
3. **No git metadata** is available on this host; no branch or status context exists.
4. **No statistical re-analysis** was performed. Everything below is a reading of what
   authors did and claimed, not a recomputation.
5. **Search-engine negative results are weak evidence.** "I could not find study X" is
   reported as *not located*, never as *does not exist*.

---

## 1. The originals: what each study actually did

Scope: studies that (a) report a capability/scale→security relationship, or (b) are the
principal comparison points for such a claim, or (c) are load-bearing for the
"operational cost" and "attacker budget" questions.

### 1.1 AgentDojo (R01) — **A**, fetched in full (main text) in this pass

Debenedetti, Zhang, Balunovic, Beurer-Kellner, Fischer, Tramèr (ETH Zurich + Invariant
Labs). NeurIPS 2024 Datasets & Benchmarks Track. `arXiv:2406.13352`, v3.

| Field | Record |
|---|---|
| Models | Gemini 1.5 Flash & Pro, Claude 3 Sonnet & Opus, Claude 3.5 Sonnet, GPT-3.5 Turbo, GPT-4 Turbo, GPT-4o, Llama 3 70B, Command R+ (11 model configurations) |
| Families | Google, Anthropic, OpenAI, Meta, Cohere — genuinely cross-provider |
| Sizes | Not used as an analytic variable |
| Framework | AgentDojo's own Python package; stateful environments; function-calling APIs |
| Environments | Workspace (24 tools / 40 user tasks / 6 injection targets), Slack (11/21/5), Travel (28/20/7), Banking (11/16/9) |
| Benchmark size | 97 user tasks, 27 injection targets, 629 security test cases; tool count 74 (rows sum; caption says 70) |
| Attacks | "Important message" injection; InjecAgent-style IPI; "ignore previous instructions"; `TODO:` prefix; an adaptive **Max** attack selecting the best of the four per case |
| Defenses | Data delimiters/spotlighting-style, BERT-based prompt-injection detector, prompt sandwiching, tool filter |
| Metrics | Benign utility; utility under attack; targeted ASR. 95% CIs via `statsmodels.stats.proportion.proportion_confint` |
| Capability explicitly measured? | **No.** "Capability" is read off benign utility / model identity |
| Utility measured? | **Yes**, formally, from environment state, not by an LLM judge |
| Cost measured? | **Partially.** The checklist states they "report the estimated cost of running the full suite of security test cases on GPT-4o in Appendix D." That is *evaluation* cost, not *defense* overhead |
| Statistical methodology | Descriptive scatter plots (benign utility vs. targeted ASR) plus 95% CIs. **No correlation coefficient or significance test of the capability–ASR relation is stated in the main text** |

**The claim, verbatim (§4.1):**

> "We find that more capable models tend to be easier to attack, a form of inverse scaling
> law (a similar observation had been made in [37])."

…immediately followed by the authors' own confound note:

> "This is a potentially unsurprising result, as models with low utility often fail at
> correctly executing the attacker's goal, even when the prompt injection succeeds."

Other load-bearing numbers: attacks succeed against the best agents in <25% of cases;
the detector defense drops ASR to 8%; the tool-filter defense drops ASR to 7.5% but fails
when the required tools are also sufficient for the attack (true for 17% of cases); "All
defenses lose 15-20% of utility under attack"; the Slack suite is attackable at 92%;
injections at the end of a tool response reach up to 70% ASR against GPT-4o.

**Note for §6:** AgentDojo's own future-work list includes *"(v) the addition of
constraints on prompt injections (e.g., in terms of length or format) could better capture
the capabilities of realistic adversaries."* The benchmark authors themselves flag
attacker-constraint modelling as unfinished.

### 1.2 MCPTox (R06) — **A**, abstract page fetched; full text read in pass 1 only

Wang, Gao, Wang, Liu, Sun, Cheng, Shi, Du, Li. `arXiv:2508.14925`.
Tool **poisoning** (malicious instructions in tool *metadata*, not tool output) against
live MCP servers.

| Field | Record |
|---|---|
| Corpus | 45 live real-world MCP servers, 353 authentic tools, 1312 malicious cases |
| Attack templates | Three; §3 reports paradigms P1 Explicit-Trigger Function Hijacking (224), P2 Implicit-Trigger Function Hijacking (548), P3 Implicit-Trigger Parameter Tampering (725) — pass-1 reading |
| Model settings | 20 |
| Metrics | ASR; refusal rate |
| Utility measured? | **No** |
| Cost measured? | **No** |
| Defenses evaluated? | **No** (only refusal/failure-case analysis) |
| Turns | Single-turn (pass-1 reading) |

**The claim, verbatim (abstract):**

> "We find that more capable models are often more susceptible, as the attack exploits
> their superior instruction-following abilities."

Reported ASRs include o1-mini 72.8%; highest refusal rate (Claude-3.7-Sonnet) <3%.

**Confounders already visible at source:** the abstract itself attributes the effect to
*instruction-following ability* — i.e. it names a specific sub-component of capability as
the mechanism. Pass 1 further recorded that the inverse-scaling evidence is argued on the
**Qwen3 family only** (8B vs 32B) and that reasoning-on vs. reasoning-off accounts for
**+27.8% ASR**, which confounds capability with an inference-time mode change. Also
recorded: abstract says 10 risk categories, §3 text says 11.

### 1.3 RAS-Eval (R03) — **A** (abstract); full text read in pass 1, **truncated in both passes**

Fu, Yuan, Wang (Zhejiang University). `arXiv:2506.15253`, v1, 18 Jun 2025.

| Field | Record |
|---|---|
| Corpus | 80 test cases, 3802 attack tasks, 11 CWE categories, 7 scenarios, 75 real tools |
| Tool formats | JSON, LangGraph, MCP |
| Execution | Simulated **and** real-world |
| Models | Abstract: "6 state-of-the-art LLMs". §3.1.1 reportedly says "eight representative LLMs" — internal inconsistency (pass-1 reading) |
| Metrics | TCR, TIR, TFR, performance score, ASR |
| Agreement | Per-model κ 0.43–0.78 (avg 0.6499) — pass-1 reading |
| Utility measured? | Partially, via TCR |
| Cost measured? | **No evidence located** |

**The claim, verbatim (abstract):**

> "attacks reduced agent task completion rates (TCR) by 36.78% on average and achieved an
> 85.65% success rate in academic settings. **Notably, scaling laws held for security
> capabilities, with larger models outperforming smaller counterparts.**"

**Critical methodological finding (pass-1 full-text read — flag as needing re-confirmation):**
the scaling-law analysis (RQ2) regresses the **unattacked performance score** on
log(parameters) over the **Qwen series only** (reported R² = 0.9051, adj. R² = 0.8577,
SSE = 68.0004, RMSE = 5.8310). If that reading is right, the headline sentence is not a
test of *security* as a function of capability at all — it is a capability-scaling result
relabelled as a security-scaling result. Pass 1 additionally recorded that all attack-task
tests were run exclusively on **GLM4-Flash**.

**This is the single most consequential item in the reconciliation and the first thing that
must be re-verified against the untruncated text.**

### 1.4 ASB / Agent Security Bench (R02) — **A**, fetched in this pass

Zhang, Huang, Mei, Yao, Wang, Zhan, Wang, Zhang (Zhejiang + Rutgers). ICLR 2025,
`arXiv:2410.02644`, v4.

| Field | Record |
|---|---|
| Scenarios | 10 (e-commerce, autonomous driving, finance, …) |
| Agents / tools / tasks | 10 agents, >400 tools, 400 tasks (aggressive / non-aggressive) |
| Attacks | 10 prompt-injection attacks, 1 memory-poisoning attack, 1 novel Plan-of-Thought (PoT) backdoor, 4 mixed attacks |
| Defenses | 11 |
| Methods total | 27 attack/defence types |
| Metrics | 7, **including a new metric "to evaluate the agents' capability to balance utility and security"** (introduced as Net Resilient Performance, NRP) |
| Backbones | 13 |
| Headline | Highest average ASR 84.30% |
| Cost measured? | **No evidence located** |

Relevance: ASB is the strongest existing **utility-security co-metric** contribution
(NRP). It also explicitly frames its 13-backbone sweep as guidance "for selecting suitable
backbones for agent applications". Whether ASB *statistically tests* a capability→security
relation is **not confirmed** from the abstract; treat as unverified.

### 1.5 AgentDyn (R08) — **A**, fetched in this pass

Li, Wen, Shi, Zhang, Vorobeychik, Xiao (Washington University in St. Louis + JHU).
`arXiv:2602.03117`, v3.

| Field | Record |
|---|---|
| Corpus | 60 open-ended tasks, 560 injection cases; Shopping, GitHub, Daily Life |
| Avg. per task | 33.33 tools, 7.10 trajectory steps, 3.17 applications |
| Comparison (Table 1) | AgentDojo 19.87 / 3.49 / 1.38; InjecAgent 2 / 1 / 1; ASB 3 / 1 / 1 |
| Defenses | Abstract says "ten"; Figure 1 caption says "9 advanced defenses powered by GPT-4o" — internal inconsistency |
| Targets | Three flaws in prior benchmarks: (i) no dynamic open-ended tasks, (ii) no helpful third-party instructions, (iii) simplistic user tasks |
| Contention | Only 6 of 97 AgentDojo tasks require dynamic planning |
| Finding | Nearly all defenses either insecure or severely over-defensive; Progent degrades sharply on larger tool sets; CaMeL/DRIFT/Tool Filter over-defend on dynamic tasks |

Relevance: AgentDyn is the current frontier of *defence-deployability* evaluation and of
**over-defence** measurement. It strengthens the "utility" side of the utility-security
pair. It does **not** test a capability→security relation.

### 1.6 Nasr et al., "The Attacker Moves Second" (formerly R48) — **now A**, fetched in this pass

Nasr, Sitawarin, Hayes, Schulhoff, Ilie, Pluto, Song, Chaudhari, Shumailov, Thakurta,
Xiao, Carlini, Terzis, Tramèr. `arXiv:2510.09023`.

| Field | Record |
|---|---|
| Claim | 12 recent defences bypassed with **ASR >90% for most**, where the original papers reported near-zero |
| Attack families | Gradient descent, reinforcement learning (GRPO), search/genetic, **human red-teaming (>500 participants)** |
| Substrates | HarmBench (jailbreaks); AgentDojo, OpenPromptInject, adversarial Davinci (prompt injection) |
| Notable results | Spotlighting & Prompt Sandwiching: static ASR as low as 1% on AgentDojo → **>95%** adaptive; 265 and 178 human-authored successful attacks respectively. MetaSecAlign: 2% static → **96%** adaptive. Circuit Breakers: **100%** ASR on HarmBench. RPO: 98% (RL) / 96% (gradient). Detectors ProtectAI / PromptGuard / Model Armor: **>90%**; PIGuard 71%. Data Sentinel: bypassed, >80% attacker-task accuracy |
| Attacker compute | **Explicitly unbounded**: "we assume the adversary has access to a large amount of computational resources… our aim is not to study how hard it is to break any particular defense, but rather whether or not any particular defense is effective or not" — following Kerckhoffs |
| Efficiency | Declared **future work**: "In the future, we believe it would be interesting to investigate to what extent it is possible to achieve strong attacks like the ones we will present here more efficiently" |
| Comparability caveat | Authors state the robustness numbers "are not necessarily comparable across defenses" because they follow each defence's original protocol |

Relevance: this is the strongest single piece of evidence that (a) adaptive-attack
evaluation is already the field's established practice, and (b) **attacker budget is
explicitly deferred** by the leading group in the area.

### 1.7 Progent (R11) — **A**, fetched in this pass

Shi, He, Wang, Li, Wu, Guo, Song (UC Berkeley + UCSB + NUS). `arXiv:2504.11703`, v2.

| Field | Record |
|---|---|
| Mechanism | Tool-level privilege control; DSL; deterministic runtime; Z3 SMT used for condition-overlap analysis |
| Claim | Reduces ASR to **0%** "while preserving agent utility **and speed**"; expresses "a strong security-utility trade-off" |
| Substrates | AgentDojo, ASB, AgentPoison |
| LLM-generated policies on AgentDojo | ASR 39.9% → 1.0%; utility 79.4% → 76.3% |
| Declared scope limits | Cannot defend attacks operating *within* least privilege (e.g. preference manipulation); cannot handle attacks targeting text output rather than tool calls |
| Cost measured? | **"Speed" is claimed preserved — a qualitative overhead claim. The magnitude is not verified here** |

Relevance: Progent is the clearest existing instance of a defence paper *co-reporting* an
overhead dimension. This materially weakens any claim that "operational cost is absent
from the literature."

### 1.8 InjecAgent (R04) and Zhan et al. adaptive attacks (R05) — **A** (abstract level, pass 1)

- **InjecAgent** (Findings of ACL 2024, `arXiv:2403.02691`): 1054 test cases, 17 user
  tools, 62 attacker tools, 30 LLM agents; ReAct GPT-4 vulnerable on 24% of cases.
  Single-turn, simulated. AgentDojo positions it as "close in spirit … but focuses on
  simulated single-turn scenarios".
- **Zhan et al., Adaptive Attacks Break Defenses** (Findings of NAACL 2025,
  `arXiv:2503.00061`): evaluates 8 defences, **bypasses all** with adaptive attacks, ASR
  consistently above 50%; code `uiuc-kang-lab/AdaptiveAttackAgent`.

Together with §1.6 these occupy the "adaptive attacks" candidate space almost completely.

---

## 2. Verifying the capability→security claim, paper by paper

The brief's A–J questions, answered per study. "Capability" is treated as **under-specified**
unless a paper defines it.

### 2.1 AgentDojo

| Q | Answer |
|---|---|
| A. Did they test capability? | Indirectly. Benign utility is measured; capability is *inferred* from it |
| B. How defined? | **Implicitly** as benign task-solve rate, and otherwise as model identity |
| C. Model size as proxy? | No |
| D. Benchmark performance as proxy? | **Yes** — benign utility on AgentDojo itself |
| E. Instruction-following measured? | No separate measure |
| F. Reasoning measured? | No |
| G. Coding measured? | No |
| H. Tool-use measured? | Only as part of end-to-end utility |
| I. Statistically tested? | **No significance test or correlation coefficient stated in the main text.** Scatter plot + 95% CIs |
| J. Causal or correlational? | **Purely correlational**, and the authors say so by naming the confound |

### 2.2 MCPTox

| Q | Answer |
|---|---|
| A. Did they test capability? | Indirectly; capability is asserted from model identity and (for Qwen3) parameter count |
| B. How defined? | **Not formally defined.** Used interchangeably with "more capable" |
| C. Model size as proxy? | **Yes**, but only within the Qwen3 family (8B vs 32B) — pass-1 |
| D. Benchmark performance as proxy? | Not stated |
| E. Instruction-following? | **Yes** — named in the abstract as the mechanism |
| F–H. | Not measured |
| I. Statistically tested? | No significance test located; the reasoning-mode contrast (+27.8% ASR) is a single ablation — pass-1 |
| J. Causal? | **Correlational.** The mechanistic sentence is an interpretation, not an intervention |

### 2.3 RAS-Eval

| Q | Answer |
|---|---|
| A. Did they test capability? | Claimed, via a scaling analysis |
| B. How defined? | **Parameter count** (log-parameters regressor) |
| C. Model size as proxy? | **Yes — explicitly** |
| D. Benchmark performance as proxy? | The **regressand** appears to be the unattacked performance score — pass-1 |
| E–H. | Not measured |
| I. Statistically tested? | Yes: R² / adj. R² / RMSE reported (pass-1 figures) |
| J. Causal? | Correlational regression across a small, single-family model set |

### 2.4 ASB — capability *not* explicitly tested (as far as verified)

13 backbones are benchmarked and results are framed as backbone-selection guidance, but no
capability construct is defined in the abstract. **Unverified** whether a formal
capability→security test exists in the body.

### 2.5 AgentDyn — capability *not* tested

AgentDyn's independent variable is **defence**, not model capability. It uses GPT-4o as
the backbone. It cannot adjudicate the capability question; it can only rule out "prior
benchmarks are saturated" as an explanation for null results.

---

## 3. Reconciliation

### 3.1 Comparison table

| Study | Model population | Capability measure | Agent architecture | Attack | Security metric | Main finding | Potential confounders |
|---|---|---|---|---|---|---|---|
| **AgentDojo** (2024) | 11 configs, 5 providers | Benign utility (implicit) | Stateful tool-calling, 4 envs, 74 tools | Indirect prompt injection (incl. adaptive "Max") | Targeted ASR | More capable models **easier** to attack ("inverse scaling law") | ASR bounded by task competence (author-named); no significance test |
| **MCPTox** (2025) | 20 settings; Qwen3 8B/32B for the scaling argument | Model identity; parameter count within one family | MCP tool metadata poisoning, single-turn | Tool poisoning (3 templates) | ASR; refusal rate | More capable models **more susceptible**, via instruction-following | Within-family only; reasoning-mode confounded with capability; no utility/cost/defences |
| **RAS-Eval** (2025) | 6 (abstract) / "eight" (§3.1.1) | log(parameters) | JSON/LangGraph/MCP, simulated + real | CWE-mapped attack tasks | TCR, TIR, TFR, perf. score, ASR | "Scaling laws held for security capabilities" — **larger models more secure** | Regressand appears to be *unattacked* performance; one family; attack tests on one model (pass-1, unconfirmed) |
| **ASB** (2024/25) | 13 backbones | Not defined | 10 scenarios, ReAct, memory | DPI, IPI, memory poisoning, PoT backdoor, mixed | 7 metrics incl. NRP (utility-security balance) | High ASR (≤84.30%); defences weak | No capability construct; ASR/utility balance only |
| **AgentDyn** (2026) | GPT-4o backbone | n/a | Open-ended, 33.33 tools, 7.10 steps | Indirect prompt injection | ASR + attacked utility (over-defence) | Defences not deployable; over-defence | Defence-side study; cannot speak to capability |
| **InjecAgent** (2024) | 30 agents | Not defined | Single-turn, simulated | Indirect prompt injection | ASR | 24% ASR on ReAct GPT-4 | Single-turn; no planning |
| **Zhan et al.** (2025) | Not a scaling study | Not defined | Multiple | Adaptive attacks | ASR | **All 8 defences bypassed**, ASR >50% | Defence-side |
| **Nasr et al.** (2025) | Varied per defence | Not defined | AgentDojo / HarmBench / OpenPromptInject | Adaptive: gradient, RL, search, human | ASR | **All 12 defences bypassed**, mostly >90% ASR | Deliberately unbounded attacker compute; not cross-defense comparable (author-stated) |

### 3.2 Could the contradictory findings be explained by the listed factors?

**Yes — for the most part. The contradiction is largely an artefact.**

**(a) Different dependent variables — the dominant explanation.**
AgentDojo and MCPTox measure **ASR under compliance-requiring attacks**. RAS-Eval's
quantitative scaling analysis appears to measure **unattacked task performance** against
log-parameters (pass-1). Scoring a benign-capability curve and calling it a "security
capability" scaling law is not the same experiment as measuring attack success. If the
pass-1 reading holds, RAS-Eval and MCPTox/AgentDojo are not in conflict: one is a
capability-scaling result, the other two are attack-susceptibility results.

**(b) ASR is a composite, not a security measure.**
AgentDojo states the mechanism explicitly: low-utility models "often fail at correctly
executing the attacker's goal, even when the prompt injection succeeds." ASR is therefore
approximately `P(adversarial compliance) × P(sufficient task competence to realise the
goal)`. A model can have lower ASR because it is *weaker*, not because it is *safer*.
Any cross-model ASR comparison — in either direction — inherits this composition.

**(c) "Capability" is at least four different constructs across these papers.**

| Construct | Where used |
|---|---|
| Parameter count | RAS-Eval; MCPTox (Qwen3) |
| General benchmark ability | AgentDojo (benign utility) |
| Instruction-following | MCPTox (abstract mechanism) |
| Reasoning (inference-time mode) | MCPTox ablation |

A relation that holds for one construct need not hold for another. Instruction-following is
plausibly *positively* associated with injection success while general competence is
*negatively* associated with ASR through the (b) channel. These can coexist.

**(d) Attack type determines the sign.**
Poisoning/injection attacks that exploit **compliance** penalise capable models.
Attacks that are **detectable or refusal-triggering** reward capable models. RAS-Eval's
CWE-mapped academic test set and MCPTox's metadata poisoning are on opposite sides of this
line. This is a *hypothesis*, not an established finding.

**(e) Model family and provider.** AgentDojo is cross-provider; the MCPTox scaling argument
and the RAS-Eval regression are both within a single family. Family and capability are
confounded in the latter two.

**(f) Metric definition.** Targeted ASR (AgentDojo), ASR over refusals (MCPTox), TCR drop
(RAS-Eval), and NRP (ASB) are not commensurable.

**(g) Defence and architecture.** AgentDojo uses a stateful 74-tool environment; MCPTox
poisons metadata on live MCP servers; RAS-Eval mixes JSON/LangGraph/MCP with real execution.
The attack surface differs enough to change measured ASR.

### 3.3 What remains genuinely unexplained

After removing (a)–(g), the following **survives as a real, unresolved question**:

> Holding attack type, architecture, task set, metric, and model family constant, and using
> a *single* capability construct, is there a monotone relationship between capability and
> attack success — and **how much of any measured relationship is attributable to the
> task-competence confound rather than to adversarial compliance?**

This is unresolved for a specific reason: the confound has been **named** (AgentDojo, 2024)
but never **measured, partitioned, or reported as an uncertainty-bearing quantity**. Every
cross-model ASR number in this literature is reported unconditionally. No study located in
this project reports the *conditional* quantity — attack success **given** that the agent
executed the tool chain required to realise the attack goal — nor sensitivity analyses for
this composition.

That is a measurement-validity gap, and it is testable.

---

## 4. Nearest existing work (and what would differentiate us)

Ranked by proximity to the candidate direction in §8.

1. **AgentDojo (R01, NeurIPS 2024 D&B).** Contributed the stateful, formally-scored agent
   security environment plus 629 cases; measured benign utility, utility under attack,
   targeted ASR; explicitly designed for adaptive attacks. **Measured** the utility-security
   Pareto frontier. **Did not measure**: the decomposition of ASR into compliance vs
   competence; defence overhead cost. **Overlap with our idea:** high — same substrate.
   **Differentiator:** we would not build an environment; we would re-analyse and condition
   its outcomes, and add a capability ladder with defined parameter counts.
2. **MCPTox (R06).** Contributed the first large-scale tool-poisoning benchmark. **Did not
   measure** utility, cost, defences, or multi-turn behaviour; its scaling argument is
   within-family and reasoning-confounded. **Overlap:** the capability question.
   **Differentiator:** we would not advance a new capability claim but test the *validity*
   of the ASR estimand.
3. **RAS-Eval (R03).** Contributed a CWE-mapped, dual-execution (simulated/real) benchmark.
   **Differentiator:** its scaling claim is the thing to *test*, not to extend.
4. **ASB (R02, ICLR 2025).** Contributed the NRP utility-security co-metric and the widest
   attack/defence × backbone sweep. **Did not** define capability. **Overlap:** moderate.
   **Differentiator:** ASB's NRP is a *score*; our contribution would be an *estimand* with
   an identified confound.
5. **AgentDyn (R08, 2026).** Contributed over-defence measurement and the deployability
   critique. **Differentiator:** complementary; it fixes the *task-realism* axis, we would
   fix the *measurement* axis.
6. **Nasr et al., The Attacker Moves Second (arXiv:2510.09023).** Contributed decisive
   evidence that adaptive attacks break 12 defences. **Explicitly did not** study attack
   cost. **Overlap:** the attacker-budget axis, if pursued.
7. **Zhan et al. (R05, Findings of NAACL 2025).** Adaptive attacks break 8 defences.
   **Overlap:** closes the "adaptive attacks" candidate.
8. **Progent (R11).** Contributed deterministic privilege control and a security-utility
   trade-off point (ASR 39.9%→1.0% with utility 79.4%→76.3% under LLM-generated policies).
   **Overlap:** the cost axis, weakly.
9. **Kirgis et al. (R09).** Log-analysis methodology; reports pass^5 under-elicitation near
   50% on tau-Bench Airline. **Overlap:** the reproducibility axis — and it is the strongest
   available lever there.
10. **IETF draft-han-bmwg-agent-security-benchmark-00 (R29).** 55 metrics across 4
    dimensions. **Overlap:** standardisation of metric vocabularies. Anyone proposing a new
    metric surface must reconcile with this draft.

---

## 5. Is operational cost a genuine gap? — **claim NOT confirmed**

The pass-1 claim was that "operational cost" is the only comparison column with no "yes"
anywhere. On primary-source reading, that claim **does not survive as stated.**

Evidence found:

| Evidence | Source | Verified? |
|---|---|---|
| Estimated cost of running the full 629-case suite on GPT-4o, reported in Appendix D | AgentDojo, checklist 3(d) | **Yes (this pass)** |
| Defence preserves "utility **and speed**" | Progent, abstract & §1 | **Yes (this pass)** |
| Prompt-injection detector has "too many false positives" and significantly degrades utility | AgentDojo §4.3 | Yes |
| Attack-induced utility loss 15–20% under attack, reported per defence | AgentDojo §4.3 | Yes |
| Latency / token budget as a named dimension of attack design | Nasr et al. (compute-budget framing of attacks); GCG's 500 steps × 512 queries × 20-token suffix quoted in their footnote | Yes |
| Token-cost figure for a defence (14605 tokens) surfaced in a survey | R22 (survey) | **No — primary source unread; NOT usable** |
| 55 metrics across 4 dimensions including deployment/operational measures | IETF draft-han-bmwg (R29) | Draft read in pass 1; **cost coverage not confirmed** |

**Conclusion.** Any credible cost claim must be narrowly stated. The defensible residual is:

> *Per-defence, per-model operational overhead (tokens, latency, extra model calls, tool
> calls) is reported qualitatively or sporadically — Progent claims speed is preserved;
> AgentDojo reports the one-off cost of running its own suite — but no located study
> co-reports a systematic overhead profile alongside security and utility for a set of
> defences across a set of models.*

That residual is a **measurement-instrumentation gap (class B/C)**, not an untouched
research area. It is also the weakest of the candidates: a "cost leaderboard" is not on its
own a research contribution, and the risk that a 2026 defence paper already reports
overhead is high. **Do not lead with cost.**

---

## 6. Is adaptive attacker budget a genuine gap? — **weakly studied, but publicly staked**

What exists:

| Study | Budget-like variable already varied? |
|---|---|
| AgentDojo (R01) | Partly: a single "Max" adaptive attack over 4 candidate injections (+10% ASR) |
| Zhan et al. (R05) | Yes, in practice: adaptive attacks bypass all 8 defences |
| Nasr et al. (R48/2510.09023) | **Explicitly waived**: adversarial compute is assumed unbounded, and *attack efficiency is declared future work* |
| AgentDojo future work | Acknowledged gap: constraints on injection "length or format" to "better capture the capabilities of realistic adversaries" |
| GCG-derived attacks | Query/step cost is documented (500 steps × 512 queries/step, 20-token suffix) but not swept as an independent variable |

So the field has **not** produced a systematic attacker-budget→ASR curve. But:

1. The leading group in adaptive-attack evaluation (Nasr/Carlini/Tramèr et al.) has publicly
   named attack efficiency as the next question. A named future-work item from a strong
   group is a *crowded* gap — likely already in flight.
2. AgentDojo's authors have also pre-registered attacker-constraint modelling as their own
   future work.
3. The direction is a natural extension of R48, and any result would be calibrated against
   their unbounded-budget baselines.

**Classification: C (weakly studied) — but with high competition risk.** Viable only as a
*secondary axis* inside a study whose primary claim lies elsewhere, or as a distinctly
scoped formulation (e.g. budget as it interacts with *model capability*, which neither R48
nor MCPTox addresses).

---

## 7. Gap decision tree — classification of the 10 candidates

Scale: **A** substantially solved · **B** partially studied, still open · **C** weakly
studied · **D** potentially novel · **E** cannot determine.

| # | Candidate | Class | Evidence |
|---|---|---|---|
| 1 | Multi-model evaluation | **A** | ASB 13 backbones; AgentDojo 11 configs; MCPTox 20 settings; InjecAgent 30 agents. Near-universal. Not a contribution |
| 2 | Adaptive attacks | **A** | AgentDojo built for it (2024); Zhan et al. bypass 8 defences; Nasr et al. bypass 12 defences, mostly >90% ASR. Also named "adaptive" in R05/R48 titles |
| 3 | Reproducibility | **B** | AgentDojo reports 95% CIs and releases code; but commercial-model non-determinism (R25, unverified) and Kirgis et al.'s pass^5 ≈ 50% under-elicitation (R09) show the problem is live. Partially studied; still open — but crowded |
| 4 | Operational cost | **B/C** | §5. Sporadic/qualitative (Progent "speed"; AgentDojo suite-run cost). Not a clean gap; not a standalone contribution |
| 5 | Security–utility trade-off | **A** | AgentDojo Pareto frontier (2024); ASB's NRP metric; Progent's named trade-off; AgentDyn's over-defence. Substantially solved |
| 6 | Attacker budget | **C** | §6. No systematic budget sweep located; explicitly deferred as future work by R48 and partially by AgentDojo. High competition risk |
| 7 | **Capability–security relationship** | **B** | Claimed in both directions (§3). Confound named but **never measured or partitioned**. No orthogonal manipulation of capability located; no single capability construct held fixed across attack types |
| 8 | Defense overhead | **B** | Progent's speed claim plus AgentDyn's over-defence utility costs. No systematic overhead profile located. Subsumed by #4 |
| 9 | Cross-model generalisation | **B/C** | ASB across 13 backbones; MCPTox cross-model; but no located study tests attack/defence transfer with **family and capability jointly controlled** |
| 10 | **Measurement validity of ASR (the competence confound)** — discovered in this pass | **B/D** | AgentDojo states the confound; no located study quantifies it, conditions on it, or reports sensitivity analyses. Highest defensibility of the set |

**Candidates to drop now:** 1, 2, 5 (class A). **Candidates to demote:** 4 and 8 (cost),
6 (attacker budget) — viable only as secondary axes.

---

## 8. A defensible study design

Proposed only because §7 leaves a residual that survives §3.2's explanations, and because
it is **not** a new benchmark.

### 8.1 Question

> To what extent is the observed association between model capability and measured agent
> attack success rate an artefact of ASR being jointly determined by adversarial compliance
> and task-execution competence?

### 8.2 Design

| Element | Specification |
|---|---|
| **Independent variable** | Capability, operationalised through **two orthogonal channels**: (i) a *within-family parameter ladder* with published parameter counts (open-weight, ≥4 rungs), and (ii) an *inference-time* manipulation (reasoning enabled/disabled, or reasoning-token budget) applied **within** each rung. Channel (ii) exists precisely to break the family↔capability confound that invalidates both MCPTox's and RAS-Eval's scaling arguments |
| **Second independent variable** | Attack **type**, dichotomised as *compliance-exploiting* (indirect prompt injection / tool poisoning) vs *detection-refusal-triggering* injections. This tests the §3.2(d) sign hypothesis |
| **Dependent variables** | (1) benign utility; (2) utility under attack; (3) targeted ASR — **reported unconditionally**; (4) **conditional ASR**: attack success *given* the agent executed the tool chain required for the attacker's goal; (5) tool-execution competence on matched benign controls; (6) per-case cost (tokens, wall-clock, tool calls) |
| **Units of analysis** | (user task, injection task, model configuration, seed) quadruples; ≥5 seeds per cell |
| **Controlled** | Task set, injection set, tool surface, framework, system prompt *strings*, decoding temperature, environment version — all held identical across rungs |
| **Manipulated** | Capability channel; attack type; injection position (beginning/end of tool response) |
| **Measured** | All six dependent variables above; plus κ-style inter-scorer agreement for any judged outcome |
| **Primary hypothesis (H1)** | The unconditional capability–ASR association is non-null, **and** the conditional association is materially weaker — i.e. a substantial fraction of the apparent capability effect is carried by the competence channel |
| **Falsifier** | The conditional association remains positive, non-trivial, and its CI excludes the competence-explained portion — i.e. capability genuinely raises adversarial compliance beyond what competence explains. (Equally: the competence channel explains ≈0% of variance) |
| **Secondary hypothesis (H2)** | The sign of the capability–ASR relation differs between compliance-exploiting and refusal-triggering attacks |
| **Design features that make H1 credible** | Pre-registered estimand and stopping rule; ordinal competence-matching instead of post-hoc conditioning; E-value-style sensitivity analysis for unmeasured confounding; reuse of AgentDojo/InjecAgent case sets rather than authoring new ones |

### 8.3 Why this is not merely "interesting"

It is falsifiable, it targets a *named but unquantified* confound, and — unlike a new
benchmark — it produces a quantity (the conditional estimand) that every prior cross-model
security ranking can be re-expressed in. It also fails informatively: if H1 is false, the
field's inverse-scaling findings become substantially stronger than they currently are.

---

## 9. Can our four available models support this? — **No, not for the primary claim**

Available: DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4.

### 9.1 What is verified about them

**Essentially nothing at vendor-source level.** All four carry label **B/C** in
`sources.csv` (R35–R38):

| Model | Verified status |
|---|---|
| DeepSeek V4 / V4.1 Flash | `B/C`. The ".1 Flash" designation is **unconfirmed at a vendor source**. The "1M-token context" claim traces to tech-media/aggregator pages. Vendor spec page still required |
| MiMo-V2-Flash | `B/C`. 256K context, hybrid thinking toggle, function calling reported. A "2.6" generation appears in vendor release documentation but was **not fetched** |
| GLM-5 | `B/C`. GLM-5 (2026-02-11, MIT-licensed weights reported); 5.1/5.2 documented. A **5.3 Flash variant is unconfirmed at a vendor source** |
| Solar Mini 4 | `B/C`. ~35B MoE / 3B active / 524K context from aggregator pages and API docs. Vendor launch note **not fetched** |

**Do not build the design on these figures.**

### 9.2 Scientific verdict

**Inadequate for the primary claim, for four independent reasons:**

1. **No capability spread.** All four are Flash/mini tier. A capability ladder requires
   rungs that differ in capability, not four peers.
2. **Provider is perfectly confounded with everything else.** Three Chinese vendors + one
   Korean; no Western frontier model. Any "capability" effect is inseparable from
   tokenizer, alignment pipeline, system-prompt handling, refusal training, and API
   implementation. This is the same defect that invalidates MCPTox's and RAS-Eval's scaling
   arguments, reproduced by us.
3. **No verified parameter counts.** RAS-Eval's own construct — log(parameters) — is
   unavailable. A MoE model's "active parameters" is a further definitional problem.
4. **Version pinning is not demonstrated.** R25's reproducibility concern (commercial
   inference non-determinism) applies directly; without a vendor-documented frozen revision
   ID, results are not reproducible.

**What they *are* adequate for:**

- A **methods pilot**: variance estimation, per-case cost instrumentation, κ calibration
  for judged outcomes, and a power analysis for the real study. Useful, not evidentiary.
- A **within-model inference-time capability manipulation** (reasoning on/off), which
  reproduces MCPTox's own manipulation and would let us test whether *their* effect
  survives competence-partitioning — but this is an inference-time-compute construct, not
  model capability, and must be labelled as such.
- A genuine **cross-provider robustness check** at the *Flash tier only* — a legitimate
  small contribution if reported as such.

**Requirement to proceed with the primary claim:** add ≥4 rungs of **one open-weight
family with published parameter counts** (run locally), plus fixed decoding and a frozen
revision for every commercial model used. Local open weights also solve the pinning and
cost problems simultaneously.

---

## 10. Final research decision

### A. What we now know with high confidence

1. **Inverse scaling in agent prompt injection is not new.** AgentDojo (NeurIPS 2024 D&B)
   already reported, in 2024: *"more capable models tend to be easier to attack, a form of
   inverse scaling law"*. MCPTox (2025) reports the same direction for tool poisoning.
2. **The authors of the inverse-scaling result named its confound themselves:** low-utility
   models "often fail at correctly executing the attacker's goal, even when the prompt
   injection succeeds."
3. **ASR is a composite quantity** — adversarial compliance × task-execution competence —
   and is reported unconditionally throughout the literature.
4. **"Capability" denotes at least four different constructs** across these papers
   (parameter count, benign benchmark ability, instruction-following, reasoning mode). No
   paper located holds one construct fixed while varying attack type.
5. **RAS-Eval's headline claim is not, as verifiable, a security-scaling result.** Its
   quantitative scaling analysis appears to regress *unattacked* performance on
   log-parameters within one family. The apparent contradiction is therefore largely an
   artefact of comparing a capability curve to attack-susceptibility curves.
6. **Adaptive attacks are the established standard**, not an open gap: Nasr et al. bypass
   12 defences at mostly >90% ASR where near-zero was originally reported.
7. **Multi-model evaluation and the security–utility trade-off are saturated** as novelty
   claims (ASB's NRP, AgentDojo's Pareto frontier, AgentDyn's over-defence).
8. **Operational cost is partially represented** (AgentDojo's suite-run cost; Progent's
   "speed" claim), so it is not the clean gap pass 1 suggested.

### B. What remains uncertain

1. Whether RAS-Eval's full text contains a *separate* attacked-security scaling analysis.
   **Both fetches were truncated** — this is the highest-priority re-verification.
2. Whether ASB formally tests a capability→security relation in its body.
3. The magnitude of Progent's speed overhead (claimed, not quantified here).
4. Whether any 2026 paper already partitions the competence confound. Not located — which
   is **not** the same as not existing.
5. Whether MCPTox's inverse-scaling result survives removing the reasoning-mode confound.
6. Vendor-level facts about all four of our models (parameters, context, versions).

### C. Apparent gaps that are no longer viable

- **Multi-model evaluation** — standard practice.
- **Adaptive attacks** — established practice with a definitive recent demonstration.
- **Security–utility trade-off** — well instrumented (NRP, Pareto frontiers, over-defence).
- **A new prompt-injection benchmark.** AgentDojo, AgentDyn, ASB, InjecAgent, RAS-Eval and
  IETF's metric draft collectively crowd this out; AgentDyn's critique is specifically that
  the community over-produces defences (79% of effort). A new environment is the wrong shape.
- **Operational cost as a standalone contribution** — partially covered; low novelty.
- **Attacker-budget sweeps as a standalone contribution** — weakly studied but explicitly
  staked as future work by the strongest group in the area, and by AgentDojo's authors.

### D. The 1–3 gaps that remain genuinely promising

1. **Measurement validity of ASR under capability variation** (the competence confound).
   Most defensible: named-but-unquantified, portable to existing benchmarks, falsifiable.
2. **Attack-type dependence of the capability–security sign** — the *compliance-exploiting
   vs. refusal-triggering* distinction. Testable and, if it holds, reconciles the literature
   without requiring any new benchmark.
3. **Attacker budget × model capability interaction** — a distinctly scoped formulation of
   the attacker-budget axis that neither Nasr et al. (unbounded budget, single defence
   configuration) nor MCPTox (no budget variation) examines. Secondary.

### E. The single recommended question

> **To what extent is the measured relationship between model capability and agent attack
> success rate an artefact of ASR being jointly determined by adversarial compliance and
> task-execution competence — and does the sign of that relationship depend on whether the
> attack exploits compliance or triggers refusal?**

### F. Why this is not a reimplementation

- It **does not build an environment.** AgentDojo, InjecAgent and RAS-Eval case sets can be
  reused; the contribution is an analysis and a targeted experiment on top of them.
- **AgentDojo** established the confound qualitatively and reported ASR unconditionally.
  **MCPTox** reported an inverse-scaling claim whose own mechanism (instruction-following)
  is a component of capability, within one family, with reasoning mode confounded.
  **RAS-Eval** reported a scaling law for what appears to be a benign-capability measure.
  **ASB** reported a balance *score*. **AgentDyn** reported defence deployability.
  None of them reports a **conditional** attack-success estimand with uncertainty, or a
  capability ladder in which family is controlled and attack type is varied.
- The deliverable is a **quantity**, not a leaderboard: it lets every prior cross-model
  security ranking be re-expressed, and it can *strengthen* the inverse-scaling finding if
  the confound turns out to explain little.

### G. The experiment that would provide the strongest evidence

The §8 design, reduced to its decisive core:

1. ≥4 rungs of one open-weight family with published parameter counts, decoding fixed;
2. two attack types (compliance-exploiting vs. refusal-triggering) on identical task and
   injection sets;
3. per-case joint outcomes, so that unconditional ASR and **conditional ASR | executed
   tool chain** can be reported side by side with CIs;
4. ordinal competence-matching plus a sensitivity analysis (E-value) for residual
   confounding;
5. ≥5 seeds; pre-registered estimand.

The decisive figure is a single panel: unconditional capability–ASR slope versus conditional
capability–ASR slope, with overlapping CIs indicating that capability's apparent security
effect is carried by competence.

### H. The most likely reviewer objection

> *"This confound is already known — AgentDojo said it in 2024. You have re-stated a known
> limitation and re-analysed an existing benchmark. And you cannot make capability claims
> from four Flash-tier vendor APIs whose sizes you cannot verify."*

A second, closely related objection:

> *"If the confound explains little, your contribution is a null result; if it explains a
> lot, it is a correction to a two-year-old footnote."*

### I. What evidence would answer those objections

1. **Evidence that the confound is consequential, not cosmetic.** Re-express at least one
   published cross-model security ranking under the conditional estimand and show that the
   ranking **reverses, collapses, or materially re-orders**. "Known but inconsequential" is
   answered only by a change in conclusions — not by restating the confound.
2. **An uncertainty-bearing decomposition.** Report both slopes with CIs and the share of
   the association attributable to the competence channel, plus an E-value. A point estimate
   alone will be dismissed as a re-reading.
3. **A capability ladder with verified parameter counts**, at least one family run locally,
   and every commercial model pinned to a documented frozen revision. This directly answers
   the model-set objection and simultaneously fixes reproducibility.
4. **A pre-registered falsifier** — a stated outcome under which we would report that
   capability genuinely, causally raises susceptibility. Pre-commitment is the strongest
   available defence against the "null-result-as-contribution" objection.
5. **Reconciliation with the IETF metric draft (R29)** so the new estimand is stated in the
   vocabulary the standards track is already using.

---

## Appendix: sources newly verified or re-labelled in this pass

| ID | Change |
|---|---|
| R48 | **C → A.** Verified as Nasr, Sitawarin, Hayes, Schulhoff, Ilie, Pluto, Song, Chaudhari, Shumailov, Thakurta, Xiao, Carlini, Terzis, Tramèr, *"The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"*, `arXiv:2510.09023`. Note the **title differs** from the pass-1 placeholder |
| R01 | Notes updated: verbatim inverse-scaling claim and the authors' own confound statement; tool count 74 (Table 1 rows) vs 70 (caption) |
| R11 | Notes updated: "preserving agent utility and speed"; LLM-generated-policy numbers (ASR 39.9%→1.0%, utility 79.4%→76.3%) |
| R02 | Notes updated: NRP utility-security metric confirmed in abstract |
| R03 | Notes updated: verbatim scaling-law sentence; flagged as the item requiring re-verification |
| R06 | Notes updated: verbatim inverse-scaling sentence and its named mechanism |
| R08 | Notes updated: Table 1 statistics; abstract/Figure-1 defence-count inconsistency (ten vs nine) |
| R51 | **New.** McKenzie et al., *Inverse Scaling: When Bigger Isn't Better*, `arXiv:2306.09479` — label **B** (surfaced only via AgentDojo's reference list; not fetched) |
