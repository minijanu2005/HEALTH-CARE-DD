# Local multi-facility sync demonstration

This demonstrates **distributed data exchange** between fictional healthcare facilities on one Windows PC. It is **not** production multi-region hosting.

## Architecture

- **Main app** (`streamlit run app.py`) — staff UI for one facility (`FACILITY_ID` in `.env`).
- **Sync API nodes** (`scripts/run_facility_node.py`) — FastAPI endpoints that accept authenticated sync messages.
- **MongoDB** — separate database per facility (e.g. `healthcare_facility_alpha`, `healthcare_facility_beta`).
- **Outbox** — local changes queued in `sync_outbox`, pushed to peers with `X-Sync-Api-Key`.
- **Idempotency** — `sync_processed.message_id` prevents duplicate application.
- **Conflicts** — if local version is newer, inbound copy is rejected and logged in `sync_conflicts`.

## Start two facility nodes

**Terminal 1 — Alpha**

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
.\.venv\Scripts\Activate.ps1
$env:FACILITY_ID="FAC-ALPHA"
$env:FACILITY_NAME="Alpha Clinic"
$env:MONGODB_DB_NAME="healthcare_facility_alpha"
$env:SYNC_API_PORT="8101"
$env:SYNC_API_KEY="demo-sync-secret"
$env:SYNC_PEER_URLS="http://127.0.0.1:8102"
python scripts\run_facility_node.py
```

**Terminal 2 — Beta**

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
.\.venv\Scripts\Activate.ps1
$env:FACILITY_ID="FAC-BETA"
$env:FACILITY_NAME="Beta Clinic"
$env:MONGODB_DB_NAME="healthcare_facility_beta"
$env:SYNC_API_PORT="8102"
$env:SYNC_API_KEY="demo-sync-secret"
$env:SYNC_PEER_URLS="http://127.0.0.1:8101"
python scripts\run_facility_node.py
```

**Terminal 3 — Main UI (HQ)**

```powershell
$env:FACILITY_ID="HQ-MAIN"
$env:MONGODB_DB_NAME="healthcare_dev"
$env:SYNC_PEER_URLS="http://127.0.0.1:8101,http://127.0.0.1:8102"
$env:SYNC_API_KEY="demo-sync-secret"
streamlit run app.py
```

Register a patient in the UI, then open **Facilities & sync** → **Push pending sync messages**.

Verify in mongosh:

```javascript
use healthcare_facility_alpha
db.patients.find().pretty()
```

## Conflict test

1. Sync the same `patient_id` to both nodes.
2. Update the patient on both nodes with different data (different versions).
3. Push sync again — inspect **Facilities & sync** → **Conflicts** and `sync_log`.
