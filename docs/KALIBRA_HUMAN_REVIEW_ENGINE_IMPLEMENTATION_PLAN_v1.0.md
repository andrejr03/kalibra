# Kalibra Human Review Engine Implementation Plan

## About This Plan

This document is the implementation plan for the **Human Review Engine**,
Kalibra's destination for everything the system declines to decide alone. It
consumes the trust-qualified outcomes produced by the
[Trust Qualification Engine](KALIBRA_TRUST_QUALIFICATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)
and manages the human-review boundary.

It is an architecture-first plan: it fixes the permanent engineering boundary of
the Human Review Engine — what it owns, what it refuses, what crosses its seams,
and how it is validated — without choosing how any of it is built.

The plan deliberately does **not** select UI frameworks, storage frameworks,
model-training workflows, or evaluation metrics. Those belong to later phases and
to other domains. This document defines the boundary those later choices must
respect.

Throughout, **must** and **must not** express binding engineering obligations,
consistent with the language of
[`docs/KALIBRA_ENGINEERING_PLAN_v1.0.md`](KALIBRA_ENGINEERING_PLAN_v1.0.md) and
[`docs/KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md`](KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md).

---

## 1. Purpose

The Human Review Engine is the architectural guarantee that **uncertainty has
somewhere to go** (Architecture §Human Review Layer). It is the destination for
every case Kalibra declines to decide alone — the cases the Trust Qualification
Engine qualified as *review*, or flagged as drifted.

Its purpose is to keep human judgement in the loop precisely where confidence is
low: to accept deferred cases, present each one to a reviewer with the complete
evidence behind it, record the reviewer's decision as durable evidence, and hold
the boundary between the system's authority and human authority (Requirements
H1–H4).

The engine makes Kalibra a **partner to human judgement rather than a replacement
for it**. By design, the cases it cannot safely automate are exactly the cases it
surfaces for review — and the human decision it collects is recorded as evidence,
never silently folded back into model behaviour (AGENTS.md Scope Protection,
Exclusion X5).

---

## 2. Responsibilities

The Human Review Engine **must**:

- **Accept deferred cases.** Receive, across the defined upstream seam, the cases
  the Trust Qualification Engine qualified as *review* or as needing human
  judgement (including drifted cases), and treat their arrival as a normal,
  engineered outcome (Requirement H1).
- **Preserve the reason for deferral.** Carry forward, unchanged, why the case was
  deferred — the qualified outcome and the uncertainty or drift that warranted it —
  so the reviewer and the record both reflect the true basis for review.
- **Prepare the evidence hand-off.** Assemble, for each routed case, the complete
  evidence a reviewer needs to act — the source input, its localization, the raw
  inspection result, and the trust qualification — so the human acts on a complete
  picture rather than a bare verdict (Requirement H2).
- **Record the reviewer decision.** Capture the human's judgement for each routed
  case as a durable artifact.
- **Preserve the full upstream chain.** Maintain the link binding the reviewer
  action to its trust qualification, its raw inspection result, and its source
  input, so every review decision remains traceable end to end.
- **Hold the boundary of authority.** Ensure the system decides only what it is
  confident about and defers what it is not, and never overrides its own expressed
  uncertainty (Requirement H3).
- **Treat review as an outcome, not a failure.** Handle deferral as a designed
  destination, not an error state.
- **Emit review records as evidence.** Emit a durable record of each routing and
  each reviewer decision into the Evidence Engine, so human decisions are recorded
  as evidence and not silently folded back into model behaviour (Requirement E1,
  Exclusion X5).

These responsibilities are the complete remit of the engine. Anything not listed
here is, by design, not its job.

---

## 3. Explicit Non-Responsibilities

The Human Review Engine **must not** take on any of the following. Each belongs to
a named domain or to a deferred architecture, and the boundary is load-bearing:

- **Inspect images directly.** It must not examine the visual input. Examination
  happened two domains upstream. *(Inspection Engine.)*
