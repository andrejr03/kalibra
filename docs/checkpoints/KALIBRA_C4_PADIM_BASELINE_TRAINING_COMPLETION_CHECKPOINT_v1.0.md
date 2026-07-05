# Kalibra C-4 PaDiM Baseline Training Completion Checkpoint v1.0

**Status:** Recorded — engineering-completion checkpoint (bounded C-4 training completed; no inference, no evaluation, no claim)
**Date:** 2026-07-05
**Repository baseline HEAD:** `3f728e3 docs: authorize padim baseline training`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **completed C-4 PaDiM Baseline Training review** as a
versioned repository checkpoint. It is an engineering-completion artifact. It persists
the review that was produced after the C-4 implementation was written and validated. It
does not summarize the review, does not reinterpret it, and does not modify any ADR,
Dataset Strategy, Evaluation Strategy, or Implementation Authorization gate.

It records that the bounded scope authorized in the
[PaDiM Baseline Training Authorization Checkpoint](KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md)
has been implemented and validated against every authorized boundary. It authorizes
nothing further. It does not authorize C-5.

It draws its standing from the same lineage as the authorization checkpoint: the
[Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
(PaDiM selected first), the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
the [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
(`SELECTED — VisA`), the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
and the recorded
[PaDiM Baseline Training Evidence](../evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md).

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
honors every C-4 governance boundary and the engineering philosophy (evidence before
assertion, reproducibility, honesty over capability, explicit boundaries).

---

## 2. Review Findings

- **No must-fix findings.**
- **No should-fix findings.**

Three observations are persisted below as engineering knowledge. None blocks commit.

### 2.1 O-1 — `verify_training()` is intentionally lighter than the full replay

`verify_training()` (the standalone `verify` command in
`scripts/train_padim_baseline.py`) is intentionally lighter than the full replay executed
by `train`. The standalone `verify` re-derives only three artifacts (`mu_by_class`,
`covariance_inverse_by_class`, `feature_indices`) against recomputed hashes, and reads the
previously-written `replay_verification.json` `status` field. It does **not** re-verify the
full Σ, feature tensors, conditioning, sample counts, or re-run the second fit.

The task's "verify → train → verify" sequence passes because `train` itself performs the
complete replay and writes self-consistent records; `verify` is a lighter integrity check,
not a full independent re-fitting.

- **This is acceptable for C-4.** The durable, complete replay lives in the `train` path
  and in `replay_verification.json`.
- **Future C-5/C-6 verification should decide whether stronger verification is required.**
  Whoever defines the next verification bar should decide whether the standalone `verify`
  command must independently re-fit and re-compare the full Σ, feature tensors,
  conditioning, and sample counts, rather than trusting the recorded replay record.

### 2.2 O-2 — Derived artifacts use `artifact_hashes.json` rather than sidecar `.sha256` files

Unlike `data/visa/manifests/splits/*.csv.sha256` and `files.sha256.sha256` written by the
acquisition stage, the derived PaDiM artifacts (μ, Σ, Σ⁻¹, feature tensors, training and
metadata JSON) carry their hashes only **inside**
`data/visa/derived/padim/training/artifact_hashes.json`, not as co-located sidecar
`.sha256` files. `verify_record_hash` (which *does* expect sidecars) is used only for the
upstream governed inputs, never for the derived outputs.

- **Acquisition and training use different integrity conventions.**
- **This is acceptable** — hashes are durably recorded and cross-referenced inside the
  governed training records.
- **Future phases may choose to unify the convention.** A later checkpoint may decide
  whether derived artifacts should also emit co-located sidecar hashes for symmetry with
  the acquisition stage.

### 2.3 O-3 — Training timestamp pinning keeps replay byte-stable (engineering note)

`training_timestamp_for_run` (`scripts/train_padim_baseline.py`) freezes the training
timestamp on the second run to the first run's recorded value. This keeps
`training_record.json`, `training_metadata.json`, and the evidence file byte-stable across
replays, because the evidence file is otherwise governed by `write_governed_bytes` (which
fails-closed if a governed record would change).

Persisted as an engineering note. The only unstabilized field in the evidence markdown is
`Date:` (date-only, ISO), which only changes day-to-day.

---

## 3. Governance Assessment

Every governance checkpoint authorized for C-4 was verified.

### 3.1 Governed dataset verification

- Only the governed VisA acquisition was consumed. `verify_archive_hash` +
  `verify_files_manifest` + `verify_governed_acquisition` re-check the archive SHA-256, the
  files manifest SHA-256, all per-file hashes against `files.sha256`, and validate
  provenance.
- Archive / files manifest / split / provenance hashes are verified **before** fitting.
  `verify_governed_acquisition` runs before `load_train_samples` in `run_training`.
- All five governed SHAs match the known values:
  - `archive_sha256 = 2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362`
  - `files_manifest_sha256 = a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c`
  - `train_split_sha256 = 9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736`
  - `validation_split_sha256 = 79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5`
  - `test_split_sha256 = 2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510`
  - `provenance_sha256 = 01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0`

### 3.2 Train-only consumption

- Only `train.csv` was consumed. `load_train_samples` opens only
  `data/visa/manifests/splits/train.csv`; no other split is read into the fit path.
- Validation samples consumed = **0**. Test samples consumed = **0**. Hard-coded as
  `validation_samples_loaded: 0` and `test_samples_loaded: 0` in `train_split_use.json`.
- `train.csv` was independently confirmed to contain 3,849 rows, all `label = normal`,
  all `source_label = normal`, 12 classes, all `artifact_type = image`.

### 3.3 All train samples are normal

`validate_train_row` rejects:
- any `label != normal`;
- any `source_label != normal`;
- any non-empty `source_mask`;
- any non-`1cls.csv` upstream source;
- any non-image artifact;
- any hash mismatch between `files.sha256` and the train manifest row;
- any image missing from the extracted dataset.

The 3,849 normal train samples decompose upstream as `train = 3489`, `test = 360` in
upstream provenance, with all rows carrying Kalibra `label = normal`. Upstream
`source_split` is preserved only as provenance, never as a training-path branch.

### 3.4 Deterministic feature extraction

- Backbone identity: `kalibra-fixed-patch-feature-backbone-v1`.
- Backbone layer: `fixed_patch_statistics_64x64_patch8`.
- Preprocessing contract id: `kalibra-padim-rgb64-bilinear-float64-patch8-v1`.
- RGB → 64×64 bilinear → float64 in [0, 1] → fixed patch statistics (mean/std for RGB,
  grayscale, gradient x, gradient y, gradient magnitude) over 8×8 patches.
- `extract_features` and `patch_mean_std` are pure functions; replay confirms identical
  feature tensors per class across the two fits.
- Full feature dimension: 14. Selected feature dimension: 8. Patch grid: (8, 8).

### 3.5 Deterministic feature selection

- `FEATURE_SUBSAMPLE_SEED = 271828`, recorded and used.
- Threaded through `FitConfig` → `select_feature_indices`, which uses a single
  `np.random.default_rng(seed)` and returns `np.sort(rng.choice(...))`.
- Selected feature indices: `[0, 2, 5, 6, 7, 9, 12, 13]`.
- Recorded in `feature_indices.json`, `training_metadata.json`, and the evidence file.
- Replay confirms `np.array_equal(first, second)` and records the SHA-256 of the index
  array.

### 3.6 Deterministic μ

- μ generated at `data/visa/derived/padim/statistics/mu_by_class.npy`.
- Per-class, per-patch mean over the selected feature dimension.
- Replay confirms identical μ across the two fits, both by `np.array_equal` and by SHA-256
  of the serialized array.

### 3.7 Deterministic Σ

- Σ generated at `data/visa/derived/padim/covariance/covariance_by_class.npy`.
- Sample covariance, `centered.T @ centered / (n - 1)`, regularized as `Σ + εI` with
  `ε = 0.001`.
- Covariance conditioning (max before, max after, mean after regularization) is recorded
  per class in `training_metadata.json`.
- Replay confirms identical Σ across the two fits.

### 3.8 Deterministic Σ⁻¹

- Σ⁻¹ generated at `data/visa/derived/padim/covariance/covariance_inverse_by_class.npy`.
- Computed via `numpy.linalg.inv` on the regularized covariance.
- All inverse entries finite (verified by tests and by replay).
- Replay confirms identical Σ⁻¹ across the two fits, both by `np.array_equal` and by
  SHA-256 of the serialized array.

### 3.9 Replay verification

- The replay is a **complete second fit**. `replay_verify` calls `fit_padim(samples,
  config)` a second time — a full re-extraction and re-fit over all 12 classes.
- The replay asserts identity of feature indices, feature tensors, μ, Σ, Σ⁻¹, plus hash
  agreement on μ and Σ⁻¹.
- `replay_verification.json` records `complete_second_fit: true` and all seven comparisons
  as `true`, with per-class feature-tensor hashes and the four core array hashes.

### 3.10 Absence of inference

- No inference was executed. No validation inference. No test inference.
- Grep for forbidden scope in the script returns only non-claim declarations
  (`scope_boundaries`, `non_claims`, evidence prose).
- No `predict`, `score`, or any inference symbol exists in the script.
- `scope_boundaries` in `training_metadata.json` records `inference_executed: false`,
  `validation_inference_executed: false`, `test_inference_executed: false`.

### 3.11 Absence of evaluation

- No evaluation was executed. `scope_boundaries` records `evaluation_executed: false`.
- The C-2 evaluation protocol remains fixed but **deliberately not invoked** by C-4.

### 3.12 Absence of benchmark

- No benchmark was generated. `scope_boundaries` records `benchmark_generated: false`.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, threshold, calibration, or
  product metric was computed.

### 3.13 Absence of scientific claim

- No scientific claim was made. The evidence file explicitly states that the training
  record "makes no scientific claim and does not state that Kalibra detects defects."
- The backbone is honestly labeled `kalibra-fixed-patch-feature-backbone-v1` with
  `pretrained_external_weights: false` and a provenance note that all feature extraction is
  deterministic local code with no external model weights.
- `scope_boundaries` records `scientific_claim: false`.

---

## 4. Git / Storage Assessment

### 4.1 Gitignore assessment

- `.gitignore` change is correct and well-constructed. It inverts the previous blanket
  ignore of `data/visa/derived/` and replaces it with a narrow allowlist.
- Large tensors (`statistics/`, `covariance/`, `evidence/`) are explicitly re-ignored.
- Only `padim/training/**` and `padim/metadata/**` are committable.
- `git check-ignore -v` confirms `mu_by_class.npy`, `covariance_by_class.npy`,
  `covariance_inverse_by_class.npy`, and every `feature_tensors/*.npy` are **IGNORED**.

### 4.2 Local-only tensors

- Verified via `git add -n -A` that a repository-owner `git add -A` would stage **only**
  the ten governed JSON records (~19.6 KB total) plus the script, the test, the evidence
  markdown, and `.gitignore`, and **zero `.npy` files under any path**.

### 4.3 Committable metadata

The following ten governed JSON records are the committable training/metadata surface:

```text
data/visa/derived/padim/metadata/backbone_metadata.json
data/visa/derived/padim/metadata/dataset_identity.json
data/visa/derived/padim/metadata/feature_indices.json
data/visa/derived/padim/metadata/numerical_config.json
data/visa/derived/padim/metadata/preprocessing_contract.json
data/visa/derived/padim/metadata/train_split_use.json
data/visa/derived/padim/metadata/training_metadata.json
data/visa/derived/padim/training/artifact_hashes.json
data/visa/derived/padim/training/replay_verification.json
data/visa/derived/padim/training/training_record.json
```

Plus the evidence report at
`docs/evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md`.

### 4.4 Downstream isolation

- Downstream scope check produced **no output** for `src/inspection`, `src/frameworks`,
  `src/trust`, `src/review`, `src/evidence`, `src/evaluation`, `src/integration`,
  `src/prototype_ui`.
- No provider, preprocessing runtime, output mapping, Trust, Review, Evidence Engine,
  Evaluation Engine, integration, or prototype UI code was modified.

### 4.5 Large tensor handling

- `mu_by_class.npy` ≈ 49 KB.
- `covariance_by_class.npy` ≈ 384 KB.
- `covariance_inverse_by_class.npy` ≈ 384 KB.
- `feature_tensors/*.npy` ≈ 1.6 MB each × 12 classes.

These tensors are regenerable from the governed acquisition and the pinned seed and remain
local. The size profile confirms the ignore decision is load-bearing, not cosmetic.

---

## 5. Validation Summary

All required validations passed:

| Command | Result |
|---|---|
| `python3 scripts/train_padim_baseline.py verify` | exit 0 |
| `python3 scripts/train_padim_baseline.py train` | exit 0 |
| `python3 scripts/train_padim_baseline.py verify` (post-train) | exit 0 |
| `python3 -m pytest -q` | 470 passed, 1 skipped (pre-existing skip) |
| `python3 -m compileall -q src tests scripts` | exit 0 |
| `git diff --check` | clean |
| Downstream scope check (`git status --short -- src/{inspection,frameworks,trust,review,evidence,evaluation,integration,prototype_ui}`) | no output (correct) |
| Large-tensor gitignore check (`git check-ignore -v` for μ, Σ, Σ⁻¹) | all three paths IGNORED |

Per `AGENTS.md` Git Rules, no `git add`, `git commit`, or `git push` was executed. Those
are reserved for the repository owner.

---

## 6. Completion Summary

```text
C-4 PaDiM Baseline Training completed successfully.
```

- Deterministic baseline artifacts exist (μ, Σ, Σ⁻¹, feature indices, feature tensors) for
  all 12 VisA classes.
- Replay verification succeeded — a complete second fit reproduced identical feature
  selection, feature tensors, μ, Σ, and Σ⁻¹.
- Governed training records exist (`training_record.json`, `artifact_hashes.json`,
  `replay_verification.json`, `training_metadata.json`, plus the per-aspect metadata
  records).
- No inference was executed.
- No evaluation was executed.
- No metrics were generated.
- No benchmark was generated.
- No scientific claim was made.

The C-4 implementation may be committed.

---

## 7. Scope Boundaries and Explicit Non-Claims

This completion checkpoint records, for the C-4 implementation it persists:

- **no inference** (no validation inference, no test inference)
- **no ONNX export**
- **no evaluation**
- **no calibration**
- **no thresholds**
- **no product claim**
- **no scientific claim**
- **no downstream code modified** (provider, preprocessing runtime, output mapping, Trust,
  Review, Evidence Engine, Evaluation Engine, integration, prototype UI all unchanged)

Kalibra does **not** yet perform real defect detection, and this completion checkpoint
does not change that. A fitted μ / Σ⁻¹ artifact is a prepared model input, not proof that
Kalibra detects defects.

---

## 8. Next Natural Step

```text
Review this checkpoint.

After approval:

Generate the authorization checkpoint for the next capability phase.

Do not begin C-5 until that authorization exists.
```

No governing document is updated by this task. No ADR, Dataset Strategy, Evaluation
Strategy, or Implementation Authorization gate is modified. The persisted completion
checkpoint must be reviewed before any further capability phase is authorized.
