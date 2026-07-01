# Kalibra — VisA Licensing & Governance Investigation v1.0

## About This Document

This is a focused governance investigation of the **VisA (Visual Anomaly)**
dataset. It exists solely to determine whether VisA can satisfy Kalibra's
dataset-governance requirements. It implements no code, **modifies no ADR**,
recommends no dataset selection, and discusses no framework.

It is a research artifact filed under `docs/research/`. It informs, but does not
change, the
[`Dataset Selection ADR`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md),
which currently records VisA as *Deferred* because of a licensing contradiction
reported across sources.

**Verification convention.** A **Verified** statement is confirmed against an
official or primary source during this investigation (research conducted July 2026):
the dataset's official repository, the AWS Open Data registry entry, AWS-hosted
distribution metadata, the official paper, Amazon Science, Springer, or Creative
Commons legal text. An **Observation** is an inference, a risk assessment, or a
secondary-source statement and is **not** treated as fact.

**Headline finding.** The previously recorded VisA license contradiction is resolved
on official sources. The official repository, the repository `NOTICE`, the
repository `LICENSE-DATASET` file, the AWS Open Data registry entry, and the AWS
Marketplace listing all identify the dataset license as **Creative Commons
Attribution 4.0 International (CC BY 4.0)**. A third-party documentation page that
reports CC BY-NC-SA 4.0 is not authoritative. This finding is strong enough for a
future ADR update to revise VisA's licensing status, but it does **not** by itself
select VisA as Kalibra's dataset.

---

## 1. Official Sources

- **Official repository.** `https://github.com/amazon-science/spot-diff`.
  The `amazon-research/spot-diff` URL named in the paper and registry redirects to
  `amazon-science/spot-diff`. The repository describes itself as resources for
  the ECCV 2022 paper and states that it currently releases the VisA dataset.
  *(Verified.)*
- **Official maintainers / authors.** Yang Zou, Jongheon Jeong, Latha Pemula,
  Dongqing Zhang, and Onkar Dabeer are named by the official repository, Amazon
  Science publication page, arXiv record, Springer chapter, and ECVA paper PDF.
  *(Verified.)*
- **Affiliations.** The official paper lists AWS AI Labs for Yang Zou, Latha
  Pemula, Dongqing Zhang, and Onkar Dabeer, and KAIST for Jongheon Jeong; it also
  notes that Jongheon Jeong's work was done during an Amazon internship.
  *(Verified.)*
- **Hosting institution / managed-by source.** The AWS Open Data registry entry
  lists the dataset as managed by Amazon Web Services. The dataset object is hosted
  in an AWS S3 bucket under `amazon-visual-anomaly` in `us-west-2`. *(Verified.)*
- **Official paper.** "SPot-the-Difference Self-supervised Pre-training for
  Anomaly Detection and Segmentation," ECCV 2022 / Springer LNCS, pp. 392-408,
  DOI `10.1007/978-3-031-20056-4_23`; also available from ECVA, arXiv
  `2207.14315`, and Amazon Science. *(Verified.)*
- **Canonical download source.** The official repository links directly to
  `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar`.
  The AWS Open Data registry records the same object as
  `arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar`, with no AWS account
  required for access. *(Verified.)*
- **S3 object metadata checked.** A HEAD request on 2026-07-01 returned
  `Content-Length: 1929840640`, `Last-Modified: Thu, 22 Sep 2022 19:23:39 GMT`,
  `Content-Type: application/x-tar`, and ETag
  `"05c830591a1172938cb714895c9e0cfb-113"`. *(Verified.)*
- **Repository release state.** The official GitHub repository had no published
  releases and no tags when checked; `main` resolved to commit
  `2a692ab575001cbde74d402d897a7286086c6199`. *(Verified.)*

**Official vs secondary sources.** The official source set is the repository,
dataset license file, repository notice, AWS registry, AWS Marketplace listing,
canonical S3 object, and official paper records. Secondary catalogues, mirrors,
and tooling documentation are not authoritative for provenance or license terms.

---

## 2. Licensing Resolution

### 2.1 Dataset License

