"""Automatic Director D digest using evidence from independent GitHub jobs.

Never confuse a model completion with a job contract or received coins.
Never disclose owner wallet directories. Does not run downloaded artifacts.
"""
import hashlib
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

REPO="kwesigaamon8-web/Amon-Kwesiga"
WORKER="Real Free-Hosted AI Worker Processes"
RESEARCH="Independent Crypto Opportunity Agents"
NAMES=[WORKER,RESEARCH]
TOKEN=os.getenv("GH_TOKEN")
HEADERS={"Accept":"application/vnd.github+json",
 "User-Agent":"B-Independent-Director-D-Reports",
 "X-GitHub-Api-Version":"2022-11-28"}
if TOKEN:HEADERS["Authorization"]="Bearer "+TOKEN

def api(path,payload=None,raw=False):
    if not path.startswith("/repos/"+REPO+"/"):raise ValueError("Invalid API path")
    data=json.dumps(payload).encode() if payload is not None else None
    headers=dict(HEADERS)
    if data:headers["Content-Type"]="application/json"
    req=urllib.request.Request("https://api.github.com"+path,data=data,headers=headers)
    with urllib.request.urlopen(req,timeout=25) as response:
        blob=response.read(16000000)
    if raw:return blob
    return json.loads(blob)

def audited(r,name):
    if not r or r.get("status")!="completed":return {}
    try:
        entries=api("/repos/"+REPO+"/actions/runs/"+str(r["id"])+"/artifacts?per_page=100").get("artifacts",[])
        desired="real-ai-workers-overall-audit" if name==WORKER else "consolidated-opportunity-report"
        a=next((a for a in entries if a.get("name")==desired and not a.get("expired")),None)
        if not a:return {}
        blob=api("/repos/"+REPO+"/actions/artifacts/"+str(a["id"])+"/zip",raw=True)
        wanted=["ai-process-summary.json","director-D-results/DIRECTOR_D_RESULTS.json"] if name==WORKER else ["summary.json","delivery-audit/REPORT.json"]
        result={}
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for path in wanted:
                match=next((p for p in z.infolist() if (p.filename==path or p.filename.endswith("/"+path)) and p.file_size<1200000),None)
                if match:
                    with z.open(match) as file:result[path]=json.loads(file.read(1200000))
        return result
    except Exception as exc:
        print("AUDIT_ARTIFACT_NOT_READABLE",name,type(exc).__name__)
        return {}

def clean(s):
    return re.sub(r"[\r\n\[\]()\x00-\x1f]"," ",str(s or ""))[:120]

def digest(latest,completed,audits):
    lines=["## Director D — Actual B Results","","**Current execution**"]
    for name in NAMES:
        x=latest.get(name)
        if not x:lines.append("- "+name+": no run found");continue
        status=clean(x.get("conclusion") or x.get("status"))
        lines.append("- ["+name+"](https://github.com/"+REPO+"/actions/runs/"+str(x["id"])+"): "+status)
    w=audits.get(WORKER,{})
    a=w.get("ai-process-summary.json") or {}
    d=w.get("director-D-results/DIRECTOR_D_RESULTS.json") or {}
    lines+=["","**Last successful completed worker audit**"]
    if a:
        lines.append("- Actual model subprocess invocations: "+str(int(a.get("actual_os_processes_invoked") or 0)))
        lines.append("- Actual completed model inferences: "+str(int(a.get("actual_independent_model_completions") or 0)))
        lines.append("- Individual written reports: "+str(int(a.get("per_agent_markdown_reports_written") or 0)))
        lines.append("- Directors with manifests: "+str(int(a.get("director_manifests_present") or 0))+"/10")
    else:lines.append("- No completed worker audit artifact available; counts not inferred.")
    if d:
        lines.append("- Source-linked worker reports: "+str(int(d.get("workers_with_public_source_links") or 0)))
        lines.append("- Next-step checkpoints: "+str(int(d.get("workers_with_specific_next_action") or 0)))
    p=audits.get(RESEARCH,{})
    sr=p.get("summary.json") or {}
    dr=p.get("delivery-audit/REPORT.json") or {}
    lines+=["","**Last successful completed opportunity research audit**"]
    if sr:
        leads=sr.get("qualified_unverified_leads") or []
        lines.append("- Reporting researcher roles: "+str(int(sr.get("report_count") or 0))+"/30")
        lines.append("- Screened potential leads (payer/payment not verified): "+str(len(leads)))
        for lead in leads[:3]:
            if not isinstance(lead,dict):continue
            url=lead.get("url","")
            if isinstance(url,str) and re.fullmatch(r"https://[a-zA-Z0-9./_?&=%#:+-]{4,500}",url):
                lines.append("- "+clean(lead.get("title"))+": "+url+" (unverified prospect)")
    else:lines.append("- No completed readable opportunity summary; no earning claim.")
    if dr:lines.append("- Individual agent deliverables audited: "+str(int(dr.get("individual_deliverables_verified_present") or 0)))
    lines+=["","**Owner cryptocurrency receipts confirmed by this workflow: NONE ASSESSED.**",
    "No payment is claimed here. An AI reply, search result or GitHub job cannot establish a credit in the owner's wallet.",
    "Next: verify real payer and terms for credible leads, prepare useful paid-service deliverables, seek appropriate owner approval for external commitments.",
    "Source: GitHub Actions metadata and existing machine-generated audit JSON, not external deposit verification."]
    return "\n".join(lines)

def main():
    if os.getenv("GITHUB_REPOSITORY")!=REPO or not TOKEN:raise SystemExit("Owner GitHub token required")
    rows=api("/repos/"+REPO+"/actions/runs?per_page=100").get("workflow_runs",[])
    latest={n:next((x for x in rows if x.get("name")==n),None) for n in NAMES}
    complete={n:next((x for x in rows if x.get("name")==n and x.get("status")=="completed" and x.get("conclusion")=="success"),None) for n in NAMES}
    state=[(n,(latest[n] or {}).get("id"),(latest[n] or {}).get("status"),
            (latest[n] or {}).get("conclusion"),(complete[n] or {}).get("id"))
           for n in NAMES]
    key=hashlib.sha256(json.dumps(state).encode()).hexdigest()[:18]
    marker="<!-- b-owner-digest-v1:"+key+" -->"
    comments=api("/repos/"+REPO+"/issues/6/comments?per_page=100&sort=created&direction=desc")
    if any(marker in x.get("body","") for x in comments):
        print("DIRECTOR_D_UNCHANGED",key);return
    audits={n:audited(complete[n],n) for n in NAMES}
    body=digest(latest,complete,audits)+"\n"+marker
    r=api("/repos/"+REPO+"/issues/6/comments",payload={"body":body})
    print("DIRECTOR_D_POSTED",r.get("html_url"))

def test():
    a={WORKER:{"id":1,"status":"completed","conclusion":"success"},
       RESEARCH:{"id":2,"status":"completed","conclusion":"failure"}}
    result=digest(a,a,{WORKER:{"ai-process-summary.json":{
       "actual_os_processes_invoked":500,"actual_independent_model_completions":500,
       "per_agent_markdown_reports_written":500,"director_manifests_present":10}},
       RESEARCH:{"summary.json":{"report_count":12,"qualified_unverified_leads":[]}}})
    assert "500" in result and "NONE ASSESSED" in result
    assert "payer/payment not verified" in result and "No payment is claimed" in result
    print("B_OWNER_DIGEST_SELFTEST_PASS")

if __name__=="__main__":
    test() if "--self-test" in sys.argv else main()
