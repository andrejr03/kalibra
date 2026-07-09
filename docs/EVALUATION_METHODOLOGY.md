# Kalibra Evaluation Methodology

## Evaluation Philosophy

Kalibra holds itself to a single evaluative standard: no claim is made until it has
been demonstrated. The purpose of this methodology is to define how Kalibra proves
what it asserts about itself, so that its trustworthiness is something an observer
can verify rather than something the system declares.

The philosophy rests on three commitments. First, **evidence precedes assertion** —
a property is described as true only once a reproducible artifact supports it.
Second, **accuracy is necessary but not sufficient** — being right on average does
not establish that the system knows when it is wrong, and it is that self-knowledge
that Kalibra must prove. Third, **honesty outranks presentation** — when the
evidence for a claim is weak, flat, or absent, the claim is softened or withdrawn
rather than stated.

This methodology is deliberately independent of how Kalibra is built. It describes
what must be shown and to what standard, not how any measurement is computed. It
remains valid even if every component beneath it is replaced.

## Reliability Objectives

Evaluation in Kalibra serves a small set of objectives, each tied directly to the
system's central thesis that it knows when not to trust itself:

- **Demonstrate that confidence is meaningful** — that a stated level of certainty
  corresponds to the real chance of being correct.
- **Demonstrate that uncertainty is informative** — that the cases the system marks
  as doubtful are genuinely the cases where it is more often wrong.
- **Demonstrate that deferral is appropriate** — that the cases routed to human
  judgement are the ones that should not have been automated.
- **Demonstrate that caution responds to change** — that the system becomes
  measurably more careful as inputs drift from familiar conditions.
- **Demonstrate that all of the above are reproducible** — that the same evidence
  can be regenerated from a fixed starting point by an observer who does not trust
  the system.

Every dimension of evaluation below exists to serve one or more of these
objectives. Nothing is measured for its own sake.

## Evaluation Dimensions

Kalibra evaluates itself along distinct dimensions, kept separate so that strength
in one cannot disguise weakness in another:

- **Detection quality** — how well the system distinguishes defective from sound
  inputs, and how well it locates the defect within an input.
- **Calibration** — whether the confidence attached to decisions means what it
  says.
- **Uncertainty quality** — whether the system's own doubt corresponds to where it
  is actually wrong.
- **Review quality** — whether the cases sent to human judgement are the right ones
  to defer.
- **Drift response** — whether the system's caution increases as inputs move away
  from familiar conditions.

Detection quality establishes that Kalibra is a competent inspector. The remaining
four dimensions establish that it is a *trustworthy* one. A result is only complete
when the trust dimensions are reported alongside detection quality, never in place
of it.

## Calibration

Calibration evaluation asks a single question: when Kalibra states a level of
confidence, does reality agree with it?

The methodology requires confidence to be assessed against observed outcomes, so
that the gap between what the system claims and what actually happens is made
visible. A well-calibrated system's stated certainty tracks its real rate of being
correct; a poorly-calibrated one is overconfident or underconfident, and the
evaluation must expose which.

Calibration must be demonstrated, not assumed. The methodology requires that the
relationship between confidence and correctness be shown as inspectable evidence,
and that any step intended to improve calibration be evaluated by comparing the
state of the system before and after that step. Confidence that has not been shown
to be calibrated is not permitted to stand as confidence in any claim.

## Uncertainty

Uncertainty evaluation asks whether the system's doubt is informative — whether the
cases it is unsure about are the cases it tends to get wrong.

The central requirement is to show a relationship between expressed uncertainty and
actual error: the more uncertain the system reports itself to be, the higher the
rate of mistakes among those cases should be. If uncertain cases are no more
error-prone than confident ones, the uncertainty carries no information and the
system's self-knowledge is unproven, regardless of how accurate it is overall.

The methodology also requires that abstention be evaluated as a deliberate outcome.
Declining to decide must be shown to concentrate the hard and ambiguous cases,
rather than discarding decisions at random. Uncertainty is only a virtue when it
points at the right places, and the evaluation exists to confirm that it does.

## Human Review

Evaluation of the human review path asks whether the cases Kalibra hands to human
judgement are the cases that genuinely warrant it.

The methodology distinguishes the outcomes the system decides automatically from
the outcomes it defers, and requires that the deferred set be shown to be
disproportionately the difficult, error-prone, or ambiguous cases. The right
behaviour is for the cases the system keeps to be the ones it handles well, and for
the cases it surfaces for review to be the ones where automation would have been
unsafe.

