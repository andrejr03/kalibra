#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import governed_visa_acquisition as acquisition  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "visa"
SOURCE_DIR = DATA_ROOT / "source"
EXTRACTED_DIR = DATA_ROOT / "extracted"
MANIFESTS_DIR = DATA_ROOT / "manifests"
SPLITS_DIR = MANIFESTS_DIR / "splits"
PROVENANCE_DIR = DATA_ROOT / "provenance"
PADIM_ROOT = DATA_ROOT / "derived" / "padim"
TRAINING_DIR = PADIM_ROOT / "training"
STATISTICS_DIR = PADIM_ROOT / "statistics"
COVARIANCE_DIR = PADIM_ROOT / "covariance"
METADATA_DIR = PADIM_ROOT / "metadata"
LOCAL_EVIDENCE_DIR = PADIM_ROOT / "evidence"
FEATURE_TENSOR_DIR = STATISTICS_DIR / "feature_tensors"
EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "evidence" / "PADIM_BASELINE_TRAINING.md"
)

ARCHIVE_SHA256 = "2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362"
FILES_MANIFEST_SHA256 = "a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c"
TRAIN_SPLIT_SHA256 = "9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736"
VALIDATION_SPLIT_SHA256 = "79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5"
TEST_SPLIT_SHA256 = "2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510"
PROVENANCE_SHA256 = "01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0"

BACKBONE_IDENTITY = "kalibra-fixed-patch-feature-backbone-v1"
BACKBONE_LAYER = "fixed_patch_statistics_64x64_patch8"
PREPROCESSING_CONTRACT_ID = "kalibra-padim-rgb64-bilinear-float64-patch8-v1"
TRAINING_RECORD_SCHEMA = "kalibra_padim_baseline_training_record_v1"
TRAINING_LABEL = "visa-padim-baseline-fit-v1"
FEATURE_SUBSAMPLE_SEED = 271828
COVARIANCE_EPSILON = 1.0e-3
IMAGE_SIZE = 64
PATCH_SIZE = 8
FULL_FEATURE_DIMENSION = 14
SELECTED_FEATURE_DIMENSION = 8
BATCH_SIZE = 16
DTYPE_NAME = "float64"


class TrainingError(RuntimeError):
    """Raised when C-4 training cannot proceed safely."""


@dataclass(frozen=True)
class TrainSample:
    filename: str
    class_name: str
    label: str
    sha256: str
    source_csv: str
    source_split: str


@dataclass(frozen=True)
class FitConfig:
    image_size: int = IMAGE_SIZE
    patch_size: int = PATCH_SIZE
    full_feature_dimension: int = FULL_FEATURE_DIMENSION
    selected_feature_dimension: int = SELECTED_FEATURE_DIMENSION
    feature_subsample_seed: int = FEATURE_SUBSAMPLE_SEED
    covariance_epsilon: float = COVARIANCE_EPSILON
    batch_size: int = BATCH_SIZE

    @property
    def patch_grid(self) -> tuple[int, int]:
        if self.image_size % self.patch_size != 0:
            raise TrainingError("image_size must be divisible by patch_size")
        grid = self.image_size // self.patch_size
        return (grid, grid)

    @property
    def patch_count(self) -> int:
        grid_h, grid_w = self.patch_grid
        return grid_h * grid_w

    def to_json_dict(self) -> dict[str, object]:
        return {
            "image_size": self.image_size,
            "patch_size": self.patch_size,
            "patch_grid": list(self.patch_grid),
            "patch_count": self.patch_count,
            "full_feature_dimension": self.full_feature_dimension,
            "selected_feature_dimension": self.selected_feature_dimension,
            "feature_subsample_seed": self.feature_subsample_seed,
            "covariance_epsilon": self.covariance_epsilon,
            "batch_size": self.batch_size,
            "dtype": DTYPE_NAME,
        }


@dataclass(frozen=True)
class FitResult:
    class_names: tuple[str, ...]
    feature_indices: np.ndarray
    mu: np.ndarray
    covariance: np.ndarray
    covariance_inverse: np.ndarray
    feature_tensors: dict[str, np.ndarray]
    conditioning: dict[str, object]
    sample_counts: dict[str, int]


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
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


