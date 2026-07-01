# Kalibra ML Phase 2 — Dataset Strategy v1.0

## About This Document

This document is the **authoritative dataset strategy** for the second
machine-learning phase of Kalibra. It fixes the scientific requirements that **any**
future dataset must satisfy before it may support a Kalibra claim.

It is **not** an implementation plan, and it is **not** a dataset acquisition
document. It writes no code, downloads no data, selects no dataset, names no
industrial domain, and fixes no train/validation/test numbers. It defines the
**evidence requirements** a dataset must meet, not the act of obtaining one.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_DATASET_STRATEGY_v1.0.md`](KALIBRA_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md`](KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md),
and
[`docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md`](KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md).

This document continues the ML Phase 2 planning sequence. It follows the Scientific
Architecture Plan (which fixed the scientific direction) and the Framework ADR
(which fixed how a runtime would be evaluated and named this document as the next
artifact), and it precedes the Evaluation Strategy (§13).

**Binding gate.** No dataset may be accepted for ML Phase 2, and no
framework-backed implementation may begin, until the requirements in this document
are approved by the repository owner and a candidate dataset is shown to satisfy
them. Until then, the dataset remains unselected by design.

---

## 1. Purpose

Dataset strategy precedes framework-backed implementation because the dataset **is
part of the evidence**, not a background detail of it. Under Kalibra's
evidence-precedes-assertion discipline, a scientific claim is only as credible as
the data it is demonstrated on. Fixing a runtime, wiring a trained model behind the
seam, or reporting a number before the data obligations are settled would force a
premature, undocumented commitment to whatever data happened to be convenient — the
exact failure the planning sequence exists to prevent.

The Framework ADR made this explicit: it deferred framework selection in part
because "framework fit cannot be finalized without knowing the data, labels, splits,
provenance, localization support, hardware expectations, and evaluation evidence
obligations," and it named
`KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md` as the required next planning
artifact. This document answers that requirement at the level of **requirements**,
not selection.

Accordingly, this document defines **what any dataset must provide** before it can
support a Kalibra claim. It does **not** acquire data, and it grants no authority to
acquire, download, label, or select data. Dataset acquisition is a separate,
owner-authorized activity gated by the approval criteria in §11.

The existing [`KALIBRA_DATASET_STRATEGY_v1.0.md`](KALIBRA_DATASET_STRATEGY_v1.0.md)
remains the standing dataset philosophy and governance for Kalibra as a whole. This
document does not replace it; it specializes it for ML Phase 2 and inherits every
obligation it states.

---

## 2. Current Baseline

ML Phase 2 dataset work begins from the following completed repository state. Each
item is already present and validated; none is re-opened here.

- **Deterministic fixture set.** Fixed PGM P2 inspection inputs (e.g. under
  `tests/fixtures/inspection/`) that provide byte-identical, offline, versioned
  content and act as the reproducibility backbone for boundary and replay tests.
- **`LocalArtifactInferenceProvider`.** The first real local provider, reading the
  deterministic PGM P2 fixture content with the Python standard library and deriving
  an `InspectionPrediction` from real bytes. It returns only `InspectionPrediction`
  and remains unwired from `InspectionEngine.inspect()`.
- **Prototype integration.** A prototype adapter that projects the real
  local-provider result into inspection-only prototype data, explicitly withholding
  calibrated confidence, trust, routing, drift, and evaluation claims.
- **Evidence-chain integration.** An opt-in path that runs the real local-provider
  result through the canonical
  Inspection → Trust Qualification → Human Review → Evidence → Evaluation chain, with
  downstream domains consuming only canonical records — never provider objects,
  predictions, pixels, or screenshots.
- **ML Phase 1 closure.** The ML Phase 1 local-provider path checkpoint is formally
  closed, with an explicit list of what remains unclaimed. It proved a boundary and
  a composition path, not machine-learning quality.