- **Dataset license — Satisfied / Verified.** VisA is released under
  **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
  The official README states that the data is released under CC BY 4.0; the
  official `LICENSE-DATASET` file is the CC BY 4.0 legal code; the repository
  `NOTICE` says the dataset is made available under CC BY 4.0; the AWS Open Data
  registry and AWS Marketplace listing both link to CC BY 4.0. *(Verified.)*
- **Commercial use — Permitted under CC BY 4.0.** Creative Commons' CC BY 4.0 deed
  permits sharing and adaptation for any purpose, including commercial purposes,
  provided the license terms are followed. *(Verified.)*
- **Redistribution — Permitted with attribution and no additional restrictions.**
  CC BY 4.0 permits copying and redistribution in any medium or format; downstream
  recipients must not be restricted from exercising the licensed rights.
  *(Verified.)*
- **Derivative works — Permitted.** CC BY 4.0 permits remixing, transformation, and
  building upon the material. It does **not** impose ShareAlike and it is **not**
  NonCommercial. *(Verified.)*
- **Attribution — Required.** Sharing the dataset or adapted material requires
  appropriate credit, a license reference, and indication of changes where changes
  were made. *(Verified.)*
- **Other rights caveat.** CC BY 4.0 does not license patent or trademark rights,
  and the Creative Commons deed warns that other rights such as publicity, privacy,
  or moral rights may still limit a use. *(Verified.)*

### 2.2 Repository License

- **Repository code license — Apache License 2.0.** The official repository contains
  an Apache-2.0 `LICENSE` file for the utility code. The repository notice states
  that the utility code is made available under Apache-2.0 and the dataset under
  CC BY 4.0. *(Verified.)*
- **Repository redistribution and derivatives.** Apache-2.0 permits reproduction,
  distribution, and derivative works, subject to license, notice, and attribution
  conditions. *(Verified.)*
- **Repository commercial use.** Apache-2.0 does not impose a non-commercial
  restriction. *(Verified from license text.)*

### 2.3 Source Disagreement

No official source disagreement was found. Official sources consistently identify
the dataset license as **CC BY 4.0**.

A third-party documentation page reports the VisA dataset as CC BY-NC-SA 4.0.
That page is a secondary tooling reference, not the dataset publisher, host, or
licensor. The authoritative license source is the official repository's
`LICENSE-DATASET` file, corroborated by the official README, repository notice,
AWS Open Data registry entry, and AWS Marketplace listing.

---

## 3. Governance Assessment

Assessed against Kalibra's Dataset Strategy and ML Phase 2 Dataset Strategy. Each
item is marked **Satisfied**, **Partially satisfied**, or **Unresolved**, on
verified facts.

| Governance requirement | Status | Assessment |
| --- | --- | --- |
| Provenance | Partially satisfied | Dataset-level provenance is clear: named authors, official Amazon Science repository, AWS AI Labs / KAIST paper affiliations, AWS Open Data hosting, and official paper. The paper documents object domains, counts, high-resolution RGB acquisition, and manually generated realistic defects. Per-input capture conditions, item lineage, and label provenance are not fully documented at source. |
| Ownership | Partially satisfied | The official repository notice identifies Amazon.com, Inc. or its affiliates as copyright holder for SpotDiff and states the dataset is made available under CC BY 4.0. The public license establishes reuse rights. A separate ownership statement covering all upstream physical objects, object designs, or third-party interests was not located. |
| Licensing | Satisfied | Dataset license is verified CC BY 4.0. Repository code license is verified Apache-2.0. Commercial use, redistribution, derivative works, and attribution obligations are resolved from official license texts. |
| Versioning | Partially satisfied | The canonical archive has a dated filename, `VisA_20220922.tar`, and the AWS registry says update frequency is "Not updated." Repository split files and utility code can be pinned by Git commit. However, there is no formal dataset version number, release tag, DOI, or immutable GitHub release. |
| Integrity | Partially satisfied | The canonical S3 object exposes official object metadata including content length, last-modified timestamp, and ETag. No official SHA-256 or manifest checksum was located, and the multipart-style ETag is not a clean substitute for a published content digest. |
| Reproducibility | Partially satisfied | The repository documents download, structure, preparation scripts, split CSV files, and evaluation protocols; the AWS registry exposes the canonical S3 object. Reproducibility is still short of Kalibra's full bar because the dataset is not tied to a formal release/DOI and lacks a published strong checksum. |
| Long-term availability | Partially satisfied | AWS Open Data hosting, S3 access without an AWS account, and an AWS-managed registry entry are materially stronger than personal-file-share hosting. Still, no DOI-backed archive, immutable release, preservation commitment, or independent archival record was found. |

