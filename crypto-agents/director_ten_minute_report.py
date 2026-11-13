"""One-off ten-director one-page evidence report at the owner's deadline.

Runs on an authorized owner repository token; no fictitious director speech,
payment, social outreach, model invocation or one-billion-agent claims.
"""
import io,json,os,re,time,urllib.request,urllib.error,zipfile
from datetime import datetime,timezone
from pathlib import Path

REPO="kwesigaamon8-web/Amon-Kwesiga"
TOKEN=os.environ.get("GH_TOKEN","")
RUN_ID=os.environ.get("GITHUB_RUN_ID","")
DUE="2026-11-13T17:07:13+00:00"
ROOT=Path("ten-minute-director-report");ROOT.mkdir(exist_ok=True)
HEADERS={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"OwnerOnePageDirectorReport/1.0"}
if TOKEN:HEADERS["Authorization"]="Bearer "+TOKEN

def fetch(path,download_bytes=False):
    url=path if path.startswith("https://") else f"https://api.github.com/repos/{REPO}/{path}"
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=22) as resp:
        data=resp.read(14000000)
        return data if download_bytes else json.loads(data)

def post_issue(body):
    if not TOKEN or os.environ.get("GITHUB_REPOSITORY")!=REPO:
        return None,"No authorized issue-posting token"
    url=f"https://api.github.com/repos/{REPO}/issues/6/comments"
    req=urllib.request.Request(url,method="POST",headers=HEADERS,
        data=json.dumps({"body":body}).encode("utf-8"))
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            return json.loads(resp.read(250000)).get("html_url"),None
    except Exception as exc:
        return None,"Posting failed: "+str(exc)[:170]

def due_wait():
    due=datetime.fromisoformat(DUE)
    remaining=max(0,int((due-datetime.now(timezone.utc)).total_seconds()))
    if remaining:
        print("SCHEDULED_ONE_PAGE_DUE_AT",DUE,"seconds_until_due",remaining,flush=True)
        time.sleep(min(remaining,615))

