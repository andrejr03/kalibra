# Kalibra — Portfolio Experience Implementation Plan v1.0

> **For agentic workers:** This plan is executed task-by-task via
> `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`.
> Section 16 holds the ordered, bite-sized task sequence with exact paths and verify commands.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** Plan only — no implementation. No repository file is modified except this plan document.
**Date:** 2026-07-08
**Branch:** `codex/initial-engineering-skeleton`
**Current HEAD:** `46aaf25 docs: add portfolio experience design baseline`
**Governing principle:** *Evidence before assertion.*

**Goal:** Turn the approved v0.2 visual prototype in `assets/portfolio-experience/` into the final,
recruiter-facing static site — deployed on GitHub Pages, rendering **only** governed values projected
from `artifacts/` and `docs/evidence/`, with every unproven capability shown as an explicit
"Not yet demonstrated" state.

**Architecture (one paragraph):** A deterministic Python generator reads the existing governed
artifacts and emits a small set of static JSON bundles. Those bundles are both (a) committed to disk as
the inspectable governed-evidence layer and (b) injected inline into the site's HTML as
`<script type="application/json">` so the browser renders them **without any network fetch** — which
keeps the page working identically over `file://` and GitHub Pages. The visual layer is the approved
prototype, unchanged; only its data source changes from hard-coded literals to governed JSON, and its
CDN/generated-runtime liabilities are removed. No Node, no framework, no backend, no live inference.

**Tech Stack:** Static HTML + CSS + vanilla JS (approved prototype), Python 3.9 stdlib generator
(`json`, `hashlib`, `string`, `pathlib` — no new dependencies), GitHub Pages via a minimal Actions
Pages workflow, `pytest` for the generator's tests.

---

## Authoritative inputs (normative)

- `docs/plans/KALIBRA_PORTFOLIO_UX_ARCHITECTURE_v1.0.md` — the recruiter experience (journey, stations, hero, honesty convention, free-stack mandate).
- `docs/checkpoints/KALIBRA_PORTFOLIO_UX_STACK_AND_PROTOTYPE_REVIEW_v1.0.md` — the settled stack decision (Option B: static HTML/CSS/JS + bundled JSON), reuse decision, and non-authorizing plan preview.
- `assets/portfolio-experience/` — the **approved** visual baseline (`index.html`, `styles.css`, `app.js`, `README.md`, `screenshots/`). Must not be redesigned.
- `README.md` — repository overview requiring an honesty fix.

Governed data sources the generator reads (read-only):
`artifacts/runtime/integration_metadata.json`, `artifacts/runtime/runtime_replay.json`,
`artifacts/runtime/runtime_hashes.json`, `artifacts/runtime/equivalence/runtime_equivalence_report.json`,
`artifacts/padim/artifact_hashes.json`, `docs/evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md`,
`src/prototype_ui/local_provider_projection.py` output (the approved inspection projection).

---

## 1. Scope

**In scope (this sprint):**

1. A new deployable static site directory `portfolio/` derived from the approved baseline, with the
   same visual experience but rendering from governed JSON.
2. A deterministic Python generator `scripts/build_portfolio_evidence_bundle.py` that projects
   governed artifacts into `portfolio/data/*.json` and injects them inline into `portfolio/index.html`.
3. Removal of the two prototype liabilities the architecture named: (a) any CDN/generated-React
   dependency, (b) any fabricated metric — replaced by governed values or "Not yet demonstrated".
4. A GitHub Pages deployment path (`.github/workflows/pages.yml` + `.nojekyll`).
5. A `pytest` test module for the generator (no-fabrication guard, determinism, `--check` mode).
6. The `README.md` honesty fix (Current Status, maturity, portfolio pointer).
7. Validation: offline/`file://` compatibility, no-external-host audit, value traceability, visual
   regression against the approved screenshots.

**Explicitly out of scope:**

- Any redesign of the approved visuals, layout, palette, typography, spacing, or copy.
- Client-side inference of any kind (prohibited).
- The interactive "switch between representative inputs" idea from architecture §5 — the approved
   prototype renders a single case; adding a switcher is a visual/UX change and is deferred.
