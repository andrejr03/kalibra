# Kalibra ML Phase 2 — Evaluation Strategy v1.0

## About This Document

This document is the **authoritative evaluation strategy** for the second
machine-learning phase of Kalibra. It fixes how Kalibra will evaluate a future
ML system scientifically, before any framework-backed implementation begins.

It is **not** an implementation plan, and it is **not** an evaluation report. It
writes no code, selects no metric, fixes no threshold, names no benchmark dataset,
and sets no performance target. It defines the **standard of proof** any ML Phase 2
evaluation must meet — what must be shown, to what standard, and in what order the
decision is taken — not how any measurement is computed.

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
process, selection deferred), and the Dataset Strategy (dataset evidence
requirements), and it precedes an implementation-authorization decision (§14).

**Binding gate.** No ML Phase 2 evaluation result may be accepted, and no
framework-backed implementation may begin, until the evaluation standard in this
document is approved by the repository owner. Until then, the concrete metrics,
procedures, and benchmarks remain unselected by design.

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

Accordingly, this document defines **how a future ML system will be evaluated**. It
does **not** choose metrics, thresholds, benchmark datasets, or performance targets,
and it grants no authority to begin implementation. Those remain deferred (§13) and
gated by the approval criteria in §12 and the implementation-authorization decision
in §14.

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

**Why evaluation now becomes the next dependency.** The planning sequence orders
decisions by dependency. The Dataset Strategy fixed what data must provide; an
evaluation is meaningful only with respect to the data it is computed on, so it
could not be fixed earlier without binding it to assumptions the data may not
satisfy. With the dataset requirements settled, the standard of proof is the next
thing that must be fixed — and it must be fixed **before** implementation, so the
eventual evidence is judged against a standard chosen independently of the model.
Evaluation is therefore the last decision document before an implementation is
authorized.

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

## 5. Metrics Policy

This section fixes the **policy** for metrics by naming the categories any ML Phase 2
evaluation must reason about. It **selects no specific metric** and fixes no
threshold. Metrics are chosen later, against the approved dataset and inspection
problem, and recorded in the evaluation that produces evidence.

Categories to be reasoned about:

- **Anomaly detection metrics.** Measures of how well the method separates defective
  from sound inputs, appropriate to imbalanced defect data. Both error kinds must be
  expressible; no single average may stand in for the whole picture.
- **Localization metrics.** Where defect localization is in scope as the bounded
  secondary objective and ground truth supports it, measures of whether a localized
  region agrees with the ground-truth location. Where such ground truth does not
  exist, no localization metric is reported and no localization claim is made.
- **Calibration metrics.** Measures of whether stated confidence matches observed
  correctness. Because confidence is a Trust concern (§7), these apply to the
  *calibrated* output, not to the raw anomaly measure.
- **Uncertainty metrics.** Measures of whether expressed doubt tracks actual error —
  whether uncertain cases are more error-prone — and whether abstention concentrates
  the hard and ambiguous cases rather than discarding decisions at random.
- **Robustness metrics.** Measures of how results hold under controlled, graded
  variation of conditions, informing the drift and domain-shift reasoning of §9.

**Why metric selection depends on the dataset and inspection problem.** A metric is
only meaningful with respect to what the data can support and what question is being
asked. The right detection metric depends on class balance and defect diversity; any
localization metric depends on the existence and granularity of localization ground
truth; calibration and uncertainty metrics depend on sufficient labeled outcomes;
robustness metrics depend on the graded variation the dataset actually contains.
Fixing metrics before the dataset is approved would either bind evaluation to
assumptions the data may not satisfy or invite metrics chosen to flatter a
not-yet-chosen dataset — both forbidden by the claim policy (§11). Metric selection
is therefore deferred (§13).

---

## 6. Statistical Validation

Any ML Phase 2 result must account for sampling and variability. This section fixes
the **obligations**; it prescribes **no numerical threshold**.

- **Statistical significance.** A difference is reported as a result only when the
  evidence supports it, not on the strength of a single favorable comparison. What
  counts as sufficient support is fixed with the approved dataset and metrics, not
  here.
