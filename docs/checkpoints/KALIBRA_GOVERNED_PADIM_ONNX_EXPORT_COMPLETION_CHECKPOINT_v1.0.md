# Kalibra Governed PaDiM ONNX Export Completion Checkpoint v1.0

**Status:** Recorded — Phase 3 / Task 1 implementation-review completion checkpoint (review only; no source, test, evidence, or artifact file was modified by this review)
**Date:** 2026-07-07
**Branch:** `codex/initial-engineering-skeleton`
**HEAD (review baseline):** `7f6cb35 docs: authorize governed padim onnx`
**Review mode:** Pre-commit implementation review
**Review authority:** [Governed PaDiM ONNX Export Authorization Checkpoint](KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_AUTHORIZATION_CHECKPOINT_v1.0.md)

## About This Document

This is the completion checkpoint for **Phase 3 / Task 1 — Governed ONNX Export of the fitted
PaDiM baseline**. It records the review decision, findings, validation results, the
export-governance assessment, the fidelity assessment, the git/storage assessment, the explicit
non-claims, and the next natural step. It is a review artifact only: it creates no ONNX model,
modifies no runtime, provider, model loader, output mapping, preprocessing, feature extraction,
inspection domain, Trust, Review, Evidence, or Evaluation code, runs no inference, performs no
evaluation, computes no metric, calibrates nothing, and modifies no normative document.

---

## 1. Decision

```text
PASS — Phase 3 / Task 1 — Governed ONNX Export is approved for commit.
```

The implementation satisfies every authorized-scope, forbidden-scope, required-output,
validation, fidelity, and scientific-boundary requirement of the governing authorization
checkpoint. The export produced a governed, hash-anchored, replay-verified ONNX artifact from
governed C-4 inputs only, with deterministic graph generation, byte-identical replay, and
export fidelity passing against the governed C-5 reference at machine-epsilon deviation. No
runtime, provider, model-loader, output-mapping, preprocessing, feature-extraction, inference,
evaluation, Trust, or Review code was modified. The exported `model.onnx` is a governed artifact
and is **not yet a runtime artifact**.

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

- **L1 — Bbox tolerance of 0.0 is mathematically exact, not a hidden rounding risk.** The
  offline C-5 localization rounds the normalized bounding box to 6 decimals
  (`localization_from_anomaly_map`), while the ONNX graph computes the unrounded
  `pixel_index / 64` coordinate. Because the only achievable coordinate values are multiples of
  `1/64 = 2⁻⁶`, and `round(k/64, 6) == k/64` holds for **every** `k` in `0..64` (verified), the
  two formulations are bit-identical for every input the system can ever observe. The declared
  `bbox_absolute_tolerance = 0.0` is therefore honest and exact, not a tolerance that masks
  divergence. No change required; recorded for traceability.

- **L2 — Fidelity verified against recorded (rounded) C-5 predictions, not a fresh
  recomputation.** The export's `verify_export_fidelity` reads the bbox reference from the
  recorded `predictions/{split}_predictions.jsonl` (the rounded C-5 values) rather than
  recomputing the offline localization. This is consistent with how the raw-measure and
  anomaly-map references are also read from recorded C-5 artifacts, and — combined with L1 —
  introduces no hidden error. No change required; recorded for traceability.

- **L3 — Fidelity executed against the full 6,492-sample inference set, but per-split only.**
  `verify_export_fidelity` iterates both `validation` (2,164) and `test` (4,328) splits and
  records per-split maxima plus the global maxima. This is the governed C-5 set; no held-out or
  evaluation-only data is touched. No change required.

- **L4 — Evidence and metadata embed toolchain versions as a Python dict repr.** Values such as
  the toolchain and tolerance maps are written to evidence as `repr(dict)`. This is
  human-readable and matches the established Phase 2 evidence idiom, but is not strictly
  canonical JSON inside the markdown. The governed JSON records (`artifact.json`,
  `metadata.json`) carry the canonical form; the markdown is the human-facing summary. No change
  required.

### Observations (positive)

- **O1 — Export replay is enforced three ways.** (a) two in-process `build_onnx_model_bytes`
  calls are compared byte-for-byte before any artifact is written; (b) two complete
  `build_export_records` builds are compared byte-for-byte; (c) a governed `export_replay.json`
  records the comparison and is itself hash-anchored. A mismatch at any stage raises
  `ExportError` and halts. This is stronger than the authorization required.

- **O2 — Write-once governance.** `write_governed_bytes` refuses to overwrite an existing
  artifact with differing bytes, so a second `export` run is a no-op (or a fail-closed guard)
  rather than a silent mutation. Confirmed: re-running `export` left all artifact hashes
  unchanged.

