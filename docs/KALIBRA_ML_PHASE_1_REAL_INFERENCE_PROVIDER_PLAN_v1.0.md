# Kalibra ML Phase 1 — First Real Inference Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Where this plan reaches a commit
> point, it instead defines a **validation checkpoint**: run the listed commands,
> report results, and let the repository owner commit. Do not commit.

**Goal:** Add the first *real* `InspectionInferenceProvider` —
`LocalArtifactInferenceProvider` — which reads a local PGM P2 image artifact and
derives an `InspectionPrediction` from the artifact's actual pixel content, using
only the Python standard library and existing Inspection-domain contracts.

**Architecture:** The provider proves the seam
`InspectionInferenceProvider -> InspectionPrediction ->
InspectionEngine.transform_prediction() -> RawInspectionResult` with *real input
content*. It owns only prediction production. It never produces
`RawInspectionResult`, emits evidence, qualifies trust, routes review, evaluates,
persists, calls `InspectionEngine`, or calls `transform_prediction()`. The
existing default `InspectionEngine.inspect()` path is unchanged.

**Tech Stack:** Existing Python 3.9 `dataclasses` substrate under
`src/inspection/`; `hashlib`; the existing local PGM P2 reader logic; `pytest`
for tests. **No new dependency. No PyTorch, ONNX, TensorFlow, CoreML, OpenVINO.
No model, weights, training, or dataset.**

---

## Interpretation Note (scope boundary)

The current repository state is authoritative:

- `InspectionPrediction`, `InvalidInspectionPrediction`, and
  `PartialInspectionPrediction` already exist in `src/inspection/`.
- `InspectionInferenceProvider` already exists as a protocol with only
  `predict(...) -> InspectionPrediction` (`src/inspection/interfaces.py`).
- `InspectionEngine.transform_prediction(...)` already validates and transforms an
  accepted `InspectionPrediction` into the canonical `RawInspectionResult`
  (`src/inspection/engine.py`).
- `DeterministicMockInferenceProvider` already exists and derives a prediction
  from stabilized-input *fields* (not artifact content)
  (`src/inspection/providers.py`).
- The PGM P2 reader (`_read_pgm_p2`, `_resolve_local_artifact_path`,
  `_pgm_tokens`) and the local-contrast derivation (`_localization_from_deviations`
  plus the deviation math inside `DeterministicImageBaselineExaminer.examine`)
  currently live as private helpers in `src/inspection/engine.py` and are used
  only by the image baseline examiner.
- `tests/test_inspection_engine.py` imports `_read_pgm_p2` and
  `_resolve_local_artifact_path` *by name* from `src.inspection.engine`; those
  names must remain resolvable from that module after any extraction.

**Modifiable (this plan):**

- Create `src/inspection/local_artifacts.py` (clean extraction target).
- Create `LocalArtifactInferenceProvider` in `src/inspection/providers.py`.
- Modify `src/inspection/engine.py` to import the extracted helpers and keep its
  existing underscored names as backward-compatible aliases (behavior-preserving).
- Modify `src/inspection/__init__.py` (additive export of the new provider).
- Modify `tests/test_inspection_engine.py` (additive tests).
- Add fixtures under `tests/fixtures/inspection/`.

**Must NOT be modified:** `README.md`, the prototype, `assets/`, the asset
pipeline (`tools/`), `src/integration/`, the CLI, `src/trust/`, `src/review/`,
`src/evidence/`, `src/evaluation/`, `scripts/`. No change to the
`InspectionPrediction` contract, the `InspectionInferenceProvider` protocol, the
`RawInspectionResult` contract, or `transform_prediction()` behavior.

The extraction of the PGM reader and contrast helpers into
`src/inspection/local_artifacts.py` is a **behavior-preserving** refactor inside
the Inspection domain; it moves no responsibility out of Inspection. It exists so
the new provider reuses the existing reader rather than duplicating it (AGENTS.md
Coding Rules: reuse over invention; DRY).

---

## 1. Purpose

`LocalArtifactInferenceProvider` is the first `InspectionInferenceProvider` that is
*real* in a concrete, testable sense: it reads a **local image artifact** and
derives its prediction from the **artifact's actual content**, not from input
identifiers or metadata hashes.

It exists to validate the ML Phase 1 provider seam against real local input
content **before** any external ML framework is introduced. It proves that a
provider can:

- accept a `StabilizedInspectionInput`;
- open the local artifact the input references;
- read real pixel content deterministically;
- derive a valid `InspectionPrediction` from that content;
- return **only** that prediction, which `InspectionEngine.transform_prediction()`
  can later validate and transform.

The provider is **not** a visual-quality claim, a production computer-vision
method, or a learned model. Its derivation is a deterministic local-contrast
heuristic over grayscale pixels. No output produced through this provider may be
documented or presented as production inspection capability, accuracy, or
benchmark.

It complements, and does not replace, `DeterministicMockInferenceProvider`: the
mock proves the seam with no I/O; this provider proves the seam with real local
artifact reads.

## 2. Scope

**In scope:**

- A new module `src/inspection/local_artifacts.py` holding the extracted,
  behavior-preserving local PGM P2 reader and local-contrast derivation helpers,
  shared by the existing image baseline examiner and the new provider.
- A new `LocalArtifactInferenceProvider` in `src/inspection/providers.py`
  implementing the existing `InspectionInferenceProvider` protocol.
- Behavior-preserving refactor of `DeterministicImageBaselineExaminer` and the
  PGM-reader call sites in `src/inspection/engine.py` to consume the extracted
  helpers, keeping the existing underscored names as aliases.
- Additive public export of `LocalArtifactInferenceProvider` through
  `src/inspection/__init__.py`.
- Additive provider tests and fixtures in `tests/`.

**Likely implementation files:**

- Create: `src/inspection/local_artifacts.py`
- Modify: `src/inspection/providers.py`
- Modify: `src/inspection/engine.py`
- Modify: `src/inspection/__init__.py`
- Modify: `tests/test_inspection_engine.py`
- Add: `tests/fixtures/inspection/blob_defect_shifted.pgm`

**Explicitly out of scope (later tasks / forbidden here):**

- Any model, learned weights, training, dataset, hyperparameter, or external ML
  framework (PyTorch, ONNX, TensorFlow, CoreML, OpenVINO).
- Wiring the provider into `InspectionEngine.inspect()` or any integration/CLI
  selection path.
- Any change to the `InspectionPrediction` contract,
  `InspectionInferenceProvider` protocol, `RawInspectionResult`, or
  `transform_prediction()`.
- Any change to README, prototype, assets, asset pipeline, integration, CLI,
  Trust, Review, Evidence, or Evaluation.

## 3. Why the First Real Provider Should Be Local and Stdlib-Only

- **It validates the seam, not a model.** Phase 1's purpose is to prove that real
  input content can flow through `InspectionInferenceProvider ->
  InspectionPrediction -> transform_prediction()` without bending the
  architecture. That requires real local content, not an external runtime.
- **It honours "evidence before assertion" and "honesty over capability"**
  (AGENTS.md). A stdlib local-contrast heuristic makes no detection-quality claim
  it cannot support. An external framework would invite accuracy claims that
  Phase 1 explicitly forbids.
- **It keeps the change reproducible and dependency-free** (AGENTS.md
  Reproducibility; Coding Rules). Reading a fixed local PGM with the standard
  library yields identical output on every machine, with no install, GPU, or
  network state.
- **It reuses proven repository capability.** The repository already reads local
  grayscale PGM P2 artifacts deterministically for `DeterministicImageBaselineExaminer`.
  The first real provider should reuse that reader, not introduce a parallel one.
- **It defers ML cleanly.** Framework-backed providers (CNN, Transformer, YOLO,
  foundation model) remain interchangeable implementations behind the *same* seam
  (inference-boundary doc §8, §12). This provider proves the seam so those later
  choices change nothing downstream.

## 4. Provider Responsibilities

`LocalArtifactInferenceProvider` owns only:

- Validate that its input is a `StabilizedInspectionInput`.
- Resolve the input's `artifact_uri` to a **local** filesystem path.
- Read the local PGM P2 artifact's real pixel content deterministically.
- Derive one deterministic prediction payload (raw anomaly measure, judgement, and
  — for defects only — a localization) from that content and fixed provider
  constants.
- Construct and return exactly one `InspectionPrediction`.
- Surface a missing, non-local, unreadable, or malformed artifact as an explicit
  Inspection-domain failure.

The provider carries a descriptive provider identifier
(`local-artifact-inference-provider-v1`) for deterministic replay provenance only.
That identifier creates no trust, calibration, review, evidence, or evaluation
authority.

## 5. Provider Non-Responsibilities

`LocalArtifactInferenceProvider` must not:

- return `RawInspectionResult`;
- construct `RawInspectionResult`;
- emit `InspectionEvidenceRecord` or any evidence;
- qualify trust or expose calibrated confidence;
- abstain or assess drift;
- route review;
- evaluate, score, benchmark, or claim accuracy;
- persist any record;
- mutate the stabilized input;
- call `InspectionEngine`;
- call `transform_prediction()`;
- change any downstream domain;
- become the default `InspectionEngine.inspect()` path.

The provider's output remains an untrusted, non-canonical prediction until the
Inspection Engine validates and transforms it (inference-boundary doc §5).

## 6. Accepted Input Format

- The provider accepts **only** a `StabilizedInspectionInput`. Any other object
  raises `MalformedInspectionInput` (matching `DeterministicMockInferenceProvider`).
- The provider reads the artifact referenced by `inspection_input.artifact_uri`,
  resolved to a local path by the shared `resolve_local_artifact_path(...)`:
  - empty scheme (`part.pgm`) → local `Path`;
  - `file://` scheme → local `Path`;
  - any other scheme (`artifact://`, `http://`, `https://`) →
    `InspectionExaminationFailure` (non-local artifacts are refused).
- The artifact must be an **ASCII PGM (P2)** grayscale image, read by the shared
  `read_pgm_p2(...)` — the same reader the image baseline examiner uses. This is
  the only local image artifact format the repository currently supports; no new
  format is introduced.
- The provider does not require or read any label, ground-truth, trust, or routing
  information; none exists at this stage (Inspection plan §4).

## 7. Prediction Derivation

Derivation is deterministic and depends on real artifact content.

Provider constants (explicit, fixed, test-covered — changing any is a behavior
change):

```python
provider_id: str = "local-artifact-inference-provider-v1"
defect_threshold: float = 50.0      # raw 0–100 scale
anomaly_fraction: float = 0.5       # localization inclusion fraction
```

Derivation steps (reusing the shared helpers from `local_artifacts.py`):

1. `pixels, maxval = read_pgm_p2(path)` — real grayscale content.
2. `deviations, max_deviation, width, height = local_contrast_analysis(pixels, maxval)`
   — per-pixel absolute deviation from the normalized image mean (the same
   computation the image baseline examiner performs today).
3. `predicted_raw_anomaly_measure = round(max_deviation * 100.0, 6)` — a finite
   raw measure in the stable raw 0–100 range. It is raw substrate, never
   confidence.
4. `predicted_judgement = DEFECT if predicted_raw_anomaly_measure >= defect_threshold
   else OK`.
5. For `DEFECT`: `predicted_localization =
   localization_from_deviations(deviations, max_deviation, anomaly_fraction, width,
   height, localization_kind="local_artifact_suspected_region")` — a normalized,
   ordered-bounds `DefectLocalization`. For `OK`: `predicted_localization = None`.
6. `prediction_id = f"local-artifact-prediction:{digest[:32]}"`, where `digest`
   is `sha256` over a canonical payload of `provider_id`, `input_id`, `pixels`,
   and `maxval`. Because `pixels`/`maxval` are real content, **changed artifact
   content changes the digest, the id, and therefore the prediction**.

Constructed prediction (`InspectionPrediction`):

| Field | Source |
| --- | --- |
| `input_id` | `inspection_input.input_id` |
| `prediction_id` | content-derived `local-artifact-prediction:<digest>` |
| `predicted_judgement` | step 4 threshold rule |
| `predicted_raw_anomaly_measure` | step 3 raw measure |
| `predicted_localization` | step 5 (defect only, else `None`) |
| `raw_measure_kind` | `InspectionPrediction` default (`RAW_MEASURE_KIND`) — unchanged |
| `raw_measure_scale` | `InspectionPrediction` default (`PREDICTION_RAW_MEASURE_SCALE`) — unchanged |
| `prediction_kind` | `InspectionPrediction` default (`INSPECTION_PREDICTION_KIND`) — unchanged |
| `model_metadata` | descriptive strings only: `{"method": provider_id, "version": "1", "artifact_format": "pgm_p2"}` |

The provider keeps the prediction's default `raw_measure_kind`,
`raw_measure_scale`, and `prediction_kind` so that the existing
`transform_prediction()` accepts it unchanged (engine validation requires
`prediction_kind == INSPECTION_PREDICTION_KIND` and
`raw_measure_kind == RAW_MEASURE_KIND`). The PGM origin is recorded only as
descriptive `model_metadata`.

