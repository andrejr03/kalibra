from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.evaluation import (
    EVALUATION_REPORT_KIND,
    WEAK_PERFORMANCE_EVIDENCE_KIND,
    AbsenceDisclosure,
    DimensionFinding,
    EvaluationFindingStatus,
    EvidenceBackedEvaluationReport,
    EvaluationDimension,
    EvaluationEngine,
    EvaluationFinding,
    EvaluationReport,
    EvaluationResult,
    EvaluationStatus,
    FabricatedEvaluationEvidence,
    FailureCategory,
    FailureCategoryFinding,
    InvalidEvaluationReport,
    InvalidEvaluationResult,
    PrototypePerformanceEvaluationRejected,
    UntraceableEvaluationFinding,
)
from src.evidence import (
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceDomain,
    EvidenceEngine,
    EvidenceRecordLink,
    EvidenceReference,
    EvidenceResult,
    EvidenceSourceDomain,
    EvidenceStatus,
    EvidenceView,
    InboundEvidenceRecord,
    PreservedEvidenceRecord,
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
    HumanReviewEngine,
    ReviewerDecision,
    ReviewerDecisionValue,
)
from src.trust import (
    AbstentionStatus,
    CalibratedConfidence,
    DriftReference,
    DriftAssessment,
    DriftAssessmentStatus,
    TrustQualificationEngine,
    QualificationOutcome,
    TrustQualifiedResult,
)


