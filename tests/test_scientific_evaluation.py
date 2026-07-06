from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "scientific_evaluation.py"
SPEC = importlib.util.spec_from_file_location("scientific_evaluation", SCRIPT_PATH)
assert SPEC is not None
scientific_evaluation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = scientific_evaluation
SPEC.loader.exec_module(scientific_evaluation)


def test_binary_auroc_uses_average_ranks_for_ties() -> None:
    labels = np.array([0, 1, 1, 0], dtype=np.int8)
    scores = np.array([0.1, 0.2, 0.2, 0.4], dtype=np.float64)

    auc = scientific_evaluation.binary_auroc(labels, scores)

    assert auc == 0.5


def test_operating_point_balances_validation_error_rates() -> None:
    observations = [
        observation("normal-1", "normal", 0.10),
        observation("normal-2", "normal", 0.20),
        observation("normal-3", "normal", 0.90),
        observation("anomaly-1", "anomaly", 0.30),
        observation("anomaly-2", "anomaly", 0.80),
        observation("anomaly-3", "anomaly", 0.95),
    ]

    record = scientific_evaluation.derive_operating_point(observations)

    assert record["rule_id"] == "validation_balanced_fpr_fnr_v1"
    assert record["validation_derived_value"] == 0.8
    assert record["validation_confusion"] == {
        "true_positive": 2,
        "false_positive": 1,
        "true_negative": 2,
        "false_negative": 1,
    }
    assert record["diagnostic_only"] is True
    assert record["not_calibrated"] is True
    assert record["not_product_threshold"] is True


def test_aupro_scores_perfect_single_region_localization() -> None:
    maps = np.zeros((1, 4, 4), dtype=np.float64)
    masks = np.zeros((1, 4, 4), dtype=bool)
    maps[0, 1:3, 1:3] = 1.0
    masks[0, 1:3, 1:3] = True

    original_size = scientific_evaluation.MASK_SIZE
    scientific_evaluation.MASK_SIZE = 4
    try:
        score = scientific_evaluation.aupro_score(maps, masks)
    finally:
        scientific_evaluation.MASK_SIZE = original_size

    assert score == 1.0


def test_downsample_binary_mask_preserves_tiny_positive_region() -> None:
    mask = np.zeros((1284, 1168), dtype=bool)
    mask[777, 901] = True

    reduced = scientific_evaluation.downsample_binary_mask(mask)

    assert reduced.shape == (64, 64)
    assert np.any(reduced)


def test_replay_record_fails_closed_on_metric_mismatch() -> None:
    first = computation({"metric": 1.0})
    second = computation({"metric": 0.0})

    try:
        scientific_evaluation.build_replay_record(first, second)
    except scientific_evaluation.EvaluationError as error:
        assert "deterministic evaluation replay mismatch" in str(error)
    else:
        raise AssertionError("replay comparison must fail closed")


def observation(input_id: str, label: str, score: float):
    sample = scientific_evaluation.EvaluationSample(
        split="validation",
        input_id=input_id,
        filename=f"{input_id}.JPG",
        class_name="part",
        label=label,
        sample_sha256="a" * 64,
        mask_filename=None if label == "normal" else f"{input_id}.png",
        mask_sha256=None if label == "normal" else "b" * 64,
    )
    return scientific_evaluation.EvaluationObservation(
        sample=sample,
        score=score,
        localization={"region": {"x_min": 0.0, "y_min": 0.0, "x_max": 1.0, "y_max": 1.0}},
        prediction_record={"input_id": input_id},
        anomaly_map=np.zeros((64, 64), dtype=np.float64),
    )


def computation(metrics: dict[str, float]):
    return scientific_evaluation.EvaluationComputation(
        records={"metrics/official_metrics.json": scientific_evaluation.canonical_json_bytes(metrics)},
        evidence_content=scientific_evaluation.canonical_json_bytes({"evidence": metrics}),
        official_metrics=metrics,
        diagnostic_metrics={},
        operating_point={},
        failure_analysis={},
        per_class={},
        metadata={},
    )