def main():
    due_wait()
    now=datetime.now(timezone.utc).isoformat()
    errors=[]
    runs=[]
    try:runs=fetch("actions/runs?per_page=100").get("workflow_runs",[])
    except Exception as exc:errors.append("Unable to fetch GitHub Actions runs: "+str(exc)[:150])
    fleet=[x for x in runs if x.get("name")=="Independent Crypto Opportunity Agents"]
    last_fleet=fleet[0] if fleet else None
    complete=[x for x in fleet if x.get("status")=="completed" and x.get("conclusion")=="success"]
    newest_success=complete[0] if complete else None
    job_status={}
    if last_fleet:
        try:
            jobs=fetch("actions/runs/"+str(last_fleet["id"])+"/jobs?per_page=100").get("jobs",[])
            for j in jobs:
                name=j.get("name","")
                if re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB])?",name):
                    job_status[name]=j.get("conclusion") or j.get("status","unknown")
        except Exception as exc:errors.append("Unable to check latest fleet jobs: "+str(exc)[:100])
    reports={}
    # The only valid 'director gave a response' proof is an existing artifact
    # from a completed successful run with a role-specific report. Download a
    # maximum of 4 reports to avoid unbounded processing and API calls.
    for run in complete[:4]:
        if len(reports)>=30:break
        try:
            archives=fetch("actions/runs/"+str(run["id"])+"/artifacts?per_page=100").get("artifacts",[])
            for artifact in archives:
                name=artifact.get("name","")
                if not name.startswith("crypto-research-") or artifact.get("expired"):continue
                rid=name[len("crypto-research-"):]
                if not re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB])?",rid) or rid in reports:
                    continue
                # Follow the artifact API redirection to the ZIP archive.
                raw=fetch("actions/artifacts/"+str(artifact["id"])+"/zip",True)
                with zipfile.ZipFile(io.BytesIO(raw)) as arc:
                    paths=[p for p in arc.namelist() if p.endswith("/"+rid+".json") or p==rid+".json"]
                    paths=[p for p in paths if ("reports/" in p or "/" not in p)]
                    if not paths:continue
                    obj=json.loads(arc.read(paths[0]))
                    if obj.get("role")==rid and isinstance(obj.get("leads"),list):
                        reports[rid]=obj
        except Exception as exc:
            errors.append("Could not inspect some individual artifacts: "+str(exc)[:100])
            break
    checked_count=sum(1 for r in reports.values() if r.get("ai_analysis",{}).get("status")=="llm_completed")
    leads={}
    for rid,record in reports.items():
        for lead in record.get("leads",[]):
            url=lead.get("url","")
            if isinstance(url,str) and url.startswith("https://") and url not in leads:
                leads[url]=dict(lead,director=rid[:3])
    # No on-chain/exchange proof available from generic job result files;
    # income cannot be certified by the research fleet or proposal count.
    lines=[
      "<!-- owner-director-one-page-2026-11-13-1707 -->",
      "## Ten Directors — One-Page Owner Report",
      "",
      "**Deadline requested:** 13 Nov 2026, 17:07 UTC (20:07 Kampala). **Checked:** "+now[:19]+" UTC.",
      "",
      "**Objective:** legitimate BTC/USDC or owner-approved cryptocurrency credited on the exact approved network. Research leads or agent headcount are not money received.",
      "",
      "| Director | Actual role output available | Latest workflow job | Reporting outcome |",
      "|---|---|---|---|"
    ]
    for i in range(1,11):
        did=f"D{i:02d}"
        report=reports.get(did)
        status=job_status.get(did,"not reported")
        if report:
            n=len(report.get("leads",[]))
            details=f"{n} unverified lead(s); model {report.get('ai_analysis',{}).get('status','unknown')}"
            proof="Recorded in prior completed fleet artifact"
        else:
            details="No actual per-role report retrieved at deadline"
            proof="Not verified"
        lines.append(f"| {did} | {proof} | {status} | {details} |")
    lines+=["",
      f"**Latest research run:** "+(f"[{last_fleet['id']}]({last_fleet['html_url']}) — {last_fleet.get('status')}/{last_fleet.get('conclusion') or 'pending'}" if last_fleet else "no workflow found"),
      f"**Completed successful research run evidence:** {len(complete)} run(s) in retrieved history; individual director artifact outputs found **{len(reports)}/30**; confirmed language-model director/assistant reviews **{checked_count}**.",
      f"**Unique source-linked leads in retrievable role reports:** {len(leads)}; all remain **unverified paid opportunities**, not earned coins.",
      "",
      "**Highest-priority next action:** Confirm a genuine client/bounty payer offering crypto settlement, current eligibility, agreed deliverable, payment terms and network; then deliver the work and check credited receipt. No role should claim it applied, posted, negotiated or received coins without supported action evidence.",
      "",
      "**Crypto receipts independently verified in this report: NOT ESTABLISHED.** This research-run audit is not a chain/exchange ledger check.",
      "**No immediate mass outreach or wallet signing was authorized.**"
    ]
    if leads:
        lines+=["","**Source leads requiring due diligence:**"]
        for u,lead in list(leads.items())[:3]:
            title=str(lead.get("title") or "Original source").replace("]","").replace("[","")[:75]
            lines.append(f"- [{title}]({u}) — unverified; payer and crypto network must be established")
    if errors:
        lines+=["","**Evidence access problems:** "+str(len(errors))+"; no unavailable detail is assumed completed."]
    lines+=["","*The 375,188,632,680 registered role IDs are software definitions, not active individuals. Missing reports are explicitly missing.*"]
    body="\n".join(lines)
    (ROOT/"ONE_PAGE.md").write_text(body+"\n",encoding="utf-8")
    results={"generated_at_utc":now,"deadline_utc":DUE,"latest_fleet_run_id":last_fleet.get("id") if last_fleet else None,
      "successful_fleet_runs_in_recent_history":len(complete),
      "independent_primary_role_reports_verified":len(reports),
      "distinct_source_leads_unverified":len(leads),
      "on_chain_or_exchange_cryptocurrency_receipt_verified":None,
      "errors":errors}
    link,post_error=post_issue(body)
    results["published_comment"]=link
    results["posting_error"]=post_error
    (ROOT/"STATUS.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print("TEN_MINUTE_DIRECTOR_REPORT",json.dumps(results),flush=True)

if __name__=="__main__":main()
