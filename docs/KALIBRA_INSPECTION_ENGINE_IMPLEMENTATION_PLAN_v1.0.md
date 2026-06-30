# Kalibra Inspection Engine Implementation Plan

## About This Plan

This document is the implementation plan for the **Inspection Engine**, the first
functional AI domain of Kalibra. It is an architecture-first plan: it fixes the
permanent engineering boundary of the Inspection Engine — what it owns, what it
refuses, what crosses its seams, and how it is validated — without choosing how
any of it is built.

The plan deliberately does **not** select machine-learning models, frameworks,
libraries, or datasets, and does **not** discuss training, calibration, or
evaluation metrics. Those belong to later phases and to other domains. This
document defines the boundary that all of those later choices must respect.

Throughout, **must** and **must not** express binding engineering obligations,
consistent with the language of
[`docs/KALIBRA_ENGINEERING_PLAN_v1.0.md`](KALIBRA_ENGINEERING_PLAN_v1.0.md) and
[`docs/KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md`](KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md).

---

## 1. Purpose

The Inspection Engine performs Kalibra's first act: it examines a stable visual
input and reaches a defect judgement, locating where any suspected defect lies
and measuring how anomalous the input is.

Its purpose is bounded and singular. The Inspection Engine answers exactly one
question — *is this input defective, and where?* — and produces the **raw
substrate** on which every downstream domain builds. It deliberately does not
decide whether its own answer can be trusted. That separation is the seam along
which the rest of Kalibra is organised (see Architecture §Core System and
§Self-Evaluation Layer).

The engine exists so that decision and trust can later be produced from one
source: the raw judgement and raw anomaly measure it emits are the single
examination that the Trust Qualification Engine must reuse, never reconstruct.

---

## 2. Responsibilities

The Inspection Engine **must**:

- **Accept inputs only in stable form.** Reason only about inputs that have
  already passed through the system's single, well-defined intake and have been
  placed into a stable, reproducible form (Requirement F1). The engine reasons
  about nothing that has not passed through that entry point.
- **Produce a defect judgement.** For each input, produce an overall judgement of
  whether the input is defective (Requirement F2).
- **Produce a localization.** For each input judged defective, indicate where
  within the input the suspected defect lies (Requirement F3).
- **Produce a raw anomaly measure.** Produce a raw, uncalibrated measure of how
  anomalous each input is, to serve as the substrate for trust qualification
  (Engineering Plan §Inspection Engine).
- **Treat the raw measure as raw.** Hand the raw measure downstream explicitly
  labelled as *not yet trustworthy confidence*, leaving its calibration to the
  Trust Qualification Engine.
- **Transform accepted predictions.** When an `InspectionPrediction` is
  explicitly passed to `InspectionEngine.transform_prediction(...)`, validate it
  and transform it into the canonical `RawInspectionResult` before evidence
  emission.
- **Emit a record.** Emit a durable record of each judgement, localization, and
  raw measure into the Evidence Engine as part of normal operation, so the
  engine's outputs are inspectable and regenerable.
- **Be reproducible.** Produce the same outputs from the same fixed input, with
  no hidden state that would prevent regeneration (Constraints C1, C2).

These responsibilities are the complete remit of the Inspection Engine. Anything
not listed here is, by design, not its job.

---

## 3. Explicit Non-Responsibilities

The Inspection Engine **must not** take on any of the following. Each belongs to
a named later domain, and the boundary is load-bearing:

- **Confidence calibration.** It must not map its raw measure into confidence, or
  present any score as calibrated confidence. *(Trust Qualification Engine.)*
- **Trust estimation / qualification.** It must not sort decisions into
  acceptable / rejectable / uncertain outcomes. *(Trust Qualification Engine.)*
- **Abstention.** It must not decline to decide; it always emits a raw judgement.
  Declining to act automatically is a qualified outcome decided elsewhere.
  *(Trust Qualification Engine.)*
- **Drift assessment.** It must not measure how far an input has drifted from
  familiar conditions, nor adjust its behaviour in response to drift.
  *(Trust Qualification Engine.)*
