# Kalibra Runtime Equivalence Verification Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no runtime equivalence verification executed, no comparison run, no runtime modified, no provider touched, no model loader touched, no preprocessing touched, no feature extraction touched, no output mapping touched, no evidence file produced)
**Date:** 2026-07-07
**Repository baseline tag:** `ml-phase-2-complete`
**Repository baseline HEAD:** `a9743b4 docs: review ml phase 2 documentation`
**Architecture baseline:** [ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md)
**Previous capability:** Phase 3 / Task 3 — Runtime Provider Integration (complete)
**Review HEAD:** `d05c0dc feat: integrate governed padim runtime provider`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **Phase 3 / Task 4 — Runtime
Equivalence Verification** implementation. It is authorization planning only. It verifies no
runtime equivalence, runs no comparison, produces no equivalence report, computes no deviation,
generates no hash, modifies no runtime, modifies no provider, modifies no model loader, modifies
no output mapping, modifies no preprocessing, modifies no feature extraction, runs no new
evaluation, calibrates nothing, and modifies no ADR, Strategy, Evaluation Strategy,
Implementation Authorization, or any normative document.

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
- [Runtime Provider Integration Authorization Checkpoint](KALIBRA_RUNTIME_PROVIDER_INTEGRATION_AUTHORIZATION_CHECKPOINT_v1.0.md),
- [Runtime Provider Integration Completion Checkpoint](KALIBRA_RUNTIME_PROVIDER_INTEGRATION_COMPLETION_CHECKPOINT_v1.0.md),
- [Runtime Provider Integration Evidence](../evidence/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_EVIDENCE_v1.0.md),

