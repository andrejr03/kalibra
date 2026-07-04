from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

from src.frameworks import model_artifact, onnx_runtime, onnx_session


_SESSION_OPTIMIZATION_LEVELS = {
    onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL: "ORT_DISABLE_ALL",
    onnx_session.OPTIMIZATION_LEVEL_BASIC: "ORT_ENABLE_BASIC",
    onnx_session.OPTIMIZATION_LEVEL_EXTENDED: "ORT_ENABLE_EXTENDED",
    onnx_session.OPTIMIZATION_LEVEL_ALL: "ORT_ENABLE_ALL",
}


class ModelLoaderError(Exception):
    """Base error for deterministic governed model loading failures."""


class ModelLoaderValidationError(ModelLoaderError, ValueError):
    """Raised when governed artifact validation fails before loading."""


class ModelLoaderCompatibilityError(ModelLoaderValidationError):
    """Raised when artifact/runtime compatibility validation fails."""


class ModelLoaderSessionError(ModelLoaderError):
    """Raised when provider-private session construction fails."""


@dataclass(frozen=True)
class ValidatedModelLoad:
    artifact: model_artifact.GovernedModelArtifact
    model_path: Path
    model_content_sha256: str
    artifact_fingerprint: str
    session_configuration: onnx_session.OnnxSessionConfiguration
    session_configuration_hash: str


@dataclass(frozen=True)
class ProviderPrivateInferenceSession:
    session_configuration_hash: str
    _runtime_session: object = field(repr=False, compare=False)

    def _session_for_provider(self) -> object:
        return self._runtime_session


@dataclass(frozen=True)
class ProviderPrivateLoadedModel:
    artifact: model_artifact.GovernedModelArtifact
    model_path: Path
    model_content_sha256: str
    artifact_fingerprint: str
    session_configuration: onnx_session.OnnxSessionConfiguration
    session_configuration_hash: str
    _provider_private_session: ProviderPrivateInferenceSession = field(
        repr=False,
        compare=False,
    )

    def _session_for_provider(self) -> object:
        return self._provider_private_session._session_for_provider()


def load_model(
    artifact: model_artifact.GovernedModelArtifact,
    *,
    session_configuration: onnx_session.OnnxSessionConfiguration | None = None,
    expected_identity: model_artifact.ModelIdentity | str | None = None,
    expected_version: model_artifact.ModelVersion | str | None = None,
    expected_artifact_fingerprint: str | None = None,
    expected_compatibility: model_artifact.ModelCompatibility | None = None,
    runtime: object | None = None,
) -> ProviderPrivateLoadedModel:
    return load_governed_model(
        artifact,
        session_configuration=session_configuration,
        expected_identity=expected_identity,
        expected_version=expected_version,
        expected_artifact_fingerprint=expected_artifact_fingerprint,
        expected_compatibility=expected_compatibility,
        runtime=runtime,
    )


def load_governed_model(
    artifact: model_artifact.GovernedModelArtifact,
    *,
    session_configuration: onnx_session.OnnxSessionConfiguration | None = None,
    expected_identity: model_artifact.ModelIdentity | str | None = None,
    expected_version: model_artifact.ModelVersion | str | None = None,
    expected_artifact_fingerprint: str | None = None,
    expected_compatibility: model_artifact.ModelCompatibility | None = None,
    runtime: object | None = None,
) -> ProviderPrivateLoadedModel:
    validated = validate_model_before_loading(
        artifact,
        session_configuration=session_configuration,
        expected_identity=expected_identity,
        expected_version=expected_version,
        expected_artifact_fingerprint=expected_artifact_fingerprint,
        expected_compatibility=expected_compatibility,
        runtime=runtime,
    )
    private_session = _create_inference_session(validated, runtime=runtime)
    return ProviderPrivateLoadedModel(
        artifact=validated.artifact,
        model_path=validated.model_path,
        model_content_sha256=validated.model_content_sha256,
        artifact_fingerprint=validated.artifact_fingerprint,
        session_configuration=validated.session_configuration,
        session_configuration_hash=validated.session_configuration_hash,
        _provider_private_session=private_session,
    )