- **Review routing.** It must not decide that a case should go to a human, nor
  perform any hand-off. *(Human Review Engine.)*
- **Evidence custody.** It must not own, present, or arbitrate the evidence
  surface; it only emits records into it. *(Evidence Engine.)*
- **Performance evaluation.** It must not measure its own detection quality or
  any other dimension, nor judge whether its outputs are good.
  *(Evaluation Engine.)*

The engine must also not reach for any deferred scope (Engineering Plan
§Engineering Boundaries): no continuous, streaming, or live operation; no
hosting, serving, or deployment; no monitoring over time; no feedback loops from
human decisions; no parallel inspection settings; no exhaustive comparison of
detection approaches; and no reliance on live or continuously changing inputs.

A judgement leaving the Inspection Engine is **unqualified by design**. It is not
yet a decision Kalibra stands behind — that qualification is added downstream and
must not be anticipated here.

---

## 4. Inputs

The Inspection Engine accepts a single kind of input:

- **A stabilized inspection input.** A visual input that has already passed
  through the system's intake and been placed into a stable, reproducible form.
  The engine treats this stabilized form as immutable and authoritative.

**Input Intake is a prerequisite subsystem, not a domain.** Intake is the
system's single, well-defined entry point — the prerequisite subsystem that
places a raw visual input into the stable, reproducible form the Inspection
Engine consumes (Architecture §Core System; Requirement F1). It sits *upstream*
of the five permanent engineering domains and is **not** one of them: it is not a
sixth domain and not a separate engine. The Inspection Engine consumes intake's
product across the upstream seam; it does not perform intake. This consumes/emits
relationship is `Input Intake → Inspection Engine`.

Properties the input **must** satisfy before the engine reasons about it:

- It originates from the single, well-defined entry point (F1); the engine never
  ingests raw or unstabilized material directly.
- It is fixable into a known, unchanging starting point, so any result derived
  from it is regenerable (P1, P2).
- It carries enough identity to be referenced later in records (so a judgement
  can be tied back to the exact input that produced it). This plan does not fix
  the form of that identifier; it fixes only the obligation that one exist.

What the engine **must not** require or assume:

- Any label, ground-truth, or outcome annotation for the input. The engine
  produces a judgement; it is not told the answer.
- Any prior trust, confidence, drift, or routing information about the input.
  Such information does not exist yet at this stage of the flow.
- Any live, streaming, or mutable source. Inputs are drawn from a fixed body
  (C1, C4, X8).

The concrete representation of the stabilized input (its container, encoding, or
on-disk form) is intentionally left to implementation and to the Input Intake
subsystem (the prerequisite entry point described above). This plan fixes the
engine's *contract* with its input, not its storage.

---

## 5. Outputs

For each accepted input, the Inspection Engine emits exactly one **raw
inspection result** carrying:

- **A defect judgement** — an overall determination of whether the input is
  defective (F2).
- **A localization** — an indication of where within the input the suspected
  defect lies, present for inputs judged defective (F3).
- **A raw anomaly measure** — an uncalibrated measure of how anomalous the input
  is, explicitly marked as raw substrate and not as confidence.
- **A reference to the originating input** — so the result is traceable to the
  exact stabilized input that produced it (supports P1, E1).

Properties of the output that the plan fixes:

- The result is **raw**. It carries no calibrated confidence, no trust
  qualification, no abstention, no drift signal, and no routing decision. Any
  field that would imply trust must be absent, not stubbed.
- The result is **complete for one input**. Each input yields one result; the
  engine does not batch multiple inputs into one verdict or split one input
  across verdicts.
- The result is **emitted as evidence**. A durable record of the result is handed
  to the Evidence Engine as part of normal operation (E1).
- The result is **regenerable**. Re-running the engine on the same fixed input
  reproduces the same result (P2, C2).

The output is the engine's only product. Everything Kalibra later asserts about
trust is built on top of this raw result without modifying it.

