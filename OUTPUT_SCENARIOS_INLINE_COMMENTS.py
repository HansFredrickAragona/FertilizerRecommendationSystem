# ============================================================================
# INLINE DOCUMENTATION - Possible Output Scenarios for build_recommendation()
# ============================================================================
# Add this below the build_recommendation() method return statement
# ============================================================================

# SCENARIO 1: CABBAGE with P="Low" (60 kg/ha), N="Low" (150 kg/ha), K="Low" (75 kg/ha)
# 
# Input: crop_label="Cabbage", n_status="Low", p_status="Low", k_status="Low", 
#        soil_ph=6.5, raw_area=500.0, area_unit="Square Meters (sqm)"
# 
# base_targets_per_ha: {"N": 150.0, "P": 60.0, "K": 75.0}
# For 500 sqm (0.05 ha): total_base: {"N": 7.5, "P": 3.0, "K": 3.75}
# 
# standard_mix (Top 3 from solve_npk, sorted by Total Weight):
# [
#   {
#     "Source": "13-33-21 Compound",
#     "Total Weight": 9.09,
#     "Applied N": 10.37,
#     "Applied P": 3.0,
#     "Applied K": 1.91,
#     "Prescription": [
#       "10.37 kg/500 sqm sqm of Urea",
#       "9.09 kg/500 sqm sqm of 13-33-21 Compound"
#     ]
#   },
#   {
#     "Source": "Complete (16-16-16)",
#     "Total Weight": 18.75,
#     "Applied N": 7.5,
#     "Applied P": 3.0,
#     "Applied K": 3.0,
#     "Prescription": [
#       "18.75 kg/500 sqm sqm of Complete (16-16-16)",
#       "6.25 kg/500 sqm sqm of Muriate of Potash"
#     ]
#   },
#   {
#     "Source": "Complete (14-14-14)",
#     "Total Weight": 21.43,
#     "Applied N": 7.5,
#     "Applied P": 3.0,
#     "Applied K": 3.0,
#     "Prescription": [
#       "21.43 kg/500 sqm sqm of Complete (14-14-14)",
#       "6.25 kg/500 sqm sqm of Muriate of Potash"
#     ]
#   }
# ]

# ─────────────────────────────────────────────────────────────────────────

# SCENARIO 2: PH ENGINE OUTPUTS (run_ph_engine) - 5 CASES
#
# Case 2A: pH ≤ 5.0 (DEFICIENT - Liming Required)
#   ph_result: {
#     "ph_status": "acidic",
#     "ph_action": "liming_required",
#     "borderline_warning": false,
#     "borderline_message": null,
#     "recommendation_message": "Soil pH is at or below 5.0. Liming required...",
#     "soil_ph": 4.8,
#     "perfect_ph": 6.5
#   }
#
# Case 2B: pH = 5.1 (BORDERLINE ACIDIC - Warning)
#   ph_result: {
#     "ph_status": "borderline_acidic",
#     "ph_action": "none",
#     "borderline_warning": true,
#     "borderline_message": "Monitor closely...",
#     "soil_ph": 5.1,
#     "perfect_ph": 6.5
#   }
#
# Case 2C: 5.1 < pH < 7.4 (OPTIMAL - No Action)
#   ph_result: {
#     "ph_status": "acceptable",
#     "ph_action": "none",
#     "borderline_warning": false,
#     "borderline_message": null,
#     "recommendation_message": "Soil pH within acceptable range...",
#     "soil_ph": 6.5,
#     "perfect_ph": 6.5
#   }
#
# Case 2D: pH = 7.4 (BORDERLINE ALKALINE - Warning)
#   ph_result: {
#     "ph_status": "borderline_alkaline",
#     "ph_action": "none",
#     "borderline_warning": true,
#     "borderline_message": "Monitor closely...",
#     "soil_ph": 7.4,
#     "perfect_ph": 6.5
#   }
#
# Case 2E: pH ≥ 7.5 (EXCESS - Gypsum Recommended)
#   ph_result: {
#     "ph_status": "alkaline",
#     "ph_action": "gypsum_recommended",
#     "borderline_warning": false,
#     "borderline_message": null,
#     "recommendation_message": "Soil pH above 7.5. Gypsum recommended...",
#     "soil_ph": 7.8,
#     "perfect_ph": 6.5
#   }

