# Demonstration checklist for lecturer

1. **Stack** — Python 3.14, Streamlit UI, MongoDB, Argon2 auth, FastAPI sync nodes.
2. **Login / logout** — Show audit entries for success and failure (Admin → Audit logs).
3. **RBAC** — Receptionist vs doctor vs admin (medical records, admin page, delete patient).
4. **Dashboard** — Metrics and charts from live DB (not hardcoded).
5. **Patients** — Register, search, paginate, update, deactivate.
6. **Medical records** — Create with visit date; doctor-only write; view audit on open.
7. **Doctors** — Directory, specialty filter, appointment counts, activate/deactivate.
8. **Appointments** — Schedule, conflict prevention, status badges, calendar-style chart.
9. **Reports** — Summaries and CSV export.
10. **Distributed sync** — Two facility nodes + push from **Facilities & sync** (see `distributed-sync-demo.md`).
11. **Backup** — `python scripts/backup_db.py`.
12. **Tests** — `pytest -q`.

**Disclaimer:** Fictional data only; not HIPAA-compliant or production-ready.
