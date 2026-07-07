# Kalibra Runtime Provider Integration Evidence v1.0

**Status:** Recorded - governed runtime provider integration evidence only
**Date:** 2026-07-07
**Scope:** Phase 3 / Task 3 - Runtime Provider Integration only

## Integration Result

- Runtime integration completed: `true`
- Governed ONNX artifact loaded through runtime substrate: `true`
- Runtime substrate used: `model_loader.load_governed_model` -> `ProviderPrivateInferenceSession`
- Provider seam preserved: `InspectionInferenceProvider.predict(...) -> InspectionPrediction`
- Provider uses governed artifact: `kalibra-padim-onnx-export-v1`
- Placeholder no longer used on canonical runtime path: `true`
- Runtime replay status: `passed`

## Artifact Identity

- Model path: `artifacts/padim/model.onnx`
- Model reference id: `kalibra-padim-onnx-export-v1`
- Model SHA-256: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Runtime artifact hash: `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`
- Opset: `18`
- ONNX IR version: `10`
- Artifact metadata schema: `kalibra_governed_padim_onnx_export_metadata_v1`
- Export equivalence identity verified before runtime integration: `true`

## Runtime Configuration

- Execution provider: `CPUExecutionProvider`
- Execution provider policy: `exact_order`
- Intra-op threads: `1`
- Inter-op threads: `1`
- Graph optimization level: `ORT_DISABLE_ALL` (`disable_all`)
- Session configuration hash: `2893fd1fc592cb831bfccd9d53c3e784a5aba4ffdfbb58ad4de32eb512c4a2e4`

## Replay Result

- Complete second load and execution: `true`
- Representative input count: `2`
- Same artifact identity: `true`
- Same session configuration: `true`
- Same raw anomaly measures: `true`
- Same localization: `true`
- Same `InspectionPrediction`: `true`
- Same hashes: `true`
- Runtime replay record: `artifacts/runtime/runtime_replay.json`
- Runtime hashes record: `artifacts/runtime/runtime_hashes.json`
- Integration metadata SHA-256: `5e885feb6ada4585a0c295b3935a0d1c73ce2753dd7a1227adad63953fae2757`
- Runtime replay SHA-256: `0a7969eb6da592ff7de73c2853b460d5b50acb8c80892054532c03889b36b579`

## Explicit Non-Claims

- No runtime-equivalence verification was performed.
- No comparison against C-5 or C-6 reference outputs was performed.
- No scientific evaluation was performed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, or F1 was generated.
- No metrics were generated.
- No calibration was performed.
- No threshold was derived.
- No benchmark was run.
- No Trust domain change was made.
- No Review domain change was made.
- No Evidence domain change was made.
- No Evaluation domain change was made.
- No scientific claim was made.
- No product claim was made.
