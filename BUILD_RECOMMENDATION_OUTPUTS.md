# Possible Output Scenarios for build_recommendation()

## SCENARIO 1: CABBAGE with P="Low" (60 kg/ha), N="Low", K="Low"

### Input Parameters
```python
crop_label = "Cabbage"
n_status = "Low"
p_status = "Low"
k_status = "Low"
soil_ph = 6.5
raw_area = 500.0
area_unit = "Square Meters (sqm)"
selected_inventory_names = None
```

### Base Targets Per Hectare
```python
base_targets_per_ha: {
    "N": 150.0,
    "P": 60.0,
    "K": 75.0
}
```

### Total Base (for 500 sqm = 0.05 ha)
```python
total_base: {
    "N": 7.5,
    "P": 3.0,
    "K": 3.75
}
```

### Standard Mix (Top 3 from solve_npk)
```python
[
  {
    "Source": "13-33-21 Compound",
    "Total Weight": 9.09,
    "Applied N": 10.37,
    "Applied P": 3.0,
    "Applied K": 1.91,
    "Prescription": [
      "10.37 kg/500 sqm sqm of Urea",
      "9.09 kg/500 sqm sqm of 13-33-21 Compound"
    ]
  },
  {
    "Source": "Complete (16-16-16)",
    "Total Weight": 18.75,
    "Applied N": 7.5,
    "Applied P": 3.0,
    "Applied K": 3.0,
    "Prescription": [
      "18.75 kg/500 sqm sqm of Complete (16-16-16)",
      "6.25 kg/500 sqm sqm of Muriate of Potash"
    ]
  },
  {
    "Source": "Complete (14-14-14)",
    "Total Weight": 21.43,
    "Applied N": 7.5,
    "Applied P": 3.0,
    "Applied K": 3.0,
    "Prescription": [
      "21.43 kg/500 sqm sqm of Complete (14-14-14)",
      "6.25 kg/500 sqm sqm of Muriate of Potash"
    ]
  }
]
```

---

## SCENARIO 2: pH ENGINE OUTPUTS (run_ph_engine) - 5 CASES

### Case 2A: pH ≤ 5.0 (DEFICIENT - Liming Required)
```python
ph_result: {
    "ph_status": "acidic",
    "ph_action": "liming_required",
    "borderline_warning": false,
    "borderline_message": null,
    "recommendation_message": "Soil pH is at or below 5.0. Liming is required before planting to raise soil pH toward the ideal level of 6.5.",
    "soil_ph": 4.8,
    "perfect_ph": 6.5
}
```

### Case 2B: pH = 5.1 (BORDERLINE ACIDIC - Warning Only)
```python
ph_result: {
    "ph_status": "borderline_acidic",
    "ph_action": "none",
    "borderline_warning": true,
    "borderline_message": "Soil pH is at 5.1, which is borderline acidic. No liming is required at this level, but closely monitor soil pH before the next cropping season.",
    "recommendation_message": "Soil pH is within the acceptable range but approaching the acidic threshold. Monitor closely.",
    "soil_ph": 5.1,
    "perfect_ph": 6.5
}
```

### Case 2C: 5.1 < pH < 7.4 (OPTIMAL - No Action)
```python
ph_result: {
    "ph_status": "acceptable",
    "ph_action": "none",
    "borderline_warning": false,
    "borderline_message": null,
    "recommendation_message": "Soil pH is within the acceptable range of 5.1 to 7.4. No soil amendment is required. The ideal pH is 6.5.",
    "soil_ph": 6.5,
    "perfect_ph": 6.5
}
```

### Case 2D: pH = 7.4 (BORDERLINE ALKALINE - Warning Only)
```python
ph_result: {
    "ph_status": "borderline_alkaline",
    "ph_action": "none",
    "borderline_warning": true,
    "borderline_message": "Soil pH is at 7.4, which is borderline alkaline. No gypsum is required at this level, but closely monitor soil pH before the next cropping season.",
    "recommendation_message": "Soil pH is within the acceptable range but approaching the alkaline threshold. Monitor closely.",
    "soil_ph": 7.4,
    "perfect_ph": 6.5
}
```

