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
    NonReproducibleEvaluation,
    PreservedEvidenceInput,
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

EXPECTED_DIMENSION_FINDING_ORDER = (
    EvaluationDimension.DETECTION,
    EvaluationDimension.CALIBRATION,
    EvaluationDimension.UNCERTAINTY,
    EvaluationDimension.REVIEW,
    EvaluationDimension.DRIFT,
)

EXPECTED_FAILURE_CATEGORY_FINDING_ORDER = (
    FailureCategory.MISSED_DEFECT,
    FailureCategory.FALSE_ALARM,
    FailureCategory.CONFIDENT_ERROR,
    FailureCategory.MISPLACED_UNCERTAINTY,
    FailureCategory.MISLOCALIZED_DEFECT,
    FailureCategory.UNRESPONSIVE_DRIFT,
)

AGGREGATE_SCORE_ATTRIBUTES = (
    "score",
    "aggregate_score",
    "overall_score",
    "pass_rate",
)

FORBIDDEN_ENGINE_BOUNDARY_ATTRIBUTES = (
    "inspect",
    "inspect_image",
    "image_inspection",
    "run_inspection",
    "calibrate",
    "qualify",
    "qualify_trust",
    "trust_qualification",
    "review",
    "human_review",
    "create_review_case",
    "record_review",
    "route",
    "route_for_review",
    "route_case",
    "operational_route",
    "routing_command",
    "mutate_evidence",
    "write_evidence",
    "update_evidence",
    "preserve",
    "preserve_evidence",
    "persist",
    "save",
    "load",
    "store",
    "database",
    "database_storage",
    "db",
    "filesystem",
    "filesystem_storage",
    "write_to_disk",
    "render",
    "render_ui",
    "ui",
    "rendering",
    "update_model",
    "model_update",
    "train",
    "retrain",
    "recalibrate",
    "feedback_loop",
    "feedback",
    "stream",
    "streaming",
    "live",
    "live_stream",
    "subscribe",
    "monitor",
)

FORBIDDEN_REPORT_FIELDS = (
    *AGGREGATE_SCORE_ATTRIBUTES,
    "benchmark_result",
    "benchmark_score",
    "statistical_confidence",
    "analytics_payload",
    "production_readiness",
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
)

EXPECTED_REPORT_METADATA_KEYS = {
    "evaluation_mode",
    "reference_set_id",
}


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


def make_absence_only_evidence_view() -> EvidenceView:
    evidence_engine = EvidenceEngine()
    return EvidenceView(
        view_id="absence-only-evaluation-view",
        records=(),
        absences=(
            evidence_engine.record_absence(
                EvidenceSourceDomain.INSPECTION,
                "inspection_evidence_absent",
                "absence-only-input",
            ),
            evidence_engine.record_absence(
                EvidenceSourceDomain.TRUST,
                "trust_evidence_absent",
                "absence-only-input",
            ),
            evidence_engine.record_absence(
                EvidenceSourceDomain.HUMAN_REVIEW,
                "human_review_evidence_absent",
                "absence-only-input",
            ),
        ),
    )


def make_weak_performance_record(
    dimension: EvaluationDimension = EvaluationDimension.CALIBRATION,
    category: FailureCategory = FailureCategory.CONFIDENT_ERROR,
    suffix: str = "",
) -> PreservedEvidenceRecord:
    suffix_part = f"-{suffix}" if suffix else ""
    record_id = (
        f"weak-performance-evidence-{dimension.value}-"
        f"{category.value}{suffix_part}"
    )
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


def test_legacy_evaluation_result_path_remains_compatibility_only():
    evidence_result = make_evidence_result()
    method = RecordingEvaluationMethod()

    result = EvaluationEngine(method=method).evaluate(evidence_result)

    assert isinstance(result, EvaluationResult)
    assert isinstance(result.evaluation_report, EvaluationReport)
    assert not isinstance(result, EvidenceBackedEvaluationReport)
    assert method.seen_evidence_result is evidence_result


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


