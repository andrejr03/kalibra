from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .errors import (
    EvidenceAbsenceFailure,
    EvidenceLinkingFailure,
    EvidenceViewFailure,
    FabricatedEvidenceRecord,
    MalformedInboundEvidenceRecord,
    PrototypePerformanceEvidenceRejected,
)


PERFORMANCE_EVIDENCE_KIND = "performance_evidence"

_FABRICATED_MARKERS = frozenset({"fabricated", "inferred", "synthetic_claim"})
_PROTOTYPE_MARKERS = frozenset(
    {
        "prototype_visual",
        "synthetic_overlay",
        "prototype_overlay",
        "illustrative_overlay",
    }
)


class EvidenceSourceDomain(str, Enum):
    INSPECTION = "inspection"
    TRUST = "trust"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class EvidenceRecordLink:
    from_record_id: str
    to_record_id: str
    relation: str

    def __post_init__(self) -> None:
        if not self.from_record_id.strip():
            raise EvidenceLinkingFailure("evidence link requires from_record_id")
        if not self.to_record_id.strip():
            raise EvidenceLinkingFailure("evidence link requires to_record_id")
        if not self.relation.strip():
            raise EvidenceLinkingFailure("evidence link relation is required")


@dataclass(frozen=True)
class InboundEvidenceRecord:
    record_id: str
    evidence_kind: str
    source_domain: EvidenceSourceDomain
    payload: Mapping[str, Any]
    links: tuple[EvidenceRecordLink, ...] = ()

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise MalformedInboundEvidenceRecord(
                "inbound evidence record_id is required"
            )
        if not self.evidence_kind.strip():
            raise MalformedInboundEvidenceRecord(
                "inbound evidence_kind is required"
            )
        try:
            source_domain = EvidenceSourceDomain(self.source_domain)
        except (TypeError, ValueError) as exc:
            raise MalformedInboundEvidenceRecord(
                "inbound evidence source_domain must name an upstream Kalibra domain"
            ) from exc
        canonical_payload = _canonicalize(self.payload)
        if not isinstance(canonical_payload, dict):
            raise MalformedInboundEvidenceRecord(
                "inbound evidence payload must be a mapping"
            )
        _reject_fabrication_markers(canonical_payload)
        _reject_prototype_performance_evidence(
            self.evidence_kind,
            canonical_payload,
        )
        object.__setattr__(self, "source_domain", source_domain)
        object.__setattr__(self, "payload", _freeze(canonical_payload))
        object.__setattr__(self, "links", tuple(self.links))


@dataclass(frozen=True)
class PreservedEvidenceRecord:
    preserved_record_id: str
    inbound_record_id: str
    evidence_kind: str
    source_domain: EvidenceSourceDomain
    payload: Mapping[str, Any]
    content_hash: str

    def __post_init__(self) -> None:
        if not self.preserved_record_id.strip():
            raise MalformedInboundEvidenceRecord(
                "preserved evidence record_id is required"
            )
        if not self.inbound_record_id.strip():
            raise MalformedInboundEvidenceRecord(
                "preserved evidence requires inbound_record_id"
            )
        if not self.evidence_kind.strip():
            raise MalformedInboundEvidenceRecord(
                "preserved evidence_kind is required"
            )
        if not self.content_hash.strip():
            raise MalformedInboundEvidenceRecord(
                "preserved evidence content_hash is required"
            )
        object.__setattr__(
            self,
            "source_domain",
            EvidenceSourceDomain(self.source_domain),
        )
        object.__setattr__(self, "payload", _freeze(_canonicalize(self.payload)))


@dataclass(frozen=True)
class EvidenceChainLink:
    link_id: str
    from_record_id: str
    to_record_id: str
    relation: str
    immutable: bool = True

    def __post_init__(self) -> None:
        if not self.link_id.strip():
            raise EvidenceLinkingFailure("evidence chain link_id is required")
        if not self.from_record_id.strip():
            raise EvidenceLinkingFailure("evidence chain link requires source")
        if not self.to_record_id.strip():
            raise EvidenceLinkingFailure("evidence chain link requires target")
        if not self.relation.strip():
            raise EvidenceLinkingFailure("evidence chain link relation is required")
        if self.immutable is not True:
            raise EvidenceLinkingFailure("evidence chain links must be immutable")


@dataclass(frozen=True)
class EvidenceAbsenceMarker:
    absence_id: str
    expected_stage: str
    reason: str
    upstream_ref: str

    def __post_init__(self) -> None:
        if not self.absence_id.strip():
            raise EvidenceAbsenceFailure("absence marker absence_id is required")
        if not self.expected_stage.strip():
            raise EvidenceAbsenceFailure("absence marker expected_stage is required")
        if not self.reason.strip():
            raise EvidenceAbsenceFailure("absence marker reason is required")
        if not self.upstream_ref.strip():
            raise EvidenceAbsenceFailure("absence marker upstream_ref is required")


