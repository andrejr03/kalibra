# Kalibra End-to-End Substrate Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` or `superpowers:subagent-driven-development` to
> implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for
> tracking. Repository rules forbid agent-controlled `git add`, `git commit`,
> `git push`, and branch creation.

**Goal:** Build the smallest deterministic integration layer that proves the five
implemented Kalibra substrates compose in the canonical order.

**Architecture:** A thin orchestration layer should call the existing substrate
engines without adding domain behavior of its own. It should preserve each stage
artifact as emitted, pass only canonical substrate contracts across seams, and
return one integrated result that references Inspection, Trust Qualification,
Human Review, Evidence, and Evaluation outputs.

**Tech Stack:** Existing Python dataclasses and engines under `src/`, with
`pytest` coverage in `tests/`.

---

## 1. Purpose

This plan defines a minimal end-to-end integration chain across the five Kalibra
substrates:

```text
Inspection -> Trust Qualification -> Human Review -> Evidence -> Evaluation
```

The purpose is substrate composition only. The future implementation must prove
that the existing implemented boundaries can be exercised in one deterministic
offline flow, with each domain receiving and emitting its own canonical contract.

This is not product functionality. It must not make inspection-quality,
calibration-quality, review-quality, drift-response, or evaluation-performance
claims. It should validate that the substrate handoffs are structurally correct,
traceable, reproducible, and evidence-backed.

Planned implementation surface:

- [ ] Create `src/integration/__init__.py` to expose the integration substrate.
- [ ] Create `src/integration/domain.py` for one integrated result contract.
- [ ] Create `src/integration/engine.py` for the thin orchestration flow.
- [ ] Create `tests/test_end_to_end_substrate_integration.py` for the minimal
      chain and boundary tests.

The integration layer is not a sixth Kalibra domain. It owns no inspection,
qualification, review, evidence, or evaluation responsibility. It only composes
the five existing domains in their documented order.

## 2. Canonical Contract Selection

New integration work must use the substrate contracts implemented in the domain
modules as canonical.

Canonical Inspection contracts:

- `src.inspection.StabilizedInspectionInput`
- `src.inspection.RawInspectionResult`
- `src.inspection.InspectionEvidenceRecord`
- `src.inspection.InspectionEngineOutput`

Canonical Trust Qualification contracts:

- `src.trust.DriftReference`
- `src.trust.CalibratedTrustConfidence`
- `src.trust.UncertaintyCharacterization`
- `src.trust.DriftCaution`
- `src.trust.QualifiedOutcome`
- `src.trust.TrustQualificationResult`
- `src.trust.TrustQualificationEvidenceRecord`
- `src.trust.TrustQualificationEngineOutput`

Canonical Human Review contracts:

- `src.review.ReviewQualifiedCase`
- `src.review.ReviewerDecision`
- `src.review.ReviewerDecisionValue`
- `src.review.ReviewHandoff`
- `src.review.ReviewUpstreamChain`
- `src.review.ReviewEvidenceRecord`
- `src.review.HumanReviewEngineOutput`

Canonical Evidence contracts:

- `src.evidence.InboundEvidenceRecord`
- `src.evidence.EvidenceRecordLink`
- `src.evidence.EvidenceSourceDomain`
- `src.evidence.PreservedEvidenceRecord`
- `src.evidence.EvidenceChainLink`
- `src.evidence.EvidenceAbsenceMarker`
- `src.evidence.EvidenceView`

Canonical Evaluation contracts:

- `src.evaluation.PreservedEvidenceInput`
- `src.evaluation.DimensionFinding`
- `src.evaluation.FailureCategoryFinding`
- `src.evaluation.AbsenceDisclosure`
- `src.evaluation.EvidenceBackedEvaluationReport`

The future integration result should be a new canonical integration contract, for
example `EndToEndSubstrateIntegrationResult`, that references the canonical
objects above rather than translating them into legacy containers.

## 3. Legacy Compatibility Boundary

Legacy contracts remain compatibility-only. They must not be used as the primary
flow for new integration work.

Compatibility-only Inspection contracts:

- `InspectionInput`
- `InspectionResult`
- `DefectJudgment`
- `RawAnomalyScore`

Compatibility-only Trust Qualification contracts:

