"""Publish only actual model-run evidence from the bounded B/D worker pool.

Does not claim Moltbook account authentication, external posts, or receipt verification.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "kwesigaamon8-web/Amon-Kwesiga"
workforce = os.environ.get("WORKFORCE_ID", "")
repo = os.environ.get("GITHUB_REPOSITORY", "")
token = os.environ.get("GH_TOKEN", "")
run_id = os.environ.get("GITHUB_RUN_ID", "")
if repo != REPO or workforce not in ("transferexperiment", "BountyScoutAI") or not token:
    raise SystemExit("Missing authorized GitHub identity or workflow namespace")

audit_path = Path("ai-process-summary.json")
if not audit_path.exists():
    print("No actual worker audit file: no results claimed")
    raise SystemExit(0)
audit = json.loads(audit_path.read_text(encoding="utf-8"))
report_path = Path("owner-B-reports/EVERY_ACTUAL_AGENT.json")
report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
marker = "<!-- deployed-worker-models:" + workforce + ":" + day + " -->"
url = "https://api.github.com/repos/" + REPO + "/issues/9/comments"
headers = {"Authorization": "Bearer " + token,
           "Accept": "application/vnd.github+json",
           "User-Agent": "IndependentWorkerEvidencePublisher/1.0"}

def call(address, method="GET", obj=None):
    raw = json.dumps(obj).encode("utf-8") if obj is not None else None
    request = urllib.request.Request(address, data=raw, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

for page in range(1, 4):
    comments = call(url + "?" + urllib.parse.urlencode({"per_page": 100, "page": page}))
    if any(marker in (c.get("body") or "") for c in comments):
        print("This workforce already shared model-run evidence today")
        raise SystemExit(0)
    if len(comments) < 100:
        break

attempts = int(audit.get("actual_os_processes_invoked", 0))
completed = int(audit.get("actual_independent_model_completions", 0))
examples = []
for item in report.get("individual_actual_agent_reports", []):
    if not item.get("real_model_output_evidenced"):
        continue
    for source in item.get("public_source_urls", []):
        if source.startswith("https://") and source not in examples:
            examples.append(source)
        if len(examples) >= 3:
            break
    if len(examples) >= 3:
        break

lines = [
    marker,
    "## " + workforce + " — ACTUAL bounded AI processes, " + day,
    "",
    "- **Actual separately invoked OS worker processes:** " + str(attempts),
    "- **Independent open-weight model outputs completed:** " + str(completed),
    "- **Failed or incomplete attempts:** " + str(max(0, attempts-completed)),
    "- **Director reports received:** " + str(audit.get("director_manifests_present", 0)) + "/10",
    "- **First-tier job assignments defined (not independently running):** " + str(audit.get("work_assignments_recorded", 0)),
    "- **Actual Moltbook messages sent by this workflow:** none",
    "- **Confirmed cryptocurrency deposits assessed:** none. This is not a wallet scanner.",
    "",
    "**Original public-source research links (unverified as paying assignments):**",
]
lines += ["- " + x for x in examples] if examples else ["- No original public-source links were captured in this owner report."]
lines += [
    "",
    "**Director D enforcement:** Examine leads and community rules; use a valid authenticated Moltbook connection before any public request; distinguish drafts, sent messages, negotiated work, and on-chain receipts. Never claim donations from the existence of wallet addresses.",
    "Actual worker artifacts and independently reviewable run: https://github.com/" + REPO + "/actions/runs/" + run_id,
]
posted = call(url, "POST", {"body": "\n".join(lines)})
print("Real worker evidence comment:", posted.get("html_url", "unknown"))
