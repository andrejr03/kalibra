from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pytest

import src.inspection.engine as inspection_engine_module
import src.inspection as inspection_api
from src.inspection.engine import _read_pgm_p2, _resolve_local_artifact_path
from src.inspection.local_artifacts import local_contrast_analysis
from src.inspection import (
    IMAGE_BASELINE_EXAMINATION_KIND,
    IMAGE_BASELINE_RAW_SCALE,
    INSPECTION_EVIDENCE_KIND,
    INSPECTION_PREDICTION_KIND,
    PREDICTION_RAW_MEASURE_SCALE,
    RAW_MEASURE_KIND,
    DefectJudgment,
    DefectLocalization,
    DeterministicImageBaselineExaminer,
    EvidenceEmissionFailure,
    InspectionEngine,
    InspectionEngineOutput,
    InspectionError,
    InspectionEvidenceRecord,
    InspectionExaminationFailure,
    InspectionInferenceProvider,
    InspectionInput,
    InspectionJudgement,
    InspectionPrediction,
    InspectionResult,
    InvalidInspectionInput,
    InvalidInspectionPrediction,
    InvalidInspectionResult,
    MalformedInspectionInput,
    MissingContentHash,
    MissingInputIdentity,
    NonReproducibleInspection,
    NormalizedBoundingBox,
    PartialInspectionPrediction,
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

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "inspection"


def _inspection_fixture_path(filename: str) -> Path:
    return FIXTURES / filename


def _read_pgm_fixture(filename: str) -> tuple[list[list[int]], int]:
    return _read_pgm_p2(_inspection_fixture_path(filename))


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


def _baseline_engine() -> InspectionEngine:
    return InspectionEngine(examiner=DeterministicImageBaselineExaminer())


def _local_artifact_fixture_input(
    filename: str,
    *,
    input_id_prefix: str = "baseline",
) -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=f"{input_id_prefix}-{filename}",
        artifact_uri=str(_inspection_fixture_path(filename)),
        content_hash=f"content-hash-{filename}",
    )


def _baseline_input(filename: str) -> StabilizedInspectionInput:
    return _local_artifact_fixture_input(filename, input_id_prefix="baseline")


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


def _prediction_localization() -> DefectLocalization:
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=0.2,
            y_min=0.3,
            x_max=0.6,
            y_max=0.7,
        )
    )


def _ok_prediction_for(
    inspection_input: StabilizedInspectionInput,
    prediction_id: str = "prediction-ok",
) -> InspectionPrediction:
    return InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id=prediction_id,
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
    )


def _defect_prediction_for(
    inspection_input: StabilizedInspectionInput,
    prediction_id: str = "prediction-defect",
) -> InspectionPrediction:
    return InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id=prediction_id,
        predicted_judgement=InspectionJudgement.DEFECT,
        predicted_raw_anomaly_measure=42.0,
        predicted_localization=_prediction_localization(),
    )


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


def test_image_baseline_labels_are_accepted_by_contracts():
    examination = PlaceholderExamination(
        input_id="input-baseline",
        examination_id="exam-baseline",
        judgement=InspectionJudgement.OK,
        raw_anomaly_measure=12.5,
        localization=None,
        examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
        raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
    )
    assert examination.raw_measure_scale == "local_contrast_raw_0_100"

    result = RawInspectionResult(
        inspection_result_id="result-baseline",
        input_id="input-baseline",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=12.5,
        examination_id="exam-baseline",
        examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
        raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
    )
    assert result.examination_kind == "deterministic_local_image_baseline_v1"
    assert result.raw_measure_kind == "raw_anomaly_measure"


def test_pgm_reader_parses_grid_and_maxval():
    pixels, maxval = _read_pgm_fixture("blob_defect.pgm")

    assert maxval == 255
    assert pixels == [
        [0, 0, 0, 0],
        [0, 255, 255, 0],
        [0, 255, 255, 0],
        [0, 0, 0, 0],
    ]


