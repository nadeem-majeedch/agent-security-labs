# Decisive Prior-Art Closure Audit

**Phase:** 20 — Step 5 (decisive prior-art closure)
**Date:** 2026-09-28
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs.git`
**HEAD at audit:** `6802c81`
**Prior audits:** `research/20-research-positioning-audit.md`, `research/21-education-literature-hostile-audit.md`, `research/22-e1-fulltext-reaudit.md`, `research/23-publication-gate-audit.md`
**Deliverable:** this file only (`research/24-decisive-prior-art-closure.md`). No paper, study design, data collection, or change to source, tests, labs, policies, scenarios, MkDocs, CI or site content.

---

## 1. Scope

This audit attempts to close the single decisive prior-art uncertainty recorded by `research/22` §10 and `research/23` §10: whether either candidate source — **Wilson 2026 (JCERP)** or **"ACM 2025" (RAG security lab)** — already contains, as an explicitly taught learning object, the E1-C construct:

```
request → policy/authorization decision → execution → result
```

especially through trace/log interpretation by learners.

The purpose is **not** to preserve novelty. If either source preempts E1-C, it is reported. The audit uses the strict preemption criterion from the step brief and does **not** treat search snippets or abstracts as full-text evidence, and does **not** infer absence from an inaccessible full text.

**Retrieval constraint applied throughout:** only legitimate, publicly reachable routes were used (publisher pages, DOI resolution, institutional repositories, aggregators, public metadata APIs, official proceedings listings). No paywall circumvention, authentication, credential use, robots-directive bypass or technical-protection bypass was attempted.

---

## 2. Prior Audit Position

Recovered verbatim, unchanged.

**Exact E1 definition** (`research/21` §2, `research/22` §2, `research/23` §2):

> **E1.** Does a trace-first deterministic lab methodology improve novice understanding of the **request → policy decision → execution → result** distinctions in **agent-security** workflows?

**Exact E1-C definition** (`research/21` §2):

> **E1-C** — **Explicit separation of `request → policy decision → execution → result`** as *named, observable, distinct* concepts.

**Why Wilson 2026 matters** (`research/22` §5.1, §9.1): it is a peer-reviewed, hands-on LLM-security lab with **measured learning outcomes** for **novice (graduate) learners** — the closest located match to E1's *genre*, and therefore the most plausible preemptor.

**Why "ACM 2025" matters** (`research/22` §5.2, §9.1): a hands-on lab in which students **build and attack a RAG-based LLM system** — the same genre profile as Wilson 2026.

**What evidence would constitute preemption** (`research/22` §11; step brief §7): substantially all of — (1) an agent/action request or invocation, (2) an explicit policy/authorization/mediation decision, (3) a distinct execution stage, (4) a distinct result/observation stage, (5) these stages represented as distinguishable events/states, (6) learners expected to reason about or interpret those distinctions, (7) the distinction forming part of the educational intervention rather than an implementation detail.

**What would NOT constitute preemption:** mentioning authorization, logging, execution or results without teaching the distinction; recording events in the background without making them the learning object; a different UI, language, scenario, tool name, attack, dataset or terminology; studying students rather than developers; general (non-agent) cybersecurity; a different LLM.

**Prior status:** E1 = **HIGH-RISK / INSUFFICIENTLY DISTINCT**; publication gate = **HOLD** (`research/23` §10).

---

## 3. Wilson 2026 — Source Identification

| Field | Value |
|---|---|
| **Title** | *Integrating Adversarial Scenarios into LLM Security Labs: An Experience Report on a Hands-On Approach* |
| **Author** | Dominic A. Wilson (University of Findlay) |
| **Venue** | *Journal of Cybersecurity Education, Research and Practice* (JCERP), Vol. 2026, No. 1, Art. 2. ISSN 2472-2707 |
| **Year** | 2026 (published 2026-01-26) |
| **DOI** | **`10.62915/2472-2707.1268`** (verified via Crossref public API) |
| **Official publisher page** | `https://digitalcommons.kennesaw.edu/jcerp/vol2026/iss1/2/` (reached via DOI resolution) |
| **Repository / institutional copy** | DigitalCommons@Kennesaw State University (the publisher host itself) |
| **Preprint** | none located |
| **Access status** | **GOLD open access, CC-BY** (per Semantic Scholar metadata for DOI `10.62915/2472-2707.1268`: `openAccessPdf.status = "GOLD"`, `license = "CCBY"`) |
| **Cited by** | 1 (Crossref/Semantic Scholar, as of audit) |

