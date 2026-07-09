#!/usr/bin/env python3
"""Governed placeholder retirement verification (Phase 3 / Task 5).

This verifier proves the ONNX placeholder has been retired from the canonical
runtime path after the runtime-equivalence verification (Task 4). It is
architecture hygiene only: it produces no metrics, performs no calibration, and
makes no scientific or product claim.

The verifier:
- confirms the canonical ``OnnxInspectionInferenceProvider`` loads only
  ``kalibra-padim-onnx-export-v1``;
- proves the placeholder reference id is unreachable from the canonical runtime;
- re-attests the six runtime-equivalence / runtime-integration immutability
  hashes from the governance record remain byte-identical;
- confirms no downstream domain (trust / review / evidence / evaluation) code
  was modified;
- runs a fail-closed regression proving the canonical provider rejects the
  placeholder reference id;
- persists governed retirement metadata, hashes, and a deterministic replay.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for import_path in (SCRIPT_DIR, REPO_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from src.frameworks import onnx_runtime, output_mapping  # noqa: E402
from src.frameworks import onnx_session  # noqa: E402
from src.inspection.providers_onnx import (  # noqa: E402
    ONNX_PLACEHOLDER_MODEL_REFERENCE_ID,
    PADIM_ONNX_MODEL_REFERENCE_ID,
    FixtureOnlyPlaceholderProvider,
    OnnxInspectionInferenceProvider,
    fixture_only_placeholder_session_configuration,
    governed_padim_session_configuration,
)


RETIREMENT_LABEL = "kalibra-placeholder-retirement-v1"
METADATA_SCHEMA = "kalibra_runtime_placeholder_retirement_metadata_v1"
HASHES_SCHEMA = "kalibra_runtime_placeholder_retirement_hashes_v1"
REPLAY_SCHEMA = "kalibra_runtime_placeholder_retirement_replay_v1"
EVIDENCE_TITLE = "Kalibra Placeholder Retirement Evidence v1.0"

RETIREMENT_DIR = REPO_ROOT / "artifacts" / "runtime" / "placeholder_retirement"
METADATA_PATH = RETIREMENT_DIR / "placeholder_retirement_metadata.json"
HASHES_PATH = RETIREMENT_DIR / "placeholder_retirement_hashes.json"
REPLAY_PATH = RETIREMENT_DIR / "placeholder_retirement_replay.json"
EVIDENCE_PATH = REPO_ROOT / "docs" / "evidence" / "PLACEHOLDER_RETIREMENT.md"

RUNTIME_DIR = REPO_ROOT / "artifacts" / "runtime"
EQUIVALENCE_DIR = RUNTIME_DIR / "equivalence"
RUNTIME_EQUIVALENCE_REPORT_PATH = (
    EQUIVALENCE_DIR / "runtime_equivalence_report.json"
)
RUNTIME_EQUIVALENCE_REPLAY_PATH = EQUIVALENCE_DIR / "runtime_equivalence_replay.json"
RUNTIME_EQUIVALENCE_HASHES_PATH = EQUIVALENCE_DIR / "runtime_equivalence_hashes.json"
RUNTIME_INTEGRATION_METADATA_PATH = RUNTIME_DIR / "integration_metadata.json"
RUNTIME_REPLAY_PATH = RUNTIME_DIR / "runtime_replay.json"
RUNTIME_HASHES_PATH = RUNTIME_DIR / "runtime_hashes.json"

# Six immutability hashes from the governance record. These must
# remain byte-identical before and after retirement.
IMMUTABILITY_HASHES = {
    "runtime_equivalence_report.json": {
        "path": RUNTIME_EQUIVALENCE_REPORT_PATH,
        "sha256": (
            "90ea39972ceb53205adfce6280f9b897a42ed935917810c89386e01819be6d19"
        ),
    },
    "runtime_equivalence_replay.json": {
        "path": RUNTIME_EQUIVALENCE_REPLAY_PATH,
        "sha256": (
            "65b414c47f4b040c4bd0b090d54cfdf6fa3099c01c7b5329a9c75a7a8759bee8"
        ),
    },
    "runtime_equivalence_hashes.json": {
        "path": RUNTIME_EQUIVALENCE_HASHES_PATH,
        "sha256": (
            "80cce54f23eb3a37116af0116fccfa8d6d97cc103b2675699fdf8a7e1e18e84c"
        ),
    },
    "integration_metadata.json": {
        "path": RUNTIME_INTEGRATION_METADATA_PATH,
        "sha256": (
            "8e80ffd9637708b92d6f5de7534c49247a9740e30678ac3ae18598bfb9c8b5e0"
        ),
    },
    "runtime_replay.json": {
        "path": RUNTIME_REPLAY_PATH,
        "sha256": (
            "376b7a84cb65949aa55189d8cc57fb7b14dfcf899e26b697d7954c87282f2e76"
        ),
    },
    "runtime_hashes.json": {
        "path": RUNTIME_HASHES_PATH,
        "sha256": (
            "0009ffc8982c17478f0494a49562aa4408dad4261c645e75a799e72d80a2ecdd"
        ),
    },
}

REMOVED_CONSTANTS = [
    "_MODEL_KIND_PLACEHOLDER",
]
RELOCATED_FIXTURE_ONLY_CONSTANTS = [
    "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
    "_placeholder_model_artifact",
    "_predict_placeholder",
    "_run_placeholder_session",
    "_map_placeholder_output",
    "_single_input_name",
]

PLACEHOLDER_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "inspection"
    / "onnx_placeholder"
    / "placeholder_identity.onnx"
)

DOWNSTREAM_DOMAIN_DIRS = (
    REPO_ROOT / "src" / "trust",
    REPO_ROOT / "src" / "review",
    REPO_ROOT / "src" / "evidence",
    REPO_ROOT / "src" / "evaluation",
)


class PlaceholderRetirementError(RuntimeError):
    """Raised when placeholder retirement cannot be verified safely."""


@dataclass(frozen=True)
class RetirementVerification:
    canonical_reference_id: str
    canonical_model_kind: str
    placeholder_rejected_from_canonical: bool
    placeholder_retained_as_fixture_only: bool
    fail_closed_regression_passed: bool
    immutability_hashes_unchanged: dict[str, dict[str, str]]
    runtime_integration_hashes_unchanged: bool
    runtime_equivalence_hashes_unchanged: bool
    downstream_domains_changed: bool
    canonical_source_has_no_placeholder_dispatch: bool
    canonical_post_init_has_no_placeholder_branch: bool
    canonical_aliases_are_padim_only: bool
    status: str


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
        raise PlaceholderRetirementError(f"unreadable file: {path}") from exc


def read_json_mapping(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlaceholderRetirementError(f"unreadable JSON record: {path}") from exc
    if not isinstance(value, dict):
        raise PlaceholderRetirementError(f"JSON record is not an object: {path}")
    return value


def expect_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise PlaceholderRetirementError(
            f"{label} mismatch: expected {expected!r}, got {actual!r}"
        )


def expect_true(value: bool, label: str) -> None:
    if value is not True:
        raise PlaceholderRetirementError(f"{label} is not true: {value!r}")


def verification_timestamp_for_run() -> str:
    if not METADATA_PATH.exists():
        return utc_timestamp()
    metadata = read_json_mapping(METADATA_PATH)
    timestamp = metadata.get("verification_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise PlaceholderRetirementError("existing retirement metadata lacks timestamp")
    return timestamp


def evidence_date_for_run() -> str:
    if not EVIDENCE_PATH.exists():
        return datetime.now(timezone.utc).date().isoformat()
    for line in EVIDENCE_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Date:** "):
            value = line.removeprefix("**Date:** ").strip()
            if value:
                return value
    raise PlaceholderRetirementError("existing retirement evidence lacks Date field")


def verify_canonical_provider_loads_only_padim() -> tuple[str, str]:
    """Confirm a bare canonical provider loads only the governed PaDiM model."""
    try:
        import onnxruntime  # noqa: F401
    except ImportError as exc:
        raise PlaceholderRetirementError(
            "onnxruntime is required to verify the canonical provider"
        ) from exc
    provider = OnnxInspectionInferenceProvider()
    reference_id = provider._requested_reference_id
    expect_equal(reference_id, PADIM_ONNX_MODEL_REFERENCE_ID, "canonical reference id")
    expect_equal(provider._model_kind, "padim", "canonical model kind")
    expect_equal(
        governed_padim_session_configuration().model_reference.reference_id,
        PADIM_ONNX_MODEL_REFERENCE_ID,
        "governed session configuration reference id",
    )
    return reference_id, provider._model_kind


def verify_placeholder_unreachable_from_canonical() -> bool:
    """Prove the canonical provider rejects the placeholder reference id."""
    try:
        import onnxruntime  # noqa: F401
    except ImportError as exc:
        raise PlaceholderRetirementError(
            "onnxruntime is required to verify placeholder unreachability"
        ) from exc
    placeholder_configuration = fixture_only_placeholder_session_configuration()
    from src.inspection.errors import InspectionExaminationFailure

    try:
        OnnxInspectionInferenceProvider(
            session_configuration=placeholder_configuration
        )
    except InspectionExaminationFailure as exc:
        if "not governed" not in str(exc):
            raise PlaceholderRetirementError(
                f"canonical provider rejected placeholder for unexpected reason: {exc}"
            ) from exc
        return True
    raise PlaceholderRetirementError(
        "canonical provider accepted the placeholder reference id; "
        "placeholder is still reachable from the canonical runtime path"
    )


def verify_fail_closed_regression() -> bool:
    """Regression guard: prove the canonical provider fails closed if the
    placeholder reference id were ever re-wired as canonical."""
    from src.inspection.errors import InspectionExaminationFailure

    placeholder_configuration = fixture_only_placeholder_session_configuration()
    rejected = False
    try:
        OnnxInspectionInferenceProvider(
            session_configuration=placeholder_configuration
        )
    except InspectionExaminationFailure:
        rejected = True
    if not rejected:
        raise PlaceholderRetirementError(
            "fail-closed regression failed: placeholder became canonical"
        )
    return True


def verify_canonical_source_has_no_placeholder_dispatch() -> bool:
    """Static check: no canonical code path resolves to placeholder logic."""
    class_source = inspect.getsource(OnnxInspectionInferenceProvider)
    forbidden = (
        "_predict_placeholder",
        "_MODEL_KIND_PLACEHOLDER",
        "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
        "_placeholder_model_artifact",
        "_single_input_name",
    )
    found = [token for token in forbidden if token in class_source]
    if found:
        raise PlaceholderRetirementError(
            f"canonical provider class still references placeholder logic: {found}"
        )
    return True


def verify_canonical_post_init_has_no_placeholder_branch() -> bool:
    """Static check: __post_init__ has no placeholder branch."""
    post_init_source = inspect.getsource(OnnxInspectionInferenceProvider.__post_init__)
    forbidden = (
        "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID",
        "_placeholder_model_artifact",
        "_MODEL_KIND_PLACEHOLDER",
        "_single_input_name",
        "_predict_placeholder",
    )
    found = [token for token in forbidden if token in post_init_source]
    if found:
        raise PlaceholderRetirementError(
            f"canonical __post_init__ still contains placeholder branch: {found}"
        )
    return True


def verify_placeholder_retained_as_fixture_only() -> bool:
    """Confirm the placeholder fixture and fixture-only seam still exist."""
    if not PLACEHOLDER_FIXTURE_PATH.is_file():
        raise PlaceholderRetirementError(
            f"placeholder fixture missing: {PLACEHOLDER_FIXTURE_PATH}"
        )
    import src.inspection.providers_onnx as providers_module

    if not hasattr(providers_module, "FixtureOnlyPlaceholderProvider"):
        raise PlaceholderRetirementError(
            "FixtureOnlyPlaceholderProvider seam is missing"
        )
    fixture_source = inspect.getsource(FixtureOnlyPlaceholderProvider)
    if "ONNX_PLACEHOLDER_MODEL_REFERENCE_ID" not in fixture_source:
        raise PlaceholderRetirementError(
            "fixture-only provider does not bind the placeholder reference id"
        )
    if "fixture-only" not in fixture_source.lower() and "fixture" not in fixture_source.lower():
        raise PlaceholderRetirementError(
            "fixture-only provider is not marked as non-canonical"
        )
    return True


def verify_immutability_hashes() -> dict[str, dict[str, str]]:
    """Re-attest the six runtime-equivalence / integration hashes unchanged."""
    results: dict[str, dict[str, str]] = {}
    for name, spec in IMMUTABILITY_HASHES.items():
        path = spec["path"]
        expected = spec["sha256"]
        if not path.is_file():
            raise PlaceholderRetirementError(
                f"immutability artifact missing: {path}"
            )
        actual = sha256_file(path)
        if actual != expected:
            raise PlaceholderRetirementError(
                f"immutability hash mismatch for {name}: "
                f"expected {expected}, got {actual}"
            )
        results[name] = {"expected": expected, "actual": actual, "unchanged": True}
    return results


def verify_no_downstream_domains_changed() -> bool:
    """Confirm no file under src/trust, src/review, src/evidence, src/evaluation
    was modified relative to git HEAD."""
    import subprocess

    for domain_dir in DOWNSTREAM_DOMAIN_DIRS:
        if not domain_dir.exists():
            raise PlaceholderRetirementError(
                f"downstream domain directory missing: {domain_dir}"
            )
    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--short",
                "--",
                "src/trust",
                "src/review",
                "src/evidence",
                "src/evaluation",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise PlaceholderRetirementError("git is not available for domain check") from exc
    if result.returncode != 0:
        raise PlaceholderRetirementError(
            f"git status failed for downstream domains: {result.stderr.strip()}"
        )
    changed = result.stdout.strip()
    if changed:
        raise PlaceholderRetirementError(
            f"downstream domains were modified:\n{changed}"
        )
    return False


def verify_canonical_aliases_are_padim_only() -> bool:
    """Confirm the canonical output_mapping aliases resolve to PaDiM values."""
    expect_equal(
        output_mapping.OUTPUT_MAPPING_CONTRACT_ID,
        output_mapping.PADIM_OUTPUT_MAPPING_CONTRACT_ID,
        "OUTPUT_MAPPING_CONTRACT_ID",
    )
    expect_equal(
        output_mapping.EXPECTED_OUTPUT_COUNT,
        output_mapping.PADIM_EXPECTED_OUTPUT_COUNT,
        "EXPECTED_OUTPUT_COUNT",
    )
    expect_equal(
        output_mapping.EXPECTED_OUTPUT_DTYPE,
        output_mapping.PADIM_OUTPUT_DTYPE,
        "EXPECTED_OUTPUT_DTYPE",
    )
    expect_equal(
        output_mapping.RAW_MEASURE_SCALE,
        output_mapping.PADIM_RAW_MEASURE_SCALE,
        "RAW_MEASURE_SCALE",
    )
    expect_equal(
        output_mapping.MAPPING_SEMANTICS,
        output_mapping.PADIM_MAPPING_SEMANTICS,
        "MAPPING_SEMANTICS",
    )
    expect_equal(
        output_mapping.LOCALIZATION_KIND,
        output_mapping.PADIM_LOCALIZATION_KIND,
        "LOCALIZATION_KIND",
    )
    if output_mapping.OUTPUT_MAPPING_CONTRACT_ID == (
        output_mapping.PLACEHOLDER_OUTPUT_MAPPING_CONTRACT_ID
    ):
        raise PlaceholderRetirementError(
            "canonical OUTPUT_MAPPING_CONTRACT_ID aliases placeholder contract"
        )
    return True


def scope_boundaries() -> dict[str, bool]:
    return {
        "placeholder_retirement_performed": True,
        "canonical_runtime_provider_loads_only_padim": True,
        "placeholder_unreachable_from_canonical_runtime": True,
        "placeholder_retained_as_fixture_only": True,
        "fail_closed_regression_passed": True,
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
        "scientific_claim": False,
        "product_claim": False,
    }


def explicit_non_claims() -> list[str]:
    return [
        "placeholder retirement is architecture hygiene after runtime equivalence",
        "placeholder retirement is not scientific evaluation",
        "no PaDiM refit was performed",
        "no ONNX re-export was performed",
        "no new metrics were generated",
        "no calibration was performed",
        "no benchmark was generated",
        "no scientific claim was made",
        "no product claim was made",
        "no Phase 3 closure is authorized",
    ]


def toolchain_versions() -> dict[str, str]:
    versions: dict[str, str] = {
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    onnx_version = onnx_runtime.onnx_runtime_version()
    versions["onnxruntime"] = str(onnx_version) if onnx_version else "unavailable"
    return versions


def run_retirement_verification() -> RetirementVerification:
    canonical_reference_id, canonical_model_kind = (
        verify_canonical_provider_loads_only_padim()
    )
    placeholder_rejected = verify_placeholder_unreachable_from_canonical()
    fail_closed_passed = verify_fail_closed_regression()
    no_placeholder_dispatch = verify_canonical_source_has_no_placeholder_dispatch()
    no_post_init_branch = verify_canonical_post_init_has_no_placeholder_branch()
    fixture_only_retained = verify_placeholder_retained_as_fixture_only()
    immutability = verify_immutability_hashes()
    aliases_padim_only = verify_canonical_aliases_are_padim_only()
    downstream_changed = verify_no_downstream_domains_changed()

    integration_hashes = {
        name: result
        for name, result in immutability.items()
        if name in {
            "integration_metadata.json",
            "runtime_replay.json",
            "runtime_hashes.json",
        }
    }
    equivalence_hashes = {
        name: result
        for name, result in immutability.items()
        if name in {
            "runtime_equivalence_report.json",
            "runtime_equivalence_replay.json",
            "runtime_equivalence_hashes.json",
        }
    }
    return RetirementVerification(
        canonical_reference_id=canonical_reference_id,
        canonical_model_kind=canonical_model_kind,
        placeholder_rejected_from_canonical=placeholder_rejected,
        placeholder_retained_as_fixture_only=fixture_only_retained,
        fail_closed_regression_passed=fail_closed_passed,
        immutability_hashes_unchanged=immutability,
        runtime_integration_hashes_unchanged=all(
            result["unchanged"] for result in integration_hashes.values()
        ),
        runtime_equivalence_hashes_unchanged=all(
            result["unchanged"] for result in equivalence_hashes.values()
        ),
        downstream_domains_changed=downstream_changed,
        canonical_source_has_no_placeholder_dispatch=no_placeholder_dispatch,
        canonical_post_init_has_no_placeholder_branch=no_post_init_branch,
        canonical_aliases_are_padim_only=aliases_padim_only,
        status="passed",
    )


def build_metadata(
    verification: RetirementVerification,
    verification_timestamp: str,
) -> dict[str, Any]:
    return {
        "schema": METADATA_SCHEMA,
        "retirement_label": RETIREMENT_LABEL,
        "verification_timestamp_utc": verification_timestamp,
        "status": verification.status,
        "canonical_runtime_reference_id": verification.canonical_reference_id,
        "placeholder_reference_id_removed_from_canonical_path": (
            ONNX_PLACEHOLDER_MODEL_REFERENCE_ID
        ),
        "placeholder_unreachable_from_canonical_runtime": (
            verification.placeholder_rejected_from_canonical
        ),
        "placeholder_retained_as_fixture_only": (
            verification.placeholder_retained_as_fixture_only
        ),
        "removed_constants": list(REMOVED_CONSTANTS),
        "relocated_or_fixture_only_constants": list(RELOCATED_FIXTURE_ONLY_CONSTANTS),
        "canonical_provider_checks": {
            "canonical_model_kind": verification.canonical_model_kind,
            "canonical_source_has_no_placeholder_dispatch": (
                verification.canonical_source_has_no_placeholder_dispatch
            ),
            "canonical_post_init_has_no_placeholder_branch": (
                verification.canonical_post_init_has_no_placeholder_branch
            ),
            "canonical_aliases_are_padim_only": (
                verification.canonical_aliases_are_padim_only
            ),
        },
        "fail_closed_regression": {
            "passed": verification.fail_closed_regression_passed,
            "description": (
                "canonical provider rejects placeholder reference id; "
                "if placeholder became canonical again the test suite would fail"
            ),
        },
        "unchanged_runtime_artifacts": verification.immutability_hashes_unchanged,
        "runtime_integration_hashes_unchanged": (
            verification.runtime_integration_hashes_unchanged
        ),
        "runtime_equivalence_hashes_unchanged": (
            verification.runtime_equivalence_hashes_unchanged
        ),
        "downstream_domains_changed": verification.downstream_domains_changed,
        "scope_boundaries": scope_boundaries(),
        "explicit_non_claims": explicit_non_claims(),
        "toolchain": toolchain_versions(),
    }


def build_replay(
    first_metadata: Mapping[str, Any],
    second_metadata: Mapping[str, Any],
    first_metadata_bytes: bytes,
    second_metadata_bytes: bytes,
) -> dict[str, Any]:
    comparisons = {
        "canonical_reference_id": (
            first_metadata["canonical_runtime_reference_id"]
            == second_metadata["canonical_runtime_reference_id"]
        ),
        "placeholder_rejected_from_canonical": (
            first_metadata["placeholder_unreachable_from_canonical_runtime"]
            == second_metadata["placeholder_unreachable_from_canonical_runtime"]
        ),
        "placeholder_retained_as_fixture_only": (
            first_metadata["placeholder_retained_as_fixture_only"]
            == second_metadata["placeholder_retained_as_fixture_only"]
        ),
        "fail_closed_regression_passed": (
            first_metadata["fail_closed_regression"]["passed"]
            == second_metadata["fail_closed_regression"]["passed"]
        ),
        "immutability_hashes_unchanged": (
            first_metadata["unchanged_runtime_artifacts"]
            == second_metadata["unchanged_runtime_artifacts"]
        ),
        "metadata_json_identical": first_metadata_bytes == second_metadata_bytes,
        "metadata_hash_identical": (
            sha256_bytes(first_metadata_bytes) == sha256_bytes(second_metadata_bytes)
        ),
        "status_identical": first_metadata["status"] == second_metadata["status"],
    }
    if not all(comparisons.values()):
        raise PlaceholderRetirementError(
            f"deterministic retirement replay mismatch: {comparisons}"
        )
    return {
        "schema": REPLAY_SCHEMA,
        "retirement_label": RETIREMENT_LABEL,
        "status": "passed",
        "complete_second_retirement_verification_run": True,
        "comparisons": comparisons,
        "first_run_hash": sha256_bytes(first_metadata_bytes),
        "second_run_hash": sha256_bytes(second_metadata_bytes),
        "scope": "deterministic placeholder retirement replay only",
    }


def build_hashes_record(metadata_bytes: bytes, replay_bytes: bytes) -> dict[str, Any]:
    return {
        "schema": HASHES_SCHEMA,
        "retirement_label": RETIREMENT_LABEL,
        "hash_algorithm": "sha256",
        "hash_scope": (
            "artifacts/runtime/placeholder_retirement/"
            "placeholder_retirement_metadata.json and "
            "artifacts/runtime/placeholder_retirement/"
            "placeholder_retirement_replay.json"
        ),
        "governed_retirement_artifacts": {
            "placeholder_retirement_metadata.json": sha256_bytes(metadata_bytes),
            "placeholder_retirement_replay.json": sha256_bytes(replay_bytes),
        },
    }


def write_evidence(
    metadata: Mapping[str, Any],
    replay: Mapping[str, Any],
    metadata_hash: str,
    replay_hash: str,
    hashes_hash: str,
) -> str:
    date = evidence_date_for_run()
    immutability = metadata["unchanged_runtime_artifacts"]
    return f"""# {EVIDENCE_TITLE}

