from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from src.evidence import (
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceDomain,
    EvidenceEngine,
    EvidenceReference,
    EvidenceResult,
    EvidenceStatus,
    InvalidEvidenceBundle,
    InvalidEvidenceResult,
)
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
    HumanReviewRequest,
    HumanReviewResult,
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


def make_trust_result(
    inspection_result: InspectionResult,
    outcome: QualificationOutcome = QualificationOutcome.REVIEW,
) -> TrustQualifiedResult:
    return TrustQualifiedResult(
        inspection_result=inspection_result,
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


def make_review_result(
    trust_result: TrustQualifiedResult,
) -> HumanReviewResult:
    request = HumanReviewRequest(
        trust_qualified_result=trust_result,
        request_id="review-1",
    )
    return HumanReviewResult(
        trust_qualified_result=trust_result,
        review_request=request,
        status=ReviewStatus.COMPLETED,
        reviewer_identity=ReviewerIdentity(reviewer_id="reviewer-1"),
        decision=HumanReviewDecision.INCONCLUSIVE,
        method_id="review-method",
        method_version="1",
    )


def make_artifacts(
    inspection_result: InspectionResult,
    trust_result: TrustQualifiedResult,
    review_result: HumanReviewResult | None = None,
) -> tuple[EvidenceArtifact, ...]:
    artifacts = (
        EvidenceArtifact(
            artifact_id="inspection-artifact",
            reference=EvidenceReference(
                domain=EvidenceDomain.INSPECTION,
                reference_id=inspection_result.inspection_input.input_id,
            ),
            status=EvidenceStatus.PRESENT,
        ),
        EvidenceArtifact(
            artifact_id="trust-artifact",
            reference=EvidenceReference(
                domain=EvidenceDomain.TRUST,
                reference_id=(
                    f"{trust_result.method_id}:"
                    f"{trust_result.inspection_result.inspection_input.input_id}"
                ),
            ),
            status=EvidenceStatus.PRESENT,
        ),
    )
    if review_result is not None:
        artifacts = (
            *artifacts,
            EvidenceArtifact(
            artifact_id="review-artifact",
            reference=EvidenceReference(
                domain=EvidenceDomain.HUMAN_REVIEW,
                reference_id=(
                    f"{review_result.method_id}:"
                    f"{review_result.review_request.request_id}"
                ),
            ),
            status=EvidenceStatus.PRESENT,
            ),
        )
    return artifacts


def make_bundle(
    outcome: QualificationOutcome = QualificationOutcome.REVIEW,
    include_review: bool = True,
) -> EvidenceBundle:
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(inspection_result, outcome)
    review_result = make_review_result(trust_result) if include_review else None
    return EvidenceBundle(
        inspection_result=inspection_result,
        trust_qualified_result=trust_result,
        artifacts=make_artifacts(inspection_result, trust_result, review_result),
        bundle_id="bundle-1",
        human_review_result=review_result,
    )


class RecordingEvidenceMethod:
    method_id = "recording-evidence-method"
    method_version = "1"

    def __init__(self) -> None:
        self.seen_bundle: EvidenceBundle | None = None

    def collect(self, evidence_bundle: EvidenceBundle) -> EvidenceResult:
        self.seen_bundle = evidence_bundle
        return EvidenceResult(
            inspection_result=evidence_bundle.inspection_result,
            trust_qualified_result=evidence_bundle.trust_qualified_result,
            evidence_bundle=evidence_bundle,
            method_id=self.method_id,
            human_review_result=evidence_bundle.human_review_result,
            method_version=self.method_version,
        )


def test_evidence_can_be_collected_for_accept_without_human_review_result():
    bundle = make_bundle(
        outcome=QualificationOutcome.ACCEPT,
        include_review=False,
    )

    result = EvidenceEngine(method=RecordingEvidenceMethod()).collect(bundle)

    assert result.inspection_result is bundle.inspection_result
    assert result.trust_qualified_result is bundle.trust_qualified_result
    assert result.human_review_result is None
    assert EvidenceDomain.HUMAN_REVIEW not in bundle.reference_ids


def test_evidence_can_be_collected_for_reject_without_human_review_result():
    bundle = make_bundle(
        outcome=QualificationOutcome.REJECT,
        include_review=False,
    )

    result = EvidenceEngine(method=RecordingEvidenceMethod()).collect(bundle)

    assert result.inspection_result is bundle.inspection_result
    assert result.trust_qualified_result is bundle.trust_qualified_result
    assert result.human_review_result is None
    assert EvidenceDomain.HUMAN_REVIEW not in bundle.reference_ids


def test_evidence_can_be_collected_for_review_with_human_review_result():
    bundle = make_bundle()
    method = RecordingEvidenceMethod()

    result = EvidenceEngine(method=method).collect(bundle)

    assert method.seen_bundle is bundle
    assert result.inspection_result is bundle.inspection_result
    assert result.trust_qualified_result is bundle.trust_qualified_result
    assert result.human_review_result is bundle.human_review_result


def test_evidence_artifacts_remain_immutable():
    artifact = make_bundle().artifacts[0]

    with pytest.raises(FrozenInstanceError):
        artifact.status = EvidenceStatus.MISSING


def test_bundle_rejects_mismatched_domain_chain():
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(inspection_result)
    other_trust = make_trust_result(make_inspection_result())
    review_result = make_review_result(other_trust)

    with pytest.raises(InvalidEvidenceBundle):
        EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_result,
            artifacts=make_artifacts(inspection_result, trust_result, review_result),
            bundle_id="bundle-1",
            human_review_result=review_result,
        )


