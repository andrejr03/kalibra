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
DEFER DATASET SELECTION.
No dataset selected. No dataset acquired. No implementation authorized.
```

**Revision note (MPDD governance revision).** This revision incorporates the verified
findings of the
[`MPDD Licensing & Governance Investigation`](research/KALIBRA_MPDD_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md)
and records the repository owner's current project posture. Two facts change; the
**decision does not**. (1) MPDD's license is now **verified CC BY-NC-SA 4.0**,
replacing the earlier "license type unconfirmed." (2) The project's commercial posture
is recorded below. Neither fact makes any candidate governance-complete, so the ADR
decision remains **DEFER DATASET SELECTION**, and MPDD remains **Deferred**.

**Revision note (VisA governance update).** This revision also incorporates the
verified findings of the
[`VisA Licensing & Governance Investigation`](research/KALIBRA_VISA_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md).
VisA's dataset license is now verified as **CC BY 4.0**, and the repository utility
code is verified as **Apache-2.0**. Official sources agree; the earlier CC BY-NC-SA
statement came from a secondary tooling source and is not authoritative. Licensing is
therefore **no longer a VisA governance blocker**. The decision still does **not**
change, because VisA remains incomplete on non-licensing governance evidence
(versioning, integrity, reproducibility, long-term availability, and annotation-process
documentation), and it is not a domain match for Kalibra's target parts.

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
- **Industrial Dataset Landscape** — surveyed the public candidates, verified
  maintainers/sources/licensing where possible, and recorded that **no candidate is
  simultaneously clearly relevant to Kalibra's domain, clearly licensed, and free of
  saturation/narrowness concerns.**
- **Focused governance investigations** — subsequently resolved the MPDD and VisA
  license records without completing either candidate's full governance evidence.

**Why dataset selection is now possible.** The requirements and the field are both on
the record: the Dataset Strategy fixed *what a dataset must provide*, and the
Landscape fixed *what each candidate verifiably is*. With both in hand, a defensible
decision — to select, or to defer with reasons — can finally be taken. "Possible to
decide" does not mean "obliged to select": deferral with justification is a valid ADR
outcome and, on the verified evidence, the correct one (§6).

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
or whose long-term availability is constrained, **cannot** be selected — however
strong its science — until the gate is cleared against the original source.

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
- **Governance readiness.** **Incomplete.** Licensing is **Satisfied**. Provenance,
  ownership, versioning, integrity, reproducibility, and long-term availability are
  **Partially satisfied**: official authorship, AWS hosting, a dated S3 archive, and
  split files improve governance, but no DOI/release tag/formal version, published
  strong checksum, full annotation-process record, or archival preservation guarantee
  completes the Dataset Strategy gate.
- **Suitability for Kalibra.** *(Observation.)* Attractive scale, anomaly-detection
  structure, and annotation depth; useful as a governed proxy, not a cast-aluminium or
  machined-component domain match.
- **Decision:** `Deferred` — licensing is resolved, but governance remains incomplete
  and the dataset is still domain-distant from Kalibra's target parts. Not selected.

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
  by the four non-licensing governance blockers above. Not selected. It remains a
  domain-relevant candidate to mature toward governance readiness.

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

**Assessment summary.** Selected: **none.** Deferred: **MVTec AD, MVTec AD 2, VisA,
BTAD, MPDD, KolektorSDD, KolektorSDD2, Magnetic Tile, Severstal.** Rejected (for first
selection): **DAGM 2007, NEU.**

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
  (CC BY 4.0 for the dataset; Apache-2.0 for utility code) and stronger public-hosting
  evidence than MPDD, but it is also domain-distant and still incomplete on versioning,
  integrity, annotation-process documentation, and archival preservation. MVTec and
  Kolektor have verified non-commercial licenses compatible with the recorded posture
  and comparatively mature institutional source records, but they are also proxies for
  Kalibra's target domain. Governance *completeness* and domain match still do not
  coincide in any single candidate.
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

The comparison shows a field where **no candidate is both governance-complete on
verified facts and a match for Kalibra's domain.** VisA's licensing evidence has
materially improved and is now the strongest verified licensing position. MPDD's
evidence has also materially improved and remains the closest scientific/domain match.
Neither is governance-complete: VisA is held by non-license governance gaps and domain
distance, while MPDD is held by versioning, integrity, archival availability, and
source-level documentation gaps.

---

## 6. ADR Decision

```text
DECISION: DEFER DATASET SELECTION.
```

**Exactly one outcome is recorded: dataset selection is deferred.** No dataset is
selected.

**Why selection is deferred (and not made):**

- **The best domain match is not yet governance-complete.** MPDD's license is now
  **verified CC BY-NC-SA 4.0** and **compatible** with the recorded non-commercial
  posture, so licensing no longer blocks it. But it remains held by **non-licensing
  governance gaps** — no official version identifier/DOI, no integrity hashes, fragile
  (personal-SharePoint) hosting rather than archival availability, and no source-level
  documentation of composition and annotation. The Dataset Strategy requires
  versioning, integrity verification, and long-term availability, none of which is yet
  established for MPDD.
- **The strongest verified licensing position is not yet governance-complete.** VisA
  is now verified CC BY 4.0 for the dataset and Apache-2.0 for repository utility
  code; official sources agree, and licensing no longer blocks it. But VisA still
  lacks a formal dataset version/DOI/release tag, a published strong checksum, complete
  annotation-process documentation, and an archival preservation guarantee, and it is a
  domain proxy rather than a metal-component match.
- **Other mature-license candidates remain domain-distant proxies.** MVTec AD/AD 2
  and KSDD/KSDD2 are compatible under the non-commercial posture and have clear source
  records, but they are not closer to Kalibra's target parts than MPDD; selecting one
  only because its governance is tidier would still import a domain-shift caveat.
- **Some candidates still have unresolved terms.** BTAD/DAGM/NEU remain unconfirmed,
  Magnetic Tile remains absent-license, and Severstal remains competition-gated.
- **Scientific conservatism forbids selecting on convenience.** Selecting before the
  closest match is governance-complete — or defaulting to a saturated benchmark to make
  progress — would import exactly the risks the governance sequence exists to prevent.

Deferral is not inaction: it is the correct, evidence-respecting outcome given that no
candidate is yet **governance-complete** on verified facts. The resolution of MPDD's
license, the project's posture, and VisA's earlier licensing uncertainty all narrow
the gap without closing it. The path from deferral to selection is defined in §9 and
§11.

---

## 7. Consequences

- **Implementation.** Unchanged and still blocked. The Implementation Authorization
  gate requires an approved dataset; with selection deferred, that precondition remains
  unmet and its status stays **Deferred**.
- **Documentation.** This ADR becomes the record of the first dataset decision. It does
  not modify the Dataset Strategy, Evaluation Strategy, or Implementation
  Authorization; it applies them. Resolving a candidate's gating item will require a
  superseding ADR version (§10) that records a selection.
- **MPDD licensing (resolved).** Licensing type is **no longer an unresolved issue for
  MPDD**: it is verified CC BY-NC-SA 4.0 and compatible with the recorded
  non-commercial posture. This is recorded as fact, not as a selection.
- **VisA licensing (resolved).** Licensing type is **no longer an unresolved issue for
  VisA**: official sources verify CC BY 4.0 for the dataset and Apache-2.0 for the
  repository utility code. The previous CC BY-NC-SA statement is recorded as a
  secondary-source error, not a continuing conflict.
- **Governance evidence (still incomplete).** MPDD's remaining governance evidence —
  versioning/DOI, integrity hashes, archival availability, and source-level
  composition/annotation documentation — is **not** yet established. VisA's remaining
  governance evidence — formal versioning/DOI/release, a published strong checksum,
  complete annotation-process documentation, and archival preservation guarantee — is
  also **not** yet established. No candidate is governance-complete.
- **Net effect on this ADR.** Because governance evidence remains incomplete, the
  **Dataset Selection ADR remains deferred**; the MPDD and VisA findings advance the
  record but do not change the decision.
- **Framework choice.** Unchanged. The Framework ADR remains in "defer selection"
  status; framework fit still cannot be finalized without an approved dataset, so
  deferral here keeps the runtime decision correctly open.
- **Evaluation.** Concrete metrics remain deferred, as the Evaluation Strategy fixed
  them to the approved dataset; no metric may be chosen while no dataset is selected.
- **Future datasets.** The verification and governance discipline applied here sets the
  standard for every future candidate, including industrial-partner or Kalibra-owned
  data; the Landscape's identified gaps (cast aluminium, CNC machining, multi-camera)
  remain the direction of travel.

---

## 8. Risks

- **Benchmark bias.** Selecting a saturated benchmark (e.g. MVTec AD) later could
  produce numbers that reflect community tuning rather than capability; any future
  selection must carry this caveat.
- **Licensing uncertainty.** Reduced but not eliminated. It is **resolved** for VisA
  (verified dataset CC BY 4.0; utility code Apache-2.0), MPDD (verified CC BY-NC-SA
  4.0), MVTec, and Kolektor. MPDD, MVTec, and Kolektor remain admissible only under
  the recorded non-commercial posture; any future shift to a commercial posture would
  re-open their admissibility. Licensing uncertainty **remains** for BTAD, DAGM, NEU,
  Magnetic Tile, and Severstal, where proceeding on an unverified, absent, or
  competition-gated term would breach the Dataset Strategy.
- **Domain mismatch.** Every verified-license candidate is a proxy for, not a match to,
  Kalibra's cast-aluminium/machining target; any first selection inherits a
  domain-shift caveat that must be disclosed and must bound the claims.
- **Future migration.** A first dataset chosen as a proxy will likely be superseded by
  nearer-domain or Kalibra-owned data; comparability across that migration must be
  protected, per the Dataset Strategy's evolution policy.
- **Scientific claims.** No scientific claim may be made until an approved dataset,
  fixed splits, and reproducible evidence exist; deferral makes explicit that no such
  claim is yet possible.

---

## 9. Approval Conditions

This ADR (recording the **deferral**) is considered approved when:

- The repository owner approves the deferral decision and its reasoning.
- The decision status and the per-candidate assessments are recorded in the project
  record.
- The now-resolved items are recorded: the **project's non-commercial posture**,
  **MPDD's verified CC BY-NC-SA 4.0 license**, and **VisA's verified CC BY 4.0 dataset
  license / Apache-2.0 repository utility-code license**.
- The open items blocking selection — MPDD's **non-licensing governance evidence**
  (versioning/DOI, integrity hashes, archival availability, composition/annotation
  documentation), VisA's **non-licensing governance evidence** (formal versioning/DOI
  or release, strong checksum, annotation-process documentation, archival preservation
  guarantee), and the **licensing confirmations** for BTAD, Magnetic Tile, DAGM, NEU,
  and Severstal — are acknowledged as prerequisites to any future selection.

For a **future selection** to be recorded (via a superseding ADR), all of the
following must hold for the chosen candidate: verified provenance; a verified,
explicit, Kalibra-compatible license; satisfiable governance (versioning, hashing,
lineage, evidence linkage) and long-term availability; adequate anomaly-detection and
(where claimed) localization ground truth; and conformance to the Dataset Strategy
approval criteria. Selection remains subject to the Implementation Authorization gate
before any framework-backed work begins.

---

## 10. Future Review

This revision records two material improvements: **VisA governance evidence has
materially improved** through verified licensing and AWS-hosted provenance evidence,
and **MPDD governance evidence has materially improved** through verified licensing
and a completed versioning/archival investigation. Neither improvement completes the
Dataset Strategy gate.

This ADR should be revisited only when one of the following occurs:

- **MPDD governance blockers are resolved.** MPDD's outstanding non-licensing evidence
  is established — an official version identifier/DOI or equivalent fixed release,
  integrity hashes, archival availability, and source-level composition/annotation
  documentation — at which point the closest domain match could be reassessed against
  the Dataset Strategy gate.
- **A candidate materially exceeds both current anchors.** A new public, partner, or
  Kalibra-owned candidate provides verified governance evidence that materially exceeds
  VisA's licensing/hosting maturity **and** scientific/domain relevance that materially
  exceeds MPDD's present domain fit.

Any such event triggers a superseding ADR version; this v1.0 deferral remains the
record until then.

---

## 11. Final Recommendation

```text
DEFER DATASET SELECTION.
```

The evidence is insufficient to select a first dataset: **no candidate is yet
governance-complete on verified facts** — the closest domain match (MPDD) now has a
verified, compatible license but still lacks versioning, integrity verification,
archival availability, and source-level documentation; the strongest verified
licensing candidate (VisA) now has a permissive, official CC BY 4.0 dataset license
but still lacks complete non-license governance evidence and remains domain-distant.
The project's commercial posture is now **recorded (non-commercial)**, resolving that
open question without, by itself, completing any candidate's governance.

**Why no competing candidate was selected:**

- **MPDD** — closest domain match; license now **verified CC BY-NC-SA 4.0** and
  compatible with the non-commercial posture, but held by non-licensing governance gaps
  (versioning/DOI, integrity hashes, archival availability, composition/annotation
  documentation). *Deferred.*
- **VisA** — strongest verified licensing position (**CC BY 4.0** dataset;
  **Apache-2.0** repository utility code) and canonical AWS Open Data/S3 distribution,
  but governance remains incomplete on formal versioning/DOI or release, published
  strong checksum, annotation-process documentation, and archival preservation; also a
  proxy rather than Kalibra's metal-component domain. *Deferred.*
- **MVTec AD, MVTec AD 2, KolektorSDD, KolektorSDD2** — verified **non-commercial**
  licenses, now compatible with the recorded posture; domain-distant proxies and (for
  MVTec AD) saturated, so not the closest match for a first selection. *Deferred.*
- **BTAD** — license/provenance at observation level, unverified; small. *Deferred.*
- **Magnetic Tile** — **no license located**. *Deferred (→ Rejected if none exists).*
- **Severstal** — **competition-rule licensing** conflicts with redistribution and
  long-term-availability governance. *Deferred (→ Rejected if unsatisfiable).*
- **DAGM 2007** — **synthetic**; cannot carry a real-world detection claim as the first
  evidence base; weak localization. *Rejected for first selection.*
- **NEU** — primarily **classification**, outside ML Phase 2 scope; localization
  insufficient. *Rejected for first selection.*

The recommendation preserves the provider abstraction and every domain ownership
(Inspection, Trust, Review, Evidence, Evaluation) by touching none of them, makes no
benchmark claim, and holds implementation blocked. Selection may be recorded only by a
superseding ADR once a candidate clears the governance gate on verified facts under
§9.
