# Kalibra ML Phase 2 Data Strategy Decision Memo v1.0

## 1. Executive Summary

Kalibra has completed a public industrial dataset landscape review and focused
governance investigations for MPDD and VisA. The resulting evidence improves the
ML Phase 2 dataset posture, but it does not yet justify selecting a dataset.

The current governance state is stronger than the initial landscape review
suggested. VisA now has a verified dataset license of CC BY 4.0 and repository
utility code under Apache-2.0, with official sources agreeing on that position.
MPDD now has a verified dataset license of CC BY-NC-SA 4.0, which is compatible
with Kalibra's recorded non-commercial research and portfolio posture. Licensing
is therefore no longer the central blocker for either leading candidate.

The current scientific state remains split. VisA is the stronger governance
candidate because its licensing, official repository, maintainers, hosting, and
canonical download source are better evidenced. MPDD remains the stronger domain
candidate because it is the closest surveyed public dataset to Kalibra's target
of industrial metal-component visual inspection. Neither candidate satisfies all
governance requirements.

No dataset has been selected because the evidence still leaves open governance
gaps in provenance depth, ownership clarity, versioning, integrity,
reproducibility, and long-term availability. ML Phase 2 dataset selection remains
intentionally deferred.

## 2. Dataset Landscape Outcome

The completed landscape review found no public dataset that fully satisfies
Kalibra's scientific and governance needs at the same time.

The public dataset landscape supports anomaly detection and localization
experimentation, but only as a proxy for Kalibra's target domain. Several
datasets offer useful image-level and pixel-level annotations, and several are
institutionally maintained. However, the landscape does not contain a verified
public dataset dedicated to Kalibra's long-term target areas:

- cast aluminium inspection;
- CNC machining defects, tool marks, chatter, or burrs;
- gearbox housings or similarly complex cast and machined housings.

The outcome of the landscape review is therefore strategic rather than
selective. Public datasets can support early evidence-building only if their
governance is sufficient and their limits are made explicit. They should not be
treated as permanent substitutes for a governed dataset closer to Kalibra's
intended inspection domain.

## 3. Current Candidate Position

### VisA

Strengths:

- Verified official repository under Amazon Science.
- Verified official maintainers and hosting path.
- Verified dataset license of CC BY 4.0.
- Verified repository utility-code license of Apache-2.0.
- Official sources agree on licensing.
- Canonical download source is documented.
- Supports anomaly detection and localization through image-level and pixel-level
  labels.
- Broader object coverage than narrower single-domain datasets.

Weaknesses:

- Not a cast aluminium, CNC machining, or gearbox housing dataset.
- Defects are manually generated rather than direct production-line captures.
- No formal dataset version number, DOI, release tag, or immutable archival
  record has been verified.
- No official strong checksum or complete manifest has been verified.
- Annotation-process evidence remains incomplete.

Current governance maturity:

VisA is currently the strongest governance candidate. Its licensing evidence is
satisfied, and its official repository, institutional provenance, hosting, and
download path are better established than the other active public candidates.
Its governance remains incomplete because versioning, integrity,
reproducibility, and long-term availability are only partially satisfied.

### MPDD

Strengths:

- Closest surveyed public match to Kalibra's industrial metal-component target.
- Supports anomaly detection and localization through image-level structure and
  pixel masks.
- Provides a train-on-normal and evaluate-on-mixed structure relevant to
  anomaly detection work.
- Official repository and academic paper are identified.
- Dataset license is verified as CC BY-NC-SA 4.0.
- The verified license is compatible with Kalibra's current non-commercial
  research and portfolio posture.

Weaknesses:

- Smaller and narrower than broader public anomaly-detection datasets.
- Not specifically a cast aluminium, CNC machining, or gearbox housing dataset.
- Canonical distribution is not a formal immutable release.
- No official version number, DOI, release tag, or archival preservation record
  has been verified.
- No official checksum or complete manifest has been verified.
- Annotation-process and dataset-composition evidence remain incomplete.
- Commercial reuse would require a future licensing review or separate
  permission.

Current governance maturity:

MPDD is currently the strongest domain candidate. Its licensing evidence has
materially improved, but its governance remains incomplete. The main blockers are
versioning, archival durability, integrity evidence, and deeper documentation of
dataset composition and annotation provenance.

### Remaining datasets

MVTec AD and MVTec AD 2 remain mature and institutionally maintained public
industrial anomaly-detection datasets, but they are domain-distant proxies for
Kalibra's target metal-component inspection focus. Their governance maturity is
useful as a reference point, but their scientific fit is weaker than MPDD for
Kalibra's current target.

