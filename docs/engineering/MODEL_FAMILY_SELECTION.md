# Model Family Selection

**Date:** 2026-07-05

## 1. Repository State / Baseline

The engineering infrastructure is treated as complete. The runtime executes
`Image → Deterministic preprocessing → Tensor → Placeholder ONNX model → Governed
output mapping → InspectionPrediction`, with the placeholder identity model as the
only model. Two grounding facts from the substrate shape this decision:

- The semantic output contract is a **single scalar raw-anomaly measure in [0,100]**,
  thresholded into `ok` / `defect`; current localization is synthesized
  deterministically rather than model-derived.
- The Scientific Architecture ranks **one-class / distribution-based anomaly
  detection** as the strong fit and treats ViT / foundation / multimodal approaches
  as premature. The dominant selection axes are determinism, governed ONNX export,
  and deterministic replay — not peak accuracy.

## 2. Decision Summary

- **Recommended first model family: PaDiM.**
- **PatchCore is reserved as the planned second-generation model candidate**, to be
  adopted once the real map → prediction pipeline and an evaluation baseline are
  proven.

Selection is weighted by: determinism; governed ONNX export; deterministic replay;
explainability / localization; offline simplicity; and architecture compatibility.

## 3. Candidate Model Family Comparison

Weighted for Kalibra's priorities (determinism > governed ONNX export >
explainability/localization > offline simplicity > accuracy ceiling):

| Family | Learning | Determinism | ONNX export maturity | Localization | Footprint | MPDD/VisA fit | First-model verdict |
|---|---|---|---|---|---|---|---|
| **PaDiM** | Closed-form (per-patch Gaussian, Mahalanobis) | Highest — no SGD; only a seeded feature-subsample | Cleanest — backbone + precomputed inverse-covariance as fixed matmul | Dense anomaly map | Moderate | Strong (both aligned) | **Best first** |
| **PatchCore** | Training-free memory bank + coreset + kNN | High, but coreset/kNN need seed & tie-break pinning | Medium — kNN/memory-bank not ONNX-native | Excellent map | Large memory bank | Strongest | Best second |
| **EfficientAD** | SGD (student-teacher + AE) | Medium | Medium | Good | Low, very fast | Strong | Premature |
| **FastFlow** | SGD normalizing flow | Lower (flow export quirks) | Medium/low | Good | Moderate | Good | Premature |
| **Reverse Distillation** | SGD teacher-student | Medium | Medium | Good | Higher | Good | Premature |
| **DRAEM** | SGD + synthetic anomalies | Lower (synthetic-defect randomness) | Medium | Good | Moderate | Good | Premature |
| **STFPM** | SGD feature-pyramid matching | Medium | Medium | Good | Low | Good | Premature |
| **CFA** | SGD + memory bank | Medium | Medium/low | Good | Moderate | Good | Premature |
| **SimpleNet** | SGD + synthetic negatives | Medium | Medium | Good | Low | Strong | Premature |

The field splits cleanly: **PaDiM and PatchCore are training-free / closed-form** and
dominate the determinism, replay, and explainability axes the infrastructure phase
was built to enforce. All seven SGD-trained families introduce gradient-training
nondeterminism, heavier export surface, and (DRAEM/SimpleNet) synthetic-anomaly design
burden — wrong for a *first* replacement of a placeholder.

## 4. Technical Justification

- **PaDiM is closed-form / deterministic-first.** It fits per-patch multivariate
  Gaussians and scores with Mahalanobis distance — no SGD, no coreset. The only
  randomness (feature-dimension subsampling) is fully controlled by a pinned seed.
- **PaDiM has a cleaner ONNX export path than PatchCore.** Mahalanobis scoring is
  `(f − μ)ᵀ Σ⁻¹ (f − μ)` with precomputed μ and Σ⁻¹, composing with the backbone into
  a fixed graph of standard ONNX ops. PatchCore's memory-bank kNN is not ONNX-native.
- **PaDiM produces anomaly maps suitable for both raw measure and localization.** The
  distance map directly supplies the scalar raw measure and a real, model-derived
  bounding box, replacing the current synthesized localization.
