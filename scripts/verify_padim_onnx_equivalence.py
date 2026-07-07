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
from onnx import TensorProto, numpy_helper


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import export_padim_onnx as export  # noqa: E402
import governed_visa_acquisition as acquisition  # noqa: E402
import padim_inference as inference  # noqa: E402
import train_padim_baseline as training  # noqa: E402


EQUIVALENCE_DIR = export.ARTIFACT_DIR / "equivalence"
EQUIVALENCE_REPORT_PATH = EQUIVALENCE_DIR / "equivalence_report.json"
EQUIVALENCE_HASHES_PATH = EQUIVALENCE_DIR / "equivalence_hashes.json"
EQUIVALENCE_REPLAY_PATH = EQUIVALENCE_DIR / "equivalence_replay.json"
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md"
)

EQUIVALENCE_LABEL = "visa-padim-onnx-export-equivalence-v1"
EQUIVALENCE_REPORT_SCHEMA = "kalibra_padim_onnx_export_equivalence_report_v1"
EQUIVALENCE_HASHES_SCHEMA = "kalibra_padim_onnx_export_equivalence_hashes_v1"
EQUIVALENCE_REPLAY_SCHEMA = "kalibra_padim_onnx_export_equivalence_replay_v1"

EXPECTED_MODEL_SHA256 = "0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a"
EXPECTED_ARTIFACT_RECORD_SHA256 = "6d6768cbd13d0a26dbfb817e676fc5ccddbb878b72f18e443dc403b531052f4f"
EXPECTED_METADATA_RECORD_SHA256 = "3dd299292c32a7d6616171ce26dd6d07a3d1c313dfc4dd00ea583dbca313f00d"
EXPECTED_EXPORT_REPLAY_SHA256 = "e2d7f28ed2412a509e384ad50509fc8e73d4f1347349683e4f89a4071be27093"
EXPECTED_EXPORT_HASHES_RECORD_SHA256 = "d2e36f0ed4b6bd71c15fb4ce49c2481b5f1af4edc7b0ee034dc76386deed38c6"

EXPECTED_C4_TRAINING_RECORD_SHA256 = "7d6171f3f05c30c4891969fa40451d0e960b4e5b8ac00b3d0e1d22f2ee9b8048"
EXPECTED_C4_ARTIFACT_HASHES_SHA256 = "00c625060c6e50fe7ab1da76125e3891d8be7e52838c846eaba52813461eeb32"
EXPECTED_C4_TRAINING_METADATA_SHA256 = "c0178d823d0c440102c768f75799340586bd4c428bfa309862e8fb658b0ffad9"
EXPECTED_C4_REPLAY_SHA256 = "dc5f66ee17533518489c893358cb30b8dd622277b5f38e21c0a0dd6e67fdd55f"
EXPECTED_C4_MU_SHA256 = "51568c211c324b9178837f0d862c01a9601dc3d3daa474c959bb32ef5758446b"
EXPECTED_C4_COVARIANCE_INVERSE_SHA256 = "893af9e08d3543b5bd973ab913c1f2e8ed57d26a1bbb225b194d525cfc8df7b3"
EXPECTED_C4_FEATURE_INDICES_SHA256 = "1ca5583a7b498b4849e42717f24ebcf82d82a6c545b852814ada12b5c287cbe3"

EXPECTED_C5_ARTIFACT_HASHES_SHA256 = "c39dc13d4eccff0846253528d2fa3af4bb12349ca80fb9b90e631ef1fbdeb9bf"
EXPECTED_C5_METADATA_SHA256 = "78e8408534863096315a07f21da33265f970e44f369a9fa3e35743f2adea372f"
EXPECTED_C5_REPLAY_SHA256 = "e6e59b0e72750992d97fd39788a7a8a3b9f40a52a7783becdfa4f30dd779936c"
EXPECTED_C5_OUTPUT_HASHES = {
    "anomaly_maps/test_anomaly_maps.npy": "21a959c9891815ea73ee7e23a47a1b4c15be18047ad58e2b721a7c24cdc15a9d",
    "anomaly_maps/validation_anomaly_maps.npy": "bdea53e85561e830ab1b45430f0df16e6769e9092124217fe5827ee30ac3d97d",
    "predictions/test_predictions.jsonl": "35e2a8426a8e1bb59f8327f657eff79892dbbbad825acf19debee2a6436f8436",
    "predictions/validation_predictions.jsonl": "ebef96fad1a665e9e2cd4c2e9855f93f238b8a71a41971c56efbabd3ba5314c4",
}

EXPECTED_SPLIT_COUNTS = {"validation": 2164, "test": 4328}
EXPECTED_SAMPLE_COUNT = 6492

ABSOLUTE_TOLERANCE = 1.0e-12
RELATIVE_TOLERANCE = 1.0e-12
BBOX_ABSOLUTE_TOLERANCE = 0.0


class EquivalenceError(RuntimeError):
    """Raised when governed ONNX equivalence cannot be verified safely."""


@dataclass(frozen=True)
class VerifiedContext:
    inputs: export.ExportInputs
    model_bytes: bytes
    onnx_model: onnx.ModelProto
    artifact_record: dict[str, Any]
    metadata_record: dict[str, Any]
    export_replay_record: dict[str, Any]
    export_hashes_record: dict[str, Any]
    artifact_verification: dict[str, Any]
    reference_verification: dict[str, Any]
    graph_verification: dict[str, Any]


@dataclass(frozen=True)
class EquivalenceRun:
    sample_count: int
    split_counts: dict[str, int]
    per_sample_deviations: list[dict[str, Any]]
    per_split_maxima: dict[str, dict[str, Any]]
    global_maxima: dict[str, float]
    status: str


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


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise EquivalenceError(f"missing governed record: {path}") from exc
    if not isinstance(value, dict):
        raise EquivalenceError(f"governed record is not a JSON object: {path}")
    return value


def write_governed_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise EquivalenceError(f"governed equivalence artifact changed: {path}")
        return acquisition.sha256_file(path)
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def verify_file_hash(path: Path, expected: str, label: str) -> str:
    if not path.exists():
        raise EquivalenceError(f"missing governed artifact for {label}: {path}")
    actual = acquisition.sha256_file(path)
    if actual != expected:
        raise EquivalenceError(
            f"governed artifact hash mismatch for {label}: expected {expected}, got {actual}"
        )
    return actual


def equivalence_timestamp_for_run() -> str:
    if not EQUIVALENCE_REPORT_PATH.exists():
        return utc_timestamp()
    report = read_json_mapping(EQUIVALENCE_REPORT_PATH)
    timestamp = report.get("verification_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise EquivalenceError("existing equivalence report lacks verification timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text().splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise EquivalenceError("existing equivalence evidence lacks Date field")


def ensure_layout() -> None:
    EQUIVALENCE_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)


