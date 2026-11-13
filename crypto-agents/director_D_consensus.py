"""Director D's evidence-led ten-director deliberation over ACTUAL worker results.

A genuine director AI response is counted only if model inference succeeded.
All 10 directors receive the same cross-brief in the second deliberation round.
No dummy director votes, fabricated receipts, contracts or completed applications.
"""
from __future__ import annotations
import json
import os
from datetime import datetime,timezone
from pathlib import Path

BASE=Path("combined-ai-processes")/"ai-process-reports"
OUT=Path("director-D-discussion")
OUT.mkdir(exist_ok=True)
DIRECTORS=[f"D{i:02d}" for i in range(1,11)]
source_checks={}
briefs={}
for d in DIRECTORS:
    fp=BASE/("manifest-"+d+".json")
    if not fp.exists():
        source_checks[d]={"status":"missing_manifest","model_completed":0,"sampled_evidence":[]}
        continue
    try:
        m=json.loads(fp.read_text(encoding="utf-8"))
        findings=[]
        for role_id in m.get("worker_processes_selected",[])[:50]:
            rp=BASE/(role_id+".json")
            if not rp.exists():continue
            obj=json.loads(rp.read_text(encoding="utf-8"))
            if obj.get("inference_status")!="model_completed":continue
            sources=obj.get("source_items") or []
            learning=obj.get("coin_learning") or {}
            findings.append({
               "worker":role_id,
               "source":str((sources[0].get("url") if sources else learning.get("official_source_url")) or "")[:180],
               "research_result":str(obj.get("model_response") or "")[:340],
               "coin":str(learning.get("coin",""))[:50],
               "model_status":"model_completed",
               "payment_verified":bool(obj.get("verified_wallet_receipts"))
            })
        source_checks[d]={
          "status":"real_worker_results_available" if findings else "no_valid_completed_workers",
          "model_completed":int(m.get("real_model_completed",0)),
          "sampled_evidence":findings[:4],
          "manifest_model_attempts":int(m.get("subprocesses_invoked",0))
        }
    except Exception as exc:
        source_checks[d]={"status":"invalid_worker_manifest",
                          "error":f"{type(exc).__name__}: {str(exc)[:140]}",
                          "model_completed":0,"sampled_evidence":[]}
    briefs[d]=source_checks[d]

timestamp=datetime.now(timezone.utc).isoformat()
record={
 "coordinator":"Director D",
 "owner_order":"ORD-037",
 "manager_in_charge":"Director D",
 "performance_scorecard":{},
 "actionable_source_linked_leads_count":0,
 "ORD038_activation_by_director":{},
 "verified_payer_or_contract_count":0,
 "created_utc":timestamp,
 "defined_virtual_roles":375188632680,
 "source_status_by_director":source_checks,
 "round_one":{},
 "round_two":{},
 "director_D_response":None,
 "director_D_teaching":None,
 "director_D_teaching_model_completed":False,
 "lesson_source":"crypto-agents/DIRECTOR_D_LESSON_TO_B.md",
 "real_director_model_round_one":0,
 "real_director_model_round_two":0,
 "D_model_completed":False,
 "agreement_status":"not_established",
 "reviewed_recommendation":[],
 "verified_crypto_receipts":[],
 "truth":"This is a bounded genuine small-model cross-review only where model executions succeed. A missing model is not a director's vote. No payment verified by local worker logs."
}
# D grades only actual evidence, never pre-filled or configured role identities.
for director_id in DIRECTORS:
    evidence=source_checks.get(director_id) or {}
    findings=evidence.get("sampled_evidence",[])
    real_urls=[f["source"] for f in findings if str(f.get("source","")).startswith("https://")]
    model_ok=int(evidence.get("model_completed",0))
    if real_urls and model_ok:
        status="WORK_RESEARCHED_PAYER_AND_PAYOUT_NOT_VERIFIED"
    elif model_ok:
        status="MODEL_RAN_NO_VERIFIABLE_SOURCE_LINK"
    else:
        status="NO_REAL_MODEL_WORK_VERIFIED"
    record["ORD038_activation_by_director"][director_id]={
       "confirmed_actual_individual_agent_model_completions":model_ok,
       "defined_role_identities_under_director_not_running":True,
       "verified_live_persistent_agents":0,
       "research_based_activities_checked":len(real_urls),
       "next_action":"Activate more distinct workers within free runner limits, retrieve model reports and resume confirmed pay-eligible work."
    }
    record["performance_scorecard"][director_id]={
       "status":status,"model_completions_reported":model_ok,
       "source_linked_sample_count":len(real_urls),
       "best_actual_source_url":real_urls[0] if real_urls else None,
       "payer_and_crypto_terms_verified":False,
       "verified_earned_coin_receipts":0,
       "required_next_action":"Verify real payer, a fee-free task and exact coin/network payment terms at this original source" if real_urls else "Run a real source-check and individual AI model report first",
       "report_ready_for_payment_claim":False
    }
    record["actionable_source_linked_leads_count"]+=len(real_urls)
