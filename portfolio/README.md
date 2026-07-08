# Kalibra Portfolio Experience

This directory is the deployable static portfolio surface for Kalibra.

It is generated from governed repository artifacts by:

```bash
python3 scripts/build_portfolio_evidence_bundle.py
```

The generator writes `portfolio/data/*.json` and injects the same governed
bundle into `portfolio/index.html` as inline JSON. The browser reads that inline
JSON with vanilla JavaScript; it does not fetch data, run inference, or contact
external services.

To verify that the committed portfolio output is current:

```bash
python3 scripts/build_portfolio_evidence_bundle.py --check
```

The site is intentionally static and self-contained so it works from both
GitHub Pages and `file://`.
