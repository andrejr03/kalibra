from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "padim_inference.py"
SPEC = importlib.util.spec_from_file_location("padim_inference", SCRIPT_PATH)
assert SPEC is not None
padim_inference = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = padim_inference
SPEC.loader.exec_module(padim_inference)


def test_mahalanobis_patch_distances_are_deterministic() -> None:
    selected_features = np.array([[3.0, 4.0], [1.0, 2.0]], dtype=np.float64)
    mu = np.zeros((2, 2), dtype=np.float64)
    covariance_inverse = np.stack(
        [np.eye(2, dtype=np.float64), np.eye(2, dtype=np.float64)],
        axis=0,
    )

    first = padim_inference.mahalanobis_patch_distances(
        selected_features,
        mu,
        covariance_inverse,
    )
    second = padim_inference.mahalanobis_patch_distances(
        selected_features,
        mu,
        covariance_inverse,
    )

    assert np.array_equal(first, second)
    assert np.array_equal(first, np.array([5.0, np.sqrt(5.0)], dtype=np.float64))


def test_anomaly_map_repeats_patch_distances_without_dtype_change() -> None:
    config = padim_inference.training.FitConfig(image_size=16, patch_size=8)
    patch_distances = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)

    anomaly_map = padim_inference.anomaly_map_from_patch_distances(
        patch_distances,
        config,
    )

    assert anomaly_map.dtype == np.float64
    assert anomaly_map.shape == (16, 16)
    assert np.all(anomaly_map[:8, :8] == 1.0)
    assert np.all(anomaly_map[:8, 8:] == 2.0)
    assert np.all(anomaly_map[8:, :8] == 3.0)
    assert np.all(anomaly_map[8:, 8:] == 4.0)


def test_localization_uses_maximum_anomaly_region() -> None:
    anomaly_map = np.zeros((4, 4), dtype=np.float64)
    anomaly_map[1:3, 2:4] = 7.0

    localization = padim_inference.localization_from_anomaly_map(anomaly_map)

    assert localization.localization_kind == padim_inference.LOCALIZATION_IDENTIFIER
    assert localization.label == "raw_anomaly_maximum"
    assert localization.region.x_min == 0.5
    assert localization.region.y_min == 0.25
    assert localization.region.x_max == 1.0
    assert localization.region.y_max == 0.75


def test_replay_comparison_fails_closed_on_prediction_mismatch() -> None:
    first = padim_inference.InferenceRunResult(
        sample_records=(
            padim_inference.SampleInferenceRecord(
                split="validation",
                input_id="input",
                filename="part.png",
                class_name="part",
                sample_sha256="a" * 64,
                feature_tensor_sha256="b" * 64,
                anomaly_map_sha256="c" * 64,
                prediction_sha256="d" * 64,
                predicted_raw_anomaly_measure=1.0,
                localization={"region": {"x_min": 0.0}},
                prediction_record={"prediction_id": "first"},
            ),
        ),
        output_artifact_hashes={"anomaly_maps/validation_anomaly_maps.npy": "e" * 64},
    )
    second = padim_inference.InferenceRunResult(
        sample_records=(
            padim_inference.SampleInferenceRecord(
                split="validation",
                input_id="input",
                filename="part.png",
                class_name="part",
                sample_sha256="a" * 64,
                feature_tensor_sha256="b" * 64,
                anomaly_map_sha256="c" * 64,
                prediction_sha256="f" * 64,
                predicted_raw_anomaly_measure=1.0,
                localization={"region": {"x_min": 0.0}},
                prediction_record={"prediction_id": "second"},
            ),
        ),
        output_artifact_hashes={"anomaly_maps/validation_anomaly_maps.npy": "e" * 64},
    )

    try:
        padim_inference.compare_inference_runs(first, second)
    except padim_inference.InferenceError as error:
        assert "deterministic replay mismatch" in str(error)
    else:
        raise AssertionError("comparison must fail closed on prediction mismatch")
