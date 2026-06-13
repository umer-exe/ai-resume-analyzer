# Project Plan - AI Powered Resume and Profile Analyzer

## Completed Phases

### Phase 1: Basic Structure

Created the backend, frontend, service, test, documentation, and Git-ignore
structure.

### Phase 2: Flask Backend Starter

Added the Flask application, CORS support, JSON responses, and API status route.

### Phase 3: Dummy Analyze API

Added `POST /api/v1/analyze` with form-data validation and a stable JSON
response shape.

### Phase 4: Next.js Frontend Starter

Created the standalone Next.js App Router frontend with Tailwind CSS.

### Phase 5: Frontend and Backend Connection

Connected profile text submission to the Flask API with loading, error, and
result states.

### Phase 5.5: Result Flow and UI Refinement

Added the two-column workspace, report preview, loading checklist, sample
profile helper, and tabbed result flow.

### Phase 6: Deterministic Rule-Based Analyzer

Replaced dummy analysis with explainable skill detection and six
profile-quality categories:

* Skills
* Projects
* Experience
* Education
* ATS Keywords
* Formatting

The analyzer returns a weighted score, status, summary, checks, category
feedback, detected skills, and a prioritized action plan.

### Phase 6.5: ML Category Classifier

Added a local TF-IDF classifier that compares Multinomial Naive Bayes and
Logistic Regression during training and saves the better model. ML remains the
only source of resume category prediction.

### Phase 6.6: Architecture and UI/UX Refinement

Separated analyzer rules from analysis flow, kept ML prediction independent,
simplified the API output, refined the three-tab UI, added sample categories,
and improved the presentation of the existing workflow.

### Phase 6.7: Project Structure and Maintainability Refactor

Refactored the completed Phase 6.6 code without changing application behavior:

* Moved analyzer constants, thresholds, terms, and patterns into
  `analyzer_rules.py`.
* Kept `analyzer.py` focused on extraction, scoring, summaries, and action plans.
* Renamed tests by responsibility and isolated analyzer tests from the ML model.
* Renamed the ML entry point to `predict_category()`.
* Split the frontend into `page.js`, `analyzer-data.js`, and
  `report-components.js`.
* Added environment-based API and debug configuration.
* Pinned backend dependencies and removed unused Next.js starter files.

The reusable API structure is already established:

* Flask routes stay thin and return JSON.
* Analyzer and ML logic live in backend services.
* The API response shape is stable.
* The frontend API endpoint is configurable.
* The backend can be reused by another frontend without project-specific code.

### Phase 7: Resume Upload and Text Extraction

Added single-file PDF, DOCX, and TXT resume upload support:

* Files are validated and parsed in memory without permanent storage.
* PDF text is extracted with PyMuPDF.
* DOCX paragraphs and table cells are extracted with python-docx.
* TXT files use UTF-8 text decoding.
* Extracted text uses the existing analyzer and ML classifier.
* Direct profile-text analysis remains available.
* Upload and parser behavior is covered by focused tests.

Phase 7 does not change the analyzer/ML responsibility boundary.

## Next Optional Phase

### Phase 8: Optional AI Upgrade

Optionally add Gemini or OpenAI for richer natural-language feedback after the
deterministic analyzer and resume upload flow are complete.

This phase is optional. It must not replace deterministic scoring or the local
ML category classifier.
