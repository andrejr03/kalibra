# Kalibra Domain Plans Index

## 1. Purpose

This document is the canonical index and governance artifact for Kalibra's five
implementation-domain plans. It exists so that the boundaries fixed in those plans
are read together as one system, in one fixed order, with one handoff chain.

It is **not** a new implementation plan. It does not restate the five plans in
full, introduce new domain responsibilities, change the architecture, or choose
frameworks, models, storage, datasets, or metrics. Its job is narrower and durable:
to link the domain plans, summarise each boundary, fix the implementation order and
explain why, document the handoff chain, and preserve the rule that **each domain
owns exactly one responsibility** — so later implementation cannot skip a domain,
merge two for convenience, or let responsibilities bleed across the seams
(Engineering Plan §Engineering Principles; AGENTS.md Engineering Domains).

The five engine plans remain the authoritative domain-boundary documents. Where this
index and a domain plan appear to differ, the domain plan governs that domain's
boundary and the conflict must be surfaced, not silently resolved (AGENTS.md
Documentation Rules).

---

## 2. Domain Plan Inventory

The five permanent engineering domains of Kalibra, each with its authoritative plan:

1. **Inspection Engine** —
   [KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md](KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)
2. **Trust Qualification Engine** —
   [KALIBRA_TRUST_QUALIFICATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md](KALIBRA_TRUST_QUALIFICATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)
3. **Human Review Engine** —
   [KALIBRA_HUMAN_REVIEW_ENGINE_IMPLEMENTATION_PLAN_v1.0.md](KALIBRA_HUMAN_REVIEW_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)
4. **Evidence Engine** —
   [KALIBRA_EVIDENCE_ENGINE_IMPLEMENTATION_PLAN_v1.0.md](KALIBRA_EVIDENCE_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)
5. **Evaluation Engine** —
   [KALIBRA_EVALUATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md](KALIBRA_EVALUATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md)

These rest on the authoritative foundation documents — the
[Architecture](KALIBRA_ARCHITECTURE_v1.0.md) and the
[Engineering Plan](KALIBRA_ENGINEERING_PLAN_v1.0.md) — which define the domains and
their seams at the system level.

---

## 3. Fixed Implementation Sequence

The domains must be implemented in this fixed order:

1. **Inspection Engine**
2. **Trust Qualification Engine**
3. **Human Review Engine**
4. **Evidence Engine**
5. **Evaluation Engine**

This order follows the dependency chain:

```
raw inspection result
  → trust qualification
    → review handoff
      → evidence preservation
        → evaluation from evidence
```

**Why the order is fixed.** Each domain depends on the responsibility established
before it, and a domain must not be engineered to depend on one that has not yet
established its responsibility (Engineering Plan §Engineering Dependencies):

- The **Trust Qualification Engine** depends on the **Inspection Engine**: there is
  no confidence to calibrate until there is a raw judgement to qualify.
- The **Human Review Engine** depends on the **Trust Qualification Engine**: there is
  no principled deferral until decisions are qualified as *review*/drifted.
- The **Evidence Engine** preserves the records the first three emit: there is
  nothing durable to preserve and link until those domains produce records.
- The **Evaluation Engine** depends on the **Evidence Engine**: it can measure only
  what has been recorded.

The order is load-bearing. Building in this sequence ensures the system never depends
on a capability it has not yet proven.

> **Note on the Evidence seam.** Inspection, Trust Qualification, and Human Review
> each *emit* records into the Evidence Engine, so the Evidence contract is referenced
> from the start. The Evidence Engine is implemented as the fourth domain — after the
> three producers exist to define what it must preserve — but its emission seam is
> honoured by every producing domain from their own implementation onward. Sequencing
> Evidence fourth does not licence the earlier domains to skip emitting evidence.

---

## 4. Domain Boundary Summary

Concise summaries only. The authoritative boundary for each domain is its plan
(§2); these summaries must not be read as broadening or narrowing it.

### Inspection Engine

- **Owns:** examining one stabilized input; producing the raw defect judgement,
  localization, and raw (uncalibrated) anomaly measure.
- **Must not own:** calibration, trust qualification, abstention, drift, review
  routing, evidence custody, evaluation.
- **Consumes:** a stabilized inspection input from intake.
- **Emits:** a raw inspection result (+ its evidence record).

### Trust Qualification Engine

- **Owns:** calibrating confidence; qualifying the outcome (accept/reject/review/
  abstain); identifying uncertainty; drift-aware caution.
- **Must not own:** inspecting images, reconstructing or mutating inspection
  results, human review, operational routing, evidence presentation, evaluation,
  training.
- **Consumes:** the raw inspection result (reused, not re-inspected).
- **Emits:** a trust qualification result (+ its evidence record), preserving the
  raw result separately.

### Human Review Engine

- **Owns:** accepting *review*/drifted cases; preserving the deferral reason;
  preparing the evidence handoff; recording the reviewer decision; holding the
  boundary of authority.
- **Must not own:** inspection, calibration, mutation of upstream records, model
  updates from reviewer decisions, evaluation, evidence-surface ownership.
- **Consumes:** review-qualified cases with their full upstream chain.
- **Emits:** a review case and recorded reviewer decision (+ its evidence record).

### Evidence Engine

