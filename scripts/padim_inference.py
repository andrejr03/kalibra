#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import governed_visa_acquisition as acquisition  # noqa: E402
import train_padim_baseline as training  # noqa: E402
from src.inspection.domain import (  # noqa: E402
    DefectLocalization,
    InspectionJudgement,
    InspectionPrediction,
    NormalizedBoundingBox,
)


PADIM_ROOT = training.PADIM_ROOT
INFERENCE_DIR = PADIM_ROOT / "inference"
ANOMALY_MAPS_DIR = INFERENCE_DIR / "anomaly_maps"
PREDICTIONS_DIR = INFERENCE_DIR / "predictions"
INFERENCE_METADATA_DIR = INFERENCE_DIR / "metadata"
REPLAY_DIR = INFERENCE_DIR / "replay"
INFERENCE_ARTIFACT_HASHES_PATH = INFERENCE_DIR / "artifact_hashes.json"
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md"
)

INFERENCE_LABEL = "visa-padim-governed-inference-v1"
INFERENCE_RECORD_SCHEMA = "kalibra_governed_padim_inference_metadata_v1"
INFERENCE_ARTIFACT_HASHES_SCHEMA = "kalibra_governed_padim_inference_artifact_hashes_v1"
INFERENCE_REPLAY_SCHEMA = "kalibra_governed_padim_inference_replay_v1"
PREDICTION_RECORD_SCHEMA = "kalibra_governed_padim_prediction_record_v1"
ARTIFACT_IDENTITY_SCHEMA = "kalibra_governed_padim_artifact_identity_v1"
INFERENCE_SPLITS = ("validation", "test")
AGGREGATION_POLICY = "maximum finite Mahalanobis distance over anomaly map"
AGGREGATION_IDENTIFIER = "padim_anomaly_map_max_v1"
LOCALIZATION_POLICY = "bounding box covering pixels equal to maximum anomaly-map value"
LOCALIZATION_IDENTIFIER = "padim_raw_anomaly_map_argmax_region_v1"
PREDICTION_JUDGEMENT_POLICY = (
    "contract_required_defect_for_raw_localization_no_threshold_v1"
)
EXPECTED_FEATURE_INDICES = (0, 2, 5, 6, 7, 9, 12, 13)
DTYPE_NAME = "float64"


class InferenceError(RuntimeError):
    """Raised when C-5 inference cannot proceed safely."""


@dataclass(frozen=True)
class InferenceSample:
    split: str
    filename: str
    class_name: str
    sha256: str
    input_id: str


@dataclass(frozen=True)
class GovernedArtifacts:
    class_names: tuple[str, ...]
    mu: np.ndarray
    covariance_inverse: np.ndarray
    feature_indices: np.ndarray
    dataset_identity: dict[str, Any]
    preprocessing_contract: dict[str, Any]
    backbone_metadata: dict[str, Any]
    numerical_config: dict[str, Any]
    feature_indices_metadata: dict[str, Any]
    training_metadata: dict[str, Any]
    training_record: dict[str, Any]
    training_artifact_hashes: dict[str, Any]
    training_replay_record: dict[str, Any]
    artifact_identity: dict[str, Any]


@dataclass(frozen=True)
class SampleInferenceRecord:
    split: str
    input_id: str
    filename: str
    class_name: str
    sample_sha256: str
    feature_tensor_sha256: str
    anomaly_map_sha256: str
    prediction_sha256: str
    predicted_raw_anomaly_measure: float
    localization: dict[str, Any]
    prediction_record: dict[str, Any]


@dataclass(frozen=True)
class InferenceRunResult:
    sample_records: tuple[SampleInferenceRecord, ...]
    output_artifact_hashes: dict[str, str]


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
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def npy_bytes(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, array, allow_pickle=False)
    return buffer.getvalue()


def npy_sha256(array: np.ndarray) -> str:
    return sha256_bytes(npy_bytes(array))


def stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    digest = sha256_bytes(canonical_json_bytes(value))
    return f"{prefix}-{digest[:24]}"