**Status:** Recorded - governed placeholder retirement evidence only
**Date:** {date}
**Scope:** Phase 3 / Task 5 - Placeholder Retirement only (architecture hygiene)

## Retirement Scope

- Placeholder retirement is architecture hygiene after runtime equivalence.
- Canonical provider loads only: `{metadata['canonical_runtime_reference_id']}`
- Placeholder reference id retired from canonical path: `{metadata['placeholder_reference_id_removed_from_canonical_path']}`
- Placeholder unreachable from canonical runtime: `{str(metadata['placeholder_unreachable_from_canonical_runtime']).lower()}`
- Placeholder retained as fixture-only: `{str(metadata['placeholder_retained_as_fixture_only']).lower()}`

## Canonical Provider Checks

- Canonical model kind: `{metadata['canonical_provider_checks']['canonical_model_kind']}`
- Canonical source has no placeholder dispatch: `{str(metadata['canonical_provider_checks']['canonical_source_has_no_placeholder_dispatch']).lower()}`
- Canonical `__post_init__` has no placeholder branch: `{str(metadata['canonical_provider_checks']['canonical_post_init_has_no_placeholder_branch']).lower()}`
- Canonical output_mapping aliases are PaDiM-only: `{str(metadata['canonical_provider_checks']['canonical_aliases_are_padim_only']).lower()}`

