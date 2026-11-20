import unittest
from country_bitcoin_worker_allocation import allocate_exact,ROLES_PER_SYSTEM,TOTAL,ROLE_SYSTEMS
class CountryTests(unittest.TestCase):
 def test_exact_coverage_and_tiebreaking(self):
  r=allocate_exact(100,{"USA":20,"IND":30,"UGA":10,"FRA":40})
  self.assertEqual(sum(r.values()),100)
  self.assertEqual(r["USA"],20)
  self.assertEqual(allocate_exact(4,{"A":1,"B":1,"C":1}),{"A":2,"B":1,"C":1})
 def test_all_30_systems(self):
  self.assertEqual(TOTAL,11255658980400)
  self.assertEqual(ROLE_SYSTEMS,30)
  self.assertEqual(ROLES_PER_SYSTEM*ROLE_SYSTEMS,TOTAL)
 def test_bounded_rounding(self):
  r=allocate_exact(ROLES_PER_SYSTEM,{"A":3,"B":2,"C":1})
  self.assertEqual(sum(r.values()),ROLES_PER_SYSTEM)
  self.assertTrue(r["A"]>=r["B"]>=r["C"])
if __name__=="__main__":unittest.main()
