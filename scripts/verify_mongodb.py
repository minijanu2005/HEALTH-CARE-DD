"""
Verify MongoDB connectivity from the project settings.

Usage (PowerShell, with venv activated):
    python scripts/verify_mongodb.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from project root when running as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import ping_mongodb  # noqa: E402


def main() -> int:
    result = ping_mongodb()
    if result.get("ok"):
        version = result.get("server_version", "unknown")
        db_name = result.get("database", "")
        print(f"OK: {result['message']}")
        print(f"    Server version: {version}")
        print(f"    Database name (app): {db_name}")
        return 0

    print(f"FAIL: {result['message']}", file=sys.stderr)
    print(
        "Tip: Install MongoDB Community, start the service, then run this script again.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
