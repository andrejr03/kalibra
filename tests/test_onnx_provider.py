from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import fields, is_dataclass
from hashlib import sha256
import inspect
from pathlib import Path

import pytest

from provider_conformance import (
    ProviderConformanceCase,
    assert_provider_boundary_isolation,
    assert_provider_conforms_to_prediction_contract,
    assert_provider_deterministic_replay,
)
from src.frameworks import onnx_runtime
from src.frameworks.onnx_session import (
    OnnxExecutionProvider,
    OnnxModelReference,
    OnnxSessionConfiguration,
    OnnxSessionOptions,
)
from src.inspection import (
    InspectionEngine,
    InspectionInferenceProvider,
    InspectionPrediction,
    RawInspectionResult,
    StabilizedInspectionInput,
)
from src.inspection.errors import InspectionExaminationFailure
from src.inspection import providers_onnx
from src.inspection.providers_onnx import (
    ONNX_PLACEHOLDER_MODEL_REFERENCE_ID,
    OnnxInspectionInferenceProvider,
)


FIXTURE_DIR = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "inspection"
    / "onnx_placeholder"
)
PLACEHOLDER_MODEL_PATH = FIXTURE_DIR / "placeholder_identity.onnx"


def test_onnx_provider_satisfies_inference_provider_boundary(monkeypatch) -> None:
    provider: InspectionInferenceProvider = _provider(monkeypatch)

    prediction = provider.predict(_inspection_input())

    assert type(prediction) is InspectionPrediction
    assert prediction.input_id == "onnx-provider-input"


def test_onnx_provider_returns_exactly_inspection_prediction(monkeypatch) -> None:
    prediction = _provider(monkeypatch).predict(_inspection_input())

    assert type(prediction) is InspectionPrediction
    assert not isinstance(prediction, RawInspectionResult)
    assert not hasattr(prediction, "runtime_session")
    assert not hasattr(prediction, "onnx_session")
    assert not hasattr(prediction, "tensor")


def test_onnx_provider_replays_identical_predictions(monkeypatch) -> None:
    provider = _provider(monkeypatch)
    inspection_input = _inspection_input()

    first = provider.predict(inspection_input)
    second = provider.predict(inspection_input)
    separate_provider = _provider(monkeypatch).predict(inspection_input)

    assert first == second
    assert first == separate_provider


def test_onnx_provider_transforms_to_identical_raw_result(monkeypatch) -> None:
    provider = _provider(monkeypatch)
    inspection_input = _inspection_input()
    first_prediction = provider.predict(inspection_input)
    second_prediction = provider.predict(inspection_input)
    engine = InspectionEngine()

    first_output = engine.transform_prediction(inspection_input, first_prediction)
    second_output = engine.transform_prediction(inspection_input, second_prediction)

    assert type(first_output.raw_inspection_result) is RawInspectionResult
    assert first_output.raw_inspection_result == second_output.raw_inspection_result
    assert first_output == second_output


def test_onnx_provider_passes_conformance_harness(monkeypatch) -> None:
    case = _conformance_case(monkeypatch)

    assert_provider_conforms_to_prediction_contract(case)
    assert_provider_deterministic_replay(case)
    assert_provider_boundary_isolation(case)


def test_onnx_provider_real_runtime_integration() -> None:
    ort = pytest.importorskip("onnxruntime")

    def build_provider() -> OnnxInspectionInferenceProvider:
        return OnnxInspectionInferenceProvider(
            session_configuration=_session_configuration()
        )

    provider = build_provider()
    inspection_input = _inspection_input()

    prediction = provider.predict(inspection_input)
    assert type(prediction) is InspectionPrediction
    assert not isinstance(prediction, RawInspectionResult)

    engine = InspectionEngine()
    first_output = engine.transform_prediction(inspection_input, prediction)
    assert type(first_output.raw_inspection_result) is RawInspectionResult

    replay_prediction = build_provider().predict(inspection_input)
    assert replay_prediction == prediction
    second_output = engine.transform_prediction(inspection_input, replay_prediction)
    assert second_output.raw_inspection_result == first_output.raw_inspection_result
    assert second_output == first_output

    case = ProviderConformanceCase(
        name="onnx_inspection_inference_provider_real_runtime",
        provider_factory=build_provider,
        input_factory=_inspection_input,
    )
    assert_provider_conforms_to_prediction_contract(case)
    assert_provider_deterministic_replay(case)
    assert_provider_boundary_isolation(case)

    assert not any(
        isinstance(value, ort.InferenceSession)
        for value in _walk_object_graph(prediction)
    )
    assert not any(
        isinstance(value, ort.InferenceSession)
        for value in _walk_object_graph(first_output)
    )


def test_onnx_runtime_objects_do_not_leak_downstream(monkeypatch) -> None:
    runtime = FakeRuntime()
    provider = _provider(monkeypatch, runtime=runtime)
    inspection_input = _inspection_input()

    prediction = provider.predict(inspection_input)
    output = InspectionEngine().transform_prediction(inspection_input, prediction)

    forbidden_types = (
        FakeRuntime,
        FakeInferenceSession,
        FakeSessionInput,
        FakeSessionOptions,
    )
    assert not any(
        isinstance(value, forbidden_types)
        for value in _walk_object_graph(prediction)
    )
    assert not any(
        isinstance(value, forbidden_types)
        for value in _walk_object_graph(output)
    )


def test_onnx_provider_does_not_construct_raw_inspection_result() -> None:
    source = inspect.getsource(providers_onnx)

    assert "RawInspectionResult" not in source


