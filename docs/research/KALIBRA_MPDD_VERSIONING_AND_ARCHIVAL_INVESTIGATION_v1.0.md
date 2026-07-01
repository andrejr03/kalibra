# Kalibra — MPDD Versioning & Archival Investigation v1.0

## About This Document

This is a focused investigation of whether the **MPDD (Metal Parts Defect Detection)**
dataset has an officially citable, stable, versioned release. It exists to close (or
confirm as open) one of the non-licensing governance blockers recorded against MPDD in
the
[`Dataset Selection ADR`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md) and the
[`MPDD Licensing & Governance Investigation`](KALIBRA_MPDD_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md).

It implements no code, **modifies no ADR**, recommends no dataset selection, and
discusses no framework. It is a research artifact filed under `docs/research/`.

**Verification convention.** A **Verified** statement is confirmed against an
official/primary source (the dataset's own repository, its authors' paper, or a
persistent-archive record) during this investigation (research conducted July 2026).
An **Observation** is an inference or secondary-source report and is **not** treated as
fact.

**Headline finding.** MPDD has **no** official version number, release tag, DOI, or
persistent archive. Its canonical distribution is a **personal institutional SharePoint
share**. The versioning/archival governance requirement is therefore **not** satisfied.

---

## 1. Official Versioning

Investigated against the official repository `github.com/stepanje/MPDD`.

- **Official version number — None.** No dataset version number is stated at the
  official source. *(Verified.)*
- **Release tag — None.** The repository shows **"No releases published"** and carries
  no version tags (a small commit history on the main branch, no tagged releases).
  *(Verified.)*
- **DOI — None.** No DOI for the dataset is present in or linked from the repository.
  *(Verified.)* The associated ICUMT 2021 paper may carry its own IEEE publication DOI,
  but a **paper DOI is not a dataset persistent identifier** and does not version the
  data. *(Observation / distinction.)*
- **Zenodo archive — None found.** No Zenodo record with a DOI for MPDD (or MPDD2) was
  located. *(Verified absence in searches; a private/unindexed record cannot be fully
  excluded — Observation.)*
- **Figshare archive — None found.** No Figshare record located. *(Verified absence in
  searches.)*
- **Institutional repository — None found.** No Brno University of Technology (VUT)
  institutional data-repository record with a persistent identifier was located; the
  only VUT-hosted artifact is a personal SharePoint share (§2). *(Verified absence of a
  formal institutional archive record.)*
- **Immutable release — None.** With no tags, releases, DOI, or archival copy, there is
  no immutable, content-fixed release of MPDD at the official source. *(Verified by the
  absence of all of the above.)*
- **Software Heritage record — Unverified.** Software Heritage routinely archives
  public GitHub repositories, so a snapshot of `stepanje/MPDD` may exist; however, the
  Software Heritage search endpoint was **inaccessible** during this investigation
  (bot-protection wall), so **no snapshot could be confirmed**. *(Explicitly Unverified
  — neither confirmed nor excluded.)*

**Explicit statement.** On verified facts, **no official versioned, citable, immutable
release of MPDD exists.**

---

## 2. Official Distribution

- **Canonical download location.** A **personal VUT SharePoint** share
  (`vutbr-my.sharepoint.com`, personal account `xjezek16`), linked from the official
  README with wording to the effect that "the dataset can be downloaded at the
  following link." *(Verified.)*
- **Is SharePoint the canonical release?** Yes — it is the **only official download
  pointer**, referenced directly from the authors' repository. But it is a **live file
  share, not a release**: it exposes files for download without a version tag, content
  hash, or immutability guarantee. It is canonical *by being the only official source*,
  not by being a fixed release. *(Verified it is the official pointer; "not a release"
  is a characterization grounded in verified facts.)*
