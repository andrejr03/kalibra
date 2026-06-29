# Kalibra ML Phase 1 — Task 1: InspectionPrediction Contract & Provider Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Where this plan reaches a commit
> point, it instead defines a **validation checkpoint**: run the listed commands,
> report results, and let the repository owner commit. Do not commit.

**Goal:** Introduce the first piece of the ML inference boundary as a
**contract-only** change inside the Inspection domain: the abstract
`InspectionPrediction` contract and the `InspectionInferenceProvider` protocol.
No model, no ML runtime, no training, no datasets, and no inference
implementation are added. The provider is **not** wired into `InspectionEngine`,
and `InspectionPrediction` is **not** transformed into `RawInspectionResult` —
those are later tasks.

**Architecture:** This task realizes the seam fixed by
[`docs/KALIBRA_ML_PHASE_1_INSPECTION_INFERENCE_BOUNDARY_v1.0.md`](KALIBRA_ML_PHASE_1_INSPECTION_INFERENCE_BOUNDARY_v1.0.md)
(§3 Boundary, §6 Prediction Contract, §9 Failure Modes). Machine Learning will
later sit behind an `InspectionInferenceProvider` and produce only an
`InspectionPrediction`; the Inspection Engine remains the sole owner of
`RawInspectionResult`. This task adds **only the two boundary objects** and their
validation — the untrusted, non-canonical prediction shape and the protocol that
produces it — so that later tasks can wire and transform against a fixed contract.

**Tech Stack:** Existing Python 3.9 `dataclasses` substrate under
`src/inspection/`, Python standard library only. **No new dependencies. No ML
library. No model. No inference runtime.** `pytest` for tests under `tests/`.

---

## Interpretation Note (scope boundary)

