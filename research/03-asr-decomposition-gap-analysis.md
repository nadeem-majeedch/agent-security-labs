# Is the "ASR conflates attack influence with task competence" gap real?

**Status:** working analysis, not a paper. Pass 3 of the AgentSec Lab landscape work.
**Date:** 2026-09-25.
**Extends:** `research/01-landscape-and-gap-analysis.md`, `research/02-capability-vs-security-analysis.md`.

---

## 0. Headline finding, stated first

The proposed measurement problem — *observed attack success approximately decomposes into
attack influence and agent task/execution competence* — has been **identified, formalised,
and in substantial part measured** by existing work. It is no longer a novel observation.

Three findings drive this conclusion, all verified at primary source in this pass:

1. **Pathade, Pawar & Patil, "Attack Success Rate Is Not a Number: On Measurement Validity
   in Agentic AI Security Evaluation"** (`arXiv:2609.25173v1`, posted ~2026-09-21, i.e.
   **days before this analysis**) argues that ASR "is not a single quantity but a family of
   metrics parameterized by six design choices that papers seldom specify and never hold
   constant across the literature," and backs this with a 259-paper meta-analysis, a power
   analysis, and a ten-item reporting checklist. Its checklist item 10 is verbatim:
   *"A defense can drive ASR toward zero by refusing broadly, and without a paired utility
   number a reader cannot distinguish that from a real defense."*
2. **REDAgentBench** (`arXiv:2608.10669`) states that "existing evaluations often reduce
   agent safety to a single attack success rate (ASR), **collapsing exposure, execution,
   observation, and adjudication**," and names a **Recognition–Execution Gap**.
3. The specific remedy proposed in the brief — condition attack success on task success —
   **already exists as a named metric**: *Conditional Attack Success Rate (C-ASR)*, and
   *Task-Success-Conditional Attack Success Rate*.

Classification (§5): **B — substantially addressed** as a conceptual and formal matter;
**C — partially addressed** as an empirical-magnitude matter. It is not viable as a
standalone novelty claim in its current framing.

Everything below is the evidence chain. Verification labels are as in previous passes:
**A** read at primary source · **B** search-result level · **C** unverified.

---

## 1. Defining the measurement problem

### 1.1 The seven quantities

Let an evaluation unit `u` be a (user task, injection payload, model configuration, seed)
tuple. Let a trajectory `τ` be the full record of the agent's actions and environment state
changes. Write `A(τ)` for the multiset of tool calls issued, and `S(τ)` for the final
environment state.

| Symbol | Name | Operational definition | Observable? |
|---|---|---|---|
| **E** | **Attack injection success / exposure** | The adversarial content was present in the agent's context at some step, *and* the agent read or received it (e.g. the poisoned tool metadata was loaded, or the injected record was retrieved). | Observable from the trace + payload position **if** the scaffold logs retrieved content. Often only inferable. |
| **I** | **Adversarial influence** | The agent's action distribution shifted toward the attacker's intent *because of* `E`. Counterfactually: the agent would not have taken the attacker-aligned action had the payload been absent. | **Latent.** Not directly observable. Requires either a counterfactual run or a proxy. |
| **C** | **Instruction-following under attack** | The agent demonstrably treated the injected text as an instruction addressed to it (e.g. explicitly acknowledges it, or reorders its plan to accommodate it) rather than as inert data. | Observable only via a text oracle; noisy. |
| **K** | **Agent task competence** | Probability the agent completes *the benign user task* for `u` in the absence of any attack. | Observable (benign-control run + task oracle). |
| **X** | **Tool-execution competence** | Probability the agent can produce the *action sequence the attacker's objective requires*, given it intends to. Generally a function of `K` and of whether the required tools are callable. | Observable via tool-call log + a per-tool success flag. |
| **O** | **Attack objective completion** | The attacker's stated goal holds in the environment state: `O = 1[S(τ) ⊨ G_attack]`. | Observable given a *state* oracle. |
| **ASR** | **End-to-end attack success rate** | `ASR = (1/|U|) Σ_u O(u)`. | Observable. |

Two distinct "attack success" notions must be kept apart, because they are what actually
collide across the literature:

- **ASR-targeted** = `P(O)` — the attacker's goal achieved (AgentDojo, ASB, RAS-Eval §3.1.2).
- **ASR-untargeted** = `1 − P(user task solved ∧ no adversarial side effect)` — i.e. *any*
  deviation. AgentDojo reports this as the complement of "utility under attack."

### 1.2 On the proposed decomposition

The brief proposes:

```
P(O) ≈ P(agent follows adversarial instruction) × P(agent executes required action | follows)
```

**This multiplication is not a hypothesis — it is the chain rule and is always exactly true**:

```
P(O) = P(I) · P(X ∧ C | I)        (exact, for well-defined I)
```

provided `I` is a well-defined event. Independence is *not* assumed and is *not* needed.
The reason the brief correctly warns "do NOT assume independence" is the inverse of the
real problem: **the identity is trivially true, and that triviality is precisely why this
cannot be the contribution.**

The genuine difficulty is that **`I` is latent**. Every decomposition of `P(O)` is a
factorisation over quantities the experimenter cannot observe directly. So the research
problem is *not* "decompose ASR"; it is:

> **Which of the observable quantities (`K`, `X`, `O`) can be used to identify the
> unobservable `I`, with what bias, and does the resulting correction change any published
> cross-model or cross-defence ordering?**

That is an **identification / measurement-validity** problem, not an arithmetic one. And
Pathade et al. (2026) already frame the field's problem in exactly these terms — as
"measurement validity," with "six design choices" playing the role of the unobservable
degrees of freedom.

### 1.3 Conditional probabilities vs causal models

Conditional probabilities are **not** the right tool on their own, and this matters for §7.

- `P(O | X = 1)` — conditioning on observed execution success — is estimable and useful, but
  **conditioning on a post-treatment variable** induces selection bias: `X` is affected by
  `I` itself, and stratifying on it can *create* an association between `I` and `O` where
  none exists (the classic collider/selection problem). Reporting C-ASR is therefore not
  automatically an improvement over ASR; it is a *different* estimand with its own bias.
- Isolating **`I`** requires a **causal** quantity: an intervention on payload presence
  (the counterfactual in §7, Control A vs D), or a mediation analysis with explicit
  assumptions.
- The honest formulation is a **principal-stratification / mediation** one: define
  compliance as a potential outcome under payload-present vs payload-absent, and report the
  *natural indirect effect* (the share of `P(O)` mediated by competence) with a sensitivity
  analysis, rather than a product of two marginal rates.

**This is the only framing in which the idea survives as non-trivial** — and it is
substantially the framing Pathade et al. have already adopted for the field, minus the
capability channel specifically.

---

## 2. Prior work: does the literature already do this?

### 2.1 The decisive paper

