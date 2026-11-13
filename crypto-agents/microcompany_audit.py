"""Evidence-based audit for 1,125,000 microcompanies and 562.5m role definitions.

Proves deterministic uniqueness symbolically and checks only ACTUAL executed
worker AI reports. Never iterates through 562,500,000 potential role objects.
"""
import argparse
import csv
import json
from datetime import datetime,timezone
from pathlib import Path
from microcompany_factory import audit_definitions,verify_id,describe_micro_worker

p=argparse.ArgumentParser()
p.add_argument("--reports",default=None)
p.add_argument("--output",default="microcompany-audit")
args=p.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
static=audit_definitions()
with Path("crypto-agents/agent_registry.csv").open(newline="",encoding="utf-8") as f:
    workers=[row for row in csv.DictReader(f) if row.get("level")=="worker"]
config=json.loads(Path("crypto-agents/microcompany_structure.json").read_text(encoding="utf-8"))
errors=[]
if len(workers)!=7500:errors.append("Expected 7500 registered original worker parents")
if config["microcompanies"]!=len(workers)*150:errors.append("Bad microcompany parent count")
if config["new_employee_identities"]!=len(workers)*150*500:errors.append("Bad 500-worker per microcompany arithmetic")
if config["total_role_identities"]!=len(workers)*150*500+1132680:errors.append("Grand total identity count wrong")
registered_parent_ids={x["id"] for x in workers}
evidence={
  "reports_supplied":False,
  "micro_worker_report_files":0,
  "separate_model_inference_successes":0,
  "model_attempts_that_failed":0,
  "bad_reporting_relationships":0,
  "distinct_microcompanies_with_executed_reports":0,
  "external_social_accounts_created_by_this_factory":0,
  "verified_crypto_receipts":[],
}
if args.reports and Path(args.reports).exists():
    evidence["reports_supplied"]=True
    seen={}
    companies=set()
    for path in Path(args.reports).rglob("*.json"):
        try:obj=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,ValueError):continue
        if obj.get("level")!="microcompany_worker":continue
        rid=obj.get("id");parent=obj.get("parent_id")
        if not isinstance(rid,str) or not verify_id(rid) or not isinstance(parent,str) or not rid.startswith(parent+"-G"):
            evidence["bad_reporting_relationships"]+=1;continue
        parent_worker=parent.rsplit("-S",1)[0]
        if parent_worker not in registered_parent_ids or obj.get("company_id")!="MC-"+parent:
            evidence["bad_reporting_relationships"]+=1;continue
        seen[rid]=obj
        companies.add(parent)
    evidence["micro_worker_report_files"]=len(seen)
    evidence["distinct_microcompanies_with_executed_reports"]=len(companies)
    evidence["separate_model_inference_successes"]=sum(
        x.get("model_inference",{}).get("status")=="model_completed" for x in seen.values())
    evidence["model_attempts_that_failed"]=len(seen)-evidence["separate_model_inference_successes"]
    if evidence["bad_reporting_relationships"]:errors.append("Actual reports violate single-parent chain")
result={
   "timestamp_utc":datetime.now(timezone.utc).isoformat(),
   "structural_status":"PASS" if not errors else "FAIL",
   "parent_subagent_identities_defined":1125000,
   "new_company_identities_defined":1125000,
   "new_worker_identifiers_defined":562500000,
   "total_system_role_identifiers_defined":563632680,
   "one_parent_uniqueness_proof":static["identity_formula_and_one_parent"],
   "actual_runtime_evidence":evidence,
   "failures":errors,
   "definition_vs_reality":"The 562,500,000 are lazily defined addresses of software research roles. They are NOT actual employees, external agents or concurrently running models. Only completed inference records qualify as active AI instances."
}
(out/"audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
md=[
"# Nested microcompany and AI activity audit",
"",
f"UTC: {result['timestamp_utc']}",
f"Identity mapping & one-parent chain: **{result['structural_status']}**.",
"Defined microcompanies: **1,125,000**.",
"Defined subordinate workers: **562,500,000**.",
"Grand total defined roles: **563,632,680**.",
"",
"## Verified executed inference, not registered IDs",
f"Executed micro-worker report files: **{evidence['micro_worker_report_files']}**.",
f"Actually completed distinct micro-worker model calls: **{evidence['separate_model_inference_successes']}**.",
f"Failed/unavailable model calls: **{evidence['model_attempts_that_failed']}**.",
f"Invalid actual reporting lines: **{evidence['bad_reporting_relationships']}**.",
"",
"**No received cryptocurrency is verified by this structure audit.**",
"",
result["definition_vs_reality"]
]
(out/"AUDIT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print("MICROCOMPANY_AUDIT",json.dumps({
 "structural":result["structural_status"],"defined_microcompanies":1125000,
 "defined_workers":562500000,"actual_model_success":evidence["separate_model_inference_successes"],
 "reports_available":evidence["reports_supplied"]}))
if errors:raise SystemExit("Microcompany audit failed: "+"; ".join(errors))
