#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_portfolio_evidence_bundle as portfolio_builder


REPO_ROOT = SCRIPT_DIR.parent
PUBLIC_MANIFEST_PATH = Path("artifacts/public_clone_manifest.json")
EXPECTED_MODEL_SHA256 = (
    "0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a"
)
HASH_RECORDS = (
    (
        Path("artifacts/padim/artifact_hashes.json"),
        "governed_export_artifacts",
        Path("artifacts/padim"),
    ),
    (
        Path("artifacts/padim/equivalence/equivalence_hashes.json"),
        "governed_equivalence_artifacts",
        Path("artifacts/padim/equivalence"),
    ),
    (
        Path("artifacts/runtime/runtime_hashes.json"),
        "governed_runtime_artifacts",
        Path("artifacts/runtime"),
    ),
    (
        Path("artifacts/runtime/equivalence/runtime_equivalence_hashes.json"),
        "governed_runtime_equivalence_artifacts",
        Path("artifacts/runtime/equivalence"),
    ),
    (
        Path(
            "artifacts/runtime/placeholder_retirement/"
            "placeholder_retirement_hashes.json"
        ),
        "governed_retirement_artifacts",
        Path("artifacts/runtime/placeholder_retirement"),
    ),
)


class PublicCloneVerificationError(RuntimeError):
    """Raised when committed public evidence fails an integrity check."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json_object(path: Path) -> Mapping[str, object]:
    if not path.is_file():
        raise PublicCloneVerificationError(f"missing committed file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicCloneVerificationError(f"invalid JSON file: {path}") from exc
    if not isinstance(value, dict):
        raise PublicCloneVerificationError(f"JSON root is not an object: {path}")
    return value


def verify_expected_hash(path: Path, expected: str) -> None:
    if not path.is_file():
        raise PublicCloneVerificationError(f"missing committed file: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise PublicCloneVerificationError(
            f"committed artifact drift: {path}; expected {expected}, got {actual}"
        )


def verify_hash_record(
    repo_root: Path,
    record_path: Path,
    artifact_key: str,
    artifact_dir: Path,
) -> None:
    record = read_json_object(repo_root / record_path)
    if record.get("hash_algorithm") != "sha256":
        raise PublicCloneVerificationError(
            f"unsupported hash algorithm in {record_path}"
        )
    artifacts = record.get(artifact_key)
    if not isinstance(artifacts, dict) or not artifacts:
        raise PublicCloneVerificationError(
            f"missing artifact hash map {artifact_key} in {record_path}"
        )
    for filename, expected in sorted(artifacts.items()):
        if not isinstance(filename, str) or not isinstance(expected, str):
            raise PublicCloneVerificationError(
                f"invalid artifact hash entry in {record_path}"
            )
        verify_expected_hash(repo_root / artifact_dir / filename, expected)


def verify_public_manifest(repo_root: Path) -> None:
    manifest_path = repo_root / PUBLIC_MANIFEST_PATH
    manifest = read_json_object(manifest_path)
    if manifest.get("schema") != "kalibra_public_clone_manifest_v1":
        raise PublicCloneVerificationError(
            f"unexpected public clone manifest schema: {manifest_path}"
        )
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise PublicCloneVerificationError(
            f"public clone manifest has no file hashes: {manifest_path}"
        )
    for relative_path, expected in sorted(files.items()):
        if not isinstance(relative_path, str) or not isinstance(expected, str):
            raise PublicCloneVerificationError(
                f"invalid public clone manifest entry: {relative_path!r}"
            )
        verify_expected_hash(repo_root / relative_path, expected)


def verify_public_clone(repo_root: Path) -> None:
    repo_root = repo_root.expanduser().resolve()
    verify_expected_hash(
        repo_root / "artifacts/padim/model.onnx",
        EXPECTED_MODEL_SHA256,
    )
    for record_path, artifact_key, artifact_dir in HASH_RECORDS:
        verify_hash_record(repo_root, record_path, artifact_key, artifact_dir)
    verify_public_manifest(repo_root)
    review_head = portfolio_builder.committed_portfolio_review_head(repo_root)
    drift = portfolio_builder.check_portfolio(repo_root, review_head=review_head)
    if drift:
        raise PublicCloneVerificationError(
            "portfolio evidence bundle drift: " + "; ".join(drift)
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Level 1 clean-clone integrity checks over committed public artifacts."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    try:
        verify_public_clone(args.repo_root)
    except (PublicCloneVerificationError, portfolio_builder.PortfolioEvidenceError) as exc:
        print(f"PUBLIC CLONE VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(
        "Level 1 clean-clone verification passed for committed public artifacts. "
        "Governed runtime replay and full scientific reproduction were not run."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
