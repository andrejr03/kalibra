from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from .domain import DefectLocalization, NormalizedBoundingBox
from .errors import InspectionExaminationFailure


def resolve_local_artifact_path(artifact_uri: str) -> Path:
    parsed = urlparse(artifact_uri)
    if parsed.scheme == "":
        return Path(artifact_uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    raise InspectionExaminationFailure(
        "image baseline only reads local file artifacts, "
        f"not '{parsed.scheme}://' references"
    )


def read_pgm_p2(path: Path) -> tuple[list[list[int]], int]:
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


def local_contrast_analysis(
    pixels: list[list[int]], maxval: int
) -> tuple[list[list[float]], float, int, int]:
    height = len(pixels)
    width = len(pixels[0])
    normalized_mean = sum(sum(row) for row in pixels) / (width * height * maxval)
    deviations = [
        [abs(value / maxval - normalized_mean) for value in row]
        for row in pixels
    ]
    max_deviation = max(max(row) for row in deviations)
    return deviations, max_deviation, width, height


def localization_from_deviations(
    deviations: list[list[float]],
    max_deviation: float,
    anomaly_fraction: float,
    width: int,
    height: int,
    localization_kind: str = "local_contrast_suspected_region",
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
        localization_kind=localization_kind,
    )


def _pgm_tokens(text: str):
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0]
        for token in line.split():
            yield token
