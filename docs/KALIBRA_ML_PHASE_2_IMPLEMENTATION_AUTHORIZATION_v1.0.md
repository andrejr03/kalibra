# Kalibra ML Phase 2 — Implementation Authorization v1.0

## About This Document

This document is the **final governance gate** before ML Phase 2 implementation. It
defines the objective decision process that must be satisfied before any
framework-backed provider work is permitted, and it authorizes implementation
**only** when every objective condition below is met.

It is **not** an implementation plan. It writes no code, selects no framework,
chooses no dataset, selects no metric, and expresses no framework preference. It is a
**gate**, not a step across it.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md`](KALIBRA_ML_PHASE_2_SCIENTIFIC_ARCHITECTURE_PLAN_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md`](KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md),
[`docs/KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md),
and
[`docs/KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md`](KALIBRA_ML_PHASE_2_EVALUATION_STRATEGY_v1.0.md).

**Current authorization status.**

```text
AUTHORIZED WITH RESTRICTIONS — Sprint 1B only.

General ML Phase 2 implementation remains BLOCKED.
Only the ONNX Session Substrate (Sprint 1B) is authorized.
ONNX Runtime selected as first runtime candidate (Framework ADR).
No dataset approved. Dataset Selection ADR remains deferred.
No evaluation protocol fixed.
No provider / inference / model-loading / dataset / evaluation work authorized.
```

This revision (recorded under §13 and detailed in **Addendum A**) grants a single,
narrowly bounded restricted authorization for the ONNX Session Substrate slice and
nothing else. The **full** ML Phase 2 authorization remains **Deferred**: the §3
preconditions for provider-and-inference work are not all met, and that status
**must not** change to "Authorized" except by the repository owner and only when the
conditions in §12 are met. The Sprint 1B restriction is defined, scoped, and bounded
in **Addendum A**; work outside it remains unauthorized.

---

## 1. Purpose

This document is the **final governance gate** in the ML Phase 2 planning sequence.
Every preceding document deferred implementation and named the next decision; this
one gathers those deferred decisions into a single, explicit authorization so that
implementation begins **only when objective conditions are satisfied**, never by
default and never by accumulated momentum.

Its role is deliberately narrow. It does not decide the science, the framework, the
dataset, or the metrics — those belong to the documents it references. It decides one
thing: **whether the prerequisites for implementation are all demonstrably in place.**
Until they are, ML Phase 2 implementation remains blocked.

The document authorizes implementation **only** when the objective conditions of §3–§9
are met, recorded, and signed off by the repository owner (§10, §11). Absent that,
the standing status of the full authorization is Deferred (§11). It grants no
authority to select a framework or make any claim; the sole implementation authority
it currently grants is the restricted Sprint 1B slice recorded in Addendum A, and,
beyond that, at most the conditional permission to begin implementation under the
constraints of §8 once every gate is green.

---

## 2. Current Repository Baseline

ML Phase 2 implementation authorization is considered against the following completed
repository state. Each item is already present and validated; none is re-opened here.

- **Deterministic five-domain runtime.** A complete
  Inspection → Trust Qualification → Human Review → Evidence → Evaluation chain in
  which each domain owns one responsibility and consumes only the canonical output of
  the domain before it.
- **Provider abstraction.** `InspectionInferenceProvider` is the single boundary
  object behind the Inspection Engine's examination seam where inference
  implementations may be referenced.
- **`InspectionPrediction` boundary.** The abstract, non-canonical, untrusted
  prediction contract produced by Machine Learning and consumed only by the
  Inspection Engine.
- **`transform_prediction` ownership.** `InspectionEngine.transform_prediction(...)`
  owns validation of every prediction and its deterministic conversion into the
  canonical `RawInspectionResult`.
- **`LocalArtifactInferenceProvider`.** The first real local provider, reading
  deterministic PGM P2 fixture content with the Python standard library and deriving
  an `InspectionPrediction` from real bytes. It returns only `InspectionPrediction`
  and remains unwired from `InspectionEngine.inspect()`.
- **Prototype integration.** A prototype adapter that projects the real
  local-provider result into inspection-only prototype data, explicitly withholding
  calibrated confidence, trust, routing, drift, and evaluation claims.
- **End-to-end evidence integration.** An opt-in path that runs the real
  local-provider result through the canonical downstream chain, with downstream
  domains consuming only canonical records — never provider objects, predictions,
  pixels, or screenshots.
- **ML Phase 1 closure.** The ML Phase 1 local-provider path checkpoint is formally
  closed, with an explicit list of what remains unclaimed.
- **Scientific Architecture Plan.** The ML Phase 2 scientific baseline (objectives,
  anomaly-detection-first scope, evidence obligations, roadmap).
- **Framework ADR.** The runtime-evaluation decision process, updated to record
  **ONNX Runtime as the first selected runtime candidate** while keeping provider
  implementation deferred.
- **Dataset Strategy.** The dataset evidence requirements (provenance, licensing,
  ownership, traceability, reproducibility, versioning, integrity verification,
  long-term availability, honest content and ground truth, leak-free frozen splits,
  bounded synthetic-data policy, governance, scientific-risk reasoning).
- **Evaluation Strategy.** The standard of proof (three validation layers, metric
  policy by category, statistical obligations, calibration boundary, explainability,
  mandatory failure analysis, benchmark policy, claim policy, approval criteria).

**Why implementation authorization is the final remaining decision.** The planning
sequence ordered decisions by dependency, and each was fixed in turn: scientific
direction, runtime-evaluation process, dataset evidence requirements, and the
standard of proof. What remains is not another design decision but a **governance
decision** — whether those prerequisites are all satisfied for a specific framework,
dataset, and evaluation. This document is that decision. After it, the next artifact
is code, not another strategy.

---

## 3. Required Preconditions

Implementation authorization requires **all** of the following prerequisites. Every
one is mandatory; a single unmet prerequisite blocks authorization.

- **Approved Scientific Architecture.** The Scientific Architecture Plan is approved by
  the repository owner and is reflected, not contradicted, by what is proposed.
- **Approved Framework ADR.** The Framework ADR is approved and updated to record a
  selected runtime (§4), no longer in "defer selection" status.
- **Approved Dataset Strategy.** The Dataset Strategy is approved and a specific
  dataset is shown to satisfy its approval criteria (§5).
- **Approved Evaluation Strategy.** The Evaluation Strategy is approved and a concrete
  evaluation protocol is fixed under it (§6).
- **Approved repository scope.** The scope of ML Phase 2 implementation is approved and
  bounded — anomaly-detection-first with bounded secondary localization — with no
  scope widening beyond the approved documents.
- **Approved implementation owner.** A named owner is accountable for the
  implementation and for keeping it within these constraints.
- **Approved claim policy.** The three-tier claim policy (engineering / scientific /
  product) is approved and binding on the implementation and every surface it touches.

Every prerequisite is **mandatory**. None may be waived, assumed, or treated as
satisfied by proximity to completion. Where any prerequisite is unmet, authorization
status remains Deferred (§11).

---

## 4. Framework Authorization

Implementation may begin only after the runtime framework decision is closed. This
document expresses **no framework preference**; it requires only that the decision be
made and recorded through the Framework ADR's own process. Specifically:

- **Framework selected.** One runtime is selected under the Framework ADR's decision
  drivers and approval criteria, against a named target environment (operating
  system, Python version, CPU baseline, and any optional accelerator policy).
- **Framework ADR updated.** The Framework ADR is revised or superseded to record the
  selection, moving it out of "defer selection" status.
- **Rationale recorded.** The evidence for the selection against every decision driver
  is recorded, including the trade-offs accepted, so an observer can see why the
  runtime was chosen and not merely that it was.
- **Compatibility confirmed.** The selected runtime is confirmed to satisfy the
  compatibility rules of the Framework ADR: it sits behind
  `InspectionInferenceProvider`, returns only `InspectionPrediction`, keeps all
  runtime tensors, sessions, interpreters, execution providers, device handles, and
  intermediate outputs provider-private, and changes no downstream contract.

Until all four hold, the framework precondition of §3 is unmet.

---

## 5. Dataset Authorization

Implementation may begin only after a specific dataset is authorized under the
Dataset Strategy. Required:

- **Approved dataset.** A specific dataset is accepted against the Dataset Strategy
  approval criteria, with the acceptance and any recorded limitations captured in the
  project record.
- **Provenance verified.** The origin of every input is known and recorded; data of
  unknown or unclear origin is declined, not used.
- **Licensing verified.** The terms of use are known, explicit, and compatible with
  Kalibra's local, reproducible, evidence-bearing use; unclear licensing is a reason
  to decline.
- **Version recorded.** The dataset, its splits, and its label sets each carry a
  stable, identifiable version, so any result ties to exactly the data behind it.
- **Hashes recorded.** The exact content used is recorded by content hash, so
  integrity can be verified and silent substitution or corruption detected.
- **Governance completed.** Version IDs, hashes, metadata, lineage, provenance, and
  evidence linkage are in place, and the scientific risks of the Dataset Strategy have
  been assessed and reflected in the scope of permitted claims.

Until all hold for a specific dataset, the dataset precondition of §3 is unmet.

---

## 6. Evaluation Authorization

Implementation may begin only after a concrete evaluation is fixed under the
Evaluation Strategy. This document **chooses no metric**; it requires that the
strategy's deferred decisions be closed under the strategy's own standard. Required:

- **Metrics selected.** Specific metrics within each applicable category are selected
  and justified against the approved dataset and inspection problem, with both error
  kinds expressible. (No metric is chosen here.)
- **Evaluation protocol fixed.** The end-to-end evaluation procedure is fixed for the
  approved dataset, computed on an untouched, frozen test partition, reading only
  preserved evidence.
- **Statistical procedure documented.** The significance procedure, interval method,
  sample sizes, repetition, and variance reporting are documented and regenerable.
- **Benchmark policy approved.** The benchmark policy is approved and binding: no
  benchmark or comparison without a reproducible artifact, named dataset version, and
  documented procedure; no unsupported benchmark claim.
- **Claim policy approved.** The three-tier claim policy is approved and binding, with
  reproducible evidence required before any scientific claim.

Until all hold, the evaluation precondition of §3 is unmet.

---

## 7. Architecture Authorization

Implementation may begin only with the canonical architecture confirmed intact.
Authorization requires confirmation that:

- **Provider abstraction preserved.** Inference is referenced only behind
  `InspectionInferenceProvider`, which returns only `InspectionPrediction`.
- **Inspection ownership preserved.** `InspectionEngine.transform_prediction(...)`
  remains the only owner of prediction validation and conversion into
  `RawInspectionResult`, and the Inspection Engine remains the only owner of
  `RawInspectionResult`.
- **Trust ownership preserved.** Trust Qualification remains the only owner of
  calibrated confidence, uncertainty characterization, drift caution, and qualified
  outcomes.
- **Review ownership preserved.** Human Review remains the only owner of review-case
  preparation and reviewer decision recording.
- **Evidence ownership preserved.** Evidence remains the only owner of preservation,
  lineage, absence markers, and read-only evidence views.
- **Evaluation ownership preserved.** Evaluation remains the only owner of
  evidence-backed evaluation reports.

**Violating the architecture automatically blocks authorization.** Any proposed
implementation that would move ownership, cross the provider boundary, or change the
downstream chain is rejected on that basis alone, regardless of how attractive the
framework, dataset, or expected result may be.

---

## 8. Implementation Constraints

If authorization is granted, the implementation is bound by the following mandatory
rules. They are conditions of the authorization, not guidance.

- **Provider returns only `InspectionPrediction`.** A framework-backed provider may
  change the raw values inside a valid `InspectionPrediction`, but it may return
  nothing else across the boundary.
- **`InspectionEngine` owns transformation.** Validation and deterministic conversion
  into `RawInspectionResult` remain with `InspectionEngine.transform_prediction(...)`.
- **No downstream ownership changes.** Trust, Review, Evidence, and Evaluation
  ownership are unchanged, and the default CLI and default deterministic integration
  path are unchanged unless a later owner-approved plan explicitly changes them.
- **Offline-first.** Inference runs fully locally with no network dependency; hosted
  services, phone-home behavior, and live operation are disallowed.
- **Deterministic replay.** Inference is repeatable for fixed artifacts, fixed input
  bytes, fixed preprocessing, fixed configuration, and fixed hardware class; any
  residual nondeterminism is bounded, documented, and tested.
- **Reproducibility.** Every result is regenerable from a fixed starting point — fixed
  dataset version, split, and configuration — by an observer who does not trust
  Kalibra.
- **Evidence-first.** No claim is made ahead of the reproducible evidence that
  supports it; raw measures are never presented as confidence, and absence of
  evidence is reported as absence.

Breaching any constraint voids the authorization for the affected work.

---

## 9. Prohibited Implementation

The following are explicitly prohibited. Any of them blocks authorization if
proposed, and voids authorization if attempted after grant:

- **Bypassing the provider boundary.** Referencing inference anywhere other than
  behind `InspectionInferenceProvider`, or leaking runtime objects across it.
- **Changing canonical ownership.** Moving validation, transformation, calibrated
  confidence, uncertainty, drift, review, evidence, or evaluation ownership from the
  domain that holds it.
- **Introducing unsupported claims.** Stating any engineering, scientific, product,
  or benchmark claim without the reproducible evidence its tier requires.
- **Skipping evaluation.** Proceeding without the fixed evaluation protocol, on
  touched or unfrozen test data, or with favorable-only reporting.
- **Skipping dataset governance.** Using data without approved provenance, licensing,
  versioning, hashes, or governance.
- **Skipping framework authorization.** Implementing against an unselected or
  unrecorded runtime, or one whose compatibility is unconfirmed.

Prohibited work is not authorized under any status short of an explicit,
owner-approved change to the referenced governing document.

---

## 10. Authorization Checklist

The following checklist is suitable for repository-owner sign-off. **Full** ML Phase 2
authorization requires every item checked; any unchecked item leaves the full
authorization at Deferred. The checklist distinguishes the full authorization (still
incomplete) from the Sprint 1B restricted authorization (Addendum A), which is
allowed only while every Sprint 1B restriction is met.

**Full ML Phase 2 authorization — status: INCOMPLETE.**

```text
Preconditions (§3)
[ ] Scientific Architecture approved
[ ] Framework ADR approved and updated with a selected runtime
[ ] Dataset Strategy approved and a specific dataset qualified
[ ] Evaluation Strategy approved and a concrete protocol fixed
[ ] Repository scope approved and bounded
[ ] Implementation owner named and accountable
[ ] Claim policy approved and binding

Framework (§4)
[ ] Framework selected against a named target environment
[ ] Framework ADR updated / superseded to record the selection
[ ] Selection rationale and trade-offs recorded
[ ] Provider-boundary compatibility confirmed

Dataset (§5)
[ ] Dataset approved against Dataset Strategy criteria
[ ] Provenance verified
[ ] Licensing verified
[ ] Dataset / split / label versions recorded
[ ] Content hashes recorded
[ ] Governance and scientific-risk assessment completed

Evaluation (§6)
[ ] Metrics selected and justified against dataset and problem
[ ] Evaluation protocol fixed on an untouched, frozen test set
[ ] Statistical procedure documented and regenerable
[ ] Benchmark policy approved
[ ] Claim policy approved

Architecture (§7)
[ ] Provider abstraction preserved
[ ] Inspection ownership preserved
[ ] Trust ownership preserved
[ ] Review ownership preserved
[ ] Evidence ownership preserved
[ ] Evaluation ownership preserved

Constraints & prohibitions (§8, §9)
[ ] Implementation constraints accepted as binding
[ ] No prohibited implementation present in the proposal

Sign-off
[ ] Repository owner approves the authorization decision (§11)
```

**Sprint 1B restricted authorization (Addendum A) — status: ALLOWED under
restrictions.**

```text
Sprint 1B — ONNX Session Substrate (Addendum A)
[x] Framework ADR approved and updated: ONNX Runtime selected as first
    runtime candidate
[x] Provider conformance and deterministic-replay harness in place and green
[x] ONNX Runtime discovery substrate in place, isolated, absence-safe
[x] Sprint 1B scope bounded to session-configuration value modeling
    (Addendum A §A.2), with all forbidden items (§A.3) excluded
[x] Architecture contracts reaffirmed unchanged (Addendum A §A.4)
[x] No dataset, evaluation, benchmark, or scientific claim implied
[ ] Sprint 1B validation evidence recorded on completion (Addendum A §A.7)
```

An unchecked or breached Sprint 1B item voids only the Sprint 1B grant; it does not
and cannot advance the full authorization, which remains governed by §3–§9 and §12.

---

## 11. Approval Decision

The repository owner records exactly one of the following outcomes.

- **Authorized.** Every checklist item (§10) is satisfied and recorded. Implementation
  may begin, bound by the constraints of §8 and the prohibitions of §9. This outcome
  requires that the framework, dataset, and evaluation gates are all closed.
- **Authorized with restrictions.** The prerequisites are met, but implementation is
  permitted only within explicitly recorded limits (for example a bounded scope, a
  specific runtime configuration, or a withheld surface). The restrictions are
  recorded and binding, and work outside them remains unauthorized.
- **Deferred.** One or more prerequisites are unmet. Implementation remains blocked;
  the unmet items are recorded as the reason. **This is the standing default until a
  full sign-off occurs**, and it remains the status of the **full** ML Phase 2
  authorization.
- **Rejected.** The proposal violates the architecture (§7), the claim policy, or a
  prohibition (§9) in a way that cannot be remedied by meeting a checklist item.
  Implementation is refused, and the violated rule is recorded as the reason.

No outcome other than **Authorized** or **Authorized with restrictions** permits
implementation to begin, and neither may be recorded except by the repository owner.

**Recorded outcome for this revision.**

```text
AUTHORIZED WITH RESTRICTIONS — Sprint 1B only (Addendum A).
Full ML Phase 2 authorization: DEFERRED (unchanged).
```

The restriction is the entirety of Addendum A: only the ONNX Session Substrate
slice defined there is permitted, and all provider, inference, model-loading,
dataset, and evaluation work remains unauthorized. The unmet items for the full
authorization remain the dataset gate (§5), the evaluation gate (§6), and full
owner sign-off (§10, §12).

---

## 12. Exit Criteria

The authorization status may be changed to **Authorized** only when all of the
following evidence exists and is recorded:

- **Approvals.** The Scientific Architecture, Framework ADR (updated with a selection),
  Dataset Strategy, and Evaluation Strategy are all approved by the repository owner.
- **Framework closed.** A runtime is selected, its ADR updated, its rationale recorded,
  and its provider-boundary compatibility confirmed (§4).
- **Dataset qualified.** A specific dataset is approved with provenance, licensing,
  versions, hashes, and governance recorded (§5).
- **Evaluation fixed.** Metrics, protocol, statistical procedure, benchmark policy, and
  claim policy are fixed and approved under the Evaluation Strategy (§6).
- **Architecture confirmed.** Provider abstraction and all five domain ownerships are
  confirmed preserved (§7), with no prohibited implementation proposed (§9).
- **Checklist complete.** Every item in §10 is checked.
- **Owner sign-off.** The repository owner records the decision (§11) as Authorized or
  Authorized with restrictions.

Until every criterion is met, the status remains Deferred. Meeting the engineering or
architectural criteria alone does **not** authorize implementation; the dataset and
evaluation gates are equally required.

---

## 13. Governance Notes

- **This document is authoritative over convenience.** Where a proposed implementation
  is easier if a gate is skipped, the gate governs. Authorization is changed by
  meeting the criteria, never by relaxing them.
- **Revisions supersede, not erase.** A future change to the authorization is recorded
  as a new version (for example `v1.1` or `v2.0`) that supersedes this one; the prior
  decision and its rationale remain in the record so the history of the gate is clear.
- **Referenced documents govern their own domains.** This document does not restate or
  override the science, framework, dataset, or evaluation decisions; it references
  them. If a referenced document is revised, this authorization is re-evaluated
  against the revision before any status change stands.
- **Scope changes require re-authorization.** Widening scope beyond the approved
  bounds — for example adding defect classification or segmentation — requires an
  approved update to the governing documents and a fresh authorization decision.
- **Status changes are owner acts.** Only the repository owner may change the
  authorization status, and only by recording an outcome under §11 with the evidence
  of §12.

---

## 14. Closing Statement

This document is the final governance gate before ML Phase 2 implementation. It
chooses no dataset, picks no metric, and expresses no preference; it fixes the
objective conditions under which implementation may begin. The full ML Phase 2
authorization remains Deferred until those conditions are met and signed off by the
repository owner. The only implementation permission this revision grants is the
restricted Sprint 1B slice recorded in Addendum A.

```text
Sprint 1B may proceed under restriction.
Full ML Phase 2 implementation remains blocked.
```

Three principles are affirmed and binding:

- **ML Phase 2 implementation remains blocked until the full authorization is
  granted.** No framework-backed provider work is permitted while the full status is
  Deferred, and none is permitted outside the constraints of an Authorized or
  restricted grant. The Sprint 1B grant (Addendum A) is such a restricted grant and
  extends to nothing beyond its recorded scope.
- **Architecture governance remains authoritative over implementation convenience.**
  The provider abstraction and the Inspection, Trust, Review, Evidence, and Evaluation
  ownerships hold regardless of how much easier a violation would make the work.
- **Scientific evidence remains authoritative over engineering preference.** No claim
  is made, and no implementation is authorized to imply one, ahead of the reproducible
  evidence that supports it.

---

## Addendum A — Sprint 1B Restricted Authorization (ONNX Session Substrate)

This addendum records the single restricted authorization granted under §11
("Authorized with restrictions"). It authorizes exactly one bounded engineering
slice and nothing else. It is a narrow implementation authorization update, not a
general ML Phase 2 authorization.

### A.1 Authorized Slice

```text
Sprint 1B — ONNX Session Substrate
```

Sprint 1B is substrate-only work: representing, validating, and testing ONNX
Runtime session **configuration** as deterministic values, without creating
sessions, loading models, creating tensors, or running inference.

### A.2 Permitted Scope

Sprint 1B work **may** include, and only include:

- a session configuration object or value model;
- a deterministic runtime options representation;
- an execution-provider policy representation;
- a model artifact **reference** type if needed (a reference by path/hash/identity —
  never loaded content);
- validation of session configuration inputs;
- tests proving that no inference, session, tensor, or runtime object crosses any
  provider or domain boundary.

All Sprint 1B code remains under `src/frameworks/` (with its tests under `tests/`),
isolated from every Kalibra domain package.

### A.3 Forbidden Scope

Sprint 1B work **must not** include:

- any `InspectionInferenceProvider` implementation;
- any model-specific inspection logic;
- any real model inference;
- any production model loading;
- any dataset ingestion;
- any evaluation metrics;
- any benchmark claims;
- any CLI/UI integration.

Any of these voids the Sprint 1B grant for the affected work (§8, §9) and remains
unauthorized until the full authorization is granted under §12.

### A.4 Architecture Constraints (Unchanged and Binding)

All existing boundaries remain binding exactly as fixed by §7–§9:

```text
InspectionInferenceProvider
    ↓
InspectionPrediction
    ↓
InspectionEngine.transform_prediction(...)
    ↓
RawInspectionResult
    ↓
Trust
    ↓
Review
    ↓
Evidence
    ↓
Evaluation
```

Sprint 1B must not modify these contracts, move any ownership, or wire any
framework object across any of them. Session-configuration values are framework
substrate values; they must never appear inside `InspectionPrediction`,
`RawInspectionResult`, or any downstream record.

### A.5 Framework Decision Linkage

The Framework ADR
([`KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md`](KALIBRA_ML_PHASE_2_FRAMEWORK_ADR_v1.0.md))
records **ONNX Runtime as the first selected runtime candidate**. That selection
permits only bounded ONNX **substrate** work — runtime discovery (Sprint 1A,
complete) and session-configuration modeling (Sprint 1B, this grant). It does not
permit a provider implementation, inference, or model loading; those remain gated
by the full authorization (§4, §12).

### A.6 Dataset and Evaluation Status

Recorded as of this revision:

- **No dataset is selected.** The Dataset Selection ADR remains **DEFER DATASET
  SELECTION**.
- The Data Strategy Decision Memo treats **VisA as the governance anchor** and
  **MPDD as the domain anchor**; neither is selected or acquired.
- **No evaluation protocol is fixed.** Metrics, statistical procedure, and benchmark
  policy application remain deferred under the Evaluation Strategy.

Therefore Sprint 1B **may not produce scientific claims** of any kind. Its outputs
are engineering-tier only under the three-tier claim policy: configuration
modeling, validation behavior, and boundary tests — never accuracy, performance,
benchmark, or product claims.

### A.7 Required Validation for Sprint 1B

Any Sprint 1B implementation must pass, and record the output of:

```bash
python3 -m pytest tests/test_onnx_runtime_substrate.py -q
python3 -m pytest tests/test_provider_conformance.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git diff --check
```

It must additionally record checks proving:

- no domain package (`src/inspection/`, `src/trust/`, `src/review/`,
  `src/evidence/`, `src/evaluation/`, `src/integration/`, `src/prototype_ui/`)
  changed unless explicitly justified;
- no provider implementation added;
- no inference path added;
- no model loading path added;
- no benchmark/performance wording introduced.

### A.8 Standing Recommendation

```text
Sprint 1B may proceed under restriction.
Full ML Phase 2 implementation remains blocked.
```
