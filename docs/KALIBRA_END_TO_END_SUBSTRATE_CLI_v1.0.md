# KALIBRA End-to-End Substrate CLI v1.0

## 1. Purpose

The End-to-End Substrate CLI is a developer utility for exercising KALIBRA's
complete deterministic substrate chain from a local command.

It is not a product feature, product manual, user guide, implementation plan, or
performance demonstration. It exists to run the already implemented integration
layer and print a concise engineering summary.

## 2. Architecture Position

The CLI sits above the Integration layer. It owns no domain behavior and does
not inspect, qualify, review, preserve, or evaluate anything itself.

It invokes the existing integration runner, which composes the five substrates
in the documented order:

```text
Inspection
  -> Trust Qualification
    -> Human Review
      -> Evidence
        -> Evaluation
```

The CLI is not a sixth domain. It is a developer entry point over the existing
end-to-end substrate integration.

## 3. Running the CLI

Run the command from the repository root:

```sh
python3 scripts/run_end_to_end_substrate.py
```

The command executes the deterministic default integration fixture defined by
the integration layer. It does not accept production inputs, read images, write
state, persist records, update models, or touch prototype assets.

## 4. Output

The CLI prints JSON to stdout.

The JSON summary includes:

- `input_id`: stabilized integration input identifier.
- `inspection_result_id`: raw inspection result identifier.
- `trust_qualification_result_id`: trust qualification result identifier.
- `qualified_outcome`: canonical trust qualification outcome.
- `human_review_occurred`: whether Human Review ran for the fixture.
- `review_case_id`: review case identifier when review occurred; otherwise
  `null`.
- `evidence_view_id`: preserved evidence view identifier.
- `evaluation_report_id`: evidence-backed evaluation report identifier.
- `preserved_record_count`: count of preserved evidence records.
- `absence_disclosure_count`: count of evaluation absence disclosures.
- `claims`: explicit non-claim flags for ML, CV, production readiness, and
  performance claims.

The CLI does not output accuracy, benchmark results, quality scores, model
performance claims, or production readiness claims.

## 5. Engineering Guarantees

The CLI preserves these engineering boundaries:

- deterministic local execution;
- canonical substrate contracts as the primary flow;
- no legacy contract primary flow;
- no database or file persistence;
- no product UI or prototype behavior;
- no ML or computer vision implementation;
- no training, feedback, or model update behavior;
- no benchmark, quality-score, or performance claim.

## 6. Intended Usage

The CLI is intended for developers and maintainers who need a quick manual check
that the integrated substrate chain still runs.

Appropriate uses include:

- substrate verification;
- manual engineering checks;
- regression testing;
- architecture-boundary validation.

It is not intended for end users or operational use.

## 7. Out of Scope

The CLI does not implement:

- ML inference;
- computer vision;
- production calibration;
- evaluation science;
- persistence;
- deployment;
- product UI;
- monitoring;
- feedback loops.
