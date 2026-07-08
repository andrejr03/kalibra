# Kalibra — Engineering Documentation Naming Review v1.0

**Status:** Review only. No file is moved, renamed, deleted, sanitized, archived,
committed, or pushed by this document. It decides the public documentation
naming scheme before any migration happens.
**Date:** 2026-07-08
**Branch:** `codex/initial-engineering-skeleton`
**Repository HEAD observed:** `cd846f4`
**Repository:** `/Users/agentisstudio/Documents/kalibra`

## 0. Purpose and Boundary

Kalibra is being prepared for public GitHub publication. Two prior plans already
exist and are the authority for *what* is public:

- `docs/plans/KALIBRA_PUBLIC_GITHUB_PREPARATION_PLAN_v1.0.md`
- `docs/plans/KALIBRA_CHECKPOINT_ADR_PUBLIC_CURATION_PLAN_v1.0.md`

This review does **not** re-decide public vs private classification. It inherits
those classifications and decides only the **public naming scheme**: naming
principles, the final documentation taxonomy, and an exact
`current path -> public path` mapping for every document that is PUBLIC or a
public-facing REVIEW_REQUIRED candidate.

Classification vocabulary inherited from the curation plan:

- **PUBLIC** — keep in the public repository.
- **PRIVATE_ARCHIVE** — move to the private archive; never published, so this
  review assigns it **no public name**.
- **REVIEW_REQUIRED** — do not publish as-is; resolve during sanitization. Where
  the resolution can yield a public document, this review assigns the public
  name that document should take.

## 1. Current Naming Audit

All tracked `docs/` files were audited (`find docs -maxdepth 3 -type f`). The
current scheme is uniform and internal-workflow-heavy:

`KALIBRA_` prefix + topic + workflow role + `_v1.0` suffix, with a
`docs/checkpoints/` folder.

Internal-workflow / process tokens present in current filenames:

| Token | Where it appears | Public verdict |
| --- | --- | --- |
| `KALIBRA_` | every doc | Drop — redundant with the repository name. |
| `_v1.0` | every doc | Drop — git history and release tags carry versioning. |
| `CHECKPOINT` | 31 files in `docs/checkpoints/` | Drop — internal workflow language; no `checkpoints/` folder in public. |
| `AUTHORIZATION` | ~11 checkpoints + 1 top-level doc | Drop — all PRIVATE_ARCHIVE; not published. |
| `CLOSURE` | 3 top-level + several checkpoints | Drop — replace with topic/"milestone" naming. |
| `REVIEW` / `REREVIEW` | portfolio + phase closure reviews | Drop — internal review-iteration language. |
| `IMPLEMENTATION` (as `*_IMPLEMENTATION_PLAN`, `*_COMPLETION`) | many | Drop from public names; most are PRIVATE_ARCHIVE. |
| `PLAN` (per-slice/baseline plans) | many | Drop — internal per-slice planning; all PRIVATE_ARCHIVE. See §5 exception for the single normative `ENGINEERING_PLAN`. |
| `PROMPT` | none in filenames (only in body text) | N/A for filenames. |
| `C1`..`C6` | 6 checkpoints | Drop — internal checkpoint numbering. |
| `ML_PHASE_1/2/3`, `PHASE_1/2` | many | Drop the phase index; keep `ML` only as a product/domain term (machine learning), never as `ML_PHASE`. |
| `SPRINT_1F` | 1 evidence doc | Drop — internal sprint label. |
| `INVESTIGATION` | 3 research docs | Drop — `research/` folder implies it. |
| `EVIDENCE` (suffix) | 10 evidence docs | Drop the suffix — `evidence/` folder implies it. |
| `DECISION_MEMO`, `STRATEGY` (ML-phase internals) | several | Not published (PRIVATE_ARCHIVE); no public name. |

Legitimate **product/domain** terms that are NOT workflow vocabulary and stay:
`PADIM`, `ONNX`, `VISA`, `MPDD`, `RUNTIME`, `EQUIVALENCE`, `INFERENCE`,
`EVALUATION`, `DATASET`, `MODEL_FAMILY`, `PORTFOLIO`, `ML` (as machine learning),
`GOVERNED`/`GOVERNANCE`.

