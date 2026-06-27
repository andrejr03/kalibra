# Kalibra Trust Qualification Engine Implementation Plan

## About This Plan

This document is the implementation plan for the **Trust Qualification Engine**,
Kalibra's second act. It consumes the raw inspection result produced by the
[Inspection Engine](KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md) and
determines how far that raw result can be trusted.

It is an architecture-first plan: it fixes the permanent engineering boundary of
the Trust Qualification Engine — what it owns, what it refuses, what crosses its
seams, and how it is validated — without choosing how any of it is built.

The plan deliberately does **not** select machine-learning models, frameworks,
libraries, or datasets, does **not** discuss training implementation, and does
**not** define final evaluation metrics. Those belong to later phases and to
other domains. This document defines the boundary those later choices must
respect.

Throughout, **must** and **must not** express binding engineering obligations,
consistent with the language of
[`docs/KALIBRA_ENGINEERING_PLAN_v1.0.md`](KALIBRA_ENGINEERING_PLAN_v1.0.md) and
[`docs/KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md`](KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md).

---

## 1. Purpose

The Trust Qualification Engine performs Kalibra's second act: it takes the raw
judgement of the Inspection Engine and decides **how far that judgement can be
relied upon**. It shares the same input and the same underlying examination — it
is a second perspective on one system, not a separate system (Architecture
§Self-Evaluation Layer).

Its purpose is to ensure that **no decision leaves Kalibra without a defensible,
calibrated statement of how much it can be trusted** (Requirement R1). It turns a
raw, uncalibrated anomaly measure into calibrated confidence, sorts each decision
into a qualified outcome (accept, review, reject, or abstain), and grows more
cautious as inputs drift from familiar conditions.

The engine is the architectural expression of Kalibra's thesis. It answers the
second of Kalibra's two questions — *can the system be trusted when it says
so?* — and its obligations may not be weakened to simplify any other domain
(Engineering Plan §Trust Qualification Engine).

---

## 2. Responsibilities

The Trust Qualification Engine **must**:

- **Consume the raw inspection result.** Receive, across the defined upstream
  seam, the raw defect judgement, the raw anomaly measure, and the localization
  reference — the single examination of one input — and reason about that result
  rather than about the image.
- **Calibrate confidence.** Map the raw anomaly measure into confidence that
  means what it says, so a stated level of certainty corresponds to the real
  chance of being correct (Requirement R3). It must not present an uncalibrated
  measure as confidence.
- **Qualify the outcome.** Sort each calibrated decision into an outcome
  reflecting its trustworthiness — clearly acceptable, clearly rejectable, or
  uncertain (Requirement F5).
- **Identify uncertainty.** Recognise the cases whose confidence is insufficient
  to act on automatically, so they can be qualified as uncertain.
- **Support abstention.** Decline to decide automatically when confidence is
  insufficient, treating abstention as a valid qualified outcome and not a
  failure (Requirement F6).
- **Support accept / review / reject qualification.** Produce the accept, review,
  and reject qualifications, where review is an engineered outcome for the
  uncertain, not an error state.
- **Apply drift-aware caution where available.** Assess how far an input has
  drifted from familiar conditions and increase caution accordingly — deferring
  more as that distance grows (Requirement F7) — without overwriting any raw
  inspection output.
- **Operate on one source.** Use the same examination of the same input as the
  Inspection Engine, never an independently reconstructed one (Requirement R2).
- **Emit trust qualification records.** Emit a durable record of every
  calibration, qualification, abstention, and drift response into the Evidence
  Engine as part of normal operation (Requirement E1), preserving both the raw
  inspection result and the trust qualification result.

These responsibilities are the complete remit of the engine. Anything not listed
here is, by design, not its job.

---

## 3. Explicit Non-Responsibilities

The Trust Qualification Engine **must not** take on any of the following. Each
belongs to a named domain, and the boundary is load-bearing:

