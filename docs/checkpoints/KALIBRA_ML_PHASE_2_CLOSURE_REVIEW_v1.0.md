# Kalibra ML Phase 2 Closure Review v1.0

**Status:** Recorded — phase-closing engineering review (review only; not an implementation, not an authorization, not a roadmap update)
**Date:** 2026-07-06
**Repository baseline HEAD:** `4036d63 feat: implement scientific evaluation`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **ML Phase 2 Closure Review** as a versioned checkpoint
following the repository checkpoint convention. It is a phase-closing engineering review
only. It concludes whether ML Phase 2 is genuinely complete and whether the repository is
ready to transition into ML Phase 3.

It is **not** an implementation. It writes no code. It is **not** an authorization — it
authorizes no sprint, no Phase 3 work, no calibration, no ONNX export, and no
product-facing capability. It is **not** a roadmap update — it modifies no ADR, no
Strategy, no Implementation Authorization, and no normative document. It records a review
and a recommendation only.

It draws its standing from the full ML Phase 2 lineage: the governing documents
([`AGENTS.md`](../../AGENTS.md),
[ML Phase 2 Scientific Architecture Plan](../KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md),
[Framework ADR](../KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md),
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md),
[Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[Implementation Authorization](../KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md)),
the strategy checkpoints
([Architecture & Capability](KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md),
[ML Capability Engineering Strategy](KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md),
[Scientific Model Family Selection](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)),
the C-1 through C-6 authorization and completion checkpoints, and the four recorded
evidence documents.

Throughout, **must**, **must not**, **complete**, and **not yet demonstrated** carry the
binding sense established across the ML Phase 2 documents.

---

## 0. Repository Baseline Correction

The closure-review task brief stated the baseline HEAD as `300b808 feat: implement
governed padim inference`. **The actual repository HEAD is
`4036d63 feat: implement scientific evaluation`.** The working tree is **clean**
(no uncommitted changes). ML Phase 2 has therefore advanced one commit beyond the brief's
stated baseline: C-6 Scientific Evaluation is **implemented and committed**, and its
completion checkpoint
([C-6](KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md)) is part of the
committed lineage. This review is performed against the actual repository state, not the
brief's stated baseline.

The ML Phase 2 capability lineage, as committed:

```text
Infrastructure Engineering (Sprint 0, 1A–1H) — placeholder identity model on a real ONNX Runtime substrate
        ↓
C-1 Dataset Selection Closure     (SELECTED — VisA)
        ↓
C-2 Evaluation Protocol Fixation  (Image AUROC primary; AUPRO + Pixel AUROC secondary; P/R/F1 diagnostic)
        ↓
C-3 Governed VisA Acquisition Strategy + acquisition sprint (governed dataset + frozen splits)
        ↓
Scientific Model Family Selection (PaDiM first; PatchCore reserved)
        ↓
C-4 PaDiM Baseline Training       (single-seed fit, μ / Σ⁻¹ for 12 VisA classes)
        ↓
C-5 Governed PaDiM Inference      (offline 6492-input inference, anomaly maps + InspectionPrediction records)
        ↓
C-6 Scientific Evaluation         (per-class VisA proxy metrics, validation-derived operating point, failure analysis, replay)
        = HEAD
```

---

## 1. Phase Objective Achievement

### 1.1 What ML Phase 2 was created to accomplish

The [ML Capability Engineering Strategy Checkpoint](KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_CHECKPOINT_v1.0.md)
opened ML Phase 2 capability work with a single binding constraint identified by the
[Architecture & Capability Checkpoint](KALIBRA_ML_PHASE_2_ARCHITECTURE_AND_CAPABILITY_CHECKPOINT_v1.0.md):
**the binding constraint was scientific, not foundational.** The placeholder identity
model was "the only model at the center of the chain," scientific capability was
"effectively zero," and the substrate was declared "substantially complete." The stated
next strategic problem was: *"the absence of a real, learned model trained on a real
governed dataset and measured by a real evaluation — currently masked by the placeholder
identity graph."*

ML Phase 2 capability engineering was therefore created to **replace the placeholder
identity model's null scientific behavior with a real, learned model, trained on a real
governed dataset, and measured by a real evaluation.** That is the objective against
which completion is judged.

### 1.2 Assessment by dimension

