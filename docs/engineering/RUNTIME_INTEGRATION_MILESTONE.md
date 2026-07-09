# Runtime Integration Milestone

**Date:** 2026-07-07
**Repository baseline tag:** `ml-phase-2-complete`

## 0. Baseline Confirmation

The review was performed against the actual repository state, not the narrative alone.
Independent inspection confirms:

- The repository HEAD is `9c8e618 feat: retire canonical placeholder runtime`. The working
  tree is **clean** (no uncommitted changes).
- The baseline tag `ml-phase-2-complete` resolves to HEAD `a9743b4`. Phase 3 spans
  **11 commits** from baseline to HEAD.
- The canonical provider ([`src/inspection/providers_onnx.py`](../../src/inspection/providers_onnx.py))
  now defaults to `governed_padim_session_configuration()` and raises
  `InspectionExaminationFailure("ONNX provider model reference is not governed")` for any
  non-PaDiM reference. The placeholder identity model is reachable only through the
  explicit, non-canonical `FixtureOnlyPlaceholderProvider`.
- The runtime output scale
  ([`src/frameworks/output_mapping.py`](../../src/frameworks/output_mapping.py)) canonical
  alias `RAW_MEASURE_SCALE` resolves to `PADIM_RAW_MEASURE_SCALE = "padim_anomaly_map_max_v1"`.
- The governed PaDiM ONNX artifact (`artifacts/padim/model.onnx`, SHA-256
  `0437ae28…741a`, independently re-hashed during this review) is loaded by the canonical
  path.
- Runtime-equivalence artifacts are byte-stable (independently re-hashed during this
  review; all three match the recorded evidence exactly).

The Phase 3 opening record's central premise — *"the real learned signal is
offline-only; the runtime carries the placeholder"* — has been **inverted by execution**:
the runtime now carries the real learned signal, and the placeholder survives only as a
fixture.

---

## 1. Phase 3 Objective Achievement

### 1.1 What ML Phase 3 was created to accomplish

The Phase 3 Architecture record
defined a single, bounded objective (§3):

> *The canonical `inspect()` path must carry the real learned PaDiM signal end-to-end at
> runtime — deterministically, governed, and replay-verified — with the placeholder
> retired, and with demonstrated equivalence to the offline C-6 result.*

The record further defined **completion by equivalence and governance, not by any
improvement in metrics** (§7), and explicitly bounded the phase as a **transport /
integration** achievement, not a scientific or product one (§3).

### 1.2 Assessment by dimension

**Engineering — ACHIEVED.** The five-task capability ordering (§6) was executed in
sequence, each behind its own governance approval + completion record pair. The engineering
center of gravity moved from `scripts/` into the runtime seam exactly as planned: export →
offline equivalence verification → provider wiring → runtime-equivalence evidence →
placeholder retirement. Every task's completion record recorded PASS; every required
validation command was run and recorded; the test suite grew from 479 (Phase 2 close) to
**503 passing** at HEAD.

**Architecture — ACHIEVED (zero architectural drift).** This is the decisive architectural
property of the phase. The opening record declared (§4.1) that Phase 3 should require
*no architectural delta* and that any apparent need for one would be a red flag. Independent
`git diff` of the full Phase 3 lineage (`ml-phase-2-complete..HEAD`) confirms:

- **Only four `src/` files changed:** `src/frameworks/output_mapping.py`,
  `src/inspection/providers_onnx.py`, `src/inspection/__init__.py`,
  `src/inspection/domain.py`.
- **Zero downstream-domain changes:** `git diff --stat` for `src/trust`, `src/review`,
  `src/evidence`, `src/evaluation`, `src/integration`, `src/prototype_ui` is **empty**.
- **The prediction-contract owner is untouched:** `src/inspection/engine.py`
  (`transform_prediction`) has **zero diff** across the entire phase.

The change surface is exactly the seam-local surface the opening record approved
(§4.2): output mapping, provider wiring, and the canonical/fixture split. No new domain,
seam, or contract shape was created.

