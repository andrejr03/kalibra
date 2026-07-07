# Kalibra Portfolio UX Stack & Prototype Review v1.0

**Status:** Recorded — review and planning only (no implementation, no file modification, no dependency addition)
**Date:** 2026-07-07
**Review HEAD:** `9c8e618 feat: retire canonical placeholder runtime`
**Branch:** `codex/initial-engineering-skeleton`
**Context:** ML Phases 2 and 3 are complete. The engineering/runtime core is strong enough for a
portfolio showcase. The goal is to make Kalibra memorable for Werkstudent recruiters, using only
free tooling.

## About This Document

This document persists the **Portfolio UX Stack & Prototype Review**. It is a review and planning
artifact only. It inspects the existing Claude Design prototype and recommends the minimum free stack
needed to turn Kalibra into a memorable, recruiter-facing portfolio experience.

It is **not** an implementation. It writes no code. It is **not** an authorization — it authorizes
no sprint, no dependency, no rewrite. It is **not** a roadmap update — it modifies no ADR, no
Strategy, no normative document. It records findings, a reuse decision, a stack recommendation, and
a non-authorizing implementation plan preview only.

Throughout, every claim made about Kalibra's actual capabilities is bounded to the evidence recorded
in the ML Phase 2 and Phase 3 checkpoints. The review refuses to recommend any portfolio element that
would assert a capability Kalibra has not demonstrated.

---

## 0. Repository State Context

ML Phase 3 closed at HEAD `9c8e618`. The repository now holds:

- A real, governed, replay-verified **runtime** that carries the learned PaDiM signal end-to-end
  through the canonical `inspect()` path (placeholder retired to a fixture-only seam).
- Real, governed **offline scientific evidence** (C-6): per-class VisA-proxy Image AUROC `0.757826`,
  Pixel AUROC `0.865196`, AUPRO `0.555765`, diagnostic P/R/F1 — single-seed, VisA-proxy only.
- A governed ONNX artifact, export-equivalence evidence, runtime-equivalence evidence, and
  placeholder-retirement evidence — all hash-anchored and inspectable.

Two honest gaps shape the portfolio:

- **No calibrated confidence / trust qualification.** The runtime carries a real raw anomaly measure
  but presents no calibrated confidence, no accept/review/reject outcome, no abstention, no drift.
- **README "Current Status" is stale.** It lists `[ ] Computer vision implementation` and
  `[ ] Evidence-backed evaluation results` as incomplete, but ML Phases 2–3 have delivered both.
  This is a documentation-drift issue a portfolio sprint should correct.

These two facts — real engineering depth, absent calibration — define the honest envelope of any
portfolio experience.

---

## 1. Existing Prototype Inventory

### 1.1 Assets found

| Asset | Location | Type | Role |
| --- | --- | --- | --- |
| **Canonical prototype** | `assets/kalibra-prototype/prototype.html` | static HTML | primary design prototype |
| Design-Component twin | `assets/kalibra-prototype/prototype.dc.html` | static HTML | byte-identical to `prototype.html` |
| Design runtime | `assets/kalibra-prototype/support.js` (57 KB, 1595 lines) | generated JS | "dc-runtime" React-based rendering engine |
| Honest demo data | `assets/kalibra-prototype/local-provider-demo-data.js` (5 KB) | static JS | real local-provider projection (single case) |
| Workbench PNG | `assets/KALIBRA_WORKBENCH_PROTOTYPE_v1.0.png` (1.8 MB) | image | static concept render |
| Archived v2 | `assets/prototypes/kalibra-prototype-v2.zip` (6.6 MB) | archive | superseded prototype snapshot |
| Evidence screenshots | `docs/evidence/prototype-ui/*.png` (3 files) | images | local-provider demo captures |
| Python projection | `src/prototype_ui/local_provider_projection.py` | Python | generates the honest demo data |
| Build script | `scripts/build_prototype_local_provider_demo.py` | Python | emits the demo data JS |

