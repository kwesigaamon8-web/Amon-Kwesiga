"""No-network validation for hosted worker research assignments."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hosting_scout import HOSTS, plan, self_test, probe


class HostingScoutTest(unittest.TestCase):
    def test_catalog_and_distinct_assignments(self):
        result=self_test()
        self.assertEqual(result["result"],"PASS")
        self.assertEqual(result["candidate_platforms"],10)

    def test_two_company_assignments_never_fake_deployment(self):
        for fleet in ("transferexperiment","BountyScoutAI"):
            assignment=plan(fleet,"D01-M01-W01")
            self.assertFalse(assignment["registration_or_deployment_done"])
            self.assertNotEqual(assignment["assigned"]["id"],
                                assignment["independent_alternative"]["id"])
            self.assertTrue(assignment["source_document"].endswith(".md"))

    def test_disallowed_unknown_worker_or_fleet(self):
        with self.assertRaises(ValueError):
            plan("unknown","D01-M01-W01")
        with self.assertRaises(ValueError):
            plan("transferexperiment","")

    def test_no_credentials_or_deployment_claims(self):
        for host in HOSTS:
            self.assertNotEqual(host["account_status"],"DEPLOYED")
            self.assertTrue(host["official_url"].startswith("https://"))
            self.assertNotIn("secret",str(host).lower())

if __name__=="__main__":
    unittest.main()
