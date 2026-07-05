# Kalibra Scientific Evaluation Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no evaluation executed, no metric computed)
**Date:** 2026-07-06
**Repository baseline HEAD:** `300b808 feat: implement governed padim inference`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future **C-6 — Scientific
Evaluation** implementation. It is authorization planning only. It runs no evaluation,
scores no metric, derives no threshold, performs no failure analysis, calibrates nothing,
exports no ONNX, fits no model, runs no inference, and modifies no ADR, Dataset Strategy,
Evaluation Strategy, or Implementation Authorization gate.

It draws its authority from the now-normative decisions recorded in:

- the [Scientific Model Family Selection Checkpoint](KALIBRA_SCIENTIFIC_MODEL_FAMILY_SELECTION_CHECKPOINT_v1.0.md)
  (PaDiM selected first; PatchCore reserved second);
- the [Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) and the
  [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)
  (`SELECTED — VisA`);
- the [Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md)
  (§5 dataset partition policy, §6 metric policy, §7 statistical validation, §8
  calibration boundary, §9 explainability, §10 failure analysis, §11 benchmark policy,
  §12 claim policy, §13 evaluation approval criteria);
- the [C-1 Dataset Selection Closure Checkpoint](KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md);
- the [C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md);
- the [C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md)
  and the recorded
  [Governed VisA Acquisition Evidence](../evidence/KALIBRA_GOVERNED_VISA_ACQUISITION_EVIDENCE_v1.0.md);
- the [C-4 PaDiM Baseline Training Completion Checkpoint](KALIBRA_C4_PADIM_BASELINE_TRAINING_COMPLETION_CHECKPOINT_v1.0.md)
  and the recorded
  [PaDiM Baseline Training Evidence](../evidence/KALIBRA_PADIM_BASELINE_TRAINING_EVIDENCE_v1.0.md);
- the [C-5 Governed PaDiM Inference Completion Checkpoint](KALIBRA_C5_GOVERNED_PADIM_INFERENCE_COMPLETION_CHECKPOINT_v1.0.md)
  and the recorded
  [Governed PaDiM Inference Evidence](../evidence/KALIBRA_GOVERNED_PADIM_INFERENCE_EVIDENCE_v1.0.md).

