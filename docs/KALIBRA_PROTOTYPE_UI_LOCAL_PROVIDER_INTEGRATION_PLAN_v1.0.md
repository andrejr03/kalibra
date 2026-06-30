# Kalibra Prototype UI Local Provider Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **Repository git rules (AGENTS.md):** Agents must never run `git add`,
> `git commit`, `git push`, or create branches. Validation checkpoints require
> running the listed commands, reporting results, and letting the repository
> owner control git history.

**Goal:** Make the existing Kalibra prototype UI display one deterministic,
real local inspection result produced from an existing PGM fixture through the
current local provider seam, without implementing product UI, a server, trust
qualification, review routing, evidence persistence, evaluation, or any new ML
framework.

**Architecture:** The slice adds a prototype-only adapter boundary above the
Inspection domain. The adapter calls
`LocalArtifactInferenceProvider.predict(...)`, passes the returned
`InspectionPrediction` to `InspectionEngine.transform_prediction(...)`, projects
the resulting `RawInspectionResult` into UI-safe static data, and the prototype
renders that projection. `InspectionEngine.inspect()` remains unwired from
providers.

**Tech Stack:** Existing Python standard-library implementation, existing
Inspection-domain dataclasses, existing PGM P2 fixtures, static HTML/Design
Component prototype, generated local JavaScript data artifact, and `pytest`.
No new third-party dependency, no new ML framework, no cloud service, no live
or hosted runtime.

---

## 1. Current Repository Map

### Prototype UI location

- Canonical prototype documents:
  - `assets/kalibra-prototype/prototype.html`
  - `assets/kalibra-prototype/prototype.dc.html`
- These two files are currently byte-identical and should remain intentionally
  synchronized if both are modified.
- Runtime support:
  - `assets/kalibra-prototype/support.js`
  - The file is generated (`GENERATED from dc-runtime/src/*.ts - do not edit`)
    and must not be edited for this slice.
- Prototype visuals:
  - `assets/parts/generated/master_clean/...`
  - `assets/parts/generated/master_clean_v2/...`
  - The current prototype paths reference `../parts/generated/...`, which is a
    legacy relative path that does not point at the nested `master_clean*`
    folders in the current repo layout. Do not repair the asset pipeline in this
    slice unless the implementation reviewer explicitly chooses to include a
    prototype asset path fix.

### Current mock/static data source

The active UI data is embedded directly inside the prototype document's
`<script type="text/x-dc" data-dc-script>` block.

- `const TH = '../parts/generated/';`
- `const CASES = [...]`
- `const EVAL = [...]`
- `const NAV = [...]`
- `const PRINCIPLES = [...]`
- `class Component extends DCLogic { ... renderVals() ... }`

`CASES` is currently fully static and fabricated for the prototype. It contains
fields such as `conf`, `outcome`, `drift`, `regionConf`, review reasons, and
evaluation-adjacent values. Those fields are not produced by the local provider
and must not be inferred for the real local result.

`EVAL` is also static prototype data. The implementation slice must not present
the local-provider result as evidence for those evaluation values.

### UI entry point and rendering path

1. Browser loads `assets/kalibra-prototype/prototype.html`.
2. The page loads `./support.js`.
3. `support.js` loads React/ReactDOM and boots the Design Component runtime.
4. The runtime parses the `<x-dc>` template.
5. The embedded `Component` class owns state and exposes `renderVals()`.
6. `renderVals()` derives:
   - `featured` from `CASES[s.caseIndex]`
   - `inspectList` from `CASES`
   - `trust` from the selected case
   - `reviewQueue` from cases whose `outcome` is `REVIEW` or `ABSTAIN`
   - `evidenceRows` from `CASES`
   - `datasetThumbs` from `CASES`
7. The template renders fields such as `featured.file`, `featured.runId`,
   `featured.result`, `featured.rawText`, `featured.regionConfText`, and
   hard-coded prototype images.

The smallest safe UI change is to prepend or separately render a single
adapter-produced case while preserving compatibility with the existing mock
case shape.

## 2. Existing Provider Boundary

The current Inspection-domain provider path already exists:

```text
LocalArtifactInferenceProvider.predict(StabilizedInspectionInput)
  -> InspectionPrediction
InspectionEngine.transform_prediction(StabilizedInspectionInput, InspectionPrediction)
  -> InspectionEngineOutput
  -> RawInspectionResult
  -> InspectionEvidenceRecord
```

The implementation slice must preserve these rules:

- `LocalArtifactInferenceProvider` returns only `InspectionPrediction`.
- `LocalArtifactInferenceProvider` does not construct `RawInspectionResult`.
- `LocalArtifactInferenceProvider` does not emit evidence, trust, review, or
  evaluation records.
- `InspectionEngine.transform_prediction(...)` owns transformation into
  `RawInspectionResult`.
