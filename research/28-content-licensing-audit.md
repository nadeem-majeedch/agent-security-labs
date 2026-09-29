# Phase 20 — Step 11: Content Licensing Audit

**Phase:** 20 — Step 11 (content/documentation licensing)
**Date:** 2026-09-29
**Repository:** `https://github.com/nadeem-majeedch/agent-security-labs`
**Audited revision:** `995cf68` (`main`) with the uncommitted Step 10–11 working tree
**Documentation site:** `https://nadeem-majeedch.github.io/agent-security-labs/`
**Deliverable:** `LICENSE-DATA` (new), a `Licensing` section in `README.md`, and this record.
**Mode:** read-only audit plus the licensing edits below. No code, tests, labs, policies, scenarios, CI, MkDocs or research-audit file was modified.

---

## 1. Audit scope

Step 10 licensed the **software** of this repository under MIT (`LICENSE`, `pyproject.toml`, `CITATION.cff`, `README.md`). This step audits whether the repository should carry a **second licence for its non-software content** — documentation, lab instructions, exercises, instructor material, and machine-readable content — and, if so, exactly which files that licence may and may not cover.

The audit was performed against the working tree, and it inspected:

| Area | Inspected |
|---|---|
| Licence/metadata files | `LICENSE`, `pyproject.toml`, `CITATION.cff`, `README.md` |
| Documentation | `docs/`, `labs/**/*.md` |
| Content and configuration | `labs/**/*.yaml`, `policies/`, `configs/`, `schemas/` |
| Research records | `research/**/*.md`, `research/tables/*.csv` |
| Tooling/CI | `scripts/`, `.github/`, `mkdocs.yml` |
| Historical records | `research/01`, `research/13`, `research/14`, `research/20`, `research/27` |

Two questions governed the work:

1. **Is a second licence justified at all?** A repository that adds a licence it cannot honestly apply is worse off than one that ships only the software licence.
2. **Where exactly is the boundary?** A content licence that silently claims third-party material is a misrepresentation, so the boundary had to be established from evidence, not convention.

This is a licensing/documentation task. It did **not** reopen Phase 17, did not reopen the closed security-research directions, did not search the literature, did not draft a paper, did not design or run a study, and did not collect learner data.

---

## 2. Current MIT licence state (as established by Step 10)

| Artifact | State |
|---|---|
| `LICENSE` | Verbatim MIT licence text, `Copyright (c) 2026 Dr. Muhammad Nadeem Majeed`. **Unmodified by this step.** |
| `pyproject.toml` | `license = { text = "MIT" }` (was `"TBD"` before Step 10). |
| `CITATION.cff` | `license: MIT`. |
| `README.md` | Documents the MIT software licence. |

The MIT text refers to "this software **and associated documentation files**". That phrase matters: a bare reading arguably already reaches the Markdown documentation. The consequence is recorded in §16 as a residual question rather than resolved by narrowing the MIT text — `LICENSE` is standard template wording and was left byte-for-byte untouched.

---

## 3. Historical content-licence intent

A separate content/data licence was contemplated three times during planning and then left unassigned. Exact evidence:

| Location | Text | Kind |
|---|---|---|
| `research/01-landscape-and-gap-analysis.md:670` | `├── LICENSE-DATA            # data: CC-BY-4.0` | historical plan |
| `research/01-landscape-and-gap-analysis.md` (item 21) | "**Licences** separately for code, data, and documents." | historical plan |
| `research/13-lab-scope-and-architecture.md:306` | `├── LICENSE-DATA               # data/docs, likely CC-BY-4.0` | historical plan |
| `research/14-implementation-blueprint.md:29` | `├── LICENSE-DATA                   # docs/data licence (e.g. CC-BY-4.0)` | historical plan |
| `research/20-research-positioning-audit.md:348` | "`LICENSE`, `LICENSE-DATA`, `CITATION.cff` … all still unassigned" | audit finding |
| `research/27-design-rationale-artifact-audit.md:363` | "`LICENSE-DATA` (or equivalent) — **Absent**" | audit finding |

