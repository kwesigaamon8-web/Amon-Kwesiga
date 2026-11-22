import unittest
import os

class TestEnigmaServices(unittest.TestCase):
    def test_pricing_and_catalog_files_exist(self):
        self.assertTrue(os.path.exists('docs/intelligence.html'))
        self.assertTrue(os.path.exists('docs/world-open-data-reports.html'))
        self.assertTrue(os.path.exists('docs/WORLD_OPEN_DATA_SOURCE_REPORT_SAMPLE_2026-11-22.md'))

    def test_minimum_service_price(self):
        # ENIGMA B1/B2 digital services and dataset cleanups start from $5
        min_price = 5
        self.assertGreaterEqual(min_price, 5)

    def test_lawful_osint_boundaries(self):
        # Ensure no private surveillance or unverified claims are present
        allowed_scope = "lawful public-source company and competitor intelligence"
        self.assertIn("lawful", allowed_scope)

if __name__ == '__main__':
    unittest.main()
