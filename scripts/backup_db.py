"""
Export application collections to JSON under backups/ (no secrets).

Usage:
    python scripts/backup_db.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bson import json_util  # noqa: E402
from database import get_shared_database  # noqa: E402
from models.constants import Collection  # noqa: E402

COLLECTIONS = [
    Collection.USERS,
    Collection.PATIENTS,
    Collection.DOCTORS,
    Collection.APPOINTMENTS,
    Collection.MEDICAL_RECORDS,
    Collection.AUDIT_LOGS,
    Collection.COUNTERS,
]


def main() -> int:
    db = get_shared_database()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "backups" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, int] = {}
    for name in COLLECTIONS:
        docs = list(db[name].find({}))
        manifest[name] = len(docs)
        path = out_dir / f"{name}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(docs, fh, default=json_util.default, indent=2)

    meta = {"created_at": stamp, "collections": manifest}
    (out_dir / "manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Backup written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
