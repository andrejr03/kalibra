from __future__ import annotations

from pathlib import Path

from PIL import Image

from tools import generate_kalibra_part_assets as pipeline


def file_hashes(paths: list[Path]) -> dict[str, str]:
    return {path.name: pipeline.sha256_file(path) for path in paths}


def generated_paths() -> list[Path]:
    return [pipeline.GENERATED_DIR / name for name in sorted(pipeline.OUTPUT_SPECS)]


def parts_files_outside_generated() -> list[Path]:
    return sorted(
        path.relative_to(pipeline.PARTS_DIR)
        for path in pipeline.PARTS_DIR.rglob("*")
        if path.is_file() and not path.is_relative_to(pipeline.GENERATED_DIR)
    )


def test_pipeline_preserves_source_image() -> None:
    source_hash_before = pipeline.sha256_file(pipeline.SOURCE_IMAGE_PATH)

    pipeline.generate_assets()

    assert pipeline.sha256_file(pipeline.SOURCE_IMAGE_PATH) == source_hash_before


def test_generated_files_exist_with_exact_png_dimensions() -> None:
    pipeline.generate_assets()

    assert {path.name for path in pipeline.GENERATED_DIR.iterdir()} == set(
        pipeline.OUTPUT_SPECS
    )
    for file_name, expected_size in pipeline.OUTPUT_SPECS.items():
        output_path = pipeline.GENERATED_DIR / file_name
        assert output_path.exists()
        with Image.open(output_path) as image:
            assert image.format == "PNG"
            assert image.size == expected_size


def test_thumbnail_outputs_exist_with_exact_png_dimensions() -> None:
    pipeline.generate_assets()

    assert set(pipeline.THUMBNAIL_NAMES).issubset(
        {path.name for path in pipeline.GENERATED_DIR.iterdir()}
    )
    for file_name in pipeline.THUMBNAIL_NAMES:
        output_path = pipeline.GENERATED_DIR / file_name
        with Image.open(output_path) as image:
            assert image.format == "PNG"
            assert image.size == pipeline.THUMBNAIL_SIZE


def test_pipeline_execution_is_deterministic() -> None:
    pipeline.generate_assets()
    first_hashes = file_hashes(generated_paths())

    pipeline.generate_assets()
    second_hashes = file_hashes(generated_paths())

    assert second_hashes == first_hashes


def test_pipeline_writes_only_generated_part_assets() -> None:
    before = parts_files_outside_generated()

    pipeline.generate_assets()

    assert parts_files_outside_generated() == before
    assert Path("source/master_clean.png") in before
    assert {path.name for path in pipeline.GENERATED_DIR.iterdir()} == set(
        pipeline.OUTPUT_SPECS
    )
