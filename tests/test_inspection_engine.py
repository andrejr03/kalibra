from __future__ import annotations

import pytest

from src.inspection import (
    DefectJudgment,
    DefectLocalization,
    InspectionEngine,
    InspectionInput,
    InspectionResult,
    InvalidInspectionInput,
    InvalidInspectionResult,
    NormalizedBoundingBox,
    RawAnomalyScore,
)


class RecordingInspectionMethod:
    method_id = "recording-method"
    method_version = "1"

    def __init__(self, judgment: DefectJudgment) -> None:
        self.judgment = judgment
        self.seen_input: InspectionInput | None = None

    def inspect(self, inspection_input: InspectionInput) -> InspectionResult:
        self.seen_input = inspection_input
        localizations = ()
        if self.judgment is DefectJudgment.DEFECTIVE:
            localizations = (
                DefectLocalization(
                    region=NormalizedBoundingBox(
                        x_min=0.1,
                        y_min=0.2,
                        x_max=0.3,
                        y_max=0.4,
                    )
                ),
            )

        return InspectionResult(
            inspection_input=inspection_input,
            judgment=self.judgment,
            raw_anomaly_score=RawAnomalyScore(
                value=12.5,
                scale="method-specific-distance",
            ),
            localizations=localizations,
            method_id=self.method_id,
            method_version=self.method_version,
        )


def test_engine_prepares_stable_input_and_delegates_inspection(tmp_path):
    image_path = tmp_path / "part.png"
    image_path.write_bytes(b"stable visual input")
    method = RecordingInspectionMethod(DefectJudgment.DEFECTIVE)

    result = InspectionEngine(method=method).inspect_path(image_path)

    assert method.seen_input == result.inspection_input
    assert result.inspection_input.source_path == image_path.resolve()
    assert result.inspection_input.media_type == "image/png"
    assert result.inspection_input.size_bytes == len(b"stable visual input")
    assert (
        result.inspection_input.content_sha256
        == "e7c50cd20b95f55c43a283dc8382e24723c7d91cb337dfaebf7a1c27bb671d7d"
    )
    assert result.judgment is DefectJudgment.DEFECTIVE
    assert len(result.localizations) == 1
    assert result.raw_anomaly_score.value == 12.5


def test_engine_accepts_prepared_input_directly(tmp_path):
    image_path = tmp_path / "part.jpeg"
    image_path.write_bytes(b"prepared input")
    engine = InspectionEngine(
        method=RecordingInspectionMethod(DefectJudgment.NON_DEFECTIVE)
    )
    inspection_input = engine.input_preparer.prepare_path(image_path)

    result = engine.inspect(inspection_input)

    assert result.inspection_input == inspection_input
    assert result.judgment is DefectJudgment.NON_DEFECTIVE
    assert result.localizations == ()


def test_input_preparer_rejects_non_visual_files(tmp_path):
    text_path = tmp_path / "part.txt"
    text_path.write_text("not a visual input")

    with pytest.raises(InvalidInspectionInput):
        InspectionEngine(
            method=RecordingInspectionMethod(DefectJudgment.NON_DEFECTIVE)
        ).inspect_path(text_path)


def test_defective_results_require_localization(tmp_path):
    image_path = tmp_path / "part.png"
    image_path.write_bytes(b"stable visual input")
    inspection_input = InspectionEngine(
        method=RecordingInspectionMethod(DefectJudgment.NON_DEFECTIVE)
    ).input_preparer.prepare_path(image_path)

    with pytest.raises(InvalidInspectionResult):
        InspectionResult(
            inspection_input=inspection_input,
            judgment=DefectJudgment.DEFECTIVE,
            raw_anomaly_score=RawAnomalyScore(
                value=1.0,
                scale="method-specific-distance",
            ),
            method_id="method",
        )


def test_raw_anomaly_score_is_not_restricted_to_confidence_range():
    score = RawAnomalyScore(value=42.0, scale="method-specific-distance")

    assert score.value == 42.0


def test_engine_rejects_results_for_a_different_input(tmp_path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"first visual input")
    second.write_bytes(b"second visual input")
    engine = InspectionEngine(
        method=RecordingInspectionMethod(DefectJudgment.NON_DEFECTIVE)
    )
    other_input = engine.input_preparer.prepare_path(second)

    class MismatchedInspectionMethod(RecordingInspectionMethod):
        def inspect(self, inspection_input: InspectionInput) -> InspectionResult:
            return InspectionResult(
                inspection_input=other_input,
                judgment=DefectJudgment.NON_DEFECTIVE,
                raw_anomaly_score=RawAnomalyScore(
                    value=0.0,
                    scale="method-specific-distance",
                ),
                method_id=self.method_id,
                method_version=self.method_version,
            )

    with pytest.raises(InvalidInspectionResult):
        InspectionEngine(
            method=MismatchedInspectionMethod(DefectJudgment.NON_DEFECTIVE)
        ).inspect_path(first)