- **Inspect images directly.** It must not examine the visual input. Examination
  happened upstream. *(Inspection Engine.)*
- **Reconstruct inspection results.** It must not re-derive the judgement,
  localization, or anomaly measure; it reuses them. *(Inspection Engine.)*
- **Modify the raw inspection result.** It must not mutate, overwrite, or correct
  any field of the raw inspection result. The raw result is immutable to it.
- **Perform human review.** It identifies and qualifies cases needing review; it
  does not present cases to humans or collect their judgement. *(Human Review
  Engine.)*
- **Route cases operationally.** It produces the *review* qualification; the
  operational direction and hand-off of those cases is not its job. *(Human
  Review Engine.)*
- **Own evidence presentation.** It emits records; it does not curate or present
  the inspectable surface. *(Evidence Engine.)*
- **Evaluate model performance.** It must not measure detection quality,
  calibration quality, uncertainty quality, review quality, or drift response.
  *(Evaluation Engine.)*
- **Train models, choose ML frameworks, or choose datasets.** These are out of
  scope for this plan and this engine's boundary.

The engine must also not reach for any deferred scope (Engineering Plan
§Engineering Boundaries): no continuous, streaming, or live operation; no
hosting, serving, or deployment; no monitoring over time; no feedback loops from
human decisions into system updates; no parallel inspection settings; and no
reliance on live or continuously changing inputs.

---

## 4. Inputs

The Trust Qualification Engine accepts a single kind of input:

- **A raw inspection result.** The complete result emitted by the Inspection
  Engine for one input, carrying the raw defect judgement, the raw (uncalibrated)
  anomaly measure, the localization reference (for inputs judged defective), and
  a reference to the originating stabilized input. (See Inspection Engine plan
  §8, Contract B.)

Optionally, where the capability exists:

- **A drift reference.** A fixed characterisation of familiar conditions against
  which an input's drift can be assessed. Drift-aware caution applies *where
  available*; when no drift reference exists, the engine qualifies without a
  drift adjustment and discloses that plainly rather than inventing one.

Properties the input **must** satisfy:

- It must be the genuine upstream result, reused across the defined seam — not a
  reconstruction (R2).
- Its raw anomaly measure must be treated as **raw substrate, not confidence**
  (core boundary). The engine is the place calibration happens; the input arrives
  uncalibrated by contract.
- It must carry the originating-input reference, so the qualified outcome remains
  traceable to the exact input and examination that produced it (P1, E1).

What the engine **must not** require or assume:

- Any access to the raw image or to intake; it reasons about the inspection
  result, not the picture.
- Any pre-existing confidence, qualification, routing, or human judgement; none
  exists yet at this stage of the flow.
- Any label or ground-truth for the input; calibration learned in a later phase
  is applied here, but the engine is not told the per-input answer.

The concrete representation of these inputs is left to implementation; this plan
fixes the engine's *contract* with them.

---

## 5. Outputs

For each raw inspection result, the engine emits exactly one **trust
qualification result** carrying:

- **Calibrated confidence** — the raw anomaly measure mapped into confidence that
  corresponds to observed correctness, explicitly marked as calibrated (R3).
- **A qualified outcome** — one of *accept*, *review*, *reject*, or *abstain*,
  reflecting how far the decision can be trusted (F5, F6).
- **An uncertainty characterisation** — the basis on which the case was treated
  as confident or uncertain.
- **A drift-aware caution annotation** — where a drift reference is available, the
  assessed drift and the caution it induced; where unavailable, an explicit
  disclosure of its absence (F7, E5).
- **A reference to the raw inspection result** — binding the qualification to the
  exact upstream result and, through it, to the originating input.

Properties the plan fixes:

- The output is **additive, never destructive.** It accompanies the raw
  inspection result; it does not replace or mutate it. Both the raw inspection
  result and the trust qualification result are preserved (core boundary).