def test_preserved_evidence_input_uses_canonical_report_path():
    evidence_view = make_preserved_evidence_view()
    evidence_input = PreservedEvidenceInput(
        evidence_view=evidence_view,
        reference_set_id="fixed-task-2-reference-set",
    )

    report = EvaluationEngine().evaluate(evidence_input)

    assert isinstance(report, EvidenceBackedEvaluationReport)
    assert report.metadata["reference_set_id"] == "fixed-task-2-reference-set"


def test_evaluation_report_is_traceable_to_preserved_evidence_records():
    evidence_view = make_preserved_evidence_view()

    report = EvaluationEngine().evaluate(evidence_view)

    preserved_refs = {record.preserved_record_id for record in evidence_view.records}
    assert preserved_refs.issubset(set(report.evidence_refs))
    for finding in report.dimension_findings:
        assert set(finding.evidence_refs).issubset(set(report.evidence_refs))


def test_report_rejects_untraceable_dimension_finding_reference():
    finding = DimensionFinding(
        finding_id="dimension-finding-missing-report-ref",
        dimension=EvaluationDimension.DETECTION,
        status=EvaluationFindingStatus.SUPPORTED,
        evidence_refs=("missing-preserved-evidence-ref",),
        summary="This finding references evidence outside the report.",
    )

    with pytest.raises(UntraceableEvaluationFinding):
        EvidenceBackedEvaluationReport(
            report_id="untraceable-dimension-report",
            dimension_findings=(finding,),
            failure_category_findings=(),
            absence_disclosures=(),
            evidence_refs=("preserved-evidence-ref",),
        )


def test_report_rejects_untraceable_failure_category_reference():
    finding = FailureCategoryFinding(
        finding_id="failure-category-finding-missing-report-ref",
        category=FailureCategory.CONFIDENT_ERROR,
        status=EvaluationFindingStatus.WEAK,
        evidence_refs=("missing-preserved-evidence-ref",),
        summary="This category finding references evidence outside the report.",
    )

    with pytest.raises(UntraceableEvaluationFinding):
        EvidenceBackedEvaluationReport(
            report_id="untraceable-category-report",
            dimension_findings=(),
            failure_category_findings=(finding,),
            absence_disclosures=(),
            evidence_refs=("preserved-evidence-ref",),
        )


def test_report_rejects_untraceable_absence_disclosure_reference():
    disclosure = AbsenceDisclosure(
        disclosure_id="absence-disclosure-missing-report-ref",
        dimension_or_category=EvaluationDimension.REVIEW.value,
        reason="review_quality_evidence_missing",
        evidence_refs=("missing-preserved-evidence-ref",),
    )

    with pytest.raises(UntraceableEvaluationFinding):
        EvidenceBackedEvaluationReport(
            report_id="untraceable-disclosure-report",
            dimension_findings=(),
            failure_category_findings=(),
            absence_disclosures=(disclosure,),
            evidence_refs=("preserved-evidence-ref",),
        )


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


def test_evidence_backed_report_rejects_duplicate_dimensions():
    first = DimensionFinding(
        finding_id="dimension-finding-review-1",
        dimension=EvaluationDimension.REVIEW,
        status=EvaluationFindingStatus.SUPPORTED,
        evidence_refs=("preserved-review-evidence-1",),
        summary="Review evidence remains dimension-specific.",
    )
    second = DimensionFinding(
        finding_id="dimension-finding-review-2",
        dimension=EvaluationDimension.REVIEW,
        status=EvaluationFindingStatus.SUPPORTED,
        evidence_refs=("preserved-review-evidence-1",),
        summary="Duplicate review evidence must be rejected.",
    )

    with pytest.raises(InvalidEvaluationReport):
        EvidenceBackedEvaluationReport(
            report_id="duplicate-dimension-report",
            dimension_findings=(first, second),
            failure_category_findings=(),
            absence_disclosures=(),
            evidence_refs=("preserved-review-evidence-1",),
        )


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


