"""Local regression tests for the free read-only Render dashboard."""
import unittest
from unittest.mock import patch

from app import app


class PublicDashboardTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_only_certifies_dashboard_not_agents(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["running_agents_claim"], False)

    def test_public_api_does_not_claim_unverified_payments(self):
        with patch("app.fetch_run_status", return_value={"runs": [], "error": None}):
            response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["runs"], [])
        self.assertIsNone(body["source_error"])
        self.assertIs(body["real_agent_work_verified_by_dashboard"], False)
        self.assertIs(body["cryptocurrency_received_verified_by_dashboard"], False)

    def test_homepage_renders_even_when_github_is_unavailable(self):
        with patch("app.fetch_run_status", return_value={"runs": [], "error": "temporary outage"}):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("temporary outage", body)
        self.assertIn("No cryptocurrency receipts", body)


if __name__ == "__main__":
    unittest.main()
