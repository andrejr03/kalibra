from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.prototype_ui import write_local_provider_demo_data  # noqa: E402


def main() -> int:
    write_local_provider_demo_data()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