**R52 — Pathade, Pawar & Patil, "Attack Success Rate Is Not a Number: On Measurement
Validity in Agentic AI Security Evaluation"** (`arXiv:2609.25173v1`, ~2026-09-21,
Independent Researchers). **Verified at primary source (A).**

| Element | Content |
|---|---|
| Core claim | ASR "is not a single quantity but a family of metrics parameterized by six design choices that papers seldom specify and never hold constant across the literature" |
| Formalisation | `ASR̂ = (1/|U|) Σ_{u∈U} O(τ_u)`, with `U` the evaluation set, `τ_u ∼ π_θ(·|u)` a sampled trajectory, `O: τ ↦ {0,1}` a success oracle. Argues all four components are researcher-chosen in the agentic setting |
| Six axes | **A1** unit of analysis (injection vs task vs trajectory — a factor-`k` gap from identical behaviour); **A2** success oracle (string/regex, LLM judge, environment state, human); **A3** trials & non-determinism; **A4** attacker adaptivity; **A5** attacker knowledge of the defence; **A6** binarisation of partial success |
| Meta-analysis | 259 agentic-security papers on arXiv, 2025-02-27 → 2026-09-17 (43 from 2025, 216 from 2026); 1,168 records → 911 unique → 550 candidates → 535 full texts → 259 included |
| Measurement-validity results | Variance/CI on the attack metric 23.9%; repeated runs 20.5%; **neither variance nor repeated runs 65.3%** (hand-coded random sample of 50: 58.0%, 95% Wilson CI 44.2–70.6); any decoding info 30.9%; LLM judge in ≥24.7%, of those 29.7% report any human-agreement check; adaptive attacker 30.5%; **attack budget stated 10.8%**; attacker knowledge of defence stated 16.2%; partial success addressed 2.3%; **benign-task utility reported 37.8%**; code released 65.3% |
| Power analysis | At 80% power, α=0.05, a 100-instance benchmark cannot resolve differences below ≈**18.2 percentage points**; two defences truly separated by 5 points are ranked backwards ≈**21%** of the time, by 2 points ≈38% |
| Oracle analysis | `p̂ = p(1−β) + (1−p)α`; ordering inverts when `(1−β_B)/(1−β_A) < p_A/p_B`. Reports honestly that this is demanding, and that the real issue is that judge calibration is unmeasured |
| Checklist item 10 | *"Utility. Report benign-task success under the same defense. … A defense can drive ASR toward zero by refusing broadly, and without a paired utility number a reader cannot distinguish that from a real defense."* |
| **Explicitly not done** | *"We have not run defenses end to end, so we report no empirical ranking inversion; that experiment is the natural next step and needs model access we did not have."* Also: no artifact repository; checklist "proposed, not validated" |
| Lineage | Positions itself on the adversarial-robustness correction (Athalye 2018; Tramèr 2020; **Carlini et al. 2019, "On Evaluating Adversarial Robustness"**) and the jailbreak correction (**StrongREJECT**) |

**What this means for us.** Pathade et al. have taken the *general* measurement-validity
claim and made it a measured, published result. Their six axes, however, **do not include
the capability/competence channel**. Adjacent to ours: A6 (partial-success binarisation,
which covers "recognition without execution" and "refused-then-retried") and checklist item
10 (paired utility). But "ASR is inflated by the model's own competence" is **not one of the
six axes** — it is a seventh candidate axis sitting next to a framework that exists.

### 2.2 The closest structural decomposition

**R53 — Chen et al., REDAgentBench: Executable Red Teaming and Faithful Measurement of LLM
Agent Systems** (`arXiv:2608.10669`, 2026-08-11). Verified at abstract level (A).

| Element | Content |
|---|---|
| Direct statement | "existing evaluations often reduce agent safety to a single attack success rate (ASR), **collapsing exposure, execution, observation, and adjudication** and potentially conflating actual violations with evidence visibility" |
| Method | Derives attacks from explicit safety constraints; runs them in isolated service sandboxes; **verifies harmful effects from service receipts and final-state changes** |
| Scale | 1,661 cases, five service surfaces; six models, three agent harnesses |
| Result | Macro-average ASR **65.69%**; "**reported ASR varies with harness and evidence view**, while evaluation-context disclosure changes execution behavior" |
| Named gap | In a state-grounded diagnostic cohort, **almost one in five confirmed violations with resolved action anchors occurs *after* the agent states the relevant constraint or risk** — the **Recognition–Execution Gap** |
| Intervention | Training-free policy reminder reduces confirmed violations by **>70 percentage points** in matched replay |

This is the closest structural match to the proposed idea. Their decomposition
(**exposure → execution → observation → adjudication**) is a stage decomposition of attack
success, and the **Recognition–Execution Gap** is precisely "the agent was influenced but
did not, or could not, act." Note also that they identify a *third* channel the brief did
not enumerate: **evidence visibility / adjudication** — reported ASR depends on what the
evaluator can observe. That is a confound on top of ours.

### 2.3 The proposed remedy already exists as a named metric

This is the most consequential single finding for §6.

Searching terminology variants produced direct evidence that "condition attack success on
task success" is **established practice with established names**:

| Terminology | Source | Level |
|---|---|---|
| **Task-Success-Conditional Attack Success Rate** — section titled "4 Task-Success-Conditional Attack Success Rate": *"In addition to reporting ASR over all evaluated cases, we also report a task-success-…"* | Jin et al., **SkillSafetyBench**, `arXiv:2605.12015v2` | **A** (the section title verified in the search index; full text truncated before that section) |
| **Conditional Attack Success Rate (C-ASR)** and **Conditional Refusal Rate (C-RR)**, reported "to account for comprehension failures" | ACM Multimedia 2026 technical programme entry; a VLM-safety benchmark | **B** |
| "attack success rate **conditional on** agent navigation to a declared trap URL" | `arXiv:2606.00497` | **B** |
| "the **conditional attack-success rate** (ASR), defined as the percentage of scored…" | **HarnessSafe**, `arXiv:2608.06984` | **B** |

So the answer to the brief's §6 instruction *"Determine whether similar metrics already
exist. If they do, use the established terminology instead. Do not invent terminology
unnecessarily"* is unambiguous: **they exist, and the established term is C-ASR /
task-success-conditional ASR.** The candidate names AIR / AIC / TES / AOC in the brief
should be discarded.

### 2.4 The capability channel is already built into a major metric

**R14 — AgentHarm** (`arXiv:2410.09024v3`, **accepted at ICLR 2025**). Abs page fetched
(A); venue now verified, upgrading R14 from label B.

- 110 explicitly malicious agent tasks (440 with augmentations), 11 harm categories.
- Verbatim: *"In addition to measuring whether models refuse harmful agentic requests,
  **scoring well on AgentHarm requires jailbroken agents to maintain their capabilities
  following an attack to complete a multi-step task**."*
- Finding (3): *"these jailbreaks enable coherent and malicious multi-step agent behavior
  and **retain model capabilities**."*

