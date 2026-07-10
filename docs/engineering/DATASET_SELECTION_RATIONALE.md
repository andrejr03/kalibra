# Dataset Selection Rationale

**Date:** 2026-07-05

## 1. Repository State / Baseline

- Kalibra engineering infrastructure is complete through Sprint 1H; the governed,
  deterministic image → evaluation substrate is proven on real ONNX Runtime.
- ML Capability Engineering has begun (roadmap phases C-1 … C-8).
- **PaDiM** is selected as the first model family; **PatchCore** is reserved as the
  second-generation candidate.
- The Dataset Selection ADR currently records **`DEFER`**, with VisA as the
  governance anchor and MPDD as the domain anchor.
- This record records the decision basis for moving from `DEFER` to
  `SELECTED — VisA`. The formal ADR amendment is a separate, later action.

## 2. Context

The DEFER decision was never a data-availability problem. It reflected (a) an unmade
governance-acceptance decision, and (b) residual governance evidence that is
self-closable by Kalibra's own governed-acquisition infrastructure. Two developments
now permit closure: PaDiM has been selected as the first model family (adding an
image-alignment criterion), and this record is the approved venue to make the
explicit governed-proxy acceptance that the Data Strategy Decision Memo named as the
precondition for selecting VisA. Only the repository's existing recorded research is
used; no new external research was performed.

## 3. Dataset Comparison Summary

Drawn solely from recorded repository research (Dataset Selection ADR §4, MPDD/VisA
governance investigations, Data Strategy Decision Memo).

| Candidate | Anomaly-detection suitability | Domain fit | PaDiM alignment | Localization | Licensing (verified) | Governance readiness |
|---|---|---|---|---|---|---|
| **VisA** | Yes (train-normal) | Proxy (3 domains, not parts) | **Good — well-aligned** | Image **+ pixel** | **CC BY 4.0 (permissive)** | Licensing satisfied; provenance/version/integrity **partial**, self-closable |
| **MPDD** | Yes (train-normal / mixed-val) | **Closest — metal parts** | **Weaker — pose variation** | Pixel masks | CC BY-NC-SA 4.0 (NC, compatible) | Licensing satisfied; **4 non-licensing blockers**, incl. weak long-term availability |
| MVTec AD | Yes | Proxy | Excellent (native benchmark) | Pixel | CC BY-NC-SA 4.0 (NC) | High, but **benchmark-saturated** |
| MVTec AD 2 | Yes | Proxy (distant) | Good | Pixel | CC BY-NC-SA 4.0 (NC) | High, but newer / less-settled |
| BTAD | Yes | Real-industrial | — | Body/surface | **Unverified** (obs. CC BY-SA 4.0) | Provenance/license unconfirmed |
| KolektorSDD | Yes | Narrow (commutators) | — | To confirm | CC BY-NC-SA 4.0 (NC) | Acceptable, but domain too narrow |
| KolektorSDD2 | Yes | Specific surface setting | — | To confirm | CC BY-NC-SA 4.0 (NC) | Acceptable, but domain-distant |

The field reduces to the two recorded anchors — **VisA (governance)** and
**MPDD (domain)**. The remaining governance-clean candidates are proxies with
saturation (MVTec) or narrow/distant domains (Kolektor); BTAD is blocked on
unverified provenance/license.

## 4. Governance Assessment

### VisA — governance anchor (SELECTED)
- Verified **CC BY 4.0** — permissive; the only non-NC verified license in the field.
- Official source: Amazon Science; canonical AWS S3 archive in the **AWS Open Data
  Registry**; license agreement across official repo, AWS registry, and marketplace.
- **Long-term availability strongest among candidates.**
- Image-level **and** pixel-level labels — supports PaDiM raw measure and localization.
- **Governance gaps are self-closable by Kalibra's governed acquisition:**
  - Kalibra-side sha256 integrity manifest
  - pinned dated archive / acquisition record
  - provenance manifest
  - immutable train/validation/test split manifest
- **Remaining limitations (irreducible from Kalibra's side):**
  - no upstream DOI / formal version tag
  - no published strong upstream checksum
  - incomplete annotation-process documentation
  - proxy domain — not the direct metal-parts domain

### MPDD — domain anchor (NOT selected)
- Closest domain fit (industrial metal parts); pixel masks.
- Verified **CC BY-NC-SA 4.0**, compatible with the current non-commercial /
  research-portfolio posture.
- **Not selected because:**
  - long-term availability remains weak (personal VUT SharePoint distribution)
  - versioning / integrity / archival evidence incomplete
  - pose variation weakens PaDiM alignment
- Retained as the domain anchor to mature toward governance readiness for a later
  domain-specific pass.

### Other candidates (not selected)
- **MVTec AD / AD 2:** strong benchmarks, but proxy domain and benchmark-saturated.
- **BTAD:** license/provenance insufficiently verified.
- **KolektorSDD / KolektorSDD2:** governance acceptable, but domain narrow
  (commutators) or domain-distant (surface-inspection setting).

## 5. Decision

```text
SELECT — VisA
```

Qualifier:

```text
Selected as governed proxy dataset for first Kalibra baseline.
No domain-of-record claim approved.
```

MPDD remains the domain anchor and is not selected for the first governed baseline.

## 6. Technical Justification

- The Data Strategy Decision Memo required **explicit acceptance that VisA is a
  governed proxy** rather than a direct domain match; this record makes that
  acceptance explicit.
- **PaDiM selection tips the balance to VisA** — PaDiM benefits from image alignment,
  and VisA is well-aligned with image and pixel labels, whereas MPDD's pose variation
  is a recorded PaDiM degradation risk.
- VisA holds the **strongest licensing and governance position** (permissive CC BY
  4.0; AWS Open Data Registry availability).
- **VisA's residual gaps are mostly self-closable** by the governed-acquisition step
  using infrastructure Kalibra already has (deterministic content hashing, provenance
  manifests).
- **MPDD's domain fit is stronger, but its governance/availability risk is worse** and
  not self-closable (upstream archival fragility).
- Selecting VisA **enables C-2 Evaluation Protocol Fixation** on solid governance
  footing while MPDD matures.

## 7. Accepted Limitations / Non-Claims

- VisA is a **governed proxy**, not Kalibra's direct target domain.
- **No cast-aluminium / machined-component claim** is approved.
- **No real defect-detection claim** is approved.
- **No product-readiness claim** is approved.
- **No benchmark claim** is approved.
- The dataset is **selected but not yet acquired**.
- Governed acquisition must still produce the **local manifest, hashes, and split
  record** before any data is used.
- **No model training** is approved by this record.

## 8. Readiness for C-2

```text
C-1 decision gate is closed.
Kalibra is ready to begin C-2 Evaluation Protocol Fixation.
```

Caveat:
- C-2 **may be designed now** — VisA's structure (12 classes, 3 domains, image- and
  pixel-level labels, official split files) is known from recorded research and is
  sufficient to design the deterministic evaluation protocol, metrics, and splits.
- C-2 **execution requires the governed acquisition of VisA to complete first**
  (download + Kalibra-side integrity manifest + version pinning).

## 9. Next Natural Step

```text
Update Dataset Selection ADR from DEFER to SELECTED — VisA.
```

That ADR update is a separate, approved documentation action and is **not**
performed by this record. See the C-1 strategy context in
`docs/adr/001-dataset-selection.md`.
