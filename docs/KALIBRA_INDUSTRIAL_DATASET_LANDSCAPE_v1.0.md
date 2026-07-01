# Kalibra — Industrial Dataset Landscape v1.0

## About This Document

This document is a **landscape survey** of public industrial visual-inspection
datasets that could, in principle, support Kalibra's ML Phase 2. It exists to inform
a future Dataset Selection ADR; it **selects no dataset, recommends none, and
authorizes no acquisition.**

It is not an implementation plan and not a dataset-acquisition document. It writes no
code and downloads no data. It surveys what exists, records what can be verified from
official sources, and marks clearly where a fact could not be confirmed.

Throughout, **must**, **must not**, **owns**, and **does not own** carry the same
binding sense as in the ML Phase 2 governance documents
([`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md`](KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md)).

### Verification convention

To honor the Dataset Strategy's demand that provenance and licensing be **known, not
assumed**, this document separates two kinds of statement:

- **Verified** — confirmed against an official or primary source (a dataset's own
  page, its authors' repository, or the hosting institution) during preparation of
  this document (research conducted July 2026).
- **Observation** — an inference, a secondary-source report, or an unconfirmed
  detail. Observations are **not** treated as facts and **must** be re-verified
  before any selection.

Licensing is the area of greatest risk. Where sources disagree or a license could not
be confirmed, this document records the disagreement rather than resolving it. No
statement here grants permission to use any dataset; permission is established only at
selection time, against the original source, per the Dataset Strategy.

---

## 1. Purpose

Dataset selection begins with a landscape survey, not with an immediate choice,
because choosing first would invert Kalibra's evidence discipline. A dataset is part
of the evidence (Dataset Strategy §1); picking one before the field is understood
would commit Kalibra to whatever was familiar or convenient, and would risk
importing a benchmark's blind spots — narrow domains, saturated leaderboards,
unclear licensing — as if they were neutral ground. Surveying first makes the
trade-offs visible **before** any commitment is possible to defend or regret.

This document therefore supports a future architectural decision and **makes no
recommendation**. It maps the candidate datasets against qualitative criteria
(§3), records what is verifiable about each (§4), compares them without ranking
(§5), and surfaces the licensing, scientific, and gap considerations (§6–§8) that a
Dataset Selection ADR (§11) must resolve. It selects nothing, and it grants no
authority to acquire, download, or label data — that authority is governed by the
Dataset Strategy approval criteria and the Implementation Authorization gate, not by
this survey.

---

## 2. Kalibra Target Domain

The survey is read against Kalibra's intended inspection scope, fixed by the
Scientific Architecture Plan and specialized here only to frame relevance. Kalibra's
target domain is:

- **Industrial visual inspection.** Deciding, from a stabilized visual input, whether
  a manufactured item is sound or defective — an inspection task, not a general
  computer-vision task.
- **Precision manufactured components.** Parts made to tight tolerances, where defects
  are often small, subtle, and consequential.
- **Cast aluminium parts.** Components produced by casting, where anomalies include
  porosity, inclusions, cracks, and surface irregularities characteristic of the
  process.
- **Machined components.** Parts finished by machining (for example CNC operations),
  where anomalies include tool marks, dimensional/surface defects, and finishing
  faults.
- **Anomaly detection first.** The primary sub-problem is separating defective from
  sound inputs, aligned with the raw-anomaly-measure substrate and the
  "trained mostly on sound data" reality of inspection.
- **Bounded localization.** Indicating *where* a suspected defect lies is a secondary
  objective, pursued only where ground truth supports its evaluation.
- **Offline-first deployment.** Inference runs fully locally, deterministically, and
  reproducibly, with no hosted or network dependency.

A dataset's relevance to Kalibra is judged by how well it speaks to *this* domain —
not by its popularity or size. Cast aluminium and machined-component inspection are
the sharpest lens: datasets close to them are most relevant, and their scarcity is
itself a finding (§8).

---

## 3. Evaluation Criteria

The following qualitative criteria frame the survey. Consistent with the objective of
this document, **no numerical score is assigned** and no weighting is fixed; these
are lenses for description, not a scorecard.

- **Scientific quality.** Whether the data supports honest demonstration of behavior,
  including failure, rather than flattering results.
- **Industrial relevance.** How closely the setting reflects real industrial
  inspection, and specifically Kalibra's target domain (§2).
- **Anomaly detection suitability.** Whether the data supports the sound-vs-defective
  separation that is Kalibra's primary sub-problem, including a faithful population
  of sound inputs.
- **Localization support.** Whether trustworthy defect-location ground truth (for
  example pixel masks) exists to support the bounded secondary objective.
- **Annotation quality.** Whether labels are produced by a documented process, with
  difficulty and ambiguity recorded rather than hidden.
- **Reproducibility.** Whether the data can be fixed into a stable, versioned,
  integrity-verifiable form and regenerated by an untrusting observer.
- **Licensing.** Whether terms of use are known, explicit, and compatible with
  Kalibra's intended use; unclear terms are a reason to decline.
- **Documentation quality.** Whether an official description of content, collection,
  and limitations exists.
- **Maintenance.** Whether the dataset is maintained, hosted stably, and likely to
  remain available.
- **Community adoption.** Whether the dataset is widely used, which aids comparison
  but also raises overfitting risk (§7).
- **Benchmark relevance.** Whether the dataset functions as a recognized benchmark,
  and what that implies for both comparability and saturation.

---

## 4. Candidate Dataset Survey

Each entry records **verified** facts where confirmed against an official/primary
source, and marks anything unconfirmed as an **observation**. "Suitability for
Kalibra" is an observation in every case — a framing for the future ADR, never a
recommendation. **No licensing statement here authorizes use.**

### 4.1 MVTec AD

- **Purpose.** Benchmark for unsupervised industrial anomaly detection and
  localization.
- **Maintainer.** MVTec Software GmbH. *(Verified.)*
- **Licensing.** CC BY-NC-SA 4.0 — non-commercial use only; the dataset page states
  it is not allowed to use the dataset for commercial purposes. *(Verified.)*
- **Official source.** `https://www.mvtec.com/company/research/datasets/mvtec-ad`.
  *(Verified.)*
- **Inspection domain.** 15 categories spanning object and texture classes (e.g.
  industrial objects and textured surfaces). *(Verified.)*
- **Image modality.** High-resolution photographic images; exact color/grayscale
  breakdown per category not confirmed here. *(Observation.)*
- **Anomaly types.** Many defect types per category (scratches, dents, contamination,
  structural faults, etc.). *(Observation, from general documentation.)*
- **Localization support.** Yes — pixel-precise anomaly annotations. *(Verified.)*
- **Strengths.** De facto standard benchmark; clean train/test structure with sound
  training data; strong localization ground truth; well documented.
- **Limitations.** Non-commercial license; heavy community saturation raises
  overfitting risk (§7); not specific to cast aluminium or machined parts.
- **Suitability for Kalibra.** *(Observation.)* Highly relevant as a scientific
  reference for anomaly-detection-first with localization, but the non-commercial
  term and benchmark saturation are material considerations for the ADR.

### 4.2 MVTec AD 2

- **Purpose.** Successor benchmark with advanced/ more challenging scenarios for
  unsupervised anomaly detection.
- **Maintainer.** MVTec Software GmbH. *(Verified.)*
- **Licensing.** CC BY-NC-SA 4.0 — non-commercial. *(Verified.)*
- **Official source.** `https://www.mvtec.com/company/research/datasets/mvtec-ad-2`.
  *(Verified.)*
- **Inspection domain.** Industrial anomaly detection under harder conditions
  (lighting variation and other advanced scenarios). *(Verified in outline; full
  category list not confirmed here.)*
- **Image modality.** Photographic images. *(Observation.)*
- **Anomaly types.** Diverse defects under more demanding capture conditions.
  *(Observation.)*
- **Localization support.** Pixel-level anomaly annotations, consistent with the MVTec
  line. *(Observation — confirm against source.)*
- **Strengths.** Introduces harder, more realistic conditions (e.g. lighting) that
  speak to Kalibra's diversity requirements; recent (associated 2024 arXiv work by
  Heckler-Kram et al.).
