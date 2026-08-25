# Project status (public handoff summary)

Sanitized mirror of the local `agent-memory/` folder — safe to commit.
Updated: 2026-08-25

## Status

Foundation complete: documentation, agent harness, and MVC restructure done.
Next: CI workflow update (pending approval) and frontend scaffolding.

## Key decisions

- Architecture: **MVC** — `engine/` (Model), `api/` (Controller),
  `ui/` + `frontend/` (Views), protected JSON data under `rules/`.
- Frontend: Next.js in `frontend/`, same repo; hosting target Vercel.
- Ruff adopted as the single linter/formatter.
- Two-layer memory discipline documented in AGENTS.md.
- Timeline: 2-3 days to portfolio-ready (frontend, MVC structure, PDF export).

## Completed

- Restructured to MVC layout; loaders, imports, Procfile, and docs updated.
- Rewrote AGENTS.md (constitution), CONTRIBUTING.md, ARCHITECTURE.md,
  PORTFOLIO_ROADMAP.md, and README.md.
- Added LICENSE (MIT), ruff.toml, PR template, bug-report template.
- Ruff installed; 39 lint findings fixed; codebase formatted.
- `.opencode/` harness configured: permission-gated edits, 6-agent team
  (coordinator + specialists), `/handoff`, `/quality-gate`, `/session-save`
  commands.

## Known issues / next steps

1. Update the CI workflow for the new layout (Ruff steps, `rules/*.json`
   glob, module paths) — pending owner approval.
2. Add Streamlit to requirements.txt (approval required).
3. Scaffold the Next.js frontend, add API smoke tests, restrict CORS
   (Day 1 of roadmap).
4. Verify P/P2O5 and K/K2O unit labeling with the owner.

## Validation results

- compileall OK; ruff check pass; ruff format --check pass
- unittest 5/5 pass; rules/*.json parse correctly
