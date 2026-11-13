"""Execute a rotated portion of 7,500 provisioned research roles.

Hierarchy: 10 directors (with two independently reporting assistants each)
 -> 15 manager role records per director -> 50 distinct research worker roles
 per manager. Managers are supervised by the director's existing GitHub job.
 
Each hourly cycle dispatches only 2/50 worker roles per manager (300 total
across 10 companies) to respect public-provider rates and free runner limits.
This module creates genuine report files for attempted queries; it cannot
recruit actual human workers, create online identities or send messages.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path
from wallet_routes import private_directory_status
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path("crypto-agents")
CONFIG = json.loads((ROOT/"company_hierarchy.json").read_text(encoding="utf-8"))
BRIEF = json.loads((ROOT/"branch_brief.json").read_text(encoding="utf-8"))
PAYMENT_DIRECTORY_STATUS = private_directory_status()
ROLE = os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "")
COMPANY = next((c for c in CONFIG["companies"] if c["director_id"]==ROLE),None)
if COMPANY is None:
    print("COMPANY_DISPATCH_SKIPPED", ROLE, "independent assistant is not a manager")
    raise SystemExit(0)
assert len(COMPANY["managers"])==15 and len(CONFIG["worker_roles"])==50
if BRIEF.get("professional_profile") or BRIEF.get("owner_name"):
    raise SystemExit("Sensitive owner information must not enter subordinate instructions")
OUT = Path("company-reports")
OUT.mkdir(exist_ok=True)
PAID = re.compile(r"(?i)\b(hiring|need|looking for|paid|freelance|contract|bounty|reward|job|gig)\b")
RISK = re.compile(r"(?i)\b(airdrop|giveaway|connect your wallet|private key|seed phrase|pay first|presale)\b")
LIMIT = datetime.now(timezone.utc)-timedelta(days=45)
RUN_SLOT = int(time.time()//3600)%25
headers={"User-Agent":"CompanyResearch/1.0","Accept":"application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]

def read_date(value):
    try:
        dt=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except (ValueError,TypeError):
        return None

def fetch(address, auth=False):
    request=urllib.request.Request(address,headers=(headers if auth else
        {"User-Agent":"CompanyResearch/1.0","Accept":"application/json"}))
    with urllib.request.urlopen(request,timeout=13) as resp:
        return json.loads(resp.read(500000))

def dispatch(job):
    manager, assignment = job
    n=int(assignment["ordinal"])
    worker=manager["id"]+"-W"+str(n).zfill(2)
    item={
        "worker_id":worker,"manager_id":manager["id"],
        "company_id":COMPANY["id"],"director_id":ROLE,
        "assigned_role":assignment["role_name"],"search_source":assignment["source"],
        "search_query":assignment["query"],
        "payment_instruction_source":"crypto-agents/branch_brief.json",
        "wallet_directory_access":PAYMENT_DIRECTORY_STATUS["status"],
        "payment_route_ids_available":PAYMENT_DIRECTORY_STATUS["route_ids"],
        "personal_details_received":False,
        "checked_at_utc":datetime.now(timezone.utc).isoformat(),
        "execution_status":"source_unavailable","unverified_leads":[],
        "verified_earnings":[],"source_error":None,
        "notes":"Read-only public research only; no paid job, agreement or payment is established by a search result."
    }
    try:
        if assignment["source"]=="github":
            query=assignment["query"]+" is:issue is:open"
            url="https://api.github.com/search/issues?"+urllib.parse.urlencode(
                {"q":query,"per_page":8,"sort":"updated"})
            data=fetch(url,True)
            if "message" in data and not data.get("items"):
                raise ValueError("GitHub API: "+str(data["message"])[:100])
            source=[{
                "title":o.get("title",""),"url":o.get("html_url",""),
                "description":(o.get("body") or "")[:300],"observed_at":o.get("updated_at","")
            } for o in data.get("items",[]) if o.get("state")=="open" and not o.get("pull_request")]
        else:
            url="https://hn.algolia.com/api/v1/search_by_date?"+urllib.parse.urlencode(
                {"query":assignment["query"],"tags":"story","hitsPerPage":9})
            data=fetch(url)
            source=[{
                "title":o.get("title",""),
                "url":o.get("url") or ("https://news.ycombinator.com/item?id="+str(o.get("objectID",""))),
                "description":(o.get("story_text") or "")[:300],"observed_at":o.get("created_at","")
            } for o in data.get("hits",[])]
        candidates=[]
        for lead in source:
            link=str(lead["url"])
            dt=read_date(lead["observed_at"])
            body=str(lead["title"])+" "+str(lead["description"])
            if not link.startswith("https://") or not dt or dt<LIMIT or not PAID.search(body) or RISK.search(body):
                continue
            candidates.append({
                "title":str(lead["title"])[:150],"url":link,
                "source":assignment["source"],"observed_at":lead["observed_at"],
                "evidence_excerpt":str(lead["description"])[:220],
                "status":"unverified_search_candidate",
                "payer_verified":False,"owner_country_eligibility_verified":False,"amount_verified":False,
                "payout_verified":False,
                "next_action":"Confirm original source, true paid deliverable, payer, amount, country eligibility and network; no fees."
            })
        item["execution_status"]="source_checked"
        item["unverified_leads"]=candidates[:2]
    except Exception as exc:
        item["source_error"]=str(exc)[:170]
    (OUT/(worker+".json")).write_text(json.dumps(item,indent=2),encoding="utf-8")
    return item

jobs=[]
for manager in COMPANY["managers"]:
    for index in (RUN_SLOT*2,RUN_SLOT*2+1):
        jobs.append((manager,CONFIG["worker_roles"][index]))
assert len(jobs)==30
with ThreadPoolExecutor(max_workers=5) as pool:
    records=list(pool.map(dispatch,jobs))
for manager in COMPANY["managers"]:
    childs=[r for r in records if r["manager_id"]==manager["id"]]
    assert len(childs)==2
    msg={
        "manager_id":manager["id"],"company_id":COMPANY["id"],
        "reports_to_director":ROLE,"workforce_authorized":50,
        "workers_executed_this_cycle":len(childs),
        "worker_ids_this_cycle":[w["worker_id"] for w in childs],
        "assigned_roles_this_cycle":[w["assigned_role"] for w in childs],
        "source_checked":sum(w["execution_status"]=="source_checked" for w in childs),
        "source_unavailable":sum(w["execution_status"]=="source_unavailable" for w in childs),
        "unverified_leads_count":sum(len(w["unverified_leads"]) for w in childs),
        "source_linked_candidate_examples":[dict(candidate,worker_id=w["worker_id"])
            for w in childs for candidate in w["unverified_leads"]][:3],
        "manager_review":"Review the two independent role reports, challenge weak paid-work claims and hand credible URL evidence to the director; no funds or outreach are claimed.",
        "legitimate_income_received_verified":False
    }
    (OUT/(manager["id"]+".json")).write_text(json.dumps(msg,indent=2),encoding="utf-8")
managers=[json.loads((OUT/(m["id"]+".json")).read_text(encoding="utf-8")) for m in COMPANY["managers"]]
summary={
    "company_id":COMPANY["id"],"director_id":ROLE,
    "assistant_roles":COMPANY["assistant_ids"],"configured_managers":15,
    "configured_workers":750,"run_slot":RUN_SLOT,"slots_per_full_rotation":25,
    "workers_attempted_this_cycle":len(records),
    "worker_reports_created":sum((OUT/(r["worker_id"]+".json")).exists() for r in records),
    "source_checked":sum(r["execution_status"]=="source_checked" for r in records),
    "source_unavailable":sum(r["execution_status"]=="source_unavailable" for r in records),
    "unverified_leads_count":sum(len(r["unverified_leads"]) for r in records),
    "manager_report_ids":[m["manager_id"] for m in managers],
    "manager_findings":[dict(candidate,manager_id=m["manager_id"])
        for m in managers for candidate in m["source_linked_candidate_examples"]][:10],
    "owner_personal_details_shared":False,
    "private_directory_access_status":PAYMENT_DIRECTORY_STATUS["status"],
    "wallet_route_count_available":len(PAYMENT_DIRECTORY_STATUS["route_ids"]),
    "payments_received_verified":[],
    "caveat":"Configured 750 workers per company; only 30 bounded worker searches dispatched this hourly cycle. No separate AI account or confirmed payee is created."
}
(OUT/(ROLE+"-COMPANY-SUMMARY.json")).write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("COMPANY",ROLE,"managers",15,"configured_workers",750,
      "attempted",len(records),"source_checked",summary["source_checked"],
      "failed",summary["source_unavailable"],"unverified_leads",summary["unverified_leads_count"])