- **O3 — C-4 hash verification is mandatory and pre-export.** `verify_authorized_c4_artifact_set`
  verifies every required C-4 array, metadata record, and the training metadata hash before any
  graph construction begins. The export cannot proceed on a mutated or partial C-4 set.

- **O4 — C-5 reference is verified, not just consumed.** `load_c5_reference` verifies the C-5
  artifact-hashes file, every referenced metadata/local-output artifact, the replay record, the
  inference metadata schema, the aggregation/localization identifiers, and the artifact-identity
  chain back to C-4, and requires `evaluation_executed is False` for export safety.

- **O5 — Scope-boundary flags are exhaustive and explicitly false.** Both `artifact.json` and
  `metadata.json` record a 16-field `scope_boundaries` block with every runtime/evaluation/
  claim flag set to `false`. This is the machine-readable form of the explicit non-claims.

---

## 3. Required Changes

None. The implementation is approved for commit as-is.

---

## 4. Governed ONNX Export Assessment

| Authorization requirement (§2, §4) | Result |
| --- | --- |
| Deterministic export of the fitted PaDiM baseline | ✔ PASS |
| Export from governed C-4 artifacts only | ✔ PASS |
| C-4 artifact hashes verified before export | ✔ PASS (`verify_authorized_c4_artifact_set`) |
| No PaDiM re-fit | ✔ PASS (no training code invoked; `data/visa/derived/` untouched) |
| No training artifact mutated | ✔ PASS (`git status --short -- data/` clean) |
| Deterministic ONNX graph generation | ✔ PASS (two in-process builds byte-identical; `onnx.helper` construction) |
| Governed `model.onnx` with recorded SHA-256 | ✔ PASS (`0437ae28…741a`) |
| Governed `artifact.json` (identity, provenance, contract) | ✔ PASS |
| Governed `metadata.json` (consumed C-4 identity, toolchain, ops, dtype policy) | ✔ PASS |
| Governed `artifact_hashes.json` (integrity anchor) | ✔ PASS |
| Deterministic replay → `export_replay.json` | ✔ PASS (status `passed`; per-artifact hash agreement) |
| Governed export evidence report | ✔ PASS (`docs/evidence/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md`) |
| Graph embeds feature indices `[0, 2, 5, 6, 7, 9, 12, 13]` | ✔ PASS (verified in-graph as INT64 initializer) |
| Graph embeds governed μ | ✔ PASS (DOUBLE `[12, 64, 8]`, byte-equal to C-4 μ) |
| Graph embeds governed Σ⁻¹ | ✔ PASS (DOUBLE `[12, 64, 8, 8]`, byte-equal to C-4 Σ⁻¹) |
| Graph implements per-patch Mahalanobis distance | ✔ PASS (`Gather`→`Sub`→`Einsum bpi,bpij,bpj->bp`→`Max`→`Sqrt`) |
| Graph implements anomaly-map max aggregation | ✔ PASS (8×8 `Tile` to 64×64; `ReduceMax` over axes `[1,2]`) |
| Graph implements argmax-region localization | ✔ PASS (`Equal`/`Where`/`ReduceMin`/`ReduceMax` mask; normalized `[x_min,y_min,x_max,y_max]`) |
| Graph input/output contracts match `artifact.json`/`metadata.json` | ✔ PASS |
| Dtype policy explicit; C-4 float64 preserved as ONNX DOUBLE | ✔ PASS (DOUBLE tensors; `float32_transition=false`) |
| Opset / IR pinned and recorded | ✔ PASS (opset 18, IR 10) |
| Export toolchain version recorded | ✔ PASS (python/numpy/onnx/onnxruntime) |

The export is governed, reproducible, hash-anchored, and provenance-continuous from C-3 → C-4 →
C-5 → ONNX artifact. Every governed export artifact (`model.onnx`, `artifact.json`,
`metadata.json`, `export_replay.json`) is hash-recorded in `artifact_hashes.json`, and the
`artifact_hashes.json` self-hash is recorded in evidence.

---

## 5. Export Fidelity Assessment

