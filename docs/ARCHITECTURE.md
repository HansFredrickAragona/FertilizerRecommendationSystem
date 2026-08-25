# Architecture

## Current system

```text
Streamlit UI (`ui/streamlit_app.py`) ─┐
                                      ├─> `build_recommendation` (`engine/core.py`)
FastAPI endpoint                       │       ├─ crop N/P/K targets
(`api/main.py`) ───────────────────────┘       ├─ pH assessment
                                               ├─ area scaling
                                               ├─ inventory sufficiency check
                                               └─ standard fertilizer mixes
                                                        │
                             ┌──────────────────────────┴─────────────────────────┐
                             │                                                    │
                  JSON agronomic/configuration data                    recommendation JSON
                  under `rules/`                                        to UI or API caller
```

## Target architecture: MVC

The project is small-scale, so **MVC (Model–View–Controller)** is the chosen
architecture — not a heavier layered/Clean design. The target layout keeps the
existing engine logic and reorganizes it by responsibility:

```text
FertilizerRecommendationSystem/
├── engine/                 # Model: active engine + rules loading
│   ├── core.py             #   build_recommendation (public entry point)
│   └── prototype_solver.py #   prototype; not wired into the engine
├── api/                    # Controller: request validation -> Model -> response
│   └── main.py             #   POST /recommendation
├── ui/                     # View (reference): Streamlit form/results display
│   └── streamlit_app.py
├── frontend/               # View (portfolio): Next.js dashboard
│   ├── app/                #   pages/routes (Next.js App Router)
│   ├── components/         #   presentation-only React components
│   └── lib/api.ts          #   single client for POST /recommendation
├── rules/                  # domain data (protected)
└── tests/                  # unit + API + end-to-end tests
```

MVC responsibilities:

| Layer | Responsibility | Rule |
| --- | --- | --- |
| **Model** | N/P/K targets, pH assessment, area scaling, mix solving. All agronomic computation. | No UI or HTTP concerns; deterministic. |
| **Controller** | FastAPI request/response handling, validation, error mapping. | Thin adapter over the Model; no calculation logic. |
| **View** | Streamlit reference UI and the Next.js frontend. | Render API responses only; never reimplement N/P/K math in the browser or Python views. |

Migration is incremental: `engine/core.py` acts as the Model, `api/main.py`
as the Controller, and both UIs are Views. If the engine grows, split it into
modules within `engine/` (e.g. `targets.py`, `ph.py`, `solver.py`) without
changing the public contract.

## Request flow

`build_recommendation` receives a crop label, N/P/K soil statuses, pH, area,
area unit, and optional selected fertilizer names. It then:

1. maps display crop names through `THESIS_CROP_MAP`;
2. loads the inventory and rule files from the repository root;
3. converts square metres to hectares when required;
4. looks up kg/ha N/P/K targets and scales them to the supplied land area;
5. evaluates pH independently (liming required / borderline / acceptable /
   gypsum recommended);
6. checks whether the selected fertilizers alone can form a valid mix; and
7. generates up to ten standard mixes, sorted by total weight.

## Data contracts

### API request

`POST /recommendation` accepts:

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

### Core response

The result includes the normalized crop and area, per-hectare and total N/P/K
targets, the pH result, the farmer-selected set (at least one selected item
whenever possible, preferring all of them), inventory sufficiency reporting,
and standard mixes from the full catalogue. Frontends render this response;
they must not reimplement calculations.

## Important constraints

- `engine_rules.json` currently forbids nutrient over-fertilization.
- The active solver is phosphorus-first: it selects a P-bearing fertilizer,
  then fills remaining N and K with pure sources.
- A compound fertilizer is rejected when it would exceed an N or K target.
- pH advice is independent from N/P/K quantities but returned in the same
  response.
- JSON rule files are runtime dependencies and live under `rules/`; do not
  move or rename them unless the loader and tests are deliberately updated.

## Frontend and deployment direction

- Frontend framework: **Next.js**, living in this same repository under
  `frontend/`.
- It consumes only the FastAPI contract; CORS must be restricted to approved
  origins before deployment (current setting is permissive `*`).
- Default deployment target: **Vercel** for the Next.js frontend, with the
  FastAPI hosting approach validated before production release.
- Recommendation history exists only during the active browser session, with
  an unsaved-results warning before tab close and user-triggered PDF export.