- **Scientific Architecture Plan.** The ML Phase 2 scientific baseline, fixing the
  scientific objectives, the anomaly-detection-first problem scope, the dataset
  obligations at direction level, the evaluation obligations, and the claim policy.
- **Framework ADR.** The proposed runtime-evaluation decision process, which selects
  no framework, defers implementation, and requires this dataset strategy before
  framework fit can be finalized.

**Why fixtures suffice for boundary validation but not for scientific validation.**
The deterministic fixtures were engineered to prove one thing: that the
Machine Learning → Inspection seam holds and composes correctly through the
canonical chain. For that purpose they are sufficient and appropriate — they are
byte-stable, offline, and reproducible, so they isolate the boundary from data
noise. But they were never assembled to answer a scientific question. They do not
represent the real variety of an inspection setting, they carry no vetted ground
truth beyond what a boundary test needs, they contain no honest population of hard
and ambiguous cases, and any metric computed on them would measure the fixtures, not
the method. A boundary is proven by construction; a scientific property is proven by
evidence on honest data. The fixtures give the first and **must not** be mistaken
for the second.

---

## 3. Scientific Dataset Requirements

A dataset may support a Kalibra scientific claim only when all of the following
mandatory properties hold. These properties concern the dataset **as evidence**;
they are prior to, and independent of, what the data contains (§4) or how it is
labeled (§5).

- **Provenance.** The origin of every input must be known and recorded — who or what
  produced it, under what conditions, and how it reached Kalibra. Data of unknown or
  unclear origin is declined, not used.
- **Licensing.** The terms under which the data may be used must be known, explicit,
  and compatible with Kalibra's intended local, reproducible, evidence-bearing use.
  Unclear or unverifiable licensing is a reason to decline, never a reason to
  proceed.
- **Ownership.** The rights to use the data for Kalibra's purpose must be established
  and recorded, including any third-party or upstream ownership that constrains use.
- **Traceability.** Every input and every label must be traceable to its source and
  to the process that produced it, so an observer can follow a result back to the
  exact data that produced it.
- **Reproducibility.** Every result must be regenerable from a fixed starting point
  by an observer who does not trust Kalibra, using the recorded data version and
  procedure — not merely by Kalibra, and not only once.
- **Versioning.** The dataset, its splits, and its label sets must each be fixed into
  a stable, identifiable version, so any result can be tied to exactly the data that
  produced it and distinguished from results on any other version.
- **Integrity verification.** The exact bytes of the data used for a result must be
  verifiable — for example by recorded content hashes — so corruption, silent
  substitution, or drift in the stored data can be detected.
- **Long-term availability.** The data used for a claim must remain obtainable in its
  fixed form for as long as the claim stands, so the evidence does not evaporate when
  an upstream source changes or disappears.

A dataset that lacks any of these properties **cannot** support a scientific claim,
regardless of how large, convenient, relevant, or high-performing it appears. The
missing property is recorded as the reason for declining, consistent with the
governance discipline of the standing dataset strategy.

---

## 4. Inspection Data Requirements

To support the anomaly-detection-first scope fixed by the Scientific Architecture
Plan, a dataset must contain inspection content of the following kinds and
variation. This section describes **what the data must contain**; it names no
dataset and fixes no counts.

Required content:

- **Good parts.** A population of sound inputs sufficient to characterize the normal
  distribution the method reasons against. Anomaly detection is grounded in what
  "sound" looks like; without a faithful population of good parts, deviation has no
  honest reference.
- **Defective parts.** A population of genuinely defective inputs, sufficient for the
  method's ability to separate defective from sound to be assessed rather than
  assumed.
- **Anomaly diversity.** Defects of more than one kind, severity, size, and
  subtlety — including hard, faint, and borderline defects — so the method is tested
  against real difficulty, not only against obvious cases.

Required variation:

- **Lighting variation.** Differences in illumination that a real inspection setting
  would exhibit, so results do not depend on a single controlled lighting regime.
