# CareSync — Distributed Healthcare Data Management System

**Educational prototype** using **fictional patient data only**. Not for real clinical use, HIPAA compliance, or production deployment without full security review.

## Quick start (Windows PowerShell)

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Ensure MongoDB Windows service is running:
Get-Service MongoDB
Start-Service MongoDB

python scripts\verify_mongodb.py
python scripts\seed_demo_data.py --patients 50
streamlit run app.py
```

**In the app:** open **Data import** to generate 50+ fictional records or upload a CSV.

**Browser URL:** http://localhost:8501

### Demo accounts (after seed)

| Username | Password | Role |
|----------|----------|------|
| admin | Demo@2026! | Administrator |
| dr.morgan | Demo@2026! | Doctor |
| reception | Demo@2026! | Receptionist |

### First admin (no seed)

Set in `.env` (copy from `.env.example`):

- `ADMIN_BOOTSTRAP_USERNAME`
- `ADMIN_BOOTSTRAP_PASSWORD`

Restart the app when the database has **zero** users.

## Features

- Professional Streamlit UI (Inter typography, healthcare theme)
- RBAC: Administrator, Doctor, Receptionist (server-side checks)
- Patients, medical records, doctors, appointments
- Dashboard metrics and charts from **live MongoDB queries**
- Reports with CSV export
- Audit logs (login, CRUD, record views)
- Backup / restore scripts
- **Multi-facility sync demo** (FastAPI nodes + outbox + idempotency + conflicts)

## Commands

```powershell
python scripts\backup_db.py
pytest -q
$env:INTEGRATION_TESTS="1"; pytest -q
```

## Distributed sync demo

See `docs/distributed-sync-demo.md`.

## Documentation

| Doc | Purpose |
|-----|---------|
| `docs/architecture.md` | Layers and collections |
| `docs/mongodb-setup-windows.md` | MongoDB install |
| `docs/replication.md` | MongoDB replica set |
| `docs/distributed-sync-demo.md` | Multi-facility sync |
| `docs/demo-for-lecturer.md` | Viva checklist |
| `docs/troubleshooting.md` | Common fixes |
| `docs/SETUP-NEW-LAPTOP.md` | Clone repo on another PC |

## Data safety

- Existing MongoDB data is **preserved**; migrations only add missing fields.
- Destructive restore requires `--confirm`.
- Do not commit `.env` or backups with secrets.
