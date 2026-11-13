"""Launch small REAL OS subprocesses from the 750 assigned W roles for one director.

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
max_workers=min(4,max(1,int(os.environ.get("REAL_AI_PROCESSES_PER_DIRECTOR","2"))))
cycle=int(time.time()//3600)
offset=(cycle*max_workers)%750
selected=[]
events=[]
for slot in range(max_workers):
    index=(offset+slot)%750
    m=index//50+1
    w=index%50+1
    wid=f"{role}-M{m:02d}-W{w:02d}"
    selected.append(wid)
    started=datetime.now(timezone.utc).isoformat()
    try:
        # This is a separate child operating-system process.
        result=subprocess.run(
            [sys.executable,"crypto-agents/ai_process_worker.py",wid],
            capture_output=True,text=True,timeout=180,check=False,
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
 "run_at_utc":datetime.now(timezone.utc).isoformat(),
 "cycle":cycle,"workers_total_assigned":750,
 "worker_processes_selected":selected,
 "subprocesses_invoked":len(events),
 "independent_worker_process_documents":sum((out/(wid+".md")).exists() for wid in selected),
 "real_model_completed":sum(r.get("inference_status")=="model_completed" for r in rows),
 "real_model_failed_or_missing":sum(r.get("inference_status")!="model_completed" for r in rows),
 "owner_orders_count":summary()["count"],
 "owner_order_register_sha256":summary()["sha256"],
 "verified_paid_crypto_receipts":[],
 "events":events,
 "truth":"Only the selected subprocesses were attempted. Other configured first-tier workers and S/G/H descendants are not concurrently hosted or reported as executed."
}
(out/("manifest-"+role+".json")).write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("REAL_WORKER_PROCESSES",role,"attempted",len(events),
      "model_completed",manifest["real_model_completed"],
      "reports",manifest["independent_worker_process_documents"],
      "defined_roles_not_running",True)
