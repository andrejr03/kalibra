# Kalibra C-2 Evaluation Protocol Fixation Checkpoint v1.0

**Status:** Recorded — scientific evaluation-protocol decision checkpoint (no sprint authorized)
**Date:** 2026-07-05
**Repository baseline HEAD:** `ad3a8ae docs: select visa as governed proxy dataset`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **first scientific evaluation protocol** for Kalibra's
first ML baseline. It is a scientific protocol-definition checkpoint only. It
authorizes no sprint, implements no code, and modifies no ML runtime, provider,
dataset, evaluation, or authorization logic.

It does **not** modify the Evaluation Strategy, the Dataset Strategy, or the Dataset
Selection ADR. It specializes the approved Evaluation Strategy (its §5 metric policy,
§6 statistical obligations, §9 failure analysis, and §11 claim policy) to the concrete
pairing of **VisA (governed proxy dataset)** and **PaDiM (first model family)**,
without revising any governing document.

It records **what the first evaluation protocol is** — not how it will be implemented,
and not that it has been run. No evaluation is performed, no metric is computed, and no
scientific, benchmark, calibrated-confidence, or product claim is produced by this
checkpoint.

This checkpoint is equivalent in standing to the Architecture & Capability Checkpoint,
the ML Capability Engineering Strategy Checkpoint, the Scientific Model Family Selection
Checkpoint, and the C-1 Dataset Selection Closure Checkpoint. Like them, it must be
persisted before any implementation or normative change.

Throughout, **must**, **must not**, **owns**, and **does not own** carry the binding
sense established across the ML Phase 2 documents
([`AGENTS.md`](../../AGENTS.md),
[`docs/KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`](../KALIBRA_EVALUATION_METHODOLOGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)).

---

## 1. Repository Baseline

The C-2 protocol is fixed against the following completed repository state. None of it
is re-opened here.

- **Engineering infrastructure complete through Sprint 1H.** The runtime executes
  `Image → Deterministic preprocessing → Tensor → Placeholder ONNX model → Governed
  output mapping → InspectionPrediction`, with deterministic replay (content and
  configuration hashing), the `InspectionInferenceProvider` seam, the
  `InspectionPrediction` boundary, and `InspectionEngine.transform_prediction(...)`
  ownership all in place.
- **VisA selected.** `SELECTED — VisA` is recorded in the Dataset Selection ADR as the
  **governed proxy dataset** and current **governance anchor** for the first Kalibra ML
  baseline. VisA is not the final production domain and not the domain of record.
- **PaDiM selected.** PaDiM is the first model family — closed-form, deterministic
  (only a seeded feature-subsample), cleanest governed ONNX export, dense anomaly map
  supplying both the scalar raw measure and model-derived localization.
- **PatchCore reserved.** PatchCore is the planned second-generation model, to be
  adopted only after the real map → prediction pipeline and an evaluation baseline are
  proven.
- **C-1 completed.** C-1 Dataset Selection Closure is complete; MPDD remains the domain
  anchor and is retained for future domain-specific evolution.

The semantic output contract is a **single scalar raw-anomaly measure in [0,100]**,
thresholded into `ok` / `defect`. The map-statistic → [0,100] rescaling is arbitrary
until an evaluation fixes a real operating point; the raw measure **must not** be
presented as calibrated confidence (a Trust-domain concern).

---

## 2. Evaluation Protocol Definition

This protocol is a bounded specialization of the approved Evaluation Strategy for
VisA + PaDiM. It creates no metric, procedure, or claim not justified by that pairing.

### 2.1 Dataset partition policy

VisA is a one-class anomaly-detection dataset (train on sound only; test on sound +
defective, with image-level and pixel-level labels). PaDiM fits one model per class.
The protocol therefore fixes a **per-class, one-class partition, evaluated
class-by-class over all 12 VisA classes** (never pooled across classes).

Three partitions, frozen before any fitting:

- **Frozen train** — **normal (sound) images only.** No defective image, no pixel mask,
  and no test image may ever enter train. This is the only data PaDiM sees while fitting
  the per-patch Gaussians (μ and Σ⁻¹).
