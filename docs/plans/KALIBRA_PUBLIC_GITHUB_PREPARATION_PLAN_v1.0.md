# Kalibra — Public GitHub Preparation Plan v1.0

**Status:** Plan only — no files moved, deleted, modified, sanitized, archived, committed, or pushed.
**Date:** 2026-07-08
**Branch:** `codex/initial-engineering-skeleton`
**Repository HEAD Observed:** `3f6ff98`
**Repository:** `/Users/agentisstudio/Documents/kalibra`
**Private archive destination:** `/Users/agentisstudio/Documents/andre-projects/kalibra-private/`

## 0. Purpose and Boundaries

This plan defines how to prepare Kalibra for its final public GitHub
publication. The end state is three things at once:

1. a clean, recruiter-friendly **public repository**;
2. a complete **private engineering archive** at the destination above;
3. **zero loss of engineering history** or traceability.

This document is planning only. It does not authorize any file move, deletion,
rename, sanitization, archival, commit, or push. Execution is authorized in a
later, separate step after this plan is reviewed.

### Observed repository facts (basis for this plan)

- Git tracks **316 files**. `data/` on disk is ~3.9 GB but almost entirely
  git-ignored; only **50 governed JSON files** under `data/visa/derived/padim/**`
  are tracked. Tracked-file distribution by top directory:
  `docs` 92, `data` 50, `src` 47, `assets` 43, `tests` 34, `artifacts` 17,
  `scripts` 13, `portfolio` 13, plus `tools`, `output`, `README.md`, `LICENSE`,
  `AGENTS.md`, `.gitignore`, `.github`.
- `docs/` tracked content: **41 top-level normative/plan `*.md`**,
  `docs/checkpoints/` **33 files**, `docs/plans/` **2 files**,
  `docs/evidence/` **11 files** (+ `prototype-ui/` screenshots),
  `docs/research/` **3 files**.
- Internal-workflow vocabulary is concentrated in `docs/checkpoints/`,
  `docs/plans/`, several top-level `docs/*.md`, and `AGENTS.md`.
- The token "Codex" appears in **35 tracked files**, but it is almost entirely
  the **git branch name** `codex/initial-engineering-skeleton`, not a reference
  to any external tool. This must not be mistaken for tool leakage.
- Absolute local paths (`/Users/agentisstudio/Documents/kalibra/...`) are baked
  into tracked governed artifacts (`artifacts/runtime/integration_metadata.json`,
  `artifacts/runtime/runtime_replay.json`,
  `artifacts/runtime/equivalence/runtime_equivalence_report.json`) and two docs
  (`docs/checkpoints/KALIBRA_C5_...CHECKPOINT_v1.0.md`,
  `docs/evidence/KALIBRA_REAL_ONNX_RUNTIME_EVIDENCE_SPRINT_1F_v1.0.md`).
- Application code (`src/`, `scripts/`, `tests/`) is free of internal-workflow
  narrative except benign `authorization_basis` string pointers to checkpoint
  file paths and recruiter/review wording inside portfolio-generator comments.

## 1. Repository Audit

Every major tracked path classified as **PUBLIC**, **PRIVATE_ARCHIVE**, or
**REVIEW_REQUIRED**.

