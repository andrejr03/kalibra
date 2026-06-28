from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from src.inspection import (
    DefectJudgment,
    DefectLocalization,
    InspectionInput,
    InspectionJudgement,
    InspectionResult,
    NormalizedBoundingBox,
    RawAnomalyScore,
    RawInspectionResult,
)
from src.trust import (
    AbstentionStatus,
    CalibratedTrustConfidence,
    CalibrationFailure,
    CalibratedConfidence,
    DriftCautionStatus,
    DriftAssessment,
    DriftAssessmentStatus,
    DriftReference,
    InvalidTrustQualificationResult,
    MalformedRawInspectionResult,
    NonReproducibleTrustQualification,
    PLACEHOLDER_CALIBRATION_KIND,
    QualifiedOutcome,
    QualificationOutcome,
    RawInspectionMutationError,
    TrustEvidenceEmissionFailure,
    DeterministicPlaceholderCalibrator,
    DeterministicTrustBaselineCalibrator,
    TrustQualificationEngine,
    TrustQualificationEngineOutput,
    TrustQualificationEvidenceRecord,
    TrustQualificationResult,
    TrustQualifiedResult,
)


EXPECTED_BASELINE_CALIBRATION_KIND = "deterministic_rule_based_trust_baseline_v1"
LOW_BASELINE_UNCERTAINTY_RATIONALE = (
    "Deterministic trust baseline confidence is far from the raw decision "
    "boundary."
)
ELEVATED_BASELINE_UNCERTAINTY_RATIONALE = (
    "Deterministic trust baseline confidence is near the raw decision boundary."
)
HIGH_BASELINE_UNCERTAINTY_RATIONALE = (
    "Deterministic trust baseline confidence is too close to the raw decision "
    "boundary."
)


def make_inspection_result() -> InspectionResult:
    inspection_input = InspectionInput(
        source_path=Path("part.png"),
        content_sha256="abc123",
        media_type="image/png",
        size_bytes=10,
    )
    return InspectionResult(
        inspection_input=inspection_input,
        judgment=DefectJudgment.DEFECTIVE,
        raw_anomaly_score=RawAnomalyScore(
            value=42.0,
            scale="method-specific-distance",
        ),
        localizations=(
            DefectLocalization(
                region=NormalizedBoundingBox(
                    x_min=0.1,
                    y_min=0.1,
                    x_max=0.5,
                    y_max=0.5,
                )
            ),
        ),
        method_id="inspection-method",
        method_version="1",
    )


def make_raw_result(
    raw_measure: float = 5.0,
    judgement: InspectionJudgement = InspectionJudgement.OK,
    result_id: str = "raw-result-1",
) -> RawInspectionResult:
    localization = None
    if judgement is InspectionJudgement.DEFECT:
        localization = DefectLocalization(
            region=NormalizedBoundingBox(
                x_min=0.1,
                y_min=0.1,
                x_max=0.5,
                y_max=0.5,
            )
        )
    return RawInspectionResult(
        inspection_result_id=result_id,
        input_id="input-raw-1",
        judgement=judgement,
        localization=localization,
        raw_anomaly_measure=raw_measure,
        examination_id="examination-raw-1",
    )


class RecordingTrustQualificationMethod:
    method_id = "recording-trust-method"
    method_version = "1"

    def __init__(
        self,
        outcome: QualificationOutcome = QualificationOutcome.ACCEPT,
        abstention_status: AbstentionStatus = AbstentionStatus.NOT_ABSTAINED,
        drift_status: DriftAssessmentStatus = DriftAssessmentStatus.NOT_ASSESSED,
    ) -> None:
        self.outcome = outcome
        self.abstention_status = abstention_status
        self.drift_status = drift_status
        self.seen_result: InspectionResult | None = None

    def qualify(self, inspection_result: InspectionResult) -> TrustQualifiedResult:
        self.seen_result = inspection_result
        return TrustQualifiedResult(
            inspection_result=inspection_result,
            calibrated_confidence=CalibratedConfidence(
                value=0.8,
                method_id=self.method_id,
                method_version=self.method_version,
            ),
            qualification_outcome=self.outcome,
            abstention_status=self.abstention_status,
            drift_assessment=DriftAssessment(
                status=self.drift_status,
                method_id=self.method_id,
                method_version=self.method_version,
            ),
            method_id=self.method_id,
            method_version=self.method_version,
        )


