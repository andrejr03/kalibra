# Kalibra README Improvement Plan v1.0

**Plan type:** Recruiter-facing communication plan  
**Scope:** `README.md` presentation only  
**Primary audience:** AI/ML, Data Science, and Computer Vision Werkstudent recruiters; University of Passau professors; research supervisors  
**Objective:** Make Kalibra understandable, credible, memorable, and reproducible within a recruiter's first two to three minutes without expanding any scientific claim.

## 1. Executive Decision

The README should stop opening as a project vision and start opening as evidence of work André Ramos has already completed.

The first scan must establish five facts in this order:

1. Kalibra is a governed, offline computer-vision engineering project.
2. It carries a real PaDiM anomaly signal through an ONNX runtime.
3. Runtime equivalence was verified across 6,492 samples, with a maximum absolute deviation of `7.105e-15` against a `1e-12` tolerance.
4. Deterministic replay passed all 7 governed comparisons.
5. It was designed and built by André Ramos, and calibrated confidence, routing, drift handling, and interactive review are not yet demonstrated.

This framing makes the implemented runtime the memorable signal and makes the unimplemented trust layer an explicit boundary rather than a buried disclaimer.

## 2. Recruiter Communication Target

### What recruiters should notice

- André's ownership in the first scan.
- A real computer-vision and ONNX engineering stack, not generic “AI” language.
- A governed dataset-to-runtime evidence chain.
- A quantified equivalence result and deterministic replay.
- A copy-paste verification path.
- Clear separation between implemented runtime evidence and future trust-qualification work.

### What recruiters should remember

> André built a governed visual-anomaly runtime and proved that its integrated ONNX path preserves the validated signal to machine precision, while stating exactly what the project does not yet prove.

### What the README should stop asking recruiters to process

- Vision and philosophy before concrete evidence.
- Nine consecutive screenshots.
- Repeated maturity and status explanations.
- Equal visual weight for implemented and proposed functionality.
- Repository descriptions that omit `src/`, `tests/`, `scripts/`, and governed artifacts.

## 3. Final README Information Architecture

The target README should use the following order. Approximate lengths are limits, not targets to fill.

| Order | Section title | Purpose | Approximate length | Decision | Content direction |
|---:|---|---|---|---|---|
| 1 | `# Kalibra` | Preserve the short, memorable project identity. | 1 line | **KEEP** | Do not add a long product-style name to the H1. |
| 2 | Unheaded subtitle | State the implemented technical category immediately. | 1 line; 8–14 words | **SHORTEN / REPLACE** | Use concrete language such as “A governed, reproducible visual-inspection runtime for industrial anomaly detection.” Remove “Self-Evaluating” and “Calibrated Uncertainty” from the subtitle because those capabilities are not yet demonstrated. |
| 3 | Opening description | Explain what exists, how it works at a high level, and why it is distinctive. | 45–65 words; one compact paragraph | **SHORTEN / REPLACE** | Name the offline boundary, PaDiM, governed VisA proxy, ONNX Runtime, evidence provenance, and deterministic verification. End with the single-seed/proxy boundary rather than a broad trust claim. |
| 4 | Authorship byline | Make André's ownership unmistakable before the reader scrolls. | 1 line | **ADD / MOVE TO TOP** | Use: `Designed and built by [André Ramos](https://github.com/andrejr03) as an AI/ML engineering portfolio project.` Keep it factual; do not add seniority or team claims. |
| 5 | `## What This Project Demonstrates` | Surface the strongest recruiter signals before background material. | 3–4 bullets; 55–80 words total | **ADD / MOVE EVIDENCE UP** | Lead with runtime equivalence and deterministic replay, then the governed dataset-to-runtime chain, then the explicit scientific boundary. Each bullet should point to evidence where practical. |
| 6 | `## Technology Stack` | Let technical reviewers classify role fit in seconds. | 1 compact line or 2 short rows; 20–35 words | **ADD** | List only evidenced technologies: Python 3.9, NumPy, Pillow, PaDiM, ONNX, ONNX Runtime, pytest, and the HTML/CSS/vanilla JavaScript portfolio. Name VisA separately as the governed proxy dataset, not as a technology. Do not list PyTorch, OpenCV, Streamlit, cloud infrastructure, or deployment technologies not used by the repository. |
| 7 | `## Quick Verification` | Give a clean-clone, copy-paste proof path near the top. | 1 sentence, one 4-line command block, 1 expected-result line | **ADD** | Use the dependency-light verification block in Section 5. Call it verification, not full reproduction. Link deeper runtime replay documentation after the block. |
| 8 | `## Current Status` | Separate demonstrated functionality from designed but unevidenced work. | 90–130 words plus two short lists | **MOVE UP / MERGE / SHORTEN** | Merge the current `Current Status` and `Project Maturity` sections. Use two labels: `Implemented and evidenced` and `Designed, not yet demonstrated`. Retain the offline, batch, single-seed, VisA-proxy, non-production boundary. |
| 9 | `## Portfolio Experience` | Show polish and make the evidence approachable without turning the README into a gallery. | 45–70 words plus exactly 3 visible screenshots and one link | **KEEP / SHORTEN** | Describe it as a static, offline presentation of committed evidence—not live inference. Use the three-image sequence in Section 6. Link the GitHub Pages experience only after the URL has been verified; until then, state that `portfolio/` contains the deployable static experience. |
| 10 | `## Engineering Domains` | Show architectural thinking and the implementation boundary in one scan. | 5-row table; no introductory essay | **KEEP / SHORTEN / REFORMAT** | Use columns `Domain`, `Status`, and `Evidence or next step`. Mark Inspection, Evidence, and Evaluation as implemented/evidenced; Trust Qualification and Human Review as designed/not yet evidenced. |
| 11 | `## Repository Structure` | Prove that the repository contains implementation, verification, and evidence—not only documentation. | 7–8 rows; 55–85 words | **KEEP / REFOCUS** | Include `src/`, `scripts/`, `tests/`, `artifacts/`, tracked `data/` manifests/results, `docs/`, `portfolio/`, and `assets/`. Put `src/`, `scripts/`, and `tests/` first. Remove the self-referential `README.md` row. |
| 12 | `## Roadmap` | State the next scientific/engineering steps without making the current project look unfinished. | 3 bullets; 40–65 words | **KEEP / SHORTEN** | Order future work as trust calibration and qualification; accept/review/reject plus abstention and human-review routing; drift and end-to-end validation. Label all as future work. Do not repeat completed foundation work. |
| 13 | `## Future Concept: Workbench Prototype (Not Implemented)` | Preserve the design concept while preventing it from being mistaken for the current system. | 25–45 visible words; image and detail inside collapsed disclosure | **MOVE LOWER / RENAME / COLLAPSE** | Place after Roadmap and before License. Use the exact treatment in Section 7. Never call it the “official” workbench. |
| 14 | `## License` | Close with the legal status. | 1 sentence | **KEEP** | Retain the MIT statement and `LICENSE` link. |