# A source link alone does not establish an actionable paying opportunity.
record["actionable_source_linked_leads_count_is_provisional"]=True
model=None
load_error=None
try:
    from transformers import pipeline
    os.environ.setdefault("OMP_NUM_THREADS","2")
    model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
except Exception as exc:
    load_error=f"{type(exc).__name__}: {str(exc)[:300]}"
record["model_load_error"]=load_error

def ask(role,system,task):
    if model is None:return {"status":"no_model_loaded","response":"","error":load_error}
    try:
        result=model([{"role":"system","content":system},
                      {"role":"user","content":task}],max_new_tokens=125,
                       do_sample=False,return_full_text=False)
        response=result[0].get("generated_text","")
        if isinstance(response,list):response=response[-1].get("content","")
        response=str(response or "").strip()
        if not response:raise ValueError("empty output")
        return {"status":"model_completed","response":response[:900]}
    except Exception as exc:
        return {"status":"model_failed","response":"",
                "error":f"{type(exc).__name__}: {str(exc)[:250]}"}

# A separate real D model execution presents the prepared training curriculum.
# The curriculum file by itself is not proof D actually taught or workers learned.
lesson_path=Path("crypto-agents/DIRECTOR_D_LESSON_TO_B.md")
if lesson_path.exists():
    record["director_D_teaching"]=ask(
        "D-TEACHER",
        "You are designated Director D teaching actual B workers. Explain your real abilities and limitations; do not falsely claim students attended or learned.",
        "Deliver your own short lesson to all activated B agents: D coordinates ten directors, audits sources and real model executions, prepares one owner report, checks legitimate payment with D09, and resolves software problems with D10. D cannot compel outsiders, create coins from prompts, or claim a wallet payment without proof. Require each worker to answer what D CAN do, CANNOT do, and name its real direct PARENT. The lesson file is crypto-agents/DIRECTOR_D_LESSON_TO_B.md. Include an honest line: attendance and learning remain unverified until each real agent replies."
    )
    record["director_D_teaching_model_completed"]=(record["director_D_teaching"].get("status")=="model_completed")
else:
    record["director_D_teaching"]={"status":"not_run_lesson_missing","response":""}

for d in DIRECTORS:
    evidence=source_checks.get(d) or {"status":"missing_manifest"}
    if evidence["status"]!="real_worker_results_available":
        record["round_one"][d]={"status":"not_run_no_evidence","response":"",
                                "reason":evidence["status"]}
        continue
    task=("You are "+d+" with genuine worker research evidence: "+
      json.dumps(evidence["sampled_evidence"],ensure_ascii=False)[:1650]+
      ". Speak only from an actual URL provided; state one real payer/deliverable if evidenced (else unknown), one crypto-payment uncertainty, "
      "and ONE immediate authorized no-fee next action, not a motivational statement. You have not contacted payers or received coins. "
      "No unverifiable claims.")
    reply=ask(d,"You are one of ten independent director review model calls. Evaluate only supplied evidence. Challenge unsupported claims, protect owner funds, no fictional actions.",task)
    record["round_one"][d]=reply
    if reply["status"]=="model_completed":record["real_director_model_round_one"]+=1

summaries={k:v["response"][:450] for k,v in record["round_one"].items()
           if v.get("status")=="model_completed"}
for d in DIRECTORS:
    first=record["round_one"][d]
    if first.get("status")!="model_completed":
        record["round_two"][d]={"status":"not_run_no_initial_response","response":""}
        continue
    task=("This is an ACTUAL second AI inference for director "+d+
        ". Your first opinion: "+first["response"][:360]+
        ". Other director research opinions: "+
        json.dumps({k:v for k,v in summaries.items() if k!=d},ensure_ascii=False)[:1350]+
        ". Prioritize one concrete payer verification, eligibility check or preparation of an actual paid-work deliverable. Explain what "
        "you disagree with or cannot verify, and distinguish work leads from coins received.")
    reply=ask(d,"Independent director cross-review. Accept colleagues' claims only if their source evidence supports them; disagreement is allowed; do not fake consensus.",task)
    record["round_two"][d]=reply
    if reply["status"]=="model_completed":record["real_director_model_round_two"]+=1

