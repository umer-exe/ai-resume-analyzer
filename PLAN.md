# Project Plan — AI Powered Resume and Profile Analyzer

## Phase 1, Basic Structure

Goal: Create folders, placeholder files, README, PLAN.md, IMPLEMENTATION.md, and .gitignore.

## Phase 2, Flask Backend Starter

Goal: Set up Flask, virtual environment, basic GET / route, and test backend.

## Phase 3, Dummy Analyze API

Goal: Create POST /api/v1/analyze that accepts profile_text and returns dummy JSON.

The API response format should stay clean and consistent because the backend may later be reused by another frontend or system.

## Phase 4, Next.js Frontend Starter

Goal: Create a simple Next.js frontend for this AI course project.

This frontend is for the standalone course project demo.

## Phase 5, Connect Frontend to Backend

Goal: Send profile_text from the Next.js frontend to the Flask backend and display the dummy response.

## Phase 6, Rule Based Analyzer

Goal: Add basic skill detection, ATS score, strengths, weaknesses, role recommendations, and career roadmap.

The main analyzer logic should stay inside backend/services so it remains reusable.

## Phase 7, Resume Upload

Goal: Add PDF, DOCX, and TXT upload support using PyMuPDF and python-docx.

The backend should extract resume text and pass it to the analyzer service.

## Phase 8, UI Polish

Goal: Improve the standalone course project frontend with better result cards, spacing, dashboard layout, and presentation readiness.

## Phase 9, Optional AI Upgrade

Goal: Add Gemini or OpenAI API later for smarter resume feedback if time allows.

## Phase 10, Reusable API Structure

Goal: Keep this project as a separate AI course project, but build the backend in a reusable way.

The Flask backend should be API-first so it can later be connected to another frontend, dashboard, or external system if needed.

Important rules:

* Backend should return JSON only.
* Analyzer logic should stay inside backend/services.
* Flask routes should stay simple.
* API response format should remain consistent.
* Do not add project-specific external integration code for now.
