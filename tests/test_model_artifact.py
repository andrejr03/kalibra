from __future__ import annotations

import builtins
from dataclasses import FrozenInstanceError
import json
import socket
import sys

import pytest

from src.frameworks import model_artifact


MODEL_SHA256 = "A" * 64
CHANGED_MODEL_SHA256 = "B" * 64


def test_model_artifact_objects_are_immutable() -> None:
    artifact = _explicit_artifact()

    with pytest.raises(FrozenInstanceError):
        artifact.artifact_kind = "changed"
    with pytest.raises(FrozenInstanceError):
        artifact.metadata.identity.identifier = "changed"
    with pytest.raises(FrozenInstanceError):
        artifact.reference.content_hash.content_sha256 = CHANGED_MODEL_SHA256
    with pytest.raises(TypeError):
        artifact.metadata.provenance.lineage[0][0] = "changed"


def test_equivalent_artifacts_have_deterministic_equality_and_hashing() -> None:
    first = _explicit_artifact()
    second = model_artifact.canonical_model_artifact(
        identity=" Kalibra/Inspection/Anomaly-Detector ",
        version=model_artifact.ModelVersion("1.2.3"),
        content_hash=MODEL_SHA256.lower(),
        artifact_path=" models/inspection-anomaly.onnx ",
        artifact_format=" ONNX ",
        producer=" Kalibra Fixture Builder ",
        provenance=" Generated from documented deterministic fixture recipe ",
        lineage={
            "source": "fixture-source-v1",
            "export": "onnx-export-v1",
        },
        framework_name=" ONNXRUNTIME ",
        framework_version="1.17.3",
        onnx_opset=17,
        compatibility_declaration="CPU baseline compatibility only",
    )

    assert first == second
    assert hash(first) == hash(second)
    assert hash(first.identity) == hash(second.identity)
    assert hash(first.content_hash) == hash(second.content_hash)


def test_model_artifact_fingerprint_is_stable_and_canonical() -> None:
    first = _explicit_artifact()
    equivalent = model_artifact.canonical_model_artifact(_explicit_artifact())
    changed = model_artifact.canonical_model_artifact(
        identity="kalibra/inspection/anomaly-detector",
        version="1.2.4",
        content_hash=MODEL_SHA256,
        artifact_uri="models/inspection-anomaly.onnx",
        artifact_format="onnx",
        producer="Kalibra Fixture Builder",
        provenance="Generated from documented deterministic fixture recipe",
        lineage=(
            ("source", "fixture-source-v1"),
            ("export", "onnx-export-v1"),
        ),
        framework_name="onnxruntime",
        framework_version="1.17.3",
        onnx_opset=17,
        compatibility_declaration="CPU baseline compatibility only",
    )

    first_fingerprint = model_artifact.model_artifact_fingerprint(first)

    assert first_fingerprint == (
        model_artifact.model_artifact_fingerprint(equivalent)
    )
    assert first_fingerprint == model_artifact.model_artifact_fingerprint(first)
    assert first_fingerprint != model_artifact.model_artifact_fingerprint(changed)
    assert len(first_fingerprint) == 64
    assert all(character in "0123456789abcdef" for character in first_fingerprint)


def test_canonical_model_json_is_stable() -> None:
    artifact = _explicit_artifact()

    first = model_artifact.canonical_model_json(artifact)
    second = model_artifact.canonical_model_json(artifact)

    assert first == second
    assert first == (
        '{"artifact_kind":"governed_model_artifact_v1",'
        '"metadata":{"compatibility":{"artifact_format":"onnx",'
        '"compatibility_declaration":"CPU baseline compatibility only",'
        '"framework_name":"onnxruntime","framework_version":"1.17.3",'
        '"onnx_opset":17},"identity":{"identifier":'
        '"kalibra/inspection/anomaly-detector"},'
        '"metadata_kind":"model_artifact_metadata_v1",'
        '"provenance":{"lineage":[["export","onnx-export-v1"],'
        '["source","fixture-source-v1"]],'
        '"producer":"Kalibra Fixture Builder",'
        '"provenance":"Generated from documented deterministic fixture recipe"},'
        '"version":{"semantic_version":"1.2.3"}},'
        '"reference":{"artifact_uri":"models/inspection-anomaly.onnx",'
        '"content_hash":{"algorithm":"sha256","content_sha256":"'
        + MODEL_SHA256.lower()
        + '"}}}'
    )
    assert json.loads(first) == json.loads(second)


