from __future__ import annotations

from dataclasses import dataclass

from src.inspection import InspectionResult

from .errors import InvalidTrustQualificationResult
from .interfaces import TrustQualificationMethod
from .types import TrustQualifiedResult


@dataclass(frozen=True)
class TrustQualificationEngine:
    method: TrustQualificationMethod

    def qualify(self, inspection_result: InspectionResult) -> TrustQualifiedResult:
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

