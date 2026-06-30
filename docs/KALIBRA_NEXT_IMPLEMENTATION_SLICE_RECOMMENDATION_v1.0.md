# KALIBRA Next Implementation Slice Recommendation v1.0

## 1. Current Completed Milestones

This recommendation starts from repository HEAD `f320fc3` on
`codex/initial-engineering-skeleton`.

The completed milestones relevant to the next slice are:

- Public foundation, architecture, requirements, evaluation methodology, dataset
  strategy, roadmap, and engineering plan are documented.
- Architecture Phase 1 is closed. The five-domain architecture and deterministic
  substrate foundation are established.
- Engineering Phase 2 is closed. The deterministic runtime chain exists across:
  Inspection, Trust Qualification, Human Review, Evidence, and Evaluation.
- The end-to-end substrate integration layer and developer CLI exist for the
  deterministic default chain.
- The ML Phase 1 inference boundary is documented: providers produce only
  `InspectionPrediction`; the Inspection Engine owns transformation into
  `RawInspectionResult`.
- `InspectionPrediction`, `InspectionInferenceProvider`, and
  `InspectionEngine.transform_prediction(...)` are implemented and tested.
- The deterministic mock inference provider is implemented and tested.
- Shared local artifact helpers were extracted for PGM P2 reading and local
  contrast analysis.
- `LocalArtifactInferenceProvider` is implemented and tested as a deterministic
  standard-library provider over real local PGM content.
- The provider remains unwired from `InspectionEngine.inspect()`, integration,
  and CLI default paths.
- The prototype UI local-provider adapter exists. It renders the real
  `blob_defect.pgm` inspection-only result through
  `LocalArtifactInferenceProvider.predict(...)` and
  `InspectionEngine.transform_prediction(...)`.
- Prototype evidence screenshots under `docs/evidence/prototype-ui/` demonstrate
  the real provider result while explicitly withholding trust, review, drift, and
  evaluation claims for that UI slice.

## 2. Remaining Documented Milestones

The remaining documented milestones fall into three groups.

First, the roadmap still contains the full system capability milestones:

- competent inspection and localization from a real inspection method;
- calibrated trust qualification for every decision;
- human review routing for uncertain and drifted cases;
- evidence-backed evaluation with distinct dimensions and failure categories;
- final end-to-end validation with no claim exceeding its evidence.

Second, Engineering Phase 2 completed deterministic substrate baselines but did
not make those baselines production science:

- Trust Qualification remains deterministic baseline behavior, not production
  calibration science.
- Human Review remains deterministic package and decision-recording behavior,
  not reviewer-quality modelling.
- Evidence remains deterministic in-memory preservation, not persistence or UI.
- Evaluation remains evidence-backed structural reporting, not statistical
  benchmark evaluation.

Third, ML Phase 1 has introduced a real local provider but has not yet composed
that provider result through the already implemented end-to-end chain:

- `LocalArtifactInferenceProvider` is tested through
  `InspectionEngine.transform_prediction(...)`.
- The prototype renders the transformed raw inspection result.
- The canonical integration runner still begins with `InspectionEngine.inspect()`
  and therefore exercises the deterministic default inspection path, not the
  local provider path.
- The real local provider result has not yet been trust-qualified, optionally
  routed to review, preserved into `EvidenceView`, or evaluated from preserved
  evidence inside the canonical integration result.

No current public document selects an external ML framework, model architecture,
training dataset, benchmark, hosted runtime, persistence layer, or production UI
as the next step.

## 3. Dependency Analysis

The dependency order remains load-bearing:

```text
InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> RawInspectionResult
  -> TrustQualificationEngine.qualify(...)
  -> optional Human Review
  -> EvidenceEngine.preserve(...)
  -> EvaluationEngine.evaluate(...)
```

The local provider already satisfies the ML Phase 1 provider boundary. Its output
is an untrusted prediction until the Inspection Engine transforms it. Once
transformed, downstream domains should depend only on `RawInspectionResult` and
its evidence record, not on the provider.

The prototype UI checkpoint intentionally stopped before downstream production:
calibrated confidence, trust qualification, review routing, drift, and evaluation
claims remain absent for the real local provider result. That was correct for the
UI slice, but it now identifies the next architectural gap: the repository has a
real local provider result and a deterministic five-domain chain, but no
documented implementation slice that composes those together.

Provider wiring into `InspectionEngine.inspect()` remains the wrong dependency
move. The existing ML Phase 1 documents repeatedly require the provider to remain
opt-in and transformed only through `InspectionEngine.transform_prediction(...)`.
The integration layer should therefore accept or build a canonical
`InspectionEngineOutput` from the provider path without changing the default
Inspection Engine path.

External ML framework work is also premature. The local provider was introduced
to prove the seam with real local content before any model/runtime dependency.
Adding a framework provider now would broaden the system before the real local
provider has been exercised through the existing evidence chain.