KolektorSDD and KolektorSDD2 remain relevant public surface-defect datasets, but
their narrower domain fit does not exceed MPDD for Kalibra's intended direction
and does not exceed VisA's current governance position.

The remaining surveyed datasets are no longer priority candidates because they
have weaker licensing evidence, weaker provenance, competition-gated access,
synthetic-only limitations, classification-oriented structure, or weaker
alignment with Kalibra's target industrial inspection claims.

## 4. Strategic Position

Kalibra's official ML Phase 2 data strategy is:

- VisA is currently the strongest governance candidate.
- MPDD is currently the strongest domain candidate.
- Neither candidate satisfies all governance requirements.
- Dataset selection therefore remains intentionally deferred.

This strategy preserves the current Dataset Selection ADR decision. It does not
select VisA. It does not reject MPDD. It treats both candidates as useful
evidence anchors for future review.

## 5. Long-term Dataset Roadmap

Kalibra should evolve its dataset strategy along the following path:

```text
Public benchmark
        ↓
Industrial partner dataset
        ↓
Kalibra governed dataset
```

Public benchmarks are useful for early comparative discipline, reproducibility
practice, and basic anomaly-detection and localization evidence. They are not a
complete long-term answer because they remain proxies for Kalibra's target
inspection domain and often carry unresolved governance limits.

Industrial partner datasets are the next strategic step because they can move
the evidence closer to real industrial inspection conditions, including the
materials, part geometries, capture conditions, and defect types Kalibra is
intended to address. Partner data would still need explicit governance before it
could support project claims.

A Kalibra governed dataset is the long-term target. It should have clear
provenance, usage rights, ownership boundaries, fixed versioning, integrity
evidence, reproducible acquisition records, documented annotations, and durable
availability. This is preferable to permanent reliance on public datasets
because Kalibra's trust claims ultimately need evidence from the inspection
conditions it is built to evaluate.

## 6. Exit Conditions

Selecting VisA would require evidence that its remaining governance gaps have
been closed or consciously bounded. At minimum, a future ADR revision would need
to verify a fixed dataset snapshot, integrity evidence for the acquired archive,
reproducible acquisition instructions, documented attribution requirements, and
explicit acceptance that VisA is a governed proxy rather than a direct
metal-component domain match.

Selecting MPDD would require evidence that its remaining governance gaps have
been closed or consciously bounded. At minimum, a future ADR revision would need
to verify a fixed dataset snapshot, stronger archival or institutional
availability, integrity evidence for the acquired archive, reproducible
acquisition instructions, and enough dataset-composition and annotation evidence
to support Kalibra's documented claims. Any future commercial posture would also
require a separate licensing review or permission because MPDD is licensed under
CC BY-NC-SA 4.0.

Replacing both candidates would require a new candidate that materially exceeds
both current anchors. The new candidate would need to match or exceed VisA's
governance position while matching or exceeding MPDD's domain relevance. A
candidate focused on cast aluminium inspection, CNC machining defects, or
gearbox housings would be strategically stronger only if its license,
provenance, versioning, integrity, reproducibility, and long-term availability
were also verified.

## 7. Future Direction

The likely long-term strategic direction is not permanent dependence on public
benchmarks. It is a transition toward partner, proprietary, or Kalibra-governed
datasets that better reflect the inspection domains Kalibra is intended to
serve.

The most relevant future dataset areas are:

- cast aluminium inspection;
- CNC machining;
- gearbox housings and related complex cast or machined components.

These areas are strategically important because they align more directly with
Kalibra's target industrial inspection claims than the current public proxies.
They should be pursued only through governed data arrangements that make usage
rights, provenance, versioning, integrity, reproducibility, and availability
explicit before the data is used to support claims.

## 8. Final Recommendation

Kalibra should keep ML Phase 2 dataset selection deferred while preserving VisA
and MPDD as the two active reference candidates.

VisA should be treated as the current governance anchor. MPDD should be treated
as the current domain anchor. Neither should be selected until its remaining
governance gaps are resolved or explicitly bounded in a future Dataset Selection
ADR revision.

The project should avoid broad new public-dataset searching unless a candidate
materially exceeds both VisA and MPDD. The more important strategic work is to
move toward a governed industrial dataset path, ultimately ending in a
Kalibra-controlled or Kalibra-governed dataset for the inspection domains the
system is meant to evaluate.

This memo recommends continued deferral of ML Phase 2 dataset selection. Public
benchmarks remain useful as temporary evidence-building tools, but the long-term
dataset strategy should move toward governed data in cast aluminium inspection,
CNC machining, and gearbox housing inspection.
