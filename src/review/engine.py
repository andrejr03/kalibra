from __future__ import annotations

from dataclasses import dataclass

from src.trust import TrustQualifiedResult

from .errors import InvalidHumanReviewResult
from .interfaces import HumanReviewMethod
from .types import HumanReviewRequest, HumanReviewResult


@dataclass(frozen=True)
class HumanReviewEngine:
    method: HumanReviewMethod

    def create_request(
        self,
        trust_qualified_result: TrustQualifiedResult,
        request_id: str,
    ) -> HumanReviewRequest:
        return HumanReviewRequest(
            trust_qualified_result=trust_qualified_result,
            request_id=request_id,
        )

    def review(
        self,
        trust_qualified_result: TrustQualifiedResult,
        request_id: str,
    ) -> HumanReviewResult:
        return self.review_request(
            self.create_request(
                trust_qualified_result=trust_qualified_result,
                request_id=request_id,
            )
        )

    def review_request(self, review_request: HumanReviewRequest) -> HumanReviewResult:
        result = self.method.review(review_request)
        if not isinstance(result, HumanReviewResult):
            raise InvalidHumanReviewResult(
                "human review methods must return HumanReviewResult"
            )
        if result.review_request != review_request:
            raise InvalidHumanReviewResult(
                "human review result must reference the reviewed request"
            )
        if result.trust_qualified_result != review_request.trust_qualified_result:
            raise InvalidHumanReviewResult(
                "human review result must reference the reviewed trust result"
            )
        if result.method_id != self.method.method_id:
            raise InvalidHumanReviewResult(
                "human review result method_id must match the method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidHumanReviewResult(
                "human review result method_version must match the method"
            )
        return result

