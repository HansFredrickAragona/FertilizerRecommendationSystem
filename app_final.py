import json
from pathlib import Path

THESIS_CROP_MAP = {
    "Ampalaya": "Ampalaya",
    "Batao": "Batao",
    "String Beans": "String Beans",
    "Snap Bean": "String Beans",
    "Baguio Beans": "Baguio Beans",
    "Lima (Patani)": "Lima (Patani)",
    "Winged Beans": "Winged Beans",
    "Seguidillas": "Seguidillas",
    "Dwarf Beans": "Dwarf Beans",
    "Chayote": "Chayote",
    "Cucumber": "Cucumber",
    "Parsnip": "Parsnip",
    "Patani": "Patani",
    "Patola": "Patola",
    "Peas": "Peas",
    "Carrot": "Carrot",
    "Garlic": "Garlic",
    "Onion": "Onion",
    "Ginger (Local)": "Ginger (Local)",
    "Ginger (Improved)": "Ginger (Improved)",
    "Potato": "Potato",
    "Radish/Turnips": "Radish/Turnips",
    "Asparagus": "Asparagus",
    "Broccoli": "Broccoli",
    "Cabbage": "Cabbage",
    "Cauliflower": "Cauliflower",
    "Cabbage (Head)": "Cabbage (Head)",
    "Lettuce": "Lettuce",
    "Mustard": "Mustard",
    "Pechay": "Pechay",
    "Celery": "Celery",
    "Bell Pepper": "Bell Pepper",
    "Green (siling-haba) Pepper": "Green (siling-haba) Pepper",
    "Pepper": "Pepper",
    "Black Pepper": "Black Pepper",
    "Eggplant": "Eggplant",
    "Okra (Local)": "Okra (Local)",
    "Okra (Hybrid)": "Okra (Hybrid)",
    "Tomato": "tomatoes",
    "tomatoes": "tomatoes",
    "Squash": "Squash",
    "Basil": "Basil",
    "Mint herb": "Mint herb"
}

def get_project_root() -> Path:
    """Resolve the project root directory for the rule-based engine.

    This function searches upward from the current file until it finds a
    directory containing the expected "data" folder. It ensures the rest of
    the app can reliably load JSON assets from the rule-based data directory.

    Returns:
        Path: The project root directory containing the "data" folder.
    """
    current = Path(__file__).resolve()
    return current.parent

def load_assets():
    """Load rule engine JSON assets from the project data folder.

    Reads the fertilizer inventory, engine rules, crop NPK target rules, and
    pH adjustment rules from JSON files under the configured data directory.

    Returns:
        tuple: A tuple containing (inventory, rules, crop_rules, ph_rules).
    """
    base_dir = get_project_root()

    with open(base_dir / "fertilizers.json", "r", encoding="utf-8") as f:
        inventory = json.load(f)["inventory"]
    with open(base_dir / "engine_rules.json", "r", encoding="utf-8") as r:
        rules = json.load(r)["engine_logic"]
    with open(base_dir / "crop_npk_rules.json", "r", encoding="utf-8") as c:
        crop_rules = json.load(c)
    with open(base_dir / "ph_rules.json", "r", encoding="utf-8") as p:
        ph_rules = json.load(p)

    return inventory, rules, crop_rules, ph_rules

def parse_target_value(val):
    """Normalize a crop nutrient target value into a float.

    This helper accepts numeric values and range strings such as "10-12" or
    "6–8". If a range string is provided, it returns the midpoint.

    Args:
        val: The raw value from crop target rules, which may be int, float, or str.

    Returns:
        float: The parsed numeric target, or 0.0 on failure.
    """
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, str) and ("–" in val or "-" in val):
        val = val.replace("–", "-")
        parts = [float(p.strip()) for p in val.split("-")]
        return sum(parts) / len(parts)
    try:
        return float(val)
    except:
        return 0.0

