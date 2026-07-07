#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from src.frameworks import onnx_runtime, onnx_session, output_mapping  # noqa: E402
from src.inspection.domain import (  # noqa: E402
    DefectLocalization,
    InspectionPrediction,
    StabilizedInspectionInput,
)
from src.inspection.providers_onnx import (  # noqa: E402
    ONNX_BOUNDARY_PROVIDER_ID,
    ONNX_PLACEHOLDER_MODEL_REFERENCE_ID,
    PADIM_MODEL_SHA256,
    PADIM_ONNX_MODEL_REFERENCE_ID,
    OnnxInspectionInferenceProvider,
)


INTEGRATION_LABEL = "kalibra-runtime-provider-integration-v1"
METADATA_SCHEMA = "kalibra_runtime_provider_integration_metadata_v1"
REPLAY_SCHEMA = "kalibra_runtime_provider_integration_replay_v1"
HASHES_SCHEMA = "kalibra_runtime_provider_integration_hashes_v1"
EVIDENCE_TITLE = "Kalibra Runtime Provider Integration Evidence v1.0"
EVIDENCE_DATE = "2026-07-07"

RUNTIME_DIR = REPO_ROOT / "artifacts" / "runtime"
INTEGRATION_METADATA_PATH = RUNTIME_DIR / "integration_metadata.json"
RUNTIME_REPLAY_PATH = RUNTIME_DIR / "runtime_replay.json"
RUNTIME_HASHES_PATH = RUNTIME_DIR / "runtime_hashes.json"
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "KALIBRA_RUNTIME_PROVIDER_INTEGRATION_EVIDENCE_v1.0.md"
)
PADIM_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "padim"
PADIM_MODEL_PATH = PADIM_ARTIFACT_DIR / "model.onnx"
EQUIVALENCE_DIR = PADIM_ARTIFACT_DIR / "equivalence"
PREDICTION_RECORDS = (
    REPO_ROOT
    / "data"
    / "visa"
    / "derived"
    / "padim"
    / "inference"
    / "predictions"
)
REPRESENTATIVE_RECORDS = (
    PREDICTION_RECORDS / "validation_predictions.jsonl",
    PREDICTION_RECORDS / "test_predictions.jsonl",
)


class RuntimeIntegrationError(RuntimeError):
    """Raised when runtime provider integration replay cannot be governed."""


@dataclass(frozen=True)
class RepresentativeInput:
    split: str
    input_id: str
    artifact_uri: str
    content_hash: str
    class_name: str
    sample_filename: str

    def to_stabilized_input(self) -> StabilizedInspectionInput:
        return StabilizedInspectionInput(
            input_id=self.input_id,
            artifact_uri=self.artifact_uri,
            content_hash=self.content_hash,
            metadata={
                "class_name": self.class_name,
                "sample_filename": self.sample_filename,
                "split": self.split,
            },
        )

    def to_json_dict(self) -> dict[str, str]:
        return {
            "artifact_uri": self.artifact_uri,
            "class_name": self.class_name,
            "content_hash": self.content_hash,
            "input_id": self.input_id,
            "sample_filename": self.sample_filename,
            "split": self.split,
        }


