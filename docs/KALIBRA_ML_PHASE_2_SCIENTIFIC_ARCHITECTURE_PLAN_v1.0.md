# Kalibra ML Phase 2 — Scientific Architecture Plan v1.0

## About This Document

This document is the **scientific architecture baseline** for the second
machine-learning phase of Kalibra. It governs all future machine-learning work
by fixing the scientific questions, evaluation obligations, and decision order
that any ML Phase 2 implementation must respect.

It is **not** an implementation plan. It writes no code, chooses no model, selects
no framework, commits to no dataset, and fixes no metric threshold. It defines
**scientific direction**, not implementation tasks.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_1_INSPECTION_INFERENCE_BOUNDARY_v1.0.md`](KALIBRA_ML_PHASE_1_INSPECTION_INFERENCE_BOUNDARY_v1.0.md),
[`docs/KALIBRA_DATASET_STRATEGY_v1.0.md`](KALIBRA_DATASET_STRATEGY_v1.0.md), and
[`docs/KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`](KALIBRA_EVALUATION_METHODOLOGY_v1.0.md).

This document continues directly from
[`docs/KALIBRA_ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE_v1.0.md`](KALIBRA_ML_PHASE_1_LOCAL_PROVIDER_PATH_CLOSURE_v1.0.md),
which closed the ML Phase 1 local-provider path and named the next step as a
planning or decision document, not code.

**Binding gate.** ML Phase 2 implementation **must not** begin until the scientific
decisions in this document are approved by the repository owner. Until then, the
next artifacts are decision documents (§13), not code.

---

## 1. Purpose

ML Phase 1 has concluded successfully. It set out to fix the permanent
architectural seam between Machine Learning and the Inspection Engine and to prove
that seam with real local content — not to prove machine-learning quality. Against
that goal it is complete:

- the Machine Learning → Inspection seam is documented and one-directional;
- providers produce only `InspectionPrediction`;
- the Inspection Engine owns validation, transformation, and evidence emission;
- a deterministic mock provider and a real `LocalArtifactInferenceProvider` both
  exercise the seam;
- the real local provider result has been projected into the prototype and
  composed through the canonical evidence chain via an opt-in integration path;
- the architecture boundary was validated and the checkpoint was formally closed.

ML Phase 1 succeeded precisely because it made no scientific claim. It proved a
boundary, not a model. That is why ML Phase 2 **must begin with scientific
architecture rather than implementation**: the seam is ready, but the science that
would justify putting a trained model behind it is not yet decided. Writing code
first would force premature, undocumented commitments to a model family, a runtime
framework, a dataset, and a metric — exactly the commitments Kalibra's
evidence-precedes-assertion discipline forbids until they are justified.

This document therefore defines the scientific direction of ML Phase 2. It clarifies
which questions Kalibra intends to answer, how answers will be evidenced, and in
what order the decisions must be made. It **does not** define implementation tasks,
and it grants no authority to begin them.

---

## 2. Current Technical Baseline

ML Phase 2 begins from the following completed repository state. Each item is
already present and validated; none is re-opened by this document.

- **Deterministic five-domain runtime.** A complete
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
- **Deterministic mock provider.** A no-I/O provider that proves the provider seam
  without artifact reads and returns only `InspectionPrediction`.
- **`LocalArtifactInferenceProvider`.** The first real local provider, reading
  deterministic local PGM P2 fixture content with the Python standard library and
  deriving an `InspectionPrediction` from real bytes. It remains unwired from
  `InspectionEngine.inspect()`.
- **Prototype UI integration.** A prototype adapter that projects the real
  local-provider result into inspection-only prototype data, explicitly
  withholding calibrated confidence, trust, routing, drift, and evaluation claims.
- **Evidence-chain integration.** An opt-in integration path that runs the real
  local-provider result through the canonical downstream chain, with downstream
  domains consuming only canonical records — never provider objects, predictions,
  pixels, or screenshots.
- **Architecture validation.** Focused and repo-wide test runs, `compileall`, and
  `git diff --check` confirmed the boundary intact at a clean HEAD.
- **ML Phase 1 closure.** The ML Phase 1 local-provider path checkpoint is formally
  closed, with an explicit list of what remains unclaimed.

**What the baseline does not include.** It includes no trained model, no learned
weights, no external ML framework, no chosen model architecture, no benchmark
dataset beyond fixed fixtures, no calibrated confidence, and no performance claim.
The raw anomaly measure carried through the chain (e.g. `75.0` on the
`model_raw_anomaly_measure` scale) is raw substrate and is not confidence.

This baseline is a **boundary and composition proof**. ML Phase 2 builds science on
top of it without moving it.

---

## 3. Scientific Objectives

This section separates the three kinds of goal that ML Phase 2 touches. Keeping
them apart is itself an obligation: an engineering success is not a scientific
result, and neither is a product claim.

### 3.1 Engineering goals

Engineering goals concern the machinery that lets science be done reproducibly.
They are true or false by construction and testing.

- Keep the Machine Learning → Inspection seam unchanged: a Phase 2 provider still
  returns only `InspectionPrediction`.
- Make it possible to run a framework-backed provider **behind the existing seam**
  without changing any downstream domain, the integration layer, or the CLI.
- Preserve determinism of transformation and reproducibility of inference behind
  the seam.
- Keep any new dependency, artifact, or fixture bounded, offline, and versioned.

Engineering goals do **not** establish that inference is good, only that it is
correctly contained.

### 3.2 Scientific goals

Scientific goals are the questions Kalibra actually intends to answer with
evidence. They are the reason ML Phase 2 exists.

- **Does the inspection method separate defective from sound inputs** on a fixed,
  honest dataset, and how well?
- **Does the raw anomaly measure carry usable signal** that, once calibrated,
  yields confidence that means what it says?
- **Is the method's uncertainty informative** — are the cases it is unsure about
  the cases it is more often wrong about?
- **Where the method localizes a defect, is the localization meaningful** against
  ground truth?
- **Is every one of the above reproducible** from a fixed starting point by an
  observer who does not trust Kalibra?

Scientific goals are answered only with reproducible evidence, never by assertion.

### 3.3 Product goals

Product goals concern what a user or stakeholder experiences. They are downstream
of, and gated by, the scientific goals.

- Present inspection results, and eventually qualified trust, honestly in the
  prototype/product surface.
- Communicate uncertainty and deferral in a way a non-expert can act on.
- Never let a product surface imply a scientific claim that the evidence does not
  support.

Product goals **must not** be pursued ahead of the scientific goals that justify
them, and product presentation **must not** manufacture confidence the science has
not earned.

**No mixing.** A statement like "the model works" is meaningless in this document
unless it is decomposed into an engineering claim (it runs behind the seam), a
scientific claim (it separates classes on dataset X with evidence Y), and a product
claim (a user can trust its presentation). Each is proven separately.

---

## 4. Inspection Problem Definition

Kalibra's inspection problem is: **given one stabilized inspection input, decide
whether it is defective, and when it is, indicate where** — while producing a raw
anomaly measure that downstream trust qualification can calibrate. The following
sub-problems each address part of that, and this section fixes which are in scope
for ML Phase 2.

- **Anomaly detection** — deciding whether an input deviates from the sound
  distribution, without necessarily naming the defect. This is the most natural fit
  for Kalibra's raw-anomaly-measure substrate and its "knows when to doubt itself"
  thesis. **In scope** for ML Phase 2 as the primary sub-problem.
- **Defect localization** — indicating where a suspected defect lies when the
  judgement is defective. The `InspectionPrediction` contract already carries an
  optional predicted localization. **In scope**, but as a secondary objective
  subordinate to detection; localization quality is evaluated only where ground
  truth supports it.
- **Defect classification** — naming the *kind* of defect among known categories.
  This requires categorical labels the current fixtures do not carry. **Out of
  scope** for ML Phase 2; deferred (§12).
- **Segmentation** — producing a pixel- or region-level mask of the defect. This
  requires dense annotations and a heavier evaluation apparatus. **Out of scope**
  for ML Phase 2; deferred (§12).
- **Confidence estimation** — turning a raw anomaly measure into calibrated
  confidence. Under the fixed architecture, confidence is **owned by the Trust
  Qualification Engine, not by the inference method**. ML Phase 2 is responsible
  for producing an honest *raw* measure and evidencing that it carries signal; it
  is **not** responsible for calibrating it. Calibration remains a Trust concern and
  is scoped conservatively in §9.

**Scope summary.** ML Phase 2 targets **anomaly detection** as primary and
**defect localization** as a bounded secondary, both producing only
`InspectionPrediction`. Classification and segmentation are deferred. Confidence
estimation stays with Trust Qualification and is not an inference responsibility.

This scope **must not** widen without an approved update to this document.

---

## 5. Dataset Strategy

This section states the dataset obligations ML Phase 2 must satisfy. Consistent
with [`KALIBRA_DATASET_STRATEGY_v1.0.md`](KALIBRA_DATASET_STRATEGY_v1.0.md), it
**does not choose a specific dataset**; it defines what any chosen data must
provide before it may support a claim.

- **Provenance.** The origin of every input must be known and recorded. Data of
  unknown or unclear origin is declined, not used.
- **Labeling.** The data must carry enough trustworthy ground truth (sound vs
  defective at minimum, plus defect location where localization is evaluated) to
  support the scientific goals in §3.2. Absent or unreliable labels disqualify a
  claim that depends on them.
- **Annotation quality.** Labels must be produced by a documented process, with
  ambiguity and disagreement recorded rather than hidden. Annotation that conceals
  difficulty is treated as a defect in the data.
- **Synthetic vs real data.** Synthetic data may be used for controlled, graded
  variation and for reproducible fixtures, but a claim of real-world inspection
  quality **must not** rest on synthetic data alone. The proportion and role of
  synthetic data must be stated wherever it informs a claim.
- **Deterministic fixtures.** The existing fixed fixtures (e.g. the PGM P2 inputs
  under `tests/fixtures/inspection/`) remain the deterministic backbone for
  boundary and reproducibility tests. Scientific claims require more than fixtures,
  but fixtures remain the reproducibility anchor.
- **Train/validation/test separation.** Any learned method must use a documented,
  leak-free split. The test partition must be untouched during development and used
  only for final evidence. Split definitions must themselves be versioned.
- **Versioning.** Every dataset, split, and label set used for a claim must be
  fixed into a stable, identifiable version, so results can be tied to exactly the
  data that produced them.
- **Reproducibility.** Every result must be regenerable from a fixed starting point
  by an observer who does not trust Kalibra, using the recorded data version and
  procedure.
- **Evidence requirements.** A dataset is admitted as evidence only when it can
  show competent inspection, meaningful confidence signal, informative
  uncertainty, and appropriate deferral — not when it merely makes the system look
  good.

No specific dataset is selected here. Dataset selection is a deferred decision
(§12) and a dedicated downstream document (§13).

---

## 6. Candidate ML Approaches

This section surveys candidate inference approaches and the trade-offs that will
decide among them. It **selects none**. Every approach, if chosen, sits behind the
`InspectionInferenceProvider` seam and returns only `InspectionPrediction`.

Each approach is weighed on the same axes: **offline suitability** (can it run
locally, deterministically, without network or hosted services), **explainability**
(can a result be honestly explained and traced), **computational cost** (training
and inference footprint), and **fit to the anomaly-detection-first scope** of §4.

- **Classical computer vision** (thresholding, morphology, edge/blob analysis).
  *Strengths:* fully offline, cheap, deterministic, highly explainable; the current
  local provider already lives here. *Weaknesses:* brittle to real-world variation,
  limited ceiling on hard cases. *Fit:* strong reproducibility baseline; weak on
  subtle defects.
- **Feature engineering + classical ML** (hand-crafted features into a simple
  classifier/scorer). *Strengths:* offline, low cost, features are inspectable.
  *Weaknesses:* feature design is manual and dataset-specific; limited on complex
  textures. *Fit:* a transparent, low-risk step up from pure classical CV.
- **Anomaly detection methods** (one-class / distribution-based scoring of deviation
  from sound inputs). *Strengths:* aligns directly with the raw-anomaly-measure
  substrate and the "trained mostly on sound data" reality of inspection; can be
  offline. *Weaknesses:* threshold/scoring choices need honest calibration;
  localization may be indirect. *Fit:* strong fit to §4's primary scope.
- **Autoencoders / reconstruction-based** (score anomaly by reconstruction error).
  *Strengths:* learns the sound distribution, offline-capable, gives a natural raw
  measure and coarse localization via error maps. *Weaknesses:* training stability,
  sensitivity to normal-data coverage, explainability of error maps is partial.
  *Fit:* good fit to anomaly-detection-first, with heavier cost than classical.
- **CNNs (supervised).** *Strengths:* strong on learned defect patterns, mature
  tooling, offline inference feasible. *Weaknesses:* need labeled defective data,
  higher cost, explainability requires added technique. *Fit:* strong if labels
  and dataset justify it; heavier evidentiary burden.
- **Vision Transformers.** *Strengths:* high ceiling, strong on global context.
  *Weaknesses:* data-hungry, expensive, harder to run cheaply offline, weaker
  default explainability. *Fit:* likely premature for ML Phase 2's scope and data.
- **Foundation models.** *Strengths:* strong priors, few-shot potential.
  *Weaknesses:* large, often network/hosted-dependent, licensing and provenance
  complexity, explainability and reproducibility risk. *Fit:* tension with the
  offline, reproducible architecture; treated with caution.
- **Multimodal models.** *Strengths:* can combine image with text/metadata.
  *Weaknesses:* scope, cost, and provenance concerns compound; far beyond the
  single-input inspection problem of §4. *Fit:* out of scope for ML Phase 2's
  problem definition.

**No selection is made.** Approach selection is deferred (§12) and depends on the
dataset (§5), the runtime framework evaluation (§7), and the evaluation strategy
(§8). What is fixed here is only the set of axes on which the choice must be
justified.

---

## 7. Runtime Framework Evaluation

This section defines the **criteria** by which an inference runtime would be
evaluated. It **selects no framework**. Framework selection is a deferred decision
that must be recorded in a dedicated Architecture Decision Record (ADR), per §13.

Candidate runtimes to be evaluated when the decision is opened include, without
preference or ordering: **ONNX Runtime, PyTorch, TensorFlow Lite, OpenVINO, and
OpenCV DNN**. Any candidate must be judged against every criterion below.

- **Offline execution.** Must run fully locally with no network dependency at
  inference time. A runtime that requires hosted services or phone-home behavior is
  disqualified by Kalibra's offline posture.
- **Reproducibility.** Must support producing the same output for the same input
  and recorded configuration, so results can be regenerated by an untrusting
  observer.
- **Deterministic inference.** Must allow inference to be made deterministic behind
  the seam; non-determinism from a fixed input must be controllable and, if
  uncontrollable, treated as an Inspection-domain defect.
- **Deployment.** Must fit a bounded, local deployment without introducing hosted,
  streaming, or continuously operating components.
- **Portability.** Must run across the platforms Kalibra targets without binding the
  project to a single vendor or accelerator.
- **Licensing.** License terms must be known and compatible with Kalibra's use;
  unclear licensing is a reason to decline, not to proceed.
- **Hardware support.** Must run acceptably on the available hardware; any
  accelerator requirement must be optional, not load-bearing.
- **Future maintainability.** Must have a sustainable maintenance and versioning
  story, so a chosen runtime does not become an unmaintainable dependency.

A framework earns selection only when a written ADR shows it satisfies these
criteria and records the trade-offs. **No framework is selected in this document.**

---

## 8. Model Evaluation Strategy

This section defines how any ML Phase 2 method is judged. Consistent with
[`KALIBRA_EVALUATION_METHODOLOGY_v1.0.md`](KALIBRA_EVALUATION_METHODOLOGY_v1.0.md),
evidence precedes assertion, accuracy is necessary but not sufficient, and honesty
outranks presentation. Evaluation reads only preserved evidence; it does not
inspect images or provider internals.

Evaluation dimensions and obligations:

- **Metrics.** Detection is measured with metrics appropriate to imbalanced defect
  data (e.g. precision, recall, and threshold-independent separation), reported
  with the dataset version they were computed on. No single average is allowed to
  stand in for the whole picture.
- **Calibration.** Whether stated confidence corresponds to real correctness must
  be measured, not assumed. Because confidence is a Trust concern, calibration is
  evaluated on the *calibrated* output, not on the raw measure (see the distinction
  below).
- **Uncertainty.** The link between the method's expressed doubt and its actual
  errors must be shown: uncertain cases must be the cases it is more often wrong
  about.
- **Explainability.** A result must be honestly explainable and traceable to the
  input and inference method that produced it, at a level appropriate to the chosen
  approach.
- **False positives / false negatives.** Both error kinds are reported separately
  and never netted against each other; their operational asymmetry (a missed defect
  vs a false alarm) is stated, not hidden.
- **Localization quality.** Where localization is in scope (§4) and ground truth
  supports it, localization is measured against that ground truth; where it is not
  supported, no localization claim is made.
- **Statistical validation.** Claims must account for sample size and variability;
  a difference is reported as a result only when the evidence supports it, not on a
  single favorable run.

**Three levels that must never be conflated:**

- **Raw anomaly measure** — the inference method's uncalibrated deviation score. It
  is raw substrate, produced inside `InspectionPrediction`, and is **not** a
  probability or confidence.
- **Calibrated confidence** — a statement of the real chance of being correct,
  produced by the **Trust Qualification Engine** from the raw measure, and only
  once calibration evidence exists.
- **Trust qualification** — the qualified outcome (including abstention/deferral)
  the Trust domain owns, built on calibrated confidence and drift-awareness.

Evaluation **must** keep these three separate and **must not** present a raw measure
as confidence or a confidence figure as a trust decision.

---

## 9. Drift & Calibration Strategy

This section states Kalibra's position on calibration and drift for ML Phase 2. Its
central point is restraint: these are Trust-domain scientific concerns, and they
**remain outside ML Phase 2 implementation until scientifically justified**.

- **Calibration evidence.** Before any Kalibra output is described as calibrated,
  there must be reproducible evidence that stated confidence matches real
  correctness on a fixed dataset. ML Phase 2 produces an honest raw measure and
  evidences that it carries signal; it does **not** ship calibration.
- **Drift monitoring.** Detecting that inputs have moved away from familiar
  conditions is a Trust-domain capability. ML Phase 2 does not implement drift
  monitoring; it only ensures the raw substrate needed to reason about drift later
  is honestly produced and preserved.
- **Dataset shift.** Changes in the input distribution between training/reference
  data and live data must eventually be reasoned about, but doing so requires
  reference distributions and evidence that ML Phase 2 does not yet establish.
- **Domain shift.** Systematic differences between the demonstration setting and a
  new deployment setting are acknowledged as a real risk and explicitly deferred;
  no cross-domain generalization is claimed.
- **Uncertainty estimation.** Turning a raw measure into a defensible statement of
  doubt is part of the calibration science above and is gated by the same evidence
  requirement.

**Why deferred.** Calibration and drift are exactly the claims Kalibra most risks
overstating. Implementing them before the underlying detection science is evidenced
would produce confidence figures and drift signals with no basis. They therefore
stay out of ML Phase 2 implementation until (a) detection signal is evidenced and
(b) a dataset with sufficient ground truth exists to demonstrate calibration and
drift honestly. Until then they are documented direction, not implemented behavior.

---

## 10. Safety & Claim Policy

This section fixes what Kalibra **may and may not claim** during and after ML
Phase 2. It applies to code comments, documents, the prototype/product surface, and
any external communication.

- **Benchmark policy.** No benchmark or performance number may be stated without a
  reproducible artifact, a named dataset version, and a documented procedure. A
  number without regenerable evidence is not a benchmark and must not be presented
  as one.
- **Scientific evidence policy.** A property is described as true only once a
  reproducible artifact supports it. Where evidence is weak, flat, or absent, the
  claim is softened or withdrawn rather than stated. Absence of evidence is
  reported as absence, not glossed over.
- **Marketing claim policy.** No marketing or product-facing statement may imply
  detection quality, calibrated confidence, accuracy, or robustness beyond what the
  scientific evidence supports. Product presentation **must not** manufacture
  confidence the science has not earned. Raw measures are never shown as confidence.
- **Evaluation policy.** Evaluation is done on untouched test data, reports both
  error kinds, keeps evaluation dimensions separate so strength in one cannot mask
  weakness in another, and reads only preserved evidence. Favorable-only reporting
  is prohibited.

Any claim that cannot be traced to reproducible evidence under these policies is,
by default, **not made**.

---

## 11. Exit Criteria

ML Phase 2 may be considered complete **only** when all of the following objective
criteria are met. Each is verifiable; none is a matter of opinion.

- **Architectural.** A framework-backed inference provider runs behind the existing
  `InspectionInferenceProvider` seam, returns only `InspectionPrediction`, and
  changes nothing downstream: the Inspection Engine still owns transformation, and
  Trust, Review, Evidence, Evaluation, the integration layer, and the CLI are
  unchanged. The default runtime path still begins with `InspectionEngine.inspect()`.
- **Scientific.** The primary scientific goals of §3.2 (detection separation, and
  evidence that the raw measure carries usable signal) are answered with
  reproducible evidence on a fixed, honest dataset, within the anomaly-detection
  scope of §4.
- **Validation.** Detection metrics, both error kinds, and (where in scope)
  localization quality are reported on untouched test data under the evaluation
  policy of §8 and §10, with statistical variability accounted for.
- **Documentation.** The framework ADR (§13), dataset strategy document, and
  evaluation strategy document exist, are approved, and match what was actually
  built. This scientific baseline is reflected, not contradicted, by the
  implementation.
- **Reproducibility.** Every stated result is regenerable from a fixed starting
  point — fixed dataset version, fixed split, fixed configuration — by an observer
  who does not trust Kalibra.

Meeting the engineering/architectural criterion alone does **not** close ML
Phase 2. All five criteria are required.

---

## 12. Open Decisions

The following decisions are intentionally deferred. None is made by this document;
each must be settled by an approved downstream decision document before it can
constrain implementation.

- **Approach selection.** Which candidate approach (§6) is chosen for the primary
  anomaly-detection scope.
- **Framework selection.** Which runtime (§7) is chosen, recorded in a dedicated
  ADR.
- **Dataset selection.** The specific dataset, splits, labels, and provenance (§5).
- **Metric thresholds.** The concrete metrics and any decision thresholds (§8),
  which cannot be fixed before dataset and approach are known.
- **Localization depth.** How far localization is pursued as a secondary objective,
  and what ground truth supports its evaluation.
- **Calibration entry.** When, and on what evidence, calibration and drift work
  (§9) may enter implementation as a Trust-domain concern.
- **Product surface.** Whether and when the prototype moves beyond inspection-only
  demonstration toward qualified-trust presentation.
- **Deferred sub-problems.** Whether defect classification or segmentation (§4) are
  ever brought into scope, which would require new labels and a scope update.

Deferred scope remains deferred unless the repository owner updates the public
project documentation.

---

## 13. Recommended Roadmap

The recommended decision order is sequential: each step is gated by approval of the
one before it, and implementation is the second-to-last step, not the first.

```text
Scientific Architecture   (this document — approve before proceeding)
        |
        v