def ensure_layout() -> None:
    for directory in (
        ANOMALY_MAPS_DIR,
        PREDICTIONS_DIR,
        INFERENCE_METADATA_DIR,
        REPLAY_DIR,
        EVIDENCE_PATH.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def write_governed_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise InferenceError(f"governed inference record changed: {path}")
        return acquisition.sha256_file(path)
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def write_local_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise InferenceError(f"local inference artifact changed: {path}")
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def write_json_record(path: Path, value: Mapping[str, Any]) -> str:
    return write_governed_bytes(path, canonical_json_bytes(value))


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise InferenceError(f"missing governed record: {path}") from exc
    if not isinstance(value, dict):
        raise InferenceError(f"governed record is not a JSON object: {path}")
    return value


def verify_file_hash(path: Path, expected: str, label: str) -> str:
    if not path.exists():
        raise InferenceError(f"missing governed artifact for {label}: {path}")
    actual = acquisition.sha256_file(path)
    if actual != expected:
        raise InferenceError(
            f"governed artifact hash mismatch for {label}: expected {expected}, got {actual}"
        )
    return actual


def verify_recorded_training_artifacts(
    artifact_hashes: Mapping[str, Any],
) -> None:
    for section in ("array_artifacts", "metadata_artifacts"):
        records = artifact_hashes.get(section)
        if not isinstance(records, Mapping):
            raise InferenceError(f"training artifact hash record lacks {section}")
        for relative_path, expected_digest in records.items():
            if not isinstance(relative_path, str) or not isinstance(expected_digest, str):
                raise InferenceError(f"invalid training artifact hash entry in {section}")
            verify_file_hash(PADIM_ROOT / relative_path, expected_digest, relative_path)


def load_json_artifact(
    relative_path: str,
    artifact_hashes: Mapping[str, Any],
) -> dict[str, Any]:
    metadata_artifacts = artifact_hashes.get("metadata_artifacts")
    if not isinstance(metadata_artifacts, Mapping):
        raise InferenceError("training artifact hash record lacks metadata artifacts")
    expected = metadata_artifacts.get(relative_path)
    if not isinstance(expected, str):
        raise InferenceError(f"missing metadata artifact hash for {relative_path}")
    path = PADIM_ROOT / relative_path
    verify_file_hash(path, expected, relative_path)
    return read_json_mapping(path)


def load_npy_artifact(
    relative_path: str,
    artifact_hashes: Mapping[str, Any],
) -> np.ndarray:
    array_artifacts = artifact_hashes.get("array_artifacts")
    if not isinstance(array_artifacts, Mapping):
        raise InferenceError("training artifact hash record lacks array artifacts")
    expected = array_artifacts.get(relative_path)
    if not isinstance(expected, str):
        raise InferenceError(f"missing array artifact hash for {relative_path}")
    path = PADIM_ROOT / relative_path
    verify_file_hash(path, expected, relative_path)
    return np.load(path, allow_pickle=False)


def load_governed_artifacts(
    governed: Mapping[str, Any],
    config: training.FitConfig,
) -> GovernedArtifacts:
    artifact_hashes_path = training.TRAINING_DIR / "artifact_hashes.json"
    training_artifact_hashes = read_json_mapping(artifact_hashes_path)
    if training_artifact_hashes.get("schema") != "kalibra_padim_training_artifact_hashes_v1":
        raise InferenceError("unexpected C-4 training artifact hash schema")
    verify_recorded_training_artifacts(training_artifact_hashes)

    training_record_path = training.TRAINING_DIR / "training_record.json"
    training_record = read_json_mapping(training_record_path)
    training_record_hash = acquisition.sha256_file(training_record_path)
    artifact_hash_record_sha256 = acquisition.sha256_file(artifact_hashes_path)
    if training_record.get("artifact_hashes_record_sha256") != artifact_hash_record_sha256:
        raise InferenceError("training record does not match C-4 artifact hashes identity")

    replay_info = training_artifact_hashes.get("replay_verification")
    if not isinstance(replay_info, Mapping):
        raise InferenceError("training artifact hash record lacks replay verification")
    replay_path = REPO_ROOT / str(replay_info.get("path", ""))
    replay_sha = replay_info.get("sha256")
    if not isinstance(replay_sha, str):
        raise InferenceError("training replay hash is missing")
    verify_file_hash(replay_path, replay_sha, "training replay verification")
    training_replay_record = read_json_mapping(replay_path)
    if training_replay_record.get("status") != "passed":
        raise InferenceError("C-4 replay verification is not passed")

    training_metadata_path = training.METADATA_DIR / "training_metadata.json"
    training_metadata_sha256 = verify_file_hash(
        training_metadata_path,
        str(training_record.get("training_metadata_sha256")),
        "training metadata",
    )
    training_metadata = read_json_mapping(training_metadata_path)
    if training_record.get("training_metadata_sha256") != training_metadata_sha256:
        raise InferenceError("training metadata hash does not match training record")
    if training_record.get("replay_verification_sha256") != replay_sha:
        raise InferenceError("training replay hash does not match training record")

    scope = training_metadata.get("scope_boundaries")
    if not isinstance(scope, Mapping):
        raise InferenceError("training metadata lacks scope boundaries")
    for key in (
        "inference_executed",
        "validation_inference_executed",
        "test_inference_executed",
        "evaluation_executed",
        "benchmark_generated",
        "onnx_exported",
        "scientific_claim",
    ):
        if scope.get(key) is not False:
            raise InferenceError(f"C-4 training scope boundary is not closed: {key}")

    dataset_identity = load_json_artifact(
        "metadata/dataset_identity.json",
        training_artifact_hashes,
    )
    if dataset_identity != training.dataset_identity(governed):
        raise InferenceError("C-4 dataset identity does not match governed acquisition")

    preprocessing_contract = load_json_artifact(
        "metadata/preprocessing_contract.json",
        training_artifact_hashes,
    )
    backbone_metadata = load_json_artifact(
        "metadata/backbone_metadata.json",
        training_artifact_hashes,
    )
    numerical_config = load_json_artifact(
        "metadata/numerical_config.json",
        training_artifact_hashes,
    )
    feature_indices_metadata = load_json_artifact(
        "metadata/feature_indices.json",
        training_artifact_hashes,
    )

    verify_metadata_contracts(
        preprocessing_contract,
        backbone_metadata,
        numerical_config,
        feature_indices_metadata,
        config,
    )

    mu = load_npy_artifact("statistics/mu_by_class.npy", training_artifact_hashes)
    covariance_inverse = load_npy_artifact(
        "covariance/covariance_inverse_by_class.npy",
        training_artifact_hashes,
    )
    feature_indices = load_npy_artifact(
        "statistics/feature_indices.npy",
        training_artifact_hashes,
    )

    class_names = training_record.get("class_order")
    if not isinstance(class_names, list) or not all(
        isinstance(class_name, str) for class_name in class_names
    ):
        raise InferenceError("training record lacks class order")
    class_order = tuple(class_names)
    verify_loaded_array_contracts(mu, covariance_inverse, feature_indices, class_order, config)

    artifact_identity = {
        "schema": ARTIFACT_IDENTITY_SCHEMA,
        "training_label": training_record["training_label"],
        "training_record_sha256": training_record_hash,
        "training_artifact_hashes_sha256": artifact_hash_record_sha256,
        "training_metadata_sha256": training_metadata_sha256,
        "training_replay_verification_sha256": replay_sha,
        "mu_by_class_sha256": training_artifact_hashes["array_artifacts"][
            "statistics/mu_by_class.npy"
        ],
        "covariance_inverse_by_class_sha256": training_artifact_hashes[
            "array_artifacts"
        ]["covariance/covariance_inverse_by_class.npy"],
        "feature_indices_sha256": training_artifact_hashes["array_artifacts"][
            "statistics/feature_indices.npy"
        ],
        "class_order": list(class_order),
        "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
        "backbone_identity": training.BACKBONE_IDENTITY,
        "selected_layer": training.BACKBONE_LAYER,
        "dtype": DTYPE_NAME,
    }

    return GovernedArtifacts(
        class_names=class_order,
        mu=np.ascontiguousarray(mu, dtype=np.float64),
        covariance_inverse=np.ascontiguousarray(covariance_inverse, dtype=np.float64),
        feature_indices=np.ascontiguousarray(feature_indices, dtype=np.int64),
        dataset_identity=dataset_identity,
        preprocessing_contract=preprocessing_contract,
        backbone_metadata=backbone_metadata,
        numerical_config=numerical_config,
        feature_indices_metadata=feature_indices_metadata,
        training_metadata=training_metadata,
        training_record=training_record,
        training_artifact_hashes=training_artifact_hashes,
        training_replay_record=training_replay_record,
        artifact_identity=artifact_identity,
    )


def verify_metadata_contracts(
    preprocessing_contract: Mapping[str, Any],
    backbone_metadata: Mapping[str, Any],
    numerical_config: Mapping[str, Any],
    feature_indices_metadata: Mapping[str, Any],
    config: training.FitConfig,
) -> None:
    if preprocessing_contract.get("contract_id") != training.PREPROCESSING_CONTRACT_ID:
        raise InferenceError("unexpected preprocessing contract id")
    contract_config = preprocessing_contract.get("config")
    if not isinstance(contract_config, Mapping):
        raise InferenceError("preprocessing contract lacks config")
    expected_config = config.to_json_dict()
    for key in (
        "image_size",
        "patch_size",
        "patch_grid",
        "patch_count",
        "full_feature_dimension",
        "selected_feature_dimension",
        "batch_size",
        "dtype",
    ):
        if contract_config.get(key) != expected_config[key]:
            raise InferenceError(f"preprocessing contract mismatch: {key}")
    if backbone_metadata.get("backbone_identity") != training.BACKBONE_IDENTITY:
        raise InferenceError("unexpected backbone identity")
    if backbone_metadata.get("selected_layers") != [training.BACKBONE_LAYER]:
        raise InferenceError("unexpected selected backbone layer")
    if numerical_config.get("dtype") != DTYPE_NAME:
        raise InferenceError("unexpected numerical dtype")
    batching = numerical_config.get("batching")
    if not isinstance(batching, Mapping) or batching.get("batch_size") != config.batch_size:
        raise InferenceError("unexpected inference batching contract")
    if feature_indices_metadata.get("selected_indices") != list(EXPECTED_FEATURE_INDICES):
        raise InferenceError("unexpected governed feature indices")


def verify_loaded_array_contracts(
    mu: np.ndarray,
    covariance_inverse: np.ndarray,
    feature_indices: np.ndarray,
    class_order: Sequence[str],
    config: training.FitConfig,
) -> None:
    expected_mu_shape = (
        len(class_order),
        config.patch_count,
        config.selected_feature_dimension,
    )
    expected_inverse_shape = (
        len(class_order),
        config.patch_count,
        config.selected_feature_dimension,
        config.selected_feature_dimension,
    )
    if mu.shape != expected_mu_shape:
        raise InferenceError(f"unexpected mu shape: {mu.shape}")
    if covariance_inverse.shape != expected_inverse_shape:
        raise InferenceError(
            f"unexpected covariance inverse shape: {covariance_inverse.shape}"
        )
    if feature_indices.shape != (config.selected_feature_dimension,):
        raise InferenceError(f"unexpected feature index shape: {feature_indices.shape}")
    if mu.dtype != np.float64 or covariance_inverse.dtype != np.float64:
        raise InferenceError("governed PaDiM arrays must be float64")
    if not np.array_equal(feature_indices, np.array(EXPECTED_FEATURE_INDICES)):
        raise InferenceError("loaded feature indices do not match the governed index set")
    if not np.all(np.isfinite(mu)) or not np.all(np.isfinite(covariance_inverse)):
        raise InferenceError("governed PaDiM arrays contain non-finite values")


def load_inference_samples(
    file_hashes: Mapping[str, str],
    class_names: Sequence[str],
) -> list[InferenceSample]:
    samples: list[InferenceSample] = []
    class_set = set(class_names)
    for split in INFERENCE_SPLITS:
        samples.extend(load_split_samples(split, file_hashes, class_set))
    if not samples:
        raise InferenceError("no governed inference samples loaded")
    return sorted(samples, key=lambda sample: (sample.split, sample.class_name, sample.filename))


def load_split_samples(
    split: str,
    file_hashes: Mapping[str, str],
    class_names: set[str],
) -> list[InferenceSample]:
    split_path = training.SPLITS_DIR / f"{split}.csv"
    expected_header = [
        "filename",
        "class",
        "label",
        "artifact_type",
        "sha256",
        "source_csv",
        "source_split",
        "source_label",
        "source_image",
        "source_mask",
    ]
    samples: list[InferenceSample] = []
    seen: set[str] = set()
    with split_path.open(newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != expected_header:
            raise InferenceError(f"unexpected {split} manifest header: {reader.fieldnames}")
        for row in reader:
            if row["artifact_type"] != "image":
                continue
            filename = row["filename"]
            if filename in seen:
                raise InferenceError(f"duplicate image row in {split} split: {filename}")
            seen.add(filename)
            class_name = row["class"]
            if class_name not in class_names:
                raise InferenceError(f"sample class lacks governed PaDiM artifact: {class_name}")
            if row["source_image"] != filename:
                raise InferenceError(f"image row source_image mismatch: {filename}")
            if filename not in file_hashes:
                raise InferenceError(f"inference sample missing from files.sha256: {filename}")
            if file_hashes[filename] != row["sha256"]:
                raise InferenceError(f"inference sample hash mismatch: {filename}")
            image_path = training.EXTRACTED_DIR / filename
            if not image_path.exists():
                raise InferenceError(f"inference image missing from extracted dataset: {filename}")
            input_id = stable_id(
                "visa-inference-input",
                {
                    "split": split,
                    "filename": filename,
                    "sha256": row["sha256"],
                },
            )
            samples.append(
                InferenceSample(
                    split=split,
                    filename=filename,
                    class_name=class_name,
                    sha256=row["sha256"],
                    input_id=input_id,
                )
            )
    if not samples:
        raise InferenceError(f"{split} split has no image rows")
    return samples


def mahalanobis_patch_distances(
    selected_features: np.ndarray,
    mu: np.ndarray,
    covariance_inverse: np.ndarray,
) -> np.ndarray:
    if selected_features.shape != mu.shape:
        raise InferenceError(
            f"feature/mu shape mismatch: {selected_features.shape} vs {mu.shape}"
        )
    if covariance_inverse.shape != (
        selected_features.shape[0],
        selected_features.shape[1],
        selected_features.shape[1],
    ):
        raise InferenceError(f"unexpected covariance inverse shape: {covariance_inverse.shape}")
    diff = selected_features - mu
    squared = np.einsum("pi,pij,pj->p", diff, covariance_inverse, diff)
    if not np.all(np.isfinite(squared)):
        raise InferenceError("non-finite Mahalanobis distance encountered")
    distances = np.sqrt(np.maximum(squared, 0.0))
    return np.ascontiguousarray(distances, dtype=np.float64)


def anomaly_map_from_patch_distances(
    patch_distances: np.ndarray,
    config: training.FitConfig,
) -> np.ndarray:
    patch_map = np.ascontiguousarray(
        patch_distances.reshape(config.patch_grid),
        dtype=np.float64,
    )
    anomaly_map = np.repeat(
        np.repeat(patch_map, config.patch_size, axis=0),
        config.patch_size,
        axis=1,
    )
    expected_shape = (config.image_size, config.image_size)
    if anomaly_map.shape != expected_shape:
        raise InferenceError(f"unexpected anomaly map shape: {anomaly_map.shape}")
    return np.ascontiguousarray(anomaly_map, dtype=np.float64)


def aggregate_raw_anomaly_measure(anomaly_map: np.ndarray) -> float:
    if anomaly_map.dtype != np.float64:
        raise InferenceError("anomaly map must remain float64")
    if not np.all(np.isfinite(anomaly_map)):
        raise InferenceError("anomaly map contains non-finite values")
    return float(np.max(anomaly_map))


def localization_from_anomaly_map(anomaly_map: np.ndarray) -> DefectLocalization:
    raw_maximum = aggregate_raw_anomaly_measure(anomaly_map)
    rows, cols = np.where(anomaly_map == raw_maximum)
    if rows.size == 0 or cols.size == 0:
        raise InferenceError("cannot derive localization from empty maximum set")
    height, width = anomaly_map.shape
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=round(float(cols.min()) / width, 6),
            y_min=round(float(rows.min()) / height, 6),
            x_max=round(float(cols.max() + 1) / width, 6),
            y_max=round(float(rows.max() + 1) / height, 6),
        ),
        label="raw_anomaly_maximum",
        localization_kind=LOCALIZATION_IDENTIFIER,
    )


