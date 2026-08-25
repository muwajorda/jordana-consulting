# Jordana Consulting — Assessment README

This branch adds a minimal assessment product and a prototype API to score and store results.

Running the API (local development)
- Requires Python 3.10+
- Install dependencies: pip install fastapi uvicorn pydantic
- Run: uvicorn api.assessment_api:app --reload --port 8000

The static site pages are simple HTML files under the repo root. The client-side JS calls the API endpoints:
- POST /api/assess — submit answers, returns token and summary
- POST /api/claim/{token} — provide email to claim full report
- GET /api/result/{token} — fetch report (full report only returned after claim)

Scheduling integration: the site places a Google Meet placeholder link for the "Book an Architecture Review" CTA. Replace with a dedicated Google Calendar Meet link or integrate with your scheduling workflow.

Assessment gating: this implementation requires email to view/download the full report (recommended). The summary is immediately available after the quick analysis.