def test_evidence_backed_report_rejects_duplicate_failure_categories():
    first = FailureCategoryFinding(
        finding_id="failure-category-confident-error-1",
        category=FailureCategory.CONFIDENT_ERROR,
        status=EvaluationFindingStatus.WEAK,
        evidence_refs=("preserved-weak-evidence-1",),
        summary="Confident error evidence remains category-specific.",
    )
    second = FailureCategoryFinding(
        finding_id="failure-category-confident-error-2",
        category=FailureCategory.CONFIDENT_ERROR,
        status=EvaluationFindingStatus.WEAK,
        evidence_refs=("preserved-weak-evidence-1",),
        summary="Duplicate confident error evidence must be rejected.",
    )

    with pytest.raises(InvalidEvaluationReport):
        EvidenceBackedEvaluationReport(
            report_id="duplicate-category-report",
            dimension_findings=(),
            failure_category_findings=(first, second),
            absence_disclosures=(),
            evidence_refs=("preserved-weak-evidence-1",),
        )


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


def test_missing_dimensions_produce_absence_only():
    evidence_view = make_preserved_evidence_view(
        include_review=False,
        include_drift=False,
    )

    report = EvaluationEngine().evaluate(evidence_view)

    missing_dimensions = {
        EvaluationDimension.REVIEW,
        EvaluationDimension.DRIFT,
    }
    reported_dimensions = {finding.dimension for finding in report.dimension_findings}
    weak_dimensions = {
        finding.dimension
        for finding in report.dimension_findings
        if finding.status is EvaluationFindingStatus.WEAK
    }
    absence_targets = {
        disclosure.dimension_or_category
        for disclosure in report.absence_disclosures
    }

    assert reported_dimensions.isdisjoint(missing_dimensions)
    assert weak_dimensions.isdisjoint(missing_dimensions)
    assert {dimension.value for dimension in missing_dimensions}.issubset(
        absence_targets
    )


def test_missing_failure_categories_produce_absence_only():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    category_targets = {category.value for category in FailureCategory}
    absence_targets = {
        disclosure.dimension_or_category
        for disclosure in report.absence_disclosures
    }

    assert report.failure_category_findings == ()
    assert category_targets.issubset(absence_targets)


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


