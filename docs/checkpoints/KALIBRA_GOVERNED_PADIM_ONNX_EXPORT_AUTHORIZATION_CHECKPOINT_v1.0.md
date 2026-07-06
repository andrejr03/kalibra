# Kalibra Governed PaDiM ONNX Export Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no ONNX export executed, no model exported, no runtime modified)
**Date:** 2026-07-06
**Repository baseline tag:** `ml-phase-2-complete`
**Repository baseline HEAD:** `e898f9f docs: open ml phase 3`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **Phase 3 / Task 1 — Governed
ONNX Export of the fitted PaDiM baseline** implementation. It is authorization planning
only. It exports no ONNX model, generates no ONNX graph, modifies no runtime, modifies no
provider, modifies no model loader, modifies no output mapping, performs no inference,
runs no evaluation, computes no metric, calibrates nothing, and modifies no ADR, Strategy,
Evaluation Strategy, Implementation Authorization, or any normative document.

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

and from the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md),
which establishes Phase 3's objective, scope, ordering (§6, capability #1), integration
risks (§5, R2 export fidelity as a named risk), and the requirement that every Phase 3
capability remain behind its own separate authorization gate before implementation.

This checkpoint defines **what a future export sprint is allowed to do**, what it is
**forbidden** to do, what it must **produce**, and how it must be **validated**. It does
not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3
checkpoints, the Governed VisA Acquisition Authorization checkpoint, the C-4 PaDiM
Baseline Training Authorization checkpoint, and the C-5 Governed PaDiM Inference
Authorization checkpoint, and must be reviewed before any implementation prompt is
generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents and the Phase 3 architecture
checkpoint.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Phase 3 / Task 1 — Governed ONNX Export
```

The authorization is **strictly limited to the deterministic export of the already-fitted
PaDiM baseline into a governed ONNX artifact, produced from the governed C-4 artifacts
only, with deterministic graph generation, governed metadata, governed hashes,
deterministic replay, and governed export evidence**. It grants no permission to integrate
the runtime, change providers, change the model loader, change output mapping, change
preprocessing, change feature extraction, run inference, evaluate, calibrate, generate
benchmarks, or make any scientific or product claim.

**Basis for readiness — why the repository is now technically ready:**

- **The fitted PaDiM baseline exists and is governed.** C-4 completed and recorded the
  deterministic PaDiM baseline fit. The μ
  (`data/visa/derived/padim/statistics/mu_by_class.npy`) and Σ⁻¹
  (`data/visa/derived/padim/covariance/covariance_inverse_by_class.npy`) artifacts exist
  for all 12 VisA classes, with recorded artifact hashes in
  `data/visa/derived/padim/training/artifact_hashes.json`, replay verification in
  `replay_verification.json`, and the governing metadata set
  (`training_metadata.json`, `dataset_identity.json`, `feature_indices.json`,
  `numerical_config.json`, `preprocessing_contract.json`, `backbone_metadata.json`).
  Export therefore has a real, integrity-anchored, reproducible fitted model to export.

- **The offline numerical contract is fully pinned and recorded.** The selected feature
  indices (`[0, 2, 5, 6, 7, 9, 12, 13]`, dimension 8 of 14), the dtype (`float64`), the
  covariance estimator (`sample covariance, centered.T @ centered / (n - 1)`), the
  covariance regularization (`covariance + epsilon * I`, `ε = 0.001`), the inverse
  (`numpy.linalg.inv`), and the preprocessing contract id
  (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`) are all recorded and frozen. An
  ONNX export can therefore faithfully embed exactly these constants — no numerical
  behavior is left implicit.

- **The offline reference signal exists to export faithfully.** C-5 recorded the governed
  offline anomaly measure (`padim_anomaly_map_max_v1`) and localization
  (`padim_raw_anomaly_map_argmax_region_v1`) under the existing `InspectionPrediction`
  contract, with replay verification. The ONNX export can therefore be defined as a
  faithful transcription of an already-validated offline computation, not a new
  computation.

