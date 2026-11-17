"""Read-only BTC mainnet bounty qualification gate. No network, wallet, or signing access.
Run: python3 inventions/btc_bounty_acceptance_gate.py --self-test
Input JSON object: buyer_url, buyer_identity, reward_btc, payment_network,
claim_route, submission_route, funding_proof_url, acceptance_criteria,
uganda_eligible, upfront_fee_btc, buyer_confirmed.
This is a conservative triage tool, not a guarantee of escrow or payment.
"""
import json
import sys
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

REQUIRED = ("buyer_url", "buyer_identity", "reward_btc", "payment_network",
            "claim_route", "submission_route", "funding_proof_url",
            "acceptance_criteria", "uganda_eligible", "upfront_fee_btc",
            "buyer_confirmed")

def https_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username

def assess(record):
    failures = []
    if not isinstance(record, dict):
        return {"eligible_for_review": False, "blockers": ["Input must be a JSON object"]}
    for key in REQUIRED:
        if key not in record:
            failures.append("Missing: " + key)
    if failures:
        return {"eligible_for_review": False, "blockers": failures}
    for key in ("buyer_url", "claim_route", "submission_route", "funding_proof_url"):
        if not https_url(record[key]):
            failures.append(key + ": HTTPS evidence URL required")
    for key in ("buyer_identity", "acceptance_criteria"):
        if not isinstance(record[key], str) or not record[key].strip():
            failures.append(key + ": nonempty text required")
    try:
        reward = Decimal(str(record["reward_btc"]))
        fee = Decimal(str(record["upfront_fee_btc"]))
        if not reward.is_finite() or reward <= 0:
            failures.append("Reward must be positive finite BTC")
        if not fee.is_finite() or fee != 0:
            failures.append("No upfront fees allowed")
    except (InvalidOperation, ValueError):
        failures.append("Invalid reward or fee")
    if record["payment_network"] != "bitcoin-mainnet":
        failures.append("Native Bitcoin mainnet payout not established")
    if record["uganda_eligible"] is not True:
        failures.append("Uganda eligibility not confirmed")
    if record["buyer_confirmed"] is not True:
        failures.append("Buyer has not confirmed paid commission")
    return {"eligible_for_review": not failures, "blockers": failures,
            "note": "Passing checks only verifies supplied fields, NOT actual funding, authenticity, claim, submission, acceptance or settlement."}

def self_test():
    base = dict(buyer_url="https://example.org/buyer", buyer_identity="Buyer",
                reward_btc="0.0005", payment_network="bitcoin-mainnet",
                claim_route="https://example.org/claim",
                submission_route="https://example.org/submit",
                funding_proof_url="https://example.org/funding",
                acceptance_criteria="Deliver and pass buyer tests",
                uganda_eligible=True, upfront_fee_btc="0", buyer_confirmed=True)
    assert assess(base)["eligible_for_review"]
    for key, value in [("reward_btc","NaN"), ("reward_btc","-1"),
                       ("upfront_fee_btc","0.01"), ("payment_network","lightning"),
                       ("uganda_eligible",False), ("buyer_confirmed",False),
                       ("funding_proof_url","http://example.org")]:
        case = dict(base, **{key:value})
        assert not assess(case)["eligible_for_review"], key
    assert not assess({})["eligible_for_review"]
    assert not assess([])["eligible_for_review"]
    print("10/10 local assertions passed; no external claims verified")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    else:
        print(json.dumps(assess(json.load(sys.stdin)), indent=2))
