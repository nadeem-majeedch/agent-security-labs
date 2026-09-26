# 11 — Empirical Anomaly and Contradiction Map (Phase 11)

**Status: PHASE 11 COMPLETE — SURVIVORS: 2 (as first returned). Post-audit hostile verification later KILLED S1 (see §Part O-bis) and then KILLED S2 (see §Part P-bis). Live survivors after verification: 0.**

**Date of audit:** 26 September 2026
**Question of this phase (deliberately different from Phases 1–10):** not "which topic is unstudied?" but *"which important empirical observation in the recent AI / data-science / agent literature is not yet adequately explained?"*
**Search window:** primarily 2024–2026, with canonical pre-2024 anchors where a claim depends on them.
**Standing constraints (unchanged):** no invented contradictions, no invented papers, no invented numerical results, no abstracts where full texts exist, no replication-as-novelty, no "another benchmark" as novelty, no return to generic agent security or generic audit AI, no implementation, no paper prose, no commit/push.

---

## Part 0 — Method, labels, and headline finding

### 0.1 Verification labels (unchanged convention)

| Label | Meaning | Citable as a figure? |
|---|---|---|
| **A** | Fetched and read at the source (abstract or full text) in this session. | Yes, for what was read |
| **B** | Read only via a snippet, listing, or another work's summary. | **No** |
| **C** | Not verified at all. | No |

### 0.2 Claim tags

**[FACT]** · **[INFER]** · **[HYP]** · **[OPEN]**

### 0.3 Headline finding

**[FACT]** Twenty candidate anomalies were assembled from primary and traceable-secondary sources. Sixteen are **CLOSED** and four are **UNCERTAIN or PROMISING**; after the Part N kill pass, **two survive** (ANO-08, ANO-10). The full machine-readable record is `research/tables/empirical-anomaly-matrix.csv` (21 rows × 21 columns; validated).

**[INFER]** The dominant reason 16 of 20 die is not that the phenomena are unreal. It is that the 2025–2026 literature has developed a **general-purpose explanatory vocabulary for exactly these apparent contradictions** — the measurement-validity programme. A single cluster of works now explains most "method X works / method X fails" contradictions as artefacts of an unreported variable:

* **estimand choice** (one-shot vs top-K over repetitions) — Chouldechova et al. (R74) **[A]**;
* **attack budget vs replication conflation** — CAISI (R60) **[A]**, Swept AI (R75) **[A]**, Hofer et al. (R71) **[A]**;
* **metric axis-design** (unit of analysis, oracle, binarisation) — Pathade et al. (R52) **[A]**;
* **evidence channel** (trajectory vs state) — REDAgentBench (R77) **[A]**;
* **judge measurement validity** (differential TPR/FPR) — Chouldechova (R74) **[A]**, Eiras et al. (R78) **[A]**;
* **test-time compute normalisation** — Tran & Kiela (R202) **[A]**;
* **correlated generator–verifier error** — R145 **[B]**, R146 **[B]**;
* **contamination / memorisation** — R214 **[B]**, R215 **[B]**.

**[INFER]** This is the phase's structural result: the *contradiction-resolution* space is itself largely occupied, so an anomaly survives only when it (i) is a genuine conflict or unexplained pattern, (ii) is not dissolved by one of the named hidden variables above, and (iii) yields an explanatory contribution rather than a new number. Two candidates satisfy this: the **grounding rate-versus-detectability inversion** (ANO-08) and the **AI-test coverage-versus-fault-detection reversal** (ANO-10). Both are reconciled by naming a *controlling factor*, and both are feasible with the four Flash-tier models and public artifacts.

**[OPEN]** Whether either is truly unoccupied depends on two papers we could only reach at snippet level (R204, R206); both are flagged for full-text reading before any claim is load-bearing.

---

## Part A — Contradictions located in the 2024–2026 literature

The brief supplied example patterns; the audit replaced them with real pairs. The pattern-level yield:

| Pattern | Real instance found | Primary sources | Verdict |
|---|---|---|---|
| "Technique X improves reliability" vs "X has no effect" | defences near-zero ASR vs adaptive attacks >90% | R11/R15 vs R48 | CLOSED |
| "More capable models are safer" vs "less safe" | RAS-Eval positive scaling vs AgentDojo/MCPTox inverse scaling | R03 vs R01/R06 | UNCERTAIN (ANO-01) |
| "Agentic systems improve productivity" vs "increase error rates" | SWE-bench pass vs maintainer non-merge; reward hacking | R200/R139 | CLOSED |
| "RAG reduces hallucination" vs "RAG increases vulnerability" | rate reduction vs detection evasion | R204 | **PROMISING (ANO-08)** |
| "LLM judges correlate strongly with humans" vs "systematically disagree" | correlation vs agreement; style-driven FN swing | R78/R203/R74 | CLOSED |
| "AI-generated code passes tests" vs "contains semantic errors" | grader vs merge; mutation vs coverage | R200/R206 | **PROMISING (ANO-10)** |
| "More reasoning helps" vs "more reasoning hurts" | inverted-U CoT length | R201 | CLOSED |
| "More agents help" vs "more agents hurt" | equal-budget SAS ≥ MAS | R202 | CLOSED |

**[FACT]** The eight pattern classes the brief named all have real 2024–2026 instantiations. Six are already explained; two are not fully.

---

## Part B — Unexplained empirical findings (language-filtered, then filtered again)

