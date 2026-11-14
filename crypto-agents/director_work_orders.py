"""Issue 750 individual first-tier work orders per director, lazily inheriting all orders.

Assignment is a durable instruction, NOT a successful model execution or wallet receipt.
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from owner_order_distribution import summary
from command_chain_receipts import configured_assignment
from hierarchical_idea_governance import assignment as governed_idea_assignment

role=os.environ.get("ROLE_ID","")
if not re.fullmatch(r"D(?:0[1-9]|10)",role):
    raise SystemExit("Expected D01..D10 director for worker assignment")
config=json.loads(Path("crypto-agents/company_hierarchy.json").read_text(encoding="utf-8"))
company=next(c for c in config["companies"] if c["director_id"]==role)
orders=summary()
chief_D_latest=json.loads(Path("crypto-agents/chief_D_owner_orders.json").read_text(encoding="utf-8"))["orders"][-1]
collection=json.loads(Path("crypto-agents/b_collection_assignments.json").read_text(encoding="utf-8"))
payment_director=collection["director_operations"]["payment_director_id"]
director_function="payment_recovery" if role==payment_director else "independent_paid_work"
assignment_text=(
    "LOCAL D10 for this company only: investigate external delivered AND accepted work for this company's account, verify agreement, payer, amount, due date and authenticated settlement contact; report genuine payments to the overarching sole Chief D. Never count the other company's payment or internal jobs as debts."
    if director_function=="payment_recovery" else
    "D01-D09 earning directors within their own company: independently source real lawful paid opportunities, validate payer, eligibility and correct asset/network, produce useful deliverables and route true accepted unpaid client claims to their LOCAL D10; both company boards ultimately report to Chief D."
)
out=Path("director-work-orders")
out.mkdir(exist_ok=True)
records=[]
for manager in company["managers"]:
    for worker in config["worker_roles"]:
        n=int(worker["ordinal"])
        wid=manager["id"]+f"-W{n:02d}"
        idea_governance=governed_idea_assignment(os.environ.get("WORKFORCE_ID","transferexperiment"),wid)
        records.append({
          "agent_id":wid,"parent_id":manager["id"],
          "director_id":role,"specialty":worker["role_name"],
          "manager_domain":manager["domain"],
          "search_query":worker["query"],
          "hierarchical_idea_instruction":{
              "owner_order_id":idea_governance["issued_under"],
              "actual_worker_id":idea_governance["individual_worker"],
              "immediate_boss":idea_governance["direct_supervisor"],
              "company_director":idea_governance["company_director"],
              "idea_target":10,
              "specific_task":idea_governance["task"],
              "two_step_execution_sequence":idea_governance["task_sequence"],
              "first_unique_crypto_task":idea_governance["unique_funding_task"],
              "second_licensed_software_study":idea_governance["software_second_task"],
              "second_task_lawful_reuse_and_license_gate":True,
              "supervisor_if_stuck":idea_governance["manager_if_worker_stuck"],
              "state":"ASSIGNED_WAITING_FOR_REAL_MODEL_EXECUTION",
          },
          "chief_D_universal_audit_and_open_research_order":chief_D_latest["instruction"][:1300],
          "authorized_work":assignment_text, "director_function":director_function, "payment_director_id":payment_director,
          "strict_chief_D_order_id":orders["chief_D_current_owner_order_id"],
          "required_actual_execution_evidence":["model_completed","unique_agent_id","original_source_or_failure","separate_model_output","realistic_next_action","payment_status_truth"],
          "owner_order_registry_sha256":orders["sha256"],
          "all_owner_order_ids":orders["ids"],
          "defined_subagents":150,
          "defined_micro_workers":150*500,
          "defined_last_tier_workers":150*500*666,
          "status":"work_assigned_waiting_for_real_process_invocation",
          "command_chain_assignment":configured_assignment(wid),
          "verified_wallet_receipts":[]
        })
assert len(records)==750
doc={
 "director_id":role,
 "company_director_id":os.environ.get("WORKFORCE_ID","transferexperiment")+"/"+role,
 "chief_director_id":collection["hierarchy"]["chief_director"],
 "director_function":director_function,
 "payment_director_id":payment_director,
 "manager_assignments":[{"id":m["id"],"focus":m["domain"],"workers_assigned":50,
    "command_chain_assignment":configured_assignment(m["id"]),
    "idea_first_directive":"Manage your own 50 W workers. Each must generate ten distinct independently model-produced ideas, verify one original potential paying source, and know correct company BTC network. If unable or repetitive, issue one narrower task and verify a new actual response; escalate to your local company director.",
    "ten_ideas_required_per_actual_worker":True,
    "two_ordered_tasks_each_actual_B":[
        "FIRST original 10 ideas plus unique source-confirmed funding assignment",
        "SECOND inspect assigned public software, verify actual license, learn its functionality and prepare an original, license-compliant improvement linked to first task"
    ],
    "manager_checks_actual_second_model_result_and_license":True,
    "manager_must_not_call_open_code_copy_completed_without_committed_artifact":True,
    "manager_review_model_status":"NOT_EXECUTED_IN_THIS_ASSIGNMENT",
    "supervisor_correction_status":"ASSIGNED_ONLY",
    "understanding_status":"pending_manager_model_response"} for m in company["managers"]],
 "individual_first_tier_worker_assignments":records,
 "first_tier_work_order_count":len(records),
 "director_command_chain":configured_assignment(role),
 "manager_model_replies_not_verified_in_this_dispatch":15,
 "worker_model_replies_not_verified_in_this_dispatch":750,
 "defined_S_G_H_roles_accessible_by_lazy_factory":True,
 "total_descendant_defined_roles_per_director":750*(1+150+150*500+150*500*666),
 "canonical_owner_orders":orders,
 "generated_utc":datetime.now(timezone.utc).isoformat(),
 "execution_status":"assignments_only_not_750_live_models",
 "cryptocurrency_earnings_verified":[]
}
(out/(role+".json")).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("WORK_ORDERS",role,"managers",15,"worker_assignments",len(records),
      "all_owner_orders",orders["count"],"actual_models_claimed",0)