**Runtime — ACHIEVED.** The canonical `inspect()` path now executes the governed PaDiM ONNX
artifact through the existing `model_loader.load_governed_model` →
`ProviderPrivateInferenceSession` substrate. The placeholder identity model no longer
participates in the canonical flow; it survives only behind the explicit
`FixtureOnlyPlaceholderProvider` seam for legacy fixture tests. Runtime equivalence to the
offline C-5/C-6-observable signal is demonstrated across all 6,492 governed samples at
machine-epsilon deviation.

**Governance — ACHIEVED.** Every capability ran under its own governance approval + completion
record pair, following the public project documentation workflow. The hash-anchored provenance chain now
extends unbroken from archive → files → splits → C-4 training → C-5 inference → C-6
evaluation → ONNX export → export equivalence → runtime integration → runtime equivalence →
placeholder retirement. Fail-closed validation is enforced at every seam: any hash drift,
schema drift, opset/IR mismatch, contract mismatch, or unverified artifact raises
`InspectionExaminationFailure`.

**Scientific continuity — ACHIEVED (equivalence, not advancement).** Phase 3's scientific
contribution is exactly what the opening record declared (§1.4): proving that the
*same* offline C-6 signal survives the crossing into the runtime **unchanged**. The
runtime-equivalence evidence confirms this — the integrated path reproduces the offline
anomaly measure and localization at ~7.1e-15 absolute deviation (float64 machine epsilon),
four to five orders of magnitude inside the pre-declared 1e-12 tolerance. No new scientific
claim was made and none was needed.

### 1.3 Objective achievement verdict

Phase 3's bounded integration objective is **achieved in full**. The defining property — a
runtime that carries the real learned signal, equivalent to C-6, governed and replayable,
placeholder retired — is objectively true and evidenced. The phase is a crossing, not a
discovery, and the crossing is complete.

---

## 2. Runtime Assessment

An honest assessment of the runtime today, verified against code and independently re-hashed
artifacts.

### 2.1 What executes today (real, canonical)

- **The canonical `inspect()` path loads and executes the governed PaDiM ONNX artifact.**
  `OnnxInspectionInferenceProvider()` defaults to
  `governed_padim_session_configuration()` (`kalibra-padim-onnx-export-v1`), loads
  `artifacts/padim/model.onnx` (SHA-256 `0437ae28…741a`) through
  `model_loader.load_governed_model`, and obtains a `ProviderPrivateInferenceSession`.
- **The full governed chain executes end-to-end with real signal:**
  stabilized image → governed feature extraction → `InspectionInferenceProvider.predict`
  → ONNX Mahalanobis + anomaly-map-max + argmax-region → `map_padim_onnx_outputs` →
  `InspectionPrediction` (raw measure `padim_anomaly_map_max_v1`, localization
  `padim_raw_anomaly_map_argmax_region_v1`) → `InspectionEngine.transform_prediction` →
  `RawInspectionResult` → Trust → Review → Evidence → Evaluation.
- **Determinism is real and proven.** CPUExecutionProvider, `exact_order`, intra/inter = 1,
  `ORT_DISABLE_ALL`. A complete second runtime load + execution is byte-identical
  (`run_hash` comparison `true`).
- **Equivalence is real and proven.** Across all 6,492 governed samples, the runtime
  reproduces the offline C-5 anomaly map and raw measure at 7.1e-15 absolute deviation and
  the localization at exactly 0.0 — inside the pre-declared `{1e-12, 1e-12, 0.0}` tolerance.
- **Governance is real and dense.** Loading verifies the model SHA-256, seven Task-1 / C-4 /
  C-5 governance-record hashes, opset 18, IR 10, the preprocessing-not-in-ONNX declaration,
  the equivalence identity, and the export/equivalence replay status — before session
  construction.

### 2.2 What changed since ML Phase 2

| Aspect | Phase 2 close | Phase 3 close |
| --- | --- | --- |
| Canonical model | placeholder identity model | governed PaDiM ONNX artifact |
| Provider default | placeholder session config | `governed_padim_session_configuration()` |
| Output scale | `placeholder_output_raw_0_100` | `padim_anomaly_map_max_v1` |
| Runtime signal | null scientific behaviour | real learned PaDiM signal |
| Placeholder in canonical path | yes | **no** (fixture-only) |
| Runtime-equivalence evidence | none (signal offline-only) | demonstrated, 6,492 samples |

