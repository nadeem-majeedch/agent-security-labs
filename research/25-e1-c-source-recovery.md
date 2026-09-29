# Phase 20 — Step 6: E1-C Source Recovery and Closure

**Phase:** 20 — Step 6 (decisive source recovery and E1-C closure)
**Date:** 2026-09-29
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs.git`
**HEAD at audit:** `6802c81`
**Prior audits:** `research/20-research-positioning-audit.md`, `research/21-education-literature-hostile-audit.md`, `research/22-e1-fulltext-reaudit.md`, `research/23-publication-gate-audit.md`, `research/24-decisive-prior-art-closure.md`
**Deliverable:** this file only (`research/25-e1-c-source-recovery.md`). No paper was drafted, no study designed or implemented, no data collected, and no source, test, lab YAML, policy, scenario, CI, MkDocs or site file was modified.

---

## 1. Status

**PASS — audit completed.**

This step performed one final, tightly scoped attempt to close the decisive E1-C prior-art uncertainty carried by `research/22` §10, `research/23` §10 and `research/24` §14. It retired the *tooling* blocker that defeated Step 5 and read the two decisive near-neighbours at full-text level, plus the official record of the third.

Terminology is preserved exactly and was not altered. The E1 question (`research/21` §2, `research/22` §2, `research/23` §2, `research/24` §2) is unchanged:

> **E1.** Does a trace-first deterministic lab methodology improve novice understanding of the **request → policy decision → execution → result** distinctions in **agent-security** workflows?

The component definitions E1-A … E1-H are those of `research/23` §2 (trace-first instruction; deterministic/synthetic agent-security environment; explicit four-stage separation; trace reading as primary learning activity; novice learners; agent/LLM/tool-use security context; measured conceptual understanding; reproducible educational artefact). They are used verbatim and are **not** redefined here. The decisive construct remains:

> **E1-C** — **Explicit separation of `request → policy decision → execution → result`** as *named, observable, distinct* concepts.

E1-C was decomposed for inspection using the brief's own sub-elements (E1-C1 request; E1-C2 policy/authorization decision; E1-C3 execution; E1-C4 result; E1-C5 observable trace/event structure; E1-C6 learner actually distinguishes the stages).

**Phase 17 remains CLOSED.** No closed security-research direction (benchmark/scoring, attack-success measurement, model-propensity measurement, detector research, policy-effectiveness claims, real-LLM behavioural experiments, real-world leakage experiments, provider integration, network functionality) was reopened, and E1 was not redefined to rescue novelty.

**Research boundary (restated in full in §16):** this step establishes **no** research novelty, publication acceptance, educational effectiveness, causal learning effects, security effectiveness, model behaviour, benchmark validity or measurement validity. It determines the evidence status of E1-C prior art only.

---

## 2. Sources Investigated

Priority order as specified by the brief.

| Priority | Source | Identifier | Why it matters |
|---|---|---|---|
| 1 | Wilson, *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach* | JCERP Vol. 2026 No. 1 Art. 2 · DOI `10.62915/2472-2707.1268` | The closest located match to E1's *genre*: a peer-reviewed, hands-on LLM-security lab with measured learning outcomes for novice (graduate) learners (`research/22` §5.1; `research/24` §3) |
| 2 | Wilson, *A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation* | JCSC 41(4):173–182 (2025) · ACM DL `10.5555/3787712.3787744` | The source that `research/22`/`research/24` called "ACM 2025": a build-and-attack RAG lab, the second half of the decisive pair |
| 3 | Devadiga, Kuzminykh, Cao & Ghita, *A Virtual Lab for Learning AI Security and Adversarial Prompt Engineering* | ITiCSE 2026 V.1 pp. 107–113 · DOI `10.1145/3803400.3809384` | Newly surfaced in `research/24` §13 as a leading-venue AI-security virtual lab and therefore a potentially **closer** near-neighbour than either Wilson source |

Plan-of-record anchors recovered from the prior audits and re-confirmed, not changed:

- **Exact author identifications.** Wilson is a single author — **Dominic A. Wilson, University of Findlay, ORCID `0000-0001-6356-0871`** (the ORCID is printed on the JCERP 2026 title page). Devadiga et al. is a **different, independent** team: Dhanraj Jagadish Devadiga, Ievgeniia Kuzminykh, Hannah Cao (Department of Informatics, King's College London) and Bogdan Ghita (School of Engineering, Computing and Mathematics, University of Plymouth).
- **DOI/venue corrections to `research/24`.** None were required for Wilson 2026 or the JCERP venue. One classification detail is corrected: `research/24` §3 recorded Wilson 2026 as "GOLD open access" (Semantic Scholar). OpenAlex classifies the same work as **`oa_status: diamond`**, `is_oa: true`, `any_repository_has_fulltext: true`. Both are metadata classifications of the *same* fact — the article is fully open access under a CC-BY licence — so nothing substantive changes. `research/24`'s designation of the JCSC 2025 record as closed access is confirmed by Semantic Scholar (`isOpenAccess: false`, `openAccessPdf.url: ""`, abstract elided by the publisher).

---

## 3. Retrieval Results

The Step 5 blocker was diagnosed in `research/24` §4 and §17 as **tooling, not access**: the Wilson 2026 PDF is served under CC-BY but the audit's server-side page reader rejected `application/pdf`; and ACM DL returned 403 to that reader for everything. This step changed the retrieval method rather than the sources, and both blockages were retired.

| Source | Route used in this step | Result |
|---|---|---|
| **Wilson 2026** | The publisher's own CC-BY PDF, retrieved as an **archived copy held by the Internet Archive Wayback Machine** (snapshot `20260609213721` of `digitalcommons.kennesaw.edu/cgi/viewcontent.cgi?article=1268&context=jcerp`) | ✅ **474,426-byte PDF, 12 pages, text extracted in full** |
| **Wilson 2026** | Direct DOI resolution and the publisher landing page | ✓ landing page reachable (abstract + metadata); the live PDF endpoint answers **403** to non-browser HTTP clients behind the host's bot protection |
| **Wilson 2026** | OpenAlex / Semantic Scholar / Crossref metadata | ✓ metadata + abstract; `any_repository_has_fulltext: true`; no second host (DOAJ is metadata only) |
| **Wilson 2025 (JCSC)** | ACM DL in a **real local browser session** | ✓ **official abstract + full record obtained** (the same page the server-side reader could not reach) |
| **Wilson 2025 (JCSC)** | ACM DL "Get Access" state; Semantic Scholar; Crossref; Wayback; search for author/repository/preprint copy | ❌ **full text not reachable.** ACM DL marks it closed access ("Get Access", "Get this Article"); Semantic Scholar `isOpenAccess: false` with no OA PDF; no Wayback snapshot of the article or PDF; no repository, author-hosted or preprint copy located |
| **Devadiga et al. 2026** | ACM DL — record is marked **OPEN ACCESS**, so the PDF is legitimately free to download | ✅ **1,891,474-byte PDF, 7 pages, text extracted in full** |
| **Devadiga et al. 2026** | OpenAlex | ✗ reports `oa_status: closed` — **contradicted by the publisher's own page**, which carries the ACM "OPEN ACCESS" badge and a downloadable `PDF/eReader`; the CC-BY notice is printed on the PDF itself. OpenAlex is lagging for this record |

**Access discipline.** No paywall was circumvented, no authentication or credentials were used, no robots directive or technical protection was defeated, and no pirated copy was consulted. Wilson 2026 is open access under CC-BY and was read from an archived copy of the publisher's own file; Devadiga et al. is open access by the publisher's own designation; Wilson 2025 is closed access and was **not** obtained — only its freely visible official abstract was read. Where a browser was used (ACM DL), it was an ordinary read of public pages in the same way any reader would perform it.

**Method note (recorded for reproducibility).** PDFs were fetched by the local browser session, written to the operating system's temporary directory **outside** the repository working tree, and converted to text locally with Poppler `pdftotext`. No artefact of the retrieval entered the repository. Both temporary copies were deleted after extraction (§14, §15).

---

## 4. Wilson 2026

*Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach.* JCERP Vol. 2026 No. 1, Art. 2. DOI `10.62915/2472-2707.1268`. 12 pages; 8 sections; 31 references; 3 appendices.

### 4.1 Evidence level

**A — full text directly inspected.** The complete 12-page document was read, including both abstracts, the methodology, the architecture description, the lab-activity description, the results, the discussion, the limitations, the conclusion and **all three appendices** (Appendix A: the 12-item post-module quiz; Appendix B: the student feedback survey instrument; Appendix C: the student lab-log assessment rubric).

### 4.2 System-level findings

The platform is a **Retrieval-Augmented Generation (RAG) chatbot**, not a mediated agent. The paper's own architecture description: a document-based knowledge repository, an embedding index (FAISS) for semantic search, a retriever module, and an LLM for response generation; LangChain manages the retrieve-augment-generate workflow; Llama 3.1 (8B) and Phi-3 Mini run locally via Ollama. The stated pedagogical value of the multi-component design is *attack surface* — "Because the architecture integrated multiple application components (the LLM, the retrieval mechanism, the database, and the documents), it inherently offered a broader attack surface than a standalone LLM prompt."

There is **no tool-execution component, no policy engine, no authorization/mediation layer and no gateway** anywhere in the described architecture. Attacks are performed by prompting the chatbot: jailbreaking its guardrails, or extracting a planted secret from the knowledge base or system prompt. Nothing in the system decides whether an *action* may proceed; the only "decision" that exists is the model's own refusal-or-compliance behaviour.

**Term frequency in the full text (whole-word, case-insensitive):** `trace` **0**, `authorization` **0**, `policy decision` **0**, `deny` **0**, `approval` **0**, `mediation` **0**, `gateway` **0**, `access control` **0**, `permission` **0**, `tool call` **0**, `tool execution` **0**, `tool result` **0**, `audit trail` **0**, `provenance` **0**. The only near-terms present are `execution` **1** (in the phrase "attackers can escalate from simple command execution to jailbreaking", describing attack escalation in general), `policy` **2** (an external service's "usage policies"; and "AI policies" in the literature review), `log` **13** (students' own **lab logs** of prompts tried, plus a planted "confidential log file" used as a dummy training artefact), and `event` **1**.

### 4.3 Educational-level findings

Two labs, run in small teams over two weeks, framed as penetration-test / capture-the-flag exercises: **Lab 1 — jailbreaking the chatbot** (bypass the system instructions and content restrictions) and **Lab 2 — model inversion / data extraction** (recover a planted secret). The stated learning objectives are: identifying advanced LLM vulnerabilities; red-team exploration of an LLM system; analysis-and-mitigation thinking; and critical evaluation of AI security challenges. The design is grounded in Kolb's experiential-learning stages and mapped onto Bloom levels.

The data collection instruments are the decisive evidence for the educational level, because they define what learners were required to do:

- **Appendix A — post-module quiz (12 items).** Knowledge-recall and concept questions about attack types and defences. Item 3 asks how indirect prompt injection occurs in the RAG lab (answer: the model retrieves a poisoned document); item 4 asks why LLMs are vulnerable to prompt injection (answer: they cannot distinguish developer instructions from user input in the context window); item 7 asks which defence checks the model's output for sensitive keywords (answer: output filtering/redaction). No item asks a learner to distinguish a request from an authorization decision from an execution from a result, and no item involves reading an event stream.
- **Appendix B — feedback survey.** Six Likert items (concept clarity, engagement, skill acquisition, real-world relevance, difficulty balance, ethical awareness) and three open-ended questions about observed behaviours, effective attack strategies and proposed defences.
- **Appendix C — student lab-log rubric.** Lab logs are graded on *exploration volume* (number of prompt iterations), *strategy diversity* (number of distinct attack vectors) and *analytical reflection* (explaining why a prompt failed or succeeded). **The log is a student-written narrative of prompt-and-response attempts — it is not a machine-generated event trace, and it is not read or interpreted as one.**

The outcome evidence is module-level and conceptual, not stage-level: mean quiz score **88.1%** (SD 5.64), 100% pass rate against a 75% threshold, 90% self-reported confidence gain, and a 4.8/5 Likert rating for "the lab activities helped me learn about LLM security in depth."

Two findings sharpen the negative result:

1. **Provenance and placement distinctions are taught — but not the mediation distinction.** Item 3 distinguishes *where* an injection comes from (typed by the user vs. retrieved from the knowledge base), and item 7 distinguishes *where* in the pipeline a filter sits (input vs. output). Both are real pipeline-architecture distinctions. Neither is `request → policy decision → execution → result`, and neither has a learner-visible decision or execution stage.
2. **Agent/tool mediation is explicitly future work, not current content.** The paper states that instructors could "simulate an insecure plugin or **an agent with external tools** to illustrate other LLM risks", and the future-work paragraph promises "exploring other threat vectors (such as prompt spoofing in multi-modal models or **attacks on LLM-integrated agents**)". The agent/tool-mediated pipeline that E1-C concerns is named as something the lab does **not** yet do.

### 4.4 E1-C assessment

| E1-C element | Present? | Location | What the source actually does |
|---|---|---|---|
| E1-C1 — Request / invocation | **PARTIAL (no)** | §III–IV, Appendix A | The learner submits prompts to a chatbot; there is no agent action request or tool invocation. A prompt is a chat message, not an action request that could be mediated. |
| E1-C2 — Policy/authorization decision | **NO** | whole document (`authorization` 0, `policy decision` 0, `deny` 0, `approval` 0, `mediation` 0) | Nothing decides whether an action may proceed. Guardrail bypass is measured as *model* compliance/refusal behaviour in debrief discussion; it is never represented as a policy decision stage. |
| E1-C3 — Execution | **NO** | §III–IV | There is no execution stage. The chatbot's response *is* the outcome; nothing is invoked and run as a separate step. |
| E1-C4 — Result | **PARTIAL** | §IV, Table 2 | Attack outcomes exist (flag found/not found; partial extraction; quiz items about attacks), but they are not the result of an executed mediated action. |
| E1-C5 — Observable trace/event structure | **NO** | Appendix C | The only "log" is a student-authored prose journal of prompt attempts, graded on iteration count, strategy diversity and reflection. No machine event stream, no event schema, no distinguishable decision/execution events. |
| E1-C6 — Learner distinguishes the stages | **NO** | Appendices A–C | The learning objectives, quiz, survey and rubric all target vulnerability identification, exploitation skill and mitigation reasoning. No activity requires distinguishing request from decision from execution from result. |

**Wilson 2026: DOES NOT PREEMPT E1-C.** Evidence level **A**. In the `research/24` A–D scheme this is **C. RELATED BUT DOES NOT PREEMPT E1-C** — not merely "related", but related *and* fully inspected. Its overlap with E1 is genuine at the **genre** level (E1-E novices, E1-G measured outcomes, partial E1-B, partial E1-F) and absent at the **construct** level (E1-C, E1-A, E1-D).

---

## 5. Wilson 2025

*A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation.* JCSC 41(4):173–182, September 2025. ACM DL `10.5555/3787712.3787744`. DBLP `journals/jcscoll/Wilson25`.

### 5.1 Evidence level

**C — official abstract / official record only.** The full text was **not** obtained: the ACM DL record is closed access ("Get Access"; "Get this Article"), Semantic Scholar reports `isOpenAccess: false` with an empty `openAccessPdf.url` and a publisher-elided abstract, and no author manuscript, institutional-repository copy, accepted manuscript, preprint, conference version, university-hosted PDF or legitimate repository copy was located. There is no Wayback snapshot of either the article page or the PDF. **Nothing in this audit is inferred from search-engine snippets**; the abstract below is quoted from the publisher's own record as rendered in a browser session.

### 5.2 System-level findings

Not determinable at full-text level. From the official abstract: "an educational approach to LLM security using a Retrieval-Augmented Generation (RAG) framework in lab exercises. Students learn about LLM threats and mitigation strategies by building and attacking a RAG-based LLM system. Interactive labs integrate a vector database and LLM to simulate chatbot scenarios, where students can exploit and defend the system."

### 5.3 Educational-level findings

Not determinable at full-text level. The abstract reports "Results from a pilot module show high engagement and improved understanding of AI security. Practical experience in attacking and securing an LLM application reinforced theoretical lessons." No learning activity involving a decision stage or a trace is mentioned.

### 5.4 Relationship to Wilson 2026

**This confirms, at a stronger evidence level, the structural finding of `research/24` §7: the two "decisive sources" are one author's one line of work, not two independent prior works.**

- **Same author.** Both are by Dominic Wilson; the JCERP 2026 title page carries the University of Findlay affiliation and ORCID `0000-0001-6356-0871`, and the JCERP 2026 reference list cites the JCSC paper as **[24] "D. Wilson, 'A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation,' Journal of Computing Sciences in Colleges, vol. 41, no. 4, 2025."**
- **Same platform lineage.** The JCERP 2026 full text states: "**Prior work introduced a lab framework for prompt injection and data poisoning using a retrieval-augmented chatbot [24].** That approach demonstrated the value of a multi-component AI system for exposing students to LLM vulnerabilities. **This work builds on the spirit of such active learning but significantly extends the scope of attacks covered.**" The 2026 extension adds jailbreaking and model inversion to the 2025 prompt-injection-and-data-poisoning lab, on the same RAG-chatbot architecture.
- **Independent corroboration.** Devadiga et al. (2026) cite the two as separate items — **[31]** for the JCSC paper and **[32]** for the JCERP paper — and describe [31] as students who "built and attacked a RAG chatbot, learning about data poisoning and retrieval manipulation through direct exploitation", and [32] as "a structured module where students engaged in jailbreaking activities to exploit model alignment and privacy vulnerabilities, achieving 88% post-module quiz scores and 90% reported confidence."

**Consequence:** the JCSC 2025 lab is the **predecessor of the fully-read JCERP 2026 lab**, on the same architecture and by the same author, and the fully-read successor contains no E1-C element whatsoever. Three independent descriptions — the JCSC paper's own official abstract, the same author's extended 2026 report, and an independent third-party related-work summary — converge on the same characterisation: an exploitation-centric build-and-attack RAG lab with no policy/authorization decision stage and no trace-reading activity.

### 5.5 E1-C assessment

| E1-C element | Present? | Location | What the source actually does |
|---|---|---|---|
| E1-C1 — Request | **NOT DETERMINED** | — | Full text not inspected. Abstract reports lab exercises in which students attack a RAG system. |
| E1-C2 — Policy/authorization decision | **NOT DETERMINED** | — | Full text not inspected. Nothing in the accessible record describes a decision stage. |
| E1-C3 — Execution | **NOT DETERMINED** | — | Full text not inspected. |
| E1-C4 — Result | **NOT DETERMINED** | — | Full text not inspected. Abstract reports module-level "high engagement and improved understanding". |
| E1-C5 — Observable trace | **NOT DETERMINED** | — | Full text not inspected. Nothing in the accessible record mentions traces, logs or event streams. |
| E1-C6 — Learner distinguishes stages | **NOT DETERMINED** | — | Full text not inspected. |

**Wilson 2025: INSUFFICIENT EVIDENCE.** The strict rule of the brief applies — absence may **not** be inferred from a full text that was not read, and no element is recorded as `NO`. The classification is **not** PREEMPTS, and it is **not** a clean negative: what is recorded is that the **official abstract contains no positive evidence of E1-C**, that two independent descriptions converge on an exploitation-centric RAG lab, and that the fully-inspected 2026 extension of the same lab line contains no E1-C. That convergence substantially narrows the residual risk without eliminating it.

---

## 6. Devadiga et al. 2026

*A Virtual Lab for Learning AI Security and Adversarial Prompt Engineering.* ITiCSE 2026, Proceedings of the 31st ACM Conference on Innovation and Technology in Computer Science Education V.1, pp. 107–113. DOI `10.1145/3803400.3809384`. 7 pages. CC-BY (stated on the PDF). Authors: Dhanraj Jagadish Devadiga, Ievgeniia Kuzminykh, Hannah Cao (King's College London); Bogdan Ghita (University of Plymouth).

### 6.1 Evidence level

**A — full text directly inspected.** The complete 7-page paper was read: abstract, introduction and research gap, related work, lab design, the student learning workflow, the scaffolded modules, the evaluation, the discussion, the limitations, the future work and the reference list.

### 6.2 System-level findings

The **Adversarial AI Lab** is a virtual learning environment with two components: (1) an **isolated test network** — a Kali Linux VM with standard security tooling plus three vulnerable target machines (Metasploitable2, Ubuntu, Windows 10), resettable to a clean snapshot; and (2) an **LLM interaction layer** providing access to commercial APIs (GPT-4, Claude, Copilot, Gemini) and a locally hosted LLaMA.

The workflow is explicitly human-in-the-loop and is described in the paper's own words: the "Human Tester … **crafts adversarial prompts, submits them to the LLM layer, and then manually executes any generated payload within the isolated test network**." The paper then states: "**This clear separation between the AI interaction and the execution environment is a fundamental safety and pedagogical feature, teaching students the critical practice of validating AI output in a controlled space.**" Students "analyse outcomes using a logging framework" and compute metrics: **ASR** (attack success rate), **EGA** (exploit generation accuracy), **Refusal Rate**, **VES** (vulnerability exploit success, a qualitative score) and **MSP** (mitigation steps provided).

There is **no agent, no tool-calling interface, no policy engine, no authorization or mediation decision, and no gateway**. The only decision-adjacent concept is the LLM's own refusal to generate content, quantified as a *model behaviour statistic*: "Refusal Rate: Quantifies how often a LLM declined to generate exploit-related content due to safety or policy restrictions." The sandbox "allows students to execute" the payloads, but the sandbox does not *decide* anything.

**Term frequency in the full text (whole-word, case-insensitive):** `trace` **0**, `authorization` **0**, `policy decision` **0**, `deny` **0**, `approval` **0**, `mediation` **0**, `gateway` **0**, `access control` **0**, `permission` **0**, `tool call` **0**, `event` **0**, `agent` **4** (all four are "autonomous red-teaming agents" as related work or as planned future work — never a component of the lab). `policy` appears once, in the refusal-rate definition quoted above; `execution` appears as "remote code execution" and "the execution environment".

### 6.3 Educational-level findings

Three scaffolded modules (web, code, system-level vulnerabilities), each tiered Apprentice/Practitioner/Expert. The lab is supported by a **written worksheet** and an **assessment rubric**, and the worksheet is where the educational level becomes explicit. Per module, students must:

1. record their initial descriptive prompt **and the LLM's response**;
2. record their refined contextual prompt **and the generated payload**;
3. document **the manual test result (Success / Fail / Refusal)**;
4. calculate a simple metric (e.g. ASR over their 3–5 tests);
5. write a brief comparative analysis.

The final synthesis report is marked on use of evidence, application of the security metrics, and ethical reasoning.

This is the **strongest partial overlap with E1-C located in any prior source to date**, and it must be stated plainly rather than minimised:

- The worksheet **requires learners to keep the agent-free stages distinct**: prompt → model response → generated payload → manual execution result. Step 3 in particular distinguishes *generated* from *tested*, which is a real request/execution distinction in spirit.
- The AI-interaction-versus-execution-environment separation is not an accident of implementation: the paper calls it "a fundamental safety and **pedagogical** feature".
- Outcomes are **learner-recorded** rather than only system-recorded (the worksheet, not merely a server log), which is the kind of "who does the interpreting" property E1-C5/C6 care about.

What it nevertheless does **not** do:

- It has **no authorization or policy decision stage gating execution**. The nearest concept, refusal rate, is a statistic about *model* behaviour (how often the model declines to generate content) and is the object of study, not a decision layer of the system. Under E1-C2's own rule in the brief — "Do NOT count generic 'security checking' unless the source clearly distinguishes it as a decision stage" — a refusal-rate statistic is not a policy/authorization decision between request and execution.
- Its "logging framework" is the student's own written record, not a machine-generated, learner-interpreted event trace. There is no event schema, no distinguishable event types, and no activity in which a learner reads a trace and reasons from it. E1-C5 is therefore only partially satisfied at best, and E1-A/E1-D are absent.
- It has **no agent and no tool invocation** (E1-F absent as a *construct*; the lab is prompt-level LLM security), and agents appear only as future work.
- Its learning target is **attack assessment**: ASR, EGA, refusal rate, VES, MSP. The paper's own pedagogical claims are about moving students "from subjective opinion … to evidence-based argument" and about the dual-use/ethical dilemma — not about understanding a mediation distinction.
- It reports **no student study**: "While a formal study with students is planned", the evaluation is expert validation with three cybersecurity educators. E1-G is therefore absent here too.

### 6.4 E1-C assessment

| E1-C element | Present? | Location | What the source actually does |
|---|---|---|---|
| E1-C1 — Request | **PARTIAL** | §3.1 workflow; worksheet step 1–2 | The student crafts a prompt and submits it to the LLM layer. This is a chat request, not an agent action request or tool invocation; the model output (a payload) is the artefact, not the request. |
| E1-C2 — Policy/authorization decision | **NO** | §3.1 metrics | No decision gates execution. Refusal Rate is a model-behaviour statistic ("declined to generate … due to safety or policy restrictions"); execution of a generated payload happens unconditionally in the sandbox, and a refusal simply means there is nothing to execute. |
| E1-C3 — Execution | **YES** | §3.1; §5.1 | The payload is **manually executed** in the isolated test network, explicitly separated from the AI interaction and described as a pedagogical feature. This is a genuine, learner-performed execution stage — but it is human execution of generated content, not mediated tool execution. |
| E1-C4 — Result | **YES** | worksheet step 3; §3.1 | "Document the manual test result (Success/Fail/Refusal)"; outcomes feed ASR/EGA/VES. A distinct result stage exists. |
| E1-C5 — Observable trace/event structure | **PARTIAL** | §3.1; worksheet | A "logging framework" plus the written worksheet record prompt → response → payload → manual test result. This is a *learner-written* record, not a machine event trace with distinguishable event types; no trace-reading activity exists. |
| E1-C6 — Learner distinguishes stages | **PARTIAL** | worksheet steps 1–5; rubric | Learners must record prompt, response, payload and manual test result separately, and are marked on evidence use. But the required distinctions are *generation vs. testing* and *which model is better*, not request vs. decision vs. execution vs. result, and there is no decision stage to distinguish. |

**Devadiga et al. 2026: DOES NOT PREEMPT E1-C.** Evidence level **A**. In the `research/24` A–D scheme this is **B. PARTIALLY OVERLAPS E1-C** — the closest partial overlap found in any prior source so far, and the finding the hostile audit must carry forward. Partial overlap is not preemption: elements E1-C2 (decisive), E1-C5 and E1-C6 are not satisfied, and no mediation construct exists.

---

## 7. Semantic-Equivalent Search

### 7.1 Equivalence criteria actually used

Because the brief forbids broad-brush lexical matching, the equivalence test was run **conceptually**, against five explicit criteria. An apparent equivalent counts only if:

1. **Distinct stage** — it is a *stage in the lifecycle of one action*, not a category of content or a statistic.
2. **Gating** — the policy/authorization equivalent *conditions whether execution occurs* (allow / deny / require approval / mediation / an access-control or policy-evaluation decision), and is not merely a model declining to emit text.
3. **Same action** — all four stages belong to the *same* action: one request that is decided, executed, and yields a result.
4. **Learner-visible** — the stages are visible to the learner as events/states/logs/records (not merely present in the implementation).
5. **Learner-reasoned** — the learner is required to distinguish or interpret them.

Generic cybersecurity logs, debugging traces and generic program traces do **not** count automatically: they count only if criteria 2, 4 and 5 hold. This is the same standard as the brief's §8 caution and `research/22` §6.

### 7.2 Terms searched and findings

Both retrieved full texts were searched for the literal four-stage terms and for the semantic equivalents named in the brief — request / invocation, tool call, action request, authorization, access control, policy enforcement, policy evaluation, mediation, approval, permission decision, allow / deny, execution / action execution / tool execution, effect / outcome / result, provenance, event trace / execution trace / audit trace / agent trace / tool trace, and learner trace analysis.

| Stage | Semantic equivalents considered | Wilson 2026 (A) | Devadiga et al. 2026 (A) |
|---|---|---|---|
| Request | action, invocation, agent action, tool call, operation | **Fails criteria 1 & 3.** A prompt is a chat message; there is no action request that could be decided or executed. | **Fails criteria 1 & 3.** The prompt is a chat request; the generated payload is model output, not a request for an action that anything adjudicates. |
| Policy / authorization decision | authorization, access control, permission, guard, gate, approval, mediation, policy enforcement, policy evaluation | **Fails criterion 2.** Zero occurrences of authorization/decision vocabulary. Guardrail bypass and refusal are *model* behaviour measured in debriefs, not a decision stage. | **Fails criteria 2 & 3.** Refusal Rate is a statistic about the model declining to *generate content*, explicitly a model-safety behaviour ("due to safety or policy restrictions"). It does not gate execution of anything. |
| Execution | execution, tool invocation, operation execution, action execution, environment transition | **Fails criterion 1.** No execution stage; the chat response is the terminal event. | **Satisfies criteria 1, 3, 4 partly** for *manual payload execution* in the sandbox, and the paper elevates the AI/execution separation to a pedagogical feature. Still not *mediated* execution. |
| Result | response, observation, tool output, environment result, effect | **Fails criterion 3.** Results exist (flag found; partial extraction) but are not the result of an executed mediated action. | **Satisfies criteria 1, 3, 4 partly**: manual test result (Success/Fail/Refusal) recorded by the learner and turned into metrics. |
| Observable trace | event trace, execution trace, audit trace, agent trace, tool trace, provenance | **Fails criteria 4 & 5.** "Logs" are student prose journals graded on iteration count and reflection (Appendix C). | **Fails criteria 4 & 5 narrowly.** A logging framework plus a *learner-written* worksheet record; no machine event schema and no trace-reading activity. |

**Semantic-equivalence conclusion.** No inspected source teaches the same four-stage distinction under different vocabulary. Devadiga et al. is the only source in which a *request → generation → manual execution → recorded result* separation is **deliberately taught**, but the decisive middle stage of E1-C — an authorization/policy decision that gates execution — has **no equivalent** there, and the whole pipeline is a human-in-the-loop exploit-testing workflow rather than a mediated agent action.

---

## 8. E1-C Evidence Matrix

Only evidence supported by the retrieved material is recorded. `NOT DETERMINED` means the full text was not inspected; **no element is inferred as absent from an unread document**. The final row is this repository, included as a **comparator, not as prior art**.

| Source | Request | Policy/Authorization | Execution | Result | Observable Trace | Learner Distinguishes Stages | Evidence |
|---|---|---|---|---|---|---|---|
| **Wilson 2026** (JCERP, `10.62915/2472-2707.1268`) | PARTIAL — prompt to a chatbot; no action/tool invocation | **NO** — no decision stage exists (`authorization` 0, `policy decision` 0, `deny` 0, `mediation` 0) | **NO** — no execution stage | PARTIAL — attack outcome only (flag/secret found or not) | **NO** — student-written lab logs (Appendix C), not an event trace | **NO** — quiz/survey/rubric target attack concepts and mitigation reasoning | **A** |
| **Wilson 2025** (JCSC 41(4):173–182, `10.5555/3787712.3787744`) | NOT DETERMINED | NOT DETERMINED | NOT DETERMINED | NOT DETERMINED | NOT DETERMINED | NOT DETERMINED | **C** |
| **Devadiga et al. 2026** (ITiCSE, `10.1145/3803400.3809384`) | PARTIAL — student crafts a prompt; "human tester"; no agent/tool invocation | **NO** — refusal rate is a *model-behaviour statistic*, not a decision gating execution | **YES** — manual execution of the generated payload in the isolated test network, explicitly separated from AI interaction as a pedagogical feature | **YES** — manual test result (Success/Fail/Refusal) feeds ASR/EGA/VES | PARTIAL — a logging framework + learner-written worksheet record; no machine event trace, no event schema | PARTIAL — worksheet requires separate records of prompt / response / payload / manual test result; the required distinctions are generation-vs-testing and cross-model comparison, with no decision stage | **A** |
| *Agent Security Labs (comparator, not prior art)* | YES | YES | YES | YES | YES | YES | repository |

---

## 9. Strongest Hostile-Reviewer Interpretation

The brief requires the strongest preemption argument to be tested with evidence rather than dismissed. It is:

> **"Devadiga et al. (ITiCSE 2026) already teaches the separation that E1-C claims as its distinctive construct: a learner-initiated request, a recorded model response, a distinct execution stage in a separate sandbox — with the paper itself calling that separation 'a fundamental safety and pedagogical feature' — and a recorded test result, all captured in a structured record the learner must complete by hand. If E1-C is 'explicit separation of request → decision → execution → result as named, observable, distinct concepts', a hostile reviewer can say the *separation* is not new; only the vocabulary and the domain are."**

**Assessment of this argument on the evidence.** It is a serious argument, and it is the strongest one available against E1-C. It nonetheless **fails at the decisive element**:

- **The decision stage is absent, and it is not a technicality.** E1-C's third word is the one that carries the construct. Devadiga et al. contains **zero** occurrences of `authorization`, `deny`, `approval`, `mediation`, `gateway`, `access control` or `policy decision`. The only decision-like quantity, Refusal Rate, measures a *model's* willingness to emit content and is defined as a model-behaviour metric; it does not gate whether an action executes. The learner's execution step is unconditional — if a payload was generated, it is run in the sandbox.
- **The separation taught is generation-versus-testing, not request-versus-decision-versus-execution-versus-result.** What the worksheet enforces is: *what did you ask, what did the model give you, did it work, and which model is better.* That is an evaluation workflow. It is not the lifecycle of a mediated action.
- **There is no mediation infrastructure at all** — no agent, no tool call, no policy engine, no gateway — so the construct cannot be taught *about the system*, only about the LLM's own output policy.
- **The trace is a student's prose record, not an interpreted event stream.** E1-C5 and E1-C6 are only partially met, and E1-A and E1-D (trace-first instruction; trace reading as the primary learning activity) are absent entirely.
- **The educational target is different.** Assessment is on ASR, EGA, refusal rate, VES and MSP, plus ethical reasoning about dual use — not on understanding a mediation distinction.

**Conclusion on the hostile reading:** the strongest available argument establishes that an adjacent pedagogical separation *exists in the literature* (which is precisely why E1 is classified HIGH-RISK / INSUFFICIENTLY DISTINCT and not "novel"), but it does **not** establish preemption of E1-C. The correct description is **partial overlap**, not preemption.

---

## 10. E1-C Final Status

Per-source verdicts, using the brief's three categories, with the `research/24` A–D label given for continuity:

| Source | Evidence level | Verdict (brief §9) | `research/24` label |
|---|---|---|---|
| Wilson 2026 (JCERP) | **A** — full text | **DOES NOT PREEMPT** | C. Related but does not preempt |
| Wilson 2025 (JCSC) | **C** — official abstract only; full text closed access and not obtained | **INSUFFICIENT EVIDENCE** | D. Insufficient evidence (unchanged, on the full text) |
| Devadiga et al. 2026 (ITiCSE) | **A** — full text | **DOES NOT PREEMPT** | B. Partially overlaps (closest to date) |

**Combined E1-C status: `E1-C: NOT PREEMPTED BY INSPECTED SOURCES`** — recorded together, and without conflating, with:

- the explicit caveat that **one originally decisive source (Wilson 2025, JCSC 41(4):173–182) remains unread**, so absence of E1-C in *that document* is **not** asserted and its full-text status stays INSUFFICIENT EVIDENCE; and
- the explicit statement that **"not preempted by inspected sources" is not "novel."** No novelty is claimed for E1, for E1-C, or for the repository. Case B of the brief's decision tree is satisfied in substance; Case C applies to the one unread document only.

**Answer to the brief's §10 question — "Was the decisive full-text uncertainty actually closed?"**

### **PARTIALLY CLOSED.**

- **Closed:** Wilson 2026 (the first half of the decisive pair) was inspected at **full-text level (A)** and contains no E1-C element. The newly surfaced near-neighbour Devadiga et al. 2026 was also inspected at **full-text level (A)** and does not preempt E1-C.
- **Still open:** Wilson 2025 (the second half of the decisive pair) remains **closed access**; only its official abstract was inspected. No author manuscript, repository copy, accepted manuscript or preprint exists in any index consulted, and there is no archived copy.
- **Substantially narrowed:** the residual uncertainty for Wilson 2025 is much smaller than in `research/24`, because (i) its own official abstract describes an exploitation-centric build-and-attack RAG lab, (ii) the same author's *fully-read* 2026 extension of the same lab line on the same architecture contains no E1-C element at all, and (iii) an independent third-party related-work treatment describes it the same way.
- **Exactly what remains unknown:** whether the JCSC 2025 paper's *body text* (beyond its abstract) contains any authorization/policy-decision stage, any distinguishable event/state representation, or any trace/log-interpretation activity. Nothing more.

---

## 11. Overall E1 Classification

**Overall E1 classification: `HIGH-RISK / INSUFFICIENTLY DISTINCT` — UNCHANGED.**

The classification is **not** changed by this step, in either direction:

- **Not upgraded to PREEMPTED.** No source was shown, at a sufficient evidence level, to contain the E1-C learning object. Wilson 2026 (A) and Devadiga et al. 2026 (A) clearly do not; Wilson 2025 is unread.
- **Not upgraded to SURVIVES.** The brief forbids selecting survival merely because a source was not found, and the prior audits' reasons stand unchanged: the **genre is occupied** (hands-on LLM-security labs with measured outcomes for novices exist and are published); **E1-A, E1-B, E1-D, E1-E and E1-G have substantial prior-art coverage** (trace-based pedagogy; SEED/cyber-range reproducibility; novice populations; validated instruments for *other* constructs); **E1-C is the distinctive conceptual element**; and **E1-G — measured conceptual understanding of those distinctions — is the missing empirical outcome**. There is still **no evidence that novices actually experience the hypothesized E1-C confusion**.
- **Not moved to overall INCONCLUSIVE.** The evidence base for the *risk* assessment is unchanged and this step did not weaken it. What was inconclusive is one specific sub-question, and that sub-question is now **halved** (one of the two decisive documents resolved; one remaining).

What this step *does* add to the risk assessment is a sharpened, fully-evidenced negative: **the two closest same-genre prior works, read at full-text level, do not contain E1-C** — and, simultaneously, the **closest partial overlap in the literature to date** (Devadiga et al.) shows that an adjacent request→generation→manual-execution→result teaching separation, framed as a pedagogical feature, is already published in a leading computing-education venue.

---

## 12. Publication-Gate Consequence

**Publication gate: `HOLD` — UNCHANGED** (`research/23` §10; `research/24` §16).

| Gate | Status | Relation to this step |
|---|---|---|
| **Gate A — artefact publication readiness** | **NOT READY** (unchanged) | No stated design claim and no evaluation/adoption evidence. This step does not change that; it is a prior-art audit, not an evaluation. |
| **Gate B — experience-report readiness** | **NOT READY** (unchanged) | No written rationale synthesis and no light learner/instructor evaluation. Unchanged by this step. |
| **Gate C — empirical-study readiness** | **INSUFFICIENT EVIDENCE** (unchanged) | Still no participants, instrument, comparison condition, protocol, ethics approval, data or analysis. Unchanged by this step. |

Against the explicit conditions recorded in `research/23` §10 as things that would move the decision:

1. **Condition (1) — "the decisive full-text test resolves *against* preemption (Wilson 2026 / ACM 2025 contain no mediated-tool/authorization construct)": now *partially* satisfied.** Wilson 2026 resolves against preemption at full-text level; the JCSC 2025 half remains unresolved because the document is closed access. Because the condition names **both** sources and only one is settled, the condition is **not** met.
2. **Condition (2)** — evidence that novices do conflate request/decision/execution/result in agent-security tasks: **not addressed** by this step (no data, no observation, no study).
3. **Condition (3)** — a full-text, venue-targeted review (ACM DL, IEEE Xplore, TOCE, JCERP, SIGCSE/ITiCSE/ICER proceedings) confirming the construct is unoccupied: **partially advanced but not met.** Three decisive/priority sources were read or recorded at depth, and one of them (Devadiga et al.) was discovered only in `research/24`; the review is still web-search sampling, not a systematic database search.

**Gate consequence, stated factually:** resolving a prior-art uncertainty **removes (or retains) one uncertainty only. It does not create empirical evidence.** Half of the prior-art uncertainty is now removed for one decisive source and retained for the other, and **no new empirical evidence of any kind exists**. The gate therefore does not move. **No publication venue is recommended here, and no acceptance likelihood is estimated or implied.**

---

## 13. Remaining Uncertainty

1. **Wilson 2025 (JCSC 41(4):173–182) — full text.** Closed access at ACM DL; no OA PDF, author manuscript, accepted manuscript, institutional-repository copy, preprint, conference version or archived copy located. Only the official abstract was inspected. **This is the single remaining decisive document.**
2. **Newly surfaced same-author works (byproducts of the ORCID check in §2/§3, level C, not inspected in full).**
   - Wilson, *Operationalizing Supply-Chain Hygiene in Graduate IS Education: A Hands-On Module for Secure Software and AI/ML Pipelines*, JCERP DOI `10.62915/2472-2707.1301` (published 2026-06-29). Its **official abstract** was inspected (Crossref): deterministic Python environments, private package indexes, "CI policies that prohibit public fallback", SBOM/MBOM, "visibility of dependencies and provenance", "integrity enforcement by default", evidence-based risk triage. This is a supply-chain-hygiene module; its "CI policies" are build-configuration gates, not a learner-interpreted authorization decision in an action lifecycle, and it contains no described trace-reading activity. **No E1-C content at abstract level; full text not inspected (remains C).**
   - Wilson, *Scaling AI Security Pedagogy: From Local Labs to HPC-Enabled Red Teaming* (figshare presentation) — not retrieved; title/record only (C).
   - Wilson, *The Rise of the Agentic Era: Quantifying the Shift from Chatbots to Autonomous Security* (TechRxiv preprint, DOI `10.36227/techrxiv.177273622.27994930`) — not retrieved (the TechRxiv host answered 403 to this environment's client); title/record only (C). The title indicates agentic-security measurement, not education; it cannot be classified from a title.
3. **Devadiga et al. partial-overlap residue.** If that lab is ever extended with a mediation layer (its own future work proposes autonomous red-teaming *agents*), it would move materially closer to E1-C. On the inspected text it does not preempt.
4. **Coverage remains non-systematic.** No database search (Scopus, Web of Science, ACM DL search, IEEE Xplore) and no venue-targeted full-text review were performed; coverage is web-search sampling plus targeted API lookups (Crossref, OpenAlex, Semantic Scholar, ORCID) and Wayback retrieval.
5. **Terminology drift risk.** Sources using entirely different vocabulary for mediation (e.g. "guardrails", "policy enforcement point", "capability gating") could still be missed by the equivalence criteria in §7; the criteria are recorded so a future audit can challenge them rather than inherit them silently.

**What would close the gap (recorded, not performed):** obtaining the JCSC 2025 PDF through a library or institutional subscription to ACM DL (or an author copy obtained directly from the author); a systematic venue-targeted search; and reading the newly surfaced Wilson works listed in item 2.

---

## 14. Verification

Commands run for this step (read-only with respect to tracked files):

```
PYTHONPATH=src py -m pytest -q --tb=no
    -> exit 0; 694 tests executed (694 progress marks), zero failures/errors
