# Runtime Integration Architecture

**Date:** 2026-07-06
**Repository baseline tag:** `ml-phase-2-complete`

## 0. Baseline Confirmation

The baseline was confirmed by independent inspection of the repository at tag
`ml-phase-2-complete`, not by re-reading the closure narrative alone:

- The tag `ml-phase-2-complete` resolves to HEAD `a9743b4 docs: review ml phase 2
  documentation`. The working tree is clean.
- The runtime ONNX provider ([`src/inspection/providers_onnx.py`](../../src/inspection/providers_onnx.py))
  is restricted to `ONNX_PLACEHOLDER_MODEL_REFERENCE_ID = "onnx-placeholder-boundary-model-v1"`
  and raises if handed any other model reference.
- The runtime output scale
  ([`src/frameworks/output_mapping.py`](../../src/frameworks/output_mapping.py)) is
  `RAW_MEASURE_SCALE = "placeholder_output_raw_0_100"`.
- The real ONNX Runtime substrate is genuine and present: `load_governed_model(...)` and
  `ProviderPrivateInferenceSession` in
  [`src/frameworks/model_loader.py`](../../src/frameworks/model_loader.py) construct and
  drive a real `InferenceSession`. That substrate is fed **only** the placeholder model
  today.
- The PaDiM pipeline in `scripts/` records `"onnx_exported": False` and "No ONNX export was
  produced." explicitly in both
  [`scripts/train_padim_baseline.py`](../../scripts/train_padim_baseline.py) and
  [`scripts/padim_inference.py`](../../scripts/padim_inference.py).

The milestone assessment's central finding is therefore verified against code: **the real learned
signal is offline-only; the runtime carries the placeholder.**

---

## 1. Phase 2 → Phase 3 Transition

What fundamentally changes between ML Phase 2 and ML Phase 3, kept in the four separate
capability classes the Architecture & Capability record convention requires.

### 1.1 Engineering

- **Phase 2:** built and proved a governed, deterministic, replay-verified **offline** ML
  pipeline (acquire → train → infer → evaluate) living entirely in `scripts/`, isolated
  from `src/`.
- **Phase 3:** the engineering center of gravity moves **from `scripts/` into the runtime
  seam.** The work becomes *integration* engineering on the existing substrate — export,
  load, provider wiring, output mapping, placeholder retirement — rather than new offline
  pipeline construction. No new domain, contract, or seam is created; the existing seams
  are exercised for the first time with a real model.

### 1.2 Architecture

- **Phase 2:** architecture was declared substantially complete and unchanged; the offline
  pipeline deliberately touched no `src/` domain package.
- **Phase 3:** architecture **remains fixed**. The change is not architectural — it is
  populating a seam that was designed precisely to receive a real model
  (`InspectionInferenceProvider.predict`, the `InspectionPrediction` boundary, the
  `model_loader` / `onnx_session` substrate). Phase 3's defining property is that it should
  require *no* architectural delta (see §4). If it appears to require one, that is a signal
  to stop and re-review, not to proceed.

### 1.3 Runtime

- **Phase 2:** the runtime executed the **placeholder identity model** end-to-end. The real
  ONNX Runtime substrate existed and was proven (Sprint 1F) but only ever loaded the
  placeholder boundary model.
- **Phase 3:** the runtime must, for the first time, **carry genuine learned signal**. The
  canonical `inspect()` path must consume a real exported PaDiM artifact instead of the
  placeholder — with byte-for-byte determinism and full replay preserved.

### 1.4 Scientific capability

- **Phase 2:** produced real, bounded, single-seed VisA-proxy scientific *evidence* offline
  (macro Image AUROC `0.757826`), but that signal never reached the runtime.
- **Phase 3:** does **not** aim to improve the science. It aims to prove that the *same*
  offline scientific signal survives the crossing into the runtime **unchanged**. The
  scientific claim boundary is inherited from C-6 and must not be expanded. Phase 3's
  scientific contribution is *equivalence*, not *advancement*: demonstrating that the
  runtime path reproduces the offline result rather than producing a new one.

**Summary of the transition:** Phase 2 answered "does a real model produce real signal on a
governed dataset?" (yes, offline). Phase 3 answers "does that same signal survive end-to-end
through the production runtime, deterministically and governed?" It is a crossing, not a
discovery.

---

## 2. Current Runtime Assessment

An honest assessment of what the runtime is today, verified against code.

### 2.1 What still executes today (real)

- **The ONNX Runtime substrate is real.** `load_governed_model(...)` constructs a genuine
  `InferenceSession` and executes it behind the provider seam; the Sprint 1F evidence
  demonstrated real session load and execution. This machinery is production-grade and
  deterministic.