The provider must not add trust, calibrated confidence, review, evidence,
evaluation, outcome, or target meaning to `model_metadata`; the existing metadata
guards reject any forbidden downstream key.

## 8. Failure Modes

All failures remain inside the Inspection domain and are never converted into a
judgement.

| Failure | Trigger | Required handling |
| --- | --- | --- |
| Input is not `StabilizedInspectionInput` | `provider.predict(object())` | Raise `MalformedInspectionInput`. |
| Stabilized input already invalid | blank id / hash / unstabilized status | Rely on existing `StabilizedInspectionInput` construction guards. |
| Non-local artifact reference | `artifact://`, `http://`, `https://` scheme | `InspectionExaminationFailure` (from shared `resolve_local_artifact_path`). |
| Missing / unreadable artifact | path does not exist or not a file | `InspectionExaminationFailure`. |
| Malformed / non-P2 / truncated artifact | bad magic, bad header, truncated pixels, out-of-range pixel | `InspectionExaminationFailure` (from shared `read_pgm_p2`). |
| Derived values cannot form a valid prediction | non-finite measure, invalid bounds | Let `InspectionPrediction` / `NormalizedBoundingBox` raise the existing prediction/geometry error. |
| Provider accidentally returns a non-prediction | regression | Tests fail before any downstream transformation. |
| Provider gains evidence/trust/review/persist/evaluate behavior | regression | Tests fail. |

The provider must not catch a prediction-construction failure and substitute an OK
or DEFECT judgement. Failures are explicit and inspectable (AGENTS.md; Inspection
plan §9).

## 9. Tests

All tests are additive in `tests/test_inspection_engine.py` (consistent with the
existing provider tests). Tests assert **contract and boundary**, never model
quality, accuracy, or calibration. Test name prefix:
`test_local_artifact_inference_provider_`.