The single, well-localized disconnection that the opening record identified (§2.4) —
"no governed ONNX export of the real model" — is **closed**.

### 2.3 Whether the runtime now carries the real governed model

**Yes.** Verified by source inspection: the canonical `OnnxInspectionInferenceProvider`
constructs only the PaDiM path (`_model_kind == "padim"`), dispatches `predict()` only to
`_predict_padim`, and the placeholder tokens (`_predict_placeholder`,
`_MODEL_KIND_PLACEHOLDER`, `_placeholder_model_artifact`, `_single_input_name`) are absent
from the canonical class. The canonical path is unambiguously PaDiM-only.

### 2.4 Whether the placeholder is truly retired from the canonical path

**Yes — retired from the canonical path; retained as fixture-only.** This is the honest,
precise boundary:

- **Retired from the canonical runtime `inspect()` path.** The canonical provider rejects
  `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID` with an `InspectionExaminationFailure`. A
  fail-closed regression test (`test_fail_closed_if_placeholder_becomes_canonical_again`)
  ensures the suite breaks if the placeholder ever returns to the canonical path.
- **Retained as an explicit, non-canonical fixture.** The placeholder ONNX fixture
  (`tests/fixtures/inspection/onnx_placeholder/placeholder_identity.onnx`) and the
  `FixtureOnlyPlaceholderProvider` survive so legacy boundary tests can still exercise the
  fixture through a clearly-marked NON-CANONICAL seam. This is fixture-only retention, which
  the opening record explicitly permitted (§4.2.4: "may be retained only as a governed
  test fixture").

The placeholder is therefore **truly retired from the canonical path** in the binding sense,
while remaining available as a test fixture. This is the correct boundary and matches the
phase's success criterion #2.

---

## 3. Scientific Assessment

The four scientific classes are kept strictly separate, per convention.

### 3.1 Scientific capability inherited from ML Phase 2 — UNCHANGED

The C-6 single-seed, VisA-proxy scientific result stands exactly as recorded:

| Metric | Macro mean | Role |
| --- | --- | --- |
| Image AUROC | `0.757826` | primary official |
| Pixel AUROC | `0.865196` | secondary official (background-dominance caveat) |
| AUPRO | `0.555765` | secondary official |
| Precision / Recall / F1 | `0.209019` / `0.714583` / `0.323432` | diagnostic only |

Phase 3 made **no** new scientific claim and modified **no** scientific result. The C-6
evidence is the reference of record and remains the scientific claim boundary.

### 3.2 Runtime capability established by ML Phase 3 — EQUIVALENCE DEMONSTRATED

Phase 3's scientific contribution is **equivalence**, not advancement. Demonstrated:

- The integrated runtime path reproduces the offline C-5 anomaly map, raw measure, and
  localization across **all 6,492 governed samples** (validation 2,164 + test 4,328) at
  machine-epsilon deviation (~7.1e-15 absolute for the continuous signals; exactly 0.0 for
  localization), inside the pre-declared `{1e-12, 1e-12, 0.0}` tolerance declared *before*
  comparison.
- The `InspectionPrediction` contract is verified per-sample across all 6,492 inputs, with
  expected-by-design identifier differences (`raw_measure_scale`, `prediction_id`)
  correctly distinguished from signal mismatches.
- Runtime replay is byte-identical across a complete second load + execution.

This is a genuine, defensible transport achievement: the validated offline signal now
reaches the runtime **unchanged**.

### 3.3 What still has NOT been demonstrated

The following remain **not demonstrated** and are carried forward as deferred debt (see §5):

- **Multi-seed characterization.** Still single-seed (`271828`). No per-class variance,
  confidence intervals, or significance testing. The C-2 §2.5 statistical obligation
  remains unmet.
- **Calibration / Trust qualification.** No calibrated confidence. The raw anomaly measure
  is not and must not be presented as confidence. The runtime `predicted_judgement=DEFECT`
  is contract-required for raw-localization output, **not** threshold-driven and **not**
  calibrated.
- **Domain-of-record performance.** VisA is still a proxy. No metal-part / cross-domain
  performance.
- **Operating-point at runtime.** The validation-derived operating point `2.445569`
  exists only in the offline C-6 evaluation; the runtime path carries the raw measure and
  localization without applying a threshold.

Phase 3 did not attempt any of these, correctly, because each is downstream of a runtime
that carries the real model — which now exists.

---

## 4. Architectural Assessment

### 4.1 Runtime architecture completeness

| Component | State | Evidence |
| --- | --- | --- |
| Provider seam | **Complete.** `InspectionInferenceProvider.predict` unchanged in shape; dispatches to PaDiM. | zero diff on contract; conformance harness passes |
| Model loader | **Complete.** `model_loader.load_governed_model` loads the governed artifact. | unchanged through Phase 3 |
| ONNX runtime | **Complete.** `ProviderPrivateInferenceSession` drives a real `InferenceSession`. | unchanged through Phase 3 |
| Preprocessing boundary | **Complete (contract-recorded, not in-graph).** The preprocessing contract `kalibra-padim-rgb64-biline-float64-patch8-v1` is recorded and required; the runtime reuses the governed offline feature extraction. Preprocessing is intentionally not reimplemented inside the ONNX graph (the graph input is the deterministic full-patch feature tensor). | `preprocessing_reimplemented_in_onnx == False`, fail-closed enforced |
| Feature-extraction boundary | **Complete (reused, not redesigned).** The PaDiM path reuses `scripts.train_padim_baseline.extract_features` with `FitConfig()` — the governed offline extraction. | `feature_extraction_semantics_changed == false` |
| Output mapping | **Complete.** `map_padim_onnx_outputs` maps the four graph outputs (patch distances, anomaly map, raw measure, argmax region) into the unchanged `InspectionPrediction` contract shape. | parallel PaDiM mapping; placeholder path preserved separately |
| Prediction contract | **Complete & unchanged.** No field added, removed, or renamed. `InspectionPrediction` carries the PaDiM raw measure and localization via existing fields. | zero diff on `engine.py` |
| Downstream ownership | **Complete & isolated.** Trust, Review, Evidence, Evaluation, Integration, Prototype UI untouched. | empty `git diff --stat` across Phase 3 |

### 4.2 Whether any substrate work remains

**No substrate work remains for the Phase 3 objective.** The runtime architecture is
complete for carrying the real governed PaDiM signal end-to-end. Every seam the substrate
was designed to provide — provider, loader, session, mapping, contract, downstream
ownership — is now exercised with a real model.

The only honest caveat is the **preprocessing-in-graph gap**: image preprocessing is not
reimplemented inside the ONNX graph; the graph consumes precomputed patch features, and the
runtime performs feature extraction outside the graph. This is a deliberate, governed
design choice (recorded as a contract and fail-closed-enforced declaration), **not** a
substrate defect. It does mean a future phase that wanted a single "image-in →
judgement-out" ONNX artifact would have to bring preprocessing into the graph — but that is
out of Phase 3's scope and is not required for the phase's integration objective.

---

## 5. Remaining Technical Debt

Prioritized from highest to lowest leverage. Each is a deferred obligation, not a defect in
what Phase 3 delivered.

1. **(Highest) Calibration / Trust qualification.** The runtime now carries a real raw
   anomaly measure but presents **no calibrated confidence, no trust qualification, no
   abstention, no drift response**. The runtime `predicted_judgement` is contract-required
   DEFECT for raw-localization output, not a calibrated classification. This is the single
   largest gap between "a runtime that carries real signal" and "a system whose decisions
   carry a defensible trust statement." It is a Trust-domain obligation, correctly deferred
   until a measured integrated baseline exists — which Phase 3 has now established.

2. **Multi-seed characterization.** Still single-seed (`271828`). The C-2 §2.5
   "repeated seeded runs … variance … confidence intervals" obligation remains unmet. Now
   that the runtime carries the real model, multi-seed characterization can be performed
   against the integrated path. Requires its own refit governance approval.

3. **Proxy-domain gap.** VisA is not Kalibra's domain of record (cast-aluminium, CNC,
   gearbox-housing, metal parts). PaDiM is alignment-sensitive; no cross-domain
   generalization is claimed or demonstrated.

