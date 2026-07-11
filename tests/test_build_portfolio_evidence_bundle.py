from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from scripts import build_portfolio_evidence_bundle as builder


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_PRIVATE_USERNAME = "example-user"
SYNTHETIC_PRIVATE_PATH = "/home/example-user/private-project"


def test_bundles_have_required_fields_and_no_fabricated_claims():
    bundles = builder.build_bundles(REPO_ROOT, review_head="abc1234")

    assert sorted(bundles) == [
        "architecture",
        "boundaries",
        "equivalence",
        "evaluation",
        "evidence",
        "meta",
        "runtime",
        "timeline",
    ]
    assert bundles["meta"]["review_head"] == "abc1234"
    assert bundles["meta"]["review_head_explanation"] == (
        "Commit against which the displayed evidence bundle was reviewed; "
        "not the current repository HEAD."
    )
    assert bundles["meta"]["model_sha256"].startswith("0437ae28")
    assert bundles["runtime"]["trust"]["state"] == "not_yet_demonstrated"
    assert bundles["runtime"]["visual"]["input"]["filename"] == (
        "pcb4/Data/Images/Anomaly/049.JPG"
    )
    assert bundles["runtime"]["visual"]["anomaly_map"]["label"] == (
        "PaDiM raw anomaly map"
    )
    assert bundles["boundaries"]["not_yet_demonstrated"][0] == (
        "Calibrated confidence"
    )

    flat_text = json.dumps(bundles, sort_keys=True)
    assert "calibrated confidence: 0" not in flat_text.lower()
    assert "production-ready" not in flat_text.lower()
    assert "state-of-the-art" not in flat_text.lower()


def test_sampled_values_match_governed_sources():
    bundles = builder.build_bundles(REPO_ROOT, review_head="abc1234")

    artifact_hashes = _read_json(
        REPO_ROOT / "artifacts/padim/artifact_hashes.json"
    )
    integration = _read_json(
        REPO_ROOT / "artifacts/runtime/integration_metadata.json"
    )
    replay = _read_json(REPO_ROOT / "artifacts/runtime/runtime_replay.json")
    equivalence = _read_json(
        REPO_ROOT
        / "artifacts/runtime/equivalence/runtime_equivalence_report.json"
    )
    evidence_text = (
        REPO_ROOT / "docs/evidence/SCIENTIFIC_EVALUATION.md"
    ).read_text(encoding="utf-8")

    assert bundles["meta"]["model_sha256"] == (
        artifact_hashes["governed_export_artifacts"]["model.onnx"]
    )
    assert bundles["runtime"]["session_config_hash_short"] == builder.short_hash(
        integration["session_configuration_hash"]
    )
    visual = builder.build_governed_runtime_visual_projection(REPO_ROOT)
    assert bundles["runtime"]["input"]["content_hash_short"] == (
        visual["bundle"]["input"]["content_hash_short"]
    )
    assert bundles["runtime"]["raw_anomaly_measure"] == "6.276"
    assert bundles["runtime"]["localization"]["kind"] == (
        "padim_raw_anomaly_map_argmax_region_v1"
    )
    assert bundles["evaluation"]["metrics"][0]["value"] == _metric(
        evidence_text, "Image AUROC"
    )
    assert bundles["evaluation"]["metrics"][1]["value"] == _metric(
        evidence_text, "Pixel AUROC"
    )
    assert bundles["evaluation"]["metrics"][2]["value"] == _metric(
        evidence_text, "AUPRO"
    )
    assert bundles["equivalence"]["max_abs_deviation_full"] == str(
        equivalence["anomaly_map_equivalence"]["max_absolute_deviation"]
    )
    assert bundles["equivalence"]["replay"]["comparisons"][0]["value"] is (
        replay["comparisons"]["artifact_identity"]
    )
    assert all(replay["comparisons"].values())


