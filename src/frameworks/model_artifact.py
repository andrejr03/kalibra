from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from hashlib import sha256
import json
import re


GOVERNED_MODEL_ARTIFACT_KIND = "governed_model_artifact_v1"
MODEL_ARTIFACT_METADATA_KIND = "model_artifact_metadata_v1"
MODEL_HASH_ALGORITHM = "sha256"
MODEL_ARTIFACT_FORMAT_ONNX = "onnx"
MODEL_FRAMEWORK_ONNX_RUNTIME = "onnxruntime"

_SHA256_HEX_LENGTH = 64
_HEX_DIGITS = frozenset("0123456789abcdef")
_MODEL_IDENTIFIER_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9._/-]{0,126}[a-z0-9])?$"
)
_SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_ALLOWED_ARTIFACT_FORMATS = frozenset({MODEL_ARTIFACT_FORMAT_ONNX})
_ALLOWED_FRAMEWORK_NAMES = frozenset({MODEL_FRAMEWORK_ONNX_RUNTIME})


@dataclass(frozen=True, order=True)
class ModelIdentity:
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "identifier",
            _normalize_model_identifier(self.identifier),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, str]:
        return {"identifier": self.identifier}


@dataclass(frozen=True, order=True)
class ModelVersion:
    semantic_version: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "semantic_version",
            _normalize_semantic_version(self.semantic_version),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, str]:
        return {"semantic_version": self.semantic_version}


@dataclass(frozen=True, order=True, init=False)
class ModelHash:
    content_sha256: str

    def __init__(
        self,
        content_sha256: object | None = None,
        *,
        sha256_digest: object | None = None,
        digest: object | None = None,
    ) -> None:
        supplied = tuple(
            value
            for value in (content_sha256, sha256_digest, digest)
            if value is not None
        )
        if len(supplied) != 1:
            raise TypeError("ModelHash requires exactly one SHA-256 digest")
        object.__setattr__(
            self,
            "content_sha256",
            _normalize_sha256(supplied[0], "model content_sha256"),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, str]:
        return {
            "algorithm": MODEL_HASH_ALGORITHM,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, order=True)
class ModelProvenance:
    producer: str
    provenance: str
    lineage: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "producer",
            _normalize_nonblank_string(self.producer, "producer"),
        )
        object.__setattr__(
            self,
            "provenance",
            _normalize_nonblank_string(self.provenance, "provenance"),
        )
        object.__setattr__(
            self,
            "lineage",
            _normalize_string_pairs(self.lineage, "provenance lineage"),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, object]:
        return {
            "lineage": [list(pair) for pair in self.lineage],
            "producer": self.producer,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, order=True)
class ModelCompatibility:
    artifact_format: str
    framework_name: str
    framework_version: str
    onnx_opset: int
    compatibility_declaration: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "artifact_format",
            _normalize_allowed_value(
                self.artifact_format,
                "artifact_format",
                _ALLOWED_ARTIFACT_FORMATS,
            ),
        )
        object.__setattr__(
            self,
            "framework_name",
            _normalize_allowed_value(
                self.framework_name,
                "framework_name",
                _ALLOWED_FRAMEWORK_NAMES,
            ),
        )
        object.__setattr__(
            self,
            "framework_version",
            _normalize_semantic_version(self.framework_version),
        )
        object.__setattr__(
            self,
            "onnx_opset",
            _normalize_positive_int(self.onnx_opset, "onnx_opset"),
        )
        object.__setattr__(
            self,
            "compatibility_declaration",
            _normalize_nonblank_string(
                self.compatibility_declaration,
                "compatibility_declaration",
            ),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, object]:
        return {
            "artifact_format": self.artifact_format,
            "compatibility_declaration": self.compatibility_declaration,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "onnx_opset": self.onnx_opset,
        }


@dataclass(frozen=True, order=True, init=False)
class ModelArtifactReference:
    artifact_uri: str
    content_hash: ModelHash

    def __init__(
        self,
        artifact_uri: object | None = None,
        content_hash: ModelHash | str | None = None,
        *,
        artifact_path: object | None = None,
    ) -> None:
        uri = _select_artifact_uri(artifact_uri, artifact_path)
        if isinstance(content_hash, str):
            normalized_hash = ModelHash(content_hash)
        elif isinstance(content_hash, ModelHash):
            normalized_hash = ModelHash(content_hash.content_sha256)
        else:
            raise TypeError("content_hash must be a ModelHash or SHA-256 string")

        object.__setattr__(
            self,
            "artifact_uri",
            _normalize_artifact_uri(uri),
        )
        object.__setattr__(self, "content_hash", normalized_hash)

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, object]:
        return {
            "artifact_uri": self.artifact_uri,
            "content_hash": self.content_hash.to_json_dict(),
        }