This is the capability-mediation condition **enforced inside the benchmark's own success
criterion**. An AgentHarm agent that complies with the malicious request but cannot execute
the multi-step task does **not** score as a success. That is the proposed decomposition,
implemented as a benchmark design decision, published at ICLR 2025 — and Pathade et al.
characterise AgentHarm as the exception that "grade[s] partial harm rather than
binarizing."

### 2.5 The phenomenon was named in the jailbreak literature first

**R55 — Souly et al., A StrongREJECT for Empty Jailbreaks** (`arXiv:2402.10260v2`,
NeurIPS 2024 Datasets & Benchmarks). Abs page fetched (A).

- *"it is perhaps more common than not for jailbreak developers to substantially exaggerate
  the effectiveness of their jailbreaks"*; *"existing evaluation methods significantly
  overstate jailbreak effectiveness compared to human judgments."*
- **The mechanism, verbatim: *"a surprising and novel phenomenon that explains this
  discrepancy: jailbreaks bypassing a victim model's safety fine-tuning tend to reduce its
  capabilities."***

This is the capability-mediation effect, named and measured in February 2024 — one day
before AgentDojo's arXiv posting. Note the sign: StrongREJECT found that attack success
*overstates* effectiveness because a compliant model may be capability-degraded; AgentDojo
found ASR *understates* vulnerability for weak models because they cannot execute the
attacker's goal. **These are the two directions of the same confound**, in the two
sub-fields.

### 2.6 The agent-side confound was named in 2024

**R01 — AgentDojo** (§4.1, full text read in pass 2, **A**):

> "We find that more capable models tend to be easier to attack, a form of inverse scaling
> law… **This is a potentially unsurprising result, as models with low utility often fail at
> correctly executing the attacker's goal, even when the prompt injection succeeds.**"

That sentence *is* the proposed hypothesis, stated as a caveat in a NeurIPS 2024 D&B paper.

### 2.7 RAS-Eval: now fully verified, and it confirms rather than contradicts

Full text retrieved in this pass (**A**, previously truncated). Relevant to the audit and
to the pass-2 caveat:

- **Metrics are defined formally (Eq. 2–8).** TCR (all human-annotated required tools
  invoked, as a subsequence, in order); TIR (subset invoked or wrong tools); TFR (empty
  sequence or `len(O) > max_length`); performance score
  `= n_correct / (n_correct + n_wrong + n_lack)`; ASR.
- **ASR definition (Eq. 7–8), verbatim:** *"An attack was deemed successful if the
  attacker's target tool τ_e appeared in the agent's final tool invocation sequence **and**
  the tool's output r contained the attacker's desired content r^e."*
  → **RAS-Eval's own ASR is defined on the agent's tool-invocation sequence.** It therefore
  *structurally requires tool-execution competence* to register a success. RAS-Eval's
  headline metric is an instance of the very confound under discussion, and this is not
  discussed in the paper.
- **Pass-2 caveat resolved.** §3.2.2 "Verification of Scaling Law (RQ2)" is framed as
  *"If models of varying scales exhibit this trend on our benchmark, it indicates the
  benchmark's strong discriminative power"* — i.e. it is **a benchmark-validity check, not
  a security-scaling claim**. It regresses *performance score* (benign) on log(parameters)
  for Qwen-series models only, reporting `SSE 68.0004, R² 0.9051, adj R² 0.8577,
  RMSE 5.8310`. The abstract's sentence *"scaling laws held for security capabilities"* is
  therefore a **mischaracterisation of RQ2**. Pass-2's reading is confirmed.
- **Verbatim:** *"We conducted attack task tests exclusively on the GLM4-Flash model."*
  Confirmed.
- **Internal inconsistencies:** abstract says 6 LLMs, §3.1.1 says "eight representative
  LLMs", the conclusion says "7 mainstream LLMs"; κ table (Table 6) lists 6 models.
- **Directly relevant data:** Table 8 reports `score/TCR/TIR` **before** attack and
  `score'/TCR'/TIR'` **after** attack alongside ASR, per scenario. Average TCR 61.44% →
  38.84% (↓36.78%), average ASR 73.44%. Table 5: "Perfect" outcomes 63.96% (no attack) →
  20.73% (attack); Partial Tool Omission 25.42% → 75.54%.
  → **RAS-Eval does report benign and attacked task performance separately**, which is the
  minimum needed to *notice* the confound — but it does not condition ASR on TCR, nor
  discuss the confound.

### 2.8 Contemporaneous practitioner and standards attention

| Item | Content | Level |
|---|---|---|
| ARES (`preprints.org/manuscript/202608.0594`, 2026) | "Attack-success rate is calculated over all attack trials, **including those in which no harmful action is generated**. Defense-success rate is …" — i.e. the denominator/influence question | **B** |
| "Measuring Indirect Prompt Injection in Autonomous Web Agents" (SSRN, 2026) | "The phrase 'attack success rate' is often treated as if it were a stable property of a model. **It is not.** A web agent can encounter an injection but ignore it; …" | **B** |
| promptfoo engineering blog (2025-12-12) | "Why Attack Success Rate (ASR) Isn't Comparable Across…" — ASR "changes with attempt budget, prompt sets, …" | **B** (practitioner) |
| NIST technical blog (2025-01-17) | "Strengthening AI Agent Hijacking Evaluations" | **B** |

The fact that a commercial eval vendor and a standards body are both publishing on ASR
non-comparability is evidence the problem is now widely recognised, which is the opposite
of a novelty signal.

---

## 3. Terminology variants — what the field actually calls this

Requested list, with what each term maps to and whether it is in use:

| Proposed / suggested term | Established term found | Who uses it |
|---|---|---|
| "conditional attack success" | **C-ASR (Conditional Attack Success Rate)**; **Task-Success-Conditional Attack Success Rate** | ACM MM 2026 entry; HarnessSafe; SkillSafetyBench |
| "controlling for benign task performance" | **paired utility reporting** / "benign-task success under the same defense" | Pathade et al. checklist item 10 (37.8% of 259 papers do it) |
| "separates prompt injection from task execution" | **exposure / execution / observation / adjudication** decomposition | REDAgentBench |
| "attack influence" | not an established term for our construct; closest is **compliance** vs **recognition** | REDAgentBench's **Recognition–Execution Gap**; MCPTox's "instruction-following" |
| "tool execution success" | **tool-call correctness**; RAS-Eval's **performance score**; AgentDojo's state-based utility | RAS-Eval §3.1.2; AgentDojo §3.1 |
| "security benchmark confounding" | **measurement validity**; **incomparability**; **six axes of measurement divergence** | Pathade et al. (the exact phrase "measurement validity" is in their title) |
| "attack objective completion" | **targeted ASR** (AgentDojo) vs **utility under attack** | AgentDojo §3.4 |
| "capability confound in agent security" | **capability maintenance** required for a successful attack | AgentHarm |
| "benchmark underpowered" | **minimum detectable difference (MDD)** | Pathade et al. §V-A; Miller 2024 (`arXiv:2411.00640`) |