- **Camera variation.** Differences in sensor, optics, focus, resolution, and framing
  representative of realistic capture, so results are not artifacts of one imaging
  path.
- **Manufacturing variation.** Legitimate part-to-part variation among sound units,
  so normal variation is not mistaken for defect and vice versa.
- **Environmental variation.** Differences in the surrounding conditions of capture
  (for example background, positioning, or contamination) that a deployment would
  realistically encounter.

**Why diversity matters.** Diversity is what turns a demonstration into evidence. A
dataset that is uniformly easy, uniformly lit, uniformly captured, and uniformly
manufactured proves nothing about the method's self-knowledge: it cannot show
whether the method is uncertain where it should be, whether it separates classes for
the right reasons, or whether it would survive conditions it was not tuned on.
Diversity is also what exposes hidden correlations and domain narrowness (§9) before
they become silent, overstated claims. A dataset without honest diversity limits
every claim drawn from it to the narrow conditions it actually represents, and that
limit **must** be stated with the claim.

---

## 5. Ground Truth

Ground truth is the reference every reliability claim is ultimately measured
against. A dataset must satisfy the following for the claims that depend on it.

- **Labels.** Each input must carry a trustworthy label sufficient for the scientific
  goal it supports — at minimum sound vs defective for detection. Absent or
  unreliable labels disqualify any claim that depends on them.
- **Localization.** Where defect localization is evaluated as the bounded secondary
  objective, the data must carry trustworthy localization ground truth (the location
  of the defect) for the inputs on which localization is claimed. Localization is
  measured only where such ground truth exists; where it does not, no localization
  claim is made.
- **Annotation quality.** Labels must be produced by a documented process, to a
  documented standard, so an observer can judge the labeling as well as the result.
  Annotation that conceals difficulty is treated as a defect in the data.
- **Reviewer agreement.** Where labels rest on human judgement, the degree of
  agreement between reviewers must be recorded, so the reliability of the ground
  truth itself is visible. Labels presented as certain when reviewers disagreed
  misrepresent the evidence.
- **Uncertainty.** Genuine uncertainty in the correct answer must be recorded rather
  than forced into false certainty. Uncertainty in the ground truth is part of the
  evidence, not noise to be removed.
- **Ambiguous cases.** Cases that are genuinely borderline or contested must be
  retained and marked as such, not discarded to make results look cleaner. Ambiguous
  cases are exactly where a method's honesty about its own doubt is tested.

Missing, weak, or opaque ground truth **limits** the claims that may be made. Where
ground truth is incomplete or uncertain, the limitation is stated plainly and the
dependent claim is narrowed or withdrawn — never presented as stronger than the
ground truth beneath it allows.

---

## 6. Dataset Splits

Any learned method must use documented dataset partitions. This section fixes the
**policy** for those partitions; consistent with the objective of this document, it
specifies **no percentages** and fixes **no counts**.

- **Train.** The partition a method may learn from. Nothing evaluated as evidence may
  be drawn from it.
- **Validation.** The partition used for development-time tuning and model selection.
  It informs choices during development but is not the source of final reported
  evidence.
- **Test.** The partition reserved solely for final evidence. It must remain
  untouched during development and be used only once the method is fixed.

Policy requirements:

- **Leakage prevention.** The separation between what a method learns from and what it
  is evaluated on must be genuine. Near-duplicates, shared capture sessions, shared
  physical parts, or shared derivation must not span partitions, so results reflect
  capability rather than memorized answers.
- **Independence.** The partitions must be independent to the degree the inspection
  setting allows, and any residual dependency (for example limited distinct physical
  parts) must be documented so its effect on the evidence can be judged.
- **Versioning.** The split definitions must themselves be versioned and tied to the
  dataset version, so an observer can reconstruct exactly which inputs were in which
  partition for a given result.
- **Frozen test sets.** The test partition must be frozen: defined once, recorded, and
  not revised in response to results. A test set that is adjusted after seeing
  outcomes is no longer honest evidence and **must not** be presented as such.

