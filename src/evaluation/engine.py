from __future__ import annotations

from dataclasses import dataclass

from src.evidence import EvidenceResult

from .errors import InvalidEvaluationResult
from .interfaces import EvaluationMethod
from .types import EvaluationResult


@dataclass(frozen=True)
class EvaluationEngine:
    method: EvaluationMethod

    def evaluate(self, evidence_result: EvidenceResult) -> EvaluationResult:
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