and from the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md),
which establishes Phase 3's objective, scope, and ordering — and explicitly places **end-to-end
runtime equivalence + replay evidence** as capability #4 of §6, immediately after the governed
export (capability #1, complete), the offline export-equivalence verification (capability #2,
complete), and the runtime provider integration (capability #3, complete), and before placeholder
retirement (capability #5). The phase-opening checkpoint names R1 (inference equivalence) as the
**existential risk** of the phase and R4 (replay integrity across the runtime boundary) as the
reproducibility property the phase must defend; both are the direct subject of this capability.

This checkpoint defines **what a future runtime-equivalence-verification sprint is allowed to
do**, what it is **forbidden** to do, what it must **produce**, and how it must be
**validated**. It does not perform the sprint. It is equivalent in standing to the C-1, C-2, and
C-3 checkpoints, the Governed VisA Acquisition Authorization checkpoint, the C-4 PaDiM Baseline
Training Authorization checkpoint, the C-5 Governed PaDiM Inference Authorization checkpoint, the
Governed PaDiM ONNX Export Authorization checkpoint, the PaDiM ONNX Export Equivalence
Authorization checkpoint, and the Runtime Provider Integration Authorization checkpoint, and must
be reviewed before any implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding sense
established across the ML Phase 2 documents, the Phase 3 architecture checkpoint, and the Task 1 /
Task 2 / Task 3 authorization checkpoints.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Runtime Equivalence Verification
```

The authorization is **strictly limited to demonstrating, under governance, that the canonical
runtime path — `OnnxInspectionInferenceProvider` loading the governed PaDiM artifact through
`model_loader.load_governed_model` → `ProviderPrivateInferenceSession`, executing the governed
graph, and producing an `InspectionPrediction` — reproduces the governed offline C-5 PaDiM
reference and the governed C-6 runtime-observable outputs to a pre-declared, justified tolerance,
on governed inputs, with governed runtime-equivalence records, governed hashes, deterministic
replay, and governed runtime-equivalence evidence**. It grants no permission to modify the
runtime, modify the provider, modify the model loader, modify preprocessing, modify feature
extraction, modify output mapping, modify the prediction contract, re-fit, re-export, evaluate,
calibrate, generate benchmarks, or make any scientific or product claim.

**Basis for readiness — why the repository is now technically ready:**

- **The canonical runtime path now consumes the governed artifact.** Phase 3 / Task 3 wired
  `OnnxInspectionInferenceProvider` so its canonical default (`governed_padim_session_configuration()`)
  loads `artifacts/padim/model.onnx` (SHA-256
  `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`, model reference id
  `kalibra-padim-onnx-export-v1`, opset 18, IR 10) through `model_loader.load_governed_model` →
  `ProviderPrivateInferenceSession`, with deterministic CPUExecutionProvider / `exact_order` /
  intra/inter threads = 1 / `ORT_DISABLE_ALL` session configuration, hash-anchored artifact
  identity, fail-closed validation, and provenance-continuous governance records. Runtime
  equivalence verification therefore has a live, governed, replay-verified canonical runtime path
  to measure. It does not need to *build* that path; it needs to *prove what the path carries*.

- **The governed offline C-5 reference exists and is hash-anchored.** C-5 recorded the governed
  offline outputs that runtime equivalence must reproduce: per-split anomaly maps
  (`data/visa/derived/padim/inference/anomaly_maps/{validation,test}_anomaly_maps.npy`) and
  per-sample predictions
  (`data/visa/derived/padim/inference/predictions/{validation,test}_predictions.jsonl`), 6,492
  samples total (validation 2,164 + test 4,328), under the recorded identifiers
  `padim_anomaly_map_max_v1` and `padim_raw_anomaly_map_argmax_region_v1`. Every reference file is
  hash-anchored in the C-5 `artifact_hashes.json`, so runtime-equivalence verification can fail
  closed on any reference mutation rather than compare against an unverifiable signal.

- **The governed C-6 scientific evaluation exists and is hash-anchored.** C-6 produced the
  scientific reference of record over the same governed C-5 outputs — metrics, per-class
  metrics, the operating point, and failure analysis under `data/visa/derived/padim/evaluation/`.
  C-6 is **not** recomputed by this capability; but the C-6 runtime-observable outputs (the raw
  measures, localizations, and per-sample predictions that the evaluation consumed) are the
  scientific baseline against which runtime equivalence is judged. Where applicable, runtime
  equivalence may compare the canonical runtime's per-sample outputs against the C-6
  runtime-observable record.

- **The offline export-equivalence precedent is established and evidenced.** Phase 3 / Task 2
  already proved, off the runtime path, that the governed ONNX artifact reproduces the offline
  C-5 PaDiM computation across all 6,492 samples at machine-epsilon deviation (max anomaly-map
  abs/rel `7.1e-15 / 3.6e-15`; max raw-measure abs/rel `7.1e-15 / 3.6e-15`; max localization
  abs `0.0`), well inside the pre-declared `{1e-12, 1e-12, 0.0}` tolerance, with byte-identical
  deterministic replay. The graph is faithful to the offline signal. Runtime equivalence
  therefore isolates the one remaining question — does the *integrated runtime path* (with its
  feature-extraction reuse, class-index lookup, and prediction assembly) reproduce the same
  signal that the *offline direct-execution* path already proved? The dominant risk (R1) is
  narrowed from "does the model compute the right thing?" to "does the runtime seam carry the
  right thing through?".

- **A direct spot-check already indicates numerical equivalence at machine epsilon.** A
  representative sample comparison performed for this authorization (the first validation sample,
  read from the governed C-5 predictions and from the Task 3 runtime replay record) shows the
  canonical runtime `predicted_raw_anomaly_measure` differs from the C-5 reference by
  `8.9e-16` absolute (`1.3e-16` relative), with byte-identical localization region
  (`{x_min: 0.75, y_min: 0.125, x_max: 0.875, y_max: 0.25}`) and identical localization kind
  (`padim_raw_anomaly_map_argmax_region_v1`) and label (`raw_anomaly_maximum`). This is
  consistent with — but does **not** discharge — Task 4's obligation to produce the dedicated,
  exhaustive, governed runtime-equivalence evidence.

- **Runtime-equivalence verification is the prerequisite for the phase's closing claim, and
  nothing downstream is authorized by performing it.** Per Phase 3 §7, `ML Phase 3 COMPLETE`
  requires that "the runtime anomaly measure/localization reproduces the offline C-6 result on
  governed inputs within a pre-declared, justified tolerance, with per-class equivalence
  evidence." Authorizing this verification unblocks that success criterion without authorizing
  placeholder retirement (capability #5), calibration, or any scientific or product claim beyond
  C-6.

**Honest qualification of the equivalence surface.** A direct field-level inspection, performed
for this authorization, of the canonical runtime `InspectionPrediction` (Task 3) against the
governed C-5 reference surfaces honest, in-scope differences that Task 4's equivalence policy
must address explicitly rather than paper over:

- **The raw measure is numerically equivalent at machine epsilon** (abs `8.9e-16`, rel
  `1.3e-16` on the spot-checked sample), inside any reasonable DOUBLE tolerance.
- **The localization region and localization kind are byte-identical.**
- **`raw_measure_scale` differs by design.** The C-5 offline reference records
  `raw_measure_scale = "model_raw_anomaly_measure"` (the generic dataclass default carried by the
  offline prediction writer), while the canonical runtime records
  `raw_measure_scale = "padim_anomaly_map_max_v1"` (the more specific identifier carried through
  the governed output mapping). These are two identifiers for the same underlying measure
  semantics; they are **not** a numerical divergence. Task 4 must record this identifier
  difference explicitly and must not treat it as a signal mismatch.
- **`prediction_id` differs by design** (the runtime uses a runtime-specific stable id;
  the offline reference uses an offline-specific stable id). These are provenance/identity
  fields, not signal fields, and are expected to differ.

This means Task 4 is a genuine **equivalence-verification** task: it must define, per
equivalence dimension, which fields are compared for **numerical equality within tolerance**
(raw measure, localization region), which are compared for **identifier equality**
(localization kind, label, raw_measure_kind, prediction_kind), which are **expected to differ by
design and recorded as such** (`raw_measure_scale` identifier, `prediction_id`), and which
**must not be compared at all** (forbidden downstream fields: trust, review, ground truth). The
authorization below is written to permit exactly that bounded, honest, fail-closed verification.

Readiness is **for runtime-equivalence verification only**. Placeholder retirement from the
canonical flow, calibration, and any scientific or product claim beyond C-6 each remain behind
their own separate authorization gates.

---

## 2. Authorized Scope

If and when the runtime-equivalence-verification sprint is authorized by a bounded implementation
prompt, it may do **only** the following:

- **execution of the canonical runtime path** — execute the existing, Task 3-integrated
  `OnnxInspectionInferenceProvider` (canonical default `governed_padim_session_configuration()`)
  over governed inputs via `provider.predict(StabilizedInspectionInput) → InspectionPrediction`,
  reusing the existing runtime substrate exactly as integrated (no runtime modification, no
  provider modification, no loader modification). The runtime path is the **object** of
  verification, not something to rebuild;

- **comparison of runtime outputs against the governed C-5 reference** — for each governed C-5
  sample, compare the canonical runtime's `InspectionPrediction` (and, where the graph exposes
  it, the underlying `anomaly_map`) against the governed C-5 offline predictions and anomaly
  maps, recording per-sample, per-split, and global deviation. The C-5 reference is the
  governed, hash-anchored reference of record; it must not be regenerated, mutated, or
  substituted;

- **comparison of runtime outputs against the governed C-6 runtime-observable baseline where
  applicable** — compare the canonical runtime's per-sample raw measures, localizations, and
  predictions against the C-6 runtime-observable record (the per-sample predictions C-6
  consumed), where that record is hash-anchored and available. C-6 **aggregate metrics** (Image
  AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1) are the scientific reference of record and
  are **not** recomputed, extended, or compared as new metrics by this capability (see §7);

- **runtime anomaly-map equivalence** — verify that the canonical runtime path reproduces the
  governed C-5 anomaly map (where the runtime graph exposes the `anomaly_map` output) per sample,
  recording max absolute and max relative deviation per split and globally;

- **runtime raw-anomaly-measure equivalence** — verify that the canonical runtime
  `predicted_raw_anomaly_measure` reproduces the governed C-5
  `predicted_raw_anomaly_measure` per sample, recording max absolute and max relative deviation
  per split and globally;

- **runtime localization equivalence** — verify that the canonical runtime
  `predicted_localization` reproduces the governed C-5 localization per sample (region
  coordinates and localization kind), recording max absolute deviation per split and globally;

- **runtime `InspectionPrediction` equivalence** — verify that the canonical runtime
  `InspectionPrediction` satisfies the contract shape (`prediction_kind`, `raw_measure_kind`,
  `predicted_judgement`) and reproduces the C-5 signal fields, with the identifier differences
  (`raw_measure_scale`, `prediction_id`) recorded explicitly as expected-by-design rather than
  masked;

- **deterministic runtime replay** — re-run the runtime-equivalence verification over the same
  governed inputs and prove the second run reproduces identical per-sample deviations, identical
  per-split and global maxima, identical aggregate status, and identical governed records;

- **governed runtime-equivalence evidence** — produce a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating runtime execution,
  reference verification, anomaly-map equivalence, raw-measure equivalence, localization
  equivalence, `InspectionPrediction` equivalence, deterministic replay, governed provenance
  continuity, tolerance compliance, and no runtime/provider/loader/mapping/preprocessing/feature
  code touched.

Nothing beyond this list is authorized. In particular: **no runtime modification, no provider
modification, no model-loader modification, no preprocessing modification, no feature-extraction
modification, no output-mapping modification, no prediction-contract modification, no Trust /
Review / Evidence / Evaluation change, no re-fit, no re-export, no calibration, no benchmark
generation, no scientific or product claim.**

The runtime seam and the governed artifacts are the **inputs** to verification. Task 4 verifies
what they carry; it does not change them.

---

## 3. Forbidden Scope

The runtime-equivalence-verification sprint **must not**, under any circumstances, perform or
produce:

- **runtime redesign** (no modification to `src/inspection/providers_onnx.py`, including the
  canonical default `governed_padim_session_configuration()`, the PaDiM/placeholder dispatch, the
  graph-contract verification, the feature-input assembly, or the prediction assembly);
- **provider redesign** (no modification to the `OnnxInspectionInferenceProvider` seam, the
  `InspectionInferenceProvider` protocol, or the `predict() → InspectionPrediction` boundary);
- **model-loader redesign** (no modification to `src/frameworks/model_loader.py`,
  `src/frameworks/onnx_session.py`, or `src/frameworks/onnx_runtime.py`);
- **preprocessing redesign** (no modification to `src/frameworks/image_preprocessing.py` or its
  contract; the PaDiM path consumes the deterministic full-patch feature tensor produced by the
  existing offline feature extractor, not runtime-preprocessed pixels);
- **feature extraction redesign** (no modification to the deterministic feature extraction path;
  the feature indices `[0, 2, 5, 6, 7, 9, 12, 13]`, layer, and backbone are fixed by C-4 and
  embedded unchanged in the governed graph — verification reuses the existing feature extraction,
  it does not redefine it);
- **output mapping redesign** (no modification to `src/frameworks/output_mapping.py`, including
  the PaDiM mapping contract and the placeholder mapping contract; the mapping is the object of
  verification, not a thing to change);
- **prediction contract redesign** (no modification to the `InspectionPrediction` field set, field
  types, field validation, `prediction_kind`, or `raw_measure_kind` literals; the prediction
  boundary is the verification's immovable reference);
- **Trust changes** (no Trust-domain modification; no calibrated or qualified trust statement is
  produced; trust qualification remains deferred);
- **Review changes** (no Review-domain modification; no review routing is produced);
- **Evidence changes** (no Evidence-domain modification; the Evidence Engine's emitter, records,
  and hash-anchoring contract are unchanged — Task 4 produces its own equivalence evidence
  document, it does not alter the Evidence domain);
- **Evaluation changes** (no modification to `scripts/scientific_evaluation.py` or the C-6
  evaluation harness; equivalence is **not** evaluation — no new Image AUROC, Pixel AUROC,
  AUPRO, Precision, Recall, or F1 is produced or implied);
- **calibration** (no calibrated confidence, no threshold tuning, no operating-point selection,
  no abstention);
- **benchmark generation** (no benchmark suite, no multi-dataset claim, no generality claim);
- **product claims** (no product-facing capability, no deployment, no live/streaming/hosted
  behavior, no operational alerting);
- **re-export or re-fit** (the governed `model.onnx` is the *input* to verification, not an
  output; the C-4 fit and the C-5 reference are *consumed*, not regenerated; no governed source
  artifact in `data/visa/derived/` may be mutated);
- **placeholder retirement** (Task 4 does not retire the placeholder; the placeholder remains
  available as an explicit fixture/test path; full placeholder retirement is capability #5,
  separately authorized);
- **architecture changes** (no new domain, contract, seam, or domain responsibility; no rewiring
  of the canonical Inspection → Trust → Review → Evidence → Evaluation flow).

Any of these would exceed the runtime-equivalence-verification boundary and requires its own
separate authorization gate. The provider seam, the `InspectionPrediction` contract, the
`InspectionEngine.transform_prediction()` path, the model loader, the output mapping, the
preprocessing contract, and the feature-extraction path must be preserved untouched;
runtime-equivalence verification measures what the integrated path carries, it does not alter it.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined here,
**not created now**):

```text
artifacts/runtime/equivalence/
  runtime_equivalence_report.json   # governed runtime-equivalence record (per-dimension, per-split, global)
  runtime_equivalence_hashes.json   # hashes of every governed runtime-equivalence record
  runtime_equivalence_replay.json   # governed replay record (second verification == first)
docs/evidence/                      # committed governed runtime-equivalence evidence report
```

Required artifacts:

- **`runtime_equivalence_report.json`** — the governed runtime-equivalence record: the verified
  canonical runtime identity (loaded `model.onnx` SHA-256
  `0437ae28…741a`, model reference id `kalibra-padim-onnx-export-v1`, opset 18, IR 10), the
  actual loaded session configuration and session-configuration hash
  (`2893fd1fc592cb831bfccd9d53c3e784a5aba4ffdfbb58ad4de32eb512c4a2e4`), the provider
  configuration (`OnnxInspectionInferenceProvider`, `model_loader.load_governed_model`,
  `ProviderPrivateInferenceSession`), the consumed governed reference identities (C-5 anomaly-map
  hashes and prediction hashes per split, C-5 `artifact_hashes.json` hash, C-5 inference metadata
  hash; C-6 evaluation metadata and runtime-observable record hashes where applicable; Task 1
  export artifact hashes; Task 2 offline equivalence record hashes; Task 3 runtime integration
  record hashes), the per-sample / per-split / global deviation for the anomaly map
  (absolute + relative), the raw measure (absolute + relative), and the localization (absolute),
  the `InspectionPrediction` contract/identifier equivalence record (contract fields equal;
  `raw_measure_scale` and `prediction_id` differing by design and recorded), the sample count
  (6,492; validation 2,164 + test 4,328), the tolerance policy (every tolerance explicit and
  justified), the pass/fail status per dimension and overall, and the machine-readable
  `scope_boundaries` block with every runtime-modification / evaluation / claim flag set to
  `false`;

- **`runtime_equivalence_hashes.json`** — hashes of every governed runtime-equivalence artifact
  (`runtime_equivalence_report.json` content hash plus the hash of
  `runtime_equivalence_replay.json`), so an observer can verify integrity without re-running;

- **`runtime_equivalence_replay.json`** — the governed replay record confirming that a second
  runtime-equivalence verification over the same governed inputs reproduced identical per-sample
  deviations, identical per-split and global maxima, identical aggregate status, and identical
  governed records (per-record hash agreement), with a `passed` status and a complete second
  canonical-runtime load + execution;

- **governed runtime-equivalence evidence report** — a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating canonical-runtime
  execution, reference verification, anomaly-map equivalence, raw-measure equivalence,
  localization equivalence, `InspectionPrediction` equivalence (with the by-design identifier
  differences recorded), tolerance compliance (every tolerance explicit and justified),
  deterministic replay, governed provenance continuity (C-3 → C-4 → C-5 → Task 1 artifact →
  Task 2 equivalence → Task 3 runtime integration → Task 4 runtime equivalence), no
  runtime/provider/loader/mapping/preprocessing/feature code touched, and the explicit non-claims.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `artifacts/runtime/equivalence/runtime_equivalence_report.json` | **Committed** — reviewable governed runtime-equivalence record |
| `artifacts/runtime/equivalence/runtime_equivalence_hashes.json` | **Committed** — integrity anchor |
| `artifacts/runtime/equivalence/runtime_equivalence_replay.json` | **Committed** — reviewable replay proof |
| `docs/evidence/` runtime-equivalence evidence report | **Committed** — evidence of a clean, reproducible, governed runtime-equivalence verification |
| verification script (e.g. `scripts/verify_padim_runtime_equivalence.py`) | **Committed** — reviewable text |
| verification tests (e.g. `tests/test_padim_runtime_equivalence.py`) | **Committed** — reviewable text |

All runtime-equivalence outputs are reviewable JSON / Markdown / Python text; no large binary is
produced by this sprint (the governed `model.onnx`, the C-5 anomaly maps, and the C-5
predictions already exist and are not reproduced). No `.gitignore` change is anticipated; any
`.gitignore` update is authorized **only if strictly required**, minimal, and scoped.

---

## 5. Validation Requirements

The runtime-equivalence-verification sprint must validate, and its evidence report must
demonstrate, that:

- **the canonical runtime reproduces the governed C-5 reference** — the canonical runtime path's
  anomaly map, raw measure, and localization match the governed C-5 reference across all 6,492
  samples, with the deviation recorded per sample, per split, and globally;

- **the canonical runtime reproduces the governed ONNX export** — the canonical runtime's loaded
  artifact identity (`model.onnx` SHA-256, opset 18, IR 10, model reference id
  `kalibra-padim-onnx-export-v1`) matches the Task 1 governed export records, and the runtime
  session configuration matches the Task 3 runtime integration records;

- **the canonical runtime reproduces the governed C-6 runtime-observable outputs** — the
  canonical runtime's per-sample raw measures, localizations, and predictions match the C-6
  runtime-observable record (the per-sample predictions C-6 consumed), where that record is
  hash-anchored and available. C-6 **aggregate metrics** are not recomputed;

- **anomaly-map equivalence** — the canonical runtime anomaly map matches the governed C-5
  anomaly map within the pre-declared tolerance, with max absolute and max relative deviation
  recorded per split and globally (where the runtime graph exposes the anomaly-map output);

- **raw-measure equivalence** — the canonical runtime `predicted_raw_anomaly_measure` matches the
  governed C-5 `predicted_raw_anomaly_measure` within the pre-declared tolerance, with max
  absolute and max relative deviation recorded per split and globally;

- **localization equivalence** — the canonical runtime `predicted_localization` matches the
  governed C-5 localization within the pre-declared tolerance (region coordinates absolute;
  localization kind identifier-equal), with max absolute deviation recorded per split and
  globally;

- **`InspectionPrediction` equivalence** — the canonical runtime `InspectionPrediction` satisfies
  the contract (`prediction_kind = inspection_prediction`, `raw_measure_kind =
  raw_anomaly_measure`, `predicted_judgement` consistent) and reproduces the C-5 signal fields,
  with the by-design identifier differences (`raw_measure_scale`, `prediction_id`) recorded
  explicitly and not treated as mismatches;

- **deterministic runtime replay** — a complete second canonical-runtime load + execution +
  verification over the same governed inputs reproduces identical per-sample deviations,
  identical per-split and global maxima, identical aggregate status, and identical governed
  records, recorded in `runtime_equivalence_replay.json` with per-record hash agreement and
  `status: passed`;

- **deterministic hashes** — every governed runtime-equivalence record has a stable SHA-256
  recorded in `runtime_equivalence_hashes.json`, and a second verification leaves every hash
  unchanged;

- **governed provenance continuity** — the hash-anchored chain extends unbroken from the C-3
  acquisition through the C-4 fit, the C-5 reference, the C-6 evaluation, the Task 1 ONNX
  artifact, the Task 2 equivalence record, the Task 3 runtime integration record, and into the
  Task 4 runtime-equivalence record; the consumed artifact hashes are verified before any
  comparison and recorded in the report; the verification fails closed on any hash mismatch.

**Every comparison must fail closed.** A deviation that exceeds its declared tolerance, a
reference-hash mismatch, a contract-shape drift, or a provenance gap must halt the verification
and be surfaced — never silently widened, never silently passed.

The evidence must record the verification toolchain versions (python, numpy, onnx, onnxruntime)
and the canonical runtime execution provider, matching the Task 2 / Task 3 evidence idiom.

---

## 6. Runtime Equivalence Policy

The runtime-equivalence-verification sprint must verify, **explicitly and fail-closed**, each of
the following equivalences. Every comparison must be against the governed reference, never
against a recomputed or substitute signal.

- **artifact identity equivalence** — the canonical runtime's loaded artifact identity
  (`model.onnx` SHA-256 `0437ae28…741a`, opset 18, IR 10, model reference id
  `kalibra-padim-onnx-export-v1`) matches the Task 1 governed export records and the Task 3
  runtime integration records byte-for-byte;

- **provider configuration equivalence** — the canonical runtime provider configuration
  (`OnnxInspectionInferenceProvider`, `model_loader.load_governed_model`,
  `ProviderPrivateInferenceSession`, `CPUExecutionProvider`) matches the Task 3 runtime
  integration records;

- **session configuration equivalence** — the canonical runtime session configuration
  (`CPUExecutionProvider`, `exact_order`, intra/inter = 1, `ORT_DISABLE_ALL`) and its hash
  (`2893fd1fc592cb831bfccd9d53c3e784a5aba4ffdfbb58ad4de32eb512c4a2e4`) match the Task 3 runtime
  integration records;

- **preprocessing-contract equivalence** — the canonical runtime consumes the deterministic
  full-patch feature tensor produced by the existing offline feature extractor
  (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`), exactly as the offline C-5 path does; the
  preprocessing contract is unchanged and is not reimplemented by this verification;

- **feature extraction equivalence** — the canonical runtime's feature extraction (reused from
  `scripts.train_padim_baseline.extract_features` with `FitConfig()`) is the governed offline
  extraction; the feature indices `[0, 2, 5, 6, 7, 9, 12, 13]`, layer, and backbone are fixed by
  C-4 and unchanged;