### Case 2E: pH ≥ 7.5 (EXCESS - Gypsum Recommended)
```python
ph_result: {
    "ph_status": "alkaline",
    "ph_action": "gypsum_recommended",
    "borderline_warning": false,
    "borderline_message": null,
    "recommendation_message": "Soil pH is at or above 7.5. Applying gypsum is recommended to lower soil pH toward the ideal level of 6.5.",
    "soil_ph": 7.8,
    "perfect_ph": 6.5
}
```

---

## SCENARIO 3: check_fertilizer_input() VALIDATION CASES - 6 OUTCOMES

### Case 3A: No Fertilizers Selected
```python
inventory_check: {
    "valid": false,
    "reason": "No fertilizers selected.",
    "details": null
}
```

### Case 3B: Unknown Fertilizer Names
```python
inventory_check: {
    "valid": false,
    "reason": "Unknown fertilizer name(s): Bogus Fertilizer, Fake NPK.",
    "details": null
}
```

### Case 3C: Missing Required Nutrients
Example: Only "Urea" selected but Phosphorus needed
```python
inventory_check: {
    "valid": false,
    "reason": "Selected inventory cannot supply: Phosphorus (P).",
    "details": null
}
```

Possible missing nutrient combinations:
- "Nitrogen (N)"
- "Phosphorus (P)"
- "Potassium (K)"
- "Nitrogen (N), Phosphorus (P)"
- "Nitrogen (N), Potassium (K)"
- "Phosphorus (P), Potassium (K)"
- "Nitrogen (N), Phosphorus (P), Potassium (K)"

### Case 3D: Lacks Pure N/K Fillers or Valid P-Sources
```python
inventory_check: {
    "valid": false,
    "reason": "Selected inventory lacks required pure N/K fillers or valid P-source fertilizers.",
    "details": null
}
```

### Case 3E: Cannot Satisfy Full NPK Requirements
Example: Best mix only provides K=2.1 but need K=3.75
```python
inventory_check: {
    "valid": false,
    "reason": "Selected inventory cannot fully satisfy: Potassium.",
    "details": {
        "candidate_prescription": [
            "5.5 kg/500 sqm sqm of Urea",
            "15.0 kg/500 sqm sqm of Complete (14-14-14)"
        ],
        "applied": {
            "N": 6.5,
            "P": 3.0,
            "K": 2.1
        }
    }
}
```

### Case 3F: Valid - Selected Inventory Can Satisfy All NPK
```python
inventory_check: {
    "valid": true,
    "reason": "Selected inventory can satisfy the required NPK values.",
    "details": {
        "needed_kg": 24.59,
        "source": "Complete (14-14-14)",
        "applied": {
            "N": 7.5,
            "P": 3.0,
            "K": 3.0
        },
        "prescription": [
            "21.43 kg/500 sqm sqm of Complete (14-14-14)",
            "6.25 kg/500 sqm sqm of Muriate of Potash"
        ]
    }
}
```

---

## SCENARIO 4: solve_npk() OUTPUT STRUCTURE

### Algorithm Flow
1. Extract constraint rules (precision_decimals, allow_over_fertilization, max_combinations)
2. Identify pure N fertilizer (n>0, p=0, k=0)
3. Identify pure K fertilizer (k>0, n=0, p=0)
4. Collect all P-bearing fertilizers (p>0)
5. For each P-source fertilizer:
   - Solve for quantity to meet P target: qty_p = (target_p / p_percent) * 100
   - Calculate provided N, P, K from P-source quantity
   - Calculate remainders: rem_n = target_n - n_provided, rem_k = target_k - k_provided
   - Skip if over-fertilization detected (rem_n < -0.01 or rem_k < -0.01) and not allowed
   - Calculate pure N and K filler quantities from remainders
   - Round all quantities to precision_decimals (2)
   - Format prescription using output_format template
   - Append to results
6. Sort by Total Weight, limit to max_combinations (10)

### Sample Output for Cabbage (1000 sqm = 0.1 ha)
Input targets: N=15.0 kg, P=6.0 kg, K=7.5 kg

