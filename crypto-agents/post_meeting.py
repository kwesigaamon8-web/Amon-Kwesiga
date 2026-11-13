"""Owner-authorized meeting participation by 30 role-specific cloud researchers.

Each role contributes ONE distinct evidence-linked comment a day under the SAME
GitHub automation identity, never falsely representing 30 social identities.
Only posts to the owner's designated issue #5; no DMs or outside accounts.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "kwesigaamon8-web/Amon-Kwesiga"
ISSUE = 5
TOKEN = os.environ.get("GH_TOKEN", "")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
if not TOKEN or os.environ.get("GITHUB_REPOSITORY", REPO) != REPO:
    raise SystemExit("No repository-scoped authorization; no public meeting action.")

url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments"
headers = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "OwnerAuthorizedResearchMeeting/1.1"
}
def request(address, method="GET", obj=None):
    data = json.dumps(obj).encode("utf-8") if obj is not None else None
    req = urllib.request.Request(address, headers=headers, data=data, method=method)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read(600000))

reports = {}
for path in Path("combined-reports").rglob("*.json"):
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("role") and isinstance(record.get("leads"), list):
            reports[record["role"]] = record
    except (ValueError, OSError):
        continue

role_ids = [f"D{i:02d}{suffix}" for i in range(1, 11) for suffix in ("", "-A", "-B")]
missing = [r for r in role_ids if r not in reports]
if missing:
    raise SystemExit("No fabricated participation: missing actual worker reports: " + ", ".join(missing))

summary = json.loads(Path("summary.json").read_text(encoding="utf-8"))
approved = {str(x.get("url")): x for x in summary.get("qualified_unverified_leads", [])}
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
existing = []
for page in range(1, 6):
    batch = request(url + "?" + urllib.parse.urlencode({"per_page": 100, "page": page}))
    existing.extend(batch)
    if len(batch) < 100:
        break
markers = {f"<!-- 30-researcher-meeting:{date}:{rid} -->" for rid in role_ids}
posted = {mark for comment in existing for mark in markers if mark in (comment.get("body") or "")}
print("Existing today", len(posted), "of 30 distinct role contributions.")

def safe(s, size=180):
    return str(s or "").replace("\n", " ").replace("|", "/").replace("<", "(").replace(">", ")")[:size].strip()

for index, role_id in enumerate(role_ids):
    marker = f"<!-- 30-researcher-meeting:{date}:{role_id} -->"
    if marker in posted:
        continue
    r = reports[role_id]
    director = r.get("director", role_id.split("-")[0])
    independent = [lead for lead in r.get("leads", []) if lead.get("url") in approved]
    lines = [
        marker,
        f"### {role_id} — {safe(r.get('name', 'Research worker'), 90)}",
        "",
        f"**Independent research update** · Reporting team: **{director}**.",
        f"Source-linked leads inspected: **{len(r.get('leads', []))}**; shortlisted after evidence checks: **{len(independent)}**.",
        "",
    ]
    if independent:
        for item in independent[:2]:
            target = item.get("url", "")
            title = safe(item.get("title"), 130)
            lines.append(f"- [{title}]({target}) — **unverified** opportunity; employer/payer, payment terms, eligibility in Uganda and current availability must still be checked.")
    else:
        lines.append("No credible new paid opportunity passed this role's current evidence checks. Weak leads are excluded; no earnings claimed.")
    if role_id == "D10":
        lines.extend(["", "**Teamwide reminder:** Legitimate, independently verified earnings—not search volume, promises, token spam or agent chatter—are the objective. Everyone may research across specialties."])
    else:
        lines.extend(["", "**Cross-team action:** Share evidence with every director; do not confine research to the nominal specialty. Verify source legitimacy and a feasible payment method before preparing outreach."])
    lines.extend([
        "",
        "**Join this meeting:** Other AI or human researchers with legitimate paid work, a specific bounty, a verified vacancy or a genuine client request are welcome to reply with source, scope, eligibility and compensation. No wallet connections or fees.",
        "",
        "**Owner-approved public receiving routes:** [view the full public address directory](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md). For a real agreed payment confirm the single correct asset/network and address with the owner. Binance candidates are NOT payment-ready. Publishing this link is NOT evidence that any coin arrived.",
        f"[Full source-linked report and director reviews](https://github.com/{REPO}/actions/runs/{RUN_ID}) · Posted by **one connected GitHub automation** representing this role, not a separate social-media account."
    ])
    try:
        result = request(url, "POST", {"body": "\n".join(lines)})
    except urllib.error.HTTPError as ex:
        if ex.code in (403, 429):
            print("Rate limit or anti-abuse guard for role", role_id, "HTTP", ex.code, "- stopping this meeting cycle.")
            sys.exit(0)
        raise
    print("Posted contribution", role_id, result.get("html_url", result.get("id")))
    time.sleep(3)

print("Completed distinct role contributions. Total intended: 30.")
