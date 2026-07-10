from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "verify_padim_runtime_equivalence.py"
)
SPEC = importlib.util.spec_from_file_location(
    "verify_padim_runtime_equivalence",
    SCRIPT_PATH,
)
assert SPEC is not None
runtime_equivalence = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = runtime_equivalence
SPEC.loader.exec_module(runtime_equivalence)


class _ValueInfo:
    def __init__(self, name: str, type_: str, shape: list[int]) -> None:
        self.name = name
        self.type = type_
        self.shape = shape


class _RuntimeSession:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object]] = []

    def get_inputs(self) -> list[_ValueInfo]:
        return [_ValueInfo("full_patch_features", "tensor(double)", [1, 64, 14])]

    def get_outputs(self) -> list[_ValueInfo]:
        return [_ValueInfo("anomaly_map", "tensor(double)", [1, 64, 64])]

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]

    def run(self, output_names: object, input_feed: object) -> list[str]:
        self.calls.append((output_names, input_feed))
        return ["provider-invoked-output"]


def test_session_capture_observes_provider_invoked_run() -> None:
    session = _RuntimeSession()
    capture = runtime_equivalence.ProviderSessionCapture(session)

    outputs = capture.run(None, {"full_patch_features": "features"})

    assert outputs == ["provider-invoked-output"]
    assert capture.take_outputs() == ["provider-invoked-output"]
    assert session.calls == [(None, {"full_patch_features": "features"})]
    assert capture.get_providers() == ["CPUExecutionProvider"]


def test_replay_record_fails_closed_on_per_sample_mismatch() -> None:
    first_run = runtime_equivalence.RuntimeEquivalenceRun(
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
                "localization_region_absolute": 0.0,
            }
        },
        global_maxima={
            "anomaly_map_absolute": 0.0,
            "anomaly_map_relative": 0.0,
            "raw_measure_absolute": 0.0,
            "raw_measure_relative": 0.0,
            "localization_region_absolute": 0.0,
        },
        prediction_contract={"status": "passed"},
        runtime_artifact_identity={"model_sha256": "sha"},
        provider_configuration={"provider": "OnnxInspectionInferenceProvider"},
        session_configuration={"execution_providers": []},
        session_configuration_hash="hash",
        status="passed",
    )
    second_run = runtime_equivalence.RuntimeEquivalenceRun(
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
        prediction_contract=first_run.prediction_contract,
        runtime_artifact_identity=first_run.runtime_artifact_identity,
        provider_configuration=first_run.provider_configuration,
        session_configuration=first_run.session_configuration,
        session_configuration_hash=first_run.session_configuration_hash,
        status="passed",
    )

    try:
        runtime_equivalence.build_replay_record(
            first_run,
            second_run,
            b'{"report":"first"}\n',
            b'{"report":"first"}\n',
        )
    except runtime_equivalence.RuntimeEquivalenceError as error:
        assert "deterministic runtime-equivalence replay mismatch" in str(error)
    else:
        raise AssertionError("replay must fail closed on per-sample mismatch")


def test_hashes_record_covers_report_and_replay_artifacts() -> None:
    report_bytes = b'{"schema":"report"}\n'
    replay_bytes = b'{"schema":"replay"}\n'

    hashes = runtime_equivalence.build_hashes_record(report_bytes, replay_bytes)

    assert hashes["schema"] == runtime_equivalence.RUNTIME_EQUIVALENCE_HASHES_SCHEMA
    assert hashes["governed_runtime_equivalence_artifacts"] == {
        "runtime_equivalence_report.json": runtime_equivalence.sha256_bytes(
            report_bytes
        ),
        "runtime_equivalence_replay.json": runtime_equivalence.sha256_bytes(
            replay_bytes
        ),
    }


def test_public_session_configuration_json_replaces_repo_local_artifact_path() -> None:
    repo_model_path = (
        runtime_equivalence.REPO_ROOT / "artifacts" / "padim" / "model.onnx"
    )
    session_json = {
        "model_reference": {
            "artifact_path": str(repo_model_path),
            "content_sha256": "a" * 64,
        },
        "execution_providers": [],
    }

    public_json = runtime_equivalence.public_session_configuration_json(session_json)

    assert public_json["model_reference"]["artifact_path"] == (
        "<REPO>/artifacts/padim/model.onnx"
    )
    assert session_json["model_reference"]["artifact_path"] == str(repo_model_path)


def test_missing_governed_archive_reports_expected_public_clone_boundary(
    tmp_path: Path,
) -> None:
    try:
        runtime_equivalence.require_governed_runtime_data(tmp_path)
    except runtime_equivalence.GovernedDataUnavailableError as error:
        message = str(error)
    else:
        raise AssertionError("missing governed data must fail closed")

    assert "GOVERNED DATA UNAVAILABLE" in message
    assert "data/visa/source/VisA_20220922.tar" in message
    assert "intentionally not shipped in Git" in message
    assert "docs/engineering/VISA_ACQUISITION_AND_GOVERNANCE.md" in message
    assert "expected in a normal public clone" in message
    assert "verification failed" not in message.lower()


@pytest.mark.governed_data
def test_real_runtime_equivalence_verifier_command_passes() -> None:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "verify",
        ],
        cwd=SCRIPT_PATH.parents[1],
        check=True,
    )


def test_real_placeholder_retirement_verifier_command_passes() -> None:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH.parents[1] / "scripts" / "verify_placeholder_retirement.py"),
            "verify",
        ],
        cwd=SCRIPT_PATH.parents[1],
        check=True,
    )
