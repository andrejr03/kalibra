# Local Provider Path Milestone

## 1. Purpose

This document closes the completed ML Phase 1 local-provider path record.

It records the repository state after the local provider was introduced,
projected into the prototype, composed through the canonical evidence chain, and
hardened at the integration boundary.

This is a milestone document. It is not an implementation plan, a model
selection document, a benchmark report, or a claim of production machine-learning
capability. It records what has been completed and what remains explicitly
unclaimed.

The record is recorded at repository HEAD:

```text
9290814 fix: harden local provider integration boundary
```

## 2. Completed Milestones

The ML Phase 1 local-provider path now includes the following completed
milestones.

### Inference Boundary

The ML Phase 1 inspection inference boundary is documented. Providers produce
only `InspectionPrediction`. The Inspection Engine owns validation,
transformation into `RawInspectionResult`, and inspection evidence emission.

The provider boundary remains one-directional:

```text
InspectionInferenceProvider
  -> InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> RawInspectionResult
```

No provider output is a canonical runtime result until the Inspection Engine has
accepted and transformed it.

### Prediction And Transformation Contract

`InspectionPrediction`, `InspectionInferenceProvider`, and
`InspectionEngine.transform_prediction(...)` exist and are tested.

The transformation path preserves the raw anomaly measure as raw inspection
substrate. It does not calibrate confidence, qualify trust, route review,
preserve downstream evidence, or evaluate performance.

### Deterministic Mock Provider

The deterministic mock inference provider exists as a no-I/O provider proving
the provider seam without artifact reads.

It remains provider-only and returns `InspectionPrediction`.

### Local Artifact Provider

`LocalArtifactInferenceProvider` exists as the first real local provider. It
reads deterministic local PGM P2 artifact content with the Python standard
library and derives an `InspectionPrediction` from real fixture bytes.

Shared local artifact helpers exist for local path resolution, PGM P2 reading,
local contrast analysis, and localization construction.

For the primary fixture:

```text
tests/fixtures/inspection/blob_defect.pgm
```

the local provider path preserves these inspection facts after transformation:

- judgement: `DEFECT`;
- raw anomaly measure: `75.0`;
- raw measure scale: `model_raw_anomaly_measure`;
- examination kind: `inspection_prediction`.

The provider remains unwired from `InspectionEngine.inspect()`.

### Prototype UI Projection

The prototype UI local-provider adapter exists. It builds static prototype data
from the real local-provider result by running:

```text
StabilizedInspectionInput
  -> LocalArtifactInferenceProvider.predict(...)
  -> InspectionEngine.transform_prediction(...)
  -> UI-safe projection
```

The prototype displays the real inspection-only result while explicitly
withholding calibrated confidence, trust qualification, review routing, drift,
and evaluation claims for that UI slice.

Prototype evidence screenshots exist under:

```text
docs/evidence/prototype-ui/
```

Those screenshots demonstrate the prototype rendering only. They are not
performance evidence.

### End-To-End Evidence Integration

The integration layer has an opt-in local-provider fixture path. It runs the
real local-provider result through the canonical downstream chain:

```text
tests/fixtures/inspection/blob_defect.pgm
  -> StabilizedInspectionInput
  -> LocalArtifactInferenceProvider.predict(...)
  -> InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> InspectionEngineOutput
  -> TrustQualificationEngine.qualify(...)
  -> optional Human Review
  -> EvidenceEngine.preserve(...)
  -> EvaluationEngine.evaluate(...)
  -> EndToEndSubstrateIntegrationResult
```

Downstream domains consume only canonical Inspection, Trust, Review, Evidence,
and Evaluation records. They do not consume provider objects, prediction
objects, PGM pixels, prototype artifacts, or screenshots.

### Boundary Hardening

The opt-in local-provider fixture path is cwd-independent. The integration
helper anchors the fixture path before the unchanged provider reads it.

`run_from_inspection_output(...)` has a boundary docstring clarifying that it is
the shared composition core for already-canonical `InspectionEngineOutput`, not
a generic untrusted injection point.

The default deterministic integration path and CLI path remain unchanged.

## 3. Validation Summary

The completed record has been validated through focused and repo-wide test
commands during implementation and hardening review.

Key reported validation:

```text
python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
  9 passed, 83 deselected

python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
  5 passed

python3 -m pytest tests/test_end_to_end_substrate_integration.py -k local_provider -q
  6 passed, 8 deselected

python3 -m pytest tests/test_end_to_end_substrate_integration.py -k "local_provider or default or cli" -q
  7 passed, 8 deselected

python3 -m pytest tests/test_integration_cli.py -q
  5 passed

python3 -m pytest -q
  333 passed

python3 -m compileall -q src tests scripts
  OK

git diff --check
  OK
```