**How this evidence was weighed.** The plan documents name a *file name and a candidate licence* (`#"likely"`, `#"e.g."`), never an executed decision, and the two later audits record it as outstanding housekeeping. So the historical records establish **intent and a candidate licence**, not a decision. They are also consistent with the separate licence file being for **content/data**, not code, which is the option this step implements.

Note also that `research/01` and `research/13` label the path `LICENSE-DATA` and describe it as covering "data", "docs" and "documents" — a wider category than the Markdown-only scope adopted in §6. That difference is deliberate and is explained there.

No third-party licence was found anywhere in this repository. The only other CC references in tracked files — `research/11`, `research/24`, `research/25`, `research/tables/sources.csv` — describe **licences of cited external works** (e.g. a CC BY 4.0 OpenReview submission; Wilson 2026 under CC-BY), never a licence of this repository. Those were excluded from the analysis and must not be read as repository licensing evidence.

---

## 4. Repository content categories

Tracked population: **153 files** (`git ls-files`), partitioned as follows.

| # | Category | Files | Examples | Licence assigned |
|---|---|---|---|---|
| 1 | Software source | 74 `.py` | `src/agentsec/**`, `tests/**`, `scripts/export_trace_schema.py` | **MIT** |
| 2 | Repository-authored documentation | 39 `.md` | `README.md`, `docs/development.md`, `labs/**/*.md`, `research/**/*.md` | **CC BY 4.0** |
| 3 | Configuration / scenario content | 20 `.yaml` | `labs/**/{config,scenario}.yaml`, `policies/examples/*.yaml`, `configs/examples/*.yaml` | **MIT** |
| 4 | Machine-readable schema | 1 `.json` | `schemas/trace/trace_event.v1.schema.json` (generated from the models, drift-tested) | **MIT** |
| 5 | Research tables (data) | 13 `.csv` | `research/tables/*.csv` | **MIT** (third-party exclusions apply) |
| 6 | Build / CI configuration | 3 `.yml`, 1 `.toml`, 1 `.gitignore` | `mkdocs.yml`, `.github/workflows/{ci,docs}.yml`, `pyproject.toml`, `.gitignore` | **MIT** |
| 7 | Local tooling metadata | 1 | `.freebuff/project-id` | **excluded** — not project content |
| 8 | Licence instruments | 2 | `LICENSE` (MIT template); `LICENSE-DATA` (CC legal code, public-domain-dedicated) | **excluded** — licence texts are not licensed content |

By directory: `labs/` 30 (15 `.md` + 15 `.yaml`), `src/` 39, `tests/` 34, `research/` 35 (22 `.md` + 13 `.csv`), `policies/` 4, `.github/` 2, `docs/` 1, `schemas/` 1, `configs/` 1, `scripts/` 1, plus 5 root files.

The partition is therefore complete and disjoint: **39 Markdown files → CC BY 4.0; the other 114 → MIT** (with `.freebuff/` and the licence texts outside both grants).

---

## 5. Third-party and provenance findings

A conservative provenance scan was run across every tracked text file.

**Scans performed and results**

| Scan | Command pattern | Result |
|---|---|---|
| Copyright/licence notices | `copyright`, `all rights reserved`, `SPDX`, `©`, `(c) 20`, `adapted from`, `reprinted`, `used with permission` over `.md/.yaml/.yml/.csv/.json/.py` | **Zero hits** outside the two licence files (and the MIT boilerplate phrase "authors or copyright holders"). No third-party notice, no vendored or adapted code. |
| Non-text assets | `git ls-files` filtered to `png jpg jpeg gif svg pdf docx pptx xlsx ipynb zip tar gz woff ttf` | **Zero.** The only non-text, non-source tracked files are the 13 research CSVs. No figure, image, photograph, font, media file, notebook or dataset is redistributed. |
| Non-Markdown/YAML files in content dirs | `find docs labs schemas policies configs` excluding `*.md/*.yaml/*.yml` | Only `schemas/trace/trace_event.v1.schema.json`. |
| External URLs in reader-facing content | `https?://…` over `labs/`, `docs/`, `README.md` | **Three, all first-party:** the Pages URL (×2) and the GitHub repository URL (×1). |