This checkpoint defines **what a future evaluation sprint is allowed to do**, what it is
**forbidden** to do, what it must **produce**, and how it must be **validated**. It does
not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3 checkpoints,
the Governed VisA Acquisition Authorization checkpoint, the C-4 PaDiM Baseline Training
Authorization checkpoint, and the C-5 Governed PaDiM Inference Authorization checkpoint,
and must be reviewed before any implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents
([`AGENTS.md`](../../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)).

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — C-6 Scientific Evaluation
```

The authorization is **strictly limited to the read-only, evidence-only execution of the
frozen C-2 Evaluation Protocol over governed VisA partitions, governed PaDiM inference
outputs, and governed `InspectionPrediction` records, the derivation of a single
validation-derived operating point, the deterministic replay of the evaluation, and the
generation of governed evaluation evidence**. It grants no permission to retrain, refit,
change preprocessing or feature extraction, change inference, change the provider seam,
change any downstream domain, calibrate, export ONNX, or make any product claim.

**Basis for readiness — why the repository is now scientifically and technically ready:**

- **The frozen evaluation protocol exists.** C-2 fixed the first scientific evaluation
  protocol for the VisA + PaDiM pairing: per-class one-class partitions, the frozen
  train/validation/test partition policy (§2.1), the governed input tuple (§2.2), the
  official metric set (Image AUROC primary; AUPRO and Pixel AUROC secondary), the
  diagnostic-only metric set (Precision, Recall, F1 at a validation-derived operating
  point), the validation-derived operating-point rule (§2.4), the statistical protocol
  (§2.5), and the failure-analysis protocol (§2.6). Evaluation therefore has a real,
  already-fixed procedure to execute, not one to invent.
- **The governed dataset exists and is verified.** C-3 implemented and evidenced the
  governed VisA acquisition — the immutable source archive, the per-file SHA-256
  manifest, the provenance and attribution records, and the immutable split manifests.
  C-4 and C-5 each independently re-verified the archive, files manifest, split hashes,
  and provenance before consuming the dataset. Evaluation therefore has a real, governed
  input with integrity anchors it can verify before use.
- **The frozen split manifests exist and are hash-anchored.** `train.csv`,
  `validation.csv`, and `test.csv` under `data/visa/manifests/splits/` carry recorded
  SHA-256 identities (`TRAIN_SPLIT_SHA256`, `VALIDATION_SPLIT_SHA256`,
  `TEST_SPLIT_SHA256`), each re-verified by C-4 (train) and C-5 (validation + test)
  before use. The untouched, frozen test partition required by C-2 §2.1 therefore exists
  and is verifiable.
- **The governed model artifacts exist and are recorded.** C-4 completed and recorded the
  deterministic PaDiM baseline fit — the μ (`statistics/mu_by_class.npy`) and Σ⁻¹
  (`covariance/covariance_inverse_by_class.npy`) artifacts for all 12 VisA classes, with
  recorded artifact hashes, replay verification, and the governing metadata set. The
  baseline carries a recorded `deterministic_seed` and a single fixed feature-index
  subsample `[0, 2, 5, 6, 7, 9, 12, 13]`.
- **The governed inference outputs exist and are recorded.** C-5 completed governed
  inference over the validation (2164) and test (4328) splits — 6492 governed
  `InspectionPrediction` records and per-input anomaly maps — with recorded artifact
  hashes, replay verification, and the governing inference metadata set. Evaluation
  therefore reads preserved canonical evidence (anomaly maps, raw measures, predicted
  localizations) and never images, provider internals, or model objects, exactly as C-2
  §2.2 requires.
- **The evaluation contract surface is already fixed and isolated.** Evaluation consumes
  only governed `InspectionPrediction` records and governed anomaly maps behind the
  existing prediction boundary (`src/inspection/domain.py`). It must not alter the
  contract, must not alter `InspectionEngine.transform_prediction`, and must not wire
  evaluation into the canonical Inspection flow.
- **The inference-vs-evaluation separation is already explicit.** C-5 recorded that the
  `predicted_judgement` field on every prediction is a contract artifact
  (`contract_required_defect_for_raw_localization_no_threshold_v1`), not a classification.
  Evaluation must derive its own thresholded operating points from the raw anomaly
  measures and the recorded labels, and must not retroactively read the inference-layer
  judgement field as a classification (see §6 and the C-5 completion checkpoint O-1).

**Single-seed scientific boundary (must be disclosed).** C-2 §2.5 and Evaluation Strategy
§7 require "repeated seeded runs over a fixed seed set" with per-class variance and
intervals for every official metric, because PaDiM's only stochastic element is the seeded
feature-dimension subsample. C-4, however, fit the baseline on a **single** recorded seed
(`deterministic_seed: 271828`) and C-5 inference consumed that single baseline. Because
this authorization **forbids refitting and re-inference**, the C-6 sprint can evaluate
**only the one available seed**; it cannot, on its own, produce the multi-seed variance
and intervals that C-2 §2.5 names as mandatory for a fully evidenced baseline. The C-6
sprint is therefore authorized to execute the protocol's deterministic-replay,
per-class-metric, operating-point, and failure-analysis obligations on the single
goverened seed, and **must** record the single-seed limitation explicitly in its evidence
and in any claim it makes. Multi-seed variance remains a deferred scientific obligation
that requires a separate, later authorization (one that permits re-fitting over a
pre-registered seed set). No bounded detection or localization claim may present itself as
more precise than this single-seed evidence allows.

Readiness is **for evaluation of the existing governed baseline only**. Multi-seed
variance, calibration, ONNX export, any new model, and any product or cross-domain claim
each remain behind their own separate authorization gates.

---

## 2. Authorized Scope

If and when the evaluation sprint is authorized by a bounded implementation prompt, it may
do **only** the following:

- load the **governed VisA acquisition** (verifying the archive SHA-256, files manifest
  SHA-256, per-file hashes, split hashes, and provenance before use, failing closed on
  any mismatch), reading **only** the immutable splits the C-2 protocol fixes;
- load the **frozen split manifests** (`train.csv`, `validation.csv`, `test.csv`) and
  verify each split's SHA-256 against its recorded governed identity before use;
- load the **governed PaDiM inference outputs** — the C-5 anomaly maps
  (`anomaly_maps/{validation,test}_anomaly_maps.npy`), the C-5 prediction records
  (`predictions/{validation,test}_predictions.jsonl`), and the C-5 inference metadata —
  verifying each against the C-5 `artifact_hashes.json` before use, failing closed on any
  mismatch;
- consume the **governed `InspectionPrediction` records** as the only prediction surface,
  reading `predicted_raw_anomaly_measure`, the recorded predicted localization, and the
  governed `model_metadata`, never the inference-side `predicted_judgement` field as a
  classification (see §6);
- execute the **frozen C-2 Evaluation Protocol** exactly as fixed:
  - per-class, one-class, evaluated class-by-class over all 12 VisA classes (never pooled
    for a headline);
  - on the **untouched, frozen test partition** for headline evidence;
  - **Image AUROC** as the primary official metric (threshold-free detection separation);
  - **Pixel AUROC** and **AUPRO** as the bounded secondary official localization metrics
    (Pixel AUROC reported **with** AUPRO and the background-dominance caveat);
  - **Precision, Recall, F1** at a single validation-derived operating point, reported as
    **diagnostic only** (both error kinds exposed separately, never netted, F1 never
    maximized on test, never an official score);
- derive a single **validation-derived operating point** by a **pre-registered rule fixed
  before the test partition is touched** (e.g. the validation point that balances the two
  error kinds), recorded as a provisional diagnostic artifact, then applied **unchanged**
  to test;
- perform **failure analysis** exactly as C-2 §2.6 fixes it — false negatives (per class),
  false positives (per class), per-class breakdown across all 12 classes, localization
  failures interpreted against pixel ground truth only where ground truth supports it,
  near-operating-point boundary behavior framed strictly as raw-measure behavior, and
  proxy-domain limitation disclosure (VisA is a governed proxy; no cross-domain
  generalization claimed);
- perform **deterministic replay of the evaluation** — re-running the metric, operating
  point, and failure-analysis computation over the same governed inputs reproduces
  identical figures and identical confusion counts;
- generate **governed evaluation evidence**.

Nothing beyond this list is authorized. In particular: **no refitting, no re-inference, no
multi-seed runs, no calibration, no benchmark, no ONNX export, no product claim, no
architecture change.**

The runtime seams must be respected. The sprint may **read** `InspectionPrediction`
records and anomaly maps under the existing contract; it must not alter the contract, must
not alter `InspectionEngine.transform_prediction`, must not alter
`InspectionInferenceProvider`, and must not wire evaluation into `InspectionEngine.inspect()`
or into the canonical Inspection → Trust → Review → Evidence → Evaluation flow.

---

## 3. Forbidden Scope

The evaluation sprint **must not**, under any circumstances, perform or produce:

- retraining or PaDiM fitting (the C-4 baseline is frozen and read-only);
- preprocessing changes (the preprocessing contract
  `kalibra-padim-rgb64-bilinear-float64-patch8-v1` is fixed by C-4 and must be reused
  unchanged);
- feature extraction changes (the deterministic feature path and the selected feature
  indices `[0, 2, 5, 6, 7, 9, 12, 13]` are fixed by C-4);
- inference changes (the C-5 anomaly maps, raw measures, and predicted localizations are
  frozen governed inputs; evaluation must not re-run or alter inference);
- multi-seed evaluation runs (the available baseline is single-seed; multi-seed variance
  requires a separate refit authorization — see §1 and §6);
- provider changes (`InspectionInferenceProvider` protocol and seam unchanged);
- output mapping changes (the governed anomaly-map → raw-measure / localization reduction
  fixed by C-5 is consumed unchanged);
- Trust changes (no calibrated confidence, no abstention, no drift, no presenting the raw
  measure as confidence or probability);
- Review changes;
- Evidence Engine changes;
- Evaluation Engine architecture changes (the sprint executes the protocol; it must not
  introduce a new contract, seam, or domain responsibility);
- calibration;
- ONNX export;
- benchmark generation, leaderboard scores, ranking, state-of-the-art, or comparison
  claims (including against published VisA numbers);
- product claims, product-readiness claims, accuracy-for-users, robustness, SaaS,
  deployment, cloud, or commercialization claims;
- cross-domain or generalization claims from the VisA proxy;
- scientific claims beyond the bounded, single-seed claims of §6;
- any architecture change — no new contract, no new seam, no new domain responsibility,
  no rewiring of the canonical flow.

Any of these would exceed the evaluation boundary and requires its own separate
authorization gate.

---

## 4. Required Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
data/visa/derived/padim/
  evaluation/                 # governed evaluation outputs (this sprint's surface)
    metrics/                  # per-class official + diagnostic metric reports
    per_class/                # per-class metric and confusion summaries
    failure_analysis/         # false-negative / false-positive / localization-failure records
    operating_point/          # validation-derived operating point + applied-on-test record
    replay/                   # governed evaluation replay record
    metadata/                 # governed evaluation metadata
    artifact_hashes.json      # hashes of every governed evaluation artifact
docs/evidence/                # committed governed evaluation evidence report
```

