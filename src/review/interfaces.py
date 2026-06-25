from __future__ import annotations

from typing import Protocol

from .types import HumanReviewRequest, HumanReviewResult


class HumanReviewMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def review(self, review_request: HumanReviewRequest) -> HumanReviewResult:
        ...

