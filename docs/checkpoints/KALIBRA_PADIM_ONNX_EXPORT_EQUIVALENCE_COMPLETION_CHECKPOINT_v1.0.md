# Kalibra PaDiM ONNX Export Equivalence Completion Checkpoint v1.0

**Status:** Recorded — Phase 3 / Task 2 implementation-review completion checkpoint (review only; no source, test, evidence, or governed artifact file was modified by this review beyond re-running the governed verifier, which is write-once idempotent and left every hash unchanged)
**Date:** 2026-07-07
**Branch:** `codex/initial-engineering-skeleton`
**Review HEAD:** `c72b134 docs: authorize onnx export equivalence`
**Review mode:** Pre-commit implementation review
**Review authority:** [PaDiM ONNX Export Equivalence Authorization Checkpoint](KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_AUTHORIZATION_CHECKPOINT_v1.0.md)

## About This Document

This is the completion checkpoint for **Phase 3 / Task 2 — Export Equivalence
Verification**. It records the review decision, findings, validation results, the
export-equivalence governance assessment, the equivalence assessment, the git/storage
assessment, the explicit non-claims, and the next natural step. It is a review
artifact only: it creates no ONNX model, modifies no runtime, provider, model loader,
output mapping, preprocessing, feature extraction, inspection domain, Trust, Review,
Evidence, or Evaluation code, runs no runtime inference, performs no evaluation,
computes no metric, calibrates nothing, and modifies no normative document.

The verifier (`scripts/verify_padim_onnx_equivalence.py`) was executed twice during
this review to confirm deterministic replay; both runs are governed write-once no-ops
that left every equivalence artifact hash byte-identical. No implementation file was
modified by this review.

---

## 1. Decision

```text
PASS — Phase 3 / Task 2 — Export Equivalence Verification is approved for commit.
```

The implementation satisfies every authorized-scope, forbidden-scope, required-output,
validation, equivalence-policy, and scientific-boundary requirement of the governing
authorization checkpoint. It verifies the governed ONNX artifact produced by Task 1
against the governed C-5 reference across all 6,492 samples (validation 2,164 + test
4,328) via a direct `onnxruntime.InferenceSession` with `CPUExecutionProvider` only,
at machine-epsilon deviation well inside the pre-declared `{1e-12, 1e-12, 0.0}`
tolerance, with governed artifact/reference verification, graph-contract verification,
deterministic replay, governed equivalence hashes, and governed equivalence evidence.
No runtime, provider, model-loader, output-mapping, preprocessing, feature-extraction,
inference, evaluation, Trust, or Review code was modified.

The implementation **may be committed**.

---

## 2. Findings by Severity

### Critical

None.

### High

None.

### Medium

None.

### Low (informational, no change required)

- **L1 — Per-class evidence is derivable, not pre-aggregated.** The authorization §4
  binding Required Outputs for `equivalence_report.json` specify "per-sample,
  per-split and global deviation" for each equivalence dimension, and the report
  provides exactly that. Each of the 6,492 `per_sample_deviations` records carries a
  `class_name` field, so per-class maxima can be derived by an observer (confirmed:
  12 classes, maxima range `2.7e-15`–`7.1e-15`, all far inside tolerance). The §1
  readiness narrative also mentioned "per-class" evidence; the report satisfies the
  binding per-sample requirement and preserves class identity rather than
  pre-aggregating a per-class block. No change required; recorded for traceability.

- **L2 — Bbox tolerance of 0.0 is exact, not a rounding mask (carried from Task 1 L1).**
  The localization coordinates are multiples of `1/64 = 2⁻⁶`, and the recorded C-5
  rounded values are bit-identical to the unrounded `k/64` for every achievable `k`
  in `0..64`. The declared `bbox_absolute_tolerance = 0.0` is therefore an equality
  requirement, confirmed empirically: max localization deviation is exactly `0.0`
  across all 6,492 samples. No change required.

