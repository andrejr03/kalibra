from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from src.inspection import RAW_MEASURE_KIND, RawInspectionResult

from .errors import InvalidTrustQualificationResult, MalformedRawInspectionResult


CONFIDENCE_KIND = "calibrated_confidence"
DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND = (
    "deterministic_rule_based_trust_baseline_v1"
)
PLACEHOLDER_CALIBRATION_KIND = "deterministic_placeholder_calibration"
VALID_CALIBRATION_KINDS = frozenset(
    {
        DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND,
        PLACEHOLDER_CALIBRATION_KIND,
    }
)
DRIFT_UNAVAILABLE = "drift_reference_unavailable"
TRUST_EVIDENCE_KIND = "trust_qualification_result"


class QualifiedOutcome(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    REVIEW = "review"
    ABSTAIN = "abstain"


class UncertaintyStatus(str, Enum):
    LOW = "low_uncertainty"
    ELEVATED = "elevated_uncertainty"
    HIGH = "high_uncertainty"


class DriftCautionStatus(str, Enum):
    UNAVAILABLE = "unavailable"
    IN_DISTRIBUTION = "in_distribution"
    DRIFTED = "drifted"


@dataclass(frozen=True)
class CalibratedTrustConfidence:
    value: float
    confidence_kind: str = CONFIDENCE_KIND
    calibration_kind: str = DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND
    source_raw_measure_kind: str = RAW_MEASURE_KIND

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise InvalidTrustQualificationResult(
                "calibrated confidence must be finite"
            )
        if not 0.0 <= self.value <= 1.0:
            raise InvalidTrustQualificationResult(
                "calibrated confidence must be bounded between 0 and 1"
            )
        if self.confidence_kind != CONFIDENCE_KIND:
            raise InvalidTrustQualificationResult(
                "confidence must be explicitly marked as calibrated"
            )
        if self.calibration_kind not in VALID_CALIBRATION_KINDS:
            raise InvalidTrustQualificationResult(
                "calibration kind must be explicit"
            )
        if self.source_raw_measure_kind != RAW_MEASURE_KIND:
            raise InvalidTrustQualificationResult(
                "confidence must record the raw measure source kind"
            )


@dataclass(frozen=True)
class UncertaintyCharacterization:
    status: UncertaintyStatus
    rationale: str

    def __post_init__(self) -> None:
        if not self.rationale.strip():
            raise InvalidTrustQualificationResult(
                "uncertainty characterization rationale is required"
            )


@dataclass(frozen=True)
class DriftReference:
    reference_id: str
    available: bool
    drift_score: float | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.reference_id.strip():
            raise InvalidTrustQualificationResult("drift reference_id is required")
        if not self.available and self.drift_score is not None:
            raise InvalidTrustQualificationResult(
                "unavailable drift references must not carry a drift score"
            )
        if self.drift_score is not None:
            if not isfinite(self.drift_score):
                raise InvalidTrustQualificationResult(
                    "drift reference score must be finite"
                )
            if not 0.0 <= self.drift_score <= 1.0:
                raise InvalidTrustQualificationResult(
                    "drift reference score must be bounded between 0 and 1"
                )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class DriftCaution:
    status: DriftCautionStatus
    drift_reference_id: str | None = None
    drift_score: float | None = None
    caution_applied: bool = False
    absence_reason: str | None = DRIFT_UNAVAILABLE

    def __post_init__(self) -> None:
        if self.status is DriftCautionStatus.UNAVAILABLE:
            if self.drift_reference_id is not None:
                raise InvalidTrustQualificationResult(
                    "unavailable drift caution must not reference drift data"
                )
            if self.drift_score is not None:
                raise InvalidTrustQualificationResult(
                    "unavailable drift caution must not carry a score"
                )
            if not self.absence_reason:
                raise InvalidTrustQualificationResult(
                    "missing drift reference requires an absence disclosure"
                )
            if self.caution_applied:
                raise InvalidTrustQualificationResult(
                    "unavailable drift reference cannot apply drift caution"
                )
        else:
            if not self.drift_reference_id:
                raise InvalidTrustQualificationResult(
                    "available drift caution requires a drift reference"
                )
            if self.drift_score is None or not isfinite(self.drift_score):
                raise InvalidTrustQualificationResult(
                    "available drift caution requires a finite score"
                )
            if self.absence_reason is not None:
                raise InvalidTrustQualificationResult(
                    "available drift caution must not include absence reason"
                )


@dataclass(frozen=True)
class TrustQualificationResult:
    qualification_result_id: str
    inspection_result_id: str
    input_id: str
    calibrated_confidence: CalibratedTrustConfidence
    qualified_outcome: QualifiedOutcome
    uncertainty_characterization: UncertaintyCharacterization
    drift_caution: DriftCaution
    raw_inspection_result_ref: str
    confidence_kind: str = CONFIDENCE_KIND

    def __post_init__(self) -> None:
        if not self.qualification_result_id.strip():
            raise InvalidTrustQualificationResult(
                "qualification_result_id is required"
            )
        if not self.inspection_result_id.strip():
            raise InvalidTrustQualificationResult(
                "qualification requires inspection_result_id"
            )
        if not self.input_id.strip():
            raise InvalidTrustQualificationResult(
                "qualification requires originating input_id"
            )
        if self.raw_inspection_result_ref != self.inspection_result_id:
            raise InvalidTrustQualificationResult(
                "qualification must reference the raw inspection result"
            )
        if self.confidence_kind != CONFIDENCE_KIND:
            raise InvalidTrustQualificationResult(
                "qualification confidence must be explicitly calibrated"
            )
        if self.confidence_kind != self.calibrated_confidence.confidence_kind:
            raise InvalidTrustQualificationResult(
                "qualification confidence markers must agree"
            )


@dataclass(frozen=True)
class TrustQualificationEvidenceRecord:
    record_id: str
    qualification_result_id: str
    inspection_result_id: str
    raw_inspection_result: RawInspectionResult
    trust_qualification_result: TrustQualificationResult
    evidence_kind: str = TRUST_EVIDENCE_KIND

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise InvalidTrustQualificationResult(
                "trust qualification evidence record_id is required"
            )
        if self.evidence_kind != TRUST_EVIDENCE_KIND:
            raise InvalidTrustQualificationResult(
                "trust evidence must preserve trust qualification results"
            )
        if self.inspection_result_id != self.raw_inspection_result.inspection_result_id:
            raise InvalidTrustQualificationResult(
                "trust evidence must link to the raw inspection result"
            )
        if (
            self.qualification_result_id
            != self.trust_qualification_result.qualification_result_id
        ):
            raise InvalidTrustQualificationResult(
                "trust evidence must link to the qualification result"
            )
        if (
            self.trust_qualification_result.inspection_result_id
            != self.raw_inspection_result.inspection_result_id
        ):
            raise InvalidTrustQualificationResult(
                "qualification must reference the preserved raw result"
            )


@dataclass(frozen=True)
class TrustQualificationEngineOutput:
    trust_qualification_result: TrustQualificationResult
    trust_qualification_evidence_record: TrustQualificationEvidenceRecord

    def __post_init__(self) -> None:
        result = self.trust_qualification_result
        record = self.trust_qualification_evidence_record
        if record.trust_qualification_result != result:
            raise InvalidTrustQualificationResult(
                "trust output evidence must preserve the qualification"
            )
        if record.qualification_result_id != result.qualification_result_id:
            raise InvalidTrustQualificationResult(
                "trust output evidence must link to the qualification"
            )


def validate_raw_inspection_result(raw_result: RawInspectionResult) -> None:
    if not isinstance(raw_result, RawInspectionResult):
        raise MalformedRawInspectionResult(
            "trust qualification requires RawInspectionResult"
        )
    if not raw_result.input_id.strip():
        raise MalformedRawInspectionResult(
            "raw inspection result requires originating input_id"
        )
    if not raw_result.inspection_result_id.strip():
        raise MalformedRawInspectionResult(
            "raw inspection result requires inspection_result_id"
        )
    if raw_result.raw_measure_kind != RAW_MEASURE_KIND:
        raise MalformedRawInspectionResult(
            "raw inspection result must expose a raw anomaly measure"
        )
    if not isfinite(raw_result.raw_anomaly_measure):
        raise MalformedRawInspectionResult(
            "raw inspection result raw anomaly measure must be finite"
        )
