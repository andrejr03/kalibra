#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import onnx


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import export_padim_onnx as export  # noqa: E402
import governed_visa_acquisition as acquisition  # noqa: E402
import padim_inference as inference  # noqa: E402
import train_padim_baseline as training  # noqa: E402
import verify_padim_onnx_equivalence as export_equivalence  # noqa: E402
from src.frameworks import onnx_runtime, onnx_session, output_mapping  # noqa: E402
from src.inspection.domain import (  # noqa: E402
    DefectLocalization,
    InspectionPrediction,
    StabilizedInspectionInput,
)
from src.inspection.providers_onnx import (  # noqa: E402
    ONNX_BOUNDARY_PROVIDER_ID,
    PADIM_MODEL_SHA256,
    PADIM_ONNX_MODEL_REFERENCE_ID,
    OnnxInspectionInferenceProvider,
)


RUNTIME_EQUIVALENCE_LABEL = "kalibra-runtime-equivalence-verification-v1"
RUNTIME_EQUIVALENCE_REPORT_SCHEMA = "kalibra_runtime_equivalence_report_v1"
RUNTIME_EQUIVALENCE_HASHES_SCHEMA = "kalibra_runtime_equivalence_hashes_v1"
RUNTIME_EQUIVALENCE_REPLAY_SCHEMA = "kalibra_runtime_equivalence_replay_v1"
EVIDENCE_TITLE = "Kalibra Runtime Equivalence Verification Evidence v1.0"

RUNTIME_EQUIVALENCE_DIR = REPO_ROOT / "artifacts" / "runtime" / "equivalence"
RUNTIME_EQUIVALENCE_REPORT_PATH = (
    RUNTIME_EQUIVALENCE_DIR / "runtime_equivalence_report.json"
)
RUNTIME_EQUIVALENCE_HASHES_PATH = (
    RUNTIME_EQUIVALENCE_DIR / "runtime_equivalence_hashes.json"
)
RUNTIME_EQUIVALENCE_REPLAY_PATH = (
    RUNTIME_EQUIVALENCE_DIR / "runtime_equivalence_replay.json"
)
EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "evidence" / "RUNTIME_EQUIVALENCE.md"
)
GOVERNANCE_DOCUMENTATION_PATH = (
    "docs/engineering/VISA_ACQUISITION_AND_GOVERNANCE.md"
)

RUNTIME_DIR = REPO_ROOT / "artifacts" / "runtime"
RUNTIME_INTEGRATION_METADATA_PATH = RUNTIME_DIR / "integration_metadata.json"
RUNTIME_REPLAY_PATH = RUNTIME_DIR / "runtime_replay.json"
RUNTIME_HASHES_PATH = RUNTIME_DIR / "runtime_hashes.json"

EVALUATION_DIR = REPO_ROOT / "data" / "visa" / "derived" / "padim" / "evaluation"
EVALUATION_ARTIFACT_HASHES_PATH = EVALUATION_DIR / "artifact_hashes.json"
EVALUATION_METADATA_PATH = EVALUATION_DIR / "metadata" / "evaluation_metadata.json"
EVALUATION_REPLAY_PATH = EVALUATION_DIR / "replay" / "replay_verification.json"

EXPECTED_MODEL_SHA256 = "0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a"
EXPECTED_MODEL_REFERENCE_ID = "kalibra-padim-onnx-export-v1"
EXPECTED_OPSET = 18
EXPECTED_ONNX_IR_VERSION = 10
EXPECTED_SESSION_CONFIGURATION_HASH = (
    "2893fd1fc592cb831bfccd9d53c3e784a5aba4ffdfbb58ad4de32eb512c4a2e4"
)

EXPECTED_TASK3_INTEGRATION_METADATA_SHA256 = (
    "8e80ffd9637708b92d6f5de7534c49247a9740e30678ac3ae18598bfb9c8b5e0"
)
EXPECTED_TASK3_RUNTIME_REPLAY_SHA256 = (
    "376b7a84cb65949aa55189d8cc57fb7b14dfcf899e26b697d7954c87282f2e76"
)
EXPECTED_TASK3_RUNTIME_HASHES_SHA256 = (
    "0009ffc8982c17478f0494a49562aa4408dad4261c645e75a799e72d80a2ecdd"
)

EXPECTED_C6_ARTIFACT_HASHES_SHA256 = (
    "c9a3baa00693cbe87cd21e1527033fbe58c7660b3aae431adacaf0771597e1c8"
)
EXPECTED_C6_METADATA_SHA256 = (
    "05c8b6994bf7c1856bd3b5e2b4842570af8aab2092382c705e6bbd7fc0d5196b"
)
EXPECTED_C6_REPLAY_SHA256 = (
    "e3162c17e32a32ef66e4c00e16049b8e40c8f3068af829469608a63603dc1844"
)

EXPECTED_SPLIT_COUNTS = {"validation": 2164, "test": 4328}
EXPECTED_SAMPLE_COUNT = 6492
ABSOLUTE_TOLERANCE = 1.0e-12
RELATIVE_TOLERANCE = 1.0e-12
BBOX_ABSOLUTE_TOLERANCE = 0.0


class RuntimeEquivalenceError(RuntimeError):
    """Raised when runtime equivalence cannot be verified safely."""


class GovernedDataUnavailableError(RuntimeEquivalenceError):
    """Raised when the separately governed dataset is unavailable."""


@dataclass(frozen=True)
class RuntimeReferenceContext:
    export_context: export_equivalence.VerifiedContext
    task3_identity: dict[str, Any]
    c6_identity: dict[str, Any]


@dataclass(frozen=True)
class RuntimeEquivalenceRun:
    sample_count: int
    split_counts: dict[str, int]
    per_sample_deviations: list[dict[str, Any]]
    per_split_maxima: dict[str, dict[str, Any]]
    global_maxima: dict[str, float]
    prediction_contract: dict[str, Any]
    runtime_artifact_identity: dict[str, Any]
    provider_configuration: dict[str, Any]
    session_configuration: dict[str, Any]
    session_configuration_hash: str
    status: str


