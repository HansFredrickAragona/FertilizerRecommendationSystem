from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.core import build_recommendation, load_assets

app = FastAPI(title="Rule-Based Fertilizer Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Example request body:
# {
#   "crop_label": "Cabbage",
#   "n_status": "Low",
#   "p_status": "Medium",
#   "k_status": "High",
#   "soil_ph": 5.5,
#   "raw_area": 500.0,
#   "area_unit": "Square Meters (sqm)",
#   "selected_inventory_names": ["Urea", "14-14-14"]
# }
# Accepted area_unit values include:
# - "Square Meters (sqm)"
# - "sqm"
# - "Hectares (ha)"
# - "ha"
class RecommendationRequest(BaseModel):
    crop_label: str
    n_status: str
    p_status: str
    k_status: str
    soil_ph: float
    raw_area: float
    area_unit: str = "Square Meters (sqm)"
    selected_inventory_names: list[str] | None = None


@app.get("/catalog")
def catalog():
    inventory, _rules, crop_rules, _ph_rules = load_assets()
    return {
        "crops": sorted(crop_rules.keys()),
        "fertilizers": [
            {"name": item["name"], "n": item["n"], "p": item["p"], "k": item["k"]}
            for item in inventory
        ],
    }


@app.post("/recommendation")
def recommendation(request: RecommendationRequest):
    return build_recommendation(
        crop_label=request.crop_label,
        n_status=request.n_status,
        p_status=request.p_status,
        k_status=request.k_status,
        soil_ph=request.soil_ph,
        raw_area=request.raw_area,
        area_unit=request.area_unit,
        selected_inventory_names=request.selected_inventory_names,
    )
