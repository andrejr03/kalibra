# Kalibra Evidence Real Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task by task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Repository rules in `AGENTS.md` apply:
> do not run `git add`, `git commit`, `git push`, or create branches.

**Goal:** Establish the first deterministic Evidence Engine baseline for
canonical evidence preservation, deterministic views, lineage, and explicit
absence recording.

**Architecture:** The baseline remains inside `src/evidence/` and starts from
the canonical records already emitted by Inspection, Trust Qualification, and
Human Review. It preserves those records in memory as immutable deterministic
records, links them without re-running upstream domains, records absence
explicitly, and exposes read-only evidence views.

**Tech Stack:** Existing Python 3.9 dataclasses and standard library only. No new
dependencies, storage backend, filesystem persistence, UI, analytics platform,
model behavior, or hosted service behavior.

---

## 1. Purpose

This plan defines the first deterministic Evidence Engine baseline.

The current Evidence substrate already establishes the canonical boundary:
`InboundEvidenceRecord`, `PreservedEvidenceRecord`, `EvidenceChainLink`,
`EvidenceAbsenceMarker`, `EvidenceView`, explicit evidence errors, deterministic
identifiers, and compatibility-only legacy bundle/result types. The baseline
should make the canonical path a deterministic engineering contract rather than
only a structural substrate.

The baseline does not inspect images, qualify trust, perform review, evaluate
performance, persist records outside memory, or expose a UI. It only accepts
upstream evidence records, canonicalizes preserved records, preserves
deterministic ordering and content hashes, records explicit absence, preserves
lineage, and returns deterministic read-only evidence views.

## 2. Why Evidence Fourth

Evidence must follow Inspection, Trust Qualification, and Human Review because
there is nothing principled to preserve until those domains have emitted their
records. Evidence is fourth in the chain because it is the preservation boundary,
not the producer of inspection, trust, or review decisions.

The order remains:

```text
InspectionEvidenceRecord
  -> TrustQualificationEvidenceRecord
    -> ReviewEvidenceRecord
      -> EvidenceView
        -> evaluation from preserved evidence
```

This keeps the repository's dependency order intact:

- Inspection emits raw inspection evidence.
- Trust Qualification emits trust qualification evidence bound to the raw result.
- Human Review emits review evidence when review occurs.
- Evidence preserves those records, links them, and records absence where an
  expected stage has no record.
- Evaluation remains a downstream reader of preserved evidence.

## 3. Boundary Preservation

The implementation must preserve the Evidence Engine boundary:

- consume evidence records only;
- preserve records faithfully and immutably;
- preserve deterministic content hashes;
- preserve deterministic evidence identifiers;
- preserve deterministic ordering;
- preserve lineage through immutable links;
- preserve explicit absence markers;
- expose read-only `EvidenceView` values.

The implementation must not inspect images, create raw inspection judgements,
qualify trust, perform review, evaluate performance, mutate upstream records,
fabricate evidence, train models, update models, persist records outside memory,
or expose UI behavior.

The canonical baseline path should remain separate from legacy compatibility
types. `EvidenceBundle`, `EvidenceResult`, `EvidenceArtifact`,
`EvidenceReference`, `EvidenceStatus`, `EvidenceDomain`, and `EvidenceMethod`
may remain for compatibility tests, but new deterministic baseline behavior must
be built on `InboundEvidenceRecord`, `PreservedEvidenceRecord`,
`EvidenceChainLink`, `EvidenceAbsenceMarker`, and `EvidenceView`.

## 4. Input Assumptions

The baseline starts from a fixed body of evidence records:

- `InspectionEvidenceRecord`;
- `TrustQualificationEvidenceRecord`;
- `ReviewEvidenceRecord`;
- or an already canonical `InboundEvidenceRecord`.

Accepted records must carry:

- a non-blank record identifier;
- a non-blank evidence kind;
- a valid upstream `EvidenceSourceDomain`;
- a mapping payload after canonicalization;
- linking references sufficient to bind the record into the evidence chain.

