from __future__ import annotations

from dataclasses import dataclass

from src.evaluation import EvidenceBackedEvaluationReport
from src.evidence import EvidenceView
from src.inspection import InspectionEngineOutput, StabilizedInspectionInput
from src.review import HumanReviewEngineOutput, ReviewQualifiedCase
from src.trust import TrustQualificationEngineOutput


@dataclass(frozen=True)
class EndToEndSubstrateStageReferences:
    source_input_id: str
    inspection_result_id: str
    inspection_evidence_record_id: str
    trust_qualification_result_id: str
    trust_qualification_evidence_record_id: str
    evidence_view_id: str
    evaluation_report_id: str
    review_case_id: str | None = None
    review_evidence_record_id: str | None = None
    reviewer_decision_id: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.source_input_id,
            self.inspection_result_id,
            self.inspection_evidence_record_id,
            self.trust_qualification_result_id,
            self.trust_qualification_evidence_record_id,
            self.evidence_view_id,
            self.evaluation_report_id,
        )
        if any(not value.strip() for value in required):
            raise ValueError("integration stage references require stable ids")

        review_refs = (
            self.review_case_id,
            self.review_evidence_record_id,
            self.reviewer_decision_id,
        )
        if any(value is None for value in review_refs) and any(
            value is not None for value in review_refs
        ):
            raise ValueError(
                "human review stage references must be all present or absent"
            )
        if any(value is not None and not value.strip() for value in review_refs):
            raise ValueError("human review stage references must not be blank")


@dataclass(frozen=True)
class EndToEndSubstrateIntegrationResult:
    source_input: StabilizedInspectionInput
    inspection_output: InspectionEngineOutput
    trust_qualification_output: TrustQualificationEngineOutput
    evidence_view: EvidenceView
    evaluation_report: EvidenceBackedEvaluationReport
    stage_references: EndToEndSubstrateStageReferences
    review_case: ReviewQualifiedCase | None = None
    human_review_output: HumanReviewEngineOutput | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_input, StabilizedInspectionInput):
            raise TypeError("integration source input must be StabilizedInspectionInput")
        if not isinstance(self.inspection_output, InspectionEngineOutput):
            raise TypeError("integration inspection output must be canonical")
        if not isinstance(
            self.trust_qualification_output,
            TrustQualificationEngineOutput,
        ):
            raise TypeError("integration trust output must be canonical")
        if self.review_case is not None and not isinstance(
            self.review_case,
            ReviewQualifiedCase,
        ):
            raise TypeError("integration review case must be canonical")
        if self.human_review_output is not None and not isinstance(
            self.human_review_output,
            HumanReviewEngineOutput,
        ):
            raise TypeError("integration review output must be canonical")
        if not isinstance(self.evidence_view, EvidenceView):
            raise TypeError("integration evidence view must be canonical")
        if not isinstance(self.evaluation_report, EvidenceBackedEvaluationReport):
            raise TypeError("integration evaluation report must be canonical")

        self._validate_chain()
        self._validate_stage_references()

    def _validate_chain(self) -> None:
        raw_result = self.inspection_output.raw_inspection_result
        trust_result = self.trust_qualification_output.trust_qualification_result

        if raw_result.input_id != self.source_input.input_id:
            raise ValueError("inspection output must reference the source input")
        if trust_result.inspection_result_id != raw_result.inspection_result_id:
            raise ValueError("trust output must reference the raw inspection result")
        if trust_result.input_id != raw_result.input_id:
            raise ValueError("trust output must preserve the source input id")

        if (self.review_case is None) != (self.human_review_output is None):
            raise ValueError("review case and review output must appear together")

        if self.review_case is not None and self.human_review_output is not None:
            if self.review_case.raw_inspection_result != raw_result:
                raise ValueError("review case must carry the raw inspection result")
            if self.review_case.trust_qualification_result != trust_result:
                raise ValueError("review case must carry the trust result")
            if (
                self.human_review_output.review_handoff.review_case_id
                != self.review_case.review_case_id
            ):
                raise ValueError("review output must reference the review case")

    def _validate_stage_references(self) -> None:
        raw_result = self.inspection_output.raw_inspection_result
        inspection_record = self.inspection_output.inspection_evidence_record
        trust_result = self.trust_qualification_output.trust_qualification_result
        trust_record = (
            self.trust_qualification_output.trust_qualification_evidence_record
        )

        expected = EndToEndSubstrateStageReferences(
            source_input_id=self.source_input.input_id,
            inspection_result_id=raw_result.inspection_result_id,
            inspection_evidence_record_id=inspection_record.record_id,
            trust_qualification_result_id=trust_result.qualification_result_id,
            trust_qualification_evidence_record_id=trust_record.record_id,
            evidence_view_id=self.evidence_view.view_id,
            evaluation_report_id=self.evaluation_report.report_id,
            review_case_id=(
                self.review_case.review_case_id
                if self.review_case is not None
                else None
            ),
            review_evidence_record_id=(
                self.human_review_output.review_evidence_record.record_id
                if self.human_review_output is not None
                else None
            ),
            reviewer_decision_id=(
                self.human_review_output
                .review_evidence_record
                .reviewer_decision
                .decision_id
                if self.human_review_output is not None
                else None
            ),
        )
        if self.stage_references != expected:
            raise ValueError("integration stage references must match emitted outputs")
