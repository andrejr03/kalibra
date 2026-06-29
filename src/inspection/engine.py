from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .domain import (
    DefectLocalization,
    IMAGE_BASELINE_EXAMINATION_KIND,
    IMAGE_BASELINE_RAW_SCALE,
    INSPECTION_PREDICTION_KIND,
    InspectionEngineOutput,
    InspectionEvidenceRecord,
    InspectionJudgement,
    InspectionPrediction,
    NormalizedBoundingBox,
    PlaceholderExamination,
    RAW_MEASURE_KIND,
    RawInspectionResult,
    StabilizedInspectionInput,
)
from .errors import (
    EvidenceEmissionFailure,
    InspectionError,
    InspectionExaminationFailure,
    InvalidInspectionResult,
    InvalidInspectionPrediction,
    MalformedInspectionInput,
    NonReproducibleInspection,
    PartialInspectionPrediction,
)
from .interfaces import InspectionEvidenceEmitterProtocol, InspectionExaminer


@dataclass(frozen=True)
class DeterministicPlaceholderExaminer:
    examiner_id: str = "inspection-placeholder-hash-v1"

    def examine(
        self, inspection_input: StabilizedInspectionInput
    ) -> PlaceholderExamination:
        digest = _digest(
            {
                "artifact_uri": inspection_input.artifact_uri,
                "content_hash": inspection_input.content_hash,
                "examiner_id": self.examiner_id,
                "input_id": inspection_input.input_id,
                "input_kind": inspection_input.input_kind,
            }
        )
        raw_measure = round(_unit_interval(digest[:16]) * 100.0, 6)
        judgement = (
            InspectionJudgement.DEFECT
            if raw_measure >= 50.0
            else InspectionJudgement.OK
        )
        localization = (
            _localization_from_digest(digest)
            if judgement is InspectionJudgement.DEFECT
            else None
        )
        return PlaceholderExamination(
            input_id=inspection_input.input_id,
            examination_id=_stable_id(
                "placeholder-examination",
                {
                    "digest": digest,
                    "input_id": inspection_input.input_id,
                },
            ),
            judgement=judgement,
            raw_anomaly_measure=raw_measure,
            localization=localization,
        )


@dataclass(frozen=True)
class DeterministicImageBaselineExaminer:
    examiner_id: str = "inspection-image-baseline-pgm-v1"
    defect_threshold: float = 50.0
    anomaly_fraction: float = 0.5

    def examine(
        self, inspection_input: StabilizedInspectionInput
    ) -> PlaceholderExamination:
        path = _resolve_local_artifact_path(inspection_input.artifact_uri)
        if not path.exists() or not path.is_file():
            raise InspectionExaminationFailure(
                f"inspection artifact is missing or unreadable: {path}"
            )

        pixels, maxval = _read_pgm_p2(path)
        height = len(pixels)
        width = len(pixels[0])
        normalized_mean = sum(sum(row) for row in pixels) / (
            width * height * maxval
        )
        deviations = [
            [abs(value / maxval - normalized_mean) for value in row]
            for row in pixels
        ]
        max_deviation = max(max(row) for row in deviations)
        raw_measure = round(max_deviation * 100.0, 6)
        judgement = (
            InspectionJudgement.DEFECT
            if raw_measure >= self.defect_threshold
            else InspectionJudgement.OK
        )
        localization = (
            _localization_from_deviations(
                deviations,
                max_deviation,
                self.anomaly_fraction,
                width,
                height,
            )
            if judgement is InspectionJudgement.DEFECT
            else None
        )

        return PlaceholderExamination(
            input_id=inspection_input.input_id,
            examination_id=_stable_id(
                "image-baseline-examination",
                {
                    "examiner_id": self.examiner_id,
                    "input_id": inspection_input.input_id,
                    "pixels": pixels,
                    "maxval": maxval,
                },
            ),
            judgement=judgement,
            raw_anomaly_measure=raw_measure,
            localization=localization,
            examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
            raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
        )


