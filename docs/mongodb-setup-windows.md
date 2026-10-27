# MongoDB setup on Windows (Phase 3)

This project uses **MongoDB Community Edition** as the primary database. Phase 3 uses a **single node** on your PC. Phase 9 adds a **replica set** to demonstrate replication (not the same as sharding or simple file backups).

## Concepts (simple)

| Term | Meaning |
|------|--------|
| **mongod** | The MongoDB server process that stores data. |
| **mongosh** | The MongoDB shell (command-line client). |
| **Database** | A namespace inside MongoDB (we use `healthcare_dev` from `.env`). |
| **Collection** | Like a table in SQL (e.g. `patients` — added in Phase 4). |
| **Replication** | Copying data across multiple mongod nodes for redundancy (Phase 9). |
| **Backup** | Exporting data so you can restore after failure (Phase 10). |

## Install MongoDB Community Server

### Option A — winget (recommended)

Open **PowerShell as Administrator** and run:

```powershell
winget install -e --id MongoDB.Server --accept-package-agreements --accept-source-agreements
winget install -e --id MongoDB.Shell --accept-package-agreements --accept-source-agreements
```

Close and reopen your terminal so `PATH` updates. Typical install path:

`C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe`

### Option B — MSI installer

1. Download **MongoDB Community Server** from [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community).
2. Run the MSI; choose **Complete** setup.
3. Optionally install **MongoDB Compass** (GUI) for learning — not required for this project.

## Run MongoDB as a Windows service

The MSI usually registers a service named **MongoDB**. Check and start it:

```powershell
Get-Service MongoDB
Start-Service MongoDB
```

Default data directory (typical): `C:\Program Files\MongoDB\Server\<version>\data\`

Default port: **27017** (matches `.env.example`).

## Verify from this project

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
.\.venv\Scripts\Activate.ps1
python scripts\verify_mongodb.py
```

Expected when MongoDB is running:

```text
OK: MongoDB ping succeeded.
    Server version: ...
    Database name (app): healthcare_dev
```

Optional integration test:

```powershell
$env:INTEGRATION_TESTS = "1"
pytest tests/test_database_connection.py -q
```

## Security notes (student prototype)

- Do not expose port 27017 to the public internet on a real network.
- Use **fictional** patient data only.
- In later phases we can create an application user with least privilege instead of using open local access.

## Troubleshooting

| Symptom | What to try |
|--------|-------------|
| `mongod` not recognized | Reopen terminal; add `...\MongoDB\Server\<version>\bin` to PATH. |
| Connection timeout | `Start-Service MongoDB`; check firewall allows local connections. |
| Port in use | Another program uses 27017 — change port in `mongod.cfg` and update `MONGODB_URI` in `.env`. |

## What comes in Phase 9

We will run multiple mongod processes (or containers) as a **replica set**, with one **primary** (accepts writes) and **secondaries** (replicate data). That is how we demonstrate **distributed** storage for your report — not separate SQLite files or unrelated collections alone.