def test_shifted_blob_fixture_is_valid_changed_defect_content():
    original_pixels, original_maxval = _read_pgm_fixture("blob_defect.pgm")
    shifted_pixels, shifted_maxval = _read_pgm_fixture("blob_defect_shifted.pgm")

    assert original_maxval == shifted_maxval == 255
    assert shifted_pixels == [
        [255, 255, 0, 0],
        [255, 255, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    assert shifted_pixels != original_pixels

    _, max_deviation, _, _ = local_contrast_analysis(
        shifted_pixels,
        shifted_maxval,
    )
    assert round(max_deviation * 100.0, 6) >= 50.0


def test_pgm_reader_rejects_non_p2_and_truncated():
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(FIXTURES / "bad_magic.pgm")
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(FIXTURES / "truncated.pgm")


def test_pgm_reader_rejects_malformed_missing_and_out_of_range_files(tmp_path):
    malformed_header = tmp_path / "malformed_header.pgm"
    malformed_header.write_text("P2\nx 1\n255\n0\n", encoding="ascii")
    non_numeric_pixel = tmp_path / "non_numeric_pixel.pgm"
    non_numeric_pixel.write_text("P2\n1 1\n255\nx\n", encoding="ascii")
    out_of_range_pixel = tmp_path / "out_of_range_pixel.pgm"
    out_of_range_pixel.write_text("P2\n1 1\n255\n256\n", encoding="ascii")

    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(malformed_header)
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(non_numeric_pixel)
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(out_of_range_pixel)
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(FIXTURES / "missing.pgm")


def test_resolver_rejects_non_local_scheme():
    assert _resolve_local_artifact_path("part.pgm") == Path("part.pgm")
    assert _resolve_local_artifact_path("file:///tmp/x.pgm") == Path("/tmp/x.pgm")
    with pytest.raises(InspectionExaminationFailure):
        _resolve_local_artifact_path("artifact://kalibra/x.png")
    with pytest.raises(InspectionExaminationFailure):
        _resolve_local_artifact_path("http://example.test/x.pgm")
    with pytest.raises(InspectionExaminationFailure):
        _resolve_local_artifact_path("https://example.test/x.pgm")


def test_baseline_defect_image_produces_localized_raw_result():
    output = _baseline_engine().inspect(_baseline_input("blob_defect.pgm"))
    result = output.raw_inspection_result

    assert result.judgement is InspectionJudgement.DEFECT
    assert result.raw_measure_kind == "raw_anomaly_measure"
    assert result.raw_measure_kind == RAW_MEASURE_KIND
    assert result.raw_measure_scale == "local_contrast_raw_0_100"
    assert result.raw_measure_scale == IMAGE_BASELINE_RAW_SCALE
    assert 0.0 <= result.raw_anomaly_measure <= 100.0
    assert result.localization is not None
    assert result.localization.region == NormalizedBoundingBox(
        x_min=0.25, y_min=0.25, x_max=0.75, y_max=0.75
    )
    assert not hasattr(result, "confidence")
    assert not hasattr(result, "calibrated_confidence")


def test_baseline_uniform_image_is_ok_without_localization():
    output = _baseline_engine().inspect(_baseline_input("uniform_ok.pgm"))
    result = output.raw_inspection_result

    assert result.judgement is InspectionJudgement.OK
    assert result.localization is None
    assert result.raw_anomaly_measure == 0.0


def test_baseline_same_image_is_reproducible():
    engine = _baseline_engine()
    inspection_input = _baseline_input("blob_defect.pgm")

    first = engine.inspect(inspection_input)
    second = engine.inspect(inspection_input)

    assert first.raw_inspection_result == second.raw_inspection_result
    assert first.inspection_evidence_record == second.inspection_evidence_record


def test_baseline_missing_or_non_local_artifact_fails_explicitly():
    missing = StabilizedInspectionInput(
        input_id="baseline-missing",
        artifact_uri=str(FIXTURES / "does_not_exist.pgm"),
        content_hash="content-hash-missing",
    )
    with pytest.raises(InspectionExaminationFailure):
        _baseline_engine().inspect(missing)

    non_local = StabilizedInspectionInput(
        input_id="baseline-non-local",
        artifact_uri="artifact://kalibra/integration/input-000.png",
        content_hash="content-hash-non-local",
    )
    with pytest.raises(InspectionExaminationFailure):
        _baseline_engine().inspect(non_local)


def test_raw_result_contains_no_downstream_domain_fields():
    assert_no_downstream_fields(RawInspectionResult)
    assert_no_downstream_fields(InspectionEvidenceRecord)
    assert_no_downstream_fields(InspectionEngineOutput)


def test_prediction_transformation_raw_result_accepts_prediction_provenance():
    result = RawInspectionResult(
        inspection_result_id="result-from-prediction",
        input_id="input-from-prediction",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=7.5,
        examination_id="prediction-001",
        raw_measure_scale=PREDICTION_RAW_MEASURE_SCALE,
        examination_kind=INSPECTION_PREDICTION_KIND,
    )

    assert result.examination_kind == INSPECTION_PREDICTION_KIND
    assert result.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert result.raw_measure_kind == RAW_MEASURE_KIND


def test_prediction_transformation_raw_result_exposes_no_downstream_fields():
    assert_no_downstream_fields(RawInspectionResult)


def test_prediction_transformation_raw_result_has_no_prediction_id_field():
    result = RawInspectionResult(
        inspection_result_id="result-no-prediction-field",
        input_id="input-no-prediction-field",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=7.5,
        examination_id="prediction-001",
        raw_measure_scale=PREDICTION_RAW_MEASURE_SCALE,
        examination_kind=INSPECTION_PREDICTION_KIND,
    )

    assert "prediction_id" not in field_names(RawInspectionResult)
    assert not hasattr(result, "prediction_id")


def test_prediction_transformation_preserves_existing_raw_result_provenance():
    placeholder_result = RawInspectionResult(
        inspection_result_id="result-placeholder",
        input_id="input-placeholder",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=7.5,
        examination_id="examination-placeholder",
    )
    baseline_result = RawInspectionResult(
        inspection_result_id="result-baseline",
        input_id="input-baseline",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=12.5,
        examination_id="examination-baseline",
        raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
        examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
    )

    assert placeholder_result.raw_measure_kind == RAW_MEASURE_KIND
    assert baseline_result.raw_measure_kind == RAW_MEASURE_KIND
    assert placeholder_result.raw_measure_scale == "placeholder_hash_raw_0_100"
    assert baseline_result.raw_measure_scale == "local_contrast_raw_0_100"
    assert placeholder_result.examination_kind == "deterministic_placeholder_examination"
    assert baseline_result.examination_kind == "deterministic_local_image_baseline_v1"


def test_prediction_transformation_valid_ok_prediction_returns_engine_output():
    inspection_input = make_input(input_id="input-transform-ok")
    prediction = _ok_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-ok",
    )

    output = InspectionEngine().transform_prediction(inspection_input, prediction)

    assert isinstance(output, InspectionEngineOutput)
    assert isinstance(output.raw_inspection_result, RawInspectionResult)
    assert isinstance(output.inspection_evidence_record, InspectionEvidenceRecord)
    assert output.raw_inspection_result.judgement is InspectionJudgement.OK
    assert output.raw_inspection_result.localization is None


def test_prediction_transformation_valid_defect_prediction_returns_localized_result():
    inspection_input = make_input(input_id="input-transform-defect")
    prediction = _defect_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-defect",
    )

    output = InspectionEngine().transform_prediction(inspection_input, prediction)
    result = output.raw_inspection_result

    assert result.judgement is InspectionJudgement.DEFECT
    assert result.localization == prediction.predicted_localization
    assert result.localization is not None
    assert result.localization.region == _prediction_localization().region


