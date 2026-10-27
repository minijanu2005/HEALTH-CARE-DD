# Troubleshooting

## MongoDB connection failed

- Run `Get-Service MongoDB` and `Start-Service MongoDB`.
- Run `python scripts/verify_mongodb.py`.

## Login fails after install

- Run `python scripts/seed_demo_data.py` for demo users.
- Or set `ADMIN_BOOTSTRAP_USERNAME` / `ADMIN_BOOTSTRAP_PASSWORD` in `.env` and restart the app when the database has zero users.

## Streamlit shows blank page

- Check terminal for Python errors.
- Ensure venv is activated and `pip install -r requirements.txt` completed.

## pytest integration tests skipped

- Set `$env:INTEGRATION_TESTS = "1"` and ensure MongoDB is running.

## Restore overwrote data accidentally

- Always use `restore_db.py --confirm` only on disposable dev databases.
- Keep backups under `backups/` before experiments.
