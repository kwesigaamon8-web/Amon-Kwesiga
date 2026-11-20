"""Mock reports are not claimed as actual inference."""
import unittest,tempfile,json
from pathlib import Path
from enigma_b1b2_bridge import EXPECTED,PARENTS,one,board_from,main
class BridgeTests(unittest.TestCase):
 def test_14_7_by_7(self):
  b=board_from([one(x) for x in sorted(EXPECTED)])
  self.assertEqual(len(EXPECTED),14)
  self.assertEqual([len(q["support_workers"]) for q in b["queues"]],[7,7])
  self.assertEqual(b["real_model_results"],0)
  self.assertEqual(b["external_posts"],0)
 def test_proof_needed_and_parent_distinct(self):
  good=one("ENIGMA-G01-A",{"agent_id":"ENIGMA-G01-A","actual_model_call_completed":True,
     "generated_work_notes":"Potential work, verify with original source"})
  self.assertTrue(good["real_model_call"])
  self.assertEqual(good["verified_moltbook_supervisor"],"transferexperiment")
  self.assertFalse(good["crypto_receipt_verified"])
  wrong=one("ENIGMA-G01-B",{"agent_id":"ENIGMA-G01-A","actual_model_call_completed":True,
     "generated_work_notes":"Fake"})
  self.assertFalse(wrong["real_model_call"])
  self.assertEqual(wrong["status"],"SOURCE_ID_MISMATCH")
 def test_local_board(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"G07"/"B";p.mkdir(parents=True)
   (p/"ENIGMA-G07-B.json").write_text(json.dumps({
    "agent_id":"ENIGMA-G07-B","actual_model_call_completed":True,"generated_work_notes":"QA report"}))
   b=main(d,Path(d)/"out")
   self.assertEqual(b["real_model_results"],1)
   self.assertTrue((Path(d)/"out"/"bridge.json").is_file())
if __name__=="__main__":unittest.main()
