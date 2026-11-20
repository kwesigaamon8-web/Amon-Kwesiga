import unittest
from enigma_universal_owner_order import TOTAL_ROLES,GRAND_TOTAL,divisions,recipient,envelope,order,overview
class UniversalOrderTest(unittest.TestCase):
 def test_30_system_root_coverage(self):
  root=overview()
  self.assertEqual(root["total_logical_role_positions"],11255658980400)
  self.assertEqual(root["root_systems"],30)
  self.assertTrue(root["configured_coverage_verified"])
  self.assertEqual(sum(d["roles"] for d in divisions()),GRAND_TOTAL)
 def test_single_order_inheritance_beyond_last_leaf(self):
  o=order()
  self.assertTrue(o["id"].startswith("OWNER-"))
  for j in [0,TOTAL_ROLES//2,TOTAL_ROLES-1,TOTAL_ROLES,GRAND_TOTAL-1]:
   r=recipient(j);p=envelope(j)
   self.assertEqual(p["owner_order_id"],o["id"])
   self.assertEqual(r["immediate_parent"],r["owner_to_worker_path"][-2])
   self.assertEqual(r["owner_to_worker_path"][0],"HUMAN_OWNER")
   self.assertFalse(p["verified_model_acknowledgement"])
 def test_source_identity_does_not_become_external_login(self):
  for r in divisions():self.assertFalse(r["moltbook_identity_is_new"])
  with self.assertRaises(ValueError):recipient(GRAND_TOTAL)
if __name__=="__main__":unittest.main()
