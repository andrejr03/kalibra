from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

from src.evidence import (
    PERFORMANCE_EVIDENCE_KIND,
    EvidenceAbsenceFailure,
    EvidenceAbsenceMarker,
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceChainLink,
    EvidenceDomain,
    EvidenceEngine,
    EvidenceLinkingFailure,
    EvidenceRecordLink,
    EvidenceReference,
    EvidenceResult,
    EvidenceSourceDomain,
    EvidenceStatus,
    EvidenceView,
    EvidenceViewFailure,
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


def make_inbound_inspection_evidence(
    record_id: str,
    input_id: str,
    inspection_result_id: str,
    relation: str = "source_input_to_raw_inspection",
    payload_extra: dict | None = None,
    links: tuple[EvidenceRecordLink, ...] | None = None,
) -> InboundEvidenceRecord:
    payload = {
        "input_id": input_id,
        "inspection_result_id": inspection_result_id,
    }
    if payload_extra:
        payload.update(payload_extra)
    return InboundEvidenceRecord(
        record_id=record_id,
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload=payload,
        links=links
        if links is not None
        else (
            EvidenceRecordLink(
                from_record_id=input_id,
                to_record_id=inspection_result_id,
                relation=relation,
            ),
        ),
    )


def make_inbound_trust_evidence(
    record_id: str,
    inspection_result_id: str,
    qualification_result_id: str,
) -> InboundEvidenceRecord:
    return InboundEvidenceRecord(
        record_id=record_id,
        evidence_kind="trust_qualification_result",
        source_domain=EvidenceSourceDomain.TRUST,
        payload={
            "inspection_result_id": inspection_result_id,
            "qualification_result_id": qualification_result_id,
        },
        links=(
            EvidenceRecordLink(
                from_record_id=inspection_result_id,
                to_record_id=qualification_result_id,
                relation="raw_inspection_result_to_trust_qualification",
            ),
        ),
    )


def make_inbound_review_evidence(
    record_id: str,
    qualification_result_id: str,
    review_case_id: str,
    decision_id: str,
) -> InboundEvidenceRecord:
    return InboundEvidenceRecord(
        record_id=record_id,
        evidence_kind="human_review_result",
        source_domain=EvidenceSourceDomain.HUMAN_REVIEW,
        payload={
            "review_case_id": review_case_id,
            "reviewer_decision": {
                "decision_id": decision_id,
                "decision": "inconclusive",
            },
            "upstream_chain": {
                "qualification_result_id": qualification_result_id,
                "review_case_id": review_case_id,
            },
        },
        links=(
            EvidenceRecordLink(
                from_record_id=qualification_result_id,
                to_record_id=review_case_id,
                relation="trust_qualification_to_human_review",
            ),
            EvidenceRecordLink(
                from_record_id=review_case_id,
                to_record_id=decision_id,
                relation="review_case_to_reviewer_decision",
            ),
        ),
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


def test_same_fixed_evidence_produces_identical_preserved_records_and_view():
    records = make_upstream_evidence_records()
    engine = EvidenceEngine()

    first = engine.preserve(records)
    second = engine.preserve(records)

    assert first == second
    assert first.records == second.records
    assert tuple(record.content_hash for record in first.records) == tuple(
        record.content_hash for record in second.records
    )
    assert tuple(record.preserved_record_id for record in first.records) == tuple(
        record.preserved_record_id for record in second.records
    )
    assert first.view_id == second.view_id


def test_equivalent_canonical_payloads_produce_identical_content_hashes():
    first_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-1",
            "input_id": "input-1",
            "measure": {
                "kind": "raw_anomaly_measure",
                "value": 42.0,
            },
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "measure": {
                "value": 42.0,
                "kind": "raw_anomaly_measure",
            },
            "input_id": "input-1",
            "inspection_result_id": "raw-1",
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    first_view = EvidenceEngine().preserve((first_record,))
    second_view = EvidenceEngine().preserve((second_record,))

    assert first_view.records[0].content_hash == (
        second_view.records[0].content_hash
    )
    assert first_view.records[0].preserved_record_id == (
        second_view.records[0].preserved_record_id
    )
    assert first_view.view_id == second_view.view_id


def test_content_hash_depends_only_on_canonical_payload_content():
    payload = {
        "inspection_result_id": "raw-1",
        "input_id": "input-1",
        "measure": {
            "kind": "raw_anomaly_measure",
            "value": 42.0,
        },
    }
    first_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload=payload,
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-2",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload=payload,
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    first_preserved = EvidenceEngine().preserve((first_record,)).records[0]
    second_preserved = EvidenceEngine().preserve((second_record,)).records[0]

    assert first_preserved.content_hash == second_preserved.content_hash
    assert first_preserved.preserved_record_id != (
        second_preserved.preserved_record_id
    )


def test_preserved_record_id_uses_inbound_id_source_domain_and_content_hash():
    payload = {
        "inspection_result_id": "raw-1",
        "input_id": "input-1",
    }
    first_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload=payload,
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="canonical-evidence-record-1",
        evidence_kind="trust_qualification_result",
        source_domain=EvidenceSourceDomain.TRUST,
        payload={
            "inspection_result_id": "raw-1",
            "qualification_result_id": "qualification-1",
        },
        links=(
            EvidenceRecordLink(
                from_record_id="raw-1",
                to_record_id="qualification-1",
                relation="raw_inspection_result_to_trust_qualification",
            ),
        ),
    )

    first_preserved = EvidenceEngine().preserve((first_record,)).records[0]
    second_preserved = EvidenceEngine().preserve((second_record,)).records[0]

    assert first_preserved.inbound_record_id == second_preserved.inbound_record_id
    assert first_preserved.source_domain is not second_preserved.source_domain
    assert first_preserved.preserved_record_id != (
        second_preserved.preserved_record_id
    )


def test_preserved_payload_sequences_are_immutable():
    record = InboundEvidenceRecord(
        record_id="sequence-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-1",
            "input_id": "input-1",
            "measurements": ["raw", "localized"],
            "nested": {
                "labels": ["alpha", "beta"],
            },
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    preserved = EvidenceEngine().preserve((record,)).records[0]

    assert preserved.payload["measurements"] == ("raw", "localized")
    assert preserved.payload["nested"]["labels"] == ("alpha", "beta")
    with pytest.raises(TypeError):
        preserved.payload["measurements"][0] = "changed"
    with pytest.raises(TypeError):
        preserved.payload["nested"]["labels"][0] = "changed"


def test_set_payloads_are_canonicalized_deterministically():
    first_record = InboundEvidenceRecord(
        record_id="set-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-1",
            "input_id": "input-1",
            "tags": {"gamma", "alpha", "beta"},
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="set-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-1",
            "input_id": "input-1",
            "tags": {"beta", "gamma", "alpha"},
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    first_preserved = EvidenceEngine().preserve((first_record,)).records[0]
    second_preserved = EvidenceEngine().preserve((second_record,)).records[0]

    assert first_preserved.payload["tags"] == ("alpha", "beta", "gamma")
    assert first_preserved.content_hash == second_preserved.content_hash


def test_path_payloads_are_canonicalized_deterministically():
    first_record = InboundEvidenceRecord(
        record_id="path-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-1",
            "input_id": "input-1",
            "artifact_path": Path("fixtures/part.pgm"),
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="path-evidence-record-1",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "artifact_path": Path("fixtures") / "part.pgm",
            "input_id": "input-1",
            "inspection_result_id": "raw-1",
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-1",
                to_record_id="raw-1",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    first_preserved = EvidenceEngine().preserve((first_record,)).records[0]
    second_preserved = EvidenceEngine().preserve((second_record,)).records[0]

    assert first_preserved.payload["artifact_path"] == "fixtures/part.pgm"
    assert first_preserved.content_hash == second_preserved.content_hash


def test_shuffled_inbound_evidence_produces_same_preserved_ordering():
    inspection_record, trust_record, review_record = make_upstream_evidence_records()
    expected_order = tuple(
        record.preserved_record_id
        for record in EvidenceEngine().preserve(
            (inspection_record, trust_record, review_record)
        ).records
    )

    shuffled_order = tuple(
        record.preserved_record_id
        for record in EvidenceEngine().preserve(
            (review_record, trust_record, inspection_record)
        ).records
    )

    assert shuffled_order == expected_order


def test_shuffled_inbound_records_produce_identical_evidence_view():
    inspection_record, trust_record, review_record = make_upstream_evidence_records()

    first = EvidenceEngine().preserve(
        (inspection_record, trust_record, review_record)
    )
    second = EvidenceEngine().preserve(
        (review_record, inspection_record, trust_record)
    )

    assert second == first


def test_preserved_record_ordering_follows_source_domain_then_inbound_id():
    inspection_b = make_inbound_inspection_evidence(
        record_id="inspection-record-b",
        input_id="input-b",
        inspection_result_id="raw-b",
    )
    inspection_a = make_inbound_inspection_evidence(
        record_id="inspection-record-a",
        input_id="input-a",
        inspection_result_id="raw-a",
    )
    trust_record = make_inbound_trust_evidence(
        record_id="trust-record-a",
        inspection_result_id="raw-a",
        qualification_result_id="qualification-a",
    )
    review_record = make_inbound_review_evidence(
        record_id="review-record-a",
        qualification_result_id="qualification-a",
        review_case_id="review-case-a",
        decision_id="decision-a",
    )

    view = EvidenceEngine().preserve(
        (review_record, inspection_b, trust_record, inspection_a)
    )

    assert tuple(
        (record.source_domain, record.inbound_record_id)
        for record in view.records
    ) == (
        (EvidenceSourceDomain.INSPECTION, "inspection-record-a"),
        (EvidenceSourceDomain.INSPECTION, "inspection-record-b"),
        (EvidenceSourceDomain.TRUST, "trust-record-a"),
        (EvidenceSourceDomain.HUMAN_REVIEW, "review-record-a"),
    )


def test_preserved_record_ordering_uses_preserved_id_as_final_tie_breaker():
    first = make_inbound_inspection_evidence(
        record_id="inspection-record-duplicate",
        input_id="input-a",
        inspection_result_id="raw-a",
        payload_extra={"measure": 1},
    )
    second = make_inbound_inspection_evidence(
        record_id="inspection-record-duplicate",
        input_id="input-b",
        inspection_result_id="raw-b",
        payload_extra={"measure": 2},
    )

    forward_view = EvidenceEngine().preserve((first, second))
    reversed_view = EvidenceEngine().preserve((second, first))
    forward_ids = tuple(
        record.preserved_record_id for record in forward_view.records
    )
    reversed_ids = tuple(
        record.preserved_record_id for record in reversed_view.records
    )

    assert forward_ids == reversed_ids
    assert forward_ids == tuple(sorted(forward_ids))


def test_chain_link_ordering_is_deterministic():
    records = make_upstream_evidence_records()
    first = EvidenceEngine().preserve(records)
    second = EvidenceEngine().preserve(tuple(reversed(records)))

    first_link_ids = tuple(link.link_id for link in first.links)
    second_link_ids = tuple(link.link_id for link in second.links)

    assert first_link_ids == second_link_ids
    assert first_link_ids == tuple(sorted(first_link_ids))


def test_chain_links_are_deterministic_and_deduplicated():
    duplicate_link = EvidenceRecordLink(
        from_record_id="input-duplicate",
        to_record_id="raw-duplicate",
        relation="source_input_to_raw_inspection",
    )
    record = make_inbound_inspection_evidence(
        record_id="inspection-record-duplicate-links",
        input_id="input-duplicate",
        inspection_result_id="raw-duplicate",
        links=(duplicate_link, duplicate_link),
    )

    first = EvidenceEngine().preserve((record,))
    second = EvidenceEngine().preserve((record,))
    link_identities = tuple(
        (link.from_record_id, link.to_record_id, link.relation)
        for link in first.links
    )

    assert first.links == second.links
    assert len(link_identities) == len(set(link_identities))
    assert tuple(link.link_id for link in first.links) == tuple(
        sorted(link.link_id for link in first.links)
    )


def test_chain_links_are_created_only_when_both_cross_record_endpoints_exist():
    inspection_record, trust_record, review_record = make_upstream_evidence_records()

    only_trust = EvidenceEngine().preserve((trust_record,))
    trust_and_review = EvidenceEngine().preserve((trust_record, review_record))
    inspection_and_trust = EvidenceEngine().preserve(
        (inspection_record, trust_record)
    )
    only_review = EvidenceEngine().preserve((review_record,))

    assert "inspection_evidence_to_trust_evidence" not in {
        link.relation for link in only_trust.links
    }
    assert "trust_evidence_to_human_review_evidence" not in {
        link.relation for link in only_review.links
    }
    assert "trust_evidence_to_human_review_evidence" in {
        link.relation for link in trust_and_review.links
    }
    assert "inspection_evidence_to_trust_evidence" not in {
        link.relation for link in trust_and_review.links
    }
    assert "inspection_evidence_to_trust_evidence" in {
        link.relation for link in inspection_and_trust.links
    }
    assert "trust_evidence_to_human_review_evidence" not in {
        link.relation for link in inspection_and_trust.links
    }


def test_missing_cross_record_links_are_not_fabricated():
    inspection_record, _, review_record = make_upstream_evidence_records()

    view = EvidenceEngine().preserve((inspection_record, review_record))

    assert "inspection_evidence_to_trust_evidence" not in {
        link.relation for link in view.links
    }
    assert "trust_evidence_to_human_review_evidence" not in {
        link.relation for link in view.links
    }


def test_absence_marker_ordering_is_deterministic():
    first = EvidenceEngine().preserve(
        (),
        expected_stages=(
            EvidenceSourceDomain.HUMAN_REVIEW,
            EvidenceSourceDomain.TRUST,
        ),
    )
    second = EvidenceEngine().preserve(
        (),
        expected_stages=(
            EvidenceSourceDomain.TRUST,
            EvidenceSourceDomain.HUMAN_REVIEW,
        ),
    )

    first_absence_ids = tuple(absence.absence_id for absence in first.absences)
    second_absence_ids = tuple(absence.absence_id for absence in second.absences)

    assert first_absence_ids == second_absence_ids
    assert first_absence_ids == tuple(sorted(first_absence_ids))


def test_evidence_view_id_changes_when_record_link_or_absence_identity_changes():
    first_record = make_inbound_inspection_evidence(
        record_id="view-id-record-a",
        input_id="input-view-id",
        inspection_result_id="raw-view-id",
    )
    second_record = make_inbound_inspection_evidence(
        record_id="view-id-record-b",
        input_id="input-view-id",
        inspection_result_id="raw-view-id",
    )
    link_variant_record = make_inbound_inspection_evidence(
        record_id="view-id-record-a",
        input_id="input-view-id",
        inspection_result_id="raw-view-id",
        relation="source_input_to_raw_inspection_variant",
    )

    first_view = EvidenceEngine().preserve((first_record,))
    record_variant_view = EvidenceEngine().preserve((second_record,))
    link_variant_view = EvidenceEngine().preserve((link_variant_record,))
    absence_view = EvidenceEngine().preserve(
        (),
        expected_stages=(EvidenceSourceDomain.TRUST,),
    )

    assert record_variant_view.view_id != first_view.view_id
    assert link_variant_view.view_id != first_view.view_id
    assert absence_view.view_id != first_view.view_id


def test_evidence_view_id_remains_stable_when_semantic_input_is_unchanged():
    first_record = InboundEvidenceRecord(
        record_id="stable-view-record",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "inspection_result_id": "raw-stable",
            "input_id": "input-stable",
            "measure": {
                "kind": "raw_anomaly_measure",
                "value": 42.0,
            },
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-stable",
                to_record_id="raw-stable",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )
    second_record = InboundEvidenceRecord(
        record_id="stable-view-record",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "measure": {
                "value": 42.0,
                "kind": "raw_anomaly_measure",
            },
            "input_id": "input-stable",
            "inspection_result_id": "raw-stable",
        },
        links=(
            EvidenceRecordLink(
                from_record_id="input-stable",
                to_record_id="raw-stable",
                relation="source_input_to_raw_inspection",
            ),
        ),
    )

    first_view = EvidenceEngine().preserve((first_record,))
    second_view = EvidenceEngine().preserve((second_record,))

    assert second_view.view_id == first_view.view_id


def test_evidence_view_is_deterministic_and_read_only():
    records = make_upstream_evidence_records()
    first = EvidenceEngine().preserve(records)
    second = EvidenceEngine().preserve(records)

    assert first == second
    assert first.view_id == second.view_id
    assert first.read_only is True
    with pytest.raises(FrozenInstanceError):
        first.read_only = False
    with pytest.raises(FrozenInstanceError):
        first.absences = ()


def test_preserved_records_remain_immutable_after_preservation():
    preserved_record = EvidenceEngine().preserve(
        make_upstream_evidence_records()
    ).records[0]

    with pytest.raises(FrozenInstanceError):
        preserved_record.preserved_record_id = "changed"
    with pytest.raises(FrozenInstanceError):
        preserved_record.inbound_record_id = "changed"
    with pytest.raises(FrozenInstanceError):
        preserved_record.evidence_kind = "changed"
    with pytest.raises(TypeError):
        preserved_record.payload["evidence_kind"] = "changed"


def test_each_upstream_evidence_record_remains_unchanged_after_preservation():
    records = make_upstream_evidence_records()
    inspection_before, trust_before, review_before = deepcopy(records)

    EvidenceEngine().preserve(tuple(reversed(records)))

    assert records[0] == inspection_before
    assert records[1] == trust_before
    assert records[2] == review_before


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


def test_blank_inbound_record_id_raises_malformed_inbound_record():
    with pytest.raises(MalformedInboundEvidenceRecord):
        InboundEvidenceRecord(
            record_id=" ",
            evidence_kind="inspection_raw_result",
            source_domain=EvidenceSourceDomain.INSPECTION,
            payload={
                "input_id": "input-malformed",
                "inspection_result_id": "raw-malformed",
            },
        )


def test_blank_evidence_kind_raises_malformed_inbound_record():
    with pytest.raises(MalformedInboundEvidenceRecord):
        InboundEvidenceRecord(
            record_id="malformed-evidence-record",
            evidence_kind=" ",
            source_domain=EvidenceSourceDomain.INSPECTION,
            payload={
                "input_id": "input-malformed",
                "inspection_result_id": "raw-malformed",
            },
        )


def test_non_mapping_payload_raises_malformed_inbound_record():
    with pytest.raises(MalformedInboundEvidenceRecord):
        InboundEvidenceRecord(
            record_id="malformed-evidence-record",
            evidence_kind="inspection_raw_result",
            source_domain=EvidenceSourceDomain.INSPECTION,
            payload=("not", "a", "mapping"),  # type: ignore[arg-type]
        )


def test_invalid_source_domain_raises_malformed_inbound_record():
    with pytest.raises(MalformedInboundEvidenceRecord):
        InboundEvidenceRecord(
            record_id="malformed-evidence-record",
            evidence_kind="inspection_raw_result",
            source_domain="outside-domain",  # type: ignore[arg-type]
            payload={
                "input_id": "input-malformed",
                "inspection_result_id": "raw-malformed",
            },
        )


@pytest.mark.parametrize(
    "link",
    (
        {"from_record_id": " ", "to_record_id": "raw-1", "relation": "rel"},
        {"from_record_id": "input-1", "to_record_id": " ", "relation": "rel"},
        {"from_record_id": "input-1", "to_record_id": "raw-1", "relation": " "},
    ),
)
def test_blank_chain_link_fields_raise_evidence_domain_error(link):
    with pytest.raises(EvidenceLinkingFailure):
        EvidenceRecordLink(**link)


@pytest.mark.parametrize(
    "absence",
    (
        {
            "absence_id": "absence-1",
            "expected_stage": " ",
            "reason": "missing",
            "upstream_ref": "upstream-1",
        },
        {
            "absence_id": "absence-1",
            "expected_stage": "human_review",
            "reason": " ",
            "upstream_ref": "upstream-1",
        },
        {
            "absence_id": "absence-1",
            "expected_stage": "human_review",
            "reason": "missing",
            "upstream_ref": " ",
        },
    ),
)
def test_blank_absence_fields_raise_evidence_absence_failure(absence):
    with pytest.raises(EvidenceAbsenceFailure):
        EvidenceAbsenceMarker(**absence)


def test_blank_expected_absence_stage_raises_evidence_absence_failure():
    with pytest.raises(EvidenceAbsenceFailure):
        EvidenceEngine().preserve((), expected_stages=(" ",))


def test_non_read_only_evidence_view_raises_evidence_view_failure():
    with pytest.raises(EvidenceViewFailure):
        EvidenceView(view_id="view-1", records=(), read_only=False)


def test_empty_preserve_without_records_or_expected_absences_is_rejected():
    with pytest.raises(MalformedInboundEvidenceRecord):
        EvidenceEngine().preserve(())


def test_well_formed_expected_absence_is_preserved_in_evidence_view():
    view = EvidenceEngine().preserve(
        (),
        expected_stages=(EvidenceSourceDomain.HUMAN_REVIEW,),
    )

    assert len(view.absences) == 1
    assert view.absences[0].expected_stage == "human_review"
    assert view.absences[0].reason == "human_review_evidence_absent"
    assert view.absences[0].upstream_ref == "no-upstream-record"


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


def test_evidence_engine_exposes_no_forbidden_boundary_surface():
    engine = EvidenceEngine()
    forbidden_surface = (
        "inspect",
        "inspect_image",
        "image_inspection",
        "create_raw_inspection_judgement",
        "create_raw_inspection_judgment",
        "raw_inspection_judgement",
        "raw_inspection_judgment",
        "judge_raw_inspection",
        "create_inspection_result",
        "qualify",
        "qualify_trust",
        "trust_qualification",
        "qualify_trust_result",
        "review",
        "human_review",
        "perform_review",
        "record_review",
        "route",
        "route_for_review",
        "operational_routing",
        "evaluate",
        "evaluation",
        "measure_performance",
        "score_performance",
        "performance_score",
        "quality_score",
        "persist",
        "save",
        "store",
        "database",
        "database_storage",
        "db",
        "filesystem_storage",
        "write_filesystem",
        "render",
        "render_ui",
        "ui",
        "present",
        "train",
        "model_train",
        "update_model",
        "model_update",
        "recalibrate",
        "calibrate",
        "feedback",
        "feedback_loop",
        "stream",
        "streaming",
        "subscribe",
        "live",
        "run_live",
        "monitor",
        "monitoring",
    )

    for surface in forbidden_surface:
        assert not hasattr(engine, surface)
        assert not hasattr(EvidenceEngine, surface)


def test_canonical_evidence_outputs_expose_no_forbidden_boundary_fields():
    view = EvidenceEngine().preserve(make_upstream_evidence_records())
    absence_view = EvidenceEngine().preserve(
        (),
        expected_stages=(EvidenceSourceDomain.HUMAN_REVIEW,),
    )
    canonical_outputs = (
        view.records[0],
        view.links[0],
        absence_view.absences[0],
        view,
    )
    forbidden_fields = {
        "inspection_result",
        "trust_qualification_result",
        "review_result",
        "evaluation_report",
        "benchmark_result",
        "performance_score",
        "quality_score",
        "routing_command",
        "persistence_handle",
        "database_handle",
        "filesystem_path",
        "ui_payload",
        "rendering_payload",
        "model_update_payload",
        "training_payload",
        "calibration_payload",
        "feedback_payload",
        "live_subscription",
        "monitoring_payload",
    }

    for output in canonical_outputs:
        field_names = {field.name for field in fields(output)}
        assert field_names.isdisjoint(forbidden_fields)
        for field_name in forbidden_fields:
            assert not hasattr(output, field_name)


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


@pytest.mark.parametrize("marker", ("fabricated", "inferred", "synthetic_claim"))
def test_fabricated_records_are_refused_explicitly(marker):
    with pytest.raises(FabricatedEvidenceRecord):
        InboundEvidenceRecord(
            record_id="fabricated-record",
            evidence_kind="inspection_raw_result",
            source_domain=EvidenceSourceDomain.INSPECTION,
            payload={marker: True},
        )


def test_unauthorized_upstream_rerun_behaviour_does_not_exist():
    engine = EvidenceEngine()

    assert not hasattr(engine, "rerun_inspection")
    assert not hasattr(engine, "rerun_trust_qualification")
    assert not hasattr(engine, "run_upstream")
    assert not hasattr(engine, "reinspect")