@pytest.mark.governed_data
def test_runtime_visual_projection_uses_governed_case_and_stable_assets():
    first = builder.build_governed_runtime_visual_projection(REPO_ROOT)
    second = builder.build_governed_runtime_visual_projection(REPO_ROOT)
    bundle = first["bundle"]
    manifest = json.loads(
        first["assets"][builder.RUNTIME_VISUAL_MANIFEST_ASSET].decode("utf-8")
    )

    assert bundle == second["bundle"]
    assert first["assets"] == second["assets"]
    assert bundle["input"]["filename"] == "pcb4/Data/Images/Anomaly/049.JPG"
    assert bundle["split"] == "test"
    assert bundle["category"] == "pcb4"
    assert manifest["input_id"] == builder.RUNTIME_VISUAL_INPUT_ID
    assert manifest["input_asset_sha256"] == (
        "d7873fe67f9e5c195504e3fec7d71daeb7818791e3bf4be23b6ec2764fa91d2e"
    )
    assert manifest["input_asset_sha256"] == sha256(
        (REPO_ROOT / "data/visa/extracted/pcb4/Data/Images/Anomaly/049.JPG").read_bytes()
    ).hexdigest()
    assert manifest["anomaly_map_sha256"] == bundle["anomaly_map"]["sha256"]
    assert manifest["anomaly_overlay_asset"] == (
        builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET
    )
    assert manifest["anomaly_overlay_asset_sha256"] == sha256(
        first["assets"][builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET]
    ).hexdigest()
    assert manifest["anomaly_overlay_alpha"] == 0.33
    assert manifest["colour_map_identity"] == builder.RUNTIME_VISUAL_COLOUR_MAP
    assert manifest["interpolation_mode"] == "bilinear (presentation-only)"
    assert manifest["raw_map_interpolation_mode"] == "nearest-neighbour"
    assert bundle["anomaly_map"]["interpolation_mode"] == "nearest-neighbour"
    assert manifest["anomaly_map_native_dimensions"] == {
        "height": 64,
        "width": 64,
    }
    assert manifest["rendered_overlay_dimensions"] == {
        "height": 1104,
        "width": 1358,
    }
    assert manifest["localization_region"] == bundle["localization"]["region"]
    assert manifest["raw_measure_kind"] == "raw_anomaly_measure"
    assert "presentation-only" in manifest["scientific_boundary"]
    assert "creates no new metric" in manifest["scientific_boundary"]
    assert "changes no prediction or localization" in manifest["scientific_boundary"]
    assert "does not increase scientific resolution" in manifest[
        "scientific_boundary"
    ]
    assert "confidence" not in bundle["anomaly_map"]["label"].lower()
    assert "confidence" not in bundle["anomaly_overlay"]["label"].lower()
    assert "not calibrated confidence" in bundle["anomaly_overlay"][
        "supporting_text"
    ].lower()
    assert "generalized performance proof" in bundle["selection_rationale"]

    for relative_path in first["assets"]:
        assert not Path(relative_path).is_absolute()
        assert SYNTHETIC_PRIVATE_USERNAME not in relative_path
        assert SYNTHETIC_PRIVATE_PATH not in relative_path

    overlay_bytes = first["assets"][builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET]
    assert SYNTHETIC_PRIVATE_USERNAME.encode() not in overlay_bytes
    assert SYNTHETIC_PRIVATE_PATH.encode() not in overlay_bytes


@pytest.mark.governed_data
def test_anomaly_overlay_is_exact_blend_of_governed_input_and_recorded_map():
    from PIL import Image

    projection = builder.build_governed_runtime_visual_projection(REPO_ROOT)
    overlay = Image.open(
        io.BytesIO(
            projection["assets"][builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET]
        )
    ).convert("RGB")
    overlay_with_metadata = Image.open(
        io.BytesIO(
            projection["assets"][builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET]
        )
    )
    governed_input = Image.open(
        REPO_ROOT / "data/visa/extracted/pcb4/Data/Images/Anomaly/049.JPG"
    ).convert("RGB")
    inputs = _read_json(
        REPO_ROOT
        / "data/visa/derived/padim/inference/metadata/inference_inputs.json"
    )
    sample_index, _ = builder._find_inference_sample(
        inputs, builder.RUNTIME_VISUAL_INPUT_ID
    )
    anomaly_map = builder._load_selected_anomaly_map(
        REPO_ROOT
        / "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy",
        sample_index,
    )
    colour_layer = Image.fromarray(
        builder._colourize_anomaly_map(anomaly_map)
    ).resize(governed_input.size, Image.Resampling.BILINEAR)
    expected = Image.blend(
        governed_input,
        colour_layer,
        builder.RUNTIME_VISUAL_OVERLAY_ALPHA,
    )

    assert overlay.size == governed_input.size
    assert overlay.tobytes() == expected.tobytes()
    assert overlay_with_metadata.info["kalibra.recorded_localization_region"] == (
        '{"x_max":0.375,"x_min":0.25,"y_max":0.5,"y_min":0.375}'
    )
    assert "not calibrated confidence" in overlay_with_metadata.info[
        "kalibra.scientific_boundary"
    ]


