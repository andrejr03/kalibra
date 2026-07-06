# Kalibra Scientific Evaluation Evidence v1.0

**Status:** Recorded — governed single-seed scientific evaluation evidence
**Date:** 2026-07-05
**Scope:** C-6 Scientific Evaluation only

## Dataset Identity

- Dataset: VisA governed proxy acquisition `visa-acq-v1`
- Archive SHA-256: `2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362`
- Files manifest SHA-256: `a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c`
- Train split SHA-256: `9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736`
- Validation split SHA-256: `79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5`
- Test split SHA-256: `2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510`
- Provenance SHA-256: `01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0`

## Model Identity

- Training label: `visa-padim-baseline-fit-v1`
- Training record SHA-256: `7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048`
- Training artifact hashes SHA-256: `00c625060c6e50fe7ab1da76125e3891d8be7e52838c846eaba52813461eeb32`
- Training replay SHA-256: `dc5f66ee17533518489c893358cb30b8dd622277b5f38e21c0a0dd6e67fdd55f`
- Mu artifact SHA-256: `51568c211c324b9178837f0d862c01a9601dc3d3daa474c959bb32ef5758446b`
- Covariance inverse artifact SHA-256: `893af9e08d3543b5bd973ab913c1f2e8ed57d26a1bbb225b194d525cfc8df7b3`
- Feature indices artifact SHA-256: `1ca5583a7b498b4849e42717f24ebcf82d82a6c545b852814ada12b5c287cbe3`
- Feature subsampling seed: `271828`

## Inference Identity

- Inference label: `visa-padim-governed-inference-v1`
- Inference artifact hashes SHA-256: `c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf`
- Inference replay SHA-256: `e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c`
- Aggregation identifier: `padim_anomaly_map_max_v1`
- Localization identifier: `padim_raw_anomaly_map_argmax_region_v1`

## Official Metrics

- Image AUROC (primary, macro mean beside per-class table): `0.757826`
- Pixel AUROC (secondary, macro mean beside per-class table): `0.865196`
- AUPRO (secondary, macro mean beside per-class table): `0.555765`

Pixel AUROC is reported with AUPRO because normal-background dominance can inflate Pixel AUROC.

| Class | N | Normal | Anomaly | Image AUROC | Pixel AUROC | AUPRO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| candle | 440 | 400 | 40 | 0.785750 | 0.762630 | 0.390396 |
| capsules | 281 | 241 | 40 | 0.509647 | 0.765898 | 0.340064 |
| cashew | 240 | 200 | 40 | 0.763375 | 0.949214 | 0.631020 |
| chewinggum | 241 | 201 | 40 | 0.635697 | 0.782026 | 0.396828 |
| fryum | 240 | 200 | 40 | 0.784750 | 0.905844 | 0.529413 |
| macaroni1 | 440 | 400 | 40 | 0.730563 | 0.799483 | 0.478572 |
| macaroni2 | 440 | 400 | 40 | 0.639188 | 0.843014 | 0.506723 |
| pcb1 | 442 | 402 | 40 | 0.892600 | 0.927967 | 0.676397 |
| pcb2 | 440 | 400 | 40 | 0.939937 | 0.906200 | 0.688384 |
| pcb3 | 442 | 402 | 40 | 0.759950 | 0.915235 | 0.673536 |
| pcb4 | 442 | 402 | 40 | 0.909826 | 0.877148 | 0.678214 |
| pipe_fryum | 240 | 200 | 40 | 0.742625 | 0.947693 | 0.679637 |

## Diagnostic Metrics

Diagnostic only.

- Precision: `0.209019`
- Recall: `0.714583`
- F1: `0.323432`
- True positives: `343`
- False positives: `1298`
- True negatives: `2550`
- False negatives: `137`

