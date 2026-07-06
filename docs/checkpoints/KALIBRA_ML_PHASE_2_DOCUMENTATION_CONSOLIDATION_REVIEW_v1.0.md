# Kalibra ML Phase 2 Documentation Consolidation Review v1.0

**Status:** Recorded — repository-governance review (review only; no implementation, no document modification, no file move, no archival, no deletion, no authorization)
**Date:** 2026-07-06
**Repository baseline HEAD:** `c4a78ec docs: close ml phase 2`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **ML Phase 2 Documentation Consolidation Review** as a
versioned checkpoint. It is a repository-governance review only. It determines which ML
Phase 2 documents become permanent, historical, absorbed, or archived.

It **performs no implementation** (no source, test, or script change). It **modifies no
documentation** (no ADR, Strategy, Authorization, checkpoint, or evidence edit). It
**authorizes nothing** (no Phase 3 work, no archival action, no public release). It
**moves, archives, and deletes nothing** — it only classifies and recommends.

It draws its standing from the full ML Phase 2 lineage and the `AGENTS.md` checkpoint
convention, including the
[ML Phase 2 Closure Review](KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md) that closed the
phase. The classification definitions (PERMANENT / HISTORICAL / ABSORBED) are taken from
the task brief and applied uniformly.

---

## 1. Documentation Inventory

The complete ML Phase 2 document corpus is grouped below. Pre-ML-Phase-2 foundational,
architecture, domain-plan, and ML Phase 1 documents are listed in §1.7 for completeness
but are **out of scope** for this consolidation review (they were not created during ML
Phase 2 and are not candidates for ML Phase 2 archival). Counts: **63** markdown documents
total; **27** are in ML Phase 2 scope.

### 1.1 Foundations (in scope — referenced/updated by ML Phase 2)

| Document | Created | Role |
| --- | --- | --- |
| `AGENTS.md` (root) | pre-Phase-2 | Workflow + binding rules; **updated** in ML Phase 2 (`789b57e docs: require engineering knowledge persistence`) to add the checkpoint-persistence workflow |
| `README.md` (root) | pre-Phase-2 | Public project entry |

### 1.2 ADRs (in scope)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md` | `ad3a8ae` | Records `SELECTED — VisA`; the dataset-selection decision |
| `KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md` | `b684ab7` | Records ONNX Runtime as the selected runtime candidate |

### 1.3 Strategies (in scope)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md` | `448a065` | Scientific direction; anomaly-detection-first scope |
| `KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md` | `da307c1` | Dataset evidence requirements + governed acquisition rules for VisA |
| `KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md` | `7e8cc39` (created), `769f933` (C-2 incorporated) | Standard of proof; first VisA + PaDiM protocol |
| `KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md` | `0a01d38` | Pre-selection dataset posture (DEFER) |

### 1.4 Authorization documents (in scope)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md` | `b5ddd80` | Final governance gate; Sprint 1x restricted authorizations |
| `KALIBRA_GOVERNED_VISA_ACQUISITION_AUTHORIZATION_CHECKPOINT_v1.0.md` | `c117bfa` | C-3 acquisition authorization |
| `KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md` | `3f728e3` | C-4 training authorization |
| `KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md` | `9148e93` | C-5 inference authorization |
| `KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md` | `9684d05` | C-6 evaluation authorization |

### 1.5 Checkpoints (in scope)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md` | `1b723e1` | Infrastructure-complete assessment; substrate closed |
| `KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md` | `1b723e1` | C-1…C-8 capability roadmap |
| `KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md` | `1b723e1` | PaDiM first; PatchCore reserved |
| `KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md` | `6f24597` | VisA selected (DEFER → SELECTED) |
| `KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md` | `94e589c` | First evaluation protocol fixed |
| `KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md` | `8d069ba` | Acquisition protocol defined |
| `KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md` | `e0ef4b6` | Training PASS |
| `KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md` | `300b808` | Inference PASS |
| `KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md` | `4036d63` | Evaluation PASS |
| `KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md` | `c4a78ec` | Phase closure decision |