`InspectionPrediction` is an ML-boundary object, not a runtime contract. It may
enter Inspection only through `InspectionEngine.transform_prediction(...)`.
`RawInspectionResult` remains the canonical runtime contract and the only raw
inspection object consumed downstream.

---

## 6. Domain Boundaries

The Inspection Engine sits first in Kalibra's directed flow and touches exactly
two other domains directly.

**Upstream seam — Input Intake → Inspection.**
The engine receives stabilized inputs from the Input Intake subsystem — the
single system entry point, a prerequisite subsystem that sits outside the five
engineering domains (it is not a sixth domain or a separate engine). The engine
treats what crosses this seam as immutable and reasons about nothing that has not
crossed it. The engine does not perform intake itself; it consumes its product.

**Downstream seam — Inspection → Trust Qualification.**
The engine hands its raw inspection results across a defined, stable seam to the
Trust Qualification Engine. What crosses this seam is the **single examination of
the single input** — the same judgement, localization, and raw measure that the
Trust Qualification Engine must reuse. This is the load-bearing seam that lets
decision and trust share one source (Engineering Plan §Engineering Dependencies).
The engine must not pre-empt anything on the far side of this seam.

**Lateral seam — Inspection → Evidence.**
The engine emits a record of each result into the Evidence Engine. It emits into
the evidence backbone; it does not own, curate, or present it.

Boundaries the engine must hold:

- It must not call back into, depend on, or anticipate the Trust Qualification,
  Human Review, Evidence-presentation, or Evaluation logic. Responsibilities must
  not bleed across the seam for convenience (Engineering Plan §Engineering
  Principles).
- It must not be the place where a decision becomes trusted. A result leaving the
  engine is explicitly unqualified.
- It must not depend on any domain that has not yet established its
  responsibility; the engine is engineered to stand on intake alone.

---

## 7. Internal Processing Stages

The engine's internal work is described here as **responsibility stages**, not as
an algorithm. The stages fix *what must happen in order*, not *how* any stage is
implemented. No model, technique, or framework is chosen here.

1. **Intake acceptance.** Receive a stabilized input across the upstream seam and
   confirm it is in the expected stable form. Reject — as a failure mode (§9),
   not as a defect judgement — anything that has not properly passed intake.

2. **Examination.** Assess the input for the presence of a defect. This stage is
   the engine's single examination of the single input; its product is reused by
   later stages and must not be reconstructed.

   The current implementation supports three examination sources:

   - `DeterministicPlaceholderExaminer` — the default examiner used by
     `InspectionEngine()` and by substrate integration.
   - `DeterministicImageBaselineExaminer` — an opt-in deterministic local image
     baseline selected only by constructing
     `InspectionEngine(examiner=DeterministicImageBaselineExaminer())`.
   - `InspectionPrediction` transformation path — an explicit path selected
     only by calling `InspectionEngine.transform_prediction(input, prediction)`.
     This path validates an already-produced prediction and transforms it into
     `RawInspectionResult`; it is not part of `InspectionEngine.inspect()`.

   The image baseline reads local grayscale PGM P2 artifacts, computes a
   deterministic raw local-contrast measure, and returns the same downstream
   examination contract as the placeholder examiner. It exists to exercise the
   Inspection boundary with real image artifacts. It does not implement ML,
   production computer vision, calibration, trust qualification, review routing,
   evaluation, benchmark measurement, or performance claims.

   ML Phase 1 also defines `InspectionInferenceProvider` and the concrete
   `DeterministicMockInferenceProvider`. The provider is a deterministic,
   framework-independent architecture-validation provider only. It produces
   `InspectionPrediction`, is not wired into `InspectionEngine.inspect()`, is not
   a Machine Learning runtime, and is not production inference. The provider does
   not produce `RawInspectionResult`; the Inspection Engine owns the
   transformation from prediction to raw result.

3. **Judgement formation.** Derive, from the examination, an overall judgement of
   whether the input is defective.

4. **Localization.** For an input judged defective, derive from the same
   examination an indication of where the suspected defect lies.

5. **Raw scoring.** Derive from the same examination a raw, uncalibrated measure
   of how anomalous the input is, and mark it explicitly as raw substrate.

