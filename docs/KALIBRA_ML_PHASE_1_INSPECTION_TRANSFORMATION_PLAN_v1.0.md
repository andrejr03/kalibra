# Kalibra ML Phase 1 — Inspection Prediction Transformation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Where this plan reaches a commit
> point, it instead defines a **validation checkpoint**: run the listed commands,
> report results, and let the repository owner commit. Do not commit.

**Goal:** Add the Inspection Engine-owned transformation from a validated
`InspectionPrediction` into the canonical `RawInspectionResult`, with evidence
emission preserved and no provider wiring.

**Architecture:** Machine Learning owns only `InspectionPrediction`. The
Inspection Engine owns prediction validation, deterministic transformation,
`RawInspectionResult`, inspection evidence, and the runtime contract. Downstream
domains continue to consume only `RawInspectionResult` and must not see
`InspectionPrediction`.

**Tech Stack:** Existing Python 3.9 dataclasses and protocols under
`src/inspection/`; Python standard library only; `pytest` for tests.

---

## Interpretation Note

This plan assumes the current repository state is authoritative:

- `InspectionPrediction`, `InvalidInspectionPrediction`, and
  `PartialInspectionPrediction` already exist.
- `InspectionInferenceProvider` already exists as a protocol with only
  `predict(...) -> InspectionPrediction`.
- `InspectionEngine` currently owns the deterministic examiner path and remains
  unwired from inference providers.

This task introduces the transformation boundary only. It must not introduce a
real model, provider implementation, inference runtime, provider wiring,
framework dependency, integration path, CLI path, or downstream-domain change.

## 1. Purpose

This task fixes the first point where a machine-learning prediction enters
Kalibra's deterministic runtime.

The purpose is to make the Inspection Engine accept an already-produced
`InspectionPrediction` only after Inspection-owned validation, then transform
that accepted prediction into the canonical `RawInspectionResult` it already
owns. The provider never creates `RawInspectionResult`; the provider owns only
the prediction claim.

The transformed result remains raw, unqualified, and downstream-compatible. It
continues to carry `raw_measure_kind = "raw_anomaly_measure"` and remains the
only object that Trust, Review, Evidence, Evaluation, Integration, and CLI flows
consume.

## 2. Scope

**In scope:**

- Inspection Engine validation for an already-created `InspectionPrediction`.
- Deterministic transformation from accepted `InspectionPrediction` to
  `RawInspectionResult`.
- Preservation of evidence emission after transformation.
- Raw-result contract adjustments inside Inspection only when required for
  prediction-origin provenance labels.
- Tests that prove transformation behavior, failure behavior, deterministic
  output, and downstream isolation.

**Likely implementation files:**

- `src/inspection/engine.py`
- `src/inspection/domain.py`
- `tests/test_inspection_engine.py`

**Explicitly out of scope:**

- `src/inspection/interfaces.py`, unless a review finds a direct conflict with
  the existing provider protocol.
- `src/trust/`
- `src/review/`
- `src/evidence/`
- `src/evaluation/`
- `src/integration/`
- `scripts/`
- `README.md`
- `assets/`
- `tools/`

## 3. Transformation Boundary

The transformation boundary is:

```text
InspectionPrediction
  |
  v
Inspection Engine validation
  |
  v
Inspection Engine deterministic transformation
  |
  v
RawInspectionResult
  |
  v
Inspection evidence emission
```

The Inspection Engine must own every step after the prediction is produced.

The provider must not:

- create `RawInspectionResult`;
- emit evidence;
- route review;
- qualify trust;
- calibrate confidence;
- evaluate performance;
- persist inspection evidence;
- mutate the runtime contract.

The Inspection Engine must not hand an invalid prediction to Trust, Review,
Evidence, Evaluation, Integration, or CLI code. Nothing downstream sees an
invalid prediction, a malformed prediction, or a prediction object directly.

## 4. Validation Pipeline

The transformation path must validate in this order:

1. The inspection input must be a `StabilizedInspectionInput`.
2. The prediction must be an `InspectionPrediction`.
3. `prediction.input_id` must equal the stabilized input's `input_id`.
4. `prediction.prediction_kind` must equal `INSPECTION_PREDICTION_KIND`.
5. `prediction.raw_measure_kind` must equal `RAW_MEASURE_KIND`.
6. `prediction.predicted_raw_anomaly_measure` must be finite.
7. `prediction.raw_measure_scale` must be non-blank.
8. `prediction.predicted_judgement is InspectionJudgement.DEFECT` must require
   `prediction.predicted_localization`.
