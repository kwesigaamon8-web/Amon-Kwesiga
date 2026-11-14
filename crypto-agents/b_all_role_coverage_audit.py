"""Auditable inclusion of both B fleets in the latest owner order.

A deterministic exact role lookup is NOT evidence that the corresponding AI
model ran or personally received the order. This audit checks all 20 directors,
all 40 assistants, all 300 managers and representative descendants, plus
boundary and distributed checks in the seven-billion H namespace.
"""
from __future__ import annotations

import json
from datetime import datetime,timezone
from pathlib import Path
from b_universal_order_cascade import packet, packet_for_global_index, chief_packet, child_for_slot, wallet, FLEETS
from owner_first_oath import current_order

OUTPUT=Path("chief-D-global")
TOTAL_H=7_000_000_000

def audit():
    owner=current_order()["order_id"]
    chief=chief_packet()
    assert chief["owner_order_id"]==owner
    assert chief["companies"]==list(FLEETS)
    checked={"chief":1,"directors":0,"assistants":0,"managers":0,
             "W":0,"S":0,"G":0,"H_sampled":0}
    actual_model_runs_confirmed_by_this_audit=0
    receipt_evidence_confirmed_by_this_audit=0
    parent_names=set()
    sample_ids=set()
    for company in FLEETS:
        for d in range(1,11):
            director=f"D{d:02d}"
            root=packet(company,director)
            assert root["owner_order_id"]==owner
            assert root["worker_report_travels_up"]==[
                company+"/"+director,company,"CHIEF_D","OWNER"]
            assert root["actual_reporting_parent"]=="CHIEF_D"
            assert root["own_company_primary_payment"]["receive_address"]==wallet(company)
            checked["directors"]+=1
            for i in (16,17):
                advisor=child_for_slot(company,director,i)
                adv=packet(company,advisor)
                assert adv["owner_order_id"]==owner
                assert adv["actual_reporting_parent"]==company+"/"+director
                assert adv["own_company_primary_payment"]["receive_address"]==wallet(company)
                checked["assistants"]+=1
            for m in range(1,16):
                manager=child_for_slot(company,director,m)
                mg=packet(company,manager)
                assert mg["owner_order_id"]==owner
                assert mg["actual_reporting_parent"]==company+"/"+director
                assert mg["own_company_primary_payment"]["receive_address"]==wallet(company)
                checked["managers"]+=1
                # Each manager has 50 defined W positions; verify boundary
                # children and the inherited parent, then one S/G/H chain.
                for wi in (1,50):
                    w=child_for_slot(company,manager,wi)
                    wp=packet(company,w)
                    assert wp["owner_order_id"]==owner
                    assert wp["actual_reporting_parent"]==company+"/"+manager
                    checked["W"]+=1
                w=child_for_slot(company,manager,1)
                s=child_for_slot(company,w,150)
                g=child_for_slot(company,s,500)
                h=child_for_slot(company,g,666)
                for label,role,parent in (("S",s,w),("G",g,s),("H_sampled",h,g)):
                    row=packet(company,role)
                    assert row["actual_reporting_parent"]==company+"/"+parent
                    assert row["owner_order_id"]==owner
                    assert row["own_company_primary_payment"]["receive_address"]==wallet(company)
                    assert row["autonomous_commercial_freedom"]["may_choose_own_lawful_paying_task_market_and_method"]
                    checked[label]+=1
                    parent_names.add(row["actual_reporting_parent"])
    indexes=[0,1,2,9,123,9999,234567,3456789,99999999,
       500000000,1749999999,3499999997,3499999998,3499999999,
       3500000000,3500000001,3500000002,3500012345,
       4098765432,5999999999,6999999996,6999999997,6999999998,6999999999]
    examples=[]
    for idx in indexes:
        p=packet_for_global_index(idx)
        assert p["owner_order_id"]==owner
        assert p["worker_report_travels_up"][-1]=="OWNER"
        assert p["actual_reporting_parent"]==p["worker_report_travels_up"][1]
        assert p["current_real_delivery_state"]=="ORDER_INHERITED_IN_CONFIG_NOT_DELIVERED_TO_RUNNING_MODEL"
        assert p["own_company_primary_payment"]["receive_address"]==wallet(p["company"])
        assert p["global_H_target_index"]==idx
        assert p["role_id"] not in sample_ids
        sample_ids.add(p["role_id"])
        examples.append({"target_index":idx,"company":p["company"],"role_id":p["role_id"],
                         "owner_order_id":p["owner_order_id"],"immediate_parent":p["actual_reporting_parent"],
                         "assignment_only_no_live_model_claim":True})
    assert checked=={"chief":1,"directors":20,"assistants":40,"managers":300,
                     "W":600,"S":300,"G":300,"H_sampled":300}
    assert len(sample_ids)==len(indexes)
    return {
        "schema":"OWNER_ROLE_INCLUSION_AUDIT_V1",
        "owner_order_id":owner,
        "checked_at_utc":datetime.now(timezone.utc).isoformat(),
        "company_fleets":list(FLEETS),
        "directors_defined_all_included":20,
        "advisors_defined_all_included":40,
        "managers_defined_all_included":300,
        "seven_billion_global_H_indexes_covered_by_exact_on_demand_allocator":True,
        "H_index_range_inclusive":[0,TOTAL_H-1],
        "sampled_unique_H_target_indexes":len(indexes),
        "sampled_unique_H_target_ids":len(sample_ids),
        "representative_role_packets_checked":checked,
        "actual_cpu_models_started_by_this_audit":actual_model_runs_confirmed_by_this_audit,
        "incoming_transactions_proven_by_this_audit":receipt_evidence_confirmed_by_this_audit,
        "real_individual_order_receipts_verified":False,
        "no_assumption_all_7B_roles_are_active":True,
        "sample_H_orders":examples,
        "operational_rule":"Every actually running agent reads latest owner order at startup and reports evidence via one parent; configurations are not live agents."
    }

def main():
    a=audit()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/"ALL_ROLE_OWNER_ORDER_COVERAGE.json").write_text(json.dumps(a,indent=2)+"\n",encoding="utf-8")
    print("B_ALL_ROLE_OWNER_COVERAGE_AUDIT_PASS",
          json.dumps({k:a[k] for k in (
          "owner_order_id","representative_role_packets_checked",
          "sampled_unique_H_target_ids","seven_billion_global_H_indexes_covered_by_exact_on_demand_allocator",
          "actual_cpu_models_started_by_this_audit","incoming_transactions_proven_by_this_audit"
          )}))
if __name__=="__main__":main()