def localization_to_json(localization: DefectLocalization) -> dict[str, Any]:
    return {
        "label": localization.label,
        "localization_kind": localization.localization_kind,
        "region": {
            "x_min": localization.region.x_min,
            "y_min": localization.region.y_min,
            "x_max": localization.region.x_max,
            "y_max": localization.region.y_max,
        },
    }


def prediction_to_json(prediction: InspectionPrediction) -> dict[str, Any]:
    localization = (
        None
        if prediction.predicted_localization is None
        else localization_to_json(prediction.predicted_localization)
    )
    return {
        "schema": PREDICTION_RECORD_SCHEMA,
        "input_id": prediction.input_id,
        "prediction_id": prediction.prediction_id,
        "predicted_judgement": prediction.predicted_judgement.value,
        "predicted_raw_anomaly_measure": prediction.predicted_raw_anomaly_measure,
        "predicted_localization": localization,
        "raw_measure_kind": prediction.raw_measure_kind,
        "raw_measure_scale": prediction.raw_measure_scale,
        "prediction_kind": prediction.prediction_kind,
        "model_metadata": dict(prediction.model_metadata),
    }


def prediction_metadata(
    sample: InferenceSample,
    artifacts: GovernedArtifacts,
    anomaly_map_sha256: str,
    feature_tensor_sha256: str,
) -> dict[str, str]:
    split_hash = artifacts.dataset_identity["split_hashes"][sample.split]
    return {
        "method": INFERENCE_LABEL,
        "training_label": str(artifacts.training_record["training_label"]),
        "dataset": "VisA",
        "dataset_acquisition_label": str(artifacts.dataset_identity["acquisition_label"]),
        "archive_sha256": str(artifacts.dataset_identity["archive_sha256"]),
        "files_manifest_sha256": str(artifacts.dataset_identity["files_manifest_sha256"]),
        "split": sample.split,
        "split_sha256": str(split_hash),
        "sample_filename": sample.filename,
        "sample_sha256": sample.sha256,
        "class_name": sample.class_name,
        "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
        "backbone_identity": training.BACKBONE_IDENTITY,
        "selected_layer": training.BACKBONE_LAYER,
        "feature_indices": json.dumps(list(EXPECTED_FEATURE_INDICES), separators=(",", ":")),
        "dtype": DTYPE_NAME,
        "mu_by_class_sha256": str(artifacts.artifact_identity["mu_by_class_sha256"]),
        "covariance_inverse_by_class_sha256": str(
            artifacts.artifact_identity["covariance_inverse_by_class_sha256"]
        ),
        "feature_indices_sha256": str(artifacts.artifact_identity["feature_indices_sha256"]),
        "aggregation_policy": AGGREGATION_POLICY,
        "aggregation_identifier": AGGREGATION_IDENTIFIER,
        "localization_policy": LOCALIZATION_POLICY,
        "localization_identifier": LOCALIZATION_IDENTIFIER,
        "prediction_judgement_policy": PREDICTION_JUDGEMENT_POLICY,
        "anomaly_map_sha256": anomaly_map_sha256,
        "feature_tensor_sha256": feature_tensor_sha256,
    }


