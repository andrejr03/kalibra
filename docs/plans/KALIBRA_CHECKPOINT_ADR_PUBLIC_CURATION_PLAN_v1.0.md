# Kalibra Checkpoint and ADR Public Curation Plan v1.0

**Status:** Plan only. No file move, deletion, archival, sanitization, commit, or
push is authorized by this document.
**Date:** 2026-07-08
**Repository:** `/Users/agentisstudio/Documents/kalibra`
**Private archive destination:** `/Users/agentisstudio/Documents/andre-projects/kalibra-private/`

## 0. Purpose and Boundary

This plan curates Kalibra documents that sit between obviously public system
documentation and obviously private internal workflow history.

The reviewed scope is:

- all files in `docs/checkpoints/`;
- all ADR files found under `docs/`;
- adjacent architecture-decision, closure, implementation-review, and
  authorization documents outside `docs/checkpoints/` where the filename or
  document role puts them in the same curation problem.

This plan makes recommendations only. It creates no migration, archive, rewrite,
or public sanitization.

## 1. Classification Rules

Each reviewed document is classified as exactly one of:

- **PUBLIC**: keep in the public repository because it records durable
  architectural rationale, scientific rationale, important engineering
  decisions, system evolution, or repository understanding that improves public
  technical credibility.
- **PRIVATE_ARCHIVE**: move to the private archive during sanitization because it
  mainly records authorization gates, implementation reviews, review iterations,
  PASS/FAIL workflow, internal planning, prompt-driven workflow, AI-agent
  workflow, publication preparation, or migration planning.
- **REVIEW_REQUIRED**: do not publish as-is and do not archive blindly. The
  document mixes valuable engineering with internal workflow. During
  sanitization, either keep after sanitization, archive, split, or replace with a
  public derivative.

## 2. Inventory

Observed inventory:

- `docs/checkpoints/`: 33 files.
- ADRs by filename: 2 files.
- Adjacent closure / authorization / decision documents outside
  `docs/checkpoints/`: 5 files.

Total documents classified by this plan: 40.

## 3. Checkpoint Classification