- **Limitations.** Non-commercial license; newer, so tooling and comparison points are
  less settled; not domain-specific to Kalibra's parts.
- **Suitability for Kalibra.** *(Observation.)* Scientifically interesting for its
  harder conditions, subject to the same non-commercial constraint as MVTec AD.

### 4.3 VisA (Visual Anomaly)

- **Purpose.** Large visual anomaly detection/segmentation dataset (from the
  SPot-the-Difference work).
- **Maintainer.** Amazon Science (`amazon-science/spot-diff`), ECCV 2022.
  *(Verified.)*
- **Licensing.** **Sources disagree.** The AWS Registry of Open Data and the project
  GitHub indicate CC BY 4.0; some third-party tooling docs (Anomalib) state
  CC BY-NC-SA 4.0. **Unresolved — must be verified against the original source before
  any use.** *(Verified that a discrepancy exists; the correct term is not settled
  here.)*
- **Official source.** `https://github.com/amazon-science/spot-diff` and the AWS Open
  Data registry entry for VisA. *(Verified.)*
- **Inspection domain.** 12 object classes across 3 domains. *(Verified.)*
- **Image modality.** Photographic images. *(Observation.)*
- **Anomaly types.** Surface and structural defects, plus multi-instance/placement
  anomalies. *(Observation.)*
