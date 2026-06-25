class HumanReviewError(Exception):
    """Base error for human-review domain failures."""


class InvalidHumanReviewRequest(HumanReviewError):
    """Raised when a case cannot enter the human-review boundary."""


class InvalidHumanReviewResult(HumanReviewError):
    """Raised when a human review method returns invalid output."""

