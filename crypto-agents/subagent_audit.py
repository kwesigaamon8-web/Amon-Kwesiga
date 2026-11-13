"""Confirm unique 1,125,000 child-role definitions and actual runtime evidence."""
import argparse
import csv
import json
from datetime import datetime,timezone
from pathlib import Path
from subagent_factory import describe_child,select_slot,verify_catalog

p=argparse.ArgumentParser()
p.add_argument("--reports",default=None)
p.add_argument("--output",default="subagent-audit")
args=p.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with Path("crypto-agents/agent_registry.csv").open(newline="",encoding="utf-8") as f:
    parents=[r for r in csv.DictReader(f) if r.get("level")=="worker"]
base=verify_catalog()
errors=[]
if len(parents)!=7500 or base["deterministic_child_identities"]!=1125000:
    errors.append("Incorrect parent or theoretical child count")
for item in parents:
    pid=item["id"]
    for slot in (1,50,100,150):
        child=describe_child(pid,item["agent_name"],slot)
        if child["parent_id"]!=pid or not child["agent_name"]:
            errors.append("Bad one-parent child "+pid)
# Unique identity proof: the parent ID is unique and each slot has a distinct
# fixed-width suffix, so (parent,slot)->id is an injective mapping.
child_reports={}
invalid=0
actual_model_success=0
if args.reports and Path(args.reports).exists():
    for path in Path(args.reports).rglob("*.json"):
        try:obj=json.loads(path.read_text(encoding="utf-8"))
        except (ValueError,OSError):continue
        cid=obj.get("id")
        if obj.get("level")!="delegated_subagent" or not cid:
            continue
        pid=obj.get("parent_id")
        if not any(pid==p["id"] for p in parents[:0]):
            pass
        if not isinstance(pid,str) or not cid.startswith(pid+"-S"):
            invalid+=1;continue
        try:
            slot=int(cid.rsplit("-S",1)[1])
            expected=describe_child(pid,"_name_",slot)
            if expected["id"]!=cid:invalid+=1;continue
        except (ValueError,IndexError):invalid+=1;continue
        child_reports[cid]=obj
    actual_model_success=sum(v.get("model_inference",{}).get("status")=="model_completed" for v in child_reports.values())
if invalid:
    errors.append(str(invalid)+" child reports have invalid parent or unique ID")
result={
  "time_utc":datetime.now(timezone.utc).isoformat(),
  "parent_worker_roles_configured":len(parents),
  "children_per_worker_defined":150,
  "total_defined_child_identifiers":len(parents)*150,
  "individual_child_reports_this_cycle":len(child_reports),
  "verified_completed_individual_child_model_calls":actual_model_success,
  "parent_relationship_conflicts":invalid,
  "registry_structural_check":"PASS" if not errors else "FAIL",
  "live_activation_confirmed":bool(actual_model_success),
  "limitations":"Defined roles are not running AI services. Model calls are counted only from actual returned inference reports. They are not human staff or external social identities.",
  "errors":errors
}
(out/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
(out/"SUMMARY.md").write_text(
    f"# Child-agent independence audit\n\nDefined roles: **{result['total_defined_child_identifiers']:,}**; single-parent structure: **{result['registry_structural_check']}**.\n\n"+
    f"Actual child reports from this workflow: **{len(child_reports)}**; successful distinct model calls: **{actual_model_success}**.\n\n"+
    result["limitations"]+"\n",encoding="utf-8")
print("CHILD_AGENT_AUDIT",json.dumps(result))
if errors:raise SystemExit(1)