@dataclass(frozen=True, order=True)
class ModelArtifactMetadata:
    identity: ModelIdentity
    version: ModelVersion
    provenance: ModelProvenance
    compatibility: ModelCompatibility
    metadata_kind: str = MODEL_ARTIFACT_METADATA_KIND

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ModelIdentity):
            raise TypeError("identity must be a ModelIdentity")
        if not isinstance(self.version, ModelVersion):
            raise TypeError("version must be a ModelVersion")
        if not isinstance(self.provenance, ModelProvenance):
            raise TypeError("provenance must be a ModelProvenance")
        if not isinstance(self.compatibility, ModelCompatibility):
            raise TypeError("compatibility must be a ModelCompatibility")
        object.__setattr__(
            self,
            "metadata_kind",
            _normalize_required_literal(
                self.metadata_kind,
                "metadata_kind",
                MODEL_ARTIFACT_METADATA_KIND,
            ),
        )

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, object]:
        return {
            "compatibility": self.compatibility.to_json_dict(),
            "identity": self.identity.to_json_dict(),
            "metadata_kind": self.metadata_kind,
            "provenance": self.provenance.to_json_dict(),
            "version": self.version.to_json_dict(),
        }


@dataclass(frozen=True, order=True)
class GovernedModelArtifact:
    reference: ModelArtifactReference
    metadata: ModelArtifactMetadata
    artifact_kind: str = GOVERNED_MODEL_ARTIFACT_KIND

    def __post_init__(self) -> None:
        if not isinstance(self.reference, ModelArtifactReference):
            raise TypeError("reference must be a ModelArtifactReference")
        if not isinstance(self.metadata, ModelArtifactMetadata):
            raise TypeError("metadata must be a ModelArtifactMetadata")
        object.__setattr__(
            self,
            "artifact_kind",
            _normalize_required_literal(
                self.artifact_kind,
                "artifact_kind",
                GOVERNED_MODEL_ARTIFACT_KIND,
            ),
        )

    @property
    def identity(self) -> ModelIdentity:
        return self.metadata.identity

    @property
    def version(self) -> ModelVersion:
        return self.metadata.version

    @property
    def content_hash(self) -> ModelHash:
        return self.reference.content_hash

    def __hash__(self) -> int:
        return _stable_value_hash(self.to_json_dict())

    def to_json_dict(self) -> dict[str, object]:
        return {
            "artifact_kind": self.artifact_kind,
            "metadata": self.metadata.to_json_dict(),
            "reference": self.reference.to_json_dict(),
        }


def canonical_model_artifact(
    artifact: GovernedModelArtifact | None = None,
    *,
    identity: ModelIdentity | str | None = None,
    version: ModelVersion | str | None = None,
    content_hash: ModelHash | str | None = None,
    artifact_uri: str | None = None,
    artifact_path: str | None = None,
    artifact_format: str | None = None,
    producer: str | None = None,
    provenance: str | None = None,
    lineage: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
    framework_name: str | None = None,
    framework_version: str | None = None,
    onnx_opset: int | None = None,
    compatibility_declaration: str | None = None,
) -> GovernedModelArtifact:
    if artifact is not None:
        _reject_extra_artifact_arguments(
            identity=identity,
            version=version,
            content_hash=content_hash,
            artifact_uri=artifact_uri,
            artifact_path=artifact_path,
            artifact_format=artifact_format,
            producer=producer,
            provenance=provenance,
            lineage=lineage,
            framework_name=framework_name,
            framework_version=framework_version,
            onnx_opset=onnx_opset,
            compatibility_declaration=compatibility_declaration,
        )
        if not isinstance(artifact, GovernedModelArtifact):
            raise TypeError("artifact must be a GovernedModelArtifact")
        return GovernedModelArtifact(
            reference=ModelArtifactReference(
                artifact_uri=artifact.reference.artifact_uri,
                content_hash=artifact.reference.content_hash,
            ),
            metadata=ModelArtifactMetadata(
                identity=ModelIdentity(artifact.identity.identifier),
                version=ModelVersion(artifact.version.semantic_version),
                provenance=ModelProvenance(
                    producer=artifact.metadata.provenance.producer,
                    provenance=artifact.metadata.provenance.provenance,
                    lineage=artifact.metadata.provenance.lineage,
                ),
                compatibility=ModelCompatibility(
                    artifact_format=(
                        artifact.metadata.compatibility.artifact_format
                    ),
                    framework_name=(
                        artifact.metadata.compatibility.framework_name
                    ),
                    framework_version=(
                        artifact.metadata.compatibility.framework_version
                    ),
                    onnx_opset=artifact.metadata.compatibility.onnx_opset,
                    compatibility_declaration=(
                        artifact.metadata.compatibility
                        .compatibility_declaration
                    ),
                ),
            ),
        )

    normalized_identity = _coerce_identity(identity)
    normalized_version = _coerce_version(version)
    normalized_hash = _coerce_hash(content_hash)
    normalized_reference = ModelArtifactReference(
        artifact_uri=artifact_uri,
        artifact_path=artifact_path,
        content_hash=normalized_hash,
    )
    normalized_metadata = ModelArtifactMetadata(
        identity=normalized_identity,
        version=normalized_version,
        provenance=ModelProvenance(
            producer=_require_supplied(producer, "producer"),
            provenance=_require_supplied(provenance, "provenance"),
            lineage=lineage or (),
        ),
        compatibility=ModelCompatibility(
            artifact_format=_require_supplied(
                artifact_format,
                "artifact_format",
            ),
            framework_name=_require_supplied(
                framework_name,
                "framework_name",
            ),
            framework_version=_require_supplied(
                framework_version,
                "framework_version",
            ),
            onnx_opset=_require_supplied(onnx_opset, "onnx_opset"),
            compatibility_declaration=_require_supplied(
                compatibility_declaration,
                "compatibility_declaration",
            ),
        ),
    )
    return GovernedModelArtifact(
        reference=normalized_reference,
        metadata=normalized_metadata,
    )


