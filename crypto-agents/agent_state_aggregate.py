"""Aggregate completed worker checkpoints for the next independent scheduled run.

This tool runs in GitHub Actions, not under ChatGPT. It is deliberately bounded
and stores only public research metadata and next-action pointers.
"""
from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path

STATE=Path("agent-state/latest.json")
REPORTS=Path("combined-ai-processes/ai-process-reports")
MAX_WORKERS=10000
try:
    current=json.loads(STATE.read_text(encoding="utf-8"))
    workers=current.get("workers",{})
    if not isinstance(workers,dict):workers={}
except (OSError,ValueError,TypeError):
    workers={}
updated=0
failed=0
skipped=0
for manifest_path in sorted(REPORTS.glob("manifest-D??.json")):
    try:
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError):
        skipped+=1;continue
    for wid in manifest.get("worker_processes_selected",[])[:50]:
        rp=REPORTS/(str(wid)+".json")
        try:
            report=json.loads(rp.read_text(encoding="utf-8"))
        except (OSError,ValueError,TypeError):
            skipped+=1;continue
        if report.get("inference_status")!="model_completed":
            failed+=1;continue
        chk=report.get("cognitive_checkpoint") or {}
        act=report.get("activation_evidence") or {}
        if (not chk.get("next_action") or
            not act.get("unique_os_pid") or
            not chk.get("source_url")):
            skipped+=1;continue
        prior=workers.get(wid,{})
        workers[wid]={
          "last_utc":str(report.get("completed_at_utc") or "")[:55],
          "last_pid":report.get("os_process_pid"),
          "last_owner_order_sha":str((report.get("order_inheritance") or {}).get("order_registry_sha256") or "")[:80],
          "run_count":int(prior.get("run_count",0))+1,
          "model_status":"model_completed",
          "coin":str(chk.get("coin") or "")[:60],
          "source_url":str(chk.get("source_url") or "")[:240],
          "next_action":str(chk.get("next_action") or "")[:450],
          "critic_status":str(chk.get("critic_status") or "")[:50],
          "source_status":str(chk.get("public_source_status") or "")[:80],
          "report_id":str(wid)[:100],
          "currently_running":False,
          "payment_verified":False
        }
        updated+=1
workers=dict(sorted(workers.items(),key=lambda kv:kv[1].get("last_utc",""),reverse=True)[:MAX_WORKERS])
STATE.parent.mkdir(parents=True,exist_ok=True)
doc={
 "version":"independent-owner-workers-memory-v1",
 "generated_utc":datetime.now(timezone.utc).isoformat(),
 "new_finished_worker_checkpoints":updated,
 "failed_model_responses_not_recorded":failed,
 "missing_or_unusable_records":skipped,
 "stored_distinct_worker_checkpoints":len(workers),
 "continuous_live_agents_claimed":False,
 "persistence":"GitHub Actions cache save after this script; check workflow result to verify actually saved",
 "workers":workers
}
STATE.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("INDEPENDENT_AGENT_MEMORY",json.dumps({k:doc[k] for k in
 ["new_finished_worker_checkpoints","failed_model_responses_not_recorded",
 "missing_or_unusable_records","stored_distinct_worker_checkpoints"]}))