- **Owns:** preserving records faithfully and immutably; linking the full chain;
  recording absence explicitly; exposing inspectable, reproducible views.
- **Must not own:** inspection, qualification, routing, review, mutation of upstream
  records, training, evaluation, fabrication, hiding absence.
- **Consumes:** evidence records from Inspection, Trust Qualification, and Human
  Review.
- **Emits:** a preserved, linked record set and read-only inspectable views.

### Evaluation Engine

- **Owns:** measuring the system only from preserved evidence; keeping the five
  dimensions separate; surfacing named failure categories; separating missing
  evidence from weak performance.
- **Must not own:** inspection, calibration, qualification, routing, review,
  mutation of evidence, fabrication, training/feedback, single flattering scores,
  treating prototype visuals as performance.
- **Consumes:** preserved evidence records (read-only).
- **Emits:** evidence-backed evaluation reports, traceable to the records.

---

## 5. Handoff Chain

The system is one continuous flow. Each artifact is produced by exactly one domain
and consumed downstream without being reconstructed or mutated:

```
source input
  → raw inspection result            (Inspection Engine)
    → trust qualification result     (Trust Qualification Engine)
      → review case / reviewer decision   (Human Review Engine)
        → evidence records           (Evidence Engine)
          → evaluation report        (Evaluation Engine)
```

Properties the chain must preserve:

- **Single source.** The raw inspection result and its trust qualification derive
  from one examination of one input; they are never independently reconstructed and
  reconciled (Architecture §Reliability Principles; Engineering Plan §One source of
  truth).
- **Additive, non-destructive.** Each downstream artifact accompanies its upstream
  artifacts; nothing upstream is mutated. Raw inspection results and trust
  qualification results are preserved separately.
- **Full-chain traceability.** Where each link is present, the chain from source
  input to evaluation report remains traceable end to end; where a link is absent,
  the Evidence Engine records explicit absence rather than inventing it.
- **Evidence underlies all.** Inspection, Trust Qualification, and Human Review each
  emit into the Evidence Engine; the Evaluation Engine reads back from it. Evidence
  is produced by construction, not added later.

---

## 6. Implementation Rules

Later implementation **must not**:

- **Skip a domain.** All five domains must exist; uncertain and drifted cases must
  have their defined, unavoidable path through Trust Qualification and Human Review,
  and no decision may leave the system unqualified.
- **Merge two domains for convenience.** Each domain owns exactly one responsibility;
  responsibilities must not be combined to save effort (Engineering Plan §Single
  responsibility per domain).
- **Let downstream domains reconstruct upstream outputs.** Downstream domains reuse
  upstream artifacts across the defined seams; they must not re-inspect, re-derive,
  or recompute what an upstream domain already produced.
- **Let prototype visuals become evidence.** Prototype visuals and synthetic overlays
  are illustrative; they must never be preserved, exposed, or measured as evidence of
  model performance.
- **Let reviewer decisions update models.** Reviewer decisions are recorded as
  evidence only; no feedback loop may route them into retraining, recalibration, or
  model update (Exclusion X5).
- **Collapse evaluation into a single flattering score.** The five evaluation
  dimensions and named failure categories must remain separate; no aggregate may hide
  a weak dimension or category.

These rules restate boundaries already fixed in the domain plans and the foundation
documents; they are gathered here so a later implementer cannot breach one without
breaching this index.

---

## 7. Completion Criteria

The **domain-planning phase** (this phase — planning, not implementation) is
considered closed only when all of the following hold:

- **All five plans exist and are linked.** Each domain in §2 has its authoritative
  plan, reachable from this index.
- **Each plan fixes one responsibility.** Every plan states its single owned
  responsibility, its explicit non-responsibilities, its inputs, and its outputs,
  with no responsibility bleeding across a seam.
- **The seams agree.** Each domain's declared consumes/emits matches the adjacent
  domains' — the handoff chain in §5 is consistent end to end, with raw and qualified
  results kept separate and the full chain traceable.
- **The fixed order and its rationale are recorded.** The implementation sequence
  (§3) and its dependency rationale are documented and consistent with the
  Engineering Plan's dependency order.
- **The governance rules are stated.** The implementation rules (§6) are recorded so
  later work cannot skip, merge, reconstruct, mis-evidence, feed back, or flatter
  without breaching this index.
- **No scope drift.** The plans collectively introduce no new domain, no deferred
  capability, and no framework/model/storage/dataset/metric choice; boundaries match
  the architecture and requirements.

When these hold, planning is closed and the next phase is **review of the plans
before implementation begins**. Closure of planning is **not** a claim that any
domain is implemented; implementation proceeds in the fixed order of §3, each domain
validated against its own plan, and each reliability claim narrowed to the evidence
that supports it.

---

## Closing Statement

This index binds Kalibra's five domain plans into one governed whole. It fixes the
order in which the domains are built, the chain by which their artifacts flow, and
the rules that keep each domain to its single responsibility. It adds no capability
and changes no boundary; it makes the boundaries already fixed harder to cross by
accident.

Read together through this index, the five plans describe one system in which
inspection and trust arise from one source, uncertainty always has somewhere to go,
every artifact is preserved as honest evidence, and every claim is measured against
that evidence — built in order, domain by domain, with no step skipped and no seam
quietly erased.