**Infrastructure — COMPLETE (and unchanged through C-6).** The governed, deterministic
image → `InspectionPrediction` → `RawInspectionResult` → Trust → Review → Evidence →
Evaluation substrate built in Sprint 0 and Sprint 1A–1H remains intact. Every C-x
completion checkpoint's downstream scope check produced no output. No substrate work is
owed.

**Governance — COMPLETE.** The dataset, framework, evaluation, and authorization gates
that the Implementation Authorization named as "Deferred" are now closed by execution:
VisA is `SELECTED` (Dataset Selection ADR), ONNX Runtime is the selected runtime
(Framework ADR), the C-2 protocol fixes metrics and statistics, and every capability
sprint ran under its own bounded authorization + completion checkpoint pair. The
checkpoint workflow defined in `AGENTS.md` (Decision → Persist Checkpoint → Review →
Authorization → Implementation → Implementation Review → Persist Completion Evidence)
was followed faithfully for every capability phase.

**Scientific capability — PARTIALLY ACHIEVED (the decisive nuance of this review).** A
real learned PaDiM model has been fit on a real governed VisA dataset and measured by a
real evaluation. The placeholder's null scientific behavior has been replaced **offline**:
the raw anomaly measure measurably separates sound from defective VisA images
(macro Image AUROC `0.757826`), with bounded per-class localization signal. This is a
genuine scientific result that did not exist at the start of the phase. **However**, the
real model is **not wired into the runtime** — the canonical `inspect()` path still
executes the placeholder identity model, so the chain does not yet carry genuine signal
end-to-end at runtime. The phase objective is achieved in the offline scientific sense
and **not yet** achieved in the integrated runtime sense.

**Engineering maturity — HIGH.** Determinism, replay verification, hash-anchored
integrity, governed scope boundaries, fail-closed verification, and per-phase completion
evidence are consistently applied across all six capability phases. The discipline is the
strongest asset of the phase and is the reason the scientific results are trustworthy.

### 1.3 Objective achievement verdict

The phase's **scientific objective is achieved in evidence** (a real learned model,
trained on a real governed dataset, measured by a real evaluation, with reproducible
governed results) **but not yet achieved in integration** (the real model is not the
runtime model). This distinction is the central finding of the closure review and drives
the completion decision in §6.

---

## 2. Capability Assessment

The four capability classes are kept strictly separate, per the Architecture & Capability
Checkpoint convention. They are **not** mixed.

- **Engineering capability — HIGH.** A production-grade, contract-bound, deterministic,
  fully tested inference substrate (Sprint 0, 1A–1H) plus a governed, replay-verified
  offline ML pipeline (C-3 acquisition, C-4 training, C-5 inference, C-6 evaluation).
  479 tests pass; `compileall` is clean; deterministic replay is proven at every stage.
  This is the repository's strongest asset and is unchanged by the capability phases.

- **Scientific capability — BOUNDED, REAL, SINGLE-SEED, PROXY-ONLY.** For the first
  time, the repository holds reproducible evidence that a learned model's raw anomaly
  measure separates sound from defective images on a governed dataset: per-class Image
  AUROC, Pixel AUROC, and AUPRO across all 12 VisA classes, with a validation-derived
  operating point, full failure analysis, and deterministic replay. The capability is
  *bounded*: single seed (no variance, no confidence intervals), VisA proxy only (no
  domain-of-record, no cross-domain), and the operating point is diagnostic-only (not
  calibrated, not a product threshold). It is real signal, honestly bounded.

- **Runtime capability — REAL BUT STILL PLACEHOLDER-DRIVEN.** ONNX Runtime genuinely
  loads and executes a session end-to-end behind the provider seam (Sprint 1F evidence).
  **However**, the runtime's `inspect()` path still consumes the **placeholder identity
  model** (`RAW_MEASURE_SCALE = "placeholder_hash_raw_0_100"`,
  `PLACEHOLDER_EXAMINATION_KIND`, `OnnxInspectionInferenceProvider` restricted to the
  `onnx-placeholder-boundary-model-v1`). PaDiM exists only in `scripts/` and is not
  exported to ONNX and not integrated into the canonical flow. The runtime can carry real
  inference in principle; it does not yet carry real inference in practice.

