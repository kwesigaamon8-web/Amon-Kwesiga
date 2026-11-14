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
        records.append({
          "agent_id":wid,"parent_id":manager["id"],
          "director_id":role,"specialty":worker["role_name"],
          "manager_domain":manager["domain"],
          "search_query":worker["query"],
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