@pytest.mark.governed_data
def test_raw_anomaly_map_remains_nearest_neighbour_and_byte_stable():
    from PIL import Image

    projection = builder.build_governed_runtime_visual_projection(REPO_ROOT)
    inputs = _read_json(
        REPO_ROOT
        / "data/visa/derived/padim/inference/metadata/inference_inputs.json"
    )
    sample_index, _ = builder._find_inference_sample(
        inputs, builder.RUNTIME_VISUAL_INPUT_ID
    )
    anomaly_map = builder._load_selected_anomaly_map(
        REPO_ROOT
        / "data/visa/derived/padim/inference/anomaly_maps/test_anomaly_maps.npy",
        sample_index,
    )
    expected = Image.fromarray(builder._colourize_anomaly_map(anomaly_map)).resize(
        (768, 768), Image.Resampling.NEAREST
    )
    rendered = Image.open(
        io.BytesIO(projection["assets"][builder.RUNTIME_VISUAL_HEATMAP_ASSET])
    ).convert("RGB")

    assert rendered.tobytes() == expected.tobytes()
    assert sha256(
        projection["assets"][builder.RUNTIME_VISUAL_HEATMAP_ASSET]
    ).hexdigest() == "4a9716ebedc873324cd41bdd82dcb6b7df085434fd9177ec42147c35a158aaba"


def test_overlay_refinement_does_not_change_governed_result_or_metrics():
    bundles = builder.build_bundles(REPO_ROOT, review_head="abc1234")
    visual = bundles["runtime"]["visual"]

    assert visual["prediction_id"] == (
        "padim-inspection-prediction-542d2df3c9baee3daf0d9c99"
    )
    assert bundles["runtime"]["raw_anomaly_measure"] == "6.276"
    assert visual["localization"]["region"] == {
        "x_max": 0.375,
        "x_min": 0.25,
        "y_max": 0.5,
        "y_min": 0.375,
    }
    assert [metric["value"] for metric in bundles["evaluation"]["metrics"]] == [
        "0.757826",
        "0.865196",
        "0.555765",
    ]


def test_runtime_visual_render_outputs_include_public_safe_assets():
    outputs = builder.render_outputs(REPO_ROOT, review_head="abc1234")

    for prefix in ("portfolio", "assets/portfolio-experience"):
        for relative_asset in (
            builder.RUNTIME_VISUAL_INPUT_ASSET,
            builder.RUNTIME_VISUAL_HEATMAP_ASSET,
            builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET,
            builder.RUNTIME_VISUAL_LOCALIZATION_ASSET,
            builder.RUNTIME_VISUAL_MANIFEST_ASSET,
        ):
            key = f"{prefix}/{relative_asset}"
            assert key in outputs
            assert outputs[key]

    html = outputs["portfolio/index.html"].decode("utf-8")
    assert "4×4 PGM fixture" not in html
    assert "4x4 PGM fixture" not in html
    assert "PaDiM raw anomaly map" in html
    assert "PaDiM anomaly overlay" in html
    assert "Raw anomaly intensity over governed input — not calibrated confidence" in html
    assert "confidence overlay" not in html.lower()
    assert "confidence heatmap" not in html.lower()
    assert SYNTHETIC_PRIVATE_USERNAME not in html
    assert SYNTHETIC_PRIVATE_PATH not in html