- `CalibratedConfidence`
- `QualificationOutcome`
- `AbstentionStatus`
- `DriftAssessment`
- `DriftAssessmentStatus`
- `TrustQualifiedResult`
- `TrustQualificationMethod`
- `TrustQualificationEngine._qualify_legacy(...)`

Compatibility-only Human Review contracts:

- `HumanReviewRequest`
- `HumanReviewResult`
- `HumanReviewDecision`
- `ReviewerIdentity`
- `ReviewStatus`
- `HumanReviewMethod`
- `HumanReviewEngine.create_request(...)`
- `HumanReviewEngine.review(...)`
- `HumanReviewEngine.review_request(...)`

Compatibility-only Evidence contracts:

- `EvidenceArtifact`
- `EvidenceReference`
- `EvidenceDomain`
- `EvidenceStatus`
- `EvidenceBundle`
- `EvidenceResult`
- `EvidenceMethod`
- `EvidenceEngine.create_bundle(...)`
- `EvidenceEngine.collect(...)`

Compatibility-only Evaluation contracts:

- `EvaluationFinding`
- `EvaluationReport`
- `EvaluationStatus`
- `EvaluationResult`
- `EvaluationMethod`
- `EvaluationEngine._evaluate_legacy(...)`

The integration layer may leave these contracts available for existing tests and
callers, but must not import or instantiate them for the new end-to-end chain.
Tests for the integration layer should assert that the produced stage artifacts
are canonical substrate objects.

Legacy retirement is deferred. This plan does not remove, rename, weaken, or
migrate legacy contracts. Any retirement plan requires a separate owner-approved
scope.

## 4. Integration Flow

The future implementation should run one deterministic vertical flow:

1. Accept or construct one `StabilizedInspectionInput`.
2. Run `InspectionEngine.inspect(...)`.
3. Pass `inspection_output.raw_inspection_result` to
   `TrustQualificationEngine.qualify(...)`.
4. If the trust result is review-qualified or drifted, run Human Review using a
   deterministic `ReviewerDecision`.
5. Pass emitted inspection, trust, and when present review evidence records to
   `EvidenceEngine.preserve(...)`.
6. Pass the resulting `EvidenceView` to `EvaluationEngine.evaluate(...)`, or to
   `EvaluationEngine.evaluate(PreservedEvidenceInput(...))` when a fixed
   reference-set identifier is needed.
7. Return one integrated result object containing references to each stage.

The deterministic full-chain fixture should use:

- `StabilizedInspectionInput(input_id="integration-input-000",
  artifact_uri="artifact://kalibra/integration/input-000.png",
  content_hash="integration-content-hash-000")`
- `DriftReference(reference_id="integration-drift-reference-001",
  available=True, drift_score=0.8)`
- `ReviewerDecisionValue.INCONCLUSIVE`
- `reviewer_ref="deterministic-reviewer-001"`

With the current placeholder substrates, this fixture exercises Human Review
through drift-aware caution and yields a `review` trust outcome. If the
placeholder implementation changes, the fixture value may be adjusted to preserve
the same structural path; the integration logic must not be adjusted to force a
review outcome artificially.

Planned orchestration responsibilities:

- [ ] Instantiate or accept existing `InspectionEngine`,
      `TrustQualificationEngine`, `HumanReviewEngine`, `EvidenceEngine`, and
      `EvaluationEngine` instances.
- [ ] Execute the stages in the documented order only.
- [ ] Pass each downstream stage the exact upstream object it is documented to
      consume.
- [ ] Store references to stage outputs without mutating or normalizing them.
- [ ] Surface failures explicitly rather than fabricating missing downstream
      artifacts.

## 5. Stage Inputs and Outputs

| Stage | Input | Output kept in integrated result |
| --- | --- | --- |
| Inspection | `StabilizedInspectionInput` | `InspectionEngineOutput`, including `RawInspectionResult` and `InspectionEvidenceRecord` |
| Trust Qualification | `RawInspectionResult`, optional `DriftReference` | `TrustQualificationEngineOutput`, including `TrustQualificationResult` and `TrustQualificationEvidenceRecord` |
| Human Review | `ReviewQualifiedCase`, `ReviewerDecision` | `HumanReviewEngineOutput`, including `ReviewHandoff` and `ReviewEvidenceRecord`; absent when not review-qualified or drifted |
| Evidence | Tuple of emitted upstream evidence records | `EvidenceView` containing preserved records, links, and explicit absences |
| Evaluation | `EvidenceView` or `PreservedEvidenceInput` | `EvidenceBackedEvaluationReport` |

