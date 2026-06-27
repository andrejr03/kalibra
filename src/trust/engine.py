from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import json
from math import isfinite
from typing import Any

from src.inspection import InspectionResult, InspectionJudgement, RawInspectionResult

from .domain import (
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
    validate_raw_inspection_result,
)
from .errors import (
    CalibrationFailure,
    InvalidTrustQualificationResult,
    NonReproducibleTrustQualification,
    RawInspectionMutationError,
    TrustEvidenceEmissionFailure,
)
from .interfaces import (
    TrustCalibrationMethod,
    TrustQualificationEvidenceEmitterProtocol,
    TrustQualificationMethod,
)
from .types import TrustQualifiedResult


@dataclass(frozen=True)
class DeterministicPlaceholderCalibrator:
    calibrator_id: str = "trust-placeholder-calibrator-v1"

    def calibrate(
        self, raw_result: RawInspectionResult
    ) -> CalibratedTrustConfidence:
        raw_measure = raw_result.raw_anomaly_measure
        if not isfinite(raw_measure):
            raise CalibrationFailure("raw anomaly measure must be finite")
        normalized_distance_from_boundary = min(
            1.0,
            max(0.0, abs(raw_measure - 50.0) / 50.0),
        )
        return CalibratedTrustConfidence(
            value=round(normalized_distance_from_boundary, 6)
        )


@dataclass(frozen=True)
class TrustQualificationEvidenceEmitter:
    emitter_id: str = "trust-qualification-evidence-emitter-v1"

    def emit(
        self,
        raw_result: RawInspectionResult,
        qualification: TrustQualificationResult,
    ) -> TrustQualificationEvidenceRecord:
        record_id = _stable_id(
            "trust-qualification-evidence-record",
            {
                "emitter_id": self.emitter_id,
                "inspection_result_id": raw_result.inspection_result_id,
                "qualification_result_id": qualification.qualification_result_id,
            },
        )
        return TrustQualificationEvidenceRecord(
            record_id=record_id,
            qualification_result_id=qualification.qualification_result_id,
            inspection_result_id=raw_result.inspection_result_id,
            raw_inspection_result=raw_result,
            trust_qualification_result=qualification,
        )


