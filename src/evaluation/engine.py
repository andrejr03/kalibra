from __future__ import annotations

from dataclasses import fields, is_dataclass
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from src.evidence import (
    PERFORMANCE_EVIDENCE_KIND,
    EvidenceSourceDomain,
    EvidenceView,
    EvidenceResult,
)

from .domain import (
    EVALUATION_REPORT_KIND,
    WEAK_PERFORMANCE_EVIDENCE_KIND,
    AbsenceDisclosure,
    DimensionFinding,
    EvaluationDimension,
    EvaluationFindingStatus,
    EvidenceBackedEvaluationReport,
    FailureCategory,
    FailureCategoryFinding,
    PreservedEvidenceInput,
    absence_disclosure,
    dimension_finding,
    failure_category_finding,
    stable_report_id,
    validate_evaluation_evidence_payload,
)
from .errors import (
    FabricatedEvaluationEvidence,
    InvalidEvaluationResult,
    NonReproducibleEvaluation,
    PrototypePerformanceEvaluationRejected,
)
from .interfaces import EvaluationMethod
from .types import EvaluationResult


@dataclass(frozen=True)
class EvaluationEngine:
    method: EvaluationMethod | None = None

    def evaluate(
        self,
        evidence_input: EvidenceResult | EvidenceView | PreservedEvidenceInput,
    ) -> EvaluationResult | EvidenceBackedEvaluationReport:
        if isinstance(evidence_input, EvidenceResult):
            return self._evaluate_legacy(evidence_input)
        if isinstance(evidence_input, EvidenceView):
            return self._evaluate_preserved(
                PreservedEvidenceInput(evidence_view=evidence_input)
            )
        if isinstance(evidence_input, PreservedEvidenceInput):
            return self._evaluate_preserved(evidence_input)
        raise InvalidEvaluationResult(
            "evaluation requires preserved evidence or legacy EvidenceResult"
        )

    def _evaluate_legacy(self, evidence_result: EvidenceResult) -> EvaluationResult:
        if self.method is None:
            raise InvalidEvaluationResult(
                "legacy evidence results require an evaluation method"
            )
        result = self.method.evaluate(evidence_result)
        if not isinstance(result, EvaluationResult):
            raise InvalidEvaluationResult(
                "evaluation methods must return EvaluationResult"
            )
        if result.evidence_result is not evidence_result:
            raise InvalidEvaluationResult(
                "evaluation result must reference the evaluated evidence result"
            )
        if result.evaluation_report.evidence_result is not evidence_result:
            raise InvalidEvaluationResult(
                "evaluation report must reference the evaluated evidence result"
            )
        if result.method_id != self.method.method_id:
            raise InvalidEvaluationResult(
                "evaluation result method_id must match the method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidEvaluationResult(
                "evaluation result method_version must match the method"
            )
        return result

    def _evaluate_preserved(
        self,
        evidence_input: PreservedEvidenceInput,
    ) -> EvidenceBackedEvaluationReport:
        evidence_before = _evidence_signature(evidence_input.evidence_view)
        first_report = self._evaluate_preserved_once(evidence_input)
        _guard_evidence_unchanged(evidence_input.evidence_view, evidence_before)

        second_report = self._evaluate_preserved_once(evidence_input)
        _guard_evidence_unchanged(evidence_input.evidence_view, evidence_before)

        if first_report != second_report:
            raise NonReproducibleEvaluation(
                "fixed preserved evidence produced divergent evaluation reports"
            )
        return first_report

    def _evaluate_preserved_once(
        self,
        evidence_input: PreservedEvidenceInput,
    ) -> EvidenceBackedEvaluationReport:
        evidence_view = evidence_input.evidence_view
        _validate_evidence_view(evidence_view)

        evidence_refs = _report_evidence_refs(evidence_view)
        weak_by_dimension, weak_by_category = _weak_performance_refs(evidence_view)
        dimension_findings = _dimension_findings(
            evidence_view,
            weak_by_dimension,
        )
        failure_findings = _failure_category_findings(weak_by_category)
        absences = _absence_disclosures(
            evidence_view=evidence_view,
            dimension_findings=dimension_findings,
            failure_findings=failure_findings,
            weak_by_dimension=weak_by_dimension,
            weak_by_category=weak_by_category,
            fallback_refs=evidence_refs,
        )
        return EvidenceBackedEvaluationReport(
            report_id=stable_report_id(
                {
                    "absence_disclosures": [
                        disclosure.disclosure_id for disclosure in absences
                    ],
                    "dimension_findings": [
                        finding.finding_id for finding in dimension_findings
                    ],
                    "failure_category_findings": [
                        finding.finding_id for finding in failure_findings
                    ],
                    "reference_set_id": evidence_input.reference_set_id,
                    "view_id": evidence_view.view_id,
                }
            ),
            dimension_findings=dimension_findings,
            failure_category_findings=failure_findings,
            absence_disclosures=absences,
            evidence_refs=evidence_refs,
            report_kind=EVALUATION_REPORT_KIND,
            metadata={
                "evaluation_mode": "deterministic_placeholder_substrate",
                "reference_set_id": evidence_input.reference_set_id,
            },
        )


