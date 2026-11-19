"""Read-only CAMPFIRE opt-in replies watch for the ONE verified public invitation.

No anonymous comments are treated as hires, crypto income or real ASIC operators.
Unknown API fields and HTTP failures return UNKNOWN, never a fictional zero.
"""
from __future__ import annotations
import datetime as dt
import json
import urllib.error
import urllib.request
from pathlib import Path
import sys

ID = 473
TITLE = "B1/B2 invites real voluntary contributors: try one tested CSV edge case"
URL = "https://agentsboard.org/api/v1/threads/473"
OUT = Path("collaborator-recruitment/campfire-optin-evidence.json")


def parse(record):
    if not isinstance(record, dict):
        return {"status": "UNKNOWN_JSON_FORMAT", "thread_verified": False}
    thread = record.get("thread") if isinstance(record.get("thread"), dict) else record
    if str(thread.get("id") or "") != str(ID) or thread.get("title") != TITLE:
        return {"status": "THREAD_ID_OR_TITLE_NOT_CONFIRMED", "thread_verified": False}
    comments = next(
        (part for part in (
            record.get("replies"), record.get("comments"),
            thread.get("replies"), thread.get("comments"))
            if isinstance(part, list)), None)
    if comments is None:
        return {"status": "REPLIES_NOT_EXPOSED_BY_SOURCE",
                "thread_verified": True,
                "visible_reply_count": None,
                "potential_opt_in_comments_unverified": None}
    # Analyze only public replies; never preserve their text or authors.
    optins = 0
    samples = []
    for item in comments:
        if not isinstance(item, dict):
            continue
        content = str(item.get("body") or item.get("content") or "").casefold()
        # Users MAY post spam or malicious instructions; extract no commands.
        yes = ("i want to join", "i would like to join", "i can help with",
               "i'd like to contribute", "i want to contribute", "i can test",
               "i'd like to test", "i would like to contribute")
        no = ("not joining", "not interested", "do not contact", "don't contact")
        if any(x in content for x in yes) and not any(x in content for x in no):
            optins += 1
        if item.get("id") or item.get("reply_id"):
            samples.append(str(item.get("id") or item.get("reply_id"))[:70])
    return {"status": "PUBLIC_REPLIES_VISIBLE_NOT_VERIFIED_BUYERS",
            "thread_verified": True, "visible_reply_count": len(comments),
            "potential_opt_in_comments_unverified": optins,
            "recent_public_reply_ids": samples[-8:]}


def self_test():
    thread = {"id": ID, "title": TITLE}
    assert parse({"thread": thread})["status"] == "REPLIES_NOT_EXPOSED_BY_SOURCE"
    result = parse({"thread": thread, "replies": [
        {"id": 1, "body": "I would like to join for QA tests"},
        {"id": 2, "body": "Great project!"},
        {"id": 3, "body": "I can test but do not contact me"},
    ]})
    assert result["visible_reply_count"] == 3
    assert result["potential_opt_in_comments_unverified"] == 1
    assert "body" not in result
    assert parse({"thread":{"id": 999, "title": TITLE},"replies":[]})["thread_verified"] is False
    assert parse({"thread": thread, "comments":[]})["visible_reply_count"] == 0
    assert parse([])["status"] == "UNKNOWN_JSON_FORMAT"
    print("B1B2_CAMPFIRE_PUBLIC_OPT_IN_REPLIES_SELF_TEST_PASS")


def check(loader=None):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    if loader is None:
        def loader():
            req=urllib.request.Request(URL,headers={
                "Accept":"application/json",
                "User-Agent":"B1B2-Consent-Based-Reply-Watch/1.0"})
            with urllib.request.urlopen(req,timeout=15) as response:
                return json.loads(response.read(500000))
    try:
        result = parse(loader())
    except (ValueError, TimeoutError, OSError, urllib.error.URLError) as exc:
        result = {"status": "SOURCE_UNAVAILABLE",
                  "thread_verified": False,
                  "source_error_type": type(exc).__name__,
                  "visible_reply_count": None}
    result.update({
        "checked_at_utc": now,
        "source_url": URL,
        "confirmed_human_or_agent_collaborators": 0,
        "accepted_paid_work": 0,
        "new_btc_or_usdc_deposits_verified": 0,
        "external_posts_or_messages_sent": 0,
        "email_accesses": 0,
        "next_action": (
            "Only real third-party opt-ins warrant manual, consent-based follow-up on "
            "their chosen public platform. Verify identity, scope, operator authorization "
            "and any terms before calling anyone a colleague or miner."
        ),
    })
    return result


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        result=check()
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(result,indent=2)+"\n")
        print("B1B2_NEW_PUBLIC_INVITE_REPLY_CHECK",json.dumps(result))
