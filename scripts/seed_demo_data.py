"""
Seed users + generate a rich fictional dataset (~50 patients).

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --patients 50
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth import hash_password  # noqa: E402
from database import ensure_indexes, get_shared_database  # noqa: E402
from models.constants import Collection, Role  # noqa: E402
from services.bulk_data_service import generate_fictional_dataset  # noqa: E402
from services.migration_service import apply_safe_migrations  # noqa: E402

DEMO_PASSWORD = "Demo@2026!"


def upsert_user(db, username: str, role: str, full_name: str) -> None:
    if db[Collection.USERS].find_one({"username": username}):
        return
    db[Collection.USERS].insert_one(
        {
            "username": username,
            "password_hash": hash_password(DEMO_PASSWORD),
            "role": role,
            "full_name": full_name,
            "active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients", type=int, default=50, help="Target active patient count")
    args = parser.parse_args()

    db = get_shared_database()
    ensure_indexes(db)
    apply_safe_migrations(db)

    upsert_user(db, "admin", Role.ADMINISTRATOR, "Alex Admin")
    upsert_user(db, "dr.morgan", Role.DOCTOR, "Dr. Jordan Morgan")
    upsert_user(db, "reception", Role.RECEPTIONIST, "Riley Reception")

    stats = generate_fictional_dataset(
        db,
        target_patients=args.patients,
        actor={"username": "admin", "role": Role.ADMINISTRATOR},
    )

    print("Demo data ready.")
    print(f"Dataset stats: {stats}")
    print("Login accounts (fictional):")
    print("  admin / dr.morgan / reception")
    print(f"  Password for all: {DEMO_PASSWORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
