"""Consent-first B1/B2 public collaborator lead watch. No unsolicited contact.

Counts only public opt-in inquiries; author identity, hardware authorization,
employment, fee eligibility and receipts are NEVER verified by this scanner.
No messages, emails, wallet actions, account creation, recruitment claims or
automatic acceptance. GitHub API GETs only; bounded pages and timeouts.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

OWNER = "kwesigaamon8-web"
REPO = "Amon-Kwesiga"
INVITATION_ISSUE = 32
REPORT = Path("collaborator-recruitment/evidence.json")
WINDOW_DAYS = 30
OPT_IN_TOKENS = (
    "i can ", "i would like", "i'd like", "i want to join", "i can help",
    "join the", "volunteer", "collaborate", "contribute", "interested in joining",
    "interested to join", "want to help", "i have an asic", "i operate an asic",
)


def utcparse(raw):
    try:
        value = dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if not value.tzinfo:
            raise ValueError("no UTC offset")
        return value.astimezone(dt.timezone.utc)
    except (ValueError, TypeError):
        return None


def eligible_author(obj):
    u = obj.get("user") or {}
    name = str(u.get("login") or "").strip()
    if not name or name.casefold() == OWNER.casefold() or name.endswith("[bot]"):
        return None
    if u.get("type") == "Bot":
        return None
    return name


def is_recent(obj, now):
    t = utcparse(obj.get("created_at"))
    return bool(t and now - dt.timedelta(days=WINDOW_DAYS) <= t <= now + dt.timedelta(minutes=5))


def classify_public_lead(obj, kind, now):
    user = eligible_author(obj)
    if not user or not is_recent(obj, now):
        return None
    text = str(obj.get("body") or "").casefold()
    if kind == "comment" and not any(w in text for w in OPT_IN_TOKENS):
        return None
    if kind == "issue" and not str(obj.get("title") or "").startswith("[Opt-in collaborator]"):
        return None
    url = str(obj.get("html_url") or "")
    if not url.startswith(f"https://github.com/{OWNER}/{REPO}/issues/"):
        return None
    # Never copy comment body, contact info or potentially sensitive free text.
    return {
        "public_source_url": url,
        "github_public_user": user,
        "source_kind": kind,
        "posted_utc": obj.get("created_at"),
        "status": "PUBLIC_INQUIRY_NOT_VERIFIED_OR_ACCEPTED",
        "eligible_for_paid_work": False,
        "hardware_control_or_mining_partnership_verified": False,
        "agreement_verified": False,
    }


def github_json(path, token="", timeout=12):
    if not path.startswith("/repos/kwesigaamon8-web/Amon-Kwesiga/"):
        raise ValueError("Only owner-controlled repository is allowed")
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "B1B2-Collaborator-OptIn-Scout/1",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": "Bearer " + token} if token else {})
        })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read(1200000))
    if not isinstance(data, list):
        raise ValueError("Expected GitHub list")
    return data


def scout(loader=github_json, now=None, max_pages=2):
    now = now or dt.datetime.now(dt.timezone.utc)
    token = os.environ.get("GH_TOKEN", "")
    candidates = []
    failures = []
    seen = set()
    scanned = {"open_issues": 0, "invitation_comments": 0}
    sources = [
        ("issue", "/repos/kwesigaamon8-web/Amon-Kwesiga/issues?state=open&sort=created&direction=desc&per_page=100"),
        ("comment", f"/repos/kwesigaamon8-web/Amon-Kwesiga/issues/{INVITATION_ISSUE}/comments?per_page=100"),
    ]
    for kind, base in sources:
        for page in range(1, max_pages + 1):
            try:
                suffix = "&page=" if "?" in base else "?page="
                items = loader(base + suffix + str(page), token)
                scanned["open_issues" if kind == "issue" else "invitation_comments"] += len(items)
            except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                failures.append({"kind": kind, "page": page, "error_type": type(exc).__name__})
                break
            for obj in items:
                if kind == "issue" and obj.get("pull_request"):
                    continue
                record = classify_public_lead(obj, kind, now)
                if record is None or record["public_source_url"] in seen:
                    continue
                seen.add(record["public_source_url"])
                candidates.append(record)
            if len(items) < 100:
                break
    # One public user appearing twice is ONE candidate, not two recruited people.
    by_person = {}
    for item in sorted(candidates, key=lambda x: x["posted_utc"], reverse=True):
        by_person.setdefault(item["github_public_user"].casefold(), item)
    rows = sorted(by_person.values(), key=lambda x: x["posted_utc"], reverse=True)
    checked = sum(scanned.values())
    status = "READ_ONLY_CHECKED" if not failures else ("PARTIAL_SOURCE_FAILURE" if checked else "SOURCE_UNAVAILABLE")
    return {
        "checked_at_utc": now.isoformat(),
        "status": status,
        "sources": scanned,
        "source_errors": failures,
        "possible_public_opt_in_users_not_verified": len(rows),
        "candidate_public_links": rows[:30],
        "confirmed_real_friends_or_contributors": 0,
        "verified_new_asic_mining_partners": 0,
        "accepted_paid_referrals": 0,
        "confirmed_new_btc_or_usdc_receipts": 0,
        "unverified_not_automatically_recruited": True,
        "external_messages_sent": 0,
        "email_accesses": 0,
        "wallet_signatures_or_payout_redirects": 0,
        "next_action": (
            "Review genuinely new opt-in public threads for a concrete original task. "
            "Agree contributor rights, terms and any mining payout splits separately. "
            "Never claim recruited miners or money from a form submission."
        )
    }


def self_test():
    now = dt.datetime(2026, 11, 20, 0, tzinfo=dt.timezone.utc)
    def issue(user, number, title, body="Test source link"):
        return {
            "user": {"login": user, "type": "User"}, "created_at": "2026-11-19T23:40:00Z",
            "title": title, "body": body,
            "html_url": f"https://github.com/{OWNER}/{REPO}/issues/{number}",
        }
    owner = issue(OWNER, 32, "[Opt-in collaborator] owner")
    first = issue("real-coder", 33, "[Opt-in collaborator] Python tests")
    duplicate = issue("real-coder", 34, "[Opt-in collaborator] another message")
    unrelated = issue("passerby", 35, "Unrelated issue")
    bot = issue("helper[bot]", 36, "[Opt-in collaborator] Fake bot")
    comment = issue("rig-operator", 32, "Re: Join", "I can help review your pool policy.")
    comment["html_url"] += "#issuecomment-100"
    nonsense = issue("crawler", 32, "Re: Join", "great site")
    nonsense["html_url"] += "#issuecomment-101"
    paths = {"issues?": [owner, first, duplicate, unrelated, bot],
             "/comments?": [comment, nonsense]}
    def loader(path, token):
        return next((v for part, v in paths.items() if part in path), [])
    result = scout(loader=loader, now=now)
    assert result["status"] == "READ_ONLY_CHECKED"
    assert result["possible_public_opt_in_users_not_verified"] == 2
    assert result["confirmed_real_friends_or_contributors"] == 0
    assert result["verified_new_asic_mining_partners"] == 0
    assert result["confirmed_new_btc_or_usdc_receipts"] == 0
    assert result["email_accesses"] == 0
    assert result["external_messages_sent"] == 0
    assert all("body" not in row for row in result["candidate_public_links"])
    failed = scout(loader=lambda path, token: (_ for _ in ()).throw(OSError("network")), now=now)
    assert failed["status"] == "SOURCE_UNAVAILABLE"
    assert failed["possible_public_opt_in_users_not_verified"] == 0 and failed["source_errors"]
    assert classify_public_lead(issue("outside", 5, "[Opt-in collaborator] hi") |
        {"html_url": "https://attacker.example/5"}, "issue", now) is None
    print("B1B2_GLOBAL_OPT_IN_RECRUITMENT_SELF_TEST_PASS")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        report = scout()
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B1B2_WORLDWIDE_OPT_IN_WATCH", json.dumps({
            "status": report["status"],
            "possible_public_optins_unverified": report["possible_public_opt_in_users_not_verified"],
            "github_issue_count_scanned": report["sources"]["open_issues"],
            "errors": report["source_errors"],
            "real_partnerships_verified": 0,
            "coins_received_verified": 0
        }))