- **PaDiM fits both MPDD and VisA better as a first baseline** than SGD-heavy or
  synthetic-anomaly approaches; it needs only normal samples and suits position-
  aligned industrial imagery.
- **PatchCore is the stronger second-generation candidate** — higher accuracy and
  localization ceiling — to adopt after the PaDiM baseline validates the real
  map → prediction pipeline.

## 5. Migration Strategy — Placeholder Identity → PaDiM

Smallest migration; no substrate redesign.

**Unchanged infrastructure (reused verbatim):**
- Provider boundary — `predict(StabilizedInspectionInput) → InspectionPrediction`
  seam unchanged.
- Deterministic Model Loader — unchanged.
- ONNX Runtime substrate (and session substrate) — unchanged.
- Governed Model Artifact system — unchanged; it references a real `.onnx`.
- `InspectionEngine.transform_prediction(...)` — unchanged.
- Downstream Trust / Review / Evidence / Evaluation — unchanged.
- Deterministic-replay machinery (content and configuration hashing) — unchanged.

**Required future deltas (localized):**
1. **Dataset closure** — an approved, governed dataset must exist first (see C-1).
2. **Offline PaDiM fitting** — fit backbone + per-patch μ + Σ⁻¹ on the normal split,
   with a pinned feature-subsample seed (out-of-band, not a runtime change).
3. **ONNX export** — compose backbone + Mahalanobis scorer into one governed graph;
   replace the placeholder artifact; regenerate artifact metadata/hash.
4. **Real image tensor contract upgrade** — replace the 4×4-PGM / scalar contract with
   a real image → normalized CHW float tensor, under a new preprocessing contract id.
5. **Output mapping upgrade** — reduce the real anomaly map to a scalar raw measure
   (rescaled into the existing [0,100] band) and a real localization box, retiring the
   placeholder scalar/synthesized-localization path. The output contract, status rule,
   and downstream handoff are preserved; only the *source* of the values changes from
   fabricated to model-derived.

## 6. Scientific Risks

- **Alignment assumption.** PaDiM is position-sensitive; MPDD pose variation may
  degrade localization/scoring (VisA is better aligned). Verify registration during
  evaluation.
- **Covariance conditioning.** Few normal samples yield ill-conditioned Σ; requires
  deterministic regularization (Σ + εI). Determinism is preserved.
- **Backbone provenance / licensing.** PaDiM relies on an ImageNet-pretrained CNN
  whose weights carry a license and provenance obligation to be governed as a
  first-class artifact.
- **Raw measure is not confidence.** The map-statistic → [0,100] rescaling is
  arbitrary until the evaluation phase fixes a real operating point; the raw measure
  must not be presented as calibrated confidence (a Trust-domain concern).
- **ONNX determinism across hardware / providers.** Convolution kernels can be
  nondeterministic across providers/devices; pin opset, disable nondeterministic
  optimizations, and prove fixed-output behavior per target device.
- **Accuracy ceiling.** PaDiM sits below PatchCore / EfficientAD; the first baseline
  may be modest — the accepted cost of maximal determinism, bounded by the planned
  PatchCore successor.

## 7. Scope Boundaries and Explicit Non-Claims

- This record approves no sprint and changes no code or governed logic.
- The placeholder model's behavior is **not** a scientific result.
- Kalibra does **not** yet perform real defect detection.
- No product-readiness claim is made or implied.
- Nothing here concerns UI, SaaS, deployment, cloud, or commercialization.

## 8. Final Recommendation

Adopt **PaDiM** as Kalibra's first real learned model family, replacing the
placeholder identity graph, and reserve **PatchCore** as the deliberate second model
once the real map → prediction pipeline and evaluation baseline are proven. One
choice, no hedge: **PaDiM first.**

## 9. Next Natural Step

Review the persisted ML capability record documents before committing, then begin
**C-1 Dataset Selection Closure & Governed Acquisition** as the highest-value phase.
See
KALIBRA_ML_CAPABILITY_ENGINEERING_STRATEGY_record_v1.0.md.
