"""Publish one per-fleet reporting-chain report per UTC day to Chief D's shared issue."""
import json, os, urllib.parse, urllib.request
from datetime import datetime,timezone
from pathlib import Path

fleet=os.environ.get("WORKFORCE_ID","")
repo=os.environ.get("GITHUB_REPOSITORY","")
run=os.environ.get("GITHUB_RUN_ID","")
token=os.environ.get("GH_TOKEN","")
if fleet not in ("transferexperiment","BountyScoutAI") or repo!="kwesigaamon8-web/Amon-Kwesiga" or not run or not token:
    raise SystemExit("Publishing requires authorized company GitHub Action identity")
report=Path("hierarchical-reports")/fleet/"CHIEF_D_COMPANY_REPORT.json"
if not report.exists():
    raise SystemExit("No aggregation report exists; cannot claim supervisor handoff")
r=json.loads(report.read_text(encoding="utf-8"))
if r.get("company")!=fleet: raise SystemExit("Wrong-company report blocked")
day=datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker="<!-- b-to-chief-d:"+fleet+":"+day+" -->"
endpoint="https://api.github.com/repos/"+repo+"/issues/9/comments"
headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","User-Agent":"B-Manager-Director-ChiefD-Handoff"}
def call(url,method="GET",payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(url,headers=headers,method=method,data=data)
    with urllib.request.urlopen(req,timeout=20) as response: return json.load(response)
for p in range(1,6):
    comments=call(endpoint+"?"+urllib.parse.urlencode({"page":p,"per_page":100}))
    if any(marker in str(c.get("body") or "") for c in comments):
        print("Chief D already received this fleet's hierarchy report today")
        raise SystemExit(0)
    if len(comments)<100:break
url="https://github.com/"+repo+"/actions/runs/"+run
lines=[marker,"## "+fleet+" — B workers → managers → directors → Chief D","",
       "**This is automated forwarding of actual recorded B worker reports, not live manager conversations.**","",
       "- Actual attempted B reports: "+str(r["attempted_worker_reports"]),
       "- Completed model responses: "+str(r["completed_worker_model_reports"]),
       "- Strict-qualified source research: "+str(r["strict_qualified_research_reports"]),
       "- Parent/manager/director inboxes populated: "+str(r["supervisor_inboxes"]),
       "- Forwarding steps: "+str(r["recorded_handoffs"]),
       "- Independently evidenced supervisor AI reviews: "+str(r["actual_parent_AI_reviews_verified"]),
       "- Confirmed cryptocurrency income by this report: NOT ASSESSED (requires transaction proof)","",
       "**Company director submissions:**"]
for d in r["directors"]:
    lines.append("- "+d["director"]+": "+str(d["attempted_workers"])+" attempted B reports; "+str(d["completed_model_reports"])+" model completions; "+str(d["corrections"])+" corrections")
lines += ["", "Every actual worker has an individual JSON and Markdown report. All managers, intermediate W/S/G supervisors and directors have inbox files, with traceable edges in HANDOFFS.json.",
          "**Evidence artifact:** hierarchical-worker-reports-"+fleet+" — [open workflow run]("+url+")",
          "Chief D: do not report payment until buyer acceptance, correct-network TXID and independent chain evidence exist."]
result=call(endpoint,"POST",{"body":"\n".join(lines)})
print("CHIEF_D_HIERARCHY_REPORT_PUBLISHED",result.get("html_url"))