The baseline must not require raw image access, labels, ground truth,
downstream evaluation results, live reviewer sessions, or any external storage.
When an expected stage is absent, the caller supplies the expected stage and the
engine records an explicit absence instead of inventing a record.

## 5. Proposed Deterministic Evidence Baseline

The deterministic baseline should formalize this canonical sequence:

1. Accept only upstream evidence records or canonical `InboundEvidenceRecord`
   values.
2. Adapt upstream records into canonical inbound records without mutating them.
3. Canonicalize payloads using deterministic dataclass, enum, mapping, sequence,
   and path handling.
4. Freeze preserved payloads so consumers cannot mutate preserved content through
   the view.
5. Compute deterministic content hashes from canonical payloads.
6. Compute deterministic preserved record identifiers from inbound identity,
   source domain, and content hash.
7. Sort preserved records deterministically by source-domain order and record ID.
8. Build deterministic immutable chain links from inbound links and preserved
   cross-record relationships.
9. Build deterministic explicit absence markers for expected stages without
   records.
10. Return a deterministic read-only `EvidenceView`.
11. Re-run preservation for the same fixed inputs and fail if the view differs.

The baseline should continue using immutable dataclasses and stable hash-derived
identifiers. It must not normalize away record content, merge raw inspection and
trust qualification records, fabricate missing links, or produce evaluation
claims.

## 6. Canonical Evidence Preservation

Use the existing canonical Evidence objects:

- `InboundEvidenceRecord` for accepted canonical input;
- `PreservedEvidenceRecord` for immutable preserved records;
- `EvidenceChainLink` for immutable lineage links;
- `EvidenceAbsenceMarker` for explicit absence;
- `EvidenceView` for the read-only preserved output.

Preservation rules:

- `EvidenceEngine.preserve(...)` is the canonical preservation entry point.
- It accepts only `InboundEvidenceRecord`, `InspectionEvidenceRecord`,
  `TrustQualificationEvidenceRecord`, or `ReviewEvidenceRecord`.
- The same fixed evidence inputs must produce equal preserved records and equal
  views every time.
- Preserved records must carry deterministic `content_hash` values derived from
  canonical payloads.
- Preserved records must carry deterministic `preserved_record_id` values.
- Preserved records must remain immutable and expose frozen payload mappings.
- Input records and upstream objects must remain unchanged.
- Raw inspection evidence and trust qualification evidence must remain separate
  preserved records.

Malformed preservation must fail explicitly with Evidence-domain errors. It must
not repair, infer, or fabricate evidence.

## 7. Evidence View Construction

`EvidenceView` is the canonical read-only evidence view.

View rules:

- Views contain only preserved records, chain links, and absence markers.
- Views must have deterministic `view_id` values derived from preserved record
  IDs, chain link IDs, and absence IDs.
- Record order must be stable and deterministic.
- Link order must be stable and deterministic.
- Absence order must be stable and deterministic.
- Views must be read-only.
- Views must not expose evaluation reports, scores, model update payloads,
  routing commands, persistence handles, or UI payloads.

View construction must not inspect images, rerun upstream engines, qualify trust,
perform review, or evaluate evidence quality.

## 8. Lineage Preservation

The baseline must preserve this chain where each link exists:

```text
source input
  -> raw inspection result
    -> trust qualification result
      -> review case
        -> reviewer decision
          -> preserved evidence view
```

Lineage preservation means:

- inbound record links are preserved as deterministic `EvidenceChainLink`
  values;
- preserved record links are added only from existing upstream identifiers;
- inspection evidence links to trust evidence when both are present;
- trust evidence links to human review evidence when both are present;
- absent stages are represented by `EvidenceAbsenceMarker`, not fabricated links;
- preserved records keep upstream source domains visible;
- the Evidence Engine never mutates upstream `InspectionEvidenceRecord`,
  `TrustQualificationEvidenceRecord`, or `ReviewEvidenceRecord` values.

## 9. Explicit Absence Recording

Explicit absence remains part of normal evidence preservation.