- `InspectionEngine.inspect()` is not modified, extended, configured, or wired
  to a provider.
- `src/integration/engine.py` and `scripts/run_end_to_end_substrate.py` remain
  unchanged because they intentionally use the canonical substrate flow and
  currently call `InspectionEngine.inspect(...)`.

The safe seam for this UI slice is therefore a prototype-only adapter outside
the five permanent engines.

## 3. Recommended Implementation Slice

### Slice summary

Create a deterministic local adapter that generates a static UI projection from
`tests/fixtures/inspection/blob_defect.pgm`, then teach the prototype to render
that projection as a real inspection-only case.

This is the smallest safe slice because it:

- uses the existing local provider and existing PGM fixture;
- exercises the real provider-to-engine transformation path;
- avoids a server, hosted app, polling, scheduling, and live input handling;
- does not touch Trust, Review, Evidence, Evaluation, Integration, or CLI
  runtime behavior;
- does not add model dependencies or ML frameworks;
- keeps all downstream trust/review/evaluation fields explicitly absent for the
  real case.

### Demo data path

Use one fixture for the first UI integration:

```text
tests/fixtures/inspection/blob_defect.pgm
  -> StabilizedInspectionInput
  -> LocalArtifactInferenceProvider.predict(...)
  -> InspectionPrediction
  -> InspectionEngine.transform_prediction(...)
  -> RawInspectionResult
  -> UI-safe projection
  -> assets/kalibra-prototype/local-provider-demo-data.js
  -> assets/kalibra-prototype/prototype.html
```

The adapter should compute the fixture file's actual SHA-256 as
`content_hash`. It should not rely on a placeholder content hash.

Expected provider-derived values for `blob_defect.pgm` in the current
checkpoint:

- `judgement`: `DEFECT`
- `raw_anomaly_measure`: `75.0`
- `localization.region`: `x_min=0.25`, `y_min=0.25`, `x_max=0.75`,
  `y_max=0.75`
- `raw_measure_kind`: `raw_anomaly_measure`
- `raw_measure_scale`: `model_raw_anomaly_measure`
- `examination_kind`: `inspection_prediction`

The UI may include `uniform_ok.pgm` later, but the smallest initial slice should
display exactly one real local result unless the implementation reviewer expands
the scope.

## 4. UI-Safe Projection Contract

The projection must be a display view model, not a new domain result. It should
contain only presentation-safe copies of Inspection-owned data and explicit
absence markers for unimplemented downstream domains.

Required fields for the first slice:

| Field | Source | Notes |
| --- | --- | --- |
| `sourceKind` | constant | Use `local_provider_fixture_demo`. |
| `inputId` | `StabilizedInspectionInput.input_id` | Stable fixture-derived id. |
| `file` | fixture filename | `blob_defect.pgm`. |
| `artifactUri` | input artifact URI | Local path or `file://` URI. |
| `contentHash` | fixture SHA-256 | Actual file digest. |
| `inspectionResultId` | `RawInspectionResult.inspection_result_id` | Engine-owned. |
| `inspectionEvidenceRecordId` | `InspectionEngineOutput.inspection_evidence_record.record_id` | Engine-owned inspection evidence only. |
| `examinationId` | `RawInspectionResult.examination_id` | Prediction id after transformation. |
| `examinationKind` | `RawInspectionResult.examination_kind` | Must be `inspection_prediction`. |
| `result` | `RawInspectionResult.judgement` | UI label `DEFECT` or `OK`. |
| `rawMeasureKind` | `RawInspectionResult.raw_measure_kind` | Must stay raw. |
| `rawMeasureScale` | `RawInspectionResult.raw_measure_scale` | Do not relabel as confidence. |
| `rawMeasureValue` | `RawInspectionResult.raw_anomaly_measure` | Keep original 0-100 value. |
| `rawText` | formatted raw measure | Example: `75.00`. |
| `rawBarPercent` | derived display value | Clamp 0-100 for bar width only. |
| `localization` | `RawInspectionResult.localization.region` | Present only for defect. |
| `localizationText` | projection | Example: `x 0.25-0.75, y 0.25-0.75`. |
| `hasLocalization` | projection | Boolean. |
| `calibratedConfidence` | constant `null` | Explicitly absent. |
| `qualifiedOutcome` | constant `null` or `UNQUALIFIED` | Explicitly not produced. |
| `trustStatusText` | constant | `Trust qualification not run in this prototype slice.` |
| `reviewStatusText` | constant | `No review routing produced in this prototype slice.` |
| `evaluationStatusText` | constant | `No evaluation claim produced in this prototype slice.` |
| `visualization` | generated display data | Inline pixel-grid or SVG data URI generated from the PGM fixture. |

Forbidden projection fields:

- `confidence`
- `calibrated_confidence`
- `calibratedConfidence`, except as explicit `null`
- `drift`
- `driftScore`
- `qualifiedOutcome`, except as explicit absence/unqualified marker
- `reviewRouting`
- `groundTruth`
- `accuracy`
- `auc`
- `benchmark`
- `performanceClaim`
- any field that turns the raw measure into a trust or evaluation claim

The projection may include an inline SVG data URI built from the PGM pixels so
the prototype can display the actual fixture content without adding image
dependencies or generated PNG assets. This is preferable to manually creating a
PNG or modifying the deterministic prototype asset pipeline.

## 5. Exact Files Likely To Change

### Create

- `src/prototype_ui/__init__.py`
- `src/prototype_ui/local_provider_projection.py`
- `scripts/build_prototype_local_provider_demo.py`
- `tests/test_prototype_ui_local_provider_projection.py`
- `assets/kalibra-prototype/local-provider-demo-data.js`

### Modify

- `assets/kalibra-prototype/prototype.html`
- `assets/kalibra-prototype/prototype.dc.html`

### Must not modify in this slice

- `src/inspection/engine.py`
- `src/inspection/providers.py`
- `src/inspection/domain.py`
- `src/inspection/interfaces.py`
- `src/integration/engine.py`
- `scripts/run_end_to_end_substrate.py`
- `src/trust/`
- `src/review/`
- `src/evidence/`
- `src/evaluation/`
- `tools/generate_kalibra_part_assets.py`
- `assets/parts/source/`
- `assets/parts/generated/`

If implementation discovers that any "must not modify" file must change, stop
and surface the conflict before proceeding.

## 6. Implementation Tasks

### Task 1: Add a prototype UI projection adapter

**Goal:** Produce a deterministic, UI-safe projection from a local provider
result without changing core Inspection-domain contracts.

**Files:**

- Create: `src/prototype_ui/__init__.py`
- Create: `src/prototype_ui/local_provider_projection.py`
- Test: `tests/test_prototype_ui_local_provider_projection.py`

**Approach:**

- Build a `StabilizedInspectionInput` for
  `tests/fixtures/inspection/blob_defect.pgm`.
- Compute the fixture SHA-256 from bytes and use it as `content_hash`.
- Call `LocalArtifactInferenceProvider().predict(inspection_input)`.
- Call `InspectionEngine().transform_prediction(inspection_input, prediction)`.
- Project only `InspectionEngineOutput.raw_inspection_result` plus the
  engine-owned inspection evidence record id into a plain dictionary.
- Generate an inline visualization from PGM pixels for display only. The
  visualization is not evidence, not a performance artifact, and not part of the
  Inspection domain.

**Acceptance Criteria:**

- The adapter returns a dictionary with all required fields in Section 4.
- The adapter output is deterministic across repeated calls.
- `rawMeasureValue` is `75.0` for `blob_defect.pgm`.
- `rawText` is `75.00`.
- `rawBarPercent` is `75`.
- `result` is `DEFECT`.
- `localization` contains the normalized region `0.25, 0.25, 0.75, 0.75`.
- Trust, review, drift, ground-truth, and evaluation fields are absent or
  explicit absence markers.
- Tests prove the provider returns only `InspectionPrediction` and the adapter
  uses `InspectionEngine.transform_prediction(...)` for the raw result.

**Verify:**

```bash
python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
```

**Out of Scope:**

- Calling or modifying `InspectionEngine.inspect()`.
- Producing trust qualification, review routing, evidence views, or evaluation
  reports.
- Reading any non-fixture input.

### Task 2: Generate a static prototype data artifact

**Goal:** Make the real local inspection projection available to the static
prototype without adding a server or fetch dependency.

**Files:**

- Create: `scripts/build_prototype_local_provider_demo.py`
- Create/update generated output:
  `assets/kalibra-prototype/local-provider-demo-data.js`
- Test: `tests/test_prototype_ui_local_provider_projection.py`

**Approach:**

- The script imports the projection adapter.
- It writes a deterministic JavaScript assignment such as a single
  `window.KALIBRA_LOCAL_PROVIDER_DEMO = ...` payload.
- The payload must be stable across repeated runs for the same fixture.
- Do not include timestamps, random values, hostnames, absolute machine-specific
  paths, or environment-dependent metadata in the generated file.

**Acceptance Criteria:**

- Running the script produces
  `assets/kalibra-prototype/local-provider-demo-data.js`.
- Re-running the script without source changes produces byte-identical output.
- The generated payload contains the fixture filename, input id, inspection
  result id, raw result fields, localization, and explicit downstream absence
  messages.
- The generated payload does not contain `accuracy`, `auc`, `benchmark`,
  `groundTruth`, `calibratedConfidence` with a non-null value, or review routing.

**Verify:**

```bash
python3 scripts/build_prototype_local_provider_demo.py
python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
```