- **Reconstruct inspection results.** It must not re-derive any judgement,
  localization, or anomaly measure; it presents what it received.
- **Calibrate confidence.** It must not produce or alter calibrated confidence.
  *(Trust Qualification Engine.)*
- **Modify trust qualification records.** It must not mutate, overwrite, or correct
  any qualified outcome it receives. The qualification is immutable to it.
- **Modify raw inspection records.** It must not mutate the raw inspection result.
  It is immutable to it.
- **Perform model training.** It must not train any model.
- **Update the inspection system from reviewer decisions.** It must not retrain,
  recalibrate, or otherwise update the model from human decisions; no feedback
  loop exists (Exclusion X5, AGENTS.md Scope Protection).
- **Evaluate performance.** It must not measure review quality or any other
  dimension; it records reviews, it does not judge them. *(Evaluation Engine.)*
- **Own the Evidence presentation layer.** It emits records and assembles the
  hand-off; it does not own, curate, or present the inspectable evidence surface.
  *(Evidence Engine.)*

The engine must also remain within Kalibra's constraints: offline, batch, and
reproducible, with no live, streaming, hosted, or continuously operating behaviour
and no operational alerting or scheduling (Constraints C1, C2; Exclusions X1–X4).

---

## 4. Inputs

The Human Review Engine accepts a single kind of input:

- **A review-qualified case.** A trust qualification result whose qualified
  outcome is *review*, or which arises from a drifted input warranting human
  judgement, together with the upstream chain it carries: the trust qualification
  result, the raw inspection result it qualifies, and the reference to the source
  input. (See Trust Qualification Engine plan §5 and §8, Contract C.)

Properties the input **must** satisfy:

- It is a genuine qualified outcome handed across the defined seam — review is a
  **qualified outcome from the Trust Qualification Engine, not an Inspection
  Engine failure** (core boundary). The engine never receives raw images or
  unqualified cases.
- It carries, intact, the reason for deferral (the qualified outcome and the
  uncertainty or drift basis) so the engine can preserve it.
- It carries references that let the full chain — source input → raw inspection
  result → trust qualification → review case — be reconstructed for hand-off and
  recording (Requirement H2, E1).

What the engine **must not** require or assume:

- Any access to the raw image or to intake; it reasons about the qualified case
  and the references it carries, not the picture.
- Any label, ground-truth, or downstream evaluation of the case.
- Any live or streaming source; cases are drawn from a fixed body (C1, C4, X8).

It also accepts, from the reviewer, the **reviewer decision** for a routed case —
the human judgement to be recorded. The concrete form of that decision, and the
surface through which a reviewer supplies it, are left to implementation; this
plan fixes only that the decision is captured and recorded as evidence.

---

## 5. Outputs

For each routed case, the engine produces and emits:

- **A review case (the prepared hand-off).** The assembled evidence a reviewer
  needs — source input reference, localization, raw inspection result, and trust
  qualification — together with the preserved reason for deferral. This is what is
  presented for human judgement (H2).
- **A recorded reviewer decision.** The human's judgement for the case, captured as
  a durable artifact and bound to the review case.
- **A preserved upstream-chain link.** The binding from the reviewer action through
  trust qualification, raw inspection result, and source input, so the decision is
  traceable end to end.
- **A review evidence record.** A durable record of the routing and the reviewer
  decision emitted into the Evidence Engine (E1).

Properties the plan fixes:

- The output is **additive, never destructive.** The review case and reviewer
  decision accompany the upstream artifacts; they do not replace or mutate the raw
  inspection result or the trust qualification (core boundary).
- **Reviewer decisions are evidence, not feedback.** A reviewer decision is
  recorded as durable evidence and is **not** routed back to retrain, recalibrate,
  or update any model (Exclusion X5, core boundary).
- **Review is an engineered outcome.** A routed case and its recorded decision are
  first-class results, not error states.
- The output is **emitted as evidence** and is **regenerable** from the same fixed
  inputs and the same recorded reviewer decision (E1, P2, C2).

