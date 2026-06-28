# Kalibra Inspection Engine Real Image Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Where this plan reaches a commit
> point, it instead defines a **validation checkpoint**: run the listed commands,
> report results, and let the repository owner commit. Do not commit.

**Goal:** Add a first deterministic, local, non-ML image-analysis examiner to the
Inspection Engine that inspects a fixed grayscale image artifact and emits a raw
defect judgement, a localization when defective, a raw anomaly measure, and an
inspection evidence record — without changing any downstream substrate, the
integration layer, or the CLI.

**Architecture:** The Inspection Engine already accepts a pluggable
`InspectionExaminer` (default `DeterministicPlaceholderExaminer`). This plan adds
a second, opt-in examiner — `DeterministicImageBaselineExaminer` — that reads a
local grayscale Netpbm **PGM (P2 ASCII)** artifact, computes deterministic
pixel statistics, derives a raw judgement / raw anomaly measure / localization
by rule-based local-contrast analysis, and returns the same canonical
examination contract the engine already consumes. Small additive,
downstream-compatible relaxations inside `src/inspection/` let the examination
honestly label its own kind and raw-measure scale.

**Tech Stack:** Existing Python 3.9 `dataclasses` substrate under `src/`, Python
standard library only (`pathlib`, `urllib.parse`, `hashlib`, `json`). **No new
dependencies. No image/CV library. No ML.** `pytest` for tests under `tests/`.

---

## Interpretation Note (scope boundary)

The task says "do not modify existing substrates." The Inspection Engine is the
**deliberate target** of this upgrade, authorized by the objective and by the
Inspection Engine plan §12 ("Examination internals are replaceable … the chosen
method can be implemented and later replaced without changing the engine's
boundary, as long as the contracts in §8 are honoured"). Therefore:

- **Modifiable (this plan):** `src/inspection/` and `tests/test_inspection_engine.py`,
  plus new test fixtures under `tests/fixtures/inspection/`.
- **Must NOT be modified:** `src/trust/`, `src/review/`, `src/evidence/`,
  `src/evaluation/`, `src/integration/`, `scripts/run_end_to_end_substrate.py`,
  `README.md`, `assets/`, `tools/generate_kalibra_part_assets.py` (asset
  pipeline), and any prototype.

Every change to `src/inspection/` in this plan is **additive and
downstream-compatible**: the public examination contract keeps the same field
shapes and the same `raw_measure_kind` (`"raw_anomaly_measure"`); only the set of
*allowed descriptive labels* (`examination_kind`, `raw_measure_scale`) is widened
by one value, and one optional field with a backward-compatible default is added.

---

## 1. Purpose

Replace the Inspection Engine's reliance on the hash-only placeholder examination
as the *only* available examiner by **supplementing** it with the first real,
local, deterministic image-analysis examiner. The new examiner inspects an actual
local grayscale image artifact and produces:

- a raw defect judgement (`DEFECT` / `OK`);
- a localization (normalized bounding box) **only when defective**;
- a raw, uncalibrated anomaly measure on `[0, 100]`;
- an inspection evidence record (via the existing, in-memory evidence emitter).

This is a **substrate baseline**, not a product capability. It exists to prove
that the Inspection Engine boundary can carry a real local analysis method
through its existing contracts and seams, with everything downstream unchanged.

**Explicit non-claims (must be stated in code/docstrings and honored):**

- **No ML.** No learning of any kind.
- **No training.** No fit step, no data-derived parameters.
- **No learned weights.** All thresholds are fixed, hand-chosen structural
  constants, not tuned or learned.
- **No benchmark claim.** No accuracy, precision, recall, or quality number is
  produced or asserted.
- **No production CV claim.** A single, minimal, rule-based grayscale contrast
  pass on one local file format is not production computer vision.

## 2. Why Inspection First

The five domains are implemented in fixed order (Domain Plans Index §3), and
Inspection is the **source** of the raw substrate every downstream domain reuses.
Upgrading Inspection first is the only point where a "real" behavior can be
introduced without any downstream domain having to change:

- Trust Qualification consumes a `RawInspectionResult` and reuses its raw measure;
  it does not care *how* that measure was produced, only that it is raw and
  carries `raw_measure_kind == "raw_anomaly_measure"`.
- Human Review, Evidence, and Evaluation consume artifacts further downstream and
  never read the examiner internals.

So a real examiner that keeps the `RawInspectionResult` contract intact is a
strictly local change with zero downstream blast radius — exactly the "examination
internals are replaceable" extension point named in the Inspection plan §12. Doing
Inspection first also keeps the dependency chain honest: no later domain is asked
to depend on a capability that does not yet exist.

## 3. Boundary Preservation

The Inspection Engine must still honor every obligation from
`docs/KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md`. This plan preserves
them as follows:

- **Consumes only stabilized inspection input.** The new examiner is invoked by
  the unchanged `InspectionEngine.inspect`, which already enforces
  `isinstance(inspection_input, StabilizedInspectionInput)`. The examiner reads
  only `inspection_input.artifact_uri` (the stable reference produced by intake)
  and treats it as immutable.
- **Does not perform Input Intake.** Reading the already-stabilized artifact at
  its authoritative `artifact_uri` is **examination (stage 2)**, not intake. The
  examiner does not normalize, re-encode, re-hash, or rewrite the artifact, and
  does not accept raw/unstabilized material; it only reads the reference intake
  produced.
- **Does not calibrate confidence.** The output is a raw measure on a raw scale,
  explicitly labelled raw. No `[0,1]` confidence, no calibration, no mapping to
  certainty. Calibration remains the Trust Qualification Engine's job.
- **Does not qualify trust / route to review / evaluate / persist.** The examiner
  returns only an examination; the engine assembles a `RawInspectionResult` and
  emits an **in-memory** `InspectionEvidenceRecord` via the existing emitter. No
  qualified outcome, no routing, no metrics, no storage.
- **Raw judgement vs calibration.** Thresholding the raw measure into a raw
  `DEFECT`/`OK` judgement is the engine's own Requirement F2 responsibility (the
  existing placeholder already thresholds at `50.0`). It is a *raw structural
  judgement*, not calibrated confidence; the raw measure itself is carried
  downstream unchanged for Trust to calibrate.

