from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from hashlib import sha256
import json


ONNX_SESSION_CONFIGURATION_KIND = "onnx_session_configuration_v1"
DEFAULT_MODEL_REFERENCE_ID = "unbound-onnx-model-reference"
DEFAULT_EXECUTION_PROVIDER = "CPUExecutionProvider"

OPTIMIZATION_LEVEL_DISABLE_ALL = "disable_all"
OPTIMIZATION_LEVEL_BASIC = "basic"
OPTIMIZATION_LEVEL_EXTENDED = "extended"
OPTIMIZATION_LEVEL_ALL = "all"

EXECUTION_PROVIDER_POLICY_EXACT_ORDER = "exact_order"
EXECUTION_PROVIDER_POLICY_ORDERED_FALLBACK = "ordered_fallback"

_ALLOWED_OPTIMIZATION_LEVELS = frozenset(
    {
        OPTIMIZATION_LEVEL_DISABLE_ALL,
        OPTIMIZATION_LEVEL_BASIC,
        OPTIMIZATION_LEVEL_EXTENDED,
        OPTIMIZATION_LEVEL_ALL,
    }
)
_ALLOWED_EXECUTION_PROVIDER_POLICIES = frozenset(
    {
        EXECUTION_PROVIDER_POLICY_EXACT_ORDER,
        EXECUTION_PROVIDER_POLICY_ORDERED_FALLBACK,
    }
)
_SHA256_HEX_LENGTH = 64
_HEX_DIGITS = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class OnnxExecutionProvider:
    name: str = DEFAULT_EXECUTION_PROVIDER
    provider_options: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "name",
            _normalize_nonblank_string(self.name, "execution provider name"),
        )
        object.__setattr__(
            self,
            "provider_options",
            _normalize_string_pairs(
                self.provider_options,
                "execution provider options",
            ),
        )


@dataclass(frozen=True)
class OnnxSessionOptions:
    intra_op_num_threads: int = 1
    inter_op_num_threads: int = 1
    optimization_level: str = OPTIMIZATION_LEVEL_DISABLE_ALL

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "intra_op_num_threads",
            _normalize_positive_int(
                self.intra_op_num_threads,
                "intra_op_num_threads",
            ),
        )
        object.__setattr__(
            self,
            "inter_op_num_threads",
            _normalize_positive_int(
                self.inter_op_num_threads,
                "inter_op_num_threads",
            ),
        )
        object.__setattr__(
            self,
            "optimization_level",
            _normalize_allowed_value(
                self.optimization_level,
                "optimization_level",
                _ALLOWED_OPTIMIZATION_LEVELS,
            ),
        )


@dataclass(frozen=True)
class OnnxModelReference:
    reference_id: str
    artifact_path: str | None = None
    content_sha256: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reference_id",
            _normalize_nonblank_string(self.reference_id, "model reference_id"),
        )
        object.__setattr__(
            self,
            "artifact_path",
            _normalize_optional_nonblank_string(
                self.artifact_path,
                "model artifact_path",
            ),
        )
        object.__setattr__(
            self,
            "content_sha256",
            _normalize_optional_sha256(self.content_sha256),
        )


@dataclass(frozen=True)
class OnnxSessionConfiguration:
    model_reference: OnnxModelReference
    execution_providers: tuple[OnnxExecutionProvider, ...] = field(
        default_factory=lambda: (OnnxExecutionProvider(),)
    )
    session_options: OnnxSessionOptions = field(default_factory=OnnxSessionOptions)
    execution_provider_policy: str = EXECUTION_PROVIDER_POLICY_EXACT_ORDER
    configuration_kind: str = ONNX_SESSION_CONFIGURATION_KIND

    def __post_init__(self) -> None:
        if not isinstance(self.model_reference, OnnxModelReference):
            raise TypeError("model_reference must be an OnnxModelReference")
        if not isinstance(self.session_options, OnnxSessionOptions):
            raise TypeError("session_options must be an OnnxSessionOptions")

        object.__setattr__(
            self,
            "execution_providers",
            _normalize_execution_providers(self.execution_providers),
        )
        object.__setattr__(
            self,
            "execution_provider_policy",
            _normalize_allowed_value(
                self.execution_provider_policy,
                "execution_provider_policy",
                _ALLOWED_EXECUTION_PROVIDER_POLICIES,
            ),
        )
        object.__setattr__(
            self,
            "configuration_kind",
            _normalize_required_literal(
                self.configuration_kind,
                "configuration_kind",
                ONNX_SESSION_CONFIGURATION_KIND,
            ),
        )


