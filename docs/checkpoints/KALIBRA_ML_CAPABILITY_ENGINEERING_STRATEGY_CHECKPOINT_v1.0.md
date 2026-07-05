# Kalibra ML Capability Engineering Strategy Checkpoint v1.0

**Status:** Recorded — strategic checkpoint (no sprint authorized)
**Date:** 2026-07-05
**Repository baseline HEAD:** `docs: close ml phase 2 sprint 1h`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the ML capability engineering roadmap determined after the
completion of ML Phase 2 Sprint 1H. It is a strategic record only. It authorizes no
sprint, implements no code, and modifies no ML runtime, provider, dataset,
evaluation, or authorization logic. It proposes nothing outside ML engineering and
scientific validation — no UI, SaaS, deployment, cloud, or commercialization scope.

## 1. Repository State / Baseline

The ML inference infrastructure is treated as substantially complete: the governed,
deterministic image → evaluation substrate is built and proven on real ONNX Runtime.
The placeholder identity model remains the only model. The binding constraint is now
scientific, not foundational. A decisive governance fact shapes the ordering below:
**no dataset has been finally selected or acquired** — the Dataset Selection ADR
records `DEFER`, with VisA as governance anchor and MPDD as domain anchor.

## 2. Decision Summary

Kalibra is entering **ML Capability Engineering**. The capability roadmap below
begins immediately after Sprint 1H. Numbering deliberately breaks from the `1x`
infrastructure series — that series is closed. The highest-value next phase is
**C-1 Dataset Selection Closure & Governed Acquisition**.

## 3. Recommended Phase 2 Capability Roadmap (C-1 … C-8)

