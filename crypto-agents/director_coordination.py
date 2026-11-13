"""Cross-company, one-owner source handoff and director performance register.

Ten directors supervise independent assistant A and B plus fifteen company
managers each. A manager independently evaluates exactly fifty unique workers.
Source-linked handoffs share evidence, not reporting lines. None of this
is proof of a job application, successful payment or social account.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT=Path("combined-reports")
OUT=Path("director-communications")
OUT.mkdir(exist_ok=True)
NOW=datetime.now(timezone.utc).isoformat()
D=[f"D{i:02d}" for i in range(1,11)]
STRENGTHS={
    "D01":"BTC-paid work","D02":"USDC contracts","D03":"AI-agent tasks",
    "D04":"Accounting and bookkeeping","D05":"Open source bounties",
    "D06":"AI evaluation microtasks","D07":"Direct clients",
    "D08":"Competitions and grants","D09":"Payer and payment legitimacy",
    "D10":"Mission quality and earnings accountability"
}
KEYWORDS={
    "D01":["bitcoin","btc"],"D02":["usdc","stablecoin"],
    "D03":["agent","automation"],"D04":["accounting","bookkeep","quickbooks","payroll"],
    "D05":["bounty","open source"],"D06":["annotation","model evaluation"],
    "D07":["client","freelance","contractor"],"D08":["grant","prize","competition"]
}
def canonical(s):
    try:
        p=urlsplit(str(s or "").strip())
        if p.scheme!="https" or not p.netloc or "@" in p.netloc:
            return None
        q=[(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith("utm_") and k.lower() not in ("ref","fbclid")]
        return urlunsplit(("https",p.netloc.lower(),p.path.rstrip("/"),urlencode(q),""))
    except (ValueError,TypeError):
        return None
def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError):
        return {}
roles,companies,managers,workers={},{},{},{}
for path in ROOT.rglob("*.json"):
    r=load(path)
    if re.fullmatch(r"D\d\d(?:-[AB])?",str(r.get("role",""))):
        roles[r["role"]]=r
    if r.get("configured_managers")==15 and r.get("director_id") in D:
        companies[r["director_id"]]=r
    elif r.get("manager_id") and r.get("workers_executed_this_cycle") is not None:
        managers[r["manager_id"]]=r
    elif r.get("worker_id") and r.get("manager_id"):
        workers[r["worker_id"]]=r

src=load(Path("summary.json"))
found=src.get("qualified_unverified_leads",[])
dedup={}
for lead in found:
    u=canonical(lead.get("url"))
    if not u or u in dedup:
        continue
    label=(str(lead.get("title") or "")+" "+str(lead.get("evidence_excerpt") or "")).lower()
    scores={d:sum(k in label for k in keys) for d,keys in KEYWORDS.items()}
    max_score=max(scores.values())
    assigned=sorted(d for d,v in scores.items() if v==max_score)[0] if max_score else (
        lead.get("director") if lead.get("director") in KEYWORDS else "D07")
    dedup[u]={
        "url":u,"title":str(lead.get("title") or "")[:180],
        "assigned_director":assigned,"origin_director":lead.get("director"),
        "discovered_by":lead.get("researcher"),
        "d09_payment_checker":"D09","d10_quality_checker":"D10",
        "risks":lead.get("risk_and_counterevidence",[])[:5],
        "unknowns":lead.get("unknowns",[])[:6],
        "current_status":"unverified_research_candidate",
        "paid_assignment_confirmed":False,"payment_received_verified":False,
        "next_action":"Review original source; check scope, payer, country eligibility, amount, no-fee condition and exact network before drafting work proposal."
    }
handoffs=list(dedup.values())
messages=[]
for director in D:
    assistants=[director+"-A",director+"-B"]
    manager_ids=[f"{director}-M{i:02d}" for i in range(1,16)]
    director_managers=[managers[m] for m in manager_ids if m in managers]
    child=[w for w in workers.values() if w.get("director_id")==director]
    main=[director,*assistants]
    owned=[lead for lead in handoffs if lead["assigned_director"]==director]
    errors=sum(len(roles.get(r,{}).get("source_errors",[])) for r in main)
    errors+=sum(w.get("execution_status")=="source_unavailable" for w in child)
    msg={
      "director":director,"specialty":STRENGTHS[director],
      "created_at_utc":NOW,"independent_assistant_ids":assistants,
      "one_parent_reporting_line":f"Assistants {assistants[0]} and {assistants[1]} report only to {director}; each of 15 managers reports only to {director}; each worker reports only to its allocated manager.",
      "own_roles_expected":3,
      "own_roles_reporting":sum(r in roles for r in main),
      "company_id":"COMP-"+director,
      "company_report_received":director in companies,
      "managers_configured":15,
      "manager_reports_received":len(director_managers),
      "worker_roles_configured":750,
      "delegated_worker_reports_received":len(child),
      "worker_ai_completed":sum(w.get("model_inference",{}).get("status")=="model_completed" for w in child),
      "manager_ai_completed":sum(m.get("model_inference",{}).get("status")=="model_completed" for m in director_managers),
      "team_source_errors":errors,
      "assigned_qualified_leads":owned[:8],
      "handoffs_received":[{"from":x.get("origin_director"),"to":director,"source_url":x["url"]}
          for x in owned if x.get("origin_director")!=director][:8],
      "handoffs_sent":[{"to":x["assigned_director"],"source_url":x["url"]}
          for x in handoffs if x.get("origin_director")==director and x["assigned_director"]!=director][:8],
      "allowed_independent_actions":["Find, inspect, challenge and reject leads",
          "Choose research priorities and document source-linked cross-company handoffs",
          "Prepare proposals, but only send using an authorized authenticated tool"],
      "restricted_actions":["No unsupported outreach, fee, private key, wallet signing or transfer"],
      "mission":"Real legitimate compensated assignments and independently evidenced incoming payments, not number of registered agents.",
      "verified_paid_receipts":[]
    }
    if director=="D09":
        msg["critical_review_queue"]=handoffs[:15]
    if director=="D10":
        msg["teamwide_performance"]={
            "configured_companies":10,"companies_reporting":len(companies),
            "managers_configured":150,"managers_reporting":len(managers),
            "specialist_roles_configured":7500,"worker_reports_generated":len(workers),
            "worker_model_inference_completed":sum(w.get("model_inference",{}).get("status")=="model_completed" for w in workers.values()),
            "manager_model_inference_completed":sum(m.get("model_inference",{}).get("status")=="model_completed" for m in managers.values()),
            "independent_assistants_expected":20,
            "independent_assistants_reporting":sum(f"D{i:02d}-{a}" in roles for i in range(1,11) for a in ("A","B")),
            "distinct_screened_candidate_urls":len(handoffs),
            "verified_receipts":0
        }
    messages.append(msg)
    (OUT/(director+".json")).write_text(json.dumps(msg,indent=2),encoding="utf-8")
document={
 "schema":"ten-company-director-coordination-v2",
 "generated_at_utc":NOW,"director_reports":len(messages),
 "company_reports_received":len(companies),"manager_reports_received":len(managers),
 "unique_worker_reports_received":len(workers),
 "worker_llm_inferences_completed":sum(w.get("model_inference",{}).get("status")=="model_completed" for w in workers.values()),
 "source_candidates_before_dedup":len(found),"unique_candidates_after_dedup":len(handoffs),
 "handoff_register":handoffs,"verified_paid_receipts":[],
 "limitation":"These are unique role-specific independent model inferences, not 7,680 concurrent AI processes or independently authenticated social accounts."
}
(OUT/"coordination.json").write_text(json.dumps(document,indent=2),encoding="utf-8")
lines=[
 "# Ten director companies: performance and one-parent reporting","",
 f"UTC: {NOW}. Distinct source candidates: {len(handoffs)} (all still unverified).",
 "",
 "| Director | Main reports | 15 managers | Worker outputs (of 750 configured) | Actual worker AI inferences | Source errors | Leads assigned |",
 "|---|---:|---:|---:|---:|---:|---:|"
]
for m in messages:
    lines.append(f"| {m['director']} | {m['own_roles_reporting']}/3 | {m['manager_reports_received']}/15 | {m['delegated_worker_reports_received']} | {m['worker_ai_completed']} | {m['team_source_errors']} | {len(m['assigned_qualified_leads'])} |")
lines.extend(["","## Handoff register"])
for x in handoffs[:12]:
    lines.append(f"- {x['assigned_director']} owns [{x['title'].replace('[','(').replace(']',')')}]({x['url']}); D09 challenges authenticity. No verified payment.")
if not handoffs:lines.append("No lead met the evidence screening conditions; no fabricated progress.")
lines.extend(["","## Governance","Each specialist worker reports to one manager, each manager to one director, each independent assistant directly to one director, and each director to the owner. Cross-company evidence handoffs do not alter the reporting line.","**Money received from the research fleet: none independently established.**"])
(OUT/"INDEX.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("DIRECTOR_COORDINATION",len(messages),"directors",len(managers),"manager files",len(workers),"worker files",len(handoffs),"unique screened leads")
