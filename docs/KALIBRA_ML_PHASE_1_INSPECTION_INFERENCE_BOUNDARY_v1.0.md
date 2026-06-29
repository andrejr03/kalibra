# Kalibra ML Phase 1 — Inspection Inference Boundary

## About This Plan

This document is the architecture-first plan for the first machine-learning phase
of Kalibra (Engineering Phase 3). It fixes the **permanent architectural seam
between Machine Learning and the Inspection Engine** — exactly where Machine
Learning ends and the Inspection Engine begins.

This is **not** a model-selection document. It is **not** a training plan. It is
**not** an inference implementation. It chooses no model architecture, no
framework, no library, no dataset, and no metric. It defines only the boundary
that every later machine-learning choice must respect, and across which no model
is ever allowed to own a runtime contract.

Throughout, **must**, **must not**, **owns**, and **does not own** express binding
architectural obligations, consistent with the normative language of
[`AGENTS.md`](../AGENTS.md),
[`docs/KALIBRA_ENGINEERING_PLAN_v1.0.md`](KALIBRA_ENGINEERING_PLAN_v1.0.md), and
[`docs/KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md`](KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md).

This plan continues directly from
[`docs/KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md`](KALIBRA_ENGINEERING_PHASE_2_CLOSURE_v1.0.md)
§8, which states that the next phase begins the controlled introduction of ML
*through the documented domain contracts*, preserving the fixed
Inspection → Trust Qualification → Human Review → Evidence → Evaluation chain.

---

## 1. Purpose

Engineering Phase 3 introduces Machine Learning into Kalibra **without changing
the permanent architecture**.

Phase 2 closed the deterministic runtime: a complete
Inspection → Trust → Review → Evidence → Evaluation chain in which every domain
owns one responsibility and consumes only the canonical output of the domain
before it (Phase 2 Closure §3). Phase 3 introduces, for the first time, a learned
inference method *inside* the Inspection domain's examination stage — and nowhere
else.

The purpose of this document is to fix the seam at which that learned method
attaches, so that:

- Machine Learning supplies a prediction, and only a prediction;
- the Inspection Engine remains the sole owner of the canonical
  `RawInspectionResult` runtime contract;
- every downstream domain (Trust, Review, Evidence, Evaluation) is unchanged and
  unaware that inference was learned rather than rule-based.

This continues the extension point already named in Inspection plan §12
("Examination internals are replaceable") and already exercised by two
interchangeable non-ML examiners in `src/inspection/engine.py`. Phase 3 adds a
third *kind* of examination source — a learned one — behind the same seam,
without granting it any new authority.

This document fixes the boundary. It does not open it.

---

## 2. Architectural Principle

> **Machine Learning plugs into the architecture. The architecture does not bend
> around Machine Learning.**

This is the single load-bearing principle of Phase 3. From it follow the
binding rules:

- **Machine Learning never owns the runtime contract.** No model, framework,
  tensor, weight file, or inference session is ever a Kalibra runtime contract.
  The canonical runtime object remains `RawInspectionResult`, owned by the
  Inspection Engine.
- **The Inspection Engine always owns `RawInspectionResult`.** A model never
  produces, populates, or signs the canonical result. It produces only an
  `InspectionPrediction`, which the Inspection Engine must validate and transform.
- **The architecture never depends directly on a model.** Every downstream
  dependency is on `RawInspectionResult` and its evidence record, never on the
  inference implementation that informed it. Replacing, removing, or failing the
  model must change nothing downstream except the values carried inside the
  already-canonical result, or an explicit Inspection-domain failure.

Because the architecture owns the contract and the model owns only a prediction,
Machine Learning is, by construction, a replaceable detail behind a fixed seam —
never a structural dependency.

---

## 3. Boundary

The Phase 3 seam is a one-directional flow with exactly one downstream contract:

```text
InspectionInferenceProvider
  |
  v
InspectionPrediction        (produced by Machine Learning)
  |
  v
Inspection Engine           (validates + transforms)
  |
  v
RawInspectionResult         (the only downstream contract)
```

