"""
Run a facility sync API node (local multi-facility demo).

Example — Terminal 1 (Alpha):
  $env:FACILITY_ID="FAC-ALPHA"
  $env:MONGODB_DB_NAME="healthcare_facility_alpha"
  $env:SYNC_API_PORT="8101"
  $env:SYNC_PEER_URLS="http://127.0.0.1:8102"
  python scripts/run_facility_node.py

Example — Terminal 2 (Beta):
  $env:FACILITY_ID="FAC-BETA"
  $env:MONGODB_DB_NAME="healthcare_facility_beta"
  $env:SYNC_API_PORT="8102"
  $env:SYNC_PEER_URLS="http://127.0.0.1:8101"
  python scripts/run_facility_node.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uvicorn  # noqa: E402

from config import get_settings  # noqa: E402


def main() -> int:
    settings = get_settings()
    uvicorn.run(
        "api.facility_api:app",
        host="127.0.0.1",
        port=settings.sync_api_port,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