**Downstream-compatibility guarantee.** The examiner returns the existing
examination type and the engine assembles the existing `RawInspectionResult`
type. The only contract widenings are: (a) one extra allowed value for the
descriptive `examination_kind`, (b) one extra allowed value for the descriptive
`raw_measure_scale`, and (c) one optional `raw_measure_scale` field on the
examination with a default equal to the current placeholder scale. The
`raw_measure_kind` stays exactly `"raw_anomaly_measure"`, which is the only field
any downstream domain inspects (`src/trust/domain.py:validate_raw_inspection_result`
checks `raw_measure_kind`, never the scale or examination kind).

## 4. Input Assumptions

The examiner consumes the existing `StabilizedInspectionInput`
(`src/inspection/domain.py`). Relevant fields:

- `artifact_uri: str` — the stable artifact reference. Supported forms for the
  baseline:
  - a bare local filesystem path (e.g. `tests/fixtures/inspection/blob_defect.pgm`
    or `/abs/path/img.pgm`);
  - a `file://` URI (e.g. `file:///abs/path/img.pgm`).
  - **Any other scheme** (e.g. the integration default `artifact://…`, or
    `http(s)://`) is **rejected** as an explicit examination failure. The baseline
    performs **no network access**.
- `content_hash: str` — treated as an opaque, authoritative integrity token
  produced by intake. The baseline **does not** recompute or verify it (the hash
  algorithm is not fixed by contract); the artifact is trusted as the stable
  reference. (Optional hash verification is named in §11 as deferred.)
- `input_id`, `input_kind`, `intake_status`, `metadata` — unchanged; validated by
  the existing `StabilizedInspectionInput.__post_init__`.

**Image format assumption.** The baseline reads **grayscale Netpbm PGM, P2 (ASCII)
only**. This is chosen because it is parseable in pure Python with zero
dependencies and is fully deterministic. Binary PGM (P5), PNG, JPEG, and color
are **out of scope** (§11) and are rejected explicitly. Pixel values are integers
in `[0, maxval]`.

## 5. Proposed Deterministic Image Baseline

A new examiner class `DeterministicImageBaselineExaminer` is added to
`src/inspection/engine.py`. It implements the existing `InspectionExaminer`
protocol (`examine(self, inspection_input) -> PlaceholderExamination`) and is
**opt-in**: callers select it via `InspectionEngine(examiner=DeterministicImageBaselineExaminer())`.
The default `InspectionEngine` examiner stays `DeterministicPlaceholderExaminer`
(see §10 for why this keeps the integration chain green).

**Deterministic analysis algorithm (rule-based, fixed constants):**

1. **Resolve** `artifact_uri` to a local `Path` (bare path or `file://`); reject
   other schemes with `InspectionExaminationFailure`.
2. **Read** the PGM (P2) file into a 2-D integer grid `pixels[h][w]` and `maxval`;
   reject malformed/truncated/empty data with `InspectionExaminationFailure`.
3. **Normalize** each pixel: `v[y][x] = pixels[y][x] / maxval` in `[0, 1]`.
4. **Global mean** `mu = mean(v)`.
5. **Per-pixel deviation** `dev[y][x] = abs(v[y][x] - mu)`; track `max_dev`.
6. **Raw anomaly measure** `raw = round(max_dev * 100.0, 6)` (range `[0, 100]`).
7. **Raw judgement:** `DEFECT` if `raw >= defect_threshold` (fixed `50.0`), else
   `OK`.