def validate_model_before_loading(
    artifact: model_artifact.GovernedModelArtifact,
    *,
    session_configuration: onnx_session.OnnxSessionConfiguration | None = None,
    expected_identity: model_artifact.ModelIdentity | str | None = None,
    expected_version: model_artifact.ModelVersion | str | None = None,
    expected_artifact_fingerprint: str | None = None,
    expected_compatibility: model_artifact.ModelCompatibility | None = None,
    runtime: object | None = None,
) -> ValidatedModelLoad:
    canonical_artifact = _canonical_artifact(artifact)
    _validate_expected_identity(canonical_artifact, expected_identity)
    _validate_expected_version(canonical_artifact, expected_version)
    _validate_expected_compatibility(
        canonical_artifact,
        expected_compatibility,
    )
    artifact_fingerprint = _artifact_fingerprint(canonical_artifact)
    _validate_expected_fingerprint(
        artifact_fingerprint,
        expected_artifact_fingerprint,
    )

    model_path = _resolved_model_path(canonical_artifact)
    content_sha256 = _read_and_hash_model(model_path)
    if content_sha256 != canonical_artifact.content_hash.content_sha256:
        raise ModelLoaderValidationError("model fingerprint mismatch")

    configuration = _canonical_session_configuration(
        canonical_artifact,
        model_path,
        session_configuration,
    )
    runtime_object = _load_runtime(runtime)
    _validate_compatibility(canonical_artifact, configuration, runtime_object)

    return ValidatedModelLoad(
        artifact=canonical_artifact,
        model_path=model_path,
        model_content_sha256=content_sha256,
        artifact_fingerprint=artifact_fingerprint,
        session_configuration=configuration,
        session_configuration_hash=(
            onnx_session.session_configuration_hash(configuration)
        ),
    )


def _create_inference_session(
    validated_model: ValidatedModelLoad,
    *,
    runtime: object | None = None,
) -> ProviderPrivateInferenceSession:
    validated_model = _validate_session_creation_inputs(validated_model)

    runtime_object = _load_runtime(runtime)
    _validate_compatibility(
        validated_model.artifact,
        validated_model.session_configuration,
        runtime_object,
    )
    session_factory = getattr(runtime_object, "InferenceSession", None)
    if not callable(session_factory):
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime does not expose InferenceSession"
        )

    try:
        runtime_session = session_factory(
            str(validated_model.model_path),
            sess_options=_session_options(
                runtime_object,
                validated_model.session_configuration.session_options,
            ),
            providers=_provider_names(validated_model.session_configuration),
            provider_options=_provider_options(
                validated_model.session_configuration
            ),
        )
    except ModelLoaderError:
        raise
    except Exception as exc:
        raise ModelLoaderSessionError(
            "ONNX Runtime session creation failed for invalid model"
        ) from exc

    return ProviderPrivateInferenceSession(
        session_configuration_hash=validated_model.session_configuration_hash,
        _runtime_session=runtime_session,
    )


def _validate_session_creation_inputs(
    validated_model: ValidatedModelLoad,
) -> ValidatedModelLoad:
    if not isinstance(validated_model, ValidatedModelLoad):
        raise TypeError("validated_model must be a ValidatedModelLoad")

    canonical_artifact = _canonical_artifact(validated_model.artifact)
    actual_fingerprint = _artifact_fingerprint(canonical_artifact)
    if actual_fingerprint != validated_model.artifact_fingerprint:
        raise ModelLoaderValidationError("model artifact fingerprint mismatch")

    model_path = _resolved_model_path(canonical_artifact)
    try:
        supplied_model_path = Path(validated_model.model_path).expanduser().resolve()
    except TypeError as exc:
        raise ModelLoaderValidationError("validated model path is invalid") from exc
    if supplied_model_path != model_path:
        raise ModelLoaderValidationError("validated model path mismatch")

    content_sha256 = _read_and_hash_model(model_path)
    if content_sha256 != canonical_artifact.content_hash.content_sha256:
        raise ModelLoaderValidationError("model fingerprint mismatch")
    if content_sha256 != validated_model.model_content_sha256:
        raise ModelLoaderValidationError("validated model content hash mismatch")

    configuration = _canonical_session_configuration(
        canonical_artifact,
        model_path,
        validated_model.session_configuration,
    )
    if configuration != validated_model.session_configuration:
        raise ModelLoaderValidationError(
            "validated session configuration mismatch"
        )

    configuration_hash = onnx_session.session_configuration_hash(configuration)
    if configuration_hash != validated_model.session_configuration_hash:
        raise ModelLoaderValidationError(
            "validated session configuration hash mismatch"
        )

    return ValidatedModelLoad(
        artifact=canonical_artifact,
        model_path=model_path,
        model_content_sha256=content_sha256,
        artifact_fingerprint=actual_fingerprint,
        session_configuration=configuration,
        session_configuration_hash=configuration_hash,
    )


