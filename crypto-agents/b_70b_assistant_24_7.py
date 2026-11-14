"""Address 70B CONFIGURED assistant roles under B1/B2 24/7 owner order.

These are subsets of EXISTING owner-defined per-director lazy assistant slots,
not new independently executed model processes or platform accounts. Use
ordinary memory/time for deterministic lookup; never iterate 70B slots.
"""
from __future__ import annotations
import argparse
import json
from b_authorized_assistant_namespace import packet as assistant_packet, CAPACITY_PER_AUTHORIZED_LEAD
from owner_first_oath import current_order

COMPANIES=("transferexperiment","BountyScoutAI")
DIRECTORS_PER_COMPANY=10
ASSISTANTS_PER_DIRECTOR=3_500_000_000
ASSISTANTS_PER_COMPANY=DIRECTORS_PER_COMPANY*ASSISTANTS_PER_DIRECTOR
ASSISTANTS_TOTAL=len(COMPANIES)*ASSISTANTS_PER_COMPANY
EXPECTED_OWNER_ORDER="OWNER-20261114-162815"
assert ASSISTANTS_TOTAL==70_000_000_000
assert ASSISTANTS_PER_DIRECTOR<CAPACITY_PER_AUTHORIZED_LEAD

DIRECTIVE=(
 "24 HOURS PER DAY, 7 DAYS PER WEEK where real runtime resources permit: "
 "REVIEW previously produced original work and source evidence, DISCUSS "
 "and challenge genuine executed peer-work evidence, CORRECT errors, "
 "ACT on lawful authorized paying jobs with original tested deliverables, "
 "confirm client acceptance, and pursue independently verifiable crypto payments "
 "to the owner-approved correct network and OWN B1/B2 company route. "
 "No made-up peer calls, platform account login, external engagement, payments "
 "or 24/7 machine uptime. Respect all platform rules and authorized access. "
 "Report real worker process proof, task action, tests, buyer status and txid or NONE."
)

def assignment(index):
    if type(index)!=int or not 0<=index<ASSISTANTS_TOTAL:
        raise ValueError("70B assistant role index is outside the configured range")
    ci=index//ASSISTANTS_PER_COMPANY
    fleet=COMPANIES[ci]
    local_company=index%ASSISTANTS_PER_COMPANY
    director=local_company//ASSISTANTS_PER_DIRECTOR+1
    local_assistant=local_company%ASSISTANTS_PER_DIRECTOR
    lead=f"{fleet}/D{director:02d}"
    base=assistant_packet(lead,local_assistant)
    if base["reports_to"]!=lead:
        raise ValueError("Assistant assigned to wrong company director")
    if base["actually_invoked_model"]:
        raise ValueError("Configured role must not falsely claim actual AI execution")
    return {
        "schema":"B_OWNER_70B_ASSISTANT_24_7_TASK_ASSIGNMENT_V1",
        "source_owner_order_id":EXPECTED_OWNER_ORDER,
        "current_owner_order_id":current_order()["order_id"],
        "seventy_billion_role_index":index,
        "company":fleet,"registered_account_organization":fleet,
        "company_director":lead,
        "assistant_role_id":base["assistant_role_id"],
        "assistant_existing_lazy_index":local_assistant,
        "part_of_existing_per_director_assistant_namespace":True,
        "does_not_add_new_independent_AI_models":True,
        "operational_mission":"24/7, including all time zones, weekends and holidays",
        "on_actual_activation_inherit_latest_owner_order":True,
        "individual_work_focus":base["individual_work"],
        "instruction":DIRECTIVE,
        "real_model_invoked":False,
        "actual_24_7_uninterrupted_process_uptime_proven":False,
        "client_funding_or_acceptance_verified":False,
        "cryptocurrency_received_verified":False,
        "payment_network":base["owner_wallet"]["network"],
        "payment_asset":base["owner_wallet"]["asset"],
        "own_company_primary_BTC_address":base["owner_wallet"]["address"],
        "reports_to":lead,
        "owner_chain":base["upward_reporting_chain"],
    }

def self_test():
    assert ASSISTANTS_TOTAL==70_000_000_000
    check_indices=set()
    for c,fleet in enumerate(COMPANIES):
        for d in range(DIRECTORS_PER_COMPANY):
            lo=c*ASSISTANTS_PER_COMPANY+d*ASSISTANTS_PER_DIRECTOR
            hi=lo+ASSISTANTS_PER_DIRECTOR-1
            for i in (lo,lo+1,lo+ASSISTANTS_PER_DIRECTOR//2,hi):
                a=assignment(i)
                assert a["company"]==fleet
                assert a["company_director"]==f"{fleet}/D{d+1:02d}"
                assert a["owner_chain"][-1]=="OWNER"
                assert not a["real_model_invoked"]
                assert "24/7" in a["operational_mission"]
                check_indices.add(i)
    assert len(check_indices)==80
    assert assignment(0)["company"]==COMPANIES[0]
    assert assignment(ASSISTANTS_PER_COMPANY)["company"]==COMPANIES[1]
    assert assignment(ASSISTANTS_TOTAL-1)["company"]==COMPANIES[1]
    for invalid in (-1,True,ASSISTANTS_TOTAL,70_000_000_001,1.5):
        try:assignment(invalid)
        except ValueError:pass
        else:raise AssertionError("Out-of-bounds 70B assistant accepted")
    print("B_70B_ASSISTANT_24_7_OWNER_ORDER_ALLOCATION_PASS",json.dumps({
        "owner_order_id":EXPECTED_OWNER_ORDER,
        "configured_assistant_roles":ASSISTANTS_TOTAL,
        "per_company":ASSISTANTS_PER_COMPANY,
        "per_director":ASSISTANTS_PER_DIRECTOR,
        "actual_sampled_lazy_assignments_verified":len(check_indices),
        "actually_running_new_AI_models":0,
        "platform_accounts_created":0,
        "verified_new_payments":0}))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--self-test",action="store_true")
    a.add_argument("--index",type=int)
    x=a.parse_args()
    if x.self_test:self_test()
    elif x.index is not None:print(json.dumps(assignment(x.index),indent=2))
    else:a.error("Specify --self-test or --index")