def infer_sample(
    sample: InferenceSample,
    artifacts: GovernedArtifacts,
    config: training.FitConfig,
) -> tuple[np.ndarray, SampleInferenceRecord]:
    class_index = artifacts.class_names.index(sample.class_name)
    full_features = training.extract_features(training.EXTRACTED_DIR / sample.filename, config)
    selected_features = np.ascontiguousarray(
        full_features[:, artifacts.feature_indices],
        dtype=np.float64,
    )
    feature_tensor_sha256 = npy_sha256(selected_features)
    patch_distances = mahalanobis_patch_distances(
        selected_features,
        artifacts.mu[class_index],
        artifacts.covariance_inverse[class_index],
    )
    anomaly_map = anomaly_map_from_patch_distances(patch_distances, config)
    anomaly_map_sha256 = npy_sha256(anomaly_map)
    raw_measure = aggregate_raw_anomaly_measure(anomaly_map)
    localization = localization_from_anomaly_map(anomaly_map)
    metadata = prediction_metadata(
        sample,
        artifacts,
        anomaly_map_sha256,
        feature_tensor_sha256,
    )
    prediction_id = stable_id(
        "padim-inspection-prediction",
        {
            "input_id": sample.input_id,
            "method": INFERENCE_LABEL,
            "training_label": artifacts.training_record["training_label"],
            "aggregation_identifier": AGGREGATION_IDENTIFIER,
            "localization_identifier": LOCALIZATION_IDENTIFIER,
        },
    )
    prediction = InspectionPrediction(
        input_id=sample.input_id,
        prediction_id=prediction_id,
        predicted_judgement=InspectionJudgement.DEFECT,
        predicted_raw_anomaly_measure=raw_measure,
        predicted_localization=localization,
        model_metadata=metadata,
    )
    prediction_record = prediction_to_json(prediction)
    prediction_sha256 = sha256_bytes(canonical_json_bytes(prediction_record))
    return anomaly_map, SampleInferenceRecord(
        split=sample.split,
        input_id=sample.input_id,
        filename=sample.filename,
        class_name=sample.class_name,
        sample_sha256=sample.sha256,
        feature_tensor_sha256=feature_tensor_sha256,
        anomaly_map_sha256=anomaly_map_sha256,
        prediction_sha256=prediction_sha256,
        predicted_raw_anomaly_measure=raw_measure,
        localization=localization_to_json(localization),
        prediction_record=prediction_record,
    )


