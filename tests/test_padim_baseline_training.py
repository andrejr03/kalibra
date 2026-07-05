from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "train_padim_baseline.py"
SPEC = importlib.util.spec_from_file_location("train_padim_baseline", SCRIPT_PATH)
assert SPEC is not None
padim = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = padim
SPEC.loader.exec_module(padim)


def test_feature_subsampling_is_seeded_sorted_and_reproducible() -> None:
    first = padim.select_feature_indices(14, 8, 271828)
    second = padim.select_feature_indices(14, 8, 271828)

    assert np.array_equal(first, second)
    assert np.array_equal(first, np.sort(first))
    assert len(set(first.tolist())) == 8


def test_train_manifest_row_accepts_train_manifest_row_with_upstream_test_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = {
        "filename": "part/Data/Images/Normal/001.JPG",
        "class": "part",
        "label": "normal",
        "artifact_type": "image",
        "sha256": "a" * 64,
        "source_csv": "1cls.csv",
        "source_split": "test",
        "source_label": "normal",
        "source_image": "part/Data/Images/Normal/001.JPG",
        "source_mask": "",
    }

    image_path = tmp_path / row["filename"]
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"image")
    monkeypatch.setattr(padim, "EXTRACTED_DIR", tmp_path)
    assert padim.validate_train_row(row, {row["filename"]: row["sha256"]}) is None


def test_train_manifest_row_rejects_anomaly_sample() -> None:
    row = {
        "filename": "part/Data/Images/Anomaly/001.JPG",
        "class": "part",
        "label": "anomaly",
        "artifact_type": "image",
        "sha256": "a" * 64,
        "source_csv": "1cls.csv",
        "source_split": "train",
        "source_label": "anomaly",
        "source_image": "part/Data/Images/Anomaly/001.JPG",
        "source_mask": "part/Data/Masks/Anomaly/001.png",
    }

    with pytest.raises(padim.TrainingError):
        padim.validate_train_row(row, {row["filename"]: row["sha256"]})


def test_feature_extraction_is_deterministic(tmp_path: Path) -> None:
    image_path = tmp_path / "fixture.png"
    pixels = np.arange(16 * 16 * 3, dtype=np.uint8).reshape(16, 16, 3)
    Image.fromarray(pixels).save(image_path)
    config = padim.FitConfig(image_size=16, patch_size=8)

    first = padim.extract_features(image_path, config)
    second = padim.extract_features(image_path, config)

    assert first.shape == (4, 14)
    assert np.array_equal(first, second)


def test_class_statistics_are_reproducible_and_regularized() -> None:
    features = np.arange(5 * 4 * 4, dtype=np.float64).reshape(5, 4, 4) / 100.0

    first = padim.fit_class_statistics(features, epsilon=1.0e-3)
    second = padim.fit_class_statistics(features, epsilon=1.0e-3)

    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])
    assert np.array_equal(first[2], second[2])
    for covariance_inverse in first[2]:
        assert np.all(np.isfinite(covariance_inverse))


def test_governed_record_write_fails_when_existing_content_changes(tmp_path: Path) -> None:
    record = tmp_path / "record.json"
    padim.write_governed_bytes(record, b"first")

    with pytest.raises(padim.TrainingError):
        padim.write_governed_bytes(record, b"second")
