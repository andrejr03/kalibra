#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "visa"
SOURCE_DIR = DATA_ROOT / "source"
EXTRACTED_DIR = DATA_ROOT / "extracted"
MANIFESTS_DIR = DATA_ROOT / "manifests"
SPLITS_DIR = MANIFESTS_DIR / "splits"
PROVENANCE_DIR = DATA_ROOT / "provenance"
DERIVED_DIR = DATA_ROOT / "derived"
EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "evidence" / "VISA_ACQUISITION.md"
)

ARCHIVE_FILENAME = "VisA_20220922.tar"
ARCHIVE_STEM = "VisA_20220922"
ARCHIVE_URL = (
    "https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar"
)
ARCHIVE_AWS_ARN = "arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar"
UPSTREAM_REPO_URL = "https://github.com/amazon-science/spot-diff.git"
UPSTREAM_REPO_DISPLAY_URL = "https://github.com/amazon-science/spot-diff"
UPSTREAM_COMMIT = "2a692ab575001cbde74d402d897a7286086c6199"
OPEN_DATA_REGISTRY_URL = "https://registry.opendata.aws/visa/"
DOI = "10.1007/978-3-031-20056-4_23"
ARXIV = "2207.14315"
EXPECTED_ARCHIVE_METADATA = {
    "content_length": 1929840640,
    "last_modified": "Thu, 22 Sep 2022 19:23:39 GMT",
    "content_type": "application/x-tar",
    "etag": '"05c830591a1172938cb714895c9e0cfb-113"',
}
UPSTREAM_SPLIT_CSVS = {
    "1cls": Path("split_csv") / "1cls.csv",
    "2cls_fewshot": Path("split_csv") / "2cls_fewshot.csv",
    "2cls_highshot": Path("split_csv") / "2cls_highshot.csv",
}
SPLIT_MANIFEST_NAMES = ("train", "validation", "test")
REQUIRED_PROVENANCE_TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "dataset",
        "acquisition",
        "upstream_identifiers",
        "licenses",
        "attribution",
        "archive",
        "archive_metadata",
        "manifest_hashes",
        "local_governed_identity",
        "source_disagreement_note",
        "scope_boundaries",
    }
)


class AcquisitionError(RuntimeError):
    """Raised when governed acquisition cannot proceed safely."""


@dataclass(frozen=True)
class ArchiveRecord:
    sha256: str
    size_bytes: int
    metadata: dict[str, object]


@dataclass(frozen=True)
class SplitRow:
    object_class: str
    source_split: str
    label: str
    image: str
    mask: str
    source_csv: str


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def ensure_layout() -> None:
    for directory in (
        SOURCE_DIR,
        EXTRACTED_DIR,
        MANIFESTS_DIR,
        SPLITS_DIR,
        PROVENANCE_DIR,
        DERIVED_DIR,
        EVIDENCE_PATH.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def run_git(args: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def ensure_upstream_checkout(upstream_repo: Path) -> None:
    if not upstream_repo.exists():
        upstream_repo.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                UPSTREAM_REPO_URL,
                str(upstream_repo),
            ],
            cwd=REPO_ROOT,
            check=True,
        )

    if not (upstream_repo / ".git").exists():
        raise AcquisitionError(f"upstream checkout is not a git repository: {upstream_repo}")

    origin = run_git(["config", "--get", "remote.origin.url"], upstream_repo)
    allowed_origins = {
        UPSTREAM_REPO_URL,
        UPSTREAM_REPO_DISPLAY_URL,
        "git@github.com:amazon-science/spot-diff.git",
    }
    if origin not in allowed_origins:
        raise AcquisitionError(
            f"upstream checkout origin is not the canonical repository: {origin}"
        )

    run_git(["fetch", "--quiet", "origin", UPSTREAM_COMMIT], upstream_repo)
    run_git(["checkout", "--quiet", UPSTREAM_COMMIT], upstream_repo)
    commit = run_git(["rev-parse", "HEAD"], upstream_repo)
    if commit != UPSTREAM_COMMIT:
        raise AcquisitionError(f"upstream checkout is not pinned: {commit}")


def fetch_archive_metadata() -> dict[str, object]:
    request = urllib.request.Request(ARCHIVE_URL, method="HEAD")
    with urllib.request.urlopen(request, timeout=60) as response:
        headers = response.headers
    metadata = {
        "url": ARCHIVE_URL,
        "content_length": int(headers["Content-Length"]),
        "last_modified": headers["Last-Modified"],
        "content_type": headers["Content-Type"],
        "etag": headers["ETag"],
        "accept_ranges": headers.get("Accept-Ranges"),
        "storage_class": headers.get("x-amz-storage-class"),
    }
    for field, expected in EXPECTED_ARCHIVE_METADATA.items():
        if metadata[field] != expected:
            raise AcquisitionError(
                f"canonical archive metadata mismatch for {field}: "
                f"expected {expected!r}, got {metadata[field]!r}"
            )
    return metadata


