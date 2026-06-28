from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "scripts" / "run_end_to_end_substrate.py"

REQUIRED_KEYS = {
    "input_id",
    "inspection_result_id",
    "trust_qualification_result_id",
    "qualified_outcome",
    "human_review_occurred",
    "review_case_id",
    "evidence_view_id",
    "evaluation_report_id",
    "preserved_record_count",
    "absence_disclosure_count",
    "claims",
}

FORBIDDEN_OUTPUT_FIELDS = {
    "accuracy",
    "benchmark_result",
    "quality_score",
    "score",
    "aggregate_score",
    "overall_score",
    "pass_rate",
    "production_readiness_claim",
    "model_performance_claim",
}


def run_cli() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI_PATH)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def parse_cli_json() -> dict[str, Any]:
    completed = run_cli()
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    return json.loads(completed.stdout)


def test_cli_command_runs_successfully():
    completed = run_cli()

    assert completed.returncode == 0
    assert completed.stdout.strip().startswith("{")
    assert completed.stderr == ""


def test_cli_output_is_valid_json_with_required_identifiers():
    payload = parse_cli_json()

    assert REQUIRED_KEYS.issubset(payload)
    assert payload["input_id"] == "integration-input-000"
    assert payload["inspection_result_id"]
    assert payload["trust_qualification_result_id"]
    assert payload["qualified_outcome"] == "review"
    assert payload["human_review_occurred"] is True
    assert payload["review_case_id"]
    assert payload["evidence_view_id"]
    assert payload["evaluation_report_id"]
    assert payload["preserved_record_count"] == 3
    assert isinstance(payload["absence_disclosure_count"], int)


def test_cli_output_includes_explicit_non_claim_flags():
    payload = parse_cli_json()

    assert payload["claims"] == {
        "ml_implemented": False,
        "cv_implemented": False,
        "production_ready": False,
        "performance_claim": False,
    }


def test_cli_output_contains_no_forbidden_score_or_performance_fields():
    payload = parse_cli_json()

    assert not (set(_walk_keys(payload)) & FORBIDDEN_OUTPUT_FIELDS)


def test_cli_does_not_modify_assets_prototype_readme_or_asset_pipeline():
    before = _protected_file_hashes()

    completed = run_cli()

    assert completed.returncode == 0
    assert _protected_file_hashes() == before


def _protected_file_hashes() -> dict[str, str]:
    protected_files = []
    protected_files.extend(
        path for path in (REPO_ROOT / "assets").rglob("*") if path.is_file()
    )
    protected_files.extend(
        (
            REPO_ROOT / "README.md",
            REPO_ROOT / "tools" / "generate_kalibra_part_assets.py",
        )
    )
    return {
        str(path.relative_to(REPO_ROOT)): _sha256_file(path)
        for path in sorted(protected_files)
    }


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)