def test_prediction_transformation_preserves_prediction_provenance_labels():
    inspection_input = make_input(input_id="input-transform-provenance")
    prediction = _ok_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-provenance",
    )

    result = InspectionEngine().transform_prediction(
        inspection_input,
        prediction,
    ).raw_inspection_result

    assert result.raw_measure_kind == RAW_MEASURE_KIND
    assert result.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert result.examination_kind == INSPECTION_PREDICTION_KIND


def test_prediction_transformation_preserves_single_source_prediction_mapping():
    inspection_input = make_input(input_id="input-transform-single-source")
    prediction = _defect_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-single-source",
    )

    result = InspectionEngine().transform_prediction(
        inspection_input,
        prediction,
    ).raw_inspection_result

    assert result.judgement is prediction.predicted_judgement
    assert result.localization == prediction.predicted_localization
    assert result.raw_anomaly_measure == prediction.predicted_raw_anomaly_measure
    assert result.examination_id == prediction.prediction_id


def test_prediction_transformation_emits_evidence_for_transformed_raw_result():
    inspection_input = make_input(input_id="input-transform-evidence")
    prediction = _ok_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-evidence",
    )

    output = InspectionEngine().transform_prediction(inspection_input, prediction)
    result = output.raw_inspection_result
    record = output.inspection_evidence_record

    assert record.evidence_kind == INSPECTION_EVIDENCE_KIND
    assert record.input_id == result.input_id
    assert record.inspection_result_id == result.inspection_result_id
    assert record.raw_inspection_result == result


def test_prediction_transformation_does_not_expose_prediction_downstream():
    inspection_input = make_input(input_id="input-transform-isolation")
    prediction = _ok_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-isolation",
    )

    output = InspectionEngine().transform_prediction(inspection_input, prediction)

    assert not hasattr(output, "prediction")
    assert not hasattr(output, "inspection_prediction")
    assert not hasattr(output.raw_inspection_result, "prediction")
    assert not hasattr(output.raw_inspection_result, "prediction_id")
    assert output.inspection_evidence_record.raw_inspection_result is not prediction
    assert output.inspection_evidence_record.raw_inspection_result == (
        output.raw_inspection_result
    )


def test_prediction_transformation_rejects_non_prediction_object():
    inspection_input = make_input(input_id="input-transform-non-prediction")

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, object())


def test_prediction_transformation_rejects_input_mismatch():
    inspection_input = make_input(input_id="input-transform-mismatch")
    prediction = InspectionPrediction(
        input_id="different-input",
        prediction_id="prediction-transform-mismatch",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
    )

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, prediction)


