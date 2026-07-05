# Kalibra ML Phase 2 — Dataset Selection ADR v1.0

## About This Document

This Architecture Decision Record records the **first dataset decision** for
Kalibra ML Phase 2. It governs **dataset selection only**. It writes no code,
acquires no data, selects no framework, and **does not authorize implementation.**

It applies the approved governance requirements to the candidates surveyed in the
Industrial Dataset Landscape, justifies the outcome for **every serious candidate**,
and records a single ADR decision (§6).

Throughout, **must**, **must not**, **owns**, and **does not own** carry the binding
sense established across the ML Phase 2 documents
([`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md`](KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md)).

**Verification convention (inherited from the Landscape survey).** A **Verified**
statement is confirmed against an official/primary source; an **Observation** is an
inference or secondary-source report that is **not** treated as fact. Consistent with
the requirement to use only verified facts for decisions, **no decision in this ADR
rests on an unverified permission or an assumed license.**

**Decision status.**

```text
SELECTED — VisA.
Selected as the governed proxy dataset for the first Kalibra ML baseline.
MPDD remains the domain anchor for future domain-specific evolution.
No dataset acquired. No implementation authorized.
```

**Revision note (MPDD governance revision).** This revision incorporates the verified
findings of the
[`MPDD Licensing & Governance Investigation`](research/KALIBRA_MPDD_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md)
and records the repository owner's current project posture. Two facts change; the
original deferral record was narrowed. (1) MPDD's license is now **verified
CC BY-NC-SA 4.0**,
replacing the earlier "license type unconfirmed." (2) The project's commercial posture
is recorded below. Neither fact selected MPDD for the first governed baseline. MPDD
remains the **domain anchor** and is retained for future domain-specific evolution.

**Revision note (VisA governance update).** This revision also incorporates the
verified findings of the
[`VisA Licensing & Governance Investigation`](research/KALIBRA_VISA_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md).
VisA's dataset license is now verified as **CC BY 4.0**, and the repository utility
code is verified as **Apache-2.0**. Official sources agree; the earlier CC BY-NC-SA
statement came from a secondary tooling source and is not authoritative. Licensing is
therefore **no longer a VisA governance blocker**.

**Revision note (C-1 Dataset Selection Closure).** This revision incorporates the
recorded C-1 Dataset Selection Closure checkpoint. PaDiM is now the selected first
model family, and its image-alignment preference favours VisA over MPDD for the first
ML baseline. VisA is selected as a **governed proxy dataset**, not as Kalibra's final
production domain and not as a domain-of-record dataset. The remaining VisA
governance gaps are mostly self-closable by Kalibra's governed acquisition
(Kalibra-side hashes, provenance manifest, acquisition record, and split manifest).
Dataset acquisition is still incomplete, and this ADR authorizes no implementation,
model training, evaluation result, benchmark claim, or product claim.

**Project commercial posture (recorded).**

```text
Research / Portfolio — Non-commercial.
```

The repository owner records the current project as **research / portfolio,
non-commercial**. This **resolves the previously open question** of whether a
non-commercial license is inherently incompatible with the project: for the current
non-commercial posture, a **CC BY-NC-SA 4.0 (non-commercial) license is compatible**,
and non-commercial terms are therefore **no longer a licensing blocker** for the
current project. This record is **scoped to the present non-commercial posture only**;
it is **not** a commercial authorization, and it does **not** license any commercial
use. Should the posture ever change to commercial, non-commercial datasets would again
become inadmissible for any future selection or implementation authorization.
ShareAlike and attribution obligations continue to apply regardless of posture.

---

## 1. Purpose

This ADR records the first dataset decision for ML Phase 2: whether to **select** a
first industrial dataset now, or to **defer** that selection with reasons. It exists
because the Dataset Strategy and the Landscape survey deferred the concrete choice to
a dedicated ADR, and this is that ADR.