def test_inspection_result_can_be_qualified_without_mutation():
    inspection_result = make_inspection_result()
    method = RecordingTrustQualificationMethod()

    qualified = TrustQualificationEngine(method=method).qualify(inspection_result)

    assert method.seen_result == inspection_result
    assert qualified.inspection_result is inspection_result
    assert qualified.inspection_result == make_inspection_result()
    assert qualified.calibrated_confidence.value == 0.8
    assert qualified.qualification_outcome is QualificationOutcome.ACCEPT


def test_valid_raw_result_produces_one_trust_qualification_result():
    raw_result = make_raw_result()

    output = TrustQualificationEngine().qualify(raw_result)

    assert isinstance(output, TrustQualificationEngineOutput)
    assert isinstance(output.trust_qualification_result, TrustQualificationResult)
    assert output.trust_qualification_result.inspection_result_id == (
        raw_result.inspection_result_id
    )
    assert output.trust_qualification_result.input_id == raw_result.input_id


def test_raw_anomaly_measure_is_not_exposed_as_calibrated_confidence():
    raw_result = make_raw_result(raw_measure=5.0)

    qualification = TrustQualificationEngine().qualify(
        raw_result
    ).trust_qualification_result

    assert raw_result.raw_anomaly_measure == 5.0
    assert qualification.calibrated_confidence.value == 0.9
    assert not hasattr(qualification, "raw_anomaly_measure")


def test_calibrated_confidence_is_explicitly_marked_calibrated():
    qualification = TrustQualificationEngine().qualify(
        make_raw_result()
    ).trust_qualification_result

    assert qualification.confidence_kind == "calibrated_confidence"
    assert qualification.calibrated_confidence.confidence_kind == (
        "calibrated_confidence"
    )
    assert qualification.calibrated_confidence.calibration_kind == (
        EXPECTED_BASELINE_CALIBRATION_KIND
    )


def test_deterministic_trust_baseline_confidence_is_distinct_from_raw_anomaly():
    raw_result = make_raw_result(raw_measure=5.0)

    qualification = TrustQualificationEngine().qualify(
        raw_result
    ).trust_qualification_result

    assert raw_result.raw_anomaly_measure == 5.0
    assert qualification.calibrated_confidence.value == 0.9
    assert not hasattr(qualification, "raw_anomaly_measure")
    assert (
        qualification.calibrated_confidence.calibration_kind
        == EXPECTED_BASELINE_CALIBRATION_KIND
    )


def test_deterministic_trust_baseline_calibrator_is_default():
    engine = TrustQualificationEngine()

    assert isinstance(engine.calibrator, DeterministicTrustBaselineCalibrator)


def test_deterministic_trust_baseline_calibrator_examples():
    calibrator = DeterministicTrustBaselineCalibrator()

    examples = (
        (5.0, 0.9),
        (35.0, 0.3),
        (49.0, 0.02),
        (95.0, 0.9),
    )
    for raw_measure, expected_confidence in examples:
        confidence = calibrator.calibrate(
            make_raw_result(raw_measure=raw_measure)
        )
        assert confidence.value == expected_confidence
        assert confidence.calibration_kind == EXPECTED_BASELINE_CALIBRATION_KIND


def test_placeholder_calibrator_remains_available_as_compatibility_surface():
    confidence = DeterministicPlaceholderCalibrator().calibrate(
        make_raw_result(raw_measure=5.0)
    )

    assert confidence.value == 0.9
    assert confidence.calibration_kind == PLACEHOLDER_CALIBRATION_KIND


def test_deterministic_trust_baseline_same_raw_result_is_reproducible():
    engine = TrustQualificationEngine()
    raw_result = make_raw_result(raw_measure=5.0)

    first = engine.qualify(raw_result)
    second = engine.qualify(raw_result)

    assert first == second
    assert first.trust_qualification_result == second.trust_qualification_result
    assert (
        first.trust_qualification_evidence_record
        == second.trust_qualification_evidence_record
    )