def get_fertilizer_recommendation(crop_name, n_status, p_status, k_status, crop_rules):
    """Compute the base N-P-K target rates for a specific crop and soil status.

    Args:
        crop_name: The normalized crop key used by crop rules.
        n_status: Nitrogen soil status code (e.g. "Low", "Medium", "High").
        p_status: Phosphorus soil status code (e.g. "Low", "Medium", "High").
        k_status: Potassium soil status code (e.g. "Low", "Medium", "High").
        crop_rules: Mapping of crop names to NPK target rule definitions.

    Returns:
        tuple|None: Target rates (N, P, K) in kg/ha or None if crop data is missing.
    """
    crop_data = crop_rules.get(crop_name)
    if not crop_data: return None
    t_n = parse_target_value(crop_data["N"].get(n_status, 0))
    t_p = parse_target_value(crop_data["P"].get(p_status, 0))
    t_k = parse_target_value(crop_data["K"].get(k_status, 0))
    return t_n, t_p, t_k

def run_ph_engine(data, ph_rules):
    """Evaluate the universal soil pH rule engine.

    Applies the universal pH rule set from ph_rules.json. Rules are checked
    in order and the first matching condition is applied. Returns pH status,
    required action (liming/gypsum/none), and any borderline warnings.

    Note: pH multipliers have been removed per agronomic standards
    (BSU La Trinidad consultation). NPK targets are no longer adjusted by pH.

    Args:
        data: A dictionary containing at least a soil_ph value.
        ph_rules: Loaded pH rule definitions from ph_rules.json.

    Returns:
        dict: pH engine output including ph_status, ph_action, borderline_warning,
              borderline_message, recommendation_message, perfect_ph, and soil_ph.
    """
    soil_ph = data["soil_ph"]
    constants = ph_rules.get("constants", {})
    perfect_ph = constants.get("perfect_ph", 6.5)
    liming_max = constants.get("liming_trigger_ph_max", 5.0)
    gypsum_min = constants.get("gypsum_trigger_ph_min", 7.5)
    borderline_low = constants.get("borderline_low_ph", 5.1)
    borderline_high = constants.get("borderline_high_ph", 7.4)

    # Evaluate rules in order: liming, borderline low, acceptable, borderline high, gypsum
    if soil_ph <= liming_max:
        matched_rule = next(r for r in ph_rules["ph_rules"] if r["id"] == "PH_001")
    elif soil_ph == borderline_low:
        matched_rule = next(r for r in ph_rules["ph_rules"] if r["id"] == "PH_002")
    elif soil_ph >= gypsum_min:
        matched_rule = next(r for r in ph_rules["ph_rules"] if r["id"] == "PH_005")
    elif soil_ph == borderline_high:
        matched_rule = next(r for r in ph_rules["ph_rules"] if r["id"] == "PH_004")
    else:
        matched_rule = next(r for r in ph_rules["ph_rules"] if r["id"] == "PH_003")

    result = dict(matched_rule["then"])
    result["soil_ph"] = soil_ph
    result["perfect_ph"] = perfect_ph
    return result

