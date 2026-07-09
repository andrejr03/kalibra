# Kalibra Real ONNX Runtime Evidence - Sprint 1F

## Purpose

This document records a narrow evidence slice for the governed
loader/provider chain using real `onnxruntime`.

It records runtime evidence only. It does not introduce architecture, provider
semantics, dataset ingestion, evaluation, benchmark, scientific, or product
claims.

## Evidence Target

The validated chain is:

```text
Governed Model Artifact
  -> Deterministic Model Loader
  -> Real ONNX Runtime InferenceSession
  -> OnnxInspectionInferenceProvider
  -> InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> RawInspectionResult
```

Only `InspectionPrediction` crosses the provider boundary. The real
`onnxruntime.InferenceSession` remains provider-private.

## Command Executed

```bash
python3 scripts/validate_real_onnx_runtime.py
```

Result:

```text
PASSED tests/test_onnx_provider.py::test_onnx_provider_real_runtime_integration
15 passed in 1.38s
```

The evidence tool created an isolated temporary virtual environment, installed
the optional runtime dependency, ran `tests/test_onnx_provider.py`, and would
have failed if the real-runtime integration test skipped.

## Environment Summary

- Repository: `<REPO>`
- Branch: `/initial-engineering-skeleton`
- HEAD: `59fc350f27f2e79ca5d42552819a6bb3077002e3`
- Host platform: `macOS-26.5.2-arm64-arm-64bit`
- Host Python: `Python 3.9.6`
- Host Python executable: `/Applications/Xcode.app/Contents/Developer/usr/bin/python3`
- Host pytest: `pytest 8.4.2`
- Host `onnxruntime` importable before optional evidence install: `False`
- Temporary evidence environment dependency set included:
  - `onnxruntime 1.19.2`
  - `numpy 2.0.2`
  - `pytest 8.4.2`
  - `pip 26.0.1`

## Evidence Result

Real-runtime test PASSED.

The provider test result was:

```text
15 passed in 1.38s
```

The real-runtime integration test did not skip. The required real
`onnxruntime` path was exercised by the isolated evidence tool.

## Normal Local Optional Dependency Behavior

The normal local environment does not require `onnxruntime`.

```bash
python3 -m pytest tests/test_onnx_provider.py -q
```

Result:

```text
14 passed, 1 skipped in 0.11s
```

```bash
python3 -m pytest -q
```

Result:

```text
432 passed, 1 skipped in 10.01s
```

This confirms that the local test suite still skips cleanly when optional
`onnxruntime` is absent from the normal environment.

## Additional Validation

```bash
python3 -m compileall -q src tests scripts
```

Result: passed with no output.

```bash
git diff --check
```

Result: passed with no output after this evidence document was added. The new
evidence file is untracked, so this command reported no tracked diff issues.

```bash
git status --short
```

Result after this evidence document was added:

```text
?? docs/evidence/KALIBRA_REAL_ONNX_RUNTIME_EVIDENCE_SPRINT_1F_v1.0.md
```

## Scope Confirmation

- No architecture change was made.
- No provider semantics change was made.
- No `src/`, `tests/`, or `scripts/` files were modified.
- No inference lifecycle abstraction was added.
- No dataset ingestion, benchmark logic, performance measurement, CLI/UI
  integration, hosted behavior, scheduling, alerting, or production service
  infrastructure was added.
- No dataset, evaluation, benchmark, calibration, drift-response, scientific, or
  product claim is made by this evidence record.
