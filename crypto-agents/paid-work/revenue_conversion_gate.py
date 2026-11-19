"""Reject fake/noncash earning leads before allocating B1/B2 AI time.

Source metadata in conversion-targets.json is a dated human-reviewed snapshot;
this script does not independently validate an on-chain transaction or contact.
"""
import json
from pathlib import Path

ROOT=Path("crypto-agents/paid-work")
INPUT=ROOT/"conversion-targets.json"
OUTPUT=Path("paid-opportunity-reports/conversion-scorecard.json")

def evaluate(x):
    fail=[]
    if x["reward_kind"]!="transferable_crypto":
        fail.append("NOT_CRYPTO_CASH")
    if x["region"] not in ("global","uganda"):
        fail.append("REGION_NOT_VERIFIED_FOR_UGANDA")
    if x.get("spend_required",False):
        fail.append("OWNER_SPENDING_PROHIBITED")
    if not x.get("source_url","").startswith("https://"):
        fail.append("SOURCE_URL_MISSING")
    if x.get("receipt_verified") and not all(x.get(k) for k in ("txid","amount","network","payer_context")):
        fail.append("RECEIPT_WITHOUT_CHAIN_AND_PAYER_EVIDENCE")
    if x.get("submission_verified") and not x.get("submission_url"):
        fail.append("SUBMISSION_WITHOUT_ACCEPTANCE_ROUTE")
    # Auth alone cannot make a task actionable: an account can submit an
    # ineligible, unfunded, or wrong-network claim and still return HTTP 200.
    if x.get("auth_submission_available") and not x.get("eligibility_verified",False):
        fail.append("ELIGIBILITY_NOT_VERIFIED")
    if x.get("auth_submission_available") and not x.get("funding_verified",False):
        fail.append("FUNDING_NOT_VERIFIED")
    if x.get("auth_submission_available") and not x.get("payout_route_verified",False):
        fail.append("PAYOUT_ROUTE_NOT_VERIFIED")
    if x.get("auth_submission_available") and not x.get("ready_deliverable",False):
        fail.append("DELIVERABLE_NOT_READY")
    if fail:
        status="REJECT_OR_HOLD"
    elif x.get("receipt_verified"):
        status="DECLARED_RECEIPT_NEEDS_EXTERNAL_CHAIN_CHECK"
    elif x.get("accepted"):
        status="ACCEPTED_AWAITING_RECEIPT"
    elif x.get("submission_verified"):
        status="SUBMITTED_PENDING_ACCEPTANCE"
    elif x.get("auth_submission_available"):
        status="ELIGIBLE_ACTIONABLE_WITH_PERMITTED_ACCESS"
    elif x.get("ready_deliverable"):
        status="DELIVERABLE_READY_EXTERNAL_AUTH_BLOCKED"
    else:
        status="RESEARCH_NOT_SUBMITTABLE"
    return {"id":x["id"],"source":x.get("source_url"),"status":status,
            "reasons":fail,"owner_action":x.get("owner_action",""),
            "no_earned_revenue_inferred":True}

def test():
    a={"id":"test","reward_kind":"transferable_crypto","region":"global",
       "source_url":"https://example.com","ready_deliverable":True}
    assert evaluate(a)["status"]=="DELIVERABLE_READY_EXTERNAL_AUTH_BLOCKED"
    assert "REGION_NOT_VERIFIED_FOR_UGANDA" in evaluate(a|{"region":"ukraine"})["reasons"]
    assert "NOT_CRYPTO_CASH" in evaluate(a|{"reward_kind":"service_credit"})["reasons"]
    assert "OWNER_SPENDING_PROHIBITED" in evaluate(a|{"spend_required":True})["reasons"]
    assert "RECEIPT_WITHOUT_CHAIN_AND_PAYER_EVIDENCE" in evaluate(a|{"receipt_verified":True})["reasons"]
    assert evaluate(a|{"submission_verified":True,"submission_url":"https://example.com/issue"})["status"]=="SUBMITTED_PENDING_ACCEPTANCE"
    waiting=evaluate(a|{"auth_submission_available":True})
    assert waiting["status"]=="REJECT_OR_HOLD"
    assert set(waiting["reasons"])=={"ELIGIBILITY_NOT_VERIFIED","FUNDING_NOT_VERIFIED","PAYOUT_ROUTE_NOT_VERIFIED"}
    ready=a|{"auth_submission_available":True,"eligibility_verified":True,
             "funding_verified":True,"payout_route_verified":True}
    assert evaluate(ready)["status"]=="ELIGIBLE_ACTIONABLE_WITH_PERMITTED_ACCESS"
    assert "DELIVERABLE_NOT_READY" in evaluate(ready|{"ready_deliverable":False})["reasons"]
    print("CRYPTO_PAYMENT_CONVERSION_GATE_SELF_TEST_PASS")

def run():
    test()
    candidates=json.loads(INPUT.read_text())
    assert len(candidates)==len({x["id"] for x in candidates})
    result=[evaluate(x) for x in candidates]
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n")
    counters={k:sum(y["status"]==k for y in result)
              for k in sorted({y["status"] for y in result})}
    print("ACTUAL_PAYMENT_CONVERSION_GATES",json.dumps(
        {"candidate_count":len(result),"status_counts":counters,
         "verified_income_from_pipeline":False}))
    for y in result:
        print("PAYMENT_GATE",y["id"],y["status"],
              ";".join(y["reasons"]) or y["owner_action"])

if __name__=="__main__":run()
