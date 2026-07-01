# KALIBRA ML Phase 2 Framework ADR v1.0

## 1. Purpose

This Architecture Decision Record defines how Kalibra will evaluate candidate
inference runtimes for ML Phase 2.

It does not authorize implementation. It does not select a runtime framework.
It records the decision process, evaluation criteria, candidate trade-offs, and
current recommendation after the ML Phase 2 Scientific Architecture Plan.

Framework selection is deferred until the scientific architecture is approved
because a framework choice cannot be separated from the scientific decisions it
serves:

- the inspection approach;
- the fixed dataset and split policy;
- the evaluation procedure;
- the target hardware and operating environments;
- the reproducibility obligations;
- the claims Kalibra is allowed to make.

Choosing a framework before those decisions are fixed would turn an engineering
preference into an implicit scientific commitment. That would violate Kalibra's
rule that evidence precedes assertion.

Status of this ADR:

```text
Proposed decision process.
No framework selected.
No implementation authorized.
```

## 2. Context

Kalibra now has a completed ML Phase 1 local-provider path.

The current repository baseline includes:

- a deterministic five-domain runtime:
  Inspection -> Trust Qualification -> Human Review -> Evidence -> Evaluation;
- the permanent `InspectionInferenceProvider` boundary;
- `InspectionPrediction` as the only provider output contract;
- `InspectionEngine.transform_prediction(...)` as the owner of validation and
  transformation into `RawInspectionResult`;
- `LocalArtifactInferenceProvider` as the first real local provider, reading
  deterministic PGM P2 fixture content and returning only `InspectionPrediction`;
- prototype integration that displays the real local-provider inspection result
  while explicitly withholding trust, review, drift, and evaluation claims;
- an opt-in local-provider end-to-end evidence integration path;
- ML Phase 1 local-provider closure, which records that the checkpoint proves a
  boundary and composition path, not production ML quality.

The ML Phase 2 Scientific Architecture Plan defines runtime framework selection
as a deferred decision that must be recorded in a dedicated ADR before any
framework-backed provider implementation begins.

Runtime selection is now the next architectural decision because the provider
seam is ready but the first framework-backed implementation would introduce a
new dependency boundary. That boundary must be evaluated before code is added,
so the framework cannot quietly reshape Kalibra's contracts, claims, evidence
model, or reproducibility posture.

Official candidate references checked for this ADR include:

- [ONNX Runtime documentation](https://onnxruntime.ai/docs/)
- [PyTorch documentation](https://docs.pytorch.org/) and
  [determinism notes](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [LiteRT / TensorFlow Lite documentation](https://developers.google.com/edge/litert)
- [OpenVINO documentation](https://docs.openvino.ai/) and
  [OpenVINO repository](https://github.com/openvinotoolkit/openvino)
- [OpenCV DNN documentation](https://docs.opencv.org/4.x/d6/d0f/group__dnn.html)
  and [OpenCV license page](https://opencv.org/license/)

These references establish candidate characteristics only. They do not provide
Kalibra-specific benchmark evidence.

## 3. Decision Drivers

Every candidate runtime must be evaluated against all of the criteria below.
No single criterion dominates all others. A strong runtime on one axis may still
be rejected if it weakens a load-bearing architecture boundary or makes evidence
hard to reproduce.

Mandatory criteria:

- **Offline execution.** Inference must run fully locally. Network services,
  hosted inference, phone-home behavior, and live operation are disallowed.
- **Deterministic inference.** The runtime must support repeatable inference for
  fixed model artifacts, fixed input bytes, fixed preprocessing, fixed runtime
  configuration, and fixed hardware class. Any nondeterminism must be bounded,
  documented, and tested.
- **Reproducibility.** The runtime, model artifact, preprocessing, configuration,
  and environment must be versioned so an observer can regenerate the result.
- **Provider-boundary compatibility.** The runtime must sit behind
  `InspectionInferenceProvider` and return only `InspectionPrediction`.
- **Portability.** The runtime should work across the local platforms Kalibra is
  likely to support without tying the architecture to one vendor or accelerator.
- **Maintainability.** The runtime should have a stable API, active maintenance,
  clear release/versioning behavior, and practical Python integration.
- **Licensing.** License terms and relevant third-party dependencies must be
  compatible with Kalibra's intended local reproducible use before adoption.
- **Hardware support.** CPU execution must be viable for baseline reproducibility.
  Accelerators may be supported but must not be required unless explicitly
  approved.
- **Explainability impact.** The runtime should not prevent Kalibra from tracing
  predictions to model version, input, preprocessing, and raw output evidence.
- **Deployment complexity.** The runtime should not force hosted services,
  heavyweight build systems, fragile binary packaging, or platform-specific
  operational assumptions into the baseline.
- **Ecosystem maturity.** The runtime should have sufficient documentation,
  examples, support, and model-format stability to sustain future providers.

Decision quality depends on recorded evidence for each criterion, not on runtime
popularity.

## 4. Candidate Frameworks

This section evaluates the candidate runtimes neutrally. It selects none.

### ONNX Runtime

**Strengths**

- Strong architectural fit for an inference-only provider.
- Cross-platform runtime with a clear model artifact boundary around ONNX.
- Can consume models exported from several training ecosystems.
- Supports CPU execution and optional hardware execution providers.
- Keeps training framework choice separate from runtime choice.

**Weaknesses**

- Requires model export or conversion to ONNX, which adds a failure mode and a
  reproducibility artifact that must be validated.
- Operator support and numerical behavior may differ between source framework,
  ONNX export, and runtime execution.
- Execution providers can introduce hardware-specific behavior that must be
  pinned or disabled for baseline reproducibility.

**Architectural fit**

Good. ONNX Runtime can live behind `InspectionInferenceProvider` and produce raw
prediction values that are adapted into `InspectionPrediction`.

**Offline suitability**

Good to Excellent. Local CPU inference is compatible with Kalibra's offline
posture.

**Inference determinism**

Acceptable to Good, subject to model operations, threading, execution provider,
and hardware configuration. Determinism must be proven by Kalibra tests rather
than assumed.

**Deployment considerations**

Moderate. The runtime dependency is focused, but model export, ONNX opset
version, and execution provider selection become required evidence.

**Maintenance implications**

Good. The runtime is mature and widely used, but Kalibra would need explicit
version pinning and export compatibility tests.

### PyTorch

**Strengths**

- Mature ecosystem for model development, experimentation, and training.
- Strong Python support and broad model availability.
- Official controls exist for using deterministic algorithms where available.
- Good fit for research iteration before a final inference runtime is selected.

**Weaknesses**

- Larger dependency footprint than an inference-only runtime.
- Blurs training and inference concerns unless carefully constrained.
- Some operations and hardware paths may remain nondeterministic unless avoided
  or configured.
- Packaging and runtime environment can be heavier than Kalibra's first
  framework-backed provider likely needs.

**Architectural fit**

Acceptable to Good if strictly wrapped behind `InspectionInferenceProvider`.
Weaker if it encourages training-time objects, tensors, or model internals to
leak into runtime contracts.

**Offline suitability**

Good. Local inference is feasible.

**Inference determinism**

Acceptable to Good, depending on operations, seeds, deterministic algorithm
settings, hardware, and backend configuration. The ADR cannot treat PyTorch
determinism as automatic.

**Deployment considerations**

Moderate to heavy. PyTorch may be appropriate for training or research, but a
leaner inference runtime may be preferable for Kalibra's first production-shaped
provider boundary.

**Maintenance implications**

Good ecosystem maturity, but higher dependency and environment management cost.

### TensorFlow Lite / LiteRT

**Strengths**

- Designed for on-device and edge inference.
- Focuses on local execution, low latency, and compact deployment.
- Useful when target devices are mobile, embedded, or resource constrained.
- Separation between converted model artifact and runtime can support provider
  encapsulation.

**Weaknesses**

- Requires conversion into TFLite/LiteRT-compatible artifacts.
- Operator coverage and quantization behavior can constrain model choices.
- Python-first desktop development may be less direct than with PyTorch or ONNX
  Runtime.
- The TensorFlow Lite to LiteRT naming/ecosystem transition must be tracked
  carefully before approval.

**Architectural fit**

Good if Kalibra targets edge-style local inference and conversion artifacts are
versioned. Less compelling if the near-term runtime target is a general local
desktop/server CPU environment.

**Offline suitability**

Excellent for on-device inference.

**Inference determinism**

Acceptable to Good, depending on delegate, quantization, operator support, and
hardware path. Determinism must be tested for the selected artifact and delegate.

**Deployment considerations**

Good for constrained devices, but conversion, delegate selection, and operator
compatibility become part of the evidence burden.

**Maintenance implications**

Good ecosystem maturity, with the caveat that Kalibra must track current LiteRT
documentation, package names, and TensorFlow Lite compatibility.

### OpenVINO

**Strengths**

- Inference-focused toolkit for optimizing and deploying models.
- Strong support for CPU execution and Intel hardware acceleration.
- Supports multiple operating systems and Python/C++ APIs.
- Can provide strong performance for supported hardware without changing the
  Kalibra provider contract.

**Weaknesses**

- Hardware story is strongest on Intel platforms, which may create portability
  and vendor-lock-in concerns.
- Model conversion and intermediate representation handling add evidence and
  maintenance obligations.
- Non-Intel hardware support and behavior must be evaluated against Kalibra's
  actual target platforms.

**Architectural fit**

Good if hardware assumptions are explicit and optional. Weakens if Intel
acceleration becomes load-bearing before project scope approves it.

**Offline suitability**

Good to Excellent. It is designed for local inference.

**Inference determinism**

Acceptable to Good, depending on device plugin, precision, threading, and model
operations. Kalibra must validate fixed-output behavior for the selected device
configuration.

**Deployment considerations**

Moderate. Strong if the environment is Intel-centered; more complex if Kalibra
needs broad vendor-neutral portability.

**Maintenance implications**

Good for supported hardware, with explicit version and conversion pipeline
management required.

### OpenCV DNN

**Strengths**

- Familiar computer-vision library with an inference-only DNN module.
- Supports loading serialized networks from multiple formats.
- Designed for forward-pass computation, not training, which aligns with the
  provider-only runtime boundary.
- OpenCV may also cover preprocessing needs in the same dependency.

**Weaknesses**

- DNN model support can lag dedicated runtimes for newer architectures and
  operators.
- Performance and backend support depend heavily on OpenCV build options.
- Python package variants may pull in additional third-party dependencies that
  require license and packaging review.
- It may encourage mixing image preprocessing and inference runtime concerns
  unless provider boundaries are disciplined.

**Architectural fit**

Acceptable. It can sit behind `InspectionInferenceProvider`, but Kalibra must
avoid letting OpenCV become a general inspection-domain dependency outside the
provider.

**Offline suitability**

Good. Local forward-pass inference is compatible with Kalibra.

**Inference determinism**

Acceptable, subject to backend, target device, model support, and preprocessing.
Determinism must be proven per model and backend.

**Deployment considerations**

Moderate. CPU-only use may be straightforward; accelerated backends can require
custom builds or platform-specific configuration.

**Maintenance implications**

Acceptable to Good for stable classical/CV-adjacent models. Weaker for rapidly
evolving deep-learning architectures.

## 5. Compatibility With Kalibra Architecture

No candidate framework may alter Kalibra's architecture:

```text
InspectionInferenceProvider
        |
        v
InspectionPrediction
        |
        v
InspectionEngine.transform_prediction(...)
        |
        v
RawInspectionResult
        |
        v
Trust
        |
        v
Review
        |
        v
Evidence
        |
        v
Evaluation
```

Required compatibility rules for every candidate:

- The runtime appears only inside an `InspectionInferenceProvider`
  implementation.
- The provider returns only `InspectionPrediction`.
- Runtime tensors, model sessions, interpreter handles, execution providers,
  device handles, intermediate outputs, and framework metadata never cross into
  Trust, Review, Evidence, or Evaluation.
- The Inspection Engine remains the only owner of `RawInspectionResult`.
- Trust Qualification remains the only owner of calibrated confidence,
  uncertainty characterization, drift caution, and qualified outcomes.
- Human Review remains the only owner of review case preparation and reviewer
  decision recording.
- Evidence remains the only owner of preservation, lineage, absence markers, and
  read-only evidence views.
- Evaluation remains the only owner of evidence-backed evaluation reports.
- The default CLI and default deterministic integration path remain unchanged
  unless a later owner-approved implementation plan explicitly changes them.

Candidate-specific compatibility notes:

- **ONNX Runtime:** Compatible when ONNX session output is immediately projected
  into `InspectionPrediction` and ONNX artifacts stay provider-private.
- **PyTorch:** Compatible when tensors, modules, and device state remain
  provider-private and no training objects enter runtime contracts.
- **TensorFlow Lite / LiteRT:** Compatible when interpreter outputs are mapped
  into `InspectionPrediction` and delegates remain provider-private.
- **OpenVINO:** Compatible when compiled models, device plugins, and IR artifacts
  remain provider-private.
- **OpenCV DNN:** Compatible when OpenCV `Net`, blobs, and backend/target
  details remain provider-private.

Any implementation that requires changing the downstream chain is rejected, even
if the runtime is otherwise attractive.

## 6. Decision Matrix

Qualitative comparison:

| Criterion | ONNX Runtime | PyTorch | TensorFlow Lite / LiteRT | OpenVINO | OpenCV DNN |
| --- | --- | --- | --- | --- | --- |
| Offline execution | Excellent | Good | Excellent | Excellent | Good |
| Deterministic inference controllability | Good | Acceptable | Good | Good | Acceptable |
| Reproducibility artifact clarity | Good | Acceptable | Good | Good | Acceptable |
| Provider-boundary compatibility | Excellent | Good | Good | Good | Acceptable |
| Portability | Good | Good | Good | Acceptable | Good |
| Maintainability | Good | Good | Good | Good | Acceptable |
| Licensing clarity | Good | Good | Good | Good | Good |
| Hardware support | Good | Good | Good | Excellent on supported hardware | Acceptable |
| Explainability impact | Good | Acceptable | Good | Good | Acceptable |
| Deployment complexity | Good | Weak to Acceptable | Good | Acceptable | Acceptable |
| Ecosystem maturity | Excellent | Excellent | Good | Good | Good |

Interpretation:

- The matrix is a planning instrument, not a scorecard.
- "Excellent" does not mean approved.
- "Weak" does not mean disqualified by itself.
- Final selection requires Kalibra-specific proof under the approval criteria in
  this ADR.

## 7. Risks

### Vendor lock-in

OpenVINO may optimize best for Intel hardware. TensorFlow Lite / LiteRT may pull
the project toward Google's edge ecosystem. ONNX Runtime reduces training
framework lock-in but introduces the ONNX conversion boundary. PyTorch may lock
runtime and training choices together if not constrained. OpenCV DNN may lock
model choice to the subset of formats and operators it supports well.

### Runtime complexity

Every runtime adds model loading, preprocessing, postprocessing, artifact
versioning, dependency pinning, and failure modes. A runtime that looks simple in
an example can become complex when determinism and evidence are required.

### Reproducibility

Hardware acceleration, threading, precision changes, quantization, graph
optimizations, delegates, and execution providers can change outputs. Kalibra
must test reproducibility on the exact runtime configuration it intends to
support.

### Dependency footprint

Large binary packages can make local replay harder. Dependency size also affects
reviewability, supply-chain risk, and long-term maintenance.

### Future maintenance

Model formats, operator support, runtime APIs, and package names change. Any
selected runtime needs a version policy and compatibility tests.

### Hardware assumptions

Kalibra must not accidentally require a GPU, NPU, vendor accelerator, or hosted
service. CPU execution should remain the reproducible baseline unless the owner
approves a different hardware baseline.

### Unsupported claims

Selecting a runtime does not prove detection quality, calibration quality,
localization quality, robustness, or product readiness. The ADR must not be used
as a proxy for benchmark evidence.

## 8. Current Recommendation

Current recommendation:

```text
Defer framework selection and defer implementation.
```

Reasoning:

- The ML Phase 2 Scientific Architecture Plan requires this ADR before
  implementation, but it also requires dataset and evaluation strategy approval
  before implementation.
- No specific dataset, model approach, metric policy, or hardware target has
  been approved.
- No candidate has been tested in this repository against Kalibra's fixed
  provider boundary, deterministic replay requirements, and evidence-chain
  expectations.
- Candidate documentation shows all five runtimes can plausibly support local
  inference, but plausibility is not sufficient evidence for adoption.
- Selecting a framework now would be premature and could bias dataset and model
  decisions that should remain evidence-led.

Shortlist for later proof-of-fit:

- Keep all five candidates open for the next decision cycle.
- Give first proof-of-fit attention to ONNX Runtime, TensorFlow Lite / LiteRT,
  and OpenVINO if the approved dataset/model approach is exportable to those
  inference-focused runtimes.
- Treat PyTorch as strong for research and model development, but require an
  explicit justification before using it as the runtime dependency.
- Treat OpenCV DNN as a pragmatic baseline candidate for simple vision models,
  but require operator-support and packaging evidence before adoption.

No framework is selected by this ADR.

## 9. Consequences

### Implementation impact

No framework-backed provider may be implemented yet. Future provider work must
wait until the framework decision, dataset strategy, and evaluation strategy are
approved.

### Documentation impact

The next documents must close the evidence gaps this ADR identifies. The
framework ADR remains proposed until approval criteria are satisfied.

### Testing impact

Future tests must include:

- provider-boundary tests proving only `InspectionPrediction` exits the provider;
- deterministic replay tests for repeated inference;
- environment/version capture tests;
- failure tests for missing model artifacts, incompatible runtime versions, and
  nondeterministic outputs;
- downstream unchanged tests for Trust, Review, Evidence, Evaluation,
  integration, and CLI.

### Reproducibility impact

Deferring selection preserves reproducibility by avoiding an unpinned runtime
dependency before the project knows which artifacts and environment must be
fixed.

### Future provider implementations

Future providers must remain interchangeable implementations behind
`InspectionInferenceProvider`. A framework-backed provider may change raw values
inside a valid `InspectionPrediction`, but it may not change downstream
contracts or domain ownership.

## 10. Approval Criteria

This ADR may be considered approved only when all conditions below are met.

- The repository owner approves the ML Phase 2 Scientific Architecture Plan.
- The repository owner approves this ADR's decision process and current
  recommendation.
- A specific target runtime environment is named: operating system, Python
  version, CPU baseline, and any optional accelerator policy.
- Candidate licenses and runtime package dependencies are reviewed and recorded.
- A dataset strategy document exists and defines the dataset, labels, splits,
  provenance, and fixture role.
- An evaluation strategy document exists and defines metrics, procedure,
  reproducibility evidence, and non-claims.
- A proof-of-fit plan exists for one or more shortlisted runtimes, limited to the
  provider boundary and explicitly out of implementation scope until approved.
- Approval explicitly states whether the ADR remains in "defer selection" status
  or is revised to select one runtime.

A runtime may be selected only after these conditions are met and the selection
is recorded as an update or superseding ADR.

## 11. Open Questions

- What dataset will ML Phase 2 use, and what labels and localization ground truth
  will it contain?
- Which inspection approach will be evaluated first: classical CV, feature-based
  ML, anomaly detection, autoencoder, supervised CNN, or another bounded method?
- What operating systems and CPU architectures must be supported for local
  replay?
- Is GPU, NPU, or other accelerator support optional or part of the baseline?
- What exact determinism tolerance is acceptable for floating-point inference?
- How will preprocessing be versioned and kept provider-private?
- How will model artifacts be stored, hashed, and referenced as evidence?
- What license review process applies to runtime dependencies and model
  artifacts?
- What failure behavior is required when runtime inference is unavailable or
  non-reproducible?
- How will evaluation distinguish runtime numerical differences from model
  quality differences?

## 12. Next Decision

Recommended next planning artifact:

```text
KALIBRA_ML_PHASE_2_DATASET_STRATEGY_v1.0.md
```

Dataset strategy should come next because framework fit cannot be finalized
without knowing the data, labels, splits, provenance, localization support,
hardware expectations, and evaluation evidence obligations. Until that document
is approved, framework-backed implementation remains deferred.