6. **Result assembly.** Assemble the judgement, localization, raw measure, and a
   reference to the originating input into one raw inspection result.

7. **Evidence emission.** Emit a durable record of the assembled result into the
   Evidence Engine.

Ordering obligations:

- Stages 3, 4, and 5 must draw on the **same examination** produced in stage 2,
  so that judgement, localization, and raw measure are one perspective on one
  input — never independently reconstructed views.
- No stage may introduce calibration, qualification, abstention, drift, routing,
  or evaluation. If a stage appears to need any of these, the need belongs to a
  different domain and the seam, not this engine.
- Every stage must be deterministic with respect to a fixed input so the whole
  sequence is regenerable.

---

## 8. Data Contracts

This section fixes the **shape and obligations** of what the engine consumes and
produces, expressed as abstract contracts. Concrete types, encodings, field
names, and storage formats are deliberately left to implementation; only the
obligations below are binding.

**Contract A — Stabilized Input (consumed).**
- Must carry the stable, reproducible representation of one visual input.
- Must carry a stable identity by which the input can be referenced later.
- Must be treated as immutable by the engine.
- Must not carry trust, confidence, drift, routing, or label information (none
  exists at this stage).

**Contract B — Raw Inspection Result (produced).**
- Must carry the defect judgement for the input.
- Must carry the localization for inputs judged defective.
- Must carry the raw, uncalibrated anomaly measure, explicitly marked as raw.
- Must carry a reference to the originating input's identity.
- Must not carry any calibrated confidence, qualified outcome, abstention, drift
  signal, or routing decision. Trust-bearing fields must be *absent*, not present
  and empty.
- Remains the canonical runtime contract for Inspection and for every downstream
  domain.

**Contract C — Inspection Evidence Record (emitted).**
- Must durably preserve the raw inspection result and its link to the originating
  input (E1).
- Must be regenerable from the same fixed input (P2).
- Must faithfully represent the result as raw; it must not present the result as
  stronger or more trustworthy than it is.

**Contract D — Inspection Prediction (accepted for transformation only).**
- Must be produced by an `InspectionInferenceProvider`; the current concrete
  provider is `DeterministicMockInferenceProvider`.
- Must carry a prediction identity, input identity, predicted judgement,
  predicted raw anomaly measure, and localization only when the prediction is
  defective.
- Must remain a pre-runtime boundary object. It is not emitted downstream and is
  not consumed directly by Trust, Review, Evidence, Evaluation, Integration, or
  CLI code.
- Must not carry calibrated confidence, qualified outcome, review routing,
  evaluation, evidence, persistence, model update, training, or UI authority.

Contract invariants:

- **Single source.** The judgement, localization, and raw measure within one
  Raw Inspection Result must originate from one examination of one input. The
  contract exists to make that single source carryable across the downstream
  seam without reconstruction (R2).
- **Rawness is explicit.** The raw measure must be self-describing as raw, so no
  downstream consumer can mistake it for calibrated confidence (R3 is satisfied
  downstream, but the contract must not enable its violation here).
- **Traceability.** Every produced and emitted artifact must be tied back to the
  exact input that produced it.
- **Descriptive labels may differ by examiner.** The current implementation
  accepts distinct `examination_kind` and `raw_measure_scale` labels for the
  placeholder examiner, local image baseline examiner, and prediction-origin
  transformation path, while preserving `raw_measure_kind =
  "raw_anomaly_measure"` as the downstream-compatible raw measure kind.
- **Prediction transformation is Inspection-owned.** The implemented path is
  `InspectionPrediction → InspectionEngine.transform_prediction(...) →
  RawInspectionResult → InspectionEvidenceRecord`. Providers never own
  `RawInspectionResult` or evidence emission.
- **Downstream consumers see only raw results.** No downstream subsystem consumes
  `InspectionPrediction` directly; all downstream domains continue to consume
  `RawInspectionResult`.

---

## 9. Failure Modes

