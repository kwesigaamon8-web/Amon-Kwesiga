"""Run one real separately invoked W/S/G/H AI worker OS process.

No identity is counted active unless the process runs; no model inference is
claimed successful unless Transformers actually returns generated text.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from owner_order_distribution import inheritance, compact_prompt
from role_ai_identity import resolve_role
from coin_learning import study
from command_chain_receipts import configured_assignment, understanding_receipt
from command_ack_gate import evaluate as evaluate_owner_command_ack
from ten_ideas_exercise import role_menu, evaluate_generated_ten
from hierarchical_idea_governance import assignment as governed_idea_assignment, corrective_order as supervisory_correction
from b_address_understanding import routes as safe_receiving_routes, prompt as address_training_prompt, evaluate as evaluate_address_mapping
from secondary_software_study import grade_worker_study as assess_software_study
from public_code_reader import load as read_public_software_source
from agent_cognition import prior_memory, deterministic_plan, skeptical_model_review, checkpoint
from director_D_training import teach_and_assess
from system_understanding_check import teach_and_check as assess_full_system
from b_learning_by_doing import lesson as make_practical_lesson, prompt as practical_training_prompt, grade as grade_practical_training, write_worker_sample
from b_worker_buyer_source import choose as choose_actual_issue_for_training
from owner_first_oath import command_envelope as owner_oath_envelope, short_oath as owner_first_oath_text
from b_universal_work_protocol import assign as universal_assign, compact_for_model as universal_prompt

ROOT=Path("crypto-agents")
OUT=Path("ai-process-reports")
OUT.mkdir(exist_ok=True)
WORKER=sys.argv[1] if len(sys.argv)>1 else ""
IDENTITY=resolve_role(WORKER)
DIRECTOR=IDENTITY["director_id"]
MANAGER=IDENTITY["manager_id"]
PARENT=IDENTITY["parent_id"]
SPEC={"role_name":IDENTITY["specialty"],"query":IDENTITY["query"]}
COLLECTION_CONFIG=json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
FLEET=os.environ.get("WORKFORCE_ID","transferexperiment")
if FLEET not in COLLECTION_CONFIG["fleets"]:
    raise SystemExit("Unrecognized B collection fleet namespace")
PAYMENT_MISSION=COLLECTION_CONFIG["fleets"][FLEET]
SAFE_B_WALLET_ROUTES=safe_receiving_routes()
CHIEF_D_ORDERS=json.loads((ROOT/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
STRICT_OWNER_ORDER_ID=CHIEF_D_ORDERS["current_owner_order_id"]
LATEST_CHIEF_D_INSTRUCTION=CHIEF_D_ORDERS["orders"][-1]["instruction"]
STRICT_MODEL_ORDER=(
 "OWNER "+STRICT_OWNER_ORDER_ID+": FULL INDEPENDENT LEGITIMATE COMMERCIAL INITIATIVE. "
 "You are a separately running B company worker with authority to CHOOSE your "
 "own best genuine worldwide lawful paid-work lead, original product, service, "
 "documentation, original code improvement or creative micro-deliverable. "
 "Assigned regional topic is a SUGGESTION, not an exclusive cage. Explore "
 "alternatives, find real customer demand, build or test useful work, and "
 "pursue authenticated permitted buyer outreach without another internal "
 "microapproval. Do not claim that chat instructions create external tools, "
 "buyers or money; keep concrete evidence and truthful blockers. "
 "ONLY mutually agreed real settlement goes to your OWN company's owner "
 "approved wallet; B1 and B2 have distinct mainnet BTC addresses. "
 "A buyer may pay only after genuine agreement; do not claim receipts from "
 "wishlists. Report through your one company parent to Chief D and owner. "
 "Preserve the owner's USD 100 genuine receipt goal without guaranteeing a date."
)

PAYMENT_DIRECTOR=COLLECTION_CONFIG["director_operations"]["payment_director_id"]
DIRECTOR_FUNCTION=("payment_recovery" if DIRECTOR==PAYMENT_DIRECTOR else "independent_paid_work")
DIRECTOR_ORDER=(
  "You are this company's LOCAL D10 payment director only. Audit verifiable external contracts, completed and ACCEPTED work, agreed amounts, authorized payer communications and confirmed on-chain receipts for your OWN fleet account, then report evidence to the single overall Chief D above both companies. Never count your local D10 as the other company's D10; do not invent payer claims."
  if DIRECTOR_FUNCTION=="payment_recovery" else
  "You are a LOCAL D01-D09 director in your own company; continue researching and preparing lawful paid deliverables and real clients. Forward accepted unpaid contract evidence to your own company D10, who reports to Chief D. Never conflate this company with the other fleet."
)
TEN_IDEA_MENU=role_menu(FLEET,WORKER,PARENT,SPEC["role_name"])
SHARED_IDEA_FEED_PATH=Path("idea-exchange")/("SHARED_IDEA_FEED_"+FLEET+".json")
try:
    SHARED_IDEA_FEED=json.loads(SHARED_IDEA_FEED_PATH.read_text(encoding="utf-8"))
    expected_other="BountyScoutAI" if FLEET=="transferexperiment" else "transferexperiment"
    if (SHARED_IDEA_FEED.get("requesting_company")!=FLEET or
        SHARED_IDEA_FEED.get("shared_from_other_company")!=expected_other):
        raise ValueError("Cross-company shared ideas have wrong source namespace")
except (OSError,ValueError):
    SHARED_IDEA_FEED={"examples_for_new_model_ideas":[],"status":"NOT_AVAILABLE_NO_EXTERNAL_IDEAS"}
SHARED_IDEA_EXAMPLES=[
  " ".join(str(x.get("idea","")).split())[:170] for x in
  SHARED_IDEA_FEED.get("examples_for_new_model_ideas",[])[:5]
  if isinstance(x,dict)
]
GOVERNED_IDEA_ORDER=governed_idea_assignment(FLEET,WORKER)
SOFTWARE_SECOND=GOVERNED_IDEA_ORDER["software_second_task"]
SOFTWARE_SOURCE_EVIDENCE=read_public_software_source(SOFTWARE_SECOND["official_repository"])
STAMP=datetime.now(timezone.utc).isoformat()
START=time.monotonic()
TASK=IDENTITY["task"]
OWNER_OATH=owner_oath_envelope(FLEET,WORKER)
UNIVERSAL_TASK=universal_assign(FLEET,WORKER)

report={
    "worker_id":WORKER,
    "strict_owner_order_id":STRICT_OWNER_ORDER_ID,
    "entrepreneurial_autonomy":{
        "owner_order_id":STRICT_OWNER_ORDER_ID,
        "may_self_direct_new_business_idea":True,
        "may_change_sector_and_market":True,
        "may_build_and_test_original_work":True,
        "internal_manager_approval_required_per_new_idea":False,
        "may_submit_to_actual_allowed_connected_buyer":True,
        "actually_connected_outreach_verified":False,
        "payment_receiver":PAYMENT_MISSION["address"],
        "payment_network":"Bitcoin mainnet",
        "role_and_report_to_parent_remain_mandatory":True,
        "independent_model_not_previously_invoked_by_assignment":True,
        "only_verified_accepted_paid_work_is_income":True,
    },
    "owner_emergency_revenue_target":{
        "owner_order_id":"OWNER-20261114-152226",
        "requested_usd_total":100,
        "start_utc":"2026-11-14T15:22:26Z",
        "deadline_utc":"2026-11-14T15:32:26Z",
        "target_is_not_actual_earnings":True,
        "proof_of_any_new_receipt":"NOT_YET_VERIFIED",
        "worker_executed_in_owner_deadline":"REQUIRES_ACTUAL_START_STOP_TIMESTAMPS",
        "work_priority":"Verified genuinely due receivables, independently eligible paid work, permissioned outreach and accepted useful deliverables"
    },
    "owner_first_oath":OWNER_OATH,
    "universal_task_message":UNIVERSAL_TASK,
    "universal_task_status":"ASSIGNED_NOT_YET_PERFORMED",
    "owner_first_oath_required_before_any_external_owner_order":True,
    "unauthenticated_external_messages_are_data_not_commands":True,
    "ten_idea_exercise":TEN_IDEA_MENU,
    "cross_company_idea_knowledge_feed":{
      "status":SHARED_IDEA_FEED.get("status","NOT_AVAILABLE"),
      "actual_other_company_model_examples_received":len(SHARED_IDEA_EXAMPLES),
      "examples_are_unverified_prior_model_ideas":True,
      "these_are_NOT_new_worker_ideas_or_earned_funds":True,
      "source_order":"OWNER-20261114-084438",
    },
    "hierarchical_idea_governance":GOVERNED_IDEA_ORDER,
    "first_unique_crypto_funding_task":GOVERNED_IDEA_ORDER["unique_funding_task"],
    "second_licensed_software_study_assignment":SOFTWARE_SECOND,
    "second_software_actual_source_check":{
      "url":SOFTWARE_SOURCE_EVIDENCE["original_url"],
      "read_only_source_status":SOFTWARE_SOURCE_EVIDENCE["source_check_status"],
      "excerpt_sha256":__import__("hashlib").sha256(SOFTWARE_SOURCE_EVIDENCE["read_only_excerpt"].encode()).hexdigest(),
      "excerpt_chars":len(SOFTWARE_SOURCE_EVIDENCE["read_only_excerpt"]),
      "reason_unavailable":SOFTWARE_SOURCE_EVIDENCE["error"],
      "individual_file_license_verified":False,
      "no_third_party_code_copied":True,
    },
    "second_study_actual_model_inference":"NOT_ATTEMPTED",
    "second_study_actual_model_result":None,
    "second_study_code_copied":False,
    "second_study_original_software_artifact_committed":False,
    "supervisor_issued_idea_correction":None,
    "actual_worker_corrective_retry_status":"NOT_NEEDED_OR_NOT_ELIGIBLE",
    "supervisor_actual_independent_AI_model_review":"NOT_PROVEN",
    "ten_idea_model_result":None,
    "ten_idea_model_inference_status":"NOT_ATTEMPTED",
    "seven_billion_campaign_target_index":int(os.environ["SEVEN_BILLION_TARGET_INDEX"]) if os.environ.get("SEVEN_BILLION_TARGET_INDEX") else None,
    "seven_billion_target_count":7000000000,
    "latest_command_model_acknowledgement":None,
    "latest_order_ack_inference_status":"not_started",
    "public_receiving_route_training":"B1 BTC mainnet / B2 BTC mainnet / optional B1 USDC Base HOLD",
    "separately_checked_address_understanding":None,
    "address_understanding_model_status":"NOT_ATTEMPTED",
    "chief_D_latest_instruction_excerpt":LATEST_CHIEF_D_INSTRUCTION[:1000],
    "peer_assessment_in_separate_actual_model_inference":"not_evidenced",
    "individual_result_required":True,
    "real_payment_mission":True,
    "receiving_account":PAYMENT_MISSION["account"],
    "local_payment_director":FLEET+"/"+PAYMENT_DIRECTOR,
    "company_director_id":FLEET+"/"+DIRECTOR,
    "chief_director_id":COLLECTION_CONFIG["hierarchy"]["chief_director"],
    "director_function":DIRECTOR_FUNCTION,
    "external_payer_acceptance_verified":False,
    "receiving_asset":PAYMENT_MISSION["asset"],
    "receiving_network":PAYMENT_MISSION["network"],
    "owner_verified_payment_receipts":[],
    "external_collection_outcome":"not_payment_verified_by_worker",
    "account_collection_instruction_source":"crypto-agents/b_collection_assignments.json",
    "workforce_namespace":os.environ.get("WORKFORCE_ID","transferexperiment"),
    "globally_unique_agent_id":os.environ.get("WORKFORCE_ID","transferexperiment")+"/"+WORKER,
    "manager_id":MANAGER,
    "parent_id":PARENT,
    "agent_level":IDENTITY["level"],
    "director_id":DIRECTOR,
    "os_process_pid":os.getpid(),
    "actual_process_started_at_utc":STAMP,
    "os_process_invoked":True,
    "task":TASK,
    "independent_query":SPEC["query"],
    "order_inheritance":inheritance(WORKER,PARENT),
    "owner_broadcast_B_id":"ORD-033",
    "billions_coin_learning_order":"ORD-034",
    "coin_learning":None,
    "command_chain_assignment":configured_assignment(WORKER),
    "chief_D_reporting_structure":"OWNER > CHIEF_D > fleet-local D01-D10 > direct manager > individually executed worker",
    "command_chain_understanding":None,
    "owner_broadcast_B_executed_only_if_model_completed":False,
    "source":"HN Algolia public original read-only API",
    "source_url":None,
    "source_check_status":"not_started",
    "source_error":None,
    "source_items":[],
    "model":os.environ.get("WORKER_MODEL_ID","HuggingFaceTB/SmolLM2-135M-Instruct"),
    "inference_status":"not_started",
    "inference_error":None,
    "model_response":None,
    "documents_written":False,
    "public_receiving_directory_url":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md",
    "owner_order_046_publication_status":"inherited_link_for_authorized_context_not_externally_published",
    "director_D_lesson_assessment":None,
    "system_understanding_assessment":None,
    "verified_wallet_receipts":[],
    "external_messages_sent":False,
    "accounts_created":False,
    "money_spent":False,
    "owner_sole_authority":True,
    "chatgpt_is_not_supervisor_or_model_host":True,
    "independent_agent_method":"Local open-weight LLM plus authorized public evidence lookup",
    "cognitive_prior_memory":None,
    "cognitive_plan":None,
    "cognitive_critical_review":None,
    "cognitive_checkpoint":None,
}
report["coin_learning"]=study(WORKER)
query=SPEC["query"]
url="https://hn.algolia.com/api/v1/search_by_date?"+urllib.parse.urlencode({
    "query":query,"tags":"story","hitsPerPage":8,
})
report["source_url"]=url
try:
    req=urllib.request.Request(url,headers={
       "User-Agent":"IndependentlyHostedWorker/1.0",
       "Accept":"application/json",
    })
    with urllib.request.urlopen(req,timeout=12) as response:
        data=json.loads(response.read(300000))
    for item in data.get("hits",[])[:8]:
        title=str(item.get("title") or "")[:150]
        link=str(item.get("url") or "")
        if not link.startswith("https://"):
            continue
        report["source_items"].append({
           "title":title,"url":link,
           "status":"unverified_search_result_not_paid_work",
        })
    report["source_check_status"]="source_checked"
except Exception as exc:
    report["source_check_status"]="source_failed"
    report["source_error"]=f"{type(exc).__name__}: {str(exc)[:200]}"

# For paid-work execution prioritize an ORIGINAL current open job issue,
# not a generic Hacker News story that merely mentions money.
# Preserve generic HN links strictly as background research; they are not
# payer evidence and must not displace an authentic source.
report["background_research_links_not_buyer_qualified"]=list(report["source_items"])
task_candidate=choose_actual_issue_for_training(
    FLEET,WORKER,"paid-opportunity-reports/new-earning-lanes.json")
report["task_source_fallback"]=task_candidate
if task_candidate.get("source_item"):
    report["source_items"]=[task_candidate["source_item"]]
    report["source_check_status"]="source_checked"
    report["original_research_api_url"]=report["source_url"]
    report["source_url"]=task_candidate["source_item"]["url"]
    report["source_original_issue_checked"]=True
    report["external_payer_acceptance_verified"]=False
else:
    report["paid_work_issue_selected"]=False
    # A general HN search link is NOT a genuine task/payer and should not
    # pass a qualified commercial delivery source test.
    report["source_items"]=[]
    report["source_check_status"]="no_original_paid_work_issue_verified"
    report["source_error"]="No accepted original GitHub task; "+task_candidate.get("status","unknown")

# All research and decisions are executed in this standalone Python process.
# ChatGPT does not run, own or control this model; it may merely relay orders.
report["cognitive_prior_memory"]=prior_memory(WORKER)
report["cognitive_plan"]=deterministic_plan(
    WORKER,SPEC["role_name"],report["source_items"],
    report["coin_learning"],report["cognitive_prior_memory"])
model=None

try:
    # Inference runs here in THIS process, not in the director's interpreter.
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY","1")
    os.environ.setdefault("OMP_NUM_THREADS","2")
    from transformers import pipeline
    model=pipeline("text-generation",
      model=report["model"],device=-1)
    coin_study=report["coin_learning"]
    examples=[{"title":x["title"],"url":x["url"]}
              for x in report["source_items"][:2]]
    prompt=[
      {"role":"system","content":"You are one genuinely running B company agent. HUMAN OWNER grants broad creative and commercial initiative: you MAY self-select any lawful original product, service, source-check, software idea or useful buyer task WORLDWIDE, change sectors, try multiple distinct hypotheses and create concrete useful work without asking a manager to preapprove each internal idea. Your specific preassigned location/specialty/source is a STARTING POINT ONLY, not a restriction. Prefer real sponsor identity, actual payer readiness and deliverable over repeating instructions. You cannot invent buyer consent, platform access, hiring, workers or payments. Permitted external posting or selling requires actual authorized account, venue permission and willing counterparties. All mutually agreed payment must go to the owner-approved BTC mainnet address for YOUR company's account; never use arbitrary or other-fleet wallet. Preserve one-parent reporting and owner authority. A verified $100 real-receipt target remains, not a guaranteed or already realized sum.",
      {"role":"user","content":(universal_prompt(UNIVERSAL_TASK)[:1100]+"\n"+owner_first_oath_text(OWNER_OATH)[:650]+"\n"+compact_prompt()[:380]+
        "\nDIRECTOR SPECIALIZATION "+DIRECTOR_ORDER[:850]+
        "\nHIERARCHICAL IDEA TASK "+GOVERNED_IDEA_ORDER["task"][:260]+
        "\nSECOND DISTINCT TASK — STUDY PUBLIC CODE FROM "+SOFTWARE_SECOND["source_platform"]+"; "+SOFTWARE_SECOND["reference_software"]+
        " "+SOFTWARE_SECOND["official_repository"]+" feature "+SOFTWARE_SECOND["focus_feature"]+
        "; legal reuse requires actual license/attribution verification; do not copy proprietary or unlicensed code."+
        " DIRECT BOSS "+GOVERNED_IDEA_ORDER["direct_supervisor"]+
        " CORRECTIVE RULE "+GOVERNED_IDEA_ORDER["manager_if_worker_stuck"][:320]+
        "\nSTRICT CHIEF D ORDER "+STRICT_MODEL_ORDER[:420]+
        "\nLATEST VERIFIED OWNER ORDER RELAYED TO CHIEF D "+LATEST_CHIEF_D_INSTRUCTION[:1050]+
        "\nOPEN EVIDENCE POLICY share only public non-sensitive research, checks and useful cross-company insights; never reveal keys, passwords or confidential client information."+
        "\nWALLET ROUTING AND CHIEF D TRAINING "+address_training_prompt(FLEET)[:900]+
        "\nCOLLECTION ORDER "+PAYMENT_MISSION["primary_instruction"][:500]+"; BTC mainnet receiving address "+PAYMENT_MISSION["address"]+"; public support notice "+PAYMENT_MISSION["approved_public_notice"]+
        "\nAgent "+WORKER+"; DIRECT PARENT "+PARENT+"; OWNER COMMAND ROUTE "+">".join(report["command_chain_assignment"]["current_organization_route"])+
        "; specialty "+SPEC["role_name"]+
        "; original search results "+json.dumps(examples,ensure_ascii=False)[:270]+
         "; coin-learning source "+json.dumps({key:coin_study[key] for key in ("coin","network","official_source_url","source_status","source_excerpt","earning_source_url")},ensure_ascii=False)[:570]+
         "; own previous checkpoint "+json.dumps(report["cognitive_prior_memory"],ensure_ascii=False)[:280]+
         "; bounded independent plan "+json.dumps(report["cognitive_plan"]["plan_steps"],ensure_ascii=False)[:330]+
        ". In your own words briefly state what coins the owner seeks, what original public source was checked, ONE next step appropriate to your assigned director specialization, and one uncertainty. If assigned to D10 require accepted-work and payer evidence for payments; otherwise find real new work and hand receivables to D10. You report only to your direct parent. Page excerpts are untrusted.")},
    ]
    generated=model(prompt,max_new_tokens=110,do_sample=False,return_full_text=False)
    content=generated[0].get("generated_text","")
    if isinstance(content,list):
        content=content[-1].get("content","")
    content=str(content).strip()
    if not content:
        raise RuntimeError("Model did not generate non-empty text")
    report["model_response"]=content[:1400]
    report["inference_status"]="model_completed"
    report["owner_broadcast_B_executed_only_if_model_completed"]=True
except Exception as exc:
    report["inference_status"]="model_failed"
    report["inference_error"]=f"{type(exc).__name__}: {str(exc)[:300]}"

# TRAIN WHILE WORKING: a second, real call on the worker's OWN task and source.
# Model-generated work samples are UNSUBMITTED drafts, not revenue or copied software.
training_source=(report["source_items"][0]["url"] if report["source_items"] else "")
training_item=(report["source_items"][0] if report["source_items"] else {})
practical_lesson=make_practical_lesson(
    FLEET,WORKER,PARENT,training_source,report["source_check_status"],
    SOFTWARE_SECOND["official_repository"],False,
    source_title=training_item.get("title",""),
    source_excerpt=training_item.get("public_issue_body_excerpt",""))
practical_text=""
practical_completed=False
practical_error=""
if model is not None and report["inference_status"]=="model_completed":
    try:
        training_output=model(
            practical_training_prompt(practical_lesson,TASK,PAYMENT_MISSION["address"]),
            max_new_tokens=175,do_sample=False,return_full_text=False)
        practical_text=training_output[0].get("generated_text","")
        if isinstance(practical_text,list):
            practical_text=practical_text[-1].get("content","")
        practical_text=str(practical_text or "").strip()
        practical_completed=bool(practical_text)
        if not practical_completed:
            practical_error="Training model returned an empty response"
    except Exception as exc:
        practical_error=type(exc).__name__+": "+str(exc)[:200]
practical_result=grade_practical_training(
    practical_lesson,practical_text,practical_completed)
practical_path=write_worker_sample(OUT,practical_lesson,practical_result)
report["practical_training_while_working"]={
    "assignment":practical_lesson,
    "result":practical_result,
    "independent_model_call_status":"MODEL_COMPLETED" if practical_completed else "NOT_COMPLETED",
    "model_error":practical_error,
    "actual_work_sample_file":practical_path,
    "external_job_submission_or_payment_verified":False,
}

## Director D lesson ORD-047: this is an independent real worker-model response.
# Missing lesson/model access and weak answers NEVER produce a fake "learned" response.
report["director_D_lesson_assessment"]=teach_and_assess(model, WORKER, PARENT)
# Every actual model must independently explain the two-company hierarchy,
# recruiting cascade, its correct company wallet, and reporting via its own
# parent/director/Chief D to the human OWNER. No model => NOT_RUN, not understood.
report["system_understanding_assessment"]=assess_full_system(
    model,FLEET,WORKER,PARENT,PAYMENT_MISSION["address"])
report["system_report_to_human_owner_via_hierarchy"]={
    "immediate_parent":FLEET+"/"+PARENT,
    "local_director":FLEET+"/"+DIRECTOR,
    "sole_chief_director":"CHIEF_D",
    "ultimate_owner":"HUMAN_OWNER",
    "worker_finished_report_uploaded_to_parent_verified":False,
    "actual_owner_received_this_worker_report_verified":False,
    "knowledge_check_execution_status":report["system_understanding_assessment"]["model_execution"],
    "knowledge_check_grade":report["system_understanding_assessment"]["assessment"],
}

report["command_chain_understanding"]=understanding_receipt(
    WORKER,report.get("model_response",""),report["inference_status"],
    report["coin_learning"]["official_source_url"])
report["understanding_model_attempts"]=1
# If the small model replied but did not mention both its coin mission and a
# concrete research action, give THAT SAME real model a single clarification.
# This is not proof of comprehension, and it never invents a child response.
if (report["inference_status"]=="model_completed" and
    report["command_chain_understanding"]["understanding_status"]=="model_response_needs_parent_review"):
    try:
        correction=[
            {"role":"system","content":"You are the SAME worker continuing your own reply. State your authorized role, what legitimate cryptocurrency work is needed, one public source to verify, one next concrete research action and important uncertainty. No fabricated earnings."},
            {"role":"user","content":"Worker "+WORKER+" reports only to "+PARENT+
             ". Owner order ORD-035 asks you to explain, in your own words, how you will research genuine coin-paying work and verify deposits. Answer briefly in your own words."},
        ]
        second=model(correction,max_new_tokens=110,do_sample=False,return_full_text=False)
        new=second[0].get("generated_text","")
        if isinstance(new,list):new=new[-1].get("content","")
        if str(new or "").strip():
            new_receipt=understanding_receipt(WORKER,str(new), "model_completed",
                report["coin_learning"]["official_source_url"])
            report["understanding_model_attempts"]=2
            report["first_understanding_status"]="model_response_needs_parent_review"
            report["command_chain_understanding"]=new_receipt
            report["understanding_retry_status"]=new_receipt["understanding_status"]
        else:
            report["understanding_retry_status"]="retry_model_returned_empty"
    except Exception as exc:
        report["understanding_retry_status"]="retry_failed:"+str(exc)[:170]
# A separate bounded inference is required to record what THIS real B model
# thinks the *latest* Chief D owner command means. Merely constructing or
# receiving an assignment never counts as an acknowledged instruction.
ack_reply=""
if model is not None and report["inference_status"]=="model_completed":
    try:
        ack_messages=[
            {"role":"system","content":"Answer accurately in your own words, briefly. Do not invent external jobs, wallet payments or outreach. Echo the exact order ID and your correct parent. State the legitimate Bitcoin earning objective, source-evidence requirement and one next lawful work action."},
            {"role":"user","content":"Current Chief D order "+STRICT_OWNER_ORDER_ID+
                ". Your worker identity "+WORKER+"; your direct supervisor "+PARENT+
                ". Give YOUR own command acknowledgement in 1-3 short sentences: include EXACT ORDER "+STRICT_OWNER_ORDER_ID+
                ", EXACT PARENT "+PARENT+", real cryptocurrency payment objective, source proof, and your next useful lawful action. Do not claim a coin has been paid."}
        ]
        ack_output=model(ack_messages,max_new_tokens=100,do_sample=False,return_full_text=False)
        ack_reply=ack_output[0].get("generated_text","")
        if isinstance(ack_reply,list):
            ack_reply=ack_reply[-1].get("content","")
        report["latest_order_ack_inference_status"]="model_inference_completed"
    except Exception as exc:
        report["latest_order_ack_inference_status"]="model_ack_failed:"+type(exc).__name__
report["latest_command_model_acknowledgement"]=evaluate_owner_command_ack(
    ack_reply,WORKER,PARENT,STRICT_OWNER_ORDER_ID)
# Owner's separate 10-ideas-per-executed-worker brainstorming exercise.
# Every eligible role has 10 non-confidential, evidence-gated assigned
# hypotheses, but only a REAL additional model inference counts as the
# worker's own generated ideas. Weak/deduplicated ideas fail qualification.
brainstorm=""
if model is not None and report["inference_status"]=="model_completed":
    try:
        menu_line="; ".join(x["idea_title"] for x in TEN_IDEA_MENU["candidate_ideas"])
        idea_prompt=[
            {"role":"system","content":"You are an actual independently invoked B worker. Produce ten distinct, realistic ways a legal original digital service or opt-in miner collaboration might result in BTC payment to an authorized account. These are proposals, not real clients or payment commitments. Output EXACTLY ten SHORT numbered lines 1. through 10. No made-up earnings, wallet keys, upfront fees, or spam."},
            {"role":"user","content":"Worker "+WORKER+" in "+FLEET+", direct parent "+PARENT+
                ". Chief D idea order OWNER-20261114-075553. Worker specialty: "+SPEC["role_name"][:75]+
                ". Ten avenues to assess/extend: "+menu_line[:950]+
                ". OTHER COMPANY'S EXECUTED MODEL LESSONS (UNVERIFIED, DO NOT COPY): "+json.dumps(SHARED_IDEA_EXAMPLES,ensure_ascii=False)[:650]+
                ". Create TEN DISTINCT brief concrete action ideas, one 8-15-word line each, numbered 1. to 10. Do not claim funding or contracts exist."}
        ]
        answer=model(idea_prompt,max_new_tokens=230,do_sample=False,return_full_text=False)
        brainstorm=answer[0].get("generated_text","")
        if isinstance(brainstorm,list):
            brainstorm=brainstorm[-1].get("content","")
        report["ten_idea_model_inference_status"]="MODEL_INFERENCE_COMPLETED"
    except Exception as exc:
        report["ten_idea_model_inference_status"]="MODEL_ERROR:"+type(exc).__name__
report["ten_idea_model_result"]=evaluate_generated_ten(brainstorm)
report["ten_idea_model_result"]["worker_id"]=FLEET+"/"+WORKER
report["ten_idea_model_result"]["direct_parent"]=PARENT
report["ten_idea_model_result"]["inference_status"]=report["ten_idea_model_inference_status"]
# Real manager-directed corrective intervention: an executable instruction from
# the chain of command, NOT a claim the manager separately ran a model.
if report["ten_idea_model_result"]["status"]!="TEN_MODEL_GENERATED_IDEAS_NEED_FACT_CHECK":
    report["supervisor_issued_idea_correction"]=supervisory_correction(
        GOVERNED_IDEA_ORDER,["TEN_ORIGINAL_MODEL_IDEAS_MISSING_OR_REPETITIVE"])
    if model is not None and report["inference_status"]=="model_completed":
        try:
            narrower=[
              {"role":"system","content":"Complete a CORRECTIVE IDEA EXERCISE under your immediate supervisor. Give EXACTLY 10 separate numbered lines 1. through 10. Each idea should be a different specific lawful service/deliverable or opt-in mining contribution with an evidence check; do not assert anyone is paying yet."},
              {"role":"user","content":"Company "+FLEET+", worker "+WORKER+", immediate manager "+PARENT+
                  ". Supervisor correction: "+report["supervisor_issued_idea_correction"]["supervisory_instruction"][:500]+
                  ". Your specialty: "+SPEC["role_name"][:90]+
                  ". List TEN distinct realistic ways to earn legitimate BTC with concrete paid deliverables. Number all lines 1. to 10. Never ask for fees or claim confirmed contracts."}
            ]
            second=model(narrower,max_new_tokens=260,do_sample=False,return_full_text=False)
            candidate=second[0].get("generated_text","")
            if isinstance(candidate,list):
                candidate=candidate[-1].get("content","")
            candidate_result=evaluate_generated_ten(candidate)
            report["actual_worker_corrective_retry_status"]="ACTUAL_MODEL_RETRY_COMPLETED"
            report["corrective_model_result"]=candidate_result
            if candidate_result["status"]=="TEN_MODEL_GENERATED_IDEAS_NEED_FACT_CHECK":
                report["ten_idea_model_result"]=candidate_result
                report["ten_idea_model_inference_status"]="MODEL_CORRECTIVE_RETRY_COMPLETED"
                report["supervisor_issued_idea_correction"]["after_retry"]="Worker's actual revised model output passes ten-item format; source and payer review still required"
            else:
                report["supervisor_issued_idea_correction"]["after_retry"]="STILL_INCOMPLETE_ESCALATE_TO_COMPANY_DIRECTOR"
        except Exception as exc:
            report["actual_worker_corrective_retry_status"]="ACTUAL_MODEL_RETRY_FAILED:"+type(exc).__name__
            report["supervisor_issued_idea_correction"]["after_retry"]="MODEL_RETRY_FAILED_ESCALATE_TO_COMPANY_DIRECTOR"
    else:
        report["actual_worker_corrective_retry_status"]="NO_MODEL_AVAILABLE_ESCALATE_TO_COMPANY_DIRECTOR"
# Independent address-mapping exercise for this actual model worker:
# never count merely receiving the public map as comprehension.
wallet_reply=""
if model is not None and report["inference_status"]=="model_completed":
    try:
        wallet_prompt=[
          {"role":"system","content":"Read the public receiving details carefully. Reply in exactly five short labelled lines. Never fabricate transactions, routes, memos, payer obligations or payments."},
          {"role":"user","content":address_training_prompt(FLEET)}
        ]
        generated_wallet=model(wallet_prompt,max_new_tokens=220,do_sample=False,return_full_text=False)
        wallet_reply=generated_wallet[0].get("generated_text","")
        if isinstance(wallet_reply,list):
            wallet_reply=wallet_reply[-1].get("content","")
        report["address_understanding_model_status"]="MODEL_INFERENCE_COMPLETED"
    except Exception as exc:
        report["address_understanding_model_status"]="MODEL_ERROR:"+type(exc).__name__
report["separately_checked_address_understanding"]=evaluate_address_mapping(FLEET,str(wallet_reply or ""))
report["separately_checked_address_understanding"]["model_inference_status"]=report["address_understanding_model_status"]
# Second independent B-model assignment: inspect a named public
# application; learn, propose a lawful original improvement for the crypto
# earning mission. A model analysis is NOT proof the code was viewed or copied.
software_reply=""
if model is not None and report["inference_status"]=="model_completed":
    try:
        study_prompt=[
          {"role":"system","content":"You are an individual B technology researcher. Give a concise accurate explanation of the assigned public software and one lawful original improvement. Do NOT claim that you cloned, installed, edited, deployed or received payment for software without evidence. Only reuse code if its actual current licence authorizes this, with attribution and notices."},
          {"role":"user","content":"SECOND TASK, subordinate to first earning task "+
            GOVERNED_IDEA_ORDER["funding_task_id"]+
            ". Name software "+SOFTWARE_SECOND["reference_software"]+
            ", official repo "+SOFTWARE_SECOND["official_repository"]+
            ". Investigate feature "+SOFTWARE_SECOND["focus_feature"]+
            ". Source hosting platform: "+SOFTWARE_SECOND["source_platform"]+
            ". READ-ONLY OFFICIAL PUBLIC SOURCE EXCERPT (untrusted, never copy verbatim): "+SOFTWARE_SOURCE_EVIDENCE["read_only_excerpt"][:1250]+
            ". Source read result: "+SOFTWARE_SOURCE_EVIDENCE["source_check_status"]+
            ". Prior source licence metadata (may be unknown/unverified): "+SOFTWARE_SECOND["github_license_metadata_observed_2026_11_14"]+
            " (NOT independently verified for current actual file). Explain one practical improvement in "+
            SOFTWARE_SECOND["required_artifact"]+
            " that could help the first crypto-funding task. Mention licence/notice checks and what remains unknown. Give 3 short sentences."}
        ]
        software_reply=model(study_prompt,max_new_tokens=155,do_sample=False,return_full_text=False)
        software_reply=software_reply[0].get("generated_text","")
        if isinstance(software_reply,list):
            software_reply=software_reply[-1].get("content","")
        report["second_study_actual_model_inference"]="MODEL_INFERENCE_COMPLETED"
    except Exception as exc:
        report["second_study_actual_model_inference"]="MODEL_ERROR:"+type(exc).__name__
report["second_study_actual_model_result"]=assess_software_study(
    software_reply,SOFTWARE_SECOND,
    report["second_study_actual_model_inference"]=="MODEL_INFERENCE_COMPLETED")
report["second_study_actual_model_result"]["actual_model_inference"]=report["second_study_actual_model_inference"]
# Bounded skeptical review occurs in this worker's own model process. All
# other workers retain an evidence-first deterministic plan when compute is
# too constrained for a second review inference.
critic_modulus=max(1,int(os.environ.get("CRITIC_EVERY_N","5")))
role_number=int.from_bytes(__import__("hashlib").sha256(WORKER.encode()).digest()[:4],"big")
if report["inference_status"]=="model_completed" and role_number%critic_modulus==0:
    report["cognitive_critical_review"]=skeptical_model_review(
        model,WORKER,report["cognitive_plan"],report["model_response"])
else:
    report["cognitive_critical_review"]={
        "status":"not_run_model_failed" if report["inference_status"]!="model_completed"
                 else "deferred_with_rule_based_evidence_plan",
        "response":"","actually_second_inference":False}
report["cognitive_checkpoint"]=checkpoint(
    WORKER,report["cognitive_plan"],report["inference_status"],
    report.get("model_response"),report["cognitive_critical_review"],
    report["source_check_status"])
# The individual agent's output is inspectable and resumable, not a promise
# that this ephemeral runner will continue after it shuts down.
report["activation_evidence"]={
    "owner_order":"ORD-038",
    "agent_id":WORKER,
    "independent_model_completed":report["inference_status"]=="model_completed",
    "public_source_research_attempted":report["source_check_status"] in ("source_checked","source_failed") or
         report["coin_learning"]["source_status"]!="not_checked",
    "direct_parent":PARENT,
    "unique_os_pid":os.getpid(),
    "state":"ephemeral_agent_process_completed" if report["inference_status"]=="model_completed" else "model_failed_or_incomplete",
    "next_step_checkpoint":("Independently verify payer, work deliverable, eligibility and correct network for "+
        (report["source_items"][0]["url"] if report["source_items"] else report["coin_learning"]["earning_source_url"])),
    "model_next_action":report["model_response"][:550] if report.get("model_response") else None,
    "will_resume_automatically_without_new_run":False,
    "independently_verified_payment":False
}
report["duration_sec"]=round(time.monotonic()-START,2)
report["completed_at_utc"]=datetime.now(timezone.utc).isoformat()
path=OUT/(WORKER+".json")
md=OUT/(WORKER+".md")
report["documents_written"]=True
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=[
    "# Independently hosted worker — "+WORKER,"",
    f"- **Actual OS process PID:** {report['os_process_pid']}",
    f"- **Director/Manager:** {DIRECTOR} / {MANAGER}",
    f"- **Level/Parent:** {IDENTITY['level']} / {PARENT}",
    f"- **B = billions of workers; ORD-034:** inherited; inference {report['inference_status']}",
    f"- **Coin learned:** {report['coin_learning']['coin']} / {report['coin_learning']['source_status']}",
    f"- **Started:** {STAMP}",
    f"- **Source result:** {report['source_check_status']}",
    f"- **AI inference result:** {report['inference_status']}",
    "- **Latest Chief D command response:** "+report["latest_command_model_acknowledgement"]["status"],
    "- **Latest Chief D owner command:** "+STRICT_OWNER_ORDER_ID,
    "- **First oath:** owner-only root -> Chief D -> two separate boards of ten -> direct parent "+OWNER_OATH["immediate_parent"],
    "- **Universal cross-country protocol:** "+UNIVERSAL_TASK["schema"]+" / "+UNIVERSAL_TASK["assignment"]["task_id"],
    "- **World market hypothesis (NOT a confirmed customer):** "+UNIVERSAL_TASK["assignment"]["city_focus"]+", "+UNIVERSAL_TASK["assignment"]["country_iso_3166_alpha2"]+" / locale "+UNIVERSAL_TASK["localization"]["content_language"],
    "- **Owner-approved universal task stage:** "+UNIVERSAL_TASK["assignment"]["phase"]+"; per-worker model execution proof separate",
    "- **Oath chain:** "+" -> ".join(OWNER_OATH["owner_to_worker_path"]),
    "- **Cryptographic origin authentication of GitHub order:** NOT PROVEN; versioned owner relay only",
    "- **Ten assigned idea candidates:** "+str(TEN_IDEA_MENU["count"])+" (deterministic, not yet paid)",
    "- **Own AI-generated ten-idea exercise:** "+report["ten_idea_model_result"]["status"],
    "- **First unique crypto funding task:** "+GOVERNED_IDEA_ORDER["funding_task_id"],
    "- **Second distinct software study task:** "+SOFTWARE_SECOND["task_id"]+" / "+SOFTWARE_SECOND["reference_software"],
    "- **Second software study model status:** "+report["second_study_actual_model_result"]["status"],
    "- **Actual code reuse/commits by this worker:** NONE VERIFIED",
    "- **Training while working:** "+report["practical_training_while_working"]["result"]["status"],
    "- **Practical training evidence file:** "+report["practical_training_while_working"]["actual_work_sample_file"],
    "- **Direct manager corrective order status:** "+str((report.get("supervisor_issued_idea_correction") or {}).get("status","NOT_NEEDED")),
    "- **Actual corrective AI model retry:** "+report["actual_worker_corrective_retry_status"],
    "- **Model-verified company wallet mapping:** "+report["separately_checked_address_understanding"]["status"],
    f"- **Director D lesson accessible:** {report['director_D_lesson_assessment']['lesson_accessible']}",
    f"- **Separate lesson model execution:** {report['director_D_lesson_assessment']['model_execution_status']}",
    f"- **Worker reports learned:** {report['director_D_lesson_assessment']['reported_learned']}",
    f"- **Director D lesson grade:** {report['director_D_lesson_assessment']['assessment']}",
    f"- **Duration:** {report['duration_sec']} sec",
    f"- **All owner orders inherited:** {report['order_inheritance']['order_count']}",
    "- **Owner-to-role command chain:** "+" -> ".join(report["command_chain_assignment"]["owner_to_role_route"]),
    "- **Independent understanding receipt:** "+report["command_chain_understanding"]["understanding_status"],
    "- **Actual comprehension-model attempts:** "+str(report["understanding_model_attempts"]),
    "- **Direct-parent review:** pending; do not claim human understanding",
    "- **Previous independent checkpoint:** "+str(report["cognitive_prior_memory"]["state_source"]),
    "- **Second-pass critique:** "+report["cognitive_critical_review"]["status"],
    "","## Director D lesson — what I learned (independent model response)",
    report["director_D_lesson_assessment"].get("answer") or "NOT LEARNED / NOT VERIFIED: no separately completed response",
    "Teacher lesson assessment: "+report["director_D_lesson_assessment"]["assessment"],
    "","## Individual model-generated understanding reply",
    report["command_chain_understanding"]["model_generated_own_words"] or "No independent model response recorded",
    "","## Independent task",TASK,
    "","## Public evidence / original links",
]
lines.extend("- "+x["title"]+" — "+x["url"] for x in report["source_items"][:5])
if not report["source_items"]:lines.append("- No eligible original links obtained.")
lines += [
    "","## Independent B-billion-worker coin research",
    "- Coin: "+report["coin_learning"]["coin"],
    "- Network: "+report["coin_learning"]["network"],
    "- Official source URL: "+report["coin_learning"]["official_source_url"],
    "- Actual source check: "+report["coin_learning"]["source_status"],
    "- Research question: "+report["coin_learning"]["question"],
    "- Fetched public text (untrusted): "+(report["coin_learning"]["source_excerpt"][:420] or "not available"),
    "- Earning channel to investigate: "+report["coin_learning"]["earning_source_url"],
    "- Earning question: "+report["coin_learning"]["earning_question"],
]
lines+=["","## Separate AI decision",report["model_response"] or
  ("Model unavailable: "+str(report["inference_error"] or "unknown")),
  "","## Actual limitations",
  "- Search results are unverified leads, not paid contracts.",
  "- No application or message was sent.",
  "- No blockchain payment was independently confirmed.",
  "- The role exists as a real process ONLY for its recorded invocation.",
  "","## Next step",
  "Verify the original payer, explicit deliverable, account eligibility and coin payout using permitted methods."
]
md.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"worker_id":WORKER,"pid":os.getpid(),
   "source_check_status":report["source_check_status"],
   "model_inference_status":report["inference_status"],
   "report_json":str(path),"report_md":str(md)},ensure_ascii=False))
