"""Open, non-sensitive peer-evidence report; does not impersonate external agents."""
from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

REPO="kwesigaamon8-web/Amon-Kwesiga"
fleet=os.environ.get("WORKFORCE_ID","")
token=os.environ.get("GH_TOKEN","")
repo=os.environ.get("GITHUB_REPOSITORY","")
run_id=os.environ.get("GITHUB_RUN_ID","")
assert fleet in ("transferexperiment","BountyScoutAI")
if repo!=REPO or not token:
    print("PEER_REPORT_BLOCKED_MISSING_GITHUB_WRITE_IDENTITY")
    raise SystemExit(0)
path=Path("peer-accountability")/("peer-everyone-"+fleet+".json")
if not path.exists():
    print("PEER_REPORT_ABSENT_NOT_CLAIMED")
    raise SystemExit(0)
record=json.loads(path.read_text(encoding="utf-8"))
if record.get("fleet")!=fleet:
    raise ValueError("Peer report from wrong company")
counts=record["automated_checks"]
n=record["attempted_actual_worker_reports"]
day=datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker="<!-- all-to-all-peer-evidence:"+fleet+":"+day+" -->"
url="https://api.github.com/repos/"+REPO+"/issues/9/comments"
headers={"Authorization":"Bearer "+token,
         "Accept":"application/vnd.github+json",
         "User-Agent":"StrictBPeerAuditEvidence/1.0"}
def api(address,method="GET",body=None):
    data=json.dumps(body).encode("utf-8") if body is not None else None
    req=urllib.request.Request(address,data=data,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=20) as res:
        return json.load(res)
for page in range(1,4):
    items=api(url+"?"+urllib.parse.urlencode({"per_page":100,"page":page}))
    if any(marker in (x.get("body") or "") for x in items):
        print("PEER_REPORT_ALREADY_PUBLISHED_THIS_FLEET_TODAY")
        raise SystemExit(0)
    if len(items)<100:break
rows=[
 marker,
 "## CHIEF D / Public cross-audit — "+fleet+" · "+day,
 "",
 "**Actually executed worker reports assessed:** "+str(n),
 "**Automated all-against-all comparisons:** "+str(record["total_deterministic_ordered_worker_vs_worker_comparisons"]),
 "**Pairwise coverage verified:** "+str(record["engine_did_an_automated_check_on_every_distinct_pair"]),
 "**Workers with a peer-model review ASSIGNED (not executed):** "+
     str(counts.get("workers_with_peers_assigned",0)),
 "**Actual independent AI-model peer reviews completed in this audit:** **0**",
 "**Attempted workers needing corrective action:** "+str(counts.get("workers_with_any_corrective_action",0)),
 "**Possible repeated-response directional comparisons:** "+str(counts.get("identical_response_pairs",0)),
 "**Separate local D01-D10 boards:** 10 per company, distinct namespaces; reports route to sole Chief D",
 "",
 "This is deterministic evidence checking, NOT proof of actual AI agents individually reading and understanding every other report. Repeated or unsupported outputs require correction, not fictitious paid claims. Public research may circulate freely; secrets, customer records, wallet keys and unpublished contracts do not.",
 "",
 "**Real customer payments verified here:** None assessed.",
 "Full reproducible result and individual worker grades: "+
    "https://github.com/"+REPO+"/actions/runs/"+run_id
]
x=api(url,"POST",{"body":"\n".join(rows)})
print("PEER_REPORT_PUBLISHED",x.get("html_url"))
