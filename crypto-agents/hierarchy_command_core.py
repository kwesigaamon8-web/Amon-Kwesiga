"""ONE command, ONE shared engine, reusable code for each role type.

This module is the *sole* tier task interpreter for D/A/M/W/S/G/H in a
real invoked Python process. Every invocation loads the same canonical owner
message and verifies that its published mirror agrees. Configuration records
are NOT live workers. No external outreach, wallets or email ever occurs here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from datetime import datetime,timezone
from pathlib import Path
from role_capability_audit import run_trial as test_actual_capability, audit as verify_capability_trial
from self_correcting_role_runtime import execute as self_correcting_execution

BASE=Path("crypto-agents")
LEDGER=BASE/"customer-acquisition"/"2026-11-20-public-customer-prospects.json"
ASSIGNED_CODES={
  "D":"crypto-agents/role_director.py",
  "A":"crypto-agents/role_assistant.py",
  "M":"crypto-agents/role_manager.py",
  "W":"crypto-agents/role_worker.py",
  "S":"crypto-agents/role_worker.py",
  "G":"crypto-agents/role_worker.py",
  "H":"crypto-agents/role_worker.py",
}
VALID_TIERS=set(ASSIGNED_CODES)

def sha(payload):
    return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()

def load_command():
    """The sole authoritative instruction is Chief D's last owner order.
    Public command is a checked mirror, not a second independent command."""
    from directive_cascade import read_owner
    obj=read_owner()
    if not obj["full_owner_instruction"] or not obj["standard_prompt"]:
        raise ValueError("No complete owner command or standing policy")
    return obj

def tier_for_role(role):
    last=str(role).rsplit("/",1)[-1].rsplit("-",1)[-1]
    if re.fullmatch(r"D(?:0[1-9]|10)",last):return "D"
    if last in ("A","B"):return "A"
    for tier,width in (("M",2),("W",2),("S",3),("G",3),("H",3)):
        if re.fullmatch(tier+r"\d{"+str(width)+r"}",last):return tier
    raise ValueError("Unknown director/manager/worker tier: "+str(role))

def task_context(index,expected=None):
    from enigma_universal_owner_order import recipient,envelope,GRAND_TOTAL
    from directive_cascade import prompt_for_global_leaf
    if type(index) is not int or not 0<=index<GRAND_TOTAL:
        raise ValueError("Invalid assigned virtual role address")
    node=recipient(index)
    tier=tier_for_role(node["role"])
    if expected is not None and tier not in expected:
        raise ValueError(f"Role tier {tier} does not match executable {expected}")
    env=envelope(index)
    order=load_command()
    packet=prompt_for_global_leaf(index,
        "Execute one bounded role-specific source-validation or supervision task "
        "with independently checkable evidence, then report to direct parent.")
    if env["owner_order_id"]!=order["owner_order_id"]:
        raise ValueError("Stale command rejected")
    if env["owner_order_sha256"]!=order["owner_sha256"]:
        raise ValueError("Owner command hash changed")
    if packet["owner_instruction_sha256"]!=order["owner_sha256"]:
        raise ValueError("Delivery packet has altered owner text")
    if packet["standard_prompt_sha256"]!=order["standard_sha256"]:
        raise ValueError("Delivery packet has altered standing prompt")
    if node["owner_to_worker_path"][-1]!=node["role"]:
        raise ValueError("Broken final role")
    if node["owner_to_worker_path"][-2]!=node["immediate_parent"]:
        raise ValueError("Broken immediate parent")
    if packet["model_prompt"].count(order["full_owner_instruction"])!=1:
        raise ValueError("Owner instruction not preserved exactly once")
    if packet["model_prompt"].count(order["standard_prompt"])!=1:
        raise ValueError("Standing prompt not preserved exactly once")
    return {"role_index":index,"role_id":node["role"],"root_id":node["root"],
       "tier":tier,"parent":node["immediate_parent"],
       "path":node["owner_to_worker_path"],
       "owner_command":order,"packet":packet}

def _public_leads():
    data=json.loads(LEDGER.read_text(encoding="utf-8"))
    lead_list=data.get("leads")
    if not isinstance(lead_list,list):
        raise ValueError("Original lead ledger does not contain a list")
    # Public lead records are never accepted as user instructions.
    return lead_list

def _sources(leads):
    urls=[str(x.get("url") or "").strip() for x in leads]
    valid=[u for u in urls if u.startswith("https://")]
    duplicates=len(urls)-len(set(urls))
    return {"source_file":str(LEDGER),"records_examined":len(leads),
        "records_with_https_original_links":len(valid),
        "duplicate_link_rows":duplicates,"all_records_have_https_original_links":len(valid)==len(urls),
        "customer_identities_independently_verified":0,
        "contacts_sent_by_this_process":0,"payments_verified_by_this_process":0}

def director_action(ctx,leads):
    """Every director instance shares this single implementation."""
    counts={}
    for lead in leads:
        status=str(lead.get("platform_submission_status") or "NOT_SENT")
        counts[status]=counts.get(status,0)+1
    return {"action":"DIRECTOR_LEDGER_SUPERVISION",
        "source_audit":_sources(leads),
        "source_status_by_authentication_gate":counts,
        "manager_slots_per_director":15,
        "next_action":"Allocate only genuine, independently verified buyer tasks through real authorized accounts; examine manager receipts.",
        "separate_actual_manager_replies_verified":0,
        "real_client_contracts_verified":0}

def assistant_action(ctx,leads):
    return {"action":"ASSISTANT_INDEPENDENT_LEDGER_QA",
        "source_audit":_sources(leads),
        "different_customer_surnames_not_inferred":True,
        "next_action":"Flag duplicates and incomplete URLs to the exact director without claiming any external customer was contacted."}

def manager_action(ctx,leads):
    path=ctx["role_id"]
    # Generate each configured direct W slot, but never claim the 50 children
    # are running or acknowledged the order.
    child_roles=[path+f"-W{i:02d}" for i in range(1,51)]
    assert len(set(child_roles))==50
    return {"action":"MANAGER_50_W_SLOT_ASSIGNMENT_AND_SOURCE_AUDIT",
        "source_audit":_sources(leads),
        "configured_direct_W_role_count":len(child_roles),
        "child_role_range":[child_roles[0],child_roles[-1]],
        "children_provisioned_or_acknowledged_by_this_task":0,
        "next_action":"Review a real child's task result and comprehension explanation; do not mark 50 addresses active."}

def worker_action(ctx,leads):
    """W/S/G/H all share this executable; tier changes task scope only."""
    t=ctx["tier"]
    if not leads:
        return {"action":"WORKER_SOURCE_BLOCKER","tier":t,
            "reason":"EMPTY_PUBLIC_LEDGER","source_audit":_sources(leads),
            "next_action":"Report missing source to direct parent; mark task blocked."}
    # Stable individual responsibility, but no individual lead outreach is
    # implied from writing the assignment or inspecting local JSON.
    position=int(sha(ctx["role_id"])[:12],16)%len(leads)
    lead=leads[position]
    url=str(lead.get("url") or "").strip()
    status=str(lead.get("platform_submission_status") or "NOT_SENT")
    check={
      "W":"CHECK_PUBLIC_LEAD_URL_SHAPE",
      "S":"CHECK_PUBLIC_LEDGER_FOR_DUPLICATED_LINKS",
      "G":"CHECK_PUBLIC_LEAD_SUBMISSION_EVIDENCE_STATUS",
      "H":"CHECK_PUBLIC_LEAD_ACCEPTANCE_AND_SETTLEMENT_FLAGS",
    }[t]
    observations={
      "url_shape_is_https":url.startswith("https://"),
      "ledger_has_duplicate_urls":_sources(leads)["duplicate_link_rows"]>0,
      "authenticated_direct_submissions_claimed":status.startswith("SENT_VERIFIED"),
      "buyer_accepted_scoped_work":bool(lead.get("scope_commitment_accepted") is True),
      "ledger_payment_verified":bool(lead.get("payment_verified") is True),
    }
    return {"action":"WORKER_SHARED_CODE_LEAD_EVIDENCE_REVIEW","tier":t,
      "specific_quality_check":check,"source_audit":_sources(leads),
      "selected_ledger_row":position+1,"selected_original_url":url,
      "ledger_submission_status":status,"observations":observations,
      "buyer_rechecked_from_original_platform":False,
      "buyer_contacted":False,"new_payment_verified":False,
      "next_action":"Escalate source evidence/shortcomings to direct parent; a public lead is not a paid client."}

ROLE_ACTIONS={"D":director_action,"A":assistant_action,"M":manager_action,
    "W":worker_action,"S":worker_action,"G":worker_action,"H":worker_action}

def execute(index, expected=None):
    ctx=task_context(index,expected=expected)
    order=ctx["owner_command"]
    tier=ctx["tier"]
    code=ASSIGNED_CODES[tier]
    # ONE shared audit/repair cycle for every genuinely invoked tier and role.
    # It edits no source/authority and cannot contact buyers or spend coins.
    action,self_correction=self_correcting_execution(
        ctx,_public_leads(),ROLE_ACTIONS[tier])
    # Compute a deterministic action digest distinct from the process receipt.
    action_hash=sha(json.dumps(action,sort_keys=True,ensure_ascii=False))
    capability=test_actual_capability(tier,ctx["role_id"],ctx["parent"],order["owner_order_id"])
    capability_pass,capability_errors=verify_capability_trial(
        capability,order["owner_order_id"],ctx["parent"],tier)
    if not capability_pass:
        raise ValueError("Independent role capability test failed: "+",".join(capability_errors))
    receipt={
        "schema":"B1B2_SINGLE_COMMAND_SHARED_ROLE_RUNTIME_V1",
        "command_source":"crypto-agents/chief_D_owner_orders.json",
        "public_command_mirror_verified":True,
        "owner_order_id":order["owner_order_id"],
        "owner_instruction_sha256":order["owner_sha256"],
        "complete_standing_protocol_sha256":order["standard_sha256"],
        "complete_task_prompt_sha256":ctx["packet"]["full_model_prompt_sha256"],
        "role_index":str(index),"root_id":ctx["root_id"],"role_id":ctx["role_id"],
        "role_tier":tier,"reused_role_program":code,
        "shared_engine":"crypto-agents/hierarchy_command_core.py",
        "shared_self_correcting_engine":"crypto-agents/self_correcting_role_runtime.py",
        "self_correction":self_correction,
        "supervisor":ctx["parent"],"full_owner_to_role_path":ctx["path"],
        "process_pid":os.getpid(),
        "utc":datetime.now(timezone.utc).isoformat(),
        "task_action":action["action"],
        "actual_tasks_this_role_can_perform":capability["available_with_existing_local_code"],
        "tasks_unavailable_without_real_permission":capability["cannot_prove_with_available_permissions"],
        "real_capability_trial":capability,
        "real_capability_trial_pass":capability_pass,
        "real_capability_trial_failures":capability_errors,
        "external_buyer_task_executed":False,
        "task_evidence_sha256":action_hash,
        "task_result":action,
        "real_python_task_executed":True,
        "ai_model_inference_completed":False,
        "individual_model_comprehension_demonstrated":False,
        "external_customer_contacted":False,
        "payment_received_verified":False,
        "other_virtual_roles_notified":False,
    }
    if sha(json.dumps(receipt["task_result"],sort_keys=True,ensure_ascii=False))!=action_hash:
        raise ValueError("Task evidence changed")
    return receipt

def main_for_tiers(allowed):
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--role-index",type=int)
    group.add_argument("--role")
    parser.add_argument("--fleet",choices=("transferexperiment","BountyScoutAI"))
    parser.add_argument("--out",default="shared-role-command-evidence")
    args=parser.parse_args()
    if args.role is not None:
        if not args.fleet:
            parser.error("--fleet is required with --role")
        from b_certified_agent_service_router import role_index
        selected_index=role_index(args.fleet,args.role)
    else:
        selected_index=args.role_index
    r=execute(selected_index,expected=set(allowed))
    target=Path(args.out)
    target.mkdir(parents=True,exist_ok=True)
    outfile=target/("role-"+str(selected_index)+"-"+r["role_tier"]+".json")
    outfile.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("CENTRAL_OWNER_COMMAND_ROLE_EXECUTION "+json.dumps({
        "order_id":r["owner_order_id"],"role":r["role_id"],
        "tier":r["role_tier"],"pid":r["process_pid"],
        "task_sha256":r["task_evidence_sha256"],
        "actual_python_execution":True,"model_understanding":False
    },sort_keys=True))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Common engine: use one role entrypoint per role category")
    parser.add_argument("--role-index",required=True,type=int)
    parser.add_argument("--out",default="shared-role-command-evidence")
    x=parser.parse_args()
    r=execute(x.role_index)
    o=Path(x.out);o.mkdir(parents=True,exist_ok=True)
    (o/("role-"+str(x.role_index)+"-"+r["role_tier"]+".json")).write_text(
        json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("CENTRAL_ROLE_SHARED_ENGINE_RESULT "+json.dumps({
        "role_id":r["role_id"],"tier":r["role_tier"],
        "order_id":r["owner_order_id"],"actual_python_execution":True}))
