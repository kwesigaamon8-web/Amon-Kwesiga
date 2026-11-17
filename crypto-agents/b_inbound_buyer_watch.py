"""Read-only inbound buyer enquiry scout for owner-controlled GitHub sales pages.

Conservatively filters owner and bot comments; a stranger's public reply is
not evidence of a contract or payment. No automatic outreach or wallet signing.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

OWNER = "kwesigaamon8-web"
REPO = "Amon-Kwesiga"
CHANNELS = (10, 11, 17, 18, 19)
REPORT = Path("paid-opportunity-reports/inbound-buyer-requests.json")


def inbound_candidate(comment, issue_number, now):
    person = comment.get("user") or {}
    login = str(person.get("login") or "").strip()
    if not login or login.lower() == OWNER.lower():
        return None
    if person.get("type") == "Bot" or login.endswith("[bot]"):
        return None
    posted = str(comment.get("created_at") or "")
    try:
        at = dt.datetime.fromisoformat(posted.replace("Z", "+00:00"))
    except ValueError:
        return None
    if at > now + dt.timedelta(minutes=5) or at < now - dt.timedelta(days=14):
        return None
    body = str(comment.get("body") or "").lower()
    # These are leads to REVIEW, never buyers verified by the script.
    keywords = ("hire", "need ", "need a", "quote", "budget", "can you",
                "looking for", "want to", "interested in", "please help",
                "paid task", "service", "send payment", "contribute")
    if not any(term in body for term in keywords):
        return None
    comment_url = str(comment.get("html_url") or "")
    if not comment_url.startswith(f"https://github.com/{OWNER}/{REPO}/issues/"):
        return None
    return {
        "issue_number": issue_number,
        "public_comment_url": comment_url,
        "public_comment_author": login,
        "comment_created_at_utc": posted,
        "payer_identity_verified": False,
        "paid_scope_agreed": False,
        "contact_reply_sent_by_this_scout": False,
        "receipt_verified": False,
        "next_step": "Read the actual comment and assess intent, legitimacy, requested scope, consent and permitted response before offering work."
    }


def check(issues=CHANNELS, now=None, loader=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if loader is None:
        def loader(issue):
            url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{issue}/comments?per_page=100"
            headers = {"Accept": "application/vnd.github+json",
                       "User-Agent": "ChiefDReadOnlyBuyerWatch/1.0"}
            token = os.environ.get("GH_TOKEN", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.load(response)
    rows, failed, seen, checked = [], [], set(), []
    for issue in issues:
        try:
            comments = loader(issue)
            if not isinstance(comments, list):
                raise ValueError("Comment page not a JSON list")
            checked.append(issue)
            for comment in comments:
                lead = inbound_candidate(comment, issue, now)
                if lead is None or lead["public_comment_url"] in seen:
                    continue
                seen.add(lead["public_comment_url"])
                rows.append(lead)
        except (OSError, ValueError, urllib.error.HTTPError) as exc:
            failed.append({"issue": issue, "error": type(exc).__name__})
    rows.sort(key=lambda x: x["comment_created_at_utc"], reverse=True)
    return {
        "checked_at_utc": now.isoformat(),
        "status": "checked" if not failed else ("partial_failure" if checked else "unavailable"),
        "owner_public_sales_issues_checked": checked,
        "failed_issue_checks": failed,
        "outside_owner_inbound_enquiries_not_verified_as_buyers": rows[:30],
        "external_inquiry_count": len(rows),
        "buyer_contracts_proven_by_this_check": 0,
        "correct_network_crypto_receipts_verified_by_this_check": 0,
        "owner_posts_are_not_leads": True,
        "network_failure_is_not_zero_inquiries": True,
        "not_permitted_to_auto_contact_or_collect": True
    }


def self_test():
    now = dt.datetime(2026, 11, 17, 6, tzinfo=dt.timezone.utc)
    def row(who, msg, cid, created="2026-11-17T05:00:00Z",typ="User"):
        return {
            "user": {"login": who, "type": typ}, "body": msg,
            "created_at": created,
            "html_url": f"https://github.com/{OWNER}/{REPO}/issues/18#issuecomment-{cid}"
        }
    sample = [
        row(OWNER, "We offer paid services; request quotes", 1),
        row("github-actions[bot]", "I want to hire", 2, typ="Bot"),
        row("actual-shop", "Could you quote a reconciliation of 100 rows?", 3),
        row("passerby", "Great README, thanks", 4),
        row("old-user", "Need paid services", 5, "2026-10-01T05:00:00Z")
    ]
    result = check((18,), now, lambda _: sample)
    assert result["status"] == "checked" and result["external_inquiry_count"] == 1
    assert result["outside_owner_inbound_enquiries_not_verified_as_buyers"][0]["public_comment_author"] == "actual-shop"
    assert result["buyer_contracts_proven_by_this_check"] == 0
    assert result["correct_network_crypto_receipts_verified_by_this_check"] == 0
    result = check((18,), now, lambda _: (_ for _ in ()).throw(OSError("no internet")))
    assert result["status"] == "unavailable" and result["failed_issue_checks"]
    print("INBOUND_BUYER_SCOUT_SELF_TEST_PASS: false posts filtered; network failure explicit")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        result = check()
        REPORT.parent.mkdir(exist_ok=True, parents=True)
        REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print("CHIEF_D_INBOUND_BUYER_CHECK", json.dumps({
            "status": result["status"], "candidate_inquiries": result["external_inquiry_count"],
            "checked_issues": len(result["owner_public_sales_issues_checked"]),
            "failed_checks": len(result["failed_issue_checks"]),
            "contracts_verified": 0, "payments_verified": 0
        }))
