# AI Powered Resume and Profile Analyzer

A basic full-stack resume and profile analysis project for students and job
seekers. The Next.js frontend sends profile text to a reusable Flask API and
displays a profile score, grouped skills, category feedback, an ML category
prediction, recommended improvements, and an action plan.

Phase 6 uses deterministic, explainable rules for skill detection, profile
scoring, category analysis, recommendations, and the action plan.

Phase 6.5 adds an optional local TF-IDF classifier for resume category
prediction. It supports the rule-based report and does not replace its scores,
skill detection, recommendations, or action plan. The ML classifier is the
only category prediction source.

## Tech Stack

* Backend: Python, Flask, flask-cors, pandas, scikit-learn, joblib
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

## Train the Optional ML Classifier

Place the dataset at:

```text
backend/data/resume_dataset.csv
```

Then run:

```powershell
cd backend
python ml/train_model.py
```

The script compares TF-IDF with Multinomial Naive Bayes and Logistic
Regression, then saves the better pipeline to
`backend/models/resume_role_classifier.pkl`. ML prediction remains optional
until this model has been trained.

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

The endpoint returns deterministic rule-based analysis. It does not perform
resume upload or document parsing and does not use Gemini, OpenAI, or another
external AI API.

## Tests

```powershell
cd backend
python -m unittest discover -s tests
```
