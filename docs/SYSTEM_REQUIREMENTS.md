# Kalibra System Requirements

## Purpose

This document states the requirements that any implementation of Kalibra must
satisfy. It translates the system's guiding principles into normative, system-level
obligations: what Kalibra must do, what it must guarantee, and what it must never do.

The requirements are deliberately implementation-agnostic. They describe the
capabilities and properties a conforming system must exhibit, not how those
capabilities are achieved. Any implementation — present or future, however built — is
considered correct only insofar as it satisfies these requirements. Where an
implementation cannot meet a requirement, the corresponding claim must not be made.

Throughout this document, **must** and **must not** express binding obligations.
Each requirement reads as a condition a conforming Kalibra is required to meet.

## Functional Requirements

A conforming Kalibra must provide the following capabilities.

- **F1 — Input intake.** The system must accept visual inputs through a single,
  well-defined entry point and bring them into a stable, reproducible form before
  any judgement is made.
- **F2 — Defect detection.** For each input, the system must produce a judgement of
  whether the input is defective.
- **F3 — Defect localization.** For each input judged defective, the system must
  indicate where, within the input, the suspected defect lies.
- **F4 — Decision qualification.** For each judgement, the system must produce a
  statement of how far that judgement can be trusted, expressed as calibrated
  confidence.
- **F5 — Outcome routing.** The system must sort each qualified decision into an
  outcome that reflects its trustworthiness — clearly acceptable, clearly rejectable,
  or uncertain.
- **F6 — Abstention.** The system must be able to decline to decide automatically
  when confidence is insufficient, treating abstention as a valid outcome.
- **F7 — Drift response.** The system must adjust its caution in response to how far
  an input has moved from familiar conditions, deferring more as that distance grows.

These capabilities define the minimum behaviour of Kalibra. An implementation that
omits any of them is not Kalibra, regardless of its other merits.

## Reliability Requirements

A conforming Kalibra must uphold the following reliability properties, each of which
must be demonstrable rather than merely intended.

- **R1 — Trust as output.** Every decision the system emits must carry an
  accompanying, defensible statement of how far it can be relied upon. No decision
  may leave the system unqualified.
- **R2 — Single source.** A decision and its trust qualification must derive from the
  same input and the same examination; the two must not be produced by separate,
  independently reconciled processes.
- **R3 — Calibrated confidence.** Stated confidence must correspond to observed
  correctness. The system must not present uncalibrated scores as confidence.
- **R4 — Informative uncertainty.** The cases the system reports as uncertain must be
  demonstrably more error-prone than the cases it reports as confident.
- **R5 — Appropriate deferral.** The cases the system declines or routes away from
  automation must be demonstrably the cases that warranted deferral.
- **R6 — Responsive caution.** The system's willingness to defer must increase
  measurably as inputs drift from familiar conditions.
- **R7 — Honest claims.** The system must not assert any reliability property it
  cannot demonstrate. Where evidence is weak or absent, the corresponding claim must
  be narrowed or withdrawn.

These requirements are the expression of Kalibra's thesis. Where a design choice
conflicts with them, the design must change, not the requirement.

## Human Review Requirements

A conforming Kalibra must keep human judgement in the loop where confidence is low.

- **H1 — Defined destination.** The system must provide a defined path by which
  uncertain and drifted cases are directed toward human judgement rather than forced
  into an automated answer.
- **H2 — Complete hand-off.** Each case directed to human judgement must be
  presented together with the evidence behind it — the input, its localization, and
  its qualified outcome — so that a human can act on a complete picture.
- **H3 — Bounded authority.** The system must decide only what it is confident about
  and defer what it is not. It must not override its own expressed uncertainty.
- **H4 — Correct deferral.** The set of cases the system routes for review must be
  demonstrably weighted toward the difficult, ambiguous, and error-prone cases.

These requirements ensure Kalibra functions as a partner to human judgement and
never silently substitutes for it.

## Evidence Requirements

A conforming Kalibra must make its claims verifiable through recorded evidence.

- **E1 — Recorded decisions.** Each decision, its localization, its calibrated
  confidence, its qualified outcome, and any routing or abstention must be preserved
  as durable artifacts.
- **E2 — Inspectable surface.** The system must present its evidence through a surface
  that lets an observer see what was concluded, where, and with what confidence,
  without having to trust the system's word.
- **E3 — Claim-bound evidence.** Each reliability claim must travel with the evidence
  that supports it, so that an assertion and its justification are never separated.
