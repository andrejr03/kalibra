# Kalibra ML Phase 2 — Evaluation Strategy v1.0

## About This Document

This document is the **authoritative evaluation strategy** for the second
machine-learning phase of Kalibra. It fixes how Kalibra will evaluate a future
ML system scientifically, before any framework-backed implementation begins.

It is **not** an implementation plan, and it is **not** an evaluation report. It
writes no code, performs no evaluation, authorizes no training or execution, names
no benchmark dataset, and sets no performance target. It defines the **standard of
proof** any ML Phase 2 evaluation must meet — what must be shown, to what standard,
and in what order the decision is taken. It now also records the first official
evaluation protocol fixed by the
[`C-2 Evaluation Protocol Fixation Checkpoint`](checkpoints/KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md)
for the governed VisA proxy dataset and PaDiM first model family.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`](KALIBRA_EVALUATION_METHODOLOGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md`](KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md`](KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md),
and
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md).

This document continues the ML Phase 2 planning sequence. It follows the Scientific
Architecture Plan (scientific direction), the Framework ADR (runtime-evaluation
process, selection deferred), the Dataset Strategy (dataset evidence requirements),
the Dataset Selection ADR (`SELECTED — VisA`), the Scientific Model Family Selection
Checkpoint (PaDiM first; PatchCore reserved), and the C-2 Evaluation Protocol
Fixation Checkpoint (first protocol fixed), and it precedes any execution of that
protocol (§15).

**Binding gate.** No ML Phase 2 evaluation result may be accepted, and no
framework-backed implementation may begin, until the evaluation standard in this
document is approved by the repository owner. The first baseline metrics and protocol
are now fixed for VisA + PaDiM by C-2, but no dataset acquisition, training,
evaluation execution, benchmark, calibrated-confidence claim, product claim, or
implementation is authorized by this document.

---

## 1. Purpose

Evaluation strategy must be approved before implementation because, under Kalibra's
discipline, **evidence precedes assertion**. The evaluation defines what would count
as proof of a scientific property; if it is fixed after a model exists, it can be
shaped — consciously or not — to flatter what was built. Deciding the standard of
proof first is what keeps the eventual evidence honest. It is the same reason the
Dataset Strategy came before data acquisition: the rules that judge a result are
fixed before the result exists.

Evaluation in Kalibra governs **scientific evidence, not model optimization**. Its
purpose is to establish what an untrusting observer may conclude, not to make a
model score higher. Optimization chooses among candidate methods during development;
evaluation decides whether a fixed method has earned a claim. This document concerns
only the second. A metric used to tune a model is not, by that use, evidence for a
claim; evidence is produced under the frozen, reproducible conditions this strategy
fixes.

Accordingly, this document defines **how a future ML system will be evaluated** and
records the first approved protocol specialization for VisA + PaDiM. It does **not**
choose benchmark datasets, set performance targets, authorize a fixed production
threshold, or grant authority to begin implementation, acquisition, training, or
evaluation execution. Those remain gated by the approval criteria in §13, governed
VisA acquisition, and the implementation-authorization decision in §15.

The existing
[`KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`](KALIBRA_EVALUATION_METHODOLOGY_v1.0.md)
remains Kalibra's standing evaluation methodology. This document does not replace it;
it specializes it for ML Phase 2 and inherits every obligation it states.

---

## 2. Current Baseline

ML Phase 2 evaluation work begins from the following completed repository state. Each
item is already present and validated; none is re-opened here.

- **Deterministic runtime.** A complete
  Inspection → Trust Qualification → Human Review → Evidence → Evaluation chain in
  which each domain owns one responsibility and consumes only the canonical output
  of the domain before it.
- **Provider abstraction.** `InspectionInferenceProvider` is the single boundary
  object behind the Inspection Engine's examination seam where inference
  implementations may be referenced.
- **`InspectionPrediction` boundary.** The abstract, non-canonical, untrusted
  prediction contract produced by Machine Learning and consumed only by the
  Inspection Engine.
- **`transform_prediction` ownership.** `InspectionEngine.transform_prediction(...)`
  owns validation of every prediction and its deterministic conversion into the
  canonical `RawInspectionResult`.
- **`LocalArtifactInferenceProvider`.** The first real local provider, reading
  deterministic PGM P2 fixture content with the Python standard library and deriving
  an `InspectionPrediction` from real bytes. It returns only `InspectionPrediction`
  and remains unwired from `InspectionEngine.inspect()`.
- **Prototype integration.** A prototype adapter that projects the real
  local-provider result into inspection-only prototype data, explicitly withholding
  calibrated confidence, trust, routing, drift, and evaluation claims.
- **Evidence-chain integration.** An opt-in path that runs the real local-provider
  result through the canonical downstream chain, with downstream domains consuming
  only canonical records — never provider objects, predictions, pixels, or
  screenshots.
- **ML Phase 1 closure.** The ML Phase 1 local-provider path checkpoint is formally
  closed, with an explicit list of what remains unclaimed.
- **Scientific Architecture Plan.** The ML Phase 2 scientific baseline, fixing the
  scientific objectives, the anomaly-detection-first problem scope, and the
  evaluation obligations at direction level.
- **Framework ADR.** The proposed runtime-evaluation decision process, which selects
  no framework and defers implementation.
- **Dataset Strategy.** The dataset evidence requirements — provenance, licensing,
  ownership, traceability, reproducibility, versioning, integrity verification,
  long-term availability, honest content and ground truth, leak-free frozen splits,
  bounded synthetic-data policy, governance, and scientific-risk reasoning.
- **Dataset Selection ADR.** The repository now records `SELECTED — VisA`: VisA is
  the governed proxy dataset and governance anchor for the first Kalibra ML baseline;
  MPDD remains the domain anchor for future domain-specific evolution. VisA is not
  the final production domain and not the domain of record.
- **Scientific Model Family Selection Checkpoint.** PaDiM is selected as the first
  model family. PatchCore is reserved as the planned second-generation model, to be
  considered only after the real map → prediction pipeline and the first evaluation
  baseline are proven.
- **C-2 Evaluation Protocol Fixation Checkpoint.** The first evaluation protocol is
  fixed for VisA + PaDiM. It defines the first official metric set, operating-point
  policy, statistical protocol, failure-analysis minimums, and claim boundaries. It
  has not been executed and produces no scientific result.

**Why the first baseline protocol is now defined.** The Evaluation Strategy remains
dataset-independent in principle: any future dataset must still satisfy the same
evidence, claim, statistical, and failure-analysis obligations. The first baseline
protocol is now defined because the repository has selected VisA as the governed
proxy dataset, selected PaDiM as the first model family, and recorded the C-2
protocol checkpoint. Execution remains dependent on governed VisA acquisition and the
appropriate downstream gates.

---

## 3. Evaluation Philosophy

Kalibra's evaluation rests on the following principles, inherited from the standing
methodology and specialized here for ML Phase 2.

- **Evidence precedes assertion.** A property is described as true only once a
  reproducible artifact supports it. No metric, however favorable, is a claim until
  it is evidenced under frozen, reproducible conditions.
- **Reproducibility.** Every result must be regenerable from a fixed starting
  point — fixed dataset version, fixed split, fixed configuration — by an observer
  who does not trust Kalibra. A result that cannot be regenerated is not evidence.
- **Scientific conservatism.** Where evidence is weak, flat, or absent, the claim is
  softened or withdrawn rather than stated. Partial evidence yields a partial,
  honestly stated claim, never a full one. Absence of evidence is reported as
  absence.
- **Engineering versus science.** An engineering success (the method runs correctly
  behind the seam) is not a scientific result (the method exhibits a real property on
  honest data). The two are proven separately and never substituted for one another.
- **Uncertainty.** Accuracy is necessary but not sufficient. Kalibra's central thesis
  is that it knows when not to trust itself; evaluation must show that the cases the
  method is unsure about are the cases it is more often wrong about, not merely that
  it is right on average.
- **Honest reporting.** Honesty outranks presentation. Distinct dimensions and
  distinct failure kinds are reported separately so strength in one cannot mask
  weakness in another, both error kinds are reported and never netted, and no result
  is presented more favorably than the evidence allows.

These principles are binding on every layer, metric category, and claim in this
document.

---

## 4. Evaluation Layers

ML Phase 2 evaluation is separated into three layers, kept distinct so that success
at one is never mistaken for success at another. Each layer has a different question,
a different standard, and a different owner.

- **Engineering validation.** Asks whether the system is correctly contained and
  reproducible: a framework-backed provider runs behind `InspectionInferenceProvider`
  and returns only `InspectionPrediction`; `InspectionEngine.transform_prediction`
  still owns validation and transformation into `RawInspectionResult`; downstream
  domains, the integration layer, and the CLI are unchanged; inference is
  deterministic and replayable. These are true or false by construction and testing.
  Engineering validation establishes correct containment and **nothing** about
  inspection quality. It is bounded by the provider seam and the compatibility rules
  of the Framework ADR.
- **Scientific validation.** Asks whether the method exhibits a real property on
  honest data: detection separation, usable signal in the raw anomaly measure,
  informative uncertainty, and meaningful localization where in scope. It is measured
  only on a qualifying dataset (Dataset Strategy §3–§9) and only on an untouched,
  frozen test partition, reading preserved evidence. Scientific validation is owned
  by the **Evaluation domain**, which owns evidence-backed evaluation reports and
  reads only preserved evidence — never images, provider internals, or model objects.
- **Product validation.** Asks whether a user or stakeholder can rely on what a
  surface presents. It is downstream of, and gated by, scientific validation. A
  product surface **must not** imply detection quality, calibrated confidence,
  accuracy, or robustness beyond what the scientific evidence supports, and **must
  not** present a raw anomaly measure as confidence.

Ownership across layers is preserved and never blurred by evaluation: the Inspection
Engine **owns** validation and transformation; Trust Qualification **owns**
calibrated confidence, uncertainty characterization, and drift caution; Human Review
**owns** review-case preparation and reviewer decision recording; Evidence **owns**
preservation, lineage, absence markers, and read-only views; Evaluation **owns**
evidence-backed reports. Evaluation reasons about outputs; it does not assume any
other domain's responsibility.

---

## 5. Dataset Partition Policy

The first baseline protocol uses VisA as a one-class anomaly-detection dataset:
normal images form the fitting population, and mixed normal/defective images form
the evaluation population. PaDiM is fitted per class, so the first baseline is
partitioned and evaluated **per class** across the 12 VisA classes; a cross-class
mean may be reported only beside the per-class table and spread, never as a
standalone benchmark headline.

Three partitions are mandatory and frozen before fitting:

- **Frozen train.** Normal images only. No defective image, pixel mask, validation
  image, or test image may enter train. This is the only partition used for PaDiM
  fitting.
- **Frozen validation.** A held-out mixed partition containing normal and defective
  images. It may be used only for operating-point derivation and conditioning or
  regularization checks. It must not be used to fit PaDiM and must not overlap test.
- **Frozen test.** An untouched, mixed partition containing normal and defective
  images with pixel ground truth. It is reserved for final evidence. No tuning,
  metric-driven reselection, or peeking is permitted.

The partition record must be reproducible by an untrusting observer. At minimum, it
must include:

- immutable split manifests for train, validation, and test;
- per-file SHA-256 hashes for every image and label artifact used by the protocol;
- the governed VisA acquisition record, local integrity manifest, provenance
  manifest, and attribution record;
- the adopted VisA split convention, recorded sufficiently for identical
  regeneration;
- proof that no image, derived duplicate, label, or mask leaks across partitions.

If any dataset, label, or split manifest hash changes, the result is a **new**
evaluation, not a rerun of the old one. A result that cannot be regenerated from the
frozen dataset, split, model, configuration, and procedure records is not evidence.

---

## 6. Metrics Policy

This section fixes the **policy** for metrics by naming the categories any ML Phase 2
evaluation must reason about and records the first official metric set fixed by the
C-2 Evaluation Protocol Fixation Checkpoint for VisA + PaDiM. The official set is
threshold-free where it supports scientific claims; operating-point-dependent metrics
are diagnostic only.

Categories to be reasoned about:

- **Anomaly detection metrics.** Measures of how well the method separates defective
  from sound inputs, appropriate to imbalanced defect data. Both error kinds must be
  expressible; no single average may stand in for the whole picture.
- **Localization metrics.** Where defect localization is in scope as the bounded
  secondary objective and ground truth supports it, measures of whether a localized
  region agrees with the ground-truth location. Where such ground truth does not
  exist, no localization metric is reported and no localization claim is made.
- **Calibration metrics.** Measures of whether stated confidence matches observed
  correctness. Because confidence is a Trust concern (§8), these apply to the
  *calibrated* output, not to the raw anomaly measure.
- **Uncertainty metrics.** Measures of whether expressed doubt tracks actual error —
  whether uncertain cases are more error-prone — and whether abstention concentrates
  the hard and ambiguous cases rather than discarding decisions at random.
- **Robustness metrics.** Measures of how results hold under controlled, graded
  variation of conditions, informing the drift and domain-shift reasoning of §10.

### 6.1 First Official Metric Set

The first official VisA + PaDiM metric set is:

- **Primary official metric:** Image AUROC. This is the headline detection metric
  because it is threshold-free and measures separation of the raw anomaly measure
  without allowing threshold tuning to shape the result.
- **Secondary official metrics:** AUPRO and Pixel AUROC. These are bounded
  localization metrics supported by VisA pixel masks and PaDiM dense anomaly maps.
  AUPRO is reported as the stronger localization signal because it reasons over
  defect regions; Pixel AUROC is reported alongside it with the caveat that normal
  background dominance can inflate it.
- **Diagnostic-only metrics:** Precision, Recall, and F1 at the validation-derived
  operating point (§6.2). These metrics exist to expose false positives, false
  negatives, and failure-analysis counts. They are **not** headline metrics, not
  targets, and not benchmark scores. F1 is descriptive only and must never be
  maximized on test.

Calibration metrics, uncertainty-quality metrics, review-routing metrics, and drift
metrics are excluded from the first official set because no calibrated confidence,
Trust evaluation, Review evaluation, or drift evidence exists for this baseline.

### 6.2 Operating Point

The first protocol uses a **validation-derived operating point** for diagnostic
counts only.

- No fixed threshold is authorized. The raw anomaly measure is rescaled into the
  existing `[0,100]` band, but that scale is not calibrated and must not be treated
  as a probability or confidence.
- No test tuning is permitted. The operating-point rule is fixed before the test
  partition is touched, derived on validation, and then applied unchanged to test.
- The operating point is descriptive only. It may support Precision, Recall, F1, and
  confusion-count diagnostics, but it is not a calibrated confidence threshold, not a
  product threshold, and not an authorization to make a product decision.
- Threshold-free metrics remain primary. Image AUROC, AUPRO, and Pixel AUROC carry
  the first official baseline evidence; diagnostic metrics cannot replace them.

**Why metric selection depends on the dataset and inspection problem.** A metric is
only meaningful with respect to what the data can support and what question is being
asked. The C-2 checkpoint fixes the first official set for VisA + PaDiM because that
pairing provides image-level labels, pixel-level labels, and a dense PaDiM anomaly
map. Future datasets or model families must still justify their metric set against
their own evidence shape and may not inherit metrics uncritically.

---

## 7. Statistical Validation

Any ML Phase 2 result must account for sampling and variability. This section fixes
the **obligations** for every evaluation and records the first C-2 statistical
protocol for VisA + PaDiM. It prescribes no performance target.

- **Deterministic replay.** Every figure must be regenerable from the pinned dataset,
  split, model artifact, contracts, seed set, procedure, and configuration by an
  untrusting observer. A figure that cannot be replayed is not evidence.
- **Repeated seeded runs.** Where the method or evaluation has any source of
  variability, results must rest on repeated pre-registered seeded runs. For the
  first PaDiM baseline, the seeded feature-dimension subsample is repeated over a
  fixed seed set recorded before execution; a single favorable run may not stand as
  the result.
- **Statistical significance.** A difference is reported as a result only when the
  evidence supports it, not on the strength of a single favorable comparison.
- **Confidence intervals.** Reported figures must be accompanied by an honest
  expression of their uncertainty, so a point estimate is never presented as more
  precise than the evidence allows. The first protocol reports intervals across the
  repeated seed runs for each official metric.
- **Sample size.** Claims must account for how much data underlies them, especially
  for rare defects and for the trust dimensions, where small samples can mislead.
  Where a sample is too small to support a claim, the claim is narrowed or withheld.
  Per-class sample sizes must be reported for the first VisA baseline.
- **Variance.** The spread of results across repetitions must be reported, not hidden
  behind a single average, so an observer can judge stability as well as central
  tendency. The first protocol reports per-class mean and spread for every official
  metric.
- **Aggregation rules.** Per-class results are primary. Any cross-class mean must be
  reported only alongside the full per-class table, spread, intervals, and sample
  sizes; it must not be used as a standalone benchmark headline.
- **Reporting requirements.** Each recorded result must carry the dataset version and
  split manifest hash, governed model artifact hash, preprocessing and output-mapping
  contract identifiers, seed set, per-class official metrics with spread and
  intervals, diagnostic counts, failure-analysis package, and stated limitations.
- **Reproducibility.** Every statistical result must be regenerable from the recorded
  dataset version, split, procedure, and configuration by an untrusting observer.

Concrete interval methods and seed counts are fixed in the evaluation configuration
before execution. They must be recorded before the test partition is touched and may
not be changed in response to test results.

---

## 8. Calibration Strategy

This section fixes the position on calibration for ML Phase 2 by keeping three levels
strictly separate, consistent with the Scientific Architecture Plan.

- **Raw anomaly measure.** The inference method's uncalibrated deviation score. It is
  raw substrate produced inside `InspectionPrediction`, and it is **not** a
  probability or confidence. ML Phase 2 is responsible for producing an honest raw
  measure and evidencing that it carries usable signal.
- **Calibrated confidence.** A statement of the real chance of being correct, produced
  by the **Trust Qualification Engine** from the raw measure, and only once
  reproducible calibration evidence exists that stated confidence matches observed
  correctness on a fixed dataset.
- **Trust qualification.** The qualified outcome — including abstention and
  deferral — the Trust domain owns, built on calibrated confidence and
  drift-awareness.

**Why calibration remains a Trust concern.** Under the fixed architecture, confidence
is **owned by the Trust Qualification Engine, not by the inference method**.
Calibration and drift are exactly the claims Kalibra most risks overstating;
implementing them before detection signal is evidenced would produce confidence
figures with no basis. Calibration is therefore evaluated on the calibrated output,
gated by its own evidence, and stays outside ML Phase 2 implementation until (a)
detection signal is evidenced and (b) a dataset with sufficient ground truth exists
to demonstrate calibration honestly. Evaluation **must not** present a raw measure as
confidence, nor a confidence figure as a trust decision.

---

## 9. Explainability Strategy

Explainability in Kalibra is the ability to honestly account for a result, and it is
**broader than a saliency map**. A visual highlight is at most one optional
component; it is neither necessary nor sufficient, and it can itself mislead. The
evaluation therefore treats explainability as a property of the whole evidence path.

- **Traceability.** A result must be traceable to the input, preprocessing, model
  version, and inference method that produced it, so an observer can follow it back to
  its origin.
- **Reproducibility.** The explanation must rest on evidence that can be regenerated
  from a fixed starting point, so it is a standing record rather than a momentary
  rationalization.
- **Evidence linkage.** Each result must link to the preserved evidence records the
  Evidence domain owns, tying it to the exact dataset version, split, and
  configuration behind it. This linkage is recorded through Evidence, which owns
  preservation and lineage; explainability consumes that linkage and does not assume
  Evidence's ownership.
- **Localization interpretation.** Where localization is in scope, a localized region
  is interpreted honestly against ground truth (Dataset Strategy §5) and only where
  ground truth supports it; a highlight is never presented as an explanation it has
  not earned.
- **Model transparency.** The account of a result must be appropriate to the chosen
  approach, so the degree of transparency a method actually offers is stated rather
  than overstated.

**Why explainability is broader than saliency maps.** A saliency map shows where a
method attended, not whether the result is right, reproducible, or traceable — and a
convincing highlight can lend false credibility to a wrong or spurious decision
(Dataset Strategy §9, hidden correlations). Kalibra's standard is that a result can
be **honestly accounted for and independently verified**, which depends on
traceability, reproducibility, and evidence linkage far more than on any single
visualization.

---

## 10. Failure Analysis

Failure analysis is **mandatory**: an aggregate figure can conceal every way a
method fails, and Kalibra's thesis is precisely about failure — knowing when not to
trust itself. The following must be reported separately, never collapsed into a
single rate.

- **False positives.** Sound inputs flagged as defective, with their cost to trust
  and throughput, reported in their own right and per class for the first VisA
  baseline.
- **False negatives.** Defective inputs accepted as sound — the most consequential
  failure — surfaced explicitly, per class for the first VisA baseline, and never
  netted against false positives.
- **Per-class reporting.** Each failure category that applies to the first baseline
  must be reported for each VisA class. A strong class must not mask a weak one.
- **Localization failures.** Where localization is in scope, defect images that are
  correctly detected but localized to the wrong region must be reported against
  pixel ground truth. Worst-case qualitative overlays may be preserved as evidence
  only when linked to the exact input, model, split, and result record.
- **Boundary cases.** Cases near the validation-derived operating point must be
  inspected as raw-measure boundary behavior. They must not be described as
  uncertainty quality, because no Trust-domain uncertainty evidence exists for the
  first baseline.
- **Abstentions, uncertainty, and review routing.** These remain mandatory categories
  when their domains produce evidence. For the first VisA + PaDiM baseline they are
  explicitly **not evaluated**: no abstention quality, uncertainty-quality,
  review-routing correctness, or drift claim has an evidence basis yet.
- **Domain shift.** Systematic differences between the evaluation setting and any
  other deployment setting, acknowledged as a real risk; no cross-domain
  generalization is claimed from a single-domain dataset.
- **Proxy-domain limitations.** VisA is a governed proxy dataset, not Kalibra's
  domain of record. Failure analysis must state the proxy-domain gap to
  cast-aluminium, CNC-machining, gearbox-housing, or similar metal-part inspection
  settings, and must record PaDiM's alignment sensitivity as an active risk.

**Why failure analysis is mandatory.** The operational asymmetry between a missed
defect and a false alarm, the risk of confident errors, and the honesty of
abstention and routing are all invisible in an average. Naming and reporting the
failure categories separately is itself an evaluative act — it is how the specific
ways the method can fail are made accountable, and how a claim is prevented from
resting on a favorable aggregate.

---

## 11. Benchmark Policy

This section fixes what may stand as a benchmark. Its default is restraint.

- **Benchmark requirements.** No benchmark or performance number may be stated without
  a reproducible artifact, a named dataset version, and a documented procedure. A
  number without regenerable evidence is not a benchmark.
- **Comparison policy.** Any comparison — between methods, configurations, or against
  an external reference — must be made on the same fixed dataset version and split,
  under the same procedure, with both error kinds and variability reported. A
  comparison drawn across differing data or procedures is not evidence and **must
  not** be presented as one.
- **Reproducibility.** Every benchmark must be regenerable from a fixed starting point
  by an observer who does not trust Kalibra, using the recorded dataset version,
  split, configuration, and procedure.
- **Publication requirements.** Any benchmark communicated beyond the repository must
  carry its dataset version, procedure, both error kinds, variability, and stated
  limitations, so the claim and its justification are never separated. Favorable-only
  reporting is prohibited.

**Unsupported benchmark claims are forbidden.** No benchmark, comparison, ranking, or
performance figure may be presented — in code, documents, the product surface, or any
external communication — unless it meets every requirement above. A benchmark that
cannot be reproduced is, by default, **not made**.

---

## 12. Claim Policy

This section separates the three kinds of claim ML Phase 2 evaluation may support and
fixes the evidence each requires. They must never be conflated.

- **Engineering claims** — that the system is correctly contained and reproducible:
  it runs behind the seam, returns only `InspectionPrediction`, replays
  deterministically, and changes nothing downstream. *Evidence required:* passing
  construction and boundary tests, deterministic replay, and unchanged-downstream
  tests. Establishes correct containment only; establishes **nothing** about
  inspection quality.
- **Scientific claims** — that the method exhibits a real property: detection
  separation, usable raw-measure signal, informative uncertainty, meaningful
  localization. *Evidence required:* a reproducible artifact on a qualifying dataset
  (Dataset Strategy §3–§9), computed on an untouched, frozen test partition, with
  both error kinds reported, statistical variability accounted for (§7), failure
  categories reported separately (§10), and dataset risks disclosed. Weak, flat, or
  absent evidence narrows or withdraws the claim.
- **Product claims** — that a user can rely on what a surface presents. *Evidence
  required:* an established scientific claim beneath it. A product surface **must
  not** imply detection quality, calibrated confidence, accuracy, or robustness
  beyond the scientific evidence, and **must not** present a raw measure as
  confidence.

Binding across all three: **reproducible evidence precedes any scientific claim**;
calibration and drift claims stay with the Trust domain and are gated by their own
evidence; and evaluation preserves every domain's ownership (§4). Any claim that
cannot be traced to reproducible evidence under this policy is, by default, **not
made**.

For the first VisA + PaDiM protocol fixed by C-2, the following scientific claims are
allowed **only after successful execution** on governed VisA evidence:

- **Bounded detection claim.** PaDiM's raw anomaly measure measurably separates sound
  from defective images on the governed VisA proxy dataset, quantified primarily by
  Image AUROC, with per-class results, variance, intervals, both error kinds, and
  limitations reported.
- **Bounded localization claim.** Conditional on supporting AUPRO and Pixel AUROC
  evidence, PaDiM's anomaly map provides bounded localization signal on VisA pixel
  masks. This claim must disclose VisA's incomplete upstream annotation-process
  documentation and is withdrawn where localization evidence is weak or absent.
- **Reproducibility claim.** The accepted figures and claim record are regenerable
  from the pinned dataset, split, model, seed, configuration, and procedure records by
  an untrusting observer.

The following remain prohibited regardless of first-baseline outcome:

- benchmark, ranking, leaderboard, state-of-the-art, or comparison claims;
- domain-of-record, real-world production defect-detection, or final production-domain
  claims;
- calibrated-confidence claims or any presentation of the raw `[0,100]` measure as
  confidence;
- product, product-readiness, accuracy-for-users, robustness, SaaS, deployment, cloud,
  or commercialization claims;
- cross-domain or generalization claims from the VisA proxy dataset;
- uncertainty-quality, abstention, review-routing, or drift claims for the first
  baseline;
- any claim that acquisition, training, or evaluation has already occurred.

---

## 13. Evaluation Approval Criteria

An ML Phase 2 evaluation may be accepted **only** when all of the following objective
conditions are met and recorded. Each is verifiable; none is a matter of preference.

- **Standard approved.** This evaluation strategy is approved by the repository owner
  as the standard of proof.
- **Layers respected.** Engineering, scientific, and product validation (§4) are kept
  separate, with ownership preserved and no layer substituted for another.
- **Dataset qualified.** The evaluation is computed on a dataset that satisfies the
  Dataset Strategy approval criteria, on immutable train/validation/test partitions
  that satisfy §5.
- **Metrics justified.** The metric categories of §6 are addressed with specific
  metrics justified against the approved dataset and inspection problem, both error
  kinds expressible. The first VisA + PaDiM baseline uses the C-2 official metric set.
- **Statistics accounted for.** Significance, intervals, sample size, repeated
  seeded evaluation, variance, aggregation, and reporting requirements (§7) are
  addressed, with results regenerable.
- **Calibration boundary kept.** Raw measure, calibrated confidence, and trust
  qualification (§8) are kept distinct, and no raw measure is presented as confidence.
- **Explainability shown.** Traceability, reproducibility, and evidence linkage (§9)
  are demonstrated at a level appropriate to the chosen approach.
- **Failures reported.** The failure categories of §10 are reported separately, not
  hidden in an aggregate.
- **Benchmarks supported.** Any benchmark meets every requirement of §11; no
  unsupported benchmark is present.
- **Claims traced.** Every claim conforms to §12, with reproducible evidence beneath
  it or the claim withdrawn.
- **Owner approval.** The repository owner explicitly approves the evaluation and its
  recorded limitations in the project record.

An evaluation that fails any criterion is not accepted, and the failing criterion is
recorded as the reason. Meeting these criteria authorizes an evaluation as the
standard of proof; it does not by itself authorize implementation, which remains a
separate gate (see §15).

---

## 14. Open Decisions

The following decisions remain intentionally deferred. The first VisA + PaDiM metric
set and protocol are fixed by C-2; the items below are outside that first protocol or
belong to later execution records.

- **Benchmark datasets or comparisons.** Any dataset used as a benchmark or comparison
  reference, and the terms under which comparison is drawn. No benchmark or comparison
  claim is authorized for the first baseline.
- **Calibration methods.** The concrete calibration approach and its evaluation, which
  remain Trust-domain concerns gated by their own evidence (§8).
- **Execution-time statistical parameters.** The concrete interval method, seed count,
  and any pre-registered significance procedure for a specific execution record (§7).
- **Publication policy.** How, and to whom, benchmarks and results may be communicated
  beyond the repository, within the requirements of §11.
- **Robustness protocol.** The concrete graded-variation protocol used to evaluate
  robustness and inform drift and domain-shift reasoning (§10).
- **Future metric sets.** Metric sets for future datasets, future model families, or
  future project phases. They must be justified against their own evidence shape and
  may not be inferred from the first VisA + PaDiM protocol.

Deferred decisions remain deferred unless the repository owner authorizes them
through an approved downstream document.

---

## 15. Next Dependency

Recommended next dependency:

```text
Governed VisA Acquisition
```

The C-2 Evaluation Protocol Fixation Checkpoint has fixed the first protocol, and
this strategy now incorporates it. The next dependency is governed VisA acquisition:
the pinned archive, local SHA-256 integrity manifest, provenance manifest,
attribution record, and immutable split manifests required before any execution can
produce evidence.

The current decision order is therefore:

```text
Scientific Architecture   (approved)
        |
        v
Framework ADR             (proposed; selection deferred)
        |
        v
Dataset Strategy          (dataset evidence requirements fixed)
        |
        v
Dataset Selection ADR     (SELECTED — VisA)
        |
        v
Scientific Model Family   (PaDiM first; PatchCore reserved)
        |
        v
C-2 Evaluation Protocol   (fixed for VisA + PaDiM)
        |
        v
Evaluation Strategy       (this document — C-2 incorporated)
        |
        v
Governed VisA Acquisition (required before execution)
        |
        v
Implementation Authorization / execution gates
        |
        v
ML Phase 2 Implementation (framework-backed provider behind the existing seam)
        |
        v
Scientific Validation     (evidence produced on untouched test data)
        |
        v
ML Phase 2 Closure        (all exit criteria met; checkpoint recorded)
```

Implementation, training, and evaluation execution **must not** begin from this
strategy alone. They remain gated by governed VisA acquisition, the Framework ADR
selection, the Implementation Authorization conditions, and the execution records
required by C-2.

---

## Closing Statement

This document fixes how Kalibra will evaluate a future ML system scientifically,
before any framework-backed implementation begins. It now records the first official
VisA + PaDiM protocol: frozen partitions, Image AUROC as primary metric, AUPRO and
Pixel AUROC as secondary metrics, Precision/Recall/F1 as diagnostic-only metrics, a
validation-derived descriptive operating point, deterministic replay, repeated seeded
runs, variance and interval reporting, and mandatory failure analysis. It names no
benchmark dataset, fixes no performance target, authorizes no execution, and makes no
scientific, benchmark, calibrated-confidence, or product claim.

Above all it preserves Kalibra's discipline: the provider abstraction is untouched,
Inspection, Trust, Review, Evidence, and Evaluation each keep their ownership, and
**no scientific claim is made without reproducible evidence on qualifying data**. It
exists so that whenever Kalibra eventually claims a property of its ML system, that
claim rests on evidence an observer who does not trust Kalibra can regenerate and
verify — and so that implementation begins only after the standard by which it will
be judged is fixed.