- Self-hosting webfonts (approved baseline uses system fallbacks; keeping them satisfies the no-CDN
   rule). Deferred as a future identity-pinning enhancement.
- Any change to `src/`, `artifacts/`, `data/`, ML documentation, or normative docs beyond the README
   honesty fix.
- New governed capabilities (calibration, routing, abstention, drift, review) — these remain
   "Not yet demonstrated".
- Custom domain, analytics, service worker, or PWA features.

---

## 2. Implementation Strategy

**Philosophy.** Evidence before assertion, enforced in the pipeline. The generator may emit only values
that exist in a governed artifact; any field absent from the evidence is rendered as an explicit
"Not yet demonstrated" state, never invented. The site is itself evidence of the offline-reproducible
thesis, so it must render self-contained with no external host in the critical path.

**Architecture.** Three layers:

1. **Governed source** — existing artifacts under `artifacts/`, `docs/evidence/`, and the
   `local_provider_projection.py` output. Read-only.
2. **Projection** — `scripts/build_portfolio_evidence_bundle.py` reads the source and produces the
   static JSON bundles (`portfolio/data/*.json`) with a fixed schema, sorted keys, and deterministic
   formatting.
3. **Presentation** — `portfolio/index.html` (approved markup) + `styles.css` (approved, unchanged) +
   `app.js` (interaction + a small data-bind render pass). The generator injects the bundles inline as
   `<script type="application/json" id="kalibra-data">…</script>` between two marker comments so the
   browser needs no `fetch()`.

**Data flow.**

```
artifacts/*.json ┐
docs/evidence/*  ├─▶ build_portfolio_evidence_bundle.py ─▶ portfolio/data/*.json  (committed, inspectable)
local_provider   ┘                                     └─▶ inline <script type=application/json> in index.html
                                                                     │
                                                          app.js data-bind render pass
                                                                     ▼
                                                        identical-to-approved rendered page
```

**Rendering strategy.** Build-time projection + inline JSON + progressive-enhancement data binding:

- Every governed value in the markup carries a `data-bind="bundle.path"` attribute and a **literal
  fallback** equal to the last generated value. With JS disabled, the literal fallback is shown (page
  stays fully readable — an approved property). With JS enabled, `app.js` parses the inline JSON and
  writes the same governed values into the bound elements.
- Because the literal fallback and the inline JSON are both emitted by the same generator run, there is
  **no manually duplicated value** — the two representations are single-sourced and kept identical by
  the generator and its `--check` mode.
- No client-side `fetch()` (fails on `file://`); no framework; no CDN. `app.js` keeps the approved
  interactions (copy-to-clipboard, smooth scroll, scrollspy, `<details>` disclosure) and adds only the
  render pass.

---

## 3. Repository Structure

Target structure (canonical folders marked **[CANONICAL]**):

```
portfolio/                         [CANONICAL] — the deployable static site
  index.html                       approved markup + data-bind attrs + injected <script type=application/json>
  styles.css                       approved stylesheet, copied verbatim (no visual change)
  app.js                           interaction + data-bind render pass (vanilla, no deps)
  .nojekyll                        disables Jekyll so underscored paths serve as-is on Pages
  data/                            [CANONICAL] — generated governed JSON bundles (committed, inspectable)
    meta.json
    runtime.json
    evaluation.json
    equivalence.json
    evidence.json
    architecture.json
    boundaries.json
    timeline.json
  README.md                        one-page "how this site is generated / how to verify" note

scripts/
  build_portfolio_evidence_bundle.py   [CANONICAL] — the deterministic generator (+ --check mode)

.github/workflows/
  pages.yml                        minimal GitHub Pages deploy (uploads portfolio/ as the Pages artifact)

tests/
  test_build_portfolio_evidence_bundle.py   generator tests (no-fabrication, determinism, --check)

assets/portfolio-experience/       FROZEN approved design reference (NOT deployed)
  index.html styles.css app.js README.md
  screenshots/                     [CANONICAL baseline] — 9 approved screenshots used for visual regression
```