def test_weak_evidence_never_becomes_absence():
    dimension_records = tuple(
        make_weak_performance_record(
            dimension=dimension,
            category=FailureCategory.CONFIDENT_ERROR,
            suffix=f"dimension-{index}",
        )
        for index, dimension in enumerate(EXPECTED_DIMENSION_FINDING_ORDER)
    )
    category_records = tuple(
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=category,
            suffix=f"category-{index}",
        )
        for index, category in enumerate(EXPECTED_FAILURE_CATEGORY_FINDING_ORDER)
    )

    report = EvaluationEngine().evaluate(
        make_preserved_evidence_view(
            include_review=False,
            include_drift=False,
            extra_records=(*dimension_records, *category_records),
        )
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

    assert weak_dimensions == set(EXPECTED_DIMENSION_FINDING_ORDER)
    assert weak_categories == set(EXPECTED_FAILURE_CATEGORY_FINDING_ORDER)
    assert not {
        *(dimension.value for dimension in EXPECTED_DIMENSION_FINDING_ORDER),
        *(category.value for category in EXPECTED_FAILURE_CATEGORY_FINDING_ORDER),
    } & absence_targets


def test_absence_never_becomes_weak_evidence():
    report = EvaluationEngine().evaluate(make_absence_only_evidence_view())

    assert report.dimension_findings == ()
    assert report.failure_category_findings == ()
    assert report.absence_disclosures


def test_supported_evidence_produces_supported_dimension_findings_only():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    assert report.dimension_findings
    assert all(
        finding.status is EvaluationFindingStatus.SUPPORTED
        for finding in report.dimension_findings
    )


def test_no_single_flattering_aggregate_exists():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    for attribute in AGGREGATE_SCORE_ATTRIBUTES:
        assert not hasattr(report, attribute)


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

    for attribute in (
        "inspect",
        "calibrate",
        "qualify",
        "route_for_review",
        "review",
        "mutate_evidence",
        "write_evidence",
    ):
        assert not hasattr(engine, attribute)


def test_no_model_update_training_recalibration_or_feedback_behaviour_exists():
    engine = EvaluationEngine()

    for attribute in (
        "update_model",
        "train",
        "retrain",
        "recalibrate",
        "feedback_loop",
    ):
        assert not hasattr(engine, attribute)


def test_evaluation_engine_exposes_no_out_of_scope_boundary_surface():
    engine = EvaluationEngine()

    for attribute in FORBIDDEN_ENGINE_BOUNDARY_ATTRIBUTES:
        assert not hasattr(engine, attribute)


def test_same_fixed_evidence_produces_identical_evaluation_report():
    weak_record = make_weak_performance_record(
        dimension=EvaluationDimension.CALIBRATION,
        category=FailureCategory.CONFIDENT_ERROR,
    )
    evidence_view = make_preserved_evidence_view(
        include_review=False,
        extra_records=(weak_record,),
    )
    engine = EvaluationEngine()

    first = engine.evaluate(evidence_view)
    second = engine.evaluate(evidence_view)

    assert first == second
    assert first.report_id == second.report_id
    assert first.dimension_findings == second.dimension_findings
    assert first.failure_category_findings == second.failure_category_findings
    assert first.absence_disclosures == second.absence_disclosures


def test_equivalent_record_order_produces_identical_finding_and_absence_identity():
    weak_records = (
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=FailureCategory.MISSED_DEFECT,
            suffix="a",
        ),
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=FailureCategory.MISSED_DEFECT,
            suffix="b",
        ),
        make_weak_performance_record(
            dimension=EvaluationDimension.CALIBRATION,
            category=FailureCategory.CONFIDENT_ERROR,
            suffix="a",
        ),
        make_weak_performance_record(
            dimension=EvaluationDimension.CALIBRATION,
            category=FailureCategory.CONFIDENT_ERROR,
            suffix="b",
        ),
    )
    evidence_view = make_preserved_evidence_view(
        include_review=False,
        extra_records=weak_records,
    )
    reordered_view = EvidenceView(
        view_id=evidence_view.view_id,
        records=tuple(reversed(evidence_view.records)),
        links=evidence_view.links,
        absences=evidence_view.absences,
    )

    first = EvaluationEngine().evaluate(evidence_view)
    second = EvaluationEngine().evaluate(reordered_view)

    assert first.report_id == second.report_id
    assert (
        tuple(finding.dimension for finding in first.dimension_findings)
        == tuple(finding.dimension for finding in second.dimension_findings)
    )
    assert (
        tuple(finding.finding_id for finding in first.dimension_findings)
        == tuple(finding.finding_id for finding in second.dimension_findings)
    )
    assert (
        tuple(finding.category for finding in first.failure_category_findings)
        == tuple(finding.category for finding in second.failure_category_findings)
    )
    assert (
        tuple(finding.finding_id for finding in first.failure_category_findings)
        == tuple(finding.finding_id for finding in second.failure_category_findings)
    )
    assert (
        tuple(
            disclosure.dimension_or_category
            for disclosure in first.absence_disclosures
        )
        == tuple(
            disclosure.dimension_or_category
            for disclosure in second.absence_disclosures
        )
    )
    assert (
        tuple(
            disclosure.disclosure_id
            for disclosure in first.absence_disclosures
        )
        == tuple(
            disclosure.disclosure_id
            for disclosure in second.absence_disclosures
        )
    )


def test_dimension_findings_follow_fixed_dimension_order():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    assert (
        tuple(finding.dimension for finding in report.dimension_findings)
        == EXPECTED_DIMENSION_FINDING_ORDER
    )


def test_failure_category_findings_follow_fixed_category_order():
    weak_records = tuple(
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=category,
        )
        for category in EXPECTED_FAILURE_CATEGORY_FINDING_ORDER
    )

    report = EvaluationEngine().evaluate(
        make_preserved_evidence_view(extra_records=weak_records)
    )

    assert (
        tuple(finding.category for finding in report.failure_category_findings)
        == EXPECTED_FAILURE_CATEGORY_FINDING_ORDER
    )