- **Frozen validation** — a small held-out slice containing **both** normal and
  defective images, carved from the non-test pool. Used **only** for operating-point
  derivation (§2.4) and conditioning/regularization checks. Never used to fit the
  Gaussians; never overlapping test.
- **Frozen test** — **untouched, frozen, mixed** (normal + defective) with pixel ground
  truth. Consumed exactly once per recorded evaluation. No tuning, no metric-driven
  reselection, no peeking.

**Immutable split manifests and reproducibility rules — what must remain immutable:**

- The exact image membership of each partition, per class, pinned in an **immutable
  split manifest** with **per-file sha256 hashes**.
- The governed VisA acquisition: pinned archive, local sha256 integrity manifest,
  provenance manifest, and attribution record (the governed-acquisition obligations of
  the Dataset Selection ADR §9).
- The VisA split convention adopted (the published one-class split), recorded verbatim
  so an untrusting observer regenerates identical partitions.
- **Immutability is enforced by hash.** If any manifest hash changes, the result is a
  **new** evaluation, not a re-run of the old one. A result that cannot be regenerated
  from these frozen records is not evidence.

Rationale: leak-free frozen splits are a Dataset Strategy requirement; fixing partition
membership before fitting is what keeps the eventual test result honest.

### 2.2 Evaluation inputs (governed input tuple)

The evaluation is a pure function of the following pinned inputs and **nothing else**.
The Evaluation domain reads only preserved canonical evidence — never images, provider
internals, or the model object.

1. **Governed dataset** — VisA at a pinned acquisition + local integrity manifest.
2. **Frozen split manifest** — per-class train/validation/test membership with per-file
   hashes (§2.1).
3. **Governed model artifact** — the exported PaDiM `.onnx` (backbone + precomputed μ,
   Σ⁻¹ Mahalanobis scorer) with its metadata/hash; PaDiM fitted offline on the **train**
   partition only, with a **pinned feature-subsample seed**.
4. **Preprocessing contract** — the real image → normalized CHW float tensor contract,
   referenced by its contract id (deterministic).
5. **Output-mapping contract** — the governed anomaly-map → (scalar raw measure in
   [0,100], localization box) reduction, referenced by contract id.
6. **Evaluation configuration** — the seed set (§2.5), opset/provider pinning, the
   deterministic regularization ε (Σ + εI), and the metric and operating-point
   definitions of §2.3–§2.4.

Every produced figure must be traceable back to this exact input tuple.

### 2.3 Metric selection

Metrics are split into **official (threshold-free, headline)** and **diagnostic
(operating-point-dependent, descriptive only)**, because the governance forbids
threshold tuning before evidence and forbids presenting a raw measure as confidence.

**Official metrics (become the first official baseline):**

- **Image-level AUROC** — *Detection (primary).* Threshold-free, robust to VisA's
  sound/defect imbalance, the canonical one-class AD detection metric. Directly measures
  separation of the raw anomaly measure — the primary scientific property — and requires
  no operating point, so it cannot be shaped by threshold tuning.
- **AUPRO** (per-region overlap) — *Localization (bounded secondary).* The standard
  localization metric for VisA-style pixel masks; normalizes over connected defect
  regions so a few large defects do not dominate and tiny defects are not drowned out.
  Preferred over pixel AUROC alone because pixel AUROC is inflated by the vast
  normal-background majority.
- **Pixel-level AUROC** — *Localization (bounded secondary), reported alongside AUPRO.*
  Threshold-free localization measure VisA supports via pixel masks; reported **with**
  AUPRO and with the honest caveat that background dominance inflates it. PaDiM's dense
  distance map makes it natively available.

**Diagnostic metrics only (reported for failure analysis — NOT headline, NOT targets):**

- **Precision, Recall, F1** at a single **validation-derived** operating point (§2.4).
  Reported strictly to expose **both error kinds separately** (false negatives and false
  positives, never netted), not as a performance claim. F1 is a diagnostic summary,
  never an official score, and is never maximized on test.

**Explicitly excluded from the first official set:**