- **Confidence intervals.** Reported figures must be accompanied by an honest
  expression of their uncertainty, so a point estimate is never presented as more
  precise than the evidence allows.
- **Sample size.** Claims must account for how much data underlies them, especially
  for rare defects and for the trust dimensions, where small samples can mislead.
  Where a sample is too small to support a claim, the claim is narrowed or withheld.
- **Repeated evaluation.** Where a method or its evaluation has any source of
  variability, results must rest on repeated evaluation rather than a single run, so
  a favorable outcome cannot be selected after the fact.
- **Variance.** The spread of results across repetitions must be reported, not hidden
  behind a single average, so an observer can judge stability as well as central
  tendency.
- **Reproducibility.** Every statistical result must be regenerable from the recorded
  dataset version, split, procedure, and configuration by an untrusting observer.

Concrete significance levels, interval widths, sample sizes, and repetition counts
are deferred decisions (§13) belonging to the evaluation of the approved dataset, not
to this document.

---

## 7. Calibration Strategy

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

## 8. Explainability Strategy

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
  is interpreted honestly against ground truth (§5) and only where ground truth
  supports it; a highlight is never presented as an explanation it has not earned.
- **Model transparency.** The account of a result must be appropriate to the chosen
  approach, so the degree of transparency a method actually offers is stated rather
  than overstated.

**Why explainability is broader than saliency maps.** A saliency map shows where a
method attended, not whether the result is right, reproducible, or traceable — and a
convincing highlight can lend false credibility to a wrong or spurious decision (§9,
hidden correlations). Kalibra's standard is that a result can be **honestly
accounted for and independently verified**, which depends on traceability,
reproducibility, and evidence linkage far more than on any single visualization.

---

## 9. Failure Analysis

Failure analysis is **mandatory**: an aggregate figure can conceal every way a
method fails, and Kalibra's thesis is precisely about failure — knowing when not to
trust itself. The following must be reported separately, never collapsed into a
single rate.

- **False positives.** Sound inputs flagged as defective, with their cost to trust
  and throughput, reported in their own right.
- **False negatives.** Defective inputs accepted as sound — the most consequential
  failure — surfaced explicitly and never netted against false positives.
- **Abstentions.** Declining to decide, evaluated as a deliberate outcome: abstention
  must be shown to concentrate the hard and ambiguous cases, not to discard decisions
  at random.
- **Uncertainty.** Misplaced uncertainty — confident errors and uncertain-but-correct
  cases — reported so it is visible whether expressed doubt tracks actual error.
- **Review routing.** Whether the cases routed toward human review are the ones that
  genuinely warranted deferral, evaluated as the right cases being routed rather than
  simply more or fewer. Review-case preparation and reviewer decision recording
  remain **owned** by Human Review; evaluation reasons about the outcomes it
  preserves.
- **Domain shift.** Systematic differences between the evaluation setting and any
  other deployment setting, acknowledged as a real risk; no cross-domain
  generalization is claimed from a single-domain dataset.

**Why failure analysis is mandatory.** The operational asymmetry between a missed
defect and a false alarm, the risk of confident errors, and the honesty of
abstention and routing are all invisible in an average. Naming and reporting the
failure categories separately is itself an evaluative act — it is how the specific
ways the method can fail are made accountable, and how a claim is prevented from
resting on a favorable aggregate.

---

## 10. Benchmark Policy

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

## 11. Claim Policy

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
  both error kinds reported, statistical variability accounted for (§6), failure
  categories reported separately (§9), and dataset risks disclosed. Weak, flat, or
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

---

## 12. Evaluation Approval Criteria

An ML Phase 2 evaluation may be accepted **only** when all of the following objective
conditions are met and recorded. Each is verifiable; none is a matter of preference.

- **Standard approved.** This evaluation strategy is approved by the repository owner
  as the standard of proof.
- **Layers respected.** Engineering, scientific, and product validation (§4) are kept
  separate, with ownership preserved and no layer substituted for another.
- **Dataset qualified.** The evaluation is computed on a dataset that satisfies the
  Dataset Strategy approval criteria, on an untouched, frozen test partition.
