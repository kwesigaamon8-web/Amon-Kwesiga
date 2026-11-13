"""Independent-agent integrity audit: unique identities, ONE boss and real AI execution.

This checks source-of-truth registry AND, when supplied, actual cloud reports.
Configured roles != running models != humans. No credentials or wallet actions.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("--reports",default=None,help="Optional downloaded GitHub Actions reports")
parser.add_argument("--output",default="independence-audit")
args=parser.parse_args()
ROOT=Path("crypto-agents")
out=Path(args.output)
out.mkdir(parents=True,exist_ok=True)
hierarchy=json.loads((ROOT/"company_hierarchy.json").read_text(encoding="utf-8"))
roles=json.loads((ROOT/"roles.json").read_text(encoding="utf-8"))
with (ROOT/"agent_registry.csv").open(encoding="utf-8",newline="") as handle:
    records=list(csv.DictReader(handle))

failures=[]
warnings=[]
ids=[r["id"] for r in records]
names=[r["agent_name"] for r in records]
if len(ids)!=7680: failures.append(f"Registry has {len(ids)} roles, expected 7680")
if len(set(ids))!=len(ids): failures.append("Duplicate role IDs")
if len(set(names))!=len(names): failures.append("Duplicate agent display names")
if len(hierarchy.get("companies",[]))!=10: failures.append("Expected 10 director companies")
type_count=Counter(r.get("level") for r in records)
expected_count={"director":10,"independent_assistant":20,"manager":150,"worker":7500}
for level,expected in expected_count.items():
    if type_count[level]!=expected:
        failures.append(f"Expected {expected} {level} roles, found {type_count[level]}")
lookup={r["id"]:r for r in records}
expected_parents={}
names_seen=set()
for company in hierarchy["companies"]:
    d=company["director_id"]
    if d not in lookup: failures.append("Director absent: "+d);continue
    expected_parents[d]="OWNER"
    if lookup[d]["level"]!="director":
        failures.append("Director not director: "+d)
    assist=company["assistant_ids"]
    if len(assist)!=2 or len(set(assist))!=2:
        failures.append("Director must have two distinct independent assistants: "+d)
    for a in assist:
        expected_parents[a]=d
        if lookup.get(a,{}).get("level")!="independent_assistant":
            failures.append("Assistant has wrong level: "+a)
    managers=company["managers"]
    if len(managers)!=15: failures.append(d+" must have exactly 15 managers")
    for manager in managers:
        mid=manager["id"]
        expected_parents[mid]=d
        if lookup.get(mid,{}).get("level")!="manager":
            failures.append("Manager has wrong level: "+mid)
        if manager.get("reports_to")!=d:
            failures.append("Manager points to wrong director: "+mid)
        for n in range(1,51):
            wid=f"{mid}-W{n:02d}"
            expected_parents[wid]=mid
            worker=lookup.get(wid)
            if not worker:
                failures.append("Missing worker "+wid)
                continue
            if worker["level"]!="worker":
                failures.append("Worker has wrong level "+wid)
            if not worker["assignment"].strip():
                failures.append("Worker has no assignment "+wid)

if len(expected_parents)!=7680:
    failures.append(f"Hierarchy expected role references {len(expected_parents)}/7680")
for rid,expected_parent in expected_parents.items():
    entry=lookup.get(rid)
    if entry and entry.get("parent_id")!=expected_parent:
        failures.append(f"Incorrect reporting line {rid}: expected {expected_parent}")
for rid,record in lookup.items():
    parent=record.get("parent_id")
    if not parent:
        failures.append("No reporting parent "+rid)
    if parent!="OWNER" and parent not in lookup:
        failures.append("Nonexistent reporting parent "+rid)
    if rid not in expected_parents:
        failures.append("Unexpected role "+rid)
    # Follow reporting chain; it must terminate in the owner.
    chain=set()
    target=rid
    for _ in range(5):
        if target=="OWNER":break
        if target in chain or target not in lookup:
            failures.append("Cycle or broken chain starting "+rid)
            break
        chain.add(target)
        target=lookup[target]["parent_id"]
    else:
        failures.append("Reporting chain exceeded expected depth "+rid)
    if target!="OWNER":
        failures.append("Reporting does not terminate with owner: "+rid)

base_role_ids={x["id"] for x in roles}
expected_supervisors={d+s for d in (f"D{i:02d}" for i in range(1,11)) for s in ("","-A","-B")}
if base_role_ids!=expected_supervisors:
    failures.append("30 primary AI roles do not match registered directors and assistants")
parented=defaultdict(list)
for r in records:
    parented[r["parent_id"]].append(r["id"])
for c in hierarchy["companies"]:
    d=c["director_id"]
    direct=parented[d]
    if len(direct)!=17:
        failures.append(d+" has "+str(len(direct))+" direct reports, expected 2 assistants + 15 managers")
    for manager in c["managers"]:
        mid=manager["id"]
        if len(parented[mid])!=50:
            failures.append(mid+" has "+str(len(parented[mid]))+" reports, expected 50")

evidence={
  "reports_available":False,
  "actual_AI_executions_verified":0,
  "actual_worker_AI_executions_verified":0,
  "actual_manager_AI_executions_verified":0,
  "actual_director_and_assistant_AI_executions_verified":0,
  "worker_reports_found":0,
  "manager_reports_found":0,
  "main_role_reports_found":0,
  "inference_results_with_wrong_reporting_parent":0,
  "identical_worker_ai_answers":0,
  "actual_independent_model_execution_status":"not_assessed_no_cloud_reports",
  "scheduled_cloud_run_is_not_proof_of_all_7680_models":True
}
if args.reports and Path(args.reports).exists():
    evidence["reports_available"]=True
    reports_dir=Path(args.reports)
    worker_responses=defaultdict(list)
    seen_worker=set()
    seen_manager=set()
    seen_main=set()
    for file in reports_dir.rglob("*.json"):
        try:
            data=json.loads(file.read_text(encoding="utf-8"))
        except (ValueError,OSError):
            continue
        wid=data.get("worker_id")
        mid=data.get("manager_id")
        rid=data.get("role")
        if wid in lookup and lookup[wid]["level"]=="worker":
            seen_worker.add(wid)
            if mid!=lookup[wid]["parent_id"] or data.get("reports_to_one")!=mid:
                evidence["inference_results_with_wrong_reporting_parent"]+=1
            inference=data.get("model_inference") or {}
            if inference.get("status")=="model_completed":
                if inference.get("parent_id")!=mid:
                    evidence["inference_results_with_wrong_reporting_parent"]+=1
                evidence["actual_worker_AI_executions_verified"]+=1
                answer=re.sub(r"\s+"," ",inference.get("analysis","").strip().lower())
                if answer:
                    worker_responses[hashlib.sha256(answer.encode()).hexdigest()].append(wid)
        elif mid in lookup and lookup[mid]["level"]=="manager" and data.get("workers_executed_this_cycle") is not None:
            seen_manager.add(mid)
            inference=data.get("model_inference") or {}
            if data.get("reports_to_one")!=lookup[mid]["parent_id"]:
                evidence["inference_results_with_wrong_reporting_parent"]+=1
            if inference.get("status")=="model_completed":
                evidence["actual_manager_AI_executions_verified"]+=1
                if inference.get("parent_id")!=lookup[mid]["parent_id"]:
                    evidence["inference_results_with_wrong_reporting_parent"]+=1
        elif rid in expected_supervisors and isinstance(data.get("leads"),list):
            seen_main.add(rid)
            if (data.get("ai_analysis") or {}).get("status")=="llm_completed":
                evidence["actual_director_and_assistant_AI_executions_verified"]+=1
    evidence["worker_reports_found"]=len(seen_worker)
    evidence["manager_reports_found"]=len(seen_manager)
    evidence["main_role_reports_found"]=len(seen_main)
    evidence["identical_worker_ai_answers"]=sum(len(x)-1 for x in worker_responses.values() if len(x)>1)
    evidence["actual_AI_executions_verified"]=sum([
        evidence["actual_worker_AI_executions_verified"],
        evidence["actual_manager_AI_executions_verified"],
        evidence["actual_director_and_assistant_AI_executions_verified"]])
    if evidence["actual_AI_executions_verified"]:
        evidence["actual_independent_model_execution_status"]="some_distinct_role_inferences_verified"
    else:
        evidence["actual_independent_model_execution_status"]="no_proven_model_inferences_in_supplied_reports"
    if evidence["identical_worker_ai_answers"]:
        warnings.append("Identical AI responses found across "+str(evidence["identical_worker_ai_answers"])+
                        " worker instances; shared model/prompt may limit real independence")
    if evidence["inference_results_with_wrong_reporting_parent"]:
        failures.append("Cloud reports violate their unique-parent reporting assignments")
    if len(seen_worker)<7500:
        warnings.append("Not all 7,500 worker identities have run in supplied cloud reports")

result={
 "audit_time_utc":datetime.now(timezone.utc).isoformat(),
 "unique_roles_configured":len(ids),
 "unique_names_configured":len(set(names)),
 "hierarchy_levels":dict(type_count),
 "companies_expected":10,
 "configured_reporting_parent_uniqueness_verified":len(failures)==0,
 "structural_independence_pass":len(failures)==0,
 "roles_are_humans":False,
 "actual_ai_independence_evidence":evidence,
 "limitations":"Distinct names and prompts are not independent living persons. Actual model inference is counted only if a completed execution report contains the successful status.",
 "issues":failures[:100],
 "warnings":warnings[:40]
}
(out/"audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
doc=["# Agent independence and reporting-flow audit","",
     f"UTC: {result['audit_time_utc']}",
     f"Distinct role IDs: {len(ids)}; unique names: {len(set(names))}; configured structural check: {'PASS' if not failures else 'FAIL'}.",
     f"Hierarchy: {type_count['director']} directors, {type_count['independent_assistant']} assistants, {type_count['manager']} managers, {type_count['worker']} workers.",
     "Each worker has one manager, each manager one director, each assistant one director, each director the owner.","",
     "## Actual cloud execution",
     f"Worker AI inferences recorded: {evidence['actual_worker_AI_executions_verified']}; manager: {evidence['actual_manager_AI_executions_verified']}; directors/assistants: {evidence['actual_director_and_assistant_AI_executions_verified']}.",
     f"Worker reports actually present: {evidence['worker_reports_found']}; manager reports: {evidence['manager_reports_found']}; director/assistant reports: {evidence['main_role_reports_found']}.",
     f"Actual independence evidence status: {evidence['actual_independent_model_execution_status']}.",
     "A model called once per role is an independently scoped inference, not a human mind, separate user account or proof of creativity.",
     "","## Integrity issues"]
doc += ["- "+x for x in failures[:35]] if failures else ["No structural hierarchy errors found."]
doc += ["","## Warnings"]+([("- "+x) for x in warnings[:20]] if warnings else ["No additional warnings."])
(out/"audit.md").write_text("\n".join(doc)+"\n",encoding="utf-8")
print("STRUCTURAL_AUDIT", "PASS" if not failures else "FAIL",len(ids),"unique IDs",len(set(names)),"unique names")
print("MODEL_EVIDENCE",evidence["actual_independent_model_execution_status"],evidence["actual_AI_executions_verified"])
if failures:
    raise SystemExit("Audit failed: "+str(len(failures))+" violations; see report")
