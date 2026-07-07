#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import governed_visa_acquisition as acquisition  # noqa: E402
import padim_inference as inference  # noqa: E402
import train_padim_baseline as training  # noqa: E402


ARTIFACT_DIR = REPO_ROOT / "artifacts" / "padim"
MODEL_PATH = ARTIFACT_DIR / "model.onnx"
ARTIFACT_RECORD_PATH = ARTIFACT_DIR / "artifact.json"
ARTIFACT_HASHES_PATH = ARTIFACT_DIR / "artifact_hashes.json"
METADATA_PATH = ARTIFACT_DIR / "metadata.json"
EXPORT_REPLAY_PATH = ARTIFACT_DIR / "export_replay.json"
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md"
)

EXPORT_LABEL = "visa-padim-governed-onnx-export-v1"
MODEL_REFERENCE_ID = "kalibra-padim-onnx-export-v1"
MODEL_SCHEMA = "kalibra_governed_padim_onnx_artifact_v1"
METADATA_SCHEMA = "kalibra_governed_padim_onnx_export_metadata_v1"
ARTIFACT_HASHES_SCHEMA = "kalibra_governed_padim_onnx_export_artifact_hashes_v1"
EXPORT_REPLAY_SCHEMA = "kalibra_governed_padim_onnx_export_replay_v1"

ONNX_OPSET_VERSION = 18
ONNX_IR_VERSION = 10
GRAPH_NAME = "kalibra_governed_padim_scorer_v1"
ONNX_DTYPE_NAME = "float64"
ONNX_TENSOR_TYPE = TensorProto.DOUBLE

ABSOLUTE_TOLERANCE = 1.0e-12
RELATIVE_TOLERANCE = 1.0e-12
BBOX_ABSOLUTE_TOLERANCE = 0.0

INPUT_FULL_PATCH_FEATURES = "full_patch_features"
INPUT_CLASS_INDEX = "class_index"
OUTPUT_PATCH_DISTANCES = "patch_mahalanobis_distances"
OUTPUT_ANOMALY_MAP = "anomaly_map"
OUTPUT_RAW_MEASURE = "raw_anomaly_measure"
OUTPUT_ARGMAX_REGION = "argmax_region"


class ExportError(RuntimeError):
    """Raised when governed ONNX export cannot proceed safely."""


@dataclass(frozen=True)
class C5Reference:
    artifact_hashes: dict[str, Any]
    artifact_hashes_sha256: str
    inference_metadata: dict[str, Any]
    inference_metadata_sha256: str
    replay_record: dict[str, Any]
    replay_sha256: str


@dataclass(frozen=True)
class ExportInputs:
    config: training.FitConfig
    governed: dict[str, Any]
    artifacts: inference.GovernedArtifacts
    c5_reference: C5Reference


@dataclass(frozen=True)
class GraphVerification:
    feature_indices_unchanged: bool
    mu_unchanged: bool
    covariance_inverse_unchanged: bool
    output_contract_matches_metadata: bool
    model_input_names: tuple[str, ...]
    model_output_names: tuple[str, ...]


@dataclass(frozen=True)
class ExportBuild:
    model_bytes: bytes
    artifact_record: dict[str, Any]
    metadata_record: dict[str, Any]
    artifact_bytes: bytes
    metadata_bytes: bytes


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise ExportError(f"missing governed record: {path}") from exc
    if not isinstance(value, dict):
        raise ExportError(f"governed record is not a JSON object: {path}")
    return value


def write_governed_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise ExportError(f"governed export artifact changed: {path}")
        return acquisition.sha256_file(path)
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def write_json_record(path: Path, value: Mapping[str, Any]) -> str:
    return write_governed_bytes(path, canonical_json_bytes(value))


def verify_file_hash(path: Path, expected: str, label: str) -> str:
    if not path.exists():
        raise ExportError(f"missing governed artifact for {label}: {path}")
    actual = acquisition.sha256_file(path)
    if actual != expected:
        raise ExportError(
            f"governed artifact hash mismatch for {label}: expected {expected}, got {actual}"
        )
    return actual


def ensure_layout() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)


