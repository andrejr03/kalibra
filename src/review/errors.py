class HumanReviewError(Exception):
    """Base error for human-review domain failures."""


class InvalidHumanReviewRequest(HumanReviewError):
    """Raised when a case cannot enter the human-review boundary."""


class InvalidHumanReviewResult(HumanReviewError):
    """Raised when a human review method returns invalid output."""


class NonReviewQualifiedCase(HumanReviewError):
    """Raised when a case was not qualified for human review."""


class IncompleteReviewChain(HumanReviewError):
    """Raised when a review case is missing upstream artifacts."""


class MalformedReviewerDecision(HumanReviewError):
    """Raised when a reviewer decision cannot be recorded."""


class UpstreamReviewMutationError(HumanReviewError):
    """Raised when review handling mutates upstream records."""


class ReviewEvidenceEmissionFailure(HumanReviewError):
    """Raised when a human review evidence record cannot be emitted."""


class NonReproducibleHumanReview(HumanReviewError):
    """Raised when fixed review inputs produce divergent records."""
