# Kalibra Placeholder Retirement Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization
planning only; no placeholder retired, no runtime modified, no provider modified, no
model loader modified, no output mapping modified, no preprocessing modified, no
feature extraction modified, no prediction contract changed, no Trust/Review/Evidence/
Evaluation domain touched, no calibration, no metrics, no benchmark, no scientific or
product claim, no files deleted)
**Date:** 2026-07-07
**Repository baseline HEAD:** `8864ef0 feat: verify runtime equivalence`
**Branch:** `codex/initial-engineering-skeleton`
**Architecture baseline:** [ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md)
**Previous capability:** Phase 3 / Task 4 — Runtime Equivalence Verification (completion
checkpoint [here](KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_COMPLETION_CHECKPOINT_v1.0.md))

---

## About This Document

This document persists the **Placeholder Retirement Authorization Checkpoint** as a
versioned checkpoint following the repository checkpoint convention and the AGENTS.md
engineering-knowledge workflow (Decision → Persist Checkpoint → Review → Authorization →
Implementation → Implementation Review → Persist Completion Evidence).

It is **authorization planning only**. It writes no code, retires no placeholder,
modifies no runtime, deletes no files, and performs no evaluation. It records the
governance decision to authorize a bounded implementation of Phase 3 / Task 5 —
Placeholder Retirement — and the precise scope, forbidden scope, required outputs,
validation requirements, and scientific boundaries that implementation must obey.

It takes the Task 4 completion checkpoint as the prior capability state. Runtime
equivalence has been verified deterministic and within machine-epsilon tolerances
(`7.105427357601002e-15` max absolute deviation across all 6,492 samples, byte-identical
replay). The canonical runtime path is proven to carry only the governed PaDiM model
(`kalibra-padim-onnx-export-v1`). Placeholder retirement is therefore **architecture
hygiene on a verified substrate**, not a signal-affecting change.

---

## 0. Baseline Confirmation

The baseline was confirmed by independent inspection of the repository at HEAD
`8864ef0`:

- **Task 4 completion checkpoint exists and records PASS.** The Runtime Equivalence
  Verification Completion Checkpoint records the canonical runtime path executing
  `OnnxInspectionInferenceProvider().predict(StabilizedInspectionInput)` across all
  6,492 samples with final status `passed`, tolerances satisfied, and deterministic
  replay.
- **Canonical runtime path uses only the governed PaDiM model.** The default
  `OnnxInspectionInferenceProvider` session configuration
  (`src/inspection/providers_onnx.py:116-118`) is
  `governed_padim_session_configuration()`. A bare `OnnxInspectionInferenceProvider()`
  loads `kalibra-padim-onnx-export-v1` (SHA-256
  `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`). The placeholder
  is reachable **only** through an explicit placeholder reference id, never by default.
- **The placeholder seam is fully retained but not canonical.** The placeholder branch
  in `__post_init__` (`providers_onnx.py:146-149`) and the `else` fallback in `predict()`
  (`providers_onnx.py:204`) remain wired. The placeholder fixture exists at
  `tests/fixtures/inspection/onnx_placeholder/placeholder_identity.onnx`.
- **Runtime-equivalence and runtime-integration artifacts are unchanged.**
  - `artifacts/runtime/equivalence/runtime_equivalence_report.json` →
    `637098d4ba73070f2ea734ac76c6f212572d1b66da8df72e622f1376c238523d`
  - `artifacts/runtime/equivalence/runtime_equivalence_replay.json` →
    `9e9336da2ce12007b2ca97861314e60c0d599e5fc4e6bba8ad1930853a8ce9ce`
  - `artifacts/runtime/equivalence/runtime_equivalence_hashes.json` →
    `53e7dd52ca7d97ec37ce713926689ef9b6d607da47875ff8f73ad069087fcf4f`
  - `artifacts/runtime/integration_metadata.json` →
    `5e885feb6ada4585a0c295b3935a0d1c73ce2753dd7a1227adad63953fae2757`
  - `artifacts/runtime/runtime_replay.json` →
    `0a7969eb6ada592ff7de73c2853b460d5b50acb8c80892054532c03889b36b579`
  - `artifacts/runtime/runtime_hashes.json` →
    `6b746f4c0ab7babd8d957ebdb6b9d3f7b8ff83aefa65cfef192aacf1ee7c23e3`