def export_timestamp_for_run() -> str:
    if not METADATA_PATH.exists():
        return utc_timestamp()
    metadata = read_json_mapping(METADATA_PATH)
    timestamp = metadata.get("export_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise ExportError("existing export metadata lacks export timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text().splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise ExportError("existing export evidence lacks Date field")


def load_c5_reference(artifacts: inference.GovernedArtifacts) -> C5Reference:
    artifact_hashes = read_json_mapping(inference.INFERENCE_ARTIFACT_HASHES_PATH)
    if artifact_hashes.get("schema") != inference.INFERENCE_ARTIFACT_HASHES_SCHEMA:
        raise ExportError("unexpected C-5 inference artifact hash schema")
    artifact_hashes_sha256 = acquisition.sha256_file(inference.INFERENCE_ARTIFACT_HASHES_PATH)

    metadata_artifacts = artifact_hashes.get("metadata_artifacts")
    if not isinstance(metadata_artifacts, Mapping):
        raise ExportError("C-5 artifact hashes lack metadata artifacts")
    for relative_path, expected_digest in metadata_artifacts.items():
        if not isinstance(relative_path, str) or not isinstance(expected_digest, str):
            raise ExportError("invalid C-5 metadata artifact hash entry")
        verify_file_hash(inference.INFERENCE_DIR / relative_path, expected_digest, relative_path)

    local_outputs = artifact_hashes.get("local_output_artifacts")
    if not isinstance(local_outputs, Mapping):
        raise ExportError("C-5 artifact hashes lack local output artifacts")
    for relative_path, expected_digest in local_outputs.items():
        if not isinstance(relative_path, str) or not isinstance(expected_digest, str):
            raise ExportError("invalid C-5 local output artifact hash entry")
        verify_file_hash(inference.INFERENCE_DIR / relative_path, expected_digest, relative_path)

    replay_info = artifact_hashes.get("replay_verification")
    if not isinstance(replay_info, Mapping):
        raise ExportError("C-5 artifact hashes lack replay verification")
    replay_path = REPO_ROOT / str(replay_info.get("path", ""))
    replay_sha256 = replay_info.get("sha256")
    if not isinstance(replay_sha256, str):
        raise ExportError("C-5 replay hash is missing")
    verify_file_hash(replay_path, replay_sha256, "C-5 replay verification")
    replay_record = read_json_mapping(replay_path)
    if replay_record.get("status") != "passed":
        raise ExportError("C-5 replay verification is not passed")

    metadata_path = inference.INFERENCE_METADATA_DIR / "inference_metadata.json"
    inference_metadata_sha256 = verify_file_hash(
        metadata_path,
        str(metadata_artifacts.get("metadata/inference_metadata.json")),
        "C-5 inference metadata",
    )
    inference_metadata = read_json_mapping(metadata_path)
    if inference_metadata.get("schema") != inference.INFERENCE_RECORD_SCHEMA:
        raise ExportError("unexpected C-5 inference metadata schema")
    if inference_metadata.get("aggregation_identifier") != inference.AGGREGATION_IDENTIFIER:
        raise ExportError("C-5 aggregation identifier is not the governed reference")
    if inference_metadata.get("localization_identifier") != inference.LOCALIZATION_IDENTIFIER:
        raise ExportError("C-5 localization identifier is not the governed reference")

    artifact_identity = inference_metadata.get("artifact_identity")
    if not isinstance(artifact_identity, Mapping):
        raise ExportError("C-5 inference metadata lacks artifact identity")
    expected_identity = artifacts.artifact_identity
    for key in (
        "training_record_sha256",
        "training_artifact_hashes_sha256",
        "training_metadata_sha256",
        "training_replay_verification_sha256",
        "mu_by_class_sha256",
        "covariance_inverse_by_class_sha256",
        "feature_indices_sha256",
    ):
        if artifact_identity.get(key) != expected_identity.get(key):
            raise ExportError(f"C-5 reference does not match C-4 artifact identity: {key}")
    if inference_metadata.get("scope_boundaries", {}).get("evaluation_executed") is not False:
        raise ExportError("C-5 metadata scope boundary is not export-safe")

    return C5Reference(
        artifact_hashes=dict(artifact_hashes),
        artifact_hashes_sha256=artifact_hashes_sha256,
        inference_metadata=dict(inference_metadata),
        inference_metadata_sha256=inference_metadata_sha256,
        replay_record=dict(replay_record),
        replay_sha256=replay_sha256,
    )


def load_export_inputs() -> ExportInputs:
    config = training.FitConfig()
    governed = training.verify_governed_acquisition()
    artifacts = inference.load_governed_artifacts(governed, config)
    verify_authorized_c4_artifact_set(artifacts)
    c5_reference = load_c5_reference(artifacts)
    return ExportInputs(
        config=config,
        governed=dict(governed),
        artifacts=artifacts,
        c5_reference=c5_reference,
    )


def verify_authorized_c4_artifact_set(artifacts: inference.GovernedArtifacts) -> None:
    artifact_hashes = artifacts.training_artifact_hashes
    required_arrays = (
        "statistics/mu_by_class.npy",
        "covariance/covariance_inverse_by_class.npy",
        "statistics/feature_indices.npy",
    )
    required_metadata = (
        "metadata/feature_indices.json",
        "metadata/numerical_config.json",
        "metadata/preprocessing_contract.json",
        "metadata/backbone_metadata.json",
    )
    required_records = (
        training.TRAINING_DIR / "artifact_hashes.json",
        training.TRAINING_DIR / "training_record.json",
    )
    array_hashes = artifact_hashes.get("array_artifacts")
    metadata_hashes = artifact_hashes.get("metadata_artifacts")
    if not isinstance(array_hashes, Mapping) or not isinstance(metadata_hashes, Mapping):
        raise ExportError("C-4 artifact hashes lack required sections")
    for relative_path in required_arrays:
        expected = array_hashes.get(relative_path)
        if not isinstance(expected, str):
            raise ExportError(f"C-4 hash record lacks {relative_path}")
        verify_file_hash(training.PADIM_ROOT / relative_path, expected, relative_path)
    for relative_path in required_metadata:
        expected = metadata_hashes.get(relative_path)
        if not isinstance(expected, str):
            raise ExportError(f"C-4 hash record lacks {relative_path}")
        verify_file_hash(training.PADIM_ROOT / relative_path, expected, relative_path)
    training_metadata_sha256 = artifacts.training_record.get("training_metadata_sha256")
    if not isinstance(training_metadata_sha256, str):
        raise ExportError("C-4 training record lacks training metadata hash")
    verify_file_hash(
        training.METADATA_DIR / "training_metadata.json",
        training_metadata_sha256,
        "metadata/training_metadata.json",
    )
    for path in required_records:
        if not path.exists():
            raise ExportError(f"missing governed C-4 record: {path}")


def toolchain_versions() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "onnx": onnx.__version__,
        "onnxruntime": ort.__version__,
    }


def dtype_policy() -> dict[str, Any]:
    return {
        "dtype_source": training.DTYPE_NAME,
        "onnx_dtype": ONNX_DTYPE_NAME,
        "precision_policy": (
            "preserve the C-4 float64 numerical contract in ONNX DOUBLE tensors; "
            "no float32 execution transition is introduced by export"
        ),
        "float32_transition": False,
        "expected_fidelity_tolerance": {
            "absolute": ABSOLUTE_TOLERANCE,
            "relative": RELATIVE_TOLERANCE,
            "bbox_absolute": BBOX_ABSOLUTE_TOLERANCE,
        },
        "reason": (
            "ONNX Runtime CPUExecutionProvider supports the arithmetic used by this "
            "export with DOUBLE tensors, so the governed C-4 dtype can be preserved."
        ),
    }


def graph_input_contract() -> dict[str, Any]:
    return {
        INPUT_FULL_PATCH_FEATURES: {
            "dtype": ONNX_DTYPE_NAME,
            "shape": [1, training.FitConfig().patch_count, training.FULL_FEATURE_DIMENSION],
            "semantics": (
                "C-4 deterministic full patch feature tensor before governed feature "
                "subsampling; preprocessing contract remains "
                f"{training.PREPROCESSING_CONTRACT_ID}"
            ),
        },
        INPUT_CLASS_INDEX: {
            "dtype": "int64",
            "shape": [1],
            "semantics": "index into the governed C-4 class_order recorded in artifact.json",
        },
    }


def graph_output_contract() -> dict[str, Any]:
    return {
        OUTPUT_PATCH_DISTANCES: {
            "dtype": ONNX_DTYPE_NAME,
            "shape": [1, training.FitConfig().patch_count],
            "semantics": "per-patch Mahalanobis distance after governed feature selection",
        },
        OUTPUT_ANOMALY_MAP: {
            "dtype": ONNX_DTYPE_NAME,
            "shape": [1, training.IMAGE_SIZE, training.IMAGE_SIZE],
            "aggregation_source": inference.AGGREGATION_IDENTIFIER,
            "semantics": "8x8 patch distances repeated over 8x8 pixel cells",
        },
        OUTPUT_RAW_MEASURE: {
            "dtype": ONNX_DTYPE_NAME,
            "shape": [1],
            "identifier": inference.AGGREGATION_IDENTIFIER,
            "semantics": inference.AGGREGATION_POLICY,
        },
        OUTPUT_ARGMAX_REGION: {
            "dtype": ONNX_DTYPE_NAME,
            "shape": [1, 4],
            "identifier": inference.LOCALIZATION_IDENTIFIER,
            "order": ["x_min", "y_min", "x_max", "y_max"],
            "semantics": inference.LOCALIZATION_POLICY,
        },
    }


