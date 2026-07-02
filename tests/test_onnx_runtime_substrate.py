from __future__ import annotations

import builtins
import socket

import pytest

from src.frameworks import onnx_runtime


class FakeOnnxRuntime:
    __version__ = "1.17.3"

    def __init__(
        self,
        providers: tuple[str, ...] = (
            "CPUExecutionProvider",
            "AzureExecutionProvider",
        ),
    ) -> None:
        self.providers = providers
        self.session_creation_calls = 0

    def get_available_providers(self) -> list[str]:
        return list(self.providers)

    def InferenceSession(self, *args, **kwargs):  # noqa: N802
        self.session_creation_calls += 1
        raise AssertionError("substrate must not create ONNX Runtime sessions")


def test_onnx_runtime_absence_is_reported_gracefully(monkeypatch) -> None:
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: None)

    assert onnx_runtime.onnx_runtime_available() is False
    assert onnx_runtime.onnx_runtime_version() is None
    assert onnx_runtime.available_execution_providers() == ()
    assert onnx_runtime.default_execution_provider() is None

    capabilities = onnx_runtime.runtime_capabilities()
    assert capabilities["runtime"] == "onnxruntime"
    assert capabilities["available"] is False
    assert capabilities["version"] is None
    assert capabilities["execution_providers"] == ()
    assert capabilities["default_execution_provider"] is None
    assert capabilities["capability_scope"] == "runtime_discovery_only"


def test_onnx_runtime_presence_reports_version_and_providers(monkeypatch) -> None:
    runtime = FakeOnnxRuntime(
        providers=(
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        )
    )
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)

    assert onnx_runtime.onnx_runtime_available() is True
    assert onnx_runtime.onnx_runtime_version() == "1.17.3"
    assert onnx_runtime.available_execution_providers() == (
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    )
    assert onnx_runtime.default_execution_provider() == "CUDAExecutionProvider"


def test_runtime_capabilities_are_deterministic_and_read_only(monkeypatch) -> None:
    runtime = FakeOnnxRuntime()
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)

    first = onnx_runtime.runtime_capabilities()
    second = onnx_runtime.runtime_capabilities()

    assert dict(first) == dict(second)
    assert first["available"] is True
    assert first["version"] == "1.17.3"
    assert first["execution_providers"] == (
        "CPUExecutionProvider",
        "AzureExecutionProvider",
    )
    assert first["session_creation"] == "not_exposed"
    assert first["model_loading"] == "not_exposed"
    assert first["tensor_creation"] == "not_exposed"
    assert first["inference"] == "not_exposed"
    with pytest.raises(TypeError):
        first["available"] = False


def test_execution_provider_ordering_is_stable(monkeypatch) -> None:
    runtime = FakeOnnxRuntime(
        providers=(
            "TensorrtExecutionProvider",
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        )
    )
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)

    first = onnx_runtime.available_execution_providers()
    second = onnx_runtime.available_execution_providers()

    assert first == second
    assert first == (
        "TensorrtExecutionProvider",
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    )
    assert onnx_runtime.default_execution_provider() == (
        "TensorrtExecutionProvider"
    )


def test_substrate_exposes_no_session_model_tensor_or_inference_api(
    monkeypatch,
) -> None:
    runtime = FakeOnnxRuntime()
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)

    onnx_runtime.onnx_runtime_available()
    onnx_runtime.onnx_runtime_version()
    onnx_runtime.available_execution_providers()
    onnx_runtime.default_execution_provider()
    onnx_runtime.runtime_capabilities()

    assert runtime.session_creation_calls == 0
    assert not hasattr(onnx_runtime, "InferenceSession")
    assert not hasattr(onnx_runtime, "create_session")
    assert not hasattr(onnx_runtime, "load_model")
    assert not hasattr(onnx_runtime, "create_tensor")
    assert not hasattr(onnx_runtime, "predict")
    assert not hasattr(onnx_runtime, "run_inference")


def test_substrate_performs_no_filesystem_or_network_access(
    monkeypatch,
) -> None:
    runtime = FakeOnnxRuntime()
    monkeypatch.setattr(onnx_runtime, "_load_onnxruntime", lambda: runtime)

    def fail_filesystem_access(*args, **kwargs):
        raise AssertionError("ONNX substrate must not access the filesystem")

    def fail_network_access(*args, **kwargs):
        raise AssertionError("ONNX substrate must not access the network")

    monkeypatch.setattr(builtins, "open", fail_filesystem_access)
    monkeypatch.setattr(socket, "socket", fail_network_access)
    monkeypatch.setattr(socket, "create_connection", fail_network_access)

    assert onnx_runtime.onnx_runtime_available() is True
    assert onnx_runtime.onnx_runtime_version() == "1.17.3"
    assert onnx_runtime.available_execution_providers() == (
        "CPUExecutionProvider",
        "AzureExecutionProvider",
    )
    assert onnx_runtime.default_execution_provider() == "CPUExecutionProvider"
    assert onnx_runtime.runtime_capabilities()["available"] is True