- **HTML:** `portfolio/index.html` (deployed) is derived from `assets/portfolio-experience/index.html`
  (frozen reference).
- **CSS:** `portfolio/styles.css` is a verbatim copy of the approved stylesheet.
- **JS:** `portfolio/app.js` is the approved `app.js` plus the render pass.
- **Generated JSON:** lives only in `portfolio/data/`.
- **Assets:** the two inspection images stay inline `data:` SVG URIs in the markup (approved); no binary
  assets ship with the site. Webfonts remain system fallbacks (no CDN).
- **Screenshots:** the 9 approved PNGs under `assets/portfolio-experience/screenshots/` are the visual
  regression baseline and are **not** copied into the deployed site.

---

## 4. Governed Data Strategy

**Principle:** No duplicated manual values. Every visible number/hash originates from exactly one
governed artifact and is projected by the generator.

**Which governed artifacts become JSON, and the exact mapping:**

| Bundle | Source artifact(s) | Fields projected |
|---|---|---|
| `meta.json` | `artifacts/padim/artifact_hashes.json`, `runtime_replay.json`, git HEAD | model sha256 (`0437ae28…741a`), offline mode, evidence basis qualifier (`Single-seed · VisA-proxy`), review HEAD short sha |
| `runtime.json` | `local_provider_projection.py` output + `runtime_replay.json` (`first_run`) + `integration_metadata.json` | input id/name, class (`candle`), verdict (`DEFECT`), localization region, raw anomaly measure, model identity string, model sha256, input content hash, feature contract id (`kalibra-padim-rgb64-bilinear-float64-patch8-v1`), toolchain pins (`onnxruntime 1.19.2 · numpy 2.0.2 · python 3.9.6`), determinism knobs, session config hash (`2893fd…a2e4`) |
| `evaluation.json` | `docs/evidence/KALIBRA_SCIENTIFIC_EVALUATION_EVIDENCE_v1.0.md` | Image AUROC `0.757826`, Pixel AUROC `0.865196`, AUPRO `0.555765`, per-class P/R/F1 (incl. weakest precision `0.209`), inline qualifier `single-seed, VisA-proxy` |
| `equivalence.json` | `artifacts/runtime/equivalence/runtime_equivalence_report.json` + `runtime_replay.json` | samples compared (`6,492`), max abs deviation (`7.105427357601002e-15`), max rel deviation, atol/rtol (`1e-12`), localization exact (`0.0`), replay comparisons (7 booleans, all `true`), status `passed` |
| `evidence.json` | evidence docs + `integration_metadata.json` hashes | the 7 chain links: claim sentence, status chip (`governed`/`replay`/`verified`/`integrated`/`passed`), labels/paths, copyable hashes |
| `architecture.json` | architecture doc + evidence envelope | 5 domains (name, one-line role, status `real`/`gap`), flow ordering |
| `boundaries.json` | evidence envelope (architecture §8, README boundary) | ordered "Not yet demonstrated" list (calibrated confidence, routing, abstention, drift, review loop, multi-seed, model families, real-time, production), reframe sentence |
| `timeline.json` | checkpoint titles P1/P2/P3 + "next" | phase number, title, subtitle, bullet items, open/closed default, "next" note |

**How JSON is generated:** one entry point, `python scripts/build_portfolio_evidence_bundle.py`.
It reads sources, builds an in-memory dict per bundle, writes each `portfolio/data/<name>.json` with
`json.dump(..., indent=2, sort_keys=True, ensure_ascii=False)` + trailing newline, then injects the
concatenated bundles as an inline JSON `<script>` into `portfolio/index.html` between
`<!-- KALIBRA_DATA:START -->` and `<!-- KALIBRA_DATA:END -->` markers, and writes each governed value
into its literal fallback slot in the markup.

**Where JSON lives:** `portfolio/data/` (committed) and, inlined, inside `portfolio/index.html`.

**How updates occur:** when a governed artifact changes, re-run the generator; the JSON bundles, the
inline block, and the literal fallbacks all regenerate together. `--check` (Section 5) fails CI if the
committed output drifts from a fresh generation, so a stale value cannot be merged.