The concrete split proportions and counts are a deferred decision (§12) and belong
to the dataset selection and the Evaluation Strategy (§13), not to this document.

---

## 7. Synthetic Data Policy

Synthetic data may play a bounded, honest role. This section fixes what is
acceptable and what is not.

Techniques in scope:

- **Procedural generation.** Programmatically generated inputs used for controlled,
  reproducible variation.
- **Augmentation.** Transformations of real inputs (for example controlled changes in
  lighting, orientation, or noise) used to exercise variation reproducibly.
- **Simulation.** Modeled inputs standing in for a capture process or condition.
- **Synthetic defects.** Artificially introduced defects used to produce graded,
  controllable difficulty.

Acceptable uses:

- Producing **deterministic, reproducible fixtures** for boundary and replay tests,
  as the current baseline already does.
- Producing **controlled, graded variation** to demonstrate behavior under conditions
  that are hard to sample evenly from real data.
- **Supplementing** real data where the synthetic role, proportion, and generation
  procedure are documented and versioned.

Unacceptable uses:

- Letting a claim of **real-world inspection quality** rest on synthetic data alone.
  Real-world quality is claimed only on real, honestly labeled data.
- Using synthetic data to **manufacture apparent difficulty, diversity, or ground
  truth** that the real evidence does not contain.
- Introducing synthetic data into any partition **without recording** its presence,
  proportion, and role, or in a way that could leak the generation procedure across
  the train/test boundary.

Wherever synthetic data informs a claim, its **proportion and role must be stated**
with the claim. Synthetic data is a tool for reproducible variation, not a substitute
for honest real-world evidence.

---

## 8. Dataset Governance

Every dataset admitted for ML Phase 2 must be governed so that it can stand as
credible evidence. Governance is not administrative overhead; it is what makes the
data auditable.

- **Dataset version IDs.** Every dataset, split, and label set carries a stable,
  unique version identifier, so any result names exactly the data it was produced on.
- **Hashes.** The exact content used for a result is recorded by content hash, so its
  integrity can be verified and silent substitution or corruption detected (§3).
- **Metadata.** The dataset's characteristics, known biases, gaps, capture
  conditions, and limitations are recorded alongside it, so results can be
  interpreted in light of what the data can and cannot show.
- **Lineage.** The chain from source through any transformation, augmentation,
  labeling, and splitting is recorded, so every derived artifact traces back to its
  origin.
- **Provenance.** The origin and terms of the data are documented before it is relied
  upon, per §3, and preserved with the dataset record.
- **Reproducibility.** The recorded version, splits, procedure, and configuration are
  sufficient for an untrusting observer to regenerate any result from a fixed
  starting point.
- **Evidence linkage.** Each dataset artifact is linkable to the evidence records the
  canonical chain preserves, so a preserved result can be tied to the exact dataset
  version, split, and labels behind it. This linkage is recorded through the Evidence
  domain, which **owns** preservation, lineage, and read-only evidence views; the
  dataset governance record supplies the identifiers it references and does not
  assume Evidence's ownership.

Governance obligations apply for as long as any claim rests on the data (§3,
long-term availability).

---

## 9. Scientific Risks

A dataset can undermine a claim as easily as it can support one. The following risks
must be reasoned about explicitly for any candidate dataset; each unaddressed risk
is a reason to narrow or withhold a claim.

- **Bias.** Systematic skew in what the data represents (for example over-representing
  one part type, condition, or defect) that makes results unrepresentative of the
  inspection setting claimed.
- **Imbalance.** Too few examples of the outcomes that matter — especially rare
  defects — for behavior on them to be assessed, such that an average metric hides
  failure on the cases that count.
- **Overfitting.** Evidence that reflects a method memorizing the specific data
  rather than capturing genuine capability, especially on small or narrow datasets.
- **Leakage.** Information shared across the train/validation/test boundary (§6) that
  inflates apparent performance and produces evidence that would not survive on truly
  unseen data.