def make_inspection_result(content_sha256: str = "abc123") -> InspectionResult:
    inspection_input = InspectionInput(
        source_path=Path("part.png"),
        content_sha256=content_sha256,
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


def make_trust_result(inspection_result: InspectionResult) -> TrustQualifiedResult:
    return TrustQualifiedResult(
        inspection_result=inspection_result,
        calibrated_confidence=CalibratedConfidence(
            value=0.8,
            method_id="trust-method",
            method_version="1",
        ),
        qualification_outcome=QualificationOutcome.ACCEPT,
        abstention_status=AbstentionStatus.NOT_ABSTAINED,
        drift_assessment=DriftAssessment(
            status=DriftAssessmentStatus.NOT_ASSESSED,
            method_id="trust-method",
            method_version="1",
        ),
        method_id="trust-method",
        method_version="1",
    )


def make_evidence_result(content_sha256: str = "abc123") -> EvidenceResult:
    inspection_result = make_inspection_result(content_sha256)
    trust_result = make_trust_result(inspection_result)
    bundle = EvidenceBundle(
        inspection_result=inspection_result,
        trust_qualified_result=trust_result,
        artifacts=(
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
        ),
        bundle_id="bundle-1",
    )
    return EvidenceResult(
        inspection_result=inspection_result,
        trust_qualified_result=trust_result,
        evidence_bundle=bundle,
        method_id="evidence-method",
        method_version="1",
    )


def make_raw_inspection_result(
    raw_measure: float = 65.0,
    judgement: InspectionJudgement = InspectionJudgement.DEFECT,
    result_id: str = "raw-evaluation-result-1",
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
        input_id="input-evaluation-1",
        judgement=judgement,
        localization=localization,
        raw_anomaly_measure=raw_measure,
        examination_id="examination-evaluation-1",
    )


def make_preserved_evidence_view(
    include_review: bool = True,
    include_drift: bool = True,
    extra_records: tuple[PreservedEvidenceRecord, ...] = (),
) -> EvidenceView:
    raw_result = make_raw_inspection_result()
    inspection_record = InspectionEvidenceRecord(
        record_id="inspection-evaluation-evidence-1",
        input_id=raw_result.input_id,
        inspection_result_id=raw_result.inspection_result_id,
        raw_inspection_result=raw_result,
    )
    drift_reference = (
        DriftReference(
            reference_id="drift-reference-evaluation-1",
            available=True,
            drift_score=0.8,
        )
        if include_drift
        else None
    )
    trust_output = TrustQualificationEngine().qualify(
        raw_result,
        drift_reference=drift_reference,
    )
    records = (
        inspection_record,
        trust_output.trust_qualification_evidence_record,
    )
    if include_review:
        review_case = HumanReviewEngine().create_case(
            raw_inspection_result=raw_result,
            trust_qualification_result=trust_output.trust_qualification_result,
            review_case_id="review-evaluation-case-1",
        )
        review_output = HumanReviewEngine().record_decision(
            review_case,
            ReviewerDecision(
                decision_id="reviewer-decision-evaluation-1",
                review_case_id=review_case.review_case_id,
                reviewer_ref="reviewer-1",
                decision=ReviewerDecisionValue.INCONCLUSIVE,
                rationale="Fixed evaluation substrate review decision.",
            ),
        )
        records = (*records, review_output.review_evidence_record)
    evidence_view = EvidenceEngine().preserve(
        records,
        expected_stages=(EvidenceSourceDomain.HUMAN_REVIEW,),
    )
    if not extra_records:
        return evidence_view
    return EvidenceView(
        view_id=(
            f"{evidence_view.view_id}:"
            f"{':'.join(record.preserved_record_id for record in extra_records)}"
        ),
        records=(*evidence_view.records, *extra_records),
        links=evidence_view.links,
        absences=evidence_view.absences,
    )


def make_weak_performance_record(
    dimension: EvaluationDimension = EvaluationDimension.CALIBRATION,
    category: FailureCategory = FailureCategory.CONFIDENT_ERROR,
) -> PreservedEvidenceRecord:
    record_id = f"weak-performance-evidence-{dimension.value}-{category.value}"
    return PreservedEvidenceRecord(
        preserved_record_id=f"preserved-{record_id}",
        inbound_record_id=record_id,
        evidence_kind=WEAK_PERFORMANCE_EVIDENCE_KIND,
        source_domain=EvidenceSourceDomain.TRUST,
        payload={
            "weak_performance": True,
            "dimension": dimension.value,
            "failure_category": category.value,
            "summary": "Explicit weak-performance fixture for substrate tests.",
        },
        content_hash=f"weak-performance-content-{dimension.value}-{category.value}",
    )


def make_report(evidence_result: EvidenceResult) -> EvaluationReport:
    return EvaluationReport(
        evidence_result=evidence_result,
        findings=(
            EvaluationFinding(
                dimension=EvaluationDimension.DETECTION_QUALITY,
                status=EvaluationStatus.NOT_EVALUATED,
                summary="Detection quality evidence is represented for later evaluation.",
            ),
        ),
        status=EvaluationStatus.NOT_EVALUATED,
        report_id="evaluation-report-1",
    )


class RecordingEvaluationMethod:
    method_id = "recording-evaluation-method"
    method_version = "1"

    def __init__(self) -> None:
        self.seen_evidence_result: EvidenceResult | None = None

    def evaluate(self, evidence_result: EvidenceResult) -> EvaluationResult:
        self.seen_evidence_result = evidence_result
        return EvaluationResult(
            evidence_result=evidence_result,
            evaluation_report=make_report(evidence_result),
            method_id=self.method_id,
            method_version=self.method_version,
        )


def test_evaluation_result_references_original_evidence_result():
    evidence_result = make_evidence_result()
    result = EvaluationEngine(method=RecordingEvaluationMethod()).evaluate(
        evidence_result
    )

    assert result.evidence_result is evidence_result
    assert result.evaluation_report.evidence_result is evidence_result


def test_evaluation_dimensions_are_explicit_and_complete():
    assert {dimension.value for dimension in EvaluationDimension} == {
        "detection_quality",
        "calibration",
        "uncertainty_quality",
        "review_quality",
        "drift_response",
    }


def test_failure_categories_are_explicit_and_complete():
    assert {category.value for category in FailureCategory} == {
        "missed_defect",
        "false_alarm",
        "confident_error",
        "misplaced_uncertainty",
        "mislocalized_defect",
        "unresponsive_drift",
    }


def test_evaluation_findings_are_immutable():
    finding = EvaluationFinding(
        dimension=EvaluationDimension.REVIEW_QUALITY,
        status=EvaluationStatus.NOT_EVALUATED,
        summary="Review quality evidence is represented for later evaluation.",
    )

    with pytest.raises(FrozenInstanceError):
        finding.status = EvaluationStatus.REPORTED


def test_report_rejects_duplicate_dimensions():
    evidence_result = make_evidence_result()
    finding = EvaluationFinding(
        dimension=EvaluationDimension.CALIBRATION,
        status=EvaluationStatus.NOT_EVALUATED,
        summary="Calibration evidence is represented for later evaluation.",
    )

    with pytest.raises(InvalidEvaluationReport):
        EvaluationReport(
            evidence_result=evidence_result,
            findings=(finding, finding),
            status=EvaluationStatus.NOT_EVALUATED,
            report_id="evaluation-report-1",
        )


def test_engine_rejects_malformed_evaluation_results():
    class MalformedEvaluationMethod:
        method_id = "malformed-evaluation-method"
        method_version = "1"

        def evaluate(self, evidence_result: EvidenceResult) -> object:
            return object()

    with pytest.raises(InvalidEvaluationResult):
        EvaluationEngine(method=MalformedEvaluationMethod()).evaluate(
            make_evidence_result()
        )


def test_delegated_evaluation_protocol_is_respected():
    evidence_result = make_evidence_result()
    method = RecordingEvaluationMethod()

    result = EvaluationEngine(method=method).evaluate(evidence_result)

    assert method.seen_evidence_result is evidence_result
    assert result.method_id == method.method_id
    assert result.method_version == method.method_version


def test_engine_preserves_evidence_result_reference():
    evidence_result = make_evidence_result()

    result = EvaluationEngine(method=RecordingEvaluationMethod()).evaluate(
        evidence_result
    )

    assert result.evidence_result is evidence_result
    assert result.evidence_result.evidence_bundle is evidence_result.evidence_bundle


def test_report_must_be_derived_from_same_evidence_result():
    evidence_result = make_evidence_result()
    other_evidence_result = make_evidence_result("def456")

    class MismatchedEvaluationMethod(RecordingEvaluationMethod):
        def evaluate(self, evidence_result: EvidenceResult) -> EvaluationResult:
            return EvaluationResult(
                evidence_result=evidence_result,
                evaluation_report=make_report(other_evidence_result),
                method_id=self.method_id,
                method_version=self.method_version,
            )

    with pytest.raises(InvalidEvaluationResult):
        EvaluationEngine(method=MismatchedEvaluationMethod()).evaluate(evidence_result)


def test_engine_rejects_method_identity_mismatch():
    class MismatchedMethodIdentity(RecordingEvaluationMethod):
        def evaluate(self, evidence_result: EvidenceResult) -> EvaluationResult:
            return EvaluationResult(
                evidence_result=evidence_result,
                evaluation_report=make_report(evidence_result),
                method_id="other-evaluation-method",
                method_version=self.method_version,
            )

    with pytest.raises(InvalidEvaluationResult):
        EvaluationEngine(method=MismatchedMethodIdentity()).evaluate(
            make_evidence_result()
        )


def test_preserved_evidence_can_be_consumed_read_only():
    evidence_view = make_preserved_evidence_view()

    report = EvaluationEngine().evaluate(evidence_view)

    assert isinstance(report, EvidenceBackedEvaluationReport)
    assert evidence_view.read_only is True
    assert report.report_kind == EVALUATION_REPORT_KIND


def test_evaluation_report_is_traceable_to_preserved_evidence_records():
    evidence_view = make_preserved_evidence_view()

    report = EvaluationEngine().evaluate(evidence_view)

    preserved_refs = {record.preserved_record_id for record in evidence_view.records}
    assert preserved_refs.issubset(set(report.evidence_refs))
    for finding in report.dimension_findings:
        assert set(finding.evidence_refs).issubset(set(report.evidence_refs))


def test_evaluation_dimensions_remain_separate_in_report():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    dimensions = {finding.dimension for finding in report.dimension_findings}

    assert dimensions == {
        EvaluationDimension.DETECTION,
        EvaluationDimension.CALIBRATION,
        EvaluationDimension.UNCERTAINTY,
        EvaluationDimension.REVIEW,
        EvaluationDimension.DRIFT,
    }
    assert len(report.dimension_findings) == len(dimensions)


def test_named_failure_categories_remain_separate():
    weak_records = tuple(
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=category,
        )
        for category in FailureCategory
    )
    report = EvaluationEngine().evaluate(
        make_preserved_evidence_view(extra_records=weak_records)
    )

    categories = {finding.category for finding in report.failure_category_findings}

    assert categories == set(FailureCategory)
    assert len(report.failure_category_findings) == len(categories)


