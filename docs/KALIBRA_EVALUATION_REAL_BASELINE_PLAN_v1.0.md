# Kalibra Evaluation Real Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task by task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Repository rules in `AGENTS.md` apply:
> do not run `git add`, `git commit`, `git push`, or create branches.

**Goal:** Establish the first deterministic Evaluation Engine baseline that
constructs evidence-backed evaluation reports deterministically from preserved
evidence, with deterministic finding ordering, deterministic report identifiers,
deterministic dimension and failure-category ordering, deterministic absence
disclosures, and preserved traceability.

**Architecture:** The baseline remains inside `src/evaluation/` and starts from
the canonical `EvidenceView` already emitted by the Evidence Engine. It reads
preserved records and absence markers only, assesses each evaluation dimension
and failure category separately, records explicit absence where evidence is
missing, binds every finding back to preserved records, and returns a
deterministic read-only `EvidenceBackedEvaluationReport`. It computes no
aggregate score and makes no benchmark claim.

**Tech Stack:** Existing Python 3.9 dataclasses and standard library only
(`dataclasses`, `enum`, `hashlib`, `json`, `types.MappingProxyType`). No new
dependencies, analytics library, statistics package, storage backend, model
behavior, UI, or hosted service behavior.

---

## 1. Purpose

This plan defines the first deterministic Evaluation Engine baseline.

The current Evaluation substrate already establishes the canonical boundary:
`PreservedEvidenceInput`, `DimensionFinding`, `FailureCategoryFinding`,
`AbsenceDisclosure`, `EvidenceBackedEvaluationReport`, deterministic identifiers,
a read-only consumption guard, a reproducibility self-check, and
compatibility-only legacy report/result types. The baseline should make the
canonical preserved-evidence path a deterministic engineering contract rather
than only a structural substrate.

The baseline is a deterministic engineering baseline. It is not statistical
evaluation, benchmark reporting, model scoring, ML evaluation, calibration
research, or production analytics. It only reads preserved evidence, decides
per dimension and category whether evidence is sufficient, constructs
deterministic findings and absence disclosures, binds them to preserved records,
and returns a deterministic report.

The baseline must not inspect images, qualify trust, perform review, mutate
evidence, fabricate findings, train or update models, persist data, expose a UI,
produce an aggregate score, or make a benchmark claim.

## 2. Why Evaluation Fifth

Evaluation must follow Inspection, Trust Qualification, Human Review, and
Evidence because it can measure only what has already been recorded. There is
nothing to evaluate until upstream domains have emitted records and the Evidence
Engine has preserved them into an `EvidenceView`. Evaluation is fifth in the
chain because it is the final reader of preserved evidence, not a producer of
inspection, trust, review, or evidence records.

The order remains:

```text
raw inspection result
  -> trust qualification result
    -> review case / reviewer decision
      -> preserved evidence view
        -> evidence-backed evaluation report
```

This keeps the repository's dependency order intact:

- Inspection emits raw inspection evidence.
- Trust Qualification emits trust qualification evidence bound to the raw result.
- Human Review emits review evidence when review occurs.
- Evidence preserves those records, links them, and records explicit absence.
- Evaluation reads the preserved `EvidenceView` and reports findings against it.

Sequencing Evaluation fifth does not licence it to reconstruct, re-inspect,
re-qualify, or re-preserve anything upstream. It reads back from preserved
evidence and reports.

## 3. Boundary Preservation

The implementation must preserve the Evaluation Engine boundary. The engine
must still:

- consume `EvidenceView` only (via `PreservedEvidenceInput` or a bare
  `EvidenceView`);
- consume preserved evidence and explicit absence markers only;
- preserve traceability from every finding to preserved records;
- produce deterministic evaluation reports;
- preserve separation of the five dimensions;
- preserve separation of the six failure categories;
- preserve explicit absence disclosures distinct from weak-performance findings.

The implementation must not:

- inspect images;
- qualify trust;
- perform review;
- mutate evidence;
- fabricate findings;
- train models;
- update models;
- persist data;
- expose UI;
- produce an aggregate, overall, pass-rate, or otherwise flattering score;
- assert benchmark performance, statistical claims, or production analytics.