def make_tensor(name: str, array: np.ndarray) -> onnx.TensorProto:
    return numpy_helper.from_array(np.ascontiguousarray(array), name=name)


def make_scalar(name: str, value: float) -> onnx.TensorProto:
    return numpy_helper.from_array(np.asarray(value, dtype=np.float64), name=name)


def build_onnx_model_bytes(artifacts: inference.GovernedArtifacts) -> bytes:
    config = training.FitConfig()
    row_indices = np.repeat(
        np.arange(config.image_size, dtype=np.float64).reshape(1, config.image_size, 1),
        config.image_size,
        axis=2,
    )
    col_indices = np.repeat(
        np.arange(config.image_size, dtype=np.float64).reshape(1, 1, config.image_size),
        config.image_size,
        axis=1,
    )
    initializers = [
        make_tensor("feature_indices", artifacts.feature_indices.astype(np.int64)),
        make_tensor("mu_by_class", artifacts.mu.astype(np.float64)),
        make_tensor("covariance_inverse_by_class", artifacts.covariance_inverse.astype(np.float64)),
        make_scalar("zero", 0.0),
        make_tensor("tile_input_shape", np.array([1, 8, 1, 8, 1], dtype=np.int64)),
        make_tensor("tile_repeats", np.array([1, 1, 8, 1, 8], dtype=np.int64)),
        make_tensor("anomaly_map_shape", np.array([1, 64, 64], dtype=np.int64)),
        make_tensor("raw_measure_axes", np.array([1, 2], dtype=np.int64)),
        make_tensor("raw_measure_broadcast_shape", np.array([1, 1, 1], dtype=np.int64)),
        make_tensor("row_indices", row_indices),
        make_tensor("col_indices", col_indices),
        make_scalar("high_sentinel", float(config.image_size)),
        make_scalar("low_sentinel", -1.0),
        make_scalar("image_size", float(config.image_size)),
        make_scalar("one", 1.0),
        make_tensor("argmax_region_shape", np.array([1, 4], dtype=np.int64)),
    ]
    nodes = [
        helper.make_node(
            "Gather",
            [INPUT_FULL_PATCH_FEATURES, "feature_indices"],
            ["selected_features"],
            axis=2,
            name="gather_governed_feature_indices",
        ),
        helper.make_node(
            "Gather",
            ["mu_by_class", INPUT_CLASS_INDEX],
            ["mu_selected_class"],
            axis=0,
            name="gather_mu_for_class",
        ),
        helper.make_node(
            "Gather",
            ["covariance_inverse_by_class", INPUT_CLASS_INDEX],
            ["covariance_inverse_selected_class"],
            axis=0,
            name="gather_covariance_inverse_for_class",
        ),
        helper.make_node(
            "Sub",
            ["selected_features", "mu_selected_class"],
            ["feature_delta"],
            name="subtract_mu",
        ),
        helper.make_node(
            "Einsum",
            [
                "feature_delta",
                "covariance_inverse_selected_class",
                "feature_delta",
            ],
            ["squared_mahalanobis"],
            equation="bpi,bpij,bpj->bp",
            name="patch_squared_mahalanobis",
        ),
        helper.make_node(
            "Max",
            ["squared_mahalanobis", "zero"],
            ["nonnegative_squared_mahalanobis"],
            name="clip_negative_roundoff",
        ),
        helper.make_node(
            "Sqrt",
            ["nonnegative_squared_mahalanobis"],
            [OUTPUT_PATCH_DISTANCES],
            name="patch_mahalanobis_distance",
        ),
        helper.make_node(
            "Reshape",
            [OUTPUT_PATCH_DISTANCES, "tile_input_shape"],
            ["patch_grid_for_tile"],
            name="reshape_patch_distances_for_repeat",
        ),
        helper.make_node(
            "Tile",
            ["patch_grid_for_tile", "tile_repeats"],
            ["tiled_patch_grid"],
            name="repeat_patch_distances_to_pixels",
        ),
        helper.make_node(
            "Reshape",
            ["tiled_patch_grid", "anomaly_map_shape"],
            [OUTPUT_ANOMALY_MAP],
            name="reshape_repeated_grid_to_anomaly_map",
        ),
        helper.make_node(
            "ReduceMax",
            [OUTPUT_ANOMALY_MAP, "raw_measure_axes"],
            [OUTPUT_RAW_MEASURE],
            keepdims=0,
            name="aggregate_raw_anomaly_measure",
        ),
        helper.make_node(
            "Reshape",
            [OUTPUT_RAW_MEASURE, "raw_measure_broadcast_shape"],
            ["raw_measure_for_mask"],
            name="reshape_raw_measure_for_mask",
        ),
        helper.make_node(
            "Equal",
            [OUTPUT_ANOMALY_MAP, "raw_measure_for_mask"],
            ["argmax_mask"],
            name="argmax_region_mask",
        ),
        helper.make_node(
            "Where",
            ["argmax_mask", "row_indices", "high_sentinel"],
            ["row_min_candidates"],
            name="row_min_candidates",
        ),
        helper.make_node(
            "ReduceMin",
            ["row_min_candidates", "raw_measure_axes"],
            ["y_min_pixel"],
            keepdims=0,
            name="y_min_pixel",
        ),
        helper.make_node(
            "Where",
            ["argmax_mask", "row_indices", "low_sentinel"],
            ["row_max_candidates"],
            name="row_max_candidates",
        ),
        helper.make_node(
            "ReduceMax",
            ["row_max_candidates", "raw_measure_axes"],
            ["y_max_pixel"],
            keepdims=0,
            name="y_max_pixel",
        ),
        helper.make_node(
            "Where",
            ["argmax_mask", "col_indices", "high_sentinel"],
            ["col_min_candidates"],
            name="col_min_candidates",
        ),
        helper.make_node(
            "ReduceMin",
            ["col_min_candidates", "raw_measure_axes"],
            ["x_min_pixel"],
            keepdims=0,
            name="x_min_pixel",
        ),
        helper.make_node(
            "Where",
            ["argmax_mask", "col_indices", "low_sentinel"],
            ["col_max_candidates"],
            name="col_max_candidates",
        ),
        helper.make_node(
            "ReduceMax",
            ["col_max_candidates", "raw_measure_axes"],
            ["x_max_pixel"],
            keepdims=0,
            name="x_max_pixel",
        ),
        helper.make_node(
            "Div",
            ["x_min_pixel", "image_size"],
            ["x_min_normalized"],
            name="x_min_normalized",
        ),
        helper.make_node(
            "Div",
            ["y_min_pixel", "image_size"],
            ["y_min_normalized"],
            name="y_min_normalized",
        ),
        helper.make_node(
            "Add",
            ["x_max_pixel", "one"],
            ["x_max_exclusive_pixel"],
            name="x_max_exclusive_pixel",
        ),
        helper.make_node(
            "Add",
            ["y_max_pixel", "one"],
            ["y_max_exclusive_pixel"],
            name="y_max_exclusive_pixel",
        ),
        helper.make_node(
            "Div",
            ["x_max_exclusive_pixel", "image_size"],
            ["x_max_normalized"],
            name="x_max_normalized",
        ),
        helper.make_node(
            "Div",
            ["y_max_exclusive_pixel", "image_size"],
            ["y_max_normalized"],
            name="y_max_normalized",
        ),
        helper.make_node(
            "Concat",
            [
                "x_min_normalized",
                "y_min_normalized",
                "x_max_normalized",
                "y_max_normalized",
            ],
            ["argmax_region_flat"],
            axis=0,
            name="argmax_region_concatenate",
        ),
        helper.make_node(
            "Reshape",
            ["argmax_region_flat", "argmax_region_shape"],
            [OUTPUT_ARGMAX_REGION],
            name="reshape_argmax_region",
        ),
    ]
    graph = helper.make_graph(
        nodes,
        GRAPH_NAME,
        [
            helper.make_tensor_value_info(
                INPUT_FULL_PATCH_FEATURES,
                ONNX_TENSOR_TYPE,
                [1, config.patch_count, config.full_feature_dimension],
            ),
            helper.make_tensor_value_info(INPUT_CLASS_INDEX, TensorProto.INT64, [1]),
        ],
        [
            helper.make_tensor_value_info(
                OUTPUT_PATCH_DISTANCES,
                ONNX_TENSOR_TYPE,
                [1, config.patch_count],
            ),
            helper.make_tensor_value_info(
                OUTPUT_ANOMALY_MAP,
                ONNX_TENSOR_TYPE,
                [1, config.image_size, config.image_size],
            ),
            helper.make_tensor_value_info(OUTPUT_RAW_MEASURE, ONNX_TENSOR_TYPE, [1]),
            helper.make_tensor_value_info(OUTPUT_ARGMAX_REGION, ONNX_TENSOR_TYPE, [1, 4]),
        ],
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name="kalibra-governed-padim-onnx-export",
        producer_version="1.0.0",
        domain="kalibra.governed.export",
        model_version=1,
        opset_imports=[helper.make_operatorsetid("", ONNX_OPSET_VERSION)],
    )
    model.ir_version = ONNX_IR_VERSION
    helper.set_model_props(
        model,
        {
            "kalibra_export_label": EXPORT_LABEL,
            "model_reference_id": MODEL_REFERENCE_ID,
            "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
            "backbone_identity": training.BACKBONE_IDENTITY,
            "selected_layer": training.BACKBONE_LAYER,
            "aggregation_identifier": inference.AGGREGATION_IDENTIFIER,
            "localization_identifier": inference.LOCALIZATION_IDENTIFIER,
        },
    )
    onnx.checker.check_model(model)
    return model.SerializeToString()


