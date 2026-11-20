"""Regression coverage for all-addressable but bounded B1/B2 message routing."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("role_messages.py")
spec = importlib.util.spec_from_file_location("role_messages", PATH)
# Supply the sibling import used by the standalone CLI.
sys.path.insert(0, str(PATH.parent))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class MessageTests(unittest.TestCase):
    def test_exact_address_space(self):
        self.assertEqual(mod.ALL_ROLES, 750377265360)
        self.assertEqual(mod.PER_FLEET, 375188632680)

    def test_unique_addresses_and_stable_message_ids(self):
        samples = (0, 1, 9, 10, 30, 1000000,
                   mod.PER_FLEET-1, mod.PER_FLEET, mod.ALL_ROLES-1)
        ids = set()
        for index in samples:
            fleet, local = mod.fleet_for_global_index(index)
            role = mod.role_from_local_index(local)
            a = mod.build_message(fleet, role)
            b = mod.build_message(fleet, role)
            self.assertEqual(a["message_id"], b["message_id"])
            self.assertNotIn(a["message_id"], ids)
            ids.add(a["message_id"])
            self.assertEqual(a["global_index_zero_based"], index)
            self.assertEqual(a["delivery_status"], "VIRTUAL_ADDRESS_ONLY_NOT_SENT")
            self.assertFalse(a["received_by_real_worker_process"])
            self.assertFalse(a["external_platform_posted"])
            self.assertIsNone(a["verified_external_post_url"])

    def test_actual_worker_process_receives_one_personalized_message(self):
        role = "D01-M01-W01"
        a = mod.worker_process_order("transferexperiment", role)
        self.assertEqual(a["recipient"]["role"], role)
        self.assertTrue(a["received_by_real_worker_process"])
        self.assertEqual(a["delivery_status"], "READ_BY_ACTUAL_WORKER_PROCESS_AT_START")
        self.assertFalse(a["AI_model_read_receipt_verified"])
        self.assertFalse(a["external_platform_posted"])
        msg = mod.model_instruction(a)
        self.assertIn(role, msg)
        self.assertIn(a["message_id"], msg)
        self.assertIn("Chief D", msg)

    def test_unexecuted_role_not_eligible_for_model_ack(self):
        a = mod.build_message("BountyScoutAI", "D09-M15-W50-S150-G500-H666")
        with self.assertRaises(ValueError):
            mod.model_instruction(a)
        self.assertFalse(a["verified_buyer_acceptance"])

    def test_rejected_roles(self):
        for bad in ("D00", "D11", "D01-M16", "D01-M01-W51"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                mod.build_message("transferexperiment", bad)

    def test_separate_fleet_routing(self):
        for fleet, agent in zip(mod.FLEETS, ("B1", "B2")):
            a = mod.build_message(fleet, "D10-M15-W50-S150-G500-H666")
            self.assertEqual(a["recipient"]["agent"], agent)
            self.assertEqual(a["routing"]["reported_to_agent"], agent)

    def test_cli_highest_index_and_five_samples_do_not_send(self):
        for args, expected_count in (
            (["--global-index", str(mod.ALL_ROLES-1)], 1),
            (["--sample", "5"], 5),
        ):
            result = subprocess.run([sys.executable, str(PATH), *args],
                                    capture_output=True, text=True, check=True)
            j = json.loads(result.stdout)
            self.assertEqual(j["message_space_available"], mod.ALL_ROLES)
            self.assertEqual(j["message_templates_materialized_in_this_call"], expected_count)
            self.assertEqual(j["actual_messages_transmitted_to_live_accounts"], 0)
            self.assertEqual(j["actual_social_media_posts_sent"], 0)

    def test_email_and_platform_safety(self):
        a = mod.build_message("transferexperiment", "D01")
        rules = a["permission_rules"]
        self.assertTrue(rules["no_email_read_draft_or_send"])
        self.assertTrue(rules["no_unsolicited_bulk_posts_or_dms"])
        self.assertTrue(rules["external_post_requires_connected_account_and_platform_permission"])


if __name__ == "__main__":
    unittest.main()
