from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping

from .errors import (
    InvalidInspectionInput,
    InvalidInspectionPrediction,
    InvalidInspectionResult,
    MissingContentHash,
    MissingInputIdentity,
    PartialInspectionPrediction,
    PartialInspectionResult,
    UnstabilizedInspectionInput,
)


STABILIZED_INPUT_KIND = "stabilized_inspection_input"
STABILIZED_INTAKE_STATUS = "stabilized"
RAW_MEASURE_KIND = "raw_anomaly_measure"
RAW_MEASURE_SCALE = "placeholder_hash_raw_0_100"
PLACEHOLDER_EXAMINATION_KIND = "deterministic_placeholder_examination"
INSPECTION_EVIDENCE_KIND = "inspection_raw_result"
INSPECTION_PREDICTION_KIND = "inspection_prediction"
PREDICTION_RAW_MEASURE_SCALE = "model_raw_anomaly_measure"
PADIM_RAW_MEASURE_SCALE = "padim_anomaly_map_max_v1"
IMAGE_BASELINE_EXAMINATION_KIND = "deterministic_local_image_baseline_v1"
IMAGE_BASELINE_RAW_SCALE = "local_contrast_raw_0_100"
VALID_EXAMINATION_KINDS = frozenset(
    {PLACEHOLDER_EXAMINATION_KIND, IMAGE_BASELINE_EXAMINATION_KIND}
)
VALID_RAW_MEASURE_SCALES = frozenset(
    {RAW_MEASURE_SCALE, IMAGE_BASELINE_RAW_SCALE}
)
_VALID_RAW_RESULT_EXAMINATION_KINDS = frozenset(
    {
        PLACEHOLDER_EXAMINATION_KIND,
        IMAGE_BASELINE_EXAMINATION_KIND,
        INSPECTION_PREDICTION_KIND,
    }
)
_VALID_RAW_RESULT_RAW_MEASURE_SCALES = frozenset(
    {
        RAW_MEASURE_SCALE,
        IMAGE_BASELINE_RAW_SCALE,
        PREDICTION_RAW_MEASURE_SCALE,
        PADIM_RAW_MEASURE_SCALE,
    }
)

_FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "abstain",
        "abstention",
        "calibrated_confidence",
        "confidence",
        "defect_label",
        "drift",
        "drift_assessment",
        "drift_signal",
        "ground_truth",
        "ground_truth_label",
        "outcome",
        "qualification",
        "qualified_outcome",
        "review",
        "review_routing",
        "route_to_review",
        "routing",
        "routing_decision",
        "target",
        "true_label",
        "trust",
        "trust_qualification",
    }
)

_FORBIDDEN_METADATA_TOKEN_SEQUENCES = (
    ("calibrated", "confidence"),
    ("defect", "label"),
    ("drift", "assessment"),
    ("drift", "signal"),
    ("ground", "truth"),
    ("qualified", "outcome"),
    ("review", "routing"),
    ("route", "to", "review"),
    ("routing", "decision"),
    ("true", "label"),
    ("trust", "qualification"),
)


class DefectJudgment(str, Enum):
    DEFECTIVE = "defective"
    NON_DEFECTIVE = "non_defective"


class InspectionJudgement(str, Enum):
    DEFECT = "defect"
    OK = "ok"

    DEFECTIVE = "defect"
    NON_DEFECTIVE = "ok"


@dataclass(frozen=True)
class StabilizedInspectionInput:
    input_id: str
    artifact_uri: str
    content_hash: str
    metadata: Mapping[str, str] = field(default_factory=dict)
    input_kind: str = STABILIZED_INPUT_KIND
    intake_status: str = STABILIZED_INTAKE_STATUS

    def __post_init__(self) -> None:
        if not self.input_id.strip():
            raise MissingInputIdentity("stabilized inspection input requires input_id")
        if not self.artifact_uri.strip():
            raise InvalidInspectionInput(
                "stabilized inspection input requires artifact_uri"
            )
        if not self.content_hash.strip():
            raise MissingContentHash(
                "stabilized inspection input requires content_hash"
            )
        if self.input_kind != STABILIZED_INPUT_KIND:
            raise InvalidInspectionInput(
                "inspection input must use the stabilized input contract"
            )
        if self.intake_status != STABILIZED_INTAKE_STATUS:
            raise UnstabilizedInspectionInput(
                "inspection input must already be stabilized by upstream intake"
            )
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True)
class InspectionInput:
    source_path: Path
    content_sha256: str
    media_type: str
    size_bytes: int

    def __post_init__(self) -> None:
        source_path = self.source_path.expanduser().resolve()
        if not self.content_sha256:
            raise InvalidInspectionInput("content_sha256 is required")
        if not self.media_type.startswith("image/"):
            raise InvalidInspectionInput("inspection inputs must be image media")
        if self.size_bytes <= 0:
            raise InvalidInspectionInput("inspection inputs must not be empty")
        object.__setattr__(self, "source_path", source_path)

    @property
    def input_id(self) -> str:
        return self.content_sha256


