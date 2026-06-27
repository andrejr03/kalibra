from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pytest

import src.inspection as inspection_api
from src.inspection import (
    INSPECTION_EVIDENCE_KIND,
    RAW_MEASURE_KIND,
    DefectJudgment,
    DefectLocalization,
    EvidenceEmissionFailure,
    InspectionEngine,
    InspectionEngineOutput,
    InspectionEvidenceRecord,
    InspectionExaminationFailure,
    InspectionInput,
    InspectionJudgement,
    InspectionResult,
    InvalidInspectionInput,
    MalformedInspectionInput,
    MissingContentHash,
    MissingInputIdentity,
    NonReproducibleInspection,
    NormalizedBoundingBox,
    PartialInspectionResult,
    PlaceholderExamination,
    RawAnomalyScore,
    RawInspectionResult,
    StabilizedInspectionInput,
    UnstabilizedInspectionInput,
)


DOWNSTREAM_FIELD_NAMES = {
    "abstention",
    "calibrated_confidence",
    "confidence",
    "drift",
    "evaluation",
    "qualified_outcome",
    "qualification",
    "review",
    "review_routing",
    "routing",
    "trust",
    "trust_qualification",
}


def make_input(
    content_hash: str = "stable-content-hash-001",
    input_id: str = "input-001",
) -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=input_id,
        artifact_uri=f"artifact://kalibra/parts/{input_id}.png",
        content_hash=content_hash,
        metadata={"fixture": "fixed"},
    )


def output_for_judgement(judgement: InspectionJudgement) -> InspectionEngineOutput:
    engine = InspectionEngine()
    for index in range(200):
        candidate = make_input(
            content_hash=f"stable-content-hash-{index:03d}",
            input_id=f"input-{index:03d}",
        )
        output = engine.inspect(candidate)
        if output.raw_inspection_result.judgement is judgement:
            return output
    raise AssertionError(f"no deterministic fixture produced {judgement.value}")


def field_names(contract_type: type[object]) -> set[str]:
    return {field.name for field in fields(contract_type)}


def assert_no_downstream_fields(contract_type: type[object]) -> None:
    names = field_names(contract_type)
    assert names.isdisjoint(DOWNSTREAM_FIELD_NAMES)


def test_well_formed_stabilized_input_produces_one_raw_result():
    inspection_input = make_input()

    output = InspectionEngine().inspect(inspection_input)

    assert isinstance(output, InspectionEngineOutput)
    assert isinstance(output.raw_inspection_result, RawInspectionResult)
    assert output.raw_inspection_result.input_id == inspection_input.input_id
    assert output.raw_inspection_result.inspection_result_id


def test_legacy_public_inspection_result_contract_remains_available():
    inspection_input = InspectionInput(
        source_path=Path("part.png"),
        content_sha256="abc123",
        media_type="image/png",
        size_bytes=10,
    )
    result = InspectionResult(
        inspection_input=inspection_input,
        judgment=DefectJudgment.DEFECTIVE,
        raw_anomaly_score=RawAnomalyScore(
            value=42.0,
            scale="method-specific-distance",
        ),
        localizations=(
            DefectLocalization(
                region=NormalizedBoundingBox(
                    x_min=0.1,
                    y_min=0.1,
                    x_max=0.5,
                    y_max=0.5,
                )
            ),
        ),
        method_id="legacy-inspection-method",
        method_version="1",
    )

    assert result.inspection_input.input_id == "abc123"
    assert result.judgment is DefectJudgment.DEFECTIVE
    assert result.raw_anomaly_score.value == 42.0


def test_legacy_and_raw_inspection_result_contracts_are_distinct():
    assert InspectionResult is not RawInspectionResult
    assert "raw_anomaly_score" in field_names(InspectionResult)
    assert "raw_anomaly_measure" in field_names(RawInspectionResult)


def test_raw_measure_is_explicitly_raw_and_not_confidence():
    result = InspectionEngine().inspect(make_input()).raw_inspection_result

    assert result.raw_measure_kind == RAW_MEASURE_KIND
    assert result.raw_measure_kind == "raw_anomaly_measure"
    assert "raw" in result.raw_measure_scale
    assert not hasattr(result, "confidence")
    assert not hasattr(result, "calibrated_confidence")


def test_raw_result_contains_no_downstream_domain_fields():
    assert_no_downstream_fields(RawInspectionResult)
    assert_no_downstream_fields(InspectionEvidenceRecord)
    assert_no_downstream_fields(InspectionEngineOutput)


def test_defect_results_include_localization():
    result = output_for_judgement(
        InspectionJudgement.DEFECT
    ).raw_inspection_result

    assert result.judgement is InspectionJudgement.DEFECT
    assert result.localization is not None
    assert isinstance(result.localization.region, NormalizedBoundingBox)


def test_ok_results_do_not_include_localization():
    result = output_for_judgement(InspectionJudgement.OK).raw_inspection_result

    assert result.judgement is InspectionJudgement.OK
    assert result.localization is None


