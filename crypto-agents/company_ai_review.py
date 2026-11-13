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
from wallet_routes import private_directory_status
from friendly_pitch import warm_pitch
from datetime import datetime, timezone

ROLE=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "")
PLAYBOOK=json.loads(Path("crypto-agents/earnings_playbook.json").read_text(encoding="utf-8"))
POLICY=json.loads(Path("crypto-agents/autonomy_policy.json").read_text(encoding="utf-8"))
PUBLIC_ROUTES=json.loads(Path("crypto-agents/branch_brief.json").read_text(encoding="utf-8"))
FRIENDLY=json.loads(Path("crypto-agents/friendly_earnings_directive.json").read_text(encoding="utf-8"))
PRIVATE_ROUTE_ACCESS=private_directory_status()
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
      "freedom_to_choose":POLICY["autonomy"]["freedom_to_reject"]+" "+POLICY["autonomy"]["freedom_to_improve"],
      "where_paid_work_comes_from":list(PLAYBOOK["where_to_find_pay"].keys()),
      "earning_steps":PLAYBOOK["steps_per_candidate"][:4],
      "public_payment_route_types":list(PUBLIC_ROUTES["public_payment_routes"].keys()),
      "all_private_payment_route_ids_if_configured":PRIVATE_ROUTE_ACCESS["route_ids"],
      "private_wallet_directory_status":PRIVATE_ROUTE_ACCESS["status"],
      "unverified_evidence":evidence,
      "owner_personal_details":None,
      "goal":"Independently choose a legitimate no-fee way to earn BTC, USDC or ordinary compensation through real delivered work, and decide a concrete next step. Use a warm, respectful, truthful tone. Reject weak evidence, spam and fake earnings.",
      "friendly_communication_rules":FRIENDLY["communication_style"],
      "independent_earning_process":FRIENDLY["independent_steps"][:4],
      "never_auto_send":True
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
        worker["autonomy_policy_version"]=POLICY["version"]
        worker["wallet_directory_access"]=PRIVATE_ROUTE_ACCESS["status"]
        worker["earnings_playbook_version"]=PLAYBOOK["version"]
        worker["allowed_independent_actions"]=["choose public research focus","reject weak lead","draft evidence-based next step"]
        worker["source_model_status"]=decision["status"]
        worker["agent_name"]=ids[worker_id]["agent_name"]
        worker["reports_to_one"]=manager_id
        worker["model_inference"]=decision
        worker["friendly_reply_drafts"]=[warm_pitch(x,role=worker["assigned_role"],writer_id=worker_id) for x in worker.get("unverified_leads",[])[:2]]
        worker["outreach_activity"]="DRAFTED only; no public social-network post or payer message sent."
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
    mgr["autonomy_policy_version"]=POLICY["version"]
    mgr["wallet_directory_access"]=PRIVATE_ROUTE_ACCESS["status"]
    mgr["earnings_playbook_version"]=PLAYBOOK["version"]
    mgr["independent_authority"]="Can select or reject research leads; can propose changes; must report to assigned director only."
    mgr["agent_name"]=ids[manager_id]["agent_name"]
    mgr["reports_to_one"]=ROLE
    mgr["worker_ai_reviews"]=worker_results
    mgr["model_inference"]=decision
    mgr["friendly_reply_drafts"]=[warm_pitch(x,role="manager",writer_id=manager_id) for x in mgr.get("source_linked_candidate_examples",[])[:2]]
    mgr["reporting_handoff_to"]=ROLE
    mgr["information_shared_with_director"]=True
    manager_path.write_text(json.dumps(mgr,indent=2),encoding="utf-8")
    if decision["status"]=="model_completed":tally["manager_ai_completed"]+=1
    else:tally["ai_failed"]+=1
summary["director_agent_name"]=ids[ROLE]["agent_name"]
summary["friendly_earning_directive"]=FRIENDLY["version"]
summary["warm_drafts_prepared"]=sum(len(json.loads((root/(mid+".json")).read_text(encoding="utf-8")).get("friendly_reply_drafts",[])) for mid in manager_ids)
summary["status_report"]="Independent AI and respectful reply drafts generated only where code has actually executed. No applications, DMs or payments implied."
summary["wallet_directory_access"]=PRIVATE_ROUTE_ACCESS["status"]
summary["model_execution"]={**tally,"model":"HuggingFaceTB/SmolLM2-135M-Instruct",
   "note":"Only worker and manager inferences with model_completed are real AI executions. Configured roles without completed inference remain not yet activated."}
summary_path.write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("AI_COMPANY",ROLE,json.dumps(tally))
