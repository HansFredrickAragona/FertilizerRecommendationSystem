# Project status (public handoff summary)

Sanitized mirror of the local `agent-memory/` folder — safe to commit.
Updated: 2026-08-26

## Status

Day 1 roadmap complete: API hardened (CORS restricted, catalog endpoint,
smoke tests) and Next.js frontend built (recommendation form, standard and
farmer-selected result sets, pH guidance, session history, PDF export).
All validation passing. Changes not yet committed.

## Key decisions

- Architecture: **MVC** — `engine/` (Model), `api/` (Controller),
  `ui/` + `frontend/` (Views), protected JSON data under `rules/`.
- Frontend: Next.js in `frontend/`, same repo; hosting target Vercel.
- Ruff adopted as the single linter/formatter.
- Added read-only `GET /catalog` so frontends consume crop/fertilizer data
  from the engine's rules instead of duplicating domain data.
- Two-layer memory discipline documented in AGENTS.md.

## Completed

- Restructured to MVC layout; loaders, imports, Procfile, and docs updated.
- Rewrote AGENTS.md (constitution), CONTRIBUTING.md, ARCHITECTURE.md,
  PORTFOLIO_ROADMAP.md, and README.md.
- Added LICENSE (MIT), ruff.toml, PR template, bug-report template.
- `.opencode/` harness configured: permission-gated edits, 6-agent team,
  `/handoff`, `/quality-gate`, `/session-save` commands.
- CI workflow updated for the new layout.
- API: CORS restricted to the frontend dev origin; `GET /catalog` added;
  6 API smoke tests added (valid request, unknown crop, invalid unit/area,
  missing fields, CORS preflight allow/deny).
- Frontend: Next.js scaffold, typed API client, recommendation form
  (crop, N/P/K status, pH, area/unit, fertilizer selection), both result
  sets rendered as tables, pH guidance box, loading/error states, CAR
  disclaimer, session-only history with tab-close warning, print-based PDF
  export.
- UI redesign (bb2cde4): iOS-style minimalism, compact horizontal form
  layout (NPK/area/pH side-by-side), button-style fertilizer selection
  with selected-state color change, multi-session PDF export (current/all/selected).
- Engine enhancements: `farmer_selected_mix`, `farmer_supplemented_mix`,
  `selection_status` (sufficient/supplementable/insufficient/none).

## Known issues / next steps

1. Add Streamlit to requirements.txt (approval required).
2. Unit convention confirmed: rules use elemental P/K (per Benguet State
   University reference); fertilizer grades are %N-%P-%K.
3. Before deployment: add production Vercel origin to CORS allowlist.
4. Optional polish: sessionStorage-backed history, richer PDF export.

## Validation results

- compileall OK; ruff check pass; ruff format --check pass
- unittest 11/11 pass (engine + API); rules/*.json parse correctly
- `next build`: success; live uvicorn smoke test of /catalog and
  /recommendation returned 200