- **Localization support.** Yes — both image-level and pixel-level annotations.
  *(Verified.)*
- **Strengths.** Large (10,821 images: 9,621 normal, 1,200 anomaly, per project
  reporting); image- and pixel-level labels; potentially permissive license if CC
  BY 4.0 is confirmed.
- **Limitations.** The licensing discrepancy is a genuine risk; not specific to
  Kalibra's target parts.
- **Suitability for Kalibra.** *(Observation.)* Attractive scale and annotation depth;
  the license question is the decisive open item.

### 4.4 BTAD (BeanTech Anomaly Detection)

- **Purpose.** Real-world industrial anomaly detection benchmark.
- **Maintainer.** Associated with BeanTech / the BTAD authors. *(Observation — confirm
  maintainer and hosting.)*
- **Licensing.** Reported as CC BY-SA 4.0. *(Observation — verify against the original
  release.)*
- **Official source.** Distributed via the authors' materials and mirrors (e.g.
  dataset aggregators); a single canonical URL should be confirmed. *(Observation.)*
- **Inspection domain.** 3 industrial products with body and surface defects.
  *(Verified in outline.)*
- **Image modality.** Photographic images. *(Observation.)*
- **Anomaly types.** Body and surface defects across the 3 products. *(Verified in
  outline.)*
- **Localization support.** Pixel-level masks for defective regions. *(Observation.)*
- **Strengths.** Real industrial capture; small and tractable; used as a secondary
  benchmark alongside MVTec AD.
- **Limitations.** Small (≈2,830 images); only 3 products; canonical source and exact
  license should be re-confirmed.
- **Suitability for Kalibra.** *(Observation.)* Real-industrial character is relevant;
  scale and provenance clarity are the open items.

### 4.5 MPDD (Metal Parts Defect Detection)

- **Purpose.** Benchmark for defect detection on industrial **metal parts**.
- **Maintainer.** Stepan Jezek and Radim Burget, Brno University of Technology (VUT);
  repository `stepanje/MPDD`. *(Verified maintainers.)*
- **Licensing.** A LICENSE file exists in the repository, but the specific license
  type was **not confirmed** here. **Must be verified before use.** *(Observation.)*
- **Official source.** `https://github.com/stepanje/MPDD`. *(Verified.)*
- **Inspection domain.** Metal parts manufacturing — 6 types of metal parts.
  *(Verified.)*
- **Image modality.** Photographic images of metal parts under varying conditions.
  *(Observation.)*
