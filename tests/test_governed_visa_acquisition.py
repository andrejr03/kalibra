from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "governed_visa_acquisition.py"
SPEC = importlib.util.spec_from_file_location("governed_visa_acquisition", SCRIPT_PATH)
assert SPEC is not None
visa = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = visa
SPEC.loader.exec_module(visa)


def row(
    object_class: str,
    split: str,
    label: str,
    image: str,
    mask: str = "",
    source_csv: str = "fixture.csv",
) -> object:
    return visa.SplitRow(
        object_class=object_class,
        source_split=split,
        label=label,
        image=image,
        mask=mask,
        source_csv=source_csv,
    )


def test_split_policy_uses_official_csv_membership_without_overlap() -> None:
    one_cls = [
        row("part", "train", "normal", "n1.jpg", source_csv="1cls.csv"),
        row("part", "train", "normal", "n2.jpg", source_csv="1cls.csv"),
        row("part", "train", "normal", "n3.jpg", source_csv="1cls.csv"),
        row("part", "test", "normal", "n4.jpg", source_csv="1cls.csv"),
        row("part", "test", "anomaly", "a1.jpg", "m1.png", source_csv="1cls.csv"),
        row("part", "test", "anomaly", "a2.jpg", "m2.png", source_csv="1cls.csv"),
    ]
    partitions = visa.derive_split_partitions(
        {
            "1cls": one_cls,
            "2cls_fewshot": [
                row("part", "train", "normal", "n2.jpg", source_csv="2cls_fewshot.csv"),
                row(
                    "part",
                    "train",
                    "anomaly",
                    "a1.jpg",
                    "m1.png",
                    source_csv="2cls_fewshot.csv",
                ),
            ],
            "2cls_highshot": [
                row("part", "test", "normal", "n4.jpg", source_csv="2cls_highshot.csv"),
                row(
                    "part",
                    "test",
                    "anomaly",
                    "a2.jpg",
                    "m2.png",
                    source_csv="2cls_highshot.csv",
                ),
            ],
        }
    )

    assert {entry.image for entry in partitions["train"]} == {"n1.jpg", "n3.jpg"}
    assert {entry.image for entry in partitions["validation"]} == {"n2.jpg", "a1.jpg"}
    assert {entry.image for entry in partitions["test"]} == {"n4.jpg", "a2.jpg"}


def test_split_policy_fails_closed_on_partition_overlap() -> None:
    one_cls = [
        row("part", "train", "normal", "n1.jpg", source_csv="1cls.csv"),
        row("part", "test", "anomaly", "a1.jpg", "m1.png", source_csv="1cls.csv"),
    ]

    with pytest.raises(visa.AcquisitionError):
        visa.derive_split_partitions(
            {
                "1cls": one_cls,
                "2cls_fewshot": [
                    row(
                        "part",
                        "train",
                        "anomaly",
                        "a1.jpg",
                        "m1.png",
                        source_csv="2cls_fewshot.csv",
                    ),
                ],
                "2cls_highshot": [
                    row(
                        "part",
                        "test",
                        "anomaly",
                        "a1.jpg",
                        "m1.png",
                        source_csv="2cls_highshot.csv",
                    ),
                ],
            }
        )


def test_write_governed_record_fails_when_existing_bytes_differ(tmp_path: Path) -> None:
    record = tmp_path / "record.txt"
    visa.write_governed_record(record, b"first")

    with pytest.raises(visa.AcquisitionError):
        visa.write_governed_record(record, b"second")


def test_verify_files_manifest_fails_closed_for_missing_file(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    manifest = tmp_path / "files.sha256"
    manifest.write_text(f"{'0' * 64}  missing.txt\n")

    with pytest.raises(visa.AcquisitionError):
        visa.verify_files_manifest(root, manifest)


def test_verify_files_manifest_fails_closed_for_changed_file(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    target = root / "file.txt"
    target.write_text("before")
    manifest = tmp_path / "files.sha256"
    manifest.write_text(f"{visa.sha256_file(target)}  file.txt\n")

    target.write_text("after")

    with pytest.raises(visa.AcquisitionError):
        visa.verify_files_manifest(root, manifest)


def test_verify_record_hash_fails_closed_for_split_drift(tmp_path: Path) -> None:
    manifest = tmp_path / "test.csv"
    manifest.write_text("filename,class,sha256\n")
    hash_path = tmp_path / "test.csv.sha256"
    hash_path.write_text(f"{visa.sha256_file(manifest)}  test.csv\n")
    manifest.write_text("filename,class,sha256\nchanged,part," + "0" * 64 + "\n")

    with pytest.raises(visa.AcquisitionError):
        visa.verify_record_hash(manifest)


def test_validate_provenance_fails_closed_for_missing_required_fields() -> None:
    with pytest.raises(visa.AcquisitionError):
        visa.validate_provenance({"schema": "kalibra_governed_visa_provenance_v1"})