**Categories established**

1. **Repository-authored code** — all Python; no vendored dependencies (dependencies are *declared* in `pyproject.toml`, not copied in).
2. **Repository-authored documentation** — all `.md`; written for this project; prose, tables and exercises only.
3. **Configuration/scenario content** — YAML authored here; consumed by the harness.
4. **Generated/derived material** — `schemas/trace/trace_event.v1.schema.json` is generated from the models and guarded by a drift test (derived from repository-owned source → MIT). `site/` is generated build output and `runs/` is generated run output; **both are git-ignored and untracked**, so neither is distributed and neither is in licensing scope.
5. **Research records** — repository-authored, but **contain third-party material**: bibliographic records (titles, author names, venues, DOIs, URLs) and short quotations of cited published work, most visibly the quoted findings recorded in `research/tables/sources.csv` and the audits in `research/20`–`research/26`.
6. **Third-party material** — as above, plus the CC BY 4.0 legal code embedded in `LICENSE-DATA` (itself public-domain-dedicated by Creative Commons).
7. **Ambiguous items** — one candidate: `.freebuff/project-id` (local coding-tool metadata, accidentally tracked). It is neither educational content nor software; it is **excluded** from both grants and was **not** deleted or modified, pending an owner decision (§16).

**Nothing ambiguous was deleted or rewritten**, as instructed.

**Conclusion.** The repository redistributes **no** third-party code, figure, image, dataset, font or lengthy excerpt that a content licence could not legitimately cover. The only third-party text present is scholarly citation and short quotation inside the research records — which the grant must therefore **exclude**, which §7 does.

---

## 6. Proposed and adopted CC BY scope

**Decision: CC BY 4.0 is safe to apply — to Markdown authored for this repository.**

The line adopted is deliberately the narrowest one that is also unambiguous:

> **What a person reads is CC BY 4.0. What a machine parses is MIT.**

Anything a human being is meant to read *as prose or as an exercise* — the landing page, the architecture reference, the lab instructions, the walkthroughs, the exercises, the instructor guide, the research records — is educational content, and CC BY 4.0 is the conventional licence for material an instructor is expected to reuse and adapt. The step's own proposed boundary listed "schemas" and "YAML scenario/configuration content" among the candidate content categories; the audit **narrowed** that, because those files are inputs to the harness and are not read by learners as text. Assigning them to MIT keeps one crisp boundary rather than a list of judgement calls.

Adopted scope (**licensed CC BY 4.0**, 39 files):

* `README.md`
* `docs/**/*.md`
* `labs/**/*.md` — the lab map and observables matrix, the individual LAB-00…LAB-07 instructions, the trace walkthroughs, the practice exercises **and the instructor-only answer key**, the getting-started page, the local-verification page, the instructor guide
* `research/**/*.md` — the repository's own analysis, subject to the exclusions in §7

---

## 7. Exclusions

**Not covered by the content licence: everything in §4 categories 1, 3, 4, 5, 6 and 7.** Those are MIT (categories 1, 3, 4, 5, 6) or outside both grants (7). The practical rendering: `labs/LAB-04-tool-misuse/scenario.yaml` is MIT while `labs/LAB-04-tool-misuse/README.md` is CC BY 4.0; `policies/` and `configs/` are MIT; the research CSVs are MIT.

**Third-party material is excluded from *both* grants, repository-wide.** CC BY 4.0 would in any case not reach it — this repository cannot license what it does not own — and the exclusion is stated explicitly so that no reader infers otherwise. Specifically outside the content grant:

* quotations of, and excerpts from, cited published work;
* bibliographic records: titles of cited works, author names, journal/venue names, DOIs, URLs;
* any third-party figure, image, photograph, dataset, font or lengthy excerpt — of which this repository contains **none**.

The exclusion is stated in `LICENSE-DATA` §3 and in the README's `Licensing` section, and it applies to the Markdown records *and* to the CSV tables alike, so it does not matter that the two file types carry different repository licences.

**Also excluded:** `.freebuff/project-id` (tooling metadata) and the licence instruments themselves (`LICENSE`'s MIT template; `LICENSE-DATA`'s embedded CC legal code, dedicated to the public domain under CC0).

