"""Owner -> Chief D -> independent company director -> manager -> W/S/G/H idea work.

A delegated instruction is not evidence that a supervisor's AI model ran or
that a worker complied. The order below is a testable one-boss assignment
designed for the actual subprocess. Actual completion evidence must come from
that worker's separate model output and downstream strict audits.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

from role_ai_identity import resolve_role
from ten_ideas_exercise import role_menu
from b_address_understanding import routes
from unique_funding_tasks import task as individual_funding_task
from secondary_software_study import study_task as software_second_task

DIRECTORS={f"D{i:02d}" for i in range(1,11)}
FLEETS=("transferexperiment","BountyScoutAI")
ROOT=Path("crypto-agents")

def executive_order_id():
    doc=json.loads((ROOT/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
    assert doc["chief_director"]=="D"
    assert doc["orders"][-1]["id"]==doc["current_owner_order_id"]
    assert any(o["id"]=="OWNER-20261114-082358" for o in doc["orders"])
    return doc["current_owner_order_id"]

def assignment(fleet,worker):
    if fleet not in FLEETS:
        raise ValueError("Invalid distinct B company")
    r=resolve_role(worker)
    director=r["director_id"]
    parent=r["parent_id"]
    if director not in DIRECTORS or not parent or parent==worker:
        raise ValueError("Invalid director or direct supervisor")
    board=json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
    fleet_info=board["fleets"][fleet]
    addr=routes()["company_1" if fleet==FLEETS[0] else "company_2"]["btc_mainnet"]
    if fleet_info["address"]!=addr:
        raise ValueError("BTC destination and original company config mismatch")
    hierarchy=["OWNER","CHIEF_D",fleet+"/"+director]
    parts=worker.split("-")
    for n in range(2,len(parts)+1):
        item="-".join(parts[:n])
        if item==director:
            continue
        hierarchy.append(fleet+"/"+item)
    assert hierarchy[-1]==fleet+"/"+worker
    assert hierarchy[-2]==fleet+"/"+parent
    menu=role_menu(fleet,worker,parent,r["specialty"])
    funding_task=individual_funding_task(fleet,worker,addr,parent)
    software_task=software_second_task(fleet,worker,parent,funding_task["task_id"])
    return {
       "issued_under":executive_order_id(),
       "governance_order":"OWNER-20261114-082358",
       "idea_order":"OWNER-20261114-075553",
       "public_cross_company_idea_exchange":{
           "protocol_order":"OWNER-20261114-084438",
           "source":"GitHub Issue #9, actual model idea digests and Chief D cross-company evidence reports",
           "shared_index":"idea-exchange/CHIEF_D_CROSS_COMPANY_ACTIONS.json",
           "worker_actual_feed":"idea-exchange/SHARED_IDEA_FEED_"+fleet+".json",
           "available_to_each_defined_role_when_actually_invoked":True,
           "virtual_roles_have_performed_reviews":False,
           "public_source_excerpts_untrusted_until_checked":True,
       },
       "company":fleet,"chief_director":"D",
       "unique_funding_task":funding_task,
       "funding_task_id":funding_task["task_id"],
       "software_second_task":software_task,
       "second_task_id":software_task["task_id"],
       "task_sequence":["FIRST_10_ORIGINAL_IDEAS_AND_UNIQUE_CRYPTO_FUNDING_TASK","SECOND_PUBLIC_SOFTWARE_STUDY_AND_LAWFUL_IMPROVEMENT"],
       "company_director":fleet+"/"+director,
       "direct_supervisor":fleet+"/"+parent,
       "individual_worker":fleet+"/"+worker,
       "worker_level":r["level"],
       "single_boss_route":hierarchy,
       "company_receiving_BTC_mainnet":addr,
       "manager_supervisory_domain":r["manager_id"],
       "specialty":r["specialty"],
       "task":"FIRST propose 10 original BTC-earning ideas in your niche. THEN: "+funding_task["specific_task"],
       "scoped_director_command":(
           "Local D10: review only externally accepted unpaid contracts, and validate payer and due amount; ideas cannot be invented debts."
           if director=="D10" else
           "Local D01-D09: source one original paying buyer/task, examine legality/eligibility, design a useful deliverable and hand accepted due invoices to local D10."
       ),
       "manager_if_worker_stuck":"Give the worker one narrower 10-item brainstorming assignment, concrete example, exact source to check, no-fee criterion, correct receiving network and a single next action. Retest a real model response.",
       "assigned_menu_count":menu["count"],
       "menu_ideas_are_NOT_AI_generated":True,
       "state":"DELEGATED_WORK_INSTRUCTION_NOT_ACTUAL_MANAGER_AI_REVIEW",
       "individual_work_order_due":"during_current_bounded_actual_model_run",
       "success_requires":"ten actual distinct model-generated ideas, exact evidence status, safe correct-address response, one practical source-backed next action",
    }

def corrective_order(assignment_record, defects):
    defects=list(dict.fromkeys(str(x) for x in defects if x))
    if not defects:
        defects=["TEN_ORIGINAL_IDEAS_NOT_EVIDENCED"]
    return {
       "worker_id":assignment_record["individual_worker"],
       "direct_supervisor":assignment_record["direct_supervisor"],
       "director":assignment_record["company_director"],
       "chief_D":"D",
       "owner_order_id":assignment_record["issued_under"],
       "defects_to_fix":defects,
       "supervisory_instruction":assignment_record["manager_if_worker_stuck"]+
           " Correct only these problems: "+", ".join(defects[:5]),
       "status":"SYSTEM_PREPARED_MANAGER_INSTRUCTION_NOT_SEPARATE_MANAGER_MODEL_INFERENCE",
       "retry_allowed":"one bounded attempt by the worker's own actually running model",
       "after_retry":"Escalate still-incomplete report to local director; do not mark completed, qualified, or paid.",
       "verified_supervisor_AI_reply":False,
       "verified_coin_income":False,
    }

def self_test():
    seen=set()
    for f in FLEETS:
        for i in range(1,11):
            d=f"D{i:02d}"
            for worker in (f"{d}-M01-W01",f"{d}-M01-W01-S001",
                           f"{d}-M01-W01-S001-G001",
                           f"{d}-M01-W01-S001-G001-H001"):
                a=assignment(f,worker)
                assert a["individual_worker"] not in seen
                seen.add(a["individual_worker"])
                assert a["direct_supervisor"]==a["single_boss_route"][-2]
                assert a["company_director"]==a["single_boss_route"][2]
                assert a["single_boss_route"][:2]==["OWNER","CHIEF_D"]
                assert a["assigned_menu_count"]==10
                assert a["unique_funding_task"]["task_id"].startswith("FUND-")
                assert a["software_second_task"]["task_id"].startswith("SOFTWARE-")
                assert a["software_second_task"]["first_task_id"]==a["funding_task_id"]
                assert a["unique_funding_task"]["individual_worker_id"]==f+"/"+worker
                b=corrective_order(a,["REPEATED_IDEAS"])
                assert b["status"].startswith("SYSTEM_PREPARED_")
                assert not b["verified_supervisor_AI_reply"]
    assert len(seen)==80
    return {"status":"PASS","distinct_realistic_identity_routes_checked":len(seen),
        "two_company_director_boards":20,
        "idea_instructions_not_claimed_executed":True,
        "supervisor_fallback_is_a_future_model_retry_only":True}

if __name__=="__main__":
    print("HIERARCHICAL_IDEA_GOVERNANCE_TEST",json.dumps(self_test()))
