# SoilScanRuleBased

## Project Overview

SoilScanRuleBased is a rule-based soil recommendation engine designed to help developers and researchers assess soil conditions and suggest fertilizer or crop guidance based on predefined agronomic rules.

## Repository Structure

- `app_final.py` - Main executable application entry point for running the soil rule engine and generating recommendations.
- `app_ui.py` - User interface layer for collecting soil inputs, displaying results, and managing user interaction.
- `inventory.py` - Working development file for inventory and fertilizer mix logic. Developers should use this file for experimenting and making changes before updating `app_final.py`.
  - Includes `solve_npk_with_inv`, which generates inventory-based fertilizer combinations and requires each valid prescription to contain at least one selected inventory item when `selected_inventory` is provided.
- `RuleBasedAPI.py` - Service/API integration layer for exposing the rule engine through an API.
- `requirements.txt` - Python dependencies required to run the project.
- `crop_npk_rules.json` - Crop-specific nitrogen, phosphorus, and potassium rules.
- `engine_rules.json` - Core soil evaluation rules used by the engine.
- `fertilizers.json` - Fertilizer recommendations and details.
- `orig_crop_npk.json` - Original crop NPK reference data.
- `ph_rules.json` - Soil pH rules and recommendations.

## Installation

1. Create a Python virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

## Usage
Run the user interface application:

```powershell
streamlit run app_ui.py
```

If `RuleBasedAPI.py` is intended as a service layer, run it using the Python interpreter or integrate it into a web/API framework as needed.

## Recommendations

- Update the fertilizer check flow to integrate the new `solve_npk_with_inv` method in `inventory.py`.
- Use `inventory.py` for developing and validating new fertilizer mix logic before moving changes into `app_final.py`.
- Keep `selected_inventory` items as required elements in valid prescriptions when they are provided.

## Limitations

- The current `solve_npk` implementation uses a phosphorus-driven greedy approach.
- This strategy may not produce the most balanced NPK mixes in all cases, so alternative nutrient balancing approaches are recommended.

## Notes for Developers

- The engine relies on JSON rule files in the repository root.
- Modify the rule files carefully to preserve JSON structure and rule semantics.
- `inventory.py` is the working development file for developers to prototype inventory and fertilizer mix logic.
- `inventory.py` now uses `selected_inventory` as a required element for valid prescriptions when selected items are provided.
- Output from `solve_npk_with_inv` only includes combinations that contain at least one selected inventory fertilizer.
- Update the fertilizer check method to integrate the new `solve_npk_with_inv` logic as part of validation.
- Prefer updating `inventory.py` first for changes, then integrate tested logic into `app_final.py`.
- Use the Python files as the entry point for processing soil data and generating recommendations.

## Contribution

1. Review existing rules before adding new crop or soil recommendations.
2. Keep rule file formats consistent and validate JSON after edits.
3. Test changes locally by running the application and verifying expected output.
