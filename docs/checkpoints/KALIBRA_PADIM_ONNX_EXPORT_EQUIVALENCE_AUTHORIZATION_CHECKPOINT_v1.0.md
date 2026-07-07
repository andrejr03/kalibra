# Kalibra PaDiM ONNX Export Equivalence Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no equivalence verification executed, no comparison run, no runtime modified, no provider touched, no model loader touched, no preprocessing touched, no evidence file produced)
**Date:** 2026-07-07
**Repository baseline tag:** `ml-phase-2-complete`
**Repository baseline HEAD:** `a9743b4 docs: review ml phase 2 documentation`
**Architecture baseline:** [ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md)
**Previous capability:** Phase 3 / Task 1 — Governed ONNX Export (complete)
**Review HEAD:** `ee43c61 feat: export governed padim onnx artifact`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **Phase 3 / Task 2 — Export
Equivalence Verification** implementation. It is authorization planning only. It verifies no
ONNX artifact, runs no comparison, produces no equivalence report, computes no deviation,
generates no hash, modifies no runtime, modifies no provider, modifies no model loader,
modifies no output mapping, modifies no preprocessing, runs no inference, runs no evaluation,
calibrates nothing, and modifies no ADR, Strategy, Evaluation Strategy, Implementation
Authorization, or any normative document.

It draws its authority from the now-normative decisions recorded in the

