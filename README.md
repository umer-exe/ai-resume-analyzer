# AI Powered Resume and Profile Analyzer

A basic full-stack resume and profile analysis project for students and job
seekers. The Next.js frontend sends profile text to a reusable Flask API and
displays an ATS score, grouped skills, strengths, weaknesses, recommended
roles, and a career roadmap.

The current Phase 2-5 implementation uses a fixed dummy analysis response.
Real rule-based analyzer logic will be added in Phase 6.

## Tech Stack

* Backend: Python, Flask, flask-cors
* Frontend: Next.js App Router, React, JavaScript
* Styling: Tailwind CSS

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the backend:

```powershell
python app.py
```

The API runs at `http://127.0.0.1:5000`.

## Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

## API

### `GET /`

Returns the API status.

### `POST /api/v1/analyze`

Accepts multipart form data with a `profile_text` field:

```text
profile_text=Python developer with Flask and SQL experience
```

All API responses use this shape:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

The current endpoint returns dummy data for the dashboard. It does not yet
perform resume parsing, ATS analysis, skill detection, or AI-based analysis.
