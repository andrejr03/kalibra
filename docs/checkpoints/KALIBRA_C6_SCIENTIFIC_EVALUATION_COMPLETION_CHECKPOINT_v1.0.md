# Kalibra C-6 Scientific Evaluation Completion Checkpoint v1.0

**Status:** Recorded — engineering-completion checkpoint (bounded C-6 scientific evaluation completed; single-seed VisA proxy evidence recorded; no calibration, no ONNX export, no multi-seed characterization, no product-facing capability)
**Date:** 2026-07-06
**Repository baseline HEAD:** `9684d05 docs: authorize scientific evaluation`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **completed C-6 Scientific Evaluation review** as a
versioned repository checkpoint. It is an engineering-completion artifact. It persists the
review that was produced after the C-6 implementation was written and validated. It does
not summarize the review, does not reinterpret it, and does not modify any ADR, Dataset
Strategy, Evaluation Strategy, or Implementation Authorization gate.

It records that the bounded scope authorized in the
[Scientific Evaluation Authorization Checkpoint](KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md)
has been implemented and validated against every authorized boundary. It authorizes
nothing further. It does **not** authorize calibration, ONNX export, multi-seed
characterization, or any product-facing capability.

It draws its standing from the same lineage as the authorization checkpoint: the
[Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
(PaDiM selected first), the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) and the
[Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
(`SELECTED — VisA`), the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md),
the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
the [C-4 PaDiM Baseline Training Completion Checkpoint](KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md),
the [C-5 Governed PaDiM Inference Completion Checkpoint](KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md),
the [Scientific Evaluation Authorization Checkpoint](KALIBRA_SCIENTIFIC_EVALUATION_AUTHORIZATION_CHECKPOINT_v1.0.md),
and the recorded
[Scientific Evaluation Evidence](../evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md).

Throughout, **must**, **must not**, and **completed** carry the binding sense established
across the ML Phase 2 documents ([`AGENTS.md`](../../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)).

---

## 1. Decision

```text
PASS
```

All required validations pass. No must-fix or should-fix findings. The implementation
honors every C-6 governance boundary and the engineering philosophy (evidence before
assertion, reproducibility, honesty over capability, explicit boundaries, depth over
breadth, one source of truth for inspection and trust qualification).

The C-6 scientific evaluation implementation **may be committed**.

---

## 2. Review Findings

- **No must-fix findings.**
- **No should-fix findings.**

One observation is persisted below as engineering knowledge. It does not block commit.

### 2.1 O-1 — `evaluation_metadata.json` embeds the full C-5 `sample_artifacts` map (~3.7 MB committed)

The committed `data/visa/derived/padim/evaluation/metadata/evaluation_metadata.json` is
approximately 3.7 MB. The bulk of that size is the `inference_identity.sample_artifacts`
field, which embeds the full 6,492-entry per-sample artifact map
(`{input_id → {prediction_sha256, anomaly_map_sha256, feature_tensor_sha256, ...}}`)
copied from the governed C-5 inference `artifact_hashes.json`.

- **This is acceptable for C-6.** It is consistent with the established C-4 / C-5
  convention, where the governed `artifact_hashes.json` record (3.6 MB for C-5) is itself
  committed because it is the reviewable governance record an untrusting observer uses to
  verify integrity without re-running. The C-6 `.gitignore` additions follow the same
  allow-list pattern C-5 uses (commit the governance records under `metadata/`, `replay/`,
  `metrics/`, `per_class/`, `operating_point/`, `failure_analysis/`, and
  `artifact_hashes.json`; keep only a dedicated `evaluation/local/` directory ignored),
  and the authorization's commit policy explicitly permits committing lightweight,
  reviewable governance records. No binary `.npy` anomaly maps, source images, or model
  objects are committed.
- **Future work may factor the per-sample map out of metadata** if repository size becomes
  a concern, but this is not required by the authorization and is not a C-6 blocker.

---

## 3. Required Changes

