from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import fields, is_dataclass
from hashlib import sha256
import inspect
from pathlib import Path

import numpy
import pytest

from src.frameworks import (
    image_preprocessing,
    model_artifact,
    model_loader,
    onnx_session,
    output_mapping,
)
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
    PADIM_ONNX_MODEL_REFERENCE_ID,
    OnnxInspectionInferenceProvider,
    governed_padim_session_configuration,
)


FIXTURE_DIR = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "inspection"
    / "onnx_placeholder"
)
IMAGE_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "inspection"
PLACEHOLDER_MODEL_PATH = FIXTURE_DIR / "placeholder_identity.onnx"
DEFAULT_IMAGE_PATH = IMAGE_FIXTURE_DIR / "blob_defect.pgm"
SHIFTED_IMAGE_PATH = IMAGE_FIXTURE_DIR / "blob_defect_shifted.pgm"
GOVERNED_SAMPLE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "visa"
    / "extracted"
    / "candle"
    / "Data"
    / "Images"
    / "Anomaly"
    / "004.JPG"
)
GOVERNED_SAMPLE_SHA256 = (
    "a78ee870594f161f86073b5983ae1f05be178009d819b4a73997f7cbc99a5ab2"
)


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


def test_canonical_onnx_provider_uses_governed_padim_artifact() -> None:
    pytest.importorskip("onnxruntime")
    provider = OnnxInspectionInferenceProvider()
    inspection_input = _governed_padim_input()

    prediction = provider.predict(inspection_input)

    assert type(prediction) is InspectionPrediction
    assert prediction.model_metadata["model_reference_id"] == (
        PADIM_ONNX_MODEL_REFERENCE_ID
    )
    assert prediction.model_metadata["model_kind"] == "padim"
    assert prediction.raw_measure_scale == "padim_anomaly_map_max_v1"
    assert prediction.predicted_localization is not None
    assert prediction.predicted_localization.localization_kind == (
        "padim_raw_anomaly_map_argmax_region_v1"
    )
    assert provider.session_configuration.model_reference.reference_id != (
        ONNX_PLACEHOLDER_MODEL_REFERENCE_ID
    )
    assert governed_padim_session_configuration().model_reference.reference_id == (
        PADIM_ONNX_MODEL_REFERENCE_ID
    )


def test_canonical_padim_provider_requires_governed_class_metadata() -> None:
    pytest.importorskip("onnxruntime")
    provider = OnnxInspectionInferenceProvider()
    inspection_input = StabilizedInspectionInput(
        input_id="visa-inference-input-8ddbf63dbe194bfd91ebe271",
        artifact_uri=str(GOVERNED_SAMPLE_PATH),
        content_hash=GOVERNED_SAMPLE_SHA256,
        metadata={"sample_filename": "candle/Data/Images/Anomaly/004.JPG"},
    )

    with pytest.raises(InspectionExaminationFailure, match="class_name"):
        provider.predict(inspection_input)


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


def test_onnx_provider_uses_validated_model_loader_path(monkeypatch) -> None:
    runtime = FakeRuntime()
    _install_runtime(monkeypatch, runtime)
    calls = []

    def fake_load_governed_model(
        artifact,
        *,
        session_configuration,
        expected_artifact_fingerprint,
        **kwargs,
    ):
        calls.append(
            (
                artifact,
                session_configuration,
                expected_artifact_fingerprint,
                kwargs,
            )
        )
        assert type(artifact) is model_artifact.GovernedModelArtifact
        assert type(session_configuration) is OnnxSessionConfiguration
        assert expected_artifact_fingerprint == (
            model_artifact.model_artifact_fingerprint(artifact)
        )
        assert session_configuration.model_reference.reference_id == (
            model_artifact.model_artifact_identity(artifact)
        )
        assert session_configuration.model_reference.content_sha256 == (
            _placeholder_model_hash()
        )
        assert kwargs == {
            "expected_identity": artifact.identity,
            "expected_version": artifact.version,
            "expected_compatibility": artifact.metadata.compatibility,
        }
        return FakeLoadedModel(session_configuration, artifact)

    monkeypatch.setattr(
        model_loader,
        "load_governed_model",
        fake_load_governed_model,
    )

    provider = OnnxInspectionInferenceProvider(
        session_configuration=_session_configuration()
    )
    prediction = provider.predict(_inspection_input())

    assert type(prediction) is InspectionPrediction
    assert len(calls) == 1
    assert runtime.sessions == []


