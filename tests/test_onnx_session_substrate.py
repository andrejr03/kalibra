from __future__ import annotations

import builtins
from dataclasses import FrozenInstanceError
import json
import socket
import sys

import pytest

from src.frameworks import onnx_session


MODEL_SHA256 = "A" * 64


def test_session_configuration_objects_are_immutable() -> None:
    configuration = _explicit_configuration()

    with pytest.raises(FrozenInstanceError):
        configuration.execution_provider_policy = (
            onnx_session.EXECUTION_PROVIDER_POLICY_ORDERED_FALLBACK
        )
    with pytest.raises(FrozenInstanceError):
        configuration.session_options.intra_op_num_threads = 4
    with pytest.raises(FrozenInstanceError):
        configuration.execution_providers[0].name = "CUDAExecutionProvider"
    with pytest.raises(TypeError):
        configuration.execution_providers[0].provider_options[0][0] = (
            "changed"
        )


def test_equivalent_configurations_have_deterministic_equality() -> None:
    first = _explicit_configuration()
    second = onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=" model-v1 ",
            artifact_path=" models/model.onnx ",
            content_sha256=MODEL_SHA256.lower(),
        ),
        execution_providers=[
            onnx_session.OnnxExecutionProvider(
                name=" CPUExecutionProvider ",
                provider_options=(
                    ("arena_extend_strategy", "kSameAsRequested"),
                    ("device_id", "0"),
                ),
            )
        ],
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=1,
            inter_op_num_threads=1,
            optimization_level=" DISABLE_ALL ",
        ),
        execution_provider_policy=" EXACT_ORDER ",
    )

    assert first == second
    assert hash(first) == hash(second)


def test_session_configuration_hash_is_stable_and_canonical() -> None:
    first = _explicit_configuration()
    equivalent = onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id="model-v1",
            artifact_path="models/model.onnx",
            content_sha256=MODEL_SHA256.lower(),
        ),
        execution_providers=(
            onnx_session.OnnxExecutionProvider(
                name="CPUExecutionProvider",
                provider_options={
                    "device_id": "0",
                    "arena_extend_strategy": "kSameAsRequested",
                },
            ),
        ),
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=1,
            inter_op_num_threads=1,
            optimization_level=onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL,
        ),
    )
    changed = onnx_session.OnnxSessionConfiguration(
        model_reference=first.model_reference,
        execution_providers=first.execution_providers,
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=2,
            inter_op_num_threads=1,
            optimization_level=(
                onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL
            ),
        ),
    )

    first_hash = onnx_session.session_configuration_hash(first)

    assert first_hash == onnx_session.session_configuration_hash(equivalent)
    assert first_hash == onnx_session.session_configuration_hash(first)
    assert first_hash != onnx_session.session_configuration_hash(changed)
    assert len(first_hash) == 64
    assert all(character in "0123456789abcdef" for character in first_hash)


def test_canonical_session_configuration_normalizes_value_inputs() -> None:
    configuration = onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id=" model-v1 ",
            artifact_path=" models/model.onnx ",
            content_sha256=MODEL_SHA256,
        ),
        execution_providers=[
            onnx_session.OnnxExecutionProvider(
                name=" CPUExecutionProvider ",
                provider_options={
                    "device_id": "0",
                    "arena_extend_strategy": "kSameAsRequested",
                },
            )
        ],
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=1,
            inter_op_num_threads=1,
            optimization_level=" DISABLE_ALL ",
        ),
        execution_provider_policy=" EXACT_ORDER ",
    )

    canonical = onnx_session.canonical_session_configuration(configuration)

    assert canonical.model_reference.reference_id == "model-v1"
    assert canonical.model_reference.artifact_path == "models/model.onnx"
    assert canonical.model_reference.content_sha256 == MODEL_SHA256.lower()
    assert canonical.execution_providers == (
        onnx_session.OnnxExecutionProvider(
            name="CPUExecutionProvider",
            provider_options=(
                ("arena_extend_strategy", "kSameAsRequested"),
                ("device_id", "0"),
            ),
        ),
    )
    assert canonical.session_options.optimization_level == (
        onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL
    )
    assert canonical.execution_provider_policy == (
        onnx_session.EXECUTION_PROVIDER_POLICY_EXACT_ORDER
    )


def test_session_configuration_validation_accepts_valid_configuration() -> None:
    configuration = onnx_session.default_session_configuration()

    validated = onnx_session.validate_session_configuration(configuration)

    assert validated == configuration
    assert validated.model_reference.reference_id == (
        onnx_session.DEFAULT_MODEL_REFERENCE_ID
    )
    assert validated.execution_providers == (
        onnx_session.OnnxExecutionProvider(
            name=onnx_session.DEFAULT_EXECUTION_PROVIDER
        ),
    )
    assert validated.session_options == onnx_session.OnnxSessionOptions()