None. The implementation satisfies every authorized boundary and every validation
requirement of the C-6 authorization (§2 authorized scope, §3 forbidden scope, §4 required
outputs, §5 validation requirements, §6 scientific claim policy).

---

## 4. Scientific Evaluation Governance Assessment

The implementation executes the **frozen C-2 Evaluation Protocol** as a pure, read-only
function of governed inputs and produces governed evidence. Governance was verified as
follows:

### 4.1 Governed acquisition verified before evaluation

`verify_governed_acquisition_inputs()` calls `training.verify_governed_acquisition()` and
additionally hash-verifies the archive metadata, attribution, and every upstream split CSV
before any evaluation input is loaded. Evaluation fails closed on any mismatch. ✔

### 4.2 Frozen split manifests verified

`load_split_samples()` loads `validation.csv` and `test.csv`, validates the exact manifest
header, and verifies every image and mask row's `sha256` against the governed
`files.sha256` manifest plus the on-disk artifact before use. Split-level identities are
anchored through C-4 / C-5 (`TRAIN_SPLIT_SHA256`, `VALIDATION_SPLIT_SHA256`,
`TEST_SPLIT_SHA256`) and re-derived from governed acquisition. ✔

### 4.3 Governed C-5 inference outputs consumed

`load_anomaly_maps()` reads `{validation,test}_anomaly_maps.npy` from the C-5 inference
directory and verifies each per-input anomaly-map SHA-256 against the C-5
`sample_artifacts` map. `load_prediction_records()` reads the C-5 prediction JSONL records
and verifies each prediction's canonical-JSON SHA-256 against the same map. The C-5
`artifact_hashes.json`, inference metadata, and replay record are hash-verified first. ✔

### 4.4 Governed `InspectionPrediction` records consumed (not the contract field)

`validate_prediction_record()` consumes `predicted_raw_anomaly_measure`, the recorded
predicted localization, and the governed `model_metadata` only. It explicitly checks
`raw_measure_kind == "raw_anomaly_measure"` and
`raw_measure_scale == "model_raw_anomaly_measure"`, and it never reads the inference-layer
`predicted_judgement` field as a classification — honoring C-5 completion checkpoint O-1
and authorization §6. Evaluation derives its own thresholded operating point from raw
measures and labels. ✔

### 4.5 No source images, providers, runtime objects, or model objects consumed directly

Imports are limited to the standard library, `numpy`, `PIL.Image`, and the three governed
scripts (`governed_visa_acquisition`, `padim_inference`, `train_padim_baseline`). There is
no import of `src/inspection`, no ONNX runtime, no provider protocol, and no model object
load. The only `PIL.Image` use reads governed VisA **pixel ground-truth masks** (dataset
labels required for Pixel AUROC / AUPRO) from the governed extracted directory after a
SHA-256 check — never inspection images via a provider, and never model objects. Metadata
records `source_images_read: false`, `providers_used: false`,
`model_objects_loaded: false`, `inference_rerun: false`. ✔

### 4.6 No retraining, refitting, or re-inference

`scope_boundaries` records `retraining_performed: false`, `refitting_performed: false`,
`inference_rerun: false`, `preprocessing_modified: false`,
`feature_extraction_modified: false`, `provider_modified: false`,
`output_mapping_modified: false`. All twelve scope-boundary flags are closed (`False`). The
C-4 statistics/covariance artifacts and C-5 anomaly maps are read-only inputs. ✔

### 4.7 No downstream architecture modified

The downstream scope check (`git status --short` over `src/inspection`, `src/frameworks`,
`src/trust`, `src/review`, `src/evidence`, `src/evaluation`, `src/integration`,
`src/prototype_ui`) produced **no output**. No Trust, Review, Evidence, Evaluation-Engine
architecture, runtime, integration, or prototype-UI code was modified. Evaluation is not
wired into `inspect()` or the canonical Inspection → Trust → Review → Evidence →
Evaluation flow. ✔

---

## 5. Metric and Evidence Assessment

### 5.1 Official metrics