@dataclass(frozen=True)
class NormalizedBoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def __post_init__(self) -> None:
        values = (self.x_min, self.y_min, self.x_max, self.y_max)
        if not all(isfinite(value) for value in values):
            raise InvalidInspectionResult("localization coordinates must be finite")
        if not all(0.0 <= value <= 1.0 for value in values):
            raise InvalidInspectionResult(
                "localization coordinates must be normalized"
            )
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise InvalidInspectionResult(
                "localization minimums must precede maximums"
            )


@dataclass(frozen=True)
class DefectLocalization:
    region: NormalizedBoundingBox
    label: str | None = None
    localization_kind: str = "placeholder_suspected_region"

    def __post_init__(self) -> None:
        if self.label is not None and not self.label.strip():
            raise InvalidInspectionResult("localization labels must not be blank")
        if not self.localization_kind.strip():
            raise InvalidInspectionResult("localization kind is required")


@dataclass(frozen=True)
class RawAnomalyScore:
    value: float
    scale: str

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise InvalidInspectionResult("raw anomaly score must be finite")
        if not self.scale.strip():
            raise InvalidInspectionResult("raw anomaly score scale is required")


@dataclass(frozen=True)
class InspectionResult:
    inspection_input: InspectionInput
    judgment: DefectJudgment
    raw_anomaly_score: RawAnomalyScore
    localizations: tuple[DefectLocalization, ...] = ()
    method_id: str = ""
    method_version: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise InvalidInspectionResult("method_id is required")
        if self.method_version is not None and not self.method_version.strip():
            raise InvalidInspectionResult("method_version must not be blank")
        if self.judgment is DefectJudgment.DEFECTIVE and not self.localizations:
            raise InvalidInspectionResult("defective judgements require localization")
        if self.judgment is DefectJudgment.NON_DEFECTIVE and self.localizations:
            raise InvalidInspectionResult(
                "non-defective judgements must not include localizations"
            )
        normalized_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "metadata", normalized_metadata)


@dataclass(frozen=True)
class PlaceholderExamination:
    input_id: str
    examination_id: str
    judgement: InspectionJudgement
    raw_anomaly_measure: float
    localization: DefectLocalization | None
    examination_kind: str = PLACEHOLDER_EXAMINATION_KIND
    raw_measure_scale: str = RAW_MEASURE_SCALE

    def __post_init__(self) -> None:
        if not self.input_id.strip():
            raise InvalidInspectionResult("examination requires input_id")
        if not self.examination_id.strip():
            raise InvalidInspectionResult("examination requires examination_id")
        if not isfinite(self.raw_anomaly_measure):
            raise InvalidInspectionResult("raw anomaly measure must be finite")
        if self.examination_kind not in VALID_EXAMINATION_KINDS:
            raise InvalidInspectionResult(
                "inspection examination kind must remain explicit"
            )
        if self.raw_measure_scale not in VALID_RAW_MEASURE_SCALES:
            raise InvalidInspectionResult("raw anomaly measure scale is required")
        if self.judgement is InspectionJudgement.DEFECT and self.localization is None:
            raise PartialInspectionResult(
                "defect examinations require localization"
            )
        if self.judgement is InspectionJudgement.OK and self.localization is not None:
            raise PartialInspectionResult(
                "ok examinations must not include localization"
            )


@dataclass(frozen=True)
class InspectionPrediction:
    input_id: str
    prediction_id: str
    predicted_judgement: InspectionJudgement
    predicted_raw_anomaly_measure: float
    predicted_localization: DefectLocalization | None
    raw_measure_kind: str = RAW_MEASURE_KIND
    raw_measure_scale: str = PREDICTION_RAW_MEASURE_SCALE
    prediction_kind: str = INSPECTION_PREDICTION_KIND
    model_metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.input_id.strip():
            raise InvalidInspectionPrediction("prediction requires input_id")
        if not self.prediction_id.strip():
            raise InvalidInspectionPrediction("prediction requires prediction_id")
        if not isfinite(self.predicted_raw_anomaly_measure):
            raise InvalidInspectionPrediction(
                "prediction raw anomaly measure must be finite"
            )
        if self.raw_measure_kind != RAW_MEASURE_KIND:
            raise InvalidInspectionPrediction(
                "prediction measure must be explicitly marked raw"
            )
        if not self.raw_measure_scale.strip():
            raise InvalidInspectionPrediction(
                "prediction raw anomaly measure scale is required"
            )
        if not self.prediction_kind.strip():
            raise InvalidInspectionPrediction("prediction kind is required")
        if (
            self.predicted_judgement is InspectionJudgement.DEFECT
            and self.predicted_localization is None
        ):
            raise PartialInspectionPrediction(
                "defect predictions require localization"
            )
        if (
            self.predicted_judgement is InspectionJudgement.OK
            and self.predicted_localization is not None
        ):
            raise PartialInspectionPrediction(
                "ok predictions must not include localization"
            )
        object.__setattr__(
            self,
            "model_metadata",
            _freeze_metadata(self.model_metadata),
        )


