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
- **Governance readiness.** High on versioning/provenance; **gated** by commercial
  posture (Kalibra's intended-use commerciality is an open question).
- **Suitability for Kalibra.** *(Observation.)* Strong scientific reference; domain
  is a proxy, not a match; licensing gate binds.
- **Decision:** `Deferred` — blocked by the unresolved commercial-posture question
  against a verified non-commercial license, plus saturation concerns.

### 4.2 MVTec AD 2

- **Verified strengths.** MVTec maintainer; official source; harder/advanced scenarios
  including lighting variation that speaks to Kalibra's diversity requirements; recent.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; not domain-specific.
- **Unresolved risks.** *(Observation.)* Newer → less settled tooling and comparison;
  full category/localization details to confirm at source.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High; **gated** by commercial posture.
- **Suitability for Kalibra.** *(Observation.)* Scientifically attractive for harder
  conditions; same non-commercial gate.
- **Decision:** `Deferred` — same gating as MVTec AD.

### 4.3 VisA

- **Verified strengths.** Amazon Science maintainer; official source; 12 classes across
  3 domains; large; image- **and** pixel-level annotations.
- **Verified weaknesses.** Not specific to Kalibra's parts.
- **Unresolved risks.** **License discrepancy** across sources (CC BY 4.0 vs
  CC BY-NC-SA 4.0) — unresolved and decision-relevant.
- **Licensing status.** **Unresolved** — must be confirmed against the original source.
- **Governance readiness.** Potentially high **if** the permissive term is confirmed;
  currently **gated** by the licensing contradiction.
- **Suitability for Kalibra.** *(Observation.)* Attractive scale and annotation depth;
  the license question is decisive.
- **Decision:** `Deferred` — cannot select on a contradictory, unverified license.

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

- **Verified strengths.** **Closest surveyed domain match** — industrial **metal
  parts**, 6 part types; pixel-precise defect masks (>1000 images); maintained by named
  authors at Brno University of Technology; official repository.
- **Verified weaknesses.** Relatively small; not cast-aluminium specific.
- **Unresolved risks.** License **file exists but type unconfirmed**; capture
  conditions/defect taxonomy details at observation level.
- **Licensing status.** **Unresolved** — license present but not identified; must be
  verified.
- **Governance readiness.** Promising on domain and localization; **gated** by the
  unconfirmed license.
- **Suitability for Kalibra.** *(Observation.)* On domain grounds the most directly
  relevant candidate; scientific relevance and governance readiness do not yet
  coincide.
- **Decision:** `Deferred` — strongest domain fit, blocked solely by an unconfirmed
  license; a priority to resolve at source.

### 4.6 KolektorSDD

- **Verified strengths.** Genuine production-line provenance (ViCoS Lab + Kolektor
  Group); grayscale; clear official source and license.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; narrow single-component
  domain (commutators); small.
- **Unresolved risks.** *(Observation.)* Localization granularity to confirm.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High on provenance/versioning; **gated** by commercial
  posture.
- **Suitability for Kalibra.** *(Observation.)* Real-industrial provenance relevant;
  domain narrow; licensing gate binds.
- **Decision:** `Deferred` — non-commercial gate plus domain narrowness.

### 4.7 KolektorSDD2

- **Verified strengths.** Production provenance; color; larger/richer than KSDD; clear
  source and license.
- **Verified weaknesses.** CC BY-NC-SA 4.0 — **non-commercial**; specific surface-
  inspection setting, not Kalibra's parts.
- **Unresolved risks.** *(Observation.)* Localization/annotation details to confirm.
- **Licensing status.** **Verified** CC BY-NC-SA 4.0 (non-commercial).
- **Governance readiness.** High; **gated** by commercial posture.
- **Suitability for Kalibra.** *(Observation.)* Stronger real-industrial reference than
  KSDD; same non-commercial gate.
- **Decision:** `Deferred` — non-commercial gate.

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
  domain (MPDD, metal parts) is blocked by an unconfirmed license, while the
  candidates with the clearest licenses (MVTec, Kolektor) are non-commercial and
  domain-distant. Relevance and governance readiness do not coincide in any single
  candidate.
- **Anomaly detection.** The MVTec line, VisA, BTAD, MPDD, and the Kolektor datasets
  fit the sound-vs-defective framing; NEU (classification) fits it least.
- **Localization.** Pixel/mask ground truth exists in MVTec AD, VisA, MPDD, KSDD/KSDD2,
  Magnetic Tile, and Severstal; DAGM is weak; NEU is bounding-box at best — so any
  localization claim is strongly dataset-dependent.
- **Licensing.** The decisive axis: verified non-commercial (MVTec, Kolektor),
  contradictory (VisA), unconfirmed (MPDD, BTAD, DAGM, NEU), absent (Magnetic Tile),
  or competition-gated (Severstal). No candidate offers a verified, unencumbered,
  Kalibra-compatible license today.
- **Reproducibility.** Institutionally hosted datasets (MVTec, ViCoS/Kolektor,
  Heidelberg) are easiest to fix and regenerate; competition-gated (Severstal) and
  single-repository (Magnetic Tile) candidates carry reproducibility and
  availability risk.
- **Scientific evidence.** Real data is required for a real-world claim (excluding
  synthetic DAGM as a primary basis), and strong published benchmark numbers cannot be
  imported as Kalibra evidence — they inform expectations, not claims.

The comparison shows a field where **no candidate clears the governance gate on
verified facts while also matching Kalibra's domain.** That is the crux the decision
must respect.

---

## 6. ADR Decision

```text
DECISION: DEFER DATASET SELECTION.
```

**Exactly one outcome is recorded: dataset selection is deferred.** No dataset is
selected.

**Why selection is deferred (and not made):**

- **No candidate clears the licensing gate on verified facts.** The clearly-licensed
  candidates are verified **non-commercial** (MVTec AD/AD 2, KSDD/KSDD2), which cannot
  be selected while Kalibra's **commercial posture is an open question**; the
  domain-relevant and large candidates (MPDD, VisA, BTAD, Magnetic Tile, DAGM, NEU,
  Severstal) have **unconfirmed, contradictory, absent, or competition-gated**
  licenses. The Dataset Strategy requires known, explicit, compatible terms before
  use; none is established here.
- **The best domain match is blocked, not disqualified.** MPDD is the closest fit but
  its license type is unconfirmed; selecting it now would violate the rule that
  permissions are established, not assumed.
- **A required open question is unanswered.** Kalibra's commercial posture (§10 of the
  Landscape) governs whether the non-commercial datasets are even admissible; it must
  be answered before any of them can be selected.
