from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.integration import EndToEndSubstrateIntegrationEngine  # noqa: E402


def build_summary() -> dict[str, Any]:
    result = EndToEndSubstrateIntegrationEngine().run()
    trust_result = result.trust_qualification_output.trust_qualification_result
    references = result.stage_references

    return {
        "input_id": references.source_input_id,
        "inspection_result_id": references.inspection_result_id,
        "trust_qualification_result_id": (
            references.trust_qualification_result_id
        ),
        "qualified_outcome": trust_result.qualified_outcome.value,
        "human_review_occurred": result.human_review_output is not None,
        "review_case_id": references.review_case_id,
        "evidence_view_id": references.evidence_view_id,
        "evaluation_report_id": references.evaluation_report_id,
        "preserved_record_count": len(result.evidence_view.records),
        "absence_disclosure_count": len(
            result.evaluation_report.absence_disclosures
        ),
        "claims": {
            "ml_implemented": False,
            "cv_implemented": False,
            "production_ready": False,
            "performance_claim": False,
        },
    }


def main() -> int:
    print(json.dumps(build_summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
