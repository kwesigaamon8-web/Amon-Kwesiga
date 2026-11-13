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

today = datetime.now(timezone.utc)
cutoff = today - timedelta(days=45)
def recent(s):
    if not s:
        return False
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return t >= cutoff
    except (TypeError, ValueError):
        return False

money_pattern = re.compile(r"(?i)(?:\$|US\$|USD\s*|USDC\s*|USDT\s*|BTC\s+)(?:[0-9][0-9,]*(?:\.[0-9]+)?)")
paid_pattern = re.compile(r"(?i)\b(?:bounty|paid task|paid contract|reward|freelance|hiring|contractor|job opening)\b")
job_pattern = re.compile(r"(?i)\b(?:accountant|bookkeep|quickbooks|tax specialist|remote finance|accounting|payroll)\b")
exclude = re.compile(r"(?i)\b(?:show hn|ask hn|feature request|policy|daily content|prompt-feedback|roadmap|content opportunities|mission statement|explainer)\b")
qualified = []
seen = set()
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
        direct_job = not from_github and any(s in parsed.path.lower() for s in ("/jobs/", "/job/", "/careers/", "/positions/")) and bool(job_pattern.search(combined)) and bool(paid_pattern.search(combined))
        if not (strong_bounty or direct_job):
            continue
        seen.add(url)
        qualified.append({
            "director": r.get("director"), "researcher": r.get("role"),
            "title": title, "url": url, "source": x.get("source"),
            "updated": x.get("updated"), "evidence_excerpt": snippet,
            "amount_claimed_in_source": bool(money_pattern.search(combined)),
            "Uganda_eligibility_verified": False, "payment_verified": False,
            "status": "candidate_requires_manual_verification"
        })

qualified.sort(key=lambda x: (x["amount_claimed_in_source"], x["updated"]), reverse=True)
out = {
    "generated_at_utc": today.isoformat(),
    "expected_research_jobs": 30, "report_count": len(reports),
    "researcher_ids": sorted({r["role"] for r in reports}),
    "AI_review_completed": sum(r.get("ai_analysis", {}).get("status") == "llm_completed" for r in reports),
    "source_errors_count": sum(len(r.get("source_errors", [])) for r in reports),
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
    f"Small-model AI reviews completed: **{out['AI_review_completed']}**",
    f"Source errors: **{out['source_errors_count']}**",
    f"Strictly screened candidate leads: **{len(qualified)}**",
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