| Path | Tracked scope | Classification | Rationale |
| --- | --- | --- | --- |
| `README.md` | 1 | REVIEW_REQUIRED | Public face; must be re-verified (links, Pages URL, structure claims) but stays. |
| `LICENSE` | 1 (MIT) | PUBLIC | Required for a public repo. |
| `AGENTS.md` | 1 | REVIEW_REQUIRED | Agent-workflow contract; exposes internal AI process. Move to archive or replace with a neutral `CONTRIBUTING.md`. |
| `.gitignore` | 1 | PUBLIC | Needed; may be extended for the public repo. |
| `.github/workflows/pages.yml` | 1 | PUBLIC | Drives Pages deploy; keep. |
| `portfolio/` | 13 | PUBLIC | The recruiter-facing deliverable. Keep in full. |
| `src/` | 47 | PUBLIC | Real engineering; keep. Comment-level review only. |
| `tests/` | 34 | PUBLIC | Demonstrates rigor; keep. |
| `scripts/` | 13 | PUBLIC | Reproducibility surface; keep (comment review). |
| `artifacts/` | 17 | REVIEW_REQUIRED | Governed evidence, but 3 JSONs embed absolute local paths. Keep, path-sanitize under governance. |
| `data/` (tracked 50) | 50 | REVIEW_REQUIRED | Governed derived JSON only; large raw bytes already ignored. Confirm no absolute paths / PII before keeping. |
| `docs/` top-level `*.md` | 41 | REVIEW_REQUIRED | Mix of public-suitable normative docs and internal planning/authorization docs. Split per §2. |
| `docs/checkpoints/` | 33 | PRIVATE_ARCHIVE | Internal review/authorization/closure history. Not for public. |
| `docs/plans/` | 2 | REVIEW_REQUIRED | UX architecture is arguably public; implementation plan is internal. Split per §2. |
| `docs/evidence/` | 11 | REVIEW_REQUIRED | Substantiates portfolio claims; keep a curated subset, sanitize paths. |
| `docs/research/` | 3 | REVIEW_REQUIRED | Licensing/governance investigations; likely keep (dataset provenance) after review. |
| `assets/` | 43 | REVIEW_REQUIRED | Mixed: portfolio-experience baseline (keep) vs prototype zips/parts (archive). |
| `tools/` | 1 | REVIEW_REQUIRED | Asset generator; keep if referenced, else archive. |
| `output/` | 1 (`.gitkeep`) | PUBLIC | Empty placeholder; harmless. |
| `.local/`, `.pytest_cache/`, `.DS_Store` | untracked/ignored | REMOVE AFTER ARCHIVE | Ensure never published; already git-ignored. |

## 2. Public vs Private Classification

Per documentation category, with justification. Actions:
**KEEP PUBLIC**, **MOVE TO PRIVATE ARCHIVE**, **REVIEW**, **REMOVE AFTER ARCHIVE**.

