# Kalibra Runtime Equivalence Verification Evidence v1.0

**Status:** Recorded - governed runtime-equivalence verification evidence only
**Date:** 2026-07-07
**Scope:** Phase 3 / Task 4 - Runtime Equivalence Verification only

## Verification Scope

- Canonical runtime path executed: `OnnxInspectionInferenceProvider().predict(StabilizedInspectionInput)`
- Runtime substrate: `model_loader.load_governed_model` -> `ProviderPrivateInferenceSession`
- Execution provider: `CPUExecutionProvider`
- Session configuration hash: `2893fd1fc592cb831bfccd9d53c3e784a5aba4ffdfbb58ad4de32eb512c4a2e4`
- Model reference id: `kalibra-padim-onnx-export-v1`
- Model SHA-256: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Runtime-equivalence report: `artifacts/runtime/equivalence/runtime_equivalence_report.json`
- Runtime-equivalence hashes: `artifacts/runtime/equivalence/runtime_equivalence_hashes.json`
- Runtime-equivalence replay: `artifacts/runtime/equivalence/runtime_equivalence_replay.json`

## Governed References Verified

- Governed C-5 inference identity verified: `c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf`
- Governed C-5 replay hash verified: `e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c`
- Governed C-6 identity verified: `02ebf0ba9da0ab1c747cce4218d0685094a7c39908a4f21b5af2075f2110b1f9`
- Task 1 governed ONNX artifact identity verified: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Task 2 export-equivalence identity verified before runtime equivalence: `true`
- Task 3 runtime integration identity verified: `5e885feb6ada4585a0c295b3935a0d1c73ce2753dd7a1227adad63953fae2757`

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
- `InspectionPrediction` contract verified: `true`
- Expected-by-design `raw_measure_scale` difference: `C-5=model_raw_anomaly_measure`; `runtime=padim_anomaly_map_max_v1`
- Expected-by-design `prediction_id` difference: `C-5=offline stable id`; `runtime=runtime stable id`

## Tolerance Policy

- Absolute tolerance: `1e-12`
- Relative tolerance: `1e-12`
- Bbox absolute tolerance: `0.0`
- Tolerances declared before comparison: `true`
- Absolute justification: `The governed ONNX export already reproduced the C-5 float64 PaDiM signal across 6,492 samples at machine-epsilon deviation. Runtime equivalence keeps the same 1e-12 bound to verify the integrated provider seam without silently widening the established regime.`
- Relative justification: `The relative tolerance mirrors Task 2's demonstrated DOUBLE CPUExecutionProvider regime for anomaly maps and raw measures.`
- Bbox justification: `The localization coordinates are exact multiples of 1/64 and the C-5 rounded records are exact for those values; zero tolerance is therefore an equality requirement.`

## Replay Result

- Complete second runtime-equivalence run executed: `true`
- Complete second canonical runtime load and execution: `true`
- Per-sample deviations identical: `true`
- Per-split maxima identical: `true`
- Global maxima identical: `true`
- Pass/fail status identical: `true`
- Runtime-equivalence report hash identical: `true`
- Runtime-equivalence hashes record deterministic: `true`
- Runtime-equivalence report SHA-256: `637098d4ba73070f2ea734ac76c6f212572d1b66da8df72e622f1376c238523d`
- Runtime-equivalence replay SHA-256: `9e9336da2ce12007b2ca97861314e60c0d599e5fc4e6bba8ad1930853a8ce9ce`
- Runtime-equivalence hashes record SHA-256: `53e7dd52ca7d97ec37ce713926689ef9b6d607da47875ff8f73ad069087fcf4f`

## Explicit Non-Claims

- Runtime equivalence verification is not scientific evaluation.
- No new Image AUROC was generated.
- No new Pixel AUROC was generated.
- No new AUPRO was generated.
- No Precision/Recall/F1 was generated.
- No calibration was performed.
- No benchmark was generated.
- No scientific claim was made.
- No product claim was made.
- Placeholder retirement was not performed.