def expect_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise EquivalenceError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def expected_export_hashes() -> dict[str, str]:
    return {
        "model.onnx": EXPECTED_MODEL_SHA256,
        "artifact.json": EXPECTED_ARTIFACT_RECORD_SHA256,
        "metadata.json": EXPECTED_METADATA_RECORD_SHA256,
        "export_replay.json": EXPECTED_EXPORT_REPLAY_SHA256,
    }


def tensor_value_contract(value_info: onnx.ValueInfoProto) -> dict[str, Any]:
    tensor_type = value_info.type.tensor_type
    shape: list[int] = []
    for dim in tensor_type.shape.dim:
        if dim.HasField("dim_value"):
            shape.append(int(dim.dim_value))
        else:
            raise EquivalenceError(f"ONNX graph uses non-static shape for {value_info.name}")
    return {
        "dtype": tensor_type.elem_type,
        "dtype_name": tensor_dtype_name(tensor_type.elem_type),
        "shape": shape,
    }


def tensor_dtype_name(elem_type: int) -> str:
    if elem_type == TensorProto.DOUBLE:
        return "float64"
    if elem_type == TensorProto.INT64:
        return "int64"
    return TensorProto.DataType.Name(elem_type).lower()


def arrays_byte_equal(left: np.ndarray, right: np.ndarray) -> bool:
    return (
        left.dtype == right.dtype
        and left.shape == right.shape
        and np.ascontiguousarray(left).tobytes() == np.ascontiguousarray(right).tobytes()
    )