| Category | Action | Justification |
| --- | --- | --- |
| `README.md` | KEEP PUBLIC (after REVIEW) | Public overview; verify it references only public paths and the correct Pages URL. |
| `portfolio/` | KEEP PUBLIC | The intended recruiter experience; self-contained and truthful (closure review complete). |
| `src/` | KEEP PUBLIC | Genuine engineering substance; the credibility of the portfolio. |
| `tests/` | KEEP PUBLIC | 510 passing tests demonstrate discipline. |
| `assets/portfolio-experience/` | KEEP PUBLIC | Frozen design baseline backing the portfolio. |
| `assets/KALIBRA_WORKBENCH_PROTOTYPE_v1.0.png` | KEEP PUBLIC | Referenced by README. |
| `assets/kalibra-prototype/`, `assets/prototypes/*.zip`, `assets/parts/` | MOVE TO PRIVATE ARCHIVE | Internal prototype iterations and raw part assets; not part of the public story. |
| `docs/` normative set (`KALIBRA_FOUNDATION`, `KALIBRA_ARCHITECTURE`, `KALIBRA_EVALUATION_METHODOLOGY`, `KALIBRA_DATASET_STRATEGY`, `KALIBRA_SYSTEM_REQUIREMENTS`, `KALIBRA_IMPLEMENTATION_ROADMAP`, `KALIBRA_ENGINEERING_PLAN`) | KEEP PUBLIC (after REVIEW) | AGENTS.md already declares these the "public project documentation"; they describe the system, not the workflow. |
| `docs/` `*_IMPLEMENTATION_PLAN`, `*_BASELINE_PLAN`, `*_AUTHORIZATION`, `*_DECISION_MEMO`, `*_ADR`, `*_STRATEGY` (ML phase internals), `KALIBRA_NEXT_IMPLEMENTATION_SLICE_RECOMMENDATION`, `KALIBRA_CLAUDE_DESIGN_BRIEF` | MOVE TO PRIVATE ARCHIVE | Internal planning, authorization, and AI-design-brief material; exposes process, not product. |
| `docs/` phase closures (`ARCHITECTURE_PHASE_1_CLOSURE`, `ENGINEERING_PHASE_2_CLOSURE`) | REVIEW | Decide whether a sanitized "engineering milestones" summary is public; raw closures go to archive. |
| `docs/checkpoints/` (all 33) | MOVE TO PRIVATE ARCHIVE | Review/authorization/closure/prompt lineage — the internal workflow itself. |
| `docs/plans/KALIBRA_PORTFOLIO_UX_ARCHITECTURE_v1.0.md` | REVIEW | Candidate public design rationale; sanitize recruiter/Werkstudent framing first. |
| `docs/plans/PORTFOLIO_EXPERIENCE_IMPLEMENTATION_PLAN_v1.0.md` | MOVE TO PRIVATE ARCHIVE | Internal build plan. |
| `docs/evidence/` (10 evidence docs + `prototype-ui/` screenshots) | REVIEW | Keep a curated subset that substantiates portfolio claims; sanitize absolute paths; archive the rest. |
| `docs/research/` (VisA/MPDD licensing & governance) | REVIEW → likely KEEP PUBLIC | Dataset provenance/licensing strengthens credibility; verify no internal-process language. |
| `AGENTS.md` | MOVE TO PRIVATE ARCHIVE | Pure internal agent-workflow contract. Optionally replaced by a neutral public `CONTRIBUTING.md`. |
| `tools/generate_kalibra_part_assets.py` | REVIEW | Keep only if a public asset path depends on it; else archive. |
| `.local/`, caches, `.DS_Store` | REMOVE AFTER ARCHIVE | Never publish; confirm ignored. |

## 3. Private Archive Structure

Target: `/Users/agentisstudio/Documents/andre-projects/kalibra-private/`.

Mirror the repository's own vocabulary so traceability is 1:1. Proposed layout:

```text
kalibra-private/
  README.md                      # what this archive is, source commit, date
  MANIFEST.md                    # every archived file + original repo path + sha256
  git-bundle/
    kalibra-full-history.bundle  # git bundle --all (complete history, no loss)
  docs/
    normative-internal/          # ML-phase plans, ADRs, strategies, memos
    checkpoints/                 # all 33 docs/checkpoints/*
    plans/                       # internal implementation plans
    evidence-archived/           # evidence docs not carried to public
    research-archived/           # research not carried to public
    phase-closures/              # raw closure docs
    design-brief/                # KALIBRA_CLAUDE_DESIGN_BRIEF_v1.0.md
  agents/
    AGENTS.md
  assets-internal/
    prototypes/                  # kalibra-prototype*, *.zip
    parts/                       # assets/parts/*
  notes/                         # any loose internal notes discovered in REVIEW
```

Preservation rules:

- **No-loss guarantee via `git bundle --all`**: a full clone-able bundle of the
  entire history is archived *before* any sanitization, so complete engineering
  history survives even if the public repo's history is later rewritten.
- **MANIFEST.md** records, for every archived artifact: original repo-relative
  path, archive path, and SHA-256, so any archived doc can be traced back to its
  exact source.
- Directory names deliberately echo `plans / checkpoints / reviews /
  investigations / research / prompts` so the archive reads like the internal
  workflow it preserves.

## 4. Public Repository Structure

Final public tree (recruiter-friendly, minimal, credible):