4. **PatchCore reserved, not adopted.** The planned second-generation model remains
   reserved. A proven real-map → prediction → evaluation baseline now exists at runtime;
   PatchCore remains future work.

5. **Preprocessing-in-graph.** The ONNX graph consumes precomputed features, not image
   pixels. A future "image-in → judgement-out" artifact would require embedding
   preprocessing in the graph. Not required for Phase 3; recorded for future awareness.

6. **VisA upstream documentation gaps.** No DOI/version tag, no upstream checksum,
   incomplete annotation-process documentation. Recorded, not closed.

7. **Evidence repository size.** The runtime-equivalence report embeds per-sample deviation
   records for all 6,492 samples (~5.6 MB). This is correct (durable, inspectable evidence)
   but is the largest single evidence artifact; worth factoring if repository size grows.

8. **Deployment / UI / monitoring.** Explicitly out of scope per public project documentation (no hosted,
   streaming, live, or operational behaviour). Correctly absent.

Only items 1–4 are genuine scientific/engineering debt that influences future ML phases.
Items 5–8 are recorded awareness, not blocking obligations.

---

## 6. Phase Completion Decision

```text
ML Phase 3 COMPLETE
```

**Technical justification.** Against the eight success criteria the opening record
defined (§7), every criterion is objectively true and evidenced:

1. **Real model at runtime** — ✔ The canonical `inspect()` path loads and executes the
   governed PaDiM ONNX artifact; the provider no longer restricts to the placeholder.
2. **Placeholder retired** — ✔ The placeholder identity model no longer participates in the
   canonical runtime path (fixture-only retention, explicitly permitted).
3. **Export governed and replayable** — ✔ The ONNX artifact is deterministic, hash-anchored,
   provenance-linked, and a second export is byte-identical.
4. **Runtime equivalence demonstrated** — ✔ The runtime reproduces the offline C-5/C-6
   signal across all 6,492 samples within the pre-declared `{1e-12, 1e-12, 0.0}` tolerance,
   with per-sample, per-split, and global evidence.
5. **Runtime replay proven** — ✔ A complete second integrated runtime run is byte-identical.
6. **Governance continuity intact** — ✔ The hash-anchored chain extends unbroken from
   archive through the ONNX artifact to the runtime path; the provider fails closed on
   mismatch.
7. **No architectural drift, no expanded claims** — ✔ Zero downstream-domain diff; zero
   diff on the prediction-contract owner; scientific claim boundary unchanged from C-6.
8. **Full completion evidence persisted** — ✔ Five governance approval + completion record
   pairs and five evidence documents, all committed.

Completion was defined by **equivalence and governance**, not by metric improvement. The
runtime metrics do not differ from C-6 — they reproduce C-6's signal at machine-epsilon
deviation. That is exactly the property the phase was created to defend.

This closure is honest **only because** the deferred debts (§5) are named explicitly and
carried forward — not hidden behind a favorable aggregate. Phase 3 closed the integration
gap; it did not close the calibration, multi-seed, or domain-of-record gaps, and those
remain the obligations of future phases.

**This closure approves nothing.** It does not approve calibration, multi-seed
characterization, PatchCore, or any Phase 4 capability. Each remains behind its own
separate governance gate.

---

## 7. Readiness for ML Phase 4

ML Phase 3 is complete (per §6). The repository is **ready to transition into ML Phase 4**.

The recommended (not approved) architectural objective of ML Phase 4:

```text
Trust Qualification of the integrated runtime: convert the real, raw, uncalibrated PaDiM
anomaly measure — now carried end-to-end at runtime — into calibrated, qualified trust
statements, abstentions, and drift-aware caution, with the evidence obligations the
Trust Qualification Engine requires.
```

Rationale:

- It is the **single largest remaining gap** between a runtime that carries real signal
  (which Phase 3 delivered) and a system whose decisions carry a defensible trust statement
  (Kalibra's defining purpose per public project documentation: "for every inspection decision, determine
  whether that decision can be trusted"). Every other deferred item — multi-seed variance,
  PatchCore, domain-of-record — is downstream of, or parallel to, a trust-qualified runtime.
- The integrated baseline it requires now **exists**. The opening Phase 3 record noted
  that calibration is "correctly deferred until the real model runs in the runtime and a
  measured baseline exists on the integrated path." Phase 3 established exactly that: a
  runtime carrying the real model, equivalent to C-6, with deterministic replay.
- It is a **Trust-domain** responsibility, preserving domain boundaries. The five-domain
  ownership remains intact; Phase 4 would exercise the Trust Qualification Engine against
  the real integrated signal for the first time.

**Parallel / secondary (each its own governance approval):** multi-seed characterization of the
fitted baseline against the integrated path, to begin discharging the C-2 §2.5 statistical
obligation.

**Not recommended as a Phase 4 first step:** PatchCore adoption or domain-of-record
expansion. Both are scientific-payload changes that should follow, not precede, a
trust-qualified runtime.

This recommendation **approves nothing.** It identifies the next engineering frontier
only. Any Phase 4 work requires its own phase-opening architecture record and
governance approval, reviewed and approved by the repository owner, before implementation begins.

---

## 8. Lessons Learned

Recorded to influence future phases.

### 8.1 Runtime integration

- **The seam was ready, and that was the strongest readiness signal.** Phase 3 required no
  architectural delta (§4) because the Sprint 0 / 1A–1H substrate was built to receive a
  real model. The discipline of *building the seam before needing it* — and resisting the
  temptation to re-architect when populating it — is what kept the phase bounded.
- **Equivalence is the integration property; defend it above all.** The phase's existential
  risk (R1, inference-equivalence failure) never materialized because the export, offline
  equivalence, runtime integration, and runtime equivalence were each separately evidenced
  with pre-declared tolerances. The layering of export-fidelity → export-equivalence →
  runtime-equivalence meant a divergence would have been caught at the earliest possible
  stage, not at the runtime.
- **Machine-epsilon equivalence is achievable for a statistical model under DOUBLE
  CPUExecutionProvider.** The float64 Mahalanobis computation survived ONNX export and
  ONNX Runtime execution at ~7.1e-15 deviation. This is a reproducible numerical result, not
  a lucky one — and it justifies the strict `{1e-12, 1e-12, 0.0}` tolerance regime.

### 8.2 Governance

- **The governance approval + completion record pair scales to integration work.** Five
  bounded tasks were delivered without scope creep, each closing exactly what it declared.
  The discipline held even though Tasks 1–2 were offline and Tasks 3–5 touched the live
  runtime — the same workflow served both.
- **Fail-closed density is the governance asset.** The canonical provider verifies the
  model hash, seven governance-record hashes, opset/IR, the preprocessing declaration, the
  equivalence identity, and the replay status *before* session construction. This density is
  what makes "the runtime carries the governed artifact" a verifiable claim rather than a
  narrative one.
- **Immutability contracts across phases work.** Task 5 (placeholder retirement) re-attested
  six SHA-256 digests from Tasks 3–4 as byte-identical, proving that retirement was
  architecture hygiene and not a re-integration. Cross-phase immutability hashing is a
  pattern worth preserving.

### 8.3 Replay

- **Deterministic replay proven, not asserted, at every new boundary.** Export replay,
  export-equivalence replay, runtime-integration replay, runtime-equivalence replay, and
  placeholder-retirement replay — five separate replay proofs, each byte-identical. This is
  the gold standard and is now the baseline expectation.
- **The runtime replay extends the Phase 2 standard through the runtime boundary**, exactly
  as the opening record (§7.5) required. The strongest reproducibility property of the
  repository now holds end-to-end, not just offline.

### 8.4 Evidence

- **Per-sample evidence at scale is durable but heavy.** The 6,492-sample per-sample
  deviation records make the equivalence claims inspectable by an untrusting observer — but
  the ~5.6 MB report is the largest evidence artifact. The trade-off (inspectability vs.
  repository size) is currently correct but should be watched.
- **Expected-by-design differences must be distinguished from signal mismatches.** The
  runtime-equivalence verifier correctly treated `raw_measure_scale` and `prediction_id`
  differences as identifier/provenance differences, not equivalence failures. This is a
  subtle but important governance posture: not every difference is a defect.

### 8.5 governance approval workflow

- **The phase-opening architecture record's non-governance approval held.** Despite defining
  a clear five-task ordering, the opening record approved nothing, and each task
  required its own governance approval. This prevented the phase from collapsing into a single
  unbounded implementation push.
- **Authorizing placeholder retirement *after* runtime equivalence was the correct
  ordering.** Retiring the placeholder before proving runtime equivalence would have left
  no fallback and no equivalence reference. The ordering (prove equivalence, then retire)
  is a reusable principle.

### 8.6 record persistence

- **The public project documentation workflow was followed for every task and for this closure.** Nothing
  lived only in chat. This is the single most important reproducibility property of the
  phase and should be preserved unchanged in Phase 4.
- **Phase-milestone assessments remain valuable.** This review confirms what no individual
  completion record could see: that the five tasks, taken together, closed the
  integration gap without architectural drift and without expanding the scientific claim
  boundary.

### 8.7 Deterministic engineering

- **Write-once governance (`write_governed_bytes`) is effective.** Refusing to overwrite an
  existing artifact with differing bytes makes a second run a no-op or a fail-closed guard,
  never a silent mutation. This pattern should be preserved for all future governed
  artifacts.
- **Canonical/fixture splitting is a clean retirement pattern.** Rather than deleting the
  placeholder (which would have broken legacy tests and lost a useful fixture), Phase 3
  split the surface: canonical = PaDiM-only, fixture-only = explicit non-canonical seam.
  This preserved test coverage while making the canonical boundary unambiguous.

---

## 9. Runtime Maturity Assessment

The four maturity classes are kept strictly independent.

- **Engineering maturity — HIGH.** A production-grade, contract-bound, deterministic,
  fully tested (503 passing), governed, replay-verified runtime that carries a real model
  end-to-end. Fail-closed validation at every seam. Hash-anchored provenance from archive
  to runtime. This is the repository's strongest asset and is now exercised with real
  signal.

- **Runtime maturity — REAL, GOVERNED, EQUIVALENCE-VERIFIED, PLACEHOLDER-RETIRED.** The
  canonical `inspect()` path executes the governed PaDiM artifact through the real ONNX
  Runtime substrate, deterministic and replay-proven, equivalent to the offline C-6 signal
  at machine-epsilon deviation. The placeholder is retired from the canonical path
  (fixture-only retention). The runtime is mature *as a transport for the validated
  offline signal*. It is not mature as a calibrated, trust-qualified, product-ready system.

- **Scientific maturity — BOUNDED, SINGLE-SEED, PROXY-ONLY (unchanged from Phase 2).**
  Phase 3 advanced the *transport* of the scientific signal, not the *science*. The
  scientific claim boundary remains exactly C-6's: single-seed, VisA-proxy, no calibration,
  no confidence intervals, no domain-of-record performance. This is the honest boundary and
  Phase 3 correctly refused to expand it.

- **Product maturity — NONE.** Nothing in the system can be relied upon by a user to detect
  a defect on a real part with a defensible trust statement. The runtime carries a real raw
  measure, but presents no calibrated confidence, no trust qualification, no abstention, no
  drift response, and no product threshold. The prototype surface remains projection-only.
  This is unchanged from the start of Phase 3 and is correct.

---

## 10. Final Recommendation

```text
READY FOR ML PHASE 4
```

**Justification.**

1. **The Phase 3 objective is fully achieved.** The canonical runtime carries the real
   learned PaDiM signal end-to-end, deterministic, governed, replay-verified, equivalent to
   C-6, with the placeholder retired from the canonical path (§6).
2. **No architectural debt was introduced.** Zero downstream-domain diff; zero diff on the
   prediction-contract owner; the change surface is exactly the seam-local surface the
   opening record approved (§4). The substrate is intact and ready for the next
   phase.
3. **The integrated baseline Phase 4 needs now exists.** Trust qualification, multi-seed
   characterization, and any scientific advancement all require a runtime carrying the real
   model. That precondition is now met — for the first time — at HEAD.
4. **The governance discipline is intact and mandatory.** The record/governance approval/
   evidence/replay workflow held across five tasks and will hold for Phase 4.
5. **The deferred debts are explicitly named (§5) and carried forward**, not hidden.
   Closing Phase 3 here is honest because the calibration, multi-seed, and domain-of-record
   gaps are recorded as obligations of future phases.

The repository is ready for ML Phase 4 — **only because** Phase 3 closed the integration
gap without expanding the scientific claim boundary, and the remaining gaps are the honest,
named obligations of trust qualification and scientific characterization, not hidden
defects.

---

## 11. Scope Boundaries and Explicit Non-Claims

This milestone assessment records:

- **No code implemented.** No source, test, script, runtime, or artifact file was created
  or modified by this review. The only working-tree change is the creation of this
  record document.
- **No governance approval granted.** No Phase 4 work, no calibration, no multi-seed
  characterization, no PatchCore adoption, no domain-of-record expansion, and no
  product-facing capability is approved by this review.
- **No roadmap update.** No ADR, Strategy, Evaluation Strategy, or Implementation
  governance approval was modified.
- **No scientific or product claim beyond C-6.** The bounded single-seed VisA-proxy claims
  stand exactly as recorded in the
  C-6 completion record
  and the
  [scientific evaluation evidence](../evidence/SCIENTIFIC_EVALUATION.md).
  Phase 3 demonstrated *equivalence* to that signal at runtime; it did not advance it.
- **Kalibra does not yet perform calibrated, trust-qualified defect detection.** The
  runtime now carries a real raw anomaly measure, but that measure is not calibrated
  confidence, not a trust statement, and not a product threshold. The scientific-claim
  boundary remains single-seed, VisA-proxy, no calibration, no confidence, no
  product-readiness.

The closing boundary is honest only because the deferred debts (§5) and the
not-yet-demonstrated capabilities (§3.3) are named explicitly here.

---

## 12. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (no output) ✔ |
| Test suite | `python3 -m pytest -q` | 503 passed in 12.02s ✔ |
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | `a9743b4` ✔ |
| HEAD | `git log -1 --oneline` | `9c8e618 feat: retire canonical placeholder runtime` ✔ |
| Phase 3 commit count | `git rev-list --count ml-phase-2-complete..HEAD` | 11 ✔ |
| Downstream-domain isolation | `git diff --stat ml-phase-2-complete..HEAD -- src/trust src/review src/evidence src/evaluation src/integration src/prototype_ui` | empty ✔ |
| Prediction-contract owner | `git diff --stat ml-phase-2-complete..HEAD -- src/inspection/engine.py` | empty ✔ |
| PaDiM ONNX model hash | `shasum -a 256 artifacts/padim/model.onnx` | `0437ae28…741a` ✔ |
| Runtime-equivalence report hash | `shasum -a 256 artifacts/runtime/equivalence/runtime_equivalence_report.json` | `90ea3997…6d19` ✔ |
| Runtime-equivalence replay hash | `shasum -a 256 artifacts/runtime/equivalence/runtime_equivalence_replay.json` | `65b414c4…bee8` ✔ |
| Runtime-equivalence hashes hash | `shasum -a 256 artifacts/runtime/equivalence/runtime_equivalence_hashes.json` | `80cce54f…84c` ✔ |

itself.

---

## 13. Next Natural Step

```text
Review this persisted ML Phase 3 milestone assessment before deciding whether to open ML Phase 4.
```

If ML Phase 4 is opened, the recommended (not approved) architectural objective is Trust
Qualification of the integrated runtime (§7). That work requires its own phase-opening
architecture record, reviewed and approved by the repository owner, before any
governance approval or implementation begins. Until then, the runtime carries the real governed
PaDiM signal end-to-end, and every claim remains bounded to the offline single-seed
VisA-proxy evidence recorded in C-6, now demonstrably reproduced at runtime.
