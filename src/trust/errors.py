class TrustQualificationError(Exception):
    """Base error for trust-qualification domain failures."""


class InvalidTrustQualificationResult(TrustQualificationError):
    """Raised when a trust qualification method returns invalid output."""