def _canonical_artifact(
    artifact: model_artifact.GovernedModelArtifact,
) -> model_artifact.GovernedModelArtifact:
    try:
        return model_artifact.validate_model_artifact(artifact)
    except (TypeError, ValueError) as exc:
        raise ModelLoaderValidationError(
            "governed model artifact validation failed"
        ) from exc


def _validate_expected_identity(
    artifact: model_artifact.GovernedModelArtifact,
    expected_identity: model_artifact.ModelIdentity | str | None,
) -> None:
    if expected_identity is None:
        return
    try:
        expected = (
            model_artifact.ModelIdentity(expected_identity)
            if isinstance(expected_identity, str)
            else model_artifact.ModelIdentity(expected_identity.identifier)
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise ModelLoaderValidationError("expected model identity is invalid") from exc
    if artifact.identity != expected:
        raise ModelLoaderValidationError("model identity mismatch")


def _validate_expected_version(
    artifact: model_artifact.GovernedModelArtifact,
    expected_version: model_artifact.ModelVersion | str | None,
) -> None:
    if expected_version is None:
        return
    try:
        expected = (
            model_artifact.ModelVersion(expected_version)
            if isinstance(expected_version, str)
            else model_artifact.ModelVersion(expected_version.semantic_version)
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise ModelLoaderValidationError("expected model version is invalid") from exc
    if artifact.version != expected:
        raise ModelLoaderValidationError("model version mismatch")


def _validate_expected_compatibility(
    artifact: model_artifact.GovernedModelArtifact,
    expected_compatibility: model_artifact.ModelCompatibility | None,
) -> None:
    if expected_compatibility is None:
        return
    if not isinstance(expected_compatibility, model_artifact.ModelCompatibility):
        raise ModelLoaderValidationError(
            "expected compatibility must be a ModelCompatibility"
        )
    if artifact.metadata.compatibility != expected_compatibility:
        raise ModelLoaderCompatibilityError("model compatibility mismatch")


def _artifact_fingerprint(
    artifact: model_artifact.GovernedModelArtifact,
) -> str:
    try:
        return model_artifact.model_artifact_fingerprint(artifact)
    except (TypeError, ValueError) as exc:
        raise ModelLoaderValidationError(
            "model artifact fingerprint validation failed"
        ) from exc


def _validate_expected_fingerprint(
    actual_fingerprint: str,
    expected_fingerprint: str | None,
) -> None:
    if expected_fingerprint is None:
        return
    normalized = _normalize_sha256(
        expected_fingerprint,
        "expected_artifact_fingerprint",
    )
    if normalized != actual_fingerprint:
        raise ModelLoaderValidationError("model artifact fingerprint mismatch")


def _resolved_model_path(
    artifact: model_artifact.GovernedModelArtifact,
) -> Path:
    path = Path(artifact.reference.artifact_uri).expanduser().resolve()
    if not path.is_file():
        raise ModelLoaderValidationError(f"model file is missing: {path}")
    return path


def _read_and_hash_model(model_path: Path) -> str:
    try:
        model_bytes = model_path.read_bytes()
    except OSError as exc:
        raise ModelLoaderValidationError(
            f"model file is unreadable: {model_path}"
        ) from exc
    return sha256(model_bytes).hexdigest()


def _canonical_session_configuration(
    artifact: model_artifact.GovernedModelArtifact,
    model_path: Path,
    session_configuration: onnx_session.OnnxSessionConfiguration | None,
) -> onnx_session.OnnxSessionConfiguration:
    expected_reference_id = model_artifact.model_artifact_identity(artifact)
    expected_hash = artifact.content_hash.content_sha256
    if session_configuration is None:
        return onnx_session.OnnxSessionConfiguration(
            model_reference=onnx_session.OnnxModelReference(
                reference_id=expected_reference_id,
                artifact_path=str(model_path),
                content_sha256=expected_hash,
            )
        )

    try:
        configuration = onnx_session.validate_session_configuration(
            session_configuration
        )
    except (TypeError, ValueError) as exc:
        raise ModelLoaderValidationError(
            "session configuration validation failed"
        ) from exc

    reference = configuration.model_reference
    if reference.reference_id not in (
        expected_reference_id,
        onnx_session.DEFAULT_MODEL_REFERENCE_ID,
    ):
        raise ModelLoaderValidationError("model reference identity mismatch")
    if reference.artifact_path is not None:
        configured_path = Path(reference.artifact_path).expanduser().resolve()
        if configured_path != model_path:
            raise ModelLoaderValidationError("model reference path mismatch")
    if (
        reference.content_sha256 is not None
        and reference.content_sha256 != expected_hash
    ):
        raise ModelLoaderValidationError("model reference content hash mismatch")

    return onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=expected_reference_id,
            artifact_path=str(model_path),
            content_sha256=expected_hash,
        ),
        execution_providers=configuration.execution_providers,
        session_options=configuration.session_options,
        execution_provider_policy=configuration.execution_provider_policy,
    )


