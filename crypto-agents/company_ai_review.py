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
from subagent_factory import describe_child, select_slot
from microcompany_factory import describe_micro_worker, select_micro_worker_slot
from mega_branch_factory import describe_branch_worker, rotating_slot
from understanding_response import understanding_report, BRIEF
from capability_engine import capability_review, short_model_context, PACK as CAPABILITY_PACK
from datetime import datetime, timezone

ROLE=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "")
PLAYBOOK=json.loads(Path("crypto-agents/earnings_playbook.json").read_text(encoding="utf-8"))
POLICY=json.loads(Path("crypto-agents/autonomy_policy.json").read_text(encoding="utf-8"))
PUBLIC_ROUTES=json.loads(Path("crypto-agents/branch_brief.json").read_text(encoding="utf-8"))
FRIENDLY=json.loads(Path("crypto-agents/friendly_earnings_directive.json").read_text(encoding="utf-8"))
OWNER_COMMAND=json.loads(Path("crypto-agents/owner_command_chain.json").read_text(encoding="utf-8"))
SHARED=json.loads(Path("crypto-agents/shared_understanding.json").read_text(encoding="utf-8"))
TOOL_ECOSYSTEM=json.loads(Path("crypto-agents/tool_ecosystem.json").read_text(encoding="utf-8"))
TOOL_REPORT_PATH=Path("tool-reports")/(ROLE+".json")
TOOL_REPORT=json.loads(TOOL_REPORT_PATH.read_text(encoding="utf-8")) if TOOL_REPORT_PATH.exists() else {"status":"not_run","new_tool_candidates":[]}
TOOL_EVIDENCE=[{"name":x.get("name","")[:75],"url":x.get("url","")[:160],
                "status":x.get("status","unverified")} for x in TOOL_REPORT.get("new_tool_candidates",[])[:2]]
