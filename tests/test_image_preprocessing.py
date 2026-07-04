from __future__ import annotations

from hashlib import sha256
import inspect
from pathlib import Path
import socket

import pytest

from src.frameworks import image_preprocessing
from src.frameworks.image_preprocessing import (
    ImagePreprocessingError,
    PreprocessedImageTensor,
)
from src.inspection import StabilizedInspectionInput


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "inspection"


def test_valid_pgm_fixture_decodes_successfully() -> None:
    preprocessed = image_preprocessing.preprocess_image(
        _inspection_input("blob_defect.pgm")
    )

    assert type(preprocessed) is PreprocessedImageTensor
    assert preprocessed.image_format == image_preprocessing.IMAGE_FORMAT
    assert preprocessed.tensor_values == (25.0,)


def test_malformed_pgm_fails_closed() -> None:
    with pytest.raises(ImagePreprocessingError, match="ascii PGM"):
        image_preprocessing.preprocess_image(_inspection_input("bad_magic.pgm"))

    with pytest.raises(ImagePreprocessingError, match="truncated"):
        image_preprocessing.preprocess_image(_inspection_input("truncated.pgm"))


def test_content_hash_mismatch_fails_closed() -> None:
    inspection_input = _inspection_input(
        "blob_defect.pgm",
        content_hash="0" * 64,
    )

    with pytest.raises(ImagePreprocessingError, match="content hash mismatch"):
        image_preprocessing.preprocess_image(inspection_input)


def test_identical_image_bytes_produce_identical_tensor() -> None:
    inspection_input = _inspection_input("blob_defect.pgm")

    first = image_preprocessing.preprocess_image(inspection_input)
    second = image_preprocessing.preprocess_image(inspection_input)

    assert first == second
    assert first.tensor_values == second.tensor_values


def test_declared_tensor_contract_is_stable() -> None:
    preprocessed = image_preprocessing.preprocess_image(
        _inspection_input("blob_defect.pgm")
    )

    assert preprocessed.tensor_shape == image_preprocessing.TENSOR_SHAPE
    assert preprocessed.tensor_shape == (1,)
    assert preprocessed.tensor_dtype == image_preprocessing.TENSOR_DTYPE
    assert preprocessed.tensor_dtype == "float32"
    assert preprocessed.tensor_value_range == (
        image_preprocessing.TENSOR_VALUE_RANGE
    )
    assert preprocessed.tensor_value_range == (0.0, 100.0)
    assert all(
        preprocessed.tensor_value_range[0]
        <= value
        <= preprocessed.tensor_value_range[1]
        for value in preprocessed.tensor_values
    )
    assert preprocessed.normalization_mode == (
        image_preprocessing.NORMALIZATION_MODE
    )
    assert preprocessed.source_image_shape == (4, 4)
    assert preprocessed.resize_mode == image_preprocessing.RESIZE_MODE


def test_non_local_references_fail_before_file_read(monkeypatch) -> None:
    def unexpected_read(_path: Path) -> bytes:
        raise AssertionError("unexpected artifact read")

    monkeypatch.setattr(Path, "read_bytes", unexpected_read)

    with pytest.raises(ImagePreprocessingError, match="local file artifacts"):
        image_preprocessing.preprocess_image(
            StabilizedInspectionInput(
                input_id="non-local-input",
                artifact_uri="artifact://kalibra/parts/input.pgm",
                content_hash="0" * 64,
            )
        )


def test_preprocessing_does_not_use_network_access(monkeypatch) -> None:
    def unexpected_socket(*_args, **_kwargs):
        raise AssertionError("unexpected socket access")

    monkeypatch.setattr(socket, "socket", unexpected_socket)

    preprocessed = image_preprocessing.preprocess_image(
        _inspection_input("blob_defect.pgm")
    )

    assert preprocessed.tensor_values == (25.0,)


def test_preprocessing_does_not_use_runtime_session_or_inference() -> None:
    source = inspect.getsource(image_preprocessing)

    forbidden_text = (
        "onnx_runtime",
        "onnx_session",
        "model_loader",
        "InferenceSession",
        ".run(",
    )
    for text in forbidden_text:
        assert text not in source


def _inspection_input(
    filename: str,
    *,
    content_hash: str | None = None,
) -> StabilizedInspectionInput:
    path = FIXTURES / filename
    return StabilizedInspectionInput(
        input_id=f"preprocessing-{filename}",
        artifact_uri=str(path),
        content_hash=content_hash or _fixture_hash(path),
        metadata={"fixture": filename},
    )


def _fixture_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