- **Confidence is calibrated.** No output may present the raw measure, or any
  uncalibrated value, as confidence (R3).
- **Abstention and review are valid outcomes.** *Abstain* and *review* are
  first-class qualified outcomes, emitted with the same standing as *accept* and
  *reject* — not error states.
- The output is **emitted as evidence.** A durable record of both the raw result
  and its qualification is handed to the Evidence Engine (E1).
- The output is **regenerable** from the same fixed inputs (P2, C2).

The qualified outcome is what allows a decision to leave Kalibra defensibly; the
Human Review Engine later acts on the *review* and drifted outcomes this engine
produces.

---

## 6. Domain Boundaries

The Trust Qualification Engine sits second in Kalibra's directed flow and touches
three other domains directly.

**Upstream seam — Inspection → Trust Qualification.**
The engine receives the raw inspection result across the defined, stable seam.
What crosses this seam is the **single examination of the single input**. The
engine reuses it and treats it as immutable; it must not re-inspect the image or
reconstruct the result (R2, core boundary). This is the load-bearing seam that
lets decision and trust share one source (Engineering Plan §Engineering
Dependencies).

**Downstream seam — Trust Qualification → Human Review.**
The engine passes outcomes qualified as *review* or arising from drifted inputs
toward the Human Review Engine. It produces the qualification that warrants
deferral; it does not itself perform the operational routing, hand-off, or human
adjudication.

**Lateral seam — Trust Qualification → Evidence.**
The engine emits a record of every calibration, qualification, abstention, and
drift response into the Evidence Engine, preserving both the raw inspection
result and the trust qualification result. It emits into the evidence backbone;
it does not own or present it.

Boundaries the engine must hold:

- It must not bypass itself: no decision may leave Kalibra unqualified, and the
  engine must not be circumvented (AGENTS.md Architectural Rules).
- It must not separate trust qualification from the same inspection source it
  qualifies (AGENTS.md Architectural Rules; R2).
- It must not mutate the inspection record, nor let drift handling overwrite raw
  inspection outputs (core boundary).
- It must not take on Human Review, Evidence presentation, or Evaluation
  responsibilities; responsibilities must not bleed across the seam for
  convenience (Engineering Plan §Engineering Principles).

---

## 7. Internal Processing Stages

The engine's internal work is described here as **responsibility stages**, not as
an algorithm. The stages fix *what must happen in order*, not *how* any stage is
implemented. No model, technique, calibration method, or framework is chosen
here.

1. **Result intake.** Receive a raw inspection result across the upstream seam and
   confirm it is a complete, well-formed upstream result carrying its
   originating-input reference. Reject — as a failure mode (§9), not as a
   qualified outcome — anything malformed or reconstructed.

2. **Calibration.** Map the raw anomaly measure into calibrated confidence, so the
   stated certainty corresponds to observed correctness. Mark the result
   explicitly as calibrated. The raw measure is read, never altered.

3. **Drift-aware caution (where available).** If a drift reference is available,
   assess how far the input has drifted and determine the additional caution that
   drift induces. This adjustment influences qualification only; it must not
   overwrite the raw inspection outputs or the calibrated confidence's provenance.
   If no drift reference is available, record its absence and proceed without a
   drift adjustment.

4. **Uncertainty identification.** From the calibrated confidence and any drift
   caution, determine whether the case is confident enough to act on
   automatically or should be treated as uncertain.

5. **Outcome qualification.** Sort the decision into one qualified outcome —
   *accept*, *reject*, *review*, or *abstain* — reflecting its trustworthiness.
   *Review* and *abstain* are engineered outcomes, not failures.

6. **Result assembly.** Assemble the calibrated confidence, the qualified outcome,
   the uncertainty characterisation, the drift-caution annotation, and a reference
   to the raw inspection result into one trust qualification result. The raw
   inspection result is carried alongside, unmodified.