Its scope is deliberately narrow. It governs **dataset selection only**. It does not
authorize implementation, does not select or update the runtime framework, and does
not fix metrics — those remain governed by their own documents and by the
Implementation Authorization gate. A dataset decision here, even a selection, grants
no permission to begin framework-backed work.

---

## 2. Decision Context

Dataset selection is considered against the completed ML Phase 2 planning sequence:

- **Scientific Architecture Plan** — fixed the scientific direction: anomaly detection
  first, bounded localization second, offline and reproducible, no scientific claim
  without evidence.
- **Framework ADR** — defined runtime-evaluation criteria, selected no framework, and
  named dataset strategy as a prerequisite to framework fit.
- **Dataset Strategy** — fixed the evidence requirements any dataset must satisfy:
  provenance, licensing, ownership, traceability, reproducibility, versioning,
  integrity verification, long-term availability, honest content and ground truth,
  leak-free frozen splits, bounded synthetic-data policy, governance, and
  scientific-risk reasoning.
- **Evaluation Strategy** — fixed the standard of proof and deferred concrete metrics
  to the approved dataset.
- **Implementation Authorization** — fixed the final governance gate; its status is
  Deferred, and it requires an approved dataset as one precondition.
- **Scientific Model Family Selection Checkpoint** — selected **PaDiM** as the first
  model family, adding an image-alignment criterion relevant to VisA and MPDD.
- **C-1 Dataset Selection Closure Checkpoint** — closed the dataset-selection decision
  by selecting **VisA** as the governed proxy dataset for the first Kalibra ML baseline
  and retaining **MPDD** as the domain anchor.
- **Industrial Dataset Landscape** — surveyed the public candidates, verified
  maintainers/sources/licensing where possible, and recorded that **no candidate is
  simultaneously clearly relevant to Kalibra's domain, clearly licensed, and free of
  saturation/narrowness concerns.**
- **Focused governance investigations** — subsequently resolved the MPDD and VisA
  license records without completing either candidate's full governance evidence.

**Why dataset selection is now closed.** The requirements, candidate field, focused
governance investigations, first model-family decision, and C-1 closure checkpoint are
all now on the record. The Data Strategy Decision Memo named the explicit acceptance
required for selecting VisA as a governed proxy; the C-1 checkpoint records that
acceptance. This ADR therefore moves the repository dataset-selection state from
`DEFER` to `SELECTED — VisA`, while keeping acquisition, implementation, metrics,
training, evaluation, and claims governed by their own downstream gates.

---

## 3. Decision Criteria

Candidates are assessed against the approved governance requirements. Consistent with
the objective, **no numerical score or ranking is used**; these are qualitative
gates, and a failure on a load-bearing governance gate (licensing, provenance,
reproducibility) is disqualifying regardless of scientific appeal.

- **Scientific suitability** — supports honest demonstration including failure, per the
  Evaluation Strategy.
- **Anomaly-detection suitability** — supports sound-vs-defective separation with a
  faithful sound population (the primary sub-problem).
- **Localization support** — trustworthy defect-location ground truth for the bounded
  secondary objective, where claimed.
- **Industrial relevance** — closeness to Kalibra's target domain (precision
  components, cast aluminium, machining).
- **Reproducibility** — can be fixed into a stable, versioned, integrity-verifiable
  form and regenerated by an untrusting observer.
- **Provenance** — origin known and recorded.
- **Licensing** — terms known, explicit, and compatible with Kalibra's intended use;
  unclear terms are a reason to decline.
- **Governance readiness** — versioning, hashing, metadata, lineage, and evidence
  linkage achievable under the license and hosting.
- **Long-term maintainability** — durable availability for as long as a claim stands.
- **Architecture compatibility** — consumable behind the provider seam without moving
  any domain ownership.

**Governance gate.** Licensing, provenance, and long-term availability are treated as
**gating**: a candidate whose license is unconfirmed, contradictory, or incompatible,
or whose long-term availability cannot be governed in a durable local record, **cannot
be used** — however strong its science — until the gate is cleared or consciously
bounded. A bounded governed-proxy selection may be recorded only when remaining gaps
are explicit, claim-limiting, and closable before execution by the governed-acquisition
record.