9. `prediction.predicted_judgement is InspectionJudgement.OK` must require
   `prediction.predicted_localization is None`.
10. `prediction.model_metadata` must remain frozen and must not carry forbidden
    downstream keys.
11. The assembled `RawInspectionResult` must pass its own contract validation.
12. The existing inspection evidence emitter must emit evidence for the
    canonical raw result.

Prediction construction already enforces most field-level rules. The
Inspection Engine must still validate at the transformation boundary because it
owns acceptance into the deterministic runtime.

## 5. Prediction to RawInspectionResult Mapping

The transformation must map one accepted prediction into one raw result.

| `InspectionPrediction` source | `RawInspectionResult` destination | Rule |
| --- | --- | --- |
| `input_id` | `input_id` | Must match the stabilized input. |
| `prediction_id` | `examination_id` | Must become the source identity inside the existing raw-result contract. |
| `predicted_judgement` | `judgement` | Must be copied without recalibration or reinterpretation. |
| `predicted_localization` | `localization` | Must be copied from the same prediction. |
| `predicted_raw_anomaly_measure` | `raw_anomaly_measure` | Must be copied as raw, uncalibrated substrate. |
| `raw_measure_kind` | `raw_measure_kind` | Must remain exactly `RAW_MEASURE_KIND`, whose value is `"raw_anomaly_measure"`. |
| `raw_measure_scale` | `raw_measure_scale` | Must remain descriptive raw-scale provenance, not confidence. |
| `prediction_kind` | `examination_kind` | Must identify the raw result as prediction-origin examination provenance. |
| engine-owned deterministic identity | `inspection_result_id` | Must be derived deterministically from the accepted prediction and input. |

The raw result must not gain a `prediction_id` field. The existing
`examination_id` slot must carry the accepted prediction's identity because
the raw-result contract must remain the single downstream contract.

The transformation must not reconstruct judgement, localization, or raw measure
from separate sources. The accepted prediction is the single source.

## 6. Transformation Failure Modes

All transformation failures remain inside Inspection. A failure must never be
silently converted into a defect judgement, an OK judgement, a trusted result,
or a review route.

| Failure | Example trigger | Required handling |
| --- | --- | --- |
| Malformed prediction | Object is not `InspectionPrediction`. | Raise an Inspection-domain prediction failure. |
| Input mismatch | Prediction references a different `input_id`. | Raise `InvalidInspectionPrediction`. |
| Invalid localization | Defect prediction lacks localization, OK prediction has localization, or localization geometry is invalid. | Raise `PartialInspectionPrediction` or the existing localization validation error. |
| Invalid raw measure | Raw measure is non-finite or not marked raw. | Raise `InvalidInspectionPrediction`. |
| Unsupported prediction kind | `prediction_kind` is not `INSPECTION_PREDICTION_KIND`. | Raise `InvalidInspectionPrediction`. |
| Incompatible prediction version | A versioned or future prediction kind such as `inspection_prediction_v2` reaches the current transformer. | Raise `InvalidInspectionPrediction`. |
| Raw-result assembly failure | Accepted values cannot form a valid `RawInspectionResult`. | Raise `InvalidInspectionResult`. |
| Evidence emission failure | Raw result exists but evidence cannot be emitted. | Reuse the existing evidence-emission failure path. |

The current prediction contract has no separate version field. Therefore, this
task must treat version-like or future `prediction_kind` values as unsupported
prediction kinds. It must not add version negotiation unless the public
prediction contract is updated first.

## 7. Determinism Requirements

The transformation must be deterministic.

For a fixed stabilized input and fixed accepted prediction:

- the transformed `RawInspectionResult` must be identical across repeated
  transformations;
- the emitted `InspectionEvidenceRecord` must be identical across repeated
  transformations;
- `inspection_result_id` must be stable;
- judgement, localization, raw measure, raw-measure kind, raw-measure scale, and
  source identity must not change;
- no hidden state, time, randomness, process state, or provider state must enter
  the transformation.

The provider's future inference determinism belongs to a later provider-wiring
task. This task owns only deterministic transformation of an already-produced
prediction.

## 8. Runtime Ownership

The Inspection Engine owns:

- prediction acceptance into runtime;
- prediction validation at the transformation boundary;
- `RawInspectionResult` construction;
- deterministic result identity;
- evidence emission for the transformed result;
- the runtime contract exposed downstream.

Machine Learning owns only:

- producing an `InspectionPrediction` behind the provider seam.

Machine Learning does not own:

- `RawInspectionResult`;
- inspection evidence;
- trust qualification;
- review routing;
- evaluation;
- integration orchestration;
- CLI behavior;
- any downstream runtime contract.

## 9. Tests

All tests must be additive and must live in `tests/test_inspection_engine.py`.
Tests must assert contract and boundary behavior, not model quality.

Planned test coverage:

1. A valid OK `InspectionPrediction` transforms into an `InspectionEngineOutput`
   whose `raw_inspection_result` is a `RawInspectionResult`.
2. A valid DEFECT `InspectionPrediction` with localization transforms into a
   localized raw result.
3. The transformed result preserves `raw_measure_kind == RAW_MEASURE_KIND`.
4. The transformed result preserves the single-source mapping from the accepted
   prediction: judgement, localization, raw measure, source identity, kind, and
   scale.
5. The same stabilized input and same prediction produce identical
   `RawInspectionResult` and `InspectionEvidenceRecord` values on repeated
   transformation.
6. A malformed non-`InspectionPrediction` object is rejected.
7. A prediction whose `input_id` does not match the stabilized input is rejected.
8. A prediction with unsupported `prediction_kind` is rejected.
9. A prediction with version-like unsupported `prediction_kind` is rejected.
10. Invalid localization and invalid raw measure failures remain covered by the
    prediction contract tests and must remain green.
11. A structural provider stub's returned prediction does not reach downstream
    directly; only the Inspection Engine's transformed `RawInspectionResult`
    reaches evidence and downstream tests.
12. Existing raw-result canonical tests remain green.
13. Existing Trust tests remain unchanged.
14. Existing Integration tests remain green.
15. Existing CLI tests remain green.

Focused commands for implementation:

```bash
python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
python3 -m pytest tests/test_inspection_engine.py -q
python3 -m pytest tests/test_trust_qualification_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
```

## 10. Integration Impact

The default deterministic inspection path must remain unchanged:

```text
InspectionEngine.inspect(StabilizedInspectionInput)
  -> PlaceholderExamination
  -> RawInspectionResult
  -> InspectionEvidenceRecord
```

The prediction transformation path must be additive:

```text
InspectionPrediction
  -> InspectionEngine-owned validation
  -> RawInspectionResult
  -> InspectionEvidenceRecord
```

No integration or CLI call path must change in this task. Trust, Review,
Evidence, and Evaluation must continue to consume only `RawInspectionResult` and
existing evidence records.

`src/integration/`, CLI code, Trust, Review, Evidence, and Evaluation tests must
remain green without edits.

## 11. Out of Scope

This plan does not authorize:

- a real ML model;
- PyTorch;
- ONNX;
- TensorFlow;
- CoreML;
- OpenVINO;
- datasets;
- inference runtime;
- model loading;
- batching;
- GPU work;
- quantization;
- provider implementation;
- provider wiring into `InspectionEngine`;
- transformation outside Inspection;
- Trust changes;
- Review changes;
- Evidence changes outside the existing inspection evidence emission path;
- Evaluation changes;
- Integration changes;
- CLI changes;
- README changes;
- prototype changes;
- asset or asset-pipeline changes;
- hosted, live, streaming, scheduled, or continuously operating behavior.

## 12. Implementation Steps

Each task is test-first. After each task, run the listed command and report
results. Do not commit.

### Task A: Accept Prediction-Origin Raw-Result Provenance

**Files:**

- Modify: `src/inspection/domain.py`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1 — Failing tests.** Add focused tests proving
  `RawInspectionResult` can represent prediction-origin provenance without new
  downstream fields:
  - `examination_kind == INSPECTION_PREDICTION_KIND`;
  - `raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE`;
  - `raw_measure_kind == RAW_MEASURE_KIND`;
  - no downstream fields are present.

- [ ] **Step 2 — Run focused tests.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result before implementation: failure caused by raw-result contract
  rejection of prediction-origin provenance.

- [ ] **Step 3 — Implement minimal domain acceptance.** Update only the
  Inspection-domain raw-result validation needed for prediction-origin
  provenance. The raw-result shape must not gain fields. Trust-bearing fields
  must remain absent.