## 4. Existing Sections to Merge or Remove

| Current section | Decision | Destination and rationale |
|---|---|---|
| `Project Vision` | **MERGE / REMOVE AS A STANDALONE SECTION** | Reduce its two-question thesis to one sentence in the opening description. It is meaningful but too abstract to lead the README. |
| `Engineering Philosophy` | **MERGE / REMOVE AS A STANDALONE SECTION** | Move evidence-before-assertion into `What This Project Demonstrates` and the honesty boundary in `Current Status`. Recruiters need proof before philosophy. |
| `Project Maturity` | **MERGE** | Combine with `Current Status` to eliminate repetition and make implemented versus absent capabilities directly comparable. |
| Current status checklist | **SHORTEN / REPLACE** | Replace the long mixed checklist with two compact lists: demonstrated now and not yet demonstrated. |
| Nine-image gallery text | **SHORTEN** | Replace nine repetitive “station showing” captions with three captions that explain recruiter value: overview, strongest engineering proof, scientific boundaries. |

## 5. First Screen Strategy

### Exact ordering

1. `# Kalibra`
2. Concrete, implemented-state subtitle.
3. One-paragraph opening description.
4. `Designed and built by André Ramos…` byline.
5. `What This Project Demonstrates` with the quantified runtime-equivalence result first and deterministic replay second.
6. Compact technology stack.
7. `Quick Verification` command block.

Do not place a badge, architecture description, roadmap, large screenshot, or workbench concept before this sequence is complete.

### Inclusion decisions

| Element | Include in the top block? | Decision |
|---|---|---|
| What this project demonstrates | **Yes** | It converts an abstract idea into recruiter-readable proof. |
| Technology stack | **Yes** | It establishes AI/ML/CV role fit without requiring source inspection. |
| Built by André Ramos | **Yes** | Put directly after the opening, not in acknowledgements or the footer. |
| Runtime equivalence | **Yes** | It is the first proof bullet and the strongest engineering achievement. |
| Deterministic replay | **Yes** | It is the second proof bullet and differentiates the repository from a conventional model demo. |
| Quick start / verification | **Yes** | It is the last element of the compact top block, before status and screenshots. |

### Recommended top-level proof language

Use a bounded claim equivalent to:

> Runtime equivalence verified across 6,492 samples: maximum absolute deviation `7.105e-15` against a `1e-12` tolerance; deterministic replay passed all 7 governed comparisons.

Do not shorten this to “production-grade,” “fully reproducible,” “trustworthy predictions,” or “self-evaluating.” Runtime equivalence proves preservation of the validated signal through the integrated runtime; it does not prove calibrated confidence, production readiness, or domain-of-record performance.

### Copy-paste Quick Verification block

Recommend this exact clean-clone block:

```bash
git clone https://github.com/andrejr03/kalibra.git
cd kalibra
python3 scripts/build_portfolio_evidence_bundle.py --check
python3 -c "from hashlib import sha256; from pathlib import Path; expected='0437ae28e172489387da07c4bd1f0c6b1ed95f3970ca3c7fa1dcd55935bd741a'; actual=sha256(Path('artifacts/padim/model.onnx').read_bytes()).hexdigest(); assert actual == expected, actual; print('model hash verified')"
```

Expected result: the bundle check exits successfully with no drift and the final command prints `model hash verified`.

This block is intentionally called **Quick Verification**, not **Run Kalibra** or **Reproduce the full experiment**. A public clone does not contain the ignored VisA source/extracted bytes or the full local inference records required by the governed runtime-equivalence replay, and the repository has no public dependency manifest. The README must not imply that the full 6,492-sample replay is a clean-clone one-command workflow. Link `docs/evidence/RUNTIME_EQUIVALENCE.md` and `docs/evidence/RUNTIME_PROVIDER_INTEGRATION.md` for the recorded full verification.

## 6. Screenshot Strategy

### Recruiter-optimal visible sequence

Keep exactly three portfolio screenshots visible in the README, in this order:

1. `hero.png` — establishes identity, visual finish, offline scope, and the headline runtime result.
2. `runtime-equivalence.png` — proves the strongest engineering achievement with sample count, tolerance, maximum deviation, and replay status.
3. `scientific-boundaries.png` — proves scientific honesty by showing bounded metrics, weak results, and absent capabilities.

This sequence tells a complete recruiter story: **finished artifact → hard engineering proof → honest scientific boundary**. Use one sentence per caption. Do not repeat the full station descriptions.

### Evaluation of every existing README image

`REMOVE` below means remove from the README presentation, not delete the asset from the repository.

| Image | Recommendation | README placement | Reason |
|---|---|---|---|
| `assets/portfolio-experience/screenshots/hero.png` | **KEEP** | First image in `Portfolio Experience` | Best first visual summary and strongest polish signal. Caption it as a static evidence overview, not a live application. |
| `assets/portfolio-experience/screenshots/runtime-inspection.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | The governed decision is useful in the interactive sequence, but the screenshot is dense and repeats implemented/not-implemented distinctions already stated in text. |
| `assets/portfolio-experience/screenshots/evidence-chain.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | Strong technical detail but too text-heavy at GitHub README scale. Link the live portfolio and evidence docs instead. |
| `assets/portfolio-experience/screenshots/runtime-equivalence.png` | **KEEP** | Second image in `Portfolio Experience` | The clearest visual proof of the repository's most memorable engineering result. |
| `assets/portfolio-experience/screenshots/architecture.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | The proposed five-row Engineering Domains table communicates the same status boundary faster and accessibly. |
| `assets/portfolio-experience/screenshots/why-trust-this-result.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | Its demonstrated/not-demonstrated split is valuable but duplicated by `Current Status` and the boundaries image. |
| `assets/portfolio-experience/screenshots/scientific-boundaries.png` | **KEEP** | Third image in `Portfolio Experience` | Especially valuable for professors and research supervisors; it shows metrics, limitations, and absent claims together. |
| `assets/portfolio-experience/screenshots/engineering-timeline.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | Build history is lower-priority than present capability during a two-minute recruiter scan. |
| `assets/portfolio-experience/screenshots/repository-verify.png` | **MOVE TO LIVE PORTFOLIO ONLY** | No README image | A real copy-paste verification block is more useful and accessible than a screenshot of terminal commands. |
| `assets/kalibra-workbench-prototype.png` | **MOVE LOWER / COLLAPSE** | Collapsed future-concept section after Roadmap | Visually compelling but depicts calibration, routing, drift, and review capabilities that are not implemented. It must never sit beside implemented portfolio screenshots without an explicit distinction. |

### Screenshot presentation rules

- Maximum visible screenshot count: **3**.
- Use the same width and a one-sentence caption for each.
- Do not use “dashboard,” “live demo,” or “interactive runtime” for the static portfolio.
- State once that the portfolio reads committed governed artifacts, does not run browser inference, and makes no network request.
- If GitHub Pages is not enabled and checked, do not publish a dead live-demo link.
- Keep all nine stations available through the portfolio experience; the README is an attention filter, not an inventory.

## 7. Workbench Strategy

### Decision

**Keep the asset, move it below Roadmap, rename the section, and collapse the image inside `<details>`.**

The workbench is useful evidence of product and interface thinking, but it is currently the highest presentation risk because it shows calibrated confidence, accept/review/reject routing, drift, and human review as if they already exist. Removing it entirely would discard a useful portfolio signal; leaving it visible beside implemented functionality would weaken scientific honesty.

### Required treatment

Use the heading:

```markdown
## Future Concept: Workbench Prototype (Not Implemented)
```

The visible sentence above the disclosure should state:

> This design concept explores the intended review surface; the calibrated confidence, routing, drift, and human-review capabilities shown here are not implemented or evidenced in the current runtime.

Then use a collapsed disclosure:

```html
<details>
<summary>View the future workbench concept</summary>

