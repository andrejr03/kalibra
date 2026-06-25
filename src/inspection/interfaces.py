from __future__ import annotations

from typing import Protocol

from .types import InspectionInput, InspectionResult


class InspectionMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def inspect(self, inspection_input: InspectionInput) -> InspectionResult:
        ...

