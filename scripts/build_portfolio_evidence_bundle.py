#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import html
import io
import json
from pathlib import Path
import re
from string import Template
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_FOR_IMPORT))

from src.prototype_ui.local_provider_projection import (
    build_local_provider_demo_projection,
)


RUNTIME_VISUAL_INPUT_ID = "visa-inference-input-07fabbcc7f1fc18cdff4634f"
RUNTIME_VISUAL_MEDIA_DIR = "media/runtime-inspection"
RUNTIME_VISUAL_INPUT_ASSET = f"{RUNTIME_VISUAL_MEDIA_DIR}/pcb4-049-input.jpg"
RUNTIME_VISUAL_HEATMAP_ASSET = f"{RUNTIME_VISUAL_MEDIA_DIR}/pcb4-049-padim-map.png"
RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET = (
    f"{RUNTIME_VISUAL_MEDIA_DIR}/pcb4-049-anomaly-overlay.png"
)
RUNTIME_VISUAL_LOCALIZATION_ASSET = f"{RUNTIME_VISUAL_MEDIA_DIR}/pcb4-049-localization.png"
RUNTIME_VISUAL_MANIFEST_ASSET = f"{RUNTIME_VISUAL_MEDIA_DIR}/manifest.json"
RUNTIME_VISUAL_OVERLAY_ALPHA = 0.33
RUNTIME_VISUAL_COLOUR_MAP = "kalibra_raw_anomaly_six_stop_linear_rgb_v1"
RUNTIME_VISUAL_INTERPOLATION = "bilinear (presentation-only)"
RUNTIME_VISUAL_RAW_MAP_INTERPOLATION = "nearest-neighbour"
RUNTIME_VISUAL_PALETTE = (
    (5, 7, 13),
    (18, 43, 88),
    (96, 49, 111),
    (202, 65, 64),
    (238, 158, 63),
    (255, 238, 174),
)

BUNDLE_NAMES = (
    "meta",
    "runtime",
    "evaluation",
    "equivalence",
    "evidence",
    "architecture",
    "boundaries",
    "timeline",
)

DATA_START = "<!-- KALIBRA_DATA:START -->"
DATA_END = "<!-- KALIBRA_DATA:END -->"
DATA_BLOCK_RE = re.compile(
    rf"{re.escape(DATA_START)}.*?{re.escape(DATA_END)}",
    re.DOTALL,
)


