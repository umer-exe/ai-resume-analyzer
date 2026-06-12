# AI Powered Resume and Profile Analyzer

A basic full-stack resume and profile analysis project for students and job
seekers. The Next.js frontend sends profile text to a reusable Flask API and
displays a profile score, detected skills, category feedback, an ML category
prediction, and a focused action plan.

Phase 6 uses deterministic, explainable rules for skill detection, profile
scoring, category analysis, and the action plan.

Phase 6.5 adds an optional local TF-IDF classifier for resume category
prediction. It supports the rule-based report and does not replace its scores,
skill detection, or action plan. The ML classifier is the only category
prediction source.

Phase 6.6 simplifies the analyzer response to a flat, deterministic `skills`
array, six category actions, and one prioritized `action_plan`. Rule-based code
handles profile quality only; dataset category labels come only from
`ml_prediction`.

## Tech Stack

* Backend: Python, Flask, flask-cors, pandas, scikit-learn, joblib
* Frontend: Next.js App Router, React, JavaScript, lucide-react
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

The `skills` field is a flat ordered array of canonical detected skills.
The `action_plan` field contains up to three actions selected from the weakest
quality categories. Separate recommendation and next-step collections are not
generated.
Resume category labels and confidence values are returned separately under
`ml_prediction`.

## Tests

```powershell
cd backend
python -m unittest discover -s tests
```