**No third-party material is represented as repository-owned** anywhere in the new files.

---

## 8. Was `LICENSE-DATA` created?

**Yes.** The audit supports a content licence with a defensible, narrow scope, so it was created rather than skipped.

Contents (~24 KB), in order:

1. **Scope** (§1) — the file-name-level list of covered Markdown.
2. **Exclusions** (§2) — the MIT list, the statement that the MIT grant's "associated documentation files" phrase now coincides with the content licence, and the two outside-both categories.
3. **Third-party material** (§3) — the exclusion, and the explicit statement that no third-party asset is redistributed.
4. **Attribution** (§4) — a ready-made attribution string plus the "indicate if you changed anything" and no-endorsement requirements.
5. **Notes** (§5) — that the notice states the project's licensing intent, is not legal advice, and grants nothing beyond the legal code; as-is disclaimer.
6. **Legal code** (§6) — the **complete, unmodified CC BY 4.0 legal code**, preceded by the canonical URL.

**Fidelity of the legal code.** The canonical plain-text legal code was retrieved from `https://creativecommons.org/licenses/by/4.0/legalcode.txt` (18,657 bytes, 396 lines) and the embedded copy was verified against it:

```
extract bytes=18657  canonical bytes=18657
diff → no differences
md5  2ab724713fdaf49e4523c4503bfd068d  (both the embedded section and the canonical file)
```

The embedded text is therefore **byte-identical** to Creative Commons' own published legal code — no paraphrase, no re-typesetting, no editing. Shipping the full text rather than a bare hyperlink was chosen deliberately: the repository is offline-first, its existing `LICENSE` is self-contained, and instructors may copy the labs without network access. The authoritative URL is given as well.

---

## 9. Exact files created and modified