def test_missing_evidence_produces_absence_disclosure_not_weak_score():
    evidence_view = make_preserved_evidence_view(include_review=False)

    report = EvaluationEngine().evaluate(evidence_view)

    review_disclosures = [
        disclosure for disclosure in report.absence_disclosures
        if disclosure.dimension_or_category == EvaluationDimension.REVIEW.value
    ]
    assert review_disclosures
    assert all(
        finding.dimension is not EvaluationDimension.REVIEW
        for finding in report.dimension_findings
        if finding.status is EvaluationFindingStatus.WEAK
    )


def test_weak_performance_evidence_produces_weak_finding_not_absence():
    weak_record = make_weak_performance_record(
        dimension=EvaluationDimension.CALIBRATION,
        category=FailureCategory.CONFIDENT_ERROR,
    )

    report = EvaluationEngine().evaluate(
        make_preserved_evidence_view(extra_records=(weak_record,))
    )

    weak_dimensions = {
        finding.dimension
        for finding in report.dimension_findings
        if finding.status is EvaluationFindingStatus.WEAK
    }
    weak_categories = {
        finding.category
        for finding in report.failure_category_findings
        if finding.status is EvaluationFindingStatus.WEAK
    }
    absence_targets = {
        disclosure.dimension_or_category
        for disclosure in report.absence_disclosures
    }

    assert EvaluationDimension.CALIBRATION in weak_dimensions
    assert FailureCategory.CONFIDENT_ERROR in weak_categories
    assert EvaluationDimension.CALIBRATION.value not in absence_targets
    assert FailureCategory.CONFIDENT_ERROR.value not in absence_targets


