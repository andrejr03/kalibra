# Kalibra Architecture

## Architectural Vision

Kalibra is structured around a single architectural commitment: every inspection
decision and the judgement of whether that decision can be trusted are produced
together, by one system, from the same evidence.

The architecture therefore is not a defect detector with reliability features
attached. It is a system whose two responsibilities — deciding, and qualifying
that decision — are designed as one continuous flow. An input is examined, a
conclusion is drawn, the conclusion is calibrated and qualified, uncertain cases
are routed away from automation, and every step leaves an inspectable trace.

This document fixes the boundaries of that system. It defines what the
architecture contains, what it deliberately excludes, and the principles that any
future extension must respect. It describes structure, not construction: the
shape of the system, independent of how any part of it is built.

The guiding architectural sentence is this — Kalibra inspects, and in the same
motion decides whether its own inspection can be trusted.

## System Boundary

Kalibra is bounded as an **offline, batch, locally reproducible** system. It
operates on a fixed body of inputs, produces a fixed body of outputs, and can be
re-run to regenerate the same evidence from the same starting point.

Inside the boundary:

- examination of visual inputs for defects,
- calibration and qualification of each decision,
- separation of confident decisions from uncertain ones,
- routing of uncertain cases toward human judgement,
- demonstration that the system grows more cautious as inputs drift,
- and the production of inspectable, reproducible evidence for all of the above.

Outside the boundary:

- live, streaming, or continuously serving operation,
- hosting, serving interfaces, or remote operation,
- and any behaviour that cannot be reproduced from a fixed starting point.

The boundary is deliberately drawn so that the whole system can be reasoned about,
reproduced, and completed. Everything the architecture claims happens within it.

## Core System

The Core System is responsible for the first of Kalibra's two acts: examining an
input and reaching a defect judgement.

Architecturally it comprises three responsibilities:

- **Input intake.** Visual inputs enter the system through a single, well-defined
  entry point and are placed into a stable, reproducible form. The system reasons
  only about inputs that have passed through this intake.
- **Examination.** Each input is assessed for the presence of a defect. The
  examination yields both an overall judgement for the input and a localization of
  where, within the input, the suspected defect lies.
- **Scoring.** The examination produces a raw measure of how anomalous the input
  is. This raw measure is the substrate everything downstream builds upon; it is
  not yet a trustworthy confidence, and the architecture treats it as such.

The Core System answers only one question: *is this input defective, and where?*
It does not decide whether that answer can be trusted. That separation is
deliberate and is the seam along which the rest of the architecture is organised.

## Self-Evaluation Layer

The Self-Evaluation Layer is Kalibra's second act. It takes the raw judgement of
the Core System and decides how far that judgement can be relied upon. It shares
the same input and the same underlying examination — it is a second perspective on
one system, not a separate system.

It carries four responsibilities:

- **Calibration.** Raw scores are mapped into confidence that means what it says,
  so that a stated level of certainty corresponds to the real chance of being
  correct.
- **Qualification.** Each calibrated decision is sorted into an outcome that
  reflects how much it can be trusted — clearly acceptable, clearly rejectable, or
  uncertain.
- **Abstention.** When confidence is too low to act on, the layer declines to
  decide automatically. Abstention is treated as a valid outcome, not a failure of
  the system.
- **Drift awareness.** The layer observes how far an input has moved from familiar
  conditions and responds by becoming more cautious — deferring more, deciding
  less — as that distance grows.

The Self-Evaluation Layer is the architectural expression of Kalibra's thesis. Its
purpose is to ensure that no decision leaves the system without a defensible
statement of how much it can be trusted.

## Human Review Layer

The Human Review Layer is the destination for everything Kalibra declines to
decide alone. It is the architectural guarantee that uncertainty has somewhere to
go.

Its responsibilities are:

- **Routing.** Decisions qualified as uncertain, or arising from drifted inputs,
  are directed toward human judgement rather than forced into an automated answer.
- **Hand-off.** Each routed case is presented together with the evidence behind
  it — the input, the localization, the qualified outcome — so that a human can
  act on a complete picture rather than a bare verdict.
- **Boundary of authority.** The architecture fixes where the system's authority
  ends and human authority begins. Kalibra decides what it is confident about and
  defers what it is not; it does not override its own uncertainty.

This layer is what makes Kalibra a partner to human judgement rather than a
replacement for it. By design, the cases it cannot safely automate are exactly the
cases it surfaces for review.

## Evidence Layer