```text
kalibra/  (public)
  README.md              # sanitized public overview
  LICENSE                # MIT
  CONTRIBUTING.md        # optional neutral replacement for AGENTS.md
  .gitignore
  .github/workflows/pages.yml
  portfolio/             # deployable static experience (unchanged)
  src/                   # engineering code
  tests/                 # test suite
  scripts/               # reproducibility scripts
  artifacts/             # governed evidence (paths sanitized)
  data/                  # tracked governed derived JSON only
  assets/
    KALIBRA_WORKBENCH_PROTOTYPE_v1.0.png
    portfolio-experience/   # frozen design baseline
  docs/
    KALIBRA_FOUNDATION_v1.0.md
    KALIBRA_ARCHITECTURE_v1.0.md
    KALIBRA_EVALUATION_METHODOLOGY_v1.0.md
    KALIBRA_DATASET_STRATEGY_v1.0.md
    KALIBRA_SYSTEM_REQUIREMENTS_v1.0.md
    KALIBRA_IMPLEMENTATION_ROADMAP_v1.0.md
    KALIBRA_ENGINEERING_PLAN_v1.0.md
    evidence/            # curated, path-sanitized subset
    research/            # dataset licensing/governance (if cleared)
```

- **Canonical folders:** `portfolio/`, `src/`, `tests/`, `scripts/`,
  `artifacts/`, `data/`, `assets/`, `docs/`.
- **Documentation:** the seven system-level normative docs + curated evidence +
  (optionally) research.
- **Portfolio:** `portfolio/` unchanged; it is the entry point.
- **Assets:** only the workbench PNG and the frozen portfolio-experience baseline.
- **Examples:** the `scripts/verify_*` + Verify station already function as a
  runnable "reproduce it yourself" example; no separate `examples/` needed.

## 5. Public-Boundary Language Audit Strategy

Method: run a case-insensitive, tracked-files-only scan
(`git grep -I -i -l "<term>"`) for the full term list, then triage each hit by
**file location** and **usage context** — not by raw count. Concentration is
already known: internal vocabulary lives in `docs/checkpoints/`, `docs/plans/`,
some top-level `docs/*.md`, and `AGENTS.md`; code is clean.

Triage classes: **KEEP_PUBLIC**, **RENAME**, **MOVE_PRIVATE**,
**DELETE_AFTER_ARCHIVE**, **REVIEW_CONTEXT**.

| Term | Observed locus | Disposition |
| --- | --- | --- |
| `recruiter` (4) | docs/plans, docs/checkpoints | MOVE_PRIVATE (checkpoints); REVIEW_CONTEXT + RENAME to neutral "reader/reviewer" if UX-architecture doc goes public. |
| `Werkstudent` (3) | docs/plans, docs/checkpoints | MOVE_PRIVATE; RENAME out of any doc that goes public. |
| `portfolio` (many) | portfolio/, docs | KEEP_PUBLIC — it is a legitimate product noun for the static site. |
| `Claude` / `Claude Code` / `Claude Design` (4) | KALIBRA_CLAUDE_DESIGN_BRIEF, docs/plans, docs/checkpoints | MOVE_PRIVATE (design brief + checkpoints); REVIEW_CONTEXT elsewhere. Public repo must not name the AI tooling. |
| `Codex` (35) | 31× docs/checkpoints, else scattered | REVIEW_CONTEXT — almost all are the **branch name** `codex/initial-engineering-skeleton`. RENAME the publication branch (e.g. `main`) so the token disappears naturally; checkpoints go MOVE_PRIVATE regardless. |
| `Kilo`, `ChatGPT`, `EloiRamos`, `Alex` (0) | none | No action — confirmed absent. |
| `Agentis` (5) | docs | REVIEW_CONTEXT → MOVE_PRIVATE/DELETE_AFTER_ARCHIVE; studio identity should not appear in the public repo unless intended as authorship. |
| `prompt` (10) | docs/checkpoints | MOVE_PRIVATE. |
| `checkpoint` (57) | docs/checkpoints + refs in src/scripts comments | MOVE_PRIVATE (the docs); REVIEW_CONTEXT for `authorization_basis` string pointers in `scripts/` (rewrite to neutral evidence reference or accept as benign). |
| `authorization` (37) | docs/checkpoints, some docs, 2 scripts | MOVE_PRIVATE (docs); REVIEW_CONTEXT in scripts. |
| `closure review` / `implementation review` (11 / 10) | docs/checkpoints | MOVE_PRIVATE. |
| `internal` (25), `private` (24), `workflow` (21) | docs | REVIEW_CONTEXT; most ride along with archived docs. Scan survivors in public set. |
| `agent` (43) | docs, AGENTS.md | MOVE_PRIVATE (AGENTS.md, checkpoints); REVIEW_CONTEXT for any public doc. |
| `publication` (11), `temporary` (5), `archive` (48), `do not push` (0) | docs | REVIEW_CONTEXT; these describe *this* preparation process and must not survive into the public set. |
| `sanitize` (0) | none | No action. |

