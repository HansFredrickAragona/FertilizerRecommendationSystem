# SoilScanRuleBased

## Project Overview

SoilScanRuleBased is a rule-based soil recommendation engine designed to help developers and researchers assess soil conditions and suggest fertilizer or crop guidance based on predefined agronomic rules.

## Repository Structure

- `app_final.py` - Main application logic for running the soil rule engine.
- `RuleBasedAPI.py` - API layer or integration code for exposing the rule-based engine.
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

Run the main application:

```powershell
python app_final.py
```

If `RuleBasedAPI.py` is intended as a service layer, run it using the Python interpreter or integrate it into a web/API framework as needed.

## Notes for Developers

- The engine relies on JSON rule files in the repository root.
- Modify the rule files carefully to preserve JSON structure and rule semantics.
- Use the Python files as the entry point for processing soil data and generating recommendations.

## Contribution

1. Review existing rules before adding new crop or soil recommendations.
2. Keep rule file formats consistent and validate JSON after edits.
3. Test changes locally by running the application and verifying expected output.