def test_onnx_provider_does_not_bypass_loader_content_hash_validation(
    monkeypatch,
) -> None:
    runtime = FakeRuntime()
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(InspectionExaminationFailure, match="fingerprint"):
        OnnxInspectionInferenceProvider(
            session_configuration=_session_configuration(content_sha256="0" * 64)
        )

    assert runtime.sessions == []


def test_onnx_provider_uses_preprocessed_image_tensor_not_metadata_hash(
    monkeypatch,
) -> None:
    runtime = FakeRuntime()
    _install_runtime(monkeypatch, runtime)
    calls = []

    def fake_preprocess(inspection_input: StabilizedInspectionInput):
        calls.append(inspection_input)
        return image_preprocessing.PreprocessedImageTensor(
            tensor_values=(12.5,)
        )

    monkeypatch.setattr(
        image_preprocessing,
        "preprocess_image",
        fake_preprocess,
    )
    provider = OnnxInspectionInferenceProvider(
        session_configuration=_session_configuration()
    )
    inspection_input = _inspection_input(
        metadata={"fixture": "metadata-does-not-drive-input"}
    )

    prediction = provider.predict(inspection_input)

    assert calls == [inspection_input]
    assert prediction.predicted_raw_anomaly_measure == 12.5
    assert _last_session_input_values(runtime.sessions[0]) == (12.5,)
    assert prediction.model_metadata["preprocessing_contract_id"] == (
        image_preprocessing.PREPROCESSING_CONTRACT_ID
    )
    assert prediction.model_metadata["input_tensor_shape"] == "1"
    assert prediction.model_metadata["input_tensor_dtype"] == "float32"
    source = inspect.getsource(providers_onnx)
    assert "_raw_measure_input" not in source
    assert "sorted(inspection_input.metadata.items())" not in source


def test_changing_image_bytes_changes_provider_input_and_prediction(
    monkeypatch,
) -> None:
    runtime = FakeRuntime()
    provider = _provider(monkeypatch, runtime=runtime)

    first = provider.predict(
        _inspection_input(input_id="same-input", image_path=DEFAULT_IMAGE_PATH)
    )
    second = provider.predict(
        _inspection_input(input_id="same-input", image_path=SHIFTED_IMAGE_PATH)
    )

    first_value, second_value = _session_run_values(runtime.sessions[0])
    assert first_value == pytest.approx(25.0)
    assert second_value == pytest.approx(10.294118)
    assert first.predicted_raw_anomaly_measure == pytest.approx(first_value)
    assert second.predicted_raw_anomaly_measure == pytest.approx(second_value)
    assert first.predicted_raw_anomaly_measure != (
        second.predicted_raw_anomaly_measure
    )
    assert first.prediction_id != second.prediction_id


def test_changing_metadata_alone_does_not_substitute_for_image_content(
    monkeypatch,
) -> None:
    provider = _provider(monkeypatch)

    first = provider.predict(
        _inspection_input(metadata={"fixture": "first-metadata"})
    )
    second = provider.predict(
        _inspection_input(metadata={"fixture": "changed-metadata"})
    )

    assert first == second


def test_onnx_provider_uses_governed_output_mapper(monkeypatch) -> None:
    runtime = FakeRuntime()
    _install_runtime(monkeypatch, runtime)
    calls = []

    def fake_map_outputs(
        outputs,
        *,
        input_id,
        content_hash,
        defect_threshold,
        preprocessing_contract_id,
    ):
        calls.append(
            {
                "outputs": outputs,
                "input_id": input_id,
                "content_hash": content_hash,
                "defect_threshold": defect_threshold,
                "preprocessing_contract_id": preprocessing_contract_id,
            }
        )
        return output_mapping.MappedModelOutput(
            predicted_status=output_mapping.PREDICTED_STATUS_DEFECT,
            raw_anomaly_measure=62.5,
            localization=output_mapping.MappedLocalization(
                x_min=0.1,
                y_min=0.2,
                x_max=0.3,
                y_max=0.4,
                localization_kind="mapped_placeholder_region",
            ),
            localization_kind="mapped_placeholder_region",
            model_metadata={
                "output_mapping_contract_id": (
                    output_mapping.PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID
                ),
                "output_mapping_version": output_mapping.MAPPING_VERSION,
                "output_shape": "1",
                "output_dtype": "float32",
                "raw_measure_scale": output_mapping.PLACEHOLDER_RAW_MEASURE_SCALE,
            },
        )

    monkeypatch.setattr(
        output_mapping,
        "map_onnx_outputs",
        fake_map_outputs,
    )
    inspection_input = _inspection_input()
    provider = OnnxInspectionInferenceProvider(
        session_configuration=_session_configuration()
    )

    prediction = provider.predict(inspection_input)

    assert len(calls) == 1
    assert calls[0]["outputs"][0] is runtime.sessions[0].run_inputs[-1]["raw_input"]
    assert calls[0]["input_id"] == inspection_input.input_id
    assert calls[0]["content_hash"] == inspection_input.content_hash
    assert calls[0]["preprocessing_contract_id"] == (
        image_preprocessing.PREPROCESSING_CONTRACT_ID
    )
    assert prediction.predicted_judgement.value == "defect"
    assert prediction.predicted_raw_anomaly_measure == 62.5
    assert prediction.predicted_localization is not None
    assert prediction.predicted_localization.localization_kind == (
        "mapped_placeholder_region"
    )
    assert prediction.model_metadata["output_mapping_contract_id"] == (
        output_mapping.PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID
    )