**Public-boundary guarantee:** after execution, the public repository must not
expose internal AI workflow, internal review/authorization process, prompt
engineering, the publication process itself, private archive paths, or internal
planning history. Verification is a re-run of the same scan restricted to the
public file set, expecting zero hits for the workflow terms (allowing the
product noun `portfolio` and any deliberately retained neutral usages).

## 6. Sensitive Content Audit

| Signal | Finding | Recommended action |
| --- | --- | --- |
| Local filesystem paths | `/Users/agentisstudio/Documents/kalibra/...` embedded in `artifacts/runtime/integration_metadata.json`, `artifacts/runtime/runtime_replay.json`, `artifacts/runtime/equivalence/runtime_equivalence_report.json`, and 2 docs | **REVIEW_REQUIRED (highest priority).** These are governed, hash-anchored artifacts — blindly editing them may break equivalence/replay checks and tests. Options, in order of preference: (a) regenerate the artifacts under a relative/placeholder base path if the generators support it; (b) if not, sanitize to a neutral token (e.g. `<REPO>/...`) and re-govern the hashes with an ADR noting the substitution; (c) as a last resort, archive-and-exclude the offending files from the public set. Decide during execution, not now. |
| Usernames | `agentisstudio` appears only inside those absolute paths | Resolved by the path action above. |
| Studio / personal identity | `Agentis` in 5 docs | Confirm intended authorship; otherwise archive/neutralize. |
| Temporary folders | `.local/`, `.pytest_cache/`, `.DS_Store` | Already git-ignored; confirm not tracked before publish. |
| Unpublished / internal URLs | README references `https://andrejr03.github.io/kalibra/` (public Pages target) | KEEP but VERIFY the account/repo slug is correct for the publication target. |
| Internal repository references | Branch name `codex/initial-engineering-skeleton` in 35 files | Publish from a clean `main`; ensure no doc that survives to public hard-codes the branch name. |
| Private deployment notes | None found in tracked files | No action. |
| Secrets / credentials | Prior re-review security scan reported no secret candidates | Re-run a secret scan as a validation gate before push. |

## 7. Migration Strategy

Safe, ordered, no-data-loss sequence. Each stage gated by the next only
proceeding on success.

1. **Classify** — freeze this plan's classifications into an execution manifest
   (source path → PUBLIC / PRIVATE_ARCHIVE / REVIEW → resolved decision).
2. **Archive** — create `kalibra-private/`, write `git bundle --all` first, then
   copy every PRIVATE_ARCHIVE and archived-REVIEW artifact with the `MANIFEST.md`
   (path + sha256). Nothing deleted from the repo yet.
3. **Verify (archive integrity)** — confirm the bundle clones cleanly and every
   manifest sha256 matches its archived copy; confirm no PRIVATE item lacks an
   archive counterpart.
4. **Sanitize** — only after archive integrity is proven: remove/relocate
   internal docs from the public working set, resolve absolute-path artifacts per
   §6, rename branch to `main`, replace/remove `AGENTS.md`, and re-verify the
   language scan on the public set.
5. **Validate** — run the full §8 validation suite on the sanitized public tree.
6. **Publish** — only on explicit human authorization (§10): push clean `main`
   to the public remote and enable Pages.

Principle: **archive-before-alter**. No destructive step runs until the archive
and its integrity check pass.