def verify_graph_constants(
    model_bytes: bytes,
    artifacts: inference.GovernedArtifacts,
) -> GraphVerification:
    model = onnx.load_from_string(model_bytes)
    initializers = {
        initializer.name: numpy_helper.to_array(initializer)
        for initializer in model.graph.initializer
    }
    feature_indices_ok = np.array_equal(
        initializers.get("feature_indices"),
        np.asarray(inference.EXPECTED_FEATURE_INDICES, dtype=np.int64),
    )
    mu_ok = np.array_equal(initializers.get("mu_by_class"), artifacts.mu)
    covariance_ok = np.array_equal(
        initializers.get("covariance_inverse_by_class"),
        artifacts.covariance_inverse,
    )
    input_names = tuple(input_value.name for input_value in model.graph.input)
    output_names = tuple(output_value.name for output_value in model.graph.output)
    output_contract_ok = output_names == (
        OUTPUT_PATCH_DISTANCES,
        OUTPUT_ANOMALY_MAP,
        OUTPUT_RAW_MEASURE,
        OUTPUT_ARGMAX_REGION,
    )
    if not all((feature_indices_ok, mu_ok, covariance_ok, output_contract_ok)):
        raise ExportError(
            "exported ONNX graph constants or output contract do not match governed metadata"
        )
    return GraphVerification(
        feature_indices_unchanged=feature_indices_ok,
        mu_unchanged=mu_ok,
        covariance_inverse_unchanged=covariance_ok,
        output_contract_matches_metadata=output_contract_ok,
        model_input_names=input_names,
        model_output_names=output_names,
    )


def session_options() -> ort.SessionOptions:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
    return options


def prediction_records_for_split(split: str) -> list[dict[str, Any]]:
    path = inference.PREDICTIONS_DIR / f"{split}_predictions.jsonl"
    records: list[dict[str, Any]] = []
    with path.open() as file:
        for line in file:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ExportError(f"C-5 prediction record is not an object: {path}")
                records.append(value)
    if not records:
        raise ExportError(f"C-5 prediction record is empty: {path}")
    return records


def localization_vector(record: Mapping[str, Any]) -> np.ndarray:
    localization = record.get("predicted_localization")
    if not isinstance(localization, Mapping):
        raise ExportError("C-5 prediction record lacks localization")
    region = localization.get("region")
    if not isinstance(region, Mapping):
        raise ExportError("C-5 prediction localization lacks region")
    return np.asarray(
        [
            float(region["x_min"]),
            float(region["y_min"]),
            float(region["x_max"]),
            float(region["y_max"]),
        ],
        dtype=np.float64,
    )


