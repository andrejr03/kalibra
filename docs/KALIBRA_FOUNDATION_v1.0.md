# Kalibra

## Project Definition

Kalibra is a visual inspection system that detects defects and, for every
prediction it makes, decides whether that prediction can be trusted. Its first
and primary application is industrial quality control — detecting defects in
manufactured parts — but it is conceived for high-consequence visual inspection
more broadly.

It is not only a defect detector. It is a detector that holds itself to account:
it calibrates its own confidence, separates the cases it can decide from the
cases it cannot, hands the uncertain ones to a human, and demonstrates that it
becomes more cautious as the world it is shown drifts away from the world it
knows.

Kalibra exists to answer two questions at once — *is this part defective?* and
*can you trust me when I say so?*

## Vision

Most automated systems fail silently. They do not crash or stop; they keep
answering with the same confidence while quietly becoming wrong. In inspection,
that silence is expensive: a defect waved through, or a good part wrongly
rejected, by a model that never signalled any doubt.

Kalibra is built on a different premise — that a system's awareness of its own
limits is as important as its accuracy. The goal is a kind of machine judgement
that is honest about uncertainty, explicit about when it should defer, and
measurably more careful when conditions degrade — wherever visual inspection
carries real consequences, beginning with industrial quality control.

The long-term vision is simple to state and hard to earn: an inspection system
that knows how much to trust itself, and can prove it.

## The Problem

Visual quality inspection is one of the most common and most consequential tasks
in demanding environments — manufacturing first among them. Defects are rare,
varied, and often subtle. A useful inspector must find them reliably — but
reliability alone is not enough.

The deeper problem is trust under uncertainty:

- A confident wrong answer is worse than an admitted unknown, yet most systems
  cannot tell the two apart.
- Confidence scores are routinely uncalibrated: a reported 90% certainty may be
  right far less than 90% of the time.
- Inputs in the real world drift — lighting changes, sensors age, processes
  shift — and a model trained on yesterday's conditions rarely notices that today
  no longer resembles them.
- When a system cannot be sure, there is often no principled path to route the
  decision to a human who can.

The result is automation that looks dependable until the moment it is not.
Kalibra treats that gap — between apparent confidence and actual reliability — as
the problem worth solving.

## Core Idea

Kalibra is organised around a single idea: an inspection decision and a trust
decision are inseparable, and both must be produced together.

For each part, the system does two things. First, it judges whether the part is
defective and shows where the suspected defect lies. Second, it judges whether
that first judgement is reliable enough to act on — calibrating its confidence,
sorting the outcome into *accept*, *review*, or *reject*, and abstaining when it
should not decide alone.

This second act is not an afterthought bolted onto the first. It uses the same
evidence and the same model. The inspector and the self-evaluator are one system
seen from two angles: what it concludes, and how far that conclusion can be
trusted.

The thesis Kalibra sets out to demonstrate is that this self-knowledge can be
made concrete — observed, measured, and shown to hold even as conditions change.

## Engineering Philosophy

Kalibra is built from a small set of engineering convictions.

- **Honesty over polish.** A claim is only as good as the evidence behind it. If
  a capability cannot be demonstrated, it is softened or removed — never asserted.
- **Depth over breadth.** One problem solved completely is worth more than many
  solved partially. Kalibra would rather do a single thing rigorously than many
  things superficially.
- **Reproducibility as a baseline, not a feature.** Results must be regenerable
  from frozen inputs. Anyone should be able to see the same evidence the system
  reports.
- **Evidence before assertion.** Every headline claim is backed by an artifact
  that can be inspected. Nothing important is taken on faith.
- **Boundaries stated, not hidden.** What the system does not do is named
  deliberately. A clearly drawn limit is a sign of understanding, not a gap.
- **Finish what is started.** A complete, modest system is more valuable than an
  ambitious, abandoned one. Scope is defended so that the work can be finished.

These convictions favour systems that are smaller, clearer, and more trustworthy
than they are impressive — and earn their impressiveness from that trust.

## Design Principles

The following principles govern how Kalibra is designed and how future work on
it should be judged.

1. **Trust is a first-class output.** Every prediction is accompanied by a
   defensible statement of how much it can be relied upon.
2. **Calibration is mandatory.** Confidence must mean what it says; a stated
   certainty should match the observed rate of being correct.
