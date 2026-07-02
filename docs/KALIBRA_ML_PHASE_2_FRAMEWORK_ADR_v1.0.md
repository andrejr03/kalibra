# KALIBRA ML Phase 2 Framework ADR v1.0

## 1. Purpose

This Architecture Decision Record defines how Kalibra evaluated candidate
inference runtimes for ML Phase 2 and records the first selected runtime
candidate for a future framework-backed provider.

It does not authorize implementation. It does not authorize model loading,
session creation, inference, benchmark claims, dataset selection, or Sprint 1B.
It records the decision process, evaluation criteria, candidate trade-offs, and
runtime selection after the ML Phase 2 Scientific Architecture Plan.

Framework selection is a bounded engineering decision that remains subordinate
to the scientific decisions it serves:

- the inspection approach;
- the fixed dataset and split policy;
- the evaluation procedure;
- the target hardware and operating environments;
- the reproducibility obligations;
- the claims Kalibra is allowed to make.

Choosing a framework does not settle those scientific decisions and must not be
treated as evidence that the future method works. Treating a runtime choice as a
dataset, evaluation, or capability claim would violate Kalibra's rule that
evidence precedes assertion.

Status of this ADR:

```text
ONNX Runtime selected as the first framework-backed inference runtime candidate.
No model loading, session creation, inference, benchmark claim, or dataset
selection authorized.
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
as a decision that must be recorded in a dedicated ADR before any
framework-backed provider implementation begins. This ADR now records ONNX
Runtime as that first selected runtime candidate while keeping implementation
authorization separate.

Runtime selection was the next architectural decision because the provider seam
was ready but the first framework-backed implementation would introduce a new
dependency boundary. That boundary had to be evaluated before provider code was
added, so the framework could not quietly reshape Kalibra's contracts, claims,
evidence model, or reproducibility posture.

Sprint 1A added a narrow ONNX Runtime substrate in
`src/frameworks/onnx_runtime.py`. That module only detects runtime availability,
runtime version, execution-provider ordering, and read-only capability
information. Its tests prove graceful absence handling, deterministic capability
reporting, no session creation, no model loading, no tensor creation, no
inference API, and no filesystem or network access. This substrate supports the
runtime-selection decision without implementing a provider or changing any
Inspection, Trust, Review, Evidence, Evaluation, integration, CLI, or prototype
behavior.

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

This section preserves the candidate evaluation that led to the selected first
runtime candidate. Selection is recorded in §8.

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
- "Excellent" does not mean scientifically validated.
- "Weak" does not mean disqualified by itself.
- The ONNX Runtime selection is an engineering boundary decision only. It does
  not prove inspection quality, calibration quality, localization quality, or
  product readiness.

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

## 8. Decision

Decision:

```text
Select ONNX Runtime as the first framework-backed inference runtime candidate
for ML Phase 2.
```

Reasoning:

- **Inference-only fit.** ONNX Runtime is an inference-focused runtime rather
  than a training framework. That aligns with Kalibra's requirement that the
  future framework-backed provider execute inference behind the provider seam and
  return only an `InspectionPrediction`.
- **Provider-boundary compatibility.** ONNX Runtime can remain private to a
  future `InspectionInferenceProvider`. Runtime tensors, sessions, execution
  providers, device handles, model artifacts, intermediate outputs, and framework
  metadata must not cross into `InspectionPrediction`,
  `InspectionEngine.transform_prediction(...)`, Trust, Review, Evidence, or
  Evaluation.
- **Offline execution.** ONNX Runtime supports local execution, including CPU
  execution. That fits Kalibra's offline, batch, locally reproducible boundary.
- **Deterministic replay potential.** ONNX Runtime provides a bounded runtime
  surface where model artifact, execution provider, runtime version, threading,
  preprocessing, and hardware assumptions can be recorded and tested. Determinism
  remains a requirement to prove for each future provider; it is not assumed by
  selection.
- **Model-artifact boundary.** ONNX introduces a clear model artifact boundary
  that can be versioned, hashed, and kept provider-private. Export/conversion
  remains a risk to validate, but the artifact boundary is clearer than a
  training-framework runtime object.
- **Portability.** ONNX Runtime has a cross-platform runtime story with CPU
  execution as the appropriate baseline and optional execution providers that can
  remain non-load-bearing unless explicitly approved.
- **Substrate isolation already proven.** The committed Sprint 1A substrate
  `src/frameworks/onnx_runtime.py` exposes only availability, version,
  execution-provider ordering, default-provider discovery, and read-only
  capability information. Its tests prove that this repository can isolate ONNX
  Runtime discovery without session creation, model loading, tensor creation,
  inference, filesystem access, network access, or domain-boundary changes.

This decision does **not** authorize model loading, ONNX session creation,
inference, a framework-backed provider, benchmark claims, dataset selection,
evaluation protocol selection, or Sprint 1B. It only selects ONNX Runtime as the
first runtime candidate to use if and when the implementation authorization gate
is revised.

## 9. Consequences

### Implementation impact

No framework-backed provider may be implemented yet. ONNX Runtime is selected as
the first runtime candidate, but future provider work must wait until the
implementation authorization is revised and the remaining dataset and evaluation
gates are closed. Selection of ONNX Runtime does not permit model loading,
session creation, tensor creation, inference, benchmark claims, or downstream
domain changes.

### Documentation impact

The next documentation step is to revise the ML Phase 2 Implementation
Authorization if the repository owner chooses to authorize the next slice. That
revision must preserve the constraints in this ADR and must explicitly state
whether Sprint 1B is authorized.

### Testing impact

Future tests must include:

- provider-boundary tests proving only `InspectionPrediction` exits the provider;
- deterministic replay tests for repeated inference;
- mandatory use of the provider conformance harness for every framework-backed
  provider;
- environment/version capture tests;
- failure tests for missing model artifacts, incompatible runtime versions, and
  nondeterministic outputs;
- downstream unchanged tests for Trust, Review, Evidence, Evaluation,
  integration, and CLI.

### Reproducibility impact

Selecting ONNX Runtime fixes the first runtime candidate but does not yet fix a
model artifact, preprocessing path, execution-provider policy, dataset, or
evaluation protocol. Each future result must still be reproducible from pinned
runtime, model, input, preprocessing, configuration, and hardware evidence.

### Future provider implementations

Future providers must remain interchangeable implementations behind
`InspectionInferenceProvider`. A framework-backed provider may change raw values
inside a valid `InspectionPrediction`, but it may not change downstream
contracts or domain ownership.

`InspectionPrediction`, `InspectionInferenceProvider`,
`InspectionEngine.transform_prediction(...)`, Trust, Review, Evidence, and
Evaluation ownership are preserved. ONNX Runtime objects may not cross any domain
boundary.

## 10. Approval Criteria

This ADR records the first runtime-candidate selection. Sprint 1B or any
framework-backed provider implementation still requires the conditions below.

- The repository owner approves the ML Phase 2 Scientific Architecture Plan.
- The repository owner approves this ADR's decision process and ONNX Runtime
  selection.
- A specific target runtime environment is named: operating system, Python
  version, CPU baseline, and any optional accelerator policy.
- ONNX Runtime license and runtime package dependencies are reviewed and
  recorded.
- A dataset strategy document exists and defines the dataset, labels, splits,
  provenance, and fixture role.
- An evaluation strategy document exists and defines metrics, procedure,
  reproducibility evidence, and non-claims.
- A proof-of-fit implementation plan exists for ONNX Runtime, limited to the
  provider boundary and explicitly preserving all downstream domain ownership.
- The ML Phase 2 Implementation Authorization is updated by the repository owner
  to authorize the next bounded implementation slice.

ONNX Runtime is selected by this ADR. Implementation remains blocked until the
Implementation Authorization is revised and the remaining dataset and evaluation
conditions are satisfied or explicitly restricted by the repository owner.

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
- What exact restrictions will the Implementation Authorization place on Sprint
  1B before any ONNX Runtime provider work begins?

## 12. Next Decision

Recommended next planning artifact:

```text
KALIBRA_ML_PHASE_2_IMPLEMENTATION_AUTHORIZATION_v1.0.md
```

Implementation Authorization should be revised next because ONNX Runtime is now
selected as the first framework-backed inference runtime candidate, but provider
implementation is still not authorized. That revision must record whether Sprint
1B is permitted and under what restrictions.

Remaining conditions before Sprint 1B:

- the Implementation Authorization must be updated by the repository owner;
- the provider conformance and deterministic replay harness remains mandatory;
- no dataset is yet selected;
- no evaluation protocol is yet fixed;
- no model loading, session creation, inference, benchmark claim, or downstream
  domain change is authorized by this ADR.
