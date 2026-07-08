# Kalibra — Portfolio Experience · Design Handoff v1.0

Front-end handoff for the **approved v0.2 visual prototype**. These four files
reproduce that design exactly. Open `index.html` in any browser — it works
fully offline, with no build step, no server, and no network access.

```
index.html    markup + content (semantic, static)
styles.css    all visual styling (single stylesheet)
app.js        interaction only (vanilla, ~40 lines)
README.md     this file
```

This document exists only to help you reproduce the approved look and feel.
It does **not** describe the Kalibra system, architecture, or repository — see
the product's own docs for that.

---

## 1 · Project purpose

A single-page, scroll-driven "workbench" that walks a reader through nine
stations (00 Overview → 08 Verify). It is a **visual approval artifact**: every
number shown is a real governed value or an explicit "Not yet demonstrated"
state. There is no live inference and no dashboard — the page presents recorded
evidence, calmly.

## 2 · Visual philosophy

Industrial, elegant, dark, minimal, evidence-first. Restrained by intent:

- **Evidence beside every claim.** Hashes, sample counts, and tolerances sit
  next to the statements they support. Copyable hashes are the recurring motif.
- **Honesty is a visible design element.** Anything unproven uses the dashed,
  diagonal-hatched **"Not yet demonstrated"** treatment (`.nyd`, `.st.gap`,
  `.nyd-item`). Never restyle an absence to look finished — the emptiness is the
  message.
- **Quiet surfaces, one accent.** Near-black panels, hairline borders, a single
  amber accent. No gradients-as-decoration, no glow except the one status dot.

## 3 · Colour palette

All colours are CSS variables on `:root` in `styles.css`. Do not introduce new
colours; reuse these tokens.

| Token | Value | Role |
|---|---|---|
| `--bg` | `#07090d` | Page background |
| `--bg2` | `#080b10` | Rail / footer background |
| `--panel` | `#0e141c` | Card surface |
| `--panel2` | `#0b1017` | Deep card surface |
| `--panel3` | `#090d12` | Inset (hash pill) surface |
| `--line` / `--line2` | `rgba(255,255,255,.07)` / `.12` | Hairline borders |
| `--ink` / `--ink2` | `#f3f5f8` / `#eef1f5` | Primary text |
| `--mut` … `--mut4` | `#c4ccd6` → `#5f6975` | Muted text (4 steps) |
| `--amber` | `#e6a23c` | Brand accent · links · CTAs |
| `--green` | `#45c46a` | Demonstrated / verified |
| `--red` | `#e5514e` | Defect judgement |
| `--slate` | `#7d93bf` | "Not yet demonstrated" |

Semantics matter: **green = proven, slate = not yet, amber = brand/action,
red = the defect verdict only.** Keep these meanings fixed.

## 4 · Typography

Three families, referenced with system fallbacks so the file renders offline
today. If you self-host webfonts later, keep the roles identical.

- `--disp` — **Space Grotesk** (fallback Eurostile / system): display, headings,
  labels, kickers. Often light weight (300) at large sizes; 600 + wide
  letter-spacing for uppercase labels.
- `--body` — **IBM Plex Sans** (fallback system): body copy, ledes, metric values.
- `--mono` — **IBM Plex Mono** (fallback SF Mono/Menlo): hashes, paths, terminal,
  station numbers, all machine values.

Conventions to preserve: uppercase labels use `letter-spacing` .1–.18em; large
display numbers use light weight; every hash/path/metric is mono.

## 5 · Spacing principles

- Section (`.stn`) vertical rhythm: **64px** top/bottom, **56px** horizontal.
- Card padding **22–24px**; card radius **11–12px**; pill/chip radius **6–9px**.
- Gaps come from flex/grid **`gap`**, not margins — 14–18px between cards,
  8–12px between inline chips. Keep it this way when adding elements.
- One breakpoint: **`max-width:1120px`** collapses the nav rail and drops all
  multi-column grids to one column; section padding relaxes to 44/26px.

## 6 · Interaction principles

Motion is minimal and functional — nothing decorative.

- **Copy-to-clipboard** on every `.hashrow`; the label briefly flips to
  "copied". This is the page's signature "verify it yourself" gesture.
- **Smooth scroll** from nav rail items and `[data-scroll]` CTAs to stations.
- **Scrollspy** highlights the active station in the rail (IntersectionObserver).
- **Disclosure** via native `<details>`: the inspection "Walk the decision" panel
  and the three timeline phases. Carets rotate on open.
- Hover states are subtle (border/%-lift only). No parallax, no autoplay.

## 7 · Component list

Reusable classes in `styles.css` (selector → purpose):

- `header.top`, `.brandchip`, `.wordmark`, `.chip` — sticky masthead + brand.
- `nav.rail` / `.navitem` / `.railfoot` — left navigation + status footer.
- `.stn` / `.stn-head` / `.kick` / `.stn-title` / `.lede` — station scaffold.
- `.card` (`.deep`) / `.card-k` — surfaces + card label.
- `.hashrow` + `.k-copy` — copyable hash pill.
- `.nyd`, `.nyd-item`, `.st.gap` — "Not yet demonstrated" treatments.
- `.st` (`.real` / `.amber` / `.gap`) — status chips.
- Hero: `.identity-strip`, `.idcell`, `.verdict-badge`, `.cta`, `.honest-line`.
- `.insp-grid`, `.frame`, `.metric-big`, `.bar`, `.kv`, `.disclose`, `.precomp`.
- `.chain` / `.link` (`.node` `.stem` `.claim` `.meta` `.pathpill`) — evidence chain.
- `.eq-grid`, `.bignum`, `.axis` (`.track` `.tick` `.marker` `.mlab`), `.replay-row`.
- `.arch` / `.domain` (`.real` / `.gap`), `.archflow` — architecture row.
- `.three` — the demonstrated / not / verify columns.
- `.metrics` / `.metric`, `.qualbar`, `.nyd-list`, `.reframe` — boundaries.
- `.tl` / `.phase` — timeline disclosures.
- `.verify-grid`, `.term` — verify terminal block.
- `.footer-principles` / `.fp`, `.proto-note` — footer.

## 8 · Implementation notes for the frontend engineer

- **Reproduce exactly.** This is an approved design. Match spacing, colour, and
  type. If you migrate into a framework, keep the class names as component names
  and the tokens as your theme — do not re-derive values.
- **Static content.** All governed values (SHA prefixes, `6,492`, `7.105e-15`,
  the three AUROC/AUPRO metrics) are literal text. They are correct as written;
  do not compute or "improve" them, and never invent confidence or metrics.
- **The two inspection images are inline SVG `data:` URIs** in the markup — no
  binary assets ship with this package. They render pixelated by design.
- **`app.js` is optional to behaviour, not to content.** With JS disabled the
  page is fully readable; only copy/scrollspy degrade.
- **No dependencies.** No framework, no CDN, no fonts fetched over the network.
  Keep it that way — the offline guarantee is part of the approval.
- **Fonts:** to pin the identity precisely, self-host Space Grotesk, IBM Plex
  Sans, and IBM Plex Mono and add `@font-face` rules; the `--disp/--body/--mono`
  variables already route every element to the right family.
- **Accessibility carried over:** semantic landmarks (`header`, `nav`, `main`,
  `section`), `alt` text on both SVG images, native `<details>` for disclosures.
  Preserve these if you refactor.