def verify_export_fidelity(
    model_bytes: bytes,
    inputs: ExportInputs,
) -> dict[str, Any]:
    file_hashes = inputs.governed.get("file_hashes")
    if not isinstance(file_hashes, Mapping):
        raise ExportError("invalid governed file hash map")
    samples = inference.load_inference_samples(file_hashes, inputs.artifacts.class_names)
    session = ort.InferenceSession(
        model_bytes,
        sess_options=session_options(),
        providers=["CPUExecutionProvider"],
    )
    if tuple(output.name for output in session.get_outputs()) != (
        OUTPUT_PATCH_DISTANCES,
        OUTPUT_ANOMALY_MAP,
        OUTPUT_RAW_MEASURE,
        OUTPUT_ARGMAX_REGION,
    ):
        raise ExportError("ONNX Runtime output contract does not match export metadata")

    max_map_abs = 0.0
    max_map_rel = 0.0
    max_raw_abs = 0.0
    max_raw_rel = 0.0
    max_bbox_abs = 0.0
    per_split: dict[str, Any] = {}

    for split in inference.INFERENCE_SPLITS:
        split_samples = [sample for sample in samples if sample.split == split]
        reference_maps_path = inference.ANOMALY_MAPS_DIR / f"{split}_anomaly_maps.npy"
        reference_predictions_path = inference.PREDICTIONS_DIR / f"{split}_predictions.jsonl"
        expected_map_hash = inputs.c5_reference.artifact_hashes["local_output_artifacts"][
            f"anomaly_maps/{split}_anomaly_maps.npy"
        ]
        expected_prediction_hash = inputs.c5_reference.artifact_hashes["local_output_artifacts"][
            f"predictions/{split}_predictions.jsonl"
        ]
        verify_file_hash(reference_maps_path, expected_map_hash, f"C-5 {split} anomaly maps")
        verify_file_hash(
            reference_predictions_path,
            expected_prediction_hash,
            f"C-5 {split} predictions",
        )
        reference_maps = np.load(reference_maps_path, allow_pickle=False)
        reference_predictions = prediction_records_for_split(split)
        if reference_maps.shape != (
            len(split_samples),
            inputs.config.image_size,
            inputs.config.image_size,
        ):
            raise ExportError(f"C-5 {split} anomaly map shape mismatch")
        if len(reference_predictions) != len(split_samples):
            raise ExportError(f"C-5 {split} prediction count mismatch")

        split_max_map_abs = 0.0
        split_max_raw_abs = 0.0
        split_max_bbox_abs = 0.0
        for sample_index, sample in enumerate(split_samples):
            prediction_record = reference_predictions[sample_index]
            if prediction_record.get("input_id") != sample.input_id:
                raise ExportError(f"C-5 {split} prediction order mismatch")
            class_index = inputs.artifacts.class_names.index(sample.class_name)
            full_features = training.extract_features(
                training.EXTRACTED_DIR / sample.filename,
                inputs.config,
            )
            outputs = session.run(
                [
                    OUTPUT_ANOMALY_MAP,
                    OUTPUT_RAW_MEASURE,
                    OUTPUT_ARGMAX_REGION,
                ],
                {
                    INPUT_FULL_PATCH_FEATURES: full_features.reshape(
                        1,
                        inputs.config.patch_count,
                        inputs.config.full_feature_dimension,
                    ).astype(np.float64),
                    INPUT_CLASS_INDEX: np.asarray([class_index], dtype=np.int64),
                },
            )
            onnx_map = np.asarray(outputs[0][0], dtype=np.float64)
            onnx_raw = float(np.asarray(outputs[1], dtype=np.float64).reshape(-1)[0])
            onnx_bbox = np.asarray(outputs[2], dtype=np.float64).reshape(4)
            reference_map = np.asarray(reference_maps[sample_index], dtype=np.float64)
            reference_raw = float(prediction_record["predicted_raw_anomaly_measure"])
            reference_bbox = localization_vector(prediction_record)

            map_abs = float(np.max(np.abs(onnx_map - reference_map)))
            map_rel = float(map_abs / max(float(np.max(np.abs(reference_map))), 1.0e-12))
            raw_abs = abs(onnx_raw - reference_raw)
            raw_rel = raw_abs / max(abs(reference_raw), 1.0e-12)
            bbox_abs = float(np.max(np.abs(onnx_bbox - reference_bbox)))

            max_map_abs = max(max_map_abs, map_abs)
            max_map_rel = max(max_map_rel, map_rel)
            max_raw_abs = max(max_raw_abs, raw_abs)
            max_raw_rel = max(max_raw_rel, raw_rel)
            max_bbox_abs = max(max_bbox_abs, bbox_abs)
            split_max_map_abs = max(split_max_map_abs, map_abs)
            split_max_raw_abs = max(split_max_raw_abs, raw_abs)
            split_max_bbox_abs = max(split_max_bbox_abs, bbox_abs)

        per_split[split] = {
            "sample_count": len(split_samples),
            "max_anomaly_map_abs_deviation": split_max_map_abs,
            "max_raw_measure_abs_deviation": split_max_raw_abs,
            "max_argmax_region_abs_deviation": split_max_bbox_abs,
        }

    tolerances_passed = (
        max_map_abs <= ABSOLUTE_TOLERANCE
        and max_map_rel <= RELATIVE_TOLERANCE
        and max_raw_abs <= ABSOLUTE_TOLERANCE
        and max_raw_rel <= RELATIVE_TOLERANCE
        and max_bbox_abs <= BBOX_ABSOLUTE_TOLERANCE
    )
    if not tolerances_passed:
        raise ExportError(
            "ONNX export fidelity exceeded declared tolerance: "
            f"map_abs={max_map_abs}, map_rel={max_map_rel}, "
            f"raw_abs={max_raw_abs}, raw_rel={max_raw_rel}, bbox_abs={max_bbox_abs}"
        )
    return {
        "status": "passed",
        "scope": "export fidelity verification only; not runtime integration and not evaluation",
        "reference": "governed C-5 inference outputs",
        "sample_count": len(samples),
        "per_split": per_split,
        "max_anomaly_map_abs_deviation": max_map_abs,
        "max_anomaly_map_relative_deviation": max_map_rel,
        "max_raw_measure_abs_deviation": max_raw_abs,
        "max_raw_measure_relative_deviation": max_raw_rel,
        "max_argmax_region_abs_deviation": max_bbox_abs,
        "tolerance": {
            "absolute": ABSOLUTE_TOLERANCE,
            "relative": RELATIVE_TOLERANCE,
            "bbox_absolute": BBOX_ABSOLUTE_TOLERANCE,
        },
        "onnx_execution": {
            "provider": "CPUExecutionProvider",
            "direct_onnxruntime_session_only": True,
            "runtime_provider_loaded": False,
        },
    }


def graph_verification_to_json(verification: GraphVerification) -> dict[str, Any]:
    return {
        "feature_indices_unchanged": verification.feature_indices_unchanged,
        "mu_unchanged": verification.mu_unchanged,
        "covariance_inverse_unchanged": verification.covariance_inverse_unchanged,
        "output_contract_matches_metadata": verification.output_contract_matches_metadata,
        "model_input_names": list(verification.model_input_names),
        "model_output_names": list(verification.model_output_names),
    }


def c4_identity(artifacts: inference.GovernedArtifacts) -> dict[str, Any]:
    return {
        "training_label": artifacts.training_record["training_label"],
        "training_record_sha256": artifacts.artifact_identity["training_record_sha256"],
        "training_artifact_hashes_sha256": artifacts.artifact_identity[
            "training_artifact_hashes_sha256"
        ],
        "training_metadata_sha256": artifacts.artifact_identity["training_metadata_sha256"],
        "training_replay_verification_sha256": artifacts.artifact_identity[
            "training_replay_verification_sha256"
        ],
        "mu_by_class_sha256": artifacts.artifact_identity["mu_by_class_sha256"],
        "covariance_inverse_by_class_sha256": artifacts.artifact_identity[
            "covariance_inverse_by_class_sha256"
        ],
        "feature_indices_sha256": artifacts.artifact_identity["feature_indices_sha256"],
        "feature_indices": list(inference.EXPECTED_FEATURE_INDICES),
        "class_order": list(artifacts.class_names),
        "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
        "backbone_identity": training.BACKBONE_IDENTITY,
        "selected_layer": training.BACKBONE_LAYER,
        "dtype_source": training.DTYPE_NAME,
        "epsilon": training.COVARIANCE_EPSILON,
    }


