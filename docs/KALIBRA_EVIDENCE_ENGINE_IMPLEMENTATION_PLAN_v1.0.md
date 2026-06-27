# Kalibra Evidence Engine Implementation Plan

## About This Plan

This document is the implementation plan for the **Evidence Engine**, the
architectural backbone that makes every other Kalibra domain inspectable. It
preserves, links, and exposes the durable evidence records produced by the
[Inspection Engine](KALIBRA_INSPECTION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md), the
[Trust Qualification Engine](KALIBRA_TRUST_QUALIFICATION_ENGINE_IMPLEMENTATION_PLAN_v1.0.md),
and the
[Human Review Engine](KALIBRA_HUMAN_REVIEW_ENGINE_IMPLEMENTATION_PLAN_v1.0.md).

It is an architecture-first plan: it fixes the permanent engineering boundary of
the Evidence Engine — what it owns, what it refuses, what crosses its seams, and
how it is validated — without choosing how any of it is built.

The plan deliberately does **not** select databases, storage frameworks, or UI
frameworks, and does **not** define final evaluation metrics. Those belong to
later phases and to other domains. This document defines the boundary those later
choices must respect.

Throughout, **must** and **must not** express binding engineering obligations,
consistent with the language of
[`docs/KALIBRA_ENGINEERING_PLAN_v1.0.md`](KALIBRA_ENGINEERING_PLAN_v1.0.md) and
[`docs/KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md`](KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md).

---

## 1. Purpose

The Evidence Engine is the architectural backbone that turns Kalibra's
trustworthiness from a property the system *claims* into a property an observer
can *verify* (Architecture §Evidence Layer). Nothing important in Kalibra is taken
on faith; the Evidence Engine is how that principle is enforced structurally.

Its purpose is to **preserve, link, and expose** the durable records produced by
the upstream engines — so that each decision, its localization, its calibrated
confidence, its qualified outcome, any routing or abstention, and any reviewer
decision can be inspected, reproduced, and audited (Requirements E1–E5, P1–P5).

The Evidence Engine creates no findings of its own. It does not inspect, qualify,
review, or evaluate. It is the durable record and the inspectable surface over
that record — faithful to what the upstream engines did, explicit about what is
absent, and never stronger than the evidence it holds (Engineering Plan §Evidence
Engine).

---

## 2. Responsibilities

The Evidence Engine **must**:

- **Accept evidence records from upstream engines.** Receive the durable records
  emitted by the Inspection, Trust Qualification, and Human Review engines as part
  of their normal operation (E1).
- **Preserve the full chain.** Preserve, where present, the complete chain: source
  input → raw inspection result → trust qualification → review case → reviewer
  decision — so any decision remains traceable end to end (E1, H2, P-traceability).
- **Record absence explicitly.** Where a stage's evidence is missing, unavailable,
  or not yet produced, store that absence as an explicit, inspectable fact — never
  as a gap to be guessed or filled (E5).
- **Preserve immutable links between records.** Maintain durable, immutable links
  binding each record to the upstream artifacts it derives from, so an assertion
  and its justification are never separated (E3).
- **Expose inspectable evidence views.** Provide inspectable views over the
  preserved records for later prototype and product surfaces, letting an observer
  see what was concluded, where, and with what confidence, without trusting the
  system's word (E2).
- **Support reproducibility and replay.** Hold records such that the same evidence
  can be regenerated from a fixed starting point, supporting replay and audit
  (P1, P2, C2).
- **Keep evidence additive, not destructive.** Preserve records additively;
  upstream artifacts are never mutated, overwritten, or corrected (core boundary).
- **Keep evidence honest.** Ensure records and views do not overstate system
  capability, and that limitations are disclosed plainly alongside the affected
  claims (E5, R7).

These responsibilities are the complete remit of the engine. Anything not listed
here is, by design, not its job.

---

## 3. Explicit Non-Responsibilities

The Evidence Engine **must not** take on any of the following. Each belongs to a
named domain or a deferred architecture, and the boundary is load-bearing:

- **Inspect images.** It must not examine visual inputs. *(Inspection Engine.)*
- **Create raw inspection judgements.** It must not produce judgements,
  localizations, or anomaly measures; it stores those it receives. *(Inspection
  Engine.)*