These hashes are the **immutability contract** Task 5 must not violate.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Placeholder Retirement
```

**Justification.**

1. **The prerequisite capability is complete.** Task 4 (Runtime Equivalence
   Verification) is recorded PASS with deterministic, replay-verified equivalence of the
   canonical runtime path to the governed C-5/C-6-observable signal across all 6,492
   samples. There is a verified substrate to retire the placeholder against.
2. **The placeholder is already non-canonical.** Since Task 3, the default runtime
   provider loads only the governed PaDiM model. The placeholder is reachable only via an
   explicit reference id. Retirement is therefore the removal of a *dormant* fallback
   branch, not a change to the active signal path.
3. **The change surface is bounded and architectural-hygienic.** Placeholder retirement
   touches the placeholder-specific branch in `providers_onnx.py`, the placeholder-specific
   constants/helpers, the placeholder fixture's classification (fixture-only vs.
   canonical), and tests/evidence — nothing downstream of the `InspectionPrediction`
   boundary.
4. **It produces no new signal, metric, or claim.** Retirement is architecture hygiene
   after runtime equivalence, explicitly within the Phase 3 / Task 5 capability slot
   defined by the architecture baseline (§6 item 5) and the Task 3 authorization
   convention (full placeholder fixture retirement deferred to capability #5).

---

## 2. Authorized Scope

Authorize **only** the following:

1. **Removal of the placeholder from the canonical runtime path.** The placeholder
   branch in `OnnxInspectionInferenceProvider.__post_init__`
   (`providers_onnx.py:146-149`) and the `else` placeholder fallback in `predict()`
   (`providers_onnx.py:204`) must no longer be reachable from the canonical runtime
   path. The canonical provider must load and execute only
   `kalibra-padim-onnx-export-v1`.

2. **Conversion of the placeholder to an explicit legacy fixture, if still needed.**
   The placeholder ONNX fixture (`tests/fixtures/inspection/onnx_placeholder/`) and its
   generator (`generate_placeholder_onnx.py`) may be retained **only** as an explicit
   test/legacy fixture, clearly marked as non-canonical. Any retained placeholder code
   must be unreachable from the canonical `inspect()` path.

3. **Cleanup of placeholder-specific constants from canonical provider logic.**
   Placeholder-specific identifiers in `providers_onnx.py`
   (`ONNX_PLACEHOLDER_MODEL_REFERENCE_ID`, `_MODEL_KIND_PLACEHOLDER`,
   `_placeholder_model_artifact`, `_predict_placeholder`, `_run_placeholder_session`,
   `_map_placeholder_output`, `_single_input_name`) may be removed from the canonical
   provider, or relocated behind an explicit fixture-only boundary. The generic
   module-level aliases in `output_mapping.py` (`OUTPUT_MAPPING_CONTRACT_ID`,
   `EXPECTED_OUTPUT_COUNT/SHAPE/DTYPE`, `RAW_MEASURE_SCALE`, `LOCALIZATION_KIND`,
   `MAPPING_SEMANTICS`) currently still alias placeholder values and must be reconciled
   so the canonical surface reflects only the governed PaDiM contract.

4. **Test updates proving the canonical path uses only governed PaDiM.** Existing
   placeholder-path tests (`tests/test_onnx_provider.py`,
   `tests/test_output_mapping.py`, `tests/test_inspection_engine.py`) must be updated to
   reflect the placeholder's fixture-only status, and new tests must demonstrate the
   canonical provider cannot load the placeholder by default.

5. **Evidence that the placeholder is not reachable from the canonical runtime.** A
   persisted verification (script + artifacts) proving the canonical provider rejects the
   placeholder reference id and that no canonical code path resolves to placeholder
   logic.

6. **Governed retirement metadata/evidence.** The retirement artifacts (§4) recording
   what was removed/converted, the fail-closed test results, and the unchanged-runtime
   attestation.

**Scope boundary for test changes:** test modifications are permitted **only** where they
assert the new placeholder-status contract. Tests that exercise the *canonical* PaDiM path
must remain unchanged in their assertions (the signal they verify is unchanged).

---

## 3. Forbidden Scope

The implementation must **not** perform any of the following. Violating any item is
grounds for stopping and re-reviewing:

- **PaDiM refit.** The fitted single-seed baseline (μ / Σ⁻¹, seed `271828`) is the input;
  it is not re-fit or re-selected.
- **ONNX re-export.** The governed ONNX artifact
  (`kalibra-padim-onnx-export-v1`, SHA-256
  `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`) is the model;
  it is not re-exported.
- **Runtime redesign.** No new runtime architecture, session substrate, or execution
  model.
- **Provider redesign.** The `OnnxInspectionInferenceProvider` shape, the
  `InspectionInferenceProvider` protocol, and the `predict()` → `InspectionPrediction`
  contract shape are unchanged.
- **Output mapping redesign.** The PaDiM output mapping contract
  (`kalibra-padim-onnx-output-mapping-v1`) is unchanged; only the placeholder aliases are
  reconciled.
- **Preprocessing changes.** `src/frameworks/image_preprocessing.py` is unchanged.
- **Feature extraction changes.** The PaDiM feature extraction contract and feature
  indices `[0, 2, 5, 6, 7, 9, 12, 13]` are unchanged.
- **Prediction contract changes.** The `InspectionPrediction` field set and semantics
  are unchanged.
- **Trust / Review / Evidence / Evaluation domain changes.** No file under `src/trust`,
  `src/review`, `src/evidence`, `src/evaluation` may be modified. The placeholder
  calibrator compatibility surface (`DeterministicPlaceholderCalibrator`) is a Trust-domain
  concern and is explicitly **out of scope** — Task 5 retires the *runtime inspection*
  placeholder, not the Trust placeholder calibrator.
- **Calibration, metrics, benchmark.** No calibration performed; no new metrics
  generated; no benchmark produced.
- **Scientific or product claims.** No claim beyond the C-6 single-seed VisA-proxy
  boundary.

**Hard immutability constraint.** The runtime-equivalence and runtime-integration
artifacts listed in §0 must remain **byte-identical** (SHA-256 unchanged). If retirement
logic would require touching the canonical signal path such that these artifacts would
change, that is a red flag that retirement has drifted into re-architecture — stop and
re-review.

---

## 4. Required Outputs

The implementation must produce the following governed artifacts:

```text
artifacts/runtime/placeholder_retirement/
  placeholder_retirement_metadata.json
  placeholder_retirement_hashes.json
  placeholder_retirement_replay.json
