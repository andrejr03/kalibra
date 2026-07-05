# Kalibra Governed PaDiM Inference Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no inference executed)
**Date:** 2026-07-05
**Repository baseline HEAD:** `e0ef4b6 feat: implement deterministic padim baseline training`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **C-5 — Governed PaDiM
Inference** implementation. It is authorization planning only. It runs no inference,
produces no anomaly map, computes no Mahalanobis distance, scores no metric, evaluates
no result, exports no ONNX, calibrates nothing, derives no threshold, and modifies no
ADR, Dataset Strategy, Evaluation Strategy, or Implementation Authorization gate.

It draws its authority from the now-normative decisions recorded in the
[Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
(PaDiM selected first; PatchCore reserved second), the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) §8, the
[Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
(`SELECTED — VisA`), the
[Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md)
(§2 provider / prediction boundary; §8 raw-anomaly-measure boundary), the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
the recorded
[Governed VisA Acquisition Evidence](../evidence/KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md),
the [C-4 PaDiM Baseline Training Authorization Checkpoint](KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md),
and the recorded
[C-4 PaDiM Baseline Training Completion Checkpoint](KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md)
together with
[PaDiM Baseline Training Evidence](../evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md).

This checkpoint defines **what a future inference sprint is allowed to do**, what it is
**forbidden** to do, what it must **produce**, and how it must be **validated**. It does
not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3
checkpoints, the Governed VisA Acquisition Authorization checkpoint, and the C-4 PaDiM
Baseline Training Authorization checkpoint, and must be reviewed before any
implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — C-5 Governed PaDiM Inference
```

The authorization is **strictly limited to deterministic offline PaDiM inference against
governed artifacts over the governed VisA dataset, the production of `InspectionPrediction`
under the existing prediction contract, and the generation of governed inference
evidence**. It grants no permission to evaluate, score a metric, derive a threshold,
calibrate, export ONNX, or claim.

**Basis for readiness — why the repository is now technically ready:**

- **The governed model artifacts exist and are recorded.** C-4 completed and recorded the
  deterministic PaDiM baseline fit. The μ (`statistics/mu_by_class.npy`) and Σ⁻¹
  (`covariance/covariance_inverse_by_class.npy`) artifacts exist for all 12 VisA classes,
  with recorded artifact hashes, replay verification, and the governing metadata set
  (`training_metadata.json`, `dataset_identity.json`, `feature_indices.json`,
  `numerical_config.json`, `preprocessing_contract.json`, `backbone_metadata.json`).
  Inference therefore has a real, integrity-anchored, reproducible model artifact to read.
- **The governed input dataset exists and is verified.** VisA is SELECTED (C-1) and its
  governed acquisition is implemented and evidenced (C-3) — the immutable source archive,
  extracted tree, per-file and archive SHA-256 manifests, immutable split manifests, and
  provenance/attribution records are present. Inference therefore has a real, governed
  input with integrity anchors it can verify before use.
- **The inference contract is already fixed and isolated.** `InspectionPrediction`
  (`src/inspection/domain.py`) is the abstract, non-canonical, untrusted prediction
  boundary, and `InspectionInferenceProvider.predict(...)` is the single seam behind which
  inference implementations may be referenced (Evaluation Strategy §2). The contract
  already carries `predicted_raw_anomaly_measure`, `predicted_localization`,
  `raw_measure_kind = raw_anomaly_measure`, and `raw_measure_scale =
  model_raw_anomaly_measure` — exactly the fields a deterministic PaDiM inference must
  populate. Inference can produce this object without inventing a new contract.
- **The raw-anomaly-measure boundary is explicit.** Evaluation Strategy §8 fixes the raw
  anomaly measure as the inference method's uncalibrated deviation score — substrate
  inside `InspectionPrediction`, explicitly **not** a probability or confidence.
  Confidence, calibration, abstention, and drift remain Trust Qualification concerns.
  Inference therefore has a precise, already-documented scientific boundary.
- **Feature extraction is deterministic and replayable.** C-4 recorded that
  `extract_features` and `patch_mean_std` are pure functions over the governed
  preprocessing contract (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`), with identical
  feature tensors reproduced across two fits. Inference can reuse the **same** deterministic
  extraction path and the **same** preprocessing contract, so a per-sample anomaly map is
  reproducible from the same governed inputs and the same governed μ / Σ⁻¹.