- **The full governed chain executes end-to-end:** stabilized image →
  `InspectionInferenceProvider.predict` → `InspectionPrediction` →
  `InspectionEngine.transform_prediction(...)` → `RawInspectionResult` → Trust → Review →
  Evidence → Evaluation. Every seam is live and contract-bound.
- **Determinism, hash-anchoring, and fail-closed validation are real** at every runtime
  boundary.

### 2.2 What is placeholder

- **The model the runtime executes is the placeholder identity model.**
  `providers_onnx.py` is hard-restricted to `onnx-placeholder-boundary-model-v1` and refuses
  any other reference. The runtime output scale is `placeholder_output_raw_0_100`. The
  examiner id is `inspection-placeholder-hash-v1`. The signal carried through the entire live
  chain is **null scientific behaviour** — a deterministic placeholder, not a learned measure.

### 2.3 What is real but disconnected

- **The learned PaDiM baseline** (μ / Σ⁻¹ for 12 VisA classes) is real, fitted,
  replay-proven — and lives only in `scripts/` artifacts. It is **not** an ONNX artifact and
  is **not** reachable from any `src/` runtime path.
- **The offline anomaly measure** (`padim_anomaly_map_max_v1`) and its localization
  (`padim_raw_anomaly_map_argmax_region_v1`) exist only in the offline inference/evaluation
  outputs. The runtime's output mapping does not know them.

### 2.4 What remains disconnected (the gap)

The gap is a **single, well-localized disconnection**: there is no governed ONNX export of
the real PaDiM model, and therefore no artifact for the real ONNX substrate to load. The
substrate is ready to receive a real model; no real model has been handed to it. Everything
else — session machinery, provider seam, prediction contract, downstream domains — is
already in place. Phase 3 is the work of closing exactly this one seam-level gap without
disturbing anything around it.

---

## 3. Runtime Integration Goal

Defined architecturally, not as implementation.

**ML Phase 3's runtime integration goal is: the canonical `inspect()` path must carry the
real learned PaDiM signal end-to-end at runtime — deterministically, governed, and
replay-verified — with the placeholder retired, and with demonstrated equivalence to the
offline C-6 result.**

Successful runtime integration means **all** of the following hold simultaneously:

1. **Real model executes in the runtime.** A governed ONNX artifact derived from the fitted
   PaDiM baseline is loaded by the existing `model_loader`/`onnx_session` substrate and
   executed by `InspectionInferenceProvider.predict` on the canonical path. The placeholder
   restriction in `providers_onnx.py` is lifted/replaced under governance, and the
   placeholder is retired from the canonical flow.

2. **Signal equivalence is demonstrated.** For governed inputs, the runtime path reproduces
   the offline PaDiM anomaly measure and localization to a pre-declared numerical tolerance
   (ideally byte-identical; at minimum a governed, justified tolerance). The runtime does not
   silently produce a *different* number than the offline pipeline.

3. **Determinism and replay are preserved.** The integrated runtime path is deterministic and
   a complete second run is proven identical, matching the Phase 2 replay standard. Governance
   (hash-anchored artifacts, fail-closed validation, provenance) extends unbroken from the
   offline artifacts into the runtime artifact.

4. **The scientific claim boundary is unchanged.** The integrated runtime makes **no**
   scientific claim beyond C-6. It carries the same bounded, single-seed, VisA-proxy signal —
   now at runtime. No calibration, no confidence, no product-readiness is introduced or
   implied.

Integration is a **transport** achievement, not a **scientific** or **product** one.
"Successful" means the runtime now carries what the offline pipeline already proved — nothing
more, nothing less.

---

## 4. Architectural Delta

### 4.1 Components that remain UNCHANGED

Phase 3 must leave the following untouched. Each is inherited intact from ML Phase 2:

- **Dataset governance** — VisA `SELECTED`, pinned archive, per-file manifest, frozen splits.
- **PaDiM training** — the fitted single-seed baseline (μ / Σ⁻¹, seed `271828`) is the input
  to export; it is not re-fit or re-selected in Phase 3.
- **Scientific evaluation (C-6 protocol)** — the frozen C-2 protocol, metrics, and
  operating-point discipline are the *reference* against which runtime equivalence is judged;
  they are not modified.
- **Evidence domain** — the emitter, records, and hash-anchoring contract.
- **Trust domain** — no calibration, no confidence; unchanged and still deferred.
- **Review domain** — unchanged.
- **Evaluation Strategy** — the C-2 evaluation strategy and its statistical obligations are
  unchanged (and multi-seed remains owed, but is *not* a Phase 3 integration concern).
