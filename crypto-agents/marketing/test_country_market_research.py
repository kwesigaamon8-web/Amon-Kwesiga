"""Validate 249 country research orders & virtual role boundary routing."""
import unittest
from country_market_research import COUNTRY_CODES, SECTORS, research_assignment, worker_country
from role_campaign_dispatch import FLEETS, ALL_ROLES, fleet_for_global_index, role_from_local_index
from role_messages import build_message

class CountryDispatch(unittest.TestCase):
    def test_exact_iso_territory_coverage(self):
        self.assertEqual(len(COUNTRY_CODES), 249)
        self.assertEqual(len(set(COUNTRY_CODES)), 249)
        self.assertIn("UG", COUNTRY_CODES)
        self.assertIn("MK", COUNTRY_CODES)
        self.assertIn("US", COUNTRY_CODES)
    def test_each_country_has_a_specific_app_and_required_research(self):
        for code in COUNTRY_CODES:
            d=research_assignment(code)
            self.assertEqual(d["country_or_territory_code"],code)
            self.assertTrue(d["candidate_software"].startswith("SW-"))
            self.assertFalse(d["verified_local_problem"])
            self.assertEqual(d["actual_market_interviews"],0)
            self.assertEqual(d["authorized_external_posts"],0)
            self.assertFalse(d["independently_confirmed_crypto_payment"])
            self.assertTrue(d["reference_data"][0].startswith("https://"))
    def test_virtual_role_dispatch_honest_and_total_coverage(self):
        samples=[0,248,249,ALL_ROLES//2-1,ALL_ROLES//2,ALL_ROLES-1]
        for i in samples:
            d=worker_country(i)
            self.assertIn(d["country_or_territory_code"],COUNTRY_CODES)
            self.assertFalse(d["worker_is_a_real_process"])
            fleet,local=fleet_for_global_index(i)
            msg=build_message(fleet,role_from_local_index(local))
            self.assertEqual(msg["country_market_research"]["country_or_territory_code"],d["country_or_territory_code"])
            self.assertEqual(msg["delivery_status"],"VIRTUAL_ADDRESS_ONLY_NOT_SENT")
            self.assertFalse(msg["external_platform_posted"])
            self.assertIn("COUNTRY RESEARCH",msg["required_actions"][2])
    def test_rejects_invalid_country_and_role_ids(self):
        with self.assertRaises(ValueError):
            research_assignment("ZZ")
        with self.assertRaises(ValueError):
            worker_country(-1)
        with self.assertRaises(ValueError):
            worker_country(ALL_ROLES)

if __name__=="__main__":
    unittest.main()
