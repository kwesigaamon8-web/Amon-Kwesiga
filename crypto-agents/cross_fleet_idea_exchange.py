"""Two-fleet public idea sharing from ACTUAL model evidence, not 7B phantom agents."""
import argparse,hashlib,json,os,re,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
FLEETS=("transferexperiment","BountyScoutAI")
REPO="kwesigaamon8-web/Amon-Kwesiga"
URL="https://api.github.com/repos/"+REPO+"/issues/9/comments"
OUT=Path("idea-exchange")
OUT.mkdir(exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def textclean(x):
    x=" ".join(str(x or "").split())
    x=re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}","[email withheld]",x)
    x=re.sub(r"(?i)(password|seed phrase|private key|api token).{0,55}","[redacted]",x)
    return x[:250]
def acceptable(x):
    low=x.lower()
    bad=any(t in low for t in ("send money first","private key","pay deposit","guaranteed btc","spam","steal","malware"))
    concrete=any(t in low for t in ("document","data","code","test","audit","build","fix","translate","research","customer","client","spreadsheet","service","bounty","design","miner","website"))
    return not bad and concrete and len(x)>=28
def github(url,method="GET",data=None):
    h={"Accept":"application/vnd.github+json","User-Agent":"ChiefDIdeaExchange/1.0"}
    if os.getenv("GH_TOKEN"):h["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
    req=urllib.request.Request(url,headers=h,
       data=(json.dumps(data).encode() if data is not None else None),method=method)
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def compile_digest(fleet,runid,docs,strict):
    if fleet not in FLEETS or not str(runid).isdigit():raise ValueError("Company/run invalid")
    evidence={r.get("id"):r for r in strict.get("individual_results",[])}
    seen=set();ideas=[];counts=Counter();fingerprints=set()
    for doc in docs:
        if doc.get("workforce_namespace")!=fleet or doc.get("inference_status")!="model_completed":continue
        worker=fleet+"/"+str(doc.get("worker_id",""))
        if worker in seen:continue
        seen.add(worker);counts["actual_model_main_responses"]+=1
        if doc.get("ten_idea_model_inference_status") not in ("MODEL_INFERENCE_COMPLETED","MODEL_CORRECTIVE_RETRY_COMPLETED"):
            counts["no_real_model_idea_inference"]+=1;continue
        counts["actual_idea_model_responses"]+=1
        r=doc.get("ten_idea_model_result") or {}
        if r.get("has_all_ten_distinct_numbered_ideas"):counts["full_ten_distinct"]+=1
        sources=[e.get("url") for e in doc.get("source_items",[]) if isinstance(e,dict) and
                 str(e.get("url","")).startswith("https://github.com/")][:2]
        for item in r.get("model_generated_ideas",[])[:3]:
            idea=textclean(item.get("text",""))
            if not acceptable(idea):counts["failed_idea_quality"]+=1;continue
            digest=hashlib.sha256(idea.lower().encode()).hexdigest()
            if digest in fingerprints:counts["repeated_idea"]+=1;continue
            fingerprints.add(digest)
            if len(ideas)<16:
                ideas.append({"idea":idea,"hash":digest,"worker":worker,
                   "director":fleet+"/"+str(doc.get("director_id","")),
                   "source_urls":sources,"strict_grade":evidence.get(worker,{}).get("grade","NOT_GRADED"),
                   "model_idea_status":r.get("status","NOT_QUALIFIED"),
                   "actual_model_response":True,"buyer_verified":False,"income_verified":False})
    return {"schema":"b-fleet-model-idea-digest-v1","fleet":fleet,"run_id":str(runid),
      "created_at_utc":now(),"counts":dict(counts),"actual_model_idea_excerpts":ideas,
      "proven_independent_ai_peer_reviews":0,"verified_new_coin_receipts":0,
      "evidence":"https://github.com/"+REPO+"/actions/runs/"+str(runid),
      "caveat":"Worker model text is NOT sponsor-verified work, buyer acceptance, independently completed peer review or cryptocurrency income."}
def comments():
    for page in range(1,4):
        arr=github(URL+"?"+urllib.parse.urlencode({"per_page":100,"page":page}))
        for x in arr:yield x
        if len(arr)<100:break
def share(fleet,run_id):
    if os.getenv("GITHUB_REPOSITORY")!=REPO or not os.getenv("GH_TOKEN"):
        print("IDEA_SHARE_BLOCKED_NO_AUTH");return
    path=Path("strict-worker-accountability/strict-"+fleet+".json")
    if not path.exists():
        print("IDEA_SHARE_BLOCKED_NO_EXECUTED_REPORT");return
    reports=[]
    for p in Path("combined-ai-processes/ai-process-reports").glob("D??-M*-W*.json"):
        try:reports.append(json.loads(p.read_text()))
        except (OSError,ValueError):pass
    d=compile_digest(fleet,run_id,reports,json.loads(path.read_text()))
    (OUT/("B_MODEL_IDEAS_"+fleet+".json")).write_text(json.dumps(d,indent=2)+"\n")
    marker="<!-- actual-b-idea-share:"+fleet+":"+str(run_id)+" -->"
    if any(marker in str(x.get("body") or "") for x in comments()):
        print("IDEA_SHARE_EXISTING",fleet,run_id);return
    body=marker+"\n## Real B worker idea evidence — "+fleet+"\n"+
       "The following are unverified actual-model excerpts. No payer or coins proven.\n"+
       "BEGIN_B_IDEA_JSON\n"+json.dumps(d,ensure_ascii=False,separators=(",",":"))+
       "\nEND_B_IDEA_JSON\n"
    r=github(URL,"POST",{"body":body})
    print("B_IDEA_SHARE_POSTED",r.get("html_url"),d["counts"])
def read_digests():
    out={};errors=[]
    if not os.getenv("GH_TOKEN"):
        return {},["GITHUB_TOKEN_NOT_AVAILABLE"]
    try:
        for row in comments():
            who=(row.get("user") or {}).get("login")
            if who not in ("github-actions[bot]","kwesigaamon8-web"):continue
            body=str(row.get("body") or "")
            match=re.search(r"<!-- actual-b-idea-share:(transferexperiment|BountyScoutAI):(\d+) -->",body)
            m=re.search(r"BEGIN_B_IDEA_JSON\s*([\s\S]*?)\s*END_B_IDEA_JSON",body)
            if not match or not m:continue
            try:doc=json.loads(m.group(1))
            except ValueError:continue
            fleet,run=match.groups()
            if doc.get("schema")!="b-fleet-model-idea-digest-v1" or doc.get("fleet")!=fleet or doc.get("run_id")!=run:continue
            if str(row.get("created_at",""))>out.get(fleet,{}).get("created_at",""):
                out[fleet]={"created_at":row.get("created_at",""),
                            "url":row.get("html_url"),"data":doc}
    except Exception as e:errors.append(type(e).__name__+":"+str(e)[:100])
    return out,errors
def make_actions(digests,lead_doc):
    actual=[];seen=set();stats=Counter()
    for source,wrapped in digests.items():
        for item in wrapped.get("data",{}).get("actual_model_idea_excerpts",[])[:16]:
            idea=textclean(item.get("idea"))
            fp=hashlib.sha256(idea.lower().encode()).hexdigest()
            if fp!=item.get("hash") or not item.get("worker","").startswith(source+"/"):
                stats["invalid_provenance"]+=1;continue
            if not acceptable(idea) or fp in seen:
                stats["weak_or_duplicate"]+=1;continue
            seen.add(fp)
            target=FLEETS[1] if source==FLEETS[0] else FLEETS[0]
            director=target+"/D"+str(1+int(fp[:4],16)%9).zfill(2)
            actual.append({"origin_company":source,"actual_worker":item["worker"],
                "idea":idea,"original_source_urls":item.get("source_urls",[])[:2],
                "cross_company_evaluating_director":director,
                "reviewer_ai_model_actually_ran":False,
                "status":"ASSIGNED_DETERMINISTIC_SOURCE_REVIEW_NOT_COMPLETED",
                "payer_confirmed":False,"coin_receipt_confirmed":False,
                "next_action":"Verify current original buyer, reward, due date, eligibility and network; deliver a small lawful sample only when permitted."})
    leads=[]
    for x in (lead_doc or {}).get("candidates",[])[:40]:
        url=x.get("original_url","")
        d=x.get("assigned_company_director","")
        if str(url).startswith("https://github.com/") and d.split("/")[0] in FLEETS:
            leads.append({"source_url":url,"title":textclean(x.get("title")),
                "director":d,"status":"SOURCE_LEAD_NOT_VERIFIED_FUNDED_OR_AVAILABLE",
                "next_action":"Open sponsor's actual issue/latest comments, validate reward and scope, propose deliverable if allowed.",
                "accepted_customer":False,"income_verified":False})
    return {"owner_order":"OWNER-20261114-084438","created_at_utc":now(),
        "billion_role_target":7000000000,
        "actual_model_idea_digests_available":len(digests),
        "actual_model_idea_excerpts_cross_shared":len(actual),
        "cross_fleet_auto_review_issues":dict(stats),
        "cross_company_model_peer_reviews_evidenced":0,
        "actual_idea_exchange_assignments":actual[:32],
        "sponsor_verification_actions":leads,
        "real_revenue_agreements_verified_by_this_job":0,
        "new_coin_receipts_verified_by_this_job":"NOT_ASSESSED",
        "status":"Action assignments to existing company boards; no new external contact or AI process launched."}
def review():
    docs,errors=read_digests()
    try:leads=json.loads(Path("paid-opportunity-reports/new-earning-lanes.json").read_text())
    except (OSError,ValueError):leads={}
    data=make_actions(docs,leads)
    data["source_errors"]=errors
    data["digest_source_links"]={k:v["url"] for k,v in docs.items()}
    (OUT/"CHIEF_D_CROSS_COMPANY_ACTIONS.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Chief D: across-company idea review and actionable source queue","",
       "Real model digests available: "+str(len(docs))+"/2",
       "Individual real-model idea excerpts passed preliminary dedup: "+str(len(data["actual_idea_exchange_assignments"])),
       "Outside client opportunities needing sponsor checks: "+str(len(data["sponsor_verification_actions"])),
       "AI-to-AI model peer reviews verified: 0 (automatic checks only)",
       "External contacts or coins paid as a result of this review: NOT VERIFIED",""]
    for item in data["actual_idea_exchange_assignments"][:8]:
        lines.append("- "+item["cross_company_evaluating_director"]+" to check: "+item["idea"]+
            " — source: "+(item["original_source_urls"][0] if item["original_source_urls"] else "missing"))
    lines+=["","## Real original listing follow-ups"]
    for item in data["sponsor_verification_actions"][:12]:
        lines.append("- "+item["director"]+": "+item["title"]+" — "+item["source_url"])
    lines+=["","A registered 7B-role hierarchy can read this shared evidence on activation; these are NOT 7B executed agents. No paid acceptance, private key, outside miner consent, or transaction is inferred."]
    (OUT/"CHIEF_D_CROSS_COMPANY_ACTIONS.md").write_text("\n".join(lines)+"\n")
    print("B_CROSS_IDEA_REVIEW",json.dumps({"real_digest_companies":len(docs),
       "shared_model_ideas":len(data["actual_idea_exchange_assignments"]),
       "original_source_leads_to_check":len(data["sponsor_verification_actions"]),
       "actually_completed_AI_peer_reviews":0,"coins_received":"not_assessed"}))
def selftest():
    w={"workforce_namespace":FLEETS[0],"worker_id":"D01-M01-W01","director_id":"D01",
       "inference_status":"model_completed","ten_idea_model_inference_status":"MODEL_INFERENCE_COMPLETED",
       "ten_idea_model_result":{"status":"INCOMPLETE_OR_REPEATED_MODEL_IDEAS",
          "model_generated_ideas":[{"number":1,"text":"Build a spreadsheet cleanup service and document client requirements before charging"}]},
       "source_items":[{"url":"https://github.com/org/app/issues/1"}]}
    d=compile_digest(FLEETS[0],123,[w],{"individual_results":[]})
    assert d["counts"]["actual_model_main_responses"]==1
    assert len(d["actual_model_idea_excerpts"])==1
    m=make_actions({FLEETS[0]:{"data":d}},{"candidates":[{"original_url":"https://github.com/org/repo/issues/1",
      "assigned_company_director":"BountyScoutAI/D02","title":"Test bounty"}]})
    assert m["actual_model_idea_excerpts_cross_shared"]==1
    assert m["actual_idea_exchange_assignments"][0]["cross_company_evaluating_director"].startswith("BountyScoutAI/")
    assert m["cross_company_model_peer_reviews_evidenced"]==0
    assert len(m["sponsor_verification_actions"])==1
    print("B_CROSS_IDEA_EXCHANGE_SELFTEST_PASS")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["test","share","review"])
    p.add_argument("--fleet",choices=FLEETS);p.add_argument("--run-id")
    args=p.parse_args()
    if args.mode=="test":selftest()
    elif args.mode=="share":
        if not args.fleet or not args.run_id:raise SystemExit("Requires --fleet and --run-id")
        share(args.fleet,args.run_id)
    else:review()
