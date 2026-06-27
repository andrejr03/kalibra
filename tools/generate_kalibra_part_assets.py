from __future__ import annotations

import argparse
import hashlib
import math
import sys
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = REPO_ROOT / "assets" / "parts"
SOURCE_DIR = PARTS_DIR / "source"
MASTER_IMAGE_PATTERN = "master_clean*.png"
GENERATED_DIR = PARTS_DIR / "generated"

PART_CLEAN_NAME = "part_clean.png"
PART_MAIN_NAME = "part_main.png"
PART_LOCALIZATION_NAME = "part_localization.png"

PART_CLEAN_SIZE = (960, 600)
PART_MAIN_SIZE = (960, 600)
PART_LOCALIZATION_SIZE = (520, 460)
THUMBNAIL_SIZE = (240, 160)
LOCALIZATION_CROP_WIDTH = 678
LOCALIZATION_CROP_HEIGHT = 600

THUMBNAIL_NAMES = (
    "thumb_01.png",
    "thumb_02.png",
    "thumb_03.png",
    "thumb_04.png",
    "thumb_05.png",
    "thumb_06.png",
    "thumb_07.png",
    "thumb_08.png",
)

OUTPUT_SPECS = {
    PART_CLEAN_NAME: PART_CLEAN_SIZE,
    PART_MAIN_NAME: PART_MAIN_SIZE,
    PART_LOCALIZATION_NAME: PART_LOCALIZATION_SIZE,
    **{thumbnail_name: THUMBNAIL_SIZE for thumbnail_name in THUMBNAIL_NAMES},
}

FOREGROUND_LUMA_THRESHOLD = 55
TARGET_OBJECT_OCCUPANCY = 0.80

ANOMALY_X = 690
ANOMALY_Y = 292
ANOMALY_RADIUS = 52
ANOMALY_INTENSITY = 1.0
ANOMALY_CENTER_OVERRIDES = {
    "master_clean_v2": (620, 292),
}
LOCALIZATION_CROP_SIZE_OVERRIDES = {
    "master_clean_v2": (620, 548),
}
ANOMALY_COLORS = {
    "outer": (255, 184, 64),
    "middle": (255, 111, 54),
    "core": (255, 232, 112),
    "contour": (72, 218, 255),
    "accent": (255, 255, 255),
}
ANOMALY_OPACITY = 0.72
OVERLAY_CENTER_ALPHA = 0.78
OVERLAY_EDGE_ALPHA = 0.34
OVERLAY_FEATHER_RADIUS = 12
OVERLAY_CONTOUR_WIDTH = 5
OVERLAY_CONTOUR_DASH_PATTERN = (20, 8)


@dataclass(frozen=True)
class ThumbnailSpec:
    file_name: str
    crop_center: tuple[int, int]
    crop_size: tuple[int, int]
    overlay_center: tuple[int, int] | None = None
    overlay_intensity: float = 1.0
    overlay_radius: int = 40


THUMBNAIL_SPECS = (
    ThumbnailSpec("thumb_01.png", (480, 300), (900, 600)),
    ThumbnailSpec("thumb_02.png", (690, 292), (600, 400), (690, 292)),
    ThumbnailSpec("thumb_03.png", (340, 302), (600, 400)),
    ThumbnailSpec("thumb_04.png", (520, 330), (660, 440), (548, 365), 0.42, 34),
    ThumbnailSpec("thumb_05.png", (330, 310), (600, 400), (322, 318)),
    ThumbnailSpec("thumb_06.png", (748, 310), (600, 400)),
    ThumbnailSpec("thumb_07.png", (720, 388), (600, 400), (760, 416), 1.0, 38),
    ThumbnailSpec("thumb_08.png", (430, 255), (660, 440), (418, 248), 0.40, 34),
)

THUMBNAIL_SPEC_OVERRIDES = {
    "master_clean_v2": {
        "thumb_02.png": {
            "crop_center": (620, 292),
            "overlay_center": (620, 292),
        },
        "thumb_07.png": {
            "crop_center": (660, 388),
            "overlay_center": (690, 416),
        },
        "thumb_08.png": {
            "overlay_center": (390, 248),
        },
    },
}