def test_deterministic_trust_baseline_drift_changes_caution_not_raw_result():
    raw_result = make_raw_result(
        raw_measure=5.0,
        judgement=InspectionJudgement.OK,
    )
    raw_before = deepcopy(raw_result)

    without_drift = TrustQualificationEngine().qualify(
        raw_result
    ).trust_qualification_result
    with_drift = TrustQualificationEngine().qualify(
        raw_result,
        drift_reference=DriftReference(
            reference_id="baseline-drift-reference-1",
            available=True,
            drift_score=0.9,
        ),
    ).trust_qualification_result

    assert without_drift.qualified_outcome is QualifiedOutcome.ACCEPT
    assert with_drift.calibrated_confidence == without_drift.calibrated_confidence
    assert with_drift.qualified_outcome is QualifiedOutcome.REVIEW
    assert with_drift.drift_caution.status is DriftCautionStatus.DRIFTED
    assert with_drift.drift_caution.caution_applied is True
    assert raw_result == raw_before


def test_deterministic_trust_baseline_review_and_abstain_are_outcomes():
    review = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=35.0)
    ).trust_qualification_result
    abstain = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=49.0)
    ).trust_qualification_result

    assert review.qualified_outcome is QualifiedOutcome.REVIEW
    assert abstain.qualified_outcome is QualifiedOutcome.ABSTAIN


def test_deterministic_trust_baseline_uncertainty_rationales():
    low = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=5.0)
    ).trust_qualification_result
    elevated = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=35.0)
    ).trust_qualification_result
    high = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=49.0)
    ).trust_qualification_result

    assert (
        low.uncertainty_characterization.rationale
        == LOW_BASELINE_UNCERTAINTY_RATIONALE
    )
    assert (
        elevated.uncertainty_characterization.rationale
        == ELEVATED_BASELINE_UNCERTAINTY_RATIONALE
    )
    assert (
        high.uncertainty_characterization.rationale
        == HIGH_BASELINE_UNCERTAINTY_RATIONALE
    )


def test_deterministic_trust_baseline_malformed_input_fails_explicitly():
    with pytest.raises(MalformedRawInspectionResult):
        TrustQualificationEngine().qualify(object())  # type: ignore[arg-type]


def test_deterministic_trust_baseline_calibration_failure_emits_no_abstain():
    class FailingCalibrator:
        def calibrate(self, raw_result: RawInspectionResult) -> object:
            raise CalibrationFailure("baseline calibration unavailable")

    class RecordingEvidenceEmitter:
        def __init__(self) -> None:
            self.emitted: list[TrustQualificationResult] = []

        def emit(
            self,
            raw_result: RawInspectionResult,
            qualification: TrustQualificationResult,
        ) -> object:
            self.emitted.append(qualification)
            return object()

    evidence_emitter = RecordingEvidenceEmitter()

    with pytest.raises(CalibrationFailure):
        TrustQualificationEngine(
            calibrator=FailingCalibrator(),
            evidence_emitter=evidence_emitter,
        ).qualify(make_raw_result(raw_measure=49.0))

    assert evidence_emitter.emitted == []


def test_deterministic_trust_baseline_evidence_preserves_raw_and_qualification():
    raw_result = make_raw_result(raw_measure=5.0)

    output = TrustQualificationEngine().qualify(raw_result)

    assert output.trust_qualification_evidence_record.raw_inspection_result == (
        raw_result
    )
    assert (
        output.trust_qualification_evidence_record.trust_qualification_result
        == output.trust_qualification_result
    )


def test_deterministic_trust_baseline_exposes_no_out_of_scope_behavior():
    engine = TrustQualificationEngine()

    assert not hasattr(engine, "inspect")
    assert not hasattr(engine, "inspect_image")
    assert not hasattr(engine, "inspect_path")
    assert not hasattr(engine, "review")
    assert not hasattr(engine, "route_for_review")
    assert not hasattr(engine, "present_evidence")
    assert not hasattr(engine, "evaluate")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "update")
    assert not hasattr(engine, "update_model")
    assert not hasattr(engine, "persist")
    assert not hasattr(engine, "save")
    assert not hasattr(engine, "store")
    assert not hasattr(engine, "render")
    assert not hasattr(engine, "ui")
    assert not hasattr(engine, "prototype_asset")