Absence rules:

- Absence is represented by `EvidenceAbsenceMarker`.
- Absence markers require expected stage, reason, and upstream reference.
- Absence IDs must be deterministic for the same expected stage, reason, and
  upstream reference.
- Missing human review evidence for an accepted or rejected case is an absence,
  not weak review performance.
- Missing trust or inspection evidence is represented only when the caller marks
  that stage as expected.
- Absence markers must not contain fabricated evidence payloads.
- Absence markers must be included in `EvidenceView.absences`.

Absence is a recorded fact. It is not an error unless the absence marker itself
is malformed.

## 10. Failure Modes

The implementation must surface these failures explicitly:

- **Malformed inbound evidence.** Non-record objects, blank record IDs, blank
  evidence kinds, non-mapping payloads, invalid source domains, or malformed
  links raise Evidence-domain errors.
- **Unsupported evidence input.** `preserve(...)` receiving anything other than
  the accepted canonical or upstream evidence records raises
  `MalformedInboundEvidenceRecord`.
- **Fabricated evidence.** Payload markers indicating fabricated, inferred, or
  synthetic-claim evidence raise `FabricatedEvidenceRecord`.
- **Prototype performance evidence.** Prototype visuals or synthetic overlays
  offered as performance evidence raise `PrototypePerformanceEvidenceRejected`.
- **Missing linkage.** Preserved records that cannot carry any chain link or
  usable reference raise `EvidencePreservationFailure`, except where absence is
  explicitly recorded.
- **Malformed absence.** Blank absence identifiers, stages, reasons, or upstream
  references raise `EvidenceAbsenceFailure`.
- **Malformed view.** Blank view identifiers or non-read-only views raise
  `EvidenceViewFailure`.
- **Attempted mutation.** Preserved records, links, absences, and views remain
  frozen; mutation attempts fail through dataclass or mapping immutability.
- **Non-reproducibility.** Identical fixed evidence inputs producing different
  views raise `NonReproducibleEvidencePreservation`.
- **Boundary leak.** Any method or output path that inspects images, qualifies
  trust, performs review, evaluates, persists, exposes UI, trains, updates a
  model, or creates feedback is a boundary violation and must remain absent.

Failures are not evidence. The engine must not disguise malformed input,
fabrication, mutation, or non-reproducibility as a preserved record.

## 11. Tests

Update `tests/test_evidence_engine.py` with focused tests proving the baseline
contract:

- preserved records remain immutable;
- upstream records remain unchanged after preservation;
- identical evidence produces identical preserved records;
- shuffled evidence inputs produce deterministic preserved record ordering;
- content hashes are deterministic for equivalent canonical payloads;
- preserved record IDs are deterministic;
- chain link ordering is deterministic;
- evidence views are deterministic;
- explicit absence markers are deterministic and preserved in views;
- malformed evidence fails explicitly;
- fabricated evidence is rejected explicitly;
- prototype performance evidence is rejected explicitly;
- the Evidence Engine exposes no image inspection, trust qualification, review,
  evaluation, persistence, UI, model update, training, or feedback behavior;
- integration remains green;
- CLI remains green;
- repo-wide tests remain green.

Run the existing integration checks to prove the baseline composes:

```bash
python3 -m pytest tests/test_evidence_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

The CLI must remain green and must not gain evaluation claims, persistence
behavior, UI fields, feedback fields, model update fields, or prototype-derived
evidence claims from the Evidence baseline.

## 12. Integration Impact

No integration source change is expected for the baseline.

`src/integration/` should remain a thin consumer of canonical domain contracts:

- inspect stable input;
- qualify raw inspection output;
- create and record review evidence only when Trust requires review;
- pass emitted upstream evidence records to `EvidenceEngine.preserve(...)`;
- pass the resulting `EvidenceView` downstream to Evaluation.

The integration layer should continue to use:

- `InspectionEvidenceRecord`;
- `TrustQualificationEvidenceRecord`;
- `ReviewEvidenceRecord` when review occurs;
- `EvidenceView` as the Evidence output.

If implementation tightens deterministic ordering or identifiers, integration
tests should continue to assert canonical types and chain relations. They should
not switch back to legacy `EvidenceBundle` or `EvidenceResult` for the primary
flow.

## 13. Out of Scope

This plan does not implement:

- image inspection;
- trust qualification;
- human review;
- evaluation;
- evaluation metrics;
- reviewer quality scoring;
- model training;
- model update behavior;
- feedback loops;
- storage backend behavior;
- filesystem persistence;
- hosted services;
- live, streaming, or continuously operating behavior;
- operational alerting or scheduling;
- UI or evidence presentation surfaces;
- analytics platform behavior;
- prototype, asset, or asset pipeline behavior;
- CLI feature changes;
- legacy contract retirement.

## 14. Implementation Steps

### Task 1: Add Deterministic Preservation Tests

**Files:**

- Modify: `tests/test_evidence_engine.py`

**Goal:** Define deterministic preservation behavior before source changes.

**Context:** The current tests cover basic preservation, immutability, explicit
absence, and replay. This task should add focused assertions for stable record
ordering, stable content hashes, stable preserved IDs, and stable views.

**Proposed Approach:**

- Add a test that preserves the same fixed upstream records twice and asserts
  equal `EvidenceView`, equal `PreservedEvidenceRecord` tuples, equal
  `content_hash` values, and equal `view_id` values.
- Add a test that preserves the same records in shuffled input order and asserts
  the resulting record order is identical.
- Add a test that constructs two equivalent `InboundEvidenceRecord` values with
  differently ordered payload keys and asserts the preserved `content_hash` is
  identical.
- Add a test that link IDs and absence IDs are stable across repeated
  preservation.

**Acceptance Criteria:**

- Determinism expectations are encoded before implementation changes.
- New tests use existing canonical Evidence objects.
- No tests introduce storage, UI, evaluation, or upstream recomputation.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
```

Expected before implementation: any newly introduced stricter determinism test
may fail until Task 2 or Task 3 is complete.

### Task 2: Formalize Canonical Record Preservation

**Files:**

- Modify: `src/evidence/domain.py`
- Modify: `src/evidence/engine.py`
- Modify: `src/evidence/__init__.py` only if an existing canonical helper needs
  to be exported

**Goal:** Make preserved records a deterministic canonical projection of inbound
evidence without adding a duplicate record type.

**Context:** Use existing `InboundEvidenceRecord` and `PreservedEvidenceRecord`.
Do not introduce a storage abstraction or persistence layer.

**Proposed Approach:**

- Keep `preserved_record_from_inbound(...)` as the canonical preservation helper.
- Ensure payload canonicalization handles dataclasses, enums, mappings, tuples,
  lists, sets, and paths deterministically.
- Ensure payload freezing preserves read-only mappings and immutable sequences.
- Ensure `content_hash` is derived only from canonical payload content.
- Ensure `preserved_record_id` is derived from inbound record ID, source domain,
  and content hash.
- Ensure `EvidenceEngine.preserve(...)` rejects non-record substitutes with
  `MalformedInboundEvidenceRecord`.
- Keep upstream `InspectionEvidenceRecord`, `TrustQualificationEvidenceRecord`,
  and `ReviewEvidenceRecord` values unchanged.

**Acceptance Criteria:**

