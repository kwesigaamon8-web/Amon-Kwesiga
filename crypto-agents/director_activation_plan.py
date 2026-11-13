"""Director responsibility: convert role definitions into verifiable AI agents.

A worker is not active because it has an ID, assignment, or a JSON file.
This plans a bounded next wave of *different* roles for each director and
summarizes the activation requirements. Actual model work is checked later.
"""
import json
import os
import re
import time
from datetime import datetime,timezone
from pathlib import Path
from owner_order_distribution import summary
from fair_agent_scheduler import activation_summary

DIRECTOR=os.environ.get("ROLE_ID","")
if not re.fullmatch(r"D(?:0[1-9]|10)",DIRECTOR):
    raise SystemExit("A director D01..D10 must be selected")
CONFIG=json.loads(Path("crypto-agents/company_hierarchy.json").read_text(encoding="utf-8"))
OWN=summary()
company=next(c for c in CONFIG["companies"] if c["director_id"]==DIRECTOR)
OUT=Path("director-work-orders");OUT.mkdir(exist_ok=True)
# Deterministic tier-fair queue: 12 or 13 ACTUAL MODEL SLOTS per W/S/G/H
# tier each run. Defined IDs not selected remain mathematically available,
# but NOT claimed active until a real AI model independently executes.
cycle=int(os.getenv("GITHUB_RUN_NUMBER") or int(time.time()//3600))
fair=activation_summary(DIRECTOR,cycle,50)
roles=fair["selected_ids"]
assert len(roles)==len(set(roles))==50
out={
 "director":DIRECTOR,
 "prepared_utc":datetime.now(timezone.utc).isoformat(),
 "owner_order":"ORD-038",
 "director_D_reports_to_owner":True,
 "director_activation_target_per_batch":50,
 "selection_run_cycle":cycle,
 "selection_method":"Four-tier bijective mixed-radix scheduling via GitHub workflow-run counter; each selected role becomes active ONLY upon actual model inference",
 "role_tier_activation_budget":fair["activation_counts_by_tier"],
 "distinct_managers_selected":fair["distinct_managers_selected"],
 "scheduler_version":"ORD-041-fair-agent-fabric",
 "defined_roles_under_director":750*(1+150+150*500+150*500*666)+17,
 "registered_owner_orders":OWN["count"],
 "owner_order_register_sha256":OWN["sha256"],
 "examples_eligible_for_process_launch":roles,
 "owner_directive_applies_to_every_defined_role":True,
 "still_virtual_until_executed":True,
 "accountability":{
  "recruit_or_instantiate_billions_of_paid_external_host_accounts":False,
  "use_only_current_approved_free_host_capacity":True,
  "agent_must_execute_a_model":True,
  "agent_must_attempt_authorized_public_research":True,
  "agent_must_independently_decide_next_action":True,
  "agent_must_have_unique_parent_and_order_receipt":True,
  "agent_must_write_source_cited_individual_report":True,
  "agent_must_have_checkpoint_for_future_cycle":True,
  "agent_is_not_permanently_live_after_runner_shutdown":True,
  "payment_requires_separate_verified_owner_wallet_credit":True,
  "success_metric":"Actual successful distinct role process+inference+source+report, not role definitions."
 },
 "not_yet_executed":roles,
 "activated_distinct_agents_verified_by_this_planning_script":0,
 "activation_failures_and_blockers":[],
 "forward_to":"Director D"
}
(OUT/(DIRECTOR+"-activation-plan.json")).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print("ACTIVATION_PLANNED",DIRECTOR,len(roles),"no_live_agents_claimed",True)
