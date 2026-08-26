import unittest

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
error_client = TestClient(app, raise_server_exceptions=False)


class RecommendationAPITests(unittest.TestCase):
    def test_valid_request_returns_200(self):
        response = client.post(
            "/recommendation",
            json={
                "crop_label": "Cabbage",
                "n_status": "Low",
                "p_status": "Medium",
                "k_status": "High",
                "soil_ph": 5.5,
                "raw_area": 500.0,
                "area_unit": "Square Meters (sqm)",
                "selected_inventory_names": ["Urea", "Ammonium Phosphate"],
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["selected_crop_label"], "Cabbage")
        self.assertIn("standard_mix", body)
        self.assertIn("ph_result", body)
        self.assertIn("user_inventory", body)

    def test_unknown_crop_returns_error(self):
        response = error_client.post(
            "/recommendation",
            json={
                "crop_label": "Nonexistent Crop",
                "n_status": "Low",
                "p_status": "Low",
                "k_status": "Low",
                "soil_ph": 6.0,
                "raw_area": 100.0,
            },
        )
        self.assertEqual(response.status_code, 500)

    def test_invalid_area_unit_returns_error(self):
        response = error_client.post(
            "/recommendation",
            json={
                "crop_label": "Cabbage",
                "n_status": "Low",
                "p_status": "Low",
                "k_status": "Low",
                "soil_ph": 6.0,
                "raw_area": 100.0,
                "area_unit": "bananas",
            },
        )
        self.assertEqual(response.status_code, 500)

    def test_missing_field_returns_422(self):
        response = client.post(
            "/recommendation",
            json={
                "crop_label": "Cabbage",
                "n_status": "Low",
                "soil_ph": 6.0,
                "raw_area": 100.0,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_cors_allows_local_frontend_only(self):
        response = client.options(
            "/recommendation",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:3000",
        )

    def test_cors_rejects_unknown_origin(self):
        response = client.options(
            "/recommendation",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertIsNone(response.headers.get("access-control-allow-origin"))


if __name__ == "__main__":
    unittest.main()