- **`InspectionInferenceProvider`** is the abstract boundary object that loads and
  executes an inference implementation. It is the *only* place in Kalibra where
  model code, frameworks, or weights may be referenced. It sits at the
  examination stage of the Inspection Engine (Inspection plan §7 stage 2), behind
  the existing examiner seam, and produces an `InspectionPrediction`.
- **`InspectionPrediction`** is the abstract product of Machine Learning. It is a
  *claim*, not a result. It is untrusted, unvalidated, and non-canonical until
  the Inspection Engine accepts it. It is never handed to any domain other than
  the Inspection Engine.
- **The Inspection Engine** validates every prediction and transforms accepted
  predictions into the canonical `RawInspectionResult`, exactly as it does today
  for non-ML examinations.
- **`RawInspectionResult`** remains the only object that crosses the downstream
  seam to Trust Qualification, and the only object preserved as inspection
  evidence.

**Why `RawInspectionResult` remains the only downstream contract.** Kalibra's
architecture is organized around one source of truth for inspection and trust
(AGENTS.md Engineering Philosophy; Inspection plan §1): the raw judgement,
localization, and raw anomaly measure that Trust Qualification must *reuse, never
reconstruct*. Trust, Review, Evidence, and Evaluation are already engineered to
consume `RawInspectionResult` and to read only its declared fields (for example,
trust validation inspects `raw_measure_kind`, never how the measure was produced).
If a model output were allowed downstream, the architecture would depend on the
model and the single-source seam would be broken. Keeping `RawInspectionResult`
as the only downstream contract means Machine Learning can change completely
while the rest of Kalibra does not move at all.

---

## 4. Responsibilities

### 4.1 `InspectionInferenceProvider` owns only

- **Loading the inference implementation.** Acquiring whatever the chosen
  inference method needs to run (its implementation, parameters, or session),
  behind the seam, where no other domain can see it.
- **Executing inference.** Running that implementation against the stabilized
  inspection input it is given.
- **Producing an `InspectionPrediction`.** Returning the abstract prediction
  contract (§6) and nothing else.

That is the **complete** remit of the provider. Anything not in this list is, by
design, not its job.

### 4.2 The Inspection Engine owns

- **Validation.** Checking every `InspectionPrediction` against the prediction
  contract (§6) before anything canonical is built (§7).
- **Conversion.** Deterministically transforming an accepted prediction into the
  canonical runtime object (§7).
- **Canonical `RawInspectionResult`.** Assembling, owning, and signing the
  single canonical runtime result — as it does today in
  `InspectionEngine._assemble_result`.
- **Evidence emission.** Emitting the durable inspection evidence record for the
  canonical result (Inspection plan §5; Phase 2 Closure §2).
- **Deterministic runtime contracts.** Holding the reproducibility, traceability,
  single-source, and failure-surfacing obligations of the Inspection domain
  (Inspection plan §§8–9), regardless of how inference was performed.

The Inspection Engine remains the owner of everything canonical. Machine Learning
informs the result; it never owns it.

---

## 5. Explicit Non-Responsibilities

The `InspectionInferenceProvider` **must not**:

- **emit `RawInspectionResult`.** It produces only an `InspectionPrediction`; the
  canonical result is the Inspection Engine's to assemble.
- **emit trust qualification.** No calibrated confidence, no qualified outcome, no
  abstention, no drift signal. *(Trust Qualification Engine.)*
- **emit evidence.** It does not create, own, present, or arbitrate any evidence
  record. *(Evidence Engine; Inspection Engine for inspection evidence.)*
- **emit evaluation.** No metric, score, accuracy, or quality claim about itself
  or anything else. *(Evaluation Engine.)*
- **route review.** It does not decide that a case goes to a human, nor perform
  any hand-off. *(Human Review Engine.)*
- **mutate architecture.** It does not add a domain, change a seam, widen a
  downstream contract, or introduce a new runtime object. It plugs into the
  existing examination seam and changes nothing structural.
- **bypass the Inspection Engine.** It must never hand a prediction, or anything
  derived from one, to any domain directly. Every prediction reaches the rest of
  Kalibra only after the Inspection Engine has validated and transformed it.