## 2. Public Naming Principles

The public repository targets external technical reviewers (recruiters,
engineers) with zero Kalibra context. Filenames must read as topic-first
documentation, not as internal process artifacts.

1. **Readable by external reviewers.** The filename alone states the subject.
2. **No internal workflow vocabulary.** No `CHECKPOINT`, `AUTHORIZATION`,
   `CLOSURE`, `REVIEW`, `REREVIEW`, `COMPLETION`, `PROMPT`, per-slice `PLAN`,
   `SPRINT`, `C1..C6`, `ML_PHASE_N`.
3. **No process / preparation vocabulary.** Nothing that describes the
   publication process, AI-agent workflow, or archival planning survives into a
   public filename.
4. **Topic-first, descriptive.** `DATASET_SELECTION_RATIONALE`, not
   `C1_DATASET_SELECTION_CLOSURE_CHECKPOINT`.
5. **No `KALIBRA_` prefix.** The repository is named `kalibra`; the prefix is
   redundant noise on every file.
6. **Minimal version suffixes.** Drop `_v1.0`. Versioning lives in git history
   and release tags. Re-introduce a suffix only if two live public versions of
   the same document must coexist (not the case today).
7. **Stable filenames.** Names chosen here should not need to change again;
   they are keyed to durable topics, not phase numbers or iteration counts.
8. **No `checkpoints/` folder** and **no `plans/` folder** in the public tree.
9. **Folder implies role.** Because `adr/`, `engineering/`, `evidence/`, and
   `research/` carry the role, do not repeat it in the filename (`EVIDENCE`,
   `INVESTIGATION`, `ADR` suffixes are dropped).

### Case convention (decision)

- **`docs/adr/`** uses the industry-standard numbered lowercase-kebab form:
  `NNN-topic.md` (e.g. `001-dataset-selection.md`). This matches how external
  reviewers expect to find ADRs.
- **All other docs** use `UPPER_SNAKE_CASE.md`. Justification: it preserves the
  readable style of the retained normative set (`FOUNDATION`, `ARCHITECTURE`,
  …) that AGENTS.md already declares public, keeps a single consistent
  convention across `architecture`/`engineering`/`evidence`/`research`, and
  minimises churn versus a full kebab-case rewrite. ADRs are the one deliberate,
  convention-driven exception.

## 3. Public Documentation Taxonomy (decision)

Final public documentation tree. Folders are chosen so that role is expressed by
location, not by filename tokens.

```text
docs/
  FOUNDATION.md
  ARCHITECTURE.md
  SYSTEM_REQUIREMENTS.md
  EVALUATION_METHODOLOGY.md
  DATASET_STRATEGY.md
  IMPLEMENTATION_ROADMAP.md
  ENGINEERING_PLAN.md
  adr/                # numbered architecture decision records
  engineering/        # durable engineering & scientific rationale + milestones
  evidence/           # curated, path-sanitized reproducibility evidence
  research/           # dataset licensing / governance investigations
```

Decisions:

- **Keep the seven system-level normative docs flat at `docs/` root.** They are
  the declared public project documentation and function as the reader's entry
  set; nesting them under `architecture/` would misfile non-architecture docs
  (roadmap, requirements). This matches the retained set in the curation plan.
- **`docs/adr/`** — new folder; ADRs move out of the flat `docs/` root into a
  conventional numbered ADR log.
- **`docs/engineering/`** — the neutral home for public checkpoint-derived
  rationale and milestone summaries. Replaces the internal `docs/checkpoints/`.
- **`docs/evidence/`** and **`docs/research/`** — retained folders, contents
  renamed per §6 / §4.
- **`docs/architecture/` is NOT created.** Its intended content already lives in
  the flat `ARCHITECTURE.md` plus `docs/engineering/` architecture docs; a
  separate folder would fragment the small public set.
