from __future__ import annotations

from typing import Protocol

from src.inspection import InspectionResult, RawInspectionResult

from .domain import CalibratedTrustConfidence, TrustQualificationEvidenceRecord
from .domain import TrustQualificationResult

from .types import TrustQualifiedResult


class TrustQualificationMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def qualify(self, inspection_result: InspectionResult) -> TrustQualifiedResult:
        ...


class TrustCalibrationMethod(Protocol):
    def calibrate(
        self, raw_result: RawInspectionResult
    ) -> CalibratedTrustConfidence:
        ...


class TrustQualificationEvidenceEmitterProtocol(Protocol):
    def emit(
        self,
        raw_result: RawInspectionResult,
        qualification: TrustQualificationResult,
    ) -> TrustQualificationEvidenceRecord:
        ...