COMPANY=json.loads(Path("crypto-agents/company_hierarchy.json").read_text(encoding="utf-8"))
MANAGER_GOALS={m["id"]:m["domain"] for c in COMPANY["companies"] for m in c["managers"]}
CYCLE=int(datetime.now(timezone.utc).timestamp()//3600)
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

def run_agent(agent_id, mission, evidence, meta_override=None):
    meta=meta_override if meta_override is not None else ids[agent_id]
    # Every worker independently receives one unique name, role, task, and the
    # evidence from its own search. No other workers' chats or private data.
    director_id=agent_id[:3]
    manager_id=agent_id.split("-W")[0] if "-W" in agent_id else agent_id
    understanding=SHARED["owner_intent"]
    leadership=SHARED["assistant_method_the_directors_should_understand"]
    capabilities=capability_review(agent_id, meta['parent_id'], mission, evidence, TOOL_EVIDENCE)
    question={
      "professional_context":BRIEF["whom_you_work_for"]["description"]+" "+BRIEF["whom_you_work_for"]["commercial_advantage"],
      "you_must_answer_in_your_own_words":"Who you serve professionally, your specific role and ONE supervisor, concrete research next action, exact proof of cryptocurrency credited, and any unknowns. Do not merely repeat the instruction.",
      "owner_goal":understanding["real_goal"],
      "standing_owner_order":SHARED["owner_order_cascade"]["id"],
      "capability_order":"ORD-026",
      "independent_role_order":"ORD-027",
      "freedom_to_choose_work":"ORD-029",
      "broadcast_B_id":"ORD-033",
      "broadcast_B_directive":SHARED["universal_broadcast_B"],
      "free_independent_research":SHARED["owner_intent"]["agent_freedom"],
      "capability_method_ids":[c["id"] for c in CAPABILITY_PACK["implemented_capabilities"]],
      "independent_capability_assessment":capabilities,
      "additional_owner_order":"ORD-022",
      "render_network_order":"ORD-028",
      "render_outbound_source_ip_context":SHARED.get("render_network_instructions",{}),
      "independence_order":"ORD-023",
      "immediate_independent_work":SHARED["owner_intent"]["immediate_independent_execution"],
      "autonomy_scope":POLICY["immediate_independent_execution"]["autonomous_without_reasking"],
      "tools_and_sites_improvement":SHARED["owner_intent"]["tool_improvement"],
      "tools_and_sites_discovered_read_only":TOOL_EVIDENCE,
      "new_site_or_tool_use_rule":"Evaluate new sites/models and improve paid-work discovery. Only public permitted read-only tools or authenticated approved integrations; never claim access/installation or received funds without evidence.",
      "inherited_owner_instruction":SHARED["owner_intent"]["worldwide"],
      "order_chain_to_last_worker":SHARED["owner_order_cascade"]["chain"],
      "payment_routing_reference":SHARED["owner_order_cascade"]["payment_routes"],
      "SUCCESS_ONLY": "Confirmed genuine cryptocurrency received by owner's approved exact-network receiving address. All other activity is NOT earnings.",
      "director":director_id,
      "director_strategy":SHARED["director_mandates"].get(director_id,"Find verified real crypto-paid work"),
      "method":leadership["reasoning"],
      "check":leadership["success_test"],
      "one_boss":meta["parent_id"],
      "manager_focus":MANAGER_GOALS.get(manager_id,"challenge evidence and share verified source links"),
      "agent_id":agent_id,
      "cascade_last_tier":"H-level branch worker is included and must receive ORD-021 if activated",
      "individual_role":mission,
      "source_evidence_untrusted":evidence,
      "task":"Independently judge whether REAL work is likely to be paid in genuine transferable cryptocurrency sent to the owner's correct approved address. Return short reasoning, specific next step and unknowns. Do not invent received coins."
    }
    if model is None:
        return {"status":"llm_unavailable","analysis":"","error":error,
                "parent_id":meta["parent_id"],"capability_assessment":capabilities}
    prompt=[
      {"role":"system","content":"OWNER B=ORD-033 BROADCAST applies to EVERY D/A/M/W/S/G/H role, including final H workers; independently FIND genuine paid cryptocurrency opportunities and submit a distinct evidenced report. OWNER ORD-021 through ORD-033 apply to EVERY activated level, including final H branch workers: when you receive the owner's instruction, proceed INDEPENDENTLY without another prompt on all already authorized source research, permitted tool uses, evidence checks, reviews and reporting to your one boss; if a source fails try a different permitted one and report proof of your work. Independently discover and assess other research sites, tools and public AI models to improve verified paid-work research, using only permitted read-only or explicitly authorized functionality. Report actual tested utility, costs, unknowns, and when connection is needed. Independently research WORLDWIDE for legitimate real paid work across any practical field, verify genuine payer, deliverable, no upfront fee, eligibility, and matching owner-approved cryptocurrency receiving network. Seek real completed work and verified coin deposits; leads, drafts and account names are NOT received coins. Report to exactly one parent; challenge weak sources; never invent transfers, send bulk unsolicited messages or share keys. Reply concisely."},
      {"role":"user","content":json.dumps({"agent_id":agent_id,"one_boss":meta["parent_id"],
        "independent_task":str(mission)[:220],
        "orders":["ORD-021","ORD-022","ORD-023","ORD-024","ORD-025","ORD-026","ORD-027","ORD-028","ORD-029","ORD-030","ORD-031","ORD-032","ORD-033"],
        "B_broadcast_instruction":"B=ORD-033: independently identify evidence-backed legal ways to earn real transferable crypto; report unique source, payer, deliverable, eligible token/network, risk and next action; only actual model execution is counted.",
        "render_network":"Shared Render source egress CIDRs 74.220.48.0/24 and 74.220.56.0/24, NOT destination endpoints. Never scan them. Verify authorized provider hostnames.",
        "independent_method":"You are FREE to choose your own legal research task, website and next permitted action without waiting for supervisor approval; use your own judgment and evidence, then report it. Never copy another agent's conclusion as your own.",
        "capability_review":short_model_context(capabilities),
        "instruction":"Briefly plan, independently evaluate, identify risk and next permitted action; every activated role needs its own document. Do not invent transfers."},
        ensure_ascii=False)[:1800]}
    ]
    try:
        result=model(prompt,max_new_tokens=85,do_sample=False,return_full_text=False)[0]["generated_text"]
        if isinstance(result,list):
            result=result[-1].get("content","")
        return {"status":"model_completed","analysis":str(result)[:650],
                "parent_id":meta["parent_id"],"generated_at_utc":datetime.now(timezone.utc).isoformat(),
                "capability_pack_version":CAPABILITY_PACK["version"],"capability_assessment":capabilities}
    except Exception as exc:
        return {"status":"llm_execution_failed","analysis":"",
                "error":str(exc)[:180],"parent_id":meta["parent_id"],"capability_assessment":capabilities}

tally={"worker_ai_completed":0,"manager_ai_completed":0,"subagent_ai_completed":0,"subagent_roles_activated":0,"micro_worker_model_completed":0,"micro_worker_inference_attempted":0,"H_branch_model_completed":0,"H_branch_model_attempted":0,"ai_failed":0}
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
        worker["shared_understanding_version"]=SHARED["version"]
        worker["director_objective"]=SHARED["director_mandates"].get(ROLE,"")
        worker["owner_coin_only_goal"]=SHARED["owner_intent"]["real_goal"]
        worker["agent_name"]=ids[worker_id]["agent_name"]
        worker["reports_to_one"]=manager_id
        worker["model_inference"]=decision
        worker["understanding_response"]=understanding_report(worker_id,ids[worker_id]["agent_name"],manager_id,
            worker["assigned_role"],decision,[x.get("url") for x in worker.get("unverified_leads",[])[:2]])
        worker["friendly_reply_drafts"]=[warm_pitch(x,role=worker["assigned_role"],writer_id=worker_id) for x in worker.get("unverified_leads",[])[:2]]
        worker["outreach_activity"]="DRAFTED only; no public social-network post or payer message sent."
        worker["report_status"]="AI completed" if decision["status"]=="model_completed" else "No verified AI inference"
        selected=select_slot(worker_id,CYCLE)
        child=describe_child(worker_id,ids[worker_id]["agent_name"],selected)
        if child["parent_id"]!=worker_id:
            raise ValueError("Subagent reports to an incorrect worker")
        child_decision=run_agent(child["id"],child["objective"],
            worker.get("unverified_leads",[])[:1],
            meta_override={"agent_name":child["agent_name"],"parent_id":worker_id})
        child["shared_understanding_version"]=SHARED["version"]
        child["director_objective"]=SHARED["director_mandates"].get(ROLE,"")
        child["owner_coin_only_goal"]=SHARED["owner_intent"]["real_goal"]
        child["model_inference"]=child_decision
        child["understanding_response"]=understanding_report(child["id"],child["agent_name"],worker_id,
            child["objective"],child_decision,child.get("source_evidence_urls",[]))
        child["status"]="model_completed" if child_decision["status"]=="model_completed" else "not_verified_active_AI"
        child["source_evidence_urls"]=[x["url"] for x in worker.get("unverified_leads",[])[:1] if x.get("url","").startswith("https://")]
        child["real_payments_verified"]=[]
        (root/(child["id"]+".json")).write_text(json.dumps(child,indent=2),encoding="utf-8")
        tally["subagent_roles_activated"]+=1
        if child_decision["status"]=="model_completed":tally["subagent_ai_completed"]+=1
        else:tally["ai_failed"]+=1
        # The child subagent is the head of one deterministically defined 500-worker
        # microcompany. Rotate just one of its workers each actual parent cycle.
        # This is a bounded separate inference, NOT 500 independent cloud agents.
        micro_slot=select_micro_worker_slot(child["id"],CYCLE)
        micro=describe_micro_worker(child["id"],child["agent_name"],micro_slot)
        if micro["parent_id"]!=child["id"]:
            raise ValueError("Micro-worker must report exclusively to its subagent head")
        micro_decision=run_agent(micro["id"],micro["independent_research_objective"],
            worker.get("unverified_leads",[])[:1],
            meta_override={"agent_name":micro["name"],"parent_id":child["id"]})
        micro["model_inference"]=micro_decision
        micro["understanding_response"]=understanding_report(micro["id"],micro["name"],child["id"],
            micro["independent_research_objective"],micro_decision,[x.get("url") for x in worker.get("unverified_leads",[])[:1]])
        micro["role_execution_status"]="model_completed" if micro_decision["status"]=="model_completed" else "not_verified_active_AI"
        micro["research_source_urls"]=[x["url"] for x in worker.get("unverified_leads",[])[:1] if x.get("url","").startswith("https://")]
        micro["external_outreach_sent"]=False
        micro["paid_contracts_verified"]=[]
        micro["cryptocurrency_receipts_verified"]=[]
        (root/(micro["id"]+".json")).write_text(json.dumps(micro,indent=2),encoding="utf-8")
        tally["micro_worker_inference_attempted"]+=1
        if micro_decision["status"]=="model_completed":
            tally["micro_worker_model_completed"]+=1
        else:
            tally["ai_failed"]+=1
        # Each active G-level micro-worker defines a separate branch of 666
        # differently specialized H-level researcher roles. A single H-level
        # model call is attempted ONLY when the parent G-level call completed.
        micro["configured_H_branch_roles"]=666
        micro["H_branch_head_id"]=micro["id"]
        if micro_decision["status"]=="model_completed":
            hslot=rotating_slot(micro["id"],CYCLE)
            hchild=describe_branch_worker(micro["id"],micro["name"],hslot)
            if hchild["parent_id"]!=micro["id"]:
                raise ValueError("H-level worker must report to exactly one G parent")
            hdecision=run_agent(hchild["id"],hchild["mission"],
                worker.get("unverified_leads",[])[:1],
                meta_override={"agent_name":hchild["name"],"parent_id":micro["id"]})
            hchild["model_inference"]=hdecision
            hchild["understanding_response"]=understanding_report(hchild["id"],hchild["name"],micro["id"],
                hchild["mission"],hdecision,[x.get("url") for x in worker.get("unverified_leads",[])[:1]])
            hchild["actual_inference_status"]=hdecision["status"]
            hchild["source_links"]=[x["url"] for x in worker.get("unverified_leads",[])[:1] if x.get("url","").startswith("https://")]
            hchild["verified_cryptocurrency_receipts"]=[]
            hchild["messages_sent"]=False
            (root/(hchild["id"]+".json")).write_text(json.dumps(hchild,indent=2),encoding="utf-8")
            tally["H_branch_model_attempted"]+=1
            if hdecision["status"]=="model_completed":
                tally["H_branch_model_completed"]+=1
            else:
                tally["ai_failed"]+=1
            micro["H_branch_sampled_child_id"]=hchild["id"]
            micro["H_branch_sampled_inference_status"]=hdecision["status"]
        else:
            micro["H_branch_sampled_child_id"]=None
            micro["H_branch_runtime_note"]="G-level parent inference did not complete; no child model call attempted."
        (root/(micro["id"]+".json")).write_text(json.dumps(micro,indent=2),encoding="utf-8")
        child["microcompany_id"]=micro["company_id"]
        child["microcompany_configured_staff"]=500
        child["activated_micro_worker_id"]=micro["id"]
        child["micro_worker_model_status"]=micro["role_execution_status"]
        (root/(child["id"]+".json")).write_text(json.dumps(child,indent=2),encoding="utf-8")
        worker["delegated_subagent_id"]=child["id"]
        worker["delegated_subagent_status"]=child["status"]
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
    mgr["shared_understanding_version"]=SHARED["version"]
    mgr["director_objective"]=SHARED["director_mandates"].get(ROLE,"")
    mgr["owner_coin_only_goal"]=SHARED["owner_intent"]["real_goal"]
    mgr["agent_name"]=ids[manager_id]["agent_name"]
    mgr["reports_to_one"]=ROLE
    mgr["worker_ai_reviews"]=worker_results
    mgr["model_inference"]=decision
    mgr["understanding_response"]=understanding_report(manager_id,ids[manager_id]["agent_name"],ROLE,
        "Supervise and independently verify 50 specialist workers",decision,[x.get("url") for x in mgr.get("source_linked_candidate_examples",[])[:2]])
    mgr["friendly_reply_drafts"]=[warm_pitch(x,role="manager",writer_id=manager_id) for x in mgr.get("source_linked_candidate_examples",[])[:2]]
    mgr["reporting_handoff_to"]=ROLE
    mgr["information_shared_with_director"]=True
    manager_path.write_text(json.dumps(mgr,indent=2),encoding="utf-8")
    if decision["status"]=="model_completed":tally["manager_ai_completed"]+=1
    else:tally["ai_failed"]+=1
summary["shared_understanding_version"]=SHARED["version"]
summary["tool_improvement_standing_order"]="ORD-022"
summary["independent_after_owner_order"]="ORD-023"
summary["agent_independence_order"]="ORD-027"
summary["capability_pack_version"]=CAPABILITY_PACK["version"]
summary["active_worker_independent_actions"]="Read-only research, evaluation, evidence, draft and one-parent report within existing capabilities; external authorization not implied"
summary["external_tools_discovered_this_cycle"]=len(TOOL_REPORT.get("new_tool_candidates",[]))
summary["external_tools_actually_installed_or_connected"]=0
summary["tool_research_report_status"]="generated" if TOOL_REPORT_PATH.exists() else "missing"
summary["owner_professional_brief_version"]=BRIEF["version"]
summary["understanding_reports_collected"]="Only model-generated reports from activated workers, managers, S/G/H workers; dormant roles are not counted."
summary["owner_coin_only_goal"]=SHARED["owner_intent"]["real_goal"]
summary["director_objective"]=SHARED["director_mandates"].get(ROLE,"")
summary["director_agent_name"]=ids[ROLE]["agent_name"]
summary["owner_command_chain_version"]=OWNER_COMMAND["version"]
summary["configured_delegation_per_worker"]=150
summary["subagent_model_checks_this_cycle"]=tally["subagent_roles_activated"]
summary["subagent_model_successes_this_cycle"]=tally["subagent_ai_completed"]
summary["microcompany_count_configured_beneath_company"]=750*150
summary["microcompany_worker_roles_configured_beneath_company"]=750*150*500
summary["micro_worker_model_attempts_this_cycle"]=tally["micro_worker_inference_attempted"]
summary["micro_worker_model_successes_this_cycle"]=tally["micro_worker_model_completed"]
summary["H_tier_branches_configured_under_company"]=750*150*500
summary["H_tier_workers_defined_under_company"]=750*150*500*666
summary["H_tier_inferences_attempted_this_cycle"]=tally["H_branch_model_attempted"]
summary["H_tier_successful_model_inferences_this_cycle"]=tally["H_branch_model_completed"]
summary["grandchildren_proof_status"]="Attempted independent model calls are distinguished from completed inferences, configured identities and real cryptocurrency receipts."
summary["friendly_earning_directive"]=FRIENDLY["version"]
summary["warm_drafts_prepared"]=sum(len(json.loads((root/(mid+".json")).read_text(encoding="utf-8")).get("friendly_reply_drafts",[])) for mid in manager_ids)
summary["status_report"]="Independent AI and respectful reply drafts generated only where code has actually executed. No applications, DMs or payments implied."
summary["wallet_directory_access"]=PRIVATE_ROUTE_ACCESS["status"]
summary["model_execution"]={**tally,"model":"HuggingFaceTB/SmolLM2-135M-Instruct",
   "note":"Only worker and manager inferences with model_completed are real AI executions. Configured roles without completed inference remain not yet activated."}
summary_path.write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("AI_COMPANY",ROLE,json.dumps(tally))