The integrated result should include stable identifiers for each stage:

- source input id;
- inspection result id;
- inspection evidence record id;
- trust qualification result id;
- trust evidence record id;
- review case id, when review occurred;
- review evidence record id, when review occurred;
- evidence view id;
- evaluation report id.

The integrated result must not include a single aggregate trust score or
evaluation score. It should expose stage references and limitations, not flatter
the composed system.

## 6. Evidence Preservation Strategy

Evidence preservation should use records emitted by the upstream engines, not
records fabricated by the integration layer.

Required preservation inputs:

- `inspection_output.inspection_evidence_record`
- `trust_output.trust_qualification_evidence_record`
- `review_output.review_evidence_record`, only when Human Review ran

The integration layer should call:

```text
EvidenceEngine.preserve(
    evidence_records,
    expected_stages=(
        EvidenceSourceDomain.INSPECTION,
        EvidenceSourceDomain.TRUST,
        EvidenceSourceDomain.HUMAN_REVIEW,
    ),
)
```

When review does not occur, `EvidenceEngine` should record an explicit
`human_review` absence marker. The integration layer must not invent a
`ReviewEvidenceRecord` to fill the gap.

The Evidence Engine's adapters may convert upstream records into
`InboundEvidenceRecord` internally. The integration layer should not rely on that
adapter output as its primary contract; its responsibility is to pass genuine
upstream evidence records and consume the resulting `EvidenceView`.

Evidence views must remain read-only. No database, persistence layer, UI surface,
or asset pipeline behavior is part of this integration.

Prototype visuals and synthetic overlays must never be passed as performance
evidence. The integration should use artifact URIs only as stable input
references, not as evidence of model performance.

## 7. Human Review Handling

Human Review should run only when the canonical trust result satisfies at least
one of these conditions:

- `trust_result.qualified_outcome is QualifiedOutcome.REVIEW`
- `trust_result.drift_caution.status is DriftCautionStatus.DRIFTED`

When Human Review runs:

1. Build the case with `HumanReviewEngine.create_case(...)`, passing the exact
   `RawInspectionResult` and `TrustQualificationResult`.
2. Create one deterministic `ReviewerDecision` bound to the returned
   `review_case_id`.
3. Use `HumanReviewEngine.record_decision(...)`.
4. Preserve the emitted `ReviewEvidenceRecord`.

The deterministic reviewer decision should be explicit and conservative:

- `decision=ReviewerDecisionValue.INCONCLUSIVE`
- `reviewer_ref="deterministic-reviewer-001"`
- `rationale="Deterministic integration reviewer decision for substrate composition."`

This decision is not a quality-control label, model update, calibration signal, or
evaluation target. It exists only to exercise the review substrate contract and
its evidence record.

If the trust result is not review-qualified and not drifted, the integration
should skip Human Review and let Evidence record `human_review` absence. It must
not call `HumanReviewEngine.create_case(...)` for an accept, reject, or abstain
result that is not accepted by the canonical review contract.

## 8. Evaluation Handling

Evaluation should consume only the preserved evidence view:

- preferred input: `PreservedEvidenceInput(evidence_view=evidence_view,
  reference_set_id="fixed-end-to-end-substrate-reference-v1")`
- acceptable shorthand: `EvidenceEngine.evaluate(evidence_view)` only if the
  default reference set is acceptable for the test

The expected output is `EvidenceBackedEvaluationReport`.

The report should be treated as a structural, evidence-backed substrate report.
It may show that evidence is present, absent, weak, separated, and traceable. It
must not be presented as final detection quality, final calibration quality, final
review quality, final drift-response quality, or a benchmark.

Tests should verify:

- dimension findings remain separated;
- failure-category findings remain separated when explicit weak-performance
  evidence exists;
- absence disclosures remain distinct from weak-performance findings;
- report evidence references are a subset of the `EvidenceView` records and
  absence markers;
- no single aggregate score exists.

## 9. Failure Modes

The integration layer should surface these failures explicitly:

- Invalid or unstabilized inspection input. Do not run Inspection.
- Inspection failure or non-reproducible inspection output. Do not run Trust.
- Trust qualification failure, calibration failure, raw-result mutation, or
  non-reproducible qualification. Do not run Review, Evidence, or Evaluation.
