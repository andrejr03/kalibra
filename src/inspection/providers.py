from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from .domain import (
    DefectLocalization,
    InspectionJudgement,
    InspectionPrediction,
    NormalizedBoundingBox,
    StabilizedInspectionInput,
)
from .errors import MalformedInspectionInput


@dataclass(frozen=True)
class DeterministicMockInferenceProvider:
    provider_id: str = "deterministic-mock-inference-provider-v1"
    defect_threshold: float = 50.0
    localization_width: float = 0.2
    localization_height: float = 0.18
    localization_x_offset: float = 0.05
    localization_y_offset: float = 0.05

    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        if not isinstance(inspection_input, StabilizedInspectionInput):
            raise MalformedInspectionInput(
                "deterministic mock provider requires StabilizedInspectionInput"
            )

        digest = _digest(self._canonical_payload(inspection_input))
        raw_measure = round(_unit_interval(digest[:16]) * 100.0, 6)
        judgement = (
            InspectionJudgement.DEFECT
            if raw_measure >= self.defect_threshold
            else InspectionJudgement.OK
        )
        localization = (
            self._localization_from_digest(digest)
            if judgement is InspectionJudgement.DEFECT
            else None
        )

        return InspectionPrediction(
            input_id=inspection_input.input_id,
            prediction_id=f"deterministic-mock-prediction:{digest[:32]}",
            predicted_judgement=judgement,
            predicted_raw_anomaly_measure=raw_measure,
            predicted_localization=localization,
            model_metadata={
                "method": self.provider_id,
                "version": "1",
            },
        )

    def _canonical_payload(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> dict[str, Any]:
        return {
            "artifact_uri": inspection_input.artifact_uri,
            "content_hash": inspection_input.content_hash,
            "input_id": inspection_input.input_id,
            "input_kind": inspection_input.input_kind,
            "intake_status": inspection_input.intake_status,
            "metadata": sorted(inspection_input.metadata.items()),
            "provider_id": self.provider_id,
        }

    def _localization_from_digest(self, digest: str) -> DefectLocalization:
        max_x_min = 1.0 - self.localization_width
        max_y_min = 1.0 - self.localization_height
        x_min = round(
            self.localization_x_offset
            + _unit_interval(digest[16:24])
            * (max_x_min - self.localization_x_offset),
            6,
        )
        y_min = round(
            self.localization_y_offset
            + _unit_interval(digest[24:32])
            * (max_y_min - self.localization_y_offset),
            6,
        )
        return DefectLocalization(
            region=NormalizedBoundingBox(
                x_min=x_min,
                y_min=y_min,
                x_max=round(x_min + self.localization_width, 6),
                y_max=round(y_min + self.localization_height, 6),
            ),
            localization_kind="deterministic_mock_suspected_region",
        )


def _unit_interval(hex_fragment: str) -> float:
    return int(hex_fragment, 16) / float((16 ** len(hex_fragment)) - 1)


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