- **Anomaly types.** Multiple defect types across the metal parts. *(Observation.)*
- **Localization support.** Yes — pixel-precise defect annotation masks (>1000
  images). *(Verified.)*
- **Strengths.** **The closest surveyed match to Kalibra's metal-component domain**;
  pixel-precise masks; explicitly aimed at industrial metal-part inspection with
  varied conditions.
- **Limitations.** Relatively small; license type unconfirmed; not cast-aluminium
  specific.
- **Suitability for Kalibra.** *(Observation.)* On domain grounds the most directly
  relevant candidate; the unconfirmed license is the decisive open item.

### 4.6 KolektorSDD (KSDD)

- **Purpose.** Surface-defect detection benchmark from a production inspection setting.
- **Maintainer.** ViCoS Lab, University of Ljubljana; industrial partner Kolektor
  Group. *(Verified.)*
- **Licensing.** CC BY-NC-SA 4.0 — non-commercial; commercial use requires contacting
  Danijel Skočaj. *(Verified.)*
- **Official source.** `https://www.vicos.si/resources/kolektorsdd/`. *(Verified.)*
- **Inspection domain.** Electrical commutators (surface inspection). *(Verified.)*
- **Image modality.** Grayscale images. *(Verified.)*
- **Anomaly types.** Surface cracks/defects on commutators. *(Observation.)*
- **Localization support.** Pixel-level defect annotations. *(Observation.)*
- **Strengths.** Genuine production-line provenance; clear official source and license.
- **Limitations.** Non-commercial; narrow single-component domain; small.
- **Suitability for Kalibra.** *(Observation.)* Real-industrial provenance is
  relevant; domain narrowness and non-commercial term are considerations.

### 4.7 KolektorSDD2 (KSDD2)

- **Purpose.** Larger successor surface-defect dataset from a production inspection
  system.
- **Maintainer.** ViCoS Lab; provided and partially annotated by Kolektor Group.
  *(Verified.)*
- **Licensing.** CC BY-NC-SA 4.0 — non-commercial. *(Verified.)*
- **Official source.** `https://www.vicos.si/resources/kolektorsdd2/`. *(Verified.)*
- **Inspection domain.** Defective production items (color surface inspection).
  *(Verified.)*
- **Image modality.** Color images. *(Verified.)*
- **Anomaly types.** Varied surface defects. *(Observation.)*
- **Localization support.** Pixel-level annotations. *(Observation.)*
- **Strengths.** Larger and richer than KSDD; real production provenance; clear
  source and license.
- **Limitations.** Non-commercial; still a specific surface-inspection setting, not
  Kalibra's parts.
- **Suitability for Kalibra.** *(Observation.)* A stronger real-industrial reference
  than KSDD; same non-commercial constraint.

### 4.8 DAGM 2007

- **Purpose.** Weakly-supervised industrial optical inspection competition dataset.
- **Maintainer.** Matthias Wieler, Tobias Hahn, Fred A. Hamprecht; Heidelberg
  Collaboratory for Image Processing (HCI), University of Heidelberg. *(Verified
  authors/host.)*
- **Licensing.** Reported as CC BY 4.0 on common mirrors (e.g. Kaggle); the original
  DAGM competition terms should be confirmed against the HCI source. **Re-verify.**
  *(Observation.)*
- **Official source.** HCI Heidelberg
  (`https://hci.iwr.uni-heidelberg.de/content/weakly-supervised-learning-industrial-optical-inspection`);
  widely mirrored. *(Verified host.)*
- **Inspection domain.** Textured-surface optical inspection, 10 defect classes on
  **synthetically generated** backgrounds and defects. *(Verified in outline.)*
- **Image modality.** Grayscale texture images. *(Observation.)*
- **Anomaly types.** Synthetic surface defects across 10 texture classes.
  *(Verified.)*
- **Localization support.** Weak/approximate defect region labels (ellipse-style),
  not fine pixel masks. *(Observation.)*