- **Image AUROC** is computed and recorded as the **primary** official metric
  (`official_metrics.official_metrics.primary == "Image AUROC"`), per-class over all 12
  VisA classes, threshold-free via average-rank (tie-handling verified by a unit test). ✔
- **Pixel AUROC** and **AUPRO** are computed and recorded as the **secondary** official
  metrics (`secondary == ["Pixel AUROC", "AUPRO"]`), reported together with the
  background-dominance caveat on Pixel AUROC. AUPRO is computed per connected component up
  to `AUPRO_MAX_FPR = 0.30` and normalized by that range. ✔
- A macro mean is reported **only beside** the full per-class table, with caveats; it is
  never a standalone headline. ✔

Recorded macro-mean official figures (VisA governed proxy, single seed):

| Metric | Value |
| --- | --- |
| Image AUROC (primary) | `0.757826` |
| Pixel AUROC (secondary) | `0.865196` |
| AUPRO (secondary) | `0.555765` |

### 5.2 Diagnostic-only metrics

**Precision, Recall, and F1** are computed and recorded as **diagnostic only**, at the
single validation-derived operating point applied unchanged to test, with both error kinds
exposed separately (true/false positives and negatives, never netted). The diagnostic
record carries `diagnostic_only: true` and explicit non-claims ("Diagnostic Precision,
Recall, and F1 are not headline metrics"; "F1 was not maximized on test"; "The operating
point is not calibrated and not a product threshold"). F1 is never an official score and is
never maximized on test. ✔

Recorded diagnostic figures (VisA governed proxy, single seed, at validation-derived
operating point): Precision `0.209019`, Recall `0.714583`, F1 `0.323432`; TP `343`, FP
`1298`, TN `2550`, FN `137`.

### 5.3 Operating point

The operating point is **derived only from the validation split** by the pre-registered
rule `validation_balanced_fpr_fnr_v1` (minimize the absolute validation FPR/FNR gap;
tie-break by lower max error rate, lower total error count, then higher threshold), then
applied **unchanged** to test. It is recorded as `diagnostic_only: true`,
`not_calibrated: true`, `not_product_threshold: true`. Validation-derived value:
`2.445569`. **No product threshold and no calibrated confidence was produced.** ✔

### 5.4 Failure analysis

The failure-analysis record covers, for all 12 VisA classes: false positives (1,298),
false negatives (137), per-class summaries, localization failures (237, defined as
true-positive anomaly images where the governed C-5 predicted box has zero overlap with the
resized governed pixel mask), boundary cases (10 per class, the closest raw-measure margins
to the operating point, framed strictly as raw-measure behavior and not uncertainty
quality), and five proxy-domain limitations. ✔

### 5.5 Deterministic replay

`build_replay_record()` runs a **complete second evaluation** over the same governed
inputs and compares metrics, operating point, failure analysis, reports, and per-record
hashes. All five comparisons are `true`, with `complete_second_evaluation_run: true` and
identical first/second run report hashes. The standalone `verify` command re-derives every
record and hash and fails closed on any byte-level mismatch against the committed governed
records. ✔

### 5.6 Single-seed limitation explicitly recorded

`single_seed_limitation` records `single_seed: true`, `deterministic_seed: 271828`,
`multi_seed_variance_available: false`, `confidence_intervals_available: false`. The
evidence document states the single-seed limitation, the absence of variance estimation,
and the absence of confidence intervals. ✔

### 5.7 Evidence-value verification

All ten known evidence values match the committed governed records exactly (Image AUROC,
Pixel AUROC, AUPRO, Precision, Recall, F1, operating point, FP, FN, localization
failures). ✔

---

## 6. Git and Storage Assessment

### 6.1 Changed paths

```text
M  .gitignore
?? scripts/scientific_evaluation.py
?? tests/test_scientific_evaluation.py
?? docs/evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md
?? data/visa/derived/padim/evaluation/
```

Only the intended paths changed. `git diff --check` reports no whitespace errors.

### 6.2 `.gitignore`

The `.gitignore` delta extends the existing `data/visa/derived/padim/` allow-list family
with minimal, purpose-scoped `evaluation/` rules: it allows the governed governance
records (`metadata/`, `metrics/`, `per_class/`, `failure_analysis/`, `operating_point/`,
`replay/`, `artifact_hashes.json`) and ignores only a dedicated
`data/visa/derived/padim/evaluation/local/` directory for any large local-only
derivatives. This matches the established C-5 pattern and the authorization's commit
policy. The current run produced no `evaluation/local/` contents.

### 6.3 Committed governed artifacts

The committed governed evaluation records are JSON governance records. The two largest are
`metadata/evaluation_metadata.json` (~3.7 MB, dominated by the embedded C-5
`sample_artifacts` map — see O-1) and `failure_analysis/failure_analysis.json` (~1.1 MB,
the inspectable per-sample FP/FN/localization/boundary records). Both are reviewable text
records, regenerable from the governed inputs, and consistent with the C-4/C-5 commit
convention. No binary `.npy` anomaly maps, source images, extracted images, or model
objects are committed.

### 6.4 Downstream scope

The downstream scope check over all `src/` domain directories produced **no output**,
confirming no downstream architecture, runtime, provider, Trust, Review, Evidence,
Evaluation-Engine, integration, or prototype-UI modification.

---

## 7. Validation Summary

| Validation | Command | Result |
| --- | --- | --- |
| Evaluation verify (initial) | `python3 scripts/scientific_evaluation.py verify` | exit 0 ✔ |
| Evaluation evaluate | `python3 scripts/scientific_evaluation.py evaluate` | exit 0 ✔ |
| Evaluation verify (post-evaluate) | `python3 scripts/scientific_evaluation.py verify` | exit 0 ✔ |
| Test suite | `python3 -m pytest -q` | 479 passed, 1 skipped ✔ |
| Byte-compile | `python3 -m compileall -q src tests scripts` | exit 0 ✔ |
| Whitespace | `git diff --check` | exit 0 ✔ |
| Status | `git status --short` | only the 4 intended paths ✔ |
| Downstream scope | `git status --short -- src/inspection src/frameworks src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui` | no output ✔ |
| Evidence values | all 10 known values vs committed records | exact match ✔ |

The single skipped test predates this change and is unrelated to C-6.

---

## 8. Completion Summary

C-6 completed **scientific evaluation only**. The frozen C-2 Evaluation Protocol has been
executed as a pure, read-only function over the governed VisA acquisition, the frozen split
manifests, the governed C-4 PaDiM baseline artifacts, and the governed C-5 inference
outputs (anomaly maps and `InspectionPrediction` records). A single validation-derived
operating point was derived and applied unchanged to test. Deterministic replay was
performed over a complete second evaluation run and reproduces identical metrics, operating
point, failure analysis, reports, and hashes. Governed evaluation evidence has been
recorded.

**Image AUROC, Pixel AUROC, and AUPRO are now available as bounded single-seed VisA proxy
metrics**, reported per class across all 12 VisA classes, with a macro mean reported only
beside the full per-class table. **Precision, Recall, and F1 are diagnostic only**,
reported at the validation-derived operating point with both error kinds exposed
separately. **The operating point is validation-derived, not calibrated, and not a product
threshold.** **The result is single-seed only; no variance estimation or confidence
intervals exist.**

The implementation changed no preprocessing, feature extraction, provider, output mapping,
Trust, Review, Evidence Engine, Evaluation-Engine architecture, runtime, integration, or
prototype-UI code. No retraining, refitting, re-inference, calibration, ONNX export, or
benchmark generation occurred.

---

## 9. Explicit Allowed Claims and Prohibited Claims

### 9.1 Allowed (bounded, single-seed, VisA proxy only)

Each of the following is permitted **only** with the per-class table, both error kinds
reported separately, single-seed limitation disclosed, failures reported separately, and
proxy-domain limitations stated, and each is bounded by the single-seed limitation:

- **Bounded Image AUROC claim** — on the governed VisA proxy dataset, on the untouched
  frozen per-class test partition, the governed PaDiM baseline's raw anomaly measure
  separates sound from defective images, quantified by image-level AUROC per class
  (macro mean `0.757826`), reproducible by an untrusting observer.
- **Bounded Pixel AUROC claim** — reported **with** the background-dominance caveat (macro
  mean `0.865196`).
- **Bounded AUPRO claim** — bounded per-region localization signal on VisA pixel masks
  (macro mean `0.555765`), reported with VisA's incomplete upstream annotation-process
  documentation disclosed.
- **Reproducibility claim** — the accepted figures are regenerable from the pinned governed
  inputs, the frozen split manifests, the C-4 model artifacts, the C-5 inference outputs,
  and the recorded evaluation configuration by an untrusting observer.

### 9.2 Prohibited (regardless of evaluation outcome)

- **No production, product-readiness, accuracy-for-users, robustness, SaaS, deployment,
  cloud, or commercialization claim.**
- **No cross-domain or generalization claim** from the VisA proxy.
- **No calibrated-confidence claim**, and **no presenting the raw anomaly measure or the
  validation-derived operating point as a probability, confidence, or trust statement.**
- **No benchmark, ranking, leaderboard, state-of-the-art, or comparison claim** (including
  against published VisA numbers).
- **No uncertainty-quality, abstention, review-routing, or drift claim** (no Trust, Review,
  or drift evidence basis in this baseline).
- **No multi-seed variance or confidence-interval claim** that the single-seed baseline
  cannot support.

Any claim not explicitly allowed by §9.1 is, by default, **not made**.

---

## 10. Commit Authorization

```text
PASS — the C-6 scientific evaluation implementation may be committed.
```

The C-6 implementation may be committed by the repository owner. This checkpoint does not
commit anything (per the Git Rules in AGENTS.md, agents never run `git add`, `git commit`,
or `git push`).

The following remain **unauthorized** and each requires its own separate authorization
gate before any work may begin:

- **calibration** (Trust-domain calibrated confidence);
- **ONNX export** (governed model serialization);
- **multi-seed characterization** (re-fitting over a pre-registered seed set to produce
  per-class variance and confidence intervals);
- **any product-facing capability** (production, product-readiness, cross-domain, or
  benchmark claim).

---

## 11. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **C-6 completed scientific evaluation only** — no calibration, no ONNX export, no
  multi-seed characterization, no product-facing capability.
- **Image AUROC, Pixel AUROC, and AUPRO are now available as bounded single-seed VisA proxy
  metrics** (per-class primary; macro mean beside the per-class table only).
- **Precision, Recall, and F1 are diagnostic only.**
- **The operating point is validation-derived, not calibrated, and not a product
  threshold.**
- **The result is single-seed only; no variance estimation or confidence intervals exist.**
- **No production, cross-domain, calibrated-confidence, benchmark-leadership, or
  product-readiness claim is authorized.**
- **Calibration, ONNX export, multi-seed characterization, and product-facing capability
  remain unauthorized.**
- **No downstream architecture, runtime, provider, Trust, Review, Evidence Engine,
  Evaluation-Engine architecture, integration, or prototype-UI code was modified.**
- **No ADR, Dataset Strategy, Evaluation Strategy, or Implementation Authorization gate was
  modified.**

Kalibra does not yet perform calibrated, production-grade defect detection, and this
checkpoint does not change that. It records that one governed, single-seed scientific
evaluation of one governed VisA + PaDiM baseline has been executed and evidenced; it does
not assert that the baseline is good, and it makes no product claim.

---

## 12. Next Natural Step

```text
Review this persisted C-6 completion checkpoint before authorizing any calibration,
ONNX export, multi-seed characterization, or product-facing capability work.
```

No governing document is updated in this task. The persisted completion checkpoint must be
reviewed before any further authorization gate is opened.