### 1.6 Evidence (in scope)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md` | `548a436` | C-3 acquisition evidence (archive/manifest/provenance/splits) |
| `KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md` | `e0ef4b6` | C-4 training evidence (μ/Σ⁻¹/feature indices) |
| `KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md` | `300b808` | C-5 inference evidence (6492 inputs) |
| `KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md` | `4036d63` | C-6 evaluation evidence (per-class VisA metrics) |
| `KALIBRA_REAL_ONNX_RUNTIME_EVIDENCE_SPRINT_1F_v1.0.md` | `e50b84a` | Real-runtime corroboration (Sprint 1F; pre-capability) |

### 1.7 Research (in scope — inputs to dataset selection)

| Document | Created | Role |
| --- | --- | --- |
| `KALIBRA_VISA_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md` | ML Phase 2 | VisA governance evidence for the ADR |
| `KALIBRA_MPDD_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md` | ML Phase 2 | MPDD governance evidence (deferred candidate) |
| `KALIBRA_MPDD_VERSIONING_AND_ARCHIVAL_INVESTIGATION_v1.0.md` | ML Phase 2 | MPDD versioning evidence (deferred candidate) |
| `KALIBRA_INDUSTRIAL_DATASET_LANDSCAPE_v1.0.md` | `84efc93` (pre-Phase-2-planning, consumed by Phase 2) | Public dataset survey feeding the ADR |

### 1.8 Out-of-scope (pre-ML-Phase-2; listed for completeness, not classified)

Foundations: `KALIBRA_FOUNDATION_v1.0.md`, `KALIBRA_ARCHITECTURE_v1.0.md`,
`KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md`, `KALIBRA_ENGINEERING_PLAN_v1.0.md`,
`KALIBRA_IMPLEMENTATION_ROADMAP_v1.0.md`, `KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`,
`KALIBRA_DATASET_STRATEGY_v1.0.md`, `KALIBRA_CLAUDE_DESIGN_BRIEF_v1.0.md`. Phase-1 / domain
plans and closures: the five engine implementation plans, the five real-baseline plans,
`KALIBRA_DOMAIN_PLANS_INDEX_v1.0.md`, the ML Phase 1 plan/closure docs, the asset-pipeline
docs, the substrate/CLI docs, `KALIBRA_ARCHITECTURE_PHASE_1_CLOSURE_v1.0.md`,
`KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md`,
`KALIBRA_NEXT_IMPLEMENTATION_SLICE_RECOMMENDATION_v1.0.md`,
`KALIBRA_PROTOTYPE_UI_LOCAL_PROVIDER_INTEGRATION_PLAN_v1.0.md`. These are **not** ML Phase 2
artefacts and are not archival candidates here; they belong to earlier phases and remain
permanent/historical on their own merits.

---

## 2. Document Classification

Each in-scope ML Phase 2 document is classified as exactly one of PERMANENT, HISTORICAL, or
ABSORBED.

### 2.1 PERMANENT — must remain in the main repository indefinitely

| Document | Why permanent |
| --- | --- |
| `AGENTS.md` | Source of truth for workflow + binding rules. |
| `KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md` | The dataset decision of record (`SELECTED — VisA`). ADRs are permanent. |
| `KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md` | The runtime decision of record (ONNX Runtime). ADRs are permanent. |
| `KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md` | Authoritative scientific direction; referenced as binding by every later strategy. |
| `KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md` | Authoritative dataset evidence requirements + VisA governed-acquisition rules. |
| `KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md` | Authoritative standard of proof; first VisA + PaDiM protocol; referenced by C-2/C-6. |

### 2.2 HISTORICAL — must remain because it preserves reasoning not fully reproducible elsewhere

