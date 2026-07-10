# ML Architecture and Capability

**Date:** 2026-07-05

## 1. Repository State / Baseline

The completed engineering baseline assumed by this record (all PASS):

- Sprint 0 — Provider Conformance
- Sprint 1A — ONNX Runtime Substrate
- Sprint 1B — ONNX Session Substrate
- Sprint 1C — ONNX-backed Provider
- Sprint 1D — Governed Model Artifact
- Sprint 1E — Deterministic Model Loader
- Sprint 1F — Loader Hardening + Provider Wiring
- Real ONNX Runtime Evidence
- Sprint 1G — Deterministic Image Preprocessing
- Sprint 1H — Governed Model Output Mapping

The runtime executes the full governed inference chain:

```text
Image → Deterministic Preprocessing → Tensor Contract → Governed Model Artifact →
Deterministic Model Loader → ONNX Runtime → Governed Output Mapping →
InspectionPrediction → InspectionEngine.transform_prediction(...) →
RawInspectionResult → Trust → Review → Evidence → Evaluation
```

The **placeholder identity model remains the only model** at the center of this chain.

## 2. Architecture Maturity Assessment

The inference chain is **internally complete and structurally sound**. Every stage
exists as real, governed, deterministic code — not stubs:

- **Provider boundary** — mature; the runtime is isolated behind `predict()` and the
  session is provider-private.
- **Preprocessing** — mature as a governed contract, degenerate as vision; it accepts
  only a 4×4 PGM image reduced to a single float32 scalar.
- **Loader** — mature; fingerprinted artifact, session-configuration hash,
  compatibility validation.
- **Runtime** — real; ONNX Runtime executes a real session, corroborated by the Real
  ONNX Runtime Evidence.
- **Output mapping** — mature as a governed contract; a single scalar is thresholded
  into `ok` / `defect`, and localization is currently synthesized deterministically
  rather than model-derived.
- **Deterministic replay** — mature; sha256 content hashing, frozen dataclasses, and
  configuration hashing throughout.
- **Governance** — mature; artifact identity/version/format allow-lists, contract
  ids, semantic-version validation.
- **Downstream ownership** — mature; clean handoff through
  `InspectionPrediction → transform_prediction → RawInspectionResult → Trust →
  Review → Evidence → Evaluation`.

**Conclusion:** the architecture is internally complete. There are no missing boxes
in the inference diagram.

## 3. Current Capability Assessment

These capability classes are kept strictly separate and must not be conflated.

- **Engineering capability — HIGH.** A production-grade, contract-bound,
  deterministic, fully tested inference substrate. This is the strongest asset in
  the repository.
- **Runtime capability — REAL.** ONNX Runtime genuinely loads and executes a session
  end-to-end, with recorded real-runtime evidence. It is not mocked.
- **Scientific capability — EFFECTIVELY ZERO (while the placeholder identity model
  remains).** The model is an identity graph: output equals input. There are no
  learned parameters, no dataset, no ground-truth labels, and no accuracy /
  precision / recall / calibration measurement.
- **Product capability — NONE.** Nothing in the system can detect a defect on a real
  part. Any prototype surface is projection only.

## 4. Remaining Gaps

- **Blocker — no learned model.** The placeholder is an identity function; the system
  cannot discriminate defect from non-defect on any real input.
- **Blocker — no dataset ingested or selected.** Dataset candidates exist in
  documentation, but no data is present or wired.
- **High — toy input contract.** The 4×4 PGM / single-scalar tensor contract cannot
  represent a real inspection image.
- **High — no real evaluation against ground truth.** There is no accuracy,
  confusion matrix, or evidence-based operating point.
- **Medium — no calibration / confidence semantics** grounded in evidence.
- **Low — synthetic localization semantics** carry no learned meaning yet.

## 5. Infrastructure Completion Decision

The ML inference **infrastructure is substantially complete**. The governed,
deterministic, replayable path from image to evaluation is built, wired, and
evidenced. The remaining work is **scientific payload, not foundational substrate**.
No further substrate sprints are required to reach real inference; the pipeline is
ready to receive a real model, real data, and a real input contract.

## 6. Next Strategic Engineering Problem

The single largest remaining capability gap is the **absence of a real, learned model
trained on a real governed dataset and measured by a real evaluation** — currently
masked by the placeholder identity graph. Every other gap (input width, tensor
shape, threshold semantics, calibration) is downstream of that one gap.

## 7. Scope Boundaries and Explicit Non-Claims

- This record approves no sprint and changes no code or governed logic.
- The placeholder model's behavior is **not** a scientific result.
- Kalibra does **not** yet perform real defect detection.
- No product-readiness claim is made or implied.

## 8. Readiness Decision

**Kalibra is ready to transition from infrastructure engineering to ML capability
engineering.** The substrate is complete enough to carry real inference; the
placeholder model is now the binding constraint, and it is a modeling and data
problem, not an engineering-substrate problem.

## 9. Next Natural Step

Proceed to the public ML capability evidence sequence documented in
`docs/engineering/DATASET_SELECTION_RATIONALE.md`,
`docs/engineering/MODEL_FAMILY_SELECTION.md`, and
`docs/engineering/ML_CAPABILITY_MILESTONE.md`.