# ─────────────────────────────────────────────────────────────────────────

# SCENARIO 3: check_fertilizer_input() VALIDATION CASES - 6 OUTCOMES
#
# Case 3A: No Fertilizers Selected
#   {"valid": false, "reason": "No fertilizers selected.", "details": null}
#
# Case 3B: Unknown Fertilizer Names
#   {"valid": false, "reason": "Unknown fertilizer name(s): ...", "details": null}
#
# Case 3C: Missing Required Nutrients (Multiple Combinations)
#   {"valid": false, "reason": "Cannot supply: Phosphorus (P).", "details": null}
#   OR: "Nitrogen (N)", "Potassium (K)", "N + P", "N + K", "P + K", "N + P + K"
#
# Case 3D: Lacks Pure N/K Fillers or P-Sources
#   {"valid": false, "reason": "Lacks required N/K fillers or P-sources.", "details": null}
#
# Case 3E: Cannot Satisfy Full NPK
#   {
#     "valid": false,
#     "reason": "Cannot fully satisfy: Potassium.",
#     "details": {
#       "candidate_prescription": ["5.5 kg/500 sqm of Urea", ...],
#       "applied": {"N": 6.5, "P": 3.0, "K": 2.1}
#     }
#   }
#
# Case 3F: Valid - Satisfies All NPK
#   {
#     "valid": true,
#     "reason": "Selected inventory can satisfy the required NPK values.",
#     "details": {
#       "needed_kg": 24.59,
#       "source": "Complete (14-14-14)",
#       "applied": {"N": 7.5, "P": 3.0, "K": 3.0},
#       "prescription": [...]
#     }
#   }

# ─────────────────────────────────────────────────────────────────────────

# SCENARIO 4: solve_npk() OUTPUT - For Cabbage (1000 sqm = 0.1 ha)
# Input targets: N=15.0 kg, P=6.0 kg, K=7.5 kg
#
# [
#   {
#     "Source": "13-33-21 Compound",
#     "Total Weight": 18.18,
#     "Applied N": 20.75,
#     "Applied P": 6.0,
#     "Applied K": 3.82,
#     "Prescription": [
#       "20.75 kg/1000 sqm of Urea",
#       "18.18 kg/1000 sqm of 13-33-21 Compound"
#     ]
#   },
#   {
#     "Source": "Complete (16-16-16)",
#     "Total Weight": 37.5,
#     "Applied N": 15.0,
#     "Applied P": 6.0,
#     "Applied K": 6.0,
#     "Prescription": [
#       "37.5 kg/1000 sqm of Complete (16-16-16)",
#       "12.5 kg/1000 sqm of Muriate of Potash"
#     ]
#   }
# ]
# (Sorted by Total Weight, max 10 combinations)

# ─────────────────────────────────────────────────────────────────────────

# SCENARIO 5: COMPLETE build_recommendation() RESPONSE STRUCTURE
#
# {
#   "inventory": [14 fertilizer objects],
#   "rules": {constraints, output_format},
#   "crop_rules": {all crop NPK data},
#   "ph_rules": {pH engine rules},
#   "selected_crop_label": "Cabbage",
#   "selected_crop": "Cabbage",
#   "area_ha": 0.05,
#   "unit_label": "sqm",
#   "raw_area": 500.0,
#   "base_targets_per_ha": {"N": 150.0, "P": 60.0, "K": 75.0},
#   "total_base": {"N": 7.5, "P": 3.0, "K": 3.75},
#   "ph_result": {...ph case above...},
#   "user_inventory": [matching fertilizers or []],
#   "inventory_check": {...inventory case above...},
#   "inventory_sufficiency": {
#     "has_n": true,
#     "has_p": true,
#     "has_k": true,
#     "missing_nutrients": []
#   },
#   "standard_mix": [up to 10 fertilizer combinations]
# }

# =============================================================================