- **Calibrate confidence.** It must not produce or alter calibrated confidence.
  *(Trust Qualification Engine.)*
- **Qualify trust.** It must not sort decisions into accept/review/reject/abstain.
  *(Trust Qualification Engine.)*
- **Decide review routing.** It must not determine that a case goes to a human.
  *(Trust Qualification Engine / Human Review Engine.)*
- **Perform human review.** It must not present cases for adjudication or collect
  reviewer judgement; it stores the records of those that occurred. *(Human Review
  Engine.)*
- **Modify upstream records.** It must not mutate, overwrite, or correct any record
  it receives. All upstream artifacts are immutable to it.
- **Train or update models.** It must not train, retrain, recalibrate, or update
  any model, and must not turn reviewer decisions into a feedback loop (Exclusion
  X5).
- **Evaluate performance.** It must not measure detection quality, calibration,
  uncertainty quality, review quality, or drift response. *(Evaluation Engine.)*
- **Fabricate evidence.** It must not invent, infer, or synthesise records or
  fields that the upstream engines did not produce.
- **Hide evidence absence.** It must not conceal, smooth over, or silently omit
  missing evidence; absence is recorded explicitly (E5).

The engine must also remain within Kalibra's constraints: offline, batch, and
reproducible, with no live, streaming, hosted, or continuously operating
behaviour and no operational alerting or scheduling (Constraints C1, C2;
Exclusions X1–X4).

A specific honesty boundary: the Evidence Engine **must not turn prototype visuals
or synthetic overlays into evidence of model performance.** Prototype assets are
illustrative; they must never be recorded or exposed as if they were demonstrated
model results (Foundation §Engineering Philosophy; AGENTS.md Trust & Reliability
Rules).

---

## 4. Inputs

The Evidence Engine accepts evidence records emitted by the three upstream
engines, each as part of that engine's normal operation:

- **Inspection evidence records** — the raw inspection result (raw defect
  judgement, raw anomaly measure, localization reference) bound to its
  source-input reference. (Inspection Engine plan §8, Contract C.)
- **Trust qualification evidence records** — calibrated confidence, qualified
  outcome (accept/reject/review/abstain), uncertainty characterisation, and
  drift-caution annotation, bound to the raw inspection result they qualify. (Trust
  Qualification Engine plan §8, Contract D.)
- **Review evidence records** — the prepared review case, preserved deferral
  reason, recorded reviewer decision, and the upstream-chain binding. (Human Review
  Engine plan §8, Contract D.)

Properties the inputs **must** satisfy:

- Each record is a genuine artifact emitted by an upstream engine, carrying the
  references needed to link it into the chain (E1, E3).
- Each record arrives **already complete and immutable** from the engine that
  produced it; the Evidence Engine reads and preserves it, never edits it.
- Records arrive from a fixed body of upstream outputs (offline/batch); there is no
  live or streaming source (C1, C4, X8).

What the engine **must not** require or assume:

- Any access to the raw image or to intake beyond the source-input *reference*
  carried in the records.
- Any label, ground-truth, or evaluation of any record.
- That every stage is present. A chain may legitimately stop early (e.g. a case
  that was accepted and never reviewed); the engine records what exists and marks
  the rest as explicit absence (E5).

The concrete representation of these records and of stored absence is left to
implementation; this plan fixes the engine's *contract* with them.

---

## 5. Outputs

The Evidence Engine produces:

- **A preserved evidence record set.** The durable, immutable store of all accepted
  records, each kept faithfully as received (E1).
- **Immutable chain links.** The durable links binding records into the chain
  source input → raw inspection result → trust qualification → review case →
  reviewer decision, with each present link traceable and each missing link marked
  as explicit absence (E3, E5).
- **Inspectable evidence views.** Read-only views over the preserved records for
  later prototype and product surfaces, exposing what was concluded, where, and
  with what confidence — including disclosed limitations and recorded absences
  (E2, E5).
- **Replay/reproducibility support.** The means to regenerate the same evidence
  from a fixed starting point, so records are standing, reconstructable artifacts
  rather than momentary outputs (P1, P2, C2).

Properties the plan fixes:

- Outputs are **additive and non-destructive.** Preserving and exposing evidence
  never mutates upstream artifacts (core boundary).
- **Raw inspection results and trust qualification results are preserved
  separately.** They are linked but kept as distinct records, so a raw measure is
  never conflated with calibrated confidence (core boundary).
- **Reviewer decisions are recorded evidence, not feedback.** They are preserved
  and exposed as evidence; the engine opens no path from them into model updates
  (Exclusion X5, core boundary).
- **Views never overstate capability.** No view presents a record as stronger than
  it is, and none presents prototype visuals or synthetic overlays as model
  performance (E5, R7, core boundary).
- Outputs are **read-only to consumers.** Prototype/product surfaces read from the
  Evidence Engine; they do not write upstream artifacts through it.

The Evidence Engine is the source from which the Human Review Engine draws hand-off
material and from which the Evaluation Engine later draws everything it measures.

---

## 6. Domain Boundaries

The Evidence Engine is the backbone beneath all other domains; it is written to by
three engines and read by two consumers.

**Inbound seams — Inspection / Trust Qualification / Human Review → Evidence.**
Every upstream engine emits its records into the Evidence Engine. What crosses each
seam is a complete, immutable record. The Evidence Engine preserves it faithfully;
it must record faithfully and must not present a result as stronger than its
evidence allows (Engineering Plan §Evidence Engine).

**Outbound seam — Evidence → Human Review.**
The Human Review Engine draws the supporting material it presents from the Evidence
Engine. The Evidence Engine supplies read-only views; it does not perform the
review.

**Outbound seam — Evidence → Evaluation.**
The Evaluation Engine consumes the records held by the Evidence Engine. The
Evidence Engine supplies the evidence; it does not perform the evaluation, and it
draws no measurements of its own (Engineering Plan §Engineering Dependencies).

**Outbound seam — Evidence → Prototype/Product surfaces.**
Later inspectable surfaces read evidence views. The Evidence Engine exposes; it
does not own those surfaces' UI, and it never lets a surface's illustrative assets
become recorded evidence of performance.

Boundaries the engine must hold:

- It must **weaken no Evidence requirement** and must not let any other domain do
  so (AGENTS.md Architectural Rules).
- It must not create, mutate, qualify, route, review, train, or evaluate;
  responsibilities must not bleed across the seam for convenience (Engineering Plan
  §Engineering Principles).
- It must preserve raw inspection and trust qualification results **separately**,
  and keep reviewer decisions as recorded evidence, not feedback (core boundary).
- It must remain offline/batch/reproducible and introduce no live operation
  (C1, C2, X1).

---

## 7. Internal Processing Stages

The engine's internal work is described here as **responsibility stages**, not as
an algorithm. The stages fix *what must happen in order*, not *how* any stage is
implemented. No database, storage mechanism, or UI is chosen here.

1. **Record intake.** Receive an evidence record from an upstream engine across an
   inbound seam and confirm it is a complete, well-formed record carrying its
   linking references. Reject — as a failure mode (§9), not by silent repair —
   anything malformed or missing required references.

2. **Faithful preservation.** Store the record durably and immutably, exactly as
   received. The record is read; it must not be edited, normalised in a way that
   loses content, or merged into another record. Raw inspection results and trust
   qualification results are preserved as **separate** records.

3. **Link binding.** Bind the record into the chain via immutable links to the
   upstream artifacts it references — source input, raw inspection result, trust
   qualification, review case, reviewer decision — as those references indicate.

4. **Absence recording.** Where a chain link has no corresponding record (a stage
   that did not occur or whose evidence is unavailable), record that absence
   explicitly as an inspectable fact. Absence is stored, never inferred away (E5).

5. **View construction.** Construct read-only, inspectable views over the preserved
   records and their links — surfacing conclusions, localizations, calibrated
   confidence, qualified outcomes, routing/abstention, reviewer decisions, recorded
   absences, and disclosed limitations — without altering any record.

6. **Replay support.** Provide the means to regenerate the same evidence and the
   same views from the same fixed starting point, so records and views are
   reproducible (P1, P2).

Ordering and boundary obligations:

- Preservation (stage 2) must precede linking and views; nothing is exposed that
  was not first faithfully preserved.