def c3_identity(inputs: ExportInputs) -> dict[str, Any]:
    dataset_identity = inputs.artifacts.dataset_identity
    return {
        "dataset": dataset_identity["dataset"],
        "role": dataset_identity["role"],
        "acquisition_label": dataset_identity["acquisition_label"],
        "archive_sha256": dataset_identity["archive_sha256"],
        "files_manifest_sha256": dataset_identity["files_manifest_sha256"],
        "split_hashes": dataset_identity["split_hashes"],
        "provenance_sha256": dataset_identity["provenance_sha256"],
        "repository_commit": dataset_identity["repository_commit"],
    }


def c5_identity(inputs: ExportInputs) -> dict[str, Any]:
    return {
        "inference_label": inputs.c5_reference.inference_metadata["inference_label"],
        "inference_artifact_hashes_sha256": inputs.c5_reference.artifact_hashes_sha256,
        "inference_metadata_sha256": inputs.c5_reference.inference_metadata_sha256,
        "inference_replay_sha256": inputs.c5_reference.replay_sha256,
        "aggregation_identifier": inference.AGGREGATION_IDENTIFIER,
        "localization_identifier": inference.LOCALIZATION_IDENTIFIER,
        "reference_output_artifacts": inputs.c5_reference.artifact_hashes[
            "local_output_artifacts"
        ],
    }


def build_export_records(
    inputs: ExportInputs,
    model_bytes: bytes,
    graph_verification: GraphVerification,
    fidelity: Mapping[str, Any],
    export_timestamp: str,
) -> ExportBuild:
    model_sha256 = sha256_bytes(model_bytes)
    graph_inputs = graph_input_contract()
    graph_outputs = graph_output_contract()
    graph_config = {
        "graph_name": GRAPH_NAME,
        "opset_version": ONNX_OPSET_VERSION,
        "ir_version": ONNX_IR_VERSION,
        "input_contract": graph_inputs,
        "output_contract": graph_outputs,
        "encoded_components": [
            "selected feature indices",
            "mu_by_class",
            "covariance_inverse_by_class",
            "per-patch Mahalanobis distance",
            "padim_anomaly_map_max_v1 raw-measure aggregation",
            "padim_raw_anomaly_map_argmax_region_v1 localization",
        ],
        "localization_represented_in_onnx": True,
        "preprocessing_reimplemented_in_onnx": False,
    }
    scope_boundaries = {
        "runtime_integration_performed": False,
        "runtime_provider_loaded": False,
        "provider_changed": False,
        "model_loader_changed": False,
        "onnx_session_changed": False,
        "onnx_runtime_changed": False,
        "output_mapping_changed": False,
        "preprocessing_changed": False,
        "inspection_domain_changed": False,
        "inspection_transform_prediction_changed": False,
        "inference_capability_added": False,
        "evaluation_executed": False,
        "metrics_generated": False,
        "calibration_performed": False,
        "benchmark_generated": False,
        "scientific_claim": False,
        "product_claim": False,
        "refit_performed": False,
    }
    artifact_record = {
        "schema": MODEL_SCHEMA,
        "export_label": EXPORT_LABEL,
        "model_reference_id": MODEL_REFERENCE_ID,
        "artifact_type": "governed ONNX export of fitted PaDiM baseline",
        "model_path": "artifacts/padim/model.onnx",
        "model_sha256": model_sha256,
        "content_hash_algorithm": "sha256",
        "provenance": {
            "c3_acquisition": c3_identity(inputs),
            "c4_fitted_baseline": c4_identity(inputs.artifacts),
            "c5_reference": c5_identity(inputs),
        },
        "graph": graph_config,
        "dtype_policy": dtype_policy(),
        "export_fidelity": {
            "status": fidelity["status"],
            "sample_count": fidelity["sample_count"],
            "max_anomaly_map_abs_deviation": fidelity["max_anomaly_map_abs_deviation"],
            "max_raw_measure_abs_deviation": fidelity["max_raw_measure_abs_deviation"],
            "max_argmax_region_abs_deviation": fidelity["max_argmax_region_abs_deviation"],
            "tolerance": fidelity["tolerance"],
        },
        "scope_boundaries": scope_boundaries,
    }
    metadata_record = {
        "schema": METADATA_SCHEMA,
        "export_label": EXPORT_LABEL,
        "export_timestamp_utc": export_timestamp,
        "toolchain": toolchain_versions(),
        "onnx": {
            "opset_version": ONNX_OPSET_VERSION,
            "ir_version": ONNX_IR_VERSION,
            "producer_name": "kalibra-governed-padim-onnx-export",
            "producer_version": "1.0.0",
        },
        "export_configuration": {
            "source": "governed C-4 fitted PaDiM artifacts only",
            "graph_generation": "deterministic onnx.helper graph construction",
            "constant_embedding": "mu, covariance_inverse, and feature_indices are ONNX initializers",
            "runtime_integration": "not performed",
            "provider_change": "not performed",
            "model_loader_change": "not performed",
            "output_mapping_change": "not performed",
            "preprocessing_change": "not performed",
        },
        "dtype_policy": dtype_policy(),
        "consumed_governed_inputs": {
            "mandatory_c4_inputs": {
                "statistics/mu_by_class.npy": inputs.artifacts.artifact_identity[
                    "mu_by_class_sha256"
                ],
                "covariance/covariance_inverse_by_class.npy": inputs.artifacts.artifact_identity[
                    "covariance_inverse_by_class_sha256"
                ],
                "statistics/feature_indices.npy": inputs.artifacts.artifact_identity[
                    "feature_indices_sha256"
                ],
                "training/artifact_hashes.json": inputs.artifacts.artifact_identity[
                    "training_artifact_hashes_sha256"
                ],
                "training/training_record.json": inputs.artifacts.artifact_identity[
                    "training_record_sha256"
                ],
                "metadata/training_metadata.json": inputs.artifacts.artifact_identity[
                    "training_metadata_sha256"
                ],
                "metadata/feature_indices.json": inputs.artifacts.training_artifact_hashes[
                    "metadata_artifacts"
                ]["metadata/feature_indices.json"],
                "metadata/numerical_config.json": inputs.artifacts.training_artifact_hashes[
                    "metadata_artifacts"
                ]["metadata/numerical_config.json"],
                "metadata/preprocessing_contract.json": inputs.artifacts.training_artifact_hashes[
                    "metadata_artifacts"
                ]["metadata/preprocessing_contract.json"],
                "metadata/backbone_metadata.json": inputs.artifacts.training_artifact_hashes[
                    "metadata_artifacts"
                ]["metadata/backbone_metadata.json"],
            },
            "c5_reference": c5_identity(inputs),
        },
        "graph": graph_config,
        "graph_verification": graph_verification_to_json(graph_verification),
        "export_fidelity_verification": dict(fidelity),
        "scope_boundaries": scope_boundaries,
    }
    return ExportBuild(
        model_bytes=model_bytes,
        artifact_record=artifact_record,
        metadata_record=metadata_record,
        artifact_bytes=canonical_json_bytes(artifact_record),
        metadata_bytes=canonical_json_bytes(metadata_record),
    )