- **Mirrors.** Secondary copies and catalog entries exist (e.g. dataset aggregators
  such as HyperAI, Papers with Code's dataset entry, and third-party mirrors). These
  are **not official**, may lag or diverge from the SharePoint contents, and carry no
  authority over provenance or integrity. *(Verified such mirrors exist; their fidelity
  is Observation.)*
- **Archive stability.** A personal SharePoint share depends on the individual account
  and institutional tenancy; links of this kind are subject to rotation, permission
  change, and account lifecycle. No stability guarantee is published. *(Verified
  hosting mechanism; instability is an Observation-level risk.)*
- **Official ownership.** The dataset is owned/maintained by the named authors at VUT
  (Stepan Jezek, Radim Burget, et al.); a successor `MPDD2` repository exists under the
  same owner. *(Verified maintainers; MPDD2 existence Verified.)*

---

## 3. Long-term Availability

- **Archival guarantees — None (Verified absence).** No published guarantee of
  continued availability exists for the SharePoint distribution.
- **Persistent identifiers — None (Verified absence).** No DOI or other persistent
  identifier resolves to MPDD.
- **Institutional preservation — Not evidenced (Verified absence of record).** No VUT
  institutional-repository preservation record was located; a personal SharePoint share
  is not an institutional preservation service.
- **Backup mirrors — Unofficial only (Observation).** Third-party mirrors provide
  incidental redundancy but no authoritative or guaranteed backup, and may diverge from
  the official contents.
- **DOI-backed archives — None (Verified absence).** No Zenodo/Figshare/institutional
  DOI-backed archive was found.
- **Future availability risk — Elevated (Observation, grounded in verified hosting).**
  Because availability depends on a single personal institutional share with no
  archival fallback or persistent identifier, the risk that the exact bytes used for a
  result become unavailable — through link rotation, account change, or dataset
  revision — is materially higher than for a DOI-backed archive.

**Verified vs Observation summary.** *Verified:* no DOI, no persistent identifier, no
release/tag, no institutional-archive record, SharePoint-only official distribution.
*Observation:* the resulting elevated future-availability risk, mirror fidelity, and
the possible-but-unconfirmed Software Heritage snapshot.

---

## 4. Reproducibility Impact

The absence of a DOI, a version identifier, and an immutable archive has concrete
governance consequences, read against the Dataset Strategy's requirements.

- **Scientific reproducibility — Impaired.** Reproducibility requires regenerating a
  result from a **fixed** starting point. Without a version identifier or immutable
  release, "the MPDD used" cannot be pinned unambiguously; a future download from the
  same SharePoint link could differ (correction, re-annotation, re-split) with no way
  to detect or name the difference. *(Verified mechanism; impairment is the direct
  consequence.)*
- **Evidence integrity — Weakened.** With no official content hash and no immutable
  release, the exact bytes behind any result cannot be verified against a
  source-of-truth digest, so integrity cannot be independently confirmed. This compounds
  the separately-recorded integrity blocker. *(Verified.)*
- **Long-term governance — Not satisfiable as-is.** The Dataset Strategy requires
  versioning, integrity verification, and long-term availability for as long as a claim
  stands. A live, unversioned, non-archived share cannot meet these obligations on its
  own terms. *(Verified against the requirement.)*

Reproducibility is not merely inconvenienced here; the missing version/immutability
directly undermines the ability of an untrusting observer to regenerate and verify a
result — which is the standard Kalibra holds itself to.

---

## 5. Possible Remediation

The following are qualitative options that could, in principle, establish a citable,
stable version **without altering the dataset content**. This section **defines no
policy and decides no acceptance** — whether any option is sufficient is a decision for
the repository owner under the Dataset Strategy, not for this investigation.

- **Git commit hash.** Pinning the repository at a specific commit gives a stable
  reference to the *repository state* (README, LICENSE, pointers). *Qualitatively:* cheap
  and precise for the repo, but the **actual image data lives on SharePoint, not in
  Git**, so a commit hash does not by itself fix or verify the dataset bytes. Partial at
  best.
- **GitHub release.** An official tagged release (ideally with the data attached as
  release assets) would provide a named, immutable snapshot. *Qualitatively:* strong
  **if** it carries the actual data and a checksum; weak if it only tags the pointer
  repository. Requires author action.
- **Software Heritage snapshot.** SH can archive the public repository, giving a durable
  reference to the repo state and a persistent SWHID. *Qualitatively:* good durability
  for whatever is *in Git*; again does **not** capture SharePoint-hosted data unless the
  data is in the repository. Its current status here is Unverified (§1).
- **Institutional archive.** Deposit in a VUT (or other) institutional data repository
  with preservation commitments. *Qualitatively:* strong on preservation and provenance;
  depends entirely on author/institution action and is not evidenced today.
- **DOI registration.** A Zenodo/Figshare/institutional DOI minted over a fixed dataset
  snapshot would provide a persistent identifier and an immutable, citable version.
  *Qualitatively:* the **most complete** remedy for versioning, integrity, and long-term
  availability together; requires author action and does not exist today.
- **Author confirmation.** Direct written confirmation from the maintainers of a fixed
  version and its integrity (e.g. a published hash). *Qualitatively:* helpful as
  provenance evidence, but a private assurance is weaker than a public persistent
  archive and would itself need to be preserved as evidence.

Common thread: because the **image data is distributed via SharePoint rather than
version control**, the strongest remedies (DOI over a fixed snapshot, or a data-bearing
release) require **author/institution action**; repository-only measures (commit hash,
SH snapshot) address the repo state but not the dataset bytes. None of these is
established today.

---

## 6. Final Conclusion

```text
INSUFFICIENT VERSIONING EVIDENCE
```

**Why.** On verified facts, MPDD has **no official version number, no release tag, no
DOI, no Zenodo/Figshare/institutional archive, and no immutable release**; its only
official distribution is a **personal VUT SharePoint share** that is a live file
listing rather than a fixed, content-verified release. The Dataset Strategy's
versioning, integrity, and long-term-availability requirements cannot be met by this
distribution as it stands. Accordingly, the versioning requirement is **not satisfied**.

This conclusion is independent of MPDD's licensing (separately **resolved** as verified
CC BY-NC-SA 4.0) and of MPDD's scientific suitability (separately assessed as strong).
It concerns **only** versioning and archival stability.

**Remaining blockers (versioning/archival specifically):**

1. **No official version identifier** (no version number, no release tag).
2. **No persistent identifier** (no DOI; no Zenodo/Figshare/institutional archive).
3. **No immutable release** (SharePoint share is mutable and unversioned).
4. **No archival long-term-availability guarantee** (single personal share; no
   preservation commitment; Software Heritage status Unverified).

Clearing these would require **author/institution action** (most completely, a
DOI-backed immutable snapshot, or a data-bearing tagged release with a published
checksum), per the qualitative options in §5 — subject to the repository owner's
judgment under the Dataset Strategy.

---

## Closing Statement

This investigation confirms, on verified facts, that MPDD currently has **no citable,
stable, versioned release**: no version number, tag, DOI, or persistent archive, and a
SharePoint-only official distribution. The versioning/archival governance blocker
recorded against MPDD therefore **stands**, and the conclusion is **INSUFFICIENT
VERSIONING EVIDENCE**. The document modifies no ADR, authorizes no selection, and
recommends MPDD nowhere; the provider abstraction and the Inspection, Trust, Review,
Evidence, and Evaluation ownerships are untouched, and no benchmark claim is made.