Framework ADR             (§7 criteria applied; one runtime selected and recorded)
        |
        v
Dataset Strategy          (§5 obligations applied; a specific dataset fixed)
        |
        v
Evaluation Strategy       (§8 metrics and procedure fixed for the chosen dataset)
        |
        v
ML Phase 2 Implementation (framework-backed provider behind the existing seam)
        |
        v
Scientific Validation     (evidence produced on untouched test data)
        |
        v
ML Phase 2 Closure        (all §11 exit criteria met; checkpoint recorded)
```

Implementation **must not** begin before the Framework ADR, Dataset Strategy, and
Evaluation Strategy are approved. Closure **must not** be declared before scientific
validation meets every exit criterion in §11.

---

## Closing Statement

ML Phase 1 proved a boundary; it did not prove a model. ML Phase 2 begins with
science, not code, because the seam is ready but the scientific decisions that
would justify a trained model behind it are not yet made. This document fixes the
scientific direction: the questions to answer, the data and evaluation obligations
to meet, the claims that may and may not be made, and the order in which decisions
must be taken.

It selects no approach, no framework, and no dataset, and it preserves the existing
provider architecture and the fixed
Inspection → Trust → Review → Evidence → Evaluation separation. Above all, it fixes
one gate: **ML Phase 2 implementation cannot begin until these scientific decisions
are approved.**
