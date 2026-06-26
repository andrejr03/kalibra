from __future__ import annotations

import argparse
import hashlib
import math
import sys
from collections import deque
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = REPO_ROOT / "assets" / "parts"
SOURCE_IMAGE_PATH = PARTS_DIR / "source" / "master_clean.png"
GENERATED_DIR = PARTS_DIR / "generated"

PART_CLEAN_NAME = "part_clean.png"
PART_MAIN_NAME = "part_main.png"
PART_LOCALIZATION_NAME = "part_localization.png"

PART_CLEAN_SIZE = (960, 600)
PART_MAIN_SIZE = (960, 600)
PART_LOCALIZATION_SIZE = (520, 460)

OUTPUT_SPECS = {
    PART_CLEAN_NAME: PART_CLEAN_SIZE,
    PART_MAIN_NAME: PART_MAIN_SIZE,
    PART_LOCALIZATION_NAME: PART_LOCALIZATION_SIZE,
}

FOREGROUND_LUMA_THRESHOLD = 55
TARGET_OBJECT_OCCUPANCY = 0.80

ANOMALY_X = 690
ANOMALY_Y = 292
ANOMALY_RADIUS = 48
ANOMALY_INTENSITY = 1.0
ANOMALY_COLORS = {
    "outer": (255, 196, 57),
    "middle": (245, 94, 54),
    "core": (255, 247, 148),
    "contour": (255, 255, 255),
    "accent": (60, 150, 255),
}
ANOMALY_OPACITY = 0.56
OVERLAY_FEATHER_RADIUS = 16
OVERLAY_CONTOUR_WIDTH = 4
OVERLAY_CONTOUR_DASH_PATTERN = (18, 10)


class AssetPipelineError(RuntimeError):
    """Raised when the deterministic asset pipeline cannot complete safely."""


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


def load_source_image() -> Image.Image:
    if not SOURCE_IMAGE_PATH.exists():
        raise AssetPipelineError(f"source image is missing: {SOURCE_IMAGE_PATH}")
    if not SOURCE_IMAGE_PATH.is_file():
        raise AssetPipelineError(f"source image is not a file: {SOURCE_IMAGE_PATH}")

    try:
        with Image.open(SOURCE_IMAGE_PATH) as image:
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


def scaled_alpha(multiplier: float) -> int:
    alpha = 255 * ANOMALY_OPACITY * ANOMALY_INTENSITY * multiplier
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
) -> Image.Image:
    base = image.convert("RGBA")
    center_x, center_y = center

    heat = Image.new("RGBA", base.size, (0, 0, 0, 0))
    heat_draw = ImageDraw.Draw(heat, "RGBA")
    for radius_multiplier, color_name, alpha_multiplier in (
        (1.35, "outer", 0.42),
        (0.92, "middle", 0.68),
        (0.48, "core", 0.82),
    ):
        radius = int(round(ANOMALY_RADIUS * radius_multiplier))
        heat_draw.ellipse(
            (
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ),
            fill=rgba(color_name, scaled_alpha(alpha_multiplier)),
        )
    heat = heat.filter(ImageFilter.GaussianBlur(OVERLAY_FEATHER_RADIUS))
    composed = Image.alpha_composite(base, heat)

    contour = Image.new("RGBA", base.size, (0, 0, 0, 0))
    contour_draw = ImageDraw.Draw(contour, "RGBA")
    contour_radius = ANOMALY_RADIUS + OVERLAY_CONTOUR_WIDTH
    contour_bbox = (
        center_x - contour_radius,
        center_y - contour_radius,
        center_x + contour_radius,
        center_y + contour_radius,
    )
    draw_dashed_ellipse(
        contour_draw,
        contour_bbox,
        rgba("contour", scaled_alpha(0.95)),
        OVERLAY_CONTOUR_WIDTH,
        OVERLAY_CONTOUR_DASH_PATTERN,
    )

    marker_size = max(8, ANOMALY_RADIUS // 4)
    marker_color = rgba("accent", scaled_alpha(0.9))
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


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", optimize=False)


def validate_outputs(expected_source_hash: str | None = None) -> None:
    current_hash = sha256_file(SOURCE_IMAGE_PATH)
    load_source_image()

    if expected_source_hash is not None:
        if current_hash != expected_source_hash:
            raise AssetPipelineError("source image changed during pipeline execution")

    if not GENERATED_DIR.exists():
        raise AssetPipelineError(f"generated folder is missing: {GENERATED_DIR}")
    if not GENERATED_DIR.is_dir():
        raise AssetPipelineError(f"generated path is not a folder: {GENERATED_DIR}")

    expected_names = set(OUTPUT_SPECS)
    actual_names = {path.name for path in GENERATED_DIR.iterdir()}
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        raise AssetPipelineError(f"missing generated files: {', '.join(missing)}")
    if unexpected:
        raise AssetPipelineError(f"unexpected generated files: {', '.join(unexpected)}")

    for file_name, expected_size in OUTPUT_SPECS.items():
        path = GENERATED_DIR / file_name
        if not path.is_file():
            raise AssetPipelineError(f"generated output is not a file: {path}")
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise AssetPipelineError(f"{file_name} is not a PNG")
                if image.size != expected_size:
                    raise AssetPipelineError(
                        f"{file_name} has size {image.size}, expected {expected_size}"
                    )
        except UnidentifiedImageError as error:
            raise AssetPipelineError(f"{file_name} cannot be decoded as a PNG") from error


def generate_assets() -> None:
    source_hash = sha256_file(SOURCE_IMAGE_PATH)
    source_image = load_source_image()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    clean = create_clean_asset(source_image)
    clean_path = GENERATED_DIR / PART_CLEAN_NAME
    save_png(clean, clean_path)

    with Image.open(clean_path) as clean_image:
        clean_image.load()
        clean_base = clean_image.convert("RGB")

    main = apply_anomaly_overlay(clean_base)
    save_png(main, GENERATED_DIR / PART_MAIN_NAME)

    localization_box = clamp_crop_box(
        ANOMALY_X,
        ANOMALY_Y,
        PART_LOCALIZATION_SIZE,
        clean_base.size,
    )
    localization_clean = clean_base.crop(localization_box)
    localization_center = (
        ANOMALY_X - localization_box[0],
        ANOMALY_Y - localization_box[1],
    )
    localization = apply_anomaly_overlay(localization_clean, localization_center)
    save_png(localization, GENERATED_DIR / PART_LOCALIZATION_NAME)

    validate_outputs(expected_source_hash=source_hash)


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