| Document | Why historical |
| --- | --- |
| `KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md` | The "substrate complete, science is the binding constraint" decision that opened capability work. Not reproducible from the strategies alone. |
| `KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md` | The C-1…C-8 roadmap and its ordering rationale. Historical but **carries documented roadmap drift** (see §6.1). |
| `KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md` | PaDiM-vs-PatchCore selection reasoning, migration strategy, scientific risks. Not reproducible elsewhere. |
| `KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md` | DEFER → SELECTED reasoning; preserves why MPDD was held. |
| `KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md` | Metric/threshold/statistics choices that the C-6 evaluation executed. Load-bearing provenance. |
| `KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md` | Acquisition protocol design (source tiers, integrity policy, failure modes). |
| `KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md` | C-4 PASS record + observations (O-1/O-2/O-3) that influenced C-5/C-6. |
| `KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md` | C-5 PASS + the O-1 `predicted_judgement` contract-artifact reasoning that C-6 honored. |
| `KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md` | C-6 PASS; the bounded single-seed VisA proxy claim boundary of record. |
| `KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md` | The phase-closure decision and the carried-forward scientific debt. |
| `KALIBRA_GOVERNED_VISA_ACQUISITION_AUTHORIZATION_CHECKPOINT_v1.0.md` | Authorization reasoning for C-3. |
| `KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md` | Authorization reasoning for C-4. |
| `KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md` | Authorization reasoning for C-5. |
| `KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md` | Authorization reasoning for C-6. |
| `KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md` | Sprint 1x restricted-authorization record + the gate logic. **Historical but stale-as-current** (see §6.2); its status wording predates C-1…C-6. |
| `KALIBRA_VISA_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md` | Primary-source governance evidence behind the VisA selection. Not reproducible without re-doing the investigation. |
| `KALIBRA_MPDD_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md` | Why MPDD was held; preserves the deferred-candidate reasoning for future MPDD review. |
| `KALIBRA_MPDD_VERSIONING_AND_ARCHIVAL_INVESTIGATION_v1.0.md` | MPDD versioning blocker evidence; load-bearing for any future MPDD selection. |
| `KALIBRA_INDUSTRIAL_DATASET_LANDSCAPE_v1.0.md` | The full candidate survey; the ADR selects from it but does not reproduce it. |

### 2.3 ABSORBED — engineering content now completely represented elsewhere (archival candidates)

| Document | Why absorbed |
| --- | --- |
| `KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md` | Its recommendation ("keep selection deferred; VisA governance anchor; MPDD domain anchor") is **superseded** by the Dataset Selection ADR's `SELECTED — VisA`. Its candidate analysis is reproduced (and improved) by the research investigations + the ADR. It is the clearest absorption candidate in the corpus. |

### 2.4 Evidence classification (detailed in §4)

All five evidence documents are **PERMANENT** — they are the durable scientific/governance
records an untrusting observer verifies against, and they are not reproducible without
re-running the governed pipeline. The Sprint 1F runtime evidence is the weakest case
(pre-capability) but remains the only real-runtime corroboration record and stays permanent.

---

## 3. Checkpoint Review

For every checkpoint: useful / historically important / fully absorbed, with justification.

| Checkpoint | Verdict | Justification |
| --- | --- | --- |
| `ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY` | **Historically important** | The single document that declared the substrate complete and named the scientific gap as the binding constraint. It is the pivot between infrastructure and capability. Unique; not absorbed. |
| `ML_CAPABILITY_ENGINEERING_STRATEGY` | **Historically important (with drift)** | The C-1…C-8 roadmap and strict ordering rationale. Historically important, **but** its C-5/C-6/C-7/C-8 numbering drifted from execution (C-5/C-6 were repurposed; C-7/C-8 not executed as numbered). Must be retained but read alongside the Closure Review. |
| `SCIENTIFIC_MODEL_FAMILY_SELECTION` | **Historically important** | PaDiM selection reasoning + migration plan + 6 scientific risks. The only place this reasoning lives. Not absorbed. |
| `C1_DATASET_SELECTION_CLOSURE` | **Still useful** | Records the DEFER → SELECTED transition and the explicit VisA-as-proxy acceptance. Load-bearing for the dataset claim boundary. |
| `C2_EVALUATION_PROTOCOL_FIXATION` | **Still useful** | The protocol C-6 executed. Without it, the C-6 metric/threshold/statistics choices have no pre-registration provenance. |
| `C3_GOVERNED_VISA_ACQUISITION_STRATEGY` | **Still useful** | The acquisition protocol (source tiers, integrity, failure modes) that the acquisition sprint implemented. Referenced by C-4/C-5/C-6 verification. |
| `C4_PADIM_BASELINE_TRAINING_COMPLETION` | **Still useful** | C-4 PASS + the observations that shaped C-5/C-6 (e.g. the lighter `verify` posture, the artifact-hash convention). |
| `C5_GOVERNED_PADIM_INFERENCE_COMPLETION` | **Still useful** | C-5 PASS + O-1 (`predicted_judgement` contract artifact, not classification) that C-6 explicitly honored. |
| `C6_SCIENTIFIC_EVALUATION_COMPLETION` | **Still useful** | The current state-of-the-art completion record; defines the bounded single-seed VisA proxy claim boundary. |
| `ML_PHASE_2_CLOSURE_REVIEW` | **Still useful** | The phase-closure decision and carried-forward debt; the bridge to any Phase 3. |
| 4 × capability authorization checkpoints (C-3…C-6) | **Historically important** | Each fixes the authorized/forbidden scope of one phase. Retained as the authorization record; their content is summarized in the completion checkpoints but not fully reproduced. |