---

## 4. Candidate Assessment

Each candidate is assessed on verified facts, with observations marked. Per-candidate
decisions use **Selected / Deferred / Rejected**, where **Deferred** means "eligible
in principle but blocked by an unresolved gating item" and **Rejected** means "unfit
for the first ML Phase 2 selection on its verified merits."

### 4.1 MVTec AD

- **Verified strengths.** MVTec Software GmbH maintainer; official source; 15
  object/texture categories; pixel-precise anomaly annotations; de facto standard
  anomaly-detection benchmark with clean sound-training structure.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; not specific to
  cast aluminium or machined parts.
- **Unresolved risks.** *(Observation.)* Heavy benchmark saturation → overfitting risk;
  possible hidden correlations in a curated benchmark.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High on versioning/provenance; non-commercial license now
  **compatible** with the recorded non-commercial posture, so licensing no longer
  gates it.
- **Suitability for Kalibra.** *(Observation.)* Strong scientific reference; domain is
  a proxy, not a match; heavy saturation is the main concern.
- **Decision:** `Deferred` — licensing no longer a blocker, but domain is a proxy and
  benchmark saturation weighs against it as a *first* selection; not the closest domain
  match.

### 4.2 MVTec AD 2

- **Verified strengths.** MVTec maintainer; official source; harder/advanced scenarios
  including lighting variation that speaks to Kalibra's diversity requirements; recent.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; not domain-specific.
- **Unresolved risks.** *(Observation.)* Newer → less settled tooling and comparison;
  full category/localization details to confirm at source.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High; non-commercial license now **compatible** with the
  recorded non-commercial posture, so licensing no longer gates it.
- **Suitability for Kalibra.** *(Observation.)* Scientifically attractive for harder
  conditions; domain a proxy, not a match.
- **Decision:** `Deferred` — licensing no longer a blocker, but domain-distant and
  newer/less-settled; not the closest domain match.

### 4.3 VisA

- **Verified strengths.** Amazon Science maintainer; official source; 12 classes across
  3 domains; large; image- **and** pixel-level annotations; canonical AWS S3 archive
  recorded in the AWS Open Data registry; official repository, AWS registry, AWS
  Marketplace listing, and repository notice agree on the dataset license.
- **Verified weaknesses.** Not specific to Kalibra's parts; the official paper states
  that defects were manually generated to produce realistic anomalies; no formal
  dataset version/DOI/release tag or official strong checksum was located.
- **Unresolved risks.** *(Observation grounded in verified absence.)* Annotation
  process, reviewer agreement, ambiguity handling, and quality-control procedure are
  not fully documented at source; archival preservation guarantee is not established.
- **Licensing status.** **Verified CC BY 4.0 for the dataset** and **Apache-2.0 for
  repository utility code**. Official sources agree. The earlier CC BY-NC-SA statement
  came from a secondary tooling source and is not authoritative. Commercial use,
  redistribution, derivative works, and attribution obligations are resolved from the
  official license record. **Licensing is no longer a VisA blocker.**
- **Governance readiness.** **Selected with governed-acquisition obligations.**
  Licensing is **Satisfied**. Provenance, ownership, versioning, integrity,
  reproducibility, and long-term availability are **Partially satisfied** before local
  acquisition: official authorship, AWS hosting, a dated S3 archive, and split files
  improve governance, but no DOI/release tag/formal version, published strong
  checksum, full annotation-process record, or archival preservation guarantee
  completes the record at source. The C-1 checkpoint records that the remaining
  practical gaps are mostly self-closable by Kalibra's governed acquisition through
  Kalibra-side hashing, provenance manifest, acquisition record, and split manifest.
- **Suitability for Kalibra.** *(Observation.)* Attractive scale, anomaly-detection
  structure, image and pixel labels, and image alignment; useful as a governed proxy,
  not a cast-aluminium or machined-component domain match.
