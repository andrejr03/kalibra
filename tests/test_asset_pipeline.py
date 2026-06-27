from __future__ import annotations

from pathlib import Path

from PIL import Image

from tools import generate_kalibra_part_assets as pipeline


def file_hashes(paths: list[Path]) -> dict[str, str]:
    return {
        str(path.relative_to(pipeline.GENERATED_DIR)): pipeline.sha256_file(path)
        for path in paths
    }


def generated_paths() -> list[Path]:
    return [
        pipeline.output_dir_for_source(source_path) / name
        for source_path in pipeline.discover_master_images()
        for name in sorted(pipeline.OUTPUT_SPECS)
    ]


def generated_root_entries() -> set[str]:
    return {path.name for path in pipeline.visible_children(pipeline.GENERATED_DIR)}


def expected_generated_directories() -> set[str]:
    return {path.stem for path in pipeline.discover_master_images()}


def parts_files_outside_generated() -> list[Path]:
    return sorted(
        path.relative_to(pipeline.PARTS_DIR)
        for path in pipeline.PARTS_DIR.rglob("*")
        if path.is_file() and not path.is_relative_to(pipeline.GENERATED_DIR)
    )


def test_pipeline_detects_multiple_master_images() -> None:
    master_paths = pipeline.discover_master_images()

    assert len(master_paths) >= 2
    assert [path.name for path in master_paths] == sorted(
        path.name for path in master_paths
    )
    assert {"master_clean.png", "master_clean_v2.png"}.issubset(
        {path.name for path in master_paths}
    )


def test_pipeline_preserves_source_images() -> None:
    source_hashes_before = {
        path: pipeline.sha256_file(path) for path in pipeline.discover_master_images()
    }

    pipeline.generate_assets()

    assert {
        path: pipeline.sha256_file(path) for path in pipeline.discover_master_images()
    } == source_hashes_before


def test_generated_files_exist_with_exact_png_dimensions() -> None:
    pipeline.generate_assets()

    assert generated_root_entries() == expected_generated_directories()
    for source_path in pipeline.discover_master_images():
        output_dir = pipeline.output_dir_for_source(source_path)
        assert output_dir.is_dir()
        assert {path.name for path in pipeline.visible_children(output_dir)} == set(
            pipeline.OUTPUT_SPECS
        )
        for file_name, expected_size in pipeline.OUTPUT_SPECS.items():
            output_path = output_dir / file_name
            assert output_path.exists()
            with Image.open(output_path) as image:
                assert image.format == "PNG"
                assert image.size == expected_size


def test_thumbnail_outputs_exist_with_exact_png_dimensions() -> None:
    pipeline.generate_assets()

    for source_path in pipeline.discover_master_images():
        output_dir = pipeline.output_dir_for_source(source_path)
        assert set(pipeline.THUMBNAIL_NAMES).issubset(
            {path.name for path in pipeline.visible_children(output_dir)}
        )
        for file_name in pipeline.THUMBNAIL_NAMES:
            output_path = output_dir / file_name
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
    assert {
        Path("source") / path.name for path in pipeline.discover_master_images()
    }.issubset(set(before))
    assert generated_root_entries() == expected_generated_directories()