def build_replay_record(
    first: ExportBuild,
    second: ExportBuild,
) -> dict[str, Any]:
    comparisons = {
        "model_onnx_bytes": first.model_bytes == second.model_bytes,
        "model_sha256": sha256_bytes(first.model_bytes) == sha256_bytes(second.model_bytes),
        "artifact_json": first.artifact_bytes == second.artifact_bytes,
        "metadata_json": first.metadata_bytes == second.metadata_bytes,
    }
    if not all(comparisons.values()):
        raise ExportError(f"deterministic ONNX export replay mismatch: {comparisons}")
    return {
        "schema": EXPORT_REPLAY_SCHEMA,
        "export_label": EXPORT_LABEL,
        "status": "passed",
        "complete_second_export": True,
        "comparisons": {
            **comparisons,
            "artifact_hashes_json": True,
            "export_replay_json": True,
        },
        "first_run_hashes": {
            "model.onnx": sha256_bytes(first.model_bytes),
            "artifact.json": sha256_bytes(first.artifact_bytes),
            "metadata.json": sha256_bytes(first.metadata_bytes),
        },
        "second_run_hashes": {
            "model.onnx": sha256_bytes(second.model_bytes),
            "artifact.json": sha256_bytes(second.artifact_bytes),
            "metadata.json": sha256_bytes(second.metadata_bytes),
        },
        "stable_fields": {
            "export_timestamp_utc": first.metadata_record["export_timestamp_utc"],
            "evidence_date": evidence_date_for_run(),
        },
        "scope": "deterministic export replay only; no runtime integration and no evaluation",
    }


def build_artifact_hashes_record(
    model_bytes: bytes,
    artifact_bytes: bytes,
    metadata_bytes: bytes,
    replay_bytes: bytes,
) -> dict[str, Any]:
    return {
        "schema": ARTIFACT_HASHES_SCHEMA,
        "export_label": EXPORT_LABEL,
        "hash_algorithm": "sha256",
        "hash_scope": (
            "artifacts/padim/model.onnx, artifact.json, metadata.json, and "
            "export_replay.json; artifact_hashes.json self-hash is recorded in evidence"
        ),
        "governed_export_artifacts": {
            "model.onnx": sha256_bytes(model_bytes),
            "artifact.json": sha256_bytes(artifact_bytes),
            "metadata.json": sha256_bytes(metadata_bytes),
            "export_replay.json": sha256_bytes(replay_bytes),
        },
    }


def write_evidence(
    inputs: ExportInputs,
    build: ExportBuild,
    replay_hash: str,
    artifact_hashes_hash: str,
) -> str:
    date = evidence_date_for_run()
    artifact = build.artifact_record
    metadata = build.metadata_record
    fidelity = metadata["export_fidelity_verification"]
    content = f"""# Kalibra Governed PaDiM ONNX Export Evidence v1.0

**Status:** Recorded - deterministic governed ONNX export evidence only
**Date:** {date}
**Scope:** Phase 3 / Task 1 - Governed ONNX Export only

## Export Scope

- Export label: `{EXPORT_LABEL}`
- Artifact: `artifacts/padim/model.onnx`
- Scope: deterministic export of the already-fitted C-4 PaDiM baseline only.
- No runtime integration was performed.
- No provider change was performed.
- No model loader change was performed.
- No output mapping change was performed.
- No preprocessing change was performed.

## Governed C-4 Input Identity

- Training label: `{inputs.artifacts.training_record["training_label"]}`
- Training record SHA-256: `{inputs.artifacts.artifact_identity["training_record_sha256"]}`
- Training artifact hashes SHA-256: `{inputs.artifacts.artifact_identity["training_artifact_hashes_sha256"]}`
- Training metadata SHA-256: `{inputs.artifacts.artifact_identity["training_metadata_sha256"]}`
- Training replay SHA-256: `{inputs.artifacts.artifact_identity["training_replay_verification_sha256"]}`
- Mu artifact SHA-256: `{inputs.artifacts.artifact_identity["mu_by_class_sha256"]}`
- Covariance inverse artifact SHA-256: `{inputs.artifacts.artifact_identity["covariance_inverse_by_class_sha256"]}`
- Feature indices artifact SHA-256: `{inputs.artifacts.artifact_identity["feature_indices_sha256"]}`
- Feature indices: `{list(inference.EXPECTED_FEATURE_INDICES)}`
- Source dtype: `{training.DTYPE_NAME}`
- Epsilon: `{training.COVARIANCE_EPSILON}`
- Preprocessing contract: `{training.PREPROCESSING_CONTRACT_ID}`
- Backbone: `{training.BACKBONE_IDENTITY}`
- Layer: `{training.BACKBONE_LAYER}`

## Governed C-5 Reference Identity

- Inference label: `{inputs.c5_reference.inference_metadata["inference_label"]}`
- Inference artifact hashes SHA-256: `{inputs.c5_reference.artifact_hashes_sha256}`
- Inference metadata SHA-256: `{inputs.c5_reference.inference_metadata_sha256}`
- Inference replay SHA-256: `{inputs.c5_reference.replay_sha256}`
- Aggregation identifier: `{inference.AGGREGATION_IDENTIFIER}`
- Localization identifier: `{inference.LOCALIZATION_IDENTIFIER}`
- Reference use: export fidelity verification only.

## ONNX Artifact Identity

- Model SHA-256: `{artifact["model_sha256"]}`
- Artifact record SHA-256: `{sha256_bytes(build.artifact_bytes)}`
- Metadata record SHA-256: `{sha256_bytes(build.metadata_bytes)}`
- Export replay SHA-256: `{replay_hash}`
- Artifact hashes record SHA-256: `{artifact_hashes_hash}`
- Opset: `{ONNX_OPSET_VERSION}`
- ONNX IR version: `{ONNX_IR_VERSION}`
- Toolchain: `{metadata["toolchain"]}`

## Dtype Policy

- Source dtype: `{training.DTYPE_NAME}`
- ONNX dtype: `{ONNX_DTYPE_NAME}`
- Precision policy: preserve C-4 float64 as ONNX DOUBLE.
- Float32 transition: `false`
- Expected numerical tolerance: `{dtype_policy()["expected_fidelity_tolerance"]}`

## Graph Contract

- Inputs: `{graph_input_contract()}`
- Outputs: `{graph_output_contract()}`
- Localization represented in ONNX: `true`
- Preprocessing reimplemented in ONNX: `false`

## Export Replay Result

- Complete second export executed: `true`
- Identical ONNX bytes: `true`
- Identical model hash: `true`
- Identical artifact metadata: `true`
- Identical artifact hashes: `true`
- Replay record: `artifacts/padim/export_replay.json`

## Export Fidelity Result

- Status: `{fidelity["status"]}`
- Reference: governed C-5 inference outputs.
- Sample count: `{fidelity["sample_count"]}`
- Max anomaly-map absolute deviation: `{fidelity["max_anomaly_map_abs_deviation"]}`
- Max anomaly-map relative deviation: `{fidelity["max_anomaly_map_relative_deviation"]}`
- Max raw-measure absolute deviation: `{fidelity["max_raw_measure_abs_deviation"]}`
- Max raw-measure relative deviation: `{fidelity["max_raw_measure_relative_deviation"]}`
- Max argmax-region absolute deviation: `{fidelity["max_argmax_region_abs_deviation"]}`
- Numerical tolerance: `{fidelity["tolerance"]}`
- Offline ONNX execution provider used for fidelity: `CPUExecutionProvider`
- Runtime provider loaded: `false`

## Known Limitations

- The graph input is the deterministic full patch feature tensor, not image pixels.
- The preprocessing contract is recorded and required but not reimplemented in ONNX.
- The artifact is not wired into `src/inspection/providers_onnx.py`.
- Export fidelity is not runtime equivalence.
- Export fidelity is not scientific evaluation.
- No calibrated confidence, threshold, operating point, abstention, review routing, or drift behavior is introduced.

## Explicit Non-Claims

- No runtime integration.
- No provider change.
- No model loader change.
- No output mapping change.
- No preprocessing change.
- No inference capability added.
- No evaluation executed.
- No metric generated.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, or F1 generated.
- No calibration performed.
- No benchmark generated.
- No scientific claim.
- No product claim.
"""
    return write_governed_bytes(EVIDENCE_PATH, content.encode("utf-8"))