7. **Evidence emission.** Emit a durable record preserving **both** the raw
   inspection result and the trust qualification result into the Evidence Engine.

Ordering obligations:

- Calibration (stage 2) must precede uncertainty identification and qualification;
  the engine must never qualify on an uncalibrated value (R3, core boundary).
- Drift caution (stage 3) may **increase** caution but must not rewrite raw
  inspection outputs or fabricate confidence (core boundary).
- No stage may inspect the image, reconstruct the inspection result, perform human
  review, route operationally, or evaluate performance. If a stage appears to need
  any of these, the need belongs to a different domain and the seam, not this
  engine.
- Every stage must be deterministic with respect to fixed inputs so the whole
  sequence is regenerable (C2, P2).

---

## 8. Data Contracts

This section fixes the **shape and obligations** of what the engine consumes and
produces, expressed as abstract contracts. Concrete types, encodings, field
names, calibration mechanisms, and storage formats are deliberately left to
implementation; only the obligations below are binding.

**Contract A — Raw Inspection Result (consumed).**
- Carries the raw defect judgement, the raw (uncalibrated) anomaly measure, the
  localization reference, and the originating-input reference.
- Is treated as **immutable**: the engine reads it and must not mutate, overwrite,
  or correct any field.
- Its anomaly measure must be treated as raw substrate, never as confidence.

**Contract B — Drift Reference (consumed, optional).**
- Carries a fixed characterisation of familiar conditions, used only to assess an
  input's drift.
- Is treated as immutable.
- When absent, the engine must proceed and disclose the absence (E5); it must not
  fabricate a drift signal.

**Contract C — Trust Qualification Result (produced).**
- Carries calibrated confidence, explicitly marked as calibrated.
- Carries one qualified outcome from the fixed set {accept, reject, review,
  abstain}.
- Carries an uncertainty characterisation.
- Carries a drift-aware caution annotation, or an explicit disclosure that drift
  assessment was unavailable.
- Carries a reference to the raw inspection result it qualifies (and through it,
  the originating input).
- Must not contain any mutated copy of the raw inspection result; it accompanies,
  never replaces it.

**Contract D — Trust Qualification Evidence Record (emitted).**
- Durably preserves **both** the raw inspection result and the trust
  qualification result, bound together (E1, core boundary).
- Is regenerable from the same fixed inputs (P2).
- Faithfully represents calibrated confidence as calibrated and raw measures as
  raw; it must not present a result as stronger than its evidence allows (E2, R7).

Contract invariants:

- **Single source.** The qualification must derive from the same examination of
  the same input as the raw inspection result it qualifies; the two are never
  produced by separate, independently reconciled processes (R2).
- **Calibration is explicit.** Confidence must be self-describing as calibrated,
  and the raw measure must remain self-describing as raw, so neither can be
  mistaken for the other (R3).
- **Non-destruction.** The raw inspection result remains intact and recoverable
  alongside its qualification (core boundary).
- **Traceability.** Every produced and emitted artifact is tied back to the exact
  raw inspection result and originating input.

---

## 9. Failure Modes

The engine must distinguish **qualified outcomes** (accept / reject / review /
abstain — all normal) from **engine failures** (the engine cannot produce a valid
trust qualification result). A failure is never silently converted into a
qualified outcome, and *abstain* must never be used to mask a failure.

Identified failure modes and required handling:

- **Malformed or incomplete raw inspection result.** The upstream result is
  missing required fields or is not well-formed. The engine must refuse to
  qualify and surface the failure; it must not invent a qualification.
- **Reconstructed or untraceable input.** The result cannot be tied to a genuine
  upstream examination and originating input. The engine must refuse, because an
  untraceable qualification would violate single-source and traceability
  invariants (R2, §8).
- **Calibration cannot be applied.** The engine cannot map the raw measure into
  calibrated confidence. It must surface this as a failure and must not present
  the uncalibrated measure as confidence (R3). It must not silently emit *abstain*
  to hide that calibration was impossible.
