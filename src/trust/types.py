from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from src.inspection import InspectionResult

from .domain import (
    CONFIDENCE_KIND,
    DRIFT_UNAVAILABLE,
    PLACEHOLDER_CALIBRATION_KIND,
    TRUST_EVIDENCE_KIND,
    CalibratedTrustConfidence,
    DriftCaution,
    DriftCautionStatus,
    DriftReference,
    QualifiedOutcome,
    TrustQualificationEngineOutput,
    TrustQualificationEvidenceRecord,
    TrustQualificationResult,
    UncertaintyCharacterization,
    UncertaintyStatus,
)
from .errors import InvalidTrustQualificationResult


class QualificationOutcome(str, Enum):
    ACCEPT = "accept"
    REVIEW = "review"
    REJECT = "reject"


class AbstentionStatus(str, Enum):
    NOT_ABSTAINED = "not_abstained"
    ABSTAINED = "abstained"


class DriftAssessmentStatus(str, Enum):
    NOT_ASSESSED = "not_assessed"
    IN_DISTRIBUTION = "in_distribution"
    DRIFTED = "drifted"


@dataclass(frozen=True)
class CalibratedConfidence:
    value: float
    method_id: str
    method_version: str | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise InvalidTrustQualificationResult(
                "calibrated confidence must be finite"
            )
        if not 0.0 <= self.value <= 1.0:
            raise InvalidTrustQualificationResult(
                "calibrated confidence must be bounded between 0 and 1"
            )
        if not self.method_id.strip():
            raise InvalidTrustQualificationResult(
                "calibrated confidence method_id is required"
            )
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidTrustQualificationResult(
                "calibrated confidence method_version must not be blank"
            )


@dataclass(frozen=True)
class DriftAssessment:
    status: DriftAssessmentStatus
    method_id: str
    method_version: str | None = None
    score: float | None = None

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise InvalidTrustQualificationResult(
                "drift assessment method_id is required"
            )
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidTrustQualificationResult(
                "drift assessment method_version must not be blank"
            )
        if self.score is not None and not isfinite(self.score):
            raise InvalidTrustQualificationResult("drift assessment score must be finite")


@dataclass(frozen=True)
class TrustQualifiedResult:
    inspection_result: InspectionResult
    calibrated_confidence: CalibratedConfidence
    qualification_outcome: QualificationOutcome
    abstention_status: AbstentionStatus
    drift_assessment: DriftAssessment
    method_id: str
    method_version: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise InvalidTrustQualificationResult(
                "trust qualification method_id is required"
            )
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidTrustQualificationResult(
                "trust qualification method_version must not be blank"
            )
        if (
            self.abstention_status is AbstentionStatus.ABSTAINED
            and self.qualification_outcome is not QualificationOutcome.REVIEW
        ):
            raise InvalidTrustQualificationResult(
                "abstained qualifications must use the review outcome"
            )
        if (
            self.drift_assessment.status is DriftAssessmentStatus.DRIFTED
            and self.qualification_outcome is not QualificationOutcome.REVIEW
        ):
            raise InvalidTrustQualificationResult(
                "drifted qualifications must use the review outcome"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)
