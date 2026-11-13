"""Audit and safely execute the owner's standing research-system orders.

Execution means actual check/triage/report actions in a standalone cloud run.
It never interprets arbitrary text as executable Python/shell or makes external
wallet, financial, mass-message or contracting actions.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path("crypto-agents")
ORDERS=ROOT/"owner_orders.json"
REGISTRY=ROOT/"agent_registry.csv"
HIERARCHY=ROOT/"company_hierarchy.json"
SHARED=ROOT/"shared_understanding.json"
COMMAND=ROOT/"owner_command_chain.json"
FACTORY=ROOT/"subagent_factory.json"
READONLY_COMMENT_PATTERN=re.compile(r"^/owner-order[ \t]+(.{4,2000})",re.S)

def as_json(path):
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,ValueError): return None

def get_authenticated_pending(issue=8,owner="kwesigaamon8-web"):
    """Return owner-written request data; NEVER execute comments as commands."""
    token=os.getenv("GITHUB_TOKEN")
    url=f"https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/issues/{issue}/comments?per_page=100"
    headers={"Accept":"application/vnd.github+json","User-Agent":"OwnerInstructionAudit/1.0"}
    if token:headers["Authorization"]="Bearer "+token
    found=[]
    try:
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=12) as resp:
            comments=json.loads(resp.read(500000))
        for comment in comments:
            if (comment.get("user") or {}).get("login")!=owner:
                continue
            m=READONLY_COMMENT_PATTERN.match((comment.get("body") or "").strip())
            if not m:continue
            instruction=m.group(1).strip()
            found.append({
                "source":"authenticated_repository_comment",
                "comment_id":comment.get("id"),
                "created_at":comment.get("created_at"),
                "instruction":instruction,
                "status":"new_order_requires_scoping_and_tool_verification",
                "executed":False,
                "safe_action":"Record and assess; never execute comment text as program code."
            })
        return found, None
    except Exception as exc:
        return [],"owner_order_inbox_unavailable:"+str(exc)[:145]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="owner-order-audit")
    parser.add_argument("--reports",default=None)
    parser.add_argument("--skip-inbox",action="store_true")
    args=parser.parse_args()
    now=datetime.now(timezone.utc).isoformat()
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    instructions=as_json(ORDERS)
    hierarchy=as_json(HIERARCHY)
    shared=as_json(SHARED)
    command=as_json(COMMAND)
    factory=as_json(FACTORY)
    hard_fail=[]
    warnings=[]
    if not all([instructions,hierarchy,shared,command,factory]):
        raise SystemExit("Order control cannot proceed: required standing files missing or malformed")
    with REGISTRY.open(encoding="utf-8",newline="") as f:
        roles=list(csv.DictReader(f))
    by_id={r["id"]:r for r in roles}
    if len(by_id)!=len(roles):hard_fail.append("Duplicate registered role identifiers")
    if len(set(r["agent_name"] for r in roles))!=len(roles):hard_fail.append("Nonunique agent names")
    counts=Counter(r["level"] for r in roles)
    required={"director":10,"independent_assistant":20,"manager":150,"worker":7500}
    if any(counts[key]!=value for key,value in required.items()):
        hard_fail.append("Main hierarchy role counts differ from authorized staffing")
    companies=hierarchy.get("companies",[])
    if len(companies)!=10:hard_fail.append("Expected ten director companies")
    mismatches=0
    for c in companies:
        d=c["director_id"]
        if by_id.get(d,{}).get("parent_id")!="OWNER":mismatches+=1
        if len(c["assistant_ids"])!=2 or len(c["managers"])!=15:mismatches+=1
        for a in c["assistant_ids"]:
            if by_id.get(a,{}).get("parent_id")!=d:mismatches+=1
        for m in c["managers"]:
            mid=m["id"]
            if by_id.get(mid,{}).get("parent_id")!=d:mismatches+=1
            for n in range(1,51):
                if by_id.get(f"{mid}-W{n:02d}",{}).get("parent_id")!=mid:
                    mismatches+=1
    if mismatches:hard_fail.append("Broken one-parent reporting relationships: "+str(mismatches))
    if factory.get("new_subagents_per_worker")!=150 or factory.get("parent_workers")!=7500:
        hard_fail.append("Child agent factory does not define 150 per 7500")
    if factory.get("new_subagent_identities")!=1125000:
        hard_fail.append("Subagent cardinality incorrect")
    if len(factory.get("independent_scope_templates",[]))!=150:
        hard_fail.append("Child task templates are not all distinct 150 slots")
    if len({x.get("id") for x in factory["independent_scope_templates"]})!=150:
        hard_fail.append("Child role specialization IDs are duplicated")
    owner_goal=(shared.get("owner_intent") or {}).get("real_goal","")
    if not all(word in owner_goal.lower() for word in ("cryptocurrency","approved","received")):
        hard_fail.append("Owner understanding does not require received cryptocurrency")
    command_goal=command.get("owner_directive","")
    if "cryptocurrency" not in command_goal.lower() or "received" not in command_goal.lower():
        hard_fail.append("Owner command directive does not state crypto-only receipt goal")
    for file,checks in {
      "agents.py":["SHARED[","owner_understanding","director_priority_understood"],
      "company_ai_review.py":["SHARED[","child[","owner_coin_only_goal"],
      "deep_research.py":["check_one","counter_evidence_and_risks"],
      "director_coordination.py":["handoff_register","verified_paid_receipts"],
      "wallet_routes.py":["private_directory_not_configured"],
      "post_conference.py":["company-conference-activity","no completed company worker reports"],
      "subagent_factory.py":["def describe_child","def select_slot"],
      "subagent_audit.py":["verified_completed_individual_child_model_calls"]
    }.items():
        src=(ROOT/file)
        if not src.exists():
            hard_fail.append("Missing execution component: "+file)
            continue
        code=src.read_text(encoding="utf-8")
        for needle in checks:
            if needle not in code:
                warnings.append("Missing expected evidence marker "+file+": "+needle)
    # Real results are assessed separately from saved source. Default to no
    # runtime verification, not to an invented "zero cryptocurrency" statement.
    runtime={
      "provided_report_folder":bool(args.reports),
      "worker_ai_success_count":0,"subagent_ai_success_count":0,
      "manager_ai_success_count":0,"director_ai_success_count":0,
      "verified_incoming_coin_receipts":[],
      "reported_receipts_are_not_wallet_verified":True,
      "status":"not_assessed_no_completed_reports"
    }
    if args.reports:
        base=Path(args.reports)
        if base.exists():
            runtime["status"]="inspected_available_report_files"
            for path in base.rglob("*.json"):
                record=as_json(path)
                if not isinstance(record,dict):continue
                completed=(record.get("model_inference") or {}).get("status")=="model_completed"
                if record.get("level")=="delegated_subagent" and completed:
                    runtime["subagent_ai_success_count"]+=1
                elif record.get("worker_id") and completed:
                    runtime["worker_ai_success_count"]+=1
                elif record.get("manager_id") and record.get("workers_executed_this_cycle") is not None and completed:
                    runtime["manager_ai_success_count"]+=1
                elif record.get("role") and (record.get("ai_analysis") or {}).get("status")=="llm_completed":
                    runtime["director_ai_success_count"]+=1
            warnings.append("Research report markers cannot independently verify blockchain/exchange account ownership or credit.")
        else:
            warnings.append("Requested runtime evidence directory is unavailable.")
    if args.skip_inbox:
        owner_inbox, inbox_error=[], "owner comment intake intentionally skipped"
    else:
        owner_inbox, inbox_error=get_authenticated_pending(
            instructions.get("order_intake_issue",8),
            instructions.get("order_author_gitHub_login","kwesigaamon8-web"))
    if inbox_error:warnings.append(inbox_error)
    order_results=[]
    director_queues=defaultdict(list)
    for order in instructions["orders"]:
        refs=order.get("evidence_files",[])
        missing=[p for p in refs if not Path(p).is_file()]
        configured=(len(missing)==0)
        blockers=[]
        if missing:blockers.extend("Missing source or proof: "+p for p in missing)
        if order["id"] in ("ORD-010","ORD-015"):
            blockers.append("Outside-network replies not authorized by existing GitHub-only automation; only permitted research and drafts are configured.")
        if order["id"]=="ORD-012":
            blockers.append("Encrypted full wallet route directory cannot be confirmed configured or injected into active jobs.")
        if order["id"] in ("ORD-005","ORD-006","ORD-007","ORD-008","ORD-009","ORD-011","ORD-014"):
            blockers.append("Requires a successful relevant cloud run with inspectable role-specific report evidence.")
        if order["id"] in ("ORD-001","ORD-013"):
            blockers.append("No independently verified incoming cryptocurrency receipt supplied to this audit.")
        if order["id"]=="ORD-016":
            blockers.append("Future ChatGPT messages are not automatically accessible to this GitHub process. Instructions must be synchronized here or owner-authored in issue #8.")
        status=("source_missing" if missing else
                "configured_with_execution_blockers" if blockers else
                "configuration_present_needs_runtime_proof")
        outcome={
          "id":order["id"],"title":order["title"],
          "accountable_director":order["accountable_director"],
          "config_files_valid":configured,
          "actual_audit_action_executed":"source_file_presence_and_consistency_checked",
          "status":status,
          "remaining_blockers":blockers,
          "missing_files":missing,
          "coins_received_verified_by_this_audit":False,
          "next_action":order["verification_condition"]
        }
        order_results.append(outcome)
        director_queues[order["accountable_director"]].append(outcome)
    for director in [f"D{i:02d}" for i in range(1,11)]:
        queue=director_queues[director]
        (out/(director+".json")).write_text(json.dumps({
          "director":director,
          "owner_goal":owner_goal,
          "orders_assigned":queue,
          "audit_completed_utc":now,
          "reporting":"Report actual actions and blockers up one parent to OWNER; no claimed crypto receipts."
        },indent=2),encoding="utf-8")
    (out/"new_owner_requests_pending_review.json").write_text(
        json.dumps(owner_inbox,indent=2),encoding="utf-8")
    result={
      "audited_utc":now,
      "executed_checks":["Read standing order registry","Verify role IDs, unique names and exact one-parent hierarchy","Verify 150-child identity formula","Check code evidence per order","Inspect available model records if provided","Triage owner-authored pending issue comments"],
      "standing_orders_total":len(order_results),
      "standing_orders_with_configuration_present":sum(x["config_files_valid"] for x in order_results),
      "owner_orders_executed_as_external_actions":0,
      "payment_receipts_independently_verified":[],
      "new_owner_requests_requires_review":len(owner_inbox),
      "hard_failures":hard_fail,"warnings":warnings,
      "runtime":runtime,
      "orders":order_results,
      "limitations":"This is a real configuration and evidence audit, not arbitrary autonomous command execution, a crypto wallet monitor, or confirmation that all generated agent roles are running."
    }
    (out/"audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    md=[
      "# Owner instructions: audit and safe execution results",
      "",f"UTC audit: {now}",
      "",
      f"**Standing orders checked:** {len(order_results)}.",
      f"**Configuration references present:** {result['standing_orders_with_configuration_present']}/{len(order_results)}.",
      f"**Owner requests in GitHub issue #8 awaiting review:** {len(owner_inbox)}.",
      f"**Independent received-coin proofs available to this audit:** none.",
      f"**Structural audit:** {'PASS' if not hard_fail else 'FAIL'}",
      "",
      "| Order | Accountable director | Code state | Evidence still needed |",
      "|---|---|---|---|"
    ]
    for o in order_results:
        missing=("; ".join(o["remaining_blockers"][:2]) if o["remaining_blockers"] else "Live execution evidence")
        md.append(f"| {o['id']} {o['title']} | {o['accountable_director']} | {o['status']} | {missing.replace('|','/')} |")
    md+=["","## Runtime AI results",f"Status: {runtime['status']}",
         f"Worker model calls: {runtime['worker_ai_success_count']}, manager: {runtime['manager_ai_success_count']}, subagent: {runtime['subagent_ai_success_count']}, director/assistant: {runtime['director_ai_success_count']}.",
         "These are only counts of saved successful inference markers, if inspected; not verified payment receipts.",
         "","## Unresolved risks"]
    md.extend("- "+w for w in (hard_fail+warnings)[:20])
    if not hard_fail and not warnings:md.append("No structural or retrieval warnings.")
    md+=["","## Operational boundaries",
        "Only read-only validation, evidence-backed report generation and previously authorized repository communications are performed here.",
        "Owner comments become requests for review, never executable shell code; unauthenticated or unscoped requests are not executed.",
        "No coins or contracts were created by this audit itself."]
    (out/"AUDIT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print("OWNER_ORDER_AUDIT",json.dumps({
      "orders_checked":len(order_results),"configured":result["standing_orders_with_configuration_present"],
      "structural":"PASS" if not hard_fail else "FAIL",
      "new_owner_requests":len(owner_inbox),
      "verified_receipts":0,
      "model_execution_status":runtime["status"]
    }))
    if hard_fail:
        raise SystemExit("Owner order structural audit failed: "+"; ".join(hard_fail[:8]))

if __name__=="__main__":main()
