"""Truthful one-shift D report from ACTUAL B worker artifact JSON files.

Scheduled role definitions, completed GitHub jobs, synthetic files and repeated
workers do not count as independent AI work. Failed slots remain missing.
"""
from __future__ import annotations
import argparse,json,tempfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

FLEETS=("transferexperiment","BountyScoutAI")
EXPECTED_PER_FLEET=2
QUALIFIED="APPLIED_ORIGINAL_DRAFT_NEEDS_INDEPENDENT_REVIEW"

def summarize(folder, run_url=""):
    files=list(Path(folder).glob("practical-work-*/D??-M??-W??.json"))
    # Full GitHub artifact tree may contain more source files; only root individual
    # worker report names count, and four different fleet/worker identities are required.
    records=[]
    seen=set()
    problems=[]
    for p in sorted(files):
        try:r=json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(p.name+":invalid_json:"+type(exc).__name__)
            continue
        company=r.get("workforce_namespace")
        worker=r.get("worker_id")
        if company not in FLEETS or not isinstance(worker,str):
            problems.append(str(p)+":invalid_fleet_or_worker")
            continue
        key=(company,worker)
        if key in seen:
            problems.append(str(p)+":duplicate_worker_identity")
            continue
        seen.add(key)
        training=(r.get("practical_training_while_working") or {})
        result=(training.get("result") or {})
        model_completed=(r.get("inference_status")=="model_completed")
        training_completed=(training.get("independent_model_call_status")=="MODEL_COMPLETED" and result.get("real_model_call_completed") is True)
        pid=r.get("os_process_pid")
        valid_pid=isinstance(pid,int) and pid>0
        trained=bool(model_completed and training_completed and valid_pid)
        original_source=(training.get("assignment") or {}).get("real_original_research_url") or ""
        quality=(result.get("status") or "NOT_EVALUATED")
        records.append({
          "company":company,"worker":worker,
          "actual_model_completed":bool(model_completed and valid_pid),
          "trained_with_real_separate_model_call":trained,
          "training_grade":quality,
          "source_url":original_source,
          "original_source_present":original_source.startswith("https://"),
          "direct_parent":r.get("parent_id") or (r.get("command_chain_assignment") or {}).get("direct_parent"),
          "real_pid":pid if valid_pid else None,
          "delivered_original_draft_needs_review":bool(trained and quality==QUALIFIED),
          "externally_submitted":False,
          "genuine_buyer_acceptance_verified":False,
          "cryptocurrency_receipt_verified":"NOT_ASSESSED_BY_THIS_SHIFT",
        })
    by_company={}
    for company in FLEETS:
        company_rows=[z for z in records if z["company"]==company]
        by_company[company]={
          "expected_slots":EXPECTED_PER_FLEET,
          "reported_unique_workers":len(company_rows),
          "actual_model_completions":sum(z["actual_model_completed"] for z in company_rows),
          "real_training_completions":sum(z["trained_with_real_separate_model_call"] for z in company_rows),
          "original_drafts_needing_review":sum(z["delivered_original_draft_needs_review"] for z in company_rows),
          "missing_or_unverified_slots":max(0,EXPECTED_PER_FLEET-sum(z["trained_with_real_separate_model_call"] for z in company_rows)),
        }
    summary={
      "schema":"B_ACTUAL_RECURRING_SHIFT_REPORT_V1",
      "created_utc":datetime.now(timezone.utc).isoformat(),
      "run_url":run_url,
      "expected_total_actual_worker_slots":2*EXPECTED_PER_FLEET,
      "actually_completed_model_workers":sum(z["actual_model_completed"] for z in records),
      "actual_independent_training_completions":sum(z["trained_with_real_separate_model_call"] for z in records),
      "quality_graded_original_work_drafts":sum(z["delivered_original_draft_needs_review"] for z in records),
      "actual_customer_contact_verified":0,
      "actual_paid_contracts_verified":0,
      "crypto_payments_verified":"NOT_ASSESSED_BY_THIS_SHIFT",
      "company_reports":by_company,
      "individual_worker_evidence":records,
      "anomalies":problems,
      "note":"One shift proves only its actual worker subprocess/model reports. These are ephemeral, not continuous. Drafts need independent source, licence, quality and buyer acceptance checks. No onchain payment claimed."
    }
    return summary

def write(out,summary):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"CHIEF_D_SHIFT.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Chief D — two independent B-company REAL worker shift","",
     "Executed AI workers: **"+str(summary["actually_completed_model_workers"])+"/"+str(summary["expected_total_actual_worker_slots"])+"**",
     "Applied-training AI completions: **"+str(summary["actual_independent_training_completions"])+"**",
     "Original drafts needing supervisor review: **"+str(summary["quality_graded_original_work_drafts"])+"**",
     "Genuine accepted customer jobs: **not verified by this shift**",
     "Confirmed new coins: **not assessed by this shift**","",
     "| Company | Scheduled slots | Model calls completed | Practical lessons completed | Drafts for review | Missing/unverified |",
     "|---|---:|---:|---:|---:|---:|"]
    for company, x in summary["company_reports"].items():
        lines.append(f"| {company} | {x['expected_slots']} | {x['actual_model_completions']} | {x['real_training_completions']} | {x['original_drafts_needing_review']} | {x['missing_or_unverified_slots']} |")
    lines.extend(["","## Individual executed worker evidence"])
    for z in summary["individual_worker_evidence"]:
        lines.append(f"- **{z['company']}/{z['worker']}** → parent {z['direct_parent'] or 'not established'}; model={z['actual_model_completed']}; on-job training={z['trained_with_real_separate_model_call']}; grade={z['training_grade']}; source={z['source_url'] or 'NONE'}")
    if summary["anomalies"]:lines.extend(["","## Inconsistent input",*[f"- {x}" for x in summary["anomalies"]]])
    lines+=["","Software-collected supervisor evidence is not independent AI manager acknowledgment. A role is active only during actual execution. Company directors should correct weak drafts and obtain authenticated buyer acceptance before billing."]
    (out/"CHIEF_D_SHIFT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("REAL_B_SHIFT_CHIEF_D",json.dumps({k:summary[k] for k in ("actually_completed_model_workers","actual_independent_training_completions","quality_graded_original_work_drafts","actual_customer_contact_verified","actual_paid_contracts_verified")}))
def selftest():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"practical-work-transferexperiment-slot-0";p.mkdir()
        record={"workforce_namespace":"transferexperiment","worker_id":"D01-M01-W01","parent_id":"D01-M01","os_process_pid":42,"inference_status":"model_completed","practical_training_while_working":{
          "independent_model_call_status":"MODEL_COMPLETED","assignment":{"real_original_research_url":"https://github.com/a/b/issues/1"},
          "result":{"real_model_call_completed":True,"status":QUALIFIED}
        }}
        (p/"D01-M01-W01.json").write_text(json.dumps(record))
        x=summarize(d)
        assert x["actually_completed_model_workers"]==1,x
        assert x["actual_independent_training_completions"]==1,x
        assert x["quality_graded_original_work_drafts"]==1,x
        assert x["company_reports"]["BountyScoutAI"]["missing_or_unverified_slots"]==2,x
        assert x["actual_paid_contracts_verified"]==0
        write(Path(d)/"report",x)
    print("B_SHIFT_AGGREGATE_SELFTEST_PASS")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--inputs",default="shift-evidence")
    parser.add_argument("--output",default="shift-chief-D")
    parser.add_argument("--run-url",default="")
    a=parser.parse_args()
    if a.self_test:selftest()
    else:write(a.output,summarize(a.inputs,a.run_url))