def solve_npk(t_n, t_p, t_k, inventory, rules, area, unit_label):
    """Generate fertilizer mix options based on target nutrient requirements.

    This algorithm uses a pure-n fertilizer, a pure-k fertilizer, and one or more
    compound P-bearing fertilizers to generate candidate prescriptions.

    Args:
        t_n: Total nitrogen requirement for the field.
        t_p: Total phosphorus requirement for the field.
        t_k: Total potassium requirement for the field.
        inventory: Loaded fertilizer inventory list.
        rules: Engine rule definitions including constraints and output formatting.
        area: The raw area value entered by the user.
        unit_label: The unit string used for display in prescriptions.

    Returns:
        list: Sorted fertilizer combination results limited by rule constraints.
    """
    results = []
    max_target = max(t_n, t_p, t_k)
    precision = 3 if max_target < 1.0 else rules["constraints"]["precision_decimals"]
    allow_over = rules["constraints"]["allow_over_fertilization"]

    n_fillers = [f for f in inventory if f["n"] > 0 and f["p"] == 0 and f["k"] == 0]
    k_fillers = [f for f in inventory if f["k"] > 0 and f["n"] == 0 and f["p"] == 0]
    p_sources = [f for f in inventory if f["p"] > 0]

    for p_fert in p_sources:
        for n_filler in (n_fillers if n_fillers else [None]):
            for k_filler in (k_fillers if k_fillers else [None]):

                qty_p = (t_p / p_fert["p"]) * 100 if p_fert["p"] > 0 else 0

                n_provided = (qty_p * p_fert["n"]) / 100
                p_provided = (qty_p * p_fert["p"]) / 100
                k_provided = (qty_p * p_fert["k"]) / 100

                rem_n = t_n - n_provided
                rem_k = t_k - k_provided

                if not allow_over and (rem_n < -0.01 or rem_k < -0.01):
                    continue

                if rem_n > 0.01 and n_filler is None:
                    continue

                if rem_k > 0.01 and k_filler is None:
                    continue

                qty_n = (max(0, rem_n) / n_filler["n"]) * 100 if rem_n > 0.01 and n_filler else 0
                qty_k = (max(0, rem_k) / k_filler["k"]) * 100 if rem_k > 0.01 and k_filler else 0

                total_n = n_provided + ((qty_n * n_filler["n"]) / 100 if n_filler else 0)
                total_k = k_provided + ((qty_k * k_filler["k"]) / 100 if k_filler else 0)

                fmt = rules["output_format"]
                prescription = []
                if qty_n > 0:
                    prescription.append(fmt.format(
                        qty=round(qty_n, precision),
                        area=area,
                        unit=unit_label,
                        fertilizer_name=n_filler["name"]
                    ))
                prescription.append(fmt.format(
                    qty=round(qty_p, precision),
                    area=area,
                    unit=unit_label,
                    fertilizer_name=p_fert["name"]
                ))
                if qty_k > 0:
                    prescription.append(fmt.format(
                        qty=round(qty_k, precision),
                        area=area,
                        unit=unit_label,
                        fertilizer_name=k_filler["name"]
                    ))

                results.append({
                    "Source": " + ".join(filter(None, [
                        n_filler["name"] if qty_n > 0 else None,
                        p_fert["name"],
                        k_filler["name"] if qty_k > 0 else None,
                    ])),
                    "Prescription": prescription,
                    "Total Weight": qty_n + qty_p + qty_k,
                    "Applied N": total_n,
                    "Applied P": p_provided,
                    "Applied K": total_k,
                })

    return sorted(results, key=lambda x: x["Total Weight"])[:rules["constraints"]["max_combinations"]]


def check_fertilzer_input(t_base_n, t_base_p, t_base_k, selected_inventory_names, area, unit_label):
    """Validate selected fertilizer inventory by attempting to solve the required
    NPK mix using only the selected fertilizers.

    Args:
        t_base_n: Total nitrogen requirement for the target area.
        t_base_p: Total phosphorus requirement for the target area.
        t_base_k: Total potassium requirement for the target area.
        selected_inventory_names: List of fertilizer names selected by the user.
        area: The area for which to calculate the prescription.
        unit_label: The unit label for the area.

    Returns:
        dict: {'valid': bool, 'reason': str, 'details': dict | None}
    """
    inventory, rules, _, _ = load_assets()
    selected_inventory_names = selected_inventory_names or []

    if not selected_inventory_names:
        return {
            "valid": False,
            "reason": "No fertilizers selected. Please choose at least one fertilizer to evaluate.",
            "details": None,
        }

    available_names = [f["name"] for f in inventory]
    invalid_names = [name for name in selected_inventory_names if name not in available_names]
    if invalid_names:
        return {
            "valid": False,
            "reason": f"The following fertilizer(s) were not recognized: {', '.join(invalid_names)}.",
            "details": None,
        }

    selected_inventory = [f for f in inventory if f["name"] in selected_inventory_names]

    # Core check: attempt to solve NPK using only the selected fertilizers
    try:
        candidate_mix = solve_npk(
            t_base_n, t_base_p, t_base_k,
            selected_inventory, rules,
            area=area, unit_label=unit_label
        )
    except StopIteration:
        return {
            "valid": False,
            "reason": (
                "The selected fertilizers cannot form a valid combination. "
                "The solver requires at least one pure N-source, one pure K-source, "
                "and a compatible P-source among the selected items."
            ),
            "details": None,
        }
    except Exception as exc:
        return {
            "valid": False,
            "reason": f"The solver encountered an error with the selected fertilizers: {exc}",
            "details": None,
        }

    if not candidate_mix:
        return {
            "valid": False,
            "reason": (
                "The selected fertilizers could not produce a valid mix for the "
                "required NPK targets. Try adding fertilizers that cover the missing nutrients."
            ),
            "details": None,
        }

    best = candidate_mix[0]
    return {
       "valid": True,
        "reason": (
            f"The selected fertilizers can solve the required NPK targets using "
            f"'{best['Source']}'."
        ),
        "details": best,
    }