def execute_inference_run(
    samples: Sequence[InferenceSample],
    artifacts: GovernedArtifacts,
    config: training.FitConfig,
    persist_outputs: bool,
) -> InferenceRunResult:
    sample_records: list[SampleInferenceRecord] = []
    anomaly_maps_by_split: dict[str, list[np.ndarray]] = defaultdict(list)
    predictions_by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for batch in training.iter_batches(samples, config.batch_size):
        for sample in batch:
            anomaly_map, record = infer_sample(sample, artifacts, config)
            sample_records.append(record)
            anomaly_maps_by_split[sample.split].append(anomaly_map)
            predictions_by_split[sample.split].append(record.prediction_record)

    output_hashes: dict[str, str] = {}
    for split in INFERENCE_SPLITS:
        maps = anomaly_maps_by_split.get(split)
        predictions = predictions_by_split.get(split)
        if not maps or not predictions:
            raise InferenceError(f"missing inference outputs for split: {split}")
        anomaly_stack = np.ascontiguousarray(np.stack(maps, axis=0), dtype=np.float64)
        anomaly_path = ANOMALY_MAPS_DIR / f"{split}_anomaly_maps.npy"
        anomaly_content = npy_bytes(anomaly_stack)
        relative_anomaly_path = anomaly_path.relative_to(INFERENCE_DIR).as_posix()
        output_hashes[relative_anomaly_path] = (
            write_local_bytes(anomaly_path, anomaly_content)
            if persist_outputs
            else sha256_bytes(anomaly_content)
        )

        prediction_path = PREDICTIONS_DIR / f"{split}_predictions.jsonl"
        prediction_content = b"".join(canonical_json_line(record) for record in predictions)
        relative_prediction_path = prediction_path.relative_to(INFERENCE_DIR).as_posix()
        output_hashes[relative_prediction_path] = (
            write_local_bytes(prediction_path, prediction_content)
            if persist_outputs
            else sha256_bytes(prediction_content)
        )

    return InferenceRunResult(
        sample_records=tuple(sample_records),
        output_artifact_hashes=dict(sorted(output_hashes.items())),
    )