@dataclass(frozen=True)
class EvidenceView:
    view_id: str
    records: tuple[PreservedEvidenceRecord, ...]
    links: tuple[EvidenceChainLink, ...] = ()
    absences: tuple[EvidenceAbsenceMarker, ...] = ()
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.view_id.strip():
            raise EvidenceViewFailure("evidence view_id is required")
        if self.read_only is not True:
            raise EvidenceViewFailure("evidence views must be read-only")
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "links", tuple(self.links))
        object.__setattr__(self, "absences", tuple(self.absences))


def preserved_record_from_inbound(
    inbound_record: InboundEvidenceRecord,
) -> PreservedEvidenceRecord:
    payload = _thaw(inbound_record.payload)
    content_hash = _stable_hash(payload)
    preserved_record_id = _stable_id(
        "preserved-evidence-record",
        {
            "content_hash": content_hash,
            "inbound_record_id": inbound_record.record_id,
            "source_domain": inbound_record.source_domain.value,
        },
    )
    return PreservedEvidenceRecord(
        preserved_record_id=preserved_record_id,
        inbound_record_id=inbound_record.record_id,
        evidence_kind=inbound_record.evidence_kind,
        source_domain=inbound_record.source_domain,
        payload=payload,
        content_hash=content_hash,
    )


def chain_link(
    from_record_id: str,
    to_record_id: str,
    relation: str,
) -> EvidenceChainLink:
    return EvidenceChainLink(
        link_id=_stable_id(
            "evidence-chain-link",
            {
                "from_record_id": from_record_id,
                "relation": relation,
                "to_record_id": to_record_id,
            },
        ),
        from_record_id=from_record_id,
        to_record_id=to_record_id,
        relation=relation,
    )


def absence_marker(
    expected_stage: EvidenceSourceDomain | str,
    reason: str,
    upstream_ref: str,
) -> EvidenceAbsenceMarker:
    stage = _stage_value(expected_stage)
    return EvidenceAbsenceMarker(
        absence_id=_stable_id(
            "evidence-absence",
            {
                "expected_stage": stage,
                "reason": reason,
                "upstream_ref": upstream_ref,
            },
        ),
        expected_stage=stage,
        reason=reason,
        upstream_ref=upstream_ref,
    )


def view_from_parts(
    records: Iterable[PreservedEvidenceRecord],
    links: Iterable[EvidenceChainLink],
    absences: Iterable[EvidenceAbsenceMarker],
) -> EvidenceView:
    record_tuple = tuple(records)
    link_tuple = tuple(links)
    absence_tuple = tuple(absences)
    return EvidenceView(
        view_id=_stable_id(
            "evidence-view",
            {
                "absences": [absence.absence_id for absence in absence_tuple],
                "links": [link.link_id for link in link_tuple],
                "records": [record.preserved_record_id for record in record_tuple],
            },
        ),
        records=record_tuple,
        links=link_tuple,
        absences=absence_tuple,
    )


def _stage_value(stage: EvidenceSourceDomain | str) -> str:
    try:
        return EvidenceSourceDomain(stage).value
    except ValueError as exc:
        raise EvidenceAbsenceFailure(
            "absence markers must name an upstream evidence stage"
        ) from exc


def _canonicalize(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonicalize(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_canonicalize(item) for item in value)
    if isinstance(value, list):
        return tuple(_canonicalize(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted(_canonicalize(item) for item in value))
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_thaw(item) for item in value)
    return value


def _reject_fabrication_markers(payload: Mapping[str, Any]) -> None:
    flattened = set(_flatten_payload_tokens(payload))
    if flattened & _FABRICATED_MARKERS:
        raise FabricatedEvidenceRecord(
            "fabricated or inferred evidence records are not accepted"
        )


def _reject_prototype_performance_evidence(
    evidence_kind: str,
    payload: Mapping[str, Any],
) -> None:
    flattened = set(_flatten_payload_tokens(payload))
    if (
        evidence_kind == PERFORMANCE_EVIDENCE_KIND
        and flattened & _PROTOTYPE_MARKERS
    ):
        raise PrototypePerformanceEvidenceRejected(
            "prototype visuals and synthetic overlays are not performance evidence"
        )


def _flatten_payload_tokens(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _flatten_payload_tokens(item)
    elif isinstance(value, tuple):
        for item in value:
            yield from _flatten_payload_tokens(item)
    elif isinstance(value, str):
        yield value


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    return f"{prefix}:{_stable_hash(payload)[:32]}"


def _stable_hash(payload: Any) -> str:
    canonical = json.dumps(
        _canonicalize(payload),
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()
