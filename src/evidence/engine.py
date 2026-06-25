from __future__ import annotations

from dataclasses import dataclass

from src.inspection import InspectionResult
from src.review import HumanReviewResult
from src.trust import TrustQualifiedResult

from .errors import InvalidEvidenceResult
from .interfaces import EvidenceMethod
from .types import EvidenceArtifact, EvidenceBundle, EvidenceResult


@dataclass(frozen=True)
class EvidenceEngine:
    method: EvidenceMethod

    def create_bundle(
        self,
        inspection_result: InspectionResult,
        trust_qualified_result: TrustQualifiedResult,
        artifacts: tuple[EvidenceArtifact, ...],
        bundle_id: str,
        human_review_result: HumanReviewResult | None = None,
    ) -> EvidenceBundle:
        return EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_qualified_result,
            artifacts=artifacts,
            bundle_id=bundle_id,
            human_review_result=human_review_result,
        )

    def collect(
        self,
        evidence_bundle: EvidenceBundle,
    ) -> EvidenceResult:
        result = self.method.collect(evidence_bundle)
        if not isinstance(result, EvidenceResult):
            raise InvalidEvidenceResult(
                "evidence methods must return EvidenceResult"
            )
        if result.evidence_bundle is not evidence_bundle:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected bundle"
            )
        if result.inspection_result is not evidence_bundle.inspection_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected inspection result"
            )
        if result.trust_qualified_result is not evidence_bundle.trust_qualified_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected trust result"
            )
        if result.human_review_result is not evidence_bundle.human_review_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected human review result"
            )
        if result.method_id != self.method.method_id:
            raise InvalidEvidenceResult(
                "evidence result method_id must match the method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidEvidenceResult(
                "evidence result method_version must match the method"
            )
        return result
