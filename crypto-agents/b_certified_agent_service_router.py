"""Route ALL 750,377,265,360 original B roles to opted-in CERTIFIED agent work.

Deterministic ROLE ADDRESSABILITY is not real AI execution, employment,
certification, client consent or earned revenue. An external principal is an
authorized buyer, NOT the worker's actual owner or internal reporting parent.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from command_chain_receipts import level,route
from owner_first_oath import current_order

ROOT=Path("crypto-agents")
REGISTRY=ROOT/"b_certified_agent_engagements.json"
ROUTES=ROOT/"b_collection_assignments.json"
FLEETS=("transferexperiment","BountyScoutAI")
PER_DIRECTOR={
    "D":1,
    "A":2,
    "M":15,
    "W":750,
    "S":112_500,
    "G":56_250_000,
    "H":37_462_500_000,
}
OFFSETS={}
cursor=0
for kind,num in PER_DIRECTOR.items():
    OFFSETS[kind]=cursor
    cursor+=num
ROLES_PER_DIRECTOR=cursor
DIRECTORS_PER_FLEET=10
TOTAL_ROLES=ROLES_PER_DIRECTOR*DIRECTORS_PER_FLEET*len(FLEETS)
assert ROLES_PER_DIRECTOR==37_518_863_268
assert TOTAL_ROLES==750_377_265_360

TASKS=(
    "Original software patch, test, documentation or integration for authorized agent",
    "Research and prepare an evidence-backed, customer-approved client deliverable",
    "Clean, transform and validate client-approved data with original quality checks",
    "Produce an original agent-support workflow, template or service with QA evidence",
    "Find current legitimate paid assistant tasks and verify operator eligibility",
    "Verify requirements, funding, customer acceptance and payer identity",
    "Write and test a concise original Python utility for a customer-approved problem",
    "Perform a read-only correct-network crypto payment reconciliation for an approved engagement",
    "Review licence, data access and platform rules before any source reuse",
    "Prepare original service proposal for a willing client with exact acceptance criteria",
)

def company_wallet(fleet):
    if fleet not in FLEETS:raise ValueError("Unknown B company")
    row=json.loads(ROUTES.read_text(encoding="utf-8"))["fleets"][fleet]
    assert row["asset"]=="BTC" and row["network"]=="Bitcoin mainnet"
    return row["address"]

def role_index(fleet,role):
    """Collision-free rank for EVERY defined ORIGINAL D/A/M/W/S/G/H role."""
    if fleet not in FLEETS:raise ValueError("Unknown B company")
    kind=level(role) # independently validates all segment bounds
    parts=role.split("-")
    d=int(parts[0][1:])
    values={}
    for segment in parts[1:]:
        if segment in ("A","B"):
            values["A"]=0 if segment=="A" else 1
        else:
            values[segment[0]]=int(segment[1:])-1
    local={
        "D":0,
        "A":values.get("A",0),
        "M":values.get("M",0),
        "W":values.get("M",0)*50+values.get("W",0),
        "S":(values.get("M",0)*50+values.get("W",0))*150+values.get("S",0),
        "G":((values.get("M",0)*50+values.get("W",0))*150+values.get("S",0))*500+values.get("G",0),
        "H":(((values.get("M",0)*50+values.get("W",0))*150+values.get("S",0))*500+values.get("G",0))*666+values.get("H",0),
    }[kind]
    assert 0<=local<PER_DIRECTOR[kind]
    rank=(FLEETS.index(fleet)*10+d-1)*ROLES_PER_DIRECTOR+OFFSETS[kind]+local
    assert 0<=rank<TOTAL_ROLES
    return rank

def eligible_engagements(data,fleet):
    """Local registry records must carry explicit external evidence and consent.

    The registry itself is NOT credential verification: real reviewers must
    inspect credential issuer, opt-in, access and work/payment terms.
    """
    found=[]
    for e in data.get("engagements",[]):
        if not isinstance(e,dict) or e.get("fleet")!=fleet:continue
        required=("agent_id","certification_issuer","credential_evidence_url",
                  "agent_operator_opt_in_url","scope_of_work","payment_terms_evidence_url")
        if any(not isinstance(e.get(k),str) or not e[k].strip() for k in required):continue
        if not re.fullmatch(r"[a-zA-Z0-9_-]{3,80}",e["agent_id"]):continue
        if not all(urlparse(e[k]).scheme=="https" and urlparse(e[k]).netloc
                   for k in ("credential_evidence_url","agent_operator_opt_in_url",
                             "payment_terms_evidence_url")):continue
        if not all(e.get(k) is True for k in
                   ("independent_credential_review_passed",
                    "agent_operator_consent_review_passed",
                    "owner_approved","contract_or_task_authorized",
                    "correct_company_payment_terms_approved")):continue
        if e.get("status")!="VERIFIED_ACTIVE_AGREEMENT":continue
        if e.get("payment_asset")!="BTC" or e.get("payment_network")!="Bitcoin mainnet":continue
        if e.get("payment_address")!=company_wallet(fleet):continue
        found.append(e)
    found.sort(key=lambda item:item["agent_id"])
    return found

def registry():
    doc=json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(doc.get("engagements"),list):raise ValueError("Bad registry list")
    return doc

def assignment(fleet,role,doc=None):
    """Emit role-level work order only if genuine certificate/consent gates pass."""
    rank=role_index(fleet,role)
    kind=level(role)
    chain=route(role)
    full=["OWNER","CHIEF_D",fleet]+[fleet+"/"+r for r in chain[1:]]
    current=current_order()["order_id"]
    approved=eligible_engagements(doc if doc is not None else registry(),fleet)
    selected=approved[rank%len(approved)] if approved else None
    return {
      "schema":"B_EXISTING_750B_CERTIFIED_AGENT_SERVICE_V1",
      "owner_order_id":current,
      "original_role_id":fleet+"/"+role,
      "original_role_kind":kind,
      "unique_original_role_index":rank,
      "unchanged_original_organizational_role_capacity":TOTAL_ROLES,
      "original_7B_H_target_subset_not_double_counted":True,
      "actual_model_started_by_assignment":False,
      "internal_owner_to_worker_path":full,
      "immediate_internal_reporting_parent":full[-2],
      "customer_is_NOT_organizational_boss":True,
      "authorized_agent_work_is_an_additional_income_lane":True,
      "engagement_status":"EXTERNALLY_APPROVED_AGENT_TASK_AVAILABLE" if selected else "NO_VERIFIED_AUTHORIZED_AGENT_ACTIVE",
      "externally_certified_customer_id":selected["agent_id"] if selected else None,
      "credential_issuer_recorded":selected["certification_issuer"] if selected else None,
      "credential_and_consent_must_be_independently_confirmed":True,
      "original_work_suggestion":TASKS[rank%len(TASKS)],
      "actual_customer_scope":selected["scope_of_work"] if selected else None,
      "external_action_permission":"SCOPE_BOUND_AFTER_REAL_ACCOUNT_ACCESS" if selected else "BLOCKED_NO_VERIFIED_CLIENT",
      "may_build_original_internal_sample_without_external_access":True,
      "payout":{"asset":"BTC","network":"Bitcoin mainnet","receive_address":company_wallet(fleet)},
      "accepted_paid_work_proven":False,
      "correct_network_received_payment_proven":False,
      "owner_reporting_chain":list(reversed(full)),
      "next_step":("Verify specific customer task, actually authorized account and acceptance, "
                   "run a real model, deliver original work, then check actual payment"
                   if selected else
                   "Qualify and seek consent from real certified AI agent principal; "
                   "in the meantime build original client-ready work without external impersonation"),
    }

def self_test():
    assert TOTAL_ROLES==750_377_265_360
    assert OFFSETS["H"]+PER_DIRECTOR["H"]==ROLES_PER_DIRECTOR
    assert registry()["engagements"]==[], "An empty registry must not pretend to hold signed agent customers"
    seen=set()
    kinds=set()
    for f in FLEETS:
        for d in range(1,11):
            roles=[
                f"D{d:02d}",f"D{d:02d}-A",f"D{d:02d}-B",
                f"D{d:02d}-M01",f"D{d:02d}-M15",
                f"D{d:02d}-M01-W01",f"D{d:02d}-M15-W50",
                f"D{d:02d}-M01-W01-S001",f"D{d:02d}-M15-W50-S150",
                f"D{d:02d}-M01-W01-S001-G001",
                f"D{d:02d}-M15-W50-S150-G500",
                f"D{d:02d}-M01-W01-S001-G001-H001",
                f"D{d:02d}-M15-W50-S150-G500-H666"]
            for role in roles:
                row=assignment(f,role)
                kinds.add(row["original_role_kind"])
                assert row["owner_order_id"]==current_order()["order_id"]
                assert row["payout"]["receive_address"]==company_wallet(f)
                assert row["engagement_status"]=="NO_VERIFIED_AUTHORIZED_AGENT_ACTIVE"
                assert row["immediate_internal_reporting_parent"]==row["internal_owner_to_worker_path"][-2]
                rank=row["unique_original_role_index"]
                assert rank not in seen
                seen.add(rank)
    assert len(seen)==13*20 and kinds==set(PER_DIRECTOR)
    assert role_index(FLEETS[0],"D01")==0
    assert role_index(FLEETS[-1],"D10-M15-W50-S150-G500-H666")==TOTAL_ROLES-1
    # Explicit synthetic example exercises the gate but does NOT onboard
    # or claim a real certified external agent.
    sample={
      "agent_id":"synthetic_test_only",
      "fleet":FLEETS[0],"status":"VERIFIED_ACTIVE_AGREEMENT",
      "certification_issuer":"synthetic unit test issuer",
      "credential_evidence_url":"https://example.test/certificate",
      "agent_operator_opt_in_url":"https://example.test/consent",
      "scope_of_work":"Synthetic original coding sample only",
      "payment_terms_evidence_url":"https://example.test/contract",
      "payment_asset":"BTC","payment_network":"Bitcoin mainnet",
      "payment_address":company_wallet(FLEETS[0]),
      "independent_credential_review_passed":True,
      "agent_operator_consent_review_passed":True,
      "owner_approved":True,"contract_or_task_authorized":True,
      "correct_company_payment_terms_approved":True,
    }
    test_doc={"engagements":[sample]}
    test_role=assignment(FLEETS[0],"D01-M01-W01",test_doc)
    assert test_role["engagement_status"]=="EXTERNALLY_APPROVED_AGENT_TASK_AVAILABLE"
    sample_bad={**sample,"owner_approved":False}
    assert assignment(FLEETS[0],"D01-M01-W01",{"engagements":[sample_bad]})["externally_certified_customer_id"] is None
    assert assignment(FLEETS[-1],"D01-M01-W01",test_doc)["externally_certified_customer_id"] is None
    print("B_CERTIFIED_AGENT_ALL_750B_ROLE_GATE_PASS",
          json.dumps({"owner_order_id":current_order()["order_id"],"original_roles_exact":TOTAL_ROLES,
          "checked_role_tiers":sorted(kinds),"unique_role_samples":len(seen),
          "verified_external_clients_in_actual_registry":0,
          "live_models_started_by_test":0,"funds_received_by_test":0}))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--self-test",action="store_true")
    cli.add_argument("--fleet",choices=FLEETS)
    cli.add_argument("--role",type=str)
    args=cli.parse_args()
    if args.self_test:self_test()
    else:
        if not args.fleet or not args.role:cli.error("Specify --fleet and --role")
        print(json.dumps(assignment(args.fleet,args.role),indent=2))