- **No `docs/checkpoints/` and no `docs/plans/` in public.** `docs/plans/`
  (this review, the two preparation plans, the portfolio implementation plan) is
  preparation/planning workflow and does not ship; the one public-candidate
  under `plans/` (portfolio UX architecture) is renamed into `engineering/`.

## 4. Rename / Relocation Mapping

Only PUBLIC and public-facing REVIEW_REQUIRED candidates receive a public name.
PRIVATE_ARCHIVE documents are intentionally absent (see §7). Mapping is
`current path -> public path`.

### 4.1 System-level normative docs (PUBLIC)

```text
docs/KALIBRA_FOUNDATION_v1.0.md              -> docs/FOUNDATION.md
docs/KALIBRA_ARCHITECTURE_v1.0.md            -> docs/ARCHITECTURE.md
docs/KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md     -> docs/SYSTEM_REQUIREMENTS.md
docs/KALIBRA_EVALUATION_METHODOLOGY_v1.0.md  -> docs/EVALUATION_METHODOLOGY.md
docs/KALIBRA_DATASET_STRATEGY_v1.0.md        -> docs/DATASET_STRATEGY.md
docs/KALIBRA_IMPLEMENTATION_ROADMAP_v1.0.md  -> docs/IMPLEMENTATION_ROADMAP.md
docs/KALIBRA_ENGINEERING_PLAN_v1.0.md        -> docs/ENGINEERING_PLAN.md
```

### 4.2 Phase-closure milestones (PUBLIC) -> `docs/engineering/`

```text
docs/KALIBRA_ARCHITECTURE_PHASE_1_CLOSURE_v1.0.md
  -> docs/engineering/ARCHITECTURE_FOUNDATION_MILESTONE.md
docs/KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md
  -> docs/engineering/DETERMINISTIC_RUNTIME_MILESTONE.md
docs/KALIBRA_ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE_v1.0.md
  -> docs/engineering/LOCAL_PROVIDER_PATH_MILESTONE.md
```

### 4.3 Public checkpoint-derived rationale (PUBLIC) -> `docs/engineering/`

```text
docs/checkpoints/KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md
  -> docs/engineering/DATASET_SELECTION_RATIONALE.md
docs/checkpoints/KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md
  -> docs/engineering/EVALUATION_PROTOCOL.md
docs/checkpoints/KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md
  -> docs/engineering/VISA_ACQUISITION_AND_GOVERNANCE.md
docs/checkpoints/KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md
  -> docs/engineering/ML_ARCHITECTURE_AND_CAPABILITY.md
docs/checkpoints/KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md
  -> docs/engineering/RUNTIME_INTEGRATION_ARCHITECTURE.md
docs/checkpoints/KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md
  -> docs/engineering/MODEL_FAMILY_SELECTION.md
```

(Six PUBLIC checkpoints. The curation plan's PUBLIC count of "7" includes an
off-by-one; the six above are every checkpoint row marked PUBLIC in its §3 and
match the six `engineering/` entries in its §8 tree.)

### 4.4 ADRs (REVIEW_REQUIRED -> public after link sanitization) -> `docs/adr/`

Numbered by decision chronology (dataset selection preceded framework
selection):

```text
docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md
  -> docs/adr/001-dataset-selection.md
docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md
  -> docs/adr/002-ml-inference-framework.md
```

### 4.5 REVIEW_REQUIRED closure/eval docs -> optional public summaries

These publish **only if** the owner chooses "split into public summary" over
"archive-only" during sanitization (curation plan §6, §10). If split, use:

```text
docs/checkpoints/KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md
  -> docs/engineering/SCIENTIFIC_EVALUATION_SUMMARY.md
docs/checkpoints/KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md
  -> docs/engineering/ML_CAPABILITY_MILESTONE.md
docs/checkpoints/KALIBRA_ML_PHASE_3_CLOSURE_REVIEW_v1.0.md
  -> docs/engineering/RUNTIME_INTEGRATION_MILESTONE.md
docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_CLOSURE_REVIEW_v1.0.md
  -> docs/engineering/PORTFOLIO_COMMUNICATION_NOTES.md
```

If the owner chooses archive-only for any of these, it receives **no** public
name and the mapping row is dropped.

