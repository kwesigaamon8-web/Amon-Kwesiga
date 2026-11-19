"""Strict, opt-in-only public welcome for the B1/B2 collaboration thread.

This script never looks up email or contacts people outside the owner's OWN
recruitment issue #32. It emits at most two fixed, non-binding replies per run,
only after an explicit first-person interest from a genuine non-bot user.
Replies are idempotent across scheduled runs using a source-thread marker.
Missing pages, API errors or ambiguous intent fail closed without posting.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

from opt_in_collaborator_watch import OWNER, REPO, INVITATION_ISSUE, eligible_author, utcparse

ISSUE = INVITATION_ISSUE
BASE = f"/repos/{OWNER}/{REPO}/issues/{ISSUE}/comments"
URL = "https://api.github.com"
MARKER_PREFIX = "b1b2-explicit-optin-welcome-v1"
MAX_REPLIES = 2
MAX_PAGES = 4
DATE_LIMIT_DAYS = 14
# Explicit expression of interest, NOT "I can" generally (e.g. "I can not").
SIGNALS = (
    "i want to join", "i would like to join", "i'd like to join",
    "i am interested in joining", "i'm interested in joining",
    "i volunteer", "i would like to contribute", "i'd like to contribute",
    "i can help with", "i want to contribute", "i want to collaborate",
    "i am willing to help", "i would like to collaborate",
)
OPTOUT = ("do not contact", "don't contact", "not interested", "not joining",
          "i changed my mind", "i cannot join", "i can not join", "unsubscribe")


def approved_comment(row, now):
    author = eligible_author(row)
    if not author or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", author):
        return None
    when = utcparse(row.get("created_at"))
    if not when or when < now - dt.timedelta(days=DATE_LIMIT_DAYS) or when > now + dt.timedelta(minutes=5):
        return None
    body = str(row.get("body") or "").casefold()
    if not any(signal in body for signal in SIGNALS):
        return None
    if any(optout in body for optout in OPTOUT):
        return None
    url = str(row.get("html_url") or "")
    if not re.fullmatch(
        rf"https://github\.com/{re.escape(OWNER)}/{re.escape(REPO)}/issues/{ISSUE}#issuecomment-\d+",
        url):
        return None
    return author


def marker(author):
    return "<!-- " + MARKER_PREFIX + ":" + author.casefold() + " -->"


def fixed_message(author):
    return (
        marker(author) + "\n"
        "Thank you for opting in to the B1/B2 public collaborator invitation. "
        "**This automatic welcome is not acceptance into a job, contract or mining partnership.**\n\n"
        "Choose one real, small first contribution:\n"
        "- [Reproducible CSV reconciliation test](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/33)\n"
        "- [Translation or accessibility improvement](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/34)\n"
        "- [Read our contributor rules](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/CONTRIBUTING.md)\n\n"
        "You may reply publicly with one **non-sensitive** idea or a public example, without phone "
        "numbers, email, wallets, keys or private customer records. We will review real proposals "
        "individually. Paid work, referral compensation and ASIC pool payouts require "
        "separate explicit agreements before work starts. No coins, salaries or jobs are promised.\n\n"
        "This one-time reply is not a request for personal information or payment."
    )


def decide(rows, now):
    """Fail closed if page retrieval or comment audit is incomplete."""
    greeted = set()
    latest = {}
    opted_out = set()
    for row in rows:
        body = str(row.get("body") or "")
        for a in re.findall(r"<!-- " + MARKER_PREFIX + r":([a-z0-9-]+) -->", body):
            greeted.add(a.casefold())
        author = eligible_author(row)
        if author and any(s in body.casefold() for s in OPTOUT):
            opted_out.add(author.casefold())
        author = approved_comment(row, now)
        if author:
            timestamp = utcparse(row.get("created_at"))
            key = author.casefold()
            if key not in latest or timestamp > latest[key][0]:
                latest[key] = (timestamp, author)
    return [
        a for t, a in sorted(latest.values(), key=lambda p: p[0])
        if a.casefold() not in greeted and a.casefold() not in opted_out
    ][:MAX_REPLIES]


def api(method, path, token, data=None):
    if not path.startswith(BASE):
        raise ValueError("Only owner's opt-in issue may be accessed")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "B1B2-Explicit-OptIn-Welcome/1.0",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    if method == "POST":
        if path != BASE or not token:
            raise ValueError("Unauthorised POST")
        headers["Content-Type"] = "application/json"
        body = json.dumps({"body": data}).encode()
    else:
        if method != "GET":
            raise ValueError("Invalid method")
        body = None
    request = urllib.request.Request(URL + path, headers=headers, method=method, data=body)
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.load(response)
    if method == "GET" and not isinstance(result, list):
        raise ValueError("Expected comment list")
    if method == "POST" and (not isinstance(result, dict) or not result.get("id")):
        raise ValueError("No saved public reply ID")
    return result


def run(send=False, loader=api, now=None, token=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    token = os.getenv("GH_TOKEN", "") if token is None else token
    comments = []
    # To prevent duplicate greetings: refuse posting when the last page is full.
    for page in range(1, MAX_PAGES + 1):
        rows = loader("GET", BASE + f"?per_page=100&page={page}", token)
        comments.extend(rows)
        if len(rows) < 100:
            break
    else:
        raise RuntimeError("Full history exceeded safe audit bound; no comments sent")
    choices = decide(comments, now)
    sent = []
    if send and not token and choices:
        raise ValueError("Token required to acknowledge opt-in comments")
    for author in choices:
        if send:
            record = loader("POST", BASE, token, fixed_message(author))
            sent.append({"source": "owner_issue_32", "reply_id": record["id"], "author_public_login": author})
    return {
        "checked_at_utc": now.isoformat(),
        "thread": "https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/32",
        "read_only": not send,
        "comments_read": len(comments),
        "explicit_optins_to_welcome": len(choices),
        "welcome_replies_sent": len(sent),
        "saved_replies": sent,
        "confirmed_employment_or_mining_partners": 0,
        "verified_new_earnings": 0,
        "emails_accessed_or_sent": 0,
        "wallet_signing": 0,
        "safeguards": "no opt-in = no message; one fixed reply per author; owner issue only",
    }


def test():
    now = dt.datetime(2026, 11, 20, tzinfo=dt.timezone.utc)
    rows = []
    def put(login, body, number, kind="User"):
        rows.append({
            "user": {"login": login, "type": kind},
            "created_at": "2026-11-19T23:00:00Z",
            "body": body,
            "html_url": f"https://github.com/{OWNER}/{REPO}/issues/32#issuecomment-{number}",
        })
    put(OWNER, "I want to join", 1)
    put("botty[bot]", "I want to join", 2, "Bot")
    put("just-reading", "Good luck, nice website", 3)
    put("declines", "I want to join but do not contact me", 4)
    put("volunteer-one", "I would like to contribute one QA test", 5)
    put("volunteer-one", "I want to join", 6)
    put("volunteer-two", "I can help with Kiswahili localization", 7)
    put("false-optin", "I can not join the project", 8)
    assert decide(rows, now) == ["volunteer-one", "volunteer-two"]
    posted = []
    def fake(method, path, token, data=None):
        if method == "GET":
            return rows if "page=1" in path else []
        posted.append(data)
        return {"id": 400 + len(posted)}
    first = run(True, loader=fake, now=now, token="test-token")
    assert first["welcome_replies_sent"] == 2 and len(posted) == 2
    assert "automatic welcome" in posted[0]
    assert "separate explicit agreements" in posted[0]
    for i, msg in enumerate(posted):
        put("github-actions[bot]", msg, i + 400, "Bot")
    second = run(True, loader=fake, now=now, token="test-token")
    assert second["welcome_replies_sent"] == 0 and len(posted) == 2
    assert run(False, loader=fake, now=now, token="")["welcome_replies_sent"] == 0
    assert approved_comment(rows[4] | {"html_url": "https://attacker.invalid"}, now) is None
    try:
        run(True, loader=lambda *args: (_ for _ in ()).throw(OSError("no source")), now=now, token="test")
        raise AssertionError("Failure should not be hidden")
    except OSError:
        pass
    try:
        run(True, loader=fake, now=now, token="")
    except ValueError:
        pass  # Only if a new candidate needs greeting
    print("B1B2_CONSENTED_ONE_TIME_GREETINGS_SELF_TEST_PASS")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        test()
    else:
        result = run(send="--send" in sys.argv)
        print("B1B2_OPT_IN_GREETING_RESULT", json.dumps(result))
