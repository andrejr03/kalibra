from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from src.evaluation import (
    EvaluationEngine,
    EvidenceBackedEvaluationReport,
    PreservedEvidenceInput,
)
from src.evidence import EvidenceEngine, EvidenceSourceDomain, EvidenceView
from src.inspection import (
    InspectionEngine,
    InspectionEngineOutput,
    LocalArtifactInferenceProvider,
    RawInspectionResult,
    StabilizedInspectionInput,
)
from src.review import (
    HumanReviewEngine,
    HumanReviewEngineOutput,
    ReviewEvidenceRecord,
    ReviewQualifiedCase,
    ReviewerDecision,
    ReviewerDecisionValue,
)
from src.trust import (
    DriftCautionStatus,
    DriftReference,
    QualifiedOutcome,
    TrustQualificationEngine,
    TrustQualificationEngineOutput,
    TrustQualificationResult,
)

from .domain import (
    EndToEndSubstrateIntegrationResult,
    EndToEndSubstrateStageReferences,
)


DEFAULT_INTEGRATION_INPUT_ID = "integration-input-000"
DEFAULT_INTEGRATION_ARTIFACT_URI = "artifact://kalibra/integration/input-000.png"
DEFAULT_INTEGRATION_CONTENT_HASH = "integration-content-hash-000"
DEFAULT_DRIFT_REFERENCE_ID = "integration-drift-reference-001"
DEFAULT_DRIFT_SCORE = 0.8
DEFAULT_REVIEWER_REF = "deterministic-reviewer-001"
DEFAULT_REVIEWER_RATIONALE = (
    "Deterministic integration reviewer decision for substrate composition."
)
DEFAULT_REFERENCE_SET_ID = "fixed-end-to-end-substrate-reference-v1"
LOCAL_PROVIDER_INTEGRATION_INPUT_ID = "local-provider-end-to-end-blob-defect"
LOCAL_PROVIDER_FIXTURE_ARTIFACT_URI = "tests/fixtures/inspection/blob_defect.pgm"

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOCAL_PROVIDER_FIXTURE_PATH = _REPO_ROOT / LOCAL_PROVIDER_FIXTURE_ARTIFACT_URI

_UNSET = object()


