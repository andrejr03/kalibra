# Kalibra — MPDD Licensing & Governance Investigation v1.0

## 1. Official Sources

- **Official repository.** `https://github.com/stepanje/MPDD` — the authors'
  repository, containing the README, the `LICENSE` file, and the download pointer.
  *(Verified.)* A successor repository `https://github.com/stepanje/MPDD2` ("Metal
  Parts Defect Detection Dataset 2") also exists under the same owner. *(Verified it
  exists; not assessed here.)*
- **Official download.** The dataset is distributed via a **Brno University of
  Technology (VUT) personal SharePoint** link hosted under the account
  `xjezek16_vutbr_cz`, referenced from the official README. *(Verified the README
  points to a VUT SharePoint URL.)* This is an official, institution-hosted pointer —
  but a **personal** SharePoint share, not an archival/DOI record (relevant to §3).
- **Official paper.** Jezek, Jonak, Burget, Dvorak, Skotak, "Deep learning-based defect
  detection of metal parts: evaluating current methods in complex conditions," 13th
  International Congress on Ultra Modern Telecommunications and Control Systems and
  Workshops (**ICUMT 2021**), Brno, Czech Republic, 25–27 Oct 2021, pp. 66–71.
  *(Verified via the README citation and IEEE/ResearchGate records.)*
- **Official maintainers / authors.** Stepan Jezek (`Stepan.Jezek1@vut.cz`) and Radim
  Burget (`burgetrm@vut.cz`) are the contact maintainers; additional named authors are
  Martin Jonak, Pavel Dvorak, and Milos Skotak. *(Verified from the README and paper.)*
- **Hosting institution.** Brno University of Technology (Vysoké učení technické v
  Brně, VUT), Czech Republic — indicated by the `@vut.cz` / `vutbr` author addresses
  and the VUT SharePoint host. *(Verified by domain; a formal institutional
  data-repository record was not located.)*
- **Corresponding authors.** Stepan Jezek and Radim Burget, per the README contacts.
  *(Verified as contacts; "corresponding author" designation in the paper not
  separately confirmed.)*

**Official vs mirror.** The GitHub repository and the VUT SharePoint download are
**official**. Copies on dataset aggregators (e.g. Dataset Ninja), Kaggle mirrors, and
third-party tooling documentation are **mirrors/secondary** and are **not** relied on
for any governance fact here.

---

## 2. Licensing

- **Repository / dataset license.** **CC BY-NC-SA 4.0** — read directly from the
  official repository `LICENSE` file. *(Verified.)* The MPDD README does not restate a
  license inline; the `LICENSE` file is the authoritative license artifact in the
  repository, and it is the standard Creative Commons
  Attribution-NonCommercial-ShareAlike 4.0 International text.
- **Commercial use.** **Restricted.** The license defines NonCommercial as "not
  primarily intended for or directed towards commercial advantage or monetary
  compensation," and permits reproduction and sharing "for NonCommercial purposes
  only." *(Verified from the license text.)*
- **Redistribution.** **Permitted for non-commercial purposes, with conditions.** The
  license allows reproducing and sharing the material "in whole or in part, for
  NonCommercial purposes only." *(Verified.)*
- **Derivative works.** **Permitted for non-commercial purposes under ShareAlike.**
  Adapted material may be produced and shared "for NonCommercial purposes only," and
  must carry "the same License Elements, this version or later, or a BY-NC-SA
  Compatible License." *(Verified.)*
- **Attribution.** **Required.** On sharing, one must retain creator identification, a
  copyright notice, and a notice referring to the public license. *(Verified.)*
- **No-additional-terms.** The license forbids imposing "additional or different terms
  or conditions" that restrict recipients' exercise of the licensed rights.
  *(Verified.)*
