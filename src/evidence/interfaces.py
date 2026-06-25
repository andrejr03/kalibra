from __future__ import annotations

from typing import Protocol

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

