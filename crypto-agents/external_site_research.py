"""ORD-025: actually attempt one independent low-volume public external-site query per primary role.

Only fixed official HTTPS API endpoints; no logins, submissions, remote code execution,
payments or claims that listings are confirmed crypto-paying contracts.
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("crypto-agents")
CFG = json.loads((BASE / "external_sites.json").read_text(encoding="utf-8"))
ROLE = os.getenv("ROLE_ID") or (sys.argv[1] if len(sys.argv) > 1 else "")
if not re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB])?", ROLE):
    raise SystemExit("Unknown scheduled primary role")
now = datetime.now(timezone.utc)
# Three different sources are covered by the 30 job identities, and rotation
# changes the assignment each day without ever dispatching billions of requests.
site = CFG["sites"][(sum(ord(c) for c in ROLE) + now.toordinal()) % len(CFG["sites"])]
queries = ["bitcoin bounty", "crypto accounting", "AI evaluation", "bookkeeper",
           "finance analyst", "open source", "data annotation", "remote accountant",
           "project contract", "spreadsheet"]
query = queries[int(ROLE[1:3])-1]
headers = {"User-Agent": "OwnerPaidResearchORD025/1.0", "Accept": "application/json"}

def get(url, exact_host):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != exact_host:
        raise ValueError("Endpoint not in approved exact-host allowlist")
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.loads(response.read(750000))

def safe(text, n=250):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(text or ""))).strip()[:n]

results = []
status = "source_unavailable"
error = None
url = ""
try:
    if site["id"] == "himalayas":
        url = "https://himalayas.app/jobs/api/search?" + urllib.parse.urlencode({
            "q": query, "country": "Uganda", "sort": "recent", "page": 1
        })
        payload = get(url, "himalayas.app")
        rows = payload.get("jobs", payload.get("data", [])) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            raise ValueError("Unexpected Himalayas response structure")
        for x in rows[:12]:
            if not isinstance(x, dict): continue
            name = safe(x.get("title") or x.get("jobTitle"), 160)
            link = str(x.get("guid") or x.get("applicationLink") or "")
            if not name or not link.startswith("https://"): continue
            results.append({"title": name, "url": link, "source": "Himalayas jobs API",
                "excerpt": safe((x.get("companyName") or "") + " " + (x.get("description") or ""), 320),
                "updated": str(x.get("pubDate") or ""),
                "application_link": str(x.get("applicationLink") or "")[:300],
                "payment_verified": False, "eligibility_verified": False,
                "status": "public_job_listing_unverified_crypto_settlement"})
    elif site["id"] == "arbeitnow":
        url = "https://www.arbeitnow.com/api/job-board-api"
        payload = get(url, "www.arbeitnow.com")
        rows = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            raise ValueError("Unexpected Arbeitnow response structure")
        for x in rows[:40]:
            if not isinstance(x, dict): continue
            title = safe(x.get("title"), 160)
            link = str(x.get("url") or "")
            if not title or not link.startswith("https://"): continue
            term = (title + " " + str(x.get("description") or "")).lower()
            relevance = any(t in term for t in ("account", "finance", "bookkeep",
                "data", "remote", "contract", "analytics", "software", "quality", "assistant"))
            if not relevance or x.get("remote") is False: continue
            results.append({"title": title, "url": link, "source": "Arbeitnow jobs API",
                "excerpt": safe((x.get("company_name") or "") + " " + (x.get("description") or ""), 320),
                "updated": str(x.get("created_at") or ""), "payment_verified": False,
                "eligibility_verified": False, "status": "public_job_listing_unverified_crypto_settlement"})
    else:
        url = "https://superteam.fun/api/listings?take=20"
        payload = get(url, "superteam.fun")
        rows = payload if isinstance(payload, list) else (
            payload.get("listings", payload.get("data", [])) if isinstance(payload, dict) else [])
        if not isinstance(rows, list):
            raise ValueError("Unexpected Superteam listing response structure")
        for x in rows[:20]:
            if not isinstance(x, dict): continue
            title = safe(x.get("title"), 160)
            if not title: continue
            expiry = str(x.get("deadline") or "")
            if expiry:
                try:
                    exp = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                    if exp.tzinfo is not None and exp < now: continue
                except (ValueError, TypeError): pass
            slug = str(x.get("slug") or "")
            # Never invent an individual listing URL unless API returned it.
            link = str(x.get("url") or "https://superteam.fun/earn")
            if not link.startswith("https://"): link = "https://superteam.fun/earn"
            results.append({"title": title, "url": link, "source": "Superteam Earn public listings",
                "excerpt": safe("Token: " + str(x.get("token") or "not specified")
                    + "; advertised reward: " + str(x.get("rewardAmount") or "not specified")
                    + "; listing type: " + str(x.get("type") or "not specified"), 320),
                "updated": str(x.get("deadline") or ""), "payment_verified": False,
                "eligibility_verified": False, "source_slug": slug[:100],
                "status": "public_crypto_bounty_unverified_terms_and_network"})
    status = "public_source_checked"
except Exception as exc:
    error = str(exc)[:180]
    status = "source_unavailable"

data = {
  "role_id": ROLE, "date_utc": now.isoformat(), "site_id": site["id"],
  "source_name": site["name"], "official_site": site["official_url"],
  "api_endpoint_attempted": url, "source_check_status": status,
  "source_error": error, "unverified_leads": results[:6],
  "next_allowed_action": "Recheck original payer, scope, eligibility and crypto payment conditions. Prepare targeted draft or use an explicitly authorized authenticated connector, if one exists.",
  "received_coins_verified": [],
  "claims_actual_site_account": False, "claims_apps_sent": False,
  "limitations": "API lookup is not a paid contract, accepted application or cryptocurrency receipt. Some returned jobs may not offer crypto payout."
}
out = Path("site-reports")
out.mkdir(exist_ok=True)
(out / (ROLE + ".json")).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("OTHER_SITES", ROLE, site["id"], status, "leads", len(data["unverified_leads"]),
      "error", error or "none")
