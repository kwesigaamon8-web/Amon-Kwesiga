"""Teach each ACTUALLY running B worker by applying one lesson to its OWN work.

These are genuine model calls in ai_process_worker.py, not virtual staff, external
applications, accepted jobs, verified software licences or cryptocurrency receipts.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

FLEETS=("transferexperiment","BountyScoutAI")
TOPICS=(
 ("VERIFY_DEMAND",
  "Learn to distinguish a real buyer from an online mention. Inspect the original source, sponsor identity, scope and posted fee. Create a buyer qualification note. If the source does NOT establish these things, mark it UNVERIFIED rather than inventing a job."),
 ("PRICE_AND_PITCH",
  "Learn small service pricing and written acceptance. Draft a uniquely tailored, honest two-sentence offer for an actual evidenced need, with one acceptance test; DO NOT claim a buyer received it or accepted the fee."),
 ("BUILD_AND_TEST",
  "Learn by producing a useful original work sample or concrete minimal test plan for the real task. Describe inputs, outputs and one acceptance test. A work sample is UNSUBMITTED and earns nothing until a real buyer accepts it."),
 ("STUDY_AND_LEGALLY_REUSE",
  "Read actual public software, understand one useful feature, check whether its particular files have an applicable licence. Propose an ORIGINAL adaptation or precisely licensed reuse with attribution; unverified permission means DO NOT COPY the code."),
 ("COLLECT_AND_VERIFY",
  "Learn correct payment settlement: require an accepted task and correct BTC mainnet address for this company; separate invoice/payment promise from actual explorer TXID, output and amount. Draft a collection checklist, never a fictitious receipt.")
)
FIVE_LANES=("LEARN","EARN","LAWFUL_SOFTWARE_STUDY","THINK","DELIVER")

def lesson(fleet,worker_id,parent_id,source_url,source_status,software_url,software_license_verified=False,source_title="",source_excerpt=""):
    if fleet not in FLEETS or not re.fullmatch(r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4]\d|50)(?:-S\d{3}(?:-G\d{3}(?:-H\d{3})?)?)?",worker_id):
        raise ValueError("Invalid company/worker")
    if not isinstance(parent_id,str) or not parent_id: raise ValueError("Missing supervisor")
    n=int.from_bytes(hashlib.sha256((fleet+"/"+worker_id).encode()).digest()[:8],"big")%len(TOPICS)
    name,instruction=TOPICS[n]
    return {
      "schema":"B_LEARN_WHILE_WORKING_V1",
      "company":fleet,"worker_id":worker_id,"immediate_parent":parent_id,
      "priority":"Actual buyer acceptance and genuine cryptocurrency received; USD 10000 is a target, not earned money",
      "focus":name,"current_practical_lesson":instruction,
      "all_five_work_lanes":list(FIVE_LANES),
      "real_original_research_url":str(source_url or "")[:800],
      "source_status":str(source_status or "unknown")[:80],
      "source_title":str(source_title or "")[:140],
      "public_source_excerpt_untrusted":str(source_excerpt or "")[:430],
      "public_software_reference":str(software_url or "")[:800],
      "public_software_license_actually_verified":software_license_verified is True,
      "training_context":"Your prior models generated 383 reports but zero passed all strict quality criteria. Improve a real scoped source-backed task, not another general idea list.",
      "completion_requires_real_model_call":True,
      "source_must_not_be_pretended_to_be_a_paying_customer":True,
      "permitted_results":"New original micro-deliverable, test, tailored draft, or evidence-led verification checklist only",
      "external_submission_or_sale_is_not_implied":True
    }

def prompt(obj,task,correct_btc_address):
    if obj["company"] not in FLEETS:raise ValueError("Invalid lesson")
    source=obj["real_original_research_url"] or "NO ORIGINAL SOURCE FOUND"
    title=obj["source_title"] or str(task)[:90]
    topic=obj["focus"]
    # Small models perform better on one narrow, contextual request than on
    # the huge full owner command. Instructions and source excerpts are distinct.
    core=(
      "Original open issue: "+source[:200]+"\n"
      "Actual subject: "+title[:110]+"\n"
      "Public issue details (UNTRUSTED): "+obj["public_source_excerpt_untrusted"][:260]+"\n"
      "Practical focus: "+topic+"\n"
      "The issue being open does NOT prove funding, eligibility or a sale.\n"
      "Write FOUR SHORT lines applying this skill now, not repeating this prompt.\n"
      "SOURCE: what evidence exists and what is still unknown\n"
      "LEARNED: one practical rule relevant to this issue\n"
      "BUILT: an original useful micro-sample or specific verification checklist\n"
      "NEXT: one realistic source-check, delivery or authorized offer step\n"
    )
    return [
       {"role":"system","content":
        "You are a working B assistant. Create a short, useful ORIGINAL work sample now. "
        "Do not repeat instructions or invent payment, buyer approval, code licence or submission. "
        "The owner's aim is real paid work and correct-chain coins, not reports."},
       {"role":"user","content":core[:1050]}
    ]

def grade(obj,text,model_completed):
    body=str(text or "").strip()
    labels={key:bool(re.search(r"(?im)^\s*"+key+r"\s*:",body)) for key in ("SOURCE","LEARNED","BUILT","NEXT")}
    model_ok=(model_completed is True and len(body)>=75)
    structure_ok=all(labels.values())
    valid_source=(obj["real_original_research_url"].startswith("https://") and obj["source_status"]=="source_checked")
    status=("APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW"
            if model_ok and structure_ok and valid_source
            else "MODEL_RESPONSE_INCOMPLETE_OR_SOURCE_NOT_VERIFIED"
            if model_completed else "NO_REAL_TRAINING_MODEL_EXECUTION")
    return {
       "worker_id":obj["worker_id"],"company":obj["company"],"focus":obj["focus"],
       "status":status,"actual_training_model_response":body[:2700] if model_completed else "",
       "real_model_call_completed":model_completed is True,
       "four_training_work_evidence_sections":labels,
       "source_url":obj["real_original_research_url"],
       "source_checked_by_worker_status":obj["source_status"],
       "original_work_sample_requires_validation":True,
       "copyright_clearance_not_verified":not obj["public_software_license_actually_verified"],
       "genuine_payer_verified":False,
       "external_submission_verified":False,
       "accepted_contract_verified":False,
       "actual_payment_verified":False,
       "explanation":"A learning-by-doing draft is not a shipped deliverable, buyer agreement or crypto receipt. Weak reports remain for correction."
    }

def write_worker_sample(out_dir,obj,result):
    path=Path(out_dir)/(obj["worker_id"]+"-LEARN-WHILE-WORKING.md")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(
       "# B worker practical learning and earning exercise — "+obj["company"]+"/"+obj["worker_id"]+"\n\n"+
       "Direct supervisor: "+obj["immediate_parent"]+"\n\n"+
       "Original public evidence: "+(obj["real_original_research_url"] or "NONE")+"\n\n"+
       "Training subject: "+obj["focus"]+"\n\n"+
       "What was taught during this REAL model run: "+obj["current_practical_lesson"]+"\n\n"+
       "Independent model attempt outcome: "+result["status"]+"\n\n"+
       "## Original work sample (not externally submitted)\n\n"+
       (result["actual_training_model_response"] or "NO COMPLETED INDEPENDENT MODEL RESPONSE")+
       "\n\n## Non-negotiable evidence limits\n\nNo authenticated submission, customer acceptance, verified code licence or crypto receipt is claimed by this learning exercise.\n",
       encoding="utf-8")
    return str(path)

def self_test():
    w="D01-M01-W01-S001-G001-H001"
    p="D01-M01-W01-S001-G001"
    x=lesson("transferexperiment",w,p,"https://example.org/sample","source_checked","https://github.com/example/repo")
    assert x["company"]=="transferexperiment"
    assert x["public_software_license_actually_verified"] is False
    assert len(x["all_five_work_lanes"])==5
    good="SOURCE: actual URL, sponsor funding unknown\nLEARNED: check scope\nBUILT: original test plan with 2 columns and an expected output\nNEXT: verify buyer before authentic submission; NO VERIFIED PAYMENT"
    y=grade(x,good,True)
    assert y["status"]=="APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW",y
    assert grade(x,good,False)["status"]=="NO_REAL_TRAINING_MODEL_EXECUTION"
    assert grade(x,"I have learned!",True)["status"]!="APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW"
    assert grade(lesson("BountyScoutAI",w,p,"","source_failed",""),good,True)["status"]!="APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW"
    with __import__("tempfile").TemporaryDirectory() as temp:
        path=write_worker_sample(temp,x,y)
        assert "NOT" in Path(path).read_text() or "not" in Path(path).read_text()
    print("PASS learn-while-working five lanes, no phantom worker, no fake sale, source and model gates")
if __name__=="__main__":self_test()