def test_onnx_provider_contains_no_inline_output_scalar_mapping() -> None:
    source = inspect.getsource(providers_onnx)

    assert "output_mapping.map_onnx_outputs" in source
    assert "_scalar_output" not in source
    assert "asarray(value" not in source
    assert "placeholder output must contain exactly one raw measure" not in source


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
        image_preprocessing.PreprocessedImageTensor,
        output_mapping.MappedLocalization,
        output_mapping.MappedModelOutput,
        numpy.ndarray,
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
    source = inspect.getsource(providers_onnx) + inspect.getsource(output_mapping)

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


def _inspection_input(
    *,
    input_id: str = "onnx-provider-input",
    image_path: Path = DEFAULT_IMAGE_PATH,
    content_hash: str | None = None,
    metadata: Mapping[str, str] | None = None,
) -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=input_id,
        artifact_uri=str(image_path),
        content_hash=content_hash or _image_hash(image_path),
        metadata=metadata or {"fixture": image_path.name},
    )


def _governed_padim_input() -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id="visa-inference-input-8ddbf63dbe194bfd91ebe271",
        artifact_uri=str(GOVERNED_SAMPLE_PATH),
        content_hash=GOVERNED_SAMPLE_SHA256,
        metadata={
            "class_name": "candle",
            "split": "validation",
            "sample_filename": "candle/Data/Images/Anomaly/004.JPG",
        },
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


def _image_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _last_session_input_values(session: "FakeInferenceSession") -> tuple[float, ...]:
    return tuple(
        float(value)
        for value in session.run_inputs[-1]["raw_input"].reshape(-1)
    )


def _session_run_values(session: "FakeInferenceSession") -> tuple[float, ...]:
    return tuple(
        float(run_input["raw_input"].reshape(-1)[0])
        for run_input in session.run_inputs
    )


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
        self.run_inputs: list[dict[str, object]] = []

    def get_inputs(self):
        return (FakeSessionInput("raw_input"),)

    def run(self, output_names, inputs):
        assert output_names is None
        self.run_inputs.append(dict(inputs))
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


class FakeLoadedModel:
    def __init__(
        self,
        configuration: OnnxSessionConfiguration,
        artifact: model_artifact.GovernedModelArtifact | None = None,
    ) -> None:
        self.artifact = artifact or model_artifact.canonical_model_artifact(
            identity="kalibra/inspection/onnx-placeholder-boundary-model",
            version="1.0.0",
            content_hash=_placeholder_model_hash(),
            artifact_path=str(PLACEHOLDER_MODEL_PATH),
            artifact_format=model_artifact.MODEL_ARTIFACT_FORMAT_ONNX,
            producer="Kalibra deterministic ONNX provider fixture",
            provenance="Deterministic placeholder ONNX model for provider boundary proof",
            lineage=(("source", "test"),),
            framework_name=model_artifact.MODEL_FRAMEWORK_ONNX_RUNTIME,
            framework_version="1.17.3",
            onnx_opset=17,
            compatibility_declaration="CPU baseline compatibility only",
        )
        self.session_configuration = configuration
        self.session_configuration_hash = onnx_session.session_configuration_hash(
            configuration
        )
        self.artifact_fingerprint = model_artifact.model_artifact_fingerprint(
            self.artifact
        )
        self.model_content_sha256 = self.artifact.content_hash.content_sha256
        self.session = FakeInferenceSession(
            str(PLACEHOLDER_MODEL_PATH.resolve()),
            sess_options=FakeSessionOptions(),
            providers=("CPUExecutionProvider",),
            provider_options=(),
        )

    def _session_for_provider(self):
        return self.session


class IncompatibleRuntime:
    __version__ = "1.17.3"
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