### C-1 — Dataset Selection Closure & Governed Acquisition
- **Objective:** Convert the standing `DEFER` decision into a single *Selected*
  dataset (resolve remaining non-licensing governance gaps for VisA, or explicitly
  accept MPDD's non-commercial terms).
- **Engineering outcome:** Governed local dataset with provenance manifest, per-file
  sha256, license record, and an immutable train/validation/test split.
- **Scientific outcome:** A defensible ground-truth substrate exists for the first
  time; the inspection problem becomes measurable.
- **Dependencies:** Dataset Selection ADR, Data Strategy Decision Memo, governance
  investigations (complete).
- **Deliverable:** Selection ADR revision (Selected) + governed dataset artifact +
  split manifest.

### C-2 — Evaluation Protocol Fixation
- **Objective:** Bind concrete metrics, threshold policy, and the deterministic
  evaluation harness to the approved dataset.
- **Engineering outcome:** Reproducible evaluation harness consuming held-out splits;
  deterministic, hashed metric computation.
- **Scientific outcome:** Image-level and (where labels permit) region-level metrics
  are defined *before* a model exists, preventing metric-shopping.
- **Dependencies:** C-1.
- **Deliverable:** Evaluation Protocol spec + harness skeleton + frozen metric
  definitions.

### C-3 — Model Family Selection
- **Objective:** Select the concrete ML approach from the scientific-architecture
  candidate set (anomaly-detection family).
- **Engineering outcome:** Recorded model-family ADR with the selection rationale and
  trade-offs.
- **Scientific outcome:** A named, justified approach whose success is measurable
  under C-2.
- **Dependencies:** C-1 (data shape/labels), C-2 (measurability).
- **Deliverable:** Model-family ADR. *(See the Scientific Model Family Selection
  Checkpoint: PaDiM recommended as first family.)*

### C-4 — Training / Fitting
- **Objective:** Fit the selected model on the approved training split.
- **Engineering outcome:** Reproducible fitting run with pinned seeds, environment
  capture, and a fitted parameter set.
- **Scientific outcome:** First model that actually discriminates — replacing the
  identity placeholder's null behavior.
- **Dependencies:** C-3.
- **Deliverable:** Fitted model + fitting reproducibility record.

### C-5 — Deterministic ONNX Export & Governed Artifact
- **Objective:** Export the fitted model to a governed ONNX artifact and upgrade the
  toy tensor contract to a real image → tensor contract.
- **Engineering outcome:** New governed artifact passing existing loader / artifact /
  session validation; upgraded preprocessing and output-mapping contracts.
- **Scientific outcome:** The runtime executes a *learned* function end-to-end;
  determinism of the real artifact is proven.
- **Dependencies:** C-4.
- **Deliverable:** Governed real model artifact + revised contracts + export
  determinism evidence.

### C-6 — Model Integration
- **Objective:** Wire the real artifact through the untouched substrate.
- **Engineering outcome:** Placeholder retired; the real model is default; downstream
  engines consume real predictions with no substrate changes.
- **Scientific outcome:** The full image → evaluation chain carries genuine signal for
  the first time.
- **Dependencies:** C-5.
- **Deliverable:** Integrated inference path + end-to-end substrate evidence on real
  inputs.

### C-7 — Real Evaluation Baseline
- **Objective:** Execute C-2's harness on the held-out test split to produce
  Kalibra's first real accuracy baseline.
- **Engineering outcome:** Reproducible, hashed evaluation report.
- **Scientific outcome:** First honest performance figures; operating point selected
  on evidence rather than a hard-coded threshold.
- **Dependencies:** C-6.
- **Deliverable:** Real Evaluation Baseline report.

### C-8 — Calibration & Scientific Validation
- **Objective:** Calibrate confidence (Trust-domain, on the *calibrated* output — never
  the raw measure) and complete statistical validation, failure analysis, and
  claim-policy conformance.
- **Engineering outcome:** Calibration mapping + validation harness.
- **Scientific outcome:** Stated confidence matches observed reliability; claims are
  governed and defensible; drift posture established.
- **Dependencies:** C-7.
- **Deliverable:** Calibration + Scientific Validation report closing ML Phase 2 as a
  scientifically valid system.

## 4. Ordering Rationale

```text
dataset → protocol → model family → training/fitting → export/artifact →
integration → measurement → calibration/validation
```

- **Dataset first** — non-negotiable; the Selection ADR still reads `DEFER` and there
  is no selected data. Every downstream act is undefined without governed ground
  truth, and proceeding on an unselected dataset would violate the repository's own
  governance gate.
- **Protocol before model** — metrics and splits must be fixed before a model exists,
  or evaluation becomes post-hoc rationalization.
- **Family and training before export** — you cannot export what does not exist, nor
  integrate what is not exported; the toy tensor contract must be replaced at export
  time because a real model forces a real input/output shape.
- **Measurement after integration** — a real baseline requires the real artifact
  running through the real substrate; measuring the placeholder is meaningless.
- **Calibration and validation last** — calibration operates on calibrated confidence,
  which requires a fitted model, real outputs, and a measured baseline; doing it
  earlier would fabricate confidence from an ungrounded raw measure.

The dependency chain is strict and acyclic; no stage can be honestly begun before its
predecessor completes.

## 5. Highest-Value Next Phase

**C-1 — Dataset Selection Closure & Governed Acquisition.** One choice, no hedge.
The entire capability chain is blocked on a single missing input: an approved,
acquired, governed dataset. It is also the only phase that is a decision-and-
governance problem rather than a modeling problem, so it can start now while
everything else cannot.

## 6. Scope Boundaries and Explicit Non-Claims

- This checkpoint authorizes no sprint and changes no code or governed logic.
- No UI, SaaS, deployment, cloud, or commercialization scope is proposed.
- The placeholder model's behavior is **not** a scientific result.
- Kalibra does **not** yet perform real defect detection, and no product-readiness
  claim is made.

## 7. Readiness Decision

Kalibra is entering **ML Capability Engineering**. ML Infrastructure Engineering is
closed. The first capability act is **not model training — it is dataset selection
closure (C-1)**, because the repository's governance state forbids proceeding on an
unselected dataset.

## 8. Next Natural Step

Proceed to the Scientific Model Family Selection Checkpoint, which fixes the first
real model family to replace the placeholder. See
[KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md).
