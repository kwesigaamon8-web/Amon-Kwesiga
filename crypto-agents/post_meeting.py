"""Post one daily public meeting digest of 30 independently generated reports.

Posts only inside the repository owner's explicit meeting issue (#5).
Never posts in third-party threads or advertises arbitrary wallets.
Uses the short-lived GitHub Actions token with issues:write.
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ISSUE = 5
REPO = os.environ.get("GITHUB_REPOSITORY", "kwesigaamon8-web/Amon-Kwesiga")
TOKEN = os.environ.get("GH_TOKEN")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
if not TOKEN or REPO != "kwesigaamon8-web/Amon-Kwesiga":
    raise SystemExit("Meeting publisher: no authorized GitHub token/repository; no public action")

base = "https://api.github.com/repos/" + REPO + "/issues/" + str(ISSUE)
head = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "OwnerAuthorizedResearchMeeting/1.0"
}
def call(url, method="GET", payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, headers=head, method=method, data=data)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read(400000))

reports = {}
for path in Path("combined-reports").rglob("*.json"):
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
        role = r.get("role")
        if role and isinstance(r.get("leads"), list):
            reports[role] = r
    except (ValueError, OSError):
        continue
if len(reports) < 25:
    raise SystemExit("Insufficient independent role reports to hold a credible meeting: " + str(len(reports)))

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker = "<!-- owner-research-meeting:" + today + " -->"
# A daily digest is enough to hold an accountable public meeting without
# producing 30 spam comments on every hourly scan.
for page in range(1, 6):
    existing = call(base + "/comments?" + urllib.parse.urlencode({"per_page": 100, "page": page}))
    if any(marker in c.get("body", "") for c in existing):
        print("A daily public research meeting digest has already been posted; no duplicate")
        sys.exit(0)
    if len(existing) < 100:
        break

summary = json.loads(Path("summary.json").read_text(encoding="utf-8"))
qualified = {str(x.get("url", "")): x for x in summary.get("qualified_unverified_leads", [])}
lines = [
    marker,
    "## 30-worker independent research meeting · " + today,
    "",
    "**10 directors + 20 assistants.** Each worker researched independently; all can follow legitimate opportunities across disciplines.",
    "Participants: please bring verified job specifications, bounty terms, Uganda eligibility, source links, and payout methods. Other AI agents and people are invited to contribute here.",
    "",
    "| Agent report | Director team | Screened opportunity (not verified payment) |",
    "|---|---|---|"
]
for i in range(1, 11):
    director = "D" + str(i).zfill(2)
    for role_id in (director, director + "-A", director + "-B"):
        r = reports.get(role_id)
        if not r:
            lines.append("| " + role_id + " | " + director + " | Missing report |")
            continue
        useful = None
        for x in r.get("leads", []):
            if x.get("url") in qualified:
                useful = x
                break
        if useful:
            title = useful.get("title", "")[:85].replace("|", "-").replace("[", "(").replace("]", ")").replace("\n", " ")
            link = useful.get("url", "")
            detail = "[" + title + "](" + link + ") — unverified; check payer, eligibility and scope"
        else:
            detail = "No independently screened paid opportunity this cycle"
        lines.append("| " + role_id + " | " + director + " | " + detail + " |")
lines += [
    "",
    "**Mission reminder from Director D10:** Only legitimately earned, independently verified transferable payment counts as income; research, social replies, leads, claimed token drops and promises are not receipts.",
    "",
    "The owner has shared payment instructions in this issue's opening post. They are not a request for donations or a claim of earnings. Verify chain, token and owner approval before any actual payer sends funds.",
    "",
    "Full role-specific reports and director reviews: [this cloud research run](https://github.com/" + REPO + "/actions/runs/" + RUN_ID + ") (Artifacts).",
    "Public meeting responses should be substantive and non-spammy. Research jobs here do not autonomously sign deals, conduct social messaging or move funds."
]
body = "\n".join(lines)
result = call(base + "/comments", "POST", {"body": body})
print("Published owner-authorized meeting digest comment", result.get("html_url", "id=" + str(result.get("id"))), "roles", len(reports))
