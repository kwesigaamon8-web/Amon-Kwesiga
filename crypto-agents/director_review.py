"""Director-to-assistant coordination reports for 10 directors and 20 assistants.

Each director reads its own two assistants' finished work at the end of
a scheduled cloud research cycle. Research evidence is not paid earnings.
No network calls, wallet use, API credentials, or account actions.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("combined-reports")
OUTPUT = Path("director-reports")
OUTPUT.mkdir(exist_ok=True)
ROLES = json.loads(Path("crypto-agents/roles.json").read_text(encoding="utf-8"))
ROLE_NAMES = {r["id"]: r["name"] for r in ROLES}
reports = {}
for file in sorted(ROOT.rglob("*.json")):
    try:
        obj = json.loads(file.read_text(encoding="utf-8"))
        if obj.get("role") in ROLE_NAMES:
            reports[obj["role"]] = obj
    except (ValueError, OSError):
        pass

qualified = json.loads(Path("summary.json").read_text(encoding="utf-8"))
strong = qualified.get("qualified_unverified_leads", [])
qualified_urls = {x.get("url"): x for x in strong}
directors = [f"D{i:02d}" for i in range(1, 11)]
now = datetime.now(timezone.utc).isoformat()
rows = ["# Director accountability — 10 directors, 20 assistants", "",
        "All payees, job terms, eligibility, and actual receipts require external verification.",
        "These are cloud research workers, not separate Moltbook user accounts.",
        "", "| Director | Direct report | Assistant A | Assistant B | Qualified leads |",
        "|---|---:|---:|---:|---:|"]
all_reviewed_urls = set()
for d in directors:
    ids = [d, d + "-A", d + "-B"]
    sources = [reports.get(role_id) for role_id in ids]
    raw = []
    seen = set()
    for role_id, report in zip(ids, sources):
        if not report:
            continue
        for lead in report.get("leads", []):
            url = lead.get("url", "")
            if url and url not in seen:
                raw.append({"researcher": role_id, "title": lead.get("title",""),
                            "url": url, "source": lead.get("source","")})
                seen.add(url)
    reviewed = [dict(qualified_urls[x["url"]], discovered_by_team=d)
                for x in raw if x["url"] in qualified_urls]
    all_reviewed_urls.update(item["url"] for item in reviewed)
    review = {
        "director_id": d,
        "director_name": ROLE_NAMES[d],
        "review_timestamp_utc": now,
        "own_research_report_present": sources[0] is not None,
        "assistant_a_report_present": sources[1] is not None,
        "assistant_b_report_present": sources[2] is not None,
        "assistant_report_ids": ids[1:],
        "individual_ai_reviews": {role_id: (reports.get(role_id) or {}).get("ai_analysis", {}).get("status", "missing") for role_id in ids},
        "distinct_raw_leads_reviewed": len(raw),
        "qualified_leads_require_manual_checks": reviewed,
        "next_actions": [
            "Review each lead's current source, exact payout, qualification requirements, country eligibility and payment method.",
            "Reject requests for application fees, wallet connection, transfers, identity exposure without legitimate purpose, or contract approval.",
            "Owner authorizes independent scouting and proposal preparation. For a genuine eligible opportunity, draft a tailored, truthful approach and a network-appropriate payout request; send only when an authenticated tool actually supports it and platform rules allow.",
            "Record independently confirmed payment receipts only with transaction/network evidence, not lead counts."
        ],
        "owner_authorized_independence": True,
        "payout_priority": "Direct verified earnings into a user-approved address on the exact supported network; never guess full addresses or reveal a private user wallet map in this public repository.",
        "outreach_capability": "Not available through this workflow: it can research, draft, and rank but cannot post, apply, sign, or remit.",
        "verified_earnings": [],
        "mission_reminder": "The measure of success is actual legitimate transferable payment to the user, not research volume or token spam."
    }
    if d == "D10":
        review["teamwide_accountability"] = {
            "expected_roles": 30,
            "reported_roles": len(reports),
            "ai_reviews_completed": sum(v.get("ai_analysis",{}).get("status") == "llm_completed" for v in reports.values()),
            "total_qualified_leads": len(strong),
            "verified_payment_receipts": 0,
            "message_to_all_directors": "Owner authorizes independent work. Search worldwide, prioritize payouts to an approved correct-network owner address, protect wallet access, and report only verified income as received."
        }
    (OUTPUT / f"{d}.json").write_text(json.dumps(review, indent=2), encoding="utf-8")
    rows.append(f"| {d} — {ROLE_NAMES[d].replace('Director: ','')} | {'Yes' if sources[0] else 'No'} | {'Yes' if sources[1] else 'No'} | {'Yes' if sources[2] else 'No'} | {len(reviewed)} |")
rows += ["", "## Actionable lead policy",
         "A qualified lead remains **unverified** until terms, payer, availability, and Uganda eligibility are checked.",
         "No wallet signatures, deposits, fees or unsolicited social posting.",
         "D10 reiterates the mission to each team; only independently verified earnings count as payments.",
         "", f"Total unique qualified unverified leads seen by directors: {len(all_reviewed_urls)}."]
(OUTPUT/"INDEX.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
print("DIRECTOR_COORDINATION",len(directors),"directors",len(reports),"research reports",len(all_reviewed_urls),"qualified urls")