@dataclass(frozen=True)
class TrustQualificationEngine:
    method: TrustQualificationMethod | None = None
    calibrator: TrustCalibrationMethod = field(
        default_factory=DeterministicPlaceholderCalibrator
    )
    evidence_emitter: TrustQualificationEvidenceEmitterProtocol = field(
        default_factory=TrustQualificationEvidenceEmitter
    )

    def qualify(
        self,
        inspection_result: RawInspectionResult | InspectionResult,
        drift_reference: DriftReference | None = None,
    ) -> TrustQualificationEngineOutput | TrustQualifiedResult:
        if isinstance(inspection_result, RawInspectionResult):
            return self._qualify_raw(inspection_result, drift_reference)
        if isinstance(inspection_result, InspectionResult):
            return self._qualify_legacy(inspection_result)
        validate_raw_inspection_result(inspection_result)  # type: ignore[arg-type]
        raise AssertionError("unreachable")

    def _qualify_legacy(
        self, inspection_result: InspectionResult
    ) -> TrustQualifiedResult:
        if self.method is None:
            raise InvalidTrustQualificationResult(
                "legacy inspection results require a trust qualification method"
            )
        result = self.method.qualify(inspection_result)
        if not isinstance(result, TrustQualifiedResult):
            raise InvalidTrustQualificationResult(
                "trust qualification methods must return TrustQualifiedResult"
            )
        if result.inspection_result != inspection_result:
            raise InvalidTrustQualificationResult(
                "trust qualification result must reference the qualified inspection"
            )
        if result.method_id != self.method.method_id:
            raise InvalidTrustQualificationResult(
                "trust qualification result method_id must match the method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidTrustQualificationResult(
                "trust qualification result method_version must match the method"
            )
        return result

    def _qualify_raw(
        self,
        raw_result: RawInspectionResult,
        drift_reference: DriftReference | None = None,
    ) -> TrustQualificationEngineOutput:
        validate_raw_inspection_result(raw_result)
        raw_before = deepcopy(raw_result)

        first_output = self._qualify_raw_once(raw_result, drift_reference)
        self._guard_raw_unchanged(raw_result, raw_before)

        second_output = self._qualify_raw_once(raw_result, drift_reference)
        self._guard_raw_unchanged(raw_result, raw_before)

        if first_output != second_output:
            raise NonReproducibleTrustQualification(
                "fixed trust qualification inputs produced divergent outputs"
            )
        return first_output

    def _qualify_raw_once(
        self,
        raw_result: RawInspectionResult,
        drift_reference: DriftReference | None,
    ) -> TrustQualificationEngineOutput:
        confidence = self._calibrate(raw_result)
        drift_caution = self._assess_drift(drift_reference)
        uncertainty = _uncertainty_for_confidence(confidence)
        qualified_outcome = _qualified_outcome(
            raw_result=raw_result,
            confidence=confidence,
            drift_caution=drift_caution,
        )
        qualification = self._assemble_result(
            raw_result=raw_result,
            confidence=confidence,
            uncertainty=uncertainty,
            drift_caution=drift_caution,
            qualified_outcome=qualified_outcome,
        )
        evidence_record = self._emit_evidence(raw_result, qualification)
        return TrustQualificationEngineOutput(
            trust_qualification_result=qualification,
            trust_qualification_evidence_record=evidence_record,
        )

    def _calibrate(
        self, raw_result: RawInspectionResult
    ) -> CalibratedTrustConfidence:
        try:
            confidence = self.calibrator.calibrate(raw_result)
        except CalibrationFailure:
            raise
        except Exception as exc:
            raise CalibrationFailure(
                "placeholder trust calibration failed"
            ) from exc
        if not isinstance(confidence, CalibratedTrustConfidence):
            raise CalibrationFailure(
                "trust calibration must return CalibratedTrustConfidence"
            )
        return confidence

    def _assess_drift(
        self, drift_reference: DriftReference | None
    ) -> DriftCaution:
        if drift_reference is None or not drift_reference.available:
            return DriftCaution(status=DriftCautionStatus.UNAVAILABLE)
        score = drift_reference.drift_score
        if score is None:
            return DriftCaution(status=DriftCautionStatus.UNAVAILABLE)
        status = (
            DriftCautionStatus.DRIFTED
            if score >= 0.6
            else DriftCautionStatus.IN_DISTRIBUTION
        )
        return DriftCaution(
            status=status,
            drift_reference_id=drift_reference.reference_id,
            drift_score=score,
            caution_applied=status is DriftCautionStatus.DRIFTED,
            absence_reason=None,
        )

    def _assemble_result(
        self,
        raw_result: RawInspectionResult,
        confidence: CalibratedTrustConfidence,
        uncertainty: UncertaintyCharacterization,
        drift_caution: DriftCaution,
        qualified_outcome: QualifiedOutcome,
    ) -> TrustQualificationResult:
        qualification_id = _stable_id(
            "trust-qualification-result",
            {
                "confidence": confidence.value,
                "drift_status": drift_caution.status.value,
                "input_id": raw_result.input_id,
                "inspection_result_id": raw_result.inspection_result_id,
                "outcome": qualified_outcome.value,
                "uncertainty": uncertainty.status.value,
            },
        )
        return TrustQualificationResult(
            qualification_result_id=qualification_id,
            inspection_result_id=raw_result.inspection_result_id,
            input_id=raw_result.input_id,
            calibrated_confidence=confidence,
            qualified_outcome=qualified_outcome,
            uncertainty_characterization=uncertainty,
            drift_caution=drift_caution,
            raw_inspection_result_ref=raw_result.inspection_result_id,
        )

    def _emit_evidence(
        self,
        raw_result: RawInspectionResult,
        qualification: TrustQualificationResult,
    ) -> TrustQualificationEvidenceRecord:
        try:
            record = self.evidence_emitter.emit(raw_result, qualification)
        except TrustEvidenceEmissionFailure:
            raise
        except Exception as exc:
            raise TrustEvidenceEmissionFailure(
                "trust qualification evidence emission failed"
            ) from exc
        if not isinstance(record, TrustQualificationEvidenceRecord):
            raise TrustEvidenceEmissionFailure(
                "trust evidence emission must return TrustQualificationEvidenceRecord"
            )
        if record.raw_inspection_result != raw_result:
            raise TrustEvidenceEmissionFailure(
                "trust evidence record must preserve the raw result"
            )
        if record.trust_qualification_result != qualification:
            raise TrustEvidenceEmissionFailure(
                "trust evidence record must preserve the qualification"
            )
        return record

    def _guard_raw_unchanged(
        self,
        raw_result: RawInspectionResult,
        raw_before: RawInspectionResult,
    ) -> None:
        if raw_result != raw_before:
            raise RawInspectionMutationError(
                "trust qualification must not mutate raw inspection results"
            )


def _uncertainty_for_confidence(
    confidence: CalibratedTrustConfidence,
) -> UncertaintyCharacterization:
    if confidence.value >= 0.75:
        return UncertaintyCharacterization(
            status=UncertaintyStatus.LOW,
            rationale="Placeholder confidence is far from the decision boundary.",
        )
    if confidence.value >= 0.15:
        return UncertaintyCharacterization(
            status=UncertaintyStatus.ELEVATED,
            rationale="Placeholder confidence is near the decision boundary.",
        )
    return UncertaintyCharacterization(
        status=UncertaintyStatus.HIGH,
        rationale="Placeholder confidence is too close to the decision boundary.",
    )


def _qualified_outcome(
    raw_result: RawInspectionResult,
    confidence: CalibratedTrustConfidence,
    drift_caution: DriftCaution,
) -> QualifiedOutcome:
    if confidence.value < 0.15:
        return QualifiedOutcome.ABSTAIN
    if confidence.value < 0.4:
        return QualifiedOutcome.REVIEW

    base_outcome = (
        QualifiedOutcome.REJECT
        if raw_result.judgement is InspectionJudgement.DEFECT
        else QualifiedOutcome.ACCEPT
    )
    if (
        drift_caution.status is DriftCautionStatus.DRIFTED
        and base_outcome in {QualifiedOutcome.ACCEPT, QualifiedOutcome.REJECT}
    ):
        return QualifiedOutcome.REVIEW
    return base_outcome


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
