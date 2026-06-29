from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from src.inspection import InspectionEvidenceRecord, InspectionResult
from src.review import HumanReviewResult, ReviewEvidenceRecord
from src.trust import TrustQualificationEvidenceRecord, TrustQualifiedResult

from .domain import (
    EvidenceRecordLink,
    EvidenceSourceDomain,
    EvidenceView,
    InboundEvidenceRecord,
    absence_marker,
    chain_link,
    preserved_record_from_inbound,
    view_from_parts,
)
from .errors import (
    EvidenceAbsenceFailure,
    EvidencePreservationFailure,
    InvalidEvidenceResult,
    MalformedInboundEvidenceRecord,
    NonReproducibleEvidencePreservation,
)
from .interfaces import EvidenceMethod
from .types import EvidenceArtifact, EvidenceBundle, EvidenceResult


@dataclass(frozen=True)
class EvidenceEngine:
    method: EvidenceMethod | None = None

    def preserve(
        self,
        evidence_records: Iterable[
            InboundEvidenceRecord
            | InspectionEvidenceRecord
            | TrustQualificationEvidenceRecord
            | ReviewEvidenceRecord
        ],
        expected_stages: Iterable[EvidenceSourceDomain | str] = (),
    ) -> EvidenceView:
        materialized_records = tuple(evidence_records)
        materialized_expected_stages = tuple(expected_stages)

        first_view = self._preserve_once(
            materialized_records,
            materialized_expected_stages,
        )
        second_view = self._preserve_once(
            materialized_records,
            materialized_expected_stages,
        )
        if first_view != second_view:
            raise NonReproducibleEvidencePreservation(
                "fixed evidence inputs produced divergent preserved views"
            )
        return first_view

    def record_absence(
        self,
        expected_stage: EvidenceSourceDomain | str,
        reason: str,
        upstream_ref: str,
    ):
        return absence_marker(expected_stage, reason, upstream_ref)

    def create_bundle(
        self,
        inspection_result: InspectionResult,
        trust_qualified_result: TrustQualifiedResult,
        artifacts: tuple[EvidenceArtifact, ...],
        bundle_id: str,
        human_review_result: HumanReviewResult | None = None,
    ) -> EvidenceBundle:
        return EvidenceBundle(
            inspection_result=inspection_result,
            trust_qualified_result=trust_qualified_result,
            artifacts=artifacts,
            bundle_id=bundle_id,
            human_review_result=human_review_result,
        )

    def collect(
        self,
        evidence_bundle: EvidenceBundle,
    ) -> EvidenceResult:
        if self.method is None:
            raise InvalidEvidenceResult(
                "legacy evidence collection requires an evidence method"
            )
        result = self.method.collect(evidence_bundle)
        if not isinstance(result, EvidenceResult):
            raise InvalidEvidenceResult(
                "evidence methods must return EvidenceResult"
            )
        if result.evidence_bundle is not evidence_bundle:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected bundle"
            )
        if result.inspection_result is not evidence_bundle.inspection_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected inspection result"
            )
        if result.trust_qualified_result is not evidence_bundle.trust_qualified_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected trust result"
            )
        if result.human_review_result is not evidence_bundle.human_review_result:
            raise InvalidEvidenceResult(
                "evidence result must reference the collected human review result"
            )
        if result.method_id != self.method.method_id:
            raise InvalidEvidenceResult(
                "evidence result method_id must match the method"
            )
        if result.method_version != self.method.method_version:
            raise InvalidEvidenceResult(
                "evidence result method_version must match the method"
            )
        return result

    def _preserve_once(
        self,
        evidence_records: tuple[
            InboundEvidenceRecord
            | InspectionEvidenceRecord
            | TrustQualificationEvidenceRecord
            | ReviewEvidenceRecord,
            ...,
        ],
        expected_stages: tuple[EvidenceSourceDomain | str, ...],
    ) -> EvidenceView:
        inbound_records = tuple(
            _adapt_inbound_record(record) for record in evidence_records
        )
        if not inbound_records and not expected_stages:
            raise MalformedInboundEvidenceRecord(
                "evidence preservation requires records or explicit absences"
            )

        inbound_records = tuple(sorted(inbound_records, key=_inbound_sort_key))
        preserved_records = tuple(
            sorted(
                (
                    preserved_record_from_inbound(record)
                    for record in inbound_records
                ),
                key=_preserved_sort_key,
            )
        )
        preserved_by_inbound_id = {
            preserved.inbound_record_id: preserved
            for preserved in preserved_records
        }
        links = _build_chain_links(inbound_records, preserved_by_inbound_id)
        absences = _build_absence_markers(preserved_records, expected_stages)
        return view_from_parts(preserved_records, links, absences)


