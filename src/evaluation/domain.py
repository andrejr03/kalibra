from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.evidence import EvidenceView

from .errors import (
    FabricatedEvaluationEvidence,
    InvalidEvaluationReport,
    PrototypePerformanceEvaluationRejected,
    UntraceableEvaluationFinding,
)


EVALUATION_REPORT_KIND = "evidence_backed_evaluation_report"
WEAK_PERFORMANCE_EVIDENCE_KIND = "weak_performance_observation"

_FABRICATION_MARKERS = frozenset({"fabricated", "inferred", "synthetic_claim"})
_PROTOTYPE_PERFORMANCE_MARKERS = frozenset(
    {
        "prototype_visual",
        "synthetic_overlay",
        "prototype_overlay",
        "illustrative_overlay",
    }
)


class EvaluationDimension(str, Enum):
    DETECTION = "detection_quality"
    DETECTION_QUALITY = "detection_quality"
    CALIBRATION = "calibration"
    UNCERTAINTY = "uncertainty_quality"
    UNCERTAINTY_QUALITY = "uncertainty_quality"
    REVIEW = "review_quality"
    REVIEW_QUALITY = "review_quality"
    DRIFT = "drift_response"
    DRIFT_RESPONSE = "drift_response"


class FailureCategory(str, Enum):
    MISSED_DEFECT = "missed_defect"
    FALSE_ALARM = "false_alarm"
    CONFIDENT_ERROR = "confident_error"
    MISPLACED_UNCERTAINTY = "misplaced_uncertainty"
    MISLOCALIZED_DEFECT = "mislocalized_defect"
    UNRESPONSIVE_DRIFT = "unresponsive_drift"


class EvaluationFindingStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    WEAK = "weak_performance"


@dataclass(frozen=True)
class PreservedEvidenceInput:
    evidence_view: EvidenceView
    reference_set_id: str = "fixed-placeholder-reference-set"

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_view, EvidenceView):
            raise InvalidEvaluationReport(
                "evaluation requires an EvidenceView from the Evidence Engine"
            )
        if self.evidence_view.read_only is not True:
            raise InvalidEvaluationReport("evaluation evidence input must be read-only")
        if not self.reference_set_id.strip():
            raise InvalidEvaluationReport("evaluation reference_set_id is required")
        if not self.evidence_view.records and not self.evidence_view.absences:
            raise InvalidEvaluationReport(
                "evaluation requires preserved evidence or explicit absence"
            )


@dataclass(frozen=True)
class DimensionFinding:
    finding_id: str
    dimension: EvaluationDimension
    status: EvaluationFindingStatus
    evidence_refs: tuple[str, ...]
    summary: str
    limitation: str | None = None

    def __post_init__(self) -> None:
        if not self.finding_id.strip():
            raise InvalidEvaluationReport("dimension finding_id is required")
        if not self.summary.strip():
            raise InvalidEvaluationReport("dimension finding summary is required")
        if not self.evidence_refs:
            raise UntraceableEvaluationFinding(
                "dimension findings must reference preserved evidence"
            )
        if self.limitation is not None and not self.limitation.strip():
            raise InvalidEvaluationReport("dimension finding limitation is blank")
        object.__setattr__(self, "dimension", EvaluationDimension(self.dimension))
        object.__setattr__(self, "status", EvaluationFindingStatus(self.status))
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))


@dataclass(frozen=True)
class FailureCategoryFinding:
    finding_id: str
    category: FailureCategory
    status: EvaluationFindingStatus
    evidence_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if not self.finding_id.strip():
            raise InvalidEvaluationReport("failure category finding_id is required")
        if not self.summary.strip():
            raise InvalidEvaluationReport(
                "failure category finding summary is required"
            )
        if not self.evidence_refs:
            raise UntraceableEvaluationFinding(
                "failure category findings must reference preserved evidence"
            )
        object.__setattr__(self, "category", FailureCategory(self.category))
        object.__setattr__(self, "status", EvaluationFindingStatus(self.status))
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))


@dataclass(frozen=True)
class AbsenceDisclosure:
    disclosure_id: str
    dimension_or_category: str
    reason: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.disclosure_id.strip():
            raise InvalidEvaluationReport("absence disclosure_id is required")
        if not self.dimension_or_category.strip():
            raise InvalidEvaluationReport(
                "absence disclosure dimension_or_category is required"
            )
        if not self.reason.strip():
            raise InvalidEvaluationReport("absence disclosure reason is required")
        if not self.evidence_refs:
            raise UntraceableEvaluationFinding(
                "absence disclosures must reference preserved evidence or absence"
            )
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))


