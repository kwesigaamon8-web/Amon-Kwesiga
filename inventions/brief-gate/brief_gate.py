"""BriefGate: offline commission-readiness checklist, not buyer verification.
Run: python brief_gate.py brief.json ; python brief_gate.py --test
No network, keys, payments, or automatic acceptance. All evidence is caller-supplied.
Market hypothesis: small Bitcoin bounty sponsors and technical writers on
BitcoinTalk Services / GitHub opt-in commissions. Proposed pilot 20,000 sats
for one reviewed brief; no buyer has agreed to that price or commissioned this.
Difference from Proof-to-Payout Capsule: pre-work missing-terms gate, not TX proof.
Alternatives checked 2026-11-17: GitHub issue forms collect structured fields
(https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms);
BIP21/321 encode payment requests, not work acceptance criteria
(https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki).
This is a narrow integration hypothesis, not a claim of absolute novelty.
"""
import json
import sys
import unittest
from datetime import datetime, timezone

ROUTES = {
    "B1": "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
    "B2": "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}

def review(brief, now):
    """Return gaps; even no gaps means human review, never verified engagement."""
    gaps = []
    for field in ("buyer_profile_url", "buyer_offer_url", "scope",
                  "acceptance_criteria", "funding_evidence_url",
                  "buyer_agreement_url", "region_eligibility_evidence_url"):
        value = brief.get(field)
        if not isinstance(value, str) or not value.strip():
            gaps.append("missing:" + field)
        elif field.endswith("_url") and not value.startswith("https://"):
            gaps.append("https_required:" + field)
    amount = brief.get("fee_sats")
    if type(amount) is not int or amount <= 0:
        gaps.append("positive_integer_fee_sats_required")
    if brief.get("asset") != "BTC" or brief.get("network") != "bitcoin-mainnet":
        gaps.append("unsupported_payment_route")
    account = brief.get("account")
    if account not in ROUTES or brief.get("address") != ROUTES.get(account):
        gaps.append("owner_route_mismatch")
    if brief.get("upfront_worker_cost_sats") != 0 or type(brief.get("upfront_worker_cost_sats")) is not int:
        gaps.append("zero_worker_cost_required")
    try:
        deadline = datetime.fromisoformat(brief.get("deadline", "").replace("Z", "+00:00"))
        if deadline.tzinfo is None or deadline <= now:
            gaps.append("deadline_expired_or_naive")
    except (ValueError, TypeError, AttributeError):
        gaps.append("valid_deadline_required")
    return {"status": "HOLD" if gaps else "READY_FOR_INDEPENDENT_REVIEW",
            "gaps": gaps, "buyer_verified": False, "engagement_accepted": False,
            "payment_received": False,
            "warning": "Presence of URLs does not verify their contents, funding or agreement."}

class Tests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 17, tzinfo=timezone.utc)
        self.b = {k: "https://example.invalid/fixture" for k in (
            "buyer_profile_url", "buyer_offer_url", "funding_evidence_url",
            "buyer_agreement_url", "region_eligibility_evidence_url")}
        self.b.update(scope="Synthetic guide", acceptance_criteria="Synthetic checklist",
                      fee_sats=20000, asset="BTC", network="bitcoin-mainnet",
                      account="B1", address=ROUTES["B1"], upfront_worker_cost_sats=0,
                      deadline="2026-12-01T00:00:00Z")
    def test_complete_still_unverified(self):
        r=review(self.b,self.now)
        self.assertEqual(r["status"],"READY_FOR_INDEPENDENT_REVIEW")
        self.assertFalse(r["buyer_verified"] or r["engagement_accepted"] or r["payment_received"])
    def test_ln_not_mainnet(self):
        self.b["network"]="lightning"
        self.assertIn("unsupported_payment_route",review(self.b,self.now)["gaps"])
    def test_missing_acceptance(self):
        del self.b["buyer_agreement_url"]
        self.assertIn("missing:buyer_agreement_url",review(self.b,self.now)["gaps"])
    def test_wrong_recipient(self):
        self.b["address"]=ROUTES["B2"]
        self.assertIn("owner_route_mismatch",review(self.b,self.now)["gaps"])
    def test_expired(self):
        self.b["deadline"]="2026-11-01T00:00:00Z"
        self.assertIn("deadline_expired_or_naive",review(self.b,self.now)["gaps"])
    def test_fee_bool_rejected(self):
        self.b["fee_sats"]=True
        self.assertIn("positive_integer_fee_sats_required",review(self.b,self.now)["gaps"])
    def test_worker_spending(self):
        self.b["upfront_worker_cost_sats"]=1
        self.assertIn("zero_worker_cost_required",review(self.b,self.now)["gaps"])
    def test_empty(self):
        self.assertEqual(review({},self.now)["status"],"HOLD")

if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        unittest.main(argv=[sys.argv[0]])
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            print(json.dumps(review(json.load(f), datetime.now(timezone.utc)), indent=2))
