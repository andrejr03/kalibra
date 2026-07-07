# Kalibra Runtime Provider Integration Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no runtime integration performed, no provider modified, no model loader modified, no output mapping modified, no preprocessing modified, no feature extraction modified, no placeholder retired, no runtime inference executed, no evaluation, no calibration, no evidence file produced)
**Date:** 2026-07-07
**Repository baseline tag:** `ml-phase-2-complete`
**Repository baseline HEAD:** `a9743b4 docs: review ml phase 2 documentation`
**Architecture baseline:** [ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md)
**Previous capability:** Phase 3 / Task 2 — Export Equivalence Verification (complete)
**Review HEAD:** `5171483 feat: verify governed onnx export equivalence`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **Phase 3 / Task 3 — Runtime
Provider Integration** implementation. It is authorization planning only. It modifies no
runtime, modifies no provider, modifies no model loader, modifies no output mapping,
modifies no preprocessing, modifies no feature extraction, retires no placeholder, runs no
runtime inference, runs no evaluation, calibrates nothing, and modifies no ADR, Strategy,
Evaluation Strategy, Implementation Authorization, or any normative document.

It draws its authority from the now-normative decisions recorded in the

- [Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
  (PaDiM selected first; PatchCore reserved second),
- [Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) §8,
- [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
  (`SELECTED — VisA`),
- [Evaluation Strategy](../KALIBRA_EVALUATION_METHODOLOGY_v1.0.md)
  (provider / prediction boundary; raw-anomaly-measure boundary),
- [C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
- [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
- [Governed VisA Acquisition Evidence](../evidence/KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md),
- [C-4 PaDiM Baseline Training Authorization Checkpoint](KALIBRA_PADIM_BASELINE_TRAINING_AUTHORIZATION_CHECKPOINT_v1.0.md),
- [C-4 PaDiM Baseline Training Completion Checkpoint](KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md),
- [PaDiM Baseline Training Evidence](../evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md),
- [C-5 Governed PaDiM Inference Authorization Checkpoint](KALIBRA_GOVERNED_PADIM_INFERENCE_AUTHORIZATION_CHECKPOINT_v1.0.md),
- [C-5 Governed PaDiM Inference Completion Checkpoint](KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md),
- [C-6 Scientific Evaluation Completion Checkpoint](KALIBRA_C6_SCIENTIFIC_EVALUATION_COMPLETION_CHECKPOINT_v1.0.md),
- [Scientific Evaluation Evidence](../evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md),
- [Governed PaDiM ONNX Export Authorization Checkpoint](KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_AUTHORIZATION_CHECKPOINT_v1.0.md),
- [Governed PaDiM ONNX Export Completion Checkpoint](KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_COMPLETION_CHECKPOINT_v1.0.md),
- [Governed PaDiM ONNX Export Evidence](../evidence/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md),
- [PaDiM ONNX Export Equivalence Authorization Checkpoint](KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_AUTHORIZATION_CHECKPOINT_v1.0.md),
- [PaDiM ONNX Export Equivalence Completion Checkpoint](KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_COMPLETION_CHECKPOINT_v1.0.md),
- [PaDiM ONNX Export Equivalence Evidence](../evidence/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md),

and from the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md),
which establishes Phase 3's objective, scope, and ordering — and explicitly places
**runtime provider integration** as capability #3 of §6, immediately after the governed
export (capability #1, complete) and the offline export-equivalence verification
(capability #2, complete), and before end-to-end runtime equivalence (capability #4) and
placeholder retirement (capability #5). The phase-opening checkpoint names R1 (inference
equivalence), R4 (replay integrity across the runtime boundary), R5 (runtime determinism),
and R6 (governance continuity) as the dominant risks for this capability, and prescribes
that each Phase 3 capability remain behind its own separate authorization gate before
implementation.

This checkpoint defines **what a future runtime-provider-integration sprint is allowed to
do**, what it is **forbidden** to do, what it must **produce**, and how it must be
**validated**. It does not perform the sprint. It is equivalent in standing to the C-1,
C-2, and C-3 checkpoints, the Governed VisA Acquisition Authorization checkpoint, the C-4
PaDiM Baseline Training Authorization checkpoint, the C-5 Governed PaDiM Inference
Authorization checkpoint, the Governed PaDiM ONNX Export Authorization checkpoint, and the
PaDiM ONNX Export Equivalence Authorization checkpoint, and must be reviewed before any
implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents, the Phase 3 architecture checkpoint, and
the Task 1 / Task 2 authorization checkpoints.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Runtime Provider Integration
```

The authorization is **strictly limited to loading the governed, equivalence-verified ONNX
artifact through the existing runtime substrate so that the canonical runtime path consumes
the governed PaDiM artifact instead of the placeholder boundary model — under governance
(hash-anchored identity, fail-closed validation, deterministic configuration, replay
verification), with the provider seam, the `InspectionPrediction` contract shape, and the
`InspectionEngine.transform_prediction()` path preserved, and with governed runtime
integration evidence.** It grants no permission to verify runtime equivalence against C-6
(that is capability #4), to perform end-to-end runtime equivalence, to change Trust, Review,
Evidence, or Evaluation ownership, to calibrate, to generate benchmarks, or to make any
scientific or product claim.

**Basis for readiness — why the repository is now technically ready:**

- **The governed, equivalence-verified ONNX artifact exists and is hash-anchored.** Phase 3 /
  Task 1 produced `artifacts/padim/model.onnx` (SHA-256
  `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`, opset 18, IR 10,
  model reference id `kalibra-padim-onnx-export-v1`), and Phase 3 / Task 2 proved that this
  artifact reproduces the governed offline C-5 PaDiM computation across all 6,492 samples at
  machine-epsilon deviation (max anomaly-map abs/rel `7.1e-15 / 3.6e-15`; max raw-measure
  abs/rel `7.1e-15 / 3.6e-15`; max localization abs `0.0`), well inside the pre-declared
  `{1e-12, 1e-12, 0.0}` tolerance, with byte-identical deterministic replay. Runtime
  integration therefore has a real, integrity-anchored, equivalence-proven artifact to load.

- **The real ONNX Runtime substrate exists and is proven.** `model_loader.load_governed_model`,
  `onnx_session`, `onnx_runtime`, and the `ProviderPrivateInferenceSession` machinery in
  `src/frameworks/` construct and drive a genuine `InferenceSession`, with hash-anchored
  artifact validation, fingerprint enforcement, compatibility validation, pinned
  single-threaded `CPUExecutionProvider` session options, and fail-closed behavior on every
  mismatch. This substrate is production-grade, deterministic, and ready to receive a real
  model; it is only fed the placeholder today.

- **The provider seam and the prediction contract exist and are contract-bound.** The
  `InspectionInferenceProvider.predict → InspectionPrediction →
  InspectionEngine.transform_prediction → RawInspectionResult → Trust → Review → Evidence →
  Evaluation` chain is live and contract-bound. The `InspectionPrediction` contract
  (`input_id`, `prediction_id`, `predicted_judgement`, `predicted_raw_anomaly_measure`,
  `predicted_localization`, `raw_measure_kind`, `raw_measure_scale`, `prediction_kind`,
  `model_metadata`) is the stable boundary across which a real model's output must be
  carried. Integration populates this seam; it does not redesign it.

- **The runtime already carries model-sourced signal through the contract (via a non-ONNX
  provider).** `LocalArtifactInferenceProvider` already produces an `InspectionPrediction`
  and feeds `InspectionEngine.transform_prediction()` in `src/integration/engine.py`. The
  model → prediction → result path is therefore exercised end-to-end today; Task 3 extends
  this from a PGM-contrast fixture provider to the governed ONNX artifact, behind the same
  contract boundary.

- **Runtime integration is the prerequisite for everything downstream in Phase 3, and
  nothing downstream is authorized by performing it.** Per Phase 3 §6, runtime provider
  integration is capability #3 precisely because end-to-end runtime equivalence (#4) and
  placeholder retirement (#5) presuppose that the runtime loads and executes the real
  governed artifact. Authorizing this integration unblocks that ordering without authorizing
  runtime-equivalence verification, placeholder retirement, or any claim beyond C-6.

**Honest qualification of the change surface.** The phase-opening architecture checkpoint
(§4.2) described the integration change surface as deliberately minimal and seam-local. A
direct code review of the runtime substrate, performed for this authorization, confirms the
*locations* identified there (the ONNX provider, the model loader path, the output mapping,
and the placeholder restriction) but also surfaces — honestly — that the placeholder seam is
**structurally specialized to the placeholder model** and is **not a drop-in receptor** for
the governed PaDiM artifact:

- the ONNX provider is hard-restricted to `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID`
  (`providers_onnx.py`) and enforces **exactly one input** via `_single_input_name`;
- the placeholder model is a 1-input / 1-output `Identity` graph over a single float32
  scalar, whereas the governed PaDiM graph exposes **two** inputs
  (`full_patch_features[1,64,14] float64`, `class_index[1] int64`) and **four** outputs
  (patch distances, anomaly map, raw measure, argmax region, all float64);
- the output mapping (`output_mapping.py`) expects exactly **one float32 output** in the
  range `[0.0, 100.0]` with scale `placeholder_output_raw_0_100`, whereas the PaDiM raw
  measure is an unbounded float64 Mahalanobis distance and the localization is a four-value
  normalized region;
- the runtime image preprocessing
  (`kalibra-pgm-p2-fixed-4x4-weighted-projection-v1`, a 4×4 PGM → single luminance scalar)
  does **not** produce the PaDiM feature tensor the graph consumes
  (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`, RGB 64×64 → 64 patches × 14 features);
  the governed graph explicitly does **not** reimplement preprocessing and takes the
  deterministic full-patch feature tensor as its input contract.

This means Task 3 is a genuine **integration-engineering** task — it must adapt the existing
substrate to the governed artifact's real contract **without** breaching the forbidden
boundaries in §3 and **without** expanding the scientific claim. The authorization below is
written to permit exactly that adaptation, bounded and governed, while forbidding every form
of drift the phase-opening checkpoint warns against. Where the substrate must change, it
must change by **populating the existing seam under governance**, not by creating a new
domain, a new seam shape, or a new prediction contract.

Readiness is **for runtime provider integration only**. Runtime-equivalence verification,
placeholder retirement from the canonical flow, calibration, and any scientific or product
claim each remain behind their own separate authorization gates.

---

## 2. Authorized Scope

If and when the runtime-provider-integration sprint is authorized by a bounded
implementation prompt, it may do **only** the following:

- **loading the governed ONNX artifact through the existing runtime substrate** — load
  `artifacts/padim/model.onnx` only after verifying its recorded SHA-256
  (`0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`) against the Task 1 /
  Task 2 governed records, via the existing `model_loader.load_governed_model` /
  `ProviderPrivateInferenceSession` substrate, with the governed `OnnxSessionConfiguration`
  (pinned `CPUExecutionProvider`, single-threaded, `ORT_DISABLE_ALL`), failing closed on any
  hash, fingerprint, identity, version, or compatibility mismatch;

- **replacing the placeholder model reference with the governed model reference** — replace
  the hard restriction to `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID`
  (`onnx-placeholder-boundary-model-v1`) with a governed acceptance of the real model
  reference id `kalibra-padim-onnx-export-v1` (and its recorded content hash), under
  governance, so the provider loads and executes the governed PaDiM artifact. The placeholder
  restriction is lifted **under governance** for the canonical runtime path; placeholder
  retirement from the live flow is a separate, later capability (#5) and is **not** authorized
  here beyond what is required to make the canonical path consume the governed artifact;

- **provider wiring** — adapt `OnnxInspectionInferenceProvider` (or introduce a governed
  provider that occupies the same seam) so it feeds the governed graph's actual input
  contract (the deterministic full-patch feature tensor and the governed `class_index`) to the
  loaded session and runs it, producing an `InspectionPrediction` that satisfies the existing
  contract shape. The provider seam (`InspectionInferenceProvider.predict →
  InspectionPrediction`) must remain the integration boundary;

- **model-loader wiring** — use the existing `model_loader.load_governed_model` path to load
  the governed artifact; the loader's validation, fingerprint, compatibility, and session
  machinery must be reused, not bypassed. The loader already constructs a real
  `InferenceSession` behind `ProviderPrivateInferenceSession`; integration wires the governed
  artifact into that path;

- **runtime artifact identity verification** — verify, at integration time, that the loaded
  artifact's identity, version, content hash, opset (18), IR (10), and framework version
  match the governed Task 1 records, and record them in the runtime integration metadata;
  fail closed on any mismatch;

- **runtime replay verification** — prove that a complete second load + execution of the
  integrated runtime path over governed inputs reproduces identical outputs, identical
  session configuration, and identical artifact identity, recorded in a governed runtime
  replay record, matching the Phase 2 / Phase 3 replay standard;

- **governed runtime integration evidence** — produce a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating that the governed
  artifact is loaded, the provider uses the governed artifact, the model loader uses the
  governed artifact, the placeholder is no longer used on the canonical runtime path, the
  runtime configuration is deterministic, replay is deterministic, no downstream domain was
  modified, and the explicit non-claims hold.

Nothing beyond this list is authorized. In particular: **no runtime-equivalence verification
against C-6, no end-to-end runtime equivalence, no calibration, no Trust/Review/Evidence/
Evaluation change, no scientific or product claim.**

The runtime-equivalence question — "does the canonical `inspect()` path reproduce the offline
C-6 result?" — is explicitly **deferred** to capability #4. Task 3 makes the runtime
*consume* the governed artifact; it does not yet *prove* that the integrated path is
equivalent to C-6 end-to-end. That proof is a separately authorized capability with its own
tolerance, per-class evidence, and replay obligations.

---

## 3. Forbidden Scope

The runtime-provider-integration sprint **must not**, under any circumstances, perform or
produce:

- **runtime-equivalence verification** — Task 3 must not measure the integrated runtime path
  against the C-6 scientific result, must not compute Image AUROC / Pixel AUROC / AUPRO /
  Precision / Recall / F1 over the runtime path, and must not assert runtime equivalence to
  the offline signal. Runtime equivalence is capability #4, separately authorized;

- **end-to-end runtime equivalence** — Task 3 must not run the full canonical
  `inspect() → Trust → Review → Evidence → Evaluation` chain for scientific measurement
  against C-6; it wires the provider and proves deterministic load/replay, not scientific
  equivalence;

- **preprocessing changes** (no modification to `src/frameworks/image_preprocessing.py` or
  its contract `kalibra-pgm-p2-fixed-4x4-weighted-projection-v1`) — the PaDiM graph consumes
  the deterministic full-patch feature tensor, not runtime-preprocessed pixels; the
  preprocessing boundary is fixed. If feature tensors are required at the provider seam, they
  must be produced by the **existing offline feature extractor** path under governance, not
  by altering runtime image preprocessing;

- **feature extraction changes** (no modification to the deterministic feature extraction
  path; the feature indices `[0, 2, 5, 6, 7, 9, 12, 13]`, layer, and backbone are fixed by
  C-4 and embedded unchanged in the governed graph) — integration must reuse the existing
  feature extraction, not redefine it;

- **output mapping redesign** (no modification to `MappedModelOutput` / `MappedLocalization`
  field shapes; the `InspectionPrediction` → `RawInspectionResult` mapping semantics must be
  preserved) — the runtime raw-measure scale and localization kind may be updated under
  governance to carry the real PaDiM semantics (`padim_anomaly_map_max_v1`,
  `padim_raw_anomaly_map_argmax_region_v1`), but the mapping **contract shape** must remain
  unchanged; the placeholder scale `placeholder_output_raw_0_100` is replaced under
  governance, not silently widened;

- **prediction contract changes** (no modification to the `InspectionPrediction` field set,
  field types, field validation, `prediction_kind`, or `raw_measure_kind` literals) — the
  prediction boundary is the integration's immovable seam; a real model's output must be
  carried **through** the existing contract, not by expanding it;

- **Trust changes** (no Trust-domain modification; no calibrated or qualified trust statement
  is produced; trust qualification remains deferred);

- **Review changes** (no Review-domain modification; no review routing is produced);

- **Evidence changes** (no Evidence-domain modification; the Evidence Engine's emitter,
  records, and hash-anchoring contract are unchanged — Task 3 produces its own integration
  evidence document, it does not alter the Evidence domain);

- **Evaluation changes** (no modification to `scripts/scientific_evaluation.py` or the C-6
  evaluation harness; integration is **not** evaluation);

- **calibration** (no calibrated confidence, no threshold tuning against C-6, no operating
  point selection, no abstention);

- **benchmark generation** (no benchmark suite, no multi-dataset claim, no generality claim);

- **scientific claims** (no claim that Kalibra detects defects at runtime, no claim of
  product-readiness, no claim of generality, no multi-seed claim; the scientific claim
  boundary remains exactly C-6's — single-seed, VisA-proxy, no calibration, no confidence,
  no product-readiness);

- **product claims** (no product-facing capability, no deployment, no live/streaming/
  hosted behavior, no operational alerting);

- **placeholder retirement from the canonical flow beyond what is required to consume the
  governed artifact** — full placeholder retirement (removal from the live path, fixture-only
  retention) is capability #5, separately authorized. Task 3 may make the canonical path
  consume the governed artifact; it must not delete the placeholder fixture or alter
  placeholder-gated tests except as strictly required to demonstrate the canonical path now
  uses the real artifact;

- **re-export or re-fit** (the governed `model.onnx` is the *input* to integration, not an
  output; the C-4 fit and the C-5 reference are *consumed*, not regenerated; no governed
  source artifact in `data/visa/derived/` may be mutated);

- **architecture changes** (no new domain, contract, seam, or domain responsibility; no
  rewiring of the canonical Inspection → Trust → Review → Evidence → Evaluation flow).

Any of these would exceed the runtime-provider-integration boundary and requires its own
separate authorization gate. The provider seam, the `InspectionPrediction` contract, and the
`InspectionEngine.transform_prediction()` path must be preserved; integration populates the
existing architecture, it does not redesign it.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
artifacts/runtime/
  integration_metadata.json   # governed runtime integration record
  runtime_replay.json         # governed runtime replay record (second load == first)
  runtime_hashes.json         # hashes of every governed runtime integration record
docs/evidence/                # committed governed runtime integration evidence report
```

Required artifacts:

- **`integration_metadata.json`** — the governed runtime integration record: the loaded
  governed artifact identity (`model.onnx` SHA-256, model reference id
  `kalibra-padim-onnx-export-v1`, opset 18, IR 10, framework version), the governed
  `OnnxSessionConfiguration` actually used (execution provider `CPUExecutionProvider`,
  single-threaded, `ORT_DISABLE_ALL`, exact-order provider policy), the session configuration
  hash, the consumed governed provenance (C-4 / C-5 / Task 1 / Task 2 identity hashes), the
  provider wiring record (which provider occupies the seam, the model reference it loads, the
  placeholder reference it replaces), the model-loader wiring record (loader path, fingerprint
  validation result, compatibility validation result), the runtime artifact identity
  verification result, the pass/fail status, and the machine-readable `scope_boundaries`
  block with every forbidden-scope flag set to `false`;

- **`runtime_replay.json`** — the governed runtime replay record confirming that a second
  load + execution of the integrated runtime path over governed inputs reproduced identical
  outputs, identical session configuration, identical artifact identity, and identical
  integration status, with per-record hash agreement and `status: passed`;

- **`runtime_hashes.json`** — hashes of every governed runtime integration artifact
  (`integration_metadata.json` content hash plus the hash of `runtime_replay.json`), so an
  observer can verify integrity without re-running;

- **governed runtime integration evidence report** — a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating artifact loading,
  provider wiring, model-loader wiring, runtime artifact identity verification, runtime
  replay, placeholder-no-longer-used on the canonical path, deterministic configuration,
  governed provenance continuity (C-3 → C-4 → C-5 → ONNX artifact → equivalence record →
  runtime integration record), no downstream domain modified, and the explicit non-claims.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `artifacts/runtime/integration_metadata.json` | **Committed** — reviewable governed integration record |
| `artifacts/runtime/runtime_replay.json` | **Committed** — reviewable replay proof |
| `artifacts/runtime/runtime_hashes.json` | **Committed** — integrity anchor |
| `docs/evidence/` runtime integration evidence report | **Committed** — evidence of a clean, reproducible, governed integration |
| integration script(s) under `scripts/` | **Committed** — reviewable text |
| integration tests under `tests/` | **Committed** — reviewable text |
| modified runtime source under `src/` (provider, loader path, mapping scale/kind) | **Committed** — reviewable text, in-scope per §2 only |

All runtime-integration outputs are reviewable JSON / Markdown / Python text; no large binary
is produced by this sprint (the governed `model.onnx` already exists from Task 1 and is not
reproduced). No `.gitignore` change is anticipated; any `.gitignore` update is authorized
**only if strictly required**, minimal, and scoped.

---

## 5. Validation Requirements

The runtime-provider-integration sprint must validate, and its evidence report must
demonstrate, that:

- **the governed ONNX artifact is loaded** — the integrated runtime loads
  `artifacts/padim/model.onnx` via `model_loader.load_governed_model`, verifies its SHA-256
  (`0437ae28…741a`), identity (`kalibra-padim-onnx-export-v1`), opset (18), and IR (10)
  against the governed records, and fails closed on any mismatch;

- **the provider uses the governed artifact** — `OnnxInspectionInferenceProvider` (or its
  governed successor occupying the same seam) loads and executes the governed PaDiM artifact,
  not the placeholder; the loaded model reference id is
  `kalibra-padim-onnx-export-v1`, not `onnx-placeholder-boundary-model-v1`;

- **the model loader uses the governed artifact** — the loader's validation, fingerprint,
  compatibility, and session-construction path are exercised against the governed artifact;
  the `ProviderPrivateInferenceSession` is constructed from the governed `model.onnx`;

- **the placeholder is no longer used on the canonical runtime path** — the canonical runtime
  path that previously executed the placeholder boundary model now consumes the governed
  PaDiM artifact; the placeholder reference id is not the model loaded by the canonical
  runtime provider. (Full placeholder fixture retirement is capability #5; Task 3 need only
  prove the canonical path no longer uses it.);

- **the runtime configuration is deterministic** — the `OnnxSessionConfiguration` is pinned
  (`CPUExecutionProvider`, single-threaded intra/inter, `ORT_DISABLE_ALL`, exact-order
  provider policy), hash-anchored, and recorded in `integration_metadata.json`;

- **replay is deterministic** — a complete second load + execution of the integrated runtime
  path over governed inputs reproduces identical outputs, identical session configuration,
  identical artifact identity, and identical integration status, recorded in
  `runtime_replay.json` with per-record hash agreement and `status: passed`;

- **no downstream domain is modified** — `git status --short --` over `src/trust`,
  `src/review`, `src/evidence`, `src/evaluation`, and `src/integration` (the downstream
  domain wiring) produces no output that changes domain ownership or the canonical flow; the
  provider seam, the `InspectionPrediction` contract, and
  `InspectionEngine.transform_prediction()` are unchanged in shape;

- **governed provenance continuity is intact** — the hash-anchored chain extends unbroken
  from the C-3 acquisition through the C-4 fit, the C-5 reference, the Task 1 ONNX artifact,
  and the Task 2 equivalence record into the runtime integration record.

The evidence must record the integration toolchain versions (python, numpy, onnx,
onnxruntime) and the runtime execution provider, matching the Phase 2 / Phase 3 evidence
idiom.

---

## 6. Integration Policy

The sprint must verify, explicitly and fail-closed, that the integration **populates the
existing architecture rather than redesigning it**:

- **the provider seam remains unchanged** — `InspectionInferenceProvider.predict` remains the
  boundary; a real model's output is carried through `predict()`, not around it. Whether the
  existing `OnnxInspectionInferenceProvider` is adapted or a governed successor occupies the
  seam, the seam itself (provider → `InspectionPrediction`) is preserved;

- **the `InspectionPrediction` contract remains unchanged** — the field set
  (`input_id`, `prediction_id`, `predicted_judgement`, `predicted_raw_anomaly_measure`,
  `predicted_localization`, `raw_measure_kind`, `raw_measure_scale`, `prediction_kind`,
  `model_metadata`), the field types, the validation rules, and the `prediction_kind` /
  `raw_measure_kind` literals are preserved. A real model's raw measure and localization are
  carried **through** these fields, not by adding new ones;

- **`InspectionEngine.transform_prediction()` remains unchanged** — the transformation from
  `InspectionPrediction` to `RawInspectionResult` + `InspectionEvidenceRecord` is preserved;
  integration does not alter the engine's validation, assembly, or evidence emission;

- **Trust ownership unchanged** — no calibrated or qualified trust statement is produced;
  Trust remains deferred;

- **Review ownership unchanged** — no review routing is produced;

- **Evidence ownership unchanged** — the Evidence Engine's emitter, records, and
  hash-anchoring contract are unchanged; Task 3 produces its own integration evidence
  document but does not alter the Evidence domain;

- **Evaluation ownership unchanged** — the C-6 evaluation harness and protocol are
  unchanged; integration is not evaluation.

If the implementation finds itself needing to change any of these, that is a red flag that
the integration has drifted into re-architecture and must stop and be re-reviewed, per the
phase-opening checkpoint §4.1. Integration must populate the existing architecture, not
redesign it.

---

## 7. Scientific Boundaries

Explicitly:

- **Runtime integration is not runtime equivalence.** Wiring the governed artifact into the
  runtime provider and proving deterministic load/replay is not proving that the canonical
  runtime path reproduces the offline C-6 result. Runtime-equivalence verification is the
  objective of a later, separately authorized capability (Phase 3 §6 #4). Task 3 makes the
  runtime *consume* the governed artifact; it does not yet *prove equivalence* end-to-end.

- **Runtime integration is not scientific evaluation.** No Image AUROC, Pixel AUROC, AUPRO,
  Precision, Recall, F1, or any aggregate score is produced or implied. The C-6 scientific
  evaluation is the *reference of record*; it is not recomputed, extended, or replaced here.

- **Runtime integration produces no new scientific claim.** Its purpose is solely to make the
  canonical runtime consume the already-validated, already-equivalence-verified governed ONNX
  artifact. It does not prove that Kalibra detects defects (that is C-6's bounded,
  single-seed, VisA-proxy claim, unchanged), does not prove product-readiness, calibration
  quality, drift response, or generality. The scientific claim boundary remains exactly C-6's
  — single-seed, VisA-proxy, no calibration, no confidence, no product-readiness — and this
  checkpoint makes no claim beyond it.

- **Runtime integration does not prove the integrated path is correct end-to-end.** It proves
  the governed artifact is loaded, the provider uses it, the configuration is deterministic,
  and replay is deterministic. Proving the integrated path carries the *right* signal
  end-to-end (equivalent to C-6) is capability #4.

Kalibra does **not** yet perform real defect detection at runtime as a *proven, measured*
property of the integrated path, and this checkpoint does not change that. It authorizes
making the runtime consume the real governed artifact; the proof that this consumption is
equivalent to the validated offline signal is a separate, later gate.

---

## 8. Readiness Decision

```text
READY — the repository is ready for a bounded Phase 3 / Task 3 — Runtime Provider
Integration implementation prompt.

- Authorized scope: governed ONNX artifact loading through the existing runtime substrate +
  placeholder reference replacement with the governed model reference + provider wiring +
  model-loader wiring + runtime artifact identity verification + runtime replay verification
  + governed runtime integration evidence only.
- Forbidden scope: runtime-equivalence verification, end-to-end runtime equivalence,
  preprocessing changes, feature extraction changes, output mapping redesign, prediction
  contract changes, Trust/Review/Evidence/Evaluation changes, calibration, benchmark
  generation, scientific and product claims, placeholder retirement beyond canonical-path
  consumption, re-export, re-fit, and any architecture change.
- Required outputs, commit policy, validation requirements, integration policy, and
  scientific boundaries are defined.
- Honest change-surface qualification: the placeholder seam is structurally specialized to
  the placeholder model (1 input / 1 output, float32 scalar, [0,100] range, PGM-4×4
  preprocessing); the governed PaDiM graph has a different contract (2 inputs / 4 outputs,
  float64, unbounded Mahalanobis measure, feature-tensor input). Task 3 is genuine
  integration engineering to adapt the substrate to the governed artifact under governance,
  not a drop-in reference swap.
- Nothing integrated, loaded, wired, evaluated, calibrated, or claimed by this checkpoint.
- No normative document modified.
```

---

## 9. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no runtime integration** (no provider modified, no model loader modified, no output
  mapping modified, no artifact loaded, no session constructed);
- **no placeholder retired** (the placeholder fixture and its tests are untouched; only the
  canonical runtime path's consumption is in scope for the future sprint);
- **no runtime modification** (`providers_onnx.py`, `model_loader.py`, `onnx_session.py`,
  `onnx_runtime.py`, `output_mapping.py`, `image_preprocessing.py`, `domain.py`,
  `transform_prediction`, `engine.py`, `src/integration/` all unchanged by this checkpoint);
- **no provider loaded** (no `InspectionInferenceProvider`, no `OnnxInspectionInferenceProvider`
  instantiated);
- **no runtime inference** (no runtime execution of the governed artifact);
- **no runtime-equivalence verification** (no comparison against C-6);
- **no evaluation / metric / benchmark**;
- **no calibration**;
- **no scientific or product claim** beyond the C-6 single-seed VisA-proxy boundary;
- **no re-export or re-fit** (the `model.onnx` and the C-4 / C-5 artifacts are inputs, not
  outputs);
- **no documentation modified** (no ADR, Strategy, Evaluation Strategy, or Implementation
  Authorization change);
- **authorization planning only**.

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document.

---

## 10. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (only the Task 2 commit; no stray changes) ✔ |
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | `a9743b4` (Phase 2 close) ✔ |
| HEAD | `git log -1 --oneline` | `5171483 feat: verify governed onnx export equivalence` ✔ |
| Architecture baseline | `docs/checkpoints/KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md` | present ✔ |
| Previous capability evidence | `docs/evidence/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md` | present ✔ |
| Governed export artifact present | `artifacts/padim/model.onnx` (+ `artifact.json`, `metadata.json`, `artifact_hashes.json`, `export_replay.json`) | present ✔ |
| Governed equivalence records present | `artifacts/padim/equivalence/` (`equivalence_report.json`, `equivalence_hashes.json`, `equivalence_replay.json`) | present ✔ |
| Runtime substrate present | `src/inspection/providers_onnx.py`, `src/frameworks/model_loader.py`, `src/frameworks/onnx_session.py`, `src/frameworks/onnx_runtime.py`, `src/frameworks/output_mapping.py` | present ✔ |

The only working-tree change after this review is the creation of this checkpoint document
itself.

---

## 11. Next Natural Step

```text
Review the persisted Runtime Provider Integration Authorization checkpoint before
generating the bounded implementation prompt for Phase 3 / Task 3 — Runtime Provider
Integration.
```

If and when the repository owner approves this authorization, the logical next step (per
Phase 3 §6, **not authorized by reviewing this checkpoint**) is to generate the bounded
implementation prompt for Phase 3 / Task 3 — Runtime Provider Integration. Until then, the
runtime continues to run the placeholder on its canonical path, and every claim remains
bounded to the offline single-seed VisA-proxy evidence recorded in C-6. Runtime-equivalence
verification (capability #4) and placeholder retirement (capability #5) each remain behind
their own separate authorization gates, unopened by this checkpoint.