### 4.6 Portfolio UX architecture (REVIEW_REQUIRED -> public candidate)

```text
docs/plans/KALIBRA_PORTFOLIO_UX_ARCHITECTURE_v1.0.md
  -> docs/engineering/PORTFOLIO_UX_ARCHITECTURE.md   # after recruiter/Werkstudent framing is sanitized
```

### 4.7 Documents intentionally NOT renamed (no public name)

PRIVATE_ARCHIVE per the two prior plans — kept in the private archive under
their **original** names for 1:1 traceability, never in the public tree:

- all remaining `docs/checkpoints/*` (the 22 PRIVATE_ARCHIVE + any
  REVIEW_REQUIRED resolved as archive-only);
- `docs/plans/PORTFOLIO_EXPERIENCE_IMPLEMENTATION_PLAN_v1.0.md`;
- `docs/plans/KALIBRA_PUBLIC_GITHUB_PREPARATION_PLAN_v1.0.md`,
  `docs/plans/KALIBRA_CHECKPOINT_ADR_PUBLIC_CURATION_PLAN_v1.0.md`, and this
  review (`..._ENGINEERING_DOCUMENTATION_NAMING_REVIEW_v1.0.md`) — preparation
  workflow;
- `docs/KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md`,
  `docs/KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md`,
  `docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`,
  `docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`,
  `docs/KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md`,
  `docs/KALIBRA_CLAUDE_DESIGN_BRIEF_v1.0.md`,
  `docs/KALIBRA_NEXT_IMPLEMENTATION_SLICE_RECOMMENDATION_v1.0.md`,
  and every top-level `*_IMPLEMENTATION_PLAN` / `*_BASELINE_PLAN` /
  `*_INTEGRATION_PLAN` / `*_SUBSTRATE_*` doc (ML-phase internals).

Two documents are **not classified by either prior plan** and are flagged here
as REVIEW_REQUIRED for the owner to rule on before sanitization; proposed public
names if kept:

```text
docs/KALIBRA_INDUSTRIAL_DATASET_LANDSCAPE_v1.0.md
  -> docs/research/INDUSTRIAL_DATASET_LANDSCAPE.md   # if kept public (research)
docs/KALIBRA_DOMAIN_PLANS_INDEX_v1.0.md
  -> (recommend PRIVATE_ARCHIVE; it indexes internal per-domain plans)
```

## 5. ADR Naming (decision + justification)

- **Convention:** `docs/adr/NNN-topic.md`, zero-padded 3-digit sequence,
  lowercase kebab topic. This is the widely recognised ADR log form and reads
  correctly to any external engineer.
- **Numbering:** chronological by when the decision was made, independent of the
  old `ML_PHASE_2` grouping. `001` dataset selection, `002` ML inference
  framework. New ADRs append (`003-…`); numbers are never reused.
- **Dropped tokens:** `KALIBRA_`, `ML_PHASE_2_`, `_ADR`, `_v1.0`. The `adr/`
  folder and the number carry the "this is an ADR" signal.
- **Body requirement (sanitization, not naming):** both ADRs currently link to
  `AGENTS.md` and internal authorization/implementation docs (curation plan §4).
  Those links must be rewritten to public targets or removed; the decision,
  criteria, risks, and non-claims must be preserved unchanged. This is flagged
  here because it is the gating dependency for the ADRs receiving their public
  names.

### `ENGINEERING_PLAN.md` — the one retained `PLAN` token

`PLAN` is a forbidden token *as a per-slice workflow suffix*
(`*_IMPLEMENTATION_PLAN`, `*_BASELINE_PLAN`). The single top-level
`ENGINEERING_PLAN` is a **normative product document** declared public by
AGENTS.md, not a workflow artifact. It is retained as `docs/ENGINEERING_PLAN.md`.
Acceptable alternative if the owner wants zero ambiguity:
`docs/ENGINEERING_OVERVIEW.md`. Recommendation: keep `ENGINEERING_PLAN.md`.

## 6. Evidence Naming (decision)