**No-fabrication rule (enforced in code):** if a required source field is missing or unparseable, the
generator raises and exits non-zero — it never substitutes a default or invents a value. Any capability
without a governed field is emitted only into `boundaries.json` / the "Not yet demonstrated" states.

---

## 5. Static Build Strategy

**Pipeline:** a single Python 3.9 stdlib script, deterministic and reproducible, no Node, no framework.

`scripts/build_portfolio_evidence_bundle.py` supports two modes:

- **generate (default):** `python scripts/build_portfolio_evidence_bundle.py`
  Reads governed sources → writes `portfolio/data/*.json` → injects inline block + literal fallbacks
  into `portfolio/index.html`.
- **check:** `python scripts/build_portfolio_evidence_bundle.py --check`
  Regenerates all outputs into a temp buffer and compares byte-for-byte against the committed files.
  Exit `0` if identical, non-zero with a diff summary otherwise. This is the drift/fabrication guard
  used by tests and CI.

**Determinism requirements:**

- Stable ordering: `sort_keys=True`; ordered lists (chain links, domains, boundaries, timeline phases)
  are built from explicit ordered sequences, never from dict iteration.
- Fixed formatting: `indent=2`, `ensure_ascii=False`, single trailing newline; numbers copied as strings
  where the display form matters (e.g. `"7.105e-15"`, `"6,492"`) so float repr can never drift the page.
- No timestamps, no environment-dependent values in the bundles except the git short SHA, which is read
  from `git rev-parse --short HEAD` and can be overridden by `--review-head <sha>` for reproducible
  builds and tests.
- No network access; the script fails if any source file is missing.

**Reproducibility:** given the same governed artifacts and `--review-head`, byte-identical output.
The `--check` mode makes this a testable invariant.

**No build framework:** templating uses `str.replace` on the two marker regions and `string.Template`
for literal-fallback slots — stdlib only. No Jinja, no bundler, no transpiler.

---

## 6. Frontend Strategy

**Do not redesign UX.** The rendered page must remain visually identical to the approved v0.2 baseline.

**HTML organisation (`portfolio/index.html`):**

- Same nine-station structure and markup as `assets/portfolio-experience/index.html`.
- Each governed value gets `data-bind="bundle.path"` on its existing element; the element keeps its
  current literal text as the fallback.
- A single injected block near end-of-`<body>`:
  `<!-- KALIBRA_DATA:START --><script type="application/json" id="kalibra-data">{…}</script><!-- KALIBRA_DATA:END -->`.

**CSS organisation (`portfolio/styles.css`):** verbatim copy of the approved stylesheet — no new rules,
no token changes. If any class is needed for a bound element, it already exists (Section 7 of the
handoff README lists the component classes).

**JS organisation (`portfolio/app.js`):** the approved interaction script, unchanged, plus one added
render pass at the top of execution:

```
(function render(){
  var el = document.getElementById('kalibra-data');
  if(!el) return;                       // no-JS / missing block → literal fallbacks remain
  var data;
  try { data = JSON.parse(el.textContent); } catch(e){ return; }
  document.querySelectorAll('[data-bind]').forEach(function(node){
    var val = resolve(data, node.getAttribute('data-bind'));   // dotted-path lookup
    if(val != null) node.textContent = String(val);
  });
  // copyable hashes: also refresh the value passed to kcopy() from data-copy attr if present
})();
```

**Interaction model (unchanged from approved):** copy-to-clipboard on `.hashrow` ("verify it yourself"),
smooth scroll from rail + `[data-scroll]`, IntersectionObserver scrollspy, native `<details>`
disclosure. No parallax, no autoplay, no spinner, no fake motion.

**Offline guarantee:** no `fetch`, no CDN, no external font/icon/runtime. The inline JSON is read from
the DOM, so the page renders identically from `file://` and from GitHub Pages.

---

## 7. Runtime Data Model

Every bundle below is emitted to `portfolio/data/<name>.json` and inlined. Display-sensitive numbers are
strings to freeze their rendered form. Schemas (representative fields; all values shown are the real
governed values to be projected):

