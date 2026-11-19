"""Ten independently scheduled, read-only paying-work scouts (B1/B2).
Each GitHub Actions matrix job is a distinct OS process, not a persistent AI model.
Evidence is recorded even when the search source fails; no payment claims, emails,
outreach, wallet interactions, commitments, or external posting are performed.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

AGENTS = {
    "B1-01": ("BTC-funded coding tasks", "bitcoin bounty is:issue is:open"),
    "B1-02": ("Python paid bug fixes", "python paid bounty is:issue is:open"),
    "B1-03": ("CSV and data reconciliation", "csv bounty is:issue is:open"),
    "B1-04": ("Open-source technical writing", "documentation bounty is:issue is:open"),
    "B1-05": ("Accounting automation", "accounting bounty is:issue is:open"),
    "B2-01": ("USDC-funded development", "usdc bounty is:issue is:open"),
    "B2-02": ("Software quality assurance", "testing paid bounty is:issue is:open"),
    "B2-03": ("Data cleanup tasks", "data cleanup bounty is:issue is:open"),
    "B2-04": ("AI evaluation tasks", "ai evaluation bounty is:issue is:open"),
    "B2-05": ("Developer tooling tasks", "automation bounty is:issue is:open"),
}
REWARD = re.compile(r"\b(bounty|reward|paid|payment|funded|compensation|usdc|btc)\b", re.I)
DANGER = re.compile(r"(send (?:us|me) (?:a )?(?:deposit|fee)|seed phrase|private key|"
                    r"pay (?:a |the )?(?:fee|deposit) first|connect your wallet to claim|"
                    r"guaranteed (?:profit|income))", re.I)
OUT = Path("ten-agent-reports")
CUTOFF_DAYS = 120


def now():
    return datetime.now(timezone.utc)


def parse_date(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def request_json(url):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "B1B2-ten-agent-evidence-scout/1.0",
               "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=16) as response:
        return json.loads(response.read(600000))


def classify(issue, at=None):
    at = at or now()
    title = str(issue.get("title") or "")[:180]
    body = str(issue.get("body") or "")[:2500]
    link = str(issue.get("html_url") or "")
    date = parse_date(issue.get("updated_at"))
    if issue.get("state") != "open" or issue.get("pull_request"):
        return None
    if not link.startswith("https://github.com/") or not date:
        return None
    if date < at - timedelta(days=CUTOFF_DAYS):
        return None
    content = title + "\n" + body
    if not REWARD.search(content) or DANGER.search(content):
        return None
    if not issue.get("number") or not issue.get("repository_url"):
        return None
    return {
        "issue_id": issue.get("id"),
        "title": title,
        "source_url": link,
        "updated_at": issue.get("updated_at"),
        "evidence_snippet": body[:360],
        "payment_language_present": bool(REWARD.search(content)),
        "payer_verified": False,
        "payout_amount_verified": False,
        "uganda_eligibility_verified": False,
        "crypto_network_verified": False,
        "funds_escrowed_verified": False,
        "source_status": "search_hit_only",
        "next_step": "Check payer, exact deliverable, funding, eligibility, conditions and payout network before any work or outreach",
    }


def run_agent(agent):
    if agent not in AGENTS:
        raise ValueError("Unknown agent")
    mission, query = AGENTS[agent]
    report = {
        "agent_id": agent,
        "company": "B1" if agent.startswith("B1") else "B2",
        "parent": "Chief D via company director board",
        "mission": mission,
        "query": query,
        "started_utc": now().isoformat(),
        "execution_type": "independent GitHub Actions Python process",
        "ai_model_invoked": False,
        "search_completed": False,
        "original_source_rechecked": 0,
        "unverified_opportunities": [],
        "verified_paid_jobs": 0,
        "verified_deposits": [],
        "external_messages_sent": 0,
        "email_accessed": False,
        "wallet_operations": 0,
        "source_error": None,
    }
    try:
        url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
            {"q": query, "per_page": 12, "sort": "updated", "order": "desc"})
        data = request_json(url)
        report["search_completed"] = True
        candidates = [c for item in data.get("items", []) if (c := classify(item))]
        # Validate at most two live issue records, preventing a search-result-only claim.
        for candidate in candidates[:2]:
            item = next((i for i in data.get("items", [])
                         if i.get("id") == candidate["issue_id"]), None)
            if not item:
                continue
            try:
                fresh = request_json(item["repository_url"] + "/issues/" + str(item["number"]))
                report["original_source_rechecked"] += 1
                if fresh.get("id") == candidate["issue_id"] and classify(fresh):
                    candidate["source_status"] = "original_github_issue_rechecked_open"
                else:
                    candidate["source_status"] = "original_issue_not_confirmed"
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError) as exc:
                candidate["source_status"] = "direct_check_failed"
                candidate["source_error"] = type(exc).__name__
            report["unverified_opportunities"].append(candidate)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError) as exc:
        report["source_error"] = type(exc).__name__ + (":" + str(exc.code) if isinstance(exc, urllib.error.HTTPError) else "")
    report["ended_utc"] = now().isoformat()
    report["status"] = "SOURCE_CHECKED" if report["search_completed"] else "SOURCE_UNAVAILABLE"
    OUT.mkdir(parents=True, exist_ok=True)
    file = OUT / (agent + ".json")
    file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"agent": agent, "status": report["status"],
                      "direct_source_rechecks": report["original_source_rechecked"],
                      "leads": len(report["unverified_opportunities"]),
                      "file": str(file)}))
    return 0 if report["search_completed"] else 2


def audit(folder):
    reports = []
    problems = []
    for agent in AGENTS:
        file = folder / (agent + ".json")
        if not file.is_file():
            problems.append("missing:" + agent)
            continue
        try:
            report = json.loads(file.read_text(encoding="utf-8"))
            if report.get("agent_id") != agent:
                problems.append("wrong_identity:" + agent)
            if report.get("verified_paid_jobs") != 0 or report.get("verified_deposits") != []:
                problems.append("unsupported_payment_claim:" + agent)
            if report.get("external_messages_sent") or report.get("email_accessed") or report.get("wallet_operations"):
                problems.append("unauthorized_action:" + agent)
            reports.append(report)
        except (OSError, ValueError):
            problems.append("invalid_report:" + agent)
    complete = sum(bool(r.get("search_completed")) for r in reports)
    checked = sum(r.get("original_source_rechecked", 0) for r in reports)
    results = {
        "defined_agent_roles": len(AGENTS),
        "distinct_reported_processes": len(reports),
        "successful_source_searches": complete,
        "direct_issue_rechecks": checked,
        "ai_models_executed": 0,
        "real_crypto_receipts_verified": 0,
        "worker_outreach_confirmed": 0,
        "missing_or_invalid": problems,
        "status": "PASS" if not problems else "FAIL",
        "note": "10 distinct finite automated scouts; not 10 continuously running LLM agents or confirmed paid workers",
        "audited_utc": now().isoformat(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "AUDIT.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results))
    return 0 if not problems else 1


def self_test():
    current = now().isoformat()
    issue = {"id": 9, "number": 4, "state": "open", "title": "Paid Python bounty",
             "body": "Bounty funded after confirmed acceptance, $50", "updated_at": current,
             "html_url": "https://github.com/example/repo/issues/4",
             "repository_url": "https://api.github.com/repos/example/repo"}
    assert classify(issue)["payer_verified"] is False
    assert classify({**issue, "state": "closed"}) is None
    assert classify({**issue, "body": "Send us a deposit first"}) is None
    assert classify({**issue, "html_url": "http://unknown.invalid"}) is None
    assert len(AGENTS) == 10 and len(set(AGENTS)) == 10
    print("PASS: 5 offline worker integrity checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=list(AGENTS))
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.audit is not None:
        sys.exit(audit(args.audit))
    elif args.agent:
        sys.exit(run_agent(args.agent))
    else:
        parser.error("Choose --agent, --audit or --self-test")
