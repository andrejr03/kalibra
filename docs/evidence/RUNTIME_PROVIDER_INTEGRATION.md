# Kalibra Runtime Provider Integration Evidence v1.0

**Date:** 2026-07-07
**Scope:** Phase 3 / Task 3 - Runtime Provider Integration only

## Verification Levels

- **Level 1 - Clean-Clone Verification:** `python3 scripts/verify_public_clone.py` validates the committed model, runtime records, and public evidence drift without replaying governed data.
- **Level 2 - Governed Runtime Verification:** `python3 scripts/verify_padim_runtime_equivalence.py verify` requires separately acquired VisA source/archive bytes; see `docs/engineering/VISA_ACQUISITION_AND_GOVERNANCE.md`.
- **Level 3 - Full Scientific Reproduction:** governed acquisition plus the documented scientific and runtime environment; it is separate from the public clone contract.

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
- Integration metadata SHA-256: `8e80ffd9637708b92d6f5de7534c49247a9740e30678ac3ae18598bfb9c8b5e0`
- Runtime replay SHA-256: `376b7a84cb65949aa55189d8cc57fb7b14dfcf899e26b697d7954c87282f2e76`

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
