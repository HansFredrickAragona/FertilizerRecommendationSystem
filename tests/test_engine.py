"""Regression tests for the active deterministic recommendation engine."""

import unittest

from engine.core import build_recommendation, load_assets, normalize_area, run_ph_engine


class AssetTests(unittest.TestCase):
    def test_required_rule_assets_load(self):
        inventory, rules, crop_rules, ph_rules = load_assets()

        self.assertGreaterEqual(len(inventory), 1)
        self.assertIn("constraints", rules)
        self.assertIn("Cabbage", crop_rules)
        self.assertIn("ph_rules", ph_rules)


class AreaAndPhTests(unittest.TestCase):
    def test_square_metres_are_converted_to_hectares(self):
        area_ha, unit_label = normalize_area(500, "Square Meters (sqm)")

        self.assertEqual(area_ha, 0.05)
        self.assertEqual(unit_label, "sqm")

    def test_invalid_area_unit_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_area(1, "acres")

    def test_ph_thresholds_preserve_current_rules(self):
        _, _, _, ph_rules = load_assets()

        self.assertEqual(run_ph_engine({"soil_ph": 5.0}, ph_rules)["ph_action"], "liming_required")
        self.assertTrue(run_ph_engine({"soil_ph": 5.1}, ph_rules)["borderline_warning"])
        self.assertEqual(run_ph_engine({"soil_ph": 6.5}, ph_rules)["ph_status"], "acceptable")
        self.assertEqual(
            run_ph_engine({"soil_ph": 7.5}, ph_rules)["ph_action"], "gypsum_recommended"
        )


class RecommendationTests(unittest.TestCase):
    def test_cabbage_recommendation_scales_targets_and_returns_mixes(self):
        result = build_recommendation(
            crop_label="Cabbage",
            n_status="Low",
            p_status="Medium",
            k_status="High",
            soil_ph=5.5,
            raw_area=500,
            area_unit="Square Meters (sqm)",
        )

        self.assertEqual(result["selected_crop"], "Cabbage")
        self.assertEqual(result["area_ha"], 0.05)
        self.assertEqual(result["total_base"], {"N": 7.5, "P": 2.0, "K": 0.0})
        self.assertEqual(result["ph_result"]["ph_status"], "acceptable")
        self.assertTrue(result["standard_mix"])


if __name__ == "__main__":
    unittest.main()