| Class | Precision | Recall | F1 | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| candle | 0.225490 | 0.575000 | 0.323944 | 23 | 79 | 321 | 17 |
| capsules | 0.147860 | 0.950000 | 0.255892 | 38 | 219 | 22 | 2 |
| cashew | 0.301075 | 0.700000 | 0.421053 | 28 | 65 | 135 | 12 |
| chewinggum | 0.288136 | 0.425000 | 0.343434 | 17 | 42 | 159 | 23 |
| fryum | 0.340909 | 0.750000 | 0.468750 | 30 | 58 | 142 | 10 |
| macaroni1 | 0.173333 | 0.650000 | 0.273684 | 26 | 124 | 276 | 14 |
| macaroni2 | 0.093750 | 0.975000 | 0.171053 | 39 | 377 | 23 | 1 |
| pcb1 | 0.250000 | 0.800000 | 0.380952 | 32 | 96 | 306 | 8 |
| pcb2 | 0.360825 | 0.875000 | 0.510949 | 35 | 62 | 338 | 5 |
| pcb3 | 0.200000 | 0.525000 | 0.289655 | 21 | 84 | 318 | 19 |
| pcb4 | 0.382716 | 0.775000 | 0.512397 | 31 | 50 | 352 | 9 |
| pipe_fryum | 0.353846 | 0.575000 | 0.438095 | 23 | 42 | 158 | 17 |

## Operating Point

- Derivation rule: `Minimize absolute validation false-positive-rate / false-negative-rate gap; tie-break by lower maximum error rate, lower total error count, then higher threshold.`
- Validation-derived value: `2.445569`

Not calibrated.
Not a product threshold.

## Failure Analysis

- False positives: `1298`
- False negatives: `137`
- Localization failures: `237`
- Boundary-case rule: `closest_absolute_raw_measure_margin_per_class_v1`

| Class | FP | FN | Localization failures | Boundary cases |
| --- | ---: | ---: | ---: | ---: |
| candle | 79 | 17 | 17 | 10 |
| capsules | 219 | 2 | 35 | 10 |
| cashew | 65 | 12 | 24 | 10 |
| chewinggum | 42 | 23 | 12 | 10 |
| fryum | 58 | 10 | 13 | 10 |
| macaroni1 | 124 | 14 | 23 | 10 |
| macaroni2 | 377 | 1 | 33 | 10 |
| pcb1 | 96 | 8 | 21 | 10 |
| pcb2 | 62 | 5 | 19 | 10 |
| pcb3 | 84 | 19 | 13 | 10 |
| pcb4 | 50 | 9 | 9 | 10 |
| pipe_fryum | 42 | 17 | 18 | 10 |

Localization observations are based on true-positive anomaly images where the governed C-5 predicted box has zero overlap with the resized governed pixel mask. Boundary cases are the closest raw-measure margins to the validation-derived operating point and are raw-measure behavior only, not uncertainty quality.

## Proxy-Domain Limitations

- VisA is a governed proxy dataset, not Kalibra's domain of record.
- VisA is not a cast-aluminium, CNC-machining, gearbox-housing, or metal-part inspection dataset.
- The evaluation supports no production claim and no cross-domain generalization claim.
- PaDiM is alignment-sensitive; pose or registration differences remain an active risk for future metal-part domains.
- VisA upstream annotation-process documentation is incomplete, limiting localization interpretation.

## Scientific Limitations

- Single-seed evaluation only.
- No variance estimation.
- No confidence intervals.
- VisA is a governed proxy dataset.
- No production claim.
- No cross-domain claim.
- No calibrated-confidence claim.
- No benchmark, ranking, leaderboard, or state-of-the-art claim.
- No uncertainty, abstention, review-routing, or drift claim.

## Replay

- Deterministic evaluation replay: `passed`
- Identical metrics: `true`
- Identical operating point: `true`
- Identical failure analysis: `true`
- Identical reports: `true`
- Identical hashes: `true`

## Explicit Scope Checks

- No retraining.
- No refitting.
- No re-inference.
- No preprocessing change.
- No feature-extraction change.
- No provider change.
- No output-mapping change.
- No calibration.
- No ONNX export.
- No product threshold.
- No downstream architecture modification.
