"""Audit evidence from genuinely invoked independent worker OS processes."""
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

root=Path("combined-ai-processes")
reports=root/"ai-process-reports"
directors=[f"D{i:02d}" for i in range(1,11)]
summary={
 "generated_at_utc":datetime.now(timezone.utc).isoformat(),
 "directors_expected":10,
 "first_tier_worker_ids_defined":7500,
 "billion_scale_descendant_roles_are_defined_not_running":True,
 "actual_os_processes_invoked":0,
 "completed_models_with_pid_evidence":0,
 "attempts_by_level":{"W":0,"S":0,"G":0,"H":0},
 "B_broadcast_ORD033_model_completions":0,
 "ord035_individual_model_replies":0,
 "ord035_understanding_needs_review_or_failed":0,
 "ord035_invalid_command_paths":0,
 "actual_independent_model_completions":0,
 "per_agent_markdown_reports_written":0,
 "director_manifests_present":0,
 "work_assignments_recorded":0,
 "verified_wallet_receipts":[],
 "issues":[],
 "directors":[]
}
seen=set()
for d in directors:
    manifest=reports/("manifest-"+d+".json")
    work=root/"director-work-orders"/(d+".json")
    if not manifest.exists():
        summary["issues"].append("Missing process manifest: "+d)
        summary["directors"].append({"id":d,"process_manifest":"missing"})
        continue
    try:
        data=json.loads(manifest.read_text(encoding="utf-8"))
        summary["director_manifests_present"]+=1
        summary["actual_os_processes_invoked"]+=int(data.get("subprocesses_invoked",0))
        summary["actual_independent_model_completions"]+=int(data.get("real_model_completed",0))
        summary["per_agent_markdown_reports_written"]+=int(data.get("independent_worker_process_documents",0))
        selected=data.get("worker_processes_selected",[])
        for wid in selected:
            if wid in seen:summary["issues"].append("Duplicate active worker ID: "+wid)
            level="H" if "-H" in wid else "G" if "-G" in wid else "S" if "-S" in wid else "W"
            summary["attempts_by_level"][level]+=1
            record_path=reports/(wid+".json")
            if record_path.exists():
                individual=json.loads(record_path.read_text(encoding="utf-8"))
                receipt=individual.get("command_chain_understanding") or {}
                chain=individual.get("command_chain_assignment") or {}
                valid_chain=(receipt.get("role_id")==wid and chain.get("role_id")==wid and
                             receipt.get("direct_parent")==chain.get("direct_supervisor") and
                             (chain.get("owner_to_role_route") or [])[-1:]==[wid])
                if not valid_chain:
                    summary["ord035_invalid_command_paths"]+=1
                    summary["issues"].append("Invalid or missing owner-to-parent receipt: "+wid)
                if receipt.get("understanding_status") in ("model_response_has_mission_and_action","model_response_needs_parent_review"):
                    summary["ord035_individual_model_replies"]+=1
                if receipt.get("understanding_status")!="model_response_has_mission_and_action":
                    summary["ord035_understanding_needs_review_or_failed"]+=1
                if individual.get("inference_status")=="model_completed" and individual.get("os_process_pid"):
                    summary["completed_models_with_pid_evidence"]+=1
                    if individual.get("owner_broadcast_B_id")=="ORD-033" and individual.get("order_inheritance",{}).get("broadcast_B_inherited"):
                        summary["B_broadcast_ORD033_model_completions"]+=1
            seen.add(wid)
            if not (reports/(wid+".md")).exists():summary["issues"].append("Missing per-worker report: "+wid)
        if work.exists():
            content=json.loads(work.read_text(encoding="utf-8"))
            num=len(content.get("individual_first_tier_worker_assignments",[]))
            summary["work_assignments_recorded"]+=num
            if num!=750:summary["issues"].append("Expected 750 assignments for "+d+", got "+str(num))
        else:
            summary["issues"].append("Missing director work-order file for "+d)
        summary["directors"].append({
          "id":d,"processes_invoked":data.get("subprocesses_invoked",0),
          "model_completed":data.get("real_model_completed",0),
          "worker_ids":selected
        })
    except (ValueError,OSError,TypeError) as exc:
        summary["issues"].append("Invalid process data for "+d+": "+str(exc)[:180])

summary["truth"]="Configured billions of role identities are NOT billions of hosted AI processes. Count only actual children with logs and completed inference; payments must be independently verified."
Path("ai-process-summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
rows=[
 "# Real free-hosted worker AI process audit","",
 f"Director manifests present: **{summary['director_manifests_present']}/10**",
 f"Worker work orders assigned: **{summary['work_assignments_recorded']}/7,500**",
 f"Actual OS processes invoked: **{summary['actual_os_processes_invoked']}**",
 f"Actually completed independent model calls: **{summary['actual_independent_model_completions']}**",
 f"Individual documents: **{summary['per_agent_markdown_reports_written']}**",
 f"ORD-035 individual model-generated replies: **{summary['ord035_individual_model_replies']}**",
 f"ORD-035 replies needing review or retry: **{summary['ord035_understanding_needs_review_or_failed']}**",
 f"ORD-035 invalid command paths: **{summary['ord035_invalid_command_paths']}**",
 f"Completed AI with unique PID evidence: **{summary['completed_models_with_pid_evidence']}**",
 f"B=ORD-033 completed model reports: **{summary['B_broadcast_ORD033_model_completions']}**",
 f"Attempted by W/S/G/H level: **{summary['attempts_by_level']}**",
 "Confirmed new crypto deposits: **not verified by this workflow**",
 "","## Director evidence"
]
rows += [f"- {r['id']}: {r.get('processes_invoked',0)} actual attempts; {r.get('model_completed',0)} completed model inferences" for r in summary["directors"]]
rows += ["","## Limitations",summary["truth"],"","## Missing or failed evidence"]
rows += ["- "+a for a in summary["issues"]] or ["- No missing files among reported records."]
Path("ai-process-summary.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
print("AI_PROCESS_AUDIT",json.dumps({k:summary[k] for k in
 ("director_manifests_present","work_assignments_recorded","actual_os_processes_invoked",
  "actual_independent_model_completions","per_agent_markdown_reports_written")}))