| Document | Classification | Recommendation | Rationale |
| --- | --- | --- | --- |
| `docs/checkpoints/KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Durable dataset-selection rationale. Explains VisA as governed proxy and MPDD as domain anchor, with explicit limitations and non-claims. |
| `docs/checkpoints/KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Durable scientific protocol decision. Separates metrics, operating point, statistical protocol, failure analysis, allowed claims, and prohibited claims. |
| `docs/checkpoints/KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Publicly useful reproducibility and governance rationale for acquisition, provenance, integrity, layout, and failure policy. |
| `docs/checkpoints/KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive original. | Engineering-completion review with git/storage assessment, validation summary, and implementation-history detail. Public claims should rely on curated evidence docs instead. |
| `docs/checkpoints/KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive original. | Implementation-completion review, including review findings, required changes, local artifact/storage details, and commit authorization. |
| `docs/checkpoints/KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md` | REVIEW_REQUIRED | Split or sanitize. | Contains valuable bounded scientific claims and prohibited claims, but also implementation-review findings, git/storage assessment, and commit authorization. Keep the public scientific summary only; archive the original review record. |
| `docs/checkpoints/KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Bounded implementation-authorization checkpoint. It is useful internally but exposes execution gating workflow rather than public engineering rationale. |
| `docs/checkpoints/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for a specific implementation slice. |
| `docs/checkpoints/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation-review completion checkpoint with findings, validation, storage assessment, and commit decision. |
| `docs/checkpoints/KALIBRA_GOVERNED_VISA_ACQUISITION_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization checkpoint for future acquisition implementation. |
| `docs/checkpoints/KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Internal capability roadmap checkpoint. Its durable content is superseded by later strategy, ADR, and closure documents. |
| `docs/checkpoints/KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Concise architecture/capability state checkpoint. It records maturity, remaining gaps, infrastructure completion, and readiness without implementation-review detail. |
| `docs/checkpoints/KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md` | REVIEW_REQUIRED | Sanitize or split. | Increases public technical quality by explaining achieved capability, scientific debt, architecture assessment, and non-claims. It also contains authorization/checkpoint workflow lessons and review-process framing. |
| `docs/checkpoints/KALIBRA_ML_PHASE_2_DOCUMENTATION_CONSOLIDATION_REVIEW_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Repository-governance review about documentation consolidation and archival candidates. It is internal curation history. |
| `docs/checkpoints/KALIBRA_ML_PHASE_3_CLOSURE_REVIEW_v1.0.md` | REVIEW_REQUIRED | Sanitize or split. | Increases public technical quality by documenting runtime maturity, equivalence, placeholder retirement, remaining debt, and non-claims. It also contains authorization workflow and checkpoint-persistence discussion. |
| `docs/checkpoints/KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Durable phase-opening architecture review. Records runtime gap, architectural delta, integration risks, ordering, success criteria, and non-claims. |
| `docs/checkpoints/KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for training implementation. |
| `docs/checkpoints/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for export-equivalence verification. |
| `docs/checkpoints/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation-review completion checkpoint with validation and commit decision. |
| `docs/checkpoints/KALIBRA_PLACEHOLDER_RETIREMENT_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for placeholder retirement. |
| `docs/checkpoints/KALIBRA_PLACEHOLDER_RETIREMENT_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Completion review for a specific implementation slice. Public readers only need the resulting runtime/evidence docs. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_CLOSURE_REVIEW_v1.0.md` | REVIEW_REQUIRED | Sanitize or split. | May contain public value similar to the ML Phase 2 and ML Phase 3 closure reviews because it assesses whether the recruiter-facing experience communicates Kalibra's engineering truthfully. Do not publish as-is; archive the original before any sanitized public summary or replacement. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation completion record for the portfolio surface. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_FINAL_REREVIEW_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Final re-review and PASS workflow record. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_REREVIEW_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Re-review and FAIL workflow record. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_REVIEW_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation review and FAIL workflow record. |
| `docs/checkpoints/KALIBRA_PORTFOLIO_UX_STACK_AND_PROTOTYPE_REVIEW_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Internal portfolio/UX planning and recruiter-facing strategy. Public value belongs in the finished portfolio, not the planning review. |
| `docs/checkpoints/KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for runtime equivalence verification. |
| `docs/checkpoints/KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation-review completion checkpoint with validation, storage assessment, and commit decision. |
| `docs/checkpoints/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for runtime provider integration. |
| `docs/checkpoints/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_COMPLETION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Implementation-review completion checkpoint. |
| `docs/checkpoints/KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Authorization planning for evaluation execution. |
| `docs/checkpoints/KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md` | PUBLIC | Keep. | Durable scientific architecture decision selecting PaDiM as first model family and naming risks/non-claims. |

Checkpoint counts:

- PUBLIC: 7
- PRIVATE_ARCHIVE: 22
- REVIEW_REQUIRED: 4

## 4. ADR Review

| Document | Classification | Recommendation | Rationale |
| --- | --- | --- | --- |
| `docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md` | REVIEW_REQUIRED | Keep public after link/scope sanitization, or publish a sanitized successor and archive the original. | The ADR strongly improves public engineering credibility: it records candidate criteria, license/provenance reasoning, the bounded `SELECTED - VisA` decision, MPDD's domain-anchor role, and explicit non-claims. It also links to `AGENTS.md` and internal implementation/authorization documents that are likely private after sanitization. |
| `docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md` | REVIEW_REQUIRED | Keep public after link/scope sanitization, or publish a sanitized successor and archive the original. | The ADR strongly improves public engineering credibility: it records framework candidates, decision drivers, architecture compatibility rules, risks, and ONNX Runtime selection boundaries. It also contains implementation-authorization language and internal workflow references. |

ADR conclusion:

Both ADRs should remain part of the public engineering narrative, but the current
files should not be treated as publish-ready until internal links and workflow
references are resolved. Sanitization must preserve the decisions and non-claims;
it must not soften the engineering constraints.

## 5. Adjacent Closure, Authorization, and Decision Documents

| Document | Classification | Recommendation | Rationale |
| --- | --- | --- | --- |
| `docs/KALIBRA_ARCHITECTURE_PHASE_1_CLOSURE_v1.0.md` | PUBLIC | Keep. | Durable milestone record for architecture/substrate readiness. It improves public understanding without exposing implementation-review workflow. |
| `docs/KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md` | PUBLIC | Keep. | Durable milestone record for deterministic runtime completion across the five domains. It improves public understanding and claim boundaries. |
| `docs/KALIBRA_ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE_v1.0.md` | PUBLIC | Keep. | Durable milestone record for the first local-provider path and its non-claims. It strengthens the public story of provider-boundary discipline. |
| `docs/KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Large implementation authorization document with sprint gates and owner-authorization workflow. Not public-facing. |
| `docs/KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md` | PRIVATE_ARCHIVE | Archive. | Internal decision memo now superseded by the Dataset Selection ADR's `SELECTED - VisA` decision and later checkpoints. |