- **L3 — Equivalence verified against recorded (rounded) C-5 reference, not a fresh
  recomputation.** The anomaly-map and raw-measure references are read from the
  governed C-5 `predictions/{split}_predictions.jsonl` and
  `anomaly_maps/{split}_anomaly_maps.npy`, and the localization reference from the
  recorded rounded bbox. This is the governed reference of record and the correct
  basis for an independent equivalence check; regenerating C-5 would destroy the
  independence the authorization requires. No change required.

- **L4 — Evidence embeds the tolerance policy as a Python dict repr.** The
  `tolerance_policy` is written into the evidence markdown as `repr(dict)`, matching
  the Phase 2 / Task 1 evidence idiom. The governed JSON
  (`equivalence_report.json`) carries the canonical structured form; the markdown is
  the human-facing summary. No change required.

### Positive observations

- **O1 — Every governed artifact and reference hash was independently confirmed.**
  This review recomputed the SHA-256 of the Task 1 ONNX artifact set
  (`model.onnx`, `artifact.json`, `metadata.json`, `export_replay.json`,
  `artifact_hashes.json`), the C-4 reference set (`training_record`,
  `artifact_hashes`, `training_metadata`, `replay_verification`, `mu_by_class`,
  `covariance_inverse_by_class`, `feature_indices`), and the C-5 reference set
  (`artifact_hashes`, `inference_metadata`, `replay_verification`, both anomaly-map
  arrays, both prediction jsonl files). Every hash matches the values hard-coded in
  the verifier and recorded in the evidence exactly.

- **O2 — μ and Σ⁻¹ byte-equality to C-4 was independently confirmed at the ONNX
  initializer level.** Beyond the verifier's internal check, this review loaded
  `model.onnx`, extracted the `mu_by_class`, `covariance_inverse_by_class`, and
  `feature_indices` initializers via `numpy_helper.to_array`, and confirmed
  byte-equality against the governed C-4 `.npy` files (dtype, shape, and contiguous
  bytes all identical). The graph embeds exactly the governed C-4 statistics.

- **O3 — Fail-closed is enforced at every seam.** The verifier raises
  `EquivalenceError` on: missing/mutated governed artifact (hash mismatch), schema
  drift, replay status not `passed`, non-static ONNX shapes, graph initializer drift,
  preprocessing-implementation flag flipped to true, image-preprocessing input
  contract present, non-`CPUExecutionProvider` provider loaded, output-order drift,
  sample-count/split-count drift, any tolerance exceeded, and any deterministic-replay
  field mismatch. The replay comparison requires all seven comparison fields true.

- **O4 — Deterministic replay is enforced three ways.** (a) two complete equivalence
  runs are compared per-sample, per-split, globally, and on pass/fail status;
  (b) the two generated report byte-strings are compared for byte-identical equality;
  (c) the governed `equivalence_replay.json` records the comparison and is itself
  hash-anchored. A second full `verify` invocation during this review was a write-once
  no-op (idempotent guard), confirming on-disk determinism.

- **O5 — Scope-boundary flags are exhaustive and explicitly false.** The report's
  29-field `scope_boundaries` block sets every runtime/provider/model-loader/output-
  mapping/preprocessing/feature-extraction/inspection/trust/review/evidence/evaluation/
  integration/prototype-ui/re-export/re-fit/re-inference/evaluation/metric/calibration/
  benchmark/scientific-claim/product-claim flag to `false`. The 14-entry
  `explicit_non_claims` list restates them in prose.

- **O6 — Tests cover the three independent failure modes.** The test suite exercises
  graph-contract verification against a fixture model (including byte-equality
  assertions for feature indices, μ, Σ⁻¹), fail-closed replay on a per-sample
  deviation mismatch, and the hashes-record coverage of report and replay artifacts.

- **O7 — Execution path is unambiguously off-runtime.** The session is constructed
  directly from `model_bytes` via `ort.InferenceSession(..., providers=["CPUExecutionProvider"])`,
  `session.get_providers()` is asserted to equal exactly `["CPUExecutionProvider"]`,
  graph optimizations are disabled (`ORT_DISABLE_ALL`, single-threaded), and no `src/`
  module is imported. The only mentions of `inspection_engine`/`model_loader` in the
  verifier are the `False` scope-boundary assertions.

---

## 3. Required Changes

None. The implementation is approved for commit as-is.

---