Required artifacts (defined here; **not created by this checkpoint**):

- **evaluation metadata** — the consumed governed dataset identity, the consumed frozen
  split identity (train/validation/test hashes), the consumed C-4 model artifact identity
  (μ / Σ⁻¹ hashes, feature indices, layer, backbone, preprocessing contract, dtype, single
  recorded seed), the consumed C-5 inference identity (anomaly-map and prediction-record
  hashes, aggregation and localization identifiers), and the evaluation configuration
  (metric definitions, operating-point rule, failure-analysis categories, replay
  definition, single-seed limitation);
- **metric reports** — Image AUROC (primary), Pixel AUROC and AUPRO (secondary,
  reported together), per class, with the per-class sample sizes and the
  background-dominance caveat on Pixel AUROC;
- **per-class reports** — every metric and diagnostic count for each of the 12 VisA
  classes; no pooled headline;
- **confusion summaries** — true-positive, false-positive, true-negative, false-negative
  counts at the validation-derived operating point, per class, both error kinds exposed
  separately and never netted;
- **failure-analysis records** — false negatives (per class), false positives (per class),
  localization failures (where pixel ground truth supports them), near-operating-point
  boundary behavior, and proxy-domain limitation disclosure, all preserved as inspectable
  governed records;
- **operating-point records** — the pre-registered validation-derived rule, the derived
  operating point, and its unchanged application to test, marked as a provisional
  diagnostic artifact (not a calibrated or product threshold);
