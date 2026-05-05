# Summary: All Possible Outputs for build_recommendation()

## Quick Reference Table

| Scenario | Input | Output Count | Key Fields | Notes |
|----------|-------|--------------|-----------|-------|
| **Cabbage L-L-L** | crop="Cabbage", n/p/k="Low", 500sqm | 3+ mixes | standard_mix, total_base | P=60 kg/ha target |
| **pH Acidic** | soil_ph ≤ 5.0 | 1 case | ph_action="liming_required" | Requires liming |
| **pH Borderline Low** | soil_ph = 5.1 | 1 case | borderline_warning=true | Monitor only |
| **pH Optimal** | 5.1 < pH < 7.4 | 1 case | ph_action="none" | No action needed |
| **pH Borderline High** | soil_ph = 7.4 | 1 case | borderline_warning=true | Monitor only |
| **pH Alkaline** | soil_ph ≥ 7.5 | 1 case | ph_action="gypsum_recommended" | Gypsum needed |
| **No Inventory** | selected_inventory_names=[] | 1 case | valid=false | Must select something |
| **Unknown Names** | invalid fertilizer names | 1 case | valid=false | Check fertilizer names |
| **Missing N** | only P,K selected | 1 case | valid=false, missing=["N"] | Need N source |
| **Missing P** | only N,K selected | 1 case | valid=false, missing=["P"] | Need P source |
| **Missing K** | only N,P selected | 1 case | valid=false, missing=["K"] | Need K source |
| **Insufficient Mix** | inventory can't meet needs | 1 case | valid=false, applied data | Shows shortfall |
| **Valid Mix** | all NPK satisfied | 1 case | valid=true, prescription | Ready to use |

---

## Output Files Created

### 1. **BUILD_RECOMMENDATION_OUTPUTS.md** (Detailed Reference)
   - Complete markdown documentation with all scenarios
   - Full JSON/Python output examples
   - Algorithm flow for solve_npk()
   - Summary comparison table

### 2. **OUTPUT_SCENARIOS_INLINE_COMMENTS.py** (Inline Comments)
   - Ready-to-copy Python comments
   - Can be added below methods in app_final.py
   - All 5 scenarios with examples

---

## Scenarios Overview

### SCENARIO 1: Cabbage NPK Recommendations (P=Low)
- **When**: crop_label="Cabbage", n_status="Low", p_status="Low", k_status="Low"
- **Base targets**: N=150.0, P=60.0, K=75.0 kg/ha
- **For 500 sqm (0.05 ha)**: N=7.5, P=3.0, K=3.75 kg
- **Output**: 3-10 fertilizer mix options sorted by Total Weight
- **Example Sources**: 13-33-21 Compound, Complete (16-16-16), Complete (14-14-14)

### SCENARIO 2: pH Engine Outputs (5 Cases)

| pH Range | Status | Action | Warning |
|----------|--------|--------|---------|
| ≤ 5.0 | acidic | liming_required | false |
| = 5.1 | borderline_acidic | none | true |
| 5.1 < x < 7.4 | acceptable | none | false |
| = 7.4 | borderline_alkaline | none | true |
| ≥ 7.5 | alkaline | gypsum_recommended | false |

### SCENARIO 3: Fertilizer Input Validation (6 Outcomes)

1. **No fertilizers selected** → valid=false
2. **Unknown fertilizer names** → valid=false
3. **Missing nutrients** (N, P, K, or combinations) → valid=false
4. **Lacks pure N/K fillers or P-sources** → valid=false
5. **Insufficient inventory** (can't meet full NPK) → valid=false + details
6. **Valid mix** (satisfies all NPK) → valid=true + prescription

### SCENARIO 4: solve_npk() Fertilizer Combinations
- **Algorithm**: Solve for P first, then top up N and K with pure fillers
- **Precision**: 2 decimal places (configurable via rules)
- **Sorting**: By Total Weight (ascending)
- **Limit**: max 10 combinations (configurable via rules)
- **Output fields**: Source, Total Weight, Applied N/P/K, Prescription array

### SCENARIO 5: Complete Response Structure
- Includes all configuration data (inventory, rules, crop_rules, ph_rules)
- Contains computed targets per hectare and area-adjusted totals
- Includes pH analysis result (1 of 5 pH cases)
- Includes user inventory validation (1 of 6 validation cases)
- Includes fertilizer mix recommendations (1-10 combinations)

---

## Key Constraints & Rules

From `engine_rules.json`:
```
allow_over_fertilization: false    (over-fert combinations skipped)
max_combinations: 10               (top 10 by weight returned)
precision_decimals: 2              (quantities rounded to 2 decimals)
output_format: "{qty} kg/{area} {unit} of {fertilizer_name}"
```

From `ph_rules.json`:
```
Perfect pH: 6.5
Liming trigger (max): 5.0
Gypsum trigger (min): 7.5
Borderline low: 5.1
Borderline high: 7.4
```

---

## Usage Examples

### Example 1: Cabbage Recommendation Request
```python
result = build_recommendation(
    crop_label="Cabbage",
    n_status="Low",
    p_status="Low", 
    k_status="Low",
    soil_ph=6.5,
    raw_area=500.0,
    area_unit="Square Meters (sqm)",
    selected_inventory_names=None
)
# Returns: full recommendation with 3+ fertilizer mix options
```

### Example 2: Acidic Soil pH
```python
result = build_recommendation(
    crop_label="Cabbage",
    n_status="Low",
    p_status="Low",
    k_status="Low",
    soil_ph=4.8,  # ACIDIC!
    raw_area=500.0,
    area_unit="Square Meters (sqm)"
)
# ph_result.ph_action = "liming_required"
# ph_result.borderline_warning = false
```

### Example 3: Inventory Check - Missing P
```python
result = build_recommendation(
    crop_label="Cabbage",
    n_status="Low",
    p_status="Low",
    k_status="Low",
    soil_ph=6.5,
    raw_area=500.0,
    selected_inventory_names=["Urea", "Muriate of Potash"]  # No P!
)
# inventory_check.valid = false
# inventory_check.reason = "Cannot supply: Phosphorus (P)."
```

### Example 4: Valid Custom Inventory
```python
result = build_recommendation(
    crop_label="Cabbage",
    n_status="Low",
    p_status="Low",
    k_status="Low",
    soil_ph=6.5,
    raw_area=500.0,
    selected_inventory_names=["Urea", "Complete (14-14-14)", "Muriate of Potash"]
)
# inventory_check.valid = true
# inventory_check.details.prescription = [list of applications]
```

---

## Development Notes

- All scenarios are based on actual rules from JSON configuration files
- Output structures are deterministic given the same inputs
- pH rules are universal (apply to all crops)
- Crop NPK targets vary by soil status (Low, Medium, High)
- Fertilizer costs are not factored into solve_npk() (sorted by weight only)
- Area is converted to hectares internally but displayed in user's preferred unit

---

## Files Referenced

- `crop_npk_rules.json` - NPK targets by crop and soil status
- `ph_rules.json` - pH decision rules and constants
- `fertilizers.json` - Fertilizer inventory (N, P, K percentages)
- `engine_rules.json` - Solver constraints and output formatting
- `app_final.py` - Main logic implementation
- `RuleBasedAPI.py` - FastAPI endpoint wrapper
