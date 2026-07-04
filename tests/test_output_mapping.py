from __future__ import annotations

from dataclasses import fields, is_dataclass
import builtins
import inspect
from pathlib import Path
import socket
from collections.abc import Iterable, Mapping, Sequence

import numpy
import pytest

from src.frameworks import output_mapping
from src.frameworks.output_mapping import (
    MappedModelOutput,
    OutputMappingError,
)


def test_valid_placeholder_output_maps_deterministically() -> None:
    mapped = _map_output(75.0)

    assert type(mapped) is MappedModelOutput
    assert mapped.predicted_status == output_mapping.PREDICTED_STATUS_DEFECT
    assert mapped.raw_anomaly_measure == 75.0
    assert mapped.localization is not None
    assert mapped.localization_kind == output_mapping.LOCALIZATION_KIND
    assert mapped.model_metadata["output_mapping_contract_id"] == (
        output_mapping.OUTPUT_MAPPING_CONTRACT_ID
    )
    assert mapped.model_metadata["output_mapping_version"] == (
        output_mapping.MAPPING_VERSION
    )
    assert mapped.model_metadata["output_count"] == "1"
    assert mapped.model_metadata["output_shape"] == "1"
    assert mapped.model_metadata["output_dtype"] == "float32"
    assert mapped.model_metadata["raw_measure_scale"] == (
        output_mapping.RAW_MEASURE_SCALE
    )
    assert mapped.model_metadata["preprocessing_contract_id"] == (
        "preprocessing-contract-v1"
    )


def test_identical_output_tensors_produce_identical_mapped_output() -> None:
    first = _map_output(25.0)
    second = _map_output(25.0)

    assert first == second
    assert first.predicted_status == output_mapping.PREDICTED_STATUS_OK
    assert first.localization is None
    assert first.localization_kind is None


def test_incompatible_output_count_fails_closed() -> None:
    with pytest.raises(OutputMappingError, match="output count"):
        output_mapping.map_onnx_outputs(
            [],
            input_id="input-1",
            content_hash="hash-1",
        )

    with pytest.raises(OutputMappingError, match="output count"):
        output_mapping.map_onnx_outputs(
            [_tensor(25.0), _tensor(25.0)],
            input_id="input-1",
            content_hash="hash-1",
        )


def test_incompatible_output_shape_fails_closed() -> None:
    with pytest.raises(OutputMappingError, match="shape"):
        output_mapping.map_onnx_outputs(
            [numpy.array([[25.0]], dtype="float32")],
            input_id="input-1",
            content_hash="hash-1",
        )

    with pytest.raises(OutputMappingError, match="shape"):
        output_mapping.map_onnx_outputs(
            [numpy.array([25.0, 30.0], dtype="float32")],
            input_id="input-1",
            content_hash="hash-1",
        )


def test_incompatible_dtype_or_non_numeric_output_fails_closed() -> None:
    with pytest.raises(OutputMappingError, match="dtype"):
        output_mapping.map_onnx_outputs(
            [numpy.array([25.0], dtype="float64")],
            input_id="input-1",
            content_hash="hash-1",
        )

    with pytest.raises(OutputMappingError, match="dtype"):
        output_mapping.map_onnx_outputs(
            [numpy.array(["not-number"])],
            input_id="input-1",
            content_hash="hash-1",
        )


def test_non_finite_values_fail_closed() -> None:
    with pytest.raises(OutputMappingError, match="finite"):
        _map_output(float("nan"))

    with pytest.raises(OutputMappingError, match="finite"):
        _map_output(float("inf"))


def test_out_of_range_values_fail_closed() -> None:
    with pytest.raises(OutputMappingError, match="range"):
        _map_output(-0.01)

    with pytest.raises(OutputMappingError, match="range"):
        _map_output(100.01)


def test_mapping_metadata_is_string_only() -> None:
    mapped = _map_output(25.0)

    assert all(isinstance(key, str) for key in mapped.model_metadata)
    assert all(isinstance(value, str) for value in mapped.model_metadata.values())

    with pytest.raises(OutputMappingError, match="metadata values"):
        MappedModelOutput(
            predicted_status=output_mapping.PREDICTED_STATUS_OK,
            raw_anomaly_measure=25.0,
            localization=None,
            localization_kind=None,
            model_metadata={"bad": 1},
        )


def test_no_tensor_or_runtime_objects_are_exposed() -> None:
    mapped = _map_output(25.0)

    forbidden_types = (
        numpy.ndarray,
        FakeRuntime,
        FakeSession,
    )
    assert not any(
        isinstance(value, forbidden_types)
        for value in _walk_object_graph(mapped)
    )


def test_output_mapping_uses_no_filesystem_access(monkeypatch) -> None:
    def unexpected_open(*_args, **_kwargs):
        raise AssertionError("unexpected open")

    def unexpected_read(_path: Path) -> bytes:
        raise AssertionError("unexpected read")

    monkeypatch.setattr(builtins, "open", unexpected_open)
    monkeypatch.setattr(Path, "read_bytes", unexpected_read)

    mapped = _map_output(25.0)

    assert mapped.raw_anomaly_measure == 25.0


def test_output_mapping_uses_no_network_access(monkeypatch) -> None:
    def unexpected_socket(*_args, **_kwargs):
        raise AssertionError("unexpected socket")

    monkeypatch.setattr(socket, "socket", unexpected_socket)

    mapped = _map_output(25.0)

    assert mapped.raw_anomaly_measure == 25.0


def test_output_mapping_uses_no_runtime_session_or_inference() -> None:
    source = inspect.getsource(output_mapping)

    forbidden_text = (
        "onnx_runtime",
        "onnx_session",
        "model_loader",
        "InferenceSession",
        ".run(",
    )
    for text in forbidden_text:
        assert text not in source


def _map_output(value: float) -> MappedModelOutput:
    return output_mapping.map_onnx_outputs(
        [_tensor(value)],
        input_id="input-1",
        content_hash="hash-1",
        preprocessing_contract_id="preprocessing-contract-v1",
    )


def _tensor(value: float):
    return numpy.array([value], dtype="float32")


class FakeRuntime:
    pass


class FakeSession:
    pass


def _walk_object_graph(value: object) -> Iterable[object]:
    seen: set[int] = set()
    yield from _walk(value, seen)


def _walk(value: object, seen: set[int]) -> Iterable[object]:
    yield value
    if isinstance(value, (str, int, float, bool, type(None))):
        return
    value_id = id(value)
    if value_id in seen:
        return
    seen.add(value_id)

    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield from _walk(getattr(value, field.name), seen)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk(key, seen)
            yield from _walk(item, seen)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for item in value:
            yield from _walk(item, seen)
