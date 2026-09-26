# AgentSec Lab

Working project name for a planned empirical study on the security evaluation of LLM-based AI agents.

**Working research theme:** reproducible, adaptive, multi-model security evaluation of LLM-based agents, with explicit measurement of security, utility and operational cost.

---

## Status of this repository

This repository currently contains **one research-discovery deliverable only**. It contains **no paper**.

Not present, and intentionally not written: abstract, introduction, methodology, results, conclusion, or any claim of novelty. Those come after the direction is chosen and the experiments are run.

| Stage | State |
|---|---|
| Research landscape and gap analysis | **Complete** (draft v0.1) |
| Full-text reading of the priority papers | Not started |
| Systematic database search | Not started |
| Model configuration verification | Not started |
| Direction selection and pre-registration | Not started |
| Implementation, experiments, paper | Not started |

---

## What is in here

```
README.md
research/
├── 01-landscape-and-gap-analysis.md     # the deliverable: landscape, comparisons, gaps, directions
└── tables/
    ├── benchmark-comparison.csv          # 23 artefacts x 22 fields, machine-readable
    ├── gap-matrix.csv                    # 22 works x 16 capability columns + evidence level
    └── sources.csv                       # 50 sources with verification status
```

Start with `research/01-landscape-and-gap-analysis.md`. It is organised as sections **A–M** matching the brief:

| Section | Content |
|---|---|
| 0 | Method, evidentiary rules, verification labels, limitations of this pass |
| A | Executive research landscape summary |
| B (1A–1Q) | Literature analysis by topic |
| C (§2) | Benchmark comparison, plus three observations it yields |
| D (§3) | Research-gap matrix and per-column verdicts |
| E (§4) | Eight candidate gaps, with three explicit rejections |
| F (§5) | Three strongest directions, compared qualitatively (no numerical scoring) |
| G (§6) | Model-availability assessment for the four available models |
| J (§7) | Reproducibility requirements and a proposed repository structure |
| K (§8) | Threats to validity |
| L (§9) | Critical reviewer assessment |
| M | Bibliography |
| Appendix | Blocking next actions |

---

## Evidentiary rules this repository follows

These are enforced conventions, not aspirations. They exist because the project's stated requirement is that nothing may be fabricated.

1. **Every load-bearing claim was retrieved from a primary source in the session that produced it** — arXiv abstract pages, publisher/proceedings pages, standards drafts, repository or dataset pages.
2. **Verification labels.** `A` = primary source fetched. `B` = traceable secondary source only. `C` = unverified; **not usable in a paper until re-checked**. Recorded per source in `research/tables/sources.csv`.
3. **Venue claims are made only when the authors' own arXiv `Comments` field or a proceedings page states them.** Inference from prestige or from third-party bibliographies is not allowed.
4. **Missing data is written `not reported` or `unverified`.** It is never filled by inference. The two terms are distinct: `not reported` is weak evidence of absence; `unverified` is no evidence.
5. **No numeric result, benchmark score, citation, DOI or venue in this repository was produced from memory.**
6. **Where a claim's status is contested, the conflict is recorded rather than resolved by preference** (see the ST-WebAgentBench venue conflict and the capability–vulnerability contradiction between MCPTox and RAS-Eval).
7. **Community artefacts are not treated as peer-reviewed benchmarks.** `AgentInjectionBench` is recorded as a Hugging Face dataset with no located publication, and is explicitly marked as not citable as a benchmark.

### Known limitations of the current pass

- Most entries rest on **abstract-level** evidence, not full-text reading. `research/tables/gap-matrix.csv` carries a per-row `evidence_level` column for this reason. **The gap matrix is provisional** and must be re-derived from full texts before it justifies any publication claim.
- Coverage is English-language and skewed toward arXiv, ACL, NeurIPS, ICLR, ICML and USENIX. Non-English venues and industry disclosures are under-sampled.
- Search-engine sampling is not a systematic review. A documented database query (Scopus / Web of Science / ACM DL / IEEE Xplore) is still required.

---

## Headline findings from the analysis

Stated here only as pointers into the document; the reasoning and evidence are in §A, §C and §E.

- **Operational cost is the only comparison field that is uniformly absent** across every benchmark examined. That uniformity, not any single omission, is the strongest evidence in the analysis. Details: §C.3, §D.1.
- **Two credible benchmarks report opposite relationships between model capability and attack susceptibility** (MCPTox, `arXiv:2508.14925`; RAS-Eval, `arXiv:2506.15352`). Neither addresses the other. Details: §B (1N), §E (Gap 2).
- **The first three adjectives of the project's theme are already occupied** by AgentDojo, ASB, RAS-Eval and AgentDyn. The differentiating element, if any, is cost plus independent verifiability. Details: §A.4.
- **The available model set cannot support a capability-spread study**, because all four models sit in the same "Flash"/mini tier, and three of four providers are from one region. This threatens one of the three candidate directions outright. Details: §G.
- **Three candidate gaps are explicitly rejected** rather than reframed, because existing work substantially addresses them. Details: §D.3.

---

## AI-tool use

This repository requires transparency about how AI systems were used. The policy is drafted in §J.3 of the analysis document. Its central rule, which applied to this deliverable:

> No AI system generated a citation, a numeric result, or a claim about the literature without independent verification at the primary source.

**Disclosure for this deliverable:** an AI coding assistant was used to search for and retrieve sources, and to draft and structure the document. Every citation marked `A` was retrieved and read during the session. Every source marked `B` or `C` is flagged as such in `research/tables/sources.csv` and must be verified by a human before use in a manuscript.

---

## Immediate next actions

In dependency order. Items 1–2 block any experimental design.

1. **Full-text reading (blocking).** AgentDyn; Zhan et al. (`2503.00061`); Kirgis et al. (`2605.08545`); Progent; RAS-Eval; ASB; AgentDojo; and the taxonomy/consistency paper (`2605.16282`) to avoid duplicating its comparison.
2. **Systematic database search** with a documented, reproducible query string, to replace search-engine sampling and to check gaps 4 and 5 for prior art.
3. **Model verification.** Obtain vendor-issued specification pages and exact API model IDs for all four models; determine whether weights are downloadable and hash-pinnable. This also decides whether one of the three candidate directions survives.
4. **Check provider terms** for redistribution of raw model outputs — this gates the entire reproducibility design.
5. **Resolve the outstanding venue questions** in the bibliography, or drop the venue claim.

---

## Licences

Not yet assigned. Before any public release, `LICENSE` (code), `LICENSE-DATA` (data, likely CC-BY-4.0) and `CITATION.cff` must be created, and the dual-use policy for releasing attack payloads must be written.
