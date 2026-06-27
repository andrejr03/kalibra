from __future__ import annotations

from typing import Protocol

from .domain import EvidenceView, InboundEvidenceRecord
from .types import EvidenceBundle, EvidenceResult


class EvidenceMethod(Protocol):
    @property
    def method_id(self) -> str:
        ...

    @property
    def method_version(self) -> str | None:
        ...

    def collect(self, evidence_bundle: EvidenceBundle) -> EvidenceResult:
        ...


class EvidencePreserver(Protocol):
    def preserve(
        self,
        evidence_records: tuple[InboundEvidenceRecord, ...],
    ) -> EvidenceView:
        ...
