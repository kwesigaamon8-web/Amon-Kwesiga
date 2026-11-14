"""Launch genuine independent W/S/G/H OS/model subprocesses from one director.

Each Python child has its own PID, individual Transformers model invocation, and
separate JSON/Markdown reports. Never spawn billions of configured roles.
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from owner_order_distribution import summary

role=os.environ.get("ROLE_ID","")
if not re.fullmatch(r"D(?:0[1-9]|10)",role):
    raise SystemExit("Expected one executing director D01..D10")
out=Path("ai-process-reports")
out.mkdir(exist_ok=True)
max_workers=min(50,max(1,int(os.environ.get("REAL_AI_PROCESSES_PER_DIRECTOR","50"))))
start_batch=time.monotonic()
max_batch_seconds=min(1200,max(60,int(os.environ.get("MAX_BATCH_SECONDS","1080"))))
cycle=int(os.getenv("GITHUB_RUN_NUMBER") or int(time.time()//3600))
offset=(cycle*max_workers)%750
activation_file=Path("director-work-orders")/(role+"-activation-plan.json")
activation_plan=json.loads(activation_file.read_text(encoding="utf-8")) if activation_file.exists() else None
planned_roles=(activation_plan or {}).get("examples_eligible_for_process_launch",[])
if activation_plan and activation_plan.get("owner_order")!="ORD-038":
    raise ValueError("Unexpected activation directive in director plan")
selected=[]
events=[]
for slot in range(max_workers):
    if time.monotonic()-start_batch>=max_batch_seconds:
        break
    # Allocate only 2 rotated high-priority activation examples. Without this
    # cap the first 20 static plan examples consume the entire daily model
    # budget and the remaining defined hierarchy never receives real inference.
    plan_priority_slots=min(2,len(planned_roles),max_workers)
    if slot<plan_priority_slots:
        wid=planned_roles[(cycle+slot)%len(planned_roles)]
    else:
        index=(offset+slot-plan_priority_slots)%750
        m=index//50+1
        w=index%50+1
        wid=f"{role}-M{m:02d}-W{w:02d}"
        level=(slot+cycle)%4
        s=(cycle+index*7)%150+1
        g=(cycle+index*17)%500+1
        h=(cycle+index*37)%666+1
        if level>=1:wid+=f"-S{s:03d}"
        if level>=2:wid+=f"-G{g:03d}"
        if level>=3:wid+=f"-H{h:03d}"
    selected.append(wid)
    started=datetime.now(timezone.utc).isoformat()
    try:
        # This is a separate child operating-system process.
        result=subprocess.run(
            [sys.executable,"crypto-agents/ai_process_worker.py",wid],
            capture_output=True,text=True,timeout=80,check=False,
            env={**os.environ,"OMP_NUM_THREADS":"2","HF_HUB_DISABLE_TELEMETRY":"1"}
        )
        status="process_terminated"
        if result.returncode!=0:
            status="process_failed"
        event={
          "worker_id":wid,"started_at_utc":started,
          "subprocess_exit_code":result.returncode,
          "subprocess_status":status,
          "subprocess_stdout_tail":result.stdout[-900:],
          "subprocess_stderr_tail":result.stderr[-1500:],
        }
    except subprocess.TimeoutExpired as exc:
        event={"worker_id":wid,"started_at_utc":started,
               "subprocess_status":"process_timed_out",
               "subprocess_error":str(exc)[:250]}
    except Exception as exc:
        event={"worker_id":wid,"started_at_utc":started,
               "subprocess_status":"launcher_error",
               "subprocess_error":str(exc)[:250]}
    record_file=out/(wid+".json")
    if record_file.exists():
        try:
            record=json.loads(record_file.read_text(encoding="utf-8"))
            event["os_pid_evidenced"]=record.get("os_process_pid")
            event["inference_status"]=record.get("inference_status")
            event["source_check_status"]=record.get("source_check_status")
            event["report_found"]=True
        except (ValueError,OSError):
            event["report_found"]=False
    else:
        event["report_found"]=False
        failure={"worker_id":wid,"model":"HuggingFaceTB/SmolLM2-135M-Instruct",
                 "inference_status":"no_model_result",
                 "source_check_status":"unknown",
                 "os_process_invoked":True,
                 "actual_execution_status":event["subprocess_status"],
                 "subprocess_error":event.get("subprocess_error") or event.get("subprocess_stderr_tail","")[:450],
                 "reported_utc":datetime.now(timezone.utc).isoformat(),
                 "verified_wallet_receipts":[]}
        record_file.write_text(json.dumps(failure,indent=2)+"\n",encoding="utf-8")
        (out/(wid+".md")).write_text(
            "# Worker process attempt — "+wid+"\n\n"
            "Status: "+event["subprocess_status"]+"\n\n"
            "No completed AI model inference was verified. No payment received was verified.\n",
            encoding="utf-8")
    events.append(event)

rows=[json.loads((out/(wid+".json")).read_text(encoding="utf-8")) for wid in selected]
manifest={
 "director_id":role,
 "workforce_namespace":os.environ.get("WORKFORCE_ID","transferexperiment"),
 "globally_unique_worker_ids":[os.environ.get("WORKFORCE_ID","transferexperiment")+"/"+wid for wid in selected],
 "run_at_utc":datetime.now(timezone.utc).isoformat(),
 "cycle":cycle,"workers_total_assigned":750,
 "director_activation_plan_used":bool(planned_roles),
 "activation_examples_rotated":min(2,len(planned_roles),max_workers),
 "other_workers_rotating_through_W_S_G_H":True,
 "strict_accountability_authority":"chief_D_owner_orders.json",
 "activation_plan_cycle":(activation_plan or {}).get("selection_run_cycle"),
 "max_worker_processes_per_director":max_workers,
 "batch_time_budget_seconds":max_batch_seconds,
 "process_attempts_skipped_due_to_budget":max_workers-len(events),
 "worker_processes_selected":selected,
 "subprocesses_invoked":len(events),
 "independent_worker_process_documents":sum((out/(wid+".md")).exists() for wid in selected),
 "real_model_completed":sum(r.get("inference_status")=="model_completed" for r in rows),
 "real_model_failed_or_missing":sum(r.get("inference_status")!="model_completed" for r in rows),
 "owner_orders_count":summary()["count"],
 "owner_order_register_sha256":summary()["sha256"],
 "verified_paid_crypto_receipts":[],
 "events":events,
 "truth":"Only the selected W/S/G/H OS subprocesses were attempted; other defined roles are not concurrently hosted or reported as executed."
}
(out/("manifest-"+role+".json")).write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("REAL_WORKER_PROCESSES",role,"attempted",len(events),
      "model_completed",manifest["real_model_completed"],
      "reports",manifest["independent_worker_process_documents"],
      "defined_roles_not_running",True)
