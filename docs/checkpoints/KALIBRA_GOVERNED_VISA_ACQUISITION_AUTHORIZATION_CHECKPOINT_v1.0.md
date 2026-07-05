# Kalibra Governed VisA Acquisition Authorization Checkpoint v1.0

**Status:** Recorded — bounded implementation-authorization checkpoint (authorization planning only; no sprint executed)
**Date:** 2026-07-05
**Repository baseline HEAD:** `d44d9c4 docs: define governed visa acquisition strategy`
**Branch:** `codex/initial-engineering-skeleton`

## About This Document

This document authorizes the **bounded scope** of a future Governed VisA Acquisition
implementation. It is authorization planning only. It downloads no data, implements no
tooling, generates no hashes or manifests, and modifies no ADR, Dataset Strategy,
Evaluation Strategy, or Implementation Authorization gate.

It draws its authority from the now-normative governed-acquisition rules recorded in
the
[Dataset Strategy](../KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md) §8, the
[C-3 Governed VisA Acquisition Strategy Checkpoint](KALIBRA_C3_GOVERNED_VISA_ACQUISITION_STRATEGY_CHECKPOINT_v1.0.md),
the [Dataset Selection ADR](../KALIBRA_ML_PHASE_2_DATASET_SELECTION_ADR_v1.0.md), the
[Evaluation Strategy](../KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md), and the
[C-2 Evaluation Protocol Fixation Checkpoint](KALIBRA_C2_EVALUATION_PROTOCOL_FIXATION_CHECKPOINT_v1.0.md).

This checkpoint defines **what a future acquisition sprint is allowed to do**, what it
is **forbidden** to do, what it must **produce**, and how it must be **validated**. It
does not perform the sprint. It is equivalent in standing to the C-1, C-2, and C-3
checkpoints and must be reviewed before any implementation prompt is generated.

Throughout, **must**, **must not**, **authorized**, and **forbidden** carry the binding
sense established across the ML Phase 2 documents.

---

## 1. Authorization Decision

```text
READY TO AUTHORIZE — Governed VisA Acquisition implementation
```

The authorization is **strictly limited to acquisition infrastructure and acquisition
evidence**. It grants no permission to preprocess, fit, export, evaluate, or claim.

**Basis for readiness:**

- The governed acquisition strategy is fully defined and is now **normative** in the
  Dataset Strategy §8 (source, archive identity, SHA-256 integrity anchor, immutable
  split manifests, provenance/attribution record, versioning, fail-closed behavior).
- **VisA is SELECTED** as the governed proxy dataset (C-1), with verified **CC BY 4.0**
  licensing and a canonical AWS Open Data archive.
- The **C-2 evaluation protocol** already depends on exactly these acquisition outputs
  (governed dataset + local integrity manifest + immutable split manifest) as its
  pinned input tuple, so producing them unblocks C-2 without pre-empting it.
- The four self-closable governance gaps (archive hash, pinned archive, provenance
  manifest, split manifest) are precisely what this acquisition closes; the four
  irreducible upstream limitations remain recorded, not closed, and are out of scope.

---

## 2. Authorized Future Scope

If and when the acquisition sprint is authorized by a bounded implementation prompt, it
may do **only** the following, in the mandatory sequence of Dataset Strategy §8 /
C-3 §1.3:

- fetch the canonical VisA archive from the official S3 URL
  (`https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar`);
- store the immutable source archive locally, read-only;
- compute the archive SHA-256 (root-of-trust integrity anchor);
- extract into a separate, treated-as-immutable extracted tree (source never mutated);
- compute the per-file SHA-256 manifest over the extracted tree;
- adopt the upstream split CSVs verbatim from the pinned commit
  (`spot-diff@2a692ab575001cbde74d402d897a7286086c6199`);
- generate immutable train / validation / test split manifests with per-file hashes
  (train = sound only; validation = mixed slice; test = mixed + pixel GT, per C-2 §2.1);
- generate the provenance manifest (§3 of C-3);
- generate the attribution / license record (CC BY 4.0 dataset; Apache-2.0 utility code);
- generate an acquisition evidence report under `docs/evidence/`;
- verify fail-closed behavior for every mismatch class (§5, §7 of C-3).

Nothing beyond this list is authorized.

---

## 3. Forbidden Scope

The acquisition sprint **must not**, under any circumstances:

- perform model training;
- perform PaDiM fitting;
- change preprocessing implementation;
- perform ONNX export;
- change any inference provider;
- change output mapping;
- execute any evaluation;
- generate any benchmark;
- produce any scientific claim;
- produce any product / product-readiness claim;
- add or change UI/CLI integration **unless strictly required for acquisition
  validation** (e.g. a minimal verification entrypoint), and never as product surface;
