class EvaluationError(Exception):
    """Base error for evaluation-domain failures."""


class InvalidEvaluationReport(EvaluationError):
    """Raised when an evaluation report is inconsistent."""


class InvalidEvaluationResult(EvaluationError):
    """Raised when an evaluation method returns invalid output."""


class MalformedPreservedEvidenceInput(EvaluationError):
    """Raised when preserved evidence cannot be consumed by evaluation."""


class UntraceableEvaluationFinding(EvaluationError):
    """Raised when an evaluation finding cannot be tied to preserved evidence."""


class FabricatedEvaluationEvidence(EvaluationError):
    """Raised when evaluation input attempts to fabricate evidence."""


class PrototypePerformanceEvaluationRejected(EvaluationError):
    """Raised when prototype visuals are offered as performance evidence."""


class EvidenceMutationAttempt(EvaluationError):
    """Raised when evaluation would mutate preserved evidence."""


class NonReproducibleEvaluation(EvaluationError):
    """Raised when fixed evidence produces divergent evaluation reports."""
