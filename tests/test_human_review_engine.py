from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
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
from src.review import (
    HUMAN_REVIEW_EVIDENCE_KIND,
    HumanReviewDecision,
    HumanReviewEngine,
    HumanReviewEngineOutput,
    IncompleteReviewChain,
    HumanReviewRequest,
    HumanReviewResult,
    InvalidHumanReviewRequest,
    InvalidHumanReviewResult,
    MalformedReviewerDecision,
    NonReviewQualifiedCase,
    ReviewEvidenceRecord,
    ReviewerDecision,
    ReviewerDecisionValue,
    ReviewerIdentity,
    ReviewStatus,
)
from src.trust import (
    AbstentionStatus,
    CalibratedConfidence,
    DriftAssessment,
    DriftAssessmentStatus,
    QualifiedOutcome,
    QualificationOutcome,
    TrustQualificationEngine,
    TrustQualificationResult,
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


def make_raw_result(
    raw_measure: float = 65.0,
    judgement: InspectionJudgement = InspectionJudgement.DEFECT,
    result_id: str = "raw-review-result-1",
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
        input_id="input-review-1",
        judgement=judgement,
        localization=localization,
        raw_anomaly_measure=raw_measure,
        examination_id="examination-review-1",
    )


def make_trust_qualification_result(
    raw_result: RawInspectionResult,
) -> TrustQualificationResult:
    output = TrustQualificationEngine().qualify(raw_result)
    return output.trust_qualification_result


def make_review_case():
    raw_result = make_raw_result()
    trust_result = make_trust_qualification_result(raw_result)
    review_case = HumanReviewEngine().create_case(
        raw_inspection_result=raw_result,
        trust_qualification_result=trust_result,
        review_case_id="review-case-1",
    )
    return review_case


def make_reviewer_decision(review_case_id: str = "review-case-1") -> ReviewerDecision:
    return ReviewerDecision(
        decision_id="decision-1",
        review_case_id=review_case_id,
        reviewer_ref="reviewer-1",
        decision=ReviewerDecisionValue.INCONCLUSIVE,
        rationale="Insufficient visual certainty in the review handoff.",
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


def test_review_qualified_case_is_accepted():
    review_case = make_review_case()

    handoff = HumanReviewEngine().prepare_handoff(review_case)

    assert handoff.review_case_id == review_case.review_case_id
    assert review_case.trust_qualification_result.qualified_outcome is (
        QualifiedOutcome.REVIEW
    )


def test_non_review_non_drifted_case_is_refused():
    raw_result = make_raw_result(
        raw_measure=5.0,
        judgement=InspectionJudgement.OK,
        result_id="raw-accept-result",
    )
    trust_result = make_trust_qualification_result(raw_result)

    with pytest.raises(NonReviewQualifiedCase):
        HumanReviewEngine().create_case(
            raw_inspection_result=raw_result,
            trust_qualification_result=trust_result,
            review_case_id="review-case-accept",
        )


def test_handoff_contains_complete_upstream_context():
    review_case = make_review_case()

    handoff = HumanReviewEngine().prepare_handoff(review_case)

    assert handoff.source_input_ref == review_case.input_id
    assert handoff.localization_ref == review_case.localization_ref
    assert handoff.raw_inspection_result == review_case.raw_inspection_result
    assert handoff.trust_qualification_result == (
        review_case.trust_qualification_result
    )
    assert handoff.deferral_reason == review_case.deferral_reason


def test_deferral_reason_is_preserved_unchanged():
    review_case = make_review_case()

    output = HumanReviewEngine().record_decision(
        review_case,
        make_reviewer_decision(review_case.review_case_id),
    )

    assert output.review_handoff.deferral_reason == review_case.deferral_reason
    assert (
        output.review_evidence_record.review_handoff.deferral_reason
        == review_case.deferral_reason
    )


def test_reviewer_decision_is_recorded_for_exactly_one_case():
    review_case = make_review_case()
    decision = make_reviewer_decision(review_case.review_case_id)

    output = HumanReviewEngine().record_decision(review_case, decision)

    assert output.review_evidence_record.reviewer_decision == decision
    assert output.review_evidence_record.review_case_id == review_case.review_case_id

    with pytest.raises(InvalidHumanReviewResult):
        HumanReviewEngine().record_decision(
            review_case,
            make_reviewer_decision("other-review-case"),
        )


def test_raw_inspection_result_is_not_mutated():
    review_case = make_review_case()
    raw_before = deepcopy(review_case.raw_inspection_result)

    HumanReviewEngine().record_decision(
        review_case,
        make_reviewer_decision(review_case.review_case_id),
    )

    assert review_case.raw_inspection_result == raw_before


def test_trust_qualification_result_is_not_mutated():
    review_case = make_review_case()
    trust_before = deepcopy(review_case.trust_qualification_result)

    HumanReviewEngine().record_decision(
        review_case,
        make_reviewer_decision(review_case.review_case_id),
    )

    assert review_case.trust_qualification_result == trust_before


def test_review_evidence_record_preserves_full_upstream_chain():
    review_case = make_review_case()

    output = HumanReviewEngine().record_decision(
        review_case,
        make_reviewer_decision(review_case.review_case_id),
    )
    record = output.review_evidence_record

    assert isinstance(record, ReviewEvidenceRecord)
    assert record.evidence_kind == HUMAN_REVIEW_EVIDENCE_KIND
    assert record.upstream_chain.input_id == review_case.input_id
    assert record.upstream_chain.inspection_result_id == (
        review_case.inspection_result_id
    )
    assert record.upstream_chain.qualification_result_id == (
        review_case.qualification_result_id
    )
    assert record.upstream_chain.review_case_id == review_case.review_case_id


def test_reviewer_decision_is_evidence_only_not_feedback():
    output = HumanReviewEngine().record_decision(
        make_review_case(),
        make_reviewer_decision(),
    )

    assert isinstance(output, HumanReviewEngineOutput)
    assert output.review_evidence_record.reviewer_decision.decision is (
        ReviewerDecisionValue.INCONCLUSIVE
    )
    assert not hasattr(HumanReviewEngine(), "feedback")
    assert not hasattr(HumanReviewEngine(), "update_model")
    assert not hasattr(HumanReviewEngine(), "train")
    assert not hasattr(HumanReviewEngine(), "recalibrate")


def test_no_model_update_training_recalibration_or_feedback_behaviour_exists():
    engine = HumanReviewEngine()

    assert not hasattr(engine, "update_model")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "retrain")
    assert not hasattr(engine, "recalibrate")
    assert not hasattr(engine, "feedback_loop")


def test_no_image_inspection_or_reconstruction_exists():
    engine = HumanReviewEngine()

    assert not hasattr(engine, "inspect")
    assert not hasattr(engine, "inspect_path")
    assert not hasattr(engine, "reconstruct_inspection")


def test_no_evidence_engine_storage_or_presentation_is_implemented():
    engine = HumanReviewEngine()

    assert not hasattr(engine, "store")
    assert not hasattr(engine, "collect")
    assert not hasattr(engine, "present_evidence")
    assert not hasattr(engine, "evidence_view")


def test_no_evaluation_logic_is_implemented():
    engine = HumanReviewEngine()

    assert not hasattr(engine, "evaluate")
    assert not hasattr(engine, "measure_review_quality")


def test_same_fixed_case_and_decision_produce_identical_review_record():
    engine = HumanReviewEngine()
    review_case = make_review_case()
    decision = make_reviewer_decision(review_case.review_case_id)

    first = engine.record_decision(review_case, decision)
    second = engine.record_decision(review_case, decision)

    assert first.review_evidence_record == second.review_evidence_record


def test_missing_or_malformed_reviewer_decision_is_explicit():
    with pytest.raises(MalformedReviewerDecision):
        ReviewerDecision(
            decision_id="decision-bad",
            review_case_id="review-case-1",
            reviewer_ref="reviewer-1",
            decision=ReviewerDecisionValue.ACCEPT,
            rationale="",
        )


def test_incomplete_upstream_chain_is_refused():
    raw_result = make_raw_result()
    other_raw = make_raw_result(result_id="other-raw-result")
    trust_result = make_trust_qualification_result(other_raw)

    with pytest.raises(IncompleteReviewChain):
        HumanReviewEngine().create_case(
            raw_inspection_result=raw_result,
            trust_qualification_result=trust_result,
            review_case_id="review-case-bad-chain",
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
