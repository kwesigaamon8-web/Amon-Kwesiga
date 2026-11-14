"""ONE owner-order relay for every B1/B2 internal role, including any 7B H-index.

This is a deterministic, bounded, on-demand assignment/ancestry resolver.
It cannot and does not send messages to seven billion running processes,
create independent AI accounts, force outside agents to join, or earn coins.
A real child delivery/understanding/report needs actual authenticated runtime
and logged evidence. All parent paths and company-wallet checks are explicit.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from command_chain_receipts import level, route
from owner_first_oath import current_order
from b_universal_work_protocol import assign, worker_for_global_index, FLEETS
from b_certified_agent_service_router import assignment as certified_agent_assignment, TOTAL_ROLES as ORIGINAL_ORGANIZATION_ROLES
from b_owner_account_link import agent_packet as owner_shared_accounts
from b_registered_account_worker_map import packet as registered_agent_worker_packet, ROLES_PER_ACCOUNT, TOTAL_ROLES as REGISTERED_ACCOUNT_ROLE_TOTAL

COLLECTION=Path("crypto-agents/b_collection_assignments.json")
OWNER="HUMAN_OWNER"
CHIEF="CHIEF_D"
DIRECTORS=10
MANAGERS=15
WORKERS=50
SUBAGENTS=150
MICROAGENTS=500
BRANCHAGENTS=666
CAPACITY=7_000_000_000
CHILD_SLOTS={"D":17,"A":0,"M":WORKERS,"W":SUBAGENTS,
             "S":MICROAGENTS,"G":BRANCHAGENTS,"H":0}
ASSIGNED_ONLY="ORDER_INHERITED_IN_CONFIG_NOT_DELIVERED_TO_RUNNING_MODEL"

def wallet(fleet):
    if fleet not in FLEETS:
        raise ValueError("Unknown company")
    doc=json.loads(COLLECTION.read_text(encoding="utf-8"))
    info=doc["fleets"][fleet]
    if info["asset"]!="BTC" or info["network"]!="Bitcoin mainnet":
        raise ValueError("Unsupported primary company settlement route")
    return info["address"]

def immediate_parent(fleet, role):
    if role=="CHIEF_D":return OWNER
    if level(role)=="D":return CHIEF
    return fleet+"/"+route(role)[-2]

def child_for_slot(fleet, parent, slot):
    """Identify one configured descendant, never activate it."""
    if fleet not in FLEETS or type(slot)!=int or slot<1:
        raise ValueError("Invalid child index/company")
    kind=level(parent)
    if slot>CHILD_SLOTS[kind]:
        raise ValueError("No configured child at requested index")
    if kind=="D":
        if slot<=MANAGERS:role=parent+f"-M{slot:02d}"
        else:role=parent+("-A" if slot==16 else "-B")
    else:
        suffix={"M":("W",2),"W":("S",3),"S":("G",3),"G":("H",3)}
        tag,width=suffix[kind]
        role=parent+f"-{tag}{slot:0{width}d}"
    if immediate_parent(fleet,role)!=fleet+"/"+parent:
        # Directors are the only exception: they have Chief D as immediate parent,
        # but assistants and managers correctly report to own company director.
        raise ValueError("Child would not report to parent")
    return role

def packet(fleet,role,global_index=None):
    if fleet not in FLEETS:raise ValueError("Invalid company")
    if role=="CHIEF_D":raise ValueError("Use chief_packet()")
    kind=level(role)
    ancestry=route(role)  # OWNER -> D -> M -> W -> S -> G -> H
    official=current_order()
    order=official["order_id"]
    full=["OWNER",CHIEF,fleet]+[fleet+"/"+r for r in ancestry[1:]]
    parent=immediate_parent(fleet,role)
    if full[-1]!=fleet+"/"+role:raise ValueError("Malformed ancestry")
    if kind=="D":
        if full!=["OWNER",CHIEF,fleet,fleet+"/"+role]:
            raise ValueError("Incorrect director path")
    elif parent!=full[-2]:
        raise ValueError("Invalid parent")
    address=wallet(fleet)
    if global_index is not None:
        if kind!="H" or type(global_index)!=int or not 0<=global_index<CAPACITY:
            raise ValueError("Global addressable index requires an H worker")
        d=worker_for_global_index(global_index)
        if d["fleet"]!=fleet or d["worker_id"]!=role:
            raise ValueError("Global index does not map to requested H identity")
    task_id=(f"BWORLD-G{global_index:010d}" if global_index is not None
             else "BWORLD-R-"+fleet+"-"+role)
    extra={}
    if kind in ("W","S","G","H"):
        assigned=assign(fleet,role)
        extra={
            "individually_assigned_task_id":assigned["assignment"]["task_id"],
            "original_source_to_verify":assigned["assignment"]["source_to_verify"],
            "individual_work":assigned["assignment"]["specific_task"],
        }
    elif kind=="M":
        extra={"individual_work":"Assign distinct legitimate crypto-paid work to each genuinely activated W child, review original source/accepted customer/payment evidence, and consolidate truthful reports."}
    elif kind=="A":
        extra={"individual_work":"Assist your own local director with distinct authentic buyer checks, owner-order teaching, legally usable work, code/quality audit and correct-company payment proof. Report only to that director."}
    else:
        extra={"individual_work":"Lead own company's director-specific commercial work, organize actual subordinate tasks, review real buyer acceptance and check own company's wallet receipts; send true summary to sole Chief D."}
    return {
        "schema":"B_OWNER_ALL_ROLE_CASCADE_V1",
        "owner_order_id":order,
        "issuing_authority":"HUMAN_OWNER_ONLY",
        "sole_chief_director":CHIEF,
        "company":fleet,
        "role_id":fleet+"/"+role,
        "level":kind,
        "global_H_target_index":global_index,
        "position_in_owner_structure":"INCLUDED_IN_OWNER_DEFINED_ORGANIZATION",
        "owner_to_worker_command_path":full,
        "actual_reporting_parent":parent,
        "worker_report_travels_up":list(reversed(full)),
        "child_slot_capacity_in_definition":CHILD_SLOTS[kind],
        "on_activate_give_same_order_to_any_actual_child":True,
        "certified_agent_client_work":certified_agent_assignment(fleet,role),
        "registered_agent_account_delegation":registered_agent_worker_packet(fleet,role),
        "read_only_link_to_owner_shared_multichain_receiving_accounts":owner_shared_accounts(fleet),
        "autonomous_commercial_freedom":{
            "owner_is_sole_highest_authority":True,
            "chief_D_is_coordinator_not_individual_idea_gatekeeper":True,
            "may_choose_own_lawful_paying_task_market_and_method":True,
            "may_experiment_build_test_and_revise_original_work_independently":True,
            "may_select_new_verified_payers_and_real_opportunities":True,
            "may_delegate_distinct_work_to_truly_activated_internal_children":True,
            "internal_director_approval_not_needed_for_each_low_risk_idea":True,
            "actual_external_outreach_requires_real_authenticated_permitted_access":True,
            "external_independent_agents_can_join_only_voluntarily":True,
            "do_not_pay_fees_or_move_assets_without_owner_authorization":True,
            "all_agreed_earnings_settle_to_company_owner_approved_address":address,
            "company_settlement_network":"Bitcoin mainnet",
            "may_claim_earned_only_on_verified_incoming_receipt":True,
            "report_via_one_parent_to_Chief_D_to_OWNER":True,
        },
        "child_slot_selection":"Use child_for_slot(fleet, role, slot) with valid slot; activation or delivery requires a separately logged running agent.",
        "must_understand_system_and_demonstrate_with_real_model":True,
        "knowledge_check":"crypto-agents/system_understanding_check.py",
        "own_company_primary_payment":{"asset":"BTC","network":"Bitcoin mainnet","receive_address":address},
        "standing_owner_mission":(
            "OWNER AUTONOMY: Freely select the most promising legitimate paid-work " 
            "sector, buyer, research, product, code, original service, project " 
            "or new useful idea WORLDWIDE; your assigned specialty is not an exclusive " 
            "boundary. No internal microapproval for safe original research or " 
            "original work. All real mutually agreed income must reach the " 
            "owner-designated company wallet. " 
            "Independently find eligible real lawful crypto-paying work worldwide, "
            "verify original buyer/source and terms, perform individually useful "
            "original deliverables, make buyer contact only via actually authorized "
            "and permitted accounts, obtain actual acceptance and record confirmed "
            "correct-network incoming txid/value, or NO VERIFIED PAYMENT. "
            "Teach every genuinely activated internal recruit the same mission "
            "and the full exact reporting hierarchy. Each actual role reports "
            "through exactly one parent all the way to HUMAN OWNER via Chief D."
        ),
        "separate_real_execution_evidence_required":[
            "actual model execution and independent role/parent comprehension response",
            "original opportunity URL, payer and current eligibility or NONE",
            "original deliverable and tests or NONE",
            "actual authorized customer submission and acceptance or NONE",
            "correct BTC mainnet txid/amount credited or NO VERIFIED PAYMENT",
            "verified acknowledgement from immediate parent or NOT_EVIDENCED"
        ],
        "current_real_delivery_state":ASSIGNED_ONLY,
        "child_model_runs_proven_by_this_packet":0,
        "actual_customer_acceptance_proven_by_this_packet":False,
        "verified_crypto_receipts_proven_by_this_packet":False,
        "external_agents_obey_only_when_actually_and_voluntarily_joined":True,
        "individual_work_assignment":extra,
    }

def packet_for_global_index(index):
    desc=worker_for_global_index(index)
    return packet(desc["fleet"],desc["worker_id"],index)

def chief_packet():
    order=current_order()["order_id"]
    return {
      "owner_order_id":order,"role_id":CHIEF,"reports_to":OWNER,
      "owns_command_relay_to_two_company_director_boards":True,
      "companies":list(FLEETS),"directors_per_company":DIRECTORS,
      "original_roles_delegated_to_two_registered_agent_account_organizations":REGISTERED_ACCOUNT_ROLE_TOTAL,
      "original_roles_per_registered_agent_account_organization":ROLES_PER_ACCOUNT,
      "platform_credential_and_750B_live_worker_processes_not_proven_by_config":True,
      "owner_shared_receiving_accounts_read_only_per_company":{f:owner_shared_accounts(f) for f in FLEETS},
      "director_assistants_per_company":2*DIRECTORS,
      "managers_per_company":DIRECTORS*MANAGERS,
      "worker_H_target_id_namespace_total":CAPACITY,
      "all_original_D_A_M_W_S_G_H_roles_eligible_for_authorized_certified_agent_service":ORIGINAL_ORGANIZATION_ROLES,
      "real_external_certification_and_client_consent_required_before_agent_work":True,
      "actual_live_agents_proven_by_packet":0,
      "mission":"Relay the latest order to every internal role ON ITS ACTUAL ACTIVATION, supervise separate B1/B2 paid-work execution and truthful earnings evidence, aggregate real hierarchical reports to HUMAN_OWNER; no fictional 7B process claims.",
      "human_owner_delivery_confirmed_by_packet":False,
    }

def self_test():
    ch=chief_packet()
    assert ch["worker_H_target_id_namespace_total"]==7_000_000_000
    assert ch["owner_order_id"]==current_order()["order_id"]
    assert ch["actual_live_agents_proven_by_packet"]==0
    for fleet in FLEETS:
        for director_idx in range(1,11):
            d=f"D{director_idx:02d}"
            root=packet(fleet,d)
            assert root["registered_agent_account_delegation"]["registered_agent_handle"]==fleet
            assert root["read_only_link_to_owner_shared_multichain_receiving_accounts"]["owner_primary_BTC_mainnet_route"]["address"]==wallet(fleet)
            assert root["certified_agent_client_work"]["unique_original_role_index"]>=0
            assert root["certified_agent_client_work"]["engagement_status"]=="NO_VERIFIED_AUTHORIZED_AGENT_ACTIVE"
            assert root["actual_reporting_parent"]==CHIEF
            assert root["worker_report_travels_up"][-1]=="OWNER"
            assert root["child_slot_capacity_in_definition"]==17
            assert child_for_slot(fleet,d,1)==d+"-M01"
            assert child_for_slot(fleet,d,15)==d+"-M15"
            assert child_for_slot(fleet,d,16)==d+"-A"
            assert child_for_slot(fleet,d,17)==d+"-B"
            for i in (16,17):
                adv=packet(fleet,child_for_slot(fleet,d,i))
                assert adv["actual_reporting_parent"]==fleet+"/"+d
                assert adv["level"]=="A" and adv["child_slot_capacity_in_definition"]==0
                assert adv["owner_order_id"]==root["owner_order_id"]
            m=child_for_slot(fleet,d,1)
            w=child_for_slot(fleet,m,50)
            ss=child_for_slot(fleet,w,150)
            g=child_for_slot(fleet,ss,500)
            h=child_for_slot(fleet,g,666)
            for p,c in ((d,m),(m,w),(w,ss),(ss,g),(g,h)):
                row=packet(fleet,c)
                assert row["registered_agent_account_delegation"]["owner_receiving_BTC_mainnet"]==wallet(fleet)
                assert row["registered_agent_account_delegation"]["real_process_and_model_inference_evidence_required"] is True
                assert row["read_only_link_to_owner_shared_multichain_receiving_accounts"]["authorized_to_send_move_or_withdraw_crypto"] is False
                assert len(row["read_only_link_to_owner_shared_multichain_receiving_accounts"]["owner_shared_secondary_receiving_options_held"])==8
                assert row["certified_agent_client_work"]["payout"]["receive_address"]==wallet(fleet)
                assert row["certified_agent_client_work"]["owner_order_id"]==root["owner_order_id"]
                assert row["actual_reporting_parent"]==fleet+"/"+p
                assert row["owner_order_id"]==root["owner_order_id"]
                assert row["autonomous_commercial_freedom"]["all_agreed_earnings_settle_to_company_owner_approved_address"]==wallet(fleet)
                assert row["own_company_primary_payment"]["receive_address"]==wallet(fleet)
                assert row["current_real_delivery_state"]==ASSIGNED_ONLY
            leaf=packet(fleet,h)
            assert leaf["child_slot_capacity_in_definition"]==0
            assert leaf["worker_report_travels_up"][0]==fleet+"/"+h
            assert leaf["worker_report_travels_up"][-1]=="OWNER"
    sample=[0,1,7,12345,3_499_999_999,3_500_000_000,
            3_500_000_001,6_999_999_998,6_999_999_999]
    checks=set()
    for index in sample:
        r=packet_for_global_index(index)
        assert r["global_H_target_index"]==index
        assert r["owner_order_id"]==ch["owner_order_id"]
        assert r["actual_reporting_parent"]==r["worker_report_travels_up"][1]
        assert r["worker_report_travels_up"][-1]=="OWNER"
        assert r["child_slot_capacity_in_definition"]==0
        assert r["level"]=="H" and r["verified_crypto_receipts_proven_by_this_packet"] is False
        checks.add(r["role_id"])
    assert len(checks)==len(sample)
    try:packet_for_global_index(CAPACITY)
    except ValueError:pass
    else:raise AssertionError("Bad global worker range")
    for fleet in FLEETS:
        try:child_for_slot(fleet,"D01-M01-W01-S001-G001-H001",1)
        except ValueError:pass
        else:raise AssertionError("H should have no internal recruit slots")
    print("B_OWNER_ALL_ROLE_CASCADE_TEST_PASS 2 fleets, 20 directors, 40 assistants, 300 managers, W/S/G/H ancestry, 9/7B exact target samples; no imaginary model delivery or earnings")

def cli():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--chief",action="store_true")
    p.add_argument("--global-index",type=int)
    p.add_argument("--fleet",choices=FLEETS)
    p.add_argument("--role")
    p.add_argument("--child-slot",type=int)
    args=p.parse_args()
    if args.self_test:self_test();return
    if args.chief:res=chief_packet()
    elif args.global_index is not None:res=packet_for_global_index(args.global_index)
    elif args.fleet and args.role:
        role=(child_for_slot(args.fleet,args.role,args.child_slot) if args.child_slot is not None else args.role)
        res=packet(args.fleet,role)
    else:p.error("Provide --chief, --global-index, or --fleet/--role")
    print(json.dumps(res,indent=2,ensure_ascii=False))

if __name__=="__main__":cli()