def run_export() -> None:
    ensure_layout()
    inputs = load_export_inputs()
    export_timestamp = export_timestamp_for_run()
    first_model = build_onnx_model_bytes(inputs.artifacts)
    second_model = build_onnx_model_bytes(inputs.artifacts)
    if first_model != second_model:
        raise ExportError("deterministic ONNX graph generation did not reproduce identical bytes")
    graph_verification = verify_graph_constants(first_model, inputs.artifacts)
    fidelity = verify_export_fidelity(first_model, inputs)
    first_build = build_export_records(
        inputs,
        first_model,
        graph_verification,
        fidelity,
        export_timestamp,
    )
    second_build = build_export_records(
        inputs,
        second_model,
        graph_verification,
        fidelity,
        export_timestamp,
    )
    replay_record = build_replay_record(first_build, second_build)
    replay_bytes = canonical_json_bytes(replay_record)
    first_hashes = build_artifact_hashes_record(
        first_build.model_bytes,
        first_build.artifact_bytes,
        first_build.metadata_bytes,
        replay_bytes,
    )
    second_hashes = build_artifact_hashes_record(
        second_build.model_bytes,
        second_build.artifact_bytes,
        second_build.metadata_bytes,
        replay_bytes,
    )
    if canonical_json_bytes(first_hashes) != canonical_json_bytes(second_hashes):
        raise ExportError("deterministic export replay produced different artifact hashes")

    model_hash = write_governed_bytes(MODEL_PATH, first_build.model_bytes)
    artifact_hash = write_governed_bytes(ARTIFACT_RECORD_PATH, first_build.artifact_bytes)
    metadata_hash = write_governed_bytes(METADATA_PATH, first_build.metadata_bytes)
    replay_hash = write_governed_bytes(EXPORT_REPLAY_PATH, replay_bytes)
    artifact_hashes_hash = write_json_record(ARTIFACT_HASHES_PATH, first_hashes)
    if first_hashes["governed_export_artifacts"] != {
        "model.onnx": model_hash,
        "artifact.json": artifact_hash,
        "metadata.json": metadata_hash,
        "export_replay.json": replay_hash,
    }:
        raise ExportError("written export artifact hashes do not match generated hashes")
    write_evidence(inputs, first_build, replay_hash, artifact_hashes_hash)


def verify_existing_export_records(
    inputs: ExportInputs,
    fidelity: Mapping[str, Any],
) -> None:
    model_bytes = MODEL_PATH.read_bytes()
    model_sha256 = sha256_bytes(model_bytes)
    graph_verification = verify_graph_constants(model_bytes, inputs.artifacts)
    artifact_record = read_json_mapping(ARTIFACT_RECORD_PATH)
    metadata_record = read_json_mapping(METADATA_PATH)
    replay_record = read_json_mapping(EXPORT_REPLAY_PATH)
    artifact_hashes = read_json_mapping(ARTIFACT_HASHES_PATH)
    if artifact_record.get("schema") != MODEL_SCHEMA:
        raise ExportError("unexpected export artifact schema")
    if metadata_record.get("schema") != METADATA_SCHEMA:
        raise ExportError("unexpected export metadata schema")
    if replay_record.get("schema") != EXPORT_REPLAY_SCHEMA or replay_record.get("status") != "passed":
        raise ExportError("export replay record is not passed")
    if artifact_hashes.get("schema") != ARTIFACT_HASHES_SCHEMA:
        raise ExportError("unexpected export artifact hashes schema")
    if artifact_record.get("model_sha256") != model_sha256:
        raise ExportError("artifact record model hash does not match model.onnx")
    if metadata_record.get("graph_verification") != graph_verification_to_json(graph_verification):
        raise ExportError("metadata graph verification no longer matches ONNX graph")
    if metadata_record.get("export_fidelity_verification") != dict(fidelity):
        raise ExportError("metadata fidelity verification no longer matches ONNX outputs")

    expected_hashes = artifact_hashes.get("governed_export_artifacts")
    actual_hashes = {
        "model.onnx": model_sha256,
        "artifact.json": acquisition.sha256_file(ARTIFACT_RECORD_PATH),
        "metadata.json": acquisition.sha256_file(METADATA_PATH),
        "export_replay.json": acquisition.sha256_file(EXPORT_REPLAY_PATH),
    }
    if expected_hashes != actual_hashes:
        raise ExportError("export artifact_hashes.json does not match current artifacts")
    if not EVIDENCE_PATH.exists():
        raise ExportError("missing governed ONNX export evidence")


def verify_export() -> None:
    inputs = load_export_inputs()
    if not MODEL_PATH.exists():
        raise ExportError(f"missing ONNX model artifact: {MODEL_PATH}")
    fidelity = verify_export_fidelity(MODEL_PATH.read_bytes(), inputs)
    verify_existing_export_records(inputs, fidelity)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3 governed PaDiM ONNX export")
    parser.add_argument("command", choices=("export", "verify"))
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            run_export()
        elif args.command == "verify":
            verify_export()
    except (ExportError, inference.InferenceError, training.TrainingError, acquisition.AcquisitionError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
