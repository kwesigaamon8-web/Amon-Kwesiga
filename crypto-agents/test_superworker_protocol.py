import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from superworker_protocol import create
class SuperWorkerTests(unittest.TestCase):
 def test_accurate_hierarchy_and_no_phantom_revenue(self):
  x=create("BountyScoutAI","D03-M02-W08-S014-G033-H222","coding and QA","H")
  self.assertEqual(x["supervisor_chain"][0],"BountyScoutAI/D03-M02-W08-S014-G033")
  self.assertEqual(x["supervisor_chain"][-2:],["CHIEF_D","HUMAN_OWNER"])
  self.assertEqual(len(x["phases"]),7)
  self.assertFalse(x["sha256_miner_started"])
  self.assertFalse(x["paid_customer_verified"])
 def test_company_local_D10(self):
  x=create("transferexperiment","D10-M01-W01","marketing","W")
  self.assertEqual(x["primary_lane"],"PAYMENT_EVIDENCE")
 def test_reject_wrong_company(self):
  with self.assertRaises(ValueError):create("B3","D01-M01-W01","code","W")
if __name__=="__main__":unittest.main()
