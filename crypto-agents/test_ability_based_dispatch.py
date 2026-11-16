"""Offline tests: no API calls or actual miners."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ability_based_dispatch import dispatch,self_test
class CapabilityAssignmentTest(unittest.TestCase):
    def test_samples(self):
        self.assertEqual("PASS",self_test()["result"])
    def test_qa(self):
        p=dispatch("transferexperiment","D04-M01-W01","security QA regression tests","D04","W")
        self.assertIn(p["primary_lane"],("QA_REVIEW","PAYER_VALIDATE"))
        self.assertEqual("ROLE_ASSIGNED_NOT_EXECUTED",p["assignment_state"])
        self.assertFalse(p["actual_bitcoin_miner_created"])
    def test_wallet_specialist(self):
        p=dispatch("BountyScoutAI","D10-M02-W02","customer acquisition","D10","W")
        self.assertEqual("PAYMENT_EVIDENCE",p["primary_lane"])
        self.assertTrue(p["reports_to"].startswith("BountyScoutAI/D10-M02"))
    def test_invalid_hierarchy(self):
        with self.assertRaises(ValueError):
            dispatch("transferexperiment","D03-M01-W01","code","D09","W")
        with self.assertRaises(ValueError):
            dispatch("not_real","D03-M01-W01","code","D03","W")
if __name__=="__main__":
    unittest.main()