| Fidelity requirement (§6) | Result |
| --- | --- |
| Exported ONNX reproduces governed C-4 PaDiM baseline | ✔ PASS |
| No change to feature indices | ✔ PASS (`[0, 2, 5, 6, 7, 9, 12, 13]`) |
| No change to preprocessing contract | ✔ PASS (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`, recorded as graph input semantics; not reimplemented in ONNX) |
| No change to numerical configuration (dtype, ε, inverse) | ✔ PASS (float64 source/ONNX; ε=0.001 recorded in `artifact.json`) |
| No change to μ | ✔ PASS (byte-equal to C-4 μ_by_class) |
| No change to Σ⁻¹ | ✔ PASS (byte-equal to C-4 covariance_inverse_by_class) |
| Fidelity checked against governed C-5 reference outputs | ✔ PASS (6,492 samples: validation 2,164 + test 4,328) |
| Max anomaly-map abs/rel deviation within tolerance | ✔ PASS (7.1e-15 / 3.6e-15 ≤ 1e-12) |
| Max raw-measure abs/rel deviation within tolerance | ✔ PASS (7.1e-15 / 3.6e-15 ≤ 1e-12) |
| Max argmax-region abs deviation within tolerance | ✔ PASS (0.0 ≤ 0.0; see finding L1) |
| Runtime provider not loaded | ✔ PASS (`CPUExecutionProvider` direct session; `runtime_provider_loaded=false`) |

**Independent confirmation.** An out-of-band spot-check re-ran the offline C-5 computation
(`mahalanobis_patch_distances`, `anomaly_map_from_patch_distances`,
`aggregate_raw_anomaly_measure`, `localization_from_anomaly_map`) and compared it against the
ONNX graph outputs for representative samples across both splits. Observed deviations were at
machine-epsilon (~1e-15) for the anomaly map and raw measure, and exactly 0.0 for the bbox,
consistent with the recorded evidence.

**Known limitations (carried into evidence).** The graph input is the deterministic full-patch
feature tensor, not image pixels; the preprocessing contract is recorded and required but **not**
reimplemented inside the ONNX graph; the artifact is **not** wired into
`src/inspection/providers_onnx.py`; export fidelity is **not** runtime equivalence and **not**
scientific evaluation.

---

## 6. Git / Storage Assessment

| Concern | Result |
| --- | --- |
| `git status --short` shows only intended new files | ✔ PASS |
| `git diff --check` clean | ✔ PASS (exit 0) |
| Runtime/domain scope check (`src/inspection`, `src/frameworks`, `src/trust`, `src/review`, `src/evidence`, `src/evaluation`, `src/integration`, `src/prototype_ui`) | ✔ PASS (no output — untouched) |
| `data/visa/derived/` (governed C-4/C-5 artifacts) | ✔ PASS (clean — no mutation) |
| `.gitignore` | ✔ PASS (unchanged; no edit was needed) |
| `model.onnx` size | 500 KB (500,109 bytes) — small enough to commit and inspect |
| `model.onnx` ignored? | No — commitable |

**Working-tree changes after review:**

```text
?? artifacts/
?? docs/evidence/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_EVIDENCE_v1.0.md
?? docs/checkpoints/KALIBRA_GOVERNED_PADIM_ONNX_EXPORT_COMPLETION_CHECKPOINT_v1.0.md
?? scripts/export_padim_onnx.py
?? tests/test_padim_onnx_export.py
```

The `artifacts/` directory contains the five governed export artifacts
(`model.onnx`, `artifact.json`, `artifact_hashes.json`, `metadata.json`, `export_replay.json`).
Per the authorization §4 commit policy, `model.onnx` is lightweight (~500 KB) and reviewable, so
it is intended to be committed as a governed, inspectable artifact. No `.gitignore` change is
required.

**Commit suitability:** the governed JSON records, the evidence report, the export script, and
the tests are all reviewable text and are intended to be committed. The `model.onnx` binary is
small and governed by its committed SHA-256 in `artifact.json` / `artifact_hashes.json`.

---

## 7. Validation Summary

All validation commands requested by the task were run and passed.

| Validation | Command | Result |
| --- | --- | --- |
| Verify (pre-export) | `python3 scripts/export_padim_onnx.py verify` | ✔ exit 0 |
| Export (determinism) | `python3 scripts/export_padim_onnx.py export` | ✔ exit 0 (write-once no-op; hashes unchanged) |
| Verify (post-export) | `python3 scripts/export_padim_onnx.py verify` | ✔ exit 0 |
| Test suite | `python3 -m pytest -q` | ✔ 482 passed in 13.74s |
| Byte-compile | `python3 -m compileall -q src tests scripts` | ✔ exit 0 |
| Whitespace | `git diff --check` | ✔ exit 0 (clean) |
| Working tree | `git status --short` | ✔ only intended new files |
| Runtime/domain scope | `git status --short -- src/inspection src/frameworks src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui` | ✔ no output (untouched) |
| `model.onnx` size | `ls -lh artifacts/padim/model.onnx` | ✔ 500 KB |

**Known-values cross-check.** All 18 values supplied in the review task
(`model_sha256`, `opset`, `onnx_ir_version`, `onnx_dtype`, `source_dtype`,
`float32_transition`, `sample_count`, the four anomaly-map/raw-measure deviation pairs,
`max_argmax_region_absolute_deviation`, the three tolerances,
`runtime_provider_loaded`, `preprocessing_reimplemented_in_onnx`,
`localization_represented_in_onnx`) match the recorded evidence exactly. Every deviation is
within its pre-declared tolerance.

---

## 8. Completion Summary

Phase 3 / Task 1 — Governed ONNX Export is **complete and verified**. The implementation:

- transcribed the already-fitted C-4 PaDiM baseline (per-class μ, Σ⁻¹, the governed feature
  indices, the per-patch Mahalanobis distance, the anomaly-map max aggregation, and the
  argmax-region localization) into a single deterministic ONNX graph (opset 18, IR 10, 29 nodes);
- consumed **only** governed C-4 artifacts, verifying each hash before use;
- produced a governed, hash-anchored `model.onnx` (500 KB) plus governed `artifact.json`,
  `metadata.json`, `artifact_hashes.json`, and `export_replay.json`;
- proved deterministic export via two in-process builds and a governed replay record;
- proved export fidelity against the full governed C-5 reference set (6,492 samples) at
  machine-epsilon deviation, well inside the pre-declared 1e-12 tolerance;
- preserved the C-4 float64 dtype as ONNX DOUBLE with no float32 transition;
- modified **no** runtime, provider, model-loader, output-mapping, preprocessing,
  feature-extraction, inference, evaluation, Trust, or Review code;
- added **no** inference capability to the runtime, and **no** evaluation, metric, calibration,
  benchmark, scientific, or product claim.

---

## 9. Explicit Non-Claims

This checkpoint explicitly records that Phase 3 / Task 1:

- completed **ONNX export only**;
- is **not runtime integration** — the artifact is produced off the runtime path and is not
  loaded into `inspect()`;
- is **not inference** — it transcribes an already-validated offline computation; it does not
  produce an anomaly measure for any image at runtime;
- is **not evaluation** — no Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, F1, or any
  aggregate score is produced or implied;
- loaded **no runtime provider** — fidelity used a direct `onnxruntime.InferenceSession` with
  `CPUExecutionProvider` only; the governed runtime provider was not loaded;
- changed **no** provider, model-loader, output-mapping, preprocessing, feature-extraction,
  inspection-domain, Trust, Review, Evidence, or Evaluation code;
- `model.onnx` is a **governed artifact, not yet a runtime artifact**;
- preprocessing is recorded as a **contract** (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`)
  but is **not implemented inside the ONNX graph** — the graph input is the deterministic
  full-patch feature tensor, not image pixels;