**Governance summary.** Licensing is now **Satisfied** on verified facts. Provenance,
ownership, versioning, integrity, reproducibility, and long-term availability are
**Partially satisfied**, not fully closed. No assessed governance requirement is
fully **Unresolved**, but VisA is not yet governance-complete under Kalibra's full
evidence standard without an acquisition record that pins the archive bytes, commit,
splits, and limitations.

---

## 4. Dataset Characteristics

- **Size and classes — Verified.** VisA contains 10,821 high-resolution color
  images: 9,621 normal and 1,200 anomalous samples, covering 12 objects in
  3 domains. Both image-level and pixel-level labels are provided.
- **Object groups — Verified.** The 12 objects include four PCB subsets with complex
  structures, four multiple-instance subsets, and four roughly aligned single-instance
  subsets.
- **Anomaly types — Verified in outline.** The official repository and paper describe
  surface defects such as scratches, dents, color spots, or cracks, and structural
  defects such as misplacement or missing parts. The paper states that an image may
  contain multiple defects.
- **Image acquisition — Verified.** The official paper states that all images were
  acquired using a 4000 x 6000 high-resolution RGB sensor.
- **Defect creation — Verified.** The official paper states that defects were
  manually generated to produce realistic anomalies.
- **Annotation support — Verified in outline.** The repository states that
  `image_anno.csv` gives image-level labels and pixel-level annotation masks, and
  that normal masks are not stored to save space.
- **Splits and preparation — Verified.** The repository provides preparation scripts
  and split CSV files for 1-class and 2-class setups. For the 1-class setup, normal
  images are used for training and both normal and anomalous images appear in test.
- **Annotation process — Unresolved.** The official sources verify that masks and
  labels exist, but they do not fully document the annotation process, reviewer
  agreement, ambiguity handling, or quality-control procedure.

---

## 5. Scientific Suitability

This section is qualitative. It makes no benchmark claim and imports no reported
performance as Kalibra evidence.

- **Anomaly detection — Strong fit.** *(Observation grounded in verified structure.)*
  VisA directly supports sound-vs-defective inspection with a large normal population,
  anomalous samples, 1-class and 2-class protocols, and official split files.
- **Localization — Supported.** *(Observation grounded in verified labels.)* Pixel-
  level masks support Kalibra's bounded localization objective where localization is
  claimed. The absence of detailed annotation-process documentation limits how strong
  any localization-ground-truth claim can be.
- **Industrial realism — Partial.** *(Observation.)* VisA is framed by the official
  paper as an industrial anomaly dataset and includes PCBs and manufactured consumer
  items captured with a high-resolution RGB sensor. However, defects were manually
  generated, and the source is a curated benchmark rather than a documented production
  inspection line.
- **Relevance to Kalibra — Useful proxy, not domain match.** *(Observation.)* VisA is
  relevant to anomaly detection and localization, and its official licensing/governance
  posture is stronger than previously recorded. It is not specific to cast aluminium,
  CNC machining, gearbox housings, or Kalibra's target metal-component domain, so it
  cannot support those domain-specific claims without a domain-shift caveat.

---

## 6. Risks and Remaining Gaps

- **Domain mismatch.** VisA is not a cast-aluminium or machined-component dataset.
  Any Kalibra claim based on it would need to be bounded to VisA-like objects and
  conditions. *(Observation.)*
- **Curated / manual defects.** The paper states that defects were manually generated
  to produce realistic anomalies. This supports controlled defect presence but limits
  claims about production-occurring defect distributions. *(Verified fact; risk is
  Observation.)*
- **Annotation process opacity.** Pixel masks are present, but reviewer agreement,
  ambiguity policy, and annotation quality-control process are not fully documented
  at the official source. *(Verified absence.)*
- **Versioning incompleteness.** The archive filename is dated, but no formal version
  ID, DOI, release tag, or immutable release was found. *(Verified.)*