def test_no_single_flattering_aggregate_exists():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    assert not hasattr(report, "score")
    assert not hasattr(report, "aggregate_score")
    assert not hasattr(report, "overall_score")
    assert not hasattr(report, "pass_rate")


def test_prototype_visuals_cannot_be_treated_as_performance_evidence():
    prototype_record = PreservedEvidenceRecord(
        preserved_record_id="preserved-prototype-performance-evaluation-1",
        inbound_record_id="prototype-performance-evaluation-1",
        evidence_kind="performance_evidence",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "artifact_kind": "prototype_visual",
            "claim": "performance evidence",
        },
        content_hash="prototype-performance-content-hash",
    )

    with pytest.raises(PrototypePerformanceEvaluationRejected):
        EvaluationEngine().evaluate(
            EvidenceView(
                view_id="prototype-performance-view",
                records=(prototype_record,),
            )
        )


def test_evidence_records_are_not_mutated_by_evaluation():
    evidence_view = make_preserved_evidence_view()
    before = repr(evidence_view)

    EvaluationEngine().evaluate(evidence_view)

    assert repr(evidence_view) == before


def test_no_cross_domain_or_evidence_mutation_behaviour_exists():
    engine = EvaluationEngine()

    assert not hasattr(engine, "inspect")
    assert not hasattr(engine, "calibrate")
    assert not hasattr(engine, "qualify")
    assert not hasattr(engine, "route_for_review")
    assert not hasattr(engine, "review")
    assert not hasattr(engine, "mutate_evidence")
    assert not hasattr(engine, "write_evidence")


def test_no_model_update_training_recalibration_or_feedback_behaviour_exists():
    engine = EvaluationEngine()

    assert not hasattr(engine, "update_model")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "retrain")
    assert not hasattr(engine, "recalibrate")
    assert not hasattr(engine, "feedback_loop")


def test_same_fixed_evidence_produces_identical_evaluation_report():
    evidence_view = make_preserved_evidence_view()
    engine = EvaluationEngine()

    first = engine.evaluate(evidence_view)
    second = engine.evaluate(evidence_view)

    assert first == second


def test_untraceable_findings_are_refused():
    with pytest.raises(UntraceableEvaluationFinding):
        DimensionFinding(
            finding_id="dimension-finding-untraceable",
            dimension=EvaluationDimension.DETECTION,
            status=EvaluationFindingStatus.SUPPORTED,
            evidence_refs=(),
            summary="This finding has no preserved evidence reference.",
        )


def test_fabrication_pressure_is_refused_explicitly():
    fabricated_record = PreservedEvidenceRecord(
        preserved_record_id="preserved-fabricated-evaluation-record",
        inbound_record_id="fabricated-evaluation-record",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "fabricated": True,
            "summary": "This should never become evaluation evidence.",
        },
        content_hash="fabricated-evaluation-content-hash",
    )

    with pytest.raises(FabricatedEvaluationEvidence):
        EvaluationEngine().evaluate(
            EvidenceView(
                view_id="fabricated-evaluation-view",
                records=(fabricated_record,),
            )
        )


def test_repo_wide_public_contracts_remain_intact():
    legacy_report = make_report(make_evidence_result())
    substrate_report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    assert isinstance(legacy_report, EvaluationReport)
    assert isinstance(substrate_report, EvidenceBackedEvaluationReport)
    assert EvaluationDimension.DETECTION_QUALITY is EvaluationDimension.DETECTION
    assert EvaluationDimension.REVIEW_QUALITY is EvaluationDimension.REVIEW
    assert FailureCategory.CONFIDENT_ERROR.value == "confident_error"
