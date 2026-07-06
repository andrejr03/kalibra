#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter, defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import governed_visa_acquisition as acquisition  # noqa: E402
import padim_inference as inference  # noqa: E402
import train_padim_baseline as training  # noqa: E402


PADIM_ROOT = training.PADIM_ROOT
EVALUATION_DIR = PADIM_ROOT / "evaluation"
EVALUATION_METADATA_DIR = EVALUATION_DIR / "metadata"
EVALUATION_METRICS_DIR = EVALUATION_DIR / "metrics"
EVALUATION_PER_CLASS_DIR = EVALUATION_DIR / "per_class"
EVALUATION_FAILURE_DIR = EVALUATION_DIR / "failure_analysis"
EVALUATION_OPERATING_POINT_DIR = EVALUATION_DIR / "operating_point"
EVALUATION_REPLAY_DIR = EVALUATION_DIR / "replay"
EVALUATION_ARTIFACT_HASHES_PATH = EVALUATION_DIR / "artifact_hashes.json"
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md"
)

EVALUATION_LABEL = "visa-padim-scientific-evaluation-v1"
EVALUATION_METADATA_SCHEMA = "kalibra_scientific_evaluation_metadata_v1"
EVALUATION_METRICS_SCHEMA = "kalibra_scientific_evaluation_metrics_v1"
EVALUATION_FAILURE_SCHEMA = "kalibra_scientific_evaluation_failure_analysis_v1"
EVALUATION_OPERATING_POINT_SCHEMA = "kalibra_scientific_evaluation_operating_point_v1"
EVALUATION_REPLAY_SCHEMA = "kalibra_scientific_evaluation_replay_v1"
EVALUATION_ARTIFACT_HASHES_SCHEMA = "kalibra_scientific_evaluation_artifact_hashes_v1"

EVALUATION_SPLITS = ("validation", "test")
ANOMALY_LABEL = "anomaly"
NORMAL_LABEL = "normal"
MASK_SIZE = training.IMAGE_SIZE
AUPRO_MAX_FPR = 0.30
BOUNDARY_CASES_PER_CLASS = 10
OPERATING_POINT_RULE_ID = "validation_balanced_fpr_fnr_v1"
LOCALIZATION_FAILURE_RULE_ID = "tp_predicted_box_zero_mask_overlap_v1"
BOUNDARY_CASE_RULE_ID = "closest_absolute_raw_measure_margin_per_class_v1"


class EvaluationError(RuntimeError):
    """Raised when C-6 scientific evaluation cannot proceed safely."""


@dataclass(frozen=True)
class EvaluationSample:
    split: str
    input_id: str
    filename: str
    class_name: str
    label: str
    sample_sha256: str
    mask_filename: str | None
    mask_sha256: str | None


@dataclass(frozen=True)
class EvaluationObservation:
    sample: EvaluationSample
    score: float
    localization: dict[str, Any]
    prediction_record: dict[str, Any]
    anomaly_map: np.ndarray


@dataclass(frozen=True)
class GovernedInputIdentity:
    dataset_identity: dict[str, Any]
    training_identity: dict[str, Any]
    inference_identity: dict[str, Any]
    training_artifact_hashes: dict[str, Any]
    inference_artifact_hashes: dict[str, Any]
    class_order: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationComputation:
    records: dict[str, bytes]
    evidence_content: bytes
    official_metrics: dict[str, Any]
    diagnostic_metrics: dict[str, Any]
    operating_point: dict[str, Any]
    failure_analysis: dict[str, Any]
    per_class: dict[str, Any]
    metadata: dict[str, Any]


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


def npy_bytes(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, array, allow_pickle=False)
    return buffer.getvalue()