Planned coverage (mapped to the task's testing requirements):

1. **Public import.** `LocalArtifactInferenceProvider` imports from
   `src.inspection` and is the same object as `inspection_api.LocalArtifactInferenceProvider`.
2. **Protocol conformance.** A `LocalArtifactInferenceProvider` instance is
   assignable to `InspectionInferenceProvider` and `provider.predict` is callable.
3. **Reads local artifact content deterministically.**
   `provider.predict(_baseline_input("blob_defect.pgm"))` returns an
   `InspectionPrediction` referencing the input id.
4. **Same artifact → identical prediction.** Two `predict` calls (same instance,
   and two separate instances) on the same fixture input produce equal
   `InspectionPrediction` values.
5. **Changed artifact content → changed prediction.** Predictions for
   `blob_defect.pgm` and `blob_defect_shifted.pgm` (same DEFECT judgement,
   different pixel content) are unequal, and both are valid `InspectionPrediction`
   values — proving derivation tracks real content, not just judgement.
6. **Returns only `InspectionPrediction`.** The returned object is an
   `InspectionPrediction` and is `not isinstance(..., RawInspectionResult)`.
7. **DEFECT includes localization; OK omits it.** `blob_defect.pgm` →
   `predicted_judgement is DEFECT` with non-`None` localization;
   `uniform_ok.pgm` → `predicted_judgement is OK` with `predicted_localization is None`.
8. **No downstream fields.** `assert_no_downstream_fields(InspectionPrediction)`
   stays green; the returned prediction exposes no `confidence`,
   `calibrated_confidence`, `qualified_outcome`, `raw_inspection_result`,
   evidence, trust, or evaluation attribute.
9. **Provider emits no evidence / no downstream behavior.** The provider exposes
   no `qualify`, `calibrate`, `emit`, `evidence`, `evaluate`, `inspect`,
   `persist`, `raw_result`, `route_for_review`, `transform_prediction`,
   `update_model`, or `train` attribute.
10. **Malformed input rejected.** `provider.predict(object())` raises
    `MalformedInspectionInput`.
11. **Non-local / missing / malformed artifact rejected.** A `StabilizedInspectionInput`
    with an `artifact://` URI, a missing file path, and a `bad_magic.pgm` path each
    raise `InspectionExaminationFailure`.
12. **Integrates with `transform_prediction()`.**
    `InspectionEngine().transform_prediction(input, provider.predict(input))`
    returns an `InspectionEngineOutput` whose `raw_inspection_result` is a
    `RawInspectionResult` with `examination_kind == INSPECTION_PREDICTION_KIND`,
    `raw_measure_scale == PREDICTION_RAW_MEASURE_SCALE`, and
    `raw_measure_kind == RAW_MEASURE_KIND`.
13. **Evidence is engine-owned.** A recording evidence emitter records nothing from
    `provider.predict(...)` and records exactly the transformed raw result only
    after `transform_prediction(...)` (mirrors the existing mock-provider evidence
    test).
14. **Default engine path unchanged.** `InspectionEngine().inspect(input)` still
    uses the placeholder examiner; the engine exposes no `provider`,
    `inference_provider`, `model`, or `predict` attribute, and the default result's
    `examination_kind` is not `INSPECTION_PREDICTION_KIND`.
15. **Behavior-preserving extraction.** The existing PGM-reader tests
    (`test_pgm_reader_*`, `test_resolver_rejects_non_local_scheme`) and image
    baseline tests (`test_baseline_*`) stay green unchanged, confirming the
    extracted helpers preserve behavior and the engine's `_read_pgm_p2` /
    `_resolve_local_artifact_path` names remain importable.
16. **Downstream suites green.** Trust, integration, and CLI suites and the
    repo-wide suite pass unchanged.

Focused commands:

```bash
python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
python3 -m pytest tests/test_inspection_engine.py -q
python3 -m pytest tests/test_trust_qualification_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
```

## 10. Integration Impact

- **None to `InspectionEngine.inspect()`.** The default path remains:

  ```text
  InspectionEngine.inspect(StabilizedInspectionInput)
    -> DeterministicPlaceholderExaminer
    -> RawInspectionResult
    -> InspectionEvidenceRecord
  ```

- **Provider path is test-only** unless a later public plan authorizes wiring:

  ```text
  LocalArtifactInferenceProvider.predict(StabilizedInspectionInput)
    -> InspectionPrediction
    -> InspectionEngine.transform_prediction(...)
    -> RawInspectionResult
    -> InspectionEvidenceRecord
  ```

- **None to integration or CLI.** `src/integration/` and the CLI are not modified
  and do not reference the provider.
- **None downstream.** Trust, Review, Evidence, and Evaluation continue to consume
  only `RawInspectionResult` and existing evidence records.
- **Behavior-preserving engine refactor.** Extracting the PGM reader/contrast
  helpers changes no observable engine behavior; existing baseline and reader tests
  guard this.
- **Public surface (additive only).** `src/inspection/__init__.py` adds
  `LocalArtifactInferenceProvider`. Nothing is removed or renamed.

## 11. Out of Scope

This plan does not authorize, and the implementation must not introduce:

- model training, learned weights, datasets, or dataset creation;
- benchmarking, accuracy claims, or production computer-vision claims;
- GPU, batching, quantization, or deployment;
- external ML frameworks (PyTorch, ONNX, TensorFlow, CoreML, OpenVINO);
- any new third-party dependency;
- provider wiring into `InspectionEngine.inspect()`, integration, or CLI;
- changes to the `InspectionPrediction` contract,
  `InspectionInferenceProvider` protocol, `RawInspectionResult`, or
  `transform_prediction()`;
- changes to README, prototype, assets, asset pipeline, Trust, Review, Evidence,
  or Evaluation;
- persistence, hosted, live, streaming, scheduled, or continuously operating
  behavior, or any feedback loop.

## 12. Implementation Steps

> Each task is test-first (TDD). After each task, run the listed command and
> confirm the expected result. Commit points are **owner validation checkpoints**:
> report results and let the repository owner commit. Do not run git yourself.

### Task A: Extract the shared local-artifact helpers (behavior-preserving)

**Files:** Create `src/inspection/local_artifacts.py`; Modify
`src/inspection/engine.py`.

- [ ] **Step 1 — Confirm the guard tests pass before refactor.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k "pgm_reader or resolver or baseline" -q
  ```

  Expected: PASS (these protect behavior preservation across the extraction).

- [ ] **Step 2 — Create `src/inspection/local_artifacts.py`** with the moved
  helpers, exposing public names:

  ```python
  from __future__ import annotations

  from pathlib import Path
  from urllib.parse import unquote, urlparse

  from .domain import DefectLocalization, NormalizedBoundingBox
  from .errors import InspectionExaminationFailure


  def resolve_local_artifact_path(artifact_uri: str) -> Path:
      parsed = urlparse(artifact_uri)
      if parsed.scheme == "":
          return Path(artifact_uri)
      if parsed.scheme == "file":
          return Path(unquote(parsed.path))
      raise InspectionExaminationFailure(
          "local artifact reader only reads local file artifacts, "
          f"not '{parsed.scheme}://' references"
      )


  def read_pgm_p2(path: Path) -> tuple[list[list[int]], int]:
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
                  "local artifact reader supports only ascii PGM (P2) artifacts"
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


  def local_contrast_analysis(
      pixels: list[list[int]], maxval: int
  ) -> tuple[list[list[float]], float, int, int]:
      height = len(pixels)
      width = len(pixels[0])
      normalized_mean = sum(sum(row) for row in pixels) / (width * height * maxval)
      deviations = [
          [abs(value / maxval - normalized_mean) for value in row]
          for row in pixels
      ]
      max_deviation = max(max(row) for row in deviations)
      return deviations, max_deviation, width, height


  def localization_from_deviations(
      deviations: list[list[float]],
      max_deviation: float,
      anomaly_fraction: float,
      width: int,
      height: int,
      localization_kind: str = "local_contrast_suspected_region",
  ) -> DefectLocalization:
      threshold = anomaly_fraction * max_deviation
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
      return DefectLocalization(
          region=NormalizedBoundingBox(
              x_min=round(min(cols) / width, 6),
              y_min=round(min(rows) / height, 6),
              x_max=round((max(cols) + 1) / width, 6),
              y_max=round((max(rows) + 1) / height, 6),
          ),
          localization_kind=localization_kind,
      )


  def _pgm_tokens(text: str):
      for raw_line in text.splitlines():
          line = raw_line.split("#", 1)[0]
          for token in line.split():
              yield token
  ```

- [ ] **Step 3 — Rewire `src/inspection/engine.py` to consume the extracted
  helpers** (behavior-preserving). Remove the moved function bodies
  (`_resolve_local_artifact_path`, `_read_pgm_p2`, `_pgm_tokens`,
  `_localization_from_deviations`) and the inline deviation math in
  `DeterministicImageBaselineExaminer.examine`. Add the import and keep
  backward-compatible aliases so the existing test imports still resolve:

  ```python
  from .local_artifacts import (
      local_contrast_analysis,
      localization_from_deviations,
      read_pgm_p2 as _read_pgm_p2,
      resolve_local_artifact_path as _resolve_local_artifact_path,
  )
  ```

  Update `DeterministicImageBaselineExaminer.examine` to use the helpers while
  preserving the exact current behavior (same rounding, same labels, same
  `localization_kind="local_contrast_suspected_region"`):

  ```python
  path = _resolve_local_artifact_path(inspection_input.artifact_uri)
  if not path.exists() or not path.is_file():
      raise InspectionExaminationFailure(
          f"inspection artifact is missing or unreadable: {path}"
      )

  pixels, maxval = _read_pgm_p2(path)
  deviations, max_deviation, width, height = local_contrast_analysis(pixels, maxval)
  raw_measure = round(max_deviation * 100.0, 6)
  judgement = (
      InspectionJudgement.DEFECT
      if raw_measure >= self.defect_threshold
      else InspectionJudgement.OK
  )
  localization = (
      localization_from_deviations(
          deviations, max_deviation, self.anomaly_fraction, width, height
      )
      if judgement is InspectionJudgement.DEFECT
      else None
  )
  ```

  Keep `_localization_from_digest`, `_unit_interval`, `_stable_id`, and `_digest`
  in `engine.py` (still used by the placeholder examiner / id derivation).

- [ ] **Step 4 — Run the guard tests; confirm unchanged behavior.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k "pgm_reader or resolver or baseline" -q
  ```

  Expected: PASS (identical to Step 1).

- [ ] **Step 5 — Validation checkpoint.** Report; do not commit.

### Task B: Add the changed-content fixture

**Files:** Add `tests/fixtures/inspection/blob_defect_shifted.pgm`.

- [ ] **Step 1 — Create a DEFECT-producing PGM whose content differs from
  `blob_defect.pgm`** (defect block in a different location, still a 4×4 ascii P2
  grid so `max_deviation * 100 >= 50.0`):

  ```text
  P2
  4 4
  255
  255 255 0 0
  255 255 0 0
  0 0 0 0
  0 0 0 0
  ```

- [ ] **Step 2 — Sanity-check it parses and is DEFECT under the baseline reader.**

  ```bash
  python3 -c "from pathlib import Path; from src.inspection.local_artifacts import read_pgm_p2, local_contrast_analysis; p,m=read_pgm_p2(Path('tests/fixtures/inspection/blob_defect_shifted.pgm')); d,mx,w,h=local_contrast_analysis(p,m); print(round(mx*100,6))"
  ```

  Expected: a printed value `>= 50.0` (DEFECT), and different from
  `blob_defect.pgm`'s value, confirming the fixtures differ in content.

- [ ] **Step 3 — Validation checkpoint.** Report; do not commit.

### Task C: Add provider-focused failing tests

**Files:** Modify `tests/test_inspection_engine.py`.

- [ ] **Step 1 — Add a helper and the §9 tests** under the
  `test_local_artifact_inference_provider_` prefix. Helper:

  ```python
  def _local_artifact_provider_type():
      from src.inspection import LocalArtifactInferenceProvider

      return LocalArtifactInferenceProvider
  ```

  Add tests covering §9 items 1–14: public import; protocol conformance;
  deterministic read; same-input determinism (one instance and two instances);
  changed-content inequality (`blob_defect.pgm` vs `blob_defect_shifted.pgm`);
  returns only `InspectionPrediction` (never `RawInspectionResult`); DEFECT
  localization present / OK localization absent; no downstream fields; no
  downstream/runtime methods; `MalformedInspectionInput` on `object()`;
  `InspectionExaminationFailure` on `artifact://`, missing path, and
  `bad_magic.pgm`; `transform_prediction()` integration producing a
  prediction-origin `RawInspectionResult`; engine-owned evidence; and unchanged
  default `inspect()` path. Reuse the existing `make_input`, `_baseline_input`,
  `FIXTURES`, and `assert_no_downstream_fields` helpers already in the file.

- [ ] **Step 2 — Run; confirm failure (`ImportError`).**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
  ```

  Expected: failure caused by the missing `LocalArtifactInferenceProvider` import.

- [ ] **Step 3 — Validation checkpoint.** Report; do not commit.

### Task D: Implement `LocalArtifactInferenceProvider`

**Files:** Modify `src/inspection/providers.py`; Modify
`src/inspection/__init__.py`.

- [ ] **Step 1 — Add the provider to `src/inspection/providers.py`**, reusing the
  module-local `_digest` and the shared helpers from `local_artifacts.py`:

  ```python
  from .local_artifacts import (
      local_contrast_analysis,
      localization_from_deviations,
      read_pgm_p2,
      resolve_local_artifact_path,
  )


  @dataclass(frozen=True)
  class LocalArtifactInferenceProvider:
      provider_id: str = "local-artifact-inference-provider-v1"
      defect_threshold: float = 50.0
      anomaly_fraction: float = 0.5

      def predict(
          self,
          inspection_input: StabilizedInspectionInput,
      ) -> InspectionPrediction:
          if not isinstance(inspection_input, StabilizedInspectionInput):
              raise MalformedInspectionInput(
                  "local artifact provider requires StabilizedInspectionInput"
              )

          path = resolve_local_artifact_path(inspection_input.artifact_uri)
          if not path.exists() or not path.is_file():
              raise InspectionExaminationFailure(
                  f"inspection artifact is missing or unreadable: {path}"
              )

          pixels, maxval = read_pgm_p2(path)
          deviations, max_deviation, width, height = local_contrast_analysis(
              pixels, maxval
          )
          raw_measure = round(max_deviation * 100.0, 6)
          judgement = (
              InspectionJudgement.DEFECT
              if raw_measure >= self.defect_threshold
              else InspectionJudgement.OK
          )
          localization = (
              localization_from_deviations(
                  deviations,
                  max_deviation,
                  self.anomaly_fraction,
                  width,
                  height,
                  localization_kind="local_artifact_suspected_region",
              )
              if judgement is InspectionJudgement.DEFECT
              else None
          )
          digest = _digest(
              {
                  "input_id": inspection_input.input_id,
                  "maxval": maxval,
                  "pixels": pixels,
                  "provider_id": self.provider_id,
              }
          )

          return InspectionPrediction(
              input_id=inspection_input.input_id,
              prediction_id=f"local-artifact-prediction:{digest[:32]}",
              predicted_judgement=judgement,
              predicted_raw_anomaly_measure=raw_measure,
              predicted_localization=localization,
              model_metadata={
                  "method": self.provider_id,
                  "version": "1",
                  "artifact_format": "pgm_p2",
              },
          )
  ```

  Update the `providers.py` imports to add `InspectionExaminationFailure` from
  `.errors` (alongside `MalformedInspectionInput`). Do not import
  `InspectionEngine`. Do not construct `RawInspectionResult` or
  `InspectionEvidenceRecord`.

- [ ] **Step 2 — Export the provider in `src/inspection/__init__.py`.** Add
  `LocalArtifactInferenceProvider` to the `.providers` import line and insert
  `"LocalArtifactInferenceProvider"` into `__all__` (alphabetically, after
  `InvalidInspectionResult` / before `MalformedInspectionInput`). Do not alter
  existing exports.

- [ ] **Step 3 — Run; confirm PASS.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
  ```

  Expected: PASS (all §9 provider tests).

- [ ] **Step 4 — Validation checkpoint.** Report; do not commit.

### Task E: Verify the inspection suite and downstream isolation

**Files:** none (verification only).

- [ ] **Step 1 — Inspection suite.**

  ```bash
  python3 -m pytest tests/test_inspection_engine.py -q
  ```

  Expected: PASS (existing + new; extraction preserved behavior).

- [ ] **Step 2 — Downstream unchanged.**

  ```bash
  python3 -m pytest tests/test_trust_qualification_engine.py tests/test_end_to_end_substrate_integration.py tests/test_integration_cli.py -q
  ```

  Expected: PASS.

- [ ] **Step 3 — Validation checkpoint.** Report; do not commit.

### Task F: Full validation checkpoint

**Files:** none (verification only).

- [ ] **Step 1 — Repo-wide suite.**

  ```bash
  python3 -m pytest -q
  ```

  Expected: PASS.

- [ ] **Step 2 — Compile.**

  ```bash
  python3 -m compileall -q src tests scripts
  ```

  Expected: exit 0.

- [ ] **Step 3 — Scope discipline.**

  ```bash
  git status --short
  ```

  Expected changed/created files only: `src/inspection/local_artifacts.py`,
  `src/inspection/providers.py`, `src/inspection/engine.py`,
  `src/inspection/__init__.py`, `tests/test_inspection_engine.py`, and
  `tests/fixtures/inspection/blob_defect_shifted.pgm`. **No** change under
  `src/trust/`, `src/review/`, `src/evidence/`, `src/evaluation/`,
  `src/integration/`, `scripts/`, `README.md`, `assets/`, or `tools/`.

- [ ] **Step 4 — Final validation checkpoint.** Report all results to the owner;
  the owner commits. Do not commit.

---

## Self-Review

- **Spec coverage:** purpose (§1), scope (§2), why local + stdlib (§3), provider
  responsibilities (§4), non-responsibilities (§5), accepted input format (§6),
  prediction derivation (§7), failure modes (§8), tests (§9), integration impact
  (§10), out of scope (§11), implementation steps (§12) — all present, matching the
  requested structure.
- **Boundary rules honored:** the provider implements `InspectionInferenceProvider`,
  accepts `StabilizedInspectionInput`, returns only `InspectionPrediction`, never
  returns `RawInspectionResult`, never emits evidence, never calls
  `InspectionEngine` or `transform_prediction()`, never qualifies trust, routes
  review, evaluates, or persists.
- **Real-but-stdlib discipline:** derivation reads real PGM pixel content via the
  existing reader; no PyTorch/ONNX/TensorFlow/CoreML/OpenVINO, no new dependency,
  no model, weights, training, or dataset.
- **Reuse over invention (DRY):** the PGM reader and contrast/localization helpers
  are extracted once into `local_artifacts.py` and shared by the image baseline
  examiner and the new provider; no logic is duplicated, and no responsibility
  leaves the Inspection domain. Engine refactor is behavior-preserving and guarded
  by existing reader/baseline tests; the engine's `_read_pgm_p2` /
  `_resolve_local_artifact_path` names stay importable via aliases.
- **Determinism & content sensitivity:** prediction id and payload derive from real
  `pixels`/`maxval`, so identical artifacts yield identical predictions and changed
  artifact content yields a changed prediction — both asserted by tests.
- **Type consistency:** `LocalArtifactInferenceProvider.predict` returns
  `InspectionPrediction`; the prediction keeps default `raw_measure_kind`,
  `raw_measure_scale`, and `prediction_kind` so existing `transform_prediction()`
  accepts it unchanged; helper names (`read_pgm_p2`,
  `resolve_local_artifact_path`, `local_contrast_analysis`,
  `localization_from_deviations`) are used consistently across §7 and §12.
- **Placeholder scan:** no TBD/TODO; every code step shows concrete code and every
  run step lists the exact command and expected result.
