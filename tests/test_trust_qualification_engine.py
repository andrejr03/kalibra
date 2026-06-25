from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from src.inspection import (
    DefectJudgment,
    DefectLocalization,
    InspectionInput,
    InspectionResult,
    NormalizedBoundingBox,
    RawAnomalyScore,
)
from src.trust import (
    AbstentionStatus,
    CalibratedConfidence,
    DriftAssessment,
    DriftAssessmentStatus,
    InvalidTrustQualificationResult,
    QualificationOutcome,
    TrustQualificationEngine,
    TrustQualifiedResult,
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