def _adapt_inbound_record(
    record: (
        InboundEvidenceRecord
        | InspectionEvidenceRecord
        | TrustQualificationEvidenceRecord
        | ReviewEvidenceRecord
    ),
) -> InboundEvidenceRecord:
    if isinstance(record, InboundEvidenceRecord):
        return record
    if isinstance(record, InspectionEvidenceRecord):
        return _inspection_inbound_record(record)
    if isinstance(record, TrustQualificationEvidenceRecord):
        return _trust_inbound_record(record)
    if isinstance(record, ReviewEvidenceRecord):
        return _review_inbound_record(record)
    raise MalformedInboundEvidenceRecord(
        "evidence engine only accepts upstream evidence records"
    )


def _inspection_inbound_record(
    record: InspectionEvidenceRecord,
) -> InboundEvidenceRecord:
    return InboundEvidenceRecord(
        record_id=record.record_id,
        evidence_kind=record.evidence_kind,
        source_domain=EvidenceSourceDomain.INSPECTION,
        payload=record,
        links=(
            EvidenceRecordLink(
                from_record_id=record.input_id,
                to_record_id=record.inspection_result_id,
                relation="source_input_to_raw_inspection",
            ),
        ),
    )


def _trust_inbound_record(
    record: TrustQualificationEvidenceRecord,
) -> InboundEvidenceRecord:
    return InboundEvidenceRecord(
        record_id=record.record_id,
        evidence_kind=record.evidence_kind,
        source_domain=EvidenceSourceDomain.TRUST,
        payload=record,
        links=(
            EvidenceRecordLink(
                from_record_id=record.inspection_result_id,
                to_record_id=record.qualification_result_id,
                relation="raw_inspection_result_to_trust_qualification",
            ),
        ),
    )


def _review_inbound_record(record: ReviewEvidenceRecord) -> InboundEvidenceRecord:
    return InboundEvidenceRecord(
        record_id=record.record_id,
        evidence_kind=record.evidence_kind,
        source_domain=EvidenceSourceDomain.HUMAN_REVIEW,
        payload=record,
        links=(
            EvidenceRecordLink(
                from_record_id=record.upstream_chain.qualification_result_id,
                to_record_id=record.review_case_id,
                relation="trust_qualification_to_human_review",
            ),
            EvidenceRecordLink(
                from_record_id=record.review_case_id,
                to_record_id=record.reviewer_decision.decision_id,
                relation="review_case_to_reviewer_decision",
            ),
        ),
    )


def _source_domain_order(source_domain: EvidenceSourceDomain) -> int:
    domain_order = {
        EvidenceSourceDomain.INSPECTION: 0,
        EvidenceSourceDomain.TRUST: 1,
        EvidenceSourceDomain.HUMAN_REVIEW: 2,
    }
    return domain_order[source_domain]


def _inbound_sort_key(record: InboundEvidenceRecord) -> tuple[int, str]:
    return (_source_domain_order(record.source_domain), record.record_id)


def _preserved_sort_key(record) -> tuple[int, str, str]:
    return (
        _source_domain_order(record.source_domain),
        record.inbound_record_id,
        record.preserved_record_id,
    )


