---
name: Add assessment funnel and pages
about: Implements the homepage redesign, assessments flow, results, demos and a minimal assessment API prototype.
assignees:
  - muwajorda

labels:
  - enhancement

---

## Summary

This PR implements the assessment-first redesign for the Jordana Consulting website and adds a minimal FastAPI prototype for scoring and storing assessment results.

### Changes
- New homepage (index.html) with updated hero, Who We Help, The Actual Problem and Assessment centerpiece.
- Services page restructured by lifecycle: ASSESS → DESIGN → BUILD → OPTIMIZE.
- Assessments: landing page, interactive flow, result template.
- Demos reorganized around problems and includes AI Technology Advisor CTA.
- Static CSS and JS assets to run the assessment flow client-side.
- Python FastAPI prototype (api/assessment_api.py) with SQLite persistence.
- README with developer notes.

### How to run locally
See README.md. Key steps:
1. Serve static files (python -m http.server 8000) and open http://localhost:8000/index.html
2. Run API: `uvicorn api.assessment_api:app --reload --port 8000`

### TODO / Next steps
- Replace Google Meet placeholder link with your calendar/scheduling link.
- Add PDF export and email delivery for the full report.
- Integrate with CRM or lead capture if desired.

Please review and merge when ready.