def test_absence_disclosures_follow_dimensions_then_categories_order():
    expected_targets = tuple(
        target.value
        for target in (
            *EXPECTED_DIMENSION_FINDING_ORDER,
            *EXPECTED_FAILURE_CATEGORY_FINDING_ORDER,
        )
    )
    evidence_view = make_absence_only_evidence_view()

    first = EvaluationEngine().evaluate(evidence_view)
    second = EvaluationEngine().evaluate(evidence_view)

    assert (
        tuple(
            disclosure.dimension_or_category
            for disclosure in first.absence_disclosures
        )
        == expected_targets
    )
    assert (
        tuple(
            disclosure.dimension_or_category
            for disclosure in second.absence_disclosures
        )
        == expected_targets
    )
    assert (
        tuple(
            disclosure.disclosure_id
            for disclosure in first.absence_disclosures
        )
        == tuple(
            disclosure.disclosure_id
            for disclosure in second.absence_disclosures
        )
    )


def test_report_evidence_refs_are_sorted_and_record_order_independent():
    weak_records = tuple(
        make_weak_performance_record(
            dimension=EvaluationDimension.DETECTION,
            category=category,
        )
        for category in EXPECTED_FAILURE_CATEGORY_FINDING_ORDER
    )
    evidence_view = make_preserved_evidence_view(
        include_review=False,
        extra_records=weak_records,
    )
    reordered_view = EvidenceView(
        view_id=evidence_view.view_id,
        records=tuple(reversed(evidence_view.records)),
        links=evidence_view.links,
        absences=evidence_view.absences,
    )
    expected_refs = tuple(
        sorted(
            record.preserved_record_id for record in evidence_view.records
        )
        + sorted(absence.absence_id for absence in evidence_view.absences)
    )

    first = EvaluationEngine().evaluate(evidence_view)
    second = EvaluationEngine().evaluate(reordered_view)

    assert first.evidence_refs == tuple(sorted(first.evidence_refs))
    assert second.evidence_refs == tuple(sorted(second.evidence_refs))
    assert first.evidence_refs == second.evidence_refs
    assert first.evidence_refs == tuple(sorted(expected_refs))


def test_report_metadata_contains_only_deterministic_mode_and_reference_set():
    evidence_input = PreservedEvidenceInput(
        evidence_view=make_preserved_evidence_view(),
        reference_set_id="metadata-reference-set",
    )

    report = EvaluationEngine().evaluate(evidence_input)

    assert dict(report.metadata) == {
        "evaluation_mode": "deterministic_placeholder_substrate",
        "reference_set_id": "metadata-reference-set",
    }
    assert set(report.metadata) == EXPECTED_REPORT_METADATA_KEYS


def test_evidence_backed_report_exposes_no_out_of_scope_fields():
    report = EvaluationEngine().evaluate(make_preserved_evidence_view())
    report_dataclass_fields = set(report.__dataclass_fields__)

    for field_name in FORBIDDEN_REPORT_FIELDS:
        assert not hasattr(report, field_name)
        assert field_name not in report_dataclass_fields
        assert field_name not in report.metadata


def test_untraceable_findings_are_refused():
    with pytest.raises(UntraceableEvaluationFinding):
        DimensionFinding(
            finding_id="dimension-finding-untraceable",
            dimension=EvaluationDimension.DETECTION,
            status=EvaluationFindingStatus.SUPPORTED,
            evidence_refs=(),
            summary="This finding has no preserved evidence reference.",
        )


def test_failure_category_findings_with_empty_evidence_refs_are_refused():
    with pytest.raises(UntraceableEvaluationFinding):
        FailureCategoryFinding(
            finding_id="failure-category-finding-untraceable",
            category=FailureCategory.CONFIDENT_ERROR,
            status=EvaluationFindingStatus.WEAK,
            evidence_refs=(),
            summary="This category finding has no preserved evidence reference.",
        )


def test_absence_disclosures_with_empty_evidence_refs_are_refused():
    with pytest.raises(UntraceableEvaluationFinding):
        AbsenceDisclosure(
            disclosure_id="absence-disclosure-untraceable",
            dimension_or_category=EvaluationDimension.REVIEW.value,
            reason="review_quality_evidence_missing",
            evidence_refs=(),
        )