## 4. Recommended Next Implementation Slice

Recommended next slice:

**Local Provider End-to-End Evidence Integration**

Build the smallest opt-in path that runs the existing local provider result
through the already implemented canonical downstream chain:

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

This slice should be integration/evidence focused. It should not update the
prototype UI yet, should not change provider behavior, should not make the
provider the default `InspectionEngine.inspect()` path, and should not alter the
developer CLI default fixture.

## 5. Why This Is The Highest-Priority Slice

This slice is the highest-priority next step because it closes the first real
composition gap after the local-provider checkpoint.

It uses the completed local provider without expanding ML scope. It validates the
ML Phase 1 promise that downstream domains remain unchanged when inference is
provider-origin, because every downstream domain consumes the canonical
`RawInspectionResult`.

It also advances the roadmap in the correct order. The current real provider
prototype demonstrates raw inspection only. The next meaningful capability is not
a new visual demo or a broader model choice; it is proving that the real provider
raw result can be qualified, preserved, and evaluated through the same evidence
chain as the deterministic default substrate.

This gives the repository a stronger, inspectable checkpoint without inflating
claims:

- real local artifact content informs the raw inspection result;
- trust qualification remains a deterministic baseline, not validated
  calibration science;
- review occurs only if the canonical trust result or drift caution requires it;
- evidence is preserved from emitted records, not prototype visuals;
- evaluation reports only from preserved evidence and explicit absence.

## 6. Estimated Implementation Scope

Estimated size: one narrow integration slice.

Expected behavior:

- Keep `InspectionEngine.inspect()` provider-unwired.
- Keep `LocalArtifactInferenceProvider` provider-only; it must still return only
  `InspectionPrediction`.
- Add an opt-in integration path that can compose a precomputed
  `InspectionEngineOutput` or a provider-transformed inspection output through
  Trust, Human Review, Evidence, and Evaluation.
- Use `tests/fixtures/inspection/blob_defect.pgm` as the first real local
  provider fixture.
- Compute the fixture SHA-256 rather than using a placeholder hash.
- Preserve the raw anomaly value `75.0` and raw scale
  `model_raw_anomaly_measure` as raw inspection data.
- Let the existing deterministic Trust baseline qualify the transformed raw
  result.
- Use an explicit deterministic `DriftReference` only in tests that intentionally
  exercise review routing; otherwise record unavailable or absent drift honestly.
- Preserve inspection, trust, and review evidence records when present.
- Preserve explicit absence when review does not occur.
- Produce an `EvidenceBackedEvaluationReport` from the resulting `EvidenceView`.
- Add tests proving no provider object, prediction object, prototype visual, or
  synthetic overlay reaches downstream as performance evidence.

Out of scope:

- external ML frameworks, learned weights, training, datasets, or benchmark
  metrics;
- production calibration or drift science;
- provider wiring into `InspectionEngine.inspect()`;
- integration or CLI default behavior changes unless explicitly reviewed later;
- prototype UI updates;
- persistence, hosted services, live operation, scheduling, monitoring, or
  feedback loops.

## 7. Validation Strategy

Future implementation should validate at least:

```sh
python3 -m pytest tests/test_end_to_end_substrate_integration.py -k local_provider -q
python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest tests/test_inspection_engine.py tests/test_trust_qualification_engine.py tests/test_human_review_engine.py tests/test_evidence_engine.py tests/test_evaluation_engine.py tests/test_end_to_end_substrate_integration.py -q
python3 -m compileall -q src tests scripts
git diff --check
git status --short
```

Review validation should additionally confirm:

- provider output remains `InspectionPrediction`, not `RawInspectionResult`;
- the Inspection Engine owns the transformed `RawInspectionResult`;
- downstream domains never inspect the provider, fixture pixels, or prototype
  artifacts;
- raw anomaly is not presented as calibrated confidence;
- Trust baseline output is not described as production calibration quality;
- Evaluation output does not contain an aggregate score or benchmark claim;
- prototype evidence remains illustrative and is not used as performance
  evidence.

## 8. Files Expected To Change

Expected implementation files:

- `src/integration/engine.py`
- `src/integration/domain.py`, only if a small provenance or alternate-run
  contract is required
- `src/integration/__init__.py`, only if a new opt-in helper is exported
- `tests/test_end_to_end_substrate_integration.py`

Expected files that should not change in the first implementation slice:

- `src/inspection/providers.py`
- `src/inspection/engine.py`, except if a direct contract conflict is surfaced
  before implementation
- `src/trust/`
- `src/review/`
- `src/evidence/`
- `src/evaluation/`
- `scripts/run_end_to_end_substrate.py`
- `assets/`
- `assets/kalibra-prototype/`
- `docs/evidence/prototype-ui/`

If implementation findings show that a broader change is needed, the work should
stop and the repository owner should review a narrower revised plan before code
changes continue.