- **Strengths.** Long-standing, freely mirrored; controlled difficulty.
- **Limitations.** **Synthetic**, so real-world claims cannot rest on it (Dataset
  Strategy §7); weak localization; dated.
- **Suitability for Kalibra.** *(Observation.)* Useful as a controlled/synthetic
  reference only; not a basis for real-world inspection claims.

### 4.9 Magnetic Tile Defect

- **Purpose.** Surface-defect detection/saliency on magnetic tiles.
- **Maintainer.** Yibin Huang, Congying Qiu, Kui Yuan (2018); repository
  `abin24/Magnetic-tile-defect-datasets.`. *(Verified authors/repo.)*
- **Licensing.** **Not confirmed** — no explicit license located during this survey.
  **Must be verified before use.** *(Observation.)*
- **Official source.** `https://github.com/abin24/Magnetic-tile-defect-datasets.`.
  *(Verified.)*
- **Inspection domain.** Magnetic tile surface inspection. *(Verified.)*
- **Image modality.** Photographic images (varied real conditions). *(Observation.)*
- **Anomaly types.** Blowhole, crack, fray, break, uneven, plus defect-free (≈1,344
  images). *(Verified.)*
- **Localization support.** Pixel/saliency masks for defects. *(Observation.)*
- **Strengths.** Real surface defects with masks; captures real lighting variation.
- **Limitations.** Small; **license unclear**; narrow single-component domain.
- **Suitability for Kalibra.** *(Observation.)* Relevant defect character, but the
  absent license confirmation is a blocking open item.

### 4.10 NEU Surface Defect Database

- **Purpose.** Classification (and detection variants) of steel-strip surface defects.
- **Maintainer.** Song Kechen (and Yan), Northeastern University (China).
  *(Verified.)*
- **Licensing.** No explicit license located; described as available for research use.
  **Terms must be confirmed before any non-research use.** *(Observation.)*
- **Official source.** NEU faculty page
  (`http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html`); also
  mirrored on Kaggle. *(Verified host.)*
- **Inspection domain.** Hot-rolled steel-strip surface defects. *(Verified.)*
- **Image modality.** Grayscale, 200×200; 1,800 images, 6 classes × 300. *(Verified.)*
- **Anomaly types.** Crazing, inclusion, patches, pitted surface, rolled-in scale,
  scratches. *(Verified.)*
- **Localization support.** The classification set is image-level; detection variants
  add bounding boxes, not pixel masks. *(Observation.)*
- **Strengths.** Well known; clean 6-class structure; real steel-surface defects.
- **Limitations.** Primarily classification (a sub-problem out of ML Phase 2 scope);
  weak localization; license unspecified.
- **Suitability for Kalibra.** *(Observation.)* Limited fit to anomaly-detection-first
  with localization; more a classification reference.

### 4.11 Severstal Steel Defect Detection

- **Purpose.** Kaggle competition for steel-surface defect segmentation/classification.
- **Maintainer.** Severstal (competition sponsor), hosted by Kaggle. *(Verified.)*
- **Licensing.** Governed by **Kaggle competition rules** requiring rule acceptance to
  access data; competition data is generally **not freely redistributable**. **Terms
  must be read and confirmed at the source.** *(Observation, with high confidence that
  competition-rule constraints apply.)*
- **Official source.** `https://www.kaggle.com/c/severstal-steel-defect-detection`.
  *(Verified.)*
- **Inspection domain.** Flat steel-surface inspection. *(Verified.)*
- **Image modality.** Grayscale-like photographic strip images. *(Observation.)*
- **Anomaly types.** 4 defect classes, run-length-encoded segmentation. *(Verified in
  outline.)*
- **Localization support.** Yes — segmentation masks (RLE). *(Verified in outline.)*
- **Strengths.** Large, real, industrially sponsored; pixel-level segmentation.
- **Limitations.** **Competition-rule licensing** complicates reproducible
  redistribution and long-term availability (Dataset Strategy §3); test labels
  withheld; not Kalibra's parts.