def test_prediction_transformation_rejects_unsupported_prediction_kind():
    inspection_input = make_input(input_id="input-transform-unsupported-kind")
    prediction = InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id="prediction-transform-unsupported-kind",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
        prediction_kind="unsupported_prediction_kind",
    )

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, prediction)


@pytest.mark.parametrize(
    "prediction_kind",
    [
        "inspection_prediction_v2",
        "inspection_prediction_future",
    ],
)
def test_prediction_transformation_rejects_version_like_prediction_kind(
    prediction_kind,
):
    inspection_input = make_input(input_id=f"input-transform-{prediction_kind}")
    prediction = InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id=f"prediction-transform-{prediction_kind}",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
        prediction_kind=prediction_kind,
    )

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, prediction)


def test_prediction_transformation_rejects_bypassed_prediction_validation():
    inspection_input = make_input(input_id="input-transform-bypassed-validation")
    prediction = _ok_prediction_for(
        inspection_input,
        prediction_id="prediction-transform-bypassed-validation",
    )
    object.__setattr__(prediction, "raw_measure_kind", "confidence")

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, prediction)


def test_prediction_transformation_rejected_prediction_emits_no_evidence():
    class RecordingEvidenceEmitter:
        def __init__(self) -> None:
            self.raw_results: list[RawInspectionResult] = []

        def emit(self, raw_result: RawInspectionResult) -> InspectionEvidenceRecord:
            self.raw_results.append(raw_result)
            return InspectionEvidenceRecord(
                record_id="should-not-be-emitted",
                input_id=raw_result.input_id,
                inspection_result_id=raw_result.inspection_result_id,
                raw_inspection_result=raw_result,
            )

    inspection_input = make_input(input_id="input-transform-no-evidence")
    prediction = InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id="prediction-transform-no-evidence",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
        prediction_kind="inspection_prediction_future",
    )
    evidence_emitter = RecordingEvidenceEmitter()

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine(evidence_emitter=evidence_emitter).transform_prediction(
            inspection_input,
            prediction,
        )

    assert evidence_emitter.raw_results == []


def test_prediction_transformation_rejected_prediction_produces_no_raw_result(
    monkeypatch,
):
    inspection_input = make_input(input_id="input-transform-no-raw-result")
    prediction = InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id="prediction-transform-no-raw-result",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=7.5,
        predicted_localization=None,
        prediction_kind="inspection_prediction_v2",
    )
    raw_result_calls = []

    def fail_if_raw_result_is_constructed(*args, **kwargs):
        raw_result_calls.append((args, kwargs))
        raise AssertionError("rejected predictions must not produce raw results")

    monkeypatch.setattr(
        inspection_engine_module,
        "RawInspectionResult",
        fail_if_raw_result_is_constructed,
    )

    with pytest.raises(InvalidInspectionPrediction):
        InspectionEngine().transform_prediction(inspection_input, prediction)

    assert raw_result_calls == []


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


def test_prediction_error_hierarchy_extends_inspection_errors():
    assert issubclass(InvalidInspectionPrediction, InspectionError)
    assert issubclass(PartialInspectionPrediction, InvalidInspectionPrediction)


def test_valid_ok_inspection_prediction_constructs_with_raw_defaults():
    prediction = InspectionPrediction(
        input_id="input-ok-prediction",
        prediction_id="prediction-ok",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=0.25,
        predicted_localization=None,
    )

    assert prediction.input_id == "input-ok-prediction"
    assert prediction.prediction_id == "prediction-ok"
    assert prediction.predicted_judgement is InspectionJudgement.OK
    assert prediction.predicted_raw_anomaly_measure == 0.25
    assert prediction.predicted_localization is None
    assert prediction.raw_measure_kind == RAW_MEASURE_KIND
    assert prediction.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert prediction.prediction_kind == INSPECTION_PREDICTION_KIND


def test_valid_defect_inspection_prediction_constructs_with_localization():
    localization = _prediction_localization()

    prediction = InspectionPrediction(
        input_id="input-defect-prediction",
        prediction_id="prediction-defect",
        predicted_judgement=InspectionJudgement.DEFECT,
        predicted_raw_anomaly_measure=42.0,
        predicted_localization=localization,
        model_metadata={"method": "abstract-v1", "version": "1"},
    )

    assert prediction.predicted_judgement is InspectionJudgement.DEFECT
    assert prediction.predicted_localization == localization
    assert prediction.model_metadata["method"] == "abstract-v1"
    assert prediction.model_metadata["version"] == "1"


def test_inspection_prediction_defect_without_localization_is_partial():
    with pytest.raises(PartialInspectionPrediction):
        InspectionPrediction(
            input_id="input-defect-without-localization",
            prediction_id="prediction-defect-without-localization",
            predicted_judgement=InspectionJudgement.DEFECT,
            predicted_raw_anomaly_measure=51.0,
            predicted_localization=None,
        )


