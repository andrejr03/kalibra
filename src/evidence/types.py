from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from src.inspection import InspectionResult
from src.review import HumanReviewResult
from src.trust import TrustQualifiedResult

from .domain import (
    EvidenceAbsenceMarker,
    EvidenceChainLink,
    EvidenceRecordLink,
    EvidenceSourceDomain,
    EvidenceView,
    InboundEvidenceRecord,
    PreservedEvidenceRecord,
)
from .errors import InvalidEvidenceBundle, InvalidEvidenceResult


class EvidenceStatus(str, Enum):
    PRESENT = "present"
    INCOMPLETE = "incomplete"
    MISSING = "missing"


class EvidenceDomain(str, Enum):
    INSPECTION = "inspection"
    TRUST = "trust"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class EvidenceReference:
    domain: EvidenceDomain
    reference_id: str

    def __post_init__(self) -> None:
        if not self.reference_id.strip():
            raise InvalidEvidenceBundle("evidence reference_id is required")


@dataclass(frozen=True)
class EvidenceArtifact:
    artifact_id: str
    reference: EvidenceReference
    status: EvidenceStatus
    description: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.artifact_id.strip():
            raise InvalidEvidenceBundle("evidence artifact_id is required")
        if self.description is not None and not self.description.strip():
            raise InvalidEvidenceBundle("evidence description must not be blank")
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)


@dataclass(frozen=True)
class EvidenceBundle:
    inspection_result: InspectionResult
    trust_qualified_result: TrustQualifiedResult
    artifacts: tuple[EvidenceArtifact, ...]
    bundle_id: str
    human_review_result: HumanReviewResult | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.bundle_id.strip():
            raise InvalidEvidenceBundle("evidence bundle_id is required")
        if self.trust_qualified_result.inspection_result is not self.inspection_result:
            raise InvalidEvidenceBundle(
                "trust result must reference the bundled inspection result"
            )
        if self.human_review_result is not None:
            if (
                self.human_review_result.trust_qualified_result
                is not self.trust_qualified_result
            ):
                raise InvalidEvidenceBundle(
                    "human review result must reference the bundled trust result"
                )
        if not self.artifacts:
            raise InvalidEvidenceBundle("evidence bundle requires artifacts")
        expected = self.reference_ids
        seen_domains: set[EvidenceDomain] = set()
        for artifact in self.artifacts:
            expected_reference = expected.get(artifact.reference.domain)
            if expected_reference is None:
                raise InvalidEvidenceBundle(
                    "evidence artifact references a domain result that is absent"
                )
            if artifact.reference.reference_id != expected_reference:
                raise InvalidEvidenceBundle(
                    "evidence artifact references an unknown domain result"
                )
            seen_domains.add(artifact.reference.domain)
        required_domains = {EvidenceDomain.INSPECTION, EvidenceDomain.TRUST}
        if self.human_review_result is not None:
            required_domains.add(EvidenceDomain.HUMAN_REVIEW)
        missing_domains = required_domains - seen_domains
        if missing_domains:
            raise InvalidEvidenceBundle(
                "evidence bundle must reference every completed domain output"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)

    @property
    def reference_ids(self) -> Mapping[EvidenceDomain, str]:
        reference_ids = {
            EvidenceDomain.INSPECTION: self.inspection_result.inspection_input.input_id,
            EvidenceDomain.TRUST: (
                f"{self.trust_qualified_result.method_id}:"
                f"{self.trust_qualified_result.inspection_result.inspection_input.input_id}"
            ),
        }
        if self.human_review_result is not None:
            reference_ids[EvidenceDomain.HUMAN_REVIEW] = (
                f"{self.human_review_result.method_id}:"
                f"{self.human_review_result.review_request.request_id}"
            )
        return MappingProxyType(reference_ids)


@dataclass(frozen=True)
class EvidenceResult:
    inspection_result: InspectionResult
    trust_qualified_result: TrustQualifiedResult
    evidence_bundle: EvidenceBundle
    method_id: str
    human_review_result: HumanReviewResult | None = None
    method_version: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise InvalidEvidenceResult("evidence method_id is required")
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidEvidenceResult("evidence method_version must not be blank")
        if self.evidence_bundle.inspection_result is not self.inspection_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the bundled inspection result"
            )
        if self.evidence_bundle.trust_qualified_result is not self.trust_qualified_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the bundled trust result"
            )
        if self.evidence_bundle.human_review_result is not self.human_review_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the bundled human review result"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)