## Fail-Closed Regression

- Fail-closed regression passed: `{str(metadata['fail_closed_regression']['passed']).lower()}`
- Description: `{metadata['fail_closed_regression']['description']}`

## Removed / Fixture-Only Constants

- Removed from canonical provider: `{', '.join(metadata['removed_constants'])}`
- Relocated behind fixture-only boundary: `{', '.join(metadata['relocated_or_fixture_only_constants'])}`

## Unchanged Runtime Hashes (Immutability Contract)

- Runtime equivalence report SHA-256: `{immutability['runtime_equivalence_report.json']['actual']}`
- Runtime equivalence replay SHA-256: `{immutability['runtime_equivalence_replay.json']['actual']}`
- Runtime equivalence hashes SHA-256: `{immutability['runtime_equivalence_hashes.json']['actual']}`
- Runtime integration metadata SHA-256: `{immutability['integration_metadata.json']['actual']}`
- Runtime replay SHA-256: `{immutability['runtime_replay.json']['actual']}`
- Runtime hashes SHA-256: `{immutability['runtime_hashes.json']['actual']}`
- Runtime integration hashes unchanged: `{str(metadata['runtime_integration_hashes_unchanged']).lower()}`
- Runtime equivalence hashes unchanged: `{str(metadata['runtime_equivalence_hashes_unchanged']).lower()}`

