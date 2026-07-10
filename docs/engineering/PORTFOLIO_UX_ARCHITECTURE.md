# Portfolio UX Architecture

**Date:** 2026-07-07
**Baseline:** ML Phase 2 complete, ML Phase 3 complete. Runtime complete, runtime equivalence complete, placeholder retired. Portfolio UX not yet implemented.
**Audience:** early-career engineering technical reviewers and technically literate junior-hiring reviewers.
**Governing principle:** *Evidence before assertion.*

---

## The Evidence Envelope (what the UI is allowed to claim)

This is the factual boundary. The UI may build experiences on the left column. It must
present the right column as **Not yet demonstrated**.

| Demonstrated — usable as evidence | Not yet demonstrated — must be labeled |
| --- | --- |
| Governed VisA proxy acquisition (`visa-acq-v1`), archive + split SHA-256 | Live data ingestion / streaming |
| PaDiM baseline fit (`visa-padim-baseline-fit-v1`), training replay | Multiple model families / comparison |
| ONNX export + **export-equivalence** vs PyTorch (hash-anchored) | Real-time / on-device inference |
| **Runtime-equivalence** verification (byte-level replay) | **Calibrated confidence** |
| Runtime provider integration, deterministic **replay** (`status: passed`) | **Accept / review / reject** routing |
| Placeholder retirement (canonical path carries real PaDiM signal) | **Abstention** on low confidence |
| Scientific evaluation C-6: Image AUROC `0.757826`, Pixel AUROC `0.865196`, AUPRO `0.555765` | **Drift assessment** |
| Diagnostic P/R/F1 per class (incl. weaknesses: precision `0.209`) | **Human review** loop (interactive) |
| SHA-256 governance across every artifact | Any production / deployment claim |

Numbers above are single-seed, VisA-proxy only. The UI must carry that qualifier
wherever a metric appears.

---

## 1. Portfolio Objective

**Why this UI exists.** To let a technical reviewer who does *not* trust the system verify, in a
few minutes and without reading code, that Kalibra is a serious AI-runtime engineering
project whose every claim is backed by an inspectable artifact — and that its author
understands the difference between a result and a *trustworthy* result.

The UI is not a product demo and not a portfolio brag page. It is an **inspectable
surface over a fixed, reproducible body of evidence**.

**What technical reviewers remember, by dwell time:**

- **After 30 seconds** — *"This is a real inspection runtime, not a slideshow. It says
  what it can and can't prove, and it looks like an engineer built it."* One sentence of
  identity + one piece of undeniable evidence (a governed hash, an equivalence verdict).
- **After 2 minutes** — *"Every number on screen traces to a hash I could re-check.
  There's a full engineering chain from raw dataset to a governed ONNX runtime, and the
  author deliberately did **not** fake the trust/calibration layer they haven't built
  yet."* The evidence chain + the honesty boundary.
- **After 10 minutes** — *"This person builds trustworthy ML systems. They separate a
  raw anomaly score from calibrated confidence, they proved runtime equivalence to
  machine precision, they retired their own placeholder, and they can name exactly where
  the science stops. I want to interview them."* The full thesis: honesty as an
  engineering discipline.

**Single success test:** a technically literate technical reviewer who tries to poke a hole in
the project finds the hole already labeled, with the evidence sitting next to it.

---

## 2. technical reviewer Journey

The journey is engineered so the **strongest, most falsifiable evidence appears first**,
and the honesty boundary is presented as a strength, not a footnote.

```
1. Landing / Hero        →  Identity + one undeniable proof
        ↓
2. The Two Questions     →  The thesis: verdict AND trustworthiness
        ↓
3. Inspection (Runtime)  →  A real governed decision, followed end to end
        ↓
4. Evidence Chain        →  Dataset → model → ONNX → equivalence → runtime → replay
        ↓
5. Architecture          →  The five domains as a directed flow
        ↓
6. Scientific Results    →  Honest metrics, including the weak ones
        ↓
7. The Honest Boundary   →  What is NOT yet demonstrated (trust/calibration/drift)
        ↓
8. Engineering Timeline  →  records as a governed build history
        ↓
9. Repository / Verify   →  How to reproduce it yourself
```

**Why this sequence:**

- **Evidence before narrative.** The runtime and the equivalence proof are the hardest
  things to fake, so they come before any prose about vision. This inverts the typical
  portfolio (story first, proof maybe-never).
- **The thesis (step 2) is placed early but after the hero**, so the technical reviewer has a
  reason to care about "can it be trusted?" before seeing a decision.