def test_raw_qualified_outcomes_are_explicit_and_complete():
    assert {outcome.value for outcome in QualifiedOutcome} == {
        "accept",
        "reject",
        "review",
        "abstain",
    }


def test_accept_reject_review_and_abstain_can_be_produced():
    accept = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=5.0, judgement=InspectionJudgement.OK)
    ).trust_qualification_result
    reject = TrustQualificationEngine().qualify(
        make_raw_result(
            raw_measure=95.0,
            judgement=InspectionJudgement.DEFECT,
            result_id="raw-result-defect",
        )
    ).trust_qualification_result
    review = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=35.0, judgement=InspectionJudgement.OK)
    ).trust_qualification_result
    abstain = TrustQualificationEngine().qualify(
        make_raw_result(raw_measure=49.0, judgement=InspectionJudgement.OK)
    ).trust_qualification_result

    assert accept.qualified_outcome is QualifiedOutcome.ACCEPT
    assert reject.qualified_outcome is QualifiedOutcome.REJECT
    assert review.qualified_outcome is QualifiedOutcome.REVIEW
    assert abstain.qualified_outcome is QualifiedOutcome.ABSTAIN


def test_missing_drift_reference_is_absence_not_failure():
    qualification = TrustQualificationEngine().qualify(
        make_raw_result()
    ).trust_qualification_result

    assert qualification.drift_caution.status is DriftCautionStatus.UNAVAILABLE
    assert qualification.drift_caution.absence_reason == (
        "drift_reference_unavailable"
    )


def test_deterministic_trust_baseline_drift_status_rules():
    engine = TrustQualificationEngine()
    raw_result = make_raw_result(raw_measure=5.0, judgement=InspectionJudgement.OK)

    none_reference = engine.qualify(raw_result).trust_qualification_result
    unavailable = engine.qualify(
        raw_result,
        drift_reference=DriftReference(
            reference_id="drift-reference-unavailable",
            available=False,
        ),
    ).trust_qualification_result
    in_distribution = engine.qualify(
        raw_result,
        drift_reference=DriftReference(
            reference_id="drift-reference-in-distribution",
            available=True,
            drift_score=0.59,
        ),
    ).trust_qualification_result
    drifted = engine.qualify(
        raw_result,
        drift_reference=DriftReference(
            reference_id="drift-reference-drifted",
            available=True,
            drift_score=0.6,
        ),
    ).trust_qualification_result

    assert none_reference.drift_caution.status is DriftCautionStatus.UNAVAILABLE
    assert none_reference.drift_caution.caution_applied is False
    assert unavailable.drift_caution.status is DriftCautionStatus.UNAVAILABLE
    assert unavailable.drift_caution.caution_applied is False
    assert (
        in_distribution.drift_caution.status
        is DriftCautionStatus.IN_DISTRIBUTION
    )
    assert in_distribution.drift_caution.caution_applied is False
    assert in_distribution.qualified_outcome is QualifiedOutcome.ACCEPT
    assert drifted.drift_caution.status is DriftCautionStatus.DRIFTED
    assert drifted.drift_caution.caution_applied is True
    assert drifted.qualified_outcome is QualifiedOutcome.REVIEW
    assert drifted.calibrated_confidence == none_reference.calibrated_confidence


def test_drift_caution_can_increase_caution_without_mutating_raw_result():
    raw_result = make_raw_result(raw_measure=5.0, judgement=InspectionJudgement.OK)
    raw_before = deepcopy(raw_result)

    without_drift = TrustQualificationEngine().qualify(
        raw_result
    ).trust_qualification_result
    with_drift = TrustQualificationEngine().qualify(
        raw_result,
        drift_reference=DriftReference(
            reference_id="drift-reference-1",
            available=True,
            drift_score=0.9,
        ),
    ).trust_qualification_result

    assert without_drift.qualified_outcome is QualifiedOutcome.ACCEPT
    assert with_drift.qualified_outcome is QualifiedOutcome.REVIEW
    assert with_drift.drift_caution.caution_applied is True
    assert raw_result == raw_before