- No stage may inspect images, create or alter upstream results, qualify, route,
  review, train, or evaluate. If a stage appears to need any of these, the need
  belongs to a different domain and the seam, not this engine.
- Replay support (stage 6) **regenerates preserved evidence**; it must not silently
  **re-run** the Inspection or Trust Qualification engines. Re-running upstream
  computation is out of scope unless a later implementation scope explicitly
  authorises it (core boundary).
- All stages operate offline and in batch; no stage introduces live, streaming, or
  continuously operating behaviour (C1, X1).
- Every stage must be deterministic with respect to the fixed body of records, so
  the store and views are regenerable (C2, P2).

---

## 8. Data Contracts

This section fixes the **shape and obligations** of what the engine consumes,
preserves, and exposes, expressed as abstract contracts. Concrete types,
encodings, field names, storage layouts, and view formats are deliberately left to
implementation; only the obligations below are binding.

**Contract A — Inbound Evidence Record (consumed).**
- One of: an inspection evidence record, a trust qualification evidence record, or
  a review evidence record (see §4).
- Carries the linking references needed to place it in the chain.
- Is treated as **immutable**: the engine reads and preserves it and must not
  mutate, overwrite, or correct any field.

**Contract B — Preserved Record (stored).**
- A durable, faithful copy of an inbound record, kept exactly as received.
- Raw inspection results and trust qualification results are preserved as
  **separate** preserved records, never merged (core boundary).
- Carries enough identity to be referenced by links and views.

**Contract C — Chain Link (stored).**
- An immutable link binding one preserved record to an upstream artifact it
  references, along one edge of: source input → raw inspection result → trust
  qualification → review case → reviewer decision.
- Where a referenced artifact is absent, the link is replaced by an **explicit
  absence marker** rather than omitted silently (E5).

**Contract D — Absence Marker (stored).**
- An explicit, inspectable record that a given stage's evidence is missing or
  unavailable, with no fabricated content standing in for it (E5).

**Contract E — Evidence View (exposed).**
- A read-only projection over preserved records, links, and absence markers.
- Faithfully represents what was concluded, where, and with what confidence, and
  surfaces recorded absences and disclosed limitations.
- Must not present a record as stronger than its evidence allows, and must not
  present prototype visuals or synthetic overlays as model performance (E2, E5, R7,
  core boundary).

Contract invariants:

- **Additive, non-destructive.** Preserving, linking, and exposing never mutate
  upstream artifacts (core boundary).
- **Full-chain where present.** The chain from source input to reviewer decision is
  preserved wherever each link exists; missing links are explicit absences (E1, E5).
- **Separation preserved.** Raw inspection and trust qualification results remain
  distinct records (core boundary).
- **No feedback.** Reviewer decisions are preserved and exposed as evidence and are
  never transformed into a model update (Exclusion X5).
- **Honest exposure.** Views never overstate capability and never re-label
  illustrative assets as demonstrated results.
- **Reproducibility.** The store and its views are regenerable from a fixed
  starting point (P1, P2, C2).

---

## 9. Failure Modes

The engine must distinguish **recorded absence** (a legitimate, inspectable fact —
normal) from **engine failure** (the engine cannot accept, preserve, link, expose,
or reproduce evidence). A failure is never silently smoothed into an apparent
record, and an absence is never disguised as present evidence or vice versa.

Identified failure modes and required handling:

- **Malformed or incomplete inbound record.** A record arrives missing required
  fields or linking references. The engine must refuse it and surface the failure;
  it must not repair, complete, or fabricate the record.
- **Attempted mutation of an upstream artifact.** Any internal path that would
  alter a preserved record or an upstream artifact is a defect to be prevented; all
  records are immutable (core boundary).
- **Conflation of raw and qualified results.** Any path that would merge a raw
  inspection result with a trust qualification result violates required separation
  and must be prevented (core boundary).
- **Missing chain link.** A referenced upstream artifact is absent. This is **not**
  a failure: the engine records explicit absence (Contract D). It is listed here to
  fix that absence must be recorded, never hidden or invented (E5).
- **Fabrication pressure.** Any path that would invent, infer, or synthesise a
  record or field the upstream engines did not produce is a boundary violation to
  be prevented.