The Inspection Engine must distinguish **inspection outcomes** (a defect
judgement, which is normal) from **engine failures** (the engine cannot produce a
valid result). A failure is never silently converted into a defect judgement.

Identified failure modes and required handling:

- **Unstabilized or malformed input.** Input did not properly pass intake, or is
  not in the expected stable form. The engine must refuse to produce a judgement
  and must surface the failure explicitly; it must not guess a verdict.
- **Missing or unreferenceable input identity.** The input cannot be tied to a
  stable identity. The engine must refuse, because an untraceable result would
  violate the traceability invariant (§8).
- **Examination cannot complete.** The engine cannot form an examination of the
  input. It must surface this as an engine failure, distinct from a "not
  defective" judgement.
- **Partial result.** A judgement could be formed but localization or raw measure
  could not, or vice versa. The engine must not emit a partial Raw Inspection
  Result as if complete; an incomplete result must be surfaced as a failure
  against Contract B.
- **Malformed or invalid prediction.** A value passed to
  `transform_prediction(...)` is not an `InspectionPrediction`, references a
  different input, uses unsupported provenance labels, carries a non-finite raw
  measure, or violates localization rules. The engine must refuse
  transformation and must not convert the failure into a judgement.
- **Evidence emission failure.** The result was assembled but could not be
  recorded. Because evidence is an obligation of normal operation (E1), the
  engine must surface this rather than report success without a record.
- **Non-reproducibility.** Re-running on the same fixed input yields a different
  result, indicating hidden state. This violates C2/P2 and must be treated as a
  defect in the engine to be surfaced, not tolerated.

General obligations for all failure modes:

- Failures must be **explicit and inspectable**, never swallowed.
- A failure must never be **disguised as a confident or trusted result**; the
  engine has no trust to assert in the first place.
- Failure handling must not import downstream responsibilities (it must not, for
  example, "route to review" — it only surfaces the failure).

This plan fixes *which* failures must be handled and *how they must be treated*.
It does not fix the concrete error types or mechanisms, which are implementation
choices.

---

## 10. Validation Strategy

Validation here means confirming the engine honours its boundary and contracts —
**not** measuring detection quality, which is the Evaluation Engine's job and is
out of scope for this plan. No metrics are defined.

The Inspection Engine must be validated against:

- **Contract conformance.** Every produced Raw Inspection Result conforms to
  Contract B: it carries judgement, localization (when defective), a raw measure
  marked raw, and an input reference — and carries no trust-bearing fields.
- **Boundary conformance.** The engine performs no calibration, qualification,
  abstention, drift assessment, routing, evidence custody, or evaluation. The
  absence of these responsibilities is itself validated, not assumed.
- **Single-source conformance.** Judgement, localization, and raw measure for one
  input demonstrably originate from one examination of that input.
- **Examination-source conformance.** Both current examiners exercise the
  `InspectionExaminer` protocol, and the explicit prediction transformation path
  exercises the `InspectionInferenceProvider` boundary while preserving the same
  downstream raw inspection contract.
- **Reproducibility.** The same fixed input yields the same result and the same
  emitted record on re-run (C2, P2).
- **Traceability.** Every result and record is tied back to the exact originating
  input.
- **Failure handling.** Each failure mode in §9 is surfaced explicitly and is
  never converted into a silent verdict or a disguised "confident" result.
- **Intake discipline.** The engine reasons only about inputs that passed intake
  and refuses anything that did not.

Validation must rest on **inspectable evidence** (the emitted records), so that an
observer can verify conformance without trusting the engine's word, consistent
with Kalibra's evidence-before-assertion philosophy.

---

## 11. Testing Strategy

Testing fixes *what must be demonstrated* about the engine; it does not fix a
test framework, harness, or tooling, and it does not test model quality.

The engine's test suite must demonstrate, at minimum:

- **Contract tests.** Given a well-formed stabilized input, the engine produces a
  Raw Inspection Result that satisfies Contract B in full, including the explicit
  absence of trust-bearing fields and the explicit "raw" marking of the measure.
