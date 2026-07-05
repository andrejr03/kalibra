# Kalibra PaDiM Baseline Training Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no training executed)
**Date:** 2026-07-05
**Repository baseline HEAD:** `548a436 feat: implement governed visa acquisition`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **C-4 — PaDiM Baseline
Training** implementation. It is authorization planning only. It fits no model, extracts
no features, computes no statistics, exports no ONNX, runs no inference, evaluates no
metric, and modifies no ADR, Dataset Strategy, Evaluation Strategy, or Implementation
Authorization gate.

It draws its authority from the now-normative decisions recorded in the
[Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
(PaDiM selected first; PatchCore reserved second), the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) §8, the
[Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
(`SELECTED — VisA`), the
[Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md), the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
and the recorded
[Governed VisA Acquisition Evidence](../evidence/KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md).

This checkpoint defines **what a future training sprint is allowed to do**, what it is
**forbidden** to do, what it must **produce**, and how it must be **validated**. It does
not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3
checkpoints and the Governed VisA Acquisition Authorization checkpoint, and must be
reviewed before any implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — C-4 PaDiM Baseline Training
```

The authorization is **strictly limited to the offline fitting of the first PaDiM
baseline and the generation of its governed training artifacts and evidence**. It grants
no permission to infer, evaluate, export ONNX, calibrate, threshold, or claim.

**Basis for readiness — why the repository is now scientifically and technically ready:**

- **The model family is decided.** PaDiM is the SELECTED first model family and
  PatchCore is the reserved second-generation candidate; the scientific selection is
  closed and is the direct predecessor of this bounded training authorization.
- **The dataset is governed and present.** VisA is SELECTED (C-1) and its **governed
  acquisition is implemented and its evidence recorded** — the immutable source archive,
  extracted tree, per-file and archive SHA-256 manifests, immutable split manifests, and
  provenance/attribution records now exist as governed local artifacts. Training
  therefore has a real, integrity-anchored, immutable input to fit against.
- **The train split is fixed and isolable.** The C-2 protocol pins the immutable
  train / validation / test split (train = sound only). PaDiM fits on the normal
  (train) split alone, so training consumes exactly the input the acquisition produced
  without touching validation or test.
- **PaDiM is closed-form and deterministic-first.** Fitting is per-patch multivariate
  Gaussian estimation with Mahalanobis scoring — no SGD, no coreset. The only randomness
  (feature-dimension subsampling) is fully controlled by a pinned seed, so a bounded,
  reproducible, replay-verifiable fit is achievable now.
- **The evaluation protocol is fixed but deliberately not invoked here.** C-2 already
  defines how the resulting artifact will later be evaluated; producing the μ / Σ⁻¹
  artifact unblocks that future evaluation without pre-empting it.

Readiness is **for training only**. Inference, export, and evaluation each remain behind
their own separate authorization gates.

---

## 2. Authorized Scope

If and when the training sprint is authorized by a bounded implementation prompt, it may
do **only** the following:

- load the **governed VisA acquisition** (verifying manifests / integrity anchors before
  use, fail-closed on any mismatch);
- read the **immutable train split only** (sound samples only, per C-2);
- perform **deterministic feature extraction** from the governed pretrained backbone
  over the train split;
- perform **deterministic feature-dimension subsampling using pinned seeds**;
- perform **deterministic PaDiM fitting** (per-patch multivariate Gaussian estimation);
- compute **μ (per-patch mean)** and **Σ⁻¹ (per-patch inverse covariance)**, with
  deterministic regularization (Σ + εI) where required for conditioning;
- generate **governed training artifacts** (feature statistics, covariance matrices,
  training metadata, pinned seeds, governed training record);
- generate **governed training evidence**;
- perform **deterministic replay verification** (re-fit reproduces identical μ / Σ⁻¹).

Nothing beyond this list is authorized. In particular: **no inference, no evaluation, no
ONNX export.**

---

## 3. Forbidden Scope

The training sprint **must not**, under any circumstances, perform or produce:

- validation inference;
- test inference;
- metric computation;
- benchmark generation;
- Image AUROC;
- Pixel AUROC;
- AUPRO;
- threshold derivation;
- calibration;
- Trust changes;
- Review changes;
- Evidence Engine changes;
- Evaluation Engine changes;
- preprocessing changes;
- output mapping changes;
- provider changes;
- ONNX export;
- scientific claims;
- product / product-readiness claims.

Any of these would exceed the training boundary and requires its own separate
authorization gate. The runtime seams
(`InspectionInferenceProvider`, `InspectionPrediction`, `transform_prediction`) must
remain untouched.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
data/visa/derived/padim/
  training/           # training metadata, pinned seeds, governed training record
  statistics/         # μ (per-patch mean), feature statistics
  covariance/         # Σ⁻¹ (per-patch inverse covariance) matrices
  evidence/           # local training evidence products
docs/evidence/        # committed governed training evidence report
```

Required artifacts:

- **feature statistics** (per-patch μ, feature-subsample layout);
- **covariance matrices** (per-patch Σ⁻¹, with recorded regularization ε);
- **training metadata** (backbone identity/provenance, layer selection, subsample
  dimension, input contract, governed acquisition identity consumed);
- **deterministic seeds** (the pinned feature-subsample seed(s) and any tie-break
  seeds);
- **governed training record** (what was fit, from which governed input, with which
  seeds, producing which artifact hashes).

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `data/visa/derived/padim/statistics/` (μ) | **Untracked / gitignored** — regenerable derived artifact |
| `data/visa/derived/padim/covariance/` (Σ⁻¹) | **Untracked / gitignored** — regenerable, potentially large |
| `data/visa/derived/padim/training/` record + metadata + seeds | **Committed if lightweight** — reviewable governance record; large binaries stay local |
| `data/visa/derived/padim/evidence/` local evidence products | **Local** unless lightweight and reviewable |
| `docs/evidence/` training evidence report | **Committed** — evidence of a clean, reproducible fit |

The derived μ / Σ⁻¹ tensors are regenerable from the governed acquisition and the pinned
seeds and remain local; the training record, metadata, seeds, and evidence report are
the committed, reviewable proof of a governed, reproducible fit. Any `.gitignore` update
is authorized **only if required** to prevent accidental commit of derived binaries
(e.g. ignoring `data/visa/derived/padim/` statistics and covariance), minimal and scoped
strictly to that purpose.

---

## 5. Validation Requirements

The training sprint must validate, and its evidence report must demonstrate, that:

- the **governed dataset only** was used (integrity anchors verified; no mirror, no
  ungoverned data);
- the **train split only** was read (no validation, no test access);
- **deterministic seeds** were pinned and recorded;
- **feature extraction is reproducible** (identical features from identical governed
  input and backbone);
- **μ is reproducible** (bit- or tolerance-stable across re-fit, per recorded policy);
- **Σ⁻¹ is reproducible** (stable across re-fit, with recorded regularization);
- **replay consistency** holds — an independent re-fit reproduces the governed artifact;
- **no evaluation** was performed;
- **no inference** was performed;
- **no downstream code was touched** — provider, preprocessing, output mapping, Trust,
  Review, Evidence Engine, and Evaluation Engine are unchanged.

---

## 6. Scientific Boundaries

Explicitly:

- **Training is not evidence.** A fitted μ / Σ⁻¹ artifact is a prepared model input, not
  proof that Kalibra detects defects.
- **Training produces no scientific claim.**
- **Training produces no benchmark.**
- **Training produces no performance result.** No AUROC, AUPRO, threshold, or calibrated
  operating point is produced or implied.
- **Training merely prepares the governed model artifact.** The scalar raw-anomaly
  measure, localization, thresholds, and any performance characterization remain the
  concern of later, separately authorized inference and evaluation phases.

Kalibra does **not** yet perform real defect detection, and this checkpoint does not
change that.

---

## 7. Readiness Decision

```text
READY — the repository is ready for a bounded C-4 PaDiM Baseline Training
implementation prompt.

- Authorized scope: offline PaDiM fitting + governed training artifacts + training
  evidence + deterministic replay verification only.
- Forbidden scope: all inference, evaluation, metric, threshold, calibration, ONNX
  export, provider/preprocessing/output/Trust/Review/Evidence/Evaluation change, and
  every scientific or product claim.
- Required outputs, commit policy, validation requirements, and scientific boundaries
  are defined.
- Nothing fitted, extracted, computed, exported, or evaluated by this checkpoint.
  No normative document modified.
```

---

## 8. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no training / fitting**
- **no feature extraction**
- **no μ or Σ⁻¹ computation**
- **no inference**
- **no evaluation / metric / benchmark**
- **no ONNX export**
- **no threshold / calibration**
- **no scientific or product claim**
- **no documentation modified** (no ADR, Dataset Strategy, Evaluation Strategy, or
  Implementation Authorization change)
- **authorization planning only**

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document.

---

## 9. Next Natural Step

```text
Generate the bounded implementation prompt for C-4 — PaDiM Baseline Training.
```

No governing document is updated in this task. The persisted authorization checkpoint
must be reviewed before the implementation prompt is generated.
