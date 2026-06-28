# Kalibra Human Review Real Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task by task. This plan is
> intentionally limited to the Human Review substrate. Repository rules in
> `AGENTS.md` apply: do not run `git add`, `git commit`, `git push`, or create
> branches.

**Goal:** Replace the current structural Human Review substrate behavior with a
deterministic engineering baseline for review package preparation, reviewer
decision validation, lineage preservation, and review evidence emission.

**Architecture:** The baseline remains inside `src/review/` and starts from the
canonical `ReviewQualifiedCase`. It prepares an immutable review package from
that case, records one externally supplied reviewer decision for that case, and
emits deterministic review evidence without inspecting images, recalibrating
confidence, mutating upstream records, or feeding decisions back into the system.

**Tech Stack:** Existing Python 3.9 dataclasses and standard library only. No new
dependencies, ML, reviewer modelling, decision-feedback learning, persistence,
UI, production routing, operational tooling, prototype integration, or asset
pipeline behavior.

---

## 1. Purpose

This plan defines the first deterministic Human Review baseline.

The current Review substrate already establishes the canonical boundary:
`ReviewQualifiedCase`, `ReviewHandoff`, `ReviewerDecision`,
`ReviewEvidenceRecord`, explicit errors, deterministic evidence IDs, and
compatibility-only legacy request/result types. The next implementation should
make the canonical path a deterministic engineering baseline rather than only a
structural placeholder.

The baseline does not model human judgement. It does not decide what a reviewer
should conclude, rate reviewer quality, learn from reviewer decisions, or operate
review workflow software. It only prepares the case package, validates a supplied
decision, binds that decision to exactly one case, preserves upstream lineage,
and emits evidence.

## 2. Why Human Review Third

Human Review must follow Trust Qualification because there is no principled
review path until Trust has qualified the inspection result. Review is a
qualified outcome from the Trust boundary, not an Inspection failure and not a
decision manufactured inside the Review domain.

The order remains:

```text
RawInspectionResult
  -> TrustQualificationResult
    -> ReviewQualifiedCase
      -> review package
        -> reviewer decision evidence
```

This keeps the repository's dependency order intact:

- Inspection examines one stable input and emits one raw result.
- Trust Qualification qualifies that raw result and determines whether review is
  required.
- Human Review accepts only review-qualified or drifted cases and records the
  supplied reviewer decision as evidence.
- Evidence and Evaluation remain downstream consumers of emitted records.

## 3. Boundary Preservation

The implementation must preserve the Human Review Engine boundary:

- consume `ReviewQualifiedCase` for package preparation and decision recording;
- never inspect images, artifact URIs, file bytes, or prototype assets;
- never reconstruct inspection judgements, localizations, or raw measures;
- never calibrate confidence or change qualified outcomes;
- never modify `RawInspectionResult`;
- never modify `TrustQualificationResult`;
- prepare a deterministic review package;
- record one supplied reviewer decision for one review case;
- emit `ReviewEvidenceRecord` as additive evidence.

The implementation must not evaluate performance, train models, update models,
change trust qualification, perform operational routing, persist data, expose UI,
own evidence presentation, or create any feedback loop from reviewer decisions.

The canonical baseline path should remain separate from legacy compatibility
types. `HumanReviewRequest`, `HumanReviewResult`, `HumanReviewMethod`, and
`TrustQualifiedResult` may remain for compatibility tests, but new deterministic
baseline behavior must be built on `ReviewQualifiedCase`,
`ReviewerDecision`, and `HumanReviewEngineOutput`.

## 4. Input Assumptions

The baseline starts from a valid `ReviewQualifiedCase` carrying:

- `review_case_id`;
- `input_id`;
- `inspection_result_id`;
- `qualification_result_id`;
- the original `RawInspectionResult`;
- the original `TrustQualificationResult`;
- the preserved deferral reason;
- the optional localization reference from the raw inspection result.

The case must satisfy the existing chain constraints:

- raw inspection result ID matches `inspection_result_id`;
- raw inspection result input ID matches `input_id`;
- trust qualification result ID matches `qualification_result_id`;
- trust qualification inspection result ID matches the raw result;
- trust qualification input ID matches the review case;
- trust outcome is `QualifiedOutcome.REVIEW` or drift caution is `DRIFTED`.

The baseline must not require labels, ground truth, raw image access, evidence
storage, live reviewer sessions, reviewer skill information, or evaluation
results.

## 5. Proposed Deterministic Review Baseline

