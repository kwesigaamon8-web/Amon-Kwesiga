"""ORD-022: bounded read-only discovery of tools/sites to improve crypto-paid-work research.

This discovers public metadata only. It never installs software, opens accounts,
submits applications, authorizes external actions or claims a discovered tool is
connected. Each actually scheduled main AI role produces one independent report.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = Path("crypto-agents")
CATALOG = json.loads((ROOT / "tool_ecosystem.json").read_text(encoding="utf-8"))
ROLE = os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv) > 1 else "D01")
if not re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB])?", ROLE):
    raise SystemExit("Tool scouting may run only in a known 30-role GitHub job")

QUERIES = [
    ("open source paid bounty tools", "agent"),
    ("remote job search open source", "search"),
    ("open source finance automation", "finance"),
    ("AI model evaluation research", "evaluation"),
    ("public research automation", "research"),
    ("open source accounting tools", "accounting"),
    ("AI agent tools search automation", "automation"),
    ("open source issue bounty", "bounty"),
    ("spreadsheet financial tools", "spreadsheet"),
    ("open source data quality", "data")
]
index = sum(ord(char) for char in ROLE) % len(QUERIES)
github_term, hf_term = QUERIES[index]
errors = []
candidates = []
checks = []

def public_json(url, host):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != host:
        raise ValueError("Only preapproved exact-host read-only HTTPS endpoints")
    headers = {"User-Agent": "ResearchImprovementORD022/1.0", "Accept": "application/json"}
    if host == "api.github.com":
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read(750000))

# Official GitHub public repository search: tool/project metadata, NOT code execution.
url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
    {"q": github_term + " in:name,description", "sort": "updated", "order": "desc", "per_page": 6}
)
try:
    data = public_json(url, "api.github.com")
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError("Unexpected GitHub repository-search response")
    checks.append({"provider": "GitHub repository search", "status": "public_listing_retrieved",
                   "items": len(data.get("items", []))})
    for row in data.get("items", []):
        link = str(row.get("html_url", ""))
        if not link.startswith("https://github.com/"):
            continue
        candidates.append({
            "name": str(row.get("full_name", ""))[:100],
            "source": "GitHub official repository search",
            "url": link,
            "description": str(row.get("description") or "")[:220],
            "potential_improvement": "Evaluate open-source tooling, source verification, automation or discovery",
            "access": "public metadata read only; installation/authentication not performed",
            "independently_verified_use": False,
            "status": "discovered_not_installed_or_vetted"
        })
except Exception as exc:
    errors.append({"provider": "GitHub repository search", "error": str(exc)[:160]})
    checks.append({"provider": "GitHub repository search", "status": "unavailable"})

# Hugging Face public Spaces catalog: discover publicly described demos and tools.
url = "https://huggingface.co/api/spaces?" + urllib.parse.urlencode(
    {"search": hf_term, "limit": 6}
)
try:
    data = public_json(url, "huggingface.co")
    if not isinstance(data, list):
        raise ValueError("Unexpected Hugging Face public spaces response")
    checks.append({"provider": "Hugging Face Spaces catalog", "status": "public_listing_retrieved",
                   "items": len(data)})
    for row in data:
        full_id = str(row.get("id", ""))
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", full_id):
            continue
        candidates.append({
            "name": full_id,
            "source": "Hugging Face public Spaces metadata",
            "url": "https://huggingface.co/spaces/" + full_id,
            "description": "Public Space listing; inspect official model card and terms before considering use",
            "potential_improvement": "Evaluate publicly available AI tools and workflows",
            "access": "public metadata read only; demo not run, account not created",
            "independently_verified_use": False,
            "status": "discovered_not_installed_or_vetted"
        })
except Exception as exc:
    errors.append({"provider": "Hugging Face Spaces catalog", "error": str(exc)[:160]})
    checks.append({"provider": "Hugging Face Spaces catalog", "status": "unavailable"})

out = {
    "standing_order": "ORD-022",
    "role_id": ROLE,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "sources_checked": checks,
    "source_errors": errors,
    "new_tool_candidates": candidates[:12],
    "tested_endpoint_count": sum(item["status"] == "public_listing_retrieved" for item in checks),
    "candidate_count": len(candidates),
    "recommendation_policy": "Check license, benefits, current status, country eligibility, safety, payment and required permissions. Recommend useful tools; never auto-install remote code or grant access.",
    "tool_usage_verified": "Only public listing endpoints successfully retrieved where status says so; no candidate tool integrated or installed.",
    "authenticated_new_sites_connected": False,
    "paid_work_obtained": False,
    "crypto_receipts_verified": [],
    "one_parent": "OWNER" if re.fullmatch(r"D(?:0[1-9]|10)", ROLE) else ROLE[:3],
}
target = Path("tool-reports")
target.mkdir(exist_ok=True)
(target / (ROLE + ".json")).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print("ORD_022_TOOL_DISCOVERY", ROLE, "sources", out["tested_endpoint_count"],
      "candidates", out["candidate_count"], "errors", len(errors))
