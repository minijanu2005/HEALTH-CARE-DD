import json
import os
from pathlib import Path

import pytest

from models.constants import Collection


@pytest.mark.integration
def test_backup_and_restore_roundtrip(tmp_path: Path) -> None:
    if os.getenv("INTEGRATION_TESTS") != "1":
        pytest.skip("Set INTEGRATION_TESTS=1 for live MongoDB tests.")

    from database import ensure_indexes, get_shared_database
    from services.patient_service import create_patient, get_patient

    db = get_shared_database()
    ensure_indexes(db)

    actor = {"username": "test", "role": "Administrator"}
    created = create_patient(
        db,
        actor=actor,
        full_name="Backup Test Patient",
        date_of_birth="1999-01-01",
        gender="Female",
    )
    pid = created["patient_id"]

    # Run backup logic into temp dir
    stamp_dir = tmp_path / "bkp"
    stamp_dir.mkdir()
    from bson import json_util

    docs = list(db[Collection.PATIENTS].find({"patient_id": pid}))
    (stamp_dir / "patients.json").write_text(
        json.dumps(docs, default=json_util.default), encoding="utf-8"
    )

    db[Collection.PATIENTS].delete_one({"patient_id": pid})
    assert get_patient(db, pid) is None

    raw = json.loads((stamp_dir / "patients.json").read_text(encoding="utf-8"))
    restored = json_util.loads(json.dumps(raw))
    db[Collection.PATIENTS].insert_many(restored)
    assert get_patient(db, pid) is not None