**`meta.json`**
```json
{
  "model_sha256": "0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a",
  "model_sha256_short": "0437ae28…741a",
  "offline_mode": true,
  "evidence_basis": "Single-seed · VisA-proxy",
  "review_head": "9c8e618"
}
```

**`runtime.json`**
```json
{
  "input": { "name": "blob_defect.pgm", "fixture": "4×4 PGM", "content_hash_short": "8b719296…0da45e", "class_name": "candle" },
  "verdict": "DEFECT",
  "localization": { "x": "0.25–0.75", "y": "0.25–0.75" },
  "raw_anomaly_measure": "75.00",
  "raw_scale_max": "100",
  "model_identity": "kalibra-padim-onnx-export-v1",
  "model_sha256_short": "0437ae28…741a",
  "feature_contract": "…rgb64-bilinear-float64-patch8-v1",
  "toolchain": "onnxruntime 1.19.2 · numpy 2.0.2 · python 3.9.6",
  "determinism": "single-thread · ORT_DISABLE_ALL · CPU EP",
  "session_config_hash_short": "2893fd…a2e4",
  "precomputed_note": "Precomputed from a governed offline run. Kalibra does not run inference in your browser.",
  "trust": { "state": "not_yet_demonstrated", "absent": ["Calibrated confidence", "Outcome routing", "Drift"] }
}
```

**`evaluation.json`**
```json
{
  "metrics": [
    { "name": "Image AUROC", "value": "0.757826", "note": "Detection quality at the image level." },
    { "name": "Pixel AUROC", "value": "0.865196", "note": "Localization quality at the pixel level." },
    { "name": "AUPRO", "value": "0.555765", "note": "Per-region overlap — the harder, more honest measure." }
  ],
  "qualifier": "single-seed, VisA-proxy only",
  "weakest_precision": "0.209"
}
```

**`equivalence.json`**
```json
{
  "samples_compared": "6,492",
  "max_abs_deviation": "7.105e-15",
  "max_abs_deviation_full": "7.105427357601002e-15",
  "atol": "1e-12", "rtol": "1e-12", "localization_exact": "0.0",
  "replay": {
    "status": "passed",
    "comparisons": [
      { "name": "Artifact identity", "value": true },
      { "name": "Predictions", "value": true },
      { "name": "Localization", "value": true },
      { "name": "Raw anomaly measures", "value": true },
      { "name": "Run hash", "value": true },
      { "name": "Session config", "value": true },
      { "name": "Output digest", "value": true }
    ]
  }
}
```

**`evidence.json`**
```json
{ "links": [
  { "n": 1, "claim": "Governed dataset…", "status": "governed", "labels": ["visa-acq-v1", "archive + split SHA-256 in repo"] },
  { "n": 3, "claim": "ONNX export…", "status": "governed", "hash_short": "0437ae28…741a" },
  { "n": 5, "claim": "Runtime equivalence…", "status": "verified", "labels": ["6,492 samples · max dev 7.1e-15"] },
  { "n": 7, "claim": "Deterministic replay + placeholder retirement…", "status": "passed", "labels": ["runtime_replay.json · 7/7 true", "placeholder_used… : false"] }
] }
```
(All seven links present; abbreviated here.)

**`architecture.json`**
```json
{ "domains": [
  { "name": "Inspection Engine", "status": "real", "role": "What the system sees…" },
  { "name": "Trust Qualification", "status": "gap", "role": "How far to trust it… not yet evidenced." },
  { "name": "Human Review", "status": "gap", "role": "Where uncertainty goes… not yet demonstrated." },
  { "name": "Evidence Engine", "status": "real", "role": "What can be inspected…" },
  { "name": "Evaluation Engine", "status": "real", "role": "What the science says…" }
],
  "flow": ["Inspection", "Trust Qualification", "Human Review", "Evidence", "Evaluation"] }
```

**`boundaries.json`**
```json
{ "not_yet_demonstrated": [
  "Calibrated confidence", "Accept / review / reject routing", "Abstention on low confidence",
  "Drift assessment", "Interactive human-review loop", "Multi-seed variance",
  "Multiple model families", "Real-time / on-device inference", "Production / deployment"
],
  "reframe": "A clearly drawn limit is a sign of understanding, not a gap." }
```