def test_raw_inspection_result_is_unchanged_after_qualification():
    raw_result = make_raw_result(raw_measure=95.0, judgement=InspectionJudgement.DEFECT)
    raw_before = deepcopy(raw_result)

    TrustQualificationEngine().qualify(raw_result)

    assert raw_result == raw_before


def test_trust_evidence_record_preserves_raw_result_and_qualification():
    raw_result = make_raw_result()

    output = TrustQualificationEngine().qualify(raw_result)
    qualification = output.trust_qualification_result
    evidence = output.trust_qualification_evidence_record

    assert isinstance(evidence, TrustQualificationEvidenceRecord)
    assert evidence.raw_inspection_result == raw_result
    assert evidence.trust_qualification_result == qualification
    assert evidence.inspection_result_id == raw_result.inspection_result_id
    assert evidence.qualification_result_id == qualification.qualification_result_id


def test_raw_trust_engine_does_not_require_or_inspect_images():
    engine = TrustQualificationEngine()

    output = engine.qualify(make_raw_result())

    assert output.trust_qualification_result.input_id == "input-raw-1"
    assert not hasattr(engine, "inspect")
    assert not hasattr(engine, "inspect_path")


def test_raw_trust_engine_exposes_no_downstream_or_model_behaviour():
    engine = TrustQualificationEngine()

    assert not hasattr(engine, "review")
    assert not hasattr(engine, "route_for_review")
    assert not hasattr(engine, "present_evidence")
    assert not hasattr(engine, "evaluate")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "update_model")


def test_same_raw_input_produces_identical_qualification_and_record():
    engine = TrustQualificationEngine()
    raw_result = make_raw_result()

    first = engine.qualify(raw_result)
    second = engine.qualify(raw_result)

    assert first.trust_qualification_result == second.trust_qualification_result
    assert (
        first.trust_qualification_evidence_record
        == second.trust_qualification_evidence_record
    )


def test_malformed_raw_inspection_result_is_refused():
    with pytest.raises(MalformedRawInspectionResult):
        TrustQualificationEngine().qualify(object())  # type: ignore[arg-type]


def test_calibration_failure_is_explicit_and_not_disguised_as_abstain():
    class FailingCalibrator:
        def calibrate(self, raw_result: RawInspectionResult) -> object:
            raise RuntimeError("calibration unavailable")

    with pytest.raises(CalibrationFailure):
        TrustQualificationEngine(calibrator=FailingCalibrator()).qualify(
            make_raw_result(raw_measure=49.0)
        )


def test_evidence_emission_failure_is_explicit():
    class FailingEvidenceEmitter:
        def emit(
            self,
            raw_result: RawInspectionResult,
            qualification: TrustQualificationResult,
        ) -> object:
            return object()

    with pytest.raises(TrustEvidenceEmissionFailure):
        TrustQualificationEngine(evidence_emitter=FailingEvidenceEmitter()).qualify(
            make_raw_result()
        )


def test_detectable_raw_result_mutation_is_refused():
    class MutatingCalibrator:
        def calibrate(
            self, raw_result: RawInspectionResult
        ) -> CalibratedTrustConfidence:
            object.__setattr__(raw_result, "raw_anomaly_measure", 1.0)
            return CalibratedTrustConfidence(value=0.9)

    with pytest.raises(RawInspectionMutationError):
        TrustQualificationEngine(calibrator=MutatingCalibrator()).qualify(
            make_raw_result()
        )


def test_detectable_non_reproducibility_is_refused():
    class NonReproducibleCalibrator:
        def __init__(self) -> None:
            self.count = 0

        def calibrate(
            self, raw_result: RawInspectionResult
        ) -> CalibratedTrustConfidence:
            self.count += 1
            return CalibratedTrustConfidence(value=0.8 + (self.count / 100.0))

    with pytest.raises(NonReproducibleTrustQualification):
        TrustQualificationEngine(calibrator=NonReproducibleCalibrator()).qualify(
            make_raw_result()
        )