- **Metrics justified.** The metric categories of §5 are addressed with specific
  metrics justified against the approved dataset and inspection problem, both error
  kinds expressible.
- **Statistics accounted for.** Significance, intervals, sample size, repeated
  evaluation, and variance (§6) are addressed, with results regenerable.
- **Calibration boundary kept.** Raw measure, calibrated confidence, and trust
  qualification (§7) are kept distinct, and no raw measure is presented as confidence.
- **Explainability shown.** Traceability, reproducibility, and evidence linkage (§8)
  are demonstrated at a level appropriate to the chosen approach.
- **Failures reported.** The failure categories of §9 are reported separately, not
  hidden in an aggregate.
- **Benchmarks supported.** Any benchmark meets every requirement of §10; no
  unsupported benchmark is present.
- **Claims traced.** Every claim conforms to §11, with reproducible evidence beneath
  it or the claim withdrawn.
- **Owner approval.** The repository owner explicitly approves the evaluation and its
  recorded limitations in the project record.

An evaluation that fails any criterion is not accepted, and the failing criterion is
recorded as the reason. Meeting these criteria authorizes an evaluation as the
standard of proof; it does not by itself authorize implementation, which is governed
by the implementation-authorization decision (§14).

---

## 13. Open Decisions

The following decisions are intentionally deferred. None is made by this document;
each must be settled by an approved downstream decision before it can constrain an
evaluation.

- **Chosen metrics.** The specific metrics within each category of §5, chosen against
  the approved dataset and inspection problem.
- **Benchmark datasets.** Any dataset used as a benchmark or comparison reference, and
  the terms under which comparison is drawn.
- **Calibration methods.** The concrete calibration approach and its evaluation, which
  remain Trust-domain concerns gated by their own evidence (§7).
- **Statistical procedures.** The concrete significance procedure, interval method,
  sample sizes, and repetition counts (§6).
- **Publication policy.** How, and to whom, benchmarks and results may be communicated
  beyond the repository, within the requirements of §10.
- **Robustness protocol.** The concrete graded-variation protocol used to evaluate
  robustness and inform drift and domain-shift reasoning (§9).
- **Localization depth.** How far localization is evaluated as a secondary objective
  and what ground truth supports it.

Deferred decisions remain deferred unless the repository owner authorizes them
through an approved downstream document.

---

## 14. Next Planning Artifact

Recommended next planning artifact:

```text
KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md
```

The implementation-authorization document should define the **explicit conditions
under which ML Phase 2 implementation may finally begin**. It is the correct next
step because the planning sequence has now fixed every decision that must precede
code: the scientific direction, the runtime-evaluation process, the dataset evidence
requirements, and — with this document — the standard of proof. What remains is a
single, explicit gate that gathers the prerequisites into one authorization, so that
implementation begins only when all of them are demonstrably satisfied rather than by
default.

The recommended decision order is therefore:

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
Evaluation Strategy       (this document — approve before proceeding)
        |
        v
Implementation Authorization (explicit conditions for implementation to begin)
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

Implementation **must not** begin before the Framework ADR selection, the Dataset
Strategy, this Evaluation Strategy, and the implementation-authorization conditions
are approved, and before a specific dataset is shown to satisfy the dataset approval
criteria.

---

## Closing Statement

This document fixes how Kalibra will evaluate a future ML system scientifically,
before any framework-backed implementation begins. It selects no metric, sets no
threshold, names no benchmark dataset, and fixes no performance target. It fixes the
standard of proof: three separated validation layers; a metric policy stated by
category and deferred in specifics; statistical, calibration, explainability, and
failure-analysis obligations; a benchmark policy that forbids unsupported claims; a
three-tier claim policy; and objective approval criteria.

Above all it preserves Kalibra's discipline: the provider abstraction is untouched,
Inspection, Trust, Review, Evidence, and Evaluation each keep their ownership, and
**no scientific claim is made without reproducible evidence on qualifying data**. It
exists so that whenever Kalibra eventually claims a property of its ML system, that
claim rests on evidence an observer who does not trust Kalibra can regenerate and
verify — and so that implementation begins only after the standard by which it will
be judged is fixed.