A prediction leaving Machine Learning is **unqualified, non-canonical, and
untrusted by design**. It is not a result, not evidence, and not a decision
Kalibra stands behind until the Inspection Engine has owned it.

---

## 6. `InspectionPrediction` Contract

This section fixes the **shape and obligations** of `InspectionPrediction` as an
**abstract contract only**. Concrete types, fields, encodings, and storage are
deliberately left to implementation. No tensor, array layout, framework object,
or serialized model output is defined here, and none may be treated as the
contract.

An `InspectionPrediction` is the abstract claim produced by Machine Learning
about one stabilized inspection input. It carries, in abstract terms:

- **A predicted judgement.** The model's claim of whether the input is defective.
  This is a *claim*, not the canonical judgement; the canonical judgement is the
  Inspection Engine's to assemble (Requirement F2 remains the engine's).
- **A predicted localization.** The model's claim of where a suspected defect
  lies, when its judgement is defective. Present only when the predicted
  judgement is defective; absent otherwise.
- **A predicted anomaly measure.** The model's raw, uncalibrated measure of how
  anomalous the input is. It is raw substrate, explicitly not confidence, not a
  probability, and not calibrated certainty. It must remain marked as raw so the
  Inspection Engine can carry it downstream under the existing
  `raw_anomaly_measure` kind without any consumer mistaking it for confidence.
- **Model metadata.** Abstract, descriptive provenance of the inference that
  produced the prediction (for example, an opaque inference-method identifier and
  version), sufficient for the prediction to be honestly described and traced.
  This metadata is descriptive only; it carries no trust, calibration, routing,
  evaluation, or ground-truth meaning.

Obligations the contract fixes (not the representation):

- The prediction **must** be self-describing as a *prediction* — non-canonical,
  unvalidated, and untrusted until the Inspection Engine accepts it.
- The predicted measure **must** be self-describing as *raw*, never as confidence.
- The prediction **must** reference the exact stabilized input it concerns, so the
  resulting canonical result remains traceable (Inspection plan §8 traceability
  invariant).
- The prediction **must not** carry any trust, calibrated-confidence, abstention,
  drift, routing, evaluation, or ground-truth field. Such fields belong to later
  domains and must be *absent*, not stubbed.

The contract exists so that one abstract prediction shape can be produced by any
inference implementation and validated by one Inspection Engine, with no
framework detail crossing the seam.

---

## 7. Transformation Contract

The Inspection Engine owns the deterministic transformation:

```text
InspectionPrediction
  |
  v   (Inspection Engine: validate, then transform)
RawInspectionResult
```

**The Inspection Engine validates every prediction before producing the canonical
runtime object.** No prediction is ever transformed unvalidated, and no
unvalidated prediction value ever reaches the canonical result.

Ordered obligations of the transformation:

1. **Validate.** The Inspection Engine checks the `InspectionPrediction` against
   the contract in §6: the prediction references the inspected input; its
   predicted measure is finite and marked raw; a defective predicted judgement
   carries a predicted localization and a non-defective one does not; and the
   prediction carries no forbidden downstream field. A prediction that fails any
   check is rejected as an Inspection-domain failure (§9) — never silently
   repaired and never converted into a verdict.
2. **Transform.** From an accepted prediction, the Inspection Engine
   deterministically derives the canonical judgement, localization (when
   defective), and raw anomaly measure, and assembles the canonical
   `RawInspectionResult` it already owns — preserving `raw_measure_kind =
   "raw_anomaly_measure"` as the single downstream-compatible raw-measure kind.
3. **Emit evidence.** The Inspection Engine emits the inspection evidence record
   for the canonical result, exactly as today.

Invariants the transformation must hold:

- **Single source.** The canonical judgement, localization, and raw measure for
  one input must derive from one prediction about one input — never independently
  reconstructed or reconciled across predictions (Inspection plan §8).
- **Determinism.** A fixed accepted prediction must transform to a fixed
  `RawInspectionResult`. (Determinism of the *inference* that produced the
  prediction is an inference concern, named in §9; determinism of the
  *transformation* is fixed here.)
