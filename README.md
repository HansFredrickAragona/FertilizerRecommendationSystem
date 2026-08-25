# Fertilizer Recommendation System

A deterministic, rule-based fertilizer decision-support prototype designed for
**CAR (Cordillera Administrative Region) produce and land conditions**.

Enter a crop, soil N/P/K statuses, pH, and land area — the engine computes
nutrient targets, assesses soil pH independently, and generates fertilizer mix
recommendations from an approved catalogue, including combinations built around
fertilizers the farmer already has.

> **Disclaimer:** this is a decision-support prototype. It does not replace
> site-specific soil analysis or advice from a qualified agricultural
> professional. Results are designed for CAR produce and are not assured for
> other locations.

## Features

- **Crop nutrient targets** — per-hectare N/P/K requirements for 41 crops,
  scaled to any area (sqm or ha)
- **Independent pH assessment** — liming / borderline / acceptable / gypsum
  guidance, separate from nutrient math but returned together
- **Two recommendation sets**:
  - *Standard* — mixes from the full approved fertilizer catalogue
  - *Farmer-selected* — mixes built around preselected fertilizers (uses at
    least one selected item whenever possible, prefers all)
- **No over-fertilization** — the solver never exceeds a nutrient target
- **FastAPI backend** + Streamlit reference UI; Next.js frontend in progress

## Architecture

MVC: the engine (`engine/core.py`) is the Model, FastAPI (`api/main.py`) is
the Controller, and both UIs are Views that only render API responses.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

Streamlit UI:

```powershell
streamlit run ui/streamlit_app.py
```

API:

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Example request to `POST /recommendation`:

```json
{
  "crop_label": "Cabbage",
  "n_status": "Low",
  "p_status": "Medium",
  "k_status": "High",
  "soil_ph": 5.5,
  "raw_area": 500,
  "area_unit": "Square Meters (sqm)",
  "selected_inventory_names": ["Urea", "Ammonium Phosphate"]
}
```

## Repository structure

| Path | Purpose |
| --- | --- |
| `engine/core.py` | Active recommendation engine (`build_recommendation`). |
| `api/main.py` | FastAPI endpoint (`POST /recommendation`). |
| `ui/streamlit_app.py` | Streamlit reference UI. |
| `engine/prototype_solver.py` | Prototype inventory-aware solver (not wired into the engine). |
| `frontend/` | Next.js portfolio frontend (in progress). |
| `rules/crop_npk_rules.json` | Crop N/P/K targets (protected agronomic data). |
| `rules/engine_rules.json` | Solver constraints and policy (protected). |
| `rules/ph_rules.json` | pH thresholds and amendment guidance (protected). |
| `rules/fertilizers.json` | Fertilizer catalogue with N/P/K analyses (protected). |
| `rules/orig_crop_npk.json` | Original reference data (protected). |
| `tests/` | Engine regression tests. |
| `docs/` | Architecture, roadmap, and project status. |

The JSON rule files are final domain data — changes require explicit owner
approval with a cited agronomic source.

## Development

Read [AGENTS.md](AGENTS.md) (project constitution) and
[CONTRIBUTING.md](CONTRIBUTING.md) (workflow and quality gate) before making
changes. Validation:

```powershell
python -m compileall -q .
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
```

## Known limitations

- The active solver is phosphorus-first greedy; it always produces valid
  (never excessive) mixes but not necessarily the most balanced ones.
- pH advice is universal, not crop-specific, and does not adjust fertilizer
  targets.
- P values follow the P₂O₅ convention and K follows K₂O, matching the UI
  labels; verify locally before field application.

## Roadmap

See [docs/PORTFOLIO_ROADMAP.md](docs/PORTFOLIO_ROADMAP.md): Next.js frontend,
session PDF export, and deployment on Vercel.

## License

[MIT](LICENSE) © 2026 Hans Fredrick Aragona
