from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from src.evidence import (
    PERFORMANCE_EVIDENCE_KIND,
    EvidenceAbsenceMarker,
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceChainLink,
    EvidenceDomain,
    EvidenceEngine,
    EvidenceRecordLink,
    EvidenceReference,
    EvidenceResult,
    EvidenceSourceDomain,
    EvidenceStatus,
    EvidenceView,
    FabricatedEvidenceRecord,
    InboundEvidenceRecord,
    InvalidEvidenceBundle,
    InvalidEvidenceResult,
    MalformedInboundEvidenceRecord,
    PreservedEvidenceRecord,
    PrototypePerformanceEvidenceRejected,
)
from src.inspection import (
    DefectJudgment,
    DefectLocalization,
    InspectionEvidenceRecord,
    InspectionJudgement,
    InspectionInput,
    InspectionResult,
    NormalizedBoundingBox,
    RawAnomalyScore,
    RawInspectionResult,
)
from src.review import (
    HumanReviewDecision,
    HumanReviewEngine,
    HumanReviewRequest,
    HumanReviewResult,
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
    TrustQualificationEngine,
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


def make_raw_inspection_result(
    raw_measure: float = 65.0,
    judgement: InspectionJudgement = InspectionJudgement.DEFECT,
    result_id: str = "raw-evidence-result-1",
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
        input_id="input-evidence-1",
        judgement=judgement,
        localization=localization,
        raw_anomaly_measure=raw_measure,
        examination_id="examination-evidence-1",
    )


def make_upstream_evidence_records():
    raw_result = make_raw_inspection_result()
    inspection_record = InspectionEvidenceRecord(
        record_id="inspection-evidence-record-1",
        input_id=raw_result.input_id,
        inspection_result_id=raw_result.inspection_result_id,
        raw_inspection_result=raw_result,
    )
    trust_output = TrustQualificationEngine().qualify(raw_result)
    review_case = HumanReviewEngine().create_case(
        raw_inspection_result=raw_result,
        trust_qualification_result=trust_output.trust_qualification_result,
        review_case_id="review-evidence-case-1",
    )
    review_output = HumanReviewEngine().record_decision(
        review_case,
        ReviewerDecision(
            decision_id="reviewer-decision-evidence-1",
            review_case_id=review_case.review_case_id,
            reviewer_ref="reviewer-1",
            decision=ReviewerDecisionValue.INCONCLUSIVE,
            rationale="Fixed substrate review decision for evidence tests.",
        ),
    )
    return (
        inspection_record,
        trust_output.trust_qualification_evidence_record,
        review_output.review_evidence_record,
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


def test_inspection_evidence_record_can_be_preserved():
    inspection_record, _, _ = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((inspection_record,))

    assert isinstance(view, EvidenceView)
    assert len(view.records) == 1
    assert view.records[0].source_domain is EvidenceSourceDomain.INSPECTION
    assert view.records[0].inbound_record_id == inspection_record.record_id


def test_trust_qualification_evidence_record_can_be_preserved():
    _, trust_record, _ = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((trust_record,))

    assert len(view.records) == 1
    assert view.records[0].source_domain is EvidenceSourceDomain.TRUST
    assert view.records[0].inbound_record_id == trust_record.record_id


def test_human_review_evidence_record_can_be_preserved():
    _, _, review_record = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((review_record,))

    assert len(view.records) == 1
    assert view.records[0].source_domain is EvidenceSourceDomain.HUMAN_REVIEW
    assert view.records[0].inbound_record_id == review_record.record_id


def test_preserved_records_are_immutable_and_read_only():
    inspection_record, _, _ = make_upstream_evidence_records()
    preserved_record = EvidenceEngine().preserve((inspection_record,)).records[0]

    assert isinstance(preserved_record, PreservedEvidenceRecord)
    with pytest.raises(FrozenInstanceError):
        preserved_record.content_hash = "changed"
    with pytest.raises(TypeError):
        preserved_record.payload["record_id"] = "changed"


def test_upstream_records_are_not_mutated_by_preservation():
    records = make_upstream_evidence_records()
    before = deepcopy(records)

    EvidenceEngine().preserve(records)

    assert records == before


def test_raw_inspection_and_trust_qualification_records_remain_separate():
    inspection_record, trust_record, _ = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((inspection_record, trust_record))

    assert len(view.records) == 2
    assert {record.source_domain for record in view.records} == {
        EvidenceSourceDomain.INSPECTION,
        EvidenceSourceDomain.TRUST,
    }
    assert view.records[0].preserved_record_id != view.records[1].preserved_record_id
    assert view.records[0].content_hash != view.records[1].content_hash


def test_full_chain_links_are_preserved_where_present():
    view = EvidenceEngine().preserve(make_upstream_evidence_records())

    assert all(isinstance(link, EvidenceChainLink) for link in view.links)
    assert all(link.immutable is True for link in view.links)
    assert {link.relation for link in view.links} >= {
        "source_input_to_raw_inspection",
        "raw_inspection_result_to_trust_qualification",
        "trust_qualification_to_human_review",
        "review_case_to_reviewer_decision",
        "inspection_evidence_to_trust_evidence",
        "trust_evidence_to_human_review_evidence",
    }


def test_missing_review_evidence_is_recorded_as_explicit_absence():
    inspection_record, trust_record, _ = make_upstream_evidence_records()

    view = EvidenceEngine().preserve(
        (inspection_record, trust_record),
        expected_stages=(EvidenceSourceDomain.HUMAN_REVIEW,),
    )

    assert len(view.absences) == 1
    assert isinstance(view.absences[0], EvidenceAbsenceMarker)
    assert view.absences[0].expected_stage == "human_review"
    assert view.absences[0].reason == "human_review_evidence_absent"
    assert EvidenceSourceDomain.HUMAN_REVIEW not in {
        record.source_domain for record in view.records
    }


def test_evidence_views_are_read_only():
    inspection_record, _, _ = make_upstream_evidence_records()
    view = EvidenceEngine().preserve((inspection_record,))

    assert view.read_only is True
    with pytest.raises(FrozenInstanceError):
        view.records = ()


def test_prototype_visuals_cannot_be_accepted_as_performance_evidence():
    with pytest.raises(PrototypePerformanceEvidenceRejected):
        InboundEvidenceRecord(
            record_id="prototype-performance-claim",
            evidence_kind=PERFORMANCE_EVIDENCE_KIND,
            source_domain=EvidenceSourceDomain.INSPECTION,
            payload={
                "artifact_kind": "synthetic_overlay",
                "claim": "performance evidence",
            },
            links=(
                EvidenceRecordLink(
                    from_record_id="prototype-input",
                    to_record_id="prototype-overlay",
                    relation="prototype_visual_claim",
                ),
            ),
        )


def test_reviewer_decisions_remain_evidence_only_not_feedback():
    _, _, review_record = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((review_record,))

    assert view.records[0].payload["reviewer_decision"]["decision"] == (
        "inconclusive"
    )
    assert not hasattr(EvidenceEngine(), "feedback")
    assert not hasattr(EvidenceEngine(), "update_model")
    assert not hasattr(EvidenceEngine(), "train")
    assert not hasattr(EvidenceEngine(), "recalibrate")


def test_no_model_update_training_recalibration_or_feedback_behaviour_exists():
    engine = EvidenceEngine()

    assert not hasattr(engine, "update_model")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "retrain")
    assert not hasattr(engine, "recalibrate")
    assert not hasattr(engine, "feedback_loop")


def test_no_cross_domain_or_evaluation_behaviour_exists():
    engine = EvidenceEngine()

    assert not hasattr(engine, "inspect")
    assert not hasattr(engine, "calibrate")
    assert not hasattr(engine, "qualify")
    assert not hasattr(engine, "route_for_review")
    assert not hasattr(engine, "review")
    assert not hasattr(engine, "evaluate")
    assert not hasattr(engine, "measure_performance")


def test_replay_over_same_fixed_records_is_identical():
    records = make_upstream_evidence_records()
    engine = EvidenceEngine()

    first = engine.preserve(records)
    second = engine.preserve(records)

    assert first == second


def test_malformed_inbound_records_are_refused():
    with pytest.raises(MalformedInboundEvidenceRecord):
        EvidenceEngine().preserve((object(),))  # type: ignore[arg-type]


def test_fabricated_records_are_refused_explicitly():
    with pytest.raises(FabricatedEvidenceRecord):
        InboundEvidenceRecord(
            record_id="fabricated-record",
            evidence_kind="inspection_raw_result",
            source_domain="outside-domain",  # type: ignore[arg-type]
            payload={"fabricated": True},
        )


def test_unauthorized_upstream_rerun_behaviour_does_not_exist():
    engine = EvidenceEngine()

    assert not hasattr(engine, "rerun_inspection")
    assert not hasattr(engine, "rerun_trust_qualification")
    assert not hasattr(engine, "run_upstream")
    assert not hasattr(engine, "reinspect")