def test_calibrated_confidence_is_bounded_as_confidence():
    CalibratedConfidence(value=0.0, method_id="method")
    CalibratedConfidence(value=1.0, method_id="method")

    with pytest.raises(InvalidTrustQualificationResult):
        CalibratedConfidence(value=-0.01, method_id="method")
    with pytest.raises(InvalidTrustQualificationResult):
        CalibratedConfidence(value=1.01, method_id="method")


def test_raw_anomaly_score_remains_distinct_from_calibrated_confidence():
    inspection_result = make_inspection_result()
    qualified = TrustQualificationEngine(
        method=RecordingTrustQualificationMethod()
    ).qualify(inspection_result)

    assert inspection_result.raw_anomaly_score.value == 42.0
    assert qualified.calibrated_confidence.value == 0.8
    assert inspection_result.raw_anomaly_score is not qualified.calibrated_confidence


def test_qualification_outcomes_are_explicit():
    assert {outcome.value for outcome in QualificationOutcome} == {
        "accept",
        "review",
        "reject",
    }


def test_abstention_is_valid_review_qualification_outcome():
    inspection_result = make_inspection_result()

    qualified = TrustQualificationEngine(
        method=RecordingTrustQualificationMethod(
            outcome=QualificationOutcome.REVIEW,
            abstention_status=AbstentionStatus.ABSTAINED,
        )
    ).qualify(inspection_result)

    assert qualified.qualification_outcome is QualificationOutcome.REVIEW
    assert qualified.abstention_status is AbstentionStatus.ABSTAINED


def test_abstention_cannot_be_hidden_inside_accept_or_reject():
    inspection_result = make_inspection_result()

    with pytest.raises(InvalidTrustQualificationResult):
        TrustQualificationEngine(
            method=RecordingTrustQualificationMethod(
                outcome=QualificationOutcome.ACCEPT,
                abstention_status=AbstentionStatus.ABSTAINED,
            )
        ).qualify(inspection_result)


def test_drift_status_is_represented_without_inventing_an_algorithm():
    inspection_result = make_inspection_result()

    qualified = TrustQualificationEngine(
        method=RecordingTrustQualificationMethod(
            outcome=QualificationOutcome.REVIEW,
            drift_status=DriftAssessmentStatus.DRIFTED,
        )
    ).qualify(inspection_result)

    assert qualified.drift_assessment.status is DriftAssessmentStatus.DRIFTED
    assert qualified.drift_assessment.score is None


def test_engine_rejects_mismatched_qualification_result():
    inspection_result = make_inspection_result()
    other_result = replace(
        inspection_result,
        raw_anomaly_score=RawAnomalyScore(value=1.0, scale="other-scale"),
    )

    class MismatchedTrustQualificationMethod(RecordingTrustQualificationMethod):
        def qualify(self, inspection_result: InspectionResult) -> TrustQualifiedResult:
            return TrustQualifiedResult(
                inspection_result=other_result,
                calibrated_confidence=CalibratedConfidence(
                    value=0.5,
                    method_id=self.method_id,
                    method_version=self.method_version,
                ),
                qualification_outcome=QualificationOutcome.REVIEW,
                abstention_status=AbstentionStatus.NOT_ABSTAINED,
                drift_assessment=DriftAssessment(
                    status=DriftAssessmentStatus.NOT_ASSESSED,
                    method_id=self.method_id,
                    method_version=self.method_version,
                ),
                method_id=self.method_id,
                method_version=self.method_version,
            )

    with pytest.raises(InvalidTrustQualificationResult):
        TrustQualificationEngine(method=MismatchedTrustQualificationMethod()).qualify(
            inspection_result
        )


def test_engine_rejects_malformed_qualification_return():
    class MalformedTrustQualificationMethod:
        method_id = "malformed"
        method_version = "1"

        def qualify(self, inspection_result: InspectionResult) -> object:
            return object()

    with pytest.raises(InvalidTrustQualificationResult):
        TrustQualificationEngine(method=MalformedTrustQualificationMethod()).qualify(
            make_inspection_result()
        )
