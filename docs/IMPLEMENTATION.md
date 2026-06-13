# Implementation

## Table of Contents

- [Current Status](#current-status)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Responsibility Boundaries](#responsibility-boundaries)
  - [Rule-Based Analyzer](#rule-based-analyzer)
  - [ML Classifier](#ml-classifier)
  - [Resume Parser](#resume-parser)
- [Request Flow](#request-flow)
- [Backend API](#backend-api)
  - [Health Route](#health-route)
  - [Analyze Route](#analyze-route)
- [Analyzer Implementation](#analyzer-implementation)
  - [Skill Detection](#skill-detection)
  - [Quality Categories](#quality-categories)
  - [Summary and Action Plan](#summary-and-action-plan)
- [ML Classifier Implementation](#ml-classifier-implementation)
  - [TF-IDF Preprocessing](#tf-idf-preprocessing)
  - [Models Evaluated](#models-evaluated)
    - [Multinomial Naive Bayes](#multinomial-naive-bayes)
    - [Logistic Regression](#logistic-regression)
  - [Training and Evaluation](#training-and-evaluation)
  - [Model Selection](#model-selection)
  - [Runtime Prediction](#runtime-prediction)
- [Resume Upload Implementation](#resume-upload-implementation)
- [Frontend Implementation](#frontend-implementation)
  - [Input Flow](#input-flow)
  - [Report States](#report-states)
  - [Result Tabs](#result-tabs)
- [Configuration](#configuration)
- [Testing](#testing)
- [Current Limitations](#current-limitations)

## Current Status

Phase 7 is complete. The application accepts pasted profile text or one PDF,
DOCX, or TXT resume. It returns an overall score, six deterministic quality
scores, detected skills, strengths and improvement areas, an action plan, and
a separate ML resume-category prediction.

The project does not use an external AI API, database, authentication system,
or permanent upload storage.

## Technology Stack

- **Frontend:** Next.js, React, Tailwind CSS, and Lucide icons
- **Backend:** Python, Flask, and Flask-CORS
- **Rule-based analysis:** Python regular expressions and deterministic scoring
- **ML classification:** scikit-learn TF-IDF pipeline
- **File extraction:** PyMuPDF and python-docx
- **Testing:** Python standard-library `unittest`

## Project Structure

```text
backend/
|-- app.py
|-- requirements.txt
|-- ml/
|   `-- train_model.py
|-- models/
|   `-- resume_role_classifier.pkl
|-- services/
|   |-- analyzer.py
|   |-- analyzer_rules.py
|   |-- ml_classifier.py
|   `-- resume_parser.py
`-- tests/
    |-- test_analyzer.py
    |-- test_ml_classifier.py
    `-- test_resume_parser.py

frontend/
`-- app/
    |-- analyzer-data.js
    |-- api.js
    |-- globals.css
    |-- layout.js
    |-- page.js
    `-- report-components.js

docs/
|-- IMPLEMENTATION.md
|-- PLAN.md
`-- proposal.docx
```

## Responsibility Boundaries

The three backend services have separate responsibilities:

| Service | Handles | Does not handle |
| --- | --- | --- |
| Rule-based analyzer | Skill detection, quality scoring, category feedback, summaries, checks, and action plans | Role or category prediction |
| ML classifier | Category labels, display names, confidence, and up to three ranked predictions | Quality scoring or recommendations |
| Resume parser | File validation, text extraction, normalization, and safe parser errors | Analysis or classification |

### Rule-Based Analyzer

Produces deterministic resume-quality analysis without predicting a role or
category.

### ML Classifier

Produces category predictions without calculating quality scores or
recommendations.

### Resume Parser

Converts a validated file to text without analyzing or classifying it.

## Request Flow

```text
Pasted text --------------------+
                                |
Uploaded file -> text extraction+-> API validation
                                   -> rule-based analyzer + ML classifier
                                   -> JSON response
                                   -> report tabs
```

## Backend API

### Health Route

`GET /`

Returns `200` with an API status message in the standard response envelope.

### Analyze Route

`POST /api/v1/analyze`

Accepts multipart form data containing exactly one of `profile_text` or
`resume_file`.

All responses use the same envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

For errors, `success` is `false`, `data` is `null`, and `error` contains a safe
message. HTTP statuses are:

- `200`: health check or successful analysis
- `400`: missing input, conflicting inputs, unsupported file, or parser error
- `404`: unknown route
- `413`: file larger than 2 MB
- `500`: unexpected analysis failure

## Analyzer Implementation

`services/analyzer.py` controls the analysis flow.
`services/analyzer_rules.py` stores catalogs, weights, thresholds, terms,
patterns, and default actions.

### Skill Detection

Skills are matched case-insensitively using escaped, phrase-aware regular
expressions. Boundaries prevent substring false positives such as detecting
`Java` inside `JavaScript`.

Aliases map different forms to canonical skills, such as `js` to `JavaScript`,
database names to `SQL`, `reactjs` to `React`, `ai` to `Artificial
Intelligence`, and `ml` to `Machine Learning`.

The result is a flat, deduplicated skill list in deterministic catalog order.

### Quality Categories

The analyzer evaluates six categories:

| Category | Weight | Main signals |
| --- | ---: | --- |
| Skills | 25% | Number of clearly detected technical skills |
| Projects | 20% | Project terms, tools, action verbs, and measurable outcomes |
| Experience | 15% | Experience terms, actions, duration, and measurable results |
| Education | 15% | Education terms, degree, field, and year |
| ATS Keywords | 15% | Skills, action verbs, and measurable evidence |
| Formatting | 10% | Length, headings, bullets, readable case, and sentence length |

Each category returns:

```json
{
  "category": "Skills",
  "score": 80,
  "status": "Good",
  "feedback": "Category-specific explanation",
  "action": "Suggested improvement"
}
```

Scores are clamped to `0-100` and rounded to whole integers.

Category statuses:

- `Good`: score of 75 or higher
- `Warning`: score from 50 to 74
- `Needs Work`: score below 50

Overall statuses:

- `Strong`: score of 80 or higher
- `Moderate`: score from 60 to 79
- `Needs Work`: score below 60

### Summary and Action Plan

The summary identifies the two strongest and weakest categories. The action
plan prioritizes up to three non-`Good` categories from weakest to strongest
and assigns `High`, `Medium`, or `Low` priority from their status.

The analyzer output contains:

```json
{
  "score": 0,
  "status": "Needs Work",
  "summary": "",
  "checks": {
    "passed": 0,
    "warnings": 0,
    "issues": 0
  },
  "category_analysis": [],
  "skills": [],
  "action_plan": [],
  "ml_prediction": {}
}
```

## ML Classifier Implementation

The project uses supervised text classification to predict the closest resume
category. Model training is implemented in `backend/ml/train_model.py`, while
runtime loading and prediction are handled by
`backend/services/ml_classifier.py`.

### TF-IDF Preprocessing

Both evaluated models use the same `TfidfVectorizer` configuration:

- English stop-word removal
- Unigrams and bigrams through `ngram_range=(1, 2)`
- Terms must appear in at least two documents
- Terms appearing in more than 95% of documents are ignored
- Maximum vocabulary size of 30,000 features
- Sublinear term-frequency scaling

TF-IDF converts resume text into numeric vectors and gives more importance to
terms that are frequent in one resume but less common across the dataset. Both
models use this same vectorizer for a consistent comparison.

### Models Evaluated

#### Multinomial Naive Bayes

Multinomial Naive Bayes is a fast, explainable probabilistic text classifier
that works well with sparse TF-IDF features, making it a useful baseline. Its
independence assumption can miss interactions between resume terms and
phrases, which can reduce accuracy.

#### Logistic Regression

Logistic Regression learns weighted decision boundaries for multiple
categories, handles large sparse feature sets, and provides probabilities
through `predict_proba`. It handled overlapping category vocabulary better than
the baseline and produced the higher test accuracy.

### Training and Evaluation

The classifier was trained and evaluated using the
[Resume dataset by Avishek Majhi](https://www.kaggle.com/datasets/avishekmajhi/resume-dataset?resource=download),
published on Kaggle under the MIT license. It contains `Resume` and `Category`
columns with:

- 8,234 usable resumes
- 10 resume categories
- 6,587 training samples
- 1,647 test samples

Training uses an 80/20 split with `random_state=42`. The split is stratified
when every category contains enough examples, preserving category proportions
between the training and test sets.

Verified results from the current dataset and training configuration:

| Model | Test Accuracy | Result |
| --- | ---: | --- |
| Multinomial Naive Bayes | 78.32% | Not selected |
| Logistic Regression | 91.32% | Selected and saved |

Logistic Regression test summary:

- Macro-average F1-score: 0.89
- Weighted-average F1-score: 0.91
- Test samples: 1,647

These figures describe one reproducible evaluation using the current local
dataset, fixed preprocessing configuration, and fixed train/test split. They do
not guarantee the same accuracy for unrelated resume datasets or real-world
resume text outside the training distribution.

### Model Selection

The higher-accuracy Logistic Regression pipeline is retrained on all 8,234
usable resumes and saved with its TF-IDF vectorizer to:

`backend/models/resume_role_classifier.pkl`

The saved artifact contains `TfidfVectorizer`,
`LogisticRegression(max_iter=1000, random_state=42)`, and 10 learned classes.

The trained pipeline is included in the repository, so users do not need to
download the dataset or retrain the model. The ignored local path
`backend/data/resume_dataset.csv` is used only for optional retraining.

### Runtime Prediction

The absolute model path is derived from the service file location, so loading
does not depend on the terminal's working directory.

The model is cached in memory and reloaded only if the model file modification
time changes.

Prediction output:

```json
{
  "predicted_category": "Python_Developer",
  "display_category": "Python Developer",
  "confidence": 82,
  "source": "ml_classifier",
  "message": null,
  "top_predictions": []
}
```

Confidence values are whole integers from `0-100`. If `predict_proba` is
available, the response can include the top three categories.

Missing models, empty input, and prediction errors return a safe fallback
object rather than crashing the analyzer.

## Resume Upload Implementation

`services/resume_parser.py` supports PDF through PyMuPDF, DOCX through
python-docx, and UTF-8 TXT with BOM support.

Files are read directly from the request and are not written to disk.

PDF pages, DOCX paragraphs and table cells, or TXT content are joined and
normalized by trimming lines and removing blanks. Validation enforces one
supported file up to 2 MB and rejects empty, unreadable, corrupt, or
password-protected documents with safe errors.

Scanned PDFs that require OCR are outside the current implementation.

## Frontend Implementation

### Input Flow

`frontend/app/page.js` manages text, file and sample input, client-side
validation, loading and error states, API submission, and the active tab.

Text and file inputs are mutually exclusive: selecting a file clears text,
while typing or selecting a sample clears the file.

The frontend submits FormData containing only `profile_text` or `resume_file`.

### Report States

The right report area has three states:

- **Empty:** explains what the report will contain
- **Loading:** shows the analysis checklist
- **Results:** displays the completed report

### Result Tabs

The result interface contains:

1. **Overview**
   - Overall score and status
   - Passed, warning, and issue counts
   - ML category prediction and confidence
   - Summary, strongest areas, and improvement areas
2. **Analysis**
   - Six quality-category cards
   - Category scores, feedback, and suggested actions
   - Expandable detected-skills section
3. **Action Plan**
   - Up to three prioritized improvements

Defensive rendering handles missing arrays, invalid percentages, unavailable ML
predictions, and empty skill lists.

## Configuration

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Frontend API override: `NEXT_PUBLIC_API_BASE_URL`
- Backend debug mode: `FLASK_DEBUG=1`
- Maximum resume file size: 2 MB
- Supported languages: English profile text

## Testing

The backend tests are divided by responsibility:

- `test_analyzer.py`: schema, skills, false-positive prevention, scores,
  statuses, action plans, and API errors
- `test_ml_classifier.py`: fallbacks, labels, confidence, top predictions,
  integration, and dataset-column detection
- `test_resume_parser.py`: all supported formats, DOCX tables, invalid files,
  password protection, the exact 2 MB boundary, and upload integration

Setup and run commands are documented separately in
[HOW_TO_RUN.md](../HOW_TO_RUN.md).

## Current Limitations

- No OCR for scanned or image-only PDFs
- No legacy `.doc` support
- No image uploads
- No multiple-file analysis
- No database or saved report history
- No authentication
- No external AI-generated feedback
- No live job matching
