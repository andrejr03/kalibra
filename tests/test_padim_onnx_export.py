from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "export_padim_onnx.py"
SPEC = importlib.util.spec_from_file_location("export_padim_onnx", SCRIPT_PATH)
assert SPEC is not None
padim_export = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = padim_export
SPEC.loader.exec_module(padim_export)


def test_export_graph_computes_mahalanobis_map_and_argmax_region() -> None:
    class_names = tuple(f"class_{index}" for index in range(12))
    mu = np.zeros((12, 64, 8), dtype=np.float64)
    covariance_inverse = np.repeat(
        np.eye(8, dtype=np.float64).reshape(1, 1, 8, 8),
        12 * 64,
        axis=0,
    ).reshape(12, 64, 8, 8)
    feature_indices = np.array(padim_export.inference.EXPECTED_FEATURE_INDICES, dtype=np.int64)
    artifacts = padim_export.inference.GovernedArtifacts(
        class_names=class_names,
        mu=mu,
        covariance_inverse=covariance_inverse,
        feature_indices=feature_indices,
        dataset_identity={},
        preprocessing_contract={},
        backbone_metadata={},
        numerical_config={},
        feature_indices_metadata={},
        training_metadata={},
        training_record={"training_label": "fixture"},
        training_artifact_hashes={},
        training_replay_record={},
        artifact_identity={},
    )
    model_bytes = padim_export.build_onnx_model_bytes(artifacts)
    session = ort.InferenceSession(
        model_bytes,
        sess_options=padim_export.session_options(),
        providers=["CPUExecutionProvider"],
    )
    full_features = np.zeros((1, 64, 14), dtype=np.float64)
    full_features[0, 10, feature_indices] = 1.0

    outputs = session.run(
        [
            padim_export.OUTPUT_PATCH_DISTANCES,
            padim_export.OUTPUT_ANOMALY_MAP,
            padim_export.OUTPUT_RAW_MEASURE,
            padim_export.OUTPUT_ARGMAX_REGION,
        ],
        {
            padim_export.INPUT_FULL_PATCH_FEATURES: full_features,
            padim_export.INPUT_CLASS_INDEX: np.array([0], dtype=np.int64),
        },
    )

    assert outputs[0].shape == (1, 64)
    assert np.isclose(outputs[0][0, 10], np.sqrt(8.0))
    assert outputs[1].shape == (1, 64, 64)
    assert np.isclose(outputs[2][0], np.sqrt(8.0))
    assert np.array_equal(
        outputs[3],
        np.array([[0.25, 0.125, 0.375, 0.25]], dtype=np.float64),
    )


def test_replay_record_fails_closed_on_model_byte_mismatch() -> None:
    first = padim_export.ExportBuild(
        model_bytes=b"first",
        artifact_record={"a": 1},
        metadata_record={"m": 1},
        artifact_bytes=b"artifact",
        metadata_bytes=b"metadata",
    )
    second = padim_export.ExportBuild(
        model_bytes=b"second",
        artifact_record={"a": 1},
        metadata_record={"m": 1},
        artifact_bytes=b"artifact",
        metadata_bytes=b"metadata",
    )

    try:
        padim_export.build_replay_record(first, second)
    except padim_export.ExportError as error:
        assert "deterministic ONNX export replay mismatch" in str(error)
    else:
        raise AssertionError("replay must fail closed on ONNX byte mismatch")
