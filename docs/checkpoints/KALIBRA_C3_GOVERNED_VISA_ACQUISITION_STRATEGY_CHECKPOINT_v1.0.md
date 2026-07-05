# Kalibra C-3 Governed VisA Acquisition Strategy Checkpoint v1.0

**Status:** Recorded — governed-acquisition strategy checkpoint (no sprint authorized)
**Date:** 2026-07-05
**Repository baseline HEAD:** `769f933 docs: fix c2 evaluation protocol`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document persists the **C-3 Governed VisA Acquisition Strategy** review. It is a
strategy-definition checkpoint only. It authorizes no sprint, implements no code,
downloads no dataset, creates no manifests or hashes, and modifies no ADR, Dataset
Strategy, or Evaluation Strategy.

It specializes the governed-acquisition obligations already recorded in the
[Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md), the
[C-1 Closure Checkpoint](KALIBRA_C1_DATASET_SELECTION_CLOSURE_CHECKPOINT_v1.0.md) §4,
and the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md)
§2.1–2.2, against the verified source facts in the
[VisA Licensing & Governance Investigation](../research/KALIBRA_VISA_LICENSING_AND_GOVERNANCE_INVESTIGATION_v1.0.md).
It closes exactly the four self-closable gaps C-1 named: **local sha256 integrity
manifest, pinned dated archive, provenance manifest, immutable split manifest.**

This checkpoint is equivalent in standing to the C-1 Dataset Selection Closure
Checkpoint and the C-2 Evaluation Protocol Fixation Checkpoint. Like them, it must be
reviewed and persisted before any governing document is modified and before any
implementation or acquisition begins.