- **The evaluation protocol is fixed but deliberately not invoked here.** C-2 already
  defines how the resulting predictions will later be evaluated; producing governed
  `InspectionPrediction` objects unblocks that future evaluation without pre-empting it.

Readiness is **for inference only**. Evaluation, thresholding, calibration, ONNX export,
and any scientific or product claim each remain behind their own separate authorization
gates.

---

## 2. Authorized Scope

If and when the inference sprint is authorized by a bounded implementation prompt, it may
do **only** the following:

- load the **governed PaDiM artifacts** (μ, Σ⁻¹, `feature_indices`, and the governing
  metadata set), verifying artifact hashes against `training/artifact_hashes.json` before
  use and failing closed on any mismatch;
- load the **governed VisA dataset** (verifying the archive SHA-256, files manifest
  SHA-256, per-file hashes, split hashes, and provenance before use, failing closed on any
  mismatch) — reading **only** the immutable split(s) the implementation prompt names;
- perform **deterministic feature extraction** over the consumed inputs using the **same**
  preprocessing contract (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`), **same**
  backbone identity (`kalibra-fixed-patch-feature-backbone-v1`), **same** selected layer
  (`fixed_patch_statistics_64x64_patch8`), and **same** feature-dimension subsample
  (indices `[0, 2, 5, 6, 7, 9, 12, 13]`) recorded by C-4;
- compute the **per-patch Mahalanobis distance** against the governed μ and Σ⁻¹ for the
  matching class, using the recorded dtype (`float64`) and numerical configuration;
- generate **anomaly maps** (per-patch / per-pixel raw deviation surfaces) from the
  Mahalanobis distances;
- derive the **scalar raw anomaly measure** per input strictly as an aggregation of the
  anomaly map (e.g. the maximum deviation), explicitly marked `raw_anomaly_measure` and
  `model_raw_anomaly_measure` — never as probability or confidence;
- produce **governed output tensors** (the anomaly maps and any intermediate governed
  surfaces), with recorded hashes;
- produce an **`InspectionPrediction`** per input under the existing contract in
  `src/inspection/domain.py`, populating `predicted_raw_anomaly_measure`,
  `predicted_localization` (where a localization is derived), the raw measure kind/scale,
  and `model_metadata` (governed artifact and dataset identity, preprocessing contract,
  feature indices, layer, dtype);
- perform **deterministic replay verification** (re-running inference over a governed
  subset reproduces identical anomaly maps, identical scalar raw anomaly measures, and
  identical localizations);
- generate **governed inference evidence**.

Nothing beyond this list is authorized. In particular: **no evaluation, no metrics, no
thresholds, no calibration, no ONNX export.**

The runtime seams must be respected. The sprint may **construct** `InspectionPrediction`
objects under the existing contract; it must not alter the contract, must not alter
`InspectionEngine.transform_prediction`, and must not wire inference into
`InspectionEngine.inspect()` unless the implementation prompt explicitly authorizes a
specific, bounded wiring and the seam is preserved.

---

## 3. Forbidden Scope

The inference sprint **must not**, under any circumstances, perform or produce:

- Image AUROC;
- Pixel AUROC;
- AUPRO;
- Precision;
- Recall;
- F1;
- threshold derivation;
- operating-point derivation;
- calibration;
- benchmark generation;
- scientific claims;
- product / product-readiness claims;
- Trust changes (no calibrated confidence, no abstention, no drift);
- Review changes;
- Evidence Engine changes;
- Evaluation Engine changes;
- ONNX export;
- preprocessing changes (the preprocessing contract is fixed by C-4 and must be reused
  unchanged);
- architecture changes — no new contract, no new seam, no new domain responsibility, no
  rewiring of the canonical Inspection → Trust → Review → Evidence → Evaluation flow.

Any of these would exceed the inference boundary and requires its own separate
authorization gate. The runtime seams (`InspectionInferenceProvider`,
`InspectionPrediction`, `InspectionEngine.transform_prediction`) must be preserved; if a
new inference-side object is introduced it must remain on the inference side of the seam
and must not be consumed by any downstream domain in this sprint.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
data/visa/derived/padim/
  inference/                # governed inference outputs (this sprint's surface)
    anomaly_maps/           # per-input anomaly maps (raw deviation surfaces)
    predictions/            # per-input InspectionPrediction records (governed)
    metadata/               # governed inference metadata
    replay/                 # governed replay record
    artifact_hashes.json    # hashes of every governed inference artifact
docs/evidence/              # committed governed inference evidence report
```

Required artifacts:

- **anomaly maps** — per-input raw Mahalanobis deviation surfaces;
- **governed inference metadata** — the consumed governed dataset identity, the consumed
  governed PaDiM artifact identity (μ / Σ⁻¹ hashes, feature indices, layer, backbone,
  preprocessing contract, dtype), the consumed split identity, and the inference
  configuration (aggregation policy for the scalar measure, localization policy, replay
  subset definition);
- **governed output tensors** — the anomaly maps and any intermediate governed surfaces,
  with recorded hashes;
- **`InspectionPrediction` records** — one per input, produced under the existing contract,
  with `model_metadata` carrying full governed provenance back to the C-4 artifacts and the
  C-3 acquisition;
- **governed replay record** — confirming that re-running inference over the replay subset
  reproduced identical anomaly maps, identical scalar raw anomaly measures, and identical
  localizations, with per-artifact hash agreement;
- **inference hashes** — `artifact_hashes.json` covering every governed inference artifact,
  so an observer can verify integrity without re-running.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `data/visa/derived/padim/inference/anomaly_maps/` | **Untracked / gitignored** — regenerable, potentially large derived tensors |
| `data/visa/derived/padim/inference/predictions/` per-input records | **Untracked / gitignored** if large / numerous; **committed if lightweight and reviewable** |
| `data/visa/derived/padim/inference/metadata/` + `replay/` + `artifact_hashes.json` | **Committed if lightweight** — reviewable governance record; large binaries stay local |
| `docs/evidence/` inference evidence report | **Committed** — evidence of clean, reproducible, governed inference |

The anomaly maps and per-input prediction records are regenerable from the governed
acquisition, the governed μ / Σ⁻¹ artifacts, and the fixed preprocessing contract; they
remain local. The inference metadata, replay record, artifact hashes, and the evidence
report are the committed, reviewable proof of governed, reproducible inference. Any
`.gitignore` update is authorized **only if required** to prevent accidental commit of
derived inference outputs (e.g. extending the existing
`data/visa/derived/padim/inference/` ignore rule), minimal and scoped strictly to that
purpose.

---

## 5. Validation Requirements

The inference sprint must validate, and its evidence report must demonstrate, that:

- the **governed dataset only** was used (integrity anchors verified before use; no mirror,
  no ungoverned data);
- the **governed PaDiM artifacts only** were used (μ / Σ⁻¹ / feature-indices hashes
  verified against `training/artifact_hashes.json` before use; no re-fit, no substitution);
- **deterministic replay** holds — re-running inference over the replay subset reproduces
  identical outputs;
- **identical anomaly maps** are produced across the replay (bit- or tolerance-stable per
  recorded policy, with hash agreement);
- **identical raw anomaly measures** are produced across the replay (the scalar
  `predicted_raw_anomaly_measure` per input is stable);
- **identical localization** is produced across the replay (the same
  `predicted_localization` per input, where one is derived);
- **identical hashes** are recorded for every governed inference artifact across the replay;
- only **`InspectionPrediction`** is produced as the prediction surface — under the existing
  contract, with the raw measure kind/scale correctly marked, and with full governed
  provenance in `model_metadata`;
- **no downstream domain was modified** — `InspectionEngine.transform_prediction`,
  `InspectionInferenceProvider` protocol, Trust, Review, Evidence Engine, and Evaluation
  Engine are unchanged; inference is not wired into `inspect()` unless explicitly
  authorized by the implementation prompt and the seam is preserved;
- **no evaluation, no metric, no threshold, no calibration, no ONNX export** was performed.

---

## 6. Scientific Boundaries

Explicitly:

- **Inference is not evaluation.** Producing an `InspectionPrediction` is preparing an
  input for the Evaluation Strategy; it is not measuring the system against its claims.
- **Inference produces no benchmark.** No Image AUROC, Pixel AUROC, AUPRO, Precision,
  Recall, F1, or any aggregate score is produced or implied.
- **Inference produces no scientific claim.** A raw anomaly measure that fires on a test
  image is not evidence that Kalibra detects defects; only evaluation against frozen,
  preserved, untouched evidence can establish that, and evaluation is gated separately.
- **Inference produces no calibrated confidence.** The scalar raw anomaly measure is
  explicitly marked `raw_anomaly_measure` / `model_raw_anomaly_measure` and is **not** a
  probability, not a confidence, and not a trust statement. Calibration, abstention, and
  drift remain owned by the Trust Qualification Engine (Evaluation Strategy §8).
- **Inference prepares inputs for the Evaluation Strategy only.** The governed
  `InspectionPrediction` records and anomaly maps exist so that a later, separately
  authorized evaluation phase can consume preserved evidence — never images, provider
  internals, or model objects.

Kalibra does **not** yet perform real defect detection, and this checkpoint does not
change that. Governed inference produces governed raw predictions; it does not establish
that those predictions are good.

---

## 7. Readiness Decision

```text
READY — the repository is ready for a bounded C-5 Governed PaDiM Inference
implementation prompt.

- Authorized scope: governed PaDiM artifact loading + governed VisA dataset loading +
  deterministic feature extraction (reusing the C-4 contract) + Mahalanobis-distance
  inference + anomaly-map generation + governed output tensors + deterministic replay
  verification + production of InspectionPrediction under the existing contract +
  governed inference evidence only.
- Forbidden scope: all evaluation, all metrics (Image AUROC, Pixel AUROC, AUPRO,
  Precision, Recall, F1), threshold / operating-point derivation, calibration, benchmark
  generation, scientific and product claims, Trust / Review / Evidence Engine /
  Evaluation Engine changes, ONNX export, preprocessing changes, and any architecture
  change.
- Required outputs, commit policy, validation requirements, and scientific boundaries
  are defined.
- Nothing inferred, scored, evaluated, exported, or claimed by this checkpoint.
  No normative document modified.
```

---

## 8. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no inference** (no Mahalanobis scoring, no anomaly map, no `InspectionPrediction`
  produced)
- **no evaluation / metric / benchmark**
- **no thresholds / operating points**
- **no calibration**
- **no ONNX export**
- **no scientific or product claim**
- **no downstream code modified** (provider protocol, `transform_prediction`, Trust,
  Review, Evidence Engine, Evaluation Engine, integration, prototype UI all unchanged)
- **no documentation modified** (no ADR, Dataset Strategy, Evaluation Strategy, or
  Implementation Authorization change)
- **authorization planning only**

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document.

---

## 9. Next Natural Step

```text
Generate the bounded implementation prompt for C-5 — Governed PaDiM Inference.
```

No governing document is updated in this task. The persisted authorization checkpoint
must be reviewed before the implementation prompt is generated.