- **Rawness preserved.** The raw measure must remain explicitly raw across the
  transformation; the engine must not calibrate, qualify, or rescale it into
  confidence.
- **No widening.** The transformation must produce only the existing canonical
  `RawInspectionResult` shape. It must not add trust-bearing, routing, or
  evaluation fields to accommodate a model.

The transformation is the point at which a model's untrusted claim becomes
Kalibra's owned raw result. Everything Kalibra later asserts is built on the
canonical result the engine produced here, never on the prediction.

---

## 8. Model Independence

Because Machine Learning produces only an `InspectionPrediction` behind the
provider seam, the **inference implementation is interchangeable without changing
any downstream subsystem**.

Future `InspectionInferenceProvider` implementations may be built on any inference
technology — for example PyTorch, ONNX Runtime, TensorFlow, OpenVINO, or CoreML —
**without changing**:

- the `InspectionPrediction` contract (§6);
- the Inspection Engine's validation and transformation (§7);
- the canonical `RawInspectionResult` contract;
- Trust Qualification, Human Review, Evidence, or Evaluation;
- the integration layer or the CLI.

This document **names these technologies only as examples of interchangeability**.
It selects none of them, recommends none of them, and treats none of them as the
chosen solution. The architectural guarantee is that the choice is contained
entirely behind the provider seam: swapping one for another must be a strictly
local change inside an `InspectionInferenceProvider`, with zero downstream blast
radius — the same "examination internals are replaceable" guarantee already
proven by the two existing non-ML examiners, now extended to learned inference.

---

## 9. Failure Modes

Machine-learning failures **remain inside the Inspection domain**. They are
surfaced as Inspection-domain failures (Inspection plan §9), never leaked
downstream and never disguised as a confident or trusted result. A failure is
never silently converted into a defect judgement.

Identified Phase 3 failure modes and required handling:

- **Model unavailable.** The inference implementation cannot be loaded or
  executed. The Inspection Engine must surface an explicit examination failure; it
  must not guess a verdict or emit a degraded result.
- **Malformed prediction.** The provider returns something that is not a valid
  `InspectionPrediction`, or violates the §6 contract. The engine must reject it
  in validation (§7 step 1) and surface the failure.
- **Incompatible prediction version.** The prediction's declared contract or
  metadata version is one the Inspection Engine does not accept. The engine must
  refuse it explicitly rather than coerce it.
- **Invalid localization.** A predicted localization is missing for a defective
  prediction, present for a non-defective one, or outside the normalized,
  ordered-bounds obligations. The engine must reject it as a partial/invalid
  prediction.
- **Invalid anomaly measure.** The predicted measure is non-finite, absent, or not
  marked raw. The engine must reject it.

General obligations for all Phase 3 failures:

- Failures **must** be explicit and inspectable, surfaced by the Inspection
  Engine, never swallowed.
- A failure **must not** be disguised as a confident, calibrated, or trusted
  result — the provider has no trust to assert in the first place.
- Failure handling **must not** import downstream responsibilities: the engine
  surfaces the failure; it does not route to review, qualify trust, or evaluate.
- **Inference non-reproducibility** (a fixed input yielding divergent predictions,
  indicating hidden inference state) must be treated as an Inspection-domain
  defect to be surfaced, consistent with the engine's existing reproducibility
  obligation (Inspection plan §9; `NonReproducibleInspection`), not tolerated.

This section fixes *which* failures must be handled and *how they must be
treated*. It does not fix concrete error types or mechanisms, which are
implementation choices.

---

## 10. Testing Strategy

