# Kalibra — Claude Design Brief

## How to use this brief

You are Claude Design. This document is your complete source of truth for
Kalibra. You do not have access to the project's code, and you do not need it.
Everything required to design for Kalibra is contained here.

Read the whole brief before you begin. Your task is defined at the end, under
**Your task**. The sections before it exist so that what you design is grounded
in what Kalibra actually is — not in assumptions about what an inspection tool
usually looks like.

---

## What Kalibra is

Kalibra is a self-evaluating visual inspection system for industrial quality
control. It examines visual inputs — manufactured parts — for defects, and for
every inspection decision it makes, it also decides whether that decision can be
trusted.

That second act is the point of the whole system. Kalibra is not a defect
detector with reliability features attached. It is a system whose two
responsibilities — reaching a judgement, and qualifying how far that judgement
can be relied upon — are produced together, from the same examination of the
same input.

Kalibra exists to answer two questions at once:

> *Is this part defective?* and *Can you trust me when I say so?*

It is built on a single conviction: the most valuable thing an automated
inspector can offer is not certainty, but honesty about uncertainty. Most
automated systems fail silently — they keep answering with the same confidence
while quietly becoming wrong. Kalibra is designed to do the opposite: to know
when it should hesitate, to say so plainly, and to hand the cases it cannot
safely decide to a human.

### The boundary of the system

Kalibra is deliberately bounded. Understanding these boundaries is essential,
because they shape what the interface is and is not.

- **Offline, batch, locally reproducible.** Kalibra operates on a fixed body of
  inputs and produces a fixed body of outputs. From a fixed starting point, it
  can be re-run to regenerate exactly the same evidence.
- **Not live, not streaming, not a service.** There is no real-time feed, no
  continuous monitoring, no operational alerting, no deployment-as-a-service.
  Demonstrations of how the system behaves under changing conditions are
  produced as controlled, reproducible experiments — never as live operation.
- **One focused inspection setting.** A single, well-defined inspection problem,
  pursued to completion — not many product types or defect categories in
  parallel.
- **A partner to human judgement, not a replacement for it.** Where confidence is
  low, the human stays in the loop by design.

The interface you design is therefore not a live operations dashboard. It is an
**inspectable surface over a fixed, reproducible body of evidence** — a way for
an observer who does not trust the system to verify, for themselves, that the
system knows when not to trust itself.

---

## Engineering philosophy

Kalibra is built from a small set of convictions. These are not decoration; they
are the personality of the system, and the interface must embody them.

- **Honesty over polish.** A claim is only as good as the evidence behind it. If
  a capability cannot be demonstrated, it is softened or removed — never
  asserted. The interface must never make the system look more certain or more
  capable than its evidence supports.
- **Evidence before assertion.** Every headline claim is backed by an artifact
  that can be inspected. Nothing important is taken on faith. The interface's job
  is to *show the work*, not to summarise it away.
- **Reproducibility as a baseline.** Results are regenerable from a fixed
  starting point. The same evidence an observer sees can be reproduced by anyone.
- **Depth over breadth.** One problem solved completely, rather than many solved
  partially.
- **Boundaries stated, not hidden.** What the system does not do is named
  deliberately. A clearly drawn limit is a sign of understanding, not a gap.
- **Trust is earned through demonstration, not declared.** Reliability is a
  property to be evidenced on every decision, not a reputation to assume.

A guiding sentence for the whole system: *Kalibra inspects, and in the same
motion decides whether its own inspection can be trusted.*

---

## The five engineering domains

Kalibra is organised as five cooperating domains, each owning exactly one
responsibility, joined by explicit seams. They form a single directed flow. The
interface should make this flow legible — a decision is not a single verdict but
a chain that can be followed end to end.