- **Calibration metrics** — excluded. Confidence is a Trust-domain concern; no
  calibrated confidence exists yet (Evaluation Strategy §7). Not justified by PaDiM's
  raw measure.
- **Uncertainty-quality, drift, review-routing metrics** — excluded. No Trust, Review,
  or drift machinery is in scope for this baseline; these would have no evidentiary
  basis.
- Any **single cross-class aggregate presented as a benchmark** — excluded as a
  headline; per-class results are primary, with a mean reported only alongside per-class
  spread.

### 2.4 Operating point

**Decision: validation-derived operating point, reported as descriptive only — not a
fixed threshold, not a learned/test-tuned threshold, not calibrated confidence.**

- The headline evidence is **threshold-free** (image AUROC, AUPRO, pixel AUROC).
  Detection separation is claimed on threshold-free metrics so no operating point can
  flatter it.
- Where a concrete decision point is needed to produce the precision/recall/F1
  diagnostics and the confusion counts for failure analysis, it is **derived on the
  validation partition** by a **pre-registered rule fixed before test is touched**
  (e.g. the validation point that balances the two error kinds), then applied
  **unchanged** to test.
- A **fixed threshold** is rejected: the map-statistic → [0,100] rescaling is arbitrary
  until evidence exists, so any hardcoded number would be meaningless.
- A **test-tuned / learned threshold** is forbidden: it would violate "no threshold
  tuning before evidence" and leak the test set.
- The operating point is recorded as a **provisional diagnostic artifact**, explicitly
  **not** a calibrated or product operating point, and **no raw measure is presented as
  confidence**.

### 2.5 Statistical protocol

PaDiM's only stochastic element is the seeded feature-dimension subsample; everything
else is closed-form and deterministic. The protocol characterizes that variability
rather than hiding it.

- **Deterministic replay (mandatory).** Every figure regenerable from the pinned input
  tuple (§2.2) by an untrusting observer. Pinned opset, disabled nondeterministic
  optimizations, and fixed-output proof per target device. A figure that cannot be
  regenerated is not evidence.
- **Repeated seeded runs.** Each per-class evaluation is repeated over a **pre-registered
  set of N feature-subsample seeds** (N fixed in the evaluation configuration before
  execution). A single run may not stand as the result.
- **Variance reporting (mandatory).** Report per-class **mean and spread (std /
  min–max)** across seeds for every official metric. A point estimate is never shown
  without its spread.
- **Confidence intervals.** Report an honest interval for each official metric across
  the seed repetitions, so no figure is presented as more precise than the evidence
  allows.
- **Sample-size reporting.** Where a class's defect count (or defect sub-type) is too
  small to support a stable figure, the figure is **narrowed or withheld**, and the
  small-sample limitation is stated. VisA's per-class defect counts are modest; this
  must be surfaced.
- **Aggregation rules.** The cross-class mean is reported **only** beside the full
  per-class table and its spread — never as a standalone benchmark headline.
- **Reporting requirements.** Each recorded result carries: dataset version + split
  manifest hash, model artifact hash, preprocessing + output-mapping contract ids, the
  seed set, per-class metrics with spread and intervals, the failure-analysis package
  (§2.6), and stated limitations. Claim and justification travel together.

### 2.6 Failure-analysis protocol (minimum, mandatory)

An aggregate figure can conceal every way PaDiM fails. Failure analysis is required,
reported separately and never collapsed into one rate:

- **False negatives (missed defects)** — defective images scored sound at the diagnostic
  operating point. Surfaced **explicitly, per class**, as the most consequential
  failure; **never netted** against false positives.
- **False positives (false alarms)** — sound images flagged defective, reported in their
  own right, per class.
- **Per-class analysis** — every category above reported for each of the 12 VisA classes;
  a strong class may not mask a weak one.
- **Localization failures (where localization is in scope)** — defect images correctly
  detected but with the anomaly map / box pointing to the wrong region, interpreted
  honestly against pixel ground truth and only where ground truth supports it.
  Qualitative worst-case overlays are preserved as inspectable evidence linked to the
  exact input.
