"""Offline tests: never count unit-test stubs as actual model executions."""
import json,random,tempfile,unittest
from pathlib import Path
from enigma_all_b_systems import (
 AGENTS,PARENTS,PER_AGENT_ROLES,ALL_ROLE_SLOTS,DIVISIONS,ROLES_PER_ACCOUNT,
 role_at,index_of,hierarchy,rotate,software_qa,summarize
)
class TestHierarchy(unittest.TestCase):
 def test_each_of_fourteen_has_full_original_two_fleets(self):
  self.assertEqual(len(AGENTS),14)
  self.assertEqual(DIVISIONS,28)
  self.assertEqual(PER_AGENT_ROLES,750377265360)
  self.assertEqual(ALL_ROLE_SLOTS,10505281715040)
  self.assertEqual(ROLES_PER_ACCOUNT,375188632680)
  x=[hierarchy(a,f) for a in AGENTS for f in PARENTS]
  self.assertEqual(len({a["division"] for a in x}),28)
  self.assertTrue(all(len(a["ten_directors"])==10 for a in x))
  self.assertTrue(all(a["first_tier_worker_slots"]==7500 for a in x))
  self.assertTrue(all(not a["independent_moltbook_identity"] for a in x))
 def test_virtual_mapping_is_invertible_across_all_boundaries(self):
  rng=random.Random(20261120)
  indexes=[0,1,ROLES_PER_ACCOUNT-1,ROLES_PER_ACCOUNT,
       PER_AGENT_ROLES-1,PER_AGENT_ROLES,ALL_ROLE_SLOTS-1]
  indexes += [rng.randrange(ALL_ROLE_SLOTS) for _ in range(25)]
  ids=set()
  for n in indexes:
   doc=role_at(n)
   self.assertEqual(doc["global_index"],n)
   self.assertFalse(doc["live_model_completed"])
   origin=doc["internal_worker_id"].split("/",2)[2]
   fleet=doc["division"].split("/")[-1]
   self.assertEqual(index_of(doc["enigma_agent"],fleet,origin),n)
   ids.add(doc["internal_worker_id"])
  self.assertEqual(len(ids),len(set(indexes)))
  for bad in [-1,ALL_ROLE_SLOTS,1.5]:
   with self.assertRaises(ValueError):role_at(bad)
 def test_rotated_human_chain_and_d10_payment_reservation(self):
  for a in AGENTS:
   for f in PARENTS:
    r=rotate(a,f,45)
    self.assertEqual(r["reports_via"][-2],"CHIEF_D")
    self.assertEqual(r["reports_via"][-1],"HUMAN_OWNER")
    self.assertTrue(r["reports_via"][2].startswith("D"))
    self.assertNotEqual(r["reports_via"][2],"D10")
 def test_aggregate_has_honest_missing_results(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"in"/AGENTS[0];p.mkdir(parents=True)
   (p/"B1.json").write_text(json.dumps({"agent_id":AGENTS[0],
     "division_id":AGENTS[0]+"/B1","actual_model_completed":True,
     "os_pid":123,"original_task_proposals_untrusted":"Unverified candidate"}))
   report=summarize(Path(tmp)/"in",Path(tmp)/"out")
   self.assertEqual(report["actual_completed_inference_calls"],1)
   self.assertEqual(report["B1_results"],1)
   self.assertEqual(report["B2_results"],0)
   self.assertEqual(report["new_moltbook_accounts"],0)
 def test_b2_real_product_qa_manifest_missing_is_failure(self):
  r=software_qa(AGENTS[0],"/no/such/manifest.json")
  self.assertEqual(r["status"],"MISSING_MANIFEST")
if __name__=="__main__":unittest.main()