The engine prepares and records the human decision; it does not own how that
evidence is later presented — that is the Evidence Engine's responsibility.

---

## 6. Domain Boundaries

The Human Review Engine sits third in Kalibra's directed flow and touches two
other domains directly.

**Upstream seam — Trust Qualification → Human Review.**
The engine receives review-qualified and drifted cases across the defined, stable
seam. It treats the trust qualification result and the raw inspection result it
carries as **immutable**; it must not revise the judgements it receives — its
responsibility is to route and present them, not to revise them (Engineering Plan
§Human Review Engine). Review arrives as a *qualified outcome*, never as an
Inspection Engine failure (core boundary).

**Lateral seam — Human Review → Evidence.**
The engine **records** the routing and reviewer decision into the Evidence Engine
(Engineering Plan §Human Review Engine). It emits into the evidence backbone; it
does not own or present that surface.

**Runtime independence from the Evidence Engine.** The engine prepares the review
hand-off from the **Review-Qualified Case it receives** across the upstream seam —
which already carries the full upstream chain (source-input reference, raw
inspection result, localization reference, trust qualification, and the reason for
review). It must **not** depend on the Evidence Engine for its runtime operation,
and nothing in this engine requires the Evidence Engine to exist in order to
assemble or record a hand-off. This keeps the engine consistent with the fixed
implementation sequence, in which Human Review (third) is built before the
Evidence Engine (fourth). The Evidence Engine remains the canonical preservation
layer: where the Engineering Plan describes Human Review *drawing* supporting
material from Evidence, that is a property of the later, integrated system once the
Evidence Engine exists — a read of already-recorded material — not a runtime
dependency of this engine, which carries everything it needs in the case itself.

Boundaries the engine must hold:

- It must not be bypassed: uncertain and drifted cases have a defined, unavoidable
  path to human judgement, and that path is this engine (AGENTS.md Architectural
  Rules; A5).
- It must not alter the judgements it receives, nor mutate raw inspection or trust
  qualification records (core boundary).
- It must not close a feedback loop into the model; reviewer decisions terminate as
  evidence (Exclusion X5).
- It must not take on Inspection, Trust Qualification, Evidence-presentation, or
  Evaluation responsibilities; responsibilities must not bleed across the seam for
  convenience (Engineering Plan §Engineering Principles).
- It must hold the boundary of authority: the system defers what it is unsure about
  and never overrides its own expressed uncertainty (H3).

---

## 7. Internal Processing Stages

The engine's internal work is described here as **responsibility stages**, not as
an algorithm. The stages fix *what must happen in order*, not *how* any stage is
implemented. No UI, storage, or training mechanism is chosen here.

1. **Case intake.** Receive a review-qualified case across the upstream seam and
   confirm it is a genuine qualified outcome (review or drifted) carrying its full
   upstream chain. Reject — as a failure mode (§9), not as a reviewer decision —
   anything that is not a qualified case or that arrives without its chain.

2. **Deferral-reason preservation.** Capture, unchanged, why the case was deferred
   — the qualified outcome and the uncertainty or drift basis — so the true reason
   travels with the case.

3. **Evidence hand-off preparation.** Assemble the complete evidence for the
   reviewer: the source input reference, the localization, the raw inspection
   result, and the trust qualification — **from the Review-Qualified Case the
   engine received**, which already carries this full chain. The assembly reads the
   upstream artifacts carried in the case; it must not modify them, and it must not
   depend on the Evidence Engine to perform this assembly.

4. **Reviewer decision capture.** Receive the human's judgement for the case and
   capture it as a durable artifact bound to the review case. The engine collects
   the decision; it does not adjudicate it.

5. **Chain binding.** Bind the reviewer action to its trust qualification, its raw
   inspection result, and its source input, so the decision is traceable end to
   end.

6. **Review record assembly.** Assemble the review case, the preserved deferral
   reason, the recorded reviewer decision, and the upstream-chain binding into one
   review record. Upstream artifacts are carried alongside, unmodified.

