"""Consolidate independently generated role reports with strict payout evidence checks.

This is NOT a wallet monitor and never claims earnings. Reports are public-source leads.
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

root = Path(sys.argv[1] if len(sys.argv) > 1 else "combined-reports")
files = sorted(root.rglob("*.json")) if root.exists() else []
reports = []
bad = []
for path in files:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("role") and isinstance(report.get("leads"), list):
            reports.append(report)
    except Exception as exc:
        bad.append(str(path) + ": " + str(exc)[:80])

branch_manifest=json.loads(Path("crypto-agents/branch_manifest.json").read_text(encoding="utf-8"))
expected_subagents={a["id"] for branch in branch_manifest["branches"] for a in branch["agents"]}
branch_reports={}
branch_summaries={}
for subpath in root.rglob("*.json"):
    try:
        subobj=json.loads(subpath.read_text(encoding="utf-8"))
        if subobj.get("subagent_id") in expected_subagents:
            branch_reports[subobj["subagent_id"]]=subobj
        elif subobj.get("branch_manager") and subobj.get("subagent_count") == 15:
            branch_summaries[subobj["branch_manager"]]=subobj
    except (ValueError, OSError):
        pass

today = datetime.now(timezone.utc)
cutoff = today - timedelta(days=45)
def recent(s):
    if not s:
        return False
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return t >= cutoff
    except (TypeError, ValueError):
        return False

money_pattern = re.compile(r"(?i)(?:\$|US\$|USD\s*|USDC\s*|USDT\s*|BTC\s+)(?:[0-9][0-9,]*(?:\.[0-9]+)?)")
paid_pattern = re.compile(r"(?i)\b(?:bounty|paid task|paid contract|reward|freelance|hiring|contractor|job opening)\b")
job_pattern = re.compile(r"(?i)\b(?:accountant|bookkeep|quickbooks|tax specialist|remote finance|accounting|payroll)\b")
exclude = re.compile(r"(?i)\b(?:show hn|ask hn|feature request|policy|daily content|prompt-feedback|roadmap|content opportunities|mission statement|explainer)\b")
qualified = []
seen = set()
dossiers_by_url = {}
for report in reports:
    for dossier in report.get("deep_research", {}).get("dossiers", []):
        url = dossier.get("url")
        if url and (url not in dossiers_by_url or
                dossier.get("score_for_followup_not_payment_probability", 0) >
                dossiers_by_url[url].get("score_for_followup_not_payment_probability", 0)):
            dossiers_by_url[url] = dossier
for r in reports:
    for x in r.get("leads", []):
        url = x.get("url", "").strip()
        if not url.startswith("https://") or url in seen or not recent(x.get("updated")):
            continue
        title = x.get("title", "")
        snippet = x.get("excerpt", "")[:350]
        combined = title + " " + snippet
        if exclude.search(title):
            continue
        parsed = urlparse(url)
        from_github = parsed.netloc.lower() == "github.com" and "/issues/" in parsed.path
        # A GitHub issue is only a qualified bounty lead if it explicitly
        # mentions both payment and a monetary amount in public source text.
        strong_bounty = from_github and bool(money_pattern.search(combined)) and bool(paid_pattern.search(combined))
        # Fresh accounting listings elsewhere need a direct job URL and
        # hiring language, but payment/eligibility remain unverified.
        direct_job = (x.get("source") == "Jobicy" and bool(job_pattern.search(combined))) or (not from_github and any(part in parsed.path.lower() for part in ("/jobs/", "/job/", "/careers/", "/positions/")) and bool(job_pattern.search(combined)) and bool(paid_pattern.search(combined)))
        # Social posts are only possible leads, never verified vacancies.
        # Require a current, explicit paid-work signal and a money amount or
        # relevant work description before placing them on the review shortlist.
        social_source = x.get("source") in ("Bluesky public post", "Reddit public post")
        social_text = combined.lower()
        social_action = any(k in social_text for k in ("hiring", "looking for", "need a bookkeeper",
            "need an accountant", "paid bounty", "paid task", "paid gig", "paid contract", "freelance work"))
        social_candidate = (social_source and (today - timedelta(days=7) <=
            datetime.fromisoformat(x["updated"].replace("Z","+00:00")).astimezone(timezone.utc))
            and social_action and (bool(money_pattern.search(combined)) or bool(job_pattern.search(combined))))
        if not (strong_bounty or direct_job or social_candidate):
            continue
        dossier = dossiers_by_url.get(url)
        if dossier and dossier.get("outcome") in ("avoid_until_risk_resolved", "reject_closed"):
            continue
        if from_github and (not dossier or not dossier.get("source_refetched")):
            # A GitHub issue scraped from search but not independently rechecked
            # is not a sufficiently substantiated bounty lead.
            continue
        seen.add(url)
        qualified.append({
            "director": r.get("director"), "researcher": r.get("role"),
            "title": title, "url": url, "source": x.get("source"),
            "updated": x.get("updated"), "evidence_excerpt": snippet,
            "amount_claimed_in_source": bool(money_pattern.search(combined)),
            "Uganda_eligibility_verified": False, "payment_verified": False,
            "status": "candidate_requires_manual_verification",
            "original_source_refetched": bool(dossier and dossier.get("source_refetched")),
            "followup_priority_score_not_payment_probability": dossier.get("score_for_followup_not_payment_probability") if dossier else None,
            "risk_and_counterevidence": (dossier.get("counter_evidence_and_risks", []) if dossier else ["Not independently rechecked in this cycle"]),
            "unknowns": (dossier.get("unknowns", []) if dossier else ["Payer, terms, eligibility and payment remain unverified"])
        })

qualified.sort(key=lambda x: (x["amount_claimed_in_source"], x["updated"]), reverse=True)
out = {
    "generated_at_utc": today.isoformat(),
    "expected_research_jobs": 30, "report_count": len(reports),
    "expected_branches": len(branch_manifest["branches"]),
    "branches_reporting": len(branch_summaries),
    "expected_subagents": len(expected_subagents),
    "distinct_subagent_reports_received": len(branch_reports),
    "missing_subagent_ids": sorted(expected_subagents.difference(branch_reports.keys())),
    "branch_source_failures": sum(r.get("status")=="source_unavailable" for r in branch_reports.values()),
    "branch_unverified_leads": sum(len(r.get("leads", [])) for r in branch_reports.values()),
    "researcher_ids": sorted({r["role"] for r in reports}),
    "AI_review_completed": sum(r.get("ai_analysis", {}).get("status") == "llm_completed" for r in reports),
    "adversarial_AI_challenges_completed": sum(r.get("ai_analysis", {}).get("critical_challenge_status") == "completed" for r in reports),
    "original_source_records_refetched": sum(sum(1 for x in r.get("deep_research",{}).get("dossiers",[]) if x.get("source_refetched")) for r in reports),
    "deep_research_dossiers_written": sum(len(r.get("deep_research",{}).get("dossiers",[])) for r in reports),
    "source_errors_count": sum(len(r.get("source_errors", [])) for r in reports),
    "public_social_candidates": sum(1 for x in qualified if x["source"] in ("Bluesky public post", "Reddit public post")),
    "social_sources_checked": ["Bluesky", "Reddit"],
    "qualified_unverified_leads": qualified[:35],
    "verified_paid_receipts": [],
    "warnings": [
        "Leads are not earnings, confirmed work, or verified payment offers.",
        "No deposit or payment is claimed; confirmation requires independent transaction or payer evidence.",
        "Do not pay fees, connect wallets or approve contracts to claim jobs or tokens.",
        "Mission reminder director D10: focus on real transferable value and legitimate paid work worldwide."
    ],
    "unreadable_report_files": bad
}
Path("summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
lines = [
    "# Independent crypto opportunity fleet — consolidated report",
    "", f"UTC: {today.isoformat()}",
    f"Research jobs with reports: **{len(reports)}/30**",
    f"Reporting branch supervisors: **{out['branches_reporting']}/{out['expected_branches']}**",
    f"Individual branch researcher outputs: **{out['distinct_subagent_reports_received']}/{out['expected_subagents']}**",
    f"Branch source errors: **{out['branch_source_failures']}**",
    f"Small-model AI reviews completed: **{out['AI_review_completed']}**",
    f"Adversarial AI challenges completed: **{out['adversarial_AI_challenges_completed']}**",
    f"Original sources independently refetched: **{out['original_source_records_refetched']}**",
    f"Evidence/risk dossiers completed: **{out['deep_research_dossiers_written']}**",
    f"Source errors: **{out['source_errors_count']}**",
    f"Strictly screened candidate leads: **{len(qualified)}**",
    f"Unverified social-source candidates: **{out['public_social_candidates']}**",
    "**Verified new earnings: none established by this research workflow.**",
    "", "## Director 10 — mission reminder",
    "Real, legitimately earned payments are the deliverable. Search worldwide. Never misclassify leads, token spam, unverified transfers, or offers as received income.",
    "", "## Screened follow-ups (still unverified)"
]
if qualified:
    for x in qualified[:20]:
        lines.append(f"- [{x['title'].replace('[','(').replace(']',')')}]({x['url']}) — {x['researcher']} (updated {x['updated']}); eligibility, payer and terms still require verification")
else:
    lines.append("No lead met the freshness and explicit payment/job evidence gate. Older or unrelated search hits were deliberately excluded.")
lines.extend(["", "## Controls", "Public-source research only. No account actions, posting, wallet interactions, or payments."])
body = "\n".join(lines) + "\n"
Path("summary.md").write_text(body, encoding="utf-8")
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(body)
print("report_count", len(reports), "ai_reviews", out["AI_review_completed"], "qualified_leads", len(qualified))