def test_public_sources_exclude_private_identifiers_and_paths():
    prohibited_tokens = (
        "agentis" + "studio",
        "/" + "Users/",
        "andre-" + "projects",
        "kalibra-" + "private",
    )
    public_sources = (
        REPO_ROOT / "tests/test_build_portfolio_evidence_bundle.py",
        REPO_ROOT / "scripts/build_portfolio_evidence_bundle.py",
        REPO_ROOT / "portfolio/index.html",
        REPO_ROOT / "assets/portfolio-experience/index.html",
        REPO_ROOT / "README.md",
    )

    for source in public_sources:
        text = source.read_text(encoding="utf-8")
        for token in prohibited_tokens:
            assert token not in text, f"{source.relative_to(REPO_ROOT)} contains {token!r}"


def test_synthetic_leakage_fixtures_remain_private_and_excluded():
    synthetic_manifest = {
        "source_path": SYNTHETIC_PRIVATE_PATH,
        "source_user": SYNTHETIC_PRIVATE_USERNAME,
    }
    public_html = builder.render_outputs(REPO_ROOT, review_head="abc1234")[
        "portfolio/index.html"
    ].decode("utf-8")

    assert SYNTHETIC_PRIVATE_USERNAME in json.dumps(synthetic_manifest)
    assert SYNTHETIC_PRIVATE_PATH in json.dumps(synthetic_manifest)
    assert SYNTHETIC_PRIVATE_USERNAME not in public_html
    assert SYNTHETIC_PRIVATE_PATH not in public_html


def test_portfolio_explains_evidence_review_head_semantics():
    canonical_html = (REPO_ROOT / "portfolio/index.html").read_text(encoding="utf-8")
    preserved_html = (
        REPO_ROOT / "assets/portfolio-experience/index.html"
    ).read_text(encoding="utf-8")
    explanation = (
        "Commit against which the displayed evidence bundle was reviewed; "
        "not the current repository HEAD."
    )

    for html in (canonical_html, preserved_html):
        assert "EVIDENCE REVIEW HEAD" in html
        assert explanation in html
    assert 'data-bind="meta.review_head"' in canonical_html


def test_verify_station_separates_public_and_governed_levels():
    canonical_html = (REPO_ROOT / "portfolio/index.html").read_text(encoding="utf-8")
    preserved_html = (
        REPO_ROOT / "assets/portfolio-experience/index.html"
    ).read_text(encoding="utf-8")
    required_copy = (
        "Public clean-clone verification",
        "Works from a normal public clone using tracked repository contents only.",
        "python3 -m pytest -q",
        "python3 scripts/verify_public_clone.py",
        "python3 scripts/build_portfolio_evidence_bundle.py --check",
        "Governed-data verification",
        "Requires separately acquired governed VisA data and is expected to fail closed when that data is absent.",
        "python3 scripts/verify_padim_runtime_equivalence.py verify",
        "python3 scripts/verify_placeholder_retirement.py verify",
        "python3 -m pytest -q -m governed_data",
    )

    for html in (canonical_html, preserved_html):
        for text in required_copy:
            assert text in html
        assert html.index("Public clean-clone verification") < html.index(
            "Governed-data verification"
        )


def test_portfolio_wording_does_not_claim_zero_network_requests():
    paths = (
        REPO_ROOT / "README.md",
        REPO_ROOT / "portfolio/index.html",
        REPO_ROOT / "assets/portfolio-experience/index.html",
        REPO_ROOT / "assets/portfolio-experience/README.md",
    )
    prohibited_claim = "no " + "network request"
    for path in paths:
        assert prohibited_claim not in path.read_text(encoding="utf-8").lower()


