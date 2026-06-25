from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.evaluation import (
    EvaluationDimension,
    EvaluationEngine,
    EvaluationFinding,
    EvaluationReport,
    EvaluationResult,
    EvaluationStatus,
    FailureCategory,
    InvalidEvaluationReport,
    InvalidEvaluationResult,
)
from src.evidence import (
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceDomain,
    EvidenceReference,
    EvidenceResult,
    EvidenceStatus,
)
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