- **The honest boundary (step 7) comes *after* the strong results**, never before. A
  technical reviewer who has already seen real equivalence proofs reads "trust layer not yet
  built" as *discipline*; a technical reviewer who saw it first would read it as *incompleteness*.
- **Timeline is late (step 8), not early.** Process is only interesting once the
  technical reviewer believes the output is real.
- **Repository is the exit, not the entrance.** The UI earns the click to GitHub by
  first proving the work is worth reading.

The journey must be **skimmable in one axis**: a technical reviewer can scroll top-to-bottom in
90 seconds and get the whole story, or stop and expand any station to inspect it.

---

## 3. Information Architecture

**Recommendation: a single long-scroll narrative page with anchored stations and
on-demand depth — not a multi-page dashboard, not a tabbed SPA.**

Rationale: technical reviewers give portfolios one linear pass. A single governed page with a
persistent progress rail lets them consume the whole story in one scroll and drill in
where curious. Tabs hide the narrative; multi-page loses the through-line.

**Primary structure (one page, nine stations):**

| # | Station | Priority | Depth model |
| --- | --- | --- | --- |
| 0 | Hero | P0 | Fixed centerpiece + two CTAs |
| 1 | The Two Questions (thesis) | P0 | Static, one screen |
| 2 | Inspection / Runtime | P0 | Summary visible; raw payload expandable |
| 3 | Evidence Chain | P0 | Chain visible; each hash expandable + copyable |
| 4 | Architecture (five domains) | P1 | Flow visible; per-domain detail expandable |
| 5 | Scientific Results | P1 | Macro numbers visible; per-class table expandable |
| 6 | Honest Boundary | P0 | Static, deliberately prominent |
| 7 | Engineering Timeline | P2 | Collapsed list; each record expandable |
| 8 | Repository / Verify | P1 | Commands + links |

**Navigation:** a slim persistent left/top rail mirroring the five-domain vocabulary
(Inspection · Trust · Review · Evidence · Evaluation) plus Dataset and Timeline. The
rail doubles as a **reading-progress indicator**. It must reuse the existing prototype's
domain vocabulary (the seven-item nav already mirrors the architecture) so the site and
the codebase speak the same language.

**Flows:** exactly one primary flow (scroll the narrative). Two secondary flows:
(a) "inspect a case" — expand any decision to its raw governed payload; (b) "verify a
hash" — copy any SHA-256 and re-check it against the repo. No other flows. No filters,
no search, no settings, no account.

**Explicitly avoided:** a generic KPI dashboard, a card grid of vanity metrics, a
sidebar of unrelated widgets, any surface that implies live operation.

---

## 4. Hero Experience

The first 15 seconds must establish **identity + credibility + honesty** simultaneously,
without a single fabricated number.

- **Headline:** *"Kalibra inspects — and decides whether its own inspection can be
  trusted."* (States the thesis; not a tagline about AI.)
- **Subheadline:** *"An offline, reproducible visual-inspection runtime for industrial
  quality control. Every result on this page is backed by a governed, inspectable
  artifact — and everything not yet demonstrated is labeled as such."*
- **Primary CTA:** *"Follow a governed decision"* → scrolls to the Inspection/Runtime
  station (the strongest evidence, not a signup).
- **Secondary CTA:** *"Verify the evidence"* → scrolls to the Evidence Chain (invites
  the skeptic to check hashes).
- **Visual centerpiece:** the **live governed identity strip** — the real runtime
  artifact fingerprint (`model.onnx` SHA-256 `0437ae…d741a`), the `OFFLINE MODE` chip,
  and a single unfakeable verdict badge: **"Runtime equivalence: verified · replay:
  passed."** This is the one thing on the hero that a technical technical reviewer cannot
  dismiss, and it is true today.

