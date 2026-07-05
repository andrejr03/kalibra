# Kalibra PaDiM Baseline Training Evidence v1.0

**Status:** Recorded — deterministic offline PaDiM fitting evidence only
**Date:** 2026-07-05
**Scope:** C-4 PaDiM baseline training only

## Governed Dataset Identity

- Dataset: VisA governed proxy acquisition `visa-acq-v1`
- Archive SHA-256: `2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362`
- Files manifest SHA-256: `a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c`
- Train split SHA-256: `9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736`
- Validation split SHA-256 recorded for identity only: `79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5`
- Test split SHA-256 recorded for identity only: `2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510`
- Provenance SHA-256: `01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0`

## Train Split Only

- Training manifest consumed: `data/visa/manifests/splits/train.csv`
- Normal train samples consumed: `3849`
- Validation samples consumed: `0`
- Test samples consumed: `0`
- Class distribution: `{'candle': 400, 'capsules': 241, 'cashew': 200, 'chewinggum': 201, 'fryum': 200, 'macaroni1': 400, 'macaroni2': 400, 'pcb1': 401, 'pcb2': 401, 'pcb3': 403, 'pcb4': 402, 'pipe_fryum': 200}`

## Deterministic Feature Extraction

- Backbone identity: `kalibra-fixed-patch-feature-backbone-v1`
- Backbone layer: `fixed_patch_statistics_64x64_patch8`
- Preprocessing contract id: `kalibra-padim-rgb64-bilinear-float64-patch8-v1`
- Full feature dimension: `14`
- Selected feature dimension: `8`
- Patch grid: `(8, 8)`
- Deterministic batch size: `16`

## Deterministic Feature Subsampling

- Feature subsampling seed: `271828`
- Selected feature indices: `[0, 2, 5, 6, 7, 9, 12, 13]`

## PaDiM Fitting

- μ generated: `data/visa/derived/padim/statistics/mu_by_class.npy`
- Σ generated: `data/visa/derived/padim/covariance/covariance_by_class.npy`
- Σ^-1 generated: `data/visa/derived/padim/covariance/covariance_inverse_by_class.npy`
- Covariance regularization: `Σ + εI`
- ε: `0.001`
- Numerical configuration: `data/visa/derived/padim/metadata/numerical_config.json`
- Training timestamp: `2026-07-05T16:07:14Z`

## Replay Verification

- Complete second fit executed: `true`
- Identical feature selection: `true`
- Identical feature tensors: `true`
- Identical μ: `true`
- Identical Σ^-1: `true`
- Identical hashes: `true`
- Replay record: `data/visa/derived/padim/training/replay_verification.json`

## Generated Governed Training Records

- Training record SHA-256: `7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048`
- Artifact hashes record SHA-256: `00c625060c6e50fe7ab1da76125e3891d8be7e52838c846eaba52813461eeb32`
- Training metadata SHA-256: `c0178d823d0c440102c768f75799340586bd4c428bfa309862e8fb658b0ffad9`
- Replay verification SHA-256: `dc5f66ee17533518489c893358cb30b8dd622277b5f38e21c0a0dd6e67fdd55f`

## Explicit Non-Claims

- No inference was executed.
- No validation inference was executed.
- No test inference was executed.
- No evaluation was executed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, threshold, calibration, benchmark, or product metric was computed.
- No ONNX export was produced.
- No provider, preprocessing runtime, output mapping, Trust, Review, Evidence Engine, Evaluation Engine, integration, prototype UI, runtime, or architecture code was modified.
- This training record makes no scientific claim and does not state that Kalibra detects defects.