@dataclass(frozen=True)
class InspectionEvidenceEmitter:
    emitter_id: str = "inspection-evidence-record-emitter-v1"

    def emit(self, raw_result: RawInspectionResult) -> InspectionEvidenceRecord:
        record_id = _stable_id(
            "inspection-evidence-record",
            {
                "emitter_id": self.emitter_id,
                "input_id": raw_result.input_id,
                "inspection_result_id": raw_result.inspection_result_id,
                "raw_measure_kind": raw_result.raw_measure_kind,
                "raw_anomaly_measure": raw_result.raw_anomaly_measure,
            },
        )
        return InspectionEvidenceRecord(
            record_id=record_id,
            input_id=raw_result.input_id,
            inspection_result_id=raw_result.inspection_result_id,
            raw_inspection_result=raw_result,
        )


@dataclass(frozen=True)
class InspectionEngine:
    examiner: InspectionExaminer = field(
        default_factory=DeterministicPlaceholderExaminer
    )
    evidence_emitter: InspectionEvidenceEmitterProtocol = field(
        default_factory=InspectionEvidenceEmitter
    )

    def inspect(
        self, inspection_input: StabilizedInspectionInput
    ) -> InspectionEngineOutput:
        self._validate_stabilized_input(inspection_input)

        first_output = self._inspect_once(inspection_input)
        second_output = self._inspect_once(inspection_input)
        if first_output != second_output:
            raise NonReproducibleInspection(
                "fixed inspection input produced divergent raw outputs"
            )
        return first_output

    def transform_prediction(
        self,
        inspection_input: StabilizedInspectionInput,
        prediction: InspectionPrediction,
    ) -> InspectionEngineOutput:
        self._validate_stabilized_input(inspection_input)
        self._validate_prediction_for_input(inspection_input, prediction)

        raw_result = self._assemble_result_from_prediction(
            inspection_input,
            prediction,
        )
        evidence_record = self._emit_evidence(raw_result)
        return InspectionEngineOutput(
            raw_inspection_result=raw_result,
            inspection_evidence_record=evidence_record,
        )

    def _validate_stabilized_input(
        self, inspection_input: StabilizedInspectionInput
    ) -> None:
        if not isinstance(inspection_input, StabilizedInspectionInput):
            raise MalformedInspectionInput(
                "inspection engine only accepts StabilizedInspectionInput"
            )

    def _validate_prediction_for_input(
        self,
        inspection_input: StabilizedInspectionInput,
        prediction: InspectionPrediction,
    ) -> None:
        if not isinstance(prediction, InspectionPrediction):
            raise InvalidInspectionPrediction(
                "inspection prediction transformation requires InspectionPrediction"
            )
        if not isinstance(prediction.input_id, str) or not prediction.input_id.strip():
            raise InvalidInspectionPrediction("prediction requires input_id")
        if (
            not isinstance(prediction.prediction_id, str)
            or not prediction.prediction_id.strip()
        ):
            raise InvalidInspectionPrediction("prediction requires prediction_id")
        if prediction.input_id != inspection_input.input_id:
            raise InvalidInspectionPrediction(
                "inspection prediction must reference the inspected input"
            )
        if prediction.prediction_kind != INSPECTION_PREDICTION_KIND:
            raise InvalidInspectionPrediction(
                "inspection prediction kind is not supported"
            )
        if prediction.raw_measure_kind != RAW_MEASURE_KIND:
            raise InvalidInspectionPrediction(
                "prediction measure must be explicitly marked raw"
            )
        if not isinstance(
            prediction.predicted_raw_anomaly_measure,
            (float, int),
        ) or not isfinite(prediction.predicted_raw_anomaly_measure):
            raise InvalidInspectionPrediction(
                "prediction raw anomaly measure must be finite"
            )
        if (
            not isinstance(prediction.raw_measure_scale, str)
            or not prediction.raw_measure_scale.strip()
        ):
            raise InvalidInspectionPrediction(
                "prediction raw anomaly measure scale is required"
            )
        if not isinstance(prediction.prediction_kind, str):
            raise InvalidInspectionPrediction("prediction kind is required")
        if not isinstance(prediction.predicted_judgement, InspectionJudgement):
            raise InvalidInspectionPrediction(
                "prediction judgement must use InspectionJudgement"
            )
        if (
            prediction.predicted_localization is not None
            and not isinstance(prediction.predicted_localization, DefectLocalization)
        ):
            raise InvalidInspectionPrediction(
                "prediction localization must use DefectLocalization"
            )
        if (
            prediction.predicted_judgement is InspectionJudgement.DEFECT
            and prediction.predicted_localization is None
        ):
            raise PartialInspectionPrediction(
                "defect predictions require localization"
            )
        if (
            prediction.predicted_judgement is InspectionJudgement.OK
            and prediction.predicted_localization is not None
        ):
            raise PartialInspectionPrediction(
                "ok predictions must not include localization"
            )

    def _inspect_once(
        self, inspection_input: StabilizedInspectionInput
    ) -> InspectionEngineOutput:
        examination = self._examine(inspection_input)
        raw_result = self._assemble_result(inspection_input, examination)
        evidence_record = self._emit_evidence(raw_result)
        return InspectionEngineOutput(
            raw_inspection_result=raw_result,
            inspection_evidence_record=evidence_record,
        )

    def _examine(
        self, inspection_input: StabilizedInspectionInput
    ) -> PlaceholderExamination:
        try:
            examination = self.examiner.examine(inspection_input)
        except InspectionError:
            raise
        except Exception as exc:
            raise InspectionExaminationFailure(
                "inspection examination failed"
            ) from exc
        if not isinstance(examination, PlaceholderExamination):
            raise InspectionExaminationFailure(
                "inspection examination must return PlaceholderExamination"
            )
        if examination.input_id != inspection_input.input_id:
            raise InvalidInspectionResult(
                "inspection examination must reference the inspected input"
            )
        return examination

    def _assemble_result(
        self,
        inspection_input: StabilizedInspectionInput,
        examination: PlaceholderExamination,
    ) -> RawInspectionResult:
        result_id = _stable_id(
            "raw-inspection-result",
            {
                "examination_id": examination.examination_id,
                "input_id": inspection_input.input_id,
                "judgement": examination.judgement.value,
                "raw_anomaly_measure": examination.raw_anomaly_measure,
            },
        )
        try:
            return RawInspectionResult(
                inspection_result_id=result_id,
                input_id=inspection_input.input_id,
                judgement=examination.judgement,
                localization=examination.localization,
                raw_anomaly_measure=examination.raw_anomaly_measure,
                examination_id=examination.examination_id,
                raw_measure_scale=examination.raw_measure_scale,
                examination_kind=examination.examination_kind,
            )
        except InspectionError:
            raise
        except Exception as exc:
            raise InvalidInspectionResult("raw inspection result failed") from exc

    def _assemble_result_from_prediction(
        self,
        inspection_input: StabilizedInspectionInput,
        prediction: InspectionPrediction,
    ) -> RawInspectionResult:
        result_id = _stable_id(
            "raw-inspection-result",
            {
                "input_id": inspection_input.input_id,
                "prediction_id": prediction.prediction_id,
                "prediction_kind": prediction.prediction_kind,
                "predicted_judgement": prediction.predicted_judgement.value,
                "predicted_raw_anomaly_measure": (
                    prediction.predicted_raw_anomaly_measure
                ),
                "raw_measure_kind": prediction.raw_measure_kind,
                "raw_measure_scale": prediction.raw_measure_scale,
            },
        )
        try:
            return RawInspectionResult(
                inspection_result_id=result_id,
                input_id=inspection_input.input_id,
                judgement=prediction.predicted_judgement,
                localization=prediction.predicted_localization,
                raw_anomaly_measure=prediction.predicted_raw_anomaly_measure,
                examination_id=prediction.prediction_id,
                raw_measure_kind=prediction.raw_measure_kind,
                raw_measure_scale=prediction.raw_measure_scale,
                examination_kind=prediction.prediction_kind,
            )
        except InspectionError:
            raise
        except Exception as exc:
            raise InvalidInspectionResult("raw inspection result failed") from exc

    def _emit_evidence(
        self, raw_result: RawInspectionResult
    ) -> InspectionEvidenceRecord:
        try:
            record = self.evidence_emitter.emit(raw_result)
        except InspectionError:
            raise
        except Exception as exc:
            raise EvidenceEmissionFailure(
                "inspection evidence record emission failed"
            ) from exc
        if not isinstance(record, InspectionEvidenceRecord):
            raise EvidenceEmissionFailure(
                "inspection evidence emission must return InspectionEvidenceRecord"
            )
        if record.raw_inspection_result != raw_result:
            raise EvidenceEmissionFailure(
                "inspection evidence record must preserve the raw result"
            )
        return record


