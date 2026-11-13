"""450 independent lightweight research workers, 15 per 30 supervisors.

Uses public read-only search, no LLM per child, account credentials or wallet actions.
Each worker writes distinct evidence-linked JSON; parent AI reviews the team.
"""
import concurrent.futures
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("crypto-agents")
manifest = json.loads((ROOT / "branch_manifest.json").read_text(encoding="utf-8"))
brief = json.loads((ROOT / "branch_brief.json").read_text(encoding="utf-8"))
boss = os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv) > 1 else "")
branch = next((b for b in manifest["branches"] if b["boss_id"] == boss), None)
if not branch or len(branch.get("agents", [])) != 15:
    raise SystemExit("Unknown branch manager or invalid number of research workers: " + str(boss))
if "professional_profile" in brief or "location" in brief:
    raise SystemExit("Unexpected personal data in branch worker briefing")
outdir = Path("branch-reports")
outdir.mkdir(exist_ok=True)
PAID = re.compile(r"(?i)\b(?:paid|paying|hire|hiring|freelanc\w*|bounty|reward|contract|remote job|need a bookkeeper)\b")
RISKS = re.compile(r"(?i)\b(?:airdrop|giveaway|pay first|seed phrase|private key|connect your wallet|presale|guaranteed profit)\b")
MONEY = re.compile(r"(?i)(?:\$\s*|USD\s*|USDC\s*|USDT\s*)[0-9]")
cutoff = datetime.now(timezone.utc) - timedelta(days=60)
headers = {"User-Agent": "OwnerAuthorizedPublicResearch/1.0",
           "Accept": "application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

def parse_date(text):
    try:
        obj = datetime.fromisoformat(str(text).replace("Z","+00:00"))
        return obj.replace(tzinfo=timezone.utc) if obj.tzinfo is None else obj
    except (ValueError, TypeError):
        return None

def fetch(url, authenticated=False):
    request = urllib.request.Request(url, headers=headers if authenticated else
        {"User-Agent": "OwnerAuthorizedPublicResearch/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as res:
        return json.loads(res.read(500000))

def work(agent):
    result = {
        "subagent_id": agent["id"], "branch_manager": boss, "branch_id": branch["branch_id"],
        "mission": agent["specialty"], "query": agent["query"], "source": agent["source"],
        "brief_version": brief["version"], "brief_scope": "payment routes and research instructions only; no owner personal details",
        "approved_payment_route_ids": list(brief["public_payment_routes"].keys()),
        "status": "research_attempted", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "leads": [], "source_error": None, "received_payments_verified": [],
        "warning": "Search hits and advertised amounts are not work contracts, verified payouts or earnings."
    }
    # No query contains the owner's name, location, email, identity or wallets.
    if any(addr["address"].lower() in agent["query"].lower() for addr in brief["public_payment_routes"].values()):
        raise ValueError("Wallet address must not be included in public search terms")
    try:
        if agent["source"] == "github":
            query = agent["query"] + " is:issue is:open"
            url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
                {"q": query, "per_page": 10, "sort": "updated"})
            data = fetch(url, True)
            records = [
                {"title": x.get("title", ""), "url": x.get("html_url", ""),
                 "excerpt": (x.get("body") or "")[:400], "updated": x.get("updated_at", ""),
                 "source": "GitHub public issue"}
                for x in data.get("items", []) if not x.get("pull_request")]
        else:
            url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
                {"query": agent["query"], "tags": "story", "hitsPerPage": 12})
            data = fetch(url)
            records = [
                {"title": x.get("title", ""), "url": x.get("url") or
                 ("https://news.ycombinator.com/item?id=" + str(x.get("objectID",""))),
                 "excerpt": (x.get("story_text") or "")[:400], "updated": x.get("created_at", ""),
                 "source": "Hacker News public story"}
                for x in data.get("hits", [])]
        candidates = []
        for row in records:
            link = str(row.get("url") or "")
            if not link.startswith("https://"):
                continue
            published = parse_date(row.get("updated"))
            if not published or published < cutoff:
                continue
            body = str(row["title"]) + " " + str(row["excerpt"])
            if RISKS.search(body):
                continue
            evidence = {
                "has_paid_work_keyword": bool(PAID.search(body)),
                "contains_numeric_compensation_claim": bool(MONEY.search(body)),
                "source_date_known": True
            }
            confidence = int(evidence["has_paid_work_keyword"]) + int(evidence["contains_numeric_compensation_claim"])
            if confidence == 0:
                continue
            candidates.append({
                "title": str(row["title"])[:160], "url": link, "source": row["source"],
                "observed_update": row["updated"], "description_excerpt": str(row["excerpt"])[:240],
                "signals": evidence, "status": "unverified_research_lead",
                "eligibility_verified": False, "payer_verified": False, "payment_verified": False,
                "next_step": "Read original scope; verify payer, terms, country eligibility, payout route and no fees."
            })
        candidates.sort(key=lambda x: (x["signals"]["contains_numeric_compensation_claim"],
                                        x["observed_update"]), reverse=True)
        result["leads"] = candidates[:3]
        result["status"] = "completed"
    except Exception as exc:
        result["status"] = "source_unavailable"
        result["source_error"] = str(exc)[:180]
    target = outdir / (agent["id"] + ".json")
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(work, branch["agents"]))
if len(results) != 15:
    raise SystemExit("Supervisor's 15 subagent reports incomplete")
summary = {
    "branch_manager": boss, "branch_id": branch["branch_id"],
    "subagent_count": len(results),
    "subagent_ids": [r["subagent_id"] for r in results],
    "completed": sum(r["status"] == "completed" for r in results),
    "source_unavailable": sum(r["status"] == "source_unavailable" for r in results),
    "unverified_lead_count": sum(len(r["leads"]) for r in results),
    "sample_unverified_leads": [dict(lead, discovered_by=r["subagent_id"])
        for r in results for lead in r["leads"]][:6],
    "manager_action": "Inspect fifteen independent reports, challenge unsupported leads, and recommend legitimate payable work.",
    "public_payment_route_file": "crypto-agents/branch_brief.json",
    "privacy": "Branch instructions include only public payment addresses and research mission; no personal data",
    "income_verified": False,
    "recorded_at_utc": datetime.now(timezone.utc).isoformat()
}
(outdir / (boss + "-SUMMARY.json")).write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("BRANCH", boss, "subagents", len(results), "searched", summary["completed"],
      "unavailable", summary["source_unavailable"], "unverified leads", summary["unverified_lead_count"])