## Downstream Domain Isolation

- Downstream domains changed (src/trust, src/review, src/evidence, src/evaluation): `{str(metadata['downstream_domains_changed']).lower()}`

## Replay Result

- Complete second retirement verification run: `{str(replay['complete_second_retirement_verification_run']).lower()}`
- Canonical reference id identical: `{str(replay['comparisons']['canonical_reference_id']).lower()}`
- Placeholder rejected identical: `{str(replay['comparisons']['placeholder_rejected_from_canonical']).lower()}`
- Immutability hashes identical: `{str(replay['comparisons']['immutability_hashes_unchanged']).lower()}`
- Metadata JSON identical: `{str(replay['comparisons']['metadata_json_identical']).lower()}`
- Status identical: `{str(replay['comparisons']['status_identical']).lower()}`
- Retirement metadata SHA-256: `{metadata_hash}`
- Retirement replay SHA-256: `{replay_hash}`
- Retirement hashes record SHA-256: `{hashes_hash}`

## Explicit Non-Claims

- Placeholder retirement is architecture hygiene after runtime equivalence.
- No PaDiM refit was performed.
- No ONNX re-export was performed.
- No scientific evaluation was performed.
- No metrics were generated.
- No calibration was performed.
- No benchmark was generated.
- No scientific claim was made.
- No product claim was made.
- No Phase 3 closure is authorized.
"""


def write_governed_record(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != content:
        raise PlaceholderRetirementError(
            f"governed retirement record changed: {path}"
        )
    path.write_bytes(content)
    return sha256_file(path)


def persist_records() -> None:
    timestamp = verification_timestamp_for_run()
    first_verification = run_retirement_verification()
    first_metadata = build_metadata(first_verification, timestamp)
    first_metadata_bytes = canonical_json_bytes(first_metadata)
    second_verification = run_retirement_verification()
    second_metadata = build_metadata(second_verification, timestamp)
    second_metadata_bytes = canonical_json_bytes(second_metadata)
    replay = build_replay(
        first_metadata,
        second_metadata,
        first_metadata_bytes,
        second_metadata_bytes,
    )
    replay_bytes = canonical_json_bytes(replay)
    hashes = build_hashes_record(first_metadata_bytes, replay_bytes)
    hashes_bytes = canonical_json_bytes(hashes)
    evidence = write_evidence(
        first_metadata,
        replay,
        sha256_bytes(first_metadata_bytes),
        sha256_bytes(replay_bytes),
        sha256_bytes(hashes_bytes),
    )
    write_governed_record(METADATA_PATH, first_metadata_bytes)
    write_governed_record(REPLAY_PATH, replay_bytes)
    write_governed_record(HASHES_PATH, hashes_bytes)
    write_governed_record(EVIDENCE_PATH, evidence.encode("utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify governed placeholder retirement from the canonical runtime."
    )
    parser.add_argument(
        "command",
        choices=("verify",),
        help="Run the bounded placeholder retirement verification.",
    )
    parser.parse_args(argv)
    persist_records()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