- **replay records** — confirming that re-running the metric, operating-point, and
  failure-analysis computation over the same governed inputs reproduced identical figures
  and confusion counts, with per-artifact hash agreement;
- **artifact hashes** — `evaluation/artifact_hashes.json` covering every governed
  evaluation artifact, so an observer can verify integrity without re-running.

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `evaluation/metrics/`, `evaluation/per_class/`, `evaluation/failure_analysis/`, `evaluation/operating_point/` per-input records | **Untracked / gitignored** if large or numerous; **committed if lightweight and reviewable** |
| `evaluation/metadata/` + `replay/` + `artifact_hashes.json` | **Committed if lightweight** — reviewable governance record; large binaries stay local |
| `docs/evidence/` evaluation evidence report | **Committed** — evidence of clean, reproducible, governed evaluation |

The metric, per-class, and failure-analysis records are regenerable from the governed
acquisition, the frozen split manifests, the governed C-4 artifacts, and the governed C-5
inference outputs; large derivatives remain local. The evaluation metadata, replay record,
artifact hashes, and the evidence report are the committed, reviewable proof of governed,
reproducible evaluation. Any `.gitignore` update is authorized **only if required** to
prevent accidental commit of large evaluation derivatives (e.g. extending the existing
`data/visa/derived/padim/` ignore family with a minimal `evaluation/` rule), scoped
strictly to that purpose.

