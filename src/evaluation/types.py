from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from src.evidence import EvidenceResult

from .errors import InvalidEvaluationReport, InvalidEvaluationResult


class EvaluationDimension(str, Enum):
    DETECTION_QUALITY = "detection_quality"
    CALIBRATION = "calibration"
    UNCERTAINTY_QUALITY = "uncertainty_quality"
    REVIEW_QUALITY = "review_quality"
    DRIFT_RESPONSE = "drift_response"


class FailureCategory(str, Enum):
    MISSED_DEFECT = "missed_defect"
    FALSE_ALARM = "false_alarm"
    CONFIDENT_ERROR = "confident_error"
    MISPLACED_UNCERTAINTY = "misplaced_uncertainty"
    MISLOCALIZED_DEFECT = "mislocalized_defect"
    UNRESPONSIVE_DRIFT = "unresponsive_drift"


class EvaluationStatus(str, Enum):
    NOT_EVALUATED = "not_evaluated"
    EVIDENCE_INCOMPLETE = "evidence_incomplete"
    REPORTED = "reported"


@dataclass(frozen=True)
class EvaluationFinding:
    dimension: EvaluationDimension
    status: EvaluationStatus
    summary: str
    failure_category: FailureCategory | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise InvalidEvaluationReport("evaluation finding summary is required")
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)


@dataclass(frozen=True)
class EvaluationReport:
    evidence_result: EvidenceResult
    findings: tuple[EvaluationFinding, ...]
    status: EvaluationStatus
    report_id: str
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.report_id.strip():
            raise InvalidEvaluationReport("evaluation report_id is required")
        if not self.findings:
            raise InvalidEvaluationReport("evaluation report requires findings")
        dimensions = {finding.dimension for finding in self.findings}
        if len(dimensions) != len(self.findings):
            raise InvalidEvaluationReport(
                "evaluation report findings must not duplicate dimensions"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)


@dataclass(frozen=True)
class EvaluationResult:
    evidence_result: EvidenceResult
    evaluation_report: EvaluationReport
    method_id: str
    method_version: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise InvalidEvaluationResult("evaluation method_id is required")
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidEvaluationResult(
                "evaluation method_version must not be blank"
            )
        if self.evaluation_report.evidence_result is not self.evidence_result:
            raise InvalidEvaluationResult(
                "evaluation result must reference the report evidence result"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)