class AssetPipelineError(RuntimeError):
    """Raised when the deterministic asset pipeline cannot complete safely."""


def discover_master_images() -> tuple[Path, ...]:
    if not SOURCE_DIR.exists():
        raise AssetPipelineError(f"source folder is missing: {SOURCE_DIR}")
    if not SOURCE_DIR.is_dir():
        raise AssetPipelineError(f"source path is not a folder: {SOURCE_DIR}")

    master_paths = tuple(
        path
        for path in sorted(
            SOURCE_DIR.glob(MASTER_IMAGE_PATTERN),
            key=lambda item: item.name,
        )
        if path.is_file() and path.suffix == ".png"
    )
    if not master_paths:
        raise AssetPipelineError(
            f"no source images found matching {SOURCE_DIR / MASTER_IMAGE_PATTERN}"
        )
    return master_paths


def output_dir_for_source(source_path: Path) -> Path:
    return GENERATED_DIR / source_path.stem


def anomaly_center_for_source(source_path: Path) -> tuple[int, int]:
    return ANOMALY_CENTER_OVERRIDES.get(source_path.stem, (ANOMALY_X, ANOMALY_Y))


def localization_crop_size_for_source(source_path: Path) -> tuple[int, int]:
    return LOCALIZATION_CROP_SIZE_OVERRIDES.get(
        source_path.stem,
        (LOCALIZATION_CROP_WIDTH, LOCALIZATION_CROP_HEIGHT),
    )


def thumbnail_specs_for_source(source_path: Path) -> tuple[ThumbnailSpec, ...]:
    overrides = THUMBNAIL_SPEC_OVERRIDES.get(source_path.stem, {})
    specs = []
    for spec in THUMBNAIL_SPECS:
        spec_overrides = overrides.get(spec.file_name)
        if spec_overrides is not None:
            spec = replace(spec, **spec_overrides)
        specs.append(spec)
    return tuple(specs)


