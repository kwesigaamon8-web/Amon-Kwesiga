"""Chief D consolidated read-only board report for two separate companies.

Owner instructions reach this script ONLY when ChatGPT has put them in the
version-controlled chief_D_owner_orders.json after an actual owner request.
This script cannot read ChatGPT directly, pay invoices, message Moltbook users
or convert worker-role definitions into running agent processes.
"""
from __future__ import annotations
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("crypto-agents")
OUT = Path("chief-D-reports")
OUT.mkdir(exist_ok=True)
CFG = json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
ORDERS = json.loads((ROOT/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
LEDGER_FILE = Path("d10-payment-reports/D10_TWO_ACCOUNT_PAYMENT_REPORT.json")
PAYMENTS = json.loads(LEDGER_FILE.read_text(encoding="utf-8")) if LEDGER_FILE.exists() else {}
CENSUS_FILE=Path("chief-D-reports/TWO_COMPANY_WORKFORCE_CENSUS.json")
CENSUS=json.loads(CENSUS_FILE.read_text(encoding="utf-8")) if CENSUS_FILE.exists() else {}
GH_REPO = "kwesigaamon8-web/Amon-Kwesiga"
GH_TOKEN = os.environ.get("GH_TOKEN","")
RUN_ID = os.environ.get("GITHUB_RUN_ID","")

assert CFG["hierarchy"]["chief_director"] == "D"
assert ORDERS["chief_director"] == "D"
assert CFG["hierarchy"]["distinct_local_director_count"] == 20
assert CFG["hierarchy"]["top_level_executive_count"] == 1
assert ORDERS["orders"] and ORDERS["orders"][-1]["id"] == ORDERS["current_owner_order_id"]

def gh_request(url, method="GET", body=None):
    headers={"User-Agent":"ChiefDTwoCompanyEvidence/1.0",
             "Accept":"application/vnd.github+json"}
    if GH_TOKEN:
        headers["Authorization"]="Bearer "+GH_TOKEN
    payload=json.dumps(body).encode("utf-8") if body is not None else None
    req=urllib.request.Request(url, data=payload, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)

latest_runs={}
try:
    runs=gh_request("https://api.github.com/repos/"+GH_REPO+
        "/actions/runs?per_page=85").get("workflow_runs",[])
    for x in runs:
        name=x.get("name","")
        if name in latest_runs: continue
        if name in ("Independent Crypto Opportunity Agents",
                    "BountyScoutAI Independent Workforce",
                    "Real Free-Hosted AI Worker Processes",
                    "BountyScoutAI Real AI Worker Processes"):
            latest_runs[name]={
                "run_id": x.get("id"),"status": x.get("status"),
                "conclusion": x.get("conclusion"),"url":x.get("html_url"),
                "started_or_created_at":x.get("run_started_at") or x.get("created_at")
            }
except Exception as err:
    latest_runs={"source_error":type(err).__name__+": "+str(err)[:120]}

# Independent company worker auditor summaries are published by GitHub Actions
# only after worker artifacts exist. This is source evidence, not an independent
# model-to-model peer review or proof of payment.
peer_published={}
try:
    for page in range(1,5):
        comments=gh_request("https://api.github.com/repos/"+GH_REPO+
            "/issues/9/comments?"+
            urllib.parse.urlencode({"per_page":100,"page":page}))
        for comment in comments:
            author=(comment.get("user") or {}).get("login")
            if author not in ("github-actions[bot]","kwesigaamon8-web"):
                continue
            body=str(comment.get("body") or "")
            for fleet in ("transferexperiment","BountyScoutAI"):
                if "<!-- all-to-all-peer-evidence:"+fleet+":" not in body:
                    continue
                nmatch=re.search(r"\*\*Actually executed worker reports assessed:\*\*\s*(\d+)",body)
                cmatch=re.search(r"\*\*Automated all-against-all comparisons:\*\*\s*([\d,]+)",body)
                fmatch=re.search(r"\*\*Pairwise coverage verified:\*\*\s*(True|False)",body)
                if not (nmatch and cmatch and fmatch):
                    continue
                n=int(nmatch.group(1))
                count=int(cmatch.group(1).replace(",",""))
                if n<0 or n>500 or count!=n*(n-1):
                    continue
                stamp=str(comment.get("created_at") or "")
                if stamp > peer_published.get(fleet,{}).get("created_at",""):
                    peer_published[fleet]={
                        "public_audit_state":"reported_in_owner_control_room",
                        "source":comment.get("html_url"),
                        "created_at":stamp,
                        "attempted_real_worker_reports_reported":n,
                        "deterministic_pairwise_checks_reported":count,
                        "pairwise_coverage_claimed":fmatch.group(1)=="True",
                        "actual_AI_worker_peer_reviews_confirmed":0,
                        "caveat":"Summary self-reported by controlled GitHub Actions job. Full artifact evidence still requires independent inspection."
                    }
        if len(comments)<100:
            break
except Exception as err:
    peer_published={"source_error":type(err).__name__+": "+str(err)[:120]}

pair={
    "transferexperiment":(
        "Independent Crypto Opportunity Agents",
        "Real Free-Hosted AI Worker Processes"),
    "BountyScoutAI":(
        "BountyScoutAI Independent Workforce",
        "BountyScoutAI Real AI Worker Processes")
}
companies={}
for fleet,(res,ai) in pair.items():
    board=CFG["hierarchy"]["companies"][fleet]
    proof=(PAYMENTS.get("accounts") or {}).get(fleet,{})
    companies[fleet]={
        "company_name":board["company"],
        "latest_public_peer_audit":peer_published.get(fleet,{"public_audit_state":"not_yet_published"}),
        "configured_role_positions":(CENSUS.get("companies") or {}).get(fleet,{}).get("mathematically_defined_total","not_assessed"),
        "billions_scale_descendants_actually_running":"not_verified_as_running",
        "independent_local_directors":board["local_director_ids"],
        "local_payment_director":board["local_payment_director"],
        "earning_directors":board["local_director_ids"][:9],
        "reports_to":"D",
        "account":board["account"],
        "research_workflow":latest_runs.get(res,{"status":"not_checked"}),
        "actual_model_worker_workflow":latest_runs.get(ai,{"status":"not_checked"}),
        "payment_evidence_inspected_by_own_local_director":bool(proof),
        "payment_purpose_verified":False,
        "external_authenticated_payer_contact_verified_by_chief_job":False,
        "wallet_receipts_new_this_job":"not_assessed",
        "raw_public_btc_output_snapshot":
             (proof.get("btc_output_snapshot") or {}).get("status","not_available"),
    }
assert set(companies)=={"transferexperiment","BountyScoutAI"}
assert len(set(companies["transferexperiment"]["independent_local_directors"]+
               companies["BountyScoutAI"]["independent_local_directors"]))==20
current=ORDERS["orders"][-1]
now=datetime.now(timezone.utc).isoformat()
report={
    "as_of_utc":now,
    "chief_director":"D",
    "chief_director_count":1,
    "receives_instructions_through":"ChatGPT relayed only after an explicit owner message",
    "last_owner_instruction_id":current["id"],
    "last_owner_instruction_text":current["instruction"],
    "reporting_chain":"Company A D01-D10 -> Chief D; Company B D01-D10 -> Chief D -> owner",
    "companies":companies,
    "local_director_total":20,
    "owner_active_worker_target":ORDERS.get("seven_billion_execution_target",{}).get("total_distinct_eligible_role_ids","not_defined"),
    "seven_billion_per_company":ORDERS.get("seven_billion_execution_target",{}).get("per_company","not_defined"),
    "seven_billion_actual_worker_acknowledgements_verified_by_chief_report":"not_assessed_no_completed_new_evidence",
    "seven_billion_actual_distinct_qualified_worker_completions_verified_by_chief_report":"not_assessed_no_completed_new_evidence",
    "seven_billion_pending_unexecuted_count":"not_computed_without_deduplicated_actual_run_history",
    "separate_company_peer_audit_summaries_found":sum(1 for fleet in ("transferexperiment","BountyScoutAI") if fleet in peer_published),
    "chief_D_peer_audit_assessment":"Evidence checks are automated; actual completed independent model peer reviews are not verified by this report.",
    "configured_company_positions_combined":CENSUS.get("combined_configured_company_role_positions","not_assessed"),
    "configured_positions_plus_one_chief_D":CENSUS.get("combined_configured_roles_plus_chief_D","not_assessed"),
    "billions_scale_positions_are_live_ai_models":False,
    "known_receivables_verified_by_chief_job":0,
    "actual_external_collections_by_chief_job":0,
    "new_crypto_earnings_verified_by_chief_job":"not_assessed",
    "evidence_limits":"Workflow status is not a customer contract or a new coin receipt. No program has authenticated its Moltbook credentials here. Evidence is restricted to accessible GitHub runs and optional local D10 public snapshots. Actual model outputs, external payer agreement and chain transaction history require separate audit. Repeated 'pending' or 'cancelled' workflow results are not verified work.",
}
(OUT/"CHIEF_D_TO_OWNER.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=[
  "# CHIEF D — CONSOLIDATED OWNER REPORT",
  "",
  "Date: "+now,
  "Owner order: "+current["id"],
  "",
  "**One Chief D** coordinates **two SEPARATE companies**, each with **its OWN 10 directors**, so 20 distinct local director IDs.",
  "**Defined role positions, both companies:** "+str(CENSUS.get("combined_configured_company_role_positions","not_assessed"))+" (not concurrently live AI models).",
  "**Grand total, including one Chief D:** "+str(CENSUS.get("combined_configured_roles_plus_chief_D","not_assessed"))+".",
  "**Owner priority: 7B specific eligible identities** (3.5B per company); real model execution and real order acknowledgement have NOT yet been verified against that target.",
  "**Latest owner instruction relayed by ChatGPT:** "+current["instruction"],
  ""
]
for fleet,x in companies.items():
    lines.extend([
        "## "+x["company_name"]+" — "+fleet,
        "Local directors: "+fleet+"/D01 through "+fleet+"/D10",
        "Mathematically defined positions: "+str(x["configured_role_positions"])+" (most are dormant definitions)",
        "Owner 7B campaign share: "+str(ORDERS.get("seven_billion_execution_target",{}).get("per_company","unknown"))+" distinct eligible H roles; not all concurrently running.",
        "Local payment director: "+x["local_payment_director"],
        "Worker-versus-worker audit evidence: "+str(x["latest_public_peer_audit"].get("public_audit_state","unknown")),
        "Deterministic comparisons published: "+str(x["latest_public_peer_audit"].get("deterministic_pairwise_checks_reported","not yet available")),
        "Actual individual peer AI-model critique: NOT VERIFIED.",
        "Local D01-D09 keep seeking legitimate income and doing authorized work.",
        "Research run: "+str(x["research_workflow"].get("status","unknown"))+
             " / "+str(x["research_workflow"].get("conclusion") or "unverified"),
        "AI model process run: "+str(x["actual_model_worker_workflow"].get("status","unknown"))+
             " / "+str(x["actual_model_worker_workflow"].get("conclusion") or "unverified"),
        "Local BTC evidence audit: "+str(x["raw_public_btc_output_snapshot"]),
        "Confirmed new crypto income by this reporting job: NOT ASSESSED.",
        ""
    ])
lines += [
    "## Direction from Chief D",
    "Prioritize authentic accepted/unpaid work and actionable payer messages; both local D10s reconcile only their own company's obligations and transfer evidence to Chief D. Other directors continue paid-work sourcing and real deliveries.",
    "## Limitations",
    report["evidence_limits"],
    "",
    "To send new instructions, owner tells ChatGPT, which updates Chief D's GitHub instructions. This workflow cannot listen to ChatGPT messages.",
]
(OUT/"CHIEF_D_TO_OWNER.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("CHIEF_D_CONSOLIDATION",json.dumps({
    "chief":"D","boards":2,"directors_each":10,
    "total_local_directors":20,"last_order":current["id"],
    "workflows_checked":sum(1 for v in companies.values() for key in (
      "research_workflow","actual_model_worker_workflow") if "run_id" in v[key]),
    "verified_new_income":"not_assessed"
}))
# Publish once per new owner order / UTC day; use GitHub issue comments as
# durable evidence, NOT as direct ChatGPT delivery or a live Moltbook post.
if GH_TOKEN and os.environ.get("GITHUB_REPOSITORY")==GH_REPO:
    comments_url="https://api.github.com/repos/"+GH_REPO+"/issues/9/comments"
    marker="<!-- chief-D-owner:"+current["id"]+":"+now[:10]+":peer-"+str(report["separate_company_peer_audit_summaries_found"])+" -->"
    try:
        posted=False
        for page in range(1,5):
            responses=gh_request(comments_url+"?"+
                urllib.parse.urlencode({"per_page":100,"page":page}))
            if any(marker in (c.get("body") or "") for c in responses):
                posted=True
                break
            if len(responses)<100:
                break
        if not posted:
            body=marker+"\n"+("\n".join(lines))[:13000]
            result=gh_request(comments_url,method="POST",body={"body":body})
            print("CHIEF_D_REPORT_POSTED",result.get("html_url"))
        else:
            print("CHIEF_D_REPORT_ALREADY_SHARED_FOR_ORDER_TODAY")
    except Exception as err:
        print("CHIEF_D_REPORT_GITHUB_POST_BLOCKED",type(err).__name__,str(err)[:180])
