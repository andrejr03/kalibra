# Kalibra Portfolio Experience Implementation Review v1.0

**Status:** Implementation review persisted.  
**Date:** 2026-07-08  
**Branch:** `codex/initial-engineering-skeleton`  
**Reviewed HEAD:** `410a81f` (`feat: implement portfolio experience`)  
**Decision:** `FAIL`

## Scope

Reviewed:

- `portfolio/`
- `scripts/build_portfolio_evidence_bundle.py`
- `tests/test_build_portfolio_evidence_bundle.py`
- `.github/workflows/pages.yml`
- `README.md`

Reviewed against:

- `docs/plans/PORTFOLIO_EXPERIENCE_IMPLEMENTATION_PLAN_v1.0.md`
- `docs/plans/KALIBRA_PORTFOLIO_UX_ARCHITECTURE_v1.0.md`
- `assets/portfolio-experience/`

This review did not modify implementation files.

## Findings by Severity

### Critical

None.

### High

1. The committed generated portfolio bundle is stale relative to the reviewed HEAD, so the mandatory generator check fails.

   Evidence:

   - Current HEAD is `410a81f`.
   - `portfolio/data/meta.json` still records `"review_head": "6cd5d5e"`.
   - `portfolio/index.html` displays and inlines the same stale `review_head` value.
   - `python3 scripts/build_portfolio_evidence_bundle.py --check` exits non-zero and reports drift in `portfolio/data/meta.json` and `portfolio/index.html`, with generated output expecting `410a81f`.

   Impact:

   - The implementation does not satisfy the governed-data freshness requirement.
   - The Pages workflow's `Verify governed portfolio bundle` step would fail at the reviewed commit.
   - The visible Repository / Verify station points reviewers to a stale review HEAD.

### Medium

None.

### Low

1. Browser validation over a local static HTTP server reports a missing `favicon.ico`.

   Evidence:

   - Playwright console output reported `Failed to load resource: the server responded with a status of 404 (File not found) @ http://127.0.0.1:8765/favicon.ico:0`.
   - Static requests otherwise loaded only `index.html`, `styles.css`, and `app.js` from localhost.

   Impact:

   - This does not affect portfolio functionality or governed claims.
   - It does leave the implementation short of the plan's stricter "zero console error" validation expectation.

### Positive Observations

- `portfolio/styles.css` is byte-identical to `assets/portfolio-experience/styles.css`, preserving the approved visual styling baseline.
- `portfolio/app.js` preserves the approved interaction script and adds only the governed data-bind render pass plus regenerated copy values.
- The rendered station structure matches the required nine stations: Hero, Runtime Inspection, Evidence Chain, Runtime Equivalence, Architecture, Why Trust This Result, Scientific Boundaries, Engineering Timeline, and Repository / Verify.
- The site is static HTML, CSS, and vanilla JavaScript with inline JSON; no framework, backend, authentication, live inference, or CDN dependency was introduced.
- The generator reads governed artifacts and fails on missing required fields.
- Tests cover sampled source traceability, missing-source failure, bind-path resolution, determinism, and `--check` drift detection.
- The README update keeps trust qualification, calibrated confidence, routing, drift, and human review explicitly unevidenced.
- The implementation scope did not modify `src/`, `data/`, `artifacts/`, or ML runtime files.

## Portfolio UX Assessment

The implemented site substantially reproduces the approved visual baseline and station structure:

- Hero: present, evidence-first, no confidence or production claim.
- Runtime Inspection: present, raw anomaly measure separated from trust qualification.
- Evidence Chain: present, provenance-oriented and hash-copyable.
- Runtime Equivalence: present, sample count, deviation, tolerance, and replay status visible.
- Architecture: present, five-domain flow with real and not-yet-demonstrated states.
- Why Trust This Result: present, separates demonstrated evidence from absent trust features.
- Scientific Boundaries: present, metrics qualified as single-seed, VisA-proxy only.
- Engineering Timeline: present, governed build history shown.
- Repository / Verify: present, but includes the stale review HEAD noted in the High finding.

No visual redesign was found. The stale review-head value is evidence drift, not a layout redesign.

## Governed Data Assessment

The governed-data architecture is sound but the committed output is not current.

- Displayed metrics and hashes are projected from governed artifacts or explicit not-yet-demonstrated states.
- No fabricated calibrated confidence, drift, review, or production capability was found.
- The JSON generator is deterministic when a fixed `--review-head` is supplied.
- `--check` correctly detects drift, but because committed output is stale, the required check fails at the reviewed HEAD.

## Static Architecture Assessment

Verified:

- GitHub Pages workflow uploads `portfolio/` as a static Pages artifact.
- `portfolio/.nojekyll` is present.
- The site uses relative `styles.css` and `app.js` paths.
- The data bundle is inline JSON; no `fetch()` is used.
- No CDN, framework, backend, authentication, or live inference path was found.
- Browser HTTP sanity check loaded local `index.html`, `styles.css`, and `app.js` only.

`file://` compatibility is supported by static inspection of relative local assets and inline JSON. Browser-level `file://` navigation could not be performed through the available Playwright wrapper because it blocks the `file:` protocol.

## Engineering Assessment

- Generator architecture: appropriate for the stated scope; reads governed sources, builds explicit bundles, writes deterministic JSON, injects inline JSON, and regenerates fallback text and copy values.
- JSON schema: compact and aligned to the plan's required bundles.
- Rendering strategy: progressive enhancement over literal fallbacks; no network fetch required.
- README update: honest about current maturity and absent trust-qualification capabilities.
- Deployment workflow: simple Pages deployment, but currently blocked by the failing `--check` step.
- Tests: relevant and passing, including determinism and drift detection.

## Git / Repository Assessment

- Latest commit changes are limited to the intended portfolio, generator, test, workflow, README, and completion checkpoint scope.
- `git diff --name-only HEAD^..HEAD -- src data artifacts` returned no files.
- Frozen baseline under `assets/portfolio-experience/` was preserved.
- No ML runtime files were modified.

## Validation Summary

Commands run:

```bash
python3 scripts/build_portfolio_evidence_bundle.py --check
python3 -m pytest -q
python3 -m compileall -q src tests scripts
git diff --check
git status --short
find portfolio -type f | sort
```

Results:

- `python3 scripts/build_portfolio_evidence_bundle.py --check`: FAIL. Drift detected in `portfolio/data/meta.json` and `portfolio/index.html`; generated `review_head` is `410a81f`, committed value is `6cd5d5e`.
- `python3 -m pytest -q`: PASS, `509 passed in 11.70s`.
- `python3 -m compileall -q src tests scripts`: PASS.
- `git diff --check`: PASS.
- Initial `git status --short`: clean before this review checkpoint was created.
- `find portfolio -type f | sort`: returned the expected static portfolio files.
- Static HTTP browser sanity check: loaded page and all nine stations; local requests were `index.html`, `styles.css`, and `app.js`; console reported a missing `favicon.ico`.

## Explicit Non-Claims

Confirmed:

- No trust qualification is implemented or claimed.
- No calibration is implemented or claimed.
- No drift assessment is implemented or claimed.
- No interactive review engine is implemented or claimed.
- No fabricated capabilities were found.
- No scientific overclaim was found; metrics remain qualified as single-seed, VisA-proxy evidence.

## Commit Decision

The implementation is not approved at this review gate.

The primary blocker is generated evidence drift: the committed portfolio bundle does not match the reviewed HEAD, and the required `--check` validation fails. Closure is not authorized.

## Next Natural Step

Review the persisted Portfolio Experience Implementation Review before opening the Portfolio Experience Closure Review.