def test_valid_placeholder_model_path_succeeds(monkeypatch) -> None:
    runtime = FakeRuntime()
    provider = _provider(monkeypatch, runtime=runtime)

    prediction = provider.predict(_inspection_input())

    assert type(prediction) is InspectionPrediction
    assert len(runtime.sessions) == 1
    assert runtime.sessions[0].model_path == str(PLACEHOLDER_MODEL_PATH.resolve())


def test_invalid_model_path_fails_cleanly(monkeypatch, tmp_path) -> None:
    _install_runtime(monkeypatch, FakeRuntime())
    missing_model = tmp_path / "missing-placeholder.onnx"

    with pytest.raises(InspectionExaminationFailure, match="missing"):
        OnnxInspectionInferenceProvider(
            session_configuration=_session_configuration(
                model_path=missing_model,
                content_sha256=_placeholder_model_hash(),
            )
        )


def test_missing_onnx_runtime_fails_cleanly(monkeypatch) -> None:
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: None)

    with pytest.raises(InspectionExaminationFailure, match="unavailable"):
        OnnxInspectionInferenceProvider(
            session_configuration=_session_configuration()
        )


def test_incompatible_onnx_runtime_fails_cleanly(monkeypatch) -> None:
    _install_runtime(monkeypatch, IncompatibleRuntime())

    with pytest.raises(InspectionExaminationFailure, match="InferenceSession"):
        OnnxInspectionInferenceProvider(
            session_configuration=_session_configuration()
        )


def test_downstream_domain_and_cli_ui_paths_are_not_involved() -> None:
    source = inspect.getsource(providers_onnx)

    forbidden_text = (
        "src.trust",
        "src.review",
        "src.evidence",
        "src.evaluation",
        "src.integration",
        "src.prototype_ui",
        "TrustQualification",
        "HumanReview",
        "EvidenceEngine",
        "EvaluationEngine",
        "run_end_to_end",
        "prototype",
        "cli",
    )
    for text in forbidden_text:
        assert text not in source


def _provider(
    monkeypatch,
    *,
    runtime: FakeRuntime | None = None,
) -> OnnxInspectionInferenceProvider:
    _install_runtime(monkeypatch, runtime or FakeRuntime())
    return OnnxInspectionInferenceProvider(
        session_configuration=_session_configuration()
    )


def _install_runtime(monkeypatch, runtime: object) -> None:
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)


def _conformance_case(monkeypatch) -> ProviderConformanceCase:
    return ProviderConformanceCase(
        name="onnx_inspection_inference_provider",
        provider_factory=lambda: _provider(monkeypatch),
        input_factory=_inspection_input,
    )


def _inspection_input() -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id="onnx-provider-input",
        artifact_uri="artifact://kalibra/onnx-provider/boundary-input.png",
        content_hash="onnx-provider-boundary-input-content-hash",
        metadata={"fixture": "onnx-provider-boundary"},
    )


def _session_configuration(
    *,
    model_path: Path = PLACEHOLDER_MODEL_PATH,
    content_sha256: str | None = None,
) -> OnnxSessionConfiguration:
    return OnnxSessionConfiguration(
        model_reference=OnnxModelReference(
            reference_id=ONNX_PLACEHOLDER_MODEL_REFERENCE_ID,
            artifact_path=str(model_path),
            content_sha256=content_sha256 or _placeholder_model_hash(),
        ),
        execution_providers=(
            OnnxExecutionProvider(name="CPUExecutionProvider"),
        ),
        session_options=OnnxSessionOptions(),
    )


def _placeholder_model_hash() -> str:
    return sha256(PLACEHOLDER_MODEL_PATH.read_bytes()).hexdigest()


class FakeGraphOptimizationLevel:
    ORT_DISABLE_ALL = "disable_all"
    ORT_ENABLE_BASIC = "basic"
    ORT_ENABLE_EXTENDED = "extended"
    ORT_ENABLE_ALL = "all"


class FakeSessionOptions:
    pass


class FakeSessionInput:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeInferenceSession:
    def __init__(
        self,
        model_path: str,
        *,
        sess_options: FakeSessionOptions,
        providers: tuple[str, ...],
        provider_options: tuple[dict[str, str], ...],
    ) -> None:
        self.model_path = model_path
        self.sess_options = sess_options
        self.providers = providers
        self.provider_options = provider_options

    def get_inputs(self):
        return (FakeSessionInput("raw_input"),)

    def run(self, output_names, inputs):
        assert output_names is None
        return [inputs["raw_input"]]


class FakeRuntime:
    __version__ = "1.17.3"
    GraphOptimizationLevel = FakeGraphOptimizationLevel
    SessionOptions = FakeSessionOptions

    def __init__(self) -> None:
        self.sessions: list[FakeInferenceSession] = []

    def get_available_providers(self):
        return ("CPUExecutionProvider",)

    def InferenceSession(
        self,
        model_path: str,
        *,
        sess_options: FakeSessionOptions,
        providers: tuple[str, ...],
        provider_options: tuple[dict[str, str], ...],
    ) -> FakeInferenceSession:
        session = FakeInferenceSession(
            model_path,
            sess_options=sess_options,
            providers=providers,
            provider_options=provider_options,
        )
        self.sessions.append(session)
        return session


class IncompatibleRuntime:
    __version__ = "0.0"
    GraphOptimizationLevel = FakeGraphOptimizationLevel
    SessionOptions = FakeSessionOptions

    def get_available_providers(self):
        return ("CPUExecutionProvider",)


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