- **Five-domain ownership** — Inspection → Trust → Review → Evidence → Evaluation.
- **Provider seam, `InspectionPrediction` boundary, and `transform_prediction(...)`
  ownership** — the *shapes* are unchanged; only the model behind the seam changes.
- **Prototype UI** — projection-only; no product surface is introduced.

### 4.2 Components that MUST change

The change surface is deliberately minimal and seam-local:

1. **A new governed ONNX export path for the fitted PaDiM baseline** — a deterministic,
   hash-anchored ONNX artifact produced from the existing μ / Σ⁻¹ baseline (discharges
   scientific-debt item #4). This is new *artifact/tooling* work, not new architecture.
2. **`src/inspection/providers_onnx.py`** — the hard restriction to the placeholder boundary
   model reference must be replaced (under governance) so the real governed artifact is the
   model the provider loads and executes.
3. **`src/frameworks/output_mapping.py`** — the output mapping/scale must carry the real
   PaDiM anomaly measure (`padim_anomaly_map_max_v1`) and localization semantics instead of
   `placeholder_output_raw_0_100`, preserving the `InspectionPrediction` contract shape.
4. **Placeholder retirement from the canonical flow** — the placeholder examiner/model is
   removed from the live `inspect()` path (may be retained only as a governed test fixture).

Nothing outside this list should require modification. If Phase 3 finds itself editing Trust,
Review, Evidence, Evaluation, the prediction contract shape, or a domain seam, that is a red
flag that the integration has drifted into re-architecture and must be re-reviewed.

---

## 5. Integration Risks

Ranked highest to lowest by likelihood × impact on the integrity of the phase.

### R1 — Inference equivalence failure (HIGHEST)

The runtime ONNX execution produces a *different* anomaly measure than the offline PaDiM
pipeline (different from the C-6 result), silently. Root causes: float32-vs-float64
divergence (the offline maps are float64 Mahalanobis; ONNX Runtime commonly executes
float32), operator-level numerical differences, or accumulation-order differences in the
Mahalanobis computation. **Impact:** the runtime would carry a signal that is *not* the
validated C-6 signal, invalidating the entire integration premise. **Mitigation direction:**
pre-declared equivalence tolerance, per-class equivalence evidence against C-6 outputs,
explicit dtype policy.

### R2 — ONNX export fidelity (HIGH)

The export from a *statistical* PaDiM baseline (μ, Σ⁻¹, feature extractor + Mahalanobis
distance) into an ONNX graph may not faithfully represent the offline computation — Σ⁻¹
embedding, feature-subsample indices (`[0, 2, 5, 6, 7, 9, 12, 13]`), and the distance
operator must all survive export. **Impact:** directly causes R1. **Mitigation direction:**
export is itself a governed, hash-anchored, replay-verified artifact with its own evidence,
not an incidental byproduct.

### R3 — Preprocessing equivalence (HIGH)

The runtime image preprocessing
([`src/frameworks/image_preprocessing.py`](../../src/frameworks/image_preprocessing.py)) must
be **bit-for-bit equivalent** to the preprocessing used in the offline C-5 inference. Any
divergence in resize, normalization, channel order, or interpolation shifts the features and
breaks equivalence before the model even runs. **Impact:** a subtle, hard-to-detect source of
R1. **Mitigation direction:** treat offline and runtime preprocessing as one governed
specification with equivalence evidence.

### R4 — Replay integrity across the runtime boundary (MEDIUM-HIGH)

The Phase 2 replay guarantee (byte-identical second run) must extend through the runtime
path, not just the offline scripts. **Impact:** loss of the phase's strongest reproducibility
property. **Mitigation direction:** runtime replay proof is a required completion artifact,
matching the offline standard.

### R5 — Runtime determinism (MEDIUM)

ONNX Runtime execution-provider selection, threading, and non-deterministic kernels can break
determinism. **Impact:** undermines R4 and the governed-replay claim. **Mitigation
direction:** pinned single-threaded/CPU execution provider and session options, recorded and
hash-anchored (the `onnx_session` configuration machinery already exists for this).

### R6 — Governance continuity (MEDIUM)

The hash-anchored provenance chain (archive → files → splits → training → inference →
evaluation) must extend unbroken to include the ONNX artifact and the runtime path. **Impact:**
a governance gap would let an unverified artifact reach the runtime. **Mitigation direction:**
the ONNX artifact carries a recorded content hash and provenance back to the fitted baseline;
the provider fails closed on hash mismatch (the placeholder path already does this).

**Ranking rationale:** R1 is the phase's existential risk — everything else is a *cause* of R1
(R2, R3) or a *guarantee* that would be lost if R1 is mishandled (R4, R5, R6). Equivalence is
the property the whole phase must defend.

---

## 6. Phase 3 Capability Ordering

The logical order only. **This approves nothing** — each item requires its own
governance record before implementation.

1. **Governed ONNX export of the fitted PaDiM baseline.** Produce a deterministic,
   hash-anchored ONNX artifact from the existing μ / Σ⁻¹ baseline, with export-fidelity
   evidence (addresses R2, discharges scientific-debt #4). This is the prerequisite for
   everything downstream.

2. **Offline export equivalence verification.** Before touching the runtime, prove the
   exported ONNX artifact reproduces the offline PaDiM anomaly measure/localization on
   governed inputs to the pre-declared tolerance (addresses R1/R3 in isolation, off the
   runtime).

3. **Runtime provider integration.** Wire the governed artifact behind
   `InspectionInferenceProvider.predict` via the existing `model_loader`/`onnx_session`
   substrate; update `output_mapping.py`; lift the placeholder restriction under governance
   (addresses R5, R6).

4. **End-to-end runtime equivalence + replay evidence.** Demonstrate the canonical
   `inspect()` path carries the real signal, equivalent to C-6, with byte-identical replay
   (addresses R1, R4).

5. **Placeholder retirement from the canonical flow.** Remove the placeholder from the live
   path once the real path is proven; retain only as a governed fixture if useful.

**Explicitly ordered *after* integration, and outside the integration objective** (each its
own governance approval): multi-seed characterization (scientific-debt #2) and calibration / Trust
qualification (scientific-debt #3). These are downstream of a runtime that carries the real
model and must not be interleaved into the integration itself.

---

## 7. Success Criteria

`ML Phase 3 COMPLETE` means **all** of the following are objectively true and evidenced:

1. **Real model at runtime.** The canonical `inspect()` path loads and executes a governed
   ONNX artifact derived from the fitted PaDiM baseline; `providers_onnx.py` no longer
   restricts the canonical flow to the placeholder boundary model.

2. **Placeholder retired.** The placeholder identity model no longer participates in the
   canonical runtime `inspect()` path (fixture-only retention is acceptable).

3. **Export governed and replayable.** The ONNX artifact is deterministic, hash-anchored,
   provenance-linked to the fitted baseline, and a second export is proven identical.

4. **Runtime equivalence demonstrated.** The runtime anomaly measure/localization reproduces
   the offline C-6 result on governed inputs within a pre-declared, justified tolerance,
   with per-class equivalence evidence. Preprocessing equivalence is evidenced.

5. **Runtime replay proven.** A complete second run of the integrated runtime path is proven
   identical, matching the Phase 2 replay standard.

6. **Governance continuity intact.** The hash-anchored chain extends unbroken from archive
   through the ONNX artifact to the runtime path; the provider fails closed on artifact hash
   mismatch.

7. **No architectural drift, no expanded claims.** No new domain, seam, or contract shape was
   created; Trust/Review/Evidence/Evaluation domains are unchanged; and the scientific claim
   boundary is exactly C-6's — single-seed, VisA-proxy, no calibration, no confidence, no
   product-readiness.

8. **Full completion evidence persisted** under the public project documentation workflow (governance approval +
   completion record pair, evidence document).

Completion is defined by **equivalence and governance**, not by any improvement in metrics.
If the runtime metrics *differ* from C-6, the phase is not complete — it is broken. (Future
phases are out of scope for this record and are not discussed here.)

---

## 8. Lessons Carried Forward

The following ML Phase 2 practices become **mandatory** for ML Phase 3:

- **record persistence workflow (mandatory).** Review → persist in
  `docs/records/` → only then update ADRs/normative docs. Every Phase 3 capability gets
  its own persisted governance approval + completion record pair; nothing lives only in chat.
- **governance approval workflow (mandatory).** public project documentation's Decision → Persist record → Review
  → governance approval → Implementation → implementation assessment → Persist Completion Evidence,
  followed for **every** Phase 3 capability. This record is only the *opening* step of
  that workflow — it approves nothing.
- **Evidence-first engineering (mandatory).** Every claim (export fidelity, equivalence,
  replay) is backed by a persisted evidence document written for an untrusting observer, not
  asserted in narrative.
- **Deterministic replay proven, not asserted (mandatory).** A complete second run proves
  identity at every new boundary — the export and the integrated runtime path both.
- **Governed boundaries with hash-anchoring and fail-closed validation (mandatory).** Every
  new artifact (the ONNX model above all) is hash-anchored, provenance-linked, and rejected
  on mismatch.
- **Machine-checkable scope boundaries (mandatory).** The `scope_boundaries` metadata pattern
  (flags default `false`) makes "did this phase stay in its lane?" verifiable — especially
  important here, where the temptation to drift from *integration* into *re-architecture* or
  *new science* is the phase's characteristic failure mode.
- **Honest claim boundaries (mandatory).** Carry the C-6 single-seed / VisA-proxy boundary
  forward unchanged; integration must not silently launder the offline caveats.
- **Track C-number / roadmap divergence (carried lesson).** Phase 2's closure noted that the
  original C-1…C-8 roadmap diverged from executed phases. Phase 3 should either revise the
  roadmap record when it redefines capability numbers or use a distinct series, so a
  future observer is not misled.

---

## 9. Readiness Decision

```text
READY TO OPEN ML PHASE 3
```

**Justification.**

1. **The objective is clear, bounded, and architectural.** Phase 3's goal — carry the real
   PaDiM signal end-to-end at runtime, equivalent to C-6, governed and replayable, placeholder
   retired — is precisely defined and is a *transport/integration* objective, not an open
   scientific question.

2. **The substrate is ready and verified.** Independent code inspection confirms the real ONNX
   Runtime substrate (`model_loader.load_governed_model`, `onnx_session`, the
   `InspectionInferenceProvider` seam, the `InspectionPrediction` contract) already exists and
   executes end-to-end; it lacks only a real model to load. Phase 3 requires **no new
   architecture** (§4), which is the strongest readiness signal.

3. **The scientific payload to integrate exists.** ML Phase 2 delivered a real, replay-proven,
   governed offline PaDiM result (C-6). There is something concrete and validated to export and
   verify equivalence against — Phase 3 is not blocked on prior science.

4. **The gap is single and well-localized.** The disconnection is exactly one seam: no governed
   ONNX export of the real model. The change surface (§4.2) is minimal and seam-local.

5. **The risks are identified and bounded.** The dominant risk (R1 inference equivalence, with
   R2 export fidelity and R3 preprocessing equivalence as its causes) is understood and
   mitigable with the equivalence-and-replay discipline Phase 2 already established.

6. **The governance discipline that makes this trustworthy is intact and mandatory.** The
   record/governance approval/evidence/replay workflow carried forward (§8) is exactly what
   Phase 3 integration needs.

Opening Phase 3 is justified **only because** its objective is honestly bounded to integration
and equivalence, its scientific claim boundary is fixed at C-6, and every capability inside it
remains behind its own separate governance gate. This record **opens** the phase; it
does **not** approve any implementation within it.

---

## 10. Scope Boundaries and Explicit Non-Claims

- **No code implemented.** No source, test, script, or evidence file was created or modified.
- **No governance approval granted.** No ONNX export, no runtime integration, no provider change, no
  placeholder retirement, no multi-seed work, no calibration, and no product-facing capability
  is approved by this record.
- **No roadmap update.** No ADR, Strategy, Evaluation Strategy, or Implementation governance approval
  was modified.
- **No scientific or product claim beyond C-6.** The bounded single-seed VisA-proxy claims
  stand exactly as recorded in the
  C-6 completion record
  and the
  [scientific evaluation evidence](../evidence/SCIENTIFIC_EVALUATION.md).
- **Kalibra does not yet perform real defect detection at runtime.** As at the Phase 2 close,
  the runtime still runs the placeholder identity model. Phase 3 exists to change that; this
  record only opens it.

---

## 11. Validation

| Validation | Command | Result |
| --- | --- | --- |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (no output) ✔ |
| Baseline tag | `git rev-list -n1 ml-phase-2-complete` | `a9743b4` ✔ |
| HEAD | `git log -1 --oneline` | `a9743b4 docs: review ml phase 2 documentation` ✔ |

itself.

---

## 12. Next Natural Step

```text
Review this persisted ML Phase 3 Runtime Integration Architecture record before opening
the first ML Phase 3 governance record.
```

If the first Phase 3 capability is opened, the logical first step (per §6, **not approved
here**) is the governed ONNX export of the fitted PaDiM baseline, which requires its own
governance record — reviewed and approved by the repository owner — before any
implementation begins. Until then, the runtime continues to run the placeholder, and every
claim remains bounded to the offline single-seed VisA-proxy evidence recorded in C-6.