def normalize_area(raw_area, area_unit):
    """Convert user area input into hectares and derive display unit label.

    Args:
        raw_area: The numeric area value entered by the user.
        area_unit: The selected area unit string, either "sqm"/"Square Meters (sqm)" or
            "ha"/"Hectares (ha)".

    Returns:
        tuple: The converted area in hectares and the normalized unit label.

    Raises:
        ValueError: If the area_unit is not recognized.
    """
    normalized = area_unit.strip().lower()
    if "sqm" in normalized or "square meter" in normalized:
        return raw_area / 10000.0, "sqm"
    if "ha" in normalized or "hectare" in normalized:
        return raw_area, "ha"
    raise ValueError(
        f"Unsupported area_unit '{area_unit}'. Use 'sqm' or 'ha', or values like 'Square Meters (sqm)' or 'Hectares (ha)'."
    )


def build_recommendation(crop_label, n_status, p_status, k_status, soil_ph, raw_area,
                         area_unit="Square Meters (sqm)", selected_inventory_names=None):
    """Build a full fertilizer recommendation payload for external use.

    This method loads the engine assets, resolves crop targets, applies pH
    adjustments, scales values by land area, and computes both standard and
    adjusted fertilizer mix recommendations.

    Args:
        crop_label: User-facing crop label (e.g. "Cabbage").
        n_status: Nitrogen status code.
        p_status: Phosphorus status code.
        k_status: Potassium status code.
        soil_ph: Measured soil pH value.
        raw_area: Numeric area from the user input.
        area_unit: The area unit string, defaulting to square meters.
        selected_inventory_names: Optional list of fertilizer names the user has.

    Returns:
        dict: Recommendation results including targets, mixes, pH output, and sufficiency state.
    """
    inventory, rules, crop_rules, ph_rules = load_assets()
    selected_crop = THESIS_CROP_MAP.get(crop_label, crop_label)

    if selected_crop not in crop_rules:
        raise ValueError(f"Crop '{selected_crop}' is not configured in crop_npk_rules.json")

    area_ha, unit_label = normalize_area(raw_area, area_unit)
    
    rec = get_fertilizer_recommendation(selected_crop, n_status, p_status, k_status, crop_rules)
    if rec is None:
        raise ValueError("Unable to compute fertilizer recommendation for the selected crop and soil status.")

    base_n, base_p, base_k = rec
    ph_res = run_ph_engine({"soil_ph": soil_ph}, ph_rules)

    t_base_n, t_base_p, t_base_k = base_n * area_ha, base_p * area_ha, base_k * area_ha

    selected_inventory_names = selected_inventory_names or []
    inventory_check = check_fertilzer_input(t_base_n, t_base_p, t_base_k, selected_inventory_names,raw_area, unit_label)
    user_inventory = [f for f in inventory if f["name"] in selected_inventory_names]

    has_n = any(f["n"] > 0 for f in user_inventory)
    has_p = any(f["p"] > 0 for f in user_inventory)
    has_k = any(f["k"] > 0 for f in user_inventory)
    missing_nutrients = []
    if t_base_n > 0 and not has_n: missing_nutrients.append("Nitrogen (N)")
    if t_base_p > 0 and not has_p: missing_nutrients.append("Phosphorus (P)")
    if t_base_k > 0 and not has_k: missing_nutrients.append("Potassium (K)")

    base_mix = solve_npk(t_base_n, t_base_p, t_base_k, inventory, rules, raw_area, unit_label)

    return {
        "selected_crop_label": crop_label,
        "selected_crop": selected_crop,
        "area_ha": area_ha,
        "unit_label": unit_label,
        "raw_area": raw_area,
        "base_targets_per_ha": {"N": base_n, "P": base_p, "K": base_k},
        "total_base": {"N": t_base_n, "P": t_base_p, "K": t_base_k},
        "ph_result": ph_res,
        "user_inventory": user_inventory,
        "inventory_check": inventory_check,
        "inventory_sufficiency": {
            "has_n": has_n,
            "has_p": has_p,
            "has_k": has_k,
            "missing_nutrients": missing_nutrients,
        },
        "standard_mix": base_mix,
    }