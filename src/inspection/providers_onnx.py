from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
import io
import json
from math import isfinite
from pathlib import Path
from typing import Any

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
PADIM_ONNX_MODEL_REFERENCE_ID = "kalibra-padim-onnx-export-v1"

PADIM_MODEL_SHA256 = "0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a"
PADIM_ARTIFACT_RECORD_SHA256 = "6d6768cbd13d0a26dbfb817e676fc5ccddbb878b72f18e443dc403b531052f4f"
PADIM_METADATA_RECORD_SHA256 = "3dd299292c32a7d6616171ce26dd6d07a3d1c313dfc4dd00ea583dbca313f00d"
PADIM_EXPORT_REPLAY_SHA256 = "e2d7f28ed2412a509e384ad50509fc8e73d4f1347349683e4f89a4071be27093"
PADIM_ARTIFACT_HASHES_SHA256 = "d2e36f0ed4b6bd71c15fb4ce49c2481b5f1af4edc7b0ee034dc76386deed38c6"
PADIM_EQUIVALENCE_REPORT_SHA256 = "9741a1c77a5d0696e8c1c5d2687aed82270d0b9791492b0b47032bf70c69275d"
PADIM_EQUIVALENCE_REPLAY_SHA256 = "ef918b15edde5d07ae3f9889c014ef6647f8e2035d9f5e15fd876ef4e736a114"
PADIM_EQUIVALENCE_HASHES_SHA256 = "fec7ea31a3c5969d708820394c74f5a7b9b306b5287624508f40bf0bef63ffaa"

PADIM_MODEL_IDENTITY = "kalibra/inspection/padim-onnx-export"
PADIM_MODEL_VERSION = "1.0.0"
PADIM_EXPECTED_OPSET = 18
PADIM_EXPECTED_IR_VERSION = 10
PADIM_EXPORT_LABEL = "visa-padim-governed-onnx-export-v1"
PADIM_EQUIVALENCE_LABEL = "visa-padim-onnx-export-equivalence-v1"
PADIM_FEATURE_EXTRACTION_CONTRACT_ID = "kalibra-padim-rgb64-bilinear-float64-patch8-v1"
PADIM_FEATURE_EXTRACTION_SOURCE = "scripts/train_padim_baseline.py:extract_features"
PADIM_PREDICTION_JUDGEMENT_POLICY = (
    "contract_required_defect_for_raw_localization_no_threshold_v1"
)

PADIM_INPUT_FULL_PATCH_FEATURES = "full_patch_features"
PADIM_INPUT_CLASS_INDEX = "class_index"
PADIM_OUTPUT_PATCH_DISTANCES = "patch_mahalanobis_distances"
PADIM_OUTPUT_ANOMALY_MAP = "anomaly_map"
PADIM_OUTPUT_RAW_MEASURE = "raw_anomaly_measure"
PADIM_OUTPUT_ARGMAX_REGION = "argmax_region"

_MODEL_KIND_PADIM = "padim"
_MODEL_KIND_PLACEHOLDER = "placeholder"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_PADIM_ARTIFACT_DIR = _REPO_ROOT / "artifacts" / "padim"
_PADIM_MODEL_PATH = _PADIM_ARTIFACT_DIR / "model.onnx"
_PADIM_ARTIFACT_PATH = _PADIM_ARTIFACT_DIR / "artifact.json"
_PADIM_METADATA_PATH = _PADIM_ARTIFACT_DIR / "metadata.json"
_PADIM_EXPORT_REPLAY_PATH = _PADIM_ARTIFACT_DIR / "export_replay.json"
_PADIM_ARTIFACT_HASHES_PATH = _PADIM_ARTIFACT_DIR / "artifact_hashes.json"
_PADIM_EQUIVALENCE_DIR = _PADIM_ARTIFACT_DIR / "equivalence"
_PADIM_EQUIVALENCE_REPORT_PATH = _PADIM_EQUIVALENCE_DIR / "equivalence_report.json"
_PADIM_EQUIVALENCE_REPLAY_PATH = _PADIM_EQUIVALENCE_DIR / "equivalence_replay.json"
_PADIM_EQUIVALENCE_HASHES_PATH = _PADIM_EQUIVALENCE_DIR / "equivalence_hashes.json"