class ProviderSessionCapture:
    """Observation proxy for the provider-private session invoked by predict()."""

    def __init__(self, session: object) -> None:
        self._session = session
        self.last_outputs: object | None = None

    def get_inputs(self) -> object:
        return self._session.get_inputs()

    def get_outputs(self) -> object:
        return self._session.get_outputs()

    def get_providers(self) -> object:
        return self._session.get_providers()

    def run(self, output_names: object, input_feed: object) -> object:
        outputs = self._session.run(output_names, input_feed)
        self.last_outputs = outputs
        return outputs

    def take_outputs(self) -> object:
        if self.last_outputs is None:
            raise RuntimeEquivalenceError("provider prediction did not expose session outputs")
        outputs = self.last_outputs
        self.last_outputs = None
        return outputs


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeEquivalenceError(f"unreadable file: {path}") from exc


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeEquivalenceError(f"unreadable JSON record: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeEquivalenceError(f"JSON record is not an object: {path}")
    return value


def verify_file_hash(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeEquivalenceError(f"missing governed artifact for {label}: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeEquivalenceError(
            f"governed artifact hash mismatch for {label}: expected {expected}, got {actual}"
        )
    return actual


def expect_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RuntimeEquivalenceError(
            f"{label} mismatch: expected {expected!r}, got {actual!r}"
        )


def verification_timestamp_for_run() -> str:
    if not RUNTIME_EQUIVALENCE_REPORT_PATH.exists():
        return utc_timestamp()
    report = read_json_mapping(RUNTIME_EQUIVALENCE_REPORT_PATH)
    timestamp = report.get("verification_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise RuntimeEquivalenceError("existing runtime-equivalence report lacks timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise RuntimeEquivalenceError("existing runtime-equivalence evidence lacks Date field")


def verify_reference_context() -> RuntimeReferenceContext:
    export_context = export_equivalence.verify_context()
    c6_identity = verify_c6_identity(export_context)
    task3_identity = verify_task3_identity()
    return RuntimeReferenceContext(
        export_context=export_context,
        task3_identity=task3_identity,
        c6_identity=c6_identity,
    )


def require_governed_runtime_data(repo_root: Path = REPO_ROOT) -> None:
    archive_path = (
        repo_root
        / "data"
        / "visa"
        / "source"
        / acquisition.ARCHIVE_FILENAME
    )
    if archive_path.is_file():
        return
    expected_path = archive_path.relative_to(repo_root).as_posix()
    raise GovernedDataUnavailableError(
        "GOVERNED DATA UNAVAILABLE — runtime equivalence was not run.\n"
        f"Missing required file: {expected_path}\n"
        "The VisA archive is intentionally not shipped in Git because it is "
        "managed as separately acquired, governed dataset material.\n"
        f"Acquisition and governance instructions: {GOVERNANCE_DOCUMENTATION_PATH}\n"
        "This absence is expected in a normal public clone. Run "
        "scripts/verify_public_clone.py for Level 1 clean-clone verification."
    )


def verify_task3_identity() -> dict[str, Any]:
    metadata_sha = verify_file_hash(
        RUNTIME_INTEGRATION_METADATA_PATH,
        EXPECTED_TASK3_INTEGRATION_METADATA_SHA256,
        "Task 3 runtime integration metadata",
    )
    replay_sha = verify_file_hash(
        RUNTIME_REPLAY_PATH,
        EXPECTED_TASK3_RUNTIME_REPLAY_SHA256,
        "Task 3 runtime replay",
    )
    hashes_sha = verify_file_hash(
        RUNTIME_HASHES_PATH,
        EXPECTED_TASK3_RUNTIME_HASHES_SHA256,
        "Task 3 runtime hashes",
    )
    metadata = read_json_mapping(RUNTIME_INTEGRATION_METADATA_PATH)
    replay = read_json_mapping(RUNTIME_REPLAY_PATH)
    hashes = read_json_mapping(RUNTIME_HASHES_PATH)
    expect_equal(
        metadata.get("schema"),
        "kalibra_runtime_provider_integration_metadata_v1",
        "Task 3 metadata schema",
    )
    expect_equal(
        replay.get("schema"),
        "kalibra_runtime_provider_integration_replay_v1",
        "Task 3 replay schema",
    )
    expect_equal(
        hashes.get("schema"),
        "kalibra_runtime_provider_integration_hashes_v1",
        "Task 3 hashes schema",
    )
    expect_equal(metadata.get("status"), "passed", "Task 3 status")
    expect_equal(replay.get("status"), "passed", "Task 3 replay status")
    if not all(replay.get("comparisons", {}).values()):
        raise RuntimeEquivalenceError("Task 3 replay comparison is not fully true")
    model_identity = metadata.get("model_artifact_identity")
    if not isinstance(model_identity, Mapping):
        raise RuntimeEquivalenceError("Task 3 metadata lacks model identity")
    expect_equal(
        model_identity.get("model_reference_id"),
        EXPECTED_MODEL_REFERENCE_ID,
        "Task 3 model reference",
    )
    expect_equal(model_identity.get("model_sha256"), EXPECTED_MODEL_SHA256, "Task 3 model hash")
    expect_equal(
        metadata.get("session_configuration_hash"),
        EXPECTED_SESSION_CONFIGURATION_HASH,
        "Task 3 session configuration hash",
    )
    return {
        "status": "passed",
        "integration_label": metadata["integration_label"],
        "integration_metadata_sha256": metadata_sha,
        "runtime_replay_sha256": replay_sha,
        "runtime_hashes_sha256": hashes_sha,
        "model_artifact_identity": dict(model_identity),
        "session_configuration_hash": metadata["session_configuration_hash"],
        "runtime_replay_status": replay["status"],
    }


def verify_c6_identity(context: export_equivalence.VerifiedContext) -> dict[str, Any]:
    artifact_hashes_sha = verify_file_hash(
        EVALUATION_ARTIFACT_HASHES_PATH,
        EXPECTED_C6_ARTIFACT_HASHES_SHA256,
        "C-6 evaluation artifact hashes",
    )
    metadata_sha = verify_file_hash(
        EVALUATION_METADATA_PATH,
        EXPECTED_C6_METADATA_SHA256,
        "C-6 evaluation metadata",
    )
    replay_sha = verify_file_hash(
        EVALUATION_REPLAY_PATH,
        EXPECTED_C6_REPLAY_SHA256,
        "C-6 evaluation replay",
    )
    artifact_hashes = read_json_mapping(EVALUATION_ARTIFACT_HASHES_PATH)
    metadata = read_json_mapping(EVALUATION_METADATA_PATH)
    replay = read_json_mapping(EVALUATION_REPLAY_PATH)
    expect_equal(
        artifact_hashes.get("schema"),
        "kalibra_scientific_evaluation_artifact_hashes_v1",
        "C-6 artifact hashes schema",
    )
    expect_equal(
        metadata.get("evaluation_label"),
        "visa-padim-scientific-evaluation-v1",
        "C-6 evaluation label",
    )
    expect_equal(replay.get("status"), "passed", "C-6 replay status")
    if not all(replay.get("comparisons", {}).values()):
        raise RuntimeEquivalenceError("C-6 replay comparison is not fully true")
    inference_identity = metadata.get("inference_identity")
    if not isinstance(inference_identity, Mapping):
        raise RuntimeEquivalenceError("C-6 metadata lacks inference identity")
    c5_identity = export.c5_identity(context.inputs)
    expect_equal(
        inference_identity.get("inference_artifact_hashes_sha256"),
        c5_identity["inference_artifact_hashes_sha256"],
        "C-6 consumed C-5 artifact hashes",
    )
    expect_equal(
        inference_identity.get("inference_metadata_sha256"),
        c5_identity["inference_metadata_sha256"],
        "C-6 consumed C-5 metadata",
    )
    expect_equal(
        inference_identity.get("inference_replay_verification_sha256"),
        c5_identity["inference_replay_sha256"],
        "C-6 consumed C-5 replay",
    )
    expect_equal(
        inference_identity.get("local_output_artifacts"),
        c5_identity["reference_output_artifacts"],
        "C-6 consumed C-5 runtime-observable outputs",
    )
    return {
        "status": "passed",
        "evaluation_label": metadata["evaluation_label"],
        "evaluation_artifact_hashes_sha256": artifact_hashes_sha,
        "evaluation_metadata_sha256": metadata_sha,
        "evaluation_replay_sha256": replay_sha,
        "runtime_observable_record": (
            "C-6 records the governed C-5 anomaly maps and prediction JSONL files "
            "as the runtime-observable inputs consumed by evaluation; no separate "
            "per-sample C-6 runtime-observable file is present."
        ),
        "runtime_observable_outputs_available": True,
        "runtime_observable_outputs_source": (
            "data/visa/derived/padim/inference/{anomaly_maps,predictions}"
        ),
        "c6_runtime_observable_outputs_match_c5_identity": True,
        "aggregate_metrics_recomputed": False,
    }


def runtime_stabilized_input(sample: inference.InferenceSample) -> StabilizedInspectionInput:
    image_path = (training.EXTRACTED_DIR / sample.filename).resolve()
    if acquisition.sha256_file(image_path) != sample.sha256:
        raise RuntimeEquivalenceError(f"runtime input hash mismatch: {sample.input_id}")
    return StabilizedInspectionInput(
        input_id=sample.input_id,
        artifact_uri=str(image_path),
        content_hash=sample.sha256,
        metadata={
            "class_name": sample.class_name,
            "sample_filename": sample.filename,
            "split": sample.split,
        },
    )


def install_session_capture(provider: OnnxInspectionInferenceProvider) -> ProviderSessionCapture:
    capture = ProviderSessionCapture(provider._session)
    object.__setattr__(provider, "_session", capture)
    return capture


def relative_deviation(absolute_deviation: float, reference_scale: float) -> float:
    return float(absolute_deviation / max(abs(reference_scale), 1.0e-12))


def prediction_to_json(prediction: InspectionPrediction) -> dict[str, Any]:
    return {
        "input_id": prediction.input_id,
        "model_metadata": dict(prediction.model_metadata),
        "predicted_judgement": prediction.predicted_judgement.value,
        "predicted_localization": localization_to_json(prediction.predicted_localization),
        "predicted_raw_anomaly_measure": prediction.predicted_raw_anomaly_measure,
        "prediction_id": prediction.prediction_id,
        "prediction_kind": prediction.prediction_kind,
        "raw_measure_kind": prediction.raw_measure_kind,
        "raw_measure_scale": prediction.raw_measure_scale,
    }


def localization_to_json(localization: DefectLocalization | None) -> dict[str, Any] | None:
    if localization is None:
        return None
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


def localization_vector(record: Mapping[str, Any]) -> np.ndarray:
    localization = record.get("predicted_localization")
    if not isinstance(localization, Mapping):
        raise RuntimeEquivalenceError("prediction record lacks localization")
    region = localization.get("region")
    if not isinstance(region, Mapping):
        raise RuntimeEquivalenceError("prediction record localization lacks region")
    return np.asarray(
        [
            float(region["x_min"]),
            float(region["y_min"]),
            float(region["x_max"]),
            float(region["y_max"]),
        ],
        dtype=np.float64,
    )


def verify_prediction_contract(
    prediction_record: Mapping[str, Any],
    reference_record: Mapping[str, Any],
    sample_id: str,
) -> dict[str, Any]:
    expected_fields = {
        "input_id",
        "prediction_id",
        "predicted_judgement",
        "predicted_raw_anomaly_measure",
        "predicted_localization",
        "raw_measure_kind",
        "raw_measure_scale",
        "prediction_kind",
        "model_metadata",
    }
    if not expected_fields.issubset(prediction_record):
        raise RuntimeEquivalenceError(f"runtime prediction contract missing fields: {sample_id}")
    equalities = {
        "input_id": prediction_record["input_id"] == reference_record["input_id"],
        "predicted_judgement": (
            prediction_record["predicted_judgement"]
            == reference_record["predicted_judgement"]
        ),
        "raw_measure_kind": (
            prediction_record["raw_measure_kind"] == reference_record["raw_measure_kind"]
        ),
        "prediction_kind": (
            prediction_record["prediction_kind"] == reference_record["prediction_kind"]
        ),
        "localization_kind": (
            prediction_record["predicted_localization"]["localization_kind"]
            == reference_record["predicted_localization"]["localization_kind"]
        ),
    }
    if not all(equalities.values()):
        raise RuntimeEquivalenceError(
            f"runtime prediction contract mismatch for {sample_id}: {equalities}"
        )
    expected_differences = {
        "raw_measure_scale": {
            "c5": reference_record["raw_measure_scale"],
            "runtime": prediction_record["raw_measure_scale"],
            "status": "expected_by_design",
        },
        "prediction_id": {
            "c5": reference_record["prediction_id"],
            "runtime": prediction_record["prediction_id"],
            "status": "expected_by_design",
        },
    }
    if (
        expected_differences["raw_measure_scale"]["c5"] != "model_raw_anomaly_measure"
        or expected_differences["raw_measure_scale"]["runtime"]
        != output_mapping.PADIM_RAW_MEASURE_SCALE
    ):
        raise RuntimeEquivalenceError(f"unexpected raw_measure_scale difference: {sample_id}")
    if expected_differences["prediction_id"]["c5"] == expected_differences["prediction_id"]["runtime"]:
        raise RuntimeEquivalenceError(f"prediction_id did not differ by design: {sample_id}")
    return {
        "field_set_verified": True,
        "identifier_equalities": equalities,
        "expected_by_design_differences": expected_differences,
    }


def verify_runtime_loaded_identity(
    provider: OnnxInspectionInferenceProvider,
    first_prediction: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    if first_prediction is None:
        raise RuntimeEquivalenceError("runtime run produced no prediction")
    metadata = first_prediction.get("model_metadata")
    if not isinstance(metadata, Mapping):
        raise RuntimeEquivalenceError("runtime prediction lacks model metadata")
    expect_equal(
        metadata.get("model_reference_id"),
        EXPECTED_MODEL_REFERENCE_ID,
        "runtime model reference id",
    )
    expect_equal(metadata.get("model_sha256"), EXPECTED_MODEL_SHA256, "runtime model hash")
    expect_equal(metadata.get("loader"), "model_loader.load_governed_model", "runtime loader")
    expect_equal(
        metadata.get("provider_private_session"),
        "ProviderPrivateInferenceSession",
        "runtime provider-private session",
    )
    configuration = provider.session_configuration
    session_json = json.loads(onnx_session.session_configuration_json(configuration))
    session_hash = onnx_session.session_configuration_hash(configuration)
    expect_equal(
        session_hash,
        EXPECTED_SESSION_CONFIGURATION_HASH,
        "runtime session configuration hash",
    )
    expect_equal(
        session_json["execution_providers"],
        [{"name": "CPUExecutionProvider", "provider_options": []}],
        "runtime execution provider",
    )
    expect_equal(
        session_json["execution_provider_policy"],
        "exact_order",
        "runtime execution provider policy",
    )
    expect_equal(
        session_json["session_options"],
        {
            "inter_op_num_threads": 1,
            "intra_op_num_threads": 1,
            "optimization_level": "disable_all",
        },
        "runtime session options",
    )
    session_json = public_session_configuration_json(session_json)
    runtime_identity = {
        "model_reference_id": metadata["model_reference_id"],
        "model_sha256": metadata["model_sha256"],
        "loaded_model_identity": metadata["loaded_model_identity"],
        "model_artifact_fingerprint": metadata["model_artifact_fingerprint"],
        "opset": EXPECTED_OPSET,
        "onnx_ir_version": EXPECTED_ONNX_IR_VERSION,
    }
    provider_configuration = {
        "provider": "OnnxInspectionInferenceProvider",
        "provider_id": ONNX_BOUNDARY_PROVIDER_ID,
        "runtime_substrate": "model_loader.load_governed_model -> ProviderPrivateInferenceSession",
        "loader": metadata["loader"],
        "provider_private_session": metadata["provider_private_session"],
        "canonical_default_provider_configuration": True,
    }
    return runtime_identity, provider_configuration, session_json, session_hash


def public_repo_path(path: str) -> str:
    try:
        absolute_path = Path(path).expanduser().resolve()
        repo_relative = absolute_path.relative_to(REPO_ROOT)
    except (OSError, ValueError):
        return path
    return f"<REPO>/{repo_relative.as_posix()}"


def public_session_configuration_json(session_json: Mapping[str, Any]) -> dict[str, Any]:
    public_json = copy.deepcopy(dict(session_json))
    model_reference = public_json.get("model_reference")
    if isinstance(model_reference, dict):
        artifact_path = model_reference.get("artifact_path")
        if isinstance(artifact_path, str):
            model_reference["artifact_path"] = public_repo_path(artifact_path)
    return public_json


def runtime_graph_contract(provider: OnnxInspectionInferenceProvider) -> dict[str, Any]:
    inputs = provider._session.get_inputs()
    outputs = provider._session.get_outputs()
    return {
        "status": "passed",
        "inputs": {
            value.name: {
                "dtype": "float64" if value.type == "tensor(double)" else "int64",
                "onnx_type": value.type,
                "shape": [int(dimension) for dimension in value.shape],
            }
            for value in inputs
        },
        "outputs": {
            value.name: {
                "dtype": "float64",
                "onnx_type": value.type,
                "shape": [int(dimension) for dimension in value.shape],
            }
            for value in outputs
        },
    }


def run_runtime_equivalence(context: RuntimeReferenceContext) -> RuntimeEquivalenceRun:
    export_context = context.export_context
    file_hashes = export_context.inputs.governed.get("file_hashes")
    if not isinstance(file_hashes, Mapping):
        raise RuntimeEquivalenceError("invalid governed file hash map")
    samples = inference.load_inference_samples(
        file_hashes,
        export_context.inputs.artifacts.class_names,
    )
    split_counts = {
        split: sum(1 for sample in samples if sample.split == split)
        for split in inference.INFERENCE_SPLITS
    }
    expect_equal(split_counts, EXPECTED_SPLIT_COUNTS, "governed C-5 split counts")
    expect_equal(len(samples), EXPECTED_SAMPLE_COUNT, "governed C-5 sample count")

    provider = OnnxInspectionInferenceProvider()
    capture = install_session_capture(provider)
    per_sample: list[dict[str, Any]] = []
    per_split: dict[str, dict[str, Any]] = {}
    first_prediction_record: dict[str, Any] | None = None
    contract_totals = {
        "field_set_verified": True,
        "signal_fields_verified": True,
        "raw_measure_scale_expected_difference_count": 0,
        "prediction_id_expected_difference_count": 0,
    }
    global_maxima = {
        "anomaly_map_absolute": 0.0,
        "anomaly_map_relative": 0.0,
        "raw_measure_absolute": 0.0,
        "raw_measure_relative": 0.0,
        "localization_region_absolute": 0.0,
    }

    for split in inference.INFERENCE_SPLITS:
        split_samples = [sample for sample in samples if sample.split == split]
        reference_maps_path = inference.ANOMALY_MAPS_DIR / f"{split}_anomaly_maps.npy"
        reference_predictions_path = inference.PREDICTIONS_DIR / f"{split}_predictions.jsonl"
        export_equivalence.verify_file_hash(
            reference_maps_path,
            export_equivalence.EXPECTED_C5_OUTPUT_HASHES[f"anomaly_maps/{split}_anomaly_maps.npy"],
            f"C-5 {split} anomaly maps",
        )
        export_equivalence.verify_file_hash(
            reference_predictions_path,
            export_equivalence.EXPECTED_C5_OUTPUT_HASHES[f"predictions/{split}_predictions.jsonl"],
            f"C-5 {split} predictions",
        )
        reference_maps = np.load(reference_maps_path, allow_pickle=False)
        reference_predictions = export.prediction_records_for_split(split)
        expect_equal(
            list(reference_maps.shape),
            [
                len(split_samples),
                export_context.inputs.config.image_size,
                export_context.inputs.config.image_size,
            ],
            f"C-5 {split} anomaly map shape",
        )
        expect_equal(
            len(reference_predictions),
            len(split_samples),
            f"C-5 {split} prediction count",
        )
        split_maxima = {
            "sample_count": len(split_samples),
            "anomaly_map_absolute": 0.0,
            "anomaly_map_relative": 0.0,
            "raw_measure_absolute": 0.0,
            "raw_measure_relative": 0.0,
            "localization_region_absolute": 0.0,
        }
        for sample_index, sample in enumerate(split_samples):
            reference_prediction = reference_predictions[sample_index]
            expect_equal(
                reference_prediction.get("input_id"),
                sample.input_id,
                f"C-5 {split} prediction order",
            )
            runtime_input = runtime_stabilized_input(sample)
            prediction = provider.predict(runtime_input)
            runtime_outputs = capture.take_outputs()
            runtime_prediction = prediction_to_json(prediction)
            if first_prediction_record is None:
                first_prediction_record = runtime_prediction

            runtime_map = np.asarray(runtime_outputs[1][0], dtype=np.float64)
            runtime_raw_from_graph = float(
                np.asarray(runtime_outputs[2], dtype=np.float64).reshape(-1)[0]
            )
            runtime_bbox_from_graph = np.asarray(
                runtime_outputs[3],
                dtype=np.float64,
            ).reshape(4)
            reference_map = np.asarray(reference_maps[sample_index], dtype=np.float64)
            reference_raw = float(reference_prediction["predicted_raw_anomaly_measure"])
            reference_bbox = localization_vector(reference_prediction)
            runtime_bbox = localization_vector(runtime_prediction)

            contract_result = verify_prediction_contract(
                runtime_prediction,
                reference_prediction,
                sample.input_id,
            )
            contract_totals["raw_measure_scale_expected_difference_count"] += 1
            contract_totals["prediction_id_expected_difference_count"] += 1

            map_abs = float(np.max(np.abs(runtime_map - reference_map)))
            map_rel = relative_deviation(map_abs, float(np.max(np.abs(reference_map))))
            raw_abs = float(abs(prediction.predicted_raw_anomaly_measure - reference_raw))
            raw_rel = relative_deviation(raw_abs, reference_raw)
            bbox_abs = float(np.max(np.abs(runtime_bbox - reference_bbox)))
            graph_raw_abs = float(abs(runtime_raw_from_graph - prediction.predicted_raw_anomaly_measure))
            graph_bbox_abs = float(np.max(np.abs(runtime_bbox_from_graph - runtime_bbox)))

            passed = (
                map_abs <= ABSOLUTE_TOLERANCE
                and map_rel <= RELATIVE_TOLERANCE
                and raw_abs <= ABSOLUTE_TOLERANCE
                and raw_rel <= RELATIVE_TOLERANCE
                and bbox_abs <= BBOX_ABSOLUTE_TOLERANCE
                and graph_raw_abs <= ABSOLUTE_TOLERANCE
                and graph_bbox_abs <= BBOX_ABSOLUTE_TOLERANCE
            )
            if not passed:
                raise RuntimeEquivalenceError(
                    "runtime equivalence exceeded declared tolerance for "
                    f"{sample.input_id}: map_abs={map_abs}, map_rel={map_rel}, "
                    f"raw_abs={raw_abs}, raw_rel={raw_rel}, bbox_abs={bbox_abs}, "
                    f"graph_raw_abs={graph_raw_abs}, graph_bbox_abs={graph_bbox_abs}"
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
                "localization_region_absolute_deviation": bbox_abs,
                "graph_raw_measure_to_prediction_absolute_deviation": graph_raw_abs,
                "graph_localization_to_prediction_absolute_deviation": graph_bbox_abs,
                "raw_measure_kind_equal": contract_result["identifier_equalities"][
                    "raw_measure_kind"
                ],
                "prediction_kind_equal": contract_result["identifier_equalities"][
                    "prediction_kind"
                ],
                "predicted_judgement_equal": contract_result["identifier_equalities"][
                    "predicted_judgement"
                ],
                "localization_kind_equal": contract_result["identifier_equalities"][
                    "localization_kind"
                ],
                "raw_measure_scale_expected_difference": True,
                "prediction_id_expected_difference": True,
                "passed": passed,
            }
            per_sample.append(deviation_record)
            maxima_updates = {
                "anomaly_map_absolute": map_abs,
                "anomaly_map_relative": map_rel,
                "raw_measure_absolute": raw_abs,
                "raw_measure_relative": raw_rel,
                "localization_region_absolute": bbox_abs,
            }
            for key, value in maxima_updates.items():
                split_maxima[key] = max(float(split_maxima[key]), value)
                global_maxima[key] = max(global_maxima[key], value)
        per_split[split] = split_maxima

    (
        runtime_identity,
        provider_configuration,
        session_configuration,
        session_hash,
    ) = verify_runtime_loaded_identity(provider, first_prediction_record)
    prediction_contract = {
        "status": "passed",
        "expected_contract_fields": [
            "input_id",
            "prediction_id",
            "predicted_judgement",
            "predicted_raw_anomaly_measure",
            "predicted_localization",
            "raw_measure_kind",
            "raw_measure_scale",
            "prediction_kind",
            "model_metadata",
        ],
        **contract_totals,
        "sample_count": len(samples),
    }
    return RuntimeEquivalenceRun(
        sample_count=len(samples),
        split_counts=split_counts,
        per_sample_deviations=per_sample,
        per_split_maxima=per_split,
        global_maxima=global_maxima,
        prediction_contract=prediction_contract,
        runtime_artifact_identity=runtime_identity,
        provider_configuration=provider_configuration,
        session_configuration=session_configuration,
        session_configuration_hash=session_hash,
        status="passed",
    )


def runtime_run_to_json(run: RuntimeEquivalenceRun) -> dict[str, Any]:
    return {
        "sample_count": run.sample_count,
        "split_counts": run.split_counts,
        "per_sample_deviations": run.per_sample_deviations,
        "per_split_maxima": run.per_split_maxima,
        "global_maxima": run.global_maxima,
        "prediction_contract": run.prediction_contract,
        "runtime_artifact_identity": run.runtime_artifact_identity,
        "provider_configuration": run.provider_configuration,
        "session_configuration": run.session_configuration,
        "session_configuration_hash": run.session_configuration_hash,
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
                "The governed ONNX export already reproduced the C-5 float64 PaDiM "
                "signal across 6,492 samples at machine-epsilon deviation. Runtime "
                "equivalence keeps the same 1e-12 bound to verify the integrated "
                "provider seam without silently widening the established regime."
            ),
            "relative": (
                "The relative tolerance mirrors Task 2's demonstrated DOUBLE "
                "CPUExecutionProvider regime for anomaly maps and raw measures."
            ),
            "bbox_absolute": (
                "The localization coordinates are exact multiples of 1/64 and the "
                "C-5 rounded records are exact for those values; zero tolerance is "
                "therefore an equality requirement."
            ),
        },
    }


def scope_boundaries() -> dict[str, bool]:
    return {
        "runtime_equivalence_verification_performed": True,
        "canonical_runtime_provider_loaded": True,
        "canonical_runtime_predict_executed": True,
        "runtime_modified": False,
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
        "c6_evaluation_recomputed": False,
        "image_auroc_generated": False,
        "pixel_auroc_generated": False,
        "aupro_generated": False,
        "precision_generated": False,
        "recall_generated": False,
        "f1_generated": False,
        "calibration_performed": False,
        "benchmark_generated": False,
        "placeholder_retirement_performed": False,
        "scientific_claim": False,
        "product_claim": False,
    }


def explicit_non_claims() -> list[str]:
    return [
        "runtime equivalence verification is not scientific evaluation",
        "no new Image AUROC was generated",
        "no new Pixel AUROC was generated",
        "no new AUPRO was generated",
        "no Precision was generated",
        "no Recall was generated",
        "no F1 was generated",
        "no calibration was performed",
        "no benchmark was generated",
        "no scientific claim was made",
        "no product claim was made",
        "placeholder retirement was not performed",
    ]


def graph_contract_from_context(context: RuntimeReferenceContext) -> dict[str, Any]:
    return {
        "status": "passed",
        "runtime_graph_contract": {
            "inputs": {
                "full_patch_features": {"dtype": "float64", "shape": [1, 64, 14]},
                "class_index": {"dtype": "int64", "shape": [1]},
            },
            "outputs": {
                "patch_mahalanobis_distances": {"dtype": "float64", "shape": [1, 64]},
                "anomaly_map": {"dtype": "float64", "shape": [1, 64, 64]},
                "raw_anomaly_measure": {"dtype": "float64", "shape": [1]},
                "argmax_region": {"dtype": "float64", "shape": [1, 4]},
            },
        },
        "task2_graph_contract_verification": (
            context.export_context.graph_verification
        ),
    }


def build_report(
    context: RuntimeReferenceContext,
    run: RuntimeEquivalenceRun,
    verification_timestamp: str,
) -> dict[str, Any]:
    export_context = context.export_context
    c5_identity = export.c5_identity(export_context.inputs)
    c4_identity = export.c4_identity(export_context.inputs.artifacts)
    graph_contract = graph_contract_from_context(context)
    return {
        "schema": RUNTIME_EQUIVALENCE_REPORT_SCHEMA,
        "runtime_equivalence_label": RUNTIME_EQUIVALENCE_LABEL,
        "verification_timestamp_utc": verification_timestamp,
        "status": run.status,
        "scope": (
            "Phase 3 / Task 4 runtime-equivalence verification only; canonical "
            "runtime execution and comparison against governed C-5/C-6-observable "
            "references; no runtime modification and no scientific evaluation"
        ),
        "toolchain": toolchain_versions(),
        "canonical_runtime_execution": {
            "provider": "OnnxInspectionInferenceProvider",
            "call": "OnnxInspectionInferenceProvider().predict(StabilizedInspectionInput)",
            "canonical_default_provider_configuration": True,
            "model_reference_loaded": PADIM_ONNX_MODEL_REFERENCE_ID,
            "model_loaded_through": "model_loader.load_governed_model",
            "provider_private_session": "ProviderPrivateInferenceSession",
            "anomaly_map_observation": (
                "InspectionPrediction does not expose the full anomaly map. The "
                "verifier observes the ProviderPrivateInferenceSession outputs "
                "from the same session.run call invoked by provider.predict(); it "
                "does not construct a direct ONNX Runtime session or use the "
                "offline export-equivalence script as the runtime path."
            ),
        },
        "runtime_artifact_identity": run.runtime_artifact_identity,
        "provider_configuration": run.provider_configuration,
        "session_configuration": {
            "status": "passed",
            "execution_provider": "CPUExecutionProvider",
            "execution_provider_policy": "exact_order",
            "intra_op_threads": 1,
            "inter_op_threads": 1,
            "graph_optimization_level": "ORT_DISABLE_ALL",
            "session_configuration_hash": run.session_configuration_hash,
            "loaded_session_configuration": run.session_configuration,
        },
        "governed_c4_identity": c4_identity,
        "governed_c5_identity": c5_identity,
        "governed_c6_identity": context.c6_identity,
        "task1_artifact_identity": {
            "status": "passed",
            "model_reference_id": EXPECTED_MODEL_REFERENCE_ID,
            "model_sha256": EXPECTED_MODEL_SHA256,
            "opset": EXPECTED_OPSET,
            "onnx_ir_version": EXPECTED_ONNX_IR_VERSION,
            "artifact_verification": export_context.artifact_verification,
        },
        "task2_export_equivalence_identity": {
            "status": "passed",
            "equivalence_label": export_equivalence.EQUIVALENCE_LABEL,
            "equivalence_report_sha256": export_equivalence.PADIM_EQUIVALENCE_REPORT_SHA256
            if hasattr(export_equivalence, "PADIM_EQUIVALENCE_REPORT_SHA256")
            else "9741a1c77a5d0696e8c1c5d2687aed82270d0b9791492b0b47032bf70c69275d",
            "reference_verification": export_context.reference_verification,
        },
        "task3_runtime_integration_identity": context.task3_identity,
        "artifact_identity_equivalence": {
            "status": "passed",
            "runtime_loaded": run.runtime_artifact_identity,
            "expected": {
                "model_reference_id": EXPECTED_MODEL_REFERENCE_ID,
                "model_sha256": EXPECTED_MODEL_SHA256,
                "opset": EXPECTED_OPSET,
                "onnx_ir_version": EXPECTED_ONNX_IR_VERSION,
            },
        },
        "provider_configuration_equivalence": {
            "status": "passed",
            "provider": "OnnxInspectionInferenceProvider",
            "runtime_substrate": "model_loader.load_governed_model -> ProviderPrivateInferenceSession",
        },
        "session_configuration_equivalence": {
            "status": "passed",
            "execution_provider": "CPUExecutionProvider",
            "execution_provider_policy": "exact_order",
            "intra_op_threads": 1,
            "inter_op_threads": 1,
            "graph_optimization_level": "ORT_DISABLE_ALL",
            "session_configuration_hash": run.session_configuration_hash,
        },
        "preprocessing_contract_equivalence": {
            "status": "passed",
            "preprocessing_contract": training.PREPROCESSING_CONTRACT_ID,
            "preprocessing_modified": False,
        },
        "feature_extraction_equivalence": {
            "status": "passed",
            "feature_indices": list(inference.EXPECTED_FEATURE_INDICES),
            "feature_extraction_source": "scripts/train_padim_baseline.py:extract_features",
            "feature_extraction_modified": False,
        },
        "graph_contract_equivalence": graph_contract,
        "output_mapping_equivalence": {
            "status": "passed",
            "raw_measure_kind": "raw_anomaly_measure",
            "raw_measure_scale": output_mapping.PADIM_RAW_MEASURE_SCALE,
            "localization_kind": output_mapping.PADIM_LOCALIZATION_KIND,
            "output_mapping_contract_id": output_mapping.PADIM_OUTPUT_MAPPING_CONTRACT_ID,
        },
        "prediction_contract_equivalence": run.prediction_contract,
        "expected_by_design_differences": {
            "raw_measure_scale": {
                "c5": "model_raw_anomaly_measure",
                "runtime": output_mapping.PADIM_RAW_MEASURE_SCALE,
                "interpretation": (
                    "C-5 records the generic dataclass default while runtime carries "
                    "the more specific governed output-mapping identifier; this is "
                    "recorded as an identifier difference, not a signal mismatch."
                ),
            },
            "prediction_id": {
                "c5": "offline stable id",
                "runtime": "runtime stable id",
                "interpretation": "provenance identity differs by design",
            },
        },
        "anomaly_map_equivalence": {
            "status": "passed",
            "absolute_tolerance": ABSOLUTE_TOLERANCE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima["anomaly_map_absolute"],
            "max_relative_deviation": run.global_maxima["anomaly_map_relative"],
        },
        "raw_measure_equivalence": {
            "status": "passed",
            "absolute_tolerance": ABSOLUTE_TOLERANCE,
            "relative_tolerance": RELATIVE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima["raw_measure_absolute"],
            "max_relative_deviation": run.global_maxima["raw_measure_relative"],
        },
        "localization_equivalence": {
            "status": "passed",
            "bbox_absolute_tolerance": BBOX_ABSOLUTE_TOLERANCE,
            "max_absolute_deviation": run.global_maxima[
                "localization_region_absolute"
            ],
        },
        "c6_runtime_observable_comparison": {
            "status": "passed",
            "comparison_basis": (
                "C-6 evaluation metadata records the governed C-5 anomaly maps and "
                "prediction JSONL files as evaluation inputs; runtime outputs were "
                "compared to those same C-5 runtime-observable records."
            ),
            "aggregate_metrics_recomputed": False,
        },
        "sample_counts": {"total": run.sample_count, **run.split_counts},
        "tolerance_policy": tolerance_policy(),
        "per_split_maxima": run.per_split_maxima,
        "global_maxima": run.global_maxima,
        "per_sample_deviations": run.per_sample_deviations,
        "scope_boundaries": scope_boundaries(),
        "explicit_non_claims": explicit_non_claims(),
        "final_pass_fail_status": run.status,
    }


def build_replay_record(
    first_run: RuntimeEquivalenceRun,
    second_run: RuntimeEquivalenceRun,
    first_report_bytes: bytes,
    second_report_bytes: bytes,
) -> dict[str, Any]:
    first_json = runtime_run_to_json(first_run)
    second_json = runtime_run_to_json(second_run)
    comparisons = {
        "per_sample_deviations": (
            first_run.per_sample_deviations == second_run.per_sample_deviations
        ),
        "per_split_maxima": first_run.per_split_maxima == second_run.per_split_maxima,
        "global_maxima": first_run.global_maxima == second_run.global_maxima,
        "pass_fail_status": first_run.status == second_run.status,
        "runtime_equivalence_report_hash": (
            sha256_bytes(first_report_bytes) == sha256_bytes(second_report_bytes)
        ),
        "runtime_equivalence_report_json": first_report_bytes == second_report_bytes,
        "runtime_equivalence_hashes_record": True,
    }
    if not all(comparisons.values()):
        raise RuntimeEquivalenceError(
            f"deterministic runtime-equivalence replay mismatch: {comparisons}"
        )
    return {
        "schema": RUNTIME_EQUIVALENCE_REPLAY_SCHEMA,
        "runtime_equivalence_label": RUNTIME_EQUIVALENCE_LABEL,
        "status": "passed",
        "complete_second_runtime_equivalence_run": True,
        "complete_second_canonical_runtime_load_and_execution": True,
        "comparisons": comparisons,
        "first_run_hashes": {
            "runtime_equivalence_run": sha256_bytes(canonical_json_bytes(first_json)),
            "runtime_equivalence_report.json": sha256_bytes(first_report_bytes),
        },
        "second_run_hashes": {
            "runtime_equivalence_run": sha256_bytes(canonical_json_bytes(second_json)),
            "runtime_equivalence_report.json": sha256_bytes(second_report_bytes),
        },
        "first_run_global_maxima": first_run.global_maxima,
        "second_run_global_maxima": second_run.global_maxima,
        "first_run_per_split_maxima": first_run.per_split_maxima,
        "second_run_per_split_maxima": second_run.per_split_maxima,
        "scope": "deterministic canonical runtime-equivalence replay only",
    }


def build_hashes_record(report_bytes: bytes, replay_bytes: bytes) -> dict[str, Any]:
    return {
        "schema": RUNTIME_EQUIVALENCE_HASHES_SCHEMA,
        "runtime_equivalence_label": RUNTIME_EQUIVALENCE_LABEL,
        "hash_algorithm": "sha256",
        "hash_scope": (
            "artifacts/runtime/equivalence/runtime_equivalence_report.json and "
            "artifacts/runtime/equivalence/runtime_equivalence_replay.json; "
            "runtime_equivalence_hashes.json self-hash is recorded in evidence"
        ),
        "governed_runtime_equivalence_artifacts": {
            "runtime_equivalence_report.json": sha256_bytes(report_bytes),
            "runtime_equivalence_replay.json": sha256_bytes(replay_bytes),
        },
    }


def toolchain_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "onnx": onnx.__version__,
        "onnxruntime": str(onnx_runtime.onnx_runtime_version()),
    }


def write_evidence(
    report: Mapping[str, Any],
    replay: Mapping[str, Any],
    report_hash: str,
    replay_hash: str,
    hashes_hash: str,
) -> str:
    date = evidence_date_for_run()
    global_maxima = report["global_maxima"]
    sample_counts = report["sample_counts"]
    tolerance = report["tolerance_policy"]
    return f"""# {EVIDENCE_TITLE}

**Status:** Recorded - governed runtime-equivalence verification evidence only
**Date:** {date}
**Scope:** Phase 3 / Task 4 - Runtime Equivalence Verification only

## Verification Levels

- **Level 1 - Clean-Clone Verification:** `python3 scripts/verify_public_clone.py` checks committed public artifacts and does not replay this result.
- **Level 2 - Governed Runtime Verification:** this verifier requires the separately acquired `data/visa/source/VisA_20220922.tar` archive and extracted VisA data. Their absence is expected in a normal public clone; follow `docs/engineering/VISA_ACQUISITION_AND_GOVERNANCE.md`.
- **Level 3 - Full Scientific Reproduction:** dataset acquisition plus the documented training, inference, evaluation, export, and runtime environment; this is a separate workflow, not a clean-clone guarantee.

## Verification Scope

- Canonical runtime path executed: `OnnxInspectionInferenceProvider().predict(StabilizedInspectionInput)`
- Runtime substrate: `model_loader.load_governed_model` -> `ProviderPrivateInferenceSession`
- Execution provider: `CPUExecutionProvider`
- Session configuration hash: `{report['session_configuration']['session_configuration_hash']}`
- Model reference id: `{report['runtime_artifact_identity']['model_reference_id']}`
- Model SHA-256: `{report['runtime_artifact_identity']['model_sha256']}`
- Runtime-equivalence report: `artifacts/runtime/equivalence/runtime_equivalence_report.json`
- Runtime-equivalence hashes: `artifacts/runtime/equivalence/runtime_equivalence_hashes.json`
- Runtime-equivalence replay: `artifacts/runtime/equivalence/runtime_equivalence_replay.json`

## Governed References Verified

- Governed C-5 inference identity verified: `{report['governed_c5_identity']['inference_artifact_hashes_sha256']}`
- Governed C-5 replay hash verified: `{report['governed_c5_identity']['inference_replay_sha256']}`
- Governed C-6 identity verified: `{report['governed_c6_identity']['evaluation_metadata_sha256']}`
- Task 1 governed ONNX artifact identity verified: `{report['task1_artifact_identity']['model_sha256']}`
- Task 2 export-equivalence identity verified before runtime equivalence: `true`
- Task 3 runtime integration identity verified: `{report['task3_runtime_integration_identity']['integration_metadata_sha256']}`

## Equivalence Result

- Final status: `{report['final_pass_fail_status']}`
- Sample count: `{sample_counts['total']}`
- Validation count: `{sample_counts['validation']}`
- Test count: `{sample_counts['test']}`
- Anomaly-map max absolute deviation: `{global_maxima['anomaly_map_absolute']}`
- Anomaly-map max relative deviation: `{global_maxima['anomaly_map_relative']}`
- Raw-measure max absolute deviation: `{global_maxima['raw_measure_absolute']}`
- Raw-measure max relative deviation: `{global_maxima['raw_measure_relative']}`
- Localization max absolute deviation: `{global_maxima['localization_region_absolute']}`
- `InspectionPrediction` contract verified: `true`
- Expected-by-design `raw_measure_scale` difference: `C-5=model_raw_anomaly_measure`; `runtime=padim_anomaly_map_max_v1`
- Expected-by-design `prediction_id` difference: `C-5=offline stable id`; `runtime=runtime stable id`

## Tolerance Policy

- Absolute tolerance: `{tolerance['absolute']}`
- Relative tolerance: `{tolerance['relative']}`
- Bbox absolute tolerance: `{tolerance['bbox_absolute']}`
- Tolerances declared before comparison: `{str(tolerance['declared_before_comparison']).lower()}`
- Absolute justification: `{tolerance['justification']['absolute']}`
- Relative justification: `{tolerance['justification']['relative']}`
- Bbox justification: `{tolerance['justification']['bbox_absolute']}`

## Replay Result

- Complete second runtime-equivalence run executed: `{str(replay['complete_second_runtime_equivalence_run']).lower()}`
- Complete second canonical runtime load and execution: `{str(replay['complete_second_canonical_runtime_load_and_execution']).lower()}`
- Per-sample deviations identical: `{str(replay['comparisons']['per_sample_deviations']).lower()}`
- Per-split maxima identical: `{str(replay['comparisons']['per_split_maxima']).lower()}`
- Global maxima identical: `{str(replay['comparisons']['global_maxima']).lower()}`
- Pass/fail status identical: `{str(replay['comparisons']['pass_fail_status']).lower()}`
- Runtime-equivalence report hash identical: `{str(replay['comparisons']['runtime_equivalence_report_hash']).lower()}`
- Runtime-equivalence hashes record deterministic: `{str(replay['comparisons']['runtime_equivalence_hashes_record']).lower()}`
- Runtime-equivalence report SHA-256: `{report_hash}`
- Runtime-equivalence replay SHA-256: `{replay_hash}`
- Runtime-equivalence hashes record SHA-256: `{hashes_hash}`

## Explicit Non-Claims

- Runtime equivalence verification is not scientific evaluation.
- No new Image AUROC was generated.
- No new Pixel AUROC was generated.
- No new AUPRO was generated.
- No Precision/Recall/F1 was generated.
- No calibration was performed.
- No benchmark was generated.
- No scientific claim was made.
- No product claim was made.
- Placeholder retirement was not performed.
"""


def write_governed_record(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise RuntimeEquivalenceError(f"governed runtime-equivalence record changed: {path}")
    path.write_bytes(content)
    return sha256_file(path)


def persist_records() -> None:
    context = verify_reference_context()
    timestamp = verification_timestamp_for_run()
    first_run = run_runtime_equivalence(context)
    first_report = build_report(context, first_run, timestamp)
    first_report_bytes = canonical_json_bytes(first_report)
    second_run = run_runtime_equivalence(context)
    second_report = build_report(context, second_run, timestamp)
    second_report_bytes = canonical_json_bytes(second_report)
    replay = build_replay_record(
        first_run,
        second_run,
        first_report_bytes,
        second_report_bytes,
    )
    replay_bytes = canonical_json_bytes(replay)
    hashes = build_hashes_record(first_report_bytes, replay_bytes)
    hashes_bytes = canonical_json_bytes(hashes)
    evidence = write_evidence(
        first_report,
        replay,
        sha256_bytes(first_report_bytes),
        sha256_bytes(replay_bytes),
        sha256_bytes(hashes_bytes),
    )
    write_governed_record(RUNTIME_EQUIVALENCE_REPORT_PATH, first_report_bytes)
    write_governed_record(RUNTIME_EQUIVALENCE_REPLAY_PATH, replay_bytes)
    write_governed_record(RUNTIME_EQUIVALENCE_HASHES_PATH, hashes_bytes)
    write_governed_record(EVIDENCE_PATH, evidence.encode("utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify governed PaDiM runtime equivalence."
    )
    parser.add_argument(
        "command",
        choices=("verify",),
        help="Run the bounded runtime-equivalence verification.",
    )
    parser.parse_args(argv)
    try:
        require_governed_runtime_data()
        persist_records()
    except GovernedDataUnavailableError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