The deterministic baseline should formalize this canonical sequence:

1. Accept a `ReviewQualifiedCase`.
2. Validate that the case is complete, traceable, review-qualified or drifted,
   and unchanged from upstream.
3. Prepare a review package as a deterministic projection of the case.
4. Accept a supplied `ReviewerDecision`.
5. Validate that the decision is well formed and references exactly the case
   being recorded.
6. Emit `ReviewEvidenceRecord` with the package, decision, and upstream chain.
7. Re-run the fixed package/decision recording path internally and fail if the
   emitted record differs.

The baseline should continue using immutable dataclasses and stable hash-derived
record IDs. It should not choose a reviewer decision, infer a reviewer decision,
or assign any correctness to the reviewer decision. The reviewer decision is an
input to be recorded, not an automated output to be generated.

## 6. Review Package Definition

Use the existing `ReviewHandoff` as the review package unless implementation
findings prove a separate type is required. Adding a duplicate package type would
increase contract surface without changing the baseline responsibility.

A review package is the immutable, deterministic handoff prepared from one
`ReviewQualifiedCase`. It must contain:

- `review_case_id`;
- `source_input_ref`;
- `localization_ref`;
- the original `RawInspectionResult`;
- the original `TrustQualificationResult`;
- the unchanged deferral reason.

Package rules:

- The package is produced only from `ReviewQualifiedCase`.
- The same fixed case produces an equal package every time.
- The package carries references and upstream objects; it does not copy them into
  new decisions or mutate them.
- The package does not contain a reviewer decision.
- Malformed packages fail with explicit Human Review errors, not with review
  outcomes.
- Package preparation does not depend on the Evidence Engine at runtime.

The baseline may add a new method name such as `prepare_review_package` only if it
keeps `prepare_handoff` as a compatibility alias. No caller should need to
understand two different package contracts.

## 7. Reviewer Decision Definition

Use the existing `ReviewerDecision` as the canonical recorded reviewer decision.

A reviewer decision must contain:

- `decision_id`;
- `review_case_id`;
- `reviewer_ref`;
- `decision`;
- `rationale`.

Allowed `decision` values remain:

- `ReviewerDecisionValue.ACCEPT`;
- `ReviewerDecisionValue.REJECT`;
- `ReviewerDecisionValue.INCONCLUSIVE`.

Decision rules:

- The decision is externally supplied and then validated.
- The decision must bind to exactly one `review_case_id`.
- The decision must reference the same case being recorded.
- All identifier and rationale fields must be non-blank.
- The decision value must be a `ReviewerDecisionValue`.
- A malformed decision raises `MalformedReviewerDecision`.
- A decision for a different case raises `InvalidHumanReviewResult`.
- A decision is recorded as evidence only and never becomes training,
  calibration, drift, routing, or evaluation input inside this domain.

## 8. Lineage Preservation

The baseline must preserve this complete chain:

```text
source input
  -> raw inspection result
    -> trust qualification result
      -> review case
        -> review package
          -> reviewer decision
            -> review evidence record
```

`ReviewUpstreamChain` should continue to carry the source input ID, inspection
result ID, qualification result ID, and review case ID. The review package and
reviewer decision should be embedded in `ReviewEvidenceRecord`, so the evidence
record can be inspected without reconstructing upstream state.

Lineage preservation means:

- upstream IDs match the upstream objects;
- raw and trust objects remain equal to their pre-review values;
- review evidence links to the package, decision, and upstream chain;
- no evidence record is emitted if the package, decision, or chain is malformed;
- reviewer decisions never overwrite raw inspection or trust qualification
  outputs.

## 9. Failure Modes

The implementation must surface these failures explicitly:

- **Non-review case.** A case not qualified as review and not drifted raises
  `NonReviewQualifiedCase`.
- **Incomplete upstream chain.** Missing or mismatched source, raw inspection, or
  trust qualification references raise `IncompleteReviewChain`.
- **Non-case package input.** Package preparation or decision recording that
  receives anything other than `ReviewQualifiedCase` raises
  `IncompleteReviewChain`.
- **Malformed review package.** Blank package identifiers, blank source input
  references, missing deferral reason, or mismatched upstream objects raise
  `InvalidHumanReviewResult`.
- **Malformed reviewer decision.** Blank decision identifiers, blank case IDs,
  blank reviewer refs, blank rationale, or non-enum decisions raise
  `MalformedReviewerDecision`.
