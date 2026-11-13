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
          "authorized_work":"Independently find current lawful genuinely crypto-paid work; verify original source, payer, terms and eligible network; write your own evidence-backed report when executed.",
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