_PADIM_INPUT_CONTRACT = {
    PADIM_INPUT_FULL_PATCH_FEATURES: ("tensor(double)", (1, 64, 14)),
    PADIM_INPUT_CLASS_INDEX: ("tensor(int64)", (1,)),
}
_PADIM_OUTPUT_CONTRACT = {
    PADIM_OUTPUT_PATCH_DISTANCES: ("tensor(double)", (1, 64)),
    PADIM_OUTPUT_ANOMALY_MAP: ("tensor(double)", (1, 64, 64)),
    PADIM_OUTPUT_RAW_MEASURE: ("tensor(double)", (1,)),
    PADIM_OUTPUT_ARGMAX_REGION: ("tensor(double)", (1, 4)),
}
_PADIM_OUTPUT_ORDER = (
    PADIM_OUTPUT_PATCH_DISTANCES,
    PADIM_OUTPUT_ANOMALY_MAP,
    PADIM_OUTPUT_RAW_MEASURE,
    PADIM_OUTPUT_ARGMAX_REGION,
)


@dataclass(frozen=True)
class _PadimGovernanceRecords:
    artifact_record: Mapping[str, Any]
    metadata_record: Mapping[str, Any]
    export_replay: Mapping[str, Any]
    artifact_hashes: Mapping[str, Any]
    equivalence_report: Mapping[str, Any]
    equivalence_replay: Mapping[str, Any]
    equivalence_hashes: Mapping[str, Any]


@dataclass(frozen=True)
class _PadimFeatureInput:
    class_name: str
    class_index: int
    full_patch_features: object
    full_patch_features_sha256: str


