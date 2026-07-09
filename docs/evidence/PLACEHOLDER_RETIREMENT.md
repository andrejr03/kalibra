# Kalibra Placeholder Retirement Evidence v1.0

**Status:** Recorded - governed placeholder retirement evidence only
**Date:** 2026-07-07
**Scope:** Phase 3 / Task 5 - Placeholder Retirement only (architecture hygiene)

## Retirement Scope

- Placeholder retirement is architecture hygiene after runtime equivalence.
- Canonical provider loads only: `kalibra-padim-onnx-export-v1`
- Placeholder reference id retired from canonical path: `onnx-placeholder-boundary-model-v1`
- Placeholder unreachable from canonical runtime: `true`
- Placeholder retained as fixture-only: `true`

## Canonical Provider Checks

- Canonical model kind: `padim`
- Canonical source has no placeholder dispatch: `true`
- Canonical `__post_init__` has no placeholder branch: `true`
- Canonical output_mapping aliases are PaDiM-only: `true`

## Fail-Closed Regression

- Fail-closed regression passed: `true`
- Description: `canonical provider rejects placeholder reference id; if placeholder became canonical again the test suite would fail`

## Removed / Fixture-Only Constants

- Removed from canonical provider: `_MODEL_KIND_PLACEHOLDER`
- Relocated behind fixture-only boundary: `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID, _placeholder_model_artifact, _predict_placeholder, _run_placeholder_session, _map_placeholder_output, _single_input_name`

## Unchanged Runtime Hashes (Immutability Contract)

- Runtime equivalence report SHA-256: `90ea39972ceb53205adfce6280f9b897a42ed935917810c89386e01819be6d19`
- Runtime equivalence replay SHA-256: `65b414c47f4b040c4bd0b090d54cfdf6fa3099c01c7b5329a9c75a7a8759bee8`
- Runtime equivalence hashes SHA-256: `80cce54f23eb3a37116af0116fccfa8d6d97cc103b2675699fdf8a7e1e18e84c`
- Runtime integration metadata SHA-256: `8e80ffd9637708b92d6f5de7534c49247a9740e30678ac3ae18598bfb9c8b5e0`
- Runtime replay SHA-256: `376b7a84cb65949aa55189d8cc57fb7b14dfcf899e26b697d7954c87282f2e76`
- Runtime hashes SHA-256: `0009ffc8982c17478f0494a49562aa4408dad4261c645e75a799e72d80a2ecdd`
- Runtime integration hashes unchanged: `true`
- Runtime equivalence hashes unchanged: `true`

## Downstream Domain Isolation

- Downstream domains changed (src/trust, src/review, src/evidence, src/evaluation): `false`

## Replay Result

- Complete second retirement verification run: `true`
- Canonical reference id identical: `true`
- Placeholder rejected identical: `true`
- Immutability hashes identical: `true`
- Metadata JSON identical: `true`
- Status identical: `true`
- Retirement metadata SHA-256: `3915e5e09617b22c175c5974a4b44efa0a773096dfaf9cdcba1f2a346e577861`
- Retirement replay SHA-256: `50ed3fb0561b0a14eb271cab1081f31bfe79cfb278a6e43395506c5fcf5563e3`
- Retirement hashes record SHA-256: `f90faa8855be7f7774e765e2483f6a08cb5a11e505af0cc837a24bfe9cd6324c`

## Explicit Non-Claims

- Placeholder retirement is architecture hygiene after runtime equivalence.
- No PaDiM refit was performed.
- No ONNX re-export was performed.
- No scientific evaluation was performed.
- No metrics were generated.
- No calibration was performed.
- No benchmark was generated.
- No scientific claim was made.
- No product claim was made.
- No Phase 3 closure is authorized.
