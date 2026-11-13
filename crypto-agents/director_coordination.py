"""Single, auditable intra-team communications register.

Independent 30 researcher jobs finish first. This consolidation passes
their evidence to ten directors, routes each distinct lead to one owner,
records risks and blockers, and produces handoffs for subsequent cycles.
No posting, payment, applications or wallet actions occur here.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path("combined-reports")
OUT = Path("director-communications")
OUT.mkdir(exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()
DIRECTORS = ["D%02d" % i for i in range(1,11)]
STRENGTHS = {
  "D01": "BTC-paid freelance and Bitcoin-related opportunities",
  "D02": "USDC, stablecoin contract work and authentic payment networks",
  "D03": "AI-agents, automation and AI developer work",
  "D04": "Bookkeeping, QuickBooks, tax-support and accounting contracts",
  "D05": "Verifiable open-source bounties",
  "D06": "AI testing, research and data microtasks",
  "D07": "Direct client requests and recurring finance services",
  "D08": "Open competitions and grants with cash awards",
  "D09": "Payer legitimacy, hidden fee and payment-network verification",
  "D10": "Oversight, independent challenge and completion metrics"
}
KEYWORDS = {
  "D01": ("bitcoin","btc","lightning"),
  "D02": ("usdc","usdt","stablecoin"),
  "D03": ("ai agent","automation","agent","model evaluation"),
  "D04": ("accounting","bookkeep","quickbooks","tax","payroll"),
  "D05": ("bounty","open source","github issue","funded"),
  "D06": ("annotation","training data","microtask","evaluation"),
  "D07": ("looking for","need accountant","client","freelance","contractor"),
  "D08": ("grant","prize","hackathon","competition")
}
def canonical(u):
    try:
        s = urlsplit(str(u or "").strip())
        if s.scheme != "https" or not s.netloc:
            return None
        if "@" in s.netloc:
            return None
        filtered = [(k,v) for k,v in parse_qsl(s.query,keep_blank_values=True)
                    if not (k.lower().startswith("utm_") or k.lower() in ("ref","fbclid","gclid"))]
        return urlunsplit(("https",s.netloc.lower(),s.path.rstrip("/"),urlencode(filtered),""))
    except (ValueError,TypeError):
        return None

def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,ValueError):
        return {}

reports = {}
branch_reports = {}
branch_summaries = {}
for path in ROOT.rglob("*.json"):
    obj = read_json(path)
    if re.fullmatch(r"D\d\d(?:-[AB])?",str(obj.get("role",""))):
        reports[obj["role"]] = obj
    if obj.get("subagent_id") and obj.get("branch_manager"):
        branch_reports[obj["subagent_id"]] = obj
    if obj.get("branch_manager") and obj.get("subagent_count") == 15:
        branch_summaries[obj["branch_manager"]] = obj

summary = read_json("summary.json")
raw = summary.get("qualified_unverified_leads", [])
leads, seen = [], set()
for lead in raw:
    u=canonical(lead.get("url"))
    if not u or u in seen:
        continue
    seen.add(u)
    text = (str(lead.get("title") or "")+" "+str(lead.get("evidence_excerpt") or "")).lower()
    # Assign a single owner based on fit, not by whoever found it first.
    # D09 remains the skeptical cross-team checker; D10 oversees.
    weights = {d:sum(1 for k in words if k in text) for d,words in KEYWORDS.items()}
    score = max(weights.values(), default=0)
    if score == 0:
        owner = (lead.get("director") if lead.get("director") in KEYWORDS else "D07")
    else:
        owners = sorted(d for d,v in weights.items() if v == score)
        owner = owners[0]
    status = "research_candidate_unverified"
    leadrec = {
        "url":u,"title":str(lead.get("title") or "")[:180],
        "origin_role":lead.get("researcher"),"origin_director":lead.get("director"),
        "assigned_director":owner,"independent_checker":"D09",
        "accountability_director":"D10","status":status,
        "source_rechecked":bool(lead.get("original_source_refetched")),
        "payment_received_verified":False,
        "known_risks":lead.get("risk_and_counterevidence",[])[:4],
        "unknowns":lead.get("unknowns",[])[:5],
        "next_action":"Read original payer conditions; verify availability, amount, Uganda eligibility and route, then prepare a truthful no-fee proposal only if feasible.",
        "outreach_attempted":False, "contract_awarded":False
    }
    leads.append(leadrec)
    
all_role_ids = [d+s for d in DIRECTORS for s in ("","-A","-B")]
messages = []
for d in DIRECTORS:
    owned = [x for x in leads if x["assigned_director"] == d]
    three = [d,d+"-A",d+"-B"]
    child = [r for r in branch_reports.values() if r.get("branch_manager") in three]
    unique_branch_leads = set()
    for worker in child:
        for lead in worker.get("leads",[]):
            u=canonical(lead.get("url"))
            if u: unique_branch_leads.add(u)
    api_errors = sum(len(reports.get(r,{}).get("source_errors",[])) for r in three)
    api_errors += sum(r.get("status")=="source_unavailable" for r in child)
    completed_workers = sum(r.get("status")=="completed" for r in child)
    original_sources = sum(sum(bool(z.get("source_refetched")) for z in reports.get(r,{}).get("deep_research",{}).get("dossiers",[])) for r in three)
    independent_ai = sum(reports.get(r,{}).get("ai_analysis",{}).get("status")=="llm_completed" for r in three)
    roles_reporting = [r for r in three if r in reports]
    cross_team = [x for x in owned if x["origin_director"] != d]
    handoffs = [{"from":x["origin_director"],"to":d,"source_url":x["url"],"requested_check":x["next_action"]} for x in cross_team]
    msg = {
        "director":d,"specialty":STRENGTHS[d],
        "time_utc":NOW,
        "own_roles_reporting":len(roles_reporting),
        "own_roles_expected":3,
        "delegated_workers_expected":45,
        "delegated_worker_reports_received":len(child),
        "successful_worker_source_searches":completed_workers,
        "branch_reports_with_source_errors":sum(r.get("status")=="source_unavailable" for r in child),
        "team_source_errors":api_errors,
        "distinct_unverified_branch_leads":len(unique_branch_leads),
        "independent_ai_reviews_completed":independent_ai,
        "original_github_source_checks":original_sources,
        "assigned_qualified_leads":owned[:8],
        "handoffs_received":handoffs[:8],
        "handoffs_to_other_directors":[
            {"to":x["assigned_director"],"source_url":x["url"]}
            for x in leads if x["origin_director"] == d and x["assigned_director"] != d
        ][:8],
        "independent_decisions_permitted":[
            "Investigate and reject weak sources without waiting",
            "Choose promising no-fee research topics across specialties",
            "Draft a truthful approach for an eligible task",
            "Request independent checking from D09 via a documented handoff"
        ],
        "restricted_actions":["No unsanctioned outreach, signatures, payments, wallet transfers or contracts"],
        "mandatory_quality_review":"Check source evidence, counterevidence, duplicate ownership, fees, scope, Uganda eligibility and real payment feasibility.",
        "cooperation_message":"Give one accountable director each canonical lead; share counterevidence and avoid duplicated applications.",
        "mission":"Verified paid assignments and transferable receipts are outcomes; lead counts are only activity metrics.",
        "verified_received_earnings": []
    }
    if d == "D09":
        msg["cross_team_critical_queue"] = [
            {"url":x["url"],"director_owner":x["assigned_director"],"risks":x["known_risks"]}
            for x in leads[:15]]
    if d == "D10":
        msg["fleet_audit"] = {
            "bosses_expected":30,"branches_reporting":len(branch_summaries),
            "delegated_workers_expected":450,"distinct_worker_reports":len(branch_reports),
            "unique_screened_candidates":len(leads),
            "duplicate_candidate_records_removed":max(0,len(raw)-len(leads)),
            "payment_receipts_verified_from_this_research":0,
            "all_directors_reporting":len(reports.keys() & set(DIRECTORS))
        }
    messages.append(msg)
    (OUT/(d+".json")).write_text(json.dumps(msg,indent=2),encoding="utf-8")

document = {
    "schema":"director-coordination-v1","created_at_utc":NOW,
    "directors":len(messages), "main_worker_reports":len(reports),
    "branch_workers_reporting":len(branch_reports),
    "candidate_leads_before_dedup":len(raw),"canonical_leads_after_dedup":len(leads),
    "handoff_register":leads,
    "director_message_files":[d+".json" for d in DIRECTORS],
    "reporting_limitations":"Asynchronous programmatic handoffs, not ten separate social identities or live private agent conversations. Source hits and proposals are not earnings.",
    "payment_receipts_verified": []
}
(OUT/"coordination.json").write_text(json.dumps(document,indent=2),encoding="utf-8")
lines=["# Shared director communication and performance board", "",
       "Asynchronous cross-team evidence exchange, not independent chat identities. Payment claims require separate verification.",
       "",f"Workers reported: {len(reports)}/30 main roles; {len(branch_reports)}/450 delegated roles.",
       f"Nonduplicated screened leads: {len(leads)}; assigned one owner each; D09 checks claims, D10 audits outcomes.",
       "", "| Director | Team reports | Branch researcher outputs | Source issues | Assigned leads | Incoming handoffs |",
       "|---|---:|---:|---:|---:|---:|"]
for m in messages:
    lines.append(f"| {m['director']} | {m['own_roles_reporting']}/3 | {m['delegated_worker_reports_received']}/45 | {m['team_source_errors']} | {len(m['assigned_qualified_leads'])} | {len(m['handoffs_received'])} |")
lines += ["", "## One owner per distinct candidate lead"]
for lead in leads[:15]:
    lines.append(f"- {lead['assigned_director']} owns [{lead['title'].replace('[','(').replace(']',')')}]({lead['url']}); D09 must challenge. Status: unverified research only")
if not leads:
    lines.append("No screened lead received an owner assignment this cycle. Directors should improve source quality, not invent prospects.")
lines += ["", "## Expected next decisions",
          "Every director may independently choose leads to investigate or reject and prepare a draft, but may not claim outreach, negotiated commitments, fund transfers or payments it has not actually made.",
          "D10 compares evidence and progress. Paid receipts: **none established by research**."]
(OUT/"INDEX.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("COORDINATION", len(messages), "directors",len(reports),"main reports",len(branch_reports),"subagents",len(leads),"unique leads")