- Trust output returned as a legacy `TrustQualifiedResult`. Treat this as an
  integration contract violation for the new flow.
- Review required but reviewer decision missing, malformed, or bound to a
  different case. Do not fabricate a reviewer decision.
- Review attempted for a non-review and non-drifted trust result. Surface the
  Human Review error rather than forcing the case.
- Evidence preservation failure, fabricated evidence rejection, prototype
  performance evidence rejection, or non-reproducible preservation. Do not run
  Evaluation.
- Evaluation failure, fabricated evaluation evidence rejection, prototype
  performance evaluation rejection, untraceable finding, or non-reproducible
  evaluation. Do not emit a completed integrated result.
- Missing Human Review evidence for an accepted or rejected case. Preserve as
  explicit absence, not as failure.
- Missing drift reference. Let Trust Qualification record unavailable drift
  caution; do not fabricate drift.

Failures should leave upstream objects unchanged. The integration layer must not
repair, normalize away, or replace a failed domain output.

## 10. Testing Strategy

Create `tests/test_end_to_end_substrate_integration.py`.

Minimum tests:

- Full-chain composition test:
  - use `integration-input-000` and drift score `0.8`;
  - assert Inspection returns `InspectionEngineOutput`;
  - assert Trust returns `TrustQualificationEngineOutput`;
  - assert Trust outcome is `review` and drift status is `drifted`;
  - assert Human Review returns `HumanReviewEngineOutput`;
  - assert Evidence returns an `EvidenceView` with inspection, trust, and review
    records;
  - assert Evaluation returns `EvidenceBackedEvaluationReport`;
  - assert the integrated result references every stage id.
- Canonical-only contract test:
  - assert the integrated result contains `RawInspectionResult`,
    `TrustQualificationResult`, `ReviewEvidenceRecord`, `EvidenceView`, and
    `EvidenceBackedEvaluationReport`;
  - assert it does not contain legacy `InspectionResult`, `TrustQualifiedResult`,
    `HumanReviewResult`, `EvidenceResult`, or `EvaluationResult`.
- Evidence chain test:
  - assert the evidence view includes chain relations for source input to raw
    inspection, raw inspection to trust qualification, trust qualification to
    human review, and review case to reviewer decision.
- No-review branch test:
  - run a deterministic accepted or rejected case without drift;
  - assert Human Review is absent;
  - assert Evidence records a `human_review` absence marker;
  - assert Evaluation reports review evidence absence rather than weak review
    performance.
- Reproducibility test:
  - run the same integration input, drift reference, and reviewer decision twice;
  - assert the integrated result is identical.
- Boundary tests:
  - assert no feedback, model update, database persistence, UI, upstream rerun,
    prototype-performance evidence, or aggregate evaluation score is introduced.

Implementation should not add broad benchmark tests, ML tests, asset tests, or
prototype visual tests for this integration layer.

## 11. Validation Commands

For this planning-only change:

```sh
test -f docs/KALIBRA_END_TO_END_SUBSTRATE_INTEGRATION_PLAN_v1.0.md
git status --short
```

For the future implementation task:

```sh
pytest tests/test_end_to_end_substrate_integration.py
pytest tests/test_inspection_engine.py tests/test_trust_qualification_engine.py tests/test_human_review_engine.py tests/test_evidence_engine.py tests/test_evaluation_engine.py
git status --short
```

The future implementation agent must report any command that cannot be run and
why. Passing tests must not be described as proof of ML performance, calibration
science, review quality, or final evaluation quality.

## 12. Out-of-Scope Items

This plan does not authorize:

- ML implementation;
- computer vision implementation;
- real calibration science;
- real evaluation metrics or benchmark targets;
- UI or evidence presentation surfaces;
- database persistence;
- hosted services or deployment infrastructure;
- live, streaming, scheduled, or continuously operating behavior;
- prototype modification;
- asset modification;
- asset pipeline modification;
- treating prototype visuals as evidence;
- feedback loops from reviewer decisions into model updates;
- model training, retraining, recalibration, or update behavior;
- legacy contracts as the primary integration flow;
- legacy contract retirement;
- broad benchmark suites;
- multiple inspection settings;
- synthetic claims of generality.

The next natural step is review of this end-to-end substrate integration plan
before implementation.