1. **Inspection Engine — what the system sees.**
   Examines each input and reaches a defect judgement: *defective* or *not
   defective*, and where within the input the suspected defect lies. It also
   produces a *raw anomaly measure* — a number describing how unusual the input
   is. Crucially, this raw measure is **not yet trustworthy confidence**, and the
   system treats it as such. The Inspection Engine answers only "is this
   defective, and where?" — never "can this answer be trusted?"

2. **Trust Qualification Engine — how far to trust it.**
   Takes the raw judgement and turns it into a *calibrated confidence* — a stated
   certainty that is meant to correspond to the real chance of being correct. It
   sorts each decision into one of three outcomes — **accept**, **review**, or
   **reject** — and it can **abstain**, declining to decide automatically when
   confidence is insufficient. It also carries a *drift assessment*: a sense of
   how far an input has moved from familiar conditions, with the system growing
   more cautious as that distance grows. This domain is the expression of
   Kalibra's thesis. The distinction between a *raw anomaly score* and a
   *calibrated confidence* is foundational and must remain visible — they are not
   the same thing, and the interface must never blur them.

3. **Human Review Engine — where uncertainty goes.**
   The destination for everything Kalibra declines to decide alone. Only cases
   qualified as **review** enter here. Each case is handed off together with the
   evidence behind it — the input, its localization, and its qualified outcome —
   so a human can act on a complete picture rather than a bare verdict. The
   system decides what it is confident about and defers what it is not; it never
   overrides its own expressed uncertainty. A reviewer reaches a human decision
   (accept, reject, or inconclusive), or records that the case could not be
   reviewed.

4. **Evidence Engine — the durable record.**
   Preserves and presents a durable, inspectable record of everything the system
   did: each decision, its localization, its calibrated confidence, its qualified
   outcome, and any routing to review or abstention. Where evidence for a
   property is weak, incomplete, or absent, that absence is recorded *plainly and
   explicitly* rather than hidden. This is the backbone that makes every other
   domain verifiable. The interface is, in large part, the visible face of this
   domain.

5. **Evaluation Engine — measuring the system against its own claims.**
   Measures Kalibra along distinct dimensions, kept separate so that strength in
   one cannot disguise weakness in another:
   - **Detection quality** — does it find and locate defects?
   - **Calibration** — does stated confidence match real correctness?
   - **Uncertainty quality** — are the cases it is unsure about the ones it gets
     wrong?
   - **Review quality** — are the cases it defers the right ones to defer?
   - **Drift response** — does its caution rise as conditions degrade?

   It also names *failure categories* rather than collapsing them into a single
   score — missed defects, false alarms, confident errors, misplaced
   uncertainty, mislocalized defects, and unresponsive drift. The interface must
   resist the temptation to reduce all of this to one flattering number. Distinct
   dimensions and distinct failures stay distinct.

---

## The intended workflow

A single input moves through the system as one continuous chain:

> **input intake → inspection & raw judgement → trust qualification → (human
> review, where required) → evidence recording → evaluation from recorded
> evidence**

Read as a story for one part:

1. A part's image enters through one well-defined entry point and is fixed into a
   stable, reproducible form.
2. The Inspection Engine judges it defective or sound, marks where the suspected
   defect is, and produces a raw anomaly measure.
3. The Trust Qualification Engine calibrates that into a confidence, sorts it into
   accept / review / reject, possibly abstains, and assesses drift.
4. If the outcome is *review* — because the system abstained, or the input has
   drifted, or it is simply uncertain — the case is handed to a human with its
   full evidence.
5. Every step is recorded as durable evidence, including any absences or
   limitations.
6. Across many such records, the Evaluation Engine measures the system against
   its claims, dimension by dimension, naming the specific ways it can fail.

The interface should let an observer move along this chain in both directions:
from a single decision down into the evidence that produced it, and from the
aggregate evaluation back to the individual cases behind it.

---

## Product personality

If Kalibra were a person, it would be a meticulous, unshowy expert who would
rather say "I am not sure — look here" than bluff. Calm, exact, and quietly
confident precisely because it is honest about its limits.