def npy_sha256(array: np.ndarray) -> str:
    return sha256_bytes(npy_bytes(array))


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise EvaluationError(f"missing governed record: {path}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"governed record is not a JSON object: {path}")
    return value


def ensure_layout() -> None:
    for directory in (
        EVALUATION_METADATA_DIR,
        EVALUATION_METRICS_DIR,
        EVALUATION_PER_CLASS_DIR,
        EVALUATION_FAILURE_DIR,
        EVALUATION_OPERATING_POINT_DIR,
        EVALUATION_REPLAY_DIR,
        EVIDENCE_PATH.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def write_governed_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise EvaluationError(f"governed evaluation record changed: {path}")
        return acquisition.sha256_file(path)
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def verify_file_hash(path: Path, expected: str, label: str) -> str:
    if not path.exists():
        raise EvaluationError(f"missing governed artifact for {label}: {path}")
    actual = acquisition.sha256_file(path)
    if actual != expected:
        raise EvaluationError(
            f"governed artifact hash mismatch for {label}: expected {expected}, got {actual}"
        )
    return actual


def verify_record_hash(path: Path, expected_digest: str | None = None) -> str:
    hash_path = path.with_name(path.name + ".sha256")
    if not hash_path.exists():
        raise EvaluationError(f"missing hash record: {hash_path}")
    entries = acquisition.parse_sha256_manifest(hash_path)
    digest = entries.get(path.name)
    if digest is None:
        raise EvaluationError(f"hash record does not reference {path.name}")
    actual = acquisition.sha256_file(path)
    if digest != actual:
        raise EvaluationError(f"hash mismatch for {path}: expected {digest}, got {actual}")
    if expected_digest is not None and digest != expected_digest:
        raise EvaluationError(
            f"unexpected governed hash for {path}: expected {expected_digest}, got {digest}"
        )
    return digest


def verify_governed_acquisition_inputs() -> dict[str, Any]:
    governed = training.verify_governed_acquisition()
    verify_record_hash(training.MANIFESTS_DIR / "archive_metadata.json")
    verify_record_hash(training.PROVENANCE_DIR / "ATTRIBUTION.md")
    for upstream_name in acquisition.UPSTREAM_SPLIT_CSVS:
        verify_record_hash(training.SPLITS_DIR / f"upstream_{upstream_name}.csv")
    return governed


def verify_training_identity(governed: Mapping[str, Any]) -> dict[str, Any]:
    artifact_hashes_path = training.TRAINING_DIR / "artifact_hashes.json"
    training_artifact_hashes = read_json_mapping(artifact_hashes_path)
    if training_artifact_hashes.get("schema") != "kalibra_padim_training_artifact_hashes_v1":
        raise EvaluationError("unexpected C-4 training artifact hash schema")
    inference.verify_recorded_training_artifacts(training_artifact_hashes)

    training_record_path = training.TRAINING_DIR / "training_record.json"
    training_record = read_json_mapping(training_record_path)
    training_record_sha256 = acquisition.sha256_file(training_record_path)
    artifact_hashes_sha256 = acquisition.sha256_file(artifact_hashes_path)
    if training_record.get("artifact_hashes_record_sha256") != artifact_hashes_sha256:
        raise EvaluationError("training record does not match C-4 artifact hashes identity")

    training_metadata_path = training.METADATA_DIR / "training_metadata.json"
    training_metadata_sha256 = verify_file_hash(
        training_metadata_path,
        str(training_record.get("training_metadata_sha256")),
        "training metadata",
    )
    training_metadata = read_json_mapping(training_metadata_path)
    scope = training_metadata.get("scope_boundaries")
    if not isinstance(scope, Mapping):
        raise EvaluationError("training metadata lacks scope boundaries")
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
            raise EvaluationError(f"C-4 training scope boundary is not closed: {key}")

    replay_info = training_artifact_hashes.get("replay_verification")
    if not isinstance(replay_info, Mapping):
        raise EvaluationError("training artifact hashes lack replay verification")
    replay_path = REPO_ROOT / str(replay_info.get("path", ""))
    replay_sha256 = replay_info.get("sha256")
    if not isinstance(replay_sha256, str):
        raise EvaluationError("training replay hash is missing")
    verify_file_hash(replay_path, replay_sha256, "training replay verification")
    training_replay = read_json_mapping(replay_path)
    if training_replay.get("status") != "passed":
        raise EvaluationError("C-4 replay verification is not passed")
    if training_record.get("replay_verification_sha256") != replay_sha256:
        raise EvaluationError("training replay hash does not match training record")

    dataset_identity = read_hashed_training_metadata("metadata/dataset_identity.json", training_artifact_hashes)
    if dataset_identity != training.dataset_identity(governed):
        raise EvaluationError("C-4 dataset identity does not match governed acquisition")
    feature_indices = read_hashed_training_metadata("metadata/feature_indices.json", training_artifact_hashes)

    class_order = training_record.get("class_order")
    if not isinstance(class_order, list) or not all(isinstance(item, str) for item in class_order):
        raise EvaluationError("training record lacks class order")
    if feature_indices.get("selected_indices") != list(inference.EXPECTED_FEATURE_INDICES):
        raise EvaluationError("training feature indices do not match governed C-5 expectation")

    return {
        "training_label": training_record["training_label"],
        "training_record_sha256": training_record_sha256,
        "training_artifact_hashes_sha256": artifact_hashes_sha256,
        "training_metadata_sha256": training_metadata_sha256,
        "training_replay_verification_sha256": replay_sha256,
        "mu_by_class_sha256": training_artifact_hashes["array_artifacts"][
            "statistics/mu_by_class.npy"
        ],
        "covariance_inverse_by_class_sha256": training_artifact_hashes[
            "array_artifacts"
        ]["covariance/covariance_inverse_by_class.npy"],
        "feature_indices_sha256": training_artifact_hashes["array_artifacts"][
            "statistics/feature_indices.npy"
        ],
        "feature_indices": feature_indices.get("selected_indices"),
        "deterministic_seed": training_record.get("deterministic_seed", training.FEATURE_SUBSAMPLE_SEED),
        "class_order": class_order,
        "artifact_hashes": training_artifact_hashes,
    }


def read_hashed_training_metadata(
    relative_path: str,
    training_artifact_hashes: Mapping[str, Any],
) -> dict[str, Any]:
    metadata_artifacts = training_artifact_hashes.get("metadata_artifacts")
    if not isinstance(metadata_artifacts, Mapping):
        raise EvaluationError("training artifact hashes lack metadata artifacts")
    expected = metadata_artifacts.get(relative_path)
    if not isinstance(expected, str):
        raise EvaluationError(f"training metadata hash missing for {relative_path}")
    path = PADIM_ROOT / relative_path
    verify_file_hash(path, expected, relative_path)
    return read_json_mapping(path)


def verify_inference_identity(
    dataset_identity: Mapping[str, Any],
    training_identity: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_hashes = read_json_mapping(inference.INFERENCE_ARTIFACT_HASHES_PATH)
    if artifact_hashes.get("schema") != inference.INFERENCE_ARTIFACT_HASHES_SCHEMA:
        raise EvaluationError("unexpected C-5 inference artifact hash schema")

    local_outputs = artifact_hashes.get("local_output_artifacts")
    if not isinstance(local_outputs, Mapping):
        raise EvaluationError("inference artifact hashes lack local output artifacts")
    for relative_path, expected in local_outputs.items():
        if not isinstance(relative_path, str) or not isinstance(expected, str):
            raise EvaluationError("invalid inference local output hash entry")
        verify_file_hash(inference.INFERENCE_DIR / relative_path, expected, relative_path)

    metadata_artifacts = artifact_hashes.get("metadata_artifacts")
    if not isinstance(metadata_artifacts, Mapping):
        raise EvaluationError("inference artifact hashes lack metadata artifacts")
    for relative_path, expected in metadata_artifacts.items():
        if not isinstance(relative_path, str) or not isinstance(expected, str):
            raise EvaluationError("invalid inference metadata hash entry")
        verify_file_hash(inference.INFERENCE_DIR / relative_path, expected, relative_path)

    replay = artifact_hashes.get("replay_verification")
    if not isinstance(replay, Mapping):
        raise EvaluationError("inference artifact hashes lack replay verification")
    replay_path = REPO_ROOT / str(replay.get("path", ""))
    replay_sha256 = replay.get("sha256")
    if not isinstance(replay_sha256, str):
        raise EvaluationError("inference replay hash is missing")
    verify_file_hash(replay_path, replay_sha256, "inference replay verification")
    replay_record = read_json_mapping(replay_path)
    if replay_record.get("status") != "passed":
        raise EvaluationError("C-5 inference replay record is not passed")
    comparisons = replay_record.get("comparisons")
    if not isinstance(comparisons, Mapping) or not all(comparisons.values()):
        raise EvaluationError("C-5 inference replay comparisons are not all true")

    inference_metadata = read_json_mapping(inference.INFERENCE_METADATA_DIR / "inference_metadata.json")
    scope = inference_metadata.get("scope_boundaries")
    if not isinstance(scope, Mapping):
        raise EvaluationError("inference metadata lacks scope boundaries")
    for key in (
        "evaluation_executed",
        "metrics_generated",
        "threshold_derived",
        "operating_point_derived",
        "calibration_performed",
        "benchmark_generated",
        "onnx_exported",
        "fitting_performed",
        "scientific_claim",
        "product_claim",
    ):
        if scope.get(key) is not False:
            raise EvaluationError(f"C-5 inference scope boundary is not closed: {key}")

    if inference_metadata.get("dataset_identity") != dict(dataset_identity):
        raise EvaluationError("C-5 inference dataset identity does not match C-3/C-4")
    artifact_identity = inference_metadata.get("artifact_identity")
    if not isinstance(artifact_identity, Mapping):
        raise EvaluationError("C-5 inference metadata lacks artifact identity")
    expected_training_keys = {
        "training_label": "training_label",
        "training_record_sha256": "training_record_sha256",
        "training_artifact_hashes_sha256": "training_artifact_hashes_sha256",
        "training_metadata_sha256": "training_metadata_sha256",
        "training_replay_verification_sha256": "training_replay_verification_sha256",
        "mu_by_class_sha256": "mu_by_class_sha256",
        "covariance_inverse_by_class_sha256": "covariance_inverse_by_class_sha256",
        "feature_indices_sha256": "feature_indices_sha256",
    }
    for inference_key, training_key in expected_training_keys.items():
        if artifact_identity.get(inference_key) != training_identity[training_key]:
            raise EvaluationError(f"C-5 inference artifact identity mismatch: {inference_key}")
    if artifact_identity.get("class_order") != list(training_identity["class_order"]):
        raise EvaluationError("C-5 inference class order does not match C-4")
    if inference_metadata.get("prediction_judgement_policy") != inference.PREDICTION_JUDGEMENT_POLICY:
        raise EvaluationError("unexpected C-5 prediction judgement policy")

    return {
        "inference_label": inference_metadata["inference_label"],
        "inference_artifact_hashes_sha256": acquisition.sha256_file(
            inference.INFERENCE_ARTIFACT_HASHES_PATH
        ),
        "inference_replay_verification_sha256": replay_sha256,
        "local_output_artifacts": dict(sorted(local_outputs.items())),
        "metadata_artifacts": dict(sorted(metadata_artifacts.items())),
        "sample_artifacts": artifact_hashes.get("sample_artifacts"),
        "inference_metadata_sha256": metadata_artifacts["metadata/inference_metadata.json"],
        "aggregation_identifier": inference_metadata["aggregation_identifier"],
        "localization_identifier": inference_metadata["localization_identifier"],
        "prediction_judgement_policy": inference_metadata["prediction_judgement_policy"],
        "artifact_hashes": artifact_hashes,
    }


def load_governed_identities(governed: Mapping[str, Any]) -> GovernedInputIdentity:
    training_identity = verify_training_identity(governed)
    dataset_identity = training.dataset_identity(governed)
    inference_identity = verify_inference_identity(dataset_identity, training_identity)
    class_order = tuple(training_identity["class_order"])
    return GovernedInputIdentity(
        dataset_identity=dataset_identity,
        training_identity={key: value for key, value in training_identity.items() if key != "artifact_hashes"},
        inference_identity={key: value for key, value in inference_identity.items() if key != "artifact_hashes"},
        training_artifact_hashes=training_identity["artifact_hashes"],
        inference_artifact_hashes=inference_identity["artifact_hashes"],
        class_order=class_order,
    )


def load_split_samples(
    split: str,
    file_hashes: Mapping[str, str],
    class_order: Sequence[str],
) -> list[EvaluationSample]:
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
    image_rows: list[dict[str, str]] = []
    mask_rows: dict[str, dict[str, str]] = {}
    seen_images: set[str] = set()
    class_set = set(class_order)
    with split_path.open(newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != expected_header:
            raise EvaluationError(f"unexpected {split} manifest header: {reader.fieldnames}")
        for row in reader:
            artifact_type = row["artifact_type"]
            filename = row["filename"]
            if row["class"] not in class_set:
                raise EvaluationError(f"{split} row class lacks governed PaDiM artifact: {row['class']}")
            if filename not in file_hashes:
                raise EvaluationError(f"{split} artifact missing from files.sha256: {filename}")
            if file_hashes[filename] != row["sha256"]:
                raise EvaluationError(f"{split} artifact hash mismatch: {filename}")
            artifact_path = training.EXTRACTED_DIR / filename
            if not artifact_path.exists():
                raise EvaluationError(f"{split} governed artifact missing: {filename}")
            if artifact_type == "image":
                if filename in seen_images:
                    raise EvaluationError(f"duplicate image row in {split}: {filename}")
                seen_images.add(filename)
                if row["source_image"] != filename:
                    raise EvaluationError(f"{split} image source_image mismatch: {filename}")
                if row["label"] not in (NORMAL_LABEL, ANOMALY_LABEL):
                    raise EvaluationError(f"{split} image has unsupported label: {filename}")
                image_rows.append(dict(row))
            elif artifact_type == "mask":
                source_image = row["source_image"]
                if not source_image:
                    raise EvaluationError(f"{split} mask row lacks source image: {filename}")
                if row["label"] != ANOMALY_LABEL:
                    raise EvaluationError(f"{split} mask row is not anomaly-labelled: {filename}")
                if row["source_mask"] != filename:
                    raise EvaluationError(f"{split} mask source_mask mismatch: {filename}")
                if source_image in mask_rows:
                    raise EvaluationError(f"duplicate mask row for image in {split}: {source_image}")
                mask_rows[source_image] = dict(row)
            else:
                raise EvaluationError(f"unexpected artifact type in {split}: {artifact_type}")

    samples: list[EvaluationSample] = []
    for row in image_rows:
        mask_row = mask_rows.get(row["filename"])
        if row["label"] == ANOMALY_LABEL:
            if row["source_mask"] == "":
                raise EvaluationError(f"anomaly image lacks source mask: {row['filename']}")
            if mask_row is None:
                raise EvaluationError(f"anomaly image lacks governed mask row: {row['filename']}")
            mask_filename = mask_row["filename"]
            mask_sha256 = mask_row["sha256"]
        else:
            if row["source_mask"] != "":
                raise EvaluationError(f"normal image unexpectedly references mask: {row['filename']}")
            mask_filename = None
            mask_sha256 = None
        samples.append(
            EvaluationSample(
                split=split,
                input_id=inference.stable_id(
                    "visa-inference-input",
                    {
                        "split": split,
                        "filename": row["filename"],
                        "sha256": row["sha256"],
                    },
                ),
                filename=row["filename"],
                class_name=row["class"],
                label=row["label"],
                sample_sha256=row["sha256"],
                mask_filename=mask_filename,
                mask_sha256=mask_sha256,
            )
        )

    return sorted(samples, key=lambda sample: (sample.split, sample.class_name, sample.filename))


def load_prediction_records(
    split: str,
    samples: Sequence[EvaluationSample],
    sample_artifacts: Mapping[str, Any],
) -> list[dict[str, Any]]:
    prediction_path = inference.PREDICTIONS_DIR / f"{split}_predictions.jsonl"
    records: list[dict[str, Any]] = []
    with prediction_path.open() as file:
        for line_number, line in enumerate(file, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvaluationError(
                    f"invalid prediction JSON at {prediction_path}:{line_number}"
                ) from exc
            if not isinstance(record, dict):
                raise EvaluationError(f"prediction record is not an object: {prediction_path}:{line_number}")
            records.append(record)
    if len(records) != len(samples):
        raise EvaluationError(
            f"{split} prediction count mismatch: expected {len(samples)}, got {len(records)}"
        )
    for sample, record in zip(samples, records):
        validate_prediction_record(split, sample, record, sample_artifacts)
    return records


def validate_prediction_record(
    split: str,
    sample: EvaluationSample,
    record: Mapping[str, Any],
    sample_artifacts: Mapping[str, Any],
) -> None:
    if record.get("schema") != inference.PREDICTION_RECORD_SCHEMA:
        raise EvaluationError(f"unexpected prediction schema for {sample.filename}")
    if record.get("input_id") != sample.input_id:
        raise EvaluationError(f"{split} prediction input_id mismatch for {sample.filename}")
    if record.get("raw_measure_kind") != "raw_anomaly_measure":
        raise EvaluationError(f"{split} prediction raw measure kind mismatch: {sample.filename}")
    if record.get("raw_measure_scale") != "model_raw_anomaly_measure":
        raise EvaluationError(f"{split} prediction raw measure scale mismatch: {sample.filename}")
    score = record.get("predicted_raw_anomaly_measure")
    if not isinstance(score, (int, float)) or not math.isfinite(float(score)):
        raise EvaluationError(f"{split} prediction raw measure is not finite: {sample.filename}")
    metadata = record.get("model_metadata")
    if not isinstance(metadata, Mapping):
        raise EvaluationError(f"{split} prediction lacks model metadata: {sample.filename}")
    expected_metadata = {
        "split": split,
        "sample_filename": sample.filename,
        "sample_sha256": sample.sample_sha256,
        "class_name": sample.class_name,
        "split_sha256": training.VALIDATION_SPLIT_SHA256
        if split == "validation"
        else training.TEST_SPLIT_SHA256,
        "prediction_judgement_policy": inference.PREDICTION_JUDGEMENT_POLICY,
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            raise EvaluationError(f"{split} prediction metadata mismatch for {sample.filename}: {key}")
    artifact_record = sample_artifacts.get(sample.input_id)
    if not isinstance(artifact_record, Mapping):
        raise EvaluationError(f"missing C-5 sample artifact hash: {sample.input_id}")
    prediction_sha256 = sha256_bytes(canonical_json_bytes(record))
    if artifact_record.get("prediction_sha256") != prediction_sha256:
        raise EvaluationError(f"C-5 prediction hash mismatch for {sample.filename}")
    if artifact_record.get("filename") != sample.filename:
        raise EvaluationError(f"C-5 sample artifact filename mismatch for {sample.input_id}")


def load_anomaly_maps(
    split: str,
    samples: Sequence[EvaluationSample],
    sample_artifacts: Mapping[str, Any],
) -> np.ndarray:
    path = inference.ANOMALY_MAPS_DIR / f"{split}_anomaly_maps.npy"
    maps = np.load(path, allow_pickle=False)
    expected_shape = (len(samples), MASK_SIZE, MASK_SIZE)
    if maps.shape != expected_shape:
        raise EvaluationError(f"{split} anomaly map shape mismatch: expected {expected_shape}, got {maps.shape}")
    if maps.dtype != np.float64:
        raise EvaluationError(f"{split} anomaly maps must remain float64")
    if not np.all(np.isfinite(maps)):
        raise EvaluationError(f"{split} anomaly maps contain non-finite values")
    for index, sample in enumerate(samples):
        artifact_record = sample_artifacts.get(sample.input_id)
        if not isinstance(artifact_record, Mapping):
            raise EvaluationError(f"missing C-5 sample artifact hash: {sample.input_id}")
        expected = artifact_record.get("anomaly_map_sha256")
        actual = npy_sha256(np.ascontiguousarray(maps[index], dtype=np.float64))
        if expected != actual:
            raise EvaluationError(f"C-5 anomaly-map hash mismatch for {sample.filename}")
    return np.ascontiguousarray(maps, dtype=np.float64)


def load_observations(
    split: str,
    samples: Sequence[EvaluationSample],
    identity: GovernedInputIdentity,
) -> list[EvaluationObservation]:
    sample_artifacts = identity.inference_artifact_hashes.get("sample_artifacts")
    if not isinstance(sample_artifacts, Mapping):
        raise EvaluationError("C-5 inference artifact hashes lack sample artifacts")
    predictions = load_prediction_records(split, samples, sample_artifacts)
    maps = load_anomaly_maps(split, samples, sample_artifacts)
    observations: list[EvaluationObservation] = []
    for index, (sample, prediction) in enumerate(zip(samples, predictions)):
        localization = prediction.get("predicted_localization")
        if not isinstance(localization, Mapping):
            raise EvaluationError(f"prediction lacks governed localization: {sample.filename}")
        observations.append(
            EvaluationObservation(
                sample=sample,
                score=float(prediction["predicted_raw_anomaly_measure"]),
                localization=dict(localization),
                prediction_record=prediction,
                anomaly_map=np.ascontiguousarray(maps[index], dtype=np.float64),
            )
        )
    return observations


def binary_auroc(labels: Sequence[int] | np.ndarray, scores: Sequence[float] | np.ndarray) -> float:
    label_array = np.asarray(labels, dtype=np.int8)
    score_array = np.asarray(scores, dtype=np.float64)
    if label_array.shape != score_array.shape:
        raise EvaluationError("AUROC labels and scores have different shapes")
    positives = int(np.sum(label_array == 1))
    negatives = int(np.sum(label_array == 0))
    if positives == 0 or negatives == 0:
        raise EvaluationError("AUROC requires both positive and negative labels")
    order = np.argsort(score_array, kind="mergesort")
    sorted_scores = score_array[order]
    ranks = np.empty(score_array.shape[0], dtype=np.float64)
    start = 0
    while start < sorted_scores.shape[0]:
        end = start + 1
        while end < sorted_scores.shape[0] and sorted_scores[end] == sorted_scores[start]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        ranks[order[start:end]] = average_rank
        start = end
    positive_rank_sum = float(np.sum(ranks[label_array == 1]))
    auc = (
        positive_rank_sum - (positives * (positives + 1) / 2.0)
    ) / float(positives * negatives)
    return float(auc)


def confusion_at_threshold(
    labels: Sequence[str],
    scores: Sequence[float],
    threshold: float,
) -> dict[str, int]:
    counts = {"true_positive": 0, "false_positive": 0, "true_negative": 0, "false_negative": 0}
    for label, score in zip(labels, scores):
        predicted_anomaly = score >= threshold
        actual_anomaly = label == ANOMALY_LABEL
        if predicted_anomaly and actual_anomaly:
            counts["true_positive"] += 1
        elif predicted_anomaly and not actual_anomaly:
            counts["false_positive"] += 1
        elif not predicted_anomaly and actual_anomaly:
            counts["false_negative"] += 1
        else:
            counts["true_negative"] += 1
    return counts


def rates_from_confusion(confusion: Mapping[str, int]) -> dict[str, float]:
    fp = int(confusion["false_positive"])
    fn = int(confusion["false_negative"])
    tp = int(confusion["true_positive"])
    tn = int(confusion["true_negative"])
    negatives = fp + tn
    positives = tp + fn
    return {
        "false_positive_rate": fp / negatives if negatives else 0.0,
        "false_negative_rate": fn / positives if positives else 0.0,
        "true_positive_rate": tp / positives if positives else 0.0,
        "true_negative_rate": tn / negatives if negatives else 0.0,
    }


def diagnostic_metrics_from_confusion(confusion: Mapping[str, int]) -> dict[str, float]:
    tp = int(confusion["true_positive"])
    fp = int(confusion["false_positive"])
    fn = int(confusion["false_negative"])
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def derive_operating_point(validation: Sequence[EvaluationObservation]) -> dict[str, Any]:
    labels = [observation.sample.label for observation in validation]
    scores = [observation.score for observation in validation]
    candidates = sorted(set(scores), reverse=True)
    if not candidates:
        raise EvaluationError("cannot derive operating point from empty validation split")
    best: dict[str, Any] | None = None
    for threshold in candidates:
        confusion = confusion_at_threshold(labels, scores, threshold)
        rates = rates_from_confusion(confusion)
        total_errors = confusion["false_positive"] + confusion["false_negative"]
        selection_key = (
            abs(rates["false_positive_rate"] - rates["false_negative_rate"]),
            max(rates["false_positive_rate"], rates["false_negative_rate"]),
            total_errors,
            -threshold,
        )
        candidate = {
            "threshold": float(threshold),
            "confusion": confusion,
            "rates": rates,
            "selection_key": list(selection_key),
        }
        if best is None or selection_key < tuple(best["selection_key"]):
            best = candidate
    if best is None:
        raise EvaluationError("operating point derivation failed")
    return {
        "schema": EVALUATION_OPERATING_POINT_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "rule_id": OPERATING_POINT_RULE_ID,
        "derivation_split": "validation",
        "application_split": "test",
        "threshold_field": "predicted_raw_anomaly_measure",
        "prediction_rule": "anomaly if predicted_raw_anomaly_measure >= threshold",
        "selection_rule": (
            "Minimize absolute validation false-positive-rate / false-negative-rate "
            "gap; tie-break by lower maximum error rate, lower total error count, "
            "then higher threshold."
        ),
        "validation_derived_value": best["threshold"],
        "validation_confusion": best["confusion"],
        "validation_rates": best["rates"],
        "candidate_count": len(candidates),
        "diagnostic_only": True,
        "not_calibrated": True,
        "not_product_threshold": True,
    }


def label_int(label: str) -> int:
    if label == ANOMALY_LABEL:
        return 1
    if label == NORMAL_LABEL:
        return 0
    raise EvaluationError(f"unsupported label: {label}")


def load_mask(sample: EvaluationSample) -> np.ndarray:
    if sample.label == NORMAL_LABEL:
        return np.zeros((MASK_SIZE, MASK_SIZE), dtype=bool)
    if sample.mask_filename is None or sample.mask_sha256 is None:
        raise EvaluationError(f"anomaly sample lacks mask identity: {sample.filename}")
    path = training.EXTRACTED_DIR / sample.mask_filename
    verify_file_hash(path, sample.mask_sha256, f"mask {sample.mask_filename}")
    with Image.open(path) as image:
        mask = downsample_binary_mask(np.asarray(image.convert("L"), dtype=np.uint8) > 0)
    if not np.any(mask):
        raise EvaluationError(f"anomaly mask is empty after deterministic downsampling: {sample.mask_filename}")
    return np.ascontiguousarray(mask, dtype=bool)


def downsample_binary_mask(mask: np.ndarray) -> np.ndarray:
    if mask.ndim != 2:
        raise EvaluationError(f"expected 2D mask, got shape {mask.shape}")
    source_height, source_width = mask.shape
    if source_height == 0 or source_width == 0:
        raise EvaluationError("cannot downsample empty mask")
    reduced = np.zeros((MASK_SIZE, MASK_SIZE), dtype=bool)
    for row in range(MASK_SIZE):
        y0 = int(math.floor(row * source_height / MASK_SIZE))
        y1 = int(math.ceil((row + 1) * source_height / MASK_SIZE))
        for col in range(MASK_SIZE):
            x0 = int(math.floor(col * source_width / MASK_SIZE))
            x1 = int(math.ceil((col + 1) * source_width / MASK_SIZE))
            reduced[row, col] = bool(np.any(mask[y0:y1, x0:x1]))
    return reduced


def connected_components(mask: np.ndarray) -> list[np.ndarray]:
    if mask.shape != (MASK_SIZE, MASK_SIZE):
        raise EvaluationError(f"unexpected mask shape for connected components: {mask.shape}")
    visited = np.zeros(mask.shape, dtype=bool)
    components: list[np.ndarray] = []
    for row in range(mask.shape[0]):
        for col in range(mask.shape[1]):
            if not mask[row, col] or visited[row, col]:
                continue
            pixels: list[tuple[int, int]] = []
            queue: deque[tuple[int, int]] = deque([(row, col)])
            visited[row, col] = True
            while queue:
                current_row, current_col = queue.popleft()
                pixels.append((current_row, current_col))
                for next_row, next_col in (
                    (current_row - 1, current_col),
                    (current_row + 1, current_col),
                    (current_row, current_col - 1),
                    (current_row, current_col + 1),
                ):
                    if (
                        0 <= next_row < mask.shape[0]
                        and 0 <= next_col < mask.shape[1]
                        and mask[next_row, next_col]
                        and not visited[next_row, next_col]
                    ):
                        visited[next_row, next_col] = True
                        queue.append((next_row, next_col))
            components.append(np.asarray(pixels, dtype=np.int16))
    return components


def aupro_score(score_maps: np.ndarray, ground_truth: np.ndarray) -> float:
    if score_maps.shape != ground_truth.shape:
        raise EvaluationError("AUPRO score maps and ground truth have different shapes")
    region_scores: list[np.ndarray] = []
    for index in range(score_maps.shape[0]):
        mask = ground_truth[index]
        if not np.any(mask):
            continue
        for component in connected_components(mask):
            scores = score_maps[index, component[:, 0], component[:, 1]]
            region_scores.append(np.sort(np.asarray(scores, dtype=np.float64)))
    if not region_scores:
        raise EvaluationError("AUPRO requires at least one defect region")

    negative_scores = np.sort(np.asarray(score_maps[~ground_truth], dtype=np.float64))
    if negative_scores.size == 0:
        raise EvaluationError("AUPRO requires negative pixels")

    thresholds = np.unique(score_maps.reshape(-1))[::-1]
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    for threshold in thresholds:
        false_positive_pixels = negative_scores.size - int(
            np.searchsorted(negative_scores, threshold, side="left")
        )
        fpr = false_positive_pixels / float(negative_scores.size)
        overlaps = [
            (scores.size - int(np.searchsorted(scores, threshold, side="left"))) / float(scores.size)
            for scores in region_scores
        ]
        pro = float(np.mean(overlaps))
        points.append((float(fpr), pro))
        if fpr >= AUPRO_MAX_FPR:
            break

    points = collapse_duplicate_fpr(points)
    area = integrate_clipped(points, AUPRO_MAX_FPR)
    return float(area / AUPRO_MAX_FPR)


def collapse_duplicate_fpr(points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    collapsed: list[tuple[float, float]] = []
    for fpr, pro in points:
        if collapsed and fpr == collapsed[-1][0]:
            collapsed[-1] = (fpr, max(collapsed[-1][1], pro))
        else:
            collapsed.append((fpr, pro))
    return collapsed


def integrate_clipped(points: Sequence[tuple[float, float]], max_fpr: float) -> float:
    if len(points) < 2:
        return 0.0
    area = 0.0
    previous_fpr, previous_pro = points[0]
    for current_fpr, current_pro in points[1:]:
        if previous_fpr >= max_fpr:
            break
        segment_end = min(current_fpr, max_fpr)
        if segment_end > previous_fpr:
            if current_fpr == previous_fpr:
                interpolated_pro = current_pro
            else:
                ratio = (segment_end - previous_fpr) / (current_fpr - previous_fpr)
                interpolated_pro = previous_pro + ratio * (current_pro - previous_pro)
            area += (segment_end - previous_fpr) * (previous_pro + interpolated_pro) / 2.0
        previous_fpr, previous_pro = current_fpr, current_pro
    return float(area)


def bbox_mask(localization: Mapping[str, Any]) -> np.ndarray:
    region = localization.get("region")
    if not isinstance(region, Mapping):
        raise EvaluationError("localization lacks region")
    x_min = clamp01(float(region["x_min"]))
    y_min = clamp01(float(region["y_min"]))
    x_max = clamp01(float(region["x_max"]))
    y_max = clamp01(float(region["y_max"]))
    col_min = max(0, min(MASK_SIZE - 1, int(math.floor(x_min * MASK_SIZE))))
    row_min = max(0, min(MASK_SIZE - 1, int(math.floor(y_min * MASK_SIZE))))
    col_max = max(col_min + 1, min(MASK_SIZE, int(math.ceil(x_max * MASK_SIZE))))
    row_max = max(row_min + 1, min(MASK_SIZE, int(math.ceil(y_max * MASK_SIZE))))
    mask = np.zeros((MASK_SIZE, MASK_SIZE), dtype=bool)
    mask[row_min:row_max, col_min:col_max] = True
    return mask


def clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def summarize_scores(observations: Sequence[EvaluationObservation]) -> dict[str, float]:
    scores = np.asarray([observation.score for observation in observations], dtype=np.float64)
    return {
        "min": float(np.min(scores)),
        "max": float(np.max(scores)),
        "mean": float(np.mean(scores)),
        "median": float(np.median(scores)),
    }


def class_distribution(observations: Sequence[EvaluationObservation]) -> dict[str, dict[str, int]]:
    distribution: dict[str, Counter[str]] = defaultdict(Counter)
    for observation in observations:
        distribution[observation.sample.class_name][observation.sample.label] += 1
    return {
        class_name: dict(sorted(counts.items()))
        for class_name, counts in sorted(distribution.items())
    }


def aggregate_confusions(confusions: Sequence[Mapping[str, int]]) -> dict[str, int]:
    total = Counter()
    for confusion in confusions:
        total.update(confusion)
    return {
        "true_positive": int(total["true_positive"]),
        "false_positive": int(total["false_positive"]),
        "true_negative": int(total["true_negative"]),
        "false_negative": int(total["false_negative"]),
    }


def record_for_case(
    observation: EvaluationObservation,
    threshold: float,
    *,
    case_type: str,
) -> dict[str, Any]:
    return {
        "case_type": case_type,
        "split": observation.sample.split,
        "input_id": observation.sample.input_id,
        "filename": observation.sample.filename,
        "class_name": observation.sample.class_name,
        "label": observation.sample.label,
        "sample_sha256": observation.sample.sample_sha256,
        "raw_anomaly_measure": observation.score,
        "operating_point": threshold,
        "margin_from_operating_point": observation.score - threshold,
        "prediction_rule": "anomaly if raw anomaly measure >= operating point",
    }


def evaluate_observations(
    validation: Sequence[EvaluationObservation],
    test: Sequence[EvaluationObservation],
    identity: GovernedInputIdentity,
    *,
    evaluation_timestamp: str,
    evidence_date: str,
) -> EvaluationComputation:
    operating_point = derive_operating_point(validation)
    threshold = float(operating_point["validation_derived_value"])

    per_class_results: dict[str, Any] = {}
    official_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    false_positives: list[dict[str, Any]] = []
    false_negatives: list[dict[str, Any]] = []
    localization_failures: list[dict[str, Any]] = []
    boundary_cases: dict[str, list[dict[str, Any]]] = {}
    class_confusions: list[dict[str, int]] = []

    observations_by_class: dict[str, list[EvaluationObservation]] = defaultdict(list)
    for observation in test:
        observations_by_class[observation.sample.class_name].append(observation)

    for class_name in identity.class_order:
        class_observations = observations_by_class[class_name]
        if not class_observations:
            raise EvaluationError(f"test split lacks class: {class_name}")
        labels = [observation.sample.label for observation in class_observations]
        label_values = np.asarray([label_int(label) for label in labels], dtype=np.int8)
        scores = np.asarray([observation.score for observation in class_observations], dtype=np.float64)
        confusion = confusion_at_threshold(labels, scores, threshold)
        diagnostics = diagnostic_metrics_from_confusion(confusion)
        class_confusions.append(confusion)

        masks = np.stack([load_mask(observation.sample) for observation in class_observations], axis=0)
        maps = np.stack([observation.anomaly_map for observation in class_observations], axis=0)
        image_auroc = binary_auroc(label_values, scores)
        pixel_auroc = binary_auroc(masks.reshape(-1).astype(np.int8), maps.reshape(-1))
        aupro = aupro_score(maps, masks)

        class_false_positives: list[dict[str, Any]] = []
        class_false_negatives: list[dict[str, Any]] = []
        class_localization_failures: list[dict[str, Any]] = []
        for observation, mask in zip(class_observations, masks):
            predicted_anomaly = observation.score >= threshold
            actual_anomaly = observation.sample.label == ANOMALY_LABEL
            if predicted_anomaly and not actual_anomaly:
                case = record_for_case(observation, threshold, case_type="false_positive")
                false_positives.append(case)
                class_false_positives.append(case)
            elif not predicted_anomaly and actual_anomaly:
                case = record_for_case(observation, threshold, case_type="false_negative")
                false_negatives.append(case)
                class_false_negatives.append(case)
            elif predicted_anomaly and actual_anomaly:
                predicted_mask = bbox_mask(observation.localization)
                overlap = int(np.logical_and(predicted_mask, mask).sum())
                union = int(np.logical_or(predicted_mask, mask).sum())
                iou = overlap / union if union else 0.0
                if overlap == 0:
                    failure = {
                        **record_for_case(
                            observation,
                            threshold,
                            case_type="localization_failure",
                        ),
                        "failure_rule_id": LOCALIZATION_FAILURE_RULE_ID,
                        "predicted_box_overlap_pixels": overlap,
                        "predicted_box_mask_iou": iou,
                        "mask_sha256": observation.sample.mask_sha256,
                    }
                    localization_failures.append(failure)
                    class_localization_failures.append(failure)

        closest = sorted(
            class_observations,
            key=lambda observation: (
                abs(observation.score - threshold),
                observation.sample.class_name,
                observation.sample.filename,
            ),
        )[:BOUNDARY_CASES_PER_CLASS]
        boundary_cases[class_name] = [
            record_for_case(observation, threshold, case_type="boundary_case")
            for observation in closest
        ]

        official_row = {
            "class_name": class_name,
            "sample_count": len(class_observations),
            "normal_count": int(np.sum(label_values == 0)),
            "anomaly_count": int(np.sum(label_values == 1)),
            "defect_region_count": int(sum(len(connected_components(mask)) for mask in masks if np.any(mask))),
            "image_auroc": image_auroc,
            "pixel_auroc": pixel_auroc,
            "aupro": aupro,
        }
        diagnostic_row = {
            "class_name": class_name,
            "diagnostic_only": True,
            "operating_point": threshold,
            "confusion": confusion,
            **diagnostics,
        }
        official_rows.append(official_row)
        diagnostic_rows.append(diagnostic_row)
        per_class_results[class_name] = {
            "official_metrics": official_row,
            "diagnostic_metrics": diagnostic_row,
            "false_positive_count": len(class_false_positives),
            "false_negative_count": len(class_false_negatives),
            "localization_failure_count": len(class_localization_failures),
            "boundary_case_count": len(boundary_cases[class_name]),
            "score_summary": summarize_scores(class_observations),
        }

    total_confusion = aggregate_confusions(class_confusions)
    official_metrics = {
        "schema": EVALUATION_METRICS_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "split": "test",
        "official_metrics": {
            "primary": "Image AUROC",
            "secondary": ["Pixel AUROC", "AUPRO"],
            "per_class": official_rows,
            "macro_mean": {
                "image_auroc": float(np.mean([row["image_auroc"] for row in official_rows])),
                "pixel_auroc": float(np.mean([row["pixel_auroc"] for row in official_rows])),
                "aupro": float(np.mean([row["aupro"] for row in official_rows])),
            },
        },
        "caveats": [
            "Per-class results are primary; macro mean is reported only beside the full per-class table.",
            "Pixel AUROC is reported with AUPRO because normal-background dominance can inflate Pixel AUROC.",
            "Single-seed evaluation only; no multi-seed variance or confidence intervals are available.",
        ],
    }
    diagnostic_metrics = {
        "schema": EVALUATION_METRICS_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "split": "test",
        "diagnostic_only": True,
        "operating_point": threshold,
        "total_confusion": total_confusion,
        "total_metrics": diagnostic_metrics_from_confusion(total_confusion),
        "per_class": diagnostic_rows,
        "non_claims": [
            "Diagnostic Precision, Recall, and F1 are not headline metrics.",
            "F1 was not maximized on test.",
            "The operating point is not calibrated and not a product threshold.",
        ],
    }
    operating_point_record = {
        **operating_point,
        "test_application": {
            "split": "test",
            "total_confusion": total_confusion,
            "total_diagnostic_metrics": diagnostic_metrics["total_metrics"],
            "per_class_confusion": diagnostic_rows,
        },
    }
    failure_analysis = {
        "schema": EVALUATION_FAILURE_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "split": "test",
        "operating_point": threshold,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "localization_failures": localization_failures,
        "boundary_cases": boundary_cases,
        "per_class_summary": {
            class_name: {
                "false_positive_count": per_class_results[class_name]["false_positive_count"],
                "false_negative_count": per_class_results[class_name]["false_negative_count"],
                "localization_failure_count": per_class_results[class_name]["localization_failure_count"],
                "boundary_case_count": per_class_results[class_name]["boundary_case_count"],
            }
            for class_name in identity.class_order
        },
        "proxy_domain_limitations": proxy_domain_limitations(),
        "analysis_rules": {
            "false_positive": "normal test image with raw anomaly measure >= validation-derived operating point",
            "false_negative": "anomaly test image with raw anomaly measure < validation-derived operating point",
            "localization_failure": LOCALIZATION_FAILURE_RULE_ID,
            "boundary_case": BOUNDARY_CASE_RULE_ID,
        },
    }
    per_class_record = {
        "schema": "kalibra_scientific_evaluation_per_class_v1",
        "evaluation_label": EVALUATION_LABEL,
        "class_order": list(identity.class_order),
        "per_class": per_class_results,
    }
    metadata = {
        "schema": EVALUATION_METADATA_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "evaluation_timestamp_utc": evaluation_timestamp,
        "authorization_basis": "docs/checkpoints/KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md",
        "protocol_basis": "docs/checkpoints/KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md",
        "dataset_identity": identity.dataset_identity,
        "training_identity": identity.training_identity,
        "inference_identity": identity.inference_identity,
        "evaluation_inputs": {
            "validation_split": "data/visa/manifests/splits/validation.csv",
            "test_split": "data/visa/manifests/splits/test.csv",
            "anomaly_maps": [
                "data/visa/derived/padim/inference/anomaly_maps/validation_anomaly_maps.npy",
                "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy",
            ],
            "inspection_prediction_records": [
                "data/visa/derived/padim/inference/predictions/validation_predictions.jsonl",
                "data/visa/derived/padim/inference/predictions/test_predictions.jsonl",
            ],
            "source_images_read": False,
            "providers_used": False,
            "model_objects_loaded": False,
            "inference_rerun": False,
        },
        "metric_definitions": {
            "image_auroc": "rank-based AUROC over image labels and raw anomaly measures",
            "pixel_auroc": "rank-based AUROC over 64x64 anomaly-map pixels and nearest-neighbor-resized governed masks",
            "aupro": (
                "per-region overlap integrated over false-positive rate up to "
                f"{AUPRO_MAX_FPR}, normalized by that range"
            ),
            "diagnostic_precision_recall_f1": "computed on test only after applying the validation-derived operating point unchanged",
        },
        "operating_point_rule": {
            "rule_id": OPERATING_POINT_RULE_ID,
            "diagnostic_only": True,
            "not_calibrated": True,
            "not_product_threshold": True,
        },
        "single_seed_limitation": {
            "single_seed": True,
            "deterministic_seed": training.FEATURE_SUBSAMPLE_SEED,
            "multi_seed_variance_available": False,
            "confidence_intervals_available": False,
        },
        "scope_boundaries": {
            "retraining_performed": False,
            "refitting_performed": False,
            "inference_rerun": False,
            "preprocessing_modified": False,
            "feature_extraction_modified": False,
            "provider_modified": False,
            "output_mapping_modified": False,
            "calibration_performed": False,
            "onnx_exported": False,
            "benchmark_generated": False,
            "product_claim": False,
            "cross_domain_claim": False,
        },
        "sample_counts": {
            "validation": len(validation),
            "test": len(test),
            "validation_by_class": class_distribution(validation),
            "test_by_class": class_distribution(test),
        },
    }

    records = {
        "metadata/evaluation_metadata.json": canonical_json_bytes(metadata),
        "metrics/official_metrics.json": canonical_json_bytes(official_metrics),
        "metrics/diagnostic_metrics.json": canonical_json_bytes(diagnostic_metrics),
        "per_class/per_class_metrics.json": canonical_json_bytes(per_class_record),
        "failure_analysis/failure_analysis.json": canonical_json_bytes(failure_analysis),
        "operating_point/operating_point.json": canonical_json_bytes(operating_point_record),
    }
    evidence_content = build_evidence_document(
        official_metrics,
        diagnostic_metrics,
        operating_point_record,
        failure_analysis,
        metadata,
        evidence_date,
    )
    return EvaluationComputation(
        records=records,
        evidence_content=evidence_content,
        official_metrics=official_metrics,
        diagnostic_metrics=diagnostic_metrics,
        operating_point=operating_point_record,
        failure_analysis=failure_analysis,
        per_class=per_class_record,
        metadata=metadata,
    )


def proxy_domain_limitations() -> list[str]:
    return [
        "VisA is a governed proxy dataset, not Kalibra's domain of record.",
        "VisA is not a cast-aluminium, CNC-machining, gearbox-housing, or metal-part inspection dataset.",
        "The evaluation supports no production claim and no cross-domain generalization claim.",
        "PaDiM is alignment-sensitive; pose or registration differences remain an active risk for future metal-part domains.",
        "VisA upstream annotation-process documentation is incomplete, limiting localization interpretation.",
    ]


def build_replay_record(
    first: EvaluationComputation,
    second: EvaluationComputation,
) -> dict[str, Any]:
    first_hashes = {path: sha256_bytes(content) for path, content in sorted(first.records.items())}
    second_hashes = {path: sha256_bytes(content) for path, content in sorted(second.records.items())}
    comparisons = {
        "metrics": first.official_metrics == second.official_metrics
        and first.diagnostic_metrics == second.diagnostic_metrics,
        "operating_point": first.operating_point == second.operating_point,
        "failure_analysis": first.failure_analysis == second.failure_analysis,
        "reports": first.records == second.records and first.evidence_content == second.evidence_content,
        "hashes": first_hashes == second_hashes,
    }
    if not all(comparisons.values()):
        raise EvaluationError(f"deterministic evaluation replay mismatch: {comparisons}")
    return {
        "schema": EVALUATION_REPLAY_SCHEMA,
        "status": "passed",
        "complete_second_evaluation_run": True,
        "comparisons": comparisons,
        "first_run_report_hashes": first_hashes,
        "second_run_report_hashes": second_hashes,
    }


def build_artifact_hashes_record(
    records: Mapping[str, bytes],
    replay_hash: str,
) -> dict[str, Any]:
    artifact_hashes = {
        path: sha256_bytes(content)
        for path, content in sorted(records.items())
    }
    artifact_hashes["replay/replay_verification.json"] = replay_hash
    return {
        "schema": EVALUATION_ARTIFACT_HASHES_SCHEMA,
        "evaluation_label": EVALUATION_LABEL,
        "governed_evaluation_artifacts": dict(sorted(artifact_hashes.items())),
        "replay_verification": {
            "path": "data/visa/derived/padim/evaluation/replay/replay_verification.json",
            "sha256": replay_hash,
        },
        "local_large_outputs": [],
        "hash_scope": "evaluation directory artifacts except artifact_hashes.json itself",
    }


def build_evidence_document(
    official_metrics: Mapping[str, Any],
    diagnostic_metrics: Mapping[str, Any],
    operating_point: Mapping[str, Any],
    failure_analysis: Mapping[str, Any],
    metadata: Mapping[str, Any],
    evidence_date: str,
) -> bytes:
    dataset = metadata["dataset_identity"]
    training_identity = metadata["training_identity"]
    inference_identity = metadata["inference_identity"]
    macro = official_metrics["official_metrics"]["macro_mean"]
    total_diag = diagnostic_metrics["total_metrics"]
    total_confusion = diagnostic_metrics["total_confusion"]
    official_table = format_official_table(official_metrics["official_metrics"]["per_class"])
    diagnostic_table = format_diagnostic_table(diagnostic_metrics["per_class"])
    failure_summary = failure_analysis["per_class_summary"]
    failure_table = format_failure_table(failure_summary)
    limitations = "\n".join(f"- {item}" for item in proxy_domain_limitations())
    content = f"""# Kalibra Scientific Evaluation Evidence v1.0

**Status:** Recorded — governed single-seed scientific evaluation evidence
**Date:** {evidence_date}
**Scope:** C-6 Scientific Evaluation only

## Dataset Identity

- Dataset: VisA governed proxy acquisition `{dataset["acquisition_label"]}`
- Archive SHA-256: `{dataset["archive_sha256"]}`
- Files manifest SHA-256: `{dataset["files_manifest_sha256"]}`
- Train split SHA-256: `{training.TRAIN_SPLIT_SHA256}`
- Validation split SHA-256: `{training.VALIDATION_SPLIT_SHA256}`
- Test split SHA-256: `{training.TEST_SPLIT_SHA256}`
- Provenance SHA-256: `{dataset["provenance_sha256"]}`

## Model Identity

- Training label: `{training_identity["training_label"]}`
- Training record SHA-256: `{training_identity["training_record_sha256"]}`
- Training artifact hashes SHA-256: `{training_identity["training_artifact_hashes_sha256"]}`
- Training replay SHA-256: `{training_identity["training_replay_verification_sha256"]}`
- Mu artifact SHA-256: `{training_identity["mu_by_class_sha256"]}`
- Covariance inverse artifact SHA-256: `{training_identity["covariance_inverse_by_class_sha256"]}`
- Feature indices artifact SHA-256: `{training_identity["feature_indices_sha256"]}`
- Feature subsampling seed: `{training.FEATURE_SUBSAMPLE_SEED}`

## Inference Identity

- Inference label: `{inference_identity["inference_label"]}`
- Inference artifact hashes SHA-256: `{inference_identity["inference_artifact_hashes_sha256"]}`
- Inference replay SHA-256: `{inference_identity["inference_replay_verification_sha256"]}`
- Aggregation identifier: `{inference_identity["aggregation_identifier"]}`
- Localization identifier: `{inference_identity["localization_identifier"]}`

## Official Metrics

- Image AUROC (primary, macro mean beside per-class table): `{format_float(macro["image_auroc"])}`
- Pixel AUROC (secondary, macro mean beside per-class table): `{format_float(macro["pixel_auroc"])}`
- AUPRO (secondary, macro mean beside per-class table): `{format_float(macro["aupro"])}`

Pixel AUROC is reported with AUPRO because normal-background dominance can inflate Pixel AUROC.

{official_table}

## Diagnostic Metrics

Diagnostic only.

- Precision: `{format_float(total_diag["precision"])}`
- Recall: `{format_float(total_diag["recall"])}`
- F1: `{format_float(total_diag["f1"])}`
- True positives: `{total_confusion["true_positive"]}`
- False positives: `{total_confusion["false_positive"]}`
- True negatives: `{total_confusion["true_negative"]}`
- False negatives: `{total_confusion["false_negative"]}`

{diagnostic_table}

## Operating Point

- Derivation rule: `{operating_point["selection_rule"]}`
- Validation-derived value: `{format_float(operating_point["validation_derived_value"])}`

Not calibrated.
Not a product threshold.

## Failure Analysis

- False positives: `{len(failure_analysis["false_positives"])}`
- False negatives: `{len(failure_analysis["false_negatives"])}`
- Localization failures: `{len(failure_analysis["localization_failures"])}`
- Boundary-case rule: `{BOUNDARY_CASE_RULE_ID}`

{failure_table}

Localization observations are based on true-positive anomaly images where the governed C-5 predicted box has zero overlap with the resized governed pixel mask. Boundary cases are the closest raw-measure margins to the validation-derived operating point and are raw-measure behavior only, not uncertainty quality.

## Proxy-Domain Limitations

{limitations}

## Scientific Limitations

- Single-seed evaluation only.
- No variance estimation.
- No confidence intervals.
- VisA is a governed proxy dataset.
- No production claim.
- No cross-domain claim.
- No calibrated-confidence claim.
- No benchmark, ranking, leaderboard, or state-of-the-art claim.
- No uncertainty, abstention, review-routing, or drift claim.

## Replay

- Deterministic evaluation replay: `passed`
- Identical metrics: `true`
- Identical operating point: `true`
- Identical failure analysis: `true`
- Identical reports: `true`
- Identical hashes: `true`

## Explicit Scope Checks

- No retraining.
- No refitting.
- No re-inference.
- No preprocessing change.
- No feature-extraction change.
- No provider change.
- No output-mapping change.
- No calibration.
- No ONNX export.
- No product threshold.
- No downstream architecture modification.
"""
    return content.encode("utf-8")


def format_float(value: object) -> str:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f"{float(value):.6f}"
    return "not available"


def format_official_table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "| Class | N | Normal | Anomaly | Image AUROC | Pixel AUROC | AUPRO |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {class_name} | {sample_count} | {normal_count} | {anomaly_count} | {image_auroc} | {pixel_auroc} | {aupro} |".format(
                class_name=row["class_name"],
                sample_count=row["sample_count"],
                normal_count=row["normal_count"],
                anomaly_count=row["anomaly_count"],
                image_auroc=format_float(row["image_auroc"]),
                pixel_auroc=format_float(row["pixel_auroc"]),
                aupro=format_float(row["aupro"]),
            )
        )
    return "\n".join(lines)


def format_diagnostic_table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "| Class | Precision | Recall | F1 | TP | FP | TN | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        confusion = row["confusion"]
        lines.append(
            "| {class_name} | {precision} | {recall} | {f1} | {tp} | {fp} | {tn} | {fn} |".format(
                class_name=row["class_name"],
                precision=format_float(row["precision"]),
                recall=format_float(row["recall"]),
                f1=format_float(row["f1"]),
                tp=confusion["true_positive"],
                fp=confusion["false_positive"],
                tn=confusion["true_negative"],
                fn=confusion["false_negative"],
            )
        )
    return "\n".join(lines)


def format_failure_table(summary: Mapping[str, Mapping[str, int]]) -> str:
    lines = [
        "| Class | FP | FN | Localization failures | Boundary cases |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for class_name, values in summary.items():
        lines.append(
            "| {class_name} | {fp} | {fn} | {loc} | {boundary} |".format(
                class_name=class_name,
                fp=values["false_positive_count"],
                fn=values["false_negative_count"],
                loc=values["localization_failure_count"],
                boundary=values["boundary_case_count"],
            )
        )
    return "\n".join(lines)


def evaluation_timestamp_for_run() -> str:
    metadata_path = EVALUATION_METADATA_DIR / "evaluation_metadata.json"
    if not metadata_path.exists():
        return utc_timestamp()
    metadata = read_json_mapping(metadata_path)
    timestamp = metadata.get("evaluation_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise EvaluationError("existing evaluation metadata lacks evaluation timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text().splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise EvaluationError("existing scientific evaluation evidence lacks Date field")


def compute_evaluation(evaluation_timestamp: str, evidence_date: str) -> EvaluationComputation:
    governed = verify_governed_acquisition_inputs()
    file_hashes = governed.get("file_hashes")
    if not isinstance(file_hashes, Mapping):
        raise EvaluationError("invalid governed file hash map")
    identity = load_governed_identities(governed)
    samples_by_split = {
        split: load_split_samples(split, file_hashes, identity.class_order)
        for split in EVALUATION_SPLITS
    }
    observations = {
        split: load_observations(split, samples_by_split[split], identity)
        for split in EVALUATION_SPLITS
    }
    return evaluate_observations(
        observations["validation"],
        observations["test"],
        identity,
        evaluation_timestamp=evaluation_timestamp,
        evidence_date=evidence_date,
    )


def materialize_records(
    first: EvaluationComputation,
    replay_record: Mapping[str, Any],
    artifact_hashes_record: Mapping[str, Any],
) -> None:
    for relative_path, content in sorted(first.records.items()):
        write_governed_bytes(EVALUATION_DIR / relative_path, content)
    write_governed_bytes(
        EVALUATION_REPLAY_DIR / "replay_verification.json",
        canonical_json_bytes(replay_record),
    )
    write_governed_bytes(
        EVALUATION_ARTIFACT_HASHES_PATH,
        canonical_json_bytes(artifact_hashes_record),
    )
    write_governed_bytes(EVIDENCE_PATH, first.evidence_content)


def run_evaluation() -> None:
    ensure_layout()
    evaluation_timestamp = evaluation_timestamp_for_run()
    evidence_date = evidence_date_for_run()
    first = compute_evaluation(evaluation_timestamp, evidence_date)
    second = compute_evaluation(evaluation_timestamp, evidence_date)
    replay_record = build_replay_record(first, second)
    replay_content = canonical_json_bytes(replay_record)
    replay_hash = sha256_bytes(replay_content)
    artifact_hashes_record = build_artifact_hashes_record(first.records, replay_hash)
    materialize_records(first, replay_record, artifact_hashes_record)


def verify_evaluation() -> None:
    evaluation_timestamp = evaluation_timestamp_for_run()
    evidence_date = evidence_date_for_run()
    first = compute_evaluation(evaluation_timestamp, evidence_date)
    second = compute_evaluation(evaluation_timestamp, evidence_date)
    replay_record = build_replay_record(first, second)
    replay_content = canonical_json_bytes(replay_record)
    replay_hash = sha256_bytes(replay_content)
    artifact_hashes_record = build_artifact_hashes_record(first.records, replay_hash)
    expected_records = dict(first.records)
    expected_records["replay/replay_verification.json"] = replay_content
    expected_records["artifact_hashes.json"] = canonical_json_bytes(artifact_hashes_record)
    for relative_path, expected_content in sorted(expected_records.items()):
        verify_file_hash(EVALUATION_DIR / relative_path, sha256_bytes(expected_content), relative_path)
        actual = (EVALUATION_DIR / relative_path).read_bytes()
        if actual != expected_content:
            raise EvaluationError(f"evaluation record bytes mismatch: {relative_path}")
    if EVIDENCE_PATH.read_bytes() != first.evidence_content:
        raise EvaluationError("scientific evaluation evidence bytes mismatch")
    recorded_hashes = read_json_mapping(EVALUATION_ARTIFACT_HASHES_PATH)
    if recorded_hashes != artifact_hashes_record:
        raise EvaluationError("evaluation artifact hashes record does not match regenerated hashes")
    recorded_replay = read_json_mapping(EVALUATION_REPLAY_DIR / "replay_verification.json")
    if recorded_replay.get("status") != "passed":
        raise EvaluationError("evaluation replay record is not passed")
    if recorded_replay != replay_record:
        raise EvaluationError("evaluation replay record does not match regenerated replay")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="C-6 governed scientific evaluation")
    parser.add_argument("command", choices=("evaluate", "verify"))
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate":
            run_evaluation()
        elif args.command == "verify":
            verify_evaluation()
    except (
        EvaluationError,
        inference.InferenceError,
        training.TrainingError,
        acquisition.AcquisitionError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
