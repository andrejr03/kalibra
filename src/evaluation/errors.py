class EvaluationError(Exception):
    """Base error for evaluation-domain failures."""


class InvalidEvaluationReport(EvaluationError):
    """Raised when an evaluation report is inconsistent."""


class InvalidEvaluationResult(EvaluationError):
    """Raised when an evaluation method returns invalid output."""
