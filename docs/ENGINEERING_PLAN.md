# Kalibra Engineering Plan

## Engineering Objectives

This document is the engineering blueprint for Kalibra. It bridges the system's
architecture and its eventual implementation by answering one question — *what must be
engineered?* — without answering *how it will be coded*. It defines the engineering
domains the system comprises, the responsibilities each must carry, and the way they
interact, so that any implementation has a permanent reference for what it is obligated
to build.

The objectives of the engineering effort are:

- to realise a system in which an inspection decision and the judgement of its
  trustworthiness are produced together, from one source;
- to organise that system into a small number of well-bounded engineering domains, each
  with a single, clear responsibility;
- to make the seams between those domains explicit, so that responsibilities do not bleed
  and the system can be reasoned about part by part;
- to ensure that every domain produces the evidence its claims depend on, as a built-in
  obligation rather than an afterthought;
- and to keep the whole within the system's defined boundaries, so that it can be
  engineered to completion.

Throughout this document, **must** and **must not** express binding engineering
obligations. Each statement describes a responsibility a conforming Kalibra is required to
realise.

## Engineering Principles

The engineering of Kalibra is governed by the following principles.

- **Single responsibility per domain.** Each engineering domain must own one clear concern.
  A domain that accumulates unrelated responsibilities must be divided.
- **Explicit seams.** The points at which domains hand work to one another must be defined
  and stable. What crosses a seam is a deliberate engineering decision, not an accident of
  convenience.
- **One source of truth.** The inspection judgement and its trust qualification must be
  engineered from the same examination of the same input; they must not be reconstructed
  independently and reconciled afterward.
- **Evidence by construction.** Every domain must produce, as part of its normal operation,
  the durable record needed to verify its claims. Evidence is not added later.
- **Reproducibility throughout.** Every domain must behave such that its outputs can be
  regenerated from a fixed starting point.
- **Boundaries are load-bearing.** No domain may take on responsibilities the system has
  deferred. The engineering boundaries are part of the design and must hold.
- **Honesty over capability.** A domain must not be engineered to assert more than it can
  demonstrate. Where it cannot produce supporting evidence, its claim must be narrowed.

These principles outrank engineering convenience. Where a chosen structure conflicts with
them, the structure must change.

## Core Engineering Domains

Kalibra is engineered as five cooperating domains, each a distinct engine with a single
responsibility:

1. **Inspection Engine** — examines inputs and reaches defect judgements.
2. **Trust Qualification Engine** — turns raw judgements into calibrated, qualified trust.
3. **Human Review Engine** — directs uncertain and drifted cases to human judgement.
4. **Evidence Engine** — preserves and presents the record of everything the system does.
5. **Evaluation Engine** — measures the system against its claims along distinct dimensions.

These domains form a directed flow. The Inspection Engine produces the substrate the Trust
Qualification Engine acts upon; qualified outcomes feed the Human Review Engine where
deferral is warranted; every domain emits records into the Evidence Engine; and the
Evaluation Engine draws on that recorded evidence to assess the system as a whole. The
Inspection and Trust Qualification engines, in particular, must share one examination of
one input — they are two responsibilities over a single source, not two independent
systems.

The sections that follow define each domain's responsibilities and its interactions with
the others.

## Inspection Engine

**Responsibility:** to examine each input and reach a defect judgement, locating where any
suspected defect lies.

The Inspection Engine must:

- accept inputs only in the stable, reproducible form established at the system's entry
  point, and reason about nothing that has not passed through it;
- produce, for each input, an overall judgement of whether the input is defective;
- produce, for each input judged defective, an indication of where within the input the
  suspected defect lies;
- produce a raw measure of how anomalous each input is, to serve as the substrate for trust
  qualification;
- treat that raw measure as not yet trustworthy confidence, leaving its calibration to the
  Trust Qualification Engine.

**Interactions:** the Inspection Engine hands its judgements, localizations, and raw
measures across a defined seam to the Trust Qualification Engine, and emits a record of each
to the Evidence Engine. It must not itself decide whether its judgements can be trusted;
that responsibility belongs to the next domain and must not bleed back into this one.

## Trust Qualification Engine

**Responsibility:** to turn the Inspection Engine's raw judgements into calibrated,
qualified statements of how far each can be trusted.

The Trust Qualification Engine must:

- calibrate raw measures so that stated confidence corresponds to observed correctness, and
  must not present an uncalibrated measure as confidence;
- sort each calibrated decision into an outcome reflecting its trustworthiness — clearly
  acceptable, clearly rejectable, or uncertain;
- provide the ability to abstain, declining to decide automatically when confidence is
  insufficient, and treat abstention as a valid outcome;
- assess how far an input has drifted from familiar conditions and increase the system's
  caution accordingly, deferring more as that distance grows;
- operate on the same examination of the same input as the Inspection Engine, never on an
  independently reconstructed one.

**Interactions:** it receives raw judgements from the Inspection Engine across the defined
seam, passes outcomes qualified as uncertain or drifted to the Human Review Engine, and
emits a record of every calibration, qualification, abstention, and drift response to the
Evidence Engine. This domain is the engineering expression of Kalibra's thesis; its
obligations may not be weakened to simplify any other domain.

## Human Review Engine

**Responsibility:** to ensure that every case the system declines to decide alone reaches
human judgement, with the evidence needed to act on it.

The Human Review Engine must:

- provide a defined path by which uncertain and drifted cases are directed toward human
  judgement rather than forced into an automated answer;