- commit dataset binaries (source archive or extracted images) to git.

Any of these would exceed the acquisition boundary and requires its own separate
authorization gate.

---

## 4. Required Implementation Outputs

The future implementation is expected to produce the following governed layout (defined
here, **not created now**):

```text
data/visa/source/                   # immutable source archive (VisA_20220922.tar)
data/visa/extracted/                # extracted tree, treated as immutable
data/visa/manifests/                # archive.sha256, files.sha256
data/visa/manifests/splits/         # immutable per-class train/val/test manifests + hashes
data/visa/provenance/               # provenance.json + attribution/license record
data/visa/derived/                  # FUTURE regenerable artifacts (empty at acquisition)
docs/evidence/                      # acquisition evidence report
```

**Commit policy for generated files:**

| Artifact | Disposition |
|---|---|
| `data/visa/source/` archive binary | **Untracked / gitignored** — never committed |
| `data/visa/extracted/` image binaries | **Untracked / gitignored** — never committed |
| `data/visa/derived/` artifacts | **Untracked / gitignored** — regenerable |
| `data/visa/manifests/**` (hashes, split manifests) | **Committed if lightweight** — reviewable evidence |
| `data/visa/provenance/**` (provenance, attribution/license) | **Committed** — governance record |
| `docs/evidence/` acquisition report | **Committed** — evidence of a clean acquisition |

The manifests, provenance, and evidence report are the committed, reviewable proof of a
governed acquisition; the bytes themselves stay local.

---

## 5. Validation Requirements For Future Implementation

The acquisition sprint must validate, and its evidence report must demonstrate, that:

- the **canonical source** was used (official S3 URL + pinned commit; no mirror);
- the **archive SHA-256** was generated and recorded;
- the **per-file SHA-256 manifest** was generated over the full extracted tree;
- the **immutable split manifests** (train/validation/test, per class) were generated
  with per-file hashes, and each split manifest is itself hashed;
- the **provenance record** is complete (source, timestamp, URL, upstream identifiers,
  license, publication, local identity, source-disagreement note);
- the **attribution / license record** is complete (CC BY 4.0 + Apache-2.0 + NOTICE);
- **no source mutation** occurred (source and extracted trees are byte-stable);
- there is **no derived/source mixing** (`derived/` is separate and regenerable);
- **fail-closed behavior** holds for archive-hash mismatch, missing files, changed
  upstream archive, split mismatch, and provenance mismatch (C-3 §7);
- **no downstream ML / evaluation / model code was touched** — the runtime seams
  (`InspectionInferenceProvider`, `InspectionPrediction`, `transform_prediction`) are
  unchanged.

---

## 6. Git / Storage Policy

- **Large dataset binaries must not be committed.** The source archive
  (`VisA_20220922.tar`, ~1.93 GB) and the extracted image tree must never enter git
  history.
- The **source archive and extracted dataset must remain local governed artifacts**,
  reproducible from the canonical S3 URL and recorded hashes by any researcher.
- **Manifests, provenance, and the evidence report may be committed** provided they are
  lightweight (hash lists, JSON records, markdown report).
- **`.gitignore` updates may be authorized only if required** to prevent accidental
  binary commits (e.g. ignoring `data/visa/source/`, `data/visa/extracted/`,
  `data/visa/derived/`). Any such change is minimal and scoped strictly to that purpose.

---

## 7. Readiness Decision

```text
READY — the repository is ready for a bounded Governed VisA Acquisition
implementation prompt.

- Authorized scope: acquisition infrastructure and acquisition evidence only.
- Forbidden scope: all ML, evaluation, export, provider, claim, and product work.
- Required outputs, storage policy, and validation requirements are defined.
- Nothing acquired, downloaded, hashed, manifested, or implemented by this
  checkpoint. No normative document modified.
```

---

## 8. Scope Boundaries and Explicit Non-Claims

This checkpoint records:

- **no acquisition**
- **no download**
- **no implementation**
- **no manifests**
- **no hashes**
- **no model training / fitting / export / evaluation**
- **no scientific or product claim**
- **no documentation modified** (no ADR, Dataset Strategy, Evaluation Strategy, or
  Implementation Authorization change)
- **authorization planning only**

It changes no governed logic, runtime, provider, dataset, evaluation harness, or
authorization document, and Kalibra does not yet perform real defect detection.

---

## 9. Next Natural Step

```text
Generate the bounded implementation prompt for Governed VisA Acquisition.
```

No governing document is updated in this task. The persisted authorization checkpoint
must be reviewed before the implementation prompt is generated.
