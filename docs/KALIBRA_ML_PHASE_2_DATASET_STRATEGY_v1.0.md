# Kalibra ML Phase 2 — Dataset Strategy v1.0

## About This Document

This document is the **authoritative dataset strategy** for the second
machine-learning phase of Kalibra. It fixes the scientific requirements that **any**
future dataset must satisfy before it may support a Kalibra claim.

It is **not** an implementation plan, and it is **not** a dataset acquisition
document. It writes no code, downloads no data, generates no hashes or manifests,
names no industrial domain, and performs no acquisition. It defines the **evidence
requirements** a dataset must meet and now records the governed acquisition rules for
the selected first proxy dataset, not the act of obtaining it.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_DATASET_STRATEGY_v1.0.md`](KALIBRA_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md`](KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md),
and
[`docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md`](KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md).

This document continues the ML Phase 2 planning sequence. It follows the Scientific
Architecture Plan (which fixed the scientific direction), the Framework ADR (which
fixed how a runtime would be evaluated and named this document as the next artifact),
the Dataset Selection ADR (`SELECTED — VisA`), the Evaluation Strategy (first VisA +
PaDiM protocol fixed), and the C-3 Governed VisA Acquisition Strategy Checkpoint.

**Binding gate.** No dataset may be used for ML Phase 2 evidence, and no
framework-backed implementation may begin, until the requirements in this document
are approved by the repository owner and the selected dataset is governed under the
records this document requires. VisA is selected as the first governed proxy dataset,
but it is not acquired by this document.

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
support a Kalibra claim. It also defines the governed acquisition process that a
future VisA acquisition must follow. It does **not** acquire data, and it grants no
authority to acquire, download, label, hash, manifest, train on, or evaluate data.
Dataset acquisition is a separate, owner-authorized activity gated by the approval
criteria in §11.

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
- **Dataset Selection ADR.** The repository records `SELECTED — VisA`: VisA is the
  governed proxy dataset and governance anchor for the first Kalibra ML baseline.
  MPDD remains the domain anchor for future domain-specific evolution. No dataset has
  been acquired by that ADR.
- **Evaluation Strategy and C-2 checkpoint.** The first VisA + PaDiM evaluation
  protocol is fixed, including frozen train/validation/test partition policy,
  immutable split manifests, per-file SHA-256 requirements, and the prohibition on
  benchmark, product, calibrated-confidence, and generalization claims.
- **C-3 Governed VisA Acquisition Strategy Checkpoint.** The governed acquisition
  source, archive identity, integrity policy, provenance record, local-governance
  layout, versioning policy, and fail-closed behavior are now defined. The checkpoint
  performs no acquisition, downloads no data, computes no hashes, and creates no
  manifests.

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
- **Immutable manifests.** For the first VisA baseline, train/validation/test
  membership must be recorded in immutable split manifests with per-file SHA-256
  hashes, and each split manifest must itself be hashed. A split-manifest hash change
  creates a new evaluation identity, never a silent re-run.

The first VisA baseline adopts the split convention fixed by the C-2 Evaluation
Protocol and the C-3 Governed VisA Acquisition Strategy. Future split proportions and
counts for other datasets remain downstream decisions and must be fixed before the
test partition is touched.

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

### 8.1 Governed VisA Acquisition

The first governed acquisition strategy is fixed for VisA by the
[`C-3 Governed VisA Acquisition Strategy Checkpoint`](checkpoints/KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md).
It is a strategy only: no archive is fetched, no hash is computed, and no manifest is
created by this document.

The canonical acquisition source is the official Amazon Science repository:

```text
https://github.com/amazon-science/spot-diff
```

The upstream repository commit used as the identity, license, and split authority is:

```text
2a692ab575001cbde74d402d897a7286086c6199
```

The canonical archive is:

```text
https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
```

with AWS object identity:

```text
arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar
```

The AWS Open Data Registry entry is corroborating evidence for the canonical object,
license, and managed-by record. It does not replace the archive hash or the upstream
repository commit as the governed identity anchors.

Third-party mirrors are forbidden as primary acquisition sources. Kaggle,
HuggingFace, tooling caches, academic re-hosts, repackaged archives, recompressed
archives, cleaned datasets, resized datasets, or prepared redistributions must not
define Kalibra's VisA identity. A mirror may be used only as a fallback recovery path
and only if its bytes reproduce Kalibra's recorded archive SHA-256 exactly. A mirror
never redefines identity, license, provenance, or splits.

The governed acquisition sequence is mandatory:

1. Pin the upstream repository commit as the identity, license, and split authority.
2. Fetch the canonical archive from the S3 URL into an immutable source location.
3. Compute the archive SHA-256 over the raw `.tar` bytes.
4. Verify recorded upstream metadata as a coarse corroborating gate.
5. Extract into a separate treated-as-immutable extracted dataset tree.
6. Generate the per-file SHA-256 manifest over the extracted tree.
7. Adopt the published split CSVs verbatim from the pinned commit and build immutable
   train/validation/test split manifests with per-file hashes.