- **Scientific conservatism forbids selecting on convenience.** Choosing a saturated
  benchmark or an unverified-license dataset to make progress would import exactly the
  risks the governance sequence exists to prevent.

Deferral is not inaction: it is the correct, evidence-respecting outcome given that no
candidate simultaneously satisfies the gating governance criteria on verified facts.
The path from deferral to selection is defined in §9 and §11.

---

## 7. Consequences

- **Implementation.** Unchanged and still blocked. The Implementation Authorization
  gate requires an approved dataset; with selection deferred, that precondition remains
  unmet and its status stays **Deferred**.
- **Documentation.** This ADR becomes the record of the first dataset decision. It does
  not modify the Dataset Strategy, Evaluation Strategy, or Implementation
  Authorization; it applies them. Resolving a candidate's gating item will require a
  superseding ADR version (§10) that records a selection.
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
- **Licensing uncertainty.** The dominant risk: proceeding on an unverified or
  contradictory license would breach the Dataset Strategy and could invalidate any
  claim built on the data. Deferral contains this risk until terms are confirmed at
  source.
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
- The open questions blocking selection — above all **Kalibra's commercial posture**
  and the **licensing confirmations** for MPDD, VisA, BTAD, Magnetic Tile, DAGM, NEU,
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

This ADR should be revisited when any of the following occurs:

- **Licensing clarification.** A gating license is confirmed at source — especially
  **MPDD** (closest domain match), **VisA** (contradiction resolved to a permissive
  term), or a Kolektor/MVTec dataset once commercial posture is settled.
- **Commercial-posture decision.** Kalibra's intended use is fixed as non-commercial,
  commercial, or bounded, changing which datasets are admissible.
- **New industrial datasets.** A newly published dataset materially closes the domain
  gap (cast aluminium, CNC machining, multi-camera) with clear terms.
- **Industrial partner data.** Governed partner data becomes available for Kalibra's
  actual domain.
- **Kalibra-owned datasets.** Kalibra assembles its own versioned, governed data,
  enabling direct-domain claims.
- **ML Phase 3.** A later phase revises scope in a way that changes dataset
  requirements.

Any such event triggers a superseding ADR version; this v1.0 deferral remains the
record until then.

---

## 11. Final Recommendation

```text
DEFER DATASET SELECTION.
```

The evidence is insufficient to select a first dataset: **no candidate clears the
governance gate — verified, explicit, Kalibra-compatible licensing plus satisfiable
provenance, reproducibility, and long-term availability — on verified facts**, and a
required open question (commercial posture) is unanswered.

**Why no competing candidate was selected:**

- **MVTec AD, MVTec AD 2, KolektorSDD, KolektorSDD2** — verified **non-commercial**
  licenses; inadmissible until commercial posture is settled; domain-distant and (for
  MVTec AD) saturated. *Deferred.*
- **VisA** — **contradictory** license across sources; cannot select on an unverified
  term. *Deferred.*
- **MPDD** — closest domain match, but **license type unconfirmed**; permissions must
  be established, not assumed. *Deferred (priority to resolve).*
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
