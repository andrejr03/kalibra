from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from typing import Any

from src.frameworks import onnx_runtime, onnx_session

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

_SESSION_OPTIMIZATION_LEVELS = {
    onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL: "ORT_DISABLE_ALL",
    onnx_session.OPTIMIZATION_LEVEL_BASIC: "ORT_ENABLE_BASIC",
    onnx_session.OPTIMIZATION_LEVEL_EXTENDED: "ORT_ENABLE_EXTENDED",
    onnx_session.OPTIMIZATION_LEVEL_ALL: "ORT_ENABLE_ALL",
}


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

        model_path = _placeholder_model_path(configuration)
        _verify_placeholder_model_reference(configuration, model_path)
        runtime = _load_runtime()
        session = _create_session(runtime, configuration, model_path)

        object.__setattr__(self, "session_configuration", configuration)
        object.__setattr__(
            self,
            "_configuration_hash",
            onnx_session.session_configuration_hash(configuration),
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

        raw_input = _input_tensor(
            _raw_measure_input(
                inspection_input,
                self.provider_id,
                self._configuration_hash,
            )
        )
        raw_output = _run_session(self._session, self._input_name, raw_input)
        raw_measure = round(_scalar_output(raw_output), 6)
        if raw_measure < 0.0 or raw_measure > 100.0:
            raise InspectionExaminationFailure(
                "ONNX placeholder output must stay within raw 0-100 scale"
            )

        judgement = (
            InspectionJudgement.DEFECT
            if raw_measure >= self.defect_threshold
            else InspectionJudgement.OK
        )
        localization = (
            _localization_from_input(inspection_input)
            if judgement is InspectionJudgement.DEFECT
            else None
        )
        prediction_id = _stable_id(
            "onnx-placeholder-prediction",
            {
                "configuration_hash": self._configuration_hash,
                "input_id": inspection_input.input_id,
                "provider_id": self.provider_id,
                "raw_measure": raw_measure,
            },
        )

        return InspectionPrediction(
            input_id=inspection_input.input_id,
            prediction_id=prediction_id,
            predicted_judgement=judgement,
            predicted_raw_anomaly_measure=raw_measure,
            predicted_localization=localization,
            model_metadata={
                "method": self.provider_id,
                "version": "1",
                "model_reference_id": (
                    self.session_configuration.model_reference.reference_id
                ),
                "configuration_hash": self._configuration_hash,
            },
        )


def _placeholder_model_path(
    configuration: onnx_session.OnnxSessionConfiguration,
) -> Path:
    model_reference = configuration.model_reference
    if model_reference.reference_id != ONNX_PLACEHOLDER_MODEL_REFERENCE_ID:
        raise InspectionExaminationFailure(
            "ONNX provider is restricted to the placeholder boundary model"
        )
    if model_reference.artifact_path is None:
        raise InspectionExaminationFailure(
            "ONNX placeholder model requires an artifact path"
        )
    path = Path(model_reference.artifact_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise InspectionExaminationFailure(
            f"ONNX placeholder model is missing or unreadable: {path}"
        )
    return path


def _verify_placeholder_model_reference(
    configuration: onnx_session.OnnxSessionConfiguration,
    model_path: Path,
) -> None:
    expected_hash = configuration.model_reference.content_sha256
    if expected_hash is None:
        raise InspectionExaminationFailure(
            "ONNX placeholder model requires a recorded content hash"
        )
    actual_hash = sha256(model_path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise InspectionExaminationFailure(
            "ONNX placeholder model content hash does not match configuration"
        )


def _load_runtime() -> object:
    runtime = onnx_runtime._load_onnxruntime()
    if runtime is None:
        raise InspectionExaminationFailure("ONNX Runtime is unavailable")
    if not callable(getattr(runtime, "InferenceSession", None)):
        raise InspectionExaminationFailure(
            "ONNX Runtime does not expose InferenceSession"
        )
    return runtime


def _create_session(
    runtime: object,
    configuration: onnx_session.OnnxSessionConfiguration,
    model_path: Path,
) -> object:
    provider_names = _provider_names(configuration)
    _validate_provider_availability(provider_names)
    try:
        return runtime.InferenceSession(
            str(model_path),
            sess_options=_session_options(runtime, configuration.session_options),
            providers=provider_names,
            provider_options=_provider_options(configuration),
        )
    except InspectionExaminationFailure:
        raise
    except Exception as exc:
        raise InspectionExaminationFailure(
            "ONNX Runtime session creation failed"
        ) from exc


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


def _validate_provider_availability(provider_names: tuple[str, ...]) -> None:
    available = onnx_runtime.available_execution_providers()
    if not available:
        raise InspectionExaminationFailure(
            "ONNX Runtime exposes no execution providers"
        )
    missing = tuple(
        provider_name
        for provider_name in provider_names
        if provider_name not in available
    )
    if missing:
        raise InspectionExaminationFailure(
            "ONNX Runtime is missing requested execution provider"
        )


def _session_options(
    runtime: object,
    options: onnx_session.OnnxSessionOptions,
) -> object:
    session_options_factory = getattr(runtime, "SessionOptions", None)
    if not callable(session_options_factory):
        raise InspectionExaminationFailure(
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
        raise InspectionExaminationFailure(
            "ONNX Runtime does not expose graph optimization levels"
        )
    runtime_level_name = _SESSION_OPTIMIZATION_LEVELS[optimization_level]
    try:
        return getattr(graph_levels, runtime_level_name)
    except AttributeError as exc:
        raise InspectionExaminationFailure(
            "ONNX Runtime graph optimization level is incompatible"
        ) from exc


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
    if not isinstance(outputs, list) or not outputs:
        raise InspectionExaminationFailure(
            "ONNX Runtime inference returned no outputs"
        )
    return outputs[0]


def _raw_measure_input(
    inspection_input: StabilizedInspectionInput,
    provider_id: str,
    configuration_hash: str,
) -> float:
    digest = _digest(
        {
            "artifact_uri": inspection_input.artifact_uri,
            "configuration_hash": configuration_hash,
            "content_hash": inspection_input.content_hash,
            "input_id": inspection_input.input_id,
            "input_kind": inspection_input.input_kind,
            "intake_status": inspection_input.intake_status,
            "metadata": sorted(inspection_input.metadata.items()),
            "provider_id": provider_id,
        }
    )
    return round(_unit_interval(digest[:16]) * 100.0, 6)


def _input_tensor(raw_measure: float) -> object:
    return _numpy().array([raw_measure], dtype="float32")


def _scalar_output(value: object) -> float:
    array = _numpy().asarray(value, dtype="float64")
    if array.size != 1:
        raise InspectionExaminationFailure(
            "ONNX placeholder output must contain exactly one raw measure"
        )
    raw_measure = float(array.reshape(-1)[0])
    if not isfinite(raw_measure):
        raise InspectionExaminationFailure(
            "ONNX placeholder output raw measure must be finite"
        )
    return raw_measure


def _numpy() -> object:
    try:
        import numpy
    except ImportError as exc:
        raise InspectionExaminationFailure(
            "ONNX provider requires numpy for runtime tensor exchange"
        ) from exc
    return numpy


def _localization_from_input(
    inspection_input: StabilizedInspectionInput,
) -> DefectLocalization:
    digest = _digest(
        {
            "content_hash": inspection_input.content_hash,
            "input_id": inspection_input.input_id,
            "localization": "onnx-placeholder-boundary",
        }
    )
    width = 0.2
    height = 0.18
    x_min = round(0.05 + _unit_interval(digest[0:8]) * (0.95 - width), 6)
    y_min = round(0.05 + _unit_interval(digest[8:16]) * (0.95 - height), 6)
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=round(x_min + width, 6),
            y_max=round(y_min + height, 6),
        ),
        localization_kind="onnx_placeholder_suspected_region",
    )


def _stable_id(prefix: str, payload: Mapping[str, object]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _unit_interval(hex_fragment: str) -> float:
    return int(hex_fragment, 16) / float((16 ** len(hex_fragment)) - 1)


__all__ = [
    "ONNX_BOUNDARY_PROVIDER_ID",
    "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
    "OnnxInspectionInferenceProvider",
]
