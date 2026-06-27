class TrustQualificationError(Exception):
    """Base error for trust-qualification domain failures."""


class InvalidTrustQualificationResult(TrustQualificationError):
    """Raised when a trust qualification method returns invalid output."""


class MalformedRawInspectionResult(TrustQualificationError):
    """Raised when the upstream raw inspection result is malformed."""


class UntraceableRawInspectionResult(MalformedRawInspectionResult):
    """Raised when a raw inspection result cannot be traced upstream."""


class CalibrationFailure(TrustQualificationError):
    """Raised when placeholder calibration cannot be applied."""


class RawInspectionMutationError(TrustQualificationError):
    """Raised when qualification mutates the raw inspection result."""


class TrustEvidenceEmissionFailure(TrustQualificationError):
    """Raised when trust qualification evidence cannot be emitted."""


class NonReproducibleTrustQualification(TrustQualificationError):
    """Raised when fixed qualification inputs produce divergent outputs."""
