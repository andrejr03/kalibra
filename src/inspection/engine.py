from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .errors import InvalidInspectionResult
from .input import InputPreparer
from .interfaces import InspectionMethod
from .types import InspectionInput, InspectionResult


@dataclass(frozen=True)
class InspectionEngine:
    method: InspectionMethod
    input_preparer: InputPreparer = field(default_factory=InputPreparer)

    def inspect_path(
        self, source_path: str | Path, media_type: str | None = None
    ) -> InspectionResult:
        inspection_input = self.input_preparer.prepare_path(source_path, media_type)
        return self.inspect(inspection_input)

    def inspect(self, inspection_input: InspectionInput) -> InspectionResult:
        result = self.method.inspect(inspection_input)
        if not isinstance(result, InspectionResult):
            raise InvalidInspectionResult(
                "inspection methods must return InspectionResult"
            )
        if result.inspection_input != inspection_input:
            raise InvalidInspectionResult(
                "inspection result must reference the inspected input"
            )
        if result.method_id != self.method.method_id:
            raise InvalidInspectionResult(
                "inspection result method_id must match the inspection method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidInspectionResult(
                "inspection result method_version must match the inspection method"
            )
        return result

