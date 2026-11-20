"""PC AI Miner public demo and voluntary-hardware gate tests."""
from __future__ import annotations
import importlib.util
import pathlib
import unittest

p=pathlib.Path(__file__).with_name("pc_ai_miner.py")
spec=importlib.util.spec_from_file_location("pc_ai_miner",p)
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class PCMinerTests(unittest.TestCase):
    def test_known_bitcoin_genesis(self):
        self.assertTrue(a.check_math())
        self.assertEqual(a.sha256d(a.genesis_header())[::-1].hex(),a.GENESIS_HASH)
    def test_demo_never_calls_a_pool(self):
        r=a.demo(12000,8)
        self.assertIsNotNone(r["first_practice_proof"])
        self.assertFalse(r["actual_block_found"])
        self.assertEqual(r["coins_mined"],0)
        self.assertEqual(r["devices_or_networks_contacted"],0)
        self.assertLessEqual(r["tries"],12000)
    def test_bounded_demo(self):
        for count in [0,-1,250001,True]:
            with self.assertRaises(ValueError):a.demo(count,8)
        for bits in [1,40,True]:
            with self.assertRaises(ValueError):a.demo(10,bits)
    def test_no_unconsented_pool_config(self):
        for device,donation in [(False,False),(True,False),(False,True)]:
            with self.assertRaises(ValueError):
                a.pool_configuration("B1","pplns","Volunteer",device,donation)
    def test_two_explicit_opt_in_wallets(self):
        for fleet,addr in [("B1",a.B1),("B2",a.B2)]:
            r=a.pool_configuration(fleet,"solo","Volunteer007",True,True)
            self.assertEqual(r["donation_receiver"],addr)
            self.assertEqual(r["manual_pool_url"],"stratum+tls://public-pool.io:4333")
            self.assertEqual(r["worker_username"],addr+".Volunteer007")
            self.assertTrue(r["does_not_start_a_miner"])
        r=a.pool_configuration("B2","pplns","TestWorker",True,True)
        self.assertEqual(r["manual_pool_url"],"stratum+tls://public-pool.io:14333")
    def test_configuration_cannot_accept_bad_worker_or_fleet(self):
        for worker in ("../test","x"*21,"","A B"):
            with self.assertRaises(ValueError):
                a.pool_configuration("B1","solo",worker,True,True)
        with self.assertRaises(ValueError):a.pool_configuration("B3","solo","A",True,True)
        with self.assertRaises(ValueError):a.pool_configuration("B1","fp_ps","A",True,True)

if __name__=="__main__":
    unittest.main()