- **Missing drift reference.** No drift reference is available. This is **not** a
  failure: the engine proceeds without drift adjustment and discloses the absence
  (E5). It is listed here to fix that it must be handled gracefully, not as an
  error.
- **Attempted mutation of the raw result.** Any internal path that would alter the
  raw inspection result is a defect to be prevented; the raw result must remain
  immutable (core boundary).
- **Evidence emission failure.** The trust qualification result was assembled but
  the combined record (raw + qualification) could not be preserved. Because
  evidence is an obligation of normal operation (E1), the engine must surface this
  rather than report success without a record.
- **Non-reproducibility.** Re-running on the same fixed inputs yields a different
  qualified outcome, indicating hidden state. This violates C2/P2 and must be
  surfaced as a defect, not tolerated.

General obligations for all failure modes:

- Failures must be **explicit and inspectable**, never swallowed.
- A failure must never be **disguised as a confident, qualified, or abstained
  result**; *abstain* is a designed outcome, not a failure channel.
- Failure handling must not import downstream responsibilities (it must not, for
  example, perform human routing — it only surfaces the failure).

This plan fixes *which* failures must be handled and *how they must be treated*;
the concrete error mechanisms are implementation choices.

---

## 10. Validation Strategy

Validation here means confirming the engine honours its boundary and contracts —
**not** measuring calibration quality or detection quality, which is the
Evaluation Engine's job and out of scope for this plan. No final evaluation
metrics are defined.

The engine must be validated against:

- **Reuse, not re-inspection.** Every qualification is shown to be derived from
  the consumed raw inspection result, with no access to or examination of the
  image, and no reconstruction of the inspection result (R2, core boundary).
- **Calibration-before-confidence.** No output presents the raw measure or any
  uncalibrated value as confidence; confidence is always marked calibrated (R3).
- **Outcome conformance.** Every qualified outcome is one of {accept, reject,
  review, abstain}; *review* and *abstain* are emitted as valid outcomes, never as
  errors.
- **Non-destruction.** The raw inspection result is unchanged after qualification,
  and both raw result and qualification are preserved together in the emitted
  record (core boundary, E1).
- **Drift discipline.** Where a drift reference exists, drift can only increase
  caution and never overwrites raw inspection outputs; where it is absent, the
  absence is disclosed rather than fabricated (F7, E5, core boundary).
- **Boundary conformance.** The engine performs no human review, no operational
  routing, no evidence presentation, and no performance evaluation. The absence of
  these responsibilities is validated, not assumed.
- **Single-source and traceability.** Each qualification ties back to the exact
  raw inspection result and originating input (R2, P1).
- **Reproducibility.** The same fixed inputs yield the same qualification and the
  same emitted record on re-run (C2, P2).
- **Failure handling.** Each failure mode in §9 is surfaced explicitly and is
  never converted into a silent or disguised qualified outcome.

Validation must rest on **inspectable evidence** (the emitted records), so an
observer can verify conformance without trusting the engine's word, consistent
with Kalibra's evidence-before-assertion philosophy.

---

## 11. Testing Strategy

Testing fixes *what must be demonstrated* about the engine; it does not fix a test
framework, harness, or tooling, and it does not test calibration or detection
quality.

The engine's test suite must demonstrate, at minimum:

- **Reuse tests.** Given a raw inspection result, the engine qualifies it without
  any image access or reconstruction; attempts to re-inspect are shown to be
  absent from the engine's surface.
- **Calibration-marking tests.** The calibrated confidence in every output is
  marked calibrated, and no path emits the raw measure as confidence (core
  boundary, R3). *(Tests assert the marking and provenance, not the calibration's
  statistical quality.)*
- **Outcome tests.** Each of {accept, reject, review, abstain} can be produced and
  is treated as a valid qualified outcome; *review* and *abstain* are not error
  states.