def _load_runtime(runtime: object | None) -> object:
    runtime_object = runtime if runtime is not None else onnx_runtime._load_onnxruntime()
    if runtime_object is None:
        raise ModelLoaderCompatibilityError("ONNX Runtime is unavailable")
    return runtime_object


def _validate_compatibility(
    artifact: model_artifact.GovernedModelArtifact,
    configuration: onnx_session.OnnxSessionConfiguration,
    runtime: object,
) -> None:
    compatibility = artifact.metadata.compatibility
    if compatibility.artifact_format != model_artifact.MODEL_ARTIFACT_FORMAT_ONNX:
        raise ModelLoaderCompatibilityError("unsupported model artifact format")
    if compatibility.framework_name != model_artifact.MODEL_FRAMEWORK_ONNX_RUNTIME:
        raise ModelLoaderCompatibilityError("unsupported model framework")

    runtime_version = getattr(runtime, "__version__", None)
    if str(runtime_version) != compatibility.framework_version:
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime version mismatch with compatibility metadata"
        )

    if not callable(getattr(runtime, "InferenceSession", None)):
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime does not expose InferenceSession"
        )
    _session_options(runtime, configuration.session_options)
    _validate_provider_availability(runtime, _provider_names(configuration))


def _validate_provider_availability(
    runtime: object,
    provider_names: tuple[str, ...],
) -> None:
    get_available_providers = getattr(runtime, "get_available_providers", None)
    if not callable(get_available_providers):
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime does not expose execution providers"
        )
    providers = tuple(
        provider for provider in get_available_providers() if isinstance(provider, str)
    )
    if not providers:
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime exposes no execution providers"
        )
    missing = tuple(
        provider_name
        for provider_name in provider_names
        if provider_name not in providers
    )
    if missing:
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime is missing requested execution provider"
        )


def _provider_names(
    configuration: onnx_session.OnnxSessionConfiguration,
) -> tuple[str, ...]:
    return tuple(provider.name for provider in configuration.execution_providers)


def _provider_options(
    configuration: onnx_session.OnnxSessionConfiguration,
) -> tuple[dict[str, str], ...]:
    return tuple(
        dict(provider.provider_options)
        for provider in configuration.execution_providers
    )


def _session_options(
    runtime: object,
    options: onnx_session.OnnxSessionOptions,
) -> object:
    session_options_factory = getattr(runtime, "SessionOptions", None)
    if not callable(session_options_factory):
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime does not expose SessionOptions"
        )
    session_options = session_options_factory()
    setattr(session_options, "intra_op_num_threads", options.intra_op_num_threads)
    setattr(session_options, "inter_op_num_threads", options.inter_op_num_threads)
    setattr(
        session_options,
        "graph_optimization_level",
        _graph_optimization_level(runtime, options.optimization_level),
    )
    return session_options


def _graph_optimization_level(runtime: object, optimization_level: str) -> object:
    graph_levels = getattr(runtime, "GraphOptimizationLevel", None)
    if graph_levels is None:
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime does not expose graph optimization levels"
        )
    runtime_level_name = _SESSION_OPTIMIZATION_LEVELS[optimization_level]
    try:
        return getattr(graph_levels, runtime_level_name)
    except AttributeError as exc:
        raise ModelLoaderCompatibilityError(
            "ONNX Runtime graph optimization level is incompatible"
        ) from exc


def _normalize_sha256(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ModelLoaderValidationError(f"{field_name} must be a string")
    normalized = value.strip().lower()
    if len(normalized) != 64:
        raise ModelLoaderValidationError(
            f"{field_name} must be a 64-character hex digest"
        )
    if any(character not in "0123456789abcdef" for character in normalized):
        raise ModelLoaderValidationError(
            f"{field_name} must be a 64-character hex digest"
        )
    return normalized


__all__ = [
    "ModelLoaderCompatibilityError",
    "ModelLoaderError",
    "ModelLoaderSessionError",
    "ModelLoaderValidationError",
    "ProviderPrivateInferenceSession",
    "ProviderPrivateLoadedModel",
    "ValidatedModelLoad",
    "load_governed_model",
    "load_model",
    "validate_model_before_loading",
]
