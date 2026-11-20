"""Local regression tests for the free read-only Render dashboard."""
import io
import json
import unittest
from unittest.mock import patch

from app import app, fetch_run_status, _cache


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

    def test_complete_github_response_larger_than_140kb_is_parsed(self):
        # Regression: Render saw JSONDecodeError because read(140000) cut off
        # a valid ~168 KB GitHub Actions API response.
        payload = json.dumps({
            "workflow_runs": [{
                "id": 123,
                "name": "B1/B2 test run",
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/123",
                "created_at": "2026-11-20T09:00:00Z"
            }],
            "unused_metadata": "x" * 170000,
        }).encode("utf-8")
        self.assertGreater(len(payload), 140000)
        with patch.dict(_cache, {"at": 0.0, "runs": [], "error": None}, clear=True):
            with patch("app.time.time", return_value=2000000.0):
                with patch("app.urllib.request.urlopen", return_value=io.BytesIO(payload)):
                    result = fetch_run_status()
        self.assertIsNone(result["error"])
        self.assertEqual(len(result["runs"]), 1)
        self.assertEqual(result["runs"][0]["conclusion"], "success")

    def test_malformed_github_response_is_explained_without_crashing_page(self):
        with patch.dict(_cache, {"at": 0.0, "runs": [], "error": None}, clear=True):
            with patch("app.time.time", return_value=2000000.0):
                with patch("app.urllib.request.urlopen", return_value=io.BytesIO(b'{"workflow_runs": [null')):
                    result = fetch_run_status()
        self.assertIn("incomplete or invalid JSON", result["error"])
        self.assertEqual(result["runs"], [])

    def test_large_github_response_is_rejected_with_bounded_memory(self):
        with patch.dict(_cache, {"at": 0.0, "runs": [], "error": None}, clear=True):
            with patch("app.time.time", return_value=2000000.0):
                with patch("app.urllib.request.urlopen", return_value=io.BytesIO(b"x" * (512 * 1024 + 2))):
                    result = fetch_run_status()
        self.assertIn("ValueError", result["error"])

    def test_full_original_studio_served_on_render(self):
        paths = (
            ("/studio/", "B1/B2 Digital Work Studio"),
            ("/studio/software.html", "Free Software"),
            ("/studio/free-toolbox.html", "55 Tools"),
            ("/studio/mini-apps.html", "Free Mini Apps"),
            ("/studio/market-lab.html", "Marketing"),
            ("/studio/share-free-software.html", "Share Free Software"),
            ("/studio/payment.html", "Bitcoin payment instructions"),
            ("/studio/bitcoin-merchant/index.html", "Bitcoin Merchant"),
            ("/studio/crypto-ledger/index.html", "Crypto Ledger"),
        )
        for route, phrase in paths:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(phrase, response.get_data(as_text=True))

    def test_studio_static_javascript_css_and_modules(self):
        for route in (
            "/studio/assets/free-toolbox.js",
            "/studio/assets/free-toolbox-extensions.js",
            "/studio/assets/free-mini-apps.js",
            "/studio/assets/market-lab.js",
            "/studio/assets/styles.css",
            "/studio/crypto-ledger/core.mjs",
            "/studio/bitcoin-merchant/wallet_core.mjs",
        ):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertGreater(len(response.data), 100)

    def test_studio_path_traversal_and_shortlinks(self):
        self.assertEqual(self.client.get("/studio").status_code, 308)
        r = self.client.get("/software")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.location, "/studio/software.html")
        self.assertNotEqual(self.client.get("/studio/%2e%2e%2fapp.py").status_code, 200)
        self.assertEqual(self.client.get("/studio/nonexistent.html").status_code, 404)

    def test_payment_page_has_only_correct_network_routes(self):
        r = self.client.get("/studio/payment.html")
        s = r.get_data(as_text=True)
        self.assertIn("bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z", s)
        self.assertIn("bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9", s)
        self.assertIn("Bitcoin mainnet only", s)
        self.assertIn("already agreed", s)

    def test_homepage_renders_even_when_github_is_unavailable(self):
        with patch("app.fetch_run_status", return_value={"runs": [], "error": "temporary outage"}):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("temporary outage", body)
        self.assertIn("No cryptocurrency receipts", body)


if __name__ == "__main__":
    unittest.main()
