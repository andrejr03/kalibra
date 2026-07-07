from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "verify_padim_onnx_equivalence.py"
)
SPEC = importlib.util.spec_from_file_location("verify_padim_onnx_equivalence", SCRIPT_PATH)
assert SPEC is not None
padim_equivalence = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = padim_equivalence
SPEC.loader.exec_module(padim_equivalence)


def fixture_artifacts() -> object:
    class_names = tuple(f"class_{index}" for index in range(12))
    mu = np.zeros((12, 64, 8), dtype=np.float64)
    covariance_inverse = np.repeat(
        np.eye(8, dtype=np.float64).reshape(1, 1, 8, 8),
        12 * 64,
        axis=0,
    ).reshape(12, 64, 8, 8)
    feature_indices = np.array(
        padim_equivalence.inference.EXPECTED_FEATURE_INDICES,
        dtype=np.int64,
    )
    return padim_equivalence.inference.GovernedArtifacts(
        class_names=class_names,
        mu=mu,
        covariance_inverse=covariance_inverse,
        feature_indices=feature_indices,
        dataset_identity={},
        preprocessing_contract={},
        backbone_metadata={},
        numerical_config={
            "covariance_estimator": "sample covariance, centered.T @ centered / (n - 1)",
            "covariance_regularization": "covariance + epsilon * I",
            "epsilon": 0.001,
            "inverse": "numpy.linalg.inv on regularized covariance",
        },
        feature_indices_metadata={},
        training_metadata={},
        training_record={"training_label": "fixture"},
        training_artifact_hashes={},
        training_replay_record={},
        artifact_identity={},
    )


def test_graph_contract_verifies_exported_contract_for_fixture_model() -> None:
    artifacts = fixture_artifacts()
    model_bytes = padim_equivalence.export.build_onnx_model_bytes(artifacts)
    model = padim_equivalence.onnx.load_from_string(model_bytes)
    artifact_record = {
        "graph": {
            "preprocessing_reimplemented_in_onnx": False,
        }
    }
    metadata_record = {
        "graph": {
            "preprocessing_reimplemented_in_onnx": False,
        },
        "dtype_policy": {
            "dtype_source": "float64",
            "onnx_dtype": "float64",
            "float32_transition": False,
        },
    }

    verification = padim_equivalence.verify_graph_contract(
        model,
        artifact_record,
        metadata_record,
        artifacts,
    )

    assert verification["status"] == "passed"
    assert verification["inputs"]["full_patch_features"] == {
        "dtype": "float64",
        "shape": [1, 64, 14],
    }
    assert verification["outputs"]["argmax_region"] == {
        "dtype": "float64",
        "shape": [1, 4],
    }
    assert verification["feature_indices_byte_equal_to_c4"] is True
    assert verification["mu_byte_equal_to_c4"] is True
    assert verification["covariance_inverse_byte_equal_to_c4"] is True
    assert verification["preprocessing_reimplemented_in_onnx"] is False


def test_replay_record_fails_closed_on_per_sample_mismatch() -> None:
    first_run = padim_equivalence.EquivalenceRun(
        sample_count=1,
        split_counts={"validation": 1, "test": 0},
        per_sample_deviations=[
            {
                "input_id": "sample-1",
                "anomaly_map_absolute_deviation": 0.0,
                "passed": True,
            }
        ],
        per_split_maxima={
            "validation": {
                "sample_count": 1,
                "anomaly_map_absolute": 0.0,
                "anomaly_map_relative": 0.0,
                "raw_measure_absolute": 0.0,
                "raw_measure_relative": 0.0,
                "argmax_region_absolute": 0.0,
            }
        },
        global_maxima={
            "anomaly_map_absolute": 0.0,
            "anomaly_map_relative": 0.0,
            "raw_measure_absolute": 0.0,
            "raw_measure_relative": 0.0,
            "argmax_region_absolute": 0.0,
        },
        status="passed",
    )
    second_run = padim_equivalence.EquivalenceRun(
        sample_count=1,
        split_counts={"validation": 1, "test": 0},
        per_sample_deviations=[
            {
                "input_id": "sample-1",
                "anomaly_map_absolute_deviation": 1.0e-9,
                "passed": True,
            }
        ],
        per_split_maxima=first_run.per_split_maxima,
        global_maxima=first_run.global_maxima,
        status="passed",
    )

    try:
        padim_equivalence.build_replay_record(
            first_run,
            second_run,
            b'{"report":"first"}\n',
            b'{"report":"first"}\n',
        )
    except padim_equivalence.EquivalenceError as error:
        assert "deterministic equivalence replay mismatch" in str(error)
    else:
        raise AssertionError("replay must fail closed on per-sample deviation mismatch")


def test_hashes_record_covers_report_and_replay_artifacts() -> None:
    report_bytes = b'{"schema":"report"}\n'
    replay_bytes = b'{"schema":"replay"}\n'

    hashes = padim_equivalence.build_hashes_record(report_bytes, replay_bytes)

    assert hashes["schema"] == padim_equivalence.EQUIVALENCE_HASHES_SCHEMA
    assert hashes["governed_equivalence_artifacts"] == {
        "equivalence_report.json": padim_equivalence.sha256_bytes(report_bytes),
        "equivalence_replay.json": padim_equivalence.sha256_bytes(replay_bytes),
    }
