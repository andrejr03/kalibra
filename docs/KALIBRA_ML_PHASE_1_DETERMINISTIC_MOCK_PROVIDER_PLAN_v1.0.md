# Kalibra ML Phase 1 — Deterministic Mock Inference Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Validation checkpoints are for
> reporting only; the repository owner controls git history.

**Goal:** Add the first concrete `InspectionInferenceProvider` implementation as
a deterministic architecture-validation object that returns only
`InspectionPrediction`.

**Architecture:** The provider proves the one-directional seam
`InspectionInferenceProvider -> InspectionPrediction -> Inspection Engine ->
RawInspectionResult`. It does not become a result owner, evidence owner, trust
owner, review owner, or evaluation owner. The existing Inspection Engine
transformation path remains the only path by which a provider output can become a
canonical raw inspection result.

**Tech Stack:** Existing Python standard-library substrate under
`src/inspection/`; `dataclasses`, `hashlib`, `json`, and existing Inspection
domain contracts. No new dependency.

---

## Interpretation Note

The current repository state is authoritative:

- `InspectionPrediction` already exists in `src/inspection/domain.py`.
- `InspectionInferenceProvider` already exists in `src/inspection/interfaces.py`.
- `InspectionEngine.transform_prediction()` already validates and transforms an
  accepted `InspectionPrediction` into `RawInspectionResult`.
- Existing tests in `tests/test_inspection_engine.py` already cover prediction
  contract validation and transformation boundary behavior.

This task introduces only the first concrete deterministic provider. It must not
wire the provider into the default engine path and must not modify the
integration layer, CLI, Trust, Review, Evidence, or Evaluation.

## 1. Purpose

`DeterministicMockInferenceProvider` exists to validate the ML Phase 1
architecture before any external learning dependency is introduced.

The provider must prove that a concrete implementation can sit behind
`InspectionInferenceProvider`, accept a `StabilizedInspectionInput`, and produce a
valid `InspectionPrediction` that the Inspection Engine can later transform into
the canonical `RawInspectionResult`.

The provider is not a visual-quality claim. Its outputs are deterministic
architecture-validation values only. No result produced through this provider may
be documented or presented as production inspection capability.

## 2. Scope

In scope:

- Create `DeterministicMockInferenceProvider`.
- Implement the existing `InspectionInferenceProvider` protocol.
- Accept only `StabilizedInspectionInput`.
- Produce only `InspectionPrediction`.
- Use deterministic rules derived from stabilized input fields and descriptive
  metadata.
- Add focused provider tests to `tests/test_inspection_engine.py`.
- Export the provider through `src/inspection/__init__.py`.
- Prove the provider output integrates with
  `InspectionEngine.transform_prediction()` without changing the default engine
  path.

Planned future implementation files:

- Create: `src/inspection/providers.py`
- Modify: `src/inspection/__init__.py`
- Modify: `tests/test_inspection_engine.py`

Explicitly out of scope:

- `README.md`
- prototype code
- `assets/`
- asset pipeline code
- `src/integration/`
- CLI code
- `src/trust/`
- `src/review/`
- `src/evidence/`
- `src/evaluation/`
- `src/inspection/engine.py`, unless a direct conflict is found with the current
  `transform_prediction()` contract and surfaced to the repository owner first

## 3. Provider Responsibilities

`DeterministicMockInferenceProvider` must own only these responsibilities:

- Validate that its input is a `StabilizedInspectionInput`.
- Deterministically derive one prediction payload from that input.
- Construct and return one `InspectionPrediction`.
- Keep all deterministic constants local, explicit, and stable.
- Surface malformed input as an Inspection-domain failure.

The provider may include a provider identifier such as
`deterministic-mock-inference-provider-v1`. That identifier is descriptive
provenance for deterministic replay; it does not create trust, calibration,
review, evidence, or evaluation authority.

## 4. Provider Non-Responsibilities

`DeterministicMockInferenceProvider` must not:

- return `RawInspectionResult`;
- construct `RawInspectionResult`;
- emit `InspectionEvidenceRecord`;
- qualify trust;
- expose calibrated confidence;
- abstain;
- assess drift;
- route review;
- evaluate;
- persist records;
- update itself;
- mutate stabilized input;
- call `InspectionEngine`;
- call `transform_prediction()`;
- change any downstream domain;
- become the default `InspectionEngine` path.

The provider output remains an untrusted, non-canonical prediction until the
Inspection Engine validates and transforms it.

## 5. Deterministic Prediction Rules

The provider must use deterministic rules only.

Required deterministic inputs:

- `inspection_input.input_id`
- `inspection_input.artifact_uri`
- `inspection_input.content_hash`
- `inspection_input.input_kind`
- `inspection_input.intake_status`
- sorted `inspection_input.metadata`
- provider identifier

Required canonicalization:

- Build one plain mapping from the fields above.
- Serialize it with sorted keys and stable separators.
- Hash the serialized payload with SHA-256.
- Derive every prediction value from the resulting digest and fixed constants.
- Do not use time, process state, object identity, randomness, environment
  variables, file system state, network state, or hidden mutable state.

Required prediction derivation:

- `predicted_raw_anomaly_measure` must be a finite numeric value in a stable
  raw 0-to-100 range, rounded to a fixed precision.
- `predicted_judgement` must be `InspectionJudgement.DEFECT` when the raw measure
  is greater than or equal to a fixed threshold, otherwise
  `InspectionJudgement.OK`.
- `predicted_localization` must be present only for `DEFECT` predictions.
- Defect localization must be derived from digest segments into a normalized
  bounding box with ordered finite coordinates.
- OK predictions must use `predicted_localization=None`.
- `prediction_id` must be a stable digest-derived identifier prefixed with a
  provider-specific label.

The fixed threshold, localization width, localization height, and coordinate
offset constants must be explicit provider constants. Changing those constants is
a behavior change and must be covered by tests.

## 6. Prediction Construction

The provider must construct `InspectionPrediction` directly.

Required field mapping:

| `InspectionPrediction` field | Required source |
| --- | --- |
| `input_id` | `inspection_input.input_id` |
| `prediction_id` | stable provider-prefixed digest identifier |
| `predicted_judgement` | deterministic threshold rule |
| `predicted_raw_anomaly_measure` | deterministic digest-derived raw measure |
| `predicted_localization` | deterministic digest-derived localization for defects, otherwise `None` |
| `raw_measure_kind` | existing `InspectionPrediction` default |
| `raw_measure_scale` | existing `InspectionPrediction` default |
| `prediction_kind` | existing `InspectionPrediction` default |
| `model_metadata` | descriptive string metadata only, using ordinary keys such as `method` and `version` |

The provider must not add trust, calibrated confidence, review, evidence,
evaluation, outcome, or target meaning to `model_metadata`. Existing metadata
guards must reject any forbidden downstream key if one is accidentally introduced.

## 7. Failure Modes

Failures must remain inside the Inspection domain and must not be converted into
a judgement.

Required failure behavior:

| Failure | Required handling |
| --- | --- |
| Input is not `StabilizedInspectionInput` | Raise `MalformedInspectionInput`. |
| Stabilized input was already invalid | Rely on existing `StabilizedInspectionInput` construction guards. |
| Digest-derived values cannot form a valid prediction | Let `InspectionPrediction` raise the existing prediction error. |
| Digest-derived localization cannot form valid normalized bounds | Let existing localization validation raise the existing Inspection-domain error. |
| Provider result is accidentally changed to a non-prediction object | Tests must fail before any downstream transformation. |
| Provider gains evidence, trust, review, persistence, update, or evaluation methods | Tests must fail. |

The provider must not catch a prediction construction failure and replace it with
an OK or defect judgement.

## 8. Tests

All tests must be additive and belong in `tests/test_inspection_engine.py`.

Required focused tests:

- `DeterministicMockInferenceProvider` can be imported from `src.inspection`.
- The provider is assignable to `InspectionInferenceProvider`.
- `provider.predict(stabilized_input)` returns an `InspectionPrediction`.
- The returned object is never a `RawInspectionResult`.
- The same provider instance and same input produce identical
  `InspectionPrediction` values.
- Separate provider instances and the same input produce identical
  `InspectionPrediction` values.
- Different stable input identity or content hash can produce a different stable
  prediction, while still returning a valid `InspectionPrediction`.
- DEFECT predictions include localization.
- OK predictions do not include localization.
- Returned predictions expose no downstream fields.
- The provider exposes no `qualify`, `calibrate`, `route_for_review`, `emit`,
  `evaluate`, `persist`, or `update_model` behavior.
- Passing a non-`StabilizedInspectionInput` raises `MalformedInspectionInput`.
- `InspectionEngine().transform_prediction(input, provider.predict(input))`
  returns an `InspectionEngineOutput` whose raw result is a
  `RawInspectionResult`.
- The transformed raw result preserves prediction-origin provenance through the
  existing transformation contract.
- The default `InspectionEngine().inspect(input)` path remains unchanged and
  remains independent of the provider.
- Existing integration tests remain green.
- Existing CLI tests remain green.
- The repo-wide suite remains green.

Focused commands for implementation:

```bash
python3 -m pytest tests/test_inspection_engine.py -k deterministic_mock_inference_provider -q
python3 -m pytest tests/test_inspection_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
```

## 9. Integration Impact

The implementation must have no integration or CLI impact.

The existing default path remains:

```text
InspectionEngine.inspect(StabilizedInspectionInput)
  -> existing examiner
  -> RawInspectionResult
  -> InspectionEvidenceRecord
```

The provider validation path is test-only unless a later public plan authorizes
wiring:

```text
DeterministicMockInferenceProvider.predict(StabilizedInspectionInput)
  -> InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> RawInspectionResult
  -> InspectionEvidenceRecord
```

The provider must not be added to integration orchestration or CLI selection.
Trust, Review, Evidence, and Evaluation must continue to consume only existing
canonical outputs.

## 10. Out of Scope

This task does not authorize:

- changes to public README documentation;
- changes to prototype code;
- changes to assets or asset-pipeline code;
- integration changes;
- CLI changes;
- Trust changes;
- Review changes;
- Evidence changes;
- Evaluation changes;
- provider wiring into the default `InspectionEngine.inspect()` path;
- persistence;
- hosted, live, scheduled, streaming, or continuously operating behavior;
- operational alerting;
- feedback loops;
- quality, benchmark, calibration, review-quality, or drift-response claims;
- any external learning dependency.

## 11. Implementation Steps

### Task A: Add Provider-Focused Failing Tests

**Files:**

- Modify: `tests/test_inspection_engine.py`

- [ ] Add tests named with the prefix
  `test_deterministic_mock_inference_provider_`.
- [ ] Assert import/export through `src.inspection`.
- [ ] Assert provider protocol shape by assigning the provider to
  `InspectionInferenceProvider`.
- [ ] Assert same-input determinism for one provider instance and for two
  provider instances.
- [ ] Assert the provider returns only `InspectionPrediction`, never
  `RawInspectionResult`.
- [ ] Assert provider boundary exclusions: no evidence, trust, review,
  evaluation, persistence, update, or calibration methods.
- [ ] Assert malformed input raises `MalformedInspectionInput`.
- [ ] Run
  `python3 -m pytest tests/test_inspection_engine.py -k deterministic_mock_inference_provider -q`.
- [ ] Expected pre-implementation result: failure caused by missing provider
  import or missing provider behavior.

### Task B: Add `DeterministicMockInferenceProvider`

**Files:**

- Create: `src/inspection/providers.py`

- [ ] Define `DeterministicMockInferenceProvider` as a small frozen dataclass.
- [ ] Give it an explicit provider identifier and fixed deterministic constants.
- [ ] Implement `predict(inspection_input)` with the deterministic rules in §5.
- [ ] Use only existing Inspection-domain contracts to construct the prediction.
- [ ] Keep helper functions private to `src/inspection/providers.py`.
- [ ] Do not import `InspectionEngine`.
- [ ] Do not construct `RawInspectionResult` or `InspectionEvidenceRecord`.
- [ ] Run
  `python3 -m pytest tests/test_inspection_engine.py -k deterministic_mock_inference_provider -q`.
- [ ] Expected result after implementation: focused provider tests pass except
  export tests until Task C is complete.

### Task C: Export the Provider

**Files:**

- Modify: `src/inspection/__init__.py`

- [ ] Import `DeterministicMockInferenceProvider` from
  `src/inspection/providers.py`.
- [ ] Add `DeterministicMockInferenceProvider` to `__all__`.
- [ ] Do not alter existing exports.
- [ ] Run
  `python3 -m pytest tests/test_inspection_engine.py -k deterministic_mock_inference_provider -q`.
- [ ] Expected result: focused provider tests pass.

### Task D: Prove Transformation Compatibility Without Wiring

**Files:**

- Modify: `tests/test_inspection_engine.py`

- [ ] Add a test that calls `provider.predict(input)` and then explicitly calls
  `InspectionEngine().transform_prediction(input, prediction)`.
- [ ] Assert the transformed output is `InspectionEngineOutput`.
- [ ] Assert the transformed raw result is `RawInspectionResult`.
- [ ] Assert the provider did not emit evidence; evidence is emitted only by the
  Inspection Engine transformation path.
- [ ] Assert `InspectionEngine()` still has no provider, model, or predict
  attribute.
- [ ] Run `python3 -m pytest tests/test_inspection_engine.py -q`.
- [ ] Expected result: inspection tests pass.

### Task E: Verify Downstream and Repository Scope

- [ ] Run `python3 -m pytest tests/test_end_to_end_substrate_integration.py -q`.
- [ ] Run `python3 -m pytest tests/test_integration_cli.py -q`.
- [ ] Run `python3 -m pytest -q`.
- [ ] Run `python3 -m compileall -q src tests scripts`.
- [ ] Run `git status --short`.
- [ ] Expected changed files: `src/inspection/providers.py`,
  `src/inspection/__init__.py`, and `tests/test_inspection_engine.py`.
- [ ] Expected unchanged areas: `README.md`, prototype, assets, asset pipeline,
  integration, CLI, Trust, Review, Evidence, and Evaluation.
- [ ] Report results to the repository owner. Do not commit.

## Self-Review

- **Purpose covered:** The provider validates the architecture, not inspection
  quality.
- **Scope covered:** Only a concrete deterministic provider, export, and tests
  are planned.
- **Responsibilities covered:** The provider returns only `InspectionPrediction`.
- **Non-responsibilities covered:** Raw result, evidence, trust, review,
  evaluation, persistence, and update behavior remain forbidden.
- **Determinism covered:** Every output derives from canonicalized input fields,
  sorted metadata, fixed constants, and SHA-256.
- **Prediction construction covered:** Existing `InspectionPrediction` defaults
  remain the boundary contract.
- **Failure modes covered:** Malformed input and invalid prediction construction
  remain explicit Inspection-domain failures.
- **Tests covered:** Determinism, provider isolation, transformation
  compatibility, unchanged default runtime, integration, CLI, and repo-wide suite
  are covered.
- **Integration impact covered:** No wiring or downstream change is planned.
- **Out of scope covered:** Deferred and forbidden scope remains deferred.