**Terminology we had not considered, and which reframes the problem:**

- **"Recognition–Execution Gap"** (REDAgentBench) — the agent recognises the risk and
  proceeds anyway. Distinct from our `I → X` chain: it is `C → ¬I → O`.
- **"Evidence visibility"** (REDAgentBench) — reported ASR depends on whether the evaluator
  can *observe* the violation. A third confound, orthogonal to influence and competence.
- **"Exposure"** as a first-class stage, separable from execution.
- **"Attribution"** — HarnessSafe's "conditional attack-success rate… the percentage of
  **scored** …" suggests an attribution step.
- **"Judge calibration"** as the term of art for oracle-validation (Pathade et al. §IV).
- **"Unit of analysis"** — the per-injection vs per-task factor-`k` gap.

---

## 4. Audit of existing benchmarks against the 10-point checklist

Legend: **YES** · **NO** · **PARTIAL** · **UNCLEAR**. Per the brief, **PARTIAL and
UNCLEAR are used rather than inferring YES from a related metric.**

| # | Question | AgentDojo | ASB | RAS-Eval | AgentDyn | MCPTox | Progent | InjecAgent | AgentHarm | REDAgentBench | SkillSafetyBench |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Benign task success measured? | YES | YES | YES | YES | **NO** | YES | UNCLEAR | PARTIAL | UNCLEAR | YES |
| 2 | Attack success measured? | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| 3 | Tool-call correctness measured? | PARTIAL | UNCLEAR | YES | UNCLEAR | PARTIAL | UNCLEAR | UNCLEAR | PARTIAL | YES | YES |
| 4 | Execution trace recorded? | YES | UNCLEAR | YES | UNCLEAR | UNCLEAR | UNCLEAR | UNCLEAR | UNCLEAR | YES | YES |
| 5 | Was the injected instruction followed? | PARTIAL | UNCLEAR | PARTIAL | NO | PARTIAL | NO | PARTIAL | PARTIAL | YES | PARTIAL |
| 6 | Instruction-following distinguished from final objective? | PARTIAL | UNCLEAR | PARTIAL | NO | NO | PARTIAL | NO | **YES** | **YES** | PARTIAL |
| 7 | ASR conditioned on task execution? | **NO** | NO | NO | NO | NO | NO | NO | **YES** (capability maintenance) | PARTIAL | **YES** (per section title) |
| 8 | Both quantities reported separately? | **YES** | YES | **YES** | YES | **NO** | YES | PARTIAL | YES | YES | **YES** |
| 9 | Mathematical decomposition of attack success? | NO | NO | NO | NO | NO | NO | NO | PARTIAL | **YES** | PARTIAL |
| 10 | Confounding problem discussed? | **YES** | UNCLEAR | **NO** | PARTIAL | NO | PARTIAL | UNCLEAR | **YES** | **YES** | PARTIAL |

### Notes and evidence for the non-obvious cells

- **AgentDojo #7 NO, #8 YES, #10 YES.** It reports benign utility, utility under attack,
  and targeted ASR as three distinct metrics (§3.4, §4.1) — so both quantities *are*
  reported. But nothing conditions targeted ASR on task execution. #10 is YES because of the
  verbatim confound sentence quoted in §2.6.
- **RAS-Eval #3 YES, #4 YES, #7 NO, #10 NO.** `O` is an ordered sequence of triplets
  `(τ, α, r)`; performance score is `n_correct/(n_correct+n_wrong+n_lack)`; TCR requires the
  human-annotated sequence as an ordered subsequence. So tool-call correctness and traces
  are first-class. Yet ASR is computed marginally over all attack tasks and is never
  conditioned on TCR, and no confound discussion was located.
- **AgentHarm #6 YES, #7 YES, #10 YES.** Verbatim: successful scoring "requires jailbroken
  agents to maintain their capabilities following an attack." This is the capability
  condition inside the success criterion.
- **REDAgentBench #9 YES, #10 YES.** Its central claim *is* that collapsing the stages is a
  measurement error; it decomposes into exposure/execution/observation/adjudication and
  verifies from environment state.
- **MCPTox #1 NO, #8 NO.** Pass-1 reading: no utility measurement, no cost, no defence
  evaluation. Consistent with Pathade et al.'s finding that only 37.8% of papers report
  benign-task utility.
- **SkillSafetyBench #7 YES, #8 YES.** §5.3 reports ASR *and* "task-level performance using
  the original task reward inherited from SkillsBench, which serves as a measure of whether
  the underlying task is still completed successfully under attack"; Figure 3 is titled
  "Attack success versus task success." A separate section defines the
  **task-success-conditional** rate. ⚠️ **Caveat: the fetched text truncated at §5.4, so the
  conditional-ASR section was not read directly in this pass — the section title is
  search-index-level (B).**
- **InjecAgent.** Mostly UNCLEAR: only the abstract was available this pass (base ASR 24%,
  enhanced ≈47% per secondary sources; primary says "24%"). Do **not** fill these cells
  without reading the full text.
- **ASB #1/#2/#8.** NRP is a utility-security balance metric, so utility and security are
  both present; but #3–#7 could not be determined from the abstract.

### Aggregate read of the audit

- **Q7 (condition ASR on task execution)**: 1 clear YES (AgentHarm, via capability
  maintenance), 1 YES-per-title (SkillSafetyBench), 1 PARTIAL (REDAgentBench). 7 of 10 NO.
- **Q8 (report both separately)**: 8 of 10 YES or PARTIAL.
- **Q10 (discuss the confound)**: 3 clear YES, 3 PARTIAL, 2 NO, 2 UNCLEAR.

So the field has, as of 2026, moved from "nobody reports utility" to "most report utility,
two or three condition on it, and three discuss the confound." That is the shape of a
closing gap, not an open one.

---

## 5. Does the gap survive? — classification

**Classification: B — substantially addressed.** Secondarily **C — partially addressed**
on the narrow empirical question of magnitude.

| Claim | Status | Evidence |
|---|---|---|
| The problem has been **identified** | YES | AgentDojo §4.1 (2024), verbatim; StrongREJECT (2024), verbatim |
| The problem has been **formalised** | YES | Pathade et al. (2026): 6 axes, `ASR̂` formula, inversion condition; REDAgentBench: exposure/execution/observation/adjudication |
| The problem has been **measured** | YES | StrongREJECT measured capability degradation; REDAgentBench measured the Recognition–Execution Gap (~1 in 5); SkillSafetyBench reports ASR + task success jointly; Pathade et al. measured the *reporting* deficiency across 259 papers |
| The remedy **exists under an established name** | YES | C-ASR; Task-Success-Conditional ASR; AgentHarm's capability-maintenance criterion |
| The problem has been **solved** | **NO** | No consensus remedy; Pathade's checklist is "proposed, not validated"; no end-to-end empirical demonstration exists |
| **Magnitude of the competence channel on a capability ladder is unquantified** | **NO — residual open** | Not located anywhere. Pathade's power analysis covers their A1/A2 axes, not capability |