def _localization_from_digest(digest: str) -> DefectLocalization:
    x_min = round(0.05 + _unit_interval(digest[16:24]) * 0.70, 6)
    y_min = round(0.05 + _unit_interval(digest[24:32]) * 0.72, 6)
    width = 0.20
    height = 0.18
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=round(x_min + width, 6),
            y_max=round(y_min + height, 6),
        )
    )


def _localization_from_deviations(
    deviations: list[list[float]],
    max_deviation: float,
    anomaly_fraction: float,
    width: int,
    height: int,
) -> DefectLocalization:
    threshold = anomaly_fraction * max_deviation
    cols = [
        x
        for y in range(height)
        for x in range(width)
        if deviations[y][x] >= threshold
    ]
    rows = [
        y
        for y in range(height)
        for x in range(width)
        if deviations[y][x] >= threshold
    ]
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=round(min(cols) / width, 6),
            y_min=round(min(rows) / height, 6),
            x_max=round((max(cols) + 1) / width, 6),
            y_max=round((max(rows) + 1) / height, 6),
        ),
        localization_kind="local_contrast_suspected_region",
    )


def _unit_interval(hex_fragment: str) -> float:
    if not hex_fragment:
        raise InspectionExaminationFailure("digest fragment is required")
    return int(hex_fragment, 16) / float((16 ** len(hex_fragment)) - 1)


