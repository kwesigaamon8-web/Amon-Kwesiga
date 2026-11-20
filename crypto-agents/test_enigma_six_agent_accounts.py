"""Offline six-agent regression tests. No mailboxes or network required."""
import json
import tempfile
import unittest
from pathlib import Path
from enigma_six_agent_accounts import ROLE_NAMES, POLICY, role_packet, run_agents

class EnigmaAgentTests(unittest.TestCase):
    def test_six_unique_private_mailbox_aliases_no_email_credentials(self):
        self.assertEqual(len(ROLE_NAMES), 6)
        packets = [role_packet(r) for r in ROLE_NAMES]
        self.assertEqual(len({p["id"] for p in packets}), 6)
        self.assertEqual(len({p["account_alias"] for p in packets}), 6)
        for p in packets:
            self.assertFalse(p["connected_github_mailbox_credentials"])
            self.assertFalse(p["external_social_account_created"])
            self.assertNotIn("@", json.dumps(p))
            self.assertEqual(p["email_messages_sent"], 0)
            self.assertFalse(p["model_call_completed"])

    def test_six_discrete_actual_inference_calls_can_be_recorded(self):
        calls = []
        def model(prompt, **kwargs):
            calls.append((prompt, kwargs))
            return [{"generated_text": "1. Verify source. 2. Run tests. 3. Label uncertainty."}]
        with tempfile.TemporaryDirectory() as d:
            s = run_agents(enable_model=True, generator=model, output_dir=Path(d))
            self.assertEqual(len(calls), 6)
            self.assertEqual(s["model_calls_completed"], 6)
            self.assertEqual(s["email_messages_sent"], 0)
            self.assertEqual(s["accounts_linked_to_github_runners"], 0)
            for i in range(1, 7):
                p = json.loads((Path(d) / f"ENIGMA-{i:02d}.json").read_text())
                self.assertTrue(p["model_call_completed"])
                self.assertEqual(p["model_inference_status"], "MODEL_COMPLETED_OUTPUT_NOT_FACT_VERIFIED")

    def test_no_inference_is_not_counted_as_live_agent(self):
        with tempfile.TemporaryDirectory() as d:
            s = run_agents(enable_model=False, output_dir=d)
            self.assertEqual(s["model_calls_completed"], 0)
            self.assertFalse(s["model_execution_requested"])
            self.assertEqual(len(list(Path(d).glob("ENIGMA-*.json"))), 6)

    def test_error_or_empty_response_does_not_fake_model_execution(self):
        with tempfile.TemporaryDirectory() as d:
            def failed(prompt, **kwargs):
                raise RuntimeError("Inference backend unavailable")
            s = run_agents(enable_model=True, generator=failed, output_dir=d)
            self.assertEqual(s["model_calls_completed"], 0)
            p = json.loads((Path(d) / "ENIGMA-01.json").read_text())
            self.assertEqual(p["model_inference_status"], "MODEL_ERROR:RuntimeError")
        with tempfile.TemporaryDirectory() as d:
            s = run_agents(enable_model=True, generator=lambda *a, **k: [{"generated_text": ""}], output_dir=d)
            self.assertEqual(s["model_calls_completed"], 0)

if __name__ == "__main__":
    unittest.main()