## 6. Closure Review Findings

### ML Phase 2 Closure Review

Classification: **REVIEW_REQUIRED**.

This review increases the technical quality of the public repository if curated.
It explains what ML Phase 2 actually demonstrated, what remains scientific debt,
and which claims are still prohibited. That is valuable for recruiters because
it shows engineering maturity and honest claim boundaries.

It should not be published as-is because it also records internal checkpoint
workflow, authorization workflow, and review-process lessons. During
sanitization, split it into a public "ML Phase 2 Milestone Summary" or remove
the internal workflow sections and archive the original.

### ML Phase 3 Closure Review

Classification: **REVIEW_REQUIRED**.

This review increases public technical quality if curated. It explains the
runtime's current maturity, real ONNX-backed path, runtime equivalence,
placeholder retirement, remaining debt, and explicit non-claims. It is one of
the strongest artifacts for showing that Kalibra distinguishes working runtime
evidence from unsupported trust claims.

It should not be published as-is because it contains authorization-workflow and
checkpoint-persistence discussion. During sanitization, split or sanitize it and
archive the original.

### Portfolio Experience Closure Review

Classification: **REVIEW_REQUIRED**.

This review may increase public repository quality if curated. It evaluates
whether the recruiter-facing experience communicates the engineering truthfully,
keeps unsupported claims out of the portfolio surface, and connects public
presentation back to evidence.

It should not be published as-is because it remains a closure review with
internal workflow and portfolio-process framing. During sanitization, split it
into a public portfolio communication summary, sanitize it in place after
archiving the original, or archive it without replacement if the portfolio,
README, tests, and evidence bundle already carry the public value.

## 7. Public Engineering Narrative

Keeping selected ADRs and closure/milestone documents improves the public
engineering narrative in three ways:

1. **Engineering credibility.** The ADRs and selected engineering decision
   documents show that dataset, framework, model-family, evaluation-protocol,
   and runtime integration choices were made through explicit criteria rather
   than convenience.
2. **Repository quality.** Public readers can see how Kalibra preserves
   evidence-before-assertion, non-claims, reproducibility, and domain boundaries
   across major decisions.
3. **Recruiter understanding.** Curated milestone records help technical
   reviewers understand the build sequence: architecture foundation,
   deterministic runtime, local-provider boundary, governed dataset selection,
   model-family selection, evaluation protocol, and runtime integration.

The public narrative is weakened, not strengthened, by raw authorization gates,
implementation reviews, FAIL/PASS iterations, commit decisions, and publication
preparation. Those belong in the private archive.

## 8. Final Recommended Public Documentation Tree

This tree shows the recommended public documentation set after sanitization.
Files marked `REVIEW_REQUIRED` above appear here only after their internal
workflow references have been resolved.

The public repository should not expose a `docs/checkpoints/` folder.
`checkpoint` is internal workflow language. Selected public checkpoint documents
should become engineering or milestone documentation with reader-facing
filenames in a neutral external-facing area such as `docs/engineering/`.
Original checkpoint files must be archived before any rename, rewrite, or
sanitization.

```text
docs/
  KALIBRA_FOUNDATION_v1.0.md
  KALIBRA_ARCHITECTURE_v1.0.md
  KALIBRA_EVALUATION_METHODOLOGY_v1.0.md
  KALIBRA_DATASET_STRATEGY_v1.0.md
  KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md
  KALIBRA_IMPLEMENTATION_ROADMAP_v1.0.md
  KALIBRA_ENGINEERING_PLAN_v1.0.md
  KALIBRA_ARCHITECTURE_PHASE_1_CLOSURE_v1.0.md
  KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md
  KALIBRA_ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE_v1.0.md
  KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md        # after REVIEW_REQUIRED resolution
  KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md                 # after REVIEW_REQUIRED resolution
  engineering/
    DATASET_SELECTION_RATIONALE.md
    EVALUATION_PROTOCOL.md
    GOVERNED_VISA_ACQUISITION.md
    MODEL_FAMILY_SELECTION.md
    ML_PHASE_2_ARCHITECTURE_CAPABILITY.md
    ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE.md
  evidence/
    # curated evidence set from the broader public-preparation plan
  research/
    # curated dataset-governance research set from the broader public-preparation plan
```