Search language proposed by the brief ("surprisingly", "contrary to", "remains unclear", "only works when", "performance degrades", "mixed results") returns a very large set. Per the brief's own instruction, ordinary future-work statements were discarded. The experimentally meaningful subset:

* **[FACT]** METR: "roughly half of test-passing SWE-bench Verified PRs … would not be merged into main"; the maintainer merge rate is "about 24.2 percentage points (SE 2.7)" below the automated grader (R200) **[A]**. The authors explicitly do **not** claim a capability limit — a rare instance of a paper naming its own finding's most likely confound.
* **[FACT]** RAG increases the human false-negative rate of hallucination detection "from 73.1% to 78.5%" (R204) **[B]**.
* **[FACT]** "the usefulness of coverage and mutation is highly context-dependent" for LLM-generated tests (R206) **[B]**.
* **[FACT]** CoT accuracy follows "an inverted U-shaped curve", and the optimal length "increases with task difficulty but decreases with model capability" (R201) **[A]**.
* **[FACT]** "SAS consistently match or outperform MAS … when reasoning tokens are held constant", and MAS gains are "better explained by unaccounted computation and context effects" (R202) **[A]**.
* **[FACT]** REDAgentBench: state-grounded judging reports ASR 7.73–11.72 pp higher than trajectory judging, with 23 of 64 slices containing a strict pairwise reversal (R77) **[A]**.

**[INFER]** Five of these six are already-explained. Only the first two (R204 rate/detectability; R206 coverage/fault-detection) remain open at the level of the *controlling factor*.

---

## Part C — Cross-paper reconciliation (method-by-method)

For each promising pair we compared model, dataset, task, prompt, evaluation, metric, sample size, training, inference, environment, tool use, context, seed, implementation and date. The comparison table is the core of the matrix (`research/tables/empirical-anomaly-matrix.csv`, columns `what_differs`, `potential_hidden_variable`, `existing_explanation`); the narrative conclusions:

* **ANO-01 [OPEN].** The capability–safety pair fails reconciliation *because neither side controls the competence channel*. AgentDojo's own text flags that low-utility models "often fail at correctly executing the attacker's goal, even when the prompt injection succeeds" (R01) **[A]**; RAS-Eval's headline metric structurally requires the attacker's target tool to appear in the call sequence (R03) **[A]**. The divergence is thus expected a priori and is not evidence of two incompatible laws. **CLOSED as a contradiction; OPEN as a measured decomposition** — but blocked by Part R (no capability spread among our four models).
* **ANO-08 [PROMISING].** The rate and detectability claims are not contradictory on their own terms; they are two *different dependent variables* of the same intervention. What is missing is the joint characterisation. **[INFER]** This is the phase's cleanest "two papers measured different things" resolution that nevertheless leaves a real scientific question.
* **ANO-10 [PROMISING].** R205 (coverage gains) and R206 (context-dependence) reconcile at the level of "it depends", but neither names the controlling factor. **[INFER]** the candidate controller is assertion specificity.

---

## Part D — Boundary conditions

**[FACT]** The literature already supplies several boundary conditions: context length (R207, R208), test-time compute (R201, R202), tuning/time budget for tabular models (R210), attack budget (R75), repetition count (R72/R61). **[OPEN]** The ones not yet pinned to a controlling factor are the *grounding level* boundary (where does detectability loss begin?) and the *assertion-specificity* boundary (when does coverage stop tracking fault detection?).

---

## Part E — Hidden variables

Eight candidate hidden variables were considered, mirroring the brief's list. Their status:

| Variable | Studied? | Source |
|---|---|---|
| attack budget vs replication | yes | R75, R74, R60 |
| test-time compute / reasoning tokens | yes | R201, R202 |
| evidence channel (trajectory vs state) | yes | R77 |
| judge family & style/length bias | yes | R78, R79 |
| serving batch size (temperature-0 non-determinism) | partly (mechanism known) | R209 |
| harness / scaffold | yes | R77, R87 |
| contamination / memorisation | yes | R214, R215 |
| **residual-error attribution structure under grounding** | **no** | this phase |
| **assertion specificity under test generation** | **no** | this phase |

**[INFER]** The two unstudied rows are precisely the survivors' hidden variables. The other seven are occupied, which is why their associated anomalies are CLOSED.

---

## Part F — "Works on benchmark, fails in reality"

* **[FACT]** SWE-bench: automated grader vs maintainer review, 24.2 pp gap (R200) **[A]**; contamination and flawed tests (R214) **[B]**; off-benchmark accuracy below 53% (R215) **[B]**. **CLOSED** — the mechanism (grader observability, contamination, unelicited code quality) is named by the sources themselves.
* **[FACT]** Test suites: coverage gains (R205) **[B]** vs context-dependence and reward hacking (R206, R139) **[B]**. **PROMISING** — mechanism not named.
* **[FACT]** Tabular: TFM-vs-GBDT reversal explained by tuning/time budget (R210) **[B]**. **CLOSED**.

**[INFER]** The brief's instruction "do not simply say benchmark overfitting" is the operative filter: SWE-bench is closed because a *concrete mechanism* is supplied; the test-coverage case survives because no concrete controller is.

---

## Part G — Cross-domain generalization failures

**[FACT]** Tabular foundation models generalize unevenly to strategic/realistic tabular data (R211) **[B]**, and the sign of their advantage over GBDT reverses across datasets (search-level) **[B]**. **[INFER]** But the generality claim the literature actually makes is conditional (tuned, sufficient data), so this is not a genuine cross-domain failure. **CLOSED.**

