from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/verify_public_clone.py"
SPEC = importlib.util.spec_from_file_location("verify_public_clone", SCRIPT_PATH)
assert SPEC is not None
public_clone = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(public_clone)


def test_default_pytest_contract_excludes_external_data_markers() -> None:
    config = (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")

    assert 'addopts = -m "not governed_data and not scientific_replay"' in config
    assert "governed_data:" in config
    assert "scientific_replay:" in config


def test_pages_uses_governed_verification_dependencies() -> None:
    requirements = (
        REPO_ROOT / "requirements-verification.txt"
    ).read_text(encoding="utf-8").splitlines()
    workflow = (REPO_ROOT / ".github/workflows/pages.yml").read_text(
        encoding="utf-8"
    )
    metadata = json.loads(
        (
            REPO_ROOT
            / "artifacts/runtime/placeholder_retirement/"
            "placeholder_retirement_metadata.json"
        ).read_text(encoding="utf-8")
    )
    verifier = (
        REPO_ROOT / "scripts/verify_placeholder_retirement.py"
    ).read_text(encoding="utf-8")

    numpy_requirements = [
        requirement
        for requirement in requirements
        if requirement.startswith("numpy")
    ]
    runtime_requirements = [
        requirement
        for requirement in requirements
        if requirement.startswith("onnxruntime")
    ]

    assert "actions/setup-python" not in workflow
    assert "python-version:" not in workflow
    assert "container: python:3.9.6-slim" in workflow
    assert numpy_requirements == ["numpy==2.0.2"]
    assert runtime_requirements == ["onnxruntime==1.19.2"]
    assert metadata["toolchain"]["python"] == "3.9.6"
    assert numpy_requirements[0].partition("==")[2] == metadata["toolchain"][
        "numpy"
    ]
    assert runtime_requirements[0].partition("==")[2] == metadata["toolchain"][
        "onnxruntime"
    ]
    assert "python -m pip install -r requirements-verification.txt" in workflow
    assert "pip install pytest numpy" not in workflow
    assert "pip install pytest numpy pillow onnx onnxruntime" not in workflow
    assert "python --version" in workflow
    assert "assert sys.version.split()[0] == '3.9.6'" in workflow
    assert "assert np.__version__ == '2.0.2'" in workflow
    assert "assert ort.__version__ == '1.19.2'" in workflow
    assert "if path.exists() and path.read_bytes() != content:" in verifier


def test_pages_deploys_only_after_public_verification() -> None:
    workflow = (REPO_ROOT / ".github/workflows/pages.yml").read_text(
        encoding="utf-8"
    )

    assert workflow.index("  verify:") < workflow.index("  deploy:")
    assert "  deploy:\n    needs: verify" in workflow
    assert "python -m pytest -q" in workflow
    assert "python scripts/verify_public_clone.py" in workflow
    assert "python scripts/build_portfolio_evidence_bundle.py --check" in workflow
    assert "verify_padim_runtime_equivalence.py" not in workflow
    assert "verify_placeholder_retirement.py" not in workflow
    assert "VisA_20220922.tar" not in workflow
    assert "contents: read" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "uses: actions/configure-pages@v5" in workflow
    assert "uses: actions/upload-pages-artifact@v3" in workflow
    assert "path: portfolio" in workflow
    assert "uses: actions/deploy-pages@v4" in workflow


def test_pages_trusts_only_the_checked_out_repository_before_tests() -> None:
    workflow = (REPO_ROOT / ".github/workflows/pages.yml").read_text(
        encoding="utf-8"
    )
    runtime_tests = (
        REPO_ROOT / "tests/test_padim_runtime_equivalence.py"
    ).read_text(encoding="utf-8")

    checkout = workflow.index("      - name: Checkout")
    trust = workflow.index("      - name: Trust checked-out repository")
    tests = workflow.index("      - name: Run clean-clone tests")

    assert checkout < trust < tests
    assert (
        'git config --global --add safe.directory "$GITHUB_WORKSPACE"'
        in workflow
    )
    assert "/__w/kalibra/kalibra" not in workflow
    assert "safe.directory '*'" not in workflow
    assert 'safe.directory "*"' not in workflow
    assert (
        "test_real_placeholder_retirement_verifier_command_passes" in runtime_tests
    )


def test_real_data_tests_remain_explicitly_marked_and_real() -> None:
    provider_tests = (REPO_ROOT / "tests/test_onnx_provider.py").read_text(
        encoding="utf-8"
    )
    runtime_tests = (
        REPO_ROOT / "tests/test_padim_runtime_equivalence.py"
    ).read_text(encoding="utf-8")
    portfolio_tests = (
        REPO_ROOT / "tests/test_build_portfolio_evidence_bundle.py"
    ).read_text(encoding="utf-8")

    assert "@pytest.mark.governed_data\ndef test_canonical_onnx_provider" in provider_tests
    assert "provider.predict(inspection_input)" in provider_tests
    assert "data\"\n    / \"visa\"\n    / \"extracted" in provider_tests
    assert "@pytest.mark.governed_data\ndef test_real_runtime_equivalence" in runtime_tests
    assert 'str(SCRIPT_PATH),\n            "verify"' in runtime_tests
    assert portfolio_tests.count("@pytest.mark.governed_data") >= 3
    assert "Image.blend" in portfolio_tests
    assert "test_anomaly_maps.npy" in portfolio_tests


def test_public_verifier_does_not_claim_governed_or_scientific_replay(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(public_clone, "verify_public_clone", lambda repo_root: None)

    assert public_clone.main([]) == 0
    output = capsys.readouterr().out

    assert "Level 1 clean-clone verification passed" in output
    assert "were not run" in output
    assert "full scientific reproduction passed" not in output.lower()
    assert "runtime equivalence passed" not in output.lower()


def test_public_manifest_detects_modified_committed_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "artifacts/example.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{"status":"passed"}\n', encoding="utf-8")
    expected = public_clone.sha256_file(artifact)
    manifest_path = repo / public_clone.PUBLIC_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema": "kalibra_public_clone_manifest_v1",
                "files": {"artifacts/example.json": expected},
            }
        ),
        encoding="utf-8",
    )

    public_clone.verify_public_manifest(repo)
    artifact.write_text('{"status":"modified"}\n', encoding="utf-8")

    with pytest.raises(
        public_clone.PublicCloneVerificationError,
        match="committed artifact drift",
    ):
        public_clone.verify_public_manifest(repo)


def test_documented_verification_commands_exist_and_are_executable() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    commands = (
        "python3 -m pytest -q",
        "python3 scripts/verify_public_clone.py",
        "python3 scripts/build_portfolio_evidence_bundle.py --check",
        "python3 scripts/verify_padim_runtime_equivalence.py verify",
        "python3 -m pytest -q -m governed_data",
    )
    for command in commands:
        assert command in readme

    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert "Level 1 clean-clone integrity checks" in completed.stdout