@dataclass(frozen=True)
class EndToEndSubstrateIntegrationEngine:
    inspection_engine: InspectionEngine = field(default_factory=InspectionEngine)
    trust_engine: TrustQualificationEngine = field(
        default_factory=TrustQualificationEngine
    )
    human_review_engine: HumanReviewEngine = field(default_factory=HumanReviewEngine)
    evidence_engine: EvidenceEngine = field(default_factory=EvidenceEngine)
    evaluation_engine: EvaluationEngine = field(default_factory=EvaluationEngine)
    reference_set_id: str = DEFAULT_REFERENCE_SET_ID

    def run(
        self,
        inspection_input: StabilizedInspectionInput | None = None,
        drift_reference: DriftReference | None | object = _UNSET,
        reviewer_decision: ReviewerDecision | None = None,
        reviewer_ref: str = DEFAULT_REVIEWER_REF,
        reviewer_decision_value: ReviewerDecisionValue = (
            ReviewerDecisionValue.INCONCLUSIVE
        ),
        reviewer_rationale: str = DEFAULT_REVIEWER_RATIONALE,
    ) -> EndToEndSubstrateIntegrationResult:
        source_input = inspection_input or default_stabilized_inspection_input()
        drift = (
            default_drift_reference()
            if drift_reference is _UNSET
            else drift_reference
        )

        inspection_output = self.inspection_engine.inspect(source_input)
        return self.run_from_inspection_output(
            source_input=source_input,
            inspection_output=inspection_output,
            drift_reference=drift,
            reviewer_decision=reviewer_decision,
            reviewer_ref=reviewer_ref,
            reviewer_decision_value=reviewer_decision_value,
            reviewer_rationale=reviewer_rationale,
        )

    def run_local_provider_fixture(
        self,
        drift_reference: DriftReference | None = None,
        reviewer_decision: ReviewerDecision | None = None,
        reviewer_ref: str = DEFAULT_REVIEWER_REF,
        reviewer_decision_value: ReviewerDecisionValue = (
            ReviewerDecisionValue.INCONCLUSIVE
        ),
        reviewer_rationale: str = DEFAULT_REVIEWER_RATIONALE,
    ) -> EndToEndSubstrateIntegrationResult:
        source_input = local_provider_fixture_inspection_input()
        prediction = LocalArtifactInferenceProvider().predict(source_input)
        inspection_output = self.inspection_engine.transform_prediction(
            source_input,
            prediction,
        )
        return self.run_from_inspection_output(
            source_input=source_input,
            inspection_output=inspection_output,
            drift_reference=drift_reference,
            reviewer_decision=reviewer_decision,
            reviewer_ref=reviewer_ref,
            reviewer_decision_value=reviewer_decision_value,
            reviewer_rationale=reviewer_rationale,
        )

    def run_from_inspection_output(
        self,
        source_input: StabilizedInspectionInput,
        inspection_output: InspectionEngineOutput,
        drift_reference: DriftReference | None | object = _UNSET,
        reviewer_decision: ReviewerDecision | None = None,
        reviewer_ref: str = DEFAULT_REVIEWER_REF,
        reviewer_decision_value: ReviewerDecisionValue = (
            ReviewerDecisionValue.INCONCLUSIVE
        ),
        reviewer_rationale: str = DEFAULT_REVIEWER_RATIONALE,
    ) -> EndToEndSubstrateIntegrationResult:
        drift = (
            default_drift_reference()
            if drift_reference is _UNSET
            else drift_reference
        )
        _require_type(
            source_input,
            StabilizedInspectionInput,
            "integration source input must be StabilizedInspectionInput",
        )
        _require_type(
            inspection_output,
            InspectionEngineOutput,
            "integration inspection output must be InspectionEngineOutput",
        )
        raw_result = inspection_output.raw_inspection_result
        _require_type(
            raw_result,
            RawInspectionResult,
            "inspection output must expose RawInspectionResult",
        )

        trust_output = self.trust_engine.qualify(
            raw_result,
            drift_reference=drift,  # type: ignore[arg-type]
        )
        _require_type(
            trust_output,
            TrustQualificationEngineOutput,
            "TrustQualificationEngine.qualify must return canonical output",
        )
        trust_result = trust_output.trust_qualification_result
        _require_type(
            trust_result,
            TrustQualificationResult,
            "trust output must expose TrustQualificationResult",
        )

        review_case: ReviewQualifiedCase | None = None
        human_review_output: HumanReviewEngineOutput | None = None
        if _requires_human_review(trust_result):
            review_case = self.human_review_engine.create_case(
                raw_inspection_result=raw_result,
                trust_qualification_result=trust_result,
            )
            _require_type(
                review_case,
                ReviewQualifiedCase,
                "HumanReviewEngine.create_case must return ReviewQualifiedCase",
            )
            decision = reviewer_decision or deterministic_reviewer_decision(
                review_case=review_case,
                reviewer_ref=reviewer_ref,
                decision=reviewer_decision_value,
                rationale=reviewer_rationale,
            )
            human_review_output = self.human_review_engine.record_decision(
                review_case,
                decision,
            )
            _require_type(
                human_review_output,
                HumanReviewEngineOutput,
                "HumanReviewEngine.record_decision must return canonical output",
            )
            _require_type(
                human_review_output.review_evidence_record,
                ReviewEvidenceRecord,
                "human review output must expose ReviewEvidenceRecord",
            )

        evidence_records = (
            inspection_output.inspection_evidence_record,
            trust_output.trust_qualification_evidence_record,
        )
        if human_review_output is not None:
            evidence_records = (
                *evidence_records,
                human_review_output.review_evidence_record,
            )

        evidence_view = self.evidence_engine.preserve(
            evidence_records,
            expected_stages=(
                EvidenceSourceDomain.INSPECTION,
                EvidenceSourceDomain.TRUST,
                EvidenceSourceDomain.HUMAN_REVIEW,
            ),
        )
        _require_type(
            evidence_view,
            EvidenceView,
            "EvidenceEngine.preserve must return EvidenceView",
        )

        evaluation_report = self.evaluation_engine.evaluate(
            PreservedEvidenceInput(
                evidence_view=evidence_view,
                reference_set_id=self.reference_set_id,
            )
        )
        _require_type(
            evaluation_report,
            EvidenceBackedEvaluationReport,
            "EvaluationEngine.evaluate must return EvidenceBackedEvaluationReport",
        )

        return EndToEndSubstrateIntegrationResult(
            source_input=source_input,
            inspection_output=inspection_output,
            trust_qualification_output=trust_output,
            review_case=review_case,
            human_review_output=human_review_output,
            evidence_view=evidence_view,
            evaluation_report=evaluation_report,
            stage_references=_stage_references(
                source_input=source_input,
                inspection_output=inspection_output,
                trust_output=trust_output,
                review_case=review_case,
                human_review_output=human_review_output,
                evidence_view=evidence_view,
                evaluation_report=evaluation_report,
            ),
        )