**Constraints on the hero:** no hero metric that isn't governed; no calibrated-confidence
number (there isn't one yet); no motion that implies live inference. The centerpiece is
evidence, not decoration. It must render self-contained (no CDN font/icon/runtime
dependency) so it survives `file://` and GitHub Pages equally.

**What the hero must NOT do:** claim accuracy, claim trust/confidence, claim production
readiness, or show a spinner pretending to "analyze."

---

## 5. Runtime Experience

The runtime is the star. It is the one place where Kalibra's real, governed machinery is
visible end to end.

**What is visible (default):**

- The input identity — a real representative VisA case (e.g. `candle/…/Anomaly/004.JPG`,
  content-hash `a78ee8…5ab2`), its class and split.
- The **verdict**: defective / not-defective, and *where* (localization region).
- The **raw anomaly measure** — presented explicitly as *raw*, not confidence.
- The governed model identity carrying the decision
  (`kalibra/inspection/padim-onnx-export@1.0.0#sha256:0437ae…`).
- The session configuration fingerprint (`2893fd…a2e4`) and the deterministic knobs that
  make it reproducible (single-thread, `ORT_DISABLE_ALL`, CPU EP).

**What is hidden (until expanded):**

- The full replay payload (`runtime_replay.json`) — first-run vs second-run comparison
  across artifact identity, predictions, localization, raw measures, run hash, and
  session config.
- The toolchain pin (onnxruntime `1.19.2`, numpy `2.0.2`, python `3.9.6`).
- The feature-extraction contract id (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`).

**What is expandable:** every identity string is a disclosure — click to see the artifact
it names and its hash. The decision is a *chain that can be walked*, not a single badge.

**What is interactive:** the technical reviewer may switch between the small set of **real**
representative inputs (the governed `representative_inputs`, currently two) and watch the
verdict, raw measure, and localization update from **precomputed governed JSON** — never
from live inference. A visible, honest label states: *"Precomputed from a governed offline
run. Kalibra does not run inference in your browser."*

**The single most important UI rule of this station:** the *raw anomaly measure* and
*calibrated confidence* must never be blurred. Because calibrated confidence does not
exist yet, the trust panel beside the verdict must show a labeled **"Trust
qualification — not yet demonstrated"** state, not an invented gauge. The right-rail
"verdict + trust together" instinct from the prototype is correct; the trust half is
honestly empty for now.

---

## 6. Evidence Experience

Evidence is not a table to read; it is a **chain to walk and a claim to verify**.

**The spine:** a single directed evidence chain the technical reviewer can traverse:

```
Governed dataset  →  PaDiM baseline  →  ONNX export  →  Export equivalence
      →  Runtime equivalence  →  Runtime integration  →  Deterministic replay
```

Each link is a station with three layers:

1. **The claim** in one plain sentence (*"The ONNX model produces the same outputs as the
   PyTorch model it was exported from."*).
2. **The proof handle** — the governing SHA-256(s) and the verdict (`passed` / `verified`),
   rendered as **copyable** values.
3. **The re-check invitation** — the exact artifact path in the repo and, where relevant,
   the command that regenerates or re-verifies it. The technical reviewer can copy a hash and
   confirm it against the repository themselves. Verifiability is the experience.

**Signature evidence moments to design around** (each already real):

- **Runtime equivalence** — export/runtime outputs matching to machine precision. Framed
  as *"we proved the runtime didn't change the science."*
- **Deterministic replay** — the same input, run twice, producing byte-identical governed
  output (`runtime_replay.json`, all seven comparisons `true`).
- **Governed hashes** — a wall of SHA-256s that all resolve to real files; the technical reviewer
  can pick any one and check it.
- **Placeholder retirement** — the moment the canonical path stopped using a placeholder
  and started carrying the real learned signal
  (`placeholder_used_on_canonical_runtime_path: false`).

**Explicitly not a design goal:** dumping the metrics table as the "evidence" section.
The metrics live in Scientific Results (§9-of-brief / station 5). Evidence here means
*provenance and reproducibility*, not scores.

---

## 7. Architecture Experience

The five-domain architecture must be *experienced as a decision flowing through a
system*, not read as documentation.

**Design:** a single **directed flow** the technical reviewer can trace with their eye and expand
node by node:

```
Inspection  →  Trust Qualification  →  Human Review
   (real)          (not yet)             (not yet)
       ↘                                    ↙
            Evidence  ←  Evaluation
             (real)       (real)
```

Each domain node states, in one line, its single responsibility, and carries an honest
**status chip**:

- **Inspection Engine** — *what the system sees.* Real: carries the governed PaDiM signal
  end to end. Emits a raw anomaly measure that is explicitly **not** confidence.
- **Trust Qualification Engine** — *how far to trust it.* **Not yet demonstrated.** This
  is where raw score would become calibrated confidence and accept/review/reject/abstain
  outcomes. Its emptiness is labeled, and its intended contract is described as *future
  work*, not asserted as built.
- **Human Review Engine** — *where uncertainty goes.* **Not yet demonstrated** as an
  interactive loop; architectural seam only.
- **Evidence Engine** — *what can be inspected.* Real: the governed artifacts and hashes
  the whole site stands on.
- **Evaluation Engine** — *what the science says.* Real: C-6 governed metrics.

**Why a flow, not a diagram-in-a-doc:** the brief's thesis is that a decision is *a
chain, not a verdict*. The architecture experience must let the technical reviewer follow that
chain and see exactly where the chain is complete (Inspection → Evidence → Evaluation)
and where it is deliberately unbuilt (Trust → Review). The gap in the flow *is* the
honest story, drawn to scale.

---

## 8. Scientific Honesty

Honesty must read as **rigor**, never as weakness. The mechanism:

- **A single, consistent "Not yet demonstrated" treatment.** One visual/verbal
  convention, used everywhere a capability is absent (trust, calibration, drift, review,
  multi-seed, production). It is stated calmly and specifically — *what* is not
  demonstrated and *why that boundary exists* — never as an apology.
- **Boundaries are placed beside strength, not in a hidden "limitations" ghetto.** The
  "Trust — not yet demonstrated" panel sits *next to* the real verdict; the unbuilt
  domains sit *inside* the architecture flow. Proximity to real evidence converts a gap
  into a considered decision.
- **Every metric carries its qualifier inline.** "Single-seed, VisA-proxy" travels with
  the number, always. The weak diagnostic numbers (precision `0.209`, high false
  positives) are shown, not hidden — shown as evidence that the author reads their own
  results honestly.
- **Future work is described as contract, not promise.** Where calibration is absent, the
  UI can state the *intended* accept/review/reject/abstain contract as a design the author
  understands — framed explicitly as "designed, not yet evidenced."

**The reframing sentence the whole section serves:** *a clearly drawn limit is a sign of
understanding, not a gap.* The UI must make a technical reviewer think "this person knows exactly
where their science stops" — which is rarer and more hireable than a fake 0.99.

---

## 9. Memorable Moments

Five engineering moments (not animations) designed to lodge in memory:

1. **"Verify it yourself."** The technical reviewer copies a real SHA-256 from the page and
   confirms it against the repository. The instant a claim becomes *personally verified*,
   the project stops being a portfolio and becomes evidence.
2. **Raw score ≠ trust.** The verdict shows a real raw anomaly measure beside a panel that
   honestly reads *"calibrated confidence — not yet demonstrated."* The technical reviewer grasps,
   in one glance, the distinction most ML projects never even acknowledge.
3. **Machine-precision runtime equivalence.** The moment the technical reviewer sees that the ONNX
   runtime reproduces the original model's outputs to machine precision — *"they proved
   the engineering didn't corrupt the science."*
4. **Run it twice, byte for byte.** Deterministic replay: same input, two runs, identical
   governed hash across all seven comparisons. Reproducibility made tangible.
5. **They retired their own placeholder.** The point where the canonical path dropped the
   placeholder and carried the real learned signal — an author disciplined enough to
   remove their own scaffolding and prove it's gone.

Each moment is a *fact the technical reviewer can check*, not an effect they watch.

---

## 10. Visual Philosophy

Principles only — no screens.

- **Evidence-first.** Every visible claim is adjacent to its proof handle. If it can't be
  backed, it isn't shown as fact.
- **Calm and industrial.** Restraint over spectacle. The existing identity (amber
  hexagon mark, `OFFLINE MODE` chip, Space Grotesk / IBM Plex, slate palette, dense
  monospaced metrics) is a genuine asset and should be preserved and de-faked, not
  replaced.
- **Inspectable.** Depth is always one disclosure away; nothing important is summarized
  beyond the ability to check it.
- **Deterministic.** The aesthetic signals a fixed, reproducible batch artifact — no live
  feeds, no fake motion, no "analyzing…" theater.
- **Transparent about boundaries.** Absence is designed, labeled, and calm — a first-class
  visual state, not an error state.
- **Legible hierarchy.** A 90-second top-to-bottom skim yields the whole story; expansion
  yields the proof. Honesty and depth coexist without clutter.

---

## 11. Free Technology Constraints

The architecture is deliverable entirely on the free static stack. It requires nothing
else.

- **Hosting:** GitHub Pages (static). No backend, no login, no cloud, no database, no live
  inference.
- **Composition:** static HTML + CSS + vanilla JS + **generated JSON bundles** projected
  from the governed artifacts (`artifacts/runtime/*.json`, evidence docs) by an offline
  build script. The JSON is precomputed governed output — the browser only renders it.
- **Self-contained mandate.** The current prototype depends on CDN Google Fonts, Phosphor
  Icons, and a generated React/Babel runtime (`support.js`) that throws without CDN. The
  portfolio build must **inline or vendor** fonts, icons, and any runtime so the page
  renders identically on GitHub Pages and via `file://`. No external host is a dependency
  for a claim to be visible.
- **No live inference** in the browser, ever. Interactivity is switching between
  precomputed governed cases and expanding governed payloads — clearly labeled as such.

This constraint is not a limitation to hide; a fully static, self-contained, governed site
*is itself evidence* of the offline-reproducible thesis.

---

## 12. Portfolio Story

**Beginning.** *Most automated inspectors fail silently — they keep answering with
confidence while quietly going wrong.* Kalibra is built on the opposite conviction: the
most valuable thing an inspector can offer is not certainty but honesty about
uncertainty. So Kalibra is designed to do two things in one motion — reach a verdict, and
qualify how far that verdict can be trusted.

**Middle.** To earn the right to make that claim, the engineering was built and *proven*,
bottom-up and governed at every step: a governed dataset with hashed splits, a PaDiM
baseline with a replayable training record, an ONNX export proven equivalent to its
source, a runtime proven equivalent to the export, deterministic replay that reproduces
byte-identical output, and the deliberate retirement of the placeholder so the canonical
path carries only the real learned signal. Every link is a hash the technical reviewer can check.
The science is reported honestly, weak numbers included.

**End.** And then the honesty turns inward: the trust-qualification layer — the calibrated
confidence, the accept/review/reject/abstain routing, the drift, the human-review loop —
is *the thesis of the whole system*, and it is **not yet demonstrated.** Kalibra says so,
in the same calm voice it uses for its proofs. The story it leaves the technical reviewer with is
not "look how finished this is," but *"look how precisely this person knows what they have
proven and what they have not."* That is the memorable note: engineering honesty as a
demonstrated discipline.

---

## 13. Anti-Patterns

The UX must avoid, without exception:

- **Fake AI / fake inference.** No in-browser "analysis," no spinner that pretends to
  compute. All results are precomputed and governed.
- **Fabricated metrics.** No invented AUROC, ECE, calibrated confidence, or drift. The
  prototype's inline `CASES`/`EVAL` mock numbers (AUC `0.91`, ECE `0.88`, confidence
  `0.76`, drift `0.42`) are **prohibited** and must be replaced by governed values or a
  "not yet demonstrated" state.
- **Blurring raw score and calibrated confidence.** These are different things; the UI
  must never present the raw anomaly measure as if it were trust.
- **Generic dashboards / vanity KPI grids.** No card wall of decontextualized numbers.
- **Loading spinners and fake motion** implying live operation.
- **Marketing language / hype.** No "revolutionary," "powered by AI," superlatives. Plain,
  precise engineering voice only.
- **Hidden assumptions or buried limitations.** No "limitations" ghetto at the bottom;
  boundaries sit beside the relevant claim.
- **CDN-dependent claims.** No evidence whose visibility depends on an external host
  loading.
- **Overclaiming completeness or production readiness.** Kalibra is an offline engineering
  artifact, and the UI says so.

---

## 14. Readiness Decision

```
READY FOR VISUAL DESIGN
```

**Rationale.** The technical reviewer experience is fully specified at the architectural level: a
defined objective with time-boxed memory goals, an ordered journey, a single-page
information architecture, a governed hero, a runtime-as-star experience, an evidence-as-
verification model, a five-domain flow with honest gaps, a scientific-honesty convention,
five checkable memorable moments, a visual philosophy, and a free-stack delivery model —
all bounded to the existing evidence envelope, with anti-patterns named. The honest
boundary (absent trust/calibration layer) is not a blocker; it is a designed, first-class
part of the experience. Visual design can proceed against this architecture without
inventing any capability Kalibra has not evidenced.

**One precondition to carry into visual design (not a blocker):** the visual layer must
de-fake the existing prototype — remove the fabricated `CASES`/`EVAL` data and the CDN/
generated-React dependency — and bind exclusively to governed JSON projected from
`artifacts/` and `docs/evidence/`. The identity (amber hexagon, industrial palette,
`OFFLINE MODE`, Space Grotesk / IBM Plex) is preserved.

---

## Traceability

- Evidence envelope grounded in: `docs/evidence/SCIENTIFIC_EVALUATION.md`,
  `docs/evidence/RUNTIME_EQUIVALENCE.md`,
  `docs/evidence/RUNTIME_PROVIDER_INTEGRATION.md`,
  `docs/evidence/PLACEHOLDER_RETIREMENT.md`,
  `artifacts/runtime/{integration_metadata,runtime_replay,runtime_hashes}.json`.
- Thesis and domain vocabulary: `README.md`, `docs/FOUNDATION.md`, and
  `docs/ARCHITECTURE.md`.

**Next natural step:** review this persisted portfolio architecture before
starting any future visual redesign.