- **Paper license.** The ICUMT 2021 paper is an IEEE publication and is **separate**
  from the dataset license; standard IEEE copyright is expected and is **not** the
  license governing dataset use. *(Observation — the dataset `LICENSE` governs the
  data; the paper's terms are not relied on here.)*

**Source agreement.** For MPDD there is now **no licensing contradiction**: the
official `LICENSE` file is authoritative and reads CC BY-NC-SA 4.0. Where secondary
sources previously said only that "a LICENSE file exists," this investigation resolves
the specific term. The **authoritative source is the repository `LICENSE` file**;
mirrors that omit or paraphrase it are superseded by it.

---

## 3. Governance Assessment

Assessed against the Dataset Strategy's mandatory properties. Each item is marked
**Satisfied**, **Partially satisfied**, or **Unresolved**, on verified facts.

- **Provenance — Partially satisfied.** Origin is known at the dataset level (VUT Brno;
  named authors; ICUMT 2021 paper describing collection in real metal-fabrication/
  painting conditions). *(Verified.)* Per-input provenance detail (capture setup,
  device, conditions per image) is **not** documented at the official source.
  *(Observation of absence.)*
- **Ownership — Partially satisfied.** Authorship and maintainer contacts are clear and
  institution-affiliated. *(Verified.)* A formal statement of dataset ownership/rights
  beyond the CC license is not separately published. *(Observation.)*
- **Licensing — Satisfied (as a known term); compatibility Unresolved.** The license is
  now **verified** as CC BY-NC-SA 4.0. The *term is known and explicit* — this property
  is satisfied. **Compatibility with Kalibra's intended use is Unresolved**, because it
  is **non-commercial** and Kalibra's commercial posture is an unanswered open question
  (Landscape §10; Dataset Selection ADR §9). Known ≠ compatible.
- **Versioning — Unresolved.** No formal version identifier, release tag, or dataset
  DOI is published for MPDD v1 at the official source; the existence of a separate
  `MPDD2` repository implies iteration but does not version v1. Distribution via a
  mutable SharePoint share provides no fixed version handle. *(Verified absence of a
  formal version ID.)*
- **Reproducibility — Partially satisfied.** A researcher who downloads the archive can
  fix a local snapshot, and the paper documents the benchmark structure. *(Observation
  / Verified structure.)* But without a published version ID or integrity digest,
  independent regeneration from *the same verified starting point* cannot be guaranteed
  against the official source. *(Unresolved element.)*
- **Integrity verification — Unresolved.** No official content hash/checksum is
  published for the MPDD archive; integrity cannot be verified against a source-of-truth
  digest. *(Verified absence.)*
- **Long-term availability — Unresolved.** The dataset is served from a **personal VUT
  SharePoint link**, not an archival repository with persistent identifiers (e.g.
  Zenodo/DOI). Personal institutional shares are subject to link rotation, account
  changes, and revocation, posing a real availability risk for as long as a claim must
  stand. *(Verified hosting mechanism; risk is an Observation.)*

**Governance summary.** Satisfied: license-term-known, and (at dataset level)
provenance/ownership are partially there. Unresolved and **gating**: versioning,
integrity verification, long-term availability, and licensing-**compatibility**
(pending commercial posture). Governance readiness is therefore **not achieved on
verified facts**.

---

## 4. Dataset Characteristics

- **Number of images — Verified (coarse).** "more than 1000 images with pixel-precise
  defect annotation masks," per the official README. An exact total and per-class
  counts are **not** stated at the official source. *(Verified the ">1000" figure;
  exact counts Unresolved.)*
- **Number of part categories — Observation.** Secondary literature commonly reports
  **6 metal-part types**, but the official README does **not** enumerate the category
  count or names. Treated as **Observation**, not verified fact, pending the paper or
  the dataset package. *(Unverified at official source.)*
- **Anomaly types — Partially verified.** The dataset targets defects in real
  metal-fabrication and painting conditions; the official README does not enumerate a
  fixed defect taxonomy inline. Specific defect-type lists appear in secondary sources
  only. *(Verified domain; taxonomy Observation.)*
- **Pixel masks — Verified.** "pixel-precise defect annotation masks" are provided.
  *(Verified from README.)*
- **Train/test structure — Verified.** The **training subset contains anomaly-free
  (normal) samples only**, and the **validation subset contains both normal and
  anomalous samples** — an anomaly-detection-style split. *(Verified from README.)* A
  separately labeled held-out *test* partition beyond this train/validation split is
  not described at the official source. *(Observation of absence.)*
- **Annotation quality — Unresolved.** Masks are pixel-precise, but the annotation
  process, reviewer agreement, and treatment of ambiguity are **not** documented at the
  official source. *(Verified absence of process documentation.)*

---

## 5. Scientific Suitability

Qualitative, per the governing documents; no benchmark claim is made.

- **Anomaly detection — Strong fit.** The train-on-normal / validate-on-mixed structure
  and pixel-mask defects align directly with Kalibra's anomaly-detection-first scope.
  *(Observation grounded in verified structure.)*
- **Bounded localization — Supported.** Pixel-precise masks provide the ground truth the
  bounded secondary localization objective requires — where a localization claim is made.
  *(Verified masks; suitability an Observation.)*
- **Industrial realism — Strong.** Collected under real metal-fabrication/painting
  conditions; the ICUMT paper explicitly frames it as harder than lab benchmarks.
  *(Verified framing.)*
- **Metal components — Closest surveyed match.** Among the surveyed public datasets,
  MPDD is the most directly on-domain for Kalibra's metal-component target.
  *(Observation.)*
- **Cast aluminium proxy — Partial.** Metal parts under real conditions are a **proxy**,
  not a match; MPDD is not cast-aluminium specific, so any cast-aluminium claim inherits
  a domain-shift caveat. *(Observation.)*
- **Machining proxy — Partial.** Similarly a proxy; not machining-specific (no confirmed
  focus on tool marks, chatter, burrs). *(Observation.)*

Scientific suitability is comparatively high; it does **not** override the unresolved
governance items in §3.

---

## 6. Risks

- **Licensing uncertainty — Largely resolved, but compatibility risk remains.** The
  term is now verified (CC BY-NC-SA 4.0). The residual risk is **non-commercial
  incompatibility** if Kalibra's use is or becomes commercial; the ShareAlike clause
  also propagates obligations to any derivative. *(Verified license; compatibility risk
  real.)*
- **Maintenance risk — Moderate to high.** Hosting on a personal VUT SharePoint share
  and reliance on individual maintainers create link-rot and continuity risk; a
  successor MPDD2 may shift attention from v1. *(Observation.)*
- **Domain mismatch — Present.** A metal-parts proxy, not cast-aluminium/machining;
  claims must carry a domain-shift caveat. *(Observation.)*
- **Benchmark saturation — Lower than MVTec AD, rising.** MPDD is increasingly used in
  anomaly-detection literature; saturation is less severe than the dominant benchmarks
  but growing. *(Observation.)*
- **Future availability — Unresolved.** No persistent identifier or archival copy is
  established at the official source, so long-term regeneration of exact evidence is at
  risk. *(Verified absence of DOI/archive.)*

---

## 7. Final Governance Decision

```text
INSUFFICIENT VERIFIED EVIDENCE
```

**Justification.** This investigation **resolves the license question** — MPDD is
verified **CC BY-NC-SA 4.0** — which is a real advance over the Dataset Selection
ADR's "license type unconfirmed." However, resolving the license is necessary but not
sufficient for governance readiness, and several **gating** governance properties
remain unresolved on verified facts:

- **Licensing compatibility is undecided.** The license is non-commercial; it cannot be
  judged compatible until Kalibra's **commercial posture** is decided. A known term is
  not an admissible term.
- **No versioning.** No official version ID/tag/DOI fixes MPDD v1 as a citable, stable
  version.
- **No integrity verification.** No official checksum/hash allows the exact bytes used
  to be verified.
- **Long-term availability is at risk.** Distribution via a personal SharePoint share,
  with no archival record, does not meet the standing-availability requirement.
- **Annotation process and exact composition are undocumented at source.** Category
  count, per-class counts, defect taxonomy, and annotation/agreement process are
  secondary-source **observations**, not verified from the official source.

Because governance requirements are **not demonstrably satisfied**, MPDD is **not**
recommended and the decision is INSUFFICIENT VERIFIED EVIDENCE.

**Exactly what is still missing (blockers to clear before any ADR update toward
selection):**

1. A decision on Kalibra's **commercial posture**, since a non-commercial license
   gates admissibility.
2. An **official, citable version** of MPDD v1 (tag or archival DOI).
3. An **official integrity digest** (hash/checksum) for the archive.
4. A **durable, archival hosting** record (e.g. institutional repository / DOI) to meet
   long-term availability.
5. **Official documentation** of dataset composition (category count and names, defect
   taxonomy, exact counts) and of the **annotation process** (standard, reviewer
   agreement, ambiguity handling).

---

## Closing Statement

This investigation verifies MPDD's official sources, maintainers, and — decisively —
its **CC BY-NC-SA 4.0** license, resolving the item the Dataset Selection ADR left
open. It does not modify that ADR, approve selection, or recommend MPDD: on verified
facts, licensing-compatibility (pending commercial posture), versioning, integrity
verification, long-term availability, and source-level documentation of composition and
annotation remain unresolved. The governance conclusion is therefore **INSUFFICIENT
VERIFIED EVIDENCE**, with the five blockers above stated precisely. The provider
abstraction and the Inspection, Trust, Review, Evidence, and Evaluation ownerships are
untouched; no benchmark claim is made.