PYTHONPATH=src py -m agentsec labs check
    -> LAB-00 … LAB-07 all PASS; "Result: 8/8 labs passed"; exit 0
py -m mkdocs build --strict
    -> exit 0; site built, no warnings/errors
git diff --name-only
    -> (empty) — no tracked file modified
git status --porcelain
    -> ?? research/20-research-positioning-audit.md
       ?? research/21-education-literature-hostile-audit.md
       ?? research/22-e1-fulltext-reaudit.md
       ?? research/23-publication-gate-audit.md
       ?? research/24-decisive-prior-art-closure.md
       ?? research/25-e1-c-source-recovery.md      <-- expected new file
```

- **No tracked file was modified** (`git diff --name-only` is empty).
- **Exactly one file was created by this step:** `research/25-e1-c-source-recovery.md`.
- **No source, test, lab YAML, policy, scenario, CI, MkDocs configuration or site file was changed.** `site/` is git-ignored build output and is not part of the tracked tree.
- The two PDFs retrieved for inspection and their extracted text were written to the **operating system's temporary directory, outside the repository**, and were deleted after the text was extracted; they were never part of the working tree.

---

## 15. Files Changed

| Path | Change |
|---|---|
| `research/25-e1-c-source-recovery.md` | **created** (this file) — the only change |
| everything else | **unchanged** |

No prior audit file (`research/20` … `research/24`) was altered.

**Git discipline — explicit confirmation:** no `git add`; **nothing staged**; **no commit**; **no push**; no reset; no checkout; no clean; no rebase; no amend. All Git operations remain manual and are left to the repository owner.

---

## 16. Conclusion

The tooling blocker that defeated Step 5 was diagnosed correctly and has been retired. Using an archived copy of the publisher's own CC-BY PDF and a real browser session with local PDF extraction, this step read **Wilson 2026 in full (level A)** and **Devadiga et al. 2026 in full (level A)**, and obtained the **official abstract of Wilson 2025 (level C)**.

Findings:

1. **Wilson 2026 does not preempt E1-C.** It is a RAG chatbot lab about jailbreaking and model inversion. It has no tool execution, no policy/authorization decision, no execution stage and no learner-interpreted trace; agent-mediated tool pipelines appear only as stated future work.
2. **Wilson 2025 (JCSC) remains INSUFFICIENT EVIDENCE** — it is closed access and its full text was not obtained. It is confirmed to be the **same author's predecessor of the same lab line**, on the same architecture, that the fully-read 2026 report extends.
3. **Devadiga et al. 2026 is the closest partial overlap found in any prior source to date** — it explicitly and deliberately teaches a *learner-initiated request → generation → manual execution in a separate sandbox → recorded result* separation, and calls that separation a pedagogical feature — but it has **no policy/authorization decision** (the decisive E1-C element), no mediation infrastructure, no agent/tool invocation and no machine event trace, and it targets attack-assessment metrics rather than a mediation distinction. **Partial overlap, not preemption.**
4. **The decisive gap is PARTIALLY CLOSED:** one of the two decisive documents resolved at full-text level; the other remains unread.
5. **E1-C: `NOT PREEMPTED BY INSPECTED SOURCES`** — explicitly not "novel", and explicitly not a claim of absence in the one document that could not be read.
6. **Overall E1 classification unchanged: HIGH-RISK / INSUFFICIENTLY DISTINCT.** Publication gate unchanged: **HOLD** (Gates A and B NOT READY; Gate C INSUFFICIENT EVIDENCE). The prior-art condition that would move the gate is only half satisfied, and closing a prior-art question creates no empirical evidence in any case.

**What this step does NOT establish** — explicitly, and it must not be read as establishing any of the following:

- **research novelty** — none is claimed for E1, for E1-C, for any component, or for the repository; E1 remains HIGH-RISK / INSUFFICIENTLY DISTINCT;
- **publication acceptance** — no venue outcome is predicted, implied or estimated;
- **educational effectiveness** — nothing here shows that any intervention, including this repository's labs, improves learning;
- **causal learning effects** — no design, no participants, no data, no analysis;
- **security effectiveness** — no security claim is made or measured;
- **model behaviour** — nothing here speaks to real model or agent behaviour; the repository's fixture is a fixture;
- **benchmark validity** — the repository is not a benchmark, and no inspected source is treated as one;
- **measurement validity** — no instrument was validated or proposed.

It also does **not** preempt or clear the unread document: Wilson 2025 is recorded as **INSUFFICIENT EVIDENCE**, and no inference of absence is drawn from its unread body. **Phase 17 remains CLOSED**, and no closed security-research direction was reopened.

**Stop condition observed:** the audit stops here. No paper was drafted, no study designed or implemented, and no data collected.

---

*End of Phase 20 — Step 6. The decisive prior-art question is PARTIALLY CLOSED; E1-C is NOT PREEMPTED BY INSPECTED SOURCES; one decisive document (Wilson 2025, JCSC 41(4):173–182) remains unread.*