def test_bundle_rejects_artifacts_for_unknown_references():
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(inspection_result)
    review_result = make_review_result(trust_result)
    artifacts = (
        EvidenceArtifact(
            artifact_id="inspection-artifact",
            reference=EvidenceReference(
                domain=EvidenceDomain.INSPECTION,
                reference_id="unknown-input",
            ),
            status=EvidenceStatus.PRESENT,
        ),
        *make_artifacts(inspection_result, trust_result, review_result)[1:],
    )

    with pytest.raises(InvalidEvidenceBundle):
        EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_result,
            artifacts=artifacts,
            bundle_id="bundle-1",
            human_review_result=review_result,
        )


def test_human_review_artifact_is_required_when_human_review_result_is_present():
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(inspection_result)
    review_result = make_review_result(trust_result)
    artifacts = make_artifacts(inspection_result, trust_result, None)

    with pytest.raises(InvalidEvidenceBundle):
        EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_result,
            artifacts=artifacts,
            bundle_id="bundle-1",
            human_review_result=review_result,
        )


def test_human_review_artifact_is_rejected_when_human_review_result_is_absent():
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(
        inspection_result,
        QualificationOutcome.ACCEPT,
    )
    review_trust_result = make_trust_result(inspection_result)
    review_result = make_review_result(review_trust_result)
    artifacts = make_artifacts(inspection_result, trust_result, review_result)

    with pytest.raises(InvalidEvidenceBundle):
        EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_result,
            artifacts=artifacts,
            bundle_id="bundle-1",
        )


def test_malformed_evidence_results_are_rejected():
    class MalformedEvidenceMethod:
        method_id = "malformed-evidence-method"
        method_version = "1"

        def collect(self, evidence_bundle: EvidenceBundle) -> object:
            return object()

    with pytest.raises(InvalidEvidenceResult):
        EvidenceEngine(method=MalformedEvidenceMethod()).collect(make_bundle())


def test_delegated_evidence_protocol_is_respected():
    bundle = make_bundle()
    method = RecordingEvidenceMethod()

    result = EvidenceEngine(method=method).collect(bundle)

    assert method.seen_bundle is bundle
    assert result.method_id == method.method_id
    assert result.method_version == method.method_version


def test_result_for_different_bundle_is_rejected():
    bundle = make_bundle()
    other_bundle = replace(bundle, bundle_id="bundle-2")

    class MismatchedEvidenceMethod(RecordingEvidenceMethod):
        def collect(self, evidence_bundle: EvidenceBundle) -> EvidenceResult:
            return EvidenceResult(
                inspection_result=other_bundle.inspection_result,
                trust_qualified_result=other_bundle.trust_qualified_result,
                evidence_bundle=other_bundle,
                method_id=self.method_id,
                human_review_result=other_bundle.human_review_result,
                method_version=self.method_version,
            )

    with pytest.raises(InvalidEvidenceResult):
        EvidenceEngine(method=MismatchedEvidenceMethod()).collect(bundle)


def test_missing_evidence_is_represented_as_missing_artifacts():
    inspection_result = make_inspection_result()
    trust_result = make_trust_result(inspection_result)
    review_result = make_review_result(trust_result)
    artifacts = (
        EvidenceArtifact(
            artifact_id="inspection-artifact",
            reference=EvidenceReference(
                domain=EvidenceDomain.INSPECTION,
                reference_id=inspection_result.inspection_input.input_id,
            ),
            status=EvidenceStatus.MISSING,
        ),
        *make_artifacts(inspection_result, trust_result, review_result)[1:],
    )

    bundle = EvidenceBundle(
        inspection_result=inspection_result,
        trust_qualified_result=trust_result,
        artifacts=artifacts,
        bundle_id="bundle-1",
        human_review_result=review_result,
    )

    assert bundle.artifacts[0].status is EvidenceStatus.MISSING