The Evidence Layer is the architectural backbone that makes every other layer
inspectable. Nothing important in Kalibra is taken on faith; the Evidence Layer is
how that principle is enforced structurally.

Its responsibilities are:

- **Recording.** Each decision, its localization, its calibrated confidence, its
  qualified outcome, and any routing or abstention are preserved as durable
  artifacts.
- **Reproducibility.** From a fixed starting point, the same evidence can be
  regenerated. The system's claims are not momentary outputs but standing,
  reconstructable records.
- **Presentation.** Evidence is surfaced through an inspectable surface that lets
  an observer see what the system concluded, where, and with what confidence —
  without having to trust the system's word.
- **Demonstration.** The evidence that supports Kalibra's central claims —
  calibration, the link between uncertainty and error, and growing caution under
  drift — is itself recorded and presentable, so that those claims can be examined
  rather than asserted.

The Evidence Layer turns trustworthiness from a property the system claims into a
property an observer can verify.

## Reliability Principles

The architecture is governed by reliability principles that any conforming design
must uphold:

1. **Trust is a first-class output.** No decision leaves the system without an
   accompanying, defensible statement of how far it can be relied upon.
2. **Decision and trust share one source.** The judgement and its qualification are
   produced from the same input and the same examination; they are never
   reconciled after the fact from separate systems.
3. **Confidence must be calibrated.** Stated certainty must correspond to observed
   correctness; an uncalibrated score is not permitted to stand in for confidence.
4. **Uncertainty must have a destination.** Whenever the system is unsure, the
   architecture provides a path away from automation and toward human judgement.
5. **Abstention is legitimate.** Declining to decide is a designed outcome with its
   own place in the flow, not an error state.
6. **Caution must respond to change.** The system's willingness to defer must
   increase observably as inputs drift from familiar conditions.
7. **Every claim is evidenced.** Each reliability property the system asserts is
   backed by a recorded, reproducible artifact.

These principles outrank convenience. Where a design choice conflicts with them,
the architecture requires the choice to change, not the principle.

## Scope Boundaries

The architecture is held within deliberate boundaries so that it remains coherent
and completable.

- **One of everything.** The architecture is defined around a single, focused
  inspection setting and a single instance of each responsibility, rather than
  many variants pursued in parallel. Breadth is an extension, not a starting
  condition.
- **Generated, not live.** Demonstrations of the system's behaviour under changing
  conditions are produced as controlled, reproducible experiments — never as live
  or continuously streaming operation.
- **Inspect, do not operate.** Kalibra is an inspection and self-evaluation
  system. It does not host, serve, deploy, or run continuously as part of its
  defined scope.
- **Decide with a human, not instead of one.** The architecture keeps human
  judgement in the loop precisely where confidence is low; it never designs that
  judgement out.

Each boundary is stated so that what lies inside the architecture can be pursued
thoroughly. A clearly drawn limit is part of the design, not a gap in it.

## Deferred Architecture

The following belong to a later architecture, not to this one. They are named
deliberately, as boundaries rather than omissions:

- multiple inspection settings or input categories pursued at once,
- continuous, streaming, or temporal monitoring of inputs over time,
- operational alerting, scheduling, or surrounding operational infrastructure,
- feedback loops that update the system from human decisions,
- hosting, serving, or deployment of the system as a running service,
- exhaustive comparison of competing examination methods,
- and any reliance on live, collected, or continuously changing inputs.

Naming these as deferred is itself an architectural act. It fixes the present
system's edge and records where future growth may occur, so that the boundary is a
decision rather than an accident. Anything on this list is, by definition, a
question for a later version of the architecture.

## Architectural Success Criteria

The architecture is sound when its structure makes Kalibra's central claims
demonstrable rather than asserted. Specifically, it succeeds when:

- decision and trust are produced as one flow from one source, with a clean,
  defined seam between examination and self-evaluation;
- every decision carries a calibrated, qualified statement of how far it can be
  trusted before it leaves the system;
- uncertain and drifted cases have a defined and unavoidable path to human
  judgement;
- the system's growing caution under changing conditions is expressible as
  reproducible evidence rather than as an assurance;
- every reliability claim is backed by a durable, inspectable, regenerable
  artifact;
- and the boundaries of the system — what it does, and what it explicitly defers —
  are stated plainly enough that the architecture can be reasoned about and
  completed as a whole.

Above all, the architecture succeeds when an observer who does not trust the system
can still verify, from its structure and its evidence, that the system knows when
not to trust itself.