def _build_chain_links(
    inbound_records: tuple[InboundEvidenceRecord, ...],
    preserved_by_inbound_id: dict[str, object],
) -> tuple:
    links = []
    seen: set[tuple[str, str, str]] = set()

    for inbound in inbound_records:
        preserved = preserved_by_inbound_id[inbound.record_id]
        for inbound_link in inbound.links:
            link = chain_link(
                from_record_id=inbound_link.from_record_id,
                to_record_id=inbound_link.to_record_id,
                relation=inbound_link.relation,
            )
            _append_unique_link(links, seen, link)
            record_link = chain_link(
                from_record_id=inbound_link.to_record_id,
                to_record_id=preserved.preserved_record_id,  # type: ignore[attr-defined]
                relation=f"{inbound_link.relation}_evidence_record",
            )
            _append_unique_link(links, seen, record_link)

    inspection_by_result_id = {}
    trust_by_inspection_id = {}
    trust_by_qualification_id = {}
    review_by_qualification_id = {}
    review_by_case_id = {}
    for preserved in preserved_by_inbound_id.values():
        payload = preserved.payload  # type: ignore[attr-defined]
        if preserved.source_domain is EvidenceSourceDomain.INSPECTION:  # type: ignore[attr-defined]
            inspection_by_result_id[payload["inspection_result_id"]] = preserved
        elif preserved.source_domain is EvidenceSourceDomain.TRUST:  # type: ignore[attr-defined]
            trust_by_inspection_id[payload["inspection_result_id"]] = preserved
            trust_by_qualification_id[payload["qualification_result_id"]] = preserved
        elif preserved.source_domain is EvidenceSourceDomain.HUMAN_REVIEW:  # type: ignore[attr-defined]
            chain = payload["upstream_chain"]
            review_by_qualification_id[chain["qualification_result_id"]] = preserved
            review_by_case_id[chain["review_case_id"]] = preserved

    for inspection_result_id, trust_record in trust_by_inspection_id.items():
        inspection_record = inspection_by_result_id.get(inspection_result_id)
        if inspection_record is not None:
            _append_unique_link(
                links,
                seen,
                chain_link(
                    from_record_id=inspection_record.preserved_record_id,
                    to_record_id=trust_record.preserved_record_id,
                    relation="inspection_evidence_to_trust_evidence",
                ),
            )

    for qualification_id, review_record in review_by_qualification_id.items():
        trust_record = trust_by_qualification_id.get(qualification_id)
        if trust_record is not None:
            _append_unique_link(
                links,
                seen,
                chain_link(
                    from_record_id=trust_record.preserved_record_id,
                    to_record_id=review_record.preserved_record_id,
                    relation="trust_evidence_to_human_review_evidence",
                ),
            )

    if not links and inbound_records:
        raise EvidencePreservationFailure(
            "preserved evidence records must carry chain links or references"
        )
    return tuple(sorted(links, key=lambda link: link.link_id))


def _append_unique_link(links, seen, link) -> None:
    key = (link.from_record_id, link.to_record_id, link.relation)
    if key not in seen:
        links.append(link)
        seen.add(key)


def _build_absence_markers(
    preserved_records: tuple,
    expected_stages: tuple[EvidenceSourceDomain | str, ...],
) -> tuple:
    present_domains = {record.source_domain for record in preserved_records}
    absences = []
    for stage in expected_stages:
        try:
            source_domain = EvidenceSourceDomain(stage)
        except ValueError as exc:
            raise EvidenceAbsenceFailure(
                "expected absence stage must name an upstream evidence stage"
            ) from exc
        if source_domain in present_domains:
            continue
        absences.append(
            absence_marker(
                expected_stage=source_domain,
                reason=f"{source_domain.value}_evidence_absent",
                upstream_ref=_upstream_ref_for_absence(
                    preserved_records,
                    source_domain,
                ),
            )
        )
    return tuple(sorted(absences, key=lambda absence: absence.absence_id))


def _upstream_ref_for_absence(
    preserved_records: tuple,
    expected_stage: EvidenceSourceDomain,
) -> str:
    if expected_stage is EvidenceSourceDomain.HUMAN_REVIEW:
        for record in preserved_records:
            if record.source_domain is EvidenceSourceDomain.TRUST:
                return record.payload["qualification_result_id"]
    if expected_stage is EvidenceSourceDomain.TRUST:
        for record in preserved_records:
            if record.source_domain is EvidenceSourceDomain.INSPECTION:
                return record.payload["inspection_result_id"]
    for record in reversed(preserved_records):
        return record.preserved_record_id
    return "no-upstream-record"