- **Product capability — NONE.** Nothing in the system can be relied upon by a user to
  detect a defect on a real part. The prototype surface remains projection only. No
  calibrated confidence, no trust qualification, no product threshold, and no
  product-readiness claim exists. This is unchanged from the start of the phase and is
  correct.

---

## 3. Scientific Assessment

### 3.1 Governed acquisition (C-3) — DEMONSTRATED

The governed VisA acquisition is real and verified: pinned canonical S3 archive
(SHA-256 `2eb8690c…`), per-file SHA-256 manifest, provenance and attribution records,
and immutable train/validation/test split manifests with recorded split hashes. C-4, C-5,
and C-6 each independently re-verified the archive, files manifest, split hashes, and
provenance before consuming the dataset. The four irreducible upstream limitations
(no DOI/version tag, no upstream checksum, incomplete annotation-process documentation,
proxy domain) remain **recorded, not closed** — which is the honest posture.

### 3.2 PaDiM baseline (C-4) — DEMONSTRATED (single-seed)

A deterministic PaDiM baseline was fit on train-only normal images (3,849 samples) for all
12 VisA classes, with a single pinned feature-subsample seed (`271828`, indices
`[0, 2, 5, 6, 7, 9, 12, 13]`), regularized covariance (`Σ + εI`, ε = 0.001), and a
complete second-fit replay proving byte-identical μ, Σ, Σ⁻¹. The baseline is a real
learned model that replaces the placeholder's null behavior **as a fitted artifact**. The
single-seed limitation is a known scientific debt (§4).

### 3.3 Inference (C-5) — DEMONSTRATED (offline)

Governed PaDiM inference scored 6,492 inputs across the validation (2,164) and test
(4,328) splits, producing deterministic float64 Mahalanobis anomaly maps (64×64), raw
anomaly measures (`padim_anomaly_map_max_v1`), deterministic localizations
(`padim_raw_anomaly_map_argmax_region_v1`), and governed `InspectionPrediction` records
under the existing prediction contract. A complete second inference run was proven
byte-identical. Crucially, **inference is not evaluation**: no metric, threshold, or
operating point was derived, and the contract-mandated `predicted_judgement=DEFECT` field
is recorded explicitly as a contract artifact, not a classification.

### 3.4 Evaluation (C-6) — DEMONSTRATED (single-seed, proxy)

The frozen C-2 protocol was executed as a pure read-only function over governed inputs on
the untouched frozen test partition, per-class across all 12 VisA classes. Recorded
governed results:

| Metric | Macro mean | Role |
| --- | --- | --- |
| Image AUROC | `0.757826` | primary official (threshold-free detection separation) |
| Pixel AUROC | `0.865196` | secondary official (with background-dominance caveat) |
| AUPRO | `0.555765` | secondary official (per-region localization) |
| Precision / Recall / F1 | `0.209019` / `0.714583` / `0.323432` | diagnostic only |

Operating point `2.445569` (validation-derived, applied unchanged to test; not calibrated,
not a product threshold). Failure analysis: 1,298 false positives, 137 false negatives,
237 localization failures, 10 boundary cases per class, 5 proxy-domain limitations — all
per class. Deterministic replay (complete second evaluation run) reproduces identical
metrics, operating point, failure analysis, reports, and hashes.

### 3.5 What has genuinely been demonstrated

- A real learned model's raw anomaly measure **measurably separates** sound from
  defective VisA images, per class, reproducibly.
- Bounded per-region localization signal exists on VisA pixel masks (AUPRO > 0.5 macro),
  with the background-dominance caveat on Pixel AUROC disclosed.
- The entire acquire → train → infer → evaluate chain is **governed, deterministic, and
  replayable** end-to-end by an untrusting observer.
- The C-2 protocol's design discipline (threshold-free primary metrics, validation-derived
  operating point, both error kinds reported separately, per-class primacy) survived
  contact with real execution.

### 3.6 What has NOT yet been demonstrated

- **Runtime integration.** The real PaDiM model is not the runtime model. The canonical
  `inspect()` flow still runs the placeholder. No end-to-end runtime path yet carries the
  real model's signal.
- **ONNX export of the real model.** PaDiM has not been exported to a governed ONNX
  artifact. The runtime ONNX substrate therefore cannot yet execute it.
- **Multi-seed characterization.** Only one seed exists. No per-class variance, no
  confidence intervals, no significance testing. The C-2 statistical protocol's
  "repeated seeded runs" obligation is **not** met.
