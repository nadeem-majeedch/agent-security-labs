# PHASE 21 — PHASE 4 EDUCATION: TRACE-READING EXERCISES AND FIELD REFERENCE (C1/C5)

*Implementation record for `research/39` items **C1** and **C5**, the education
step of the v0.1.0 plan's **Phase 4**. Nothing was committed, pushed, tagged or
version-bumped; the Phase 17 freeze and the `v0.0.1` release are untouched. No
**LAB-08** was created and no runtime/security semantics were added.*

## 1. Requirements (from `research/39`)

* **C1 [PROPOSED]** — "Extend the existing labs rather than add a numbered one
  (respecting **no LAB-08**): additional trace-reading exercise sets, extra
  'what if' prompts, and per-lab stretch questions."
* **C5 [PROPOSED]** — "A student-facing 'trace field reference' page derived
  from the schema (single source: `trace_json_schema()`), so prose cannot drift."
* `research/39` §16 — "additional trace-reading exercise sets (beyond the current
  sets A–G) with matching answer-key entries, and per-lab 'what if' variants"; "A
  trace-field reference page generated/derived from the schema".
* `research/39` §15 — wire new pages into `mkdocs.yml` nav; strict MkDocs build
  must stay green; the **answer key stays out of nav**.
* `research/39` §17 — acceptance: `mkdocs build --strict` exits 0; new pages are
  navigable; the answer key remains out of nav.

## 2. Baseline (verified before editing)

| Item | Value |
| --- | --- |
| Tests | **859 passed** |
| Labs | exactly **LAB-00 … LAB-07** (8); **no LAB-08** |
| `agentsec labs check` | **8/8** |
| MkDocs | `python -m mkdocs build --strict` exit 0 |
| Release gate | **READY WITH WARNINGS**, `blockers: []`, warnings `{W6, W7, W12}` |
| License accounting | **188** files, 9/9 |
| Existing practice material | `TRACE-READING-EXERCISES.md` (sets **A–G**, 36 exercises + a final challenge), `TRACE-READING-EXERCISES-ANSWER-KEY.md`, `TRACE-WALKTHROUGHS.md` (694 lines) |
| Trace schema | one JSON Schema, 12 event types (`discriminator.mapping`), a shared header, and a `UsageCounts` object; **no per-field descriptions** |

## 3. Audit findings

* **Which labs get exercises.** All of them: the exercise material already draws
  across LAB-00…LAB-07 and deliberately *does not* label which lab each fragment
  came from. C1 therefore extends the **existing** central practice document
  rather than adding a lab.
* **What C5 can derive.** The schema carries, per event, the field name, JSON
  type, `required` list, `const`/`enum`/`default`/`minimum`/`minLength`/`format`
  and a machine `title` (a Title-Cased field name). It carries **no prose
  meaning** for fields — only two top-level `description`s exist — so the
  *meaning* column has to be curated, while everything else is derived.
* **Existing generation mechanism.** `scripts/export_trace_schema.py` is the
  documented "sole writer" of the two schema copies, and
  `tests/schema/test_schema_file.py` / `test_packaged_schema.py` guard drift. C5
  mirrors that pattern exactly for the new page.
* **Docs root.** MkDocs uses `docs_dir: labs`, so the field reference must live
  under `labs/` and be added to `mkdocs.yml` `nav`.

## 4. Implementation

### 4.1 C5 — schema-derived trace field reference

**New generator:** `scripts/export_trace_reference.py`. It derives the page from
the *same* `trace_json_schema()` output `export_trace_schema.py` uses (imported
from `agentsec.trace.schema`, no new dependency, no second authoritative schema).

It renders, deterministically:

* an intro stating the page is generated and how to regenerate it;
* a **shared header** table (10 fields, in reading order);
* one section per **event type** (`TRACE_EVENT_TYPES` order) listing only the
  event-specific fields;
* the **`UsageCounts`** object (`usage` / `usage_total`).

Each row has **Field · Type · Required · Meaning**. Type labels carry the
`enum` values (e.g. `decision` → *string - one of `allow`, `deny`,
`require_approval`*), `const` values, nullability from `anyOf`, and constraints
(`non-empty`, `>= 0`, RFC 3339 date-time). A field with no entry in
`FIELD_MEANINGS` (or an event with no `EVENT_MEANINGS` entry) makes the generator
**fail**, so a new schema field forces a deliberate documentation update.

**Generated page:** `labs/TRACE-FIELD-REFERENCE.md` (186 lines) — committed and
kept in sync by a test (below). Documented: all 10 shared header fields, every
event-specific property across the 12 event types, and the `UsageCounts` object.

### 4.2 C1 — additional exercise sets and per-lab what-if questions

`labs/TRACE-READING-EXERCISES.md` gains, before the capstone:

* **Exercise Set H — Field discipline** (6 questions): which field records which
  fact, required vs optional, `args_redacted` vs `args_hash`, `parent_event_id`,
  `schema_version`, the `decision` enum and `side_effects` — linking to the new
  field reference.
* **Exercise Set I — "What if" reasoning** (6 questions): flip one thing in a
  seen trace (a decision, an approval, a write, a delete, an egress) and ask
  which events change and why.
* **Per-lab "what if" stretch questions** — one counterfactual for **each** lab,
  LAB-00 … LAB-07, in the lab sequence.