def _validate_evidence_view(evidence_view: EvidenceView) -> None:
    for record in evidence_view.records:
        validate_evaluation_evidence_payload(record.payload)
        if record.evidence_kind == PERFORMANCE_EVIDENCE_KIND:
            flattened = set(_flatten_tokens(record.payload))
            if flattened & {
                "prototype_visual",
                "synthetic_overlay",
                "prototype_overlay",
                "illustrative_overlay",
            }:
                raise PrototypePerformanceEvaluationRejected(
                    "prototype visuals are not performance evidence"
                )
    if any(
        token in {"fabricated", "inferred", "synthetic_claim"}
        for token in _flatten_tokens(_canonical(evidence_view))
    ):
        raise FabricatedEvaluationEvidence(
            "evaluation must not consume fabricated evidence"
        )


def _dimension_findings(
    evidence_view: EvidenceView,
    weak_by_dimension: Mapping[EvaluationDimension, tuple[str, ...]],
) -> tuple[DimensionFinding, ...]:
    findings: list[DimensionFinding] = []
    for dimension in _DIMENSION_ORDER:
        if dimension in weak_by_dimension:
            findings.append(
                dimension_finding(
                    dimension=dimension,
                    status=EvaluationFindingStatus.WEAK,
                    evidence_refs=weak_by_dimension[dimension],
                    summary=(
                        f"Explicit weak-performance evidence is present for "
                        f"{dimension.value}; no aggregate score is produced."
                    ),
                    limitation=(
                        "Placeholder evaluation reports weakness only where "
                        "weak-performance evidence is explicit."
                    ),
                )
            )
            continue
        refs = _dimension_evidence_refs(evidence_view, dimension)
        if refs:
            findings.append(
                dimension_finding(
                    dimension=dimension,
                    status=EvaluationFindingStatus.SUPPORTED,
                    evidence_refs=refs,
                    summary=(
                        f"Preserved {dimension.value} evidence supports a "
                        "structural placeholder finding; no benchmark claim is made."
                    ),
                    limitation=(
                        "This substrate validates traceability and separation, "
                        "not final evaluation quality."
                    ),
                )
            )
    return tuple(findings)


def _failure_category_findings(
    weak_by_category: Mapping[FailureCategory, tuple[str, ...]],
) -> tuple[FailureCategoryFinding, ...]:
    findings = []
    for category in _FAILURE_CATEGORY_ORDER:
        refs = weak_by_category.get(category)
        if refs:
            findings.append(
                failure_category_finding(
                    category=category,
                    status=EvaluationFindingStatus.WEAK,
                    evidence_refs=refs,
                    summary=(
                        f"Explicit weak-performance evidence names "
                        f"{category.value}; it remains separate from other categories."
                    ),
                )
            )
    return tuple(findings)


def _absence_disclosures(
    evidence_view: EvidenceView,
    dimension_findings: tuple[DimensionFinding, ...],
    failure_findings: tuple[FailureCategoryFinding, ...],
    weak_by_dimension: Mapping[EvaluationDimension, tuple[str, ...]],
    weak_by_category: Mapping[FailureCategory, tuple[str, ...]],
    fallback_refs: tuple[str, ...],
) -> tuple[AbsenceDisclosure, ...]:
    disclosures: list[AbsenceDisclosure] = []
    dimensions_with_findings = {finding.dimension for finding in dimension_findings}
    categories_with_findings = {finding.category for finding in failure_findings}

    for dimension in _DIMENSION_ORDER:
        if dimension in dimensions_with_findings or dimension in weak_by_dimension:
            continue
        refs = _absence_refs_for_dimension(evidence_view, dimension) or fallback_refs
        disclosures.append(
            absence_disclosure(
                dimension_or_category=dimension,
                reason=f"{dimension.value}_evidence_missing",
                evidence_refs=refs,
            )
        )

    for category in _FAILURE_CATEGORY_ORDER:
        if category in categories_with_findings or category in weak_by_category:
            continue
        disclosures.append(
            absence_disclosure(
                dimension_or_category=category,
                reason=f"{category.value}_evidence_missing",
                evidence_refs=fallback_refs,
            )
        )
    return tuple(disclosures)