8. **Localization (DEFECT only):** bounding box of all pixels with
   `dev >= anomaly_fraction * max_dev` (fixed `anomaly_fraction = 0.5`),
   normalized by width/height; `OK` results carry no localization.
9. **Examination id:** a stable id derived from a digest of the pixel grid plus
   `examiner_id` and `input_id`, so identical images yield identical ids and
   different images yield different ids.

All arithmetic is pure-Python integer/float math with fixed rounding, so the
output is bit-for-bit reproducible for a fixed file. The examiner is a frozen
dataclass with fixed fields `examiner_id`, `defect_threshold = 50.0`,
`anomaly_fraction = 0.5` — these are **structural constants, not learned or tuned
parameters**.

**Reference implementation** (added to `src/inspection/engine.py`; see §12 for the
test-first build order):

```python
from pathlib import Path
from urllib.parse import unquote, urlparse

from .domain import (
    IMAGE_BASELINE_EXAMINATION_KIND,
    IMAGE_BASELINE_RAW_SCALE,
)


@dataclass(frozen=True)
class DeterministicImageBaselineExaminer:
    examiner_id: str = "inspection-image-baseline-pgm-v1"
    defect_threshold: float = 50.0
    anomaly_fraction: float = 0.5

    def examine(
        self, inspection_input: StabilizedInspectionInput
    ) -> PlaceholderExamination:
        path = _resolve_local_artifact_path(inspection_input.artifact_uri)
        if not path.exists() or not path.is_file():
            raise InspectionExaminationFailure(
                f"inspection artifact is missing or unreadable: {path}"
            )
        pixels, maxval = _read_pgm_p2(path)
        height = len(pixels)
        width = len(pixels[0])

        normalized_mean = sum(sum(row) for row in pixels) / (
            width * height * maxval
        )
        deviations = [
            [abs(value / maxval - normalized_mean) for value in row]
            for row in pixels
        ]
        max_dev = max(max(row) for row in deviations)
        raw_measure = round(max_dev * 100.0, 6)

        judgement = (
            InspectionJudgement.DEFECT
            if raw_measure >= self.defect_threshold
            else InspectionJudgement.OK
        )
        localization = None
        if judgement is InspectionJudgement.DEFECT:
            localization = _localization_from_deviations(
                deviations, max_dev, self.anomaly_fraction, width, height
            )

        return PlaceholderExamination(
            input_id=inspection_input.input_id,
            examination_id=_stable_id(
                "image-baseline-examination",
                {
                    "examiner_id": self.examiner_id,
                    "input_id": inspection_input.input_id,
                    "pixels": pixels,
                    "maxval": maxval,
                },
            ),
            judgement=judgement,
            raw_anomaly_measure=raw_measure,
            localization=localization,
            examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
            raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
        )


def _resolve_local_artifact_path(artifact_uri: str) -> Path:
    parsed = urlparse(artifact_uri)
    if parsed.scheme == "":
        return Path(artifact_uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    raise InspectionExaminationFailure(
        "image baseline only reads local file artifacts, "
        f"not '{parsed.scheme}://' references"
    )


def _read_pgm_p2(path: Path) -> tuple[list[list[int]], int]:
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise InspectionExaminationFailure(
            f"inspection artifact could not be read as ascii PGM: {path}"
        ) from exc
    tokens = _pgm_tokens(text)
    try:
        magic = next(tokens)
        if magic != "P2":
            raise InspectionExaminationFailure(
                "image baseline supports only ascii PGM (P2) artifacts"
            )
        width = int(next(tokens))
        height = int(next(tokens))
        maxval = int(next(tokens))
    except StopIteration as exc:
        raise InspectionExaminationFailure("PGM header is incomplete") from exc
    except ValueError as exc:
        raise InspectionExaminationFailure("PGM header is not numeric") from exc
    if width <= 0 or height <= 0 or maxval <= 0:
        raise InspectionExaminationFailure(
            "PGM width, height and maxval must be positive"
        )
    pixels: list[list[int]] = []
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            try:
                value = int(next(tokens))
            except StopIteration as exc:
                raise InspectionExaminationFailure(
                    "PGM pixel data is truncated"
                ) from exc
            except ValueError as exc:
                raise InspectionExaminationFailure(
                    "PGM pixel data is not numeric"
                ) from exc
            if value < 0 or value > maxval:
                raise InspectionExaminationFailure(
                    "PGM pixel value is out of range"
                )
            row.append(value)
        pixels.append(row)
    return pixels, maxval


def _pgm_tokens(text: str):
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0]
        for token in line.split():
            yield token


def _localization_from_deviations(
    deviations: list[list[float]],
    max_dev: float,
    anomaly_fraction: float,
    width: int,
    height: int,
) -> DefectLocalization:
    threshold = anomaly_fraction * max_dev
    cols = [
        x
        for y in range(height)
        for x in range(width)
        if deviations[y][x] >= threshold
    ]
    rows = [
        y
        for y in range(height)
        for x in range(width)
        if deviations[y][x] >= threshold
    ]
    x_min = round(min(cols) / width, 6)
    x_max = round((max(cols) + 1) / width, 6)
    y_min = round(min(rows) / height, 6)
    y_max = round((max(rows) + 1) / height, 6)
    return DefectLocalization(
        region=NormalizedBoundingBox(
            x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max
        ),
        localization_kind="local_contrast_suspected_region",
    )
```