3. **Uncertainty has somewhere to go.** When the system is unsure, the decision
   is routed — to review or to a human — rather than forced.
4. **Abstention is a valid answer.** Declining to decide a hard case is a correct
   behaviour, not a failure.
5. **Drift must be observable.** The system's caution should visibly increase as
   inputs move away from familiar conditions, and that response should be
   demonstrable.
6. **Decisions are inspectable.** A reviewer should be able to see what the system
   concluded, where, and why, without trusting it blindly.
7. **One of everything before two of anything.** Simplicity is protected; new
   breadth is added only after the core is complete and proven.

## Trust & Reliability Philosophy

Reliability, in Kalibra, is not accuracy by another name. A system can be
accurate on average and still be untrustworthy where it matters — overconfident
on the cases it gets wrong, oblivious to changing conditions, silent when it
should hesitate.

Kalibra treats trust as something that must be earned through demonstration, not
declared. The standard it holds itself to has three parts:

- **Confidence must be calibrated** — a reported level of certainty should
  correspond to the real chance of being right.
- **Uncertainty must correlate with error** — the cases the system flags as
  doubtful should be the cases where it is, in fact, more often wrong.
- **Caution must respond to change** — as inputs degrade, the system should defer
  more and decide less, visibly and measurably.

When these three hold, the statement "this system knows when not to trust itself"
is not a slogan but an observation. When any of them fails, the claim is withdrawn
and the system is described honestly for what it is. Reliability is a property to
be evidenced on every prediction, not a reputation to be assumed.

## Project Scope

Kalibra is an engineering artifact with a deliberately bounded purpose: to inspect
for visual defects and to qualify the trustworthiness of each inspection. Its
primary setting is industrial quality control — inspecting manufactured parts —
chosen as the first and motivating case for a system intended to serve
high-consequence visual inspection more generally.

Within that purpose, Kalibra is concerned with:

- detecting and locating visual defects in a focused, well-defined inspection
  setting;
- calibrating the confidence attached to each decision;
- routing outcomes into accept, review, and reject, with the ability to abstain;
- demonstrating, through controlled experiments, that the system grows more
  cautious as inputs drift;
- presenting all of this as inspectable, reproducible evidence that a reviewer can
  examine and verify.

The scope is intentionally narrow so that it can be pursued to completion. Kalibra
chooses to be a finished, trustworthy system over an unfinished, expansive one.

## Explicit Non-Goals

Stating what Kalibra is not is part of its design. The following are deliberate
boundaries, not omissions:

- Kalibra is **not a production platform**. It does not aim to be deployed,
  hosted, or operated as a live service.
- Kalibra is **not a real-time monitoring system**. It demonstrates its response
  to changing conditions as controlled experiment, not as continuous operation.
- Kalibra is **not a general-purpose inspector**. It does not attempt to cover
  every product, defect type, or setting at once.
- Kalibra is **not a benchmark of methods**. It is not an exhaustive comparison of
  competing techniques.
- Kalibra is **not an autonomous decision-maker**. It is designed to keep a human
  in the loop precisely where confidence is low.

These limits exist so that the things Kalibra does claim can be done thoroughly,
honestly, and to completion.

## Success Criteria

Kalibra succeeds if it can stand behind its central claim with evidence rather
than assertion. Concretely, it is successful when:

- its confidence is calibrated, so that stated certainty matches observed
  correctness;
- the cases it routes to review or abstention are demonstrably the ones where it
  is most likely to be wrong;
- its caution increases measurably as inputs drift away from familiar conditions;
- every one of these properties can be reproduced and inspected by someone who
  does not take the system's word for it;
- its boundaries are stated plainly, so that what it does not do is as clear as
  what it does;
- and the whole of it is finished — complete, coherent, and honest about its own
  limits.

Accuracy is necessary but not sufficient. Kalibra is successful only when its
self-knowledge is real and its trustworthiness is shown.

## Closing Statement

Kalibra begins from a quiet conviction: that the most valuable thing an automated
system can offer is not certainty, but honesty about uncertainty.

It is an inspector that examines parts and then examines itself — that says not
only what it believes, but how far that belief can be trusted, and that grows more
careful exactly when it should. Its ambition is narrow on purpose and deep by
design: to do one thing completely, and to prove every claim it makes.

If Kalibra earns a single sentence, let it be this — it is a system built to know
when not to trust itself, and to show its work.