**Decision: rename in place; keep the current curated set grouped under
`docs/evidence/`. Do not summarize and do not merge** — evidence value is in the
specifics (hashes, metrics, provenance), which a summary would erase.

Renaming rule: drop `KALIBRA_`, `_EVIDENCE` (folder implies it), `_v1.0`, and any
internal sprint label; keep product/domain terms.

```text
docs/evidence/KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md
  -> docs/evidence/VISA_ACQUISITION.md
docs/evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md
  -> docs/evidence/PADIM_BASELINE_TRAINING.md
docs/evidence/KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md
  -> docs/evidence/PADIM_INFERENCE.md
docs/evidence/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md
  -> docs/evidence/PADIM_ONNX_EXPORT.md
docs/evidence/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md
  -> docs/evidence/PADIM_ONNX_EQUIVALENCE.md
docs/evidence/KALIBRA_REAL_ONNX_RUNTIME_EVIDENCE_SPRINT_1F_v1.0.md
  -> docs/evidence/ONNX_RUNTIME.md                 # also path-sanitize (embeds /Users/…)
docs/evidence/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_EVIDENCE_v1.0.md
  -> docs/evidence/RUNTIME_PROVIDER_INTEGRATION.md
docs/evidence/KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_EVIDENCE_v1.0.md
  -> docs/evidence/RUNTIME_EQUIVALENCE.md
docs/evidence/KALIBRA_PLACEHOLDER_RETIREMENT_EVIDENCE_v1.0.md
  -> docs/evidence/PLACEHOLDER_RETIREMENT.md
docs/evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md
  -> docs/evidence/SCIENTIFIC_EVALUATION.md
docs/evidence/prototype-ui/*.png
  -> docs/evidence/prototype-ui/*.png              # keep; filenames already neutral
```

Which of the 10 evidence docs are actually published is the curation subset
decision from the public-preparation plan (§2); this section governs their names
if kept. The path-sanitization of `ONNX_RUNTIME.md` is a content action for
sanitization, noted here only because the rename and the sanitize touch the same
file.

## 7. Closure / Milestone Naming (decision)

How ML Phase 2 / ML Phase 3 / Portfolio closure content is represented publicly:

- **PUBLIC phase-closure docs** (`ARCHITECTURE_PHASE_1_CLOSURE`,
  `ENGINEERING_PHASE_2_CLOSURE`, `ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE`) →
  **public milestone docs** with topic-first names in `docs/engineering/`
  (§4.2). The word `CLOSURE` and the phase index are dropped; "milestone"
  conveys the durable meaning without workflow vocabulary.
- **REVIEW_REQUIRED closure reviews** (ML Phase 2 / ML Phase 3 / Portfolio) →
  **sanitized public summaries** named per §4.5, **or archive-only**. Chosen
  representation:
  - ML Phase 2 closure review → `ML_CAPABILITY_MILESTONE.md` (recommended:
    split a public capability/scientific-debt/non-claims summary; archive the
    original review record).
  - ML Phase 3 closure review → `RUNTIME_INTEGRATION_MILESTONE.md` (recommended:
    split; this is one of the strongest public artifacts — runtime maturity,
    equivalence, placeholder retirement, non-claims).
  - Portfolio experience closure review → `PORTFOLIO_COMMUNICATION_NOTES.md`
    (recommended: archive-only unless the owner wants a public communication
    summary; the portfolio, README, tests, and evidence already carry the public
    value).
  - C6 scientific evaluation completion → `SCIENTIFIC_EVALUATION_SUMMARY.md`
    (recommended: split the bounded scientific claims/non-claims; archive the
    implementation-review original).

Principle: publish the durable *result* (rationale, metrics, non-claims) under a
milestone/summary name; archive the *process* (authorization gates, PASS/FAIL
iterations, commit decisions) under its original name. No `CLOSURE`, `REVIEW`,
`REREVIEW`, or `COMPLETION` token survives into a public filename.

## 8. README / Link Impact

Verified against the current tree (read-only grep). Impact on the public set is
**LOW**:

- **`README.md`** references documentation only generically — line 143
  (`` `docs/` - public foundation, architecture, requirements, methodology,
  roadmap, … ``) and line 147 (`` `README.md` … ``). It links to **no
  individual `docs/*` filename**, so the §4 renames do not break README. README
  must still be re-verified during sanitization (prep plan classifies it
  REVIEW_REQUIRED), but not for these renames.
- **`portfolio/README.md`** contains no `docs/` links — no impact.
- **Public engineering cross-links to fix:** the two ADRs (§5) link to
  `AGENTS.md` and internal docs; those links must be rewritten when the ADRs are
  renamed into `docs/adr/`. This is the only mandatory public-set link update
  from renaming.
- **Cross-links that do NOT need fixing for the public set** (their source docs
  are PRIVATE_ARCHIVE, so they never ship):
  - `docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md:15,23` → C2 checkpoint,
    FRAMEWORK_ADR.
  - `docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md:21,360` → C3 checkpoint,
    FRAMEWORK_ADR.
  - `docs/KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md` (many) →
    FRAMEWORK_ADR.
  - `docs/KALIBRA_INDUSTRIAL_DATASET_LANDSCAPE_v1.0.md:585` → DATASET_SELECTION_ADR
    (only relevant if this doc is kept public per §4.7; if kept, update the
    reference to `docs/adr/001-dataset-selection.md`).
- **Prototype-ui image links** inside public docs
  (`docs/evidence/prototype-ui/`) are unaffected — that path and its filenames
  are retained unchanged.

No link is updated by this review. Updates happen during sanitization.

## 9. Migration Guidance (for the sanitization step — no execution here)

Codex should apply these names during sanitization, after the private archive
exists, in this order:

1. **Archive-before-rename.** Confirm the private archive and its
   `git bundle --all` + `MANIFEST.md` (path + sha256) exist per the
   public-preparation plan §3/§7 before touching any public filename.
2. **Freeze the mapping.** Treat §4 as the execution manifest
   (`current path -> public path`). For each PUBLIC and owner-approved
   REVIEW_REQUIRED row, record original path, public path, and sha256.
3. **Create folders** `docs/adr/` and `docs/engineering/`; do **not** create
   `docs/architecture/`.
4. **Rename PUBLIC docs** (§4.1–4.3) to their public paths, preserving content
   and claims verbatim (renames only; content sanitization is a separate,
   already-planned step).
5. **Resolve REVIEW_REQUIRED before naming:** ADRs — rewrite internal links
   (§5) then place as `docs/adr/001…`, `002…`. Closure reviews / C6 — per
   owner's split-vs-archive choice (§7); only split outputs get the §4.5 names.
6. **Rename evidence** (§6) and **research** (§4.7) docs; path-sanitize
   `ONNX_RUNTIME.md`.
7. **Do not publish** `docs/checkpoints/` or `docs/plans/`. Everything in §4.7
   keeps its original name in the private archive only.
8. **Update links:** rewrite the two ADRs' internal links; if
   `INDUSTRIAL_DATASET_LANDSCAPE` is kept, update its ADR reference. Re-run the
   broken-link and workflow-term scans from the preparation plan §8 on the
   public set.

Constraint: renaming must never alter a document's claims, non-claims, metrics,
or provenance. Naming is cosmetic-plus-taxonomy only.

## 10. Decision

```text
NAMING READY FOR SANITIZATION
```

The public naming scheme is fully specified: principles (§2), taxonomy (§3),
exact mappings for every PUBLIC and public-candidate document (§4), ADR
convention (§5), evidence rule (§6), milestone/closure rule (§7), and link
impact (§8). Two unclassified docs (§4.7) are flagged for an owner ruling but do
not block the scheme. Content sanitization (link rewrites, path sanitization,
split-vs-archive of REVIEW_REQUIRED files) remains a separate authorized step.

## 11. Validation

Commands run for this review (read-only):

```bash
find docs -maxdepth 3 -type f | sort
git status --short
```

The only file created by this step is this review document.

## 12. Next Natural Step

Review this Engineering Documentation Naming Review before authorizing private
archive creation and public repository sanitization.
