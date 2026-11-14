"""Chief D global revenue management: 20 company-specific director plans + 7B lazy worker packets.

This is an executable task-routing program, NOT billions of hosted AI models,
nor a sale, account login, permission grant, approved offer or received coin.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path

from b_universal_work_protocol import assign_global_index, MARKETS, FLEETS
from owner_first_oath import current_order

# The owner has two company boards, each with 10 local directors.
# Distinct director responsibilities; one actual prospective lead belongs to
# exactly ONE director so no fleet mass-spams the same customer.
DIRECTOR_LANES=(
 ("D01","Find original customer demand", "Sourced unexpired customer task and genuine payee identity"),
 ("D02","Validate ability and funding", "Payer and source legitimacy, eligibility, no advance fee"),
 ("D03","Price and propose", "Original scope and estimated quote for approved buyer"),
 ("D04","Build paid-work artifact", "Testable original customer-specific deliverable"),
 ("D05","Independent QA", "Executable tests with failure and success evidence"),
 ("D06","Package and explain", "Client-readable sample, README and clear limitations"),
 ("D07","Permissioned customer contact", "One authorised tailored offer with host-confirmed sending record"),
 ("D08","Acceptance and revisions", "Genuine buyer response, revisions and acceptance evidence"),
 ("D09","Source/code and fraud audit", "Licence, uniqueness, duplicate and risk flags"),
 ("D10","Payments and settlement", "Accepted fee and independently verifiable receiving transaction"),
)
GLOBAL_ORIGINAL_BUYER_LEADS=(
 {"lead_id":"OT-JSON-CSV-50","source":"https://opentask.ai/tasks/cmpupoqmm0027kw04351wcfhz",
  "client":"Skill Exec Agent", "service":"Python JSON-to-CSV converter",
  "advertised_budget":"50 USDC","stage":"PUBLIC_LISTING_ONLY",
  "platform_offer_requires_signin":True,
  "connected_platform_offer_account_verified":False,
  "accepted_contract":False,"funding_guaranteed":False,"crypto_received_verified":False,
  "original_work_artifact":"crypto-agents/commercial-work/opentask-json-csv/json_to_csv.py",
  "original_test_artifact":"crypto-agents/commercial-work/opentask-json-csv/tests/test_json_to_csv.py",
  "owner_of_lead":"transferexperiment/D04",
  "next_gate":"An authenticated account must make a tailored offer, customer must accept hiring terms, then submit work and verify actual USDC settlement."
 },
)
PENDING_VERIFICATION="NOT_EVIDENCED"

def director_board():
    order=current_order()["order_id"]
    entries=[]
    for fleet in FLEETS:
        for i,(d,lane,proof) in enumerate(DIRECTOR_LANES):
            # World coverage spans all continents, but chosen city is a
            # research target only, NOT a paying customer.
            choice=(i+(0 if fleet==FLEETS[0] else 19))%len(MARKETS)
            iso,city,locale,continent=MARKETS[choice]
            entries.append({
             "director":fleet+"/"+d,"reports_to":"CHIEF_D",
             "human_owner_order_id":order,"mission_limited_to_owner_order":True,
             "responsibility":lane,"target_evidence":proof,
             "market_hypothesis":{"city":city,"country_code":iso,"region":continent,"locale":locale},
             "actual_customer_known_in_this_market":False,
             "director_belongs_to_owner_internal_structure":True,
             "director_accountability":"Own fleet 10-director local board -> sole Chief D -> human OWNER",
             "two_director_assistants":[
                {"id":fleet+"/"+d+"-A","parent":fleet+"/"+d,
                 "internal_owner_defined_role":True,
                 "scope":"Independently verify buyer legitimacy and original sources, review one distinct genuine crypto-paying lead, report proof to director",
                 "actual_model_acknowledgement":"NOT_EVIDENCED"},
                {"id":fleet+"/"+d+"-B","parent":fleet+"/"+d,
                 "internal_owner_defined_role":True,
                 "scope":"Independently check owner order, worker training, consent, company-specific wallet and verified receipt evidence; report to director",
                 "actual_model_acknowledgement":"NOT_EVIDENCED"}
             ],
             "all_fifteen_manager_roles_in_owner_scope":[fleet+"/"+d+f"-M{m:02d}" for m in range(1,16)],
             "all_w_s_g_h_descendants_in_owner_scope_on_activation":True,
             "no_pretense_that_all_assistants_or_managers_ran_a_model":True,
             "manager_count_defined":15,"manager_model_acknowledgements_verified":False,
             "recruitment_cascade":{
                "owner_order_id":order,
                "director_relay_to_15_managers_and_two_assistants_on_activation":True,
                "manager_to_workers_and_worker_to_S_to_G_to_H":True,
                "actual_subordinate_activations_not_proven_by_this_plan":True,
                "external_agent_recruiting_requires_consent_and_authorized_account":True,
                "mission":"Give each truly activated recruit an individual original lawful crypto-paying work task, its correct company wallet, and a requirement to pass the same mission to its own future actual recruits.",
             },
             "understanding_assessment_on_actual_child_model_execution":True,
             "only_human_owner_receives_Chief_D_consolidation":True,
             "upward_reporting_path":[fleet+"/"+d,"CHIEF_D","HUMAN_OWNER"],
             "knowledge_check_script":"crypto-agents/system_understanding_check.py",
             "model_understanding_verified_from_director_plan":False,
             "active_worker_proof_required":True,"payment_received_verified":False,
             "real_lead_claims":[l["lead_id"] for l in GLOBAL_ORIGINAL_BUYER_LEADS if l["owner_of_lead"]==fleet+"/"+d]
            })
    return {"owner_order_id":order,"chief_director":"CHIEF_D",
        "internal_company_roles_under_human_owner":True,
        "all_directors_assistants_managers_W_S_G_H_are_included":True,
        "defined_director_assistants_both_fleets":40,
        "defined_company_local_directors_both_fleets":20,
        "defined_manager_roles_both_fleets":300,
        "actual_assistant_or_manager_model_execution_proven_by_board":0,
        "separate_company_director_boards":20,
        "director_assignments":entries,
        "source_verified_commercial_leads_not_yet_hired":list(GLOBAL_ORIGINAL_BUYER_LEADS),
        "actual_human_owner_directive":"Worldwide legitimate opportunities => original work => authenticated offer => buyer acceptance => correct-network verified income.",
        "unique_lead_claim_rule":"One owner per prospect. Directors coordinate, do not send bulk or repeated offers.",
        "actual_connected_opentask_account_confirmed":False,
        "active_billions_claim":False,
        "latest_owner_directive":order,
        "urgent_commercial_sprint":{"duration_minutes_per_activated_worker":30,
            "scope":"Source-backed paying customer -> original useful work -> authorized submission -> accepted customer -> verified actual crypto receipt",
            "applies_to_all_addressable_H_targets_on_activation":True,
            "all_7B_currently_running":False,"report_one_fleet_at_a_time":True},
        "total_addressable_H_worker_identities":7_000_000_000,
        "total_actual_model_workers_proven_by_this_dispatch":0,
        "confirmed_revenue_from_this_dispatch":0
    }

def worker_packet(global_index):
    row=assign_global_index(global_index)
    item=row["assignment"]
    parent=item["report_to"]
    company=item["company"]
    director=item["board_director"]
    dname=director.rsplit("/",1)[-1]
    speciality=next(x for x in DIRECTOR_LANES if x[0]==dname)
    return {
      "protocol":"CHIEF_D_GLOBAL_REVENUE_V2",
      "directive_source":row["owner_origin"]["current_order_id"],
      "owner_30_minute_mission":{
        "focus_minutes_on_real_activation":30,
        "intent":"Get legitimate transferable cryptocurrency paid to this company's approved correct-network owner wallet",
        "one_unique_job":"Verify real original buyer and funded scope; create independently useful work; submit only if actually authorized; follow up on buyer acceptance; confirm on-chain actual payment",
        "supervision":"Direct parent reviews concrete evidence, local company director audits, local D10 verifies receipts, sole Chief D consolidates",
        "virtual_role_is_not_live":True,
        "no_guaranteed_payment":True,
      },
      "owner_order":row["owner_origin"]["current_order_id"],
      "internal_role_under_human_owner":True,
      "my_whole_supervisory_ancestry_is_internal_to_my_company":True,
      "assistants_A_B_are_included_as_direct_reporting_children_of_local_D":True,
      "recruitment_handoff":row["recruitment_handoff"],
      "system_understanding_requirements":row["system_understanding_requirements"],
      "hierarchical_reporting":row["hierarchical_reporting"],
      "global_index":global_index,
      "task_id":item["task_id"],
      "company":company,
      "worker_id":item["worker_id"],
      "reports_to":parent,
      "reports_up_through":item["one_parent_chain"],
      "local_director":director,
      "director_job":speciality[1],
      "worker_assigned_job":speciality[2]+". "+item["specific_task"],
      "world_market_research_hypothesis":item["city_focus"]+", "+item["country_iso_3166_alpha2"],
      "translation_hint_locale":row["localization"]["content_language"],
      "original_paid_contract_or_funding_verified":False,
      "actual_worker_model_started":False,
      "independent_model_acknowledgement":PENDING_VERIFICATION,
      "submitted_to_customer":False,
      "buyer_accepted":False,
      "correct_company_BTC_mainnet_receiving_address":row["payment"]["owner_mainnet_address"],
      "receiving_network":"Bitcoin mainnet",
      "required_end_of_sprint_evidence":{
         "model_process_or_none":"NOT_YET_VERIFIED",
         "source_and_payer":"NOT_YET_VERIFIED",
         "original_deliverable":"NOT_YET_VERIFIED",
         "actual_authenticated_submission":"NOT_YET_VERIFIED",
         "buyer_acceptance":"NOT_YET_VERIFIED",
         "verified_receipt_txid":"NOT_YET_VERIFIED",
      },
      "crypto_payment_verified":False,
      "per_worker_one_cent_btc_target_only":row["payment"]["per_worker_owner_appreciation_earning_target_usd"],
      "next_required_work":"Check actual payer and original task, create unique work evidence, and obtain real buyer acceptance before claiming fees."
    }

def self_test():
    board=director_board()
    assert len(board["director_assignments"])==20
    assert board["internal_company_roles_under_human_owner"] is True
    assert sum(len(d["two_director_assistants"]) for d in board["director_assignments"])==40
    assert sum(len(d["all_fifteen_manager_roles_in_owner_scope"]) for d in board["director_assignments"])==300
    assert len({a["id"] for d in board["director_assignments"] for a in d["two_director_assistants"]})==40
    assert all(a["parent"]==d["director"] for d in board["director_assignments"] for a in d["two_director_assistants"])
    ids=[x["director"] for x in board["director_assignments"]]
    assert len(set(ids))==20
    assert all(sum(l["lead_id"] in x["real_lead_claims"] for x in board["director_assignments"])==1 for l in GLOBAL_ORIGINAL_BUYER_LEADS)
    assert board["source_verified_commercial_leads_not_yet_hired"][0]["crypto_received_verified"] is False
    tasks=[worker_packet(x) for x in (0,1,2,100,3_499_999_999,3_500_000_000,6_999_999_998,6_999_999_999)]
    assert len({t["task_id"] for t in tasks})==len(tasks)
    assert len({t["worker_id"] for t in tasks})==len(tasks)
    assert all(t["per_worker_one_cent_btc_target_only"]=="0.01" for t in tasks)
    assert all(t["owner_30_minute_mission"]["focus_minutes_on_real_activation"]==30 for t in tasks)
    assert all(t["correct_company_BTC_mainnet_receiving_address"] for t in tasks)
    assert all(t["directive_source"]==board["owner_order_id"] for t in tasks)
    assert all(t["recruitment_handoff"]["company"]==t["company"] for t in tasks)
    assert all(t["hierarchical_reporting"]["upward_path_current_role_to_owner"][-1]=="OWNER" for t in tasks)
    assert all(t["system_understanding_requirements"]["assessment_until_real_model_answer"]=="NOT_RUN" for t in tasks)
    assert all(t["recruitment_handoff"]["company_receiving_address"]==t["correct_company_BTC_mainnet_receiving_address"] for t in tasks)
    assert all(t["recruitment_handoff"]["actual_child_invited_or_created"] is False for t in tasks)
    assert all(not t["actual_worker_model_started"] and not t["submitted_to_customer"] for t in tasks)
    assert all(t["reports_up_through"][-1]==t["worker_id"] for t in tasks)
    assert {t["company"] for t in tasks}==set(FLEETS)
    print("B_GLOBAL_CHIEF_D_DISPATCH_TEST_PASS director_roles=20 unique_h_role_samples=8 actual_earnings_claimed=0")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--board",action="store_true")
    p.add_argument("--index",type=int)
    p.add_argument("--out")
    a=p.parse_args()
    if a.self_test:
        self_test()
    else:
        data=worker_packet(a.index) if a.index is not None else director_board()
        out=json.dumps(data,indent=2,ensure_ascii=False)+"\n"
        if a.out:
            Path(a.out).parent.mkdir(parents=True,exist_ok=True)
            Path(a.out).write_text(out,encoding="utf-8")
        else:print(out)
if __name__=="__main__":main()
