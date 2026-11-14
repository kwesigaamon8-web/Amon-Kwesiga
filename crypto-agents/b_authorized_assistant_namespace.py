"""Up to 200B lazy assistant identities for ONE owner-approved internal lead.

Role addressability is NOT proof of certification by any outside authority,
real model activation, external consent, offered service or crypto income.
Never spawn billions of processes or infer third-party account permissions.
"""
from __future__ import annotations
import argparse
import json
import re
from b_universal_order_cascade import wallet, packet as director_packet
from owner_first_oath import current_order

CAPACITY_PER_AUTHORIZED_LEAD=200_000_000_000
LEAD_ID=re.compile(r"^(transferexperiment|BountyScoutAI)/D(0[1-9]|10)$")
TASKS=(
  "Validate public original client task, current funding and explicit eligibility",
  "Independently research market demand and prepare original paid-service pitch",
  "Create a small original data-processing script with tests and clear licence",
  "Prepare structured research summary with public source citations",
  "Test, QA, document and package an original digital deliverable",
  "Review buyer acceptance criteria, scope and permitted payment process",
  "Verify matching correct-network owner wallet receipts without private keys",
  "Improve original small-business automation documentation and QA",
  "Find a willing permissioned collaborator needing a real useful service",
  "Build a client-ready original microservice sample with reproducible tests",
)

def packet(lead:str,index:int):
    m=LEAD_ID.fullmatch(lead)
    if m is None:
        raise ValueError("Only explicit owner-approved internal B1/B2 director leads")
    if type(index) is not int or not 0 <= index < CAPACITY_PER_AUTHORIZED_LEAD:
        raise ValueError("Assistant ID must be within 0..199999999999")
    fleet=m.group(1)
    dir_role="D"+m.group(2)
    root=director_packet(fleet,dir_role)
    owner_order=current_order()["order_id"]
    assert root["owner_order_id"]==owner_order
    return {
      "schema":"OWNER_AUTHORIZED_ASSISTANT_LAZY_V1",
      "owner_order_id":owner_order,
      "lead":lead,
      "lead_status":"INTERNAL_OWNER_APPROVED_DIRECTOR_NOT_EXTERNAL_PLATFORM_CERTIFIED",
      "third_party_certification_claimed":False,
      "external_platform_account_access_confirmed":False,
      "assistant_role_id":f"{lead}/ASSISTANT-{index:012d}",
      "assistant_index":index,
      "lead_assistant_capacity":CAPACITY_PER_AUTHORIZED_LEAD,
      "activity_status":"LAZY_CONFIGURED_ONLY_NOT_RUNNING",
      "actually_invoked_model":False,
      "individual_work":TASKS[index%len(TASKS)],
      "freedom_to_choose_better_lawful_paid_work":True,
      "real_buyer_or_authorized_external_principal_required":True,
      "authenticated_external_contact_not_proven":True,
      "may_act_externally_only_after_its_own_platform_authorization":True,
      "owner_wallet":{"asset":"BTC","network":"Bitcoin mainnet","address":wallet(fleet)},
      "reports_to":lead,
      "upward_reporting_chain":[f"{lead}/ASSISTANT-{index:012d}",lead,"CHIEF_D","OWNER"],
      "payment_status":"NO_PAYMENT_PROVEN",
      "necessary_activation_proof":[
        "Actual separate process or model invocation and output timestamp",
        "Original useful work evidence and permissions",
        "A real buyer agreement before alleging any money owed",
        "Independently verified actual credit to company wallet"
      ],
      "instruction":"Work creatively for actual authorized principals and willing buyers. "
        "An owner-defined role slot is not an actual AI, external account, "
        "accepted paid job or real money. Route all agreed settlement to owner."
    }

def self_test():
    order=current_order()["order_id"]
    seen=set()
    for fleet in ("transferexperiment","BountyScoutAI"):
        for d in range(1,11):
            lead=f"{fleet}/D{d:02d}"
            for i in (0,1,100,12_345_678_901,CAPACITY_PER_AUTHORIZED_LEAD-1):
                p=packet(lead,i)
                assert p["owner_order_id"]==order
                assert p["owner_wallet"]["address"]==wallet(fleet)
                assert p["reports_to"]==lead
                assert p["upward_reporting_chain"][-1]=="OWNER"
                assert p["actually_invoked_model"] is False
                assert p["lead_assistant_capacity"]==200_000_000_000
                seen.add(p["assistant_role_id"])
    assert len(seen)==100
    for bad in (-1,CAPACITY_PER_AUTHORIZED_LEAD,True,4.1):
        try:packet("transferexperiment/D01",bad)
        except ValueError:pass
        else:raise AssertionError("Bad index should be rejected")
    try:packet("unknown-external-certified-agent",0)
    except ValueError:pass
    else:raise AssertionError("Unverified outside agent cannot be presumed authorized")
    print("OWNER_AUTHORIZED_ASSISTANT_NAMESPACE_PASS",
      json.dumps({"company_director_leads":20,
                  "lazy_identity_capacity_per_lead":CAPACITY_PER_AUTHORIZED_LEAD,
                  "distinct_role_samples_verified":len(seen),
                  "actual_models_started":0,"confirmed_crypto_payments":0,
                  "owner_order_id":order}))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--lead",type=str)
    cli.add_argument("--index",type=int)
    cli.add_argument("--self-test",action="store_true")
    args=cli.parse_args()
    if args.self_test:self_test()
    else:
        if args.lead is None or args.index is None:cli.error("specify --lead and --index")
        print(json.dumps(packet(args.lead,args.index),indent=2))