![Future Kalibra workbench concept](assets/kalibra-workbench-prototype.png)

Concept only: the interface visualizes intended trust qualification and review workflows that are not implemented in the current runtime.

</details>
```

Remove “Official Kalibra Workbench prototype.” “Official” implies a current product surface and adds no recruiter value. The section must appear after the factual Roadmap so readers encounter it only after the implemented boundary is clear.

## 8. Scientific Honesty Rules

The README revision must preserve these qualifiers wherever the corresponding claim appears:

| Claim area | Required qualifier |
|---|---|
| Dataset | VisA is a governed **proxy dataset**, not the industrial domain of record. |
| Evaluation | Results are **single-seed** and must not be presented as generalized or state of the art. |
| Runtime equivalence | Equivalence shows the integrated runtime preserved the validated offline signal within the declared tolerance; it is not an accuracy, calibration, or production claim. |
| Deterministic replay | State the bounded result as **7/7 governed comparisons byte-identical**; do not generalize it to arbitrary hardware or environments. |
| Trust qualification | Calibrated confidence, accept/review/reject routing, abstention, drift assessment, and interactive human review are **not yet demonstrated**. |
| Portfolio | The portfolio is a static presentation generated from governed artifacts; it does not run inference. |
| Production | Kalibra is offline, batch, locally governed, and not production-ready or a hosted service. |
| Workbench | The workbench is a future design concept and does not represent the implemented runtime. |

Avoid the phrases `production-grade`, `end-to-end trustworthy AI`, `calibrated uncertainty` as a current capability, `real-time`, `live inference`, `industrial-grade accuracy`, and `fully reproducible from a clean clone`.

## 9. Content Compression Rules

- Target README length: approximately **110–150 rendered lines excluding image markup**, shorter than the current document despite adding stack, authorship, and verification.
- Use no more than four bullets in any top-level section except Repository Structure.
- Explain a limitation once in `Current Status`; link to evidence rather than repeating it under every screenshot.
- Prefer concrete nouns and results: `PaDiM`, `VisA proxy`, `ONNX Runtime`, `6,492 samples`, `7.105e-15`, `7/7 comparisons`.
- Keep only one high-level thesis sentence about trustworthy visual inspection.
- Use tables only where they accelerate comparison: Engineering Domains and Repository Structure.
- Do not add badges, vanity metrics, long architecture prose, acknowledgements, or a table of contents.

## 10. Acceptance Criteria for the README Revision

The future README implementation is ready for review when all of the following are true:

- André Ramos is named before the first screenshot.
- The top block names the actual stack and strongest quantified runtime result.
- A clean-clone reader can copy and run the Quick Verification block as written.
- The block is not described as full experiment or runtime reproduction.
- `Current Status` distinguishes implemented/evidenced from designed/not demonstrated.
- Only `hero.png`, `runtime-equivalence.png`, and `scientific-boundaries.png` remain visibly embedded from the portfolio sequence.
- The workbench image is below Roadmap, collapsed, and labeled not implemented before expansion.
- The README states that the portfolio is static and does not run inference.
- The single-seed and VisA-proxy boundaries remain visible.
- Runtime equivalence is not presented as calibrated confidence, predictive accuracy, production readiness, or cross-domain validity.
- All local links, image paths, and any GitHub Pages link resolve in the rendered GitHub README.
- No repository implementation, tests, evidence, artifacts, or portfolio files are modified as part of the README edit.

## 11. Final Recommendation

**Show after targeted README edits.**

The implementation already provides a strong interview signal. The highest-payoff change is to make the first screen say, in concrete terms, what André built and proved; the second is to reduce the visible gallery to the three images that establish finish, engineering rigor, and scientific honesty.

The next natural step is to review this communication plan before rewriting `README.md`.
