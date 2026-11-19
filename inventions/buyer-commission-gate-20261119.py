"""Offline evidence gate for a crypto-paid microservice commission.
No blockchain queries, emails, wallet actions or payment assertions.
Usage: python buyer-commission-gate-20261119.py commission.json
"""
import json
import sys
from pathlib import Path

FIELDS = ("buyer_identity_url", "buyer_task_url", "deliverable",
          "acceptance_criteria", "fee_amount", "fee_asset", "fee_network",
          "deadline_utc", "submission_url")
ALLOWED = {"BTC": {"bitcoin-mainnet"}, "USDC": {"base", "solana", "stellar", "tron"}}

def assess(d):
    missing = [k for k in FIELDS if not d.get(k)]
    if not isinstance(d.get("fee_amount"), (int, float)) or isinstance(d.get("fee_amount"), bool) or d.get("fee_amount", 0) <= 0:
        missing.append("positive_numeric_fee")
    asset, network = d.get("fee_asset"), d.get("fee_network")
    if network not in ALLOWED.get(asset, set()):
        missing.append("supported_asset_network_pair")
    if d.get("upfront_fee_required") is not False:
        missing.append("no_upfront_fee_verified")
    if d.get("buyer_authorized_submission") is not True:
        missing.append("buyer_authorized_submission")
    if d.get("payer_funding_evidence_url") is None:
        missing.append("payer_funding_evidence_url")
    if d.get("receiving_route_verified") is not True:
        missing.append("receiving_route_verified")
    # URLs alone are self-declarations, not independently authenticated evidence.
    return {"ready_for_human_evidence_review": not missing,
            "missing_or_unverified": sorted(set(missing)),
            "paid_or_accepted": False,
            "chain_receipt_verified": False,
            "note": "Human must independently verify buyer, funding, authorization, exact asset/network/route and acceptance."}

def main():
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(assess(data), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
