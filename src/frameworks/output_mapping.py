from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType


PADIM_OUTPUT_MAPPING_CONTRACT_ID = "kalibra-padim-onnx-output-mapping-v1"
PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID = "kalibra-onnx-placeholder-output-mapping-v1"
OUTPUT_MAPPING_CONTRACT_ID = PADIM_OUTPUT_MAPPING_CONTRACT_ID
MAPPING_VERSION = "1"
PADIM_EXPECTED_OUTPUT_COUNT = 4
PADIM_PATCH_DISTANCES_SHAPE = (1, 64)
PADIM_ANOMALY_MAP_SHAPE = (1, 64, 64)
PADIM_RAW_MEASURE_SHAPE = (1,)
PADIM_ARGMAX_REGION_SHAPE = (1, 4)
PADIM_OUTPUT_DTYPE = "float64"
PLACEHOLDER_EXPECTED_OUTPUT_COUNT = 1
PLACEHOLDER_EXPECTED_OUTPUT_SHAPE = (1,)
PLACEHOLDER_EXPECTED_OUTPUT_DTYPE = "float32"
EXPECTED_OUTPUT_COUNT = PLACEHOLDER_EXPECTED_OUTPUT_COUNT
EXPECTED_OUTPUT_SHAPE = PLACEHOLDER_EXPECTED_OUTPUT_SHAPE
EXPECTED_OUTPUT_DTYPE = PLACEHOLDER_EXPECTED_OUTPUT_DTYPE
ACCEPTED_RAW_MEASURE_RANGE = (0.0, 100.0)
PADIM_RAW_MEASURE_SCALE = "padim_anomaly_map_max_v1"
PLACEHOLDER_RAW_MEASURE_SCALE = "placeholder_output_raw_0_100"
RAW_MEASURE_SCALE = PADIM_RAW_MEASURE_SCALE
PADIM_MAPPING_SEMANTICS = (
    "padim_float64_raw_measure_and_argmax_region_to_raw_localized_prediction"
)
PLACEHOLDER_MAPPING_SEMANTICS = "single_float32_raw_measure_to_placeholder_status_and_region"
MAPPING_SEMANTICS = PADIM_MAPPING_SEMANTICS
DEFAULT_DEFECT_THRESHOLD = 50.0
PREDICTED_STATUS_DEFECT = "defect"
PREDICTED_STATUS_OK = "ok"
PADIM_LOCALIZATION_KIND = "padim_raw_anomaly_map_argmax_region_v1"
PLACEHOLDER_LOCALIZATION_KIND = "onnx_placeholder_suspected_region"
LOCALIZATION_KIND = PADIM_LOCALIZATION_KIND


class OutputMappingError(ValueError):
    """Raised when model output cannot satisfy the governed mapping contract."""


@dataclass(frozen=True)
class MappedLocalization:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    localization_kind: str = LOCALIZATION_KIND

    def __post_init__(self) -> None:
        values = (self.x_min, self.y_min, self.x_max, self.y_max)
        if not all(isfinite(value) for value in values):
            raise OutputMappingError("mapped localization bounds must be finite")
        if not all(0.0 <= value <= 1.0 for value in values):
            raise OutputMappingError("mapped localization bounds must be normalized")
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise OutputMappingError("mapped localization bounds are not ordered")
        if not self.localization_kind.strip():
            raise OutputMappingError("mapped localization kind is required")


@dataclass(frozen=True)
class MappedModelOutput:
    predicted_status: str
    raw_anomaly_measure: float
    localization: MappedLocalization | None
    localization_kind: str | None
    model_metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.predicted_status not in (
            PREDICTED_STATUS_DEFECT,
            PREDICTED_STATUS_OK,
        ):
            raise OutputMappingError("mapped status is incompatible")
        if not isfinite(self.raw_anomaly_measure):
            raise OutputMappingError("mapped raw measure must be finite")
        metadata = dict(self.model_metadata)
        for key, value in metadata.items():
            if not isinstance(key, str) or not key.strip():
                raise OutputMappingError("mapping metadata keys must be strings")
            if not isinstance(value, str):
                raise OutputMappingError("mapping metadata values must be strings")
        if metadata.get("raw_measure_scale") == PLACEHOLDER_RAW_MEASURE_SCALE:
            lower, upper = ACCEPTED_RAW_MEASURE_RANGE
            if (
                self.raw_anomaly_measure < lower
                or self.raw_anomaly_measure > upper
            ):
                raise OutputMappingError("mapped raw measure is outside contract range")
        if self.predicted_status == PREDICTED_STATUS_DEFECT:
            if self.localization is None:
                raise OutputMappingError("mapped defect status requires localization")
            if self.localization_kind != self.localization.localization_kind:
                raise OutputMappingError("mapped localization kind mismatch")
        if self.predicted_status == PREDICTED_STATUS_OK:
            if self.localization is not None or self.localization_kind is not None:
                raise OutputMappingError("mapped ok status must not localize")

        object.__setattr__(self, "model_metadata", MappingProxyType(metadata))