7. **Evidence emission.** Emit a durable review record into the Evidence Engine,
   preserving the full chain and the recorded reviewer decision.

Ordering and boundary obligations:

- The reviewer decision (stage 4) must never mutate the raw inspection result or
  the trust qualification; it is recorded alongside them (core boundary).
- No stage may inspect the image, reconstruct or recalibrate any upstream result,
  train or update a model, or evaluate review quality. If a stage appears to need
  any of these, the need belongs to a different domain and the seam, not this
  engine.
- All stages operate offline and in batch over a fixed body of cases; no stage
  introduces live, streaming, or continuously operating behaviour (C1, X1).
- Every stage must be deterministic with respect to fixed inputs and a fixed,
  recorded reviewer decision, so the record is regenerable (C2, P2).

---

## 8. Data Contracts

This section fixes the **shape and obligations** of what the engine consumes and
produces, expressed as abstract contracts. Concrete types, encodings, field
names, surfaces, and storage formats are deliberately left to implementation; only
the obligations below are binding.

**Contract A — Review-Qualified Case (consumed).**
- Carries the trust qualification result (with its *review*/drifted qualified
  outcome), the raw inspection result it qualifies, and the source-input reference
  — the full upstream chain.
- Carries the reason for deferral (qualified outcome plus uncertainty or drift
  basis).
- Is treated as **immutable**: the engine reads it and must not mutate, overwrite,
  or correct any field of the trust qualification or raw inspection result.

**Contract B — Reviewer Decision (consumed).**
- Carries the human judgement for one routed case.
- Is bound to exactly one review case.
- Is recorded as evidence; it must not be transformed into a model update,
  retraining signal, or recalibration input (Exclusion X5).

**Contract C — Review Case / Hand-off (produced).**
- Carries the assembled evidence for the reviewer: source-input reference,
  localization, raw inspection result, and trust qualification.
- Carries the preserved deferral reason.
- Must not contain a mutated copy of any upstream artifact; it references and
  presents them, never replaces them.

**Contract D — Review Evidence Record (emitted).**
- Durably preserves the review case, the preserved deferral reason, the recorded
  reviewer decision, and the upstream-chain binding (E1).
- Preserves the **full chain**: source input → raw inspection result → trust
  qualification → review case → reviewer decision (core boundary).
- Is regenerable from the same fixed inputs and the same recorded reviewer
  decision (P2).
- Faithfully represents the recorded decision and the upstream artifacts; it must
  not present a result as stronger than its evidence allows (E2, R7).

Contract invariants:

- **Non-destruction.** Raw inspection and trust qualification results remain intact
  and recoverable alongside the review record (core boundary).
- **No feedback loop.** A reviewer decision terminates as recorded evidence and is
  never fed back to update the model (Exclusion X5).
- **Full-chain traceability.** Every produced and emitted artifact ties back
  through trust qualification, raw inspection result, and source input.
- **Review as outcome.** A routed case is a normal qualified destination, never an
  error artifact.

---

## 9. Failure Modes

The engine must distinguish **review outcomes** (a routed case and its recorded
decision — all normal) from **engine failures** (the engine cannot accept, prepare,
record, or emit a valid review). A failure is never silently converted into a
reviewer decision, and a routed case is never treated as a failure.

Identified failure modes and required handling:

- **Non-review case received.** A case arrives that is not qualified as *review*
  or drifted. The engine must refuse it; it must not invent a review for a case
  the upstream domain did not defer (core boundary — review is a qualified
  outcome, not anything this engine manufactures).
- **Incomplete upstream chain.** A case arrives missing its trust qualification,
  raw inspection result, or source-input reference. The engine must refuse,
  because a hand-off and record without the full chain would violate H2 and
  full-chain traceability (§8).
- **Mutation attempt.** Any internal path that would alter the raw inspection
  result or the trust qualification is a defect to be prevented; both must remain
  immutable (core boundary).
