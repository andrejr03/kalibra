from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .errors import InvalidInspectionInput, InvalidInspectionResult


class DefectJudgment(str, Enum):
    DEFECTIVE = "defective"
    NON_DEFECTIVE = "non_defective"


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
            raise InvalidInspectionResult("bounding box coordinates must be finite")
        if not all(0.0 <= value <= 1.0 for value in values):
            raise InvalidInspectionResult("bounding box coordinates must be normalized")
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise InvalidInspectionResult("bounding box minimums must precede maximums")


@dataclass(frozen=True)
class DefectLocalization:
    region: NormalizedBoundingBox
    label: str | None = None

    def __post_init__(self) -> None:
        if self.label is not None and not self.label.strip():
            raise InvalidInspectionResult("localization labels must not be blank")


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