- **Annotation noise.** Errors, inconsistency, or hidden difficulty in the labels
  (§5) that corrupt the reference every claim is measured against.
- **Domain shift.** Systematic differences between the dataset's setting and any other
  deployment setting, such that results do not transfer. No cross-domain
  generalization is claimed from a single-domain dataset.
- **Hidden correlations.** Spurious cues (for example a background, timestamp,
  capture artifact, or lighting quirk correlated with the label) that let a method
  appear to separate classes for the wrong reason.

For each risk, the obligation is the same: identify it, record it, and let it
**constrain the claim**. A risk that cannot be ruled out is disclosed, and the claim
that depends on the data is tempered accordingly.

---

## 10. Claim Policy

This section fixes what Kalibra **may and may not claim** from dataset evidence. It
separates three kinds of claim that must never be conflated, consistent with the
claim policy of the Scientific Architecture Plan.

- **Engineering claims** — that the data is correctly contained and composed: that a
  provider reads it behind the seam and returns only `InspectionPrediction`, that the
  fixtures replay deterministically, that governance records exist. These are true or
  false by construction and testing. They establish that the data is handled
  correctly; they establish **nothing** about inspection quality.
- **Scientific claims** — that the method exhibits a real property on the data:
  detection separation, usable signal in the raw anomaly measure, informative
  uncertainty, meaningful localization. These may be made **only** with reproducible
  evidence on a fixed, honestly labeled dataset satisfying §3–§9, on an untouched,
  frozen test partition, with both error kinds reported and dataset risks disclosed.
- **Product claims** — that a user or stakeholder can rely on what a surface presents.
  These are downstream of, and gated by, the scientific claims. A product surface
  **must not** imply detection quality, calibrated confidence, accuracy, or
  robustness beyond what the scientific evidence supports, and **must not** present a
  raw anomaly measure as confidence.

Binding rules on dataset evidence:

- **No benchmark without evidence.** No performance number may be stated without a
  reproducible artifact, a named dataset version, and a documented procedure.
- **No scientific claim without evidence.** A property is described as true only once
  a reproducible artifact on qualifying data supports it. Absence of evidence is
  reported as absence, not glossed over.
- **Ownership is preserved.** Dataset evidence does not move ownership. The Inspection
  Engine **owns** validation and transformation into `RawInspectionResult`; Trust
  Qualification **owns** calibrated confidence, uncertainty characterization, and
  drift caution; Human Review **owns** review-case preparation and reviewer decision
  recording; Evidence **owns** preservation, lineage, and read-only views; Evaluation
  **owns** evidence-backed evaluation reports. A dataset supplies inputs and ground
  truth; it does not authorize any domain to claim another's responsibility.
- **Confidence stays with Trust.** No dataset result licenses describing an output as
  calibrated. Calibration and drift remain Trust-domain scientific concerns, gated by
  their own evidence, and are out of scope for what this dataset strategy may claim.

Any claim that cannot be traced to reproducible evidence under this policy is, by
default, **not made**.

---

## 11. Dataset Approval Criteria

A dataset may be accepted for ML Phase 2 **only** when all of the following objective
criteria are met and recorded. Each is verifiable; none is a matter of preference.

- **Scientific properties.** Provenance, licensing, ownership, traceability,
  reproducibility, versioning, integrity verification, and long-term availability
  (§3) are all established and recorded.
- **Inspection content.** The data contains good and defective parts with honest
  anomaly diversity, and the lighting, camera, manufacturing, and environmental
  variation (§4) needed to support the anomaly-detection-first scope.
- **Ground truth.** Labels — and localization ground truth where localization is
  claimed — meet the quality, agreement, uncertainty, and ambiguity requirements of
  §5, with limitations stated.
- **Splits.** Versioned, leakage-free, independent train/validation/test partitions
  exist, with a frozen test set (§6).