def test_model_artifact_identity_is_deterministic() -> None:
    artifact = _explicit_artifact()

    assert model_artifact.model_artifact_identity(artifact) == (
        "kalibra/inspection/anomaly-detector@1.2.3#sha256:"
        + MODEL_SHA256.lower()
    )


def test_artifact_values_are_json_serializable() -> None:
    artifact = _explicit_artifact()
    values = (
        artifact.identity,
        artifact.version,
        artifact.content_hash,
        artifact.metadata.provenance,
        artifact.metadata.compatibility,
        artifact.reference,
        artifact.metadata,
        artifact,
    )

    for value in values:
        encoded = json.dumps(value.to_json_dict(), sort_keys=True)
        assert json.loads(encoded) == value.to_json_dict()


def test_model_artifact_ordering_is_stable() -> None:
    older = _explicit_artifact(version="1.2.3")
    newer = _explicit_artifact(version="1.2.4")

    assert sorted((newer, older)) == [older, newer]


def test_model_artifact_validation_accepts_valid_artifact() -> None:
    artifact = _explicit_artifact()

    validated = model_artifact.validate_model_artifact(artifact)

    assert validated == artifact
    assert validated.identity.identifier == "kalibra/inspection/anomaly-detector"
    assert validated.version.semantic_version == "1.2.3"
    assert validated.content_hash.content_sha256 == MODEL_SHA256.lower()


@pytest.mark.parametrize(
    "factory",
    (
        lambda: model_artifact.ModelIdentity(""),
        lambda: model_artifact.ModelIdentity("model identifier with spaces"),
        lambda: model_artifact.ModelIdentity("/leading-slash"),
        lambda: model_artifact.ModelVersion("1.2"),
        lambda: model_artifact.ModelVersion("01.2.3"),
        lambda: model_artifact.ModelHash("not-a-sha256"),
        lambda: model_artifact.ModelHash(MODEL_SHA256, digest=MODEL_SHA256),
        lambda: model_artifact.ModelProvenance(
            producer="",
            provenance="documented",
        ),
        lambda: model_artifact.ModelProvenance(
            producer="Kalibra",
            provenance="",
        ),
        lambda: model_artifact.ModelProvenance(
            producer="Kalibra",
            provenance="documented",
            lineage=(("source", "one"), ("source", "two")),
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="pytorch",
            framework_name="onnxruntime",
            framework_version="1.17.3",
            onnx_opset=17,
            compatibility_declaration="declared",
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="onnx",
            framework_name="tensorflow",
            framework_version="1.17.3",
            onnx_opset=17,
            compatibility_declaration="declared",
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="onnx",
            framework_name="onnxruntime",
            framework_version="1.17",
            onnx_opset=17,
            compatibility_declaration="declared",
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="onnx",
            framework_name="onnxruntime",
            framework_version="1.17.3",
            onnx_opset=True,
            compatibility_declaration="declared",
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="onnx",
            framework_name="onnxruntime",
            framework_version="1.17.3",
            onnx_opset=0,
            compatibility_declaration="declared",
        ),
        lambda: model_artifact.ModelCompatibility(
            artifact_format="onnx",
            framework_name="onnxruntime",
            framework_version="1.17.3",
            onnx_opset=17,
            compatibility_declaration="",
        ),
        lambda: model_artifact.ModelArtifactReference(
            artifact_uri="",
            content_hash=model_artifact.ModelHash(MODEL_SHA256),
        ),
        lambda: model_artifact.ModelArtifactReference(
            artifact_uri="models/model.onnx",
            artifact_path="models/model.onnx",
            content_hash=model_artifact.ModelHash(MODEL_SHA256),
        ),
        lambda: model_artifact.ModelArtifactMetadata(
            identity="model",
            version=model_artifact.ModelVersion("1.0.0"),
            provenance=model_artifact.ModelProvenance("Kalibra", "documented"),
            compatibility=model_artifact.ModelCompatibility(
                artifact_format="onnx",
                framework_name="onnxruntime",
                framework_version="1.17.3",
                onnx_opset=17,
                compatibility_declaration="declared",
            ),
        ),
        lambda: model_artifact.GovernedModelArtifact(
            reference="models/model.onnx",
            metadata=_explicit_artifact().metadata,
        ),
    ),
)
def test_model_artifact_validation_rejects_invalid_inputs(factory) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()


