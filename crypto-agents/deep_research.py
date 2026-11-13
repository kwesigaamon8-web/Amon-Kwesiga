"""Evidence-first, bounded, read-only due diligence for research leads.

Rechecks GitHub issue claims against GitHub's official REST API. Everything
not independently established remains explicitly unverified. Never signs,
posts, applies, or retrieves private data. Deliberately no arbitrary URL fetch.
"""
from datetime import datetime, timezone
from urllib.parse import urlparse
import json
import os
import re
import urllib.request

ISSUE_PATH = re.compile(r"^/([^/]+)/([^/]+)/issues/([0-9]+)$")
AMOUNT = re.compile(r"(?i)(?:\b(?:USD|USDC|USDT)\s*|\$\s*)([0-9][0-9,]*(?:\.[0-9]+)?)|\b([0-9]+(?:\.[0-9]+)?)\s*(?:BTC|USDC|USDT)\b")
WORK = re.compile(r"(?i)\b(hiring|hire|paid|bounty|contract|freelanc\w*|paying|looking for|need a bookkeeper|remote job|reward)\b")
RISKS = {
    "advance_fee": r"(?i)\b(upfront fee|registration fee|application fee|pay first|deposit to join|gas fee to claim)\b",
    "wallet_connection": r"(?i)\b(connect your wallet|seed phrase|private key|sign transaction)\b",
    "speculative_token": r"(?i)\b(airdrop|mint now|100x|guaranteed returns|presale)\b",
}
SKILLS = re.compile(r"(?i)\b(bookkeep\w*|accountan\w*|quickbooks|reconcil\w*|payroll|management accounts|excel|VAT|tax filing|audit support|EFRIS|finance)\b")

def _iso(s):
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None

def _official_github_issue(url, token):
    p = urlparse(url)
    if p.scheme != "https" or p.netloc.lower() != "github.com":
        return None, "not_a_github_issue"
    m = ISSUE_PATH.fullmatch(p.path.rstrip("/"))
    if not m:
        return None, "not_a_github_issue"
    owner, repo, number = m.groups()
    address = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "ResearchDueDiligence/1.0"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        req = urllib.request.Request(address, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            record = json.loads(resp.read(450000))
        if record.get("pull_request"):
            return None, "github_pull_request_not_bounty_listing"
        if record.get("html_url","").rstrip("/") != url.rstrip("/"):
            return None, "github_source_url_mismatch"
        return record, None
    except Exception as exc:
        return None, "github_refetch_failed:" + str(exc)[:110]

def check_one(item, token=None):
    url = str(item.get("url") or "")
    text = str(item.get("title") or "") + " " + str(item.get("excerpt") or "")
    findings = []
    unknown = ["payer's identity and ability to pay", "Uganda eligibility",
               "exact payment method and payout-network support", "contract terms",
               "whether the opportunity remains available"]
    issues = []
    date = _iso(item.get("updated"))
    days = (datetime.now(timezone.utc) - date).days if date else None
    if days is None:
        issues.append("no verifiable publication/update date")
    elif days > 30:
        issues.append(f"last observed update {days} days ago; may be stale")
    source_verified = False
    source_status = "source_snippet_only"
    original, error = _official_github_issue(url, token)
    if original is not None:
        source_verified = True
        source_status = "github_official_api_refetched"
        state = original.get("state","unknown")
        findings.append("GitHub issue exists and currently has state " + state)
        if state != "open":
            issues.append("issue no longer open")
        full = str(original.get("title") or "") + " " + str(original.get("body") or "")
        text = full[:8000]
        created = _iso(original.get("created_at"))
        if created:
            findings.append("Issue creation date: " + created.date().isoformat())
        labels = [str(x.get("name") or "") for x in original.get("labels",[]) if isinstance(x,dict)]
        if labels:
            findings.append("GitHub labels as claimed by issuer: " + ", ".join(labels[:7]))
        findings.append("Source text re-read from the issue, not only a search excerpt")
        # Mirrors may contain an external source of truth; source still not verified.
        if re.search(r"(?i)source of truth|mirrored board|this is a mirror", full):
            issues.append("mirror listing: independent original bounty board confirmation required")
    elif error and error != "not_a_github_issue":
        issues.append(error)
    amount = AMOUNT.search(text)
    if amount:
        findings.append("Source advertises a numeric payment, not independently confirmed")
        unknown.append("whether advertised payout is genuine and collectible")
    else:
        issues.append("no explicit monetary amount supported by examined source")
    if not WORK.search(text):
        issues.append("no clearly stated paid-work request in examined source")
    for name, pattern in RISKS.items():
        if re.search(pattern, text):
            issues.append("possible risk signal: " + name)
    skill_match = bool(SKILLS.search(text))
    if skill_match:
        findings.append("Text mentions a skill potentially relevant to owner's accounting experience")
    # Scores prioritize investigation; they do not assert a validated employer.
    score = 10
    if source_verified: score += 20
    if amount: score += 20
    if WORK.search(text): score += 15
    if skill_match: score += 20
    if days is not None and days <= 7: score += 10
    if days is not None and days > 30: score -= 10
    if issues: score -= min(35, 8 * len(issues))
    score = max(0, min(100, score))
    if any("advance_fee" in problem or "wallet_connection" in problem for problem in issues):
        outcome = "avoid_until_risk_resolved"
    elif source_verified and original.get("state") != "open":
        outcome = "reject_closed"
    elif score >= 50:
        outcome = "investigate_original_terms"
    else:
        outcome = "weak_or_unverified"
    return {
        "title": str(item.get("title") or "")[:160],
        "source": item.get("source"),
        "url": url,
        "source_status": source_status,
        "source_refetched": source_verified,
        "score_for_followup_not_payment_probability": score,
        "outcome": outcome,
        "supporting_evidence": findings,
        "counter_evidence_and_risks": issues,
        "unknowns": unknown,
        "next_action": ("Confirm current original payer and written work scope, agree deliverable, "
                        "verify Uganda eligibility and exact owner-approved payout network; "
                        "prepare a tailored application only if authenticated action is available."),
        "payment_received_verified": False
    }

def due_diligence(leads, max_items=5):
    token = os.getenv("GITHUB_TOKEN")
    checked = [check_one(item, token) for item in leads[:max_items]]
    checked.sort(key=lambda item:item["score_for_followup_not_payment_probability"], reverse=True)
    return {
        "protocol": "multiple-source discovery -> original-record check -> adversarial risk review -> concrete follow-up",
        "examined_count": len(checked),
        "dossiers": checked,
        "warning": "Scores prioritize research only. No employer, payer, location eligibility or payment is independently certified by these checks."
    }