def test_inspection_prediction_ok_with_localization_is_partial():
    with pytest.raises(PartialInspectionPrediction):
        InspectionPrediction(
            input_id="input-ok-with-localization",
            prediction_id="prediction-ok-with-localization",
            predicted_judgement=InspectionJudgement.OK,
            predicted_raw_anomaly_measure=5.0,
            predicted_localization=_prediction_localization(),
        )


def test_inspection_prediction_invalid_localization_uses_existing_validation():
    with pytest.raises(InvalidInspectionResult):
        InspectionPrediction(
            input_id="input-invalid-localization",
            prediction_id="prediction-invalid-localization",
            predicted_judgement=InspectionJudgement.DEFECT,
            predicted_raw_anomaly_measure=77.0,
            predicted_localization=DefectLocalization(
                region=NormalizedBoundingBox(
                    x_min=0.9,
                    y_min=0.2,
                    x_max=0.1,
                    y_max=0.8,
                )
            ),
        )


@pytest.mark.parametrize(
    "raw_measure",
    [float("nan"), float("inf"), float("-inf")],
)
def test_inspection_prediction_rejects_non_finite_raw_measure(raw_measure):
    with pytest.raises(InvalidInspectionPrediction):
        InspectionPrediction(
            input_id="input-non-finite-measure",
            prediction_id="prediction-non-finite-measure",
            predicted_judgement=InspectionJudgement.OK,
            predicted_raw_anomaly_measure=raw_measure,
            predicted_localization=None,
        )


def test_inspection_prediction_rejects_wrong_raw_measure_kind():
    with pytest.raises(InvalidInspectionPrediction):
        InspectionPrediction(
            input_id="input-wrong-kind",
            prediction_id="prediction-wrong-kind",
            predicted_judgement=InspectionJudgement.OK,
            predicted_raw_anomaly_measure=3.0,
            predicted_localization=None,
            raw_measure_kind="confidence",
        )


@pytest.mark.parametrize(
    "override",
    [
        {"input_id": " "},
        {"prediction_id": " "},
        {"raw_measure_scale": " "},
        {"prediction_kind": " "},
    ],
)
def test_inspection_prediction_rejects_blank_required_labels(override):
    kwargs = {
        "input_id": "input-required-labels",
        "prediction_id": "prediction-required-labels",
        "predicted_judgement": InspectionJudgement.OK,
        "predicted_raw_anomaly_measure": 3.0,
        "predicted_localization": None,
    }
    kwargs.update(override)

    with pytest.raises(InvalidInspectionPrediction):
        InspectionPrediction(**kwargs)


def test_inspection_prediction_exposes_no_downstream_fields():
    assert_no_downstream_fields(InspectionPrediction)


@pytest.mark.parametrize(
    "metadata",
    [
        {"calibrated_confidence": "0.9"},
        {"trust_qualification": "accept"},
    ],
)
def test_inspection_prediction_model_metadata_rejects_downstream_keys(metadata):
    with pytest.raises(InvalidInspectionInput):
        InspectionPrediction(
            input_id="input-forbidden-metadata",
            prediction_id="prediction-forbidden-metadata",
            predicted_judgement=InspectionJudgement.OK,
            predicted_raw_anomaly_measure=1.0,
            predicted_localization=None,
            model_metadata=metadata,
        )


def test_inspection_prediction_model_metadata_accepts_descriptive_keys():
    prediction = InspectionPrediction(
        input_id="input-descriptive-metadata",
        prediction_id="prediction-descriptive-metadata",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=1.0,
        predicted_localization=None,
        model_metadata={"method": "abstract-v1", "version": "1"},
    )

    assert prediction.model_metadata["method"] == "abstract-v1"
    assert prediction.model_metadata["version"] == "1"


def test_inspection_prediction_model_metadata_is_immutable():
    metadata = {"method": "abstract-v1", "version": "1"}
    prediction = InspectionPrediction(
        input_id="input-immutable-metadata",
        prediction_id="prediction-immutable-metadata",
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=1.0,
        predicted_localization=None,
        model_metadata=metadata,
    )

    metadata["version"] = "2"
    assert prediction.model_metadata["version"] == "1"
    with pytest.raises(TypeError):
        prediction.model_metadata["version"] = "3"


class StubInspectionInferenceProvider:
    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        return InspectionPrediction(
            input_id=inspection_input.input_id,
            prediction_id=f"prediction-{inspection_input.input_id}",
            predicted_judgement=InspectionJudgement.OK,
            predicted_raw_anomaly_measure=0.0,
            predicted_localization=None,
            model_metadata={"method": "structural-stub"},
        )