**No checkpoint is fully absorbed.** Each preserves reasoning (authorization scope,
protocol design, selection rationale, completion observations) not reproducible from the
strategies or evidence alone.

---

## 4. Evidence Review

| Evidence document | Verdict | Justification |
| --- | --- | --- |
| `KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md` | **Permanent** | Records the archive/manifest/provenance/split hashes that root every downstream verification. The integrity root of trust; not reproducible without re-acquiring. |
| `KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md` | **Permanent** | Records the C-4 artifact hashes (μ, Σ⁻¹, feature indices, seed) that C-5/C-6 consume as governed inputs. |
| `KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md` | **Permanent** | Records the C-5 inference identity and the per-input hash anchors (in `artifact_hashes.json`) that C-6 verifies. |
| `KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md` | **Permanent** | The recorded bounded single-seed VisA proxy metrics, operating point, failure analysis, and replay status. The scientific evidence of record. |
| `KALIBRA_REAL_ONNX_RUNTIME_EVIDENCE_SPRINT_1F_v1.0.md` | **Permanent** | The only real-runtime (not mocked) corroboration record. Pre-capability but still the runtime-reality evidence; not superseded by any later document. |

**No evidence is superseded or historical-only.** All five are the durable records an
untrusting observer uses; they anchor reproducibility and must remain permanent. (The C-6
evidence is the *current* scientific record; it will become historical only when a later
evaluation supersedes it, which has not happened.)

---

## 5. Repository Health

### 5.1 Documentation duplication — LOW

The corpus is well-factored. The strategies do not restate the ADRs; the checkpoints do not
restate the strategies; the evidence does not restate the checkpoints. Each layer has a
distinct job (decision / reasoning / proof). The one genuine duplication is the dataset
candidate analysis, which appears in three places: the Industrial Dataset Landscape
(survey), the three research investigations (primary-source depth), and the Data Strategy
Decision Memo (synthesis). The Memo is the redundant layer (§2.3).

### 5.2 Documentation drift — MODERATE (two real cases)

1. **Roadmap drift (highest-priority debt).** The
   `ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT` defines C-5 (ONNX Export), C-6 (Model
   Integration), C-7 (Real Evaluation Baseline), C-8 (Calibration). Execution repurposed
   C-5 → governed inference and C-6 → scientific evaluation, and C-7/C-8 were never
   executed as numbered. A reader following the roadmap checkpoint alone would expect
   runtime integration and calibration to have occurred; they have not (per the Closure
   Review). This is documented *in the Closure Review* but **not** in the roadmap checkpoint
   itself.
2. **Authorization-status drift.** The `ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION` still
   records its current status as "AUTHORIZED WITH RESTRICTIONS — Sprint 1H only / Full ML
   Phase 2 implementation remains DEFERRED" and its checklist as INCOMPLETE. The C-1…C-6
   capability phases were authorized *separately* (under their own authorization
   checkpoints) and the dataset/framework/evaluation gates the Implementation Authorization
   named as unmet were subsequently closed by C-1/C-2/C-3. The document is historically
   accurate for the Sprint 1x era but its "current status" wording is now misleading.

### 5.3 Unnecessary repetition — LOW

The five-domain architecture chain and the claim boundaries are restated in many documents.
This is **intentional and correct** under the AGENTS.md convention (each document is
self-contained and binding), not harmful duplication. No action needed.

### 5.4 Governance quality — HIGH

The authorization + completion checkpoint pair was applied consistently to all six
capability phases. Scope boundaries are machine-checkable flags. Hash-anchoring is applied
at every boundary. The claim policy (engineering / scientific / product) is kept separate
throughout. This is the strongest property of the ML Phase 2 corpus.

### 5.5 Traceability — HIGH

Every claim traces: evidence ← completion checkpoint ← authorization checkpoint ← strategy
← ADR ← foundation. Cross-references are dense and accurate. A reader can follow any C-6
metric back to the C-2 protocol, the C-5 inference, the C-4 artifacts, the C-3 acquisition,
and the ADR selection.