> Note: `_stable_id`, `_digest`, `InspectionJudgement`, `PlaceholderExamination`,
> `DefectLocalization`, `NormalizedBoundingBox`, `InspectionExaminationFailure`,
> and `StabilizedInspectionInput` already exist in `src/inspection/engine.py` /
> `src/inspection/domain.py`. `_stable_id` already JSON-serializes its payload
> with `sort_keys=True`; nested lists (the pixel grid) serialize deterministically.

## 6. Raw Anomaly Measure Definition

- **Definition:** `raw = round(max_pixel_deviation_from_global_mean * 100.0, 6)`,
  where each pixel's deviation is `abs(pixel/maxval - global_mean)` and
  `global_mean` is the normalized mean intensity. The measure is the **peak local
  contrast against the image's own mean**, expressed on a raw `[0, 100]` span.
- **It is raw and uncalibrated.** It is not a probability, not a confidence, not
  bounded to a calibrated `[0, 1]` certainty, and is not compared to any reference
  set or learned distribution. It carries:
  - `raw_measure_kind == "raw_anomaly_measure"` (unchanged generic kind read by
    Trust);
  - `raw_measure_scale == IMAGE_BASELINE_RAW_SCALE` =
    `"local_contrast_raw_0_100"` (new, **honest** label distinguishing it from the
    placeholder's `"placeholder_hash_raw_0_100"`).
- **Why a new scale label:** the Evidence Engine preserves and the Evaluation
  Engine reads these labels; leaving the real measure tagged
  `"placeholder_hash_raw_0_100"` would misrepresent its provenance, violating the
  "rawness is explicit / self-describing" contract invariant (Inspection plan §8)
  and AGENTS.md "honesty over capability." The new label is additive and read by
  no downstream validator.
- **Raw judgement boundary:** `DEFECT` iff `raw >= 50.0`. The `50.0` boundary is a
  fixed structural constant (matching the existing placeholder boundary so
  downstream behavior is consistent); it is **not** a calibrated or learned
  decision threshold. Trust Qualification remains solely responsible for turning
  the raw measure into calibrated confidence.

## 7. Localization Strategy

- **Produced only for `DEFECT`** results (the `OK` branch returns `None`). This is
  also enforced structurally by `PlaceholderExamination.__post_init__` and
  `RawInspectionResult.__post_init__`, which already raise
  `PartialInspectionResult` if a `DEFECT` lacks localization or an `OK` carries
  one.
- **Region derivation:** the normalized bounding box of every pixel whose
  deviation is at least `anomaly_fraction (0.5) * max_dev`. Pixel indices are
  converted to normalized coordinates:
  `x_min = min_col / width`, `x_max = (max_col + 1) / width`,
  `y_min = min_row / height`, `y_max = (max_row + 1) / height`, each
  `round(_, 6)`.
- **Validity:** `(max_col + 1) > min_col` and `(max_row + 1) > min_row` always
  hold (the peak pixel always qualifies), so `x_min < x_max` and `y_min < y_max`,
  and `x_max, y_max <= 1.0`. This satisfies `NormalizedBoundingBox.__post_init__`
  (finite, normalized, min < max).
- **Kind label:** `localization_kind == "local_contrast_suspected_region"`
  (honest; `DefectLocalization.localization_kind` has no fixed-value validation,
  only non-blank, so this needs no domain change).
- **No semantic claim:** the box marks where the deterministic contrast peak lies;
  it is not asserted to be a true defect. Measuring localization correctness is
  the Evaluation Engine's job and is out of scope here.

## 8. Failure Modes

All failures are surfaced as `InspectionExaminationFailure` (an `InspectionError`
subclass), which the engine's `_examine` already re-raises cleanly. None is ever
silently converted into a verdict, and none is disguised as a confident result.

| Failure | Trigger | Handling |
| --- | --- | --- |
| Non-local URI scheme | `artifact://…`, `http(s)://…`, etc. | `InspectionExaminationFailure` ("only local file artifacts") |
| Missing / non-file artifact | path does not exist or is a directory | `InspectionExaminationFailure` ("missing or unreadable") |
| Unreadable / non-ASCII bytes | `OSError` / `UnicodeDecodeError` on read | `InspectionExaminationFailure` |
| Wrong magic / unsupported format | first token ≠ `P2` (incl. `P5`, PNG, JPEG) | `InspectionExaminationFailure` ("only ascii PGM (P2)") |
| Incomplete / non-numeric header | header tokens missing or not ints | `InspectionExaminationFailure` |
| Non-positive dimensions/maxval | `width<=0`, `height<=0`, `maxval<=0` | `InspectionExaminationFailure` |
| Truncated / non-numeric / out-of-range pixels | too few tokens, non-int, or `> maxval` | `InspectionExaminationFailure` |

Inherited from the unchanged engine:

- **Partial result:** a `DEFECT` without localization (or `OK` with localization)
  raises `PartialInspectionResult` — structurally impossible for this examiner but
  retained as a guard.
- **Non-reproducibility:** the engine already runs the examination twice per
  `inspect()` and raises `NonReproducibleInspection` on divergence. The baseline
  is deterministic for a fixed file; if the file changes between the two reads in
  one call, that divergence is correctly surfaced as a defect, not tolerated.

The examiner never repairs, guesses, or substitutes data for a failed read.

## 9. Tests

All tests are **additive** in `tests/test_inspection_engine.py` (the existing 20
placeholder tests must keep passing unchanged). Fixtures live under a new
`tests/fixtures/inspection/` directory. Tests assert **boundary and contract**
behavior (judgement, localization presence, raw labels, determinism, explicit
failure), **not** detection accuracy — consistent with the Inspection plan §11.

Planned coverage (mapped to the task's testing requirements):

1. **Valid local image → raw inspection result.** `blob_defect.pgm` through
   `InspectionEngine(examiner=DeterministicImageBaselineExaminer())` yields an
   `InspectionEngineOutput` whose `raw_inspection_result` references the input.
2. **Raw anomaly measure remains raw.** Result has
   `raw_measure_kind == "raw_anomaly_measure"`, `raw_measure_scale ==
   "local_contrast_raw_0_100"`, `0.0 <= raw_anomaly_measure <= 100.0`, and **no**
   `confidence` / `calibrated_confidence` attribute.
3. **Localization only for defective result.** `blob_defect.pgm` → `DEFECT` with a
   `NormalizedBoundingBox`; `uniform_ok.pgm` → `OK` with `localization is None`.
4. **Same image → identical output.** Two `inspect()` runs on the same fixture
   produce equal `raw_inspection_result` and equal `inspection_evidence_record`.
5. **Missing / unreadable image fails explicitly.** A non-existent path, a
   non-local `artifact://` URI, and a malformed PGM each raise
   `InspectionExaminationFailure`.
6. **No calibrated confidence exposed.** Result/examination expose no confidence
   field; downstream-field disjointness already covered by the existing
   `test_raw_result_contains_no_downstream_domain_fields`.
7. **Integration chain still passes.** `tests/test_end_to_end_substrate_integration.py`
   runs **unchanged** (default examiner is still the placeholder; the
   `artifact://` integration fixture is untouched).
8. **Repo-wide tests still pass.** Full `pytest -q` stays green.

## 10. Integration Impact

- **None to the integration layer or CLI.** `EndToEndSubstrateIntegrationEngine`
  constructs `InspectionEngine()` with its default examiner. The default stays
  `DeterministicPlaceholderExaminer`, so the integration default fixture
  (`artifact://kalibra/integration/input-000.png`, a non-local pseudo-URI) keeps
  producing the same placeholder result. `scripts/run_end_to_end_substrate.py`
  and `src/integration/` are **not modified**.
- **Why not switch the default examiner:** the integration/CLI fixtures use a
  non-local `artifact://…` reference. The real examiner correctly *rejects*
  non-local schemes (§8), so making it the default would break the integration
  chain and the CLI. Keeping it opt-in satisfies both "add real behavior" and
  "integration chain still passes." Any future switch of the default (e.g. once a
  local artifact fixture exists for integration) is a separate owner-approved
  scope.
- **Downstream substrates unchanged.** Trust/Review/Evidence/Evaluation read only
  `raw_measure_kind` and generic payload fields; the new `examination_kind` and
  `raw_measure_scale` label values flow through Evidence/Evaluation as opaque
  preserved strings. A new optional opt-in path (constructing `InspectionEngine`
  with the baseline examiner) is available to callers but exercised here only by
  the inspection tests.
- **Public surface (additive):** `src/inspection/__init__.py` exports the new
  `DeterministicImageBaselineExaminer`, `IMAGE_BASELINE_EXAMINATION_KIND`, and
  `IMAGE_BASELINE_RAW_SCALE`. Nothing is removed or renamed.

## 11. Out of Scope

This plan does **not** authorize, and the implementation must not introduce:

- machine learning, training, retraining, learned/tuned weights, or any
  data-derived parameter;
- computer-vision libraries or any new third-party dependency (no Pillow,
  NumPy, OpenCV, etc.);
- formats beyond grayscale PGM P2 (binary PGM/P5, PNM color, PNG, JPEG, TIFF are
  deferred);
- confidence calibration, trust qualification, abstention, drift, review routing,
  or evaluation/metrics of any kind;
- evidence persistence, databases, UI, or evidence presentation;
- accuracy, precision/recall, benchmark, or any performance/quality claim;
- changes to `README.md`, prototype, `assets/`, the asset pipeline
  (`tools/generate_kalibra_part_assets.py`), the integration layer, or the CLI;
- changing the **default** `InspectionEngine` examiner;
- `content_hash` verification against the artifact (integrity check is a
  reasonable future addition but is deferred — the hash algorithm is not fixed by
  contract);
- live, streaming, scheduled, hosted, or continuously operating behavior;
- network/URL fetching of artifacts.

## 12. Implementation Steps

> Each task is test-first (TDD). After each task, run the listed command and
> confirm the expected result. Commit points are **owner validation checkpoints**:
> report results and let the repository owner commit. Do not run git yourself.

### Task 1: Add honest examination labels to the inspection domain

**Files:**
- Modify: `src/inspection/domain.py`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_inspection_engine.py`)

```python
from src.inspection import (
    IMAGE_BASELINE_EXAMINATION_KIND,
    IMAGE_BASELINE_RAW_SCALE,
)


def test_image_baseline_labels_are_accepted_by_contracts():
    examination = PlaceholderExamination(
        input_id="input-baseline",
        examination_id="exam-baseline",
        judgement=InspectionJudgement.OK,
        raw_anomaly_measure=12.5,
        localization=None,
        examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
        raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
    )
    assert examination.raw_measure_scale == "local_contrast_raw_0_100"

    result = RawInspectionResult(
        inspection_result_id="result-baseline",
        input_id="input-baseline",
        judgement=InspectionJudgement.OK,
        localization=None,
        raw_anomaly_measure=12.5,
        examination_id="exam-baseline",
        examination_kind=IMAGE_BASELINE_EXAMINATION_KIND,
        raw_measure_scale=IMAGE_BASELINE_RAW_SCALE,
    )
    assert result.examination_kind == "deterministic_local_image_baseline_v1"
    assert result.raw_measure_kind == "raw_anomaly_measure"
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python3 -m pytest tests/test_inspection_engine.py::test_image_baseline_labels_are_accepted_by_contracts -q`
Expected: FAIL with `ImportError`/`AttributeError` (new constants and the
`PlaceholderExamination.raw_measure_scale` field do not exist yet).

- [ ] **Step 3: Add constants and widen validation in `src/inspection/domain.py`**

Add the constants near the existing kind constants (after
`INSPECTION_EVIDENCE_KIND`):

```python
IMAGE_BASELINE_EXAMINATION_KIND = "deterministic_local_image_baseline_v1"
IMAGE_BASELINE_RAW_SCALE = "local_contrast_raw_0_100"

VALID_EXAMINATION_KINDS = frozenset(
    {PLACEHOLDER_EXAMINATION_KIND, IMAGE_BASELINE_EXAMINATION_KIND}
)
VALID_RAW_MEASURE_SCALES = frozenset(
    {RAW_MEASURE_SCALE, IMAGE_BASELINE_RAW_SCALE}
)
```

Add a `raw_measure_scale` field to `PlaceholderExamination` (default keeps current
behavior) and validate the kind/scale against the sets. In
`PlaceholderExamination`:

```python
@dataclass(frozen=True)
class PlaceholderExamination:
    input_id: str
    examination_id: str
    judgement: InspectionJudgement
    raw_anomaly_measure: float
    localization: DefectLocalization | None
    examination_kind: str = PLACEHOLDER_EXAMINATION_KIND
    raw_measure_scale: str = RAW_MEASURE_SCALE
```

Replace the `examination_kind` equality check in
`PlaceholderExamination.__post_init__`:

```python
        if self.examination_kind not in VALID_EXAMINATION_KINDS:
            raise InvalidInspectionResult(
                "inspection examination kind must remain explicit"
            )
        if self.raw_measure_scale not in VALID_RAW_MEASURE_SCALES:
            raise InvalidInspectionResult("raw anomaly measure scale is required")
```

In `RawInspectionResult.__post_init__`, replace the two equality checks:

```python
        if self.raw_measure_scale not in VALID_RAW_MEASURE_SCALES:
            raise InvalidInspectionResult("raw anomaly measure scale is required")
        ...
        if self.examination_kind not in VALID_EXAMINATION_KINDS:
            raise InvalidInspectionResult(
                "placeholder examination kind must be explicit"
            )
```

Export the new constants from `src/inspection/__init__.py` (add to the imports
from `.domain` and to `__all__`):

```python
from .domain import (
    IMAGE_BASELINE_EXAMINATION_KIND,
    IMAGE_BASELINE_RAW_SCALE,
    ...
)
# add "IMAGE_BASELINE_EXAMINATION_KIND" and "IMAGE_BASELINE_RAW_SCALE" to __all__
```

- [ ] **Step 4: Run the test and the full inspection suite**

Run: `python3 -m pytest tests/test_inspection_engine.py -q`
Expected: PASS (the new test passes; all pre-existing placeholder tests still
pass — the defaults are unchanged so the placeholder path is unaffected).

- [ ] **Step 5: Validation checkpoint** — report results to the owner; do not
  commit.

### Task 2: Add the PGM reader and URI resolver

**Files:**
- Modify: `src/inspection/engine.py`
- Create: `tests/fixtures/inspection/uniform_ok.pgm`
- Create: `tests/fixtures/inspection/blob_defect.pgm`
- Create: `tests/fixtures/inspection/bad_magic.pgm`
- Create: `tests/fixtures/inspection/truncated.pgm`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1: Create the fixtures**

`tests/fixtures/inspection/uniform_ok.pgm`:

```
P2
4 4
255
120 120 120 120
120 120 120 120
120 120 120 120
120 120 120 120
```

`tests/fixtures/inspection/blob_defect.pgm`:

```
P2
4 4
255
0 0 0 0
0 255 255 0
0 255 255 0
0 0 0 0
```

`tests/fixtures/inspection/bad_magic.pgm`:

```
P5
1 1
255
0
```

`tests/fixtures/inspection/truncated.pgm`:

```
P2
4 4
255
0 0
```

- [ ] **Step 2: Write failing tests for the reader/resolver**

```python
from pathlib import Path

from src.inspection import InspectionExaminationFailure
from src.inspection.engine import _read_pgm_p2, _resolve_local_artifact_path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "inspection"


def test_pgm_reader_parses_grid_and_maxval():
    pixels, maxval = _read_pgm_p2(FIXTURES / "blob_defect.pgm")
    assert maxval == 255
    assert pixels == [
        [0, 0, 0, 0],
        [0, 255, 255, 0],
        [0, 255, 255, 0],
        [0, 0, 0, 0],
    ]


def test_pgm_reader_rejects_non_p2_and_truncated():
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(FIXTURES / "bad_magic.pgm")
    with pytest.raises(InspectionExaminationFailure):
        _read_pgm_p2(FIXTURES / "truncated.pgm")


def test_resolver_rejects_non_local_scheme():
    assert _resolve_local_artifact_path("part.pgm") == Path("part.pgm")
    assert _resolve_local_artifact_path("file:///tmp/x.pgm") == Path("/tmp/x.pgm")
    with pytest.raises(InspectionExaminationFailure):
        _resolve_local_artifact_path("artifact://kalibra/x.png")
```

- [ ] **Step 3: Run to confirm failure**

Run: `python3 -m pytest tests/test_inspection_engine.py -k "pgm_reader or resolver" -q`
Expected: FAIL with `ImportError` (`_read_pgm_p2` / `_resolve_local_artifact_path`
not defined).

- [ ] **Step 4: Add the reader/resolver helpers to `src/inspection/engine.py`**

Add the `from pathlib import Path` and `from urllib.parse import unquote, urlparse`
imports at the top, and the `_resolve_local_artifact_path`, `_read_pgm_p2`, and
`_pgm_tokens` functions exactly as given in §5.

- [ ] **Step 5: Run the reader/resolver tests**

Run: `python3 -m pytest tests/test_inspection_engine.py -k "pgm_reader or resolver" -q`
Expected: PASS.

- [ ] **Step 6: Validation checkpoint** — report results; do not commit.

### Task 3: Add the `DeterministicImageBaselineExaminer`

**Files:**
- Modify: `src/inspection/engine.py`
- Modify: `src/inspection/__init__.py`
- Test: `tests/test_inspection_engine.py`

- [ ] **Step 1: Write the failing behavior tests**

```python
from src.inspection import DeterministicImageBaselineExaminer, InspectionEngine


def _baseline_engine() -> InspectionEngine:
    return InspectionEngine(examiner=DeterministicImageBaselineExaminer())


def _baseline_input(filename: str) -> StabilizedInspectionInput:
    return StabilizedInspectionInput(
        input_id=f"baseline-{filename}",
        artifact_uri=str(FIXTURES / filename),
        content_hash=f"content-hash-{filename}",
    )


def test_baseline_defect_image_produces_localized_raw_result():
    output = _baseline_engine().inspect(_baseline_input("blob_defect.pgm"))
    result = output.raw_inspection_result

    assert result.judgement is InspectionJudgement.DEFECT
    assert result.raw_measure_kind == "raw_anomaly_measure"
    assert result.raw_measure_scale == "local_contrast_raw_0_100"
    assert 0.0 <= result.raw_anomaly_measure <= 100.0
    assert result.localization is not None
    assert result.localization.region == NormalizedBoundingBox(
        x_min=0.25, y_min=0.25, x_max=0.75, y_max=0.75
    )
    assert not hasattr(result, "confidence")
    assert not hasattr(result, "calibrated_confidence")


def test_baseline_uniform_image_is_ok_without_localization():
    output = _baseline_engine().inspect(_baseline_input("uniform_ok.pgm"))
    result = output.raw_inspection_result

    assert result.judgement is InspectionJudgement.OK
    assert result.localization is None
    assert result.raw_anomaly_measure == 0.0


def test_baseline_same_image_is_reproducible():
    engine = _baseline_engine()
    inspection_input = _baseline_input("blob_defect.pgm")
    first = engine.inspect(inspection_input)
    second = engine.inspect(inspection_input)
    assert first.raw_inspection_result == second.raw_inspection_result
    assert first.inspection_evidence_record == second.inspection_evidence_record


def test_baseline_missing_or_non_local_artifact_fails_explicitly():
    missing = StabilizedInspectionInput(
        input_id="baseline-missing",
        artifact_uri=str(FIXTURES / "does_not_exist.pgm"),
        content_hash="content-hash-missing",
    )
    with pytest.raises(InspectionExaminationFailure):
        _baseline_engine().inspect(missing)

    non_local = StabilizedInspectionInput(
        input_id="baseline-non-local",
        artifact_uri="artifact://kalibra/integration/input-000.png",
        content_hash="content-hash-non-local",
    )
    with pytest.raises(InspectionExaminationFailure):
        _baseline_engine().inspect(non_local)
```

- [ ] **Step 2: Run to confirm failure**

Run: `python3 -m pytest tests/test_inspection_engine.py -k baseline -q`
Expected: FAIL with `ImportError` (`DeterministicImageBaselineExaminer` not
defined).

- [ ] **Step 3: Add the examiner and localization helper**

Add `DeterministicImageBaselineExaminer` and `_localization_from_deviations` to
`src/inspection/engine.py` exactly as given in §5 (the examiner imports
`IMAGE_BASELINE_EXAMINATION_KIND` and `IMAGE_BASELINE_RAW_SCALE` from `.domain`).

Export from `src/inspection/__init__.py` (add to the imports from `.engine` and to
`__all__`):

```python
from .engine import (
    DeterministicImageBaselineExaminer,
    DeterministicPlaceholderExaminer,
    InspectionEngine,
    InspectionEvidenceEmitter,
)
# add "DeterministicImageBaselineExaminer" to __all__
```

- [ ] **Step 4: Run the baseline tests**

Run: `python3 -m pytest tests/test_inspection_engine.py -k baseline -q`
Expected: PASS (5 baseline tests).

- [ ] **Step 5: Validation checkpoint** — report results; do not commit.

### Task 4: Full verification

- [ ] **Step 1: Inspection suite**

Run: `python3 -m pytest tests/test_inspection_engine.py -q`
Expected: PASS (existing 20 + new tests).

- [ ] **Step 2: Integration chain unchanged**

Run: `python3 -m pytest tests/test_end_to_end_substrate_integration.py tests/test_integration_cli.py -q`
Expected: PASS (default examiner unchanged; no integration/CLI files modified).

- [ ] **Step 3: Repo-wide suite + compile**

Run: `python3 -m pytest -q`
Expected: PASS (all tests).

Run: `python3 -m compileall -q src tests scripts`
Expected: exit 0.

- [ ] **Step 4: Confirm scope discipline**

Run: `git status --short`
Expected: only `src/inspection/` files, `tests/test_inspection_engine.py`, and new
`tests/fixtures/inspection/` fixtures appear. **No** changes to `src/trust/`,
`src/review/`, `src/evidence/`, `src/evaluation/`, `src/integration/`, `scripts/`,
`README.md`, `assets/`, or `tools/`.

- [ ] **Step 5: Final validation checkpoint** — report all results to the owner;
  the owner commits. Do not commit.

---

## Self-Review

- **Spec coverage:** purpose (§1), why-inspection-first (§2), boundary
  preservation (§3), input assumptions (§4), deterministic baseline (§5), raw
  measure definition (§6), localization (§7), failure modes (§8), tests (§9),
  integration impact (§10), out of scope (§11), implementation steps (§12) — all
  present. Every required test (valid image → result; raw stays raw; localization
  only for defect; reproducible; missing/unreadable fails; no calibrated
  confidence; integration passes; repo-wide passes) maps to a Task in §12.
- **No-ML / no-training / no-weights / no-benchmark / no-production-CV** stated in
  §1 and §11.
- **Type consistency:** `DeterministicImageBaselineExaminer.examine` returns
  `PlaceholderExamination` (the type the engine already consumes via its
  `isinstance` check); new constants `IMAGE_BASELINE_EXAMINATION_KIND` /
  `IMAGE_BASELINE_RAW_SCALE` are defined once in §12 Task 1 and reused
  consistently; helper names (`_read_pgm_p2`, `_pgm_tokens`,
  `_resolve_local_artifact_path`, `_localization_from_deviations`) match between
  §5 and §12.
- **Placeholder scan:** no TBD/TODO; every code step shows complete code and every
  run step shows the exact command and expected result.
