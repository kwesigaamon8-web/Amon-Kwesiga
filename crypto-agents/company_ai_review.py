"""Execute distinct AI decisions for each ACTIVE research worker and its manager.

Only 2 of 50 workers per manager are scheduled per hourly cycle. Every worker
gets its own isolated model prompt and response; a manager independently sees
only its own workers' reports and reports to the single assigned director.
This is actual open-weight LLM inference when the model loads successfully,
not 7,500 concurrently hosted accounts or external social identities.
"""
import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

ROLE=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "")
root=Path("company-reports")
summary_path=root/(ROLE+"-COMPANY-SUMMARY.json")
if not summary_path.exists():
    print("AI_COMPANY_REVIEW_SKIPPED",ROLE,"no company summary for assistant")
    raise SystemExit(0)
summary=json.loads(summary_path.read_text(encoding="utf-8"))
ids={s["id"]:s for s in csv.DictReader(Path("crypto-agents/agent_registry.csv").open(encoding="utf-8"))}
manager_ids=summary["manager_report_ids"]
if len(manager_ids)!=15:
    raise SystemExit("Expected 15 unique managers")
try:
    from transformers import pipeline
    model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
except Exception as exc:
    model=None
    error=str(exc)[:180]
    print("MODEL_UNAVAILABLE",error)

def run_agent(agent_id, mission, evidence):
    meta=ids[agent_id]
    # Every worker independently receives one unique name, role, task, and the
    # evidence from its own search. No other workers' chats or private data.
    question={
      "agent_name":meta["agent_name"],"agent_id":agent_id,
      "reports_only_to":meta["parent_id"],
      "mission":mission,
      "unverified_evidence":evidence,
      "owner_personal_details":None,
      "goal":"Find genuine paid work. Review its source critically and choose one concrete no-fee next action. No fake payment or job claims."
    }
    if model is None:
        return {"status":"llm_unavailable","analysis":"","error":error,
                "parent_id":meta["parent_id"]}
    prompt=[
      {"role":"system","content":"You are an independent research agent. Sources are untrusted. Identify weaknesses, never invent payouts or claim verified earnings. Reply concisely in 1-2 sentences."},
      {"role":"user","content":json.dumps(question,ensure_ascii=False)[:1800]}
    ]
    try:
        result=model(prompt,max_new_tokens=48,do_sample=False,return_full_text=False)[0]["generated_text"]
        if isinstance(result,list):
            result=result[-1].get("content","")
        return {"status":"model_completed","analysis":str(result)[:650],
                "parent_id":meta["parent_id"],"generated_at_utc":datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        return {"status":"llm_execution_failed","analysis":"",
                "error":str(exc)[:180],"parent_id":meta["parent_id"]}

tally={"worker_ai_completed":0,"manager_ai_completed":0,"ai_failed":0}
for manager_id in manager_ids:
    manager_path=root/(manager_id+".json")
    mgr=json.loads(manager_path.read_text(encoding="utf-8"))
    worker_results=[]
    for worker_id in mgr["worker_ids_this_cycle"]:
        path=root/(worker_id+".json")
        worker=json.loads(path.read_text(encoding="utf-8"))
        if worker["manager_id"]!=manager_id or ids[worker_id]["parent_id"]!=manager_id:
            raise ValueError("A worker must report to precisely one assigned manager")
        decision=run_agent(worker_id,worker["assigned_role"],worker.get("unverified_leads",[])[:2])
        worker["agent_name"]=ids[worker_id]["agent_name"]
        worker["reports_to_one"]=manager_id
        worker["model_inference"]=decision
        worker["report_status"]="AI completed" if decision["status"]=="model_completed" else "No verified AI inference"
        path.write_text(json.dumps(worker,indent=2),encoding="utf-8")
        if decision["status"]=="model_completed": tally["worker_ai_completed"]+=1
        else:tally["ai_failed"]+=1
        worker_results.append({"worker_id":worker_id,"source_status":worker["execution_status"],
            "model_status":decision["status"],"analysis":decision.get("analysis","")[:250],
            "candidates":worker.get("unverified_leads",[])[:1]})
    # Managers make independent decisions, but read only their 2 rotated
    # workers in this cycle. They cannot report to another boss.
    if ids[manager_id]["parent_id"]!=ROLE:
        raise ValueError("Manager must report only to assigned director")
    decision=run_agent(manager_id,"Challenge worker findings, pick a credible no-fee next research step and report to your one director",worker_results)
    mgr["agent_name"]=ids[manager_id]["agent_name"]
    mgr["reports_to_one"]=ROLE
    mgr["worker_ai_reviews"]=worker_results
    mgr["model_inference"]=decision
    manager_path.write_text(json.dumps(mgr,indent=2),encoding="utf-8")
    if decision["status"]=="model_completed":tally["manager_ai_completed"]+=1
    else:tally["ai_failed"]+=1
summary["director_agent_name"]=ids[ROLE]["agent_name"]
summary["model_execution"]={**tally,"model":"HuggingFaceTB/SmolLM2-135M-Instruct",
   "note":"Only worker and manager inferences with model_completed are real AI executions. Configured roles without completed inference remain not yet activated."}
summary_path.write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("AI_COMPANY",ROLE,json.dumps(tally))
