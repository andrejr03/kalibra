from __future__ import annotations

from dataclasses import fields, is_dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import pytest

from src.frameworks import model_loader, onnx_runtime, onnx_session
from src.frameworks import model_artifact
from src.inspection import providers_onnx


VALID_MODEL_BYTES = b"valid-onnx-model-bytes"
INVALID_MODEL_BYTES = b"invalid-onnx-model-bytes"


def test_governed_artifact_loads_successfully(monkeypatch, tmp_path) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    loaded = model_loader.load_governed_model(
        artifact,
        expected_artifact_fingerprint=(
            model_artifact.model_artifact_fingerprint(artifact)
        ),
    )

    assert type(loaded) is model_loader.ProviderPrivateLoadedModel
    assert loaded.artifact == artifact
    assert loaded.model_content_sha256 == sha256(VALID_MODEL_BYTES).hexdigest()
    assert loaded.artifact_fingerprint == (
        model_artifact.model_artifact_fingerprint(artifact)
    )
    assert len(runtime.sessions) == 1
    assert runtime.sessions[0].model_path == str(loaded.model_path)
    assert runtime.sessions[0].run_count == 0


def test_fingerprint_mismatch_fails_before_session_creation(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    model_path = _write_model(tmp_path, VALID_MODEL_BYTES)
    artifact = _artifact_for_path(model_path, content_hash="0" * 64)
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError, match="fingerprint"):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_expected_artifact_fingerprint_mismatch_fails_closed(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError, match="fingerprint"):
        model_loader.load_governed_model(
            artifact,
            expected_artifact_fingerprint="f" * 64,
        )

    assert runtime.sessions == []


def test_compatibility_mismatch_fails_before_session_creation(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime(version="1.18.0")
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderCompatibilityError, match="version"):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_unsupported_framework_fails_closed(monkeypatch, tmp_path) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_with_raw_compatibility(
        _write_model(tmp_path, VALID_MODEL_BYTES),
        framework_name="pytorch",
    )
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_unsupported_artifact_format_fails_closed(monkeypatch, tmp_path) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_with_raw_compatibility(
        _write_model(tmp_path, VALID_MODEL_BYTES),
        artifact_format="torchscript",
    )
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_missing_file_fails_before_session_creation(monkeypatch, tmp_path) -> None:
    runtime = FakeRuntime()
    missing_path = tmp_path / "missing.onnx"
    artifact = _artifact_for_path(missing_path, content_hash="1" * 64)
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError, match="missing"):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_invalid_onnx_model_fails_without_partial_load(monkeypatch, tmp_path) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, INVALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderSessionError, match="invalid"):
        model_loader.load_governed_model(artifact)

    assert runtime.sessions == []


def test_duplicate_validation_inconsistencies_fail_before_loading(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    inconsistent_configuration = onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=model_artifact.model_artifact_identity(artifact),
            artifact_path=str(artifact.reference.artifact_uri),
            content_sha256="2" * 64,
        )
    )
    _install_runtime(monkeypatch, runtime)

    with pytest.raises(model_loader.ModelLoaderValidationError, match="content hash"):
        model_loader.load_governed_model(
            artifact,
            session_configuration=inconsistent_configuration,
        )

    assert runtime.sessions == []