- **Calibration / Trust.** No calibrated confidence, no trust qualification, no abstention,
  no drift. The raw measure is not and must not be presented as confidence.
- **Domain-of-record performance.** VisA is a proxy. No cast-aluminium / CNC / gearbox /
  metal-part performance, and no cross-domain generalization, is demonstrated.

---

## 4. Remaining Scientific Debt

Prioritized from highest to lowest scientific leverage. Each is a deferred obligation,
not a defect in what was delivered; each was disclosed honestly in the phase that
produced it.

1. **(Highest) Runtime integration of the real model.** The real PaDiM baseline is
   offline-only. Until it is exported to ONNX and wired behind `inspect()` (replacing the
   placeholder), the engineering substrate carries no real signal at runtime and the
   phase's *integrated* objective is unmet. This is the single largest gap between the
   executed phase and the original C-1…C-8 roadmap (whose C-6 was "Model Integration").

2. **Single-seed limitation.** PaDiM's only stochastic element (the seeded
   feature-dimension subsample) was characterized at one seed (`271828`) only. No
   per-class variance, spread, or confidence intervals exist. The C-2 §2.5 / Evaluation
   Strategy §7 "repeated seeded runs … variance … confidence intervals" obligation is
   **not** met. Any detection/localization claim is bounded to this single seed and
   **must not** present itself as variance-characterized.

3. **Absence of calibration and confidence intervals.** No calibrated confidence exists;
   the raw anomaly measure and the validation-derived operating point are not probability,
   confidence, or trust. This is a Trust-domain obligation correctly deferred, but it
   remains owed before any confidence claim.

4. **No ONNX export of the real model.** A prerequisite for (1). The deterministic ONNX
   export that the model-family selection checkpoint named as a PaDiM strength has not
   been exercised for the real fitted baseline.

5. **Proxy-domain gap.** VisA is not Kalibra's domain of record (cast-aluminium, CNC,
   gearbox-housing, metal parts). PaDiM is alignment-sensitive; pose/registration
   differences are an active risk for future metal-part domains. No cross-domain
   generalization is claimed or demonstrated.

6. **VisA upstream documentation gaps.** No DOI/version tag, no upstream checksum,
   incomplete annotation-process documentation. These constrain the strength of
   localization interpretation and are recorded, not closed.

7. **PatchCore reserved, not adopted.** The planned second-generation model is reserved
   pending a proven real map → prediction pipeline and evaluation baseline. The C-6
   evaluation baseline now exists (offline); PatchCore remains future work.

8. **Calibration metrics, uncertainty-quality, review-routing, drift metrics.** Explicitly
   excluded from the first official set; no evidence basis exists. Correctly deferred.

---

## 5. Architectural Assessment

**The current architecture requires no further substrate work.** This is the same
conclusion the Architecture & Capability Checkpoint reached at the close of Sprint 1H,
and it remains true after C-6.

- The five-domain ownership (Inspection → Trust → Review → Evidence → Evaluation) is
  intact. Every C-x completion checkpoint's downstream scope check produced no output.
- The provider seam (`InspectionInferenceProvider`), the `InspectionPrediction` boundary,
  and `InspectionEngine.transform_prediction(...)` ownership are unchanged.
- The offline ML pipeline (C-3/C-4/C-5/C-6 in `scripts/`) is correctly **isolated** from
  the runtime: it consumes governed inputs, produces governed evidence, and touches no
  `src/` domain package.
- The remaining gaps (§4) are **scientific payload and integration gaps, not substrate
  gaps.** Specifically: wiring the real model into the runtime is an *integration* task on
  the existing substrate (export PaDiM → governed ONNX artifact → loader → provider →
  retire placeholder), not new architecture. The substrate is ready to receive it.

No architectural drift was introduced. No new contract, seam, or domain responsibility
was created. The architecture is sound and ready for the integration work that the
scientific payload now demands.

---

## 6. Phase Completion Decision

```text
ML Phase 2 COMPLETE — as a bounded scientific-evaluation capability milestone.
```

With an explicit, honest boundary:

- **What is complete:** the bounded scope that was authorized and executed — governed
  VisA acquisition, frozen C-2 evaluation protocol, PaDiM family selection, deterministic
  single-seed PaDiM training, governed offline inference, and governed single-seed
  scientific evaluation producing real, bounded, per-class VisA proxy metrics with full
  failure analysis and deterministic replay. Every authorized boundary was honored; every
  completion checkpoint is PASS; the scientific objective is achieved **in evidence**.

- **What is not complete and is explicitly carried forward as deferred scientific debt:**
  the original C-1…C-8 roadmap's *integration and calibration* tail. The roadmap's C-5
  (ONNX export), C-6 (runtime integration), C-7, and C-8 (calibration) were redefined
  during execution into the offline C-5 (inference) and C-6 (evaluation) actually
  delivered. The **runtime still runs the placeholder**, the real model is **not
  exported to ONNX**, and **no calibration or multi-seed characterization exists.**

**Justification.** The phase as *executed and authorized* — six bounded capability phases,
each with its own authorization + completion checkpoint, each closing exactly its
declared scope — is genuinely complete: the placeholder's null scientific behavior has
been replaced by a real learned model, trained on a real governed dataset, and measured by
a real evaluation, all reproducibly and governed. That is a real, defensible milestone
and it is the honest boundary of what was authorized.

The phase as *originally drafted* (C-1…C-8 ending in "calibration & scientific validation
closing ML Phase 2 as a scientifically valid system") is **not** complete: the real model
is not integrated into the runtime, there is no calibrated confidence, and there is no
multi-seed statistical validation. Those are the obligations listed in §4.

This review therefore closes ML Phase 2 **as the scientific-evaluation capability
milestone that was authorized**, while explicitly recording that the integration and
calibration tail remains deferred to ML Phase 3. Closing the phase here is honest **only
because** the integration and calibration gaps are named explicitly and carried forward —
not hidden behind a favorable aggregate.

**This closure does not authorize anything.** It does not authorize ONNX export, runtime
integration, multi-seed characterization, calibration, or any product-facing capability.
Each remains behind its own separate authorization gate.

---

## 7. Readiness For Phase 3

ML Phase 2 is complete (per §6). The repository is **ready to transition into ML Phase 3**.

The highest-value next scientific capability — **recommended, not authorized** — is:

```text
Runtime integration of the real PaDiM baseline: export the fitted model to a governed
ONNX artifact, wire it behind InspectionInferenceProvider so it replaces the placeholder
in the canonical inspect() path, and evidence that the full runtime chain carries genuine
signal end-to-end on real inputs.
```

Rationale:

- It is the **single largest remaining gap** between the offline scientific result (which
  exists) and the runtime (which still runs the placeholder). Every other deferred item —
  multi-seed variance, calibration, product capability — is downstream of a runtime that
  actually carries the real model.
- It is an **integration task on the existing substrate**, not new architecture (§5). The
  provider seam, loader, output mapping, and deterministic-replay machinery were built
  precisely for this. The substrate is ready.
- It directly addresses scientific debt item #1 (§4) and unblocks #4 (ONNX export) as a
  natural sub-step.
- It is the natural resumption of the original roadmap's intent (C-5 export, C-6
  integration), now that the offline scientific payload exists to export and integrate.

**Secondary, parallelizable once integration lands:** multi-seed characterization of the
fitted baseline (re-fit over a pre-registered seed set) to discharge scientific debt item
#2 and begin satisfying the C-2 §2.5 statistical obligation. This requires its own
refit authorization.

**Not recommended as a Phase 3 first step:** calibration / Trust qualification. Calibration
operates on calibrated confidence and is gated by its own evidence; it is correctly
deferred until the real model runs in the runtime and a measured baseline exists on the
integrated path.

This recommendation **authorizes nothing.** It identifies direction only. Any Phase 3 work
requires its own authorization checkpoint, reviewed by the repository owner, before
implementation begins.

---

## 8. Lessons Learned

Recorded to influence future phases.

### 8.1 Governance

- **The authorization + completion checkpoint pair is effective.** Six bounded capability
  phases were delivered without scope creep, each closing exactly what it declared. The
  discipline of writing the authorization *before* the implementation, and the completion
  review *after*, is what kept the scientific results trustworthy.
- **C-number repurposing must be tracked.** The original C-1…C-8 roadmap was redefined
  during execution (C-5/C-6 shifted from export/integration to inference/evaluation).
  This was governed — each redefinition had its own authorization — but it means the
  *roadmap document* and the *executed phases* diverged. Future phases should either
  revise the roadmap checkpoint when redefining C-numbers, or use a distinct numbering
  series, so a future observer is not misled by stale roadmap text.