- **The runtime substrate that will eventually receive the artifact is real and ready
  (but is deliberately not touched here).** The phase-opening architecture checkpoint
  independently confirmed that `load_governed_model(...)`, `ProviderPrivateInferenceSession`,
  the `onnx_session` determinism machinery (`CPUExecutionProvider`,
  `intra_op_num_threads = 1`, `inter_op_num_threads = 1`), and the
  `InspectionInferenceProvider.predict` seam already exist and execute. This means the
  export target shape is well-defined; the export can produce an artifact the existing
  substrate can eventually consume. Producing the artifact now does not require — and
  this checkpoint does not authorize — wiring it in.

- **Export fidelity is a named, anticipated risk with an identified mitigation.** The
  phase-opening checkpoint identifies R2 (export fidelity) and R1 (inference equivalence)
  and prescribes the mitigation direction: the export is itself a governed, hash-anchored,
  replay-verified artifact with its own evidence, not an incidental byproduct. This
  authorization enforces that prescription as a scope boundary.

- **The export is the prerequisite for everything downstream in Phase 3, and nothing
  downstream is authorized by producing it.** Per Phase 3 §6, the export is capability
  #1 precisely because offline export-equivalence verification (#2), runtime provider
  integration (#3), end-to-end runtime equivalence (#4), and placeholder retirement (#5)
  all depend on a governed artifact existing. Authorizing the export unblocks that
  ordering without authorizing any of those steps.

Readiness is **for the export only**. Runtime integration, provider changes, model loader
changes, output mapping changes, inference, evaluation, calibration, and any scientific or
product claim each remain behind their own separate authorization gates.

---

## 2. Authorized Scope

If and when the export sprint is authorized by a bounded implementation prompt, it may do
**only** the following:

- **deterministic export of the fitted PaDiM baseline** — transcribe the existing
  per-class μ and Σ⁻¹ together with the offline PaDiM computation (feature-subsample
  selection, per-patch Mahalanobis distance, anomaly-map aggregation to the scalar raw
  measure, localization derivation) into a single ONNX graph, without altering any of the
  underlying numerical behavior;

- **export from governed C-4 artifacts only** — read μ
  (`statistics/mu_by_class.npy`), Σ⁻¹
  (`covariance/covariance_inverse_by_class.npy`), `feature_indices` (the recorded
  `[0, 2, 5, 6, 7, 9, 12, 13]`), and the governing metadata set, verifying each
  artifact hash against `data/visa/derived/padim/training/artifact_hashes.json` before
  use and failing closed on any mismatch — no re-fit, no substitution, no alternate
  baseline;

- **deterministic ONNX graph generation** — emit the ONNX graph deterministically from
  the governed constants, with a pinned, recorded ONNX export toolchain version and
  recorded operator set(s), so a second export reproduces a byte-identical graph;

- **governed ONNX artifact** — produce the exported model as a governed, hash-anchored
  artifact (e.g. `model.onnx`) with a recorded SHA-256 content hash and recorded
  provenance back to the C-4 fitted baseline (μ / Σ⁻¹ hashes, feature indices, layer,
  backbone, preprocessing contract, dtype);

- **governed ONNX metadata** — record the export-time governed metadata (the consumed
  C-4 artifact identity, the preprocessing contract id, the feature indices, the layer,
  the backbone identity, the dtype policy, the export toolchain version, the operator
  set(s), the graph input/output contract, and the export configuration) so the artifact
  is self-describing under governance;

- **governed export hashes** — record hashes of every governed export artifact (the
  `model.onnx` content hash plus the hashes of every accompanying governed record) in an
  `artifact_hashes.json` so an observer can verify integrity without re-running;

- **deterministic replay of export** — re-run the export over the same governed C-4
  artifacts and prove the second export reproduces a byte-identical `model.onnx`
  (matching content hash) and identical accompanying records;

- **governed export evidence** — produce a persisted evidence document written for an
  untrusting observer, demonstrating export reproducibility, deterministic graph,
  deterministic artifact hash, deterministic metadata, deterministic replay, governed
  provenance continuity, and export fidelity (§6).

Nothing beyond this list is authorized. In particular: **no runtime integration, no
provider change, no model loader change, no output mapping change, no preprocessing
change, no feature extraction change, no inference, no evaluation.**

The runtime seams must be respected. The sprint may **produce** a governed ONNX artifact;
it must not load it into the runtime, must not alter `providers_onnx.py`, must not alter
`model_loader.py`, must not alter `output_mapping.py`, must not alter
`image_preprocessing.py`, must not alter the `InspectionPrediction` contract, and must not
alter `InspectionEngine.transform_prediction`. The artifact is the output of this sprint;
its consumption is a later, separately authorized step.

---

## 3. Forbidden Scope

The export sprint **must not**, under any circumstances, perform or produce:

- runtime integration (the exported artifact must not be loaded into the live
  `inspect()` path; the placeholder must not be retired);
- provider changes (no modification to `src/inspection/providers_onnx.py`, including the
  placeholder restriction `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID`);
- model loader changes (no modification to `src/frameworks/model_loader.py`,
  `src/frameworks/onnx_session.py`, or `src/frameworks/onnx_runtime.py`);
- output mapping changes (no modification to `src/frameworks/output_mapping.py`,
  including `RAW_MEASURE_SCALE = "placeholder_output_raw_0_100"`);
- preprocessing changes (no modification to `src/frameworks/image_preprocessing.py`; the
  preprocessing contract `kalibra-padim-rgb64-bilinear-float64-patch8-v1` is fixed by C-4
  and must be embedded unchanged);
- feature extraction changes (no modification to the deterministic feature extraction
  path; the feature indices `[0, 2, 5, 6, 7, 9, 12, 13]`, layer
  `fixed_patch_statistics_64x64_patch8`, and backbone
  `kalibra-fixed-patch-feature-backbone-v1` are fixed by C-4 and must be embedded
  unchanged);
- inference changes (no modification to `scripts/padim_inference.py` or any inference
  path; the export must reproduce the existing offline computation, not redefine it);
- evaluation changes (no modification to `scripts/scientific_evaluation.py` or the C-6
  evaluation harness);
- Trust changes (no calibrated confidence, no abstention, no drift);
- Review changes;
- calibration;
- benchmark generation;
- scientific claims;
- product / product-readiness claims;
- re-fitting of the PaDiM baseline (the C-4 fit is the input; it must not be re-fit or
  re-selected);
- any new contract, seam, or domain responsibility, and any rewiring of the canonical
  Inspection → Trust → Review → Evidence → Evaluation flow.

Any of these would exceed the export boundary and requires its own separate authorization
gate. The runtime seam (`InspectionInferenceProvider`, `InspectionPrediction`,
`transform_prediction`, `model_loader`, `onnx_session`) must be preserved untouched; the
exported artifact is produced **off** the runtime path and must not be wired into it by
this sprint.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
artifacts/padim/
  model.onnx               # governed ONNX artifact (the exported fitted PaDiM baseline)
  artifact.json            # governed ONNX artifact record (identity, provenance, contract)
  artifact_hashes.json     # hashes of every governed export artifact
  metadata.json            # governed export metadata (consumed C-4 identity, toolchain, ops, dtype policy)
  export_replay.json       # governed replay record (second export == first, hash agreement)
docs/evidence/             # committed governed export evidence report
```

Required artifacts:

- **`model.onnx`** — the governed ONNX artifact, a deterministic transcription of the
  fitted PaDiM baseline (per-class μ and Σ⁻¹, the recorded feature-subsample indices, the
  per-patch Mahalanobis distance, the anomaly-map aggregation to the scalar raw measure,
  and the localization derivation), with a recorded SHA-256 content hash;

- **`artifact.json`** — the governed ONNX artifact record: artifact identity, the
  consumed C-4 artifact identity (μ / Σ⁻¹ hashes, feature indices, layer, backbone,
  preprocessing contract, dtype), the graph input/output contract, and the export
  provenance back to the C-4 fit and the C-3 acquisition;

- **`metadata.json`** — the governed export metadata: the export toolchain and version,
  the operator set(s), the dtype policy (including the float64 source / float32-execution
  policy if applicable and the equivalence justification), the export configuration, and
  the governed inputs consumed;

- **`artifact_hashes.json`** — hashes of every governed export artifact (`model.onnx`
  content hash plus the hashes of every accompanying governed record), so an observer can
  verify integrity without re-running;

- **`export_replay.json`** — the governed replay record confirming that a second export
  over the same governed C-4 artifacts reproduced a byte-identical `model.onnx` (matching
  content hash) and identical accompanying records, with per-artifact hash agreement;

- **governed export evidence report** — a persisted evidence document under
  `docs/evidence/` written for an untrusting observer, demonstrating export
  reproducibility, deterministic graph, deterministic artifact hash, deterministic
  metadata, deterministic replay, governed provenance continuity, no runtime modification,
  and export fidelity against the offline C-4/C-5 reference.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `artifacts/padim/model.onnx` | **Committed if lightweight and reviewable** — the governed runtime-bound artifact is the point of the export and must be inspectable; if large, it stays local with its hash committed |
| `artifacts/padim/artifact.json` | **Committed** — reviewable governed artifact record |
| `artifacts/padim/metadata.json` | **Committed** — reviewable governance record |
| `artifacts/padim/artifact_hashes.json` | **Committed** — integrity anchor |
| `artifacts/padim/export_replay.json` | **Committed** — reviewable replay proof |
| `docs/evidence/` export evidence report | **Committed** — evidence of a clean, reproducible, governed export |

The exported `model.onnx` is the load-bearing output of this sprint and is intended to be
inspectable; its disposition (committed vs. local-with-committed-hash) is decided by the
implementation prompt based on its actual size, with the preference toward committing it
so a future observer can inspect the artifact without re-running. The governed JSON
records and the evidence report are the committed, reviewable proof of governed,
reproducible export under all circumstances. Any `.gitignore` update is authorized **only
if required** to prevent accidental commit of a large binary, minimal and scoped strictly
to that purpose.

---

## 5. Validation Requirements

The export sprint must validate, and its evidence report must demonstrate, that:

- **export reproducibility** holds — a complete second export over the same governed C-4
  artifacts reproduces a byte-identical `model.onnx` with identical content hash;

- **deterministic graph** is produced — the ONNX graph is emitted deterministically from
  the governed constants, with a pinned, recorded export toolchain version and recorded
  operator set(s);

- **deterministic artifact hash** — the `model.onnx` content hash is stable across the
  replay, recorded in `artifact_hashes.json`;

- **deterministic metadata** — the governed export metadata is byte-stable across the
  replay (timestamps pinned where required, matching the Phase 2 timestamp-pinning
  practice);

- **deterministic replay** — `export_replay.json` records the second export as identical
  to the first, with per-artifact hash agreement;

- **governed provenance continuity** — the hash-anchored chain extends unbroken from the
  C-3 acquisition through the C-4 fit into the ONNX artifact; the consumed C-4 artifact
  hashes are verified before export and recorded in the export metadata; the export fails
  closed on any C-4 hash mismatch;

- **no runtime modification** — `src/inspection/providers_onnx.py`,
  `src/frameworks/model_loader.py`, `src/frameworks/onnx_session.py`,
  `src/frameworks/onnx_runtime.py`, `src/frameworks/output_mapping.py`,
  `src/frameworks/image_preprocessing.py`, `src/inspection/domain.py`, and the
  `InspectionEngine.transform_prediction` path are unchanged; the exported artifact is
  produced off the runtime path and is not loaded into it.

---

## 6. Export Fidelity Requirements

The future implementation must demonstrate that the exported ONNX reproduces the governed
C-4 PaDiM baseline faithfully. Specifically, the evidence must show:

- **the exported ONNX reproduces the governed C-4 PaDiM baseline** — the graph encodes
  per-class μ and Σ⁻¹, the recorded feature-subsample indices, the per-patch Mahalanobis
  distance, the anomaly-map aggregation to the scalar raw measure, and the localization
  derivation, equivalent to the offline C-5 computation;

- **no change to feature indices** — the embedded feature indices are exactly
  `[0, 2, 5, 6, 7, 9, 12, 13]` (dimension 8 of 14), as recorded by C-4;

- **no change to preprocessing contract** — the graph's input contract is exactly
  `kalibra-padim-rgb64-bilinear-float64-patch8-v1`, as fixed by C-4;

- **no change to numerical configuration** — the dtype policy (`float64` source), the
  covariance estimator, the regularization (`ε = 0.001`), and the inverse method are
  exactly as recorded by C-4; any float64→float32 execution policy is explicit, recorded,
  and justified, and does not silently change the governed numerics;

- **no change to μ** — the embedded per-class μ matches the governed
  `statistics/mu_by_class.npy` (hash agreement);

- **no change to Σ⁻¹** — the embedded per-class Σ⁻¹ matches the governed
  `covariance/covariance_inverse_by_class.npy` (hash agreement).

**No runtime integration yet.** Export fidelity is proven **offline**, against the
governed C-4/C-5 reference, before the artifact is ever handed to the runtime. Demonstrating
that the runtime path reproduces the offline signal is the objective of a later, separately
authorized capability (Phase 3 §6 #2 and #4), not of this export sprint.

Where exact offline reproduction is infeasible at export time (for example, the well-known
float64-vs-float32 divergence flagged as R1/R2 in the phase-opening checkpoint), the
evidence must state the divergence explicitly, record the pre-declared tolerance and its
justification, and quantify the per-class deviation against the offline C-5 reference —
never silently. An unstated divergence is a fidelity failure; a stated, bounded, evidenced
divergence is honest engineering that the next authorization can decide on.

---

## 7. Scientific Boundaries

Explicitly:

- **Export is not runtime integration.** Producing a governed ONNX artifact does not
  connect it to the live `inspect()` path. The runtime continues to execute the
  placeholder identity model after this sprint.

- **Export is not inference.** The export transcribes an already-validated offline
  computation; it does not run that computation on inputs or produce an anomaly measure for
  any image.

- **Export is not evaluation.** Producing an ONNX artifact is not measuring the system
  against its claims. No Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, or any
  aggregate score is produced or implied.

- **Export produces no scientific claim.** A governed ONNX artifact is a prepared runtime
  input, not proof that Kalibra detects defects, not proof that the runtime reproduces
  the offline signal, and not a calibrated or product-ready model. Only evaluation against
  frozen, preserved, untouched evidence can establish detection quality, and only runtime
  equivalence evidence (a later capability) can establish that the runtime carries the
  validated signal.

- **Export prepares the governed runtime artifact only.** The governed `model.onnx` and
  its accompanying records exist so that a later, separately authorized runtime-integration
  capability can load a real, integrity-anchored artifact behind the existing
  `model_loader` / `onnx_session` substrate — never to assert that the runtime already
  carries the real signal.

Kalibra does **not** yet perform real defect detection at runtime, and this checkpoint
does not change that. The scientific claim boundary remains exactly C-6's — single-seed,
VisA-proxy, no calibration, no confidence, no product-readiness — and the export makes no
claim beyond it.

---

## 8. Readiness Decision

```text
READY — the repository is ready for a bounded Phase 3 / Task 1 — Governed ONNX Export
implementation prompt.

- Authorized scope: deterministic export of the fitted PaDiM baseline from governed C-4
  artifacts only + deterministic ONNX graph generation + governed ONNX artifact +
  governed ONNX metadata + governed export hashes + deterministic replay of export +
  governed export evidence only.
- Forbidden scope: all runtime integration, provider changes, model loader changes,
  output mapping changes, preprocessing changes, feature extraction changes, inference
  changes, evaluation changes, Trust changes, Review changes, calibration, benchmark
  generation, scientific and product claims, re-fitting, and any architecture change.
- Required outputs, commit policy, validation requirements, export fidelity requirements,
  and scientific boundaries are defined.
- Nothing exported, generated, integrated, inferred, evaluated, or claimed by this
  checkpoint.
- No normative document modified.
```

---

## 9. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no ONNX export** (no `model.onnx` produced, no graph generated)
- **no runtime integration** (no artifact loaded into the live path, no placeholder
  retired)
- **no runtime modification** (`providers_onnx.py`, `model_loader.py`, `onnx_session.py`,
  `onnx_runtime.py`, `output_mapping.py`, `image_preprocessing.py`, `domain.py`,
  `transform_prediction` all unchanged)
- **no inference**
- **no evaluation / metric / benchmark**
- **no calibration**
- **no scientific or product claim**
- **no re-fitting of the PaDiM baseline**
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
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | resolves to the Phase 2 close ✔ |
| HEAD | `git log -1 --oneline` | `e898f9f docs: open ml phase 3` ✔ |

The only working-tree change after this review is the creation of this checkpoint document
itself.

---

## 11. Next Natural Step

```text
Generate the bounded implementation prompt for Phase 3 / Task 1 — Governed ONNX Export.
```

No governing document is updated in this task. The persisted authorization checkpoint
must be reviewed before the implementation prompt is generated.