### 5.6 Reproducibility — HIGH

The governed records (manifests, hashes, replay verifications, deterministic seeds) plus
the evidence documents and the `scripts/` pipeline allow an untrusting observer to
regenerate the C-6 results from the pinned governed inputs. This is documented honestly,
including the single-seed limitation.

---

## 6. Documentation Debt

Prioritized from highest to lowest impact.

### 6.1 (Highest) Roadmap drift in the ML Capability Engineering Strategy checkpoint

The C-1…C-8 roadmap numbering diverged from execution (C-5/C-6 repurposed; C-7/C-8 not
executed as numbered). The Closure Review records this, but the roadmap checkpoint itself
does not flag it. A future reader or agent could be misled into believing runtime
integration (original C-6) and calibration (C-8) occurred.

**Recommended resolution (not performed here):** add a short drift note to the roadmap
checkpoint (or a successor v1.1) cross-referencing the Closure Review and the executed
C-numbering, so the roadmap is not read as a description of what was delivered.

### 6.2 Stale "current status" in the Implementation Authorization

The document's status block and checklist still read as if full ML Phase 2 implementation
is deferred and only Sprint 1H is authorized, when in fact six capability phases were
subsequently authorized and executed under separate checkpoints.

**Recommended resolution (not performed here):** add a status addendum noting that the
capability gates (dataset C-1, framework, evaluation C-2) were subsequently closed by the
capability checkpoints, and that the Sprint 1x restricted authorizations remain the record
for the infrastructure era. The document's gate *logic* remains valid; only its
*as-of-now* framing is stale.

### 6.3 Absorbed Data Strategy Decision Memo

