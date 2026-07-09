# Kalibra Governed PaDiM ONNX Export Evidence v1.0

**Date:** 2026-07-06
**Scope:** Phase 3 / Task 1 - Governed ONNX Export only

## Export Scope

- Export label: `visa-padim-governed-onnx-export-v1`
- Artifact: `artifacts/padim/model.onnx`
- Scope: deterministic export of the already-fitted C-4 PaDiM baseline only.
- No runtime integration was performed.
- No provider change was performed.
- No model loader change was performed.
- No output mapping change was performed.
- No preprocessing change was performed.

## Governed C-4 Input Identity

- Training label: `visa-padim-baseline-fit-v1`
- Training record SHA-256: `7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048`
- Training artifact hashes SHA-256: `00c625060c6e50fe7ab1da76125e3891d8be7e52838c846eaba52813461eeb32`
- Training metadata SHA-256: `c0178d823d0c440102c768f75799340586bd4c428bfa309862e8fb658b0ffad9`
- Training replay SHA-256: `dc5f66ee17533518489c893358cb30b8dd622277b5f38e21c0a0dd6e67fdd55f`
- Mu artifact SHA-256: `51568c211c324b9178837f0d862c01a9601dc3d3daa474c959bb32ef5758446b`
- Covariance inverse artifact SHA-256: `893af9e08d3543b5bd973ab913c1f2e8ed57d26a1bbb225b194d525cfc8df7b3`
- Feature indices artifact SHA-256: `1ca5583a7b498b4849e42717f24ebcf82d82a6c545b852814ada12b5c287cbe3`
- Feature indices: `[0, 2, 5, 6, 7, 9, 12, 13]`
- Source dtype: `float64`
- Epsilon: `0.001`
- Preprocessing contract: `kalibra-padim-rgb64-bilinear-float64-patch8-v1`
- Backbone: `kalibra-fixed-patch-feature-backbone-v1`
- Layer: `fixed_patch_statistics_64x64_patch8`

## Governed C-5 Reference Identity

- Inference label: `visa-padim-governed-inference-v1`
- Inference artifact hashes SHA-256: `c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf`
- Inference metadata SHA-256: `78e8408534863096315a07f21da33265f970e44f369a9fa3e35743f2adea372f`
- Inference replay SHA-256: `e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c`
- Aggregation identifier: `padim_anomaly_map_max_v1`
- Localization identifier: `padim_raw_anomaly_map_argmax_region_v1`
- Reference use: export fidelity verification only.

## ONNX Artifact Identity

- Model SHA-256: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Artifact record SHA-256: `6d6768cbd13d0a26dbfb817e676fc5ccddbb878b72f18e443dc403b531052f4f`
- Metadata record SHA-256: `3dd299292c32a7d6616171ce26dd6d07a3d1c313dfc4dd00ea583dbca313f00d`
- Export replay SHA-256: `e2d7f28ed2412a509e384ad50509fc8e73d4f1347349683e4f89a4071be27093`
- Artifact hashes record SHA-256: `d2e36f0ed4b6bd71c15fb4ce49c2481b5f1af4edc7b0ee034dc76386deed38c6`
- Opset: `18`
- ONNX IR version: `10`
- Toolchain: `{'python': '3.9.6', 'numpy': '2.0.2', 'onnx': '1.16.2', 'onnxruntime': '1.19.2'}`

## Dtype Policy

- Source dtype: `float64`
- ONNX dtype: `float64`
- Precision policy: preserve C-4 float64 as ONNX DOUBLE.
- Float32 transition: `false`
- Expected numerical tolerance: `{'absolute': 1e-12, 'relative': 1e-12, 'bbox_absolute': 0.0}`

## Graph Contract

- Inputs: `{'full_patch_features': {'dtype': 'float64', 'shape': [1, 64, 14], 'semantics': 'C-4 deterministic full patch feature tensor before governed feature subsampling; preprocessing contract remains kalibra-padim-rgb64-bilinear-float64-patch8-v1'}, 'class_index': {'dtype': 'int64', 'shape': [1], 'semantics': 'index into the governed C-4 class_order recorded in artifact.json'}}`
- Outputs: `{'patch_mahalanobis_distances': {'dtype': 'float64', 'shape': [1, 64], 'semantics': 'per-patch Mahalanobis distance after governed feature selection'}, 'anomaly_map': {'dtype': 'float64', 'shape': [1, 64, 64], 'aggregation_source': 'padim_anomaly_map_max_v1', 'semantics': '8x8 patch distances repeated over 8x8 pixel cells'}, 'raw_anomaly_measure': {'dtype': 'float64', 'shape': [1], 'identifier': 'padim_anomaly_map_max_v1', 'semantics': 'maximum finite Mahalanobis distance over anomaly map'}, 'argmax_region': {'dtype': 'float64', 'shape': [1, 4], 'identifier': 'padim_raw_anomaly_map_argmax_region_v1', 'order': ['x_min', 'y_min', 'x_max', 'y_max'], 'semantics': 'bounding box covering pixels equal to maximum anomaly-map value'}}`
- Localization represented in ONNX: `true`
- Preprocessing reimplemented in ONNX: `false`

## Export Replay Result

- Complete second export executed: `true`
- Identical ONNX bytes: `true`
- Identical model hash: `true`
- Identical artifact metadata: `true`
- Identical artifact hashes: `true`
- Replay record: `artifacts/padim/export_replay.json`

## Export Fidelity Result

- Status: `passed`
- Reference: governed C-5 inference outputs.
- Sample count: `6492`
- Max anomaly-map absolute deviation: `7.105427357601002e-15`
- Max anomaly-map relative deviation: `3.586867160478407e-15`
- Max raw-measure absolute deviation: `7.105427357601002e-15`
- Max raw-measure relative deviation: `3.586867160478407e-15`
- Max argmax-region absolute deviation: `0.0`
- Numerical tolerance: `{'absolute': 1e-12, 'relative': 1e-12, 'bbox_absolute': 0.0}`
- Offline ONNX execution provider used for fidelity: `CPUExecutionProvider`
- Runtime provider loaded: `false`

## Known Limitations

- The graph input is the deterministic full patch feature tensor, not image pixels.
- The preprocessing contract is recorded and required but not reimplemented in ONNX.
- The artifact is not wired into `src/inspection/providers_onnx.py`.
- Export fidelity is not runtime equivalence.
- Export fidelity is not scientific evaluation.
- No calibrated confidence, threshold, operating point, abstention, review routing, or drift behavior is introduced.

## Explicit Non-Claims

- No runtime integration.
- No provider change.
- No model loader change.
- No output mapping change.
- No preprocessing change.
- No inference capability added.
- No evaluation executed.
- No metric generated.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, or F1 generated.
- No calibration performed.
- No benchmark generated.
- No scientific claim.
- No product claim.
