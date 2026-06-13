# How to Run

## Requirements

- Git
- Python 3.13+
- Node.js 22+ with npm
- Internet access for the first dependency installation
- Available ports `8000` and `3000`

Verify the installations:

```powershell
git --version
python --version
node --version
npm --version
```

## Download

```powershell
git clone https://github.com/umer-exe/ai-resume-analyzer.git
cd ai-resume-analyzer
```

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Backend: `http://localhost:8000`

## Frontend

Open another PowerShell terminal from the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Frontend: `http://localhost:3000`

If the backend runs at another address, create `frontend/.env.local`:

```text
NEXT_PUBLIC_API_BASE_URL=http://HOST:PORT
```

The trained ML model is included. The training dataset, model retraining, API
keys, and a database are not required to run the application.