def test_public_runtime_station_no_longer_uses_synthetic_fixture():
    rendered = builder.render_outputs(REPO_ROOT, review_head="abc1234")[
        "portfolio/index.html"
    ].decode("utf-8")
    public_static = (
        REPO_ROOT / "assets/portfolio-experience/index.html"
    ).read_text(encoding="utf-8")
    for html in (rendered, public_static):
        assert "4×4 PGM fixture" not in html
        assert "4x4 PGM fixture" not in html
        assert "blob_defect.pgm" not in html
        assert "PaDiM raw anomaly map" in html
        assert "PaDiM anomaly overlay" in html
        assert "media/runtime-inspection/pcb4-049-input.jpg" in html
        assert "media/runtime-inspection/pcb4-049-anomaly-overlay.png" in html
        assert "media/runtime-inspection/pcb4-049-padim-map.png" in html
        assert "media/runtime-inspection/pcb4-049-localization.png" in html
        assert html.index("pcb4-049-anomaly-overlay.png") != html.index(
            "pcb4-049-padim-map.png"
        )
        assert "confidence overlay" not in html.lower()


def test_canonical_and_public_runtime_assets_and_layout_are_aligned():
    canonical_html = (REPO_ROOT / "portfolio/index.html").read_text(encoding="utf-8")
    public_html = (
        REPO_ROOT / "assets/portfolio-experience/index.html"
    ).read_text(encoding="utf-8")
    required_runtime_copy = (
        "Governed input",
        "PaDiM anomaly overlay",
        "Raw anomaly intensity over governed input — not calibrated confidence",
        "PaDiM raw anomaly map",
        "Recorded localization",
    )
    required_runtime_assets = (
        builder.RUNTIME_VISUAL_INPUT_ASSET,
        builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET,
        builder.RUNTIME_VISUAL_HEATMAP_ASSET,
        builder.RUNTIME_VISUAL_LOCALIZATION_ASSET,
    )
    for value in required_runtime_copy + required_runtime_assets:
        assert value in canonical_html
        assert value in public_html

    canonical_css = (REPO_ROOT / "portfolio/styles.css").read_text(encoding="utf-8")
    public_css = (
        REPO_ROOT / "assets/portfolio-experience/styles.css"
    ).read_text(encoding="utf-8")
    assert canonical_css[canonical_css.index(":root") :] == public_css[
        public_css.index(":root") :
    ]
    for relative_asset in required_runtime_assets + (builder.RUNTIME_VISUAL_MANIFEST_ASSET,):
        assert (REPO_ROOT / "portfolio" / relative_asset).read_bytes() == (
            REPO_ROOT / "assets/portfolio-experience" / relative_asset
        ).read_bytes()

    overlay_sha256 = sha256(
        (REPO_ROOT / "portfolio" / builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET).read_bytes()
    ).hexdigest()
    for prefix in ("portfolio", "assets/portfolio-experience"):
        manifest = _read_json(
            REPO_ROOT / prefix / builder.RUNTIME_VISUAL_MANIFEST_ASSET
        )
        assert manifest["anomaly_overlay_asset_sha256"] == overlay_sha256
        assert manifest["input_asset_sha256"] == (
            "d7873fe67f9e5c195504e3fec7d71daeb7818791e3bf4be23b6ec2764fa91d2e"
        )
        assert manifest["anomaly_map_sha256"] == (
            "41c9f22495beb491cd83845abbfd826a796651b593606bb6c05021d7a29d83e2"
        )


def test_missing_governed_source_field_raises(tmp_path):
    repo = _copy_minimal_repo(tmp_path)
    artifact_path = repo / "artifacts/padim/artifact_hashes.json"
    artifact_hashes = _read_json(artifact_path)
    del artifact_hashes["governed_export_artifacts"]["model.onnx"]
    artifact_path.write_text(json.dumps(artifact_hashes), encoding="utf-8")

    with pytest.raises(builder.PortfolioEvidenceError):
        builder.build_bundles(repo, review_head="abc1234")


def test_generated_data_bind_paths_resolve():
    bundles = builder.build_bundles(REPO_ROOT, review_head="abc1234")
    html = (REPO_ROOT / "portfolio/index.html").read_text(encoding="utf-8")
    bind_paths = set(re.findall(r'data-bind="([^"]+)"', html))
    copy_paths = set(re.findall(r'data-copy-bind="([^"]+)"', html))

    assert bind_paths
    assert copy_paths
    for path in sorted(bind_paths | copy_paths):
        assert builder.resolve_path(bundles, path) is not None, path


