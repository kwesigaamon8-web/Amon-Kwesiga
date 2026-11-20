"""Offline regression tests for evidence-only B1/B2 worker report routing."""
import json
import tempfile
import unittest
from pathlib import Path

from b_worker_intelligence_router import DEFINED_PER_FLEET, generate


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / "out"

    def put(self, fleet, role, *, status="MODEL_COMPLETED_NEEDS_REVIEW",
            grade="QUALIFIED_SOURCE_BACKED_AI_RESEARCH", sources=None,
            director=None, parent=None):
        folder = self.root / fleet / "workers"
        folder.mkdir(parents=True, exist_ok=True)
        parts = role.split("-")
        record = {
            "worker_id": fleet + "/" + role,
            "director": fleet + "/" + (director or parts[0]),
            "direct_parent": fleet + "/" + (parent or "-".join(parts[:-1])),
            "actual_execution_status": status,
            "strict_grade": grade,
            "strict_defects": [],
            "source_links_unverified_as_paying": sources or [],
            "next_action": "Verify original source and whether buyer explicitly wants help"
        }
        (folder / (role + ".json")).write_text(json.dumps(record), encoding="utf-8")

    def test_b1_lead_to_b1_and_qa_failure_to_b2(self):
        self.put("transferexperiment", "D01-M01-W01",
                 sources=["https://github.com/real/repo/issues/1"])
        self.put("transferexperiment", "D02-M02-W02",
                 status="NO_COMPLETED_MODEL_EVIDENCE")
        result = generate("transferexperiment", self.root, self.out, "https://github.com/example/run/1")
        self.assertEqual(result["attempt_reports_validated"], 2)
        self.assertEqual(result["primary_agent"], "B1")
        p = self.out / "transferexperiment"
        b1 = json.loads((p / "B1_INBOX.json").read_text())
        b2 = json.loads((p / "B2_INBOX.json").read_text())
        self.assertEqual(b1["inbox_eligible_attempt_reports"], 2)
        self.assertEqual(b2["inbox_eligible_attempt_reports"], 1)
        self.assertEqual(b2["items"][0]["kind"], "EXECUTION_OR_MODEL_FAILURE")
        self.assertEqual(b1["items"][1]["worker_id"], "transferexperiment/D01-M01-W01")
        self.assertEqual(b1["items"][1]["routing_chain"],
                         ["transferexperiment/D01-M01-W01",
                          "transferexperiment/D01-M01", "transferexperiment/D01", "B1", "CHIEF_D"])
        self.assertEqual(b1["customer_acceptances_verified"], 0)
        self.assertEqual(result["total_configured_both_fleets"], 2 * DEFINED_PER_FLEET)

    def test_cross_company_report_is_rejected(self):
        self.put("BountyScoutAI", "D01-M01-W01")
        bad = self.root / "BountyScoutAI" / "workers" / "D01-M01-W01.json"
        record = json.loads(bad.read_text())
        record["worker_id"] = "transferexperiment/D01-M01-W01"
        bad.write_text(json.dumps(record))
        result = generate("BountyScoutAI", self.root, self.out)
        self.assertEqual(result["attempt_reports_validated"], 0)
        self.assertEqual(result["rejected_reports"].get("BAD_OR_CROSS_FLEET_ID"), 1)

    def test_wrong_parent_rejected_no_live_claim(self):
        self.put("BountyScoutAI", "D03-M02-W01", parent="D03-M01")
        result = generate("BountyScoutAI", self.root, self.out)
        self.assertEqual(result["rejected_reports"].get("WRONG_PARENT"), 1)
        self.assertEqual(result["verified_agent_read_receipts"], 0)

    def test_empty_run_writes_honest_inboxes(self):
        result = generate("BountyScoutAI", self.root, self.out)
        self.assertEqual(result["attempt_reports_validated"], 0)
        inbox = json.loads((self.out / "BountyScoutAI" / "B2_INBOX.json").read_text())
        self.assertEqual(inbox["items"], [])
        self.assertEqual(inbox["payments_verified_by_this_router"], "NOT_ASSESSED")
        self.assertTrue(inbox["configured_roles_are_not_active_agents"])

    def test_cannot_route_invalid_role_path(self):
        self.put("transferexperiment", "D01-M16-W01")
        report = generate("transferexperiment", self.root, self.out)
        self.assertEqual(report["rejected_reports"].get("INVALID_ROLE_ANCESTRY"), 1)


if __name__ == "__main__":
    unittest.main()