- **Synthetic data.** Any synthetic component conforms to §7, with its proportion and
  role documented, and no real-world claim rests on synthetic data alone.
- **Governance.** Version IDs, hashes, metadata, lineage, provenance, and evidence
  linkage (§8) are in place.
- **Risks.** The scientific risks of §9 have been assessed for this dataset,
  documented, and reflected in the scope of the claims it may support.
- **Owner approval.** The repository owner explicitly approves the dataset against
  these criteria, and the approval, the dataset version, and any recorded limitations
  are captured in the project record.

A dataset that fails any criterion is set aside, and the failing criterion is
recorded as the reason. Meeting these criteria authorizes a dataset as **evidence
material only**; it does not by itself authorize framework-backed implementation,
which additionally requires the approved Framework ADR selection and the approved
Evaluation Strategy.

---

## 12. Open Decisions

The following decisions are intentionally deferred. None is made by this document;
each must be settled by an approved downstream decision before it can constrain
implementation.

- **First dataset.** Which specific dataset is accepted first for ML Phase 2.
- **Labeling process.** The concrete process, standard, and reviewer arrangement by
  which ground truth is produced or verified.
- **Annotation tooling.** The tools and workflow used to create, review, and record
  annotations and their agreement and uncertainty.
- **Industrial domain.** The specific inspection setting or industrial domain the
  first dataset represents.
- **Acquisition strategy.** How data is obtained, under what terms, and with what
  ownership and licensing arrangement.
- **Split proportions and counts.** The concrete train/validation/test proportions
  and sizes, which cannot be fixed before the dataset is known and belong to the
  Evaluation Strategy.
- **Localization depth.** How far localization is pursued as a secondary objective and
  what localization ground truth supports it.
- **Synthetic proportion.** The concrete role and proportion of any synthetic data in
  the first dataset.

Deferred decisions remain deferred unless the repository owner authorizes them
through an approved downstream document.

---

## 13. Next Planning Artifact

Recommended next planning artifact:

```text
KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md
```

Evaluation strategy must follow dataset strategy, and both must precede
implementation. The reason is ordering by dependency: an evaluation is only
meaningful with respect to the data it is computed on. Metrics, decision thresholds,
statistical-validation procedure, and the definition of what counts as reproducible
evidence all depend on the dataset's content, ground truth, splits, and risks. Fixing
an evaluation procedure before the dataset requirements are approved would either
bind the evaluation to assumptions the data may not satisfy, or invite an evaluation
tuned to flatter a not-yet-chosen dataset — both of which the claim policy (§10)
forbids.

The recommended decision order is therefore unchanged from the Scientific
Architecture Plan roadmap:

```text
Scientific Architecture   (approved)
        |
        v
Framework ADR             (proposed; selection deferred)
        |
        v
Dataset Strategy          (this document — approve before proceeding)
        |
        v
Evaluation Strategy       (metrics and procedure fixed for the approved dataset)
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

Implementation **must not** begin before the Framework ADR selection, this Dataset
Strategy, and the Evaluation Strategy are approved, and before a specific dataset is
shown to satisfy the approval criteria in §11.

---

## Closing Statement

This document fixes the scientific requirements a dataset must meet before it can
support any Kalibra claim. It selects no dataset, downloads none, names no industrial
domain, and fixes no split numbers. It requires provenance, licensing, ownership,
traceability, reproducibility, versioning, integrity verification, and long-term
availability; it requires honest inspection content and diversity, trustworthy ground
truth, leak-free frozen splits, a bounded synthetic-data policy, auditable
governance, and explicit reasoning about scientific risk.

Above all it preserves Kalibra's discipline: the provider abstraction is untouched,
Inspection, Trust, Review, Evidence, and Evaluation each keep their ownership, and
**no scientific claim is made without reproducible evidence on qualifying data**. A
dataset earns its place not by being large or convenient, but by letting an observer
who does not trust Kalibra see exactly what the system can do — and exactly what it
cannot — and verify it for themselves.