@dataclass(frozen=True)
class RuntimeRun:
    artifact_identity: dict[str, str]
    session_configuration: dict[str, Any]
    session_configuration_hash: str
    provider_configuration: dict[str, str]
    predictions: tuple[dict[str, Any], ...]

    def comparable_payload(self) -> dict[str, Any]:
        return {
            "artifact_identity": self.artifact_identity,
            "predictions": list(self.predictions),
            "provider_configuration": self.provider_configuration,
            "session_configuration": self.session_configuration,
            "session_configuration_hash": self.session_configuration_hash,
        }


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(content: bytes) -> str:
    return sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeIntegrationError(f"unreadable file: {path}") from exc


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeIntegrationError(f"unreadable JSON record: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeIntegrationError(f"JSON record is not an object: {path}")
    return value


def read_first_json_line(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as file:
            line = file.readline()
    except OSError as exc:
        raise RuntimeIntegrationError(f"unreadable prediction record: {path}") from exc
    if not line:
        raise RuntimeIntegrationError(f"empty prediction record: {path}")
    value = json.loads(line)
    if not isinstance(value, dict):
        raise RuntimeIntegrationError(f"prediction line is not an object: {path}")
    return value


def load_representative_inputs() -> tuple[RepresentativeInput, ...]:
    inputs: list[RepresentativeInput] = []
    for record_path in REPRESENTATIVE_RECORDS:
        record = read_first_json_line(record_path)
        metadata = record.get("model_metadata")
        if not isinstance(metadata, Mapping):
            raise RuntimeIntegrationError("prediction record lacks model metadata")
        sample_filename = _required_string(metadata, "sample_filename")
        image_path = (REPO_ROOT / "data" / "visa" / "extracted" / sample_filename).resolve()
        sample_sha256 = _required_string(metadata, "sample_sha256")
        if sha256_file(image_path) != sample_sha256:
            raise RuntimeIntegrationError("representative input hash mismatch")
        inputs.append(
            RepresentativeInput(
                split=_required_string(metadata, "split"),
                input_id=_required_string(record, "input_id"),
                artifact_uri=str(image_path),
                content_hash=sample_sha256,
                class_name=_required_string(metadata, "class_name"),
                sample_filename=sample_filename,
            )
        )
    return tuple(inputs)


def execute_runtime_run(samples: Sequence[RepresentativeInput]) -> RuntimeRun:
    provider = OnnxInspectionInferenceProvider()
    predictions: list[dict[str, Any]] = []
    artifact_identity: dict[str, str] | None = None
    provider_configuration: dict[str, str] | None = None
    for sample in samples:
        prediction = provider.predict(sample.to_stabilized_input())
        prediction_record = prediction_to_json(prediction)
        predictions.append(prediction_record)
        metadata = dict(prediction.model_metadata)
        artifact_identity = {
            "loaded_model_identity": metadata["loaded_model_identity"],
            "model_artifact_fingerprint": metadata["model_artifact_fingerprint"],
            "model_reference_id": metadata["model_reference_id"],
            "model_sha256": metadata["model_sha256"],
        }
        provider_configuration = {
            "loader": metadata["loader"],
            "method": metadata["method"],
            "model_kind": metadata["model_kind"],
            "provider_id": ONNX_BOUNDARY_PROVIDER_ID,
            "provider_private_session": metadata["provider_private_session"],
        }
    if artifact_identity is None or provider_configuration is None:
        raise RuntimeIntegrationError("runtime run produced no predictions")

    configuration = provider.session_configuration
    return RuntimeRun(
        artifact_identity=artifact_identity,
        session_configuration=json.loads(
            onnx_session.session_configuration_json(configuration)
        ),
        session_configuration_hash=onnx_session.session_configuration_hash(
            configuration
        ),
        provider_configuration=provider_configuration,
        predictions=tuple(predictions),
    )


def prediction_to_json(prediction: InspectionPrediction) -> dict[str, Any]:
    localization = localization_to_json(prediction.predicted_localization)
    record = {
        "input_id": prediction.input_id,
        "model_metadata": dict(prediction.model_metadata),
        "predicted_judgement": prediction.predicted_judgement.value,
        "predicted_localization": localization,
        "predicted_raw_anomaly_measure": prediction.predicted_raw_anomaly_measure,
        "prediction_id": prediction.prediction_id,
        "prediction_kind": prediction.prediction_kind,
        "raw_measure_kind": prediction.raw_measure_kind,
        "raw_measure_scale": prediction.raw_measure_scale,
    }
    record["prediction_sha256"] = sha256_bytes(canonical_json_bytes(record))
    return record


def localization_to_json(localization: DefectLocalization | None) -> dict[str, Any] | None:
    if localization is None:
        return None
    return {
        "label": localization.label,
        "localization_kind": localization.localization_kind,
        "region": {
            "x_max": localization.region.x_max,
            "x_min": localization.region.x_min,
            "y_max": localization.region.y_max,
            "y_min": localization.region.y_min,
        },
    }


def build_records() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    samples = load_representative_inputs()
    first_run = execute_runtime_run(samples)
    second_run = execute_runtime_run(samples)
    first_payload = first_run.comparable_payload()
    second_payload = second_run.comparable_payload()
    first_run_hash = sha256_bytes(canonical_json_bytes(first_payload))
    second_run_hash = sha256_bytes(canonical_json_bytes(second_payload))
    comparisons = replay_comparisons(first_run, second_run, first_run_hash, second_run_hash)
    replay_status = "passed" if all(comparisons.values()) else "failed"

    replay_record = {
        "comparisons": comparisons,
        "complete_second_load_and_execution": True,
        "first_run": first_payload,
        "first_run_hash": first_run_hash,
        "integration_label": INTEGRATION_LABEL,
        "representative_inputs": [sample.to_json_dict() for sample in samples],
        "runtime_equivalence_verification_performed": False,
        "schema": REPLAY_SCHEMA,
        "scope": (
            "runtime provider integration replay only; no comparison against C-5 "
            "or C-6 reference outputs"
        ),
        "second_run": second_payload,
        "second_run_hash": second_run_hash,
        "status": replay_status,
    }
    metadata_record = integration_metadata_record(
        samples=samples,
        first_run=first_run,
        replay_status=replay_status,
        replay_comparisons=comparisons,
    )
    metadata_hash = sha256_bytes(canonical_json_bytes(metadata_record))
    replay_hash = sha256_bytes(canonical_json_bytes(replay_record))
    hashes_record = {
        "governed_runtime_artifacts": {
            "integration_metadata.json": metadata_hash,
            "runtime_replay.json": replay_hash,
        },
        "hash_algorithm": "sha256",
        "hash_scope": (
            "artifacts/runtime/integration_metadata.json and "
            "artifacts/runtime/runtime_replay.json"
        ),
        "integration_label": INTEGRATION_LABEL,
        "schema": HASHES_SCHEMA,
    }
    evidence = evidence_markdown(metadata_record, replay_record, hashes_record)
    return metadata_record, replay_record, hashes_record, evidence


def replay_comparisons(
    first_run: RuntimeRun,
    second_run: RuntimeRun,
    first_run_hash: str,
    second_run_hash: str,
) -> dict[str, bool]:
    return {
        "artifact_identity": first_run.artifact_identity == second_run.artifact_identity,
        "inspection_predictions": first_run.predictions == second_run.predictions,
        "localization": (
            [prediction["predicted_localization"] for prediction in first_run.predictions]
            == [
                prediction["predicted_localization"]
                for prediction in second_run.predictions
            ]
        ),
        "raw_anomaly_measures": (
            [
                prediction["predicted_raw_anomaly_measure"]
                for prediction in first_run.predictions
            ]
            == [
                prediction["predicted_raw_anomaly_measure"]
                for prediction in second_run.predictions
            ]
        ),
        "run_hash": first_run_hash == second_run_hash,
        "session_configuration": (
            first_run.session_configuration == second_run.session_configuration
        ),
        "session_configuration_hash": (
            first_run.session_configuration_hash
            == second_run.session_configuration_hash
        ),
    }


def integration_metadata_record(
    *,
    samples: Sequence[RepresentativeInput],
    first_run: RuntimeRun,
    replay_status: str,
    replay_comparisons: Mapping[str, bool],
) -> dict[str, Any]:
    artifact_record = read_json_mapping(PADIM_ARTIFACT_DIR / "artifact.json")
    metadata_record = read_json_mapping(PADIM_ARTIFACT_DIR / "metadata.json")
    equivalence_hashes = read_json_mapping(EQUIVALENCE_DIR / "equivalence_hashes.json")
    return {
        "consumed_governed_records": {
            "artifact_hashes_sha256": sha256_file(PADIM_ARTIFACT_DIR / "artifact_hashes.json"),
            "artifact_json_sha256": sha256_file(PADIM_ARTIFACT_DIR / "artifact.json"),
            "equivalence_hashes_sha256": sha256_file(
                EQUIVALENCE_DIR / "equivalence_hashes.json"
            ),
            "equivalence_replay_sha256": sha256_file(
                EQUIVALENCE_DIR / "equivalence_replay.json"
            ),
            "equivalence_report_sha256": sha256_file(
                EQUIVALENCE_DIR / "equivalence_report.json"
            ),
            "export_replay_sha256": sha256_file(PADIM_ARTIFACT_DIR / "export_replay.json"),
            "metadata_json_sha256": sha256_file(PADIM_ARTIFACT_DIR / "metadata.json"),
        },
        "governed_equivalence_identity": {
            "equivalence_hashes": equivalence_hashes["governed_equivalence_artifacts"],
            "equivalence_label": "visa-padim-onnx-export-equivalence-v1",
            "export_equivalence_verified_before_runtime_integration": True,
        },
        "integration_label": INTEGRATION_LABEL,
        "loader_configuration": {
            "compatibility_validation": True,
            "expected_artifact_fingerprint_enforced": True,
            "expected_identity_enforced": True,
            "expected_version_enforced": True,
            "loader_path": "model_loader.load_governed_model",
            "provider_private_session_type": "ProviderPrivateInferenceSession",
        },
        "model_artifact_identity": {
            "artifact_metadata_schema": metadata_record["schema"],
            "graph_ir_version": artifact_record["graph"]["ir_version"],
            "graph_opset_version": artifact_record["graph"]["opset_version"],
            "model_path": str(PADIM_MODEL_PATH.relative_to(REPO_ROOT)),
            "model_reference_id": artifact_record["model_reference_id"],
            "model_sha256": artifact_record["model_sha256"],
        },
        "provider_configuration": {
            "canonical_model_reference_id": PADIM_ONNX_MODEL_REFERENCE_ID,
            "placeholder_model_reference_id": ONNX_PLACEHOLDER_MODEL_REFERENCE_ID,
            "placeholder_used_on_canonical_runtime_path": False,
            "provider_id": ONNX_BOUNDARY_PROVIDER_ID,
            "provider_seam": (
                "InspectionInferenceProvider.predict(...) -> InspectionPrediction"
            ),
        },
        "representative_input_count": len(samples),
        "representative_inputs": [sample.to_json_dict() for sample in samples],
        "runtime_artifact_hash": sha256_file(PADIM_MODEL_PATH),
        "runtime_replay": {
            "comparisons": dict(replay_comparisons),
            "runtime_replay_path": "artifacts/runtime/runtime_replay.json",
            "status": replay_status,
        },
        "schema": METADATA_SCHEMA,
        "scope_boundaries": scope_boundaries(),
        "session_configuration": first_run.session_configuration,
        "session_configuration_hash": first_run.session_configuration_hash,
        "session_configuration_runtime": {
            "execution_provider_policy": "exact_order",
            "execution_providers": ["CPUExecutionProvider"],
            "graph_optimization_level": "ORT_DISABLE_ALL",
            "inter_op_num_threads": 1,
            "intra_op_num_threads": 1,
        },
        "status": "passed" if replay_status == "passed" else "failed",
        "toolchain": toolchain_versions(),
    }


def scope_boundaries() -> dict[str, bool]:
    return {
        "benchmark_generated": False,
        "c5_inference_rerun": False,
        "calibration_performed": False,
        "evaluation_domain_modified": False,
        "evaluation_executed": False,
        "evidence_domain_modified": False,
        "feature_extraction_semantics_changed": False,
        "human_review_modified": False,
        "inspection_prediction_contract_changed": False,
        "inspection_transform_prediction_changed": False,
        "metrics_generated": False,
        "onnx_reexported": False,
        "padim_refit_performed": False,
        "placeholder_used_on_canonical_runtime_path": False,
        "preprocessing_contract_changed": False,
        "product_claim": False,
        "prototype_ui_modified": False,
        "review_domain_modified": False,
        "runtime_equivalence_verification_performed": False,
        "runtime_integration_completed": True,
        "runtime_provider_loaded": True,
        "runtime_replay_performed": True,
        "scientific_claim": False,
        "scientific_evaluation_performed": False,
        "trust_domain_modified": False,
    }


def toolchain_versions() -> dict[str, str]:
    return {
        "numpy": np.__version__,
        "onnxruntime": str(onnx_runtime.onnx_runtime_version()),
        "python": platform.python_version(),
    }


def evidence_markdown(
    metadata: Mapping[str, Any],
    replay: Mapping[str, Any],
    hashes: Mapping[str, Any],
) -> str:
    session = metadata["session_configuration"]
    provider = session["execution_providers"][0]["name"]
    scope = metadata["scope_boundaries"]
    return f"""# {EVIDENCE_TITLE}

**Status:** Recorded - governed runtime provider integration evidence only
**Date:** {EVIDENCE_DATE}
**Scope:** Phase 3 / Task 3 - Runtime Provider Integration only

## Integration Result

- Runtime integration completed: `true`
- Governed ONNX artifact loaded through runtime substrate: `true`
- Runtime substrate used: `model_loader.load_governed_model` -> `ProviderPrivateInferenceSession`
- Provider seam preserved: `InspectionInferenceProvider.predict(...) -> InspectionPrediction`
- Provider uses governed artifact: `{metadata['model_artifact_identity']['model_reference_id']}`
- Placeholder no longer used on canonical runtime path: `{str(not scope['placeholder_used_on_canonical_runtime_path']).lower()}`
- Runtime replay status: `{replay['status']}`

## Artifact Identity

- Model path: `{metadata['model_artifact_identity']['model_path']}`
- Model reference id: `{metadata['model_artifact_identity']['model_reference_id']}`
- Model SHA-256: `{metadata['model_artifact_identity']['model_sha256']}`
- Runtime artifact hash: `{metadata['runtime_artifact_hash']}`
- Opset: `{metadata['model_artifact_identity']['graph_opset_version']}`
- ONNX IR version: `{metadata['model_artifact_identity']['graph_ir_version']}`
- Artifact metadata schema: `{metadata['model_artifact_identity']['artifact_metadata_schema']}`
- Export equivalence identity verified before runtime integration: `true`

## Runtime Configuration

- Execution provider: `{provider}`
- Execution provider policy: `{session['execution_provider_policy']}`
- Intra-op threads: `{session['session_options']['intra_op_num_threads']}`
- Inter-op threads: `{session['session_options']['inter_op_num_threads']}`
- Graph optimization level: `ORT_DISABLE_ALL` (`{session['session_options']['optimization_level']}`)
- Session configuration hash: `{metadata['session_configuration_hash']}`

## Replay Result

- Complete second load and execution: `{str(replay['complete_second_load_and_execution']).lower()}`
- Representative input count: `{metadata['representative_input_count']}`
- Same artifact identity: `{str(replay['comparisons']['artifact_identity']).lower()}`
- Same session configuration: `{str(replay['comparisons']['session_configuration']).lower()}`
- Same raw anomaly measures: `{str(replay['comparisons']['raw_anomaly_measures']).lower()}`
- Same localization: `{str(replay['comparisons']['localization']).lower()}`
- Same `InspectionPrediction`: `{str(replay['comparisons']['inspection_predictions']).lower()}`
- Same hashes: `{str(replay['comparisons']['run_hash']).lower()}`
- Runtime replay record: `artifacts/runtime/runtime_replay.json`
- Runtime hashes record: `artifacts/runtime/runtime_hashes.json`
- Integration metadata SHA-256: `{hashes['governed_runtime_artifacts']['integration_metadata.json']}`
- Runtime replay SHA-256: `{hashes['governed_runtime_artifacts']['runtime_replay.json']}`

## Explicit Non-Claims

- No runtime-equivalence verification was performed.
- No comparison against C-5 or C-6 reference outputs was performed.
- No scientific evaluation was performed.
- No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, or F1 was generated.
- No metrics were generated.
- No calibration was performed.
- No threshold was derived.
- No benchmark was run.
- No Trust domain change was made.
- No Review domain change was made.
- No Evidence domain change was made.
- No Evaluation domain change was made.
- No scientific claim was made.
- No product claim was made.
"""


def write_governed_record(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise RuntimeIntegrationError(f"governed runtime record changed: {path}")
    path.write_bytes(content)
    return sha256_file(path)


def persist_records() -> None:
    metadata, replay, hashes, evidence = build_records()
    write_governed_record(INTEGRATION_METADATA_PATH, canonical_json_bytes(metadata))
    write_governed_record(RUNTIME_REPLAY_PATH, canonical_json_bytes(replay))
    write_governed_record(RUNTIME_HASHES_PATH, canonical_json_bytes(hashes))
    write_governed_record(EVIDENCE_PATH, evidence.encode("utf-8"))


def _required_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeIntegrationError(f"record lacks required string: {key}")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate governed runtime provider integration records."
    )
    parser.add_argument(
        "command",
        choices=("verify",),
        help="Run the bounded runtime provider integration replay.",
    )
    parser.parse_args(argv)
    persist_records()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