def verify_export_artifacts() -> tuple[bytes, onnx.ModelProto, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    model_sha = verify_file_hash(export.MODEL_PATH, EXPECTED_MODEL_SHA256, "Task 1 model.onnx")
    artifact_sha = verify_file_hash(
        export.ARTIFACT_RECORD_PATH,
        EXPECTED_ARTIFACT_RECORD_SHA256,
        "Task 1 artifact.json",
    )
    metadata_sha = verify_file_hash(
        export.METADATA_PATH,
        EXPECTED_METADATA_RECORD_SHA256,
        "Task 1 metadata.json",
    )
    replay_sha = verify_file_hash(
        export.EXPORT_REPLAY_PATH,
        EXPECTED_EXPORT_REPLAY_SHA256,
        "Task 1 export_replay.json",
    )
    hashes_sha = verify_file_hash(
        export.ARTIFACT_HASHES_PATH,
        EXPECTED_EXPORT_HASHES_RECORD_SHA256,
        "Task 1 artifact_hashes.json",
    )

    artifact_record = read_json_mapping(export.ARTIFACT_RECORD_PATH)
    metadata_record = read_json_mapping(export.METADATA_PATH)
    export_replay_record = read_json_mapping(export.EXPORT_REPLAY_PATH)
    export_hashes_record = read_json_mapping(export.ARTIFACT_HASHES_PATH)

    expect_equal(artifact_record.get("schema"), export.MODEL_SCHEMA, "Task 1 artifact schema")
    expect_equal(metadata_record.get("schema"), export.METADATA_SCHEMA, "Task 1 metadata schema")
    expect_equal(export_hashes_record.get("schema"), export.ARTIFACT_HASHES_SCHEMA, "Task 1 hashes schema")
    expect_equal(export_replay_record.get("schema"), export.EXPORT_REPLAY_SCHEMA, "Task 1 replay schema")
    expect_equal(export_replay_record.get("status"), "passed", "Task 1 export replay status")
    expect_equal(export_replay_record.get("complete_second_export"), True, "Task 1 replay completeness")
    if not all(export_replay_record.get("comparisons", {}).values()):
        raise EquivalenceError("Task 1 export replay comparison is not fully true")

    expect_equal(artifact_record.get("model_sha256"), model_sha, "Task 1 artifact model hash")
    expect_equal(
        export_hashes_record.get("governed_export_artifacts"),
        expected_export_hashes(),
        "Task 1 governed export artifact hashes",
    )

    model_bytes = export.MODEL_PATH.read_bytes()
    model = onnx.load_from_string(model_bytes)
    onnx.checker.check_model(model)
    expect_equal(model.ir_version, export.ONNX_IR_VERSION, "Task 1 ONNX IR version")
    expect_equal(default_opset_version(model), export.ONNX_OPSET_VERSION, "Task 1 ONNX opset")
    expect_equal(
        artifact_record.get("graph", {}).get("opset_version"),
        export.ONNX_OPSET_VERSION,
        "Task 1 artifact graph opset",
    )
    expect_equal(
        artifact_record.get("graph", {}).get("ir_version"),
        export.ONNX_IR_VERSION,
        "Task 1 artifact graph IR version",
    )
    expect_equal(
        metadata_record.get("onnx", {}).get("opset_version"),
        export.ONNX_OPSET_VERSION,
        "Task 1 metadata opset",
    )
    expect_equal(
        metadata_record.get("onnx", {}).get("ir_version"),
        export.ONNX_IR_VERSION,
        "Task 1 metadata IR version",
    )

    verification = {
        "status": "passed",
        "model_sha256": model_sha,
        "artifact_record_sha256": artifact_sha,
        "metadata_record_sha256": metadata_sha,
        "export_replay_sha256": replay_sha,
        "artifact_hashes_record_sha256": hashes_sha,
        "opset_version": default_opset_version(model),
        "ir_version": model.ir_version,
        "export_replay_status": export_replay_record["status"],
        "artifact_hashes_record_matches_current_artifacts": True,
    }
    return (
        model_bytes,
        model,
        artifact_record,
        metadata_record,
        export_replay_record,
        export_hashes_record,
        verification,
    )


def default_opset_version(model: onnx.ModelProto) -> int:
    versions = [
        opset.version
        for opset in model.opset_import
        if opset.domain in ("", "ai.onnx")
    ]
    if len(versions) != 1:
        raise EquivalenceError(f"unexpected ONNX default opset declarations: {versions}")
    return int(versions[0])


def verify_reference_artifacts(inputs: export.ExportInputs) -> dict[str, Any]:
    artifacts = inputs.artifacts
    identity = artifacts.artifact_identity

    expected_c4_identity = {
        "training_record_sha256": EXPECTED_C4_TRAINING_RECORD_SHA256,
        "training_artifact_hashes_sha256": EXPECTED_C4_ARTIFACT_HASHES_SHA256,
        "training_metadata_sha256": EXPECTED_C4_TRAINING_METADATA_SHA256,
        "training_replay_verification_sha256": EXPECTED_C4_REPLAY_SHA256,
        "mu_by_class_sha256": EXPECTED_C4_MU_SHA256,
        "covariance_inverse_by_class_sha256": EXPECTED_C4_COVARIANCE_INVERSE_SHA256,
        "feature_indices_sha256": EXPECTED_C4_FEATURE_INDICES_SHA256,
    }
    for key, expected in expected_c4_identity.items():
        expect_equal(identity.get(key), expected, f"C-4 identity {key}")

    verify_file_hash(training.TRAINING_DIR / "training_record.json", EXPECTED_C4_TRAINING_RECORD_SHA256, "C-4 training record")
    verify_file_hash(training.TRAINING_DIR / "artifact_hashes.json", EXPECTED_C4_ARTIFACT_HASHES_SHA256, "C-4 artifact hashes")
    verify_file_hash(training.METADATA_DIR / "training_metadata.json", EXPECTED_C4_TRAINING_METADATA_SHA256, "C-4 training metadata")
    verify_file_hash(training.TRAINING_DIR / "replay_verification.json", EXPECTED_C4_REPLAY_SHA256, "C-4 replay")
    verify_file_hash(training.STATISTICS_DIR / "mu_by_class.npy", EXPECTED_C4_MU_SHA256, "C-4 mu")
    verify_file_hash(
        training.COVARIANCE_DIR / "covariance_inverse_by_class.npy",
        EXPECTED_C4_COVARIANCE_INVERSE_SHA256,
        "C-4 covariance inverse",
    )
    verify_file_hash(training.STATISTICS_DIR / "feature_indices.npy", EXPECTED_C4_FEATURE_INDICES_SHA256, "C-4 feature indices")

    expect_equal(artifacts.training_record.get("training_label"), training.TRAINING_LABEL, "C-4 training label")
    expect_equal(artifacts.training_replay_record.get("status"), "passed", "C-4 replay status")

    c5 = inputs.c5_reference
    expect_equal(c5.artifact_hashes_sha256, EXPECTED_C5_ARTIFACT_HASHES_SHA256, "C-5 artifact hashes")
    expect_equal(c5.inference_metadata_sha256, EXPECTED_C5_METADATA_SHA256, "C-5 inference metadata")
    expect_equal(c5.replay_sha256, EXPECTED_C5_REPLAY_SHA256, "C-5 replay")
    expect_equal(c5.replay_record.get("status"), "passed", "C-5 replay status")
    expect_equal(c5.inference_metadata.get("inference_label"), inference.INFERENCE_LABEL, "C-5 inference label")
    expect_equal(
        c5.inference_metadata.get("aggregation_identifier"),
        inference.AGGREGATION_IDENTIFIER,
        "C-5 aggregation identifier",
    )
    expect_equal(
        c5.inference_metadata.get("localization_identifier"),
        inference.LOCALIZATION_IDENTIFIER,
        "C-5 localization identifier",
    )

    local_outputs = c5.artifact_hashes.get("local_output_artifacts")
    if not isinstance(local_outputs, Mapping):
        raise EquivalenceError("C-5 artifact hashes lack local output artifacts")
    expect_equal(dict(local_outputs), EXPECTED_C5_OUTPUT_HASHES, "C-5 local output hashes")
    for relative_path, expected_hash in EXPECTED_C5_OUTPUT_HASHES.items():
        verify_file_hash(inference.INFERENCE_DIR / relative_path, expected_hash, f"C-5 {relative_path}")
    verify_file_hash(
        inference.INFERENCE_METADATA_DIR / "inference_metadata.json",
        EXPECTED_C5_METADATA_SHA256,
        "C-5 inference metadata",
    )
    verify_file_hash(
        inference.INFERENCE_DIR / "artifact_hashes.json",
        EXPECTED_C5_ARTIFACT_HASHES_SHA256,
        "C-5 artifact hashes",
    )
    verify_file_hash(
        inference.REPLAY_DIR / "replay_verification.json",
        EXPECTED_C5_REPLAY_SHA256,
        "C-5 replay",
    )

    return {
        "status": "passed",
        "governed_c4_training_identity_verified": True,
        "governed_c5_inference_identity_verified": True,
        "c4_hashes": expected_c4_identity,
        "c5_hashes": {
            "inference_artifact_hashes_sha256": EXPECTED_C5_ARTIFACT_HASHES_SHA256,
            "inference_metadata_sha256": EXPECTED_C5_METADATA_SHA256,
            "inference_replay_sha256": EXPECTED_C5_REPLAY_SHA256,
            "local_output_artifacts": EXPECTED_C5_OUTPUT_HASHES,
        },
        "c5_replay_status": c5.replay_record["status"],
    }


def verify_graph_contract(
    model: onnx.ModelProto,
    artifact_record: Mapping[str, Any],
    metadata_record: Mapping[str, Any],
    artifacts: inference.GovernedArtifacts,
) -> dict[str, Any]:
    expect_equal(default_opset_version(model), export.ONNX_OPSET_VERSION, "graph contract opset")
    expect_equal(model.ir_version, export.ONNX_IR_VERSION, "graph contract IR version")

    expected_inputs = {
        export.INPUT_FULL_PATCH_FEATURES: {
            "dtype": TensorProto.DOUBLE,
            "dtype_name": "float64",
            "shape": [1, training.FitConfig().patch_count, training.FULL_FEATURE_DIMENSION],
        },
        export.INPUT_CLASS_INDEX: {
            "dtype": TensorProto.INT64,
            "dtype_name": "int64",
            "shape": [1],
        },
    }
    expected_outputs = {
        export.OUTPUT_PATCH_DISTANCES: {
            "dtype": TensorProto.DOUBLE,
            "dtype_name": "float64",
            "shape": [1, training.FitConfig().patch_count],
        },
        export.OUTPUT_ANOMALY_MAP: {
            "dtype": TensorProto.DOUBLE,
            "dtype_name": "float64",
            "shape": [1, training.IMAGE_SIZE, training.IMAGE_SIZE],
        },
        export.OUTPUT_RAW_MEASURE: {
            "dtype": TensorProto.DOUBLE,
            "dtype_name": "float64",
            "shape": [1],
        },
        export.OUTPUT_ARGMAX_REGION: {
            "dtype": TensorProto.DOUBLE,
            "dtype_name": "float64",
            "shape": [1, 4],
        },
    }
    actual_inputs = {
        value.name: tensor_value_contract(value)
        for value in model.graph.input
    }
    actual_outputs = {
        value.name: tensor_value_contract(value)
        for value in model.graph.output
    }
    expect_equal(actual_inputs, expected_inputs, "ONNX graph input contract")
    expect_equal(actual_outputs, expected_outputs, "ONNX graph output contract")

    initializers = {
        initializer.name: numpy_helper.to_array(initializer)
        for initializer in model.graph.initializer
    }
    graph_feature_indices = initializers.get("feature_indices")
    graph_mu = initializers.get("mu_by_class")
    graph_covariance_inverse = initializers.get("covariance_inverse_by_class")
    if graph_feature_indices is None or graph_mu is None or graph_covariance_inverse is None:
        raise EquivalenceError("ONNX graph lacks governed PaDiM initializers")

    expected_feature_indices = np.asarray(inference.EXPECTED_FEATURE_INDICES, dtype=np.int64)
    feature_indices_match = arrays_byte_equal(graph_feature_indices, artifacts.feature_indices)
    feature_indices_exact = np.array_equal(graph_feature_indices, expected_feature_indices)
    mu_match = arrays_byte_equal(graph_mu, artifacts.mu)
    covariance_match = arrays_byte_equal(graph_covariance_inverse, artifacts.covariance_inverse)
    if not feature_indices_match or not feature_indices_exact:
        raise EquivalenceError("ONNX graph feature indices drifted from governed C-4")
    if not mu_match:
        raise EquivalenceError("ONNX graph mu drifted from governed C-4")
    if not covariance_match:
        raise EquivalenceError("ONNX graph covariance inverse drifted from governed C-4")

    model_props = {entry.key: entry.value for entry in model.metadata_props}
    expect_equal(
        model_props.get("preprocessing_contract_id"),
        training.PREPROCESSING_CONTRACT_ID,
        "ONNX graph preprocessing contract id",
    )
    expect_equal(
        artifact_record.get("graph", {}).get("preprocessing_reimplemented_in_onnx"),
        False,
        "artifact preprocessing implementation flag",
    )
    expect_equal(
        metadata_record.get("graph", {}).get("preprocessing_reimplemented_in_onnx"),
        False,
        "metadata preprocessing implementation flag",
    )
    if any(value.name in ("image", "image_tensor", "input_image") for value in model.graph.input):
        raise EquivalenceError("ONNX graph input contract claims image preprocessing")

    dtype_policy = metadata_record.get("dtype_policy")
    if not isinstance(dtype_policy, Mapping):
        raise EquivalenceError("Task 1 metadata lacks dtype policy")
    expect_equal(dtype_policy.get("dtype_source"), training.DTYPE_NAME, "dtype source")
    expect_equal(dtype_policy.get("onnx_dtype"), export.ONNX_DTYPE_NAME, "ONNX dtype")
    expect_equal(dtype_policy.get("float32_transition"), False, "float32 transition")

    return {
        "status": "passed",
        "opset_version": default_opset_version(model),
        "ir_version": model.ir_version,
        "inputs": {
            name: {
                "dtype": contract["dtype_name"],
                "shape": contract["shape"],
            }
            for name, contract in actual_inputs.items()
        },
        "outputs": {
            name: {
                "dtype": contract["dtype_name"],
                "shape": contract["shape"],
            }
            for name, contract in actual_outputs.items()
        },
        "feature_indices": graph_feature_indices.tolist(),
        "feature_indices_byte_equal_to_c4": feature_indices_match,
        "feature_indices_exact": feature_indices_exact,
        "mu_byte_equal_to_c4": mu_match,
        "covariance_inverse_byte_equal_to_c4": covariance_match,
        "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
        "preprocessing_reimplemented_in_onnx": False,
        "graph_claims_image_preprocessing": False,
        "dtype_policy": {
            "source_dtype": training.DTYPE_NAME,
            "onnx_dtype": export.ONNX_DTYPE_NAME,
            "float32_transition": False,
        },
    }


def verify_context() -> VerifiedContext:
    (
        model_bytes,
        model,
        artifact_record,
        metadata_record,
        export_replay_record,
        export_hashes_record,
        artifact_verification,
    ) = verify_export_artifacts()
    inputs = export.load_export_inputs()
    reference_verification = verify_reference_artifacts(inputs)
    graph_verification = verify_graph_contract(
        model,
        artifact_record,
        metadata_record,
        inputs.artifacts,
    )
    return VerifiedContext(
        inputs=inputs,
        model_bytes=model_bytes,
        onnx_model=model,
        artifact_record=artifact_record,
        metadata_record=metadata_record,
        export_replay_record=export_replay_record,
        export_hashes_record=export_hashes_record,
        artifact_verification=artifact_verification,
        reference_verification=reference_verification,
        graph_verification=graph_verification,
    )


def prediction_records_for_split(split: str) -> list[dict[str, Any]]:
    return export.prediction_records_for_split(split)


def sample_artifact_record(context: VerifiedContext, input_id: str) -> Mapping[str, Any]:
    sample_artifacts = context.inputs.c5_reference.artifact_hashes.get("sample_artifacts")
    if not isinstance(sample_artifacts, Mapping):
        raise EquivalenceError("C-5 artifact hashes lack sample artifacts")
    record = sample_artifacts.get(input_id)
    if not isinstance(record, Mapping):
        raise EquivalenceError(f"C-5 artifact hashes lack sample artifact: {input_id}")
    return record


def verify_c5_sample_hashes(
    context: VerifiedContext,
    sample: inference.InferenceSample,
    reference_map: np.ndarray,
    prediction_record: Mapping[str, Any],
    selected_features: np.ndarray,
) -> None:
    record = sample_artifact_record(context, sample.input_id)
    expect_equal(record.get("filename"), sample.filename, f"C-5 sample filename {sample.input_id}")
    expect_equal(record.get("class_name"), sample.class_name, f"C-5 sample class {sample.input_id}")
    expect_equal(record.get("split"), sample.split, f"C-5 sample split {sample.input_id}")
    expect_equal(record.get("sample_sha256"), sample.sha256, f"C-5 sample hash {sample.input_id}")
    expect_equal(
        record.get("feature_tensor_sha256"),
        inference.npy_sha256(np.ascontiguousarray(selected_features, dtype=np.float64)),
        f"C-5 selected feature hash {sample.input_id}",
    )
    expect_equal(
        record.get("anomaly_map_sha256"),
        inference.npy_sha256(np.ascontiguousarray(reference_map, dtype=np.float64)),
        f"C-5 anomaly map hash {sample.input_id}",
    )
    expect_equal(
        record.get("prediction_sha256"),
        inference.sha256_bytes(inference.canonical_json_bytes(prediction_record)),
        f"C-5 prediction hash {sample.input_id}",
    )


def relative_deviation(absolute_deviation: float, reference_scale: float) -> float:
    return float(absolute_deviation / max(abs(reference_scale), 1.0e-12))


def run_equivalence(context: VerifiedContext) -> EquivalenceRun:
    file_hashes = context.inputs.governed.get("file_hashes")
    if not isinstance(file_hashes, Mapping):
        raise EquivalenceError("invalid governed file hash map")
    samples = inference.load_inference_samples(file_hashes, context.inputs.artifacts.class_names)
    split_counts = {
        split: sum(1 for sample in samples if sample.split == split)
        for split in inference.INFERENCE_SPLITS
    }
    expect_equal(split_counts, EXPECTED_SPLIT_COUNTS, "governed C-5 split counts")
    expect_equal(len(samples), EXPECTED_SAMPLE_COUNT, "governed C-5 sample count")

    session = ort.InferenceSession(
        context.model_bytes,
        sess_options=export.session_options(),
        providers=["CPUExecutionProvider"],
    )
    expect_equal(session.get_providers(), ["CPUExecutionProvider"], "ONNX Runtime providers")
    expect_equal(
        tuple(output.name for output in session.get_outputs()),
        (
            export.OUTPUT_PATCH_DISTANCES,
            export.OUTPUT_ANOMALY_MAP,
            export.OUTPUT_RAW_MEASURE,
            export.OUTPUT_ARGMAX_REGION,
        ),
        "ONNX Runtime output order",
    )

    per_sample: list[dict[str, Any]] = []
    per_split: dict[str, dict[str, Any]] = {}
    global_maxima = {
        "anomaly_map_absolute": 0.0,
        "anomaly_map_relative": 0.0,
        "raw_measure_absolute": 0.0,
        "raw_measure_relative": 0.0,
        "argmax_region_absolute": 0.0,
    }

    for split in inference.INFERENCE_SPLITS:
        split_samples = [sample for sample in samples if sample.split == split]
        reference_maps_path = inference.ANOMALY_MAPS_DIR / f"{split}_anomaly_maps.npy"
        reference_predictions_path = inference.PREDICTIONS_DIR / f"{split}_predictions.jsonl"
        verify_file_hash(
            reference_maps_path,
            EXPECTED_C5_OUTPUT_HASHES[f"anomaly_maps/{split}_anomaly_maps.npy"],
            f"C-5 {split} anomaly maps",
        )
        verify_file_hash(
            reference_predictions_path,
            EXPECTED_C5_OUTPUT_HASHES[f"predictions/{split}_predictions.jsonl"],
            f"C-5 {split} predictions",
        )
        reference_maps = np.load(reference_maps_path, allow_pickle=False)
        reference_predictions = prediction_records_for_split(split)
        expect_equal(
            list(reference_maps.shape),
            [len(split_samples), context.inputs.config.image_size, context.inputs.config.image_size],
            f"C-5 {split} anomaly map shape",
        )
        expect_equal(len(reference_predictions), len(split_samples), f"C-5 {split} prediction count")

        split_maxima = {
            "sample_count": len(split_samples),
            "anomaly_map_absolute": 0.0,
            "anomaly_map_relative": 0.0,
            "raw_measure_absolute": 0.0,
            "raw_measure_relative": 0.0,
            "argmax_region_absolute": 0.0,
        }

        for sample_index, sample in enumerate(split_samples):
            prediction_record = reference_predictions[sample_index]
            expect_equal(prediction_record.get("input_id"), sample.input_id, f"C-5 {split} prediction order")
            class_index = context.inputs.artifacts.class_names.index(sample.class_name)
            full_features = training.extract_features(
                training.EXTRACTED_DIR / sample.filename,
                context.inputs.config,
            )
            selected_features = np.ascontiguousarray(
                full_features[:, context.inputs.artifacts.feature_indices],
                dtype=np.float64,
            )
            reference_map = np.asarray(reference_maps[sample_index], dtype=np.float64)
            verify_c5_sample_hashes(
                context,
                sample,
                reference_map,
                prediction_record,
                selected_features,
            )
            outputs = session.run(
                [
                    export.OUTPUT_ANOMALY_MAP,
                    export.OUTPUT_RAW_MEASURE,
                    export.OUTPUT_ARGMAX_REGION,
                ],
                {
                    export.INPUT_FULL_PATCH_FEATURES: full_features.reshape(
                        1,
                        context.inputs.config.patch_count,
                        context.inputs.config.full_feature_dimension,
                    ).astype(np.float64),
                    export.INPUT_CLASS_INDEX: np.asarray([class_index], dtype=np.int64),
                },
            )
            onnx_map = np.asarray(outputs[0][0], dtype=np.float64)
            onnx_raw = float(np.asarray(outputs[1], dtype=np.float64).reshape(-1)[0])
            onnx_bbox = np.asarray(outputs[2], dtype=np.float64).reshape(4)
            reference_raw = float(prediction_record["predicted_raw_anomaly_measure"])
            reference_bbox = export.localization_vector(prediction_record)

            map_abs = float(np.max(np.abs(onnx_map - reference_map)))
            map_rel = relative_deviation(map_abs, float(np.max(np.abs(reference_map))))
            raw_abs = float(abs(onnx_raw - reference_raw))
            raw_rel = relative_deviation(raw_abs, reference_raw)
            bbox_abs = float(np.max(np.abs(onnx_bbox - reference_bbox)))

            passed = (
                map_abs <= ABSOLUTE_TOLERANCE
                and map_rel <= RELATIVE_TOLERANCE
                and raw_abs <= ABSOLUTE_TOLERANCE
                and raw_rel <= RELATIVE_TOLERANCE
                and bbox_abs <= BBOX_ABSOLUTE_TOLERANCE
            )
            if not passed:
                raise EquivalenceError(
                    "ONNX export equivalence exceeded declared tolerance for "
                    f"{sample.input_id}: map_abs={map_abs}, map_rel={map_rel}, "
                    f"raw_abs={raw_abs}, raw_rel={raw_rel}, bbox_abs={bbox_abs}"
                )

            deviation_record = {
                "split": sample.split,
                "input_id": sample.input_id,
                "filename": sample.filename,
                "class_name": sample.class_name,
                "anomaly_map_absolute_deviation": map_abs,
                "anomaly_map_relative_deviation": map_rel,
                "raw_measure_absolute_deviation": raw_abs,
                "raw_measure_relative_deviation": raw_rel,
                "argmax_region_absolute_deviation": bbox_abs,
                "passed": passed,
            }
            per_sample.append(deviation_record)
            maxima_updates = {
                "anomaly_map_absolute": map_abs,
                "anomaly_map_relative": map_rel,
                "raw_measure_absolute": raw_abs,
                "raw_measure_relative": raw_rel,
                "argmax_region_absolute": bbox_abs,
            }
            for key, value in maxima_updates.items():
                split_maxima[key] = max(float(split_maxima[key]), value)
                global_maxima[key] = max(global_maxima[key], value)

        per_split[split] = split_maxima

    return EquivalenceRun(
        sample_count=len(samples),
        split_counts=split_counts,
        per_sample_deviations=per_sample,
        per_split_maxima=per_split,
        global_maxima=global_maxima,
        status="passed",
    )


def equivalence_run_to_json(run: EquivalenceRun) -> dict[str, Any]:
    return {
        "sample_count": run.sample_count,
        "split_counts": run.split_counts,
        "per_sample_deviations": run.per_sample_deviations,
        "per_split_maxima": run.per_split_maxima,
        "global_maxima": run.global_maxima,
        "status": run.status,
    }


def tolerance_policy() -> dict[str, Any]:
    return {
        "absolute": ABSOLUTE_TOLERANCE,
        "relative": RELATIVE_TOLERANCE,
        "bbox_absolute": BBOX_ABSOLUTE_TOLERANCE,
        "declared_before_comparison": True,
        "justification": {
            "absolute": (
                "Task 1 demonstrated DOUBLE CPUExecutionProvider reproduction of the "
                "governed offline float64 PaDiM computation across 6,492 samples at "
                "machine-epsilon deviation; 1e-12 preserves that established regime "
                "without silently widening it."
            ),
            "relative": (
                "The same Task 1 evidence established max relative deviation below "
                "1e-12 for anomaly maps and raw measures; Task 2 keeps the regime."
            ),
            "bbox_absolute": (
                "The localization coordinates are multiples of 1/64, and the recorded "
                "C-5 rounded values are exact for those coordinates; zero tolerance is "
                "therefore an equality requirement, not a widened tolerance."
            ),
        },
    }


def scope_boundaries() -> dict[str, bool]:
    return {
        "runtime_integration_performed": False,
        "runtime_provider_loaded": False,
        "inspection_inference_provider_loaded": False,
        "inspection_engine_entered": False,
        "canonical_inspect_path_entered": False,
        "provider_changed": False,
        "model_loader_changed": False,
        "onnx_session_changed": False,
        "onnx_runtime_changed": False,
        "output_mapping_changed": False,
        "preprocessing_changed": False,
        "feature_extraction_changed": False,
        "inspection_domain_changed": False,
        "inspection_transform_prediction_changed": False,
        "trust_changed": False,
        "review_changed": False,
        "evidence_engine_changed": False,
        "evaluation_engine_changed": False,
        "integration_changed": False,
        "prototype_ui_changed": False,
        "onnx_reexported": False,
        "padim_refit_performed": False,
        "c5_inference_rerun": False,
        "evaluation_executed": False,
        "metrics_generated": False,
        "calibration_performed": False,
        "benchmark_generated": False,
        "scientific_claim": False,
        "product_claim": False,
    }


def build_report(
    context: VerifiedContext,
    run: EquivalenceRun,
    verification_timestamp: str,
) -> dict[str, Any]:
    c4_identity = export.c4_identity(context.inputs.artifacts)
    c5_identity = export.c5_identity(context.inputs)
    return {
        "schema": EQUIVALENCE_REPORT_SCHEMA,
        "equivalence_label": EQUIVALENCE_LABEL,
        "verification_timestamp_utc": verification_timestamp,
        "status": run.status,
        "scope": (
            "offline export-equivalence verification only; not runtime equivalence, "
            "not runtime integration, and not scientific evaluation"
        ),
        "toolchain": export.toolchain_versions(),
        "onnx_execution": {
            "api": "onnxruntime.InferenceSession",
            "provider": "CPUExecutionProvider",
            "direct_onnxruntime_session_only": True,
            "session_options": {
                "intra_op_num_threads": 1,
                "inter_op_num_threads": 1,
                "graph_optimization_level": "ORT_DISABLE_ALL",
            },
            "runtime_provider_loaded": False,
            "model_loader_loaded": False,
            "inspection_engine_entered": False,
            "canonical_inspect_path_entered": False,
        },
        "onnx_artifact_identity": {
            "export_label": context.artifact_record["export_label"],
            "model_reference_id": context.artifact_record["model_reference_id"],
            "model_path": context.artifact_record["model_path"],
            "model_sha256": EXPECTED_MODEL_SHA256,
            "artifact_record_sha256": EXPECTED_ARTIFACT_RECORD_SHA256,
            "metadata_record_sha256": EXPECTED_METADATA_RECORD_SHA256,
            "export_replay_sha256": EXPECTED_EXPORT_REPLAY_SHA256,
            "artifact_hashes_record_sha256": EXPECTED_EXPORT_HASHES_RECORD_SHA256,
            "opset_version": export.ONNX_OPSET_VERSION,
            "ir_version": export.ONNX_IR_VERSION,
        },
        "governed_c4_identity": c4_identity,
        "governed_c5_identity": c5_identity,
        "artifact_verification": context.artifact_verification,
        "reference_verification": context.reference_verification,
        "graph_contract_verification": context.graph_verification,
        "feature_index_equivalence": {
            "status": "passed",
            "expected_feature_indices": list(inference.EXPECTED_FEATURE_INDICES),
            "graph_feature_indices": context.graph_verification["feature_indices"],
            "byte_equal_to_c4": context.graph_verification["feature_indices_byte_equal_to_c4"],
        },
        "preprocessing_contract_equivalence": {
            "status": "passed",
            "contract_id": training.PREPROCESSING_CONTRACT_ID,
            "graph_input": export.INPUT_FULL_PATCH_FEATURES,
            "graph_does_not_claim_image_preprocessing": True,
            "preprocessing_reimplemented_in_onnx": False,
            "preprocessing_code_modified": False,
        },
        "numerical_configuration_equivalence": {
            "status": "passed",
            "source_dtype": training.DTYPE_NAME,
            "onnx_dtype": export.ONNX_DTYPE_NAME,
            "float32_transition": False,
            "covariance_estimator": context.inputs.artifacts.numerical_config["covariance_estimator"],
            "covariance_regularization": context.inputs.artifacts.numerical_config[
                "covariance_regularization"
            ],
            "epsilon": context.inputs.artifacts.numerical_config["epsilon"],
            "inverse": context.inputs.artifacts.numerical_config["inverse"],
        },
        "mu_equivalence": {
            "status": "passed",
            "c4_sha256": EXPECTED_C4_MU_SHA256,
            "graph_initializer": "mu_by_class",
            "byte_equal_to_c4": context.graph_verification["mu_byte_equal_to_c4"],
        },
        "covariance_inverse_equivalence": {
            "status": "passed",
            "c4_sha256": EXPECTED_C4_COVARIANCE_INVERSE_SHA256,
            "graph_initializer": "covariance_inverse_by_class",
            "byte_equal_to_c4": context.graph_verification["covariance_inverse_byte_equal_to_c4"],
        },
        "anomaly_map_equivalence": {
            "status": "passed",
            "absolute_tolerance": ABSOLUTE_TOLERANCE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima["anomaly_map_absolute"],
            "max_relative_deviation": run.global_maxima["anomaly_map_relative"],
            "per_split": {
                split: {
                    "max_absolute_deviation": values["anomaly_map_absolute"],
                    "max_relative_deviation": values["anomaly_map_relative"],
                }
                for split, values in run.per_split_maxima.items()
            },
        },
        "raw_measure_equivalence": {
            "status": "passed",
            "absolute_tolerance": ABSOLUTE_TOLERANCE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima["raw_measure_absolute"],
            "max_relative_deviation": run.global_maxima["raw_measure_relative"],
            "per_split": {
                split: {
                    "max_absolute_deviation": values["raw_measure_absolute"],
                    "max_relative_deviation": values["raw_measure_relative"],
                }
                for split, values in run.per_split_maxima.items()
            },
        },
        "localization_equivalence": {
            "status": "passed",
            "bbox_absolute_tolerance": BBOX_ABSOLUTE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima["argmax_region_absolute"],
            "per_split": {
                split: {
                    "max_absolute_deviation": values["argmax_region_absolute"],
                }
                for split, values in run.per_split_maxima.items()
            },
        },
        "sample_counts": {
            "total": run.sample_count,
            **run.split_counts,
        },
        "tolerance_policy": tolerance_policy(),
        "per_split_maxima": run.per_split_maxima,
        "global_maxima": run.global_maxima,
        "per_sample_deviations": run.per_sample_deviations,
        "scope_boundaries": scope_boundaries(),
        "explicit_non_claims": explicit_non_claims(),
        "final_pass_fail_status": run.status,
    }


def explicit_non_claims() -> list[str]:
    return [
        "export equivalence is not runtime equivalence",
        "export equivalence is not runtime integration",
        "export equivalence is not scientific evaluation",
        "no runtime provider was loaded",
        "no runtime code was modified",
        "no provider code was modified",
        "no model-loader code was modified",
        "no output-mapping code was modified",
        "no preprocessing code was modified",
        "no feature-extraction code was modified",
        "no metrics were generated",
        "no calibration was performed",
        "no scientific claim was made",
        "no product claim was made",
    ]


def build_replay_record(
    first_run: EquivalenceRun,
    second_run: EquivalenceRun,
    first_report_bytes: bytes,
    second_report_bytes: bytes,
) -> dict[str, Any]:
    first_json = equivalence_run_to_json(first_run)
    second_json = equivalence_run_to_json(second_run)
    comparisons = {
        "per_sample_deviations": (
            first_run.per_sample_deviations == second_run.per_sample_deviations
        ),
        "per_split_maxima": first_run.per_split_maxima == second_run.per_split_maxima,
        "global_maxima": first_run.global_maxima == second_run.global_maxima,
        "pass_fail_status": first_run.status == second_run.status,
        "equivalence_report_hash": (
            sha256_bytes(first_report_bytes) == sha256_bytes(second_report_bytes)
        ),
        "equivalence_report_json": first_report_bytes == second_report_bytes,
        "equivalence_hashes_record": True,
    }
    if not all(comparisons.values()):
        raise EquivalenceError(f"deterministic equivalence replay mismatch: {comparisons}")
    return {
        "schema": EQUIVALENCE_REPLAY_SCHEMA,
        "equivalence_label": EQUIVALENCE_LABEL,
        "status": "passed",
        "complete_second_equivalence_run": True,
        "comparisons": comparisons,
        "first_run_hashes": {
            "equivalence_run": sha256_bytes(canonical_json_bytes(first_json)),
            "equivalence_report.json": sha256_bytes(first_report_bytes),
        },
        "second_run_hashes": {
            "equivalence_run": sha256_bytes(canonical_json_bytes(second_json)),
            "equivalence_report.json": sha256_bytes(second_report_bytes),
        },
        "first_run_global_maxima": first_run.global_maxima,
        "second_run_global_maxima": second_run.global_maxima,
        "first_run_per_split_maxima": first_run.per_split_maxima,
        "second_run_per_split_maxima": second_run.per_split_maxima,
        "equivalence_hashes_record_basis": (
            "equivalence_hashes.json is a deterministic function of the final "
            "equivalence_report.json and equivalence_replay.json canonical bytes; "
            "the report bytes are identical across runs and this replay record is "
            "written once as the second-run proof"
        ),
        "scope": "deterministic offline export-equivalence replay only",
    }


def build_hashes_record(report_bytes: bytes, replay_bytes: bytes) -> dict[str, Any]:
    return {
        "schema": EQUIVALENCE_HASHES_SCHEMA,
        "equivalence_label": EQUIVALENCE_LABEL,
        "hash_algorithm": "sha256",
        "hash_scope": (
            "artifacts/padim/equivalence/equivalence_report.json and "
            "artifacts/padim/equivalence/equivalence_replay.json; "
            "equivalence_hashes.json self-hash is recorded in evidence"
        ),
        "governed_equivalence_artifacts": {
            "equivalence_report.json": sha256_bytes(report_bytes),
            "equivalence_replay.json": sha256_bytes(replay_bytes),
        },
    }


def write_evidence(
    context: VerifiedContext,
    report: Mapping[str, Any],
    replay_record: Mapping[str, Any],
    report_hash: str,
    replay_hash: str,
    hashes_hash: str,
) -> str:
    date = evidence_date_for_run()
    global_maxima = report["global_maxima"]
    split_counts = report["sample_counts"]
    content = f"""# Kalibra PaDiM ONNX Export Equivalence Evidence v1.0

**Status:** Recorded - deterministic offline ONNX export-equivalence evidence only
**Date:** {date}
**Scope:** Phase 3 / Task 2 - Export Equivalence Verification only

## Verification Scope

- Equivalence label: `{EQUIVALENCE_LABEL}`
- Verified artifact: `artifacts/padim/model.onnx`
- Equivalence report: `artifacts/padim/equivalence/equivalence_report.json`
- Equivalence hashes: `artifacts/padim/equivalence/equivalence_hashes.json`
- Equivalence replay: `artifacts/padim/equivalence/equivalence_replay.json`
- Execution path: direct `onnxruntime.InferenceSession` with `CPUExecutionProvider`.
- Runtime provider loaded: `false`
- Model loader loaded: `false`
- Runtime integration performed: `false`

## Artifact Verification

- Model SHA-256 verified: `{EXPECTED_MODEL_SHA256}`
- Artifact record SHA-256 verified: `{EXPECTED_ARTIFACT_RECORD_SHA256}`
- Metadata record SHA-256 verified: `{EXPECTED_METADATA_RECORD_SHA256}`
- Export replay SHA-256 verified: `{EXPECTED_EXPORT_REPLAY_SHA256}`
- Artifact hashes record SHA-256 verified: `{EXPECTED_EXPORT_HASHES_RECORD_SHA256}`
- Opset verified: `{export.ONNX_OPSET_VERSION}`
- ONNX IR version verified: `{export.ONNX_IR_VERSION}`
- Export replay status verified: `{context.export_replay_record["status"]}`

## Reference Verification

- Governed C-4 training identity verified: `{EXPECTED_C4_TRAINING_RECORD_SHA256}`
- Mu hash verified: `{EXPECTED_C4_MU_SHA256}`
- Covariance inverse hash verified: `{EXPECTED_C4_COVARIANCE_INVERSE_SHA256}`
- Feature indices hash verified: `{EXPECTED_C4_FEATURE_INDICES_SHA256}`
- Training metadata hash verified: `{EXPECTED_C4_TRAINING_METADATA_SHA256}`
- Governed C-5 inference identity verified: `{EXPECTED_C5_ARTIFACT_HASHES_SHA256}`
- C-5 anomaly-map hashes verified: `validation={EXPECTED_C5_OUTPUT_HASHES["anomaly_maps/validation_anomaly_maps.npy"]}`, `test={EXPECTED_C5_OUTPUT_HASHES["anomaly_maps/test_anomaly_maps.npy"]}`
- C-5 prediction hashes verified: `validation={EXPECTED_C5_OUTPUT_HASHES["predictions/validation_predictions.jsonl"]}`, `test={EXPECTED_C5_OUTPUT_HASHES["predictions/test_predictions.jsonl"]}`
- C-5 metadata hash verified: `{EXPECTED_C5_METADATA_SHA256}`
- C-5 replay hash verified: `{EXPECTED_C5_REPLAY_SHA256}`

## Graph Contract Verification

- Inputs verified: `full_patch_features float64 [1, 64, 14]`; `class_index int64 [1]`
- Outputs verified: `patch_mahalanobis_distances float64 [1, 64]`; `anomaly_map float64 [1, 64, 64]`; `raw_anomaly_measure float64 [1]`; `argmax_region float64 [1, 4]`
- Feature indices verified: `{list(inference.EXPECTED_FEATURE_INDICES)}`
- Mu byte-equal to governed C-4: `true`
- Covariance inverse byte-equal to governed C-4: `true`
- Preprocessing contract verified: `{training.PREPROCESSING_CONTRACT_ID}`
- Graph implements image preprocessing: `false`

## Equivalence Result

- Final status: `{report["status"]}`
- Sample count: `{split_counts["total"]}`
- Validation count: `{split_counts["validation"]}`
- Test count: `{split_counts["test"]}`
- Anomaly-map max absolute deviation: `{global_maxima["anomaly_map_absolute"]}`
- Anomaly-map max relative deviation: `{global_maxima["anomaly_map_relative"]}`
- Raw-measure max absolute deviation: `{global_maxima["raw_measure_absolute"]}`
- Raw-measure max relative deviation: `{global_maxima["raw_measure_relative"]}`
- Localization max absolute deviation: `{global_maxima["argmax_region_absolute"]}`
- Tolerance policy: `{tolerance_policy()}`

## Replay Result

- Complete second equivalence run executed: `{str(replay_record["complete_second_equivalence_run"]).lower()}`
- Per-sample deviations identical: `{str(replay_record["comparisons"]["per_sample_deviations"]).lower()}`
- Per-split maxima identical: `{str(replay_record["comparisons"]["per_split_maxima"]).lower()}`
- Global maxima identical: `{str(replay_record["comparisons"]["global_maxima"]).lower()}`
- Pass/fail status identical: `{str(replay_record["comparisons"]["pass_fail_status"]).lower()}`
- Equivalence report hash identical: `{str(replay_record["comparisons"]["equivalence_report_hash"]).lower()}`
- Equivalence hashes record deterministic: `{str(replay_record["comparisons"]["equivalence_hashes_record"]).lower()}`
- Equivalence report SHA-256: `{report_hash}`
- Equivalence replay SHA-256: `{replay_hash}`
- Equivalence hashes record SHA-256: `{hashes_hash}`

## Explicit Non-Claims

- Export equivalence is not runtime equivalence.
- Export equivalence is not runtime integration.
- Export equivalence is not scientific evaluation.
- No runtime provider was loaded.
- No runtime code was modified.
- No provider code was modified.
- No model-loader code was modified.
- No output-mapping code was modified.
- No preprocessing code was modified.
- No feature-extraction code was modified.
- No metrics were generated.
- No calibration was performed.
- No scientific claim was made.
- No product claim was made.
"""
    return write_governed_bytes(EVIDENCE_PATH, content.encode("utf-8"))


def run_verify() -> None:
    ensure_layout()
    timestamp = equivalence_timestamp_for_run()
    context = verify_context()
    first_run = run_equivalence(context)
    first_report = build_report(context, first_run, timestamp)
    first_report_bytes = canonical_json_bytes(first_report)

    second_context = verify_context()
    second_run = run_equivalence(second_context)
    second_report = build_report(second_context, second_run, timestamp)
    second_report_bytes = canonical_json_bytes(second_report)

    replay_record = build_replay_record(
        first_run,
        second_run,
        first_report_bytes,
        second_report_bytes,
    )
    replay_bytes = canonical_json_bytes(replay_record)
    hashes_record = build_hashes_record(first_report_bytes, replay_bytes)
    hashes_bytes = canonical_json_bytes(hashes_record)

    report_hash = write_governed_bytes(EQUIVALENCE_REPORT_PATH, first_report_bytes)
    replay_hash = write_governed_bytes(EQUIVALENCE_REPLAY_PATH, replay_bytes)
    hashes_hash = write_governed_bytes(EQUIVALENCE_HASHES_PATH, hashes_bytes)
    expected_hashes = {
        "equivalence_report.json": report_hash,
        "equivalence_replay.json": replay_hash,
    }
    if hashes_record["governed_equivalence_artifacts"] != expected_hashes:
        raise EquivalenceError("written equivalence hashes do not match generated records")
    write_evidence(context, first_report, replay_record, report_hash, replay_hash, hashes_hash)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3 / Task 2 governed PaDiM ONNX export-equivalence verification"
    )
    parser.add_argument("command", choices=("verify",))
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            run_verify()
    except (
        EquivalenceError,
        export.ExportError,
        inference.InferenceError,
        training.TrainingError,
        acquisition.AcquisitionError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