def _resolve_local_artifact_path(artifact_uri: str) -> Path:
    parsed = urlparse(artifact_uri)
    if parsed.scheme == "":
        return Path(artifact_uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    raise InspectionExaminationFailure(
        "image baseline only reads local file artifacts, "
        f"not '{parsed.scheme}://' references"
    )


def _read_pgm_p2(path: Path) -> tuple[list[list[int]], int]:
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise InspectionExaminationFailure(
            f"inspection artifact could not be read as ascii PGM: {path}"
        ) from exc
    tokens = _pgm_tokens(text)
    try:
        magic = next(tokens)
        if magic != "P2":
            raise InspectionExaminationFailure(
                "image baseline supports only ascii PGM (P2) artifacts"
            )
        width = int(next(tokens))
        height = int(next(tokens))
        maxval = int(next(tokens))
    except StopIteration as exc:
        raise InspectionExaminationFailure("PGM header is incomplete") from exc
    except ValueError as exc:
        raise InspectionExaminationFailure("PGM header is not numeric") from exc
    if width <= 0 or height <= 0 or maxval <= 0:
        raise InspectionExaminationFailure(
            "PGM width, height and maxval must be positive"
        )
    pixels: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            try:
                value = int(next(tokens))
            except StopIteration as exc:
                raise InspectionExaminationFailure(
                    "PGM pixel data is truncated"
                ) from exc
            except ValueError as exc:
                raise InspectionExaminationFailure(
                    "PGM pixel data is not numeric"
                ) from exc
            if value < 0 or value > maxval:
                raise InspectionExaminationFailure(
                    "PGM pixel value is out of range"
                )
            row.append(value)
        pixels.append(row)
    return pixels, maxval


def _pgm_tokens(text: str):
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0]
        for token in line.split():
            yield token


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