The personality the interface must carry:

- **Honest and restrained.** Never overstated. Confidence is shown with its
  caveats attached, never louder than the evidence allows.
- **Rigorous and precise.** Every number, region, and outcome is traceable to
  something an observer can inspect.
- **Calm under uncertainty.** Doubt, abstention, and deferral are presented as
  legitimate, designed outcomes — not as errors, warnings, or failures to be
  styled in alarm.
- **Inspectable, not authoritative.** The interface invites scrutiny rather than
  asking to be believed. It says "here is the evidence," not "trust me."
- **Serious, not sterile.** This is a high-consequence domain. The tone is
  considered and grown-up, but it should still feel crafted and alive, not
  bureaucratic.

A specific tonal instruction: **distinguish the three trust outcomes — accept,
review, reject — and the abstention state without falling into a naïve
green/yellow/red traffic-light metaphor.** *Review* and *abstain* are not
warnings; they are the system behaving correctly. Find a visual language for
"the system is appropriately deferring" that reads as competence, not as a
problem state.

---

## What the interface should communicate

Above everything, the interface must let someone who does not trust Kalibra
verify, from what they can see, that Kalibra knows when not to trust itself.

Concretely, it must make these things legible:

- **A decision and its trustworthiness, together.** Never a verdict alone —
  always the verdict *and* how far it can be relied upon.
- **The separation of raw anomaly from calibrated confidence.** These are
  different quantities at different stages. The design must keep them visibly
  distinct and never let one masquerade as the other.
- **Defect localization.** Where in the input the suspected defect lies — the
  spatial evidence behind a judgement.
- **The three outcomes plus abstention**, presented so that deferral reads as
  correct behaviour rather than failure.
- **Drift** — that an input has moved away from familiar conditions, and that the
  system has grown more cautious in response.
- **The hand-off to human review** — which cases were deferred, and the complete
  evidence a reviewer needs.
- **Evidence and its absence.** Where evidence is missing or weak, that gap is
  shown plainly. Honesty about absence is a feature to be designed for, not an
  edge case to hide.
- **Evaluation along separate dimensions**, with failure categories named — not
  reduced to a single aggregate score.
- **Reproducibility** — a sense that what is shown is a standing, regenerable
  record, not a momentary readout.

Equally important — what the interface must *not* imply:

- It must not look like a live, real-time operations console.
- It must not present raw scores as if they were calibrated confidence.
- It must not let a single summary figure stand in for the distinct dimensions.
- It must not dramatise uncertainty, abstention, or deferral as error states.
- It must not claim more than the evidence shown supports.

---

## Your task

Design the visual language and interface concept for Kalibra as described above.

Produce **exactly three fundamentally different visual concepts.** Each must
represent a genuinely different *design philosophy* — a different stance on how
trust, evidence, and uncertainty are made visible — not merely a different colour
palette applied to the same layout. Two concepts that differ only in styling do
not count as two concepts. Push them apart: they should disagree about what the
interface is *for* and how an observer is meant to relate to it.

For each of the three concepts, provide:

- **Design philosophy** — the core idea, and the stance on trust and evidence it
  embodies. Show how it expresses Kalibra's personality and makes the required
  things legible.
- **Strengths** — what this philosophy does especially well for Kalibra.
- **Weaknesses** — where it is weaker, what it risks, or what it trades away.

Bring each concept to life concretely — through described layouts, visual
language, and representative views (for example, how a single qualified decision
is shown, how a deferred case is handed off, and how the evaluation surface
reports its dimensions). Make the three concepts vivid and distinct enough that a
reader can feel the difference between living inside one versus another.

Finally, **recommend exactly one concept.** State which, and justify the choice
specifically against Kalibra's philosophy, personality, and what the interface
must communicate — especially honesty over polish, the visible separation of raw
anomaly from calibrated confidence, deferral-as-competence, and evidence an
observer can inspect rather than be asked to believe.