@dataclass(frozen=True)
class RawInspectionResult:
    inspection_result_id: str
    input_id: str
    judgement: InspectionJudgement
    raw_anomaly_measure: float
    examination_id: str
    localization: DefectLocalization | None = None
    raw_measure_kind: str = RAW_MEASURE_KIND
    raw_measure_scale: str = RAW_MEASURE_SCALE
    examination_kind: str = PLACEHOLDER_EXAMINATION_KIND

    def __post_init__(self) -> None:
        if not self.inspection_result_id.strip():
            raise InvalidInspectionResult("inspection_result_id is required")
        if not self.input_id.strip():
            raise InvalidInspectionResult("raw inspection result requires input_id")
        if not self.examination_id.strip():
            raise InvalidInspectionResult(
                "raw inspection result requires examination_id"
            )
        if not isfinite(self.raw_anomaly_measure):
            raise InvalidInspectionResult("raw anomaly measure must be finite")
        if self.raw_measure_kind != RAW_MEASURE_KIND:
            raise InvalidInspectionResult(
                "raw anomaly measure must be explicitly marked raw"
            )
        if self.raw_measure_scale not in _VALID_RAW_RESULT_RAW_MEASURE_SCALES:
            raise InvalidInspectionResult("raw anomaly measure scale is required")
        if self.examination_kind not in _VALID_RAW_RESULT_EXAMINATION_KINDS:
            raise InvalidInspectionResult(
                "raw inspection result provenance kind must be explicit"
            )
        if self.judgement is InspectionJudgement.DEFECT and self.localization is None:
            raise PartialInspectionResult("defect results require localization")
        if self.judgement is InspectionJudgement.OK and self.localization is not None:
            raise PartialInspectionResult("ok results must not include localization")


@dataclass(frozen=True)
class InspectionEvidenceRecord:
    record_id: str
    input_id: str
    inspection_result_id: str
    raw_inspection_result: RawInspectionResult
    evidence_kind: str = INSPECTION_EVIDENCE_KIND

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise InvalidInspectionResult("inspection evidence record_id is required")
        if self.evidence_kind != INSPECTION_EVIDENCE_KIND:
            raise InvalidInspectionResult(
                "inspection evidence must preserve raw inspection results"
            )
        if self.input_id != self.raw_inspection_result.input_id:
            raise InvalidInspectionResult(
                "inspection evidence input_id must match the raw result"
            )
        if (
            self.inspection_result_id
            != self.raw_inspection_result.inspection_result_id
        ):
            raise InvalidInspectionResult(
                "inspection evidence must link to the raw result"
            )


@dataclass(frozen=True)
class InspectionEngineOutput:
    raw_inspection_result: RawInspectionResult
    inspection_evidence_record: InspectionEvidenceRecord

    def __post_init__(self) -> None:
        result = self.raw_inspection_result
        record = self.inspection_evidence_record
        if record.input_id != result.input_id:
            raise InvalidInspectionResult(
                "inspection output evidence must link to the input"
            )
        if record.inspection_result_id != result.inspection_result_id:
            raise InvalidInspectionResult(
                "inspection output evidence must link to the raw result"
            )
        if record.raw_inspection_result != result:
            raise InvalidInspectionResult(
                "inspection output evidence must preserve the raw result"
            )


def _freeze_metadata(metadata: Mapping[str, str]) -> Mapping[str, str]:
    normalized = dict(metadata)
    for key, value in normalized.items():
        if not isinstance(key, str) or not key.strip():
            raise InvalidInspectionInput("input metadata keys must be non-empty strings")
        if not isinstance(value, str):
            raise InvalidInspectionInput("input metadata values must be strings")
        if _is_forbidden_metadata_key(key):
            raise InvalidInspectionInput(
                "stabilized input metadata must not carry downstream domain fields"
            )
    return MappingProxyType(normalized)


def _is_forbidden_metadata_key(key: str) -> bool:
    normalized_key = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    if normalized_key in _FORBIDDEN_METADATA_KEYS:
        return True
    tokens = tuple(token for token in normalized_key.split("_") if token)
    return any(
        _contains_token_sequence(tokens, forbidden_sequence)
        for forbidden_sequence in _FORBIDDEN_METADATA_TOKEN_SEQUENCES
    )


def _contains_token_sequence(
    tokens: tuple[str, ...], forbidden_sequence: tuple[str, ...]
) -> bool:
    length = len(forbidden_sequence)
    return any(
        tokens[index : index + length] == forbidden_sequence
        for index in range(len(tokens) - length + 1)
    )
