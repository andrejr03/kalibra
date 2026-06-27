# Kalibra Asset Pipeline Implementation Plan

## 1. Purpose

This plan defines a deterministic local pipeline for deriving prototype-ready
part visuals from the clean master inspection image at
`assets/parts/source/master_clean.png`.

The pipeline supports visual prototype work only. Its synthetic overlays are not
inspection results, calibration evidence, model evidence, evaluation evidence, or
proof of defect-detection performance.

## 2. Scope

The first implementation phase must generate exactly these assets:

- `assets/parts/generated/part_clean.png` at `960 x 600`
- `assets/parts/generated/part_main.png` at `960 x 600`
- `assets/parts/generated/part_localization.png` at `520 x 460`

The pipeline must be local, offline, deterministic, non-destructive, and
re-runnable from the same source image.

## 3. Non-goals

This phase must not:

- generate thumbnails;
- modify `master_clean.png`;
- modify prototype files or prototype archives;
- write into `assets/kalibra-prototype/`, `assets/prototypes/`, or the root
  prototype image;
- implement inspection, anomaly detection, calibration, trust qualification,
  human review, evidence recording, or evaluation logic;
- claim that synthetic anomaly visuals represent model performance.

## 4. Folder Structure

The implementation should use this asset layout:

```text
assets/
  parts/
    source/
      master_clean.png
    generated/
      part_clean.png
      part_main.png
      part_localization.png
```

The source folder contains immutable input assets. The generated folder contains
only reproducible outputs from the pipeline.

## 5. Source Asset Rules

`assets/parts/source/master_clean.png` is the immutable input for this phase. The
pipeline must read it without altering its file contents, metadata, path, or
filename.

The implementation must fail clearly if the source image is missing, unreadable,
or not a PNG. It may report the source dimensions and content hash for operator
inspection, but the first phase must not require additional source assets.

## 6. Generated Output Rules

Generated files must be written only under `assets/parts/generated/`.

The implementation should create the generated folder if it does not exist. It
may replace prior generated outputs with newly generated deterministic outputs,
but it must never write outside the generated folder and must never mutate source
or prototype assets.

`part_clean.png` must be a clean resized derivative of the master image.
`part_main.png` must be a clean derivative plus the configured synthetic anomaly
overlay. `part_localization.png` must be a localization-focused derivative using
the same configured anomaly position.

## 7. Overlay Strategy

The overlay is a deterministic prototype visual layered onto the resized or
cropped derivative image. It should be visually clear enough for prototype use
while remaining explicitly synthetic.

The main image overlay should mark the configured anomaly location without
obscuring the surrounding part. The localization image should use the same
configured location, either by cropping around it before resizing or by deriving a
stable localization frame from it.

No overlay output may be described as a detected defect, model localization,
confidence evidence, or evaluation artifact.

## 8. Configurable Anomaly Parameters

The first implementation should keep anomaly controls as named constants near
the top of the generation script.

Required configurable parameters:

- anomaly center position;
- anomaly size or radius;
- configurable overlay palette, such as `ANOMALY_COLORS`;
- overlay opacity, such as `ANOMALY_OPACITY`;
- `OVERLAY_FEATHER_RADIUS`;
- `OVERLAY_CONTOUR_WIDTH`;
- `OVERLAY_CONTOUR_DASH_PATTERN`;
- localization crop size or padding.

The anomaly position must be configurable through constants, not hidden inside
ad hoc drawing code. The overlay should use a configurable colour palette rather
than a single hard-coded colour. Feathering, contour width, and contour dash
settings allow refinement of the prototype visualization without modifying the
source image. The first phase should avoid randomness entirely.

## 9. Dimension Validation Strategy

Every output image must be validated after writing by reopening the generated PNG
and checking its dimensions exactly:

- `part_clean.png`: `960 x 600`
- `part_main.png`: `960 x 600`
- `part_localization.png`: `520 x 460`

Validation must fail with a non-zero exit if any generated output is missing, has
the wrong dimensions, or cannot be decoded as a PNG.

## 10. Reproducibility Requirements

The pipeline must produce the same generated assets from the same
`master_clean.png` and the same constants.

The implementation must avoid hidden state, wall-clock-dependent output,
randomized placement, network access, live data, and writes outside the generated
output folder. Any future dependency used for image processing must be pinned or
otherwise documented by the implementation work that introduces it.

## 11. Implementation Steps

1. Add a small local image-generation entry point at
   `tools/generate_kalibra_part_assets.py`, outside the five Kalibra engine
   domains.
2. Define the source path, generated output path, target dimensions, and anomaly
   parameters as explicit constants.
3. Load `master_clean.png`, validate that it is a readable PNG, and derive a
   clean `960 x 600` base image.
4. Save the clean derivative as `part_clean.png`.
5. Apply the configured synthetic overlay to a copy of the clean derivative and
   save it as `part_main.png`.
6. Derive the localization view from the same source image and configured anomaly
   position, then save it as `part_localization.png`.
7. Reopen all generated outputs and validate exact dimensions.
8. Add focused tests at `tests/test_asset_pipeline.py` that prove source
   immutability, generated output placement, exact dimensions, and the absence of
   thumbnail generation.

## 12. Validation Commands

After implementation, the expected validation flow is:

```bash
python tools/generate_kalibra_part_assets.py
python tools/generate_kalibra_part_assets.py --check
python -m pytest tests/test_asset_pipeline.py
git status --short
```

## 13. Future Extensions

Future work may extend the pipeline to generate thumbnails, support multiple
master images, or write a reproducibility manifest. Those extensions must remain
offline, deterministic, non-destructive, and separate from Kalibra's inspection,
trust qualification, review, evidence, and evaluation domains.

Any extension that changes generated assets, source inputs, or prototype
contracts must update the public documentation before implementation.