## 4. Export Equivalence Governance Assessment

| Governance requirement (Auth §2, §4, §5) | Result |
| --- | --- |
| Governed ONNX artifact verified before comparison | ✔ PASS (5 Task 1 hashes verified before any session load) |
| Governed C-4 identities verified | ✔ PASS (7 C-4 identity hashes verified against `artifact_identity` and files) |
| Governed C-5 identities verified | ✔ PASS (C-5 artifact-hashes, metadata, replay, 4 local outputs, labels, identifiers) |
| Provenance continuity (C-3 → C-4 → C-5 → ONNX → equivalence) | ✔ PASS (identity chain recorded in `governed_c4_identity` / `governed_c5_identity` / `onnx_artifact_identity`) |
| Graph contract verified (inputs, outputs, opset, IR, initializers) | ✔ PASS (`verify_graph_contract`) |
| Feature indices verified (`[0, 2, 5, 6, 7, 9, 12, 13]`) | ✔ PASS (byte-equal to C-4 and exact) |
| μ byte-equal to governed C-4 | ✔ PASS (DOUBLE `[12, 64, 8]`, independently confirmed) |
| Σ⁻¹ byte-equal to governed C-4 | ✔ PASS (DOUBLE `[12, 64, 8, 8]`, independently confirmed) |
| Preprocessing contract verified | ✔ PASS (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`; not reimplemented in ONNX) |
| ONNX graph executed only through direct `onnxruntime.InferenceSession` | ✔ PASS |
| `CPUExecutionProvider` only | ✔ PASS (constructed with + runtime-asserted) |
| Runtime provider never loaded | ✔ PASS (`runtime_provider_loaded = false`; no `src/` import) |
| Model loader never loaded | ✔ PASS (`model_loader_loaded = false`) |
| Runtime integration never attempted | ✔ PASS (`runtime_integration_performed = false`) |
| Fail-closed behavior | ✔ PASS (every seam raises `EquivalenceError` on drift) |
| Replay governance (second run == first) | ✔ PASS (`equivalence_replay.json` status `passed`, 7/7 comparisons true) |
| Equivalence hashes deterministic | ✔ PASS (second `verify` invocation left all hashes unchanged) |

The equivalence verification is governed, reproducible, hash-anchored, and
provenance-continuous. It fails closed on every governed-input mutation and on every
deviation that exceeds its declared tolerance.

---

## 5. Equivalence Assessment

| Equivalence requirement (Auth §6) | Result |
| --- | --- |
| Anomaly-map equivalence | ✔ PASS (max abs `7.105e-15` ≤ 1e-12; max rel `3.587e-15` ≤ 1e-12) |
| Raw-anomaly-measure equivalence | ✔ PASS (max abs `7.105e-15` ≤ 1e-12; max rel `3.587e-15` ≤ 1e-12) |
| Localization equivalence | ✔ PASS (max abs `0.0` ≤ 0.0; exact, see finding L2) |
| Tolerance compliance (explicit, justified, respected) | ✔ PASS (`declared_before_comparison = true`; all three justifications recorded; all maxima inside bounds) |
| Replay stability | ✔ PASS (per-sample, per-split, global, status, report bytes all identical across two runs) |
| Numerical fidelity | ✔ PASS (float64 source preserved as ONNX DOUBLE; `float32_transition = false`; ε=0.001; `numpy.linalg.inv`) |
| Sample coverage | ✔ PASS (6,492 samples: validation 2,164 + test 4,328; per-split counts asserted) |
| Per-sample/per-split/global deviation recorded | ✔ PASS (6,492 per-sample records; per-split maxima for both splits; global maxima) |

**Observed deviation regime.** All three equivalence dimensions sit at machine
epsilon (~7.1e-15 absolute for anomaly map and raw measure; exactly 0.0 for
localization), four to five orders of magnitude inside the pre-declared 1e-12
tolerance. This reproduces the regime Task 1 already demonstrated and is consistent
with a DOUBLE Mahalanobis computation under `CPUExecutionProvider` reproducing the
offline float64 PaDiM computation.

---

## 6. Git / Storage Assessment

| Concern | Result |
| --- | --- |
| `git status --short` shows only intended new files | ✔ PASS |
| `git diff --check` clean | ✔ PASS (exit 0) |
| Runtime/domain scope check (`src/inspection`, `src/frameworks`, `src/trust`, `src/review`, `src/evidence`, `src/evaluation`, `src/integration`, `src/prototype_ui`) | ✔ PASS (no output — untouched) |
| `git diff --stat` against tracked files | ✔ PASS (empty — no tracked file modified) |
| `data/visa/derived/` (governed C-4/C-5 artifacts) | ✔ PASS (consumed read-only; hashes unchanged) |
| `artifacts/padim/` (Task 1 governed export) | ✔ PASS (consumed read-only; `model.onnx` and records unchanged) |
| New `artifacts/padim/equivalence/` artifacts reviewable | ✔ PASS (3 JSON files; report is large but text/reviewable) |
| `.gitignore` | ✔ PASS (unchanged; no edit needed) |

**Working-tree changes after review:**

```text
?? artifacts/padim/equivalence/
?? docs/evidence/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md
?? docs/checkpoints/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_COMPLETION_CHECKPOINT_v1.0.md
?? scripts/verify_padim_onnx_equivalence.py
?? tests/test_padim_onnx_equivalence.py
```

The `artifacts/padim/equivalence/` directory contains the three governed equivalence
records (`equivalence_report.json`, `equivalence_hashes.json`,
`equivalence_replay.json`). All are reviewable JSON text; no binary is produced by
this sprint (the verified `model.onnx` already exists from Task 1 and is not
reproduced). The completion checkpoint is the only file added by this review.

**Commit suitability:** the verification script, the tests, the governed equivalence
JSON records, the evidence report, and this checkpoint are all reviewable text and are
intended to be committed.

---

## 7. Validation Summary

All validation commands requested by the task were run and passed.

| Validation | Command | Result |
| --- | --- | --- |
| Equivalence verification | `python3 scripts/verify_padim_onnx_equivalence.py verify` | ✔ exit 0 (first run) |
| Equivalence verification (replay) | `python3 scripts/verify_padim_onnx_equivalence.py verify` | ✔ exit 0 (second run; write-once no-op; all hashes unchanged) |
| Test suite | `python3 -m pytest -q` | ✔ 485 passed in 23.64s |
| Byte-compile | `python3 -m compileall -q src tests scripts` | ✔ exit 0 |
| Whitespace | `git diff --check` | ✔ exit 0 (clean) |
| Working tree | `git status --short` | ✔ only intended new files |
| Runtime/domain scope | `git status --short -- src/inspection src/frameworks src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui` | ✔ no output (untouched) |

**Governed-hash cross-check.** Every hash recorded in the evidence file
(`docs/evidence/KALIBRA_PADIM_ONNX_EXPORT_EQUIVALENCE_EVIDENCE_v1.0.md`) was verified
against the governed artifacts on disk by this review:

- Task 1 ONNX artifact set (5 hashes) — all match.
- C-4 reference set (7 hashes) — all match.
- C-5 reference set (7 hashes) — all match.
- Equivalence report/replay/hashes — all match and stable across two runs.

**Report-vs-evidence consistency.** The five global-maxima values recorded in the
evidence markdown exactly match the `global_maxima` block of `equivalence_report.json`.

---

## 8. Completion Summary

```text
Phase 3 / Task 2 — Export Equivalence Verification completed successfully.
```

The implementation:

- verified the governed `artifacts/padim/model.onnx` (SHA-256
  `0437ae28…741a`) against its recorded Task 1 artifact/hashes records before any
  comparison, failing closed on any mismatch;
- verified the governed C-4 identity (μ, Σ⁻¹, feature indices, training metadata,
  replay) and the governed C-5 identity (artifact hashes, inference metadata, replay,
  anomaly maps, predictions, aggregation/localization identifiers) before any
  comparison;
- verified the ONNX graph contract (inputs, outputs, opset 18, IR 10, in-graph
  initializers byte-equal to C-4) before any comparison;
- executed the governed ONNX graph offline via a direct
  `onnxruntime.InferenceSession` with `CPUExecutionProvider` only, graph optimizations
  disabled, single-threaded, never loading the runtime provider, the model loader, or
  the canonical `inspect()` path;
- compared the graph's anomaly map, raw measure, and localization against the governed
  C-5 reference across all 6,492 samples (validation 2,164 + test 4,328), recording
  per-sample, per-split, and global deviations;
- passed all three equivalence dimensions at machine-epsilon deviation inside the
  pre-declared `{1e-12, 1e-12, 0.0}` tolerance, with every tolerance explicit,
  justified, and declared before comparison;
- proved deterministic replay via two complete equivalence runs (per-sample, per-split,
  global, status, and report bytes all identical) recorded in a governed
  `equivalence_replay.json`;
- produced governed `equivalence_report.json`, `equivalence_hashes.json`,
  `equivalence_replay.json`, and a governed evidence document;
- modified **no** runtime, provider, model-loader, output-mapping, preprocessing,
  feature-extraction, inference, evaluation, Trust, or Review code;
- added **no** runtime capability, and **no** evaluation, metric, calibration,
  benchmark, scientific, or product claim.

```text
- governed equivalence established;
- replay deterministic;
- governed evidence recorded;
- runtime untouched;
- runtime integration not performed.
```

---

## 9. Explicit Non-Claims

This checkpoint explicitly records that Phase 3 / Task 2:

- established **export equivalence only**;
- **export equivalence is not runtime equivalence** — the canonical `inspect()` path
  was not exercised; runtime equivalence remains a separately authorized capability
  (Phase 3 §6 #4);
- **export equivalence is not runtime integration** — the verified artifact was not
  loaded into the live path; the placeholder identity model remains the runtime model;
  runtime provider integration remains a separately authorized capability (Phase 3 §6
  #3);
- **export equivalence is not scientific evaluation** — no Image AUROC, Pixel AUROC,
  AUPRO, Precision, Recall, F1, or any aggregate score is produced or implied; the
  C-6 single-seed VisA-proxy evaluation is the reference of record and is unchanged;
- loaded **no runtime provider** — fidelity used a direct
  `onnxruntime.InferenceSession` with `CPUExecutionProvider` only; the governed
  runtime provider (`src/inspection/providers_onnx.py`) was never loaded;
- **no runtime capability was added** — the runtime continues to run the placeholder;
- changed **no** provider, model-loader, output-mapping, preprocessing,
  feature-extraction, inspection-domain, Trust, Review, Evidence, or Evaluation code;
- produced **no metrics**;
- produced **no benchmark**;
- performed **no calibration**;
- made **no scientific claim** — the scientific-claim boundary remains exactly C-6's
  (single-seed, VisA-proxy, no calibration, no confidence, no product-readiness);
- made **no product claim** — Kalibra does not yet perform real defect detection at
  runtime, and this task does not change that.

---

## 10. Commit Decision

```text
YES — the Phase 3 / Task 2 Export Equivalence Verification implementation may be committed.
```

All authorized-scope, forbidden-scope, required-output, validation, equivalence-policy,
and scientific-boundary requirements are satisfied. The working tree contains only
intended new files (`scripts/verify_padim_onnx_equivalence.py`,
`tests/test_padim_onnx_equivalence.py`, the governed `artifacts/padim/equivalence/`
records, the evidence report, and this checkpoint). No governed source, test, runtime,
domain, or evaluation file was modified. Commit control remains with the repository
owner.

---

## 11. Next Natural Step

```text
Review this persisted Export Equivalence Verification Completion Checkpoint before
opening the authorization checkpoint for Phase 3 / Task 3 — Runtime Provider
Integration.
```

Runtime provider integration is **not authorized** by the completion of this task. It
remains behind its own separate authorization gate, as required by the governing
authorization checkpoint and the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md).
Until that gate is opened, the runtime continues to execute the placeholder identity
model, and every claim remains bounded to the offline single-seed VisA-proxy evidence
recorded in C-6.

---

## 12. Validation of This Checkpoint

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Scope | `git status --short` | only intended new files ✔ |

This checkpoint is a review artifact. It executes no code, modifies no source, and
creates no model.
