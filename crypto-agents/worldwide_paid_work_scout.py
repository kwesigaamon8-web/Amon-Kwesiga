"""Bounded, worldwide B1/B2 legitimate paid-work scout.

Uses source URLs only (no logins, no application, no wallet authorization).
It is source discovery + review assignment, NEVER verified hire or money.
GitHub Actions runs it at most hourly as part of the existing shared scout.
"""
from __future__ import annotations
import argparse
import datetime as dt
import html.parser
import ipaddress
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
CONFIG=ROOT/"worldwide_paid_work_seeds.json"
OUTPUT=pathlib.Path("paid-opportunity-reports")
AGENT="ChiefD-WorldBuyerResearch/1.0"
STOP=("job is no longer available", "this job is closed", "posting has expired",
      "bounty is cancelled", "bounty closed", "applications are closed")

class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!="a":
            return
        for name,value in attrs:
            if name=="href" and value:
                self.links.append(value)

def safe_public_https(url):
    try:
        p=urllib.parse.urlsplit(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password:
            return False
        if p.hostname in ("localhost",) or p.hostname.endswith(".local"):
            return False
        try:
            ip=ipaddress.ip_address(p.hostname)
            if not ip.is_global:return False
        except ValueError:
            pass
        return True
    except ValueError:
        return False

def fetch(url):
    if not safe_public_https(url):
        raise ValueError("Not a public https URL")
    req=urllib.request.Request(url,headers={"User-Agent":AGENT,
                            "Accept":"text/html,application/json,text/plain"})
    with urllib.request.urlopen(req,timeout=8) as response:
        # do not follow/scrape privileged account endpoints
        final=response.geturl()
        if not safe_public_https(final):
            raise ValueError("Redirected away from public https")
        body=response.read(400000).decode("utf-8","replace")
        return {"http":response.status,"final_url":final,"body":body}

def evaluate_source(url,loader=fetch):
    try:
        v=loader(url)
        if not isinstance(v,dict) or v.get("http")!=200:
            return {"status":"unavailable","http":v.get("http") if isinstance(v,dict) else None,
                    "error":"non_200_or_invalid_body"}
        body=str(v.get("body") or "")
        lower=body.lower()
        closed=next((x for x in STOP if x in lower),None)
        return {"status":"possible_closed_check_manual" if closed else "source_readable",
                "http":200,"page_title_or_body_received":bool(body.strip()),
                "potential_closure_phrase":closed,
                "does_NOT_prove_open_task":True,
                "does_NOT_prove_funding_or_payer":True,
                "does_NOT_prove_eligibility":True,
                "body_excerpt_not_stored":True,
                "html_for_dynamic_discovery":body}
    except (OSError,urllib.error.URLError,ValueError,TimeoutError) as e:
        return {"status":"source_unavailable","error":type(e).__name__,
                "does_NOT_prove_open_task":True,"does_NOT_prove_funding_or_payer":True}

def extract_public_links(source_url,body,limit=6):
    parser=Links()
    try: parser.feed(body[:300000])
    except Exception:return []
    base_host=urllib.parse.urlsplit(source_url).hostname or ""
    seen=set()
    found=[]
    for href in parser.links:
        u=urllib.parse.urljoin(source_url,href)
        p=urllib.parse.urlsplit(u)
        if not safe_public_https(u):continue
        # Prefer actual task/job detail links from the same published board.
        if p.hostname!=base_host:continue
        path=p.path.lower()
        if path in ("/jobs","/bounties","/tasks","/"):continue
        if not (path.startswith("/jobs/") or path.startswith("/bounties/") or path.startswith("/tasks/")):
            continue
        canonical=urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,"",""))
        if canonical in seen:continue
        seen.add(canonical)
        found.append(canonical)
        if len(found)>=limit:break
    return found

def hour_rotation(items,hour,count):
    if not items:return []
    start=hour%len(items)
    return [items[(start+i)%len(items)] for i in range(min(count,len(items)))]