def compare_inference_runs(
    first: InferenceRunResult,
    second: InferenceRunResult,
) -> dict[str, bool]:
    first_sample_records = [sample_record_to_comparison(record) for record in first.sample_records]
    second_sample_records = [sample_record_to_comparison(record) for record in second.sample_records]
    comparisons = {
        "feature_tensors": all(
            first_record["feature_tensor_sha256"] == second_record["feature_tensor_sha256"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "anomaly_maps": all(
            first_record["anomaly_map_sha256"] == second_record["anomaly_map_sha256"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "raw_anomaly_measures": all(
            first_record["predicted_raw_anomaly_measure"]
            == second_record["predicted_raw_anomaly_measure"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "localizations": all(
            first_record["localization"] == second_record["localization"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "inspection_predictions": all(
            first_record["prediction_record"] == second_record["prediction_record"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "prediction_hashes": all(
            first_record["prediction_sha256"] == second_record["prediction_sha256"]
            for first_record, second_record in zip(first_sample_records, second_sample_records)
        )
        and len(first_sample_records) == len(second_sample_records),
        "output_artifact_hashes": first.output_artifact_hashes == second.output_artifact_hashes,
        "sample_order": [
            first_record["input_id"] for first_record in first_sample_records
        ]
        == [second_record["input_id"] for second_record in second_sample_records],
    }
    if not all(comparisons.values()):
        raise InferenceError(f"deterministic replay mismatch: {comparisons}")
    return comparisons


def sample_record_to_comparison(record: SampleInferenceRecord) -> dict[str, Any]:
    return {
        "split": record.split,
        "input_id": record.input_id,
        "filename": record.filename,
        "class_name": record.class_name,
        "sample_sha256": record.sample_sha256,
        "feature_tensor_sha256": record.feature_tensor_sha256,
        "anomaly_map_sha256": record.anomaly_map_sha256,
        "prediction_sha256": record.prediction_sha256,
        "predicted_raw_anomaly_measure": record.predicted_raw_anomaly_measure,
        "localization": record.localization,
        "prediction_record": record.prediction_record,
    }


def sample_artifact_hashes(
    run: InferenceRunResult,
) -> dict[str, dict[str, str]]:
    return {
        record.input_id: {
            "split": record.split,
            "filename": record.filename,
            "class_name": record.class_name,
            "sample_sha256": record.sample_sha256,
            "feature_tensor_sha256": record.feature_tensor_sha256,
            "anomaly_map_sha256": record.anomaly_map_sha256,
            "prediction_sha256": record.prediction_sha256,
        }
        for record in run.sample_records
    }


def split_counts(samples: Sequence[InferenceSample]) -> dict[str, int]:
    return dict(sorted(Counter(sample.split for sample in samples).items()))


def class_counts(samples: Sequence[InferenceSample]) -> dict[str, dict[str, int]]:
    by_split: dict[str, Counter[str]] = defaultdict(Counter)
    for sample in samples:
        by_split[sample.split][sample.class_name] += 1
    return {
        split: dict(sorted(counts.items()))
        for split, counts in sorted(by_split.items())
    }


def inference_timestamp_for_run() -> str:
    metadata_path = INFERENCE_METADATA_DIR / "inference_metadata.json"
    if not metadata_path.exists():
        return utc_timestamp()
    metadata = read_json_mapping(metadata_path)
    timestamp = metadata.get("inference_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise InferenceError("existing inference metadata lacks inference timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text().splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise InferenceError("existing inference evidence lacks Date field")


def build_replay_record(
    first: InferenceRunResult,
    second: InferenceRunResult,
    comparisons: Mapping[str, bool],
) -> dict[str, Any]:
    return {
        "schema": INFERENCE_REPLAY_SCHEMA,
        "status": "passed",
        "complete_second_inference_run": True,
        "sample_count": len(first.sample_records),
        "comparisons": dict(sorted(comparisons.items())),
        "first_run_output_artifact_hashes": first.output_artifact_hashes,
        "second_run_output_artifact_hashes": second.output_artifact_hashes,
        "first_run_sample_artifact_hashes_sha256": sha256_bytes(
            canonical_json_bytes(sample_artifact_hashes(first))
        ),
        "second_run_sample_artifact_hashes_sha256": sha256_bytes(
            canonical_json_bytes(sample_artifact_hashes(second))
        ),
    }


def write_metadata_records(
    artifacts: GovernedArtifacts,
    samples: Sequence[InferenceSample],
    first: InferenceRunResult,
    inference_timestamp: str,
) -> dict[str, str]:
    metadata_hashes: dict[str, str] = {}
    metadata_hashes["metadata/dataset_identity.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "dataset_identity.json",
        artifacts.dataset_identity,
    )
    metadata_hashes["metadata/artifact_identity.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "artifact_identity.json",
        artifacts.artifact_identity,
    )
    metadata_hashes["metadata/preprocessing_contract.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "preprocessing_contract.json",
        artifacts.preprocessing_contract,
    )
    metadata_hashes["metadata/backbone_metadata.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "backbone_metadata.json",
        artifacts.backbone_metadata,
    )
    metadata_hashes["metadata/numerical_config.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "numerical_config.json",
        artifacts.numerical_config,
    )
    metadata_hashes["metadata/feature_indices.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "feature_indices.json",
        artifacts.feature_indices_metadata,
    )
    metadata_hashes["metadata/inference_inputs.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "inference_inputs.json",
        {
            "schema": "kalibra_governed_padim_inference_inputs_v1",
            "consumed_splits": list(INFERENCE_SPLITS),
            "sample_count": len(samples),
            "split_counts": split_counts(samples),
            "class_counts": class_counts(samples),
            "samples": [
                {
                    "split": sample.split,
                    "input_id": sample.input_id,
                    "filename": sample.filename,
                    "class_name": sample.class_name,
                    "sample_sha256": sample.sha256,
                }
                for sample in samples
            ],
            "label_use": "split label columns are not consumed for inference decisions",
            "mask_use": "mask rows and mask paths are not consumed for inference decisions",
        },
    )
    inference_metadata = {
        "schema": INFERENCE_RECORD_SCHEMA,
        "inference_label": INFERENCE_LABEL,
        "inference_timestamp_utc": inference_timestamp,
        "dataset_identity": artifacts.dataset_identity,
        "artifact_identity": artifacts.artifact_identity,
        "consumed_splits": list(INFERENCE_SPLITS),
        "split_identity": {
            "validation_split_sha256": training.VALIDATION_SPLIT_SHA256,
            "test_split_sha256": training.TEST_SPLIT_SHA256,
            "train_split_sha256": training.TRAIN_SPLIT_SHA256,
            "inference_consumed_splits": list(INFERENCE_SPLITS),
        },
        "sample_count": len(samples),
        "split_counts": split_counts(samples),
        "class_counts": class_counts(samples),
        "preprocessing_contract_id": training.PREPROCESSING_CONTRACT_ID,
        "backbone_identity": training.BACKBONE_IDENTITY,
        "selected_layer": training.BACKBONE_LAYER,
        "feature_indices": list(EXPECTED_FEATURE_INDICES),
        "dtype": DTYPE_NAME,
        "batching": {
            "batch_size": training.BATCH_SIZE,
            "batch_order": "split, class, filename, all lexicographic",
        },
        "aggregation_policy": AGGREGATION_POLICY,
        "aggregation_identifier": AGGREGATION_IDENTIFIER,
        "localization_policy": LOCALIZATION_POLICY,
        "localization_identifier": LOCALIZATION_IDENTIFIER,
        "prediction_judgement_policy": PREDICTION_JUDGEMENT_POLICY,
        "output_artifacts": first.output_artifact_hashes,
        "scope_boundaries": {
            "evaluation_executed": False,
            "metrics_generated": False,
            "threshold_derived": False,
            "operating_point_derived": False,
            "calibration_performed": False,
            "benchmark_generated": False,
            "onnx_exported": False,
            "fitting_performed": False,
            "scientific_claim": False,
            "product_claim": False,
        },
    }
    metadata_hashes["metadata/inference_metadata.json"] = write_json_record(
        INFERENCE_METADATA_DIR / "inference_metadata.json",
        inference_metadata,
    )
    return dict(sorted(metadata_hashes.items()))


def write_artifact_hashes_record(
    first: InferenceRunResult,
    metadata_hashes: Mapping[str, str],
    replay_hash: str,
) -> str:
    record = {
        "schema": INFERENCE_ARTIFACT_HASHES_SCHEMA,
        "inference_label": INFERENCE_LABEL,
        "local_output_artifacts": first.output_artifact_hashes,
        "metadata_artifacts": dict(sorted(metadata_hashes.items())),
        "replay_verification": {
            "path": "data/visa/derived/padim/inference/replay/replay_verification.json",
            "sha256": replay_hash,
        },
        "sample_artifacts": sample_artifact_hashes(first),
    }
    return write_json_record(INFERENCE_ARTIFACT_HASHES_PATH, record)


def write_replay_record(record: Mapping[str, Any]) -> str:
    return write_json_record(REPLAY_DIR / "replay_verification.json", record)


def write_evidence(
    artifacts: GovernedArtifacts,
    samples: Sequence[InferenceSample],
    first: InferenceRunResult,
    metadata_hashes: Mapping[str, str],
    replay_hash: str,
    artifact_hashes_record_hash: str,
) -> str:
    date = evidence_date_for_run()
    first_five_hashes = [
        {
            "input_id": record.input_id,
            "filename": record.filename,
            "anomaly_map_sha256": record.anomaly_map_sha256,
            "prediction_sha256": record.prediction_sha256,
        }
        for record in first.sample_records[:5]
    ]
    content = f"""# Kalibra Governed PaDiM Inference Evidence v1.0

**Status:** Recorded — deterministic offline governed PaDiM inference evidence only
**Date:** {date}
**Scope:** C-5 Governed PaDiM inference only

## Governed Dataset Identity

- Dataset: VisA governed proxy acquisition `visa-acq-v1`
- Archive SHA-256: `{artifacts.dataset_identity["archive_sha256"]}`
- Files manifest SHA-256: `{artifacts.dataset_identity["files_manifest_sha256"]}`
- Train split SHA-256 verified for identity: `{training.TRAIN_SPLIT_SHA256}`
- Validation split SHA-256 consumed for inference: `{training.VALIDATION_SPLIT_SHA256}`
- Test split SHA-256 consumed for inference: `{training.TEST_SPLIT_SHA256}`
- Provenance SHA-256: `{artifacts.dataset_identity["provenance_sha256"]}`

## Governed PaDiM Artifact Identity

- Training label: `{artifacts.training_record["training_label"]}`
- Training record SHA-256: `{artifacts.artifact_identity["training_record_sha256"]}`
- Training artifact hashes SHA-256: `{artifacts.artifact_identity["training_artifact_hashes_sha256"]}`
- Training metadata SHA-256: `{artifacts.artifact_identity["training_metadata_sha256"]}`
- Training replay SHA-256: `{artifacts.artifact_identity["training_replay_verification_sha256"]}`
- Mu artifact SHA-256: `{artifacts.artifact_identity["mu_by_class_sha256"]}`
- Covariance inverse artifact SHA-256: `{artifacts.artifact_identity["covariance_inverse_by_class_sha256"]}`
- Feature indices artifact SHA-256: `{artifacts.artifact_identity["feature_indices_sha256"]}`

## Deterministic Feature Extraction

- Backbone identity: `{training.BACKBONE_IDENTITY}`
- Backbone layer: `{training.BACKBONE_LAYER}`
- Preprocessing contract id: `{training.PREPROCESSING_CONTRACT_ID}`
- Feature indices: `{list(EXPECTED_FEATURE_INDICES)}`
- Dtype: `{DTYPE_NAME}`
- Batch size: `{training.BATCH_SIZE}`

## Inference Surface

- Consumed splits: `{list(INFERENCE_SPLITS)}`
- Inference image count: `{len(samples)}`
- Split counts: `{split_counts(samples)}`
- Aggregation policy: `{AGGREGATION_POLICY}`
- Aggregation identifier: `{AGGREGATION_IDENTIFIER}`
- Localization policy: `{LOCALIZATION_POLICY}`
- Localization identifier: `{LOCALIZATION_IDENTIFIER}`
- Prediction surface: `InspectionPrediction`
- Raw measure field: `predicted_raw_anomaly_measure`
- Raw measure kind: `raw_anomaly_measure`
- Raw measure scale: `model_raw_anomaly_measure`

## Replay Verification

- Complete second inference run executed: `true`
- Identical feature tensors: `true`
- Identical anomaly maps: `true`
- Identical raw anomaly measures: `true`
- Identical localization: `true`
- Identical InspectionPrediction records: `true`
- Identical hashes: `true`
- Replay record: `data/visa/derived/padim/inference/replay/replay_verification.json`
- Replay record SHA-256: `{replay_hash}`

## Governed Inference Records

- Inference artifact hashes SHA-256: `{artifact_hashes_record_hash}`
- Metadata artifact hashes: `{dict(sorted(metadata_hashes.items()))}`
- Local output artifact hashes: `{first.output_artifact_hashes}`
- First five per-input inference hashes: `{first_five_hashes}`

## Explicit Non-Claims

- No evaluation was executed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, metric, or benchmark was generated.
- No threshold or operating point was derived.
- No thresholded OK/defect classification was derived; the existing `InspectionPrediction` contract requires `predicted_judgement` when raw localization is present, so C-5 records `{PREDICTION_JUDGEMENT_POLICY}` only as a contract policy, not as a scientific or product classification.
- No calibration was performed.
- No ONNX export was produced.
- No fitting, retraining, artifact mutation, or preprocessing change was performed.
- No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration, prototype UI, provider interface, output mapping, or architecture code was modified.
- The raw anomaly measure is not a probability, not confidence, and not trust.
- This inference record makes no scientific claim and does not state that Kalibra detects defects.
"""
    return write_governed_bytes(EVIDENCE_PATH, content.encode("utf-8"))


def run_inference() -> None:
    ensure_layout()
    config = training.FitConfig()
    governed = training.verify_governed_acquisition()
    file_hashes = governed["file_hashes"]
    if not isinstance(file_hashes, Mapping):
        raise InferenceError("invalid governed file hash map")
    artifacts = load_governed_artifacts(governed, config)
    samples = load_inference_samples(file_hashes, artifacts.class_names)
    inference_timestamp = inference_timestamp_for_run()
    first = execute_inference_run(samples, artifacts, config, persist_outputs=True)
    second = execute_inference_run(samples, artifacts, config, persist_outputs=False)
    comparisons = compare_inference_runs(first, second)
    replay = build_replay_record(first, second, comparisons)
    replay_hash = write_replay_record(replay)
    metadata_hashes = write_metadata_records(
        artifacts,
        samples,
        first,
        inference_timestamp,
    )
    artifact_hashes_record_hash = write_artifact_hashes_record(
        first,
        metadata_hashes,
        replay_hash,
    )
    write_evidence(
        artifacts,
        samples,
        first,
        metadata_hashes,
        replay_hash,
        artifact_hashes_record_hash,
    )


def verify_inference() -> None:
    config = training.FitConfig()
    governed = training.verify_governed_acquisition()
    file_hashes = governed["file_hashes"]
    if not isinstance(file_hashes, Mapping):
        raise InferenceError("invalid governed file hash map")
    artifacts = load_governed_artifacts(governed, config)
    samples = load_inference_samples(file_hashes, artifacts.class_names)
    first = execute_inference_run(samples, artifacts, config, persist_outputs=False)
    second = execute_inference_run(samples, artifacts, config, persist_outputs=False)
    comparisons = compare_inference_runs(first, second)
    if not all(comparisons.values()):
        raise InferenceError("inference replay verification did not pass")
    verify_existing_inference_records(first)


def verify_existing_inference_records(first: InferenceRunResult) -> None:
    artifact_hashes = read_json_mapping(INFERENCE_ARTIFACT_HASHES_PATH)
    if artifact_hashes.get("schema") != INFERENCE_ARTIFACT_HASHES_SCHEMA:
        raise InferenceError("unexpected inference artifact hash schema")
    expected_outputs = artifact_hashes.get("local_output_artifacts")
    if expected_outputs != first.output_artifact_hashes:
        raise InferenceError("recorded local output hashes do not match regenerated inference")
    for relative_path, expected_digest in first.output_artifact_hashes.items():
        verify_file_hash(INFERENCE_DIR / relative_path, expected_digest, relative_path)
    if artifact_hashes.get("sample_artifacts") != sample_artifact_hashes(first):
        raise InferenceError("recorded per-sample inference hashes do not match regenerated inference")
    metadata_artifacts = artifact_hashes.get("metadata_artifacts")
    if not isinstance(metadata_artifacts, Mapping):
        raise InferenceError("inference artifact hash record lacks metadata artifacts")
    for relative_path, expected_digest in metadata_artifacts.items():
        if not isinstance(relative_path, str) or not isinstance(expected_digest, str):
            raise InferenceError("invalid inference metadata hash entry")
        verify_file_hash(INFERENCE_DIR / relative_path, expected_digest, relative_path)
    replay = artifact_hashes.get("replay_verification")
    if not isinstance(replay, Mapping):
        raise InferenceError("inference artifact hash record lacks replay verification")
    replay_path = REPO_ROOT / str(replay.get("path"))
    replay_sha = replay.get("sha256")
    if not isinstance(replay_sha, str):
        raise InferenceError("inference replay hash is missing")
    verify_file_hash(replay_path, replay_sha, "inference replay verification")
    replay_record = read_json_mapping(replay_path)
    if replay_record.get("status") != "passed":
        raise InferenceError("inference replay record is not passed")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="C-5 governed PaDiM inference")
    parser.add_argument("command", choices=("infer", "verify"))
    args = parser.parse_args(argv)
    try:
        if args.command == "infer":
            run_inference()
        elif args.command == "verify":
            verify_inference()
    except (InferenceError, training.TrainingError, acquisition.AcquisitionError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
