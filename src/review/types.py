from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from src.trust import QualificationOutcome, TrustQualifiedResult

from .domain import (
    HUMAN_REVIEW_EVIDENCE_KIND,
    HumanReviewEngineOutput,
    ReviewEvidenceRecord,
    ReviewHandoff,
    ReviewQualifiedCase,
    ReviewUpstreamChain,
    ReviewerDecision,
    ReviewerDecisionValue,
)
from .errors import InvalidHumanReviewRequest, InvalidHumanReviewResult


class ReviewStatus(str, Enum):
    REQUESTED = "requested"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    UNABLE_TO_REVIEW = "unable_to_review"


class HumanReviewDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ReviewerIdentity:
    reviewer_id: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.reviewer_id.strip():
            raise InvalidHumanReviewResult("reviewer_id is required")
        if self.display_name is not None and not self.display_name.strip():
            raise InvalidHumanReviewResult("display_name must not be blank")


@dataclass(frozen=True)
class HumanReviewRequest:
    trust_qualified_result: TrustQualifiedResult
    request_id: str
    status: ReviewStatus = ReviewStatus.REQUESTED
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.trust_qualified_result.qualification_outcome is not QualificationOutcome.REVIEW:
            raise InvalidHumanReviewRequest(
                "only review-qualified cases may enter human review"
            )
        if not self.request_id.strip():
            raise InvalidHumanReviewRequest("request_id is required")
        if self.status not in {ReviewStatus.REQUESTED, ReviewStatus.IN_REVIEW}:
            raise InvalidHumanReviewRequest(
                "review requests must be requested or in review"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)


@dataclass(frozen=True)
class HumanReviewResult:
    trust_qualified_result: TrustQualifiedResult
    review_request: HumanReviewRequest
    status: ReviewStatus
    method_id: str
    reviewer_identity: ReviewerIdentity | None = None
    decision: HumanReviewDecision | None = None
    method_version: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.review_request.trust_qualified_result != self.trust_qualified_result:
            raise InvalidHumanReviewResult(
                "human review result must reference the request's trust result"
            )
        if not self.method_id.strip():
            raise InvalidHumanReviewResult("human review method_id is required")
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidHumanReviewResult(
                "human review method_version must not be blank"
            )
        if self.status is ReviewStatus.COMPLETED:
            if self.reviewer_identity is None:
                raise InvalidHumanReviewResult(
                    "completed human review requires reviewer identity"
                )
            if self.decision is None:
                raise InvalidHumanReviewResult(
                    "completed human review requires a decision"
                )
        elif self.status is ReviewStatus.UNABLE_TO_REVIEW:
            if self.decision is not None:
                raise InvalidHumanReviewResult(
                    "unable-to-review results must not include a decision"
                )
        else:
            raise InvalidHumanReviewResult(
                "human review results must be completed or unable to review"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)