@pytest.mark.parametrize("marker", ("fabricated", "inferred", "synthetic_claim"))
def test_fabrication_pressure_is_refused_explicitly(marker: str):
    fabricated_record = PreservedEvidenceRecord(
        preserved_record_id=f"preserved-{marker}-evaluation-record",
        inbound_record_id=f"{marker}-evaluation-record",
        evidence_kind="inspection_raw_result",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            marker: True,
            "summary": "This should never become evaluation evidence.",
        },
        content_hash=f"{marker}-evaluation-content-hash",
    )

    with pytest.raises(FabricatedEvaluationEvidence):
        EvaluationEngine().evaluate(
            EvidenceView(
                view_id=f"{marker}-evaluation-view",
                records=(fabricated_record,),
            )
        )


@pytest.mark.parametrize(
    "marker",
    (
        "prototype_visual",
        "synthetic_overlay",
        "prototype_overlay",
        "illustrative_overlay",
    ),
)
def test_prototype_performance_markers_are_rejected_explicitly(marker: str):
    prototype_record = PreservedEvidenceRecord(
        preserved_record_id=f"preserved-{marker}-performance-evaluation-1",
        inbound_record_id=f"{marker}-performance-evaluation-1",
        evidence_kind="performance_evidence",
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload={
            "artifact_kind": marker,
            "claim": "performance evidence",
        },
        content_hash=f"{marker}-performance-content-hash",
    )

    with pytest.raises(PrototypePerformanceEvaluationRejected):
        EvaluationEngine().evaluate(
            EvidenceView(
                view_id=f"{marker}-performance-view",
                records=(prototype_record,),
            )
        )


def test_non_reproducible_evaluation_is_refused_explicitly():
    class NonReproducibleEvaluationEngine(EvaluationEngine):
        def _evaluate_preserved_once(
            self,
            evidence_input: PreservedEvidenceInput,
        ) -> EvidenceBackedEvaluationReport:
            report = super()._evaluate_preserved_once(evidence_input)
            count = getattr(self, "_report_count", 0) + 1
            object.__setattr__(self, "_report_count", count)
            return EvidenceBackedEvaluationReport(
                report_id=f"{report.report_id}:{count}",
                dimension_findings=report.dimension_findings,
                failure_category_findings=report.failure_category_findings,
                absence_disclosures=report.absence_disclosures,
                evidence_refs=report.evidence_refs,
                report_kind=report.report_kind,
                metadata=report.metadata,
            )

    with pytest.raises(NonReproducibleEvaluation):
        NonReproducibleEvaluationEngine().evaluate(make_preserved_evidence_view())


def test_evidence_view_mutation_during_evaluation_is_refused_explicitly():
    class MutatingEvaluationEngine(EvaluationEngine):
        def _evaluate_preserved_once(
            self,
            evidence_input: PreservedEvidenceInput,
        ) -> EvidenceBackedEvaluationReport:
            report = super()._evaluate_preserved_once(evidence_input)
            if not getattr(self, "_mutated", False):
                object.__setattr__(self, "_mutated", True)
                object.__setattr__(
                    evidence_input.evidence_view,
                    "records",
                    (
                        *evidence_input.evidence_view.records,
                        make_weak_performance_record(
                            dimension=EvaluationDimension.CALIBRATION,
                            category=FailureCategory.CONFIDENT_ERROR,
                            suffix="malicious-mutation",
                        ),
                    ),
                )
            return report

    with pytest.raises(InvalidEvaluationResult):
        MutatingEvaluationEngine().evaluate(make_preserved_evidence_view())


def test_repo_wide_public_contracts_remain_intact():
    legacy_report = make_report(make_evidence_result())
    substrate_report = EvaluationEngine().evaluate(make_preserved_evidence_view())

    assert isinstance(legacy_report, EvaluationReport)
    assert isinstance(substrate_report, EvidenceBackedEvaluationReport)
    assert EvaluationDimension.DETECTION_QUALITY is EvaluationDimension.DETECTION
    assert EvaluationDimension.REVIEW_QUALITY is EvaluationDimension.REVIEW
    assert FailureCategory.CONFIDENT_ERROR.value == "confident_error"
