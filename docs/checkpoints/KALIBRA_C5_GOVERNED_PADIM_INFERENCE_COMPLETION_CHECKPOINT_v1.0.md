# Kalibra C-5 Governed PaDiM Inference Completion Checkpoint v1.0

**Status:** Recorded — engineering-completion checkpoint (bounded C-5 governed inference completed; no evaluation, no metric, no threshold, no claim)
**Date:** 2026-07-05
**Repository baseline HEAD:** `9148e93 docs: authorize governed padim inference`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **completed C-5 Governed PaDiM Inference review** as a
versioned repository checkpoint. It is an engineering-completion artifact. It persists the
review that was produced after the C-5 implementation was written and validated. It does
not summarize the review, does not reinterpret it, and does not modify any ADR, Dataset
Strategy, Evaluation Strategy, or Implementation Authorization gate.

It records that the bounded scope authorized in the
[Governed PaDiM Inference Authorization Checkpoint](KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md)
has been implemented and validated against every authorized boundary. It authorizes
nothing further. It does **not** authorize C-6 Evaluation.

It draws its standing from the same lineage as the authorization checkpoint: the
[Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
(PaDiM selected first), the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
the [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
(`SELECTED — VisA`), the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
the [C-4 PaDiM Baseline Training Authorization Checkpoint](KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md),
the [C-4 PaDiM Baseline Training Completion Checkpoint](KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md),
and the recorded
[Governed PaDiM Inference Evidence](../evidence/KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md).

Throughout, **must**, **must not**, and **completed** carry the binding sense established
across the ML Phase 2 documents ([`AGENTS.md`](../../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)).

---

## 1. Decision

```text
PASS
```

All required validations pass. No must-fix or should-fix findings. The implementation
honors every C-5 governance boundary and the engineering philosophy (evidence before
assertion, reproducibility, honesty over capability, explicit boundaries, one source of
truth for inspection and trust qualification).

The C-5 governed PaDiM inference implementation **may be committed**.

---

## 2. Review Findings

- **No must-fix findings.**
- **No should-fix findings.**

Three observations are persisted below as engineering knowledge. None blocks commit.

### 2.1 O-1 — `predicted_judgement=DEFECT` is a contract artifact, not a classification

The `InspectionPrediction` contract (`src/inspection/domain.py`) requires that any
prediction carrying a `predicted_localization` must carry `predicted_judgement=DEFECT`
(`PartialInspectionPrediction` is raised otherwise). Because PaDiM inference always
produces a raw anomaly map and therefore always produces a localization, every C-5
prediction record carries `predicted_judgement: "defect"`.

This is **not** an OK/defect product or scientific classification. The implementation
records the policy explicitly as
`contract_required_defect_for_raw_localization_no_threshold_v1` in both
`inference_metadata.json` and every prediction record's `model_metadata`, and the evidence
file's Explicit Non-Claims section states this directly. No threshold was derived, no
operating point was selected, and the raw anomaly measure is not presented as confidence,
probability, trust, or a calibrated value.

- **This is acceptable for C-5.** The contract constraint is satisfied without claiming a
  classification.
- **Future C-6 evaluation must not retroactively read these `defect` judgements as
  classifications.** Evaluation must derive its own thresholded operating points from the
  raw anomaly measures and the recorded labels, and must keep the inference-layer
  `predicted_judgement` field separate from any evaluated classification.

### 2.2 O-2 — `verify_inference()` re-runs inference twice but does not re-derive training artifacts

The standalone `verify` command (`scripts/padim_inference.py verify`) re-executes the
goverened acquisition verification, re-loads and re-verifies the C-4 training artifacts by
hash, re-runs inference **twice** (the deterministic replay pair), and re-derives every
inference output hash against the recorded `artifact_hashes.json`. It does **not** re-fit
or re-derive the C-4 μ, Σ⁻¹, or feature indices; it consumes them as governed, hash-anchored
inputs and verifies the C-4 replay record's `status == "passed"`.

- **This is the correct division of responsibility.** Re-fitting is C-4's responsibility;
  C-5 only consumes governed training artifacts.
- **The complete C-5 replay lives in the `infer` path** (a full second inference run with
  byte-level comparison of feature tensors, anomaly maps, raw measures, localization,
  `InspectionPrediction` records, and hashes), and `verify` independently re-runs that
  same replay and re-checks the recorded hashes.

### 2.3 O-3 — Anomaly maps and prediction payloads are local-only; hashes are committable

The four large inference outputs
(`anomaly_maps/{validation,test}_anomaly_maps.npy`,
`predictions/{validation,test}_predictions.jsonl`) total roughly 227 MB and are correctly
gitignored by `data/visa/derived/padim/inference/*` with explicit re-includes for the
lightweight governed records (`metadata/**`, `replay/**`, `artifact_hashes.json`). The
full per-sample hashes for every one of the 6492 inputs are durably recorded inside the
committable `artifact_hashes.json`, and the first five per-input hashes are surfaced in
the evidence file.

- **This is the correct storage split.** Reproducibility is preserved by hashes; repository
  bloat is avoided.
- **Future re-derivation requires the governed source archive.** As with C-4, anyone
  re-running inference must first restore the governed VisA archive and the C-4 training
  artifacts; the recorded hashes then anchor byte-identical reproduction.

---

## 3. Required Changes

None.

---

## 4. Governed PaDiM Inference Governance Assessment

The implementation was verified against every governance boundary in the C-5
authorization and the task verify list.

### 4.1 Governed input consumption

- **Only the governed VisA acquisition was consumed.** `run_inference` and
  `verify_inference` both begin with `training.verify_governed_acquisition()`, which
  re-verifies the archive SHA-256, the per-file manifest, the provenance record, and all
  three split hashes against their governed identities before any sample is loaded.
- **Inference sample hashes and provenance were verified before inference.**
  `load_inference_samples` cross-checks every validation/test image row against
  `files.sha256`, confirms the file exists in the extracted tree, and requires the row's
  `source_image` to equal its `filename`. No inference ran without a verified input.

### 4.2 Governed training artifact consumption

- **Only governed C-4 PaDiM artifacts were consumed.** `load_governed_artifacts` reads
  `training/artifact_hashes.json`, verifies its schema, and then hash-verifies every
  array and metadata artifact it subsequently loads (`mu_by_class.npy`,
  `covariance_inverse_by_class.npy`, `feature_indices.npy`, and the six metadata records).
- **μ, Σ⁻¹, feature indices, preprocessing metadata, backbone metadata, numerical
  metadata, training metadata, and replay records were verified before inference.**
  `verify_recorded_training_artifacts` checks both the `array_artifacts` and
  `metadata_artifacts` sections; the C-4 training record's
  `artifact_hashes_record_sha256`, `training_metadata_sha256`, and
  `replay_verification_sha256` are all re-derived and cross-checked; and the C-4 replay
  record's `status == "passed"` is required.
- **C-4 scope boundaries were re-asserted.** The C-4 `training_metadata.json`
  `scope_boundaries` block is read and every closed-scope flag
  (`inference_executed`, `validation_inference_executed`, `test_inference_executed`,
  `evaluation_executed`, `benchmark_generated`, `onnx_exported`, `scientific_claim`)
  is required to be `false`, confirming C-5 consumes a strictly training-only baseline.
- **No fitting or retraining occurred.** No `fit_*`, `train_*`, or covariance-inversion
  routine is invoked anywhere in `scripts/padim_inference.py`. The training module is
  imported only for its deterministic feature-extraction contract
  (`extract_features`, `iter_batches`, `FitConfig`) and shared identifiers/paths.
- **No artifact mutation occurred.** μ, Σ⁻¹, and feature indices are loaded read-only and
  re-cast into fresh contiguous arrays; no governed file is written outside the
  `data/visa/derived/padim/inference/` subtree and the evidence file.

### 4.3 Deterministic feature extraction and anomaly scoring

- **Deterministic feature extraction reused the C-4 contract unchanged.** `infer_sample`
  calls `training.extract_features` with a default `FitConfig` and selects the governed
  feature indices `(0, 2, 5, 6, 7, 9, 12, 13)`, exactly the indices recorded in the C-4
  `feature_indices.json` and re-verified by `verify_loaded_array_contracts`.
- **Mahalanobis anomaly maps were generated.** `mahalanobis_patch_distances` computes
  per-patch `sqrt(diff · Σ⁻¹ · diff)` in float64 with a finite-value guard, and
  `anomaly_map_from_patch_distances` upsamples the patch grid to the full 64×64 map.
- **Raw anomaly measures were generated only as raw anomaly measures.**
  `aggregate_raw_anomaly_measure` returns the finite maximum of the anomaly map; the
  `raw_measure_kind` is `raw_anomaly_measure` and the `raw_measure_scale` is
  `model_raw_anomaly_measure` on every `InspectionPrediction`, exactly as fixed in
  `src/inspection/domain.py`.
- **Raw anomaly measures were not presented as confidence, probability, trust, or
  calibrated values.** The evidence file, the inference metadata `scope_boundaries`, and
  the prediction records all state this. `calibration_performed` is `false`.

### 4.4 Localization and prediction surface

- **Localization was generated deterministically from anomaly maps.**
  `localization_from_anomaly_map` derives a normalized bounding box from the pixels equal
  to the maximum anomaly value, identified as
  `padim_raw_anomaly_map_argmax_region_v1`. No threshold is applied.
- **`InspectionPrediction` records were generated under the existing contract.** Each
  prediction is constructed via `src.inspection.domain.InspectionPrediction` and therefore
  passes its `__post_init__` invariants (raw measure finite, raw kind/scale fixed,
  localization consistent with judgement). See O-1 for the contract-mandated
  `predicted_judgement`.
- **`RawInspectionResult` was not constructed.** No reference to `RawInspectionResult`
  appears in `scripts/padim_inference.py`.
- **`InspectionEngine.transform_prediction(...)` was not invoked.** No
  `InspectionEngine` import or call exists in the inference script. Only the four
  prediction-surface data types (`InspectionPrediction`, `InspectionJudgement`,
  `DefectLocalization`, `NormalizedBoundingBox`) are imported from `src.inspection.domain`.

### 4.5 Inference-vs-evaluation separation

- **Validation/test inference was executed only as inference, not evaluation.** Both
  splits are consumed solely to produce `InspectionPrediction` records and anomaly maps.
- **No metric was computed.** No AUROC, AUPRO, Precision, Recall, F1, or any other metric
  appears in the implementation. `metrics_generated` is `false`.
- **No threshold or operating point was derived.** No threshold search, ROC point
  selection, or operating-point derivation exists. `threshold_derived` and
  `operating_point_derived` are both `false`.
- **No OK/defect product or scientific classification was claimed.** See O-1.

### 4.6 Replay verification

- **Replay verification performed a complete second inference pass.** `run_inference`
  executes `execute_inference_run` twice in succession. `verify_inference` does the same.
- **Replay verification proves identical feature tensors, anomaly maps, raw measures,
  localization, `InspectionPrediction` records, and hashes.** `compare_inference_runs`
  compares all seven dimensions per sample and aggregate; any mismatch raises
  `InferenceError("deterministic replay mismatch: ...")`. The recorded replay record
  shows all comparisons `true`, `complete_second_inference_run: true`, and matching
  first/second-run output and sample-artifact hashes.

### 4.7 Scope integrity

- **No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration,
  prototype UI, provider interface, output mapping, or architecture code was modified.**
  `git status --short -- src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui`
  returns no output.
- **No scientific or product claim was introduced.** The evidence file's Explicit
  Non-Claims section states this directly, and the inference metadata `scope_boundaries`
  records `scientific_claim: false` and `product_claim: false`.

---

## 5. Git / Storage Assessment

### 5.1 Changed / added files

```text
M .gitignore
?? scripts/padim_inference.py
?? tests/test_padim_inference.py
?? docs/evidence/KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md
?? data/visa/derived/padim/inference/   (filtered by .gitignore)
```

### 5.2 `.gitignore` correctness

The `.gitignore` diff adds a `data/visa/derived/padim/inference/*` blanket ignore with
explicit re-includes for the lightweight governed records only:

```text
!data/visa/derived/padim/inference/
data/visa/derived/padim/inference/*
!data/visa/derived/padim/inference/metadata/
!data/visa/derived/padim/inference/metadata/**
!data/visa/derived/padim/inference/replay/
!data/visa/derived/padim/inference/replay/**
!data/visa/derived/padim/inference/artifact_hashes.json
```

- **Anomaly maps and prediction payloads are gitignored.** `git check-ignore -v` confirms
  `anomaly_maps/{test,validation}_anomaly_maps.npy` and
  `predictions/{test,validation}_predictions.jsonl` are all ignored (matched by the
  `inference/*` rule).
- **Metadata, replay records, hashes, and evidence are lightweight and committable.**
  `git check-ignore` confirms `metadata/inference_metadata.json`,
  `replay/replay_verification.json`, and `artifact_hashes.json` are **not** ignored. The
  evidence markdown under `docs/evidence/` is committable.

### 5.3 Whitespace and tree state

- `git diff --check` reports no whitespace errors.
- The working tree contains exactly the five entries listed in §5.1; no stray files.

---

## 6. Validation Summary

All commands were run from `/Users/agentisstudio/Documents/kalibra` on branch
`codex/initial-engineering-skeleton`.

| Command | Result |
| --- | --- |
| `python3 scripts/padim_inference.py verify` | `EXIT: 0` (pre-infer) |
| `python3 scripts/padim_inference.py infer` | `EXIT: 0` |
| `python3 scripts/padim_inference.py verify` | `VERIFY_EXIT: 0` (post-infer) |
| `python3 -m pytest -q` | `474 passed, 1 skipped in 11.27s` |
| `python3 -m compileall -q src tests scripts` | `COMPILEALL_EXIT: 0` |
| `git diff --check` | `DIFF_CHECK_EXIT: 0` (no whitespace errors) |
| `git status --short` | the five entries in §5.1 only |
| `git status --short -- src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui` | no output (downstream scope intact) |
| `git check-ignore -v <four large outputs>` | all four ignored |
| `git check-ignore <metadata/replay/artifact_hashes>` | none ignored (committable) |

The single skipped test is pre-existing and unrelated to C-5 (the suite contained 475
collected items, 474 passed, 1 skipped).

---

## 7. Completion Summary

C-5 completed **governed PaDiM inference only**:

- 6492 governed inference inputs scored across the validation (2164) and test (4328)
  splits of the governed VisA acquisition.
- Each input produced a deterministic float64 Mahalanobis anomaly map (upsampled to
  64×64), a raw anomaly measure (`padim_anomaly_map_max_v1`), a deterministic
  localization (`padim_raw_anomaly_map_argmax_region_v1`), and an `InspectionPrediction`
  record under the existing prediction contract.
- A complete second inference run was executed and proven byte-identical to the first
  across feature tensors, anomaly maps, raw measures, localization, prediction records,
  and hashes.
- Governed inference records (`artifact_hashes.json`, `metadata/*`, `replay/*`) and the
  evidence markdown were written and are committable; large outputs are local-only and
  hash-anchored.

---

## 8. Explicit Non-Claims

This checkpoint explicitly records that:

- **C-5 completed governed inference only.**
- **Inference is not evaluation.** No evaluation was executed.
- **No metrics were generated.** No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall,
  F1, metric, or benchmark was produced.
- **No threshold or operating point was derived.** The `predicted_judgement=DEFECT` field
  on every `InspectionPrediction` is a contract artifact
  (`contract_required_defect_for_raw_localization_no_threshold_v1`), not a thresholded
  classification.
- **No benchmark was generated.**
- **No calibration was performed.** The raw anomaly measure is not a probability, not
  confidence, and not trust.
- **No ONNX export was produced.**
- **No fitting, retraining, artifact mutation, or preprocessing change was performed.**
- **No scientific claim was made.** This inference record does not state that Kalibra
  detects defects.
- **No product claim was made.**
- **No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration, prototype
  UI, provider interface, output mapping, or architecture code was modified.**
- **C-6 Evaluation remains unauthorized.**

---

## 9. Commit Authorization

The C-5 governed PaDiM inference implementation **may be committed** by the repository
owner. The commit remains the repository owner's exclusive responsibility under the Git
Rules in [`AGENTS.md`](../../AGENTS.md); this checkpoint records engineering readiness
only and performs no git operation.

---

## 10. Next Natural Step

Review this persisted C-5 completion checkpoint before authorizing **C-6 Evaluation**.

C-6 Evaluation remains unauthorized. Any C-6 work must be preceded by its own
authorization checkpoint that fixes the evaluation procedure on the frozen test split,
selects the metric set under the Evaluation Strategy, and explicitly addresses the
inference-vs-evaluation separation noted in O-1 (evaluation must derive its own
thresholded operating points from the raw anomaly measures and recorded labels, and must
not retroactively read the inference-layer `predicted_judgement` field as a
classification).
