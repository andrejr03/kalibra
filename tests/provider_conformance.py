from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from math import isfinite
from types import MappingProxyType

from src.inspection import (
    INSPECTION_PREDICTION_KIND,
    RAW_MEASURE_KIND,
    DefectLocalization,
    InspectionEngine,
    InspectionEngineOutput,
    InspectionEvidenceRecord,
    InspectionInferenceProvider,
    InspectionJudgement,
    InspectionPrediction,
    NormalizedBoundingBox,
    RawInspectionResult,
    StabilizedInspectionInput,
)


DOWNSTREAM_FIELD_NAMES = frozenset(
    {
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
)
FORBIDDEN_METADATA_KEY_TOKENS = (
    ("calibrated", "confidence"),
    ("drift",),
    ("evaluation",),
    ("ground", "truth"),
    ("qualified", "outcome"),
    ("review",),
    ("review", "routing"),
    ("routing",),
    ("trust",),
    ("trust", "qualification"),
)
RUNTIME_STATE_TYPE_TOKENS = frozenset(
    {
        "device",
        "executionprovider",
        "framework",
        "handle",
        "interpreter",
        "model",
        "module",
        "onnx",
        "openvino",
        "provider",
        "runtime",
        "session",
        "tensorflow",
        "tensor",
        "torch",
    }
)
PREDICTION_GRAPH_TYPES = frozenset(
    {
        DefectLocalization,
        InspectionJudgement,
        InspectionPrediction,
        MappingProxyType,
        NormalizedBoundingBox,
        dict,
    }
)
CANONICAL_OUTPUT_GRAPH_TYPES = frozenset(
    {
        DefectLocalization,
        InspectionEngineOutput,
        InspectionEvidenceRecord,
        InspectionJudgement,
        NormalizedBoundingBox,
        RawInspectionResult,
    }
)
PRIMITIVE_TYPES = (str, int, float, bool, type(None))


@dataclass(frozen=True)
class ProviderConformanceCase:
    name: str
    provider_factory: Callable[[], InspectionInferenceProvider]
    input_factory: Callable[[], StabilizedInspectionInput]

    def make_provider(self) -> InspectionInferenceProvider:
        return self.provider_factory()

    def make_input(self) -> StabilizedInspectionInput:
        inspection_input = self.input_factory()
        assert isinstance(inspection_input, StabilizedInspectionInput)
        return inspection_input


def assert_provider_conforms_to_prediction_contract(
    case: ProviderConformanceCase,
) -> None:
    provider = case.make_provider()
    inspection_input = case.make_input()

    assert callable(getattr(provider, "predict", None))
    prediction = provider.predict(inspection_input)

    assert type(prediction) is InspectionPrediction
    assert not isinstance(prediction, RawInspectionResult)
    assert prediction.input_id == inspection_input.input_id
    assert prediction.prediction_id.strip()
    assert prediction.predicted_judgement in {
        InspectionJudgement.DEFECT,
        InspectionJudgement.OK,
    }
    assert isfinite(prediction.predicted_raw_anomaly_measure)
    assert prediction.raw_measure_kind == RAW_MEASURE_KIND
    assert prediction.raw_measure_scale.strip()
    assert prediction.prediction_kind == INSPECTION_PREDICTION_KIND
    assert set(_field_names(InspectionPrediction)).isdisjoint(
        DOWNSTREAM_FIELD_NAMES
    )
    _assert_prediction_localization_matches_judgement(prediction)
    _assert_descriptive_metadata_only(prediction.model_metadata)
    _assert_graph_contains_only(
        prediction,
        allowed_types=PREDICTION_GRAPH_TYPES,
        graph_name=f"{case.name} prediction",
    )

    output = InspectionEngine().transform_prediction(inspection_input, prediction)
    assert type(output) is InspectionEngineOutput
    assert type(output.raw_inspection_result) is RawInspectionResult
    assert type(output.inspection_evidence_record) is InspectionEvidenceRecord


def assert_provider_deterministic_replay(case: ProviderConformanceCase) -> None:
    inspection_input = case.make_input()
    provider = case.make_provider()

    first_prediction = provider.predict(inspection_input)
    second_prediction = provider.predict(inspection_input)
    separate_provider_prediction = case.make_provider().predict(inspection_input)

    assert first_prediction == second_prediction
    assert first_prediction == separate_provider_prediction
    assert first_prediction.predicted_raw_anomaly_measure == (
        second_prediction.predicted_raw_anomaly_measure
    )
    assert first_prediction.predicted_localization == (
        second_prediction.predicted_localization
    )
    assert first_prediction.model_metadata == second_prediction.model_metadata

    engine = InspectionEngine()
    first_output = engine.transform_prediction(inspection_input, first_prediction)
    second_output = engine.transform_prediction(inspection_input, second_prediction)

    assert first_output.raw_inspection_result == second_output.raw_inspection_result
    assert first_output.raw_inspection_result.raw_anomaly_measure == (
        second_output.raw_inspection_result.raw_anomaly_measure
    )
    assert first_output.raw_inspection_result.localization == (
        second_output.raw_inspection_result.localization
    )
    assert first_output.inspection_evidence_record == (
        second_output.inspection_evidence_record
    )
    assert first_output == second_output


def assert_provider_boundary_isolation(case: ProviderConformanceCase) -> None:
    provider = case.make_provider()
    inspection_input = case.make_input()
    prediction = provider.predict(inspection_input)
    output = InspectionEngine().transform_prediction(inspection_input, prediction)

    _assert_object_absent(prediction, provider, f"{case.name} prediction")
    _assert_object_absent(output, provider, f"{case.name} output")
    _assert_no_values_of_type(
        prediction,
        forbidden_types=(RawInspectionResult, InspectionEngineOutput),
        graph_name=f"{case.name} prediction",
    )
    _assert_no_values_of_type(
        output,
        forbidden_types=(InspectionPrediction,),
        graph_name=f"{case.name} output",
    )
    _assert_graph_contains_only(
        output,
        allowed_types=CANONICAL_OUTPUT_GRAPH_TYPES,
        graph_name=f"{case.name} output",
    )

    result = output.raw_inspection_result
    evidence_record = output.inspection_evidence_record
    assert result.examination_id == prediction.prediction_id
    assert not hasattr(result, "prediction")
    assert not hasattr(result, "prediction_id")
    assert not hasattr(evidence_record, "prediction")
    assert evidence_record.raw_inspection_result == result
    assert evidence_record.raw_inspection_result is not prediction


def _field_names(contract_type: type[object]) -> set[str]:
    return {field.name for field in fields(contract_type)}


def _assert_prediction_localization_matches_judgement(
    prediction: InspectionPrediction,
) -> None:
    if prediction.predicted_judgement is InspectionJudgement.DEFECT:
        assert type(prediction.predicted_localization) is DefectLocalization
        assert type(prediction.predicted_localization.region) is NormalizedBoundingBox
        region = prediction.predicted_localization.region
        assert 0.0 <= region.x_min < region.x_max <= 1.0
        assert 0.0 <= region.y_min < region.y_max <= 1.0
    else:
        assert prediction.predicted_judgement is InspectionJudgement.OK
        assert prediction.predicted_localization is None


def _assert_descriptive_metadata_only(metadata: Mapping[str, str]) -> None:
    assert isinstance(metadata, Mapping)
    for key, value in metadata.items():
        assert isinstance(key, str)
        assert key.strip()
        assert isinstance(value, str)
        assert not _is_forbidden_metadata_key(key)


def _is_forbidden_metadata_key(key: str) -> bool:
    normalized_key = "".join(
        character.lower() if character.isalnum() else "_"
        for character in key
    ).strip("_")
    tokens = tuple(token for token in normalized_key.split("_") if token)
    return any(
        _contains_token_sequence(tokens, forbidden_sequence)
        for forbidden_sequence in FORBIDDEN_METADATA_KEY_TOKENS
    )


def _contains_token_sequence(
    tokens: tuple[str, ...],
    sequence: tuple[str, ...],
) -> bool:
    length = len(sequence)
    return any(
        tokens[index : index + length] == sequence
        for index in range(len(tokens) - length + 1)
    )


def _assert_object_absent(value: object, forbidden: object, graph_name: str) -> None:
    forbidden_id = id(forbidden)
    assert all(
        id(item) != forbidden_id for item in _walk_object_graph(value)
    ), f"{graph_name} leaked provider object"


def _assert_no_values_of_type(
    value: object,
    *,
    forbidden_types: tuple[type[object], ...],
    graph_name: str,
) -> None:
    for item in _walk_object_graph(value):
        assert not isinstance(item, forbidden_types), (
            f"{graph_name} leaked forbidden value type {type(item).__name__}"
        )


def _assert_graph_contains_only(
    value: object,
    *,
    allowed_types: frozenset[type[object]],
    graph_name: str,
) -> None:
    for item in _walk_object_graph(value):
        if isinstance(item, PRIMITIVE_TYPES):
            continue
        if isinstance(item, (tuple, list, frozenset)):
            continue
        item_type = type(item)
        _assert_not_runtime_state_type(item, graph_name)
        assert item_type in allowed_types, (
            f"{graph_name} exposed non-canonical object {item_type.__name__}"
        )


def _assert_not_runtime_state_type(item: object, graph_name: str) -> None:
    normalized_type_name = "".join(
        character.lower()
        for character in type(item).__name__
        if character.isalnum()
    )
    assert not any(
        token in normalized_type_name for token in RUNTIME_STATE_TYPE_TOKENS
    ), f"{graph_name} exposed runtime/framework object {type(item).__name__}"


def _walk_object_graph(value: object) -> Iterable[object]:
    seen: set[int] = set()
    yield from _walk(value, seen)


def _walk(value: object, seen: set[int]) -> Iterable[object]:
    yield value
    if isinstance(value, PRIMITIVE_TYPES):
        return
    value_id = id(value)
    if value_id in seen:
        return
    seen.add(value_id)

    if is_dataclass(value) and not isinstance(value, type):
        field_names = {field.name for field in fields(value)}
        for field in fields(value):
            yield from _walk(getattr(value, field.name), seen)
        for name, item in _instance_attributes(value).items():
            if name not in field_names:
                yield from _walk(name, seen)
                yield from _walk(item, seen)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk(key, seen)
            yield from _walk(item, seen)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            yield from _walk(item, seen)
        return
    if isinstance(value, frozenset):
        for item in value:
            yield from _walk(item, seen)


def _instance_attributes(value: object) -> dict[str, object]:
    try:
        return vars(value)
    except TypeError:
        return {}