8. Write the provenance manifest and attribution/license record.
9. Freeze the acquisition only when archive hash, per-file manifest, split manifest,
   provenance record, and attribution record all exist and cross-reference each other.

The acquisition record is immutable once accepted. Any later change to source bytes,
extracted bytes, manifests, splits, provenance, or attribution creates a new governed
version.

### 8.2 Dataset Identity

A governed VisA acquisition must preserve all of the following identities:

- **Upstream dataset identity:** VisA / Visual Anomaly, as defined by the official
  Amazon Science repository and publication record.
- **Archive identity:** `VisA_20220922.tar` from the canonical S3 object.
- **Repository commit identity:** `spot-diff@2a692ab575001cbde74d402d897a7286086c6199`.
- **Acquisition identity:** the local acquisition timestamp plus the archive SHA-256
  produced during the governed acquisition.
- **Governed local identity:** the tuple of archive SHA-256, per-file manifest hash,
  split-manifest hash, provenance hash, and local governed layout identity.

These identities must travel with every downstream scientific evidence record. A
result that cannot identify the upstream dataset, archive, commit, acquisition, and
governed local version is not accepted as Kalibra evidence.

### 8.3 Integrity Policy

SHA-256 is the integrity anchor for VisA. The future acquisition must record:

- archive SHA-256 over the raw `VisA_20220922.tar` bytes;
- per-file SHA-256 for every extracted image, mask, CSV, and label artifact;
- immutable train/validation/test split manifests with per-file SHA-256 hashes;
- split-manifest hashes;
- deterministic integrity-verification procedure;
- archive verification workflow.

The upstream ETag, content length, last-modified timestamp, and content type are
corroboration only. The VisA S3 ETag is a multipart object digest, not a content
SHA-256. It may help detect obvious source mismatch, but it is never the integrity
anchor.

Archive verification must fail closed. Reuse or re-acquisition must recompute the
archive SHA-256 and match the archive-of-record, recompute every per-file hash and
match the manifest set exactly, and recompute every split-membership hash. Additions,
removals, substitutions, or split drift create a mismatch and block downstream use.

### 8.4 Provenance Policy

The provenance record is mandatory and must include:

- acquisition source;
- acquisition timestamp in UTC;
- canonical archive URL;
- upstream identifiers, including archive name, repository commit, AWS ARN, DOI, and
  arXiv identifier where recorded by C-3;
- dataset license, utility-code license, and attribution obligations;
- attribution text sufficient to satisfy CC BY 4.0;
- upstream publication record;
- local governed identity;
- note that secondary CC BY-NC-SA 4.0 license claims are superseded by the official
  CC BY 4.0 dataset license record.

Provenance must always accompany future scientific evidence. No image, tensor,
manifest, metric, report, or claim may be presented without a traceable path back to
the provenance record.

### 8.5 Local Dataset Governance

The local governed dataset must preserve a strict source/derived boundary:

- **Immutable source archive.** The raw canonical archive is stored read-only and is
  never modified, rewritten, recompressed, deleted, or replaced in place.
- **Immutable extracted dataset.** The extracted upstream tree is treated as
  immutable source data.
- **Immutable manifests.** Archive, per-file, split, and provenance hashes are
  governed records and are not edited in place after acceptance.
- **Provenance record.** Source, license, attribution, upstream identity, acquisition
  identity, and local governed identity are preserved with the dataset.
- **Derived artifacts separated from source.** Preprocessed tensors, PaDiM statistics,
  model-fitting artifacts, exports, overlays, reports, or any other future artifacts
  must live outside the source data boundary and be regenerable from governed source
  records.

Source data must never be modified. Any transformation of source data creates a
derived artifact and must preserve lineage back to the immutable source and governed
identity records.

### 8.6 Versioning Policy

VisA has no formal upstream release tag or upstream strong checksum. Kalibra
therefore treats the dated archive `VisA_20220922` plus the pinned repository commit
as the effective upstream version for the first governed baseline.

The governed versioning model is:

- **Upstream version:** `VisA_20220922` plus
  `spot-diff@2a692ab575001cbde74d402d897a7286086c6199`.
- **Acquisition version:** a Kalibra-owned governed acquisition label keyed to the
  archive SHA-256; the hash, not the label, is the integrity identity.
- **Governed version:** archive SHA-256, per-file manifest hash, split-manifest hash,
  provenance hash, and local governed layout identity.

New upstream releases, republished archives, new dated archives, new official
versions, or changed archive bytes create new governed versions. They must be stored
side-by-side and must never overwrite existing governed versions. Migration to a new
governed version is a separate authorized decision; old evidence remains tied to the
old governed version.

### 8.7 Failure Policy

Governed acquisition must fail closed:

- **Archive hash mismatch:** hard stop. Reject the bytes; do not extract or use them.
- **Missing files:** hard stop. A partial dataset is never promoted to governed
  status.
- **Split mismatch:** hard stop for evaluation. A changed split-manifest hash is a
  new evaluation identity, never a silent re-run.
- **Provenance mismatch:** hard stop. Missing or inconsistent source, license,
  attribution, hash, or local identity information blocks use.