- export fidelity **passed** against the governed C-5 reference, but export fidelity is
  **not runtime equivalence**;
- **runtime equivalence remains unauthorized**;
- **runtime integration remains unauthorized**;
- no calibrated confidence, threshold, operating point, abstention, review routing, or drift
  behavior is introduced;
- Kalibra does **not** yet perform real defect detection at runtime, and this task does not
  change that. The scientific-claim boundary remains exactly C-6's (single-seed, VisA-proxy, no
  calibration, no confidence, no product-readiness).

---

## 10. Whether Implementation May Be Committed

```text
YES — the Phase 3 / Task 1 Governed ONNX Export implementation may be committed.
```

All authorized-scope, forbidden-scope, required-output, validation, fidelity, and scientific-
boundary requirements are satisfied. The working tree contains only intended new files
(`scripts/export_padim_onnx.py`, `tests/test_padim_onnx_export.py`, the governed
`artifacts/padim/` records, the evidence report, and this checkpoint). No governed source, test,
runtime, domain, or evaluation file was modified. Commit control remains with the repository
owner.

---

## 11. Next Natural Step

```text
Review this persisted Governed ONNX Export completion checkpoint before authorizing
export-equivalence verification (Phase 3 §6 capability #2) or runtime integration
(Phase 3 §6 capability #3).
```

Neither export-equivalence verification nor runtime integration is authorized by the completion
of this task. Each remains behind its own separate authorization gate, as required by the
governing authorization checkpoint and the phase-opening
[ML Phase 3 Runtime Integration Architecture Checkpoint](KALIBRA_ML_PHASE_3_RUNTIME_INTEGRATION_ARCHITECTURE_CHECKPOINT_v1.0.md).

---

## 12. Validation of This Checkpoint

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Scope | `git status --short` | only intended new files ✔ |

This checkpoint is a review artifact. It executes no code, modifies no source, and creates no
model.
