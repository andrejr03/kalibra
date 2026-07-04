from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256
import json
from math import isfinite

from src.frameworks import (
    image_preprocessing,
    model_artifact,
    model_loader,
    onnx_runtime,
    onnx_session,
    output_mapping,
)

from .domain import (
    DefectLocalization,
    InspectionJudgement,
    InspectionPrediction,
    NormalizedBoundingBox,
    StabilizedInspectionInput,
)
from .errors import InspectionExaminationFailure, MalformedInspectionInput


ONNX_BOUNDARY_PROVIDER_ID = "onnx-inspection-inference-provider-boundary-v1"
ONNX_PLACEHOLDER_MODEL_REFERENCE_ID = "onnx-placeholder-boundary-model-v1"


@dataclass(frozen=True)
class OnnxInspectionInferenceProvider:
    session_configuration: onnx_session.OnnxSessionConfiguration
    provider_id: str = ONNX_BOUNDARY_PROVIDER_ID
    defect_threshold: float = 50.0
    _session: object = field(init=False, repr=False, compare=False)
    _input_name: str = field(init=False, repr=False, compare=False)
    _configuration_hash: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        configuration = onnx_session.validate_session_configuration(
            self.session_configuration
        )
        if not isfinite(self.defect_threshold):
            raise InspectionExaminationFailure(
                "ONNX provider defect threshold must be finite"
            )

        artifact = _placeholder_model_artifact(configuration)
        loaded_model = _load_placeholder_model(artifact, configuration)
        session = loaded_model._session_for_provider()

        object.__setattr__(
            self,
            "session_configuration",
            loaded_model.session_configuration,
        )
        object.__setattr__(
            self,
            "_configuration_hash",
            loaded_model.session_configuration_hash,
        )
        object.__setattr__(self, "_session", session)
        object.__setattr__(self, "_input_name", _single_input_name(session))

    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        if not isinstance(inspection_input, StabilizedInspectionInput):
            raise MalformedInspectionInput(
                "ONNX provider requires StabilizedInspectionInput"
            )

        preprocessed = _preprocess_input(inspection_input)
        raw_input = _input_tensor(preprocessed)
        raw_outputs = _run_session(self._session, self._input_name, raw_input)
        mapped_output = _map_output(
            raw_outputs,
            inspection_input,
            preprocessed,
            self.defect_threshold,
        )
        judgement = _inspection_judgement(mapped_output.predicted_status)
        localization = _localization_from_mapped_output(mapped_output)
        prediction_id = _stable_id(
            "onnx-placeholder-prediction",
            {
                "configuration_hash": self._configuration_hash,
                "input_id": inspection_input.input_id,
                "output_mapping_contract_id": (
                    mapped_output.model_metadata["output_mapping_contract_id"]
                ),
                "provider_id": self.provider_id,
                "preprocessing_contract_id": (
                    preprocessed.preprocessing_contract_id
                ),
                "raw_measure": mapped_output.raw_anomaly_measure,
            },
        )
        model_metadata = {
            "method": self.provider_id,
            "version": "1",
            "model_reference_id": (
                self.session_configuration.model_reference.reference_id
            ),
            "configuration_hash": self._configuration_hash,
        }
        model_metadata.update(image_preprocessing.preprocessing_metadata(preprocessed))
        model_metadata.update(mapped_output.model_metadata)

        return InspectionPrediction(
            input_id=inspection_input.input_id,
            prediction_id=prediction_id,
            predicted_judgement=judgement,
            predicted_raw_anomaly_measure=mapped_output.raw_anomaly_measure,
            predicted_localization=localization,
            model_metadata=model_metadata,
        )


def _placeholder_model_artifact(
    configuration: onnx_session.OnnxSessionConfiguration,
) -> model_artifact.GovernedModelArtifact:
    model_reference = configuration.model_reference
    if model_reference.reference_id != ONNX_PLACEHOLDER_MODEL_REFERENCE_ID:
        raise InspectionExaminationFailure(
            "ONNX provider is restricted to the placeholder boundary model"
        )
    if model_reference.artifact_path is None:
        raise InspectionExaminationFailure(
            "ONNX placeholder model requires an artifact path"
        )
    if model_reference.content_sha256 is None:
        raise InspectionExaminationFailure(
            "ONNX placeholder model requires a recorded content hash"
        )

    try:
        return model_artifact.canonical_model_artifact(
            identity="kalibra/inspection/onnx-placeholder-boundary-model",
            version="1.0.0",
            content_hash=model_reference.content_sha256,
            artifact_path=model_reference.artifact_path,
            artifact_format=model_artifact.MODEL_ARTIFACT_FORMAT_ONNX,
            producer="Kalibra deterministic ONNX provider fixture",
            provenance=(
                "Deterministic placeholder ONNX model for provider boundary proof"
            ),
            lineage=(
                (
                    "source",
                    "tests/fixtures/inspection/onnx_placeholder/"
                    "generate_placeholder_onnx.py",
                ),
            ),
            framework_name=model_artifact.MODEL_FRAMEWORK_ONNX_RUNTIME,
            framework_version=_framework_version_for_artifact(),
            onnx_opset=17,
            compatibility_declaration="CPU baseline compatibility only",
        )
    except (TypeError, ValueError) as exc:
        raise InspectionExaminationFailure(
            "ONNX provider model artifact construction failed"
        ) from exc