**`timeline.json`**
```json
{ "phases": [
  { "id": "P1", "title": "Engineering substrate", "subtitle": "…", "open": false, "items": ["…"] },
  { "id": "P2", "title": "Offline science", "subtitle": "…", "open": true, "items": ["…"] },
  { "id": "P3", "title": "Runtime integration", "subtitle": "…", "open": true, "items": ["…"] }
],
  "next": "Trust qualification — calibration, routing, abstention, drift, human review. Designed, not yet evidenced." }
```

---

## 8. README Update Strategy

Edit `README.md` only. No marketing language, no superlatives; the honest boundary stays visible.

- **Current Status:** replace the stale checklist. `Computer vision implementation` and
  `Evidence-backed evaluation results` are now demonstrated (PaDiM baseline + C-6 evaluation + governed
  ONNX runtime with equivalence and deterministic replay). Reflect ML Phases 2–3 complete, runtime and
  runtime-equivalence complete, placeholder retired. Keep `Calibrated trust qualification` and
  `End-to-end validation` **unchecked** — they are genuinely not yet demonstrated.
- **Project maturity:** state plainly that the offline inspection runtime is implemented and governed,
  and that the trust-qualification layer is designed but not yet evidenced. No "production-ready" claims.
- **Portfolio description:** add a short "Portfolio Experience" section pointing to the deployed
  GitHub Pages URL and the `portfolio/` source, describing it as a static, governed, offline-reproducible
  recruiter surface that renders only governed evidence — one factual sentence, no hype.
- Replace the workbench-prototype image reference only if it is stale; otherwise leave the existing
  prototype section intact.

Suggested Current-Status checklist after the fix:
```
- [x] Engineering foundation documented
- [x] Offline, batch, reproducible system boundary defined
- [x] Five-domain architecture established
- [x] Governed dataset, PaDiM baseline, and C-6 scientific evaluation
- [x] Governed ONNX runtime with export- and runtime-equivalence, deterministic replay
- [ ] Calibrated trust qualification
- [ ] Interactive human review and drift
- [ ] End-to-end validation
```

---

## 9. Validation Strategy