- **Suitability for Kalibra.** *(Observation.)* Scientifically rich but the
  redistribution/availability constraints are a serious governance concern.

### 4.12 Additional relevant datasets (noted, not surveyed in full)

The following recur in the industrial-inspection literature and may warrant inclusion
in the ADR; they are noted here without full verification:

- **MVTec LOCO AD** — logical + structural anomalies (MVTec; expected non-commercial).
  *(Observation.)*
- **MVTec 3D-AD** — 3D/point-cloud industrial anomalies (MVTec). Out of Kalibra's
  single-2D-input scope, noted for completeness. *(Observation.)*
- **Real-IAD** — large multi-view real industrial anomaly dataset. *(Observation —
  verify maintainer/license.)*
- **GDXray / GDXray+** — X-ray images including **castings** (relevant to cast
  aluminium via a different modality). *(Observation — verify terms.)*
- **AITEX** — fabric surface defects. *(Observation.)*

These are recorded so the ADR's field is not artificially narrowed to the twelve core
entries; each requires the same verification discipline before it counts.

---

## 5. Comparative Analysis

The comparison is qualitative and **avoids any numerical ranking**. It reads the
survey along the dimensions that matter to Kalibra.

- **Anomaly detection.** The MVTec line (AD, AD 2, LOCO), VisA, BTAD, MPDD, and the
  Kolektor datasets are structured for the sound-vs-defective framing Kalibra needs,
  typically with abundant sound data and sparser, varied defects. NEU is primarily a
  classification set and fits the anomaly-detection-first framing least well.
- **Localization.** MVTec AD, VisA, MPDD, KSDD/KSDD2, Magnetic Tile, and Severstal
  offer pixel- or mask-level defect ground truth; DAGM offers only weak region labels;
  NEU (classification) offers little. Localization support and its *granularity*
  differ sharply and should not be treated as uniform.
- **Industrial realism.** KSDD/KSDD2 (production line), MPDD (metal parts), Magnetic
  Tile, Severstal (steel production), and BTAD carry genuine industrial provenance;
  DAGM is synthetic; the MVTec line and VisA are real but curated benchmark settings
  rather than a single production line.
- **Dataset maturity.** MVTec AD, DAGM, and NEU are long-established and heavily used;
  VisA, KSDD2, MPDD are established; MVTec AD 2 is recent. Maturity aids comparison but
  correlates with saturation (§7).
- **Reproducibility.** Datasets with a stable institutional home and clear versioning
  (MVTec, ViCoS/Kolektor, Heidelberg/DAGM) are easiest to fix and regenerate;
  competition-gated data (Severstal) and single-repository datasets with unclear
  licensing (Magnetic Tile) pose reproducibility and long-term-availability risk.
- **Benchmark usage.** MVTec AD is the dominant anomaly-detection benchmark, with VisA
  a common companion; NEU and Severstal are common in steel-defect work; DAGM is a
  classic. Heavy benchmark usage cuts both ways — comparability up, headroom down.
- **Long-term viability.** Institutionally hosted datasets (MVTec, ViCoS, Heidelberg)
  look most durable; datasets whose availability depends on a single personal
  repository or a competition platform are more fragile.

No dataset is best on all dimensions, and none is dismissed here. The comparison
exists to show the shape of the trade-space the ADR must navigate, not to pre-empt it.

---

## 6. Licensing Considerations

Licensing is where this survey is most cautious, because the Dataset Strategy treats
unclear permissions as a reason to decline, not to proceed. Nothing below grants
permission; each term must be confirmed at the original source at selection time.

- **Research use.** Most surveyed datasets permit research use, but "research use" is
  not the same as Kalibra's intended use and does not by itself authorize anything.
- **Commercial use.** The MVTec datasets and the Kolektor datasets are **CC BY-NC-SA
  4.0 — non-commercial** (*verified*); commercial use is disallowed or requires direct
  permission. If Kalibra's use is or may become commercial, these terms are
  load-bearing constraints, not footnotes.
