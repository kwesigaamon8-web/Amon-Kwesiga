"""Capability-first lazy assignments for B1/B2 software worker roles.

Every indexed role can receive an individual task at real invocation. No
assignment creates an AI process, miner, account, customer, submission or money.
Distinct role IDs and their canonical hierarchy are not changed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re

FLEETS=("transferexperiment","BountyScoutAI")
SKILL_LANES=(
 {"id":"BUYER_SOURCE","skill":"public source research and market evaluation",
  "deliverable":"ONE original current customer/paid-bounty URL, scope, buyer contact route and source timestamp",
  "blocker":"NO_ORIGINAL_FUNDED_BUYER"},
 {"id":"PAYER_VALIDATE","skill":"critical evidence, funding and eligibility audit",
  "deliverable":"Independent proof of payer, available reward, owner eligibility, deadline, competing PRs and claim terms",
  "blocker":"PAYER_OR_ELIGIBILITY_NOT_VERIFIED"},
 {"id":"BUILD_ORIGINAL","skill":"original coding, document/data services and legal reuse",
  "deliverable":"Testable ORIGINAL code/sample or substantial requested useful work plus source/license checks",
  "blocker":"NO_ACCEPTED_OR_BUILDABLE_SCOPE"},
 {"id":"QA_REVIEW","skill":"unit tests, regression and original work quality checking",
  "deliverable":"Reproducible tests, pass/fail results and one concrete remediation of a real work product",
  "blocker":"NO_ACTUAL_ARTIFACT_TO_REVIEW"},
 {"id":"BUYER_CONTACT","skill":"authorized relevant buyer outreach and sales",
  "deliverable":"One contextual permission-checked actual contact/submission reference or a ready-to-send draft marked UNSENT",
  "blocker":"BLOCKED_AUTH_NO_BUYER_CHANNEL"},
 {"id":"PAYMENT_EVIDENCE","skill":"receivables and correct-chain crypto reconciliation",
  "deliverable":"Payer/accepted contract evidence, asset, chain, amount and genuine confirmed TXID or explicit NOT VERIFIED",
  "blocker":"NO_VERIFIED_ACCEPTED_PAYMENT"},
 {"id":"ASIC_PARTNER","skill":"consent-based physical Bitcoin mining partner economics",
  "deliverable":"Actual opt-in ASIC owner plus equipment/hashrate/pool/energy-cost evidence or clearly NO REAL MINER",
  "blocker":"BLOCKED_NO_CONSENTING_MINER_HARDWARE"},
 {"id":"HOST_RESEARCH","skill":"official permitted $0 hosting and online deployment capability",
  "deliverable":"Two original official provider pages, free CPU/sleep/terms and owner-authorized connected account status",
  "blocker":"NO_AUTHORIZED_FREE_EXECUTION_HOST"},
 {"id":"PROOF_AUDIT","skill":"project work audit, deadline filtering and evidence-led reports",
  "deliverable":"Check one original candidate or model run for authentic output, accepted customer and paid evidence",
  "blocker":"EVIDENCE_UNAVAILABLE"},
 {"id":"REPAIR_AND_SUPPORT","skill":"software test repair and small low-cost original demos",
  "deliverable":"Small proven source patch/test or clear technical reproduction of a genuine blocker",
  "blocker":"NO_REPRODUCIBLE_DEFECT"},
)
KEYWORDS={
 "BUYER_SOURCE":("market","sales lead","research","customer","prospect","discovery","search"),
 "PAYER_VALIDATE":("audit","fraud","eligib","compliance","funding","risk","investigat"),
 "BUILD_ORIGINAL":("code","program","software","frontend","web","document","content","json","data","spreadsheet"),
 "QA_REVIEW":("test","quality","review","lint","verify","security"),
 "BUYER_CONTACT":("outreach","negotiat","partnership","marketplace","communication","sales"),
 "PAYMENT_EVIDENCE":("payment","invoice","receivable","crypto ledger","wallet","settlement"),
 "ASIC_PARTNER":("mining","asic","pool","hash","bitcoin rig","energy"),
 "HOST_RESEARCH":("hosting","cloud","deploy","server","virtual machine","infra"),
 "PROOF_AUDIT":("monitor","report","research validation","evidence","accountability"),
 "REPAIR_AND_SUPPORT":("bug","fix","repair","debug","maintain","automation"),
}
LANES={x["id"]:x for x in SKILL_LANES}
def dispatch(fleet,role_id,specialty,director_id,level):
    if fleet not in FLEETS:raise ValueError("Unknown B company")
    if not isinstance(role_id,str) or not re.fullmatch(r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)(?:-S\d{3}(?:-G\d{3}(?:-H\d{3})?)?)?",role_id):
        raise ValueError("Unknown active role format")
    if director_id!=role_id[:3]:raise ValueError("Director mismatch")
    if level not in ("W","S","G","H"):raise ValueError("Unknown role level")
    digest=hashlib.sha256((fleet+"/"+role_id).encode()).digest()
    # D10 gets payment verification duties first; local D10s are independent.
    if director_id=="D10":lane_id="PAYMENT_EVIDENCE"
    else:
        cleaned=str(specialty or "").lower()
        scores={name:sum(1 for term in terms if term in cleaned) for name,terms in KEYWORDS.items()}
        best=max(scores.values())
        candidates=sorted(name for name,score in scores.items() if score==best) if best else [x["id"] for x in SKILL_LANES if x["id"]!="PAYMENT_EVIDENCE"]
        lane_id=candidates[int.from_bytes(digest[:4],"big")%len(candidates)]
    secondary=["ASIC_PARTNER","HOST_RESEARCH","QA_REVIEW","PAYER_VALIDATE"]
    secondary_id=secondary[digest[4]%len(secondary)]
    if secondary_id==lane_id:secondary_id=secondary[(digest[4]+1)%len(secondary)]
    parent=role_id.rsplit("-",1)[0]
    primary=LANES[lane_id]
    return {
      "schema":"B_CAPABILITY_FIRST_DISPATCH_V1",
      "company":fleet,"role_id":role_id,"level":level,"original_immediate_parent":parent,
      "local_director":fleet+"/"+director_id,"reports_to":fleet+"/"+parent,
      "unique_task_id":"CAP-"+hashlib.sha256((fleet+":"+role_id).encode()).hexdigest()[:18],
      "assignment_state":"ROLE_ASSIGNED_NOT_EXECUTED",
      "primary_lane":lane_id,"why_suitable":primary["skill"],
      "one_actual_primary_action":primary["deliverable"],
      "if_missing_prerequisite":primary["blocker"],
      "optional_secondary_lane":secondary_id,
      "second_action_only_if_capable_and_permitted":LANES[secondary_id]["deliverable"],
      "must_not_claim_every_role_online":True,
      "real_model_call_performed_by_dispatch":False,
      "external_contact_or_deployment_performed_by_dispatch":False,
      "actual_bitcoin_miner_created":False,
      "amount_earned_by_dispatch":0,
      "source_and_acceptance_required":True,
      "permission_to_sign_spend_or_create_accounts":False,
      "report_required":"actual run ID; permitted tools; real source; artifact/test; external action receipt or NOT_SENT; amount/asset/chain/TXID or NOT_VERIFIED; one-parent report; next action"
    }
def self_test():
    examples=[]
    for fleet in FLEETS:
        for d in range(1,11):
            for i in range(1,51):
                role=f"D{d:02d}-M01-W{i:02d}"
                p=dispatch(fleet,role,SKILL_LANES[i%len(SKILL_LANES)]["skill"],role[:3],"W")
                examples.append(p)
    assert len({(p["company"],p["role_id"]) for p in examples})==len(examples)
    assert len({p["unique_task_id"] for p in examples})==len(examples)
    assert all(p["primary_lane"]=="PAYMENT_EVIDENCE" for p in examples if p["local_director"].endswith("D10"))
    assert len({p["primary_lane"] for p in examples})>=7
    assert all(p["primary_lane"]!=p["optional_secondary_lane"] for p in examples)
    assert all(not p["real_model_call_performed_by_dispatch"] and p["amount_earned_by_dispatch"]==0 for p in examples)
    nested=dispatch("transferexperiment","D01-M01-W01-S001-G001-H001","original software QA","D01","H")
    assert nested["reports_to"]=="transferexperiment/D01-M01-W01-S001-G001"
    return {"result":"PASS","test_role_assignments":len(examples),"distinct_primary_lanes":len({p["primary_lane"] for p in examples}),
      "all_750377265361_models_started":False,"real_accounts_created":0,"new_miners_created":0,"payments_verified_by_test":0}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true")
    p.add_argument("--fleet",choices=FLEETS);p.add_argument("--role");p.add_argument("--specialty",default="original research")
    p.add_argument("--level",default="W")
    a=p.parse_args()
    if a.self_test:print("B_CAPABILITY_DISPATCH_TEST",json.dumps(self_test()))
    else:
        if not a.fleet or not a.role:p.error("Supply fleet and role")
        print(json.dumps(dispatch(a.fleet,a.role,a.specialty,a.role[:3],a.level),indent=2))