def sha256_file(path: Path) -> str:
    if not path.exists():
        raise AssetPipelineError(f"file is missing: {path}")
    if not path.is_file():
        raise AssetPipelineError(f"path is not a file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source_image(source_path: Path) -> Image.Image:
    if not source_path.exists():
        raise AssetPipelineError(f"source image is missing: {source_path}")
    if not source_path.is_file():
        raise AssetPipelineError(f"source image is not a file: {source_path}")

    try:
        with Image.open(source_path) as image:
            if image.format != "PNG":
                raise AssetPipelineError(
                    f"source image must be PNG, found {image.format!r}"
                )
            image.load()
            return image.convert("RGB")
    except UnidentifiedImageError as error:
        raise AssetPipelineError("source image cannot be decoded as a PNG") from error


def largest_foreground_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    width, height = image.size
    mask = image.convert("L").point(
        lambda value: 255 if value > FOREGROUND_LUMA_THRESHOLD else 0,
        "L",
    )
    mask_bytes = mask.tobytes()
    visited = bytearray(width * height)

    best_count = 0
    best_bbox: tuple[int, int, int, int] | None = None

    for start_index, value in enumerate(mask_bytes):
        if value == 0 or visited[start_index]:
            continue

        queue: deque[int] = deque([start_index])
        visited[start_index] = 1
        count = 0
        min_x = width
        min_y = height
        max_x = 0
        max_y = 0

        while queue:
            index = queue.popleft()
            y, x = divmod(index, width)
            count += 1
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            left = index - 1
            if x > 0 and mask_bytes[left] and not visited[left]:
                visited[left] = 1
                queue.append(left)

            right = index + 1
            if x < width - 1 and mask_bytes[right] and not visited[right]:
                visited[right] = 1
                queue.append(right)

            up = index - width
            if y > 0 and mask_bytes[up] and not visited[up]:
                visited[up] = 1
                queue.append(up)

            down = index + width
            if y < height - 1 and mask_bytes[down] and not visited[down]:
                visited[down] = 1
                queue.append(down)

        if count > best_count:
            best_count = count
            best_bbox = (min_x, min_y, max_x + 1, max_y + 1)

    if best_bbox is None:
        raise AssetPipelineError("source image does not contain a foreground object")

    return best_bbox


def center_crop_box(
    source_size: tuple[int, int],
    object_bbox: tuple[int, int, int, int],
    target_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    source_width, source_height = source_size
    target_width, target_height = target_size
    target_aspect = target_width / target_height

    object_left, object_top, object_right, object_bottom = object_bbox
    object_width = object_right - object_left
    object_height = object_bottom - object_top
    object_center_x = (object_left + object_right) / 2
    object_center_y = (object_top + object_bottom) / 2

    crop_width = max(
        object_width / TARGET_OBJECT_OCCUPANCY,
        (object_height / TARGET_OBJECT_OCCUPANCY) * target_aspect,
    )
    crop_height = crop_width / target_aspect

    if crop_width > source_width:
        crop_width = source_width
        crop_height = crop_width / target_aspect
    if crop_height > source_height:
        crop_height = source_height
        crop_width = crop_height * target_aspect

    crop_width = min(source_width, max(object_width, int(round(crop_width))))
    crop_height = min(source_height, max(object_height, int(round(crop_height))))

    if crop_width / crop_height > target_aspect:
        crop_width = int(round(crop_height * target_aspect))
    else:
        crop_height = int(round(crop_width / target_aspect))

    left = int(round(object_center_x - crop_width / 2))
    top = int(round(object_center_y - crop_height / 2))
    left = max(0, min(left, source_width - crop_width))
    top = max(0, min(top, source_height - crop_height))

    return (left, top, left + crop_width, top + crop_height)


def create_clean_asset(source_image: Image.Image) -> Image.Image:
    object_bbox = largest_foreground_bbox(source_image)
    crop_box = center_crop_box(source_image.size, object_bbox, PART_CLEAN_SIZE)
    return source_image.crop(crop_box).resize(
        PART_CLEAN_SIZE,
        Image.Resampling.LANCZOS,
    )


def clamp_crop_box(
    center_x: int,
    center_y: int,
    crop_size: tuple[int, int],
    image_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    crop_width, crop_height = crop_size
    image_width, image_height = image_size

    if crop_width > image_width or crop_height > image_height:
        raise AssetPipelineError("localization crop is larger than the clean asset")

    left = int(round(center_x - crop_width / 2))
    top = int(round(center_y - crop_height / 2))
    left = max(0, min(left, image_width - crop_width))
    top = max(0, min(top, image_height - crop_height))

    return (left, top, left + crop_width, top + crop_height)


def scaled_alpha(multiplier: float, intensity: float = ANOMALY_INTENSITY) -> int:
    alpha = 255 * ANOMALY_OPACITY * intensity * multiplier
    return max(0, min(255, int(round(alpha))))


def rgba(name: str, alpha: int) -> tuple[int, int, int, int]:
    red, green, blue = ANOMALY_COLORS[name]
    return (red, green, blue, alpha)


def draw_dashed_ellipse(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    width: int,
    dash_pattern: Iterable[int],
) -> None:
    pattern = tuple(dash_pattern)
    if not pattern:
        draw.ellipse(bbox, outline=fill, width=width)
        return

    radius_x = (bbox[2] - bbox[0]) / 2
    radius_y = (bbox[3] - bbox[1]) / 2
    circumference = 2 * math.pi * math.sqrt((radius_x**2 + radius_y**2) / 2)
    degrees_per_pixel = 360 / circumference

    angle = 0.0
    pattern_index = 0
    draw_segment = True
    while angle < 360:
        segment_degrees = pattern[pattern_index % len(pattern)] * degrees_per_pixel
        next_angle = min(360, angle + segment_degrees)
        if draw_segment:
            draw.arc(bbox, start=angle, end=next_angle, fill=fill, width=width)
        draw_segment = not draw_segment
        pattern_index += 1
        angle = next_angle


def apply_anomaly_overlay(
    image: Image.Image,
    center: tuple[int, int] = (ANOMALY_X, ANOMALY_Y),
    radius: int = ANOMALY_RADIUS,
    intensity: float = ANOMALY_INTENSITY,
) -> Image.Image:
    base = image.convert("RGBA")
    center_x, center_y = center

    heat = Image.new("RGBA", base.size, (0, 0, 0, 0))
    heat_draw = ImageDraw.Draw(heat, "RGBA")
    for radius_multiplier, color_name, alpha_multiplier in (
        (1.48, "outer", OVERLAY_EDGE_ALPHA),
        (1.00, "middle", (OVERLAY_CENTER_ALPHA + OVERLAY_EDGE_ALPHA) / 2),
        (0.48, "core", OVERLAY_CENTER_ALPHA),
    ):
        overlay_radius = int(round(radius * radius_multiplier))
        heat_draw.ellipse(
            (
                center_x - overlay_radius,
                center_y - overlay_radius,
                center_x + overlay_radius,
                center_y + overlay_radius,
            ),
            fill=rgba(color_name, scaled_alpha(alpha_multiplier, intensity)),
        )
    heat = heat.filter(ImageFilter.GaussianBlur(OVERLAY_FEATHER_RADIUS))
    composed = Image.alpha_composite(base, heat)

    contour = Image.new("RGBA", base.size, (0, 0, 0, 0))
    contour_draw = ImageDraw.Draw(contour, "RGBA")
    contour_radius = radius + OVERLAY_CONTOUR_WIDTH
    contour_bbox = (
        center_x - contour_radius,
        center_y - contour_radius,
        center_x + contour_radius,
        center_y + contour_radius,
    )
    draw_dashed_ellipse(
        contour_draw,
        contour_bbox,
        rgba("contour", scaled_alpha(0.95, intensity)),
        OVERLAY_CONTOUR_WIDTH,
        OVERLAY_CONTOUR_DASH_PATTERN,
    )

    marker_size = max(8, radius // 4)
    marker_color = rgba("accent", scaled_alpha(0.82, intensity))
    contour_draw.line(
        (center_x - marker_size, center_y, center_x + marker_size, center_y),
        fill=marker_color,
        width=2,
    )
    contour_draw.line(
        (center_x, center_y - marker_size, center_x, center_y + marker_size),
        fill=marker_color,
        width=2,
    )

    return Image.alpha_composite(composed, contour).convert("RGB")


def create_thumbnail_asset(clean_base: Image.Image, spec: ThumbnailSpec) -> Image.Image:
    crop_box = clamp_crop_box(
        spec.crop_center[0],
        spec.crop_center[1],
        spec.crop_size,
        clean_base.size,
    )
    thumbnail = clean_base.crop(crop_box).resize(
        THUMBNAIL_SIZE,
        Image.Resampling.LANCZOS,
    )

    if spec.overlay_center is None:
        return thumbnail

    scale_x = THUMBNAIL_SIZE[0] / spec.crop_size[0]
    scale_y = THUMBNAIL_SIZE[1] / spec.crop_size[1]
    overlay_center = (
        int(round((spec.overlay_center[0] - crop_box[0]) * scale_x)),
        int(round((spec.overlay_center[1] - crop_box[1]) * scale_y)),
    )
    overlay_radius = int(round(spec.overlay_radius * (scale_x + scale_y) / 2))

    return apply_anomaly_overlay(
        thumbnail,
        overlay_center,
        overlay_radius,
        spec.overlay_intensity,
    )


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", optimize=False)


def visible_children(path: Path) -> tuple[Path, ...]:
    return tuple(child for child in path.iterdir() if not child.name.startswith("."))


def remove_legacy_root_outputs() -> None:
    for file_name in OUTPUT_SPECS:
        legacy_path = GENERATED_DIR / file_name
        if not legacy_path.exists():
            continue
        if not legacy_path.is_file():
            raise AssetPipelineError(f"legacy output path is not a file: {legacy_path}")
        legacy_path.unlink()


def validate_output_set(output_dir: Path) -> None:
    if not output_dir.exists():
        raise AssetPipelineError(f"generated folder is missing: {output_dir}")
    if not output_dir.is_dir():
        raise AssetPipelineError(f"generated path is not a folder: {output_dir}")

    expected_names = set(OUTPUT_SPECS)
    actual_names = {path.name for path in visible_children(output_dir)}
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        raise AssetPipelineError(
            f"missing generated files in {output_dir.name}: {', '.join(missing)}"
        )
    if unexpected:
        raise AssetPipelineError(
            f"unexpected generated files in {output_dir.name}: {', '.join(unexpected)}"
        )

    for file_name, expected_size in OUTPUT_SPECS.items():
        path = output_dir / file_name
        if not path.is_file():
            raise AssetPipelineError(f"generated output is not a file: {path}")
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise AssetPipelineError(f"{path} is not a PNG")
                if image.size != expected_size:
                    raise AssetPipelineError(
                        f"{path} has size {image.size}, expected {expected_size}"
                    )
        except UnidentifiedImageError as error:
            raise AssetPipelineError(f"{path} cannot be decoded as a PNG") from error


def validate_outputs(expected_source_hashes: dict[Path, str] | None = None) -> None:
    master_paths = discover_master_images()
    current_hashes = {path: sha256_file(path) for path in master_paths}
    for source_path in master_paths:
        load_source_image(source_path)

    if expected_source_hashes is not None:
        if set(current_hashes) != set(expected_source_hashes):
            raise AssetPipelineError("source image set changed during pipeline execution")
        if current_hashes != expected_source_hashes:
            raise AssetPipelineError("source image changed during pipeline execution")

    if not GENERATED_DIR.exists():
        raise AssetPipelineError(f"generated folder is missing: {GENERATED_DIR}")
    if not GENERATED_DIR.is_dir():
        raise AssetPipelineError(f"generated path is not a folder: {GENERATED_DIR}")

    expected_names = {path.stem for path in master_paths}
    actual_children = visible_children(GENERATED_DIR)
    actual_names = {path.name for path in actual_children}
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        raise AssetPipelineError(
            f"missing generated master folders: {', '.join(missing)}"
        )
    if unexpected:
        raise AssetPipelineError(
            f"unexpected generated entries: {', '.join(unexpected)}"
        )

    for source_path in master_paths:
        output_dir = output_dir_for_source(source_path)
        validate_output_set(output_dir)


def generate_output_set(
    source_image: Image.Image,
    output_dir: Path,
    anomaly_center: tuple[int, int],
    localization_crop_size: tuple[int, int],
    thumbnail_specs: tuple[ThumbnailSpec, ...],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    clean = create_clean_asset(source_image)
    clean_path = output_dir / PART_CLEAN_NAME
    save_png(clean, clean_path)

    with Image.open(clean_path) as clean_image:
        clean_image.load()
        clean_base = clean_image.convert("RGB")

    main = apply_anomaly_overlay(clean_base, anomaly_center)
    save_png(main, output_dir / PART_MAIN_NAME)

    localization_box = clamp_crop_box(
        anomaly_center[0],
        anomaly_center[1],
        localization_crop_size,
        clean_base.size,
    )
    localization_clean = clean_base.crop(localization_box).resize(
        PART_LOCALIZATION_SIZE,
        Image.Resampling.LANCZOS,
    )
    scale_x = PART_LOCALIZATION_SIZE[0] / localization_crop_size[0]
    scale_y = PART_LOCALIZATION_SIZE[1] / localization_crop_size[1]
    localization_center = (
        int(round((anomaly_center[0] - localization_box[0]) * scale_x)),
        int(round((anomaly_center[1] - localization_box[1]) * scale_y)),
    )
    localization_radius = int(round(ANOMALY_RADIUS * (scale_x + scale_y) / 2))
    localization = apply_anomaly_overlay(
        localization_clean,
        localization_center,
        localization_radius,
    )
    save_png(localization, output_dir / PART_LOCALIZATION_NAME)

    for spec in thumbnail_specs:
        thumbnail = create_thumbnail_asset(clean_base, spec)
        save_png(thumbnail, output_dir / spec.file_name)


def generate_assets() -> None:
    master_paths = discover_master_images()
    source_hashes = {path: sha256_file(path) for path in master_paths}
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    remove_legacy_root_outputs()

    for source_path in master_paths:
        source_image = load_source_image(source_path)
        generate_output_set(
            source_image,
            output_dir_for_source(source_path),
            anomaly_center_for_source(source_path),
            localization_crop_size_for_source(source_path),
            thumbnail_specs_for_source(source_path),
        )

    validate_outputs(expected_source_hashes=source_hashes)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Kalibra prototype part assets."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate existing generated assets without regenerating them",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.check:
            validate_outputs()
        else:
            generate_assets()
    except AssetPipelineError as error:
        print(f"asset pipeline failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