def test_same_input_produces_identical_result_and_evidence_record():
    engine = InspectionEngine()
    inspection_input = make_input()

    first = engine.inspect(inspection_input)
    second = engine.inspect(inspection_input)

    assert first.raw_inspection_result == second.raw_inspection_result
    assert first.inspection_evidence_record == second.inspection_evidence_record


def test_missing_identity_is_refused():
    with pytest.raises(MissingInputIdentity):
        make_input(input_id="")


def test_missing_content_hash_is_refused():
    with pytest.raises(MissingContentHash):
        make_input(content_hash="")


def test_unstabilized_or_malformed_input_is_refused():
    with pytest.raises(UnstabilizedInspectionInput):
        StabilizedInspectionInput(
            input_id="input-raw",
            artifact_uri="artifact://kalibra/raw/input-raw.png",
            content_hash="hash",
            intake_status="raw",
        )

    with pytest.raises(MalformedInspectionInput):
        InspectionEngine().inspect(object())  # type: ignore[arg-type]


def test_evidence_record_links_back_to_input_and_raw_result():
    output = InspectionEngine().inspect(make_input())
    result = output.raw_inspection_result
    record = output.inspection_evidence_record

    assert record.evidence_kind == INSPECTION_EVIDENCE_KIND
    assert record.input_id == result.input_id
    assert record.inspection_result_id == result.inspection_result_id
    assert record.raw_inspection_result == result


def test_inspection_engine_surface_does_not_expose_downstream_domains():
    engine = InspectionEngine()

    assert not hasattr(engine, "qualify")
    assert not hasattr(engine, "calibrate")
    assert not hasattr(engine, "abstain")
    assert not hasattr(engine, "assess_drift")
    assert not hasattr(engine, "route_for_review")
    assert not hasattr(engine, "evaluate")
    assert not hasattr(engine, "inspect_path")
    assert not hasattr(inspection_api, "InputPreparer")


def test_partial_result_is_refused():
    with pytest.raises(PartialInspectionResult):
        RawInspectionResult(
            inspection_result_id="result-partial",
            input_id="input-partial",
            judgement=InspectionJudgement.DEFECT,
            localization=None,
            raw_anomaly_measure=51.0,
            examination_id="examination-partial",
        )


def test_examination_failure_is_explicit():
    class FailingExaminer:
        def examine(
            self, inspection_input: StabilizedInspectionInput
        ) -> PlaceholderExamination:
            raise RuntimeError("placeholder examination failed")

    with pytest.raises(InspectionExaminationFailure):
        InspectionEngine(examiner=FailingExaminer()).inspect(make_input())


def test_evidence_emission_failure_is_explicit():
    class FailingEvidenceEmitter:
        def emit(self, raw_result: RawInspectionResult) -> object:
            return object()

    with pytest.raises(EvidenceEmissionFailure):
        InspectionEngine(evidence_emitter=FailingEvidenceEmitter()).inspect(
            make_input()
        )


def test_detectable_non_reproducibility_is_refused():
    class NonReproducibleExaminer:
        def __init__(self) -> None:
            self.count = 0

        def examine(
            self, inspection_input: StabilizedInspectionInput
        ) -> PlaceholderExamination:
            self.count += 1
            return PlaceholderExamination(
                input_id=inspection_input.input_id,
                examination_id=f"examination-{self.count}",
                judgement=InspectionJudgement.OK,
                raw_anomaly_measure=10.0 + self.count,
                localization=None,
            )

    with pytest.raises(NonReproducibleInspection):
        InspectionEngine(examiner=NonReproducibleExaminer()).inspect(make_input())


def test_stabilized_input_metadata_cannot_smuggle_downstream_fields():
    with pytest.raises(InvalidInspectionInput):
        StabilizedInspectionInput(
            input_id="input-with-trust",
            artifact_uri="artifact://kalibra/parts/input-with-trust.png",
            content_hash="hash",
            metadata={"calibrated_confidence": "0.9"},
        )

    with pytest.raises(InvalidInspectionInput):
        StabilizedInspectionInput(
            input_id="input-with-ground-truth",
            artifact_uri="artifact://kalibra/parts/input-with-ground-truth.png",
            content_hash="hash",
            metadata={"ground-truth": "defective"},
        )


def test_stabilized_input_metadata_allows_ordinary_industrial_keys():
    inspection_input = StabilizedInspectionInput(
        input_id="input-with-industrial-metadata",
        artifact_uri="artifact://kalibra/parts/input-with-industrial-metadata.png",
        content_hash="hash",
        metadata={
            "label": "etched housing label",
            "labeled_region": "front panel",
            "router_part_number": "R-100",
        },
    )

    assert inspection_input.metadata["label"] == "etched housing label"


def test_ok_result_contract_does_not_require_localization():
    result = RawInspectionResult(
        inspection_result_id="result-ok",
        input_id="input-ok",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=5.0,
        examination_id="examination-ok",
    )

    assert result.localization is None