def test_inference_provider_structural_stub_returns_prediction():
    provider: InspectionInferenceProvider = StubInspectionInferenceProvider()

    prediction = provider.predict(make_input(input_id="input-provider"))

    assert isinstance(prediction, InspectionPrediction)
    assert prediction.input_id == "input-provider"


def test_inference_provider_protocol_defines_only_predict():
    protocol_methods = {
        name
        for name, value in InspectionInferenceProvider.__dict__.items()
        if callable(value) and not name.startswith("_")
    }

    assert protocol_methods == {"predict"}


def test_inference_provider_exposes_no_downstream_or_runtime_behavior():
    provider = StubInspectionInferenceProvider()

    assert not hasattr(provider, "qualify")
    assert not hasattr(provider, "route_for_review")
    assert not hasattr(provider, "evaluate")
    assert not hasattr(provider, "emit")
    assert not hasattr(provider, "persist")
    assert not hasattr(provider, "train")
    assert not hasattr(provider, "update_model")
    assert not hasattr(provider, "calibrate")


def _local_artifact_provider_type():
    from src.inspection import LocalArtifactInferenceProvider

    return LocalArtifactInferenceProvider


def test_local_artifact_inference_provider_imports_from_public_api():
    provider_type = _local_artifact_provider_type()

    assert provider_type is inspection_api.LocalArtifactInferenceProvider


def test_local_artifact_inference_provider_satisfies_provider_protocol():
    provider: InspectionInferenceProvider = _local_artifact_provider_type()()

    assert callable(provider.predict)


def test_local_artifact_inference_provider_reads_fixture_content():
    provider = _local_artifact_provider_type()()
    inspection_input = _local_artifact_fixture_input(
        "blob_defect.pgm",
        input_id_prefix="local-provider",
    )

    prediction = provider.predict(inspection_input)

    assert isinstance(prediction, InspectionPrediction)
    assert not isinstance(prediction, RawInspectionResult)
    assert prediction.input_id == inspection_input.input_id
    assert prediction.prediction_id.startswith("local-artifact-prediction:")
    assert prediction.predicted_judgement is InspectionJudgement.DEFECT
    assert prediction.predicted_raw_anomaly_measure == 75.0
    assert prediction.predicted_localization is not None
    assert prediction.predicted_localization.region == NormalizedBoundingBox(
        x_min=0.25,
        y_min=0.25,
        x_max=0.75,
        y_max=0.75,
    )
    assert (
        prediction.predicted_localization.localization_kind
        == "local_artifact_suspected_region"
    )
    assert prediction.model_metadata["method"] == (
        "local-artifact-inference-provider-v1"
    )
    assert prediction.model_metadata["artifact_format"] == "pgm_p2"


def test_local_artifact_inference_provider_changed_content_changes_prediction():
    provider = _local_artifact_provider_type()()
    original_input = StabilizedInspectionInput(
        input_id="local-provider-same-input",
        artifact_uri=str(_inspection_fixture_path("blob_defect.pgm")),
        content_hash="content-hash-same-input",
    )
    changed_input = StabilizedInspectionInput(
        input_id="local-provider-same-input",
        artifact_uri=str(_inspection_fixture_path("blob_defect_shifted.pgm")),
        content_hash="content-hash-same-input",
    )

    original_prediction = provider.predict(original_input)
    changed_prediction = provider.predict(changed_input)

    assert isinstance(original_prediction, InspectionPrediction)
    assert isinstance(changed_prediction, InspectionPrediction)
    assert changed_prediction != original_prediction
    assert changed_prediction.predicted_judgement is InspectionJudgement.DEFECT
    assert changed_prediction.predicted_raw_anomaly_measure == 75.0
    assert changed_prediction.predicted_localization is not None
    assert changed_prediction.predicted_localization.region == NormalizedBoundingBox(
        x_min=0.0,
        y_min=0.0,
        x_max=0.5,
        y_max=0.5,
    )


def test_local_artifact_inference_provider_is_deterministic():
    provider = _local_artifact_provider_type()()
    inspection_input = _local_artifact_fixture_input(
        "blob_defect.pgm",
        input_id_prefix="local-provider-deterministic",
    )

    first = provider.predict(inspection_input)
    second = provider.predict(inspection_input)
    from_separate_provider = _local_artifact_provider_type()().predict(
        inspection_input
    )

    assert first == second
    assert first == from_separate_provider


def test_local_artifact_inference_provider_localization_matches_judgement():
    provider = _local_artifact_provider_type()()

    defect_prediction = provider.predict(
        _local_artifact_fixture_input(
            "blob_defect.pgm",
            input_id_prefix="local-provider-defect",
        )
    )
    ok_prediction = provider.predict(
        _local_artifact_fixture_input(
            "uniform_ok.pgm",
            input_id_prefix="local-provider-ok",
        )
    )

    assert defect_prediction.predicted_judgement is InspectionJudgement.DEFECT
    assert defect_prediction.predicted_localization is not None
    assert ok_prediction.predicted_judgement is InspectionJudgement.OK
    assert ok_prediction.predicted_raw_anomaly_measure == 0.0
    assert ok_prediction.predicted_localization is None


