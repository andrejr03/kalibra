from __future__ import annotations

from typing import Protocol

from src.evidence import EvidenceResult

from .types import EvaluationResult


class EvaluationMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def evaluate(self, evidence_result: EvidenceResult) -> EvaluationResult:
        ...
