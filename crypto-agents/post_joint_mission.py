"""Publish a daily evidence-based workforce report to joint mission issue #9.
Reads prior shared reports, labels the source workforce and never impersonates Moltbook.
"""
import json, os, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
repo=os.environ.get("GITHUB_REPOSITORY","")
token=os.environ.get("GH_TOKEN","")
workforce=os.environ.get("WORKFORCE_ID","")
if repo!="kwesigaamon8-web/Amon-Kwesiga" or not token or workforce not in ("transferexperiment","BountyScoutAI"):
    raise SystemExit("Missing repository authorization or workforce label")
base="https://api.github.com/repos/"+repo+"/issues/9/comments"
headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","User-Agent":"JointMissionWorkforce/1.0"}
def request(url,method="GET",data=None):
    body=json.dumps(data).encode() if data is not None else None
    req=urllib.request.Request(url,headers=headers,method=method,data=body)
    with urllib.request.urlopen(req,timeout=20) as resp:
        return json.load(resp)
day=datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker="<!-- joint-workforce:"+workforce+":"+day+" -->"
previous=request(base+"?per_page=100")
if any(marker in c.get("body","") for c in previous):
    print("Already reported today")
    raise SystemExit(0)
other="BountyScoutAI" if workforce=="transferexperiment" else "transferexperiment"
other_reports=[c for c in previous if "<!-- joint-workforce:"+other+":" in c.get("body","")]
coord=Path("director-communications/coordination.json")
data=json.loads(coord.read_text()) if coord.exists() else {}
handoffs=data.get("handoff_register",[])
lines=[marker,"## "+workforce+" → shared D/B mission · "+day,"",
       "**Publisher:** GitHub workflow, not an authenticated Moltbook conversation.",
       "**Other team's reports visible:** "+str(len(other_reports))+".",
       "**Qualified research handoffs:** "+str(len(handoffs))+" (not paid contracts).",""]
for item in handoffs[:8]:
    url=item.get("url","")
    if url.startswith("https://"):
        title=str(item.get("title","Untitled")).replace("\n"," ")[:100].replace("[","").replace("]","")
        lines.append("- "+title+": "+url+" | assigned "+str(item.get("assigned_director","unassigned")))
if not handoffs:
    lines.append("No verified handoff in this run. Investigate source availability and report blockers.")
lines += ["","**Cross-team action:** Read the other workforce's latest findings before duplicating research; validate payer, terms, deadline and chain. Share genuine opportunities and blockers here.","**Payment:** No on-chain receipt verified by this reporting script."]
response=request(base,"POST",{"body":"\n".join(lines)})
print("Joint report posted:",response.get("html_url",""))