- **Mismatched decision binding.** A decision whose `review_case_id` differs from
  the case being recorded raises `InvalidHumanReviewResult`.
- **Upstream mutation.** Any change to raw inspection or trust qualification
  objects during review raises `UpstreamReviewMutationError`.
- **Evidence emission failure.** Invalid, missing, or mismatched evidence records
  raise `ReviewEvidenceEmissionFailure`.
- **Non-reproducibility.** Identical fixed case and decision inputs producing
  different review outputs raises `NonReproducibleHumanReview`.
- **Feedback attempt.** Any method or output path that trains, updates,
  recalibrates, routes operationally, or evaluates from reviewer decisions is a
  boundary violation and must remain absent.

Failures are not review outcomes. The engine must not disguise malformed input,
evidence failure, mutation, or non-reproducibility as an inconclusive reviewer
decision.

## 10. Tests

Update `tests/test_human_review_engine.py` with focused tests proving the
baseline contract:

- review package preparation is deterministic for the same fixed
  `ReviewQualifiedCase`;
- package preparation accepts `ReviewQualifiedCase` and rejects non-case objects;
- malformed review packages fail explicitly;
- reviewer decisions bind to exactly one review case;
- malformed reviewer decisions fail explicitly, including non-enum decision
  values;
- the upstream raw inspection result remains unchanged;
- the upstream trust qualification result remains unchanged;
- review evidence preserves the full chain and embeds the review package;
- reviewer decisions become evidence only;
- no feedback loop, model update, training, recalibration, persistence, UI,
  evidence presentation, or evaluation behavior exists on the Review engine;
- fixed case plus fixed decision produces identical review evidence;
- evidence emission failures are explicit.

Run the existing integration checks to prove the baseline composes:

```bash
python3 -m pytest tests/test_human_review_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

The CLI must remain green and must not gain reviewer quality scores,
performance claims, persistence behavior, UI fields, feedback fields, or
prototype-derived evidence.

## 11. Integration Impact

No integration source change is expected for the baseline.

`src/integration/` should remain a thin consumer of canonical domain contracts:

- inspect stable input;
- qualify raw inspection output;
- create or receive the review-qualified case;
- record the deterministic reviewer decision only when Trust requires review;
- preserve emitted records;
- evaluate from preserved evidence.

The integration chain may continue using its deterministic reviewer-decision
fixture for substrate composition. That fixture is not reviewer intelligence and
must not move the Review domain into decision generation. The Review domain owns
validation, binding, and evidence recording; the integration layer owns only
composition of already defined substrate calls.

If implementation introduces a compatibility alias such as
`prepare_review_package`, integration tests should continue to assert canonical
types and should not switch back to legacy `HumanReviewRequest` or
`HumanReviewResult`.

## 12. Out of Scope

This plan does not implement:

- human decision modelling;
- reviewer intelligence;
- reviewer quality scoring;
- decision-feedback learning;
- reward-driven learning from reviewer outcomes;
- training, retraining, or model updates;
- trust recalibration;
- drift detection;
- inspection or image analysis;
- operational routing;
- review queues or workflow software;
- persistence;
- UI;
- hosted services;
- monitoring or alerting;
- Evidence Engine presentation behavior;
- Evaluation Engine review-quality metrics;
- dataset changes;
- asset, prototype, or asset pipeline behavior;
- CLI feature changes;
- legacy contract retirement.

## 13. Implementation Steps

### Task 1: Add Baseline Package Tests

**Files:**

- Modify: `tests/test_human_review_engine.py`

**Goal:** Define deterministic review package behavior before source changes.

**Approach:**

- Add a test that prepares a package from the same `ReviewQualifiedCase` twice
  and asserts equality.
- Add a test that `prepare_handoff` or `prepare_review_package` rejects a
  non-`ReviewQualifiedCase` object with `IncompleteReviewChain`.
- Add tests that malformed `ReviewHandoff` instances fail with
  `InvalidHumanReviewResult` for blank IDs, blank source input references,
  missing deferral reason, and mismatched upstream objects.

**Acceptance Criteria:**

- The package is a deterministic projection of the case.
- Package preparation does not accept raw inspection or trust qualification
  objects as substitutes for `ReviewQualifiedCase`.
- Malformed packages fail explicitly.

**Verify:**

```bash
python3 -m pytest tests/test_human_review_engine.py -q
```

Expected before implementation: any newly introduced stricter validation test may
fail until Task 2 is complete.

### Task 2: Formalize Review Package Preparation

**Files:**

- Modify: `src/review/domain.py`
- Modify: `src/review/engine.py`
- Modify: `src/review/__init__.py` only if a new public alias is added

**Goal:** Make the review package an explicit deterministic baseline contract
without adding duplicate domain responsibility.

**Approach:**

- Continue using `ReviewHandoff` as the package object.
- Keep package fields limited to case ID, source input reference, localization
  reference, raw inspection result, trust qualification result, and deferral
  reason.
- Tighten `ReviewHandoff.__post_init__` only where tests show missing explicit
  validation.
- If adding `prepare_review_package`, implement it as the canonical method and
  keep `prepare_handoff` as a compatibility alias to the same logic.
- Keep package preparation independent from Evidence, Evaluation, CLI,
  persistence, UI, images, and assets.

**Acceptance Criteria:**

- Fixed valid case produces fixed package.
- Invalid package state raises Human Review errors.
- Raw inspection and trust qualification records are not mutated.
- Legacy request/result compatibility behavior is not expanded.

### Task 3: Tighten Reviewer Decision Validation

**Files:**

- Modify: `src/review/domain.py`
- Modify: `tests/test_human_review_engine.py`

**Goal:** Validate reviewer decisions as records for one case, not as inferred
or automated decisions.

**Approach:**

- Keep `ReviewerDecision` as the canonical decision record.
- Validate that `decision` is a `ReviewerDecisionValue`.
- Preserve existing non-blank validation for `decision_id`, `review_case_id`,
  `reviewer_ref`, and `rationale`.
- Keep `record_decision` responsible for rejecting a decision whose
  `review_case_id` differs from the `ReviewQualifiedCase`.

**Acceptance Criteria:**

- Blank decision fields raise `MalformedReviewerDecision`.
- Non-enum decision values raise `MalformedReviewerDecision`.
- Decision/case mismatch raises `InvalidHumanReviewResult`.
- The Review engine does not choose or alter the reviewer decision value.

### Task 4: Preserve Evidence and Lineage Deterministically

**Files:**

- Modify: `src/review/engine.py`
- Modify: `tests/test_human_review_engine.py`

**Goal:** Ensure review evidence is additive, deterministic, and fully traceable.

**Approach:**

- Keep `HumanReviewEvidenceEmitter.emit` producing `ReviewEvidenceRecord`.
- Keep the stable record ID derived from deterministic identifiers, not runtime
  state.
- Assert emitted evidence preserves the exact review package and reviewer
  decision.
- Preserve `ReviewUpstreamChain` IDs from the package and upstream objects.
- Keep the double-run reproducibility guard in `record_decision`.
- Keep upstream mutation guards around raw inspection and trust qualification.

**Acceptance Criteria:**

- Review evidence contains package, decision, and upstream chain.
- Same fixed package and decision produce identical output.
- Evidence emission failures raise `ReviewEvidenceEmissionFailure`.
- Reviewer decisions terminate as evidence and do not feed back into any model,
  calibration, trust, routing, persistence, UI, or evaluation path.

### Task 5: Verify Boundary Absence Tests

**Files:**

- Modify: `tests/test_human_review_engine.py`

**Goal:** Lock the absence of out-of-scope behavior.

**Approach:**

- Keep and extend negative surface tests using `hasattr`.
- Assert the Review engine exposes no image inspection, reconstruction,
  calibration, training, model update, feedback, persistence, UI, evidence
  presentation, or evaluation methods.
- Assert `HumanReviewEngineOutput` and `ReviewEvidenceRecord` do not expose
  scores, reviewer quality metrics, model update payloads, or persistence
  handles.

**Acceptance Criteria:**

- Boundary tests fail if out-of-scope behavior appears on the Review engine or
  canonical outputs.
- No test asserts review quality, reviewer correctness, benchmark performance, or
  production readiness.

### Task 6: Run Integration and Repository Validation

**Files:**

- No planned source changes outside `src/review/`.
- No planned test changes outside `tests/test_human_review_engine.py` unless a
  deterministic ID change requires existing integration assertions to follow
  emitted references.

**Goal:** Prove the baseline remains compatible with the existing canonical
integration chain and CLI.

**Verify:**

```bash
python3 -m pytest tests/test_human_review_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

**Acceptance Criteria:**

- Human Review tests pass.
- End-to-end substrate integration tests pass.
- CLI tests pass.
- Repo-wide tests pass.
- Compile check passes.
- `git status --short` shows only intended Review source/test changes for the
  future implementation task.