- **Boundary tests (negative).** The engine exposes no calibrated confidence, no
  qualified outcome, no abstention, no drift signal, and no routing decision in
  any output. These are asserted as *must-not-exist*, guarding the seam.
- **Single-source tests.** Judgement, localization, and raw measure for one input
  are shown to derive from one examination — for example, by demonstrating they
  cannot diverge to refer to different inputs or different examinations.
- **Reproducibility tests.** Re-running on an identical fixed input yields
  identical results and identical emitted records.
- **Traceability tests.** Each result and record references the exact originating
  input.
- **Failure-mode tests.** Each failure mode in §9 (unstabilized input, missing
  identity, examination failure, partial result, evidence-emission failure,
  invalid prediction, non-reproducibility) is provoked and shown to be surfaced
  explicitly and not disguised as a verdict.
- **Prediction-boundary tests.** A deterministic provider output can be
  transformed only by explicitly calling `InspectionEngine.transform_prediction`;
  provider output is an `InspectionPrediction`, provider methods do not emit
  evidence, and the default `InspectionEngine.inspect()` path remains unchanged.
- **Intake-discipline tests.** Input that has not passed intake is refused rather
  than judged.

Testing principles:

- Tests assert the engine's **boundary and contracts**, not its accuracy. No test
  in this domain may smuggle in a detection-quality or calibration metric.
- Tests must use **fixed inputs** so they are themselves reproducible (C2).
- Tests should be small and focused, each covering one obligation, consistent
  with Kalibra's coding rules (small, testable modules).

The concrete test code, fixtures, and runner are produced during implementation,
not in this plan.

---

## 12. Future Extension Points

These are points where later domains and later phases attach to the Inspection
Engine. Naming them fixes the boundary now; none of them is implemented by the
engine, and naming them grants no licence to anticipate them.

- **Trust Qualification attaches at the downstream seam.** Calibration,
  qualification, abstention, and drift response consume the Raw Inspection
  Result via Contract B and the single examination it carries. The seam is the
  designed extension point; the raw measure is deliberately shaped to be
  calibratable later without being calibrated now.
- **Evidence presentation builds on emitted records.** The Evidence Engine's
  inspectable surface is built over the records this engine emits (Contract C).
  The engine's obligation is faithful emission; presentation is the extension.
- **Evaluation consumes recorded evidence.** The Evaluation Engine later measures
  detection quality and other dimensions from the emitted records — never from
  inside this engine, and never by adding evaluation logic here.
- **Examination internals are replaceable.** Because this plan fixes the engine's
  contracts and seams but not its examination technique, the implementation now
  supports both the default deterministic placeholder examiner and the opt-in
  deterministic local image baseline examiner without changing the engine's
  boundary. ML Phase 1 also supports explicit transformation of
  `InspectionPrediction` through `InspectionEngine.transform_prediction(...)`.
  The `InspectionExaminer` and `InspectionInferenceProvider` boundaries have
  therefore both been exercised while preserving the same downstream contract.
- **The input contract can carry richer stabilized inputs.** Additional
  stabilized-input characteristics may be added at intake without changing the
  engine's responsibility, provided Contract A's obligations continue to hold.

Deferred scope remains deferred (Engineering Plan §Engineering Boundaries). An
extension that would give the Inspection Engine trust, routing, evidence custody,
evaluation, or any live/streaming behaviour is, by definition, out of bounds and
belongs to a later architecture, not to this engine.

---

## Closing Statement

This plan fixes the permanent engineering boundary of the Kalibra Inspection
Engine. The engine examines one stabilized input, reaches a defect judgement,
locates the suspected defect, and emits a raw anomaly measure — and stops there,
on purpose. It calibrates nothing, qualifies nothing, defers nothing, routes
nothing, curates no evidence, and evaluates nothing. It produces the single raw
examination that the rest of Kalibra depends on, hands it across a clean seam,
records it as evidence, and claims no trust it has not earned.

Engineered to this boundary, the Inspection Engine becomes the dependable first
act of Kalibra: the one source from which both the decision and, later, the
judgement of that decision's trustworthiness are drawn.
