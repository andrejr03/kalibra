# Kalibra PaDiM ONNX Export Equivalence Evidence v1.0

**Status:** Recorded - deterministic offline ONNX export-equivalence evidence only
**Date:** 2026-07-07
**Scope:** Phase 3 / Task 2 - Export Equivalence Verification only

## Verification Scope

- Equivalence label: `visa-padim-onnx-export-equivalence-v1`
- Verified artifact: `artifacts/padim/model.onnx`
- Equivalence report: `artifacts/padim/equivalence/equivalence_report.json`
- Equivalence hashes: `artifacts/padim/equivalence/equivalence_hashes.json`
- Equivalence replay: `artifacts/padim/equivalence/equivalence_replay.json`
- Execution path: direct `onnxruntime.InferenceSession` with `CPUExecutionProvider`.
- Runtime provider loaded: `false`
- Model loader loaded: `false`
- Runtime integration performed: `false`

## Artifact Verification

- Model SHA-256 verified: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Artifact record SHA-256 verified: `6d6768cbd13d0a26dbfb817e676fc5ccddbb878b72f18e443dc403b531052f4f`
- Metadata record SHA-256 verified: `3dd299292c32a7d6616171ce26dd6d07a3d1c313dfc4dd00ea583dbca313f00d`
- Export replay SHA-256 verified: `e2d7f28ed2412a509e384ad50509fc8e73d4f1347349683e4f89a4071be27093`
- Artifact hashes record SHA-256 verified: `d2e36f0ed4b6bd71c15fb4ce49c2481b5f1af4edc7b0ee034dc76386deed38c6`
- Opset verified: `18`
- ONNX IR version verified: `10`
- Export replay status verified: `passed`

## Reference Verification

- Governed C-4 training identity verified: `7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048`
- Mu hash verified: `51568c211c324b9178837f0d862c01a9601dc3d3daa474c959bb32ef5758446b`
- Covariance inverse hash verified: `893af9e08d3543b5bd973ab913c1f2e8ed57d26a1bbb225b194d525cfc8df7b3`
- Feature indices hash verified: `1ca5583a7b498b4849e42717f24ebcf82d82a6c545b852814ada12b5c287cbe3`
- Training metadata hash verified: `c0178d823d0c440102c768f75799340586bd4c428bfa309862e8fb658b0ffad9`
- Governed C-5 inference identity verified: `c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf`
- C-5 anomaly-map hashes verified: `validation=bdea53e85561e830ab1b45430f0df16e6769e9092124217fe5827ee30ac3d97d`, `test=21a959c9891815ea73ee7e23a47a1b4c15be18047ad58e2b721a7c24cdc15a9d`
- C-5 prediction hashes verified: `validation=ebef96fad1a665e9e2cd4c2e9855f93f238b8a71a41971c56efbabd3ba5314c4`, `test=35e2a8426a8e1bb59f8327f657eff79892dbbbad825acf19debee2a6436f8436`
- C-5 metadata hash verified: `78e8408534863096315a07f21da33265f970e44f369a9fa3e35743f2adea372f`
- C-5 replay hash verified: `e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c`

## Graph Contract Verification

- Inputs verified: `full_patch_features float64 [1, 64, 14]`; `class_index int64 [1]`
- Outputs verified: `patch_mahalanobis_distances float64 [1, 64]`; `anomaly_map float64 [1, 64, 64]`; `raw_anomaly_measure float64 [1]`; `argmax_region float64 [1, 4]`
- Feature indices verified: `[0, 2, 5, 6, 7, 9, 12, 13]`
- Mu byte-equal to governed C-4: `true`
- Covariance inverse byte-equal to governed C-4: `true`
- Preprocessing contract verified: `kalibra-padim-rgb64-bilinear-float64-patch8-v1`
- Graph implements image preprocessing: `false`

## Equivalence Result

- Final status: `passed`
- Sample count: `6492`
- Validation count: `2164`
- Test count: `4328`
- Anomaly-map max absolute deviation: `7.105427357601002e-15`
- Anomaly-map max relative deviation: `3.586867160478407e-15`
- Raw-measure max absolute deviation: `7.105427357601002e-15`
- Raw-measure max relative deviation: `3.586867160478407e-15`
- Localization max absolute deviation: `0.0`
- Tolerance policy: `{'absolute': 1e-12, 'relative': 1e-12, 'bbox_absolute': 0.0, 'declared_before_comparison': True, 'justification': {'absolute': 'Task 1 demonstrated DOUBLE CPUExecutionProvider reproduction of the governed offline float64 PaDiM computation across 6,492 samples at machine-epsilon deviation; 1e-12 preserves that established regime without silently widening it.', 'relative': 'The same Task 1 evidence established max relative deviation below 1e-12 for anomaly maps and raw measures; Task 2 keeps the regime.', 'bbox_absolute': 'The localization coordinates are multiples of 1/64, and the recorded C-5 rounded values are exact for those coordinates; zero tolerance is therefore an equality requirement, not a widened tolerance.'}}`

## Replay Result

- Complete second equivalence run executed: `true`
- Per-sample deviations identical: `true`
- Per-split maxima identical: `true`
- Global maxima identical: `true`
- Pass/fail status identical: `true`
- Equivalence report hash identical: `true`
- Equivalence hashes record deterministic: `true`
- Equivalence report SHA-256: `9741a1c77a5d0696e8c1c5d2687aed82270d0b9791492b0b47032bf70c69275d`
- Equivalence replay SHA-256: `ef918b15edde5d07ae3f9889c014ef6647f8e2035d9f5e15fd876ef4e736a114`
- Equivalence hashes record SHA-256: `fec7ea31a3c5969d708820394c74f5a7b9b306b5287624508f40bf0bef63ffaa`

## Explicit Non-Claims

- Export equivalence is not runtime equivalence.
- Export equivalence is not runtime integration.
- Export equivalence is not scientific evaluation.
- No runtime provider was loaded.
- No runtime code was modified.
- No provider code was modified.
- No model-loader code was modified.
- No output-mapping code was modified.
- No preprocessing code was modified.
- No feature-extraction code was modified.
- No metrics were generated.
- No calibration was performed.
- No scientific claim was made.
- No product claim was made.