- present each routed case together with the evidence behind it — the input, its
  localization, and its qualified outcome — so that a human can act on a complete picture;
- hold the boundary between the system's authority and human authority, so that the system
  decides only what it is confident about and defers what it is not, and never overrides its
  own expressed uncertainty;
- ensure that the cases it routes are weighted toward the difficult, ambiguous, and
  error-prone, so that deferral is appropriate and not indiscriminate.

**Interactions:** it receives uncertain and drifted outcomes from the Trust Qualification
Engine, draws the supporting material it presents from the Evidence Engine, and records the
routing of each case back into the Evidence Engine. It must not alter the judgements it
receives; its responsibility is to route and present them, not to revise them.

## Evidence Engine

**Responsibility:** to preserve and present a durable, inspectable record of everything the
system does, so that its claims can be verified rather than trusted.

The Evidence Engine must:

- preserve, as durable artifacts, each decision, its localization, its calibrated
  confidence, its qualified outcome, and any routing or abstention;
- retain, where a property is improved, the state before and after, so that the improvement
  is demonstrated and not asserted;
- ensure that each reliability claim travels with the evidence that supports it, so that an
  assertion and its justification are never separated;
- present its record through an inspectable surface that lets an observer see what was
  concluded, where, and with what confidence, without trusting the system's word;
- disclose plainly, alongside the affected claims, wherever evidence is weak, incomplete, or
  absent.

**Interactions:** every other domain emits its records into the Evidence Engine, and both
the Human Review Engine and the Evaluation Engine draw upon it. The Evidence Engine is the
backbone that makes the rest of the system verifiable; it must record faithfully and must
not present a result as stronger than its evidence allows.

## Evaluation Engine

**Responsibility:** to measure Kalibra against its own claims, along distinct dimensions,
and to surface how the system can fail.

The Evaluation Engine must:

- assess the system along separate dimensions — detection quality, calibration, uncertainty
  quality, review quality, and drift response — so that strength in one cannot disguise
  weakness in another;
- confirm that confidence is calibrated, that uncertainty concentrates error, that deferral
  is appropriate, and that caution rises as inputs drift;
- distinguish the system's failure categories rather than collapsing them into a single
  figure, so that the specific ways it can fail remain visible;
- draw only on recorded, reproducible evidence, so that every measurement it reports can be
  regenerated;
- require that any claim unsupported by its measurements be narrowed or withdrawn.

**Interactions:** the Evaluation Engine consumes the records held by the Evidence Engine and
reports its findings as further inspectable evidence. It must measure the present system as
it is, not the capabilities of a future, broader one.

## Engineering Dependencies

The domains stand in a defined order of dependence, and the engineering must respect it:

- The **Trust Qualification Engine** depends on the **Inspection Engine**: there is no
  confidence to calibrate until there is a judgement to qualify.
- The **Human Review Engine** depends on the **Trust Qualification Engine**: there is no
  principled deferral until decisions are qualified.
- The **Evidence Engine** underlies all of the above: each domain depends on it to make its
  outputs durable and inspectable.
- The **Evaluation Engine** depends on the **Evidence Engine**: it can measure only what has
  been recorded.

This order is load-bearing. A domain must not be engineered to depend on one that has not
yet established its responsibility, and the shared examination underpinning inspection and
trust qualification must be engineered before either is considered complete. Building in
this order ensures the system never depends on a capability it has not yet proven.

## Engineering Boundaries

The engineering of Kalibra is bounded as deliberately as the system itself. No domain may
take on the following; they belong to a later, broader system:

- continuous, streaming, or live operation of any domain;
- hosting, deployment, or operation as a running service;
- monitoring of inputs over time as a live operational activity, or the alerting,
  scheduling, and operational infrastructure that would accompany it;
- feedback loops that update the system from human decisions;
- multiple inspection settings or input categories engineered in parallel;
- exhaustive comparison of competing detection approaches;
- reliance on live, collected, or continuously changing inputs.

Each boundary is an engineering decision, not an omission. A domain that reaches for any of
these has exceeded its remit, and the boundary must be restored rather than the scope
quietly expanded.

## Engineering Success Criteria

The engineering of Kalibra is successful when, and only when:

- the five domains exist, each owning a single, clear responsibility, with explicit and
  stable seams between them;
- the Inspection and Trust Qualification engines demonstrably operate on one examination of
  one input, so that decision and trust share a single source;
- every decision is calibrated and qualified before it leaves the system, and uncertain and
  drifted cases have a defined, complete path to human judgement;
- every domain produces, as part of its operation, durable and inspectable evidence of what
  it did, regenerable from a fixed starting point;
- the Evaluation Engine can measure the system along its distinct dimensions and surface its
  failure categories, drawing only on recorded evidence;
- no domain asserts more than its evidence supports, and no domain has taken on deferred
  scope.

Where any criterion is only partly met, the affected claims must be narrowed to match.
Engineering success is judged by demonstrated structure and evidence, not by intention.

## Closing Statement

This plan defines what must be engineered for Kalibra to exist as designed: five cooperating
engines, each with one responsibility, joined by explicit seams, resting on a backbone of
evidence, and held within deliberate boundaries. It says what each domain owes the others
and what each owes the observer — and it stops short of saying how any of it is built.

Engineered faithfully to this plan, Kalibra becomes not a set of components but a single
coherent system in which inspection and trust arise together, every claim carries its proof,
and the whole knows — and can show — when not to trust itself.
