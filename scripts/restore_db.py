"""
Restore collections from a backup folder (requires --confirm).

Usage:
    python scripts/restore_db.py --backup backups/20260101T120000Z --confirm
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bson import json_util  # noqa: E402
from database import ensure_indexes, get_shared_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True, help="Path to backup folder")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required flag to avoid accidental overwrite",
    )
    args = parser.parse_args()

    if not args.confirm:
        print("Refusing to restore without --confirm", file=sys.stderr)
        return 2

    backup_dir = Path(args.backup)
    if not backup_dir.is_dir():
        print("Backup directory not found.", file=sys.stderr)
        return 1

    db = get_shared_database()
    for json_file in sorted(backup_dir.glob("*.json")):
        if json_file.name == "manifest.json":
            continue
        collection = json_file.stem
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        docs = json_util.loads(json.dumps(raw))
        db[collection].delete_many({})
        if docs:
            db[collection].insert_many(docs)

    ensure_indexes(db)
    print(f"Restored from {backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