def _framework_version_for_artifact() -> str:
    framework_version = onnx_runtime.onnx_runtime_version()
    if framework_version is None:
        raise InspectionExaminationFailure("ONNX Runtime is unavailable")
    return framework_version


def _load_placeholder_model(
    artifact: model_artifact.GovernedModelArtifact,
    configuration: onnx_session.OnnxSessionConfiguration,
) -> model_loader.ProviderPrivateLoadedModel:
    loader_configuration = _loader_session_configuration(artifact, configuration)
    try:
        return model_loader.load_governed_model(
            artifact,
            session_configuration=loader_configuration,
            expected_artifact_fingerprint=(
                model_artifact.model_artifact_fingerprint(artifact)
            ),
        )
    except model_loader.ModelLoaderError as exc:
        raise InspectionExaminationFailure(
            f"ONNX provider validated model loading failed: {exc}"
        ) from exc


def _loader_session_configuration(
    artifact: model_artifact.GovernedModelArtifact,
    configuration: onnx_session.OnnxSessionConfiguration,
) -> onnx_session.OnnxSessionConfiguration:
    reference = configuration.model_reference
    return onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=model_artifact.model_artifact_identity(artifact),
            artifact_path=reference.artifact_path,
            content_sha256=reference.content_sha256,
        ),
        execution_providers=configuration.execution_providers,
        session_options=configuration.session_options,
        execution_provider_policy=configuration.execution_provider_policy,
    )


def _single_input_name(session: object) -> str:
    get_inputs = getattr(session, "get_inputs", None)
    if not callable(get_inputs):
        raise InspectionExaminationFailure(
            "ONNX Runtime session does not expose input metadata"
        )
    inputs = tuple(get_inputs())
    if len(inputs) != 1:
        raise InspectionExaminationFailure(
            "ONNX placeholder model must expose exactly one input"
        )
    input_name = getattr(inputs[0], "name", None)
    if not isinstance(input_name, str) or not input_name.strip():
        raise InspectionExaminationFailure(
            "ONNX placeholder model input name is invalid"
        )
    return input_name


def _run_session(session: object, input_name: str, raw_input: object) -> object:
    run = getattr(session, "run", None)
    if not callable(run):
        raise InspectionExaminationFailure("ONNX Runtime session cannot run")
    try:
        outputs = run(None, {input_name: raw_input})
    except Exception as exc:
        raise InspectionExaminationFailure("ONNX Runtime inference failed") from exc
    return outputs


def _preprocess_input(
    inspection_input: StabilizedInspectionInput,
) -> image_preprocessing.PreprocessedImageTensor:
    try:
        return image_preprocessing.preprocess_image(inspection_input)
    except image_preprocessing.ImagePreprocessingError as exc:
        raise InspectionExaminationFailure(
            f"ONNX provider image preprocessing failed: {exc}"
        ) from exc


def _input_tensor(
    preprocessed: image_preprocessing.PreprocessedImageTensor,
) -> object:
    return _numpy().array(
        preprocessed.tensor_values,
        dtype=preprocessed.tensor_dtype,
    ).reshape(preprocessed.tensor_shape)


def _map_output(
    raw_outputs: object,
    inspection_input: StabilizedInspectionInput,
    preprocessed: image_preprocessing.PreprocessedImageTensor,
    defect_threshold: float,
) -> output_mapping.MappedModelOutput:
    try:
        return output_mapping.map_onnx_outputs(
            raw_outputs,
            input_id=inspection_input.input_id,
            content_hash=inspection_input.content_hash,
            defect_threshold=defect_threshold,
            preprocessing_contract_id=preprocessed.preprocessing_contract_id,
        )
    except output_mapping.OutputMappingError as exc:
        raise InspectionExaminationFailure(
            f"ONNX provider output mapping failed: {exc}"
        ) from exc


def _numpy() -> object:
    try:
        import numpy
    except ImportError as exc:
        raise InspectionExaminationFailure(
            "ONNX provider requires numpy for runtime tensor exchange"
        ) from exc
    return numpy


def _inspection_judgement(predicted_status: str) -> InspectionJudgement:
    if predicted_status == output_mapping.PREDICTED_STATUS_DEFECT:
        return InspectionJudgement.DEFECT
    if predicted_status == output_mapping.PREDICTED_STATUS_OK:
        return InspectionJudgement.OK
    raise InspectionExaminationFailure("ONNX provider mapped status is invalid")


def _localization_from_mapped_output(
    mapped_output: output_mapping.MappedModelOutput,
) -> DefectLocalization | None:
    mapped_localization = mapped_output.localization
    if mapped_localization is None:
        return None
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=mapped_localization.x_min,
            y_min=mapped_localization.y_min,
            x_max=mapped_localization.x_max,
            y_max=mapped_localization.y_max,
        ),
        localization_kind=mapped_localization.localization_kind,
    )


def _stable_id(prefix: str, payload: Mapping[str, object]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "ONNX_BOUNDARY_PROVIDER_ID",
    "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
    "OnnxInspectionInferenceProvider",
]