**Out of Scope:**

- JSON fetch from a server.
- Local web service.
- File watchers.
- Scheduled or recurring generation.

### Task 3: Teach the prototype to render the local provider result

**Goal:** Display the adapter-produced result in the prototype while keeping the
mock data clearly separate.

**Files:**

- Modify: `assets/kalibra-prototype/prototype.html`
- Modify: `assets/kalibra-prototype/prototype.dc.html`
- Read-only/generated support file: `assets/kalibra-prototype/support.js`

**Approach:**

- Load `./local-provider-demo-data.js` before the embedded Design Component
  script.
- In the embedded `Component` script, read
  `window.KALIBRA_LOCAL_PROVIDER_DEMO` if present.
- Render the local-provider case as the first/current inspection case or as a
  clearly labeled "Local Provider Result" panel.
- Keep existing mock cases available only as prototype sample data.
- Change hard-coded image bindings in the current-inspection/localization area
  to use the selected case's projection image fields when present, falling back
  to existing prototype images for mock cases.
- For the real local-provider case:
  - display the raw measure as raw measure, not confidence;
  - display confidence as absent;
  - display trust/review/evaluation as not produced by this slice;
  - do not place the case into the review queue unless a real
    Trust Qualification result exists in a later slice.

**Acceptance Criteria:**

- Opening the prototype after running the generator shows `blob_defect.pgm` as
  a local provider result.
- The displayed result is `DEFECT`.
- The displayed raw anomaly measure is `75.00` on the raw 0-100 scale.
- The displayed localization is present and corresponds to the normalized region
  from the transformed raw result.
- The UI contains visible wording that trust qualification, review routing, and
  evaluation are not produced for the local-provider demo case.
- Existing mock cases still render as prototype sample data.
- `prototype.html` and `prototype.dc.html` remain byte-identical after the
  intentional edits unless the implementation explicitly documents why one file
  became canonical.

**Verify:**

```bash
python3 scripts/build_prototype_local_provider_demo.py
python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
shasum assets/kalibra-prototype/prototype.html assets/kalibra-prototype/prototype.dc.html
```

**Out of Scope:**

- Redesigning the workbench.
- Updating generated prototype image assets.
- Replacing the Design Component runtime.
- Adding production UI navigation or a web app framework.

### Task 4: Boundary and regression validation

**Goal:** Prove the slice did not bend the provider seam or downstream domain
contracts.

**Files:**

- Test: `tests/test_prototype_ui_local_provider_projection.py`
- Existing tests:
  - `tests/test_inspection_engine.py`
  - `tests/test_integration_cli.py`
  - `tests/test_end_to_end_substrate_integration.py`

**Acceptance Criteria:**

- Provider-focused tests still pass.
- The prototype adapter tests pass.
- The integration CLI stays unchanged and does not start reading provider data.
- No test requires a cloud service, network access, GPU, ML framework, or
  generated assets outside the static data artifact.
- `InspectionEngine.inspect()` remains provider-unwired.

**Verify:**

```bash
python3 -m pytest tests/test_prototype_ui_local_provider_projection.py -q
python3 -m pytest tests/test_inspection_engine.py -k local_artifact_inference_provider -q
python3 -m pytest tests/test_inspection_engine.py -q
python3 -m pytest tests/test_end_to_end_substrate_integration.py -q
python3 -m pytest tests/test_integration_cli.py -q
python3 -m compileall -q src tests scripts
git status --short
```

Run the full suite if the focused commands pass and the implementation changed
shared helper behavior:

```bash
python3 -m pytest -q
```

## 7. Validation Notes For Review

Reviewers should check these points before authorizing implementation:

- The adapter calls `predict(...)` before `transform_prediction(...)`.
- The adapter never calls `InspectionEngine.inspect()`.
- No provider code imports UI/prototype modules.
- No Trust, Review, Evidence, Evaluation, Integration, or CLI runtime file is
  modified.
- The UI never displays raw anomaly as calibrated confidence.
- Any confidence, trust, review, drift, or evaluation value for the real local
  provider case is either absent or explicitly marked not produced.
- Generated static data is deterministic and fixture-derived.
- Existing prototype mock data remains visibly mock/sample data if it remains in
  the UI.

## 8. Self-Review

- Spec coverage: The plan identifies the prototype location, static data source,
  entry/rendering path, safe adapter seam, fixture path, projection fields, likely
  changed files, and validation commands.
- Boundary coverage: The plan preserves the provider-only prediction contract,
  `InspectionEngine.transform_prediction(...)` ownership, and the prohibition on
  provider wiring into `InspectionEngine.inspect()`.
- Scope coverage: The plan adds no ML framework, cloud dependency, live service,
  hosted runtime, feedback loop, trust implementation, review routing,
  evaluation result, or dataset claim.