**[FACT]** Verifier agents fail to transfer as independent checkers because generator and verifier errors are correlated (R144 **[B]**, R145 **[B]**, R146 **[B]**). **CLOSED.**

---

## Part H — Reproducibility discrepancies

**[FACT]** The specific reproducibility phenomenon of the phase: temperature-0 plus a fixed seed is **not** sufficient for determinism, because kernel output depends on batch composition (R209 **[B]**, R213 **[B]**, R62 **[B]**). **[INFER]** The discrepancy is scientifically explained (batch-size-dependent numerics) but the *consequence* — that leaderboard positions can depend on uninstrumented serving schedules — is not characterised in the agent/eval setting. **[OPEN]** but not promoted: controlling it requires serving-level access (Part R), and the mechanism is already the explanation.

---

## Part I — Negative results

**[FACT]** R202 is a negative result with an explanatory mechanism (multi-agent gains disappear under matched compute) **[A]**. **[FACT]** R200 is a negative result with reasons (grader vs review) **[A]**. **[FACT]** R201 is a negative result with a law (inverted-U) **[A]**. **[INFER]** Each is already explanatory, so none is an open anomaly.

---

## Part J — Data-science-specific anomalies

**[FACT]** SHAP is a consistency-axiom method yet its *estimates* are unstable under correlation and resampling; stabilisation methods exist **[B]**. **CLOSED** (known mechanism). **[FACT]** Imbalanced-learning method comparisons reverse with imbalance ratio and dimensionality (search-level) **[B]**; **CLOSED** (the reversal is the method's known regime-dependence). **[FACT]** Agentic multiplicity inflates significance and has an estimator (R131) **[B]**; **CLOSED**. **[FACT]** Tabular TFM-vs-GBDT **CLOSED** (R210). **[INFER]** No data-science anomaly survives beyond the two cross-cutting survivors, which are LLM/system-level rather than classical-tabular.

---

## Part K — Software-engineering-specific anomalies

* **[FACT]** Higher benchmark score but worse real-world reliability (R200, R214, R215) — **CLOSED**.
* **[FACT]** AI tests raise coverage but not necessarily fault detection (R205 vs R206, R139/R140/R141) — **PROMISING (survivor)**.
* **[FACT]** Successful patches that introduce hidden regressions — subsumed by R200's "breaks other code" rejection reason — **CLOSED**.
* **[FACT]** Longer reasoning decreasing correctness (R201) — **CLOSED**.
* **[FACT]** Autonomous agents solving tasks but violating engineering constraints — occupied by reward-hacking instruments (R139/R140/R141) and METR's maintainer study (R200) — **CLOSED**.

---

## Part L — AI/agent contradictions (non-security)

* **[FACT]** Add verifier/reflection/more agents: improves vs degrades (R144/R145/R146/R157/R202) — **CLOSED**.
* **[FACT]** Self-correction recovers agents vs agents rarely recover (R129/R130/R145) — **CLOSED** (Scout solves it; recovery depends on environment feedback).
* **[FACT]** Grounding: rate down, detectability down (R204) — **SURVIVOR**.
* **[FACT]** Evaluation awareness makes agents safer vs reverses (R77) — **UNCERTAIN**, not promoted (saturated area + model-access blocker).

---

## Part M — Twenty candidate anomalies

The full 20-field record for every candidate is in `research/tables/empirical-anomaly-matrix.csv`. To satisfy the brief literally, each is reproduced here in compact form (fields numbered as in the brief). Statuses: **CLOSED ×16, UNCERTAIN ×2, PROMISING ×2**.

### ANO-01 — Capability–safety inversion vs positive security scaling
1. **Title:** Capability–safety inversion vs positive security scaling.
2. **Paper A:** AgentDojo, R01 **[A]**; MCPTox, R06 **[A]**.
3. **Paper B:** RAS-Eval, R03 **[A]**.
4. **Apparent contradiction:** capability → attack susceptibility is reported with opposite sign.
5. **Why it matters:** decides whether scaling helps or harms agent security.
6. **Both agree:** tool-using LLM agents; capability as the independent variable.
7. **Differs:** task, attack surface, metric, model family, inference mode, sample size, no significance test.
8. **Hidden variable:** competence confound + inference reasoning mode + metric definition.
9. **Existing explanation:** AgentDojo names the confound; RAS-Eval RQ2 is a benchmark-validity regression on one family; MCPTox gives instruction-following + reasoning-mode (+27.8% ASR).
10. **Sufficient?** No (no measured decomposition).
11. **Reconciliation experiment:** decompose ASR into influence × competence at matched benchmark.
12. **Data:** AgentDojo + MCPTox cases; influence/competence labels.
13. **Models:** capability spread required.
14. **Cost:** high.
15. **Contribution:** measured partition of the inversion.
16. **Falsification:** flat competence-controlled ASR across capability.
17. **Closest:** R52, R74, R76, R77.
18. **Novelty confidence:** medium.
19. **Feasibility:** low (Part R blocker).
20. **Status:** UNCERTAIN.

### ANO-02 — Defences near-zero vs defeated above 90%
Fields as matrix. **Existing explanation:** R74 (estimand shift), R75 (budget). **Sufficient?** Yes. **Status:** CLOSED.

### ANO-03 — Temperature 0 is not reproducible
**Existing explanation:** R209 (batch-size-dependent kernels), R213. **Sufficient?** Yes; consequence uncharacterised but fix is infrastructure. **Status:** CLOSED.

### ANO-04 — Judges correlate with humans but disagree item-wise
**Existing explanation:** R74, R78, R79, R85, R203. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-05 — Advertised context windows vs context rot
**Existing explanation:** R207, R208 (length/position/distractors). **Sufficient?** Yes at phenomenon level. **Status:** CLOSED.

### ANO-06 — Longer reasoning helps vs harms
**Existing explanation:** R201 (inverted-U + scaling laws + simplicity bias). **Sufficient?** Yes. **Status:** CLOSED.

### ANO-07 — Multi-agent beats single-agent vs the reverse
**Existing explanation:** R202 (compute normalisation; DPI argument). **Sufficient?** Yes. **Status:** CLOSED.

### ANO-08 — Grounding lowers hallucination rate but also lowers its detectability
1. **Title:** Grounding lowers hallucination rate but also lowers its detectability.
2. **Paper A:** RAG-reduces-hallucination literature (e.g. MEGA-RAG >40% reduction) **[B]**.
3. **Paper B:** R204 — RAG raises the human FN detection rate 73.1% → 78.5% **[B]**.
4. **Apparent contradiction:** the same intervention improves reliability and hides failures.
5. **Why it matters:** net trust = rate × detectability; rate-only reporting is misleading.
6. **Both agree:** RAG changes the hallucination distribution; detectability matters.
7. **Differs:** dependent variable (rate vs detectability); detector (human vs automated); grounding level.
8. **Hidden variable:** residual-error attribution structure / plausibility.
9. **Existing explanation:** R204 names the effect but does not decompose it.
10. **Sufficient?** No.
11. **Reconciliation experiment:** vary grounding level; measure rate × detectability jointly, anchored to held-out human labels.
12. **Data:** public QA sets with answer spans; held-out human detection labels.
13. **Models:** four Flash models suffice.
14. **Cost:** moderate.
15. **Contribution:** a rate × detectability law for grounding, with attribution structure as the controller.
16. **Falsification:** detectability loss fully explained by length/fluency.
17. **Closest:** R204, R207, R74, R79.
18. **Novelty confidence:** medium.
19. **Feasibility:** medium-high.
20. **Status:** PROMISING.

### ANO-09 — Code passes tests but is not mergeable
**Existing explanation:** R200 (grader vs review, reasons named), R214, R215. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-10 — AI tests raise coverage but not fault detection
1. **Title:** AI tests raise coverage but not fault detection.
2. **Paper A:** R205 (MSR 2026) — AI tests reach comparable coverage, larger branch-coverage gains **[B]**.
3. **Paper B:** R206 — coverage/mutation usefulness is context-dependent; R139 reward hacking **[B]**.
4. **Apparent contradiction:** the headline metric improves while its target property does not.
5. **Why it matters:** a safety-relevant measurement failure for a deployed agent class.
6. **Both agree:** LLM-generated suites can move coverage/mutation metrics.
7. **Differs:** coverage vs mutation vs true fault detection; code context; assertion content.
8. **Hidden variable:** assertion specificity relative to code context.
9. **Existing explanation:** R206 states context-dependence; not the controller.
10. **Sufficient?** No.
11. **Reconciliation experiment:** matched LLM vs human suites; joint coverage/mutation/assertion measures; vary code context.
12. **Data:** public repositories and histories; mutation operators; R205 commit corpus.
13. **Models:** four Flash models; open mutation tooling.
14. **Cost:** low-moderate.
15. **Contribution:** boundary condition — coverage gains track assertion specificity, not fault detection.
16. **Falsification:** coverage gains persist after controlling assertion specificity and mutation rises equally.
17. **Closest:** R205, R206, R139, R140, R141, R142.
18. **Novelty confidence:** medium.
19. **Feasibility:** high.
20. **Status:** PROMISING.

### ANO-11 — Tabular foundation models beat GBDT vs GBDT still win
**Existing explanation:** R210 (tuning/time budget), R211 (strategic reversal). **Sufficient?** Mostly. **Status:** CLOSED.

### ANO-12 — SHAP is consistent vs SHAP is unstable
**Existing explanation:** estimation variance under feature correlation and model stochasticity; stabilisation methods exist. **Sufficient?** Mostly. **Status:** CLOSED.

### ANO-13 — Self-reflection helps vs harms
**Existing explanation:** R145 (correlated errors); external-feedback dependence. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-14 — Adding verifier agents improves reliability vs adds failure surfaces
**Existing explanation:** R144, R145, R146, R157. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-15 — Evaluation awareness makes agents safer vs reverses
**Existing explanation:** none — R77 reports non-uniform effect without explaining sign. **Sufficient?** No, but area saturated and model access blocked. **Status:** UNCERTAIN.

### ANO-16 — Trajectory evidence says safe; state evidence says harmful
**Existing explanation:** R77 (durable effects without verifiable write events). **Sufficient?** Yes. **Status:** CLOSED.

### ANO-17 — Benchmark score predicts usefulness vs memory/contamination
**Existing explanation:** R200, R214, R215. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-18 — Internal contraction in RAS-Eval's scaling claim
**Existing explanation:** the abstract mischaracterises RQ2 ([A], method section). **Sufficient?** Yes. **Status:** CLOSED.

### ANO-19 — Self-correction recovers agents vs agents rarely recover
**Existing explanation:** R129, R130, R145. **Sufficient?** Yes. **Status:** CLOSED.

### ANO-20 — Agentic analysis inflates significance vs single analysis
**Existing explanation:** R131 (m-value/Agentic Bootstrap). **Sufficient?** Yes. **Status:** CLOSED.

---

## Part N — The kill pass

Each UNCERTAIN/PROMISING candidate was re-searched with the intent to kill.

**ANO-01 (UNCERTAIN) — KILLED on resources, not on science.** The contradiction dissolves once the competence requirement is recognised: AgentDojo's own metric and RAS-Eval's ASR both require the attacker's goal to be executed, so a positive capability–susceptibility relation and a negative one are not mutually exclusive. **[FACT]** MCPTox additionally confounds capability with reasoning mode (+27.8% ASR) (R06) **[A]**. Kill reason: (a) partly methodological; (b) any controlled decomposition needs a capability spread our four Flash models cannot provide (Part R); (c) adjacent work already occupies the space (R52, R74, R76, R77). Not a survivor.

**ANO-15 (UNCERTAIN) — KILLED as occupied + resource-blocked.** The phenomenon is real and unexplained in sign, but it lives in the saturated agent-security evaluation area the brief excludes, and R77's model set (GPT-5.2, Qwen3.7-plus) is not in our four Flash models. Kill reason: saturated area + access blocker.

**ANO-08 (PROMISING) — SURVIVES after one failed kill attempt.** The obvious kill is "R204 already explains it". R204 reports the detection effect **[B]** but, on the available evidence, does not provide a joint rate × detectability characterisation across grounding levels or name a controlling factor. The kill attempt is **not conclusive** because R204 could not be read (OpenReview browser challenge). This residual is flagged as an **[OPEN]** condition on the survivor: if the full text already contains the joint decomposition, ANO-08 must be closed.

**ANO-10 (PROMISING) — SURVIVES.** The obvious kill is "R206 already says it is context-dependent". R206 supplies the *phenomenon* (context-dependence) but not the *controller*. The controlling factor (assertion specificity) is testable and named by neither R205 nor R206. Kill reason rejected.

---

## Part O — Survivors

Criteria from the brief: (1) real empirical contradiction/unexplained phenomenon; (2) not already explained; (3) scientifically important; (4) a controlled experiment distinguishes explanations; (5) feasible with our resources; (6) outcome changes understanding; (7) not merely a new benchmark score.

**SURVIVORS: 2** (as first returned)
* **S1 = ANO-08** — the grounding rate-versus-detectability inversion. **STATUS CHANGED: KILLED** in the hostile full-text verification at §Part O-bis.
* **S2 = ANO-10** — the AI-test coverage-versus-fault-detection reversal. **STATUS CHANGED: KILLED** in the hostile full-text verification at §Part P-bis (decision C, with E and F co-decisive).

**[OPEN] S1 carried a live kill risk** (R204 unread). The risk materialised: the full text reports both the trade-off and its explanation. See §Part O-bis.

---

## Part O-bis — S1 hostile full-text verification (post-audit)

**Decision: KILL — PRIOR WORK ALREADY EXPLAINS IT (option C), with a strong secondary finding that the proposed variable is a relabelling of existing constructs (option G).**

### 1. R204 identity and access

**[FACT]** R204 is *Retrieval-Augmented Language Models Evade Hallucination Detection*, an **anonymous ACL ARR 2026 May Submission 13595** (forum `l5vr0Q3uMX`), license CC BY 4.0, under review; an earlier version was ARR 2025 October submission 1348 (forum `n6NEjFa1hm`). No arXiv or published version was located, so the OpenReview copy **is** the primary source.

**[FACT]** `read_url` and `r.jina.ai` are both redirected to OpenReview's browser-verification challenge, so a scripted full-text read is impossible. The **28-page PDF (683,442 bytes) was read in full** through the browser panel (which passed the challenge) by extracting its text with pdf.js in the page context. The abstract was independently cross-checked against the OpenReview v2 API (`/notes?forum=l5vr0Q3uMX`). This upgrades R204 from label **B** to **A** in `research/tables/sources.csv`.

### 2. Task 2 — is the anomaly real? (A independent; B independent; C fails)

| Claim | Supported? | Evidence (verbatim) | Location | Interpretation |
|---|---|---|---|---|
| **A. Grounding improves the answer-level metric** | **Yes** | vanilla RAG and InstructRAG "well outperform the non-RAG baseline in answer accuracy across all datasets" | §2.2 Finding 1; Table 1 | Established; note this is *accuracy*, not a directly measured hallucination rate |
| **B. Grounding lowers detectability of the remaining errors** | **Yes** | automatic detectors: "RAG increases the false negative rate … from **17.6% to 34.2%** on average"; humans: "RAG increases the false negative rate of human judges by **5.4%**", Table 4 DeepSeek-R1 without RAG FNR **73.1** vs with RAG **78.5** | abstract; §3; Table 4 | The detectability effect is real, and is shown for **both** automated (recall/FNR) and human detectors |
| **C. The literature does NOT already explain A+B** | **No** | R204 itself states the mechanism: "the inclusion of **references** can create a **veneer of authority** that masks the underlying hallucinations"; "the **sycophancy** problem in RAG hallucination detectors"; annotators "are more likely to accept the response as correct despite the possibility that the references themselves may contain errors"; and preference training "manifests in **heavier citation** of retrieved information and **significantly longer answers**" | abstract; §3 discussion; §4 | The paper names the phenomenon **and** its explanation, so C fails |

**[INFER]** The three quantities the brief warned not to conflate are distinguished in R204: it reports *false-negative rate* (= 1 − detector recall) on hallucinated items, not overall detection accuracy, and it reports a separate human-annotator FNR. The claimed anomaly is therefore not a definitional artefact — it is real. But it is **already explained by the paper that reports it**.

### 3. Task 3 — prior explanations of the trade-off

**[FACT]** A second, independent line of work explains why grounded-model errors resist surface detectors:

* **R216 (The Semantic Illusion, arXiv:2512.15068):** "on real hallucinations from RLHF-aligned models (HaluEval), the same methods fail catastrophically, yielding 100% FPR at target coverage"; "the hardest hallucinations are **semantically indistinguishable from faithful responses**".
* **R217 (legal-RAG reliability)** and **R218 (reference/citation-hallucination detection)** show that the reference/citation surface is an independently studied error source, and that RAG does not eliminate hallucination.

**[INFER]** The mechanism S1 proposed to discover — grounded errors become plausible because they carry evidence-like markers — is stated by R204 and mechanistically corroborated by R216. **Classification (Task 4): situation 1 and 2 — the trade-off was directly reported and its explanation (reference authority / sycophancy) was already identified.** Not situation 4 or 5.

### 4. Task 5/6 — kill arguments and the "attribution structure" construct

**[FACT]** The decisive kill is not experimental but bibliographic: **R204 already performs the proposed experiment.** It varies grounding level (without RAG / vanilla RAG / InstructRAG) across three QA datasets and measures answer quality and detector performance jointly for four automatic detectors plus human annotators. The proposed reconciliation experiment in ANO-08 is therefore essentially a partial replication of R204.

**[INFER]** Task 6: "attribution structure" does not survive as a distinct explanatory construct. In R204 the controlling signal is **reference presence and citation volume**, i.e. the established constructs of **provenance surface, citation correctness and over-reliance / authority bias**, plus **answer length** (R204 explicitly reports longer answers after preference training). Established adjacent constructs already name this: *faithfulness* and *groundedness* (support of each claim by retrieved context) and *citation/reference hallucination* (R218). No operational definition of "attribution structure" was found that is not a re-description of (i) reference/citation presence and quality, and (ii) claim-to-evidence support — the latter being textbook faithfulness/groundedness. **This is option G.**

The residual ideas were considered and rejected: (a) a formal rate×detectability *law* — the direction and mechanism are already given, and the two quantities are already measured jointly in R204; (b) the DPO/KTO result — already published by R204 (+53.3% FNR); (c) a "human vs automated" decomposition — R204 already reports both.

### 5. Decision and consequence

**Decision: C (KILL — PRIOR WORK ALREADY EXPLAINS IT); secondary G (the proposed variable is largely a renaming).**

* No Task 8 experiment is warranted.
* `research/tables/empirical-anomaly-matrix.csv` — **ANO-08 status changed PROMISING → CLOSED**; `existing_explanation`, `explanation_sufficient`, `novelty_confidence` and `feasibility` updated; `closest_related_work` now includes R216/R217/R218.
* `research/tables/sources.csv` — R204 upgraded B → A; R216, R217, R218 added.
* **Live survivors after verification: 0 (S1 killed; S2 subsequently killed at §Part P-bis).**

**[OPEN]** S2 was subjected to the same hostile test and killed; see §Part P-bis.

---

## Part P-bis — S2 hostile full-text verification (post-audit)

**Decision: KILL — PRIOR WORK ALREADY EXPLAINS IT (option C). Co-decisive: E (the alleged contradiction is a measurement mismatch) and F ("assertion specificity" is not novel).**

### 1. Tasks 1–2 — the two sources, verified in full

**[FACT]** **R205** is *Testing with AI Agents: An Empirical Study of Test Generation Frequency, Quality, and Coverage* (Yoshimoto, Fujita, Horikawa, Feitosa, Kashiwa, Iida; MSR 2026 Mining Challenge poster; arXiv:2603.13724; DOI 10.1145/3793302.3793620). The abstract page and the **full 5-page PDF were read** (browser + pdf.js, because `read_url` rejects `application/pdf`). **Upgraded B → A.**

**[FACT]** **R206** is *Do Coverage and Mutation Scores of LLM-Generated Test Suites Correlate with Their Effectiveness? (Replicability Study)* (Zhao, Zhou, Cohen; University of Toronto; **ISSTA 2026**, PACMSE vol. 3, DOI 10.1145/3832093; arXiv:2607.22880). The **full HTML article was read** through §5.3. **Upgraded B → A.**

### 2. Task 3 — reconstructing the alleged contradiction (it is a measurement mismatch)

| Dimension | R205 | R206 | Comparable? |
|---|---|---|---|
| Task | frequency/structure/coverage of AI tests in real repos | correlation of coverage/mutation with real-bug detection | **No** |
| Code domain | real-world JS/TS repos (AIDev) | Java (Defects4J) | No |
| Language | JavaScript/TypeScript | Java | No |
| Model | agentic coding tools in AIDev commits | 11 SOTA LLMs (13 settings) | No |
| Test-generation method | observational (merged commits) | controlled white-box prompts | No |
| Coverage definition | project coverage impact of commits | CodeCover statement/branch/MCC per suite | No |
| Fault definition | **none measured** | effective test passes on fixed, fails on buggy | **No** |
| Mutation operator | **none** | PIT (raw + normalized) | **No** |
| Fault-detection metric | **not measured** | bug-detection ratio | **No** |
| Evaluation dataset | AIDev commits | Defects4J (318 focal methods) | No |
| Unit of analysis | commit / project | focal method / suite | No |
| Statistical design | descriptive, p-values on structural diffs | Pearson r and Kendall tau at three granularities | No |

**[INFER]** R205 measures coverage only; R206 measures correlations including real-bug detection. They cannot contradict each other because they do not measure the same dependent variable. **The "coverage up, fault detection not" pairing is a measurement mismatch (option E).**

### 3. Tasks 4–5 — is "coverage does not imply fault detection" already established? Yes, since 2014

**[FACT]** R206's framing states the classical result: for human-written tests, "correlations among coverage, mutation, and real-bug detection can largely vanish once test suite size is controlled" (Inozemtseva & Holmes 2014, R219; Papadakis et al. 2018, R220). **[FACT]** R206 replicates this **for LLM-generated tests** at ISSTA-2026 scale (101,123 cases) and finds it **context-dependent**, with coverage *useful* for cross-model comparison in regression/assumed-bug-free settings (inter-model branch coverage vs bug detection r = 0.86, p = 1.6e-4). **[FACT]** R205's full text **measures no fault detection at all** and states the mutation question as its own future work, verbatim: *"First, mutation testing should determine if the high assertion density of AI tests translates into superior fault-detection capabilities."*

**[INFER]** The anomaly is not an unexplained pattern: it is a *long-established* software-testing fact, a *named open question* in R205, and a *published answer* in R206.

### 4. Task 6 — is "assertion specificity" a new explanatory variable? No

**[FACT]** R205 already measures `#assertions` and reports AI tests have **higher** assertion density (median 2.00 vs 1.00, p < 0.001). The proposed mechanism is the established construct **assertion/oracle strength**, and it is already linked to mutation/fault detection in peer-reviewed work: R221 (ASE 2025 - LLM oracles average 43% mutation score vs 45% human), R222 ("implementation-derived assertions and shallow scenarios" -> poor mutation performance), R223 (a named "weak-assertion failure mode"). **[INFER]** "Assertion specificity" is a rename of assertion strength / oracle quality (option F), and R205's own direction (AI tests have *more* assertions) undercuts the hypothesis.

### 5. Tasks 7–10 — competing studies, identifiability, feasibility

**[FACT]** R206 is the directly competing study: same construct space (coverage, mutation, real-bug detection) on LLM-generated tests, at scale and at a top venue. **[INFER]** No additional study is warranted; a run on our four Flash models would be a *model-substitution* variant of R206, which the brief forbids as a rescue. Task 9's identifiability work (separating assertion specificity from input quality, suite size, coverage, mutation operators, model capability and prompt effects) is moot once the kill is established, and mutation-as-a-proxy-for-real-defects is itself contested (R220, R224).

### 6. Decision and consequence

**Decision: C (KILL — PRIOR WORK ALREADY EXPLAINS IT). Co-decisive: E (measurement mismatch) and F (assertion specificity is not novel).**

* `research/tables/empirical-anomaly-matrix.csv` — **ANO-10 status changed PROMISING → CLOSED**; `existing_explanation`, `explanation_sufficient`, `novelty_confidence`, `feasibility` and `closest_related_work` updated.
* `research/tables/sources.csv` — R205 and R206 upgraded B → A; R219–R224 added.
* **Live survivors after both verifications: 0.**

---

## Part P — Deep analysis of survivors (as originally recorded)

### Survivor 1 — ANO-08: the rate-versus-detectability inversion under grounding

**1. Scientific question.** Does retrieval grounding trade hallucination *frequency* for hallucination *detectability*, such that the net reliability benefit is smaller than the reported rate reduction?

**2. Competing explanations.**
* **H1 (attribution structure).** Grounding converts blatant fabrications into fluent, citation-flavoured misattributions; the residual error is more plausible, so detectors miss it. **[HYP]**
* **H2 (surface nuisance).** The detectability loss is a length/fluency/format artefact of judge or human perception, not of the error's semantics — a known judge-bias family (R78, R79). **[HYP]**
* **H3 (rate measurement).** There is no real inversion: the two papers use different detectors and definitions of "hallucination", so rate and detectability are not commensurable. **[HYP]**

**3. Discriminating experiment.** Hold questions, model, and ground truth fixed. Vary grounding level (none, naive RAG, answer-cited RAG, agentic RAG). For each generated answer, obtain (i) a hallucination-rate label and (ii) a detectability label from a held-out human-verified set plus a calibrated automated detector. H1 predicts detectability loss scales with the *attribution structure* of the residual error (e.g., supported-sounding vs unsupported spans) after controlling length/fluency. H2 predicts detectability loss is fully explained by length/fluency. H3 predicts the two labels are not comparable at matched definitions.

**4. Required controls.** Model checkpoint; decoding configuration; question set; answer length (regressed out); detector prompt family; RAG retriever and corpus.

**5. Primary outcome.** A joint curve: hallucination rate and detection false-negative rate as functions of grounding level, plus the fraction of detectability loss attributable to attribution structure versus surface nuisance (variance decomposition).

**6. Expected contribution.** An explanatory law: **net reliability of grounding = f(rate reduction, detectability loss)**, and the claim that rate-only reporting is insufficient. This is the Part Q form "phenomenon X occurs because factor Y controls it" (Y = residual-error attribution structure).

**7. Falsification.** If detectability loss is fully mediated by length/fluency (H2), or if the two measurements are incommensurable (H3), the contribution collapses to a reporting recommendation.

**8. Resource requirement.** Four Flash models (DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash; Solar Mini 4 excluded per R38); public QA datasets with answer spans; a small held-out human detection label set; a calibrated automated detector. No GPUs. Modest API spend.

**9. Reproducibility.** High — public data, deterministic pipeline given fixed checkpoints; API model revision pinning is the main hazard (R35–R38).

**10. Publication potential.** Measurement-validity / trustworthy-ML venues; RAG and hallucination communities; human-factors/evaluation.

---

### Survivor 2 — ANO-10: the coverage-versus-fault-detection reversal in AI-generated tests

**1. Scientific question.** When LLM-generated test suites raise coverage, does the gain correspond to real fault detection, and what factor controls the correspondence?

**2. Competing explanations.**
* **H1 (assertion specificity).** Coverage gains come from executing code without asserting on it (tautological/assertion-free tests); the controller is the ratio of assertions to executed statements/branches. **[HYP]**
* **H2 (code context).** The reversal is driven by whether the code is a bug-fix/regression context or new-feature context, independent of assertion content (R206's "context-dependent" reading). **[HYP]**
* **H3 (metric artefact).** Coverage and mutation measure different things by construction; the "reversal" is a metric-definition artefact rather than a property of AI tests. **[HYP]**

**3. Discriminating experiment.** On matched code, generate suites with the four models and with humans. Jointly measure line coverage, branch coverage, mutation score, assertion count and assertion density. Vary code context (bug-fix vs new-feature) and the generation prompt (with vs without explicit assertion instructions). H1 predicts mutation score tracks assertion density after controlling coverage, and context matters little once assertion density is held. H2 predicts context dominates after controlling assertion density. H3 predicts no model-vs-human difference once metrics are defined identically.

**4. Required controls.** Repository and commit; language; mutation operator set; test-runner version; prompt; decoding; test-suite size (regressed out).

**5. Primary outcome.** Partial correlation of assertion density with mutation score at fixed coverage, and the model-vs-human difference in mutation score after controlling coverage and assertion density.

**6. Expected contribution.** A boundary condition: **coverage gains from AI tests track assertion specificity, and above a coverage level the human–AI fault-detection gap is explained by assertion density** — the Part Q form "previously undocumented boundary condition Y for method X".

**7. Falsification.** If AI and human suites have equal mutation scores at equal coverage and equal assertion density, the anomaly is a metric artefact and no contribution remains.

**8. Resource requirement.** Four Flash models; public repositories; open-source mutation tooling (e.g. mutmut, PIT, Stryker families); the R205 commit corpus as a sampling frame. No GPUs; low API spend.

**9. Reproducibility.** High — open repositories, pinned tooling, deterministic mutation operators.

**10. Publication potential.** Software-engineering research (MSR/ICSE/FSE) and the emerging AI-for-testing community; measurement-validity audiences.

---

## Part Q — Explanatory contribution check

**[FACT]** Both survivors pass the Part Q test: neither claims merely that "method X performs differently".
* **S1** claims: *the net reliability of grounding is controlled by the attribution structure of the residual error, so rate and detectability must be reported jointly.*
* **S2** claims: *coverage gains from AI tests are controlled by assertion specificity, establishing a boundary beyond which coverage stops tracking fault detection.*

**[INFER]** Both are reconciliations or boundary conditions of the permitted forms, not replication and not a new benchmark score.

---

## Part R — Resource constraint compliance

**Available models:** DeepSeek V4.1 Flash, MiMo 2.6 Flash, GLM 5.3 Flash, Solar Mini 4.
* Both survivors use only these Flash-tier models and require **no capability spread**.
* **[FACT]** Solar Mini 4 is released ≈2026-09-22 with no pinned revision history and is excluded (R38) **[A]** for reproducibility reasons.
* Both survivors use public datasets, public code, open tooling, modest API usage and local statistical analysis.
* Rejected candidates that required frontier-only models, GPU clusters or confidential data: **ANO-01** (capability spread), **ANO-15** (non-Flash model set), **ANO-03** (serving-level control).

---

## Part S — Source registry and artifacts

**Updated:** `research/tables/sources.csv` — added R200–R215 (16 new records):
R200 METR maintainer-merge note **[A]** · R201 CoT length **[A]** · R202 SAS vs MAS **[A]** · R203 Judge's Verdict **[B]** · R204 RAG evades hallucination detection **[B]** · R205 MSR 2026 test generation **[B]** · R206 coverage/mutation context-dependence **[B]** · R207 intelligence degradation **[B]** · R208 Context Rot **[B]** · R209 nondeterminism **[B]** · R210 TabArena **[B]** · R211 strategic tabular **[B]** · R212 self-reflection **[B]** · R213 deterministic-settings nondeterminism **[B]** · R214 OpenAI SWE-bench **[B]** · R215 SWE-bench memorisation **[B]**.

**Created:** `research/11-empirical-anomaly-map.md` (this file).

**Created:** `research/tables/empirical-anomaly-matrix.csv` — 20 candidates × 20 fields (21 columns incl. `anomaly_id`), all fields quoted; **validated**: 21 rows, uniform 21 columns, no duplicate IDs; statuses CLOSED 16, UNCERTAIN 2, PROMISING 2.

**[OPEN] Outstanding verification burden before any survivor is load-bearing:** read R204 and R206 in full (both currently label B) and confirm that neither already contains the joint decomposition / controlling factor this phase claims is missing.

---

**PHASE 11 COMPLETE — SURVIVORS: 2** (original). **After the S1 verification (§Part O-bis): SURVIVORS: 1. After the S2 verification (§Part P-bis): SURVIVORS: 0 → NO SURVIVOR.**