- **graph contract equivalence** — the canonical runtime's loaded graph exposes exactly the
  recorded input contract (`full_patch_features[1,64,14] float64`, `class_index[1] int64`) and
  output contract (`patch_mahalanobis_distances[1,64]`, `anomaly_map[1,64,64]`,
  `raw_anomaly_measure[1]`, `argmax_region[1,4]`), with the recorded names, shapes, dtypes, and
  identifiers; fail closed on any drift;

- **output mapping equivalence** — the canonical runtime output mapping
  (`map_padim_onnx_outputs`, `PADIM_OUTPUT_MAPPING_CONTRACT_ID`, `PADIM_RAW_MEASURE_SCALE =
  padim_anomaly_map_max_v1`, `PADIM_LOCALIZATION_KIND =
  padim_raw_anomaly_map_argmax_region_v1`) carries the governed PaDiM semantics; the mapping
  contract is the object of verification, not a thing to change;

- **prediction contract equivalence** — the canonical runtime `InspectionPrediction` satisfies
  the contract shape (`input_id`, `prediction_id`, `predicted_judgement`,
  `predicted_raw_anomaly_measure`, `predicted_localization`, `raw_measure_kind =
  raw_anomaly_measure`, `raw_measure_scale`, `prediction_kind = inspection_prediction`,
  `model_metadata`); the contract fields are identifier-equal to the C-5 reference where they are
  contract literals (`raw_measure_kind`, `prediction_kind`, `predicted_judgement`), numerically
  equivalent where they are signal fields (`predicted_raw_anomaly_measure`,
  `predicted_localization.region`), and **recorded as expected-by-design differences** where
  they are provenance/identity fields (`raw_measure_scale` identifier, `prediction_id`).

