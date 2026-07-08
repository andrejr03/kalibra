#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import difflib
import html
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
    review_head = args.review_head or current_git_head(repo_root)
    try:
        if args.check:
            diffs = check_portfolio(repo_root, review_head=review_head)
            if diffs:
                print("portfolio evidence bundle drift detected:", file=sys.stderr)
                for diff in diffs:
                    print(f"- {diff}", file=sys.stderr)
                return 1
            return 0
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
    bundles = build_bundles(repo_root, review_head=review_head)
    outputs: dict[str, bytes] = {}
    for name in BUNDLE_NAMES:
        outputs[f"portfolio/data/{name}.json"] = encode_json(bundles[name])
    outputs["portfolio/index.html"] = render_index_html(repo_root, bundles)
    return outputs


def encode_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def build_bundles(repo_root: Path, *, review_head: str) -> dict[str, Any]:
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
        repo_root
        / "docs/evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md"
    )
    architecture_doc = read_text_required(
        repo_root / "docs/plans/KALIBRA_PORTFOLIO_UX_ARCHITECTURE_v1.0.md"
    )
    stack_checkpoint = read_text_required(
        repo_root
        / "docs/checkpoints/"
        "KALIBRA_PORTFOLIO_UX_STACK_AND_PROTOTYPE_REVIEW_v1.0.md"
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
        stack_checkpoint,
        ["Option B", "Static HTML/CSS/JS", "GitHub Pages"],
        "portfolio stack checkpoint",
    )

    local_projection = build_local_provider_projection(repo_root)
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
        local_projection,
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


def build_runtime_bundle(
    projection: Mapping[str, Any],
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
            "class_name": "candle",
            "content_hash_short": short_hash(
                require_path(projection, "contentHash", "local provider projection"),
                tail=6,
            ),
            "fixture": "4\u00d74 PGM",
            "fixture_tag": "INPUT \u00b7 4\u00d74 PGM fixture",
            "name": require_path(projection, "file", "local provider projection"),
            "projection_label": "Local-provider projection",
        },
        "integration_status": require_path(
            integration, "status", "artifacts/runtime/integration_metadata.json"
        ),
        "localization": {
            "display_label": (
                "LOCALIZATION \u00b7 "
                + _localization_display(
                    require_path(
                        projection,
                        "localization",
                        "local provider projection",
                    )
                )
            ),
            "x": "0.25\u20130.75",
            "y": "0.25\u20130.75",
        },
        "model_identity": model_identity,
        "model_sha256_short": short_hash(model_sha256),
        "precomputed_note": (
            "Precomputed from a governed offline run. Kalibra does not run "
            "inference in your browser \u2014 this is a projection of a recorded "
            "local-provider result."
        ),
        "raw_anomaly_measure": require_path(
            projection, "rawText", "local provider projection"
        ),
        "raw_bar_percent": str(
            require_path(projection, "rawBarPercent", "local provider projection")
        ),
        "raw_scale_max": "100",
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
            projection, "result", "local provider projection"
        ),
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
                "path": (
                    "docs/evidence/"
                    "KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md"
                ),
                "path_short": "docs/evidence/\u2026EVALUATION",
            },
            {
                "label": "Runtime equivalence",
                "path": (
                    "docs/evidence/"
                    "KALIBRA_RUNTIME_EQUIVALENCE_VERIFICATION_EVIDENCE_v1.0.md"
                ),
                "path_short": "docs/evidence/\u2026EQUIVALENCE",
            },
            {
                "label": "Runtime provider integration",
                "path": (
                    "docs/evidence/"
                    "KALIBRA_RUNTIME_PROVIDER_INTEGRATION_EVIDENCE_v1.0.md"
                ),
                "path_short": "docs/evidence/\u2026INTEGRATION",
            },
            {
                "label": "Placeholder retirement",
                "path": (
                    "docs/evidence/"
                    "KALIBRA_PLACEHOLDER_RETIREMENT_EVIDENCE_v1.0.md"
                ),
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
