class InspectionError(Exception):
    """Base error for inspection-domain failures."""


class InvalidInspectionInput(InspectionError):
    """Raised when an input cannot enter the inspection domain."""


class InvalidInspectionResult(InspectionError):
    """Raised when an inspection method returns an invalid domain result."""

