# Phase 20 — Step 7: Wilson 2025 Final Closure

**Phase:** 20 — Step 7 (final closure of the last unread source)
**Date:** 2026-09-29
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs.git`
**HEAD at audit:** `6802c81`
**Prior audits:** `research/20-research-positioning-audit.md`, `research/21-education-literature-hostile-audit.md`, `research/22-e1-fulltext-reaudit.md`, `research/23-publication-gate-audit.md`, `research/24-decisive-prior-art-closure.md`, `research/25-e1-c-source-recovery.md`
**Deliverable:** this file only (`research/26-wilson-2025-final-closure.md`). No paper was drafted, no study designed or implemented, no data collected, and no source, test, policy, lab YAML, scenario, CI, MkDocs, site, README, LICENSE or CITATION.cff file was created or modified.

---

## 1. Status

**PASS — the retrieval attempt was completed; the full text was NOT obtained.**

This step executed the ordered retrieval strategy of the brief in full and made a final, exhaustive legitimate attempt to locate an openly accessible copy of the last unread document in the Phase 20 audit:

> Dominic A. Wilson, *A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation*, **Journal of Computing Sciences in Colleges 41(4), 173–182 (2025)**, DOI `10.5555/3787712.3787744`.

**No legitimate copy of the full text exists in any location reachable from this environment.** The article is closed access at its publisher, no open-access copy exists in any repository or aggregator consulted, the DOI is not registered with Crossref (so no open-access metadata exists for it), and the two general scholarly indexes that might have surfaced an alternate version are gated by anti-automation measures which this audit declined to bypass.

Accordingly, and in accordance with the brief's rule that **absence must not be inferred from an unread document**, the source retains the status established in `research/25`:

> **Wilson 2025 — `INSUFFICIENT EVIDENCE` (evidence level C).**

E1-A … E1-H are used exactly as defined in `research/23` §2 and carried through `research/24` and `research/25`; E1-C was **not** broadened or redefined. The decisive educational construct remains:

> **request → policy/authorization decision → execution → result**

**Phase 17 remains CLOSED.** No closed security-research direction was reopened.

---

## 2. Target Source

| Field | Value |
|---|---|
| **Title** | *A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation* |
| **Author** | Dominic Wilson (single author) |
| **Venue** | *Journal of Computing Sciences in Colleges* (JCSC), Volume 41, Issue 4 |
| **Pages** | 173–182 |
| **Year / date** | 2025 (ACM DL publication date: 01 September 2025) |
| **Publisher** | ACM Digital Library, on behalf of the Consortium for Computing Sciences in Colleges (CCSC) |
| **ACM DL identifier** | `10.5555/3787712.3787744` |
| **DBLP key** | `journals/jcscoll/Wilson25` |
| **Semantic Scholar corpus ID** | `285103799` |
| **Access status** | **Closed access.** ACM DL presents "Get Access", "Sign in", "Get this Article"; Figures/Tables/Media tabs and Additional metrics are marked "Premium feature" |
| **Prior status (from `research/25` §5)** | Full text not obtained; official abstract obtained (level C); identified as the same author's predecessor of the same lab line later reported in JCERP 2026 |

**Relationship to the 2026 paper (established in `research/25` §5.4 at full-text level for the 2026 side).** The 2026 JCERP paper cites this paper as reference **[24]** and states: *"Prior work introduced a lab framework for prompt injection and data poisoning using a retrieval-augmented chatbot [24]. That approach demonstrated the value of a multi-component AI system for exposing students to LLM vulnerabilities. This work builds on the spirit of such active learning but significantly extends the scope of attacks covered."* The 2026 paper therefore describes itself as an **extension of the 2025 lab framework**, not as an unrelated study.

---

## 3. Retrieval Attempts

Every route in the brief's ordered strategy was attempted. Results are recorded verbatim as observed; where a route was blocked by an anti-automation measure, it was **not** bypassed.

| # | Route | Result |
|---|---|---|
| 1 | **ACM official record** (`dl.acm.org/doi/10.5555/3787712.3787744`) | ✅ Reachable. **Closed access** ("Get Access", "Sign in", "Get this Article"). Publicly visible: title, author, venue, volume/issue, pages 173–182, publication date 01 Sep 2025, the **complete abstract**, a partial reference list, "1 citation", "60 downloads". Figures/Tables/Media and "Additional metrics" are premium-gated. |
| 1b | **ACM DL eReader** (`/doi/epdf/…`) | ❌ **Redirects to the abstract page** — there is no free first-page/reader preview for this item. |
| 1c | **ACM DL PDF** (`/doi/pdf/…`, `?download=true`) | ❌ Entitlement required. The session is **not signed in and has no institutional entitlement** (the page offers only "Sign in"/"Get Access"). No purchase path, no credential use, no paywall circumvention was pursued. |
| 2 | **DOI landing page** (`https://doi.org/10.5555/3787712.3787744`) | ✅ Resolves, but via ACM. `10.5555/*` is an **ACM-internal prefix not registered with Crossref**; the Unpaywall API returns **HTTP 404 Not Found** for this DOI, i.e. **no open-access metadata exists for it**. |
| 3 | **Author's institutional profile** | ORCID `0000-0001-6356-0871` retrieved (printed on the author's 2026 JCERP title page). The works list **includes this paper with no URL** — no deposited, hosted or linked copy, in contrast to the 2026 JCERP paper, which links to its publisher page. |
| 3b | **University of Findlay (author's affiliation) profile / repository** | ❌ No publication repository or author-hosted copy located. |
| 4 | **Author's university repository** | ❌ None exists for this institution; nothing located. |
| 5 | **Institutional publication repositories** | ❌ **OpenAlex**: `is_oa: false`, `oa_status: "closed"`, `any_repository_has_fulltext: **false**`. **Semantic Scholar**: `isOpenAccess: false`, `openAccessPdf.url` empty, abstract elided by the publisher. |
| 6 | **Google Scholar indexed versions** | ❌ **Unavailable** — the session is intercepted by a bot check ("Please show you're not a robot"). **Not solved**, deliberately: defeating an anti-automation challenge is an access-control circumvention. |
| 7 | **Semantic Scholar** | ✅ Metadata retrieved — confirms venue, volume/issue, year, DOI, closed-access status and the absence of any OA PDF. |
| 8 | **OpenAlex** | ✅ Metadata retrieved — confirms closed status and no repository full text. |
| 9 | **CORE** (`core.ac.uk`) | ❌ The search service returned *"This page is not available now. Try again in a few minutes."*; the v3 API requires a key. |
| 10 | **Internet Archive / Wayback** | ❌ **No snapshot** of either the article page or the PDF (re-confirmed this step; also confirmed in `research/25` §3). |
| 10b | **Internet Archive Scholar** (`scholar.archive.org`) | ❌ **Unavailable** — the service interposes its own declared "**anti-scrape countermeasure**" (an ALTCHA proof-of-work challenge) before the first search. **Not solved**, deliberately. Its own page directs bulk access to a text-and-data-mining route that requires an account. |
| 10c | **fatcat / scholar.archive.org API** (`api.fatcat.wiki`) | ❌ Host unreachable from this environment. |
| 11 | **Author CV / publication list** | ✅ ORCID works list retrieved (see #3); no copy of this paper is linked. |
| 12 | **Accepted manuscript / preprint searches** (exact title; author + title; DOI; title fragments; author + "RAG security lab"; author + "retrieval augmented generation" + education; author + "LLM security education"; title + PDF; title + manuscript; title + repository; `filetype:pdf`) | ❌ **No preprint, accepted manuscript, author manuscript or conference version located.** |
| 13 | **University library catalogue metadata / subscription access** | ❌ Not available from this environment; the browser session carries **no institutional entitlement**, so no library-mediated access exists to record here. |
| 14 | **Legitimate institutional or author-hosted PDF** | ❌ None located. |
| 14b | **BASE** (`base-search.net`) | ❌ Request denied: *"Access denied for IP address … and user agent."* |
| 14c | **ResearchGate** | ❌ A search of the platform returns **no page for this paper** (results are unrelated RAG papers). |
| 14d | **Same author's open supplementary artefact (figshare)** | ✅ Retrieved, but it documents the **2026 JCERP** work, not the 2025 JCSC paper: *"This presentation shares the methodology and results of a hands-on cybersecurity curriculum **recently published in the Journal of Cybersecurity Education, Research and Practice (JCERP, January 2026)**."* It confirms only that the 2026 lab covers prompt injection, jailbreaking and model inversion within a RAG framework. It does **not** supply the 2025 content. |

**Not attempted, by rule:** pirated copies; authentication or credential sharing; paywall purchase paths; robots or anti-scrape challenge circumvention (Google Scholar, Internet Archive Scholar); any circulation of the user's session credentials.

**Conclusion of the retrieval attempt.** This environment has exhausted every legitimate route available to it. The 2025 paper is closed access and **no openly accessible copy is indexed anywhere** (OpenAlex, Semantic Scholar, BASE, CORE, ResearchGate, Wayback, ORCID, general web search, and `filetype:pdf` search all negative). The only remaining way to read it is **library or institutional subscription access, or a copy obtained directly from the author** — neither of which is available or authorised in this environment.

---

## 4. Evidence Level

> **C — official abstract / official record only.**

Levels B (substantial openly accessible body text) and A (full text directly inspected) were **not reached**, because no such text exists in any location reachable from this environment.

What *was* inspected at level C:

- the complete **official abstract** (publisher's own record);
- the complete bibliographic record (title, author, venue, volume/issue, pages, publication date, DBLP key, citation and download counts);
- the **access state** of every publisher endpoint;
- a **partial official reference list**, visible on the record: **[1]** L. Ammann & S. Ott, *Analysis of Risks and Mitigation Strategies in RAG – A Framework for Comprehensive Assessment* (2024); **[2]** S. Barnett et al., *Seven failure points when engineering a retrieval augmented generation system* (2024); **[3]** Cloud Security Alliance, *Mitigating Security Risks in Retrieval Augmented Generation (RAG) LLM Applications* (2023); **[4]** L. Derczynski et al., *garak: A Framework for Security Probing Large Language Models* (2024).

**Observation on the visible references (level C, recorded as an indication only, not as a finding).** Every reference visible in the public record is oriented toward RAG attack surfaces, RAG engineering failure modes, or automated LLM security probing. **None** is oriented toward access control, authorization, policy enforcement, mediation, audit logging or trace interpretation. This is consistent with an exploitation-centric lab and inconsistent with a mediation-oriented one — but it is a signal from a partial reference list, **not** evidence about the body text, and it is not treated as a finding about E1-C.

**Full text not obtained. Absence is not inferred.** Every element below that could not be read is recorded as `NOT DETERMINED`, with **no element recorded as `NO`**.

---

## 5. Full-Text Findings

**The full text was not obtained, so this section records what the official record establishes and marks everything else `NOT DETERMINED`.** The brief's "if full text is obtained" instruction is therefore not satisfied, and that fact is stated rather than papered over.

**Official abstract (publisher record, quoted in full):**

> "Large Language Models (LLMs) offer powerful language capabilities but also introduce security risks. This paper explores an educational approach to LLM security using a Retrieval-Augmented Generation (RAG) framework in lab exercises. Students learn about LLM threats and mitigation strategies by building and attacking a RAG-based LLM system. Interactive labs integrate a vector database and LLM to simulate chatbot scenarios, where students can exploit and defend the system. Results from a pilot module show high engagement and improved understanding of AI security. Practical experience in attacking and securing an LLM application reinforced theoretical lessons. This active learning approach demonstrates effectiveness and provides a template for integrating LLM security into cybersecurity education, training future professionals to secure AI systems."

### 5.1 Educational intervention

**What the record establishes:** a RAG-based educational intervention — lab exercises in which students **build and attack a RAG-based LLM system**, integrating a vector database with an LLM to simulate chatbot scenarios, framed as "exploit and defend"; a pilot module is reported with "high engagement and improved understanding of AI security".

**What is NOT determined:** the number and structure of labs; the module duration; the learning objectives; the assessment instruments; the cohort; whether the learners' activity is offensive, defensive or both beyond the phrase "exploit and defend"; the specific adversarial techniques covered.

**Independent description (level A, from a different document).** The fully-inspected 2026 JCERP paper describes this intervention as "**a lab framework for prompt injection and data poisoning using a retrieval-augmented chatbot**" — i.e. students build and attack a RAG chatbot around prompt injection and data poisoning. This is the same author's own characterisation of the same lab line in a full-text document, and it is **corroborated independently** by Devadiga et al. (2026, level A), whose related-work summary describes it as students who "**built and attacked a RAG chatbot, learning about data poisoning and retrieval manipulation through direct exploitation**". Both descriptions are recorded here **as evidence about the intervention's subject matter**, and neither is a substitute for inspecting the 2025 document itself.

### 5.2 Request / invocation

> **NOT DETERMINED.** Full text not inspected.
>
> Record-level indication only: the abstract describes interactive labs in a "chatbot scenario" in which students "exploit and defend the system". Nothing in the accessible record describes a tool invocation, an agent action request, or any request object that could be adjudicated before execution (compare `research/25` §4.2: the 2026 successor's architecture is a retrieve-augment-generate chat pipeline with **no** tool-execution component and no request/authorization model).

### 5.3 Policy / authorization

> **NOT DETERMINED.** Full text not inspected. **No `NO` is recorded**, because absence may not be inferred from an unread document.

This is the decisive E1-C element, and the accessible record contains **nothing** bearing on it: the abstract says nothing about authorization, permission, mediation, approval, allow/deny, access control or policy evaluation.

The brief's §5 caution is applied strictly here. The following are **not** policy/authorization decisions and would not satisfy E1-C even if present: RAG retrieval; context augmentation; model refusal; prompt filtering; content moderation; jailbreak resistance; model safety behaviour. Applying that distinction: the 2025 lab's subject matter, as described independently, is **prompt injection and data poisoning against a RAG chatbot** — i.e. the *retrieval and alignment* attack surface, not an authorization layer. Whether any safety mechanism in that lab functions as an authorization decision in the educational activity **cannot be determined** without the text.

### 5.4 Execution

> **NOT DETERMINED.** Full text not inspected.
>
> Record-level indication only: the abstract's verbs are "building", "attacking", "exploit", "defend" and "reinforced theoretical lessons". No distinct execution stage after a decision is described. In the fully-inspected 2026 successor there is no execution stage at all (`research/25` §4.4, E1-C3 = NO) — but that is a different document and is not used to infer the 2025 document's contents.

### 5.5 Result / effect

> **NOT DETERMINED.** Full text not inspected.
>
> Record-level indication only: module-level outcomes are reported ("high engagement", "improved understanding of AI security", "Practical experience … reinforced theoretical lessons"). Whether any per-operation result stage exists is unknown.

### 5.6 Trace / event representation

> **NOT DETERMINED.** Full text not inspected.
>
> Record-level indication only: the abstract contains no reference to traces, logs, event streams, execution states, audit records or provenance. No such concept appears in the public record for this paper. (The 2026 successor's "logs" are student-authored prose journals, not event traces — `research/25` §4.3.)

### 5.7 Learner activity

> **NOT DETERMINED.** Full text not inspected.
>
> Record-level indication only: the abstract describes students building, attacking, exploiting and defending a RAG-based system, "reinforc[ing] theoretical lessons". Nothing in the accessible record describes learners inspecting, classifying, explaining, distinguishing, tracing, debugging or being assessed on a distinction between an authorization decision and an execution.

---

## 6. E1-C Assessment

| E1-C element | Present? | Evidence | What the record actually shows |
|---|---|---|---|
| **E1-C1 — Request / invocation** | **NOT DETERMINED** | C | Chatbot-scenario interaction described; no tool/action invocation described; no `NO` recorded |
| **E1-C2 — Policy / authorization decision** | **NOT DETERMINED** | C | **The critical element.** Nothing in the accessible record addresses it |
| **E1-C3 — Execution** | **NOT DETERMINED** | C | Verbs are build/attack/exploit/defend; no distinct execution stage described |
| **E1-C4 — Result** | **NOT DETERMINED** | C | Module-level outcomes reported; no per-action result stage described |
| **E1-C5 — Trace / event representation** | **NOT DETERMINED** | C | No trace/log/event vocabulary in the accessible record |
| **E1-C6 — Learner distinguishes the stages** | **NOT DETERMINED** | C | No assessment or activity of that kind described |

**No element is recorded as present, and no element is recorded as absent.**

### Classification

> ## **INSUFFICIENT EVIDENCE**

This is the only defensible classification under the brief's own rule (§7: *"If full text remains unavailable, do NOT infer absence"*; §8: *"Use if the paper remains unread or the available evidence is insufficient to decide"*). It is **not** PREEMPTS — no element of the educational E1-C construct was demonstrated. It is **not** a clean `DOES NOT PREEMPT` either: that verdict requires sufficient text to have been inspected and the construct to be demonstrably absent, which did not happen.

Continuing uncertainty, precisely stated: whether the 2025 paper's **body text** contains (a) any authorization/policy-decision stage, (b) any distinguishable event/state/trace representation, or (c) any learner activity requiring reasoning about a decision-versus-execution distinction. Nothing more.

---

## 7. Wilson 2025 vs Wilson 2026

Wilson 2025 column = evidence level **C** (official record only). Wilson 2026 column = evidence level **A** (full text, from `research/25` §4). `NOT DETERMINED` entries carry **no** inference of absence.

| Dimension | Wilson 2025 (JCSC 41(4)) | Wilson 2026 (JCERP) |
|---|---|---|
| **RAG** | **YES** — "educational approach to LLM security using a Retrieval-Augmented Generation (RAG) framework in lab exercises"; "a vector database and LLM" | **YES** — custom RAG platform: document repository → FAISS embedding index → retriever → LLM, orchestrated with LangChain; Ollama-served Llama 3.1 and Phi-3 |
| **LLM security education** | **YES** — LLM threats and mitigation strategies; "a template for integrating LLM security into cybersecurity education" | **YES** — a two-week graduate module; explicitly framed as filling a curriculum gap |
| **Learner lab** | **YES** — interactive labs; students build and attack the system; a pilot module is reported | **YES** — two capture-the-flag labs (jailbreaking; model inversion/data extraction) in teams of 3–4 |
| **Request / invocation** | **NOT DETERMINED** — chatbot-scenario interaction only | **PARTIAL / NO** — the learner submits chat prompts; there is no action or tool invocation |
| **Policy / authorization** | **NOT DETERMINED** — the decisive element; nothing in the accessible record addresses it | **NO** — full-text counts: `authorization` 0, `policy decision` 0, `deny` 0, `approval` 0, `mediation` 0, `gateway` 0, `access control` 0. Guardrail bypass is studied as *model* behaviour, never as a decision stage |
| **Execution** | **NOT DETERMINED** | **NO** — no execution stage exists; the chatbot response is the terminal event |
| **Result** | **NOT DETERMINED** — module-level outcomes reported | **PARTIAL** — attack outcomes only (flag/secret found or not; partial extraction) |
| **Trace / events** | **NOT DETERMINED** — no trace/log vocabulary in the accessible record | **NO** — "logs" are student-written prose journals graded on iteration count, strategy diversity and reflection (Appendix C); no event schema, no event types |
| **Learner distinguishes stages** | **NOT DETERMINED** | **NO** — quiz (12 items), Likert survey and lab-log rubric all target attack concepts, mitigation reasoning and ethical awareness |
| **E1-C** | **INSUFFICIENT EVIDENCE** | **DOES NOT PREEMPT** (level A) |

**Direction of the comparison.** The 2025 column is uniformly `NOT DETERMINED` where the 2026 column is a documented `NO`, so the table establishes **no** E1-C content in 2025, and establishes **no absence** either. What it does establish is that the two documents share the same subject matter, the same architecture family and the same author, and that the one document which *was* read in full contains no E1-C element whatsoever.

---

## 8. Wilson Publication-Line Relationship

The brief requires one of four determinations, and forbids treating two publications from the same research line as two independent interventions unless the evidence supports it.

**Determination: (2) an earlier version of the same intervention.**

Evidence actually supporting this:

1. **Same author, single-author paper.** Both are by Dominic Wilson; the 2026 title page carries the University of Findlay affiliation and ORCID `0000-0001-6356-0871`.
2. **The 2026 paper cites the 2025 paper as its own prior work and describes it as the thing it extends.** Reference **[24]** in the 2026 paper is the 2025 JCSC paper; the body text states *"Prior work introduced a lab framework for prompt injection and data poisoning using a retrieval-augmented chatbot [24] … This work builds on the spirit of such active learning but **significantly extends the scope of attacks covered**."*
3. **Same architecture family.** Both are RAG-chatbot teaching labs ("a vector database and LLM to simulate chatbot scenarios" in 2025; the FAISS/LangChain/Ollama RAG platform in 2026).
4. **Independent third-party corroboration that they are a pair.** Devadiga et al. (2026) cite them together as **[31]** and **[32]** in the same related-work passage, describing [31] as building and attacking a RAG chatbot and [32] as the jailbreaking module with the 88% / 90% outcomes.
5. **The author's own dissemination treats them as one line.** His figshare talk describes the JCERP 2026 work as the curricular methodology "recently published", with no separate treatment of a distinct 2025 intervention.

**Residual caveat, stated rather than smoothed over.** The *degree* of identity between the two documents cannot be measured without the 2025 text. Options (1) and (2) of the brief cannot be distinguished from the available evidence; what **is** excluded on the evidence is option (3) (*a different intervention*), because the 2026 paper describes the 2025 lab as its own predecessor framework, and option (4) (*impossible to determine*), because the citation relationship and the shared architecture are documented. The precise degree of overlap between the two texts remains **impossible to determine from available evidence**, and is recorded as such.

**Consequence for prior-art counting.** Wilson 2025 and Wilson 2026 must be counted as **one prior-art line**, not two independent prior works. This confirms and strengthens the structural finding first recorded in `research/24` §7 and carried in `research/25` §5.4. Devadiga et al. (2026) is, by contrast, an **independent** intervention — different authors, different institutions (King's College London / University of Plymouth), a different architecture (isolated test network plus a multi-model LLM interaction layer) and a different pedagogical target (exploit-generation assessment with expert validation).

---

## 9. Combined E1-C Evidence

All three Phase 20 sources, as they now stand after this step:

| Source | Evidence level | E1-C verdict | Basis |
|---|---|---|---|
| **Wilson 2026** (JCERP, `10.62915/2472-2707.1268`) | **A** — full text, 12 pages | **DOES NOT PREEMPT** | No tool execution, no policy/authorization decision, no execution stage, no learner-interpreted trace; agent-mediated tool pipelines named only as future work (`research/25` §4) |
| **Devadiga et al. 2026** (ITiCSE, `10.1145/3803400.3809384`) | **A** — full text, 7 pages | **DOES NOT PREEMPT** — but **partially overlaps** E1-C (closest overlap located to date) | Deliberately teaches *prompt → model output → manual execution in a separate sandbox → recorded result*, and calls that separation a pedagogical feature; but has **no authorization/policy decision** (Refusal Rate is a model-behaviour statistic), no mediation infrastructure, no tool invocation, no machine event trace; assessment is ASR / EGA / VES / MSP (`research/25` §6) |
| **Wilson 2025** (JCSC 41(4):173–182) | **C** — official record only | **INSUFFICIENT EVIDENCE** | Full text closed access and not obtainable through any legitimate route (§3); **no absence inferred** |

**What the combination shows.** Of the two sources that could be inspected in full, **neither teaches E1-C**, and the closer of the two (Devadiga et al.) partially overlaps it while missing the decisive authorization/mediation element. The third source — an earlier version of the Wilson lab line whose later, fully-read report contains no E1-C element at all — remains unread, and **nothing may be concluded about its body text**.

Note also, for the record, that the Wilson 2025 and 2026 documents are **one line, not two** (§8), so the "three sources" are really **two independent interventions plus one earlier report of one of them**.

---

## 10. Final E1-C Status

Applying the brief's §9 outcomes to the present evidence:

- **Outcome A (PREEMPTED)** — does not apply. No source demonstrates the educational E1-C construct.
- **Outcome B (`NOT PREEMPTED BY INSPECTED SOURCES`)** — applies to the **sufficiently inspected** sources: Wilson 2026 (A) and Devadiga et al. 2026 (A) demonstrably lack E1-C.
- **Outcome C (`INSUFFICIENT EVIDENCE`)** — applies to the **combined** status, because **Wilson 2025 remains insufficiently evidenced**.

Since the brief gives Outcome C precedence when a source remains insufficiently evidenced, and forbids inferring absence, the combined status is:

> ## **E1-C = INSUFFICIENT EVIDENCE**

with the following two statements recorded alongside it, and not conflated with it:

1. **`NOT PREEMPTED BY INSPECTED SOURCES`** — the two source interventions inspected at full-text level (Wilson 2026; Devadiga et al. 2026) do **not** contain E1-C. **This is explicitly not a claim of novelty**, and must never be reported as one.
2. **One document remains unresolved** — Wilson 2025 (JCSC 41(4):173–182). Its body text may not be assumed clean, and its status stays `INSUFFICIENT EVIDENCE`.

**Change since `research/25`:** none. `research/25` recorded E1-C as `NOT PREEMPTED BY INSPECTED SOURCES` with the same single-document caveat; this step **failed to remove that caveat**, and therefore leaves the E1-C status exactly as it was.

---

## 11. Overall E1 Classification

**Overall E1 classification: `HIGH-RISK / INSUFFICIENTLY DISTINCT` — UNCHANGED.**

The classification was not automatically changed, and the evidence does not require a change:

- **Not upgraded to PREEMPTED.** No source was shown to contain the E1-C learning object.
- **Not upgraded to "novel".** No novelty is claimed for E1, for E1-C, for any component, or for the repository. Not-preempted-by-inspected-sources is **not** novelty.
- **Not upgraded on the strength of a research gap.** No gap is claimed merely because no located source contains the exact construct. The prior audits' reasons stand unchanged: the **genre is occupied** (hands-on LLM-security labs for novices with measured outcomes are published); **E1-A, E1-B, E1-D, E1-E and E1-G have substantial prior-art coverage**; **E1-C is the distinctive conceptual element**; and **E1-G is the missing empirical outcome**.
- **No educational effectiveness claimed.** Nothing here shows that any intervention — including this repository's labs — improves learning.
- **No novice misconception claimed.** There is still no evidence that novices actually conflate request / policy decision / execution / result in agent-security tasks. This step did not address that question, and it remains the unestablished *problem* behind E1.

What this step adds is a **sharper characterisation of the risk**, not a change in its level: the one fully-read same-genre predecessor line contains no E1-C; the closest near-neighbour in the literature teaches an adjacent, deliberately framed request→generation→execution→result separation (without the authorization element); and the single unread document is confirmed to be an earlier version of the already-read line.

---

## 12. Publication-Gate Consequence

**Publication gate: `HOLD` — UNCHANGED** (`research/23` §10; `research/24` §16; `research/25` §12).

| Gate | Status | What exists | What remains absent |
|---|---|---|---|
| **Gate A — Artefact publication readiness** | **NOT READY** | A complete, tested, reproducible, documented artefact: 694 tests passing, 8/8 labs self-checking, deterministic replay, CI, a built documentation site, instructor material | A stated design claim argued against the existing hands-on-lab genre; any evaluation or adoption evidence; licence and citation metadata |
| **Gate B — Experience-report readiness** | **NOT READY** | Substantial *implicit* rationale: the mediated-gateway invariant, declarative scenarios, the eight-lab sequence, the trace-reading materials, the boundary statements, the instructor guide | A written rationale-and-reflection artefact; any learner or instructor evaluation |
| **Gate C — Empirical-study readiness** | **INSUFFICIENT EVIDENCE** | The intervention only | Participants; instrument; comparison condition; protocol; ethics approval; data; analysis; **and any evidence that E1-C is a genuine learner difficulty** |

**Effect of this step on the gate.** **None.** This step removed **no** prior-art uncertainty: the one document it set out to close **remains unresolved**, so the condition recorded in `research/23` §10 item (1) — closing the decisive full-text test — is still only **half** satisfied (Wilson 2026 resolved against preemption; Wilson 2025 unresolved), exactly as in `research/25`. Conditions (2) (evidence that novices conflate the stages) and (3) (a systematic venue-targeted prior-art review) were not addressed. **No empirical evidence of any kind was created.**

**No venue is chosen, ranked or recommended here; no acceptance likelihood is estimated or implied.**

---

## 13. Remaining Uncertainty

1. **Wilson 2025 (JCSC 41(4):173–182) — full text.** The single remaining unread document, and it is now demonstrated to be **unobtainable through any legitimate open route**: closed at the publisher, absent from every repository, aggregator and index consulted, not registered with Crossref, not archived, and not present on the author's ORCID record with any copy. **The only remaining routes are library/institutional subscription access or a copy obtained directly from the author** — neither available or authorised in this environment. Specific unresolved questions: whether its body text contains an authorization/policy decision stage; a distinguishable event/state/trace representation; or a learner activity requiring reasoning about decision-versus-execution. **Nothing further can be concluded without the document.**
2. **Degree of overlap between Wilson 2025 and Wilson 2026** — the relationship is established as "earlier version of the same intervention line", but the precise extent of shared content, learning objectives and instruments cannot be measured without the 2025 text.
3. **Newly surfaced same-author works** (from `research/25` §13; level C, unread): the JCERP 2026 supply-chain-hygiene module (`10.62915/2472-2707.1301`); the figshare presentation on scaling AI-security pedagogy (checked here — it covers the **2026** JCERP work only); and the TechRxiv preprint *The Rise of the Agentic Era: Quantifying the Shift from Chatbots to Autonomous Security* (`10.36227/techrxiv.177273622.27994930`), whose title indicates agentic-security measurement rather than education and which could not be retrieved.
4. **Coverage remains non-systematic.** No database search (Scopus, Web of Science, ACM DL search, IEEE Xplore) and no venue-targeted full-text review were performed; coverage is web-search sampling plus targeted API lookups and archive retrieval. Two general scholarly indexes (Google Scholar, Internet Archive Scholar) were **unavailable by design** to an automated agent, and CORE and BASE were unavailable for operational/IP reasons — so the negative result in §3 should be read as "**no legitimate copy reachable from this environment**", not as a proof that no copy exists anywhere.
5. **Terminology drift risk.** A source using entirely different vocabulary for mediation (e.g. "guardrails", "policy enforcement point", "capability gating", "approval workflow") could still be missed by the equivalence criteria recorded in `research/25` §7.1; those criteria are recorded so a future audit can challenge them rather than inherit them.

---

## 14. Verification

Commands run for this step (read-only with respect to tracked files). The repository's own interpreter launcher `py` is used, per project convention.

```
PYTHONPATH=src py -m pytest -q --tb=no
    -> exit 0; 694 tests executed (694 progress marks); 0 non-dot progress characters
       (i.e. zero failures or errors)
PYTHONPATH=src py -m agentsec labs check
    -> LAB-00 … LAB-07 all PASS; "Result: 8/8 labs passed"; exit 0
py -m mkdocs build --strict
    -> exit 0; site built; no warnings or errors
git diff --name-only
    -> (empty) — no tracked file modified
git status --porcelain
    -> ?? research/20-research-positioning-audit.md
       ?? research/21-education-literature-hostile-audit.md
       ?? research/22-e1-fulltext-reaudit.md
       ?? research/23-publication-gate-audit.md
       ?? research/24-decisive-prior-art-closure.md
       ?? research/25-e1-c-source-recovery.md
       ?? research/26-wilson-2025-final-closure.md      <-- the only new file
```

- **No unexpected repository file changed.** The only change is the one new untracked research file.
- `site/` is git-ignored build output and is not part of the tracked tree; building it does not modify tracked files.
- No artefact was written anywhere in the repository during retrieval; this step created **no** temporary files, and no temporary files remain from the previous step.

---

## 15. Files Changed

| Path | Change |
|---|---|
| `research/26-wilson-2025-final-closure.md` | **created** (this file) — the only change |
| everything else | **unchanged** |

No existing file was modified or deleted. In particular, no prior audit file (`research/20` … `research/25`) was altered, and no source, test, policy, lab YAML, scenario, CI, MkDocs, site, README, LICENSE or CITATION.cff file was created or modified.

**Git discipline — explicit confirmation:** no `git add`; **nothing staged**; **no commit**; **no push**; no reset; no checkout; no clean; no rebase; no amend. All Git operations remain the repository owner's to perform manually.

---

## 16. Research Boundary

This step exists only to determine the evidence status of the final unresolved prior-art source and its relationship to E1-C. It **does NOT establish**, and must not be read as establishing, any of the following:

- **research novelty** — none is claimed for E1, for E1-C, for any component, or for the repository; E1 remains **HIGH-RISK / INSUFFICIENTLY DISTINCT**;
- **publication acceptance** — no venue outcome is predicted, ranked, implied or estimated;
- **educational effectiveness** — nothing here shows that any intervention, including this repository's labs, improves learning;
- **causal learning effects** — no design, no participants, no data, no analysis;
- **security effectiveness** — no security claim is made or measured;
- **model behaviour beyond what the source explicitly reports** — where a source reports model behaviour (e.g. refusal rates, attack success rates), it is reported as *that source's* finding; nothing here measures or generalises model behaviour, and this repository's deterministic fixture is a fixture;
- **benchmark validity** — this repository is not a benchmark, and no inspected source is treated as one;
- **measurement validity** — no instrument was validated, proposed or endorsed.

It also does **not** preempt or clear the unread document: Wilson 2025 is recorded as **`INSUFFICIENT EVIDENCE`**, and no inference of absence is drawn from its unread body. It does not redefine E1 or E1-C, does not weaken the hostile audit, and **Phase 17 remains CLOSED** — no closed security-research direction was reopened.

---

## 17. Conclusion

1. **The final retrieval attempt failed.** The last unread document — Wilson, *A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation*, JCSC 41(4):173–182 (2025) — is **closed access**, and **no legitimate copy exists in any location reachable from this environment**: no OA PDF, no author manuscript, no accepted manuscript, no preprint, no repository copy, no archive snapshot, no Crossref registration, no ResearchGate page, and no openly indexed version. Two general scholarly indexes are gated by anti-automation measures that this audit correctly declined to bypass.
2. **Evidence level remains C.** Only the official abstract and record were inspected. **No element of the E1-C analysis is recorded as absent**, because absence may not be inferred from an unread document.
3. **The pair relationship is now firmly established.** Wilson 2025 is an **earlier version of the same intervention line** as the fully-read Wilson 2026 paper (same author, same RAG-chatbot architecture, cited by the 2026 paper as the framework it extends, corroborated independently by Devadiga et al.). The two publications are therefore **one prior-art line, not two independent works**. The precise degree of overlap remains unmeasurable without the 2025 text.
4. **Combined E1-C status: `INSUFFICIENT EVIDENCE`.** Among the sources inspected at full-text level — Wilson 2026 and Devadiga et al. 2026 — E1-C is **not present**, and Devadiga et al. partially overlaps it while lacking the decisive authorization/mediation element. That is **not** novelty, and it is **not** a clearance of the unread document.
5. **Overall E1 classification unchanged:** **HIGH-RISK / INSUFFICIENTLY DISTINCT**. **Publication gate unchanged: HOLD** (Gates A and B NOT READY; Gate C INSUFFICIENT EVIDENCE). This step removed no prior-art uncertainty and created no empirical evidence.
6. **The decisive Phase 20 prior-art question is now closed *as far as this environment can take it*.** One of the two original decisive documents (Wilson 2026) is resolved at full-text level; the other (Wilson 2025) is demonstrated to be unobtainable without library, institutional or author-supplied access. **Any further progress on this specific question requires a document that cannot be retrieved from here — not more searching.**

**Stop condition observed:** the audit stops here. No paper was drafted, no study designed or implemented, and no data collected.

---

*End of Phase 20 — Step 7. The last unread source remains unread and unobtainable from this environment; E1-C = INSUFFICIENT EVIDENCE; overall E1 = HIGH-RISK / INSUFFICIENTLY DISTINCT; publication gate = HOLD.*