- **Changed upstream archive:** treat as a new dataset/acquisition version. Do not
  overwrite the existing governed version.

No degraded-mode acquisition exists. Any unresolved integrity, completeness, split,
or provenance defect blocks preprocessing, fitting, evaluation, evidence, and claims.

### 8.8 Integration Boundary

Governed acquisition supplies governed inputs only. It does not change ownership or
architecture:

- preprocessing ownership does not move;
- provider ownership does not move;
- loader ownership does not move;
- evaluation ownership does not move;
- evidence ownership does not move.

The governed acquisition envelope supplies source bytes, integrity records, split
records, provenance, attribution, and governed identity references. It must not alter
the `InspectionInferenceProvider` seam, the `InspectionPrediction` boundary,
`InspectionEngine.transform_prediction(...)`, model loading, preprocessing contracts,
evaluation ownership, or Evidence-domain preservation.

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

For the first VisA governed-acquisition strategy, this document additionally records
the following non-claims:

- no acquisition has been performed;
- no dataset has been downloaded;
- no archive hash has been generated;
- no per-file hash manifest has been generated;
- no split manifest has been generated;
- no implementation is authorized;
- no training is authorized;
- no evaluation is authorized;
- no benchmark claim is authorized;
- no product claim is authorized.

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
  linkage (§8) are in place. For the first VisA baseline, the archive SHA-256,
  per-file SHA-256 manifest, immutable split manifests, split-manifest hashes,
  provenance record, attribution/license record, and governed local identity required
  by §8.1–§8.8 must all exist and cross-reference each other before data use.
- **Fail-closed behavior.** Archive hash mismatch, missing files, split mismatch,
  provenance mismatch, or changed upstream archive behavior is handled according to
  §8.7 before any preprocessing, fitting, evaluation, evidence, or claim proceeds.
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

The following decisions remain intentionally deferred. The first dataset is selected
as VisA, and the governed VisA acquisition strategy is defined by §8 and the C-3
checkpoint. The items below are outside that strategy or belong to later authorized
work.

- **Labeling process.** The concrete process, standard, and reviewer arrangement by
  which ground truth is produced or verified.
- **Annotation tooling.** The tools and workflow used to create, review, and record
  annotations and their agreement and uncertainty.
- **Industrial domain of record.** VisA is a governed proxy, not Kalibra's domain of
  record. Any future domain-of-record dataset remains a separate decision.
- **Acquisition implementation.** The future sprint mechanics, local storage policy
  for large bytes, and review procedure for the governed VisA acquisition. The
  strategy is fixed; the acquisition has not been executed.
- **Future split proportions and counts.** The first VisA split policy is fixed by
  C-2/C-3; future datasets or future versions must fix their own splits before test
  access.
- **Future localization depth.** The first VisA protocol supports bounded
  localization where pixel labels support it; later datasets or phases must define
  their own localization depth.
- **Synthetic proportion.** The concrete role and proportion of any synthetic data in
  future datasets.

Deferred decisions remain deferred unless the repository owner authorizes them
through an approved downstream document.

---

## 13. Next Dependency

Recommended next dependency:

```text
Governed VisA Acquisition implementation authorization
```

The Dataset Selection ADR selected VisA, the Evaluation Strategy incorporated the C-2
protocol, and this document now incorporates the C-3 governed acquisition strategy.
The next dependency is repository-owner review and authorization of the governed VisA
acquisition implementation. That future work may fetch the archive and generate
hashes/manifests only after authorization; this document does none of those things.

The current decision order is therefore:

```text
Scientific Architecture   (approved)
        |
        v
Framework ADR             (proposed; selection deferred)
        |
        v
Dataset Strategy          (requirements fixed)
        |
        v
Dataset Selection ADR     (SELECTED — VisA)
        |
        v
Evaluation Strategy       (C-2 protocol fixed)
        |
        v
C-3 Acquisition Strategy  (checkpoint incorporated here)
        |
        v
Governed VisA Acquisition (future authorized implementation)
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

Implementation **must not** begin before the Framework ADR selection, this Dataset
Strategy, the Evaluation Strategy, governed VisA acquisition, and Implementation
Authorization are approved. Training and evaluation execution also remain blocked
until the C-2 and C-3 governed records exist.

---

## Closing Statement

This document fixes the scientific requirements a dataset must meet before it can
support any Kalibra claim. It now also records the governed VisA acquisition
strategy: canonical source and archive, mirror restrictions, identity preservation,
SHA-256 integrity anchors, immutable manifests, provenance, local source/derived
separation, versioning, fail-closed behavior, and integration boundaries. It
downloads no data, generates no hashes or manifests, authorizes no implementation,
and makes no scientific, benchmark, or product claim.

Above all it preserves Kalibra's discipline: the provider abstraction is untouched,
Inspection, Trust, Review, Evidence, and Evaluation each keep their ownership, and
**no scientific claim is made without reproducible evidence on qualifying data**. A
dataset earns its place not by being large or convenient, but by letting an observer
who does not trust Kalibra see exactly what the system can do — and exactly what it
cannot — and verify it for themselves.