- **Redistribution.** Competition-gated data (Severstal, *observation with high
  confidence*) is generally not redistributable and requires rule acceptance;
  ShareAlike terms (CC BY-SA / CC BY-NC-SA) impose conditions on redistributing
  derivatives. Redistribution rights bear directly on the Dataset Strategy's
  long-term-availability and integrity-verification requirements.
- **Derivative work.** ShareAlike licenses require derivatives to carry compatible
  terms; NonCommercial licenses forbid commercial derivatives. Any Kalibra artifact
  derived from such data inherits these obligations.

**Explicit uncertainties to resolve before selection:**

- **VisA** — CC BY 4.0 vs CC BY-NC-SA 4.0 disagreement across sources; unresolved.
- **MPDD** — a LICENSE file exists but its type was not confirmed here.
- **Magnetic Tile** — no explicit license located.
- **NEU** — no explicit license located; "research use" implied but unstated.
- **DAGM** — CC BY 4.0 reported on mirrors; original competition terms unconfirmed.

Where a license is unknown or contradictory, the dataset **must not** be treated as
usable until the term is confirmed against the original source and recorded.

---

## 7. Scientific Risks

The following risks apply to using public inspection benchmarks as Kalibra evidence.
Each mirrors a concern in the Dataset Strategy and Evaluation Strategy.

- **Benchmark overfitting.** Heavily used benchmarks (notably MVTec AD) are saturated;
  strong numbers on them may reflect community tuning rather than genuine capability,
  and can flatter a method that would not generalize.
- **Synthetic bias.** Synthetic data (DAGM; synthetic defects generally) cannot carry
  a real-world inspection claim on its own and may encode generation artifacts a
  method learns instead of real defect structure.
- **Narrow industrial domains.** Most datasets cover one narrow setting (commutators,
  magnetic tiles, steel strip). Evidence on one narrow domain does not transfer to
  Kalibra's cast-aluminium/machined target without a domain-shift caveat.
- **Annotation quality.** Annotation processes, reviewer agreement, and treatment of
  ambiguity are often under-documented; weak ground truth caps the claims it can
  support.
- **Hidden correlations.** Curated benchmarks can contain spurious cues (backgrounds,
  capture artifacts, lighting quirks) correlated with labels, letting a method appear
  to separate classes for the wrong reason.
- **Domain shift.** Systematic differences between any surveyed dataset's setting and
  Kalibra's deployment target are expected; no cross-domain generalization may be
  claimed from a single-domain dataset.
- **Publication bias.** Datasets and reported results are shaped by what gets
  published; apparent consensus in the literature can overstate how solved a problem
  is and understate failure modes.

These risks are reasons to constrain claims, per the governance documents — not
reasons to avoid public data, but reasons to use it with disclosed limits.

---

## 8. Gap Analysis

Read against Kalibra's target domain (§2), the public landscape has clear gaps:

- **Cast aluminium.** No surveyed 2D photographic benchmark is dedicated to
  cast-aluminium surface/subsurface defects; the closest is X-ray casting data
  (GDXray, *observation*) in a different modality. This is the sharpest gap for
  Kalibra.
- **CNC machining.** No surveyed dataset targets machined-component finishing defects
  (tool marks, chatter, burrs) specifically; MPDD (metal parts) is the nearest neighbor
  but is not machining-specific.
- **Gearbox housings / complex geometries.** No surveyed dataset covers complex cast or
  machined housings with realistic geometry-driven inspection challenges.
- **Multi-camera inspection.** Most datasets are single-view; multi-camera or
  multi-view industrial capture (relevant to real inspection stations) is largely
  absent (Real-IAD, *observation*, is a partial exception).
- **Industrial production variability.** Few datasets capture the full lighting,
  camera, and part-to-part variation of a live line as an explicit, graded axis; DAGM
  varies synthetically, MVTec AD 2 adds harder conditions, but honest production
  variability remains thin.