def test_deterministic_repeated_loading_and_identical_configuration(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    first = model_loader.load_governed_model(artifact)
    second = model_loader.load_governed_model(
        model_artifact.canonical_model_artifact(artifact)
    )

    assert first.artifact == second.artifact
    assert first.model_path == second.model_path
    assert first.model_content_sha256 == second.model_content_sha256
    assert first.artifact_fingerprint == second.artifact_fingerprint
    assert first.session_configuration == second.session_configuration
    assert first.session_configuration_hash == second.session_configuration_hash
    assert len(runtime.sessions) == 2
    assert runtime.sessions[0].providers == runtime.sessions[1].providers
    assert (
        runtime.sessions[0].provider_options
        == runtime.sessions[1].provider_options
    )


def test_loader_creates_no_inference_prediction_or_domain_output(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    loaded = model_loader.load_governed_model(artifact)

    assert len(runtime.sessions) == 1
    assert runtime.sessions[0].run_count == 0
    assert not hasattr(loaded, "predict")
    assert not hasattr(loaded, "run")
    assert not hasattr(loaded, "raw_inspection_result")
    assert "Prediction" not in model_loader.__dict__
    assert "RawInspectionResult" not in model_loader.__dict__


def test_runtime_objects_do_not_leak_from_public_loader_surface(
    monkeypatch,
    tmp_path,
) -> None:
    runtime = FakeRuntime()
    artifact = _artifact_for_path(_write_model(tmp_path, VALID_MODEL_BYTES))
    _install_runtime(monkeypatch, runtime)

    loaded = model_loader.load_governed_model(artifact)

    public_values = tuple(
        value
        for name, value in vars(loaded).items()
        if not name.startswith("_")
    )
    forbidden_types = (
        FakeRuntime,
        FakeInferenceSession,
        FakeSessionOptions,
        FakeGraphOptimizationLevel,
    )
    assert not any(
        isinstance(value, forbidden_types)
        for public_value in public_values
        for value in _walk_object_graph(public_value)
    )
    assert not hasattr(loaded, "session")
    assert not hasattr(loaded, "runtime_session")
    assert not hasattr(loaded, "onnx_session")


def test_provider_behavior_is_not_changed_by_loader_sprint() -> None:
    provider_source = Path(providers_onnx.__file__).read_text(encoding="utf-8")
    loader_source = Path(model_loader.__file__).read_text(encoding="utf-8")

    assert "model_loader" not in provider_source
    forbidden_loader_text = (
        "src.inspection",
        "src.trust",
        "src.review",
        "src.evidence",
        "src.evaluation",
        "src.integration",
        "src.prototype_ui",
        "InspectionPrediction",
        "RawInspectionResult",
        ".predict(",
        ".run(",
    )
    for text in forbidden_loader_text:
        assert text not in loader_source


def _install_runtime(monkeypatch, runtime: object) -> None:
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)


def _write_model(tmp_path: Path, content: bytes) -> Path:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(content)
    return model_path


def _artifact_for_path(
    model_path: Path,
    *,
    content_hash: str | None = None,
) -> model_artifact.GovernedModelArtifact:
    model_bytes_hash = content_hash or sha256(model_path.read_bytes()).hexdigest()
    return model_artifact.canonical_model_artifact(
        identity="kalibra/inspection/loader-model",
        version="1.0.0",
        content_hash=model_bytes_hash,
        artifact_path=str(model_path),
        artifact_format="onnx",
        producer="Kalibra Loader Fixture",
        provenance="Generated by deterministic model loader test",
        lineage=(("source", "test-model-loader"),),
        framework_name="onnxruntime",
        framework_version="1.17.3",
        onnx_opset=17,
        compatibility_declaration="CPU baseline compatibility only",
    )


def _artifact_with_raw_compatibility(
    model_path: Path,
    *,
    artifact_format: str = "onnx",
    framework_name: str = "onnxruntime",
) -> model_artifact.GovernedModelArtifact:
    artifact = _artifact_for_path(model_path)
    raw_compatibility = object.__new__(model_artifact.ModelCompatibility)
    object.__setattr__(raw_compatibility, "artifact_format", artifact_format)
    object.__setattr__(raw_compatibility, "framework_name", framework_name)
    object.__setattr__(raw_compatibility, "framework_version", "1.17.3")
    object.__setattr__(raw_compatibility, "onnx_opset", 17)
    object.__setattr__(
        raw_compatibility,
        "compatibility_declaration",
        "CPU baseline compatibility only",
    )

    raw_metadata = object.__new__(model_artifact.ModelArtifactMetadata)
    object.__setattr__(raw_metadata, "identity", artifact.identity)
    object.__setattr__(raw_metadata, "version", artifact.version)
    object.__setattr__(raw_metadata, "provenance", artifact.metadata.provenance)
    object.__setattr__(raw_metadata, "compatibility", raw_compatibility)
    object.__setattr__(
        raw_metadata,
        "metadata_kind",
        model_artifact.MODEL_ARTIFACT_METADATA_KIND,
    )

    raw_artifact = object.__new__(model_artifact.GovernedModelArtifact)
    object.__setattr__(raw_artifact, "reference", artifact.reference)
    object.__setattr__(raw_artifact, "metadata", raw_metadata)
    object.__setattr__(
        raw_artifact,
        "artifact_kind",
        model_artifact.GOVERNED_MODEL_ARTIFACT_KIND,
    )
    return raw_artifact


class FakeGraphOptimizationLevel:
    ORT_DISABLE_ALL = "disable_all"
    ORT_ENABLE_BASIC = "basic"
    ORT_ENABLE_EXTENDED = "extended"
    ORT_ENABLE_ALL = "all"


class FakeSessionOptions:
    pass


class FakeInferenceSession:
    def __init__(
        self,
        model_path: str,
        *,
        sess_options: FakeSessionOptions,
        providers: tuple[str, ...],
        provider_options: tuple[dict[str, str], ...],
    ) -> None:
        model_bytes = Path(model_path).read_bytes()
        if model_bytes != VALID_MODEL_BYTES:
            raise ValueError("invalid ONNX model")
        self.model_path = model_path
        self.sess_options = sess_options
        self.providers = providers
        self.provider_options = provider_options
        self.run_count = 0

    def run(self, *args, **kwargs):
        self.run_count += 1
        raise AssertionError("model loader must not execute inference")


class FakeRuntime:
    GraphOptimizationLevel = FakeGraphOptimizationLevel
    SessionOptions = FakeSessionOptions

    def __init__(self, *, version: str = "1.17.3") -> None:
        self.__version__ = version
        self.sessions: list[FakeInferenceSession] = []

    def get_available_providers(self) -> tuple[str, ...]:
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
