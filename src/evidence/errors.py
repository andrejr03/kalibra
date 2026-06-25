class EvidenceError(Exception):
    """Base error for evidence-domain failures."""


class InvalidEvidenceBundle(EvidenceError):
    """Raised when evidence inputs or references are inconsistent."""


class InvalidEvidenceResult(EvidenceError):
    """Raised when an evidence method returns invalid output."""