```

and:

```text
docs/evidence/KALIBRA_PLACEHOLDER_RETIREMENT_EVIDENCE_v1.0.md
```

### 4.1 `placeholder_retirement_metadata.json`

Must record at minimum:

- `schema`: `kalibra_runtime_placeholder_retirement_metadata_v1` (or governed equivalent).
- `retirement_label`: `kalibra-placeholder-retirement-v1`.
- `status`: `passed`.
- `canonical_runtime_reference_id`: `kalibra-padim-onnx-export-v1`.
- `placeholder_reference_id_removed_from_canonical_path`:
  `onnx-placeholder-boundary-model-v1`.
- `placeholder_unreachable_from_canonical_runtime`: `true`.
- `placeholder_retained_as_fixture_only`: `true`/`false` (explicit).
- `removed_constants`: explicit list of placeholder identifiers removed from canonical
  provider logic.
- `relocated_or_fixture_only_constants`: explicit list of placeholder identifiers kept
  behind a fixture-only boundary (if any).
- `unchanged_runtime_artifacts`: the six SHA-256 digests from §0, re-attested unchanged.
- `scope_boundaries`: machine-checkable flags (all `*_changed`/`*_performed` false except
  `placeholder_retirement_performed: true`).
- `explicit_non_claims`: explicit list.
- `toolchain`: python / numpy / onnx / onnxruntime versions.

### 4.2 `placeholder_retirement_replay.json`

Must record a deterministic replay proving the retirement verification is itself
deterministic: a complete second run of the retirement verification produces identical
per-sample and global results, identical hashes, and identical pass/fail status.

### 4.3 `placeholder_retirement_hashes.json`

Must record SHA-256 digests of the retirement metadata and replay artifacts.

### 4.4 `KALIBRA_PLACEHOLDER_RETIREMENT_EVIDENCE_v1.0.md`

Human-readable evidence document for an untrusting observer, recording: the retirement
scope, what was removed/converted, the fail-closed test results, the unchanged-runtime
attestation, the scientific boundaries, and the explicit non-claims.

---

## 5. Validation Requirements

The implementation must prove **all** of the following, with evidence:

1. **Canonical provider cannot load the placeholder by default.** A bare
   `OnnxInspectionInferenceProvider()` (no arguments) must load only
   `kalibra-padim-onnx-export-v1`. A test must demonstrate that the placeholder reference
   id is rejected or unreachable from the canonical default configuration, and that no
   canonical code path resolves to placeholder logic.

2. **Canonical runtime path uses only `kalibra-padim-onnx-export-v1`.** The model
   reference loaded by the canonical provider, recorded in prediction `model_metadata`,
   must be `kalibra-padim-onnx-export-v1` (SHA-256
   `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`).

3. **Placeholder references are either removed or explicitly marked fixture-only.** No
   placeholder identifier remains in the canonical provider's reachable dispatch without
   an explicit fixture-only classification.

4. **Tests fail closed if the placeholder becomes canonical again.** A regression test
   must assert that if the placeholder were re-introduced as the default/canonical model,
   the test suite would fail. This protects against silent reversion.

5. **Runtime-equivalence artifacts remain unchanged.** The six SHA-256 digests in §0
   must be re-attested identical after retirement. This is the strongest proof that
   retirement touched no signal path.

6. **No downstream domain modifications.** `git status --short -- src/trust src/review
   src/evidence src/evaluation` must be empty. No `InspectionPrediction` contract field
   may be added, removed, or renamed.

### 5.1 Validation commands the implementation must run

```bash
python3 scripts/verify_padim_runtime_equivalence.py verify   # must still pass, artifacts unchanged
python3 scripts/run_runtime_provider_integration.py verify    # must still pass, artifacts unchanged
python3 -m pytest -q                                           # full suite must pass
python3 -m compileall -q src tests scripts                    # byte-compilation clean
git diff --check                                               # whitespace clean
git status --short -- src/trust src/review src/evidence src/evaluation   # must be empty
```

The runtime-equivalence and runtime-integration verifications must produce **identical**
governed artifacts (same SHA-256) before and after retirement — proving the canonical
signal path is untouched.

---

## 6. Scientific Boundaries

State explicitly and carry into the evidence:

- **Placeholder retirement is not scientific evaluation.**
- **Placeholder retirement produces no new metrics.**
- **Placeholder retirement produces no new scientific claim.**
- **It is architecture hygiene after runtime equivalence.**

Retirement does not improve, change, or re-assert any detection quality, calibration
quality, uncertainty quality, review quality, or drift response. The scientific claim
boundary remains exactly C-6's: single-seed, VisA-proxy, no calibration, no confidence,
no product-readiness. The runtime continues to make **no** scientific claim beyond
carrying the same bounded signal C-6 already validated offline.

---

## 7. Authorized Change Surface (Reference)

For governance clarity, the placeholder surface that exists at the baseline and that
Task 5 is authorized to reconcile is:

**Canonical provider logic (`src/inspection/providers_onnx.py`):**
- `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID` (`:32`)
- `_MODEL_KIND_PLACEHOLDER` (`:64`)
- `__post_init__` placeholder branch (`:146-149`)
- `predict()` placeholder `else` fallback (`:204`)
- `_predict_placeholder` (`:264-311`)
- `_placeholder_model_artifact` (`:411-454`)
- `_single_input_name` (`:740-756`) — placeholder input-name validation
- `_run_placeholder_session` (`:759-767`)
- `_map_placeholder_output` (`:865-882`)

**Output mapping aliases (`src/frameworks/output_mapping.py`):**
- Generic module aliases that currently resolve to placeholder values: `OUTPUT_MAPPING_CONTRACT_ID`
  is already PaDiM (`:11`); but `EXPECTED_OUTPUT_COUNT/SHAPE/DTYPE` (`:22-24`) still alias
  placeholder values, and `RAW_MEASURE_SCALE` (`:28`) / `LOCALIZATION_KIND` (`:39`) /
  `MAPPING_SEMANTICS` (`:33`) alias PaDiM values. The implementation must verify and, where
  needed, reconcile so the canonical surface is unambiguously PaDiM-only.

**Tests (to update to fixture-only status, not to weaken canonical assertions):**
- `tests/test_onnx_provider.py` (placeholder-model path coverage)
- `tests/test_output_mapping.py` (`test_valid_placeholder_output_maps_deterministically`)
- `tests/test_inspection_engine.py` (placeholder-examination references in non-canonical
  assertion contexts)

**Explicitly NOT in the authorized change surface:**
- `src/trust/` (placeholder calibrator is a separate compatibility-surface concern)
- `src/inspection/engine.py` `DeterministicPlaceholderExaminer` — this is the
  inspection-substrate placeholder examiner, **not** the ONNX-runtime placeholder model.
  It is a distinct surface. The implementation must clarify whether engine-layer
  placeholder examiner retirement is in scope; **default: out of scope** unless the
  repository owner explicitly extends authorization, because the canonical runtime path
  is the ONNX provider path, not `DeterministicPlaceholderExaminer`.

**Placeholder fixture (retain as fixture-only, do not delete unless explicitly
instructed):**
- `tests/fixtures/inspection/onnx_placeholder/placeholder_identity.onnx`
- `tests/fixtures/inspection/onnx_placeholder/generate_placeholder_onnx.py`

---

## 8. Risk Assessment

### R1 — Canonical-path regression (MEDIUM)
Retirement logic accidentally alters the canonical PaDiM path, changing the runtime
signal. **Mitigation:** the runtime-equivalence and runtime-integration artifacts are
immutability contracts (§0/§3); both verifications must reproduce identical SHA-256
digests after retirement.

### R2 — Over-broad retirement (MEDIUM)
Retirement drifts into Trust/Evaluation placeholder surfaces or the engine-layer
examiner, expanding scope beyond the runtime inspection placeholder. **Mitigation:**
explicit forbidden scope (§3) and `git status --short -- src/trust src/review src/evidence
src/evaluation` must remain empty.

### R3 — Silent reversion (LOW-MEDIUM)
A future change re-introduces the placeholder as canonical without detection.
**Mitigation:** required fail-closed regression test (§5.4).

### R4 — Test weakening (LOW)
Placeholder-path tests are deleted rather than converted, reducing coverage.
**Mitigation:** test changes must assert the new fixture-only contract, not merely
remove assertions.

---

## 9. Scope Boundaries and Explicit Non-Claims

This authorization:

- **Authorizes only** the bounded implementation described in §2.
- **Authorizes no** Phase 3 closure. Phase 3 closure is a separate decision the
  repository owner makes after reviewing Task 5 completion.
- **Performs no** code implementation, no placeholder retirement, no runtime
  modification, no file deletion.
- **Makes no** scientific or product claim beyond C-6.
- **Does not** authorize calibration, metrics, benchmark, multi-seed characterization,
  or any capability outside Phase 3 / Task 5.
- **Does not** modify the `InspectionPrediction` contract, the provider protocol, or any
  downstream domain.

---

## 10. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree | `git status --short` | clean (only this checkpoint created) ✔ |
| HEAD | `git log -1 --oneline` | `8864ef0 feat: verify runtime equivalence` ✔ |

The only working-tree change after this authorization is the creation of this checkpoint
document.

---

## 11. Readiness Decision

```text
READY FOR BOUNDED IMPLEMENTATION PROMPT
```

The authorization is complete, scoped, and bounded. The substrate is verified. The
forbidden scope is explicit. The required outputs and validation requirements are
defined. The implementation may proceed under a bounded implementation prompt that
inherits this checkpoint's scope verbatim.

---

## 12. Next Natural Step

```text
Generate the bounded implementation prompt for Phase 3 / Task 5 — Placeholder Retirement.
```

The implementation prompt must inherit this checkpoint's authorized scope (§2), forbidden
scope (§3), required outputs (§4), validation requirements (§5), and scientific
boundaries (§6) verbatim, and must be reviewed and approved by the repository owner
before any code is written.