- **Boundary cases** — the near-operating-point band examined, framed strictly as
  raw-measure behavior, **not** as uncertainty quality (no Trust claim).
- **Proxy-domain limitations** — VisA is a governed **proxy**; PaDiM
  alignment-sensitivity and the proxy-domain gap to cast-aluminium / machined parts are
  recorded as active risks. **No cross-domain generalization is claimed.**
- **Explicitly out of scope for this baseline** (no evidence basis; reported only as
  *not evaluated*): abstention quality, review-routing correctness, drift responsiveness,
  and calibrated-confidence error.

### 2.7 Allowed scientific claims

Permitted **only** with reproducible evidence on the frozen VisA test partition, both
error kinds reported, variance and intervals stated, failures reported separately, and
limitations disclosed:

- **Engineering claim** — the PaDiM provider runs behind the seam, returns only
  `InspectionPrediction`, replays deterministically, and changes nothing downstream.
  (Establishes containment only — nothing about inspection quality.)
- **Bounded detection claim** — *"On the governed VisA proxy dataset, on an untouched
  frozen per-class test partition, PaDiM produces a raw anomaly measure that measurably
  separates sound from defective images, quantified by image-level AUROC with reported
  per-class variance, reproducible by an untrusting observer."* Scope: governed proxy,
  per-class, this dataset version only.
- **Bounded localization claim (conditional)** — permitted **only if** AUPRO / pixel
  AUROC evidence supports it, and **must** disclose VisA's incomplete upstream
  annotation-process documentation. Absent supporting evidence, no localization claim is
  made.
- **Reproducibility claim** — the above are regenerable from the pinned inputs.

Every such claim is **softened or withdrawn** where evidence is weak, flat, or absent
(scientific conservatism).

### 2.8 Remaining prohibited claims

Regardless of evaluation outcome:

- **No benchmark / ranking / comparison claim** — no leaderboard number, no
  "state-of-the-art," no comparison against published VisA numbers (they inform
  expectations, not claims).
- **No domain-of-record / real-world production defect-detection claim** — VisA is a
  proxy, not cast aluminium / CNC / gearbox-housing parts.
- **No cross-domain or generalization claim** from a single proxy dataset.
- **No calibrated-confidence claim**, and **no presenting the raw [0,100] measure as
  confidence** (Trust-domain, ungated here).
- **No uncertainty-quality, abstention, review-routing, or drift claim** — no evidence
  basis in this baseline.
- **No product / product-readiness / accuracy / robustness claim**, and no product
  surface implying any of the above.
- **No claim that acquisition, training, or evaluation has occurred.**
- **No SaaS, deployment, cloud, or commercialization statement.**

Any claim not traceable to reproducible evidence under this protocol is, by default,
**not made**.

---

## 3. Readiness Decision

```text
C-2 Evaluation Protocol defined.
Ready for repository-owner approval.
```

Recorded explicitly:

- **Protocol defined.** The first evaluation protocol is fully specified above.
- **Protocol not executed.** The protocol has not been run.
- **No evaluation performed.** No metric has been computed on any partition.
- **No claims produced.** No scientific, benchmark, calibrated-confidence, or product
  claim exists.
- **Governed acquisition still required.** Execution requires governed VisA acquisition
  with local integrity, provenance, attribution, and frozen split records.
- **Implementation authorization still required.** No code may begin before the
  Implementation Authorization gate.

---

## 4. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no code**
- **no implementation**
- **no training**
- **no evaluation execution**
- **no benchmark**
- **no scientific result**
- **no product claim**

It changes no governed logic, no runtime, no provider, no dataset, no evaluation
harness, and no authorization document. It does not present the placeholder model's
behavior as a scientific result, and Kalibra does not yet perform real defect detection.

---

## 5. Next Natural Step

```text
Review this checkpoint.

After approval:

1. Update the Evaluation Strategy if required.

2. Only then begin governed VisA acquisition.

3. Afterwards execute C-2.
```

No governing document is updated in this task. The persisted checkpoint must be
reviewed before any governing document is modified.