perspectives={d:record["round_two"][d].get("response","")[:550] for d in DIRECTORS
              if record["round_two"][d].get("status")=="model_completed"}
if perspectives:
    record["director_D_response"]=ask("D","You are designated Director D, the sole owner-facing reporting model. You must be candid about missing participants and real money. Make one concise unified recommendation, the key agreement, outstanding disagreements and one actual next task. Do not claim a paid contract or wallet receipt without proof.",
      "Owner has 375188632680 defined roles, not live workers. Ten director cross-reviews: "+
      json.dumps(perspectives,ensure_ascii=False)[:3500]+
      ". Number with actual round two responses: "+str(len(perspectives))+
      ". Provide a short owner performance report: actionable evidence, no-work directors, the best original URL for one opportunity, one feasible action, agreement/dissent and money verification status. Never imply ten agreeing if any model is missing.")
    record["D_model_completed"]=record["director_D_response"].get("status")=="model_completed"

if record["real_director_model_round_two"]==10 and record["D_model_completed"]:
    record["agreement_status"]="all_ten_models_cross_reviewed_D_recommendation_not_unanimity_proof"
elif record["real_director_model_round_two"]>0 and record["D_model_completed"]:
    record["agreement_status"]="partial_discussion_no_unanimous_agreement_claim"
else:
    record["agreement_status"]="no_genuine_ten_director_discussion_established"

record["reviewed_recommendation"]=[
 "Verify a real fee-free paid task with original payer, deliverable and eligibility.",
 "Prefer accounting/QuickBooks/Excel services or legitimate crypto bounties.",
 "Obtain written token/network payout terms before working and verify received funds independently.",
]
(OUT/"director-D-consensus.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=[
 "# Director D — Evidence-Based B-Workforce Discussion","",
 "Date (UTC): "+timestamp,
 "Owner order: ORD-036 — all departments discuss; D consolidates and reports",
 "Defined workforce: 375,188,632,680 role identities (not active model instances)",
 "",
 "## Director D — accountable performance orders ORD-037 and ORD-038",
 "Real agent model invocations by director are counted separately from dormant role IDs.",
 "Only original checked source URLs and real model logs count as investigated work.",
 "Source-linked research items (NOT verified paid clients): "+str(record["actionable_source_linked_leads_count"]),
 "Verified payer/contract terms: "+str(record["verified_payer_or_contract_count"]),
 "Actual wallet receipts verified by this report: 0",
 "",
 "## Director D lesson ORD-047: actual teacher model",
 "Teaching model completed: "+str(record["director_D_teaching_model_completed"]),
 "Teaching output: "+str((record["director_D_teaching"] or {}).get("response","not_run")),
 "Note: This is a teaching output, NOT evidence that dormant B roles attended or understood.",
 "",
 "## Actually executed director model discussion",
 "Round 1 model responses: "+str(record["real_director_model_round_one"])+"/10",
 "Cross-review model responses: "+str(record["real_director_model_round_two"])+"/10",
 "Director D model synthesis completed: "+str(record["D_model_completed"]),
 "Agreement assessment: "+record["agreement_status"],"",
 "## Director responses and missing evidence",
]
for d in DIRECTORS:
    lines.append("### "+d)
    lines.append("Worker results: "+source_checks.get(d,{}).get("status","unknown"))
    lines.append("D performance status: "+record["performance_scorecard"][d]["status"])
    lines.append("Actual agent model completions: "+str(record["ORD038_activation_by_director"][d]["confirmed_actual_individual_agent_model_completions"]))
    lines.append("Best original source: "+str(record["performance_scorecard"][d]["best_actual_source_url"]))
    lines.append("Next authorized action: "+record["performance_scorecard"][d]["required_next_action"])
    lines.append("First-round model: "+record["round_one"][d]["status"])
    lines.append("Second-round model: "+record["round_two"][d]["status"])
    lines.append("Actual opinion: "+record["round_two"][d].get("response","Not obtained"))
lines.extend(["","## Director D's model-generated reply",
              (record["director_D_response"] or {}).get("response","No D model result"),
              "","## Standing realistic next steps"])
lines.extend("- "+s for s in record["reviewed_recommendation"])
lines+=["","No independently verified coin deposits were established by this process."]
(OUT/"director-D-consensus.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("DIRECTOR_D",json.dumps({
 "first_round_completed":record["real_director_model_round_one"],
 "cross_review_completed":record["real_director_model_round_two"],
 "D_completed":record["D_model_completed"],
 "agreement_status":record["agreement_status"],
 "reports":[str(OUT/"director-D-consensus.json"),str(OUT/"director-D-consensus.md")]
}))
