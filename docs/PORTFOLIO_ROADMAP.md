# Portfolio-readiness roadmap

## Goal

Present the existing deterministic fertilizer engine through a polished
Next.js frontend, hosted publicly so it can be showcased in a portfolio.
Target window: **2-3 focused working days**.

## Timeline

### Day 1 - Foundation and architecture (MVC)

- Confirm MVC boundaries: engine = Model, FastAPI = Controller, UIs = Views.
- Add/verify automated engine tests; validate JSON rule files locally and in CI.
- Resolve dependency declarations (Streamlit, Ruff, test deps) with approval.
- Restrict CORS to the frontend origin; add API smoke tests.
- Scaffold `frontend/` (Next.js) with a single API client for
  `POST /recommendation`.

### Day 2 - Frontend build-out

- Responsive form: crop, N/P/K statuses, pH, area + unit, farmer-selected
  fertilizers.
- Render both recommendation sets: **standard** and **farmer-selected**,
  plus nutrient targets, independent pH guidance, loading/error states.
- Educational content: what N/P/K and pH mean and how to interpret results.
- Session-only recommendation history with unsaved-results warning on tab close.

### Day 3 - Export, polish, deploy

- User-triggered **PDF export** of the recommendation report.
- Sample/demo data so non-agricultural visitors can try it immediately.
- Professional agricultural-dashboard styling; accessibility and responsive
  checks.
- Public CAR-produce disclaimer visible before reliance on results.
- Deploy to Vercel (frontend; validated FastAPI approach for the backend),
  production CORS, screenshots for the portfolio write-up.

## Post-launch backlog (after the 3-day window)

- Saved/exported report improvements beyond session-only PDF.
- Optional AI assistant under the guidance-only contract in `AGENTS.md`.
- Coverage expansion toward the ~80% target across API tests.
- Deployment hardening review by the security reviewer role.

## Decisions already made

- Architecture: **MVC** (small scale; no heavier layered design).
- Frontend: Next.js, same repository, `frontend/` directory.
- Hosting: Vercel as default target; FastAPI hosting validated before release.
- No login/database; history is session-only with user-triggered PDF export.
- Disclaimer wording approved in `AGENTS.md` (CAR-produce decision-support).