def test_local_artifact_inference_provider_rejects_invalid_inputs():
    provider = _local_artifact_provider_type()()
    non_local = StabilizedInspectionInput(
        input_id="local-provider-non-local",
        artifact_uri="artifact://kalibra/parts/non-local.pgm",
        content_hash="content-hash-non-local",
    )
    missing = StabilizedInspectionInput(
        input_id="local-provider-missing",
        artifact_uri=str(_inspection_fixture_path("does_not_exist.pgm")),
        content_hash="content-hash-missing",
    )
    malformed = _local_artifact_fixture_input(
        "bad_magic.pgm",
        input_id_prefix="local-provider-malformed",
    )

    with pytest.raises(MalformedInspectionInput):
        provider.predict(object())
    with pytest.raises(InspectionExaminationFailure):
        provider.predict(non_local)
    with pytest.raises(InspectionExaminationFailure):
        provider.predict(missing)
    with pytest.raises(InspectionExaminationFailure):
        provider.predict(malformed)


def test_local_artifact_inference_provider_prediction_transforms_to_raw_result():
    provider = _local_artifact_provider_type()()
    inspection_input = _local_artifact_fixture_input(
        "blob_defect.pgm",
        input_id_prefix="local-provider-transform",
    )
    prediction = provider.predict(inspection_input)

    output = InspectionEngine().transform_prediction(inspection_input, prediction)
    result = output.raw_inspection_result

    assert isinstance(output, InspectionEngineOutput)
    assert isinstance(result, RawInspectionResult)
    assert result.examination_kind == INSPECTION_PREDICTION_KIND
    assert result.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert result.raw_measure_kind == RAW_MEASURE_KIND
    assert result.examination_id == prediction.prediction_id
    assert output.inspection_evidence_record.raw_inspection_result == result


def test_local_artifact_inference_provider_exposes_no_downstream_behavior():
    provider = _local_artifact_provider_type()()

    assert not hasattr(provider, "qualify")
    assert not hasattr(provider, "calibrate")
    assert not hasattr(provider, "emit")
    assert not hasattr(provider, "evidence")
    assert not hasattr(provider, "evaluate")
    assert not hasattr(provider, "inspect")
    assert not hasattr(provider, "persist")
    assert not hasattr(provider, "raw_result")
    assert not hasattr(provider, "route_for_review")
    assert not hasattr(provider, "transform_prediction")
    assert not hasattr(provider, "update_model")
    assert not hasattr(provider, "train")


def _deterministic_mock_provider_type():
    from src.inspection import DeterministicMockInferenceProvider

    return DeterministicMockInferenceProvider


def _deterministic_mock_prediction_for(
    judgement: InspectionJudgement,
) -> InspectionPrediction:
    provider = _deterministic_mock_provider_type()()
    for index in range(300):
        prediction = provider.predict(
            make_input(
                content_hash=f"mock-provider-content-hash-{index:03d}",
                input_id=f"mock-provider-input-{index:03d}",
            )
        )
        if prediction.predicted_judgement is judgement:
            return prediction
    raise AssertionError(f"no deterministic mock prediction produced {judgement.value}")


def test_deterministic_mock_inference_provider_imports_from_public_api():
    provider_type = _deterministic_mock_provider_type()

    assert provider_type is inspection_api.DeterministicMockInferenceProvider


def test_deterministic_mock_inference_provider_satisfies_provider_protocol():
    provider: InspectionInferenceProvider = _deterministic_mock_provider_type()()

    assert callable(provider.predict)


def test_deterministic_mock_inference_provider_returns_prediction_only():
    provider = _deterministic_mock_provider_type()()

    prediction = provider.predict(make_input(input_id="mock-provider-return"))

    assert isinstance(prediction, InspectionPrediction)
    assert not isinstance(prediction, RawInspectionResult)


def test_deterministic_mock_inference_provider_same_instance_is_deterministic():
    provider = _deterministic_mock_provider_type()()
    inspection_input = make_input(input_id="mock-provider-same-instance")

    first = provider.predict(inspection_input)
    second = provider.predict(inspection_input)

    assert first == second


def test_deterministic_mock_inference_provider_separate_instances_are_deterministic():
    inspection_input = make_input(input_id="mock-provider-separate-instances")

    first = _deterministic_mock_provider_type()().predict(inspection_input)
    second = _deterministic_mock_provider_type()().predict(inspection_input)

    assert first == second


