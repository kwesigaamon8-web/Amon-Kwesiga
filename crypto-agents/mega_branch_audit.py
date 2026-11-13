"""Audit 666-child mega-branch unique ID formula, reporting, and actual AI work.

No iteration over billions of roles. Identity configuration and observed role
model completion are completely separate outcomes.
"""
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
from mega_branch_factory import structural_proof,verify_branch_worker_id
from microcompany_factory import verify_id as verify_g

p=argparse.ArgumentParser()
p.add_argument("--reports",default=None)
p.add_argument("--output",default="mega-branch-audit")
a=p.parse_args()
out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
static=structural_proof()
error=[]
actual={"reports_provided":False,"distinct_H_reports":0,
        "successful_independent_model_inferences":0,"unavailable_or_failed_inferences":0,
        "different_parent_branches_observed":0,"bad_parent_paths":0,
        "verified_received_crypto_from_this_audit":[]}
if a.reports and Path(a.reports).exists():
    actual["reports_provided"]=True
    observed={}
    parents=set()
    for path in Path(a.reports).rglob("*.json"):
        try:x=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,ValueError):continue
        if x.get("level")!="mega_branch_worker":continue
        ident=x.get("id")
        parent=x.get("parent_id")
        if not isinstance(ident,str) or not isinstance(parent,str) or not verify_g(parent) or not verify_branch_worker_id(ident) or not ident.startswith(parent+"-H") or x.get("branch_id")!="BR-"+parent:
            actual["bad_parent_paths"]+=1
            continue
        observed[ident]=x
        parents.add(parent)
    actual["distinct_H_reports"]=len(observed)
    actual["different_parent_branches_observed"]=len(parents)
    actual["successful_independent_model_inferences"]=sum(x.get("model_inference",{}).get("status")=="model_completed" for x in observed.values())
    actual["unavailable_or_failed_inferences"]=len(observed)-actual["successful_independent_model_inferences"]
    if actual["bad_parent_paths"]:error.append("Misassigned child reports detected")
result={
 "at_utc":datetime.now(timezone.utc).isoformat(),
 "structure":"PASS" if not error else "FAIL",
 "branch_parent_roles_defined":static["parent_G_level_identifiers_defined"],
 "child_roles_per_branch":666,
 "new_software_role_identifiers_defined":static["unique_H_worker_identifiers_defined"],
 "grand_total_role_identifiers_defined":static["total_system_role_identifiers_defined"],
 "verified_model_runtime":actual,
 "errors":error,
 "read_this":"These are mathematical role definitions, not 374,625,000,000 active independent models, outside agents or hired people. Only completed separate actual model calls count as executed.",
 "coins_received":"No independently verified on-chain/exchange receipt is established by this structural audit."
}
(out/"audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
(out/"AUDIT.md").write_text(
 "# Branch-of-666 audit\n\n"+
 f"Hierarchy definition: **{result['structure']}**.\n\n"+
 f"Defined G-tier branch heads: **562,500,000**.\n\n"+
 f"H-tier role definitions: **374,625,000,000** (666 per branch).\n\n"+
 f"Grand total defined roles: **375,188,632,680**.\n\n"+
 f"Actual H-tier reports provided: **{actual['distinct_H_reports']}**; actual successful independent model calls: **{actual['successful_independent_model_inferences']}**.\n\n"+
 "**No cryptocurrency payment was verified by this audit.**\n\n"+result["read_this"]+"\n",
 encoding="utf-8")
print("MEGA_BRANCH_AUDIT",json.dumps({"result":result["structure"],"defined":result["new_software_role_identifiers_defined"],
"actual_model_success":actual["successful_independent_model_inferences"],"received_crypto_verified":False}))
if error:raise SystemExit("; ".join(error))
