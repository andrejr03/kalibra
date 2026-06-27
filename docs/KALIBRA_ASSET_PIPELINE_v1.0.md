# KALIBRA Asset Pipeline v1.0

## 1. Purpose

The KALIBRA asset pipeline exists to derive prototype-ready inspection visuals
from fixed master images in a deterministic, reproducible way.

The pipeline provides:

- exact output dimensions for every generated asset;
- repeatable generation from immutable source images and fixed parameters;
- separation between asset generation and prototype UI files;
- separation from image-generation models, AI inference, inspection logic, and
  evaluation evidence.

Generated overlays are synthetic prototype visuals. They are not defect
detections, model localizations, calibration evidence, or performance claims.

## 2. Architecture Overview

The asset flow is:

```text
master inspection images
  -> deterministic asset pipeline
  -> generated prototype assets
  -> prototype UI
```

The pipeline is implemented by `tools/generate_kalibra_part_assets.py`. It reads
source images, derives clean and overlayed views, writes generated PNG outputs,
and validates the generated files after writing them.

Prototype work should consume the generated assets rather than manually
maintained image files. Manual edits belong in the source image or pipeline
parameter decisions, not in generated outputs.

## 3. Directory Structure

```text
assets/
  parts/
    source/
      master_clean.png
      master_clean_v2.png
    generated/
      master_clean/
        part_clean.png
        part_main.png
        part_localization.png
        thumb_01.png
        ...
        thumb_08.png
      master_clean_v2/
        part_clean.png
        part_main.png
        part_localization.png
        thumb_01.png
        ...
        thumb_08.png
tools/
  generate_kalibra_part_assets.py
tests/
  test_asset_pipeline.py
```

`assets/parts/source/` contains immutable source images. `assets/parts/generated/`
contains reproducible outputs grouped by source-image stem.

## 4. Supported Master Images

The pipeline discovers master images automatically from:

```text
assets/parts/source/
```

A supported master image is any PNG file matching:

```text
master_clean*.png
```

Each discovered source image is processed independently, and each output set is
written to:

```text
assets/parts/generated/<source-stem>/
```

Source images are immutable inputs. The pipeline reads them, hashes them during
generation, and validates that the source set has not changed during execution.
Generated assets never overwrite source images.

## 5. Generated Assets

For every discovered master image, the pipeline writes the same asset set.

| Asset | Dimensions | Purpose |
| --- | --- | --- |
| `part_clean.png` | `960 x 600` | Clean resized derivative of the master image. |
| `part_main.png` | `960 x 600` | Clean derivative with the configured synthetic anomaly overlay. |
| `part_localization.png` | `520 x 460` | Cropped localization-focused view using the same configured anomaly position. |
| `thumb_01.png` | `240 x 160` | Thumbnail derived from the clean inspection setup. |
| `thumb_02.png` | `240 x 160` | Thumbnail with configured review/defect overlay context. |
| `thumb_03.png` | `240 x 160` | Thumbnail derived from a clean contextual crop. |
| `thumb_04.png` | `240 x 160` | Thumbnail with lower-intensity overlay context. |
| `thumb_05.png` | `240 x 160` | Thumbnail with configured review/defect overlay context. |
| `thumb_06.png` | `240 x 160` | Thumbnail derived from a clean contextual crop. |
| `thumb_07.png` | `240 x 160` | Thumbnail with configured review/defect overlay context. |
| `thumb_08.png` | `240 x 160` | Thumbnail with lower-intensity overlay context. |

The generated assets are prototype visuals only. They do not represent inspection
results or evidence-backed system behavior.

## 6. Pipeline Behaviour

Pipeline execution is deterministic. It uses no randomness, wall-clock state,
network access, AI calls, or live data.

The pipeline:

- discovers matching source images in sorted filename order;
- validates that each source is a readable PNG;
- derives a clean base asset from the largest foreground object;
- applies configurable synthetic overlays;
- derives localization and thumbnail crops from configured coordinates;
- writes outputs only under `assets/parts/generated/`;
- removes legacy root-level generated files for the configured output names;
- reopens generated PNGs and validates their dimensions.

Generation is non-destructive. Source images and prototype files are not mutated.

## 7. Validation

The generation script validates every output set after writing it. Validation
fails if:

- no matching source image exists;
- a source image is missing, unreadable, or not a PNG;
- generated folders are missing;
- unexpected visible files appear in a generated output folder;
- any expected generated PNG is missing;
- any generated PNG cannot be decoded;
- any generated PNG has the wrong dimensions;
- the source image set or source hashes change during generation.

The focused test suite in `tests/test_asset_pipeline.py` verifies:

- multiple master images are discovered;
- source images are preserved;
- every generated file exists with exact PNG dimensions;
- thumbnail dimensions remain exact;
- repeated execution is deterministic by comparing generated file hashes;
- writes are confined to generated part assets.

Expected validation commands:

```bash
python3 tools/generate_kalibra_part_assets.py
python3 tools/generate_kalibra_part_assets.py --check
python3 -m pytest tests/test_asset_pipeline.py
python3 -m compileall -q tools tests
git status --short
```

## 8. Configuration

Visual refinement is controlled through named constants in
`tools/generate_kalibra_part_assets.py`.

Tunable parameters include:

- anomaly position;
- source-specific anomaly position overrides;
- overlay opacity and alpha balance;
- overlay feathering;
- contour width and dash pattern;
- localization crop size;
- source-specific localization crop overrides;
- thumbnail crop and overlay positions.

Refinement should happen through parameter tuning before any architectural
change. Pipeline architecture, output paths, filenames, dimensions, and prototype
code should remain stable unless the documented asset pipeline contract itself
changes.

## 9. Engineering Principles

The asset pipeline follows these project conventions:

- master images in `assets/parts/source/` are immutable;
- prototype-facing assets are generated, not manually edited;
- generated outputs are the single source of truth for prototype asset files;
- reproducibility is required before visual claims are made;
- synthetic overlays must remain distinct from inspection evidence;
- engineering readability takes priority over artistic appearance;
- overlays should sit on meaningful engineered geometry;
- localization crops should retain useful mechanical context while keeping the
  anomaly centered;
- thumbnails should remain visually consistent with the same inspection setup.

## 10. Future Extensions

Future work may add a reproducibility manifest, additional master images, or new
industrial component families. These are not current pipeline outputs or system
capabilities unless implemented and validated.

Any future extension must preserve deterministic offline generation, source
immutability, exact output validation, and separation from prototype UI files,
inspection logic, trust qualification, human review, evidence, and evaluation.
