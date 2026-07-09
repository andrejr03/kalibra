# Kalibra Dataset Strategy

## Dataset Philosophy

Kalibra's claims about its own trustworthiness can only be as credible as the data
those claims are demonstrated on. The dataset is therefore not a background detail
of the system; it is part of the evidence. This document defines the philosophy and
governance that any data Kalibra uses must satisfy, without naming any particular
dataset.

The philosophy rests on a single conviction: **data must support honest
demonstration, not flattering results.** A dataset earns its place in Kalibra by
making the system's behaviour — including its failures — visible and reproducible,
not by making the system look good. Where a dataset would obscure how the system
performs, conceal its mistakes, or make its claims impossible to verify, that
dataset does not belong in Kalibra regardless of convenience.

This strategy is deliberately abstract. It describes the characteristics future
data must have, so that it remains valid even as every concrete dataset Kalibra ever
uses is chosen, replaced, or retired.

## Dataset Objectives

The data Kalibra uses exists to serve the system's evaluative purpose. Concretely,
it must make it possible to:

- **Show competent inspection** — by containing both sound and defective inputs, so
  that the system's ability to distinguish and locate defects can be assessed.
- **Show meaningful confidence** — by providing enough ground truth that stated
  confidence can be checked against real outcomes.
- **Show informative uncertainty** — by including cases that are genuinely difficult
  or ambiguous, so that the link between the system's doubt and its errors can be
  observed.
- **Show appropriate deferral** — by containing the kinds of cases that should be
  routed to human judgement, so that review behaviour can be evaluated.
- **Show response to change** — by supporting controlled, graded variation of
  conditions, so that the system's growing caution under drift can be demonstrated.

Data that cannot serve these objectives cannot support Kalibra's claims, however
large or convenient it may be. The objectives, not the size, decide a dataset's
worth.

## Dataset Selection Principles

Any dataset considered for Kalibra is judged against the following principles:

1. **Relevance.** The data must reflect the inspection setting Kalibra is reasoning
   about, so that results transfer to the problem the system claims to address.
2. **Honesty of difficulty.** The data must include genuinely hard, subtle, and
   ambiguous cases. Data that is uniformly easy proves nothing about the system's
   self-knowledge.
3. **Sufficiency of ground truth.** The data must carry enough trustworthy labelling
   to support the evaluation dimensions the system depends on.
4. **Reproducibility.** The data must be obtainable and fixable into a stable form,
   so that every result drawn from it can be regenerated from the same starting
   point.
5. **Clarity of terms.** The conditions under which the data may be used must be
   known and compatible with how Kalibra uses it. Unclear permissions are treated as
   a reason to decline, not to proceed.
6. **Focus over breadth.** A single, well-understood body of data used thoroughly is
   preferred to many bodies of data used shallowly.

A dataset that fails any of these principles is set aside, and the reason is
recorded rather than left implicit.

## Ground Truth Principles

Ground truth is the foundation on which every reliability claim ultimately rests,
and Kalibra treats it accordingly.

- **Ground truth must be trustworthy.** A claim is only as sound as the labels it is
  measured against; questionable labelling undermines every result drawn from it.
- **Ground truth must be transparent.** How a label was determined, and by what
  standard, must be knowable, so that an observer can judge the claim as well as the
  result.
- **Ground truth must acknowledge ambiguity.** Where the correct answer is genuinely
  uncertain, that uncertainty is recorded rather than forced into a false
  certainty — ambiguous cases are part of the evidence, not noise to be removed.
- **Ground truth must be stable.** The reference against which the system is measured
  must be fixed for a given evaluation, so that results remain comparable and
  reproducible.

Where ground truth is weak, incomplete, or uncertain, that limitation is stated
plainly and the claims that depend on it are tempered. Kalibra never presents a
result as stronger than the ground truth beneath it allows.

## Dataset Quality Requirements

Beyond selection, the data Kalibra uses must meet standing quality requirements:

- **Representative.** It reflects the real variety of the inspection setting,
  including the difficult and unusual cases, not only the common and easy ones.
- **Balanced enough to be informative.** It contains sufficient examples of the
  outcomes that matter — including rare defects — for the system's behaviour on them
  to be assessed.
- **Clean in provenance, not in difficulty.** Its origin and handling are clear and
  documented, but its content is not sanitised to remove the hard cases that make
  evaluation meaningful.
