class InspectionError(Exception):
    """Base error for inspection-domain failures."""


class InvalidInspectionInput(InspectionError):
    """Raised when an input cannot enter the inspection domain."""


class MissingInputIdentity(InvalidInspectionInput):
    """Raised when a stabilized input has no stable identity."""


class MissingContentHash(InvalidInspectionInput):
    """Raised when a stabilized input has no content hash."""


class UnstabilizedInspectionInput(InvalidInspectionInput):
    """Raised when input has not crossed the upstream intake seam."""


class MalformedInspectionInput(InvalidInspectionInput):
    """Raised when the input is not the stabilized input contract."""


class InspectionExaminationFailure(InspectionError):
    """Raised when the placeholder examination cannot complete."""


class InvalidInspectionResult(InspectionError):
    """Raised when the engine cannot form a valid raw result."""


class PartialInspectionResult(InvalidInspectionResult):
    """Raised when a raw result is incomplete or internally inconsistent."""


class InvalidInspectionPrediction(InspectionError):
    """Raised when an inference prediction violates the prediction contract."""


class PartialInspectionPrediction(InvalidInspectionPrediction):
    """Raised when a prediction is incomplete or internally inconsistent."""


class EvidenceEmissionFailure(InspectionError):
    """Raised when the inspection evidence record cannot be emitted."""


class NonReproducibleInspection(InspectionError):
    """Raised when fixed inspection input produces divergent outputs."""
