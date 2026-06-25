from __future__ import annotations

from dataclasses import FrozenInstanceError
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
from src.review import (
    HumanReviewDecision,
    HumanReviewEngine,
    HumanReviewRequest,
    HumanReviewResult,
    InvalidHumanReviewRequest,
    InvalidHumanReviewResult,
    ReviewerIdentity,
    ReviewStatus,
)
from src.trust import (
    AbstentionStatus,
    CalibratedConfidence,
    DriftAssessment,
    DriftAssessmentStatus,
    QualificationOutcome,
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


def make_trust_qualified_result(
    outcome: QualificationOutcome = QualificationOutcome.REVIEW,
) -> TrustQualifiedResult:
    return TrustQualifiedResult(
        inspection_result=make_inspection_result(),
        calibrated_confidence=CalibratedConfidence(
            value=0.4,
            method_id="trust-method",
            method_version="1",
        ),
        qualification_outcome=outcome,
        abstention_status=(
            AbstentionStatus.ABSTAINED
            if outcome is QualificationOutcome.REVIEW
            else AbstentionStatus.NOT_ABSTAINED
        ),
        drift_assessment=DriftAssessment(
            status=DriftAssessmentStatus.NOT_ASSESSED,
            method_id="trust-method",
            method_version="1",
        ),
        method_id="trust-method",
        method_version="1",
    )


class RecordingHumanReviewMethod:
    method_id = "recording-review-method"
    method_version = "1"

    def __init__(self) -> None:
        self.seen_request: HumanReviewRequest | None = None

    def review(self, review_request: HumanReviewRequest) -> HumanReviewResult:
        self.seen_request = review_request
        return HumanReviewResult(
            trust_qualified_result=review_request.trust_qualified_result,
            review_request=review_request,
            status=ReviewStatus.COMPLETED,
            reviewer_identity=ReviewerIdentity(reviewer_id="reviewer-1"),
            decision=HumanReviewDecision.INCONCLUSIVE,
            method_id=self.method_id,
            method_version=self.method_version,
        )


def test_only_review_qualified_cases_may_enter_human_review():
    engine = HumanReviewEngine(method=RecordingHumanReviewMethod())

    with pytest.raises(InvalidHumanReviewRequest):
        engine.create_request(
            trust_qualified_result=make_trust_qualified_result(
                QualificationOutcome.ACCEPT
            ),
            request_id="review-1",
        )


def test_trust_qualified_result_remains_immutable():
    trust_result = make_trust_qualified_result()

    with pytest.raises(FrozenInstanceError):
        trust_result.qualification_outcome = QualificationOutcome.ACCEPT


def test_human_review_result_references_original_trust_result():
    trust_result = make_trust_qualified_result()
    method = RecordingHumanReviewMethod()

    result = HumanReviewEngine(method=method).review(
        trust_qualified_result=trust_result,
        request_id="review-1",
    )

    assert method.seen_request is not None
    assert method.seen_request.trust_qualified_result is trust_result
    assert result.trust_qualified_result is trust_result
    assert result.review_request.trust_qualified_result is trust_result
    assert result.review_request.status is ReviewStatus.REQUESTED


def test_review_status_transitions_are_valid():
    trust_result = make_trust_qualified_result()
    request = HumanReviewRequest(
        trust_qualified_result=trust_result,
        request_id="review-1",
        status=ReviewStatus.IN_REVIEW,
    )

    completed = HumanReviewResult(
        trust_qualified_result=trust_result,
        review_request=request,
        status=ReviewStatus.COMPLETED,
        reviewer_identity=ReviewerIdentity(reviewer_id="reviewer-1"),
        decision=HumanReviewDecision.REJECT,
        method_id="review-method",
    )

    assert completed.status is ReviewStatus.COMPLETED


def test_completed_review_requires_reviewer_and_decision():
    trust_result = make_trust_qualified_result()
    request = HumanReviewRequest(
        trust_qualified_result=trust_result,
        request_id="review-1",
    )

    with pytest.raises(InvalidHumanReviewResult):
        HumanReviewResult(
            trust_qualified_result=trust_result,
            review_request=request,
            status=ReviewStatus.COMPLETED,
            method_id="review-method",
        )


def test_malformed_review_results_are_rejected():
    class MalformedHumanReviewMethod:
        method_id = "malformed-review-method"
        method_version = "1"

        def review(self, review_request: HumanReviewRequest) -> object:
            return object()

    with pytest.raises(InvalidHumanReviewResult):
        HumanReviewEngine(method=MalformedHumanReviewMethod()).review(
            trust_qualified_result=make_trust_qualified_result(),
            request_id="review-1",
        )


def test_delegated_review_protocol_is_respected():
    trust_result = make_trust_qualified_result()
    method = RecordingHumanReviewMethod()

    result = HumanReviewEngine(method=method).review(
        trust_qualified_result=trust_result,
        request_id="review-1",
    )

    assert method.seen_request is result.review_request
    assert result.method_id == method.method_id
    assert result.method_version == method.method_version


def test_result_for_different_request_is_rejected():
    trust_result = make_trust_qualified_result()
    other_request = HumanReviewRequest(
        trust_qualified_result=trust_result,
        request_id="review-2",
    )

    class MismatchedHumanReviewMethod(RecordingHumanReviewMethod):
        def review(self, review_request: HumanReviewRequest) -> HumanReviewResult:
            return HumanReviewResult(
                trust_qualified_result=trust_result,
                review_request=other_request,
                status=ReviewStatus.COMPLETED,
                reviewer_identity=ReviewerIdentity(reviewer_id="reviewer-1"),
                decision=HumanReviewDecision.ACCEPT,
                method_id=self.method_id,
                method_version=self.method_version,
            )

    with pytest.raises(InvalidHumanReviewResult):
        HumanReviewEngine(method=MismatchedHumanReviewMethod()).review(
            trust_qualified_result=trust_result,
            request_id="review-1",
        )


def test_unable_to_review_results_do_not_contain_automatic_decisions():
    trust_result = make_trust_qualified_result()
    request = HumanReviewRequest(
        trust_qualified_result=trust_result,
        request_id="review-1",
    )

    result = HumanReviewResult(
        trust_qualified_result=trust_result,
        review_request=request,
        status=ReviewStatus.UNABLE_TO_REVIEW,
        method_id="review-method",
    )

    assert result.decision is None
    assert result.reviewer_identity is None
