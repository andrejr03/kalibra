from __future__ import annotations

from importlib import import_module
from types import MappingProxyType
from typing import Any, Mapping


RUNTIME_NAME = "onnxruntime"
CAPABILITY_SCOPE = "runtime_discovery_only"
_NOT_EXPOSED = "not_exposed"


def onnx_runtime_available() -> bool:
    return _load_onnxruntime() is not None


def onnx_runtime_version() -> str | None:
    return _runtime_version(_load_onnxruntime())


def available_execution_providers() -> tuple[str, ...]:
    return _execution_providers(_load_onnxruntime())


def default_execution_provider() -> str | None:
    providers = available_execution_providers()
    if not providers:
        return None
    return providers[0]


def runtime_capabilities() -> Mapping[str, object]:
    runtime = _load_onnxruntime()
    providers = _execution_providers(runtime)
    return MappingProxyType(
        {
            "runtime": RUNTIME_NAME,
            "available": runtime is not None,
            "version": _runtime_version(runtime),
            "execution_providers": providers,
            "default_execution_provider": providers[0] if providers else None,
            "capability_scope": CAPABILITY_SCOPE,
            "session_creation": _NOT_EXPOSED,
            "model_loading": _NOT_EXPOSED,
            "tensor_creation": _NOT_EXPOSED,
            "inference": _NOT_EXPOSED,
        }
    )


def _runtime_version(runtime: Any | None) -> str | None:
    if runtime is None:
        return None

    version = getattr(runtime, "__version__", None)
    if version is None:
        return None
    return str(version)


def _execution_providers(runtime: Any | None) -> tuple[str, ...]:
    if runtime is None:
        return ()

    get_available_providers = getattr(
        runtime,
        "get_available_providers",
        None,
    )
    if not callable(get_available_providers):
        return ()

    providers = get_available_providers()
    return tuple(provider for provider in providers if isinstance(provider, str))


def _load_onnxruntime() -> Any | None:
    try:
        return import_module(RUNTIME_NAME)
    except ImportError:
        return None