- **Overstatement in a view.** Any view that would present a record as stronger
  than its evidence, or present prototype visuals/synthetic overlays as model
  performance, is a defect to be prevented (E5, R7, core boundary).
- **Attempted feedback into the model.** Any path that would route a reviewer
  decision into retraining, recalibration, or model update is a boundary violation
  to be prevented (Exclusion X5).
- **Unauthorised re-run.** Any replay path that would silently re-run Inspection or
  Trust Qualification, absent explicit later authorisation, exceeds the engine's
  remit and must be prevented (core boundary).
- **Non-reproducibility.** Re-running over the same fixed body of records yields a
  different store or different views, indicating hidden state. This violates
  C2/P2 and must be surfaced as a defect, not tolerated.
- **Introduction of live operation.** Any path that would make evidence handling
  live, streaming, or continuously operating is out of bounds and must be prevented
  (C1, X1).

General obligations for all failure modes:

- Failures must be **explicit and inspectable**, never swallowed.
- A failure or an absence must never be **disguised as present, complete, or
  stronger evidence**; honesty about absence and limitation is the engine's core
  duty (E5).
- Failure handling must not import other domains' responsibilities (it must not, for
  example, re-inspect, recalibrate, or evaluate — it only surfaces the failure).

This plan fixes *which* failures must be handled and *how they must be treated*;
the concrete error mechanisms are implementation choices.

---

## 10. Validation Strategy

Validation here means confirming the engine honours its boundary and contracts —
**not** measuring anything about the records it holds, which is the Evaluation
Engine's job and out of scope for this plan. No evaluation metrics are defined.

The engine must be validated against:

- **Faithful preservation.** Every preserved record matches the inbound record
  exactly; nothing is edited, lost, or merged (E1, core boundary).
- **Additive, non-destructive.** Upstream artifacts are unchanged after intake,
  preservation, linking, and exposure (core boundary).
- **Separation preserved.** Raw inspection results and trust qualification results
  are stored as distinct records (core boundary).
- **Full-chain where present.** The chain source input → raw inspection result →
  trust qualification → review case → reviewer decision is preserved wherever each
  link exists (E1, H2).
- **Explicit absence.** Missing or unavailable evidence is recorded as an explicit
  absence marker and is never invented or hidden (E5).
- **Immutable links.** Links between records are durable and immutable (E3).
- **Honest views.** No view overstates capability, and no view presents prototype
  visuals or synthetic overlays as model performance (E2, E5, R7, core boundary).
- **No feedback.** No reviewer decision is routed into model updates (Exclusion X5).
- **Replay without re-run.** Replay regenerates preserved evidence and does not
  re-run Inspection or Trust Qualification absent explicit authorisation (core
  boundary).
- **Boundary conformance.** The engine performs no inspection, calibration,
  qualification, routing, review, training, or evaluation. The absence of these
  responsibilities is validated, not assumed.
- **Offline / batch / reproducible.** The engine introduces no live operation, and
  the same fixed body of records yields the same store and views on re-run
  (C1, C2, P2, X1).
- **Failure handling.** Each failure mode in §9 is surfaced explicitly and never
  disguised as present or stronger evidence.

Validation must rest on **the preserved records and views themselves**, so an
observer can verify conformance without trusting the engine's word, consistent with
Kalibra's evidence-before-assertion philosophy.

---

## 11. Testing Strategy

Testing fixes *what must be demonstrated* about the engine; it does not fix a
database, storage framework, UI framework, harness, or tooling, and it does not
test the quality of the records held.

The engine's test suite must demonstrate, at minimum:

- **Preservation tests.** An inbound record is preserved exactly; the preserved copy
  equals the input and is not editable through the engine.
- **Non-destruction tests.** After intake, preservation, linking, and view
  construction, upstream artifacts are byte-for-byte unchanged.
- **Separation tests.** A raw inspection result and its trust qualification result
  are stored as distinct preserved records and are never merged.
- **Full-chain tests.** Given records for every stage, the chain source input →
  raw inspection result → trust qualification → review case → reviewer decision is
  preserved and traversable.
- **Absence tests.** Given a chain that stops early (e.g. accepted, never reviewed),
  the missing links are recorded as explicit absence markers — not omitted, not
  invented.