- **Missing or malformed reviewer decision.** No decision, or an uninterpretable
  one, is supplied for a routed case. The engine must surface this as an
  unresolved review, not fabricate or assume a decision.
- **Attempted feedback into the model.** Any path that would route a reviewer
  decision into retraining, recalibration, or model update is a boundary violation
  to be prevented (Exclusion X5).
- **Evidence emission failure.** The review record was assembled but could not be
  preserved with its full chain. Because evidence is an obligation of normal
  operation (E1), the engine must surface this rather than report a recorded review
  without a durable record.
- **Non-reproducibility.** Re-running on the same fixed case and the same recorded
  reviewer decision yields a different review record, indicating hidden state. This
  violates C2/P2 and must be surfaced as a defect, not tolerated.
- **Introduction of live operation.** Any path that would make review live,
  streaming, or continuously operating is out of bounds and must be prevented
  (C1, X1).

General obligations for all failure modes:

- Failures must be **explicit and inspectable**, never swallowed.
- A failure must never be **disguised as a routed case or a recorded decision**;
  review is a designed outcome, not a failure channel, and vice versa.
- Failure handling must not import other domains' responsibilities (it must not,
  for example, recalibrate or re-inspect — it only surfaces the failure).

This plan fixes *which* failures must be handled and *how they must be treated*;
the concrete error mechanisms are implementation choices.

---

## 10. Validation Strategy

Validation here means confirming the engine honours its boundary and contracts —
**not** measuring review quality, which is the Evaluation Engine's job and out of
scope for this plan. No evaluation metrics are defined.

The engine must be validated against:

- **Review-as-outcome.** Every accepted case is a genuine *review*/drifted
  qualified outcome from the Trust Qualification Engine, never a manufactured or
  Inspection-failure case (core boundary).
- **Consumes qualified cases, not images.** The engine has no image access and
  performs no inspection or reconstruction (core boundary).
- **Deferral reason preserved.** The reason a case was deferred is carried forward
  unchanged into hand-off and record.
- **Complete hand-off.** Every prepared review case presents source input,
  localization, raw inspection result, and trust qualification (H2).
- **Non-destruction.** Raw inspection and trust qualification results are unchanged
  after review, and both are preserved in the emitted record (core boundary, E1).
- **No model feedback.** No reviewer decision is routed into retraining,
  recalibration, or model update; decisions terminate as evidence (Exclusion X5,
  core boundary).
- **Full-chain traceability.** Each review record ties back through trust
  qualification, raw inspection result, and source input (H2, E1).
- **Boundary conformance.** The engine performs no inspection, no calibration, no
  training, no evaluation, and does not own evidence presentation. The absence of
  these responsibilities is validated, not assumed.
- **Offline / batch / reproducible.** The engine introduces no live operation, and
  the same fixed case plus recorded decision yields the same review record on
  re-run (C1, C2, P2, X1).
- **Failure handling.** Each failure mode in §9 is surfaced explicitly and never
  disguised as a routed case or recorded decision.

Validation must rest on **inspectable evidence** (the emitted records), so an
observer can verify conformance without trusting the engine's word, consistent
with Kalibra's evidence-before-assertion philosophy.

---

## 11. Testing Strategy

Testing fixes *what must be demonstrated* about the engine; it does not fix a UI
framework, storage framework, harness, or tooling, and it does not test review
quality.

The engine's test suite must demonstrate, at minimum:

- **Acceptance tests.** A genuine *review*/drifted qualified case is accepted and
  handled as a normal outcome; a non-review case is refused (review is not
  manufactured here).
- **Chain-preservation tests.** The full chain — source input → raw inspection
  result → trust qualification → review case → reviewer decision — is preserved in
  the emitted record; a case missing any chain link is refused.
- **Hand-off tests.** Every prepared review case presents source input,
  localization, raw inspection result, and trust qualification (H2).
