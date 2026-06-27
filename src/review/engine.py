from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

from src.inspection import RawInspectionResult
from src.trust import TrustQualificationResult, TrustQualifiedResult

from .domain import (
    HumanReviewEngineOutput,
    ReviewEvidenceRecord,
    ReviewHandoff,
    ReviewQualifiedCase,
    ReviewUpstreamChain,
    ReviewerDecision,
)
from .errors import (
    HumanReviewError,
    IncompleteReviewChain,
    InvalidHumanReviewResult,
    NonReproducibleHumanReview,
    ReviewEvidenceEmissionFailure,
    UpstreamReviewMutationError,
)
from .interfaces import HumanReviewEvidenceEmitterProtocol, HumanReviewMethod
from .types import HumanReviewRequest, HumanReviewResult


@dataclass(frozen=True)
class HumanReviewEvidenceEmitter:
    emitter_id: str = "human-review-evidence-emitter-v1"

    def emit(
        self,
        review_handoff: ReviewHandoff,
        reviewer_decision: ReviewerDecision,
    ) -> ReviewEvidenceRecord:
        upstream_chain = ReviewUpstreamChain(
            input_id=review_handoff.source_input_ref,
            inspection_result_id=(
                review_handoff.raw_inspection_result.inspection_result_id
            ),
            qualification_result_id=(
                review_handoff.trust_qualification_result.qualification_result_id
            ),
            review_case_id=review_handoff.review_case_id,
        )
        record_id = _stable_id(
            "human-review-evidence-record",
            {
                "decision_id": reviewer_decision.decision_id,
                "emitter_id": self.emitter_id,
                "qualification_result_id": upstream_chain.qualification_result_id,
                "review_case_id": review_handoff.review_case_id,
            },
        )
        return ReviewEvidenceRecord(
            record_id=record_id,
            review_case_id=review_handoff.review_case_id,
            review_handoff=review_handoff,
            reviewer_decision=reviewer_decision,
            upstream_chain=upstream_chain,
        )


@dataclass(frozen=True)
class HumanReviewEngine:
    method: HumanReviewMethod | None = None
    evidence_emitter: HumanReviewEvidenceEmitterProtocol = field(
        default_factory=HumanReviewEvidenceEmitter
    )

    def create_case(
        self,
        raw_inspection_result: RawInspectionResult,
        trust_qualification_result: TrustQualificationResult,
        review_case_id: str | None = None,
    ) -> ReviewQualifiedCase:
        case_id = review_case_id or _stable_id(
            "review-qualified-case",
            {
                "inspection_result_id": (
                    raw_inspection_result.inspection_result_id
                ),
                "qualification_result_id": (
                    trust_qualification_result.qualification_result_id
                ),
            },
        )
        return ReviewQualifiedCase(
            review_case_id=case_id,
            qualification_result_id=(
                trust_qualification_result.qualification_result_id
            ),
            inspection_result_id=raw_inspection_result.inspection_result_id,
            input_id=raw_inspection_result.input_id,
            raw_inspection_result=raw_inspection_result,
            trust_qualification_result=trust_qualification_result,
            deferral_reason=_deferral_reason(trust_qualification_result),
            localization_ref=raw_inspection_result.localization,
        )

    def prepare_handoff(self, review_case: ReviewQualifiedCase) -> ReviewHandoff:
        self._validate_case_chain(review_case)
        return ReviewHandoff(
            review_case_id=review_case.review_case_id,
            source_input_ref=review_case.input_id,
            localization_ref=review_case.localization_ref,
            raw_inspection_result=review_case.raw_inspection_result,
            trust_qualification_result=review_case.trust_qualification_result,
            deferral_reason=review_case.deferral_reason,
        )

    def record_decision(
        self,
        review_case: ReviewQualifiedCase,
        reviewer_decision: ReviewerDecision,
    ) -> HumanReviewEngineOutput:
        if reviewer_decision.review_case_id != review_case.review_case_id:
            raise InvalidHumanReviewResult(
                "reviewer decision must reference exactly one review case"
            )
        raw_before = deepcopy(review_case.raw_inspection_result)
        trust_before = deepcopy(review_case.trust_qualification_result)

        first_output = self._record_once(review_case, reviewer_decision)
        self._guard_upstream_unchanged(review_case, raw_before, trust_before)

        second_output = self._record_once(review_case, reviewer_decision)
        self._guard_upstream_unchanged(review_case, raw_before, trust_before)

        if first_output != second_output:
            raise NonReproducibleHumanReview(
                "fixed review inputs produced divergent records"
            )
        return first_output

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
        if self.method is None:
            raise InvalidHumanReviewResult(
                "legacy human review requests require a human review method"
            )
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

    def _record_once(
        self,
        review_case: ReviewQualifiedCase,
        reviewer_decision: ReviewerDecision,
    ) -> HumanReviewEngineOutput:
        handoff = self.prepare_handoff(review_case)
        record = self._emit_evidence(handoff, reviewer_decision)
        return HumanReviewEngineOutput(
            review_handoff=handoff,
            review_evidence_record=record,
        )

    def _emit_evidence(
        self,
        handoff: ReviewHandoff,
        reviewer_decision: ReviewerDecision,
    ) -> ReviewEvidenceRecord:
        try:
            record = self.evidence_emitter.emit(handoff, reviewer_decision)
        except ReviewEvidenceEmissionFailure:
            raise
        except HumanReviewError:
            raise
        except Exception as exc:
            raise ReviewEvidenceEmissionFailure(
                "human review evidence emission failed"
            ) from exc
        if not isinstance(record, ReviewEvidenceRecord):
            raise ReviewEvidenceEmissionFailure(
                "human review evidence emission must return ReviewEvidenceRecord"
            )
        if record.review_handoff != handoff:
            raise ReviewEvidenceEmissionFailure(
                "human review evidence must preserve the handoff"
            )
        if record.reviewer_decision != reviewer_decision:
            raise ReviewEvidenceEmissionFailure(
                "human review evidence must preserve the reviewer decision"
            )
        return record

    def _validate_case_chain(self, review_case: ReviewQualifiedCase) -> None:
        if not isinstance(review_case, ReviewQualifiedCase):
            raise IncompleteReviewChain(
                "human review requires ReviewQualifiedCase"
            )
        if review_case.raw_inspection_result.input_id != review_case.input_id:
            raise IncompleteReviewChain(
                "review case raw result must reference the source input"
            )
        if (
            review_case.trust_qualification_result.inspection_result_id
            != review_case.raw_inspection_result.inspection_result_id
        ):
            raise IncompleteReviewChain(
                "review case trust qualification must reference raw result"
            )

    def _guard_upstream_unchanged(
        self,
        review_case: ReviewQualifiedCase,
        raw_before: RawInspectionResult,
        trust_before: TrustQualificationResult,
    ) -> None:
        if review_case.raw_inspection_result != raw_before:
            raise UpstreamReviewMutationError(
                "human review must not mutate raw inspection results"
            )
        if review_case.trust_qualification_result != trust_before:
            raise UpstreamReviewMutationError(
                "human review must not mutate trust qualification results"
            )


def _deferral_reason(trust_result: TrustQualificationResult) -> str:
    parts = [f"qualified_outcome={trust_result.qualified_outcome.value}"]
    parts.append(
        f"uncertainty={trust_result.uncertainty_characterization.status.value}"
    )
    if trust_result.drift_caution.caution_applied:
        parts.append(f"drift={trust_result.drift_caution.status.value}")
    return ";".join(parts)


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