def map_onnx_outputs(
    outputs: object,
    *,
    input_id: str,
    content_hash: str,
    defect_threshold: float = DEFAULT_DEFECT_THRESHOLD,
    preprocessing_contract_id: str | None = None,
) -> MappedModelOutput:
    raw_measure, output_dtype, output_shape = _raw_measure_from_outputs(outputs)
    if not isinstance(input_id, str) or not input_id.strip():
        raise OutputMappingError("mapping requires input_id")
    if not isinstance(content_hash, str) or not content_hash.strip():
        raise OutputMappingError("mapping requires content_hash")
    if not isfinite(defect_threshold):
        raise OutputMappingError("mapping status rule must be finite")
    if preprocessing_contract_id is not None and (
        not isinstance(preprocessing_contract_id, str)
        or not preprocessing_contract_id.strip()
    ):
        raise OutputMappingError("preprocessing contract id must be a string")

    predicted_status = (
        PREDICTED_STATUS_DEFECT
        if raw_measure >= defect_threshold
        else PREDICTED_STATUS_OK
    )
    localization = (
        _placeholder_localization(input_id, content_hash)
        if predicted_status == PREDICTED_STATUS_DEFECT
        else None
    )
    localization_kind = (
        localization.localization_kind if localization is not None else None
    )
    return MappedModelOutput(
        predicted_status=predicted_status,
        raw_anomaly_measure=raw_measure,
        localization=localization,
        localization_kind=localization_kind,
        model_metadata=_mapping_metadata(
            output_dtype=output_dtype,
            output_shape=output_shape,
            preprocessing_contract_id=preprocessing_contract_id,
        ),
    )


def map_padim_onnx_outputs(
    outputs: object,
    *,
    input_id: str,
    content_hash: str,
    feature_extraction_contract_id: str,
) -> MappedModelOutput:
    (
        patch_distances,
        anomaly_map,
        raw_measure,
        argmax_region,
    ) = _padim_values_from_outputs(outputs)
    if not isinstance(input_id, str) or not input_id.strip():
        raise OutputMappingError("mapping requires input_id")
    if not isinstance(content_hash, str) or not content_hash.strip():
        raise OutputMappingError("mapping requires content_hash")
    if (
        not isinstance(feature_extraction_contract_id, str)
        or not feature_extraction_contract_id.strip()
    ):
        raise OutputMappingError("feature extraction contract id must be a string")

    localization = MappedLocalization(
        x_min=round(float(argmax_region[0]), 6),
        y_min=round(float(argmax_region[1]), 6),
        x_max=round(float(argmax_region[2]), 6),
        y_max=round(float(argmax_region[3]), 6),
        localization_kind=PADIM_LOCALIZATION_KIND,
    )
    return MappedModelOutput(
        predicted_status=PREDICTED_STATUS_DEFECT,
        raw_anomaly_measure=float(raw_measure[0]),
        localization=localization,
        localization_kind=localization.localization_kind,
        model_metadata=_padim_mapping_metadata(
            patch_distances_shape=patch_distances.shape,
            anomaly_map_shape=anomaly_map.shape,
            raw_measure_shape=raw_measure.shape,
            argmax_region_shape=argmax_region.shape,
            output_dtype=str(raw_measure.dtype),
            feature_extraction_contract_id=feature_extraction_contract_id,
        ),
    )


