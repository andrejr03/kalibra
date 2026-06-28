from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.inspection import DefectLocalization, RawInspectionResult
from src.trust import DriftCautionStatus, QualifiedOutcome, TrustQualificationResult

from .errors import (
    IncompleteReviewChain,
    InvalidHumanReviewResult,
    MalformedReviewerDecision,
    NonReviewQualifiedCase,
)


HUMAN_REVIEW_EVIDENCE_KIND = "human_review_decision"


class ReviewerDecisionValue(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ReviewQualifiedCase:
    review_case_id: str
    qualification_result_id: str
    inspection_result_id: str
    input_id: str
    raw_inspection_result: RawInspectionResult
    trust_qualification_result: TrustQualificationResult
    deferral_reason: str
    localization_ref: DefectLocalization | None = None

    def __post_init__(self) -> None:
        if not self.review_case_id.strip():
            raise IncompleteReviewChain("review_case_id is required")
        if not self.qualification_result_id.strip():
            raise IncompleteReviewChain("qualification_result_id is required")
        if not self.inspection_result_id.strip():
            raise IncompleteReviewChain("inspection_result_id is required")
        if not self.input_id.strip():
            raise IncompleteReviewChain("input_id is required")
        if not self.deferral_reason.strip():
            raise IncompleteReviewChain("deferral reason is required")
        if (
            self.raw_inspection_result.inspection_result_id
            != self.inspection_result_id
        ):
            raise IncompleteReviewChain(
                "review case must carry the referenced raw inspection result"
            )
        if self.raw_inspection_result.input_id != self.input_id:
            raise IncompleteReviewChain(
                "review case input_id must match the raw inspection result"
            )
        if (
            self.trust_qualification_result.qualification_result_id
            != self.qualification_result_id
        ):
            raise IncompleteReviewChain(
                "review case must carry the referenced trust qualification"
            )
        if (
            self.trust_qualification_result.inspection_result_id
            != self.inspection_result_id
        ):
            raise IncompleteReviewChain(
                "trust qualification must reference the raw inspection result"
            )
        if self.trust_qualification_result.input_id != self.input_id:
            raise IncompleteReviewChain(
                "trust qualification input_id must match the review case"
            )
        is_review = (
            self.trust_qualification_result.qualified_outcome
            is QualifiedOutcome.REVIEW
        )
        is_drifted = (
            self.trust_qualification_result.drift_caution.status
            is DriftCautionStatus.DRIFTED
        )
        if not (is_review or is_drifted):
            raise NonReviewQualifiedCase(
                "only review-qualified or drifted cases may enter human review"
            )


@dataclass(frozen=True)
class ReviewerDecision:
    decision_id: str
    review_case_id: str
    reviewer_ref: str
    decision: ReviewerDecisionValue
    rationale: str

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise MalformedReviewerDecision("reviewer decision_id is required")
        if not self.review_case_id.strip():
            raise MalformedReviewerDecision("review_case_id is required")
        if not self.reviewer_ref.strip():
            raise MalformedReviewerDecision("reviewer_ref is required")
        if not isinstance(self.decision, ReviewerDecisionValue):
            raise MalformedReviewerDecision(
                "reviewer decision must use ReviewerDecisionValue"
            )
        if not self.rationale.strip():
            raise MalformedReviewerDecision("reviewer rationale is required")


@dataclass(frozen=True)
class ReviewHandoff:
    review_case_id: str
    source_input_ref: str
    localization_ref: DefectLocalization | None
    raw_inspection_result: RawInspectionResult
    trust_qualification_result: TrustQualificationResult
    deferral_reason: str

    def __post_init__(self) -> None:
        if not self.review_case_id.strip():
            raise InvalidHumanReviewResult("handoff review_case_id is required")
        if not self.source_input_ref.strip():
            raise InvalidHumanReviewResult("handoff source_input_ref is required")
        if not self.deferral_reason.strip():
            raise InvalidHumanReviewResult("handoff deferral reason is required")
        if not isinstance(self.raw_inspection_result, RawInspectionResult):
            raise InvalidHumanReviewResult(
                "handoff raw_inspection_result is required"
            )
        if not isinstance(
            self.trust_qualification_result,
            TrustQualificationResult,
        ):
            raise InvalidHumanReviewResult(
                "handoff trust_qualification_result is required"
            )
        if not self.trust_qualification_result.qualification_result_id.strip():
            raise InvalidHumanReviewResult(
                "handoff trust qualification result id is required"
            )
        if self.raw_inspection_result.input_id != self.source_input_ref:
            raise InvalidHumanReviewResult(
                "handoff source input must match raw inspection result"
            )
        if self.trust_qualification_result.input_id != self.source_input_ref:
            raise InvalidHumanReviewResult(
                "handoff source input must match trust qualification result"
            )
        if (
            self.trust_qualification_result.inspection_result_id
            != self.raw_inspection_result.inspection_result_id
        ):
            raise InvalidHumanReviewResult(
                "handoff trust qualification must match raw inspection result"
            )


@dataclass(frozen=True)
class ReviewUpstreamChain:
    input_id: str
    inspection_result_id: str
    qualification_result_id: str
    review_case_id: str

    def __post_init__(self) -> None:
        if not self.input_id.strip():
            raise InvalidHumanReviewResult("upstream chain input_id is required")
        if not self.inspection_result_id.strip():
            raise InvalidHumanReviewResult(
                "upstream chain inspection_result_id is required"
            )
        if not self.qualification_result_id.strip():
            raise InvalidHumanReviewResult(
                "upstream chain qualification_result_id is required"
            )
        if not self.review_case_id.strip():
            raise InvalidHumanReviewResult(
                "upstream chain review_case_id is required"
            )


@dataclass(frozen=True)
class ReviewEvidenceRecord:
    record_id: str
    review_case_id: str
    review_handoff: ReviewHandoff
    reviewer_decision: ReviewerDecision
    upstream_chain: ReviewUpstreamChain
    evidence_kind: str = HUMAN_REVIEW_EVIDENCE_KIND

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise InvalidHumanReviewResult("review evidence record_id is required")
        if self.evidence_kind != HUMAN_REVIEW_EVIDENCE_KIND:
            raise InvalidHumanReviewResult(
                "review evidence must preserve human review decisions"
            )
        if self.review_case_id != self.review_handoff.review_case_id:
            raise InvalidHumanReviewResult(
                "review evidence must link to the handoff"
            )
        if self.review_case_id != self.reviewer_decision.review_case_id:
            raise InvalidHumanReviewResult(
                "review evidence must link to the reviewer decision"
            )
        if self.review_case_id != self.upstream_chain.review_case_id:
            raise InvalidHumanReviewResult(
                "review evidence must link to the upstream chain"
            )


@dataclass(frozen=True)
class HumanReviewEngineOutput:
    review_handoff: ReviewHandoff
    review_evidence_record: ReviewEvidenceRecord

    def __post_init__(self) -> None:
        if self.review_evidence_record.review_handoff != self.review_handoff:
            raise InvalidHumanReviewResult(
                "human review output evidence must preserve the handoff"
            )