- **Decision:** `Selected` — selected as the **governed proxy dataset** and
  **governance anchor** for the first Kalibra ML baseline. Selection does not mean
  acquisition is complete, and it authorizes no implementation, training, evaluation,
  benchmark, production, or domain-of-record claim.

### 4.4 BTAD (BeanTech)

- **Verified strengths.** Real industrial capture; 3 products with body and surface
  defects.
- **Verified weaknesses.** Small (≈2,830 images); only 3 products.
- **Unresolved risks.** Canonical source and exact license reported (CC BY-SA 4.0) but
  **observation-level**, not confirmed here; maintainer/hosting to confirm.
- **Licensing status.** **Observation** (CC BY-SA 4.0 reported) — unverified.
- **Governance readiness.** Provenance/license need confirmation before governance can
  be completed.
- **Suitability for Kalibra.** *(Observation.)* Real-industrial character is relevant;
  scale and provenance clarity are open.
- **Decision:** `Deferred` — pending verified provenance and license.

### 4.5 MPDD

*(Revised per the MPDD Licensing & Governance Investigation.)*

- **Verified strengths.** **Closest surveyed domain match** — industrial **metal
  parts**; pixel-precise defect masks (>1000 images, *verified*); train-on-normal /
  validate-on-mixed anomaly-detection structure (*verified*); maintained by named
  authors at Brno University of Technology (VUT); official repository and paper
  (ICUMT 2021). License now **verified**.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial** (compatible with the
  project's current non-commercial posture; ShareAlike/attribution apply); relatively
  small; not cast-aluminium specific.
- **Unresolved risks.** *(Observation.)* Part-category count/names, exact per-class
  counts, and defect taxonomy are **not** stated at the official source (secondary
  sources only); annotation process/agreement undocumented.
- **Licensing status.** **Verified CC BY-NC-SA 4.0** — read from the official
  repository `LICENSE` file. No source contradiction. Non-commercial, ShareAlike,
  attribution required. Compatible with the recorded non-commercial posture;
  **licensing is no longer an MPDD blocker.**
- **Governance readiness.** **Incomplete — remaining blockers are non-licensing.**
  Outstanding: (a) dataset **versioning** / official **version identifier or DOI**;
  (b) **integrity verification** (official hashes/checksums); (c) **long-term archival
  availability** (currently served from a personal VUT SharePoint share, not an
  archival record); (d) **official documentation** of dataset composition and the
  **annotation process**. Provenance/ownership are partially satisfied at dataset
  level.
- **Suitability for Kalibra.** *(Observation.)* On domain and localization grounds the
  most directly relevant candidate, and now with a compatible, verified license;
  scientific suitability is **strong**, but governance readiness is **incomplete**.
- **Decision:** `Deferred` — strongest domain fit and licensing now resolved, but held
  by the four non-licensing governance blockers above and not selected for the first
  governed baseline. MPDD remains the **domain anchor** and is retained for future
  domain-specific evolution.

### 4.6 KolektorSDD

- **Verified strengths.** Genuine production-line provenance (ViCoS Lab + Kolektor
  Group); grayscale; clear official source and license.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; narrow single-component
  domain (commutators); small.
- **Unresolved risks.** *(Observation.)* Localization granularity to confirm.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High on provenance/versioning; non-commercial license now
  **compatible** with the recorded non-commercial posture, so licensing no longer
  gates it.
- **Suitability for Kalibra.** *(Observation.)* Real-industrial provenance relevant;
  domain narrow (commutators).
- **Decision:** `Deferred` — licensing no longer a blocker, but narrow single-component
  domain weighs against it as a first selection.

### 4.7 KolektorSDD2

- **Verified strengths.** Production provenance; color; larger/richer than KSDD; clear
  source and license.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; specific surface-
  inspection setting, not Kalibra's parts.
- **Unresolved risks.** *(Observation.)* Localization/annotation details to confirm.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High; non-commercial license now **compatible** with the
  recorded non-commercial posture, so licensing no longer gates it.
- **Suitability for Kalibra.** *(Observation.)* Stronger real-industrial reference than
  KSDD; still a specific surface-inspection setting, not Kalibra's parts.
- **Decision:** `Deferred` — licensing no longer a blocker, but domain-distant from
  Kalibra's parts; not the closest domain match.

### 4.8 DAGM 2007

- **Verified strengths.** Long-standing, freely mirrored; controlled difficulty;
  named authors and institutional host (Heidelberg HCI).
- **Verified weaknesses.** **Synthetically generated** backgrounds and defects; weak
  (region-level, not pixel-precise) localization; dated.
- **Unresolved risks.** License reported CC BY 4.0 on mirrors; original competition
  terms unconfirmed.
- **Licensing status.** **Observation** — unverified against the original terms.
- **Governance readiness.** Reproducible, but synthetic nature caps its evidentiary
  role.
- **Suitability for Kalibra.** *(Observation.)* Per the Dataset Strategy, a real-world
  inspection claim **must not** rest on synthetic data alone; usable only as a
  controlled/synthetic reference, not as the first real-world evidence base.
- **Decision:** `Rejected` (for first ML Phase 2 selection) — synthetic data cannot
  carry the real-world detection claim this selection is meant to enable; weak
  localization compounds the unfitness.

### 4.9 Magnetic Tile Defect

- **Verified strengths.** Real surface defects with masks; named authors; captures real
  lighting variation; ≈1,344 images across 5 defect types plus defect-free.
- **Verified weaknesses.** Small; narrow single-component domain.
- **Unresolved risks.** **No explicit license located** — a blocking gap.
- **Licensing status.** **Unresolved / absent** — no license confirmed.
- **Governance readiness.** Cannot be completed without a confirmed license; single-
  repository hosting raises long-term-availability risk.
- **Suitability for Kalibra.** *(Observation.)* Relevant defect character, but the
  absent license is a blocking open item.
- **Decision:** `Deferred` — blocked by absent license confirmation; if no license can
  be established, this moves to Rejected.

### 4.10 NEU Surface Defect Database

- **Verified strengths.** Well known; clean 6-class structure; real hot-rolled steel-
  strip defects; named maintainer/host.
- **Verified weaknesses.** Primarily a **classification** set (image-level); detection
  variants add only bounding boxes, not pixel masks; 200×200 grayscale.
- **Unresolved risks.** No explicit license located; research use implied but unstated.
- **Licensing status.** **Unresolved** — research use implied, not confirmed.
- **Governance readiness.** Limited by weak localization and unconfirmed terms.
- **Suitability for Kalibra.** *(Observation.)* Classification is out of ML Phase 2
  scope (Scientific Architecture Plan §4); weak localization; poor fit to
  anomaly-detection-first with localization.
- **Decision:** `Rejected` (for first ML Phase 2 selection) — its primary framing
  (classification) sits outside the approved scope, and its localization support is
  insufficient for the bounded secondary objective.

### 4.11 Severstal Steel Defect Detection

- **Verified strengths.** Large, real, industrially sponsored; pixel-level segmentation
  masks (RLE); official Kaggle source.
- **Verified weaknesses.** Test labels withheld; not Kalibra's parts.
- **Unresolved risks.** Governed by **Kaggle competition rules** requiring rule
  acceptance; competition data generally **not freely redistributable**.
- **Licensing status.** **Observation (high confidence)** that competition-rule
  constraints apply; must be read at source.
- **Governance readiness.** **Conflicts** with the Dataset Strategy's redistribution,
  integrity-verification, and long-term-availability requirements.
- **Suitability for Kalibra.** *(Observation.)* Scientifically rich, but the
  redistribution/availability constraints are a serious governance concern.
- **Decision:** `Deferred` — pending a source reading of the competition terms; if
  redistribution/long-term availability cannot be satisfied, this moves to Rejected on
  governance grounds.

**Assessment summary.** Selected: **VisA** (governed proxy dataset, first ML
baseline, governance anchor). Deferred: **MVTec AD, MVTec AD 2, BTAD, MPDD,
KolektorSDD, KolektorSDD2, Magnetic Tile, Severstal.** MPDD remains the **domain
anchor** and is not rejected. Rejected (for first selection): **DAGM 2007, NEU.**

---

## 5. Comparative Discussion

The principal trade-offs, stated qualitatively and without ranking:

- **Benchmark maturity vs headroom.** The most mature datasets (MVTec AD, DAGM, NEU)
  bring comparability but also saturation or scope mismatch; maturity is not, by
  itself, fitness.
- **Domain relevance vs governance readiness.** The candidate closest to Kalibra's
  domain (MPDD, metal parts) now has a **verified, compatible license** but is held by
  non-licensing governance gaps (versioning, integrity, archival availability,
  source-level documentation). VisA now has the strongest verified licensing position
  (CC BY 4.0 for the dataset; Apache-2.0 for utility code), the strongest long-term
  availability position, stronger public-hosting evidence than MPDD, and remaining
  practical governance gaps that are mostly self-closable by Kalibra's governed
  acquisition. MVTec and Kolektor have verified non-commercial licenses compatible
  with the recorded posture and comparatively mature institutional source records, but
  they are also proxies for Kalibra's target domain. Governance strength and domain
  match still do not coincide in any single candidate.
- **Anomaly detection.** The MVTec line, VisA, BTAD, MPDD, and the Kolektor datasets
  fit the sound-vs-defective framing; NEU (classification) fits it least.
- **Localization.** Pixel/mask ground truth exists in MVTec AD, VisA, MPDD, KSDD/KSDD2,
  Magnetic Tile, and Severstal; DAGM is weak; NEU is bounding-box at best — so any
  localization claim is strongly dataset-dependent.
- **Licensing.** VisA is now verified **CC BY 4.0** for the dataset, with
  **Apache-2.0** repository utility code, making it the clearest and least restrictive
  verified license posture among the serious candidates. MVTec, Kolektor, and MPDD are
  verified **CC BY-NC-SA 4.0** and compatible only under the recorded non-commercial
  posture. BTAD/DAGM/NEU remain unconfirmed, Magnetic Tile has no license located, and
  Severstal remains competition-gated.
- **Reproducibility and availability.** VisA's AWS Open Data registry entry, canonical
  AWS S3 archive, dated filename, and split files materially improve its governance
  maturity, but do not replace a formal version ID, release tag, DOI, strong checksum,
  or preservation guarantee. MVTec and Kolektor retain strong institutional-source
  maturity. MPDD remains weaker on versioning and archival stability because its
  official data distribution is a personal VUT SharePoint share with no DOI or
  published checksum. Competition-gated (Severstal) and single-repository (Magnetic
  Tile) candidates continue to carry availability risk.
- **Scientific evidence.** Real data is required for a real-world claim (excluding
  synthetic DAGM as a primary basis), and strong published benchmark numbers cannot be
  imported as Kalibra evidence — they inform expectations, not claims.

The comparison shows a field where **no candidate is both the final Kalibra domain
match and fully complete at source on every governance dimension.** C-1 therefore
records a bounded selection rather than an expansive claim: **VisA** is selected as
the governed proxy dataset and governance anchor for the first Kalibra ML baseline,
because it combines verified CC BY 4.0 licensing, the strongest long-term availability
position, image and pixel labels, and better PaDiM image-alignment fit. **MPDD**
remains the domain anchor because it is the closest surveyed metal-parts candidate,
but its governance and availability risks remain higher and it is not selected for
the first governed baseline.

---

## 6. ADR Decision

```text
DECISION: SELECTED — VisA.
```

**Exactly one selection outcome is recorded: VisA is selected.** The selection is
bounded: VisA is selected as the **governed proxy dataset** for the first Kalibra ML
baseline, and as the current **governance anchor**. Dataset acquisition is not
complete, and no implementation is authorized.

### 6.1 Selected Dataset

- **Dataset:** VisA.
- **Role:** governed proxy dataset.
- **Baseline:** first Kalibra ML baseline.
- **Governance role:** governance anchor for the first governed baseline.

The selected dataset is not Kalibra's final production domain, and it does not become
the domain of record for Kalibra's long-term industrial inspection claims.

### 6.2 MPDD Status

MPDD remains the **domain anchor**. It is **not selected** for the first governed
baseline, and it is **not rejected**. It is retained for future domain-specific
evolution once its governance and availability risks can be reduced or bounded.

### 6.3 Technical Rationale

- **PaDiM selection favours VisA because of image alignment.** PaDiM is
  position-sensitive; the recorded model-family checkpoint identifies MPDD pose
  variation as a PaDiM degradation risk, while the C-1 closure records VisA as better
  aligned for the first baseline.
- **VisA has the strongest governance position among the active candidates.** Its
  dataset license is verified **CC BY 4.0**, its repository utility code is verified
  **Apache-2.0**, official sources agree, and the canonical AWS-hosted distribution
  gives it the strongest long-term availability position in the surveyed field.
- **VisA supports the needed evidence shape for C-2.** It provides image-level and
  pixel-level labels, allowing the Evaluation Protocol to be fixed for both
  anomaly-detection and bounded localization evidence without claiming results.
- **Remaining VisA governance gaps are mostly self-closable by Kalibra governed
  acquisition.** Kalibra can record a pinned acquisition, local sha256 integrity
  manifest, provenance manifest, immutable split manifest, and attribution record.
  Upstream limitations still remain documented: no DOI/formal release tag, no
  published strong upstream checksum, incomplete annotation-process documentation, and
  no archival preservation guarantee.
- **MPDD governance and availability risks remain higher.** MPDD is the closer domain
  fit, but its official distribution remains weaker for long-term availability,
  versioning, integrity verification, and archival evidence. Those risks are less
  self-closable from Kalibra's side.

### 6.4 Accepted Limitations and Non-Claims

- VisA is a **governed proxy**.
- VisA is **not** the final production domain.
- This ADR authorizes **no domain-of-record claim**.
- This ADR authorizes **no defect-detection claim**.
- This ADR authorizes **no benchmark claim**.
- This ADR authorizes **no product claim**.
- This ADR does **not** claim dataset acquisition is complete.
- This ADR does **not** claim model training, evaluation, calibration, or production
  readiness.

---

## 7. Consequences

- **C-1 Dataset Selection Closure is complete.** The repository dataset-selection
  state moves from `DEFER` to `SELECTED — VisA`.
- **C-2 may proceed.** The repository may proceed to:

```text
C-2 Evaluation Protocol Fixation
```

- **Execution remains dependent on governed acquisition.** C-2 protocol design may use
  the recorded VisA structure, but execution on data requires governed VisA
  acquisition, local integrity evidence, provenance record, and frozen split records.
- **Implementation remains separately gated.** This ADR does not authorize runtime,
  provider, preprocessing, output-mapping, loader, evaluation-harness, model-artifact,
  training, or deployment changes.
- **Framework ADR, Scientific Architecture, Evaluation Strategy, and Implementation
  Authorization remain unmodified.** This ADR applies their governance posture; it
  does not revise them.
- **MPDD remains available for future evolution.** MPDD is retained as the domain
  anchor for later domain-specific work, not rejected.
- **Claim boundaries remain unchanged.** No scientific, benchmark, calibrated
  confidence, production, or product-readiness claim may be made until reproducible
  evidence exists under the appropriate downstream gates.

---

## 8. Risks

- **Proxy-domain risk.** VisA is not a cast-aluminium, CNC-machining, gearbox-housing,
  or metal-parts dataset. Any evidence produced on it will be bounded to a governed
  proxy baseline unless later domain-specific evidence supports stronger claims.
- **Acquisition risk.** Selection is not acquisition. If governed acquisition cannot
  pin the archive, record hashes, preserve provenance, and freeze splits, execution
  must stop and the decision must be revisited.
- **Annotation-process risk.** VisA's upstream annotation-process documentation remains
  incomplete; any localization or label-dependent claim must disclose that limitation.
- **Benchmark and product-claim risk.** VisA selection must not be allowed to imply a
  benchmark result, defect-detection capability, calibrated confidence, or product
  readiness before evaluation evidence exists.
- **Future migration.** The first governed proxy baseline will likely be superseded by
  nearer-domain or Kalibra-owned data; comparability across that migration must be
  protected, per the Dataset Strategy's evolution policy.
- **MPDD maturity risk.** MPDD remains the domain anchor, but its long-term
  availability, versioning, integrity, and archival evidence are still weaker than
  VisA's and must not be glossed over.

---

## 9. Approval Conditions

This ADR (recording the **VisA selection**) is considered approved when:

- The repository owner approves `SELECTED — VisA` as the C-1 Dataset Selection Closure
  outcome.
- The role is recorded precisely: **VisA is the governed proxy dataset** for the first
  Kalibra ML baseline and the current **governance anchor**.
- MPDD is recorded precisely: **MPDD remains the domain anchor**, is not selected for
  the first governed baseline, and is retained for future domain-specific evolution.
- The accepted limitations are recorded: no domain-of-record, defect-detection,
  benchmark, product, acquisition-complete, training, evaluation, calibration, or
  production-readiness claim.
- The governed-acquisition obligations are acknowledged as prerequisites to using the
  dataset: fixed acquisition record, local sha256 integrity manifest, provenance
  manifest, attribution record, and immutable train/validation/test split record.
- The downstream ordering is preserved: C-2 Evaluation Protocol Fixation may proceed,
  but data execution and any scientific claim remain blocked until governed
  acquisition and the appropriate downstream gates are complete.

---

## 10. Future Review

This revision records C-1 Dataset Selection Closure: **VisA is selected as governed
proxy** and **MPDD remains the domain anchor**. Future review must preserve that
distinction unless a later owner-approved ADR changes it.

This ADR should be revisited only when one of the following occurs:

- **Governed VisA acquisition fails.** If Kalibra cannot produce the required local
  acquisition, hash, provenance, attribution, or split records, the selected dataset
  cannot be used and the decision must be revisited.
- **MPDD governance blockers are resolved.** MPDD's outstanding non-licensing evidence
  is established — an official version identifier/DOI or equivalent fixed release,
  integrity hashes, archival availability, and source-level composition/annotation
  documentation — at which point the domain anchor could be reassessed for a future
  domain-specific baseline.
- **A candidate materially exceeds both current anchors.** A new public, partner, or
  Kalibra-owned candidate provides verified governance evidence that materially exceeds
  VisA's licensing/hosting maturity **and** scientific/domain relevance that materially
  exceeds MPDD's present domain fit.
- **A domain-of-record or production claim is proposed.** Such a claim cannot rest on
  the VisA proxy selection and would require a separate governed dataset decision and
  supporting evidence.

Any such event triggers a superseding ADR version. Until then, this ADR records the
bounded `SELECTED — VisA` decision and its non-claims.

---

## 11. Final Recommendation

```text
SELECTED — VisA.
```

VisA is selected as the **governed proxy dataset** and **governance anchor** for the
first Kalibra ML baseline. MPDD remains the **domain anchor**, is not selected for the
first governed baseline, and is retained for future domain-specific evolution.

This decision closes C-1 Dataset Selection Closure and permits the repository to
proceed to **C-2 Evaluation Protocol Fixation**. Execution remains dependent on
governed VisA acquisition. No dataset acquisition, model training, evaluation result,
benchmark, defect-detection capability, calibrated confidence, production readiness,
or product claim is made by this ADR.