def _dimension_evidence_refs(
    evidence_view: EvidenceView,
    dimension: EvaluationDimension,
) -> tuple[str, ...]:
    if dimension is EvaluationDimension.DETECTION:
        return _record_refs(evidence_view, EvidenceSourceDomain.INSPECTION)
    if dimension in {
        EvaluationDimension.CALIBRATION,
        EvaluationDimension.UNCERTAINTY,
    }:
        return _record_refs(evidence_view, EvidenceSourceDomain.TRUST)
    if dimension is EvaluationDimension.REVIEW:
        return _record_refs(evidence_view, EvidenceSourceDomain.HUMAN_REVIEW)
    if dimension is EvaluationDimension.DRIFT:
        trust_refs = []
        for record in evidence_view.records:
            if record.source_domain is not EvidenceSourceDomain.TRUST:
                continue
            qualification = record.payload.get("trust_qualification_result", {})
            drift = qualification.get("drift_caution", {})
            if drift.get("status") != "unavailable":
                trust_refs.append(record.preserved_record_id)
        return tuple(trust_refs)
    return ()


def _absence_refs_for_dimension(
    evidence_view: EvidenceView,
    dimension: EvaluationDimension,
) -> tuple[str, ...]:
    if dimension is EvaluationDimension.REVIEW:
        refs = tuple(
            absence.absence_id
            for absence in evidence_view.absences
            if absence.expected_stage == EvidenceSourceDomain.HUMAN_REVIEW.value
        )
        if refs:
            return refs
    if dimension is EvaluationDimension.DRIFT:
        trust_refs = _record_refs(evidence_view, EvidenceSourceDomain.TRUST)
        if trust_refs:
            return trust_refs
    return tuple(absence.absence_id for absence in evidence_view.absences)


def _record_refs(
    evidence_view: EvidenceView,
    source_domain: EvidenceSourceDomain,
) -> tuple[str, ...]:
    return tuple(
        record.preserved_record_id
        for record in evidence_view.records
        if record.source_domain is source_domain
    )


def _weak_performance_refs(
    evidence_view: EvidenceView,
) -> tuple[
    dict[EvaluationDimension, tuple[str, ...]],
    dict[FailureCategory, tuple[str, ...]],
]:
    by_dimension: dict[EvaluationDimension, list[str]] = {}
    by_category: dict[FailureCategory, list[str]] = {}
    for record in evidence_view.records:
        payload = record.payload
        is_weak_record = (
            record.evidence_kind == WEAK_PERFORMANCE_EVIDENCE_KIND
            or payload.get("weak_performance") is True
        )
        if not is_weak_record:
            continue
        dimension = payload.get("dimension")
        if dimension is not None:
            by_dimension.setdefault(
                EvaluationDimension(dimension),
                [],
            ).append(record.preserved_record_id)
        category = payload.get("failure_category")
        if category is not None:
            by_category.setdefault(
                FailureCategory(category),
                [],
            ).append(record.preserved_record_id)
    return (
        {dimension: tuple(refs) for dimension, refs in by_dimension.items()},
        {category: tuple(refs) for category, refs in by_category.items()},
    )


def _report_evidence_refs(evidence_view: EvidenceView) -> tuple[str, ...]:
    refs = [
        record.preserved_record_id for record in evidence_view.records
    ]
    refs.extend(absence.absence_id for absence in evidence_view.absences)
    return tuple(sorted(refs))


def _guard_evidence_unchanged(
    evidence_view: EvidenceView,
    evidence_before: str,
) -> None:
    if _evidence_signature(evidence_view) != evidence_before:
        raise InvalidEvaluationResult(
            "evaluation must not mutate preserved evidence"
        )


def _evidence_signature(evidence_view: EvidenceView) -> str:
    return json.dumps(
        _canonical(evidence_view),
        sort_keys=True,
        separators=(",", ":"),
    )


def _canonical(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, MappingProxyType):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_canonical(item) for item in value)
    if isinstance(value, list):
        return tuple(_canonical(item) for item in value)
    return value


def _flatten_tokens(value: Any):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _flatten_tokens(item)
    elif isinstance(value, tuple):
        for item in value:
            yield from _flatten_tokens(item)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_tokens(item)
    elif isinstance(value, str):
        yield value


_DIMENSION_ORDER = (
    EvaluationDimension.DETECTION,
    EvaluationDimension.CALIBRATION,
    EvaluationDimension.UNCERTAINTY,
    EvaluationDimension.REVIEW,
    EvaluationDimension.DRIFT,
)

_FAILURE_CATEGORY_ORDER = (
    FailureCategory.MISSED_DEFECT,
    FailureCategory.FALSE_ALARM,
    FailureCategory.CONFIDENT_ERROR,
    FailureCategory.MISPLACED_UNCERTAINTY,
    FailureCategory.MISLOCALIZED_DEFECT,
    FailureCategory.UNRESPONSIVE_DRIFT,
)