- **Integrity incompleteness.** Official S3 metadata exists, but no official SHA-256
  or checksum manifest was located. *(Verified.)*
- **Availability not archival.** AWS Open Data hosting is a strong public host, but
  no persistent archival DOI or preservation guarantee was found. *(Verified absence;
  risk is Observation.)*
- **Secondary-source license conflict.** A third-party page reports CC BY-NC-SA 4.0.
  This is superseded by official CC BY 4.0 sources, but the ADR should record why the
  earlier contradiction is resolved rather than silently dropping it. *(Observation.)*

---

## 7. Final Decision

```text
READY FOR DATASET ADR UPDATE
```

**Justification.** The investigation resolves the ADR's load-bearing VisA licensing
uncertainty against official sources: the dataset license is **verified CC BY 4.0**,
not CC BY-NC-SA 4.0, and the repository utility code is **Apache-2.0**. Commercial
use, redistribution, derivative works, and attribution obligations are all resolved
from official license texts.

This decision means only that the Dataset Selection ADR has enough verified evidence
to update VisA's licensing and governance assessment. It does **not** recommend
dataset selection. VisA remains only **partially governance-satisfied** because
versioning, strong integrity verification, annotation-process evidence, and archival
availability are not fully closed under Kalibra's evidence standard.

**Items a future ADR update should record:**

1. VisA's dataset license is verified **CC BY 4.0** from official sources.
2. The repository utility code is verified **Apache-2.0**.
3. Official sources do not disagree; the CC BY-NC-SA statement is secondary and not
   authoritative.
4. Canonical distribution is the AWS S3 archive `VisA_20220922.tar`, recorded in the
   AWS Open Data registry.
5. Remaining blockers are non-license governance gaps: no DOI/release tag/formal
   version, no published strong checksum, incomplete annotation-process documentation,
   and no archival preservation guarantee.

---

## 8. Verified Source Record

- Official repository:
  `https://github.com/amazon-science/spot-diff`
- Redirected historical repository URL:
  `https://github.com/amazon-research/spot-diff`
- Official dataset license file:
  `https://raw.githubusercontent.com/amazon-science/spot-diff/main/LICENSE-DATASET`
- Official repository code license:
  `https://raw.githubusercontent.com/amazon-science/spot-diff/main/LICENSE`
- Official repository notice:
  `https://raw.githubusercontent.com/amazon-science/spot-diff/main/NOTICE`
- Official README:
  `https://raw.githubusercontent.com/amazon-science/spot-diff/main/README.md`
- AWS Open Data registry:
  `https://registry.opendata.aws/visa/`
- AWS Open Data registry source YAML:
  `https://github.com/awslabs/open-data-registry/blob/main/datasets/visa.yaml`
- AWS Marketplace listing:
  `https://aws.amazon.com/marketplace/pp/prodview-a6u3urwfasrp2`
- Canonical S3 archive:
  `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar`
- Amazon Science publication page:
  `https://www.amazon.science/publications/spot-the-difference-self-supervised-pre-training-for-anomaly-detection-and-segmentation`
- Springer official chapter:
  `https://link.springer.com/chapter/10.1007/978-3-031-20056-4_23`
- ECVA paper PDF:
  `https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136900389.pdf`
- arXiv record:
  `https://arxiv.org/abs/2207.14315`
- Creative Commons CC BY 4.0 deed:
  `https://creativecommons.org/licenses/by/4.0/`
- Creative Commons CC BY 4.0 legal code:
  `https://creativecommons.org/licenses/by/4.0/legalcode.en`
- Secondary conflicting source, not authoritative:
  `https://anomalib.readthedocs.io/en/v2.0.0/markdown/guides/reference/data/datamodules/image/visa.html`

---

## Closing Statement

VisA's licensing uncertainty is resolved on verified official evidence. The dataset
is CC BY 4.0, its utility repository is Apache-2.0, and its canonical archive is the
AWS-hosted `VisA_20220922.tar` object. This makes VisA ready for a Dataset Selection
ADR update, but not automatically ready for selection. Kalibra still needs to record
or obtain stronger versioning, integrity, annotation-process, and archival-availability
evidence before VisA could be treated as governance-complete.
