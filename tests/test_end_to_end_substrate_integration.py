from __future__ import annotations

from dataclasses import fields, is_dataclass
import json
from pathlib import Path
import subprocess
import sys
from types import MappingProxyType
from typing import Iterable, Mapping

from src.evaluation import (
    EvidenceBackedEvaluationReport,
    EvaluationEngine,
    EvaluationDimension,
    EvaluationFindingStatus,
    EvaluationResult,
)
from src.evidence import (
    EvidenceEngine,
    EvidenceResult,
    EvidenceSourceDomain,
    EvidenceView,
)
from src.inspection import (
    INSPECTION_PREDICTION_KIND,
    PREDICTION_RAW_MEASURE_SCALE,
    InspectionEngine,
    InspectionEngineOutput,
    InspectionJudgement,
    InspectionPrediction,
    InspectionResult,
    LocalArtifactInferenceProvider,
    RawInspectionResult,
)
from src.integration import (
    DEFAULT_REFERENCE_SET_ID,
    EndToEndSubstrateIntegrationEngine,
    EndToEndSubstrateIntegrationResult,
    default_stabilized_inspection_input,
)
from src.review import (
    HumanReviewEngine,
    HumanReviewEngineOutput,
    HumanReviewResult,
    ReviewEvidenceRecord,
    ReviewerDecisionValue,
)
from src.trust import (
    DriftCautionStatus,
    DriftReference,
    QualifiedOutcome,
    TrustQualificationEngine,
    TrustQualificationEngineOutput,
    TrustQualificationResult,
    TrustQualifiedResult,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "scripts" / "run_end_to_end_substrate.py"

LOCAL_PROVIDER_FORBIDDEN_EVIDENCE_KEYS = {
    "artifact_format",
    "maxval",
    "model_metadata",
    "pixels",
    "predicted_judgement",
    "predicted_localization",
    "predicted_raw_anomaly_measure",
    "prediction_kind",
    "prediction_id",
    "provider_id",
}

FORBIDDEN_CLAIM_FIELDS = {
    "accuracy",
    "aggregate_score",
    "benchmark_result",
    "model_performance_claim",
    "overall_score",
    "pass_rate",
    "performance_claim",
    "production_readiness_claim",
    "quality_score",
    "score",
}


def run_default_integration() -> EndToEndSubstrateIntegrationResult:
    return EndToEndSubstrateIntegrationEngine().run()


def no_review_drift_reference() -> DriftReference:
    return DriftReference(
        reference_id="integration-drift-reference-no-review-001",
        available=True,
        drift_score=0.0,
    )


def test_full_chain_composition_works():
    result = run_default_integration()
    trust_result = result.trust_qualification_output.trust_qualification_result

    assert isinstance(result.inspection_output, InspectionEngineOutput)
    assert isinstance(result.trust_qualification_output, TrustQualificationEngineOutput)
    assert trust_result.qualified_outcome is QualifiedOutcome.REVIEW
    assert trust_result.drift_caution.status is DriftCautionStatus.DRIFTED
    assert isinstance(result.human_review_output, HumanReviewEngineOutput)
    assert isinstance(result.evidence_view, EvidenceView)
    assert isinstance(result.evaluation_report, EvidenceBackedEvaluationReport)
    assert result.human_review_output.review_evidence_record.reviewer_decision.decision is (
        ReviewerDecisionValue.INCONCLUSIVE
    )
    assert result.evaluation_report.metadata["reference_set_id"] == (
        DEFAULT_REFERENCE_SET_ID
    )


def test_integrated_result_references_every_stage_id():
    result = run_default_integration()
    references = result.stage_references
    review_case = result.review_case
    review_output = result.human_review_output

    assert review_case is not None
    assert review_output is not None

    assert references.source_input_id == result.source_input.input_id
    assert references.inspection_result_id == (
        result.inspection_output.raw_inspection_result.inspection_result_id
    )
    assert references.inspection_evidence_record_id == (
        result.inspection_output.inspection_evidence_record.record_id
    )
    assert references.trust_qualification_result_id == (
        result.trust_qualification_output.trust_qualification_result
        .qualification_result_id
    )
    assert references.trust_qualification_evidence_record_id == (
        result.trust_qualification_output.trust_qualification_evidence_record
        .record_id
    )
    assert references.review_case_id == review_case.review_case_id
    assert references.review_evidence_record_id == (
        review_output.review_evidence_record.record_id
    )
    assert references.reviewer_decision_id == (
        review_output.review_evidence_record.reviewer_decision.decision_id
    )
    assert references.evidence_view_id == result.evidence_view.view_id
    assert references.evaluation_report_id == result.evaluation_report.report_id


def test_canonical_only_contract_flow_contains_no_legacy_stage_artifacts():
    result = run_default_integration()

    assert isinstance(result.inspection_output.raw_inspection_result, RawInspectionResult)
    assert isinstance(
        result.trust_qualification_output.trust_qualification_result,
        TrustQualificationResult,
    )
    assert isinstance(
        result.human_review_output.review_evidence_record,
        ReviewEvidenceRecord,
    )
    assert isinstance(result.evidence_view, EvidenceView)
    assert isinstance(result.evaluation_report, EvidenceBackedEvaluationReport)

    legacy_types = (
        InspectionResult,
        TrustQualifiedResult,
        HumanReviewResult,
        EvidenceResult,
        EvaluationResult,
    )
    assert not any(
        isinstance(value, legacy_types)
        for value in _walk_object_graph(result)
    )


def test_evidence_chain_contains_expected_relations():
    result = run_default_integration()

    relations = {link.relation for link in result.evidence_view.links}

    assert relations >= {
        "source_input_to_raw_inspection",
        "raw_inspection_result_to_trust_qualification",
        "trust_qualification_to_human_review",
        "review_case_to_reviewer_decision",
        "inspection_evidence_to_trust_evidence",
        "trust_evidence_to_human_review_evidence",
    }


def test_no_review_branch_records_absence_not_weak_review_performance():
    result = EndToEndSubstrateIntegrationEngine().run(
        inspection_input=default_stabilized_inspection_input(),
        drift_reference=no_review_drift_reference(),
    )
    trust_result = result.trust_qualification_output.trust_qualification_result

    assert trust_result.qualified_outcome is not QualifiedOutcome.REVIEW
    assert trust_result.drift_caution.status is not DriftCautionStatus.DRIFTED
    assert result.review_case is None
    assert result.human_review_output is None
    assert result.stage_references.review_case_id is None
    assert result.stage_references.review_evidence_record_id is None

    review_absences = [
        absence for absence in result.evidence_view.absences
        if absence.expected_stage == EvidenceSourceDomain.HUMAN_REVIEW.value
    ]
    assert len(review_absences) == 1
    assert review_absences[0].reason == "human_review_evidence_absent"

    review_disclosures = [
        disclosure for disclosure in result.evaluation_report.absence_disclosures
        if disclosure.dimension_or_category == EvaluationDimension.REVIEW.value
    ]
    assert review_disclosures
    assert all(
        finding.dimension is not EvaluationDimension.REVIEW
        for finding in result.evaluation_report.dimension_findings
        if finding.status is EvaluationFindingStatus.WEAK
    )


def test_local_provider_path_produces_end_to_end_integration_result():
    result = EndToEndSubstrateIntegrationEngine().run_local_provider_fixture()
    raw_result = result.inspection_output.raw_inspection_result
    trust_result = result.trust_qualification_output.trust_qualification_result

    assert isinstance(result, EndToEndSubstrateIntegrationResult)
    assert raw_result.judgement is InspectionJudgement.DEFECT
    assert raw_result.raw_anomaly_measure == 75.0
    assert raw_result.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert raw_result.examination_kind == INSPECTION_PREDICTION_KIND
    assert trust_result.qualified_outcome is QualifiedOutcome.REJECT
    assert trust_result.drift_caution.status is DriftCautionStatus.UNAVAILABLE
    assert trust_result.calibrated_confidence.value == 0.5
    assert trust_result.calibrated_confidence.value != raw_result.raw_anomaly_measure
    assert result.review_case is None
    assert result.human_review_output is None
    assert isinstance(result.evidence_view, EvidenceView)
    assert isinstance(result.evaluation_report, EvidenceBackedEvaluationReport)

    review_absences = [
        absence for absence in result.evidence_view.absences
        if absence.expected_stage == EvidenceSourceDomain.HUMAN_REVIEW.value
    ]
    assert len(review_absences) == 1
    assert review_absences[0].reason == "human_review_evidence_absent"


def test_local_provider_path_can_route_review_only_with_explicit_drift_reference():
    result = EndToEndSubstrateIntegrationEngine().run_local_provider_fixture(
        drift_reference=DriftReference(
            reference_id="local-provider-drifted-reference-001",
            available=True,
            drift_score=0.8,
        )
    )
    trust_result = result.trust_qualification_output.trust_qualification_result

    assert trust_result.qualified_outcome is QualifiedOutcome.REVIEW
    assert trust_result.drift_caution.status is DriftCautionStatus.DRIFTED
    assert result.review_case is not None
    assert result.human_review_output is not None
    assert not result.evidence_view.absences
    assert {record.source_domain for record in result.evidence_view.records} == {
        EvidenceSourceDomain.INSPECTION,
        EvidenceSourceDomain.TRUST,
        EvidenceSourceDomain.HUMAN_REVIEW,
    }


def test_local_provider_output_is_not_passed_downstream_as_evidence():
    result = EndToEndSubstrateIntegrationEngine().run_local_provider_fixture()

    assert not any(
        isinstance(value, (InspectionPrediction, LocalArtifactInferenceProvider))
        for value in _walk_object_graph(result.evidence_view)
    )
    assert {record.source_domain for record in result.evidence_view.records} == {
        EvidenceSourceDomain.INSPECTION,
        EvidenceSourceDomain.TRUST,
    }

    evidence_keys = set(_walk_field_and_mapping_names(result.evidence_view))
    assert not (evidence_keys & LOCAL_PROVIDER_FORBIDDEN_EVIDENCE_KEYS)
    assert all(
        "performance" not in record.evidence_kind
        for record in result.evidence_view.records
    )


def test_local_provider_evaluation_is_evidence_backed_without_performance_claims():
    result = EndToEndSubstrateIntegrationEngine().run_local_provider_fixture()
    report = result.evaluation_report

    assert report.report_kind == "evidence_backed_evaluation_report"
    assert set(report.evidence_refs) == {
        record.preserved_record_id for record in result.evidence_view.records
    } | {absence.absence_id for absence in result.evidence_view.absences}
    assert not (set(_walk_field_and_mapping_names(report)) & FORBIDDEN_CLAIM_FIELDS)
    assert all(
        finding.status is not EvaluationFindingStatus.WEAK
        for finding in report.dimension_findings
    )


def test_local_provider_path_does_not_call_inspection_engine_inspect():
    class NoInspectInspectionEngine(InspectionEngine):
        def inspect(self, inspection_input):  # type: ignore[no-untyped-def]
            raise AssertionError("local provider path must not call inspect()")

    result = EndToEndSubstrateIntegrationEngine(
        inspection_engine=NoInspectInspectionEngine()
    ).run_local_provider_fixture()

    assert result.inspection_output.raw_inspection_result.judgement is (
        InspectionJudgement.DEFECT
    )
    assert not hasattr(InspectionEngine(), "provider")
    assert not hasattr(InspectionEngine(), "inference_provider")


def test_local_provider_path_does_not_change_default_integration_or_cli_path():
    default_result = run_default_integration()
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert default_result.source_input.input_id == "integration-input-000"
    assert default_result.inspection_output.raw_inspection_result.raw_measure_scale != (
        PREDICTION_RAW_MEASURE_SCALE
    )
    assert default_result.inspection_output.raw_inspection_result.examination_kind != (
        INSPECTION_PREDICTION_KIND
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["input_id"] == "integration-input-000"
    assert payload["qualified_outcome"] == "review"
    assert payload["human_review_occurred"] is True
    assert payload["preserved_record_count"] == 3
    assert payload["claims"] == {
        "ml_implemented": False,
        "cv_implemented": False,
        "production_ready": False,
        "performance_claim": False,
    }
    assert "local-provider" not in completed.stdout


def test_same_inputs_produce_identical_integrated_result():
    engine = EndToEndSubstrateIntegrationEngine()
    inspection_input = default_stabilized_inspection_input()
    drift_reference = DriftReference(
        reference_id="integration-drift-reference-repeatable-001",
        available=True,
        drift_score=0.8,
    )

    first = engine.run(
        inspection_input=inspection_input,
        drift_reference=drift_reference,
    )
    assert first.human_review_output is not None
    reviewer_decision = first.human_review_output.review_evidence_record.reviewer_decision
    second = engine.run(
        inspection_input=inspection_input,
        drift_reference=drift_reference,
        reviewer_decision=reviewer_decision,
    )

    assert first == second


def test_boundary_surface_has_no_feedback_persistence_ui_or_score():
    engine = EndToEndSubstrateIntegrationEngine()
    result = engine.run()

    assert not hasattr(engine, "feedback")
    assert not hasattr(engine, "feedback_loop")
    assert not hasattr(engine, "update_model")
    assert not hasattr(engine, "train")
    assert not hasattr(engine, "retrain")
    assert not hasattr(engine, "recalibrate")
    assert not hasattr(engine, "persist")
    assert not hasattr(engine, "save")
    assert not hasattr(engine, "store")
    assert not hasattr(engine, "render")
    assert not hasattr(engine, "present_evidence")
    assert not hasattr(engine, "prototype_asset")
    assert not hasattr(result, "score")
    assert not hasattr(result, "aggregate_score")
    assert not hasattr(result.evaluation_report, "score")
    assert not hasattr(result.evaluation_report, "aggregate_score")
    assert not hasattr(result.evaluation_report, "overall_score")
    assert not hasattr(result.evaluation_report, "pass_rate")
    assert "prototype" not in result.source_input.artifact_uri


def test_legacy_primary_flow_methods_are_not_used():
    class BoundaryTrustEngine(TrustQualificationEngine):
        def _qualify_legacy(self, inspection_result):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy trust flow must not be used")

    class BoundaryHumanReviewEngine(HumanReviewEngine):
        def create_request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy review flow must not be used")

        def review(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy review flow must not be used")

        def review_request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy review flow must not be used")

    class BoundaryEvidenceEngine(EvidenceEngine):
        def create_bundle(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy evidence flow must not be used")

        def collect(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy evidence flow must not be used")

    class BoundaryEvaluationEngine(EvaluationEngine):
        def _evaluate_legacy(self, evidence_result):  # type: ignore[no-untyped-def]
            raise AssertionError("legacy evaluation flow must not be used")

    result = EndToEndSubstrateIntegrationEngine(
        trust_engine=BoundaryTrustEngine(),
        human_review_engine=BoundaryHumanReviewEngine(),
        evidence_engine=BoundaryEvidenceEngine(),
        evaluation_engine=BoundaryEvaluationEngine(),
    ).run()

    assert isinstance(result, EndToEndSubstrateIntegrationResult)


def _walk_object_graph(value: object) -> Iterable[object]:
    seen: set[int] = set()
    yield from _walk(value, seen)


def _walk(value: object, seen: set[int]) -> Iterable[object]:
    value_id = id(value)
    if value_id in seen:
        return
    seen.add(value_id)
    yield value

    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield from _walk(getattr(value, field.name), seen)
        return

    if isinstance(value, MappingProxyType):
        for item in value.values():
            yield from _walk(item, seen)
        return

    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk(key, seen)
            yield from _walk(item, seen)
        return

    if isinstance(value, tuple):
        for item in value:
            yield from _walk(item, seen)
        return

    if isinstance(value, list):
        for item in value:
            yield from _walk(item, seen)
        return

    if isinstance(value, set):
        for item in value:
            yield from _walk(item, seen)
        return


def _walk_field_and_mapping_names(value: object) -> Iterable[str]:
    seen: set[int] = set()
    yield from _walk_names(value, seen)


def _walk_names(value: object, seen: set[int]) -> Iterable[str]:
    value_id = id(value)
    if value_id in seen:
        return
    seen.add(value_id)

    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield field.name
            yield from _walk_names(getattr(value, field.name), seen)
        return

    if isinstance(value, MappingProxyType):
        for key, item in value.items():
            yield str(key)
            yield from _walk_names(item, seen)
        return

    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _walk_names(item, seen)
        return

    if isinstance(value, tuple):
        for item in value:
            yield from _walk_names(item, seen)
        return

    if isinstance(value, list):
        for item in value:
            yield from _walk_names(item, seen)
        return

    if isinstance(value, set):
        for item in value:
            yield from _walk_names(item, seen)
        return