@dataclass(frozen=True)
class OnnxInspectionInferenceProvider:
    session_configuration: onnx_session.OnnxSessionConfiguration = field(
        default_factory=lambda: governed_padim_session_configuration()
    )
    provider_id: str = ONNX_BOUNDARY_PROVIDER_ID
    defect_threshold: float = 50.0
    _session: object = field(init=False, repr=False, compare=False)
    _input_name: str | None = field(init=False, repr=False, compare=False)
    _configuration_hash: str = field(init=False, repr=False, compare=False)
    _model_kind: str = field(init=False, repr=False, compare=False)
    _requested_reference_id: str = field(init=False, repr=False, compare=False)
    _model_artifact_identity: str = field(init=False, repr=False, compare=False)
    _model_artifact_fingerprint: str = field(init=False, repr=False, compare=False)
    _model_content_sha256: str = field(init=False, repr=False, compare=False)
    _padim_class_order: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        configuration = onnx_session.validate_session_configuration(
            self.session_configuration
        )
        if not isfinite(self.defect_threshold):
            raise InspectionExaminationFailure(
                "ONNX provider defect threshold must be finite"
            )

        reference_id = configuration.model_reference.reference_id
        if reference_id == PADIM_ONNX_MODEL_REFERENCE_ID:
            records = _load_padim_governance_records()
            artifact = _padim_model_artifact(configuration, records)
            model_kind = _MODEL_KIND_PADIM
            class_order = _padim_class_order(records)
        elif reference_id == ONNX_PLACEHOLDER_MODEL_REFERENCE_ID:
            artifact = _placeholder_model_artifact(configuration)
            model_kind = _MODEL_KIND_PLACEHOLDER
            class_order = ()
        else:
            raise InspectionExaminationFailure(
                "ONNX provider model reference is not governed"
            )

        loaded_model = _load_provider_model(artifact, configuration)
        session = loaded_model._session_for_provider()
        input_name = None
        if model_kind == _MODEL_KIND_PADIM:
            _verify_padim_session_contract(session)
        else:
            input_name = _single_input_name(session)

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
        object.__setattr__(self, "_input_name", input_name)
        object.__setattr__(self, "_model_kind", model_kind)
        object.__setattr__(self, "_requested_reference_id", reference_id)
        object.__setattr__(
            self,
            "_model_artifact_identity",
            model_artifact.model_artifact_identity(loaded_model.artifact),
        )
        object.__setattr__(
            self,
            "_model_artifact_fingerprint",
            loaded_model.artifact_fingerprint,
        )
        object.__setattr__(
            self,
            "_model_content_sha256",
            loaded_model.model_content_sha256,
        )
        object.__setattr__(self, "_padim_class_order", class_order)

    def predict(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        if not isinstance(inspection_input, StabilizedInspectionInput):
            raise MalformedInspectionInput(
                "ONNX provider requires StabilizedInspectionInput"
            )
        if self._model_kind == _MODEL_KIND_PADIM:
            return self._predict_padim(inspection_input)
        return self._predict_placeholder(inspection_input)

    def _predict_padim(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        feature_input = _padim_feature_input(inspection_input, self._padim_class_order)
        raw_outputs = _run_padim_session(self._session, feature_input)
        mapped_output = _map_padim_output(raw_outputs, inspection_input)
        judgement = _inspection_judgement(mapped_output.predicted_status)
        localization = _localization_from_mapped_output(mapped_output)
        prediction_id = _stable_id(
            "padim-onnx-runtime-prediction",
            {
                "class_index": feature_input.class_index,
                "class_name": feature_input.class_name,
                "configuration_hash": self._configuration_hash,
                "full_patch_features_sha256": (
                    feature_input.full_patch_features_sha256
                ),
                "input_id": inspection_input.input_id,
                "localization": _localization_payload(localization),
                "model_reference_id": self._requested_reference_id,
                "output_mapping_contract_id": (
                    mapped_output.model_metadata["output_mapping_contract_id"]
                ),
                "provider_id": self.provider_id,
                "raw_measure": mapped_output.raw_anomaly_measure,
                "raw_measure_scale": (
                    mapped_output.model_metadata["raw_measure_scale"]
                ),
            },
        )
        model_metadata = self._base_model_metadata()
        model_metadata.update(
            {
                "class_name": feature_input.class_name,
                "class_index": str(feature_input.class_index),
                "feature_extraction_contract_id": (
                    PADIM_FEATURE_EXTRACTION_CONTRACT_ID
                ),
                "feature_extraction_source": PADIM_FEATURE_EXTRACTION_SOURCE,
                "full_patch_features_sha256": (
                    feature_input.full_patch_features_sha256
                ),
                "prediction_judgement_policy": PADIM_PREDICTION_JUDGEMENT_POLICY,
            }
        )
        model_metadata.update(mapped_output.model_metadata)

        return InspectionPrediction(
            input_id=inspection_input.input_id,
            prediction_id=prediction_id,
            predicted_judgement=judgement,
            predicted_raw_anomaly_measure=mapped_output.raw_anomaly_measure,
            predicted_localization=localization,
            raw_measure_scale=mapped_output.model_metadata["raw_measure_scale"],
            model_metadata=model_metadata,
        )

    def _predict_placeholder(
        self,
        inspection_input: StabilizedInspectionInput,
    ) -> InspectionPrediction:
        if self._input_name is None:
            raise InspectionExaminationFailure(
                "ONNX placeholder provider input name is unavailable"
            )
        preprocessed = _preprocess_input(inspection_input)
        raw_input = _input_tensor(preprocessed)
        raw_outputs = _run_placeholder_session(
            self._session,
            self._input_name,
            raw_input,
        )
        mapped_output = _map_placeholder_output(
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
                "preprocessing_contract_id": preprocessed.preprocessing_contract_id,
                "raw_measure": mapped_output.raw_anomaly_measure,
            },
        )
        model_metadata = self._base_model_metadata()
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

    def _base_model_metadata(self) -> dict[str, str]:
        return {
            "method": self.provider_id,
            "version": "1",
            "model_kind": self._model_kind,
            "model_reference_id": self._requested_reference_id,
            "loaded_model_identity": self._model_artifact_identity,
            "model_sha256": self._model_content_sha256,
            "model_artifact_fingerprint": self._model_artifact_fingerprint,
            "configuration_hash": self._configuration_hash,
            "loader": "model_loader.load_governed_model",
            "provider_private_session": "ProviderPrivateInferenceSession",
        }


def governed_padim_session_configuration() -> onnx_session.OnnxSessionConfiguration:
    return onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=PADIM_ONNX_MODEL_REFERENCE_ID,
            artifact_path=str(_PADIM_MODEL_PATH),
            content_sha256=PADIM_MODEL_SHA256,
        ),
        execution_providers=(
            onnx_session.OnnxExecutionProvider(
                name=onnx_session.DEFAULT_EXECUTION_PROVIDER,
            ),
        ),
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=1,
            inter_op_num_threads=1,
            optimization_level=onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL,
        ),
        execution_provider_policy=(
            onnx_session.EXECUTION_PROVIDER_POLICY_EXACT_ORDER
        ),
    )