def download_archive(archive_path: Path) -> None:
    if archive_path.exists():
        return

    temp_path = archive_path.with_suffix(archive_path.suffix + ".part")
    if temp_path.exists():
        temp_path.unlink()

    request = urllib.request.Request(ARCHIVE_URL)
    with urllib.request.urlopen(request, timeout=60) as response:
        with temp_path.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)

    actual_size = temp_path.stat().st_size
    expected_size = EXPECTED_ARCHIVE_METADATA["content_length"]
    if actual_size != expected_size:
        temp_path.unlink(missing_ok=True)
        raise AcquisitionError(
            f"downloaded archive size mismatch: expected {expected_size}, got {actual_size}"
        )
    temp_path.rename(archive_path)


def record_archive(archive_path: Path, metadata: Mapping[str, object]) -> ArchiveRecord:
    if not archive_path.exists():
        raise AcquisitionError(f"source archive missing: {archive_path}")
    actual_size = archive_path.stat().st_size
    expected_size = EXPECTED_ARCHIVE_METADATA["content_length"]
    if actual_size != expected_size:
        raise AcquisitionError(
            f"source archive size mismatch: expected {expected_size}, got {actual_size}"
        )

    archive_hash = sha256_file(archive_path)
    relative_archive = os.path.relpath(archive_path, MANIFESTS_DIR)
    archive_record = f"{archive_hash}  {relative_archive}\n"
    write_governed_record(MANIFESTS_DIR / "archive.sha256", archive_record.encode())
    archive_metadata_path = MANIFESTS_DIR / "archive_metadata.json"
    write_json_record(archive_metadata_path, dict(metadata))
    write_record_hash(archive_metadata_path)
    archive_path.chmod(0o444)
    return ArchiveRecord(
        sha256=archive_hash,
        size_bytes=actual_size,
        metadata=dict(metadata),
    )


