from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlparse


PREPROCESSING_CONTRACT_ID = "kalibra-pgm-p2-fixed-4x4-weighted-projection-v1"
IMAGE_FORMAT = "pgm_p2"
SOURCE_IMAGE_SHAPE = (4, 4)
TENSOR_SHAPE = (1,)
TENSOR_DTYPE = "float32"
TENSOR_VALUE_RANGE = (0.0, 100.0)
NORMALIZATION_MODE = "weighted_luminance_projection_0_100"
RESIZE_MODE = "none_reject_non_4x4"


class ImagePreprocessingError(ValueError):
    """Raised when deterministic image preprocessing cannot produce its contract."""


@dataclass(frozen=True)
class PreprocessedImageTensor:
    tensor_values: tuple[float, ...]
    tensor_shape: tuple[int, ...] = TENSOR_SHAPE
    tensor_dtype: str = TENSOR_DTYPE
    tensor_value_range: tuple[float, float] = TENSOR_VALUE_RANGE
    preprocessing_contract_id: str = PREPROCESSING_CONTRACT_ID
    normalization_mode: str = NORMALIZATION_MODE
    image_format: str = IMAGE_FORMAT
    source_image_shape: tuple[int, int] = SOURCE_IMAGE_SHAPE
    resize_mode: str = RESIZE_MODE


def preprocess_image(inspection_input: object) -> PreprocessedImageTensor:
    artifact_uri = _required_string_attribute(inspection_input, "artifact_uri")
    expected_content_hash = _required_string_attribute(
        inspection_input, "content_hash"
    )
    path = resolve_local_image_path(artifact_uri)
    image_bytes = _read_artifact_bytes(path)
    _validate_content_hash(image_bytes, expected_content_hash)
    pixels, maxval, width, height = _decode_pgm_p2(image_bytes)
    _validate_source_shape(width, height)
    return PreprocessedImageTensor(
        tensor_values=(_weighted_luminance_projection(pixels, maxval),)
    )


def resolve_local_image_path(artifact_uri: str) -> Path:
    parsed = urlparse(artifact_uri)
    if parsed.scheme == "":
        return Path(artifact_uri).expanduser()
    if parsed.scheme == "file" and parsed.netloc in ("", "localhost"):
        return Path(unquote(parsed.path)).expanduser()
    raise ImagePreprocessingError(
        "image preprocessing only reads local file artifacts"
    )


def preprocessing_metadata(
    preprocessed: PreprocessedImageTensor,
) -> dict[str, str]:
    return {
        "preprocessing_contract_id": preprocessed.preprocessing_contract_id,
        "input_tensor_shape": _shape_text(preprocessed.tensor_shape),
        "input_tensor_dtype": preprocessed.tensor_dtype,
        "input_tensor_value_range": (
            f"{preprocessed.tensor_value_range[0]:.1f}.."
            f"{preprocessed.tensor_value_range[1]:.1f}"
        ),
        "normalization_mode": preprocessed.normalization_mode,
        "image_format": preprocessed.image_format,
        "source_image_shape": _shape_text(preprocessed.source_image_shape),
        "resize_mode": preprocessed.resize_mode,
    }


def _read_artifact_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ImagePreprocessingError(
            f"image artifact could not be read: {path}"
        ) from exc


def _validate_content_hash(image_bytes: bytes, expected_content_hash: str) -> None:
    actual_content_hash = sha256(image_bytes).hexdigest()
    if actual_content_hash != expected_content_hash:
        raise ImagePreprocessingError("image artifact content hash mismatch")


def _decode_pgm_p2(image_bytes: bytes) -> tuple[list[list[int]], int, int, int]:
    try:
        text = image_bytes.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ImagePreprocessingError(
            "image preprocessing supports only ascii PGM artifacts"
        ) from exc

    tokens = _pgm_tokens(text)
    try:
        magic = next(tokens)
        if magic != "P2":
            raise ImagePreprocessingError(
                "image preprocessing supports only ascii PGM (P2) artifacts"
            )
        width = int(next(tokens))
        height = int(next(tokens))
        maxval = int(next(tokens))
    except ImagePreprocessingError:
        raise
    except StopIteration as exc:
        raise ImagePreprocessingError("PGM header is incomplete") from exc
    except ValueError as exc:
        raise ImagePreprocessingError("PGM header is not numeric") from exc

    if width <= 0 or height <= 0 or maxval <= 0:
        raise ImagePreprocessingError(
            "PGM width, height and maxval must be positive"
        )

    pixels: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            try:
                value = int(next(tokens))
            except StopIteration as exc:
                raise ImagePreprocessingError(
                    "PGM pixel data is truncated"
                ) from exc
            except ValueError as exc:
                raise ImagePreprocessingError(
                    "PGM pixel data is not numeric"
                ) from exc
            if value < 0 or value > maxval:
                raise ImagePreprocessingError("PGM pixel value is out of range")
            row.append(value)
        pixels.append(row)

    try:
        next(tokens)
    except StopIteration:
        return pixels, maxval, width, height
    raise ImagePreprocessingError("PGM pixel data has trailing values")


def _validate_source_shape(width: int, height: int) -> None:
    expected_width, expected_height = SOURCE_IMAGE_SHAPE
    if (width, height) != (expected_width, expected_height):
        raise ImagePreprocessingError(
            "PGM source image shape does not match preprocessing contract"
        )


def _weighted_luminance_projection(
    pixels: list[list[int]],
    maxval: int,
) -> float:
    weighted_sum = 0
    weight_total = 0
    for row_index, row in enumerate(pixels):
        for col_index, value in enumerate(row):
            weight = row_index * len(row) + col_index + 1
            weighted_sum += weight * value
            weight_total += weight

    if weight_total <= 0 or maxval <= 0:
        raise ImagePreprocessingError("PGM normalization contract is invalid")
    normalized = (weighted_sum / (weight_total * maxval)) * 100.0
    lower, upper = TENSOR_VALUE_RANGE
    if normalized < lower or normalized > upper:
        raise ImagePreprocessingError(
            "PGM normalized tensor value is outside contract range"
        )
    return round(normalized, 6)


def _required_string_attribute(value: object, name: str) -> str:
    attribute = getattr(value, name, None)
    if not isinstance(attribute, str) or not attribute.strip():
        raise ImagePreprocessingError(
            f"image preprocessing requires {name}"
        )
    return attribute


def _pgm_tokens(text: str):
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0]
        for token in line.split():
            yield token


def _shape_text(shape: tuple[int, ...]) -> str:
    return "x".join(str(dimension) for dimension in shape)


__all__ = [
    "IMAGE_FORMAT",
    "NORMALIZATION_MODE",
    "PREPROCESSING_CONTRACT_ID",
    "RESIZE_MODE",
    "SOURCE_IMAGE_SHAPE",
    "TENSOR_DTYPE",
    "TENSOR_SHAPE",
    "TENSOR_VALUE_RANGE",
    "ImagePreprocessingError",
    "PreprocessedImageTensor",
    "preprocess_image",
    "preprocessing_metadata",
    "resolve_local_image_path",
]