1. **No fake values.** `python scripts/build_portfolio_evidence_bundle.py --check` exits `0`; the
   generator raises on any missing governed field (tested in Section 10's test module).
2. **Governed JSON only.** Every `data-bind` path resolves to a field in a committed
   `portfolio/data/*.json`; a test asserts no bound path is missing and no bundle value is unused.
3. **GitHub Pages compatible.** `.nojekyll` present; `pages.yml` uploads `portfolio/`; no server-side
   logic; all paths relative.
4. **Offline / `file://` compatible.** Open `portfolio/index.html` via `file://` (and a `python -m
   http.server` sanity check); the page renders all governed values with no console error and no network
   request. No `fetch()`; JSON is read from the inline `<script>`.
5. **No external host.** `grep -RniE 'https?://|cdn|fonts\.googleapis|unpkg|jsdelivr|cdnjs' portfolio/`
   returns no dependency in the critical path (only, at most, the repository link in copy).
6. **Visual regression.** Render `portfolio/index.html` and compare against the nine approved
   screenshots in `assets/portfolio-experience/screenshots/`; differences must be nil (data source
   changed, pixels did not). Any diff is a defect to fix, not to accept.
7. **Evidence consistency.** A test cross-checks a sample of projected values (model sha256, AUROC
   trio, max deviation, replay booleans, config hash) directly against their source artifacts.
8. **Repo hygiene.** `git diff --check` clean; `git status --short` shows only the intended new/modified
   files.

---

## 10. Files Created

- `docs/plans/PORTFOLIO_EXPERIENCE_IMPLEMENTATION_PLAN_v1.0.md` (this document)
- `portfolio/index.html`
- `portfolio/styles.css`
- `portfolio/app.js`
- `portfolio/.nojekyll`
- `portfolio/README.md`
- `portfolio/data/meta.json`
- `portfolio/data/runtime.json`
- `portfolio/data/evaluation.json`
- `portfolio/data/equivalence.json`
- `portfolio/data/evidence.json`
- `portfolio/data/architecture.json`
- `portfolio/data/boundaries.json`
- `portfolio/data/timeline.json`
- `scripts/build_portfolio_evidence_bundle.py`
- `tests/test_build_portfolio_evidence_bundle.py`
- `.github/workflows/pages.yml`

---

## 11. Files Modified

- `README.md` — Current Status / maturity / portfolio pointer honesty fix (Section 8).

No other file is modified. (If, during execution, GitHub Pages requires a repository-settings change,
that is a settings action, not a file edit, and is captured in Section 16 as a manual step.)

---

## 12. Files Explicitly Untouched

Protected — read-only for this sprint:

- `src/` — including `src/prototype_ui/local_provider_projection.py` (read its **output**, do not modify).
- `artifacts/` — all governed runtime and PaDiM artifacts.
- `data/` — governed VisA archive, manifests, derived PaDiM statistics.
- `docs/` normative documents, ADRs, checkpoints, evidence, and all **ML documentation** (the portfolio
  *links to* them; it does not modify them). The only `docs/` write is this plan file.
- `assets/portfolio-experience/` — the **frozen approved design reference** (kept as the source of
  visual identity; not the deployed site). Not edited, not deleted.
- `assets/KALIBRA_WORKBENCH_PROTOTYPE_v1.0.png` and other existing assets.
- `AGENTS.md`, `LICENSE`, existing `scripts/*` and existing `tests/*`.

---

## 13. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | `fetch()` over `file://` fails, breaking the offline guarantee | High | Do not use `fetch`; inline JSON as `<script type=application/json>` read from the DOM. Validated by the `file://` open test (§9.4). |
| 2 | A projected value drifts from its governed source, or a value is fabricated | High | Generator raises on missing fields; `--check` byte-compares committed output; tests cross-check sampled values against sources (§9.1, §9.7). |
| 3 | GitHub Pages Jekyll mangles `data/`/underscored paths | Medium | Ship `portfolio/.nojekyll`; deploy the whole directory as a Pages artifact via `pages.yml`. |
| 4 | Accidental visual redesign while rewiring data | Medium | `styles.css` copied verbatim; markup diff limited to `data-bind` attrs + marker block; visual regression vs the nine approved screenshots (§9.6). |
| 5 | A CDN/generated-runtime dependency re-enters the page | Medium | No-external-host grep (§9.5); the approved baseline already has none — do not reintroduce. |
| 6 | Pages workflow pulls in a Node/framework build | Medium | `pages.yml` only uploads static files (`actions/upload-pages-artifact` + `deploy-pages`); no build job, no npm. |
| 7 | README honesty fix overclaims completeness | Low | Keep trust/calibration/validation unchecked; plain engineering voice; reviewed against the evidence envelope. |
| 8 | Duplicate value between literal fallback and inline JSON drifts | Low | Both emitted by the same generator run; `--check` fails if they diverge. |

---

## 14. Success Criteria

1. `portfolio/index.html` renders **visually identical** to the approved v0.2 baseline (nil screenshot
   diff).
2. Every visible metric/hash traces to a governed artifact; nothing is fabricated; every absence uses the
   "Not yet demonstrated" convention.
3. `python scripts/build_portfolio_evidence_bundle.py --check` exits `0`.
4. `pytest tests/test_build_portfolio_evidence_bundle.py` passes.
5. The page renders fully over `file://` with zero network requests and zero console errors.
6. No external host appears in the critical path (§9.5 grep clean).
7. The site deploys to GitHub Pages from `portfolio/` and is reachable at the Pages URL.
8. `README.md` Current Status is honest and current; no marketing language.
9. `git diff --check` clean; `git status --short` shows only the files in Sections 10–11.

---

## 15. Post-Implementation Review Strategy

Checklist for the review checkpoint before merge/authorization:

- [ ] Screenshot diff vs the nine approved baselines is nil (desktop + `max-width:1120px` mobile
      breakpoint).
- [ ] `--check` and `pytest` both green; CI (if wired) green.
- [ ] Manual `file://` open: all stations show governed values; copy-to-clipboard, scrollspy, and
      `<details>` work; no console error.
- [ ] No-external-host grep clean; DevTools Network shows zero third-party requests.
- [ ] Spot-check five governed values (model sha256, Image AUROC, max deviation, one replay boolean,
      session config hash) against their source artifacts by hand.
- [ ] Every "Not yet demonstrated" state present and correctly styled (`.nyd`, `.st.gap`, `.nyd-item`).
- [ ] `README.md` reads honestly; unchecked items are genuinely unbuilt.
- [ ] `git diff --check` / `git status --short` show only intended files.
- [ ] Persist a completion checkpoint in `docs/checkpoints/` **before** updating any normative doc
      (per the checkpoint-persistence workflow).

---

## 16. Next Natural Steps (implementation sequence — do not implement now)

Ordered, bite-sized tasks. Each names exact files and a verify command.

**Task 1 — Scaffold the deployable site from the approved baseline.**
- [ ] Copy `assets/portfolio-experience/{index.html,styles.css,app.js}` → `portfolio/`.
- [ ] Add `portfolio/.nojekyll` (empty) and `portfolio/README.md` (generation + verify note).
- [ ] Verify: `diff assets/portfolio-experience/styles.css portfolio/styles.css` → identical.

**Task 2 — Annotate the markup for binding.**
- [ ] In `portfolio/index.html`, add `data-bind="bundle.path"` to every governed value element, keeping
      existing literal text as fallback; insert the `<!-- KALIBRA_DATA:START/END -->` marker block
      before `<script src="app.js">`.
- [ ] Verify: `python -m http.server -d portfolio 8080` then load `http://localhost:8080` → unchanged.

**Task 3 — Write the generator (TDD).**
- [ ] Create `tests/test_build_portfolio_evidence_bundle.py`: assert (a) each bundle has its required
      fields, (b) sampled values equal their source-artifact values, (c) a missing source field raises,
      (d) `--check` passes after generate and fails after a manual edit.
- [ ] Run: `pytest tests/test_build_portfolio_evidence_bundle.py -v` → FAIL (module absent).
- [ ] Create `scripts/build_portfolio_evidence_bundle.py` with `generate` + `--check` + `--review-head`.
- [ ] Run: `pytest tests/test_build_portfolio_evidence_bundle.py -v` → PASS.

**Task 4 — Generate and wire the data.**
- [ ] Run: `python scripts/build_portfolio_evidence_bundle.py --review-head 9c8e618` → writes
      `portfolio/data/*.json` and injects the inline block + literal fallbacks.
- [ ] Add the render pass to `portfolio/app.js` (Section 6).
- [ ] Verify: `python scripts/build_portfolio_evidence_bundle.py --check` → exit `0`.

**Task 5 — Offline + no-external-host validation.**
- [ ] Open `portfolio/index.html` via `file://`; confirm governed values render, no console error.
- [ ] Run: `grep -RniE 'https?://|cdn|fonts\.googleapis|unpkg|jsdelivr|cdnjs' portfolio/` → clean.

**Task 6 — Visual regression.**
- [ ] Screenshot each station; compare to `assets/portfolio-experience/screenshots/*`; diff nil.

**Task 7 — GitHub Pages deploy.**
- [ ] Create `.github/workflows/pages.yml` (upload `portfolio/` via `actions/upload-pages-artifact` +
      `actions/deploy-pages`; no build job).
- [ ] Manual: enable Pages (Source = GitHub Actions) in repo settings; record the Pages URL.

**Task 8 — README honesty fix.**
- [ ] Edit `README.md` per Section 8; add the Portfolio Experience section with the Pages URL.

**Task 9 — Final validation + checkpoint.**
- [ ] Run `--check`, `pytest`, no-host grep, `git diff --check`, `git status --short`.
- [ ] Persist a completion checkpoint in `docs/checkpoints/` before touching any normative doc.

**Commit granularity:** one commit per task (Tasks 1–2 may share one). Frequent, small commits.

---

**Next natural step:** Review this implementation plan before opening the Portfolio Experience
implementation authorization.