Testing fixes *what must be demonstrated* about the seam; it does not fix a test
framework, harness, or tooling, and it does not test model quality (detection
quality is the Evaluation Engine's concern and is out of scope here).

The Phase 3 seam's tests must demonstrate, at minimum:

- **Provider isolation.** The `InspectionInferenceProvider` produces only an
  `InspectionPrediction` and exposes no `RawInspectionResult`, no trust field, no
  evidence record, no evaluation, and no routing — asserted as *must-not-exist*,
  guarding the seam.
- **Prediction validation.** A well-formed prediction is accepted, and each §6
  obligation is independently checked.
- **Deterministic transformation.** A fixed accepted prediction transforms to a
  fixed canonical `RawInspectionResult`, with the raw measure preserved as raw and
  `raw_measure_kind` unchanged.
- **Malformed prediction rejection.** Each failure mode in §9 (unavailable model,
  malformed prediction, incompatible version, invalid localization, invalid
  measure, inference non-reproducibility) is provoked and shown to be surfaced as
  an explicit Inspection-domain failure, never as a verdict or a trusted result.
- **Downstream contracts unchanged.** Trust, Review, Evidence, and Evaluation
  consume the canonical `RawInspectionResult` exactly as before; the existing
  integration chain and CLI run unchanged when inference is rule-based, and a
  learned provider that honours the canonical contract changes nothing downstream.

Testing principles:

- Tests assert the **boundary and contracts**, not accuracy. No test in this seam
  may smuggle in a detection-quality or calibration metric.
- Tests must use **fixed inputs and fixed predictions** so they are themselves
  reproducible.
- Tests should be small and focused, each covering one obligation (AGENTS.md
  Coding Rules).

The concrete test code, fixtures, and runner are produced during implementation,
not in this plan.

---

## 11. Out of Scope

This document defines only the permanent architectural boundary. It does **not**
authorize, choose, or introduce:

- model selection or model architecture;
- training, retraining, or fine-tuning;
- datasets or data collection;
- hyperparameters or learned/tuned parameters;
- GPU optimization or hardware acceleration choices;
- quantization or model compression;
- deployment, serving, or hosting;
- benchmarking, accuracy, precision/recall, or any performance/quality claim;
- frameworks, inference runtimes, or ML libraries as a chosen solution;
- any change to Trust Qualification, Human Review, Evidence, or Evaluation;
- any change to `README.md`, the prototype, `assets/`, the asset pipeline, the
  integration layer, the CLI, or any existing subsystem;
- any live, streaming, hosted, scheduled, or continuously operating behavior, or
  any feedback loop from review or evaluation into model updates (AGENTS.md Scope
  Protection; Phase 2 Closure §7).

Deferred scope remains deferred unless the public project documentation is updated
by the repository owner.

---

## 12. Future Extension Points

These name where later inference implementations attach to the boundary. Naming
them fixes the seam now; none is implemented here, and naming them grants no
licence to anticipate them or to choose among them.

Future `InspectionInferenceProvider` implementations may be built on inference
methods such as a CNN, a Transformer, a YOLO-style detector, or a foundation
vision model — **without changing**:

- the **Inspection Engine** (validation, transformation, canonical result,
  evidence emission);
- **Trust Qualification** (calibration and qualified outcomes still consume the
  canonical `RawInspectionResult`);
- **Human Review** (routing still consumes qualified cases, unchanged);
- **Evidence** (still preserves the canonical inspection evidence record);
- **Evaluation** (still measures only from preserved evidence).

Each such method is, by construction, an interchangeable implementation behind the
provider seam, returning the same abstract `InspectionPrediction` that the
Inspection Engine validates and transforms. This document names these methods only
as illustrations of the seam's generality. It chooses none of them.

Deferred scope remains deferred. An extension that would give Machine Learning
ownership of the runtime contract, let a prediction reach any domain directly, add
trust/routing/evidence/evaluation responsibility to the provider, or bend a
downstream contract around a model is, by definition, out of bounds and belongs to
no later architecture.

---

## Closing Statement

This plan fixes the permanent architectural seam between Machine Learning and the
Inspection Engine. Machine Learning, behind an `InspectionInferenceProvider`,
produces only an `InspectionPrediction`: an untrusted, non-canonical claim about
one stabilized input. The Inspection Engine validates every prediction and
deterministically transforms accepted ones into the canonical
`RawInspectionResult` it alone owns, emits its evidence, and surfaces every
failure inside the Inspection domain.

Because the architecture owns the contract and the model owns only a prediction,
Kalibra never depends directly on a model. Machine Learning plugs into the
architecture across one clean, validated, one-directional seam — and the
architecture does not bend around it.