All fragments use fields and behaviours the project already produces; no trace
example contradicts the schema or the implementation, and no new runtime
semantics are implied. Matching entries were added to the **instructor-only**
`TRACE-READING-EXERCISES-ANSWER-KEY.md` (Sets H and I, and a per-lab section).

*Design note:* per-lab "what-if" variants live in the central practice document,
following the established convention that student material and the answer key
are the single home for exercises (the lab READMEs carry guided questions and
checklists, not duplicated exercise banks). This avoids two drifting copies.

## 5. Documentation / navigation changes

`mkdocs.yml` gains one nav entry, without restructuring the site:

```yaml
  - Understanding Traces: TRACE-WALKTHROUGHS.md
  - Trace Field Reference: TRACE-FIELD-REFERENCE.md
  - Practice: TRACE-READING-EXERCISES.md
```

The answer key stays **out of nav** (unchanged). The exercises document now
links the field reference from its intro sets and its "Where to go next" list.
`python -m mkdocs build --strict` builds the site with 0 warnings, so every new
link resolves.

## 6. Tests added

| File | Tests | Guards |
| --- | --- | --- |
| `tests/schema/test_trace_reference.py` | 4 | the committed page equals fresh generator output; every schema field and event type is documented; every schema field has a curated meaning; the page is in the MkDocs nav |
| `tests/test_trace_exercises.py` | 4 | every numbered exercise has a matching answer-key entry (and vice versa); the per-lab what-if section covers every lab; the student page links the field reference |

No existing test was weakened. The two new `tests/*.py` modules are also picked
up automatically by `tests/test_architecture.py`'s per-file parametrisation.

## 7. Validation results

Run locally with the project interpreter (CPython 3.13.14):

| Command | Result |
| --- | --- |
| `python -m pytest` | **869 passed** (859 → 869: 8 new tests + 2 architecture parametrisation cases) |
| `python -m agentsec labs check` | **8/8 labs passed** |
| `ruff check src tests scripts` | exit 0 — **All checks passed!** |
| `python -m mypy` | exit 0 — **Success: no issues found in 40 source files** |
| `python -m mkdocs build --strict` | exit 0 |
| `python scripts/check_licensing.py` | **9/9** — 193 files accounted for (mit 130, cc-by 61, excluded 2, unlicensed 0), including this record |
| `python scripts/check_version.py` | **3/3** |
| `python scripts/release_check.py --json` | **READY WITH WARNINGS**, `blockers: []`, `warnings: ["W12","W6","W7"]` |
| `git diff --check` | clean |

### 7.1 Explicit acceptance checks

| Check | Result |
| --- | --- |
| Exactly 8 labs; LAB-08 absent | yes (LAB-00 … LAB-07) |
| All LAB-00 … LAB-07 self-checks pass | 8/8 |
| Reference corresponds to the canonical schema | `read_text() == render()` — **in sync: True** |
| MkDocs navigation contains the reference | yes |
| No broken documentation links | strict MkDocs exit 0 |
| No generated/build artifacts tracked | none (`build/`, `dist/`, caches, probes all absent) |
| `blockers: []` | yes |
| Warnings exactly W6/W7/W12 | yes |
| Version remains `0.0.1`; `v0.0.1` untouched | yes (`cd60b32…`) |

## 8. Files changed

```
labs/TRACE-READING-EXERCISES.md            (+ Set H, Set I, per-lab what-if, field-reference links)
labs/TRACE-READING-EXERCISES-ANSWER-KEY.md (+ matching answers)
labs/TRACE-FIELD-REFERENCE.md              (new, generated)
scripts/export_trace_reference.py          (new generator)
mkdocs.yml                                 (+ one nav entry)
tests/schema/test_trace_reference.py       (new)
tests/test_trace_exercises.py              (new)
research/48-c1-c5-trace-education.md       (this record, new)
```

**Not modified:** `src/`, `labs/LAB-*/` configs and READMEs, `schemas/`,
`scripts/release_check.py`, `.github/workflows/`, `pyproject.toml`, and the
B4/B5 quality-gate configuration and tests.

## 9. Limitations and deferred items

* **Meanings are curated, not derived.** The schema has no per-field prose, so
  `FIELD_MEANINGS` is hand-written; the generator/tests only guarantee that every
  field *has* a meaning, not that the wording is perfect. This is stated in the
  generator docstring and on the page.
* **C1 was implemented in the central practice document**, not by adding exercise
  banks to each lab README (rationale in §4.2). Per-lab coverage is complete but
  lives in one place.
* **`security_event` is documented as defined-but-not-emitted** — the reference
  says so plainly rather than implying a runtime that emits it.
* **Remaining Phase 4 items (per `research/39` §11):** optional **C3** (a richer
  read-only `inspect` view) and optional **C4** (use the three unused fixtures
  without a new numbered lab) — neither is part of this step.

## 10. Final status

**C1: [IMPLEMENTED].** **C5: [IMPLEMENTED].**

### Safety boundary (Phase 17)

This step adds no runtime behaviour, no research implementation, no corpus, no
experiment and no learner data. Phase 17 remains **CLOSED**; E1 remains **HOLD**;
no novelty, effectiveness, security-effectiveness, benchmark or publication claim
is made. No LAB-08 was created.