The Memo's central recommendation (defer selection) is superseded by the ADR (`SELECTED —
VisA`). Keeping it in the active corpus without a supersession marker risks a reader
treating a defunct recommendation as live.

**Recommended resolution (not performed here):** add a one-line supersession header to the
Memo pointing to the ADR, or archive it later (§7).

### 6.4 Missing cross-reference: research investigations ↔ ADR

The Dataset Selection ADR draws on the three research investigations and the landscape, but
the linkage is implicit. A reader landing on the ADR may not find the underlying
primary-source evidence quickly.

**Recommended resolution (not performed here):** add explicit references from the ADR to
the research documents (low effort, high traceability value).

### 6.5 Minor: evidence/prototype-ui PNGs

`docs/evidence/prototype-ui/*.png` are Phase-1 prototype screenshots. They are correctly
marked illustrative but sit under `evidence/`, which could imply they are scientific
evidence. This is a naming/organization nuance, not ML Phase 2 scope; flagged only for
completeness.

---

## 7. Archival Candidates

No deletion. Recommendations only. ARCHIVE LATER means a candidate for a future, separate,
owner-approved archival action once a supersession marker or consolidation is in place.

| Document | Recommendation | Reason |
| --- | --- | --- |
| `AGENTS.md` | KEEP | Source of truth. |
| `KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md` | KEEP | Decision of record. |
| `KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md` | KEEP | Decision of record. |
| `KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md` | KEEP | Authoritative strategy. |
| `KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md` | KEEP | Authoritative strategy. |
| `KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md` | KEEP | Authoritative strategy. |
| `KALIBRA_ML_PHASE_2_DATA_STRATEGY_DECISION_MEMO_v1.0.md` | ARCHIVE LATER (or ABSORB INTO ADR) | Superseded by the ADR's `SELECTED — VisA`. Add a supersession marker first; then it is a clean archival candidate. |
| `KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md` | KEEP (add status addendum) | Stale as-current but historically authoritative for the Sprint 1x era; gate logic still valid. Do not archive — add a status note. |
| All 4 capability authorization checkpoints (C-3…C-6) | KEEP | Authorization records. |
| All 6 capability completion/strategy checkpoints (Arch&Cap, Capability Strategy, Model Family, C-1, C-2, C-3) | KEEP | C-1/C-2/C-3 still useful; Arch&Cap / Capability Strategy / Model Family historically important. |
| C-4, C-5, C-6 completion checkpoints | KEEP | Current state-of-the-art completion records. |
| `KALIBRA_ML_PHASE_2_CLOSURE_REVIEW_v1.0.md` | KEEP | Phase-closure decision; bridge to Phase 3. |
| All 5 evidence documents | KEEP | Durable scientific/governance records. |
| 3 research investigations + Industrial Dataset Landscape | KEEP | Primary-source reasoning behind selection; not reproducible. |
| `KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md` | KEEP (add drift note) | Historically important; carries roadmap drift that must be flagged. |

**Net archival candidates: 1** — the Data Strategy Decision Memo (after a supersession
marker). Everything else is KEEP, with two documents (Implementation Authorization, Capability
Strategy checkpoint) benefiting from short clarifying addenda rather than archival.

---

## 8. Final Recommendation

```text
READY FOR LONG-TERM REPOSITORY — with two small consolidations recommended before public release.
```

**Justification.** The ML Phase 2 documentation corpus is well-factored, high-quality, and
strongly traceable. Governance quality, traceability, and reproducibility are all HIGH.
Duplication is LOW. There is **no documentation that must be removed** for the repository to
be healthy. Every ADR, strategy, checkpoint, and evidence document earns its place.

The corpus is **not** perfectly clean: there is one genuine absorption candidate (the Data
Strategy Decision Memo, superseded by the ADR) and two documented drift cases (roadmap
numbering; Implementation Authorization stale status). These are real but minor; they do
not block long-term retention, and they are **fully disclosed** in the Closure Review. A
future observer can read the corpus honestly because the drift is named, not hidden.

The recommendation is READY rather than NEEDS CONSOLIDATION because: (a) no information is
lost or contradictory in a way that would mislead a careful reader who follows the
cross-references; (b) the single archival candidate is harmless if retained temporarily;
(c) the two drift cases are documented. The two small consolidations in §9 are improvements,
not prerequisites.

---

## 9. Next Recommendation (before the first public GitHub push)

Before the first public GitHub push, the repository owner should consider (each is a small,
owner-approved documentation action — **not** authorized by this review):

1. **Add a supersession marker to the Data Strategy Decision Memo** (one line pointing to
   the Dataset Selection ADR's `SELECTED — VisA`). This is the single highest-value
   consolidation: it prevents a public reader from treating a defunct "keep deferred"
   recommendation as live.
2. **Add a short drift/status note** to (a) the ML Capability Engineering Strategy
   checkpoint (roadmap numbering vs executed C-5/C-6) and (b) the Implementation
   Authorization (capability gates subsequently closed). Cross-reference the Closure Review
   in both. This makes the corpus self-consistent for a reader who does not read the
   checkpoints in order.
3. **Add explicit references** from the Dataset Selection ADR to the three research
   investigations and the Industrial Dataset Landscape, so a public reader can trace the
   selection to primary-source evidence.
4. **Optionally** archive the Data Strategy Decision Memo (after step 1) under a
   `docs/archive/` convention, if the owner wishes to reduce the active corpus. This is
   optional; retaining it with a supersession marker is equally acceptable.

None of these are blockers. The repository is presentable as-is; these steps raise
clarity for a public audience. No code, strategy rewrite, ADR rewrite, or deletion is
recommended.

---

## 10. Scope Boundaries and Explicit Non-Claims

This consolidation review records:

- **No implementation** — no source, test, or script modified.
- **No document modified** — no ADR, Strategy, Authorization, checkpoint, or evidence edited.
- **No file moved or archived** — classification and recommendation only.
- **No deletion** — nothing is identified for deletion; one document is an archival
  *candidate* (with supersession marker as a prerequisite).
- **No authorization** — no Phase 3 work, no archival action, no public release authorized.
- **No claim beyond existing evidence** — this review makes no scientific or product claim;
  the bounded single-seed VisA proxy claims stand exactly as recorded in the C-6 evidence
  and completion checkpoint.

---

## 11. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 ✔ |
| Working tree | `git status --short` | clean (no output) ✔ |
| HEAD | `git log -1 --oneline` | `c4a78ec docs: close ml phase 2` ✔ |

The working tree is clean; this review created exactly one new checkpoint file and modified
nothing.

---

## 12. Next Natural Step

```text
Review this persisted Documentation Consolidation Review before performing any archival or
preparing the repository for a public GitHub release.
```

The recommended pre-release consolidations (§9) are small, owner-approved documentation
actions; they are not authorized by this review and require the repository owner's decision.
No archival, ADR rewrite, or Strategy rewrite should be performed on the basis of this
review alone.