- **Scope boundaries as machine-checkable flags worked.** The `scope_boundaries` blocks
  in each phase's metadata (all flags `false`) made "did this phase stay in its lane?"
  a verifiable question rather than a narrative one.

### 8.2 Documentation

- **Evidence documents are the durable scientific memory.** The four evidence files
  (acquisition, training, inference, evaluation) are what an untrusting observer actually
  uses. They carried the claim boundaries, non-claims, and limitations faithfully.
- **Normative documents were not modified during capability execution** — correct. The
  strategies and ADRs remained the source of truth; checkpoints recorded the reasoning
  that produced state. This separation held throughout.

### 8.3 Checkpoint workflow

- **The AGENTS.md workflow (Decision → Checkpoint → Review → Authorization →
  Implementation → Review → Completion Evidence) was followed for every phase.** This is
  the single most important reproducibility property of ML Phase 2 and should be preserved
  unchanged in Phase 3.
- **Phase-closure reviews are valuable.** This review surfaced the runtime-integration gap
  that no individual completion checkpoint could see, because each phase correctly closed
  only its own scope.

### 8.4 Evidence discipline

- **Hash-anchoring at every boundary held.** Archive → files → splits → training
  artifacts → inference outputs → evaluation records: each stage re-verified its inputs by
  hash before use and failed closed on mismatch. This is why the replay claims are
  defensible.
- **Keep large derivatives local; commit lightweight governance records.** The
  `.gitignore` allow-list pattern (commit metadata/replay/hashes/evidence; ignore large
  `.npy`/payload) kept the repository reviewable without bloating it. The one observation
  (C-6 metadata embedding the 6492-entry sample map at ~3.7 MB) is consistent with the
  C-4/C-5 convention but is worth factoring out if repository size grows.

### 8.5 Reproducibility

- **Deterministic replay was proven, not asserted, at every stage** (complete second
  training fit; complete second inference run; complete second evaluation run). This is
  the gold standard and should be the baseline expectation for all future scientific work.
- **Single-seed is the standing caveat.** The phase delivered strong determinism but only
  one seed. Phase 3 should treat multi-seed characterization as a first-class scientific
  obligation, not an afterthought, because the C-2 protocol already names it mandatory.

---

## 9. Scope Boundaries and Explicit Non-Claims

This closure review records:

- **No code implemented.** No source, test, script, or evidence file was modified.
- **No authorization granted.** No sprint, no Phase 3 work, no ONNX export, no runtime
  integration, no multi-seed characterization, no calibration, and no product-facing
  capability is authorized by this review.
- **No roadmap update.** No ADR, Strategy, or Implementation Authorization was modified.
- **No scientific or product claim beyond the C-6 evidence.** The bounded single-seed VisA
  proxy claims stand exactly as recorded in the
  [C-6 completion checkpoint](KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md)
  and the
  [scientific evaluation evidence](../evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md).
  No production, cross-domain, calibrated-confidence, benchmark-leadership, or
  product-readiness claim is made or implied.
- **Kalibra does not yet perform real defect detection at runtime.** The runtime still
  runs the placeholder identity model. The real PaDiM baseline is offline-only.

The closing boundary is honest only because the deferred debts (§4) and the
non-integrated runtime state are named explicitly here.

---

## 10. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 ✔ |
| Working tree | `git status --short` | clean (no output) ✔ |
| Test suite | `python3 -m pytest -q` | 479 passed, 1 skipped ✔ |
| HEAD | `git log -1 --oneline` | `4036d63 feat: implement scientific evaluation` |

The single skipped test predates ML Phase 2 capability work and is unrelated.

---

## 11. Next Natural Step

```text
Review this persisted ML Phase 2 Closure Review before deciding whether to open ML Phase 3.
```

If ML Phase 3 is opened, the recommended (not authorized) first capability is runtime
integration of the real PaDiM baseline (§7). That work requires its own authorization
checkpoint, reviewed and approved by the repository owner, before any implementation
begins. Until then, the runtime continues to run the placeholder, and every claim remains
bounded to the offline single-seed VisA proxy evidence recorded in C-6.
