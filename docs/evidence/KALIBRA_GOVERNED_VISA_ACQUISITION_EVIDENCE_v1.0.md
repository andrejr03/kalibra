# Kalibra Governed VisA Acquisition Evidence v1.0

**Status:** Recorded — governed acquisition evidence only
**Date:** 2026-07-05
**Scope:** Acquisition infrastructure and acquisition evidence only

## Canonical Source Used

- Official repository: `https://github.com/amazon-science/spot-diff`
- Pinned repository commit: `2a692ab575001cbde74d402d897a7286086c6199`
- Canonical archive URL: `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar`
- AWS object identity: `arn:aws:s3:::amazon-visual-anomaly/VisA_20220922.tar`
- Mirrors used: none

## Archive Metadata

- Archive filename: `VisA_20220922.tar`
- Archive size: `1929840640`
- Archive SHA-256: `2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362`
- Last-Modified: `Thu, 22 Sep 2022 19:23:39 GMT`
- Content-Type: `application/x-tar`
- ETag: `"05c830591a1172938cb714895c9e0cfb-113"` (corroboration only, not SHA-256)
- Metadata record: `data/visa/manifests/archive_metadata.json`

## Generated Acquisition Records

- Archive hash record: `data/visa/manifests/archive.sha256`
- Per-file hash manifest: `data/visa/manifests/files.sha256`
- Per-file manifest SHA-256: `a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c`
- Split manifests: `data/visa/manifests/splits/train.csv`, `validation.csv`, `test.csv`
- Split manifest SHA-256 values:
  - train: `9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736`
  - validation: `79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5`
  - test: `2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510`
- Provenance record: `data/visa/provenance/provenance.json`
- Provenance SHA-256: `01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0`
- Attribution/licensing record: `data/visa/provenance/ATTRIBUTION.md`
- Attribution SHA-256: `1b09f03660d97ac5f2225a1a4f3cb37930bd55778ee1027826d6770bcf30af12`

## Split Manifest Summary

- Train image rows: `3849`; labels: `{'normal': 3849}`
- Validation image rows: `2164`; labels: `{'anomaly': 240, 'normal': 1924}`
- Test image rows: `4328`; labels: `{'anomaly': 480, 'normal': 3848}`
- Split policy: official upstream split CSV membership from the pinned commit; no training, fitting, evaluation, metric, or operating point was executed.

## Provenance And Attribution

- Dataset license recorded: CC BY 4.0.
- Utility code license recorded: Apache-2.0.
- NOTICE requirement recorded: upstream NOTICE obligations must be preserved for applicable utility-code redistribution.
- DOI recorded: `10.1007/978-3-031-20056-4_23`.
- arXiv recorded: `2207.14315`.
- Secondary CC BY-NC-SA claims are recorded as superseded by the official CC BY 4.0 dataset license record.

## Fail-Closed Verification

The acquisition tooling self-test verified hard-stop behavior for:
- archive hash mismatch
- missing file
- changed file
- split hash mismatch
- provenance mismatch

The governed verification also recomputed the archive hash, every extracted file hash, every split manifest hash, provenance hash, and attribution hash before this evidence record was written.

## Local Governed Version Identity

```text
visa-acq-v1
archive_sha256=2eb8690c803ab37de0324772964100169ec8ba1fa3f7e94291c9ca673f40f362
files_manifest_sha256=a01e02b043349d78b9dc958b12779fb48ccc30c0609719c739801a8dc503246c
train_split_sha256=9fa6abf23a487075bbe8f81becbfce471bbfc94e6e4ebc3f2cdf74db0abac736
validation_split_sha256=79e6e3bf99589146143927e1e7861bb2f2b9c4b2502f4da8d8ecc3a274769cc5
test_split_sha256=2d86ae7fa4cffe7f5f4aeb89f2c9c23351f44413da5d8aa0d5a3628a1c505510
provenance_sha256=01933f8b335a520c5a22a0f9f38eb8544429343d580d3646855eae575de639d0
```

## Explicit Non-Claims

- No PaDiM training or fitting was performed.
- No model was exported.
- No preprocessing was changed.
- No inference provider was changed.
- No output mapping was changed.
- No Trust, Review, Evidence Engine, Evaluation Engine, runtime, integration, or prototype UI code was modified.
- No evaluation was executed.
- No metric, benchmark, calibrated-confidence statement, scientific claim, product claim, or architecture change is made by this evidence record.