def default_session_configuration(
    model_reference: OnnxModelReference | None = None,
) -> OnnxSessionConfiguration:
    reference = model_reference or OnnxModelReference(DEFAULT_MODEL_REFERENCE_ID)
    return OnnxSessionConfiguration(model_reference=reference)


def validate_session_configuration(
    configuration: OnnxSessionConfiguration,
) -> OnnxSessionConfiguration:
    return canonical_session_configuration(configuration)


def canonical_session_configuration(
    configuration: OnnxSessionConfiguration,
) -> OnnxSessionConfiguration:
    if not isinstance(configuration, OnnxSessionConfiguration):
        raise TypeError("configuration must be an OnnxSessionConfiguration")

    return OnnxSessionConfiguration(
        model_reference=OnnxModelReference(
            reference_id=configuration.model_reference.reference_id,
            artifact_path=configuration.model_reference.artifact_path,
            content_sha256=configuration.model_reference.content_sha256,
        ),
        execution_providers=tuple(
            OnnxExecutionProvider(
                name=provider.name,
                provider_options=provider.provider_options,
            )
            for provider in configuration.execution_providers
        ),
        session_options=OnnxSessionOptions(
            intra_op_num_threads=(
                configuration.session_options.intra_op_num_threads
            ),
            inter_op_num_threads=(
                configuration.session_options.inter_op_num_threads
            ),
            optimization_level=configuration.session_options.optimization_level,
        ),
        execution_provider_policy=configuration.execution_provider_policy,
        configuration_kind=configuration.configuration_kind,
    )


def session_configuration_json(
    configuration: OnnxSessionConfiguration,
) -> str:
    return json.dumps(
        _session_configuration_payload(
            canonical_session_configuration(configuration)
        ),
        sort_keys=True,
        separators=(",", ":"),
    )


def session_configuration_hash(
    configuration: OnnxSessionConfiguration,
) -> str:
    canonical = session_configuration_json(configuration)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _session_configuration_payload(
    configuration: OnnxSessionConfiguration,
) -> dict[str, object]:
    return {
        "configuration_kind": configuration.configuration_kind,
        "execution_provider_policy": configuration.execution_provider_policy,
        "execution_providers": [
            {
                "name": provider.name,
                "provider_options": list(provider.provider_options),
            }
            for provider in configuration.execution_providers
        ],
        "model_reference": {
            "artifact_path": configuration.model_reference.artifact_path,
            "content_sha256": configuration.model_reference.content_sha256,
            "reference_id": configuration.model_reference.reference_id,
        },
        "session_options": {
            "inter_op_num_threads": (
                configuration.session_options.inter_op_num_threads
            ),
            "intra_op_num_threads": (
                configuration.session_options.intra_op_num_threads
            ),
            "optimization_level": configuration.session_options.optimization_level,
        },
    }