Direct PDF route: `https://digitalcommons.kennesaw.edu/cgi/viewcontent.cgi?article=1268&context=jcerp`.

**Note:** the paper is **not paywalled**. The full text is openly licensed and publicly hosted. Any failure to read it in this audit is a *tooling* limitation, not an access restriction (§4).

---

## 4. Wilson 2026 — Full-Text Availability

| Route attempted | Result |
|---|---|
| DOI resolution `https://doi.org/10.62915/2472-2707.1268` | ✓ resolves to DigitalCommons landing page (abstract + metadata only) |
| Publisher landing page `/jcerp/vol2026/iss1/2/` | ✓ reachable; **abstract only**, no inline full text |
| PDF `viewcontent.cgi?article=1268&context=jcerp` | **403 Forbidden** (earlier attempts) then **"Unsupported content type: application/pdf"** (later attempt — i.e. the PDF *was* served, but this audit's reader cannot parse PDFs) |
| PDF variant with `&type=additional` | ✗ 403 |
| Semantic Scholar API (DOI lookup) | ✓ metadata + abstract; `openAccessPdf` points back to the same DigitalCommons URL |
| Crossref API | ✓ metadata only |
| DOAJ API | ✗ 403 |
| Author-hosted copy / institutional repository | none located (searched by title, DOI, author+title, title+PDF, title+manuscript, title+repository, title+author homepage) |
| Preprint servers (arXiv etc.) | none located |

**Conclusion for Wilson 2026:** the **full text is publicly available and openly licensed**, but **could not be inspected by this audit**. The record obtained is the **official abstract + metadata (label C)**. This is **not** a case of restricted access; it is a case of the audit's tooling being unable to extract text from a PDF.

---

## 5. Wilson 2026 — E1-C Audit

The step brief requires full-text inspection. Because the full text was **not obtained**, the table records `NOT DETERMINED` for every element. **No element is recorded as `NO`**, because absence may not be inferred from an unread document.

| E1-C element | Present? | Exact source location | What the source actually does |
|---|---|---|---|
| Request | **NOT DETERMINED** | — (full text not inspected) | Abstract reports "red team activities to actively exploit model alignment and privacy vulnerabilities"; no request/invocation stage is described in the accessible record. |
| Policy/authorization decision | **NOT DETERMINED** | — | Abstract references "model alignment and privacy vulnerabilities" as things to *exploit*; no policy/authorization decision stage is described in the accessible record. |
| Execution | **NOT DETERMINED** | — | Abstract reports exploitation activities; no distinct tool/operation execution stage is described. |
| Result | **NOT DETERMINED** | — | Abstract reports a module-level outcome (quiz/confidence); no per-operation result stage is described. |
| Explicit four-stage distinction | **NOT DETERMINED** | — | Nothing in the accessible record describes a four-stage request→decision→execution→result construct. |
| Trace/log interpretation as learning task | **NOT DETERMINED** | — | Abstract does not mention traces, logs, event interpretation or learner trace-reading. |

**Abstract-level indications (recorded as indications, not as findings):** the accessible record describes a **RAG-platform attack module** — "utilizing a custom Retrieval-Augmented Generation (RAG) platform with local open-source LLMs", with "red team activities to actively exploit model alignment and privacy vulnerabilities", assessed by "a post-module quiz score of 88%" and "90% of students reported increased confidence." Nothing in it points to a mediated tool pipeline, an authorization-decision stage, or trace interpretation. These are **indications from an abstract**, explicitly **not** a basis for a preemption judgement.

---

## 6. Wilson 2026 — Preemption Classification

### **D. INSUFFICIENT EVIDENCE**

Applying the strict criterion: elements (1)–(7) cannot be assessed because the educational intervention's internal content was not read. The accessible record contains **no positive evidence** of elements (1)–(7), and it also contains **no negative evidence** sufficient to rule them out. Under the rule that absence may not be assumed from an inaccessible full text — and noting that the full text is openly available and merely unread here — the only defensible classification is D.

**Explicitly not classified as PREEMPTS**, because elements (1)–(7) are unverified.

---

## 7. ACM 2025 — Source Identification

Identification is now exact, and materially changes the picture from `research/22` §5.2 (which had only a snippet).

| Field | Value |
|---|---|
| **Title** | *A Hands-on Approach to Enhancing LLM Security Education through Retrieval-Augmented Generation* |
| **Author** | **Dominic Wilson** (same author as Wilson 2026) |
| **Venue** | **Journal of Computing Sciences in Colleges (JCSC)**, Volume 41, Issue 4, pages 173–182 |
| **Year** | 2025 |
| **DOI / identifiers** | ACM Digital Library record `10.5555/3787712.3787744` (`https://dl.acm.org/doi/abs/10.5555/3787712.3787744`) |
| **Official page** | ACM DL (as above) — **403 Forbidden** to this audit |
| **Repository / author copy / preprint** | none located |
| **Cited by** | 3 |

**Structural finding:** the two "decisive sources" are **the same author's same body of work** — a RAG-based LLM-security teaching lab by Dominic Wilson, reported first in JCSC 41(4):173–182 (2025) and then as a JCERP experience report (2026). The "decisive uncertainty" therefore concerns **one intervention reported twice**, not two independent prior works. This was not evident in `research/22`, which listed them as separate sources.

---

## 8. ACM 2025 — Full-Text Availability

| Route attempted | Result |
|---|---|
| ACM DL `/doi/10.5555/3787712.3787744` | ✗ **403 Forbidden** |
| ACM DL `/doi/abs/…` variant | ✗ **403 Forbidden** |
| ACM DL PDF `/doi/pdf/…` | ✗ 403 |
| Google Scholar author profile | ✓ citation record only (confirms JCSC 41(4):173–182) |
| Search for author manuscript / institutional copy / preprint | none located |
| Crossref / Semantic Scholar metadata by title | not retrieved (rate-limited); title/venue/pages confirmed via search records |

**Conclusion for ACM 2025:** the full text is **not accessible to this audit** (ACM DL blocks the reader). Evidence level remains **C** (title + venue + pages + abstract-level snippet only).

---

## 9. ACM 2025 — E1-C Audit

Same standard as §5. Full text **not obtained**; therefore `NOT DETERMINED` throughout, and no element recorded as `NO`.

| E1-C element | Present? | Exact source location | What the source actually does |
|---|---|---|---|
| Request | **NOT DETERMINED** | — (full text not inspected) | Accessible snippet: "lab exercises … Students learn about LLM threats and mitigation strategies by building and attacking a RAG-based LLM system." No request/invocation stage described. |
| Policy/authorization decision | **NOT DETERMINED** | — | No authorization/policy-decision stage described in the accessible record. |
| Execution | **NOT DETERMINED** | — | No distinct execution stage described. |
| Result | **NOT DETERMINED** | — | No distinct result stage described. |
| Explicit four-stage distinction | **NOT DETERMINED** | — | Nothing in the accessible record describes it. |
| Trace/log interpretation as learning task | **NOT DETERMINED** | — | Nothing in the accessible record describes traces or learner trace-reading. |

**Abstract-level indications (recorded as indications only):** the record describes a **RAG build-and-attack lab**. It does not indicate a mediated tool pipeline, an authorization-decision stage, or trace interpretation.

---

## 10. ACM 2025 — Preemption Classification

### **D. INSUFFICIENT EVIDENCE**

Same reasoning as §6, with the additional observation that the source is an earlier report of the same author's same lab, so it does not introduce an independent candidate. No element of the strict criterion can be assessed; no absence is inferred.

---

## 11. Semantic-Equivalence Analysis

The step brief requires a **conceptual**, not lexical, equivalence test. Because neither full text was read, each equivalence is recorded as **unassessable at the conceptual level** here, with the abstract-level indication noted. (Semantic equivalents from the brief are treated as *potential* prior art, not as confirmed overlap.)

| Stage | Semantic equivalents (per brief) | Conceptual equivalence in the two sources |
|---|---|---|
| **Request** | action, invocation, agent action, tool call, operation | **Not assessable.** Abstract-level records describe attack actions against a RAG model, not a mediated tool-request stage. |
| **Policy / authorization decision** | authorization, access control, permission, guard, gate, approval, mediation, policy enforcement | **Not assessable.** "Alignment" and "privacy safeguards" appear in the Wilson 2026 abstract only as things to *exploit*; whether any authorization *decision* is represented or taught cannot be judged without the text. This is precisely the element that would decide preemption. |
| **Execution** | execution, tool invocation, operation execution, action execution, environment transition | **Not assessable.** |
| **Result** | response, observation, tool output, environment result, effect | **Not assessable.** |

**Important caution recorded:** the equivalence test was specified for the case where the sources are read. Running it purely from abstracts would risk converting *"the abstract does not mention X"* into *"the source does not teach X"* — the inference the brief forbids. The analysis is therefore left **open**, not resolved in either direction.

---

## 12. Implementation vs Research vs Pedagogical Evidence

The brief makes this distinction central, and it is the distinction this audit **cannot** draw for either source, because the pedagogical content is exactly what the full text contains.

| Evidence type | Definition | Wilson 2026 | ACM 2025 |
|---|---|---|---|
| **Implementation evidence** | What the system happens to record internally | Not inspected | Not inspected |
| **Research / evaluation evidence** | What the authors measure or analyse | Abstract-level: mean post-module quiz **88%**; **90%** reported increased confidence (module-level, not per-stage) | Not inspected |
| **Pedagogical evidence** | What learners are actually expected to understand, distinguish, interpret or perform | **Not inspected** — this is the decisive layer and it is unavailable | **Not inspected** |

**Consequence:** the audit cannot determine whether either source contains E1-C as an implementation detail, as an analytical construct, or as an explicitly taught learning object. Treating implementation evidence as pedagogical evidence is not possible here because neither is available.

---

## 13. Combined E1-C Finding

- **No positive evidence** of E1-C was found in either source **at the level of evidence available** (official abstracts and metadata).
- **No negative evidence** was obtained either; neither full text was read, so absence **cannot** be asserted.
- The two candidate sources are **one author's same intervention reported twice** (JCSC 2025; JCERP 2026), both a **RAG-based LLM-security attack lab** assessed at module level (quiz/confidence).
- A **newly surfaced, previously unaudited source** is closely relevant and likewise unread: **Devadiga, Kuzminykh, Cao & Ghita, *A Virtual Lab for Learning AI Security and Adversarial Prompt Engineering*, ITiCSE 2026, pp. 107–113** (ACM `10.1145/3803400.3809384`) — an "Adversarial AI Lab" virtual learning environment for LLM security, in a leading computing-education venue. Its ACM DL record is also **403** to this audit. Adjacent to it in the same proceedings: **Noviello, Sibia, Birillo, Overklift Vaupel Klein, Liut & Migut, *AI-Generated Traces for Novice Programmers: Learning Effects and Learner Differences in a Multi-Institutional Study*, ITiCSE 2026, pp. 135–141** — trace-based teaching with measured learning effects (programming, not security).

**Combined finding:** the decisive element of E1-C remains **unresolved**. The candidate preemptors contain no evidence of it in their abstracts, and their full texts could not be read.

---

## 14. Does This Close the Decisive Gap?

### **NO — neither source was available at sufficient depth.**

- **Wilson 2026:** the full text is **openly licensed (CC-BY, GOLD OA)** and the file is served, but this audit's reader **cannot parse PDFs** (`application/pdf` unsupported); no HTML full text exists at the publisher. → **Not inspected.**
- **ACM 2025 (JCSC 41(4):173–182):** the publisher record is **403** and no author/repository copy was located. → **Not inspected.**
- **Newly surfaced proximity:** the Devadiga et al. (ITiCSE 2026) virtual AI-security lab is likewise unread (ACM DL 403).

**What remains unknown, precisely:**
1. Whether either Wilson source teaches any **policy/authorization decision** stage (the element that decides preemption).
2. Whether either source represents the stages as **distinguishable events/states**.
3. Whether either source makes **trace/log interpretation** a learner activity.
4. Whether the intervention is **trace-first** at all, or purely exploit-driven.
5. Whether the Devadiga et al. (ITiCSE 2026) lab teaches the construct.

This step therefore **does not** close the gap identified by `research/22` §10 and carried by `research/23` §10.

---

## 15. Impact on E1 Classification

**E1-C status:** **unchanged** — still `NO (not located)` in every *readable* source, and still `NOT DETERMINED` in the two candidate preemptors. No element changed from `NO` to `YES` or vice versa.

**Overall E1 classification:** **HIGH-RISK / INSUFFICIENTLY DISTINCT (unchanged)**

- It is **not** upgraded to **PREEMPTED**: no source was shown, at a sufficient evidence level, to contain the E1-C learning object.
- It is **not** upgraded to **SURVIVES**: the brief forbids selecting survival merely because a source was not found; the genre remains occupied and the components remain individually established (`research/21` §11, `research/22` §11).
- It is **not** moved to **INCONCLUSIVE** overall: the prior evidence base for the *risk* assessment (occupied genre; occupied component strands; E1-C absent from every readable source) is unchanged and unaffected by this step. What remains inconclusive is one specific sub-question (the Wilson/Devadiga full texts), now recorded as unresolved rather than newly resolved.

*Note: this audit deliberately does not resolve the sub-question in either direction. The two candidate preemptors are recorded as D (insufficient evidence), not as C (related but non-preempting).*

---

## 16. Impact on Publication Gate

**Publication-gate status: HOLD (unchanged)** (`research/23` §10)

- **GATE A (artefact publication readiness): NOT READY** — unchanged; still no stated design claim and no evaluation/adoption evidence.
- **GATE B (experience-report readiness): NOT READY** — unchanged; still no written rationale synthesis and no light evaluation.
- **GATE C (empirical-study readiness): INSUFFICIENT EVIDENCE** — unchanged; still no empirical evidence of any kind, and now additionally: the decisive prior-art test remains open, and a previously unlisted candidate (Devadiga et al., ITiCSE 2026) has entered the picture and is also unread.

The conditions that would move the gate (recorded in `research/23` §10) are **not** met: condition (1) — closing the decisive full-text test — **failed to close** in this step; conditions (2) and (3) were not addressed here.

---

## 17. Remaining Uncertainty

1. **Wilson 2026 (JCERP)** — full text openly available but unreadable by this audit's tooling; the decisive element (authorization-decision pedagogy, trace interpretation) is unknown.
2. **ACM 2025 / JCSC 41(4):173–182** — full text inaccessible (403); content unknown.
3. **Devadiga et al., ITiCSE 2026** — newly surfaced, unread; a leading-venue AI-security virtual lab that could be a closer prior work than either Wilson source.
4. **Noviello et al., ITiCSE 2026** — trace-based teaching with measured learning effects (programming); unread; relevant to E1-A/E1-D/E1-G.
5. **Search coverage** — no systematic database search (Scopus, Web of Science, ACM DL search, IEEE Xplore); coverage remains web-search sampling.

**What would close the gap (recorded, not performed):** reading the CC-BY Wilson 2026 PDF directly (requires a PDF-capable reader); obtaining the JCSC paper through a library/institutional subscription; obtaining the Devadiga et al. and Noviello et al. ITiCSE 2026 papers; and a systematic venue-targeted search.

---

## 18. What This Audit Does NOT Establish

This audit explicitly does **not** establish, and must not be read as establishing:

- **research novelty** — no novelty is claimed for E1, for any component, or for the repository;
- **publication acceptance** — no venue outcome is predicted or implied;
- **educational effectiveness** — nothing here shows any intervention improves learning;
- **causal learning effects** — no data, no design, no analysis;
- **security effectiveness** — no security claim is made or measured;
- **model behaviour** — nothing here speaks to real model or agent behaviour;
- **benchmark validity** — the repository is not a benchmark, and neither source is treated as one.

It also does **not** preempt or clear the two candidate sources: they are recorded as **D. INSUFFICIENT EVIDENCE**, and no inference of absence is drawn from their unread full texts. Phase 17 remains CLOSED; no closed security-research direction was reopened.

---

## 19. Verification

Commands run after creating this file:

```
PYTHONPATH=src py -m pytest            -> 694 passed (exit 0)
agentsec labs check                    -> 8/8 labs passed (exit 0)
py -m mkdocs build --strict            -> exit 0, no warnings/errors
git diff --name-only                   -> (empty)
git status --porcelain                 -> ?? research/24-decisive-prior-art-closure.md
                                          (plus the still-untracked research/20, /21, /22, /23)
```

**Git safety confirmation:** no `git add`, no staging, no commit, no push, no reset, no checkout, no rebase, no amend, no clean.

**Files changed:** only `research/24-decisive-prior-art-closure.md` was created. No source, test, lab, policy, scenario, CI, MkDocs or site file was modified. No prior audit file was altered.

---

*End of audit. The decisive prior-art gap remains OPEN. No paper drafted; no study designed; no data collected.*