---

## 5. Validation Requirements

The evaluation sprint must validate, and its evidence report must demonstrate, that:

- **frozen split integrity** — `train.csv`, `validation.csv`, and `test.csv` SHA-256
  identities match their recorded governed values before any metric is computed;
- **governed dataset only** — the archive, files manifest, split hashes, and provenance
  were verified before use; no mirror, no ungoverned data, no leak between partitions
  (defective images and pixel masks never entered train);
- **governed inference outputs only** — the C-5 anomaly maps and prediction records were
  hash-verified against the C-5 `artifact_hashes.json` before use; no re-inference, no
  substitution, no ingestion of images or model objects by the evaluation domain;
- **deterministic replay** — re-running the evaluation over the same governed inputs
  reproduces identical outputs;
- **reproducible metrics** — Image AUROC, Pixel AUROC, and AUPRO regenerate bit-for-bit
  (or to recorded tolerance) across the replay;
- **reproducible operating point** — the validation-derived operating point and its
  unchanged application to test regenerate identically across the replay;
- **reproducible failure analysis** — false-negative, false-positive, and localization
  failure counts regenerate identically across the replay, per class;
- **both error kinds reported separately** — false negatives and false positives are never
  netted, per class and in total;
- **per-class reporting** — every official and diagnostic figure is reported for each of
  the 12 VisA classes; no pooled headline stands alone;
- **single-seed limitation stated** — the evidence record states that the evaluated
  baseline is single-seed, that multi-seed variance is not available under this sprint,
  and that any claim is bounded accordingly;
- **no downstream architecture modifications** — `InspectionEngine.transform_prediction`,
  the `InspectionInferenceProvider` protocol, `InspectionPrediction`, Trust, Review,
  Evidence Engine, integration, and prototype UI are unchanged; evaluation is not wired
  into `inspect()` or the canonical flow;
- **no calibration, no ONNX export, no benchmark, no product claim, no refitting, no
  re-inference** was performed.

---

## 6. Scientific Claim Policy

This section fixes what becomes permitted **only after successful execution** of the C-6
sprint on governed VisA evidence, and what remains forbidden regardless of outcome.

### 6.1 Allowed (only after successful execution, and bounded by the single-seed limitation)

Each of the following is permitted **only** with reproducible evidence on the frozen VisA
test partition, both error kinds reported separately, per-class results reported,
single-seed limitation disclosed, failures reported separately, and proxy-domain
limitations stated:

- **bounded Image AUROC claim** — on the governed VisA proxy dataset, on the untouched
  frozen per-class test partition, the governed PaDiM baseline's raw anomaly measure
  separates sound from defective images, quantified by image-level AUROC per class,
  reproducible by an untrusting observer. Scope: governed proxy, per-class, this dataset
  version, single seed.
- **bounded Pixel AUROC claim** — reported **with** the background-dominance caveat.
- **bounded AUPRO claim** — the governed PaDiM baseline's anomaly map provides bounded
  per-region localization signal on VisA pixel masks, reported with VisA's incomplete
  upstream annotation-process documentation disclosed.
- **bounded localization claim** — permitted **only if** the AUPRO and Pixel AUROC
  evidence supports it; withdrawn where localization evidence is weak or absent.
- **reproducibility claim** — the accepted figures are regenerable from the pinned
  governed inputs, the frozen split manifests, the C-4 model artifacts, the C-5 inference
  outputs, and the recorded evaluation configuration by an untrusting observer.