- **Non-destruction tests.** After qualification, the raw inspection result is
  byte-for-byte unchanged, and the emitted record contains both the raw result
  and the qualification bound together.
- **Drift tests.** With a drift reference, increased drift can only increase
  caution and never alters raw inspection outputs; without a drift reference, the
  engine proceeds and discloses the absence.
- **Boundary tests (negative).** The engine exposes no human-review, no
  operational-routing, no evidence-presentation, and no evaluation behaviour;
  these are asserted as *must-not-exist*, guarding the seams.
- **Single-source / traceability tests.** Each qualification references the exact
  raw inspection result and originating input.
- **Reproducibility tests.** Re-running on identical fixed inputs yields identical
  qualifications and identical emitted records.
- **Failure-mode tests.** Each failure mode in §9 (malformed result,
  reconstructed/untraceable input, calibration-not-applicable,
  evidence-emission failure, non-reproducibility) is provoked and shown to be
  surfaced explicitly and not disguised as a qualified outcome — and a missing
  drift reference is shown to be handled gracefully, not as a failure.

Testing principles:

- Tests assert the engine's **boundary and contracts**, not its calibration or
  detection accuracy. No test in this domain may smuggle in a calibration-quality
  or detection-quality metric.
- Tests must use **fixed inputs** so they are themselves reproducible (C2).
- Tests should be small and focused, each covering one obligation, consistent with
  Kalibra's coding rules (small, testable modules).

The concrete test code, fixtures, and runner are produced during implementation,
not in this plan.

---

## 12. Future Extension Points

These are points where later phases and other domains attach to the Trust
Qualification Engine. Naming them fixes the boundary now; none grants licence to
absorb another domain's responsibility.

- **Calibration method is replaceable.** Because this plan fixes the engine's
  contracts and seams but not its calibration technique, the method chosen in a
  later phase can be implemented and later replaced without changing the engine's
  boundary, provided calibrated confidence remains marked calibrated and the raw
  measure remains untouched (Contracts A, C).
- **Drift assessment attaches via the drift reference.** Drift-aware caution is
  applied *where available*; richer drift references or assessments can be
  introduced via Contract B without changing the engine's responsibility, and must
  continue to only increase caution, never overwrite raw outputs.
- **Human Review consumes the qualified outcome at the downstream seam.** The
  Human Review Engine builds on the *review* and drifted outcomes this engine
  produces; operational routing and hand-off are the extension, not this engine's
  job.
- **Evidence presentation builds on emitted records.** The Evidence Engine's
  inspectable surface is built over the combined raw-plus-qualification records
  this engine emits (Contract D). Faithful emission is the obligation;
  presentation is the extension.
- **Evaluation consumes recorded evidence.** The Evaluation Engine later measures
  calibration, uncertainty quality, review quality, and drift response from the
  emitted records — never from inside this engine, and never by adding evaluation
  logic here.

Deferred scope remains deferred (Engineering Plan §Engineering Boundaries). An
extension that would let the Trust Qualification Engine inspect images, mutate
inspection records, perform human review, present evidence, evaluate performance,
or take on any live/streaming behaviour is, by definition, out of bounds and
belongs to a later architecture, not to this engine.

---

## Closing Statement

This plan fixes the permanent engineering boundary of the Kalibra Trust
Qualification Engine. The engine reuses one raw inspection result — never the
image, never a reconstruction — calibrates its raw anomaly measure into honest
confidence, qualifies the decision as accept, reject, review, or abstain, grows
more cautious as inputs drift, and preserves both the raw result and its
qualification as evidence. It mutates nothing upstream, routes no one, presents no
surface, and evaluates nothing.

Engineered to this boundary, the Trust Qualification Engine is the act in which
Kalibra's thesis becomes concrete: every decision leaves the system carrying a
calibrated, defensible statement of how far it can be trusted — drawn from the
same source that made the decision in the first place.