- **Deferral-reason tests.** The reason for deferral is carried forward unchanged.
- **Non-destruction tests.** After review, the raw inspection result and the trust
  qualification are byte-for-byte unchanged, and both appear in the emitted record.
- **No-feedback tests.** No path routes a reviewer decision into retraining,
  recalibration, or model update; this is asserted as *must-not-exist* (Exclusion
  X5).
- **Decision-recording tests.** A supplied reviewer decision is captured and bound
  to its review case; a missing or malformed decision is surfaced as unresolved,
  not fabricated.
- **Boundary tests (negative).** The engine exposes no inspection, no calibration,
  no training, no evaluation, and no evidence-presentation behaviour; these are
  asserted as *must-not-exist*, guarding the seams.
- **Offline / reproducibility tests.** The engine introduces no live operation, and
  re-running on an identical fixed case and recorded decision yields an identical
  review record.
- **Failure-mode tests.** Each failure mode in §9 (non-review case, incomplete
  chain, mutation attempt, missing/malformed decision, attempted model feedback,
  evidence-emission failure, non-reproducibility, attempted live operation) is
  provoked and shown to be surfaced explicitly and not disguised.

Testing principles:

- Tests assert the engine's **boundary and contracts**, not review quality. No test
  in this domain may smuggle in a review-quality or any evaluation metric.
- Tests must use **fixed inputs and fixed recorded decisions** so they are
  themselves reproducible (C2).
- Tests should be small and focused, each covering one obligation, consistent with
  Kalibra's coding rules (small, testable modules).

The concrete test code, fixtures, and runner are produced during implementation,
not in this plan.

---

## 12. Future Extension Points

These are points where later phases and other domains attach to the Human Review
Engine. Naming them fixes the boundary now; none grants licence to absorb another
domain's responsibility or to open a deferred capability.

- **The reviewer surface is replaceable.** Because this plan fixes the engine's
  contracts and seams but not the surface through which a reviewer reads a case and
  supplies a decision, that surface can be implemented and later replaced without
  changing the engine's boundary, provided Contracts B and C continue to hold.
- **Evidence presentation builds on emitted records.** The Evidence Engine's
  inspectable surface is built over the review records this engine emits (Contract
  D). Faithful emission and complete hand-off are the obligations; presentation is
  the extension and belongs to the Evidence Engine.
- **Evaluation consumes recorded reviews.** The Evaluation Engine later measures
  review quality and deferral appropriateness from the emitted records — never from
  inside this engine, and never by adding evaluation logic here.
- **Reviewer-decision feedback remains deferred.** Feedback loops that update the
  system from human decisions are explicitly deferred (Exclusion X5). Should a
  later architecture introduce them, that is a new boundary set by the repository
  owner — this engine records decisions as evidence and stops there.
- **Richer deferral reasons can be carried.** Additional deferral-reason detail
  from the Trust Qualification Engine can be carried through without changing the
  engine's responsibility, provided it is preserved unchanged and recorded.

Deferred scope remains deferred (Engineering Plan §Engineering Boundaries; AGENTS.md
Scope Protection). An extension that would let the Human Review Engine inspect
images, recalibrate, mutate upstream records, train or update the model, evaluate
performance, present evidence, or operate live is, by definition, out of bounds and
belongs to a later architecture, not to this engine.

---

## Closing Statement

This plan fixes the permanent engineering boundary of the Kalibra Human Review
Engine. The engine accepts the cases Kalibra declines to decide alone — qualified
for review, not failed in inspection — preserves why each was deferred, hands the
reviewer the complete evidence chain, records the human decision as durable
evidence, and binds that decision back through trust qualification, raw inspection
result, and source input. It mutates nothing upstream, trains nothing, updates no
model from what reviewers decide, evaluates nothing, and presents no surface of its
own.

Engineered to this boundary, the Human Review Engine is what makes Kalibra a
partner to human judgement rather than a replacement for it: uncertainty always has
somewhere to go, the human always sees the whole picture, and the decision they
make is preserved as evidence the system can stand behind.
