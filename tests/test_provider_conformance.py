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