**Relation to Kalibra's long-term goals.** These gaps mean that a first-selected
public dataset will, at best, be a **relevant proxy** for Kalibra's true target, not
a match — and every claim drawn from it inherits a domain-shift caveat toward cast
aluminium and machining. The gaps also indicate where Kalibra may eventually need its
own governed, versioned data to make direct claims about its actual domain, consistent
with the Dataset Strategy's "evolution as extension, not starting point."

---

## 9. Preliminary Observations

Stated neutrally, and recommending **no dataset**:

- The public industrial-inspection landscape is **anomaly-detection-mature but
  domain-narrow**: strong benchmarks exist for the sound-vs-defective framing, but few
  sit close to cast aluminium or machined components.
- **Localization support is real but uneven** — pixel masks in several datasets, weak
  or absent labels in others — so localization claims will be dataset-dependent.
- **Licensing is the dominant unresolved variable.** The most scientifically
  attractive datasets carry non-commercial terms (MVTec, Kolektor), and several
  otherwise-relevant datasets (VisA, MPDD, Magnetic Tile, NEU, DAGM) have
  unconfirmed or contradictory terms that block use until resolved.
- **Benchmark saturation and narrow domains** mean strong published numbers cannot be
  imported as Kalibra evidence; they inform expectations, not claims.
- **MPDD is the closest domain match** on the metal-parts axis, but its license is
  unconfirmed — illustrating that scientific relevance and governance readiness do not
  coincide in any single candidate here.

No candidate is both clearly relevant to Kalibra's target domain **and** clearly clear
on licensing **and** free of saturation/narrowness concerns. That tension is the
central finding, and it is exactly what the Dataset Selection ADR must weigh.

---

## 10. Open Questions

These must be answered before dataset selection:

- **First industrial domain.** Which domain does the first dataset represent — a
  relevant proxy (e.g. metal parts, surface inspection) or a search for something
  nearer cast aluminium/machining?
- **Anomaly taxonomy.** Which defect kinds must the first dataset contain to be
  meaningful for Kalibra's intended inspection?
- **Localization requirements.** Is pixel-level localization ground truth required for
  the first selection, or is image-level detection sufficient for the initial claims?
- **Commercial posture.** Is Kalibra's intended use non-commercial, commercial, or
  undetermined? This decides whether non-commercial datasets (MVTec, Kolektor) are
  even admissible.
- **Redistribution and availability.** Can Kalibra meet its integrity-verification and
  long-term-availability obligations under the candidate's license (a problem for
  competition-gated data)?
- **Target hardware.** What offline hardware baseline must inference and reproducible
  replay run on, and does the dataset's scale/modality fit it?
- **Future scalability.** Will the first dataset be a stepping stone toward Kalibra's
  own governed data for its true domain, and how should that path be kept open?

Until these are settled, no dataset can be responsibly selected.

---

## 11. Next Planning Artifact

Recommended next planning artifact:

```text
docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md
```

The Dataset Selection ADR should choose the **first** dataset — and only after this
landscape has been **reviewed and approved**. The ordering matters: selecting before
the field, its licensing uncertainties, its scientific risks, and its domain gaps are
on the record would repeat the mistake this survey exists to prevent. The ADR should
answer the open questions of §10, resolve the licensing uncertainties of §6 against
original sources, apply the Dataset Strategy approval criteria to the chosen
candidate, and record the decision and its trade-offs — after which the dataset must
still pass the Implementation Authorization gate before any framework-backed work
begins.

---

## Closing Statement

This document surveys the public industrial-inspection dataset landscape to inform a
future Dataset Selection ADR. It selects no dataset, recommends none, and authorizes
no acquisition. It records what could be verified from official sources, marks
everything else as observation, and flags every licensing uncertainty rather than
assuming permission.

The landscape is rich for anomaly detection but narrow for Kalibra's cast-aluminium
and machined-component target, uneven in localization, and dominated by licensing and
saturation questions that no single candidate resolves cleanly. Consistent with ML
Phase 2 governance, the survey preserves the provider abstraction and every domain
ownership by touching none of them, makes no benchmark claim, and leaves selection to
an approved ADR built on verified provenance and licensing — never on convenience.