The canonical baseline path must remain separate from legacy compatibility
types. `EvaluationReport`, `EvaluationResult`, `EvaluationFinding`,
`EvaluationStatus`, and `EvaluationMethod` may remain for compatibility tests,
but new deterministic baseline behavior must be built on `PreservedEvidenceInput`,
`DimensionFinding`, `FailureCategoryFinding`, `AbsenceDisclosure`, and
`EvidenceBackedEvaluationReport`.

## 4. Input Assumptions

The baseline starts from a fixed body of preserved evidence:

- a canonical `EvidenceView` from `EvidenceEngine.preserve(...)`; or
- a `PreservedEvidenceInput` wrapping such a view with a fixed
  `reference_set_id`.

Accepted input must satisfy:

- the value is an `EvidenceView` (read-only) or a `PreservedEvidenceInput`
  wrapping one;
- `evidence_view.read_only` is `True`;
- the view contains at least one preserved record or one explicit absence marker;
- preserved records carry a non-blank `preserved_record_id`, a valid
  `EvidenceSourceDomain`, an `evidence_kind`, and a mapping payload;
- absence markers carry a non-blank `absence_id` and an `expected_stage`;
- a non-blank `reference_set_id` is supplied or defaulted.

The baseline must not require raw image access, labels, ground truth, numeric
benchmark targets, live reviewer sessions, downstream consumers, or external
storage. Partial evidence is expected: where a stage is absent, the view carries
an absence marker and the engine reports an absence disclosure rather than
inventing a value.

The baseline must not accept prototype visuals or synthetic overlays as
performance evidence, and must not accept fabricated, inferred, or
synthetic-claim payloads.

## 5. Proposed Deterministic Evaluation Baseline

The deterministic baseline should formalize this canonical sequence inside
`EvaluationEngine._evaluate_preserved(...)`:

1. Accept only an `EvidenceView` or a `PreservedEvidenceInput` for the canonical
   path; route legacy `EvidenceResult` to the existing compatibility method.
2. Capture a deterministic signature of the evidence view before any work.
3. Validate the view: reject fabricated payloads and prototype-as-performance
   evidence with explicit Evaluation-domain errors.
4. Compute the deterministic report-level evidence references as the sorted union
   of preserved record IDs and absence IDs.
5. Identify explicit weak-performance evidence per dimension and per category
   from preserved records (`weak_performance` payloads / weak-performance kind).
6. Construct deterministic dimension findings in fixed dimension order.
7. Construct deterministic failure-category findings in fixed category order.
8. Construct deterministic absence disclosures for every dimension and category
   that has neither a supporting finding nor weak-performance evidence.
9. Assemble a deterministic `EvidenceBackedEvaluationReport` with a deterministic
   `report_id` derived from the ordered finding IDs, disclosure IDs,
   `reference_set_id`, and `view_id`.
10. Re-capture the evidence signature and fail if the view changed
    (read-only guard).
11. Re-run construction once and fail if the second report differs
    (reproducibility self-check).

The baseline should continue using immutable frozen dataclasses and stable
hash-derived identifiers. It must not collapse dimensions, merge failure
categories, fabricate findings, convert absence into a low score, or produce any
aggregate score.

## 6. Evaluation Report Construction

`EvidenceBackedEvaluationReport` is the canonical evaluation output.

Report rules:

- The report contains only dimension findings, failure-category findings,
  absence disclosures, report-level `evidence_refs`, the fixed report kind
  (`evidence_backed_evaluation_report`), and read-only metadata.
- `report_id` must be deterministic for fixed preserved evidence and a fixed
  `reference_set_id`. It must be derived from the ordered dimension finding IDs,
  ordered failure-category finding IDs, ordered absence disclosure IDs,
  `reference_set_id`, and `view_id`.
- `evidence_refs` must be the deterministic sorted union of preserved record IDs
  and absence IDs in the view.
- Every finding's and disclosure's `evidence_refs` must be a subset of the
  report's `evidence_refs` (traceability invariant).
- Dimensions must not be duplicated; categories must not be duplicated.
- The report must remain read-only: findings, categories, disclosures,
  `evidence_refs`, and metadata are frozen, and metadata is a
  `MappingProxyType`.
- The report must expose no `score`, `aggregate_score`, `overall_score`,
  `pass_rate`, or any equivalent single flattering figure.
- Metadata must declare the deterministic evaluation mode and the
  `reference_set_id`; it must not carry benchmark, analytics, persistence, UI,
  routing, model-update, training, or feedback fields.