Every such claim is **softened or withdrawn** where evidence is weak, flat, or absent
(scientific conservatism), and every such claim is **bounded by the single-seed
limitation**: it must not be presented as a multi-seed variance-characterized result, and
multi-seed intervals must not be implied.

The inference-layer `predicted_judgement` field on the C-5 records is a contract artifact
(`contract_required_defect_for_raw_localization_no_threshold_v1`), **not** a
classification. Evaluation must derive its own thresholded operating points from the raw
anomaly measures and the recorded labels; the bounded claims above rest on the
evaluation-derived operating point, never on the inference-layer judgement field.

### 6.2 Still forbidden (regardless of evaluation outcome)

- **production readiness** or any product / product-readiness claim;
- **generalized industrial performance** or any domain-of-record / real-world
  production-defect-detection claim (VisA is a governed proxy);
- **calibrated confidence** or any presentation of the raw anomaly measure (or the
  `[0,100]` band it may be rescaled into) as a probability, confidence, or trust
  statement;
- **cross-domain generalization** from the VisA proxy;
- **benchmark leadership**, ranking, leaderboard, state-of-the-art, or comparison claims
  (including against published VisA numbers — they inform expectations, not claims);
- **uncertainty-quality, abstention, review-routing, or drift** claims (no Trust, Review,
  or drift evidence basis in this baseline);
- **multi-seed variance or confidence-interval claims** that the single-seed baseline
  cannot support (multi-seed characterization remains a separate, later authorization);
- **SaaS, deployment, cloud, or commercialization** statements;
- any claim not traceable to reproducible evidence under this policy.

Any claim not explicitly allowed by §6.1 is, by default, **not made**.

---

## 7. Readiness Decision

```text
READY — the repository is ready for a bounded C-6 Scientific Evaluation
implementation prompt.

- Authorized scope: governed VisA acquisition loading + frozen split manifest loading +
  governed C-5 inference-output loading + governed InspectionPrediction consumption +
  execution of the frozen C-2 Evaluation Protocol (Image AUROC, Pixel AUROC, AUPRO;
  Precision, Recall, F1 diagnostic-only) + validation-derived operating point +
  failure analysis + deterministic replay of evaluation + governed evaluation evidence
  only.
- Forbidden scope: all refitting / re-inference / multi-seed runs / preprocessing,
  feature-extraction, inference, provider, output-mapping, Trust, Review, Evidence, and
  Evaluation-architecture changes, calibration, ONNX export, benchmark generation, and
  all product, cross-domain, calibrated-confidence, and benchmark-leadership claims.
- Required outputs, commit policy, validation requirements, and scientific claim policy
  are defined.
- Single-seed scientific boundary disclosed: multi-seed variance is deferred to a
  separate later authorization.
- Nothing evaluated, scored, fitted, exported, or claimed by this checkpoint.
  No normative document modified.
```

---

## 8. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no evaluation** (no Image AUROC, Pixel AUROC, AUPRO, Precision, Recall, or F1
  computed on any partition);
- **no threshold or operating point derived**;
- **no failure analysis** performed;
- **no refitting, no re-inference, no calibration, no ONNX export**;
- **no scientific or product claim**;
- **no downstream code modified** (provider protocol, `transform_prediction`,
  `InspectionPrediction`, Trust, Review, Evidence Engine, Evaluation Engine architecture,
  integration, prototype UI all unchanged);
- **no documentation modified** (no ADR, Dataset Strategy, Evaluation Strategy, or
  Implementation Authorization change);
- **authorization planning only**.

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document. Kalibra does **not** yet perform real defect detection, and this
checkpoint does not change that. It authorizes a bounded evaluation of one governed
baseline; it does not assert that the baseline is good.

---

## 9. Next Natural Step

```text
Generate the bounded implementation prompt for C-6 — Scientific Evaluation.
```

No governing document is updated in this task. The persisted authorization checkpoint
must be reviewed before the implementation prompt is generated.