def _normalize_execution_providers(
    providers: Iterable[OnnxExecutionProvider],
) -> tuple[OnnxExecutionProvider, ...]:
    if isinstance(providers, OnnxExecutionProvider):
        normalized = (providers,)
    elif isinstance(providers, str):
        raise TypeError("execution_providers must contain OnnxExecutionProvider")
    else:
        try:
            normalized = tuple(providers)
        except TypeError as exc:
            raise TypeError(
                "execution_providers must contain OnnxExecutionProvider"
            ) from exc

    if not normalized:
        raise ValueError("execution_providers must not be empty")

    provider_names: set[str] = set()
    for provider in normalized:
        if not isinstance(provider, OnnxExecutionProvider):
            raise TypeError(
                "execution_providers must contain OnnxExecutionProvider"
            )
        if provider.name in provider_names:
            raise ValueError(
                "execution_providers must not contain duplicate provider names"
            )
        provider_names.add(provider.name)

    return normalized


def _normalize_string_pairs(
    value: Mapping[str, str] | Iterable[tuple[str, str]],
    field_name: str,
) -> tuple[tuple[str, str], ...]:
    if isinstance(value, Mapping):
        raw_pairs = tuple(value.items())
    elif isinstance(value, str):
        raise TypeError(f"{field_name} must contain key/value pairs")
    else:
        try:
            raw_pairs = tuple(value)
        except TypeError as exc:
            raise TypeError(f"{field_name} must contain key/value pairs") from exc

    normalized_pairs: list[tuple[str, str]] = []
    seen_keys: set[str] = set()
    for raw_pair in raw_pairs:
        try:
            raw_key, raw_value = raw_pair
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must contain two-item key/value pairs"
            ) from exc

        key = _normalize_nonblank_string(raw_key, f"{field_name} key")
        pair_value = _normalize_nonblank_string(
            raw_value,
            f"{field_name} value",
        )
        if key in seen_keys:
            raise ValueError(f"{field_name} must not contain duplicate keys")
        seen_keys.add(key)
        normalized_pairs.append((key, pair_value))

    return tuple(sorted(normalized_pairs))


def _normalize_nonblank_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _normalize_optional_nonblank_string(
    value: object | None,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return _normalize_nonblank_string(value, field_name)


def _normalize_optional_sha256(value: object | None) -> str | None:
    if value is None:
        return None

    normalized = _normalize_nonblank_string(value, "model content_sha256").lower()
    if len(normalized) != _SHA256_HEX_LENGTH:
        raise ValueError("model content_sha256 must be a 64-character hex digest")
    if any(character not in _HEX_DIGITS for character in normalized):
        raise ValueError("model content_sha256 must be a 64-character hex digest")
    return normalized


def _normalize_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be a positive integer")
    if value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _normalize_allowed_value(
    value: object,
    field_name: str,
    allowed_values: frozenset[str],
) -> str:
    normalized = _normalize_nonblank_string(value, field_name).lower()
    if normalized not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise ValueError(f"{field_name} must be one of: {allowed}")
    return normalized


def _normalize_required_literal(
    value: object,
    field_name: str,
    expected: str,
) -> str:
    normalized = _normalize_nonblank_string(value, field_name)
    if normalized != expected:
        raise ValueError(f"{field_name} must be {expected!r}")
    return normalized


__all__ = [
    "DEFAULT_EXECUTION_PROVIDER",
    "DEFAULT_MODEL_REFERENCE_ID",
    "EXECUTION_PROVIDER_POLICY_EXACT_ORDER",
    "EXECUTION_PROVIDER_POLICY_ORDERED_FALLBACK",
    "ONNX_SESSION_CONFIGURATION_KIND",
    "OPTIMIZATION_LEVEL_ALL",
    "OPTIMIZATION_LEVEL_BASIC",
    "OPTIMIZATION_LEVEL_DISABLE_ALL",
    "OPTIMIZATION_LEVEL_EXTENDED",
    "OnnxExecutionProvider",
    "OnnxModelReference",
    "OnnxSessionConfiguration",
    "OnnxSessionOptions",
    "canonical_session_configuration",
    "default_session_configuration",
    "session_configuration_hash",
    "session_configuration_json",
    "validate_session_configuration",
]