def test_generate_is_deterministic_and_check_detects_drift(tmp_path):
    repo = _copy_minimal_repo(tmp_path)

    builder.generate_portfolio(repo, review_head="abc1234")
    first_meta = (repo / "portfolio/data/meta.json").read_bytes()
    builder.generate_portfolio(repo, review_head="abc1234")
    second_meta = (repo / "portfolio/data/meta.json").read_bytes()

    assert first_meta == second_meta
    assert builder.check_portfolio(repo, review_head="abc1234") == []

    meta_path = repo / "portfolio/data/meta.json"
    meta_path.write_text(
        meta_path.read_text(encoding="utf-8").replace("abc1234", "changed"),
        encoding="utf-8",
    )
    assert builder.check_portfolio(repo, review_head="abc1234")


def test_cli_check_mode_passes_after_generate(tmp_path):
    repo = _copy_minimal_repo(tmp_path)
    script = REPO_ROOT / "scripts/build_portfolio_evidence_bundle.py"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(repo),
            "--review-head",
            "abc1234",
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(repo),
            "--review-head",
            "abc1234",
            "--check",
        ],
        check=True,
    )


def test_check_mode_uses_committed_review_head_by_default(tmp_path, monkeypatch):
    repo = _copy_minimal_repo(tmp_path)
    builder.generate_portfolio(repo, review_head="abc1234")

    def fail_if_head_is_read(repo_root: Path) -> str:
        raise AssertionError("check mode must not read current git HEAD")

    monkeypatch.setattr(builder, "current_git_head", fail_if_head_is_read)

    assert builder.main(["--repo-root", str(repo), "--check"]) == 0
    assert (
        builder.main(
            [
                "--repo-root",
                str(repo),
                "--check",
                "--review-head",
                "def5678",
            ]
        )
        == 1
    )


def test_generate_mode_preserves_committed_evidence_review_head_by_default(
    tmp_path, monkeypatch
):
    repo = _copy_minimal_repo(tmp_path)
    builder.generate_portfolio(repo, review_head="abc1234")

    def fail_if_head_is_read(repo_root: Path) -> str:
        raise AssertionError("generation must preserve the committed evidence review HEAD")

    monkeypatch.setattr(builder, "current_git_head", fail_if_head_is_read)

    assert builder.main(["--repo-root", str(repo)]) == 0
    assert _read_json(repo / "portfolio/data/meta.json")["review_head"] == "abc1234"


def _copy_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    paths = [
        "artifacts/padim/artifact_hashes.json",
        "artifacts/runtime/integration_metadata.json",
        "artifacts/runtime/runtime_replay.json",
        "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        "data/visa/derived/padim/evaluation/failure_analysis/failure_analysis.json",
        "docs/evidence/SCIENTIFIC_EVALUATION.md",
        "docs/engineering/PORTFOLIO_UX_ARCHITECTURE.md",
        "docs/engineering/RUNTIME_INTEGRATION_MILESTONE.md",
        "tests/fixtures/inspection/blob_defect.pgm",
        "portfolio/index.html",
        "portfolio/data/runtime.json",
    ]
    paths.extend(
        f"portfolio/{relative_path}"
        for relative_path in (
            builder.RUNTIME_VISUAL_INPUT_ASSET,
            builder.RUNTIME_VISUAL_HEATMAP_ASSET,
            builder.RUNTIME_VISUAL_ANOMALY_OVERLAY_ASSET,
            builder.RUNTIME_VISUAL_LOCALIZATION_ASSET,
            builder.RUNTIME_VISUAL_MANIFEST_ASSET,
        )
    )
    for path in paths:
        src = REPO_ROOT / path
        dst = repo / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (repo / "portfolio/data").mkdir(parents=True, exist_ok=True)
    (repo / "assets/portfolio-experience").mkdir(parents=True, exist_ok=True)
    return repo


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _metric(source: str, name: str) -> str:
    match = re.search(rf"- {re.escape(name)} .*: `([^`]+)`", source)
    assert match is not None
    return match.group(1)


def _link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        dst.symlink_to(src)
    except OSError:
        shutil.copy2(src, dst)