The task authorizes adding the inference-boundary **contract and protocol** to the
Inspection domain, consistent with the Inspection Engine plan §12 ("Examination
internals are replaceable") and the inference-boundary doc §3. Therefore:

- **Modifiable (this plan):** `src/inspection/domain.py`,
  `src/inspection/interfaces.py`, `src/inspection/errors.py`,
  `src/inspection/__init__.py`, and `tests/test_inspection_engine.py`.
- **Must NOT be modified:** `src/inspection/engine.py` (no wiring of the provider,
  no transformation), `src/trust/`, `src/review/`, `src/evidence/`,
  `src/evaluation/`, `src/integration/`, `scripts/`, `README.md`, `assets/`,
  `tools/` (asset pipeline), the CLI, and any prototype.

Every change is **additive and downstream-neutral**: no existing field, type,
constant, or default is removed or renamed; the `RawInspectionResult`,
`PlaceholderExamination`, `InspectionEvidenceRecord`, and `InspectionEngine`
contracts are untouched. The new objects stand alongside the existing ones and are
referenced by nothing in the runtime chain yet.

---

## 1. Purpose

Add the first, smallest unit of the ML inference boundary: the abstract product of
Machine Learning (`InspectionPrediction`) and the protocol that will produce it
(`InspectionInferenceProvider`).

`InspectionPrediction` is a **claim, not a result**. It is the untrusted,
non-canonical, unvalidated-until-accepted output that a future inference
implementation will return about one stabilized inspection input. This task fixes
its shape and its self-validation so that:

- a valid prediction can be constructed and is self-describing as a *prediction*
  and as *raw* (never confidence);
- an invalid judgement, localization, or raw measure is refused at construction;
- forbidden downstream fields (trust, calibration, routing, evaluation,
  ground-truth) cannot be smuggled in;
- a later task can validate and transform a fixed prediction contract into the
  canonical `RawInspectionResult` without the contract shifting under it.

`InspectionInferenceProvider` is the abstract seam object that will later load and
execute inference and **return only an `InspectionPrediction`**. This task adds the
protocol shape only — no concrete provider, no model.

This task does **not** introduce inference, does **not** wire the provider into the
engine, and does **not** transform predictions. It opens nothing it does not need
to; it only fixes the contract.

## 2. Scope

**In scope (this task):**

- A new frozen dataclass `InspectionPrediction` in `src/inspection/domain.py`,
  validated in `__post_init__`, reusing the existing `InspectionJudgement`,
  `DefectLocalization`, and `NormalizedBoundingBox` types and the existing
  forbidden-metadata machinery.
- New descriptive constants for the prediction (kind label and default raw-measure
  scale), placed beside the existing kind/scale constants.
- A new `InspectionInferenceProvider` `Protocol` in `src/inspection/interfaces.py`
  whose single method returns `InspectionPrediction`.
- New error types for invalid/partial predictions in `src/inspection/errors.py`.
- Additive public exports in `src/inspection/__init__.py`.
- Additive tests in `tests/test_inspection_engine.py`.

**Explicitly out of scope (later tasks / forbidden here):**

- Any concrete `InspectionInferenceProvider` implementation, model, weights, or
  inference runtime.
- Wiring the provider into `InspectionEngine` (no change to `engine.py`).
- Transforming `InspectionPrediction` → `RawInspectionResult`.
- Any change to Trust, Review, Evidence, Evaluation, integration, or CLI.

## 3. New Contract: `InspectionPrediction`

A new frozen dataclass added to `src/inspection/domain.py`. It mirrors the
validated discipline of `PlaceholderExamination` but is explicitly a
**non-canonical prediction**, owned by no domain until the Inspection Engine
accepts it (inference-boundary doc §6).

**Abstract fields (representation fixed here; no tensors/framework objects):**

| Field | Type | Meaning |
| --- | --- | --- |
| `input_id` | `str` | Reference to the exact stabilized input the prediction concerns (traceability). Required, non-blank. |
| `prediction_id` | `str` | Stable identity of this prediction (traceability). Required, non-blank. |
| `predicted_judgement` | `InspectionJudgement` | The model's *claimed* judgement (`DEFECT` / `OK`). A claim, not the canonical judgement. |
| `predicted_raw_anomaly_measure` | `float` | The model's *raw, uncalibrated* anomaly measure. Must be finite. Not confidence, not a probability. |
| `predicted_localization` | `DefectLocalization \| None` | The model's *claimed* suspected region. Present iff `predicted_judgement` is `DEFECT`. |
| `raw_measure_kind` | `str` = `RAW_MEASURE_KIND` | Self-describes the measure as raw; defaults to and is validated equal to `"raw_anomaly_measure"` so the engine can later carry it downstream unchanged. |
| `raw_measure_scale` | `str` = `PREDICTION_RAW_MEASURE_SCALE` | Descriptive raw-scale label for the prediction's measure. Required, non-blank. Not constrained to the examiner scales (model scales are a later concern). |
| `prediction_kind` | `str` = `INSPECTION_PREDICTION_KIND` | Descriptive provenance label of the prediction. Required, non-blank. |
| `model_metadata` | `Mapping[str, str]` = `{}` | Abstract, descriptive model provenance (e.g. opaque method id/version). Frozen and forbidden-field filtered (§6). Carries no trust/routing/evaluation/ground-truth meaning. |

New constants (added near `INSPECTION_EVIDENCE_KIND` in `domain.py`):

```python
INSPECTION_PREDICTION_KIND = "inspection_prediction"
PREDICTION_RAW_MEASURE_SCALE = "model_raw_anomaly_measure"
```

**The prediction carries no trust-bearing field.** There is deliberately no
`confidence`, `calibrated_confidence`, `qualified_outcome`, `abstention`,
`drift`, `review`/`routing`, or `evaluation` field — those belong to later domains
and must be *absent*, not stubbed (inference-boundary doc §5, §6).

## 4. New Protocol: `InspectionInferenceProvider`

Added to `src/inspection/interfaces.py`, beside the existing `InspectionExaminer`
and `InspectionEvidenceEmitterProtocol`:

```python
class InspectionInferenceProvider(Protocol):
    def predict(
        self, inspection_input: StabilizedInspectionInput
    ) -> InspectionPrediction:
        ...
```

Obligations the protocol fixes:

- It accepts a `StabilizedInspectionInput` (the same stabilized contract every
  examiner consumes) and returns **only** an `InspectionPrediction`.
- It is a *shape*, not an implementation: this task adds **no** concrete provider.
  A future task supplies a provider that loads and executes inference behind this
  seam; the only test double in this task is a trivial structural stub (no model).
- It must not be referenced by `InspectionEngine` in this task — it is wired in a
  later task.

The provider **must not** expose or return `RawInspectionResult`, trust
qualification, evidence records, evaluation reports, review routing, scores,
benchmark claims, or calibrated confidence — these are guarded by the prediction
contract (§3, §6) and asserted by tests (§8).

## 5. Validation Rules

`InspectionPrediction.__post_init__` enforces (mirroring the existing
`PlaceholderExamination` / `RawInspectionResult` discipline):

- `input_id` is non-blank → else `InvalidInspectionPrediction`.
- `prediction_id` is non-blank → else `InvalidInspectionPrediction`.
- `predicted_raw_anomaly_measure` is finite (`math.isfinite`) → else
  `InvalidInspectionPrediction`.
- `raw_measure_kind == RAW_MEASURE_KIND` (`"raw_anomaly_measure"`) → else
  `InvalidInspectionPrediction` ("prediction measure must be explicitly marked
  raw"). This keeps the prediction self-describing as raw and downstream-carryable.
- `raw_measure_scale` is non-blank → else `InvalidInspectionPrediction`.
- `prediction_kind` is non-blank → else `InvalidInspectionPrediction`.
- **Judgement/localization consistency:**
  - `predicted_judgement is DEFECT and predicted_localization is None` →
    `PartialInspectionPrediction` ("defect predictions require localization").
  - `predicted_judgement is OK and predicted_localization is not None` →
    `PartialInspectionPrediction` ("ok predictions must not include localization").
- `model_metadata` is frozen and forbidden-field filtered via the **existing**
  `_freeze_metadata` / `_is_forbidden_metadata_key` machinery already in
  `domain.py`; a forbidden key raises `InvalidInspectionInput` (reused), and
  non-string keys/values raise `InvalidInspectionInput` (reused).

Localization validity (normalized, finite, ordered bounds) is already enforced by
`NormalizedBoundingBox.__post_init__` and `DefectLocalization.__post_init__`, which
this contract reuses unchanged — so an invalid localization fails at construction
without new code.

## 6. Forbidden Fields

Two layers, both reusing existing machinery:

1. **No trust-bearing dataclass fields.** `InspectionPrediction` declares none of
   the downstream field names guarded by the test suite's `DOWNSTREAM_FIELD_NAMES`
   set (`confidence`, `calibrated_confidence`, `qualified_outcome`,
   `qualification`, `abstention`, `drift`, `review`, `review_routing`, `routing`,
   `trust`, `trust_qualification`, `evaluation`). A test asserts
   `field_names(InspectionPrediction)` is disjoint from `DOWNSTREAM_FIELD_NAMES`,
   exactly as `test_raw_result_contains_no_downstream_domain_fields` does for
   `RawInspectionResult`.
2. **No smuggling via `model_metadata`.** The metadata map is filtered by the
   existing `_FORBIDDEN_METADATA_KEYS` set and
   `_FORBIDDEN_METADATA_TOKEN_SEQUENCES` (which already cover `confidence`,
   `calibrated confidence`, `trust`, `trust qualification`, `qualified outcome`,
   `drift`, `routing`, `review routing`, `route to review`, `ground truth`,
   `true/defect label`, `outcome`, `target`, etc.). No new forbidden keys are
   required; the prediction reuses the same guard the stabilized input uses.

This satisfies the boundary rule that the provider must not produce calibrated
confidence, trust, routing, evaluation, or scores (inference-boundary doc §5).

## 7. Failure Modes

Aligned with inference-boundary doc §9, but limited to what a **contract-only**
step can enforce (construction-time validation). All are surfaced as explicit
Inspection-domain errors; none is silently repaired or converted into a verdict.

| Failure | Trigger | Handling |
| --- | --- | --- |
| Missing input reference | blank `input_id` | `InvalidInspectionPrediction` |
| Missing prediction identity | blank `prediction_id` | `InvalidInspectionPrediction` |
| Invalid raw anomaly measure | non-finite `predicted_raw_anomaly_measure` | `InvalidInspectionPrediction` |
| Measure not marked raw | `raw_measure_kind != "raw_anomaly_measure"` | `InvalidInspectionPrediction` |
| Missing scale / kind label | blank `raw_measure_scale` or `prediction_kind` | `InvalidInspectionPrediction` |
| Invalid localization (defect w/o box, ok w/ box) | judgement/localization mismatch | `PartialInspectionPrediction` |
| Invalid localization geometry | non-normalized / unordered bounds | `InvalidInspectionResult` (reused, via `NormalizedBoundingBox`) |
| Forbidden downstream field | `model_metadata` carries trust/routing/etc. key | `InvalidInspectionInput` (reused) |

New error types (added to `src/inspection/errors.py`, mirroring
`InvalidInspectionResult` / `PartialInspectionResult`):

```python
class InvalidInspectionPrediction(InspectionError):
    """Raised when an inference prediction violates the prediction contract."""


class PartialInspectionPrediction(InvalidInspectionPrediction):
    """Raised when a prediction is incomplete or internally inconsistent."""
```

Failure modes that require a running provider or engine wiring — **model
unavailable**, **incompatible prediction version**, **inference
non-reproducibility** — are named by the boundary doc but belong to the later
wiring/transformation tasks and are **out of scope** here (§10).

## 8. Tests

All tests are **additive** in `tests/test_inspection_engine.py`; the existing
suite must keep passing unchanged. Tests assert **contract and boundary**, never
model quality or detection accuracy.

Planned coverage (mapped to the task's testing requirements):

1. **Valid prediction constructs.** A well-formed `InspectionPrediction`
   (`OK`, no localization) and a defective one (`DEFECT` with a
   `NormalizedBoundingBox`) both construct, expose `input_id`, `prediction_id`,
   `raw_measure_kind == "raw_anomaly_measure"`, a non-blank `raw_measure_scale`,
   and `prediction_kind == INSPECTION_PREDICTION_KIND`.
2. **Invalid judgement fails.** `predicted_judgement is DEFECT` with
   `predicted_localization=None` raises `PartialInspectionPrediction`; `OK` with a
   localization raises `PartialInspectionPrediction`.
3. **Invalid localization fails.** A `NormalizedBoundingBox` with unordered/out-of-
   range bounds raises (reused `InvalidInspectionResult`), proving the reused
   geometry guard protects the prediction.
4. **Invalid raw anomaly measure fails.** `float("nan")`/`float("inf")` measure
   raises `InvalidInspectionPrediction`; a non-raw `raw_measure_kind` raises
   `InvalidInspectionPrediction`.
5. **Forbidden downstream fields rejected or absent.**
   - `field_names(InspectionPrediction)` is disjoint from `DOWNSTREAM_FIELD_NAMES`
     (via `assert_no_downstream_fields`).
   - `model_metadata={"calibrated_confidence": "0.9"}` and
     `model_metadata={"trust_qualification": "accept"}` each raise
     `InvalidInspectionInput`; an ordinary key (e.g. `{"method": "abstract-v1"}`)
     is accepted.
6. **Provider protocol returns `InspectionPrediction` only.** A trivial in-test
   stub implementing `InspectionInferenceProvider.predict` returns an
   `InspectionPrediction` referencing the input; the test asserts
   `isinstance(result, InspectionPrediction)`.
7. **Provider does not expose downstream surfaces.** The returned prediction has
   no `confidence`, `calibrated_confidence`, `qualified_outcome`,
   `raw_inspection_result`, evidence-record, trust, or evaluation attribute
   (`assert not hasattr(...)`), and the stub itself exposes no `qualify`,
   `route_for_review`, `evaluate`, or `emit` method.
8. **Engine remains contract-clean and unwired.** `InspectionEngine` exposes no
   `predict`/provider attribute (`assert not hasattr(...)`), confirming the
   provider is not wired this task; the existing
   `test_inspection_engine_surface_does_not_expose_downstream_domains` stays green.
9. **Downstream tests remain green.** The full repo suite passes unchanged
   (`pytest -q`), and the integration/CLI suites are untouched.

Testing principles: small, focused tests; fixed inputs; no metric, accuracy, or
calibration assertion smuggled into the inspection domain (Inspection plan §11).

## 9. Integration Impact

- **None to `InspectionEngine`.** `engine.py` is not modified; the engine neither
  imports nor calls the provider, and continues to use `InspectionExaminer`.
- **None to the integration layer or CLI.** `src/integration/` and the CLI are not
  modified and do not reference the new objects.
- **None downstream.** Trust, Review, Evidence, and Evaluation read only
  `RawInspectionResult` and its evidence record; the new prediction objects are
  referenced by nothing in the runtime chain.
- **Public surface (additive only).** `src/inspection/__init__.py` adds
  `InspectionPrediction`, `InspectionInferenceProvider`,
  `InvalidInspectionPrediction`, `PartialInspectionPrediction`,
  `INSPECTION_PREDICTION_KIND`, and `PREDICTION_RAW_MEASURE_SCALE` to its imports
  and `__all__`. Nothing is removed or renamed.

## 10. Out of Scope

This plan does **not** authorize, and the implementation must not introduce:

- any model, model architecture, learned/tuned weights, or data-derived parameter;
- any ML framework, inference runtime, or new third-party dependency;
- any concrete `InspectionInferenceProvider` implementation (beyond a trivial
  in-test structural stub);
- wiring the provider into `InspectionEngine`, or any change to `engine.py`;
- transforming `InspectionPrediction` into `RawInspectionResult` (later task);
- the "model unavailable", "incompatible prediction version", or "inference
  non-reproducibility" failure modes (require wiring/execution; later tasks);
- training, datasets, hyperparameters, GPU/quantization, deployment, benchmarking,
  calibration, trust qualification, review routing, or evaluation of any kind;
- changes to `README.md`, prototype, `assets/`, the asset pipeline, integration,
  CLI, Trust, Review, Evidence, or Evaluation;
- live, streaming, scheduled, hosted, or continuously operating behavior.

## 11. Implementation Steps

> Each task is test-first (TDD). After each task, run the listed command and
> confirm the expected result. Commit points are **owner validation checkpoints**:
> report results and let the repository owner commit. Do not run git yourself.

### Task A: Add prediction error types

**Files:** Modify `src/inspection/errors.py`; Test `tests/test_inspection_engine.py`.

- [ ] **Step 1 — Failing test.** Append a test importing
  `InvalidInspectionPrediction` and `PartialInspectionPrediction` from
  `src.inspection` and asserting `issubclass(PartialInspectionPrediction,
  InvalidInspectionPrediction)` and `issubclass(InvalidInspectionPrediction,
  InspectionError)`.
- [ ] **Step 2 — Run, confirm `ImportError`.**
  `python3 -m pytest tests/test_inspection_engine.py -k prediction_error -q`
- [ ] **Step 3 — Implement.** Add `InvalidInspectionPrediction(InspectionError)`
  and `PartialInspectionPrediction(InvalidInspectionPrediction)` to `errors.py`
  (after `NonReproducibleInspection`).
- [ ] **Step 4 — Export.** Add both names to the `.errors` import block and
  `__all__` in `src/inspection/__init__.py`.
- [ ] **Step 5 — Run, confirm PASS.** Same command as Step 2.
- [ ] **Step 6 — Validation checkpoint.** Report; do not commit.

### Task B: Add the `InspectionPrediction` contract

**Files:** Modify `src/inspection/domain.py`, `src/inspection/__init__.py`;
Test `tests/test_inspection_engine.py`.

- [ ] **Step 1 — Failing tests.** Add the §8 tests #1–#5 (valid construction,
  invalid judgement, invalid localization, invalid raw measure, forbidden-field
  rejection/absence), importing `InspectionPrediction`,
  `INSPECTION_PREDICTION_KIND`, and `PREDICTION_RAW_MEASURE_SCALE`.
- [ ] **Step 2 — Run, confirm failure (`ImportError`).**
  `python3 -m pytest tests/test_inspection_engine.py -k inspection_prediction -q`
- [ ] **Step 3 — Implement.** Add `INSPECTION_PREDICTION_KIND` and
  `PREDICTION_RAW_MEASURE_SCALE` constants, then the frozen
  `InspectionPrediction` dataclass (§3 fields) with `__post_init__` (§5 rules),
  reusing `InspectionJudgement`, `DefectLocalization`, `_freeze_metadata`,
  `_is_forbidden_metadata_key`, `isfinite`, and `RAW_MEASURE_KIND`. Raise
  `InvalidInspectionPrediction` / `PartialInspectionPrediction` from
  `.errors`.
- [ ] **Step 4 — Export.** Add `InspectionPrediction`,
  `INSPECTION_PREDICTION_KIND`, `PREDICTION_RAW_MEASURE_SCALE` to the `.domain`
  imports and `__all__` in `src/inspection/__init__.py`.
- [ ] **Step 5 — Run, confirm PASS.** Same command as Step 2.
- [ ] **Step 6 — Validation checkpoint.** Report; do not commit.

### Task C: Add the `InspectionInferenceProvider` protocol

**Files:** Modify `src/inspection/interfaces.py`, `src/inspection/__init__.py`;
Test `tests/test_inspection_engine.py`.

- [ ] **Step 1 — Failing tests.** Add §8 tests #6–#8 (stub provider returns
  `InspectionPrediction`; no downstream surfaces; engine unwired), importing
  `InspectionInferenceProvider`.
- [ ] **Step 2 — Run, confirm `ImportError`.**
  `python3 -m pytest tests/test_inspection_engine.py -k inference_provider -q`
- [ ] **Step 3 — Implement.** Add the `InspectionInferenceProvider` `Protocol`
  (with `predict`) to `interfaces.py`, importing `InspectionPrediction` from
  `.domain`.
- [ ] **Step 4 — Export.** Add `InspectionInferenceProvider` to the `.interfaces`
  imports and `__all__` in `src/inspection/__init__.py`.
- [ ] **Step 5 — Run, confirm PASS.** Same command as Step 2.
- [ ] **Step 6 — Validation checkpoint.** Report; do not commit.

### Task D: Full verification

- [ ] **Step 1 — Inspection suite.**
  `python3 -m pytest tests/test_inspection_engine.py -q` → PASS (existing + new).
- [ ] **Step 2 — Downstream unchanged.**
  `python3 -m pytest tests/test_end_to_end_substrate_integration.py tests/test_integration_cli.py -q`
  → PASS.
- [ ] **Step 3 — Repo-wide + compile.**
  `python3 -m pytest -q` → PASS;
  `python3 -m compileall -q src tests` → exit 0.
- [ ] **Step 4 — Scope discipline.** `git status --short` shows only
  `src/inspection/domain.py`, `src/inspection/interfaces.py`,
  `src/inspection/errors.py`, `src/inspection/__init__.py`, and
  `tests/test_inspection_engine.py`. **No** change to `src/inspection/engine.py`,
  `src/trust/`, `src/review/`, `src/evidence/`, `src/evaluation/`,
  `src/integration/`, `scripts/`, `README.md`, `assets/`, or `tools/`.
- [ ] **Step 5 — Final validation checkpoint.** Report all results to the owner;
  the owner commits. Do not commit.

---

## Self-Review

- **Spec coverage:** purpose (§1), scope (§2), contract (§3), protocol (§4),
  validation (§5), forbidden fields (§6), failure modes (§7), tests (§8),
  integration impact (§9), out of scope (§10), implementation steps (§11) — all
  present.
- **Boundary rules honored:** the provider produces only `InspectionPrediction`;
  `RawInspectionResult` ownership stays with the engine; the prediction declares no
  `RawInspectionResult`/trust/evidence/evaluation/routing/score/confidence field
  and filters forbidden metadata.
- **Contract-only discipline:** `engine.py` is untouched (no wiring, no
  transformation); model-execution failure modes are deferred; the only test
  double is a structural stub, not a model.
- **Reuse over invention:** reuses `InspectionJudgement`, `DefectLocalization`,
  `NormalizedBoundingBox`, `_freeze_metadata`, `_is_forbidden_metadata_key`, the
  error hierarchy, and the test suite's `DOWNSTREAM_FIELD_NAMES` /
  `assert_no_downstream_fields` guards already in the repository.
- **Type consistency:** new constants `INSPECTION_PREDICTION_KIND` /
  `PREDICTION_RAW_MEASURE_SCALE` defined once and reused; `predict` returns
  `InspectionPrediction`; error names match between §7 and §11.
- **Placeholder scan:** no TBD/TODO; every step lists the exact command and
  expected result.