**By-design identifier difference — recorded, not masked.** The C-5 offline reference records
`raw_measure_scale = "model_raw_anomaly_measure"` (the generic dataclass default carried by the
offline prediction writer), while the canonical runtime records
`raw_measure_scale = "padim_anomaly_map_max_v1"` (the specific identifier carried through the
governed output mapping). These are two identifiers for the same underlying measure semantics;
the difference is a consequence of the runtime carrying the more specific governed identifier
through the mapping, not a numerical or semantic divergence. The runtime-equivalence report must
record this difference explicitly, justify it (both identifiers denote the PaDiM anomaly-map-max
raw measure; the runtime identifier is the more specific governed one), and must not treat it as
a signal mismatch. Likewise, `prediction_id` is a provenance field that differs by design
(runtime-specific vs offline-specific stable id) and must be recorded as such, not compared for
equality.

**Every tolerance must be:**

- **explicit** — declared by name and value in the runtime-equivalence report before any
  comparison result is presented, never buried inside a threshold constant;
- **justified** — accompanied by a recorded justification (e.g. "DOUBLE Mahalanobis under
  CPUExecutionProvider reproduces the offline float64 computation at machine epsilon, as already
  demonstrated by Task 2 offline equivalence across 6,492 samples and confirmed at the runtime
  seam by Task 4; the declared tolerance is orders of magnitude above the observed maximum"),
  never asserted without reason;
- **recorded** — written into `runtime_equivalence_report.json` and the evidence document, with
  the observed maximum deviation alongside the declared tolerance, so an observer can see both
  the bound and the margin.

The sprint inherits the Task 2 demonstrated regime as the baseline expectation —
`{absolute: 1e-12, relative: 1e-12, bbox_absolute: 0.0}` — which Task 2 already met at
machine-epsilon deviation and which the Task 4 spot-check confirms at the runtime seam
(abs `8.9e-16`, rel `1.3e-16`). The sprint may retain this regime or tighten it, but must not
silently loosen it. The known bbox exactness (Task 1 finding L1: the only achievable coordinate
values are multiples of `1/64 = 2⁻⁶`, so `bbox_absolute = 0.0` is exact) is carried forward.

A deviation that exceeds its declared tolerance is a verification **failure** that must halt the
sprint and be surfaced — never silently widened.

---

## 7. Scientific Boundaries

Explicitly:

- **Runtime equivalence verification is not scientific evaluation.** Demonstrating that the
  canonical runtime reproduces the governed offline signal is not measuring the system against
  its claims. The C-6 scientific evaluation is the *reference of record*; it is not recomputed,
  extended, or replaced here.

- **Runtime equivalence verification produces no new Image AUROC.** No image-level aggregate score
  is computed over the runtime path. The C-6 Image AUROC stands as recorded.

- **Runtime equivalence verification produces no new Pixel AUROC.** No pixel-level aggregate score
  is computed over the runtime path. The C-6 Pixel AUROC stands as recorded.

- **Runtime equivalence verification produces no new AUPRO.** No per-region overlap aggregate is
  computed over the runtime path. The C-6 AUPRO stands as recorded.

- **Runtime equivalence verification produces no new Precision, Recall, or F1.** No
  threshold-operated aggregate is computed over the runtime path. The C-6 operating-point
  metrics stand as recorded.

- **Runtime equivalence verification produces no new scientific claim.** Its only purpose is to
  demonstrate that the canonical runtime reproduces the **already-validated** offline scientific
  baseline. It does not prove that Kalibra detects defects *better*, does not prove
  product-readiness, calibration quality, drift response, or generality, and does not expand the
  single-seed, VisA-proxy claim boundary. The scientific claim boundary remains exactly C-6's —
  single-seed, VisA-proxy, no calibration, no confidence, no product-readiness — and this
  checkpoint makes no claim beyond it.

Its only purpose is to demonstrate that the canonical runtime reproduces the already-validated
offline scientific baseline — nothing more.

Kalibra does **not** yet perform real defect detection at runtime as a *proven, measured*
property beyond the single-seed VisA-proxy boundary already established by C-6, and this
checkpoint does not expand that. It authorizes proving the runtime reproduces the C-6 signal; it
does not authorize any new scientific or product claim.

---

## 8. Readiness Decision

```text
READY — the repository is ready for a bounded Phase 3 / Task 4 — Runtime Equivalence
Verification implementation prompt.

- Authorized scope: canonical runtime execution + comparison against governed C-5 reference +
  comparison against governed C-6 runtime-observable outputs where applicable + anomaly-map
  equivalence + raw-measure equivalence + localization equivalence + InspectionPrediction
  equivalence + deterministic runtime replay + governed runtime-equivalence evidence only.
- Forbidden scope: all runtime/provider/loader/preprocessing/feature-extraction/output-mapping/
  prediction-contract redesign, Trust/Review/Evidence/Evaluation changes, re-fit, re-export,
  placeholder retirement, calibration, benchmark generation, scientific and product claims, and
  any architecture change.
- Required outputs, commit policy, validation requirements, runtime-equivalence policy, and
  scientific boundaries are defined.
- Honest equivalence-surface qualification: the canonical runtime reproduces the C-5 signal at
  machine epsilon (spot-checked abs 8.9e-16 / rel 1.3e-16, byte-identical localization); the
  raw_measure_scale identifier differs by design (generic vs specific governed identifier) and
  must be recorded, not masked; prediction_id differs by design (provenance field) and must be
  recorded, not compared.
- Nothing verified, compared, integrated, modified, evaluated, calibrated, or claimed by this
  checkpoint.
- No normative document modified.
```

---

## 9. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no runtime-equivalence verification** (no comparison run, no deviation computed, no
  equivalence report produced);