- Same canonical inbound record produces the same `PreservedEvidenceRecord`.
- Equivalent canonical payloads produce identical content hashes.
- Preserved payloads are read-only to consumers.
- Raw inspection evidence and trust qualification evidence remain separate.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
```

### Task 3: Formalize Ordering, Links, and View Construction

**Files:**

- Modify: `src/evidence/domain.py`
- Modify: `src/evidence/engine.py`
- Modify: `tests/test_evidence_engine.py`

**Goal:** Guarantee deterministic evidence ordering, chain link ordering, absence
ordering, and view identity.

**Context:** Use the existing source-domain order: Inspection, Trust, Human
Review. Keep `EvidenceView` as the canonical read-only output.

**Proposed Approach:**

- Preserve records in deterministic source-domain order, then by inbound record
  ID.
- Build inbound chain links deterministically from existing references only.
- Build cross-record links only when both linked preserved records are present.
- Deduplicate repeated links by `(from_record_id, to_record_id, relation)`.
- Sort `EvidenceChainLink` values deterministically.
- Sort `EvidenceAbsenceMarker` values deterministically.
- Derive `EvidenceView.view_id` from ordered preserved record IDs, link IDs, and
  absence IDs.

**Acceptance Criteria:**

- Shuffled inputs produce the same `EvidenceView`.
- Chain links are stable and immutable.
- View IDs are stable for fixed records, links, and absences.
- No missing link is fabricated.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
```

### Task 4: Tighten Explicit Absence and Failure Handling

**Files:**

- Modify: `src/evidence/domain.py`
- Modify: `src/evidence/engine.py`
- Modify: `tests/test_evidence_engine.py`

**Goal:** Make malformed evidence, fabricated evidence, malformed absence, and
view contract failures explicit.

**Context:** Absence is normal evidence metadata when a stage did not occur.
Malformed absence is a failure. Fabricated records are always rejected.

**Proposed Approach:**

- Add or strengthen tests for blank inbound record IDs, blank evidence kinds,
  non-mapping payloads, invalid source domains, blank link fields, blank absence
  fields, and non-read-only views.
- Preserve `FabricatedEvidenceRecord` for fabricated, inferred, or synthetic
  claim markers.
- Preserve `PrototypePerformanceEvidenceRejected` for prototype visuals or
  synthetic overlays offered as performance evidence.
- Preserve `EvidenceAbsenceFailure` for malformed absence markers.
- Preserve `EvidenceViewFailure` for malformed views.
- Ensure empty preservation without records or expected absences raises
  `MalformedInboundEvidenceRecord`.

**Acceptance Criteria:**

- Malformed evidence never becomes a preserved record.
- Fabricated evidence is rejected explicitly.
- Prototype performance evidence is rejected explicitly.
- Explicit absence remains preserved when well formed.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
```

### Task 5: Lock Boundary Absence Tests

**Files:**

- Modify: `tests/test_evidence_engine.py`

**Goal:** Prove the Evidence baseline exposes no out-of-scope behavior.

**Context:** This is a negative boundary-surface task. Do not change source
unless tests reveal a real boundary leak.

**Proposed Approach:**

- Assert `EvidenceEngine` exposes no methods or attributes for image inspection,
  trust qualification, review, routing, evaluation, persistence, UI rendering,
  model training, model update, recalibration, or feedback.
- Assert canonical Evidence outputs expose no fields for evaluation reports,
  benchmark results, routing commands, persistence handles, UI payloads, model
  update payloads, training payloads, calibration payloads, or feedback payloads.
- Keep payload-preserved upstream evidence distinct from newly emitted upstream
  behavior: the view may preserve upstream payloads, but the Evidence Engine must
  not create new inspection, trust, review, or evaluation outputs.

**Acceptance Criteria:**

- Boundary tests fail if out-of-scope behavior appears on the Evidence engine or
  canonical outputs.
- No test asserts evidence quality, benchmark performance, deployment readiness,
  storage behavior, or UI behavior.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
```

### Task 6: Run Integration and Repository Validation

**Files:**

- No planned source changes outside `src/evidence/`.
- No planned test changes outside `tests/test_evidence_engine.py` unless a
  deterministic evidence ID change requires existing assertions to follow emitted
  references.

**Goal:** Prove the baseline remains compatible with the existing canonical
integration chain and CLI.

**Verify:**

```bash
python3 -m pytest tests/test_evidence_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

**Acceptance Criteria:**

- Evidence tests pass.
- End-to-end substrate integration tests pass.
- CLI tests pass.
- Repo-wide tests pass.
- Compile check passes.
- `git status --short` shows only intended Evidence source/test changes for the
  future implementation task.
