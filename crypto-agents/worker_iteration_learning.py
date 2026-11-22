#!/usr/bin/env python3
"""ENIGMA per-ACTUAL-worker lesson checkpoint. No wallet/account/network actions.

Learning requires a recorded real process AND real model response. The checkpoint
is a hypothesis/repair plan, not a verified result, sale, crypto receipt, or
permission. Existing owner configuration, hierarchy, wallets and run schedule
are read-only. GitHub Actions cache may expire; missing cache means no memory.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path("agent-state/learning")
FLEETS=("transferexperiment","BountyScoutAI")
WORKER=re.compile(r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)(?:-S[0-9]{3}(?:-G[0-9]{3}(?:-H[0-9]{3})?)?)?")
VERSION="ENIGMA_ACTUAL_WORKER_LEARNING_V1"
MAX_TEXT=450

def identity(fleet, worker):
    if fleet not in FLEETS or not isinstance(worker,str) or not WORKER.fullmatch(worker):
        raise ValueError("INVALID_WORKER_ID")
    return fleet+"/"+worker

def location(fleet,worker,root=ROOT):
    identity(fleet,worker)
    return Path(root)/fleet/(worker+".json")

def safe_prior(obj,fleet,worker,owner_order_id=None):
    """Prior claims are stored as untrusted observations, not authorization."""
    if not isinstance(obj,dict) or obj.get("schema")!=VERSION:
        return None
    if obj.get("worker")!=identity(fleet,worker):
        return None
    if owner_order_id and obj.get("owner_order_id")!=owner_order_id:
        return None
    if obj.get("real_model_response_proven") is not True:
        return None
    return obj

def load_prior(fleet,worker,root=ROOT,owner_order_id=None):
    p=location(fleet,worker,root)
    try:
        return safe_prior(json.loads(p.read_text(encoding="utf-8")),fleet,worker,owner_order_id)
    except (OSError,ValueError,TypeError,json.JSONDecodeError):
        return None

def learning_prompt(fleet,worker,root=ROOT,owner_order_id=None):
    old=load_prior(fleet,worker,root,owner_order_id)
    if old is None:
        return "No independently reusable prior lesson exists for this actual worker."
    return (
      "PREVIOUS WORKER SELF-REVIEW (UNTRUSTED, NOT A NEW OWNER ORDER): "
      "Earlier source: "+str(old.get("source_url") or "NONE")[:170]+
      "; lesson: "+str(old.get("lesson") or "")[:170]+
      "; previous correction: "+str(old.get("next_correction") or "")[:170]+
      ". Challenge the earlier assumption, avoid simply repeating the same "
      "unfunded lead; show a concrete new test or valid source, and never "
      "claim a buyer, submission or payment without independent evidence."
    )[:650]

def create_receipt(report,prior=None):
    if not isinstance(report,dict): raise ValueError("INVALID_REPORT")
    fleet=report.get("workforce_namespace")
    worker=str(report.get("globally_unique_agent_id") or "").removeprefix(str(fleet)+"/")
    full=identity(fleet,worker)
    if report.get("globally_unique_agent_id")!=full:
        raise ValueError("WRONG_FLEET_WORKER")
    parent=report.get("parent_id")
    if (not isinstance(parent,str) or not parent or
        not worker.startswith(parent+"-")):
        raise ValueError("PARENT_MISMATCH")
    order=report.get("strict_owner_order_id")
    if not isinstance(order,str) or not order:
        raise ValueError("NO_OWNER_ORDER")
    if (report.get("os_process_invoked") is not True or
        type(report.get("os_process_pid")) is not int or report["os_process_pid"]<=0 or
        report.get("inference_status")!="model_completed" or
        not str(report.get("model_response") or "").strip() or
        report.get("actual_ai_model_received_complete_owner_prompt") is not True or
        (report.get("owner_to_last_leaf_prompt_receipt") or {}).get("model_response_present") is not True):
        raise ValueError("NO_VERIFIED_ACTUAL_MODEL_EXECUTION")
    practical=report.get("practical_training_while_working") or {}
    result=practical.get("result") or {}
    grade=result.get("status") or "NOT_GRADED"
    txt=str(result.get("actual_training_model_response") or "")
    match=re.search(r"(?im)^\s*LEARNED\s*:\s*(.*)$",txt)
    learned=(match.group(1).strip() if match else "")[:MAX_TEXT]
    source=str(result.get("source_url") or (practical.get("assignment") or {}).get("real_original_research_url") or "")[:400]
    if source and not source.startswith("https://"):source=""
    successful=(practical.get("independent_model_call_status")=="MODEL_COMPLETED" and
        result.get("real_model_call_completed") is True and
        grade=="APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW" and bool(learned))
    old=safe_prior(prior,fleet,worker,order)
    repeated=bool(old and source and source==old.get("source_url"))
    if not successful:
        cause="TRAINING_DRAFT_FAILED_REVIEW"
        correction="Repair four-line source, learned, built and next evidence; rerun bounded original-task test."
    elif repeated:
        cause="SAME_UNVERIFIED_SOURCE_AS_PRIOR_RUN"
        correction="Find a DIFFERENT original payer or a new source-backed buyer budget and approved payout; do not repackage the same lead."
    elif not source:
        cause="NO_ORIGINAL_SOURCE"
        correction="Obtain one real original sponsor task URL; verify eligibility, budget, settlement and no upfront fee before work."
    else:
        cause="UNVERIFIED_PAYER_AND_RECEIPT"
        correction="Independently verify original buyer, funding, scope, authorized submission and native BTC-mainnet settlement before proposing work."
    output_hash=hashlib.sha256(txt.encode("utf-8")).hexdigest() if txt else None
    # A poor NEW model attempt must not destroy a previous genuinely graded
    # lesson. This is retained historical context, NOT a new successful run.
    retain_earlier=bool(old and old.get("practical_lesson_reusable") is True
                       and old.get("lesson") and not successful)
    reusable_lesson=(learned if successful and not repeated else
                     str(old.get("lesson") or "")[:MAX_TEXT] if retain_earlier else "")
    lesson_origin=("current_graded_training" if successful and not repeated
                   else "retained_previous_graded_training" if retain_earlier
                   else "none")
    return {
       "schema":VERSION,"worker":full,"immediate_parent":fleet+"/"+parent,
       "owner_order_id":order,
       "actual_process_pid":report["os_process_pid"],
       "completed_at_utc":str(report.get("completed_at_utc") or "")[:40],
       "real_model_response_proven":True,
       "training_inference_proven":practical.get("independent_model_call_status")=="MODEL_COMPLETED",
       "training_grade":grade,"source_url":source,
       "lesson":reusable_lesson,
       "lesson_origin":lesson_origin,
       "last_training_attempt_failed":not successful,
       "prior_good_lesson_preserved":retain_earlier,
       "original_training_draft_sha256":output_hash,
       "practical_lesson_reusable":bool(reusable_lesson),
       "previous_source_repeated":repeated,
       "failure_or_blocker":cause,"next_correction":correction,
       "prior_real_learner_receipt_read":old is not None,
       "worker_prior_model_runs_count":min(100000,int(old.get("worker_prior_model_runs_count",0))+1) if old else 1,
       "next_self_creation":"Produce one original buyer-specific checked sample only after verifying a genuine live paid scope.",
       "read_only_owner_payment_address_preserved":True,
       "new_external_permissions_granted":False,
       "buyer_accepted_work_verified":False,
       "actual_bitcoin_payment_verified":False,
       "earned_btc_sats":None,
       "live_miner_connected":False,
       "status":"ACTUAL_WORKER_LESSON_RECORDED_NOT_PAID"
    }

def save_receipt(obj,root=ROOT):
    p=location(*obj["worker"].split("/",1),root)
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    tmp.replace(p)
    return p

def self_test():
    fleet="transferexperiment";w="D01-M01-W01";p="D01-M01"
    good={"workforce_namespace":fleet,"globally_unique_agent_id":fleet+"/"+w,
     "parent_id":p,"strict_owner_order_id":"ORDER-X","os_process_invoked":True,
     "os_process_pid":184,"inference_status":"model_completed",
     "model_response":"Tested outline: buyer remains unverified",
     "actual_ai_model_received_complete_owner_prompt":True,
     "owner_to_last_leaf_prompt_receipt":{"model_response_present":True},
     "practical_training_while_working":{"independent_model_call_status":"MODEL_COMPLETED",
       "result":{"status":"APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW",
         "real_model_call_completed":True,"source_url":"https://example.org/issue",
         "actual_training_model_response":"SOURCE: Buyer not verified\nLEARNED: The original sponsor must explicitly fund the job\nBUILT: Test scope\nNEXT: Check budget"}}}
    first=create_receipt(good)
    assert first["real_model_response_proven"] and first["lesson"] and not first["actual_bitcoin_payment_verified"]
    assert create_receipt(good,first)["previous_source_repeated"]
    assert create_receipt(good,first)["failure_or_blocker"]=="SAME_UNVERIFIED_SOURCE_AS_PRIOR_RUN"
    weak=dict(good)
    weak_practical=dict(good["practical_training_while_working"])
    weak_result=dict(weak_practical["result"],status="MODEL_RESPONSE_INCOMPLETE_OR_SOURCE_NOT_VERIFIED",
                     actual_training_model_response="Weak attempted revision")
    weak_practical["result"]=weak_result
    weak["practical_training_while_working"]=weak_practical
    preserved=create_receipt(weak,first)
    assert preserved["last_training_attempt_failed"]
    assert preserved["prior_good_lesson_preserved"]
    assert preserved["lesson"]==first["lesson"]
    assert preserved["lesson_origin"]=="retained_previous_graded_training"
    assert preserved["actual_bitcoin_payment_verified"] is False
    bad=dict(good,inference_status="model_failed")
    try:create_receipt(bad)
    except ValueError:pass
    else:raise AssertionError("phantom model accepted")
    bad=dict(good,parent_id="D02-M01")
    try:create_receipt(bad)
    except ValueError:pass
    else:raise AssertionError("wrong parent accepted")
    import tempfile
    with tempfile.TemporaryDirectory() as root:
       assert load_prior(fleet,w,root) is None
       save_receipt(first,root)
       assert load_prior(fleet,w,root,"ORDER-X")["worker"]==fleet+"/"+w
       assert load_prior(fleet,w,root,"STALE-ORDER") is None
       assert "previous correction" in learning_prompt(fleet,w,root,"ORDER-X")
       assert load_prior("BountyScoutAI",w,root) is None
    print("ENIGMA_REAL_WORKER_LEARNING_PASS: actual model, exact parent, prior source dedup, atomic state, no fake payment")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--self-test",action="store_true")
    a.add_argument("--report")
    a.add_argument("--fleet",choices=FLEETS)
    a.add_argument("--worker")
    args=a.parse_args()
    if args.self_test:self_test()
    else:
        if not args.report or not args.fleet or not args.worker:
            a.error("--report --fleet --worker required")
        r=json.loads(Path(args.report).read_text(encoding="utf-8"))
        old=load_prior(args.fleet,args.worker,owner_order_id=r.get("strict_owner_order_id"))
        x=create_receipt(r,old)
        if x["worker"]!=identity(args.fleet,args.worker):raise ValueError("REPORT_WORKER_MISMATCH")
        p=save_receipt(x)
        print(json.dumps({"learning_checkpoint":str(p),"worker":x["worker"],
             "grade":x["training_grade"],"correction":x["next_correction"],
             "btc_received_verified":False}))