Throughout, **must**, **must not**, and **hard stop** carry the binding sense
established across the ML Phase 2 documents
([`AGENTS.md`](../../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md`](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md)).

---

## 1. Governed Acquisition Protocol

### 1.1 Acquisition Source

| Tier | Source | Status |
|---|---|---|
| **Official source** | `https://github.com/amazon-science/spot-diff` — Amazon Science repo, ECCV 2022, pinned at commit `2a692ab575001cbde74d402d897a7286086c6199` | **Canonical authority** for identity, license, splits |
| **Canonical archive** | `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar` (ARN `arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar`, AWS Open Data Registry, no AWS account required) | **The one archive Kalibra acquires** |
| **Registry corroboration** | `https://registry.opendata.aws/visa/` | Confirms canonical object, license, managed-by |

- **Mirrors policy — forbidden as a primary source.** No third-party mirror (Kaggle,
  HuggingFace, anomalib cache, academic re-host) may be the acquisition source. A
  mirror may be used **only** as a fallback recovery path **and only if** its bytes
  reproduce the Kalibra-recorded archive sha256 exactly; otherwise it is rejected. A
  mirror never redefines identity, license, or splits.
- **Acceptable alternative (recovery only).** If the S3 object is transiently
  unreachable, retry the same canonical URL. The AWS Open Data Registry ARN is the
  same object, not an alternative. No content substitution is ever acceptable.
- **Unacceptable sources (hard reject):** any re-packaged/re-compressed archive; any
  "cleaned," "resized," or "prepared" redistribution; secondary tooling caches (e.g.
  the anomalib page that misreports the license as CC BY-NC-SA 4.0 — **superseded,
  non-authoritative**); any source that cannot be byte-verified against the recorded
  archive hash.

### 1.2 Canonical Identity

The canonical identity Kalibra must preserve:

- **Dataset name** — VisA (Visual Anomaly).
- **Archive identity** — `VisA_20220922.tar`.
- **Upstream commit authority** — `spot-diff@2a692ab575001cbde74d402d897a7286086c6199`
  (no upstream releases or tags exist).
- **AWS object** — `arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar`.
- **Recorded upstream object metadata (HEAD, 2026-07-01):** `Content-Length:
  1929840640`, `Last-Modified: 2022-09-22T19:23:39Z`, `Content-Type:
  application/x-tar`, ETag `05c830591a1172938cb714895c9e0cfb-113`.
- **Content** — 10,821 high-resolution images (9,621 normal, 1,200 anomalous), 12
  objects across 3 domains, image-level and pixel-level labels, published split CSVs
  and preparation scripts (1-class and 2-class setups).

### 1.3 Acquisition Workflow (sequence, not implementation)

1. **Pin the upstream commit** — record `spot-diff@2a692ab…` as the identity/license/
   split authority.
2. **Fetch the canonical archive** from the S3 URL to an **immutable, read-only**
   source location.
3. **Compute the archive sha256** over the raw `.tar` bytes → this becomes the Kalibra
   archive-of-record hash.
4. **Verify against recorded upstream metadata** as a coarse gate: `Content-Length:
   1929840640`, `Last-Modified: 2022-09-22T19:23:39Z`, `Content-Type:
   application/x-tar`, ETag `05c830591a1172938cb714895c9e0cfb-113`. The ETag is a
   **113-part multipart digest, not a content sha256** — it is a corroborating signal
   only, never the integrity anchor.
5. **Extract** into a separate, treated-as-immutable extracted tree (source archive is
   never mutated or deleted).
6. **Generate the per-file sha256 manifest** over the extracted tree.
7. **Adopt the published split CSVs verbatim** from the pinned commit → build the
   immutable split manifest with per-file hashes (train = sound only; validation =
   mixed slice; test = mixed + pixel GT — per C-2 §2.1).
8. **Write the provenance manifest** (§3) and **the attribution/license record**.
9. **Freeze** — the acquisition is complete only when archive hash, per-file manifest,
   split manifest, and provenance record all exist and cross-reference each other.

No step in this list is executed by this checkpoint. It defines the order the future
acquisition sprint must follow.

---

## 2. Integrity Policy

- **Primary anchor — archive sha256.** A single sha256 over the raw `VisA_20220922.tar`
  bytes is the root of trust. Kalibra generates it because upstream publishes no strong
  checksum (verified gap).
- **Per-file hashing — mandatory.** Every extracted file (images, masks, CSVs,
  `image_anno.csv`) gets a sha256 in a per-file manifest. This is what makes "missing
  file" and "silently altered file" detectable.
- **Split-manifest hashing — mandatory.** Each partition's exact per-class image
  membership is pinned with per-file sha256 (C-2 §2.1). The split manifest itself is
  hashed; **its hash is the evaluation's identity** — if it changes, the result is a
  *new* evaluation, never a re-run.
- **ETag — corroboration only.** The multipart ETag (`…-113`) and `Content-Length` are
  used as a cheap pre-check, explicitly **not** as the content digest.
- **Verification workflow.** Re-acquisition or re-use must: (a) recompute archive
  sha256 and match; (b) recompute per-file hashes and match the manifest set exactly
  (no additions, no removals, no drift); (c) recompute split-membership hashes and
  match. Any mismatch triggers the Failure Policy (§7). Integrity verification is a
  precondition for *every* downstream read, not a one-time gate.
- **Deterministic hashing policy.** Hashing reuses Kalibra's existing deterministic
  content-hashing convention (the same content/configuration hashing already proven in
  the Sprint 1H substrate, [`src/frameworks/model_artifact.py`](../../src/frameworks/model_artifact.py))
  so acquisition integrity and runtime replay speak the same language.

---

## 3. Provenance Policy

The provenance manifest is mandatory and must capture, at minimum:

| Field | Recorded value / rule |
|---|---|
| **Acquisition source** | Official repo `amazon-science/spot-diff` @ `2a692ab…` + canonical S3 archive URL |
| **Archive URL** | `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar` |
| **Acquisition date/timestamp** | UTC timestamp of the actual fetch (recorded at acquisition time) |
| **Upstream identifiers** | Archive name `VisA_20220922`; repo commit `2a692ab…`; AWS ARN; DOI `10.1007/978-3-031-20056-4_23`; arXiv `2207.14315` |
| **License** | Dataset: **CC BY 4.0** (`LICENSE-DATASET`); utility code: **Apache-2.0** (`LICENSE`); repo `NOTICE` |
| **Attribution** | Zou, Jeong, Pemula, Zhang, Dabeer — "SPot-the-Difference…", ECCV 2022 (LNCS pp. 392–408); AWS AI Labs / KAIST; copyright Amazon.com, Inc. or affiliates. **CC BY 4.0 requires credit + license reference + indication of changes** — this is a standing obligation on every derived/redistributed artifact. |
| **Upstream publication** | ECCV 2022 / Springer LNCS; Amazon Science page; ECVA PDF |
| **Local repository identity** | Kalibra archive sha256, per-file manifest hash, split manifest hash, local governed layout path |
| **Source-disagreement note** | Record that the CC BY-NC-SA 4.0 secondary claim is superseded by official CC BY 4.0 (so the resolution is auditable, per investigation §6). |

Rule: **claim and provenance travel together.** No image, tensor, or metric may later
be presented without a traceable path back to this manifest (aligns with C-2 §2.5
reporting requirements).

---

## 4. Local Dataset Layout (governed, defined — not created)

A single governed dataset root, with a strict immutable/derived boundary:

```
data/visa/                          # governed dataset root
├── source/
│   └── VisA_20220922.tar           # IMMUTABLE source archive, read-only, never mutated/deleted
├── extracted/                      # extraction of the archive, treated as immutable
│   └── … (upstream tree, verbatim)
├── manifests/
│   ├── archive.sha256              # root-of-trust archive hash
│   ├── files.sha256                # per-file integrity manifest
│   └── splits/                     # immutable per-class train/val/test membership + per-file hashes
├── provenance/
│   └── provenance.json             # §3 record + attribution/license
└── derived/                        # FUTURE artifacts (preprocessed tensors, PaDiM stats) — separate, regenerable, never confused with source
```

- **`source/` and `extracted/` are the immutable dataset-of-record.** `manifests/` +
  `provenance/` are the governance envelope. `derived/` is the only writable,
  regenerable zone.
- Large binaries are **not committed to git** (consistent with `.gitignore` posture);
  the manifests and provenance record are the committed, reviewable evidence. Storage
  policy for the bytes themselves is an acquisition-sprint decision, not fixed here.
- *No directory is created by this checkpoint.*

---

## 5. Versioning Policy

- **Upstream dataset version** — none formal upstream (no DOI, no release tag). Kalibra
  pins the **dated archive `VisA_20220922`** + repo commit `2a692ab…` as the effective
  upstream version. Registry update frequency is "Not updated," so this is stable.
- **Acquisition version** — Kalibra assigns its own governed acquisition version (e.g.
  `visa-acq-v1`) keyed to the archive sha256. The **hash is the true version**; the
  label is human-facing.
- **Local governed version** — the tuple `(archive sha256, files-manifest hash,
  split-manifest hash, provenance hash)`. Any change to any element = a new local
  governed version, full stop.
- **Future upgrade policy** — if upstream ever republishes (new dated archive, DOI, or
  release), that is a **new acquisition** under a new version, side-by-side, never an
  in-place overwrite. Prior versioned acquisitions remain intact so old evidence stays
  reproducible. Migration of the evaluation to a new version is a separate authorized
  decision.

---

## 6. Reproducibility

Another researcher reproduces the acquisition with **only**: (1) the canonical S3
archive URL; (2) the recorded archive sha256; (3) the pinned repo commit `2a692ab…`;
(4) the published split convention recorded verbatim; (5) this protocol. They fetch →
hash-match the archive → extract → regenerate the identical per-file and split
manifests → obtain a byte-identical governed dataset. If their hashes match Kalibra's,
reproduction is proven; if not, they have a *different* dataset and must not treat it
as VisA-of-record. No trust in Kalibra's copy is required — only the public archive and
the recorded hashes.

---

## 7. Failure Policy

| Failure | Required response |
|---|---|
| **Archive hash mismatch** | **Hard stop.** Reject the bytes. Do not extract, do not use. The canonical archive is presumed immutable; a mismatch means a wrong/corrupted/tampered source. No acquisition proceeds. |
| **Missing files** | **Hard stop.** Per-file manifest incomplete → acquisition invalid. No partial dataset is ever promoted to governed status. |
| **Changed upstream archive** | Treat as a **new dataset**, not an update. Do not overwrite. Record the discrepancy, open a new versioned acquisition decision (§5). Existing governed version and its evidence remain valid and untouched. |
| **Split mismatch** | **Hard stop on evaluation.** A split-manifest hash change invalidates any result tied to the old split (C-2 §2.1): it is a *new* evaluation identity, never a silent re-run. Re-derive splits verbatim from the pinned commit and re-hash. |
| **Provenance mismatch** | **Hard stop.** Missing/inconsistent provenance (source, license, attribution, hashes) blocks use. Governance-incomplete data is inadmissible regardless of integrity — claim and provenance must travel together. |

Governing principle: **fail closed.** Any unresolved integrity, completeness, split, or
provenance defect blocks all downstream use (preprocessing, fitting, evaluation,
evidence). No degraded-mode acquisition exists.

---

## 8. Future Integration (no architecture change)

The governed acquisition plugs into the existing Sprint-1H substrate without altering
any seam:

- **Preprocessing** — consumes `extracted/` images through the existing deterministic
  image→CHW-tensor contract by contract id; writes only into `derived/`.
- **Model training (PaDiM, offline)** — fits per-class Gaussians on the **train
  (sound-only)** partition of the split manifest; the fit is pinned by split hash +
  feature-subsample seed (C-2 §2.2).
- **ONNX export** — the exported PaDiM `.onnx` carries its artifact hash and references
  the governed dataset/split hashes as inputs, using the existing model_artifact
  hashing.
- **Evaluation** — reads **only** the governed input tuple (dataset+integrity manifest,
  split manifest, model artifact, preprocessing/output-mapping contract ids, config),
  exactly as C-2 §2.2 already mandates. It never touches raw images outside this
  envelope.
- **Evidence** — every recorded figure carries dataset version + split-manifest hash +
  provenance reference (C-2 §2.5). The acquisition manifests *are* the evidence anchors.

**Architecture remains unchanged.** The seams
(`InspectionInferenceProvider`, `InspectionPrediction`, `transform_prediction`) are
untouched; acquisition only supplies governed inputs to them.

---

## 9. Readiness Decision

```text
C-3 GOVERNED ACQUISITION STRATEGY — DEFINED.

- Acquisition source, integrity, provenance, layout, versioning,
  reproducibility, and failure policy are fully specified.
- Nothing acquired. No archive fetched, no hash computed, no manifest
  or split created, no code written, no documentation modified.
- The strategy closes exactly the four self-closable gaps C-1 named
  (archive hash, pinned archive, provenance manifest, split manifest);
  the four irreducible upstream limitations (no DOI/version tag, no
  upstream checksum, incomplete annotation-process docs, proxy domain)
  remain recorded, not closed.
- Ready for repository-owner review.
```

---

## 10. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no acquisition**
- **no download**
- **no implementation**
- **no manifests**
- **no hashes**
- **no documentation modified** (no ADR, no Dataset Strategy, no Evaluation Strategy)
- **strategy only**

It changes no governed logic, no runtime, no provider, no dataset, no evaluation
harness, and no authorization document. It does not present the placeholder model's
behavior as a scientific result, and Kalibra does not yet perform real defect
detection. The four irreducible upstream limitations (no DOI / formal version tag, no
published strong upstream checksum, incomplete annotation-process documentation, proxy
domain) remain recorded, not closed.

---

## 11. Next Natural Step

```text
Review this checkpoint.

Then update any governing documentation if required.

Only afterwards authorize the governed acquisition sprint.
```

No governing document is updated in this task. The persisted checkpoint must be
reviewed before any governing document is modified.