def write_governed_record(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != content:
            raise AcquisitionError(f"governed record already exists with different bytes: {path}")
        return
    path.write_bytes(content)


def write_json_record(path: Path, value: Mapping[str, object]) -> None:
    write_governed_record(path, canonical_json_bytes(value))


def write_record_hash(path: Path) -> str:
    digest = sha256_file(path)
    hash_path = path.with_name(path.name + ".sha256")
    content = f"{digest}  {path.name}\n".encode("utf-8")
    write_governed_record(hash_path, content)
    return digest


def safe_extract_tar(archive_path: Path, destination: Path) -> None:
    if any(destination.iterdir()):
        return

    destination_resolved = destination.resolve()
    with tarfile.open(archive_path, "r") as archive:
        members = archive.getmembers()
        for member in members:
            target = (destination / member.name).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise AcquisitionError(f"unsafe archive member path: {member.name}")
        archive.extractall(destination, members=members)


def make_tree_read_only(root: Path) -> None:
    for path in iter_files(root):
        path.chmod(0o444)
    directories = sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        directory.chmod(0o555)


def iter_files(root: Path) -> Iterable[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def build_files_manifest() -> dict[str, str]:
    files = list(iter_files(EXTRACTED_DIR))
    if not files:
        raise AcquisitionError("extracted dataset contains no files")
    manifest_lines: list[str] = []
    hashes: dict[str, str] = {}
    for path in files:
        relative = path.relative_to(EXTRACTED_DIR).as_posix()
        digest = sha256_file(path)
        hashes[relative] = digest
        manifest_lines.append(f"{digest}  {relative}\n")
    write_governed_record(
        MANIFESTS_DIR / "files.sha256",
        "".join(manifest_lines).encode("utf-8"),
    )
    write_record_hash(MANIFESTS_DIR / "files.sha256")
    return hashes


def dataset_root() -> Path:
    candidates = [EXTRACTED_DIR / "VisA", EXTRACTED_DIR]
    required = Path("candle") / "Data" / "Images" / "Normal"
    for candidate in candidates:
        if (candidate / required).is_dir():
            return candidate
    raise AcquisitionError("could not locate extracted VisA dataset root")


def read_upstream_split_csvs(upstream_repo: Path) -> dict[str, list[SplitRow]]:
    split_rows: dict[str, list[SplitRow]] = {}
    for name, relative_path in UPSTREAM_SPLIT_CSVS.items():
        path = upstream_repo / relative_path
        if not path.exists():
            raise AcquisitionError(f"missing upstream split CSV: {path}")
        copied_path = SPLITS_DIR / f"upstream_{name}.csv"
        write_governed_record(copied_path, path.read_bytes())
        write_record_hash(copied_path)

        with path.open(newline="") as file:
            reader = csv.DictReader(file)
            expected_fields = ["object", "split", "label", "image", "mask"]
            if reader.fieldnames != expected_fields:
                raise AcquisitionError(
                    f"unexpected upstream CSV header in {path}: {reader.fieldnames}"
                )
            rows = [
                SplitRow(
                    object_class=row["object"],
                    source_split=row["split"],
                    label=row["label"],
                    image=row["image"],
                    mask=row["mask"],
                    source_csv=f"{name}.csv",
                )
                for row in reader
            ]
        split_rows[name] = rows
    return split_rows


def derive_split_partitions(
    split_rows: Mapping[str, Sequence[SplitRow]],
) -> dict[str, list[SplitRow]]:
    by_image: dict[str, SplitRow] = {}
    for row in split_rows["1cls"]:
        if row.image in by_image:
            raise AcquisitionError(f"duplicate image in upstream 1cls.csv: {row.image}")
        by_image[row.image] = row

    validation_images = {
        row.image for row in split_rows["2cls_fewshot"] if row.source_split == "train"
    }
    test_images = {
        row.image for row in split_rows["2cls_highshot"] if row.source_split == "test"
    }
    overlap = validation_images & test_images
    if overlap:
        raise AcquisitionError(
            "official split CSV membership overlaps validation and test: "
            + sorted(overlap)[0]
        )

    train_rows = [
        row
        for row in split_rows["1cls"]
        if row.label == "normal" and row.image not in validation_images | test_images
    ]
    validation_rows: list[SplitRow] = []
    for row in split_rows["2cls_fewshot"]:
        if row.source_split == "train":
            if row.image not in by_image:
                raise AcquisitionError(f"validation image not present in 1cls.csv: {row.image}")
            validation_rows.append(row)
    test_rows: list[SplitRow] = []
    for row in split_rows["2cls_highshot"]:
        if row.source_split == "test":
            if row.image not in by_image:
                raise AcquisitionError(f"test image not present in 1cls.csv: {row.image}")
            test_rows.append(row)
    partitions = {
        "train": train_rows,
        "validation": validation_rows,
        "test": test_rows,
    }
    validate_partition_shape(partitions)
    return partitions


def validate_partition_shape(partitions: Mapping[str, Sequence[SplitRow]]) -> None:
    images_by_partition = {
        partition: {row.image for row in rows} for partition, rows in partitions.items()
    }
    for partition in SPLIT_MANIFEST_NAMES:
        if not partitions[partition]:
            raise AcquisitionError(f"{partition} split manifest would be empty")
    if any(row.label != "normal" for row in partitions["train"]):
        raise AcquisitionError("train split contains non-normal images")
    for partition in ("validation", "test"):
        labels = {row.label for row in partitions[partition]}
        if labels != {"normal", "anomaly"}:
            raise AcquisitionError(f"{partition} split is not mixed normal/anomaly")
    for left in SPLIT_MANIFEST_NAMES:
        for right in SPLIT_MANIFEST_NAMES:
            if left >= right:
                continue
            overlap = images_by_partition[left] & images_by_partition[right]
            if overlap:
                raise AcquisitionError(
                    f"split overlap between {left} and {right}: {sorted(overlap)[0]}"
                )


def extracted_relative_path(path: Path) -> str:
    return path.relative_to(EXTRACTED_DIR).as_posix()


def write_split_manifests(
    partitions: Mapping[str, Sequence[SplitRow]],
    extracted_hashes: Mapping[str, str],
) -> dict[str, str]:
    root = dataset_root()
    manifest_hashes: dict[str, str] = {}
    for partition in SPLIT_MANIFEST_NAMES:
        manifest_path = SPLITS_DIR / f"{partition}.csv"
        lines = [
            "filename,class,label,artifact_type,sha256,"
            "source_csv,source_split,source_label,source_image,source_mask\n"
        ]
        rows = sorted(
            partitions[partition],
            key=lambda row: (row.object_class, row.label, row.image),
        )
        for row in rows:
            lines.append(
                split_manifest_line(
                    root,
                    extracted_hashes,
                    row,
                    artifact_type="image",
                    filename=row.image,
                )
            )
            if row.mask:
                lines.append(
                    split_manifest_line(
                        root,
                        extracted_hashes,
                        row,
                        artifact_type="mask",
                        filename=row.mask,
                    )
                )
        write_governed_record(manifest_path, "".join(lines).encode("utf-8"))
        manifest_hashes[partition] = write_record_hash(manifest_path)
    return manifest_hashes


def split_manifest_line(
    root: Path,
    extracted_hashes: Mapping[str, str],
    row: SplitRow,
    *,
    artifact_type: str,
    filename: str,
) -> str:
    artifact_path = root / filename
    if not artifact_path.exists():
        raise AcquisitionError(f"split artifact missing from extracted dataset: {filename}")
    extracted_relative = extracted_relative_path(artifact_path)
    digest = extracted_hashes.get(extracted_relative)
    if digest is None:
        raise AcquisitionError(
            f"split artifact absent from files.sha256 manifest: {extracted_relative}"
        )
    values = [
        filename,
        row.object_class,
        row.label,
        artifact_type,
        digest,
        row.source_csv,
        row.source_split,
        row.label,
        row.image,
        row.mask,
    ]
    return ",".join(csv_escape(value) for value in values) + "\n"


def csv_escape(value: str) -> str:
    if any(character in value for character in [",", '"', "\n", "\r"]):
        return '"' + value.replace('"', '""') + '"'
    return value


def split_counts(partitions: Mapping[str, Sequence[SplitRow]]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for partition, rows in partitions.items():
        labels = Counter(row.label for row in rows)
        classes = Counter(row.object_class for row in rows)
        summary[partition] = {
            "image_rows": len(rows),
            "labels": dict(sorted(labels.items())),
            "classes": dict(sorted(classes.items())),
        }
    return summary


def attribution_content() -> bytes:
    return (
        "# VisA Attribution and Licensing Record\n\n"
        "This record is part of Kalibra's governed VisA acquisition envelope.\n\n"
        "## Dataset\n\n"
        "- Dataset: VisA / Visual Anomaly.\n"
        "- Source: official Amazon Science `spot-diff` repository pinned at "
        f"`{UPSTREAM_COMMIT}` and the canonical S3 archive `{ARCHIVE_URL}`.\n"
        "- Authors: Yang Zou, Jongheon Jeong, Latha Pemula, Dongqing Zhang, "
        "and Onkar Dabeer.\n"
        "- Publication: `SPot-the-Difference Self-Supervised Pre-training for "
        "Anomaly Detection and Segmentation`, ECCV 2022 / LNCS, pp. 392-408.\n"
        f"- DOI: `{DOI}`.\n"
        f"- arXiv: `{ARXIV}`.\n\n"
        "## Licenses\n\n"
        "- Dataset license: Creative Commons Attribution 4.0 International "
        "(`CC BY 4.0`), as recorded by the official `LICENSE-DATASET` file.\n"
        "- Utility code license: Apache License 2.0 (`Apache-2.0`), as recorded "
        "by the official repository `LICENSE` file.\n"
        "- NOTICE: the official repository `NOTICE` record must be preserved "
        "when repository utility code or NOTICE-bearing material is redistributed.\n\n"
        "## Attribution Obligations\n\n"
        "Any redistributed or derived dataset artifact must provide credit to "
        "the authors, identify the CC BY 4.0 dataset license, link or refer to "
        "the license text, and indicate whether changes were made. Kalibra's "
        "governed acquisition stores the canonical archive and extracted source "
        "tree without dataset-byte changes; generated hash manifests, split "
        "manifests, provenance, and evidence records are Kalibra governance "
        "records over those source bytes.\n\n"
        "## Source Disagreement Resolution\n\n"
        "Secondary CC BY-NC-SA 4.0 claims are not authoritative for this "
        "acquisition. The official Amazon Science repository, dataset license "
        "file, NOTICE record, and AWS Open Data Registry govern this local "
        "record and identify the dataset license as CC BY 4.0.\n"
    ).encode("utf-8")


def write_attribution_record() -> str:
    attribution_path = PROVENANCE_DIR / "ATTRIBUTION.md"
    write_governed_record(attribution_path, attribution_content())
    return write_record_hash(attribution_path)


def build_provenance(
    archive_record: ArchiveRecord,
    manifest_hashes: Mapping[str, str],
    upstream_split_hashes: Mapping[str, str],
    attribution_hash: str,
    acquisition_timestamp: str,
) -> dict[str, object]:
    files_manifest_hash = sha256_file(MANIFESTS_DIR / "files.sha256")
    archive_record_hash = sha256_file(MANIFESTS_DIR / "archive.sha256")
    archive_metadata_hash = sha256_file(MANIFESTS_DIR / "archive_metadata.json")
    provenance = {
        "schema": "kalibra_governed_visa_provenance_v1",
        "dataset": {
            "name": "VisA",
            "full_name": "Visual Anomaly",
            "role": "governed proxy dataset for the first Kalibra ML baseline",
            "upstream_version": ARCHIVE_STEM,
        },
        "acquisition": {
            "source": {
                "canonical_repository_url": UPSTREAM_REPO_DISPLAY_URL,
                "repository_commit": UPSTREAM_COMMIT,
                "canonical_archive_url": ARCHIVE_URL,
                "aws_open_data_registry_url": OPEN_DATA_REGISTRY_URL,
                "mirrors_used": [],
            },
            "timestamp_utc": acquisition_timestamp,
            "method": (
                "Fetched only from the canonical S3 archive URL and adopted split "
                "CSVs only from the pinned official Amazon Science repository commit."
            ),
        },
        "upstream_identifiers": {
            "archive_name": ARCHIVE_STEM,
            "archive_filename": ARCHIVE_FILENAME,
            "repository": "amazon-science/spot-diff",
            "repository_commit": UPSTREAM_COMMIT,
            "aws_arn": ARCHIVE_AWS_ARN,
            "doi": DOI,
            "arxiv": ARXIV,
        },
        "licenses": {
            "dataset": {
                "name": "Creative Commons Attribution 4.0 International",
                "spdx": "CC-BY-4.0",
                "upstream_file": "LICENSE-DATASET",
            },
            "utility_code": {
                "name": "Apache License 2.0",
                "spdx": "Apache-2.0",
                "upstream_file": "LICENSE",
            },
            "notice": {
                "upstream_file": "NOTICE",
                "required": True,
            },
        },
        "attribution": {
            "authors": [
                "Yang Zou",
                "Jongheon Jeong",
                "Latha Pemula",
                "Dongqing Zhang",
                "Onkar Dabeer",
            ],
            "title": (
                "SPot-the-Difference Self-Supervised Pre-training for Anomaly "
                "Detection and Segmentation"
            ),
            "venue": "ECCV 2022 / Springer LNCS",
            "organizations": ["AWS AI Labs", "KAIST"],
            "copyright": "Amazon.com, Inc. or its affiliates",
            "obligations": [
                "credit the authors",
                "reference the CC BY 4.0 dataset license",
                "indicate changes for derived or redistributed artifacts",
                "preserve applicable NOTICE information for utility code redistribution",
            ],
        },
        "archive": {
            "filename": ARCHIVE_FILENAME,
            "url": ARCHIVE_URL,
            "aws_arn": ARCHIVE_AWS_ARN,
            "sha256": archive_record.sha256,
            "size_bytes": archive_record.size_bytes,
            "stored_at": "data/visa/source/VisA_20220922.tar",
            "immutable": True,
        },
        "archive_metadata": archive_record.metadata,
        "manifest_hashes": {
            "archive_sha256_record": archive_record_hash,
            "archive_metadata": archive_metadata_hash,
            "files_sha256": files_manifest_hash,
            "split_manifests": dict(sorted(manifest_hashes.items())),
            "upstream_split_csvs": dict(sorted(upstream_split_hashes.items())),
            "attribution_record": attribution_hash,
        },
        "local_governed_identity": {
            "label": "visa-acq-v1",
            "layout": "data/visa/{source,extracted,manifests,manifests/splits,provenance,derived}",
            "archive_sha256": archive_record.sha256,
            "files_manifest_sha256": files_manifest_hash,
            "split_manifest_sha256": dict(sorted(manifest_hashes.items())),
            "provenance_record": "data/visa/provenance/provenance.json",
        },
        "source_disagreement_note": (
            "Secondary CC BY-NC-SA 4.0 license claims are superseded by the "
            "official Amazon Science repository and AWS Open Data records, which "
            "identify the dataset license as CC BY 4.0."
        ),
        "split_policy": {
            "name": "kalibra_visa_acquisition_split_policy_v1",
            "basis": "official upstream split CSVs at the pinned repository commit",
            "train": (
                "normal images from upstream 1cls.csv not reserved by the validation "
                "or test memberships below"
            ),
            "validation": "rows marked train in upstream 2cls_fewshot.csv",
            "test": "rows marked test in upstream 2cls_highshot.csv",
            "claim_boundary": (
                "This records immutable acquisition manifests only. It executes no "
                "training, no operating-point derivation, no evaluation, and no metric."
            ),
        },
        "scope_boundaries": {
            "model_training": False,
            "padim_fitting": False,
            "onnx_export": False,
            "preprocessing_change": False,
            "provider_change": False,
            "evaluation_execution": False,
            "benchmark_generation": False,
            "scientific_claim": False,
        },
    }
    return provenance


def write_provenance(provenance: Mapping[str, object]) -> str:
    validate_provenance(provenance)
    path = PROVENANCE_DIR / "provenance.json"
    write_json_record(path, provenance)
    return write_record_hash(path)


def acquisition_timestamp_for_run() -> str:
    provenance_path = PROVENANCE_DIR / "provenance.json"
    if not provenance_path.exists():
        return utc_timestamp()
    provenance = json.loads(provenance_path.read_text())
    acquisition = provenance.get("acquisition")
    if not isinstance(acquisition, Mapping):
        raise AcquisitionError("existing provenance has invalid acquisition record")
    timestamp = acquisition.get("timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp:
        raise AcquisitionError("existing provenance lacks acquisition timestamp")
    return timestamp


def validate_provenance(provenance: Mapping[str, object]) -> None:
    missing = REQUIRED_PROVENANCE_TOP_LEVEL_KEYS - set(provenance)
    if missing:
        raise AcquisitionError(
            "provenance missing required top-level keys: " + ", ".join(sorted(missing))
        )
    acquisition = provenance["acquisition"]
    if not isinstance(acquisition, Mapping):
        raise AcquisitionError("provenance acquisition record is not an object")
    source = acquisition.get("source")
    if not isinstance(source, Mapping):
        raise AcquisitionError("provenance acquisition source is not an object")
    if source.get("canonical_archive_url") != ARCHIVE_URL:
        raise AcquisitionError("provenance does not name the canonical archive URL")
    if source.get("repository_commit") != UPSTREAM_COMMIT:
        raise AcquisitionError("provenance does not name the pinned upstream commit")
    if source.get("mirrors_used") != []:
        raise AcquisitionError("provenance indicates mirror use")


def parse_sha256_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise AcquisitionError(f"invalid sha256 manifest line {line_number}: {path}") from error
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise AcquisitionError(f"invalid sha256 digest in {path}:{line_number}")
        if relative in entries:
            raise AcquisitionError(f"duplicate sha256 manifest path in {path}: {relative}")
        entries[relative] = digest
    return entries


def verify_files_manifest(root: Path, manifest_path: Path) -> None:
    recorded = parse_sha256_manifest(manifest_path)
    actual_paths = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in iter_files(root)
    }
    if recorded != actual_paths:
        missing = sorted(set(recorded) - set(actual_paths))
        added = sorted(set(actual_paths) - set(recorded))
        changed = sorted(
            path
            for path in set(recorded) & set(actual_paths)
            if recorded[path] != actual_paths[path]
        )
        detail = {
            "missing": missing[:3],
            "added": added[:3],
            "changed": changed[:3],
        }
        raise AcquisitionError(f"per-file manifest mismatch: {detail}")


def verify_record_hash(path: Path) -> None:
    hash_path = path.with_name(path.name + ".sha256")
    if not hash_path.exists():
        raise AcquisitionError(f"missing governed record hash: {hash_path}")
    expected_entries = parse_sha256_manifest(hash_path)
    expected = expected_entries.get(path.name)
    if expected is None:
        raise AcquisitionError(f"governed record hash does not reference {path.name}")
    actual = sha256_file(path)
    if expected != actual:
        raise AcquisitionError(
            f"governed record hash mismatch for {path}: expected {expected}, got {actual}"
        )


def verify_archive(archive_path: Path) -> None:
    entries = parse_sha256_manifest(MANIFESTS_DIR / "archive.sha256")
    expected = entries.get("../source/VisA_20220922.tar")
    if expected is None:
        raise AcquisitionError("archive.sha256 does not reference the source archive")
    actual = sha256_file(archive_path)
    if expected != actual:
        raise AcquisitionError(
            f"archive hash mismatch: expected {expected}, got {actual}"
        )


def verify_split_manifests() -> None:
    for partition in SPLIT_MANIFEST_NAMES:
        verify_record_hash(SPLITS_DIR / f"{partition}.csv")
    for name in UPSTREAM_SPLIT_CSVS:
        verify_record_hash(SPLITS_DIR / f"upstream_{name}.csv")


def verify_derived_empty() -> None:
    entries = [path for path in DERIVED_DIR.rglob("*") if path.name != ".DS_Store"]
    if entries:
        raise AcquisitionError("derived directory is not empty")


def verify_governed_acquisition() -> None:
    archive_path = SOURCE_DIR / ARCHIVE_FILENAME
    verify_archive(archive_path)
    verify_record_hash(MANIFESTS_DIR / "files.sha256")
    verify_files_manifest(EXTRACTED_DIR, MANIFESTS_DIR / "files.sha256")
    verify_record_hash(MANIFESTS_DIR / "archive_metadata.json")
    verify_split_manifests()
    verify_record_hash(PROVENANCE_DIR / "ATTRIBUTION.md")
    verify_record_hash(PROVENANCE_DIR / "provenance.json")
    provenance = json.loads((PROVENANCE_DIR / "provenance.json").read_text())
    validate_provenance(provenance)
    verify_derived_empty()


def upstream_split_hashes() -> dict[str, str]:
    return {
        name: sha256_file(SPLITS_DIR / f"upstream_{name}.csv")
        for name in UPSTREAM_SPLIT_CSVS
    }


def write_evidence(
    archive_record: ArchiveRecord,
    manifest_hashes: Mapping[str, str],
    provenance_hash: str,
    partitions: Mapping[str, Sequence[SplitRow]],
    fail_closed_cases: Sequence[str],
) -> None:
    files_manifest_hash = sha256_file(MANIFESTS_DIR / "files.sha256")
    attribution_hash = sha256_file(PROVENANCE_DIR / "ATTRIBUTION.md")
    counts = split_counts(partitions)
    content = f"""# Kalibra Governed VisA Acquisition Evidence v1.0

**Status:** Recorded — governed acquisition evidence only
**Date:** {datetime.now(timezone.utc).date().isoformat()}
**Scope:** Acquisition infrastructure and acquisition evidence only

## Canonical Source Used

- Official repository: `{UPSTREAM_REPO_DISPLAY_URL}`
- Pinned repository commit: `{UPSTREAM_COMMIT}`
- Canonical archive URL: `{ARCHIVE_URL}`
- AWS object identity: `{ARCHIVE_AWS_ARN}`
- Mirrors used: none

## Archive Metadata

- Archive filename: `{ARCHIVE_FILENAME}`
- Archive size: `{archive_record.size_bytes}`
- Archive SHA-256: `{archive_record.sha256}`
- Last-Modified: `{archive_record.metadata["last_modified"]}`
- Content-Type: `{archive_record.metadata["content_type"]}`
- ETag: `{archive_record.metadata["etag"]}` (corroboration only, not SHA-256)
- Metadata record: `data/visa/manifests/archive_metadata.json`

## Generated Acquisition Records

- Archive hash record: `data/visa/manifests/archive.sha256`
- Per-file hash manifest: `data/visa/manifests/files.sha256`
- Per-file manifest SHA-256: `{files_manifest_hash}`
- Split manifests: `data/visa/manifests/splits/train.csv`, `validation.csv`, `test.csv`
- Split manifest SHA-256 values:
  - train: `{manifest_hashes["train"]}`
  - validation: `{manifest_hashes["validation"]}`
  - test: `{manifest_hashes["test"]}`
- Provenance record: `data/visa/provenance/provenance.json`
- Provenance SHA-256: `{provenance_hash}`
- Attribution/licensing record: `data/visa/provenance/ATTRIBUTION.md`
- Attribution SHA-256: `{attribution_hash}`

## Split Manifest Summary

- Train image rows: `{counts["train"]["image_rows"]}`; labels: `{counts["train"]["labels"]}`
- Validation image rows: `{counts["validation"]["image_rows"]}`; labels: `{counts["validation"]["labels"]}`
- Test image rows: `{counts["test"]["image_rows"]}`; labels: `{counts["test"]["labels"]}`
- Split policy: official upstream split CSV membership from the pinned commit; no training, fitting, evaluation, metric, or operating point was executed.

## Provenance And Attribution

- Dataset license recorded: CC BY 4.0.
- Utility code license recorded: Apache-2.0.
- NOTICE requirement recorded: upstream NOTICE obligations must be preserved for applicable utility-code redistribution.
- DOI recorded: `{DOI}`.
- arXiv recorded: `{ARXIV}`.
- Secondary CC BY-NC-SA claims are recorded as superseded by the official CC BY 4.0 dataset license record.

## Fail-Closed Verification

The acquisition tooling self-test verified hard-stop behavior for:
{chr(10).join(f"- {case}" for case in fail_closed_cases)}

The governed verification also recomputed the archive hash, every extracted file hash, every split manifest hash, provenance hash, and attribution hash before this evidence record was written.

## Local Governed Version Identity

```text
visa-acq-v1
archive_sha256={archive_record.sha256}
files_manifest_sha256={files_manifest_hash}
train_split_sha256={manifest_hashes["train"]}
validation_split_sha256={manifest_hashes["validation"]}
test_split_sha256={manifest_hashes["test"]}
provenance_sha256={provenance_hash}
```

## Explicit Non-Claims

- No PaDiM training or fitting was performed.
- No model was exported.
- No preprocessing was changed.
- No inference provider was changed.
- No output mapping was changed.
- No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration, or prototype UI code was modified.
- No evaluation was executed.
- No metric, benchmark, calibrated-confidence statement, scientific claim, product claim, or architecture change is made by this evidence record.
"""
    write_governed_record(EVIDENCE_PATH, content.encode("utf-8"))


def run_fail_closed_self_test() -> list[str]:
    cases = [
        self_test_archive_hash_mismatch,
        self_test_missing_file,
        self_test_changed_file,
        self_test_split_hash_mismatch,
        self_test_provenance_mismatch,
    ]
    passed: list[str] = []
    for case in cases:
        case()
        passed.append(case.__name__.replace("self_test_", "").replace("_", " "))
    return passed


def self_test_archive_hash_mismatch() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        archive = temp / "archive.tar"
        archive.write_bytes(b"archive")
        manifest = temp / "archive.sha256"
        manifest.write_text(f"{'0' * 64}  archive.tar\n")
        try:
            entries = parse_sha256_manifest(manifest)
            expected = entries["archive.tar"]
            actual = sha256_file(archive)
            if expected != actual:
                raise AcquisitionError("archive hash mismatch")
        except AcquisitionError:
            return
    raise AssertionError("archive hash mismatch did not fail closed")


def self_test_missing_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        root = temp / "root"
        root.mkdir()
        manifest = temp / "files.sha256"
        manifest.write_text(f"{'0' * 64}  missing.txt\n")
        expect_acquisition_error(lambda: verify_files_manifest(root, manifest))


def self_test_changed_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        root = temp / "root"
        root.mkdir()
        file_path = root / "file.txt"
        file_path.write_text("before")
        manifest = temp / "files.sha256"
        manifest.write_text(f"{sha256_file(file_path)}  file.txt\n")
        file_path.write_text("after")
        expect_acquisition_error(lambda: verify_files_manifest(root, manifest))


def self_test_split_hash_mismatch() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        manifest = temp / "validation.csv"
        manifest.write_text("filename,class,sha256\n")
        hash_path = temp / "validation.csv.sha256"
        hash_path.write_text(f"{sha256_file(manifest)}  validation.csv\n")
        manifest.write_text("filename,class,sha256\nchanged,part," + "0" * 64 + "\n")
        expect_acquisition_error(lambda: verify_record_hash(manifest))


def self_test_provenance_mismatch() -> None:
    expect_acquisition_error(lambda: validate_provenance({"schema": "bad"}))


def expect_acquisition_error(callback: object) -> None:
    try:
        callback()  # type: ignore[operator]
    except AcquisitionError:
        return
    raise AssertionError("expected fail-closed AcquisitionError")


def acquire(upstream_repo: Path) -> None:
    ensure_layout()
    ensure_upstream_checkout(upstream_repo)
    acquisition_timestamp = acquisition_timestamp_for_run()
    metadata = fetch_archive_metadata()
    archive_path = SOURCE_DIR / ARCHIVE_FILENAME
    download_archive(archive_path)
    archive_record = record_archive(archive_path, metadata)
    safe_extract_tar(archive_path, EXTRACTED_DIR)
    make_tree_read_only(EXTRACTED_DIR)
    extracted_hashes = build_files_manifest()
    split_rows = read_upstream_split_csvs(upstream_repo)
    partitions = derive_split_partitions(split_rows)
    manifest_hashes = write_split_manifests(partitions, extracted_hashes)
    attribution_hash = write_attribution_record()
    provenance = build_provenance(
        archive_record,
        manifest_hashes,
        upstream_split_hashes(),
        attribution_hash,
        acquisition_timestamp,
    )
    provenance_hash = write_provenance(provenance)
    fail_closed_cases = run_fail_closed_self_test()
    verify_governed_acquisition()
    write_evidence(
        archive_record,
        manifest_hashes,
        provenance_hash,
        partitions,
        fail_closed_cases,
    )
    verify_governed_acquisition()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Governed VisA acquisition")
    parser.add_argument(
        "command",
        choices=("acquire", "verify", "self-test"),
        help="operation to run",
    )
    parser.add_argument(
        "--upstream-repo",
        default=str(REPO_ROOT / ".local" / "spot-diff"),
        help="local official amazon-science/spot-diff checkout",
    )
    args = parser.parse_args(argv)

    try:
        if args.command == "acquire":
            acquire(Path(args.upstream_repo))
        elif args.command == "verify":
            verify_governed_acquisition()
        elif args.command == "self-test":
            print(json.dumps({"passed": run_fail_closed_self_test()}, indent=2))
    except AcquisitionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