def test_model_artifact_validation_fails_closed_for_wrong_artifact_type() -> None:
    with pytest.raises(TypeError):
        model_artifact.validate_model_artifact({"artifact": "not-governed"})
    with pytest.raises(TypeError):
        model_artifact.canonical_model_artifact()
    with pytest.raises(TypeError):
        model_artifact.canonical_model_artifact(
            _explicit_artifact(),
            identity="unexpected",
        )


def test_model_artifact_substrate_exposes_no_runtime_or_inference_api() -> None:
    forbidden_public_names = {
        "Inference" + "Session",
        "OrtValue",
        "create_session",
        "create_tensor",
        "load_model",
        "predict",
        "run_inference",
    }

    assert set(dir(model_artifact)).isdisjoint(forbidden_public_names)


def test_model_artifact_does_not_create_runtime_sessions_or_load_models(
    monkeypatch,
) -> None:
    class RuntimeTrap:
        def __getattr__(self, name):
            raise AssertionError(
                "model artifact substrate must not access runtime objects"
            )

    monkeypatch.setitem(sys.modules, "onnxruntime", RuntimeTrap())

    artifact = _explicit_artifact()

    assert model_artifact.validate_model_artifact(artifact)
    assert model_artifact.canonical_model_artifact(artifact)
    assert model_artifact.canonical_model_json(artifact)
    assert model_artifact.model_artifact_fingerprint(artifact)
    assert model_artifact.model_artifact_identity(artifact)


def test_model_artifact_performs_no_filesystem_or_network_access(
    monkeypatch,
) -> None:
    def fail_filesystem_access(*args, **kwargs):
        raise AssertionError(
            "model artifact substrate must not access the filesystem"
        )

    def fail_network_access(*args, **kwargs):
        raise AssertionError(
            "model artifact substrate must not access the network"
        )

    monkeypatch.setattr(builtins, "open", fail_filesystem_access)
    monkeypatch.setattr(socket, "socket", fail_network_access)
    monkeypatch.setattr(socket, "create_connection", fail_network_access)

    artifact = _explicit_artifact(artifact_uri="models/missing-model.onnx")

    assert model_artifact.validate_model_artifact(artifact)
    assert model_artifact.canonical_model_artifact(artifact)
    assert model_artifact.canonical_model_json(artifact)
    assert model_artifact.model_artifact_fingerprint(artifact)
    assert model_artifact.model_artifact_identity(artifact)


def _explicit_artifact(
    *,
    version: str = "1.2.3",
    artifact_uri: str = "models/inspection-anomaly.onnx",
) -> model_artifact.GovernedModelArtifact:
    return model_artifact.canonical_model_artifact(
        identity="kalibra/inspection/anomaly-detector",
        version=version,
        content_hash=MODEL_SHA256,
        artifact_uri=artifact_uri,
        artifact_format="onnx",
        producer="Kalibra Fixture Builder",
        provenance="Generated from documented deterministic fixture recipe",
        lineage=(
            ("source", "fixture-source-v1"),
            ("export", "onnx-export-v1"),
        ),
        framework_name="onnxruntime",
        framework_version="1.17.3",
        onnx_opset=17,
        compatibility_declaration="CPU baseline compatibility only",
    )
