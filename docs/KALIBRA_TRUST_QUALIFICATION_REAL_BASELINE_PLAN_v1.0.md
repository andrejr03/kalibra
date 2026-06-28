# Kalibra Trust Qualification Real Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task by task. This plan is
> intentionally limited to the Trust Qualification substrate. Repository rules in
> `AGENTS.md` apply: do not run `git add`, `git commit`, `git push`, or create
> branches.

**Goal:** Replace the default placeholder trust qualification behavior with a
deterministic rule-based Trust Qualification baseline that preserves all current
domain contracts.

**Architecture:** The baseline remains inside `src/trust/` and consumes only
`RawInspectionResult` plus an optional `DriftReference`. It produces the existing
canonical `TrustQualificationEngineOutput`, preserving raw inspection output
unchanged and emitting trust evidence through the existing evidence emitter.

**Tech Stack:** Existing Python 3.9 dataclasses and standard library only. No new
dependencies, ML, fitting, benchmark-derived thresholds, probabilistic modelling,
database persistence, UI, or prototype integration.

---

## 1. Purpose

This plan defines the first deterministic Trust Qualification baseline.

The current Trust substrate already has canonical contracts, deterministic
engine structure, evidence emission, drift caution, and compatibility-only
legacy support. The next implementation should replace the current default
placeholder calibration label and placeholder framing with a named deterministic
engineering baseline.

This baseline is not calibration science, uncertainty research, probabilistic
modelling, ML, or production trust qualification. It is a reproducible rule that
maps the raw inspection measure into the existing calibrated-confidence contract
so the Trust boundary can be exercised honestly and deterministically.

## 2. Why Trust Qualification Second

Trust Qualification must follow Inspection because it qualifies the raw
inspection result and must not inspect images or reconstruct Inspection outputs.
The Inspection substrate now emits canonical `RawInspectionResult` objects from
the default placeholder examiner and can also emit the same contract from the
opt-in deterministic local image baseline examiner.

The Trust baseline should therefore operate only on `RawInspectionResult`:

- `raw_anomaly_measure`
- `raw_measure_kind`
- `judgement`
- `inspection_result_id`
- `input_id`

This keeps the dependency order fixed: Inspection produces raw judgement and raw
measure; Trust Qualification converts that single source into calibrated
confidence, qualified outcome, uncertainty characterization, drift caution, and
trust evidence.

## 3. Boundary Preservation

The implementation must preserve the Trust Qualification Engine boundary:

- consume `RawInspectionResult` as the primary canonical input;
- optionally consume `DriftReference`;
- never inspect images or artifact URIs;
- never reconstruct inspection results;
- never mutate `RawInspectionResult`;
- preserve raw anomaly measure and calibrated confidence as distinct values;
- produce exactly one `QualifiedOutcome`;
- treat `REVIEW` and `ABSTAIN` as engineered outcomes, not failures;
- let drift increase caution without overwriting raw inspection output;
- emit `TrustQualificationEvidenceRecord`.

The implementation must not perform Human Review, operational routing, evidence
presentation, evaluation, training, model updates, persistence, UI behavior,
prototype behavior, or feedback loops.

## 4. Input Assumptions

The baseline consumes the current canonical Trust input:

- `RawInspectionResult` from `src.inspection`;
- `raw_measure_kind == "raw_anomaly_measure"`;
- a finite `raw_anomaly_measure`;
- a stable `inspection_result_id`;
- a stable `input_id`;
- a raw `judgement` from `InspectionJudgement`.

The baseline must tolerate either currently supported raw measure scale:

- `placeholder_hash_raw_0_100`;
- `local_contrast_raw_0_100`.

The baseline must not branch on the examiner implementation. The Trust domain
cares that the measure is raw and finite, not whether Inspection produced it via
the default placeholder examiner or the opt-in local image baseline examiner.

The optional `DriftReference` is authoritative only for deterministic caution:

- absent or unavailable drift reference records explicit absence;
- available drift reference requires a finite score in `[0, 1]`;
- drift score affects caution and outcome only;
- drift score must not change the raw result or the calibrated confidence value.

## 5. Proposed Deterministic Calibration Baseline

Add a named default calibrator under `src/trust/engine.py`:

```python
@dataclass(frozen=True)
class DeterministicTrustBaselineCalibrator:
    calibrator_id: str = "trust-deterministic-baseline-v1"
    decision_boundary: float = 50.0
    raw_measure_span: float = 50.0

    def calibrate(
        self, raw_result: RawInspectionResult
    ) -> CalibratedTrustConfidence:
        raw_measure = raw_result.raw_anomaly_measure
        if not isfinite(raw_measure):
            raise CalibrationFailure("raw anomaly measure must be finite")
        normalized_margin = min(
            1.0,
            max(0.0, abs(raw_measure - self.decision_boundary) / self.raw_measure_span),
        )
        return CalibratedTrustConfidence(
            value=round(normalized_margin, 6),
            calibration_kind=DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND,
        )
```

This formula is deliberately simple:

- raw measure near the raw decision boundary has low confidence;
- raw measure far from the raw decision boundary has higher confidence;
- values outside the expected raw span are clamped into `[0, 1]`;
- no data fitting, learned parameter, benchmark result, or probabilistic claim is
  involved.

Keep `DeterministicPlaceholderCalibrator` available only as compatibility
surface if needed by existing callers. New default Trust Qualification work
should use `DeterministicTrustBaselineCalibrator`.

## 6. Calibrated Confidence Definition

The baseline confidence value is:

```text
round(clamp(abs(raw_anomaly_measure - 50.0) / 50.0, 0.0, 1.0), 6)
```

The output remains `CalibratedTrustConfidence` because that is the canonical
Trust contract. The value must be marked with a new baseline calibration kind:

```python
DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND = (
    "deterministic_rule_based_trust_baseline_v1"
)
```

Implementation should keep the existing placeholder calibration kind as
compatibility-only if retaining it avoids unnecessary breakage:

```python
PLACEHOLDER_CALIBRATION_KIND = "deterministic_placeholder_calibration"
VALID_CALIBRATION_KINDS = frozenset(
    {
        DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND,
        PLACEHOLDER_CALIBRATION_KIND,
    }
)
```

New default output must use
`DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND`. The raw inspection measure must
remain available only on the preserved `RawInspectionResult`; it must not be
copied into `TrustQualificationResult` as confidence or a score.

## 7. Qualified Outcome Strategy

Use deterministic thresholds as engineering constants, not benchmark-derived
targets:

```python
ABSTAIN_CONFIDENCE_THRESHOLD = 0.15
REVIEW_CONFIDENCE_THRESHOLD = 0.40
DRIFT_REVIEW_THRESHOLD = 0.60
```

Outcome rules:

1. If calibrated confidence is below `0.15`, produce `QualifiedOutcome.ABSTAIN`.
2. Else if calibrated confidence is below `0.40`, produce
   `QualifiedOutcome.REVIEW`.
3. Else derive the base outcome from the raw judgement:
   - `InspectionJudgement.OK` -> `QualifiedOutcome.ACCEPT`;
   - `InspectionJudgement.DEFECT` -> `QualifiedOutcome.REJECT`.
4. If drift is `DRIFTED` and the base outcome is `ACCEPT` or `REJECT`, downgrade
   to `QualifiedOutcome.REVIEW`.

`REVIEW` and `ABSTAIN` are normal qualified outcomes. They must never be used to
hide malformed input, calibration failure, evidence failure, or
non-reproducibility.

## 8. Drift Handling

Keep drift handling deterministic and non-destructive:

- `drift_reference is None` -> `DriftCautionStatus.UNAVAILABLE`;
- `drift_reference.available is False` -> `DriftCautionStatus.UNAVAILABLE`;
- available reference with `drift_score < 0.60` ->
  `DriftCautionStatus.IN_DISTRIBUTION`;
- available reference with `drift_score >= 0.60` ->
  `DriftCautionStatus.DRIFTED` and `caution_applied=True`.

Drift caution must:

- preserve `drift_reference_id`;
- preserve `drift_score`;
- disclose absence when unavailable;
- affect qualification only by increasing caution;
- not change `RawInspectionResult`;
- not change `CalibratedTrustConfidence.value`;
- not create a feedback loop or model update.

## 9. Uncertainty Characterization

Uncertainty status should remain explicit and deterministic:

```python
if confidence.value >= 0.75:
    status = UncertaintyStatus.LOW
elif confidence.value >= 0.15:
    status = UncertaintyStatus.ELEVATED
else:
    status = UncertaintyStatus.HIGH
```

Use baseline-specific rationales that do not mention placeholder behavior:

- `LOW`: "Deterministic trust baseline confidence is far from the raw decision boundary."
- `ELEVATED`: "Deterministic trust baseline confidence is near the raw decision boundary."
- `HIGH`: "Deterministic trust baseline confidence is too close to the raw decision boundary."

These rationales explain the rule boundary only. They must not claim statistical
calibration quality, defect-detection quality, benchmark performance, or
production reliability.

## 10. Failure Modes

Implementation must preserve existing explicit failures:

- malformed or non-`RawInspectionResult` canonical input raises
  `MalformedRawInspectionResult`;
- raw result missing `input_id`, `inspection_result_id`, or
  `raw_measure_kind == "raw_anomaly_measure"` raises
  `MalformedRawInspectionResult`;
- non-finite raw anomaly measure raises `MalformedRawInspectionResult` or
  `CalibrationFailure` at the owning boundary;
- invalid calibrated confidence or calibration kind raises
  `InvalidTrustQualificationResult`;
- calibration failure raises `CalibrationFailure`, not `ABSTAIN`;
- attempted mutation of raw result raises `RawInspectionMutationError`;
- evidence emission failure raises `TrustEvidenceEmissionFailure`;
- repeated qualification of identical fixed inputs yielding different outputs
  raises `NonReproducibleTrustQualification`;
- missing drift reference records absence and is not a failure.

## 11. Tests

Update `tests/test_trust_qualification_engine.py` with focused tests for the new
default baseline:

- calibrated confidence remains distinct from raw anomaly:
  - raw result `raw_anomaly_measure=5.0`;
  - confidence value is `0.9`;
  - `TrustQualificationResult` has no `raw_anomaly_measure` field;
  - `CalibratedTrustConfidence.calibration_kind` is
    `deterministic_rule_based_trust_baseline_v1`.
- same raw result produces identical output and evidence record.
- drift modifies caution without mutating the raw inspection result:
  - raw result `raw_anomaly_measure=5.0`, judgement `OK`;
  - no drift -> `ACCEPT`;
  - drift score `0.9` -> `REVIEW`, `DRIFTED`, `caution_applied=True`;
  - raw result remains equal to its deep copy.
- `REVIEW` and `ABSTAIN` remain engineered outcomes:
  - raw measure `35.0` -> `REVIEW`;
  - raw measure `49.0` -> `ABSTAIN`;
  - neither path raises an error.
- malformed inspection result fails explicitly:
  - `TrustQualificationEngine().qualify(object())` raises
    `MalformedRawInspectionResult`;
  - calibration failure is not disguised as `ABSTAIN`.
- trust evidence preserves both raw and qualification records.
- Trust engine exposes no image inspection, human review, operational routing,
  evaluation, training, update, persistence, or UI behavior.

Also run compatibility checks:

```bash
python3 -m pytest tests/test_trust_qualification_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

## 12. Integration Impact

The end-to-end integration layer should not change.

The default `TrustQualificationEngine()` should continue to return canonical
`TrustQualificationEngineOutput`. Existing integration expectations should
remain true:

- default integration drift score `0.8` produces a review path;
- no-review integration drift score `0.0` does not force review;
- integration continues to preserve Inspection, Trust, optional Review, Evidence,
  and Evaluation references;
- CLI output continues to include qualified outcome and identifiers only;
- CLI must not add scores, benchmark fields, production readiness claims, model
  performance claims, persistence, UI, or prototype behavior.

If deterministic output identifiers change because the calibration kind changes,
tests should assert consistency through emitted references rather than hard-code
old placeholder IDs.

## 13. Out of Scope

This plan does not implement:

- ML;
- probabilistic calibration;
- calibration science;
- uncertainty research;
- benchmark-derived thresholds;
- performance evaluation;
- image inspection;
- inspection result reconstruction;
- Human Review execution;
- operational routing;
- evidence presentation;
- Evaluation Engine behavior;
- persistence;
- UI;
- deployment;
- monitoring;
- training or model update loops;
- prototype or asset pipeline behavior;
- legacy retirement.

## 14. Implementation Steps

### Task 1: Add Baseline Contract Tests

**Files:**

- Modify: `tests/test_trust_qualification_engine.py`

**Goal:** Define the expected baseline behavior before changing Trust code.

**Approach:**

- Add imports for the new baseline calibration kind and calibrator.
- Add tests listed in §11.
- Update existing placeholder-specific assertions to expect the new baseline
  calibration kind for the default path.
- Keep legacy compatibility tests scoped to legacy types only.

**Verify:**

```bash
python3 -m pytest tests/test_trust_qualification_engine.py -q
```

Expected before implementation: tests fail because the new baseline names and
default calibration kind do not exist yet.

### Task 2: Add Baseline Calibration Labels

**Files:**

- Modify: `src/trust/domain.py`
- Modify: `src/trust/__init__.py`

**Goal:** Add the deterministic baseline calibration label without removing the
placeholder compatibility label.

**Approach:**

- Add `DETERMINISTIC_TRUST_BASELINE_CALIBRATION_KIND`.
- Add `VALID_CALIBRATION_KINDS`.
- Change `CalibratedTrustConfidence.calibration_kind` default to the baseline
  kind.
- Validate calibration kind against the allowed set.
- Export the new constant.

**Acceptance Criteria:**

- New default `CalibratedTrustConfidence` is baseline-labelled.
- Existing placeholder label can remain available as compatibility-only.
- Confidence remains bounded and explicitly marked with
  `CONFIDENCE_KIND == "calibrated_confidence"`.

### Task 3: Implement the Default Deterministic Baseline Calibrator

**Files:**

- Modify: `src/trust/engine.py`
- Modify: `src/trust/__init__.py`

**Goal:** Add `DeterministicTrustBaselineCalibrator` and make it the default
canonical calibrator.

**Approach:**

- Implement the formula in §5.
- Update `TrustQualificationEngine.calibrator` default factory to
  `DeterministicTrustBaselineCalibrator`.
- Keep `DeterministicPlaceholderCalibrator` available only if needed for
  compatibility.
- Update calibration failure text so it does not refer to placeholder behavior.
- Update uncertainty rationale strings to the baseline-specific wording in §9.
- Do not change `TrustQualificationEngine.qualify` legacy compatibility routing.

**Acceptance Criteria:**

- Default raw Trust flow uses the baseline calibrator.
- Raw result remains unchanged after qualification.
- `TrustQualificationEngine` still returns canonical
  `TrustQualificationEngineOutput` for `RawInspectionResult`.

### Task 4: Preserve Outcome and Drift Behavior

**Files:**

- Modify: `src/trust/engine.py`
- Modify: `tests/test_trust_qualification_engine.py`

**Goal:** Keep current deterministic outcome behavior while documenting it as the
baseline strategy.

**Approach:**

- Keep threshold constants aligned with §7 and §8.
- Confirm `ABSTAIN`, `REVIEW`, `ACCEPT`, and `REJECT` all remain reachable.
- Confirm drifted otherwise-automatic outcomes become `REVIEW`.
- Confirm unavailable drift records explicit absence.

**Acceptance Criteria:**

- `raw_measure=5.0`, `OK` -> `ACCEPT` without drift.
- `raw_measure=95.0`, `DEFECT` -> `REJECT` without drift.
- `raw_measure=35.0`, `OK` -> `REVIEW`.
- `raw_measure=49.0`, `OK` -> `ABSTAIN`.
- `raw_measure=5.0`, `OK`, drift `0.9` -> `REVIEW`.

### Task 5: Run Integration and Repository Validation

**Files:**

- No implementation files beyond Trust tests and Trust source.

**Goal:** Prove the baseline remains compatible with the existing canonical
integration chain and developer CLI.

**Verify:**

```bash
python3 -m pytest tests/test_trust_qualification_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git status --short
```

**Acceptance Criteria:**

- Trust tests pass.
- End-to-end substrate integration tests pass.
- CLI tests pass.
- Repo-wide tests pass.
- Compile check passes.
- `git status --short` shows only intended Trust source/test changes for the
  implementation task.
