# Distributed facility sync (local demonstration)

This is a **labeled educational demo**, not production multi-region hosting.

## What it demonstrates

- Unique **facility ID** per node (`FACILITY_ID`)
- **Version** and **source_facility_id** on records
- Authenticated HTTP sync API (`X-Sync-Api-Key`)
- **Outbox** queue, retries, idempotency (`sync_processed`)
- **Conflict detection** when local version is newer
- **Sync audit log** (`sync_log`, `sync_conflicts`)

## Start two nodes on one Windows PC

**Terminal 1 — Alpha**

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
.\.venv\Scripts\Activate.ps1
$env:FACILITY_ID="FAC-ALPHA"
$env:FACILITY_NAME="Alpha Clinic"
$env:MONGODB_DB_NAME="healthcare_facility_alpha"
$env:SYNC_API_PORT="8101"
$env:SYNC_API_KEY="dev-sync-key-change-in-production"
$env:SYNC_PEER_URLS="http://127.0.0.1:8102"
python scripts\run_facility_node.py
```

**Terminal 2 — Beta**

```powershell
$env:FACILITY_ID="FAC-BETA"
$env:FACILITY_NAME="Beta Clinic"
$env:MONGODB_DB_NAME="healthcare_facility_beta"
$env:SYNC_API_PORT="8102"
$env:SYNC_API_KEY="dev-sync-key-change-in-production"
$env:SYNC_PEER_URLS="http://127.0.0.1:8101"
python scripts\run_facility_node.py
```

**Terminal 3 — Main Streamlit app (HQ)**

```powershell
# Use .env with FACILITY_ID=HQ-MAIN and SYNC_PEER_URLS=http://127.0.0.1:8101,http://127.0.0.1:8102
streamlit run app.py
```

Register or update a patient in HQ, then open **Facilities & sync** → **Push pending sync messages**.

## Conflict strategy

If the local record **version** is greater than the incoming version, the local copy is kept and an entry is written to `sync_conflicts`.