The clean-head validation before this closure document confirmed:

```text
git status --short
  clean

current HEAD
  9290814 fix: harden local provider integration boundary
```

## 4. Architecture Boundary Status

The architecture boundary remains intact.

- `LocalArtifactInferenceProvider` returns only `InspectionPrediction`.
- `InspectionEngine.transform_prediction(...)` owns conversion into
  `RawInspectionResult`.
- `InspectionEngine.inspect()` remains provider-unwired.
- The default integration chain still begins with `InspectionEngine.inspect()`.
- The CLI default path remains unchanged and does not run the local provider.
- Trust Qualification consumes canonical `RawInspectionResult`, not provider
  internals.
- Human Review consumes canonical review-qualified cases only.
- Evidence preserves emitted upstream records, not provider objects or prototype
  visuals.
- Evaluation reads preserved evidence only and does not inspect images or
  provider data.
- Prototype visuals and screenshots remain illustrative and are not used as
  performance evidence.

The integration layer remains a thin composition layer. It is not a sixth domain
and owns no inspection, trust, review, evidence, or evaluation responsibility.

## 5. Explicitly Not Claimed

This record does not claim:

- production machine-learning capability;
- trained model behavior;
- model architecture selection;
- external ML framework selection;
- learned weights;
- training, fine-tuning, retraining, or model update workflows;
- dataset readiness beyond the fixed fixtures already present;
- production computer-vision quality;
- inspection accuracy, precision, recall, AUC, or benchmark performance;
- statistically validated calibration;
- production trust qualification quality;
- production drift science;
- reviewer-quality modelling;
- human-review workflow operation;
- persistence or durable storage beyond in-memory deterministic records and
  checked-in prototype evidence images;
- hosted, live, streaming, scheduled, or continuously operating behavior;
- operational monitoring or alerting;
- feedback loops from review or evaluation into model behavior;
- broad generality beyond the documented fixed local fixtures.

The raw anomaly value `75.0` remains a raw local-provider anomaly measure on the
`model_raw_anomaly_measure` scale. It is not calibrated confidence and must not
be presented as calibrated confidence.

The Trust output produced for the local-provider integration path is the existing
deterministic trust baseline. It is not production calibration science.

The Evaluation output produced for the local-provider integration path is
evidence-backed structural reporting. It is not a benchmark or aggregate
performance claim.

## 6. Remaining Open Decisions

The completed local-provider path closes the first real local content seam, but
it does not answer the next project-scope decisions.

Open decisions:

- Whether ML Phase 1 should stop here as a boundary/proof record or continue
  into another documented provider experiment.
- Whether the next implementation should remain documentation/planning-only until
  a model, framework, dataset, and metric policy are explicitly selected.
- Whether a future provider should use an external inference runtime, and if so
  which runtime is allowed by the offline, local, reproducible architecture.
- What fixed dataset, labels, and provenance evidence would be sufficient before
  any benchmark or production-quality claim can be attempted.
- What calibration evidence is required before any trust output can be described
  as statistically calibrated.
- Whether the prototype should remain an inspection-only demonstration or wait
  until a documented evidence UI/product-surface plan exists.
- Whether a separate Phase 3 planning document should supersede the now-completed
  local-provider recommendation.

None of these decisions is made by this closure document.

## 7. Recommended Next Planning Question

Recommended next planning question:

```text
Should Kalibra enter a new documented ML Phase 2 / Phase 3 planning step for a
framework-backed provider and fixed evaluation dataset, or should implementation
pause until the project owner updates the public scope for model selection,
dataset evidence, calibration evidence, and benchmark policy?
```

The next artifact should be a planning or decision document, not code, unless
the repository owner explicitly approves a new implementation slice with
bounded files, claims, and validation.

## 8. Closure Statement

ML Phase 1 local-provider path record complete.

The repository now has a deterministic, standard-library local provider that
reads real local fixture content, returns only `InspectionPrediction`, is
transformed by the Inspection Engine into canonical raw inspection output, can be
shown in the prototype as inspection-only data, and can be composed through the
canonical evidence chain through an opt-in integration path.

The record proves the boundary and composition path. It does not prove
production ML quality, production inspection quality, calibrated confidence,
review quality, drift response quality, benchmark performance, or product
readiness.
