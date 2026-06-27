class EvidenceError(Exception):
    """Base error for evidence-domain failures."""


class InvalidEvidenceBundle(EvidenceError):
    """Raised when evidence inputs or references are inconsistent."""


class InvalidEvidenceResult(EvidenceError):
    """Raised when an evidence method returns invalid output."""


class MalformedInboundEvidenceRecord(EvidenceError):
    """Raised when an inbound evidence record is incomplete or malformed."""


class EvidencePreservationFailure(EvidenceError):
    """Raised when evidence cannot be faithfully preserved."""


class EvidenceLinkingFailure(EvidenceError):
    """Raised when preserved evidence cannot be linked immutably."""


class EvidenceAbsenceFailure(EvidenceError):
    """Raised when evidence absence cannot be recorded explicitly."""


class EvidenceViewFailure(EvidenceError):
    """Raised when an inspectable evidence view would violate its contract."""


class FabricatedEvidenceRecord(EvidenceError):
    """Raised when a record is fabricated instead of emitted upstream."""


class PrototypePerformanceEvidenceRejected(EvidenceError):
    """Raised when illustrative prototype assets are offered as performance evidence."""


class NonReproducibleEvidencePreservation(EvidenceError):
    """Raised when fixed evidence inputs produce divergent preserved views."""


class UnauthorizedUpstreamRerun(EvidenceError):
    """Raised when evidence handling attempts to re-run upstream domains."""