@dataclass(frozen=True)
class EvidenceBackedEvaluationReport:
    report_id: str
    dimension_findings: tuple[DimensionFinding, ...]
    failure_category_findings: tuple[FailureCategoryFinding, ...]
    absence_disclosures: tuple[AbsenceDisclosure, ...]
    evidence_refs: tuple[str, ...]
    report_kind: str = EVALUATION_REPORT_KIND
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.report_id.strip():
            raise InvalidEvaluationReport("evaluation report_id is required")
        if self.report_kind != EVALUATION_REPORT_KIND:
            raise InvalidEvaluationReport(
                "evaluation report kind must be evidence-backed"
            )
        if not self.evidence_refs:
            raise InvalidEvaluationReport(
                "evaluation reports must reference preserved evidence"
            )
        _assert_unique_dimensions(self.dimension_findings)
        _assert_unique_categories(self.failure_category_findings)
        report_refs = set(self.evidence_refs)
        for finding in self.dimension_findings:
            if not set(finding.evidence_refs).issubset(report_refs):
                raise UntraceableEvaluationFinding(
                    "dimension finding evidence must be in report evidence refs"
                )
        for finding in self.failure_category_findings:
            if not set(finding.evidence_refs).issubset(report_refs):
                raise UntraceableEvaluationFinding(
                    "failure category evidence must be in report evidence refs"
                )
        for disclosure in self.absence_disclosures:
            if not set(disclosure.evidence_refs).issubset(report_refs):
                raise UntraceableEvaluationFinding(
                    "absence disclosure evidence must be in report evidence refs"
                )
        object.__setattr__(
            self,
            "dimension_findings",
            tuple(self.dimension_findings),
        )
        object.__setattr__(
            self,
            "failure_category_findings",
            tuple(self.failure_category_findings),
        )
        object.__setattr__(
            self,
            "absence_disclosures",
            tuple(self.absence_disclosures),
        )
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def dimension_finding(
    dimension: EvaluationDimension,
    status: EvaluationFindingStatus,
    evidence_refs: tuple[str, ...],
    summary: str,
    limitation: str | None = None,
) -> DimensionFinding:
    canonical_evidence_refs = _sorted_refs(evidence_refs)
    return DimensionFinding(
        finding_id=_stable_id(
            "dimension-finding",
            {
                "dimension": EvaluationDimension(dimension).value,
                "evidence_refs": canonical_evidence_refs,
                "status": EvaluationFindingStatus(status).value,
            },
        ),
        dimension=dimension,
        status=status,
        evidence_refs=canonical_evidence_refs,
        summary=summary,
        limitation=limitation,
    )


def failure_category_finding(
    category: FailureCategory,
    status: EvaluationFindingStatus,
    evidence_refs: tuple[str, ...],
    summary: str,
) -> FailureCategoryFinding:
    canonical_evidence_refs = _sorted_refs(evidence_refs)
    return FailureCategoryFinding(
        finding_id=_stable_id(
            "failure-category-finding",
            {
                "category": FailureCategory(category).value,
                "evidence_refs": canonical_evidence_refs,
                "status": EvaluationFindingStatus(status).value,
            },
        ),
        category=category,
        status=status,
        evidence_refs=canonical_evidence_refs,
        summary=summary,
    )


def absence_disclosure(
    dimension_or_category: EvaluationDimension | FailureCategory | str,
    reason: str,
    evidence_refs: tuple[str, ...],
) -> AbsenceDisclosure:
    target = _target_value(dimension_or_category)
    canonical_evidence_refs = _sorted_refs(evidence_refs)
    return AbsenceDisclosure(
        disclosure_id=_stable_id(
            "absence-disclosure",
            {
                "dimension_or_category": target,
                "evidence_refs": canonical_evidence_refs,
                "reason": reason,
            },
        ),
        dimension_or_category=target,
        reason=reason,
        evidence_refs=canonical_evidence_refs,
    )


def validate_evaluation_evidence_payload(payload: Mapping[str, Any]) -> None:
    flattened = set(_flatten_payload_tokens(payload))
    if flattened & _FABRICATION_MARKERS:
        raise FabricatedEvaluationEvidence(
            "evaluation must not consume fabricated evidence"
        )
    if flattened & _PROTOTYPE_PERFORMANCE_MARKERS:
        raise PrototypePerformanceEvaluationRejected(
            "prototype visuals and synthetic overlays are not performance evidence"
        )


def stable_report_id(payload: Mapping[str, Any]) -> str:
    return _stable_id("evidence-backed-evaluation-report", payload)


def _assert_unique_dimensions(findings: tuple[DimensionFinding, ...]) -> None:
    dimensions = [finding.dimension for finding in findings]
    if len(set(dimensions)) != len(dimensions):
        raise InvalidEvaluationReport(
            "dimension findings must keep dimensions separate"
        )


def _assert_unique_categories(findings: tuple[FailureCategoryFinding, ...]) -> None:
    categories = [finding.category for finding in findings]
    if len(set(categories)) != len(categories):
        raise InvalidEvaluationReport(
            "failure category findings must keep categories separate"
        )


def _target_value(
    target: EvaluationDimension | FailureCategory | str,
) -> str:
    try:
        return EvaluationDimension(target).value
    except ValueError:
        try:
            return FailureCategory(target).value
        except ValueError:
            if not str(target).strip():
                raise InvalidEvaluationReport("absence target is required")
            return str(target)


def _flatten_payload_tokens(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _flatten_payload_tokens(item)
    elif isinstance(value, tuple):
        for item in value:
            yield from _flatten_payload_tokens(item)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_payload_tokens(item)
    elif isinstance(value, str):
        yield value


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"{prefix}:{sha256(canonical.encode('utf-8')).hexdigest()[:32]}"


def _sorted_refs(evidence_refs: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(evidence_refs))
