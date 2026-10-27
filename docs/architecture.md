# Architecture overview

## Layers

1. **UI (`app.py`, `ui/`)** — Streamlit dashboard and forms.
2. **Services (`services/`)** — Business rules, validation, permissions, audit logging.
3. **Database (`database.py`)** — PyMongo client, indexes, ID sequences.
4. **Models (`models/`)** — Roles, collection names, statuses.

## Security flow

1. User logs in via `auth.authenticate`.
2. Session stored in `st.session_state` (username, role, user id).
3. Every service method checks permissions via `permissions.py`.
4. Passwords stored as Argon2 hashes only.
5. Audit entries written for create/update/delete actions (no passwords).

## MongoDB collections

| Collection | Purpose |
|------------|---------|
| `users` | Login accounts and roles |
| `patients` | Fictional patient demographics |
| `doctors` | Doctor directory |
| `appointments` | Scheduling and status |
| `medical_records` | Diagnoses, prescriptions, notes |
| `audit_logs` | Action history |
| `counters` | Sequential IDs (PAT-00001, …) |
| `sync_outbox` | Pending cross-facility messages |
| `sync_log` | Sync attempt audit trail |
| `sync_processed` | Idempotency keys |
| `sync_conflicts` | Version conflict records |

## Limitations (student prototype)

- Streamlit sessions are not enterprise SSO.
- Local MongoDB may run without auth in dev — enable users and TLS for production-like setups.
- Not HIPAA-certified or validated for real clinical use.
