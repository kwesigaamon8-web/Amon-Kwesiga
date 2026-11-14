"""Evidence-only roll-up of ACTUALLY invoked B workers to supervisors, managers,
company directors and ONE Chief D. Software forwarding is not a live manager acknowledgement.
"""
import argparse, json, os, re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

FLEETS=("transferexperiment","BountyScoutAI")
DIRECTORS=[f"D{i:02d}" for i in range(1,11)]
LIMITS=(("M",15,2),("W",50,2),("S",150,3),("G",500,3),("H",666,3))

def chain(role):
    parts=role.split("-") if isinstance(role,str) else []
    if not 3<=len(parts)<=6 or not re.fullmatch(r"D(?:0[1-9]|10)",parts[0]):
        raise ValueError("Invalid worker ID")
    for i,part in enumerate(parts[1:]):
        tag,maximum,width=LIMITS[i]
        if not re.fullmatch(tag+r"\d{"+str(width)+r"}",part) or not 1<=int(part[1:])<=maximum:
            raise ValueError("Invalid level/slot")
    return ["-".join(parts[:i]) for i in range(1,len(parts)+1)]

def read(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError): return None

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def short(value,n=250):
    return " ".join(str(value or "").split())[:n]

def generate(root,strict_file,out,fleet,run_url=""):
    if fleet not in FLEETS: raise ValueError("Unknown company")
    strict=read(strict_file) or {}
    if strict and strict.get("fleet")!=fleet: raise ValueError("Wrong-company strict grade")
    grades={x.get("id"):x for x in strict.get("individual_results",[]) if isinstance(x,dict)}
    out=out/fleet
    out.mkdir(parents=True,exist_ok=True)
    workers={}
    inbox=defaultdict(set)
    direct=defaultdict(set)
    handoffs=[]
    problems=[]
    missing=[]
    for director in DIRECTORS:
        manifest=read(root/("manifest-"+director+".json"))
        if manifest is None:
            missing.append(director)
            continue
        if manifest.get("director_id")!=director or manifest.get("workforce_namespace")!=fleet:
            problems.append("INVALID_MANIFEST:"+director)
            continue
        for wid in manifest.get("worker_processes_selected",[]):
            try:
                path=chain(wid)
                if path[0]!=director: raise ValueError("Wrong director")
                if wid in workers: raise ValueError("Duplicate worker ID")
            except ValueError as err:
                problems.append(short(wid,100)+":"+str(err))
                continue
            data=read(root/(wid+".json")) or {}
            grade=grades.get(fleet+"/"+wid,{})
            parent=path[-2]
            status="MODEL_COMPLETED_NEEDS_REVIEW"
            if data.get("worker_id")!=wid or data.get("globally_unique_agent_id")!=fleet+"/"+wid or data.get("workforce_namespace")!=fleet or data.get("director_id")!=director:
                status="WRONG_IDENTITY_OR_COMPANY"
            elif data.get("parent_id")!=parent:
                status="WRONG_DIRECT_SUPERVISOR"
            elif not data.get("os_process_pid") or data.get("inference_status")!="model_completed" or not short(data.get("model_response")):
                status="NO_COMPLETED_MODEL_EVIDENCE"
            checkpoint=data.get("cognitive_checkpoint") or {}
            activation=data.get("activation_evidence") or {}
            sources=[x.get("url") for x in (data.get("source_items") or []) if isinstance(x,dict) and str(x.get("url") or "").startswith("https://")][:3]
            row={
                "worker_id":fleet+"/"+wid,"direct_parent":fleet+"/"+parent,
                "director":fleet+"/"+director,"level":path[-1].split("-")[-1][0],
                "actual_execution_status":status,"strict_grade":grade.get("grade","NOT_GRADED"),
                "strict_defects":grade.get("defects",[])[:15],
                "pid":data.get("os_process_pid"),
                "model_output_excerpt":short(data.get("model_response"),300),
                "source_links_unverified_as_paying":sources,
                "next_action":short(checkpoint.get("next_action") or activation.get("next_step_checkpoint"),300),
                "latest_order_id":data.get("strict_owner_order_id"),
                "route_to_D":[fleet+"/"+x for x in path[::-1]]+["CHIEF_D"],
                "manager_accepted_or_acknowledged":False,
                "verified_paying_customer":False,
                "verified_crypto_income":"NOT_ASSESSED",
            }
            workers[wid]=row
            save(out/"workers"/(wid+".json"),row)
            (out/"workers"/(wid+".md")).write_text(
                "# Individual B report — "+fleet+"/"+wid+"\n\n"+
                "Direct parent: "+fleet+"/"+parent+"\n\n"+
                "Model status: "+status+"\n\nStrict grade: "+row["strict_grade"]+
                "\n\nOwn model response: "+(row["model_output_excerpt"] or "None")+
                "\n\nNext earning action: "+(row["next_action"] or "Not provided; corrective work required")+
                "\n\nOriginal research links (not verified payers): "+", ".join(sources)+
                "\n\nDefects: "+", ".join(row["strict_defects"])+"\n\n"+
                "Route: "+" → ".join(row["route_to_D"])+
                "\n\nSoftware forwarded this report; no live parent review or coin receipt is implied.\n",encoding="utf-8")
            for index in range(len(path)-1,0,-1):
                child,supervisor=path[index],path[index-1]
                inbox[supervisor].add(wid)
                if index==len(path)-1: direct[supervisor].add(wid)
                handoffs.append({"worker":wid,"from":fleet+"/"+child,"to":fleet+"/"+supervisor,
                                 "type":"AUTOMATED_EVIDENCE_FORWARD_NOT_SUPERVISOR_ACK"})
            handoffs.append({"worker":wid,"from":fleet+"/"+director,"to":"CHIEF_D",
                             "type":"COMPANY_DIRECTOR_AGGREGATION_AVAILABLE"})
    supervisors={}
    for parent,members in sorted(inbox.items()):
        rows=[workers[w] for w in sorted(members)]
        count_good=sum(x["actual_execution_status"]=="MODEL_COMPLETED_NEEDS_REVIEW" for x in rows)
        qualified=sum(x["strict_grade"]=="QUALIFIED_SOURCE_BACKED_AI_RESEARCH" for x in rows)
        tier="director" if re.fullmatch(r"D(?:0[1-9]|10)",parent) else ("manager" if parent.count("-")==1 else "intermediate")
        node={"company":fleet,"supervisor":fleet+"/"+parent,"tier":tier,
              "attempted_descendant_reports":len(rows),"direct_attempted_children":len(direct[parent]),
              "model_completions":count_good,"strict_qualified":qualified,
              "requiring_correction":sum(x["actual_execution_status"]!="MODEL_COMPLETED_NEEDS_REVIEW" or x["strict_grade"]!="QUALIFIED_SOURCE_BACKED_AI_RESEARCH" for x in rows),
              "worker_reports":sorted(members),
              "suggested_actions":[{"worker":x["worker_id"],"action":x["next_action"]} for x in rows if x["next_action"]][:5],
              "deterministic_review_completed":True,"real_supervisor_model_review_verified":False,
              "inbox_status":"ARTIFACT_READY_NOT_LIVE_MANAGER_ACKNOWLEDGED",
              "accepted_paid_contracts_verified":0,"coins_received":"NOT_ASSESSED"}
        supervisors[parent]=node
        save(out/tier/(parent+".json"),node)
        (out/tier/(parent+".md")).write_text(
            "# "+fleet+"/"+parent+" — supervisor inbox\n\n"+
            "Received from actual attempted B workers: "+str(len(rows))+
            "\nCompleted independent worker model outputs: "+str(count_good)+
            "\nReports to correct: "+str(node["requiring_correction"])+
            "\n\nActual independent manager/director AI review: NOT VERIFIED.\n\n"+
            "Workers: "+", ".join(sorted(members)[:50])+("\nMore in JSON." if len(members)>50 else "")+
            "\n\nNext: audit defects, send legitimate paying lead to local D10, escalate evidence to director/Chief D.\n",
            encoding="utf-8")
    directors=[{"director":fleet+"/"+d,
                "manifest_present":d not in missing,
                "attempted_workers":supervisors.get(d,{}).get("attempted_descendant_reports",0),
                "completed_model_reports":supervisors.get(d,{}).get("model_completions",0),
                "corrections":supervisors.get(d,{}).get("requiring_correction",0)} for d in DIRECTORS]
    final={"schema":"ACTUAL-B-REPORTING-CHAIN-v1","as_of_utc":datetime.now(timezone.utc).isoformat(),
           "company":fleet,"chief":"D","github_run_url":run_url,"source_worker_model_run_id":os.environ.get("SOURCE_WORKER_RUN_ID"),
           "route":"Executed H > G > S > W > manager > director > Chief D (shorter for W/S/G)",
           "attempted_worker_reports":len(workers),
           "completed_worker_model_reports":sum(x["actual_execution_status"]=="MODEL_COMPLETED_NEEDS_REVIEW" for x in workers.values()),
           "strict_qualified_research_reports":sum(x["strict_grade"]=="QUALIFIED_SOURCE_BACKED_AI_RESEARCH" for x in workers.values()),
           "supervisor_inboxes":len(supervisors),"recorded_handoffs":len(handoffs),
           "directors":directors,"missing_director_manifests":missing,"anomalies":problems,
           "actual_parent_AI_reviews_verified":0,"real_customer_acceptance_verified_by_this_report":0,
           "new_crypto_payment_verified_by_this_report":"NOT_ASSESSED_NO_CHAIN_QUERY",
           "caveat":"Software forwarding and deterministic checks do not establish live manager acknowledgements, payer agreements, external contact or wallet deposits."}
    save(out/"CHIEF_D_COMPANY_REPORT.json",final)
    save(out/"HANDOFFS.json",handoffs)
    lines=["# "+fleet+" → Chief D: complete executed-worker reporting chain","",
           "**Actual attempted workers:** "+str(final["attempted_worker_reports"]),
           "**Completed independent model reports:** "+str(final["completed_worker_model_reports"]),
           "**Strict-qualified source reports:** "+str(final["strict_qualified_research_reports"]),
           "**Parent/manager/director inboxes populated:** "+str(final["supervisor_inboxes"]),
           "**Software-recorded forwarding links:** "+str(final["recorded_handoffs"]),
           "**Live supervisor model reviews:** 0 established by this report",
           "**Confirmed incoming crypto:** NOT ASSESSED by this report","",
           "## Directors (each has individual manager and worker files)"]
    lines += ["- "+x["director"]+": "+str(x["attempted_workers"])+" reports; "+str(x["completed_model_reports"])+" models completed; "+str(x["corrections"])+" corrections" for x in directors]
    lines += ["","All actual worker records live under workers/, each intermediate parent under intermediate/, managers under manager/, company directors under director/. HANDOFFS.json traces every escalation. No dormant role is reported as active.","",
              "Run: "+(run_url or "local regression")]
    (out/"CHIEF_D_COMPANY_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return final

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fleet",default=os.environ.get("WORKFORCE_ID",""))
    p.add_argument("--root",default="combined-ai-processes/ai-process-reports")
    p.add_argument("--strict",default="")
    p.add_argument("--out",default="hierarchical-reports")
    x=p.parse_args()
    url="https://github.com/"+os.environ.get("GITHUB_REPOSITORY","kwesigaamon8-web/Amon-Kwesiga")+"/actions/runs/"+os.environ["GITHUB_RUN_ID"] if os.environ.get("GITHUB_RUN_ID") else ""
    result=generate(Path(x.root),Path(x.strict or "strict-worker-accountability/strict-"+x.fleet+".json"),Path(x.out),x.fleet,url)
    print("B_TO_CHIEF_D",json.dumps({"fleet":x.fleet,"attempts":result["attempted_worker_reports"],
          "model_completions":result["completed_worker_model_reports"],"software_handoffs":result["recorded_handoffs"]}))
if __name__=="__main__":main()