### Why "potentially novel" (D/E) is the wrong call

The brief warns: *"Do NOT choose 'potentially novel' merely because you cannot find a paper."*
Here the situation is stronger than an absence of evidence — there is **positive evidence of
coverage**:

1. A paper posted **~4 days before this analysis** formalises ASR-as-a-family, does a
   259-paper meta-analysis, and names a utility-reporting checklist item that is our
   neighbour's problem.
2. A benchmark paper names and measures the Recognition–Execution Gap.
3. The exact metric the brief proposed to invent has a published name and multiple users.
4. AgentHarm has enforced capability maintenance inside its success criterion since 2024,
   accepted at ICLR 2025.

A reviewer encountering "we propose to decompose ASR into influence × competence" in late
2026 will cite Pathade et al., REDAgentBench, AgentHarm, and StrongREJECT, and reject.

---

## 6. If the gap survives: what the contribution could be

The brief's instruction — *"Do not invent terminology unnecessarily"* — resolves the naming
question: **use C-ASR / task-success-conditional ASR and the standard companions.** Do not
propose AIR / AIC / TES / AOC.

What follows is the *only* framing I can defend, and even then it should be regarded as an
incremental empirical contribution, not a framework.

**Do not claim:** a decomposition (the chain rule is trivial); a new metric (C-ASR exists);
the observation that ASR conflates influence and competence (named in 2024, measured in
2024–2026).

**Candidate contribution, narrowly stated:**

> An **empirical mediation estimate with uncertainty** of how much of the cross-model
> variance in agent ASR is attributable to the competence channel, on a **capability ladder
> with family held constant**, together with a demonstration of whether correcting for it
> **changes a published cross-model ordering**.

Supporting argument for why this is not merely re-labelling:

- Pathade et al. explicitly leave the empirical ranking-inversion experiment undone
  ("needs model access we did not have") and scope it to their own axes A1/A2.
- The capability channel is not among their six axes.
- AgentHarm's capability condition is binary-by-design in one benchmark; no one has
  *estimated* the channel's magnitude across models.
- Correction must be done with **C-ASR plus a stated selection caveat** (§1.3), not with a
  naive product.

**Honest risk assessment:** this is a narrow, empirically-demanding, methodologically
delicate contribution whose most likely fate is to be read as "a powered execution of
Pathade et al.'s acknowledged next step, restricted to one axis." It is defensible; it is
not exciting; and the chance that Pathade et al. or the REDAgentBench group are already
doing it is material.

---

## 7. Counterfactual / control design

The brief's Controls A–E, evaluated for what each does and does not identify.

| Control | Configuration | Identifies | Does **not** identify |
|---|---|---|---|
| **A** | Benign agent, same task, no payload | `K` — benign task competence; the base rate of the action the attacker wants | Whether the agent is *susceptible* |
| **B** | Payload present, required tool **unavailable** | Attempt/intent separated from *effect*: an attempt that cannot succeed reveals `I` without `O` | Whether the agent would have completed the objective; and tool availability is a *harness* variable (REDAgentBench: ASR varies with harness) |
| **C** | Capability present, **no** payload | **Essential and often omitted.** Estimates the *coincidental* base rate of the attacker's target action. Without it, ASR counts benign-but-coincident tool calls as attack success | Nothing about influence |
| **D** | Payload present, tool available | The standard attack condition: `P(O)` | Decomposition of `P(O)` without B and C |
| **E** | Matched benign/adversarial tasks | Removes task-difficulty as a between-condition difference; enables paired analysis | Doesn't address oracle error or competence *within* a model |

**Do A–E suffice? No.** They are necessary and close to sufficient for separating
*influence*, *effect*, and *coincidence*, but four confounders survive:

1. **`I` is latent and remains so.** Controls B and C give evidence about `I` but neither
   observes it. Any decomposition is an identification claim requiring assumptions that must
   be stated and probed.
2. **Oracle error is differential, not random** (Pathade §V-B). A defence changes the
   trajectory distribution (more refusals, hedging, truncation), so a judge's error rate is
   not constant across the systems being compared — exactly the condition under which
   rankings fail to be preserved.
3. **The competence measure is itself noisily estimated.** `K` is a binomial proportion
   over a small task set. At AgentDojo's 97 tasks, the standard error on `K` is roughly
   5pp at `p=0.5`; Pathade's MDD analysis implies a 100-instance benchmark cannot resolve
   <18pp between two systems. **Designing a decomposition on an underpowered competence
   estimate produces a decomposition with an enormous confidence interval.**
4. **Harness and evidence visibility** (REDAgentBench): reported ASR varies with the agent
   harness and with whether the violation is observable. A single-harness study cannot
   generalise, and an unlogged violation is silently a failure.
5. **Non-determinism** (Pathade A3, 65.3% of papers report neither variance nor repeats).
   With four commercial Flash models this is the dominant practical obstacle.

Also note the **collider hazard** (§1.3): conditioning on `X` or on `K` stratifies on a
descendant of the treatment, which can bias the very estimate we want.

---

## 8. Minimal experiment

Scoped to be feasible **before** any AgentSec platform exists, and sized using Pathade
et al.'s power formula rather than intuition.

| Element | Specification |
|---|---|
| **Independent variables** | (i) **capability**: ≥4 rungs of one open-weight family with published parameter counts, decoding frozen; (ii) **injection condition**: Controls A, C, D (B and E as secondary); (iii) **attack type**: compliance-exploiting injection vs refusal-triggering injection |
| **Dependent variables** | unconditional **ASR** = `P(O)`; **task success** `P(K)`; **C-ASR** = `P(O | K=1)` reported **with the selection caveat**; **attempt rate** (Control B); **coincidence base rate** (Control C); refusal rate; per-case token/latency cost |
| **Controls** | A (benign), C (no-payload base rate) as the two mandatory ones. B for the intent/effect split |
| **Experimental unit** | (task, payload, model rung, seed). **State the unit explicitly** — this is Pathade's A1, worth a factor of `k` |
| **Task/payload sets** | Reuse AgentDojo's 629 security cases (or a pre-registered subset), **not** newly authored cases. Reuse avoids benchmark-authorship overhead and makes the result directly comparable to a published reference |
| **Repetitions** | ≥5 seeds per cell at temperature > 0; report run-to-run variance separately from unit-to-unit variance. This is the single cheapest differentiator, given 65.3% of the field reports neither |
| **Model requirements** | Capability ladder, family constant, parameter counts verified, frozen revision IDs |
| **Agent requirements** | One harness, version-pinned. If budget allows, two — to estimate the harness term that REDAgentBench identifies |
| **Tool requirements** | Unmodified AgentDojo tool layer; no custom tools (which would introduce a harness confound) |
| **Statistical analysis** | (a) CIs on every rate; (b) declare the MDD for the chosen `|U|` and refuse to claim smaller differences; (c) estimate the competence-channel share as a mediation quantity with a sensitivity analysis, **not** as a product of marginals; (d) test whether the ASR ordering and the C-ASR ordering of the four rungs differ; (e) κ for any judged outcome |
| **Expected observation** | If the confound is consequential: the ASR ordering is monotone in rungs in one direction while the C-ASR ordering is flatter or reversed, and the mediation share is non-trivial with a CI excluding zero. If the confound is cosmetic: the two orderings coincide and the mediation share is ~0 |
| **Falsification** | Report "competence explains ~none of it, and the corpus-wide confound is inconsequential" if the mediation share's CI includes zero **and** the ASR and C-ASR orderings agree. **Pre-register this outcome** |
| **Primary threat to feasibility** | Power. Pathade's MDD at `|U|=100` is ≈18.2pp. Either use a large case set (AgentDojo's 629 gives MDD ≈ 7pp at `p=0.35`) or accept that only large effects are detectable — and **say so** |