```python
[
  {
    "Source": "13-33-21 Compound",
    "Total Weight": 18.18,
    "Applied N": 20.75,
    "Applied P": 6.0,
    "Applied K": 3.82,
    "Prescription": [
      "20.75 kg/1000 sqm sqm of Urea",
      "18.18 kg/1000 sqm sqm of 13-33-21 Compound"
    ]
  },
  {
    "Source": "Complete (16-16-16)",
    "Total Weight": 37.5,
    "Applied N": 15.0,
    "Applied P": 6.0,
    "Applied K": 6.0,
    "Prescription": [
      "37.5 kg/1000 sqm sqm of Complete (16-16-16)",
      "12.5 kg/1000 sqm sqm of Muriate of Potash"
    ]
  },
  {
    "Source": "Complete (14-14-14)",
    "Total Weight": 42.86,
    "Applied N": 15.0,
    "Applied P": 6.0,
    "Applied K": 6.0,
    "Prescription": [
      "42.86 kg/1000 sqm sqm of Complete (14-14-14)",
      "12.5 kg/1000 sqm sqm of Muriate of Potash"
    ]
  }
]
```

Note: Results sorted by Total Weight, limited to max 10 combinations

---

## SCENARIO 5: COMPLETE build_recommendation() RESPONSE STRUCTURE

```python
{
    "inventory": [all 14 fertilizers with name, n, p, k],
    
    "rules": {
        "calculation_steps": [...],
        "constraints": {
            "allow_over_fertilization": false,
            "max_combinations": 10,
            "precision_decimals": 2
        },
        "output_format": "{qty} kg/{area} {unit} of {fertilizer_name}"
    },
    
    "crop_rules": {all crop NPK targets from crop_npk_rules.json},
    "ph_rules": {pH engine rules and constants from ph_rules.json},
    
    "selected_crop_label": "Cabbage",
    "selected_crop": "Cabbage",
    "area_ha": 0.05,
    "unit_label": "sqm",
    "raw_area": 500.0,
    
    "base_targets_per_ha": {
        "N": 150.0,
        "P": 60.0,
        "K": 75.0
    },
    
    "total_base": {
        "N": 7.5,
        "P": 3.0,
        "K": 3.75
    },
    
    "ph_result": {
        "ph_status": "acceptable",
        "ph_action": "none",
        "borderline_warning": false,
        "borderline_message": null,
        "recommendation_message": "Soil pH is within the acceptable range...",
        "soil_ph": 6.5,
        "perfect_ph": 6.5
    },
    
    "user_inventory": [matching fertilizers or []],
    
    "inventory_check": {
        "valid": true/false,
        "reason": "string describing the result",
        "details": {...}
    },
    
    "inventory_sufficiency": {
        "has_n": true,
        "has_p": true,
        "has_k": true,
        "missing_nutrients": []
    },
    
    "standard_mix": [
        {fertilizer combinations up to 10 items}
    ]
}
```

---

## Summary Table: All Possible Cases

| Scenario | Input | Output | Notes |
|----------|-------|--------|-------|
| Cabbage L-L-L | crop="Cabbage", n/p/k="Low" | 9+ fertilizer mix options | P=60 kg/ha, varies by source |
| pH Acidic | soil_ph ≤ 5.0 | liming_required | Action needed |
| pH Borderline Low | soil_ph = 5.1 | borderline_warning=true | Monitor only |
| pH Optimal | 5.1 < pH < 7.4 | acceptable | No action |
| pH Borderline High | soil_ph = 7.4 | borderline_warning=true | Monitor only |
| pH Alkaline | soil_ph ≥ 7.5 | gypsum_recommended | Action needed |
| No Inventory | selected_inventory_names=[] | valid=false | No selection |
| Unknown Fertilizer | invalid names | valid=false | Check names |
| Missing N | only P, K fertilizers | valid=false | Needs N source |
| Missing P | only N, K fertilizers | valid=false | Needs P source |
| Missing K | only N, P fertilizers | valid=false | Needs K source |
| Insufficient Mix | best combo < target | valid=false, details provided | Shows applied vs needed |
| Valid Mix | all NPK satisfied | valid=true, prescription provided | Ready to use |
