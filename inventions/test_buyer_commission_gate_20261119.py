"""Offline regression tests for the buyer-commission gate."""
import importlib.util
import pathlib
import unittest

p = pathlib.Path(__file__).with_name("buyer-commission-gate-20261119.py")
spec = importlib.util.spec_from_file_location("gate", p)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class GateTests(unittest.TestCase):
    def valid(self):
        return dict(buyer_identity_url="https://example.org/buyer",
                    buyer_task_url="https://example.org/job",
                    deliverable="CSV report",
                    acceptance_criteria="100 rows, totals agree",
                    fee_amount=5, fee_asset="BTC",
                    fee_network="bitcoin-mainnet",
                    deadline_utc="2026-11-25T12:00:00Z",
                    submission_url="https://example.org/job",
                    upfront_fee_required=False,
                    buyer_authorized_submission=True,
                    payer_funding_evidence_url="https://example.org/funding",
                    receiving_route_verified=True)
    def test_complete_is_only_review_ready(self):
        result = gate.assess(self.valid())
        self.assertTrue(result["ready_for_human_evidence_review"])
        self.assertFalse(result["paid_or_accepted"])
        self.assertFalse(result["chain_receipt_verified"])
    def test_unverified_route_rejected(self):
        d = self.valid(); d["receiving_route_verified"] = False
        self.assertFalse(gate.assess(d)["ready_for_human_evidence_review"])
    def test_lightning_not_mainnet(self):
        d = self.valid(); d["fee_network"] = "lightning"
        self.assertIn("supported_asset_network_pair", gate.assess(d)["missing_or_unverified"])
    def test_no_fee_or_bool_fee_rejected(self):
        for fee in (0, -1, True):
            d = self.valid(); d["fee_amount"] = fee
            self.assertFalse(gate.assess(d)["ready_for_human_evidence_review"])
    def test_upfront_fee_rejected(self):
        d = self.valid(); d["upfront_fee_required"] = True
        self.assertFalse(gate.assess(d)["ready_for_human_evidence_review"])

if __name__ == "__main__":
    unittest.main()