Report construction must not inspect images, rerun upstream engines, qualify
trust, perform review, mutate evidence, or compute statistical performance.

## 7. Dimension Findings

The five dimensions remain separate and are reported in a fixed order:
detection quality, calibration, uncertainty quality, review quality, drift
response.

Dimension finding rules:

- Findings are produced in the fixed `_DIMENSION_ORDER`; ordering is
  deterministic and independent of input record order.
- Each dimension is reported at most once; the report rejects duplicate
  dimensions.
- A dimension with explicit weak-performance evidence yields a `WEAK`
  `DimensionFinding` bound to the weak-performance record references.
- A dimension with supporting preserved records (and no weak evidence) yields a
  `SUPPORTED` `DimensionFinding` bound to those record references, with a
  limitation stating the substrate validates traceability and separation, not
  final evaluation quality.
- A dimension with neither supporting records nor weak evidence yields no
  dimension finding and instead an absence disclosure (see §9).
- Dimension-to-evidence mapping is deterministic and fixed: detection ← inspection
  records; calibration and uncertainty ← trust records; review ← human-review
  records; drift ← trust records whose drift caution is not `unavailable`.
- `finding_id` is deterministic, derived from the dimension value, evidence
  references, and status.
- Each finding must carry at least one evidence reference; an untraceable
  finding is refused with `UntraceableEvaluationFinding`.

Dimension findings must never be merged with one another and must never be
reduced to a single combined figure.

## 8. Failure Category Findings

The six failure categories are reported in a fixed order: missed defects, false
alarms, confident errors, misplaced uncertainty, mislocalized defects,
unresponsive drift.

Failure-category finding rules:

- Findings are produced in the fixed `_FAILURE_CATEGORY_ORDER`; ordering is
  deterministic and independent of input record order.
- Each category is reported at most once; the report rejects duplicate
  categories.
- A category named by explicit weak-performance evidence yields a `WEAK`
  `FailureCategoryFinding` bound to that evidence's references and reported
  distinctly from every other category.
- A category with no naming evidence yields no failure-category finding and
  instead an absence disclosure (see §9).
- `finding_id` is deterministic, derived from the category value, evidence
  references, and status.
- Each finding must carry at least one evidence reference; an untraceable
  finding is refused with `UntraceableEvaluationFinding`.

Failure categories must remain separate; no aggregate may absorb or hide a named
category.

## 9. Absence Disclosure

Explicit absence disclosure is part of normal evaluation, not an error.

Absence rules:

- An `AbsenceDisclosure` is produced for every dimension that has neither a
  dimension finding nor weak-performance evidence.
- An `AbsenceDisclosure` is produced for every failure category that has neither
  a category finding nor weak-performance evidence.
- Disclosures are produced in the fixed dimension order, then the fixed category
  order, so disclosure ordering is deterministic.
- Each disclosure carries a deterministic `disclosure_id` derived from the
  target, reason, and evidence references.
- Each disclosure binds to preserved evidence or absence references: a missing
  review dimension binds to human-review absence markers when present; otherwise
  disclosures bind to the report's fallback evidence references.
- A recorded absence must be reported as absence, never converted into a low or
  weak score.
- A present-but-weak dimension or category must be reported as a `WEAK` finding,
  never as an absence.

Missing evidence and weak performance are distinct outputs and must never be
represented as one another.

## 10. Traceability Preservation

Traceability is the load-bearing invariant of the baseline.

Traceability rules:

- The report's `evidence_refs` is the deterministic sorted union of preserved
  record IDs and absence IDs from the view.
- Every dimension finding, failure-category finding, and absence disclosure
  references only IDs that are present in the report's `evidence_refs`.
- A finding that cannot be bound to any preserved evidence reference is refused
  with `UntraceableEvaluationFinding` and must not be emitted.
- The engine must not mutate the preserved evidence view: it captures a
  deterministic signature before construction and fails with
  `InvalidEvaluationResult` if the signature changes afterward.
- The same fixed evidence view and `reference_set_id` must produce an identical
  report on re-run; divergence raises `NonReproducibleEvaluation`.

An observer holding the preserved `EvidenceView` and the report must be able to
confirm every finding's support without trusting the engine.

## 11. Failure Modes

The implementation must surface these failures explicitly and must never
disguise a failure, an absence, or a weak result as one another:

- **Malformed evaluation input.** A non-`EvidenceView`, non-`PreservedEvidenceInput`
  value, a non-read-only view, an empty view with neither records nor absences,
  or a blank `reference_set_id` raises an explicit Evaluation-domain error
  (`InvalidEvaluationResult` / `InvalidEvaluationReport`).
- **Fabricated evidence.** Payload markers indicating fabricated, inferred, or
  synthetic-claim evidence raise `FabricatedEvaluationEvidence`.
- **Prototype performance evidence.** Prototype visuals or synthetic overlays
  offered as performance evidence raise
  `PrototypePerformanceEvaluationRejected`.
- **Untraceable finding.** A finding with no preserved evidence reference raises
  `UntraceableEvaluationFinding` and is never emitted.
- **Dimension collapse.** Duplicate dimensions in a report raise
  `InvalidEvaluationReport`; no path may merge the five dimensions.
- **Category collapse.** Duplicate categories in a report raise
  `InvalidEvaluationReport`; no path may absorb a named category.
- **Missing-vs-weak conflation.** Any path that reports a recorded absence as a
  weak score, or a present weak result as an absence, is a defect to be
  prevented by the separate construction of findings and disclosures.
- **Attempted mutation.** The read-only guard raises `InvalidEvaluationResult`
  if the preserved evidence view changes during evaluation; preserved objects
  remain frozen.
- **Non-reproducibility.** Identical fixed evidence and reference set producing
  divergent reports raises `NonReproducibleEvaluation`.
- **Aggregate score.** No report exposes `score`, `aggregate_score`,
  `overall_score`, or `pass_rate`; their absence is asserted as must-not-exist.
- **Boundary leak.** Any method or output path that inspects images, qualifies
  trust, performs review, mutates evidence, persists data, exposes UI, trains,
  updates a model, recalibrates, or creates feedback is a boundary violation and
  must remain absent.

Failures are not findings. The engine must not turn a malformed input,
fabrication attempt, mutation, or non-reproducibility into a reported result.

## 12. Tests

Update `tests/test_evaluation_engine.py` with focused tests proving the baseline
contract. The following obligations must be demonstrated:

- identical preserved evidence produces identical evaluation reports;
- report identifiers are deterministic for fixed evidence and reference set;
- dimension finding ordering is deterministic and independent of input order;
- failure-category finding ordering is deterministic and independent of input
  order;
- absence disclosures are deterministic and ordered (dimensions then
  categories);
- every finding and disclosure is traceable to the report's evidence references;
- malformed evidence input fails explicitly;
- fabricated evidence fails explicitly;
- prototype-as-performance evidence fails explicitly;
- recorded absence yields an absence disclosure, not a weak score;
- present weak-performance evidence yields a weak finding, not an absence;
- the five dimensions remain separate in the report;
- the six failure categories remain separate in the report;
- no aggregate score (`score`, `aggregate_score`, `overall_score`, `pass_rate`)
  exists on the report;
- no benchmark, statistical, analytics, persistence, UI, routing, model-update,
  training, or feedback claim or field exists on the report;
- the Evaluation Engine exposes no image inspection, trust qualification,
  review, evidence-mutation, persistence, UI, model-update, training,
  recalibration, or feedback behavior;
- preserved evidence is not mutated by evaluation;
- integration remains green;
- CLI remains green;
- repo-wide tests remain green.

Run the existing integration checks to prove the baseline composes:

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

The CLI must remain green and must not gain benchmark claims, aggregate scores,
persistence behavior, UI fields, feedback fields, model-update fields, or
prototype-derived evidence claims from the Evaluation baseline.

## 13. Integration Impact

No integration source change is expected for the baseline.

`src/integration/` should remain a thin consumer of canonical domain contracts:

- inspect stable input;
- qualify raw inspection output;
- create and record review evidence only when Trust requires review;
- preserve emitted upstream evidence records into an `EvidenceView`;
- pass the resulting `EvidenceView` to `EvaluationEngine.evaluate(...)`;
- carry the emitted `EvidenceBackedEvaluationReport` and its `report_id`
  forward as canonical references.

The integration layer should continue to use:

- `EvidenceView` as the Evaluation input;
- `EvidenceBackedEvaluationReport` as the Evaluation output;
- `report.report_id` as the canonical evaluation reference
  (`evaluation_report_id`).