There are **two parallel data sources** inside the canonical prototype, and they are in tension:

1. **Honest source (governed):** `local-provider-demo-data.js`, produced by
   `local_provider_projection.py`, which runs the real local provider against a PGM fixture and
   *explicitly disclaims* trust/review/evaluation ("not run in this prototype slice").
2. **Fabricated source (mock):** the inline `CASES` and `EVAL` JavaScript arrays embedded directly in
   `prototype.html`, which contain invented metrics (AUC `0.91`, ECE `0.88`, calibrated confidence
   `0.76`, drift `0.42`, etc.) for 10 fake parts and 5 fake evaluation dimensions.

### 1.2 Stack assessment

- **The prototype is static HTML/CSS/JS** in the sense that it has no build step and no backend. But
  it is **not** plain hand-written HTML: the markup uses a custom `<x-dc>` Design Component dialect
  that depends on `support.js`, which is a *generated React runtime* ("GENERATED from dc-runtime/src
  — do not edit") that throws if `window.React` / `window.ReactDOM` / `window.Babel` are absent.
- **External CDN dependencies:** Google Fonts (Space Grotesk, IBM Plex Sans/Mono) and Phosphor Icons
  via `unpkg`. The React/ReactDOM/Babel trio is loaded by `support.js`. This means the prototype is
  **not currently self-contained**: opening `prototype.html` via `file://` will only render if the
  CDN runtime loads.
- **Connected to runtime or visual only?** *Visually* driven by fabricated `CASES`/`EVAL`. *Optionally*
  connected to one real result via `local-provider-demo-data.js`, but that honest projection is a
  single 4×4-pixel PGM fixture (a synthetic blob), not a compelling visual.
- **Suitable for free hosting?** Yes for static hosting (GitHub Pages / Netlify / Vercel), *if* the
  CDN-dependency and the fabricated-data problems are resolved. As-is, it is not deployable as an
  honest artifact.

### 1.3 Canonical prototype identification

`assets/kalibra-prototype/prototype.html` is the canonical prototype document.
`prototype.dc.html` is a byte-identical twin and should be kept synchronized or removed in a future
sprint. The workbench PNG is a separate static concept render, not interactive.

---

## 2. UX Quality Assessment

Assessed against the recruiter goal: *can a recruiter understand in 2–3 minutes that this is a
serious AI/runtime engineering project?*

| Dimension | Assessment |
| --- | --- |
| **First impression** | **Strong, but deceptive.** The dark "Workbench" aesthetic (amber `#e6a23c` hexagon mark, Space Grotesk/IBM Plex typography, dense monospaced metrics) reads as a polished, credible industrial tool. Visually it is well above a typical student project. **The problem:** the polish is anchored to fabricated metrics, so the strong first impression does not survive scrutiny by a technically literate recruiter. |
| **Visual identity** | **Excellent.** Consistent, restrained, industrial. The hexagon mark, the "OFFLINE MODE" chip, and the amber/slate palette signal a serious batch-inspection system, not a generic dashboard. This identity is a genuine asset worth preserving. |
| **Information architecture** | **Good.** The seven-item nav (Overview / Inspection / Trust / Review / Evidence / Evaluation / Dataset) mirrors Kalibra's five-domain architecture plus dataset. The right-rail trust gauge beside the inspection result is the right instinct (verdict + trust together). |
| **Narrative clarity** | **Weak — this is the core deficit.** Nothing in the UI explains *what makes Kalibra engineering-deep*: governed VisA acquisition, ONNX export, runtime-equivalence proofs, placeholder retirement, deterministic replay. A recruiter sees a dashboard; they do not see the engineering story that is actually the differentiator. |
| **Technical credibility** | **Undermined by fake data.** A recruiter who reads the numbers will find Image AUROC `0.91`, ECE `0.88`, calibrated confidence `0.76` — values Kalibra has not achieved and, for calibration/trust, has not even attempted. If they probe, the artifact collapses. This is the opposite of the design brief's "Honesty over polish." |
| **Memorability** | **Currently low for the right reasons, high for the wrong ones.** It looks memorable; but it is memorable as a visual, not as an engineering story. The *real* memorable story (governed evidence chain, machine-epsilon runtime equivalence, retired placeholder) is invisible. |
| **Mobile/desktop suitability** | **Desktop-only.** The overview grid sets `min-width:1180px` and a `212px 1fr` sidebar split. It does not reflow. Fine for a recruiter on a laptop; broken on mobile. |

**Verdict:** the visual layer is a real asset; the data layer is a liability. The prototype as-is
cannot be shown to a technical recruiter without misrepresenting Kalibra.

---

## 3. Engineering Storytelling Assessment

This is the core differentiator. The brief explicitly says: *do not treat this as a generic ML
dashboard.* The current UI fails this test — it *is* a generic (attractive) ML dashboard with no
engineering narrative.

| Engineering reality (demonstrated) | Currently shown in UI? |
| --- | --- |
| Governed VisA dataset (pinned archive, per-file manifest, frozen splits) | ❌ "Dataset" section shows fabricated "10,000 inputs, 1 part type" |
| Governed ONNX artifact (hash-anchored, opset 18, IR 10) | ❌ Not shown |
| Runtime provider integration (canonical `inspect()` carries real model) | ❌ Not shown |
| Runtime equivalence (6,492 samples, machine-epsilon deviation) | ❌ Not shown |
| Placeholder retirement (canonical path is PaDiM-only) | ❌ Not shown |
| Replay / deterministic validation (byte-identical second runs) | ❌ Not shown |
| Scientific boundaries (single-seed, VisA-proxy, no calibration) | ❌ "Evaluation" panel shows fabricated multi-dimensional scores implying a finished system |

**Every one of Kalibra's genuine engineering achievements is invisible, and every fabricated metric
occupies the space where the real story should be.** This is the single most important finding of the
review. The portfolio opportunity is not "polish the dashboard" — it is "replace the fake metrics
with the real evidence story."

The honest, recruiter-differentiating narrative is: *"This project doesn't just detect defects — it
proves, with hash-anchored evidence replayed byte-for-byte, that its runtime carries exactly the
validated offline signal, and it is honest about what it has not yet calibrated."* No current UI
element tells that story.

---

## 4. Minimum Free Stack Recommendation

### Option A — Keep static HTML/CSS/JS (as-is)

**Pros:** zero new dependencies; zero build step; nothing to learn; fastest path.
**Cons:** the existing `<x-dc>`/`support.js` dialect is a *generated React runtime* that depends on
CDN-loaded React/ReactDOM/Babel — it is not simple hand-written HTML, it is fragile (the "do not
edit" `support.js` cannot be maintained), and the fabricated inline data remains. Keeping it as-is
preserves the fake-claims problem.

### Option B — Static HTML/CSS/JS + lightweight bundled data (RECOMMENDED)

**Pros:**
- **Stays free, stays simple, stays honest.** No framework, no build pipeline, no backend, no
  database, no authentication, no live inference.
- **Eliminates the fake-data liability.** The UI renders only from static JSON bundles generated
  from Kalibra's real governed artifacts (the same `local_provider_projection.py` pattern, extended
  to C-6 metrics and the runtime-equivalence summary).
- **Self-contained.** Strip the `<x-dc>`/`support.js` dependency and the CDN React runtime; use plain
  HTML/CSS/vanilla-JS (or a tiny hand-written data-binding helper). This removes the fragile
  generated runtime and lets the page render from `file://` or any static host with no external JS.
- **Robust for GitHub portfolio viewing.** A static site with embedded/bundled JSON and relative
  asset paths renders directly on GitHub Pages with zero configuration.
- **Easy for André to explain.** "It's a static page that renders real, governed evidence JSON
  produced by the same Python pipeline that validates the model."

**Cons:**
- Requires rewriting the markup off the `<x-dc>` dialect (the visual design transfers; the templating
  does not).
- Vanilla-JS data binding is slightly more verbose than a framework, but the data volume is tiny
  (a handful of governed records, not thousands).

### Option C — React/Vite/Tailwind

**Pros:** modern, component-reusable, strong if the portfolio were to grow into an interactive app.
**Cons:** introduces a build toolchain (npm/Vite), a framework (React), and a utility-CSS dependency
(Tailwind) for a portfolio page whose entire data model is ~12 static JSON records. Over-engineered
for the goal; harder to keep free of maintenance; more to explain to a non-frontend recruiter.

### Option D — Next.js / Vercel Hobby

**Pros:** polished SSR/dev experience; Vercel Hobby is free.
**Cons:** the heaviest option for a need that requires no routing, no server, no API, and no dynamic
content. Pulls in React, a build pipeline, and a hosting platform coupling. Violates "must be simple
to explain" and "must not require backend hosting" in spirit.

### Decision

```text
Option B — Static HTML/CSS/JS + lightweight bundled data.
```

It is the only option that is simultaneously **free, simple, honest, self-contained, and robust on
GitHub Pages**, while removing the fabricated-data and generated-runtime liabilities. Option A is
rejected because it preserves both liabilities. Options C/D are rejected as over-engineered for a
static evidence surface.

---

## 5. Recommended Experience Concept

The minimum memorable concept, designed around the *real* engineering story. Prioritizes memorability
over feature count.

### 5.1 Landing / hero

One sentence: *"Kalibra inspects parts for defects — and, for every decision, shows you the governed
evidence for whether that decision can be trusted."* Plus the hexagon mark and the "OFFLINE · BATCH ·
LOCALLY REPRODUCIBLE" chips (already in the design language). A single line stating the honest
boundary: *"Single-seed VisA-proxy evidence. No calibrated confidence yet."*

### 5.2 Runtime inspection console (the centerpiece)

Show **one real governed inspection** rendered from honest projection data: the input, the raw
anomaly measure, the localization. Crucially, show the **raw-vs-calibrated distinction honestly**: the
raw measure is present; "Calibrated confidence — not yet produced" is shown plainly (the
`local-provider_projection.py` already emits exactly this disclaimer). This *is* the design brief's
thesis made visible.

### 5.3 Evidence / replay panel

The differentiator. Show the **governed evidence chain** as a literal, inspectable timeline:
`archive SHA-256 → files manifest → frozen splits → C-4 training → C-5 inference → C-6 evaluation →
ONNX export → runtime equivalence → placeholder retirement`, each node hash-anchored. Show the
**replay proof**: "a complete second run is byte-identical." This is what no other student project
has, and it is already fully evidenced.

### 5.4 Runtime equivalence panel

A small, honest visualization of the equivalence result: 6,492 samples, max deviation
~7.1e-15 (machine epsilon), tolerance 1e-12 — "the runtime carries exactly the validated offline
signal." One chart, one sentence. Recruiters who understand ML will recognize this is non-trivial.

### 5.5 Architecture / capability timeline

A compact timeline of the ML phase lineage (Phase 1 substrate → Phase 2 offline science → Phase 3
runtime integration), each phase linked to its checkpoint. This turns the repository's own
governance discipline into a portfolio artifact.

### 5.6 "Why trust this result?" panel

Not a fake gauge. A real panel that states: *what is demonstrated* (real learned signal, governed and
replay-verified at runtime), *what is not* (no calibration, single seed, VisA proxy), and *how to
verify it* (every claim hash-anchored in the repo). This is the design brief's "inspectable, not
authoritative" principle.

### 5.7 Limitations panel (kept, not hidden)

The current "Stated Boundaries" section is good and should be kept verbatim: "Not live / not
streaming," "One inspection setting," "Not a deployment service," "Partner to human judgement." Add
the scientific boundaries: single-seed, proxy-domain, no calibrated confidence.

### 5.8 Recruiter-friendly technical summary

A short, plain-language footer/sidebar: "What is demonstrated," "What is deferred," "How to verify,"
with links into `docs/`. Designed for a 2-minute scan.

**What is deliberately removed:** the fabricated 10-case gallery, the fake 5-dimension evaluation
scores, and the calibrated-confidence gauge (until calibration exists). Removing these *increases*
credibility with a technical recruiter.

---

## 6. Prototype Reuse Decision

```text
PARTIAL REDESIGN
```

**Technical justification:**

- **Keep:** the visual identity (hexagon mark, amber/slate palette, Space Grotesk/IBM Plex
  typography, dark "Workbench" aesthetic), the seven-section information architecture (it mirrors the
  five-domain flow), the "Stated Boundaries" panel, and the right-rail "verdict + trust together"
  layout instinct.
- **Replace:** the `<x-dc>` / `support.js` generated-React templating (fragile, unmaintainable, CDN-
  dependent) with plain static HTML/CSS + a tiny vanilla-JS data binder.
- **Replace:** the fabricated `CASES`/`EVAL` inline arrays with static JSON bundles generated from
  Kalibra's real governed artifacts.
- **Add:** the evidence/replay chain, runtime-equivalence panel, architecture timeline, and honest
  "Why trust this result?" panel — none of which exist today.
- **Remove:** the calibrated-confidence gauge and the multi-dimensional evaluation scores, until and
  unless the underlying capabilities are demonstrated and evidenced.

A full REPLACE would discard a genuine visual asset; a KEEP-AND-POLISH would preserve the fake-data
liability. PARTIAL REDESIGN is the only honest, leverage-maximizing choice.

---

## 7. Free Hosting Recommendation

| Rank | Target | Why |
| --- | --- | --- |
| **Primary** | **GitHub Pages** | Free, zero-config for a static site, lives next to the source (a recruiter sees the repo *and* the running site in one place), supports custom domains later, no backend needed. Maximally robust for "GitHub portfolio viewing." |
| **Fallback** | **Netlify Free** (or Vercel Hobby) | Also free for static sites; useful if GitHub Pages is undesirable or if drag-and-drop deploy is preferred. Vercel Hobby is free but couples to a platform; Netlify is the more neutral fallback. |

**Local-only demo** is a valid tertiary fallback (open the static HTML directly), but it does not
serve the recruiter goal of a shareable link. **Not recommended as primary.**

The recommended stack (Option B) deploys to GitHub Pages with no build step and no backend — a single
`docs/` folder or `gh-pages` branch with the static HTML/CSS/JS/JSON.

---

## 8. Implementation Plan Preview (non-authorizing)

A short, non-authorizing sketch for a future sprint. Not a commitment; not an authorization.

**Files that would be touched (additive new portfolio surface):**
- A new `portfolio/` (or `site/`) directory at the repo root containing the static site
  (`index.html`, `styles.css`, `app.js`, and bundled `data/*.json`).
- A new generator script (e.g. `scripts/build_portfolio_evidence_bundle.py`) that emits the static
  JSON bundles from the *existing* governed artifacts (C-6 evaluation summary, runtime-equivalence
  summary, evidence-chain hashes) — extending the existing
  `local_provider_projection.py` pattern.

**What should remain unchanged:**
- `src/` (no runtime, domain, or engine changes — the portfolio reads governed artifacts, it does not
  alter them).
- `docs/` normative documents and checkpoints (the portfolio *links to* them; it does not modify
  them).
- The existing `assets/kalibra-prototype/` (kept as the design reference / source of visual identity;
  not deployed as the portfolio itself).
- All governed artifacts under `artifacts/` and `data/` (read-only).

**What data can be embedded as static JSON:**
- C-6 per-class metrics (Image AUROC `0.757826`, Pixel AUROC `0.865196`, AUPRO `0.555765`, diagnostic
  P/R/F1) — *real, from the C-6 evidence*.
- Runtime-equivalence summary (6,492 samples, max abs deviation `7.105e-15`, tolerances
  `{1e-12, 1e-12, 0.0}`, replay byte-identical) — *real, from the Task-4 evidence*.
- The evidence-chain SHA-256 hashes (archive, files, splits, C-4, C-5, C-6, ONNX, runtime) — *real,
  from the governed records*.
- One real local-provider inspection projection (input, raw measure, localization, "calibration not
  produced" disclaimer) — *real, from `local_provider_projection.py`*.

**How to keep it free:** static site on GitHub Pages; no build step (or a trivial Python generator
already covered by the existing toolchain); no external paid services.

**How to avoid fake claims:** the generator reads *only* governed artifacts and *only* emits values
that exist in them. Any field not present in the evidence (calibrated confidence, accept/review/reject,
drift, multi-seed variance) is rendered as an explicit "not yet demonstrated" absence — never
invented. This is the design brief's "evidence before assertion" enforced in the build pipeline.

**How to avoid requiring a backend:** all data is pre-bundled JSON; the site is fully static; no
server, no API, no live inference. (Live runtime inference is explicitly disallowed by AGENTS.md
anyway.)

**Recommended parallel doc fix:** correct the stale `README.md` "Current Status" checklist
(`[ ] Computer vision implementation` / `[ ] Evidence-backed evaluation results`) to reflect ML
Phases 2–3. This is a small, high-value honesty fix that should accompany any portfolio sprint.

---

## 9. Recruiter Impact Assessment

What would make this UI memorable for Werkstudent recruiters — concretely, avoiding generic
"modern dashboard" language.

1. **The evidence chain as a visible artifact.** Most student ML projects show a metric; Kalibra can
   show a *hash-anchored chain of provenance* from dataset archive to runtime, each link verifiable.
   A recruiter who has seen ten dashboards will remember the one that said "every number on this page
   is reproducible from this SHA-256." This is rare and it is real.

2. **Honesty about absence as a feature.** A calibrated-confidence gauge that *says "not yet
   produced"* is more memorable — and more credible — than a fake gauge showing `0.76`. A recruiter
   who understands ML engineering will read "we have not calibrated confidence yet, and we say so" as
   maturity, not as a gap. This directly embodies the design brief's thesis and is Kalibra's
   personality made visible.

3. **The runtime-equivalence proof.** "The runtime reproduces the offline validated signal across
   6,492 samples at machine-epsilon deviation" is a sentence that distinguishes a serious runtime
   engineering project from a notebook demo. It is already evidenced; it just needs to be shown.

4. **The placeholder-retirement narrative.** "We retired the placeholder model from the canonical path
   only after proving equivalence" is a story about engineering discipline that recruiters in
   reliability/ML-ops adjacent roles will recognize as the real thing.

5. **The governed-dataset story.** VisA is a real, cited industrial anomaly dataset; showing that
   Kalibra acquires it under a governed, hash-pinned, manifest-driven pipeline — rather than
   "downloaded some images" — signals engineering seriousness.

6. **The visual identity.** The hexagon mark, the restrained amber/slate industrial aesthetic, and
   the "OFFLINE · BATCH · REPRODUCIBLE" framing already read as a credible engineering tool, not a
   student toy. Preserving this while replacing the fake data converts a deceptive asset into an
   honest one.

The memorable hook is the combination: **a polished industrial UI whose every number is backed by a
reproducible, hash-anchored evidence record, and which is openly honest about what it has not yet
achieved.** That combination is what no fabricated dashboard can fake.

---

## 10. Readiness Decision

```text
READY FOR PORTFOLIO UX IMPLEMENTATION
```

**Justification:**

1. **The engineering substance exists.** ML Phases 2–3 delivered a real governed model, a real
   runtime carrying it, real equivalence evidence, and a real evidence chain — all hash-anchored and
   inspectable. The portfolio has something real to show.
2. **The honest envelope is clear.** The portfolio can show detection evidence and runtime
   engineering honestly; it must not show calibration/trust/drift, which are not yet demonstrated.
   This boundary is well-defined and enforceable in a data-bundle generator.
3. **The stack is settled and free.** Static HTML/CSS/JS + bundled JSON on GitHub Pages requires no
   paid service, no backend, and no live inference.
4. **The reuse decision is bounded.** PARTIAL REDESIGN preserves the visual asset, replaces the
   fragile templating and fabricated data, and adds the missing engineering narrative.
5. **The one prerequisite doc fix is small.** Correcting the stale README "Current Status" is a
   minor honesty fix that should accompany the sprint.

**This readiness decision authorizes nothing.** It identifies readiness only. Any implementation
sprint requires its own authorization checkpoint, reviewed and approved by the repository owner,
before work begins. The sprint must enforce the no-fake-claims rule in its generator (only governed
artifact values are emitted; absent capabilities are rendered as explicit absences).

---

## 11. Scope Boundaries and Explicit Non-Claims

This review records:

- **No code implemented.** No source, test, script, HTML, CSS, JS, JSON, or evidence file was created
  or modified by this review. The only working-tree change is the creation of this checkpoint
  document.
- **No authorization granted.** No portfolio sprint, no dependency, no rewrite, no hosting choice,
  and no README modification is authorized by this review.
- **No scientific or product claim beyond the ML Phase 2/3 evidence.** Every capability attributed to
  Kalibra in this review (real learned model, governed dataset, runtime integration, equivalence,
  replay, placeholder retirement) is bounded to the recorded checkpoints. The explicit non-claims
  (no calibrated confidence, no trust qualification, no multi-seed variance, no domain-of-record
  performance, no product-readiness) are carried forward unchanged.
- **No endorsement of the fabricated prototype data.** This review identifies the inline `CASES`/`EVAL`
  arrays as fabricated and explicitly recommends their replacement. They must not be shown to a
  recruiter as-is.

---

## 12. Validation

| Validation | Command | Result |
| --- | --- | --- |
| HTML/CSS/JS/TS inventory | `find . -maxdepth 4 \( -iname "*.html" -o -iname "*.css" -o -iname "*.js" -o -iname "*.ts" -o -iname "*.tsx" \) \| sort` | 4 files in `assets/kalibra-prototype/` ✔ |
| Whitespace | `git diff --check` | exit 0 (clean) ✔ |
| Working tree (pre-write) | `git status --short` | clean (no output) ✔ |
| Canonical prototype identity | `diff prototype.html prototype.dc.html` | identical ✔ |
| Prototype asset path | `ls assets/parts/generated/` | resolves (master_clean, master_clean_v2) ✔ |
| HEAD | `git log -1 --oneline` | `9c8e618 feat: retire canonical placeholder runtime` ✔ |

The only working-tree change after this review is the creation of this checkpoint document itself.

---

## 13. Next Natural Step

```text
Review this persisted Portfolio UX Stack & Prototype Review before authorizing a Portfolio UX
implementation sprint.
```

If a sprint is authorized, its scope should be: PARTIAL REDESIGN on a static HTML/CSS/JS + bundled-
JSON stack (Option B), deploying to GitHub Pages, with a generator that emits *only* governed-
artifact values and renders absent capabilities as explicit absences. The sprint should also correct
the stale `README.md` "Current Status" checklist as a parallel honesty fix. Until then, the existing
prototype — with its fabricated inline metrics — must not be presented to recruiters as an honest
artifact.