Recommended optional public derivatives, not created by this plan:

```text
docs/KALIBRA_ML_PHASE_2_MILESTONE_SUMMARY_v1.0.md
docs/KALIBRA_ML_PHASE_3_RUNTIME_MILESTONE_SUMMARY_v1.0.md
docs/KALIBRA_C6_SCIENTIFIC_EVALUATION_SUMMARY_v1.0.md
docs/KALIBRA_PORTFOLIO_EXPERIENCE_COMMUNICATION_SUMMARY_v1.0.md
```

These derivatives should exist only if the repository owner chooses split over
in-place sanitization for the four REVIEW_REQUIRED checkpoint/closure files.

## 9. Final Private Archive Set

During sanitization, archive these files under the private archive destination
before any public-tree removal or rewrite.

```text
kalibra-private/
  docs/
    checkpoints/
      KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_GOVERNED_VISA_ACQUISITION_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md
      KALIBRA_ML_PHASE_2_DOCUMENTATION_CONSOLIDATION_REVIEW_v1.0.md
      KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_PLACEHOLDER_RETIREMENT_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_PLACEHOLDER_RETIREMENT_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_FINAL_REREVIEW_v1.0.md
      KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_REREVIEW_v1.0.md
      KALIBRA_PORTFOLIO_EXPERIENCE_IMPLEMENTATION_REVIEW_v1.0.md
      KALIBRA_PORTFOLIO_UX_STACK_AND_PROTOTYPE_REVIEW_v1.0.md
      KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_RUNTIME_PROVIDER_INTEGRATION_AUTHORIZATION_CHECKPOINT_v1.0.md
      KALIBRA_RUNTIME_PROVIDER_INTEGRATION_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md
    review-required-originals/
      KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md
      KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md
      KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md
      KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md
      KALIBRA_ML_PHASE_3_CLOSURE_REVIEW_v1.0.md
      KALIBRA_PORTFOLIO_EXPERIENCE_CLOSURE_REVIEW_v1.0.md
    authorization/
      KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md
    memos/
      KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md
```

If a REVIEW_REQUIRED file is sanitized in place rather than split into a public
derivative, archive the original pre-sanitization bytes first and record its
sha256 in the private archive manifest.

## 10. Migration Recommendation

During repository sanitization, execute this curation in the following order:

1. Archive first: copy every PRIVATE_ARCHIVE file and every REVIEW_REQUIRED
   original into the private archive and record original path, archive path, and
   sha256.
2. Keep PUBLIC files in the public tree without changing their claims, but do
   not publish a `docs/checkpoints/` folder. Archive original checkpoint files
   before renaming selected public checkpoint content into `docs/engineering/`
   or another neutral reader-facing folder.
3. Resolve the two ADRs by removing or replacing links to private-only workflow
   documents while preserving the decision, criteria, risks, and non-claims.
4. Resolve the four REVIEW_REQUIRED checkpoint/closure files by one of these
   owner-approved paths:
   - split public milestone summaries from private originals;
   - sanitize the originals in place after archiving their pre-sanitization
     bytes;
   - archive them without public replacement if the owner decides the remaining
     public tree is sufficient.
5. Remove PRIVATE_ARCHIVE files from the public working set only after archive
   integrity is verified.
6. Re-run public-boundary scans and link checks from the broader Public GitHub
   Preparation Plan.

No migration should publish authorization checkpoints, implementation reviews,
PASS/FAIL review iterations, commit decisions, or publication-preparation
history.

## 11. Validation Commands for This Plan

Required read-only validation commands:

```bash
find docs/checkpoints -type f | sort
find docs -maxdepth 2 -iname "*ADR*" -o -iname "*adr*" | sort
git status --short
```

This document itself is the only file created by this planning step.

## 12. Next Natural Step

Review the Checkpoint and ADR Public Curation Plan before authorizing repository
sanitization.