def _padim_model_artifact(
    configuration: onnx_session.OnnxSessionConfiguration,
    records: _PadimGovernanceRecords,
) -> model_artifact.GovernedModelArtifact:
    reference = configuration.model_reference
    if reference.reference_id != PADIM_ONNX_MODEL_REFERENCE_ID:
        raise InspectionExaminationFailure(
            "ONNX PaDiM provider requires the governed PaDiM model reference"
        )
    configured_path = (
        _PADIM_MODEL_PATH
        if reference.artifact_path is None
        else Path(reference.artifact_path).expanduser().resolve()
    )
    if configured_path != _PADIM_MODEL_PATH.resolve():
        raise InspectionExaminationFailure(
            "ONNX PaDiM provider model path is not the governed artifact"
        )
    if (
        reference.content_sha256 is not None
        and reference.content_sha256 != PADIM_MODEL_SHA256
    ):
        raise InspectionExaminationFailure(
            "ONNX PaDiM provider model hash is not the governed artifact hash"
        )
    _validate_padim_governance(records)

    try:
        return model_artifact.canonical_model_artifact(
            identity=PADIM_MODEL_IDENTITY,
            version=PADIM_MODEL_VERSION,
            content_hash=PADIM_MODEL_SHA256,
            artifact_path=str(_PADIM_MODEL_PATH.resolve()),
            artifact_format=model_artifact.MODEL_ARTIFACT_FORMAT_ONNX,
            producer="Kalibra governed PaDiM ONNX export",
            provenance=(
                "Governed, export-equivalence-verified PaDiM ONNX artifact "
                "for bounded runtime provider integration"
            ),
            lineage=(
                ("artifact_record", "artifacts/padim/artifact.json"),
                ("metadata_record", "artifacts/padim/metadata.json"),
                (
                    "export_equivalence_record",
                    "artifacts/padim/equivalence/equivalence_report.json",
                ),
            ),
            framework_name=model_artifact.MODEL_FRAMEWORK_ONNX_RUNTIME,
            framework_version=str(records.metadata_record["toolchain"]["onnxruntime"]),
            onnx_opset=PADIM_EXPECTED_OPSET,
            compatibility_declaration=(
                "CPUExecutionProvider deterministic runtime integration only"
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InspectionExaminationFailure(
            "ONNX PaDiM model artifact construction failed"
        ) from exc


def _placeholder_model_artifact(
    configuration: onnx_session.OnnxSessionConfiguration,
) -> model_artifact.GovernedModelArtifact:
    model_reference = configuration.model_reference
    if model_reference.reference_id != ONNX_PLACEHOLDER_MODEL_REFERENCE_ID:
        raise InspectionExaminationFailure(
            "ONNX placeholder fixture requires the placeholder model reference"
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


def _load_provider_model(
    artifact: model_artifact.GovernedModelArtifact,
    configuration: onnx_session.OnnxSessionConfiguration,
) -> model_loader.ProviderPrivateLoadedModel:
    loader_configuration = _loader_session_configuration(artifact, configuration)
    try:
        return model_loader.load_governed_model(
            artifact,
            session_configuration=loader_configuration,
            expected_identity=artifact.identity,
            expected_version=artifact.version,
            expected_compatibility=artifact.metadata.compatibility,
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


def _load_padim_governance_records() -> _PadimGovernanceRecords:
    _verify_file_hash(_PADIM_MODEL_PATH, PADIM_MODEL_SHA256, "model.onnx")
    return _PadimGovernanceRecords(
        artifact_record=_read_json_mapping(_PADIM_ARTIFACT_PATH),
        metadata_record=_read_json_mapping(_PADIM_METADATA_PATH),
        export_replay=_read_json_mapping(_PADIM_EXPORT_REPLAY_PATH),
        artifact_hashes=_read_json_mapping(_PADIM_ARTIFACT_HASHES_PATH),
        equivalence_report=_read_json_mapping(_PADIM_EQUIVALENCE_REPORT_PATH),
        equivalence_replay=_read_json_mapping(_PADIM_EQUIVALENCE_REPLAY_PATH),
        equivalence_hashes=_read_json_mapping(_PADIM_EQUIVALENCE_HASHES_PATH),
    )


def _validate_padim_governance(records: _PadimGovernanceRecords) -> None:
    _verify_file_hash(_PADIM_ARTIFACT_PATH, PADIM_ARTIFACT_RECORD_SHA256, "artifact")
    _verify_file_hash(_PADIM_METADATA_PATH, PADIM_METADATA_RECORD_SHA256, "metadata")
    _verify_file_hash(_PADIM_EXPORT_REPLAY_PATH, PADIM_EXPORT_REPLAY_SHA256, "export replay")
    _verify_file_hash(
        _PADIM_ARTIFACT_HASHES_PATH,
        PADIM_ARTIFACT_HASHES_SHA256,
        "artifact hashes",
    )
    _verify_file_hash(
        _PADIM_EQUIVALENCE_REPORT_PATH,
        PADIM_EQUIVALENCE_REPORT_SHA256,
        "equivalence report",
    )
    _verify_file_hash(
        _PADIM_EQUIVALENCE_REPLAY_PATH,
        PADIM_EQUIVALENCE_REPLAY_SHA256,
        "equivalence replay",
    )
    _verify_file_hash(
        _PADIM_EQUIVALENCE_HASHES_PATH,
        PADIM_EQUIVALENCE_HASHES_SHA256,
        "equivalence hashes",
    )

    _validate_artifact_record(records.artifact_record)
    _validate_metadata_record(records.metadata_record)
    _validate_artifact_hashes(records.artifact_hashes)
    _validate_export_replay(records.export_replay)
    _validate_equivalence_records(
        records.equivalence_report,
        records.equivalence_replay,
        records.equivalence_hashes,
    )


def _validate_artifact_record(record: Mapping[str, Any]) -> None:
    graph = _required_mapping(record, "graph")
    if record.get("schema") != "kalibra_governed_padim_onnx_artifact_v1":
        raise InspectionExaminationFailure("unexpected PaDiM artifact schema")
    if record.get("model_reference_id") != PADIM_ONNX_MODEL_REFERENCE_ID:
        raise InspectionExaminationFailure("PaDiM artifact reference id mismatch")
    if record.get("model_sha256") != PADIM_MODEL_SHA256:
        raise InspectionExaminationFailure("PaDiM artifact model hash mismatch")
    if graph.get("opset_version") != PADIM_EXPECTED_OPSET:
        raise InspectionExaminationFailure("PaDiM artifact opset mismatch")
    if graph.get("ir_version") != PADIM_EXPECTED_IR_VERSION:
        raise InspectionExaminationFailure("PaDiM artifact IR version mismatch")
    if graph.get("preprocessing_reimplemented_in_onnx") is not False:
        raise InspectionExaminationFailure(
            "PaDiM artifact must not claim image preprocessing in ONNX"
        )
    output_contract = _required_mapping(graph, "output_contract")
    raw_measure = _required_mapping(output_contract, PADIM_OUTPUT_RAW_MEASURE)
    localization = _required_mapping(output_contract, PADIM_OUTPUT_ARGMAX_REGION)
    if raw_measure.get("identifier") != output_mapping.PADIM_RAW_MEASURE_SCALE:
        raise InspectionExaminationFailure("PaDiM raw-measure identity mismatch")
    if localization.get("identifier") != output_mapping.PADIM_LOCALIZATION_KIND:
        raise InspectionExaminationFailure("PaDiM localization identity mismatch")


def _validate_metadata_record(record: Mapping[str, Any]) -> None:
    if record.get("schema") != "kalibra_governed_padim_onnx_export_metadata_v1":
        raise InspectionExaminationFailure("unexpected PaDiM metadata schema")
    graph = _required_mapping(record, "graph")
    if graph.get("opset_version") != PADIM_EXPECTED_OPSET:
        raise InspectionExaminationFailure("PaDiM metadata opset mismatch")
    if graph.get("ir_version") != PADIM_EXPECTED_IR_VERSION:
        raise InspectionExaminationFailure("PaDiM metadata IR version mismatch")
    toolchain = _required_mapping(record, "toolchain")
    if toolchain.get("onnxruntime") != _framework_version_for_artifact():
        raise InspectionExaminationFailure(
            "PaDiM metadata ONNX Runtime version mismatch"
        )


def _validate_artifact_hashes(record: Mapping[str, Any]) -> None:
    if record.get("schema") != "kalibra_governed_padim_onnx_export_artifact_hashes_v1":
        raise InspectionExaminationFailure("unexpected PaDiM artifact-hashes schema")
    artifacts = _required_mapping(record, "governed_export_artifacts")
    expected = {
        "model.onnx": PADIM_MODEL_SHA256,
        "artifact.json": PADIM_ARTIFACT_RECORD_SHA256,
        "metadata.json": PADIM_METADATA_RECORD_SHA256,
        "export_replay.json": PADIM_EXPORT_REPLAY_SHA256,
    }
    for name, digest in expected.items():
        if artifacts.get(name) != digest:
            raise InspectionExaminationFailure(
                f"PaDiM artifact-hashes record mismatch for {name}"
            )


def _validate_export_replay(record: Mapping[str, Any]) -> None:
    if record.get("schema") != "kalibra_governed_padim_onnx_export_replay_v1":
        raise InspectionExaminationFailure("unexpected PaDiM export replay schema")
    if record.get("status") != "passed":
        raise InspectionExaminationFailure("PaDiM export replay is not passed")
    if record.get("complete_second_export") is not True:
        raise InspectionExaminationFailure("PaDiM export replay is incomplete")
    comparisons = _required_mapping(record, "comparisons")
    if not all(value is True for value in comparisons.values()):
        raise InspectionExaminationFailure("PaDiM export replay comparison failed")


def _validate_equivalence_records(
    report: Mapping[str, Any],
    replay: Mapping[str, Any],
    hashes: Mapping[str, Any],
) -> None:
    if report.get("schema") != "kalibra_padim_onnx_export_equivalence_report_v1":
        raise InspectionExaminationFailure("unexpected PaDiM equivalence report schema")
    if report.get("equivalence_label") != PADIM_EQUIVALENCE_LABEL:
        raise InspectionExaminationFailure("PaDiM equivalence label mismatch")
    if report.get("status") != "passed" or report.get("final_pass_fail_status") != "passed":
        raise InspectionExaminationFailure("PaDiM export equivalence is not passed")
    identity = _required_mapping(report, "onnx_artifact_identity")
    expected_identity = {
        "artifact_hashes_record_sha256": PADIM_ARTIFACT_HASHES_SHA256,
        "artifact_record_sha256": PADIM_ARTIFACT_RECORD_SHA256,
        "export_label": PADIM_EXPORT_LABEL,
        "export_replay_sha256": PADIM_EXPORT_REPLAY_SHA256,
        "ir_version": PADIM_EXPECTED_IR_VERSION,
        "metadata_record_sha256": PADIM_METADATA_RECORD_SHA256,
        "model_path": "artifacts/padim/model.onnx",
        "model_reference_id": PADIM_ONNX_MODEL_REFERENCE_ID,
        "model_sha256": PADIM_MODEL_SHA256,
        "opset_version": PADIM_EXPECTED_OPSET,
    }
    if dict(identity) != expected_identity:
        raise InspectionExaminationFailure("PaDiM equivalence artifact identity mismatch")
    artifact_verification = _required_mapping(report, "artifact_verification")
    graph_verification = _required_mapping(report, "graph_contract_verification")
    if artifact_verification.get("status") != "passed":
        raise InspectionExaminationFailure("PaDiM artifact verification is not passed")
    if graph_verification.get("status") != "passed":
        raise InspectionExaminationFailure("PaDiM graph verification is not passed")

    if replay.get("schema") != "kalibra_padim_onnx_export_equivalence_replay_v1":
        raise InspectionExaminationFailure("unexpected PaDiM equivalence replay schema")
    if replay.get("status") != "passed":
        raise InspectionExaminationFailure("PaDiM equivalence replay is not passed")
    if replay.get("complete_second_equivalence_run") is not True:
        raise InspectionExaminationFailure("PaDiM equivalence replay is incomplete")
    comparisons = _required_mapping(replay, "comparisons")
    if not all(value is True for value in comparisons.values()):
        raise InspectionExaminationFailure("PaDiM equivalence replay comparison failed")

    if hashes.get("schema") != "kalibra_padim_onnx_export_equivalence_hashes_v1":
        raise InspectionExaminationFailure("unexpected PaDiM equivalence hashes schema")
    artifacts = _required_mapping(hashes, "governed_equivalence_artifacts")
    if artifacts.get("equivalence_report.json") != PADIM_EQUIVALENCE_REPORT_SHA256:
        raise InspectionExaminationFailure("PaDiM equivalence report hash mismatch")
    if artifacts.get("equivalence_replay.json") != PADIM_EQUIVALENCE_REPLAY_SHA256:
        raise InspectionExaminationFailure("PaDiM equivalence replay hash mismatch")


def _padim_class_order(records: _PadimGovernanceRecords) -> tuple[str, ...]:
    provenance = _required_mapping(records.artifact_record, "provenance")
    c4 = _required_mapping(provenance, "c4_fitted_baseline")
    class_order = c4.get("class_order")
    if not isinstance(class_order, Sequence) or isinstance(class_order, (str, bytes)):
        raise InspectionExaminationFailure("PaDiM class order is missing")
    normalized = tuple(value for value in class_order if isinstance(value, str) and value)
    if len(normalized) != len(class_order):
        raise InspectionExaminationFailure("PaDiM class order is invalid")
    return normalized


def _verify_padim_session_contract(session: object) -> None:
    inputs = _session_value_info(session, "get_inputs", "input")
    outputs = _session_value_info(session, "get_outputs", "output")
    input_names = tuple(_value_info_name(value) for value in inputs)
    output_names = tuple(_value_info_name(value) for value in outputs)
    if set(input_names) != set(_PADIM_INPUT_CONTRACT):
        raise InspectionExaminationFailure("PaDiM ONNX input contract mismatch")
    if output_names != _PADIM_OUTPUT_ORDER:
        raise InspectionExaminationFailure("PaDiM ONNX output contract mismatch")
    for value in inputs:
        name = _value_info_name(value)
        expected_type, expected_shape = _PADIM_INPUT_CONTRACT[name]
        _validate_value_info(value, expected_type, expected_shape, name)
    for value in outputs:
        name = _value_info_name(value)
        expected_type, expected_shape = _PADIM_OUTPUT_CONTRACT[name]
        _validate_value_info(value, expected_type, expected_shape, name)


def _session_value_info(session: object, method_name: str, label: str) -> tuple[object, ...]:
    method = getattr(session, method_name, None)
    if not callable(method):
        raise InspectionExaminationFailure(
            f"ONNX Runtime session does not expose {label} metadata"
        )
    values = tuple(method())
    if not values:
        raise InspectionExaminationFailure(f"ONNX Runtime session exposes no {label}s")
    return values


def _value_info_name(value: object) -> str:
    name = getattr(value, "name", None)
    if not isinstance(name, str) or not name.strip():
        raise InspectionExaminationFailure("ONNX Runtime value metadata name is invalid")
    return name


def _validate_value_info(
    value: object,
    expected_type: str,
    expected_shape: tuple[int, ...],
    label: str,
) -> None:
    actual_type = getattr(value, "type", None)
    if actual_type != expected_type:
        raise InspectionExaminationFailure(f"ONNX {label} dtype mismatch")
    try:
        actual_shape = tuple(int(dimension) for dimension in getattr(value, "shape"))
    except (TypeError, ValueError) as exc:
        raise InspectionExaminationFailure(f"ONNX {label} shape is invalid") from exc
    if actual_shape != expected_shape:
        raise InspectionExaminationFailure(f"ONNX {label} shape mismatch")


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


def _run_placeholder_session(session: object, input_name: str, raw_input: object) -> object:
    run = getattr(session, "run", None)
    if not callable(run):
        raise InspectionExaminationFailure("ONNX Runtime session cannot run")
    try:
        outputs = run(None, {input_name: raw_input})
    except Exception as exc:
        raise InspectionExaminationFailure("ONNX Runtime inference failed") from exc
    return outputs


def _run_padim_session(session: object, feature_input: _PadimFeatureInput) -> object:
    run = getattr(session, "run", None)
    if not callable(run):
        raise InspectionExaminationFailure("ONNX Runtime session cannot run")
    try:
        outputs = run(
            None,
            {
                PADIM_INPUT_FULL_PATCH_FEATURES: feature_input.full_patch_features,
                PADIM_INPUT_CLASS_INDEX: _numpy().asarray(
                    [feature_input.class_index],
                    dtype="int64",
                ),
            },
        )
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


def _padim_feature_input(
    inspection_input: StabilizedInspectionInput,
    class_order: tuple[str, ...],
) -> _PadimFeatureInput:
    class_name = _padim_class_name(inspection_input.metadata)
    try:
        class_index = class_order.index(class_name)
    except ValueError as exc:
        raise InspectionExaminationFailure(
            "ONNX PaDiM class name is not in governed class order"
        ) from exc
    image_path = Path(inspection_input.artifact_uri).expanduser().resolve()
    if not image_path.is_file():
        raise InspectionExaminationFailure("ONNX PaDiM input image is missing")
    if _sha256_file(image_path) != inspection_input.content_hash:
        raise InspectionExaminationFailure("ONNX PaDiM input content hash mismatch")
    training = _padim_training_module()
    try:
        features = training.extract_features(image_path, training.FitConfig())
    except Exception as exc:
        raise InspectionExaminationFailure(
            "ONNX PaDiM governed feature extraction failed"
        ) from exc
    numpy = _numpy()
    full_patch_features = numpy.ascontiguousarray(features, dtype="float64")
    if tuple(full_patch_features.shape) != (64, 14):
        raise InspectionExaminationFailure("ONNX PaDiM feature tensor shape mismatch")
    return _PadimFeatureInput(
        class_name=class_name,
        class_index=class_index,
        full_patch_features=full_patch_features.reshape((1, 64, 14)),
        full_patch_features_sha256=_npy_sha256(full_patch_features),
    )


def _padim_class_name(metadata: Mapping[str, str]) -> str:
    for key in ("class_name", "padim_class_name"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise InspectionExaminationFailure(
        "ONNX PaDiM provider requires governed class_name metadata"
    )


def _padim_training_module() -> object:
    try:
        from scripts import train_padim_baseline
    except ImportError as exc:
        raise InspectionExaminationFailure(
            "ONNX PaDiM provider requires governed offline feature extraction"
        ) from exc
    return train_padim_baseline


def _map_placeholder_output(
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


def _map_padim_output(
    raw_outputs: object,
    inspection_input: StabilizedInspectionInput,
) -> output_mapping.MappedModelOutput:
    try:
        return output_mapping.map_padim_onnx_outputs(
            raw_outputs,
            input_id=inspection_input.input_id,
            content_hash=inspection_input.content_hash,
            feature_extraction_contract_id=PADIM_FEATURE_EXTRACTION_CONTRACT_ID,
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
        label="raw_anomaly_maximum"
        if mapped_localization.localization_kind == output_mapping.PADIM_LOCALIZATION_KIND
        else None,
        localization_kind=mapped_localization.localization_kind,
    )


def _localization_payload(localization: DefectLocalization | None) -> object:
    if localization is None:
        return None
    return {
        "localization_kind": localization.localization_kind,
        "x_min": localization.region.x_min,
        "x_max": localization.region.x_max,
        "y_min": localization.region.y_min,
        "y_max": localization.region.y_max,
    }


def _read_json_mapping(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InspectionExaminationFailure(
            f"governed PaDiM record is unreadable: {path}"
        ) from exc
    if not isinstance(value, Mapping):
        raise InspectionExaminationFailure(
            f"governed PaDiM record is not an object: {path}"
        )
    return value


def _required_mapping(record: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = record.get(key)
    if not isinstance(value, Mapping):
        raise InspectionExaminationFailure(f"governed PaDiM record lacks {key}")
    return value


def _verify_file_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise InspectionExaminationFailure(f"missing governed PaDiM {label}")
    actual = _sha256_file(path)
    if actual != expected:
        raise InspectionExaminationFailure(
            f"governed PaDiM {label} hash mismatch"
        )


def _sha256_file(path: Path) -> str:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise InspectionExaminationFailure(f"file is unreadable: {path}") from exc


def _npy_sha256(array: object) -> str:
    buffer = io.BytesIO()
    _numpy().save(buffer, array, allow_pickle=False)
    return sha256(buffer.getvalue()).hexdigest()


def _stable_id(prefix: str, payload: Mapping[str, object]) -> str:
    return f"{prefix}:{_digest(payload)[:32]}"


def _digest(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "ONNX_BOUNDARY_PROVIDER_ID",
    "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
    "PADIM_ONNX_MODEL_REFERENCE_ID",
    "OnnxInspectionInferenceProvider",
    "governed_padim_session_configuration",
]