If implementation tightens deterministic ordering or identifiers, integration
and CLI tests should continue to assert canonical types and the deterministic
`evaluation_report_id`. They must not switch back to the legacy
`EvaluationReport`/`EvaluationResult` path for the primary flow, and the CLI
payload must continue to expose `evaluation_report_id` without adding score,
benchmark, persistence, UI, or feedback fields.

## 14. Out of Scope

This plan does not implement:

- image inspection;
- trust qualification;
- human review;
- evidence preservation or mutation;
- statistical evaluation;
- benchmark reporting or benchmark targets;
- model scoring or aggregate scoring;
- ML evaluation;
- calibration research;
- production analytics;
- model training, retraining, recalibration, or model update behavior;
- feedback loops from findings or reviewer decisions into model updates;
- storage backend behavior or filesystem persistence;
- hosted services;
- live, streaming, or continuously operating behavior;
- operational alerting or scheduling;
- UI or evaluation presentation surfaces;
- prototype, asset, or asset pipeline behavior;
- CLI feature changes;
- legacy contract retirement.

## 15. Implementation Steps

### Task 1: Add Deterministic Evaluation Tests

**Files:**

- Modify: `tests/test_evaluation_engine.py`

**Goal:** Define deterministic evaluation behavior before source changes.

**Context:** The current tests cover read-only consumption, traceability,
dimension/category separation, missing-vs-weak distinction, no-aggregate, and
single-pass reproducibility. This task adds focused assertions for deterministic
report identity, deterministic finding ordering, deterministic category ordering,
and deterministic absence ordering.

**Proposed Approach:**

- Add a test that evaluates the same fixed `EvidenceView` twice and asserts equal
  `EvidenceBackedEvaluationReport` values and equal `report_id` values.
- Add a test that builds two evidence views whose preserved records are supplied
  in different input order but are otherwise equivalent, and asserts the emitted
  dimension findings, failure-category findings, and absence disclosures appear
  in identical order with identical IDs.
- Add a test that asserts dimension findings follow the fixed dimension order
  (detection, calibration, uncertainty, review, drift) and category findings
  follow the fixed category order.
- Add a test that asserts absence disclosures are ordered dimensions-first then
  categories, deterministically.

**Acceptance Criteria:**

- Determinism expectations are encoded before implementation changes.
- New tests use existing canonical Evaluation and Evidence objects only.
- No tests introduce storage, UI, statistics, aggregate scores, or benchmark
  assertions.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
```

Expected before implementation: any newly introduced stricter determinism test
may fail until Task 2 or Task 3 is complete.

### Task 2: Formalize Deterministic Report Construction

**Files:**

- Modify: `src/evaluation/domain.py`
- Modify: `src/evaluation/engine.py`
- Modify: `src/evaluation/__init__.py` only if an existing canonical helper needs
  to be exported

**Goal:** Make `EvidenceBackedEvaluationReport` a deterministic canonical
projection of preserved evidence without adding a duplicate report type.

**Context:** Use existing `PreservedEvidenceInput`, `DimensionFinding`,
`FailureCategoryFinding`, `AbsenceDisclosure`, and `EvidenceBackedEvaluationReport`.
Do not introduce statistics, scoring, or persistence.

**Proposed Approach:**

- Keep `stable_report_id(...)`, `dimension_finding(...)`,
  `failure_category_finding(...)`, and `absence_disclosure(...)` as the canonical
  deterministic constructors.
- Ensure `report_id` derives only from ordered dimension finding IDs, ordered
  failure-category finding IDs, ordered absence disclosure IDs,
  `reference_set_id`, and `view_id`.
- Ensure `evidence_refs` is the deterministic sorted union of preserved record
  IDs and absence IDs.
- Ensure report metadata declares the deterministic evaluation mode and
  `reference_set_id` only.
- Ensure `EvaluationEngine.evaluate(...)` routes `EvidenceView` and
  `PreservedEvidenceInput` to the canonical path and legacy `EvidenceResult` to
  the compatibility path.

**Acceptance Criteria:**

- Same fixed evidence and reference set produce the same `report_id`.
- Report `evidence_refs` is deterministic and sorted.
- The report exposes no aggregate score field.
- Legacy compatibility path remains intact.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
```

### Task 3: Formalize Deterministic Dimension, Category, and Absence Ordering

**Files:**

- Modify: `src/evaluation/engine.py`
- Modify: `tests/test_evaluation_engine.py`