## 8. Validation Strategy (pre-publication gates)

Run against the sanitized public tree; all must pass before publish:

- **Build / import:** `python3 -m compileall -q src tests scripts` → clean.
- **Tests:** `python3 -m pytest -q` → expect `510 passed` (or an explained delta
  if any test referenced archived paths).
- **Portfolio bundle:** `python3 scripts/build_portfolio_evidence_bundle.py --check`
  → PASS.
- **Portfolio renders:** open `portfolio/index.html` over a static server;
  confirm nine stations, zero console errors, only `/`, `styles.css`, `app.js`
  requested, no external/CDN calls.
- **GitHub Pages:** confirm `.nojekyll` present and `pages.yml` runs the passing
  `--check`; validate the Pages URL slug.
- **No broken links:** scan Markdown + portfolio for links pointing at archived
  (now-absent) `docs/checkpoints`, `docs/plans`, or internal docs.
- **No stale screenshots:** confirm every image referenced by README/portfolio
  still resolves in the public tree.
- **No orphan files:** confirm no public file references a MOVE_PRIVATE artifact.
- **Language re-scan:** workflow-term scan on the public set returns only
  intended survivors.
- **Secret scan:** re-run; expect zero secret candidates.
- **Path scan:** `git grep -I -n "/Users/"` on the public set → zero.

## 9. Rollback Strategy

- **Pre-push failure:** the public transformation happens on a throwaway working
  copy / branch. If any §8 gate fails, discard the branch/copy; the original
  repository and the archive are untouched.
- **Restore full history:** `git clone kalibra-private/git-bundle/kalibra-full-history.bundle`
  reconstitutes the complete pre-sanitization repository.
- **Restore an individual artifact:** look it up in `MANIFEST.md`, copy back from
  the archive, and verify its sha256 matches the manifest entry.
- **Post-push failure:** if a problem is found after publishing, unpublish
  (make repo private / disable Pages), fix on the working copy, re-run §8, and
  re-push. The archive remains the source of truth for anything removed.
- **Integrity verification:** after any restore, re-run §8 build + tests +
  bundle check to confirm the restored state is consistent.

## 10. Final GitHub Publication Checklist

- [ ] Repository clean — only PUBLIC + resolved-REVIEW files remain in the
      public working set; caches/`.local`/`.DS_Store` absent.
- [ ] Archive verified — `git bundle --all` clones cleanly; `MANIFEST.md`
      sha256s all match; every PRIVATE item has an archived counterpart.
- [ ] Public-boundary audit complete — §5 scan on public set shows only intended
      survivors; no AI-workflow/process/prompt/planning leakage.
- [ ] Language audit complete — recruiter/Werkstudent/Claude/Codex/agent/
      authorization/checkpoint terms cleared from the public set.
- [ ] Sensitive content clear — no `/Users/` paths, no username, no private
      archive paths in the public set; artifact paths resolved and re-governed.
- [ ] Portfolio validated — renders, nine stations, zero console errors, no
      external calls, `--check` PASS.
- [ ] README validated — public overview only; correct Pages URL; links resolve;
      structure claims match the public tree.
- [ ] GitHub Pages validated — `.nojekyll` present, `pages.yml` green, URL slug
      correct.
- [ ] Licenses — `LICENSE` (MIT) present; dataset licensing/attribution
      (VisA/MPDD) represented if research docs are published.
- [ ] Release tag — tag the initial public release (e.g. `v1.0.0`) on clean
      `main`.
- [ ] Final push authorization — explicit human go/no-go recorded before any
      push to the public remote.

## 11. Validation (this planning step)

Commands run for this plan (read-only):

```bash
git status --short
find . -maxdepth 3 -type f | sort
```

Results are recorded in the session response. No repository file was modified by
producing this plan (the only new file is this plan document itself).

## 12. Next Natural Step

Review this Public GitHub Preparation Plan before authorizing repository
sanitization and migration to the private archive.
