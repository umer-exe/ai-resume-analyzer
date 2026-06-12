# Implementation

## Current Status

Phase 6.7 is complete. Phase 7 resume upload and document parsing have not been
implemented.

The application currently accepts profile text and returns:

* A deterministic overall profile score and status
* Six profile-quality category scores
* Detected technical skills
* Category feedback and a focused action plan
* A separate ML resume category prediction

## Architecture

```text
backend/
|-- app.py
|-- ml/train_model.py
|-- models/resume_role_classifier.pkl
|-- services/
|   |-- analyzer.py
|   |-- analyzer_rules.py
|   |-- ml_classifier.py
|   `-- resume_parser.py
`-- tests/
    |-- test_analyzer.py
    `-- test_ml_classifier.py

frontend/app/
|-- analyzer-data.js
|-- globals.css
|-- layout.js
|-- page.js
`-- report-components.js
```

Responsibilities:

* `app.py`: HTTP validation and JSON responses
* `analyzer.py`: skill detection, quality scoring, summary, and action plan
* `analyzer_rules.py`: deterministic catalogs, weights, thresholds, and patterns
* `ml_classifier.py`: saved-model loading and resume category prediction
* `train_model.py`: TF-IDF model training and selection
* `page.js`: frontend state, profile form, and API submission
* `analyzer-data.js`: frontend configuration and sample profiles
* `report-components.js`: empty, loading, and result report views

The rule-based analyzer does not predict roles or categories. Category
prediction comes only from the trained ML classifier.

## Configuration

* Backend API: `http://127.0.0.1:5000`
* Frontend: `http://localhost:3000`
* Optional frontend API override: `NEXT_PUBLIC_API_URL`
* Optional backend debug mode: `FLASK_DEBUG=1`
* Local training data: `backend/data/resume_dataset.csv`

`backend/data/` is ignored by Git.

## Validation

```powershell
cd backend
python -m unittest discover -s tests
python -m py_compile app.py services/analyzer.py services/analyzer_rules.py services/ml_classifier.py ml/train_model.py

cd ../frontend
npm run lint
npm run build
```

## Next Step

Phase 7 will add PDF, DOCX, and TXT resume upload and text extraction while
reusing the existing analyzer and ML services.