def run(now=None,loader=fetch,config=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    conf=config or json.loads(CONFIG.read_text(encoding="utf-8"))
    assert conf["schema"]=="B1_B2_WORLDWIDE_PUBLIC_PAID_WORK_SEEDS_V1"
    hour=int(now.timestamp()//3600)
    seeds=conf["seeded_leads"]
    assert len({s["source_url"] for s in seeds})==len(seeds)
    lanes={fleet:[x for x in seeds if x["fleet"]==fleet]
           for fleet in ("B1","B2")}
    # Config uses B1/B2, never pretend these assignments activate agents.
    chosen=hour_rotation(lanes["B1"],hour,2)+hour_rotation(lanes["B2"],hour+2,2)
    results=[]
    for item in chosen:
        row={k:item[k] for k in ("key","title","platform","source_url",
                               "listed_utc_date","budget_usd","category","fleet",
                               "competition","observed_hires","precondition")}
        days=(now.date()-dt.date.fromisoformat(item["listed_utc_date"])).days
        row["listing_age_days"]=days
        row["older_than_two_weeks"]=days>14
        check=evaluate_source(item["source_url"],loader)
        check.pop("html_for_dynamic_discovery",None)
        row["source_check"]=check
        row["buyer_agreed_scope"]=False
        row["buyer_has_authorized_hire"]=False
        row["work_accepted_by_buyer"]=False
        row["application_actually_sent"]=False
        row["wallet_receipt_verified"]=False
        row["payment_earned_verified"]=False
        row["already_hired_warning"]=bool(item["observed_hires"])
        row["status"]="SOURCE_REFERENCE_ONLY_REVIEW_AGAIN" if days>14 or check["status"]!="source_readable" else "SOURCE_READABLE_ELIGIBILITY_AND_HIRING_UNVERIFIED"
        row["next_B1"]=("Verify real payer, still-hiring availability, region eligibility, no upfront money and exact permitted application route; do not invent contact.")
        row["next_B2"]=("Build/QA an original relevant synthetic demo; use actual buyer data only with permission.")
        results.append(row)
    discoveries=[]
    pages=hour_rotation(conf["discovery_pages"],hour,2)
    for p in pages:
        check=evaluate_source(p["url"],loader)
        body=check.pop("html_for_dynamic_discovery","")
        found=extract_public_links(p["url"],body)
        discoveries.append({"source":p["channel"],"discovery_url":p["url"],
                "status":check["status"],"latest_public_links_unverified":found,
                "all_links_require_original_task_review":True,
                "wallet_spend_or_account_signing_not_authorized":True,
                "errors":check.get("error")})
    return {
        "schema":"CHIEF_D_WORLDWIDE_PAID_WORK_SCOUT_V1",
        "checked_at_utc":now.isoformat(),
        "worldwide_discovery_mission":"B1 buyer/source verification; B2 original demo and QA; local D10 receipt validation; one Chief D human report",
        "scheduled_continuity":"Existing shared hourly GitHub Actions scout; does not imply background agents continuously running outside a real workflow run.",
        "rotated_source_checks":len(results),
        "source_readable_count":sum(x["source_check"]["status"]=="source_readable" for x in results),
        "fresh_buyer_leads_VERIFIED":0,
        "applications_sent":0,"contracts_signed":0,"paid_work_accepted":0,
        "incoming_payments_verified":0,
        "read_only_receiving_no_wallet_spending":True,
        "external_application_account_connected":False,
        "source_candidate_review":results,
        "rotated_board_discovery":discoveries,
        "next_required_human_authorization":"An actual marketplace account connection or owner's own application submission; must verify buyers and payment terms."
    }

def self_test():
    fixed=dt.datetime(2026,11,17,6,12,tzinfo=dt.timezone.utc)
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    def fake(url):
        if "musedin" in url:
            return {"http":200,"final_url":url,"body":'<a href="/jobs/123">Job</a><a href="/jobs/123">Same</a><a href="/jobs/456">Other</a>'}
        return {"http":200,"final_url":url,"body":"An original public job listing describing the role."}
    report=run(fixed,fake,config)
    assert report["rotated_source_checks"]==4
    assert len({x["source_url"] for x in report["source_candidate_review"]})==4
    assert {x["fleet"] for x in report["source_candidate_review"]}=={"B1","B2"}
    assert report["source_readable_count"]==4
    assert report["incoming_payments_verified"]==report["applications_sent"]==0
    assert report["read_only_receiving_no_wallet_spending"] is True
    for x in report["source_candidate_review"]:
        assert x["wallet_receipt_verified"] is False
        assert x["buyer_has_authorized_hire"] is False
        assert "UNVERIFIED" in x["status"]
    closed=evaluate_source("https://example.org/job",lambda url:{"http":200,"body":"This job is closed"})
    assert closed["status"]=="possible_closed_check_manual"
    unavailable=evaluate_source("https://example.org/job",lambda url:(_ for _ in ()).throw(TimeoutError()))
    assert unavailable["status"]=="source_unavailable"
    assert extract_public_links("https://musedin.com/jobs",fake("https://musedin.com/jobs")["body"])==[
        "https://musedin.com/jobs/123","https://musedin.com/jobs/456"]
    assert not safe_public_https("http://127.0.0.1/a")
    print("WORLDWIDE_PAID_WORK_SCOUT_SELF_TEST_PASS",json.dumps({
        "distinct_fleets":2,"rotated_checks":4,"true_payer_or_payment_claims":0,
        "source_failure_reported":True,"duplicate_board_links_ignored":True}))

def save(report):
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/"worldwide.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    lines=["# B1/B2 world-paying-work scout — evidence not earnings",report["checked_at_utc"],"",
           "Rotated primary-source checks: "+str(report["rotated_source_checks"]),
           "Readable pages (not verified hiring): "+str(report["source_readable_count"]),
           "Jobs applied / accepted / payments received: **0 verified in this scan**.","",
           "| Assignment | Role | Advertised USD | Source status | Original source |",
           "|---|---|---:|---|---|"]
    for row in report["source_candidate_review"]:
        lines.append("| "+row["title"].replace("|","/")[:55]+" | "+row["fleet"]+
                     " | $"+str(row["budget_usd"])+" | "+
                     row["source_check"]["status"]+" | [Review buyer]("+row["source_url"]+") |")
    lines+=["","## Rotated public discovery boards"]
    for p in report["rotated_board_discovery"]:
        lines.append("- ["+p["source"]+"]("+p["discovery_url"]+"): "+p["status"]+
           "; "+str(len(p["latest_public_links_unverified"]))+" unverified detail links seen.")
    lines+=["","## Real next action",
        "B1: verify still-paying real customer, Uganda eligibility, payout and actual authorized submission route.",
        "B2: supply one useful original sample and QA; DO NOT use client records until permitted.",
        "D10: check only genuine agreed incoming payment evidence on a matching approved wallet network.",
        "No wallet transfers, signatures, staking, bonds, seed phrases or unauthorized mass posting.",
        "All links and prices need re-checking: this report is not a claim of an open hire or contract."]
    (OUTPUT/"worldwide.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--self-test",action="store_true")
    arg=a.parse_args()
    if arg.self_test:self_test()
    else:
        r=run()
        save(r)
        print("CHIEF_D_WORLDWIDE_SCOUT",json.dumps({
            "checked_at_utc":r["checked_at_utc"],
            "sources_checked":r["rotated_source_checks"],
            "source_readable":r["source_readable_count"],
            "directory_pages_checked":len(r["rotated_board_discovery"]),
            "application_sent":0,"buyer_contracts":0,"payments":0}))
