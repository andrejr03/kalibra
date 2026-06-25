from __future__ import annotations

from typing import Protocol

from src.inspection import InspectionResult

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