def _raw_measure_from_outputs(
    outputs: object,
) -> tuple[float, str, tuple[int, ...]]:
    output_values = _validate_output_count(outputs)
    array = _numpy().asarray(output_values[0])
    output_shape = tuple(int(dimension) for dimension in array.shape)
    if output_shape != EXPECTED_OUTPUT_SHAPE:
        raise OutputMappingError("output tensor shape is incompatible")
    output_dtype = str(array.dtype)
    if output_dtype != EXPECTED_OUTPUT_DTYPE:
        raise OutputMappingError("output tensor dtype is incompatible")

    raw_measure = float(array.reshape(-1)[0])
    if not isfinite(raw_measure):
        raise OutputMappingError("output raw measure must be finite")
    lower, upper = ACCEPTED_RAW_MEASURE_RANGE
    if raw_measure < lower or raw_measure > upper:
        raise OutputMappingError("output raw measure is outside contract range")
    return round(raw_measure, 6), output_dtype, output_shape


def _validate_output_count(outputs: object) -> Sequence[object]:
    if isinstance(outputs, (str, bytes, bytearray)) or not isinstance(
        outputs, Sequence
    ):
        raise OutputMappingError("output container is incompatible")
    if len(outputs) != EXPECTED_OUTPUT_COUNT:
        raise OutputMappingError("output count is incompatible")
    return outputs


def _padim_values_from_outputs(
    outputs: object,
):
    output_values = _validate_padim_output_count(outputs)
    numpy = _numpy()
    patch_distances = numpy.asarray(output_values[0])
    anomaly_map = numpy.asarray(output_values[1])
    raw_measure = numpy.asarray(output_values[2])
    argmax_region = numpy.asarray(output_values[3])

    _validate_array_contract(
        patch_distances,
        expected_shape=PADIM_PATCH_DISTANCES_SHAPE,
        expected_dtype=PADIM_OUTPUT_DTYPE,
        label="patch distances",
    )
    _validate_array_contract(
        anomaly_map,
        expected_shape=PADIM_ANOMALY_MAP_SHAPE,
        expected_dtype=PADIM_OUTPUT_DTYPE,
        label="anomaly map",
    )
    _validate_array_contract(
        raw_measure,
        expected_shape=PADIM_RAW_MEASURE_SHAPE,
        expected_dtype=PADIM_OUTPUT_DTYPE,
        label="raw measure",
    )
    _validate_array_contract(
        argmax_region,
        expected_shape=PADIM_ARGMAX_REGION_SHAPE,
        expected_dtype=PADIM_OUTPUT_DTYPE,
        label="argmax region",
    )
    if not isfinite(float(raw_measure.reshape(-1)[0])):
        raise OutputMappingError("output raw measure must be finite")
    if not all(isfinite(float(value)) for value in argmax_region.reshape(-1)):
        raise OutputMappingError("output localization must be finite")
    return (
        patch_distances,
        anomaly_map,
        raw_measure.reshape(-1),
        argmax_region.reshape(-1),
    )


def _validate_padim_output_count(outputs: object) -> Sequence[object]:
    if isinstance(outputs, (str, bytes, bytearray)) or not isinstance(
        outputs, Sequence
    ):
        raise OutputMappingError("output container is incompatible")
    if len(outputs) != PADIM_EXPECTED_OUTPUT_COUNT:
        raise OutputMappingError("output count is incompatible")
    return outputs


def _validate_array_contract(
    array: object,
    *,
    expected_shape: tuple[int, ...],
    expected_dtype: str,
    label: str,
) -> None:
    shape = tuple(int(dimension) for dimension in array.shape)
    if shape != expected_shape:
        raise OutputMappingError(f"{label} output tensor shape is incompatible")
    if str(array.dtype) != expected_dtype:
        raise OutputMappingError(f"{label} output tensor dtype is incompatible")


def _mapping_metadata(
    *,
    output_dtype: str,
    output_shape: tuple[int, ...],
    preprocessing_contract_id: str | None,
) -> dict[str, str]:
    metadata = {
        "output_mapping_contract_id": PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID,
        "output_mapping_version": MAPPING_VERSION,
        "output_count": str(PLACEHOLDER_EXPECTED_OUTPUT_COUNT),
        "output_shape": _shape_text(output_shape),
        "output_dtype": output_dtype,
        "raw_measure_scale": PLACEHOLDER_RAW_MEASURE_SCALE,
        "mapping_semantics": PLACEHOLDER_MAPPING_SEMANTICS,
    }
    if preprocessing_contract_id is not None:
        metadata["preprocessing_contract_id"] = preprocessing_contract_id
    return metadata


