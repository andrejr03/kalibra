from __future__ import annotations

from typing import Protocol

from .domain import (
    InspectionEvidenceRecord,
    PlaceholderExamination,
    RawInspectionResult,
    StabilizedInspectionInput,
)


class InspectionExaminer(Protocol):
    def examine(
        self, inspection_input: StabilizedInspectionInput
    ) -> PlaceholderExamination:
        ...


class InspectionEvidenceEmitterProtocol(Protocol):
    def emit(self, raw_result: RawInspectionResult) -> InspectionEvidenceRecord:
        ...