**Why a capability ladder rather than four vendor APIs:** the entire point is to isolate the
competence channel. If the four models differ in family *and* in capability *and* in
provider, the "capability" coefficient is unidentifiable (§9).

---

## 9. Can our four models support this?

Models: DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4. All four remain
label **B/C** in `sources.csv` (R35–R38) — the ".1 / 2.6 / 5.3 / 4" designations and the
parameter/context figures are **not vendor-verified**.

| Purpose | Verdict | Reason |
|---|---|---|
| **A. Pilot** | **Yes — and better suited than I said in pass 2** | They are cheap, which is precisely what a field whose dominant defect is single-run point estimates needs (§2.1 A3). They are adequate for: protocol hardening, per-case cost instrumentation, κ calibration of any judged outcome, and **variance estimation** to size the real study. A four-model repeatability study is a legitimate small artefact |
| **B. Main experiment (capability claim)** | **No** | Four independent reasons: (1) **no capability spread** — all Flash/mini tier, so four peers, not rungs; (2) **provider perfectly confounded** — three Chinese vendors + one Korean, no Western frontier, so any "capability" effect is inseparable from tokenizer, alignment pipeline, refusal training, and API implementation; (3) **no verified parameter counts**, so the standard capability proxy is unavailable (and MoE "active parameters" is a further definitional problem); (4) **version pinning not demonstrated**, so results are not reproducible |

**Recommendation.** Split the work:

1. **Main experiment** on ≥4 rungs of **one open-weight family with published parameter
   counts, run locally, frozen revision, fixed decoding**. Local open weights solve the
   ladder, the pinning, the provider confound, and the cost problem at once.
2. **The four APIs as a cross-provider Flash-tier replication and variance study** — a real
   contribution given Pathade et al.'s finding that 65.3% of papers report no uncertainty,
   and honest about being tier-restricted.

Do **not** run the main experiment on the four APIs. Four Flash models cannot carry a claim
about capability, and a reviewer will say so immediately.

---

## 10. Strongest possible criticism

I will be the hostile reviewer. Five objections, ordered by damage.

### C1 — "The decomposition is mathematically trivial, so there is nothing to contribute."

**Largely correct.** `P(O) = P(I)·P(X ∧ C | I)` is the chain rule. Multiplying two
conditionals is not a research contribution. Nothing in the brief's framing survives this as
stated.

**Evidence needed to overcome it:** a *measurement* contribution, not a decomposition.
Specifically: an estimate of the **latent** term with a validated oracle, an uncertainty
interval, and a demonstration that correcting changes a published conclusion. If the paper's
abstract contains "we decompose ASR into," it fails. If it contains "we estimate how much of
the cross-model variance is competence-mediated, with CIs, and the ranking changes," it
might survive.

### C2 — "This is already published. Pathade et al. (2026) formalised measurement validity in agentic security, and REDAgentBench decomposed attack success into stages."

**This is the killer objection, and it is substantially fatal to the current framing.** A
paper posted four days ago formalises ASR as a six-axis family, does a 259-paper
meta-analysis, and proposes a checklist whose item 10 is the utility pairing. REDAgentBench
explicitly says existing evaluations "collaps[e] exposure, execution, observation, and
adjudication."

**Evidence needed to overcome it:** position strictly *inside* Pathade's framework as a
**seventh axis with an empirical estimate**, and cite their explicit statement that the
end-to-end experiment is their acknowledged next step. State in the first paragraph that the
conceptual claim is not novel and that the contribution is the measurement. Anything less
will be read as not having done the literature review.

### C3 — "The metric already exists. You are renaming C-ASR."