- **no runtime modification** (`providers_onnx.py`, `model_loader.py`, `onnx_session.py`,
  `onnx_runtime.py`, `output_mapping.py`, `image_preprocessing.py`, `domain.py`,
  `transform_prediction`, `engine.py`, `src/integration/` all unchanged by this checkpoint);
- **no provider loaded** (no `OnnxInspectionInferenceProvider`, no `InspectionInferenceProvider`
  instantiated for verification by this checkpoint);
- **no runtime inference** (no canonical runtime execution of the governed artifact for
  measurement by this checkpoint — the spot-check cited in §1 read existing Task 3 replay
  records and C-5 reference records; it executed no new runtime inference);
- **no evaluation / metric / benchmark** (no Image AUROC, Pixel AUROC, AUPRO, Precision, Recall,
  or F1 produced or implied);
- **no calibration**;
- **no scientific or product claim** beyond the C-6 single-seed VisA-proxy boundary;
- **no re-export or re-fit** (the `model.onnx` and the C-4 / C-5 / C-6 artifacts are inputs, not
  outputs);
- **no placeholder retired** (the placeholder remains available as an explicit fixture/test
  path; full retirement is capability #5, separately authorized);
- **no documentation modified** (no ADR, Strategy, Evaluation Strategy, or Implementation
  Authorization change);
- **authorization planning only**.

It changes no governed logic, runtime, provider, dataset, evaluation harness, or authorization
document.

---

## 10. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (only the Task 3 commit; no stray changes) ✔ |
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | `a9743b4` (Phase 2 close) ✔ |
| HEAD | `git log -1 --oneline` | `d05c0dc feat: integrate governed padim runtime provider` ✔ |
| Architecture baseline | `docs/checkpoints/KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md` | present ✔ |
| Previous capability evidence | `docs/evidence/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_EVIDENCE_v1.0.md` | present ✔ |
| Previous capability completion | `docs/checkpoints/KALIBRA_RUNTIME_PROVIDER_INTEGRATION_COMPLETION_CHECKPOINT_v1.0.md` | present ✔ |
| Governed export artifact present | `artifacts/padim/model.onnx` (+ `artifact.json`, `metadata.json`, `artifact_hashes.json`, `export_replay.json`) | present ✔ |
| Governed offline equivalence records present | `artifacts/padim/equivalence/` (`equivalence_report.json`, `equivalence_hashes.json`, `equivalence_replay.json`) | present ✔ |
| Task 3 runtime integration records present | `artifacts/runtime/` (`integration_metadata.json`, `runtime_replay.json`, `runtime_hashes.json`) | present ✔ |
| C-5 reference present | `data/visa/derived/padim/inference/anomaly_maps/{validation,test}_anomaly_maps.npy`, `predictions/{validation,test}_predictions.jsonl`, `artifact_hashes.json` | present ✔ |
| C-6 reference present | `data/visa/derived/padim/evaluation/` (`metadata/`, `metrics/`, `per_class/`, `operating_point/`, `failure_analysis/`, `replay/`, `artifact_hashes.json`) | present ✔ |
| Runtime substrate present | `src/inspection/providers_onnx.py`, `src/frameworks/model_loader.py`, `src/frameworks/onnx_session.py`, `src/frameworks/onnx_runtime.py`, `src/frameworks/output_mapping.py` | present ✔ |

The only working-tree change after this review is the creation of this checkpoint document
itself.

---

## 11. Next Natural Step

```text
Review the persisted Runtime Equivalence Verification Authorization checkpoint before
generating the bounded implementation prompt for Phase 3 / Task 4 — Runtime Equivalence
Verification.
```

If and when the repository owner approves this authorization, the logical next step (per
Phase 3 §6, **not authorized by reviewing this checkpoint**) is to generate the bounded
implementation prompt for Phase 3 / Task 4 — Runtime Equivalence Verification. Until then, the
canonical runtime consumes the governed PaDiM artifact (Task 3 complete) but its end-to-end
equivalence to the C-6 scientific baseline remains unproven, and every claim remains bounded to
the offline single-seed VisA-proxy evidence recorded in C-6. Placeholder retirement (capability
#5) remains behind its own separate authorization gate, unopened by this checkpoint.