def _padim_mapping_metadata(
    *,
    patch_distances_shape: tuple[int, ...],
    anomaly_map_shape: tuple[int, ...],
    raw_measure_shape: tuple[int, ...],
    argmax_region_shape: tuple[int, ...],
    output_dtype: str,
    feature_extraction_contract_id: str,
) -> dict[str, str]:
    return {
        "output_mapping_contract_id": PADIM_OUTPUT_MAPPING_CONTRACT_ID,
        "output_mapping_version": MAPPING_VERSION,
        "output_count": str(PADIM_EXPECTED_OUTPUT_COUNT),
        "patch_mahalanobis_distances_shape": _shape_text(patch_distances_shape),
        "anomaly_map_shape": _shape_text(anomaly_map_shape),
        "raw_measure_shape": _shape_text(raw_measure_shape),
        "argmax_region_shape": _shape_text(argmax_region_shape),
        "output_dtype": output_dtype,
        "raw_measure_scale": PADIM_RAW_MEASURE_SCALE,
        "mapping_semantics": PADIM_MAPPING_SEMANTICS,
        "localization_kind": PADIM_LOCALIZATION_KIND,
        "feature_extraction_contract_id": feature_extraction_contract_id,
    }


def _placeholder_localization(input_id: str, content_hash: str) -> MappedLocalization:
    digest = _digest(
        {
            "content_hash": content_hash,
            "input_id": input_id,
            "localization": "onnx-placeholder-boundary",
        }
    )
    width = 0.2
    height = 0.18
    x_min = round(0.05 + _unit_interval(digest[0:8]) * (0.95 - width), 6)
    y_min = round(0.05 + _unit_interval(digest[8:16]) * (0.95 - height), 6)
    return MappedLocalization(
        x_min=x_min,
        y_min=y_min,
        x_max=round(x_min + width, 6),
        y_max=round(y_min + height, 6),
        localization_kind=PLACEHOLDER_LOCALIZATION_KIND,
    )


def _digest(payload: Mapping[str, object]) -> str:
    import json
    from hashlib import sha256

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _unit_interval(hex_fragment: str) -> float:
    return int(hex_fragment, 16) / float((16 ** len(hex_fragment)) - 1)


def _shape_text(shape: tuple[int, ...]) -> str:
    return "x".join(str(dimension) for dimension in shape)


def _numpy() -> object:
    try:
        import numpy
    except ImportError as exc:
        raise OutputMappingError(
            "output mapping requires numpy for tensor validation"
        ) from exc
    return numpy


__all__ = [
    "ACCEPTED_RAW_MEASURE_RANGE",
    "DEFAULT_DEFECT_THRESHOLD",
    "EXPECTED_OUTPUT_COUNT",
    "EXPECTED_OUTPUT_DTYPE",
    "EXPECTED_OUTPUT_SHAPE",
    "LOCALIZATION_KIND",
    "MAPPING_SEMANTICS",
    "MAPPING_VERSION",
    "OUTPUT_MAPPING_CONTRACT_ID",
    "PADIM_ARGMAX_REGION_SHAPE",
    "PADIM_ANOMALY_MAP_SHAPE",
    "PADIM_EXPECTED_OUTPUT_COUNT",
    "PADIM_LOCALIZATION_KIND",
    "PADIM_MAPPING_SEMANTICS",
    "PADIM_OUTPUT_DTYPE",
    "PADIM_OUTPUT_MAPPING_CONTRACT_ID",
    "PADIM_PATCH_DISTANCES_SHAPE",
    "PADIM_RAW_MEASURE_SCALE",
    "PADIM_RAW_MEASURE_SHAPE",
    "PLACEHOLDER_EXPECTED_OUTPUT_COUNT",
    "PLACEHOLDER_EXPECTED_OUTPUT_DTYPE",
    "PLACEHOLDER_EXPECTED_OUTPUT_SHAPE",
    "PLACEHOLDER_LOCALIZATION_KIND",
    "PLACEHOLDER_MAPPING_SEMANTICS",
    "PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID",
    "PLACEHOLDER_RAW_MEASURE_SCALE",
    "PREDICTED_STATUS_DEFECT",
    "PREDICTED_STATUS_OK",
    "RAW_MEASURE_SCALE",
    "MappedLocalization",
    "MappedModelOutput",
    "OutputMappingError",
    "map_padim_onnx_outputs",
    "map_onnx_outputs",
]