- **Immutable-link tests.** Links cannot be altered after creation.
- **Honest-view tests.** A view never presents a record as stronger than it is, and
  prototype visuals / synthetic overlays cannot be exposed as model performance;
  these are asserted as *must-not-exist*.
- **No-feedback tests.** No path routes a reviewer decision into retraining,
  recalibration, or model update (Exclusion X5).
- **Replay tests.** Replay regenerates the same preserved evidence and views from a
  fixed starting point and does not re-run Inspection or Trust Qualification.
- **Boundary tests (negative).** The engine exposes no inspection, calibration,
  qualification, routing, review, training, or evaluation behaviour; these are
  asserted as *must-not-exist*, guarding the seams.
- **Offline / reproducibility tests.** The engine introduces no live operation, and
  re-running over an identical fixed body of records yields an identical store and
  identical views.
- **Failure-mode tests.** Each failure mode in §9 (malformed record, mutation
  attempt, raw/qualified conflation, fabrication pressure, view overstatement,
  attempted feedback, unauthorised re-run, non-reproducibility, attempted live
  operation) is provoked and shown to be surfaced explicitly and not disguised —
  and a missing chain link is shown to be recorded as explicit absence, not a
  failure.

Testing principles:

- Tests assert the engine's **boundary and contracts**, not the quality of the
  evidence. No test in this domain may smuggle in an evaluation metric.
- Tests must use a **fixed body of records** so they are themselves reproducible
  (C2).
- Tests should be small and focused, each covering one obligation, consistent with
  Kalibra's coding rules (small, testable modules).

The concrete test code, fixtures, and runner are produced during implementation,
not in this plan.

---

## 12. Future Extension Points

These are points where later phases and other domains attach to the Evidence
Engine. Naming them fixes the boundary now; none grants licence to absorb another
domain's responsibility or open a deferred capability.

- **Storage substrate is replaceable.** Because this plan fixes the engine's
  contracts and seams but not its storage mechanism, the chosen substrate (when a
  later phase selects one) can be implemented and later replaced without changing
  the engine's boundary, provided records stay faithful, separate, immutable, and
  regenerable (Contracts A–E).
- **Inspectable surfaces build on evidence views.** Later prototype and product
  surfaces read the read-only views this engine exposes (Contract E). The Evidence
  Engine's obligation is faithful, honest exposure; the surface's UI is the
  extension and is not owned here.
- **Evaluation consumes preserved evidence.** The Evaluation Engine later measures
  the system from the records this engine holds — never from inside this engine,
  and never by adding evaluation logic here.
- **Authorised replay/re-run is a later scope.** Replay regenerates preserved
  evidence today. Should a later implementation scope explicitly authorise
  re-running Inspection or Trust Qualification for reproduction, that authorisation
  is a new, owner-set boundary — this engine does not assume it.
- **Comparative (before/after) evidence can be extended.** Retaining the state
  before and after an improvement (E4) can be carried as additional preserved
  records and links without changing the engine's responsibility, provided each
  remains faithful, separate, and honestly exposed.

Deferred scope remains deferred (Engineering Plan §Engineering Boundaries; AGENTS.md
Scope Protection). An extension that would let the Evidence Engine inspect, qualify,
route, review, train, update models from reviewer decisions, evaluate performance,
fabricate evidence, hide absence, re-run upstream computation without authorisation,
or operate live is, by definition, out of bounds and belongs to a later
architecture, not to this engine.

---

## Closing Statement

This plan fixes the permanent engineering boundary of the Kalibra Evidence Engine.
The engine preserves the durable records of inspection, trust qualification, and
human review; binds them into the chain from source input to reviewer decision;
records absence honestly where a stage did not occur; keeps raw results and
calibrated qualifications separate; holds reviewer decisions as evidence rather
than feedback; and exposes inspectable, reproducible views that never claim more
than the evidence allows. It creates no findings, mutates nothing upstream,
re-runs nothing without authorisation, and never dresses an illustration as a
result.

Engineered to this boundary, the Evidence Engine is what makes Kalibra's central
promise verifiable rather than asserted: an observer who does not trust the system
can still see, from its durable and honest record, exactly what it concluded,
where, with what confidence — and where it had nothing to show.
