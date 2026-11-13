"""Publish one verified-by-file ten-director coordination digest per UTC day.

Only posts inside the owner's own GitHub issue #6. One shared GitHub identity.
Uses local output files; claims no direct conversations or payments.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

repo = os.environ.get("GITHUB_REPOSITORY")
token = os.environ.get("GH_TOKEN")
run_id = os.environ.get("GITHUB_RUN_ID","")
if repo != "kwesigaamon8-web/Amon-Kwesiga" or not token:
    raise SystemExit("No owner repo-scoped GitHub posting authorization")
folder = Path("director-communications")
data = json.loads((folder/"coordination.json").read_text(encoding="utf-8"))
if data.get("directors") != 10:
    raise SystemExit("Ten distinct director messages required")
directors = []
for i in range(1,11):
    identifier="D%02d" % i
    directors.append(json.loads((folder/(identifier+".json")).read_text(encoding="utf-8")))
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker = "<!-- ten-director-communication-v1:"+date+" -->"
url="https://api.github.com/repos/"+repo+"/issues/6/comments"
headers={
 "Authorization":"Bearer "+token,
 "Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28",
 "User-Agent":"OwnerResearchCoordination/1.0"}
def call(address,method="GET",payload=None):
    req=urllib.request.Request(address,method=method,headers=headers,
       data=(json.dumps(payload).encode("utf-8") if payload is not None else None))
    with urllib.request.urlopen(req,timeout=20) as resp:
        return json.loads(resp.read(500000))
for page in range(1,5):
    chunk = call(url+"?"+urllib.parse.urlencode({"per_page":100,"page":page}))
    if any(marker in c.get("body","") for c in chunk):
        print("Ten director update already posted on this UTC day; no duplicate")
        sys.exit(0)
    if len(chunk)<100:
        break

def line_safe(s):
    return str(s or "").replace("|","/").replace("\n"," ")[:80]
lines=[
  marker,
  "## Ten directors' shared performance and handoff review · "+date,
  "",
  "**Operating mode:** 10 independently accountable director roles, each reviewing 2 assistants and three 15-worker branches. One GitHub automation is publishing this report; these are not ten independently logged-in social-media accounts.",
  "",
  "| Director | Main team reports | Branch researchers reporting | Source errors | Qualified leads assigned |",
  "|---|---:|---:|---:|---:|"
]
for d in directors:
    lines.append("| "+d["director"]+" | "+str(d["own_roles_reporting"])+"/3 | "+
        str(d["delegated_worker_reports_received"])+"/45 | "+
        str(d["team_source_errors"])+" | "+str(len(d["assigned_qualified_leads"]))+" |")
lines.extend(["","### Cross-team source-linked handoffs"])
for x in data.get("handoff_register",[])[:12]:
    title=line_safe(x.get("title"))
    link=x["url"]
    lines.append("- "+x["assigned_director"]+" owns ["+title+"]("+link+") (found by "+str(x.get("origin_role"))+"); D09 to check payer, scope and fee risks. **Not yet verified paid work.**")
if not data.get("handoff_register"):
    lines.append("No screened handoffs this cycle; directors should research new original sources and identify why weaker leads failed.")
lines += [
    "",
    "**D09:** independently challenge payer legitimacy, network authenticity and no-fee requirements.",
    "**D10:** check source failures, missing reports, duplicated work, honest status labels and independently evidenced receipts.",
    "**All directors:** choose credible next steps without waiting, share concrete URLs and counterevidence, cooperate across specialties, and do not misrepresent unsent applications or unsigned contracts as completed work.",
    "",
    "Full director-level messages, individual evidence and assignment register are saved in the consolidated artifacts: [view this cloud run](https://github.com/"+repo+"/actions/runs/"+run_id+").",
    "No receipt is verified by this coordination pipeline. No wallet access, transfers, signing or application fees are authorized."
]
res = call(url,"POST",{"body":"\n".join(lines)})
print("COORDINATION_DIGEST_POSTED",res.get("html_url",res.get("id")))