def default_stabilized_inspection_input() -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=DEFAULT_INTEGRATION_INPUT_ID,
        artifact_uri=DEFAULT_INTEGRATION_ARTIFACT_URI,
        content_hash=DEFAULT_INTEGRATION_CONTENT_HASH,
    )


def local_provider_fixture_inspection_input() -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=LOCAL_PROVIDER_INTEGRATION_INPUT_ID,
        artifact_uri=LOCAL_PROVIDER_FIXTURE_ARTIFACT_URI,
        content_hash=_sha256_file(_LOCAL_PROVIDER_FIXTURE_PATH),
    )


def default_drift_reference() -> DriftReference:
    return DriftReference(
        reference_id=DEFAULT_DRIFT_REFERENCE_ID,
        available=True,
        drift_score=DEFAULT_DRIFT_SCORE,
    )


def deterministic_reviewer_decision(
    review_case: ReviewQualifiedCase,
    reviewer_ref: str = DEFAULT_REVIEWER_REF,
    decision: ReviewerDecisionValue = ReviewerDecisionValue.INCONCLUSIVE,
    rationale: str = DEFAULT_REVIEWER_RATIONALE,
) -> ReviewerDecision:
    return ReviewerDecision(
        decision_id=_stable_id(
            "deterministic-reviewer-decision",
            {
                "decision": decision.value,
                "rationale": rationale,
                "review_case_id": review_case.review_case_id,
                "reviewer_ref": reviewer_ref,
            },
        ),
        review_case_id=review_case.review_case_id,
        reviewer_ref=reviewer_ref,
        decision=decision,
        rationale=rationale,
    )


def _requires_human_review(trust_result: TrustQualificationResult) -> bool:
    return (
        trust_result.qualified_outcome is QualifiedOutcome.REVIEW
        or trust_result.drift_caution.status is DriftCautionStatus.DRIFTED
    )


def _stage_references(
    source_input: StabilizedInspectionInput,
    inspection_output: InspectionEngineOutput,
    trust_output: TrustQualificationEngineOutput,
    review_case: ReviewQualifiedCase | None,
    human_review_output: HumanReviewEngineOutput | None,
    evidence_view: EvidenceView,
    evaluation_report: EvidenceBackedEvaluationReport,
) -> EndToEndSubstrateStageReferences:
    return EndToEndSubstrateStageReferences(
        source_input_id=source_input.input_id,
        inspection_result_id=(
            inspection_output.raw_inspection_result.inspection_result_id
        ),
        inspection_evidence_record_id=(
            inspection_output.inspection_evidence_record.record_id
        ),
        trust_qualification_result_id=(
            trust_output.trust_qualification_result.qualification_result_id
        ),
        trust_qualification_evidence_record_id=(
            trust_output.trust_qualification_evidence_record.record_id
        ),
        evidence_view_id=evidence_view.view_id,
        evaluation_report_id=evaluation_report.report_id,
        review_case_id=(
            review_case.review_case_id if review_case is not None else None
        ),
        review_evidence_record_id=(
            human_review_output.review_evidence_record.record_id
            if human_review_output is not None
            else None
        ),
        reviewer_decision_id=(
            human_review_output.review_evidence_record.reviewer_decision.decision_id
            if human_review_output is not None
            else None
        ),
    )


def _require_type(value: object, expected_type: type, message: str) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(message)


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"{prefix}:{sha256(canonical.encode('utf-8')).hexdigest()[:32]}"


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