def ensure_layout() -> None:
    for directory in (
        TRAINING_DIR,
        STATISTICS_DIR,
        COVARIANCE_DIR,
        METADATA_DIR,
        LOCAL_EVIDENCE_DIR,
        FEATURE_TENSOR_DIR,
        EVIDENCE_PATH.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def write_governed_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise TrainingError(f"governed training record changed: {path}")
        return acquisition.sha256_file(path)
    path.write_bytes(content)
    return acquisition.sha256_file(path)


def write_json_record(path: Path, value: Mapping[str, object]) -> str:
    return write_governed_bytes(path, canonical_json_bytes(value))


def write_npy_record(path: Path, array: np.ndarray) -> str:
    return write_governed_bytes(path, npy_bytes(array))


def verify_record_hash(path: Path, expected_digest: str | None = None) -> str:
    hash_path = path.with_name(path.name + ".sha256")
    if not hash_path.exists():
        raise TrainingError(f"missing hash record: {hash_path}")
    entries = acquisition.parse_sha256_manifest(hash_path)
    digest = entries.get(path.name)
    if digest is None:
        raise TrainingError(f"hash record does not reference {path.name}")
    actual = acquisition.sha256_file(path)
    if digest != actual:
        raise TrainingError(f"hash mismatch for {path}: expected {digest}, got {actual}")
    if expected_digest is not None and digest != expected_digest:
        raise TrainingError(
            f"unexpected governed hash for {path}: expected {expected_digest}, got {digest}"
        )
    return digest


def verify_archive_hash() -> str:
    archive_path = SOURCE_DIR / acquisition.ARCHIVE_FILENAME
    if not archive_path.exists():
        raise TrainingError(f"missing governed source archive: {archive_path}")
    entries = acquisition.parse_sha256_manifest(MANIFESTS_DIR / "archive.sha256")
    expected = entries.get("../source/VisA_20220922.tar")
    if expected != ARCHIVE_SHA256:
        raise TrainingError("archive.sha256 does not match the governed archive identity")
    actual = acquisition.sha256_file(archive_path)
    if actual != expected:
        raise TrainingError(f"source archive hash mismatch: expected {expected}, got {actual}")
    return actual


def verify_files_manifest() -> dict[str, str]:
    manifest_path = MANIFESTS_DIR / "files.sha256"
    manifest_hash = acquisition.sha256_file(manifest_path)
    if manifest_hash != FILES_MANIFEST_SHA256:
        raise TrainingError(
            f"files.sha256 identity mismatch: expected {FILES_MANIFEST_SHA256}, got {manifest_hash}"
        )
    recorded = acquisition.parse_sha256_manifest(manifest_path)
    actual_paths = {
        path.relative_to(EXTRACTED_DIR).as_posix(): acquisition.sha256_file(path)
        for path in acquisition.iter_files(EXTRACTED_DIR)
    }
    if recorded != actual_paths:
        raise TrainingError("per-file manifest does not match extracted governed dataset")
    return recorded


def verify_governed_acquisition() -> dict[str, object]:
    archive_hash = verify_archive_hash()
    file_hashes = verify_files_manifest()
    split_hashes = {
        "train": verify_record_hash(SPLITS_DIR / "train.csv", TRAIN_SPLIT_SHA256),
        "validation": verify_record_hash(
            SPLITS_DIR / "validation.csv",
            VALIDATION_SPLIT_SHA256,
        ),
        "test": verify_record_hash(SPLITS_DIR / "test.csv", TEST_SPLIT_SHA256),
    }
    provenance_hash = verify_record_hash(
        PROVENANCE_DIR / "provenance.json",
        PROVENANCE_SHA256,
    )
    provenance = json.loads((PROVENANCE_DIR / "provenance.json").read_text())
    acquisition.validate_provenance(provenance)
    if provenance["archive"]["sha256"] != archive_hash:
        raise TrainingError("provenance archive hash does not match archive identity")
    return {
        "archive_sha256": archive_hash,
        "files_manifest_sha256": FILES_MANIFEST_SHA256,
        "split_hashes": split_hashes,
        "provenance_sha256": provenance_hash,
        "provenance": provenance,
        "file_hashes": file_hashes,
    }


def load_train_samples(file_hashes: Mapping[str, str]) -> list[TrainSample]:
    train_path = SPLITS_DIR / "train.csv"
    samples: list[TrainSample] = []
    seen: set[str] = set()
    with train_path.open(newline="") as file:
        reader = csv.DictReader(file)
        expected = [
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
        if reader.fieldnames != expected:
            raise TrainingError(f"unexpected train manifest header: {reader.fieldnames}")
        for row in reader:
            filename = row["filename"]
            if filename in seen:
                raise TrainingError(f"duplicate train sample: {filename}")
            seen.add(filename)
            validate_train_row(row, file_hashes)
            samples.append(
                TrainSample(
                    filename=filename,
                    class_name=row["class"],
                    label=row["label"],
                    sha256=row["sha256"],
                    source_csv=row["source_csv"],
                    source_split=row["source_split"],
                )
            )
    if not samples:
        raise TrainingError("train split is empty")
    return sorted(samples, key=lambda sample: (sample.class_name, sample.filename))


def validate_train_row(row: Mapping[str, str], file_hashes: Mapping[str, str]) -> None:
    if row["artifact_type"] != "image":
        raise TrainingError("non-image artifact in train split")
    if row["label"] != "normal" or row["source_label"] != "normal":
        raise TrainingError("non-normal sample in train split")
    if row["source_csv"] != "1cls.csv":
        raise TrainingError("train manifest row is not sourced from upstream 1cls.csv")
    if row["source_mask"]:
        raise TrainingError("train sample unexpectedly references a mask")
    if row["source_image"] != row["filename"]:
        raise TrainingError("train source_image does not match filename")
    if row["filename"] not in file_hashes:
        raise TrainingError(f"train sample missing from files.sha256: {row['filename']}")
    if file_hashes[row["filename"]] != row["sha256"]:
        raise TrainingError(f"train sample hash mismatch: {row['filename']}")
    image_path = EXTRACTED_DIR / row["filename"]
    if not image_path.exists():
        raise TrainingError(f"train image missing from extracted dataset: {row['filename']}")


def group_samples_by_class(samples: Sequence[TrainSample]) -> dict[str, list[TrainSample]]:
    grouped: dict[str, list[TrainSample]] = defaultdict(list)
    for sample in samples:
        grouped[sample.class_name].append(sample)
    return {class_name: grouped[class_name] for class_name in sorted(grouped)}


def select_feature_indices(
    full_dimension: int,
    selected_dimension: int,
    seed: int,
) -> np.ndarray:
    if selected_dimension <= 0:
        raise TrainingError("selected feature dimension must be positive")
    if selected_dimension > full_dimension:
        raise TrainingError("selected feature dimension exceeds full feature dimension")
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(full_dimension, size=selected_dimension, replace=False))


def resampling_filter() -> int:
    try:
        return Image.Resampling.BILINEAR
    except AttributeError:
        return Image.BILINEAR


def extract_features(image_path: Path, config: FitConfig) -> np.ndarray:
    with Image.open(image_path) as image:
        resized = image.convert("RGB").resize(
            (config.image_size, config.image_size),
            resampling_filter(),
        )
        rgb = np.asarray(resized, dtype=np.float64) / 255.0

    gray = (
        0.299 * rgb[:, :, 0]
        + 0.587 * rgb[:, :, 1]
        + 0.114 * rgb[:, :, 2]
    )
    grad_y, grad_x = np.gradient(gray)
    grad_mag = np.hypot(grad_x, grad_y)

    rgb_mean, rgb_std = patch_mean_std(rgb, config)
    gray_mean, gray_std = patch_mean_std(gray, config)
    grad_x_mean, grad_x_std = patch_mean_std(grad_x, config)
    grad_y_mean, grad_y_std = patch_mean_std(grad_y, config)
    grad_mag_mean, grad_mag_std = patch_mean_std(grad_mag, config)
    features = np.concatenate(
        (
            rgb_mean,
            rgb_std,
            gray_mean,
            gray_std,
            grad_x_mean,
            grad_x_std,
            grad_y_mean,
            grad_y_std,
            grad_mag_mean,
            grad_mag_std,
        ),
        axis=1,
    )
    if features.shape != (config.patch_count, config.full_feature_dimension):
        raise TrainingError(f"unexpected feature shape: {features.shape}")
    return np.ascontiguousarray(features, dtype=np.float64)


def patch_mean_std(
    values: np.ndarray,
    config: FitConfig,
) -> tuple[np.ndarray, np.ndarray]:
    grid_h, grid_w = config.patch_grid
    patch = config.patch_size
    if values.ndim == 2:
        patched = values.reshape(grid_h, patch, grid_w, patch).transpose(0, 2, 1, 3)
        mean = patched.mean(axis=(2, 3)).reshape(config.patch_count, 1)
        std = patched.std(axis=(2, 3)).reshape(config.patch_count, 1)
        return mean, std
    if values.ndim == 3:
        channels = values.shape[2]
        patched = values.reshape(grid_h, patch, grid_w, patch, channels).transpose(
            0,
            2,
            1,
            3,
            4,
        )
        mean = patched.mean(axis=(2, 3)).reshape(config.patch_count, channels)
        std = patched.std(axis=(2, 3)).reshape(config.patch_count, channels)
        return mean, std
    raise TrainingError("patch statistics only support 2D or 3D arrays")


def iter_batches(samples: Sequence[TrainSample], batch_size: int) -> Iterable[list[TrainSample]]:
    for index in range(0, len(samples), batch_size):
        yield list(samples[index : index + batch_size])


def extract_class_feature_tensor(
    samples: Sequence[TrainSample],
    feature_indices: np.ndarray,
    config: FitConfig,
) -> np.ndarray:
    tensors: list[np.ndarray] = []
    for batch in iter_batches(samples, config.batch_size):
        for sample in batch:
            full_features = extract_features(EXTRACTED_DIR / sample.filename, config)
            tensors.append(full_features[:, feature_indices])
    if not tensors:
        raise TrainingError("cannot fit PaDiM with an empty class")
    return np.ascontiguousarray(np.stack(tensors, axis=0), dtype=np.float64)


def fit_class_statistics(
    features: np.ndarray,
    epsilon: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    sample_count, patch_count, dimension = features.shape
    if sample_count < 2:
        raise TrainingError("at least two training samples are required per class")
    mu = features.mean(axis=0)
    covariance = np.empty((patch_count, dimension, dimension), dtype=np.float64)
    covariance_inverse = np.empty_like(covariance)
    condition_before: list[float] = []
    condition_after: list[float] = []
    identity = np.eye(dimension, dtype=np.float64)
    for patch_index in range(patch_count):
        centered = features[:, patch_index, :] - mu[patch_index]
        cov = centered.T @ centered / float(sample_count - 1)
        reg_cov = cov + epsilon * identity
        covariance[patch_index] = reg_cov
        covariance_inverse[patch_index] = np.linalg.inv(reg_cov)
        condition_before.append(float(np.linalg.cond(cov)))
        condition_after.append(float(np.linalg.cond(reg_cov)))
    finite_before = [value for value in condition_before if np.isfinite(value)]
    conditioning = {
        "max_condition_before_regularization": float(max(finite_before))
        if finite_before
        else float("inf"),
        "max_condition_after_regularization": float(max(condition_after)),
        "mean_condition_after_regularization": float(np.mean(condition_after)),
    }
    return mu, covariance, covariance_inverse, conditioning


def fit_padim(samples: Sequence[TrainSample], config: FitConfig) -> FitResult:
    grouped = group_samples_by_class(samples)
    class_names = tuple(grouped)
    feature_indices = select_feature_indices(
        config.full_feature_dimension,
        config.selected_feature_dimension,
        config.feature_subsample_seed,
    )
    feature_tensors: dict[str, np.ndarray] = {}
    mu_by_class: list[np.ndarray] = []
    cov_by_class: list[np.ndarray] = []
    inv_by_class: list[np.ndarray] = []
    conditioning_by_class: dict[str, object] = {}
    sample_counts: dict[str, int] = {}
    for class_name, class_samples in grouped.items():
        feature_tensor = extract_class_feature_tensor(class_samples, feature_indices, config)
        mu, covariance, covariance_inverse, conditioning = fit_class_statistics(
            feature_tensor,
            config.covariance_epsilon,
        )
        feature_tensors[class_name] = feature_tensor
        mu_by_class.append(mu)
        cov_by_class.append(covariance)
        inv_by_class.append(covariance_inverse)
        conditioning_by_class[class_name] = conditioning
        sample_counts[class_name] = len(class_samples)
    return FitResult(
        class_names=class_names,
        feature_indices=feature_indices,
        mu=np.ascontiguousarray(np.stack(mu_by_class, axis=0), dtype=np.float64),
        covariance=np.ascontiguousarray(np.stack(cov_by_class, axis=0), dtype=np.float64),
        covariance_inverse=np.ascontiguousarray(np.stack(inv_by_class, axis=0), dtype=np.float64),
        feature_tensors=feature_tensors,
        conditioning={
            "regularization": "covariance + epsilon * I",
            "epsilon": config.covariance_epsilon,
            "classes": conditioning_by_class,
        },
        sample_counts=sample_counts,
    )


def training_timestamp_for_run() -> str:
    record_path = TRAINING_DIR / "training_record.json"
    if not record_path.exists():
        return utc_timestamp()
    record = json.loads(record_path.read_text())
    timestamp = record.get("training_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise TrainingError("existing training record lacks training timestamp")
    return timestamp


def class_distribution(samples: Sequence[TrainSample]) -> dict[str, int]:
    counts = Counter(sample.class_name for sample in samples)
    return dict(sorted(counts.items()))


def dataset_identity(governed: Mapping[str, object]) -> dict[str, object]:
    provenance = governed["provenance"]
    if not isinstance(provenance, Mapping):
        raise TrainingError("invalid provenance object")
    return {
        "dataset": "VisA",
        "role": "governed proxy dataset",
        "acquisition_label": provenance["local_governed_identity"]["label"],
        "archive_sha256": governed["archive_sha256"],
        "files_manifest_sha256": governed["files_manifest_sha256"],
        "split_hashes": governed["split_hashes"],
        "provenance_sha256": governed["provenance_sha256"],
        "canonical_archive_url": provenance["archive"]["url"],
        "repository_commit": provenance["upstream_identifiers"]["repository_commit"],
    }


def backbone_metadata() -> dict[str, object]:
    return {
        "backbone_identity": BACKBONE_IDENTITY,
        "backbone_kind": "deterministic fixed local patch feature extractor",
        "pretrained_external_weights": False,
        "selected_layers": [BACKBONE_LAYER],
        "full_feature_dimension": FULL_FEATURE_DIMENSION,
        "feature_components": [
            "rgb_patch_mean_3",
            "rgb_patch_std_3",
            "grayscale_patch_mean_1",
            "grayscale_patch_std_1",
            "gradient_x_patch_mean_1",
            "gradient_x_patch_std_1",
            "gradient_y_patch_mean_1",
            "gradient_y_patch_std_1",
            "gradient_magnitude_patch_mean_1",
            "gradient_magnitude_patch_std_1",
        ],
        "provenance": (
            "Implemented as deterministic local feature extraction code in "
            "scripts/train_padim_baseline.py; no external model weights are used."
        ),
    }


def preprocessing_contract(config: FitConfig) -> dict[str, object]:
    return {
        "contract_id": PREPROCESSING_CONTRACT_ID,
        "scope": "C-4 PaDiM training only; existing runtime preprocessing is unchanged",
        "steps": [
            "open governed train image bytes with Pillow",
            "convert to RGB",
            "resize to 64x64 using bilinear interpolation",
            "convert to float64 in [0, 1]",
            "derive deterministic patch statistics over 8x8 patches",
        ],
        "config": config.to_json_dict(),
    }


def numerical_config(config: FitConfig) -> dict[str, object]:
    return {
        "numpy_version": np.__version__,
        "pillow_version": Image.__version__,
        "dtype": DTYPE_NAME,
        "covariance_estimator": "sample covariance, centered.T @ centered / (n - 1)",
        "covariance_regularization": "covariance + epsilon * I",
        "epsilon": config.covariance_epsilon,
        "inverse": "numpy.linalg.inv on regularized covariance",
        "batching": {
            "batch_size": config.batch_size,
            "batch_order": "class then filename, both lexicographic",
        },
    }


def write_fit_artifacts(fit: FitResult, config: FitConfig) -> dict[str, str]:
    artifact_hashes: dict[str, str] = {}
    artifact_hashes["statistics/mu_by_class.npy"] = write_npy_record(
        STATISTICS_DIR / "mu_by_class.npy",
        fit.mu,
    )
    artifact_hashes["statistics/feature_indices.npy"] = write_npy_record(
        STATISTICS_DIR / "feature_indices.npy",
        fit.feature_indices,
    )
    for class_name, feature_tensor in fit.feature_tensors.items():
        artifact_hashes[f"statistics/feature_tensors/{class_name}.npy"] = write_npy_record(
            FEATURE_TENSOR_DIR / f"{class_name}.npy",
            feature_tensor,
        )
    artifact_hashes["covariance/covariance_by_class.npy"] = write_npy_record(
        COVARIANCE_DIR / "covariance_by_class.npy",
        fit.covariance,
    )
    artifact_hashes["covariance/covariance_inverse_by_class.npy"] = write_npy_record(
        COVARIANCE_DIR / "covariance_inverse_by_class.npy",
        fit.covariance_inverse,
    )
    feature_statistics = {
        "class_order": list(fit.class_names),
        "sample_counts": fit.sample_counts,
        "patch_count": config.patch_count,
        "selected_feature_dimension": config.selected_feature_dimension,
        "feature_tensor_shapes": {
            class_name: list(tensor.shape)
            for class_name, tensor in fit.feature_tensors.items()
        },
    }
    artifact_hashes["statistics/feature_statistics.json"] = write_json_record(
        STATISTICS_DIR / "feature_statistics.json",
        feature_statistics,
    )
    return dict(sorted(artifact_hashes.items()))


def write_metadata_records(
    fit: FitResult,
    config: FitConfig,
    governed: Mapping[str, object],
    samples: Sequence[TrainSample],
) -> dict[str, str]:
    metadata_hashes: dict[str, str] = {}
    metadata_hashes["metadata/dataset_identity.json"] = write_json_record(
        METADATA_DIR / "dataset_identity.json",
        dataset_identity(governed),
    )
    metadata_hashes["metadata/backbone_metadata.json"] = write_json_record(
        METADATA_DIR / "backbone_metadata.json",
        backbone_metadata(),
    )
    metadata_hashes["metadata/preprocessing_contract.json"] = write_json_record(
        METADATA_DIR / "preprocessing_contract.json",
        preprocessing_contract(config),
    )
    metadata_hashes["metadata/numerical_config.json"] = write_json_record(
        METADATA_DIR / "numerical_config.json",
        numerical_config(config),
    )
    metadata_hashes["metadata/feature_indices.json"] = write_json_record(
        METADATA_DIR / "feature_indices.json",
        {
            "seed": config.feature_subsample_seed,
            "full_feature_dimension": config.full_feature_dimension,
            "selected_feature_dimension": config.selected_feature_dimension,
            "selected_indices": fit.feature_indices.tolist(),
            "ordering": "ascending after deterministic seed selection",
        },
    )
    metadata_hashes["metadata/train_split_use.json"] = write_json_record(
        METADATA_DIR / "train_split_use.json",
        {
            "train_manifest": "data/visa/manifests/splits/train.csv",
            "train_split_sha256": TRAIN_SPLIT_SHA256,
            "sample_count": len(samples),
            "labels": {"normal": len(samples)},
            "class_distribution": class_distribution(samples),
            "upstream_source_split_distribution": dict(
                sorted(Counter(sample.source_split for sample in samples).items())
            ),
            "validation_samples_loaded": 0,
            "test_samples_loaded": 0,
            "assertion": (
                "only rows from Kalibra's immutable train.csv are parsed for "
                "training samples; upstream source_split is preserved only as "
                "provenance from the acquisition manifest"
            ),
        },
    )
    return dict(sorted(metadata_hashes.items()))


def replay_verify(first: FitResult, samples: Sequence[TrainSample], config: FitConfig) -> dict[str, object]:
    second = fit_padim(samples, config)
    feature_hashes_first = {
        class_name: npy_sha256(tensor)
        for class_name, tensor in first.feature_tensors.items()
    }
    feature_hashes_second = {
        class_name: npy_sha256(tensor)
        for class_name, tensor in second.feature_tensors.items()
    }
    comparisons = {
        "feature_indices": bool(np.array_equal(first.feature_indices, second.feature_indices)),
        "feature_tensors": feature_hashes_first == feature_hashes_second,
        "mu": bool(np.array_equal(first.mu, second.mu)),
        "covariance": bool(np.array_equal(first.covariance, second.covariance)),
        "covariance_inverse": bool(np.array_equal(first.covariance_inverse, second.covariance_inverse)),
        "mu_hash": npy_sha256(first.mu) == npy_sha256(second.mu),
        "covariance_inverse_hash": npy_sha256(first.covariance_inverse)
        == npy_sha256(second.covariance_inverse),
    }
    if not all(comparisons.values()):
        raise TrainingError(f"deterministic replay mismatch: {comparisons}")
    return {
        "status": "passed",
        "complete_second_fit": True,
        "comparisons": comparisons,
        "hashes": {
            "feature_tensors": feature_hashes_first,
            "mu_by_class": npy_sha256(first.mu),
            "covariance_by_class": npy_sha256(first.covariance),
            "covariance_inverse_by_class": npy_sha256(first.covariance_inverse),
            "feature_indices": npy_sha256(first.feature_indices),
        },
    }


def write_training_records(
    fit: FitResult,
    config: FitConfig,
    governed: Mapping[str, object],
    samples: Sequence[TrainSample],
    artifact_hashes: Mapping[str, str],
    metadata_hashes: Mapping[str, str],
    replay: Mapping[str, object],
    training_timestamp: str,
) -> dict[str, str]:
    replay_hash = write_json_record(TRAINING_DIR / "replay_verification.json", replay)
    artifact_hash_record = {
        "schema": "kalibra_padim_training_artifact_hashes_v1",
        "array_artifacts": dict(sorted(artifact_hashes.items())),
        "metadata_artifacts": dict(sorted(metadata_hashes.items())),
        "replay_verification": {
            "path": "data/visa/derived/padim/training/replay_verification.json",
            "sha256": replay_hash,
        },
    }
    artifact_hash_record_hash = write_json_record(
        TRAINING_DIR / "artifact_hashes.json",
        artifact_hash_record,
    )
    metadata = {
        "schema": "kalibra_padim_training_metadata_v1",
        "training_label": TRAINING_LABEL,
        "training_timestamp_utc": training_timestamp,
        "dataset_identity": dataset_identity(governed),
        "split_identity": {
            "train_split_sha256": TRAIN_SPLIT_SHA256,
            "validation_split_sha256": VALIDATION_SPLIT_SHA256,
            "test_split_sha256": TEST_SPLIT_SHA256,
            "training_consumed_split": "train",
        },
        "backbone": backbone_metadata(),
        "selected_layer": BACKBONE_LAYER,
        "feature_dimension": {
            "full": config.full_feature_dimension,
            "selected": config.selected_feature_dimension,
            "indices": fit.feature_indices.tolist(),
        },
        "deterministic_seed": config.feature_subsample_seed,
        "preprocessing_contract_id": PREPROCESSING_CONTRACT_ID,
        "numerical_configuration": numerical_config(config),
        "covariance_conditioning": fit.conditioning,
        "sample_counts": fit.sample_counts,
        "artifact_hashes": artifact_hash_record,
        "scope_boundaries": {
            "inference_executed": False,
            "validation_inference_executed": False,
            "test_inference_executed": False,
            "evaluation_executed": False,
            "benchmark_generated": False,
            "onnx_exported": False,
            "scientific_claim": False,
        },
    }
    metadata_hash = write_json_record(METADATA_DIR / "training_metadata.json", metadata)
    training_record = {
        "schema": TRAINING_RECORD_SCHEMA,
        "training_label": TRAINING_LABEL,
        "training_timestamp_utc": training_timestamp,
        "dataset_identity": dataset_identity(governed),
        "train_split_only": True,
        "normal_train_samples": len(samples),
        "class_order": list(fit.class_names),
        "backbone_identity": BACKBONE_IDENTITY,
        "selected_layer": BACKBONE_LAYER,
        "feature_dimension": config.selected_feature_dimension,
        "deterministic_seed": config.feature_subsample_seed,
        "preprocessing_contract_id": PREPROCESSING_CONTRACT_ID,
        "covariance_epsilon": config.covariance_epsilon,
        "artifact_hashes_record_sha256": artifact_hash_record_hash,
        "training_metadata_sha256": metadata_hash,
        "replay_verification_sha256": replay_hash,
        "non_claims": [
            "no inference",
            "no evaluation",
            "no benchmark",
            "no ONNX export",
            "no scientific claim",
        ],
    }
    training_record_hash = write_json_record(
        TRAINING_DIR / "training_record.json",
        training_record,
    )
    return {
        "training/training_record.json": training_record_hash,
        "training/artifact_hashes.json": artifact_hash_record_hash,
        "training/replay_verification.json": replay_hash,
        "metadata/training_metadata.json": metadata_hash,
    }


def write_evidence(
    fit: FitResult,
    config: FitConfig,
    governed: Mapping[str, object],
    samples: Sequence[TrainSample],
    record_hashes: Mapping[str, str],
    training_timestamp: str,
) -> str:
    content = f"""# Kalibra PaDiM Baseline Training Evidence v1.0

**Status:** Recorded — deterministic offline PaDiM fitting evidence only
**Date:** {datetime.now(timezone.utc).date().isoformat()}
**Scope:** C-4 PaDiM baseline training only

## Governed Dataset Identity

- Dataset: VisA governed proxy acquisition `visa-acq-v1`
- Archive SHA-256: `{governed["archive_sha256"]}`
- Files manifest SHA-256: `{governed["files_manifest_sha256"]}`
- Train split SHA-256: `{TRAIN_SPLIT_SHA256}`
- Validation split SHA-256 recorded for identity only: `{VALIDATION_SPLIT_SHA256}`
- Test split SHA-256 recorded for identity only: `{TEST_SPLIT_SHA256}`
- Provenance SHA-256: `{governed["provenance_sha256"]}`

## Train Split Only

- Training manifest consumed: `data/visa/manifests/splits/train.csv`
- Normal train samples consumed: `{len(samples)}`
- Validation samples consumed: `0`
- Test samples consumed: `0`
- Class distribution: `{class_distribution(samples)}`

## Deterministic Feature Extraction

- Backbone identity: `{BACKBONE_IDENTITY}`
- Backbone layer: `{BACKBONE_LAYER}`
- Preprocessing contract id: `{PREPROCESSING_CONTRACT_ID}`
- Full feature dimension: `{config.full_feature_dimension}`
- Selected feature dimension: `{config.selected_feature_dimension}`
- Patch grid: `{config.patch_grid}`
- Deterministic batch size: `{config.batch_size}`

## Deterministic Feature Subsampling

- Feature subsampling seed: `{config.feature_subsample_seed}`
- Selected feature indices: `{fit.feature_indices.tolist()}`

## PaDiM Fitting

- μ generated: `data/visa/derived/padim/statistics/mu_by_class.npy`
- Σ generated: `data/visa/derived/padim/covariance/covariance_by_class.npy`
- Σ^-1 generated: `data/visa/derived/padim/covariance/covariance_inverse_by_class.npy`
- Covariance regularization: `Σ + εI`
- ε: `{config.covariance_epsilon}`
- Numerical configuration: `data/visa/derived/padim/metadata/numerical_config.json`
- Training timestamp: `{training_timestamp}`

## Replay Verification

- Complete second fit executed: `true`
- Identical feature selection: `true`
- Identical feature tensors: `true`
- Identical μ: `true`
- Identical Σ^-1: `true`
- Identical hashes: `true`
- Replay record: `data/visa/derived/padim/training/replay_verification.json`

## Generated Governed Training Records

- Training record SHA-256: `{record_hashes["training/training_record.json"]}`
- Artifact hashes record SHA-256: `{record_hashes["training/artifact_hashes.json"]}`
- Training metadata SHA-256: `{record_hashes["metadata/training_metadata.json"]}`
- Replay verification SHA-256: `{record_hashes["training/replay_verification.json"]}`

## Explicit Non-Claims

- No inference was executed.
- No validation inference was executed.
- No test inference was executed.
- No evaluation was executed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, threshold, calibration, benchmark, or product metric was computed.
- No ONNX export was produced.
- No provider, preprocessing runtime, output mapping, Trust, Review, Evidence Engine, Evaluation Engine, integration, prototype UI, runtime, or architecture code was modified.
- This training record makes no scientific claim and does not state that Kalibra detects defects.
"""
    return write_governed_bytes(EVIDENCE_PATH, content.encode("utf-8"))


def run_training() -> None:
    ensure_layout()
    config = FitConfig()
    governed = verify_governed_acquisition()
    file_hashes = governed["file_hashes"]
    if not isinstance(file_hashes, Mapping):
        raise TrainingError("invalid governed file hash map")
    samples = load_train_samples(file_hashes)
    training_timestamp = training_timestamp_for_run()
    first_fit = fit_padim(samples, config)
    artifact_hashes = write_fit_artifacts(first_fit, config)
    metadata_hashes = write_metadata_records(first_fit, config, governed, samples)
    replay = replay_verify(first_fit, samples, config)
    record_hashes = write_training_records(
        first_fit,
        config,
        governed,
        samples,
        artifact_hashes,
        metadata_hashes,
        replay,
        training_timestamp,
    )
    write_evidence(first_fit, config, governed, samples, record_hashes, training_timestamp)


def verify_training() -> None:
    governed = verify_governed_acquisition()
    file_hashes = governed["file_hashes"]
    if not isinstance(file_hashes, Mapping):
        raise TrainingError("invalid governed file hash map")
    samples = load_train_samples(file_hashes)
    config = FitConfig()
    fit = fit_padim(samples, config)
    required = {
        STATISTICS_DIR / "mu_by_class.npy": npy_sha256(fit.mu),
        COVARIANCE_DIR / "covariance_inverse_by_class.npy": npy_sha256(fit.covariance_inverse),
        STATISTICS_DIR / "feature_indices.npy": npy_sha256(fit.feature_indices),
    }
    for path, expected in required.items():
        actual = acquisition.sha256_file(path)
        if actual != expected:
            raise TrainingError(f"training artifact verification failed for {path}")
    replay_record = json.loads((TRAINING_DIR / "replay_verification.json").read_text())
    if replay_record.get("status") != "passed":
        raise TrainingError("replay verification record is not passed")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="C-4 governed PaDiM baseline training")
    parser.add_argument("command", choices=("train", "verify"))
    args = parser.parse_args(argv)
    try:
        if args.command == "train":
            run_training()
        elif args.command == "verify":
            verify_training()
    except (TrainingError, acquisition.AcquisitionError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