| File | Action | Detail |
|---|---|---|
| `LICENSE-DATA` | **created** | New content licence: scope notice + byte-exact CC BY 4.0 legal code. 24,031 bytes. |
| `README.md` | **modified** | `+25/−2`: one `Repository status` bullet rewritten; a 24-line `## Licensing` section inserted before `## Citation`. (`git diff --numstat` reports `+42/−3` cumulative against `HEAD`, because Step 10's README changes are also still uncommitted.) |
| `research/28-content-licensing-audit.md` | **created** | This record. |

Untouched: `LICENSE`, `CITATION.cff`, `pyproject.toml`, all of `src/`, `tests/`, `labs/`, `policies/`, `configs/`, `schemas/`, `docs/`, `mkdocs.yml`, `.github/`, and **every** existing research record (`research/20`–`research/27` were neither edited nor reconciled).

For completeness: the working tree also carries the **Step 10** changes (`LICENSE`, `CITATION.cff` new; `README.md`, `pyproject.toml` modified), all still uncommitted, because the owner has not yet committed Step 10.

---

## 10. README changes

Minimal, additive, and confined to licensing/citation. No educational content, architecture description, lab map, research-boundary statement or verification claim was altered.

**1. `Repository status` bullet** — the single-line MIT statement became a two-licence statement pointing at the `Licensing` section for the boundary.

**2. New `## Licensing` section**, inserted between `Repository status` and `Citation`, containing:

* the one-line rule — *"what the harness parses is MIT; what a person reads is CC BY 4.0"*;
* a three-row table mapping material → licence → licence file, with the MIT row split into software and machine-readable configuration, and the paths listed explicitly;
* a worked example of the boundary ("the labs' YAML is MIT while the instructions that explain them are CC BY 4.0");
* a plain-language statement of what reuse is permitted (adapt the exercises, walkthroughs and instructor material, including in teaching, with attribution and a note of changes), pointing at `LICENSE-DATA` for scope, attribution string and full text;
* the third-party disclaimer scoped to `research/`, restoring the software/citation pointer.

**No** wording was added that characterises the content as novel, validated, effective, superior, benchmark-grade or publication-ready. No link to an untracked research audit was added.

---

## 11. `CITATION.cff` and `pyproject.toml` decision

**Both unchanged by this step.**

* `pyproject.toml` keeps `license = { text = "MIT" }`. Changing it to CC BY would have been wrong: it is Python packaging metadata describing the **distributed package** (the `agentsec` software), which is MIT. Regression to `"TBD"` was explicitly avoided.
* `CITATION.cff` keeps `license: MIT`. CFF 1.2.0 defines `license` as the licence of **the work being cited**, which is the software, and the field takes a single value — so the dual model cannot be expressed there. The distinction is therefore documented in the README's `Licensing` section (and §16 records it as a residual item), which is the option the step brief anticipated for exactly this case.

---

## 12. Validation results

Run after the edits, at this revision.

| Check | Command | Result |
|---|---|---|
| Test suite | `PYTHONPATH=src py -m pytest` | **694 passed** (dot count 694; F=0, E=0, skipped=0, xfail=0), exit 0 — identical to baseline |
| Lab self-check | `PYTHONPATH=src py -m agentsec labs check` | **8/8 labs passed** (LAB-00 … LAB-07 all PASS), exit 0 |
| Documentation build | `py -m mkdocs build --strict` | **exit 0.** The only line matching `warning|error` is line 2, Material for MkDocs' informational upstream 2.0 notice — not an MkDocs warning, and no new warning was introduced. The build reads `docs_dir: labs`, so root-level licence files are outside it and cannot affect it. |
| Licence-text fidelity | `diff` + `md5sum` vs canonical `legalcode.txt` | **byte-identical**, md5 `2ab724713fdaf49e4523c4503bfd068d` |
| `LICENSE` still MIT | `head -3`, `git diff` | Unmodified verbatim MIT; not in `git diff --name-only` |
| `pyproject.toml` not regressed | `grep '^license'` | `license = { text = "MIT" }` |
| `CITATION.cff` still valid + MIT | YAML parse; `grep '^license'` | `license: MIT`; file untouched |
| README link integrity | every relative link tested with a filesystem existence check | **41/41 resolve**, including the new `LICENSE-DATA` link; 0 broken |
| README anchors | `#licensing` → `## Licensing`; `#verification-status` → `## Verification status` | both resolve |
| Claim scan (new files) | `novel|state-of-the-art|benchmark|effective|improves learning|superior|better than|publication-ready|validated` over `README.md` and `LICENSE-DATA` | **No positive claims.** The only hits are a pre-existing negation in the README ("does **not** … assert that any policy is 'effective'"), three occurrences of the defined term *"Effective Technological Measures"* inside the CC legal code, and the word "benchmark" inside the CC legal code's normative text — none of which is a claim about this repository. |

---

## 13. Research-boundary verification

Confirmed for this step:

* **No research implementation** was added or changed.
* **No paper** was drafted, no abstract written, no venue discussed.
* **No empirical study** was designed; no learner evaluation, instrument, survey, rubric, metric or hypothesis was introduced.
* **No learner data** was collected, referenced or solicited.
* **No novelty claim** was made. `LICENSE-DATA` and the README section make only descriptive licensing statements.
* **No benchmark, effectiveness, superiority or publication-readiness claim** was made.
* **No literature search** was performed; no prior-art conclusion was revisited.
* **Phase 17 remains CLOSED** and its closed research directions remain closed.
* **E1 remains HOLD**; `research/20`–`research/27` were not edited, so every previous classification and uncertainty reading stands exactly as recorded.
* **The publication gate is unaffected** by this step. A content licence is release housekeeping, not evidence. It adds nothing to Gate A/B/C except that one more reproducibility/housekeeping prerequisite now exists.

---

## 14. Git status

```
$ git status --porcelain
 M README.md
 M pyproject.toml
?? CITATION.cff
?? LICENSE
?? LICENSE-DATA
?? research/28-content-licensing-audit.md

$ git diff --name-only
README.md
pyproject.toml
```

`HEAD` is `995cf68` ("Research finding complete"), which tracks `research/20`–`research/27`. The two modified files are Step 10's (`README.md`, `pyproject.toml`) plus this step's README addition; the four untracked files are Step 10's two new files, this step's `LICENSE-DATA`, and this record. `research/28` is expected to appear untracked — the instruction was to leave it for manual handling.

---

## 15. Staging / commit / push confirmation

**Nothing was staged. Nothing was committed. Nothing was pushed.**

No `git add`, no `git commit`, no `git push`, no `git reset`, no `git checkout`, no `git clean`, no `git rebase`, no `git amend` was run at any point in this step. All changes are left uncommitted and unstaged for manual review by the repository owner. No tracked file was modified beyond `README.md` and `pyproject.toml`; no research audit was modified.

---

## 16. Unresolved licensing questions

Recorded honestly; none was silently "fixed".

1. **MIT's "associated documentation files" phrase overlaps the CC BY grant.** `LICENSE` (standard MIT template, deliberately left verbatim) arguably already covers the documentation. A downstream user who received the docs under MIT retains those rights; the content licence is an explicit, narrower-scoped statement of the project's intent for readers, not a retraction. If the owner wants a strictly exclusive boundary — documentation CC BY 4.0 *only* — the scope wording inside `LICENSE` would have to be narrowed, and that is a decision, not a mechanical edit. **Owner decision required.**
2. **CC BY 4.0 was never formally decided, only contemplated.** Three planning records name it as `"data: CC-BY-4.0"`, `"likely CC-BY-4.0"`, `"e.g. CC-BY-4.0"`. This step treated that as intent plus a candidate licence and adopted it; the owner may instead prefer CC BY-SA 4.0 (share-alike, to keep derived teaching material open) or CC0 for maximum reuse. Changing it later means changing one file, one table row and one README section.
3. **The adopted scope is narrower than the historical plan.** `research/01`/`13`/`14` describe `LICENSE-DATA` as covering "data/docs/documents"; this step covers **Markdown only**, leaving YAML scenarios, the JSON Schema and the research CSVs under MIT. Deliberate (§6) and documented, but it does mean the plan records and the repository now differ in detail — and those records are historical and were not rewritten.
4. **`.freebuff/project-id` is tracked.** Local coding-tool metadata that is neither content nor software; excluded from both grants but left in place. Removing it (as untracked or git-ignored) is an owner decision.
5. **No SPDX identifiers anywhere.** Machine-readable licence detection will rely on the two root licence files and the README. Optional future work: SPDX headers or a `license-files` entry in `pyproject.toml`.
6. **`research/27` now describes a superseded state.** It is tracked and records `LICENSE`/`LICENSE-DATA`/`CITATION.cff` as "Absent", which was true when written. Per instruction it was **not** modified. Anyone reading it alongside this record should treat this record as the current state.
7. **Traces under `runs/` carry no licence statement.** They are git-ignored and never distributed, so nothing is licensed there — but if trace files are ever published (e.g. as example artefacts), a data decision would be needed. Not in scope here.
8. **No release exists**, so there is still no `date-released` in `CITATION.cff` and no versioned DOI. Release metadata remains Step 10's open item.
9. **`pyproject.toml`'s `description` still ends "(Phase A skeleton)"**, which is stale. Out of scope for both Step 10 and this step; flagged only.

---

## 17. Conclusion

The repository now carries an honest two-licence model instead of an unassigned one.

* **Software and machine-readable configuration → MIT**, unchanged and still declared consistently in `pyproject.toml` and `CITATION.cff`.
* **Documentation and educational text → CC BY 4.0**, in `LICENSE-DATA`, which states its scope, its exclusions, an attribution string, and the complete legal code verified byte-identical to Creative Commons' own text.
* **Third-party citations and quotations are excluded from both**, explicitly, in both the licence file and the README.

The scope is deliberately the narrowest defensible one — Markdown only — because everything else is parsed by the harness rather than read by a person, and because narrowing removed every ambiguous call the broader proposal would have forced. Nothing ambiguous was deleted; every residual question is itemised in §16 rather than decided unilaterally.

**What this step does not establish:** research novelty, publication acceptance, educational effectiveness, causal learning effects, security effectiveness, model behaviour, benchmark validity, or measurement validity. It settles the provenance and licensing of the repository's own content and nothing else.
