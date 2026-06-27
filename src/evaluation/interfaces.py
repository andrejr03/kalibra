from __future__ import annotations

from typing import Protocol

from src.evidence import EvidenceResult, EvidenceView

from .domain import EvidenceBackedEvaluationReport
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


class EvidenceBackedEvaluator(Protocol):
    def evaluate(
        self,
        evidence_view: EvidenceView,
    ) -> EvidenceBackedEvaluationReport:
        ...