- **Free of leakage.** The separation between what the system learns from and what it
  is evaluated on must be preserved, so that results reflect genuine capability
  rather than memorised answers.
- **Documented.** Its characteristics, limitations, and known biases are recorded, so
  that results can be interpreted in light of what the data can and cannot show.

These requirements protect the integrity of every claim Kalibra makes. Data that
cannot meet them weakens the evidence, and weak evidence is treated as a reason to
narrow the claim.

## Dataset Boundaries

Kalibra's use of data is deliberately bounded, in keeping with the system's overall
scope:

- **Fixed, not live.** Data is taken as a stable snapshot that can be reproduced, not
  as a continuously changing or streaming source.
- **Focused, not sprawling.** Data is drawn from a single, well-defined inspection
  setting rather than spread thinly across many at once.
- **Demonstrative, not exhaustive.** Variation of conditions is produced in a
  controlled, reproducible way to demonstrate behaviour, not gathered as an
  open-ended collection of real-world change.
- **Used as evidence, not collected as an activity.** Kalibra reasons about data it
  has; assembling new large-scale data collection is outside the system's purpose.

Each boundary keeps the data within a form that can be reasoned about, reproduced,
and completed. A clearly drawn limit on the data is part of the strategy, not a gap
in it.

## Dataset Governance

Data within Kalibra is governed by a small set of standing obligations:

- **Provenance is recorded.** Where data came from, and under what terms it may be
  used, is documented before it is relied upon.
- **Terms are respected.** Data is used only in ways consistent with the permissions
  attached to it, and any uncertainty about those permissions is resolved before use.
- **Limitations are disclosed.** Known biases, gaps, and weaknesses in the data are
  stated alongside the results drawn from it, never hidden.
- **State is fixed and reproducible.** The exact form of the data used for a given
  result is preserved, so that the result can be regenerated and audited.
- **Sensitivity is respected.** Where data carries sensitivity of any kind, it is
  handled accordingly, and that handling is part of the record.

Governance is not an administrative afterthought; it is what allows the data to
stand as credible evidence. An observer must be able to see not only what the data
showed, but that it was obtained and used responsibly.

## Dataset Evolution Strategy

Kalibra expects its data to change over time, and this strategy is designed to
survive that change.

- **The strategy outlives any dataset.** The principles here govern whatever data
  Kalibra uses next; replacing a dataset does not require rewriting the strategy.
- **Change is deliberate and documented.** When data is added, replaced, or retired,
  the reason and the implications for prior claims are recorded, so the history of
  the evidence is clear.
- **Broader data is an extension, not a starting point.** Expanding to additional
  inspection settings or richer conditions is treated as a later step, pursued only
  after the focused case has been demonstrated thoroughly.
- **Comparability is protected.** As data evolves, care is taken that results remain
  interpretable across versions, so that progress can be distinguished from a mere
  change of conditions.

Evolution is welcomed, but never at the cost of the honesty and reproducibility the
strategy exists to protect. New data must clear the same bar as the data it
replaces.

## Success Criteria

The dataset strategy succeeds when the data behind Kalibra's claims meets the
following, all demonstrable:

- the data is relevant to the inspection setting the system reasons about;
- it contains genuinely difficult and ambiguous cases, so that self-knowledge can be
  tested rather than assumed;
- its ground truth is trustworthy, transparent, and stable enough to support the
  claims drawn from it;
- it can be fixed into a reproducible form, so that every result can be regenerated;
- its provenance, terms, and limitations are documented and respected;
- and its boundaries are stated plainly, so what the data can and cannot show is
  clear.

Where any criterion is only partly met, the claims that rest on the data are
narrowed to match. The data is judged a success not when it is large or convenient,
but when it lets Kalibra prove exactly as much as it asserts and no more.

## Closing Statement

Data is where Kalibra's honesty is first tested. Before any decision is calibrated
or any uncertainty is examined, the evidence begins with the inputs the system is
shown — and a claim built on data that hides difficulty, obscures provenance, or
cannot be reproduced is a claim that cannot be trusted, however careful everything
above it may be.

This strategy exists so that the data beneath Kalibra is chosen and governed to the
same standard the system holds itself to: relevant, honest about difficulty,
reproducible, and plainly bounded. It names no dataset and depends on none. Whatever
data Kalibra uses, today or far in the future, must earn its place by making the
system's behaviour — its strengths and its failures alike — something an observer can
see and verify for themselves.