**Goal:** Guarantee deterministic dimension finding ordering, failure-category
finding ordering, and absence disclosure ordering, all independent of input
record order.

**Context:** Use the existing fixed `_DIMENSION_ORDER` and
`_FAILURE_CATEGORY_ORDER`. Keep `EvidenceBackedEvaluationReport` as the canonical
read-only output.

**Proposed Approach:**

- Build dimension findings strictly in `_DIMENSION_ORDER`, choosing WEAK when
  weak-performance evidence is present, SUPPORTED when supporting records are
  present, and otherwise deferring to an absence disclosure.
- Build failure-category findings strictly in `_FAILURE_CATEGORY_ORDER`, WEAK
  only where weak-performance evidence names the category.
- Build absence disclosures strictly in dimension order then category order for
  every dimension/category without a finding or weak evidence.
- Ensure dimension-to-evidence and category-to-evidence reference selection is
  deterministic and independent of record input order.

**Acceptance Criteria:**

- Shuffled-input equivalent views produce identical finding and disclosure order
  and identical IDs.
- Dimensions and categories each appear at most once.
- No missing dimension or category is fabricated into a finding.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
```

### Task 4: Tighten Traceability, Read-Only, and Reproducibility Guards

**Files:**

- Modify: `src/evaluation/engine.py`
- Modify: `src/evaluation/domain.py`
- Modify: `tests/test_evaluation_engine.py`

**Goal:** Make traceability violations, evidence mutation, fabrication,
prototype-as-performance, and non-reproducibility explicit failures.

**Context:** Traceability and reproducibility are the load-bearing invariants.
Absence is normal; fabrication and mutation are never.

**Proposed Approach:**

- Ensure every finding's and disclosure's `evidence_refs` is a subset of the
  report's `evidence_refs`; otherwise raise `UntraceableEvaluationFinding`.
- Preserve `FabricatedEvaluationEvidence` for fabricated, inferred, or
  synthetic-claim markers.
- Preserve `PrototypePerformanceEvaluationRejected` for prototype visuals or
  synthetic overlays offered as performance evidence.
- Preserve the pre/post evidence-signature guard and raise
  `InvalidEvaluationResult` on any mutation of the preserved view.
- Preserve the double-construction self-check and raise
  `NonReproducibleEvaluation` on divergence.
- Add or strengthen tests for each guard.

**Acceptance Criteria:**

- Untraceable findings never enter a report.
- Fabricated and prototype-performance evidence are rejected explicitly.
- Preserved evidence is unchanged after evaluation.
- Identical fixed evidence yields identical reports.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
```

### Task 5: Lock Boundary and No-Score Tests

**Files:**

- Modify: `tests/test_evaluation_engine.py`

**Goal:** Prove the Evaluation baseline exposes no out-of-scope behavior and no
aggregate score.

**Context:** This is a negative boundary-surface task. Do not change source
unless tests reveal a real boundary leak.

**Proposed Approach:**

- Assert `EvaluationEngine` exposes no methods or attributes for image
  inspection, trust qualification, review, routing, evidence mutation,
  persistence, UI rendering, model training, model update, recalibration, or
  feedback.
- Assert `EvidenceBackedEvaluationReport` exposes no `score`, `aggregate_score`,
  `overall_score`, or `pass_rate` attribute, and no benchmark, analytics,
  persistence, UI, routing, model-update, training, or feedback field.
- Assert report metadata carries only the deterministic evaluation mode and
  `reference_set_id`.

**Acceptance Criteria:**

- Boundary tests fail if out-of-scope behavior appears on the engine or report.
- No test asserts benchmark performance, statistical quality, deployment
  readiness, storage behavior, or UI behavior.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
```

### Task 6: Run Integration and Repository Validation

**Files:**

- No planned source changes outside `src/evaluation/`.
- No planned test changes outside `tests/test_evaluation_engine.py` unless a
  deterministic evaluation ID change requires existing integration or CLI
  assertions to follow emitted references.

**Goal:** Prove the baseline remains compatible with the existing canonical
integration chain and CLI.

**Verify:**

```bash
python3 -m pytest tests/test_evaluation_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

**Acceptance Criteria:**

- Evaluation tests pass.
- End-to-end substrate integration tests pass.
- CLI tests pass.
- Repo-wide tests pass.
- Compile check passes.
- `git status --short` shows only intended Evaluation source/test changes for the
  future implementation task.