- **E4 — Comparative evidence.** Where a step is intended to improve a property, the
  system must retain evidence of the state before and after, so the improvement is
  demonstrated rather than asserted.
- **E5 — Disclosed limitations.** Where evidence is weak, incomplete, or absent, the
  system must record that plainly alongside the affected claims.

The burden of proof rests on the system. An observer must never be required to take
Kalibra's reliability on faith.

## Reproducibility Requirements

A conforming Kalibra must produce results that can be regenerated and audited.

- **P1 — Fixed starting point.** All inputs to a given result must be fixable into a
  stable form, so that the result derives from a known, unchanging starting point.
- **P2 — Regenerable results.** From that fixed starting point, the system must be
  able to regenerate the same evidence, so that results are standing records rather
  than momentary outputs.
- **P3 — Preserved separation.** The separation between what the system learns from
  and what it is evaluated on must be preserved, so that results reflect genuine
  capability and not memorised answers.
- **P4 — Documented provenance.** The origin, terms, and known limitations of the data
  behind a result must be recorded so the result can be interpreted and audited.
- **P5 — Stable reference.** The reference against which the system is measured must be
  fixed for a given evaluation, so that results remain comparable.

Reproducibility is a baseline obligation, not an optional quality. A result that
cannot be regenerated is treated as unproven.

## System Constraints

A conforming Kalibra operates within the following constraints.

- **C1 — Offline and batch.** The system must operate on a fixed body of inputs and
  produce a fixed body of outputs; it is not required and not intended to serve
  continuously.
- **C2 — Reproducible by construction.** The system must be re-runnable from a fixed
  starting point to regenerate its results.
- **C3 — Focused scope.** The system must be defined around a single, well-defined
  inspection setting and a single instance of each responsibility, rather than many
  variants in parallel.
- **C4 — Controlled variation.** Demonstrations of behaviour under changing conditions
  must be produced as controlled, reproducible variation, not gathered from live or
  streaming change.
- **C5 — Human-in-the-loop.** The system must retain human judgement where confidence
  is low and must not design that judgement out.

These constraints keep Kalibra coherent, reproducible, and completable. They bound
what a conforming system may attempt.

## Explicit Exclusions

The following are outside the requirements of a conforming Kalibra. They are stated
as deliberate exclusions, not omissions.

- **X1** — Continuous, streaming, or live serving operation.
- **X2** — Hosting, deployment, or operation as a running service.
- **X3** — Monitoring of inputs over time as a live operational activity.
- **X4** — Operational alerting, scheduling, or surrounding operational infrastructure.
- **X5** — Feedback loops that update the system from human decisions.
- **X6** — Multiple inspection settings or input categories pursued at once.
- **X7** — Exhaustive comparison of competing detection approaches.
- **X8** — Reliance on live, collected, or continuously changing inputs.

An implementation is not required to provide any excluded capability, and providing
one does not make an implementation more conforming. Each exclusion belongs to a
later, broader system, not to this one.

## Acceptance Requirements

An implementation is accepted as a conforming Kalibra only when all of the following
hold and are supported by reproducible, inspectable evidence.

- **A1** — Every functional capability (F1–F7) is provided.
- **A2** — Every decision carries a calibrated, qualified statement of trust before it
  leaves the system (R1–R3).
- **A3** — Uncertainty is shown to be informative and deferral is shown to be
  appropriate (R4, R5, H4).
- **A4** — Caution is shown to increase measurably as inputs drift (R6).
- **A5** — Uncertain and drifted cases have a defined, unavoidable path to human
  judgement with complete hand-off (H1–H3).
- **A6** — Every reliability claim is backed by durable, inspectable, regenerable
  evidence, with limitations disclosed (E1–E5, P1–P5).
- **A7** — No claim exceeds the evidence supporting it (R7).
- **A8** — The system honours its constraints and exclusions (C1–C5, X1–X8).

Where any acceptance requirement is only partly met, the corresponding claim must be
narrowed to match. Full acceptance requires full, demonstrated satisfaction.

## Closing Statement

These requirements define what it means to be Kalibra, independent of how Kalibra is
built. They translate the system's principles into obligations that any
implementation must meet: to inspect competently, to qualify every decision, to defer
where it is unsure, to grow cautious as conditions change, and to prove every one of
these with evidence an observer can verify.

An implementation is measured against this document, not against its own ambitions.
Whatever techniques a future Kalibra employs, it remains Kalibra only so long as it
satisfies these requirements — and claims no more than it can demonstrate.