- [Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
  (PaDiM selected first; PatchCore reserved second),
- [Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) §8,
- [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
  (`SELECTED — VisA`),
- [Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md)
  (§2 provider / prediction boundary; §8 raw-anomaly-measure boundary),
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

and from the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md),
which establishes Phase 3's objective, scope, and ordering — and explicitly places **offline
export-equivalence verification** as capability #2 of §6, immediately after the governed
export (capability #1, now complete) and before any runtime provider integration (capability
#3). The phase-opening checkpoint names R1 (inference equivalence), R2 (export fidelity), and
R3 (preprocessing equivalence) as the dominant risks, and prescribes that each Phase 3
capability remain behind its own separate authorization gate before implementation.

This checkpoint defines **what a future equivalence-verification sprint is allowed to do**,
what it is **forbidden** to do, what it must **produce**, and how it must be **validated**. It
does not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3
checkpoints, the Governed VisA Acquisition Authorization checkpoint, the C-4 PaDiM Baseline
Training Authorization checkpoint, the C-5 Governed PaDiM Inference Authorization checkpoint,
and the C-1-style Governed PaDiM ONNX Export Authorization checkpoint, and must be reviewed
before any implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding sense
established across the ML Phase 2 documents, the Phase 3 architecture checkpoint, and the
Task 1 export-authorization checkpoint.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Export Equivalence Verification
```

The authorization is **strictly limited to the offline, deterministic verification that the
governed ONNX artifact produced by Phase 3 / Task 1 reproduces the governed offline C-5
PaDiM computation on governed inputs, to a pre-declared, justified tolerance, with governed
equivalence records, governed hashes, deterministic replay, and governed equivalence
evidence — produced off the runtime path, consuming no runtime code, and changing no
runtime code**. It grants no permission to integrate the runtime, change providers, change
the model loader, change output mapping, change preprocessing, change feature extraction, run
runtime inference, evaluate, calibrate, generate benchmarks, or make any scientific or
product claim.

**Basis for readiness — why the repository is now technically ready:**

- **The governed ONNX artifact exists and is hash-anchored.** Phase 3 / Task 1 produced
  `artifacts/padim/model.onnx` (SHA-256
  `0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`, opset 18, IR 10,
  500,109 bytes) plus the governed `artifact.json`, `metadata.json`,
  `artifact_hashes.json`, and `export_replay.json`. The export is governed, replay-verified,
  and provenance-continuous from C-3 → C-4 → C-5 → ONNX artifact. Equivalence verification
  therefore has a real, integrity-anchored artifact to verify.

- **The governed offline reference signal exists and is hash-anchored.** C-5 recorded the
  governed offline outputs that equivalence must reproduce: per-split anomaly maps
  (`data/visa/derived/padim/inference/anomaly_maps/{validation,test}_anomaly_maps.npy`) and
  per-sample predictions
  (`data/visa/derived/padim/inference/predictions/{validation,test}_predictions.jsonl`),
  6,492 samples total (validation 2,164 + test 4,328), under the recorded identifiers
  `padim_anomaly_map_max_v1` and `padim_raw_anomaly_map_argmax_region_v1`. Every reference
  file is hash-anchored in the C-5 `artifact_hashes.json`, so equivalence verification can
  fail closed on any reference mutation rather than compare against an unverifiable signal.

- **The graph contract is fully recorded and inspectable.** The graph input contract is
  `full_patch_features` (`[1, 64, 14]` float64, the deterministic full-patch feature tensor
  before governed feature subsampling) and `class_index` (`[1]` int64, index into the
  governed C-4 `class_order`). The graph output contract is
  `patch_mahalanobis_distances` (`[1, 64]` float64), `anomaly_map` (`[1, 64, 64]` float64,
  `padim_anomaly_map_max_v1`), `raw_anomaly_measure` (`[1]` float64,
  `padim_anomaly_map_max_v1`), and `argmax_region` (`[1, 4]` float64, ordered
  `[x_min, y_min, x_max, y_max]`, `padim_raw_anomaly_map_argmax_region_v1`). Equivalence
  verification can therefore compare four distinct output dimensions against the offline
  reference without inferring the contract.

- **The offline numerical contract is fully pinned and recorded.** The selected feature
  indices (`[0, 2, 5, 6, 7, 9, 12, 13]`, dimension 8 of 14), the dtype (`float64`, preserved
  as ONNX DOUBLE, `float32_transition = false`), the covariance estimator, the regularization
  (`ε = 0.001`), the inverse method (`numpy.linalg.inv`), and the preprocessing contract id
  (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`) are all recorded and frozen in the
  governed C-4 metadata set and re-recorded in the export `artifact.json`/`metadata.json`.
  Equivalence verification therefore compares two computations over the same pinned
  constants — it does not need to reconstruct or guess any numerical choice.

- **A tolerance policy is already established and demonstrated, not invented.** Task 1's
  export-fidelity check already compared the ONNX graph against the governed C-5 reference
  across all 6,492 samples and recorded machine-epsilon deviation
  (max anomaly-map abs/rel `7.1e-15 / 3.6e-15`; max raw-measure abs/rel
  `7.1e-15 / 3.6e-15`; max argmax-region abs `0.0`) under the pre-declared tolerance
  `{absolute: 1e-12, relative: 1e-12, bbox_absolute: 0.0}`. Task 2 therefore inherits a
  concrete, evidenced, justified tolerance regime rather than a hoped-for one, and its job is
  to produce the **separate, dedicated, deeper equivalence evidence** (its own governed
  artifacts, its own replay, its own per-class and per-dimension evidence, its own
  fail-closed verification) that the phase architecture requires as capability #2.

- **Equivalence verification is the prerequisite for everything downstream in Phase 3, and
  nothing downstream is authorized by performing it.** Per Phase 3 §6, export-equivalence
  verification is capability #2 precisely because runtime provider integration (#3),
  end-to-end runtime equivalence (#4), and placeholder retirement (#5) all presuppose that
  the exported artifact faithfully reproduces the validated offline signal. Authorizing this
  verification unblocks that ordering without authorizing any runtime change.

Readiness is **for export-equivalence verification only**. Runtime integration, provider
changes, model loader changes, output mapping changes, preprocessing changes, feature
extraction changes, runtime inference, evaluation, calibration, and any scientific or product
claim each remain behind their own separate authorization gates.

**Relationship to Task 1's in-script export-fidelity check.** Task 1's `verify_export_fidelity`
ran a fidelity comparison as a *condition of export* and recorded the outcome inside the
export's own governed records (`artifact.json`, `metadata.json`) and evidence. That is export
self-verification. Task 2 is the *separately authorized* capability the phase architecture
requires: a dedicated equivalence-verification artifact set under
`artifacts/padim/equivalence/`, with its own governed hashes, its own deterministic replay,
its own per-class / per-dimension / per-split evidence, its own graph-contract verification,
and its own standalone evidence document. Task 2 does not re-do Task 1; it produces the
independent equivalence record the phase demands before the runtime is ever touched.

---

## 2. Authorized Scope

If and when the equivalence-verification sprint is authorized by a bounded implementation
prompt, it may do **only** the following:

- **governed ONNX artifact verification** — load the governed `artifacts/padim/model.onnx`
  only after verifying its recorded SHA-256
  (`0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a`) against the
  export's `artifact.json` / `artifact_hashes.json`, and fail closed on any mismatch; the
  artifact is the *object* of verification and must not be regenerated, mutated, or
  re-exported;

- **offline equivalence verification** — execute the governed ONNX artifact **offline**,
  off the runtime path, via a direct `onnxruntime.InferenceSession` using
  `CPUExecutionProvider` with the existing pinned single-threaded session options, and
  compare its outputs against the governed offline C-5 reference — never loading the runtime
  provider (`src/inspection/providers_onnx.py`), never loading the runtime model loader
  (`src/frameworks/model_loader.py`), and never entering the canonical `inspect()` path;

- **deterministic comparison against governed C-5 outputs** — for each of the 6,492 governed
  C-5 samples (validation 2,164 + test 4,328), recompute the deterministic full-patch feature
  tensor from the governed C-3 sample files using the **existing** offline feature extractor
  (`train_padim_baseline.extract_features`), feed it to the ONNX graph together with the
  governed `class_index`, and compare against the C-5 anomaly maps and predictions — the
  comparison must reproduce the existing offline feature extraction path, not redefine it;

- **anomaly-map equivalence** — verify that the ONNX `anomaly_map` output (`[1, 64, 64]`,
  `padim_anomaly_map_max_v1`) matches the governed C-5 anomaly map
  (`{split}_anomaly_maps.npy`) per sample, recording max absolute and max relative deviation
  per split and globally;

- **raw-anomaly-measure equivalence** — verify that the ONNX `raw_anomaly_measure` output
  (`[1]`, `padim_anomaly_map_max_v1`) matches the governed C-5
  `predicted_raw_anomaly_measure` per sample, recording max absolute and max relative
  deviation per split and globally;

- **localization equivalence** — verify that the ONNX `argmax_region` output (`[1, 4]`,
  ordered `[x_min, y_min, x_max, y_max]`, `padim_raw_anomaly_map_argmax_region_v1`) matches
  the governed C-5 localization per sample, recording max absolute deviation per split and
  globally;

- **graph-contract verification** — verify, before any comparison, that the loaded ONNX graph
  still exposes exactly the recorded input contract (`full_patch_features[1,64,14] float64`,
  `class_index[1] int64`) and output contract (`patch_mahalanobis_distances[1,64]`,
  `anomaly_map[1,64,64]`, `raw_anomaly_measure[1]`, `argmax_region[1,4]`), the recorded
  opset (18) and IR (10), and that the in-graph constants (feature indices
  `[0, 2, 5, 6, 7, 9, 12, 13]`, per-class μ, per-class Σ⁻¹) are byte-equal to the governed
  C-4 artifacts — fail closed on any drift;

- **deterministic replay** — re-run the equivalence verification over the same governed
  inputs and prove the second run reproduces identical per-sample deviations, identical
  per-split and global maxima, and identical aggregate status, recording the comparison in a
  governed replay record;

- **governed equivalence evidence** — produce a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating artifact verification,
  reference verification, anomaly-map equivalence, raw-measure equivalence, localization
  equivalence, graph-contract verification, tolerance compliance, deterministic replay,
  governed provenance continuity, and no runtime code touched.

Nothing beyond this list is authorized. In particular: **no runtime integration, no provider
change, no model loader change, no output mapping change, no preprocessing change, no feature
extraction change, no runtime inference, no evaluation.**

The runtime seams must be respected. The sprint may **verify** a governed ONNX artifact; it
must not load it into the runtime, must not alter `providers_onnx.py`, must not alter
`model_loader.py`, must not alter `output_mapping.py`, must not alter `image_preprocessing.py`,
must not alter the `InspectionPrediction` contract, and must not alter
`InspectionEngine.transform_prediction`. The equivalence record is the output of this sprint;
the runtime consumption of the artifact is a later, separately authorized step.

---

## 3. Forbidden Scope

The equivalence-verification sprint **must not**, under any circumstances, perform or produce:

- **provider changes** (no modification to `src/inspection/providers_onnx.py`, including the
  placeholder restriction `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID = "onnx-placeholder-boundary-model-v1"`,
  and no loading of the governed runtime provider at all — equivalence executes against a
  direct `onnxruntime.InferenceSession`, never the provider seam);

- **runtime integration** (the verified artifact must not be loaded into the live `inspect()`
  path; the placeholder must not be retired; the canonical runtime chain
  `InspectionInferenceProvider.predict → InspectionPrediction → transform_prediction →
  RawInspectionResult → Trust → Review → Evidence → Evaluation` must not be exercised with
  the real artifact);

- **model loader changes** (no modification to `src/frameworks/model_loader.py`,
  `src/frameworks/onnx_session.py`, or `src/frameworks/onnx_runtime.py`);

- **preprocessing changes** (no modification to `src/frameworks/image_preprocessing.py`; the
  preprocessing contract `kalibra-padim-rgb64-bilinear-float64-patch8-v1` is fixed by C-4
  and recorded by Task 1 — equivalence verifies *against* the deterministic full-patch
  feature tensor that the offline path already produces, it does not reimplement or alter
  image preprocessing);

- **feature extraction changes** (no modification to the deterministic feature extraction
  path; the feature indices `[0, 2, 5, 6, 7, 9, 12, 13]`, layer
  `fixed_patch_statistics_64x64_patch8`, and backbone
  `kalibra-fixed-patch-feature-backbone-v1` are fixed by C-4 and embedded unchanged in the
  graph — equivalence must reproduce the existing offline feature extraction, not redefine
  it);

- **output mapping changes** (no modification to `src/frameworks/output_mapping.py`,
  including `RAW_MEASURE_SCALE = "placeholder_output_raw_0_100"`; the runtime output scale
  remains the placeholder scale after this sprint);

- **inference pipeline changes** (no modification to `scripts/padim_inference.py` or any
  inference path; the C-5 reference outputs are *consumed*, not regenerated — regenerating
  them would destroy the independence of the comparison);

- **evaluation changes** (no modification to `scripts/scientific_evaluation.py` or the C-6
  evaluation harness; equivalence is **not** evaluation — no Image AUROC, Pixel AUROC,
  AUPRO, Precision, Recall, or F1 is produced or implied);

- **calibration** (no calibrated confidence, no threshold, no operating point, no abstention);

- **Trust changes** (no Trust-domain modification; no calibrated or qualified trust
  statement is produced);

- **Review changes** (no Review-domain modification; no review routing is produced);

- **architecture changes** (no new domain, contract, seam, or domain responsibility; no
  rewiring of the canonical Inspection → Trust → Review → Evidence → Evaluation flow);

- **scientific claims beyond equivalence** (no claim that Kalibra detects defects, no claim
  of product-readiness, no claim of generality, no multi-seed claim, no benchmark);

- **re-export or re-fit** (the governed `model.onnx` is the *input* to verification, not an
  output; the C-4 fit and the C-5 reference are *consumed*, not regenerated; no governed
  source artifact in `data/visa/derived/` may be mutated);

- **any new contract, seam, or domain responsibility**, and any rewiring of the canonical
  runtime flow.

Any of these would exceed the equivalence-verification boundary and requires its own
separate authorization gate. The runtime seam (`InspectionInferenceProvider`,
`InspectionPrediction`, `transform_prediction`, `model_loader`, `onnx_session`) must be
preserved untouched; the equivalence record is produced **off** the runtime path and must not
be wired into it by this sprint.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
artifacts/padim/equivalence/
  equivalence_report.json     # governed equivalence record (per-dimension, per-split, global)
  equivalence_hashes.json     # hashes of every governed equivalence record
  equivalence_replay.json     # governed replay record (second verification == first)
docs/evidence/                # committed governed equivalence evidence report
```

Required artifacts:

- **`equivalence_report.json`** — the governed equivalence record: the verified artifact
  identity (`model.onnx` SHA-256, opset, IR), the consumed governed C-5 reference identity
  (anomaly-map and prediction hashes per split, the C-5 artifact-hashes file hash, the
  inference metadata hash, the aggregation/localization identifiers), the consumed governed
  C-4 identity (μ / Σ⁻¹ hashes, feature indices, layer, backbone, preprocessing contract,
  dtype, ε), the graph-contract verification result (input contract, output contract,
  in-graph feature indices, in-graph μ / Σ⁻¹ byte-equality to C-4), the per-sample, per-split
  and global deviation for the anomaly map (absolute + relative), the raw measure (absolute
  + relative), and the localization (absolute), the sample count (6,492; validation 2,164 +
  test 4,328), the tolerance policy, the pass/fail status per dimension and overall, and the
  machine-readable `scope_boundaries` block with every runtime/evaluation/claim flag set to
  `false`;

- **`equivalence_hashes.json`** — hashes of every governed equivalence artifact
  (`equivalence_report.json` content hash plus the hash of `equivalence_replay.json`), so an
  observer can verify integrity without re-running;

- **`equivalence_replay.json`** — the governed replay record confirming that a second
  equivalence verification over the same governed inputs reproduced identical per-sample
  deviations, identical per-split and global maxima, identical aggregate status, and
  identical governed records (per-record hash agreement), with a `passed` status;

- **governed equivalence evidence report** — a persisted evidence document under
  `docs/evidence/`, written for an untrusting observer, demonstrating artifact verification,
  reference verification, graph-contract verification, anomaly-map equivalence, raw-measure
  equivalence, localization equivalence, tolerance compliance (every tolerance explicit and
  justified), deterministic replay, governed provenance continuity (C-3 → C-4 → C-5 → ONNX
  artifact → equivalence record), no runtime code touched, and the explicit non-claims.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `artifacts/padim/equivalence/equivalence_report.json` | **Committed** — reviewable governed equivalence record |
| `artifacts/padim/equivalence/equivalence_hashes.json` | **Committed** — integrity anchor |
| `artifacts/padim/equivalence/equivalence_replay.json` | **Committed** — reviewable replay proof |
| `docs/evidence/` equivalence evidence report | **Committed** — evidence of a clean, reproducible, governed equivalence verification |
| verification script (e.g. `scripts/verify_padim_onnx_equivalence.py`) | **Committed** — reviewable text |
| verification tests (e.g. `tests/test_padim_onnx_equivalence.py`) | **Committed** — reviewable text |

All equivalence outputs are reviewable JSON / Markdown / Python text; no large binary is
produced by this sprint (the verified `model.onnx` already exists from Task 1 and is not
reproduced). No `.gitignore` change is anticipated; any `.gitignore` update is authorized
**only if strictly required**, minimal, and scoped.

---

## 5. Validation Requirements

The equivalence-verification sprint must validate, and its evidence report must demonstrate,
that:

- **the exported graph reproduces governed offline computation** — the ONNX graph's
  anomaly map, raw measure, and localization match the governed C-5 reference across all
  6,492 samples, with the deviation recorded per sample, per split, and globally;

- **anomaly-map equivalence** — the ONNX `anomaly_map` matches the governed C-5 anomaly maps
  within the pre-declared tolerance, with max absolute and max relative deviation recorded
  per split and globally;

- **raw-measure equivalence** — the ONNX `raw_anomaly_measure` matches the governed C-5
  `predicted_raw_anomaly_measure` within the pre-declared tolerance, with max absolute and
  max relative deviation recorded per split and globally;

- **localization equivalence** — the ONNX `argmax_region` matches the governed C-5
  localization within the pre-declared tolerance, with max absolute deviation recorded per
  split and globally;

- **deterministic replay** — a complete second equivalence verification over the same
  governed inputs reproduces identical per-sample deviations, identical per-split and global
  maxima, identical aggregate status, and identical governed records, recorded in
  `equivalence_replay.json` with per-record hash agreement and `status: passed`;

- **deterministic hashes** — every governed equivalence record has a stable SHA-256 recorded
  in `equivalence_hashes.json`, and a second verification leaves every hash unchanged;

- **governed provenance continuity** — the hash-anchored chain extends unbroken from the C-3
  acquisition through the C-4 fit, the C-5 reference, and the Task 1 ONNX artifact into the
  equivalence record; the consumed artifact hashes (ONNX `model.onnx`, C-5 anomaly maps,
  C-5 predictions, C-5 artifact-hashes file, C-5 inference metadata, C-4 μ / Σ⁻¹ /
  feature-indices) are verified before any comparison and recorded in the equivalence
  report; the verification fails closed on any hash mismatch;

- **no runtime code touched** — `src/inspection/providers_onnx.py`,
  `src/frameworks/model_loader.py`, `src/frameworks/onnx_session.py`,
  `src/frameworks/onnx_runtime.py`, `src/frameworks/output_mapping.py`,
  `src/frameworks/image_preprocessing.py`, `src/inspection/domain.py`, and the
  `InspectionEngine.transform_prediction` path are unchanged; `git status --short --` over
  `src/inspection`, `src/frameworks`, `src/trust`, `src/review`, `src/evidence`,
  `src/evaluation`, `src/integration`, and `src/prototype_ui` produces no output; the
  verified artifact is executed off the runtime path via a direct
  `onnxruntime.InferenceSession` with `CPUExecutionProvider` only, and the governed runtime
  provider is never loaded (`runtime_provider_loaded = false`).

The evidence must record the verification toolchain versions (python, numpy, onnx,
onnxruntime) and the offline execution provider, matching the Task 1 evidence idiom.

---

## 6. Equivalence Policy

The equivalence-verification sprint must verify, **explicitly and fail-closed**, each of the
following equivalences. Every comparison must be against the governed reference, never
against a recomputed or substitute signal.

- **feature-index equivalence** — the feature indices embedded in the ONNX graph are exactly
  `[0, 2, 5, 6, 7, 9, 12, 13]` (dimension 8 of 14), byte-equal to the governed C-4
  `feature_indices.json` and to the in-graph INT64 initializer recorded by Task 1;

- **preprocessing-contract equivalence** — the graph's input contract is exactly
  `kalibra-padim-rgb64-bilinear-float64-patch8-v1`, as fixed by C-4 and recorded by Task 1;
  the verification consumes the deterministic full-patch feature tensor produced by the
  existing offline feature extractor and does **not** reimplement image preprocessing in any
  form (the graph itself does not reimplement preprocessing, and neither does the
  verification);

- **numerical-configuration equivalence** — the dtype policy (`float64` source preserved as
  ONNX DOUBLE, `float32_transition = false`), the covariance estimator, the regularization
  (`ε = 0.001`), and the inverse method (`numpy.linalg.inv`) are exactly as recorded by C-4
  and re-recorded by Task 1; no numerical configuration is re-declared or overridden by the
  verification;

- **μ equivalence** — the per-class μ embedded in the ONNX graph is byte-equal to the
  governed C-4 `statistics/mu_by_class.npy` (hash agreement), verified against the governed
  C-4 hash and against the in-graph DOUBLE `[12, 64, 8]` initializer;

- **Σ⁻¹ equivalence** — the per-class Σ⁻¹ embedded in the ONNX graph is byte-equal to the
  governed C-4 `covariance/covariance_inverse_by_class.npy` (hash agreement), verified
  against the governed C-4 hash and against the in-graph DOUBLE `[12, 64, 8, 8]`
  initializer;

- **graph input contract** — the loaded graph exposes exactly the recorded inputs
  (`full_patch_features[1,64,14] float64`, `class_index[1] int64`) with the recorded names
  and semantics; fail closed on any drift;

- **graph output contract** — the loaded graph exposes exactly the recorded outputs
  (`patch_mahalanobis_distances[1,64]`, `anomaly_map[1,64,64]`, `raw_anomaly_measure[1]`,
  `argmax_region[1,4]`) with the recorded names, shapes, dtypes, and identifiers
  (`padim_anomaly_map_max_v1`, `padim_raw_anomaly_map_argmax_region_v1`); fail closed on any
  drift;

- **tolerance policy** — the anomaly map, raw measure, and localization comparisons each
  carry an explicit, pre-declared tolerance. The sprint inherits the Task 1 demonstrated
  regime as the baseline expectation —
  `{absolute: 1e-12, relative: 1e-12, bbox_absolute: 0.0}` — which Task 1 already met at
  machine-epsilon deviation (max abs/rel `7.1e-15 / 3.6e-15`; bbox `0.0`). The sprint may
  retain this regime or tighten it, but must not silently loosen it.

**Every tolerance must be:**

- **explicit** — declared by name and value in the equivalence report before any comparison
  result is presented, never buried inside a threshold constant;
- **justified** — accompanied by a recorded justification (e.g. "DOUBLE Mahalanobis under
  CPUExecutionProvider reproduces the offline float64 computation at machine epsilon, as
  already demonstrated by Task 1 across 6,492 samples; the declared tolerance is four orders
  of magnitude above the observed maximum"), never asserted without reason;
- **recorded** — written into `equivalence_report.json` and the evidence document, with the
  observed maximum deviation alongside the declared tolerance, so an observer can see both
  the bound and the margin.

A deviation that exceeds its declared tolerance is a verification **failure** that must halt
the sprint and be surfaced — never silently widened. The known, already-evidenced bbox
exactness (Task 1 finding L1: the only achievable coordinate values are multiples of
`1/64 = 2⁻⁶`, and `round(k/64, 6) == k/64` for every `k` in `0..64`, so the declared
`bbox_absolute = 0.0` is exact, not a mask) is carried forward as an accepted justification
for the bbox tolerance; any new finding that contradicts it must be surfaced, not hidden.

---

## 7. Scientific Boundaries

Explicitly:

- **Export equivalence is not runtime equivalence.** Verifying that the ONNX graph reproduces
  the offline C-5 computation off the runtime path is not verifying that the canonical
  `inspect()` path carries that signal. The runtime path is not exercised by this sprint; the
  governed runtime provider is not loaded. Runtime equivalence is the objective of a later,
  separately authorized capability (Phase 3 §6 #4).

- **Export equivalence is not runtime integration.** Producing an equivalence record does not
  connect the verified artifact to the live `inspect()` path. The runtime continues to
  execute the placeholder identity model after this sprint. Runtime provider integration is
  the objective of a later, separately authorized capability (Phase 3 §6 #3).

- **Export equivalence is not scientific evaluation.** Equivalence verification is not
  measuring the system against its claims. No Image AUROC, Pixel AUROC, AUPRO, Precision,
  Recall, F1, or any aggregate score is produced or implied. The C-6 scientific evaluation
  is the *reference of record*; it is not recomputed, extended, or replaced here.

- **Export equivalence produces no new scientific claim.** Its only purpose is to prove that
  the exported artifact faithfully represents the **already-validated** offline PaDiM
  baseline. It does not prove that Kalibra detects defects (that is C-6's bounded,
  single-seed, VisA-proxy claim, unchanged), does not prove the runtime reproduces the
  signal (that is runtime equivalence, separately authorized), and does not prove
  product-readiness, calibration quality, drift response, or generality. The scientific
  claim boundary remains exactly C-6's — single-seed, VisA-proxy, no calibration, no
  confidence, no product-readiness — and this checkpoint makes no claim beyond it.

Kalibra does **not** yet perform real defect detection at runtime, and this checkpoint does
not change that.

---

## 8. Readiness Decision

```text
READY — the repository is ready for a bounded Phase 3 / Task 2 — Export Equivalence
Verification implementation prompt.

- Authorized scope: governed ONNX artifact verification + offline equivalence verification
  against governed C-5 outputs + anomaly-map equivalence + raw-measure equivalence +
  localization equivalence + graph-contract verification + deterministic replay + governed
  equivalence evidence only.
- Forbidden scope: all runtime integration, provider changes, model loader changes, output
  mapping changes, preprocessing changes, feature extraction changes, inference pipeline
  changes, evaluation changes, Trust changes, Review changes, calibration, benchmark
  generation, scientific and product claims, re-export, re-fit, and any architecture change.
- Required outputs, commit policy, validation requirements, equivalence policy, and
  scientific boundaries are defined.
- Nothing verified, compared, integrated, inferred, evaluated, or claimed by this checkpoint.
- No normative document modified.
```

---

## 9. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no equivalence verification** (no comparison run, no deviation computed, no equivalence
  report produced)
- **no runtime integration** (no artifact loaded into the live path, no placeholder retired)
- **no runtime modification** (`providers_onnx.py`, `model_loader.py`, `onnx_session.py`,
  `onnx_runtime.py`, `output_mapping.py`, `image_preprocessing.py`, `domain.py`,
  `transform_prediction` all unchanged)
- **no provider loaded** (no `InspectionInferenceProvider`, no governed runtime provider)
- **no inference** (the runtime inference path is not exercised; only an offline direct
  `onnxruntime.InferenceSession` is anticipated by the authorized scope, and not executed
  here)
- **no evaluation / metric / benchmark**
- **no calibration**
- **no scientific or product claim** beyond the C-6 single-seed VisA-proxy boundary
- **no re-export or re-fit** (the `model.onnx` and the C-4 / C-5 artifacts are inputs, not
  outputs)
- **no documentation modified** (no ADR, Strategy, Evaluation Strategy, or Implementation
  Authorization change)
- **authorization planning only**

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document.

---

## 10. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (no output) ✔ |
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | `a9743b4` (Phase 2 close) ✔ |
| HEAD | `git log -1 --oneline` | `ee43c61 feat: export governed padim onnx artifact` ✔ |
| Architecture baseline | `docs/checkpoints/KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md` | present ✔ |
| Previous capability evidence | `docs/evidence/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md` | present ✔ |
| Export artifact present | `artifacts/padim/model.onnx` (+ `artifact.json`, `metadata.json`, `artifact_hashes.json`, `export_replay.json`) | present ✔ |

The only working-tree change after this review is the creation of this checkpoint document
itself.

---

## 11. Next Natural Step

```text
Review the persisted Export Equivalence Verification Authorization checkpoint before
generating the implementation prompt.
```

If and when the repository owner approves this authorization, the logical next step (per
Phase 3 §6, **not authorized by reviewing this checkpoint**) is to generate the bounded
implementation prompt for Phase 3 / Task 2 — Export Equivalence Verification. Until then,
the runtime continues to run the placeholder, and every claim remains bounded to the offline
single-seed VisA-proxy evidence recorded in C-6.