class PortfolioEvidenceError(RuntimeError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the governed Kalibra portfolio evidence bundle."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare generated output with committed portfolio files.",
    )
    parser.add_argument(
        "--review-head",
        help="Override the review HEAD short SHA for reproducible builds.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.expanduser().resolve()
    try:
        if args.check:
            review_head = args.review_head or committed_portfolio_review_head(repo_root)
            diffs = check_portfolio(repo_root, review_head=review_head)
            if diffs:
                print("portfolio evidence bundle drift detected:", file=sys.stderr)
                for diff in diffs:
                    print(f"- {diff}", file=sys.stderr)
                return 1
            return 0
        review_head = args.review_head or current_git_head(repo_root)
        generate_portfolio(repo_root, review_head=review_head)
        return 0
    except PortfolioEvidenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def current_git_head(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def committed_portfolio_review_head(repo_root: Path) -> str:
    meta_path = repo_root / "portfolio/data/meta.json"
    meta = read_json_required(meta_path)
    review_head = require_path(meta, "review_head", str(meta_path))
    if not isinstance(review_head, str) or not review_head:
        raise PortfolioEvidenceError(
            f"{meta_path} has invalid required field review_head"
        )
    return review_head


def generate_portfolio(repo_root: Path, *, review_head: str) -> None:
    outputs = render_outputs(repo_root, review_head=review_head)
    for relative_path, content in outputs.items():
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def check_portfolio(repo_root: Path, *, review_head: str) -> list[str]:
    diffs: list[str] = []
    for relative_path, expected in render_outputs(
        repo_root, review_head=review_head
    ).items():
        target = repo_root / relative_path
        if not target.exists():
            diffs.append(f"{relative_path} is missing")
            continue
        actual = target.read_bytes()
        if actual != expected:
            diffs.append(_diff_summary(relative_path, actual, expected))
    return diffs


def render_outputs(repo_root: Path, *, review_head: str) -> dict[str, bytes]:
    runtime_visual = build_governed_runtime_visual_projection(repo_root)
    bundles = build_bundles(
        repo_root,
        review_head=review_head,
        runtime_visual=runtime_visual["bundle"],
    )
    outputs: dict[str, bytes] = {}
    for name in BUNDLE_NAMES:
        outputs[f"portfolio/data/{name}.json"] = encode_json(bundles[name])
    outputs["portfolio/index.html"] = render_index_html(repo_root, bundles)
    for relative_path, content in runtime_visual["assets"].items():
        outputs[f"portfolio/{relative_path}"] = content
        outputs[f"assets/portfolio-experience/{relative_path}"] = content
    return outputs


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def build_bundles(
    repo_root: Path,
    *,
    review_head: str,
    runtime_visual: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.expanduser().resolve()
    artifact_hashes = read_json_required(
        repo_root / "artifacts/padim/artifact_hashes.json"
    )
    integration = read_json_required(
        repo_root / "artifacts/runtime/integration_metadata.json"
    )
    runtime_replay = read_json_required(
        repo_root / "artifacts/runtime/runtime_replay.json"
    )
    equivalence_report = read_json_required(
        repo_root
        / "artifacts/runtime/equivalence/runtime_equivalence_report.json"
    )
    scientific_evidence = read_text_required(
        repo_root / "docs/evidence/SCIENTIFIC_EVALUATION.md"
    )
    architecture_doc = read_text_required(
        repo_root / "docs/engineering/PORTFOLIO_UX_ARCHITECTURE.md"
    )
    runtime_milestone = read_text_required(
        repo_root / "docs/engineering/RUNTIME_INTEGRATION_MILESTONE.md"
    )
    _require_source_tokens(
        architecture_doc,
        [
            "Inspection Engine",
            "Trust Qualification",
            "Human Review",
            "Calibrated confidence",
            "Not yet demonstrated",
        ],
        "portfolio UX architecture",
    )
    _require_source_tokens(
        runtime_milestone,
        ["canonical", "runtime", "equivalence"],
        "runtime integration milestone",
    )

    if runtime_visual is None:
        runtime_visual = build_governed_runtime_visual_projection(repo_root)["bundle"]
    model_sha256 = require_key(
        require_path(
            artifact_hashes,
            "governed_export_artifacts",
            "artifacts/padim/artifact_hashes.json",
        ),
        "model.onnx",
        "artifacts/padim/artifact_hashes.json",
    )
    integration_model_sha = require_path(
        integration,
        "model_artifact_identity.model_sha256",
        "artifacts/runtime/integration_metadata.json",
    )
    if model_sha256 != integration_model_sha:
        raise PortfolioEvidenceError(
            "model SHA-256 differs between artifact hashes and integration metadata"
        )

    session_config_hash = require_path(
        integration,
        "session_configuration_hash",
        "artifacts/runtime/integration_metadata.json",
    )
    placeholder_used = require_path(
        integration,
        "provider_configuration.placeholder_used_on_canonical_runtime_path",
        "artifacts/runtime/integration_metadata.json",
    )
    if placeholder_used is not False:
        raise PortfolioEvidenceError(
            "canonical runtime path is not recorded as placeholder-free"
        )

    evaluation = build_evaluation_bundle(scientific_evidence)
    equivalence = build_equivalence_bundle(equivalence_report, runtime_replay)
    runtime = build_runtime_bundle(
        runtime_visual,
        integration,
        runtime_replay,
        model_sha256,
        session_config_hash,
    )
    meta = {
        "evidence_basis": "Single-seed \u00b7 VisA-proxy",
        "evidence_basis_sentence": "Single-seed, VisA-proxy evidence.",
        "hero_proof_title": "RUNTIME EQUIVALENCE: VERIFIED \u00b7 REPLAY: PASSED",
        "model_sha256": model_sha256,
        "model_sha256_short": short_hash(model_sha256),
        "offline_mode": True,
        "review_head": review_head,
    }
    evidence = build_evidence_bundle(
        model_sha256,
        session_config_hash,
        integration,
        equivalence,
    )
    architecture = build_architecture_bundle()
    boundaries = build_boundaries_bundle()
    timeline = build_timeline_bundle()

    return {
        "meta": meta,
        "runtime": runtime,
        "evaluation": evaluation,
        "equivalence": equivalence,
        "evidence": evidence,
        "architecture": architecture,
        "boundaries": boundaries,
        "timeline": timeline,
    }


def build_local_provider_projection(repo_root: Path) -> dict[str, Any]:
    fixture_path = repo_root / "tests/fixtures/inspection/blob_defect.pgm"
    if not fixture_path.exists():
        raise PortfolioEvidenceError(f"missing source file: {fixture_path}")
    return build_local_provider_demo_projection(
        fixture_path=fixture_path,
        repo_root=repo_root,
    )


def build_governed_runtime_visual_projection(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.expanduser().resolve()
    governed_image = (
        repo_root
        / "data/visa/extracted/pcb4/Data/Images/Anomaly/049.JPG"
    )
    governed_map = (
        repo_root
        / "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy"
    )
    if not governed_image.is_file() or not governed_map.is_file():
        return _load_committed_runtime_visual_projection(repo_root)
    return _build_governed_runtime_visual_projection(repo_root)


def _load_committed_runtime_visual_projection(repo_root: Path) -> dict[str, Any]:
    runtime_path = repo_root / "portfolio/data/runtime.json"
    runtime = read_json_required(runtime_path)
    visual = require_path(runtime, "visual", str(runtime_path))
    if not isinstance(visual, Mapping):
        raise PortfolioEvidenceError(f"{runtime_path} visual is not an object")

    manifest_relative = require_path(
        visual, "manifest.asset_path", str(runtime_path)
    )
    manifest_path = repo_root / "portfolio" / manifest_relative
    manifest_bytes = _read_file_with_sha256(
        manifest_path,
        require_path(visual, "manifest.sha256", str(runtime_path)),
    )
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "kalibra_portfolio_runtime_visual_projection_v2":
        raise PortfolioEvidenceError(
            f"unexpected committed runtime visual schema: {manifest_path}"
        )

    asset_contracts = (
        ("input_asset", "input_asset_sha256"),
        ("anomaly_map_asset", "anomaly_map_asset_sha256"),
        ("anomaly_overlay_asset", "anomaly_overlay_asset_sha256"),
        ("localization_asset", "localization_asset_sha256"),
    )
    assets: dict[str, bytes] = {manifest_relative: manifest_bytes}
    for path_key, hash_key in asset_contracts:
        relative_path = require_key(manifest, path_key, str(manifest_path))
        expected_hash = require_key(manifest, hash_key, str(manifest_path))
        assets[relative_path] = _read_file_with_sha256(
            repo_root / "portfolio" / relative_path,
            expected_hash,
        )

    expected_visual_values = {
        "anomaly_map.asset_path": manifest["anomaly_map_asset"],
        "anomaly_map.asset_sha256": manifest["anomaly_map_asset_sha256"],
        "anomaly_map.sha256": manifest["anomaly_map_sha256"],
        "anomaly_overlay.asset_path": manifest["anomaly_overlay_asset"],
        "anomaly_overlay.asset_sha256": manifest["anomaly_overlay_asset_sha256"],
        "input.asset_path": manifest["input_asset"],
        "input.asset_sha256": manifest["input_asset_sha256"],
        "localization.asset_path": manifest["localization_asset"],
        "localization.asset_sha256": manifest["localization_asset_sha256"],
        "prediction_id": manifest["prediction_id"],
        "split": manifest["split"],
    }
    for path, expected in expected_visual_values.items():
        actual = require_path(visual, path, str(runtime_path))
        if actual != expected:
            raise PortfolioEvidenceError(
                f"committed runtime visual mismatch at {path}: "
                f"expected {expected!r}, got {actual!r}"
            )

    return {"assets": assets, "bundle": dict(visual)}


def _build_governed_runtime_visual_projection(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.expanduser().resolve()
    inputs = read_json_required(
        repo_root / "data/visa/derived/padim/inference/metadata/inference_inputs.json"
    )
    dataset_identity = read_json_required(
        repo_root / "data/visa/derived/padim/inference/metadata/dataset_identity.json"
    )
    inference_hashes = read_json_required(
        repo_root / "data/visa/derived/padim/inference/artifact_hashes.json"
    )
    failure_analysis = read_json_required(
        repo_root / "data/visa/derived/padim/evaluation/failure_analysis/failure_analysis.json"
    )

    sample_index, sample = _find_inference_sample(inputs, RUNTIME_VISUAL_INPUT_ID)
    if sample["split"] != "test":
        raise PortfolioEvidenceError("runtime visual sample must come from the test split")
    if "/Anomaly/" not in sample["filename"]:
        raise PortfolioEvidenceError("runtime visual sample must be an anomaly case")

    localization_failures = {
        item["input_id"]
        for item in require_path(
            failure_analysis,
            "localization_failures",
            "data/visa/derived/padim/evaluation/failure_analysis/failure_analysis.json",
        )
    }
    if RUNTIME_VISUAL_INPUT_ID in localization_failures:
        raise PortfolioEvidenceError(
            "runtime visual sample is recorded as a localization failure"
        )

    prediction = _find_prediction_record(repo_root, sample["split"], RUNTIME_VISUAL_INPUT_ID)
    model_metadata = require_path(
        prediction,
        "model_metadata",
        "data/visa/derived/padim/inference/predictions/test_predictions.jsonl",
    )
    if model_metadata["sample_filename"] != sample["filename"]:
        raise PortfolioEvidenceError("runtime visual sample filename mismatch")
    if model_metadata["sample_sha256"] != sample["sample_sha256"]:
        raise PortfolioEvidenceError("runtime visual sample hash mismatch")

    image_path = repo_root / "data/visa/extracted" / sample["filename"]
    input_bytes = _read_file_with_sha256(image_path, sample["sample_sha256"])
    _require_file_manifest_entry(
        repo_root,
        relative_path=sample["filename"],
        expected_sha256=sample["sample_sha256"],
    )

    anomaly_maps_path = (
        repo_root
        / "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy"
    )
    expected_map_file_hash = require_key(
        require_path(
            inference_hashes,
            "local_output_artifacts",
            "data/visa/derived/padim/inference/artifact_hashes.json",
        ),
        "anomaly_maps/test_anomaly_maps.npy",
        "data/visa/derived/padim/inference/artifact_hashes.json",
    )
    _read_file_with_sha256(anomaly_maps_path, expected_map_file_hash)
    anomaly_map = _load_selected_anomaly_map(anomaly_maps_path, sample_index)
    if _npy_sha256(anomaly_map) != model_metadata["anomaly_map_sha256"]:
        raise PortfolioEvidenceError("runtime visual anomaly-map hash mismatch")

    localization = require_path(
        prediction,
        "predicted_localization",
        "data/visa/derived/padim/inference/predictions/test_predictions.jsonl",
    )
    if localization["localization_kind"] != "padim_raw_anomaly_map_argmax_region_v1":
        raise PortfolioEvidenceError("runtime visual localization kind mismatch")
    raw_measure = float(prediction["predicted_raw_anomaly_measure"])
    if abs(raw_measure - float(anomaly_map.max())) > 1e-12:
        raise PortfolioEvidenceError("runtime visual raw measure does not match map max")

    heatmap_bytes = _render_anomaly_map_png(anomaly_map)
    anomaly_overlay_bytes = _render_anomaly_overlay_png(
        image_path,
        anomaly_map,
        alpha=RUNTIME_VISUAL_OVERLAY_ALPHA,
        localization_region=localization["region"],
    )
    localization_bytes = _render_localization_overlay_png(
        image_path, localization["region"]
    )
    heatmap_sha256 = _sha256_bytes(heatmap_bytes)
    anomaly_overlay_sha256 = _sha256_bytes(anomaly_overlay_bytes)
    localization_sha256 = _sha256_bytes(localization_bytes)
    try:
        from PIL import Image
    except ImportError as exc:
        raise PortfolioEvidenceError(
            "Pillow is required to inspect the runtime visual dimensions"
        ) from exc
    with Image.open(image_path) as governed_image:
        rendered_dimensions = {
            "width": governed_image.width,
            "height": governed_image.height,
        }
    native_dimensions = {
        "width": int(anomaly_map.shape[1]),
        "height": int(anomaly_map.shape[0]),
    }

    manifest = {
        "anomaly_map_asset": RUNTIME_VISUAL_HEATMAP_ASSET,
        "anomaly_map_asset_sha256": heatmap_sha256,
        "anomaly_map_sha256": model_metadata["anomaly_map_sha256"],
        "anomaly_map_native_dimensions": native_dimensions,
        "anomaly_overlay_alpha": RUNTIME_VISUAL_OVERLAY_ALPHA,
        "anomaly_overlay_asset": RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET,
        "anomaly_overlay_asset_sha256": anomaly_overlay_sha256,
        "category": model_metadata["class_name"],
        "colour_map_identity": RUNTIME_VISUAL_COLOUR_MAP,
        "dataset": model_metadata["dataset"],
        "dataset_acquisition_label": model_metadata["dataset_acquisition_label"],
        "input_asset": RUNTIME_VISUAL_INPUT_ASSET,
        "input_asset_sha256": sample["sample_sha256"],
        "input_id": RUNTIME_VISUAL_INPUT_ID,
        "interpolation_mode": RUNTIME_VISUAL_INTERPOLATION,
        "localization_asset": RUNTIME_VISUAL_LOCALIZATION_ASSET,
        "localization_asset_sha256": localization_sha256,
        "localization_kind": localization["localization_kind"],
        "localization_region": localization["region"],
        "model_method": model_metadata["method"],
        "prediction_id": prediction["prediction_id"],
        "raw_anomaly_measure": raw_measure,
        "raw_map_interpolation_mode": RUNTIME_VISUAL_RAW_MAP_INTERPOLATION,
        "raw_measure_kind": prediction["raw_measure_kind"],
        "raw_measure_scale": prediction["raw_measure_scale"],
        "rendered_overlay_dimensions": rendered_dimensions,
        "sample_filename": sample["filename"],
        "sample_sha256": sample["sample_sha256"],
        "schema": "kalibra_portfolio_runtime_visual_projection_v2",
        "scientific_boundary": (
            "The anomaly overlay is presentation-only and displays raw PaDiM "
            "anomaly intensity over the governed input. It is not calibrated "
            "confidence. It creates no new metric, changes no prediction or "
            "localization, does not increase scientific resolution, and expands "
            "no scientific claim. The displayed case remains illustrative evidence "
            "from a single-seed VisA-proxy evaluation."
        ),
        "selection_rationale": (
            "Governed VisA-proxy PCB anomaly with a visible defect, recorded "
            "PaDiM raw anomaly map, and a predicted localization region not "
            "listed as a C-6 localization failure; selected for public "
            "understandability, not as generalized performance proof."
        ),
        "split": sample["split"],
        "split_sha256": model_metadata["split_sha256"],
        "source_artifacts": [
            "data/visa/extracted/pcb4/Data/Images/Anomaly/049.JPG",
            "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy",
            "data/visa/derived/padim/inference/predictions/test_predictions.jsonl",
            "data/visa/derived/padim/inference/metadata/inference_inputs.json",
            "data/visa/manifests/files.sha256",
        ],
    }
    manifest_bytes = encode_json(manifest)
    manifest_sha256 = _sha256_bytes(manifest_bytes)

    bundle = {
        "anomaly_map": {
            "asset_path": RUNTIME_VISUAL_HEATMAP_ASSET,
            "asset_sha256": heatmap_sha256,
            "label": "PaDiM raw anomaly map",
            "max_raw": f"{float(anomaly_map.max()):.3f}",
            "min_raw": f"{float(anomaly_map.min()):.3f}",
            "interpolation_mode": RUNTIME_VISUAL_RAW_MAP_INTERPOLATION,
            "sha256": model_metadata["anomaly_map_sha256"],
            "sha256_short": short_hash(model_metadata["anomaly_map_sha256"], tail=6),
        },
        "anomaly_overlay": {
            "alpha": RUNTIME_VISUAL_OVERLAY_ALPHA,
            "asset_path": RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET,
            "asset_sha256": anomaly_overlay_sha256,
            "colour_map_identity": RUNTIME_VISUAL_COLOUR_MAP,
            "interpolation_mode": RUNTIME_VISUAL_INTERPOLATION,
            "label": "PaDiM anomaly overlay",
            "native_dimensions": native_dimensions,
            "rendered_dimensions": rendered_dimensions,
            "supporting_text": (
                "Raw anomaly intensity over governed input — not calibrated confidence"
            ),
        },
        "category": model_metadata["class_name"],
        "dataset_label": model_metadata["dataset_acquisition_label"],
        "input": {
            "asset_path": RUNTIME_VISUAL_INPUT_ASSET,
            "asset_sha256": sample["sample_sha256"],
            "content_hash_short": short_hash(sample["sample_sha256"], tail=6),
            "filename": sample["filename"],
            "sample_id": Path(sample["filename"]).stem,
            "sample_label": "pcb4 / anomaly / 049.JPG",
        },
        "localization": {
            "asset_path": RUNTIME_VISUAL_LOCALIZATION_ASSET,
            "asset_sha256": localization_sha256,
            "display_label": "LOCALIZATION · " + _region_display(localization["region"]),
            "kind": localization["localization_kind"],
            "region": localization["region"],
        },
        "manifest": {
            "asset_path": RUNTIME_VISUAL_MANIFEST_ASSET,
            "sha256": manifest_sha256,
            "sha256_short": short_hash(manifest_sha256, tail=6),
        },
        "prediction_id": prediction["prediction_id"],
        "raw_anomaly_measure": f"{raw_measure:.3f}",
        "raw_bar_percent": str(max(0, min(100, int(round((raw_measure / 10.0) * 100))))),
        "raw_measure_kind": prediction["raw_measure_kind"],
        "raw_measure_scale": prediction["raw_measure_scale"],
        "selection_rationale": manifest["selection_rationale"],
        "split": sample["split"],
        "split_sha256_short": short_hash(model_metadata["split_sha256"], tail=6),
        "source_license": "VisA dataset license recorded as CC BY 4.0",
    }

    return {
        "assets": {
            RUNTIME_VISUAL_INPUT_ASSET: input_bytes,
            RUNTIME_VISUAL_HEATMAP_ASSET: heatmap_bytes,
            RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET: anomaly_overlay_bytes,
            RUNTIME_VISUAL_LOCALIZATION_ASSET: localization_bytes,
            RUNTIME_VISUAL_MANIFEST_ASSET: manifest_bytes,
        },
        "bundle": bundle,
    }


def build_runtime_bundle(
    runtime_visual: Mapping[str, Any],
    integration: Mapping[str, Any],
    runtime_replay: Mapping[str, Any],
    model_sha256: str,
    session_config_hash: str,
) -> dict[str, Any]:
    toolchain = require_path(
        integration, "toolchain", "artifacts/runtime/integration_metadata.json"
    )
    feature_contract = require_path(
        runtime_replay,
        "first_run.predictions.0.model_metadata.feature_extraction_contract_id",
        "artifacts/runtime/runtime_replay.json",
    )
    model_identity = require_path(
        integration,
        "model_artifact_identity.model_reference_id",
        "artifacts/runtime/integration_metadata.json",
    )
    return {
        "carried": [
            {
                "name": "Learned PaDiM signal, end to end",
                "status": "real",
            },
            {
                "name": "Governed model artifact",
                "status": "hash-anchored",
            },
            {
                "name": "Deterministic replay",
                "status": "byte-identical",
            },
            {
                "name": "Placeholder on canonical path",
                "source_field": (
                    "placeholder_used_on_canonical_runtime_path: false"
                ),
                "status": "retired \u00b7 false",
            },
        ],
        "determinism": "single-thread \u00b7 ORT_DISABLE_ALL \u00b7 CPU EP",
        "feature_contract": _short_feature_contract(feature_contract),
        "input": {
            "category": require_path(runtime_visual, "category", "runtime visual"),
            "class_name": require_path(runtime_visual, "category", "runtime visual"),
            "content_hash_short": require_path(
                runtime_visual, "input.content_hash_short", "runtime visual"
            ),
            "dataset_label": require_path(
                runtime_visual, "dataset_label", "runtime visual"
            ),
            "fixture": "governed VisA-proxy image",
            "fixture_tag": "INPUT \u00b7 governed VisA-proxy image",
            "name": require_path(runtime_visual, "input.sample_label", "runtime visual"),
            "projection_label": "Recorded governed case",
            "sample_id": require_path(
                runtime_visual, "input.sample_id", "runtime visual"
            ),
            "split": require_path(runtime_visual, "split", "runtime visual"),
        },
        "integration_status": require_path(
            integration, "status", "artifacts/runtime/integration_metadata.json"
        ),
        "localization": {
            "display_label": require_path(
                runtime_visual, "localization.display_label", "runtime visual"
            ),
            "kind": require_path(runtime_visual, "localization.kind", "runtime visual"),
            "x": _range_text(
                require_path(runtime_visual, "localization.region.x_min", "runtime visual"),
                require_path(runtime_visual, "localization.region.x_max", "runtime visual"),
            ),
            "y": _range_text(
                require_path(runtime_visual, "localization.region.y_min", "runtime visual"),
                require_path(runtime_visual, "localization.region.y_max", "runtime visual"),
            ),
        },
        "model_identity": model_identity,
        "model_sha256_short": short_hash(model_sha256),
        "precomputed_note": (
            "Precomputed from a governed offline run on the VisA proxy dataset. "
            "Kalibra does not run inference in your browser \u2014 this single case "
            "is illustrative evidence, not proof of generalized performance."
        ),
        "raw_anomaly_measure": require_path(
            runtime_visual, "raw_anomaly_measure", "runtime visual"
        ),
        "raw_bar_percent": str(
            require_path(runtime_visual, "raw_bar_percent", "runtime visual")
        ),
        "raw_scale_max": "10+",
        "raw_statement": "Raw anomaly measure \u2014 not calibrated confidence",
        "session_config_hash_short": short_hash(session_config_hash),
        "toolchain": (
            f"onnxruntime {require_path(toolchain, 'onnxruntime', 'toolchain')} "
            f"\u00b7 numpy {require_path(toolchain, 'numpy', 'toolchain')} "
            f"\u00b7 python {require_path(toolchain, 'python', 'toolchain')}"
        ),
        "trust": {
            "absent": [
                "Calibrated confidence",
                "Outcome routing",
                "Drift",
            ],
            "state": "not_yet_demonstrated",
        },
        "verdict": require_path(
            {"result": "DEFECT"}, "result", "runtime visual"
        ),
        "visual": runtime_visual,
    }


def build_evaluation_bundle(evidence_text: str) -> dict[str, Any]:
    precision = float(_extract_backticked_value(evidence_text, "Precision"))
    return {
        "metrics": [
            {
                "name": "Image AUROC",
                "note": "Detection quality at the image level.",
                "value": _extract_metric(evidence_text, "Image AUROC"),
            },
            {
                "name": "Pixel AUROC",
                "note": "Localization quality at the pixel level.",
                "value": _extract_metric(evidence_text, "Pixel AUROC"),
            },
            {
                "name": "AUPRO",
                "note": (
                    "Per-region overlap \u2014 the harder, more honest "
                    "localization measure."
                ),
                "value": _extract_metric(evidence_text, "AUPRO"),
            },
        ],
        "qualifier": "single-seed, VisA-proxy only",
        "weakest_precision": f"{precision:.3f}",
    }


def build_equivalence_bundle(
    report: Mapping[str, Any],
    runtime_replay: Mapping[str, Any],
) -> dict[str, Any]:
    sample_count = int(
        require_path(
            report,
            "sample_counts.total",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    max_abs = float(
        require_path(
            report,
            "anomaly_map_equivalence.max_absolute_deviation",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    max_rel = float(
        require_path(
            report,
            "anomaly_map_equivalence.max_relative_deviation",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    atol = float(
        require_path(
            report,
            "anomaly_map_equivalence.absolute_tolerance",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    rtol = float(
        require_path(
            report,
            "anomaly_map_equivalence.relative_tolerance",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    localization_exact = float(
        require_path(
            report,
            "global_maxima.localization_region_absolute",
            "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        )
    )
    comparisons = require_path(
        runtime_replay,
        "comparisons",
        "artifacts/runtime/runtime_replay.json",
    )
    comparison_rows = [
        ("Artifact identity", "artifact_identity"),
        ("Predictions", "inspection_predictions"),
        ("Localization", "localization"),
        ("Raw anomaly measures", "raw_anomaly_measures"),
        ("Run hash", "run_hash"),
        ("Session config", "session_configuration"),
        ("Output digest", "session_configuration_hash"),
    ]
    return {
        "atol": _format_tolerance(atol),
        "deviation_ratio_below_tolerance": f"{int(atol / max_abs):d}\u00d7",
        "localization_exact": f"{localization_exact:.1f}",
        "max_abs_deviation": f"{max_abs:.3e}",
        "max_abs_deviation_full": str(max_abs),
        "max_abs_deviation_short": f"{max_abs:.1e}",
        "max_relative_deviation": str(max_rel),
        "replay": {
            "compact_comparison_count_label": "7/7 comparisons",
            "comparison_count_label": "7 / 7 comparisons",
            "comparisons": [
                {
                    "name": name,
                    "value": require_path(
                        comparisons,
                        key,
                        "artifacts/runtime/runtime_replay.json",
                    ),
                }
                for name, key in comparison_rows
            ],
            "short_claim": "byte-identical second run",
            "status": require_path(
                runtime_replay,
                "status",
                "artifacts/runtime/runtime_replay.json",
            ),
        },
        "rtol": _format_tolerance(rtol),
        "samples_compared": f"{sample_count:,}",
        "samples_compared_plain": str(sample_count),
    }


def build_evidence_bundle(
    model_sha256: str,
    session_config_hash: str,
    integration: Mapping[str, Any],
    equivalence: Mapping[str, Any],
) -> dict[str, Any]:
    model_short = short_hash(model_sha256)
    session_short = short_hash(session_config_hash)
    return {
        "links": [
            {
                "claim": "Governed dataset.",
                "labels": ["visa-acq-v1", "archive + split SHA-256 in repo"],
                "n": 1,
                "status": "governed",
            },
            {
                "claim": "PaDiM baseline fit.",
                "labels": ["visa-padim-baseline-fit-v1"],
                "n": 2,
                "status": "replay",
            },
            {
                "claim": "ONNX export.",
                "copy_value": model_sha256,
                "hash_short": model_short,
                "n": 3,
                "status": "governed",
            },
            {
                "claim": "Export equivalence.",
                "labels": ["export-equivalence evidence"],
                "n": 4,
                "status": "verified",
            },
            {
                "claim": "Runtime equivalence.",
                "labels": [
                    (
                        f"{equivalence['samples_compared']} samples \u00b7 "
                        f"max dev {equivalence['max_abs_deviation_short']}"
                    )
                ],
                "n": 5,
                "status": "verified",
            },
            {
                "claim": "Runtime integration.",
                "copy_value": session_config_hash,
                "hash_short": session_short,
                "n": 6,
                "status": "integrated",
            },
            {
                "claim": "Deterministic replay + placeholder retirement.",
                "labels": [
                    "runtime_replay.json \u00b7 7/7 true",
                    "placeholder_used\u2026 : false",
                ],
                "n": 7,
                "status": require_path(
                    integration,
                    "runtime_replay.status",
                    "artifacts/runtime/integration_metadata.json",
                ),
            },
        ],
        "locations": [
            {
                "label": "Scientific evaluation (C-6)",
                "path": "docs/evidence/SCIENTIFIC_EVALUATION.md",
                "path_short": "docs/evidence/\u2026EVALUATION",
            },
            {
                "label": "Runtime equivalence",
                "path": "docs/evidence/RUNTIME_EQUIVALENCE.md",
                "path_short": "docs/evidence/\u2026EQUIVALENCE",
            },
            {
                "label": "Runtime provider integration",
                "path": "docs/evidence/RUNTIME_PROVIDER_INTEGRATION.md",
                "path_short": "docs/evidence/\u2026INTEGRATION",
            },
            {
                "label": "Placeholder retirement",
                "path": "docs/evidence/PLACEHOLDER_RETIREMENT.md",
                "path_short": "docs/evidence/\u2026RETIREMENT",
            },
            {
                "label": "Runtime artifacts",
                "path": "artifacts/runtime/*.json",
                "path_short": "artifacts/runtime/*.json",
            },
        ],
        "onnx": {
            "ir_version": str(
                require_path(
                    integration,
                    "model_artifact_identity.graph_ir_version",
                    "artifacts/runtime/integration_metadata.json",
                )
            ),
            "opset": str(
                require_path(
                    integration,
                    "model_artifact_identity.graph_opset_version",
                    "artifacts/runtime/integration_metadata.json",
                )
            ),
        },
    }


def build_architecture_bundle() -> dict[str, Any]:
    return {
        "domains": [
            {
                "name": "Inspection Engine",
                "role": "What the system sees.",
                "status": "real",
                "status_label": "Real",
            },
            {
                "name": "Trust Qualification",
                "role": "How far to trust it. Not yet evidenced.",
                "status": "gap",
                "status_label": "Not yet",
            },
            {
                "name": "Human Review",
                "role": "Where uncertainty goes. Not yet demonstrated.",
                "status": "gap",
                "status_label": "Not yet",
            },
            {
                "name": "Evidence Engine",
                "role": "What can be inspected.",
                "status": "real",
                "status_label": "Real",
            },
            {
                "name": "Evaluation Engine",
                "role": "What the science says.",
                "status": "real",
                "status_label": "Real",
            },
        ],
        "flow": [
            "Inspection",
            "Trust Qualification",
            "Human Review",
            "Evidence",
            "Evaluation",
        ],
    }


def build_boundaries_bundle() -> dict[str, Any]:
    return {
        "not_yet_demonstrated": [
            "Calibrated confidence",
            "Accept / review / reject routing",
            "Abstention on low confidence",
            "Drift assessment",
            "Interactive human-review loop",
            "Multi-seed variance",
            "Multiple model families",
            "Real-time / on-device inference",
            "Production / deployment",
        ],
        "primary_absence": "Calibrated confidence \u2014 not yet demonstrated.",
        "reframe": "A clearly drawn limit is a sign of understanding, not a gap.",
        "reframe_emphasis": "a sign of understanding, not a gap.",
    }


def build_timeline_bundle() -> dict[str, Any]:
    return {
        "next": (
            "Trust qualification \u2014 calibration, routing, abstention, drift, "
            "human review. Designed, not yet evidenced."
        ),
        "next_label": "Next",
        "next_status": "Designed, not yet evidenced.",
        "phases": [
            {
                "id": "P1",
                "items": [
                    "Offline, batch, locally reproducible system boundary defined.",
                    "Five engineering domains established as architectural boundaries.",
                    "SHA-256 governance introduced across every artifact.",
                ],
                "open": False,
                "subtitle": (
                    "Governed foundation, five-domain architecture, reproducible "
                    "offline boundary."
                ),
                "title": "Engineering substrate",
            },
            {
                "id": "P2",
                "labels": ["visa-acq-v1", "visa-padim-baseline-fit-v1"],
                "open": True,
                "subtitle": (
                    "Governed VisA acquisition, PaDiM baseline, C-6 scientific "
                    "evaluation."
                ),
                "title": "Offline science",
            },
            {
                "id": "P3",
                "open": True,
                "subtitle": (
                    "ONNX export, export- & runtime-equivalence, replay, "
                    "placeholder retirement."
                ),
                "title": "Runtime integration",
            },
        ],
    }


def render_index_html(repo_root: Path, bundles: Mapping[str, Any]) -> bytes:
    index_path = repo_root / "portfolio/index.html"
    source = read_text_required(index_path)
    source = replace_data_block(source, bundles)
    source = render_copy_values(source, bundles)
    source = render_bound_fallbacks(source, bundles)
    return source.encode("utf-8")


def replace_data_block(source: str, bundles: Mapping[str, Any]) -> str:
    payload = json.dumps(bundles, indent=2, sort_keys=True, ensure_ascii=False)
    replacement = (
        f"{DATA_START}\n"
        f'<script type="application/json" id="kalibra-data">{payload}</script>\n'
        f"{DATA_END}"
    )
    if not DATA_BLOCK_RE.search(source):
        raise PortfolioEvidenceError("portfolio/index.html is missing data markers")
    return DATA_BLOCK_RE.sub(replacement, source, count=1)


def render_copy_values(source: str, bundles: Mapping[str, Any]) -> str:
    tag_re = re.compile(
        r"(<[A-Za-z][^>]*\bdata-copy-bind=\"([^\"]+)\"[^>]*>)"
    )

    def repl(match: re.Match[str]) -> str:
        tag = match.group(1)
        path = match.group(2)
        value = str(resolve_path(bundles, path))
        attr = f'data-copy="{html.escape(value, quote=True)}"'
        if re.search(r'\sdata-copy="[^"]*"', tag):
            return re.sub(r'\sdata-copy="[^"]*"', f" {attr}", tag, count=1)
        return tag[:-1] + f" {attr}>"

    return tag_re.sub(repl, source)


def render_bound_fallbacks(source: str, bundles: Mapping[str, Any]) -> str:
    element_re = re.compile(
        r"(<(?P<tag>[A-Za-z][A-Za-z0-9]*)\b(?P<attrs>[^>]*)"
        r'\bdata-bind="(?P<path>[^"]+)"(?P<attrs2>[^>]*)>)'
        r"(?P<body>.*?)"
        r"(?P<closing></(?P=tag)>)",
        re.DOTALL,
    )

    def repl(match: re.Match[str]) -> str:
        attrs = match.group("attrs") + match.group("attrs2")
        value = resolve_path(bundles, match.group("path"))
        rendered = format_bound_value(value, attrs)
        return (
            match.group(1)
            + html.escape(rendered, quote=False)
            + match.group("closing")
        )

    previous = None
    rendered = source
    while previous != rendered:
        previous = rendered
        rendered = element_re.sub(repl, rendered)
    return rendered


def format_bound_value(value: Any, attrs: str) -> str:
    data_format = _attr(attrs, "data-format")
    if data_format == "offline-mode":
        text = "OFFLINE MODE" if value is True else "OFFLINE MODE UNVERIFIED"
    elif data_format == "bool-check":
        text = "\u2713 true" if value is True else "\u2715 false"
    else:
        text = str(value)
    prefix = _attr(attrs, "data-prefix") or ""
    suffix = _attr(attrs, "data-suffix") or ""
    return Template("$prefix$value$suffix").substitute(
        prefix=html.unescape(prefix),
        value=text,
        suffix=html.unescape(suffix),
    )


def resolve_path(root: Mapping[str, Any], path: str) -> Any:
    current: Any = root
    for part in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                raise PortfolioEvidenceError(
                    f"missing governed data path: {path}"
                ) from exc
        elif isinstance(current, Mapping):
            if part not in current:
                raise PortfolioEvidenceError(
                    f"missing governed data path: {path}"
                )
            current = current[part]
        else:
            raise PortfolioEvidenceError(f"missing governed data path: {path}")
    return current


def read_json_required(path: Path) -> Any:
    if not path.exists():
        raise PortfolioEvidenceError(f"missing source file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_text_required(path: Path) -> str:
    if not path.exists():
        raise PortfolioEvidenceError(f"missing source file: {path}")
    return path.read_text(encoding="utf-8")


def require_path(root: Mapping[str, Any], path: str, source: str) -> Any:
    try:
        value = resolve_path(root, path)
    except PortfolioEvidenceError as exc:
        raise PortfolioEvidenceError(f"{source} missing required field {path}") from exc
    if value is None:
        raise PortfolioEvidenceError(f"{source} has null required field {path}")
    return value


def require_key(root: Mapping[str, Any], key: str, source: str) -> Any:
    if key not in root:
        raise PortfolioEvidenceError(f"{source} missing required field {key}")
    value = root[key]
    if value is None:
        raise PortfolioEvidenceError(f"{source} has null required field {key}")
    return value


def short_hash(value: str, *, tail: int = 4) -> str:
    if len(value) < 12:
        raise PortfolioEvidenceError(f"hash value is too short: {value}")
    return f"{value[:8]}\u2026{value[-tail:]}"


def _short_feature_contract(model_reference: str) -> str:
    contract = "kalibra-padim-rgb64-bilinear-float64-patch8-v1"
    if contract not in model_reference:
        return "\u2026rgb64-bilinear-float64-patch8-v1"
    return "\u2026rgb64-bilinear-float64-patch8-v1"


def _localization_display(localization: Mapping[str, Any]) -> str:
    return (
        f"x {float(localization['xMin']):.2f}\u2013"
        f"{float(localization['xMax']):.2f}, "
        f"y {float(localization['yMin']):.2f}\u2013"
        f"{float(localization['yMax']):.2f}"
    )


def _find_inference_sample(
    inputs: Mapping[str, Any],
    input_id: str,
) -> tuple[int, Mapping[str, Any]]:
    samples = require_path(
        inputs,
        "samples",
        "data/visa/derived/padim/inference/metadata/inference_inputs.json",
    )
    for index, sample in enumerate(samples):
        if sample.get("input_id") == input_id:
            return index, sample
    raise PortfolioEvidenceError(f"missing runtime visual sample: {input_id}")


def _find_prediction_record(repo_root: Path, split: str, input_id: str) -> dict[str, Any]:
    path = (
        repo_root
        / f"data/visa/derived/padim/inference/predictions/{split}_predictions.jsonl"
    )
    if not path.exists():
        raise PortfolioEvidenceError(f"missing source file: {path}")
    with path.open(encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            if record.get("input_id") == input_id:
                return record
    raise PortfolioEvidenceError(f"missing runtime visual prediction: {input_id}")


def _read_file_with_sha256(path: Path, expected_sha256: str) -> bytes:
    if not path.exists():
        raise PortfolioEvidenceError(f"missing source file: {path}")
    content = path.read_bytes()
    actual = _sha256_bytes(content)
    if actual != expected_sha256:
        raise PortfolioEvidenceError(
            f"hash mismatch for {path}: expected {expected_sha256}, got {actual}"
        )
    return content


def _require_file_manifest_entry(
    repo_root: Path,
    *,
    relative_path: str,
    expected_sha256: str,
) -> None:
    manifest_path = repo_root / "data/visa/manifests/files.sha256"
    if not manifest_path.exists():
        raise PortfolioEvidenceError(f"missing source file: {manifest_path}")
    expected_line = f"{expected_sha256}  {relative_path}"
    if expected_line not in manifest_path.read_text(encoding="utf-8").splitlines():
        raise PortfolioEvidenceError(
            f"files.sha256 is missing governed sample entry: {relative_path}"
        )


def _load_selected_anomaly_map(path: Path, sample_index: int):
    try:
        import numpy as np
    except ImportError as exc:
        raise PortfolioEvidenceError("numpy is required to render the runtime visual") from exc
    maps = np.load(path, allow_pickle=False)
    if sample_index >= len(maps):
        raise PortfolioEvidenceError("runtime visual sample index exceeds map array")
    anomaly_map = maps[sample_index]
    if anomaly_map.shape != (64, 64):
        raise PortfolioEvidenceError(
            f"unexpected anomaly-map shape for runtime visual: {anomaly_map.shape}"
        )
    return anomaly_map


def _npy_sha256(array: Any) -> str:
    try:
        import numpy as np
    except ImportError as exc:
        raise PortfolioEvidenceError("numpy is required to verify the runtime visual") from exc
    buffer = io.BytesIO()
    np.save(buffer, array, allow_pickle=False)
    return _sha256_bytes(buffer.getvalue())


def _render_anomaly_map_png(anomaly_map: Any) -> bytes:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        raise PortfolioEvidenceError(
            "numpy and Pillow are required to render the runtime visual"
        ) from exc

    rgb = _colourize_anomaly_map(anomaly_map)
    image = Image.fromarray(rgb).resize((768, 768), Image.Resampling.NEAREST)
    return _png_bytes(image)


def _colourize_anomaly_map(anomaly_map: Any):
    try:
        import numpy as np
    except ImportError as exc:
        raise PortfolioEvidenceError(
            "numpy is required to colour-map the runtime visual"
        ) from exc

    values = np.asarray(anomaly_map, dtype=np.float64)
    low = float(values.min())
    high = float(values.max())
    if high <= low:
        normalized = np.zeros_like(values, dtype=np.float64)
    else:
        normalized = np.clip((values - low) / (high - low), 0.0, 1.0)

    palette = np.asarray(RUNTIME_VISUAL_PALETTE, dtype=np.float64)
    scaled = normalized * (len(palette) - 1)
    left = np.floor(scaled).astype(int)
    right = np.clip(left + 1, 0, len(palette) - 1)
    mix = (scaled - left)[..., None]
    return (palette[left] * (1.0 - mix) + palette[right] * mix).round().astype(
        "uint8"
    )


def _render_anomaly_overlay_png(
    image_path: Path,
    anomaly_map: Any,
    *,
    alpha: float,
    localization_region: Mapping[str, Any],
) -> bytes:
    try:
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
    except ImportError as exc:
        raise PortfolioEvidenceError(
            "Pillow is required to render the runtime anomaly overlay"
        ) from exc
    if not 0.0 <= alpha <= 1.0:
        raise PortfolioEvidenceError("runtime anomaly overlay alpha must be in [0, 1]")

    governed_input = Image.open(image_path).convert("RGB")
    colour_layer = Image.fromarray(_colourize_anomaly_map(anomaly_map)).resize(
        governed_input.size,
        Image.Resampling.BILINEAR,
    )
    overlay = Image.blend(governed_input, colour_layer, alpha)
    metadata = PngInfo()
    metadata.add_text(
        "kalibra.recorded_localization_region",
        json.dumps(localization_region, sort_keys=True, separators=(",", ":")),
    )
    metadata.add_text(
        "kalibra.scientific_boundary",
        "presentation-only; raw anomaly intensity; not calibrated confidence",
    )
    return _png_bytes(overlay, pnginfo=metadata)


def _render_localization_overlay_png(
    image_path: Path,
    region: Mapping[str, Any],
) -> bytes:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise PortfolioEvidenceError("Pillow is required to render the runtime visual") from exc

    image = Image.open(image_path).convert("RGB")
    image.thumbnail((900, 900), Image.Resampling.LANCZOS)
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    x_min = float(region["x_min"]) * image.width
    x_max = float(region["x_max"]) * image.width
    y_min = float(region["y_min"]) * image.height
    y_max = float(region["y_max"]) * image.height
    draw.rectangle(
        [x_min, y_min, x_max, y_max],
        fill=(229, 81, 78, 58),
        outline=(229, 81, 78, 255),
        width=max(3, round(image.width / 180)),
    )
    return _png_bytes(overlay)


def _png_bytes(image: Any, *, pnginfo: Any | None = None) -> bytes:
    buffer = io.BytesIO()
    image.save(
        buffer,
        format="PNG",
        optimize=False,
        compress_level=9,
        pnginfo=pnginfo,
    )
    return buffer.getvalue()


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _region_display(region: Mapping[str, Any]) -> str:
    return (
        f"x {float(region['x_min']):.3f}\u2013{float(region['x_max']):.3f}, "
        f"y {float(region['y_min']):.3f}\u2013{float(region['y_max']):.3f}"
    )


def _range_text(start: Any, end: Any) -> str:
    return f"{float(start):.3f}\u2013{float(end):.3f}"


def _extract_metric(source: str, name: str) -> str:
    match = re.search(rf"- {re.escape(name)} .*: `([^`]+)`", source)
    if not match:
        raise PortfolioEvidenceError(f"scientific evidence missing metric: {name}")
    return match.group(1)


def _extract_backticked_value(source: str, label: str) -> str:
    match = re.search(rf"- {re.escape(label)}: `([^`]+)`", source)
    if not match:
        raise PortfolioEvidenceError(f"scientific evidence missing value: {label}")
    return match.group(1)


def _format_tolerance(value: float) -> str:
    if value == 1e-12:
        return "1e-12"
    return f"{value:.0e}"


def _attr(attrs: str, name: str) -> str | None:
    match = re.search(rf'{re.escape(name)}="([^"]*)"', attrs)
    if not match:
        return None
    return match.group(1)


def _require_source_tokens(source: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        if token not in source:
            raise PortfolioEvidenceError(f"{label} missing expected text: {token}")


def _diff_summary(relative_path: str, actual: bytes, expected: bytes) -> str:
    actual_text = actual.decode("utf-8", errors="replace").splitlines()
    expected_text = expected.decode("utf-8", errors="replace").splitlines()
    diff = list(
        difflib.unified_diff(
            actual_text,
            expected_text,
            fromfile=f"{relative_path} (committed)",
            tofile=f"{relative_path} (generated)",
            lineterm="",
            n=1,
        )
    )
    preview = " | ".join(diff[:8])
    return f"{relative_path} differs{': ' + preview if preview else ''}"


if __name__ == "__main__":
    raise SystemExit(main())
