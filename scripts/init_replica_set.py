"""
Initialize a single-node replica set on local MongoDB (development demo).

Requires mongod started with --replSet rs0 (see docs/replication.md).

Usage:
    python scripts/init_replica_set.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import get_mongo_client  # noqa: E402


def main() -> int:
    client = get_mongo_client()
    try:
        try:
            status = client.admin.command("replSetGetStatus")
            print("Replica set already initialized:", status.get("set"))
            return 0
        except Exception:
            pass

        client.admin.command(
            "replSetInitiate",
            {
                "_id": "rs0",
                "members": [{"_id": 0, "host": "127.0.0.1:27017"}],
            },
        )
        print("Replica set rs0 initiated (single-member dev setup).")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
