from __future__ import annotations

from pathlib import Path

import pytest

from provider_conformance import (
    ProviderConformanceCase,
    assert_provider_boundary_isolation,
    assert_provider_conforms_to_prediction_contract,
    assert_provider_deterministic_replay,
)
from src.inspection import (
    DeterministicMockInferenceProvider,
    InspectionJudgement,
    InspectionPrediction,
    LocalArtifactInferenceProvider,
    StabilizedInspectionInput,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "inspection"


PROVIDER_CONFORMANCE_CASES = (
    ProviderConformanceCase(
        name="deterministic_mock_inference_provider",
        provider_factory=DeterministicMockInferenceProvider,
        input_factory=lambda: StabilizedInspectionInput(
            input_id="conformance-mock-input",
            artifact_uri="artifact://kalibra/conformance/mock-input.png",
            content_hash="conformance-mock-content-hash",
            metadata={"fixture": "provider-conformance"},
        ),
    ),
    ProviderConformanceCase(
        name="local_artifact_inference_provider",
        provider_factory=LocalArtifactInferenceProvider,
        input_factory=lambda: StabilizedInspectionInput(
            input_id="conformance-local-artifact-blob-defect",
            artifact_uri=str(FIXTURES / "blob_defect.pgm"),
            content_hash="conformance-local-artifact-blob-defect-content-hash",
            metadata={"fixture": "provider-conformance"},
        ),
    ),
)


@pytest.mark.parametrize(
    "case",
    PROVIDER_CONFORMANCE_CASES,
    ids=lambda case: case.name,
)
def test_provider_conforms_to_prediction_contract(
    case: ProviderConformanceCase,
) -> None:
    assert_provider_conforms_to_prediction_contract(case)


@pytest.mark.parametrize(
    "case",
    PROVIDER_CONFORMANCE_CASES,
    ids=lambda case: case.name,
)
def test_provider_deterministic_replay(case: ProviderConformanceCase) -> None:
    assert_provider_deterministic_replay(case)


@pytest.mark.parametrize(
    "case",
    PROVIDER_CONFORMANCE_CASES,
    ids=lambda case: case.name,
)
def test_provider_boundary_isolation(case: ProviderConformanceCase) -> None:
    assert_provider_boundary_isolation(case)


def test_harness_fails_for_nondeterministic_provider() -> None:
    with pytest.raises(AssertionError):
        assert_provider_deterministic_replay(
            _negative_case(
                "nondeterministic_provider",
                NondeterministicProvider,
            )
        )


def test_harness_fails_for_runtime_session_object_leak() -> None:
    with pytest.raises(AssertionError, match="RuntimeSessionLike"):
        assert_provider_conforms_to_prediction_contract(
            _negative_case(
                "runtime_session_leaking_provider",
                RuntimeSessionLeakingProvider,
            )
        )


def test_harness_fails_for_invalid_prediction_metadata() -> None:
    for provider_factory in (
        NonStringMetadataProvider,
        RuntimeObjectMetadataProvider,
    ):
        with pytest.raises(AssertionError):
            assert_provider_conforms_to_prediction_contract(
                _negative_case(
                    "invalid_metadata_provider",
                    provider_factory,
                )
            )


class RuntimeSessionLike:
    pass


class NondeterministicProvider:
    def __init__(self) -> None:
        self.calls = 0

    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        self.calls += 1
        return _ok_prediction(
            inspection_input,
            prediction_id=f"nondeterministic-prediction-{self.calls}",
            raw_measure=float(self.calls),
        )


class RuntimeSessionLeakingProvider:
    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        prediction = _ok_prediction(
            inspection_input,
            prediction_id="runtime-session-leaking-prediction",
        )
        object.__setattr__(prediction, "runtime_session", RuntimeSessionLike())
        return prediction


class NonStringMetadataProvider:
    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        prediction = _ok_prediction(
            inspection_input,
            prediction_id="non-string-metadata-prediction",
        )
        object.__setattr__(prediction, "model_metadata", {"method": 7})
        return prediction


class RuntimeObjectMetadataProvider:
    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        prediction = _ok_prediction(
            inspection_input,
            prediction_id="runtime-object-metadata-prediction",
        )
        object.__setattr__(
            prediction,
            "model_metadata",
            {"method": RuntimeSessionLike()},
        )
        return prediction


def _negative_case(
    name: str,
    provider_factory,
) -> ProviderConformanceCase:
    return ProviderConformanceCase(
        name=name,
        provider_factory=provider_factory,
        input_factory=lambda: StabilizedInspectionInput(
            input_id=f"{name}-input",
            artifact_uri=f"artifact://kalibra/conformance/{name}.png",
            content_hash=f"{name}-content-hash",
            metadata={"fixture": "provider-conformance-negative"},
        ),
    )


def _ok_prediction(
    inspection_input: StabilizedInspectionInput,
    *,
    prediction_id: str,
    raw_measure: float = 0.0,
) -> InspectionPrediction:
    return InspectionPrediction(
        input_id=inspection_input.input_id,
        prediction_id=prediction_id,
        predicted_judgement=InspectionJudgement.OK,
        predicted_raw_anomaly_measure=raw_measure,
        predicted_localization=None,
        model_metadata={"method": "test-only-invalid-provider"},
    )
