# Setup on another Windows laptop (from Git repo)

## 1. Prerequisites (install once)

1. **Python 3.12+ or 3.14** from [python.org](https://www.python.org/downloads/) — check **Add Python to PATH**.
2. **Git** from [git-scm.com](https://git-scm.com/download/win).
3. **MongoDB Community** — see `docs/mongodb-setup-windows.md`, or:

```powershell
winget install -e --id MongoDB.Server --accept-package-agreements --accept-source-agreements
Start-Service MongoDB
```

## 2. Clone the repository

```powershell
cd $env:USERPROFILE\Downloads
git clone <YOUR_REPO_URL> HealthcareManagementSystem
cd HealthcareManagementSystem
```

Replace `<YOUR_REPO_URL>` with your GitHub/GitLab/Origin URL.

## 3. Virtual environment and dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If `Activate.ps1` is blocked:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 4. Environment file

```powershell
copy .env.example .env
```

Edit `.env` if MongoDB is not on `127.0.0.1:27017`.

## 5. Verify database and load demo data

```powershell
python scripts\verify_mongodb.py
python scripts\seed_demo_data.py --patients 50
```

## 6. Run the application

```powershell
streamlit run app.py
```

Open **http://localhost:8501**

Login: `admin` / `Demo@2026!` (after seed)

## What NOT to copy from your old PC

- Do **not** copy `.venv` — recreate it with `pip install -r requirements.txt`.
- Do **not** commit or share `.env` — use `.env.example` on the new machine.
- MongoDB data is **local** — run seed on the new laptop or restore from `backups/` if you exported them.

## Optional: push repo from your current PC

On your development machine (first time only):

```powershell
cd C:\Users\sanna\Downloads\HealthcareManagementSystem
git add .
git commit -m "CareSync healthcare project"
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

Use branch `master` if that is your default: `git push -u origin master`.