def test_deterministic_mock_inference_provider_changed_input_remains_valid():
    provider = _deterministic_mock_provider_type()()
    base_prediction = provider.predict(
        make_input(
            content_hash="mock-provider-base-content-hash",
            input_id="mock-provider-base-input",
        )
    )
    changed_prediction = provider.predict(
        make_input(
            content_hash="mock-provider-changed-content-hash",
            input_id="mock-provider-changed-input",
        )
    )

    assert isinstance(base_prediction, InspectionPrediction)
    assert isinstance(changed_prediction, InspectionPrediction)
    assert changed_prediction != base_prediction


def test_deterministic_mock_inference_provider_localization_matches_judgement():
    defect_prediction = _deterministic_mock_prediction_for(InspectionJudgement.DEFECT)
    ok_prediction = _deterministic_mock_prediction_for(InspectionJudgement.OK)

    assert defect_prediction.predicted_localization is not None
    assert ok_prediction.predicted_localization is None


def test_deterministic_mock_inference_provider_exposes_no_downstream_behavior():
    provider = _deterministic_mock_provider_type()()

    assert not hasattr(provider, "qualify")
    assert not hasattr(provider, "calibrate")
    assert not hasattr(provider, "emit")
    assert not hasattr(provider, "evidence")
    assert not hasattr(provider, "evaluate")
    assert not hasattr(provider, "inspect")
    assert not hasattr(provider, "persist")
    assert not hasattr(provider, "raw_result")
    assert not hasattr(provider, "route_for_review")
    assert not hasattr(provider, "transform_prediction")
    assert not hasattr(provider, "update_model")
    assert not hasattr(provider, "train")


def test_deterministic_mock_inference_provider_rejects_malformed_input():
    provider = _deterministic_mock_provider_type()()

    with pytest.raises(MalformedInspectionInput):
        provider.predict(object())


def test_deterministic_mock_inference_provider_prediction_transforms_to_raw_result():
    provider = _deterministic_mock_provider_type()()
    inspection_input = make_input(input_id="mock-provider-transform")
    prediction = provider.predict(inspection_input)

    output = InspectionEngine().transform_prediction(inspection_input, prediction)
    result = output.raw_inspection_result

    assert isinstance(prediction, InspectionPrediction)
    assert isinstance(output, InspectionEngineOutput)
    assert isinstance(result, RawInspectionResult)
    assert result.examination_kind == INSPECTION_PREDICTION_KIND
    assert result.raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE
    assert result.raw_measure_kind == RAW_MEASURE_KIND


def test_deterministic_mock_inference_provider_evidence_is_engine_owned():
    class RecordingEvidenceEmitter:
        def __init__(self) -> None:
            self.raw_results: list[RawInspectionResult] = []

        def emit(self, raw_result: RawInspectionResult) -> InspectionEvidenceRecord:
            self.raw_results.append(raw_result)
            return InspectionEvidenceRecord(
                record_id=f"record-{raw_result.inspection_result_id}",
                input_id=raw_result.input_id,
                inspection_result_id=raw_result.inspection_result_id,
                raw_inspection_result=raw_result,
            )

    provider = _deterministic_mock_provider_type()()
    inspection_input = make_input(input_id="mock-provider-evidence-owned")
    evidence_emitter = RecordingEvidenceEmitter()

    prediction = provider.predict(inspection_input)
    assert evidence_emitter.raw_results == []

    output = InspectionEngine(evidence_emitter=evidence_emitter).transform_prediction(
        inspection_input,
        prediction,
    )

    assert isinstance(output.inspection_evidence_record, InspectionEvidenceRecord)
    assert evidence_emitter.raw_results == [output.raw_inspection_result]
    assert output.inspection_evidence_record.raw_inspection_result == (
        output.raw_inspection_result
    )
    assert not hasattr(prediction, "inspection_evidence_record")
    assert not hasattr(prediction, "raw_inspection_result")


def test_deterministic_mock_inference_provider_does_not_wire_default_engine_path():
    provider = _deterministic_mock_provider_type()()
    inspection_input = make_input(input_id="mock-provider-default-path")
    prediction = provider.predict(inspection_input)
    engine = InspectionEngine()

    default_output = engine.inspect(inspection_input)
    default_result = default_output.raw_inspection_result

    assert not hasattr(engine, "provider")
    assert not hasattr(engine, "inference_provider")
    assert not hasattr(engine, "model")
    assert not hasattr(engine, "predict")
    assert default_result.examination_id != prediction.prediction_id
    assert default_result.examination_kind != INSPECTION_PREDICTION_KIND
    assert default_result.raw_measure_scale != PREDICTION_RAW_MEASURE_SCALE


def test_inspection_engine_remains_unwired_from_inference_provider():
    engine = InspectionEngine()

    assert not hasattr(engine, "predict")
    assert not hasattr(engine, "inference_provider")
    assert not hasattr(engine, "provider")
    assert not hasattr(engine, "model")


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