@pytest.mark.parametrize(
    "factory",
    (
        lambda: onnx_session.OnnxModelReference(reference_id=""),
        lambda: onnx_session.OnnxModelReference(
            reference_id="model",
            artifact_path=" ",
        ),
        lambda: onnx_session.OnnxModelReference(
            reference_id="model",
            content_sha256="not-a-sha256",
        ),
        lambda: onnx_session.OnnxExecutionProvider(
            name="",
        ),
        lambda: onnx_session.OnnxExecutionProvider(
            provider_options="device_id=0",
        ),
        lambda: onnx_session.OnnxExecutionProvider(
            provider_options=((" device_id ", "0"), ("device_id", "1")),
        ),
        lambda: onnx_session.OnnxSessionOptions(
            intra_op_num_threads=0,
        ),
        lambda: onnx_session.OnnxSessionOptions(
            inter_op_num_threads=True,
        ),
        lambda: onnx_session.OnnxSessionOptions(
            optimization_level="unknown",
        ),
        lambda: onnx_session.OnnxSessionConfiguration(
            model_reference=onnx_session.OnnxModelReference("model"),
            execution_providers=(),
        ),
        lambda: onnx_session.OnnxSessionConfiguration(
            model_reference=onnx_session.OnnxModelReference("model"),
            execution_providers=(
                onnx_session.OnnxExecutionProvider("CPUExecutionProvider"),
                onnx_session.OnnxExecutionProvider("CPUExecutionProvider"),
            ),
        ),
        lambda: onnx_session.OnnxSessionConfiguration(
            model_reference=onnx_session.OnnxModelReference("model"),
            execution_provider_policy="ambient-runtime-default",
        ),
    ),
)
def test_session_configuration_validation_rejects_invalid_inputs(factory) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()


def test_session_configuration_serialization_is_stable() -> None:
    configuration = _explicit_configuration()

    first = onnx_session.session_configuration_json(configuration)
    second = onnx_session.session_configuration_json(configuration)

    assert first == second
    assert first == (
        '{"configuration_kind":"onnx_session_configuration_v1",'
        '"execution_provider_policy":"exact_order",'
        '"execution_providers":[{"name":"CPUExecutionProvider",'
        '"provider_options":[["arena_extend_strategy","kSameAsRequested"],'
        '["device_id","0"]]}],'
        '"model_reference":{"artifact_path":"models/model.onnx",'
        '"content_sha256":"'
        + MODEL_SHA256.lower()
        + '","reference_id":"model-v1"},'
        '"session_options":{"inter_op_num_threads":1,'
        '"intra_op_num_threads":1,"optimization_level":"disable_all"}}'
    )
    assert json.loads(first) == json.loads(second)


def test_session_substrate_exposes_no_runtime_or_inference_api() -> None:
    forbidden_public_names = {
        "Inference" + "Session",
        "create_session",
        "create_tensor",
        "load_model",
        "predict",
        "run_inference",
    }

    public_names = set(dir(onnx_session))

    assert public_names.isdisjoint(forbidden_public_names)


def test_session_substrate_does_not_create_runtime_sessions_or_load_models(
    monkeypatch,
) -> None:
    class RuntimeTrap:
        def __getattr__(self, name):
            raise AssertionError(
                "ONNX session substrate must not access runtime objects"
            )

    monkeypatch.setitem(sys.modules, "onnxruntime", RuntimeTrap())

    configuration = _explicit_configuration()

    assert onnx_session.validate_session_configuration(configuration)
    assert onnx_session.session_configuration_json(configuration)
    assert onnx_session.session_configuration_hash(configuration)


def test_session_substrate_performs_no_filesystem_or_network_access(
    monkeypatch,
) -> None:
    def fail_filesystem_access(*args, **kwargs):
        raise AssertionError(
            "ONNX session substrate must not access the filesystem"
        )

    def fail_network_access(*args, **kwargs):
        raise AssertionError("ONNX session substrate must not access the network")

    monkeypatch.setattr(builtins, "open", fail_filesystem_access)
    monkeypatch.setattr(socket, "socket", fail_network_access)
    monkeypatch.setattr(socket, "create_connection", fail_network_access)

    configuration = _explicit_configuration()

    assert onnx_session.validate_session_configuration(configuration)
    assert onnx_session.canonical_session_configuration(configuration)
    assert onnx_session.session_configuration_json(configuration)
    assert onnx_session.session_configuration_hash(configuration)


def _explicit_configuration() -> onnx_session.OnnxSessionConfiguration:
    return onnx_session.OnnxSessionConfiguration(
        model_reference=onnx_session.OnnxModelReference(
            reference_id="model-v1",
            artifact_path="models/model.onnx",
            content_sha256=MODEL_SHA256,
        ),
        execution_providers=(
            onnx_session.OnnxExecutionProvider(
                name="CPUExecutionProvider",
                provider_options={
                    "device_id": "0",
                    "arena_extend_strategy": "kSameAsRequested",
                },
            ),
        ),
        session_options=onnx_session.OnnxSessionOptions(
            intra_op_num_threads=1,
            inter_op_num_threads=1,
            optimization_level=onnx_session.OPTIMIZATION_LEVEL_DISABLE_ALL,
        ),
        execution_provider_policy=(
            onnx_session.EXECUTION_PROVIDER_POLICY_EXACT_ORDER
        ),
    )
