import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
p=Path(__file__).with_name("role_campaign_dispatch.py")
spec=importlib.util.spec_from_file_location("dispatch",p)
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
class TestRoleDispatch(unittest.TestCase):
 def test_total(self):
  self.assertEqual(d.PER_FLEET,375188632680)
  self.assertEqual(d.ALL_ROLES,750377265360)
 def test_boundaries(self):
  offset=0
  for count in d.COUNTS:
   for pos in (offset,offset+count-1):
    role=d.role_from_local_index(pos)
    self.assertEqual(d.local_index_from_role(role),pos,(pos,role))
   offset+=count
 def test_fleets(self):
  for fleet in d.FLEETS:
   for n in range(1,11):
    x=d.assignment(fleet,"D%02d"%n)
    self.assertEqual(x["director_id"],"D%02d"%n)
    self.assertFalse(x["task_execution_verified"])
    self.assertFalse(x["platform_permission_verified"])
    self.assertIsNone(x["verified_public_post_url"])
 def test_randomized_index_roundtrips(self):
  for n in range(150):
   i=(n*73856093)%d.PER_FLEET
   self.assertEqual(d.local_index_from_role(d.role_from_local_index(i)),i)
 def test_assistant_and_leaf(self):
  self.assertEqual(d.assignment("transferexperiment","D03-A02")["parent_id"],"D03")
  self.assertEqual(d.assignment("BountyScoutAI","D01-M01-W01-S001-G001-H001")["parent_id"],"D01-M01-W01-S001-G001")
 def test_invalid_roles(self):
  for role in ("D11","D01-A03","D01-M16","D01-M01-W51","D01-M01-W01-S151","D01-M01-W01-S001-G501","D01-M01-W01-S001-G001-H667","D01-M01-S001"):
   with self.subTest(role=role),self.assertRaises(ValueError): d.local_index_from_role(role)
 def test_invalid_global_index(self):
  for index in (-1,d.ALL_ROLES,True,None,1.5):
   with self.assertRaises(ValueError):d.fleet_for_global_index(index)
 def test_last_role_cli(self):
  r=subprocess.run([sys.executable,str(p),"--global-index",str(d.ALL_ROLES-1)],capture_output=True,text=True,check=True)
  x=json.loads(r.stdout)
  self.assertEqual(x["entries_generated"],1)
  self.assertEqual(x["total_actually_deployed_by_this_script"],0)
  self.assertEqual(x["actual_publications_made_by_this_script"],0)
  self.assertEqual(x["assignments"][0]["role_id"],"D10-M15-W50-S150-G500-H666")
 def test_sample_is_bounded(self):
  r=subprocess.run([sys.executable,str(p),"--sample","20"],capture_output=True,text=True,check=True)
  x=json.loads(r.stdout);self.assertEqual(x["entries_generated"],20)
if __name__=="__main__": unittest.main()
