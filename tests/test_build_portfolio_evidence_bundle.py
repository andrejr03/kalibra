from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from scripts import build_portfolio_evidence_bundle as builder


REPO_ROOT = Path(__file__).resolve().parents[1]


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
    assert bundles["meta"]["model_sha256"].startswith("0437ae28")
    assert bundles["runtime"]["trust"]["state"] == "not_yet_demonstrated"
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
    assert bundles["runtime"]["input"]["content_hash_short"] == builder.short_hash(
        builder.build_local_provider_projection(REPO_ROOT)["contentHash"],
        tail=6,
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


def _copy_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    paths = [
        "artifacts/padim/artifact_hashes.json",
        "artifacts/runtime/integration_metadata.json",
        "artifacts/runtime/runtime_replay.json",
        "artifacts/runtime/equivalence/runtime_equivalence_report.json",
        "docs/evidence/SCIENTIFIC_EVALUATION.md",
        "docs/engineering/PORTFOLIO_UX_ARCHITECTURE.md",
        "docs/engineering/RUNTIME_INTEGRATION_MILESTONE.md",
        "tests/fixtures/inspection/blob_defect.pgm",
        "portfolio/index.html",
    ]
    for path in paths:
        src = REPO_ROOT / path
        dst = repo / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    (repo / "portfolio/data").mkdir(parents=True, exist_ok=True)
    return repo


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _metric(source: str, name: str) -> str:
    match = re.search(rf"- {re.escape(name)} .*: `([^`]+)`", source)
    assert match is not None
    return match.group(1)