This is the evaluative expression of Kalibra's role as a partner to human judgement
rather than a replacement for it. Routing more cases to review is not inherently
good and routing fewer is not inherently good; what the methodology requires is
that the *right* cases be routed, and that this be demonstrable.

## Drift Evaluation

Drift evaluation asks whether Kalibra becomes more cautious as inputs move away from
the conditions it knows.

The methodology requires that the system's response to change be demonstrated under
controlled, reproducible variation of conditions, graded from mild to severe. As
the departure from familiar conditions grows, two responses must move together: the
system's measured sense of how far inputs have drifted should rise, and its
willingness to defer to human judgement should rise with it. A system that keeps
deciding confidently as conditions degrade has failed this dimension, however
accurate it remains on familiar inputs.

This dimension carries a strict honesty obligation. If the system's caution does not
visibly increase as conditions worsen, the claim that it grows more careful under
drift must be withdrawn. The evaluation exists precisely to prevent that claim from
being asserted without proof.

## Evidence Requirements

Every claim Kalibra makes about its own reliability must be backed by evidence that
satisfies the following requirements:

- **Reproducible** — the evidence can be regenerated from a fixed starting point, so
  that it is a standing record rather than a momentary result.
- **Inspectable** — the evidence can be examined directly by an observer, who can
  see what the system concluded, where, and with what confidence.
- **Self-contained** — the evidence supporting a claim travels with the claim, so
  that the assertion and its justification are never separated.
- **Comparative where relevant** — where a step is intended to improve a property,
  the evidence shows the state before and after, so the improvement is demonstrated
  rather than asserted.
- **Honest about absence** — where evidence for a claim is missing or weak, that is
  recorded plainly, and the claim is adjusted to match.

The central rule is that the burden of proof rests on the system. An observer should
never have to take Kalibra's word for a reliability property; the evidence must let
them confirm it independently.

## Failure Categories

The methodology recognises that failures differ in kind, and evaluation must name
them rather than collapse them into a single rate:

- **Missed defects** — defective inputs accepted as sound. The most consequential
  failure, and one the evaluation must surface explicitly.
- **False alarms** — sound inputs flagged as defective, with their own cost to trust
  and to throughput.
- **Confident errors** — wrong decisions made with high stated confidence. These are
  the failures that most directly contradict Kalibra's thesis and must be tracked
  with particular care.
- **Misplaced uncertainty** — cases the system was unsure about that it actually
  handled correctly, or confident cases it got wrong; both indicate that
  uncertainty is not tracking error as required.
- **Mislocalized defects** — correct overall judgements that point to the wrong
  region, undermining the explanation behind a decision.
- **Unresponsive drift** — failure to grow more cautious as conditions degrade.

Naming these categories is itself an evaluative act. A single aggregate figure can
hide all of them; the methodology requires that they be distinguished, so that the
specific ways the system can fail are visible and accounted for.

## Success Criteria

Evaluation succeeds — and a reliability claim may be made — only when all of the
following hold and are supported by reproducible, inspectable evidence:

- the system is shown to be a competent inspector, distinguishing defective from
  sound inputs and locating defects within them;
- confidence is shown to be calibrated, so that stated certainty matches observed
  correctness;
- uncertainty is shown to be informative, concentrating error among the cases the
  system reports itself unsure about;
- the cases routed to human review are shown to be the cases that warranted
  deferral;
- caution is shown to increase measurably as inputs drift from familiar conditions;
- the distinct failure categories are reported separately rather than hidden within
  an aggregate;
- and every one of these results can be regenerated and inspected by someone who
  does not trust the system.

If any of these cannot be demonstrated, the corresponding claim is not made. Partial
evidence yields a partial, honestly-stated claim — never a full one.

## Methodology Boundaries

This methodology is deliberately bounded so that it remains a permanent reference
rather than a description of any particular build.

- **It defines standards, not procedures.** It states what must be shown and to what
  standard of proof, not how any measurement is produced.
- **It is implementation-agnostic.** It remains valid if the components beneath it
  are entirely replaced; nothing in it depends on a specific technique.
- **It evaluates the present system.** It measures what Kalibra claims to do, not the
  capabilities of a future, broader version.
- **It is a methodology, not a verdict.** It describes how trustworthiness is to be
  proven; it does not record the outcome of any particular evaluation.

Within these boundaries, the methodology serves one durable purpose: to ensure that
whenever Kalibra claims to know when not to trust itself, that claim rests on
evidence an observer can verify.
