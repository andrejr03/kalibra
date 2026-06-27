from __future__ import annotations

from typing import Protocol

from .domain import ReviewEvidenceRecord, ReviewHandoff, ReviewerDecision
from .types import HumanReviewRequest, HumanReviewResult


class HumanReviewMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def review(self, review_request: HumanReviewRequest) -> HumanReviewResult:
        ...


class HumanReviewEvidenceEmitterProtocol(Protocol):
    def emit(
        self,
        review_handoff: ReviewHandoff,
        reviewer_decision: ReviewerDecision,
    ) -> ReviewEvidenceRecord:
        ...