**Correct.** Conditional Attack Success Rate is in use (ACM MM 2026; HarnessSafe;
SkillSafetyBench's task-success-conditional ASR). Proposing AIR/AIC/TES/AOC would be
invention for its own sake, exactly what the brief warns against.

**Evidence needed to overcome it:** use C-ASR, credit its existing users, and contribute the
*estimate* rather than the metric. Also address the non-trivial point in §1.3 — that naive
C-ASR conditions on a post-treatment variable and therefore inherits selection bias, which
is a real, citable technical correction rather than a renaming.

### C4 — "AgentHarm already conditions success on capability, and StrongREJECT already identified capability degradation. The confound has been handled."

**Serious.** AgentHarm (ICLR 2025) requires jailbroken agents to "maintain their
capabilities" to score; StrongREJECT (NeurIPS 2024 D&B) found that "jailbreaks bypassing a
victim model's safety fine-tuning tend to reduce its capabilities."

**Evidence needed to overcome it:** show that the confound is handled by *design* in one
benchmark but is **not quantified** anywhere, and that its magnitude across a capability
ladder is unknown. Then actually measure it. If the measured share turns out to be small,
report that as the finding — a small effect is a legitimate result and it *strengthens*
AgentHarm and AgentDojo.

### C5 — "Existing benchmarks already log the execution traces needed. This is a re-analysis."

**Partly true and partly self-defeating.** AgentDojo's state-based utility functions,
RAS-Eval's `O = [(τ, α, r)]` triplet logs, and REDAgentBench's service receipts all contain
the raw material.

**Evidence needed to overcome it:** either (a) do the re-analysis *and* show it flips a
published ordering — cheap, fast, and if it works, decisive; or (b) accept that a
re-analysis loses to a purpose-built measurement, and instead build the *capability ladder*
that no existing trace contains. Note the asymmetry: (a) is cheap and high-variance; (b) is
expensive but strictly more defensible. **Recommend (a) first as a decision experiment:** if
the re-analysis on published traces shows no ordering change, the whole direction should be
abandoned before spending on (b).

### C6 — "Your four models cannot support any capability claim."

**Correct** (§9). Answered only by the open-weight ladder, run locally, pinned.

---

## 11. Final decision

### A. Evidence that the gap exists

- **RAS-Eval's own ASR definition is competence-dependent** (Eq. 7: target tool must appear
  in the agent's invocation sequence), and the paper does not discuss this. Verified (A).
- **AgentHarm enforces capability maintenance** in its success criterion but does not
  *estimate* the channel (A, abstract).
- **Pathade et al. report that only 37.8% of 259 papers report benign-task utility**, so the
  confound is uncontrolled in ~62% of the current literature (A).
- **Pathade et al. explicitly leave the end-to-end empirical ranking-inversion experiment
  undone** ("needs model access we did not have") (A).
- **The capability channel is not one of Pathade's six axes**, so the framework does not yet
  contain it (A).
- **REDAgentBench reports a Recognition–Execution Gap affecting ~1 in 5 confirmed
  violations** — i.e. the influence/completion gap is empirically large in at least one
  setting (A, abstract).

### B. Evidence against the gap

- **Pathade et al. (2026-09-21) formalise ASR-as-a-family with six axes, a 259-paper
  meta-analysis, power analysis, and a utility-reporting checklist item.** This is the
  proposed contribution's conceptual core, published four days ago (A).
- **REDAgentBench (2026-08) explicitly identifies and remedies the collapse** of attack
  success into a single number, decomposing into exposure/execution/observation/adjudication (A).
- **AgentHarm (ICLR 2025) conditions success on maintained capability** — the decomposition,
  implemented (A).
- **StrongREJECT (NeurIPS 2024 D&B) named and measured the capability-mediation phenomenon**
  in jailbreaks (A).
- **AgentDojo (NeurIPS 2024 D&B) named the agent-side confound verbatim** (A).
- **The remedy exists as an established, multiply-used metric** (C-ASR /
  task-success-conditional ASR) (A/B).
- **The decomposition is the chain rule** and is mathematically trivial (§1.2, §10 C1).
- **Adjacent practice is widespread**: 8 of 10 audited benchmarks report utility and attack
  success separately (§4, Q8).
- **A commercial eval vendor and NIST are both publishing on ASR non-comparability** (B),
  indicating broad recognition.

### C. Closest existing work

1. **Pathade, Pawar & Patil (2026), "Attack Success Rate Is Not a Number"**,
   `arXiv:2609.25173v1` — **nearest by far**. Same problem space (measurement validity of
   ASR in agentic security), same method family (formalise + meta-analyse + power-analyse +
   checklist). Omits the capability channel. Leaves empirical work undone.
2. **REDAgentBench (2026)**, `arXiv:2608.10669` — nearest structural decomposition
   (exposure/execution/observation/adjudication) and the Recognition–Execution Gap.
3. **AgentHarm (ICLR 2025)**, `arXiv:2410.09024` — the capability condition inside a success
   criterion.
4. **StrongREJECT (NeurIPS 2024 D&B)**, `arXiv:2402.10260` — capability-mediated attack
   success in jailbreaks; rubric evaluator replacing binary ASR.
5. **AgentDojo (NeurIPS 2024 D&B)**, `arXiv:2406.13352` — names the agent-side confound;
   three separate metrics.
6. **SkillSafetyBench (2026)**, `arXiv:2605.12015v2` — task-success-conditional ASR and an
   attack-success-vs-task-success plot.
7. **Carlini et al. (2019), "On Evaluating Adversarial Robustness"** (`arXiv:1902.06705`, B)
   and **Tramèr et al. (2020)** (`arXiv:2002.08347`, B) — the methodological ancestors the
   field is now explicitly importing.

### D. What existing benchmarks already provide

- Benign task success (`K`) and attack success (`O`) **as separate reported metrics** —
  AgentDojo, ASB, RAS-Eval, AgentDyn, Progent, SkillSafetyBench (§4 Q1, Q2, Q8).
- **Tool-call correctness and execution traces** — RAS-Eval (ordered triplet sequences,
  performance score), AgentDojo (state-based oracles), REDAgentBench (service receipts and
  final-state deltas) (§4 Q3, Q4).
- **Formal, environment-grounded success oracles** rather than judge-only adjudication —
  AgentDojo, RAS-Eval, REDAgentBench, SkillSafetyBench.
- **Confound acknowledgement** — AgentDojo §4.1, AgentHarm, REDAgentBench (§4 Q10).
- **A conditional metric** — AgentHarm's capability-maintenance criterion; SkillSafetyBench's
  task-success-conditional ASR (§4 Q7).
- **Stage decomposition of attack success** — REDAgentBench (§4 Q9).

### E. What they do not provide

Stated narrowly, because the honest residual is small:

1. **An estimate, with uncertainty, of the share of cross-model ASR variance attributable to
   the competence channel.** Nobody has put a number — or an interval — on it.
2. **The capability channel as an explicit axis in a measurement-validity framework.**
   Pathade et al.'s six axes omit it.
3. **A demonstration that correcting for the confound changes a published cross-model
   ordering.** Pathade et al. declare the analogous end-to-end experiment undone.
4. **Proper handling of the selection bias** created by conditioning on task success —
   nobody has yet noted that naive C-ASR conditions on a post-treatment variable (§1.3).
5. **Adequate statistical power.** Pathade et al.'s own analysis shows most of the field uses
   ~100-instance benchmarks with an MDD of ~18pp.

### F. Final classification of the gap

**B — substantially addressed**, with a narrow **C — partially addressed** residual on
magnitude.

Not **E** (potentially novel): there is *positive* published evidence of coverage across the
concept, the formalisation, the metric, and one benchmark's success criterion. Not **D**
(weakly addressed): three of the ten audited benchmarks discuss the confound and two
condition on competence. Not **A** (already solved): no consensus remedy exists, Pathade's
checklist is explicitly unvalidated, and no magnitude estimate exists.

**Practical reading: this direction is no longer viable as a primary research contribution.
It is viable only as a narrow, well-positioned empirical measurement — and only if it is
scoped to the residual in §E, positioned inside Pathade et al.'s framework, and run on a
proper capability ladder.**

### G. If viable: precise research contribution

> **Estimate the competence-mediated share of cross-model variation in agent attack success,
> with uncertainty, on a within-family capability ladder; determine whether correcting for
> it changes the induced model ordering; and state and probe the identification assumptions
> — including the selection bias inherent in conditioning on task success.**

Positioned explicitly as: (i) a seventh axis in Pathade et al.'s framework, with an
empirical estimate rather than a checklist item; (ii) the end-to-end experiment Pathade et
al. declare they could not run; (iii) using established C-ASR terminology, not new names;
(iv) contributing the *estimate*, never the decomposition.

**Decision experiment before any commitment** (§10 C5): attempt the re-analysis on
**AgentDojo's published traces**. If unconditional ASR and C-ASR induce the same model
ordering there, abandon the direction — and do so cheaply.

### H. If not viable: alternative direction

Remove the capability channel; the crowded part is the *concept*, not the *measurement*.
The residuals that remain genuinely open and are better aligned with our resources:

1. **Repeatability as the contribution.** Pathade et al. show 65.3% of papers report neither
   variance nor repeated runs, and that a 100-instance benchmark cannot resolve <18.2pp. A
   **fully powered, many-seed replication of one headline agent-security claim** — reporting
   run-to-run vs unit-to-unit variance decomposition — is cheap, unambiguously useful, and
   exactly the "single cheapest improvement" shape. Our four Flash models are *well suited*
   to this, since cost is the binding constraint on seeds.
2. **The harness/evidence-visibility term.** REDAgentBench found "reported ASR varies with
   harness and evidence view." That is measured in one paper, for one benchmark, and not
   decomposed. Cross-harness variance for a fixed model and fixed attack is a clean,
   identifiable quantity.
3. **The selection-bias correction itself.** Nobody appears to have noted that C-ASR
   conditions on a post-treatment variable. A methods paper on *when conditioning on task
   success helps versus hurts* is a small but genuinely technical contribution, and it is
   compatible with direction (1).

Recommendation: **(1) as the primary, (3) as the technical spine, (2) as the extension.**

### I. Minimal pilot experiment

**Purpose:** establish variance, power, and oracle reliability — not to test the main claim.

1. Four available models (DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4),
   version-pinned as far as vendor documentation permits.
2. **One** reused benchmark subset — a fixed, pre-registered sample of AgentDojo security
   cases (`n = 100`, matching Pathade et al.'s reference scale, so their MDD of ≈18.2pp
   applies directly).
3. **≥10 seeds** per (model, case) at temperature > 0. Same system prompt string, same tool
   layer, same harness.
4. Measure: `P(O)`, `P(K)`, C-ASR, refusal rate, per-case tokens and wall-clock.
5. Report: run-to-run variance vs unit-to-unit variance; the empirical MDD at `n=100`;
   κ between two independent oracles (state-based and judge-based) on the same trajectories.
6. **Decision rule:** if run-to-run variance is of the same order as the between-model
   differences we intend to claim, then no four-model comparison at `n=100` is defensible
   and the design must change before the main experiment. If the state oracle and the judge
   disagree by more than the effects we intend to claim, the oracle must be fixed first.

This pilot is cheap, uses only the resources we have, and is decisive about whether the
*main* experiment is feasible at all — which is the real risk after C2 and C4.

### J. What we must verify before proceeding

Ordered by decisiveness.

1. **Read Pathade et al. (`arXiv:2609.25173v1`) in full**, not just the HTML we fetched —
   check whether the capability channel appears anywhere in the six axes, the checklist, or
   the limitations. **This is the go/no-go item.**
2. **Read REDAgentBench (`arXiv:2608.10669`) in full** to determine whether its
   exposure/execution decomposition already includes a competence term, and whether
   "evidence visibility" subsumes it.
3. **Read SkillSafetyBench §5.5+ (the task-success-conditional ASR section)** — the fetched
   text truncated at §5.4, so our read of Q7 is currently search-index-level (B).
4. **Read AgentHarm's full text** to confirm whether it reports a separate capability score
   alongside harm score, which would move Q9 from PARTIAL to YES.
5. **Read InjecAgent's full text** to complete the audit row — currently mostly UNKNOWN.
6. **Watch for a follow-up from Pathade et al. or the REDAgentBench group.** Pathade et al.
   named the end-to-end experiment as the next step; the direction may be taken within
   months. Check arXiv listings before committing.
7. **Verify vendor facts for all four models** (parameters where published, context,
   revision IDs, tool-calling and structured-output support) — still label B/C after three
   passes.
8. **Confirm that a ≥4-rung open-weight family with published parameter counts is
   runnable** in our environment. The main experiment depends on it.
9. **Check the SSRN web-agent measurement paper and the ARES preprint** (both B) for a prior
   decomposition of the denominator problem.

---

## Appendix: sources verified or added in this pass

| ID | Status |
|---|---|
| **R52** | **New, A.** Pathade, Pawar & Patil, *Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation*, `arXiv:2609.25173v1`, ~2026-09-21. Full abstract + §§I–VIII read. **The single most important source for this pass.** |
| **R53** | **New, A (abstract).** Chen, Liu, Zhu, Dou, Jiang, Li, Guo, Chen, Zhang, *REDAgentBench: Executable Red Teaming and Faithful Measurement of LLM Agent Systems*, `arXiv:2608.10669`, 2026-08-11. |
| **R54** | **New, A (partial — truncated at §5.4).** Jin, Wang, Wei, Wang, Zeng, Zhang, Yang, Qu, Hu, Xu (Shanghai AI Laboratory), *SkillSafetyBench: Evaluating Agent Safety under Skill-Facing Attack Surfaces*, `arXiv:2605.12015v2`. |
| **R55** | **New, A (abstract).** Souly et al., *A StrongREJECT for Empty Jailbreaks*, `arXiv:2402.10260v2`, NeurIPS 2024 Datasets & Benchmarks. |
| **R14** | **Upgraded B → A.** AgentHarm, `arXiv:2410.09024v3`, **accepted at ICLR 2025** (authors' own Comments field). Venue question resolved. |
| **R03** | **Upgraded: full text now retrieved; pass-2 caveat resolved.** RAS-Eval metrics and RQ2 verified. §3.2.2 is a *discriminative-power* check regressing benign performance score, not a security-scaling claim — confirming the abstract's sentence is a mischaracterisation. ASR (Eq. 7–8) is defined on the agent's tool-invocation sequence and is therefore structurally competence-dependent. |
| **R01** | Notes updated: the confound sentence is at §4.1; three metrics reported separately (§3.4). |
| **R56** | **New, B.** Miller, *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*, `arXiv:2411.00640` (cited by R52; not fetched). |
| **R57** | **New, B.** Carlini, Athalye, Papernot, Brendel, Rauber, Tsipras, Goodfellow, Madry et al., *On Evaluating Adversarial Robustness*, `arXiv:1902.06705` (cited by R52 as the precedent methodology checklist; not fetched). |
| **R58** | **New, B.** *HarnessSafe: Evaluating Safety Across Persistent Carriers in Agent Harnesses*, `arXiv:2608.06984` (surfaced via search only; uses "conditional attack-success rate"). |
| **R59** | **New, B.** `arXiv:2606.00497` (surfaced via search only; reports "attack success rate conditional on agent navigation to a declared trap URL"). |
| — | Existing entries whose notes should be read alongside this pass: **R48** (adaptive-attack evaluation is established practice), **R09** (pass^5 under-elicitation — the benign-evaluation analogue of this confound), **R29** (IETF 55-metric draft, for vocabulary alignment). |