def validate_model_artifact(
    artifact: GovernedModelArtifact,
) -> GovernedModelArtifact:
    return canonical_model_artifact(artifact)


def model_artifact_identity(artifact: GovernedModelArtifact) -> str:
    canonical = validate_model_artifact(artifact)
    return (
        f"{canonical.identity.identifier}"
        f"@{canonical.version.semantic_version}"
        f"#sha256:{canonical.content_hash.content_sha256}"
    )


def model_artifact_fingerprint(artifact: GovernedModelArtifact) -> str:
    return sha256(canonical_model_json(artifact).encode("utf-8")).hexdigest()


def canonical_model_json(artifact: GovernedModelArtifact) -> str:
    return json.dumps(
        validate_model_artifact(artifact).to_json_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )


def _coerce_identity(value: ModelIdentity | str | None) -> ModelIdentity:
    if isinstance(value, ModelIdentity):
        return ModelIdentity(value.identifier)
    return ModelIdentity(_require_supplied(value, "identity"))


def _coerce_version(value: ModelVersion | str | None) -> ModelVersion:
    if isinstance(value, ModelVersion):
        return ModelVersion(value.semantic_version)
    return ModelVersion(_require_supplied(value, "version"))


def _coerce_hash(value: ModelHash | str | None) -> ModelHash:
    if isinstance(value, ModelHash):
        return ModelHash(value.content_sha256)
    return ModelHash(_require_supplied(value, "content_hash"))


def _reject_extra_artifact_arguments(**arguments: object) -> None:
    provided = tuple(name for name, value in arguments.items() if value is not None)
    if provided:
        joined = ", ".join(sorted(provided))
        raise TypeError(
            "artifact cannot be combined with canonical construction "
            f"arguments: {joined}"
        )


def _select_artifact_uri(
    artifact_uri: object | None,
    artifact_path: object | None,
) -> object:
    if artifact_uri is not None and artifact_path is not None:
        raise TypeError("provide either artifact_uri or artifact_path, not both")
    if artifact_uri is not None:
        return artifact_uri
    if artifact_path is not None:
        return artifact_path
    raise TypeError("artifact_uri is required")


def _normalize_artifact_uri(value: object) -> str:
    normalized = _normalize_nonblank_string(value, "artifact_uri")
    if any(character in normalized for character in ("\x00", "\n", "\r")):
        raise ValueError("artifact_uri must not contain control characters")
    return normalized


def _normalize_model_identifier(value: object) -> str:
    normalized = _normalize_nonblank_string(value, "model identifier").lower()
    if _MODEL_IDENTIFIER_PATTERN.fullmatch(normalized) is None:
        raise ValueError(
            "model identifier must use lowercase letters, digits, '.', '-', "
            "'_', or '/', and must start and end with a letter or digit"
        )
    return normalized


def _normalize_semantic_version(value: object) -> str:
    normalized = _normalize_nonblank_string(value, "semantic version")
    if _SEMANTIC_VERSION_PATTERN.fullmatch(normalized) is None:
        raise ValueError("semantic version must follow SemVer 2.0.0")
    return normalized


def _normalize_sha256(value: object, field_name: str) -> str:
    normalized = _normalize_nonblank_string(value, field_name).lower()
    if len(normalized) != _SHA256_HEX_LENGTH:
        raise ValueError(f"{field_name} must be a 64-character hex digest")
    if any(character not in _HEX_DIGITS for character in normalized):
        raise ValueError(f"{field_name} must be a 64-character hex digest")
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


def _normalize_nonblank_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _normalize_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be a positive integer")
    if value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _require_supplied(value: object | None, field_name: str) -> object:
    if value is None:
        raise TypeError(f"{field_name} is required")
    return value


def _stable_value_hash(payload: object) -> int:
    digest = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    return int(digest[:16], 16)


__all__ = [
    "GOVERNED_MODEL_ARTIFACT_KIND",
    "MODEL_ARTIFACT_FORMAT_ONNX",
    "MODEL_ARTIFACT_METADATA_KIND",
    "MODEL_FRAMEWORK_ONNX_RUNTIME",
    "MODEL_HASH_ALGORITHM",
    "GovernedModelArtifact",
    "ModelArtifactMetadata",
    "ModelArtifactReference",
    "ModelCompatibility",
    "ModelHash",
    "ModelIdentity",
    "ModelProvenance",
    "ModelVersion",
    "canonical_model_artifact",
    "canonical_model_json",
    "model_artifact_fingerprint",
    "model_artifact_identity",
    "validate_model_artifact",
]