- [ ] **Step 4 — Run focused tests again.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result after implementation: focused provenance tests pass.

### Task B: Add Engine-Owned Prediction Transformation

**Files:**

- Modify: `src/inspection/engine.py`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1 — Failing tests.** Add tests proving a valid OK prediction and a
  valid DEFECT prediction transform through the Inspection Engine into
  `InspectionEngineOutput`, with `RawInspectionResult` and
  `InspectionEvidenceRecord` present.

- [ ] **Step 2 — Run focused tests.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result before implementation: failure caused by missing
  InspectionEngine-owned transformation path.

- [ ] **Step 3 — Implement the transformation path inside InspectionEngine.**
  The path must accept a stabilized input and an already-produced
  `InspectionPrediction`; must not accept a provider; must not call a provider;
  must validate the prediction; must transform into `RawInspectionResult`; and
  must reuse the existing evidence-emission path.

- [ ] **Step 4 — Run focused tests again.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result after implementation: valid prediction transformation tests
  pass.

### Task C: Add Transformation Failure Tests

**Files:**

- Modify: `src/inspection/engine.py`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1 — Failing tests.** Add tests proving the transformation path
  rejects:
  - non-`InspectionPrediction` objects;
  - predictions whose `input_id` does not match the stabilized input;
  - unsupported `prediction_kind`;
  - version-like unsupported `prediction_kind`;
  - provider outputs that are not passed through the Inspection Engine
    transformation.

- [ ] **Step 2 — Run focused tests.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result before implementation: failure caused by missing or incomplete
  boundary validation.

- [ ] **Step 3 — Implement minimal boundary validation.** Invalid predictions
  must raise Inspection-domain prediction failures before raw-result assembly.
  No invalid prediction must reach evidence emission or downstream code.

- [ ] **Step 4 — Run focused tests again.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result after implementation: all focused failure tests pass.

### Task D: Verify Determinism and Downstream Isolation

**Files:**

- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1 — Add determinism tests.** Prove the same stabilized input and
  same accepted prediction produce identical `RawInspectionResult` and
  `InspectionEvidenceRecord` values on repeated transformation.

- [ ] **Step 2 — Add downstream isolation assertions.** Prove transformed raw
  results remain canonical and that the Inspection Engine still exposes no
  provider, model, inference runtime, trust qualification, review routing, or
  evaluation behavior.

- [ ] **Step 3 — Run the inspection suite.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -q
  ```

  Expected result: pass.

- [ ] **Step 4 — Run downstream unchanged suites.**

  ```bash
  python3 -m pytest tests/test_trust_qualification_engine.py -q
  python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
  python3 -m pytest tests/test_integration_cli.py -q
  ```

  Expected result: pass.

### Task E: Full Validation Checkpoint

- [ ] **Step 1 — Run focused transformation tests.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k prediction_transformation -q
  ```

  Expected result: pass.

- [ ] **Step 2 — Run the inspection suite.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -q
  ```

  Expected result: pass.

- [ ] **Step 3 — Run repo-wide tests.**

  ```bash
  python3 -m pytest -q
  ```

  Expected result: pass.

- [ ] **Step 4 — Compile source, tests, and scripts.**

  ```bash
  python3 -m compileall -q src tests scripts
  ```

  Expected result: exit 0.

- [ ] **Step 5 — Confirm scope discipline.**

  ```bash
  git status --short
  ```

  Expected result: only intended Inspection files and
  `tests/test_inspection_engine.py` are modified, plus any pre-existing
  in-progress Task 1 files. No changes appear under Trust, Review, Evidence,
  Evaluation, Integration, CLI, scripts, README, assets, or tools.

## Self-Review

- **Spec coverage:** Purpose, scope, transformation boundary, validation
  pipeline, mapping, failure modes, determinism, runtime ownership, tests,
  integration impact, out of scope, and implementation steps are covered.
- **Boundary coverage:** The provider owns only `InspectionPrediction`. The
  Inspection Engine owns validation, transformation, raw result construction,
  and evidence emission. Downstream domains consume only `RawInspectionResult`.
- **Deferred scope coverage:** Models, frameworks, datasets, runtimes, provider
  implementation, provider wiring, Integration, CLI, Trust, Review, Evidence,
  Evaluation, README, prototype, assets, and tools remain out of scope.
- **Placeholder scan:** No placeholder task remains.
